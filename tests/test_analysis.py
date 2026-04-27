"""Tests for src/analysis_morris.py and src/analysis_compare.py.

Operates on tiny synthetic / toy data — no Pulse, no Docker. Verifies
that elementary-effect math, bootstrap CI, H1 calculation, Wasserstein
nulls, and Spearman bootstraps behave as expected on inputs whose
correct outputs are known a priori.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src import analysis_morris as am
from src import analysis_compare as ac
from src import sampler as sm


def test_evaluate_h1_passes_when_top3_dominates():
    """Synthetic mu_star with top-3 inputs at 100 and rest at 0 → H1 trivially passes."""
    rows = []
    for inp, val in [("hr", 100), ("sbp", 100), ("dbp", 100), ("rr", 0), ("vt", 0), ("fio2", 0), ("peep", 0)]:
        rows.append({"scenario": "S1", "sex": "M", "output": "HR", "input": inp, "mu_star": val})
    df = pd.DataFrame(rows)
    out = am.evaluate_h1(df)
    assert out.iloc[0]["top3_fraction"] == pytest.approx(1.0)
    assert bool(out.iloc[0]["h1_pass"])


def test_evaluate_h1_fails_when_uniform():
    """All inputs equal → top-3 fraction is 3/7 ≈ 0.43 < 0.5 → H1 fails."""
    rows = [
        {"scenario": "S1", "sex": "M", "output": "HR", "input": inp, "mu_star": 1.0}
        for inp in sm.INPUT_NAMES
    ]
    df = pd.DataFrame(rows)
    out = am.evaluate_h1(df)
    assert out.iloc[0]["top3_fraction"] == pytest.approx(3 / 7)
    assert not bool(out.iloc[0]["h1_pass"])


def test_sobol_promotion_thresholds():
    """sigma/mu_star >= 0.6 → promote; <= 0.4 → skip; else gray."""
    df = pd.DataFrame(
        [
            {"scenario": "S1", "sex": "M", "output": "HR", "input": "hr", "mu_star": 10.0, "sigma": 7.0},  # 0.7 -> promote
            {"scenario": "S1", "sex": "M", "output": "HR", "input": "rr", "mu_star": 10.0, "sigma": 3.0},  # 0.3 -> skip
            {"scenario": "S1", "sex": "M", "output": "HR", "input": "vt", "mu_star": 10.0, "sigma": 5.0},  # 0.5 -> gray
        ]
    )
    out = am.sobol_promotion(df, top_k=3)
    decisions = out.set_index("input")["decision"].to_dict()
    assert decisions["hr"] == "promote"
    assert decisions["rr"] == "skip"
    assert decisions["vt"] == "gray"


def test_block_bootstrap_ci_collapses_with_one_trajectory():
    """Single-trajectory block bootstrap can't form a CI."""
    df = pd.DataFrame({"trajectory": [0, 0, 0], "ee": [1.0, 2.0, 3.0]})
    rng = np.random.default_rng(0)
    lo, hi = am._block_bootstrap_mu_star_ci(df, n_bootstrap=100, rng=rng)
    assert np.isnan(lo) and np.isnan(hi)


def test_block_bootstrap_ci_brackets_estimate():
    """With multiple trajectories, the CI brackets the point mu_star."""
    rng = np.random.default_rng(0)
    ees = rng.normal(loc=5.0, scale=1.0, size=30)
    df = pd.DataFrame({"trajectory": np.repeat(np.arange(10), 3), "ee": ees})
    lo, hi = am._block_bootstrap_mu_star_ci(df, n_bootstrap=500, rng=rng)
    mu_star = float(np.mean(np.abs(ees)))
    assert lo <= mu_star <= hi
    # CI should be reasonably tight on N=30 EEs
    assert hi - lo < 2.0


def test_wasserstein_per_output_synthetic():
    """Synthetic two-cell scenario: M and F clean runs from known distributions."""
    rng = np.random.default_rng(1)
    n = 50
    rows = []
    for v in rng.normal(0, 1, n):
        rows.append({"scenario": "S1", "sex": "M", "clean": True, "HR_mean": v,
                     "MAP_mean": np.nan, "Vt_mean": np.nan, "SpO2_mean": np.nan,
                     "PaO2_mean": np.nan, "PaCO2_mean": np.nan})
    for v in rng.normal(5, 1, n):  # shifted by 5
        rows.append({"scenario": "S1", "sex": "F", "clean": True, "HR_mean": v,
                     "MAP_mean": np.nan, "Vt_mean": np.nan, "SpO2_mean": np.nan,
                     "PaO2_mean": np.nan, "PaCO2_mean": np.nan})
    df = pd.DataFrame(rows)
    out = ac.wasserstein_per_output(df, scenarios=["S1"], n_null=200)
    hr_row = out[out["output"] == "HR"].iloc[0]
    # Distance ≈ 5 (the shift)
    assert hr_row["wasserstein"] == pytest.approx(5.0, abs=0.5)
    # Significant — empirical p well below 0.05
    assert hr_row["p_value_empirical"] < 0.05


def test_wasserstein_null_high_p_for_same_distribution():
    """When M and F come from the same distribution, p_emp should NOT be small."""
    rng = np.random.default_rng(2)
    n = 50
    rows = []
    for v in rng.normal(0, 1, n):
        rows.append({"scenario": "S1", "sex": "M", "clean": True, "HR_mean": v,
                     "MAP_mean": np.nan, "Vt_mean": np.nan, "SpO2_mean": np.nan,
                     "PaO2_mean": np.nan, "PaCO2_mean": np.nan})
    for v in rng.normal(0, 1, n):  # SAME distribution
        rows.append({"scenario": "S1", "sex": "F", "clean": True, "HR_mean": v,
                     "MAP_mean": np.nan, "Vt_mean": np.nan, "SpO2_mean": np.nan,
                     "PaO2_mean": np.nan, "PaCO2_mean": np.nan})
    df = pd.DataFrame(rows)
    out = ac.wasserstein_per_output(df, scenarios=["S1"], n_null=200)
    hr_row = out[out["output"] == "HR"].iloc[0]
    # p_emp should be far from 0 (not significant)
    assert hr_row["p_value_empirical"] > 0.1


def test_cell_flag_summary_columns():
    """Output schema is stable."""
    rows = []
    for sk, sx in [("S1", "M"), ("S1", "F")]:
        for i in range(5):
            rows.append({
                "scenario": sk, "sex": sx,
                "clamped": False, "diverged": (i == 0),
                "implausible": False, "not_steady_state": False,
                "clean": (i > 0),
            })
    df = pd.DataFrame(rows)
    out = ac.cell_flag_summary(df)
    expected_cols = {"scenario", "sex", "n_total", "n_clamped", "n_diverged",
                     "n_implausible", "n_not_steady_state", "n_clean"}
    assert expected_cols.issubset(out.columns)
    s1m = out[(out["scenario"] == "S1") & (out["sex"] == "M")].iloc[0]
    assert s1m["n_total"] == 5
    assert s1m["n_diverged"] == 1
    assert s1m["n_clean"] == 4
