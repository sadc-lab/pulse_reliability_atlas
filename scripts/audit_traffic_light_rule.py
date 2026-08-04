"""Audit tool: rebuild the traffic-light classification from run-level data.

This script exists to close a structural blind spot. The ledger anchors T1.25,
T1.26 and T1.27 verify the published 7 / 29 / 12 distribution against
results/reliability_classification.csv -- the artefact the implemented rule
produced. They therefore confirm that the paper reports what the code computed;
they cannot confirm that the code implements the preregistered protocol.

Here every classification is rebuilt from the eight per-cell
aggregated.parquet files, and three rules are applied to the same rebuilt
inputs:

  implemented   red   if hard-flag rate > 30 % or deviation > 30 %
                yellow if deviation > 10 % or hard-flag rate > 0
                green  otherwise
                (src/analysis_compare.py:240-244)

  literal-hard  red   if deviation > 30 % or the cell carries any diverged /
                      implausible run
                green  if deviation < 10 % and not red
                yellow otherwise
                (preregistration.md:193, reading "any flag" as the two hard flags)

  literal-four  as above, but "any flag" spans all four flags, including
                not_steady_state and clamped

"Deviation" is the fractional distance of a cell's clean-run mean from the
clean-run mean of the healthy-male (S1, M) cell, per output.

Descriptive only: no hypothesis test, no permutation, no correction. Findings
are recorded in audit/preregistration_traffic_light_deviation.md.

Usage:  uv run python scripts/audit_traffic_light_rule.py
Exits non-zero on any assertion failure.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
SWEEP = REPO / "data" / "runs" / "full_sweep"
PUBLISHED = REPO / "results" / "reliability_classification.csv"

SCENARIOS = ["S1", "S2", "S3", "S4"]
SEXES = ["M", "F"]
# The six tracked steady-state outputs. Declared here rather than imported from
# src/analysis_compare.py so that this audit does not depend on the module it audits.
OUTPUTS = ["HR", "MAP", "Vt", "SpO2", "PaO2", "PaCO2"]

HARD_FLAGS = ["diverged", "implausible"]
ALL_FLAGS = ["clamped", "diverged", "implausible", "not_steady_state"]

DEVIATION_GREEN = 0.1
DEVIATION_RED = 0.3
HARD_RATE_RED = 0.3

# Recorded in audit/preregistration_traffic_light_deviation.md on 2026-08-04.
EXPECTED = {
    "implemented": {"green": 7, "yellow": 29, "red": 12},
    "literal-hard": {"green": 7, "yellow": 3, "red": 38},
    "literal-four": {"green": 0, "yellow": 0, "red": 48},
}
EXPECTED_YELLOW_TO_RED = 26


def load_cells() -> dict[tuple[str, str], pd.DataFrame]:
    cells = {}
    for scenario in SCENARIOS:
        for sex in SEXES:
            frame = pd.read_parquet(SWEEP / f"{scenario}_{sex}" / "aggregated.parquet")
            for output in OUTPUTS:
                assert f"{output}_mean" in frame.columns, (
                    f"audit_tl: {output}_mean missing from {scenario}_{sex}"
                )
            cells[(scenario, sex)] = frame
    return cells


def cell_statistics(cells: dict[tuple[str, str], pd.DataFrame]) -> pd.DataFrame:
    """Per (scenario, sex, output): clean-run mean, deviation, and flag rates."""
    reference = cells[("S1", "M")]
    baselines = {
        output: float(reference.loc[reference["clean"], f"{output}_mean"].mean())
        for output in OUTPUTS
    }
    for output, value in baselines.items():
        assert pd.notna(value) and value != 0, f"audit_tl: baseline for {output} is {value}"

    rows = []
    for (scenario, sex), frame in cells.items():
        n_total = len(frame)
        hard = int(frame[HARD_FLAGS].any(axis=1).sum())
        anyflag = int(frame[ALL_FLAGS].any(axis=1).sum())
        for output in OUTPUTS:
            mean_clean = float(frame.loc[frame["clean"], f"{output}_mean"].mean())
            rows.append(
                {
                    "scenario": scenario,
                    "sex": sex,
                    "output": output,
                    "mean_clean": mean_clean,
                    "deviation": abs(mean_clean - baselines[output]) / abs(baselines[output]),
                    "hard_rate": hard / n_total,
                    "hard_any": hard > 0,
                    "anyflag_any": anyflag > 0,
                }
            )
    return pd.DataFrame(rows)


def check_no_boundary_ties(stats: pd.DataFrame) -> None:
    """The two rules differ on whether the 10 % / 30 % bounds are inclusive.

    If no cell sits exactly on a bound, that difference cannot change any
    verdict, and the comparison below is about the rules rather than about a
    tie-breaking convention.
    """
    for bound in (DEVIATION_GREEN, DEVIATION_RED):
        ties = stats[stats["deviation"] == bound]
        assert ties.empty, f"audit_tl: {len(ties)} cells sit exactly on the {bound} bound"
    print("No cell sits exactly on the 10 % or 30 % bound; "
          "inclusive-versus-strict conventions cannot change any verdict.")


def classify(row: pd.Series, rule: str) -> str:
    if rule == "implemented":
        if row["hard_rate"] > HARD_RATE_RED or row["deviation"] > DEVIATION_RED:
            return "red"
        if row["deviation"] > DEVIATION_GREEN or row["hard_rate"] > 0.0:
            return "yellow"
        return "green"
    flagged = row["hard_any"] if rule == "literal-hard" else row["anyflag_any"]
    if row["deviation"] > DEVIATION_RED or flagged:
        return "red"
    if row["deviation"] < DEVIATION_GREEN:
        return "green"
    return "yellow"


def main() -> int:
    cells = load_cells()
    stats = cell_statistics(cells)
    assert len(stats) == 48, f"audit_tl: {len(stats)} cell-output combinations, expected 48"
    check_no_boundary_ties(stats)

    for rule in EXPECTED:
        stats[rule] = stats.apply(classify, axis=1, rule=rule)

    print("\n== Three rules applied to the same run-level reconstruction ==")
    print(f"{'rule':14s} {'green':>6s} {'yellow':>7s} {'red':>5s}")
    for rule, expected in EXPECTED.items():
        counts = stats[rule].value_counts()
        got = {c: int(counts.get(c, 0)) for c in ("green", "yellow", "red")}
        assert got == expected, f"audit_tl: {rule} gives {got}, expected {expected}"
        print(f"{rule:14s} {got['green']:6d} {got['yellow']:7d} {got['red']:5d}")

    # The published artefact must agree with the implemented rule, rebuilt here.
    published = pd.read_csv(PUBLISHED).set_index(["scenario", "sex", "output"])["light"]
    mismatches = [
        (r.scenario, r.sex, r.output, r.implemented, published.loc[(r.scenario, r.sex, r.output)])
        for r in stats.itertuples()
        if r.implemented != published.loc[(r.scenario, r.sex, r.output)]
    ]
    assert not mismatches, f"audit_tl: rebuilt vs published disagree on {mismatches}"
    print(f"\nRebuilt implemented rule matches results/reliability_classification.csv "
          f"on all {len(stats)} combinations.")

    green_impl = set(
        stats.loc[stats["implemented"] == "green", ["scenario", "sex", "output"]]
        .itertuples(index=False, name=None)
    )
    green_lit = set(
        stats.loc[stats["literal-hard"] == "green", ["scenario", "sex", "output"]]
        .itertuples(index=False, name=None)
    )
    assert green_impl == green_lit, "audit_tl: the green set is not invariant"
    print(f"\nGreen set is invariant across both non-degenerate rules "
          f"({len(green_impl)} combinations):")
    for scenario, sex, output in sorted(green_impl):
        print(f"  {scenario}_{sex} {output}")

    red_impl = stats["implemented"] == "red"
    red_lit = stats["literal-hard"] == "red"
    assert (red_impl & ~red_lit).sum() == 0, (
        "audit_tl: some implemented-red combination is not red under the literal rule"
    )
    moved = stats[(stats["implemented"] == "yellow") & red_lit]
    assert len(moved) == EXPECTED_YELLOW_TO_RED, (
        f"audit_tl: {len(moved)} yellow->red transitions, expected {EXPECTED_YELLOW_TO_RED}"
    )
    print(f"\n== {len(moved)} combinations yellow (implemented) -> red (literal-hard) ==")
    for (scenario, sex), group in moved.groupby(["scenario", "sex"], sort=True):
        outputs = ", ".join(sorted(group["output"], key=OUTPUTS.index))
        print(f"  {scenario}_{sex} ({len(group)}): {outputs}")
    print("  every one sits in a cell carrying at least one diverged/implausible run")

    print("\nNo hypothesis test was run. Classification counts only.")
    print("All assertions passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
