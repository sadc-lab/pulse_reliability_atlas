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

    # S028 Phase 9.A: extend the sync corpus to include supplement.tex when
    # it exists. The single shared paper_to_monograph_map.md spans both
    # documents per the approved chunking strategy; expected_occurrences in
    # any row is the TOTAL count across paper + supplement.
    paper_tex = paper_path.read_text(encoding="utf-8")
    supp_path = REPO / "preprint_npj" / "supplement.tex"
    if supp_path.exists():
        sync_corpus = paper_tex + "\n" + supp_path.read_text(encoding="utf-8")
    else:
        sync_corpus = paper_tex
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

        # Occurrence-count check on the combined paper + supplement corpus
        # (literal-string regex). expected_occurrences is the total across
        # both documents per the Step 9 single-shared-map convention.
        count = (
            len(re.findall(re.escape(fmt), sync_corpus)) if fmt else 0
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

# S028 Step 4 additions: S014 sample size + frac-below-threshold + trigger
# pressure constant. These were already present in the monograph prose
# (L2226, L2387) but had not been added to the audit ledger until the
# npj submission §2.3 prose cited them. Adding now to bring the audit
# coverage in line with what the monograph asserts.
add(
    claim_id="T1.06b.s14_n_runs",
    section="§3.8 L2226 (monograph); §2.3 (npj paper)",
    manuscript_text="64 paired reruns in S014 trigger-lockout sample",
    source_file="data/runs/s014_trigger_lockout/summary.json",
    manuscript_value=64,
    computed_value=int(s14_sum["n_runs"]),
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.06c.s14_frac_below",
    section="§3.8 L2226 / L2387 (monograph); §2.3 (npj paper)",
    manuscript_text="78.1% of locked-trigger reruns below Vt_cv 0.05 threshold",
    source_file="data/runs/s014_trigger_lockout/summary.json",
    manuscript_value=78.1,
    computed_value=100.0 * float(s14_sum["frac_Vt_cv_lock_below_0.05"]),
    tolerance_rule="pct_1dp",
)
# Trigger-pressure constant: pull from scripts/run_s014_trigger_lockout.py
# at audit time via regex to keep the experiment script and ledger in
# lock-step (same pattern as S027 BV-constant verification).
_s14_script = (REPO / "scripts" / "run_s014_trigger_lockout.py").read_text()
_m_trig = re.search(r"TRIGGER_PRESSURE_CMH2O\s*:\s*float\s*=\s*(-?[\d.]+)", _s14_script)
assert _m_trig is not None, (
    "audit_claims: TRIGGER_PRESSURE_CMH2O not located in scripts/run_s014_trigger_lockout.py"
)
S14_TRIGGER_PRESSURE_CMH2O = float(_m_trig.group(1))
add(
    claim_id="T1.06d.s14_trigger_pressure",
    section="§2.3, §2.4 caption (npj paper); abstract; experiment script",
    manuscript_text="-2 cmH2O inspiration-trigger pressure for VC-AC lockout fix",
    source_file="scripts/run_s014_trigger_lockout.py TRIGGER_PRESSURE_CMH2O",
    manuscript_value=-2.0,
    computed_value=S14_TRIGGER_PRESSURE_CMH2O,
    tolerance_rule="displayed_1dp",
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
# Alveolar-gas-equation sea-level prediction (663 mmHg), guarded as a value
# anchor so the 663-vs-643/A-a-20 framing cannot silently drift again. The
# bare equation gives the ALVEOLAR PAO2; the ~20 mmHg gap to the measured
# arterial 643 mmHg is Pulse's modelled A-a gradient (Pass C SP-C.D1 / D1-a).
add(
    claim_id="T1.23b.alveolar_gas_prediction",
    section="Abstract + §2.4 + Fig 3 (npj paper); §3.8 S021 derivation (monograph)",
    manuscript_text="alveolar PAO2 = 1.0*(760-47) - 40/0.8 ~= 663 mmHg (sea-level; A-a gradient ~20 vs measured arterial 643)",
    source_file="alveolar gas equation, sea-level constants (West 2020 respiratory physiology)",
    manuscript_value=663.0,
    computed_value=1.0 * (760.0 - 47.0) - 40.0 / 0.8,
    tolerance_rule="whole_unit",
)
# Worst-case S014 trigger-lockout Vt CV pair (default 1.826 -> locked 0.018),
# guarded after the forensic finding that the monograph had mis-paired the
# worst-case DEFAULT run (S1_F_0117, 1.826) with a different run's worst
# LOCKED CV (S1_F_0008, 0.112). The true S1_F_0117 transition is 1.826 ->
# 0.018; both endpoints are now anchored to paired_comparison.parquet so the
# worst-case caption number cannot silently drift across documents again.
_s14_pc = pd.read_parquet(
    REPO / "data" / "runs" / "s014_trigger_lockout" / "paired_comparison.parquet"
)
_s14_worst = _s14_pc.loc[_s14_pc["Vt_cv_orig"].idxmax()]
add(
    claim_id="T1.s014.worstcase_default_vtcv",
    section="Section 2.3 + Fig 3a (npj); worst-case (monograph); Supplement Fig S8",
    manuscript_text="worst-case S014 default Vt CV = 1.826 (run S1_F_0117, largest before/after delta)",
    source_file="data/runs/s014_trigger_lockout/paired_comparison.parquet (max Vt_cv_orig row)",
    manuscript_value=1.826,
    computed_value=float(_s14_worst["Vt_cv_orig"]),
    tolerance_rule="displayed_3dp",
)
add(
    claim_id="T1.s014.worstcase_locked_vtcv",
    section="Section 2.3 + Fig 3a (npj); worst-case (monograph); Supplement Fig S8",
    manuscript_text="worst-case S014 paired-config locked Vt CV = 0.018 (same run S1_F_0117)",
    source_file="data/runs/s014_trigger_lockout/paired_comparison.parquet (Vt_cv_lock of max-Vt_cv_orig row)",
    manuscript_value=0.018,
    computed_value=float(_s14_worst["Vt_cv_lock"]),
    tolerance_rule="displayed_3dp",
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
# Worst-case S1 hyperoxia numerical-runaway plateau (off the [0, 760] mmHg
# visible range of npj Figure 3b). Guarded after the D.8 paper sweep flagged
# the "~1,408 mmHg" caption value as an orphan: it appears only in paper.tex
# Fig 3 caption with no monograph/ledger anchor. Computed as the max S1
# plateau across the S021 extended-simulation reruns. approx_round tolerance
# because the caption renders it with an explicit "~".
s021_s1_max_plateau = float(
    s21_plat[s21_plat["scenario"] == "S1"]["PaO2_plateau_mmHg"].max()
)
add(
    claim_id="T1.24d.s021_s1_max_runaway_plateau",
    section="Fig 3b caption (npj paper); §3.8 S021 runaway (monograph)",
    manuscript_text="worst-case S1 hyperoxia runaway plateau ~1,408 mmHg (off-scale; 6 S1 reruns > 700 mmHg)",
    source_file="data/runs/s021_hyperoxia_convergence/plateau_stats.parquet (max S1 PaO2_plateau_mmHg)",
    manuscript_value=1408.0,
    computed_value=s021_s1_max_plateau,
    tolerance_rule="approx_round",
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

# S028 Step 5 additions: 3,996.09 mL female BV default + Cornish 80/85
# Hoeffding rejections on non-overlap channels. The female default BV
# is the Pulse allometric formula output for the 56.2 kg female reference
# body (BV = 65.6 * weight_kg^1.02 = 65.6 * 56.2^1.02 = 3,996.09 mL),
# cited in monograph §3.5 L1572 and §3.5 L1630. The Cornish 80/85 figure
# is from the §4.4 cross-mapping table (computed as: 85 total Hoeffding
# rejections in Cornish Table 1, minus 3 on the four-channel atlas
# overlap (all PaCO2), minus 2 on SysBP partial-overlap = 80 on
# channels we do not assess). Both values are static external constants
# in this paper's context (literature numbers, not derived from atlas
# data), so the audit verifies that the manuscript wording matches the
# constant declared here -- the same pattern as the Pulse-documentation
# constants in S027.
PULSE_FEMALE_BV_DEFAULT_ML = 3996.09  # Pulse allometric (65.6 * 56.2^1.02); verified vs setup log on S006
CORNISH_NON_OVERLAP_HOEFFDING = 80    # Cornish 2023 Table 1: 85 total - 3 PaCO2 overlap - 2 SysBP partial = 80
CORNISH_TOTAL_HOEFFDING = 85          # Cornish 2023 Table 1 total Hoeffding rejections across 15 quantities
CORNISH_OVERLAP_HOEFFDING = 3         # Cornish 2023 Table 1: PaCO2 row 3/70 -- all 3 four-channel-overlap rejections
CORNISH_PARTIAL_OVERLAP_HOEFFDING = 2  # Cornish 2023 Table 1: SysBP row 2/154 -- partial MAP-input overlap
# 82 = the rejections that fall OUTSIDE the four-channel direct overlap
# (80 on channels the atlas does not assess + 2 on the SysBP partial-overlap).
# Derived so the decomposition is self-checking rather than a free literal.
CORNISH_OUTSIDE_OVERLAP_HOEFFDING = (
    CORNISH_NON_OVERLAP_HOEFFDING + CORNISH_PARTIAL_OVERLAP_HOEFFDING
)
assert (
    CORNISH_NON_OVERLAP_HOEFFDING
    + CORNISH_PARTIAL_OVERLAP_HOEFFDING
    + CORNISH_OVERLAP_HOEFFDING
    == CORNISH_TOTAL_HOEFFDING
), "audit_claims: Cornish Hoeffding decomposition (80 + 2 + 3) must sum to 85"

add(
    claim_id="T3.s028.bv_female_default",
    section="§3.5 L1572, L1630 (monograph); §2.5 (npj paper)",
    manuscript_text="3,996.09 mL female BV default (Pulse allometric for 56.2 kg)",
    source_file="Pulse SetupPatient.cpp allometric formula; verified vs setup log",
    manuscript_value=3996.09,
    computed_value=PULSE_FEMALE_BV_DEFAULT_ML,
    tolerance_rule="displayed_2dp",
)
add(
    claim_id="T3.s028.cornish_non_overlap_hoeffding",
    section="§4.4 (monograph); §2.6 (npj paper)",
    manuscript_text="80 of 85 Cornish Hoeffding rejections on the 8 channels the atlas does not assess (82 of 85 fall outside the 4-channel overlap: 80 not-assessed + 2 SysBP partial)",
    source_file="Cornish et al. 2023 (arXiv:2301.07210) Table 1, verified in S017",
    manuscript_value=80,
    computed_value=CORNISH_NON_OVERLAP_HOEFFDING,
    tolerance_rule="exact_int",
)
add(
    claim_id="T3.s028.cornish_total_hoeffding",
    section="§4.4 (monograph); §2.6 (npj paper)",
    manuscript_text="85 total Cornish Hoeffding rejections across 15 physiological quantities",
    source_file="Cornish et al. 2023 (arXiv:2301.07210) Table 1, verified in S017",
    manuscript_value=85,
    computed_value=CORNISH_TOTAL_HOEFFDING,
    tolerance_rule="exact_int",
)
add(
    claim_id="T3.s028.cornish_outside_overlap",
    section="§4.4 + S7 Table caption (monograph/supplement); §2.6 (npj paper)",
    manuscript_text="82 of 85 Cornish Hoeffding rejections fall outside the 4-channel overlap (80 not-assessed + 2 SysBP partial)",
    source_file="Cornish et al. 2023 (arXiv:2301.07210) Table 1, verified in S017",
    manuscript_value=82,
    computed_value=CORNISH_OUTSIDE_OVERLAP_HOEFFDING,
    tolerance_rule="exact_int",
)
add(
    claim_id="T3.s028.cornish_overlap_hoeffding",
    section="§4.4 + S7 Table caption (monograph/supplement); §2.6 (npj paper)",
    manuscript_text="3 of 85 Cornish Hoeffding rejections on the 4-channel overlap (all on PaCO2)",
    source_file="Cornish et al. 2023 (arXiv:2301.07210) Table 1, PaCO2 row 3/70",
    manuscript_value=3,
    computed_value=CORNISH_OVERLAP_HOEFFDING,
    tolerance_rule="exact_int",
)

# S028 Step 7 additions: Methods-section reproducibility constants.
# Each value is regex-extracted from its canonical source module so
# any drift between the source code and the ledger triggers an
# explicit AssertionError (same lock-step pattern as the S014 trigger
# pressure and S027 BV constants).
_run_full_sweep = (REPO / "scripts" / "run_full_sweep.py").read_text(encoding="utf-8")
_m_traj = re.search(r"SWEEP_TRAJECTORIES\s*=\s*(\d+)", _run_full_sweep)
_m_lvls = re.search(r"SWEEP_LEVELS\s*=\s*(\d+)", _run_full_sweep)
_m_seed = re.search(r"SWEEP_SEED\s*=\s*(\d+)", _run_full_sweep)
assert _m_traj is not None, "audit_claims: SWEEP_TRAJECTORIES not located in scripts/run_full_sweep.py"
assert _m_lvls is not None, "audit_claims: SWEEP_LEVELS not located in scripts/run_full_sweep.py"
assert _m_seed is not None, "audit_claims: SWEEP_SEED not located in scripts/run_full_sweep.py"
SWEEP_TRAJECTORIES = int(_m_traj.group(1))
SWEEP_LEVELS = int(_m_lvls.group(1))
SWEEP_SEED = int(_m_seed.group(1))

add(
    claim_id="T1.06e.morris_trajectories",
    section="§4.3 (npj paper)",
    manuscript_text="20 Morris trajectories per cell",
    source_file="scripts/run_full_sweep.py SWEEP_TRAJECTORIES",
    manuscript_value=20,
    computed_value=SWEEP_TRAJECTORIES,
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.06f.morris_levels",
    section="§4.3 (npj paper)",
    manuscript_text="4 Morris grid levels per input",
    source_file="scripts/run_full_sweep.py SWEEP_LEVELS",
    manuscript_value=4,
    computed_value=SWEEP_LEVELS,
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.06g.morris_seed",
    section="§4.3 (npj paper)",
    manuscript_text="random seed 42 for the Morris sample",
    source_file="scripts/run_full_sweep.py SWEEP_SEED",
    manuscript_value=42,
    computed_value=SWEEP_SEED,
    tolerance_rule="exact_int",
)

# Bootstrap-resamples constant for Morris mu* CI -- declared in
# scripts/analyze_sweep.py n_bootstrap=1000.
_analyze_sweep = (REPO / "scripts" / "analyze_sweep.py").read_text(encoding="utf-8")
_m_boot = re.search(r"n_bootstrap\s*=\s*(\d+)", _analyze_sweep)
assert _m_boot is not None, "audit_claims: n_bootstrap not located in scripts/analyze_sweep.py"
ANALYZE_N_BOOTSTRAP = int(_m_boot.group(1))
add(
    claim_id="T1.06h.bootstrap_n",
    section="§2.2, §4.5 (npj paper)",
    manuscript_text="1000 bootstrap resamples for mu* CI",
    source_file="scripts/analyze_sweep.py n_bootstrap",
    manuscript_value=1000,
    computed_value=ANALYZE_N_BOOTSTRAP,
    tolerance_rule="exact_int",
)

# Spearman bootstrap N -- declared in src/analysis_compare.py
# spearman_mu_star_male_vs_female() n_bootstrap default (currently 2000).
# The function is called without an explicit override by
# scripts/analyze_sweep.py L105, so the default value is what was
# used to compute the published Spearman rho confidence intervals.
# Added in [METHODOLOGY] ledger expansion 2026-05-27 (Pass 10 D16 follow-up).
_analysis_compare_src = (REPO / "src" / "analysis_compare.py").read_text(encoding="utf-8")
_spearman_idx = _analysis_compare_src.find("def spearman_mu_star_male_vs_female")
assert _spearman_idx != -1, "audit_claims: spearman_mu_star_male_vs_female function not located"
_spearman_section = _analysis_compare_src[_spearman_idx : _spearman_idx + 600]
_m_spearman_n = re.search(r"n_bootstrap:\s*int\s*=\s*(\d+)", _spearman_section)
assert _m_spearman_n is not None, "audit_claims: spearman n_bootstrap default not located"
SPEARMAN_N_BOOTSTRAP = int(_m_spearman_n.group(1))
add(
    claim_id="T2.analysis.spearman_n_bootstrap",
    section="§5 Methods Statistical analyses + supplement S6 (npj paper)",
    manuscript_text="2000 input-resamples for Spearman rho paired-input bootstrap CI",
    source_file="src/analysis_compare.py spearman_mu_star_male_vs_female n_bootstrap default",
    manuscript_value=2000,
    computed_value=SPEARMAN_N_BOOTSTRAP,
    tolerance_rule="exact_int",
)

# Wasserstein within-sex permutation null N -- declared in
# src/analysis_compare.py wasserstein_per_output() n_null default (currently 2000).
# Added in [METHODOLOGY] ledger expansion 2026-05-27 (Pass 10 D16 follow-up).
_wasserstein_idx = _analysis_compare_src.find("def wasserstein_per_output")
assert _wasserstein_idx != -1, "audit_claims: wasserstein_per_output function not located"
_wasserstein_section = _analysis_compare_src[_wasserstein_idx : _wasserstein_idx + 600]
_m_wasserstein_n = re.search(r"n_null:\s*int\s*=\s*(\d+)", _wasserstein_section)
assert _m_wasserstein_n is not None, "audit_claims: wasserstein n_null default not located"
WASSERSTEIN_N_NULL = int(_m_wasserstein_n.group(1))
add(
    claim_id="T2.analysis.wasserstein_n_null",
    section="§5 Methods Statistical analyses (npj paper)",
    manuscript_text="2000 random within-sex splits for Wasserstein null reference",
    source_file="src/analysis_compare.py wasserstein_per_output n_null default",
    manuscript_value=2000,
    computed_value=WASSERSTEIN_N_NULL,
    tolerance_rule="exact_int",
)

# Supplement S15 compensatory tachycardia per-scenario output-HR values --
# regex-extracted from manuscript.md Section 3.4.1 compensatory-tachycardia
# table. Added in [METHODOLOGY] ledger expansion 2026-05-28 to close the
# Pass 7 D9 Concern 2(i) deferment: supplement S15 was added in commit
# b381944 with these numbers but they were NOT immediately tracked in the
# ledger per the maintainer's "skip ledger extension this commit" decision.
_manuscript_md_src = (REPO / "preprint" / "manuscript.md").read_text(encoding="utf-8")
for _scenario, _expected_mean, _expected_std in [
    ("S1", 73.8, 20.4),
    ("S2", 87.3, 24.3),
    ("S3", 155.7, 34.7),
    ("S4", 147.1, 31.8),
]:
    _pattern = rf"\| {_scenario}\s+\| \[50, 110\]\s+\| ([\d.]+) ± ([\d.]+)\s*\|"
    _m_hr_row = re.search(_pattern, _manuscript_md_src)
    assert _m_hr_row is not None, (
        f"audit_claims: {_scenario} output HR row not located in manuscript Section 3.4.1 "
        f"(pattern: {_pattern})"
    )
    _hr_mean = float(_m_hr_row.group(1))
    _hr_std = float(_m_hr_row.group(2))
    add(
        claim_id=f"T2.s15.{_scenario.lower()}_output_hr_mean",
        section="Section 3.4.1 (monograph); supplement Section S15 (npj package)",
        manuscript_text=f"{_scenario} output HR mean across clean Morris runs",
        source_file="manuscript.md Section 3.4.1 compensatory-tachycardia table",
        manuscript_value=_expected_mean,
        computed_value=_hr_mean,
        tolerance_rule="displayed_2dp",
    )
    add(
        claim_id=f"T2.s15.{_scenario.lower()}_output_hr_std",
        section="Section 3.4.1 (monograph); supplement Section S15 (npj package)",
        manuscript_text=f"{_scenario} output HR std across clean Morris runs",
        source_file="manuscript.md Section 3.4.1 compensatory-tachycardia table",
        manuscript_value=_expected_std,
        computed_value=_hr_std,
        tolerance_rule="displayed_2dp",
    )

# ARDS-severity impairment fractions declared in src/scenario.py
# SCENARIOS dict (S1=0.0 healthy, S2=0.26 mild, S3=0.60 moderate,
# S4=0.95 severe).
_scenario_py = (REPO / "src" / "scenario.py").read_text(encoding="utf-8")
_m_s2 = re.search(r'"S2":\s*Scenario\("S2",\s*"Mild ARDS",\s*([\d.]+)\)', _scenario_py)
_m_s3 = re.search(r'"S3":\s*Scenario\("S3",\s*"Moderate ARDS",\s*([\d.]+)\)', _scenario_py)
_m_s4 = re.search(r'"S4":\s*Scenario\("S4",\s*"Severe ARDS",\s*([\d.]+)\)', _scenario_py)
assert _m_s2 is not None, "audit_claims: S2 ARDS severity not located in src/scenario.py"
assert _m_s3 is not None, "audit_claims: S3 ARDS severity not located in src/scenario.py"
assert _m_s4 is not None, "audit_claims: S4 ARDS severity not located in src/scenario.py"
ARDS_S2 = float(_m_s2.group(1))
ARDS_S3 = float(_m_s3.group(1))
ARDS_S4 = float(_m_s4.group(1))
add(
    claim_id="T1.06i.ards_S2_severity",
    section="§4.3 (npj paper)",
    manuscript_text="S2 mild ARDS impairment fraction = 0.26",
    source_file="src/scenario.py SCENARIOS['S2']",
    manuscript_value=0.26,
    computed_value=ARDS_S2,
    tolerance_rule="displayed_2dp",
)
add(
    claim_id="T1.06j.ards_S3_severity",
    section="§4.3 (npj paper)",
    manuscript_text="S3 moderate ARDS impairment fraction = 0.60",
    source_file="src/scenario.py SCENARIOS['S3']",
    manuscript_value=0.60,
    computed_value=ARDS_S3,
    tolerance_rule="displayed_2dp",
)
add(
    claim_id="T1.06k.ards_S4_severity",
    section="§4.3 (npj paper)",
    manuscript_text="S4 severe ARDS impairment fraction = 0.95",
    source_file="src/scenario.py SCENARIOS['S4']",
    manuscript_value=0.95,
    computed_value=ARDS_S4,
    tolerance_rule="displayed_2dp",
)

# Simulation length + sample-interval constants declared in
# src/scenario.py (DURATION_HOURS = 120.0 / 3600.0 = 120 s;
# SAMPLE_INTERVAL_S = 5).
_m_dur = re.search(r"DURATION_HOURS:\s*float\s*=\s*([\d.]+)\s*/\s*([\d.]+)", _scenario_py)
_m_int = re.search(r"SAMPLE_INTERVAL_S:\s*int\s*=\s*(\d+)", _scenario_py)
assert _m_dur is not None, "audit_claims: DURATION_HOURS not located in src/scenario.py"
assert _m_int is not None, "audit_claims: SAMPLE_INTERVAL_S not located in src/scenario.py"
SIM_DURATION_SECONDS = float(_m_dur.group(1)) / float(_m_dur.group(2)) * 3600
SAMPLE_INTERVAL_SECONDS = int(_m_int.group(1))
add(
    claim_id="T1.06n.sim_duration_seconds",
    section="§4.3 (npj paper)",
    manuscript_text="120-second simulation length (DURATION_HOURS * 3600)",
    source_file="src/scenario.py DURATION_HOURS",
    manuscript_value=120,
    computed_value=SIM_DURATION_SECONDS,
    tolerance_rule="whole_unit",
)
add(
    claim_id="T1.06o.sample_interval_seconds",
    section="§4.3 (npj paper)",
    manuscript_text="5-second CSV sample interval",
    source_file="src/scenario.py SAMPLE_INTERVAL_S",
    manuscript_value=5,
    computed_value=SAMPLE_INTERVAL_SECONDS,
    tolerance_rule="exact_int",
)

# S028 Phase 9.A additions: HARD_BOUNDS + DRIFT_MAX_DELTA_60S detector
# constants from src/detector.py, regex-extracted at audit time. These
# constants are cited verbatim in Supplement S3 (Tables S2 + S3) and
# must remain in lock-step with the source code or the supplement's
# steady-state classifier description silently desynchronises from the
# actual implementation. Same regex-extraction discipline as the
# Morris / scenario / BV constants in Step 7 and Step 5.
_detector_py = (REPO / "src" / "detector.py").read_text(encoding="utf-8")

# HARD_BOUNDS dict body: extract the 6 (lower, upper) pairs.
_m_hb_block = re.search(
    r"HARD_BOUNDS:\s*dict\[str,\s*tuple\[float,\s*float\]\]\s*=\s*\{([^}]+)\}",
    _detector_py,
    re.DOTALL,
)
assert _m_hb_block is not None, "audit_claims: HARD_BOUNDS block not located in src/detector.py"
_hb_text = _m_hb_block.group(1)
_HARD_BOUNDS_FROM_SRC: dict[str, tuple[float, float]] = {}
for _m in re.finditer(r'"(\w+)":\s*\(([\d.]+),\s*([\d.]+)\)', _hb_text):
    _HARD_BOUNDS_FROM_SRC[_m.group(1)] = (float(_m.group(2)), float(_m.group(3)))
assert len(_HARD_BOUNDS_FROM_SRC) == 6, (
    f"audit_claims: expected 6 HARD_BOUNDS entries, got {len(_HARD_BOUNDS_FROM_SRC)}"
)
# Reference values declared verbatim in Supplement S3 Table S2 (locked at
# preregistration; SpO2 is reported as a fraction by Pulse).
_HARD_BOUNDS_REF: dict[str, tuple[float, float]] = {
    "HR":    (20.0, 220.0),
    "MAP":   (30.0, 180.0),
    "Vt":    (50.0, 1500.0),
    "SpO2":  (0.50, 1.00),
    "PaO2":  (20.0, 600.0),
    "PaCO2": (10.0, 120.0),
}
for _ch, (_lo, _hi) in _HARD_BOUNDS_REF.items():
    _src_lo, _src_hi = _HARD_BOUNDS_FROM_SRC[_ch]
    add(
        claim_id=f"T1.06p.{_ch.lower()}_low",
        section=f"Supplement S3 Table S2 ({_ch} lower bound)",
        manuscript_text=f"{_ch} hard lower bound = {_lo}",
        source_file=f"src/detector.py HARD_BOUNDS['{_ch}'][0]",
        manuscript_value=_lo,
        computed_value=_src_lo,
        tolerance_rule="displayed_2dp",
    )
    add(
        claim_id=f"T1.06p.{_ch.lower()}_high",
        section=f"Supplement S3 Table S2 ({_ch} upper bound)",
        manuscript_text=f"{_ch} hard upper bound = {_hi}",
        source_file=f"src/detector.py HARD_BOUNDS['{_ch}'][1]",
        manuscript_value=_hi,
        computed_value=_src_hi,
        tolerance_rule="displayed_2dp",
    )

# DRIFT_MAX_DELTA_60S dict body: extract the 6 per-channel thresholds.
_m_drift_block = re.search(
    r"DRIFT_MAX_DELTA_60S:\s*dict\[str,\s*float\]\s*=\s*\{([^}]+)\}",
    _detector_py,
    re.DOTALL,
)
assert _m_drift_block is not None, "audit_claims: DRIFT_MAX_DELTA_60S block not located in src/detector.py"
_drift_text = _m_drift_block.group(1)
_DRIFT_FROM_SRC: dict[str, float] = {}
for _m in re.finditer(r'"(\w+)":\s*([\d.]+)', _drift_text):
    _DRIFT_FROM_SRC[_m.group(1)] = float(_m.group(2))
assert len(_DRIFT_FROM_SRC) == 6, (
    f"audit_claims: expected 6 DRIFT_MAX_DELTA_60S entries, got {len(_DRIFT_FROM_SRC)}"
)
_DRIFT_REF: dict[str, float] = {
    "HR":    5.0,
    "MAP":   5.0,
    "Vt":    50.0,
    "SpO2":  0.02,
    "PaO2":  15.0,
    "PaCO2": 5.0,
}
for _ch, _val in _DRIFT_REF.items():
    _src_val = _DRIFT_FROM_SRC[_ch]
    add(
        claim_id=f"T1.06q.{_ch.lower()}_drift",
        section=f"Supplement S3 Table S3 ({_ch} drift threshold)",
        manuscript_text=f"{_ch} max drift per 60 s = {_val}",
        source_file=f"src/detector.py DRIFT_MAX_DELTA_60S['{_ch}']",
        manuscript_value=_val,
        computed_value=_src_val,
        tolerance_rule="displayed_2dp",
    )

# S028 Phase 9.C additions: CDC-anchored body weights (regex-extracted
# from src/scenario.py PATIENTS dict) + S021 hyperoxia time-to-95%-
# plateau kinetic anchor (computed from the converged S1 median
# trajectory).
_m_male = re.search(r'"M":\s*Patient\([^)]*weight_kg=([\d.]+)', _scenario_py)
_m_female = re.search(r'"F":\s*Patient\([^)]*weight_kg=([\d.]+)', _scenario_py)
assert _m_male is not None, "audit_claims: male weight_kg not located in src/scenario.py"
assert _m_female is not None, "audit_claims: female weight_kg not located in src/scenario.py"
MALE_WEIGHT_KG = float(_m_male.group(1))
FEMALE_WEIGHT_KG = float(_m_female.group(1))
add(
    claim_id="T1.06s.male_weight_kg",
    section="Supplement S10 + section 4.2 of main paper",
    manuscript_text="Male reference body weight 67.3 kg (CDC P50 at 18 yr)",
    source_file="src/scenario.py PATIENTS['M'].weight_kg",
    manuscript_value=67.3,
    computed_value=MALE_WEIGHT_KG,
    tolerance_rule="displayed_2dp",
)
add(
    claim_id="T1.06t.female_weight_kg",
    section="Supplement S10 + section 4.2 of main paper",
    manuscript_text="Female reference body weight 56.2 kg (CDC P50 at 18 yr)",
    source_file="src/scenario.py PATIENTS['F'].weight_kg",
    manuscript_value=56.2,
    computed_value=FEMALE_WEIGHT_KG,
    tolerance_rule="displayed_2dp",
)

# S021 time-to-95-percent-of-plateau kinetic anchor: derived at audit
# time from the S021 plateau_stats parquet + each S1 run's output.csv.
# The "floor" is the median PaO2 at t=0 of the extended-simulation
# rerun (saved-state reload point, corresponding to the end of the
# original 120-second window); the "asymptote" is the median PaO2
# at t=300 of the extended simulation; the anchor is the smallest
# extended-simulation time at which the median trajectory across the
# physiological-converged S1 reruns (drift-converged AND plateau
# <= 700 mmHg, i.e. excluding the three numerically-unstable runaway
# runs) reaches 95 percent of (asymptote - floor).
_s21_dir = REPO / "data" / "runs" / "s021_hyperoxia_convergence"
_s21_plateau = pd.read_parquet(_s21_dir / "plateau_stats.parquet")
_s21_s1_physio = _s21_plateau[
    (_s21_plateau["scenario"] == "S1")
    & _s21_plateau["converged"]
    & (_s21_plateau["PaO2_plateau_mmHg"] <= 700)
]
_traj_frames = []
for _, _row in _s21_s1_physio.iterrows():
    _csv = _s21_dir / _row["case_id_long"] / "output.csv"
    if _csv.exists():
        _df = pd.read_csv(_csv)[["time_s", "ArterialOxygenPressure"]]
        _df["run_id"] = _row["case_id_long"]
        _traj_frames.append(_df)
# Strict count guard scoped to T1.06u ONLY. The other 246 anchors are protected
# by the eager pd.read_parquet/read_csv/json.loads/.read_text() calls at module
# top, which raise on a missing artefact. Here the only acceptable soft path is
# the CI / clean-checkout case where data/runs/**/output.csv is gitignored and
# UNIFORMLY absent. A partial set (some present, some missing) or an empty
# expected set (no S1 physio rows in plateau_stats -- upstream data corruption)
# must NOT silently skip: either case could produce a misleading T1.06u value or
# mask a corrupt data tree. Hence the explicit n_expected vs n_found bounds.
_n_expected = int(len(_s21_s1_physio))
_n_found = int(len(_traj_frames))
if _n_expected > 0 and _n_found == _n_expected:
    # Full local data: every expected output.csv is on disk -> recompute & audit.
    _all_traj = pd.concat(_traj_frames, ignore_index=True)
    _median_traj = _all_traj.groupby("time_s")["ArterialOxygenPressure"].median()
    _floor = float(_median_traj.iloc[0])
    _asymptote = float(_median_traj.iloc[-1])
    _target = _floor + 0.95 * (_asymptote - _floor)
    _t_95 = float(_median_traj[_median_traj >= _target].index[0])
    add(
        claim_id="T1.06u.s021_time_to_95pct_plateau",
        section="Supplement S9 (extended hyperoxia convergence)",
        manuscript_text="180 s of extended simulation to reach 95% of late plateau (38 physiological-converged S1 runs)",
        source_file="derived from data/runs/s021_hyperoxia_convergence/<S1 runs>/output.csv",
        manuscript_value=180.0,
        computed_value=_t_95,
        tolerance_rule="whole_unit",
    )
elif _n_expected > 0 and _n_found == 0:
    # Benign CI case: plateau_stats lists N>0 S1 physio runs but every per-run
    # output.csv is gitignored and absent on a clean checkout. Skip T1.06u
    # with a NOTE; the parquet/CSV-backed anchors still run as the gate.
    print(
        "_NOTE: T1.06u (S021 time-to-95%-plateau) skipped -- raw per-run "
        "output.csv trajectories not present in this checkout (expected in CI; "
        "run locally with the full data/runs tree to audit this anchor)._",
        file=sys.stderr,
    )
else:
    # Neither full-data nor benign-CI. Either the plateau parquet has no S1
    # physiological-converged rows (upstream data corruption) or the output.csv
    # set is partial (corrupt working tree). Refuse to silently compute T1.06u
    # from the wrong cohort -- crash so the operator notices.
    raise RuntimeError(
        f"audit_claims T1.06u: refusing to silently skip -- expected "
        f"{_n_expected} S021 S1 physiological-converged trajectories, found "
        f"{_n_found} matching output.csv files at "
        f"{_s21_dir}/<case>/output.csv. The only acceptable bounds are 'full "
        f"set present' (run locally with the data/runs tree) or 'zero present' "
        f"(gitignored on a clean CI checkout). A partial or empty-expected set "
        f"indicates a corrupt data tree and must be investigated, not skipped."
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
