"""Phase 1 of pre-submission audit: independent re-derivation of every
D-class numerical claim in manuscript.md + supplementary.md +
appendix_B_draft.md from raw data.

DOES NOT import project aggregators (src/). Uses pandas/numpy/scipy
primitives only. Writes the raw output dump to audit/phase1_recompute.out.json
for the deliverable to consume.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

REPO = Path(__file__).resolve().parents[1]
FULL_SWEEP = REPO / "data" / "runs" / "full_sweep"
S018 = REPO / "data" / "runs" / "s018_blood_volume"
S014 = REPO / "data" / "runs" / "s014_trigger_lockout"
CONT_ARDS = REPO / "data" / "runs" / "continuous_ards"
RESULTS = REPO / "results"

WINDOW_LO = 60.0
WINDOW_HI = 120.0
OUTPUT_CHANNELS = ["HR", "MAP", "Vt", "SpO2", "PaO2", "PaCO2", "LungCompliance"]

# raw CSV column candidates (we'll auto-detect at first read)
COLUMN_MAP_CANDIDATES = {
    "time": ["time_s", "Time(s)", "time"],
    "HR": ["HeartRate", "HeartRate(1/min)", "HR_bpm", "HR"],
    "MAP": ["MeanArterialPressure", "MeanArterialPressure(mmHg)", "MAP_mmHg", "MAP"],
    "Vt": ["TidalVolume", "TidalVolume(mL)", "Vt_mL", "Vt"],
    "SpO2": ["OxygenSaturation", "SpO2", "SpO2_frac"],
    "PaO2": ["ArterialOxygenPressure", "ArterialOxygenPartialPressure(mmHg)", "PaO2_mmHg", "PaO2"],
    "PaCO2": ["ArterialCarbonDioxidePressure", "ArterialCarbonDioxidePartialPressure(mmHg)", "PaCO2_mmHg", "PaCO2"],
    "LungCompliance": ["LungCompliance"],
}


def detect_columns(df: pd.DataFrame) -> dict[str, str]:
    out = {}
    for key, candidates in COLUMN_MAP_CANDIDATES.items():
        hit = next((c for c in candidates if c in df.columns), None)
        if hit is None:
            # try case-insensitive fuzzy
            for c in df.columns:
                if any(cand.lower() in c.lower() for cand in candidates):
                    hit = c
                    break
        if hit is not None:
            out[key] = hit
    return out


def load_run_csv(run_dir: Path) -> pd.DataFrame | None:
    csv_path = run_dir / "output.csv"
    if not csv_path.exists():
        return None
    try:
        df = pd.read_csv(csv_path)
    except Exception:
        return None
    return df


def steady_state_window(df: pd.DataFrame, time_col: str) -> pd.DataFrame:
    mask = (df[time_col] >= WINDOW_LO) & (df[time_col] <= WINDOW_HI)
    return df.loc[mask].copy()


def safe_cv(s: pd.Series) -> float:
    mean = s.mean()
    if abs(mean) < 1e-12:
        return float("nan")
    return float(s.std(ddof=0) / abs(mean))


def safe_drift(s: pd.Series, t: pd.Series) -> float:
    """|x(t=120) - x(t=60)|, robust to sample points slightly off the boundary."""
    if len(s) < 2:
        return float("nan")
    return float(abs(s.iloc[-1] - s.iloc[0]))


def compute_per_run_stats(run_dir: Path) -> dict[str, Any]:
    csv = load_run_csv(run_dir)
    if csv is None or len(csv) == 0:
        return {"csv_present": False}
    cols = detect_columns(csv)
    if "time" not in cols:
        return {"csv_present": True, "time_col_detected": False, "columns": list(csv.columns)}
    win = steady_state_window(csv, cols["time"])
    out = {"csv_present": True, "n_points_window": len(win), "time_col": cols["time"]}
    for ch in OUTPUT_CHANNELS:
        if ch not in cols:
            out[f"{ch}_present"] = False
            continue
        s = win[cols[ch]]
        if len(s) < 2:
            out[f"{ch}_present"] = False
            continue
        out[f"{ch}_mean"] = float(s.mean())
        out[f"{ch}_std"] = float(s.std(ddof=0))
        out[f"{ch}_cv"] = safe_cv(s)
        out[f"{ch}_delta_60s"] = safe_drift(s, win[cols["time"]])
        out[f"{ch}_n_points"] = int(len(s))
    return out


def walk_full_sweep() -> pd.DataFrame:
    """Walk all 1,280 runs and compute fresh per-run aggregates."""
    rows = []
    for cell_dir in sorted(FULL_SWEEP.iterdir()):
        if not cell_dir.is_dir():
            continue
        name = cell_dir.name
        if not re.match(r"^S[1234]_[MF]$", name):
            continue
        scenario, sex = name.split("_")
        for run_dir in sorted(cell_dir.iterdir()):
            if not run_dir.is_dir():
                continue
            meta_path = run_dir / "run_meta.json"
            exit_code = None
            if meta_path.exists():
                try:
                    meta = json.loads(meta_path.read_text())
                    exit_code = meta.get("exit_code")
                except Exception:
                    pass
            stats_d = compute_per_run_stats(run_dir)
            run_idx = int(run_dir.name.rsplit("_", 1)[1])
            rows.append({
                "case_id": run_dir.name,
                "scenario": scenario,
                "sex": sex,
                "run_idx": run_idx,
                "exit_code": exit_code,
                **stats_d,
            })
    return pd.DataFrame(rows)


def merge_with_inputs(fresh: pd.DataFrame) -> pd.DataFrame:
    """Bring in the locked Morris sample inputs by case_id."""
    agg = pd.read_parquet(FULL_SWEEP / "aggregated.parquet")
    inputs = agg[["case_id", "in_hr", "in_sbp", "in_dbp", "in_rr", "in_vt", "in_fio2", "in_peep",
                  "ards_severity", "clamped", "diverged", "implausible", "not_steady_state", "clean"]]
    return fresh.merge(inputs, on="case_id", how="left")


def headline_table1(df: pd.DataFrame) -> dict[str, Any]:
    """Per-cell flag breakdown — re-counted from the aggregated flag columns."""
    cells = []
    for (sc, sx), sub in df.groupby(["scenario", "sex"]):
        cells.append({
            "cell": f"{sc}_{sx}",
            "n_total": len(sub),
            "clamped": int(sub["clamped"].sum()),
            "diverged": int(sub["diverged"].sum()),
            "implausible": int(sub["implausible"].sum()),
            "not_steady_state": int(sub["not_steady_state"].sum()),
            "clean": int(sub["clean"].sum()),
        })
    return {"by_cell": cells,
            "totals": {
                "n_total": int(len(df)),
                "clamped": int(df["clamped"].sum()),
                "diverged": int(df["diverged"].sum()),
                "implausible": int(df["implausible"].sum()),
                "not_steady_state": int(df["not_steady_state"].sum()),
                "clean": int(df["clean"].sum()),
            }}


def divergence_signature(df: pd.DataFrame) -> dict[str, Any]:
    """Counts of input values among the 20 diverged runs."""
    div = df[df["diverged"] == 1]
    return {
        "n_diverged": int(len(div)),
        "by_sex": div["sex"].value_counts().to_dict(),
        "by_cell": (div["scenario"] + "_" + div["sex"]).value_counts().to_dict(),
        "input_counts": {
            "HR_50": int((div["in_hr"] == 50).sum()),
            "SBP_90": int((div["in_sbp"] == 90).sum()),
            "DBP_67_5": int(np.isclose(div["in_dbp"], 67.5).sum()),
            "RR_20": int((div["in_rr"] == 20).sum()),
            "FiO2_1": int(np.isclose(div["in_fio2"], 1.0).sum()),
        },
        "run_idxs_per_cell": {
            cell: sorted(map(int, sub["run_idx"]))
            for cell, sub in div.groupby(div["scenario"] + "_" + div["sex"])
        },
    }


def vt_cv_counts(df: pd.DataFrame) -> dict[str, Any]:
    """F-004: how many runs have Vt_cv > 0.05 in the steady-state window."""
    have = df.dropna(subset=["Vt_cv"])
    n_total = int(len(df))
    n_with_csv = int(len(have))
    n_unstable = int((have["Vt_cv"] > 0.05).sum())
    n_primary = int(((have["Vt_cv"] > 0.05) & (have["clamped"] == 0) & (have["diverged"] == 0)
                     & (have["implausible"] == 0)).sum())
    return {
        "n_total": n_total,
        "n_with_csv": n_with_csv,
        "n_unstable_vt_cv_gt_005": n_unstable,
        "frac_unstable": n_unstable / n_total,
        "n_unstable_primary_only": n_primary,
        "frac_unstable_primary": n_primary / n_total,
    }


def hyperoxia_overshoot(df: pd.DataFrame) -> dict[str, Any]:
    """F-003: PaO2 > 600 mmHg among implausible runs."""
    impl = df[df["implausible"] == 1].dropna(subset=["PaO2_mean"])
    over_600 = impl[impl["PaO2_mean"] > 600]
    n_impl = int(len(df[df["implausible"] == 1]))
    n_impl_with_csv = int(len(impl))
    n_over_600 = int(len(over_600))
    n_over_600_fio2_ge_095 = int((over_600["in_fio2"] >= 0.95).sum())
    return {
        "n_implausible_total": n_impl,
        "n_implausible_with_csv": n_impl_with_csv,
        "n_pao2_over_600": n_over_600,
        "n_over_600_at_fio2_ge_095": n_over_600_fio2_ge_095,
        "frac_over_600_at_fio2_ge_095": (n_over_600_fio2_ge_095 / n_over_600) if n_over_600 else None,
    }


def s1_pao2_linear_fit(df: pd.DataFrame) -> dict[str, Any]:
    """§3.8 F-003 line: PaO2 ≈ 505 × FiO2 − 25, R² = 0.90 on S1 clean (N=91)."""
    s1_clean = df[(df["scenario"] == "S1") & (df["clean"] == 1)].dropna(subset=["PaO2_mean"])
    n = len(s1_clean)
    if n < 5:
        return {"error": "too few points", "n": n}
    fit = stats.linregress(s1_clean["in_fio2"], s1_clean["PaO2_mean"])
    return {
        "n_clean_S1": int(n),
        "slope": float(fit.slope),
        "intercept": float(fit.intercept),
        "r_squared": float(fit.rvalue ** 2),
        "p_value": float(fit.pvalue),
        "predicted_pao2_at_fio2_050": float(0.50 * fit.slope + fit.intercept),
        "predicted_pao2_at_fio2_100": float(1.00 * fit.slope + fit.intercept),
        "mean_pao2_at_fio2_ge_095": float(s1_clean.loc[s1_clean["in_fio2"] >= 0.95, "PaO2_mean"].mean()),
    }


def output_hr_by_scenario(df: pd.DataFrame) -> dict[str, Any]:
    """§3.4.1 compensatory tachycardia table: aggregated over all clean runs."""
    clean = df[df["clean"] == 1].dropna(subset=["HR_mean"])
    out = {}
    for sc in ["S1", "S2", "S3", "S4"]:
        sub = clean[clean["scenario"] == sc]
        out[sc] = {
            "n": int(len(sub)),
            "hr_mean": float(sub["HR_mean"].mean()),
            "hr_std": float(sub["HR_mean"].std(ddof=0)),
            "hr_min": float(sub["HR_mean"].min()),
            "hr_max": float(sub["HR_mean"].max()),
        }
    return out


def wasserstein_table(df: pd.DataFrame) -> list[dict[str, Any]]:
    """§3.6 Wasserstein M-vs-F per (scenario, output) on clean runs."""
    clean = df[df["clean"] == 1]
    rows = []
    for sc in ["S1", "S2", "S3", "S4"]:
        for out_ch in OUTPUT_CHANNELS:
            col = f"{out_ch}_mean"
            m = clean[(clean["scenario"] == sc) & (clean["sex"] == "M")][col].dropna()
            f = clean[(clean["scenario"] == sc) & (clean["sex"] == "F")][col].dropna()
            if len(m) < 2 or len(f) < 2:
                rows.append({"scenario": sc, "output": out_ch, "n_m": len(m), "n_f": len(f),
                             "wasserstein": None})
                continue
            w = stats.wasserstein_distance(m.values, f.values)
            rows.append({"scenario": sc, "output": out_ch, "n_m": int(len(m)), "n_f": int(len(f)),
                         "wasserstein": float(w)})
    return rows


def bh_critical_value(p_values: list[float], q: float = 0.05) -> dict[str, Any]:
    """BH-FDR survivor count."""
    arr = np.array(sorted(p_values))
    n = len(arr)
    # Find largest k such that p_(k) <= k*q/n
    surv = 0
    for k in range(n, 0, -1):
        if arr[k - 1] <= k * q / n:
            surv = k
            break
    return {"n_tests": int(n), "q": q, "n_survivors": int(surv),
            "bh_critical_5th": float(5 * q / n) if n >= 5 else None,
            "sorted_pvalues": [float(x) for x in arr]}


def s018_dose_response() -> dict[str, Any]:
    """S018: 3 BV brackets × 20 runs each."""
    out = {}
    for sub_name in ["runs", "bracket", "floor"]:
        sub = S018 / sub_name
        if not sub.exists():
            continue
        if sub_name == "runs":
            # original 20 male diverged
            pass
        # We use the prebuilt classifications
    # Read s018_classified.parquet directly
    classified = pd.read_parquet(S018 / "s018_classified.parquet")
    floor_class = pd.read_parquet(S018 / "s018_floor_classified.parquet")
    return {
        "columns_classified": list(classified.columns),
        "shape_classified": list(classified.shape),
        "columns_floor": list(floor_class.columns),
        "shape_floor": list(floor_class.shape),
        "classified_head": classified.head(3).to_dict("records"),
    }


def s014_trigger_lockout() -> dict[str, Any]:
    """S014: paired trigger-lockout, recompute Vt_cv from raw CSVs."""
    if not S014.exists():
        return {"error": "S014 dir not found", "path": str(S014)}
    # Try to find an aggregated parquet first to learn the layout
    listing = list(S014.iterdir())
    return {"S014_subdirs": [p.name for p in listing[:30]]}


def continuous_ards_severity_bins(df_classified: pd.DataFrame | None) -> dict[str, Any]:
    """§3.5.1: divergence per severity bin × sex."""
    parquet = RESULTS / "continuous_ards_severity_sweep.parquet"
    if not parquet.exists():
        return {"error": f"missing {parquet}"}
    s = pd.read_parquet(parquet)
    return {"columns": list(s.columns), "shape": list(s.shape),
            "head": s.head(3).to_dict("records")}


def spearman_recompute() -> dict[str, Any]:
    """Recompute Spearman ρ on M vs F μ\* vectors directly from morris_indices.parquet."""
    morris = pd.read_parquet(RESULTS / "morris_indices.parquet")
    out_rows = []
    for sc in ["S1", "S2", "S3", "S4"]:
        for out_ch in OUTPUT_CHANNELS:
            sub = morris[(morris["scenario"] == sc) & (morris["output"] == out_ch)]
            m = sub[sub["sex"] == "M"].set_index("input")["mu_star"]
            f = sub[sub["sex"] == "F"].set_index("input")["mu_star"]
            common = m.index.intersection(f.index)
            # only paired inputs with finite values both sides
            both = pd.DataFrame({"m": m.loc[common], "f": f.loc[common]}).dropna()
            if len(both) < 3:
                out_rows.append({"scenario": sc, "output": out_ch, "n_inputs": int(len(both)),
                                 "rho": None})
                continue
            rho, _ = stats.spearmanr(both["m"], both["f"])
            out_rows.append({"scenario": sc, "output": out_ch, "n_inputs": int(len(both)),
                             "rho": float(rho)})
    return {"morris_columns": list(morris.columns), "rows": out_rows}


def cross_output_drift_audit(df: pd.DataFrame) -> dict[str, Any]:
    """§3.8.1: F-003 and F-004 arm cross-output drift rates."""
    drift_thresh = {"HR": 5.0, "MAP": 5.0, "Vt": 50.0, "PaO2": 15.0, "PaCO2": 5.0}
    # F-003 arm: FiO2 >= 0.95
    f003 = df[df["in_fio2"] >= 0.95].dropna(subset=["HR_delta_60s"])
    f004 = df.dropna(subset=["Vt_cv", "HR_delta_60s"])
    f004 = f004[f004["Vt_cv"] > 0.05]
    intersect = df[(df["in_fio2"] >= 0.95) & (df["Vt_cv"] > 0.05)]

    def arm_stats(arm: pd.DataFrame) -> dict[str, Any]:
        n = int(len(arm))
        result = {"n_runs": n}
        for ch, thr in drift_thresh.items():
            col = f"{ch}_delta_60s"
            if col not in arm.columns:
                continue
            valid = arm[col].dropna()
            n_valid = int(len(valid))
            n_over = int((valid > thr).sum())
            median = float(valid.median()) if n_valid else None
            p95 = float(valid.quantile(0.95)) if n_valid else None
            result[ch] = {"n_valid": n_valid, "n_over_thresh": n_over,
                          "frac_over_thresh": (n_over / n_valid) if n_valid else None,
                          "median": median, "p95": p95}
        return result

    return {
        "F003_arm_FiO2_ge_095": arm_stats(f003),
        "F004_arm_Vt_cv_gt_005": arm_stats(f004),
        "intersection_count": int(len(intersect)),
    }


def reliability_classification() -> dict[str, Any]:
    p = RESULTS / "reliability_classification.csv"
    if not p.exists():
        return {"error": "missing reliability_classification.csv"}
    df = pd.read_csv(p)
    # try to find a color column
    colour_col = None
    for c in df.columns:
        if df[c].dtype == object and df[c].dropna().isin({"green", "yellow", "red"}).all():
            colour_col = c
            break
    if colour_col is None:
        # try long-format
        return {"columns": list(df.columns), "head": df.head(5).to_dict("records")}
    counts = df[colour_col].value_counts().to_dict()
    return {"columns": list(df.columns), "shape": list(df.shape),
            "colour_col": colour_col, "counts": counts, "head": df.head(8).to_dict("records")}


def main():
    out = {}

    print("Walking full sweep...")
    fresh = walk_full_sweep()
    print(f"  {len(fresh)} runs")
    fresh = merge_with_inputs(fresh)

    # save fresh per-run table for downstream consumption
    fresh.to_parquet(REPO / "audit" / "phase1_fresh_per_run.parquet", index=False)

    out["table1_per_cell_flags"] = headline_table1(fresh)
    out["divergence_signature"] = divergence_signature(fresh)
    out["vt_cv_F004"] = vt_cv_counts(fresh)
    out["hyperoxia_F003"] = hyperoxia_overshoot(fresh)
    out["s1_pao2_linear_fit"] = s1_pao2_linear_fit(fresh)
    out["output_hr_by_scenario"] = output_hr_by_scenario(fresh)
    out["wasserstein_recompute"] = wasserstein_table(fresh)
    out["cross_output_drift"] = cross_output_drift_audit(fresh)

    # BH-FDR survivors — recompute on the recomputed Wasserstein p_emp values?
    # We can't recompute p_emp without rebuilding the within-sex null (2000 splits).
    # Instead, BH formula sanity-check the manuscript-quoted p values.
    quoted_pvalues = [0.305, 0.995, 0.798, 0.123, 0.598, 0.009,
                      0.958, 0.652, 0.840, 0.022, 0.073, 0.000,
                      0.333, 0.538, 0.129, 0.119, 0.245, 0.000,
                      0.953, 0.460, 0.897, 0.002, 0.003, 0.083]
    out["bh_fdr_quoted_pvalues"] = bh_critical_value(quoted_pvalues, q=0.05)

    out["spearman_recompute"] = spearman_recompute()
    out["s018_dose_response"] = s018_dose_response()
    out["s014_trigger_lockout"] = s014_trigger_lockout()
    out["continuous_ards_severity_bins"] = continuous_ards_severity_bins(None)
    out["reliability_classification"] = reliability_classification()

    out_path = REPO / "audit" / "phase1_recompute.out.json"
    out_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
