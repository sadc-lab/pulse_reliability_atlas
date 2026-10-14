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
import math
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd

# Windows consoles default to cp1252, which cannot encode characters that
# occur verbatim in the documents this script audits -- the arrow in the
# monograph's "0.351 -> 0.016" being the first to bite. An audit report must
# print its patterns exactly as they appear in the source, so force UTF-8
# rather than substituting or crashing. No-op where stdout is already UTF-8.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

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
_PARSER.add_argument(
    "--check-monograph",
    action="store_true",
    help=(
        "Also verify that the monograph-only numerical claims declared in "
        "preprint/monograph_anchor_map.md still occur in "
        "preprint/manuscript.md at least min_occurrences times. Opt-in flag; "
        "presence guard only -- it detects drift, it does not verify "
        "correctness (see the map's header)."
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

# Anchors that COULD be registered but were not evaluated this run because a
# required artefact is absent (only the documented benign-skip path is allowed;
# see the T1.06u guard below). Each entry is (claim_id, reason). The summary
# reports the target total as len(claims) + len(skipped), so the headline ratio
# stays honest in every environment: full local data tree -> N/N, public clone
# (raw S021 trajectories gitignored) -> (N-1)/N with 1 SKIPPED. No example
# value of N is written here on purpose: N is computed at run time, and a
# hard-coded illustration is precisely what went stale between 2026-07-24 and
# 2026-08-03, while the ledger grew from 267 to 289 anchors.
skipped: list[tuple[str, str]] = []


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
    across the COMBINED paper.tex + supplement.tex corpus (see the
    `sync_corpus` construction below) and compare against the entry's
    `expected_occurrences`, which is the TOTAL across both documents.
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
# Monograph anchor check (opt-in via --check-monograph).
#
# Locks numerical claims that live ONLY in preprint/manuscript.md -- values
# derived from the atlas's own sweep data that have no ledger anchor and no
# row in the paper crosswalk. See preprint/monograph_anchor_map.md for the
# schema, the verification discipline, and the substring hazards.
#
# Two deliberate divergences from check_paper_sync(), both documented in the
# map's header:
#
#   1. Whitespace-normalised matching. manuscript.md is hard-wrapped at ~70
#      columns, so any multi-word pattern would straddle a newline and break
#      the moment an unrelated edit reflows the paragraph. Both corpus and
#      pattern are collapsed to single spaces before comparison.
#   2. min_occurrences is a FLOOR, not an equality. The paper crosswalk's
#      exact counts needed 20 documented bumps across 38 commits for 97 rows;
#      the monograph is edited far more freely. A floor catches deletion and
#      alteration while staying silent when a value is correctly cited once
#      more.
#
# What this does NOT do: verify correctness. A presence check cannot tell a
# right number from a wrong one. Every pattern in the map was re-derived by
# hand from its artefact before being locked; the guard's value begins after
# that verification, never before it.
# -----------------------------------------------------------------------------

_WS_RUN = re.compile(r"\s+")


def _normalise_ws(text: str) -> str:
    """Collapse every whitespace run to a single space.

    Applied to both the monograph corpus and each search pattern so that
    hard-wrapped prose matches patterns written on one line.
    """
    return _WS_RUN.sub(" ", text)


def check_monograph() -> tuple[int, int, int]:
    """Verify that every anchor in preprint/monograph_anchor_map.md still
    occurs in preprint/manuscript.md at least min_occurrences times.

    Outcomes:
      - PASS               : found >= min_occurrences.
      - FAIL (missing)     : found == 0.
      - FAIL (below floor) : 0 < found < min_occurrences.
      - WARN               : map or manuscript absent, or a row fails to parse.

    Graceful degradation matches check_paper_sync: a missing file WARNs and
    never crashes the audit. Returns (n_pass, n_warn, n_fail).
    """
    print("\n## Monograph anchor check (--check-monograph)\n")
    mono_path = REPO / "preprint" / "manuscript.md"
    map_path = REPO / "preprint" / "monograph_anchor_map.md"

    if not mono_path.exists():
        print(
            f"_WARN: {mono_path.relative_to(REPO)} not found; monograph "
            "anchor check skipped._\n"
        )
        return (0, 1, 0)
    if not map_path.exists():
        print(
            f"_WARN: {map_path.relative_to(REPO)} not found; monograph "
            "anchor check skipped (the map has not been initialised yet)._\n"
        )
        return (0, 1, 0)

    entries = [e for e in _parse_map_entries(map_path.read_text(encoding="utf-8"))
               if "anchor_id" in e]
    if not entries:
        print(
            "_No anchors declared yet in preprint/monograph_anchor_map.md._\n"
        )
        return (0, 0, 0)

    corpus = _normalise_ws(mono_path.read_text(encoding="utf-8"))

    rows: list[dict] = []
    n_pass = n_warn = n_fail = 0
    for entry in entries:
        anchor_id = entry.get("anchor_id", "?")
        section = entry.get("monograph_section", "?")
        pattern = entry.get("pattern", "")
        try:
            floor = int(entry.get("min_occurrences", "0"))
        except (TypeError, ValueError):
            floor = -1  # signals a parse failure

        if not pattern or floor < 0:
            status, notes, found = "WARN", "row failed to parse", 0
        else:
            found = len(re.findall(re.escape(_normalise_ws(pattern)), corpus))
            if found == 0:
                status, notes = "FAIL", "missing: pattern no longer occurs"
            elif found < floor:
                status, notes = (
                    "FAIL",
                    f"below floor: found {found}, expected at least {floor}",
                )
            else:
                status, notes = "PASS", "-"

        rows.append(
            {
                "anchor_id": anchor_id,
                "section": section,
                "pattern": pattern,
                "floor": floor,
                "found": found,
                "status": status,
                "notes": notes,
            }
        )
        if status == "PASS":
            n_pass += 1
        elif status == "WARN":
            n_warn += 1
        else:
            n_fail += 1

    print(
        f"**Monograph anchors:** {len(rows)} declared "
        f"({n_pass} PASS, {n_warn} WARN, {n_fail} FAIL).\n"
    )
    print("| anchor_id | section | pattern | min | found | status | notes |")
    print("|---|---|---|---:|---:|---|---|")
    for r in rows:
        print(
            f"| {r['anchor_id']} | {r['section']} | `{r['pattern']}` | "
            f"{r['floor']} | {r['found']} | {r['status']} | {r['notes']} |"
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
s23_rf = pd.read_csv(REPO / "results/s023/rf_metrics.csv").set_index("output")
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
    manuscript_text="worst-case Vt CV 1.826 (default max; same-run pairing -> 0.018)",
    source_file="data/runs/s014_trigger_lockout/paired_comparison.parquet",
    manuscript_value=1.826,
    computed_value=float(s14_pair["Vt_cv_orig"].max()),
    tolerance_rule="displayed_3dp",
)
add(
    # Relabeled 2026-06-14: 0.112 is the max locked Vt CV across all S014 reruns
    # (run S1_F_0008), NOT the headline worst-case. The manuscript's worst-case
    # post-lockout value is the same-run pairing 0.018 (S1_F_0117), verified by
    # T1.s014.worstcase_locked_vtcv. This entry stays as an artifact diagnostic;
    # 0.112 is no longer quoted anywhere in the manuscript.
    claim_id="T1.06",
    section="S014 diagnostic (max locked Vt CV; not quoted in manuscript)",
    manuscript_text="max locked Vt CV across S014 reruns = 0.112 (diagnostic; headline worst-case same-run pairing is 0.018, see T1.s014.worstcase_locked_vtcv)",
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

# 19-21. F-003 S021 plateau median 643 mmHg + ~20 mmHg below AGE + 93.2% converged.
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
    section="Abstract + §2.4 + Fig 4 (npj paper); §3.8 S021 derivation (monograph)",
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
    section="Section 2.3 + Fig 4a (npj); worst-case (monograph); Supplement Fig S4",
    manuscript_text="worst-case S014 default Vt CV = 1.826 (run S1_F_0117, largest before/after delta)",
    source_file="data/runs/s014_trigger_lockout/paired_comparison.parquet (max Vt_cv_orig row)",
    manuscript_value=1.826,
    computed_value=float(_s14_worst["Vt_cv_orig"]),
    tolerance_rule="displayed_3dp",
)
add(
    claim_id="T1.s014.worstcase_locked_vtcv",
    section="Section 2.3 + Fig 4a (npj); worst-case (monograph); Supplement Fig S4",
    manuscript_text="worst-case S014 paired-config locked Vt CV = 0.018 (same run S1_F_0117)",
    source_file="data/runs/s014_trigger_lockout/paired_comparison.parquet (Vt_cv_lock of max-Vt_cv_orig row)",
    manuscript_value=0.018,
    computed_value=float(_s14_worst["Vt_cv_lock"]),
    tolerance_rule="displayed_3dp",
)
add(
    claim_id="T1.24",
    section="§3.8 L1965 + L1962",
    # 93.2 % (41/44) until 2026-09-01: the S021 window selection dropped the
    # first sample of [240, 300] s, so drift was fitted on 12 points instead of
    # the 13 the preregistration fixes, and one run (S1_F_0106_long, drift
    # -14.11 on 12 points, -15.34 on 13) sat on the wrong side of the 15 mmHg
    # threshold. See audit/synthesis_pass_2026_08.md section 15.
    manuscript_text="S021 S1 frac converged 90.9% (40/44)",
    source_file="data/runs/s021_hyperoxia_convergence/summary.json",
    manuscript_value=90.9,
    computed_value=100.0 * float(s21_sum["S1_frac_converged"]),
    tolerance_rule="pct_1dp",
)
n_s1_runs_s021 = int(s21_plat[s21_plat["scenario"] == "S1"].shape[0])
n_s1_converged = int(s21_plat[(s21_plat["scenario"] == "S1") & s21_plat["converged"]].shape[0])
add(
    claim_id="T1.24b",
    section="§3.8 L1965",
    manuscript_text="S1 converged: 40 / 44 runs",  # 41 until 2026-09-01, see T1.24
    source_file="data/runs/s021_hyperoxia_convergence/plateau_stats.parquet",
    manuscript_value=40,
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
# visible range of npj Figure 4b). Guarded after the D.8 paper sweep flagged
# the "~1,408 mmHg" caption value as an orphan: it appears only in paper.tex
# Fig 4 caption with no monograph/ledger anchor. Computed as the max S1
# plateau across the S021 300-second reruns. approx_round tolerance
# because the caption renders it with an explicit "~".
s021_s1_max_plateau = float(
    s21_plat[s21_plat["scenario"] == "S1"]["PaO2_plateau_mmHg"].max()
)
add(
    claim_id="T1.24d.s021_s1_max_runaway_plateau",
    section="Fig 4b caption (npj paper); §3.8 S021 runaway (monograph)",
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

# 25. Screening retention, both definitions (npj §2.1, Table 3; was Table 4 until the
# 2026-10-06 M. Sauthier review merged it into the flag table). Added 2026-08-05.
#
# Two screens are reported side by side because neither is distribution-neutral
# and they deplete opposite ends of the severity axis. "Four-flag clean" is the
# existing `clean` column (T1.28/T1.29 already anchor its total). "Hard-failure-
# free" keeps every run firing neither `diverged` nor `implausible`; `clamped` is
# empty in this sweep, so including it in the hard set changes no count.
_hard = agg["diverged"] | agg["implausible"] | agg["clamped"]
_hard_free = int((~_hard).sum())
_cell_clean = agg.groupby(["scenario", "sex"])["clean"].sum().astype(int)
_cell_hard_free = (~_hard).groupby([agg["scenario"], agg["sex"]]).sum().astype(int)

add(
    claim_id="T1.30r.hard_free_total",
    section="npj §2.1, Table 3",
    manuscript_text="1,134 hard-failure-free simulations",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=1134,
    computed_value=_hard_free,
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.30r.hard_free_pct",
    section="npj §2.1, Table 3",
    manuscript_text="88.6% hard-failure-free rate",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=88.6,
    computed_value=100.0 * _hard_free / len(agg),
    tolerance_rule="pct_1dp",
)
add(
    claim_id="T1.30r.nss_sole",
    section="npj §2.1",
    manuscript_text="471 runs carry not_steady_state as their sole flag",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=471,
    computed_value=int(((~_hard) & ~agg["clean"]).sum()),
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.30r.non_clean",
    section="npj §2.1",
    manuscript_text="617 non-clean runs (471 + 20 + 126)",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=617,
    computed_value=int((~agg["clean"]).sum()),
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.30r.implausible_total",
    section="npj §2.1",
    manuscript_text="126 implausible runs",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=126,
    computed_value=int(agg["implausible"].sum()),
    tolerance_rule="exact_int",
)
# The identity 471 + 20 + 126 = 617 only closes if diverged and implausible are
# disjoint. That is measured here, not assumed: the manuscript states it.
add(
    claim_id="T1.30r.div_imp_disjoint",
    section="npj §2.1",
    manuscript_text="diverged and implausible are disjoint in this sweep",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=0,
    computed_value=int((agg["diverged"] & agg["implausible"]).sum()),
    tolerance_rule="exact_int",
)
# Spreads are quoted from the counts, never from rounded percentages: with
# n = 160 a per-cell percentage is a multiple of 0.625, and nine of the sixteen
# values fall on an exact rounding tie at one or two decimals (four at one, five
# at two; four more tie at the integer).
add(
    claim_id="T1.30r.spread_four_flag",
    section="npj §2.1",
    manuscript_text="3.43-fold spread in four-flag retention (144/42)",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=3.43,
    computed_value=float(_cell_clean.max()) / float(_cell_clean.min()),
    tolerance_rule="displayed_2dp",
)
add(
    claim_id="T1.30r.spread_hard_free",
    section="npj §2.1",
    manuscript_text="1.51-fold spread in hard-failure-free retention (160/106)",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=1.51,
    computed_value=float(_cell_hard_free.max()) / float(_cell_hard_free.min()),
    tolerance_rule="displayed_2dp",
)
# The sixteen retention cells of Table 3, one anchor each, so a single stale count cannot
# hide inside a table nobody re-derives.
_RETENTION_TABLE = {
    ("S1", "M"): (49, 145), ("S1", "F"): (42, 137),
    ("S2", "M"): (87, 156), ("S2", "F"): (92, 160),
    ("S3", "M"): (144, 156), ("S3", "F"): (122, 160),
    ("S4", "M"): (67, 106), ("S4", "F"): (60, 114),
}
for (_sk, _xk), (_v_clean, _v_hf) in _RETENTION_TABLE.items():
    add(
        claim_id=f"T1.30r.clean.{_sk}_{_xk}",
        section="npj Table 3",
        manuscript_text=f"{_sk}_{_xk} four-flag clean = {_v_clean}/160",
        source_file="data/runs/full_sweep/aggregated.parquet",
        manuscript_value=_v_clean,
        computed_value=int(_cell_clean.loc[(_sk, _xk)]),
        tolerance_rule="exact_int",
    )
    add(
        claim_id=f"T1.30r.hardfree.{_sk}_{_xk}",
        section="npj Table 3",
        manuscript_text=f"{_sk}_{_xk} hard-failure-free = {_v_hf}/160",
        source_file="data/runs/full_sweep/aggregated.parquet",
        manuscript_value=_v_hf,
        computed_value=int(_cell_hard_free.loc[(_sk, _xk)]),
        tolerance_rule="exact_int",
    )

# 25b. Classification drivers and not_steady_state attribution, published in
# npj Figure 2b and Supplement Figure S1 (numbered S5 until 2026-10-07, when it
# moved next to its call in S3.12). Added 2026-08-05.
#
# The driver rule is re-applied here rather than read from a stored column, so
# an anchor fails if the figure and the ledger ever disagree about it. The
# thresholds are class-relative, matching
# src/analysis_compare.reliability_classification exactly.
_tl = pd.read_csv(REPO / "results" / "reliability_traffic_light.csv")


def _driver_of(row) -> str:
    rate = (row["n_diverged"] + row["n_implausible"]) / row["n_total"]
    pct = row["pct_off_baseline"]
    if row["light"] == "red":
        dev, flag = pct > 0.3, rate > 0.3
    elif row["light"] == "yellow":
        dev, flag = pct > 0.1, rate > 0.0
    else:
        return "neither"
    if dev and flag:
        return "both"
    return "dev_only" if dev else "flag_only"


_tl["_driver"] = _tl.apply(_driver_of, axis=1)
_drv_counts = _tl["_driver"].value_counts()
_red_counts = _tl[_tl["light"] == "red"]["_driver"].value_counts()

for _key, _expected, _what in [
    ("neither", 7, "neither criterion (coincides with the green set)"),
    ("flag_only", 23, "hard flags only"),
    ("dev_only", 9, "deviation only"),
    ("both", 9, "both criteria"),
]:
    add(
        claim_id=f"T1.30d.driver_{_key}",
        section="npj Figure 2b; Supplement Figure S5d",
        manuscript_text=f"{_expected} of 48 cells classified by {_what}",
        source_file="results/reliability_traffic_light.csv",
        manuscript_value=_expected,
        computed_value=int(_drv_counts.get(_key, 0)),
        tolerance_rule="exact_int",
    )

# The 12 red cells split 6 / 4 / 2. This is the split the figure prints, and it
# is the sharpest statement of why a red cell is not a reliability verdict:
# half of them are red on deviation alone, where Pulse is behaving correctly.
for _key, _expected in [("dev_only", 6), ("flag_only", 4), ("both", 2)]:
    add(
        claim_id=f"T1.30d.red_{_key}",
        section="npj Figure 2b; Supplement Figure S5d",
        manuscript_text=f"{_expected} of the 12 red cells are red on {_key}",
        source_file="results/reliability_traffic_light.csv",
        manuscript_value=_expected,
        computed_value=int(_red_counts.get(_key, 0)),
        tolerance_rule="exact_int",
    )

# not_steady_state trigger attribution (Supplement Figure S5b). Imported from
# the calibration script so the ledger, the figure and the calibration share one
# implementation of the thresholds.
from scripts.calibrate_nss_attribution import attribution as _nss_attr  # noqa: E402

_ex, _fc, _skipped, _recon = _nss_attr(agg)
add(
    claim_id="T1.30n.reconstruction_agreement",
    section="Supplement Figure S5b caption",
    manuscript_text="the exhaustive reconstruction reproduces the stored "
                    "not_steady_state flag on 1,280 of 1,280 runs",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=1280,
    computed_value=int((_recon == agg["not_steady_state"].to_numpy().astype(bool)).sum()),
    tolerance_rule="exact_int",
)
for _cid, _ch, _trig, _expected, _txt in [
    ("spo2_flatline", "SpO2", "flatline", 232, "SpO2 flatline triggers"),
    ("vt_cv", "Vt", "cv", 303, "Vt CV triggers"),
    ("vt_drift_exhaustive", "Vt", "drift", 133, "Vt drift triggers, exhaustive"),
]:
    add(
        claim_id=f"T1.30n.{_cid}",
        section="Supplement Figure S5b",
        manuscript_text=f"{_expected} {_txt}",
        source_file="data/runs/full_sweep/aggregated.parquet",
        manuscript_value=_expected,
        computed_value=int(_ex[_ch][_trig]),
        tolerance_rule="exact_int",
    )
add(
    claim_id="T1.30n.vt_drift_recorded",
    section="Supplement Figure S5b caption",
    manuscript_text="only 3 of the 133 Vt drift triggers survive in the "
                    "detector's recorded reason",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=3,
    computed_value=int(_fc["Vt"]["drift"]),
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.30n.total_exhaustive",
    section="Supplement Figure S5b caption",
    manuscript_text="918 exhaustive channel-level trigger occurrences in total",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=918,
    computed_value=int(sum(sum(v.values()) for v in _ex.values())),
    tolerance_rule="exact_int",
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
    manuscript_text="BV=4400 mL: diverged = 0 / 20",
    source_file="data/runs/s018_blood_volume/s018_classified.parquet",
    manuscript_value=0,
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
    manuscript_text="BV=4400 mL: clean = 12 / 20",
    source_file="data/runs/s018_blood_volume/s018_classified.parquet",
    manuscript_value=12,
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

# 43-44. §3.8 F-003 reclassification: 32/34 below the 700 mmHg bound, 31 at FiO2 >= 0.95.
# The producer compares PaO2 with 700 mmHg only and re-checks no other flag, so the
# monograph no longer says these runs "become physiologically clean" (aligned with
# supplement S3.10 in the M. Sauthier review round, 2026-10-06). The artefact field
# keeps its historical name.
add(
    claim_id="T2.f003.reclass",
    section="§3.8 L2024",
    manuscript_text="32 of 34 implausibly-flagged-by-PaO2 no longer exceed the wider PaO2 bound",
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

# 46b-46c. The two ends of the same S9 sentence, anchored 2026-09-07 because
# they were the ONLY numbers in it that were not. Both were correct when written
# on 2026-07-25 (779.20 and 1168.94 in the data of the day) and were falsified
# on 2026-09-02 by da5bd97's window repair, which recomputed the window-dependent
# columns of this parquet. Nothing re-derived them, so the audit stayed green
# and the stale pair shipped to the co-authors on 2026-09-05. The maximum of the
# same sentence IS anchored (T1.24d.s021_s1_max_runaway_plateau) and came
# through the repair correctly,
# which is the whole argument for anchoring rather than guarding: a guard
# pinning the literal 770 would go stale identically at the next repair, while
# a re-derived claim cannot.
_s21_runaway = s21_plat[
    (s21_plat["scenario"] == "S1") & (s21_plat["PaO2_plateau_mmHg"] > 700)
]
add(
    claim_id="T2.f003.runaway_male_plateau",
    section="Supplement S9 + monograph 3.8",
    manuscript_text="the single male S1 runaway case plateaus at 770 mmHg",
    source_file="data/runs/s021_hyperoxia_convergence/plateau_stats.parquet",
    manuscript_value=770,
    computed_value=float(_s21_runaway[_s21_runaway["sex"] == "M"]["PaO2_plateau_mmHg"].min()),
    tolerance_rule="whole_unit",
)
add(
    claim_id="T2.f003.runaway_female_low",
    section="Supplement S9 + monograph 3.8",
    manuscript_text="female S1 runaway range lower end 1,126 mmHg",
    source_file="data/runs/s021_hyperoxia_convergence/plateau_stats.parquet",
    manuscript_value=1126,
    computed_value=float(_s21_runaway[_s21_runaway["sex"] == "F"]["PaO2_plateau_mmHg"].min()),
    tolerance_rule="whole_unit",
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
    # 2026-10-14: 1,008 -> 966. The value was right against its CSV, but the CSV's
    # formula counted 42 runs that are also implausible as clean (supplement audit
    # row S4.4); script, CSV and documents were corrected together.
    manuscript_text="clean excl both = 966",
    source_file="results/s022/nss_decomposition.csv",
    manuscript_value=966,
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
# 56. Appendix C 75.5% counterfactual clean rate (78.8% before the 2026-10-14 fix).
add(
    claim_id="T2.nss.counterfactual",
    section="Appendix C L3290-3291, §4.5 L2574",
    manuscript_text="75.5% clean rate under joint exclusion (966/1280)",
    source_file="results/s022/nss_decomposition.csv",
    # 966/1,280 = 75.47 %, no rounding tie. (The former 1,008/1,280 = 78.75 % was a
    # tie at one decimal, which pct_1dp could not arbitrate.)
    manuscript_value=75.5,
    computed_value=100.0 * int(total_row["n_clean_excl_both"]) / int(total_row["n_total"]),
    tolerance_rule="pct_1dp",
)

# Appendix C per-cell rows: 8 cells x 5 columns = 40 numbers.
cells = ["S1_M", "S1_F", "S2_M", "S2_F", "S3_M", "S3_F", "S4_M", "S4_F"]
nss_man_table = {
    "S1_M": (160, 107, 91, 74, 29, 119),
    "S1_F": (160, 118, 88, 87, 24, 122),
    "S2_M": (160, 69, 60, 45, 23, 133),
    "S2_F": (160, 68, 52, 44, 7, 153),
    "S3_M": (160, 12, 11, 9, 8, 148),
    "S3_F": (160, 38, 34, 10, 3, 157),
    "S4_M": (160, 44, 44, 39, 39, 67),
    "S4_F": (160, 74, 74, 52, 52, 67),
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

# S013 out-of-sample table (added 2026-09-10). The trajectory-grouped R2 is the
# only honest generalisation figure for this surrogate: an out-of-bag score
# treats Morris rows as exchangeable, which they are not. Each mean is pinned
# so the published table cannot drift from rf_metrics.csv unnoticed -- the
# failure mode that produced 19 stale head-line counters in this same pass.
for _out, _val in [
    ("Vt", 0.9995),
    ("HR", 0.9917),
    ("MAP", 0.9402),
    ("SpO2", 0.8736),
    ("PaCO2", 0.8734),
    ("PaO2", 0.8716),
]:
    add(
        claim_id="T2.s023.r2_grouped_%s" % _out,
        section="Supplement S13 Table (out-of-sample)",
        manuscript_text="trajectory-grouped R2 for %s = %.4f" % (_out, _val),
        source_file="results/s023/rf_metrics.csv",
        manuscript_value=_val,
        computed_value=float(s23_rf.loc[_out, "r2_grouped_cv"]),
        tolerance_rule="displayed_3dp",
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
# PROVENANCE CORRECTED 2026-07-27. These three anchors previously pointed their
# source_file at the maintainer's pulse_engine_literature_review.md §1.5 summary
# table -- a SECONDARY record -- on the assumption, stated in the old comment
# here, that the table in turn cited Pulse's own docs page. That hop was broken:
# the §1.5 table gives no URL for the speed line, and Pulse's FAQ documents
# "about 5 to 10 times real time", not 10-15x. The overstated figure had
# propagated from that table into supplement.tex §S1 and manuscript.md §1.1
# (along with the Unity binding and the Android/iOS platform list, corrected
# separately). Both anchors are now bound to primary sources, re-read verbatim.
PULSE_DOC_TIMESTEP_MS = 20.0
PULSE_DOC_SPEED_LO_X = 5.0
PULSE_DOC_SPEED_HI_X = 10.0

add(
    claim_id="T3.s027.timestep_ms",
    section="§1.1 'Pulse in a nutshell'",
    manuscript_text="20 ms fixed timestep",
    source_file="Bray et al. 2019, SN Compr Clin Med 1(5):362-377 -- verbatim "
    '"a time step of 20 ms", verified 2026-07-26',
    manuscript_value=20.0,
    computed_value=PULSE_DOC_TIMESTEP_MS,
    tolerance_rule="whole_unit",
)
add(
    claim_id="T3.s027.speed_lower",
    section="§1.1 'Pulse in a nutshell'",
    manuscript_text="about 5-10x real time (lower bound)",
    source_file="Pulse FAQ https://pulse.kitware.com/_f_a_q.html -- verbatim "
    '"about 5 to 10 times real time", verified online and against '
    "docs/Markdown/FAQ.md:31 on 2026-07-27",
    manuscript_value=5.0,
    computed_value=PULSE_DOC_SPEED_LO_X,
    tolerance_rule="whole_unit",
)
add(
    claim_id="T3.s027.speed_upper",
    section="§1.1 'Pulse in a nutshell'",
    manuscript_text="about 5-10x real time (upper bound)",
    source_file="Pulse FAQ https://pulse.kitware.com/_f_a_q.html -- verbatim "
    '"about 5 to 10 times real time", verified online and against '
    "docs/Markdown/FAQ.md:31 on 2026-07-27",
    manuscript_value=10.0,
    computed_value=PULSE_DOC_SPEED_HI_X,
    tolerance_rule="whole_unit",
)

# Introduction engine-mechanics paragraph, added 2026-07-28.
#
# The time step appears in the manuscripts in THREE forms -- "20 ms" (Bray 2019),
# "0.02 s" and "50 Hz" (Pulse System Methodology). They are one quantity, so the
# latter two are DERIVED from PULSE_DOC_TIMESTEP_MS above rather than written out
# again: if the pinned time step is ever corrected, all three move together and
# none can be left behind. That is the failure this ledger exists to prevent.
PULSE_DOC_TIMESTEP_S = PULSE_DOC_TIMESTEP_MS / 1000.0
PULSE_DOC_TIMESTEP_HZ = 1000.0 / PULSE_DOC_TIMESTEP_MS

_SYSMETH_SRC = (
    "Pulse System Methodology "
    "https://pulse.kitware.com/_system_methodology.html -- verbatim "
    '"The entire engine works off of a transient analysis time step of 0.02 s '
    '(50 Hz). All system states are recalculated every time step.", read in the '
    "local REL_4_3_2 clone at docs/Methodology/SystemMethodology.md:116-117 on "
    "2026-07-28; docs/ is identical in REL_4_3_1 (empty git diff over docs/)"
)

add(
    claim_id="T3.doc.timestep_s",
    section="Introduction, engine mechanics",
    manuscript_text="0.02 s fixed transient-analysis time step",
    source_file=_SYSMETH_SRC,
    manuscript_value=0.02,
    computed_value=PULSE_DOC_TIMESTEP_S,
    tolerance_rule="exact_int",
)
add(
    claim_id="T3.doc.timestep_hz",
    section="Introduction, engine mechanics",
    manuscript_text="50 Hz update rate",
    source_file=_SYSMETH_SRC,
    manuscript_value=50.0,
    computed_value=PULSE_DOC_TIMESTEP_HZ,
    tolerance_rule="whole_unit",
)

# The severity-to-modifier calibration nodes. 0.0 and 1.0 are the definitional
# ends of the [0, 1] severity scale and are not anchored; the three interior
# nodes are the ones a future edit could silently get wrong.
_RESPMETH_NODES_SRC = (
    "Pulse Respiratory Methodology "
    "https://pulse.kitware.com/_respiratory_methodology.html -- verbatim "
    '"These severities are mapped to corresponding modifiers through piecewise '
    "linear functions, calibrated at key transition points: 0.0 (no change), 0.3 "
    '(mild), 0.6 (moderate), 0.9 (severe), and 1.0 (maximum)", read in the local '
    "REL_4_3_2 clone at docs/Methodology/RespiratoryMethodology.md:1176 on "
    "2026-07-28"
)
PULSE_DOC_SEVERITY_NODES = (0.3, 0.6, 0.9)

for _label, _node in zip(("mild", "moderate", "severe"), PULSE_DOC_SEVERITY_NODES):
    add(
        claim_id=f"T3.doc.severity_node_{_label}",
        section="Introduction, engine mechanics",
        manuscript_text=f"severity calibration node {_node} ({_label})",
        source_file=_RESPMETH_NODES_SRC,
        manuscript_value=_node,
        computed_value=_node,
        tolerance_rule="exact_int",
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

# --- Nadler 1962 per-kg blood volume on the two reference bodies ----------
# paper.tex §2.5 states that Pulse's sex-independent allometric formula "does
# not reproduce the male--female difference reported clinically: applied to
# these same two bodies, Nadler's sex-specific equations give 73.0 and
# 63.8 mL/kg". Those two literals are COMPUTED, not quoted from any source, so
# they are anchored here rather than trusted.
#
# The body constants are read out of src/scenario.py instead of being repeated,
# so that editing a reference body makes this audit fail instead of silently
# invalidating the sentence in the paper.
#
# The regression coefficients are Nadler's own, read verbatim from the primary
# source (Surgery 1962;51(2):224-232; the height-cubed / body-mass formulas
# appear on p. 227 and are restated on pp. 229 and 231), with PBV in litres,
# H in metres and W in kilograms:
#
#     men    PBV = 0.3669 H^3 + 0.03219 W + 0.6041
#     women  PBV = 0.3561 H^3 + 0.03308 W + 0.1833
#
# Retrieved 2026-07-26 from the article scan filed as Exhibit 1016 in USPTO
# PTAB proceeding PGR2025-00077 (Terumo v. Haemonetics); that exhibit's own PDF
# title is the article's publisher item identifier, PII 0039-6060(62)90166-6,
# and its 9 pages match pp. 224-232 exactly.
_scenario_src = (REPO / "src" / "scenario.py").read_text(encoding="utf-8")

NADLER_MALE_COEFFS = (0.3669, 0.03219, 0.6041)
NADLER_FEMALE_COEFFS = (0.3561, 0.03308, 0.1833)


def _reference_body(sex_key: str) -> tuple[float, float]:
    """Weight (kg) and height (cm) of a reference body, read from the source."""
    m = re.search(
        rf'"{sex_key}":\s*Patient\([^)]*?weight_kg=([\d.]+),\s*height_cm=([\d.]+)',
        _scenario_src,
    )
    assert m is not None, (
        f"audit_claims: reference body {sex_key!r} not located in src/scenario.py"
    )
    return float(m.group(1)), float(m.group(2))


def _nadler_ml_per_kg(sex_key: str) -> float:
    weight_kg, height_cm = _reference_body(sex_key)
    a, b, c = NADLER_MALE_COEFFS if sex_key == "M" else NADLER_FEMALE_COEFFS
    litres = a * (height_cm / 100.0) ** 3 + b * weight_kg + c
    return litres * 1000.0 / weight_kg


add(
    claim_id="T1.nadler.male_ml_per_kg",
    section="§2.5 (npj paper)",
    manuscript_text="73.0 mL/kg -- Nadler 1962 male equation on the male reference body",
    source_file="src/scenario.py PATIENTS['M'] + Nadler 1962 male regression",
    manuscript_value=73.0,
    computed_value=_nadler_ml_per_kg("M"),
    tolerance_rule="displayed_1dp",
)
add(
    claim_id="T1.nadler.female_ml_per_kg",
    section="§2.5 (npj paper)",
    manuscript_text="63.8 mL/kg -- Nadler 1962 female equation on the female reference body",
    source_file="src/scenario.py PATIENTS['F'] + Nadler 1962 female regression",
    manuscript_value=63.8,
    computed_value=_nadler_ml_per_kg("F"),
    tolerance_rule="displayed_1dp",
)

# --- Traffic-light rule: the post hoc deviation declared in paper §4.5 -----
# Every count below is rebuilt HERE from the run-level sweep artefact, never read
# from results/reliability_classification.csv. That file is the output of the
# rule under audit, so anchoring against it would only confirm that the paper
# reports what the code computed -- see audit/preregistration_traffic_light_deviation.md
# §5.2. The full derivation, with the 26 transitions enumerated, lives in
# scripts/audit_traffic_light_rule.py; this block re-expresses it compactly so
# that the ledger's own numbers do not depend on that script either.
_TL_OUTPUTS = ["HR", "MAP", "Vt", "SpO2", "PaO2", "PaCO2"]
_tl_ref = agg[(agg["scenario"] == "S1") & (agg["sex"] == "M") & agg["clean"]]
_tl_rows = []
for (_sc, _sx), _cell in agg.groupby(["scenario", "sex"]):
    _hard = int(_cell[["diverged", "implausible"]].any(axis=1).sum())
    _anyflag = int(
        _cell[["clamped", "diverged", "implausible", "not_steady_state"]].any(axis=1).sum()
    )
    for _ch in _TL_OUTPUTS:
        _base = float(_tl_ref[f"{_ch}_mean"].mean())
        _mean = float(_cell[_cell["clean"]][f"{_ch}_mean"].mean())
        _tl_rows.append(
            {
                "cell": f"{_sc}_{_sx}",
                "dev": abs(_mean - _base) / abs(_base),
                "hard_rate": _hard / len(_cell),
                "hard_any": _hard > 0,
                "anyflag_any": _anyflag > 0,
            }
        )
_tl = pd.DataFrame(_tl_rows)


def _tl_light(row: pd.Series, rule: str) -> str:
    if rule == "implemented":
        if row["hard_rate"] > 0.3 or row["dev"] > 0.3:
            return "red"
        return "yellow" if (row["dev"] > 0.1 or row["hard_rate"] > 0.0) else "green"
    flagged = row["hard_any"] if rule == "literal-hard" else row["anyflag_any"]
    if row["dev"] > 0.3 or flagged:
        return "red"
    return "green" if row["dev"] < 0.1 else "yellow"


for _rule in ("implemented", "literal-hard", "literal-four"):
    _tl[_rule] = _tl.apply(_tl_light, axis=1, rule=_rule)

TL_LITERAL_HARD = {c: int((_tl["literal-hard"] == c).sum()) for c in ("green", "yellow", "red")}
TL_LITERAL_FOUR = {c: int((_tl["literal-four"] == c).sum()) for c in ("green", "yellow", "red")}
TL_YELLOW_TO_RED = int(((_tl["implemented"] == "yellow") & (_tl["literal-hard"] == "red")).sum())
TL_GREEN_INVARIANT = int(((_tl["implemented"] == "green") & (_tl["literal-hard"] == "green")).sum())
TL_RED_INVARIANT = int(((_tl["implemented"] == "red") & (_tl["literal-hard"] == "red")).sum())
TL_ON_THRESHOLD = int(_tl["dev"].isin([0.1, 0.3]).sum())
TL_S1M_HARD_RUNS = int(
    agg[(agg["scenario"] == "S1") & (agg["sex"] == "M")][["diverged", "implausible"]]
    .any(axis=1)
    .sum()
)

add(
    claim_id="T1.tl.literal_hard_green",
    section="§4.5 (npj paper); Supplement S3.11; §3.7 (monograph)",
    manuscript_text="7 green under the literal hard-flag reading of the preregistered rule",
    source_file="data/runs/full_sweep/aggregated.parquet, rule re-expressed in this ledger",
    manuscript_value=7,
    computed_value=TL_LITERAL_HARD["green"],
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.tl.literal_hard_yellow",
    section="§4.5 (npj paper); Supplement S3.11; §3.7 (monograph)",
    manuscript_text="3 yellow under the literal hard-flag reading of the preregistered rule",
    source_file="data/runs/full_sweep/aggregated.parquet, rule re-expressed in this ledger",
    manuscript_value=3,
    computed_value=TL_LITERAL_HARD["yellow"],
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.tl.literal_hard_red",
    section="§4.5 (npj paper); Supplement S3.11; §3.7 (monograph)",
    manuscript_text="38 red under the literal hard-flag reading of the preregistered rule",
    source_file="data/runs/full_sweep/aggregated.parquet, rule re-expressed in this ledger",
    manuscript_value=38,
    computed_value=TL_LITERAL_HARD["red"],
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.tl.literal_four_red",
    section="§4.5 (npj paper); Supplement S3.11; §3.7 (monograph)",
    manuscript_text="48 red -- all combinations -- when 'any flag' spans all four flags",
    source_file="data/runs/full_sweep/aggregated.parquet, rule re-expressed in this ledger",
    manuscript_value=48,
    computed_value=TL_LITERAL_FOUR["red"],
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.tl.yellow_to_red",
    section="§4.5 (npj paper); Supplement S3.11; §3.7 (monograph)",
    manuscript_text="26 combinations move from yellow to red between the two readings",
    source_file="data/runs/full_sweep/aggregated.parquet, rule re-expressed in this ledger",
    manuscript_value=26,
    computed_value=TL_YELLOW_TO_RED,
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.tl.green_invariant",
    section="§4.5 (npj paper); Supplement S3.11; §3.7 (monograph)",
    manuscript_text="the same 7 combinations are green under both non-degenerate readings",
    source_file="data/runs/full_sweep/aggregated.parquet, rule re-expressed in this ledger",
    manuscript_value=7,
    computed_value=TL_GREEN_INVARIANT,
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.tl.red_invariant",
    section="§4.5 (npj paper); Supplement S3.11; §3.7 (monograph)",
    manuscript_text="the same 12 combinations are red under both non-degenerate readings",
    source_file="data/runs/full_sweep/aggregated.parquet, rule re-expressed in this ledger",
    manuscript_value=12,
    computed_value=TL_RED_INVARIANT,
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.tl.no_threshold_ties",
    section="Supplement S3.11",
    manuscript_text="0 cells sit exactly on the 10 % or 30 % deviation threshold",
    source_file="data/runs/full_sweep/aggregated.parquet, rule re-expressed in this ledger",
    manuscript_value=0,
    computed_value=TL_ON_THRESHOLD,
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.tl.s1m_hard_runs",
    section="§4.5 (npj paper)",
    manuscript_text="15 of the 160 S1_M runs carry a hard flag (4 diverged + 11 implausible, disjoint)",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=15,
    computed_value=TL_S1M_HARD_RUNS,
    tolerance_rule="exact_int",
)

# --- Relative ventilation dose on the two reference bodies -----------------
# paper.tex §2.5 and supplement §S6.2 state that, because the sweep varies Vt in
# ABSOLUTE mL over the same range on both reference bodies, a matched input
# vector is not a matched dose per kilogram. Every literal in those passages is
# COMPUTED, so all of them are anchored here rather than trusted.
#
# The reference bodies come from src/scenario.py via _reference_body() above and
# the swept Vt range from src/sampler.py, so editing either makes this audit
# fail instead of silently invalidating the manuscript sentences.
#
# Ideal body weight is Pulse's own quantity, read from the engine source
# (SetupPatient.cpp:136-146, sex-specific Devine relation in its imperial form):
#     male    IBW_kg = 50.0 + 2.3 * (height_in - 60)
#     female  IBW_kg = 45.5 + 2.3 * (height_in - 60)
# It is deliberately NOT called "ARDSnet predicted body weight": the metric
# coefficients usually attributed to that protocol could not be verified against
# an accessible primary source on 2026-08-04 (see audit/reference_audit.md).
_sampler_src = (REPO / "src" / "sampler.py").read_text(encoding="utf-8")
_vt_spec = re.search(r'InputSpec\("vt",\s*([\d.]+),\s*([\d.]+)', _sampler_src)
assert _vt_spec is not None, "audit_claims: Vt InputSpec not located in src/sampler.py"
VT_SWEEP_MIN_ML = float(_vt_spec.group(1))
VT_SWEEP_MAX_ML = float(_vt_spec.group(2))
CM_PER_INCH = 2.54


def _pulse_ideal_body_weight_kg(sex_key: str) -> float:
    _, height_cm = _reference_body(sex_key)
    intercept = 50.0 if sex_key == "M" else 45.5
    return intercept + 2.3 * (height_cm / CM_PER_INCH - 60.0)


def _vt_per_kg(sex_key: str, vt_ml: float, *, ideal: bool) -> float:
    denom = (
        _pulse_ideal_body_weight_kg(sex_key) if ideal else _reference_body(sex_key)[0]
    )
    return vt_ml / denom


def _dose_excess_pct(*, ideal: bool) -> float:
    """Female-over-male excess in mL/kg at any matched absolute Vt setting."""
    denom_m = _pulse_ideal_body_weight_kg("M") if ideal else _reference_body("M")[0]
    denom_f = _pulse_ideal_body_weight_kg("F") if ideal else _reference_body("F")[0]
    return (denom_m / denom_f - 1.0) * 100.0


add(
    claim_id="T1.dose.ibw_male",
    section="Supplement S6.2 (npj supplement); §3.6 (monograph)",
    manuscript_text="74.99 kg ideal body weight, Pulse Devine relation on the male reference body (180 cm)",
    source_file="src/scenario.py PATIENTS['M'] + Pulse SetupPatient.cpp:136-146",
    manuscript_value=74.99,
    computed_value=_pulse_ideal_body_weight_kg("M"),
    tolerance_rule="displayed_2dp",
)
add(
    claim_id="T1.dose.ibw_female",
    section="Supplement S6.2 (npj supplement); §3.6 (monograph)",
    manuscript_text="55.10 kg ideal body weight, Pulse Devine relation on the female reference body (163 cm)",
    source_file="src/scenario.py PATIENTS['F'] + Pulse SetupPatient.cpp:136-146",
    manuscript_value=55.10,
    computed_value=_pulse_ideal_body_weight_kg("F"),
    tolerance_rule="displayed_2dp",
)
add(
    claim_id="T1.dose.actual_male_low",
    section="Supplement S6.2 (npj supplement)",
    manuscript_text="4.5 mL/kg actual body weight at the low end of the swept Vt range, male reference body",
    source_file="src/sampler.py Vt InputSpec + src/scenario.py PATIENTS['M']",
    manuscript_value=4.5,
    computed_value=_vt_per_kg("M", VT_SWEEP_MIN_ML, ideal=False),
    tolerance_rule="displayed_1dp",
)
add(
    claim_id="T1.dose.actual_male_high",
    section="Supplement S6.2 (npj supplement)",
    manuscript_text="11.9 mL/kg actual body weight at the high end of the swept Vt range, male reference body",
    source_file="src/sampler.py Vt InputSpec + src/scenario.py PATIENTS['M']",
    manuscript_value=11.9,
    computed_value=_vt_per_kg("M", VT_SWEEP_MAX_ML, ideal=False),
    tolerance_rule="displayed_1dp",
)
add(
    claim_id="T1.dose.actual_female_low",
    section="Supplement S6.2 (npj supplement)",
    manuscript_text="5.3 mL/kg actual body weight at the low end of the swept Vt range, female reference body",
    source_file="src/sampler.py Vt InputSpec + src/scenario.py PATIENTS['F']",
    manuscript_value=5.3,
    computed_value=_vt_per_kg("F", VT_SWEEP_MIN_ML, ideal=False),
    tolerance_rule="displayed_1dp",
)
add(
    claim_id="T1.dose.actual_female_high",
    section="Supplement S6.2 (npj supplement)",
    manuscript_text="14.2 mL/kg actual body weight at the high end of the swept Vt range, female reference body",
    source_file="src/sampler.py Vt InputSpec + src/scenario.py PATIENTS['F']",
    manuscript_value=14.2,
    computed_value=_vt_per_kg("F", VT_SWEEP_MAX_ML, ideal=False),
    tolerance_rule="displayed_1dp",
)
add(
    claim_id="T1.dose.ideal_male_low",
    section="Supplement S6.2 (npj supplement)",
    manuscript_text="4.0 mL/kg ideal body weight at the low end of the swept Vt range, male reference body",
    source_file="src/sampler.py Vt InputSpec + Pulse SetupPatient.cpp Devine relation",
    manuscript_value=4.0,
    computed_value=_vt_per_kg("M", VT_SWEEP_MIN_ML, ideal=True),
    tolerance_rule="displayed_1dp",
)
add(
    claim_id="T1.dose.ideal_male_high",
    section="Supplement S6.2 (npj supplement)",
    manuscript_text="10.7 mL/kg ideal body weight at the high end of the swept Vt range, male reference body",
    source_file="src/sampler.py Vt InputSpec + Pulse SetupPatient.cpp Devine relation",
    manuscript_value=10.7,
    computed_value=_vt_per_kg("M", VT_SWEEP_MAX_ML, ideal=True),
    tolerance_rule="displayed_1dp",
)
add(
    claim_id="T1.dose.ideal_female_low",
    section="Supplement S6.2 (npj supplement)",
    manuscript_text="5.4 mL/kg ideal body weight at the low end of the swept Vt range, female reference body",
    source_file="src/sampler.py Vt InputSpec + Pulse SetupPatient.cpp Devine relation",
    manuscript_value=5.4,
    computed_value=_vt_per_kg("F", VT_SWEEP_MIN_ML, ideal=True),
    tolerance_rule="displayed_1dp",
)
add(
    claim_id="T1.dose.ideal_female_high",
    section="Supplement S6.2 (npj supplement)",
    manuscript_text="14.5 mL/kg ideal body weight at the high end of the swept Vt range, female reference body",
    source_file="src/sampler.py Vt InputSpec + Pulse SetupPatient.cpp Devine relation",
    manuscript_value=14.5,
    computed_value=_vt_per_kg("F", VT_SWEEP_MAX_ML, ideal=True),
    tolerance_rule="displayed_1dp",
)
add(
    claim_id="T1.dose.excess_actual_pct",
    section="§2.5 (npj paper); Supplement S6.2; §3.6 (monograph)",
    manuscript_text="19.8 % more tidal volume per kilogram of actual body weight on the female reference body at any matched absolute setting",
    source_file="src/scenario.py PATIENTS['M'] and PATIENTS['F']",
    manuscript_value=19.8,
    computed_value=_dose_excess_pct(ideal=False),
    tolerance_rule="displayed_1dp",
)
add(
    claim_id="T1.dose.excess_ideal_pct",
    section="§2.5 (npj paper); Supplement S6.2; §3.6 (monograph)",
    manuscript_text="36.1 % more tidal volume per kilogram of ideal body weight on the female reference body at any matched absolute setting",
    source_file="Pulse SetupPatient.cpp Devine relation on both reference bodies",
    manuscript_value=36.1,
    computed_value=_dose_excess_pct(ideal=True),
    tolerance_rule="displayed_1dp",
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
    manuscript_text="2000 random relabellings (pooled M+F clean runs re-split at the original group sizes) for the Wasserstein permutation null",
    source_file="src/analysis_compare.py wasserstein_per_output n_null default",
    manuscript_value=2000,
    computed_value=WASSERSTEIN_N_NULL,
    tolerance_rule="exact_int",
)

# ---------------------------------------------------------------------------
# S031 -- Sobol trigger applied as preregistered (top-three inputs), and the
# post-hoc ratio-aware bootstrap on sigma/mu*. Every figure below is re-derived
# by scripts/sobol_ci_buckets.py into results/sobol_ci_buckets.json, so the
# ledger checks the manuscript against a regenerable artefact rather than
# against a number typed once. The CI bucketing is post-hoc: the preregistration
# conditions the trigger on the point ratio and attaches no uncertainty
# qualifier (verified against preregistration.md Sec. Sampling method).
# ---------------------------------------------------------------------------
_sobol_ci = json.loads((REPO / "results/sobol_ci_buckets.json").read_text(encoding="utf-8"))

for _cid, _text, _value, _key in [
    ("T2.sobol.point_promotions",
     "trigger fires on 72 of the 144 top-three inputs (point estimate)",
     72, "point_estimate_promotions"),
    ("T2.sobol.cells_firing",
     "spanning 43 of the 48 cell x output combinations",
     43, "cells_firing_point_estimate"),
    ("T2.sobol.cells_firing_cells",
     "the trigger fires in all 8 scenario x sex cells",
     8, "sobol_cells_firing"),
    ("T2.sobol.runs_reduced_second_order",
     "8 firing cells at 6,144 runs under the preregistered 64x(2k+2) formula",
     6144, "sobol_runs_reduced_second_order"),
    ("T2.sobol.runs_reduced_first_total",
     "3,584 runs if only S1 and ST are computed, i.e. 64x(k+2)",
     3584, "sobol_runs_reduced_first_total"),
    ("T2.sobol.runs_full_second_order",
     "8,192 runs for a full seven-input design including second order",
     8192, "sobol_runs_full_second_order"),
    ("T2.sobol.runs_full_first_total",
     "4,608 runs for a full seven-input S1/ST design",
     4608, "sobol_runs_full_first_total"),
    ("T2.sobol.budget_preregistered",
     "preregistered compute envelope of 1,500 additional runs",
     1500, "sobol_budget_runs_preregistered"),
    ("T2.sobol.core_nonlinear",
     "23 of the 144 top-three inputs keep a lower bound at or above 0.6 under each of five seeds",
     23, "core_nonlinear_all_seeds"),
    ("T2.sobol.cells_touched",
     "the stable set spans 17 of the 48 cells",
     17, "cells_touched_by_core"),
    ("T2.sobol.dominant_linear",
     "dominant-input bucketing is 31 / 48 CI-robustly linear under every seed",
     31, "dominant_linear_all_seeds"),
    ("T2.sobol.dominant_nonlinear",
     "one dominant input is CI-robustly non-linear under all five seeds",
     1, "dominant_nonlinear_all_seeds"),
    ("T2.sobol.n_bootstrap",
     "trajectories are resampled 1,000 times for each top-three input",
     1000, "n_bootstrap"),
]:
    add(
        claim_id=_cid,
        section="§2.2 Results + §5 Methods Statistical analyses + Supplement S3-sobol",
        manuscript_text=_text,
        source_file="results/sobol_ci_buckets.json via scripts/sobol_ci_buckets.py",
        manuscript_value=_value,
        computed_value=_sobol_ci[_key],
        tolerance_rule="exact_int",
    )

# The per-input breakdown of the stable set, quoted in Results and Supplement.
for _inp, _count in [("peep", 8), ("rr", 5)]:
    add(
        claim_id="T2.sobol.core_input_%s" % _inp,
        section="§2.2 Results + Supplement S3-sobol",
        manuscript_text="PEEP in 8 of the 23, ahead of respiratory rate at 5"
                        if _inp == "peep" else "respiratory rate at 5 of the 23",
        source_file="results/sobol_ci_buckets.json core_by_input",
        manuscript_value=_count,
        computed_value=_sobol_ci["core_by_input"][_inp],
        tolerance_rule="exact_int",
    )

# Delivered Vt is the most affected output, and none of those 8 falls in S1 --
# the survivorship-censoring point made in Results.
add(
    claim_id="T2.sobol.core_output_vt",
    section="§2.2 Results + Supplement S3-sobol",
    manuscript_text="delivered tidal volume is the most affected output, in 8 of the 23",
    source_file="results/sobol_ci_buckets.json core_by_output",
    manuscript_value=8,
    computed_value=_sobol_ci["core_by_output"]["Vt"],
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
    manuscript_text="Male reference body weight 67.3 kg (CDC P50 at 214 months)",
    source_file="src/scenario.py PATIENTS['M'].weight_kg",
    manuscript_value=67.3,
    computed_value=MALE_WEIGHT_KG,
    tolerance_rule="displayed_2dp",
)
add(
    claim_id="T1.06t.female_weight_kg",
    section="Supplement S10 + section 4.2 of main paper",
    manuscript_text="Female reference body weight 56.2 kg (CDC P50 at 214 months)",
    source_file="src/scenario.py PATIENTS['F'].weight_kg",
    manuscript_value=56.2,
    computed_value=FEMALE_WEIGHT_KG,
    tolerance_rule="displayed_2dp",
)

# --- Detector clamp-pattern anchors (added 2026-07-26) -------------------
# Two counts are guarded, and they are deliberately NOT the same number.
#
#   published : size of the pattern set that classified the 1,280-run sweep.
#               A frozen historical constant.  It must never be made to
#               track src/detector.py: patching the detector does not
#               retroactively change what produced the published results,
#               and the paper's Methods must keep describing what ran.
#   current   : len(CLAMP_PATTERNS) in src/detector.py today, which the
#               supplement prints verbatim for users adopting the detector.
#
# The two were equal until 2026-07-26.  Verified before freezing the 4:
# `git show e068544:src/detector.py` (the sweep commit) and `708efb1^`
# carry a byte-identical four-pattern block, so no detector change occurred
# between the sweep and the patch.
CLAMP_PATTERNS_PUBLISHED = 4

_m_clamp_block = re.search(
    r"CLAMP_PATTERNS:\s*list\[str\]\s*=\s*\[(.*?)\n\]",
    _detector_py,
    re.DOTALL,
)
assert _m_clamp_block is not None, (
    "audit_claims: CLAMP_PATTERNS block not located in src/detector.py"
)
CLAMP_PATTERNS_FROM_SRC: list[str] = re.findall(
    r'^\s*r"(.*)",\s*$', _m_clamp_block.group(1), re.MULTILINE
)
assert CLAMP_PATTERNS_FROM_SRC, (
    'audit_claims: no r"..." entries parsed out of CLAMP_PATTERNS'
)

add(
    claim_id="T1.detector.n_patterns_published",
    section="Section 4.4 of main paper (four-flag detector)",
    manuscript_text="The sweep was classified with 4 message patterns",
    source_file="frozen historical constant (sweep commit e068544)",
    manuscript_value=4,
    computed_value=CLAMP_PATTERNS_PUBLISHED,
    tolerance_rule="exact_int",
)
add(
    claim_id="T1.detector.n_patterns_current",
    section="Supplement S3.3 (clamp regex set)",
    manuscript_text="the five-pattern set now in src/detector.py",
    source_file="src/detector.py CLAMP_PATTERNS",
    manuscript_value=5,
    computed_value=len(CLAMP_PATTERNS_FROM_SRC),
    tolerance_rule="exact_int",
)

# Strongest of the three: every regex printed in the supplement's listing
# must be character-identical to its counterpart in src/detector.py.  This
# is the guard that actually prevents redistributing a stale pattern --
# the concrete harm the 2026-07-26 false negative exposed.  A drifted
# character changes the count of verbatim hits and fails here.
_supplement_src = (REPO / "preprint_npj" / "supplement.tex").read_text(encoding="utf-8")
_clamp_verbatim_hits = sum(
    1 for _p in CLAMP_PATTERNS_FROM_SRC if f'r"{_p}"' in _supplement_src
)
add(
    claim_id="T1.detector.patterns_verbatim_in_supplement",
    section="Supplement S3.3 (clamp regex set)",
    manuscript_text="each printed regex is character-identical to src/detector.py",
    source_file="src/detector.py CLAMP_PATTERNS vs preprint_npj/supplement.tex",
    manuscript_value=len(CLAMP_PATTERNS_FROM_SRC),
    computed_value=_clamp_verbatim_hits,
    tolerance_rule="exact_int",
)

# S021 time-to-95-percent-of-plateau kinetic anchor: derived at audit
# time from the S021 plateau_stats parquet + each S1 run's output.csv.
# The "floor" is the median PaO2 at t=0 of the 300-second rerun
# (recorded simulation time; the rerun re-executes from time zero, so
# t=0 follows the unchanged 120 s ventilator-settle phase and is
# already hyperoxic); the "asymptote" is the median PaO2 at t=300 --
# the last observed value, not a fitted asymptote; the anchor is the
# smallest recorded-simulation time at which the median trajectory across the
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
# Strict count guard scoped to T1.06u ONLY. The other 266 anchors are protected
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
        manuscript_text="95% of the late-plateau gain reached by t=180 s of recorded simulation (37 physiological-converged S1 runs)",
        source_file="derived from data/runs/s021_hyperoxia_convergence/<S1 runs>/output.csv",
        manuscript_value=180.0,
        computed_value=_t_95,
        tolerance_rule="whole_unit",
    )
elif _n_expected > 0 and _n_found == 0:
    # Benign CI case: plateau_stats lists N>0 S1 physio runs but every per-run
    # output.csv is gitignored and absent on a clean checkout. Skip T1.06u
    # with a NOTE; the parquet/CSV-backed anchors still run as the gate. The
    # skip is recorded in `skipped` so the summary reports 312/313 (1 SKIPPED)
    # rather than a bare 312/312 that would hide the existence of the anchor.
    skipped.append(
        (
            "T1.06u.s021_time_to_95pct_plateau",
            "raw S021 per-run output.csv trajectories gitignored / absent on "
            "this checkout; run with the full data/runs tree to evaluate it",
        )
    )
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


# -----------------------------------------------------------------------------
# T5.clip -- Cost of the pulse-pressure clip on diastolic elementary effects
# (Supplement S3.7, sec:s3-clip-cost). Re-derives every computed figure in that
# subsection from the canonical Morris sample + master aggregate. The clip ratio
# and the input bounds are READ FROM SOURCE rather than hardcoded here, so these
# anchors also fail if src/scenario.py or src/sampler.py drifts.
# -----------------------------------------------------------------------------
_clip_scen_src = (REPO / "src" / "scenario.py").read_text(encoding="utf-8")
_clip_samp_src = (REPO / "src" / "sampler.py").read_text(encoding="utf-8")
_m_ratio = re.search(r"PULSE_DBP_SBP_MAX_RATIO:\s*float\s*=\s*([\d.]+)", _clip_scen_src)
assert _m_ratio is not None, "audit_claims: PULSE_DBP_SBP_MAX_RATIO not located"
_CLIP_RATIO = float(_m_ratio.group(1))
_clip_specs = {
    m[0]: (float(m[1]), float(m[2]))
    for m in re.findall(r"InputSpec\(\"(\w+)\",\s*([\d.]+),\s*([\d.]+)", _clip_samp_src)
}
assert len(_clip_specs) == 7, f"audit_claims: expected 7 InputSpec rows, got {len(_clip_specs)}"
_CLIP_NAMES = list(_clip_specs)

_clip_smp = (
    pd.read_parquet(REPO / "data/runs/full_sweep/morris_sample.parquet")
    .sort_values(["trajectory", "point"])
    .reset_index(drop=True)
)
_clip_smp["idx"] = range(len(_clip_smp))
_clip_smp["dbp_app"] = [min(r.dbp, _CLIP_RATIO * r.sbp) for r in _clip_smp.itertuples()]


def _clip_nrm(name: str, v: float) -> float:
    lo, hi = _clip_specs[name]
    return (v - lo) / (hi - lo)


_clip_pairs = []
for _t, _g in _clip_smp.groupby("trajectory"):
    _i = _g.sort_values("point")["idx"].tolist()
    for _k in range(len(_i) - 1):
        _a, _b = _clip_smp.loc[_i[_k]], _clip_smp.loc[_i[_k + 1]]
        _d = {n: _clip_nrm(n, _b[n]) - _clip_nrm(n, _a[n]) for n in _CLIP_NAMES}
        _f = max(_d, key=lambda n: abs(_d[n]))
        _clip_pairs.append(
            {
                "a": _i[_k],
                "b": _i[_k + 1],
                "f": _f,
                "delta": _d[_f],
                "dreq": _clip_nrm("dbp", _b.dbp) - _clip_nrm("dbp", _a.dbp),
                "dapp": _clip_nrm("dbp", _b.dbp_app) - _clip_nrm("dbp", _a.dbp_app),
            }
        )

_clip_n_points = int((_clip_smp["dbp_app"] < _clip_smp["dbp"] - 1e-12).sum())
_clip_dbp_steps = [p for p in _clip_pairs if p["f"] == "dbp"]
_clip_short = [p for p in _clip_dbp_steps if abs(p["dreq"] - p["dapp"]) > 1e-9]
_clip_ratios = sorted(abs(p["dapp"] / p["dreq"]) for p in _clip_short)
_clip_oat = [p for p in _clip_pairs if p["f"] != "dbp" and abs(p["dapp"]) > 1e-9]
_clip_intact = len(_clip_pairs) - len(_clip_short) - len(_clip_oat)

add(
    claim_id="T5.clip.points",
    section="Supplement S3.7 / monograph 2.2",
    manuscript_text="35 of 160 sampled points carry a requested DBP above the ratio and are clipped",
    source_file="data/runs/full_sweep/morris_sample.parquet",
    manuscript_value=35,
    computed_value=_clip_n_points,
    tolerance_rule="exact_int",
)
add(
    claim_id="T5.clip.dbp_shortened",
    section="Supplement S3.7 / monograph 2.2",
    manuscript_text="9 of the 20 diastolic Morris steps are shortened by the clip",
    source_file="data/runs/full_sweep/morris_sample.parquet",
    manuscript_value=9,
    computed_value=len(_clip_short),
    tolerance_rule="exact_int",
)
add(
    claim_id="T5.clip.min_ratio_pct",
    section="Supplement S3.7 / monograph 2.2",
    manuscript_text="the shortest applied DBP step is 6.25 percent of nominal",
    source_file="data/runs/full_sweep/morris_sample.parquet",
    manuscript_value=6.25,
    computed_value=100.0 * _clip_ratios[0],
    tolerance_rule="displayed_2dp",
)
add(
    claim_id="T5.clip.oat_violations",
    section="Supplement S3.7 / monograph 2.2",
    manuscript_text="8 of the 140 steps flip SBP and move the applied DBP as well",
    source_file="data/runs/full_sweep/morris_sample.parquet",
    manuscript_value=8,
    computed_value=len(_clip_oat),
    tolerance_rule="exact_int",
)
add(
    claim_id="T5.clip.intact_steps",
    section="Supplement S3.7 / monograph 2.2",
    manuscript_text="123 of 140 sampled steps are untouched by the clip",
    source_file="data/runs/full_sweep/morris_sample.parquet",
    manuscript_value=123,
    computed_value=_clip_intact,
    tolerance_rule="exact_int",
)

_clip_flags = ["clamped", "diverged", "implausible", "not_steady_state"]
_clip_agg = agg.copy()
_clip_agg["idx"] = _clip_agg["case_id"].str.rsplit("_", n=1).str[1].astype(int)
_clip_agg["clean"] = ~_clip_agg[_clip_flags].any(axis=1)
_cd = _cds = _cs = _css = 0
# Per-cell systolic counts, recorded inside the loop that already produces the
# pooled 68 / 19. Supplement S3.7 publishes the per-cell retained counts, and a
# pooled total cannot show that three cells retain only four pairs.
_clip_percell: dict[str, dict[str, int]] = {}
for _key, _cell in _clip_agg.groupby(["scenario", "sex"]):
    _ok = set(_cell[_cell["clean"]]["idx"])
    _cell_s = _cell_ss = 0
    for _p in _clip_pairs:
        if _p["a"] in _ok and _p["b"] in _ok:
            if _p["f"] == "dbp":
                _cd += 1
                if abs(_p["dreq"] - _p["dapp"]) > 1e-9:
                    _cds += 1
            elif _p["f"] == "sbp":
                _cell_s += 1
                if abs(_p["dapp"]) > 1e-9:
                    _cell_ss += 1
    _clip_percell[f"{_key[0]}_{_key[1]}"] = {
        "clean": _cell_s,
        "contaminated": _cell_ss,
        "retained": _cell_s - _cell_ss,
    }
    # The pooled totals stay exactly what they were: sums over the same loop.
    _cs += _cell_s
    _css += _cell_ss

add(
    claim_id="T5.clip.clean_dbp_total",
    section="Supplement S3.7 / monograph 2.2",
    manuscript_text="78 clean diastolic elementary-effect pairs across the eight cells",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=78,
    computed_value=_cd,
    tolerance_rule="exact_int",
)
add(
    claim_id="T5.clip.clean_dbp_shortened",
    section="Supplement S3.7 / monograph 2.2",
    manuscript_text="41 of 78 clean diastolic elementary-effect pairs are shortened",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=41,
    computed_value=_cds,
    tolerance_rule="exact_int",
)
add(
    claim_id="T5.clip.clean_sbp_total",
    section="Supplement S3.7 / monograph 2.2",
    manuscript_text="68 clean systolic elementary-effect pairs across the eight cells",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=68,
    computed_value=_cs,
    tolerance_rule="exact_int",
)
add(
    claim_id="T5.clip.clean_sbp_affected",
    section="Supplement S3.7 / monograph 2.2",
    manuscript_text="19 of 68 clean systolic elementary-effect pairs are affected",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=19,
    computed_value=_css,
    tolerance_rule="exact_int",
)

# Step length versus position in the sampled space. The clip makes diastolic
# step length a function of the systolic setting: at SBP = 90 mmHg the 0.75
# ratio caps DBP at 67.5, so no full-length diastolic step can exist there.
# These three anchors guard that geometry, which is what licenses the
# supplement's statement that no difference between the nominal and the
# applied-step estimator can be attributed to step length alone.
_clip_dbp_full = [p for p in _clip_dbp_steps if abs(p["dreq"] - p["dapp"]) <= 1e-9]
_clip_min_app = min(abs(p["dapp"]) for p in _clip_short)
_clip_smallest_sbp = sorted(
    {
        float(_clip_smp.loc[p["a"], "sbp"])
        for p in _clip_short
        if abs(abs(p["dapp"]) - _clip_min_app) < 1e-9
    }
)
assert len(_clip_smallest_sbp) == 1, (
    f"audit_claims: shortest DBP steps span SBP {_clip_smallest_sbp}, expected one"
)
_clip_full_sbp_min = min(float(_clip_smp.loc[p["a"], "sbp"]) for p in _clip_dbp_full)

add(
    claim_id="T5.clip.dbp_full_steps",
    section="Supplement S3.7 / monograph 2.2",
    manuscript_text="11 of the 20 diastolic Morris steps keep their full length",
    source_file="data/runs/full_sweep/morris_sample.parquet",
    manuscript_value=11,
    computed_value=len(_clip_dbp_full),
    tolerance_rule="exact_int",
)
add(
    claim_id="T5.clip.smallest_step_sbp",
    section="Supplement S3.7 / monograph 2.2",
    manuscript_text="the shortest diastolic steps occur only at SBP = 90 mmHg",
    source_file="data/runs/full_sweep/morris_sample.parquet",
    manuscript_value=90,
    computed_value=int(_clip_smallest_sbp[0]),
    tolerance_rule="exact_int",
)
add(
    claim_id="T5.clip.full_step_sbp_min",
    section="Supplement S3.7 / monograph 2.2",
    manuscript_text="every full-length diastolic step occurs at SBP >= 100 mmHg",
    source_file="data/runs/full_sweep/morris_sample.parquet",
    manuscript_value=100,
    computed_value=int(_clip_full_sbp_min),
    tolerance_rule="exact_int",
)

# mu* under the nominal versus the applied-step denominator.
_CLIP_OUT = {
    "HR_mean": "HR",
    "MAP_mean": "MAP",
    "Vt_mean": "Vt",
    "SpO2_mean": "SpO2",
    "PaO2_mean": "PaO2",
    "PaCO2_mean": "PaCO2",
}
_clip_rows = []
for _key, _cell in _clip_agg.groupby(["scenario", "sex"]):
    _m = _cell.set_index("idx")
    _ok = set(_cell[_cell["clean"]]["idx"])
    for _p in _clip_pairs:
        if _p["a"] not in _ok or _p["b"] not in _ok:
            continue
        _deff = _p["dapp"] if _p["f"] == "dbp" else _p["delta"]
        for _oc, _on in _CLIP_OUT.items():
            _dy = _m.loc[_p["b"], _oc] - _m.loc[_p["a"], _oc]
            _clip_rows.append(
                (
                    _key[0],
                    _key[1],
                    _on,
                    _p["f"],
                    _dy / _p["delta"],
                    (_dy / _deff) if abs(_deff) > 1e-9 else float("nan"),
                )
            )
_clip_ee = pd.DataFrame(_clip_rows, columns=["sc", "sx", "out", "inp", "nom", "app"])
_clip_mu = (
    _clip_ee.groupby(["sc", "sx", "out", "inp"])
    .agg(nom=("nom", lambda x: x.abs().mean()), app=("app", lambda x: x.abs().mean()))
    .reset_index()
)
_clip_dbp_mu = _clip_mu[_clip_mu["inp"] == "dbp"].dropna()
_clip_factor = float((_clip_dbp_mu["app"] / _clip_dbp_mu["nom"]).median())
_clip_enter = 0
_clip_h1_nom, _clip_h1_app = [], []
for _k, _g in _clip_mu.dropna().groupby(["sc", "sx", "out"]):
    if "dbp" in set(_g.nlargest(3, "app")["inp"]) and "dbp" not in set(
        _g.nlargest(3, "nom")["inp"]
    ):
        _clip_enter += 1
    _clip_h1_nom.append(_g.nlargest(3, "nom")["nom"].sum() / _g["nom"].sum())
    _clip_h1_app.append(_g.nlargest(3, "app")["app"].sum() / _g["app"].sum())

add(
    claim_id="T5.clip.mustar_factor",
    section="Supplement S3.7 / monograph 2.2",
    manuscript_text="mu*(DBP) rises by a median factor of 2.4 under the applied-step denominator",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=2.4,
    computed_value=_clip_factor,
    tolerance_rule="displayed_1dp",
)
add(
    claim_id="T5.clip.dbp_enters_top3",
    section="Supplement S3.7 / monograph 2.2",
    manuscript_text="DBP enters the top three in 9 of the 48 cell-output combinations",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=9,
    computed_value=_clip_enter,
    tolerance_rule="exact_int",
)
add(
    claim_id="T5.clip.h1_applied_median",
    section="Supplement S3.7 / monograph 2.2",
    manuscript_text="median top-3 fraction 0.910 under the applied-step estimator",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=0.910,
    computed_value=float(pd.Series(_clip_h1_app).median()),
    tolerance_rule="displayed_3dp",
)
add(
    claim_id="T5.clip.h1_applied_min",
    section="Supplement S3.7 / monograph 2.2",
    manuscript_text="minimum top-3 fraction 0.696 under the applied-step estimator",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=0.696,
    computed_value=float(pd.Series(_clip_h1_app).min()),
    tolerance_rule="displayed_3dp",
)
add(
    claim_id="T5.clip.h1_holds_both",
    section="Supplement S3.7 / monograph 2.2",
    manuscript_text="H1 holds in 48 of 48 cell-output combinations under either estimator",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=48,
    computed_value=int(
        sum(1 for a, b in zip(_clip_h1_nom, _clip_h1_app) if a >= 0.5 and b >= 0.5)
    ),
    tolerance_rule="exact_int",
)

# -----------------------------------------------------------------------------
# T5.window -- Per-arm cross-output drift exceedance (Supplement S16 window
# audit, monograph S012, main paper §4.4). The PaO2 rate and the two arm sizes
# are already anchored above (T2.f003.*); these six anchors cover the HR, MAP
# and PaCO2 rates in each arm, which the main paper now states per arm instead
# of as a single (and, for PaCO2, incorrect) upper bound across both.
# The drift thresholds are read from src/detector.py rather than hardcoded.
# -----------------------------------------------------------------------------
_win_src = (REPO / "src" / "detector.py").read_text(encoding="utf-8")
_m_win = re.search(
    r"DRIFT_MAX_DELTA_60S:\s*dict\[str,\s*float\]\s*=\s*\{(.*?)\}", _win_src, re.S
)
assert _m_win is not None, "audit_claims: DRIFT_MAX_DELTA_60S not located"
_WIN_TH = {
    k: float(v) for k, v in re.findall(r'"(\w+)":\s*([\d.]+)', _m_win.group(1))
}
assert len(_WIN_TH) == 6, f"audit_claims: expected 6 drift thresholds, got {len(_WIN_TH)}"

_win_valid = agg[agg["HR_delta_60s"].notna()]
_win_arms = {
    "hyperox": _win_valid[_win_valid["in_fio2"] >= 0.95],
    "vtosc": _win_valid[_win_valid["Vt_cv"] > 0.05],
}


def _win_pct(arm: str, ch: str) -> float:
    sub = _win_arms[arm]
    return 100.0 * (sub[f"{ch}_delta_60s"].abs() > _WIN_TH[ch]).mean()


for _arm, _armlabel, _expected in (
    ("hyperox", "hyperoxia arm (FiO2 >= 0.95, n = 195)", {"HR": 2.6, "MAP": 0.0, "PaCO2": 3.6}),
    ("vtosc", "Vt-oscillation arm (Vt CV > 0.05, n = 303)", {"HR": 2.3, "MAP": 0.7, "PaCO2": 2.0}),
):
    for _ch, _val in _expected.items():
        add(
            claim_id=f"T5.window.{_arm}_{_ch.lower()}_pct",
            section="Paper §4.4 / Supplement S16 / monograph S012",
            manuscript_text=(
                f"{_val} percent of runs exceed the locked {_ch} drift threshold "
                f"in the {_armlabel}"
            ),
            source_file="data/runs/full_sweep/aggregated.parquet",
            manuscript_value=_val,
            computed_value=_win_pct(_arm, _ch),
            tolerance_rule="displayed_1dp",
        )

# -----------------------------------------------------------------------------
# T5.robust / T5.strat -- Robustness of the systolic ranking to the clip
# (paper limitation (vi), Supplement S3.7 addendum, monograph 2.2).
#
# The analysis functions are IMPORTED from the S032 script rather than
# reimplemented here. A second implementation would drift from the one that
# produced the manuscript numbers; importing alone would let a single bug reach
# both the manuscript and its own audit. The compromise is that the import is
# preceded, in this block, by four gates the imported code must clear before any
# T5.robust anchor is produced:
#   1. the nine audited S3.7 counts,
#   2. exact reproduction of results/morris_indices.parquet (318 rows, 0 delta),
#   3. the applied-step factor and top-3 entry count,
#   4. internal agreement between the f_c > f_flip test and the hybrid rank.
# Each gate is an assertion: a failure aborts the audit rather than downgrading
# a claim, because past that point the ledger would be checking the manuscript
# against machinery already known to disagree with the frozen artefacts.
# -----------------------------------------------------------------------------
import contextlib as _ctx  # noqa: E402
import io as _io  # noqa: E402

# NOTE ON A DEPARTURE. Everywhere else this ledger reads repository source as
# text and re-derives constants by regex, deliberately never executing project
# code. This block does execute it. The alternative -- a second implementation
# of the elementary-effect machinery living here -- was judged the larger risk,
# because it would drift from the one that produced the manuscript numbers
# without anything noticing. The four gates below are the price of the import.
sys.path.insert(0, str(REPO / "scripts"))
from src.scenario import iter_cells  # noqa: E402
from s032_uncontaminated_step_analysis import (  # noqa: E402
    annotate_pairs as _s32_annotate,
    applied_table as _s32_applied,
    calibrate as _s32_calibrate,
    elementary_effects as _s32_effects,
    load_inputs as _s32_load,
    mu_star as _s32_mu,
    ranked as _s32_ranked,
)

_s32_agg, _s32_smp = _s32_load()
_s32_pairs = _s32_annotate(_s32_smp)

# Gate 1 -- the nine audited S3.7 counts.
with _ctx.redirect_stdout(_io.StringIO()):
    _s32_g1 = _s32_calibrate(_s32_agg, _s32_smp, _s32_pairs)
assert _s32_g1, "audit_claims: S032 gate 1 FAILED -- S3.7 counts not reproduced"

# Gate 2 -- the nominal estimator must reproduce the published Morris index.
_s32_ee = _s32_effects(_s32_agg, _s32_pairs)
_s32_nom = _s32_mu(_s32_ee, "ee")
_s32_pub = pd.read_parquet(REPO / "results" / "morris_indices.parquet")[
    ["scenario", "sex", "output", "input", "mu_star"]
]
_s32_j = _s32_pub.merge(
    _s32_nom[["scenario", "sex", "output", "input", "mu_star"]],
    on=["scenario", "sex", "output", "input"],
    suffixes=("_pub", "_here"),
    how="outer",
    indicator=True,
)
assert (_s32_j["_merge"] == "both").all(), (
    "audit_claims: S032 gate 2 FAILED -- Morris index rows do not match one-to-one"
)
assert float((_s32_j["mu_star_pub"] - _s32_j["mu_star_here"]).abs().max()) == 0.0, (
    "audit_claims: S032 gate 2 FAILED -- nominal mu* does not reproduce the published index"
)

# Gate 3 -- the applied-step machinery reproduces its own audited anchors.
_s32_m = _s32_applied(_s32_ee)
_s32_dbpmu = _s32_m[_s32_m["input"] == "dbp"]
assert abs(float((_s32_dbpmu["app"] / _s32_dbpmu["nom"]).median()) - _clip_factor) <= 1e-9, (
    "audit_claims: S032 gate 3 FAILED -- applied/nominal DBP factor disagrees with T5.clip"
)
_s32_enter = sum(
    1
    for _, _g in _s32_m.groupby(["scenario", "sex", "output"])
    if "dbp" in set(_g.nlargest(3, "app")["input"])
    and "dbp" not in set(_g.nlargest(3, "nom")["input"])
)
assert _s32_enter == _clip_enter, (
    "audit_claims: S032 gate 3 FAILED -- DBP top-3 entry count disagrees with T5.clip"
)

# The six estimators, then gate 4 -- two independent routes to the same verdict.
_s32_unc = _s32_mu(_s32_ee[~_s32_ee["contaminated"]], "ee")
_s32_bad = set(_s32_pairs[_s32_pairs["contaminated"]]["trajectory"])
_s32_good = sorted(set(_s32_pairs["trajectory"]) - _s32_bad)
_s32_keep = _s32_ee["trajectory"].isin(_s32_good)
_s32_est = {
    "nominal": _s32_nom,
    "applied": _s32_mu(_s32_ee, "ee_app"),
    "uncontaminated": _s32_unc,
    "matched": _s32_mu(_s32_ee[_s32_keep], "ee"),
    "hybrid_combined": _s32_mu(_s32_ee[~_s32_ee["contaminated"]], "ee_app"),
    "matched_combined": _s32_mu(_s32_ee[_s32_keep], "ee_app"),
}
_s32_first = {}
for _name, _tbl in _s32_est.items():
    _r = _s32_ranked(_tbl, "MAP")
    _s32_first[_name] = sum(
        1
        for _sk, _xk in iter_cells()
        if float(
            _r[(_r["scenario"] == _sk) & (_r["sex"] == _xk) & (_r["input"] == "sbp")][
                "rank"
            ].iloc[0]
        )
        == 1.0
    )

_s32_map = _s32_m[_s32_m["output"] == "MAP"]
_s32_hyb = _s32_est["hybrid_combined"]
_s32_rows = []
for _sk, _xk in iter_cells():
    _sel = (_s32_map["scenario"] == _sk) & (_s32_map["sex"] == _xk) & (_s32_map["input"] == "dbp")
    _dn = float(_s32_map[_sel]["nom"].iloc[0])
    _da = float(_s32_map[_sel]["app"].iloc[0])
    _su = float(
        _s32_unc[
            (_s32_unc["scenario"] == _sk)
            & (_s32_unc["sex"] == _xk)
            & (_s32_unc["output"] == "MAP")
            & (_s32_unc["input"] == "sbp")
        ]["mu_star"].iloc[0]
    )
    _hd = float(
        _s32_hyb[
            (_s32_hyb["scenario"] == _sk)
            & (_s32_hyb["sex"] == _xk)
            & (_s32_hyb["output"] == "MAP")
            & (_s32_hyb["input"] == "dbp")
        ]["mu_star"].iloc[0]
    )
    _s32_rows.append({"f_c": _da / _dn, "f_flip": _su / _dn, "margin": _su / _hd})
_s32_cmb = pd.DataFrame(_s32_rows)
assert not (_s32_cmb["f_c"] > _s32_cmb["f_flip"]).any() and _s32_first[
    "hybrid_combined"
] == 8, "audit_claims: S032 gate 4 FAILED -- f_c threshold and hybrid rank disagree"

# --- Gates passed. Manuscript claims follow. ---

_lim_src = (REPO / "preprint_npj" / "paper.tex").read_text(encoding="utf-8")
# End delimiter re-registered 2026-10-06 (M. Sauthier review): the sentence after
# limit (vi) now opens "In addition, no trajectory-count convergence analysis".
_lim_txt = _lim_src[
    _lim_src.index("scope limits bound the conclusions") : _lim_src.index(
        "In addition, no trajectory-count convergence analysis"
    )
]
add(
    claim_id="T5.robust.scope_limits",
    section="Paper §3 Discussion",
    manuscript_text="Six scope limits bound the conclusions",
    source_file="preprint_npj/paper.tex",
    manuscript_value=6,
    computed_value=len(re.findall(r"\((?:i|ii|iii|iv|v|vi)\)~", _lim_txt)),
    tolerance_rule="exact_int",
)
add(
    claim_id="T5.robust.paper_dbp_shortened",
    section="Paper §3 limitation (vi)",
    manuscript_text="clipping shortened 9 of 20 DBP steps",
    source_file="data/runs/full_sweep/morris_sample.parquet",
    manuscript_value=9,
    computed_value=int(
        _s32_pairs[_s32_pairs["flipped"] == "dbp"]["shortened"].sum()
    ),
    tolerance_rule="exact_int",
)
add(
    claim_id="T5.robust.paper_sbp_contaminated",
    section="Paper §3 limitation (vi)",
    manuscript_text="applied DBP co-varied in 8 of 20 SBP steps",
    source_file="data/runs/full_sweep/morris_sample.parquet",
    manuscript_value=8,
    computed_value=int(
        _s32_pairs[_s32_pairs["flipped"] == "sbp"]["contaminated"].sum()
    ),
    tolerance_rule="exact_int",
)
add(
    claim_id="T5.robust.sbp_rank1_worst_estimator",
    section="Paper §3 limitation (vi) / Supplement S3.7 / monograph 2.2",
    manuscript_text="SBP remained rank 1 for MAP in all eight cells under six estimators",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=8,
    computed_value=min(_s32_first.values()),
    tolerance_rule="exact_int",
)
add(
    claim_id="T5.robust.n_estimators",
    section="Supplement S3.7 / monograph 2.2",
    manuscript_text="six sensitivity estimators are compared",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=6,
    computed_value=len(_s32_est),
    tolerance_rule="exact_int",
)
add(
    claim_id="T5.robust.min_combined_margin",
    section="Paper §3 limitation (vi) / Supplement S3.7 / monograph 2.2",
    manuscript_text="smallest SBP-to-DBP mu* ratio 1.22, in S2_M, under the combined estimator",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=1.22,
    computed_value=float(_s32_cmb["margin"].min()),
    tolerance_rule="displayed_2dp",
)
for _cid, _txt, _val, _got in (
    ("fc_min", "applied-to-nominal DBP mu* ratio ranges from 1.131", 1.131,
     float(_s32_cmb["f_c"].min())),
    ("fc_max", "applied-to-nominal DBP mu* ratio ranges to 3.289", 3.289,
     float(_s32_cmb["f_c"].max())),
    ("fflip_min", "uncontaminated-SBP-to-nominal-DBP ratio ranges from 2.266", 2.266,
     float(_s32_cmb["f_flip"].min())),
    ("fflip_max", "uncontaminated-SBP-to-nominal-DBP ratio ranges to 4.669", 4.669,
     float(_s32_cmb["f_flip"].max())),
):
    add(
        claim_id=f"T5.robust.{_cid}",
        section="Supplement S3.7 / monograph 2.2",
        manuscript_text=_txt,
        source_file="data/runs/full_sweep/aggregated.parquet",
        manuscript_value=_val,
        computed_value=_got,
        tolerance_rule="displayed_3dp",
    )

# T5.strat -- the transition-stratified table.
_st = _s32_ee[(_s32_ee["input"] == "sbp") & (_s32_ee["output"] == "MAP")].copy()
_st_lab = {
    int(r.trajectory): f"{int(r.sbp_lo)}-to-{int(r.sbp_hi)}"
    for r in _s32_pairs[_s32_pairs["flipped"] == "sbp"].itertuples()
}
_st["transition"] = _st["trajectory"].map(_st_lab)
_st["abs_ee"] = _st["ee"].abs()
_STRAT = {
    "100-to-120": (3, 9, 20.44, 15.74),
    "110-to-90": (15, 16, 24.94, 17.26),
    "120-to-100": (1, 19, 20.32, 16.74),
    "90-to-110": (0, 5, None, None),
}
for _t, (_nc, _nk, _mc, _mk) in _STRAT.items():
    _c = _st[(_st["transition"] == _t) & (_st["contaminated"])]
    _k = _st[(_st["transition"] == _t) & (~_st["contaminated"])]
    add(
        claim_id=f"T5.strat.{_t}.n_contaminated",
        section="Supplement S3.7 Table / monograph 2.2",
        manuscript_text=f"{_t}: {_nc} contaminated clean pairs",
        source_file="data/runs/full_sweep/aggregated.parquet",
        manuscript_value=_nc,
        computed_value=len(_c),
        tolerance_rule="exact_int",
    )
    add(
        claim_id=f"T5.strat.{_t}.n_uncontaminated",
        section="Supplement S3.7 Table / monograph 2.2",
        manuscript_text=f"{_t}: {_nk} uncontaminated clean pairs",
        source_file="data/runs/full_sweep/aggregated.parquet",
        manuscript_value=_nk,
        computed_value=len(_k),
        tolerance_rule="exact_int",
    )
    if _mc is not None:
        add(
            claim_id=f"T5.strat.{_t}.median_contaminated",
            section="Supplement S3.7 Table / monograph 2.2",
            manuscript_text=f"{_t}: median |EE| {_mc} for contaminated steps",
            source_file="data/runs/full_sweep/aggregated.parquet",
            manuscript_value=_mc,
            computed_value=float(_c["abs_ee"].median()),
            tolerance_rule="displayed_2dp",
        )
        add(
            claim_id=f"T5.strat.{_t}.median_uncontaminated",
            section="Supplement S3.7 Table / monograph 2.2",
            manuscript_text=f"{_t}: median |EE| {_mk} for uncontaminated steps",
            source_file="data/runs/full_sweep/aggregated.parquet",
            manuscript_value=_mk,
            computed_value=float(_k["abs_ee"].median()),
            tolerance_rule="displayed_2dp",
        )

# The applied-DBP path column of the same table. Anchoring only the counts and
# medians would leave the column that carries the whole dose-response reading
# unguarded, and it is the column a future resample would move first.
_MIDPOINT = {"100-to-120": 77.5, "110-to-90": 73.75, "120-to-100": 77.5}
_s32_smp_i = _s32_smp.set_index("idx")
for _t, _mid in _MIDPOINT.items():
    _rows = [
        r
        for r in _s32_pairs[_s32_pairs["flipped"] == "sbp"].itertuples()
        if f"{int(r.sbp_lo)}-to-{int(r.sbp_hi)}" == _t and r.contaminated
    ]
    add(
        claim_id=f"T5.strat.{_t}.applied_dbp_midpoint",
        section="Supplement S3.7 Table / monograph 2.2",
        manuscript_text=f"{_t}: applied-DBP path midpoint {_mid} mmHg",
        source_file="data/runs/full_sweep/morris_sample.parquet",
        manuscript_value=_mid,
        computed_value=float(
            pd.Series(
                [
                    (
                        float(_s32_smp_i.loc[r.idx_lo, "dbp_applied"])
                        + float(_s32_smp_i.loc[r.idx_hi, "dbp_applied"])
                    )
                    / 2.0
                    for r in _rows
                ]
            ).median()
        ),
        tolerance_rule="displayed_2dp",
    )

add(
    claim_id="T5.robust.matched_trajectories",
    section="Supplement S3.7 / monograph 2.2",
    manuscript_text="the 12 of 20 trajectories whose systolic step is uncontaminated",
    source_file="data/runs/full_sweep/morris_sample.parquet",
    manuscript_value=12,
    computed_value=len(_s32_good),
    tolerance_rule="exact_int",
)
add(
    claim_id="T5.robust.mu_drop_median_pct",
    section="Monograph 2.2",
    manuscript_text="dropping the contaminated pairs lowers mu*(SBP -> MAP) by a median of 10.4 percent",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=-10.4,
    computed_value=float(
        pd.Series(
            [
                100.0
                * (
                    float(
                        _s32_unc[
                            (_s32_unc["scenario"] == _sk) & (_s32_unc["sex"] == _xk)
                            & (_s32_unc["output"] == "MAP") & (_s32_unc["input"] == "sbp")
                        ]["mu_star"].iloc[0]
                    )
                    - float(
                        _s32_nom[
                            (_s32_nom["scenario"] == _sk) & (_s32_nom["sex"] == _xk)
                            & (_s32_nom["output"] == "MAP") & (_s32_nom["input"] == "sbp")
                        ]["mu_star"].iloc[0]
                    )
                )
                / float(
                    _s32_nom[
                        (_s32_nom["scenario"] == _sk) & (_s32_nom["sex"] == _xk)
                        & (_s32_nom["output"] == "MAP") & (_s32_nom["input"] == "sbp")
                    ]["mu_star"].iloc[0]
                )
                for _sk, _xk in iter_cells()
            ]
        ).median()
    ),
    tolerance_rule="displayed_1dp",
)

_st_eval = [t for t, v in _STRAT.items() if v[2] is not None]
add(
    claim_id="T5.strat.transitions_contaminated_higher",
    section="Supplement S3.7 / monograph 2.2",
    manuscript_text="contaminated steps had the higher median |EE| in all 3 evaluable transitions",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=len(_st_eval),
    computed_value=sum(
        1
        for _t in _st_eval
        if float(_st[(_st["transition"] == _t) & (_st["contaminated"])]["abs_ee"].median())
        > float(_st[(_st["transition"] == _t) & (~_st["contaminated"])]["abs_ee"].median())
    ),
    tolerance_rule="exact_int",
)
add(
    claim_id="T5.strat.loto_positive",
    section="Supplement S3.7 / monograph 2.2",
    manuscript_text="the stratified contrast stays positive in every leave-one-transition-out analysis",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=len(_st_eval),
    computed_value=sum(
        1
        for _t in _st_eval
        if float(_st[(_st["transition"] != _t) & (_st["contaminated"])]["abs_ee"].median())
        > float(_st[(_st["transition"] != _t) & (~_st["contaminated"])]["abs_ee"].median())
    ),
    tolerance_rule="exact_int",
)
add(
    claim_id="T5.strat.mu_drop_cells",
    section="Monograph 2.2",
    manuscript_text="dropping the contaminated pairs lowers mu*(SBP -> MAP) in 8 of 8 cells",
    source_file="data/runs/full_sweep/aggregated.parquet",
    manuscript_value=8,
    computed_value=sum(
        1
        for _sk, _xk in iter_cells()
        if float(
            _s32_unc[
                (_s32_unc["scenario"] == _sk) & (_s32_unc["sex"] == _xk)
                & (_s32_unc["output"] == "MAP") & (_s32_unc["input"] == "sbp")
            ]["mu_star"].iloc[0]
        )
        < float(
            _s32_nom[
                (_s32_nom["scenario"] == _sk) & (_s32_nom["sex"] == _xk)
                & (_s32_nom["output"] == "MAP") & (_s32_nom["input"] == "sbp")
            ]["mu_star"].iloc[0]
        )
    ),
    tolerance_rule="exact_int",
)

# Summary counts.
n_pass = sum(1 for c in claims if c.status == "PASS")
n_warn = sum(1 for c in claims if c.status == "WARN")
n_fail = sum(1 for c in claims if c.status == "FAIL")
n_run = len(claims)
n_skipped = len(skipped)
# Target total = anchors evaluated this run + anchors deliberately skipped for a
# missing-artefact reason. Computed dynamically so the ratio cannot go stale if
# anchors are added or removed later. Full local data tree -> N/N; public clone
# with the gitignored raw S021 trajectories absent -> (N-1)/N, 1 SKIPPED.
# Deliberately no illustrative value of N here: see the note at `skipped`.
n_expected = n_run + n_skipped

print("# Claims-Ledger Audit (S024)\n")
if n_skipped:
    _skip_detail = "; ".join(f"{cid}: {reason}" for cid, reason in skipped)
    print(
        f"**Anchors verified:** {n_run} / {n_expected} -- "
        f"{n_pass} PASS, {n_warn} WARN, {n_fail} FAIL, {n_skipped} SKIPPED "
        f"({_skip_detail}).\n"
    )
else:
    print(
        f"**Anchors verified:** {n_run} / {n_expected} -- "
        f"{n_pass} PASS, {n_warn} WARN, {n_fail} FAIL, 0 SKIPPED.\n"
    )
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

# Optional monograph anchor check (opt-in via --check-monograph). Same
# contract as the sync check: FAILs contribute to the exit code, WARNs do not.
n_mono_pass = n_mono_warn = n_mono_fail = 0
if _ARGS.check_monograph:
    n_mono_pass, n_mono_warn, n_mono_fail = check_monograph()


# -----------------------------------------------------------------------------
# Head-line counter guard (2026-08-03).
#
# The three head-line counters -- ledger anchors, crosswalk entries, monograph
# anchors -- describe the verification instrument itself, so none of the three
# layers above can cover them: an anchor asserting the anchor count would
# change the count it asserts. They were therefore the only literals in the
# corpus with no automated guard, and on 2026-08-01 exactly that failed:
# supplement.tex was updated 267 -> 289 while preprint/manuscript.md was not,
# leaving the two documents of one submission package contradicting each other.
# A third counter (crosswalk 98 -> 92) drifted the same way on 2026-08-02,
# because the N-1 restructuring deliberately did not touch supplement.tex S12.
#
# The guard is SHAPE-based, not locus-based, so it keeps working when text
# moves between documents: every `X / Y PASS` ratio quoted anywhere in the
# corpus must be one of the four legitimate audit ratios, and every counter
# quoted next to its context word must equal the live total.
# -----------------------------------------------------------------------------
def check_audit_counters(n_ledger: int, n_sync_total: int, n_mono_total: int) -> int:
    """Verify the audit's own head-line counters as quoted in the documents.

    Returns the number of FAILs (0 when every quoted counter is current).
    """
    print("\n## Head-line counter guard\n")

    docs = [
        REPO / "README.md",
        REPO / "preprint_npj" / "paper.tex",
        REPO / "preprint_npj" / "supplement.tex",
        REPO / "preprint" / "manuscript.md",
    ]
    # The only ratios a document may legitimately quote.
    ok_pairs = {
        (n_ledger, n_ledger),
        (n_ledger - 1, n_ledger),
        (n_sync_total, n_sync_total),
        (n_mono_total, n_mono_total),
    }
    # (regex, expected value, human label). One capture group each.
    singles = [
        # Lookahead is load-bearing: a bare `target of (\d+)` also matches the
        # Surviving Sepsis "MAP target of 65 mmHg" in both documents.
        (r"target of (\d+)(?=\s*(?:anchors|is computed))", n_ledger,
         "ledger target"),
        (r"Re-derives \*\*(\d+)\*\* numerical claims", n_ledger, "ledger total"),
        (r"(\d+) paper crosswalk entries", n_sync_total, "crosswalk total"),
        (r"\*\*(\d+)\*\* entries", n_sync_total, "crosswalk total"),
        (r"(\d+) mapped entries", n_sync_total, "crosswalk total"),
        (r"(\d+) monograph anchors", n_mono_total, "monograph total"),
        (r"\*\*(\d+)\*\* anchors", n_mono_total, "monograph total"),
    ]

    rows: list[tuple[str, str, str, str]] = []
    n_bad = 0
    for doc in docs:
        if not doc.exists():
            continue
        rel = doc.relative_to(REPO).as_posix()
        # Scan the WHOLE text, not line by line: a ratio wrapped across a line
        # break ("current state 313 / 313\nPASS on the ...") is invisible to a
        # per-line scan, and manuscript.md contains exactly that. Line numbers
        # are recovered from the match offset.
        text = doc.read_text(encoding="utf-8")

        def _lineno(off: int) -> int:
            return text.count("\n", 0, off) + 1

        # Both the "N/N PASS" and the "N / N on a public clone" phrasings: the
        # second carries no PASS token and was missed by the first version.
        for m in re.finditer(
            r"(\d+)\s*/\s*(\d+)\s+(PASS|on a public clone)", text
        ):
            pair = (int(m.group(1)), int(m.group(2)))
            good = pair in ok_pairs
            n_bad += 0 if good else 1
            rows.append(
                (f"{rel}:{_lineno(m.start())}", "ratio",
                 f"{m.group(1)}/{m.group(2)} {m.group(3)}",
                 "PASS" if good else
                 f"FAIL -- expected one of {sorted(ok_pairs)}")
            )
        for pat, expected, label in singles:
            for m in re.finditer(pat, text):
                good = int(m.group(1)) == expected
                n_bad += 0 if good else 1
                rows.append(
                    (f"{rel}:{_lineno(m.start())}", label, m.group(1),
                     "PASS" if good else f"FAIL -- expected {expected}")
                )

    if not rows:
        print("_No head-line counter quoted in any document._\n")
        return 0
    print("| locus | counter | quoted | verdict |")
    print("|---|---|---:|---|")
    for locus, label, quoted, verdict in rows:
        print(f"| `{locus}` | {label} | {quoted} | {verdict} |")
    print(
        f"\n**Head-line counters:** {len(rows)} quoted, "
        f"{len(rows) - n_bad} PASS, {n_bad} FAIL "
        f"(live totals: ledger {n_ledger}, crosswalk {n_sync_total}, "
        f"monograph {n_mono_total}).\n"
    )
    return n_bad


# -----------------------------------------------------------------------------
# S021 clock guard (2026-08-06).
#
# The manuscript described the S021 hyperoxia reruns as a saved-state
# continuation -- a reload of Pulse's engine state at the end of the original
# 120-second run, continuing 300 s further. No such mechanism exists in this
# repository: scripts/run_s021_hyperoxia_convergence.py builds a fresh config
# and raises duration_hours, so each rerun re-executes from time zero. Measured
# proof: across all 60 pairs the atlas CSVs are byte-identical over t=0-120 s,
# and the Pulse-native CSVs are byte-identical over the 12,000 points of
# t=0.02-240.00 s, settle phase included.
#
# No layer could see this: the defect lived in prose and carried no drifting
# literal. Every published number was and remains correct -- the failure was
# purely mechanistic, which is exactly the class the ledger cannot catch.
#
# NOTE ON 420: `420 s of Pulse-internal time` is TRUE and measured
# (VENT_SETTLE_S = 120 s + 300 s recorded = 420 s on Pulse's own clock, read
# off output_pulse_native.csv). It is deliberately NOT forbidden. No forbidden
# string below is a bare "420", which also keeps PMID 36661420 in
# manuscript.md from ever matching.
#
# Expectations are per file: the paper carries only the 300 s recorded clock,
# the supplement carries both clocks (maintainer decision, 2026-08-06).
# -----------------------------------------------------------------------------
S021_FORBIDDEN: dict[str, tuple[str, ...]] = {
    "preprint_npj/paper.tex": (
        "saved engine state",
        "continued for an additional 300",
        "of total simulated time",
    ),
    "preprint_npj/supplement.tex": (
        "saved engine state",
        "saved Pulse state",
        "saved-state reload",
        "reload point",
        "continues for an additional 300",
        "of total simulated time",
        "$t' = 0$",
    ),
    "preprint/manuscript.md": (
        "300 s beyond the locked 120 s",
        "beyond the 120 s window",
        "420 s total",
        "to 420 s of total simulated time",
    ),
    "scripts/make_supp_fig_s3.py": (
        "saved Pulse state",
        "corresponds to $t = 120$ s",
        "t'=0",
    ),
}

S021_REQUIRED: dict[str, tuple[str, ...]] = {
    "preprint_npj/paper.tex": (
        "300 seconds",
        "$t = 240$--$300$~s",
    ),
    "preprint_npj/supplement.tex": (
        "420~s of Pulse-internal time",
        "recorded simulation time",
        "120-second ventilator-settling phase",
    ),
    "scripts/make_supp_fig_s3.py": ("Recorded simulation time",),
}


def check_s021_clock() -> int:
    """Guard the S021 two-clock framing. Returns the number of FAILs."""
    print("\n## S021 clock guard\n")
    rows: list[tuple[str, str, str, str]] = []
    n_bad = 0

    for rel, needles in S021_FORBIDDEN.items():
        path = REPO / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            hits = text.count(needle)
            verdict = "PASS" if hits == 0 else f"**FAIL** ({hits}x)"
            if hits:
                n_bad += 1
            rows.append((rel, "forbidden", needle, verdict))

    for rel, needles in S021_REQUIRED.items():
        path = REPO / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            hits = text.count(needle)
            verdict = "PASS" if hits >= 1 else "**FAIL** (absent)"
            if not hits:
                n_bad += 1
            rows.append((rel, "required", needle, verdict))

    print("| file | kind | string | verdict |")
    print("|---|---|---|---|")
    for rel, kind, needle, verdict in rows:
        print(f"| `{rel}` | {kind} | `{needle}` | {verdict} |")
    print(f"\n**S021 clock guard:** {len(rows)} checks, {len(rows) - n_bad} PASS, {n_bad} FAIL.\n")
    return n_bad


n_s021_fail = check_s021_clock()


# -----------------------------------------------------------------------------
# S021 converged-plateau claim (2026-08-06).
#
# Two different statistics round to the same published integer 643:
#   S1_plateau_median_mmHg           = 643.3063  (all 44 S1 reruns)
#   S1_converged_plateau_median_mmHg = 642.8716  (the 41 drift-converged ones)
# They differ by 0.4348, below whole_unit = 0.5, so no ledger anchor can tell
# them apart: swapping one for the other leaves any such anchor green.
#
# T1.23 correctly checks the 44-run median, because that is what the MONOGRAPH
# claims (manuscript.md:2664 "S1 (n = 44): plateau median 643.3 mmHg", and the
# table at :2684). The paper and supplement instead attribute their 643 to the
# 41 CONVERGED runs, and nothing verified that quantity.
#
# This check closes the gap without adding a 383rd anchor -- which would have
# cascaded into 16 counter-bearing lines across README, supplement and
# monograph for a purely bookkeeping reason, and would have pointed the ledger
# at a quantity outside its contract (the ledger audits the monograph).
#
# It is deliberately a JOINT check: the count, the source statistic, its
# published rounding, and the prose that ties them together must agree. Any one
# of them alone is satisfiable by the wrong quantity.
# -----------------------------------------------------------------------------
# 41 and 38 until 2026-09-01. The S021 window selection used a strict comparison
# on a drifting time grid, so the drift was fitted on 12 samples where the
# preregistration fixes 13, and S1_F_0106_long sat on the wrong side of the
# 15 mmHg/60 s threshold. Repairing the selection moved it out of the converged
# set. A fourth category appears with it: that run is non-converged and is NOT a
# runaway, so the partition below gained a term. See
# audit/synthesis_pass_2026_08.md sections 15 and 16.
S021_CONVERGED_N = 40
S021_PHYSIO_CONVERGED = 37
S021_CONVERGED_PUBLISHED_MMHG = 643
# The paper-side literal deliberately omits the leading article. On 2026-09-05
# the sentence carrying it was split for readability, at P.J.'s request for
# fluidity, and "the converged S1 plateau median" became "The converged S1
# plateau median" at the head of its own sentence. The claim did not change --
# only its position in the sentence did -- so the anchor drops the article
# rather than pinning a capitalisation that carries no meaning. What the anchor
# must keep pinning is the POPULATION: "converged S1 plateau", the 40
# drift-converged reruns, which is not the 37 physiologically converged ones
# that the checks above hold apart.
S021_CONVERGED_CONTEXT: tuple[tuple[str, str], ...] = (
    ("preprint_npj/supplement.tex", "over the 40 drift-converged runs"),
    # Re-pinned 2026-10-06: the M. Sauthier round shortened the sentence to
    # "with a median of 643 mmHg"; the author restored the denominator (D30).
    ("preprint_npj/paper.tex", "with a median of 643~mmHg over all 40"),
)
# 2026-09-08, reviewer point 3.6: the paper-side literal was strengthened rather
# than merely repaired. It used to read "converged S1 plateau median was
# 643~mmHg", which named the population only by the adjective "converged" and
# left a reader to infer which of the two populations was meant. Section 2.4 now
# states the partition outright -- three of the 40 drift-converged reruns
# stabilise above 700 mmHg, so 37 of 44 plateau below that value -- and the
# median sentence names its own denominator: "over all 40 drift-converged runs".
# The anchor pins that phrase together with the value, so the two populations
# cannot be silently swapped under the number in either direction.


def check_s021_converged_plateau() -> int:
    """Verify the 40-run converged plateau median behind the published 643 mmHg."""
    print("\n## S021 converged-plateau claim\n")
    rows: list[tuple[str, str, str]] = []
    n_bad = 0

    s1 = _s21_plateau[_s21_plateau["scenario"] == "S1"]
    conv = s1[s1["converged"]]

    # 1. the converged count
    n_conv = int(len(conv))
    ok = n_conv == S021_CONVERGED_N
    n_bad += 0 if ok else 1
    rows.append(("converged S1 reruns", f"{n_conv} (expected {S021_CONVERGED_N})",
                 "PASS" if ok else "**FAIL**"))

    # 2. the source statistic, recomputed from the parquet and cross-checked
    #    against summary.json -- two artefacts, so a stale summary cannot hide
    #    a drifted parquet.
    med_parquet = float(conv["PaO2_plateau_mmHg"].median())
    med_summary = float(s21_sum["S1_converged_plateau_median_mmHg"])
    ok = abs(med_parquet - med_summary) <= 0.0005
    n_bad += 0 if ok else 1
    rows.append(("parquet vs summary.json",
                 f"{med_parquet:.4f} vs {med_summary:.4f}",
                 "PASS" if ok else "**FAIL**"))

    # 3. its published rounding
    ok = round(med_parquet) == S021_CONVERGED_PUBLISHED_MMHG
    n_bad += 0 if ok else 1
    rows.append(("rounds to published value",
                 f"round({med_parquet:.4f}) = {round(med_parquet)} "
                 f"(published {S021_CONVERGED_PUBLISHED_MMHG})",
                 "PASS" if ok else "**FAIL**"))

    # 3b. The PHYSIOLOGICALLY converged subset, added 2026-08-19 when §2.4 began
    # quoting it by size. Three populations of S1 reruns now appear in print and
    # they are easy to confuse: 44 reruns in total, 41 drift-converged (median
    # 643, quoted in §2.4 and the abstract), and 38 physiologically converged
    # (median 639, the figure trajectory and the t = 180 s statistic). The
    # difference between 41 and 38 is exactly the three runaways that clear the
    # drift criterion while sitting above 700 mmHg, so the partition must hold:
    # 38 + 3 runaway-converged + 3 runaway-non-converged = 44.
    #
    # Note that "38" collides with three unrelated ledger anchors that also
    # carry the value 38 (S3_F not_steady_state, S3_F n_nss_locked, and the
    # literal hard-flag red count), which is precisely why this one needs its
    # own check rather than a grep for the numeral.
    s1_all = s21_plat[s21_plat["scenario"] == "S1"]
    physio = s1_all[s1_all["converged"] & (s1_all["PaO2_plateau_mmHg"] <= 700)]
    runaway = s1_all[s1_all["PaO2_plateau_mmHg"] > 700]
    runaway_conv = runaway[runaway["converged"]]

    ok = len(physio) == S021_PHYSIO_CONVERGED
    n_bad += 0 if ok else 1
    rows.append(("physiologically converged S1 reruns (converged and <= 700 mmHg)",
                 f"{len(physio)} (published {S021_PHYSIO_CONVERGED})",
                 "PASS" if ok else "**FAIL**"))

    # Fourth term added 2026-09-01: a run that is neither converged nor a
    # runaway. Before the window fix every non-converged S1 rerun was a runaway,
    # so three terms closed the partition; S1_F_0106_long is now non-converged
    # with a plateau of 559 mmHg and belongs to none of the first three.
    other = s1_all[~s1_all["converged"] & (s1_all["PaO2_plateau_mmHg"] <= 700)]
    parts = (len(physio), len(runaway_conv), len(runaway) - len(runaway_conv), len(other))
    ok = sum(parts) == len(s1_all) == 44 and len(physio) + len(runaway_conv) == S021_CONVERGED_N
    n_bad += 0 if ok else 1
    rows.append(("the 44 S1 reruns partition, and physio + runaway-converged = "
                 f"{S021_CONVERGED_N}",
                 f"{parts[0]} + {parts[1]} + {parts[2]} + {parts[3]} = {sum(parts)}; "
                 f"{parts[0]} + {parts[1]} = {parts[0] + parts[1]}",
                 "PASS" if ok else "**FAIL**"))

    # NEGATIVE CONTROL: the two populations must stay distinguishable, or the
    # sentence in §2.4 could quote either one and still look right.
    ok = len(physio) != S021_CONVERGED_N
    n_bad += 0 if ok else 1
    rows.append((f"the {S021_PHYSIO_CONVERGED}-run and {S021_CONVERGED_N}-run "
                 "populations stay distinct",
                 f"{len(physio)} vs {S021_CONVERGED_N}",
                 "PASS" if ok else "**FAIL**"))

    # 4. the prose that ties the count to the value
    for rel, needle in S021_CONVERGED_CONTEXT:
        path = REPO / rel
        hits = path.read_text(encoding="utf-8").count(needle) if path.exists() else 0
        ok = hits >= 1
        n_bad += 0 if ok else 1
        rows.append((f"`{rel}`", f"`{needle}`", "PASS" if ok else "**FAIL** (absent)"))

    print("| check | observed | verdict |")
    print("|---|---|---|")
    for label, observed, verdict in rows:
        print(f"| {label} | {observed} | {verdict} |")
    print(
        f"\n**S021 converged-plateau claim:** {len(rows)} checks, "
        f"{len(rows) - n_bad} PASS, {n_bad} FAIL.\n"
    )
    return n_bad


# -----------------------------------------------------------------------------
# README science guard (2026-08-10).
#
# The hole this closes. The ledger covers preprint/manuscript.md; the crosswalk
# covers paper.tex + supplement.tex; the head-line counter guard covers the
# audit's own ratios wherever they are quoted, README included. Nothing covered
# the README's SCIENTIFIC numbers. That gap is not hypothetical: the S018
# dose-response was corrected on 2026-06-16 in the ledger, the crosswalk, a
# figure, the paper, the supplement and six loci of the monograph -- and the
# README kept printing the retracted "20 / 20 -> 2 / 20 -> 0 / 20" for SEVEN
# WEEKS while every audit layer reported green. The README is the first thing a
# reader of the public repository sees.
#
# Why this is a separate check and not extra crosswalk rows. The crosswalk
# counts each literal across a COMBINED paper.tex + supplement.tex corpus and
# asserts an exact total. Adding README.md to that corpus would change the
# occurrence count of every existing row that also appears in the README, and
# would move the crosswalk total (94) that four documents quote. A separate
# guard with its own scope costs nothing and moves no published counter.
#
# What each row asserts, end to end:
#   1. the literal is still present in README.md;
#   2. the number as the README writes it parses to the value the ledger holds,
#      within that ledger entry's own tolerance;
#   3. the ledger entry itself is PASS, i.e. still re-derived from the frozen
#      artefacts.
# So the chain is README -> ledger -> data artefact. Editing the README breaks
# (1); changing the data breaks (3); a silent drift between them breaks (2).
#
# Whitespace is normalised on both sides before matching, because README prose
# is hard-wrapped: "worst-case from 1.826\n  -> 0.018" is one claim split
# across two lines, and a literal match would miss it. Normalising is what lets
# a row quote the claim as a human reads it.
#
# DELIBERATELY OUT OF SCOPE, recorded so the omission is not mistaken for an
# oversight: the wall-clock figures "9-23 h" (README:31, :228) and "27-46 h"
# (:231). No ledger anchor exists for either -- they are provenance statements
# about how long the sweep took on given hardware, not quantities re-derived
# from an artefact -- so there is nothing to bind them to. Anchoring them would
# mean first creating a ledger entry with a real computed source.
#
# Each row: (literal as it appears in README.md, the number inside that literal
# exactly as written, ledger claim_id, human label).
README_SCIENCE_ANCHORS = [
    ("Median 0.928", "0.928", "T1.08", "H1 median top-3 fraction"),
    ("range 0.658 – 0.998", "0.658", "T1.09", "H1 top-3 range, lower end"),
    ("range 0.658 – 0.998", "0.998", "T1.10", "H1 top-3 range, upper end"),
    ("**5 of 24**", "5", "T1.15", "H4 Wasserstein survivors under BH-FDR"),
    ("(p_emp = 0.022)", "0.022", "T2.bh.s2_spo2.p", "S2 SpO2 p_emp, demoted by BH"),
    ("34 implausibly-flagged runs produce PaO2 > 600 mmHg", "34", "T1.21",
     "F-003 runs above the 600 mmHg ceiling"),
    ("91 % at FiO2 ≥ 0.95", "91", "T1.22", "F-003 share at FiO2 >= 0.95"),
    ("264 / 1,280 (20.6 %)", "20.6", "T1.02a", "F-004 primary-flag rate"),
    ("0.351 → 0.016", "0.351", "T1.03", "median Vt CV before the trigger lock"),
    ("0.351 → 0.016", "0.016", "T1.04", "median Vt CV after the trigger lock"),
    ("worst-case from 1.826 → 0.018", "1.826", "T1.05",
     "worst-case Vt CV before the lock (run S1_F_0117)"),
    ("worst-case from 1.826 → 0.018", "0.018",
     "T1.s014.worstcase_locked_vtcv",
     "same run after the lock -- NOT the max locked CV, which is 0.112"),
    ("lock-below-0.05 fraction = 78.1 %", "78.1", "T1.06c.s14_frac_below",
     "S014 fraction of reruns below the 0.05 threshold"),
    ("**1.6 %**", "1.6", "T1.13", "overall divergence rate"),
    ("male default 4,802.63 mL", "4,802.63", "T3.s027.bv_default",
     "male BloodVolumeBaseline default"),
    ("female 3,996.09 mL", "3,996.09", "T3.s028.bv_female_default",
     "female BloodVolumeBaseline default"),
    ("4,082.24 mL", "4,082.24", "T3.s027.bv_floor",
     "male blood-volume floor imposed at setup"),
]


def check_readme_science(ledger_claims: list[Claim]) -> int:
    """Bind the README's scientific numbers to the ledger entries behind them.

    Returns the number of FAILs (0 when every anchored number is current).
    """
    print("\n## README science guard\n")

    readme = REPO / "README.md"
    if not readme.exists():
        print("_WARN: README.md not found; guard skipped._\n")
        return 0

    # Collapse every run of whitespace so a hard-wrapped claim still matches.
    text = re.sub(r"\s+", " ", readme.read_text(encoding="utf-8"))
    by_id = {c.claim_id: c for c in ledger_claims}

    rows: list[tuple[str, str, str, str]] = []
    n_bad = 0
    for literal, number, claim_id, what in README_SCIENCE_ANCHORS:
        needle = re.sub(r"\s+", " ", literal)
        claim = by_id.get(claim_id)

        if number not in literal:
            # A coding error in the table above, not a defect in the README:
            # the row quotes a number that is not in its own literal.
            verdict, note = "FAIL", f"table error: {number!r} absent from the row's literal"
        elif needle not in text:
            verdict, note = "FAIL", "literal absent from README.md -- reworded, or the claim was removed"
        elif claim is None:
            verdict, note = "FAIL", f"claim_id `{claim_id}` not in the ledger"
        elif claim.status == "SKIPPED":
            # A public clone without the gitignored raw data cannot re-derive
            # every anchor. Not the README's fault, and not a reason to fail.
            verdict, note = "SKIP", "ledger entry skipped (raw artefact absent)"
        elif claim.status != "PASS":
            verdict, note = "FAIL", f"ledger entry `{claim_id}` is {claim.status}, so this number is not re-derived"
        else:
            written = float(number.replace(",", ""))
            target = claim.computed_value
            tol = TOLERANCE[claim.tolerance_rule]
            if target is None:
                verdict, note = "FAIL", f"ledger entry `{claim_id}` has no computed value"
            elif abs(written - target) <= tol + FLOAT_EPS:
                verdict, note = "PASS", ""
            else:
                verdict, note = "FAIL", f"README says {number}, ledger computes {target} (tolerance {tol})"

        if verdict == "FAIL":
            n_bad += 1
        rows.append((claim_id, what, number, verdict + (f" -- {note}" if note else "")))

    print("| ledger anchor | quantity | README value | verdict |")
    print("|---|---|---:|---|")
    for claim_id, what, number, verdict in rows:
        print(f"| `{claim_id}` | {what} | {number} | {verdict} |")
    n_skip = sum(1 for r in rows if r[3].startswith("SKIP"))
    print(
        f"\n**README science guard:** {len(rows)} anchored, "
        f"{len(rows) - n_bad - n_skip} PASS, {n_bad} FAIL, {n_skip} SKIPPED.\n"
    )
    return n_bad


# -----------------------------------------------------------------------------
# Figure-legend length guard (2026-08-10).
#
# npj caps a figure legend at 350 words, and its submission guidelines extend
# that to supplementary figures. On 2026-08-10 two legends were found over it --
# paper Figure 2 at 363 words and supplement Figure S5 at 361 -- and both had
# been over since ed5259f added their extra panels. The compliance register had
# measured a maximum of 322 words on 2026-08-03; that measurement was correct
# when taken and simply went stale, because nothing re-measured it. This guard
# is what re-measures it.
#
# THE UNIT IS THE EDITORIAL LEGEND, NOT THE `\caption{}`. This is the whole
# difficulty. The paper's Figure 3 carries SEVEN caption objects -- one main
# caption plus one per panel, inside `subfigure` blocks -- and they are one
# legend for npj's purposes, so the cap applies to their sum (293 words, under).
# Counting caption objects separately would understate a long multi-panel
# figure; counting unrelated floats together would invent a breach. So each
# top-level figure/table environment is one unit, and nested subfigure captions
# are summed into it.
#
# TWO COUNTS, BOTH REPORTED, because the convention is genuinely ambiguous and a
# single number would hide which one a verdict rests on -- the same ambiguity
# that makes the abstract count read two ways (the literal figures are not
# repeated here: they drift with the text, and nothing in this file re-measures
# them -- see audit/npj_format_compliance.md N-2). `strict` counts tokens bearing a
# letter or digit; `wp` counts every whitespace-separated token, as a word
# processor does. A legend fails if EITHER exceeds the cap.
#
# SOURCE, NOT PDF. Two earlier attempts at this measurement were unsound and are
# recorded so neither is rebuilt: matching `\caption{` only at the start of a
# line misses the six sub-captions of Figure 3, which do not begin their lines;
# and ending a legend at the first blank line in the PDF text swallows the table
# body, which reported "Table 1: 478 words" for a one-sentence legend. The
# structured source is the primary instrument. The rendered PDF is a secondary
# spot-check only, and only where the delimitation is unambiguous.
LEGEND_CAP = 350
_LEGEND_KEEP_ARG = ("textbf", "emph", "textit", "texttt", "text", "mathrm",
                    "textrm", "underline")
_LEGEND_DROP_ALL = ("cite", "label", "ref", "hyperlink", "hypertarget", "url",
                    "citep", "citet")
_LEGEND_TOP = r"(figure\*?|table\*?|sidewaystable\*?)"
_LEGEND_SUB = r"(subfigure|subtable)"


def _legend_rendered(body: str) -> str:
    """Reduce a caption body to what a reader actually reads."""
    s = body
    for name in _LEGEND_DROP_ALL:          # \cite{...} renders as a bracket number
        s = re.sub(r"\\%s(\[[^\]]*\])?\{[^{}]*\}" % name, " ", s)
    for name in _LEGEND_KEEP_ARG:          # \textbf{x} renders as x
        prev = None
        while prev != s:
            prev = s
            s = re.sub(r"\\%s\{([^{}]*)\}" % name, r"\1", s)
    s = re.sub(r"\$[^$]*\$", "MATH", s)    # inline math renders as one token
    s = s.replace("\\%", "%").replace("\\&", "&").replace("\\_", "_")
    s = re.sub(r"\\\\", " ", s)
    s = re.sub(r"\\[a-zA-Z]+\*?", " ", s)  # any macro left renders as nothing
    s = s.replace("~", " ")
    s = re.sub(r"[{}]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _legend_counts(body: str) -> tuple[int, int]:
    toks = _legend_rendered(body).split()
    return len([t for t in toks if re.search(r"[A-Za-z0-9]", t)]), len(toks)


def _caption_body(src: str, at: int) -> str:
    """Caption text from `at` to its matching close brace, braces balanced."""
    i, depth = at, 1
    while i < len(src) and depth:
        c = src[i]
        if c == "\\":                      # an escaped char cannot close a group
            i += 2
            continue
        depth += 1 if c == "{" else -1 if c == "}" else 0
        i += 1
    return src[at:i - 1]


def legend_units(src: str):
    """Yield (name, strict, wp, n_captions) for each editorial legend unit."""
    n_fig = n_tab = 0
    for m in re.finditer(r"\\begin\{%s\}" % _LEGEND_TOP, src):
        kind = m.group(1)
        depth, i = 1, m.end()
        while i < len(src) and depth:
            nxt = re.search(r"\\(begin|end)\{%s\}" % kind, src[i:])
            if not nxt:
                break
            depth += 1 if nxt.group(1) == "begin" else -1
            i += nxt.end()
        block = src[m.end():i]

        sub_spans = []
        for sm in re.finditer(r"\\begin\{%s\}" % _LEGEND_SUB, block):
            se = re.search(r"\\end\{%s\}" % _LEGEND_SUB, block[sm.end():])
            if se:
                sub_spans.append((sm.start(), sm.end() + se.end()))

        strict = wp = n_caps = 0
        for cm in re.finditer(r"\\caption\{", block):
            n_caps += 1
            s, w = _legend_counts(_caption_body(block, cm.end()))
            strict += s
            wp += w
        if not n_caps:
            continue
        if kind.startswith("figure"):
            n_fig += 1
            name = "Figure %d" % n_fig
        else:
            n_tab += 1
            name = "Table %d" % n_tab
        yield name, strict, wp, n_caps


def check_legend_lengths() -> int:
    """Verify every editorial legend stays within npj's 350-word cap.

    Returns the number of FAILs (0 when every legend is inside the cap).
    """
    print("\n## Figure-legend length guard\n")

    rows: list[tuple[str, str, int, int, str]] = []
    n_bad = 0
    for rel in ("preprint_npj/paper.tex", "preprint_npj/supplement.tex"):
        path = REPO / rel
        if not path.exists():
            print("_WARN: %s not found; guard skipped._\n" % rel)
            continue
        src = path.read_text(encoding="utf-8")
        for name, strict, wp, n_caps in legend_units(src):
            over = max(strict, wp) > LEGEND_CAP
            if over:
                n_bad += 1
            rows.append((rel.split("/")[-1], name, strict, wp,
                         "FAIL" if over else "PASS"))

    print("| document | legend | strict | word-processor | verdict |")
    print("|---|---|---:|---:|---|")
    for doc, name, strict, wp, verdict in rows:
        print("| `%s` | %s | %d / %d | %d / %d | %s |"
              % (doc, name, strict, LEGEND_CAP, wp, LEGEND_CAP, verdict))
    worst = max((max(r[2], r[3]) for r in rows), default=0)
    print(
        f"\n**Legend lengths:** {len(rows)} editorial legends, "
        f"{len(rows) - n_bad} PASS, {n_bad} FAIL "
        f"(cap {LEGEND_CAP}; longest {worst}).\n"
    )
    return n_bad


# -----------------------------------------------------------------------------
WASSERSTEIN_RAW_EXCEEDANCES = 6
WASSERSTEIN_DROPPED_BY_BH = ("S2 SpO2",)

# Sex-stratified divergence guard (2026-08-11).
#
# The hole this closes. The supplement and the monograph both described the
# input-driven regime as producing "an approximately fivefold higher divergence
# rate on the male body than on the female", while the female count in that
# regime is ZERO -- an undefined ratio, and a direct contradiction of the main
# paper's own "all 20 fell on the male reference body ... zero divergences".
# The number was introduced in e736d0d with no derivation, copied into the
# supplement by df821f3, and survived because it was anchored NOWHERE: `grep -c
# fivefold scripts/*.py` returned 0 in every script. The step-wise fact-check
# register did mark it green, but its contract is paper/supplement <-> monograph
# agreement, not number <-> data: the two documents agreed with each other,
# both carrying the same unverifiable value.
#
# Why the counts are recomputed rather than asserted as literals. Correcting the
# prose once would leave exactly the same exposure the defect had: nothing would
# re-measure it. The chain here is data -> prose. Row 1-3 rebuild the per-sex
# divergence totals from results/cell_flag_summary.csv, so a change in the sweep
# breaks the guard; rows 4+ require the contextualised prose that ties those
# totals to their denominator, so an edit that drops the scope breaks it too.
#
# Rows 4+ deliberately require the REGIME-SCOPED form. "None occurred on the
# female body" is false unscoped: in the severity-driven regime (supplement S5,
# continuous-severity sweep) female divergences do occur (F = 19, M = 14). The
# guard therefore pins the phrasing that carries its own denominator, not the
# bare fact.
#
# The forbidden list scans the three MANUSCRIPT files only. The audit register
# audit/fivefold_divergence_ratio_defect.md documents the defect and necessarily
# quotes it; scanning that file would make the register unfileable.
SEX_DIV_SOURCE = "results/cell_flag_summary.csv"
SEX_DIV_EXPECTED = {"M": 20, "F": 0}
SEX_DIV_FEMALE_RUNS = 640
# Effective input-side sample (2026-08-16).
#
# The hole this closes. Every input-signature statement about the divergence
# cluster is counted over the 20 EVENTS ("16 of 20", "13 of 20"), which reads as
# 20 independent draws from the input space. It is not: the 20 runs span only 8
# distinct operational-input vectors, because 4 vectors diverge in all four male
# cells and are therefore counted four times each. The dominant hypotensive-
# tachypneic signature is 16/20 events but only 4/8 vectors -- a 4x difference in
# evidential weight. Nothing in the repository measured this, and the paper did
# not disclose it, so a reviewer could reasonably read the signature as better
# sampled than it is.
#
# Why recomputed rather than asserted. Same reasoning as the rows above: a prose
# fix alone would leave nothing re-measuring the decomposition. Row A rebuilds
# the distinct-vector count from the sweep artefact; row B pins the replication
# STRUCTURE (four vectors seen four times, four seen once), so a sweep whose
# divergence set regrouped differently breaks the guard even if the total held;
# row C requires the paper to keep disclosing it.
#
# Run counts are NOT changed by this: "16 of 20" and "13 of 20" remain true as
# event counts, and the blood-volume rescue (20/20 -> 0/20) is legitimately a run
# count, since each of the 20 is a distinct (vector, scenario) pair. The unit
# only collapses to 8 for statements about which INPUTS are associated with
# divergence.
SEX_DIV_VECTOR_COLS = ["in_hr", "in_sbp", "in_dbp", "in_rr", "in_vt",
                       "in_fio2", "in_peep"]
SEX_DIV_DISTINCT_VECTORS = 8
# {times a vector recurs: how many vectors recur that often}
SEX_DIV_VECTOR_STRUCTURE = {1: 4, 4: 4}
# Literals re-registered 2026-10-06 (M. Sauthier review): same facts, same
# denominators, condensed wording.
SEX_DIV_UNIT_PROSE = (
    "preprint_npj/paper.tex",
    "span only 8 distinct input vectors",
)
SEX_DIV_DOCS = [
    "preprint_npj/paper.tex",
    "preprint_npj/supplement.tex",
    "preprint/manuscript.md",
]
SEX_DIV_CONTEXT = [
    ("preprint_npj/paper.tex", "diverged runs (1.6~\\%) were on the male reference body"),
    ("preprint_npj/paper.tex",
     "none of the 640 runs on the female body diverged"),
    ("preprint_npj/supplement.tex",
     "20 events in the four male cells, none in the 640 female runs"),
    ("preprint/manuscript.md", "20 divergence events on the male"),
]
# Literal reintroductions, plus a narrow proximity pattern for a reworded one.
# The pattern requires "female" within 80 characters of a fold-change token, so
# the unrelated "200-fold" in supplement S5 does not trip it.
# Two alternations, because the defect existed in BOTH forms and a single
# pattern caught only one of them. The supplement wrote "fivefold"; the
# monograph wrote "~ 5x higher than female", which contains no fold token at
# all. Calibrating the first pattern surfaced that hole -- an uncalibrated
# guard would have re-admitted the monograph's exact original wording.
SEX_DIV_FORBIDDEN = ["fivefold", "five-fold"]
SEX_DIV_FORBIDDEN_RE = re.compile(
    r"(?:\d+|two|three|four|five|six|seven|eight|nine|ten)[-\s×]*fold"
    r"[^.]{0,80}female"
    r"|"
    r"\d[\d.]*\s*[×x]\s*(?:higher|more|greater|as\s+many)[^.]{0,80}female",
    re.IGNORECASE,
)


def check_sex_divergence() -> int:
    """Bind the per-sex divergence totals to the data and to the scoped prose."""
    print("\n## Sex-stratified divergence guard\n")
    rows: list[tuple[str, str, str]] = []
    n_bad = 0

    flags = pd.read_csv(REPO / SEX_DIV_SOURCE)

    # 1-2. per-sex divergence totals, rebuilt from the artefact
    for sex, expected in SEX_DIV_EXPECTED.items():
        observed = int(flags.loc[flags["sex"] == sex, "n_diverged"].sum())
        ok = observed == expected
        n_bad += 0 if ok else 1
        rows.append((f"{sex} divergence total (recomputed)",
                     f"{observed} (expected {expected})",
                     "PASS" if ok else "**FAIL**"))

    # 3. the female denominator the prose quotes
    n_female = int(flags.loc[flags["sex"] == "F", "n_total"].sum())
    ok = n_female == SEX_DIV_FEMALE_RUNS
    n_bad += 0 if ok else 1
    rows.append(("female runs (denominator in prose)",
                 f"{n_female} (expected {SEX_DIV_FEMALE_RUNS})",
                 "PASS" if ok else "**FAIL**"))

    # 3b. the effective input-side sample: 20 events, 8 distinct vectors
    dv = agg.loc[agg["diverged"], SEX_DIV_VECTOR_COLS].round(4)
    n_vec = len(dv.drop_duplicates())
    ok = n_vec == SEX_DIV_DISTINCT_VECTORS
    n_bad += 0 if ok else 1
    rows.append(("distinct input vectors among the diverged (recomputed)",
                 f"{n_vec} (expected {SEX_DIV_DISTINCT_VECTORS})",
                 "PASS" if ok else "**FAIL**"))

    # 3c. and how those vectors recur across cells
    structure = dict(sorted(dv.groupby(SEX_DIV_VECTOR_COLS).size()
                            .value_counts().items()))
    ok = structure == SEX_DIV_VECTOR_STRUCTURE
    n_bad += 0 if ok else 1
    rows.append(("vector recurrence {times: n_vectors} (recomputed)",
                 f"{structure} (expected {SEX_DIV_VECTOR_STRUCTURE})",
                 "PASS" if ok else "**FAIL**"))

    # 3d. the paper must keep disclosing that the unit is the vector, not the run
    _rel, _needle = SEX_DIV_UNIT_PROSE
    ok = (REPO / _rel).read_text(encoding="utf-8").count(_needle) >= 1
    n_bad += 0 if ok else 1
    rows.append((f"`{_rel}` discloses the effective input sample",
                 f"`{_needle[:52]}...`",
                 "PASS" if ok else "**FAIL** (absent)"))

    # 4+. the regime-scoped prose that ties the totals to that denominator
    for rel, needle in SEX_DIV_CONTEXT:
        path = REPO / rel
        hits = path.read_text(encoding="utf-8").count(needle) if path.exists() else 0
        ok = hits >= 1
        n_bad += 0 if ok else 1
        rows.append((f"`{rel}`", f"`{needle[:52]}...`",
                     "PASS" if ok else "**FAIL** (absent)"))

    # No fold-change against a zero denominator, in any of the three documents.
    for rel in SEX_DIV_DOCS:
        text = (REPO / rel).read_text(encoding="utf-8")
        found = [lit for lit in SEX_DIV_FORBIDDEN if lit.lower() in text.lower()]
        match = SEX_DIV_FORBIDDEN_RE.search(text)
        if match:
            found.append(match.group(0)[:40])
        ok = not found
        n_bad += 0 if ok else 1
        rows.append((f"no male/female fold-change in `{rel}`",
                     "none" if ok else f"**{'; '.join(found)}**",
                     "PASS" if ok else "**FAIL**"))

    # Wasserstein: raw exceedance versus BH survival (added 2026-08-20).
    #
    # §2.5 used to say the distance "exceeds its permutation null on five". Five
    # is the BH-SURVIVOR count (anchored as T1.15); six comparisons clear the raw
    # null, and S2 SpO2 is the one the correction removes (p = 0.0215 against a
    # BH critical value of 0.0125 at rank 6). The sentence now reports both, so
    # both need re-measuring -- T1.15 only ever covered the five.
    #
    # The raw count is checked under BOTH readings of "exceeds its permutation
    # null", because the prose does not say which one it means: the empirical
    # p-value below 0.05, and the observed distance above the null's 95th
    # percentile. They agree at six here; if a future re-run made them disagree,
    # the sentence would become ambiguous and this guard should fail rather than
    # let one reading silently stand in for the other.
    raw_p = int((bh["p_value_empirical"] < 0.05).sum())
    raw_p95 = int((bh["wasserstein"] > bh["wasserstein_null_p95"]).sum())
    surviving = int(bh["bh_survives"].sum())

    ok = raw_p == WASSERSTEIN_RAW_EXCEEDANCES
    n_bad += 0 if ok else 1
    rows.append(("Wasserstein comparisons clearing the raw null (p < 0.05)",
                 f"{raw_p} (published {WASSERSTEIN_RAW_EXCEEDANCES})",
                 "PASS" if ok else "**FAIL**"))

    ok = raw_p95 == raw_p
    n_bad += 0 if ok else 1
    rows.append(("both readings of `exceeds its permutation null` agree",
                 f"p<0.05: {raw_p}; distance>null p95: {raw_p95}",
                 "PASS" if ok else "**FAIL**"))

    ok = surviving < raw_p
    n_bad += 0 if ok else 1
    rows.append(("BH correction removes at least one comparison",
                 f"{raw_p} raw -> {surviving} surviving",
                 "PASS" if ok else "**FAIL**"))

    # The survivors must be a strict subset of the raw exceedances. If BH ever
    # promoted a comparison that did not clear the raw null, the two numbers in
    # the sentence would no longer describe nested sets.
    survivor_rows = bh[bh["bh_survives"]]
    ok = bool((survivor_rows["p_value_empirical"] < 0.05).all())
    n_bad += 0 if ok else 1
    rows.append(("every BH survivor also clears the raw null (nested sets)",
                 "yes" if ok else "**no**",
                 "PASS" if ok else "**FAIL**"))

    # Name the dropped comparison, so a change of identity is visible and not
    # merely a change of count.
    dropped = bh[(bh["p_value_empirical"] < 0.05) & (~bh["bh_survives"])]
    got = sorted(f"{r.scenario} {r.output}" for r in dropped.itertuples())
    ok = got == list(WASSERSTEIN_DROPPED_BY_BH)
    n_bad += 0 if ok else 1
    rows.append(("the comparison BH removes is the expected one",
                 f"{got} (expected {list(WASSERSTEIN_DROPPED_BY_BH)})",
                 "PASS" if ok else "**FAIL**"))

    print("| check | observed | verdict |")
    print("|---|---|---|")
    for label, observed, verdict in rows:
        print(f"| {label} | {observed} | {verdict} |")
    print(
        f"\n**Sex-stratified divergence guard:** {len(rows)} checks, "
        f"{len(rows) - n_bad} PASS, {n_bad} FAIL.\n"
    )
    return n_bad


n_sexdiv_fail = check_sex_divergence()


# S011 sex-contrast guard (2026-08-16).
#
# The hole this closes. Supplement S9's practical-guidance passage carries five
# numbers from the S011 2x2 sex-by-mass design -- +13.7 and +21.3 mmHg (already
# there), and -1.97 mmHg, -3.8 % and +3.97 % (added the same day the passage was
# rebalanced to report the severe-ARDS arm). NONE of the five was anchored in the
# crosswalk or recomputed by any script: `grep 13.7 scripts/*.py` returned
# nothing. That is exactly the exposure the sex-divergence guard above exists to
# close, reproduced in the very commit that closed a dossier about verification
# discipline, and asymmetric besides -- the "8 distinct input vectors" introduced
# in the same work WAS guarded.
#
# What is recomputed, and from where. results/sex_vs_mass.parquet holds one row
# per run with PaO2_mean, sex and mass_kg. The guard subtracts F minus M itself,
# by column name, and derives the percentages as 100*(F-M)/M from those same two
# means. It deliberately does NOT read results/sex_vs_mass_decomposition.csv:
# that file is emitted by scripts/sex_vs_mass_check.py, the same producer, so
# checking against it would only confirm the script agrees with itself.
#
# Rows 1-2 are the two historically published figures and double as the positive
# witnesses: if the reconstruction is wrong, they break first, before any of the
# three new values is believed.
#
# Rows 6-8 pin the QUALIFICATIONS, not just the magnitudes. Removing "reverses
# direction", the diverged S4 female cell, or the scope sentence would leave
# every number exact while restoring precisely the one-sided reading the
# rebalancing removed. Row 6 pins the direction flip itself (F above M at S1,
# below at S4), so a sweep that changed sign without changing magnitude is caught.
#
# What this guard does NOT prove. It protects the S011 values and qualifications
# as currently known. It says nothing about whether they generalise beyond the
# single tested operating point (FiO2 = 0.6, midrange inputs), and nothing about
# any mechanism: Pulse's sex flag switches several subsystems at once, and the
# two bodies are not percentile-matched.
S011_SOURCE = "results/sex_vs_mass.parquet"
S011_IN_ENVELOPE_KG = 56.2
S011_OUT_ENVELOPE_KG = 67.3
# (scenario, mass_kg, decimals, expected F-M in mmHg)
S011_ABS_EXPECTED = [
    ("S1", 56.2, 1, 13.7),
    ("S1", 67.3, 1, 21.3),
    ("S4", 56.2, 2, -1.97),
]
# (scenario, mass_kg, decimals, expected 100*(F-M)/M)
S011_REL_EXPECTED = [
    ("S1", 56.2, 2, 3.97),
    ("S4", 56.2, 1, -3.8),
]
S011_DIVERGED_CELL = ("S4", 67.3)
S011_PROSE = [
    # "reverses direction" -> "reverses: female-minus-male" (2026-10-06, M. Sauthier
    # review); the qualification itself is unchanged.
    ("preprint_npj/supplement.tex", "comparison reverses: female-minus-male"),
    # Scenario relabelled S4 -> Severe (2026-10-06, M. Sauthier review).
    ("preprint_npj/supplement.tex", "diverged outright in Severe"),
    ("preprint_npj/supplement.tex",
     "scenario-dependent sensitivity to the sex-conditioned setup"),
]


def check_s011_sex_contrast() -> int:
    """Rebuild the S011 sex contrast from run means, and pin its qualifications."""
    print("\n## S011 sex-contrast guard\n")
    rows: list[tuple[str, str, str]] = []
    n_bad = 0
    d = pd.read_parquet(REPO / S011_SOURCE)

    def mean_for(scenario: str, sex: str, mass: float) -> float | None:
        sel = d[(d["scenario"] == scenario) & (d["sex"] == sex)
                & (d["mass_kg"] == mass)]
        if sel.empty:
            return None
        v = sel.iloc[0]["PaO2_mean"]
        return None if pd.isna(v) else float(v)

    # 1-3. absolute F - M, subtracted here rather than read from a derived field
    for scen, mass, dp, expected in S011_ABS_EXPECTED:
        f, m = mean_for(scen, "F", mass), mean_for(scen, "M", mass)
        obs = None if (f is None or m is None) else round(f - m, dp)
        ok = obs == expected
        n_bad += 0 if ok else 1
        rows.append((f"{scen} @ {mass} kg, F - M PaO2 (recomputed)",
                     f"{obs} (expected {expected})",
                     "PASS" if ok else "**FAIL**"))

    # 4-5. relative effect, derived from the same two means
    for scen, mass, dp, expected in S011_REL_EXPECTED:
        f, m = mean_for(scen, "F", mass), mean_for(scen, "M", mass)
        obs = None if (f is None or m is None or m == 0) else round(100 * (f - m) / m, dp)
        ok = obs == expected
        n_bad += 0 if ok else 1
        rows.append((f"{scen} @ {mass} kg, 100*(F-M)/M (recomputed)",
                     f"{obs} (expected {expected})",
                     "PASS" if ok else "**FAIL**"))

    # 6. the direction flip itself, independent of magnitude
    f1, m1 = mean_for("S1", "F", S011_IN_ENVELOPE_KG), mean_for("S1", "M", S011_IN_ENVELOPE_KG)
    f4, m4 = mean_for("S4", "F", S011_IN_ENVELOPE_KG), mean_for("S4", "M", S011_IN_ENVELOPE_KG)
    ok = None not in (f1, m1, f4, m4) and f1 > m1 and f4 < m4
    n_bad += 0 if ok else 1
    rows.append((f"sign flips between S1 and S4 at {S011_IN_ENVELOPE_KG} kg",
                 f"S1 F>M {f1 > m1}, S4 F<M {f4 < m4}",
                 "PASS" if ok else "**FAIL**"))

    # 7. the S4 2x2 is incomplete because the out-of-envelope female diverged
    scen, mass = S011_DIVERGED_CELL
    sel = d[(d["scenario"] == scen) & (d["sex"] == "F") & (d["mass_kg"] == mass)]
    ok = len(sel) == 1 and bool(sel.iloc[0]["diverged"])
    n_bad += 0 if ok else 1
    rows.append((f"{scen} @ {mass} kg female run diverged (S4 2x2 incomplete)",
                 f"diverged={bool(sel.iloc[0]['diverged']) if len(sel) == 1 else 'missing'}",
                 "PASS" if ok else "**FAIL**"))

    # 8-10. the qualifications that stop a one-sided reading
    for rel, needle in S011_PROSE:
        hits = (REPO / rel).read_text(encoding="utf-8").count(needle)
        ok = hits >= 1
        n_bad += 0 if ok else 1
        rows.append((f"`{rel}` keeps `{needle[:44]}`",
                     f"{hits} occurrence(s)",
                     "PASS" if ok else "**FAIL** (absent)"))

    print("| check | observed | verdict |")
    print("|---|---|---|")
    for label, observed, verdict in rows:
        print(f"| {label} | {observed} | {verdict} |")
    print(
        f"\n**S011 sex-contrast guard:** {len(rows)} checks, "
        f"{len(rows) - n_bad} PASS, {n_bad} FAIL.\n"
    )
    return n_bad


n_s011_fail = check_s011_sex_contrast()


# Setup-input instantiation (§2.1, §4.4, Discussion). Every number below is
# recomputed from the run-level long artefact, never hard-coded here: the
# expected values are the assertion, and the CSV is the measurement.
INST_SOURCE = "results/input_instantiation_long.csv"
INST_N_PARSED = 10_160
INST_N_NOT_REACHED = 80
INST_N_NOT_REACHED_RUNS = 20
INST_VENT_CONTRACTS = 4
# The design total, added to the paper on 2026-09-21 so the reader can close
# the arithmetic: 10,160 reached ingestion, 80 never did, and 8 contracts x
# 1,280 runs is where both come from. It is NOT a fourth independent figure --
# it is pinned here precisely because it must stay equal to 10,160 + 80, and a
# reader who finds it drifting from that sum has found a real defect.
INST_N_DESIGN = 10_240
# The prose these numbers live in. Pinned so a rewrite cannot quietly drop the
# scope that makes them true.
INST_LITERALS = [
    # Re-pinned 2026-10-06 (M. Sauthier review round): the contract gloss moved
    # into a parenthesis, and the design total into "80 of the 10,240 contracts".
    # "ventilator" was dropped in his version and restored by the author (D29):
    # the 80 are 20 runs x 4 ventilator contracts, the same runs' setup contracts
    # reached ingestion, so without the word a reader can count 20 x 8 = 160.
    # Never "the sweep submits 10,240": 80 of them were never offered to the engine.
    "found exact agreement for all 10{,}160 input contracts (one value submitted in one "
    "configuration block) that reached ingestion",
    "The remaining 80 of the 10{,}240 contracts are the ventilator contracts of the 20 runs "
    "that failed during patient stabilisation, before the ventilator action was submitted",
]


def check_input_instantiation() -> int:
    """Bind the H2 instantiation claims to the artefact they were measured on.

    The paper's strongest new statement is a NEGATIVE one -- no submitted input
    was altered at ingestion -- so the guard recomputes the zero rather than
    trusting it, and fails if any non-zero delta_setup ever appears.
    """
    print("\n## Setup-input instantiation guard\n")
    rows: list[tuple[str, str, str]] = []
    n_bad = 0

    def record(label: str, observed: object, expected: object) -> None:
        nonlocal n_bad
        ok = observed == expected
        n_bad += 0 if ok else 1
        rows.append((label, f"{observed} (expected {expected})",
                     "PASS" if ok else "**FAIL**"))

    long = pd.read_csv(REPO / INST_SOURCE)
    parsed = long[long["parse_status"] == "parsed"]
    unparsed = long[long["parse_status"] != "parsed"]

    record("contracts reaching ingestion (recomputed)",
           len(parsed), INST_N_PARSED)
    record("ventilator contracts NOT_REACHED (recomputed)",
           len(unparsed), INST_N_NOT_REACHED)
    record("distinct runs behind them (recomputed)",
           unparsed["run_id"].nunique(), INST_N_NOT_REACHED_RUNS)
    # Invariant: the 80 are 20 runs x the 4 ventilator contracts, nothing else.
    record("invariant 80 = 20 x 4",
           unparsed["run_id"].nunique() * INST_VENT_CONTRACTS,
           INST_N_NOT_REACHED)
    # The design total the paper now prints. Recomputed two independent ways:
    # from the artefact's own length, and as the sum the reader is invited to
    # make. Both must land on the same number, or the gloss is wrong.
    record("design total, from the artefact (recomputed)",
           len(long), INST_N_DESIGN)
    record("design total = ingested + never-reached",
           INST_N_PARSED + INST_N_NOT_REACHED, INST_N_DESIGN)
    record("every NOT_REACHED row is a ventilator contract",
           set(unparsed["source_block"]), {"vent"})
    record("every NOT_REACHED run diverged",
           bool(unparsed["diverged"].all()), True)
    # The load-bearing negative claim.
    record("non-zero delta_setup among ingested contracts",
           int((parsed["delta_setup_abs"] != 0).sum()), 0)

    paper_tex = (REPO / "preprint_npj" / "paper.tex").read_text(encoding="utf-8")
    for literal in INST_LITERALS:
        present = literal in paper_tex
        n_bad += 0 if present else 1
        rows.append((f"paper.tex: `{literal[:52]}...`",
                     "present" if present else "ABSENT",
                     "PASS" if present else "**FAIL**"))

    print("| check | observed | verdict |")
    print("|---|---|---|")
    for label, observed, verdict in rows:
        print(f"| {label} | {observed} | {verdict} |")
    print(
        f"\n**Setup-input instantiation guard:** {len(rows)} checks, "
        f"{len(rows) - n_bad} PASS, {n_bad} FAIL.\n"
    )
    return n_bad


n_inst_fail = check_input_instantiation()


# Per-cell retention of uncontaminated systolic elementary-effect pairs
# (Supplement S3.7). The pooled 68 / 19 was already anchored; what the pooled
# figure cannot show is that the systolic robustness checks rest on as few as
# four pairs in three of the eight cells, which is why S3.7 now publishes the
# breakdown and why this guard binds it to the run-level artefact.
CLIP_RETAINED_EXPECTED = {
    "S1_M": 4, "S1_F": 4, "S2_M": 7, "S2_F": 6,
    "S3_M": 10, "S3_F": 9, "S4_M": 4, "S4_F": 5,
}
CLIP_RETAINED_TOTAL = 49
# The caveat is the reason the numbers were published. Numbers alone would
# survive a rewrite that deleted it, so it is pinned too.
CLIP_RETENTION_CAVEAT = (
    # "therefore" dropped in the 2026-10-06 M. Sauthier review, and the cells
    # relabelled (S1_M -> Healthy-M ...) in the same round; caveat unchanged.
    "the systolic robustness checks below rest on as few as four "
    "elementary-effect pairs in Healthy-M, Healthy-F and Severe-M"
)


def check_clip_pair_retention() -> int:
    """Bind S3.7's per-cell uncontaminated-pair counts to the run-level data.

    Derived from ``_clip_percell``, which is built in the same loop that already
    produces the pooled 68 / 19 from ``data/runs/full_sweep/aggregated.parquet``
    -- deliberately NOT from ``results/s032/sbp_map_dominance.csv``, which is an
    output of the chain under audit.
    """
    print("\n## Clip pair-retention guard (Supplement S3.7)\n")
    rows: list[tuple[str, str, str]] = []
    n_bad = 0

    def record(label: str, observed: object, expected: object) -> None:
        nonlocal n_bad
        ok = observed == expected
        n_bad += 0 if ok else 1
        rows.append((label, f"{observed} (expected {expected})",
                     "PASS" if ok else "**FAIL**"))

    for cell, expected in CLIP_RETAINED_EXPECTED.items():
        record(f"{cell} uncontaminated systolic pairs",
               _clip_percell.get(cell, {}).get("retained"), expected)

    total = sum(v["retained"] for v in _clip_percell.values())
    record("total retained across the eight cells", total, CLIP_RETAINED_TOTAL)
    # 49 = 68 - 19, re-derived rather than restated: the guard fails if the
    # breakdown ever stops reconciling with the two anchored pooled figures.
    record("invariant retained = clean - contaminated", total, _cs - _css)

    supp = (REPO / "preprint_npj" / "supplement.tex").read_text(encoding="utf-8")
    present = CLIP_RETENTION_CAVEAT in supp
    n_bad += 0 if present else 1
    rows.append(("supplement.tex: the `as few as four` caveat",
                 "present" if present else "ABSENT",
                 "PASS" if present else "**FAIL**"))

    print("| check | observed | verdict |")
    print("|---|---|---|")
    for label, observed, verdict in rows:
        print(f"| {label} | {observed} | {verdict} |")
    print(
        f"\n**Clip pair-retention guard:** {len(rows)} checks, "
        f"{len(rows) - n_bad} PASS, {n_bad} FAIL.\n"
    )
    return n_bad


S030_PROV_SOURCE = "results/s030_published_value_provenance.csv"
S030_PROV_TOLERANCE = 0.05

# Companion anchors, transcribed in audit/S030_recalibration_plan.md, behind the
# two published tolerance bounds. They are the ORIGINAL March 2026 28-run
# calibration (Pulse_translation_new/experiments_log.md), not E6: the April E6
# refinement gave 251.9 / 148.2 / 74.8 at 0.26 / 0.60 / 0.95. Attribution
# corrected 2026-09-14 (audit/number_inventory.md section 4.1, F-S1).
S030_COMPANION_PF = {0.26: 256.0, 0.30: 199.3, 0.60: 150.1, 0.90: 118.7, 0.95: 96.1}

# (arm, severity, window, column, published literal, phrase pinned in
# supplement.tex or None). The phrase, not the bare number, is what is looked
# for: "87.3" also occurs elsewhere in the supplement, so a bare-literal check
# would survive an edit that changed this sentence's value.
S030_PUBLISHED: list[tuple[str, float, str, str, float, str | None]] = [
    ("free", 0.26, "calibration_108_168", "pf_mmhg", 256.5, "0.26 $\\to$ 256.5"),
    ("free", 0.60, "calibration_108_168", "pf_mmhg", 150.5, "0.60 $\\to$ 150.5"),
    ("free", 0.95, "calibration_108_168", "pf_mmhg", 96.6, "0.95 $\\to$ 96.6~mmHg"),
    ("free", 0.30, "calibration_108_168", "pf_mmhg", 199.8, None),
    ("free", 0.90, "calibration_108_168", "pf_mmhg", 121.0, None),
    ("free", 0.95, "atlas_60_120", "alveolar_po2_mmhg", 231.3,
     "(231.3 to 230.7~mmHg)"),
    ("free", 0.95, "late_240_300", "alveolar_po2_mmhg", 230.7,
     "(231.3 to 230.7~mmHg)"),
    ("free", 0.95, "atlas_60_120", "aa_gradient_mmhg", 196.4,
     "narrows from 196.4 to 185.7~mmHg"),
    ("free", 0.95, "late_240_300", "aa_gradient_mmhg", 185.7,
     "narrows from 196.4 to 185.7~mmHg"),
    ("locked", 0.95, "late_240_300", "aa_gradient_mmhg", 185.1,
     "(185.7 versus 185.1~mmHg)"),
    ("free", 0.95, "atlas_60_120", "pf_mmhg", 87.3,
     "P/F is 87.3~mmHg over the atlas window"),
    ("free", 0.95, "late_240_300", "pf_mmhg", 112.6,
     "and 112.6~mmHg over [240, 300]~s"),
    ("locked", 0.95, "atlas_60_120", "pf_mmhg", 69.4, "(87.3 and 69.4~mmHg)"),
    ("locked", 0.95, "late_240_300", "pf_mmhg", 91.5, "lowers P/F to 91.5~mmHg"),
]


def check_s030_provenance() -> int:
    """Bind Supplement S5's S030 literals to a re-derived artefact.

    Three of those values -- the P/F at the companion's [108, 168] s window --
    and the whole alveolar chain existed in no committed artefact until
    ``scripts/audit_s030_provenance.py`` was written: they had been computed ad
    hoc and recorded in a register only. This guard reads the artefact that
    script writes, so the published numbers stay tied to something.

    Availability, stated rather than skipped: the artefact is committed, so this
    guard is live on every clone. The raw runs it derives from
    (``data/runs/s030_ards_berlin_recalibration``) are gitignored, so on a clone
    without them nothing re-checks the artefact against the runs. There is no
    SKIP path here -- a missing artefact is a FAIL, never a pass.
    """
    print("\n## S030 published-value provenance guard (Supplement S5)\n")
    rows: list[tuple[str, str, str]] = []
    n_bad = 0

    def record(label: str, observed: object, ok: bool) -> None:
        nonlocal n_bad
        n_bad += 0 if ok else 1
        rows.append((label, str(observed), "PASS" if ok else "**FAIL**"))

    path = REPO / S030_PROV_SOURCE
    if not path.is_file():
        record(f"artefact {S030_PROV_SOURCE}", "ABSENT", False)
        print("| check | observed | verdict |")
        print("|---|---|---|")
        for label, observed, verdict in rows:
            print(f"| {label} | {observed} | {verdict} |")
        print("\n**S030 provenance guard:** 1 check, 0 PASS, 1 FAIL.\n")
        return n_bad

    prov = pd.read_csv(path)
    record("artefact rows (2 arms x 5 fractions x 3 windows)", len(prov), len(prov) == 30)

    supp = (REPO / "preprint_npj" / "supplement.tex").read_text(encoding="utf-8")

    def cell(arm: str, sev: float, window: str) -> pd.Series | None:
        sel = prov[(prov["arm"] == arm) & (prov["severity"] == sev)
                   & (prov["window"] == window)]
        return sel.iloc[0] if len(sel) == 1 else None

    for arm, sev, window, col, published, phrase in S030_PUBLISHED:
        row = cell(arm, sev, window)
        if row is None:
            record(f"{arm} {sev} {window} row", "MISSING", False)
            continue
        got = float(row[col])
        ok = abs(got - published) <= S030_PROV_TOLERANCE and round(got, 1) == published
        record(f"{arm} {sev} {window} {col} = {published}", f"{got:.4f}", ok)
        if phrase is not None:
            record(f"supplement.tex carries `{phrase}`",
                   "present" if phrase in supp else "ABSENT", phrase in supp)

    # The effective window is part of the result. Since 2026-08-13 S030 uses the
    # atlas rule (src/detector.py::_steady_state_window, 1e-6 slack), which
    # admits the drifted endpoints: 13 samples on the two windows whose bounds
    # sit on the 5 s grid, 12 on [108, 168] whose bounds do not. Reverting to
    # the slack-free comparison shifts P/F by ~0.5 mmHg and must fail here.
    for arm, sev, window, expected_n in (("free", 0.95, "atlas_60_120", 13),
                                         ("free", 0.95, "calibration_108_168", 12),
                                         ("free", 0.95, "late_240_300", 13)):
        row = cell(arm, sev, window)
        n = None if row is None else int(row["n_samples"])
        record(f"{window}: samples entering the mean", n, n == expected_n)

    def pct(sev: float) -> float:
        row = cell("free", sev, "calibration_108_168")
        return 100.0 * (float(row["pf_mmhg"]) - S030_COMPANION_PF[sev]) / S030_COMPANION_PF[sev]

    three = max(abs(pct(s)) for s in (0.26, 0.60, 0.95))
    five = max(abs(pct(s)) for s in S030_COMPANION_PF)
    record("max deviation on the three published fractions <= 0.6 %",
           f"{three:.3f} %", three <= 0.6)
    record("max deviation across all five fractions <= 2 %", f"{five:.3f} %", five <= 2.0)
    for phrase in ("within 0.6~\\%", "within 2~\\%"):
        record(f"supplement.tex carries `{phrase}`",
               "present" if phrase in supp else "ABSENT", phrase in supp)

    print("| check | observed | verdict |")
    print("|---|---|---|")
    for label, observed, verdict in rows:
        print(f"| {label} | {observed} | {verdict} |")
    print(
        f"\n**S030 provenance guard:** {len(rows)} checks, "
        f"{len(rows) - n_bad} PASS, {n_bad} FAIL.\n"
    )
    return n_bad


FIO2_ADJ_SOURCE = "results/fio2_adjustment_provenance.csv"

# Phrases, not bare numbers: "195" occurs 2/3/9 times across the three
# documents, so a literal check would survive an edit to the sentence that
# carries the finding. Matched against whitespace-normalised text, because the
# monograph is hard-wrapped and every one of these phrases spans a line break
# there.
FIO2_ADJ_PHRASES: list[tuple[str, str]] = [
    # Paper and supplement literals re-registered 2026-10-06 (M. Sauthier
    # review): the 195-run scope, the logged error, the 208/195 split and the
    # 0.04 % size are all still stated, in condensed wording.
    ("preprint_npj/paper.tex", "caps the inspired oxygen fraction at 0.9996"),
    ("preprint_npj/paper.tex", "ventilator action was reached (195 runs)"),
    ("preprint_npj/paper.tex", "at 0.9996 and logs an error"),
    ("preprint_npj/supplement.tex",
     "Of the 208 runs requesting FiO$_2$ = 1.0, 195 reach the ventilator action"),
    ("preprint_npj/supplement.tex", "The adjustment (0.04~\\% in relative terms)"),
    ("preprint_npj/supplement.tex", "from 663.0 to 662.7~mmHg"),
    ("preprint/manuscript.md",
     "208 runs request FiO2 = 1.0; **195 reach the ventilator action and "
     "all 195 are adjusted**"),
    ("preprint/manuscript.md", "from 663.0 to 662.7 mmHg"),
]


def check_fio2_adjustment() -> int:
    """Bind the FiO2 downstream-adjustment figures to a re-derived artefact.

    195 / 208 / 13 / 0.9996 / 0.04 % entered three documents on 2026-08-13 from
    shell one-liners over gitignored logs. ``scripts/audit_fio2_adjustment.py``
    recomputes them into the committed artefact this guard reads. The two
    negative facts are recomputed too, not restated: that no run requesting less
    than FiO2 = 1.0 is ever adjusted, and that the 13 unadjusted runs at 1.0 are
    unadjusted because they never reach the ventilator action -- they are not
    exceptions to the mechanism, which is what the documents claim.

    A missing artefact is a FAIL, never a skip.
    """
    print("\n## FiO2 downstream-adjustment guard (paper §2.1, Supplement S3.3, monograph §3.4)\n")
    rows: list[tuple[str, str, str]] = []
    n_bad = 0

    def record(label: str, observed: object, ok: bool) -> None:
        nonlocal n_bad
        n_bad += 0 if ok else 1
        rows.append((label, str(observed), "PASS" if ok else "**FAIL**"))

    path = REPO / FIO2_ADJ_SOURCE
    if not path.is_file():
        record(f"artefact {FIO2_ADJ_SOURCE}", "ABSENT", False)
        print("| check | observed | verdict |")
        print("|---|---|---|")
        for label, observed, verdict in rows:
            print(f"| {label} | {observed} | {verdict} |")
        print("\n**FiO2 adjustment guard:** 1 check, 0 PASS, 1 FAIL.\n")
        return n_bad

    df = pd.read_csv(path)
    record("artefact rows (the full sweep)", len(df), len(df) == 1280)

    at_one = df[df["requested_fio2"] == 1.0]
    adjusted = df[df["adjusted"]]
    missed = at_one[~at_one["adjusted"]]

    record("runs requesting FiO2 = 1.0", len(at_one), len(at_one) == 208)
    record("of those, adjusted", len(adjusted), len(adjusted) == 195)
    record("of those, unadjusted", len(missed), len(missed) == 13)
    record("every unadjusted one never reached the ventilator action",
           bool((~missed["action_reached"]).all()), bool((~missed["action_reached"]).all()))
    n_below = int((df["adjusted"] & (df["requested_fio2"] < 1.0)).sum())
    record("runs below FiO2 = 1.0 that were adjusted", n_below, n_below == 0)

    values = sorted(adjusted["adjusted_fio2"].dropna().unique())
    record("distinct substituted values", values, len(values) == 1 and values[0] == 0.9996)

    # The three derived checks below must exist whatever the artefact says: a
    # guard whose check count shrinks when the data degrade is a guard that
    # turns a defect into a silence. When the substituted value is not unique
    # they FAIL rather than disappear.
    single = values[0] if len(values) == 1 else None
    pct = 100.0 * (1.0 - single) if single is not None else None
    record("relative adjustment (%)",
           "n/a (value not unique)" if pct is None else f"{pct:.4f}",
           pct is not None and round(pct, 2) == 0.04)
    # Alveolar ceiling re-derived, not restated: FiO2*(760-47) - 40/0.8.
    ceil_one = 1.0 * (760.0 - 47.0) - 40.0 / 0.8
    ceil_adj = single * (760.0 - 47.0) - 40.0 / 0.8 if single is not None else None
    record("alveolar ceiling at FiO2 = 1.0", f"{ceil_one:.2f}", round(ceil_one, 1) == 663.0)
    record("alveolar ceiling at the substituted value",
           "n/a (value not unique)" if ceil_adj is None else f"{ceil_adj:.2f}",
           ceil_adj is not None and round(ceil_adj, 1) == 662.7)

    for rel, phrase in FIO2_ADJ_PHRASES:
        text = " ".join((REPO / rel).read_text(encoding="utf-8").split())
        present = phrase in text
        record(f"{rel} carries `{phrase[:52]}...`", "present" if present else "ABSENT", present)

    print("| check | observed | verdict |")
    print("|---|---|---|")
    for label, observed, verdict in rows:
        print(f"| {label} | {observed} | {verdict} |")
    print(
        f"\n**FiO2 adjustment guard:** {len(rows)} checks, "
        f"{len(rows) - n_bad} PASS, {n_bad} FAIL.\n"
    )
    return n_bad


FIGURE_DIRS = ("figures", "preprint_npj/figures")

# Tracked figure PDFs that legitimately carry a wall-clock timestamp, each with
# the reason. An entry that stops being needed is reported: a stale exception is
# how a real defect hides.
# Emptied 2026-08-16. The single entry, fig_s2_spearman.pdf, was exempted on the
# stated ground of "no generator anywhere in the repo
# (scripts/verify.py::MISSING_GENERATORS)". That ground was false: the figure is
# written by scripts/make_figures.py::fig_h4_spearman() under the name
# figures/fig05_h4_spearman_mu_star.pdf, which commit b3caa1c established on
# 2026-07-28. The exemption therefore rested on a premise this guard never
# re-checked, because the premise lived in another file -- and by suppressing the
# timestamp check it hid the very drift it should have caught, when 94d19c2
# rewrote the tracked figures under SOURCE_DATE_EPOCH and left the npj copy on
# its old wall-clock stamp. Exactly what the note above warns about: a stale
# exception is how a real defect hides. verify.py now propagates the generated
# file, so the figure carries the pinned epoch like every other.
FIGURE_TIMESTAMP_EXCEPTIONS: dict[str, str] = {}


def check_figure_timestamps() -> int:
    """Every regenerable tracked figure PDF must carry the pinned epoch.

    ``scripts/verify.py`` regenerates the tracked figures under a fixed
    ``SOURCE_DATE_EPOCH`` so their bytes are stable. A figure committed from a
    manual run instead embeds a wall-clock ``/CreationDate``, which no amount of
    re-running can reproduce, and the gate then reports a dirty tree on a file
    nobody edited. That happened on 2026-08-06 (fixed in ``63b99da``) and again
    on 2026-08-12 (``4e6c0b0``), because nothing checked it. This does.

    The expected timestamp is *derived* from ``verify.py``'s own constant, read
    out of its source, so the two cannot drift apart.
    """
    print("\n## Figure timestamp guard (pinned SOURCE_DATE_EPOCH)\n")
    rows: list[tuple[str, str, str]] = []
    n_bad = 0

    def record(label: str, observed: object, ok: bool) -> None:
        nonlocal n_bad
        n_bad += 0 if ok else 1
        rows.append((label, str(observed), "PASS" if ok else "**FAIL**"))

    verify_src = (REPO / "scripts" / "verify.py").read_text(encoding="utf-8")
    m = re.search(r'^REPRODUCIBLE_EPOCH\s*=\s*"(\d+)"', verify_src, re.M)
    if m is None:
        record("REPRODUCIBLE_EPOCH readable from scripts/verify.py", "NOT FOUND", False)
        print("| check | observed | verdict |")
        print("|---|---|---|")
        for label, observed, verdict in rows:
            print(f"| {label} | {observed} | {verdict} |")
        print("\n**Figure timestamp guard:** 1 check, 0 PASS, 1 FAIL.\n")
        return n_bad

    epoch = int(m.group(1))
    expected = datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("D:%Y%m%d%H%M%SZ")
    record(f"pinned epoch read from verify.py ({epoch})", expected, True)

    date_re = re.compile(rb"/CreationDate\s*\(([^)]*)\)")
    seen_exceptions: set[str] = set()
    n_pdfs = 0
    for d in FIGURE_DIRS:
        for pdf in sorted((REPO / d).glob("*.pdf")):
            n_pdfs += 1
            raw = pdf.read_bytes()
            found = date_re.search(raw)
            stamp = found.group(1).decode("latin-1") if found else None
            name = pdf.name
            if name in FIGURE_TIMESTAMP_EXCEPTIONS:
                seen_exceptions.add(name)
                # A stale exception is a defect of its own: report it.
                ok = stamp is None or stamp != expected
                record(f"{d}/{name} (documented exception)",
                       f"{stamp} -- {FIGURE_TIMESTAMP_EXCEPTIONS[name]}"
                       if ok else f"{stamp} -- now pinned, exception is obsolete",
                       ok)
                continue
            record(f"{d}/{name}", stamp if stamp else "no /CreationDate",
                   stamp == expected)

    record("tracked figure PDFs examined", n_pdfs, n_pdfs > 0)
    missing = set(FIGURE_TIMESTAMP_EXCEPTIONS) - seen_exceptions
    record("every documented exception still exists on disk",
           sorted(missing) if missing else "yes", not missing)

    print("| check | observed | verdict |")
    print("|---|---|---|")
    for label, observed, verdict in rows:
        print(f"| {label} | {observed} | {verdict} |")
    print(
        f"\n**Figure timestamp guard:** {len(rows)} checks, "
        f"{len(rows) - n_bad} PASS, {n_bad} FAIL.\n"
    )
    return n_bad


# ---------------------------------------------------------------------------
# Sobol framing guard.
#
# Until 2026-08-14 the paper closed the preregistered Sobol bolt-on with the
# parenthesis "no cell cleared its promotion trigger once sampling uncertainty
# was accounted for", and the monograph concluded S3.3.1 "closed by
# redundancy, not by compute-shortage". Both restated a reading of the
# preregistered trigger -- the dominant input alone -- that S031 withdrew in
# favour of the top-three rule the preregistration actually states. Under that
# rule 23 of the 144 top-three inputs clear the threshold in every bootstrap
# draw, spanning 17 of the 48 combinations, and the bolt-on was deferred on
# compute budget (6,144 runs under the preregistered 64x(2k+2) formula, or
# 3,584 for S1/ST alone, against a preregistered envelope of 1,500), not on an
# absence of non-linearity to decompose. The earlier 11,008 figure billed one
# sample per cell x output combination; it was withdrawn because every output
# of a cell comes from the same Pulse run and shares one sample.
#
# Nothing measured that prose. It carries no numeral, and the ledger anchors
# literals, so the wording survived six weeks in the paper and seven passages
# in the monograph -- including two sitting directly against the retraction
# that had already withdrawn them. This guard is the instrument that was
# missing.
#
# Scope is the three publishable documents only. Experiment logs and audit
# registers must stay free to quote the withdrawn wording; recording what was
# believed when is their job, so they are deliberately not scanned. For the
# same reason the phrases below are specific claim-shapes rather than broad
# motifs: "zero of the 48" is not among them, because a future retraction may
# legitimately need to name the number it retracts. The monograph's own
# retraction says "zero cells are CI-robustly non-linear under either
# formula", and no phrase here matches it.
#
# Calibration, recorded because a guard that cannot fail is not a guard. Every
# phrase was checked to match a real defective revision and to be absent from
# the corrected tree. Re-run it with:
#   git grep -c -F "<phrase>" <rev> -- <the three documents>
# ---------------------------------------------------------------------------
SOBOL_FRAMING_DOCS = (
    "preprint_npj/paper.tex",
    "preprint_npj/supplement.tex",
    "preprint/manuscript.md",
    # The bolt-on script ships under Apache-2.0, so its docstring is published
    # too, and it carried the same withdrawn thesis as the three documents.
    "scripts/s019_sobol_bolton.py",
    # The README is clean of this thesis today and never carried it. It is
    # covered anyway because it is the repository's most public living surface,
    # and it has a precedent: a retracted S018 figure survived there for seven
    # weeks because no layer re-measured it.
    "README.md",
)

# Withdrawn wording, each with the revision it was last verified to match.
SOBOL_RETIRED_PHRASES: tuple[tuple[str, str], ...] = (
    ("no cell cleared its promotion trigger", "d953d3d"),
    ("satisfy the trigger CI-robustly", "d953d3d"),
    ("statistically redundant", "d953d3d"),
    ("closed by redundancy", "d953d3d"),
    ("closed-by-redundancy", "d953d3d"),
    ("closes it by redundancy", "d953d3d"),
    ("adds no evidential weight", "d953d3d"),
    ("would re-derive the same ordering", "d953d3d"),
    # The June ancestor of the same thesis, removed by 91d705d on 2026-08-02.
    ("evidential redundancy", "bbd2cbf"),
    # scripts/s019_sobol_bolton.py is a restricted demonstrator built on the
    # withdrawn dominant-input reading: 6 cells, all 7 inputs, base sample 256,
    # first-order only, 13,824 runs. The preregistered design is 8 firing
    # cells, promoted inputs, base sample 64, 6,144 runs. Calling the script
    # "ready-to-fire" made the paper's cost argument read as its cost. If a
    # conforming implementation is ever written, this guard must fail once and
    # be revisited deliberately -- which is the point.
    ("ready-to-fire", "1c3f9b4"),
)

# The framing that replaced it. A guard that only forbids is satisfied by
# deleting the passage, so each document must still carry the current reason.
SOBOL_REQUIRED_PHRASES: tuple[tuple[str, str], ...] = (
    ("preprint_npj/paper.tex",
     "the triggered design exceeded its locked compute budget"),
    ("preprint_npj/supplement.tex", "reported rather than executed"),
    ("preprint/manuscript.md", "reported rather than executed"),
    # Added 2026-09-16. "Sobol" first reaches a paper reader in 2.6, and the
    # 2026-09-02 compression removed the gloss that stood there, leaving the
    # term of art undefined in the main text -- "variance" then occurred zero
    # times in paper.tex. The wording restored is the pre-compression one, not
    # a new composition. Re-pinned 2026-10-06: the M. Sauthier review round
    # dropped "individual"; the gloss itself is unchanged.
    ("preprint_npj/paper.tex",
     "apportions output variance among inputs and their interactions"),
)


def check_sobol_framing() -> int:
    """Forbid the withdrawn Sobol-redundancy thesis in the publishable set.

    Two directions, because either failure mode reintroduces the defect: a
    retired phrase coming back, or the replacement framing disappearing.

    A missing document is a FAIL, never a skip.
    """
    print("\n## Sobol framing guard "
          "(paper 2.1/2.2, Supplement S3.4, monograph 3.3.1)\n")
    rows: list[tuple[str, str, str]] = []
    n_bad = 0

    def record(label: str, observed: object, ok: bool) -> None:
        nonlocal n_bad
        n_bad += 0 if ok else 1
        rows.append((label, str(observed), "PASS" if ok else "**FAIL**"))

    # Whitespace-normalised before matching: the monograph hard-wraps its
    # prose, so several of these phrases spanned a line break in the very
    # revisions that motivated the guard. A raw line scan would have missed
    # them.
    texts: dict[str, str | None] = {}
    for rel in SOBOL_FRAMING_DOCS:
        path = REPO / rel
        if not path.is_file():
            texts[rel] = None
            record(f"document {rel}", "ABSENT", False)
        else:
            texts[rel] = " ".join(path.read_text(encoding="utf-8").split())

    for phrase, calibrated_at in SOBOL_RETIRED_PHRASES:
        hits = [rel for rel, t in texts.items() if t is not None and phrase in t]
        record(f"withdrawn `{phrase}` (matched at {calibrated_at})",
               ", ".join(hits) if hits else "absent from all three",
               not hits)

    for rel, phrase in SOBOL_REQUIRED_PHRASES:
        text = texts.get(rel)
        present = text is not None and phrase in text
        record(f"{rel} still states `{phrase[:44]}`",
               "present" if present else "ABSENT", present)

    print("| check | observed | verdict |")
    print("|---|---|---|")
    for label, observed, verdict in rows:
        print(f"| {label} | {observed} | {verdict} |")
    print(
        f"\n**Sobol framing guard:** {len(rows)} checks, "
        f"{len(rows) - n_bad} PASS, {n_bad} FAIL.\n"
    )
    return n_bad


n_cliprt_fail = check_clip_pair_retention()

n_s030prov_fail = check_s030_provenance()

n_figts_fail = check_figure_timestamps()

n_fio2adj_fail = check_fio2_adjustment()

n_readme_fail = check_readme_science(claims)

n_legend_fail = check_legend_lengths()


# Abstract extent guard (2026-08-16).
#
# The hole this closes. npj allows "up to 150 words" for the abstract. The
# count sat at exactly 150 for two weeks with zero margin, and NOTHING
# re-measured it: audit/npj_format_compliance.md N-2 was the only record, and a
# register is a dated observation, not an invariant. Two hyphenations in bc01969
# brought it to 148; without a guard, the next edit could cross 150 silently and
# the register would still read 148.
#
# WHAT IS PINNED IS THE LIMIT, NOT THE COUNT. Freezing 148 would be the wrong
# invariant twice over: a legitimate rewrite landing on 149 or 150 is compliant
# and would break the guard for nothing, and the count is an observed state that
# belongs in the register, not in a script. So the guard reports both counts and
# fails only above 150.
#
# The counting convention is the one N-2 has used throughout: whitespace-
# delimited tokens, as a word processor reports them, with a hyphenated compound
# counting as ONE word -- the register records `blood-` + `volume` across a line
# break as one word. The strict count (tokens bearing a letter or digit) is
# reported alongside because the convention is genuinely ambiguous, exactly as
# the legend guard above reports two counts for the same reason.
#
# Rows 1-2 are soundness witnesses, deliberately written as invariants rather
# than as pins on the current text: a renderer that leaves LaTeX behind, or that
# mangles a macro into a multi-character token, inflates the count silently and
# in the SAFE-LOOKING direction. They stay true under any rewording.
#
# WHAT THIS GUARD DOES NOT PROVE. It measures the repository's convention. npj's
# own counting method has never been verified at source, so a PASS here is not a
# guarantee about what the submission portal will report.
ABSTRACT_WORD_CAP = 150


def check_abstract_extent() -> int:
    """Bound the abstract at npj's cap under the register's counting convention."""
    print("\n## Abstract extent guard\n")
    rows: list[tuple[str, str, str]] = []
    n_bad = 0
    src = (REPO / "preprint_npj/paper.tex").read_text(encoding="utf-8")

    start = re.search(r"\\abstract\{", src)
    depth, i, out = 1, start.end(), []
    while depth:
        c = src[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                break
        out.append(c)
        i += 1
    body = "".join(out)

    t = body.replace("~", " ").replace("{,}", ",")
    t = re.sub(r"\$([^$]*)\$", r"\1", t)
    t = t.replace("\\%", "%").replace("\\,", " ")
    t = re.sub(r"\\text[a-z]*\{([^}]*)\}", r"\1", t)
    t = re.sub(r"_\{?(\d)\}?", r"\1", t)
    t = re.sub(r"\\[a-zA-Z]+", "", t)
    t = t.replace("{", "").replace("}", "")
    toks = t.split()
    strict = [w for w in toks if re.search(r"[A-Za-z0-9]", w)]
    symbols = [w for w in toks if w not in strict]

    # 1. the renderer left no LaTeX behind (invariant under rewording)
    residue = [w for w in toks if any(ch in w for ch in "\\{}$")]
    ok = not residue
    n_bad += 0 if ok else 1
    rows.append(("no LaTeX residue among the counted tokens",
                 "none" if ok else f"**{residue[:4]}**",
                 "PASS" if ok else "**FAIL**"))

    # 2. every non-alphanumeric token is a lone symbol, not a mangled macro
    fat = [w for w in symbols if len(w) > 2]
    ok = not fat
    n_bad += 0 if ok else 1
    rows.append(("non-alphanumeric tokens are lone symbols",
                 f"{symbols} " + ("" if ok else f"**oversized: {fat}**"),
                 "PASS" if ok else "**FAIL**"))

    # 3. THE INVARIANT: at or under npj's cap, word-processor reading
    ok = len(toks) <= ABSTRACT_WORD_CAP
    n_bad += 0 if ok else 1
    rows.append((f"word-processor count <= {ABSTRACT_WORD_CAP} (npj cap)",
                 f"{len(toks)}",
                 "PASS" if ok else "**FAIL**"))

    # 4. the strict reading, judged on its own terms. Written as its own
    # conjunction rather than reusing row 3's, so that each row fails only for
    # the reason its label states: an over-length abstract must trip row 3 alone,
    # not drag row 3's verdict into a row whose own condition still holds.
    ok = len(strict) <= len(toks) and len(strict) <= ABSTRACT_WORD_CAP
    n_bad += 0 if ok else 1
    rows.append(("strict count (letter/digit tokens), also under the cap",
                 f"{len(strict)}",
                 "PASS" if ok else "**FAIL**"))

    print("| check | observed | verdict |")
    print("|---|---|---|")
    for label, observed, verdict in rows:
        print(f"| {label} | {observed} | {verdict} |")
    print(
        f"\n**Abstract extent guard:** {len(rows)} checks, "
        f"{len(rows) - n_bad} PASS, {n_bad} FAIL. "
        f"Counts are reported, not pinned; only the {ABSTRACT_WORD_CAP}-word cap "
        f"is an invariant.\n"
    )
    return n_bad


# -----------------------------------------------------------------------------
# Vt-CV scenario split (2026-08-19).
#
# Section 2.2 quotes two per-scenario counts that no ledger anchor covers:
# "In S1 the delivered-Vt coefficient of variation exceeds the 0.05 threshold on
# 139 of 320 runs ... In S3 the same three figures are 36 of 320 runs".
#
# The sweep-wide count IS anchored (T1.30n.vt_cv = 303), but a total cannot tell
# a right split from a wrong one: 139 + 36 and 120 + 55 are equally consistent
# with 303. Both literals also appear in supplement.tex, so a drift would have to
# be noticed in two documents at once.
#
# Written as a guard rather than two more ledger anchors, on the author's ruling:
# the ledger audits the monograph, and these two numbers live only in the paper
# and its supplement.
# -----------------------------------------------------------------------------
VTCV_THRESHOLD = 0.05
S014_PAIRED_DROP = 0.326
S014_GATE = 0.04
VTCV_SCENARIO_SPLIT = {"S1": 139, "S3": 36}
VTCV_RUNS_PER_SCENARIO = 320
VTCV_TEXT_LOCI = (
    ("preprint_npj/paper.tex", "exceeds the 0.05 threshold on 139 of 320 runs"),
    ("preprint_npj/supplement.tex", "above 0.05 on 139 of 320 runs, versus 36 of 320 in Moderate"),
)
# The same sentence pairs each run count with how many of the 8 delivered-Vt
# entries of the stable non-linear set fall in that scenario. Those two figures
# had no anchor and were printed under a wrong label ("no Vt combination is
# estimable ... 3 estimable combinations in S3") until the number audit of
# 2026-09-13 (audit/number_inventory.md section 3.2). "Stable" means the lower
# bound clears 0.6 under each of the five seeds: nonlinear_all_seeds.
VTCV_STABLE_VT_SPLIT = {"S1": 0, "S3": 3}
VTCV_STABLE_VT_TEXT = (
    "preprint_npj/paper.tex",
    # Scenario labels S1/S3 -> Healthy/Moderate since 2026-10-06 (M. Sauthier review).
    "none of the 8 falls there, whereas in the Moderate scenario it does so on 36 of 320 runs "
    "and 3 of the 8 fall there",
)


def check_vtcv_scenario_split() -> int:
    """Re-derive Section 2.2's per-scenario Vt-CV exceedance counts."""
    print("\n## Vt-CV scenario-split guard\n")
    rows: list[tuple[str, str, str]] = []
    n_bad = 0

    # 0. Resolve the columns by NAME. A silent upstream rename would otherwise
    # make every check below vacuous instead of failing.
    missing = [c for c in ("scenario", "Vt_cv") if c not in agg.columns]
    ok = not missing
    n_bad += 0 if ok else 1
    rows.append(("columns resolve by name (scenario, Vt_cv)",
                 "both present" if ok else f"**absent: {missing}**",
                 "PASS" if ok else "**FAIL**"))

    if ok:
        exceed = agg["Vt_cv"] > VTCV_THRESHOLD

        # 1. POSITIVE CALIBRATION: the denominator the text quotes must be real.
        for sc in VTCV_SCENARIO_SPLIT:
            n_runs = int((agg["scenario"] == sc).sum())
            good = n_runs == VTCV_RUNS_PER_SCENARIO
            n_bad += 0 if good else 1
            rows.append((f"{sc} holds {VTCV_RUNS_PER_SCENARIO} runs (the quoted denominator)",
                         f"{n_runs}", "PASS" if good else "**FAIL**"))

        # 2. THE INVARIANT: each quoted numerator, re-derived from the parquet.
        for sc, published in VTCV_SCENARIO_SPLIT.items():
            got = int((exceed & (agg["scenario"] == sc)).sum())
            good = got == published
            n_bad += 0 if good else 1
            rows.append((f"{sc}: runs with Vt CV > {VTCV_THRESHOLD}",
                         f"{got} (published {published})",
                         "PASS" if good else "**FAIL**"))

        # 3. The split must sit inside the anchored sweep-wide count.
        total = int(exceed.sum())
        quoted = sum(VTCV_SCENARIO_SPLIT.values())
        good = quoted <= total
        n_bad += 0 if good else 1
        rows.append(("quoted split fits inside the sweep-wide Vt-CV count",
                     f"{quoted} of {total}", "PASS" if good else "**FAIL**"))

        # 3b. DIAGNOSTIC, reported and not pinned. Section 2.3 states that the
        # oscillation "concentrates in healthy adults and fades as ARDS severity
        # rises". Only S1 and S3 are quoted, so the monotonicity that sentence
        # asserts is invisible from the quoted pair alone. Printing all four
        # keeps it under the eye of anyone who reruns the audit, without pinning
        # values the manuscript does not state.
        per_sc = {
            sc: int((exceed & (agg["scenario"] == sc)).sum())
            for sc in sorted(agg["scenario"].unique())
        }
        ordered = [per_sc[k] for k in sorted(per_sc)]
        monotone = all(a >= b for a, b in zip(ordered, ordered[1:]))
        rows.append(("diagnostic (not pinned): Vt-CV count by scenario",
                     ", ".join(f"{k}={v}" for k, v in sorted(per_sc.items()))
                     + ("  [decreasing with severity]" if monotone
                        else "  [NOT monotone in severity]"),
                     "reported"))

        # 4. NEGATIVE CALIBRATION: the counts must depend on the threshold the
        # sentence names. If a different threshold reproduced them, this guard
        # would be measuring something other than what Section 2.2 claims.
        decoy_thr = VTCV_THRESHOLD * 4
        decoy = int(((agg["Vt_cv"] > decoy_thr) & (agg["scenario"] == "S1")).sum())
        good = decoy != VTCV_SCENARIO_SPLIT["S1"]
        n_bad += 0 if good else 1
        rows.append((f"negative control: threshold {decoy_thr} does NOT reproduce S1's count",
                     f"{decoy} vs {VTCV_SCENARIO_SPLIT['S1']}",
                     "PASS" if good else "**FAIL**"))

    # 6. The S014 gate statistic. Section 2.3 reports "+0.326" as the median
    # PAIRED drop, against a preregistered gate of 0.04. It is a median of
    # per-run differences, not a difference of medians (which is 0.335); the two
    # were confused once already, and the fix at 91d705d re-derived the right
    # one from the parquet without leaving anything that re-measures it. Both
    # forms clear the gate, so no conclusion moves either way -- but a reviewer
    # recomputing the preregistered statistic lands on the paired value, and
    # this check keeps the published literal tied to it.
    if {"Vt_cv_orig", "Vt_cv_lock"} <= set(s14_pair.columns):
        paired = float((s14_pair["Vt_cv_orig"] - s14_pair["Vt_cv_lock"]).median())
        good = abs(paired - S014_PAIRED_DROP) < 0.0005
        n_bad += 0 if good else 1
        rows.append((f"S014 median paired Vt-CV drop (gate {S014_GATE})",
                     f"{paired:+.4f} (published {S014_PAIRED_DROP:+.3f})",
                     "PASS" if good else "**FAIL**"))

        # It must clear the preregistered gate, and it must NOT be the
        # difference of medians that the sentence used to quote.
        clears = paired >= S014_GATE
        n_bad += 0 if clears else 1
        rows.append((f"the paired drop clears the preregistered {S014_GATE} gate",
                     f"{paired / S014_GATE:.2f}x", "PASS" if clears else "**FAIL**"))

        diff_of_medians = float(
            s14_pair["Vt_cv_orig"].median() - s14_pair["Vt_cv_lock"].median()
        )
        distinct = abs(diff_of_medians - paired) > 0.0005
        n_bad += 0 if distinct else 1
        rows.append(("the two statistics stay distinguishable (paired vs difference of medians)",
                     f"{paired:.4f} vs {diff_of_medians:.4f}",
                     "PASS" if distinct else "**FAIL**"))
    else:
        n_bad += 1
        rows.append(("S014 paired columns resolve by name",
                     "**absent**", "**FAIL**"))

    # 7. The stable-set half of the same sentence: how many of the 8 Vt entries
    # fall in S1 and in S3, re-derived per row from the CSV rather than read
    # from the JSON summary that T2.sobol.core_output_vt already uses.
    buckets = pd.read_csv(REPO / "results/sobol_ci_buckets.csv")
    need = ("scenario", "output", "nonlinear_all_seeds", "nonlinear_any_seed")
    missing_b = [c for c in need if c not in buckets.columns]
    if missing_b:
        n_bad += 1
        rows.append(("sobol_ci_buckets.csv columns resolve by name",
                     f"**absent: {missing_b}**", "**FAIL**"))
    else:
        vt = buckets[buckets["output"] == "Vt"]
        stable = vt[vt["nonlinear_all_seeds"].astype(bool)]
        n_total = len(stable)
        good = n_total == _sobol_ci["core_by_output"]["Vt"] == 8
        n_bad += 0 if good else 1
        rows.append(("Vt entries in the stable set, from the CSV rows (the quoted 8)",
                     f"{n_total} (JSON {_sobol_ci['core_by_output']['Vt']}, published 8)",
                     "PASS" if good else "**FAIL**"))
        for sc, published in VTCV_STABLE_VT_SPLIT.items():
            got = int((stable["scenario"] == sc).sum())
            good = got == published
            n_bad += 0 if good else 1
            rows.append((f"{sc}: stable-set Vt entries",
                         f"{got} (published {published})",
                         "PASS" if good else "**FAIL**"))
        # NEGATIVE CALIBRATION: a single seed must not reproduce the split, or
        # "under each of five seeds" would be doing no work here.
        any_seed = vt[vt["nonlinear_any_seed"].astype(bool)]
        decoy = tuple(int((any_seed["scenario"] == sc).sum()) for sc in VTCV_STABLE_VT_SPLIT)
        good = decoy != tuple(VTCV_STABLE_VT_SPLIT.values())
        n_bad += 0 if good else 1
        rows.append(("negative control: any-seed criterion does NOT reproduce the S1/S3 split",
                     f"{decoy} vs {tuple(VTCV_STABLE_VT_SPLIT.values())}",
                     "PASS" if good else "**FAIL**"))
        rel, needle = VTCV_STABLE_VT_TEXT
        present = needle in (REPO / rel).read_text(encoding="utf-8")
        n_bad += 0 if present else 1
        rows.append((f"`{rel}` states the stable-set split",
                     "present" if present else "**absent**",
                     "PASS" if present else "**FAIL**"))

    # 5. The literals must still be present in both documents that carry them.
    for rel, needle in VTCV_TEXT_LOCI:
        present = needle in (REPO / rel).read_text(encoding="utf-8")
        n_bad += 0 if present else 1
        rows.append((f"`{rel}` still states this split",
                     "present" if present else "**absent**",
                     "PASS" if present else "**FAIL**"))

    print("| check | observed | verdict |")
    print("|---|---|---|")
    for label, observed, verdict in rows:
        print(f"| {label} | {observed} | {verdict} |")
    print(
        f"\n**Vt-CV scenario-split guard:** {len(rows)} checks, "
        f"{len(rows) - n_bad} PASS, {n_bad} FAIL.\n"
    )
    return n_bad


# -----------------------------------------------------------------------------
# SHAP pooled-agreement unit (2026-08-20).
#
# T2.s023.pooled already pins the VALUE 17. What drifted was the UNIT: §2.2 first
# said SHAP "recovers the same dominant inputs", and two candidate rewrites --
# "17 of the 18 pooled top-three input selections" and "17 of the 18 pooled
# output-by-rank comparisons" -- both described a measurement the code does not
# perform. The statistic is sum(overlap_size) over the six outputs, i.e. a SET
# intersection of the two top-three sets, with a maximum of 6 x 3 = 18. It
# ignores order inside the top three: HR scores 3 although SHAP ranks
# hr|fio2|peep and Morris ranks hr|peep|fio2.
#
# A guard on the value alone would not have caught either rewrite. These checks
# pin the unit instead.
# -----------------------------------------------------------------------------
SHAP_POOLED_OVERLAP = 17
SHAP_POOLED_OUTPUTS = 6
SHAP_TOPK = 3
SHAP_PARTIAL_OUTPUTS = ("PaO2",)


def check_shap_pooled_unit() -> int:
    """Pin what the 17-of-18 pooled SHAP agreement actually counts."""
    print("\n## SHAP pooled-agreement unit guard\n")
    rows: list[tuple[str, str, str]] = []
    n_bad = 0

    n_out = len(s23_pooled)
    ok = n_out == SHAP_POOLED_OUTPUTS
    n_bad += 0 if ok else 1
    rows.append(("the pooled table holds one row per output",
                 f"{n_out} (expected {SHAP_POOLED_OUTPUTS})",
                 "PASS" if ok else "**FAIL**"))

    denom = n_out * SHAP_TOPK
    total = int(s23_pooled["overlap_size"].sum())
    ok = total == SHAP_POOLED_OVERLAP and denom == 18
    n_bad += 0 if ok else 1
    rows.append(("summed top-three membership overlap",
                 f"{total} of {denom} (published {SHAP_POOLED_OVERLAP} of 18)",
                 "PASS" if ok else "**FAIL**"))

    # The unit is a SET intersection. Demonstrate it: at least one output must
    # have a full overlap while the two orderings differ. If that ever stopped
    # holding, a rank-based rewrite of the sentence would look defensible.
    order_differs = [
        r.output for r in s23_pooled.itertuples()
        if r.overlap_size == SHAP_TOPK and r.shap_top3 != r.morris_top3
    ]
    ok = bool(order_differs)
    n_bad += 0 if ok else 1
    rows.append(("the metric ignores order within the top three",
                 f"full overlap but different ordering on {order_differs}"
                 if ok else "**no such output -- the set/rank distinction is unprovable here**",
                 "PASS" if ok else "**FAIL**"))

    partial = sorted(r.output for r in s23_pooled.itertuples()
                     if r.overlap_size < SHAP_TOPK)
    ok = partial == list(SHAP_PARTIAL_OUTPUTS)
    n_bad += 0 if ok else 1
    rows.append(("the outputs that fall short are the expected ones",
                 f"{partial} (expected {list(SHAP_PARTIAL_OUTPUTS)})",
                 "PASS" if ok else "**FAIL**"))

    # The prose must not re-describe the statistic as rank-based.
    paper_src = (REPO / "preprint_npj/paper.tex").read_text(encoding="utf-8")
    banned = [p for p in ("output-by-rank", "top-three input selections",
                          "same rank", "rank-for-rank") if p in paper_src]
    ok = not banned
    n_bad += 0 if ok else 1
    rows.append(("no rank-based description of the pooled SHAP statistic",
                 "none" if ok else f"**{banned}**",
                 "PASS" if ok else "**FAIL**"))

    print("| check | observed | verdict |")
    print("|---|---|---|")
    for label, observed, verdict in rows:
        print(f"| {label} | {observed} | {verdict} |")
    print(
        f"\n**SHAP pooled-agreement unit guard:** {len(rows)} checks, "
        f"{len(rows) - n_bad} PASS, {n_bad} FAIL.\n"
    )
    return n_bad


# -----------------------------------------------------------------------------
# detector / classifier vocabulary (2026-08-20).
#
# The four-flag object is called the "classifier" in prose; "detector" survives
# only in three places where it means something else, and each has a reason:
#
#   - the log-based rejection detector, a narrower object that reads the setup
#     log and can only see EXPLICIT refusal (§2.1, §4.4; the Discussion copy,
#     the only "rejection-log detector", was cut as a duplicate of §2.1 on
#     2026-09-15, so that phrase is no longer required -- "log-based detector"
#     still is);
#   - "Detector self-consistent", the name of preregistered pilot gating
#     criterion 2 (preregistration.md:178). That document says in the same
#     breath: "Do not silently edit pilot criteria". It is quoted, not chosen;
#   - LaTeX labels (sec:methods-detector, sec:s3-detector-order), invisible to
#     the reader and load-bearing for cross-references.
#
# This guard exists because the first harmonisation pass MISSED three loci. The
# search that enumerated them used a context window of 90 characters either side,
# and "Every simulation was classified by a four-flag steady-state detector"
# begins only 60 characters into its line, so the pattern could not match and the
# absence was read as completeness. Both directions are therefore checked: the
# banned phrasings must be gone, AND the three legitimate senses must remain.
# -----------------------------------------------------------------------------
DETECTOR_BANNED = (
    "four-flag detector",
    "four-flag steady-state detector",
    "preregistered detector flags",
    "steady-state detector",
)
DETECTOR_REQUIRED = (
    "log-based detector",
    "detector self-consistency",
)


def check_detector_vocabulary() -> int:
    """Keep 'detector' only where it does not mean the four-flag object."""
    print("\n## detector/classifier vocabulary guard\n")
    rows: list[tuple[str, str, str]] = []
    n_bad = 0

    # Corpus widened 2026-08-22. Reading paper.tex alone left a hole the size of
    # a figure: the study-design flowchart lived inside paper.tex as a
    # tikzpicture when this guard was written, and moved out to
    # figures/fig00_study_design.tex when it was externalised. Its boxes then
    # read "Four-flag steady-state detector" and "Per-cell traffic-light
    # reliability atlas" for weeks, in the guarded document's own Figure 1,
    # without this check ever seeing them.
    #
    # Globbed rather than named so a future .tex figure is covered on arrival.
    # Supplement figure sources are deliberately NOT swept: the defect was at the
    # paper/externalised-figure boundary, and an instrument should stay the size
    # of the claim it protects.
    sources = {"preprint_npj/paper.tex": (REPO / "preprint_npj/paper.tex").read_text(encoding="utf-8")}
    for tex in sorted((REPO / "preprint_npj" / "figures").glob("*.tex")):
        sources[f"preprint_npj/figures/{tex.name}"] = tex.read_text(encoding="utf-8")
    rows.append(("corpus swept",
                 ", ".join(sorted(sources)), "PASS"))

    # The checks further down -- flatline literals, verbatim clamp patterns, the
    # absence of a code listing -- are about the paper's PROSE and stay scoped to
    # paper.tex, case-sensitively. Only the banned-phrase sweep widened.
    src = sources["preprint_npj/paper.tex"]

    # Case-insensitive. The box read "Four-flag" with a capital F while the
    # banned list is lowercase, so a case-sensitive str.count would have missed
    # it even once the file was in scope. Two independent reasons for one miss.
    for phrase in DETECTOR_BANNED:
        needle = phrase.lower()
        where = {name: text.lower().count(needle) for name, text in sources.items()}
        hits = sum(where.values())
        ok = hits == 0
        n_bad += 0 if ok else 1
        detail = "absent" if ok else "**" + ", ".join(
            f"{name}: {n}" for name, n in where.items() if n) + "**"
        rows.append((f"`{phrase}` absent (any case)", detail,
                     "PASS" if ok else "**FAIL**"))

    # The other direction. A blanket replace of "detector" would silently rename
    # a preregistered criterion and erase the distinction between the four-flag
    # object and the narrower log reader. These stay required in paper.tex
    # specifically: they are prose, and a figure box is not where they belong.
    paper = sources["preprint_npj/paper.tex"].lower()
    for phrase in DETECTOR_REQUIRED:
        hits = paper.count(phrase.lower())
        ok = hits >= 1
        n_bad += 0 if ok else 1
        rows.append((f"`{phrase}` still present in paper.tex",
                     f"{hits} occurrence(s)" if ok else "**absent**",
                     "PASS" if ok else "**FAIL**"))

    # §2.6 now states the two flatline conditions numerically. They are constants
    # in src/detector.py, so the paper must not drift from the code that produced
    # the flags. Guarded rather than anchored: two numbers, and the repository
    # rule is that a ledger anchor cascades across counter-bearing lines while a
    # guard carries its own count.
    src_det = (REPO / "src" / "detector.py").read_text(encoding="utf-8")
    m_std = re.search(r"FLATLINE_STD_RATIO:\s*float\s*=\s*([\d.]+)", src_det)
    m_tol = re.search(r"FLATLINE_BOUND_TOL:\s*float\s*=\s*([\d.]+)", src_det)
    ok = m_std is not None and m_tol is not None
    n_bad += 0 if ok else 1
    rows.append(("flatline constants located in src/detector.py",
                 "both" if ok else "**absent -- the paper's numbers cannot be checked**",
                 "PASS" if ok else "**FAIL**"))

    if ok:
        std_pct = float(m_std.group(1)) * 100
        tol_pct = float(m_tol.group(1)) * 100
        ceiling = 100.0 - tol_pct
        # Each expected literal is BUILT from the constant, not hard-coded. A
        # hard-coded literal would keep passing after the constant moved, which
        # is precisely the drift this check exists to catch.
        for label, expected in (
            ("variability threshold", f"below {std_pct:g}~\\% of the mean"),
            ("bound tolerance", f"within {tol_pct:g}~\\% of a hard bound"),
            ("SpO2 flatline ceiling", f"$\\geq$~{ceiling:g}~\\%"),
        ):
            present = expected in src
            n_bad += 0 if present else 1
            rows.append((f"§2.6 states the {label} as the code defines it",
                         f"`{expected}`" if present
                         else f"**`{expected}` absent from paper.tex**",
                         "PASS" if present else "**FAIL**"))

    # The clamp regexes have ONE documentary home. They are printed in
    # supplement.tex, where T1.detector.patterns_verbatim_in_supplement holds
    # them character-identical to src/detector.py. paper.tex used to print a
    # second, unguarded copy -- the sweep-era four rather than the current five
    # -- which is a drift surface with no compensating benefit: the flag fired
    # 0 of 1,280 times, while the bounds and drift thresholds behind the flags
    # that fired 126 and 530 times were already deferred to the supplement.
    # Removed 2026-08-20; this check keeps it removed.
    # Match the PRINTED-REGEX form, r"...", not the bare string. Table 2 quotes
    # two rejection messages as prose examples of what `clamped` means, and a
    # guard that fired on those would be banning a legitimate use -- the same
    # miscalibration that "two rows earlier" produced in the CDC guard.
    for pat in CLAMP_PATTERNS_FROM_SRC:
        present = f'r"{pat}"' in src
        n_bad += 0 if not present else 1
        rows.append((f"clamp regex not printed in paper.tex: `{pat[:30]}...`",
                     "absent" if not present else "**re-introduced in paper.tex**",
                     "PASS" if not present else "**FAIL**"))

    ok = "lstlisting" not in src
    n_bad += 0 if ok else 1
    rows.append(("paper.tex prints no code listing at all",
                 "none" if ok else "**a listing environment is present**",
                 "PASS" if ok else "**FAIL**"))

    # The preregistered criterion must still match its source document.
    prereg = (REPO / "preregistration.md").read_text(encoding="utf-8")
    ok = "Detector self-consistent" in prereg
    n_bad += 0 if ok else 1
    rows.append(("preregistration.md still names the criterion `Detector self-consistent`",
                 "yes" if ok else "**no -- the paper would be quoting a phrase that moved**",
                 "PASS" if ok else "**FAIL**"))

    print("| check | observed | verdict |")
    print("|---|---|---|")
    for label, observed, verdict in rows:
        print(f"| {label} | {observed} | {verdict} |")
    print(
        f"\n**detector/classifier vocabulary guard:** {len(rows)} checks, "
        f"{len(rows) - n_bad} PASS, {n_bad} FAIL.\n"
    )
    return n_bad


# -----------------------------------------------------------------------------
# CDC body-weight provenance (2026-08-20).
#
# The manuscript, the supplement and the monograph all stated that the reference
# weights came from a CDC 214-month row, and that 67.64 / 56.41 kg were the
# values "at exactly 18.0 years". Both were wrong, from one cause: Agemos = 218.5
# was taken for the 18.0-year row. It is 18 y 2 m. The values in use sit at
# Agemos = 216.5, which CDC documents as denoting 216.0-216.99 months -- the
# interval beginning at exactly 18.0 years ("Age is listed at the half month
# point for the entire month", cdc.gov/growthcharts/cdc-data-files.htm).
#
# The preregistration erratum, which the manuscript had declared inaccurate, was
# correct. It is a dated record and is NOT edited; this guard instead pins the
# corrected provenance so the two-month shift cannot return.
#
# Values below are transcribed from the official CDC z-score file wtage.csv,
# read 2026-08-20 with columns resolved by NAME (P50 is column 10; reading
# column 9 gives P25, which is how a first pass here produced wrong figures).
# -----------------------------------------------------------------------------
CDC_P50_WEIGHT_KG = {
    (1, "216.5"): 67.28992603,
    (2, "216.5"): 56.22969564,
    (1, "218.5"): 67.64281378,
    (2, "218.5"): 56.40963105,
    (1, "214.5"): 66.91783563,
    (2, "214.5"): 56.05304601,
}
# Only phrases that UNIQUELY constitute the wrong claim. "two rows earlier" was
# tried and removed: it is generic, and it appears in the corrected text where
# the mechanism of the error is explained. A guard that forces contortions in
# legitimate prose is miscalibrated, and the four below already fail on any
# restatement of the wrong provenance.
CDC_PROVENANCE_BANNED = (
    "214 months",
    "214--214.99-month",
    "214-214.99-month",
    "at exactly 18.0 years are 67.64",
    "off-by-two-rows lookup was inherited",
)
CDC_PROVENANCE_DOCS = (
    "preprint_npj/paper.tex",
    "preprint_npj/supplement.tex",
    "preprint/manuscript.md",
)


def check_cdc_weight_provenance() -> int:
    """Pin the corrected CDC provenance of the two reference body weights."""
    print("\n## CDC body-weight provenance guard\n")
    rows: list[tuple[str, str, str]] = []
    n_bad = 0

    # 1. The published weights are the 216.5 row, rounded.
    for sex, label, published in ((1, "male", 67.3), (2, "female", 56.2)):
        exact = CDC_P50_WEIGHT_KG[(sex, "216.5")]
        ok = round(exact, 1) == published
        n_bad += 0 if ok else 1
        rows.append((f"CDC P50 at Agemos 216.5 rounds to the {label} body weight",
                     f"{exact} -> {round(exact, 1)} (published {published})",
                     "PASS" if ok else "**FAIL**"))

    # 2. NEGATIVE CONTROL, and the exact defect that motivated this guard: the
    # 214.5 row must NOT round to the published weights, and the 218.5 row must
    # not be mistakable for the 18.0-year row.
    for sex, label, published in ((1, "male", 67.3), (2, "female", 56.2)):
        wrong = CDC_P50_WEIGHT_KG[(sex, "214.5")]
        ok = round(wrong, 1) != published
        n_bad += 0 if ok else 1
        rows.append((f"the 214.5 row does NOT give the {label} weight",
                     f"{wrong} -> {round(wrong, 1)} vs {published}",
                     "PASS" if ok else "**FAIL**"))

    ok = CDC_P50_WEIGHT_KG[(1, "218.5")] != CDC_P50_WEIGHT_KG[(1, "216.5")]
    n_bad += 0 if ok else 1
    rows.append(("the 218.5 and 216.5 rows stay distinct",
                 f"{CDC_P50_WEIGHT_KG[(1, '218.5')]} vs {CDC_P50_WEIGHT_KG[(1, '216.5')]}",
                 "PASS" if ok else "**FAIL**"))

    # 3. The wrong provenance must be gone from every document that carried it.
    for rel in CDC_PROVENANCE_DOCS:
        text = (REPO / rel).read_text(encoding="utf-8")
        found = [p for p in CDC_PROVENANCE_BANNED if p in text]
        ok = not found
        n_bad += 0 if ok else 1
        rows.append((f"`{rel}` free of the 214-month provenance",
                     "clean" if ok else f"**{found}**",
                     "PASS" if ok else "**FAIL**"))

    # 4. The corrected row must be named where the provenance is stated.
    for rel in CDC_PROVENANCE_DOCS:
        text = (REPO / rel).read_text(encoding="utf-8")
        ok = "216.5" in text
        n_bad += 0 if ok else 1
        rows.append((f"`{rel}` names the corrected CDC row",
                     "Agemos 216.5 present" if ok else "**absent**",
                     "PASS" if ok else "**FAIL**"))

    # 5. The preregistration erratum is a dated record and stays untouched. It
    # was correct all along, so its text must still be there to be correct.
    prereg = (REPO / "preregistration.md").read_text(encoding="utf-8")
    ok = "216.5 months" in prereg
    n_bad += 0 if ok else 1
    rows.append(("preregistration.md still states 18 years (216.5 months)",
                 "present -- and correct" if ok else "**absent**",
                 "PASS" if ok else "**FAIL**"))

    print("| check | observed | verdict |")
    print("|---|---|---|")
    for label, observed, verdict in rows:
        print(f"| {label} | {observed} | {verdict} |")
    print(
        f"\n**CDC body-weight provenance guard:** {len(rows)} checks, "
        f"{len(rows) - n_bad} PASS, {n_bad} FAIL.\n"
    )
    return n_bad


# -----------------------------------------------------------------------------
# Publication gate (2026-08-20).
#
# The manuscript claims, in the present tense, that the code and lab-notebook
# entries ARE openly available on GitHub. That is true only once the repository
# is public, and the maintainer's release order puts the arXiv deposit and the
# visibility flip BEFORE the npj submission. The constraint had no tracked home
# -- it lived in TODO_publication_roadmap.md, which .gitignore:103 excludes --
# so audit/publication_gate.md now carries it and this guard keeps the two in
# step.
#
# What this can and cannot do: it cannot reach GitHub, so it does not check
# visibility. It checks that the register exists, that it still states the
# ordering constraint, and that the number of present-tense availability claims
# has not drifted from what the register enumerates. A new claim added without
# updating the register fails here, which is the realistic failure mode.
# -----------------------------------------------------------------------------
PUBLICATION_CLAIM_PATTERNS = (
    "are released open-source",
    "openly available",
    "is released under the Apache",
)
PUBLICATION_CLAIM_FILES = (
    "preprint_npj/paper.tex",
    "preprint_npj/supplement.tex",
    "preprint/manuscript.md",
)
# 5 -> 4 on 2026-09-28: Data availability's "already openly available in the public
# code repository" was merged into Code availability, whose "is released under the
# Apache" sentence already counted here; the register lists the four loci.
PUBLICATION_CLAIM_TOTAL = 4


def check_publication_gate() -> int:
    """Keep the availability claims in step with the publication-gate register."""
    print("\n## Publication-gate guard\n")
    rows: list[tuple[str, str, str]] = []
    n_bad = 0

    reg = REPO / "audit" / "publication_gate.md"
    ok = reg.exists()
    n_bad += 0 if ok else 1
    rows.append(("`audit/publication_gate.md` exists",
                 "present" if ok else "**absent -- the constraint has no tracked home**",
                 "PASS" if ok else "**FAIL**"))

    if ok:
        # Whitespace-normalised, because the register is prose and reflows. A
        # needle that assumes a single space between two words fails the moment
        # the line wraps between them -- which is exactly how this check failed
        # on its first run.
        text = re.sub(r"\s+", " ", reg.read_text(encoding="utf-8"))
        for needle, label in (
            ("**before** npj acceptance or review", "states that public release precedes npj"),
            ("**Private**", "records the last verified repository visibility"),
        ):
            found = needle in text
            n_bad += 0 if found else 1
            rows.append((f"register {label}",
                         "yes" if found else f"**`{needle}` absent**",
                         "PASS" if found else "**FAIL**"))

    total = 0
    per_file: list[str] = []
    for rel in PUBLICATION_CLAIM_FILES:
        src_text = (REPO / rel).read_text(encoding="utf-8")
        n = sum(src_text.count(p) for p in PUBLICATION_CLAIM_PATTERNS)
        total += n
        per_file.append(f"{rel.split('/')[-1]}={n}")
    ok = total == PUBLICATION_CLAIM_TOTAL
    n_bad += 0 if ok else 1
    rows.append(("present-tense availability claims match the register",
                 f"{total} ({', '.join(per_file)}); register enumerates "
                 f"{PUBLICATION_CLAIM_TOTAL}",
                 "PASS" if ok else "**FAIL**"))

    print("| check | observed | verdict |")
    print("|---|---|---|")
    for label, observed, verdict in rows:
        print(f"| {label} | {observed} | {verdict} |")
    print(
        f"\n**Publication-gate guard:** {len(rows)} checks, "
        f"{len(rows) - n_bad} PASS, {n_bad} FAIL. Visibility itself is not "
        f"checkable offline; see the register's checklist.\n"
    )
    return n_bad


n_pubgate_fail = check_publication_gate()

n_cdcprov_fail = check_cdc_weight_provenance()

n_detvocab_fail = check_detector_vocabulary()

n_shap_unit_fail = check_shap_pooled_unit()

n_vtcv_split_fail = check_vtcv_scenario_split()

n_abstract_fail = check_abstract_extent()

n_s021_conv_fail = check_s021_converged_plateau()


# -----------------------------------------------------------------------------
# Continuous-severity band guard (2026-09-14).
#
# The supplement's continuous-severity table, the empirical instability band
# and Figure S1 (Figure S2 since 2026-10-07) were computed on the run DIRECTORY label sev{int(sev*1000)} --
# a truncation -- instead of the severity Pulse was given. CONT_M_078 ran at
# 0.9458464, so the published band [0.879, 0.945] excluded one male
# divergence, six runs sat in the wrong bin, and "0 / 51" should have been
# 0 / 50. The parquet column named `ards_severity_continuous` is that
# truncated label; `ards_severity` is the simulated value. Found by the number
# audit (audit/number_inventory.md section 4.1, F-S5).
#
# The band is published as the smallest 3-decimal interval CONTAINING every
# diverged severity (floor the minimum, ceil the maximum): rounding would drop
# the lowest divergence, 0.87977, out of [0.880, ...].
# -----------------------------------------------------------------------------
CONT_SWEEP_SOURCE = "results/continuous_ards_severity_sweep.parquet"
CONT_BAND = (0.879, 0.946)
CONT_BAND_BY_SEX = {"F": (0.879, 0.928), "M": (0.899, 0.946)}
CONT_BIN_EDGES = (0.0, 0.5, 0.85, 0.91, 0.945, 0.95, 1.0)
# per bin, per sex: (n, diverged)
CONT_BIN_TABLE = {
    "F": ((31, 0), (19, 0), (19, 14), (9, 5), (2, 0), (20, 0)),
    "M": ((31, 0), (19, 0), (19, 5), (9, 8), (2, 1), (20, 0)),
}
CONT_TEXT_REQUIRED = (
    ("preprint_npj/paper.tex", "$[0.879, 0.946]$", 2),
    ("preprint_npj/supplement.tex", "$(0.945, 0.95]$    & 2  & 0 / 2   & \\textbf{1 / 2}", 1),
    ("preprint_npj/supplement.tex", "$(0.91, 0.945]$    & 9  & 5 / 9   & \\textbf{8 / 9}", 1),
    ("preprint_npj/supplement.tex", "0 / 50 divergences for each sex", 1),
    ("preprint/manuscript.md", "| (0.945, 0.95]    | 0 / 2      | **1 / 2**  |", 1),
    ("preprint/manuscript.md", "0.879–0.928, male 0.899–0.946", 1),
    ("README.md", "female 14/19 vs male 5/19 in (0.85, 0.91], female 5/9 vs male 8/9", 1),
    # Added 2026-09-16, in both files at once and deliberately so. The
    # non-examination claim is the novelty argument the cover letter opens on,
    # and the 2026-09-02 compression deleted the manuscript sentence that
    # carried it while the letter kept asserting it -- an editor-facing claim
    # with no locus in the submission for two weeks. Pairing the two loci makes
    # either one going missing a FAIL. Re-verified 2026-09-16 in the local
    # REL_4_3_2 clone (docs identical to 4.3.1): HowTo-IsoShuntAnalysis.cpp:60
    # sweeps {0.0, 0.3, 0.6, 0.9}, HowTo-CreateAPatient.cpp:76 sets 0.9, the
    # highest ARDS severity in any shipped adult scenario is 0.9
    # (ARDSExacerbation.json), and RespiratoryMethodology.md:1746 reports the
    # ARDS validation "against a moderate severity scenario". Nothing lands
    # inside 0.91--0.945.
    # Re-pinned 2026-10-14 (supplement audit row S5.14, cover-letter item L11):
    # the "up to 0.9 at most" half was false for the HowTo examples taken
    # together -- src/csharp/howto/HowTo_EngineUse.cs L136-137 (REL_4_3_1 and
    # REL_4_3_2) sets ARDS severity 1.0 on both lungs, in live code, which the
    # 2026-09-16 check above (C++ HowTos and scenarios only) did not open. Both
    # loci now keep only the band half, which still holds: no Pulse file that
    # mentions ARDS sets a severity inside 0.91--0.945.
    ("preprint_npj/supplement.tex",
     "HowTo examples do not examine impairment fractions within 0.91--0.945", 1),
    ("preprint_npj/cover_letter.md",
     "HowTo examples do not examine impairment fractions inside 0.91–0.945", 1),
    # Added 2026-09-17, on the author's decision, and paired for the same reason
    # as the two rows above. Results 2.5 states that all 20 divergences fall on
    # the male body; that is true of the Morris input extremes and false as a
    # statement about the engine, because the midrange severity sweep reverses
    # it in the lower part of the band (Supplement S5.5, Table S5.4: female
    # 14/19 against male 5/19 in (0.85, 0.91]). The paper carried no such
    # qualifier until now, so a reader of the paper alone could take "all-male"
    # as general. Either locus going missing is a FAIL. Re-pinned 2026-10-06:
    # the M. Sauthier review round reworded "with the female body dominating the
    # lower part" to "the female body mainly in the lower part"; both readings
    # hold on Table S11 (14 of the 19 female divergences sit in (0.85, 0.91]).
    ("preprint_npj/paper.tex", "the female body mainly in the lower part of the band", 1),
    ("preprint_npj/supplement.tex", "female divergence concentrated in the lower part", 1),
    # Added 2026-09-17 by the prose audit, which found that the qualifier added
    # above had landed on Results 2.5 ONLY: the abstract and the Figure 5 legend
    # -- the two surfaces read most often on their own -- still stated the
    # all-male result unbounded. Both now carry it, and both are pinned here
    # because the abstract sits exactly at the npj 150-word cap (measured on the
    # build: 150 whitespace tokens, 147 letter-or-digit tokens). A future
    # condensation pass needing one word would delete this clause first, and
    # nothing else in the gate would notice. Either locus going missing is a FAIL.
    ("preprint_npj/paper.tex", "all-male in an input-extreme regime", 1),
    ("preprint_npj/paper.tex",
     "The asymmetry is specific to this input-extreme regime", 1),
)
CONT_TEXT_BANNED = ("0.879, 0.945", "0.879--0.945", "0.879–0.945", "0 / 51 divergence", "14/18", "14 / 18")
CONT_TEXT_FILES = ("preprint_npj/paper.tex", "preprint_npj/supplement.tex",
                   "preprint/manuscript.md", "README.md", "preprint_npj/cover_letter.md")


def _cont_bins(sev: pd.Series, div: pd.Series) -> tuple[tuple[int, int], ...]:
    out = []
    for lo, hi in zip(CONT_BIN_EDGES[:-1], CONT_BIN_EDGES[1:]):
        mask = ((sev >= lo) if lo == 0.0 else (sev > lo)) & (sev <= hi)
        out.append((int(mask.sum()), int((mask & div).sum())))
    return tuple(out)


def check_continuous_severity_band() -> int:
    """Re-derive the continuous-severity band, per-sex ranges and bin table."""
    print("\n## Continuous-severity band guard (Supplement S5, Figure S2)\n")
    rows: list[tuple[str, str, str]] = []
    n_bad = 0

    def record(label: str, observed: str, ok: bool) -> None:
        nonlocal n_bad
        n_bad += 0 if ok else 1
        rows.append((label, observed, "PASS" if ok else "**FAIL**"))

    cont = pd.read_parquet(REPO / CONT_SWEEP_SOURCE)
    need = {"case_id", "ards_severity", "ards_severity_continuous", "diverged"}
    missing = need - set(cont.columns)
    record("columns resolve by name", "all present" if not missing else f"absent: {sorted(missing)}", not missing)
    if not missing:
        sex = cont["case_id"].str.split("_").str[1]
        sev = cont["ards_severity"].astype(float)
        div = cont["diverged"].astype(bool)
        record("200 runs, 100 per sex", f"{len(cont)} ({sex.value_counts().to_dict()})",
               len(cont) == 200 and set(sex.value_counts().to_dict().values()) == {100})
        dv = sev[div]
        band = (math.floor(dv.min() * 1000) / 1000, math.ceil(dv.max() * 1000) / 1000)
        record("containing band of diverged simulated severities", f"[{band[0]:.3f}, {band[1]:.3f}] (published {CONT_BAND})",
               band == CONT_BAND)
        for sx, pub in CONT_BAND_BY_SEX.items():
            s = sev[div & (sex == sx)]
            got = (math.floor(s.min() * 1000) / 1000, math.ceil(s.max() * 1000) / 1000)
            record(f"{sx} containing range", f"[{got[0]:.3f}, {got[1]:.3f}] (published {pub})", got == pub)
        for sx, pub in CONT_BIN_TABLE.items():
            got = _cont_bins(sev[sex == sx], div[sex == sx])
            record(f"{sx} bin table (n, diverged)", f"{got}", got == pub)
        # NEGATIVE CALIBRATION: the truncated label must NOT reproduce the published
        # table or band, or this guard would pass on a regression to label binning.
        lab = cont["ards_severity_continuous"].astype(float)
        trunc_ok = bool((lab == (sev * 1000).apply(math.floor) / 1000).all())
        record("negative-control column is the int(sev*1000) truncation", str(trunc_ok), trunc_ok)
        lab_band = (math.floor(lab[div].min() * 1000) / 1000, math.ceil(lab[div].max() * 1000) / 1000)
        lab_tab = _cont_bins(lab[sex == "M"], div[sex == "M"])
        record("negative control: the truncated label gives a different band and male table",
               f"{lab_band}, {lab_tab}", lab_band != CONT_BAND and lab_tab != CONT_BIN_TABLE["M"])

    for rel, needle, expected in CONT_TEXT_REQUIRED:
        got = (REPO / rel).read_text(encoding="utf-8").count(needle)
        record(f"`{rel}` carries `{needle[:48]}`", f"{got} (expected {expected})", got == expected)
    for rel in CONT_TEXT_FILES:
        text = (REPO / rel).read_text(encoding="utf-8")
        hits = [b for b in CONT_TEXT_BANNED if b in text]
        record(f"`{rel}` free of the truncated-label figures", "clean" if not hits else f"found {hits}", not hits)

    print("| check | observed | verdict |")
    print("|---|---|---|")
    for label, observed, verdict in rows:
        print(f"| {label} | {observed} | {verdict} |")
    print(f"\n**Continuous-severity band guard:** {len(rows)} checks, {len(rows) - n_bad} PASS, {n_bad} FAIL.\n")
    return n_bad


n_contband_fail = check_continuous_severity_band()


# -----------------------------------------------------------------------------
# Follow-up selection-rule guard (2026-10-07).
#
# npj asks that Methods "contain all elements necessary to allow interpretation
# and replication of the results". Until 2026-10-07 neither the paper nor the
# supplement said how the follow-up runs were chosen: the rules lived only in
# scripts/run_s014_trigger_lockout.py::select_top_64,
# scripts/run_s021_hyperoxia_convergence.py::select_subset and
# scripts/continuous_ards_sweep.py::severity_grid. Paper section 4.3 now states
# them, and S5.4 / S9.1 give the detail. This guard re-derives each rule from the
# tracked data and pins the sentences, so text and data cannot drift apart.
# Each rule carries a negative control that a wrong reading must fail.
# -----------------------------------------------------------------------------
FOLLOWUP_TEXT_REQUIRED = (
    ("preprint_npj/paper.tex", "took the 64 non-diverged sweep runs with the highest delivered-Vt CV", 1),
    ("preprint_npj/paper.tex", "took the 22 Morris points requested at FiO$_2$ = 1.0 that diverged in no cell, "
     "in both Healthy cells, and the first four, in sample order, in the Moderate and Severe cells", 1),
    ("preprint_npj/paper.tex", "ran 100 impairment fractions, drawn at random and more densely above 0.85, "
     "on both bodies, with the seven inputs at the midpoints of their swept ranges (FiO$_2$ rounded to 0.6)", 1),
    ("preprint_npj/paper.tex", "Further detail, including the two most affected configurations: "
     "Supplement~\\S\\,\\ref{sec:s8}.", 1),
    ("preprint_npj/supplement.tex", "The 100 impairment fractions were drawn uniformly at random (seed 2026) in three "
     "strata, 50 between 0 and 0.85, 30 between 0.85 and 0.95 and 20 between 0.95 and 1, and the same 100 values "
     "were run on both bodies.", 1),
    ("preprint_npj/supplement.tex", "The 60 reruns comprise the 22 Morris points requested at FiO$_2$ = 1.0 that "
     "diverged in none of the eight cells, run in both Healthy cells (44 reruns), and the first four of these points "
     "in sample order (run indices 6, 7, 12 and 13), run in the two Moderate and two Severe cells (16 reruns).", 1),
)
FOLLOWUP_TEXT_BANNED = {
    # Section S8 holds summaries and two named configurations, not per-run values.
    "preprint_npj/paper.tex": ("per-run values: Supplement",),
    "preprint_npj/supplement.tex": ("full protocol}",),
}
FOLLOWUP_SWEPT_RANGES = {"in_hr": (50, 110), "in_sbp": (90, 120), "in_dbp": (60, 80), "in_rr": (8, 20),
                         "in_vt": (300, 800), "in_fio2": (0.21, 1.0), "in_peep": (0, 20)}


def check_followup_selection() -> int:
    """Re-derive the S014, S021 and continuous-severity selection rules."""
    print("\n## Follow-up selection-rule guard (paper 4.3; Supplement S5.4, S8.1, S9.1)\n")
    rows: list[tuple[str, str, str]] = []
    n_bad = 0

    def record(label: str, observed: str, ok: bool) -> None:
        nonlocal n_bad
        n_bad += 0 if ok else 1
        rows.append((label, observed, "PASS" if ok else "**FAIL**"))

    sweep = pd.read_parquet(REPO / "data/runs/full_sweep/aggregated.parquet")
    sweep["run_idx"] = sweep["case_id"].str.split("_").str[-1].astype(int)

    # S014: the 64 non-diverged runs with the highest Vt CV.
    s14 = pd.read_parquet(REPO / "data/runs/s014_trigger_lockout/selection.parquet")
    pool = sweep[~sweep["diverged"] & sweep["Vt_cv"].notna()]
    top = set(pool.nlargest(64, "Vt_cv")["case_id"])
    rest_max = pool.loc[~pool["case_id"].isin(top), "Vt_cv"].max()
    sel_min = pool.loc[pool["case_id"].isin(top), "Vt_cv"].min()
    record("S014: stored selection = top-64 non-diverged by Vt CV", f"{len(s14)} rows, equal: {set(s14['case_id']) == top}",
           len(s14) == 64 and set(s14["case_id"]) == top)
    record("S014: the cut is strict (no tie at the 64th value)", f"{sel_min:.4f} > {rest_max:.4f}", sel_min > rest_max)
    lowest = set(pool.nsmallest(64, "Vt_cv")["case_id"])
    record("S014 negative control: the 64 LOWEST Vt CV differ", str(lowest != top), lowest != top)

    # S021: Morris points requested at FiO2 = 1.0 that diverged in none of the eight cells.
    s21 = pd.read_parquet(REPO / "data/runs/s021_hyperoxia_convergence/selection.parquet")
    s21["run_idx"] = s21["case_id"].str.split("_").str[-1].astype(int)
    f1 = sweep[sweep["in_fio2"] == 1.0]
    n_cells = sweep.groupby(["scenario", "sex"]).ngroups
    clean_cells = f1[~f1["diverged"]].groupby("run_idx").size()
    common = sorted(int(i) for i in clean_cells[clean_cells == n_cells].index)
    healthy = s21[s21["scenario"] == "S1"]
    shunt = sorted(int(i) for i in set(s21.loc[s21["scenario"].isin(["S3", "S4"]), "run_idx"]))
    record("S021: 22 points at FiO2 = 1.0 diverge in none of the 8 cells", f"{len(common)} over {n_cells} cells",
           len(common) == 22 and n_cells == 8)
    record("S021: both Healthy cells carry all 22 (44 reruns)",
           f"{len(healthy)} rows, sets equal: {sorted(set(healthy['run_idx'])) == common}",
           len(healthy) == 44 and sorted(set(healthy["run_idx"])) == common
           and set(healthy["sex"]) == {"M", "F"})
    record("S021: Moderate and Severe carry the first four in sample order",
           f"{shunt} vs {common[:4]}; rows {int(s21['scenario'].isin(['S3', 'S4']).sum())}",
           shunt == common[:4] == [6, 7, 12, 13] and int(s21["scenario"].isin(["S3", "S4"]).sum()) == 16)
    record("S021: 60 reruns in total", str(len(s21)), len(s21) == 60)
    any_div = sorted(int(i) for i in f1.loc[~f1["diverged"], "run_idx"].unique())
    record("S021 negative control: 'non-diverged in at least one cell' gives more than 22", str(len(any_div)),
           len(any_div) > 22)

    # Continuous-severity sweep: seed 2026, strata 50/30/20, same values on both bodies, mid-range inputs.
    cont = pd.read_parquet(REPO / CONT_SWEEP_SOURCE)
    import numpy as _np  # local: only this guard needs it
    rng = _np.random.default_rng(2026)
    grid = _np.sort(_np.concatenate([rng.uniform(0.0, 0.85, 50), rng.uniform(0.85, 0.95, 30), rng.uniform(0.95, 1.0, 20)]))
    by_sex = {s: _np.sort(cont.loc[cont["sex"] == s, "ards_severity"].astype(float).to_numpy()) for s in ("M", "F")}
    same = all(len(v) == 100 and _np.allclose(v, grid, rtol=0, atol=1e-12) for v in by_sex.values())
    record("continuous: both bodies ran exactly the seed-2026 grid", str(same), same)
    v = by_sex["M"]
    strata = (int((v < 0.85).sum()), int(((v >= 0.85) & (v < 0.95)).sum()), int((v >= 0.95).sum()))
    dens = (strata[0] / 0.85, strata[1] / 0.10, strata[2] / 0.05)
    record("continuous: strata 50 / 30 / 20", str(strata), strata == (50, 30, 20))
    record("continuous: denser above 0.85 than below (per unit)", " / ".join(f"{d:.0f}" for d in dens),
           min(dens[1], dens[2]) > dens[0])
    other = _np.sort(_np.random.default_rng(2027).uniform(0.0, 1.0, 100))
    record("continuous negative control: another seed does not match", str(not _np.allclose(other, grid)),
           not _np.allclose(other, grid))
    mids = {k: (lo + hi) / 2 for k, (lo, hi) in FOLLOWUP_SWEPT_RANGES.items()}
    got = {k: sorted(set(cont[k].astype(float))) for k in FOLLOWUP_SWEPT_RANGES}
    exact = all(got[k] == [mids[k]] for k in mids if k != "in_fio2")
    fio2_ok = got["in_fio2"] == [0.6] and round(mids["in_fio2"], 1) == 0.6
    record("continuous: inputs at the swept midpoints (FiO2 0.605 rounded to 0.6)",
           f"{ {k: g for k, g in got.items()} }", exact and fio2_ok)

    for rel, needle, expected in FOLLOWUP_TEXT_REQUIRED:
        n = re.sub(r"\s+", " ", (REPO / rel).read_text(encoding="utf-8")).count(needle)
        record(f"`{rel}` carries `{needle[:48]}`", f"{n} (expected {expected})", n == expected)
    for rel, banned in FOLLOWUP_TEXT_BANNED.items():
        text = (REPO / rel).read_text(encoding="utf-8")
        hits = [b for b in banned if b in text]
        record(f"`{rel}` free of {banned}", "clean" if not hits else f"found {hits}", not hits)

    print("| check | observed | verdict |")
    print("|---|---|---|")
    for label, observed, verdict in rows:
        print(f"| {label} | {observed} | {verdict} |")
    print(f"\n**Follow-up selection-rule guard:** {len(rows)} checks, {len(rows) - n_bad} PASS, {n_bad} FAIL.\n")
    return n_bad


n_followup_fail = check_followup_selection()


# -----------------------------------------------------------------------------
# Supplement small-number audit guard (2026-09-14).
#
# The row-by-row reading of the supplement's ambiguous_small residue
# (audit/number_inventory.md section 4.2) found, and the author corrected:
#   F-S7  "20 / 20 clean with the four-pattern set" cited a validation script
#         that passes an empty log, so no pattern was ever evaluated; replaced
#         by the runs that did exercise the patterns (pilot probes, smoke set).
#   F-S8  "the single worst-affected configuration": S1_F_0117 and S1_F_0118
#         tie exactly at the maximum pre-lock Vt CV; plus two wrong pointers.
#   F-S9  the vital-capacity 7 % came from Pulse's methodology prose, not its
#         validation table, whose current StandardMale value gives about 5 %.
#   #15   "within approximately 5 % of the asymptote" measured about 0.1 % on
#         the median trajectory and at most 1.6 % per run, against the value
#         at t = 300 s. A first measurement dropped the t = 240 s sample.
#   M-1   the blank FiO2 rows are in paper Figure 3, not Figure 2.
# -----------------------------------------------------------------------------
SMALL_AUDIT_TEXT_REQUIRED = (
    ("preprint_npj/supplement.tex",
     "Pulse's respiratory methodology reports a standard-patient vital capacity of 4.93~L "
     "against a literature value of about 4.6~L (about 7~\\% higher); its current patient "
     "validation table lists 4{,}819~mL for the standard male (about 5~\\% higher).", 1),
    ("preprint_npj/supplement.tex",
     "FiO$_2$ rows of Figure~3 of the main manuscript are therefore blank", 1),
    ("preprint_npj/supplement.tex",
     "fired on both deliberate-clamp probes of the pilot (SBP = 140 and DBP = 85~mmHg, each "
     "rejected at setup with exit code 1) and on none of the eight smoke-test runs", 1),
    ("preprint/manuscript.md", "eight [S004](#s004) smoke-test runs", 1),
    ("preprint_npj/supplement.tex", "mostly the Healthy (26 reruns) and Mild (19) cells", 1),
    ("preprint_npj/supplement.tex",
     "1.826 (S1\\_F\\_0117 and S1\\_F\\_0118, run indices 117 and 118 in the Healthy-F "
     "cell); the lock reduces them to 0.018 and 0.024", 1),
    ("preprint_npj/supplement.tex",
     "The two worst-affected configurations (\\S\\ref{sec:s8-protocol}; the two rightmost "
     "points of Figure~4a of the main manuscript)", 1),
    # The paper-side pointer ("the two worst-affected configurations and the
    # per-run values are in Supplement S8") was removed in the M. Sauthier
    # review round (2026-10-06): the paper then read "Full protocol and per-run
    # values: Supplement S8". S8 holds no per-run values, so on 2026-10-07 it
    # became "Further detail, including the two most affected configurations:
    # Supplement S8" (pinned by the follow-up selection-rule guard). The two
    # configurations stay named in S8.1, pinned above; the singular wording
    # stays banned in paper.tex below.
    ("preprint_npj/supplement.tex",
     "within about 0.1~\\% of the value at $t = 300$~s on the median trajectory, "
     "and within 1.6~\\% for any individual run", 1),
)
SMALL_AUDIT_TEXT_BANNED = {
    "preprint_npj/supplement.tex": (
        "Detector validation on twenty reference runs",
        "20 / 20 clean with the four-pattern set",
        "single worst-affected configuration",
        "named in Section~\\mainref{sec:results-vcac}{2.3}",
        "(Table~1 of the main manuscript)",
        "of the asymptote",
        "rows of Figure~2 of the main manuscript",
        "per Pulse's own validation table.",
    ),
    "preprint/manuscript.md": (
        "Detector validation on 20 reference runs",
        "20 / 20 clean with the new regex set",
    ),
    "preprint_npj/paper.tex": ("the worst-affected configuration and the per-run values",),
}
# External values, read on pulse.kitware.com on 2026-09-14: respiratory
# methodology prose (VC 4.93 L, literature about 4.6 L) and the patient
# methodology StandardMale validation table (VitalCapacity 4819.2 mL).
SMALL_AUDIT_VC = {"prose_L": 4.93, "literature_L": 4.6, "table_mL": 4819.2}


def check_supplement_small_audit() -> int:
    """Pin the five corrections of the supplement's small-number audit."""
    print("\n## Supplement small-number audit guard (F-S7, F-S8, F-S9, #15, M-1)\n")
    rows: list[tuple[str, str, str]] = []
    n_bad = 0

    def record(label: str, observed: str, ok: bool) -> None:
        nonlocal n_bad
        n_bad += 0 if ok else 1
        rows.append((label, observed, "PASS" if ok else "**FAIL**"))

    # F-S7: the runs the new sentence names.
    pilot = pd.read_parquet(REPO / "data" / "runs" / "pilot_S1_M" / "aggregated.parquet").set_index("case_id")
    for cid, col, val in (("S1_M_9900", "in_sbp", 140.0), ("S1_M_9901", "in_dbp", 85.0)):
        ok = (cid in pilot.index and float(pilot.loc[cid, col]) == val
              and bool(pilot.loc[cid, "clamped"]) and int(pilot.loc[cid, "exit_code"]) == 1)
        observed = (f"{col} {pilot.loc[cid, col]}, clamped {pilot.loc[cid, 'clamped']}, "
                    f"exit {pilot.loc[cid, 'exit_code']}") if cid in pilot.index else "absent"
        record(f"F-S7 pilot probe {cid} fired clamped at setup", observed, ok)
    smoke = pd.read_parquet(REPO / "data" / "runs" / "scenario_smoke" / "aggregated.parquet")
    record("F-S7 smoke set: eight runs, none clamped",
           f"{len(smoke)} runs, {int(smoke['clamped'].sum())} clamped",
           len(smoke) == 8 and int(smoke["clamped"].sum()) == 0)

    # F-S8: the tie, the locked values and the rerun distribution.
    pc = pd.read_parquet(REPO / "data" / "runs" / "s014_trigger_lockout" / "paired_comparison.parquet")
    top = pc.sort_values(["Vt_cv_orig", "case_id"], ascending=[False, True]).reset_index(drop=True)
    tie = (abs(float(top.loc[0, "Vt_cv_orig"]) - float(top.loc[1, "Vt_cv_orig"])) < 1e-12
           and float(top.loc[2, "Vt_cv_orig"]) < float(top.loc[1, "Vt_cv_orig"]) - 1e-6)
    record("F-S8 exactly two runs share the maximum pre-lock Vt CV",
           f"{top.loc[0, 'case_id']} {top.loc[0, 'Vt_cv_orig']:.12f}, {top.loc[1, 'case_id']} "
           f"{top.loc[1, 'Vt_cv_orig']:.12f}, next {top.loc[2, 'Vt_cv_orig']:.6f}",
           tie and list(top.loc[:1, "case_id"]) == ["S1_F_0117", "S1_F_0118"]
           and round(float(top.loc[0, "Vt_cv_orig"]), 3) == 1.826)
    locked = dict(zip(top.loc[:1, "case_id"], top.loc[:1, "Vt_cv_lock"].round(3)))
    record("F-S8 locked CVs of the two", f"{locked}",
           locked == {"S1_F_0117": 0.018, "S1_F_0118": 0.024})
    per_sc = pc["scenario"].value_counts().to_dict()
    cells = set(pc["case_id"].str.extract(r"^(S\d_[MF])")[0])
    record("F-S8 reruns per scenario: S1 26, S2 19 of 64; seven cells, S3_M absent",
           f"{per_sc}, {len(pc)} pairs, cells {sorted(cells)}",
           per_sc.get("S1") == 26 and per_sc.get("S2") == 19 and len(pc) == 64
           and len(cells) == 7 and "S3_M" not in cells)

    # F-S9: the two published percentages from the two Pulse pages.
    vc = SMALL_AUDIT_VC
    p_prose = 100.0 * (vc["prose_L"] / vc["literature_L"] - 1.0)
    p_table = 100.0 * (vc["table_mL"] / (1000.0 * vc["literature_L"]) - 1.0)
    record("F-S9 about 7 % (prose) and about 5 % (validation table)",
           f"{p_prose:.2f} %, {p_table:.2f} %", round(p_prose) == 7 and round(p_table) == 5)

    # #15: the recipe's deviation, re-derived from the S021 per-run traces.
    s21 = REPO / "data" / "runs" / "s021_hyperoxia_convergence"
    plat = pd.read_parquet(s21 / "plateau_stats.parquet")
    phys = plat[(plat["scenario"] == "S1") & plat["converged"] & (plat["PaO2_plateau_mmHg"] <= 700)]
    csvs = [s21 / cid / "output.csv" for cid in phys["case_id_long"]]
    present = [p for p in csvs if p.exists()]
    if len(phys) and len(present) == len(csvs):
        frames, per_run = [], []
        for p in present:
            df = pd.read_csv(p)[["time_s", "ArterialOxygenPressure"]]
            win = df[(df["time_s"] >= 240.0 - 1e-6) & (df["time_s"] <= 300.0 + 1e-6)]
            last = float(df["ArterialOxygenPressure"].iloc[-1])
            per_run.append((len(win), 100.0 * abs(float(win["ArterialOxygenPressure"].mean()) - last) / last))
            frames.append(df.assign(t=df["time_s"].round(6)))
        med = pd.concat(frames).groupby("t")["ArterialOxygenPressure"].median()
        wm = med[(med.index >= 240.0) & (med.index <= 300.0)]
        dev_med = 100.0 * abs(float(wm.mean()) - float(med.iloc[-1])) / float(med.iloc[-1])
        dev_max = max(d for _, d in per_run)
        n_win = {n for n, _ in per_run}
        record("#15 recipe window holds 13 samples per run (t = 240 s included)",
               f"{sorted(n_win)} over {len(per_run)} runs", n_win == {13} and len(per_run) == 37)
        record("#15 median trajectory: about 0.1 %", f"{dev_med:.3f} %", round(dev_med, 1) == 0.1)
        record("#15 any single run: within 1.6 %, and the bound is tight to 0.1",
               f"max {dev_max:.3f} %", dev_max <= 1.6 and dev_max > 1.5)
    elif len(phys) and not present:
        record("#15 S021 per-run traces absent (clean checkout): re-derivation skipped",
               f"0 of {len(csvs)} output.csv present", True)
    else:
        record("#15 S021 per-run traces partially present", f"{len(present)} of {len(csvs)}", False)

    for rel, needle, expected in SMALL_AUDIT_TEXT_REQUIRED:
        got = (REPO / rel).read_text(encoding="utf-8").count(needle)
        record(f"`{rel}` carries `{needle[:48]}`", f"{got} (expected {expected})", got == expected)
    for rel, banned in SMALL_AUDIT_TEXT_BANNED.items():
        text = (REPO / rel).read_text(encoding="utf-8")
        hits = [b for b in banned if b in text]
        record(f"`{rel}` free of the corrected wordings", "clean" if not hits else f"found {hits}", not hits)

    print("| check | observed | verdict |")
    print("|---|---|---|")
    for label, observed, verdict in rows:
        print(f"| {label} | {observed} | {verdict} |")
    print(f"\n**Supplement small-number audit guard:** {len(rows)} checks, {len(rows) - n_bad} PASS, {n_bad} FAIL.\n")
    return n_bad


n_smallaudit_fail = check_supplement_small_audit()


# -----------------------------------------------------------------------------
# Monograph number-audit guard (audit/number_inventory.md section 5), added
# 2026-09-14 with the author's decisions on MF-1..MF-21, O-3/5/7/8/9/10/11 and
# the Cornish citation (published in JMLR 27(152), 2026). Each check re-derives
# the value the corrected wording states, so that a later data or code change
# that falsifies it fails here; the text checks require the corrected wording
# and ban the one it replaced. Gitignored raw logs skip cleanly when absent.
# -----------------------------------------------------------------------------
MONO_AUDIT_TEXT_REQUIRED = (
    ("preprint/manuscript.md", "of the remaining 17 cells, 11 have a bootstrap CI straddling", 1),
    ("preprint/manuscript.md", "1 is CI-robustly non-linear (S3_M, PaO2 ← FiO2), and 5 have too few", 1),
    ("preprint/manuscript.md", "Largest in S4 (91 / 185 of", 1),
    ("preprint/manuscript.md", "(71 / 76 of those runs;", 1),
    ("preprint/manuscript.md", "S1 clean runs, whose FiO2 spans only [0.21, 0.47], gives a flatter", 1),
    ("preprint/manuscript.md", "[0.21, 0.47] vs single-input near the FiO2 = 1.0 boundary)", 1),
    ("preprint/manuscript.md", "PaO2 ≈ 480 mmHg at FiO2 = 1.0;", 1),
    ("preprint/manuscript.md", "HR and MAP drift rates stay below 3 % and PaCO2", 1),
    ("preprint/manuscript.md", "for run S1_F_0008),", 1),
    ("preprint/manuscript.md", "PaCO2 is the only one flagged under Hoeffding (3 / 70) and the most", 1),
    ("preprint/manuscript.md", "saturation-boundary cells (2 of 8 cells)", 1),
    ("preprint/manuscript.md", "the large effects\n  (|EE| 0.014–0.049) all come from pairs taken at FiO2 = 0.21, where SpO2\n"
     "  is 0.95–0.96 — three of the four pairs there (one Vt step moves SpO2\n  from 0.962 to 0.929)", 1),
    ("preprint/manuscript.md", "the largest value, 0.12 in S3, would read 12 in percentage points", 1),
    ("preprint/manuscript.md", "constants — is in Appendix B.5.\n\nCompanion verification\n"
     "(`Pulse_translation_new` female-surrogate engine tests", 1),
    ("preprint/manuscript.md", "twelve independent verification", 1),
    ("preprint/manuscript.md", "all twelve passed with zero violations", 1),
    ("preprint/manuscript.md", "neither of the laptop's two GPUs (Intel UHD, NVIDIA RTX 3050) is used", 1),
    ("preprint/manuscript.md", "was run on the mild-ARDS male cell", 1),
    ("preprint/manuscript.md", "`src/detector.py:413`", 1),
    ("preprint/manuscript.md", "8–12. Structural lumped-parameter limits — discussed in §4.5.", 1),
    ("preprint/manuscript.md", "weight^1.02 (§3.5). |", 1),
    ("preprint/manuscript.md", "§1.2 limitations list (entry 4)", 1),
    ("preprint/manuscript.md", "~105 MB of engine logs", 1),
    ("preprint/manuscript.md", "(CDC P50 ≈ 176.2", 1),
    ("preprint/manuscript.md", "E10 boundary probe, confirmed by E6, reported an", 1),
    ("preprint/manuscript.md", "output.csv / output_pulse_native.csv /", 1),
    ("preprint/manuscript.md", "files, 23 MB of them text,", 1),
    ("preprint/manuscript.md", "bit-identical\n  completed runs and 20 / 20", 1),
    ("preprint/manuscript.md", "(4 scenarios, healthy S1 and ARDS S2/S3/S4,", 1),
    ("preprint/manuscript.md", "24 core experiment-log entries\n(S001–S024)", 1),
    # O-11 again (2026-09-15): Supplement S18 (AI-use detail moved out of Methods 4.7) -> S1-S18.
    ("preprint/manuscript.md", "| §S1 – §S18 |", 1),
    ("preprint/manuscript.md", "Research 27(152):1–52 (2026)", 1),
    ("preprint/manuscript.md", "Research 27(152):1–52\n  (2026); first posted as arXiv:2301.07210", 1),
    ("preprint/manuscript.md", "the published Tables 4 and 5 keep the same counts and add\n  Manski-bound columns.", 1),
    ("preprint/manuscript.md", "(external; used by Cornish\n2026, §4.4)", 1),
    ("preprint/manuscript.md", "study (Cornish\net al. 2026; Table 2)", 1),
    ("preprint_npj/supplement.tex", "Cornish et al.\\ 2026 per-channel cross-mapping", 2),
    # GL-S1 (guard/ledger read-through, 2026-09-15): the supplement's copy of MF-19.
    ("preprint_npj/supplement.tex", "was documented in our preregistration (scenario table and hypothesis H3) "
     "and in the verified-limitations table (Supplement~\\S\\,\\ref{sec:s2}, row 4)", 1),
    # YL-M2 (year-like read-through, 2026-09-15): the companion's CDC weight audit step sits in its
    # "Female Pediatric Population -- Implementation (April 2026)" section (commit a7fa508, 2026-04-01).
    ("preprint/manuscript.md", "(CDC weight audit step,\n  2026-04)", 1),
    # MK-M1 (masked-literal read-through, 2026-09-15): the preregistration erratum is a
    # blockquote on lines 9-36, both today and when the pointer was written (219a13a).
    ("preprint/manuscript.md", "erratum of 2026-05-19, lines\n9–36).", 1),
    # Number-word findings resolved on the author's decisions (2026-09-15, register section 9).
    # W-P1: the tie count is true only at one or two decimals (4 + 5), the qualifier restored.
    # The paper literal re-pinned 2026-10-06: the M. Sauthier round dropped the
    # qualifier, and the author restored it (decision D28, audit/sauthier_review_2026-10.md).
    ("preprint_npj/paper.tex", "would fall on an exact rounding tie at one or two decimals.", 1),
    ("preprint/manuscript.md", "fall on an exact rounding tie at one or two decimals.", 1),
    # W-P2: the condensation pass measured part by part (f2ac374 -> e361c2a). The Methods ratio
    # (0.54) excludes the AI-disclosure subsection, which the pass left unchanged (0.59 with it).
    # Since 2026-09-15 the phase-by-phase detail lives in Supplement S18, so the sentence moved
    # there and "this disclosure" became "the AI-use subsection".
    # Re-pinned 2026-10-06 (M. Sauthier review round): "the Methods other than the
    # AI-use subsection" became "the Methods (except the AI-use subsection)".
    ("preprint_npj/supplement.tex", "the Introduction, the Discussion and the Methods (except the AI-use "
     "subsection) were rewritten to about half their length "
     "and the Results to about a third, the figure legends were shortened by about a quarter, and the abstract "
     "was revised within its 150-word cap", 1),
    # W-S2: the out-of-sample estimates follow in their own subsection.
    ("preprint_npj/supplement.tex", "so its training fit says nothing about predictive accuracy (out-of-sample "
     "estimates follow in \\S\\ref{sec:s13-oos})", 1),
    # W-S3: two BMR consumers form TMR/BMR, the third (EndocrineModel.cpp L164) tests TMR > BMR.
    ("preprint_npj/supplement.tex", "cancel the sex term exactly at rest, where total metabolic rate equals basal "
     "(two divide one by the other, and the third acts only when total exceeds basal).", 1),
    # W-M1: the clamp catalogue holds five patterns since the 2026-07-26 patch; no count, a pointer.
    ("preprint/manuscript.md", "instead of pattern-matching the regex set documented in §2.6.", 1),
    # W-M2 (number-word read-through, 2026-09-15): the permutation null splits the pooled runs
    # at the original M and F group sizes (src/analysis_compare.py, pool[:n_m]), not in halves.
    ("preprint/manuscript.md", "runs into two groups the same size as the original M and F groups", 1),
    ("preprint/manuscript.md", "randomly into\ntwo groups of the original sizes", 1),
    # Four defects found while reading the supplement for the 2026-09-16 condensation pass,
    # corrected on the author's decision. Each is guarded in both directions: the corrected
    # wording is required here, the wording it replaced is banned below.
    # C-S1: scripts/make_supp_fig_s3.py takes the highlighted median over the physiological
    # subset (plateau <= 700 mmHg), i.e. 37 runs, not over all 40 drift-converged ones; the
    # figure caption and S9.3 already said 37.
    ("preprint_npj/supplement.tex", "the thick line is the median of the 37 with a physiological "
     "plateau", 1),
    # C-S2: the rho table covers S2 (mild) and S3 (moderate), so the scope is both scenarios.
    # Re-pinned 2026-10-06: the M. Sauthier round dropped the trailing "S2 and S3";
    # the scope still names both scenarios.
    # Re-pinned 2026-10-07: the scenarios are named by their labels (author decision).
    ("preprint_npj/supplement.tex", "rankings across sex in the Mild and Moderate scenarios", 1),
    # C-S3: the quoted sentence was never in paper.tex verbatim (0 occurrences); it is now a
    # paraphrase, and the paper's own wording is "80 on channels the present atlas does not assess".
    # The count is kept in the sentence because crosswalk T3.s028.cornish_non_overlap_hoeffding counts
    # it; since the M. Sauthier review round (2026-10-06) it reads "80 of their 85".
    ("preprint_npj/supplement.tex", "80 of their 85 Hoeffding rejections fall on "
     "channels the atlas does not assess", 1),
    # C-S4: "this absence" had no antecedent in the paragraph (it has had none since 48912f8).
    ("preprint_npj/supplement.tex", "The absence of a surfactant model was also verified directly", 1),
    # GL-S2 (2026-09-15, author's decision; unit corrected 2026-09-27): resample-count sensitivity.
    ("preprint_npj/supplement.tex", "repeating the procedure with 500, 2{,}000 and 4{,}000 resamples returns "
     "the same 23 inputs", 1),
    ("preprint/supplementary.md", "## S10 — Verification points (twelve independent layers)", 1),
    ("preprint/supplementary.md", "12 independent verification points; 0 failures", 1),
)
MONO_AUDIT_TEXT_BANNED = {
    "preprint/manuscript.md": (
        "0.6 (12)", "cells in S1 and S4_F)", "104 / 185", "74 / 76 of those runs",
        "[0.21, 1.0] range", "[0.21, 1.0] vs single-input", "PaO2 ≈ 481 mmHg",
        "HR, MAP, and PaCO2 drift rates stay below 3 %", "worst-CV run", "only flagged channel",
        "noise-dominated", "floating-point fluctuation", "because the output sits at the",
        "NHANES P50 anchors", "SBP 118 mmHg (M)", "eleven independent verification", "all eleven passed",
        "the eleven verification", "and the eleven\n", "8 GB RAM, no GPU", "moderate-ARDS male cell",
        "detector.py:338", "discussed in §4.3.", "§4.3 / §4.5 limitations", "(§4.3 limitations)",
        "weight^1.02 (§3.6)", "preregistration limitations table", "~50 MB of engine logs",
        "CDC P50 ≈ 177", "E6 audit reported", "files / 23 MB", "bit-identical\n  clean runs",
        "4 ARDS severities S1/S2/S3/S4", "§S1 – §S16", "§S1 – §S17", "Cornish et al. 2023", "Cornish et al. (2023)",
        "Cornish-2023", "Cornish 2023 Table 4", "(Oxford, 2023)", "(November 2023, v4)",
        "used by Cornish 2023", "(Cornish et al. 2023;", "from 0.962 to 0.930",
        "NHANES resting heart-rate anchors", "median HR 70 bpm (M) / 74 bpm (F)",
        "FiO2 = 0.21, where SpO2 is 0.95–0.96, carry the large ones",
        "Tables 4 and 5 are unchanged in the published version",
        "per-run output.csv / pulse.log", "the 24 experiment-log entries cited",
        "CDC weight audit step, 2026-03", "erratum of 2026-05-19, lines 9–34",
        "runs into halves the same size", "randomly into halves of the original sizes",
        "values fall on an exact rounding tie.", "pattern-matching the four-pattern regex set",
        "four ARDS severities",
    ),
    "preprint_npj/paper.tex": ("exact rounding tie whose last digit",
                               "figure legends and abstract were rewritten to about half their length",
                               "the Introduction, Discussion and Methods were rewritten"),
    "preprint_npj/supplement.tex": ("Cornish et al.\\ 2023", "Cornish 2023 channel", "preregistration limitations table",
                                    "and at 500 one combination is lost", "carries no out-of-sample evaluation",
                                    "combine it as a ratio of total to basal metabolic rate",
                                    # C-S1 .. C-S4 (2026-09-16): the four wordings corrected in this pass.
                                    # "80 of 85 Hoeffding" stays legitimate in the monograph, hence the file scope.
                                    "median trajectory across that subset", "in the moderate-ARDS regime",
                                    "``80 of 85 Hoeffding rejections", "Separately, this absence"),
    "scripts/sobol_ci_buckets.py": ("identical at 1,000 / 2,000 / 4,000 (one combination is lost",),
    "preprint/supplementary.md": ("eleven independent layers", "11 independent verification points"),
    # 2026-10-14: "four ARDS severities" survived in the cover letter (item L1) and in the
    # monograph's conclusion although scenario S1 is the healthy baseline (impairment 0.00);
    # the banned "4 ARDS severities S1/S2/S3/S4" above did not catch the spelled-out form.
    "preprint_npj/cover_letter.md": ("four ARDS severities",),
}
MONO_AUDIT_JMLR_FIELDS = (
    ("journal", "Journal of Machine Learning Research"), ("volume", "27"), ("number", "152"),
    ("pages", "1--52"), ("year", "2026"),
)


def check_monograph_number_audit() -> int:
    """Pin the author-approved corrections of the monograph number audit."""
    print("\n## Monograph number-audit guard (MF-1..MF-21, O-3..O-11, Cornish JMLR)\n")
    rows: list[tuple[str, str, str]] = []
    n_bad = 0

    def record(label: str, observed: str, ok: bool) -> None:
        nonlocal n_bad
        n_bad += 0 if ok else 1
        rows.append((label, observed, "PASS" if ok else "**FAIL**"))

    mono = (REPO / "preprint" / "manuscript.md").read_text(encoding="utf-8")

    # MF-1, MF-14: Appendix C attribution.
    nss = pd.read_csv(REPO / "results" / "s022" / "nss_decomposition.csv")
    body = nss[nss["cell"] != "Total"].assign(sc=lambda d: d["cell"].str[:2])
    both = body.groupby("sc")["n_nss_excl_both"].sum().to_dict()
    record("MF-1 excl.-both residual: S4 91 and S1 53 of 185",
           f"{both}, total {int(body['n_nss_excl_both'].sum())}",
           both.get("S4") == 91 and both.get("S1") == 53 and int(body["n_nss_excl_both"].sum()) == 185)
    spo2 = (body["n_nss_locked"] - body["n_nss_excl_SpO2_saturation"]).groupby(body["sc"]).sum().to_dict()
    record("MF-14 SpO2-saturation contribution: S1 + S2 = 71 of 76",
           f"{spo2}", spo2.get("S1", 0) + spo2.get("S2", 0) == 71 and sum(spo2.values()) == 76)

    # MF-2: clean S1 FiO2 support and the linear extrapolation.
    flags = ["clamped", "diverged", "implausible", "not_steady_state"]
    s1c = agg[(agg["scenario"] == "S1") & ~agg[flags].any(axis=1)]
    levels = sorted(s1c["in_fio2"].round(4).unique())
    slope = ((s1c["in_fio2"] - s1c["in_fio2"].mean()) * (s1c["PaO2_mean"] - s1c["PaO2_mean"].mean())).sum() / (
        (s1c["in_fio2"] - s1c["in_fio2"].mean()) ** 2).sum()
    at1 = float(s1c["PaO2_mean"].mean() + slope * (1.0 - s1c["in_fio2"].mean()))
    record("MF-2 clean S1 FiO2 spans only [0.21, 0.47]; OLS at FiO2 = 1.0 ≈ 480",
           f"levels {levels}, n {len(s1c)}, fit at 1.0 = {at1:.1f}",
           levels == [0.21, 0.4733] and round(at1) == 480)

    # MF-3: dominant-input CI buckets.
    sb = pd.read_csv(REPO / "results" / "sobol_ci_buckets.csv")
    dom = sb[sb["rank"] == 1]
    lin, non, noci = (dom[c].astype(bool) for c in ("linear_all_seeds", "nonlinear_all_seeds", "no_estimable_ci"))
    non_cells = sorted(map(tuple, dom[non][["scenario", "sex", "output", "input"]].values.tolist()))
    noci_cells = sorted(map(tuple, dom[noci][["scenario", "sex", "output", "input"]].values.tolist()))
    record("MF-3 buckets: 31 linear, 11 straddling, 1 non-linear (S3_M PaO2←FiO2), 5 without a CI",
           f"{int(lin.sum())} / {int((~lin & ~non & ~noci).sum())} / {non_cells} / {len(noci_cells)}",
           len(dom) == 48 and int(lin.sum()) == 31 and int((~lin & ~non & ~noci).sum()) == 11
           and non_cells == [("S3", "M", "PaO2", "fio2")])
    record("MF-3 the five no-CI cells are S1_F (Vt dominant) and S4_M (FiO2 dominant)", f"{noci_cells}",
           noci_cells == [("S1", "F", "PaCO2", "vt"), ("S1", "F", "PaO2", "vt"), ("S1", "F", "Vt", "vt"),
                          ("S4", "M", "PaO2", "fio2"), ("S4", "M", "SpO2", "fio2")])

    # MF-11: per-arm drift exceedance against the detector thresholds.
    valid = agg[agg["HR_delta_60s"].notna()]
    arms = {"hyperoxia": valid[valid["in_fio2"] >= 0.95], "Vt oscillation": valid[valid["Vt_cv"] > 0.05]}
    rates = {a: {ch: 100.0 * float((d[f"{ch}_delta_60s"].abs() > _WIN_TH[ch]).mean()) for ch in ("HR", "MAP", "PaCO2")}
             for a, d in arms.items()}
    record("MF-11 HR and MAP below 3 %, PaCO2 below 4 % in both arms (hyperoxia PaCO2 above 3 %)",
           "; ".join(f"{a}: " + ", ".join(f"{k} {v:.2f} %" for k, v in r.items()) for a, r in rates.items()),
           all(r["HR"] < 3 and r["MAP"] < 3 and r["PaCO2"] < 4 for r in rates.values())
           and rates["hyperoxia"]["PaCO2"] >= 3)

    # MF-12: S1_F_0008 is not the worst pre-lock CV, and is the worst locked one.
    rk = agg[["case_id", "Vt_cv"]].dropna().assign(r=lambda d: d["Vt_cv"].rank(ascending=False, method="min"))
    pc = pd.read_parquet(REPO / "data" / "runs" / "s014_trigger_lockout" / "paired_comparison.parquet")
    r8 = int(rk.loc[rk["case_id"] == "S1_F_0008", "r"].iloc[0])
    record("MF-12 S1_F_0008: rank 6 before the lock, highest CV after it",
           f"rank {r8}, worst locked {pc.loc[pc['Vt_cv_lock'].idxmax(), 'case_id']}",
           r8 == 6 and pc.loc[pc["Vt_cv_lock"].idxmax(), "case_id"] == "S1_F_0008")

    # MF-13: engine-log volume (gitignored; skip when absent, fail when partial).
    logs = [REPO / "data" / "runs" / "full_sweep" / f"{c[:4]}" / c / "pulse.log" for c in agg["case_id"]]
    have = [p for p in logs if p.exists()]
    if len(have) == len(logs):
        mb = sum(p.stat().st_size for p in have) / 1e6
        record("MF-13 the 1,280 full-sweep pulse.log files total ≈ 105 MB", f"{mb:.1f} MB", round(mb) == 105)
    elif not have:
        record("MF-13 full-sweep pulse.log absent (clean checkout): skipped", f"0 of {len(logs)}", True)
    else:
        record("MF-13 full-sweep pulse.log partially present", f"{len(have)} of {len(logs)}", False)

    # MF-15, MF-16, MF-17, MF-9, O-11, MF-7: pointers and counts.
    det = (REPO / "src" / "detector.py").read_text(encoding="utf-8").splitlines()
    record("MF-15 src/detector.py:413 is the population-std line", det[412].strip() if len(det) > 412 else "short",
           len(det) > 412 and "std(ddof=0)" in det[412])
    record("MF-16 §4.5 is Limitations and §4.3 is not", "headings",
           "\n### 4.5 Limitations\n" in mono and "\n### 4.3 Limitations" not in mono)
    heads = [(m.start(), m.group(1)) for m in re.finditer(r"^### (\d+\.\d+(?:\.\d+)?) ", mono, re.M)]
    pos = mono.find("computedBloodVolume_mL = 65.6")
    sec = max((h for h in heads if h[0] < pos), default=(0, "?"))[1] if pos >= 0 else "absent"
    record("MF-17 the blood-volume formula sits in §3.5", sec, sec.startswith("3.5"))
    scen = (REPO / "src" / "scenario.py").read_text(encoding="utf-8")
    record("MF-9 S2 is mild ARDS (0.26)", "src/scenario.py", '"S2": Scenario("S2", "Mild ARDS", 0.26)' in scen)
    supp = (REPO / "preprint_npj" / "supplement.tex").read_text(encoding="utf-8")
    n_sec = len(re.findall(r"^\\section\{", supp, re.M))
    record("O-11 the npj supplement has 18 numbered sections", f"{n_sec}", n_sec == 18)
    smd = (REPO / "preprint" / "supplementary.md").read_text(encoding="utf-8")
    s10 = smd.split("## S10", 1)[1].split("\n## ", 1)[0] if "## S10" in smd else ""
    n_rows = len(re.findall(r"^\| S0\d\d ", s10, re.M))
    record("MF-7 the S10 verification table has 12 rows", f"{n_rows}", n_rows == 12)

    # MF-18: the four direct-overlap rows of the monograph's Table 2.
    t2 = {}
    for ch in ("PaCO2", "PaO2", "MeanBP", "HR"):
        m = re.search(r"\\textbf\{" + ch + r"\}\s*& \\textbf\{(\d+) / (\d+)\}\s*& \\textbf\{(\d+) / (\d+)\}", mono)
        t2[ch] = tuple(int(x) for x in m.groups()) if m else None
    record("MF-18 Table 2: PaCO2 only Hoeffding-flagged overlap channel; bootstrap PaO2 4, MeanBP 3, HR 1",
           f"{t2}", t2 == {"PaCO2": (3, 70, 13, 70), "PaO2": (0, 78, 4, 78), "MeanBP": (0, 92, 3, 92), "HR": (0, 162, 1, 162)})

    # MF-20: Group A elementary effects by FiO2 level (same pairs as the published index).
    ee_rows = []
    for (sk, xk, inp) in (("S1", "M", "vt"), ("S1", "F", "peep")):
        cell = _s32_agg[(_s32_agg["scenario"] == sk) & (_s32_agg["sex"] == xk)].set_index("idx")
        clean = set(cell[cell["clean"]].index)
        for pr in _s32_pairs[_s32_pairs["flipped"] == inp].itertuples():
            if pr.idx_lo in clean and pr.idx_hi in clean:
                lo, hi = cell.loc[pr.idx_lo], cell.loc[pr.idx_hi]
                ee_rows.append((sk + xk + inp, round(float(lo["in_fio2"]), 2), float(lo["SpO2_mean"]),
                                float(hi["SpO2_mean"]), (float(hi["SpO2_mean"]) - float(lo["SpO2_mean"])) / pr.delta))
    hi_f = [abs(r[4]) for r in ee_rows if r[1] >= 0.47]
    lo_f = sorted(abs(r[4]) for r in ee_rows if r[1] <= 0.21)
    per_cell = {k: sum(1 for r in ee_rows if r[0] == k) for k in ("S1Mvt", "S1Fpeep")}
    sat = [v for r in ee_rows if r[1] >= 0.47 for v in (r[2], r[3])]
    start21 = [r[2] for r in ee_rows if r[1] <= 0.21]
    # Exact rounding, no tolerance: the step ends at 0.9294957, printed 0.92950 at
    # five decimals and first written 0.930 -- a tolerance of 6e-4 let that pass.
    step = [r for r in ee_rows if r[0] == "S1Mvt" and round(r[2], 3) == 0.962 and round(r[3], 3) == 0.929]
    n_large21 = sum(1 for x in lo_f if x > 0.005)
    record("MF-20 Group A: 3 + 4 pairs; abs(EE) ≤ 0.003 at FiO2 0.47, SpO2 there 0.997–0.999; "
           "large effects 0.014–0.049 at 0.21 (three of its four pairs), from SpO2 0.95–0.96; "
           "one Vt step 0.962 to 0.929",
           f"pairs {per_cell}, max at 0.47 {max(hi_f):.4f}, SpO2 {min(sat):.5f}–{max(sat):.5f}; "
           f"at 0.21 {[round(x, 4) for x in lo_f]} ({n_large21} above 0.005) "
           f"from {min(start21):.5f}–{max(start21):.5f}; step {len(step)}",
           per_cell == {"S1Mvt": 3, "S1Fpeep": 4} and max(hi_f) <= 0.003
           and len(lo_f) == 4 and n_large21 == 3
           and round(min(sat), 3) == 0.997 and round(max(sat), 3) == 0.999
           and round(lo_f[-1], 3) == 0.049 and round(sorted(x for x in lo_f if x > 0.005)[0], 3) == 0.014
           and round(min(start21), 2) == 0.95 and round(max(start21), 2) == 0.96 and len(step) == 1)

    # MF-21: the largest SpO2 mu* and the clean SpO2 range where it sits.
    mi = pd.read_parquet(REPO / "results" / "morris_indices.parquet")
    top = mi[mi["output"] == "SpO2"].sort_values("mu_star", ascending=False).iloc[0]
    cl = agg[(agg["scenario"] == top["scenario"]) & (agg["sex"] == top["sex"]) & ~agg[flags].any(axis=1)]["SpO2_mean"]
    record("MF-21 largest SpO2 mu* ≈ 0.12 in S3, where clean SpO2 is far below the ceiling",
           f"{top['scenario']}_{top['sex']} {top['mu_star']:.4f}; clean SpO2 {cl.min():.3f}–{cl.max():.3f}",
           top["scenario"] == "S3" and round(float(top["mu_star"]), 2) == 0.12 and float(cl.min()) < 0.8)

    # W-P1: recount the rounding ties of the sixteen retention counts k (percentage 0.625 k).
    # A tie at one decimal needs k = 2 mod 4, at two decimals k odd; the text says nine.
    ks = [int(v) for v in list(_cell_clean.values) + list(_cell_hard_free.values)]
    t1 = sum(1 for k in ks if k % 4 == 2)
    t2 = sum(1 for k in ks if k % 2 == 1)
    paper_tex = (REPO / "preprint_npj" / "paper.tex").read_text(encoding="utf-8")
    record("W-P1 nine of the sixteen retention values tie at one or two decimals (paper and monograph)",
           f"{len(ks)} values, {t1} at one decimal + {t2} at two = {t1 + t2}",
           len(ks) == 16 and t1 + t2 == 9 and "nine of the sixteen retention values would fall on an exact rounding "
           "tie at one or two decimals" in paper_tex and "nine of the sixteen values fall on an exact rounding tie at one or two "
           "decimals" in mono)

    # MK-M1: the line range the monograph gives for the preregistration erratum is the
    # erratum's own extent, re-read from preregistration.md (a dated record, read only).
    prereg = (REPO / "preregistration.md").read_text(encoding="utf-8").split("\n")
    start = next((i for i, ln in enumerate(prereg, 1) if ln.startswith("> **ERRATUM — 2026-05-19")), None)
    end = start
    while start is not None and end < len(prereg) and prereg[end].startswith(">"):
        end += 1
    cited = re.search(r"erratum of 2026-05-19, lines (\d+)–(\d+)\)", re.sub(r"\s+", " ", mono))
    got = (int(cited.group(1)), int(cited.group(2))) if cited else None
    record("MK-M1 the monograph's line range is the 2026-05-19 erratum's extent in preregistration.md",
           f"cited {got}, erratum lines {(start, end) if start else 'absent'}",
           start is not None and got == (start, end))

    # YL-M1 (author's decision 2026-09-15: the title page carries the revision date). The
    # invariant is the defect itself, a title date earlier than the document's own dated
    # entries; a fixed day is not pinned, so a later revision date passes. ISO dates only.
    head = re.match(r'---\n.*?\ndate: "(\d{4}-\d{2}-\d{2})"\n', mono, re.S)
    body_dates = re.findall(r"\b20\d{2}-[01]\d-[0-3]\d\b", mono[head.end():] if head else "")
    record("YL-M1 the title-page date is not earlier than the latest ISO date in the monograph body",
           f"title {head.group(1) if head else 'absent'}, latest in body {max(body_dates) if body_dates else 'none'}",
           bool(head) and bool(body_dates) and head.group(1) >= max(body_dates))

    # O-10: Phase 4a counters.
    sha = json.loads((REPO / "data" / "runs" / "full_sweep_repro" / "sha_compare.json").read_text(encoding="utf-8"))
    record("O-10 Phase 4a: 1,260 bit-exact completed runs, 20 both diverged",
           f"{sha['counters']}", sha["counters"].get("BIT_EXACT") == 1260 and sha["counters"].get("BOTH_DIVERGED") == 20)

    # Cornish: both bibliographies carry the JMLR record.
    for rel in ("preprint_npj/paper.bib", "preprint/references.bib"):
        bib = (REPO / rel).read_text(encoding="utf-8")
        m = re.search(r"@article\{cornish2023,(.*?)\n\}", bib, re.S)
        entry = m.group(1) if m else ""
        ok = bool(m) and all(re.search(rf"{f}\s*=\s*\{{{re.escape(v)}\}}", entry) for f, v in MONO_AUDIT_JMLR_FIELDS) \
            and "arXiv preprint" not in entry
        record(f"Cornish `{rel}` entry is JMLR 27(152):1--52, 2026", "entry found" if m else "absent", ok)

    for rel, needle, expected in MONO_AUDIT_TEXT_REQUIRED:
        got = (REPO / rel).read_text(encoding="utf-8").count(needle)
        record(f"`{rel}` carries `{needle[:48]!r}`", f"{got} (expected {expected})", got == expected)
    # Banned wordings are matched on whitespace-normalised text: two Cornish year
    # labels wrapped across a line break escaped a line-based search on 2026-09-14.
    for rel, banned in MONO_AUDIT_TEXT_BANNED.items():
        text = re.sub(r"\s+", " ", (REPO / rel).read_text(encoding="utf-8"))
        hits = [b for b in banned if re.sub(r"\s+", " ", b) in text]
        record(f"`{rel}` free of the corrected wordings (whitespace-normalised)",
               "clean" if not hits else f"found {hits}", not hits)

    print("| check | observed | verdict |")
    print("|---|---|---|")
    for label, observed, verdict in rows:
        print(f"| {label} | {observed.replace('|', '/')} | {verdict} |")
    print(f"\n**Monograph number-audit guard:** {len(rows)} checks, {len(rows) - n_bad} PASS, {n_bad} FAIL.\n")
    return n_bad


n_monoaudit_fail = check_monograph_number_audit()


def check_s033_cycle_resolved() -> int:
    """Every number of Supplement S8's cycle-resolved subsection, re-derived.

    Added 2026-09-12, to repay a reproducibility debt rather than a defect.
    The subsection was written on 2026-09-09 from throwaway `awk` pipelines in
    a session scratchpad; those pipelines were lost, so its figures had no
    versioned producer, no artefact under `results/` and no entry here. Nothing
    in the repository could have told anyone that.

    `scripts/s033_cycle_resolved_vtcv.py` now re-derives them from
    `data/runs/`, and this guard is what keeps the published prose tied to that
    re-derivation. A guard rather than ledger anchors on purpose: the
    subsection carries more than twenty numbers, and each ledger anchor forces
    a rewrite of the 25 head-line counters in two documents.

    Three layers, because transcription and staleness are different failures:

      * transcription -- the literal in `supplement.tex` equals the artefact;
      * arithmetic -- the artefact's own totals are internally consistent, so a
        partial regeneration cannot pass unnoticed;
      * cross-instrument -- the artefact's 5-second column and locked flags are
        compared against `data/runs/full_sweep/aggregated.parquet`, which the
        s033 script did not write. That is the layer that catches a stale
        `results/s033/`, and the one that would survive a bug in the script.

    The cycle-resolved half cannot be re-derived here (it needs 1,344 native
    50 Hz traces, far too slow for a pre-commit hook); re-running the script is
    what checks that half, and its own four calibration controls abort if the
    reconstruction stops matching the stored classification.
    """
    print("\n## S033 cycle-resolved Vt CV guard (Supplement S8)\n")
    rows: list[tuple[str, str, str]] = []
    n_bad = 0

    d = REPO / "results" / "s033"
    needed = [
        d / "sweep_confusion.json",
        d / "lockout_estimands.csv",
        d / "lockout_paired_cv.csv",
        d / "sweep_cycle_vt_cv.csv",
    ]
    missing = [p for p in needed if not p.exists()]
    if missing:
        print("| check | observed | verdict |")
        print("|---|---|---|")
        for p in missing:
            print(f"| `{p.relative_to(REPO).as_posix()}` present | **absent** | **FAIL** |")
        print(
            f"\n**S033 cycle-resolved guard:** {len(missing)} checks, 0 PASS, "
            f"{len(missing)} FAIL. Run "
            "`uv run python scripts/s033_cycle_resolved_vtcv.py`.\n"
        )
        return len(missing)

    conf = json.loads(needed[0].read_text(encoding="utf-8"))
    est = pd.read_csv(needed[1]).set_index("summary")
    per_run = pd.read_csv(needed[3]).set_index("case_id")
    supp = (REPO / "preprint_npj" / "supplement.tex").read_text(encoding="utf-8")

    def add_row(label: str, observed: str, ok: bool) -> None:
        nonlocal n_bad
        if not ok:
            n_bad += 1
        rows.append((label, observed, "PASS" if ok else "**FAIL**"))

    def pin(label: str, literal: str, value: float, published: float) -> None:
        """The literal must appear in supplement.tex AND equal the artefact."""
        found = literal in supp
        agrees = abs(value - published) <= 5e-10
        observed = f"`{literal}`" + ("" if found else " **not in supplement.tex**")
        if not agrees:
            observed += f" -- artefact gives {value!r}, prose says {published!r}"
        add_row(label, observed, found and agrees)

    # ---- layer 1: transcription ------------------------------------------- #
    pin("agreement numerator/denominator", "1{,}239 of 1{,}260 runs",
        float(conf["n_agree"] * 1e4 + conf["n_runs_analysed"]), 1239e4 + 1260)
    pin("agreement percentage", "98.3~\\%", round(conf["pct_agree"], 1), 98.3)
    pin("flagged by both", "297 runs are flagged by both",
        float(conf["flagged_by_both"]), 297)
    pin("flagged by neither", "942 by neither", float(conf["flagged_by_neither"]), 942)
    pin("cycle-only crossings", "15 cross the 0.05 threshold only at cycle resolution",
        float(conf["cycle_only"]), 15)
    pin("5-second-only crossings", "6 only under the 5-second statistic",
        float(conf["five_second_only"]), 6)
    pin("cycle-only below the 3x cut", "ten fall below a factor of 3",
        float(conf["cycle_only_below_substantial"]), 10)

    # Three quantities, three comparisons. Packing them into one number the way
    # an earlier version did (count x 1e6 + min x 1e3 + max) is NOT injective:
    # min 4.0 with max 113.9 and min 4.1 with max 13.9 both give 4113.9, so a
    # compensating drift in two of the three would have passed.
    subst = [f for f in conf["cycle_only_factors"] if f >= conf["substantial_factor_cut"]]
    add_row("substantial cycle-only crossings, and their range",
            "`five are substantial (factors of 4.0 to 113.9)` -- artefact: "
            f"{len(subst)} factors, {round(min(subst), 1)} to {round(max(subst), 1)}",
            "five are substantial (factors of 4.0 to 113.9)" in supp
            and len(subst) == 5
            and round(min(subst), 1) == 4.0
            and round(max(subst), 1) == 113.9)
    all_female = conf["cycle_only_substantial_sex"] == {"F": len(subst)}
    add_row("all substantial crossings on the female body",
            f"`all five fall on the female reference body` -- "
            f"{conf['cycle_only_substantial_sex']}",
            "all five fall on the female reference body" in supp and all_female)
    pin("numerically constant-volume runs", "Nine runs deliver a numerically constant volume",
        float(conf["n_constant_volume"]), 9)
    pin("cycle-only already flagged otherwise",
        "Six of the 15 cycle-only crossings are already flagged",
        float(conf["cycle_only_already_flagged_otherwise"]), 6)
    pin("5-second-only that would lose the flag",
        "three of the six 5-second-only crossings would lose their flag entirely",
        float(conf["five_second_only_would_lose_flag"]), 3)
    pin("counterfactual not_steady_state total", "from 530 to 536",
        float(conf["nss_locked"]) * 1e4 + conf["nss_counterfactual"], 530e4 + 536)
    pin("counterfactual increase", "an increase of 1.1~\\%",
        round(conf["nss_delta_pct"], 1), 1.1)

    pin("estimand: ratio of group medians, 5-second", "Ratio of group medians & 21.42",
        round(float(est.loc["ratio_of_group_medians", "five_second"]), 2), 21.42)
    # Corrected 2026-09-12 from the published 22.67. The re-derived ratio is
    # 0.337324964932 / 0.0148831730646 = 22.66485537, which displays as 22.66;
    # 22.67 came from rounding once to three decimals (22.665) and again to
    # two. Register: audit/s033_estimand_rounding_mismatch.md (now CLOSED).
    pin("estimand: ratio of group medians, cycle", "21.42 & 22.66",
        round(float(est.loc["ratio_of_group_medians", "cycle_resolved"]), 2), 22.66)
    pin("estimand: median of paired ratios, 5-second", "Median of paired ratios & 27.84",
        round(float(est.loc["median_of_paired_ratios", "five_second"]), 2), 27.84)
    pin("estimand: median of paired ratios, cycle", "27.84 & 25.63",
        round(float(est.loc["median_of_paired_ratios", "cycle_resolved"]), 2), 25.63)
    pin("estimand: difference of group medians, 5-second",
        "Difference of group medians & 0.3345",
        round(float(est.loc["difference_of_group_medians", "five_second"]), 4), 0.3345)
    pin("estimand: difference of group medians, cycle", "0.3345 & 0.3224",
        round(float(est.loc["difference_of_group_medians", "cycle_resolved"]), 4), 0.3224)
    pin("estimand: median of paired differences, 5-second",
        "Median of paired differences & 0.3256",
        round(float(est.loc["median_of_paired_differences", "five_second"]), 4), 0.3256)
    pin("estimand: median of paired differences, cycle", "0.3256 & 0.3275",
        round(float(est.loc["median_of_paired_differences", "cycle_resolved"]), 4), 0.3275)

    # Two quantities, two comparisons -- see the note on injectivity above.
    gaps = est["relative_gap_pct"]
    add_row("relative-gap range",
            "`relative gap ranges from 0.6~\\% to 8.6~\\%` -- artefact: "
            f"{round(float(gaps.min()), 1)} to {round(float(gaps.max()), 1)}",
            "relative gap ranges from 0.6~\\% to 8.6~\\%" in supp
            and round(float(gaps.min()), 1) == 0.6
            and round(float(gaps.max()), 1) == 8.6)
    n_over = int((est["cycle_resolved"] > est["five_second"]).sum())
    add_row("direction split is two against two",
            "`two summaries make the 5-second statistic overstate the effect and two make "
            f"it understate it` -- cycle-resolved is larger in {n_over} of {len(est)}",
            ("two summaries make the 5-second statistic overstate the effect and two make "
             "it understate it") in supp and n_over == 2 and len(est) == 4)

    add_row("configurations entering the estimands",
            f"`computed on the 63 configurations` -- artefact {est['n_configs'].unique().tolist()}",
            "computed on the 63 configurations" in supp
            and est["n_configs"].unique().tolist() == [63])
    add_row("caption denominator",
            "`the same 63 paired configurations (of 64)`",
            "the same 63 paired configurations (of 64)" in supp)

    # ---- layer 2: internal arithmetic ------------------------------------- #
    cells_sum = (conf["flagged_by_both"] + conf["flagged_by_neither"]
                 + conf["cycle_only"] + conf["five_second_only"])
    add_row("2x2 cells sum to the analysed runs",
            f"{cells_sum} vs {conf['n_runs_analysed']}",
            cells_sum == conf["n_runs_analysed"])
    add_row("agreement is the two concordant cells",
            f"{conf['flagged_by_both']} + {conf['flagged_by_neither']} = {conf['n_agree']}",
            conf["flagged_by_both"] + conf["flagged_by_neither"] == conf["n_agree"])
    net = ((conf["cycle_only"] - conf["cycle_only_already_flagged_otherwise"])
           - conf["five_second_only_would_lose_flag"])
    add_row("counterfactual delta equals gains minus losses",
            f"({conf['cycle_only']} - {conf['cycle_only_already_flagged_otherwise']}) - "
            f"{conf['five_second_only_would_lose_flag']} = {net} vs {conf['nss_delta']}",
            net == conf["nss_delta"]
            and conf["nss_locked"] + net == conf["nss_counterfactual"])
    add_row("analysed runs plus runs without a CSV account for the sweep",
            f"{conf['n_runs_analysed']} + {conf['n_runs_without_csv']} = "
            f"{conf['n_runs_analysed'] + conf['n_runs_without_csv']} vs {conf['n_runs_total']}",
            conf["n_runs_analysed"] + conf["n_runs_without_csv"] == conf["n_runs_total"])
    add_row("native traces are sampled at exactly 50 Hz",
            f"{conf['native_sampling_hz_min']} to {conf['native_sampling_hz_max']} Hz; "
            "prose says `every 0.02~s (50~Hz)`",
            conf["native_sampling_hz_min"] == 50.0
            and conf["native_sampling_hz_max"] == 50.0
            and "every 0.02~s (50~Hz)" in supp)
    add_row("the 200-fold oversample follows from 50 Hz over 0.25 Hz",
            f"50 / 0.25 = {50.0 / 0.25:.0f}; prose says `200-fold oversampling`",
            abs(50.0 / 0.25 - 200.0) < 1e-9 and "200-fold oversampling" in supp)

    # ---- the segmentation limit and its sensitivity analysis -------------- #
    # Published 2026-09-12, after the re-derivation measured that the notebook's
    # "validated on three runs, within 7 %" was a favourable sample. Each figure
    # is pinned to the artefact rather than to the prose that quotes it.
    pin("limit: runs with a non-constant delivered volume",
        "Across the 1{,}251 runs whose delivered volume is not numerically constant",
        float(conf["cycle_count_vs_rr_n_runs"]), 1251)
    pin("limit: median cycle-count / respiration-rate disagreement",
        "agree to a median of 5.4~\\%",
        round(100.0 * conf["cycle_count_vs_rr_median_rel_err"], 1), 5.4)
    pin("limit: 95th percentile and maximum of that disagreement",
        "the 95th percentile of the disagreement is 38~\\% and the maximum 95~\\%",
        round(100.0 * conf["cycle_count_vs_rr_p95_rel_err"], 0) * 1e3
        + round(100.0 * conf["cycle_count_vs_rr_max_rel_err"], 0),
        38e3 + 95)
    pin("limit: runs past the 20 % disagreement cut",
        "Of the 126 runs that disagree by more than 20~\\%",
        float(conf["n_cycle_count_disagreement"]) * 1e3
        + round(100.0 * conf["rr_disagreement_cut"], 0),
        126e3 + 20)
    sa = conf["sensitivity_native_all"]
    mb = conf["merging_bias_direction"]
    add_row("limit: the four low-confidence verdict splits are all cycle-only",
            "`four are cycle-only crossings and none is a 5-second-only crossing` -- "
            f"artefact: {conf['n_cycle_count_disagreement_with_verdict_split']} split(s), "
            f"{conf['cycle_count_disagreement_verdict_split_runs']}",
            ("four are cycle-only crossings and none is a 5-second-only crossing" in supp)
            and conf["n_cycle_count_disagreement_with_verdict_split"] == 4
            and all(
                bool(per_run.loc[r, "flag_cycle"]) and not bool(per_run.loc[r, "flag_5s"])
                for r in conf["cycle_count_disagreement_verdict_split_runs"]
            ))
    pin("sensitivity: the 2x2 against the all-sample estimator",
        "agrees on 295 flagged and 945 unflagged runs, crosses the threshold alone on 12 "
        "and is crossed alone by the 5-second statistic on 8",
        float(sa["flagged_by_both"]) * 1e9 + sa["flagged_by_neither"] * 1e6
        + sa["native_only"] * 1e3 + sa["five_second_only"],
        295e9 + 945e6 + 12e3 + 8)
    pin("sensitivity: its agreement, against the published one",
        "(98.4~\\% agreement, versus 98.3~\\% above)",
        round(sa["pct_agree"], 1) * 1e3 + round(conf["pct_agree"], 1),
        98.4e3 + 98.3)
    pin("sensitivity: runs where the two cycle-level estimators differ",
        "disagrees with the change-point estimator on 9 of the 1{,}260 runs",
        float(sa["n_disagree_with_cycle_estimator"]) * 1e5 + conf["n_runs_analysed"],
        9e5 + 1260)
    # The direction of the merging bias. The first draft of this subsection
    # asserted that merging biases the statistic upward, reasoning that it
    # under-weights stability. Measured, it does not. These pins exist because
    # that sentence would otherwise have been published on an argument -- and
    # because the first de-noising filter written to measure it was itself
    # wrong (relative-only, so blind to two values that are both noise).
    mat = mb["material"]
    pin("bias direction: runs entering the comparison",
        "on the 1{,}250 runs whose two values differ by more than a relative $10^{-6}$",
        float(mat["n_runs"]), 1250)
    pin("bias direction: the larger side",
        "the change-point value is the larger on 640",
        float(mat["n_cycle_above_native"]), 640)
    pin("bias direction: the smaller side",
        "and the smaller on 610", float(mat["n_cycle_below_native"]), 610)
    pin("bias direction: median ratio of the two cycle-level estimators",
        "with a median ratio of 1.0005",
        round(mb["median_ratio_cycle_over_native_material"], 4), 1.0005)
    pin("bias direction: runs excluded as numerically identical",
        "the remaining ten, nine of them constant-volume runs, are identical to the "
        "precision of the trace",
        float(mb["n_below_cut"]) * 1e3 + conf["n_constant_volume"], 10e3 + 9)
    add_row("bias direction: the split accounts for every analysed run",
            f"{mat['n_runs']} compared + {mb['n_below_cut']} indistinguishable = "
            f"{mat['n_runs'] + mb['n_below_cut']} vs {conf['n_runs_analysed']}; "
            f"{mat['n_cycle_above_native']} + {mat['n_cycle_below_native']} + "
            f"{mat['n_tied']} = {mat['n_runs']}",
            mat["n_runs"] + mb["n_below_cut"] == conf["n_runs_analysed"]
            and mat["n_cycle_above_native"] + mat["n_cycle_below_native"]
            + mat["n_tied"] == mat["n_runs"])
    # Calibration of the de-noising filter, on the defect that motivated it:
    # every constant-volume run must fall below the cut, because there the only
    # difference between the two estimators is a ~1.8e-16 float residue. A
    # relative-only filter scored that residue as a 100 % difference and
    # excluded none of them.
    add_row("bias direction: the filter excludes every constant-volume run",
            f"{mb['n_constant_runs_excluded_by_cut']} of {mb['n_constant_runs']} "
            f"excluded; largest residue on those runs "
            f"{mb['max_float_residue_on_constant_runs']:.3g}",
            mb["n_constant_runs_excluded_by_cut"] == mb["n_constant_runs"]
            == conf["n_constant_volume"]
            and mb["max_float_residue_on_constant_runs"] < 1e-12)
    pin("sensitivity: the all-sample counterfactual, against the published one",
        "from 530 to 533, versus 530 to 536 above",
        float(sa["nss_counterfactual"]) * 1e4 + conf["nss_counterfactual"],
        533e4 + 536)
    add_row("sensitivity: the published counterfactual is the larger of the two",
            f"change-point +{conf['nss_delta']} vs all-sample +{sa['nss_delta']}; "
            "prose says it `overstates rather than understates`",
            conf["nss_delta"] > sa["nss_delta"]
            and "overstates rather than understates" in supp)
    add_row("sensitivity: the four cells sum to the analysed runs",
            f"{sa['flagged_by_both']} + {sa['flagged_by_neither']} + {sa['native_only']} + "
            f"{sa['five_second_only']} = "
            f"{sa['flagged_by_both'] + sa['flagged_by_neither'] + sa['native_only'] + sa['five_second_only']}"
            f" vs {conf['n_runs_analysed']}",
            sa["flagged_by_both"] + sa["flagged_by_neither"] + sa["native_only"]
            + sa["five_second_only"] == conf["n_runs_analysed"])
    add_row("the reworded caption no longer reads as group-against-group",
            "`Within each pair of summaries (the two ratio-based and the two "
            "difference-based rows), the summaries disagree` present; the old "
            "group-against-group wording absent",
            ("Within each pair of summaries (the two ratio-based and the two "
             "difference-based rows), the summaries disagree on which resolution "
             "overstates the effect") in supp
            and "The two rows built from ratios and the two built from differences disagree"
            not in supp)

    # ---- layer 3: cross-instrument, outside the s033 chain ---------------- #
    agg = pd.read_parquet(
        REPO / "data" / "runs" / "full_sweep" / "aggregated.parquet"
    ).set_index("case_id")
    joined = per_run.join(
        agg[["Vt_cv", "not_steady_state", "diverged", "sex"]], rsuffix="_agg"
    )
    # The artefact is a text file written at 12 significant digits, so equality
    # can only be asserted to that precision -- not to double precision. The
    # comparison therefore puts the stored parquet value through the same
    # formatting before comparing, which needs no epsilon at all. (Compared
    # raw, the two differ by up to 4.7e-12 on the largest CV in the sweep,
    # 1.8257, purely from the 13th significant digit the file does not carry.)
    # Compared on the decimal strings, not on parsed floats. Two routes to a
    # float cannot be required to agree bit-for-bit: pandas' C parser is not
    # correctly rounded, and it reads `8.79569357191e-12` back as
    # 8.795693571910001e-12 where `float()` gives 8.79569357191e-12 -- a
    # difference in the 16th significant digit of a CV that is numerically
    # zero. The string comparison needs no tolerance and tests exactly what
    # the artefact promises: the same 12 significant digits.
    cv_text = pd.read_csv(
        needed[3], usecols=["case_id", "cv_5s"], dtype={"cv_5s": str}
    ).set_index("case_id")["cv_5s"]
    expected_text = agg["Vt_cv"].reindex(cv_text.index).map(lambda v: "%.12g" % v)
    cv_bad = cv_text.index[cv_text != expected_text].tolist()
    max_delta = float((joined["cv_5s"] - joined["Vt_cv"]).abs().max())
    detail = ""
    if cv_bad:
        detail = " -- " + "; ".join(
            f"{cid}: artefact `{cv_text[cid]}` vs parquet `{expected_text[cid]}`"
            for cid in cv_bad[:4]
        )
    add_row("5-second column matches the stored `Vt_cv` (independent producer)",
            f"{len(cv_bad)} disagreement(s) over {len(cv_text)} runs, compared as "
            f"12-significant-digit decimals (parsed max |delta| = {max_delta:.3g})"
            f"{detail}",
            not cv_bad)
    nss_bad = int((joined["nss_locked"].astype(bool)
                   != joined["not_steady_state"].astype(bool)).sum())
    add_row("locked flag column matches the stored classification",
            f"{nss_bad} disagreement(s) over {len(joined)} runs",
            nss_bad == 0 and int(agg["not_steady_state"].sum()) == conf["nss_locked"])
    absent = sorted(set(agg.index) - set(per_run.index))
    add_row("runs absent from the artefact are exactly the stored diverged runs",
            f"{len(absent)} absent, {int(agg['diverged'].sum())} stored diverged",
            absent == sorted(agg.index[agg["diverged"]].tolist()))
    sex_counts = joined["sex_agg"].value_counts().to_dict()
    add_row("sex split of the analysed runs matches the sweep",
            f"{sex_counts} vs prose base of 640 female and 620 male",
            sex_counts == {"F": 640, "M": 620})

    # ---- controls ---------------------------------------------------------- #
    probe_ok = "1{,}239 of 1{,}260 runs" in supp
    add_row("positive control: the matcher finds a literal known to be present",
            "`1{,}239 of 1{,}260 runs` located" if probe_ok else "**not located**",
            probe_ok)
    probe_bad = "1{,}238 of 1{,}260 runs" not in supp
    add_row("negative control: an altered literal is rejected",
            "`1{,}238 of 1{,}260 runs` correctly absent" if probe_bad
            else "**a wrong literal matched**",
            probe_bad)

    print("| check | observed | verdict |")
    print("|---|---|---|")
    for label, observed, verdict in rows:
        print(f"| {label} | {observed} | {verdict} |")
    print(
        f"\n**S033 cycle-resolved guard:** {len(rows)} checks, "
        f"{len(rows) - n_bad} PASS, {n_bad} FAIL. "
        f"Artefacts from `scripts/s033_cycle_resolved_vtcv.py`; the 5-second column "
        f"and the locked flags are re-checked against `aggregated.parquet`.\n"
    )
    return n_bad


def check_s023_oos_table() -> int:
    """Every cell of Supplement S13's out-of-sample table, and its prose ranges.

    Added 2026-09-12, alongside `check_s033_cycle_resolved`, for the same
    reason: of the eighteen numbers in Table `tab:s13-oos`, only the six
    trajectory-grouped means were registered (anchors `T2.s023.r2_grouped_*`).
    The six training and six out-of-bag values, the six fold standard
    deviations, and the four ranges quoted in the surrounding prose were
    verified by nothing, and nothing said so.

    Scope, stated because it is narrower than the S033 guard's. Every value
    here comes from `results/s023/rf_metrics.csv`, which
    `scripts/shap_vs_morris_topk.py` writes; there is no second producer to
    compare against without retraining the forest. So this guard verifies that
    **the prose reports what the script computed**, not that the script
    implements the intended protocol -- the distinction that let the
    traffic-light deviation through a green ledger
    (`audit/preregistration_traffic_light_deviation.md` section 8.2).

    Two checks do reach outside that chain. The surrogate's training-set size
    is compared against the clean-subset count in
    `data/runs/full_sweep/aggregated.parquet`, which the S023 script did not
    write. And the six worst-fold values, which the notebook records as
    deliberately unpublished because `GroupKFold` yields one deterministic
    partition and so no bound, are checked to be absent from the supplement --
    a guard on a decision, which an anchor cannot express.
    """
    print("\n## S023 out-of-sample table guard (Supplement S13)\n")
    rows: list[tuple[str, str, str]] = []
    n_bad = 0

    def add_row(label: str, observed: str, ok: bool) -> None:
        nonlocal n_bad
        if not ok:
            n_bad += 1
        rows.append((label, observed, "PASS" if ok else "**FAIL**"))

    rf_path = REPO / "results" / "s023" / "rf_metrics.csv"
    if not rf_path.exists():
        add_row(f"`{rf_path.relative_to(REPO).as_posix()}` present", "**absent**", False)
        print("| check | observed | verdict |")
        print("|---|---|---|")
        for label, observed, verdict in rows:
            print(f"| {label} | {observed} | {verdict} |")
        print("\n**S023 out-of-sample guard:** 1 check, 0 PASS, 1 FAIL. Run "
              "`uv run python scripts/shap_vs_morris_topk.py`.\n")
        return 1

    rf = pd.read_csv(rf_path).set_index("output")
    supp = (REPO / "preprint_npj" / "supplement.tex").read_text(encoding="utf-8")

    # The published table, row by row: output, then the literal of each cell
    # exactly as `supplement.tex` renders it.
    published = [
        ("Vt", "Vt & 0.99997 & 0.9998 & 0.9995 $\\pm$ 0.0004", 0.99997, 0.9998, 0.9995, 0.0004),
        ("HR", "HR & 0.9995 & 0.9964 & 0.9917 $\\pm$ 0.0024", 0.9995, 0.9964, 0.9917, 0.0024),
        ("MAP", "MAP & 0.9993 & 0.9952 & 0.9402 $\\pm$ 0.0253", 0.9993, 0.9952, 0.9402, 0.0253),
        ("SpO2", "SpO$_2$ & 0.9941 & 0.9578 & 0.8736 $\\pm$ 0.0532",
         0.9941, 0.9578, 0.8736, 0.0532),
        ("PaCO2", "PaCO$_2$ & 0.9942 & 0.9601 & 0.8734 $\\pm$ 0.0705",
         0.9942, 0.9601, 0.8734, 0.0705),
        ("PaO2", "PaO$_2$ & 0.9930 & 0.9494 & 0.8716 $\\pm$ 0.0562",
         0.9930, 0.9494, 0.8716, 0.0562),
    ]
    for out, literal, p_train, p_oob, p_grp, p_sd in published:
        got = rf.loc[out]
        # Each cell is rendered at the precision the table uses, so the
        # comparison is on the displayed value, not on a tolerance band.
        mismatches = [
            f"{name} {shown!r} vs {round(float(got[col]), len(str(shown).split('.')[1]))!r}"
            for name, col, shown in (
                ("training", "r2_train", p_train),
                ("out-of-bag", "r2_oob", p_oob),
                ("grouped", "r2_grouped_cv", p_grp),
                ("sd", "r2_grouped_sd", p_sd),
            )
            if round(float(got[col]), len(str(shown).split(".")[1])) != shown
        ]
        found = literal in supp
        observed = f"`{out}` row located" if found else "**row literal not in supplement.tex**"
        if mismatches:
            observed += " -- " + "; ".join(mismatches)
        add_row(f"table row: {out}", observed, found and not mismatches)

    # ---- prose ranges, each the min/max of a column ----------------------- #
    def pin_range(label: str, literal: str, lo: float, hi: float,
                  lo_dp: int, hi_dp: int, got_lo: float, got_hi: float) -> None:
        found = literal in supp
        ok = round(got_lo, lo_dp) == lo and round(got_hi, hi_dp) == hi
        observed = f"`{literal}`" if found else "**not in supplement.tex**"
        if not ok:
            observed += (f" -- artefact gives {round(got_lo, lo_dp)!r} to "
                         f"{round(got_hi, hi_dp)!r}")
        add_row(label, observed, found and ok)

    pin_range("prose: training range", "training $R^{2}$ (0.993 to 0.99997)",
              0.993, 0.99997, 3, 5,
              float(rf["r2_train"].min()), float(rf["r2_train"].max()))
    pin_range("prose: out-of-bag range", "ranges from 0.949 to 0.9998",
              0.949, 0.9998, 3, 4,
              float(rf["r2_oob"].min()), float(rf["r2_oob"].max()))

    optimism = rf["r2_oob"] - rf["r2_grouped_cv"]
    gas = ["SpO2", "PaO2", "PaCO2"]
    pin_range("prose: out-of-bag optimism on the blood-gas channels",
              "most optimistic (by 0.078 to 0.087", 0.078, 0.087, 3, 3,
              float(optimism[gas].min()), float(optimism[gas].max()))
    add_row("prose: optimism on delivered Vt",
            "`against 0.0003 for delivered Vt` -- artefact "
            f"{round(float(optimism['Vt']), 4)!r}",
            "against 0.0003 for delivered Vt" in supp
            and round(float(optimism["Vt"]), 4) == 0.0003)
    add_row("prose: blood-gas channels average 0.87",
            f"artefact {round(float(rf.loc[gas, 'r2_grouped_cv'].mean()), 2)!r}",
            "The three blood-gas channels average 0.87" in supp
            and round(float(rf.loc[gas, "r2_grouped_cv"].mean()), 2) == 0.87)

    # The spread is a hedge, so it is checked for truth by containment, not
    # pinned to an exact figure: the measured spread ratios against heart rate
    # must all fall inside the stated interval. 2026-10-14 (supplement audit row
    # S13.6): the prose said "ten to thirty times larger" than Vt and HR together,
    # but against Vt's sd the ratios are 134-178; it now names heart rate, and the
    # interval is the measured 22-29 rounded out to [20, 30].
    ratios = (rf.loc[gas, "r2_grouped_sd"] / rf.loc["HR", "r2_grouped_sd"]).tolist()
    add_row("prose: spread `twenty to thirty times that of heart rate` contains the measured ratios",
            f"{[round(r, 1) for r in ratios]} against HR's sd, all within [20, 30]",
            "a fold-to-fold spread twenty to thirty times that of heart rate" in supp
            and all(20.0 <= r <= 30.0 for r in ratios))

    # ---- ordering the prose asserts --------------------------------------- #
    bad_order = [
        o for o in rf.index
        if not (rf.loc[o, "r2_train"] >= rf.loc[o, "r2_oob"] >= rf.loc[o, "r2_grouped_cv"])
    ]
    add_row("training >= out-of-bag >= trajectory-grouped, for every output",
            f"{len(rf)} outputs checked, {len(bad_order)} out of order"
            + (f": {bad_order}" if bad_order else ""),
            not bad_order)
    add_row("the table covers exactly the atlas's six output channels",
            f"{sorted(rf.index.tolist())}",
            sorted(rf.index.tolist()) == sorted(["HR", "MAP", "Vt", "SpO2", "PaO2", "PaCO2"]))

    # ---- outside the S023 chain ------------------------------------------- #
    agg = pd.read_parquet(REPO / "data" / "runs" / "full_sweep" / "aggregated.parquet")
    n_clean = int(agg["clean"].sum())
    n_train = sorted(set(int(v) for v in rf["n_train"]))
    add_row("surrogate training size equals the sweep's clean subset",
            f"rf_metrics n_train {n_train} vs aggregated.parquet clean {n_clean}",
            n_train == [n_clean])

    # ---- a guard on a decision, not on a number --------------------------- #
    # Matched with digit boundaries, not as a bare substring. A plain
    # `"0.999" in supp` is true inside `0.99997`, which made a first version of
    # this check report a leak that does not exist -- the instrument has to be
    # calibrated before its negative is believed.
    # Checked at four decimals only -- the precision Table `tab:s13-oos` uses,
    # and therefore the shape a leak would take. A first version also tested
    # three decimals and reported a leak that does not exist: Vt's worst fold
    # is 0.9989, which rounds to 0.999, and an unrelated SpO2 flatline
    # threshold of 0.999 appears in the caption of Table `tab:s22-nss`. A
    # coarser rendering than the one in use invents collisions.
    def leak_re(shown: str) -> str:
        return r"(?<![\d.])" + re.escape(shown) + r"(?![\d])"

    leaked = [
        f"{o} as `{v:.4f}`"
        for o, v in rf["r2_grouped_min"].items()
        if re.search(leak_re(f"{v:.4f}"), supp)
    ]
    add_row("the unpublished worst-fold column has not leaked into the supplement",
            f"6 values checked at the table's four decimals, {len(leaked)} present"
            + (f": {leaked}" if leaked else "")
            + ". GroupKFold gives one deterministic partition, so the worst fold "
              "is not a bound; recorded in the S033 notebook as deliberately withheld.",
            not leaked)
    # Calibration of that matcher, both directions, on this very document. The
    # negative probe is a strict PREFIX of a number the supplement does carry,
    # so a matcher without the digit boundary would wrongly accept it.
    probe = f"{rf.loc['Vt', 'r2_grouped_cv']:.4f}"  # 0.9995, published
    pos_leak = bool(re.search(leak_re(probe), supp))
    neg_leak = not re.search(leak_re("0.9999"), supp) and "0.9999" in supp
    add_row("leak matcher: finds a published value, and rejects a prefix of one",
            f"`{probe}` located: {pos_leak}; `0.9999` present as a substring of "
            f"`0.99997` yet correctly not matched: {neg_leak}",
            pos_leak and neg_leak)

    # ---- controls ---------------------------------------------------------- #
    pos = "Vt & 0.99997 & 0.9998 & 0.9995 $\\pm$ 0.0004" in supp
    add_row("positive control: the matcher finds a table row known to be present",
            "located" if pos else "**not located**", pos)
    neg = "Vt & 0.99997 & 0.9998 & 0.9995 $\\pm$ 0.0005" not in supp
    add_row("negative control: a row with one altered digit is rejected",
            "correctly absent" if neg else "**a wrong row matched**", neg)

    print("| check | observed | verdict |")
    print("|---|---|---|")
    for label, observed, verdict in rows:
        print(f"| {label} | {observed} | {verdict} |")
    print(
        f"\n**S023 out-of-sample guard:** {len(rows)} checks, "
        f"{len(rows) - n_bad} PASS, {n_bad} FAIL. Transcription and internal "
        f"consistency against `results/s023/rf_metrics.csv`; the training-set size "
        f"and the withheld worst-fold column are the two checks that reach outside "
        f"that producer.\n"
    )
    return n_bad


n_s033_fail = check_s033_cycle_resolved()

n_s023oos_fail = check_s023_oos_table()


# Grid shape for the Morris comparison, fixed by the design rather than by the
# artefact: 8 (scenario x sex) cells x 6 outputs = 48 rankings, and 318
# estimable (cell, output, input) triples under the locked screen, which is
# 6 inputs x 48 plus FiO2's 30. Both are asserted rather than read, so a
# regenerated artefact of the wrong shape fails instead of redefining the grid.
EXPECTED_S034_COMBINATIONS = 48
EXPECTED_S034_PUBLISHED_ROWS = 318


def check_s034_screen_sensitivity() -> int:
    """Every number of Supplement S13's screen-sensitivity subsection.

    Added 2026-09-12 with the subsection itself, so the figures are pinned from
    the day they are published rather than after someone asks -- the omission
    that produced the S033 debt two days earlier.

    Three layers, as for `check_s033_cycle_resolved`:

      * transcription -- the literal in `supplement.tex` or `paper.tex` equals
        the artefact;
      * arithmetic -- the artefact's own totals close, so a partial
        regeneration cannot pass;
      * cross-instrument -- the seed comparator is read from
        `results/phase4b_top3_comparison_seed44.csv`, which S034 did not write,
        and the calibration figures are checked against
        `results/morris_indices.parquet`, the published artefact.

    The strongest control is in the producer, not here: the S034 script aborts
    unless recomputing under the locked screen reproduces the published mu* on
    all 318 rows to double precision. This guard records that it did.
    """
    print("\n## S034 screen-sensitivity guard (Supplement S13, Morris ranks)\n")
    rows: list[tuple[str, str, str]] = []
    n_bad = 0

    d = REPO / "results" / "s034"
    needed = [d / "s034_summary.json", d / "rank_comparison.csv", d / "mu_star_by_screen.csv"]
    missing = [p for p in needed if not p.exists()]
    if missing:
        print("| check | observed | verdict |")
        print("|---|---|---|")
        for p in missing:
            print(f"| `{p.relative_to(REPO).as_posix()}` present | **absent** | **FAIL** |")
        print(
            f"\n**S034 screen-sensitivity guard:** {len(missing)} checks, 0 PASS, "
            f"{len(missing)} FAIL. Run "
            "`uv run python scripts/s034_morris_screen_sensitivity.py`.\n"
        )
        return len(missing)

    s = json.loads(needed[0].read_text(encoding="utf-8"))
    comp = pd.read_csv(needed[1])
    supp = (REPO / "preprint_npj" / "supplement.tex").read_text(encoding="utf-8")
    paper = (REPO / "preprint_npj" / "paper.tex").read_text(encoding="utf-8")

    def add_row(label: str, observed: str, ok: bool) -> None:
        nonlocal n_bad
        if not ok:
            n_bad += 1
        rows.append((label, observed, "PASS" if ok else "**FAIL**"))

    def pin(label: str, literal: str, value: float, published: float, doc: str = "supp") -> None:
        text = supp if doc == "supp" else paper
        found = literal in text
        agrees = abs(value - published) <= 5e-10
        observed = f"`{literal}`" + ("" if found else f" **not in {doc}**")
        if not agrees:
            observed += f" -- artefact gives {value!r}, prose says {published!r}"
        add_row(label, observed, found and agrees)

    # ---- layer 1: transcription, the two screens ------------------------- #
    pin("runs and pairs under the locked screen",
        "keeps 663 of the 1{,}280 runs and 454 of the 1{,}120 available pairs",
        float(s["n_runs_clean_screen"]) * 1e10 + s["distinct_pairs_clean"] * 1e5
        + s["distinct_pairs_ceiling"],
        663e10 + 454e5 + 1120)
    pin("runs and pairs under the relaxed screen",
        "1{,}134 runs and 969 pairs",
        float(s["n_runs_hard_failure_free"]) * 1e5 + s["distinct_pairs_hff"],
        1134e5 + 969)
    pin("elementary-effect observations gained, and the S1 share",
        "of the 3{,}090 additional elementary-effect observations, 1{,}152 fall in Healthy",
        float(s["ee_observation_gain"]) * 1e5 + s["ee_observation_gain_by_scenario"]["S1"],
        3090e5 + 1152)

    h1c, h1h = s["h1_by_screen"]["clean"], s["h1_by_screen"]["hff"]
    add_row("H1 holds in all 48 combinations under both screens",
            f"clean {h1c['n_pass']}/{h1c['n_combinations']}, "
            f"relaxed {h1h['n_pass']}/{h1h['n_combinations']}; prose says "
            "`holds in all 48 cell $\\times$ output combinations under both screens`",
            ("holds in all 48 cell $\\times$ output combinations under "
             "both screens") in supp
            and h1c["n_pass"] == h1c["n_combinations"] == EXPECTED_S034_COMBINATIONS
            and h1h["n_pass"] == h1h["n_combinations"] == EXPECTED_S034_COMBINATIONS)
    pin("H1 range and median under the locked screen",
        "0.658 to 0.998 of the summed $\\mu^{*}$ under the locked screen (median 0.928)",
        round(h1c["fraction_min"], 3) * 1e8 + round(h1c["fraction_max"], 3) * 1e4
        + round(h1c["fraction_median"], 3),
        0.658e8 + 0.998e4 + 0.928)
    pin("H1 range and median under the relaxed screen",
        "0.695 to 0.994 under the relaxed one (median 0.901)",
        round(h1h["fraction_min"], 3) * 1e8 + round(h1h["fraction_max"], 3) * 1e4
        + round(h1h["fraction_median"], 3),
        0.695e8 + 0.994e4 + 0.901)

    same = s["criteria_identical_candidate_set_only"]
    allc = s["criteria_all_combinations"]
    pin("rank-1 unchanged on every like-for-like combination",
        "unchanged in all 30 combinations whose candidate set is the same under both screens",
        float(same["top1_preserved"]) * 1e4 + same["n"], 30e4 + 30)
    pin("combinations that gain a seventh candidate",
        "18 of the 48 combinations gain a seventh candidate",
        float(s["n_combinations_total"] - s["n_combinations_candidate_set_identical"]) * 1e4
        + s["n_combinations_total"],
        18e4 + 48)
    pin("top-three set and order on the like-for-like subset",
        "the top-three \\emph{set} is preserved in 19 and its \\emph{order} in 15",
        float(same["top3_set_preserved"]) * 1e4 + same["top3_order_preserved"],
        19e4 + 15)
    pin("the three criteria over all 48 combinations",
        "the figures are 41, 26 and 21",
        float(allc["top1_preserved"]) * 1e8 + allc["top3_set_preserved"] * 1e4
        + allc["top3_order_preserved"],
        41e8 + 26e4 + 21)

    narrow = s["criteria_narrow_cut_margin"]
    pin("the third/fourth gap, median and narrow count",
        "39~\\% of the third under the locked screen, and only one of the 30 combinations "
        "has a gap below 10~\\%",
        round(100.0 * s["median_cut_margin_clean"], 0) * 1e4 + narrow["n"] * 1e2
        + round(100.0 * s["narrow_cut"], 0),
        39e4 + 1e2 + 10)

    s2m = s["criteria_S2_M_only"]
    pin("the screen's effect on S2_M, the seed comparator's cell",
        "the screen change preserves 6, 2 and 2 on the same outputs",
        float(s2m["top1_preserved"]) * 1e8 + s2m["top3_set_preserved"] * 1e4
        + s2m["top3_order_preserved"],
        6e8 + 2e4 + 2)

    # ---- layer 2: arithmetic --------------------------------------------- #
    add_row("the like-for-like subset plus the candidate-changed ones is the whole grid",
            f"{s['n_combinations_candidate_set_identical']} + "
            f"{s['n_combinations_total'] - s['n_combinations_candidate_set_identical']} = "
            f"{s['n_combinations_total']}",
            s["n_combinations_total"] == EXPECTED_S034_COMBINATIONS
            and len(comp) == EXPECTED_S034_COMBINATIONS)
    add_row("every candidate change is FiO2 gained, in the three cells the paper names",
            "gains: "
            + ", ".join(sorted({r["cell"] for r in s["combinations_with_candidate_change"]}))
            + "; inputs gained: "
            + ", ".join(sorted({r["inputs_gained"] for r in s["combinations_with_candidate_change"]}))
            + "; none lost"
            if s["combinations_with_candidate_change"] else "none",
            sorted({r["cell"] for r in s["combinations_with_candidate_change"]})
            == ["S1_F", "S1_M", "S4_F"]
            and {r["inputs_gained"] for r in s["combinations_with_candidate_change"]} == {"fio2"}
            and all(not r["inputs_lost"] for r in s["combinations_with_candidate_change"]))
    add_row("estimable triples grow by exactly the three cells times six outputs",
            f"{s['estimable_triples_clean']} -> {s['estimable_triples_hff']} "
            f"(+{s['estimable_triples_hff'] - s['estimable_triples_clean']}, expected +18)",
            s["estimable_triples_hff"] - s["estimable_triples_clean"] == 18
            and s["estimable_triples_clean"] == EXPECTED_S034_PUBLISHED_ROWS)
    add_row("distinct pairs are the observation counts divided by the six outputs",
            f"{s['ee_observations_clean']} / {s['n_outputs']} = {s['distinct_pairs_clean']}, "
            f"{s['ee_observations_hff']} / {s['n_outputs']} = {s['distinct_pairs_hff']}",
            s["ee_observations_clean"] == s["distinct_pairs_clean"] * s["n_outputs"]
            and s["ee_observations_hff"] == s["distinct_pairs_hff"] * s["n_outputs"])
    add_row("the relaxed screen is a superset: no combination loses pairs",
            f"{int((comp['n_pairs_hff'] < comp['n_pairs_clean']).sum())} combination(s) lose pairs",
            int((comp["n_pairs_hff"] < comp["n_pairs_clean"]).sum()) == 0)

    # ---- layer 3: outside the S034 chain --------------------------------- #
    seed_path = REPO / "results" / "phase4b_top3_comparison_seed44.csv"
    if seed_path.exists():
        seed = pd.read_csv(seed_path)
        # ⚠️ Corrected 2026-09-13 after an ultrareview finding. The first version
        # pinned `len(seed)` -- the number of ROWS, 6 -- against "preserves the
        # rank-1 input in 6 of its 6 outputs". That counts outputs, not rank-1
        # agreements: a regenerated artefact with a moved rank-1 input would have
        # kept the guard green as long as it kept six rows. It also trusted the
        # precomputed same_set / same_order columns. All three counts are now
        # re-derived from the top-three lists themselves, compared one quantity
        # at a time, and the precomputed columns are checked against them.
        def _top3(cell: str) -> list[str]:
            return re.findall(r"'([^']+)'", str(cell))

        canon = seed["canon_top3"].map(_top3)
        new = seed["new_top3"].map(_top3)
        n_out = len(seed)
        rank1 = sum(1 for a, b in zip(canon, new) if a[:1] == b[:1] and a)
        same_set_re = [set(a) == set(b) for a, b in zip(canon, new)]
        same_order_re = [a == b for a, b in zip(canon, new)]
        lit = ("preserves the rank-1 input in all 6 outputs, the top-three set "
               "in 4 and its order in 3")
        found = lit in supp
        add_row("the seed comparator, read from the phase-4b artefact",
                f"`{lit}`" + ("" if found else " **not in supp**")
                + f" -- artefact: rank-1 {rank1} of {n_out}, set {sum(same_set_re)}, "
                  f"order {sum(same_order_re)}",
                found and n_out == 6 and rank1 == 6
                and sum(same_set_re) == 4 and sum(same_order_re) == 3)
        cols_agree = (
            [bool(x) for x in seed["same_set"]] == same_set_re
            and [bool(x) for x in seed["same_order"]] == same_order_re
            and all(len(a) == 3 and len(b) == 3 for a, b in zip(canon, new))
        )
        add_row("the artefact's precomputed same_set / same_order match its own lists",
                "recomputed from canon_top3 and new_top3, each list of length 3: "
                + ("agree" if cols_agree else "**disagree**"),
                cols_agree)
    else:
        add_row("the seed comparator artefact is present",
                f"`{seed_path.relative_to(REPO).as_posix()}` absent", False)

    pub = pd.read_parquet(REPO / "results" / "morris_indices.parquet")
    add_row("the calibration the producer ran: published rows reproduced, mu* identical",
            f"{s['n_published_rows_reproduced']} of {len(pub)} rows, max |delta| = "
            f"{s['calibration_max_abs_mu_star_delta_vs_published']:.3g}; "
            f"producer reported {len(s['calibration_problems'])} problem(s)",
            s["n_published_rows_reproduced"] == len(pub) == EXPECTED_S034_PUBLISHED_ROWS
            and s["calibration_max_abs_mu_star_delta_vs_published"] == 0.0
            and not s["calibration_problems"])

    # ---- the paper's two sentences --------------------------------------- #
    # The denominator is named in the sentence on purpose. Its first version
    # read "changes in about a third of them", whose nearest plural antecedent
    # is "all 48 combinations" -- a reading under which the fraction is wrong
    # (22 of 48 is 46 %, not a third). Naming the 30 and giving the raw count
    # removes the ambiguity instead of relying on the intended reading.
    # Re-registered 2026-09-23 after an author-approved readability rewrite: the
    # sentence names both screens (a bare "both screens" left the first one
    # unnamed) and glosses "candidate set", as the producer defines it (s034:
    # set of inputs carrying a mu*, i.e. at least one retained pair). Same day,
    # re-registered again when the paper's five screen names were cut to the two
    # 2.1 defines: "four-flag" and "hard-failure-free" (the relaxed screen keeps
    # the same 1,134 runs). The three raw counts and their denominator are
    # unchanged.
    # Re-registered 2026-10-06 (M. Sauthier review round, author decision D31):
    # "under both screens" again, now unambiguous because 2.1 and Table 3 define
    # exactly two screens. The three raw counts and their denominator are unchanged.
    _paper_claim = (
        "H1 holds in all 48 combinations under both screens. In the 30 combinations "
        "whose candidate set (the inputs with at least one retained pair) is the same "
        "under both screens, the rank-1 input is preserved in all 30, whereas ranks "
        "two and three change in 11"
    )
    add_row("paper: the pointer, its denominator and its raw counts",
            f"`{_paper_claim[:60]}...` present in paper.tex; artefact: "
            f"{same['n']} like-for-like, {same['top1_preserved']} rank-1 preserved, "
            f"{same['n'] - same['top3_set_preserved']} sets changed",
            _paper_claim in paper
            and same["n"] == 30
            and same["top1_preserved"] == 30
            and same["n"] - same["top3_set_preserved"] == 11)
    add_row("paper: the vague fraction it replaced is gone",
            "`changes in about a third of them` correctly absent -- its nearest "
            "antecedent was the 48, where the true figure is 22 of 48",
            "changes in about a third of them" not in paper)
    add_row("paper caption: FiO2 is rank-1 for PaO2 and SpO2 in all three white-cell cells",
            "`estimable in all three and is then the rank-1 input for PaO$_2$ and SpO$_2$` "
            "present; artefact: "
            + ", ".join(
                f"{r['cell']}/{r['output']}"
                for r in comp[(~comp["top1_preserved"]) & (comp["top1_hff"] == "fio2")]
                .to_dict(orient="records")
            ),
            ("estimable in all three and is then the rank-1 input for PaO$_2$ and SpO$_2$")
            in paper
            and sorted(
                (r["cell"], r["output"])
                for r in comp[(~comp["top1_preserved"]) & (comp["top1_hff"] == "fio2")]
                .to_dict(orient="records")
            )
            == [("S1_F", "PaO2"), ("S1_F", "SpO2"), ("S1_M", "PaO2"),
                ("S1_M", "SpO2"), ("S4_F", "PaO2"), ("S4_F", "SpO2")])

    # ---- controls --------------------------------------------------------- #
    probe_ok = "1{,}134 runs and 969 pairs" in supp
    add_row("positive control: the matcher finds a literal known to be present",
            "`1{,}134 runs and 969 pairs` located" if probe_ok else "**not located**", probe_ok)
    probe_bad = "1{,}134 runs and 968 pairs" not in supp
    add_row("negative control: an altered literal is rejected",
            "`1{,}134 runs and 968 pairs` correctly absent" if probe_bad
            else "**a wrong literal matched**", probe_bad)

    print("| check | observed | verdict |")
    print("|---|---|---|")
    for label, observed, verdict in rows:
        print(f"| {label} | {observed} | {verdict} |")
    print(
        f"\n**S034 screen-sensitivity guard:** {len(rows)} checks, "
        f"{len(rows) - n_bad} PASS, {n_bad} FAIL. Artefacts from "
        f"`scripts/s034_morris_screen_sensitivity.py`; the seed comparator and the "
        f"published indices are read from artefacts it did not write.\n"
    )
    return n_bad


n_s034_fail = check_s034_screen_sensitivity()


def check_window_tolerance() -> int:
    """No analysis script may select a time window with a strict comparison.

    Added 2026-09-01, after the defect it detects was found for the second time.
    The recorded time grid drifts: a nominal t = 120 s is stored as
    120.0000000000557 and a nominal t = 240 s as 239.99999999996928. A strict
    `lo <= t <= hi` therefore silently drops one sample, so a window documented
    as 60 s carries 12 samples instead of the 13 the preregistration fixes at
    L58, L83, L84, L116 and L135, and makes an explicit failure condition at
    L191.

    It has bitten twice. `scripts/analyze_s030.py` first, diagnosed 2026-08-13,
    when the same nominal window held 12 samples in S030 and 13 in the main
    sweep; the epsilon was then adopted as the atlas rule but only S030 was
    migrated. Then S021, found 2026-09-01: the drift fit ran on 12 points, one
    run crossed the 15 mmHg/60 s threshold, and two published anchors were wrong
    (T1.24 93.2 % and T1.24b 41 of 44, corrected to 90.9 % and 40 of 44).
    `scripts/provenance_check.py` carried it too, and reported FAIL on faithful
    reproductions in 98 % of runs on the I:E ratio.

    A one-off repair does not stop a third occurrence; this does.
    """
    print("\n## Window-tolerance guard (no strict time-window comparison)\n")
    rows: list[tuple[str, str, str]] = []
    n_bad = 0

    # A comparison of time_s against a bound, capturing what follows the operator
    # up to the closing bracket, so the tolerance term is visible if present.
    cmp_re = re.compile(r"time_s\"?\]?\s*(>=|<=)\s*([^)&\]]+)")
    tol_tokens = ("1e-6", "1e-9", "TIME_SLACK", "slack", "SLACK", "EPS", "eps")

    # This file is excluded: it is the guard, and the strings it matches on are
    # its own pattern and its own negative control, not a window selection.
    files = sorted(
        [p for p in (REPO / "scripts").glob("*.py") if p.name != "audit_claims.py"]
        + [p for p in (REPO / "src").glob("*.py")]
    )
    scanned, with_window = 0, 0
    for path in files:
        text = path.read_text(encoding="utf-8")
        scanned += 1
        hits = list(cmp_re.finditer(text))
        if not hits:
            continue
        with_window += 1
        strict = [m for m in hits if not any(t in m.group(2) for t in tol_tokens)]
        rel = path.relative_to(REPO).as_posix()
        if strict:
            n_bad += 1
            sample = strict[0].group(0).strip()[:60]
            rows.append((f"`{rel}`",
                         f"**{len(strict)} strict of {len(hits)}** e.g. `{sample}`",
                         "**FAIL**"))
        else:
            rows.append((f"`{rel}`", f"{len(hits)} comparison(s), all tolerant",
                         "PASS"))

    # Calibration. A finder that matches nothing would report a clean sweep, so
    # the instrument is checked on a file known to carry the pattern, and on a
    # synthetic strict line that it must reject.
    det = (REPO / "src" / "detector.py").read_text(encoding="utf-8")
    pos_ok = len(list(cmp_re.finditer(det))) > 0
    n_bad += 0 if pos_ok else 1
    rows.append(("positive control: the finder sees `src/detector.py`",
                 f"{len(list(cmp_re.finditer(det)))} comparison(s) found",
                 "PASS" if pos_ok else "**FAIL**"))
    probe = 'df[(df["time_s"] >= lo) & (df["time_s"] <= hi)]'
    probe_hits = list(cmp_re.finditer(probe))
    neg_ok = len(probe_hits) == 2 and all(
        not any(t in m.group(2) for t in tol_tokens) for m in probe_hits)
    n_bad += 0 if neg_ok else 1
    rows.append(("negative control: a synthetic strict line is rejected",
                 "flagged" if neg_ok else "**missed**",
                 "PASS" if neg_ok else "**FAIL**"))

    print("| check | observed | verdict |")
    print("|---|---|---|")
    for label, observed, verdict in rows:
        print(f"| {label} | {observed} | {verdict} |")
    print(
        f"\n**Window-tolerance guard:** {len(rows)} checks, "
        f"{len(rows) - n_bad} PASS, {n_bad} FAIL. "
        f"{scanned} files scanned, {with_window} carry a time-window comparison.\n"
    )
    return n_bad


n_windowtol_fail = check_window_tolerance()

n_sobolframe_fail = check_sobol_framing()


# Prose-audit guard (2026-09-19, register audit/number_inventory.md 12.4).
#
# The hole this closes. The prose audit enumerated the sentences that assert
# something absolute while carrying no digit -- the one population neither
# number instrument could ever show -- and found four claims stronger than
# their own evidence. Each was corrected on the author's decision. Nothing else
# in the gate would notice if one came back: these are words, not numbers, so
# no inventory, residue or ledger anchor covers them, which is precisely how
# they survived until 2026-09-19.
#
# Two directions, as in the Sobol guard above: the over-claim coming back is
# one failure mode, the repaired wording quietly disappearing in a later
# condensation pass is the other. P-1 in particular sits in an abstract that is
# AT the npj 150-word cap, so it is the first clause a word-hunting edit
# reaches.
#
# Calibrated 2026-09-19 in both directions, whitespace-normalised: each retired
# phrase matches at d0406cf (the commit before the corrections) and none
# matches now; each required phrase matches now.
PROSE_AUDIT_DOCS = ("preprint_npj/paper.tex", "preprint_npj/supplement.tex",
                    "preprint/manuscript.md")

PROSE_RETIRED_PHRASES: tuple[tuple[str, str], ...] = (
    # P-1: unhedged, unattributed universal negative over the literature, in the
    # abstract, while L144 hedged it and L327 attributed it.
    ("yet no formal sensitivity analysis of its operational inputs has been published",
     "d0406cf"),
    # M-1: bold lead-in asserting as fact what its own bullet hedged 7 lines down.
    ("**No comparable open atlas exists for sibling engines.**", "d0406cf"),
    # M-2: "exactly" claims both directions of an envelope probed on one side
    # only (Vt and PEEP edges were never probed); the monograph's own 2.2 says
    # the seven ranges sit INSIDE it.
    ("*exactly* the ranges Pulse will accept", "d0406cf"),
    # M-2: a universal over future users and unsampled points, from 10,160
    # contracts at the sampled points.
    ("never trigger silent substitution", "d0406cf"),
    # M-3: larger than the 9-run acceptance probe it cites, and contradicted by
    # the monograph's own 3.8 solver-instability tail at that same setting.
    ("remains fully stable up to FiO2 = 1.0", "d0406cf"),
    # P-2 (2026-09-21, author's reading): "ventilating an impaired lung is a
    # main use of Pulse's respiratory model" carried no citation and asserted
    # relative importance that nothing measures. What the repository actually
    # sources about Pulse's uses points elsewhere -- education and
    # simulation-training integrations (pulseinaction), with an explicit note
    # that only the NAMED integrations are cited. The sentence's job is to
    # justify centring on ARDS, and its second half already does that, so the
    # claim was replaced by a verifiable one rather than hedged.
    ("a main use of Pulse", "b8ae590"),
)

PROSE_REQUIRED_PHRASES: tuple[tuple[str, str], ...] = (
    ("preprint_npj/paper.tex",
     "yet its maintainers report no formal sensitivity analysis of its operational inputs"),
    ("preprint/manuscript.md",
     "To our knowledge, no comparable open atlas exists for sibling engines"),
    ("preprint/manuscript.md",
     "all sit inside the ranges Pulse accepts without intervention"),
    ("preprint/manuscript.md",
     "was silently substituted anywhere in this sweep"),
    ("preprint/manuscript.md",
     "produces a stable trajectory; the transient hyperoxia regime and the "
     "extended-window solver-instability tail"),
    ("preprint_npj/paper.tex",
     "Pulse models mechanical ventilation of an impaired lung"),
)


def check_prose_audit() -> int:
    """Hold the four prose-audit corrections, in both directions.

    Whitespace-normalised before matching: the monograph hard-wraps, and three
    of these phrases span a line break in the very revision that created them.
    A raw line scan would report a false PASS on the retired side and a false
    FAIL on the required side -- both in the direction that hides the defect.

    A missing document is a FAIL, never a skip.
    """
    print("\n## Prose-audit guard "
          "(paper abstract, monograph 4.5 / 3.4 / Appendix B.2)\n")
    rows: list[tuple[str, str, str]] = []
    n_bad = 0

    def record(label: str, observed: object, ok: bool) -> None:
        nonlocal n_bad
        n_bad += 0 if ok else 1
        rows.append((label, str(observed), "PASS" if ok else "**FAIL**"))

    texts: dict[str, str | None] = {}
    for rel in PROSE_AUDIT_DOCS:
        path = REPO / rel
        if not path.is_file():
            texts[rel] = None
            record(f"document {rel}", "ABSENT", False)
        else:
            texts[rel] = " ".join(path.read_text(encoding="utf-8").split())

    for phrase, calibrated_at in PROSE_RETIRED_PHRASES:
        hits = [rel for rel, t in texts.items() if t is not None and phrase in t]
        record(f"retired `{phrase[:52]}` (matched at {calibrated_at})",
               ", ".join(hits) if hits else "absent from all three",
               not hits)

    for rel, phrase in PROSE_REQUIRED_PHRASES:
        text = texts.get(rel)
        present = text is not None and phrase in text
        record(f"{rel} still states `{phrase[:44]}`",
               "present" if present else "ABSENT", present)

    print("| check | observed | verdict |")
    print("|---|---|---|")
    for label, observed, verdict in rows:
        print(f"| {label} | {observed} | {verdict} |")
    print(
        f"\n**Prose-audit guard:** {len(rows)} checks, "
        f"{len(rows) - n_bad} PASS, {n_bad} FAIL.\n"
    )
    return n_bad


n_prose_fail = check_prose_audit()

n_counter_fail = 0
if _ARGS.check_paper_sync and _ARGS.check_monograph:
    n_counter_fail = check_audit_counters(
        n_expected,
        n_sync_pass + n_sync_warn + n_sync_fail,
        n_mono_pass + n_mono_warn + n_mono_fail,
    )

# Exit non-zero if any FAIL anywhere (allows piping to CI later).
sys.exit(
    1
    if (
        n_fail + n_sync_fail + n_mono_fail + n_counter_fail
        + n_s021_fail + n_s021_conv_fail + n_readme_fail + n_legend_fail
        + n_sexdiv_fail + n_inst_fail + n_cliprt_fail + n_s030prov_fail + n_figts_fail
        + n_fio2adj_fail + n_sobolframe_fail + n_s011_fail + n_abstract_fail
        + n_vtcv_split_fail + n_shap_unit_fail + n_detvocab_fail + n_cdcprov_fail + n_pubgate_fail
        + n_windowtol_fail + n_s033_fail + n_s023oos_fail + n_s034_fail + n_contband_fail
        + n_followup_fail + n_smallaudit_fail + n_monoaudit_fail + n_prose_fail
    ) > 0
    else 0
)
