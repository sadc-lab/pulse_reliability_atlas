"""How far did each run get before it stopped?

WHY THIS EXISTS
---------------
``scripts/audit_input_instantiation.py`` measures Pulse's post-ingestion value
for eight input contracts and finds it exactly equal to the submitted value on
every parsed run. Twenty runs carry no ventilator-action block, so the four
ventilator contracts are unmeasured there.

Those twenty are not one situation but two, and the difference decides how the
result may be stated:

  NOT_REACHED             execution stopped before the ventilator action was
                          ever submitted, so the engine had no opportunity to
                          transform those four values;
  REACHED_BUT_UNOBSERVABLE the action was submitted, but its ingested values do
                          not appear in the log.

Only the second is a population in which an unobserved substitution could hide.
Reporting the first as "missing" would invite exactly that misreading.

METHOD
------
The stage markers below are read out of a run that completed (S1_F_0000), not
invented: each is a literal the engine or the wrapper emits, in the order it
emits them. Every log is then assigned the last stage whose marker it contains.

The 1,260 completed runs are processed too, as a negative control: if the
staircase is right, they all reach the final stage. A staircase that only ever
sees the twenty failures would prove nothing about the ordering.

This script reads. It writes no manuscript, reruns nothing, and issues no
clamp / no-clamp verdict.

Usage::

    uv run python scripts/audit_divergence_timeline.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
SWEEP = REPO / "data" / "runs" / "full_sweep"
CELLS = ["S1_F", "S1_M", "S2_F", "S2_M", "S3_F", "S3_M", "S4_F", "S4_M"]
N_RUNS = 1280

# (stage index, name, literal). Order is the emission order in a completed run.
STAGES: list[tuple[int, str, str]] = [
    (1, "config_submitted",        "[Provided Patient]"),
    (2, "patient_instantiated",    "[Patient]"),
    (3, "circuit_tuning_started",  "Tuning to patient parameters"),
    (4, "circuit_tuned",           "Successfully tuned circuit with tissue resistances"),
    (5, "vent_setup_begun",        "Setting Up MechanicalVentilator"),
    (6, "vent_action_ingested",    '"MechanicalVentilatorVolumeControl"'),
    (7, "vent_connected",          "Ventilator connected (VC-AC)"),
    (8, "airway_switched",         "Airway Mode : MechanicalVentilator"),
]
FINAL_STAGE = STAGES[-1][0]

# Markers that say why it stopped, not how far it got. Kept separate: a failure
# reason is not a stage.
FAILURE_MARKERS = {
    "no_convergence": "Could not converge to provided Convergence",
    "no_stabilisation_criteria": "Pulse needs stabilization criteria",
    "wrapper_stabilise_error": "failed to stabilise for case",
}


def main() -> None:
    agg = pd.concat(
        [pd.read_parquet(SWEEP / c / "aggregated.parquet") for c in CELLS],
        ignore_index=True,
    )
    if len(agg) != N_RUNS:
        print(f"BLOCKING: expected {N_RUNS} runs, found {len(agg)}")
        sys.exit(1)

    rows = []
    for _, run in agg.iterrows():
        cell = f"{run['scenario']}_{run['sex']}"
        text = (SWEEP / cell / str(run["case_id"]) / "pulse.log").read_text(
            encoding="utf-8", errors="replace")

        present = {name: (lit in text) for _, name, lit in STAGES}
        reached = [idx for idx, name, _ in STAGES if present[name]]
        last = max(reached) if reached else 0
        # A staircase must not have holes. If a later stage is present while an
        # earlier one is absent, the ordering assumption is wrong and must be
        # reported rather than silently smoothed over.
        contiguous = reached == list(range(1, last + 1))

        rows.append({
            "case_id": run["case_id"], "scenario": run["scenario"],
            "body": run["sex"], "diverged": bool(run["diverged"]),
            "exit_code": int(run["exit_code"]),
            "last_stage": last,
            "last_stage_name": next((n for i, n, _ in STAGES if i == last), "none"),
            "contiguous": contiguous,
            **{f"has_{n}": present[n] for _, n, _ in STAGES},
            **{f"fail_{k}": (v in text) for k, v in FAILURE_MARKERS.items()},
        })

    df = pd.DataFrame(rows)

    holes = df[~df["contiguous"]]
    print(f"staircase contiguity: {len(df) - len(holes)}/{len(df)} runs contiguous")
    if len(holes):
        print("  NON-CONTIGUOUS (ordering assumption violated):")
        print(holes[["case_id", "last_stage_name"]].to_string(index=False))

    ok = df[~df["diverged"]]
    print(f"\nNEGATIVE CONTROL -- {len(ok)} non-diverged runs")
    print(f"  reaching final stage {FINAL_STAGE} ({STAGES[-1][1]}): "
          f"{int((ok['last_stage'] == FINAL_STAGE).sum())}/{len(ok)}")

    bad = df[df["diverged"]]
    print(f"\nTHE {len(bad)} DIVERGED RUNS -- last stage reached")
    print(bad["last_stage_name"].value_counts().to_string())
    print()
    print(bad[["case_id", "last_stage", "last_stage_name",
               "fail_no_convergence", "fail_wrapper_stabilise_error"]]
          .to_string(index=False))

    vent_stage = next(i for i, n, _ in STAGES if n == "vent_action_ingested")
    n_before = int((bad["last_stage"] < vent_stage).sum())
    print(f"\nRuns stopping BEFORE the ventilator action was ingested "
          f"(stage < {vent_stage}): {n_before}/{len(bad)}")
    classification = ("NOT_REACHED" if n_before == len(bad)
                      else "MIXED -- inspect individually")
    print(f"Classification of the four ventilator contracts on these runs: "
          f"{classification}")

    out = REPO / "results" / "divergence_timeline.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"\nwrote {out.relative_to(REPO)} ({len(df)} rows)")
    print(json.dumps({"stages": {n: i for i, n, _ in STAGES}}, indent=1))


if __name__ == "__main__":
    main()
