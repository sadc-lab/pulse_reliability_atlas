---
id: S021
author: santino
date: 2026-05-21
status: done
tags: [f-003, hyperoxia, convergence, mechanism-test, classifier-bound, causal-test, reviewer-defense]
linked_code:
  - engine/run_atlas_engine.py
  - src/scenario.py
  - scripts/run_s021_hyperoxia_convergence.py
linked_data:
  - data/runs/full_sweep/aggregated.parquet
  - data/runs/s021_hyperoxia_convergence/
supersedes: ""
related: [S005, S006, S012, S018]
---

# S021 — Hyperoxia convergence: testing the F-003 transient-regime hypothesis

## Hypothesis

The atlas's "F-003" finding — that 34 / 126 implausibly-flagged runs exceed
the locked 600 mmHg PaO2 upper bound, 91 % at FiO2 ≥ 0.95 — admits two
competing interpretations (manuscript §3.8):

(i) **Overshoot interpretation.** Pulse's oxygenation model overshoots
    physiological values at FiO2 ≈ 1.0; the steady-state PaO2 would exceed
    the alveolar-gas-equation prediction (≈ 655 mmHg in a healthy adult at
    sea level with PaCO2 = 38 mmHg, A-a gradient ≈ 10).

(ii) **Transient-regime interpretation.** Pulse's oxygenation is still
     drifting upward at the end of the locked 120 s atlas window. With a
     longer simulation, PaO2 would *plateau* at a physiologically defensible
     value (≤ ~655 mmHg in S1, monotonically lower in S2 / S3 / S4 because
     shunt fraction depresses PaO2).

This experiment commits, **before any S021 Pulse run is observed**, to the
data-driven test that discriminates (i) from (ii) on the same input
combinations that produced the original F-003 flags.

If the data support (ii), the F-003 finding is **not** a Pulse oxygenation
defect; it is a *combination* of (a) the atlas's locked 120 s steady-state
window being insufficient at FiO2 ≥ 0.95, and (b) the atlas's locked
`PaO2_bound_hi = 600 mmHg` being a conservative classifier choice rather
than a physiological impossibility threshold. The manuscript F-003 wording
should then be reframed away from "overshoot" toward "transient hyperoxia
regime + classifier bound artifact."

If the data support (i), the F-003 finding stands as written.

## Motivation

The first round of the manuscript audit (2026-05-21 audit, this session)
showed:

* The alveolar-gas equation `PAO2 = FiO2 · (P_atm − P_H2O) − PaCO2/RQ`
  predicts ≈ 655 mmHg PaO2 at FiO2 = 1.0 in a healthy adult.
* Pulse returns ≈ 606 mmHg PaO2 at FiO2 = 1.0 in S1 — i.e. Pulse already
  *undershoots* alveolar-gas-equation prediction by ≈ 50 mmHg, even before
  the 120 s window completes.
* 93.3 % of FiO2 ≥ 0.95 valid-CSV runs are still rising at end of window
  (positive PaO2 slope over [60, 120] s); 18.5 % exceed the 15 mmHg/60s
  drift threshold.
* Pulse_translation_new E20 ran 9 dedicated Docker runs at FiO2 0.95–1.0
  with a 180 s sim window and observed PaO2 = 629.5 mmHg at FiO2 = 1.0
  (single healthy patient case), consistent with non-convergence in 120 s
  but convergence in 180 s.

S021 is the controlled experiment that elevates this from
opportunistic observation to a pre-registered causal test, with a defined
plateau criterion and scenario-stratified predictions.

## Method

### Selection — paired-by-input across scenarios

The atlas Morris sample is a fixed 160-point design replayed identically in
each (scenario, sex) cell. We pick `run_idx` values that satisfy *all* of:

1. The Morris-sample row has `fio2 = 1.0`.
2. The run has valid CSV (not diverged) in *every* (scenario, sex) cell —
   so the same input combination is reproducible across S1 / S3 / S4 × M / F.

There are 22 such indices in the canonical sample (verified
2026-05-21). We use them as follows:

| Cell | Sample size | Selection |
|------|-------------|-----------|
| S1_F | 22 indices  | all 22 common indices |
| S1_M | 22 indices  | all 22 common indices |
| S3_F |  4 indices  | first 4 common indices (sorted ascending) |
| S3_M |  4 indices  | same 4 indices                            |
| S4_F |  4 indices  | same 4 indices                            |
| S4_M |  4 indices  | same 4 indices                            |

Total: **60 reruns**. S1 is sampled densely because it carries the headline
convergence test (alveolar-eq prediction is sharpest for healthy lungs).
S3 / S4 carry the shunt-depression confirmation.

Selection is deterministic and reproducible via
`scripts/run_s021_hyperoxia_convergence.py::select_subset`.

### Intervention — extended simulation window

Each selected run is rerun with **identical inputs** (HR, SBP, DBP, RR, Vt,
FiO2 = 1.0, PEEP, scenario, sex) but with two atlas defaults overridden:

* `duration_hours = 300 / 3600 ≈ 0.0833` (i.e. 300 s recorded simulation
  instead of the locked 120 s).
* `sample_interval_s = 5` (unchanged; gives 60 sample points across the
  300 s window — plenty for plateau detection).

The 120 s settle phase (`VENT_SETTLE_S` in `run_atlas_engine.py`) is
**not** changed — this preserves comparability with the original sweep's
post-settle trajectory.

### Pre-registered analysis plan

For each S021 run we compute, on the recorded `[0, 300] s` PaO2 trajectory:

* **Plateau value:** `PaO2_plateau_mmHg` = mean PaO2 over `[240, 300] s`
  (last 60 s of the 300 s window — analogous to the original atlas's
  `[60, 120]` steady-state window, scaled to the longer simulation).
* **Plateau drift:** `PaO2_plateau_drift_mmHg_per_60s` = OLS slope of PaO2
  vs time over `[240, 300] s`, multiplied by 60 to express drift per
  minute.

### Pre-registered decision rule

A run is classified **converged** if the plateau drift is below the
preregistered atlas `DRIFT_MAX_DELTA_60S["PaO2"] = 15 mmHg` threshold
(same threshold the locked detector uses; not relaxed for this experiment).

The committed outcome buckets, evaluated on the S1 (M + F) subset
(N = 44 runs):

* **Hypothesis (ii) — transient regime SUPPORTED** if both:
  1. `≥ 75 %` of S1 runs are *converged* (plateau drift < 15 mmHg / 60 s).
  2. Median S1 plateau value is in `[580, 680] mmHg`
     (alveolar-eq prediction ± 75 mmHg; the wide band accommodates
     A-a-gradient variation 0–30 mmHg and PaCO2 variation 30–50 mmHg).
* **Hypothesis (i) — overshoot SUPPORTED** if either:
  1. Median S1 plateau value > 700 mmHg (above alveolar-eq + 45 mmHg
     headroom for A-a uncertainty), OR
  2. `< 25 %` of S1 runs converge AND those that do plateau at > 680 mmHg.
* **Indeterminate** otherwise — declare neither hypothesis confirmed; flag
  for a longer-window follow-up.

Auxiliary shunt-depression check (descriptive, not used for hypothesis
decision):

* On the 4 paired indices, compare median plateau across cells:
  prediction is `S1 > S2 > S3 > S4` (monotonic shunt depression).
* This is reported in the analysis but does *not* gate the
  (i)-vs-(ii) decision.

The thresholds 75 % / 15 mmHg / 580–680 mmHg are committed before any
S021 Pulse run is observed.

### What we are *not* committing to

* No claim that 300 s is the *minimal* window for hyperoxia convergence.
  S021 only tests whether 300 s is *sufficient* for the inputs above.
* No claim about Pulse's behavior at FiO2 between 0.95 and 1.0 — only
  exactly 1.0 is tested.
* No reframing of the atlas's locked `HARD_BOUNDS` table. The 600 mmHg
  classifier bound stays locked; S021 informs a **supplementary**
  `HARD_BOUNDS_PHYSIOLOGICAL` classifier reported as a sensitivity
  analysis.

## Compute budget

60 runs × ~135 s mean wall time (extrapolated from full-sweep median 76 s
for 240 s Pulse-internal at FiO2 = 1.0; S021 is 420 s Pulse-internal,
predicted wall ≈ 76 × 420 / 240 = 133 s) / 2 parallel workers
≈ **67 minutes**. Dispatched in background.

## Expected outputs

`data/runs/s021_hyperoxia_convergence/`:

* `selection.parquet` — 60 selected rows from the original aggregated parquet
* `aggregated.parquet` — one row per `*_long` rerun
* `trajectories.parquet` — long-form `(case_id, time_s, PaO2_mmHg)` for all 60 runs
* `summary.json` — convergence / shunt-depression decision + headline stats
* per-run dirs (`<original_case_id>_long/`)

## Status

**Done — 2026-05-21. Decision: HYPOTHESIS_II_TRANSIENT_REGIME_SUPPORTED
(by very large margins on both criteria).**

## Results

60 / 60 reruns completed cleanly with the locked atlas Docker image.
Mean wall time 130 s / run; 2 parallel workers.

### Headline numbers (`data/runs/s021_hyperoxia_convergence/summary.json`)

| Metric                                  | Value  | Threshold     | Result |
|-----------------------------------------|--------|----------------|--------|
| S1 fraction converged (drift < 15 mmHg / 60 s) | **0.932** | ≥ 0.75 | PASS |
| S1 plateau median (mmHg)                | **643.3** | ∈ [580, 680] | PASS |
| Decision rule                           | both PASS | — | **HYPOTHESIS II SUPPORTED** |

### Per-cell plateau distribution

| Scenario | n  | Plateau median (mmHg) | Plateau IQR (mmHg) | Converged |
|----------|----|------------------------|---------------------|-----------|
| S1_F     | 22 | 660.0 | [631.6, 672.1]      | 20 / 22 (91 %) |
| S1_M     | 22 | 624.2 | [591.1, 646.3]      | 21 / 22 (95 %) |
| S3_F     |  4 | 177.3 | [ 99.9, 259.8]      |  4 /  4 (100 %) |
| S3_M     |  4 | 139.0 | [ 91.5, 190.3]      |  4 /  4 (100 %) |
| S4_F     |  4 |  74.9 | [ 72.6,  77.3]      |  4 /  4 (100 %) |
| S4_M     |  4 |  71.1 | [ 69.5,  72.8]      |  4 /  4 (100 %) |

### Interpretation

1. **F-003 is a transient hyperoxia regime, not an oxygenation overshoot.**
   At FiO2 = 1.0 in S1, the 300 s [240, 300] s plateau lands at
   ~ 643 mmHg — *below* the simple alveolar-gas-equation prediction
   (~ 653 mmHg for PaCO2 ≈ 40, A-a ≈ 10). Pulse under-shoots
   physiology by ~ 10 – 20 mmHg, consistent with a modelled A-a
   gradient. The original 120 s atlas observation (PaO2 > 600 mmHg
   in 31 / 195 FiO2 ≥ 0.95 runs, still drifting upward) was a
   *transient* on the way to this plateau.

2. **Shunt physiology is correctly mapped** (descriptive, not part of
   the (i)-vs-(ii) decision). The same paired-input combinations
   produce PaO2 ≈ 643 mmHg in healthy lungs, ≈ 143 mmHg at 60 %
   ARDS impairment, and ≈ 73 mmHg at 95 % ARDS impairment — an
   order-of-magnitude depression mediated entirely by the ARDS
   severity scalar. This is the expected venous-admixture / shunt
   signature.

3. **Sub-finding — extended-window solver instability tail.**
   6 / 44 S1 runs (14 %) develop unphysical plateaus > 700 mmHg
   under the extended window (4 stabilising near 1,400 mmHg, above
   the sea-level barometric pressure of 760 mmHg). All six share
   the input signature **Vt = 633.3 mL** at FiO2 = 1.0; five of the six
   also carry RR = 20 (V̇E ≈ 12.7 L/min, ~ 2× physiological norm).

   > **Correction, 2026-07-25.** This item originally read “all six
   > share the input signature Vt = 633.3 mL × RR = 20”. That is true of
   > five of the six: S1_F_0150 carries RR = 16 at PEEP = 0
   > (V̇E ≈ 10.1 L/min). Re-derivation from `plateau_stats.parquet`
   > joined to the sweep inputs also shows three runs at V̇E ≈ 12.7 L/min
   > (S1_M_0130/0131/0132) that do *not* run away, so minute
   > ventilation is neither necessary nor sufficient and the
   > “avoid > ~ 12 L/min” guidance derived from it is withdrawn from the
   > paper, the supplement and the monograph. The variable that does
   > separate the cohort is the reference body: across the five
   > input-identical male/female pairs at Vt = 633.3 mL with RR ≥ 16,
   > the female body ran away 5/5 and the male 1/5 (male plateau
   > 779 mmHg vs 1,169 – 1,408 mmHg female). No mechanism is claimed —
   > sex and the 11.1 kg mass difference are not separated in this
   > cohort. The other figures in this item re-derive exactly (6 / 44,
   > 14 %, > 700 mmHg, four near 1,400 mmHg, 760 mmHg). Per-run trajectories
   show a stable ~ 690 mmHg PaO2 through ~ 195 s, then an abrupt
   numerical runaway between 195 s and 220 s, plateauing near
   1,400 mmHg by 240 s, with concurrent unphysical PaCO2 collapse
   to < 17 mmHg. The locked 120 s atlas window protects against
   this regime by stopping the simulation before the runaway; an
   extended-window Pulse user should avoid extreme minute
   ventilation at FiO2 = 1.0 on healthy lungs.

### Supplementary classifier (decoupled from S021 but produced in the
### same session — see `scripts/f003_physiological_reclassification.py`)

The locked atlas classifier uses `HARD_BOUNDS["PaO2"] = (20, 600)` mmHg.
A `HARD_BOUNDS_PHYSIOLOGICAL["PaO2"] = (20, 700)` mmHg bound, anchored
to the alveolar-gas-equation ceiling at sea level (~ 663 mmHg PAO2 +
A-a gradient ⇒ ~ 650 mmHg PaO2), reclassifies **32 of 34** PaO2-flagged
runs as physiologically clean (31 at FiO2 ≥ 0.95; 21 S1_F + 11 S1_M).
The remaining two correspond to the solver-instability-tail signature
above and remain implausible under either bound.

### Pre-flight issues encountered (and resolutions)

None — the script ran clean on the first attempt; the trigger-pressure
sed-patch from S014 was already baked into `pulse-atlas-engine:latest`.

## Next steps

1. Splice the S021 results into manuscript §3.8 (F-003) — done in the
   same session as the experiment.
2. Cross-reference `[S021](#s021)` in abstract / Key Contributions /
   §3.2 / §4.1 / §4.2 / §4.5 (done).
3. Commit S021 + manuscript revision as a single change set with a
   commit message describing the preregistered design and result.
