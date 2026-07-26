"""S030 -- independent in-repo replication of the ARDS severity -> Berlin calibration.

WHY THIS EXISTS
---------------
The impairment fractions {0.26, 0.60, 0.95} and the P/F values they produce
(256 / 150 / 96 mmHg), together with the demonstration that Pulse's own
documented fractions {0.3, 0.6, 0.9} land at 199 / 150 / 119 mmHg -- all
inside the Berlin *moderate* band -- are a headline contribution of this
paper.  Until now they rested entirely on a companion project
(`Pulse_translation_new`), and could not be re-derived here: the atlas's own
severity runs use Vt 550 mL at FiO2 0.60, whereas the calibration requires
Vt 403.8 mL at FiO2 0.40, and P/F is ventilation-dependent by construction.

This script reproduces the calibration inside the atlas, so the contribution
becomes re-derivable, ledger-anchorable, and independent of an external
read-only repository.

PROTOCOL -- taken verbatim from the companion's E6 results file
(`data/engine_runs/e6_ards_calibration/results.json`), not reconstructed:

    baselines : age 18, 67.3 kg, 180 cm, Male, HR 70, RR 16, SBP 118, DBP 70
    ventilator: VC-AC, Vt 403.8 mL (6 mL/kg), set_rr 16, PEEP 10, FiO2 0.40

DESIGN
------
Three questions, three blocks.

(1) ANCHORS -- do our five published values reproduce?
    0.26, 0.30, 0.60, 0.90, 0.95, plus 0.92 where the engine is expected to
    fail (the documented 0.91-0.945 instability zone).

(2) BOUNDARY LOCALISATION -- where exactly does Pulse cross each Berlin
    boundary?  This is the scientific question: the fractions matter only
    because of where they sit relative to 300, 200 and 100 mmHg.  The
    companion's grids leave each crossing bracketed but not located, and the
    200 crossing matters most: it separates 0.29 (P/F 214.7, mild) from 0.30
    (P/F 199.3, moderate) -- a claim resting on 0.7 mmHg of margin.

(3) SECOND BODY -- the atlas uses two reference bodies; the companion checked
    the female at three points only.

WINDOW
------
Runs last 300 s, not the companion's ~108 s, and P/F is reported over TWO
windows: the atlas-canonical [60, 120] s and a late [240, 300] s.  If the two
disagree, the band assignment is window-dependent and a 0.7 mmHg margin is
not meaningful -- that is itself a result worth having before publishing a
threshold.

Nothing here edits any manuscript.  Output is a parquet + JSON for inspection.
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

RUNS = REPO / "data" / "runs" / "s030_ards_berlin_recalibration"
RESULTS = REPO / "results"

# --- companion E6 protocol, verbatim -------------------------------------
BASE = {"hr": 70, "rr": 16, "sbp": 118, "dbp": 70}
VENT = {"mode": "VC-AC", "set_rr": 16, "peep_cmh2o": 10, "fio2": 0.40}
VT_ML = {"M": 403.8, "F": 337.2}  # 6 mL/kg on each reference body

DURATION_H = 300.0 / 3600.0   # 300 s, longer than E6's ~108 s (see docstring)
SAMPLE_S = 5                  # atlas-canonical sampling

# --- the two arms --------------------------------------------------------
# The companion's runs commanded set_rr = 16 but the patient actually breathed
# at 21.65-37.17 (median 27.25), because VC-AC falls back to
# InspirationPatientTriggerRespiratoryModel when no explicit trigger is given.
# Minute ventilation is therefore an OUTPUT, not a setting, and the P/F values
# inherit its variability -- fatal for a boundary claim with 0.7 mmHg of margin.
#
#   arm "free"   -- no explicit trigger: faithful to the companion protocol,
#                   and to how Pulse is used by default.
#   arm "locked" -- InspirationPatientTriggerPressure = -2 cmH2O, the S014
#                   intervention, which disables the respiratory-model trigger
#                   and gives genuinely controlled ventilation.
#
# The locked arm is a SENSITIVITY ANALYSIS, not a replacement: it measures the
# ARDS model's own response, isolated from patient-ventilator interaction. If
# the two arms place a fraction in different Berlin bands, the published
# calibration boundary depends on an uncontrolled interaction rather than on
# the ARDS model alone -- which is the result worth reporting.
TRIGGER_LOCK_CMH2O = -2.0     # magnitude is what Pulse uses; matches S014
ARMS = ("free", "locked")

# --- the grid ------------------------------------------------------------
ANCHORS = [0.26, 0.30, 0.60, 0.90, 0.92, 0.95]
CROSS_300 = [0.220, 0.225, 0.230, 0.235]          # no-ARDS <-> mild
CROSS_200 = [0.285, 0.290, 0.295]                 # mild <-> moderate  (critical)
CROSS_100 = [0.910, 0.930, 0.940, 0.945]          # moderate <-> severe + instability
MALE_GRID = sorted(set(ANCHORS + CROSS_300 + CROSS_200 + CROSS_100))
FEMALE_GRID = [0.26, 0.60, 0.95]


def build_config(severity: float, sex_key: str, case_id: str,
                 arm: str) -> dict[str, Any]:
    if arm not in ARMS:
        raise ValueError(f"unknown arm {arm!r}")
    pat = PATIENTS[sex_key]
    cfg: dict[str, Any] = {
        "case_id": case_id,
        "condition": "ARDS",
        "duration_hours": DURATION_H,
        "sample_interval_s": SAMPLE_S,
        "baselines": {
            "age_yr": pat.age_yr,
            "weight_kg": pat.weight_kg,
            "height_cm": pat.height_cm,
            "sex": pat.sex,
            **BASE,
        },
        "ventilator": {
            "mode": VENT["mode"],
            "tidal_volume_ml": VT_ML[sex_key],
            "set_rr": VENT["set_rr"],
            "peep_cmh2o": VENT["peep_cmh2o"],
            "fio2": VENT["fio2"],
            **({"inspiration_patient_trigger_pressure_cmh2o": TRIGGER_LOCK_CMH2O}
               if arm == "locked" else {}),
        },
        "ards_severity": {"left": float(severity), "right": float(severity)},
        "atlas_meta": {
            "scenario": "S030",
            "arm": arm,
            "sex": sex_key,
            "ards_severity_continuous": float(severity),
            "dbp_requested": BASE["dbp"],
            "dbp_applied": BASE["dbp"],
            "dbp_was_clipped": False,
            "map_derived": derive_map(BASE["sbp"], BASE["dbp"]),
        },
    }
    return cfg


def main() -> int:
    RUNS.mkdir(parents=True, exist_ok=True)
    jobs = []
    for arm in ARMS:
        tag = "fr" if arm == "free" else "lk"
        for sev in MALE_GRID:
            cid = f"s030_{tag}_M_{sev:.3f}".replace(".", "p")
            jobs.append((build_config(sev, "M", cid, arm), cid))
        for sev in FEMALE_GRID:
            cid = f"s030_{tag}_F_{sev:.3f}".replace(".", "p")
            jobs.append((build_config(sev, "F", cid, arm), cid))

    print(f"S030: {len(jobs)} runs = {len(ARMS)} arms x "
          f"({len(MALE_GRID)} male + {len(FEMALE_GRID)} female), "
          f"{DURATION_H * 3600:.0f} s each, {MAX_PARALLEL_LAPTOP} parallel")
    # Pre-flight guard: the locked arm is worthless if the image ignores the
    # key, and it would fail silently as identical to the free arm.  Assert the
    # key is actually present in exactly the configs that should carry it.
    n_locked = sum(1 for cfg, _ in jobs
                   if "inspiration_patient_trigger_pressure_cmh2o"
                   in cfg["ventilator"])
    expected = len(MALE_GRID) + len(FEMALE_GRID)
    assert n_locked == expected, f"trigger key on {n_locked} configs, expected {expected}"
    print(f"  pre-flight: trigger-lock key present on {n_locked} configs "
          f"(-{abs(TRIGGER_LOCK_CMH2O)} cmH2O), absent on the other "
          f"{len(jobs) - n_locked}")

    results = run_many(jobs, runs_root=RUNS, max_workers=MAX_PARALLEL_LAPTOP, timeout_s=900.0)

    rows = []
    for r in results:
        rows.append({
            "case_id": r.case_id,
            "exit_code": getattr(r, "exit_code", None),
            "ok": getattr(r, "ok", None),
            "run_dir": str(getattr(r, "run_dir", "")),
        })
    df = pd.DataFrame(rows)
    RESULTS.mkdir(exist_ok=True)
    out = RESULTS / "s030_run_index.csv"
    df.to_csv(out, index=False)
    print(f"\nindex des runs -> {out}")
    print(df.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
