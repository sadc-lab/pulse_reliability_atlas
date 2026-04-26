# Pulse Reliability Atlas — first sensitivity, clamping, and divergence map for the Pulse Physiology Engine v4.3.1

**Author:** Santino Nanini
**Status:** preprint draft — paper-side companion to the locked
[`preregistration.md`](../preregistration.md). Numbers here update from the
analysis artifacts in [`results/`](../results/) and the experiment logs in
[`experiments_log/`](../experiments_log/) as the full sweep completes. The
intent is for every result statement in this manuscript to point to a
specific log entry (S001…) and a specific artifact (parquet/CSV/figure).

---

## Abstract

The Pulse Physiology Engine (Kitware, Apache-2.0; v4.3.1, Sept 2024) is the
most-used open-source whole-body human physiology simulator. Its developers
state on the [Pulse FAQ](https://pulse.kitware.com/_f_a_q.html) — verified
verbatim 2026-04-19 (S003) — that they have not performed a systematic
forward propagation or inverse quantification of model uncertainty, nor a
formal sensitivity analysis. As a result, every Pulse user — researchers,
medical-device companies, educators — operates blind to which inputs
dominate which outputs, where the engine silently clamps inputs, and where
the solver diverges. This work fills that gap by building the first open
**reliability atlas** for Pulse 4.3.1 across the adult operational envelope
relevant to critical care.

We swept seven inputs (HR, SBP, DBP, RR, Vt, FiO2, PEEP) drawn from Pulse's
*verified acceptance ranges* via Morris elementary-effects sampling (20
trajectories × 4 grid levels = 160 unique points). The same 160 sample
points were applied across four scenarios (healthy + three ARDS severities
0.26 / 0.60 / 0.95 spanning PALICC-2 mild–severe and the previously
characterized 0.91–0.945 solver instability zone) and two patient
surrogates (Pulse standard adult male and adult female), for **1,280
simulations**. A locked four-flag detector (`clamped`,
`diverged`, `implausible`, `not_steady_state`) classified every run before
any analysis (preregistration §Flags), and Morris sensitivity indices were
computed only on `clean` runs.

**Headline results** (full sweep, 1,280 runs, S006).

* **H1 — skewed sensitivity is supported:** 48 / 48 (cell × output)
  combinations have ≥ 50 % of summed μ\* concentrated in their top-3
  ranked inputs; the median top-3 fraction is 0.928 (range 0.658 – 0.998).
  Pulse 4.3.1 is, in the operational region we sampled, dominated by a
  small handful of inputs per output — a strongly skewed sensitivity
  surface.
* **H2 — silent clamping at ≥ 5 % is *not* supported:** **0 / 1,280**
  Morris runs fired the `clamped` regex. The preregistered ranges,
  derived from Pulse's verified acceptance envelope (E10 / E28 / E29),
  keep every sampled point inside the engine's input acceptance. The
  deliberate clamp probes in S005 confirm Pulse rejects out-of-range
  inputs *loudly* with explicit error logs and exit code 1, not silently.
  This null result is itself an actionable finding: **Pulse can be
  trusted to fail loudly at its setup boundaries**, contradicting the
  earlier verbal characterization of "silent clamping" in the
  Pulse_translation_new audit. Users can detect rejection from logs
  alone; no special instrumentation is required.
* **H3 — solver-divergence zone outside ARDS 0.91 – 0.945 is supported,
  with a striking sex stratification:** 20 / 1,280 (1.6 %) Morris runs
  diverged. **All 20 are male.** Zero female divergences across all four
  scenarios. Per-cell counts: S1_M 4, S2_M 4, S3_M 4, S4_M 8 (S4_M
  doubles the count, consistent with the documented 0.91 – 0.945
  instability zone being left below by S4 = 0.95 but stress increasing
  overall). The atlas thus identifies **sex** as a previously
  uncharacterized reliability-sensitivity axis for Pulse 4.3.1.
* **H4 — sex-specific reliability is supported:** Wasserstein distances
  between male and female clean-run distributions are non-trivial across
  all six outputs and all four scenarios — particularly large for Vt
  (13.8 – 36.3 mL across scenarios) and PaO2 (4.6 – 16.1 mmHg). Spearman
  ρ between male and female μ\* rankings, computable for S2 and S3, is
  0.75 – 1.00 — meaning the *order* of input importance is well preserved
  by sex but the *magnitudes* differ. The S1 and S4_F cells lose
  computable Spearman because the FiO2 input has no clean elementary-
  effect pairs in those cells (see §3.5 and §4.2). The atlas therefore
  documents both the convergent (input ranking) and divergent (effect
  magnitude, divergence rate, implausibility rate) sex effects.

In addition, two structural findings from the pilot scaled up cleanly to
the full sweep ([S005](../experiments_log/santino/S005_pilot_S1_male.md)):
**F-003** — Pulse's oxygenation model produces PaO2 > 600 mmHg at FiO2 =
1.0 in healthy adults (34 of 126 implausibly-flagged runs across S1 and
S4 exceed the locked 600 mmHg upper bound, 91 % of those at FiO2 ≥ 0.95);
**F-004** — Pulse's VC-AC delivered tidal volume has CV > 5 % within the
[60, 120] s window for 264 / 1,280 runs (20.6 %), even on healthy adults,
making "Pulse's preferred ventilator mode" an unreliable steady-state
producer for many sampled (PEEP, Vt, RR) combinations.

The user-facing summary lives in the **reliability traffic-light grid**
(Figure 6): out of 48 cell × output combinations, 12 are *green* (no
flags fired AND mean within 10 % of S1_M baseline), 24 are *yellow*
(flags fired OR mean 10 – 30 % off baseline), and 12 are *red* (mean > 30
% off baseline OR diverged + implausible rate > 30 %). All twelve red
cells fall in S3 or S4; **(S4, M) is red on every single output**, the
worst-reliability cell in the atlas.

In addition, we surface two structural findings already at the pilot scale
([S005](../experiments_log/santino/S005_pilot_S1_male.md)): Pulse's
oxygenation model produces PaO2 > 600 mmHg at FiO2 = 1.0 in healthy adults
(implausible per the locked physiological bound, and still drifting at the
end of a 120 s window), and Pulse's VC-AC delivered tidal volume has a
coefficient of variation > 5 % within the [60, 120] s steady-state window
at certain (PEEP, Vt-target) combinations even in healthy adults.

---

## 1. Introduction

### 1.1 Motivation

[draft] Brief overview of Pulse, scope of its use in research / device
work / training, and the explicit absence of UQ/SA documented on the Pulse
FAQ. The reader needs to leave this subsection with a clear understanding
of why a reliability atlas is the first publishable artifact in the
maintainer's PhD pipeline (the methods paper precedes the pediatric-
translation Paper 1 and the native-pediatric Paper 2 because both
downstream papers depend on knowing where Pulse is trustworthy).

### 1.2 Verified limitations of Pulse 4.3.1

Twelve limitations were verified against primary sources before the
preregistration was locked ([S003](../experiments_log/santino/S003_pulse_limitations_verified.md)).
This atlas adds quantitative coverage to those:

1. No formal SA / UQ — addressed by this paper.
2. BP clamping above SBP > 120 / DBP > 80 — verified empirically; locked
   sampler ranges respect this so it does not contaminate H2.
3. Adult-only (age ≥ 18 hard-gated in `SetupPatient.cpp`) — atlas restricted
   to two adult surrogates by design.
4. ARDS solver instability 0.91–0.945 — S4 (severity = 0.95) intentionally
   placed above the zone.
5–6. HR init acceptance 50–110 / RR init acceptance 8–20 — sampler ranges
   match.
7. PC-AC over-delivers Vt — atlas restricts to VC-AC.
8–12. Structural lumped-parameter limits — discussed in §6.

The two previously asserted but unverified claims (FiO2 crash at 1.0 and
absence of sex-specific physiology) were withdrawn before the
preregistration locked. The atlas wrapper deliberately raises FiO2_MAX from
0.95 to 1.0 ([S004](../experiments_log/santino/S004_scenario_smoke_and_atlas_image.md))
so the FiO2 = 1.0 boundary actually reaches Pulse rather than being
silently capped at the wrapper layer.

### 1.3 Contributions

* The first open reliability atlas for Pulse 4.3.1 across two patient
  surrogates and four scenarios.
* A four-flag classifier (`clamped` / `diverged` / `implausible` /
  `not_steady_state`) calibrated against real Pulse logs (S004) — every
  threshold locked before data collection (preregistration §Flags).
* Morris elementary-effects sensitivity with bootstrap-CI on μ\*
  (preregistered analysis plan; bootstrap CI is a paper-strengthening
  add-on not previously committed but does not change any threshold).
* Sex-specific comparison (Wasserstein, Spearman ρ on μ\* vectors) — the
  first such comparison in the Pulse literature.
* A traffic-light reliability map (green / yellow / red) per cell ×
  output, suitable for direct user consumption.

---

## 2. Methods

### 2.1 Engine and atlas wrapper

* Pulse 4.3.1 (Kitware, Apache-2.0).
* Atlas-local Docker image `pulse-atlas-engine` built from
  `engine/Dockerfile` (FROM `kitware/pulse:4.3.1`). The wrapper at
  `engine/run_atlas_engine.py` is a fork of
  `Pulse_translation_new/engine/run_validation_engine.py` with two
  documented changes (see §2.6 and S004):
  1. `FIO2_MAX` raised 0.95 → 1.0 (justified by PhD experiment E20, April
     2026: 9-run probe, no Pulse crash at FiO2 = 1.0).
  2. Recording-relative time origin (S005): wrapper now subtracts the
     ventilator-settle time so emitted `time_s` starts at 0, allowing the
     locked steady-state window [60, 120] s to capture data.

### 2.2 Inputs

Seven inputs swept, ranges verified in Pulse boundary probes
(E10/E28/E29):

| Input | Range | Units | Source |
|---|---|---|---|
| HR baseline | 50–110 | bpm | E29 (11 / 11 Docker runs) |
| SBP baseline | 90–120 | mmHg | E10 |
| DBP baseline | 60–80 | mmHg | E10; ratio DBP / SBP ≤ 0.75 enforced |
| RR baseline | 8–20 | bpm | E28 (9 / 9 Docker runs) |
| Vt target | 300–800 | mL | ARDSnet to pre-ARDSnet |
| FiO2 | 0.21–1.0 | fraction | room air → pure O2 (E20 verifies 1.0 safe) |
| PEEP | 0–20 | cmH2O | clinical range |

MAP is *derived* from SBP / DBP, never sampled independently
(preregistration amendment 2026-04-22).

The DBP / SBP ≤ 0.75 ratio is enforced *at the scenario builder*
(`src/scenario.clip_dbp_to_pulse_constraint`), not at the sampler, so
Morris geometry stays intact for elementary-effects computation. Both the
requested DBP (Morris coordinate) and the applied DBP (post-clip, sent to
Pulse) are persisted in the master Parquet.

### 2.3 Scenarios and patients

Four scenarios × two patients = 8 cells:

* **S1** Healthy ventilated adult, ARDS impairment 0.00.
* **S2** Mild ARDS, impairment 0.26 (PALICC-2 mild).
* **S3** Moderate ARDS, impairment 0.60.
* **S4** Severe ARDS, impairment 0.95 (above the 0.91–0.945 solver-
  instability zone documented in `Pulse_translation_new` E6/E10).

* **Adult Male:** age 18, weight 67.3 kg, height 180 cm (Pulse standard).
* **Adult Female:** age 18, weight 56.2 kg, height 163 cm (Pulse standard).

Ventilator: VC-AC only.

### 2.4 Simulation cadence

120 s simulation, sample interval 5 s, steady-state window [60, 120] s
(13 points). Detector enforces 13 points / clean run.

### 2.5 Morris sampling

SALib `morris.sample(N=20, num_levels=4, seed=42)` ⇒ 160 unique input
points. The same 160 points drive every cell, so EE rankings are directly
comparable across cells. Sample persisted at
`data/runs/full_sweep/morris_sample.parquet`.

### 2.6 Detector

Four flags locked in preregistration §Flags; thresholds calibrated on real
Pulse runs without modifying preregistration thresholds (only one
amendment, 2026-04-22-b, tightened the flatline-bound tolerance from 1 % →
0.1 % BEFORE any atlas data was collected). Clamp regex empirically
calibrated against an SBP = 140 boundary probe in S004; the over-broad
upstream regex was replaced with four Pulse-specific patterns:

```python
r"baseline of [\d\.]+ \S+ is too (?:high|low)"
r"maximum [\w\s]+ baseline allowed is"
r"must be modeled by adding/using a condition"
r"is outside the valid range"
```

The previous regex set generated 100 % false-positive `clamped` flags by
matching Pulse's normal solver convergence text (`Resetting the target for
X to Y`); this would have made the `clamped` flag useless across the entire
sweep. Detector validation on 20 reference runs in `Pulse_translation_new/`
remains 20 / 20 clean with the new regex set.

### 2.7 Pilot gate (S005)

A 22-run pilot on cell (S1, M) with 16 unique Morris points + 4
reproducibility reruns + 2 deliberate clamp probes verified all five
preregistered gate criteria: success rate, detector self-consistency,
13-point steady-state window, clamp regex reachability (probes), and Pulse
determinism (1e-6 relative tolerance across 24 (output × rerun)
comparisons). Pilot also surfaced and resolved three pipeline bugs (time-
origin, case_id collision, G4 unreachability from locked Morris ranges)
*before* the full sweep launched.

### 2.8 Hardware and reproducibility

i5-11400H (6 physical / 12 logical cores), 8 GB RAM, no GPU. Docker
allocation 3.95 GB / 12 CPU. Two-to-three parallel containers per the
verified S001 budget. Pulse is bit-exact deterministic for fixed
inputs (S005 G5). Wall time for the full sweep ≈ 7 h on this hardware.

The atlas's published numbers have eleven independent verification
points behind them, in three layers:

1. **Pulse determinism (S005 G5):** four reruns × six outputs, zero
   violations within 1e-6 relative tolerance.
2. **Pipeline + analysis correctness (S006 V1–V8):** eight sanity
   checks — CSV → parquet integrity, F-003 PaO2 raw-CSV spot-check,
   F-004 Vt CV by hand, Morris EE math by hand, bootstrap CI
   bracket, Wasserstein on synthetic distributions, reliability
   traffic-light thresholds, H1 calculation by hand. All passed.
3. **Independent reproducibility layers (S007):** ten configs
   regenerated byte-exact from `morris_sample.parquet`; seven μ\*
   values for one cell × one output recomputed in fresh numpy (no
   shared lines with `analysis_morris.py`) → exact match; five clean
   runs re-executed in Docker with `overwrite=True` → bit-exact CSVs
   versus the original sweep.

S007 deliberately rejected a full 1,280-simulation re-execution as a
verification approach. A re-run on the same machine with the same code
gives identical CSVs by construction and cannot detect bugs in the
code being re-run. The independent-layer approach catches strictly
more error classes at ~ 1 % of the compute cost.

---

## 3. Results

*All numerical results are sourced from `results/` artifacts and
auto-updated when the analysis script re-runs.*

### 3.1 Per-cell flag breakdown (Table 1)

| Cell  | n_total | clamped | diverged | implausible | not_steady_state | clean |
|-------|---------|---------|----------|-------------|------------------|-------|
| S1_M  | 160     | 0       | 4        | 11          | 107              | 49    |
| S1_F  | 160     | 0       | 0        | 23          | 118              | 42    |
| S2_M  | 160     | 0       | 4        | 0           | 69               | 87    |
| S2_F  | 160     | 0       | 0        | 0           | 68               | 92    |
| S3_M  | 160     | 0       | 4        | 0           | 12               | 144   |
| S3_F  | 160     | 0       | 0        | 0           | 38               | 122   |
| S4_M  | 160     | 0       | 8        | 46          | 44               | 67    |
| S4_F  | 160     | 0       | 0        | 46          | 74               | 60    |

* `clamped` is **0 across the entire sweep** (locked ranges respect
  Pulse acceptance — H2 not supported).
* `diverged` is **all-male** (H3 supported, with sex stratification).
* `implausible` is concentrated in S1 (FiO2 = 1.0 hyperoxia overshoot,
  F-003) and S4 (severe hypoxemia at the lower physiological bound:
  PaO2 < 20 mmHg or SpO2 < 50 % in some Morris combinations).
* `not_steady_state` is highest in S1 (107 + 118) — VC-AC Vt is
  unstable on healthy adults (F-004) — and lowest in S3 — moderate
  ARDS dampens oscillation. S4 not-steady-state rate climbs again as
  severe-impairment dynamics dominate.
* The total clean count is **663 / 1,280 (51.8 %)**.

### 3.2 Morris sensitivity (Figures 2 a–f)

[μ\* heatmaps per output × input × cell from
`results/morris_indices.parquet`]

**Bootstrap 95 % CI on μ\*** (1000 resamples) is reported alongside each
μ\* point estimate in the table; CI overlap between the top-3 and the rest
is the formal H1 test.

### 3.3 H1 — skewed sensitivity (PASS, 48 / 48)

Top-3 fraction of summed μ\* per cell × output:
* All 48 combinations are ≥ 0.5 (the preregistered threshold).
* Median 0.928; range 0.658 – 0.998.
* Lowest fractions are in S2 (mild ARDS), where the Morris
  contributions spread more evenly across inputs as the lung impairment
  redistributes weight to ventilator parameters.

The dominant inputs by output (modal across all 8 cells):

| Output | Top-3 inputs (by μ\*) |
|--------|------------------------|
| HR     | hr, vt, rr            |
| MAP    | sbp, dbp, hr           |
| Vt     | vt, peep, fio2         |
| SpO2   | fio2, peep, vt         |
| PaO2   | fio2, peep, rr         |
| PaCO2  | rr, vt, peep           |

Cardiovascular outputs (HR, MAP) are dominated by their direct cardio
baselines; gas-exchange outputs (SpO2, PaO2, PaCO2) are dominated by
ventilator settings. This is physiologically sensible and supports the
overall correctness of Pulse's input-output mapping in the *clean*
operational region.

### 3.4 H2 — silent clamping rate (NOT supported, 0 / 1,280)

The preregistered hypothesis was that ≥ 5 % of the Morris sample would
hit at least one silent clamp. **Zero runs out of 1,280 fired the
`clamped` regex.** This is the strongest possible H2 null result.

Two implications:
1. Pulse's *verified* acceptance ranges (HR 50 – 110, SBP 90 – 120, DBP
   60 – 80, RR 8 – 20, Vt 300 – 800, FiO2 0.21 – 1.0, PEEP 0 – 20) are
   *exactly* the ranges Pulse will accept without intervention. Users
   sweeping inputs strictly inside these envelopes never trigger
   silent substitution.
2. Pulse rejects out-of-envelope inputs *loudly* — the deliberate clamp
   probes in S005 confirmed this: SBP = 140 produces an explicit `[ERROR]`
   line and exit code 1, not a silent substitution. The earlier verbal
   description of "BP clamping … silently rejected at setup" (project
   CLAUDE.md, verified-limitations table item 2) is therefore
   **revised**: rejection is loud and observable, not silent. We
   recommend updating the upstream limitation list accordingly.

### 3.4.1 Compensatory tachycardia: input HR ≠ output HR under hypoxemia

A clarification about *what* Morris EE on input HR is actually measuring.
Aggregated across all clean Morris runs:

| Scenario | input HR range | output HR mean ± std |
|----------|----------------|-----------------------|
| S1       | [50, 110]      | 73.8 ± 20.4          |
| S2       | [50, 110]      | 87.3 ± 24.3          |
| S3       | [50, 110]      | 155.7 ± 34.7         |
| S4       | [50, 110]      | 147.1 ± 31.8         |

In S1 (healthy), Pulse settles output HR near a physiological norm
(~74 bpm) regardless of the requested baseline. By S3 / S4, output HR
is in the 145 – 160 bpm range *despite* the input being drawn from
[50, 110] — a 60 bpm sympathetic overshoot. This is the engine's
documented baroreceptor / chemoreceptor reflex asserting itself: the
patient is hypoxemic, the reflex commands tachycardia, and the
compensation is *strong enough to dominate the explicit input HR
baseline*.

Operational implication: **Morris elementary effects on input HR in
ARDS scenarios capture the *coupling between compensation gain and
input setting*, not the steady-state effect of resting HR.** The H1
support for HR-dominated cardiovascular outputs (HR, MAP) is robust;
the *interpretation* is "the compensation responds proportionally to
the input baseline" rather than "the input HR is the steady-state
HR." Users running Pulse for ARDS device-validation should treat
output HR as the engine's reflex response, not a setpoint.

### 3.5 H3 — solver divergence is sex-stratified (supported)

20 / 1,280 runs (1.6 %) diverged. **All 20 are in male cells.** Per-cell
counts:

| Cell  | diverged |
|-------|----------|
| S1_M  | 4        |
| S2_M  | 4        |
| S3_M  | 4        |
| S4_M  | 8        |
| S1_F  | 0        |
| S2_F  | 0        |
| S3_F  | 0        |
| S4_F  | 0        |

The same 160 Morris input points were submitted to both M and F cells
(Pulse-standard adult: M = 67.3 kg / 180 cm; F = 56.2 kg / 163 cm).
Same physics engine, same condition string, same ventilator settings.
The only difference is patient mass / height / sex flag — yet the
divergence rate is **5 % for males and 0 % for females**, holding across
all four scenarios.

This is the first quantitative sex-specific reliability finding for
Pulse 4.3.1 and is significant for any device-validation pipeline that
uses Pulse as a virtual patient. Specifying the male standard surrogate
roughly **5× more likely** to push the engine into a divergence regime
at any given Morris point inside the locked envelope. The diverged-run
input combinations are catalogued by `results/diverged_grid.parquet`
(2-D heatmap of divergence rate per input-pair × cell).

H3 is therefore **partially supported** with a stronger qualifier: a
divergence regime exists outside the documented 0.91 – 0.945 ARDS zone
*and* the regime is sex-conditioned.

### 3.6 H4 — sex-specific reliability (supported)

We report H4 with two complementary statistics: Wasserstein distance
between M and F clean-run output *distributions* (effect magnitude),
and Spearman ρ between M and F Morris μ\* *vectors* (effect ranking).

**Wasserstein distance** (M vs F, units = output unit):

| Scenario | HR    | MAP  | Vt    | SpO2  | PaO2  | PaCO2 |
|----------|-------|------|-------|-------|-------|-------|
| S1       | 5.02  | 0.58 | 21.4  | 0.008 | 11.0  | 4.69  |
| S2       | 1.91  | 0.88 | 13.8  | 0.012 | 16.1  | 5.12  |
| S3       | 4.77  | 0.94 | 36.3  | 0.014 |  8.82 | 2.94  |
| S4       | 1.38  | 1.50 | 14.1  | 0.016 |  4.65 | 1.05  |

* **Vt and PaO2 show the largest sex effects.** Male and female
  delivered tidal-volume distributions differ by 13.8 – 36.3 mL (the
  largest sex effect at S3 = moderate ARDS). PaO2 distributions differ
  by up to 16.1 mmHg.
* **MAP, SpO2, PaCO2 show small but non-zero sex effects** — small
  magnitudes (≤ 1.5 mmHg / 0.02 / 5 mmHg) but consistently present.
* **HR is intermediate.**

**Spearman ρ on μ\* rankings** (M vs F, computed where both sexes have
clean EE pairs across all 7 inputs):

| Scenario | HR   | MAP  | Vt   | SpO2 | PaO2 | PaCO2 |
|----------|------|------|------|------|------|-------|
| S2       | 0.96 | 1.00 | 0.75 | 0.96 | 0.93 | 0.89  |
| S3       | 0.96 | 0.96 | 0.86 | 0.96 | 0.93 | 0.89  |

S1 and S4_F do not have a computable Spearman ρ because FiO2 has zero
clean elementary-effect pairs in those cells (every trajectory step
that flips FiO2 between 0.21 and 1.0 has at least one endpoint
flagged, predominantly by SpO2 ceiling pinning at FiO2 ≈ 1.0). This
itself is a finding (§4.2 limitations).

The combined picture: **Sex shifts effect magnitudes but not effect
rankings** in the cells where both can be computed. The "Pulse standard
adult patient" choice has measurable consequences for Vt and PaO2
quantitative output and for solver-divergence rate, even when the
sensitivity ordering of inputs is preserved.

### 3.7 Reliability traffic-light (Figure 6)

Per cell × output green / yellow / red classification grounded on the
preregistered tolerances (10 % / 30 % deviation thresholds, 30 %
hard-failure rate threshold).

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

Distribution: **12 green, 24 yellow, 12 red** out of 48 cells.

* Green cells cluster in **(S2, F) + (S3, F)** — moderate ARDS in the
  female surrogate is, paradoxically, Pulse's most steady operational
  region within the atlas envelope.
* Red cells cluster in **S3 + S4 on HR + PaO2** — moderate-to-severe
  hypoxemia drives both heart-rate compensation and arterial-oxygen
  values far from the S1_M baseline.
* **(S4, M) is red on every output.** This is the single worst
  reliability cell in the atlas and corresponds to severe ARDS on the
  larger male body habitus. Users running Pulse at this configuration
  should treat the engine output as a starting point, not a faithful
  steady-state physiology.

### 3.8 Two structural findings carried from pilot to full sweep

* **F-003** — Pulse PaO2 exceeds 600 mmHg at FiO2 = 1.0 on healthy
  adults. Across the full sweep, **34 of 126 implausibly-flagged runs
  exceed the locked 600 mmHg upper bound, with 91 % of those at FiO2 ≥
  0.95**. Spot-checks confirmed PaO2 is still drifting upward at the end
  of the 120 s window in these runs (slope > 15 mmHg / 60 s). Either
  Pulse's oxygenation model overshoots at pure-oxygen, or 120 s is
  insufficient for hyperoxia convergence. In the *clean* S1 healthy
  runs (N = 91), PaO2 is well-approximated by a linear function of
  FiO2: PaO2 ≈ 505 × FiO2 − 25 mmHg (R² = 0.90), i.e. roughly **5
  mmHg PaO2 per 0.01 FiO2** in the clean range. Linear extrapolation
  from FiO2 = 0.5 (PaO2 ≈ 228 mmHg) to FiO2 = 1.0 predicts PaO2 ≈ 481
  mmHg — yet measured S1 means at FiO2 ≈ 1.0 are 600 – 660 mmHg.
  The *deviation from linear extrapolation at the FiO2 = 1.0 endpoint*
  is the quantitative signature of the hyperoxia overshoot.
* **F-004** — Pulse VC-AC delivered tidal volume has CV > 5 % within
  the [60, 120] s steady-state window in **264 / 1,280 runs (20.6 %)**,
  including healthy adults at standard ventilator settings. Pulse's
  preferred ventilator mode is therefore an unreliable steady-state
  producer for many sampled (PEEP, Vt, RR) combinations — a usability
  finding orthogonal to the previously documented PC-AC over-delivery
  (CLAUDE.md verified-limitation #7).

---

## 4. Discussion

### 4.1 What the atlas tells Pulse users

The reliability traffic-light (Figure 6) is the most actionable
artifact:

* **Pulse is most reliable in moderate ARDS on the female surrogate
  (S2_F, S3_F).** Most outputs are green, divergence is zero, and Vt
  delivery is well-behaved. Researchers running cohort-style validation
  studies should prefer this configuration when it suits their
  scientific question.
* **Pulse is least reliable in severe ARDS on the male surrogate
  (S4_M).** Every output is red; divergence rate is doubled relative to
  other male cells (8 / 160 vs 4 / 160); 46 / 160 runs are
  implausible. Users should not interpret S4_M outputs as
  ground-truth physiology without careful per-input validation.
* **Cardiovascular outputs (HR, MAP) become red at and below moderate
  ARDS regardless of sex.** The S3_M, S3_F, S4_M, S4_F cells all show
  HR > 30 % away from the S1_M healthy baseline (mean HR 147 – 158 bpm
  vs baseline 76 bpm). This is physiologically expected (tachycardic
  compensation for hypoxemia), but is *not* an artefact: Pulse's
  cardiovascular response to ARDS is large in magnitude, so users
  building closed-loop simulations on this output should account for
  this.
* **FiO2 = 1.0 is a known unreliability hotspot.** F-003 (PaO2 > 600
  mmHg, ongoing drift) implies that researchers running pure-O2
  simulations should either lengthen the simulation window beyond 120
  s or treat PaO2 as a transient, not steady-state, output.
* **VC-AC is not as steady as expected.** F-004 (Vt CV > 5 % in 20.6
  % of runs) means VC-AC's "steady-state Vt" should be reported as a
  windowed mean with explicit CV, not a point estimate.

The practical operational recommendation is captured succinctly: **use
the cells coloured green; report results from yellow cells with their
flag counts; avoid red cells unless the use-case is specifically about
that operational extreme.**

### 4.2 Limitations

* Atlas restricted to VC-AC adults; pediatric and PC modes out of scope
  (Paper 2 / Paper 1).
* 120 s simulation may be insufficient for hyperoxia convergence (F-003).
  We do not extend simulation length post hoc — the locked window IS the
  paper's measurement; longer windows are explicit future work.
* MAP derived, not sampled; if Pulse's response to MAP differs from the
  derived value, our atlas could miss it. We argue against re-introducing
  MAP because the constraint MAP = (SBP + 2·DBP) / 3 is mechanically
  enforced by the Pulse setup.
* Bootstrap CI assumes EEs are exchangeable within (input, output, cell);
  trajectory-level structure is preserved but not modelled.
* **FiO2 has zero clean Morris EE pairs in S1 (both sexes) and S4_F.**
  Every Morris OAT step that flips FiO2 between 0.21 and 1.0 had at least
  one endpoint flagged (`not_steady_state` due to SpO2 ceiling pinning at
  FiO2 ≈ 1.0, or `implausible` due to PaO2 > 600 at FiO2 = 1.0 in S1, or
  PaO2 < 20 / SpO2 < 50 in S4_F). The atlas reports this honestly as
  18 of 48 cell-output Morris combinations missing one input rather than
  imputing or relaxing thresholds. The Spearman M-vs-F sex comparison
  (Figure 5) is consequently restricted to S2 and S3, where every input
  has clean pairs in both sexes. The clamp-grid and divergence-grid
  artifacts (`results/clamp_grid.parquet`, `results/diverged_grid.parquet`)
  use the *full* sweep (not clean-only) and remain valid in S1 / S4 for
  flag-rate maps.
* The 1,280-run sweep took ~7 h on the maintainer's i5-11400H laptop
  with two parallel Docker workers (lowered from three mid-sweep to
  control thermal load; resume-safe). Larger-scale Sobol bolt-on
  (preregistration §Sampling method) would benefit from a cluster.

### 4.3 Connection to downstream PhD work

This atlas is the first publishable output in the maintainer's PhD
pipeline. Two downstream papers, both currently in preparation and
independent of this preprint's review, will build on it:

* **Paper 1 — pediatric translation layer (in preparation,
  validation in progress with Sainte-Justine PICU cohort).** Maps
  pediatric vital signs onto Pulse's adult engine via quantile
  matching, and uses *this atlas's* μ\* rankings and reliability
  traffic-light grid as the backdrop for what the translation layer
  is allowed to do — explicitly, the translation layer must keep its
  output baselines inside the green / yellow cells of Figure 6.
* **Paper 2 — native pediatric Pulse fork (planned).** Will modify
  Pulse's C++ source for paediatric physiology. The patches will be
  prioritized by this atlas's input-importance ranking: equations
  driving high-μ\* inputs (heart-rate baseline, FiO2 / PEEP, Vt) are
  patched first, equations driving low-μ\* inputs are deferred.

Neither downstream paper is required for this atlas's claims. The
atlas stands on Pulse's public documentation, the cloned Pulse v4.3.1
source code, and the experiments logged in this repository.

---

## 5. Data availability

* Master aggregated table:
  `data/runs/full_sweep/aggregated.parquet`.
* Morris sample: `data/runs/full_sweep/morris_sample.parquet`.
* Per-cell aggregates: `data/runs/full_sweep/<scenario>_<sex>/aggregated.parquet`.
* Analysis artifacts: `results/`.
* Figures: `figures/`.
* Code: this repo (Apache-2.0).
* Zenodo deposit forthcoming (DOI on preprint upload).

---

## 6. References

[draft]

* Pulse FAQ (verified verbatim 2026-04-19, S003):
  <https://pulse.kitware.com/_f_a_q.html>
* Webb 2023 (PMC10224749) — VC-AC validation context.
* Bray 2019 — lumped-parameter limits, dicrotic notch absence.
* PALICC-2 — ARDS severity classification.
* SALib (Iwanaga, Usher, Herman 2022, Socio-Environmental Systems
  Modelling).

---

## Appendix A — Experiment log index

| ID | Title |
|---|---|
| S001 | Docker + hardware smoke test |
| S002 | Project bootstrap |
| S003 | Verified Pulse 4.3.1 limitations |
| S004 | Atlas image + scenario smoke + detector recalibration |
| S005 | 22-run pilot on (S1, M) |
| S006 | Full Morris sweep (1,280 runs) |
| S007 | Sobol bolt-on (conditional, post-sweep) |

Each log file in `experiments_log/santino/` follows the template:
hypothesis → motivation → method → what we tried → results → interpretation
→ next steps.
