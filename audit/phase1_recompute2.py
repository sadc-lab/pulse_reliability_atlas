"""Phase 1 follow-up checks: items the first pass didn't cover.

- S018 dose-response counts per BV bracket
- S014 trigger-lockout median paired CV change
- Continuous-ARDS severity-bin counts (§3.5.1)
- Reliability classification colour counts (manuscript §3.7 vs supplementary §S9)
- Cornish Table 2 internal sums
- Appendix-B sweep self-consistency
- §3.3.1 sigma/mu_star CI buckets (using stored morris_indices)
- Top-3 fraction (§3.3 H1)
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

REPO = Path(__file__).resolve().parents[1]
FULL_SWEEP = REPO / "data" / "runs" / "full_sweep"
S018 = REPO / "data" / "runs" / "s018_blood_volume"
S014 = REPO / "data" / "runs" / "s014_trigger_lockout"
CONT = REPO / "data" / "runs" / "continuous_ards"
RESULTS = REPO / "results"

out = {}

# ---------------------------------------------------------------- S018 BV
s018 = pd.read_parquet(S018 / "s018_classified.parquet")
s018_floor = pd.read_parquet(S018 / "s018_floor_classified.parquet")
# bracket subset
br = s018[s018["bv_label"] == "bracket"]
fl = s018[s018["bv_label"] == "floor"]
print("S018 bracket: n=", len(br))
print("S018 floor (from s018_classified): n=", len(fl))

def s018_counts(df):
    return {
        "n_total": int(len(df)),
        "diverged": int(df["diverged"].sum()),
        "implausible": int(df["implausible"].sum()),
        "not_steady_state": int(df["not_steady_state"].sum()),
        "clean": int(df["clean"].sum()),
    }

out["s018_default_4802_63"] = {
    "n_total": 20,
    "diverged": 20,
    "note": "default-image runs are the 20 original diverged inputs — manuscript Table value is reference, no CSV produced.",
}
out["s018_bracket_4400"] = s018_counts(br)
out["s018_floor_4082_24"] = s018_counts(fl)

# ---------------------------------------------------------------- S014
s014_paired = pd.read_parquet(S014 / "paired_comparison.parquet")
print("S014 paired_comparison columns:", list(s014_paired.columns))
print("S014 paired n:", len(s014_paired))
# Median paired difference (Vt_cv_original - Vt_cv_lockout)
if "Vt_cv_original" in s014_paired.columns and "Vt_cv_lockout" in s014_paired.columns:
    diff = s014_paired["Vt_cv_original"] - s014_paired["Vt_cv_lockout"]
    out["s014_trigger_lockout"] = {
        "n_paired": int(len(s014_paired)),
        "median_diff": float(diff.median()),
        "median_original": float(s014_paired["Vt_cv_original"].median()),
        "median_lockout": float(s014_paired["Vt_cv_lockout"].median()),
        "max_original": float(s014_paired["Vt_cv_original"].max()),
        "max_lockout": float(s014_paired["Vt_cv_lockout"].max()),
        "frac_lockout_below_005": float((s014_paired["Vt_cv_lockout"] < 0.05).mean()),
    }
else:
    out["s014_trigger_lockout"] = {"columns": list(s014_paired.columns),
                                   "head": s014_paired.head(3).to_dict("records")}

# ---------------------------------------------------------------- Continuous ARDS
cont = pd.read_parquet(RESULTS / "continuous_ards_severity_sweep.parquet")
print("cont shape:", cont.shape, "cols (last):", list(cont.columns)[-5:])
# Severity bins per §3.5.1
bins = [(0.0, 0.5, "[0, 0.5]"),
        (0.5, 0.85, "(0.5, 0.85]"),
        (0.85, 0.91, "(0.85, 0.91]"),
        (0.91, 0.945, "(0.91, 0.945]"),
        (0.945, 0.95, "(0.945, 0.95]"),
        (0.95, 1.01, "(0.95, 1.0]")]
sev_col = "ards_severity_continuous" if "ards_severity_continuous" in cont.columns else "ards_severity"
binned = []
for lo, hi, label in bins:
    if lo == 0:
        mask = (cont[sev_col] >= lo) & (cont[sev_col] <= hi)
    else:
        mask = (cont[sev_col] > lo) & (cont[sev_col] <= hi)
    sub = cont[mask]
    row = {"label": label}
    for sex in ["F", "M"]:
        sex_sub = sub[sub["sex"] == sex]
        row[f"{sex}_n"] = int(len(sex_sub))
        row[f"{sex}_diverged"] = int(sex_sub["diverged"].sum())
    binned.append(row)
out["cont_severity_bins"] = binned

# Find lowest F-diverged severity (instability band lower edge)
f_div = cont[(cont["sex"] == "F") & (cont["diverged"])]
m_div = cont[(cont["sex"] == "M") & (cont["diverged"])]
out["cont_lowest_F_diverged_severity"] = float(f_div[sev_col].min()) if len(f_div) else None
out["cont_lowest_M_diverged_severity"] = float(m_div[sev_col].min()) if len(m_div) else None
out["cont_highest_F_diverged_severity"] = float(f_div[sev_col].max()) if len(f_div) else None
out["cont_highest_M_diverged_severity"] = float(m_div[sev_col].max()) if len(m_div) else None
out["cont_F_diverged_total"] = int(len(f_div))
out["cont_M_diverged_total"] = int(len(m_div))

# ---------------------------------------------------------------- Reliability traffic light
rc = pd.read_csv(RESULTS / "reliability_classification.csv")
print("rc shape:", rc.shape, "cols:", list(rc.columns))
colour_counts = rc["light"].value_counts().to_dict()
out["reliability_colours"] = {"counts": colour_counts, "total_rows": int(len(rc))}

# Per-cell grid (sanity)
pivot = rc.pivot_table(index=["scenario", "sex"], columns="output", values="light", aggfunc="first")
out["reliability_grid"] = pivot.reset_index().to_dict("records")

# ---------------------------------------------------------------- Top-3 fraction (H1)
h1 = pd.read_csv(RESULTS / "h1_top3_fraction.csv")
print("h1 shape:", h1.shape, "cols:", list(h1.columns))
out["h1_top3"] = {
    "n_rows": int(len(h1)),
    "min": float(h1["top3_fraction"].min()) if "top3_fraction" in h1.columns else None,
    "median": float(h1["top3_fraction"].median()) if "top3_fraction" in h1.columns else None,
    "max": float(h1["top3_fraction"].max()) if "top3_fraction" in h1.columns else None,
    "n_above_05": int((h1["top3_fraction"] >= 0.5).sum()) if "top3_fraction" in h1.columns else None,
    "columns": list(h1.columns),
    "head": h1.head(3).to_dict("records"),
}

# ---------------------------------------------------------------- Sigma/mu* CI buckets (§3.3.1)
mi = pd.read_parquet(RESULTS / "morris_indices.parquet")
# Dominant input per (scenario, sex, output) — argmax of mu_star
dom = mi.sort_values("mu_star", ascending=False).groupby(["scenario", "sex", "output"]).head(1)
dom = dom.copy()
dom["sigma_over_mu"] = dom["sigma"] / dom["mu_star"]
dom["sigma_hi_over_mu"] = dom["sigma_hi"] / dom["mu_star"]
dom["sigma_lo_over_mu"] = dom["sigma_lo"] / dom["mu_star"]
n_cells = len(dom)
# Buckets
def classify_row(r):
    if pd.isna(r["sigma_lo"]) or pd.isna(r["sigma_hi"]):
        return "no_CI"
    if r["sigma_lo_over_mu"] >= 0.6:
        return "robust_nonlinear"
    if r["sigma_hi_over_mu"] < 0.6:
        return "robust_linear"
    return "straddle"
dom["bucket"] = dom.apply(classify_row, axis=1)
out["sigma_mu_buckets"] = {
    "n_cells_total": int(n_cells),
    "counts": dom["bucket"].value_counts().to_dict(),
    "n_point_trigger_above_06": int((dom["sigma_over_mu"] >= 0.6).sum()),
    "n_point_below_06": int((dom["sigma_over_mu"] < 0.6).sum()),
}
# Which cells are no-CI?
no_ci_rows = dom[dom["bucket"] == "no_CI"]
out["sigma_mu_no_CI_cells"] = no_ci_rows[["scenario", "sex", "output", "input", "n_clean_pairs"]].to_dict("records")

# ---------------------------------------------------------------- Cornish Table 2 internal
cornish_table2 = [
    {"channel": "Chloride", "hoeffding": 24, "bootstrap": 47, "atlas_overlap": False},
    {"channel": "Sodium", "hoeffding": 21, "bootstrap": 46, "atlas_overlap": False},
    {"channel": "Potassium", "hoeffding": 13, "bootstrap": 33, "atlas_overlap": False},
    {"channel": "Skin Temperature", "hoeffding": 10, "bootstrap": 43, "atlas_overlap": False},
    {"channel": "Calcium", "hoeffding": 5, "bootstrap": 44, "atlas_overlap": False},
    {"channel": "Glucose", "hoeffding": 5, "bootstrap": 19, "atlas_overlap": False},
    {"channel": "HCO3", "hoeffding": 2, "bootstrap": 8, "atlas_overlap": False},
    {"channel": "pH", "hoeffding": 0, "bootstrap": 0, "atlas_overlap": False},
    {"channel": "PaCO2", "hoeffding": 3, "bootstrap": 13, "atlas_overlap": True},
    {"channel": "PaO2", "hoeffding": 0, "bootstrap": 4, "atlas_overlap": True},
    {"channel": "MeanBP", "hoeffding": 0, "bootstrap": 3, "atlas_overlap": True},
    {"channel": "SysBP", "hoeffding": 2, "bootstrap": 8, "atlas_overlap": False},  # partial
    {"channel": "DiaBP", "hoeffding": 0, "bootstrap": 0, "atlas_overlap": False},  # partial
    {"channel": "HR", "hoeffding": 0, "bootstrap": 1, "atlas_overlap": True},
    {"channel": "RR", "hoeffding": 0, "bootstrap": 12, "atlas_overlap": False},
]
total_h = sum(r["hoeffding"] for r in cornish_table2)
total_b = sum(r["bootstrap"] for r in cornish_table2)
overlap_h = sum(r["hoeffding"] for r in cornish_table2 if r["atlas_overlap"])
overlap_b = sum(r["bootstrap"] for r in cornish_table2 if r["atlas_overlap"])
non_overlap_h = total_h - overlap_h
non_overlap_b = total_b - overlap_b
# Non-cardiorespiratory = 7 channels per manuscript footnote in §4.4
nc_h = sum(r["hoeffding"] for r in cornish_table2 if r["channel"] in
           ["Chloride", "Sodium", "Potassium", "Skin Temperature", "Calcium", "Glucose", "HCO3"])
nc_b = sum(r["bootstrap"] for r in cornish_table2 if r["channel"] in
           ["Chloride", "Sodium", "Potassium", "Skin Temperature", "Calcium", "Glucose", "HCO3"])
out["cornish_table2_internal"] = {
    "total_hoeffding": total_h,
    "total_bootstrap": total_b,
    "overlap_hoeffding_3_channels": overlap_h,
    "overlap_bootstrap_3_channels": overlap_b,
    "non_overlap_hoeffding": non_overlap_h,
    "non_overlap_bootstrap": non_overlap_b,
    "non_cardiorespiratory_hoeffding_7chans": nc_h,
    "non_cardiorespiratory_bootstrap_7chans": nc_b,
    "rows": cornish_table2,
}

# ---------------------------------------------------------------- BV difference percentage
m_bv = 4802.63
f_bv = 3996.09
out["bv_difference_pct"] = {
    "male_default_mL": m_bv,
    "female_default_mL": f_bv,
    "diff_mL": m_bv - f_bv,
    "diff_pct_vs_male": (m_bv - f_bv) / m_bv * 100,
    "diff_pct_vs_female": (m_bv - f_bv) / f_bv * 100,
}

# ---------------------------------------------------------------- Sex divergence rate (§3.5)
out["sex_divergence_rate"] = {
    "male_diverged_per_male_runs": 20 / 640,  # 4 cells * 160
    "female_diverged_per_female_runs": 0 / 640,
    "male_rate_pct": 20 / 640 * 100,
    "x_more_likely": 20 / 1,  # vs zero — caveat
}

# ---------------------------------------------------------------- Compliance constancy on S1_F_0008
out["s1_f_0008_lung_compliance_check"] = {}
nat = pd.read_csv(FULL_SWEEP / "S1_F" / "S1_F_0008" / "output_pulse_native.csv")
tcol = "Time(s)" if "Time(s)" in nat.columns else "time_s"
ccol = "LungCompliance(L/cmH2O)" if "LungCompliance(L/cmH2O)" in nat.columns else "LungCompliance"
win = nat[(nat[tcol] >= 60.0) & (nat[tcol] <= 120.0)]
out["s1_f_0008_lung_compliance_check"] = {
    "n_points": int(len(win)),
    "mean": float(win[ccol].mean()),
    "std": float(win[ccol].std(ddof=0)),
    "min": float(win[ccol].min()),
    "max": float(win[ccol].max()),
    "range": float(win[ccol].max() - win[ccol].min()),
}

# ---------------------------------------------------------------- Save
(REPO / "audit" / "phase1_recompute2.out.json").write_text(json.dumps(out, indent=2, default=str))
print("Wrote audit/phase1_recompute2.out.json")
