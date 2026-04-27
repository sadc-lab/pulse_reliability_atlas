"""S009 — continuous ARDS-severity sweep (Tier 2).

Holds Morris inputs at midrange and varies ARDS impairment severity
continuously across [0, 1]. Tests whether the all-male divergence
pattern (S006 H3) corresponds to a continuous regime or to discrete
severity levels.

Design:
    * 100 severity values, denser around the documented 0.91-0.945
      instability zone:
          - 50 uniform in [0.0, 0.85]
          - 30 uniform in [0.85, 0.95]
          - 20 uniform in [0.95, 1.0]
    * Both sexes (M and F).
    * Total: 200 runs.
    * Inputs at midrange (HR=80, SBP=105, DBP=70, RR=14, Vt=550,
      FiO2=0.6, PEEP=10) — same point used in S004 scenario smoke,
      well-behaved for all 8 cells.

Output:
    data/runs/continuous_ards/
    results/continuous_ards_severity_sweep.parquet
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.aggregator import aggregate_under, write_parquet  # noqa: E402
from src.runner import run_many  # noqa: E402
from src.scenario import (  # noqa: E402
    DURATION_HOURS,
    PATIENTS,
    SAMPLE_INTERVAL_S,
    VENT_MODE,
    derive_map,
)

RUN_ROOT = REPO_ROOT / "data" / "runs" / "continuous_ards"
RESULTS = REPO_ROOT / "results"

MIDRANGE = {
    "hr": 80.0,
    "sbp": 105.0,
    "dbp": 70.0,
    "rr": 14.0,
    "vt": 550.0,
    "fio2": 0.6,
    "peep": 10.0,
}


def severity_grid() -> np.ndarray:
    """Densified grid over [0, 1] with extra coverage near 0.91-0.945 zone."""
    rng = np.random.default_rng(2026)
    a = rng.uniform(0.0, 0.85, size=50)
    b = rng.uniform(0.85, 0.95, size=30)
    c = rng.uniform(0.95, 1.0, size=20)
    grid = np.sort(np.concatenate([a, b, c]))
    return grid


def build_continuous_config(severity: float, sex_key: str, case_id: str) -> dict[str, Any]:
    pat = PATIENTS[sex_key]
    cfg: dict[str, Any] = {
        "case_id": case_id,
        "condition": "Healthy" if severity == 0.0 else "ARDS",
        "duration_hours": DURATION_HOURS,
        "sample_interval_s": SAMPLE_INTERVAL_S,
        "baselines": {
            "age_yr": pat.age_yr,
            "weight_kg": pat.weight_kg,
            "height_cm": pat.height_cm,
            "sex": pat.sex,
            "hr": MIDRANGE["hr"],
            "rr": MIDRANGE["rr"],
            "sbp": MIDRANGE["sbp"],
            "dbp": MIDRANGE["dbp"],
        },
        "ventilator": {
            "mode": VENT_MODE,
            "tidal_volume_ml": MIDRANGE["vt"],
            "set_rr": MIDRANGE["rr"],
            "peep_cmh2o": MIDRANGE["peep"],
            "fio2": MIDRANGE["fio2"],
        },
        "atlas_meta": {
            "scenario": "ContARDS",
            "sex": sex_key,
            "ards_severity_continuous": float(severity),
            "dbp_requested": MIDRANGE["dbp"],
            "dbp_applied": MIDRANGE["dbp"],
            "dbp_was_clipped": False,
            "map_derived": derive_map(MIDRANGE["sbp"], MIDRANGE["dbp"]),
        },
    }
    if severity > 0.0:
        cfg["ards_severity"] = {"left": float(severity), "right": float(severity)}
    return cfg


def main() -> int:
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    grid = severity_grid()
    print(f"[cont-ards] {len(grid)} severities x 2 sexes = {len(grid)*2} runs")

    jobs = []
    for sex_key in ("M", "F"):
        for i, sev in enumerate(grid):
            cid = f"CONT_{sex_key}_{i:03d}_sev{int(sev*1000):04d}"
            cfg = build_continuous_config(float(sev), sex_key, cid)
            jobs.append((cfg, cid))

    run_many(jobs, runs_root=RUN_ROOT, overwrite=False)

    df = aggregate_under(RUN_ROOT)
    # Add severity column for analysis (pull from atlas_meta via re-reading configs)
    severities = []
    for _, row in df.iterrows():
        # cid format CONT_<sex>_<idx>_sev<int>
        try:
            sev = float(row["case_id"].split("sev")[-1]) / 1000.0
        except Exception:  # noqa: BLE001
            sev = float("nan")
        severities.append(sev)
    df["ards_severity_continuous"] = severities

    out = RESULTS / "continuous_ards_severity_sweep.parquet"
    write_parquet(df, out)
    print(f"[cont-ards] aggregated -> {out.relative_to(REPO_ROOT)}")
    print(f"[cont-ards] total rows: {len(df)}")
    print(f"[cont-ards] diverged: {int(df['diverged'].sum())}/{len(df)}")
    print(f"[cont-ards] by sex: M_div={int(df[(df.sex=='M')&df.diverged].shape[0])}, F_div={int(df[(df.sex=='F')&df.diverged].shape[0])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
