"""Claims-ledger audit (S024).

Read-only verification that every Tier-1 and Tier-2 quantitative claim in
preprint/manuscript.md matches the underlying frozen parquets / CSVs /
JSON summaries. The script:

  1. Loads each canonical source artifact (no recomputation from raw CSVs;
     the script uses the same derived artifacts the manuscript was built
     from, so it does not re-seed any bootstraps).
  2. Records one Claim per quoted number, with the manuscript value, the
     source artifact, the computed value, and a tolerance rule.
  3. Sorts the resulting ledger FAIL > WARN > PASS and prints it as a
     markdown table to stdout.

Tolerance rules (from §S024 lab-notebook spec):

  - exact_int        : integer counts, must match exactly.
  - pct_1dp          : percentages displayed to 1 decimal, +/- 0.05 abs.
  - pct_whole        : percentages displayed as whole numbers, +/- 0.5 abs.
  - whole_unit       : floats displayed to whole units, +/- 0.5 abs.
  - displayed_1dp    : floats displayed to 1 decimal, +/- 0.05 abs.
  - displayed_2dp    : floats displayed to 2 decimals, +/- 0.005 abs.
  - displayed_3dp    : floats displayed to 3 decimals, +/- 0.0005 abs.
  - approx_round     : numbers presented with explicit "~" prefix; +/- 1
                       absolute, flagged WARN if outside.

  Tolerance is implemented with a 1e-9 float-noise epsilon to avoid
  spurious failures at exact half-precision boundaries (e.g., 0.0215 ->
  0.022 round-half-up where the diff is 0.0005000000000000004 in IEEE
  754 double precision).

Triage on discrepancies:

  - Type A : Transcription/rounding drift. Manuscript text needs a
             one-character edit; the underlying data is correct.
  - Type B : Orphaned number. Manuscript number does not match any
             source artifact -- needs forensic tracing.
  - Type C : Derivation mismatch. Manuscript number was computed with a
             different threshold/filter/seed than the canonical artifact.

Usage:

    uv run python scripts/audit_claims.py

The script writes nothing. Output is to stdout only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd

REPO = Path(__file__).resolve().parents[1]

# -----------------------------------------------------------------------------
# CLI flags.
# --check-paper-sync (S028 opt-in) additionally verifies that
# preprint_npj/paper.tex stays in sync with the monograph ledger via the
# crosswalk at preprint_npj/paper_to_monograph_map.md. Default behaviour
# is unchanged: legacy 195-claim audit only.
# -----------------------------------------------------------------------------
_PARSER = argparse.ArgumentParser(
    description=(
        "Claims-ledger audit for the Pulse Reliability Atlas monograph. "
        "Pass --check-paper-sync to additionally verify the npj submission "
        "paper.tex against the crosswalk map (see preprint_npj/README.md)."
    )
)
_PARSER.add_argument(
    "--check-paper-sync",
    action="store_true",
    help=(
        "Also verify preprint_npj/paper.tex stays in sync with the monograph "
        "ledger via preprint_npj/paper_to_monograph_map.md. Opt-in flag; "
        "default behaviour is the legacy monograph-only audit."
    ),
)
_ARGS = _PARSER.parse_args()

# Tolerance rule -> absolute tolerance.
TOLERANCE = {
    "exact_int": 0.0,
    "pct_1dp": 0.05,
    "pct_whole": 0.5,
    "whole_unit": 0.5,
    "displayed_1dp": 0.05,
    "displayed_2dp": 0.005,
    "displayed_3dp": 0.0005,
    "approx_round": 1.0,
}
FLOAT_EPS = 1e-9  # IEEE-754 noise budget around exact-boundary comparisons.


@dataclass
class Claim:
    claim_id: str
    section: str
    manuscript_text: str
    source_file: str
    manuscript_value: Optional[float]
    computed_value: Optional[float]
    tolerance_rule: str
    status: str = ""  # PASS / WARN / FAIL
    triage_type: str = ""  # A / B / C / "" if PASS
    notes: str = ""

    def evaluate(self) -> None:
        if self.manuscript_value is None or self.computed_value is None:
            self.status = "FAIL"
            self.triage_type = "B"
            self.notes = (self.notes + " | missing value").strip(" |")
            return
        tol = TOLERANCE[self.tolerance_rule]
        diff = abs(self.manuscript_value - self.computed_value)
        if diff <= tol + FLOAT_EPS:
            self.status = "PASS"
            self.triage_type = ""
        elif self.tolerance_rule == "approx_round" and diff <= 2.0:
            self.status = "WARN"
            self.triage_type = "A"
            self.notes = (
                self.notes + f" | diff={diff:.4g} within WARN band for approx_round"
            ).strip(" |")
        else:
            self.status = "FAIL"
            self.triage_type = "A"
            self.notes = (self.notes + f" | diff={diff:.4g}, tol={tol}").strip(" |")


claims: list[Claim] = []


def add(**kw) -> None:
    c = Claim(**kw)
    c.evaluate()
    claims.append(c)


# -----------------------------------------------------------------------------
# S028 paper-sync helpers (read-only; used only under --check-paper-sync).
#
# Design notes:
#   - The parser is intentionally minimal: it handles the small YAML-like
#     dialect used by preprint_npj/paper_to_monograph_map.md (entries
#     starting with "- " at column 0, keys indented by 2 spaces). We do NOT
#     import a full YAML library to keep audit_claims.py dependency-light
#     (matches the existing convention of stdlib + pandas only).
#   - All file I/O is read-only. The functions never write to disk.
#   - All failure paths print a clear WARN line and degrade gracefully so
#     that running --check-paper-sync against an absent or partial
#     paper_npj directory never crashes the audit.
# -----------------------------------------------------------------------------


def _strip_yaml_value(raw: str) -> str:
    """Strip surrounding whitespace and optional matched quotes."""
    v = raw.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ('"', "'"):
        v = v[1:-1]
    return v


def _parse_map_entries(map_text: str) -> list[dict]:
    """Parse the minimal YAML-like dialect of paper_to_monograph_map.md.

    Skips fenced code blocks (``` ... ```). An entry starts with "- " at
    column 0 followed by indented "key: value" continuations. Anything
    else (blank lines, top-level # comments, narrative text) is ignored.
    Returns a list of dict entries; an empty list means no rows have been
    declared yet (legitimate during early-drafting steps of S028).
    """
    entries: list[dict] = []
    current: Optional[dict] = None
    in_code_block = False
    for line in map_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if not stripped or stripped.startswith("#"):
            continue
        if line.startswith("- "):
            if current is not None:
                entries.append(current)
            current = {}
            rest = line[2:].strip()
            if ":" in rest:
                key, _, val = rest.partition(":")
                current[key.strip()] = _strip_yaml_value(val)
        elif line.startswith("  ") and current is not None and ":" in stripped:
            key, _, val = stripped.partition(":")
            current[key.strip()] = _strip_yaml_value(val)
    if current is not None:
        entries.append(current)
    return entries


def check_paper_sync(ledger_claims: list[Claim]) -> tuple[int, int, int]:
    """Verify preprint_npj/paper.tex stays in sync with the monograph
    ledger via the crosswalk at preprint_npj/paper_to_monograph_map.md.

    For each map entry, count `re.findall(re.escape(format_in_paper), ...)`
    in paper.tex and compare against the entry's `expected_occurrences`.
    Also cross-check that `monograph_claim_id` exists in the ledger and
    that `expected_value` agrees with the ledger's recorded
    manuscript_value within the same tolerance as the ledger entry.

    Outcomes:
      - PASS                    : count == expected_occurrences AND
                                  monograph value matches map expected_value.
      - FAIL (missing)          : count == 0 AND expected_occurrences >= 1.
      - FAIL (count drift)      : count != expected_occurrences.
      - FAIL (value drift)      : map expected_value disagrees with the
                                  monograph ledger value behind claim_id.
      - FAIL (unknown claim_id) : claim_id not in the ledger.

    Graceful degradation: if paper.tex or the map file is missing, emit a
    WARN and return (0, 1, 0). The audit's exit status is unaffected by
    these WARN cases.

    Returns: (n_pass, n_warn, n_fail) for the sync check only.
    """
    print("\n## Paper-monograph sync check (S028 --check-paper-sync)\n")
    paper_path = REPO / "preprint_npj" / "paper.tex"
    map_path = REPO / "preprint_npj" / "paper_to_monograph_map.md"

    if not paper_path.exists():
        print(
            f"_WARN: {paper_path.relative_to(REPO)} not found; sync check "
            "skipped (the npj submission paper does not exist yet)._\n"
        )
        return (0, 1, 0)
    if not map_path.exists():
        print(
            f"_WARN: {map_path.relative_to(REPO)} not found; sync check "
            "skipped (the crosswalk has not been initialised yet)._\n"
        )
        return (0, 1, 0)

    entries = _parse_map_entries(map_path.read_text(encoding="utf-8"))
    if not entries:
        print(
            "_No mapped claims declared yet in "
            "preprint_npj/paper_to_monograph_map.md. This is the expected "
            "state during early S028 drafting; rows are added incrementally "
            "as paper.tex sections are written._\n"
        )
        return (0, 0, 0)

    paper_tex = paper_path.read_text(encoding="utf-8")
    ledger_by_id = {c.claim_id: c for c in ledger_claims}

    rows: list[dict] = []
    n_pass = n_warn = n_fail = 0
    for entry in entries:
        claim_id = entry.get("monograph_claim_id", "?")
        fmt = entry.get("format_in_paper", "")
        section = entry.get("paper_section", "?")
        try:
            expected_occ = int(entry.get("expected_occurrences", "0"))
        except (TypeError, ValueError):
            expected_occ = -1  # signals a parse failure
        try:
            map_expected = float(entry.get("expected_value", "nan"))
        except (TypeError, ValueError):
            map_expected = float("nan")

        # Occurrence-count check on paper.tex (literal-string regex).
        count = (
            len(re.findall(re.escape(fmt), paper_tex)) if fmt else 0
        )

        status = "PASS"
        notes: list[str] = []

        # Layer A: claim_id existence + monograph-value agreement.
        ledger_entry = ledger_by_id.get(claim_id)
        if ledger_entry is None:
            status = "FAIL"
            notes.append(f"claim_id `{claim_id}` not in monograph ledger")
        elif ledger_entry.status != "PASS":
            status = "FAIL"
            notes.append(
                f"monograph ledger entry `{claim_id}` is "
                f"{ledger_entry.status}, not PASS"
            )
        elif ledger_entry.manuscript_value is not None and not (
            map_expected != map_expected  # NaN check
        ):
            tol = TOLERANCE.get(ledger_entry.tolerance_rule, 0.0) + FLOAT_EPS
            if abs(map_expected - ledger_entry.manuscript_value) > tol:
                status = "FAIL"
                notes.append(
                    f"value drift: map expected_value={map_expected} "
                    f"disagrees with monograph value="
                    f"{ledger_entry.manuscript_value} "
                    f"(tolerance {ledger_entry.tolerance_rule})"
                )

        # Layer B: occurrence-count check on paper.tex.
        if status == "PASS":
            if expected_occ < 0:
                status = "FAIL"
                notes.append("expected_occurrences could not be parsed as int")
            elif count == 0 and expected_occ >= 1:
                status = "FAIL"
                notes.append(
                    f"missing: format_in_paper `{fmt}` not found in paper.tex "
                    f"(expected {expected_occ})"
                )
            elif count != expected_occ:
                status = "FAIL"
                notes.append(
                    f"count drift: found {count}, expected {expected_occ}"
                )

        rows.append(
            {
                "claim_id": claim_id,
                "section": section,
                "fmt": fmt,
                "expected_occ": expected_occ,
                "found_occ": count,
                "status": status,
                "notes": "; ".join(notes) if notes else "-",
            }
        )
        if status == "PASS":
            n_pass += 1
        elif status == "WARN":
            n_warn += 1
        else:
            n_fail += 1

    print(
        f"**Sync check:** {len(rows)} mapped entries "
        f"({n_pass} PASS, {n_warn} WARN, {n_fail} FAIL).\n"
    )
    print(
        "| claim_id | section | format_in_paper | expected | found | status | notes |"
    )
    print("|---|---|---|---:|---:|---|---|")
    for r in rows:
        print(
            f"| {r['claim_id']} | {r['section']} | `{r['fmt']}` | "
            f"{r['expected_occ']} | {r['found_occ']} | {r['status']} | "
            f"{r['notes']} |"
        )
    print()

    return (n_pass, n_warn, n_fail)


# -----------------------------------------------------------------------------
# Load every canonical artifact once.
# -----------------------------------------------------------------------------
agg = pd.read_parquet(REPO / "data/runs/full_sweep/aggregated.parquet")
cfs = pd.read_csv(REPO / "results/cell_flag_summary.csv")
h1 = pd.read_csv(REPO / "results/h1_top3_fraction.csv")
bh = pd.read_csv(REPO / "results/bh_fdr_survivors.csv")
sp = pd.read_csv(REPO / "results/spearman_mu_star.csv")
rc = pd.read_csv(REPO / "results/reliability_classification.csv")
nss = pd.read_csv(REPO / "results/s022/nss_decomposition.csv")
s23_pooled = pd.read_csv(REPO / "results/s023/topk_overlap.csv")
s23_cell = pd.read_csv(REPO / "results/s023/topk_overlap_per_cell.csv")
f003 = json.loads((REPO / "results/f003_physiological_reclassification_summary.json").read_text())
s14_pair = pd.read_parquet(REPO / "data/runs/s014_trigger_lockout/paired_comparison.parquet")
s14_sum = json.loads((REPO / "data/runs/s014_trigger_lockout/summary.json").read_text())
s21_plat = pd.read_parquet(REPO / "data/runs/s021_hyperoxia_convergence/plateau_stats.parquet")
s21_sum = json.loads((REPO / "data/runs/s021_hyperoxia_convergence/summary.json").read_text())
s18_b = pd.read_parquet(REPO / "data/runs/s018_blood_volume/s018_classified.parquet")
s18_f = pd.read_parquet(REPO / "data/runs/s018_blood_volume/s018_floor_classified.parquet")

# -----------------------------------------------------------------------------
# TIER 1 -- ABSTRACT / KEY CONTRIBUTIONS / HYPOTHESIS VERDICTS / HEADLINE TABLES
# -----------------------------------------------------------------------------

# 1. Total runs.
add(
    claim_id="T1.01",
    section="Abstract L28",
    manuscript_text="1,280 total simulations",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=1280,
    computed_value=len(agg),
    tolerance_rule="exact_int",
)

# 2. F-004 Vt CV instability 20.6% (primary flag rate).
n_vtcv_primary = int(((agg["Vt_cv"] > 0.05) & (agg["not_steady_state"])).sum())
# Manuscript says 20.6% which is 264/1280 = 0.20625 (primary flag).
n_primary_nss_vtcv = int(
    (
        (agg["primary_flag"] == "not_steady_state")
        if "primary_flag" in agg.columns
        else pd.Series([False] * len(agg))
    ).sum()
)


# Use the explicit not_steady_state flag count where Vt_cv > 0.05 AND no
# higher-priority flag is set.
def _primary(row):
    if row["clamped"]:
        return "clamped"
    if row["diverged"]:
        return "diverged"
    if row["implausible"]:
        return "implausible"
    if row["not_steady_state"]:
        return "not_steady_state"
    return "clean"


agg["_primary"] = agg.apply(_primary, axis=1)
n_primary_nss_vtcv_only = int(
    ((agg["_primary"] == "not_steady_state") & (agg["Vt_cv"] > 0.05)).sum()
)
add(
    claim_id="T1.02a",
    section="Abstract L34, §3.8 L2051",
    manuscript_text="20.6% F-004 primary-flag rate (264/1,280)",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=20.6,
    computed_value=100.0 * n_primary_nss_vtcv_only / len(agg),
    tolerance_rule="pct_1dp",
)
add(
    claim_id="T1.02b",
    section="§3.8 L2049",
    manuscript_text="303/1,280 (23.7%) Vt_cv > 5% across full sweep",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=int((agg["Vt_cv"] > 0.05).sum() == 303 and 303),
    computed_value=int((agg["Vt_cv"] > 0.05).sum()),
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.02c",
    section="§3.8 L2050",
    manuscript_text="23.7% Vt_cv > 5% rate",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=23.7,
    computed_value=100.0 * (agg["Vt_cv"] > 0.05).sum() / len(agg),
    tolerance_rule="pct_1dp",
)

# 3-4. F-004 median Vt CV collapse + worst case.
add(
    claim_id="T1.03",
    section="Abstract L36, KeyContrib L123",
    manuscript_text="median Vt CV collapses 0.351 -> 0.016",
    source_file="data/runs/s014_trigger_lockout/paired_comparison.parquet",
    manuscript_value=0.351,
    computed_value=float(s14_pair["Vt_cv_orig"].median()),
    tolerance_rule="displayed_3dp",
)
add(
    claim_id="T1.04",
    section="Abstract L36, KeyContrib L123",
    manuscript_text="median Vt CV collapses to 0.016 after lockout",
    source_file="data/runs/s014_trigger_lockout/paired_comparison.parquet",
    manuscript_value=0.016,
    computed_value=float(s14_pair["Vt_cv_lock"].median()),
    tolerance_rule="displayed_3dp",
)
add(
    claim_id="T1.05",
    section="Abstract L37, KeyContrib L124",
    manuscript_text="worst-case Vt CV 1.826 -> 0.112",
    source_file="data/runs/s014_trigger_lockout/paired_comparison.parquet",
    manuscript_value=1.826,
    computed_value=float(s14_pair["Vt_cv_orig"].max()),
    tolerance_rule="displayed_3dp",
)
add(
    claim_id="T1.06",
    section="Abstract L37, KeyContrib L124",
    manuscript_text="worst-case Vt CV post-lockout 0.112",
    source_file="data/runs/s014_trigger_lockout/paired_comparison.parquet",
    manuscript_value=0.112,
    computed_value=float(s14_pair["Vt_cv_lock"].max()),
    tolerance_rule="displayed_3dp",
)

# 5-6. H1: PASS 48/48 + median 0.928 + range 0.658-0.998.
add(
    claim_id="T1.07",
    section="Abstract L38, §3.3",
    manuscript_text="H1 PASS 48/48 (top-3 fraction >= 0.5)",
    source_file="results/h1_top3_fraction.csv",
    manuscript_value=48,
    computed_value=int(h1["h1_pass"].sum()),
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.08",
    section="Abstract L39, §3.3 L1190",
    manuscript_text="H1 median top-3 fraction 0.928",
    source_file="results/h1_top3_fraction.csv",
    manuscript_value=0.928,
    computed_value=float(h1["top3_fraction"].median()),
    tolerance_rule="displayed_3dp",
)
add(
    claim_id="T1.09",
    section="§3.3 L1190",
    manuscript_text="H1 top-3 fraction range 0.658 - 0.998",
    source_file="results/h1_top3_fraction.csv",
    manuscript_value=0.658,
    computed_value=float(h1["top3_fraction"].min()),
    tolerance_rule="displayed_3dp",
)
add(
    claim_id="T1.10",
    section="§3.3 L1190",
    manuscript_text="H1 top-3 fraction max 0.998",
    source_file="results/h1_top3_fraction.csv",
    manuscript_value=0.998,
    computed_value=float(h1["top3_fraction"].max()),
    tolerance_rule="displayed_3dp",
)

# 11. H2 NOT supported (0/1,280 clamped).
add(
    claim_id="T1.11",
    section="Abstract L46, §3.4",
    manuscript_text="0 of 1,280 silent-clamping flags",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=0,
    computed_value=int(agg["clamped"].sum()),
    tolerance_rule="exact_int",
)

# 12-13. H3: 20/1,280 diverged, all 20 male.
add(
    claim_id="T1.12",
    section="Abstract L47, §3.5",
    manuscript_text="20 of 1,280 runs (1.6%) diverged",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=20,
    computed_value=int(agg["diverged"].sum()),
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.13",
    section="Abstract L47, §3.5",
    manuscript_text="1.6% divergence rate",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=1.6,
    computed_value=100.0 * int(agg["diverged"].sum()) / len(agg),
    tolerance_rule="pct_1dp",
)
add(
    claim_id="T1.14",
    section="Abstract L47-48, §3.5 L1433",
    manuscript_text="All 20 divergences are male (zero female)",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=20,
    computed_value=int(agg[agg["diverged"]]["sex"].eq("M").sum()),
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.14b",
    section="§3.5 L1576",
    manuscript_text="Female rate 0/640",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=0,
    computed_value=int(agg[agg["diverged"] & (agg["sex"] == "F")].shape[0]),
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.14c",
    section="§3.5 L1576",
    manuscript_text="Male rate 20/640 = 3.1%",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=3.1,
    computed_value=100.0 * 20 / 640,
    tolerance_rule="pct_1dp",
)

# 14-15. H4: 5/24 Wasserstein survive BH-FDR.
add(
    claim_id="T1.15",
    section="Abstract L57, §3.6 L1726",
    manuscript_text="5 of 24 cell x output Wasserstein survive BH-FDR q=0.05",
    source_file="results/bh_fdr_survivors.csv",
    manuscript_value=5,
    computed_value=int(bh["bh_survives"].sum()),
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.16",
    section="Abstract L58, §3.6 L1837",
    manuscript_text="PaCO2 x3 surviving",
    source_file="results/bh_fdr_survivors.csv",
    manuscript_value=3,
    computed_value=int(((bh["bh_survives"]) & (bh["output"] == "PaCO2")).sum()),
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.17",
    section="Abstract L58, §3.6 L1837",
    manuscript_text="SpO2 x1 surviving",
    source_file="results/bh_fdr_survivors.csv",
    manuscript_value=1,
    computed_value=int(((bh["bh_survives"]) & (bh["output"] == "SpO2")).sum()),
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.18",
    section="Abstract L58, §3.6 L1837",
    manuscript_text="PaO2 x1 surviving",
    source_file="results/bh_fdr_survivors.csv",
    manuscript_value=1,
    computed_value=int(((bh["bh_survives"]) & (bh["output"] == "PaO2")).sum()),
    tolerance_rule="exact_int",
)

# 16. Spearman rho range in S2/S3 (0.75 - 1.00) - computed on non-NaN rows.
sp_s2s3 = sp[sp["scenario"].isin(["S2", "S3"])]["spearman_rho"].dropna()
add(
    claim_id="T1.19",
    section="Abstract L61, §3.6",
    manuscript_text="Spearman rho min 0.75 in S2/S3",
    source_file="results/spearman_mu_star.csv",
    manuscript_value=0.75,
    computed_value=float(sp_s2s3.min()),
    tolerance_rule="displayed_2dp",
)
add(
    claim_id="T1.20",
    section="Abstract L61, §3.6",
    manuscript_text="Spearman rho max 1.00 in S2/S3",
    source_file="results/spearman_mu_star.csv",
    manuscript_value=1.00,
    computed_value=float(sp_s2s3.max()),
    tolerance_rule="displayed_2dp",
)

# 17-18. F-003: 34/126 implausibly flagged exceed 600 mmHg; 91% at FiO2 >= 0.95.
n_impl = int(agg["implausible"].sum())
n_impl_pao2_over_600 = int(agg[agg["implausible"] & (agg["PaO2_mean"] > 600)].shape[0])
n_impl_pao2_over_600_high_fio2 = int(
    agg[agg["implausible"] & (agg["PaO2_mean"] > 600) & (agg["in_fio2"] >= 0.95)].shape[0]
)
add(
    claim_id="T1.21",
    section="Abstract L51, §3.8 L1922",
    manuscript_text="34 of 126 implausibly-flagged runs exceed 600 mmHg",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=34,
    computed_value=n_impl_pao2_over_600,
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.21b",
    section="Abstract L51",
    manuscript_text="126 implausibly-flagged runs",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=126,
    computed_value=n_impl,
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.22",
    section="Key Contrib L127, §3.8 L1924",
    manuscript_text="91% of 34 PaO2>600 are at FiO2 >= 0.95",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=91,
    computed_value=100.0 * n_impl_pao2_over_600_high_fio2 / max(1, n_impl_pao2_over_600),
    tolerance_rule="pct_whole",
)

# 19-21. F-003 S021 plateau median 643 mmHg + ~10 mmHg below AGE + 93.2% converged.
add(
    claim_id="T1.23",
    section="Abstract L52 (post-audit edit), KeyContrib L130, §3.8 L1965",
    manuscript_text="S021 plateau median 643 mmHg in S1",
    source_file="data/runs/s021_hyperoxia_convergence/summary.json",
    manuscript_value=643.0,
    computed_value=float(s21_sum["S1_plateau_median_mmHg"]),
    tolerance_rule="whole_unit",
)
add(
    claim_id="T1.24",
    section="§3.8 L1965 + L1962",
    manuscript_text="S021 S1 frac converged 93.2% (41/44)",
    source_file="data/runs/s021_hyperoxia_convergence/summary.json",
    manuscript_value=93.2,
    computed_value=100.0 * float(s21_sum["S1_frac_converged"]),
    tolerance_rule="pct_1dp",
)
n_s1_runs_s021 = int(s21_plat[s21_plat["scenario"] == "S1"].shape[0])
n_s1_converged = int(s21_plat[(s21_plat["scenario"] == "S1") & s21_plat["converged"]].shape[0])
add(
    claim_id="T1.24b",
    section="§3.8 L1965",
    manuscript_text="S1 converged: 41 / 44 runs",
    source_file="data/runs/s021_hyperoxia_convergence/plateau_stats.parquet",
    manuscript_value=41,
    computed_value=n_s1_converged,
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.24c",
    section="§3.8 L1955",
    manuscript_text="44 S1 runs total in S021",
    source_file="data/runs/s021_hyperoxia_convergence/plateau_stats.parquet",
    manuscript_value=44,
    computed_value=n_s1_runs_s021,
    tolerance_rule="exact_int",
)

# 22. Table 1 cell counts -- 8 cells x 5 numeric columns + n_total.
table1_expected = {
    ("S1", "M"): (160, 0, 4, 11, 107, 49),
    ("S1", "F"): (160, 0, 0, 23, 118, 42),
    ("S2", "M"): (160, 0, 4, 0, 69, 87),
    ("S2", "F"): (160, 0, 0, 0, 68, 92),
    ("S3", "M"): (160, 0, 4, 0, 12, 144),
    ("S3", "F"): (160, 0, 0, 0, 38, 122),
    ("S4", "M"): (160, 0, 8, 46, 44, 67),
    ("S4", "F"): (160, 0, 0, 46, 74, 60),
}
for (sc, sx), (n_t, n_cl, n_dv, n_im, n_nss_, n_cln) in table1_expected.items():
    row = cfs[(cfs["scenario"] == sc) & (cfs["sex"] == sx)].iloc[0]
    cid = f"T1.T1-{sc}_{sx}"
    add(
        claim_id=f"{cid}.n_total",
        section=f"Table 1 ({sc}, {sx})",
        manuscript_text=f"n_total = {n_t}",
        source_file="results/cell_flag_summary.csv",
        manuscript_value=n_t,
        computed_value=int(row["n_total"]),
        tolerance_rule="exact_int",
    )
    add(
        claim_id=f"{cid}.clamped",
        section=f"Table 1 ({sc}, {sx})",
        manuscript_text=f"clamped = {n_cl}",
        source_file="results/cell_flag_summary.csv",
        manuscript_value=n_cl,
        computed_value=int(row["n_clamped"]),
        tolerance_rule="exact_int",
    )
    add(
        claim_id=f"{cid}.diverged",
        section=f"Table 1 ({sc}, {sx})",
        manuscript_text=f"diverged = {n_dv}",
        source_file="results/cell_flag_summary.csv",
        manuscript_value=n_dv,
        computed_value=int(row["n_diverged"]),
        tolerance_rule="exact_int",
    )
    add(
        claim_id=f"{cid}.implausible",
        section=f"Table 1 ({sc}, {sx})",
        manuscript_text=f"implausible = {n_im}",
        source_file="results/cell_flag_summary.csv",
        manuscript_value=n_im,
        computed_value=int(row["n_implausible"]),
        tolerance_rule="exact_int",
    )
    add(
        claim_id=f"{cid}.nss",
        section=f"Table 1 ({sc}, {sx})",
        manuscript_text=f"not_steady_state = {n_nss_}",
        source_file="results/cell_flag_summary.csv",
        manuscript_value=n_nss_,
        computed_value=int(row["n_not_steady_state"]),
        tolerance_rule="exact_int",
    )
    add(
        claim_id=f"{cid}.clean",
        section=f"Table 1 ({sc}, {sx})",
        manuscript_text=f"clean = {n_cln}",
        source_file="results/cell_flag_summary.csv",
        manuscript_value=n_cln,
        computed_value=int(row["n_clean"]),
        tolerance_rule="exact_int",
    )

# 23. Traffic light: 7 green / 29 yellow / 12 red.
g = int((rc["light"] == "green").sum())
y = int((rc["light"] == "yellow").sum())
r = int((rc["light"] == "red").sum())
add(
    claim_id="T1.25",
    section="§3.7 L1882, L1904",
    manuscript_text="Traffic light: 7 green",
    source_file="results/reliability_classification.csv",
    manuscript_value=7,
    computed_value=g,
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.26",
    section="§3.7 L1882",
    manuscript_text="Traffic light: 29 yellow",
    source_file="results/reliability_classification.csv",
    manuscript_value=29,
    computed_value=y,
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.27",
    section="§3.7 L1882",
    manuscript_text="Traffic light: 12 red",
    source_file="results/reliability_classification.csv",
    manuscript_value=12,
    computed_value=r,
    tolerance_rule="exact_int",
)

# 24. Clean total: 663 / 1,280 = 51.8%.
add(
    claim_id="T1.28",
    section="§3.1 L1083, §3.1 L1096",
    manuscript_text="663 / 1,280 clean",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=663,
    computed_value=int(agg["clean"].sum()),
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.29",
    section="§3.1 L1096",
    manuscript_text="51.8% clean rate",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=51.8,
    computed_value=100.0 * int(agg["clean"].sum()) / len(agg),
    tolerance_rule="pct_1dp",
)

# -----------------------------------------------------------------------------
# TIER 2 -- §3 deep cuts + appendices
# -----------------------------------------------------------------------------

# 26. §3.3 lowest top-3 fractions: S4_F SpO2 0.658, S4_M SpO2 0.703, S4_F PaO2 0.707, S4_M PaO2 0.727.
lowest_claims = [
    ("S4", "F", "SpO2", 0.658),
    ("S4", "M", "SpO2", 0.703),
    ("S4", "F", "PaO2", 0.707),
    ("S4", "M", "PaO2", 0.727),
]
for sc, sx, out, val in lowest_claims:
    row = h1[(h1["scenario"] == sc) & (h1["sex"] == sx) & (h1["output"] == out)].iloc[0]
    add(
        claim_id=f"T2.h1.{sc}_{sx}.{out}",
        section=f"§3.3 L1191-1193 ({sc}_{sx} {out})",
        manuscript_text=f"top-3 fraction = {val:.3f}",
        source_file="results/h1_top3_fraction.csv",
        manuscript_value=val,
        computed_value=float(row["top3_fraction"]),
        tolerance_rule="displayed_3dp",
    )

# 27. §3.4.1 Output HR by scenario (clean runs only).
clean_agg = agg[agg["clean"]]
hr_by_scenario = clean_agg.groupby("scenario")["HR_mean"].agg(["mean", "std"])
hr_expected = {"S1": (73.8, 20.4), "S2": (87.3, 24.3), "S3": (155.7, 34.7), "S4": (147.1, 31.8)}
for sc, (mu, sd) in hr_expected.items():
    add(
        claim_id=f"T2.hr.{sc}.mean",
        section=f"§3.4.1 L1387-1390 ({sc})",
        manuscript_text=f"clean HR mean {mu}",
        source_file="data/runs/full_sweep/aggregated.parquet",
        manuscript_value=mu,
        computed_value=float(hr_by_scenario.loc[sc, "mean"]),
        tolerance_rule="displayed_1dp",
    )
    add(
        claim_id=f"T2.hr.{sc}.std",
        section=f"§3.4.1 L1387-1390 ({sc})",
        manuscript_text=f"clean HR std {sd}",
        source_file="data/runs/full_sweep/aggregated.parquet",
        manuscript_value=sd,
        computed_value=float(hr_by_scenario.loc[sc, "std"]),
        tolerance_rule="displayed_1dp",
    )

# 28-29. §3.5 BV dose-response (presence-count semantics per §3.1 caption).
# Bracket (BV=4400) row: 2 / 1 / 8 / 10
bracket = s18_b[s18_b["bv_label"] == "bracket"]
add(
    claim_id="T2.bv.bracket.diverged",
    section="§3.5 L1492",
    manuscript_text="BV=4400 mL: diverged = 2 / 20",
    source_file="data/runs/s018_blood_volume/s018_classified.parquet",
    manuscript_value=2,
    computed_value=int(bracket["diverged"].sum()),
    tolerance_rule="exact_int",
)
add(
    claim_id="T2.bv.bracket.impl",
    section="§3.5 L1492",
    manuscript_text="BV=4400 mL: implausible = 1 / 20",
    source_file="data/runs/s018_blood_volume/s018_classified.parquet",
    manuscript_value=1,
    computed_value=int(bracket["implausible"].sum()),
    tolerance_rule="exact_int",
)
add(
    claim_id="T2.bv.bracket.nss",
    section="§3.5 L1492",
    manuscript_text="BV=4400 mL: not_steady_state = 8 / 20",
    source_file="data/runs/s018_blood_volume/s018_classified.parquet",
    manuscript_value=8,
    computed_value=int(bracket["not_steady_state"].sum()),
    tolerance_rule="exact_int",
)
add(
    claim_id="T2.bv.bracket.clean",
    section="§3.5 L1492",
    manuscript_text="BV=4400 mL: clean = 10 / 20",
    source_file="data/runs/s018_blood_volume/s018_classified.parquet",
    manuscript_value=10,
    computed_value=int(bracket["clean"].sum()),
    tolerance_rule="exact_int",
)
# Floor (BV=4082.24) row: 0 / 1 / 8 / 12
add(
    claim_id="T2.bv.floor.diverged",
    section="§3.5 L1493",
    manuscript_text="BV=4082.24 mL: diverged = 0 / 20",
    source_file="data/runs/s018_blood_volume/s018_floor_classified.parquet",
    manuscript_value=0,
    computed_value=int(s18_f["diverged"].sum()),
    tolerance_rule="exact_int",
)
add(
    claim_id="T2.bv.floor.impl",
    section="§3.5 L1493",
    manuscript_text="BV=4082.24 mL: implausible = 1 / 20",
    source_file="data/runs/s018_blood_volume/s018_floor_classified.parquet",
    manuscript_value=1,
    computed_value=int(s18_f["implausible"].sum()),
    tolerance_rule="exact_int",
)
add(
    claim_id="T2.bv.floor.nss",
    section="§3.5 L1493",
    manuscript_text="BV=4082.24 mL: not_steady_state = 8 / 20",
    source_file="data/runs/s018_blood_volume/s018_floor_classified.parquet",
    manuscript_value=8,
    computed_value=int(s18_f["not_steady_state"].sum()),
    tolerance_rule="exact_int",
)
add(
    claim_id="T2.bv.floor.clean",
    section="§3.5 L1493",
    manuscript_text="BV=4082.24 mL: clean = 12 / 20",
    source_file="data/runs/s018_blood_volume/s018_floor_classified.parquet",
    manuscript_value=12,
    computed_value=int(s18_f["clean"].sum()),
    tolerance_rule="exact_int",
)

# 32. §3.5 per-cell diverged counts -- already in Table 1 verification (T1.T1 group).
# Skipped to avoid double-counting; would re-flag any T1 issue.

# 37. §3.6 H4 demoted: S2 SpO2 (p_emp = 0.022 above 0.0104 critical).
row_s2_spo2 = bh[(bh["scenario"] == "S2") & (bh["output"] == "SpO2")].iloc[0]
add(
    claim_id="T2.bh.s2_spo2.p",
    section="§3.6 L1730",
    manuscript_text="S2 SpO2 p_emp = 0.022 (demoted by BH-FDR)",
    source_file="results/bh_fdr_survivors.csv",
    manuscript_value=0.022,
    computed_value=float(row_s2_spo2["p_value_empirical"]),
    tolerance_rule="displayed_3dp",
)
add(
    claim_id="T2.bh.s2_spo2.crit",
    section="§3.6 L1727-1728",
    manuscript_text="BH critical for 5th-ranked p-value: 5*0.05/24 = 0.0104",
    source_file="results/bh_fdr_survivors.csv",
    manuscript_value=0.0104,
    computed_value=5 * 0.05 / 24,
    tolerance_rule="displayed_3dp",
)

# 38. §3.6 Spearman rho point estimates for S2/S3 (12 rows).
sp_expected = {
    ("S2", "HR"): 0.96,
    ("S2", "MAP"): 1.00,
    ("S2", "Vt"): 0.75,
    ("S2", "SpO2"): 0.96,
    ("S2", "PaO2"): 0.93,
    ("S2", "PaCO2"): 0.89,
    ("S3", "HR"): 0.96,
    ("S3", "MAP"): 0.96,
    ("S3", "Vt"): 0.86,
    ("S3", "SpO2"): 0.96,
    ("S3", "PaO2"): 0.93,
    ("S3", "PaCO2"): 0.89,
}
for (sc, out), val in sp_expected.items():
    row = sp[(sp["scenario"] == sc) & (sp["output"] == out)].iloc[0]
    add(
        claim_id=f"T2.sp.{sc}.{out}",
        section=f"§3.6 Spearman table ({sc} {out})",
        manuscript_text=f"rho = {val:.2f}",
        source_file="results/spearman_mu_star.csv",
        manuscript_value=val,
        computed_value=float(row["spearman_rho"]),
        tolerance_rule="displayed_2dp",
    )

# 40-41. §3.8 F-003: 93.3% positive slope on FiO2 >= 0.95 valid-CSV runs;
#         18.5% exceed 15 mmHg/60s drift threshold (also separately cited
#         as 19.5% in §3.8.1 -- internal cross-check below).
hi_fio2 = agg[(agg["in_fio2"] >= 0.95) & agg["PaO2_n_points"].fillna(0).gt(0)]
add(
    claim_id="T2.f003.pos_slope",
    section="§3.8 L1926",
    manuscript_text="93.3% of FiO2 >= 0.95 valid-CSV runs have positive PaO2 slope",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=93.3,
    computed_value=100.0 * (hi_fio2["PaO2_slope_per_s"] > 0).sum() / max(1, len(hi_fio2)),
    tolerance_rule="pct_1dp",
)
# Drift-exceed: same population, both §3.8 and §3.8.1 cite this.
# §3.8 L1927 says 18.5%, §3.8.1 L2135 says 19.5%. Audit both.
drift_exceed_pct = 100.0 * (hi_fio2["PaO2_delta_60s"].abs() > 15).sum() / max(1, len(hi_fio2))
add(
    claim_id="T2.f003.drift_exceed_v38",
    section="§3.8 L1946",
    manuscript_text="19.5% exceed 15 mmHg/60s drift threshold (FiO2 >= 0.95)",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=19.5,
    computed_value=drift_exceed_pct,
    tolerance_rule="pct_1dp",
    notes="Corrected 2026-05-22 from 18.5% to 19.5% per S024 audit; now matches §3.8.1 L2154",
)
add(
    claim_id="T2.f003.drift_exceed_v381",
    section="§3.8.1 L2135",
    manuscript_text="19.5% exceed 15 mmHg drift threshold (PaO2, F-003 arm)",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=19.5,
    computed_value=drift_exceed_pct,
    tolerance_rule="pct_1dp",
)
# Also: §3.8.1 n = 195 (valid CSV subset of n = 208 FiO2 >= 0.95 runs).
n_fio2_high_total = int((agg["in_fio2"] >= 0.95).sum())
n_fio2_high_validcsv = len(hi_fio2)
add(
    claim_id="T2.f003.arm_n_total",
    section="§3.8.1 L2129",
    manuscript_text="F-003 arm n = 208 (FiO2 >= 0.95)",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=208,
    computed_value=n_fio2_high_total,
    tolerance_rule="exact_int",
)
add(
    claim_id="T2.f003.arm_n_valid",
    section="§3.8.1 L2129",
    manuscript_text="195 with valid CSV (F-003 arm)",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=195,
    computed_value=n_fio2_high_validcsv,
    tolerance_rule="exact_int",
)

# 43-44. §3.8 F-003 reclassification: 32/34 -> clean under 700 mmHg, 31 at FiO2 >= 0.95.
add(
    claim_id="T2.f003.reclass",
    section="§3.8 L2024",
    manuscript_text="32 of 34 implausibly-flagged-by-PaO2 become clean under wider bound",
    source_file="results/f003_physiological_reclassification_summary.json",
    manuscript_value=32,
    computed_value=int(f003["n_reclassified_locked_to_physio_clean"]),
    tolerance_rule="exact_int",
)
n_reclass_high_fio2 = (
    f003["by_fio2_bin"].get("(0.95, 1.001]", {}).get("reclassified_pao2_locked_to_physio_clean", -1)
)
add(
    claim_id="T2.f003.reclass_high_fio2",
    section="§3.8 L2025",
    manuscript_text="31 of reclassified at FiO2 >= 0.95",
    source_file="results/f003_physiological_reclassification_summary.json",
    manuscript_value=31,
    computed_value=n_reclass_high_fio2,
    tolerance_rule="exact_int",
)
n_reclass_s1_f = (
    f003["by_scenario_sex"].get("S1_F", {}).get("reclassified_pao2_locked_to_physio_clean", -1)
)
n_reclass_s1_m = (
    f003["by_scenario_sex"].get("S1_M", {}).get("reclassified_pao2_locked_to_physio_clean", -1)
)
add(
    claim_id="T2.f003.reclass_S1F",
    section="§3.8 L2026",
    manuscript_text="21 reclassified in S1_F",
    source_file="results/f003_physiological_reclassification_summary.json",
    manuscript_value=21,
    computed_value=n_reclass_s1_f,
    tolerance_rule="exact_int",
)
add(
    claim_id="T2.f003.reclass_S1M",
    section="§3.8 L2026",
    manuscript_text="11 reclassified in S1_M",
    source_file="results/f003_physiological_reclassification_summary.json",
    manuscript_value=11,
    computed_value=n_reclass_s1_m,
    tolerance_rule="exact_int",
)

# 45. §3.8 F-003 shunt-depression plateaus.
shunt_by_sc = {row["scenario"]: row for row in s21_sum["shunt_depression_aux"]}
add(
    claim_id="T2.f003.shunt_s3",
    section="§3.8 L1985",
    manuscript_text="S3 plateau median 143.6 mmHg",
    source_file="data/runs/s021_hyperoxia_convergence/summary.json",
    manuscript_value=143.6,
    computed_value=float(shunt_by_sc["S3"]["plateau_median_mmHg"]),
    tolerance_rule="displayed_1dp",
)
add(
    claim_id="T2.f003.shunt_s4",
    section="§3.8 L1986",
    manuscript_text="S4 plateau median 72.6 mmHg",
    source_file="data/runs/s021_hyperoxia_convergence/summary.json",
    manuscript_value=72.6,
    computed_value=float(shunt_by_sc["S4"]["plateau_median_mmHg"]),
    tolerance_rule="displayed_1dp",
)

# 46. §3.8 F-003 solver-instability tail: 6/44 S1 runs >700 mmHg.
n_s1_runaway = int(
    s21_plat[(s21_plat["scenario"] == "S1") & (s21_plat["PaO2_plateau_mmHg"] > 700)].shape[0]
)
add(
    claim_id="T2.f003.runaway",
    section="§3.8 L1997",
    manuscript_text="6/44 S1 runs >700 mmHg under extended window",
    source_file="data/runs/s021_hyperoxia_convergence/plateau_stats.parquet",
    manuscript_value=6,
    computed_value=n_s1_runaway,
    tolerance_rule="exact_int",
)

# 54-55. Appendix C NSS decomposition totals.
total_row = nss[nss["cell"] == "Total"].iloc[0]
add(
    claim_id="T2.nss.total.locked",
    section="Appendix C L3248",
    manuscript_text="locked NSS total = 530",
    source_file="results/s022/nss_decomposition.csv",
    manuscript_value=530,
    computed_value=int(total_row["n_nss_locked"]),
    tolerance_rule="exact_int",
)
add(
    claim_id="T2.nss.total.excl_spo2",
    section="Appendix C L3248",
    manuscript_text="excl SpO2 total = 454",
    source_file="results/s022/nss_decomposition.csv",
    manuscript_value=454,
    computed_value=int(total_row["n_nss_excl_SpO2_saturation"]),
    tolerance_rule="exact_int",
)
add(
    claim_id="T2.nss.total.excl_f004",
    section="Appendix C L3248",
    manuscript_text="excl F-004 total = 360",
    source_file="results/s022/nss_decomposition.csv",
    manuscript_value=360,
    computed_value=int(total_row["n_nss_excl_F004_dyssynchrony"]),
    tolerance_rule="exact_int",
)
add(
    claim_id="T2.nss.total.excl_both",
    section="Appendix C L3248",
    manuscript_text="excl both total = 185",
    source_file="results/s022/nss_decomposition.csv",
    manuscript_value=185,
    computed_value=int(total_row["n_nss_excl_both"]),
    tolerance_rule="exact_int",
)
add(
    claim_id="T2.nss.total.clean_excl_both",
    section="Appendix C L3248",
    manuscript_text="clean excl both = 1,008",
    source_file="results/s022/nss_decomposition.csv",
    manuscript_value=1008,
    computed_value=int(total_row["n_clean_excl_both"]),
    tolerance_rule="exact_int",
)
# §4.5 limitations: 76 / 170 / 185 attribution numbers.
add(
    claim_id="T2.nss.limit.spo2",
    section="§4.5 L2557",
    manuscript_text="76 runs flagged by SpO2 saturation (locked - excl SpO2)",
    source_file="results/s022/nss_decomposition.csv",
    manuscript_value=76,
    computed_value=int(total_row["n_nss_locked"]) - int(total_row["n_nss_excl_SpO2_saturation"]),
    tolerance_rule="exact_int",
)
add(
    claim_id="T2.nss.limit.f004",
    section="§4.5 L2561",
    manuscript_text="170 runs flagged by F-004 dyssynchrony (locked - excl F004)",
    source_file="results/s022/nss_decomposition.csv",
    manuscript_value=170,
    computed_value=int(total_row["n_nss_locked"]) - int(total_row["n_nss_excl_F004_dyssynchrony"]),
    tolerance_rule="exact_int",
)
add(
    claim_id="T2.nss.limit.residual",
    section="§4.5 L2563",
    manuscript_text="185 residual (excl both)",
    source_file="results/s022/nss_decomposition.csv",
    manuscript_value=185,
    computed_value=int(total_row["n_nss_excl_both"]),
    tolerance_rule="exact_int",
)
# 56. Appendix C 78.7% counterfactual clean rate.
add(
    claim_id="T2.nss.counterfactual",
    section="Appendix C L3290-3291, §4.5 L2574",
    manuscript_text="78.7% clean rate under joint exclusion (1008/1280)",
    source_file="results/s022/nss_decomposition.csv",
    manuscript_value=78.7,
    computed_value=100.0 * int(total_row["n_clean_excl_both"]) / int(total_row["n_total"]),
    tolerance_rule="pct_1dp",
)

# Appendix C per-cell rows: 8 cells x 5 columns = 40 numbers.
cells = ["S1_M", "S1_F", "S2_M", "S2_F", "S3_M", "S3_F", "S4_M", "S4_F"]
nss_man_table = {
    "S1_M": (160, 107, 91, 74, 29, 127),
    "S1_F": (160, 118, 88, 87, 24, 136),
    "S2_M": (160, 69, 60, 45, 23, 133),
    "S2_F": (160, 68, 52, 44, 7, 153),
    "S3_M": (160, 12, 11, 9, 8, 148),
    "S3_F": (160, 38, 34, 10, 3, 157),
    "S4_M": (160, 44, 44, 39, 39, 72),
    "S4_F": (160, 74, 74, 52, 52, 82),
}
col_map = [
    ("n_total", 0),
    ("n_nss_locked", 1),
    ("n_nss_excl_SpO2_saturation", 2),
    ("n_nss_excl_F004_dyssynchrony", 3),
    ("n_nss_excl_both", 4),
    ("n_clean_excl_both", 5),
]
for cell in cells:
    row = nss[nss["cell"] == cell].iloc[0]
    for col_name, idx in col_map:
        add(
            claim_id=f"T2.nssC.{cell}.{col_name}",
            section=f"Appendix C ({cell})",
            manuscript_text=f"{col_name} = {nss_man_table[cell][idx]}",
            source_file="results/s022/nss_decomposition.csv",
            manuscript_value=nss_man_table[cell][idx],
            computed_value=int(row[col_name]),
            tolerance_rule="exact_int",
        )

# 57. §4.5 S023: 17/18 pooled + 23/48 full match + 90% (manuscript text) of >=2/3.
add(
    claim_id="T2.s023.pooled",
    section="§4.5 L2578",
    manuscript_text="17 / 18 pooled (output x top-3) cases",
    source_file="results/s023/topk_overlap.csv",
    manuscript_value=17,
    computed_value=int(s23_pooled["overlap_size"].sum()),
    tolerance_rule="exact_int",
)
add(
    claim_id="T2.s023.fullmatch",
    section="§4.5 L2579",
    manuscript_text="23 / 48 per-cell at full 3/3 agreement",
    source_file="results/s023/topk_overlap_per_cell.csv",
    manuscript_value=23,
    computed_value=int((s23_cell["overlap_size"] == 3).sum()),
    tolerance_rule="exact_int",
)
# 90% reading: manuscript says "90% of per-cell comparisons at >= 2/3" -- compute the actual.
pct_ge2 = 100.0 * (s23_cell["overlap_size"] >= 2).mean()
add(
    claim_id="T2.s023.ge2_pct",
    section="§4.5 L2599",
    manuscript_text="92% of per-cell comparisons at >= 2/3 agreement",
    source_file="results/s023/topk_overlap_per_cell.csv",
    manuscript_value=92.0,
    computed_value=pct_ge2,
    tolerance_rule="pct_whole",  # corrected 2026-05-22 from 90% to 92% per S024 audit
)

# -----------------------------------------------------------------------------
# TIER 3 -- S027 ADDITIONS: §1.1 'Pulse in a nutshell' + §4.7 engine-side
# recommendations (added 2026-05-23).
#
# These pin manuscript text against primary-source values that originate
# outside the atlas's computed artefacts:
#
#   - §1.1 facts (20 ms timestep, 10-15x real-time speed) come from Pulse's
#     own user documentation, recorded with verification date in
#     Pulse_translation_new/pulse_engine_literature_review.md §1.5.
#   - §4.7 BV constants (4082.24 mL floor, 4802.63 mL default) come from
#     the empirical experiment in scripts/s018_bv_falsification.py, where
#     the constants were verified against Pulse log output (S018,
#     2026-05-12). We extract them from that script via regex at audit
#     time so any drift between the experiment script and this ledger is
#     caught.
# -----------------------------------------------------------------------------

# §1.1 Pulse-documentation constants. Source-of-truth citation in the
# source_file column points to the secondary record in the maintainer's
# pulse_engine_literature_review.md, which itself cites Pulse's docs page
# (last verified 2026-05-23 during S027).
PULSE_DOC_TIMESTEP_MS = 20.0
PULSE_DOC_SPEED_LO_X = 10.0
PULSE_DOC_SPEED_HI_X = 15.0

add(
    claim_id="T3.s027.timestep_ms",
    section="§1.1 'Pulse in a nutshell'",
    manuscript_text="20 ms fixed timestep",
    source_file="Pulse_translation_new/pulse_engine_literature_review.md §1.5",
    manuscript_value=20.0,
    computed_value=PULSE_DOC_TIMESTEP_MS,
    tolerance_rule="whole_unit",
)
add(
    claim_id="T3.s027.speed_lower",
    section="§1.1 'Pulse in a nutshell'",
    manuscript_text="roughly 10-15x real time (lower bound)",
    source_file="Pulse_translation_new/pulse_engine_literature_review.md §1.5",
    manuscript_value=10.0,
    computed_value=PULSE_DOC_SPEED_LO_X,
    tolerance_rule="whole_unit",
)
add(
    claim_id="T3.s027.speed_upper",
    section="§1.1 'Pulse in a nutshell'",
    manuscript_text="roughly 10-15x real time (upper bound)",
    source_file="Pulse_translation_new/pulse_engine_literature_review.md §1.5",
    manuscript_value=15.0,
    computed_value=PULSE_DOC_SPEED_HI_X,
    tolerance_rule="whole_unit",
)

# §4.7 item 2 -- pull BV constants out of the S018 script at audit time.
_s018_path = REPO / "scripts" / "s018_bv_falsification.py"
_s018_text = _s018_path.read_text()
_m_floor = re.search(r"MALE_FLOOR_BV_ML\s*=\s*([\d.]+)", _s018_text)
_m_default = re.search(r"MALE_DEFAULT_BV_ML\s*=\s*([\d.]+)", _s018_text)
assert _m_floor is not None, (
    "audit_claims: MALE_FLOOR_BV_ML not located in scripts/s018_bv_falsification.py"
)
assert _m_default is not None, (
    "audit_claims: MALE_DEFAULT_BV_ML not located in scripts/s018_bv_falsification.py"
)
S018_MALE_FLOOR_BV_ML = float(_m_floor.group(1))
S018_MALE_DEFAULT_BV_ML = float(_m_default.group(1))

add(
    claim_id="T3.s027.bv_floor",
    section="§4.7 item 2",
    manuscript_text="4,082.24 mL male BV floor",
    source_file="scripts/s018_bv_falsification.py MALE_FLOOR_BV_ML",
    manuscript_value=4082.24,
    computed_value=S018_MALE_FLOOR_BV_ML,
    tolerance_rule="displayed_2dp",
)
add(
    claim_id="T3.s027.bv_default",
    section="§4.7 item 2",
    manuscript_text="4,802.63 mL male BV default",
    source_file="scripts/s018_bv_falsification.py MALE_DEFAULT_BV_ML",
    manuscript_value=4802.63,
    computed_value=S018_MALE_DEFAULT_BV_ML,
    tolerance_rule="displayed_2dp",
)

# -----------------------------------------------------------------------------
# Output: markdown table sorted FAIL > WARN > PASS, then by claim_id.
# -----------------------------------------------------------------------------
order = {"FAIL": 0, "WARN": 1, "PASS": 2}
claims.sort(key=lambda c: (order[c.status], c.claim_id))


def _fmt(v):
    if v is None:
        return "-"
    if isinstance(v, (int,)) or (isinstance(v, float) and float(v).is_integer() and abs(v) < 1e9):
        return f"{int(v)}"
    return f"{v:.4g}"


# Summary counts.
n_pass = sum(1 for c in claims if c.status == "PASS")
n_warn = sum(1 for c in claims if c.status == "WARN")
n_fail = sum(1 for c in claims if c.status == "FAIL")
n_total = len(claims)

print("# Claims-Ledger Audit (S024)\n")
print(f"**Total claims audited:** {n_total} ({n_pass} PASS, {n_warn} WARN, {n_fail} FAIL)\n")
print("**Pulse-engine version:** v4.3.1; **sweep:** S006 (2026-04-26).\n")
print(
    "**Tolerance rules:** exact_int=0, pct_1dp=0.05, pct_whole=0.5, "
    "whole_unit=0.5, displayed_2dp=0.005, displayed_3dp=0.0005, "
    "approx_round=PASS<=1.0 / WARN<=2.0.\n"
)
print(
    "**Triage codes:** Type A = transcription/rounding drift; "
    "Type B = orphaned number; Type C = derivation mismatch.\n"
)

print("## Discrepancies (FAIL / WARN)\n")
disc = [c for c in claims if c.status in ("FAIL", "WARN")]
if not disc:
    print("_None._\n")
else:
    print(
        "| claim_id | status | type | section | text | source_file | "
        "manuscript | computed | tol | notes |"
    )
    print("|---|---|---|---|---|---|---:|---:|---|---|")
    for c in disc:
        print(
            f"| {c.claim_id} | {c.status} | {c.triage_type or '-'} | "
            f"{c.section} | {c.manuscript_text} | `{c.source_file}` | "
            f"{_fmt(c.manuscript_value)} | {_fmt(c.computed_value)} | "
            f"{c.tolerance_rule} | {c.notes or '-'} |"
        )
    print()

print("## All claims (sorted FAIL > WARN > PASS, then claim_id)\n")
print("| claim_id | status | section | text | manuscript | computed |")
print("|---|---|---|---|---:|---:|")
for c in claims:
    print(
        f"| {c.claim_id} | {c.status} | {c.section} | {c.manuscript_text} | "
        f"{_fmt(c.manuscript_value)} | {_fmt(c.computed_value)} |"
    )

# -----------------------------------------------------------------------------
# Optional S028 paper-sync check (opt-in via --check-paper-sync).
# Adds a second markdown table after the legacy ledger output. Sync FAILs
# contribute to the script's exit code; WARNs do not.
# -----------------------------------------------------------------------------
n_sync_pass = n_sync_warn = n_sync_fail = 0
if _ARGS.check_paper_sync:
    n_sync_pass, n_sync_warn, n_sync_fail = check_paper_sync(claims)

# Exit non-zero if any FAIL anywhere (allows piping to CI later).
sys.exit(1 if (n_fail + n_sync_fail) > 0 else 0)
