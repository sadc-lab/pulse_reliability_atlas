"""Audit tool: is a paired cross-body re-analysis feasible, and on what subset?

Strictly descriptive. This script runs NO hypothesis test -- no permutation, no
Wilcoxon, no Wasserstein, no multiplicity correction. It answers one question:
for each scenario, which Morris configurations are flag-clean on BOTH reference
bodies, and what does that paired subset still represent?

Motivation. paper.tex section 2.5 states that separating the physiological
effect from the flag-filter effect "would require a design in which both bodies
retain the same grid points and receive matched relative ventilation doses".
That sentence promised a design without establishing that one exists or how
large it is. This script measures it.

Everything is rebuilt from the run-level artefacts in data/runs/full_sweep/,
above both results/cell_flag_summary.csv and results/reliability_classification.csv,
because those are outputs of the aggregation chain rather than independent
evidence. The published per-cell clean counts are then compared against the
reconstruction as a cross-check.

Reference-body constants are read from src/scenario.py and the tidal-volume
range from src/sampler.py, so editing either makes this audit fail rather than
silently invalidating the numbers recorded in audit/paired_design_feasibility.md.

Usage:  uv run python scripts/audit_paired_design_feasibility.py
Exits non-zero on any assertion failure.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
SWEEP = REPO / "data" / "runs" / "full_sweep"
PUBLISHED_FLAGS = REPO / "results" / "cell_flag_summary.csv"

INPUTS = ["in_hr", "in_rr", "in_sbp", "in_dbp", "in_vt", "in_fio2", "in_peep"]
SCENARIOS = ["S1", "S2", "S3", "S4"]
SEXES = ["M", "F"]

GRID_POINTS_PER_CELL = 160
CM_PER_INCH = 2.54

# Values recorded in audit/paired_design_feasibility.md on 2026-08-04. They are
# asserted, not recomputed-and-trusted: if the sweep data or the detector ever
# changes, this script must fail loudly rather than quietly report new numbers.
EXPECTED_CLEAN = {
    ("S1", "M"): 49, ("S1", "F"): 42,
    ("S2", "M"): 87, ("S2", "F"): 92,
    ("S3", "M"): 144, ("S3", "F"): 122,
    ("S4", "M"): 67, ("S4", "F"): 60,
}
EXPECTED_CLEAN_TOTAL = 663
EXPECTED_INTERSECTION = {"S1": 34, "S2": 69, "S3": 111, "S4": 51}
# Scenarios where the paired subset loses FiO2 levels entirely, and which ones.
EXPECTED_FIO2_TRUNCATION = {"S1": "upper half absent", "S4": "lower half absent"}


def _read_source_constant(rel_path: str, pattern: str, what: str) -> re.Match[str]:
    text = (REPO / rel_path).read_text(encoding="utf-8")
    match = re.search(pattern, text)
    assert match is not None, f"audit_paired: {what} not located in {rel_path}"
    return match


def reference_bodies() -> dict[str, dict[str, float]]:
    """Weight, height and Pulse ideal body weight for each reference body.

    Ideal body weight is Pulse's own quantity, computed at patient setup by the
    sex-specific Devine relation in SetupPatient.cpp:136-146 (imperial form):
        male    IBW_kg = 50.0 + 2.3 * (height_in - 60)
        female  IBW_kg = 45.5 + 2.3 * (height_in - 60)
    It is deliberately NOT called "ARDSnet predicted body weight": the metric
    coefficients usually attributed to that protocol could not be verified
    against an accessible primary source (see audit/reference_audit.md Phase 5).
    """
    bodies: dict[str, dict[str, float]] = {}
    for sex in SEXES:
        m = _read_source_constant(
            "src/scenario.py",
            rf'"{sex}":\s*Patient\([^)]*?weight_kg=([\d.]+),\s*height_cm=([\d.]+)',
            f"reference body {sex!r}",
        )
        weight_kg, height_cm = float(m.group(1)), float(m.group(2))
        intercept = 50.0 if sex == "M" else 45.5
        bodies[sex] = {
            "weight_kg": weight_kg,
            "height_cm": height_cm,
            "ibw_kg": intercept + 2.3 * (height_cm / CM_PER_INCH - 60.0),
        }
    return bodies


def swept_vt_range() -> tuple[float, float]:
    m = _read_source_constant(
        "src/sampler.py", r'InputSpec\("vt",\s*([\d.]+),\s*([\d.]+)', "Vt InputSpec"
    )
    return float(m.group(1)), float(m.group(2))


def load_cells() -> dict[tuple[str, str], pd.DataFrame]:
    cells: dict[tuple[str, str], pd.DataFrame] = {}
    for scenario in SCENARIOS:
        for sex in SEXES:
            path = SWEEP / f"{scenario}_{sex}" / "aggregated.parquet"
            frame = pd.read_parquet(path)
            frame["key"] = list(map(tuple, frame[INPUTS].round(6).to_numpy()))
            cells[(scenario, sex)] = frame
    return cells


def check_grid_identity(cells: dict[tuple[str, str], pd.DataFrame]) -> set[tuple]:
    """The design claims one 160-point Morris grid, executed in all eight cells."""
    reference = set(cells[("S1", "M")]["key"])
    assert len(reference) == GRID_POINTS_PER_CELL, (
        f"audit_paired: S1_M holds {len(reference)} distinct input vectors, "
        f"expected {GRID_POINTS_PER_CELL}"
    )
    print("== Design premise: one Morris grid, eight cells ==")
    for (scenario, sex), frame in cells.items():
        keys = set(frame["key"])
        assert len(frame) == GRID_POINTS_PER_CELL, (
            f"audit_paired: {scenario}_{sex} has {len(frame)} runs"
        )
        assert keys == reference, (
            f"audit_paired: {scenario}_{sex} input grid differs from S1_M"
        )
        print(f"  {scenario}_{sex}: {len(keys)} distinct vectors, identical to S1_M")
    return reference


def check_clean_counts(cells: dict[tuple[str, str], pd.DataFrame]) -> None:
    """Reconstructed clean counts must match both the expectation and the artefact."""
    published = pd.read_csv(PUBLISHED_FLAGS).set_index(["scenario", "sex"])["n_clean"]
    print("\n== Clean-run counts: rebuilt from run level vs published artefact ==")
    total = 0
    for scenario in SCENARIOS:
        for sex in SEXES:
            rebuilt = int(cells[(scenario, sex)]["clean"].sum())
            total += rebuilt
            expected = EXPECTED_CLEAN[(scenario, sex)]
            from_csv = int(published.loc[(scenario, sex)])
            assert rebuilt == expected, (
                f"audit_paired: {scenario}_{sex} clean={rebuilt}, expected {expected}"
            )
            assert rebuilt == from_csv, (
                f"audit_paired: {scenario}_{sex} clean={rebuilt} but "
                f"cell_flag_summary.csv says {from_csv}"
            )
            print(f"  {scenario}_{sex}: rebuilt {rebuilt:3d} == published {from_csv:3d}")
    assert total == EXPECTED_CLEAN_TOTAL, (
        f"audit_paired: total clean={total}, expected {EXPECTED_CLEAN_TOTAL}"
    )
    print(f"  total: {total} clean runs of {GRID_POINTS_PER_CELL * 8}")


def intersections(cells: dict[tuple[str, str], pd.DataFrame]) -> dict[str, set[tuple]]:
    """Configurations flag-clean on BOTH bodies, per scenario, with bound checks."""
    print("\n== Paired subset: configurations clean on both bodies ==")
    header = (
        f"{'scen':5s} {'cleanM':>7s} {'cleanF':>7s} {'paired':>7s} "
        f"{'M only':>7s} {'F only':>7s} {'bounds':>12s}"
    )
    print(header)
    paired: dict[str, set[tuple]] = {}
    for scenario in SCENARIOS:
        male = set(cells[(scenario, "M")].loc[cells[(scenario, "M")]["clean"], "key"])
        female = set(cells[(scenario, "F")].loc[cells[(scenario, "F")]["clean"], "key"])
        both = male & female
        paired[scenario] = both
        low = max(0, len(male) + len(female) - GRID_POINTS_PER_CELL)
        high = min(len(male), len(female))
        assert low <= len(both) <= high, (
            f"audit_paired: {scenario} paired={len(both)} outside [{low}, {high}]"
        )
        assert len(both) == EXPECTED_INTERSECTION[scenario], (
            f"audit_paired: {scenario} paired={len(both)}, "
            f"expected {EXPECTED_INTERSECTION[scenario]}"
        )
        assert len(both) + len(male - female) == len(male)
        assert len(both) + len(female - male) == len(female)
        print(
            f"{scenario:5s} {len(male):7d} {len(female):7d} {len(both):7d} "
            f"{len(male - female):7d} {len(female - male):7d} "
            f"{f'[{low}, {high}]':>12s}"
        )
    return paired


def input_levels(
    cells: dict[tuple[str, str], pd.DataFrame], paired: dict[str, set[tuple]]
) -> None:
    """Which swept levels of each input still appear in the paired subset.

    This reports LEVEL PRESENCE only. It does not demonstrate balanced
    combinatorial coverage: 34 paired points cannot span a 7-input grid.
    """
    print("\n== Input levels present in the paired subset (present / swept) ==")
    print("   level presence only -- NOT a claim of balanced combinatorial coverage")
    grid = cells[("S1", "M")]
    swept = {col: sorted(grid[col].round(6).unique()) for col in INPUTS}
    print(f"{'scen':5s} " + " ".join(f"{c.removeprefix('in_'):>9s}" for c in INPUTS))
    for scenario in SCENARIOS:
        subset = grid[grid["key"].isin(paired[scenario])]
        row = f"{scenario:5s} "
        for col in INPUTS:
            row += f"{len(subset[col].round(6).unique()):4d}/{len(swept[col]):<4d} "
        print(row)

    print("\n== FiO2 truncation in the paired subset ==")
    for scenario in SCENARIOS:
        subset = grid[grid["key"].isin(paired[scenario])]
        counts = subset["in_fio2"].round(4).value_counts()
        full = grid["in_fio2"].round(4).value_counts()
        absent = [lvl for lvl in sorted(full.index) if int(counts.get(lvl, 0)) == 0]
        detail = ", ".join(
            f"{lvl:g}: {int(counts.get(lvl, 0))}/{int(full[lvl])}"
            for lvl in sorted(full.index)
        )
        note = f"  <-- {EXPECTED_FIO2_TRUNCATION[scenario]}" if absent else ""
        print(f"  {scenario}: {detail}{note}")
        if scenario in EXPECTED_FIO2_TRUNCATION:
            assert len(absent) == 2, (
                f"audit_paired: {scenario} expected 2 absent FiO2 levels, got {absent}"
            )
        else:
            assert not absent, f"audit_paired: {scenario} unexpectedly lost {absent}"


def ventilation_dose(
    cells: dict[tuple[str, str], pd.DataFrame],
    paired: dict[str, set[tuple]],
    bodies: dict[str, dict[str, float]],
) -> None:
    """Relative ventilation dose inside the paired subset, per body and normaliser."""
    vt_min, vt_max = swept_vt_range()
    grid = cells[("S1", "M")]
    print("\n== Ventilation dose inside the paired subset ==")
    print(
        f"{'scen':5s} {'n':>4s} {'Vt abs':>10s} "
        f"{'M mL/kg act':>12s} {'F mL/kg act':>12s} "
        f"{'M mL/kg IBW':>12s} {'F mL/kg IBW':>12s}"
    )
    for scenario in SCENARIOS:
        subset = grid[grid["key"].isin(paired[scenario])]
        vt = subset["in_vt"]
        assert vt.min() == vt_min and vt.max() == vt_max, (
            f"audit_paired: {scenario} paired Vt spans {vt.min()}-{vt.max()}, "
            f"expected the full swept range {vt_min}-{vt_max}"
        )
        cols = []
        for sex in SEXES:
            cols.append(f"{vt.min() / bodies[sex]['weight_kg']:.1f}-"
                        f"{vt.max() / bodies[sex]['weight_kg']:.1f}")
        for sex in SEXES:
            cols.append(f"{vt.min() / bodies[sex]['ibw_kg']:.1f}-"
                        f"{vt.max() / bodies[sex]['ibw_kg']:.1f}")
        print(
            f"{scenario:5s} {len(subset):4d} {f'{vt.min():.0f}-{vt.max():.0f}':>10s} "
            + " ".join(f"{c:>12s}" for c in cols)
        )
    excess_actual = bodies["M"]["weight_kg"] / bodies["F"]["weight_kg"] - 1.0
    excess_ideal = bodies["M"]["ibw_kg"] / bodies["F"]["ibw_kg"] - 1.0
    print(
        f"  female excess per kg at any matched absolute setting: "
        f"{excess_actual:.1%} actual weight, {excess_ideal:.1%} ideal weight"
    )


def failure_modes(
    cells: dict[tuple[str, str], pd.DataFrame], paired: dict[str, set[tuple]]
) -> None:
    """Why each non-shared configuration failed, in the body that lost it."""
    print("\n== Why configurations are not shared ==")
    print("   'clean in M only' -> the failure mode is in F, and vice versa")
    for scenario in SCENARIOS:
        male = set(cells[(scenario, "M")].loc[cells[(scenario, "M")]["clean"], "key"])
        female = set(cells[(scenario, "F")].loc[cells[(scenario, "F")]["clean"], "key"])
        for label, lost_keys, blamed in (
            ("clean in M only, failure mode in F", male - female, "F"),
            ("clean in F only, failure mode in M", female - male, "M"),
        ):
            frame = cells[(scenario, blamed)]
            subset = frame[frame["key"].isin(lost_keys)]
            modes = ", ".join(
                f"{flag}={int(subset[flag].sum())}"
                for flag in ("diverged", "implausible", "not_steady_state")
            )
            print(f"  {scenario} {label} (n={len(lost_keys):3d}): {modes}")


def main() -> int:
    bodies = reference_bodies()
    cells = load_cells()
    check_grid_identity(cells)
    check_clean_counts(cells)
    paired = intersections(cells)
    input_levels(cells, paired)
    ventilation_dose(cells, paired, bodies)
    failure_modes(cells, paired)
    print(
        "\nReference bodies: "
        + "; ".join(
            f"{sex} {b['weight_kg']} kg / {b['height_cm']:.0f} cm / "
            f"IBW {b['ibw_kg']:.2f} kg"
            for sex, b in bodies.items()
        )
    )
    print("\nNo hypothesis test was run. Descriptive counts only.")
    print("All assertions passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
