"""Pulse Engine wrapper for the Pulse Reliability Atlas.

Runs *inside* the `pulse-atlas-engine` Docker container. Reads a JSON config,
initializes Pulse 4.3.1 with the requested patient + ARDS condition, attaches
a mechanical ventilator, and writes per-time-step physiology to CSV.

Origin
------
Adapted from `Pulse_translation_new/engine/run_validation_engine.py` (read-only
reference, source-of-truth for the upstream pediatric-translation pipeline).
This file is the *atlas-only* fork. Do not patch the upstream copy from here.

Atlas-specific changes vs upstream
----------------------------------
1. ``FIO2_MAX`` raised from 0.95 → 1.00. Justification: PhD experiment E20
   (April 2026, 9-run probe) verified Pulse 4.3.1 accepts FiO2=1.0 without
   crashing. The 0.95 cap upstream is a residual conservative guard from before
   E20 was run. The atlas needs the full preregistered range [0.21, 1.0]
   (`preregistration.md` §Inputs). Capping at 0.95 would silently clamp ~17%
   of Morris samples at a layer ABOVE Pulse, polluting the atlas's clamping
   characterization with a wrapper artifact rather than a Pulse engine fact.
2. Optional ``baselines.blood_volume_ml`` override. When present, the value
   is injected via ``SEPatient.get_blood_volume_baseline().set_value(mL)``
   before engine initialization. Used by S018 (Phase B item B2) to falsify
   the §3.5 hypothesis that the male divergence cluster is mediated by the
   ~20% blood-volume difference between Pulse's standard male and female
   surrogates: re-run the 20 originally-diverged male inputs with the
   female computed BV (3,996 mL) substituted for the male computed BV
   (4,803 mL). Pulse logs the resolved BV at setup time
   ("No patient blood volume baseline set. Using a computed value..." or
   "Patient blood volume baseline set to ..."), so the override is
   verifiable post hoc from ``pulse.log``.
3. Dynamic ventilation events / spontaneous breathing branches retained but
   unused — atlas runs are static VC-AC only.

Output channels (locked, must include all 6 preregistered outputs)
------------------------------------------------------------------
HR, MAP, Vt, SpO2, PaO2, PaCO2, plus diagnostic channels (SBP, DBP, RR, lung
compliance, I:E, blood pH).
"""

from __future__ import annotations

import argparse
import csv
import json

from pulse.engine.PulseEngine import PulseEngine
from pulse.cdm.engine import SEDataRequest, SEDataRequestManager
from pulse.cdm.patient import SEPatient, SEPatientConfiguration, eSex
from pulse.cdm.physiology import eLungCompartment
from pulse.cdm.mechanical_ventilator import eSwitch
from pulse.cdm.mechanical_ventilator_actions import (
    SEMechanicalVentilatorVolumeControl,
    eMechanicalVentilator_VolumeControlMode,
)
from pulse.cdm.patient_actions import SEIntubation, eIntubationType
from pulse.cdm.scalars import (
    FrequencyUnit,
    LengthUnit,
    MassUnit,
    PressureUnit,
    TimeUnit,
    VolumeUnit,
    VolumePerTimeUnit,
)


# Channels recorded on every time step. Order matters — `_results_to_dict`
# pairs Pulse's results array with this list by index.
OUTPUT_VARIABLES = [
    ("HeartRate",                     FrequencyUnit.Per_min),
    ("RespirationRate",               FrequencyUnit.Per_min),
    ("SystolicArterialPressure",      PressureUnit.mmHg),
    ("DiastolicArterialPressure",     PressureUnit.mmHg),
    ("MeanArterialPressure",          PressureUnit.mmHg),
    ("TidalVolume",                   VolumeUnit.mL),
    ("LungCompliance",                None),
    ("InspiratoryExpiratoryRatio",    None),
    ("OxygenSaturation",              None),
    ("ArterialCarbonDioxidePressure", PressureUnit.mmHg),
    ("ArterialOxygenPressure",        PressureUnit.mmHg),
    ("BloodPH",                       None),
]

# Atlas raises FIO2_MAX to 1.0 — see module docstring.
FIO2_MAX = 1.00

PULSE_MAX_SBP_MMHG = 120.0
PULSE_MAX_DBP_MMHG = 80.0

VENT_SETTLE_S = 120.0

DEFAULT_SAMPLE_INTERVAL_S = 60
DEFAULT_DURATION_HOURS = 4

DEFAULT_FLOW_LPM = 60.0
DEFAULT_INSP_PERIOD_S = 1.0


def build_data_requests(pulse_csv_path: str | None = None) -> SEDataRequestManager:
    requests = []
    for name, unit in OUTPUT_VARIABLES:
        if unit is not None:
            requests.append(SEDataRequest.create_physiology_request(name, unit=unit))
        else:
            requests.append(SEDataRequest.create_physiology_request(name))
    mgr = SEDataRequestManager(requests)
    if pulse_csv_path:
        mgr.set_results_filename(pulse_csv_path)
    return mgr


def initialize_engine(config: dict, data_mgr: SEDataRequestManager) -> PulseEngine:
    pulse = PulseEngine()
    pulse.log_to_console(True)

    case_id = config.get("case_id", "unknown")
    pulse.set_log_filename(f"/pulse/bin/out/{case_id}.log")

    pc = SEPatientConfiguration()
    p = pc.get_patient()
    baselines = config["baselines"]
    p.set_name(f"AtlasCase_{case_id}")
    p.get_age().set_value(baselines["age_yr"], TimeUnit.yr)
    p.get_height().set_value(baselines["height_cm"], LengthUnit.cm)
    p.get_weight().set_value(baselines["weight_kg"], MassUnit.kg)
    sex_str = baselines.get("sex", "Male")
    p.set_sex(eSex.Male if sex_str == "Male" else eSex.Female)
    p.get_heart_rate_baseline().set_value(baselines["hr"], FrequencyUnit.Per_min)
    p.get_respiration_rate_baseline().set_value(baselines["rr"], FrequencyUnit.Per_min)

    sbp = baselines["sbp"]
    dbp = baselines["dbp"]
    if sbp > PULSE_MAX_SBP_MMHG or dbp > PULSE_MAX_DBP_MMHG:
        print(
            f"  WARNING: BP out of Pulse range (SBP={sbp}, DBP={dbp}). "
            f"Atlas sampler should have clipped this."
        )
    p.get_systolic_arterial_pressure_baseline().set_value(sbp, PressureUnit.mmHg)
    p.get_diastolic_arterial_pressure_baseline().set_value(dbp, PressureUnit.mmHg)

    bv_override_ml = baselines.get("blood_volume_ml")
    if bv_override_ml is not None:
        p.get_blood_volume_baseline().set_value(float(bv_override_ml), VolumeUnit.mL)
        print(
            f"  Blood-volume override active: "
            f"BloodVolumeBaseline = {float(bv_override_ml):.2f} mL "
            f"(replaces the weight-derived default for this run)."
        )

    condition = config.get("condition", "Healthy")
    if condition == "ARDS":
        ards_sev = config.get("ards_severity", {"left": 0.6, "right": 0.6})
        ards = pc.get_conditions().get_acute_respiratory_distress_syndrome()
        ards.get_severity(eLungCompartment.LeftLung).set_value(ards_sev.get("left", 0.6))
        ards.get_severity(eLungCompartment.RightLung).set_value(ards_sev.get("right", 0.6))

    pc.set_data_root_dir("/pulse/bin/")

    print(
        f"  Stabilising engine for case {case_id} "
        f"(HR={baselines['hr']}, SBP={baselines['sbp']}, "
        f"DBP={baselines['dbp']}, RR={baselines['rr']}, "
        f"condition={condition})…"
    )

    if not pulse.initialize_engine(pc, data_mgr):
        raise RuntimeError(
            f"Pulse engine failed to stabilise for case {case_id}. "
            f"Check /pulse/bin/out/{case_id}.log for details."
        )

    initial = SEPatient()
    pulse.get_initial_patient(initial)
    print(
        f"  Stabilised — HR={initial.get_heart_rate_baseline()}, "
        f"SBP={initial.get_systolic_arterial_pressure_baseline()}, "
        f"RR={initial.get_respiration_rate_baseline()}"
    )
    return pulse


def _connect_volume_control(pulse: PulseEngine, vent_params: dict) -> None:
    mode = vent_params["mode"]
    fio2 = min(vent_params.get("fio2", 0.4), FIO2_MAX)

    if mode in ("VC-AC", "VC-CMV"):
        action = SEMechanicalVentilatorVolumeControl()
        action.set_connection(eSwitch.On)
        if mode == "VC-AC":
            action.set_mode(eMechanicalVentilator_VolumeControlMode.AssistedControl)
        else:
            action.set_mode(
                eMechanicalVentilator_VolumeControlMode.ContinuousMandatoryVentilation
            )
        action.get_tidal_volume().set_value(vent_params["tidal_volume_ml"], VolumeUnit.mL)
        action.get_respiration_rate().set_value(vent_params["set_rr"], FrequencyUnit.Per_min)
        action.get_positive_end_expired_pressure().set_value(
            vent_params["peep_cmh2o"], PressureUnit.cmH2O
        )
        action.get_fraction_inspired_oxygen().set_value(fio2)
        action.get_flow().set_value(
            vent_params.get("flow_lpm", DEFAULT_FLOW_LPM), VolumePerTimeUnit.L_Per_min
        )
        action.get_inspiratory_period().set_value(
            vent_params.get("insp_period_s", DEFAULT_INSP_PERIOD_S), TimeUnit.s
        )
        # Optional explicit patient trigger pressure (cmH2O, magnitude — Pulse
        # treats the supplied value as an absolute magnitude; sign is ignored
        # internally per `MechanicalVentilatorModel.cpp` line 835). Setting this
        # disables the default `InspirationPatientTriggerRespiratoryModel = On`
        # that VC-AC falls back to when neither flow nor pressure trigger is
        # provided (see SEMechanicalVentilatorVolumeControl.cpp lines 120–128).
        # Used by S014 to causally test whether the respiratory-model trigger
        # is the source of F-004 dyssynchrony.
        trig_p = vent_params.get("inspiration_patient_trigger_pressure_cmh2o")
        if trig_p is not None:
            action.get_inspiration_patient_trigger_pressure().set_value(
                float(trig_p), PressureUnit.cmH2O
            )
        pulse.process_action(action)
    else:
        raise ValueError(
            f"Atlas wrapper supports VC-AC / VC-CMV only; got mode={mode!r}. "
            "Preregistration locks ventilator mode to VC-AC for the atlas sweep."
        )


def apply_ventilation(pulse: PulseEngine, config: dict) -> None:
    vent = config["ventilator"]
    intubation = SEIntubation()
    intubation.set_type(eIntubationType.Tracheal)
    pulse.process_action(intubation)
    _connect_volume_control(pulse, vent)
    print(f"  Ventilator connected ({vent['mode']}). Settling for {VENT_SETTLE_S}s…")
    pulse.advance_time_s(VENT_SETTLE_S)


def run_simulation(pulse: PulseEngine, config: dict) -> list[dict]:
    duration_s = config.get("duration_hours", DEFAULT_DURATION_HOURS) * 3600.0
    interval_s = config.get("sample_interval_s", DEFAULT_SAMPLE_INTERVAL_S)

    # Time origin: recording starts at t=0 *after* the ventilator-settle phase.
    # Pulse's internal sim time has already been advanced by VENT_SETTLE_S, so
    # we subtract that off when emitting CSV. Detector windows in
    # `preregistration.md` §Design ([60, 120] s) reference recording-relative
    # time, not Pulse absolute time.
    t0 = pulse.pull_data()[0]

    time_points: list[dict] = []
    results = pulse.pull_data()
    time_points.append(_results_to_dict(results, t0))

    elapsed = 0.0
    while elapsed < duration_s:
        step = min(interval_s, duration_s - elapsed)
        pulse.advance_time_s(step)
        elapsed += step
        results = pulse.pull_data()
        time_points.append(_results_to_dict(results, t0))
    return time_points


def _results_to_dict(results: list, t0: float = 0.0) -> dict:
    point = {"time_s": results[0] - t0}
    for i, (name, _) in enumerate(OUTPUT_VARIABLES):
        point[name] = results[i + 1]
    return point


def write_results(time_points: list[dict], output_path: str) -> None:
    if not time_points:
        print("  WARNING: No data points collected.")
        return
    fieldnames = list(time_points[0].keys())
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(time_points)


def main() -> None:
    parser = argparse.ArgumentParser(description="Atlas Pulse engine wrapper.")
    parser.add_argument("--config", required=True, help="Path to atlas case config JSON")
    parser.add_argument("--output", required=True, help="Path for output CSV")
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)

    case_id = config.get("case_id", "unknown")
    condition = config.get("condition", "Healthy")
    hours = config.get("duration_hours", DEFAULT_DURATION_HOURS)
    mode_desc = config["ventilator"]["mode"]

    print("=" * 60)
    print(f"  Atlas Pulse Run — Case {case_id}")
    print(f"  Condition: {condition}  |  Mode: {mode_desc}  |  Duration: {hours}h")
    print("=" * 60)

    pulse_csv = args.output.replace(".csv", "_pulse_native.csv")
    data_mgr = build_data_requests(pulse_csv)

    pulse = initialize_engine(config, data_mgr)
    apply_ventilation(pulse, config)
    print(f"  Running simulation for {hours} hours…")
    time_points = run_simulation(pulse, config)

    write_results(time_points, args.output)
    print(f"  {len(time_points)} snapshots written to {args.output}")
    print(f"  Pulse native CSV at {pulse_csv}")

    pulse.clear()
    print("=" * 60)
    print("  Done.")
    print("=" * 60)


if __name__ == "__main__":
    main()
