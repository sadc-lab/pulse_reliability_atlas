"""End-to-end analysis on the full-sweep master Parquet.

Run after `scripts/run_full_sweep.py` finishes. Produces:

    results/morris_indices.parquet           — μ, μ\*, σ, μ\* CI per cell × output × input
    results/sobol_promotion.csv              — top-3 inputs per cell × output + decision
    results/h1_top3_fraction.csv             — H1 evaluation per cell × output
    results/wasserstein_male_vs_female.csv   — H4 distribution divergence
    results/spearman_mu_star.csv             — H4 ranking similarity
    results/cell_flag_summary.csv            — Table 1 candidate
    results/reliability_classification.csv   — green/yellow/red traffic light
    results/clamp_grid.parquet               — 2D heatmap source for clamp map
    results/diverged_grid.parquet            — same for divergence map

Usage::

    uv run python scripts/analyze_sweep.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.analysis_compare import (  # noqa: E402
    cell_flag_summary,
    flag_count_grid,
    reliability_classification,
    spearman_mu_star_male_vs_female,
    wasserstein_per_output,
)
from src.analysis_morris import (  # noqa: E402
    evaluate_h1,
    morris_indices,
    sobol_promotion,
)
from src.scenario import iter_cells  # noqa: E402


SWEEP_ROOT = REPO_ROOT / "data" / "runs" / "full_sweep"
SAMPLE_PATH = SWEEP_ROOT / "morris_sample.parquet"
MASTER_PARQUET = SWEEP_ROOT / "aggregated.parquet"
RESULTS_DIR = REPO_ROOT / "results"


def main() -> int:
    if not MASTER_PARQUET.exists():
        print(f"[analyze] master parquet missing at {MASTER_PARQUET}")
        return 1
    if not SAMPLE_PATH.exists():
        print(f"[analyze] morris sample missing at {SAMPLE_PATH}")
        return 1

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(MASTER_PARQUET)
    sample = pd.read_parquet(SAMPLE_PATH)
    cells = list(iter_cells())
    scenarios = sorted({sk for sk, _ in cells})

    print(f"[analyze] master rows: {len(df)}")
    print(f"[analyze] sample rows: {len(sample)}")

    # 1. Cell flag summary (Table 1 candidate)
    flag_summary = cell_flag_summary(df)
    flag_summary.to_csv(RESULTS_DIR / "cell_flag_summary.csv", index=False)
    print("\n=== Cell flag summary ===")
    print(flag_summary.to_string(index=False))

    # 2. Morris indices with bootstrap CI
    print("\n[analyze] computing Morris indices (bootstrap=1000)...")
    morris_df = morris_indices(df, sample, cells, n_bootstrap=1000)
    morris_df.to_parquet(RESULTS_DIR / "morris_indices.parquet", index=False)
    print(f"[analyze] morris rows: {len(morris_df)}")

    # 3. H1 evaluation
    h1 = evaluate_h1(morris_df)
    h1.to_csv(RESULTS_DIR / "h1_top3_fraction.csv", index=False)
    n_pass = int(h1["h1_pass"].sum())
    print(f"\n=== H1 evaluation ({n_pass}/{len(h1)} cell-output pairs pass) ===")
    print(h1.to_string(index=False))

    # 4. Sobol promotion
    sobol = sobol_promotion(morris_df)
    sobol.to_csv(RESULTS_DIR / "sobol_promotion.csv", index=False)
    promote = sobol[sobol["decision"] == "promote"]
    print(f"\n[analyze] Sobol promote: {len(promote)} input × cell × output combos")

    # 5. Sex comparison (H4)
    wass = wasserstein_per_output(df, scenarios)
    wass.to_csv(RESULTS_DIR / "wasserstein_male_vs_female.csv", index=False)
    spearman = spearman_mu_star_male_vs_female(morris_df, scenarios)
    spearman.to_csv(RESULTS_DIR / "spearman_mu_star.csv", index=False)
    print("\n=== H4 — sex comparison (Wasserstein) ===")
    print(wass.to_string(index=False))
    print("\n=== H4 — sex comparison (Spearman ρ on μ\*) ===")
    print(spearman.to_string(index=False))

    # 6. Clamp / divergence maps
    print("\n[analyze] computing flag heatmaps...")
    clamp_grid = flag_count_grid(df, "clamped")
    clamp_grid.to_parquet(RESULTS_DIR / "clamp_grid.parquet", index=False)
    div_grid = flag_count_grid(df, "diverged")
    div_grid.to_parquet(RESULTS_DIR / "diverged_grid.parquet", index=False)

    # 7. Reliability classification
    rel = reliability_classification(df)
    rel.to_csv(RESULTS_DIR / "reliability_classification.csv", index=False)
    print("\n=== Reliability classification ===")
    print(rel.to_string(index=False))

    print(f"\n[analyze] all artifacts in {RESULTS_DIR.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
