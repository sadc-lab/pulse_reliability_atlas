"""S030b -- two remaining blocks: severe-band robustness, and HR/RR acceptance bounds.

BLOCK 1 (8 runs) -- where does the severe band become robust?
S030 showed fraction 0.95 is severe at the atlas window but MODERATE by
[240,300] s under a free trigger (86.8 -> 112.8 P/F), while the trigger-locked
arm stays severe (69.1 -> 91.8).  Fractions 0.96-0.99 x both arms locate the
point, if any, where "severe" survives both the longer window and the free
trigger.  If it does not appear cleanly here we stop and simply document the
drift, per the agreed stop rule.

BLOCK 2 (8 runs) -- the HR/RR acceptance bounds.
The paper asserts three times that Pulse accepts HR only in 50-110 bpm and RR
only in 8-20 bpm, citing companion boundary probes.  Our 1,280-run sweep
proves those values are ACCEPTED -- every run used them -- but never that 49
or 111 are REJECTED.  These eight runs test both sides of each bound:
expect 49 / 111 / 7 / 21 to fail at setup and 50 / 110 / 8 / 20 to complete.

No variance block: S007 establishes Pulse is deterministic and bit-exact for
fixed inputs, so repeated identical configs return identical output.

Touches no manuscript.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.runner import MAX_PARALLEL_LAPTOP, run_many  # noqa: E402
from src.scenario import PATIENTS, derive_map  # noqa: E402

RUNS = REPO / "data" / "runs" / "s030b_severe_and_bounds"

BASE = {"hr": 70, "rr": 16, "sbp": 118, "dbp": 70}
VENT = {"mode": "VC-AC", "set_rr": 16, "peep_cmh2o": 10, "fio2": 0.40}
VT_M = 403.8
TRIGGER_LOCK_CMH2O = -2.0

SEVERE_GRID = [0.96, 0.97, 0.98, 0.99]
# both sides of each documented bound; 49/111/7/21 are expected to be rejected
HR_PROBE = [49, 50, 110, 111]
RR_PROBE = [7, 8, 20, 21]


def _cfg(case_id: str, *, severity: float | None, hr: float, rr: float,
         locked: bool, duration_s: float) -> dict[str, Any]:
    pat = PATIENTS["M"]
    cfg: dict[str, Any] = {
        "case_id": case_id,
        "condition": "ARDS" if severity else "Healthy",
        "duration_hours": duration_s / 3600.0,
        "sample_interval_s": 5,
        "baselines": {
            "age_yr": pat.age_yr, "weight_kg": pat.weight_kg,
            "height_cm": pat.height_cm, "sex": pat.sex,
            "hr": hr, "rr": rr, "sbp": BASE["sbp"], "dbp": BASE["dbp"],
        },
        "ventilator": {
            "mode": VENT["mode"], "tidal_volume_ml": VT_M,
            "set_rr": rr, "peep_cmh2o": VENT["peep_cmh2o"],
            "fio2": VENT["fio2"],
            **({"inspiration_patient_trigger_pressure_cmh2o": TRIGGER_LOCK_CMH2O}
               if locked else {}),
        },
        "atlas_meta": {
            "scenario": "S030b", "sex": "M",
            "dbp_requested": BASE["dbp"], "dbp_applied": BASE["dbp"],
            "dbp_was_clipped": False,
            "map_derived": derive_map(BASE["sbp"], BASE["dbp"]),
        },
    }
    if severity:
        cfg["ards_severity"] = {"left": float(severity), "right": float(severity)}
    return cfg


def main() -> int:
    RUNS.mkdir(parents=True, exist_ok=True)
    jobs = []

    for arm, locked in (("fr", False), ("lk", True)):
        for sev in SEVERE_GRID:
            cid = f"s030b_{arm}_M_{sev:.3f}".replace(".", "p")
            jobs.append((_cfg(cid, severity=sev, hr=BASE["hr"], rr=BASE["rr"],
                              locked=locked, duration_s=300.0), cid))

    for hr in HR_PROBE:
        cid = f"s030b_bound_hr{hr}"
        jobs.append((_cfg(cid, severity=None, hr=hr, rr=BASE["rr"],
                          locked=False, duration_s=120.0), cid))
    for rr in RR_PROBE:
        cid = f"s030b_bound_rr{rr}"
        jobs.append((_cfg(cid, severity=None, hr=BASE["hr"], rr=rr,
                          locked=False, duration_s=120.0), cid))

    print(f"S030b: {len(jobs)} runs, {MAX_PARALLEL_LAPTOP} parallel")
    n_locked = sum(1 for c, _ in jobs
                   if "inspiration_patient_trigger_pressure_cmh2o" in c["ventilator"])
    assert n_locked == len(SEVERE_GRID), f"trigger key on {n_locked}, expected {len(SEVERE_GRID)}"
    print(f"  pre-flight: trigger-lock on {n_locked} configs")

    res = run_many(jobs, runs_root=RUNS, max_workers=MAX_PARALLEL_LAPTOP,
                   timeout_s=900.0)
    df = pd.DataFrame([{"case_id": r.case_id,
                        "exit_code": getattr(r, "exit_code", None)} for r in res])
    out = REPO / "results" / "s030b_run_index.csv"
    df.to_csv(out, index=False)
    print(f"\n-> {out}")
    print(df.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
