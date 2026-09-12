#!/usr/bin/env python3
"""S033 -- Cycle-resolved re-derivation of the delivered-Vt CV.

Why this script exists
----------------------
Supplement section S8 (subsection "Cycle-resolved check of the 5-second
classifier statistic") answers a reviewer objection that the delivered-Vt
coefficient of variation driving the `not_steady_state` flag is computed from
5-second samples (0.2 Hz) on a signal whose breath rate is near 0.25 Hz.  The
answer was produced on 2026-09-09 with throwaway `awk` pipelines in a session
scratchpad.  Those pipelines are gone, so the numbers they produced were
published with no versioned producer, no artefact under `results/` and no
ledger anchor -- the exact class of debt this repository otherwise refuses
(see `experiments_log/santino/S033_cycle_resolved_vtcv.md`, section "Defects
found in this session's own work").

This script repays that debt.  It **re-derives** every number from
`data/runs/`; it reads no value back from the supplement.  If a published
figure is wrong, this script is what reveals it.

What "reproducible" does and does not mean here
-----------------------------------------------
This script needs the raw per-run traces, `output.csv` and
`output_pulse_native.csv`.  `.gitignore` L19-L20 excludes both: about 2 GB of
them exist, and only the aggregate `aggregated.parquet` is versioned.  So
`results/s033/` **cannot be regenerated on a clean clone** -- it can only be
regenerated on a machine that holds the sweep outputs.  That is the standing
situation for twenty scripts in this repository, not a new compromise, but it
is the reason the two guards in `scripts/audit_claims.py` deliberately read
only versioned files: `results/s033/*` and `aggregated.parquet`.  Those guards
are what a clean clone and CI can check.  Re-running *this* script is the only
thing that re-checks the cycle-resolved half, and it is not available to CI.

Method (as recorded in the S033 notebook, reimplemented here)
-------------------------------------------------------------
* Time base.  The atlas classifier reads `output.csv`, whose `time_s` runs
  0 -> 120 s and is the *final* 120 s of a 240 s Pulse simulation.  The native
  50 Hz trace `output_pulse_native.csv` carries absolute time 0.02 -> 240 s, so
  `t_native = t_relative + 120`.  The locked steady-state window [60, 120] s in
  classifier-relative time is therefore [180, 240] s natively.  The offset is
  re-verified at run time by value identity on two independent channels (see
  `verify_time_offset`), not assumed.
* Cycle segmentation.  Pulse's native `TidalVolume(mL)` channel is a step
  function -- constant within a breath -- so respiratory cycles are recovered
  as change points of the recorded value.  One cycle contributes one value.
* Statistic.  Population CV (`std(ddof=0) / |mean|`) over the per-cycle values,
  against the locked `CV_THRESHOLD = 0.05`, strict `>`, unchanged.
* Float tolerance is applied **only** to the time-window bounds, never to the
  threshold.  `output.csv` stores its last sample as 120.0000000000557; the
  locked detector admits it via a 1e-6 window tolerance, and so must any
  re-derivation.  Filtering on a bare `t <= 120` drops that sample -- a defect
  actually committed in the original session.
* Precision.  All CSV output is written at `%.12g`.  An intermediate file
  written at `%.6f` in the original session rounded CVs of 1.66e-10 and
  1.35e-07 to zero, excluded two configurations as division-by-zero, and
  shifted the median of paired ratios from 25.63 to 23.33.

Built-in calibration (a positive control before any negative)
-------------------------------------------------------------
`--strict` (the default) aborts unless the reconstruction reproduces values
established by other instruments:

  1. the reconstructed four-flag classification equals the stored flags of
     `aggregated.parquet` on all 1,280 runs;
  2. the stored `not_steady_state` total is 530;
  3. 1,260 runs carry both CSVs, and the 20 that do not are exactly the stored
     `diverged` runs;
  4. the 64 trigger-lockout pairs reproduce the three published S014 headline
     values (median default 5 s CV 0.351, median locked 0.016, 78.1 % of
     locked reruns below threshold).

A reconstruction that fails any of these is not measuring what it claims to.

Outputs
-------
  results/s033/sweep_cycle_vt_cv.csv     one row per analysed sweep run
  results/s033/sweep_confusion.json      2x2 agreement + counterfactual
  results/s033/lockout_paired_cv.csv     one row per trigger-lockout pair
  results/s033/lockout_estimands.csv     4 summaries x 2 resolutions
  results/s033/s033_summary.json         every headline number, one place
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from src.detector import (  # noqa: E402
    CV_THRESHOLD,
    check_not_steady_state,
    classify,
)

SWEEP = REPO / "data" / "runs" / "full_sweep"
LOCKOUT = REPO / "data" / "runs" / "s014_trigger_lockout"
OUT_DIR = REPO / "results" / "s033"

# Native absolute-time window equal to the locked relative window [60, 120] s.
NATIVE_OFFSET_S = 120.0
NATIVE_T_LO = 180.0
NATIVE_T_HI = 240.0
TIME_EPS = 1e-6  # tolerance on window bounds ONLY -- never on CV_THRESHOLD

NATIVE_TIME_COL = "Time(s)"
NATIVE_VT_COL = "TidalVolume(mL)"
NATIVE_HR_COL = "HeartRate(1/min)"

CELLS = [f"S{i}_{s}" for i in (1, 2, 3, 4) for s in ("M", "F")]

# Values established by other instruments, used here as positive controls.
EXPECTED_TOTAL_RUNS = 1280
EXPECTED_BOTH_FILES = 1260
EXPECTED_NSS_STORED = 530
EXPECTED_LOCKOUT_PAIRS = 64
EXPECTED_S014_MEDIAN_DEFAULT_5S = 0.351  # published to 3 dp
EXPECTED_S014_MEDIAN_LOCK_5S = 0.016  # published to 3 dp
EXPECTED_S014_PCT_BELOW = 78.1  # published to 1 dp

# The "substantial" cycle-only crossings are those whose CV ratio reaches this
# factor.  The cut is descriptive and is reported with the raw factors beside
# it, so no conclusion rests on the threshold itself.
SUBSTANTIAL_FACTOR = 3.0

# Relative disagreement between the recovered cycle count and the engine's own
# reported respiration rate above which a run is examined individually.  Purely
# a reporting cut: the raw distribution is written out beside it.
RR_DISAGREEMENT_CUT = 0.20


def fmt(x: float) -> str:
    """Render a float at 12 significant digits (see module docstring)."""
    return "%.12g" % x


def read_native_window(path: Path) -> pd.DataFrame:
    """Return the native rows inside [180, 240] s, Time and TidalVolume only."""
    df = pd.read_csv(path, usecols=[NATIVE_TIME_COL, NATIVE_VT_COL])
    t = df[NATIVE_TIME_COL].to_numpy(dtype=float)
    mask = (t >= NATIVE_T_LO - TIME_EPS) & (t <= NATIVE_T_HI + TIME_EPS)
    return df.loc[mask].reset_index(drop=True)


def cycle_values(vt: np.ndarray) -> np.ndarray:
    """Collapse a step-function trace to one value per breath (change points)."""
    if vt.size == 0:
        return vt
    keep = np.ones(vt.size, dtype=bool)
    keep[1:] = vt[1:] != vt[:-1]
    return vt[keep]


def _cv(vals: np.ndarray) -> float:
    """Population CV of a sample, 0 when the mean is exactly zero."""
    mean = float(vals.mean())
    std = float(vals.std(ddof=0))
    return std / abs(mean) if mean != 0 else 0.0


def cycle_cv(path: Path) -> tuple[float, int, int, float]:
    """Cycle-resolved Vt CV, cycle count, native sample count, all-sample CV.

    Two estimators are returned from the same window:

    * `cv_cycle` -- one value per *distinct consecutive* recorded volume.  This
      is the estimator the supplement publishes.  Its known weakness is that
      two consecutive breaths delivering a numerically identical volume are
      merged into one value, so a repeated volume is counted once rather than
      twice.  It is tempting to conclude that this inflates the CV, since it
      under-weights stability.  Measured, it does not: see
      `merging_bias_direction` in the confusion artefact, where the
      change-point value is higher on 641 runs and lower on 617, at a median
      ratio of 1.0004.  What merging moves is which runs cross the threshold,
      not the magnitude of the statistic.
    * `cv_native_all` -- every native 50 Hz sample in the window, which weights
      each recorded volume by the time it persists.  At a fixed breath length
      that is per-breath weighting, so it is the natural robustness check on
      the merging weakness above.  Reported as a sensitivity analysis only; the
      published estimator is unchanged.
    """
    win = read_native_window(path)
    vt = win[NATIVE_VT_COL].to_numpy(dtype=float)
    vals = cycle_values(vt)
    if vals.size == 0:
        return float("nan"), 0, 0, float("nan")
    return _cv(vals), int(vals.size), int(vt.size), _cv(vt)


# Two cycle-level CVs count as distinguishable only if they differ by more than
# MATERIAL_ABS_DIFF + MATERIAL_REL_DIFF x scale, the `isclose` form.
#
# ⚠️ The absolute term is not decoration, and a relative-only test does not
# work here -- that was the first version of this filter and it removed nothing.
# On a constant-volume run the change-point estimator returns exactly 0 while
# the all-sample estimator returns a ~1.8e-16 two-pass residue, so their
# RELATIVE difference is 100 %: a relative criterion sees a decisive difference
# where there is only machine noise. The absolute floor is set four orders of
# magnitude above that residue and ten below the 0.05 decision threshold, so it
# separates noise from signal without touching any verdict.
MATERIAL_ABS_DIFF = 1e-12
MATERIAL_REL_DIFF = 1e-6


def _bias_direction(df: pd.DataFrame) -> dict:
    """Sign test between the two cycle-level estimators, raw and de-noised.

    Returns both, because the raw count is the one a reader would compute and
    the material count is the one that means anything. See the call site for
    why they differ.
    """
    a = df["cv_cycle"].to_numpy(dtype=float)
    b = df["cv_native_all"].to_numpy(dtype=float)
    scale = np.maximum(np.abs(a), np.abs(b))
    material = np.abs(a - b) > (MATERIAL_ABS_DIFF + MATERIAL_REL_DIFF * scale)
    ratio = np.where(b > 0, a / np.where(b > 0, b, 1.0), np.nan)

    def split(mask: np.ndarray) -> dict:
        above = int((mask & (a > b)).sum())
        below = int((mask & (a < b)).sum())
        n = int(mask.sum())
        return {
            "n_runs": n,
            "n_cycle_above_native": above,
            "n_cycle_below_native": below,
            "n_tied": n - above - below,
            "pct_cycle_above_native": (100.0 * above / n) if n else float("nan"),
        }

    all_mask = np.ones(len(df), dtype=bool)
    out = {
        "material_abs_diff_cut": MATERIAL_ABS_DIFF,
        "material_rel_diff_cut": MATERIAL_REL_DIFF,
        # Calibration of the filter itself: it must exclude every
        # constant-volume run, where the only difference is the float residue.
        "n_constant_runs_excluded_by_cut": int(
            (~material & df["constant_volume"].to_numpy(dtype=bool)).sum()
        ),
        "n_constant_runs": int(df["constant_volume"].sum()),
        "raw": split(all_mask),
        "material": split(material),
        "n_below_cut": int((~material).sum()),
        "median_ratio_cycle_over_native_material": float(
            np.nanmedian(ratio[material])
        ),
        "max_float_residue_on_constant_runs": float(
            df.loc[df["constant_volume"], "cv_native_all"].max()
        ),
    }
    return out


def verify_time_offset(run_dir: Path) -> None:
    """Assert t_native = t_relative + 120 by value identity on two channels.

    The relative CSV is written at lower precision than the native trace, so
    identity is checked to the native file's own resolution (six decimals), on
    HeartRate and TidalVolume independently.
    """
    rel = pd.read_csv(run_dir / "output.csv")
    nat = pd.read_csv(
        run_dir / "output_pulse_native.csv",
        usecols=[NATIVE_TIME_COL, NATIVE_VT_COL, NATIVE_HR_COL],
    )
    nat_t = nat[NATIVE_TIME_COL].to_numpy(dtype=float)
    rel_t_all = rel["time_s"].to_numpy(dtype=float)
    for rel_t in (0.0, 60.0, 120.0):
        j = int(np.argmin(np.abs(nat_t - (rel_t + NATIVE_OFFSET_S))))
        i = int(np.argmin(np.abs(rel_t_all - rel_t)))
        for rel_col, nat_col in (
            ("HeartRate", NATIVE_HR_COL),
            ("TidalVolume", NATIVE_VT_COL),
        ):
            a = float(rel[rel_col].iloc[i])
            b = float(nat[nat_col].iloc[j])
            if abs(a - b) > 1e-6 * max(1.0, abs(b)):
                raise SystemExit(
                    f"time-offset check FAILED in {run_dir.name} at t_rel={rel_t} "
                    f"on {rel_col}: relative={a!r} native={b!r}"
                )


def counterfactual_nss(result, cv_cycle: float) -> bool:
    """Re-evaluate `not_steady_state` with the Vt CV replaced by `cv_cycle`.

    Only the Vt channel's CV changes; every other channel, criterion and
    threshold is the locked one.  The per-channel precedence inside
    `check_not_steady_state` (flatline -> CV -> drift) is preserved because the
    locked function itself is called.
    """
    stats = dict(result.stats)
    if "Vt" not in stats or not np.isfinite(cv_cycle):
        return bool(result.not_steady_state.fired)
    stats["Vt"] = replace(stats["Vt"], cv=cv_cycle)
    return bool(check_not_steady_state(stats).fired)


def nss_without_vt_cv(result) -> bool:
    """True iff `not_steady_state` still fires with the Vt CV criterion removed.

    Implemented by setting the Vt CV to 0, which cannot trip the variance test
    and leaves the flatline and drift tests intact.  This is what "already
    flagged by another channel or criterion" means.
    """
    return counterfactual_nss(result, 0.0)


def classify_run(run_dir: Path) -> dict | None:
    """Recompute the locked flags and the cycle-resolved CV for one run."""
    out_csv = run_dir / "output.csv"
    native = run_dir / "output_pulse_native.csv"
    if not out_csv.exists() or not native.exists():
        return None
    log_path = run_dir / "pulse.log"
    log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    meta_path = run_dir / "run_meta.json"
    exit_code = 0
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        exit_code = int(meta.get("exit_code", 0))
    res = classify(out_csv, pulse_log=log, exit_code=exit_code)
    if "Vt" not in res.stats:
        return None
    cv5 = float(res.stats["Vt"].cv)
    cvc, n_cycles, n_native, cv_native_all = cycle_cv(native)
    # Mean respiration rate over the same window, so the cycle count can be
    # checked against the engine's own reported breath rate by any reader: the
    # window is 60 s long, so n_cycles and rr_mean_5s are directly comparable.
    rel = pd.read_csv(out_csv, usecols=["time_s", "RespirationRate"])
    rel_t = rel["time_s"].to_numpy(dtype=float)
    rr_win = rel.loc[(rel_t >= 60.0 - TIME_EPS) & (rel_t <= 120.0 + TIME_EPS), "RespirationRate"]
    return {
        "case_id": run_dir.name,
        "cv_5s": cv5,
        "n_points_5s": int(res.stats["Vt"].n_points),
        "cv_cycle": cvc,
        "cv_native_all": cv_native_all,
        "n_cycles": n_cycles,
        "rr_mean_5s": float(rr_win.mean()),
        "n_native_samples": n_native,
        "constant_volume": bool(n_cycles == 1),
        "flag_5s": bool(cv5 > CV_THRESHOLD),
        "flag_cycle": bool(cvc > CV_THRESHOLD),
        "flag_native_all": bool(cv_native_all > CV_THRESHOLD),
        "clamped": bool(res.clamped.fired),
        "diverged": bool(res.diverged.fired),
        "implausible": bool(res.implausible.fired),
        "nss_locked": bool(res.not_steady_state.fired),
        "nss_counterfactual": counterfactual_nss(res, cvc),
        "nss_counterfactual_native": counterfactual_nss(res, cv_native_all),
        "nss_without_vt_cv": nss_without_vt_cv(res),
    }


# --------------------------------------------------------------------------- #
# Sweep
# --------------------------------------------------------------------------- #


def analyse_sweep(strict: bool) -> tuple[pd.DataFrame, dict]:
    stored = pd.read_parquet(SWEEP / "aggregated.parquet")
    if len(stored) != EXPECTED_TOTAL_RUNS:
        raise SystemExit(f"expected {EXPECTED_TOTAL_RUNS} stored runs, got {len(stored)}")
    stored = stored.set_index("case_id")

    rows: list[dict] = []
    skipped: list[str] = []
    offset_checked = 0
    for cell in CELLS:
        cell_dir = SWEEP / cell
        if not cell_dir.is_dir():
            raise SystemExit(f"missing sweep cell directory: {cell_dir}")
        cell_offset_done = False
        for run_dir in sorted(p for p in cell_dir.iterdir() if p.is_dir()):
            # Re-verify the native/relative offset once per cell, on the first
            # run of the cell that carries both files.
            if not cell_offset_done and (run_dir / "output_pulse_native.csv").exists():
                verify_time_offset(run_dir)
                cell_offset_done = True
                offset_checked += 1
            row = classify_run(run_dir)
            if row is None:
                skipped.append(run_dir.name)
                continue
            row["cell"] = cell
            row["scenario"] = cell.split("_")[0]
            row["sex"] = cell.split("_")[1]
            rows.append(row)

    df = pd.DataFrame(rows)
    stored_diverged = sorted(stored.index[stored["diverged"]].tolist())

    # ---- positive controls ------------------------------------------------ #
    problems: list[str] = []
    if len(df) != EXPECTED_BOTH_FILES:
        problems.append(f"{len(df)} runs carry both CSVs, expected {EXPECTED_BOTH_FILES}")
    if sorted(skipped) != stored_diverged:
        problems.append(
            "runs without CSVs are not exactly the stored diverged runs "
            f"({len(skipped)} skipped vs {len(stored_diverged)} diverged)"
        )
    n_nss_stored = int(stored["not_steady_state"].sum())
    if n_nss_stored != EXPECTED_NSS_STORED:
        problems.append(f"stored not_steady_state total is {n_nss_stored}, expected {EXPECTED_NSS_STORED}")

    # Flag-by-flag identity of the reconstruction against the stored flags.
    joined = df.set_index("case_id").join(
        stored[["clamped", "diverged", "implausible", "not_steady_state"]],
        rsuffix="_stored",
    )
    mismatches: dict[str, int] = {}
    for mine, theirs in (
        ("clamped", "clamped_stored"),
        ("implausible", "implausible_stored"),
        ("nss_locked", "not_steady_state"),
    ):
        n_bad = int((joined[mine].astype(bool) != joined[theirs].astype(bool)).sum())
        mismatches[mine] = n_bad
        if n_bad:
            problems.append(f"reconstruction disagrees with stored flags on {n_bad} runs ({mine})")

    # Cross-instrument control on the 5-second half of the comparison.  This
    # script reads `output.csv` through `src.detector`; `aggregated.parquet`
    # was written by the original sweep aggregation.  Two independent code
    # paths must land on the same Vt CV, to double precision.
    stored_cv = pd.to_numeric(
        pd.read_parquet(SWEEP / "aggregated.parquet").set_index("case_id")["Vt_cv"]
    )
    cv_delta = (joined["cv_5s"] - stored_cv.reindex(joined.index)).abs()
    max_cv_delta = float(cv_delta.max())
    mismatches["cv_5s_vs_stored_Vt_cv"] = int((cv_delta > 1e-12).sum())
    if max_cv_delta > 1e-12:
        problems.append(
            f"recomputed 5-second Vt CV differs from stored Vt_cv on "
            f"{mismatches['cv_5s_vs_stored_Vt_cv']} runs (max |delta| = {max_cv_delta:.3g})"
        )

    if problems and strict:
        for p in problems:
            print(f"CALIBRATION FAILED: {p}", file=sys.stderr)
        raise SystemExit(1)

    # ---- 2x2 agreement ---------------------------------------------------- #
    both = int((df["flag_5s"] & df["flag_cycle"]).sum())
    neither = int((~df["flag_5s"] & ~df["flag_cycle"]).sum())
    cycle_only = df[~df["flag_5s"] & df["flag_cycle"]]
    fivesec_only = df[df["flag_5s"] & ~df["flag_cycle"]]
    n_agree = both + neither
    pct_agree = 100.0 * n_agree / len(df)

    factors = (cycle_only["cv_cycle"] / cycle_only["cv_5s"]).sort_values()
    n_substantial = int((factors >= SUBSTANTIAL_FACTOR).sum())

    # Method validation, on every run rather than on three hand-picked ones:
    # the window is 60 s long, so the recovered cycle count must track the
    # engine's own reported respiration rate.  Runs of numerically constant
    # volume are excluded -- change-point segmentation recovers one plateau
    # there by construction, which is a stated limit, not a disagreement.
    non_const = df[~df["constant_volume"]]
    rr_rel_err = ((non_const["n_cycles"] - non_const["rr_mean_5s"]).abs()
                  / non_const["rr_mean_5s"])
    native_hz = (non_const["n_native_samples"] - 1) / (NATIVE_T_HI - NATIVE_T_LO)

    # Where the recovered cycle count and the reported respiration rate
    # disagree materially, the question that matters is not the count but
    # whether any steady-state verdict rests on it.  Segmentation under-counts
    # precisely where consecutive breaths deliver a numerically identical
    # volume -- runs whose CV is then ~1e-9 at both resolutions, far from the
    # 0.05 threshold.  This block measures that rather than asserting it.
    disagree = non_const[rr_rel_err > RR_DISAGREEMENT_CUT]
    disagree_verdict_split = disagree[disagree["flag_5s"] != disagree["flag_cycle"]]
    disagree_near_threshold = disagree[
        (disagree[["cv_5s", "cv_cycle"]].max(axis=1) > CV_THRESHOLD / 10.0)
        & (disagree[["cv_5s", "cv_cycle"]].min(axis=1) < CV_THRESHOLD * 10.0)
    ]

    nss_locked = int(df["nss_locked"].sum())
    nss_counter = int(df["nss_counterfactual"].sum())
    cycle_only_already = int(cycle_only["nss_without_vt_cv"].sum())
    fivesec_only_lose = int((~fivesec_only["nss_without_vt_cv"]).sum())

    confusion = {
        "n_runs_analysed": int(len(df)),
        "n_runs_total": EXPECTED_TOTAL_RUNS,
        "n_runs_without_csv": len(skipped),
        "runs_without_csv": sorted(skipped),
        "flagged_by_both": both,
        "flagged_by_neither": neither,
        "cycle_only": int(len(cycle_only)),
        "five_second_only": int(len(fivesec_only)),
        "n_agree": n_agree,
        "pct_agree": pct_agree,
        "cycle_only_factors": [float(x) for x in factors],
        "cycle_only_below_substantial": int(len(cycle_only)) - n_substantial,
        "cycle_only_substantial": n_substantial,
        "substantial_factor_cut": SUBSTANTIAL_FACTOR,
        "cycle_only_substantial_sex": (
            cycle_only.loc[factors.index[factors >= SUBSTANTIAL_FACTOR], "sex"]
            .value_counts()
            .to_dict()
        ),
        "cycle_only_sex": cycle_only["sex"].value_counts().to_dict(),
        "five_second_only_sex": fivesec_only["sex"].value_counts().to_dict(),
        "n_analysed_by_sex": df["sex"].value_counts().to_dict(),
        "n_constant_volume": int(df["constant_volume"].sum()),
        "cycle_count_vs_rr_median_rel_err": float(rr_rel_err.median()),
        "cycle_count_vs_rr_p95_rel_err": float(rr_rel_err.quantile(0.95)),
        "cycle_count_vs_rr_max_rel_err": float(rr_rel_err.max()),
        "cycle_count_vs_rr_n_runs": int(len(non_const)),
        "rr_disagreement_cut": RR_DISAGREEMENT_CUT,
        "n_cycle_count_disagreement": int(len(disagree)),
        "n_cycle_count_disagreement_with_verdict_split": int(len(disagree_verdict_split)),
        "cycle_count_disagreement_verdict_split_runs": sorted(
            disagree_verdict_split["case_id"].tolist()
        ),
        "n_cycle_count_disagreement_near_threshold": int(len(disagree_near_threshold)),
        "cycle_count_disagreement_near_threshold_runs": sorted(
            disagree_near_threshold["case_id"].tolist()
        ),
        "max_cv_cycle_among_cycle_count_disagreement": (
            float(disagree["cv_cycle"].max()) if len(disagree) else 0.0
        ),
        # Sensitivity analysis (NOT published): the same window scored on every
        # native 50 Hz sample, i.e. each recorded volume weighted by how long it
        # persists.  This is the estimator that the merging weakness of
        # change-point segmentation does not affect.  If the published 15 / 6
        # split were an artefact of merging, this estimator would show a
        # markedly smaller cycle-only count.
        # Direction of the merging bias, measured rather than argued. Merging
        # drops duplicates of a repeated volume, which usually leaves a sample
        # more spread relative to its mean -- but not necessarily, if the
        # repeated value is itself an outlier. So the published sentence
        # ("the bias is towards overstating variability") needs this number,
        # not the reasoning alone.
        #
        # ⚠️ The raw sign test over all 1,260 runs is contaminated. `np.std`
        # over 3,001 *identical* doubles does not return exactly 0 but a
        # ~1.8e-16 two-pass residue, whereas the change-point estimator sees a
        # single value and returns a true 0. So seven of the nine
        # constant-volume runs register as "cycle below all-sample" on pure
        # machine noise. The same objection applies, less visibly, to any run
        # whose two CVs agree to more digits than the trace carries. The
        # `material` block is therefore the one to quote: it keeps only pairs
        # that differ by more than a relative 1e-6, a million times above the
        # noise floor and still far below anything the 0.05 threshold can see.
        "merging_bias_direction": _bias_direction(df),
        "sensitivity_native_all": {
            "flagged_by_both": int((df["flag_5s"] & df["flag_native_all"]).sum()),
            "flagged_by_neither": int((~df["flag_5s"] & ~df["flag_native_all"]).sum()),
            "native_only": int((~df["flag_5s"] & df["flag_native_all"]).sum()),
            "five_second_only": int((df["flag_5s"] & ~df["flag_native_all"]).sum()),
            "pct_agree": 100.0
            * float((df["flag_5s"] == df["flag_native_all"]).mean()),
            "n_disagree_with_cycle_estimator": int(
                (df["flag_cycle"] != df["flag_native_all"]).sum()
            ),
            # The same counterfactual as the published one, but driven by the
            # all-sample estimator. Claiming the published counterfactual is
            # "conservative" requires this number, not an argument about which
            # way the segmentation rule leans.
            "nss_counterfactual": int(df["nss_counterfactual_native"].sum()),
            "nss_delta": int(df["nss_counterfactual_native"].sum() - df["nss_locked"].sum()),
            "runs_where_cycle_and_native_disagree": sorted(
                df.loc[df["flag_cycle"] != df["flag_native_all"], "case_id"].tolist()
            ),
        },
        "native_sampling_hz_min": float(native_hz.min()),
        "native_sampling_hz_max": float(native_hz.max()),
        "nss_locked": nss_locked,
        "nss_counterfactual": nss_counter,
        "nss_delta": nss_counter - nss_locked,
        "nss_delta_pct": 100.0 * (nss_counter - nss_locked) / nss_locked,
        "cycle_only_already_flagged_otherwise": cycle_only_already,
        "five_second_only_would_lose_flag": fivesec_only_lose,
        "stored_nss_total": n_nss_stored,
        "reconstruction_mismatches_vs_stored": mismatches,
        "max_abs_cv_5s_delta_vs_stored": max_cv_delta,
        # 1,260 runs matched flag-by-flag against the stored classification,
        # plus the 20 runs with no CSV shown to be exactly the stored diverged
        # set: 1,280 runs accounted for.
        "n_flag_identity_verified": int(len(joined)) + len(skipped),
        "calibration_problems": problems,
        "n_cells_offset_verified": offset_checked,
    }
    return df, confusion


# --------------------------------------------------------------------------- #
# Trigger-lockout pairs
# --------------------------------------------------------------------------- #


def five_second_vt_cv(run_dir: Path) -> tuple[float, int]:
    """Locked 5-second Vt CV for one run, via the locked detector."""
    res = classify(run_dir / "output.csv")
    s = res.stats["Vt"]
    return float(s.cv), int(s.n_points)


def analyse_lockout(strict: bool) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    lock_dirs = sorted(p for p in LOCKOUT.iterdir() if p.is_dir() and p.name.endswith("_lock"))
    if len(lock_dirs) != EXPECTED_LOCKOUT_PAIRS:
        raise SystemExit(f"expected {EXPECTED_LOCKOUT_PAIRS} lockout dirs, got {len(lock_dirs)}")

    rows: list[dict] = []
    for lock_dir in lock_dirs:
        config_id = lock_dir.name[: -len("_lock")]
        cell = "_".join(config_id.split("_")[:2])
        default_dir = SWEEP / cell / config_id
        if not default_dir.is_dir():
            raise SystemExit(f"no default-arm run for {config_id}: {default_dir}")
        cv5_def, n5_def = five_second_vt_cv(default_dir)
        cv5_lock, n5_lock = five_second_vt_cv(lock_dir)
        cvc_def, nc_def, _, cvn_def = cycle_cv(default_dir / "output_pulse_native.csv")
        cvc_lock, nc_lock, _, cvn_lock = cycle_cv(lock_dir / "output_pulse_native.csv")
        rows.append(
            {
                "config_id": config_id,
                "cell": cell,
                "scenario": cell.split("_")[0],
                "sex": cell.split("_")[1],
                "cv_5s_default": cv5_def,
                "cv_5s_lock": cv5_lock,
                "cv_cycle_default": cvc_def,
                "cv_cycle_lock": cvc_lock,
                "n_points_5s_default": n5_def,
                "n_points_5s_lock": n5_lock,
                "n_cycles_default": nc_def,
                "n_cycles_lock": nc_lock,
                "lock_below_threshold_5s": bool(cv5_lock <= CV_THRESHOLD),
                "decrease_5s": bool(cv5_lock < cv5_def),
                "decrease_cycle": bool(cvc_lock < cvc_def),
                "lock_cycle_cv_is_zero": bool(cvc_lock == 0.0),
            }
        )
    pairs = pd.DataFrame(rows)

    # ---- positive controls against the published S014 headline values ----- #
    med_def_5s = float(pairs["cv_5s_default"].median())
    med_lock_5s = float(pairs["cv_5s_lock"].median())
    pct_below = 100.0 * float(pairs["lock_below_threshold_5s"].mean())
    problems: list[str] = []
    if abs(round(med_def_5s, 3) - EXPECTED_S014_MEDIAN_DEFAULT_5S) > 1e-9:
        problems.append(f"median default 5 s CV {med_def_5s!r} != published {EXPECTED_S014_MEDIAN_DEFAULT_5S}")
    if abs(round(med_lock_5s, 3) - EXPECTED_S014_MEDIAN_LOCK_5S) > 1e-9:
        problems.append(f"median locked 5 s CV {med_lock_5s!r} != published {EXPECTED_S014_MEDIAN_LOCK_5S}")
    if abs(round(pct_below, 1) - EXPECTED_S014_PCT_BELOW) > 1e-9:
        problems.append(f"{pct_below!r} % of locked reruns below threshold != published {EXPECTED_S014_PCT_BELOW}")
    if problems and strict:
        for p in problems:
            print(f"CALIBRATION FAILED: {p}", file=sys.stderr)
        raise SystemExit(1)

    # ---- the four estimands ----------------------------------------------- #
    # Ratios need a non-zero denominator at BOTH resolutions; the ratio and
    # difference summaries are computed on the same subset so the four rows are
    # comparable, as the supplement table states.
    ratio_ok = pairs[(pairs["cv_cycle_lock"] > 0) & (pairs["cv_5s_lock"] > 0)].copy()
    excluded = sorted(set(pairs["config_id"]) - set(ratio_ok["config_id"]))

    est_rows: list[dict] = []

    def summaries(sub: pd.DataFrame, res: str) -> dict[str, float]:
        d = sub[f"cv_{res}_default"].to_numpy(dtype=float)
        lo = sub[f"cv_{res}_lock"].to_numpy(dtype=float)
        return {
            "ratio_of_group_medians": float(np.median(d) / np.median(lo)),
            "median_of_paired_ratios": float(np.median(d / lo)),
            "difference_of_group_medians": float(np.median(d) - np.median(lo)),
            "median_of_paired_differences": float(np.median(d - lo)),
        }

    s_5s = summaries(ratio_ok, "5s")
    s_cyc = summaries(ratio_ok, "cycle")
    for key in (
        "ratio_of_group_medians",
        "median_of_paired_ratios",
        "difference_of_group_medians",
        "median_of_paired_differences",
    ):
        a, b = s_5s[key], s_cyc[key]
        gap = (max(a, b) / min(a, b) - 1.0) * 100.0 if min(a, b) != 0 else float("nan")
        est_rows.append(
            {
                "summary": key,
                "five_second": a,
                "cycle_resolved": b,
                "relative_gap_pct": gap,
                "cycle_overstates": bool(b > a),
                "n_configs": int(len(ratio_ok)),
            }
        )
    estimands = pd.DataFrame(est_rows)

    info = {
        "n_pairs": int(len(pairs)),
        "n_pairs_in_estimands": int(len(ratio_ok)),
        "excluded_from_estimands": excluded,
        "excluded_lock_cycle_cv": {
            c: fmt(float(pairs.loc[pairs["config_id"] == c, "cv_cycle_lock"].iloc[0]))
            for c in excluded
        },
        "excluded_lock_vt_value_mL": {},
        "n_decrease_5s": int(pairs["decrease_5s"].sum()),
        "n_decrease_cycle": int(pairs["decrease_cycle"].sum()),
        "median_default_5s": med_def_5s,
        "median_lock_5s": med_lock_5s,
        "pct_lock_below_threshold_5s": pct_below,
        "median_default_cycle": float(pairs["cv_cycle_default"].median()),
        "median_lock_cycle": float(pairs["cv_cycle_lock"].median()),
        "relative_gap_min_pct": float(estimands["relative_gap_pct"].min()),
        "relative_gap_max_pct": float(estimands["relative_gap_pct"].max()),
        "n_cycle_overstates": int(estimands["cycle_overstates"].sum()),
        "calibration_problems": problems,
    }

    # The delivered volume of every excluded configuration, at the precision of
    # the recorded trace -- the supplement quotes it, so it must be re-derived.
    for c in excluded:
        lock_dir = LOCKOUT / f"{c}_lock"
        win = read_native_window(lock_dir / "output_pulse_native.csv")
        vals = cycle_values(win[NATIVE_VT_COL].to_numpy(dtype=float))
        uniq = sorted({fmt(v) for v in vals})
        info["excluded_lock_vt_value_mL"][c] = uniq if len(uniq) > 1 else uniq[0]

    return pairs, estimands, info


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #


def write_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False, float_format="%.12g")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument(
        "--no-strict",
        dest="strict",
        action="store_false",
        help="report calibration failures without aborting (diagnosis only)",
    )
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("S033 -- re-deriving the cycle-resolved Vt CV from data/runs/ ...")
    sweep_df, confusion = analyse_sweep(args.strict)
    cols = [
        "case_id",
        "cell",
        "scenario",
        "sex",
        "cv_5s",
        "n_points_5s",
        "cv_cycle",
        "cv_native_all",
        "n_cycles",
        "rr_mean_5s",
        "n_native_samples",
        "constant_volume",
        "flag_5s",
        "flag_cycle",
        "flag_native_all",
        "clamped",
        "diverged",
        "implausible",
        "nss_locked",
        "nss_counterfactual",
        "nss_counterfactual_native",
        "nss_without_vt_cv",
    ]
    write_csv(sweep_df[cols].sort_values("case_id"), OUT_DIR / "sweep_cycle_vt_cv.csv")
    (OUT_DIR / "sweep_confusion.json").write_text(
        json.dumps(confusion, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    pairs, estimands, lock_info = analyse_lockout(args.strict)
    write_csv(pairs.sort_values("config_id"), OUT_DIR / "lockout_paired_cv.csv")
    write_csv(estimands, OUT_DIR / "lockout_estimands.csv")

    summary = {
        "script": "scripts/s033_cycle_resolved_vtcv.py",
        "notebook": "experiments_log/santino/S033_cycle_resolved_vtcv.md",
        "cv_threshold": CV_THRESHOLD,
        "native_window_s": [NATIVE_T_LO, NATIVE_T_HI],
        "native_offset_s": NATIVE_OFFSET_S,
        "sweep": confusion,
        "lockout": lock_info,
        "estimands": estimands.to_dict(orient="records"),
    }
    (OUT_DIR / "s033_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    # ---- human-readable report ------------------------------------------- #
    c = confusion
    print(f"\nSweep: {c['n_runs_analysed']} runs carry both CSVs "
          f"({c['n_runs_without_csv']} do not; all stored-diverged: "
          f"{c['reconstruction_mismatches_vs_stored']})")
    print(f"  flagged by both      {c['flagged_by_both']}")
    print(f"  flagged by neither   {c['flagged_by_neither']}")
    print(f"  cycle-only           {c['cycle_only']}")
    print(f"  5-second-only        {c['five_second_only']}")
    print(f"  agreement            {c['n_agree']}/{c['n_runs_analysed']} = {c['pct_agree']:.4f} %")
    print(f"  cycle-only factors   {[round(x, 2) for x in c['cycle_only_factors']]}")
    print(f"  below/at-or-above {SUBSTANTIAL_FACTOR}x  "
          f"{c['cycle_only_below_substantial']} / {c['cycle_only_substantial']}")
    print(f"  cycle-only by sex    {c['cycle_only_sex']}   "
          f"5s-only by sex {c['five_second_only_sex']}")
    print(f"  analysed by sex      {c['n_analysed_by_sex']}")
    print(f"  constant-volume runs {c['n_constant_volume']}")
    print(f"  native sampling      {c['native_sampling_hz_min']:.4f}-"
          f"{c['native_sampling_hz_max']:.4f} Hz")
    print(f"  cycle count vs RR    median {100 * c['cycle_count_vs_rr_median_rel_err']:.2f} %, "
          f"p95 {100 * c['cycle_count_vs_rr_p95_rel_err']:.2f} %, "
          f"max {100 * c['cycle_count_vs_rr_max_rel_err']:.2f} % "
          f"(n = {c['cycle_count_vs_rr_n_runs']})")
    print(f"    > {100 * c['rr_disagreement_cut']:.0f} % disagreement: "
          f"{c['n_cycle_count_disagreement']} runs, of which "
          f"{c['n_cycle_count_disagreement_with_verdict_split']} split the two verdicts "
          f"{c['cycle_count_disagreement_verdict_split_runs']}; "
          f"{c['n_cycle_count_disagreement_near_threshold']} sit within a decade of the "
          f"threshold {c['cycle_count_disagreement_near_threshold_runs']}")
    print(f"  NSS locked {c['nss_locked']} -> counterfactual {c['nss_counterfactual']} "
          f"({c['nss_delta']:+d}, {c['nss_delta_pct']:+.4f} %)")
    print(f"    cycle-only already flagged otherwise: {c['cycle_only_already_flagged_otherwise']}")
    print(f"    5s-only that would lose the flag:     {c['five_second_only_would_lose_flag']}")

    li = lock_info
    print(f"\nLockout: {li['n_pairs']} pairs, {li['n_pairs_in_estimands']} in the estimands")
    print(f"  decrease after lockout: 5 s {li['n_decrease_5s']}/{li['n_pairs']}, "
          f"cycle {li['n_decrease_cycle']}/{li['n_pairs']}")
    print(f"  calibration: median default 5 s CV {li['median_default_5s']:.4f}, "
          f"locked {li['median_lock_5s']:.4f}, "
          f"{li['pct_lock_below_threshold_5s']:.4f} % below threshold")
    print(f"  excluded from ratio summaries: {li['excluded_from_estimands']} "
          f"-> lock cycle CV {li['excluded_lock_cycle_cv']}, "
          f"Vt {li['excluded_lock_vt_value_mL']}")
    print("\n  summary                        5-second   cycle-resolved   gap %")
    for r in estimands.to_dict(orient="records"):
        print(f"  {r['summary']:<28} {r['five_second']:>10.4f} {r['cycle_resolved']:>15.4f} "
              f"{r['relative_gap_pct']:>7.2f}")
    print(f"  gap range {li['relative_gap_min_pct']:.2f} % to {li['relative_gap_max_pct']:.2f} %; "
          f"cycle-resolved is the larger summary in {li['n_cycle_overstates']} of 4 rows")

    sa = c["sensitivity_native_all"]
    print("\n  sensitivity (NOT published) -- all native 50 Hz samples, i.e. each")
    print("  recorded volume weighted by how long it persists:")
    print(f"    both {sa['flagged_by_both']}, neither {sa['flagged_by_neither']}, "
          f"native-only {sa['native_only']}, 5s-only {sa['five_second_only']}, "
          f"agreement {sa['pct_agree']:.4f} %")
    print(f"    disagrees with the published cycle estimator on "
          f"{sa['n_disagree_with_cycle_estimator']} runs: "
          f"{sa['runs_where_cycle_and_native_disagree']}")

    print(f"\nWrote 5 artefacts to {OUT_DIR.relative_to(REPO)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
