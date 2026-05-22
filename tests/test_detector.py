"""Tests for src/detector.py.

Golden-path and edge-case tests for each of the four flags, plus steady-state
stats. Each test matches the preregistration thresholds — if thresholds change,
amend `preregistration.md` first, then update tests.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src import detector as d


# ---------- Fixtures ---------- #


def _clean_csv_df(
    hr: float = 75.0,
    map_: float = 90.0,
    vt: float = 500.0,
    spo2: float = 0.98,
    pao2: float = 95.0,
    paco2: float = 40.0,
    n_points: int = 13,
    t_lo: float = 60.0,
    t_hi: float = 120.0,
    noise: float = 0.0,
) -> pd.DataFrame:
    """13 samples at 5 s in the steady-state window, optional tiny noise."""
    t = np.linspace(t_lo, t_hi, n_points)
    rng = np.random.default_rng(0)

    def col(mu: float) -> np.ndarray:
        if noise == 0:
            return np.full(n_points, mu)
        return mu + rng.normal(0, noise * abs(mu), n_points)

    return pd.DataFrame(
        {
            "time_s": t,
            "HeartRate": col(hr),
            "RespirationRate": col(15.0),
            "SystolicArterialPressure": col(115.0),
            "DiastolicArterialPressure": col(75.0),
            "MeanArterialPressure": col(map_),
            "TidalVolume": col(vt),
            "OxygenSaturation": col(spo2),
            "ArterialOxygenPressure": col(pao2),
            "ArterialCarbonDioxidePressure": col(paco2),
        }
    )


@pytest.fixture
def clean_csv(tmp_path: Path) -> Path:
    csv = tmp_path / "clean.csv"
    _clean_csv_df().to_csv(csv, index=False)
    return csv


# ---------- Golden path ---------- #


def test_clean_run_raises_no_flags(clean_csv: Path) -> None:
    result = d.classify(clean_csv, pulse_log="", exit_code=0)
    assert not result.clamped.fired
    assert not result.diverged.fired
    assert not result.implausible.fired
    assert not result.not_steady_state.fired
    assert result.clean


def test_clean_run_stats_have_13_points(clean_csv: Path) -> None:
    result = d.classify(clean_csv)
    for name, s in result.stats.items():
        assert s.n_points == 13, f"{name} n_points={s.n_points}"


# ---------- clamped ---------- #


@pytest.mark.parametrize(
    "log_text",
    [
        # Real Pulse error strings empirically captured in S004 clamp probe.
        "[ERROR] Patient systolic pressure baseline of 140 mmHg is too high. "
        "Hypertension must be modeled by adding/using a condition.",
        "Maximum systolic pressure baseline allowed is 120 mmHg",
        "must be modeled by adding/using a condition",
        "is outside the valid range",
    ],
)
def test_clamped_detects_pulse_rejection_strings(log_text: str, clean_csv: Path) -> None:
    """Verified Pulse-specific error patterns calibrated in S004."""
    result = d.classify(clean_csv, pulse_log=log_text)
    assert result.clamped.fired, f"log={log_text!r}"


def test_clamped_does_not_fire_on_clean_log(clean_csv: Path) -> None:
    result = d.classify(clean_csv, pulse_log="Pulse 4.3.1 initialized\nSimulation complete")
    assert not result.clamped.fired


@pytest.mark.parametrize(
    "log_text",
    [
        # Patterns previously over-matched by the old regex set; must NOT fire now.
        "Resetting the target for TidalVolume to 0.343",  # solver convergence text
        "Stomach is out of Sodium",  # substance depletion, NOT clamping
        "[INFO] Setting respiratory drive to 1.0",
        "out of CO2",
    ],
)
def test_clamped_does_not_false_positive(log_text: str, clean_csv: Path) -> None:
    """S004-calibrated regex must not flag normal Pulse runtime text."""
    result = d.classify(clean_csv, pulse_log=log_text)
    assert not result.clamped.fired, f"false positive on {log_text!r}"


# ---------- diverged ---------- #


def test_diverged_on_nonzero_exit_code(clean_csv: Path) -> None:
    result = d.classify(clean_csv, exit_code=1)
    assert result.diverged.fired
    assert "exit_code=1" in result.diverged.reason


def test_diverged_on_missing_csv(tmp_path: Path) -> None:
    result = d.classify(tmp_path / "nope.csv", exit_code=0)
    assert result.diverged.fired


def test_diverged_on_nan_in_csv(tmp_path: Path) -> None:
    df = _clean_csv_df()
    df.loc[5, "HeartRate"] = float("nan")
    p = tmp_path / "nan.csv"
    df.to_csv(p, index=False)
    result = d.classify(p)
    assert result.diverged.fired
    assert "NaN" in result.diverged.reason


def test_diverged_on_inf_in_csv(tmp_path: Path) -> None:
    df = _clean_csv_df()
    df.loc[3, "MeanArterialPressure"] = float("inf")
    p = tmp_path / "inf.csv"
    df.to_csv(p, index=False)
    result = d.classify(p)
    assert result.diverged.fired
    assert "Inf" in result.diverged.reason


def test_diverged_on_truncated_simulation(tmp_path: Path) -> None:
    df = _clean_csv_df(t_hi=100.0, n_points=9)  # stops at t=100, expected 120
    p = tmp_path / "short.csv"
    df.to_csv(p, index=False)
    result = d.classify(p)
    assert result.diverged.fired
    assert "truncated" in result.diverged.reason


def test_diverged_on_empty_csv(tmp_path: Path) -> None:
    p = tmp_path / "empty.csv"
    p.write_text("time_s\n")  # header only, no data rows
    result = d.classify(p)
    assert result.diverged.fired


# ---------- implausible ---------- #


@pytest.mark.parametrize(
    "kwargs, channel",
    [
        ({"hr": 15.0}, "HR"),  # below 20
        ({"hr": 230.0}, "HR"),  # above 220
        ({"map_": 25.0}, "MAP"),
        ({"map_": 200.0}, "MAP"),
        ({"spo2": 0.30}, "SpO2"),  # below 0.5
        ({"pao2": 15.0}, "PaO2"),
        ({"paco2": 150.0}, "PaCO2"),
    ],
)
def test_implausible_outside_hard_bounds(tmp_path: Path, kwargs: dict, channel: str) -> None:
    df = _clean_csv_df(**kwargs)
    p = tmp_path / "impl.csv"
    df.to_csv(p, index=False)
    result = d.classify(p)
    assert result.implausible.fired
    assert channel in result.implausible.reason


def test_implausible_does_not_fire_near_bound(tmp_path: Path) -> None:
    # HR = 25 is inside [20, 220] — should not be implausible
    df = _clean_csv_df(hr=25.0)
    # Drift would be 0 since all values are identical; but flatline near bound 20 would
    # fire the not_steady_state flag. Bump hr to 30 to avoid that interaction.
    df = _clean_csv_df(hr=30.0)
    p = tmp_path / "near.csv"
    df.to_csv(p, index=False)
    result = d.classify(p)
    assert not result.implausible.fired


# ---------- not_steady_state: variance ---------- #


def test_variance_too_high_fires_not_steady_state(tmp_path: Path) -> None:
    # CV = 10% on HR ⇒ above 5% threshold
    df = _clean_csv_df(noise=0.10)
    p = tmp_path / "noisy.csv"
    df.to_csv(p, index=False)
    result = d.classify(p)
    assert result.not_steady_state.fired
    assert "CV" in result.not_steady_state.reason


# ---------- not_steady_state: drift ---------- #


def test_drift_hr_fires_not_steady_state(tmp_path: Path) -> None:
    # HR drifts linearly 70 → 80 over 60 s ⇒ Δ=10 > 5 bpm threshold
    t = np.linspace(60.0, 120.0, 13)
    hr = np.linspace(70.0, 80.0, 13)
    df = _clean_csv_df()
    df["time_s"] = t
    df["HeartRate"] = hr
    p = tmp_path / "drift.csv"
    df.to_csv(p, index=False)
    result = d.classify(p)
    assert result.not_steady_state.fired
    assert "HR" in result.not_steady_state.reason


def test_drift_below_threshold_does_not_fire(tmp_path: Path) -> None:
    # HR drifts 75 → 77 over 60 s ⇒ Δ=2 < 5 bpm threshold
    t = np.linspace(60.0, 120.0, 13)
    hr = np.linspace(75.0, 77.0, 13)
    df = _clean_csv_df()
    df["time_s"] = t
    df["HeartRate"] = hr
    p = tmp_path / "slow_drift.csv"
    df.to_csv(p, index=False)
    result = d.classify(p)
    assert not result.not_steady_state.fired


# ---------- not_steady_state: flatline at extreme ---------- #


def test_flatline_at_upper_bound_fires(tmp_path: Path) -> None:
    # SpO2 pinned at 1.0 (upper bound) with zero variance ⇒ flatline at extreme
    df = _clean_csv_df(spo2=1.0)
    p = tmp_path / "flatline.csv"
    df.to_csv(p, index=False)
    result = d.classify(p)
    assert result.not_steady_state.fired
    assert "flatline" in result.not_steady_state.reason.lower()


def test_flatline_away_from_extreme_does_not_fire(tmp_path: Path) -> None:
    # SpO2 pinned at 0.97 (mid-range) with zero variance ⇒ fine, physiology steady
    df = _clean_csv_df(spo2=0.97)
    p = tmp_path / "stable.csv"
    df.to_csv(p, index=False)
    result = d.classify(p)
    assert not result.not_steady_state.fired


# ---------- steady-state stats ---------- #


def test_stats_window_covers_60_to_120(clean_csv: Path) -> None:
    df = pd.read_csv(clean_csv)
    stats = d.compute_steady_state_stats(df)
    assert stats["HR"].n_points == 13


def test_slope_is_zero_on_constant_series() -> None:
    t = np.linspace(60, 120, 13)
    y = np.full(13, 75.0)
    slope, r2 = d._linear_regression(t, y)
    assert slope == pytest.approx(0.0)
    # R² on a flat line is undefined (ss_tot = 0); we return 1.0
    assert r2 == pytest.approx(1.0)


def test_slope_matches_known_linear_series() -> None:
    t = np.linspace(60, 120, 13)
    y = 2.0 * t + 5.0  # slope = 2.0, perfect fit
    slope, r2 = d._linear_regression(t, y)
    assert slope == pytest.approx(2.0)
    assert r2 == pytest.approx(1.0)


def test_delta_60s_matches_slope_times_60(clean_csv: Path) -> None:
    df = pd.read_csv(clean_csv)
    stats = d.compute_steady_state_stats(df)
    for s in stats.values():
        assert s.delta_60s == pytest.approx(s.slope_per_s * 60.0)


# ---------- summary ---------- #


def test_summary_has_all_flag_fields(clean_csv: Path) -> None:
    result = d.classify(clean_csv)
    summary = result.summary()
    for k in [
        "clamped",
        "diverged",
        "implausible",
        "not_steady_state",
        "clean",
    ]:
        assert k in summary
    assert summary["clean"] is True
