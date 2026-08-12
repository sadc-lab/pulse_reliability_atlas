"""Compare every submitted operational input against Pulse's own post-ingestion
representation of it, for all 1,280 sweep runs.

WHY THIS EXISTS
---------------
The atlas publishes ``0 / 1,280`` for the ``clamped`` flag and reads it as
"Pulse never silently bent a setup input". That flag is a regex over Pulse's
*setup-rejection* log lines, so it detects LOUD rejection. A genuinely silent
substitution writes no rejection string and therefore cannot fire it: the
absence of silent clamping is currently *inferred*, not *measured*
(``audit/silent_clamping_instrument.md``).

Every run directory already stores what is needed to measure it directly, so
this runs on committed artefacts with no re-execution of the sweep and no
Docker image.

THE FOUR LAYERS -- AND WHY THEY MUST NOT BE COLLAPSED
-----------------------------------------------------
    sampled  ->  wrapper-applied  ->  Pulse post-ingestion  ->  runtime

    delta_wrapper = wrapper_applied     - sampled
    delta_setup   = pulse_instantiated  - wrapper_applied     <-- answers H2

``delta_setup`` is the only one that speaks to H2. Collapsing the first two
would charge Pulse with our own pulse-pressure clip (DBP/SBP <= 0.75), which
fires on 35 of the 160 design points, i.e. 280 of 1,280 runs.

The runtime layer is deliberately NOT computed here. Pulse re-targets the VC-AC
tidal volume during a run ("Resetting the target for TidalVolume to Y"), in
1,280 / 1,280 logs; that is control-loop behaviour posterior to ingestion, and
mixing it into delta_setup is exactly the confusion this script exists to
prevent. It is a separate measurement.

TWO SEMANTIC TRAPS THIS SCRIPT IS BUILT TO AVOID
------------------------------------------------
1. ``TidalVolumeBaseline`` in the patient block is the patient's *spontaneous*
   tidal volume, computed by Pulse from height and weight. On S1_F_0000 it is
   385.7 mL while the *ventilator* setting is 300 mL. Comparing them would
   fabricate a -22 % deviation out of two unrelated quantities. The ventilator
   setting lives in the equipment action, never in the patient block.
2. Respiration rate has TWO contracts: a patient baseline and a ventilator
   setpoint. They carry the same number in this sweep but are not the same
   object. Extraction is therefore keyed on (block, field), never on a field
   name searched globally.

A configured baseline and a tuned physiological state are likewise different
objects: the log reports ``Systolic(mmHg):100.084`` after circuit tuning for a
configured baseline of 100. That is initialisation converging, not a clamp, and
the tuned value is not read by this script.

NO VERDICT IS ISSUED HERE. This pass emits raw deltas and their distribution.
Classifying a delta as serialisation noise, deterministic transform, projection
onto a bound or genuine substitution is a later step, taken on the numbers.

Usage::

    uv run python scripts/audit_input_instantiation.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
SWEEP = REPO / "data" / "runs" / "full_sweep"
OUT_LONG = REPO / "results" / "input_instantiation_long.csv"

CELLS = ["S1_F", "S1_M", "S2_F", "S2_M", "S3_F", "S3_M", "S4_F", "S4_M"]
N_PER_CELL = 160
N_RUNS = len(CELLS) * N_PER_CELL
DBP_CLIPS_PER_CELL = 35

# (contract, block, field, expected unit, aggregated column, morris column)
# `block` is the parsed JSON object the field must be read from. Reading a field
# from the wrong block is the failure mode this table exists to prevent, so the
# block is part of the contract, not a lookup hint.
CONTRACTS: list[tuple[str, str, str, str, str, str]] = [
    ("HR_patient_baseline",   "patient", "HeartRateBaseline",                 "1/min", "in_hr",   "hr"),
    ("RR_patient_baseline",   "patient", "RespirationRateBaseline",           "1/min", "in_rr",   "rr"),
    ("SBP_patient_baseline",  "patient", "SystolicArterialPressureBaseline",  "mmHg",  "in_sbp",  "sbp"),
    ("DBP_patient_baseline",  "patient", "DiastolicArterialPressureBaseline", "mmHg",  "in_dbp",  "dbp"),
    ("Vt_ventilator",         "vent",    "TidalVolume",                       "mL",    "in_vt",   "vt"),
    ("RR_ventilator",         "vent",    "RespirationRate",                   "1/min", "in_rr",   "rr"),
    ("FiO2_ventilator",       "vent",    "FractionInspiredOxygen",            "",      "in_fio2", "fio2"),
    ("PEEP_ventilator",       "vent",    "PositiveEndExpiratoryPressure",     "cmH2O", "in_peep", "peep"),
]

PATIENT_MARKER = "[Patient]"
ACTION_MARKER = "[Action]"
VENT_PATH = ("EquipmentAction", "MechanicalVentilatorVolumeControl")

_DECODER = json.JSONDecoder()


def _fail(msg: str) -> None:
    print(f"\nBLOCKING ASSERTION FAILED: {msg}")
    sys.exit(1)


def _json_after(text: str, marker: str, start: int) -> tuple[dict | None, int]:
    """Decode the first JSON object appearing after `marker` from `start`.

    Uses the json decoder itself rather than a brace counter: braces inside
    string values would break a hand-rolled scan, and the patient block
    contains free-text names.
    """
    i = text.find(marker, start)
    if i < 0:
        return None, -1
    j = text.find("{", i)
    if j < 0:
        return None, -1
    try:
        obj, end = _DECODER.raw_decode(text, j)
    except ValueError:
        return None, i + len(marker)
    return (obj if isinstance(obj, dict) else None), end


def _extract_blocks(log_text: str) -> tuple[dict | None, dict | None, str]:
    """Return (patient_block, ventilator_action_block, status).

    `[Provided Patient]` is protobuf text, not JSON, so it cannot be decoded and
    cannot be mistaken for the instantiated `[Patient]` block. Several `[Action]`
    blocks exist per run (intubation, ventilator, ...); the ventilator one is
    identified by its structure, never by its position.
    """
    # The instantiated patient. Search for the marker not preceded by "Provided".
    patient = None
    pos = 0
    while True:
        i = log_text.find(PATIENT_MARKER, pos)
        if i < 0:
            break
        if log_text[max(0, i - 12):i].rstrip().endswith("Provided"):
            pos = i + len(PATIENT_MARKER)
            continue
        obj, end = _json_after(log_text, PATIENT_MARKER, i)
        if obj is not None:
            patient = obj
            break
        pos = i + len(PATIENT_MARKER)
        if end > pos:
            pos = end

    vent_candidates: list[dict] = []
    pos = 0
    while True:
        obj, end = _json_after(log_text, ACTION_MARKER, pos)
        if end < 0:
            break
        if obj is not None:
            node = obj
            for key in VENT_PATH:
                node = node.get(key) if isinstance(node, dict) else None
                if node is None:
                    break
            if isinstance(node, dict):
                vent_candidates.append(node)
        pos = max(end, pos + len(ACTION_MARKER))

    if len(vent_candidates) > 1:
        return patient, None, "multiple_candidates"
    vent = vent_candidates[0] if vent_candidates else None
    return patient, vent, "ok"


def _read_scalar(block: dict | None, field: str) -> tuple[float | None, str, str]:
    """Return (value, unit, scalar_type) for `field` inside `block`.

    The scalar wrapper key (ScalarPressure, ScalarFrequency, Scalar0To1, ...) is
    read from the data rather than assumed, and reported, so a change in Pulse's
    serialisation shows up as a recorded fact instead of a silent miss.
    """
    if block is None:
        return None, "", ""
    node = block.get(field)
    if not isinstance(node, dict):
        return None, "", ""
    children = [(k, v) for k, v in node.items() if isinstance(v, dict) and "Value" in v]
    if len(children) != 1:
        return None, "", f"ambiguous:{len(children)}"
    scalar_type, scalar = children[0]
    unit = scalar.get("Unit", "")
    try:
        return float(scalar["Value"]), str(unit), scalar_type
    except (TypeError, ValueError):
        return None, str(unit), scalar_type


def main() -> None:
    # ---------- blocking assertions on the corpus itself -------------------
    configs = sorted(SWEEP.glob("*/*/config.json"))
    logs = sorted(SWEEP.glob("*/*/pulse.log"))
    if len(configs) != N_RUNS:
        _fail(f"expected {N_RUNS} config.json, found {len(configs)}")
    if len(logs) != N_RUNS:
        _fail(f"expected {N_RUNS} pulse.log, found {len(logs)}")
    print(f"corpus: {len(configs)} config.json, {len(logs)} pulse.log")

    sampled = pd.read_parquet(SWEEP / "morris_sample.parquet")
    if len(sampled) != N_PER_CELL:
        _fail(f"morris_sample.parquet has {len(sampled)} rows, expected {N_PER_CELL}")

    agg = {c: pd.read_parquet(SWEEP / c / "aggregated.parquet") for c in CELLS}

    # Calibration witness 1: the pulse-pressure clip must fire on exactly 35
    # points in EVERY cell. A total of 280 alone would survive a bug that moved
    # clips between cells; a per-cell count will not.
    for c in CELLS:
        n = int(agg[c]["dbp_was_clipped"].sum())
        if n != DBP_CLIPS_PER_CELL:
            _fail(f"{c}: {n} DBP clips, expected {DBP_CLIPS_PER_CELL}")
    print(f"witness: DBP clip fires {DBP_CLIPS_PER_CELL}/cell in all 8 cells "
          f"= {DBP_CLIPS_PER_CELL * len(CELLS)}/{N_RUNS}")

    # Calibration witness 2: prove the sampled->run mapping is row order, rather
    # than assume it. Every input except DBP passes through the wrapper
    # untouched, so equality on those six is the test.
    checked = 0
    for c in CELLS:
        a = agg[c].sort_values("case_id").reset_index(drop=True)
        for _, mcol, acol in [("", "hr", "in_hr"), ("", "sbp", "in_sbp"),
                              ("", "rr", "in_rr"), ("", "vt", "in_vt"),
                              ("", "fio2", "in_fio2"), ("", "peep", "in_peep")]:
            if not (sampled[mcol].to_numpy() == a[acol].to_numpy()).all():
                _fail(f"{c}: sampled '{mcol}' does not match aggregated '{acol}' "
                      "by row order -- the case-index mapping is not what this "
                      "script assumes, and every delta_wrapper would be wrong")
            checked += len(a)
    print(f"witness: sampled<->run mapping verified on {checked} comparisons "
          "(6 unclipped inputs x 160 points x 8 cells)")

    # ---------- extraction --------------------------------------------------
    rows: list[dict] = []
    for c in CELLS:
        a = agg[c].sort_values("case_id").reset_index(drop=True)
        for i in range(N_PER_CELL):
            run = a.iloc[i]
            log_text = (SWEEP / c / str(run["case_id"]) / "pulse.log").read_text(
                encoding="utf-8", errors="replace")
            patient, vent, block_status = _extract_blocks(log_text)
            blocks = {"patient": patient, "vent": vent}

            for contract, block_name, field, want_unit, acol, mcol in CONTRACTS:
                block = blocks[block_name]
                x_sampled = float(sampled.iloc[i][mcol])
                x_wrapper = float(run[acol])
                value, unit, scalar_type = _read_scalar(block, field)

                if block is None:
                    status = ("multiple_candidates" if block_status == "multiple_candidates"
                              and block_name == "vent"
                              else f"missing_{block_name}_block")
                elif value is None:
                    status = f"field_absent:{scalar_type}" if scalar_type else "field_absent"
                elif unit != want_unit:
                    status = f"unit_mismatch:{unit!r}!={want_unit!r}"
                else:
                    status = "parsed"

                d_wrap = x_wrapper - x_sampled
                d_setup = (value - x_wrapper) if status == "parsed" else None
                rows.append({
                    "run_id": run["case_id"], "scenario": run["scenario"],
                    "reference_body": run["sex"], "contract": contract,
                    "sampled_value": x_sampled, "wrapper_applied_value": x_wrapper,
                    "pulse_instantiated_value": value,
                    "delta_wrapper_abs": d_wrap,
                    "delta_wrapper_rel": (d_wrap / x_sampled) if x_sampled else None,
                    "delta_setup_abs": d_setup,
                    "delta_setup_rel": (d_setup / x_wrapper)
                    if (d_setup is not None and x_wrapper) else None,
                    "source_block": block_name, "source_field": field,
                    "source_scalar_type": scalar_type, "source_unit": unit,
                    "parse_status": status,
                    "exit_code": run["exit_code"], "diverged": bool(run["diverged"]),
                })

    long = pd.DataFrame(rows)
    expected_rows = N_RUNS * len(CONTRACTS)
    if len(long) != expected_rows:
        _fail(f"long artefact has {len(long)} rows, expected {expected_rows}")

    OUT_LONG.parent.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_LONG, index=False)
    print(f"\nwrote {OUT_LONG.relative_to(REPO)}: {len(long)} rows "
          f"({len(CONTRACTS)} contracts x {N_RUNS} runs)\n")

    # ---------- summary, no verdict ----------------------------------------
    print("=" * 108)
    print(f"{'contract':24s} {'parsed':>6s} {'missing':>7s} | "
          f"{'d_wrap!=0':>9s} | {'d_setup!=0':>10s} {'exact==':>8s} "
          f"{'max|d_setup|':>13s} {'max|rel|':>10s}")
    print("=" * 108)
    for contract, *_ in CONTRACTS:
        sub = long[long["contract"] == contract]
        ok = sub[sub["parse_status"] == "parsed"]
        n_miss = len(sub) - len(ok)
        if len(ok) + n_miss != N_RUNS:
            _fail(f"{contract}: parsed+missing != {N_RUNS}")
        nz_w = int((sub["delta_wrapper_abs"] != 0).sum())
        ds = ok["delta_setup_abs"]
        nz_s = int((ds != 0).sum())
        mx = ds.abs().max() if len(ds) else float("nan")
        mxr = ok["delta_setup_rel"].abs().max() if len(ok) else float("nan")
        print(f"{contract:24s} {len(ok):>6d} {n_miss:>7d} | {nz_w:>9d} | "
              f"{nz_s:>10d} {len(ds) - nz_s:>8d} {mx:>13.6g} {mxr:>10.3g}")

    miss = long[long["parse_status"] != "parsed"]
    print(f"\nMISSING / non-parsed rows: {len(miss)}")
    if len(miss):
        print(miss["parse_status"].value_counts().to_string())
        print("\nby scenario x body x diverged:")
        print(miss.groupby(["scenario", "reference_body", "diverged"])
              .size().to_string())

    print("\nDistinct non-zero delta_setup values per contract "
          "(raw, unrounded, no threshold applied):")
    for contract, *_ in CONTRACTS:
        ok = long[(long["contract"] == contract) & (long["parse_status"] == "parsed")]
        vals = sorted(set(ok.loc[ok["delta_setup_abs"] != 0, "delta_setup_abs"]))
        if not vals:
            print(f"  {contract:24s} none -- instantiated == wrapper-applied on "
                  f"all {len(ok)} parsed runs")
        else:
            head = ", ".join(f"{v:.17g}" for v in vals[:6])
            print(f"  {contract:24s} {len(vals)} distinct: {head}"
                  f"{' ...' if len(vals) > 6 else ''}")

    print("\nNo verdict is issued by this script. delta_setup != 0 is a fact; "
          "whether it is\nserialisation noise, a deterministic transform, a "
          "projection onto a bound or a\ngenuine substitution is decided on the "
          "distributions above, not here.")


if __name__ == "__main__":
    main()
