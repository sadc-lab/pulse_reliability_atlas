# Results — analysis artifacts

This directory holds the outputs of `scripts/analyze_sweep.py`. Every file
here is regenerated from `data/runs/full_sweep/aggregated.parquet` and
`data/runs/full_sweep/morris_sample.parquet`. None of these files is hand-
edited.

## Files

| File | Source | Description |
|------|--------|-------------|
| `cell_flag_summary.csv`        | `analysis_compare.cell_flag_summary` | Per-cell counts of `clamped`, `diverged`, `implausible`, `not_steady_state`, `clean`. Candidate for the paper's Table 1. |
| `morris_indices.parquet`       | `analysis_morris.morris_indices`    | (μ, μ\*, σ, μ\* 95 % bootstrap CI) per cell × output × input, computed on clean runs only. Also carries `n_clean_pairs`, `n_total_pairs` and `n_trajectories`: how many of the 20 elementary-effect pairs actually entered each index. |
| `h1_top3_fraction.csv`         | `analysis_morris.evaluate_h1`       | Per cell × output: fraction of summed μ\* concentrated in the top-3 ranked inputs; H1 pass / fail. |
| `sobol_promotion.csv`          | `analysis_morris.sobol_promotion`   | Top-3 Morris inputs per cell × output with σ/μ\* ratio and promote / skip / gray decision. |
| `wasserstein_male_vs_female.csv` | `analysis_compare.wasserstein_per_output` | H4 — Wasserstein distance between M and F clean-run output distributions per scenario × output. |
| `spearman_mu_star.csv`         | `analysis_compare.spearman_mu_star_male_vs_female` | H4 — Spearman ρ between male μ\* vector and female μ\* vector per scenario × output. |
| `clamp_grid.parquet`           | `analysis_compare.flag_count_grid`  | 2D heatmap source for the clamp map (input-pair × cell × bin → rate). |
| `diverged_grid.parquet`        | `analysis_compare.flag_count_grid`  | Same for divergence. |
| `reliability_classification.csv` | `analysis_compare.reliability_classification` | Per cell × output green / yellow / red traffic light. |
| `detector_validation_summary.csv` | `scripts/validate_detector_on_existing_runs.py` | One-off detector validation against the 20 reference Pulse runs in `Pulse_translation_new/data/engine_runs/`. Useful for traceability; not part of the per-sweep regeneration loop. |

## Reading these

* The atomic unit is one row of `morris_indices.parquet`: a single
  `(scenario, sex, output, input)` tuple with its μ\*, σ, and CI.
* Read `n_clean_pairs` before reading μ\*. An input whose runs are mostly
  flagged contributes few pairs, and a row with `n_clean_pairs == 1` is one
  finite difference: its σ is 0 by construction, not by measurement, and no
  bootstrap CI exists for it. A row is absent entirely when the input has no
  clean pair at all in that cell.
* `top3_fraction` in `h1_top3_fraction.csv` is the formal H1 measurement;
  the pre-registered threshold is 0.5.
* `decision == "promote"` in `sobol_promotion.csv` selects the
  (cell × output × input) combinations for the (optional) Sobol bolt-on.
* `reliability_classification.csv`'s `light` column is the user-facing
  output: green ⇒ safe to use that input range in that cell; yellow ⇒
  use with caveats; red ⇒ avoid (or treat as a *finding* worth quoting in
  the paper).

## Regeneration

```bash
uv run python scripts/analyze_sweep.py
uv run python scripts/make_figures.py
```

Both scripts are idempotent; re-running them overwrites their outputs in
place.
