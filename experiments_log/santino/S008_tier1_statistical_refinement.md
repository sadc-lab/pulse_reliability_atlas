---
id: S008
author: santino
date: 2026-04-26
status: done
tags: [statistics, bootstrap, null-distribution, mechanism, manuscript-polish, h4]
linked_code:
  - src/analysis_morris.py
  - src/analysis_compare.py
linked_data:
  - results/morris_indices.parquet
  - results/wasserstein_male_vs_female.csv
  - results/spearman_mu_star.csv
supersedes: ""
related: [S006, S007]
---

# S008 — Tier-1 statistical refinement: block bootstrap, within-sex Wasserstein null, divergence mechanism, manuscript polish

## Hypothesis

A self-critical re-read of the manuscript identifies four defensible
weaknesses in the H4 (sex-specific reliability) analysis:

1. The μ\* bootstrap CI uses naive resampling, not block-by-trajectory.
2. The H4 Wasserstein "sex effect" lacks a within-sex null reference,
   so its precision is overstated.
3. The Spearman ρ on length-7 μ\* vectors has wide CI we never compute.
4. The 20-divergence-event sex stratification is reported as an
   observation without a candidate mechanism.

Replacing each weakness with a tighter version should refine — not
overturn — the headline H1 / H3 findings, but may *narrow* H4 from
"M-vs-F differs across all outputs" to a more honest sub-claim about
where sex matters.

## Motivation (why)

The maintainer requested a critical pass on the project before
submission. Limitation list in §A1 – §A7 of that critique identified
the four issues above as fix-before-submission rather than
fix-with-v2. All four can be addressed without new Pulse simulations.

## Method (how)

### Block bootstrap for μ\* CI (`src.analysis_morris`)

Replaced `_bootstrap_mu_star_ci` (naive resample of individual EEs) with
`_block_bootstrap_mu_star_ci` (resample trajectory IDs with replacement;
take all surviving EEs from the chosen trajectories). This preserves
within-trajectory dependence: Morris OAT pairs from the same trajectory
share endpoints and are not independent. The block bootstrap is the
honest Morris geometry. Naive bootstrap kept in the code as
`_bootstrap_mu_star_ci` for completeness; not called.

### Within-sex Wasserstein null (`src.analysis_compare`)

Replaced raw Wasserstein with a paired observed + null computation.
For each (scenario, output): pool the M and F clean-run values, shuffle
the pool, split into halves of the original M and F sizes, compute
Wasserstein on the shuffled split. Repeat n_null = 2,000 times. Report
the empirical p-value (fraction of null distances ≥ observed) plus
null p50 / p95.

Interpretation: a Wasserstein distance that exceeds the within-sex
null p95 cannot be explained by random sub-sampling of the same
population — it indicates a genuine sex-conditional effect.

### Spearman bootstrap CI (`src.analysis_compare`)

Bootstrap the M and F μ\* vectors paired across sexes by resampling
the input axis with replacement (n_bootstrap = 2,000). On length-7
vectors the resulting CIs are wide by construction — that is the
*point* of computing them, since reporting ρ = 0.96 on 7 inputs
without a CI overstates precision.

### Divergence-input mechanism (no code, source audit)

Read the diverged-run input table from
`data/runs/full_sweep/aggregated.parquet`. Searched
`Pulse_engine_adults_Gitlab/engine/src/cpp/engine/human_adult/whole_body/controller/SetupPatient.cpp`
for sex-conditional setup branches. Identified candidate mechanism for
the all-male divergence pattern.

### Manuscript polish

* Filled `§1.1 Motivation` with full prose (no [draft] tags).
* Wrote out `§6 References` with primary-source citations.
* Created `preprint/supplementary.md` with 10 numerical tables
  (S1 – S10).

## What we tried (including dead ends)

* **Initial naive bootstrap (kept as `_bootstrap_mu_star_ci`).** Fine
  for small numbers of EEs but not honest for Morris OAT geometry —
  pretends within-trajectory pairs are independent.
* **Considered explicit BCa (bias-corrected accelerated) bootstrap.**
  Rejected — over-engineering relative to the precision we need;
  percentile bootstrap on a block-resample is sufficient.
* **Considered re-computing μ\* on the full sample (clean and
  flagged) with a censored-data model.** Rejected — out of scope for
  Tier 1; would require a full analysis-method change. Documented in
  manuscript §4.2 as a known limitation.

## Results

### Block bootstrap CI (Morris μ\*)

The new `n_trajectories` column reports how many distinct
trajectories contributed clean EEs to each (cell × output × input).
Block bootstrap CI is **wider** than the previous naive bootstrap by
a small amount on most rows (the naive bootstrap was anti-conservative
because it ignored within-trajectory correlation). All point estimates
unchanged. Bootstrap CI bracket-check from S006 V5 still holds: 0 /
318 violations.

### Within-sex Wasserstein null — major H4 refinement

**Only 6 of 24 (cell × output) Wasserstein distances exceed the
within-sex null p95** (i.e. p_emp ≤ 0.05).

Significant rows (gas-exchange channels, all four scenarios at least
once):

| Scenario | Output | M-vs-F | null p95 | p_emp |
|----------|--------|--------|----------|-------|
| S1       | PaCO2  | 4.69   | 3.56     | 0.009 |
| S2       | SpO2   | 0.012  | 0.011    | 0.022 |
| S2       | PaCO2  | 5.12   | 2.13     | 0.000 |
| S3       | PaCO2  | 2.94   | 1.33     | 0.000 |
| S4       | SpO2   | 0.016  | 0.011    | 0.002 |
| S4       | PaO2   | 4.65   | 3.38     | 0.003 |

Non-significant rows include all HR, MAP, Vt distances across all
four scenarios. **The previously-headlined "Vt sex effect 13 – 36 mL"
is within the within-sex sub-sampling null** at our sample size — the
S3 Vt distance of 36.3 mL has empirical p = 0.129, not significant.

This refines H4 from a global "sex-specific reliability" claim to a
specific sub-claim: **sex effects in Pulse 4.3.1 concentrate on
gas-exchange outputs (PaCO2, SpO2, PaO2). Cardiovascular and
ventilator-output sex differences in our data are not distinguishable
from within-sex sub-sampling.**

This is exactly the kind of overstatement-risk the maintainer flagged
in the critical-review discussion. Before S008, the manuscript was
overconfident about sex effects on Vt and HR; after S008, those claims
are honestly walked back.

### Spearman ρ bootstrap CI

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

The Vt ρ = 0.75 in S2 has CI [-0.06, 1.00] — the input-importance
ranking for Vt is *not* clearly preserved across sex. Other rows have
lower bounds ≥ 0.34 supporting "rankings preserved" qualitatively,
but the CIs are wide because the underlying vector has only 6 – 7
inputs.

### Divergence input signature

Of the 20 diverged runs (all male), **16 share a single Morris-sample
signature repeated across S1 / S2 / S3 / S4_M**: Morris run indices
119, 157, 158, 159 in the canonical sample (seed = 42), corresponding
to:

| in_hr | in_sbp | in_dbp  | in_rr | in_vt | in_fio2 | in_peep |
|-------|--------|---------|-------|-------|---------|---------|
| 50    | 90     | 67.5    | 20    | 800   | 0.737   | 13.3    |
| 50    | 90     | 67.5    | 20    | 300   | 1.000   | 0       |
| 50    | 90     | 67.5    | 20    | 300   | 1.000   | 13.3    |
| 50    | 90     | 67.5    | 20    | 633.3 | 1.000   | 13.3    |

Pattern: **HR = 50 + SBP = 90 + DBP at the constraint boundary + RR
= 20 + (FiO2 = 1.0 OR Vt extreme)**. Plus 4 (S4, M)-only runs at high
HR / low Vt / high PEEP.

The signature reads clinically as "low cardiac output + high
respiratory drive on pure oxygen": a hypotensive, tachypneic, fully
oxygenated patient — recognizable as a septic / pre-arrest
configuration. All inputs are inside Pulse's verified acceptance
ranges.

### Mechanism candidate

`SetupPatient.cpp` line 534 computes blood-volume baseline as
`computedBloodVolume_mL = 65.6 × weight_kg^1.02`. For the Pulse
standard male (67.3 kg) → ≈ 5,060 mL; for the standard female (56.2
kg) → ≈ 4,200 mL. A 20 % blood-volume difference enters the
cardiovascular circuit's stabilization and shifts the operating-point
neighborhood. Other sex-conditional setup parameters: Devine ideal-
body-weight coefficient (50.0 male / 45.5 female), fat fraction
standard (0.21 / 0.28), height bounds (151 – 176 vs 163 – 190 cm).

The 20 % blood-volume difference is the most plausible candidate for
the divergence asymmetry. We do not claim it *is* the mechanism —
confirming would require manipulating only blood-volume baseline
while holding sex flag and other patient parameters constant. We
flag it as a falsifiable hypothesis for follow-up.

### Manuscript additions

* `§1.1` rewritten with full prose covering Pulse's clinical /
  industrial / educational footprint, the FAQ-quoted UQ-gap, and
  the methods-paper framing.
* `§3.5` extended with divergence input signature + mechanism
  candidate (~ 2 paragraphs).
* `§3.6` rewritten in full to cover Wasserstein with within-sex
  null (showing 6 / 24 significant) and Spearman with bootstrap CI
  (with the wide-CI on length-7 vectors honestly disclosed). The
  abstract H4 line is walked back from "supported" to "partially
  supported, gas-exchange only."
* `§6 References` filled out with primary sources and S001 – S008
  internal references.
* `preprint/supplementary.md` new — 10 numerical tables (S1 – S10)
  enumerating ranges, bounds, drift thresholds, flag breakdowns,
  divergence-input signatures, Wasserstein null, Spearman CI, Sobol
  promotion, traffic-light grid, verification points.

## Interpretation

This is a self-correction commit. The atlas's H1 (skewed sensitivity)
and H3 (sex-stratified divergence) findings are robust to the
statistical refinements. The H4 finding has been **honestly walked
back**: where we claimed a global sex-specific reliability effect, the
within-sex null shows the effect is concentrated on gas-exchange
channels and absent from cardiac / ventilator outputs at our sample
size. This is exactly the kind of refinement a careful methods paper
should make *before* submission, not after a reviewer points it out.

The divergence mechanism note converts an observation into a
falsifiable hypothesis (blood-volume scaling). Even if the hypothesis
is wrong, the paper now invites a specific follow-up rather than
leaving "all-male divergence" as an unexplained curiosity.

The supplementary file is an essential reviewer-defence artifact: it
collects every number the manuscript references in one place, with
provenance back to artifacts in `results/`.

## Next steps

* Regenerate figures (Wasserstein + Spearman now have CI / null
  data — figures 4 / 5 should be re-rendered if desired; the existing
  PNGs use point-estimate heatmaps which remain valid but underuse
  the new data).
* Commit + push S008.
* Tier-2 (seed-stability check, continuous ARDS sweep, pytest, CI/CD)
  — defer to maintainer's call; not blocking submission.
