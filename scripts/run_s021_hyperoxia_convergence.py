"""S021: Hyperoxia convergence test — does Pulse PaO2 plateau by 300 s?

Pre-registered protocol: ``experiments_log/santino/S021_hyperoxia_convergence.md``
(commit-before-run).

Hypothesis
----------
The atlas's F-003 finding (PaO2 > 600 mmHg at FiO2 = 1.0 in 31 / 195
FiO2 ≥ 0.95 valid-CSV runs) admits two interpretations:

(i)  **Overshoot:** Pulse's oxygenation model overshoots alveolar-gas
     equation prediction (≈ 655 mmHg in healthy adult at sea level).
(ii) **Transient regime:** Pulse hasn't converged in 120 s; with longer
     window it plateaus at a physiologically defensible value.

S021 reruns 60 selected FiO2 = 1.0 cases at a 300 s window (vs locked
120 s atlas window) and tests which interpretation the data support.

Selection
---------
22 Morris run indices with FiO2 = 1.0 and valid CSV in *every* (scenario,
sex) cell were identified. From those:

* 22 indices × S1 (M + F) = 44 runs (headline convergence test)
* 4 indices × {S3, S4} × {M, F}  = 16 runs (shunt-depression check)

Total: 60 reruns.

Pre-registered decision rule
----------------------------
On the S1 (M + F) subset, hypothesis (ii) is SUPPORTED if both:
* ``frac_converged_S1 >= 0.75`` (plateau drift < 15 mmHg / 60 s)
* ``median_plateau_S1 in [580, 680]`` mmHg

Hypothesis (i) is SUPPORTED if:
* ``median_plateau_S1 > 700`` mmHg, OR
* ``frac_converged_S1 < 0.25`` AND the converged ones plateau > 680 mmHg.

Otherwise INDETERMINATE.

The thresholds 75 % / 15 mmHg / 580–680 mmHg are committed before any S021
Pulse run is observed.

Outputs
-------
``data/runs/s021_hyperoxia_convergence/``
    selection.parquet         60 selected rows from the original parquet
    aggregated.parquet        one row per ``*_long`` rerun
    trajectories.parquet      long-form (case_id, time_s, PaO2) for all 60
    summary.json              decision + headline stats

Usage
-----
::

    uv run python scripts/run_s021_hyperoxia_convergence.py
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


# ---------- Locked design parameters (committed before any S021 run) ----------

ORIG_AGGREGATED_PATH: Path = REPO_ROOT / "data" / "runs" / "full_sweep" / "aggregated.parquet"
RUNS_ROOT: Path = REPO_ROOT / "data" / "runs" / "s021_hyperoxia_convergence"

# Extended window
SIM_DURATION_S: float = 300.0
SIM_DURATION_HOURS: float = SIM_DURATION_S / 3600.0
SAMPLE_INTERVAL_S: int = 5

# Subset design
TARGET_FIO2: float = 1.0
S1_USE_ALL_COMMON: bool = True  # all 22 common indices on S1
SHUNT_N_INDICES_PER_CELL: int = 4  # 4 common indices on S3, S4

# Pre-registered decision thresholds (committed before any S021 run)
DRIFT_THRESHOLD_MMHG_PER_60S: float = 15.0  # matches atlas DRIFT_MAX_DELTA_60S["PaO2"]
PLATEAU_WINDOW_S: tuple[float, float] = (240.0, 300.0)
TIME_SLACK_S: float = 1e-6  # atlas window rule, see src/detector.py and plateau_stats()
HYP2_FRAC_CONVERGED_MIN: float = 0.75
HYP2_PLATEAU_BAND_MMHG: tuple[float, float] = (580.0, 680.0)
HYP1_PLATEAU_OVER_MMHG: float = 700.0
HYP1_FRAC_CONVERGED_MAX: float = 0.25
HYP1_CONVERGED_PLATEAU_MIN: float = 680.0


# ---------- Selection ----------


def select_subset(orig: pd.DataFrame) -> pd.DataFrame:
    """Pick 22 common-indices S1 + 4 common-indices S3 + 4 common-indices S4.

    Reproducible: deterministic on the sorted intersection of common indices.
    """
    df = orig.copy()
    df["run_idx"] = df["case_id"].str.split("_").str[-1].astype(int)

    fio2_eq_1 = df[(df["in_fio2"] == TARGET_FIO2) & (~df["diverged"])]
    # Intersection of run_idx valid in every (scenario, sex) cell
    indices_by_cell = {}
    for (sc, sex), sub in fio2_eq_1.groupby(["scenario", "sex"]):
        indices_by_cell[(sc, sex)] = set(sub["run_idx"].tolist())
    common = sorted(set.intersection(*indices_by_cell.values()))

    if len(common) < SHUNT_N_INDICES_PER_CELL:
        raise RuntimeError(
            f"Need >= {SHUNT_N_INDICES_PER_CELL} common indices; found {len(common)}"
        )

    shunt_indices = common[:SHUNT_N_INDICES_PER_CELL]
    s1_indices = common  # all 22

    keep_rows = []
    for _, r in fio2_eq_1.iterrows():
        sc, sex, ri = r["scenario"], r["sex"], r["run_idx"]
        if sc == "S1" and ri in s1_indices:
            keep_rows.append(r)
        elif sc in {"S3", "S4"} and ri in shunt_indices:
            keep_rows.append(r)

    sel = pd.DataFrame(keep_rows).reset_index(drop=True)
    return sel


def row_to_sample_row(r: pd.Series) -> pd.Series:
    """Map aggregated-parquet row to the (hr, sbp, dbp, ...) form for build_config."""
    return pd.Series(
        {
            "hr": r["in_hr"],
            "sbp": r["in_sbp"],
            "dbp": r["dbp_requested"],
            "rr": r["in_rr"],
            "vt": r["in_vt"],
            "fio2": r["in_fio2"],
            "peep": r["in_peep"],
        }
    )


# ---------- Trajectory extraction ----------


def extract_trajectory(run_dir: Path) -> pd.DataFrame:
    """Read ``output.csv`` for one S021 run; return (time_s, PaO2)."""
    csv_path = run_dir / "output.csv"
    if not csv_path.exists():
        return pd.DataFrame(columns=["case_id", "time_s", "PaO2_mmHg"])
    df = pd.read_csv(csv_path)
    if "time_s" not in df.columns:
        return pd.DataFrame(columns=["case_id", "time_s", "PaO2_mmHg"])
    out = pd.DataFrame(
        {
            "case_id": run_dir.name,
            "time_s": df["time_s"],
            "PaO2_mmHg": df.get("ArterialOxygenPressure"),
        }
    )
    return out


def plateau_stats(trj: pd.DataFrame) -> tuple[float, float]:
    """(plateau_value_mmHg, plateau_drift_mmHg_per_60s) over [240, 300] s."""
    if trj.empty:
        return (float("nan"), float("nan"))
    lo, hi = PLATEAU_WINDOW_S
    # Window membership uses the atlas rule (src/detector.py::_steady_state_window):
    # `t >= lo - 1e-6` and `t <= hi + 1e-6`. The recorded grid drifts -- a nominal
    # t = 240 s is stored as 239.99999999996928 -- so a strict comparison silently
    # dropped the first sample and evaluated a 55-second window while every
    # document, and this function's own docstring, named 60 s. Aligned 2026-09-01;
    # the convention itself was adopted repository-wide on 2026-08-13, see
    # scripts/audit_s030_provenance.py.
    win = trj[(trj["time_s"] >= lo - TIME_SLACK_S) & (trj["time_s"] <= hi + TIME_SLACK_S)]
    if len(win) < 3:
        return (float("nan"), float("nan"))
    pao2 = win["PaO2_mmHg"].astype(float)
    plateau = float(pao2.mean())
    # OLS slope mmHg/s, then × 60
    t = win["time_s"].astype(float).to_numpy()
    y = pao2.to_numpy()
    slope, _intercept = (
        ((t - t.mean()) * (y - y.mean())).sum() / ((t - t.mean()) ** 2).sum(),
        0.0,
    )
    return (plateau, float(slope * 60.0))


# ---------- Driver ----------


def main() -> None:
    if not ORIG_AGGREGATED_PATH.exists():
        raise FileNotFoundError(
            f"missing original aggregated parquet at {ORIG_AGGREGATED_PATH}; "
            "run the full sweep first (scripts/run_full_sweep.py)."
        )

    orig = pd.read_parquet(ORIG_AGGREGATED_PATH)
    sel = select_subset(orig)

    print(f"[S021] selected {len(sel)} runs at FiO2 = {TARGET_FIO2}")
    print("[S021] cell breakdown:")
    print(sel.groupby(["scenario", "sex"]).size().to_string())

    RUNS_ROOT.mkdir(parents=True, exist_ok=True)
    sel_path = RUNS_ROOT / "selection.parquet"
    sel.to_parquet(sel_path)

    # Build configs with extended window
    jobs: list[tuple[dict, str]] = []
    for _, r in sel.iterrows():
        sample_row = row_to_sample_row(r)
        new_case_id = f"{r['case_id']}_long"
        cfg = build_config(
            sample_row=sample_row,
            scenario_key=r["scenario"],
            sex_key=r["sex"],
            case_id=new_case_id,
            clip_dbp=True,
        )
        cfg["duration_hours"] = SIM_DURATION_HOURS
        cfg["sample_interval_s"] = SAMPLE_INTERVAL_S
        jobs.append((cfg, new_case_id))

    # Dispatch
    print(f"[S021] dispatching {len(jobs)} runs at duration={SIM_DURATION_S}s ...")
    run_many(jobs, runs_root=RUNS_ROOT, progress=True)

    # Aggregate
    print("[S021] aggregating...")
    agg = aggregate_under(RUNS_ROOT)
    agg_path = RUNS_ROOT / "aggregated.parquet"
    write_parquet(agg, agg_path)

    # Extract trajectories + plateau stats
    print("[S021] extracting trajectories + plateau stats...")
    trj_frames = []
    plateau_rows = []
    for _, r in sel.iterrows():
        case_id = f"{r['case_id']}_long"
        run_dir = RUNS_ROOT / case_id
        trj = extract_trajectory(run_dir)
        trj_frames.append(trj)
        plateau_val, drift = plateau_stats(trj)
        plateau_rows.append(
            {
                "case_id_orig": r["case_id"],
                "case_id_long": case_id,
                "scenario": r["scenario"],
                "sex": r["sex"],
                "run_idx": int(r["case_id"].split("_")[-1]),
                "fio2": r["in_fio2"],
                "PaO2_mean_orig_120s": float(r.get("PaO2_mean", float("nan"))),
                "PaO2_plateau_mmHg": plateau_val,
                "PaO2_plateau_drift_mmHg_per_60s": drift,
                "converged": (abs(drift) < DRIFT_THRESHOLD_MMHG_PER_60S)
                if drift == drift
                else False,
            }
        )
    plateau = pd.DataFrame(plateau_rows)
    plateau.to_parquet(RUNS_ROOT / "plateau_stats.parquet")
    pd.concat(trj_frames, ignore_index=True).to_parquet(RUNS_ROOT / "trajectories.parquet")

    # Pre-registered decision (S1 subset)
    s1 = plateau[plateau["scenario"] == "S1"].copy()
    s1_converged = s1["converged"].mean() if len(s1) else float("nan")
    s1_plateau_median = s1["PaO2_plateau_mmHg"].median() if len(s1) else float("nan")
    s1_converged_set = s1[s1["converged"]]
    s1_converged_plateau_median = (
        s1_converged_set["PaO2_plateau_mmHg"].median() if len(s1_converged_set) else float("nan")
    )

    hyp2_supported = (
        s1_converged >= HYP2_FRAC_CONVERGED_MIN
        and HYP2_PLATEAU_BAND_MMHG[0] <= s1_plateau_median <= HYP2_PLATEAU_BAND_MMHG[1]
    )
    hyp1_supported = s1_plateau_median > HYP1_PLATEAU_OVER_MMHG or (
        s1_converged < HYP1_FRAC_CONVERGED_MAX
        and s1_converged_plateau_median > HYP1_CONVERGED_PLATEAU_MIN
    )
    if hyp2_supported and not hyp1_supported:
        decision = "HYPOTHESIS_II_TRANSIENT_REGIME_SUPPORTED"
    elif hyp1_supported and not hyp2_supported:
        decision = "HYPOTHESIS_I_OVERSHOOT_SUPPORTED"
    else:
        decision = "INDETERMINATE"

    # Auxiliary: shunt-depression check (descriptive)
    aux_rows = []
    for sc in ["S1", "S3", "S4"]:
        sub = plateau[plateau["scenario"] == sc]
        aux_rows.append(
            {
                "scenario": sc,
                "n": int(len(sub)),
                "plateau_median_mmHg": float(sub["PaO2_plateau_mmHg"].median())
                if len(sub)
                else float("nan"),
                "plateau_p25_mmHg": float(sub["PaO2_plateau_mmHg"].quantile(0.25))
                if len(sub)
                else float("nan"),
                "plateau_p75_mmHg": float(sub["PaO2_plateau_mmHg"].quantile(0.75))
                if len(sub)
                else float("nan"),
                "frac_converged": float(sub["converged"].mean()) if len(sub) else float("nan"),
            }
        )

    summary = {
        "n_runs": int(len(plateau)),
        "S1_frac_converged": float(s1_converged),
        "S1_plateau_median_mmHg": float(s1_plateau_median),
        "S1_converged_plateau_median_mmHg": float(s1_converged_plateau_median),
        "decision": decision,
        "thresholds": {
            "drift_threshold_mmHg_per_60s": DRIFT_THRESHOLD_MMHG_PER_60S,
            "hyp2_frac_converged_min": HYP2_FRAC_CONVERGED_MIN,
            "hyp2_plateau_band_mmHg": list(HYP2_PLATEAU_BAND_MMHG),
            "hyp1_plateau_over_mmHg": HYP1_PLATEAU_OVER_MMHG,
            "hyp1_frac_converged_max": HYP1_FRAC_CONVERGED_MAX,
            "hyp1_converged_plateau_min": HYP1_CONVERGED_PLATEAU_MIN,
            "plateau_window_s": list(PLATEAU_WINDOW_S),
        },
        "shunt_depression_aux": aux_rows,
    }
    (RUNS_ROOT / "summary.json").write_text(json.dumps(summary, indent=2))

    print()
    print("=" * 70)
    print(f"  S021 result: {decision}")
    print(f"  S1 frac converged = {s1_converged:.3f} (threshold >= {HYP2_FRAC_CONVERGED_MIN})")
    print(
        f"  S1 plateau median  = {s1_plateau_median:.1f} mmHg "
        f"(hyp-II band {HYP2_PLATEAU_BAND_MMHG[0]:.0f}..{HYP2_PLATEAU_BAND_MMHG[1]:.0f})"
    )
    print("  Shunt-depression aux (S1 > S3 > S4 predicted):")
    for row in aux_rows:
        print(
            f"    {row['scenario']}: median={row['plateau_median_mmHg']:.1f} mmHg "
            f"(n={row['n']}, converged={row['frac_converged']:.2f})"
        )
    print("=" * 70)


if __name__ == "__main__":
    main()
