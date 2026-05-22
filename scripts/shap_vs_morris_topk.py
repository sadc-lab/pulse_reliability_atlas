"""S023 — Supplementary ML/SHAP cross-check of Morris mu* rankings.

Train one RandomForestRegressor per output channel on the clean subset of the
1280-run sweep, with `sex` and `scenario` encoded as additional features
alongside the 7 operational inputs (hr, rr, sbp, dbp, vt, fio2, peep). Compute
SHAP values via TreeExplainer, derive a feature-importance ranking from mean
|SHAP|, and compare the top-3 *operational-input* features against the Morris
mu* top-3 (per (cell, output)).

Honest scoping (matches S023 caveats):
- Training data = the clean subset only (~663 runs), so the surrogate learns
  the well-behaved sub-region of input space.
- The Morris design is OAT — the input distribution is not uniform; the
  surrogate's SHAP attributions reflect that empirical distribution.
- 7 operational inputs ⇒ top-3 overlap is the headline metric (Spearman rho
  on rank-7 lists has insufficient resolution).
- Sex and scenario are included as features to absorb confounding (Morris
  is computed within a cell, so sex/scenario are *not* in its 7-input
  ranking); they get reported separately in the SHAP magnitude table.

Outputs:
  results/s023/rf_metrics.csv
  results/s023/shap_mean_abs.csv
  results/s023/topk_overlap.csv
  results/s023/topk_overlap_per_cell.csv
  results/s023/shap_vs_morris_summary.json
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import shap
from sklearn.ensemble import RandomForestRegressor

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "s023"
OUT_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FEATURES = ["hr", "rr", "sbp", "dbp", "vt", "fio2", "peep"]  # 7 operational inputs
OPERATIONAL_INPUT_COLS = [f"in_{f}" for f in INPUT_FEATURES]
EXTRA_FEATURES = ["sex", "scenario"]  # absorb confounding
ALL_FEATURES = INPUT_FEATURES + EXTRA_FEATURES

OUTPUTS = ["HR", "MAP", "Vt", "SpO2", "PaO2", "PaCO2"]
OUTPUT_COLS = [f"{o}_mean" for o in OUTPUTS]

# Random seed for the RF — locked for reproducibility
RF_SEED = 42

K = 3  # top-k overlap


def build_design_matrix(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Construct the feature matrix.

    `sex` and `scenario` are one-hot encoded (drop_first=False so SHAP gives a
    value per category, which is easier to interpret than a contrast).
    Operational inputs are passed through.
    """
    feat = df[OPERATIONAL_INPUT_COLS].copy()
    feat.columns = INPUT_FEATURES  # rename in_hr -> hr, etc.
    sex_oh = pd.get_dummies(df["sex"], prefix="sex").astype(float)
    sc_oh = pd.get_dummies(df["scenario"], prefix="scenario").astype(float)
    X = pd.concat([feat, sex_oh, sc_oh], axis=1)
    feature_names = list(X.columns)
    return X, feature_names


def topk_overlap(set_a: list[str], set_b: list[str], k: int = K) -> dict:
    a = set(set_a[:k])
    b = set(set_b[:k])
    overlap = a & b
    return {
        "overlap_size": len(overlap),
        "overlap_features": sorted(overlap),
        "a_top": list(set_a[:k]),
        "b_top": list(set_b[:k]),
        "jaccard": len(overlap) / len(a | b) if (a | b) else 0.0,
    }


def main() -> None:
    df = pd.read_parquet(ROOT / "data" / "runs" / "full_sweep" / "aggregated.parquet")
    morris = pd.read_parquet(ROOT / "results" / "morris_indices.parquet")

    clean = df[df["clean"]].copy()
    print(f"Loaded {len(df)} total runs; {len(clean)} clean (selection bias warning).")

    # Coverage diagnostic on the clean subset
    cov = clean.groupby(["scenario", "sex"]).size().reset_index(name="n_clean")
    print("\nClean coverage per cell:")
    print(cov.to_string(index=False))

    X, feature_names = build_design_matrix(clean)
    print(f"\nFeature matrix: {X.shape}  features={feature_names}")

    rf_metrics_rows = []
    shap_mean_abs_rows = []
    topk_global_rows = []
    topk_percell_rows = []

    # SHAP needs identical feature order for the model; we'll keep one X.
    # SHAP TreeExplainer is exact for tree models.

    for out_name, out_col in zip(OUTPUTS, OUTPUT_COLS):
        y = clean[out_col].to_numpy(float)
        # Skip if everything is NaN (can happen for SpO2 in extremely sick cells)
        mask = np.isfinite(y)
        if mask.sum() < 30:
            print(f"[skip] {out_name}: only {mask.sum()} finite clean values")
            continue
        Xm = X.loc[mask]
        ym = y[mask]

        rf = RandomForestRegressor(random_state=RF_SEED)  # defaults per user spec
        rf.fit(Xm, ym)
        r2_train = rf.score(Xm, ym)

        # SHAP — TreeExplainer
        explainer = shap.TreeExplainer(rf)
        sv = explainer.shap_values(Xm)
        # sv shape: (n_samples, n_features). Mean |SHAP| per feature.
        mean_abs = np.abs(sv).mean(axis=0)
        for fname, val in zip(feature_names, mean_abs):
            shap_mean_abs_rows.append(
                {"output": out_name, "feature": fname, "mean_abs_shap": float(val)}
            )

        # Restrict SHAP to the 7 operational inputs for top-k comparison with Morris
        op_idx = [feature_names.index(f) for f in INPUT_FEATURES]
        op_shap = {f: mean_abs[i] for f, i in zip(INPUT_FEATURES, op_idx)}
        shap_ranking = sorted(op_shap.items(), key=lambda kv: -kv[1])
        shap_top_ranked = [name for name, _ in shap_ranking]

        # Morris top-3 — pooled across cells (mean rank of mu_star per input)
        m_out = morris[morris["output"] == out_name].copy()
        if m_out.empty:
            print(f"[warn] no Morris rows for {out_name}")
            continue
        # rank within each (scenario, sex), then average
        m_out["rank"] = m_out.groupby(["scenario", "sex"])["mu_star"].rank(
            ascending=False, method="dense"
        )
        morris_mean_rank = (
            m_out.groupby("input")["rank"].mean().sort_values()
        )
        morris_global_ranking = morris_mean_rank.index.tolist()

        ov = topk_overlap(shap_top_ranked, morris_global_ranking, k=K)
        topk_global_rows.append(
            {
                "output": out_name,
                "shap_top3": "|".join(ov["a_top"]),
                "morris_top3": "|".join(ov["b_top"]),
                "overlap_size": ov["overlap_size"],
                "overlap_features": "|".join(ov["overlap_features"]),
                "jaccard": ov["jaccard"],
            }
        )

        # Per-cell SHAP would require training 8 RFs per output on ~50-150 runs
        # each. With RF defaults (100 trees) and that little data, the SHAP
        # ranking gets noisy. Report per-cell mean-rank comparison from the
        # global RF instead: split SHAP rows by (scenario, sex) and rerank.
        # This is *not* the same as fitting per-cell RFs (we acknowledge that
        # in the supplementary text).
        sv_df = pd.DataFrame(sv, columns=feature_names, index=Xm.index)
        joined = clean.loc[Xm.index, ["scenario", "sex"]].join(sv_df.abs())
        for (sc, sx), g in joined.groupby(["scenario", "sex"]):
            cell_mean_abs = g[INPUT_FEATURES].mean()
            cell_rank = cell_mean_abs.sort_values(ascending=False).index.tolist()

            m_cell = morris[
                (morris["scenario"] == sc)
                & (morris["sex"] == sx)
                & (morris["output"] == out_name)
            ].copy()
            if m_cell.empty:
                continue
            morris_cell_rank = (
                m_cell.sort_values("mu_star", ascending=False)["input"].tolist()
            )
            cell_ov = topk_overlap(cell_rank, morris_cell_rank, k=K)
            topk_percell_rows.append(
                {
                    "scenario": sc,
                    "sex": sx,
                    "output": out_name,
                    "shap_top3": "|".join(cell_ov["a_top"]),
                    "morris_top3": "|".join(cell_ov["b_top"]),
                    "overlap_size": cell_ov["overlap_size"],
                    "overlap_features": "|".join(cell_ov["overlap_features"]),
                    "jaccard": cell_ov["jaccard"],
                    "n_runs_in_cell": int(len(g)),
                }
            )

        rf_metrics_rows.append(
            {
                "output": out_name,
                "n_train": int(len(Xm)),
                "r2_train": float(r2_train),
                "n_features": int(Xm.shape[1]),
                "shap_top3_op": "|".join(shap_top_ranked[:3]),
                "morris_top3_pooled": "|".join(morris_global_ranking[:3]),
            }
        )

    rf_metrics = pd.DataFrame(rf_metrics_rows)
    shap_mean_abs = pd.DataFrame(shap_mean_abs_rows)
    topk_global = pd.DataFrame(topk_global_rows)
    topk_percell = pd.DataFrame(topk_percell_rows)

    rf_metrics.to_csv(OUT_DIR / "rf_metrics.csv", index=False)
    shap_mean_abs.to_csv(OUT_DIR / "shap_mean_abs.csv", index=False)
    topk_global.to_csv(OUT_DIR / "topk_overlap.csv", index=False)
    topk_percell.to_csv(OUT_DIR / "topk_overlap_per_cell.csv", index=False)

    # Summary stats
    if len(topk_global):
        global_avg = float(topk_global["overlap_size"].mean())
    else:
        global_avg = float("nan")
    if len(topk_percell):
        percell_avg = float(topk_percell["overlap_size"].mean())
        percell_full = int((topk_percell["overlap_size"] == K).sum())
        percell_total = len(topk_percell)
    else:
        percell_avg, percell_full, percell_total = float("nan"), 0, 0

    summary = {
        "n_runs_total": int(len(df)),
        "n_runs_clean": int(len(clean)),
        "outputs_modeled": [r["output"] for r in rf_metrics_rows],
        "features_used": feature_names,
        "rf_settings": {
            "model": "RandomForestRegressor(defaults, random_state=42)",
            "n_estimators": 100,
            "max_features": "sqrt",
        },
        "k": K,
        "global_avg_topk_overlap": global_avg,
        "per_cell_avg_topk_overlap": percell_avg,
        "per_cell_full_match_count": percell_full,
        "per_cell_total_comparisons": percell_total,
        "caveats": [
            "Training data is the clean subset only (selection bias).",
            "Morris design is OAT, not uniform; SHAP attributions reflect empirical input distribution.",
            "Per-cell SHAP comes from cell-conditional means of a single global RF, not from per-cell RFs (per-cell n=50-150 is too small for stable RF training).",
            "Sex/scenario one-hot features are included to absorb confounding; comparison vs Morris is restricted to the 7 operational inputs.",
        ],
    }
    (OUT_DIR / "shap_vs_morris_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    print("\n=== RF metrics ===")
    print(rf_metrics.to_string(index=False))
    print("\n=== Pooled SHAP vs Morris top-3 overlap (k=3) ===")
    print(topk_global.to_string(index=False))
    print("\n=== Per-cell top-3 overlap (cell-conditional SHAP vs cell Morris) ===")
    print(topk_percell.to_string(index=False))
    print("\nSummary:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
