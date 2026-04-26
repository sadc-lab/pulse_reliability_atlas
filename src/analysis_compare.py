"""Sex-comparison, clamp/divergence maps, reliability classification.

Implements `preregistration.md` §Analysis points 4–7:

    4. Clamp map / divergence map (per input pair, per cell)
    5. (in `analysis_morris.py`)
    6. Sex comparison via Wasserstein distance + Spearman ρ on Morris mu_star vectors.
    7. Reliability classification: green / yellow / red per output × input.

All functions take the master aggregated table and return tidy DataFrames
suitable for figure generation.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, wasserstein_distance

from src.aggregator import STAT_CHANNELS
from src.sampler import INPUT_NAMES


# ---------- H4: sex comparison ---------- #


def wasserstein_per_output(
    df_master: pd.DataFrame, scenarios: Iterable[str]
) -> pd.DataFrame:
    """Wasserstein distance between male and female clean-run output distributions
    per scenario per output. Larger ⇒ greater sex difference."""
    rows: list[dict] = []
    for sk in scenarios:
        m = df_master[
            (df_master["scenario"] == sk) & (df_master["sex"] == "M") & df_master["clean"]
        ]
        f = df_master[
            (df_master["scenario"] == sk) & (df_master["sex"] == "F") & df_master["clean"]
        ]
        for ch in STAT_CHANNELS:
            mv = m[f"{ch}_mean"].dropna().to_numpy()
            fv = f[f"{ch}_mean"].dropna().to_numpy()
            if mv.size < 2 or fv.size < 2:
                w = float("nan")
            else:
                w = float(wasserstein_distance(mv, fv))
            rows.append({
                "scenario": sk,
                "output": ch,
                "n_male": int(mv.size),
                "n_female": int(fv.size),
                "wasserstein": w,
            })
    return pd.DataFrame(rows)


def spearman_mu_star_male_vs_female(
    morris_df: pd.DataFrame, scenarios: Iterable[str]
) -> pd.DataFrame:
    """Per scenario × output: Spearman ρ between male mu_star vector and female mu_star vector
    indexed by input. ρ near 1 ⇒ same input ranking by sex."""
    rows: list[dict] = []
    for sk in scenarios:
        m = morris_df[(morris_df["scenario"] == sk) & (morris_df["sex"] == "M")]
        f = morris_df[(morris_df["scenario"] == sk) & (morris_df["sex"] == "F")]
        for ch in STAT_CHANNELS:
            mv = (
                m[m["output"] == ch]
                .set_index("input")["mu_star"]
                .reindex(INPUT_NAMES)
                .to_numpy()
            )
            fv = (
                f[f["output"] == ch]
                .set_index("input")["mu_star"]
                .reindex(INPUT_NAMES)
                .to_numpy()
            )
            if np.isnan(mv).any() or np.isnan(fv).any() or mv.size < 3:
                rho = float("nan")
                pval = float("nan")
            else:
                rho_obj = spearmanr(mv, fv)
                rho = float(rho_obj.correlation)
                pval = float(rho_obj.pvalue)
            rows.append({
                "scenario": sk,
                "output": ch,
                "spearman_rho": rho,
                "spearman_p": pval,
            })
    return pd.DataFrame(rows)


# ---------- Clamp / divergence / not-steady-state maps ---------- #


def flag_count_grid(
    df_master: pd.DataFrame, flag: str, n_bins: int = 5
) -> pd.DataFrame:
    """Build per-(cell, input-pair) heatmap of `flag` rate.

    For every cell and every (input_a, input_b) pair, returns the fraction of
    runs where `flag` == True in the (a_bin, b_bin) cell of an n_bins × n_bins
    grid. The output is long-format with one row per cell × pair × (a_bin,
    b_bin).
    """
    if flag not in ("clamped", "diverged", "implausible", "not_steady_state"):
        raise ValueError(f"unknown flag {flag!r}")

    rows: list[dict] = []
    for (sk, xk), cell_df in df_master.groupby(["scenario", "sex"]):
        for i, a in enumerate(INPUT_NAMES):
            for b in INPUT_NAMES[i + 1 :]:
                a_col = f"in_{a}"
                b_col = f"in_{b}"
                if a_col not in cell_df.columns or b_col not in cell_df.columns:
                    continue
                a_vals = cell_df[a_col].astype(float)
                b_vals = cell_df[b_col].astype(float)
                a_bins = pd.qcut(a_vals, q=n_bins, duplicates="drop").astype(str)
                b_bins = pd.qcut(b_vals, q=n_bins, duplicates="drop").astype(str)
                grid = (
                    cell_df.assign(a_bin=a_bins, b_bin=b_bins)
                    .groupby(["a_bin", "b_bin"])[flag]
                    .agg(["sum", "count"])
                )
                for (a_bin, b_bin), row in grid.iterrows():
                    rows.append({
                        "scenario": sk,
                        "sex": xk,
                        "input_a": a,
                        "input_b": b,
                        "a_bin": a_bin,
                        "b_bin": b_bin,
                        "flag": flag,
                        "n_flagged": int(row["sum"]),
                        "n_total": int(row["count"]),
                        "rate": (
                            float(row["sum"]) / float(row["count"])
                            if row["count"] > 0
                            else 0.0
                        ),
                    })
    return pd.DataFrame(rows)


# ---------- Reliability classification (green/yellow/red) ---------- #


def reliability_classification(df_master: pd.DataFrame) -> pd.DataFrame:
    """Per cell × output × input bin: green/yellow/red traffic light.

    Green:  no flags raised AND mean within 10% of cell baseline (S1 mid-range).
    Yellow: any flag raised OR mean 10–30% off baseline.
    Red:    mean > 30% off baseline OR `diverged`/`implausible` rate > 30%.

    Cell baseline is the mean of clean S1_M runs at that input bin (so all
    classifications are comparable across cells).
    """
    rows: list[dict] = []
    s1m_clean = df_master[
        (df_master["scenario"] == "S1") & (df_master["sex"] == "M") & df_master["clean"]
    ]
    if s1m_clean.empty:
        return pd.DataFrame()

    for ch in STAT_CHANNELS:
        baseline = float(s1m_clean[f"{ch}_mean"].mean())
        if not np.isfinite(baseline) or baseline == 0:
            continue
        for (sk, xk), cell_df in df_master.groupby(["scenario", "sex"]):
            n_total = int(len(cell_df))
            n_diverged = int(cell_df["diverged"].sum())
            n_implausible = int(cell_df["implausible"].sum())
            mean_clean = (
                float(cell_df[cell_df["clean"]][f"{ch}_mean"].mean())
                if cell_df["clean"].any()
                else float("nan")
            )
            if pd.isna(mean_clean):
                light = "red"
                pct_off = float("nan")
            else:
                pct_off = abs(mean_clean - baseline) / abs(baseline)
                hard_failure_rate = (n_diverged + n_implausible) / max(n_total, 1)
                if hard_failure_rate > 0.3 or pct_off > 0.3:
                    light = "red"
                elif pct_off > 0.1 or hard_failure_rate > 0.0:
                    light = "yellow"
                else:
                    light = "green"
            rows.append({
                "scenario": sk,
                "sex": xk,
                "output": ch,
                "mean_clean": mean_clean,
                "baseline_S1M": baseline,
                "pct_off_baseline": pct_off,
                "n_total": n_total,
                "n_diverged": n_diverged,
                "n_implausible": n_implausible,
                "light": light,
            })
    return pd.DataFrame(rows)


# ---------- Per-cell flag summary (Table 1 of the paper) ---------- #


def cell_flag_summary(df_master: pd.DataFrame) -> pd.DataFrame:
    """Per (scenario, sex): n_total, n_clamped, n_diverged, n_implausible,
    n_not_steady_state, n_clean. Suitable as the paper's Table 1."""
    rows: list[dict] = []
    for (sk, xk), grp in df_master.groupby(["scenario", "sex"]):
        rows.append({
            "scenario": sk,
            "sex": xk,
            "n_total": int(len(grp)),
            "n_clamped": int(grp["clamped"].sum()),
            "n_diverged": int(grp["diverged"].sum()),
            "n_implausible": int(grp["implausible"].sum()),
            "n_not_steady_state": int(grp["not_steady_state"].sum()),
            "n_clean": int(grp["clean"].sum()),
        })
    return pd.DataFrame(rows)


__all__ = [
    "cell_flag_summary",
    "flag_count_grid",
    "reliability_classification",
    "spearman_mu_star_male_vs_female",
    "wasserstein_per_output",
]
