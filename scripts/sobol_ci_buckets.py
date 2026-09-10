"""Ratio-aware bootstrap on the Morris sigma/mu* ratio, and the Sobol trigger buckets.

Why this script exists
----------------------
The preregistered Sobol bolt-on (``preregistration.md`` Sec. Sampling method)
promotes an input to variance decomposition when its ``sigma / mu*`` ratio
reaches 0.6. The rule is stated on the **top-three** mu*-ranked inputs of each
(scenario, sex, output) cell, and it conditions on the **point** ratio: the
preregistration attaches no bootstrap, confidence interval or uncertainty
qualifier of any kind.

Everything this script computes beyond the point-estimate trigger is therefore a
**post-hoc sensitivity analysis**, and the manuscript labels it as such.

Two confidence-interval formulas are possible on a ratio, and they do not agree:

1. ``sigma_hi / mu_hat*`` -- bootstrap sigma alone, divide by a fixed mu*.
   This ignores the positive covariance between sigma and mu*, which widens the
   interval in an uncontrolled direction. It is the historical variant; it was
   used for the buckets published up to S030 and is reproduced here as
   ``legacy_*`` columns so the older numbers stay checkable.
2. ``quantiles of sigma_b / mu*_b`` -- resample trajectories and recompute the
   ratio **jointly** on each draw, so the interval covers the quantity of
   interest. This is what the manuscript now adopts (S031).

Because a single bootstrap draw is itself noisy, a combination is only reported
as non-linear when its lower bound clears 0.6 under **every** seed in ``SEEDS``.
The union across seeds is deliberately *not* reported in the manuscript: it
tracks sampling noise (it moves with the resample count) rather than physiology.

Outputs
-------
- ``results/sobol_ci_buckets.csv``   one row per (scenario, sex, output, input)
  that is in the top three of its cell, with both CI formulas and the per-seed
  verdicts.
- ``results/sobol_ci_buckets.json``  the aggregate counts the manuscript quotes,
  so ``scripts/audit_claims.py`` can re-derive them without re-running the
  bootstrap.

Usage::

    uv run python scripts/sobol_ci_buckets.py

Runtime is a few minutes: len(SEEDS) x 318 combinations x N_BOOTSTRAP resamples.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.analysis_morris import compute_ee_for_cell, derive_trajectory_pairs  # noqa: E402
from src.scenario import case_id  # noqa: E402

RAW_DIR = REPO_ROOT / "data" / "runs" / "full_sweep"
RESULTS_DIR = REPO_ROOT / "results"

# Preregistered promotion threshold and gray-zone floor (preregistration.md).
PROMOTE_THRESHOLD = 0.6
SKIP_THRESHOLD = 0.4
TOP_K = 3

# Post-hoc bootstrap settings. N_BOOTSTRAP matches the mu*-CI setting used by
# morris_indices() so a single resample count appears throughout the manuscript.
# The stable set is identical at 1,000 / 2,000 / 4,000 (one combination is lost
# at 500); see the sensitivity clause in Supplement Sec. S3-sobol.
N_BOOTSTRAP = 1000
SEEDS = (12345, 999, 7, 555, 20260729)
ALPHA = 0.05

CELLS = [(s, x) for s in ("S1", "S2", "S3", "S4") for x in ("F", "M")]


def _elementary_effects() -> dict[tuple[str, str], pd.DataFrame]:
    """Clean elementary effects per cell, exactly as the Morris estimator uses them."""
    sample = pd.read_parquet(RAW_DIR / "morris_sample.parquet")
    master = pd.read_parquet(RAW_DIR / "aggregated.parquet")
    pairs = derive_trajectory_pairs(sample)
    out: dict[tuple[str, str], pd.DataFrame] = {}
    for sk, xk in CELLS:
        cell_df = master[(master["scenario"] == sk) & (master["sex"] == xk)]
        idx_map = {int(i): case_id(sk, xk, run_idx=int(i)) for i in sample.index}
        ee = compute_ee_for_cell(cell_df, pairs, idx_map)
        out[(sk, xk)] = ee[ee["both_clean"]].dropna(subset=["ee"])
    return out


def _ratio_ci(ee_group: pd.DataFrame, rng: np.random.Generator) -> tuple[float, float]:
    """Percentile CI on sigma/mu*, resampling trajectories and recomputing the ratio jointly.

    Returns (nan, nan) when fewer than two clean trajectories contribute: a
    single trajectory carries no information about between-trajectory spread.
    """
    trajectories = ee_group["trajectory"].to_numpy()
    effects = ee_group["ee"].to_numpy(dtype=float)
    unique = np.unique(trajectories)
    if unique.size < 2:
        return float("nan"), float("nan")

    by_traj = {int(t): effects[trajectories == t] for t in unique}
    draws = np.empty(N_BOOTSTRAP)
    for b in range(N_BOOTSTRAP):
        chosen = rng.choice(unique, size=unique.size, replace=True)
        pooled = np.concatenate([by_traj[int(t)] for t in chosen])
        if pooled.size < 2:
            draws[b] = np.nan
            continue
        mu_star = np.mean(np.abs(pooled))
        draws[b] = np.std(pooled, ddof=1) / mu_star if mu_star > 0 else np.inf
    draws = draws[np.isfinite(draws)]
    if draws.size == 0:
        return float("nan"), float("nan")
    return float(np.quantile(draws, ALPHA / 2)), float(np.quantile(draws, 1 - ALPHA / 2))


def build_table() -> pd.DataFrame:
    """One row per top-three input, with the ratio CI under every seed."""
    morris = pd.read_parquet(RESULTS_DIR / "morris_indices.parquet")
    ee_by_cell = _elementary_effects()

    top3 = (
        morris.sort_values(
            ["scenario", "sex", "output", "mu_star"], ascending=[True, True, True, False]
        )
        .groupby(["scenario", "sex", "output"], as_index=False)
        .head(TOP_K)
        .reset_index(drop=True)
    )
    top3["rank"] = top3.groupby(["scenario", "sex", "output"]).cumcount() + 1
    top3["ratio"] = top3["sigma"] / top3["mu_star"]
    # Historical formula, kept so the pre-S031 buckets remain reproducible.
    top3["legacy_lo"] = top3["sigma_lo"] / top3["mu_star"]
    top3["legacy_hi"] = top3["sigma_hi"] / top3["mu_star"]

    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        los, his = [], []
        for _, row in top3.iterrows():
            ee = ee_by_cell[(row["scenario"], row["sex"])]
            grp = ee[(ee["output"] == row["output"]) & (ee["input"] == row["input"])]
            lo, hi = _ratio_ci(grp[["trajectory", "ee"]], rng)
            los.append(lo)
            his.append(hi)
        top3[f"ra_lo_{seed}"] = los
        top3[f"ra_hi_{seed}"] = his

    lo_cols = [f"ra_lo_{s}" for s in SEEDS]
    hi_cols = [f"ra_hi_{s}" for s in SEEDS]
    estimable = top3["n_trajectories"] >= 2
    top3["nonlinear_all_seeds"] = estimable & (top3[lo_cols] >= PROMOTE_THRESHOLD).all(axis=1)
    top3["nonlinear_any_seed"] = estimable & (top3[lo_cols] >= PROMOTE_THRESHOLD).any(axis=1)
    top3["linear_all_seeds"] = estimable & (top3[hi_cols] < PROMOTE_THRESHOLD).all(axis=1)
    top3["no_estimable_ci"] = ~estimable
    return top3


def summarise(top3: pd.DataFrame) -> dict:
    """The aggregate figures the manuscript quotes, re-derivable by the audit ledger."""
    core = top3[top3["nonlinear_all_seeds"]]
    fires = top3["ratio"] >= PROMOTE_THRESHOLD
    cells_firing = top3[fires].groupby(["scenario", "sex", "output"]).ngroups
    dominant = top3[top3["rank"] == 1]
    dom_lo = dominant[[f"ra_lo_{s}" for s in SEEDS]]
    dom_hi = dominant[[f"ra_hi_{s}" for s in SEEDS]]
    dom_est = dominant["n_trajectories"] >= 2

    # --- Cost of the preregistered Sobol bolt-on ---------------------------
    # One Pulse run emits all six outputs, so a Sobol sample is shared by every
    # output of a cell: the cost scales with cells (8), not with cell x output
    # combinations (43). Four readings are reported because the preregistration
    # writes the cost as 64*(2k+2) -- the Saltelli size that also yields S2 --
    # while its analysis plan asks only for S1 and ST, which need 64*(k+2).
    promoted = top3[fires]
    k_per_cell = promoted.groupby(["scenario", "sex"])["input"].nunique()
    n_cells_firing = int(len(k_per_cell))
    BASE, K_FULL = 64, 7

    return {
        "n_top3_rows": int(len(top3)),
        "n_cells": int(top3.groupby(["scenario", "sex", "output"]).ngroups),
        "point_estimate_promotions": int(fires.sum()),
        "cells_firing_point_estimate": int(cells_firing),
        "core_nonlinear_all_seeds": int(len(core)),
        "cells_touched_by_core": int(core.groupby(["scenario", "sex", "output"]).ngroups),
        "core_by_input": core["input"].value_counts().to_dict(),
        "core_by_output": core["output"].value_counts().to_dict(),
        "core_by_scenario": core["scenario"].value_counts().to_dict(),
        "core_by_sex": core["sex"].value_counts().to_dict(),
        "dominant_linear_all_seeds": int((dom_est & (dom_hi < PROMOTE_THRESHOLD).all(axis=1)).sum()),
        "dominant_nonlinear_all_seeds": int((dom_est & (dom_lo >= PROMOTE_THRESHOLD).all(axis=1)).sum()),
        "dominant_no_estimable_ci": int((~dom_est).sum()),
        "sobol_budget_runs_preregistered": 1500,
        "sobol_base_sample": 64,
        "sobol_cells_firing": n_cells_firing,
        "sobol_k_per_cell": {
            f"{sc}_{sx}": int(k) for (sc, sx), k in k_per_cell.items()
        },
        "sobol_runs_reduced_second_order": int(
            sum(BASE * (2 * k + 2) for k in k_per_cell)
        ),
        "sobol_runs_reduced_first_total": int(
            sum(BASE * (k + 2) for k in k_per_cell)
        ),
        "sobol_runs_full_second_order": n_cells_firing * BASE * (2 * K_FULL + 2),
        "sobol_runs_full_first_total": n_cells_firing * BASE * (K_FULL + 2),
        # Provenance only. Withdrawn cost model: it billed one single-input
        # Sobol sample per cell x output combination (43 x 256). Superseded
        # because every output of a cell comes from the same Pulse run and
        # therefore shares one sample. Not a defensible lower bound.
        "sobol_runs_unshared_k1_withdrawn": int(cells_firing * 64 * (2 * 1 + 2)),
        "n_bootstrap": N_BOOTSTRAP,
        "seeds": list(SEEDS),
        "promote_threshold": PROMOTE_THRESHOLD,
        "skip_threshold": SKIP_THRESHOLD,
    }


def main() -> int:
    if not (RAW_DIR / "aggregated.parquet").exists():
        print(f"[sobol-ci] raw sweep not found at {RAW_DIR}")
        return 1
    table = build_table()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(RESULTS_DIR / "sobol_ci_buckets.csv", index=False)
    summary = summarise(table)
    (RESULTS_DIR / "sobol_ci_buckets.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    for k, v in summary.items():
        print(f"  {k:34s} {v}")
    print(f"[sobol-ci] wrote {RESULTS_DIR / 'sobol_ci_buckets.csv'} and .json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
