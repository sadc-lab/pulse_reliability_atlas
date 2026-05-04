"""S015 P1.4 — regenerate analysis artifacts from existing CSVs and compare
to committed artifacts WITHOUT overwriting them.

Strategy
--------
For each committed artifact under ``data/runs/*/aggregated.parquet`` and
``results/*``, regenerate the same artifact from raw inputs (per-run CSVs
+ logs + configs, OR the master parquet for downstream artifacts) using
the *current* ``src/`` code, write to ``data/audit_S015/``, and compare
column-by-column to the committed file. Numbers are compared with a
small tolerance (1e-9) to absorb harmless floating-point reordering.

Scope (only artifacts with a deterministic regeneration path):
  - data/runs/full_sweep/aggregated.parquet
  - results/morris_indices.parquet
  - results/h1_top3_fraction.csv
  - results/sobol_promotion.csv
  - results/cell_flag_summary.csv
  - results/wasserstein_male_vs_female.csv
  - results/spearman_mu_star.csv
  - results/clamp_grid.parquet
  - results/diverged_grid.parquet
  - results/reliability_classification.csv

Out of scope here (regenerate separately if needed):
  - S009 continuous-ARDS / seed-stability artifacts (different sweeps)
  - S011 sex-vs-mass artifacts (different design matrix)
  - S012 audit CSVs (script ``s012_steady_state_audit.py``)
  - S014 trigger-lockout (script ``run_s014_trigger_lockout.py``)

Output
------
Prints one section per artifact:
  [PASS] artifact: rows match, columns overlap match (tol=1e-9)
  [DRIFT] artifact: list of mismatched columns / rows
  [ADD]   artifact: extra columns in regenerated file (additive drift)
  [MISS]  artifact: missing columns in regenerated file
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from src.aggregator import aggregate_under  # noqa: E402
from src.analysis_compare import (  # noqa: E402
    cell_flag_summary,
    flag_count_grid,
    reliability_classification,
    spearman_mu_star_male_vs_female,
    wasserstein_per_output,
)
from src.analysis_morris import (  # noqa: E402
    evaluate_h1,
    morris_indices,
    sobol_promotion,
)
from src.scenario import iter_cells  # noqa: E402

SWEEP = REPO / "data" / "runs" / "full_sweep"
RESULTS = REPO / "results"
AUDIT = REPO / "data" / "audit_S015"
AUDIT.mkdir(parents=True, exist_ok=True)

TOL_ABS = 1e-9
TOL_REL = 1e-9


def _load(p: Path) -> pd.DataFrame:
    if p.suffix == ".parquet":
        return pd.read_parquet(p)
    return pd.read_csv(p)


def _save(df: pd.DataFrame, p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.suffix == ".parquet":
        df.to_parquet(p, index=False)
    else:
        df.to_csv(p, index=False)


def _series_equal(a: pd.Series, b: pd.Series) -> tuple[bool, str]:
    """Compare two series; return (match, reason_if_not)."""
    if a.dtype.kind in "fc" and b.dtype.kind in "fc":
        ma = a.to_numpy()
        mb = b.to_numpy()
        nan_a = np.isnan(ma)
        nan_b = np.isnan(mb)
        if not np.array_equal(nan_a, nan_b):
            return False, "NaN positions differ"
        ok = nan_a | np.isclose(ma, mb, atol=TOL_ABS, rtol=TOL_REL)
        if not ok.all():
            bad = np.where(~ok)[0]
            return False, f"{bad.size} value mismatches; first at row {bad[0]}: {ma[bad[0]]} vs {mb[bad[0]]}"
        return True, ""
    if a.equals(b):
        return True, ""
    diff_idx = (a != b)
    if diff_idx.any():
        i = int(np.where(diff_idx.to_numpy())[0][0])
        return False, f"{int(diff_idx.sum())} value mismatches; first at row {i}: {a.iloc[i]!r} vs {b.iloc[i]!r}"
    return True, ""


def compare(name: str, committed: pd.DataFrame, regen: pd.DataFrame, sort_by: list[str] | None = None) -> dict:
    """Compare two DataFrames on overlapping columns."""
    out = {"name": name, "rows_committed": len(committed), "rows_regen": len(regen)}

    if sort_by:
        keep = [c for c in sort_by if c in committed.columns and c in regen.columns]
        if keep:
            committed = committed.sort_values(keep).reset_index(drop=True)
            regen = regen.sort_values(keep).reset_index(drop=True)

    cols_c = set(committed.columns)
    cols_r = set(regen.columns)
    extra = sorted(cols_r - cols_c)
    missing = sorted(cols_c - cols_r)
    overlap = sorted(cols_c & cols_r)

    out["extra_in_regen"] = extra
    out["missing_in_regen"] = missing

    if len(committed) != len(regen):
        out["status"] = "ROW_COUNT_MISMATCH"
        return out

    drift_cols: list[tuple[str, str]] = []
    for c in overlap:
        ok, reason = _series_equal(committed[c], regen[c])
        if not ok:
            drift_cols.append((c, reason))

    out["drift_cols"] = drift_cols
    if drift_cols:
        out["status"] = "DRIFT"
    elif extra or missing:
        out["status"] = "ADDITIVE_OK"
    else:
        out["status"] = "EXACT"
    return out


def report(r: dict) -> None:
    name = r["name"]
    s = r["status"]
    print(f"\n[{s}] {name}")
    print(f"   rows: committed={r['rows_committed']}  regen={r['rows_regen']}")
    if r.get("extra_in_regen"):
        print(f"   extra cols in regen: {r['extra_in_regen']}")
    if r.get("missing_in_regen"):
        print(f"   missing cols in regen: {r['missing_in_regen']}")
    for c, why in r.get("drift_cols", []):
        print(f"   DRIFT {c}: {why}")


def regen_aggregated() -> pd.DataFrame:
    """Re-aggregate every per-run dir under full_sweep using the current detector."""
    cells = sorted([p for p in SWEEP.iterdir() if p.is_dir()])
    rows: list[pd.DataFrame] = []
    for cell_dir in cells:
        rows.append(aggregate_under(cell_dir))
    return pd.concat(rows, ignore_index=True)


def main() -> int:
    print("=" * 70)
    print("S015 P1.4 — regenerate-and-compare audit")
    print(f"  REPO:    {REPO}")
    print(f"  audit:   {AUDIT}")
    print(f"  tol:     atol={TOL_ABS}, rtol={TOL_REL}")
    print("=" * 70)

    results: list[dict] = []

    # 1. full_sweep/aggregated.parquet
    print("\n[1/8] full_sweep/aggregated.parquet — re-aggregating from per-run CSVs ...")
    committed = _load(SWEEP / "aggregated.parquet")
    regen = regen_aggregated()
    _save(regen, AUDIT / "full_sweep_aggregated.parquet")
    r = compare("data/runs/full_sweep/aggregated.parquet", committed, regen, sort_by=["case_id"])
    report(r); results.append(r)

    master = regen.copy()
    sample = pd.read_parquet(SWEEP / "morris_sample.parquet")
    cells = list(iter_cells())
    scenarios = sorted({sk for sk, _ in cells})

    # 2. cell_flag_summary
    print("\n[2/8] results/cell_flag_summary.csv — regenerating ...")
    committed = _load(RESULTS / "cell_flag_summary.csv")
    regen = cell_flag_summary(master)
    _save(regen, AUDIT / "cell_flag_summary.csv")
    r = compare("results/cell_flag_summary.csv", committed, regen, sort_by=["scenario", "sex"])
    report(r); results.append(r)

    # 3. morris_indices (with default seed/n_bootstrap that analyze_sweep.py uses)
    print("\n[3/8] results/morris_indices.parquet — regenerating (block bootstrap, seed=12345, B=1000) ...")
    committed = _load(RESULTS / "morris_indices.parquet")
    regen = morris_indices(master, sample, cells, n_bootstrap=1000)
    _save(regen, AUDIT / "morris_indices.parquet")
    r = compare("results/morris_indices.parquet", committed, regen, sort_by=["scenario", "sex", "output", "input"])
    report(r); results.append(r)

    morris_for_downstream = regen

    # 4. h1_top3_fraction
    print("\n[4/8] results/h1_top3_fraction.csv — regenerating ...")
    committed = _load(RESULTS / "h1_top3_fraction.csv")
    regen = evaluate_h1(morris_for_downstream)
    _save(regen, AUDIT / "h1_top3_fraction.csv")
    r = compare("results/h1_top3_fraction.csv", committed, regen, sort_by=["scenario", "sex", "output"])
    report(r); results.append(r)

    # 5. sobol_promotion
    print("\n[5/8] results/sobol_promotion.csv — regenerating ...")
    committed = _load(RESULTS / "sobol_promotion.csv")
    regen = sobol_promotion(morris_for_downstream)
    _save(regen, AUDIT / "sobol_promotion.csv")
    r = compare("results/sobol_promotion.csv", committed, regen, sort_by=["scenario", "sex", "output", "input"])
    report(r); results.append(r)

    # 6. wasserstein_male_vs_female
    print("\n[6/8] results/wasserstein_male_vs_female.csv — regenerating ...")
    committed = _load(RESULTS / "wasserstein_male_vs_female.csv")
    regen = wasserstein_per_output(master, scenarios)
    _save(regen, AUDIT / "wasserstein_male_vs_female.csv")
    r = compare("results/wasserstein_male_vs_female.csv", committed, regen, sort_by=["scenario", "output"])
    report(r); results.append(r)

    # 7. spearman_mu_star
    print("\n[7/8] results/spearman_mu_star.csv — regenerating ...")
    committed = _load(RESULTS / "spearman_mu_star.csv")
    regen = spearman_mu_star_male_vs_female(morris_for_downstream, scenarios)
    _save(regen, AUDIT / "spearman_mu_star.csv")
    r = compare("results/spearman_mu_star.csv", committed, regen, sort_by=["scenario", "output"])
    report(r); results.append(r)

    # 8. clamp_grid + diverged_grid + reliability_classification
    print("\n[8/8] heatmaps + reliability_classification — regenerating ...")
    committed = _load(RESULTS / "clamp_grid.parquet")
    regen = flag_count_grid(master, "clamped")
    _save(regen, AUDIT / "clamp_grid.parquet")
    r = compare("results/clamp_grid.parquet", committed, regen)
    report(r); results.append(r)

    committed = _load(RESULTS / "diverged_grid.parquet")
    regen = flag_count_grid(master, "diverged")
    _save(regen, AUDIT / "diverged_grid.parquet")
    r = compare("results/diverged_grid.parquet", committed, regen)
    report(r); results.append(r)

    committed = _load(RESULTS / "reliability_classification.csv")
    regen = reliability_classification(master)
    _save(regen, AUDIT / "reliability_classification.csv")
    r = compare("results/reliability_classification.csv", committed, regen, sort_by=["scenario", "sex"])
    report(r); results.append(r)

    # Final summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    by_status: dict[str, list[str]] = {}
    for r in results:
        by_status.setdefault(r["status"], []).append(r["name"])
    for s, names in sorted(by_status.items()):
        print(f"  {s:>22s}: {len(names):2d} artifact(s)")
        for n in names:
            print(f"     - {n}")

    drift_count = len(by_status.get("DRIFT", []))
    return 1 if drift_count > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
