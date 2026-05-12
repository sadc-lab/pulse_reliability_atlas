"""Morris elementary-effects analysis for the Pulse Reliability Atlas.

Computes per-input × per-output × per-cell Morris indices on the *clean* runs
of the full sweep (per `preregistration.md` §Analysis 2). Bootstrap CIs on mu_star
strengthen H1 against reviewer scrutiny.

Inputs
------
- The canonical Morris sample at ``data/runs/full_sweep/morris_sample.parquet``
  (rows ordered by ``trajectory`` then ``point``; locked across all 8 cells).
- The master aggregated table at
  ``data/runs/full_sweep/aggregated.parquet``.

Outputs
-------
- Long-format DataFrame with columns
  ``[scenario, sex, output, input, mu, mu_star, sigma,
    mu_star_lo, mu_star_hi, n_clean_pairs, n_total_pairs]``.
- Sobol promotion table per `preregistration.md` §Sampling method
  (σ/μ* ratio rule).

Notes on the elementary-effect computation
------------------------------------------
For trajectory ``T``, the SALib-OAT sample yields ``k+1`` rows where ``k`` is
the number of inputs. Going from row ``j`` to row ``j+1`` flips exactly one
input by ``Δ``. The elementary effect of that flipped input on output ``y``
is ``EE = (y[j+1] - y[j]) / Δ``. We collect EE samples per (input, output,
cell) pooling across all trajectories. Morris indices:

    μ      = mean of EEs
    μ*     = mean of |EEs|
    σ      = std  of EEs

A trajectory pair (j, j+1) is *useable* only if **both endpoints are clean**
(no flag fired). Trajectories with mid-points clamped/diverged/implausible/
not-steady-state lose the EEs that span those endpoints. We log
``n_clean_pairs / n_total_pairs`` for full transparency.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd

from src.aggregator import STAT_CHANNELS
from src.sampler import INPUT_NAMES


# ---------- Trajectory bookkeeping ---------- #


@dataclass(frozen=True)
class TrajectoryPair:
    """One Morris OAT step within a trajectory.

    `flipped_input` is the input that changed between row `j_lo` and `j_hi`;
    `delta` is the (signed) change in normalized [0, 1] coordinates.
    """

    trajectory: int
    j_lo: int        # row index of starting point
    j_hi: int        # row index of next point (j_lo + 1)
    flipped_input: str
    delta_normalized: float


def _normalized_inputs(sample: pd.DataFrame) -> pd.DataFrame:
    """Map each input column to [0, 1] using its locked range from sampler."""
    from src.sampler import INPUT_SPECS

    out = sample.copy()
    for spec in INPUT_SPECS:
        out[spec.name] = (sample[spec.name] - spec.lo) / (spec.hi - spec.lo)
    return out


def derive_trajectory_pairs(sample: pd.DataFrame) -> list[TrajectoryPair]:
    """Walk the Morris sample and identify the flipped input per OAT step."""
    norm = _normalized_inputs(sample)
    pairs: list[TrajectoryPair] = []
    for traj_id, group in norm.groupby("trajectory"):
        rows = group.sort_values("point")
        rows_index = rows.index.tolist()
        for k in range(len(rows_index) - 1):
            j_lo = rows_index[k]
            j_hi = rows_index[k + 1]
            diffs = rows.loc[j_hi, list(INPUT_NAMES)] - rows.loc[j_lo, list(INPUT_NAMES)]
            # Only one input changes by construction; pick the largest |delta|.
            mags = diffs.abs()
            flipped = mags.idxmax()
            delta = float(diffs[flipped])
            if abs(delta) < 1e-9:
                # All-zero step → trajectory glitch; skip.
                continue
            pairs.append(
                TrajectoryPair(
                    trajectory=int(traj_id),
                    j_lo=int(j_lo),
                    j_hi=int(j_hi),
                    flipped_input=str(flipped),
                    delta_normalized=delta,
                )
            )
    return pairs


# ---------- Elementary effects ---------- #


def compute_ee_for_cell(
    df_cell: pd.DataFrame,
    pairs: list[TrajectoryPair],
    sample_run_idx_map: dict[int, str],  # row_idx -> case_id
) -> pd.DataFrame:
    """Compute elementary effects for one (scenario, sex) cell.

    Returns a long-format DataFrame:
        columns = [trajectory, output, input, ee, j_lo_case, j_hi_case, both_clean]

    The ``trajectory`` column is added so downstream callers can do a
    *block bootstrap by trajectory* (preserves within-trajectory
    dependence; honest for Morris-OAT geometry).
    """
    # Index by case_id for fast lookup
    by_case = df_cell.set_index("case_id")
    rows: list[dict] = []
    for p in pairs:
        cid_lo = sample_run_idx_map.get(p.j_lo)
        cid_hi = sample_run_idx_map.get(p.j_hi)
        if cid_lo is None or cid_hi is None:
            continue
        if cid_lo not in by_case.index or cid_hi not in by_case.index:
            continue
        r_lo = by_case.loc[cid_lo]
        r_hi = by_case.loc[cid_hi]
        both_clean = bool(r_lo["clean"]) and bool(r_hi["clean"])
        for ch in STAT_CHANNELS:
            y_lo = r_lo.get(f"{ch}_mean")
            y_hi = r_hi.get(f"{ch}_mean")
            if pd.isna(y_lo) or pd.isna(y_hi):
                ee = np.nan
            else:
                ee = (float(y_hi) - float(y_lo)) / p.delta_normalized
            rows.append({
                "trajectory": p.trajectory,
                "output": ch,
                "input": p.flipped_input,
                "ee": ee,
                "j_lo_case": cid_lo,
                "j_hi_case": cid_hi,
                "both_clean": both_clean,
            })
    return pd.DataFrame(rows)


# ---------- Morris indices with bootstrap CI ---------- #


def _morris_stats(ees: np.ndarray) -> tuple[float, float, float]:
    """Return (mu, mu_star, sigma) for a 1-D array of elementary effects."""
    if ees.size == 0:
        return float("nan"), float("nan"), float("nan")
    mu = float(np.mean(ees))
    mu_star = float(np.mean(np.abs(ees)))
    sigma = float(np.std(ees, ddof=1)) if ees.size > 1 else 0.0
    return mu, mu_star, sigma


def _bootstrap_mu_star_ci(
    ees: np.ndarray,
    n_bootstrap: int,
    rng: np.random.Generator,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """Percentile bootstrap CI for mu_star. Returns (lo, hi).

    Naive bootstrap — resamples individual elementary effects
    independently. Implicitly assumes EEs are exchangeable. Kept for
    completeness; prefer ``_block_bootstrap_mu_star_ci`` which respects
    trajectory-level structure (Morris OAT pairs from one trajectory
    are not independent of each other).
    """
    if ees.size < 2:
        return float("nan"), float("nan")
    boot = np.empty(n_bootstrap)
    n = ees.size
    for b in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        boot[b] = float(np.mean(np.abs(ees[idx])))
    lo = float(np.quantile(boot, alpha / 2))
    hi = float(np.quantile(boot, 1 - alpha / 2))
    return lo, hi


def _block_bootstrap_mu_star_ci(
    ee_df_input: pd.DataFrame,
    n_bootstrap: int,
    rng: np.random.Generator,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """Block (trajectory-level) bootstrap CI for mu_star.

    ``ee_df_input`` is the subset of ``compute_ee_for_cell``'s output for
    one (cell, output, input) combo, restricted to clean & non-NaN EEs.
    The block is the trajectory: we resample trajectory IDs *with
    replacement*, then take all surviving EEs from the chosen
    trajectories. This preserves within-trajectory dependence and gives
    an honest CI for Morris-OAT geometry.

    If only one or zero trajectories contribute to this combo, the CI
    collapses to NaN — Morris is not estimable on a single trajectory.
    """
    trajs = ee_df_input["trajectory"].to_numpy()
    ees = ee_df_input["ee"].to_numpy(dtype=float)
    unique_trajs = np.unique(trajs)
    if unique_trajs.size < 2:
        return float("nan"), float("nan")

    # Pre-build trajectory -> EE-array index for speed.
    by_traj: dict[int, np.ndarray] = {
        int(t): ees[trajs == t] for t in unique_trajs
    }

    boot = np.empty(n_bootstrap)
    for b in range(n_bootstrap):
        chosen = rng.choice(unique_trajs, size=unique_trajs.size, replace=True)
        sample_ees = np.concatenate([by_traj[int(t)] for t in chosen])
        if sample_ees.size == 0:
            boot[b] = np.nan
        else:
            boot[b] = float(np.mean(np.abs(sample_ees)))
    boot = boot[~np.isnan(boot)]
    if boot.size == 0:
        return float("nan"), float("nan")
    lo = float(np.quantile(boot, alpha / 2))
    hi = float(np.quantile(boot, 1 - alpha / 2))
    return lo, hi


def _block_bootstrap_sigma_ci(
    ee_df_input: pd.DataFrame,
    n_bootstrap: int,
    rng: np.random.Generator,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """Block (trajectory-level) bootstrap CI for sigma (std of EEs).

    Same block-bootstrap structure as ``_block_bootstrap_mu_star_ci`` but
    computes sigma = std(ees, ddof=1) per resample. Needed for the
    Sobol-promotion rule which thresholds on sigma / mu_star >= 0.6
    (preregistration); without CI on sigma, the promotion decision is a
    point estimate only. The CI lets §3.3.1 report which "promote" cells
    are robust under trajectory-level uncertainty and which are borderline.
    """
    trajs = ee_df_input["trajectory"].to_numpy()
    ees = ee_df_input["ee"].to_numpy(dtype=float)
    unique_trajs = np.unique(trajs)
    if unique_trajs.size < 2:
        return float("nan"), float("nan")

    by_traj: dict[int, np.ndarray] = {
        int(t): ees[trajs == t] for t in unique_trajs
    }

    boot = np.empty(n_bootstrap)
    for b in range(n_bootstrap):
        chosen = rng.choice(unique_trajs, size=unique_trajs.size, replace=True)
        sample_ees = np.concatenate([by_traj[int(t)] for t in chosen])
        if sample_ees.size < 2:
            boot[b] = np.nan
        else:
            boot[b] = float(np.std(sample_ees, ddof=1))
    boot = boot[~np.isnan(boot)]
    if boot.size == 0:
        return float("nan"), float("nan")
    lo = float(np.quantile(boot, alpha / 2))
    hi = float(np.quantile(boot, 1 - alpha / 2))
    return lo, hi


def morris_indices(
    df_master: pd.DataFrame,
    sample: pd.DataFrame,
    cells: Iterable[tuple[str, str]],
    n_bootstrap: int = 1000,
    seed: int = 12345,
) -> pd.DataFrame:
    """Compute (μ, μ*, σ, μ* CI, σ CI) per (cell, output, input).

    Uses ONLY EE pairs whose both endpoints are clean (preregistration §A.2).

    The μ* bootstrap and σ bootstrap use SEPARATE RNG streams so adding the
    σ CI to a pre-existing artifact leaves μ* CI columns bit-identical;
    additive-only drift was verified by S015 regen_compare on 2026-05-12.
    """
    pairs = derive_trajectory_pairs(sample)

    rng = np.random.default_rng(seed)
    sigma_rng = np.random.default_rng(seed + 10_000)

    rows: list[dict] = []
    for sk, xk in cells:
        cell_df = df_master[(df_master["scenario"] == sk) & (df_master["sex"] == xk)]
        if cell_df.empty:
            continue
        # Map sample row idx -> case_id (canonical: case_id_format)
        from src.scenario import case_id

        sample_idx_to_case = {
            int(i): case_id(sk, xk, run_idx=int(i)) for i in sample.index
        }
        ee_df = compute_ee_for_cell(cell_df, pairs, sample_idx_to_case)
        if ee_df.empty:
            continue
        ee_clean = ee_df[ee_df["both_clean"]].dropna(subset=["ee"])

        for (out_name, inp_name), grp in ee_clean.groupby(["output", "input"]):
            ees = grp["ee"].to_numpy()
            mu, mu_star, sigma = _morris_stats(ees)
            # Block (trajectory-level) bootstrap — honest for Morris OAT.
            mu_star_lo, mu_star_hi = _block_bootstrap_mu_star_ci(
                grp[["trajectory", "ee"]], n_bootstrap, rng
            )
            sigma_lo, sigma_hi = _block_bootstrap_sigma_ci(
                grp[["trajectory", "ee"]], n_bootstrap, sigma_rng
            )
            n_total = int(((ee_df["output"] == out_name) & (ee_df["input"] == inp_name)).sum())
            n_unique_trajs = int(grp["trajectory"].nunique())
            rows.append({
                "scenario": sk,
                "sex": xk,
                "output": out_name,
                "input": inp_name,
                "mu": mu,
                "mu_star": mu_star,
                "sigma": sigma,
                "mu_star_lo": mu_star_lo,
                "mu_star_hi": mu_star_hi,
                "sigma_lo": sigma_lo,
                "sigma_hi": sigma_hi,
                "n_clean_pairs": int(ees.size),
                "n_total_pairs": n_total,
                "n_trajectories": n_unique_trajs,
            })
    return pd.DataFrame(rows)


# ---------- Sobol promotion rule ---------- #


def sobol_promotion(
    morris_df: pd.DataFrame,
    top_k: int = 3,
    promote_threshold: float = 0.6,
    skip_threshold: float = 0.4,
) -> pd.DataFrame:
    """Apply the preregistered σ/μ* rule to the top-k Morris inputs per cell × output.

    Returns columns:
        [scenario, sex, output, input, mu_star, sigma, sigma_over_mu_star,
         decision]   where decision ∈ {"promote", "skip", "gray"}.
    """
    rows: list[dict] = []
    for (sk, xk, out_name), grp in morris_df.groupby(["scenario", "sex", "output"]):
        ranked = grp.sort_values("mu_star", ascending=False).head(top_k)
        for _, r in ranked.iterrows():
            ratio = (
                r["sigma"] / r["mu_star"]
                if r["mu_star"] > 0
                else float("inf")
            )
            if ratio >= promote_threshold:
                decision = "promote"
            elif ratio <= skip_threshold:
                decision = "skip"
            else:
                decision = "gray"
            rows.append({
                "scenario": sk,
                "sex": xk,
                "output": out_name,
                "input": r["input"],
                "mu_star": r["mu_star"],
                "sigma": r["sigma"],
                "sigma_over_mu_star": ratio,
                "decision": decision,
            })
    return pd.DataFrame(rows)


# ---------- H1 evaluation ---------- #


def evaluate_h1(morris_df: pd.DataFrame, top_k: int = 3) -> pd.DataFrame:
    """For each cell × output: compute fraction of summed μ* explained by top-k inputs."""
    rows: list[dict] = []
    for (sk, xk, out_name), grp in morris_df.groupby(["scenario", "sex", "output"]):
        total = float(grp["mu_star"].sum())
        if total <= 0:
            frac = float("nan")
        else:
            top = grp.nlargest(top_k, "mu_star")
            frac = float(top["mu_star"].sum() / total)
        rows.append({
            "scenario": sk,
            "sex": xk,
            "output": out_name,
            "top3_fraction": frac,
            "h1_pass": frac >= 0.5,
        })
    return pd.DataFrame(rows)


__all__ = [
    "TrajectoryPair",
    "compute_ee_for_cell",
    "derive_trajectory_pairs",
    "evaluate_h1",
    "morris_indices",
    "sobol_promotion",
    "_block_bootstrap_sigma_ci",
]
