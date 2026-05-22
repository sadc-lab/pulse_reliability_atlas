"""Tests for src/aggregator.py.

Builds a synthetic run directory (config + meta + CSV + log) and
verifies the aggregator emits one well-formed row.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src import aggregator as ag


def _write_synthetic_run(
    run_dir: Path, *, hr: float = 75.0, exit_code: int = 0, clean: bool = True
):
    run_dir.mkdir(parents=True, exist_ok=True)
    cfg = {
        "case_id": run_dir.name,
        "condition": "Healthy",
        "duration_hours": 120.0 / 3600.0,
        "sample_interval_s": 5,
        "baselines": {
            "age_yr": 18,
            "weight_kg": 67.3,
            "height_cm": 180.0,
            "sex": "Male",
            "hr": 70,
            "rr": 14,
            "sbp": 105,
            "dbp": 70,
        },
        "ventilator": {
            "mode": "VC-AC",
            "tidal_volume_ml": 550,
            "set_rr": 14,
            "peep_cmh2o": 10,
            "fio2": 0.6,
        },
        "atlas_meta": {
            "scenario": "S1",
            "sex": "M",
            "dbp_requested": 70.0,
            "dbp_applied": 70.0,
            "dbp_was_clipped": False,
            "map_derived": 81.67,
        },
    }
    (run_dir / "config.json").write_text(json.dumps(cfg))
    meta = {
        "case_id": run_dir.name,
        "exit_code": exit_code,
        "wall_time_s": 45.0,
        "image": "pulse-atlas-engine",
    }
    (run_dir / "run_meta.json").write_text(json.dumps(meta))

    # 13-point steady-state window (no flag-triggers if `clean=True`)
    t = np.linspace(60.0, 120.0, 13)
    n = len(t)
    csv = pd.DataFrame(
        {
            "time_s": t,
            "HeartRate": np.full(n, hr),
            "RespirationRate": np.full(n, 15.0),
            "SystolicArterialPressure": np.full(n, 115.0),
            "DiastolicArterialPressure": np.full(n, 75.0),
            "MeanArterialPressure": np.full(n, 90.0),
            "TidalVolume": np.full(n, 500.0) + (np.linspace(0, 5, n) if not clean else 0),
            "OxygenSaturation": np.full(n, 0.97),
            "ArterialOxygenPressure": np.full(n, 95.0),
            "ArterialCarbonDioxidePressure": np.full(n, 40.0),
        }
    )
    csv.to_csv(run_dir / "output.csv", index=False)
    (run_dir / "pulse.log").write_text("[INFO] simulation done\n")


def test_build_row_clean_run(tmp_path):
    rd = tmp_path / "S1_M_TEST"
    _write_synthetic_run(rd, hr=75.0)
    row = ag.build_row(rd)
    assert row["case_id"] == "S1_M_TEST"
    assert row["scenario"] == "S1"
    assert row["sex"] == "M"
    assert row["clean"] is True
    assert row["clamped"] is False
    assert row["diverged"] is False
    assert row["HR_mean"] == 75.0
    assert row["HR_n_points"] == 13


def test_build_row_diverged_on_nonzero_exit(tmp_path):
    rd = tmp_path / "S1_M_DIV"
    _write_synthetic_run(rd, exit_code=1)
    row = ag.build_row(rd)
    assert row["diverged"] is True


def test_build_row_clamped_on_log_match(tmp_path):
    rd = tmp_path / "S1_M_CLAMP"
    _write_synthetic_run(rd)
    log = (
        "[INFO] starting\n"
        "[ERROR] Patient systolic pressure baseline of 140 mmHg is too high. "
        "Maximum systolic pressure baseline allowed is 120 mmHg.\n"
    )
    (rd / "pulse.log").write_text(log)
    row = ag.build_row(rd)
    assert row["clamped"] is True


def test_aggregate_under_walks_dirs(tmp_path):
    for i in range(3):
        _write_synthetic_run(tmp_path / f"S1_M_{i:04d}", hr=70 + i)
    df = ag.aggregate_under(tmp_path)
    assert len(df) == 3
    # Every row has all flag columns
    for col in ("clamped", "diverged", "implausible", "not_steady_state", "clean"):
        assert col in df.columns
