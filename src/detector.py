"""Reliability detector for Pulse 4.3.1 runs.

Classifies each run on four orthogonal failure modes:

    clamped           — Pulse log contains rejection strings; setup values silently changed.
    diverged          — NaN/Inf in CSV, missing CSV, non-zero exit code, or truncated sim.
    implausible       — steady-state mean outside hard physiological bounds.
    not_steady_state  — flatline at extreme, variance too high, or drift over final 60 s.

Thresholds follow `preregistration.md` §Flags (2026-04-22). No run is discarded;
every run is categorized. Do not silently change thresholds — amend the preregistration
first if a threshold needs revision.

For threshold provenance and clinical-anchor rationale, see manuscript §2.6
(HARD_BOUNDS / DRIFT_MAX_DELTA_60S tables, each row tied to its primary source).
For mechanism interpretation of the flags as they manifest on the 1,280-run
sweep — F-004 patient-ventilator dyssynchrony driving `not_steady_state` via
Vt CV, F-003 transient hyperoxia regime driving `implausible` via PaO2 > 600
at FiO2 = 1.0, and the SpO2-saturation detector edge case identified by S022 —
see manuscript §3.8 + Appendix C and lab notebooks S013 (lexical lockdown) /
S014 (F-004 causal test) / S021 (F-003 transient regime) / S022 (NSS sub-mode
attribution). This module deliberately does not duplicate that prose; it
implements the locked four-flag contract and points readers to the canonical
explanations.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd


# ---------- Output channels & thresholds ---------- #

# CSV column name per canonical output
OUTPUT_COLUMNS: dict[str, str] = {
    "HR": "HeartRate",
    "MAP": "MeanArterialPressure",
    "Vt": "TidalVolume",
    "SpO2": "OxygenSaturation",
    "PaO2": "ArterialOxygenPressure",
    "PaCO2": "ArterialCarbonDioxidePressure",
}

# Hard physiological bounds — outside ⇒ `implausible`
# Source: preregistration §Flags / hard physiological bounds table.
# These bounds are LOCKED before any sweep run and are not revised post-hoc;
# any revision needs a preregistration amendment with a clear rationale and a
# corresponding bump to the audit log.
HARD_BOUNDS: dict[str, tuple[float, float]] = {
    "HR": (20.0, 220.0),
    "MAP": (30.0, 180.0),
    "Vt": (50.0, 1500.0),
    "SpO2": (0.50, 1.00),  # Pulse reports SpO2 as fraction 0–1, not percent
    "PaO2": (20.0, 600.0),
    "PaCO2": (10.0, 120.0),
}

# Supplementary physiology-anchored bounds — outside ⇒ implausible *under the
# alveolar-gas-equation ceiling for hyperoxia*. PaO2 upper bound is raised from
# 600 to 700 mmHg because the alveolar-gas equation at sea level predicts
# PAO2 = FiO2 × (P_atm − P_H2O) − PaCO2/RQ = 1.0 × (760 − 47) − 40/0.8 ≈ 663
# mmHg in a healthy adult on 100 % O2, with arterial PaO2 reaching ~650 mmHg
# after a typical A-a gradient of 10 mmHg.
#
# This is NOT a replacement for `HARD_BOUNDS` — the locked classifier remains
# the headline atlas classification. `HARD_BOUNDS_PHYSIOLOGICAL` powers a
# sensitivity-analysis side-table reported alongside the locked classifier in
# manuscript §3.8 (F-003 supplementary reclassification). See
# `scripts/f003_physiological_reclassification.py`.
HARD_BOUNDS_PHYSIOLOGICAL: dict[str, tuple[float, float]] = {
    **HARD_BOUNDS,
    "PaO2": (20.0, 700.0),
}


def reclassify_implausible_against(
    pao2_mean: float | pd.Series,
    bounds: dict[str, tuple[float, float]] = HARD_BOUNDS_PHYSIOLOGICAL,
) -> pd.Series | bool:
    """Re-evaluate the PaO2 implausibility check against an alternative bound set.

    Used by ``scripts/f003_physiological_reclassification.py`` to attach a side
    column ``implausible_pao2_under_physio_bounds`` to the locked aggregated
    parquet without modifying the locked classifier.

    Returns a bool (or a boolean Series, if a Series is supplied) — True
    iff the PaO2 mean falls outside the supplied PaO2 bound interval.
    """
    lo, hi = bounds["PaO2"]
    if isinstance(pao2_mean, pd.Series):
        return (pao2_mean < lo) | (pao2_mean > hi)
    return bool(pao2_mean < lo or pao2_mean > hi)


# Max |Δ| over 60 s — slope × 60 s that exceeds this ⇒ `not_steady_state` (drift)
# Units match the Pulse CSV column (SpO2 is fraction, so 0.02 = 2%).
DRIFT_MAX_DELTA_60S: dict[str, float] = {
    "HR": 5.0,
    "MAP": 5.0,
    "Vt": 50.0,
    "SpO2": 0.02,
    "PaO2": 15.0,
    "PaCO2": 5.0,
}

# Coefficient-of-variation threshold for "variance too high"
CV_THRESHOLD: float = 0.05

# Flatline: std < this fraction of |mean|
FLATLINE_STD_RATIO: float = 0.01

# Flatline: mean must also be within this fraction of a hard bound.
# 0.001 (0.1%) distinguishes numerical pinning from physiological ceiling/floor.
# Calibrated on existing Pulse runs: healthy SpO2=0.996 is physiological, not pinned;
# a solver numerically pinned lands at ≥0.999. See preregistration amendment 2026-04-22-b.
FLATLINE_BOUND_TOL: float = 0.001

# Steady-state window: final 60 s of a 120 s simulation
STEADY_STATE_T_LO: float = 60.0
STEADY_STATE_T_HI: float = 120.0

# Clamping detection regexes (case-insensitive) — matched against Pulse stdout/stderr log
#
# Empirically calibrated 2026-04-25 against:
#   - clamp_probe_sbp140 (SBP=140 → loud ERROR + init failure)
#   - 8-run scenario_smoke (mid-range healthy + ARDS, no clamping expected)
#
# Patterns dropped after calibration:
#   - "out of range", "out of bounds"  → matched "Stomach is out of Sodium"
#                                        and "out of CO2/N2/O2" (substance depletion)
#   - "clamp"                          → matched normal solver behaviour text
#   - r"\bexceeds\b"                   → not present in any verified clamp log
#   - "below minimum", "above maximum" → not present in any verified clamp log
#   - "adjusted to"                    → too generic; never seen in real clamp log
#   - "setting .+ to"                  → matched "Resetting the target for X to Y"
#                                        which is normal solver convergence (52 hits/run)
#   - "requires a value"               → not Pulse phrasing
#
# Widened 2026-07-26 (S030b) after a false negative found by direct probing.
# Pulse builds these strings in SetupPatient.cpp, one branch per bound.  Nine of
# the ten write the unit between the value and "is":
#
#   L297  "... baseline of " << heartRate_bpm << " bpm is too high. Maximum ..."
#   L495  "... baseline of " << systolic_mmHg << " mmHg is too low. ..."
#   L580  "... baseline of " << respirationRate_bpm << " bpm is too high. ..."
#
# The heart-rate *lower* bound is the sole exception -- it omits the unit:
#
#   L311  "... baseline of " << heartRate_bpm << " is too low. Minimum ..."
#
# The old pattern required a token between the number and "is", so HR < 50 was
# rejected by Pulse (exit 1, no CSV) yet never flagged `clamped`.  Two changes
# close it: the unit token is now optional, and "minimum ... baseline allowed
# is" mirrors the "maximum" pattern that had no twin -- two independent nets, so
# a future formatting drift in one branch cannot reopen the same hole.
#
# Retroactively safe: replaying both pattern sets over all 3,348 pulse.log files
# on disk flips exactly one run -- the s030b HR-49 probe written to expose this.
# The published 1,280-run sweep is untouched (its inputs never leave HR [50, 110]
# or RR [8, 20]), and no run that produced a CSV becomes `clamped`.
#
# Patterns kept (verified to fire only on genuine init clamping / rejection):
CLAMP_PATTERNS: list[str] = [
    # Pulse's setup-time rejection format. Examples observed:
    #   "Patient systolic pressure baseline of 140 mmHg is too high"
    #   "Patient heart rate baseline of 49 is too low"   <- no unit, see above
    #   "Maximum systolic pressure baseline allowed is 120 mmHg"
    #   "must be modeled by adding/using a condition"
    r"baseline of [\d\.]+ (?:\S+ )?is too (?:high|low)",
    r"maximum [\w\s]+ baseline allowed is",
    r"minimum [\w\s]+ baseline allowed is",
    r"must be modeled by adding/using a condition",
    # The Pulse Setup pipeline emits this when an input is silently substituted.
    r"is outside the valid range",
]


# ---------- Data classes ---------- #


@dataclass
class FlagResult:
    """Per-flag result: fired or not, and a human-readable reason if fired."""

    fired: bool
    reason: str = ""


@dataclass
class SteadyStateStats:
    """Per-channel stats over the final-60 s window."""

    mean: float
    std: float
    cv: float  # coefficient of variation
    slope_per_s: float  # linear-regression slope
    slope_r2: float  # R² of the linear fit (diagnostic, not a threshold)
    delta_60s: float  # slope × 60 s
    n_points: int


@dataclass
class DetectorResult:
    """Full classification of one Pulse run."""

    clamped: FlagResult = field(default_factory=lambda: FlagResult(False))
    diverged: FlagResult = field(default_factory=lambda: FlagResult(False))
    implausible: FlagResult = field(default_factory=lambda: FlagResult(False))
    not_steady_state: FlagResult = field(default_factory=lambda: FlagResult(False))
    stats: dict[str, SteadyStateStats] = field(default_factory=dict)

    @property
    def any_flag(self) -> bool:
        return (
            self.clamped.fired
            or self.diverged.fired
            or self.implausible.fired
            or self.not_steady_state.fired
        )

    @property
    def clean(self) -> bool:
        return not self.any_flag

    @property
    def primary_flag(self) -> str:
        """Highest-priority flag that fired, or "clean" if none.

        Priority hierarchy (locked S013, root-cause severity top-down):

            clamped > diverged > implausible > not_steady_state > clean

        Rationale:
            * clamped     — Pulse silently modified an input; downstream
                            interpretation of any other flag is based on the
                            substituted (not requested) input.
            * diverged    — solver failed; no interpretable output exists.
            * implausible — solver produced a value outside hard physiological
                            bounds; output is mathematically valid but
                            biologically incompatible with life.
            * not_steady_state — output is physiological but did not converge
                            in window; still interpretable as a transient.
        """
        if self.clamped.fired:
            return "clamped"
        if self.diverged.fired:
            return "diverged"
        if self.implausible.fired:
            return "implausible"
        if self.not_steady_state.fired:
            return "not_steady_state"
        return "clean"

    def summary(self) -> dict[str, object]:
        """Flat dict suitable for rolling into a parquet/CSV summary table."""
        return {
            "clamped": self.clamped.fired,
            "clamped_reason": self.clamped.reason,
            "diverged": self.diverged.fired,
            "diverged_reason": self.diverged.reason,
            "implausible": self.implausible.fired,
            "implausible_reason": self.implausible.reason,
            "not_steady_state": self.not_steady_state.fired,
            "not_steady_state_reason": self.not_steady_state.reason,
            "clean": self.clean,
            "primary_flag": self.primary_flag,
        }


# ---------- Individual flag checks ---------- #


def check_clamped(pulse_log: str) -> FlagResult:
    """Flag `clamped` if Pulse log matches any clamping regex."""
    if not pulse_log:
        return FlagResult(False)
    hits: list[str] = []
    for pat in CLAMP_PATTERNS:
        m = re.search(pat, pulse_log, flags=re.IGNORECASE)
        if m:
            hits.append(pat)
    if hits:
        return FlagResult(True, f"log matched: {', '.join(hits)}")
    return FlagResult(False)


def check_diverged(
    csv_path: Path | None,
    df: pd.DataFrame | None,
    exit_code: int,
    expected_t_end: float = STEADY_STATE_T_HI,
) -> FlagResult:
    """Flag `diverged` on missing CSV, NaN/Inf, non-zero exit code, or truncated sim."""
    if exit_code != 0:
        return FlagResult(True, f"exit_code={exit_code}")
    if csv_path is not None and not Path(csv_path).exists():
        return FlagResult(True, f"missing CSV: {csv_path}")
    if df is None or df.empty:
        return FlagResult(True, "empty CSV")
    if "time_s" not in df.columns:
        return FlagResult(True, "CSV missing time_s column")

    # NaN/Inf check on any numeric column
    numeric = df.select_dtypes(include=[np.number])
    if numeric.isna().any().any():
        return FlagResult(True, "NaN in CSV")
    if np.isinf(numeric.to_numpy()).any():
        return FlagResult(True, "Inf in CSV")

    # Truncation: the CSV must reach the expected end time
    t_max = float(df["time_s"].max())
    if t_max + 1e-3 < expected_t_end:
        return FlagResult(True, f"sim truncated: t_max={t_max:.2f} < {expected_t_end:.2f}")
    return FlagResult(False)


def check_implausible(stats: dict[str, SteadyStateStats]) -> FlagResult:
    """Flag `implausible` if any channel's steady-state mean falls outside its hard bound."""
    violations: list[str] = []
    for name, s in stats.items():
        lo, hi = HARD_BOUNDS[name]
        if s.mean < lo or s.mean > hi:
            violations.append(f"{name}={s.mean:.3g} ∉ [{lo}, {hi}]")
    if violations:
        return FlagResult(True, "; ".join(violations))
    return FlagResult(False)


def check_not_steady_state(stats: dict[str, SteadyStateStats]) -> FlagResult:
    """Flag `not_steady_state` if any channel fails flatline / variance / drift checks."""
    problems: list[str] = []
    for name, s in stats.items():
        lo, hi = HARD_BOUNDS[name]

        # Flatline at extreme: std is tiny AND mean is within tol of a hard bound
        if abs(s.mean) > 0:
            std_ratio = s.std / abs(s.mean)
        else:
            std_ratio = 0.0
        near_lo = abs(s.mean - lo) <= FLATLINE_BOUND_TOL * max(abs(lo), 1.0)
        near_hi = abs(s.mean - hi) <= FLATLINE_BOUND_TOL * max(abs(hi), 1.0)
        if std_ratio < FLATLINE_STD_RATIO and (near_lo or near_hi):
            problems.append(f"{name} flatline at extreme (mean={s.mean:.3g})")
            continue

        # Variance too high
        if s.cv > CV_THRESHOLD:
            problems.append(f"{name} CV={s.cv:.3f} > {CV_THRESHOLD}")
            continue

        # Drift over final 60 s
        max_delta = DRIFT_MAX_DELTA_60S[name]
        if abs(s.delta_60s) > max_delta:
            problems.append(f"{name} Δ60s={s.delta_60s:+.3g} > {max_delta}")
            continue

    if problems:
        return FlagResult(True, "; ".join(problems))
    return FlagResult(False)


# ---------- Steady-state stats ---------- #


def _steady_state_window(df: pd.DataFrame) -> pd.DataFrame:
    """Return rows with time_s ∈ [60, 120] (inclusive)."""
    mask = (df["time_s"] >= STEADY_STATE_T_LO - 1e-6) & (df["time_s"] <= STEADY_STATE_T_HI + 1e-6)
    return df.loc[mask].reset_index(drop=True)


def _linear_regression(t: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """OLS slope and R² for y ~ a + b*t. Returns (slope_per_s, r2)."""
    if len(t) < 2:
        return 0.0, float("nan")
    t_mean = t.mean()
    y_mean = y.mean()
    dt = t - t_mean
    dy = y - y_mean
    denom = float((dt * dt).sum())
    if denom <= 0:
        return 0.0, float("nan")
    slope = float((dt * dy).sum()) / denom
    ss_res = float(((y - (y_mean + slope * dt)) ** 2).sum())
    ss_tot = float((dy * dy).sum())
    if ss_tot <= 0:
        r2 = 1.0 if ss_res <= 0 else 0.0
    else:
        r2 = max(0.0, 1.0 - ss_res / ss_tot)
    return slope, r2


def compute_steady_state_stats(df: pd.DataFrame) -> dict[str, SteadyStateStats]:
    """Compute per-channel stats on the final-60 s window.

    Channels missing from the CSV are skipped (caller should have already flagged
    the run as diverged if the CSV is malformed).
    """
    window = _steady_state_window(df)
    t = window["time_s"].to_numpy(dtype=float)
    out: dict[str, SteadyStateStats] = {}
    for name, col in OUTPUT_COLUMNS.items():
        if col not in window.columns:
            continue
        y = window[col].to_numpy(dtype=float)
        if len(y) == 0:
            continue
        mean = float(y.mean())
        std = float(y.std(ddof=0))
        cv = std / abs(mean) if mean != 0 else 0.0
        slope, r2 = _linear_regression(t, y)
        delta_60s = slope * 60.0
        out[name] = SteadyStateStats(
            mean=mean,
            std=std,
            cv=cv,
            slope_per_s=slope,
            slope_r2=r2,
            delta_60s=delta_60s,
            n_points=len(y),
        )
    return out


# ---------- Top-level driver ---------- #


def classify(
    csv_path: Path | str | None,
    pulse_log: str = "",
    exit_code: int = 0,
    expected_t_end: float = STEADY_STATE_T_HI,
) -> DetectorResult:
    """Classify one Pulse run.

    Parameters
    ----------
    csv_path
        Path to the Pulse output CSV. May be None (then `diverged` fires on
        missing CSV unless `df` is injected by a caller).
    pulse_log
        Full stdout+stderr text from the Pulse container. Searched for
        clamping patterns.
    exit_code
        Container exit code. Non-zero ⇒ `diverged`.
    expected_t_end
        Simulation is considered truncated if t_max < this.
    """
    result = DetectorResult()

    # Clamping is independent of CSV state
    result.clamped = check_clamped(pulse_log)

    # Load CSV if present; otherwise let check_diverged handle it
    df: pd.DataFrame | None = None
    p = Path(csv_path) if csv_path is not None else None
    if p is not None and p.exists():
        try:
            df = pd.read_csv(p)
        except Exception as e:  # noqa: BLE001 — any parse failure ⇒ diverged
            result.diverged = FlagResult(True, f"CSV parse error: {e}")
            return result

    result.diverged = check_diverged(p, df, exit_code, expected_t_end=expected_t_end)
    if result.diverged.fired or df is None:
        return result

    result.stats = compute_steady_state_stats(df)
    result.implausible = check_implausible(result.stats)
    result.not_steady_state = check_not_steady_state(result.stats)
    return result


__all__ = [
    "CLAMP_PATTERNS",
    "CV_THRESHOLD",
    "DRIFT_MAX_DELTA_60S",
    "DetectorResult",
    "FLATLINE_STD_RATIO",
    "FlagResult",
    "HARD_BOUNDS",
    "HARD_BOUNDS_PHYSIOLOGICAL",
    "OUTPUT_COLUMNS",
    "STEADY_STATE_T_HI",
    "STEADY_STATE_T_LO",
    "SteadyStateStats",
    "check_clamped",
    "check_diverged",
    "check_implausible",
    "check_not_steady_state",
    "classify",
    "compute_steady_state_stats",
    "reclassify_implausible_against",
]
