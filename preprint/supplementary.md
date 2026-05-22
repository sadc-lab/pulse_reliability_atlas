# Supplementary materials — Pulse Reliability Atlas

This file collects the numerical tables that support claims in the main
manuscript. All numbers are reproducible from the artifacts in
[`results/`](../results/) and the master table at
[`data/runs/full_sweep/aggregated.parquet`](../data/runs/full_sweep/aggregated.parquet).

---

## S1 — Locked input ranges and provenance

| Input         | Lo    | Hi    | Units    | Source experiment | Locked since |
|---------------|-------|-------|----------|-------------------|--------------|
| HR baseline   | 50    | 110   | bpm      | E29 (11/11 Docker runs) + Pulse `SetupPatient.cpp` line 304 | 2026-04-19 |
| SBP baseline  | 90    | 120   | mmHg     | E10 + `SetupPatient.cpp` (rejection probe SBP=140 → exit 1) | 2026-04-19 |
| DBP baseline  | 60    | 80    | mmHg     | E10; ratio DBP/SBP ≤ 0.75 enforced (clip at submission)       | 2026-04-19 |
| RR baseline   | 8     | 20    | bpm      | E28 (9/9 Docker runs) + `SetupPatient.cpp` line 568          | 2026-04-19 |
| Vt target     | 300   | 800   | mL       | ARDSnet 6 mL/kg → pre-ARDSnet 10 mL/kg @ 67 kg              | preregistered |
| FiO2          | 0.21  | 1.0   | fraction | E20 (9-run probe, no solver-divergence); atlas wrapper raises FIO2_MAX | preregistered |
| PEEP          | 0     | 20    | cmH2O    | clinical practice                                              | preregistered |

---

## S2 — Hard physiological bounds for the `implausible` flag

| Output       | Lower | Upper | Units  | Justification |
|--------------|-------|-------|--------|---------------|
| HR           | 20    | 220   | bpm    | extremes incompatible with life |
| MAP          | 30    | 180   | mmHg   | shock / hypertensive-crisis envelope |
| Vt delivered | 50    | 1500  | mL     | technical range (no-vent / equipment-impossible) |
| SpO2         | 0.50  | 1.00  | frac   | < 0.5 immediately lethal; 1.0 ceiling |
| PaO2         | 20    | 600   | mmHg   | severe hypoxemia floor; pure-O2 ceiling |
| PaCO2        | 10    | 120   | mmHg   | extreme hypocapnia; severe hypercapnia survival floor |

---

## S3 — Drift thresholds for the `not_steady_state` flag (per-variable, 60 s)

| Output       | Max |Δ| over 60 s | Units |
|--------------|--------------------|--------|
| HR           | 5                  | bpm   |
| MAP          | 5                  | mmHg  |
| Vt delivered | 50                 | mL    |
| SpO2         | 0.02               | frac  |
| PaO2         | 15                 | mmHg  |
| PaCO2        | 5                  | mmHg  |

Coefficient-of-variation threshold: 5 % (any output). Flatline-bound
tolerance: 0.1 % of the relevant hard bound (calibrated 2026-04-22-b
on the 20 reference runs in `Pulse_translation_new`, before any atlas
data was collected).

---

## S4 — Per-cell flag breakdown (Table 1 of the main manuscript)

Source: `results/cell_flag_summary.csv`.

| Cell  | n_total | clamped | diverged | implausible | not_steady_state | clean |
|-------|---------|---------|----------|-------------|------------------|-------|
| S1_F  | 160     | 0       | 0        | 23          | 118              | 42    |
| S1_M  | 160     | 0       | 4        | 11          | 107              | 49    |
| S2_F  | 160     | 0       | 0        | 0           | 68               | 92    |
| S2_M  | 160     | 0       | 4        | 0           | 69               | 87    |
| S3_F  | 160     | 0       | 0        | 0           | 38               | 122   |
| S3_M  | 160     | 0       | 4        | 0           | 12               | 144   |
| S4_F  | 160     | 0       | 0        | 46          | 74               | 60    |
| S4_M  | 160     | 0       | 8        | 46          | 44               | 67    |
| **Total** | **1,280** | **0** | **20** | **126** | **530** | **663** |

---

## S5 — Divergence-input signature

The 20 diverged runs cluster on a specific input pattern (16 of 20
share the same Morris-sample signature, repeated across S1/S2/S3 and
into S4_M):

| in_hr | in_sbp | in_dbp  | in_rr | in_vt   | in_fio2 | in_peep | Cells where this run diverged |
|-------|--------|---------|-------|---------|---------|---------|-------------------------------|
| 50    | 90     | 67.5    | 20    | 800     | 0.737   | 13.3    | S1_M, S2_M, S3_M, S4_M        |
| 50    | 90     | 67.5    | 20    | 300     | 1.000   | 0       | S1_M, S2_M, S3_M, S4_M        |
| 50    | 90     | 67.5    | 20    | 300     | 1.000   | 13.3    | S1_M, S2_M, S3_M, S4_M        |
| 50    | 90     | 67.5    | 20    | 633.3   | 1.000   | 13.3    | S1_M, S2_M, S3_M, S4_M        |

Plus 4 additional (S4, M)-only diverging runs:

| in_hr | in_sbp | in_dbp  | in_rr | in_vt   | in_fio2 | in_peep |
|-------|--------|---------|-------|---------|---------|---------|
| 110   | 120    | 80      | 8     | 633.3   | 1.000   | 20      |
| 90    | 100    | 73.3    | 12    | 800     | 0.737   | 13.3    |
| 90    | 100    | 75      | 16    | 300     | 0.737   | 13.3    |
| 90    | 100    | 75      | 16    | 300     | 0.737   | 0       |

**Pattern across all 20:** low cardiovascular pressure / output (HR ≤
50 or SBP ≤ 100) combined with high-FiO2 or extreme-Vt ventilation,
evaluated on the male Pulse standard surrogate.

**All 0 / 20 of these inputs diverge on the female surrogate.**

---

## S6 — H4 Wasserstein with within-sex null reference

Source: `results/wasserstein_male_vs_female.csv`. Within-sex null built
by repeatedly splitting the combined M+F clean-run pool into halves of
the original sizes and computing the distance (n_null = 2,000).

Significant rows under BH-FDR control at q = 0.05 (across all 24
tests) bolded; p_emp ≤ 0.0104 survives the BH-critical threshold for
the 5th-ranked test. The naive α = 0.05 cut would additionally flag
S2 SpO2 (p_emp = 0.022), kept unbolded here for transparency.

| Scenario | Output | M-vs-F  | null p50 | null p95 | p_emp  |
|----------|--------|---------|----------|----------|--------|
| S1       | HR     | 5.018   | 3.913    | 8.556    | 0.305  |
| S1       | MAP    | 0.580   | 1.382    | 2.776    | 0.995  |
| S1       | Vt     | 21.447  | 34.374   | 76.579   | 0.798  |
| S1       | SpO2   | 0.0078  | 0.0045   | 0.0095   | 0.123  |
| S1       | PaO2   | 11.022  | 12.575   | 28.379   | 0.598  |
| S1       | **PaCO2** | **4.690** | 1.646    | 3.562    | **0.009** |
| S2       | HR     | 1.911   | 3.596    | 7.718    | 0.958  |
| S2       | MAP    | 0.879   | 1.029    | 2.114    | 0.652  |
| S2       | Vt     | 13.767  | 25.053   | 55.351   | 0.840  |
| S2       | SpO2   | 0.0125  | 0.0055   | 0.0109   | 0.022  |
| S2       | PaO2   | 16.145  | 8.902    | 17.164   | 0.073  |
| S2       | **PaCO2** | **5.117** | 1.075    | 2.128    | **0.000** |
| S3       | HR     | 4.772   | 3.862    | 8.607    | 0.333  |
| S3       | MAP    | 0.941   | 0.978    | 2.018    | 0.538  |
| S3       | Vt     | 36.257  | 20.816   | 45.852   | 0.129  |
| S3       | SpO2   | 0.0139  | 0.0088   | 0.0170   | 0.119  |
| S3       | PaO2   | 8.824   | 6.567    | 12.764   | 0.245  |
| S3       | **PaCO2** | **2.940** | 0.750    | 1.326    | **0.000** |
| S4       | HR     | 1.380   | 4.731    | 11.180   | 0.953  |
| S4       | MAP    | 1.500   | 1.442    | 2.816    | 0.460  |
| S4       | Vt     | 14.052  | 28.958   | 64.068   | 0.897  |
| S4       | **SpO2** | **0.0162** | 0.0057   | 0.0108   | **0.002** |
| S4       | **PaO2** | **4.649** | 1.914    | 3.377    | **0.003** |
| S4       | PaCO2  | 1.054   | 0.607    | 1.129    | 0.083  |

---

## S7 — H4 Spearman ρ on μ\* with bootstrap CI

Source: `results/spearman_mu_star.csv`. Bootstrap = 2,000 paired-input
resamples; only computable where every input has clean EE pairs in
both sexes.

| Scenario | Output | ρ    | 95 % CI         |
|----------|--------|------|-----------------|
| S2       | HR     | 0.96 | [0.70, 1.00]    |
| S2       | MAP    | 1.00 | [1.00, 1.00]    |
| S2       | Vt     | 0.75 | [-0.06, 1.00]   |
| S2       | SpO2   | 0.96 | [0.70, 1.00]    |
| S2       | PaO2   | 0.93 | [0.41, 1.00]    |
| S2       | PaCO2  | 0.89 | [0.35, 1.00]    |
| S3       | HR     | 0.96 | [0.70, 1.00]    |
| S3       | MAP    | 0.96 | [0.70, 1.00]    |
| S3       | Vt     | 0.86 | [0.34, 1.00]    |
| S3       | SpO2   | 0.96 | [0.70, 1.00]    |
| S3       | PaO2   | 0.93 | [0.41, 1.00]    |
| S3       | PaCO2  | 0.89 | [0.41, 1.00]    |

S1 and S4_F omitted because FiO2 has zero clean elementary-effect
pairs in those cells (see main §4.2 limitations).

---

## S8 — Sobol promotion table (preregistered §Sampling method, deferred)

Source: `results/sobol_promotion.csv`.

72 promote / 55 skip / 17 gray, out of 144 (cell × output × top-3
input) combinations.

| Decision | Count | σ / μ\* threshold |
|----------|-------|-------------------|
| promote  | 72    | ≥ 0.6              |
| gray     | 17    | (0.4, 0.6)         |
| skip     | 55    | ≤ 0.4              |

The full per-(cell × output × input) promotion table lives at
`results/sobol_promotion.csv`. Sobol bolt-on is preregistered as
optional and is deferred to a follow-up paper or to a reviewer-
requested addendum (estimated cost: ~ 3,600 additional Pulse runs,
~ 13 h compute).

---

## S9 — Reliability traffic light grid (Figure 6 of the main manuscript)

Source: `results/reliability_classification.csv`.

| Cell  | HR     | MAP    | Vt     | SpO2   | PaO2   | PaCO2  |
|-------|--------|--------|--------|--------|--------|--------|
| S1_F  | yellow | yellow | yellow | yellow | yellow | yellow |
| S1_M  | yellow | yellow | yellow | yellow | yellow | yellow |
| S2_F  | yellow | green  | green  | green  | yellow | green  |
| S2_M  | yellow | yellow | yellow | yellow | yellow | yellow |
| S3_F  | red    | yellow | green  | green  | red    | green  |
| S3_M  | red    | yellow | yellow | yellow | red    | yellow |
| S4_F  | red    | yellow | yellow | yellow | red    | yellow |
| S4_M  | red    | red    | red    | red    | red    | red    |

Distribution: 7 green, 29 yellow, 12 red.

---

## S10 — Verification points (eleven independent layers)

| ID  | Layer | Method | Result |
|-----|-------|--------|--------|
| S005 G5 | Pulse determinism | 4 reruns × 6 outputs vs source | 0 / 24 violations within 1e-6 |
| S006 V1 | CSV → parquet integrity | 3 random runs, recompute mean by hand | 3 / 3 exact |
| S006 V2 | F-003 PaO2 raw-CSV spot | 3 implausible runs read directly | 3 / 3 confirmed |
| S006 V3 | F-004 Vt CV by hand | 3 runs, recompute CV | 3 / 3 exact |
| S006 V4 | Morris EE math by hand | 1 trajectory step | exact match |
| S006 V5 | Bootstrap CI bracket | all 318 rows | 0 / 318 violations |
| S006 V6 | Wasserstein synthetic | N(0,1) vs N(5,1) | 5.06 vs expected 5.0 |
| S006 V7 | Reliability thresholds | 5 spot checks | 5 / 5 match formula |
| S006 V8 | H1 calculation by hand | (S1, M, HR) | 0.9467 = parquet 0.9467 |
| S007 1  | Config regeneration | 10 random configs, byte-compare | 10 / 10 byte-exact |
| S007 2  | Independent numpy μ\* | (S2, M, HR) re-derived in raw numpy | 7 / 7 inputs exact |
| S007 3  | Docker re-execution | 5 random clean runs, re-run | 5 / 5 bit-exact |

11 independent verification points; 0 failures across all of them.

---

## S11 — ML/SHAP cross-check of Morris μ\* rankings (S023)

As an independent check on the Morris ranking reported in §3.2 and
Figures 2 a–f of the main manuscript, we trained one
`RandomForestRegressor` per output channel (`scikit-learn` 1.8.0,
default hyperparameters, `random_state = 42`, no input scaling) on the
clean subset of the sweep (n = 663). The feature matrix combined the
seven operational inputs (HR, RR, SBP, DBP, Vt, FiO2, PEEP) with
one-hot encodings of `sex` and `scenario`, for 13 features total.
The one-hot features were included to absorb between-cell confounding
that Morris does *not* see — Morris is computed *within* a cell, so
sex and ARDS scenario are not part of its 7-input ranking. SHAP values
were computed via `shap.TreeExplainer` (shap 0.51.0) and aggregated to
per-feature mean absolute SHAP. For comparison with Morris, the SHAP
ranking was restricted to the seven operational inputs (the sex /
scenario one-hots are reported separately as a confounding diagnostic
in [`results/s023/shap_mean_abs.csv`](../results/s023/shap_mean_abs.csv)).

Headline metric: **top-3 overlap**. With seven inputs the Spearman ρ
on the full 7-element ranking has too few degrees of freedom to give a
useful signal (two rank swaps drop ρ below 0.7), so we report top-3
overlap and Jaccard. Source code:
[`scripts/shap_vs_morris_topk.py`](../scripts/shap_vs_morris_topk.py).
Full per-cell artefacts:
[`results/s023/topk_overlap.csv`](../results/s023/topk_overlap.csv) and
[`results/s023/topk_overlap_per_cell.csv`](../results/s023/topk_overlap_per_cell.csv).

### S11.1 — Pooled SHAP vs Morris μ\* top-3 (per output)

Morris pooled ranking = mean-rank-of-μ\* across the 8 cells per input.

| Output | SHAP top-3       | Morris top-3       | Overlap | Overlap features |
|--------|------------------|--------------------|--------:|------------------|
| HR     | hr, fio2, peep   | hr, peep, fio2     | **3 / 3** | fio2, hr, peep |
| MAP    | sbp, dbp, hr     | sbp, dbp, hr       | **3 / 3** | dbp, hr, sbp   |
| Vt     | vt, rr, fio2     | vt, rr, fio2       | **3 / 3** | fio2, rr, vt   |
| SpO2   | fio2, peep, vt   | fio2, peep, vt     | **3 / 3** | fio2, peep, vt |
| PaO2   | fio2, peep, vt   | fio2, peep, rr     |   2 / 3   | fio2, peep     |
| PaCO2  | vt, rr, fio2     | vt, rr, fio2       | **3 / 3** | fio2, rr, vt   |

**Pooled top-3 agreement = 17 / 18 features (94 %)**, with 5 / 6
outputs at full match. The single disagreement (PaO2's third
influencer) is `vt` (SHAP) vs `rr` (Morris); both enter PaO2 through
minute ventilation Vt × RR, so the disagreement is a defensible
reshuffling rather than a contradiction.

### S11.2 — Per-cell overlap (48 comparisons)

Per-cell SHAP rankings were obtained by grouping the global RF's SHAP
rows by `(scenario, sex)` and computing the cell-conditional mean
|SHAP|. This is *not* the same as fitting eight per-cell RFs — at
n = 42–144 clean runs per cell, default-RF training is unstable.

| Statistic                                       | Value  |
|-------------------------------------------------|--------|
| Mean top-3 overlap                              | **2.40 / 3** |
| Cell-output pairs with full 3 / 3 match         | **23 / 48** (48 %) |
| Pairs with ≥ 2 / 3 match                        | 43 / 48 (90 %) |
| Pairs with 1 / 3 or 0 / 3 match                 | 5 / 48 (10 %) |

Per-output mean overlap (averaged across cells):

| Output | Mean overlap | n cells |
|--------|-------------:|--------:|
| MAP    | 3.00 / 3 | 8 |
| PaCO2  | 2.62 / 3 | 8 |
| SpO2   | 2.50 / 3 | 8 |
| HR     | 2.25 / 3 | 8 |
| Vt     | 2.12 / 3 | 8 |
| PaO2   | 2.12 / 3 | 8 |

### S11.3 — Confounder diagnostic (sex / scenario SHAP magnitudes)

For HR, SpO2, and PaO2, ARDS scenario one-hots rank in the global
top-3 of mean |SHAP| (above several of the operational inputs); for
PaCO2, the sex one-hots rank #3 / #4 with mean |SHAP| ≈ 0.9 against
`vt` ≈ 3.9 and `rr` ≈ 2.1 — consistent with the ~ 11 kg body-mass
difference between the 67.3 kg male and 56.2 kg female reference
surrogates producing measurable minute-ventilation differences. These
between-cell effects are *exactly what Morris controls for* by
computing sensitivity per cell, so their visibility in the SHAP
ranking is not a flaw in Morris but a confirmation that ARDS scenario
and body mass are real sources of variance once the per-cell stratum
is collapsed.

### S11.4 — Honest caveats

1. **Selection bias.** The RF is trained on the 663 clean runs.
   SHAP attributions reflect the well-behaved sub-region of input
   space; the 617 flagged runs are not represented.
2. **Sampling design.** Morris elementary-effect trajectories sample
   input space non-uniformly (OAT). SHAP attributions on a model
   fitted to this non-uniform empirical distribution inherit that
   distribution. We did not re-sample or re-weight.
3. **Training R² is uninformative.** With 13 features and 663
   samples, default RF (100 trees, max_features = sqrt) trivially
   memorises the data (training R² ≥ 0.993 for all six outputs).
   The top-3 ranking comparison is independent of predictive
   accuracy. We make no claim that this RF would generalise to
   unseen Pulse runs.
4. **Per-cell SHAP is conditional, not per-cell trained.** Per-cell
   n = 42–144; we used the global RF and grouped SHAP rows by cell
   rather than fitting eight per-cell RFs. Cell-conditional SHAP
   rankings are therefore tied together by the global model
   structure.
5. **Top-k overlap, not Spearman ρ.** With seven inputs ρ on the
   full ranking has insufficient statistical resolution; we report
   top-3 overlap and Jaccard.

**Interpretation.** Top-3 agreement at 17 / 18 pooled and ≥ 2 / 3 in
90 % of per-cell comparisons supports the Morris ranking as a
property of the engine rather than an artefact of the OAT trajectory
design. We present this as a supplementary cross-check, not as a
replacement for Morris. Full protocol and per-run paired data:
[`experiments_log/santino/S023_shap_vs_morris_topk.md`](../experiments_log/santino/S023_shap_vs_morris_topk.md);
raw artefacts in
[`results/s023/`](../results/s023/).
