"""S014: Causal test of F-004 mechanism (patient-ventilator dyssynchrony).

Hypothesis
----------
The 264 / 1,280 (20.6 %) Vt-CV-flagged runs from S006 are not solver / PID
pathology. They are driven by Pulse's `InspirationPatientTriggerRespiratoryModel`
which defaults to ON in VC-AC when neither flow nor pressure trigger is supplied
(`SEMechanicalVentilatorVolumeControl.cpp` lines 120–128, Pulse 4.3.1). With
this default, the simulated patient's spontaneous respiratory drive triggers
extra "assist" breaths between mandatory cycles, delivering sub-target Vt and
inflating the breath-to-breath CV.

Test
----
Re-run the **top-64** original Morris points (ranked by `Vt_cv` over all 1,280
non-diverged runs) with **identical inputs** but adding an explicit
`InspirationPatientTriggerPressure = -2 cmH2O`. Setting any explicit trigger
forces the C++ branch
    s.SetInspirationPatientTriggerRespiratoryModel(eSwitch::Off)
to fire (the `if(!HasInspirationPatientTriggerFlow() && !HasInspirationPatientTriggerPressure())`
guard becomes false). The respiratory-model trigger is locked out.

Pre-registered decision rule
----------------------------
Let CV_orig[i] be the original sweep's Vt CV for the i-th selected run, and
CV_lock[i] the same input under trigger lockout.

    PASS  (mechanism causally confirmed)
        median(CV_orig - CV_lock) >= 0.04
        AND
        proportion(CV_lock < 0.05) >= 0.75
        on the 64 paired runs.

    FAIL  (mechanism rejected — F-004 is something else)
        Either condition fails. In that case S014 disproves the hypothesis;
        the F-004 manuscript section reverts to "mechanism unresolved" and the
        next experiment is required.

The 0.04 / 0.75 thresholds are committed before any S014 run is observed.

Selection rationale
-------------------
Top-64 by Vt_cv across all cells gives the strongest signal under matched-pair
analysis. Stratification by cell is sacrificed for power; cell breakdown is
reported descriptively in the analysis but not used for any test statistic.

Compute budget
--------------
64 runs × ~10 s wall time each (S006 mean) / 2 parallel workers ≈ 5 min.

Pre-flight requirement
----------------------
The atlas Docker image MUST be rebuilt **before** running this script:

    docker build -t pulse-atlas-engine engine/

The wrapper change in `engine/run_atlas_engine.py` is the only diff vs. the
S006 image; without rebuild, the trigger-pressure key in `config.json` is
silently ignored.

Outputs
-------
``data/runs/s014_trigger_lockout/``
    aggregated.parquet              one row per of the 64 reruns
    paired_comparison.parquet       case_id, Vt_cv_orig, Vt_cv_lock, delta
    summary.json                    pass/fail decision + headline stats
    per-run dirs (case_id_lock)     output.csv, output_pulse_native.csv, etc.

Usage
-----

    docker build -t pulse-atlas-engine engine/      # one-time, after wrapper edit
    uv run python scripts/run_s014_trigger_lockout.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.aggregator import aggregate_under, write_parquet  # noqa: E402
from src.runner import run_many  # noqa: E402
from src.scenario import build_config  # noqa: E402


# ---------- Locked design parameters ---------- #

N_RUNS: int = 64
TRIGGER_PRESSURE_CMH2O: float = -2.0   # clinical default; magnitude is what Pulse uses
ORIG_AGGREGATED_PATH: Path = REPO_ROOT / "data" / "runs" / "full_sweep" / "aggregated.parquet"
RUNS_ROOT: Path = REPO_ROOT / "data" / "runs" / "s014_trigger_lockout"

# Decision thresholds (committed before any S014 run)
PASS_MEDIAN_DELTA_MIN: float = 0.04
PASS_FRAC_BELOW_005_MIN: float = 0.75
CV_FLAG_THRESHOLD: float = 0.05


# ---------- Selection ---------- #


def select_top_64(orig: pd.DataFrame) -> pd.DataFrame:
    """Top-64 non-diverged runs by `Vt_cv`. Returns the slice of the
    aggregated parquet corresponding to those runs.
    """
    pool = orig[(~orig["diverged"]) & orig["Vt_cv"].notna()].copy()
    return pool.nlargest(N_RUNS, "Vt_cv").reset_index(drop=True)


def row_to_sample_row(r: pd.Series) -> pd.Series:
    """Map an aggregated-parquet row back to the (hr, sbp, dbp, ...) form
    that `build_config` expects. Use the *requested* DBP so the run is
    bit-identical to the original Morris point pre-clipping."""
    return pd.Series(
        {
            "hr":   r["in_hr"],
            "sbp":  r["in_sbp"],
            "dbp":  r["dbp_requested"],
            "rr":   r["in_rr"],
            "vt":   r["in_vt"],
            "fio2": r["in_fio2"],
            "peep": r["in_peep"],
        }
    )


# ---------- Driver ---------- #


def main() -> None:
    if not ORIG_AGGREGATED_PATH.exists():
        raise FileNotFoundError(
            f"missing original aggregated parquet at {ORIG_AGGREGATED_PATH}; "
            "run the full sweep first (scripts/run_full_sweep.py)."
        )

    orig = pd.read_parquet(ORIG_AGGREGATED_PATH)
    sel = select_top_64(orig)

    print(f"[S014] selected {len(sel)} runs by Vt_cv (range "
          f"{sel['Vt_cv'].min():.3f} .. {sel['Vt_cv'].max():.3f})")
    print("[S014] cell breakdown:")
    print(sel.groupby(["scenario", "sex"]).size().to_string())

    RUNS_ROOT.mkdir(parents=True, exist_ok=True)
    sel_path = RUNS_ROOT / "selection.parquet"
    sel.to_parquet(sel_path)

    # Build configs with trigger lockout
    jobs: list[tuple[dict, str]] = []
    for _, r in sel.iterrows():
        sample_row = row_to_sample_row(r)
        new_case_id = f"{r['case_id']}_lock"
        cfg = build_config(
            sample_row=sample_row,
            scenario_key=r["scenario"],
            sex_key=r["sex"],
            case_id=new_case_id,
            clip_dbp=True,
            trigger_pressure_cmh2o=TRIGGER_PRESSURE_CMH2O,
        )
        jobs.append((cfg, new_case_id))

    # Dispatch
    print(f"[S014] dispatching {len(jobs)} runs (trigger_pressure="
          f"{TRIGGER_PRESSURE_CMH2O} cmH2O) to Docker...")
    run_many(jobs, runs_root=RUNS_ROOT, progress=True)

    # Aggregate
    print("[S014] aggregating...")
    agg = aggregate_under(RUNS_ROOT)
    agg_path = RUNS_ROOT / "aggregated.parquet"
    write_parquet(agg, agg_path)

    # Paired comparison
    paired = sel[["case_id", "scenario", "sex", "Vt_cv"]].rename(columns={"Vt_cv": "Vt_cv_orig"})
    paired["case_id_lock"] = paired["case_id"] + "_lock"
    lock_cv = agg.set_index("case_id")["Vt_cv"].rename("Vt_cv_lock")
    paired = paired.join(lock_cv, on="case_id_lock")
    paired["delta"] = paired["Vt_cv_orig"] - paired["Vt_cv_lock"]
    paired_path = RUNS_ROOT / "paired_comparison.parquet"
    paired.to_parquet(paired_path)

    # Decision
    median_delta = float(paired["delta"].median(skipna=True))
    frac_below = float((paired["Vt_cv_lock"] < CV_FLAG_THRESHOLD).mean())
    pass_median = median_delta >= PASS_MEDIAN_DELTA_MIN
    pass_frac = frac_below >= PASS_FRAC_BELOW_005_MIN
    decision = "PASS" if (pass_median and pass_frac) else "FAIL"

    summary = {
        "n_runs": int(len(paired)),
        "median_delta_Vt_cv": median_delta,
        "frac_Vt_cv_lock_below_0.05": frac_below,
        "pass_median": bool(pass_median),
        "pass_frac": bool(pass_frac),
        "decision": decision,
        "thresholds": {
            "median_delta_min": PASS_MEDIAN_DELTA_MIN,
            "frac_below_min": PASS_FRAC_BELOW_005_MIN,
            "cv_flag_threshold": CV_FLAG_THRESHOLD,
        },
    }
    (RUNS_ROOT / "summary.json").write_text(json.dumps(summary, indent=2))

    print()
    print("=" * 60)
    print(f"  S014 result: {decision}")
    print(f"  median delta Vt_cv (orig - lock) = {median_delta:+.4f}  "
          f"(threshold >= {PASS_MEDIAN_DELTA_MIN})")
    print(f"  frac runs with Vt_cv_lock < 0.05 = {frac_below:.3f}  "
          f"(threshold >= {PASS_FRAC_BELOW_005_MIN})")
    print("=" * 60)


if __name__ == "__main__":
    main()
