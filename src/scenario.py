"""Scenario builder: convert a Morris sample row into an atlas Pulse config.

The atlas sweep is a 4 (scenarios) × 2 (sexes) × N (Morris points) factorial.
For every cell, every Morris row produces one ``config.json`` consumed by
``pulse-atlas-engine`` (`engine/run_atlas_engine.py`).

Locked design (`preregistration.md`):
    - 4 scenarios (S1..S4) — healthy + 3 ARDS severities (0.00 / 0.26 / 0.60 / 0.95).
    - 2 patients (Pulse standards: M = 18y/67.3kg/180cm, F = 18y/56.2kg/163cm).
    - VC-AC ventilator only.
    - 120 s simulation, 5 s sample interval ⇒ 13 points in [60, 120].
    - DBP/SBP ≤ 0.75 enforced HERE (not in sampler) so Morris geometry stays
      intact; both ``dbp_requested`` and ``dbp_applied`` are persisted.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import pandas as pd


# ---------- Patients ---------- #


@dataclass(frozen=True)
class Patient:
    sex: str  # "Male" / "Female"
    age_yr: int
    weight_kg: float
    height_cm: float


# Pulse standard patients — locked by `preregistration.md` §Patient surrogates.
PATIENTS: dict[str, Patient] = {
    "M": Patient(sex="Male",   age_yr=18, weight_kg=67.3, height_cm=180.0),
    "F": Patient(sex="Female", age_yr=18, weight_kg=56.2, height_cm=163.0),
}


# ---------- Scenarios ---------- #


@dataclass(frozen=True)
class Scenario:
    """One atlas scenario: healthy or ARDS at a given severity."""

    sid: str               # "S1".."S4"
    label: str             # human-readable
    ards_severity: float   # 0.0 ⇒ healthy, otherwise ARDS impairment fraction


SCENARIOS: dict[str, Scenario] = {
    "S1": Scenario("S1", "Healthy",         0.00),
    "S2": Scenario("S2", "Mild ARDS",       0.26),
    "S3": Scenario("S3", "Moderate ARDS",   0.60),
    "S4": Scenario("S4", "Severe ARDS",     0.95),
}


# ---------- Constants ---------- #

# Pulse 4.3.1 init constraint — DBP/SBP must satisfy this ratio else Pulse
# silently clamps the offending value. Atlas enforces it pre-submission so the
# `clamped` flag isolates *Pulse-engine* clamping, not a known trivial input
# violation.
PULSE_DBP_SBP_MAX_RATIO: float = 0.75

# Locked simulation cadence (`preregistration.md` §Design)
DURATION_HOURS: float = 120.0 / 3600.0  # 120 s
SAMPLE_INTERVAL_S: int = 5

# Locked ventilator mode
VENT_MODE: str = "VC-AC"


# ---------- Helpers ---------- #


def derive_map(sbp: float, dbp: float) -> float:
    """Mean arterial pressure from SBP/DBP. MAP is *derived*, not swept."""
    return dbp + (sbp - dbp) / 3.0


def clip_dbp_to_pulse_constraint(sbp: float, dbp_requested: float) -> tuple[float, bool]:
    """Clip DBP so DBP/SBP ≤ PULSE_DBP_SBP_MAX_RATIO.

    Returns (dbp_applied, was_clipped).
    """
    cap = PULSE_DBP_SBP_MAX_RATIO * sbp
    if dbp_requested > cap:
        return cap, True
    return dbp_requested, False


# ---------- Config builder ---------- #


def build_config(
    sample_row: pd.Series,
    scenario_key: str,
    sex_key: str,
    case_id: str,
    clip_dbp: bool = True,
    trigger_pressure_cmh2o: float | None = None,
) -> dict[str, Any]:
    """Build one atlas config dict for a given Morris sample point.

    Parameters
    ----------
    sample_row
        A row from `sampler.sample_morris(...)`. Required columns: hr, sbp,
        dbp, rr, vt, fio2, peep.
    scenario_key
        One of ``"S1"``..``"S4"`` (see `SCENARIOS`).
    sex_key
        ``"M"`` or ``"F"`` (see `PATIENTS`).
    case_id
        Stable identifier; used as both the Pulse log filename and the run
        directory name.
    clip_dbp
        If True (default), clip DBP to the Pulse acceptance envelope. Set to
        False only for deliberate clamp probes that need to submit out-of-range
        values (e.g. pilot gate G4).
    trigger_pressure_cmh2o
        If provided, sets `InspirationPatientTriggerPressure` on the VC-AC
        action. Disables Pulse's default fallback to a respiratory-model-driven
        patient trigger. Used by S014 to test the F-004 dyssynchrony mechanism.
        None (default) preserves the original sweep behaviour.
    """
    if scenario_key not in SCENARIOS:
        raise KeyError(f"unknown scenario {scenario_key!r}")
    if sex_key not in PATIENTS:
        raise KeyError(f"unknown sex {sex_key!r}")

    sc = SCENARIOS[scenario_key]
    pat = PATIENTS[sex_key]

    sbp = float(sample_row["sbp"])
    dbp_requested = float(sample_row["dbp"])
    if clip_dbp:
        dbp_applied, was_clipped = clip_dbp_to_pulse_constraint(sbp, dbp_requested)
    else:
        dbp_applied, was_clipped = dbp_requested, False

    config: dict[str, Any] = {
        "case_id": case_id,
        "condition": "Healthy" if sc.ards_severity == 0.0 else "ARDS",
        "duration_hours": DURATION_HOURS,
        "sample_interval_s": SAMPLE_INTERVAL_S,
        "baselines": {
            "age_yr": pat.age_yr,
            "weight_kg": pat.weight_kg,
            "height_cm": pat.height_cm,
            "sex": pat.sex,
            "hr": float(sample_row["hr"]),
            "rr": float(sample_row["rr"]),
            "sbp": sbp,
            "dbp": dbp_applied,
        },
        "ventilator": {
            "mode": VENT_MODE,
            "tidal_volume_ml": float(sample_row["vt"]),
            "set_rr": float(sample_row["rr"]),
            "peep_cmh2o": float(sample_row["peep"]),
            "fio2": float(sample_row["fio2"]),
            **(
                {"inspiration_patient_trigger_pressure_cmh2o": float(trigger_pressure_cmh2o)}
                if trigger_pressure_cmh2o is not None
                else {}
            ),
        },
        # Atlas metadata — preserved through to the aggregated Parquet so that
        # Morris EE can use the requested (pre-clip) DBP and clamping analysis
        # can distinguish atlas-level clipping from Pulse-level clamping.
        "atlas_meta": {
            "scenario": scenario_key,
            "sex": sex_key,
            "dbp_requested": dbp_requested,
            "dbp_applied": dbp_applied,
            "dbp_was_clipped": was_clipped,
            "map_derived": derive_map(sbp, dbp_applied),
        },
    }

    if sc.ards_severity > 0.0:
        config["ards_severity"] = {
            "left":  sc.ards_severity,
            "right": sc.ards_severity,
        }

    return config


def iter_cells() -> Iterable[tuple[str, str]]:
    """Yield (scenario_key, sex_key) tuples — full 4 × 2 = 8-cell grid."""
    for sk in SCENARIOS:
        for xk in PATIENTS:
            yield sk, xk


def case_id(scenario_key: str, sex_key: str, run_idx: int) -> str:
    """Stable run identifier: '{scenario}_{sex}_{idx:04d}'."""
    return f"{scenario_key}_{sex_key}_{run_idx:04d}"


__all__ = [
    "DURATION_HOURS",
    "PATIENTS",
    "PULSE_DBP_SBP_MAX_RATIO",
    "Patient",
    "SAMPLE_INTERVAL_S",
    "SCENARIOS",
    "Scenario",
    "VENT_MODE",
    "build_config",
    "case_id",
    "clip_dbp_to_pulse_constraint",
    "derive_map",
    "iter_cells",
]
