"""Tests for src/scenario.py.

Verifies config builder produces preregistration-compliant Pulse configs:
correct patient surrogates, ARDS condition strings, derived MAP, and the
DBP/SBP <= 0.75 clip rule.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src import scenario as sc


@pytest.fixture
def midrange_row() -> pd.Series:
    return pd.Series(
        {
            "hr": 80.0,
            "sbp": 105.0,
            "dbp": 70.0,
            "rr": 14.0,
            "vt": 550.0,
            "fio2": 0.6,
            "peep": 10.0,
        }
    )


def test_patients_locked():
    """Pulse standard adult M and F demographics."""
    assert sc.PATIENTS["M"].sex == "Male"
    assert sc.PATIENTS["M"].weight_kg == 67.3
    assert sc.PATIENTS["M"].height_cm == 180.0
    assert sc.PATIENTS["F"].sex == "Female"
    assert sc.PATIENTS["F"].weight_kg == 56.2
    assert sc.PATIENTS["F"].height_cm == 163.0


def test_scenarios_locked():
    """4 scenarios at preregistered severities."""
    assert sc.SCENARIOS["S1"].ards_severity == 0.00
    assert sc.SCENARIOS["S2"].ards_severity == 0.26
    assert sc.SCENARIOS["S3"].ards_severity == 0.60
    assert sc.SCENARIOS["S4"].ards_severity == 0.95


def test_simulation_cadence_locked():
    """120 s sim, 5 s sample interval, VC-AC."""
    assert sc.DURATION_HOURS == 120.0 / 3600.0
    assert sc.SAMPLE_INTERVAL_S == 5
    assert sc.VENT_MODE == "VC-AC"


def test_derive_map():
    """MAP = DBP + (SBP - DBP) / 3."""
    assert sc.derive_map(120, 60) == pytest.approx(80.0)
    assert sc.derive_map(105, 70) == pytest.approx(70 + 35 / 3)


def test_clip_dbp_under_constraint():
    """DBP within constraint returns unchanged + was_clipped=False."""
    applied, clipped = sc.clip_dbp_to_pulse_constraint(sbp=120, dbp_requested=80)
    assert applied == 80
    assert not clipped


def test_clip_dbp_violates_constraint():
    """DBP above 0.75*SBP gets clipped + was_clipped=True."""
    applied, clipped = sc.clip_dbp_to_pulse_constraint(sbp=90, dbp_requested=80)
    assert applied == pytest.approx(67.5)
    assert clipped


def test_build_config_healthy(midrange_row):
    """S1 (healthy) config has condition='Healthy', no ards_severity."""
    cfg = sc.build_config(midrange_row, "S1", "M", "S1_M_TEST")
    assert cfg["condition"] == "Healthy"
    assert "ards_severity" not in cfg
    assert cfg["baselines"]["sex"] == "Male"
    assert cfg["ventilator"]["mode"] == "VC-AC"
    assert cfg["sample_interval_s"] == 5


def test_build_config_ards(midrange_row):
    """S3 config has condition='ARDS', ards_severity=0.6."""
    cfg = sc.build_config(midrange_row, "S3", "F", "S3_F_TEST")
    assert cfg["condition"] == "ARDS"
    assert cfg["ards_severity"] == {"left": 0.6, "right": 0.6}
    assert cfg["baselines"]["sex"] == "Female"


def test_build_config_dbp_clip_metadata(midrange_row):
    """When DBP clipped, atlas_meta records both requested and applied values."""
    row = midrange_row.copy()
    row["sbp"] = 90.0
    row["dbp"] = 80.0  # 80 > 0.75*90 = 67.5 -> clip
    cfg = sc.build_config(row, "S1", "M", "TEST")
    meta = cfg["atlas_meta"]
    assert meta["dbp_requested"] == 80.0
    assert meta["dbp_applied"] == pytest.approx(67.5)
    assert meta["dbp_was_clipped"]
    # config sent to Pulse uses applied value
    assert cfg["baselines"]["dbp"] == pytest.approx(67.5)


def test_build_config_clip_bypass(midrange_row):
    """clip_dbp=False bypasses the clip — used for deliberate clamp probes."""
    row = midrange_row.copy()
    row["sbp"] = 90.0
    row["dbp"] = 85.0
    cfg = sc.build_config(row, "S1", "M", "PROBE", clip_dbp=False)
    assert cfg["baselines"]["dbp"] == 85.0
    assert not cfg["atlas_meta"]["dbp_was_clipped"]


def test_build_config_unknown_scenario_raises(midrange_row):
    with pytest.raises(KeyError):
        sc.build_config(midrange_row, "S99", "M", "X")


def test_build_config_unknown_sex_raises(midrange_row):
    with pytest.raises(KeyError):
        sc.build_config(midrange_row, "S1", "X", "X")


def test_iter_cells_full_grid():
    """Full 4 × 2 = 8-cell grid."""
    cells = list(sc.iter_cells())
    assert len(cells) == 8
    assert all(sk in sc.SCENARIOS for sk, _ in cells)
    assert all(xk in sc.PATIENTS for _, xk in cells)


def test_case_id_format():
    assert sc.case_id("S1", "M", 0) == "S1_M_0000"
    assert sc.case_id("S4", "F", 159) == "S4_F_0159"
