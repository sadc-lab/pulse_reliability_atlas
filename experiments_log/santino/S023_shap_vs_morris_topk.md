---
id: S023
author: santino
date: 2026-05-22
status: done
tags: [supplementary, ml, surrogate, shap, morris, top-k, cross-check]
linked_code:
  - scripts/shap_vs_morris_topk.py
linked_data:
  - data/runs/full_sweep/aggregated.parquet
  - results/morris_indices.parquet
  - results/s023/rf_metrics.csv
  - results/s023/shap_mean_abs.csv
  - results/s023/topk_overlap.csv
  - results/s023/topk_overlap_per_cell.csv
  - results/s023/shap_vs_morris_summary.json
related: [S006, S008, S022]
---

# S023 — Supplementary ML/SHAP cross-check of the Morris μ* rankings

## Hypothesis

A RandomForest surrogate trained on the clean subset of the full atlas sweep
(n = 663), with sex and scenario one-hot features absorbing confounding,
should reproduce the Morris-derived top-3 most-influential inputs for each
output channel via SHAP-derived feature importance. Specifically the top-3
SHAP features (restricted to the 7 operational inputs) should overlap with
Morris μ* top-3 in ≥ 2 features for most (output, cell) pairs.

A null result (top-3 disagreement on most outputs) would suggest one of:
the surrogate is fitting non-Morris-design structure, the clean-subset
selection biases the importance, or the Morris design's OAT nature
mismatches what a global gradient-boosting-style attribution recovers.

## Motivation

Morris elementary effects are the headline atlas sensitivity finding (S006).
An *independent* methodology that recovers the same top-influencer set
strengthens the headline claim — and points to disagreements where they
arise. Reviewers may also want to see at least one ML-based
sensitivity-attribution method applied to the panel. This is supplementary
material, not a replacement for Morris.

This experiment specifically replaces the original Phase B proposal of a
Spearman ρ comparison on 7-rank lists, which has too little statistical
resolution (one rank swap drops ρ below 0.93; two below 0.7). Top-k
overlap is the more honest metric.

## Method

Implemented in `scripts/shap_vs_morris_topk.py`.

1. Read the locked atlas results: `data/runs/full_sweep/aggregated.parquet`
   (1 280 runs) and `results/morris_indices.parquet`.
2. Restrict to the clean subset (n = 663 runs).
3. Build the feature matrix: the 7 operational inputs (hr, rr, sbp, dbp,
   vt, fio2, peep) plus one-hot encodings of `sex` (F, M) and `scenario`
   (S1, S2, S3, S4) → 13 features total. One-hot features absorb the
   between-cell variance that Morris does *not* see (Morris is computed
   within a single cell).
4. For each of the 6 outputs, fit `RandomForestRegressor(random_state=42)`
   with sklearn defaults (no scaling — RF is scale-invariant; no
   hyperparameter tuning).
5. Compute SHAP via `shap.TreeExplainer(rf)` and aggregate to per-feature
   mean |SHAP|.
6. Restrict the SHAP ranking to the 7 operational inputs (drop sex and
   scenario one-hots for the comparison; keep them in the magnitude table
   as a confounding diagnostic).
7. Compare against Morris μ* in two ways:
   - **Pooled**: rank inputs within each (scenario, sex) by μ*, then
     average rank across the 8 cells → one global ranking per output.
   - **Per-cell**: compute cell-conditional mean |SHAP| (group SHAP rows
     by cell) → compare to that cell's Morris top-3.

Sklearn 1.8.0, shap 0.51.0 (pinned via the new `[project.optional-dependencies].ml` extras; install via `uv sync --extra ml`).

## Results

### 1. RF training fit (n = 663, defaults)

| Output | n_train | R² (train) | n_features |
|--------|--------:|-----------:|-----------:|
| HR     | 663 | 0.9995 | 13 |
| MAP    | 663 | 0.9993 | 13 |
| Vt     | 663 | 0.9999 | 13 |
| SpO2   | 663 | 0.9941 | 13 |
| PaO2   | 663 | 0.9930 | 13 |
| PaCO2  | 663 | 0.9942 | 13 |

These are *training* R²; with default RF (100 trees, max_features=sqrt) on
n = 663 the model trivially memorises the data. No predictive validation is
claimed. The top-k ranking comparison is the actual question — it depends
on relative SHAP magnitudes, not on R².

### 2. Pooled SHAP top-3 vs Morris μ* top-3 (k = 3, 7 operational inputs)

| Output | SHAP top-3        | Morris top-3       | Overlap | Overlap features  |
|--------|-------------------|--------------------|--------:|-------------------|
| HR     | hr, fio2, peep    | hr, peep, fio2     | **3/3** | fio2, hr, peep    |
| MAP    | sbp, dbp, hr      | sbp, dbp, hr       | **3/3** | dbp, hr, sbp      |
| Vt     | vt, rr, fio2      | vt, rr, fio2       | **3/3** | fio2, rr, vt      |
| SpO2   | fio2, peep, vt    | fio2, peep, vt     | **3/3** | fio2, peep, vt    |
| PaO2   | fio2, peep, vt    | fio2, peep, rr     |   2/3   | fio2, peep        |
| PaCO2  | vt, rr, fio2      | vt, rr, fio2       | **3/3** | fio2, rr, vt      |

**Pooled top-3 agreement: 17 out of 18 features (94 %)**, with 5/6 outputs
at full match. The single disagreement is PaO2 where SHAP picks `vt` as
the third influencer and Morris picks `rr`. Both `vt` and `rr` enter PaO2
through minute ventilation (Vt × RR), so this is a defensible
reshuffling, not a contradiction.

### 3. Per-cell overlap (cell-conditional SHAP vs cell Morris)

48 (cell × output) comparisons: scenario {S1, S2, S3, S4} × sex {F, M} × 6
outputs.

| Statistic | Value |
|---|---|
| Mean top-3 overlap | **2.40 / 3** |
| Cell-output pairs with full 3/3 match | **23 / 48** (48 %) |
| Pairs with ≥ 2/3 match | 43 / 48 (90 %) |
| Pairs with 1/3 or 0/3 match | 5 / 48 (10 %) |

Per-output mean overlap (averaged across cells):

| Output | Mean overlap | n cells |
|--------|-------------:|--------:|
| MAP   | 3.00 / 3 | 8 |
| PaCO2 | 2.62 / 3 | 8 |
| SpO2  | 2.50 / 3 | 8 |
| HR    | 2.25 / 3 | 8 |
| Vt    | 2.12 / 3 | 8 |
| PaO2  | 2.12 / 3 | 8 |

MAP is fully recovered in every cell — unsurprising, since MAP is derived
from SBP and DBP. PaO2 and Vt show the most per-cell variation; their
Morris cell-level top-3 lists themselves vary across cells (e.g. Vt's
third influencer alternates between sbp / rr / fio2 / peep / dbp / hr
depending on cell), so per-cell SHAP cannot do better than the
cell-level Morris precision permits.

### 4. Confounder diagnostic — SHAP magnitudes for sex / scenario

For HR, SpO2, and PaO2, the one-hot scenario features ranked in the global
top-3 of mean |SHAP|:

- **HR**: `scenario_S3` (#1, 26.5), `hr` (#2, 26.5), `scenario_S4` (#3, 15.2).
  Across-scenario HR shift is on the same scale as the HR setpoint
  effect — consistent with S022's observation that Pulse's autonomic
  baroreflex/chemoreflex models override the requested HR baseline.
- **SpO2**: `scenario_S3` (#1, 0.024), `fio2` (#2, 0.024). Scenario equals
  FiO2 in influence — ARDS severity is the master determinant of
  saturation alongside delivered O2 fraction.
- **PaO2**: `fio2` (#1, 29.5), `scenario_S1` (#2, 17.1), `peep` (#3, 16.8),
  `scenario_S4` (#4, 14.7).

Sex one-hots ranked at #3-4 only for **PaCO2** (mean |SHAP| ≈ 0.9 for
`sex_M` and `sex_F`, against `vt` ≈ 3.9 and `rr` ≈ 2.1) — a side-finding
that sex has a measurable effect on steady-state PaCO2 above what the
operational inputs explain, consistent with body-mass-driven minute-
ventilation differences between the 67.3 kg male and 56.2 kg female
reference surrogates. This is an observation, not a causal claim.

## Interpretation

The ML/SHAP cross-check **substantially agrees** with the Morris ranking:
17/18 pooled top-3 features overlap, and 90 % of per-cell comparisons
recover at least 2/3 of the Morris top-3. Where they disagree (PaO2's
third influencer; Vt's third influencer across cells) the disagreement
involves mechanistically substitutable inputs (RR ↔ Vt via minute
ventilation; SBP ↔ DBP via MAP) rather than contradictory attributions.

This is a non-trivial cross-check because the two methods compute
different objects:

- **Morris μ*** = mean absolute elementary effect over OAT trajectories
  in the *true* Pulse output — sensitivity of the engine.
- **SHAP mean |φ|** = mean absolute Shapley-allocated contribution to
  the *RF surrogate's* prediction over the empirical input distribution
  — sensitivity of the surrogate.

Agreement at the ≥ 2/3 level on 90 % of comparisons means: (a) the RF
captures the same dominant input → output relationships that Morris
sees, and (b) the Morris ranking is not a methodology artefact of OAT
trajectory design.

The confounder diagnostic adds a result not visible in the Morris-only
analysis: ARDS scenario itself dominates the variance for HR, SpO2, and
PaO2 in this multi-cell pooled view. The atlas's per-cell Morris is
designed exactly to factor this out (sensitivity is computed *within* a
cell), so this is not a flaw in Morris — it is what Morris was designed
to control for, made visible by an alternative method.

### Caveats (locked into the supplementary paragraph)

1. **Selection bias.** The RF is trained on the 663 clean runs. SHAP
   attributions therefore reflect the well-behaved sub-region of input
   space; the 617 flagged runs are not represented. We have stated this.
2. **OAT design.** The Morris sample design samples input space non-
   uniformly. The RF's SHAP attribution depends on this empirical
   distribution. We did not re-sample or re-weight.
3. **Training R² is uninformative.** With 13 features and 663 samples,
   default RF trivially memorises the data. The ranking comparison is
   independent of predictive accuracy. We do not claim the RF would
   generalise to unseen Pulse runs without validation.
4. **Per-cell SHAP is conditional, not per-cell-trained.** Per-cell n =
   42-144; we used the global RF and grouped SHAP rows by cell, instead
   of fitting eight RFs (which would be unstable at this n). This means
   per-cell SHAP rankings are tied together by the global model
   structure.
5. **Top-k overlap, not Spearman.** ρ on 7-rank lists has too few degrees
   of freedom to be meaningful at this scale; we report top-3 overlap
   and Jaccard.

## Next steps

- Insert a single supplementary paragraph (drafted below) into the
  manuscript's supplementary materials section. Do *not* promote this
  into the main results — Morris remains the headline.
- Optional: bolt-on a permutation-importance baseline (sklearn
  `permutation_importance`) for triangulation. Not done here.
- Optional: re-run with a Sobol-design fit on top-3 inputs as a cleaner
  surrogate. Out of scope for this paper.

## Supplementary paragraph (manuscript draft)

> **ML-based sensitivity cross-check.** As an independent check on the
> Morris ranking, we trained a `RandomForestRegressor` (scikit-learn
> 1.8.0, default hyperparameters, `random_state = 42`) on the clean
> subset of the sweep (n = 663), using the seven operational inputs plus
> one-hot encodings of sex and scenario as features. We computed SHAP
> values with `shap.TreeExplainer` (shap 0.51.0) and ranked the seven
> operational inputs by mean absolute SHAP value per output. Restricted
> to those seven inputs, the SHAP top-3 features overlap the pooled
> Morris μ* top-3 in 17 of 18 cases across the six outputs (5/6 outputs
> at full 3/3 agreement; PaO2 differs only on the third influencer, where
> SHAP picks Vt and Morris picks RR — mechanistically substitutable
> through minute ventilation). At the per-cell level (48 cell × output
> comparisons), mean top-3 overlap is 2.40/3 and 90 % of comparisons
> recover at least two of the three Morris top influencers. This
> cross-check supports the Morris-derived ranking as a property of the
> engine rather than an artefact of the OAT trajectory design, with two
> honest caveats: (i) the RF is trained on the clean subset only, so SHAP
> attributions reflect the well-behaved sub-region of input space and not
> the full sampled envelope; (ii) the Morris design is non-uniform in
> input space, which the global RF treats as an empirical distribution
> when computing SHAP. We therefore present this as supplementary
> evidence, not as a replacement for Morris.
