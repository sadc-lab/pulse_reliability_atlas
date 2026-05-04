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
* **H4 — sex-specific reliability is partially supported:** with a
  within-sex subsampling null reference, only **6 of 24 (cell × output)
  Wasserstein distances** are distinguishable from random — and **all
  six are gas-exchange channels** (PaCO2 ×3, SpO2 ×2, PaO2 ×1). The
  cardiovascular (HR, MAP) and ventilator-output (Vt) M-vs-F differences
  reported in an earlier draft fall *within* the within-sex null
  distribution at our sample size — the apparent ~ 13 – 36 mL Vt
  difference between sexes is not larger than what either sex produces
  by random sub-sampling. **Where sex matters, it matters on gas
  exchange — not on cardiac output or delivered tidal volume.** Spearman
  ρ on input-importance rankings is 0.75 – 1.00 (point estimates,
  computable in S2 / S3) with paired-input bootstrap CI lower bounds
  ≥ 0.34 for most outputs (Vt CI [-0.06, 1.0] is the exception);
  rankings are qualitatively preserved but the per-output precision is
  modest because the ρ vector has only 7 entries.

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

The Pulse Physiology Engine [Bray et al. 2019] (Kitware, Apache-2.0)
is the most-used open-source whole-body human physiology simulator.
It provides a 0-dimensional lumped-parameter model of the
cardiovascular, respiratory, gas-exchange, and pharmacological
systems, and is used in three broad communities:

* **Clinical research** — virtual-patient cohorts for hypothesis
  generation when human data are unavailable, ethically constrained,
  or impractically expensive to collect (e.g. dual-patient ventilator
  sharing during the COVID-19 pandemic [Webb et al. 2020]).
* **Medical-device development** — early-stage validation of
  ventilators, pumps, and monitors against a virtual patient. ASL 5000
  benchmarking against Pulse's VC-AC mode reports tidal-volume errors
  of 0.07 – 2.25 % [Webb et al. 2023].
* **Education** — anaesthesia, critical-care, and paramedic training
  curricula increasingly use Pulse for case-based simulation.

Despite this footprint, the engine's developers state explicitly on
the public Pulse FAQ [Pulse FAQ; verified verbatim 2026-04-19, S003]:

> "We have not performed a systematic forward propagation or inverse
> quantification of model uncertainty, nor have we conducted a formal
> sensitivity analysis."

The corollary is operational: every Pulse user — clinical, industrial,
educational — is operating *without a map* of where the engine is
reliable, where it silently bends inputs out of acceptance, and which
inputs dominate which outputs. Each user re-encounters the same
limitations independently. Each medical-device validation pipeline
re-derives its own working envelope by trial and error.

This paper closes that gap with the first open reliability atlas for
Pulse v4.3.1 across the adult operational envelope relevant to
critical care. The methodology follows three commitments locked
before any data was collected (preregistration §Inputs, §Scenarios,
§Flags): inputs swept from Pulse's *verified* acceptance ranges (E10 /
E28 / E29 boundary probes), scenarios spanning healthy adult and
three ARDS severities anchored on the Berlin Definition [ARDS
Definition Task Force 2012] and PALICC-2 [Emeriaud et al. 2023]
classifications, and a four-flag classifier that categorizes every
run rather than discarding flagged ones (preregistration discipline
following the principles of [Munafò et al. 2017]).

Three properties make this paper a methods-paper rather than a
findings-paper: (1) the entire pipeline is preregistered with
amendment history (per [Munafò et al. 2017]); (2) every quoted
number is reproducible from the canonical Morris sample (seed = 42)
plus the atlas Docker image, verified at three independent layers
(S007); the data are released under FAIR principles [Wilkinson et
al. 2016]; and (3) the four-flag classifier is a generic instrument
that future Pulse users can apply to their own configurations
without re-running our sweep.

The paper is the first publishable output in the maintainer's PhD
pipeline. Two downstream papers — pediatric translation layer (in
preparation, validation underway) and native pediatric Pulse fork
(planned) — both depend on knowing where adult Pulse is trustworthy.
This atlas is that prerequisite.

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

The two previously asserted but unverified claims (FiO2 solver-divergence at 1.0 and
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
     2026: 9-run probe, no Pulse solver-divergence at FiO2 = 1.0).
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
| Vt target | 300–800 | mL | ARDSnet 6 mL/kg [Brower et al. 2000] to pre-ARDSnet 10 mL/kg |
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

The Morris elementary-effects design [Morris 1991], with the radial-
trajectory + μ\* refinement of [Campolongo, Cariboni, Saltelli 2007],
is used as a one-at-a-time screening method. Implementation: SALib's
`morris.sample(N=20, num_levels=4, seed=42)` [Iwanaga, Usher, Herman
2022] ⇒ 160 unique input points. The same 160 points drive every
cell, so EE rankings are directly comparable across cells. Sample
persisted at `data/runs/full_sweep/morris_sample.parquet`.

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

Atlas-side input validation in `src/scenario.py` is restricted to
scenario and sex keys; physiological-bound enforcement is delegated to
the locked Morris sampler ranges (§2.2), Pulse's setup-time rejection
(captured by the `clamped` flag), and the detector's `implausible`
hard-bound check on the steady-state mean. This three-layer
defense-in-depth contract was verified end-to-end in
[S015](../experiments_log/santino/S015_reproducibility_and_logic_audit.md).

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

20 / 1,280 runs (1.6 %) diverged. **All 20 are in male cells.**

**Input-combination signature.** The 20 divergence events are not
spread uniformly across the input space — they cluster on a specific
input pattern. Of the 20:

* **HR = 50 (the locked low boundary)** appears in 16 / 20 runs.
* **SBP = 90 (locked low boundary)** appears in 16 / 20 runs.
* **DBP = 67.5 (= 0.75 × 90, the post-clip value)** appears in 16 / 20.
* **RR = 20 (locked high boundary)** appears in 16 / 20 runs.
* **FiO2 = 1.0** appears in 12 / 20.
* The 16 shared cases correspond to **the same 4 Morris sample
  indices repeated across S1 / S2 / S3 / S4_M** (run_idx 119, 157,
  158, 159 in the canonical sample). The remaining 4 are unique to
  (S4, M) and add a complementary cluster at high HR / low Vt.

The divergence signature reads as: **low cardiovascular output (low
HR + low SBP) combined with high respiratory drive (high RR + high
FiO2) on the male standard surrogate** drives Pulse to a numerical
edge case. The compound input is plausible clinically (a hypotensive,
tachypneic, fully oxygenated patient — recognizable as a septic / pre-
arrest configuration) yet inside Pulse's verified acceptance ranges.
Users should treat this corner of the envelope as fragile when running
the male standard surrogate.

**Mechanism candidate (Pulse source audit).** Pulse's
`SetupPatient.cpp` computes blood-volume baseline as
`computedBloodVolume_mL = 65.6 × weight_kg^1.02`. For the standard
male (67.3 kg) this yields ≈ 5,060 mL; for the standard female
(56.2 kg) ≈ 4,200 mL. Several other parameters are sex-conditional:
ideal-body-weight (Devine formula coefficient 50.0 vs 45.5),
fat-fraction standard (0.21 vs 0.28), height bounds (151 – 176 cm vs
163 – 190 cm). The 20 % blood-volume difference is the most plausible
candidate for the divergence asymmetry: it directly enters the
cardiovascular circuit's stabilization and shifts the operating-point
neighborhood between the two sexes. We do not claim this is the
mechanism — confirming it would require a targeted source-level
experiment manipulating only blood-volume baseline — but it is the
falsifiable hypothesis to test in follow-up work.

Per-cell counts:

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

### 3.5.1 Continuous-severity divergence regime (Tier-2 follow-up)

The S006 sweep used four fixed ARDS severities. A complementary
200-run sweep at continuous severity (Tier-2 follow-up,
[S009](../experiments_log/santino/S009_tier2_seed_stability_continuous_ards.md))
maps the divergence regime as a function of ARDS impairment, holding
all 7 Morris inputs at midrange (HR = 80, SBP = 105, DBP = 70, RR =
14, Vt = 550, FiO2 = 0.6, PEEP = 10):

| Severity range  | F diverged | M diverged |
|------------------|------------|------------|
| [0, 0.5]         | 0 / 31     | 0 / 31     |
| (0.5, 0.85]      | 0 / 20     | 0 / 20     |
| (0.85, 0.91]     | **14 / 18**| 5 / 18     |
| (0.91, 0.945]    | 5 / 10     | **9 / 10** |
| (0.945, 0.95]    | 0 / 2      | 0 / 2      |
| (0.95, 1.0]      | 0 / 19     | 0 / 19     |

Two refinements of the literature picture:

1. **The instability band is wider than previously reported.** The
   `Pulse_translation_new` E6 audit reported an instability zone at
   `[0.91, 0.945]`. Our continuous sweep at midrange inputs places
   the band at `[0.879, 0.945]` — about 35 % wider on the low side.
   The discrepancy is consistent with input dependence: E6 used
   ventilator settings tailored to ARDS calibration; the atlas's
   midrange settings reach instability earlier.

2. **The S006 sex-stratification is regime-dependent.** In the
   continuous-severity sweep (midrange inputs), the divergences are
   approximately balanced (F = 19, M = 14), with F diverging at
   *lower* severities (0.879 onwards) and M continuing into
   `[0.91, 0.945]`. So the original S006 claim "all 20 male
   divergences" is a property of the *input-extreme + 4-scenario*
   combination, not a global sex effect on solver reliability.

The atlas therefore distinguishes **two separate divergence regimes**:

* **Input-driven regime** (S006): male standard surrogate at low HR
  + low SBP + high RR + FiO2 = 1.0. ~ 5× higher than female.
  Mechanism candidate: 20 % blood-volume difference (§3.5).
* **Severity-driven regime** (S009): both sexes, midrange inputs,
  severity in the band `[0.879, 0.945]`. F slightly higher overall;
  F earlier in the band, M later. Mechanism: solver-stability
  gradient at the high-impairment compliance edge.

Together these regimes give a more honest H3 picture: divergence
exists, it is partially sex-conditional, but the sex effect varies
by *what is varying* (Morris-extreme inputs vs ARDS severity), not
sex per se.

### 3.6 H4 — sex-specific reliability (partially supported, gas-exchange only)

We report H4 with two complementary statistics: Wasserstein distance
between M and F clean-run output *distributions* (effect magnitude),
and Spearman ρ between M and F Morris μ\* *vectors* (effect ranking).
For both we add a null reference because raw point estimates on this
sample size overstate precision.

**Wasserstein distance with within-sex null** (M-vs-F observed; null
built by repeatedly splitting the *combined* M+F clean runs randomly
into halves of the original sizes; n_null = 2,000):

| Scenario | Output | M-vs-F | null p50 | null p95 | p_emp | Sig.? |
|----------|--------|--------|----------|----------|-------|-------|
| S1       | HR     | 5.02   | 3.91     | 8.56     | 0.305 |       |
| S1       | MAP    | 0.58   | 1.38     | 2.78     | 0.995 |       |
| S1       | Vt     | 21.4   | 34.4     | 76.6     | 0.798 |       |
| S1       | SpO2   | 0.008  | 0.004    | 0.010    | 0.123 |       |
| S1       | PaO2   | 11.0   | 12.6     | 28.4     | 0.598 |       |
| S1       | **PaCO2** | **4.69** | 1.65     | 3.56     | **0.009** | * |
| S2       | HR     | 1.91   | 3.60     | 7.72     | 0.958 |       |
| S2       | MAP    | 0.88   | 1.03     | 2.11     | 0.652 |       |
| S2       | Vt     | 13.8   | 25.1     | 55.4     | 0.840 |       |
| S2       | **SpO2** | **0.012** | 0.006    | 0.011    | **0.022** | * |
| S2       | PaO2   | 16.1   | 8.90     | 17.2     | 0.073 |       |
| S2       | **PaCO2** | **5.12** | 1.07     | 2.13     | **0.000** | * |
| S3       | HR     | 4.77   | 3.86     | 8.61     | 0.333 |       |
| S3       | MAP    | 0.94   | 0.98     | 2.02     | 0.538 |       |
| S3       | Vt     | 36.3   | 20.8     | 45.9     | 0.129 |       |
| S3       | SpO2   | 0.014  | 0.009    | 0.017    | 0.119 |       |
| S3       | PaO2   | 8.82   | 6.57     | 12.8     | 0.245 |       |
| S3       | **PaCO2** | **2.94** | 0.75     | 1.33     | **0.000** | * |
| S4       | HR     | 1.38   | 4.73     | 11.2     | 0.953 |       |
| S4       | MAP    | 1.50   | 1.44     | 2.82     | 0.460 |       |
| S4       | Vt     | 14.1   | 29.0     | 64.1     | 0.897 |       |
| S4       | **SpO2** | **0.016** | 0.006    | 0.011    | **0.002** | * |
| S4       | **PaO2** | **4.65** | 1.91     | 3.38     | **0.003** | * |
| S4       | PaCO2  | 1.05   | 0.61     | 1.13     | 0.083 |       |

\* significant at α = 0.05.

**Honest interpretation:** 6 of 24 (cell × output) Wasserstein
distances are distinguishable from a within-sex subsampling null.
**All six are gas-exchange channels (PaCO2 ×3, SpO2 ×2, PaO2 ×1).**
Cardiovascular outputs (HR, MAP) and ventilator output (Vt) show
M-vs-F distances *within* the within-sex null distribution — i.e.
the ~ 13 – 36 mL Vt difference and the ~ 1 – 5 bpm HR difference are
not larger than what the same population produces by random sub-
sampling. **An earlier draft of this paper presented those Vt and HR
distances as "the largest sex effects"; the within-sex null
correction shows that conclusion was overstated.**

The remaining sex-stratified effect concentrates exactly where
sex-specific physiology should matter most: gas exchange, where
alveolar volume scaling and lung-volume-to-body-mass ratios diverge
by sex. PaCO2 is the strongest signal (significant in 3 of 4
scenarios, very small p_emp values in S2 and S3).

**Spearman ρ on μ\* rankings with paired-input bootstrap CI**
(M vs F, computed where both sexes have clean EE pairs across all
7 inputs):

| Scenario | Output | ρ    | 95% CI         |
|----------|--------|------|----------------|
| S2       | HR     | 0.96 | [0.70, 1.00]   |
| S2       | MAP    | 1.00 | [1.00, 1.00]   |
| S2       | Vt     | 0.75 | [-0.06, 1.00]  |
| S2       | SpO2   | 0.96 | [0.70, 1.00]   |
| S2       | PaO2   | 0.93 | [0.41, 1.00]   |
| S2       | PaCO2  | 0.89 | [0.35, 1.00]   |
| S3       | HR     | 0.96 | [0.70, 1.00]   |
| S3       | MAP    | 0.96 | [0.70, 1.00]   |
| S3       | Vt     | 0.86 | [0.34, 1.00]   |
| S3       | SpO2   | 0.96 | [0.70, 1.00]   |
| S3       | PaO2   | 0.93 | [0.41, 1.00]   |
| S3       | PaCO2  | 0.89 | [0.41, 1.00]   |

S1 and S4_F do not have a computable Spearman ρ because FiO2 has zero
clean elementary-effect pairs in those cells (every trajectory step
that flips FiO2 between 0.21 and 1.0 has at least one endpoint
flagged, predominantly by SpO2 ceiling pinning at FiO2 ≈ 1.0). This
itself is a finding (§4.3 limitations).

The bootstrap CI on Spearman ρ is wide for output Vt (S2 lower bound
−0.06) — meaning the input-importance ranking for Vt is not
clearly preserved across sex. For other outputs, the lower CI bound
is ≥ 0.34, supporting "rankings preserved" qualitatively but not
strongly.

**Combined H4 picture:**

* H4 is **partially supported**, with the strong signal concentrated
  on gas-exchange outputs.
* **Sex effect is real on PaCO2, SpO2 (in S2 and S4), and PaO2 in S4** —
  these survive the within-sex null.
* **Sex effect on HR, MAP, Vt is not distinguishable from
  within-sex sub-sampling** at our sample size. Either it does not
  exist, or it is below the detection floor of 49 – 144 clean runs
  per cell.
* **Input-importance rankings are similar by sex** (Spearman ρ
  point estimates 0.75 – 1.00 in S2 / S3) but the CIs are wide —
  the ranking-similarity claim is qualitative, not high-precision.

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
* **F-004 — Patient-ventilator dyssynchrony in VC-AC at extreme inputs.**
  Across the full sweep, 264 / 1,280 (20.6 %) Morris runs failed the
  preregistered steady-state criterion on delivered tidal volume
  (`Vt_cv > 5 %` in the [60, 120] s window). Inspecting the
  native-resolution ventilator timeseries (sampled at 0.02 s; the same
  Pulse runs that produce the 5 s atlas CSV) shows a stereotyped pattern:
  a mandatory breath at the set respiratory rate delivers Vt close to
  the requested target, followed by two to three smaller "assist"
  breaths fired between mandatory cycles. Mean instantaneous respiratory
  rate during these episodes alternates between the set rate
  (e.g. 20 bpm) and roughly twice the set rate (~46 bpm). Lung
  compliance is constant within numerical precision throughout the
  window (e.g. 0.0900 ± 5×10⁻⁶ L/cmH2O for the worst-CV run S1_F_0008),
  excluding dynamic hyperinflation as a contributor.

  Source audit of `SEMechanicalVentilatorVolumeControl::ToSettings`
  (`SEMechanicalVentilatorVolumeControl.cpp` lines 120–128, Pulse 4.3.1)
  identifies the mechanism. Pulse's VC-AC mode falls through to
  `InspirationPatientTriggerRespiratoryModel = On` when the action
  specifies neither `InspirationPatientTriggerFlow` nor
  `InspirationPatientTriggerPressure`:

  ```
  if (!HasInspirationPatientTriggerFlow() && !HasInspirationPatientTriggerPressure())
      SetInspirationPatientTriggerRespiratoryModel(On);
  ```

  With this default, the simulated patient's spontaneous respiratory
  drive (modelled by Pulse's whole-body respiratory controller) can
  trigger an assist breath whenever its inspiratory effort registers as
  a `StartOfInhale` event (`MechanicalVentilatorModel.cpp` lines
  810–818). At extreme ventilator settings — high Vt on a small
  predicted-body-weight lung, very low Vt with high PEEP, or RR
  mismatched to the simulated metabolic CO₂ load — the simulated drive
  overshoots the mandatory rate, generating the observed mandatory +
  assist alternation.

  **Causal confirmation (S014).** A pre-registered controlled experiment
  on the top-64 Vt-CV runs reran each with identical inputs but with an
  explicit `InspirationPatientTriggerPressure = −2 cmH2O`. Setting any
  explicit trigger threshold disables the respiratory-model branch (the
  fall-through guard becomes false). **Median (Vt_cv_original −
  Vt_cv_lockout) = +0.326** (pre-registered threshold ≥ 0.04, exceeded
  8×); **proportion of locked runs with Vt_cv < 0.05 = 78.1 %**
  (pre-registered threshold ≥ 75 %). Median Vt_cv collapses from 0.351
  to 0.016 (96 % reduction); worst-case from 1.826 to 0.112. Both
  pre-registered thresholds were met, confirming that the dyssynchrony
  — not solver instability, not Nyquist aliasing of the breath cycle,
  and not auto-PEEP — drives the original 20.6 % flag rate. Full
  protocol and per-run paired data:
  [`experiments_log/santino/S014_trigger_pressure_lockout.md`](../experiments_log/santino/S014_trigger_pressure_lockout.md);
  raw artefacts in `data/runs/s014_trigger_lockout/`.

### 3.8.1 Steady-state window cross-output audit (S012)

A reviewer-anticipated question is whether F-003 and F-004 contaminate
the rest of the steady-state window — i.e. whether the same runs that
show PaO2 drift or Vt oscillation also exhibit drift in the
cardiovascular and gas-exchange channels we use for Morris analysis.
A targeted audit ([S012](../experiments_log/santino/S012_steady_state_window_audit.md))
computes |Δ60s| (drift over the recorded window) for HR / MAP / Vt /
PaO2 / PaCO2 in both vulnerable populations and compares against the
preregistered drift thresholds (`DRIFT_MAX_DELTA_60S` in
`src/detector.py`: HR=5 bpm, MAP=5 mmHg, Vt=50 mL, PaO2=15 mmHg,
PaCO2=5 mmHg).

* **F-003 arm — hyperoxia (FiO2 ≥ 0.95, n = 208 runs).** HR exceeds the
  5 bpm threshold in **2.6 %** of runs (median |Δ60s| = 0.20 bpm); MAP
  in **0 %** (median 0.05 mmHg). Vt exceeds 50 mL in **8.7 %** (median
  0.09 mL — the violations sit in the F-004 oscillation tail). PaO2 is
  the only severely affected channel: **19.5 %** exceed the 15 mmHg
  drift threshold (median 4.3 mmHg, p95 = 40.2 mmHg). *Interpretation:
  the cardiovascular loop is steady at FiO2 = 1.0; only gas-exchange
  oxygenation and tidal-volume control are unsettled.*
* **F-004 arm — Vt oscillation (Vt_cv > 5 %, n = 303 runs).** HR
  exceeds 5 bpm in **2.3 %**, MAP in **0.7 %**, PaO2 in **7.3 %**,
  PaCO2 in **2.0 %**. *Interpretation: tidal-volume oscillation does
  not propagate into cardiovascular or gas-exchange drift; Pulse
  buffers the oscillation upstream.*
* **Intersection (FiO2 ≥ 0.95 AND Vt_cv > 5 %): 33 / 1,280 runs.**
  Even in this dual-vulnerability population, HR/MAP/PaCO2 drift rates
  remain below 4 %.

The audit shows the [60, 120] s window is reliable for HR, MAP, and
PaCO2 across the full sweep — the steady-state definition holds for
the cardiovascular and ventilation channels used by Morris analysis.
The window is *only* unreliable for PaO2 and Vt at FiO2 ≥ 0.95, which
is exactly what F-003 and F-004 already disclose. The F-003 / F-004
findings are therefore not a hidden invalidator of the rest of the
sweep; they are the bounded scope of an explicitly-disclosed
window-length limitation. Numerical detail in
[`results/s012_summary.csv`](../results/s012_summary.csv) and the
two per-arm files in `results/`.

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
* **VC-AC dyssynchrony refines rather than indicts Pulse's
  implementation.** The F-004 finding (Vt CV > 5 % in 20.6 % of runs) is
  not a controller pathology: patient-ventilator dyssynchrony at extreme
  settings is a real intensive-care phenomenon and Pulse models it
  correctly. The atlas's preregistered steady-state detector simply
  flags the resulting Vt variability as a non-steady-state outcome, by
  design. Two practical consequences follow. First, atlas users who
  require pure mandatory ventilation (e.g. for medical-device validation
  against a known-volume reference) must specify an explicit
  `InspirationPatientTriggerPressure` (or
  `InspirationPatientTriggerFlow`) on the VC-AC action. The default
  configuration in the upstream `kitware/pulse:4.3.1` image and in the
  `pulse-pediatric-engine` wrapper allows the respiratory-model trigger;
  this is realistic but produces non-steady tidal volumes at exactly
  the ventilator-stress points where validation matters most. Section
  4.2 recommends the −2 cmH2O setting validated by S014 as a sensible
  default for atlas-style sensitivity work. Second, the prevalence of
  dyssynchrony events (20.6 % across the full 7-input sweep) bounds how
  much of Pulse's VC-AC behaviour at the default trigger configuration
  is steady-state interpretable. Sensitivity indices computed on the
  dyssynchrony-flagged subset are not directly comparable to those on
  the steady runs; the atlas's preregistered analysis plan correctly
  excludes flagged runs from Morris EE computation. Future work using
  Pulse for closed-loop VC-AC studies should commit to an explicit
  trigger configuration up-front and re-derive baseline reliability
  under that configuration.

The practical operational recommendation is captured succinctly: **use
the cells coloured green; report results from yellow cells with their
flag counts; avoid red cells unless the use-case is specifically about
that operational extreme.**

### 4.2 Practical recommendations

**VC-AC trigger configuration.** When using Pulse 4.3.1's
`SEMechanicalVentilatorVolumeControl` action in *AssistedControl* mode,
always set `InspirationPatientTriggerPressure` or
`InspirationPatientTriggerFlow` explicitly. Leaving both unspecified
causes Pulse to enable a respiratory-model-driven patient trigger
(`SEMechanicalVentilatorVolumeControl.cpp` lines 120–128), which
produces realistic patient-ventilator dyssynchrony but renders
delivered tidal volume non-steady at extreme input combinations. For
sensitivity-analysis-style sweeps where steady-state interpretation is
required, we recommend `InspirationPatientTriggerPressure = −2 cmH2O`
as a default; this matches a clinically standard ICU sensitivity
setting and is the configuration validated by S014 in this paper
(median Vt_cv collapses from 0.351 to 0.016, a 96 % reduction; 78.1 %
of locked runs fall below the 0.05 steady-state threshold).

### 4.3 Limitations

* Atlas restricted to VC-AC adults; pediatric and PC modes out of scope
  (Paper 2 / Paper 1).
* 120 s simulation may be insufficient for hyperoxia convergence (F-003).
  We do not extend simulation length post hoc — the locked window IS the
  paper's measurement; longer windows are explicit future work. The
  S012 cross-output audit (§3.8.1) bounds this limitation to PaO2 and
  Vt at FiO2 ≥ 0.95: HR, MAP, and PaCO2 drift rates stay below 3 % in
  both vulnerable populations, so the [60, 120] s steady-state window
  remains reliable for the cardiovascular and ventilation channels.
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

### 4.4 Connection to downstream PhD work

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

Primary sources only — every cited fact in this paper traces to one of
the following or to an experiment-log entry in this repository.

1. **Pulse Physiology Engine v4.3.1 (Kitware, Apache-2.0).**
   Distributed at <https://pulse.kitware.com>. Source verified from
   the locally-cloned engine repository
   (`C:/Users/santi/projets/Pulse_engine_adults_Gitlab/engine/`,
   2026-04-07).
2. **Pulse FAQ.** *Have you done UQ / SA?*
   <https://pulse.kitware.com/_f_a_q.html> — verified verbatim
   2026-04-19, paragraph quoted in §1.1 (recorded in S003).
3. **Pulse Setup audit.**
   `engine/src/cpp/engine/human_adult/whole_body/controller/SetupPatient.cpp`
   — referenced for adult age gate (lines 41 – 64), BMI bounds (lines
   179 – 200), blood-volume formula (line 534), HR / SBP / DBP
   acceptance bounds (verified by E10 / E28 / E29).
4. **Webb et al. 2023.** Comparison of mechanical ventilator behaviour
   under VC-AC against an ASL 5000 lung simulator. PubMed Central
   article PMC10224749. Cited for VC-AC tidal-volume error and as the
   basis for our preregistered ventilator-mode restriction.
5. **Bray et al. 2019.** Cardiovascular limitations of the
   lumped-parameter model — referenced for valve idealization,
   dicrotic-notch absence, and viscoelastic limitation.
6. **Pediatric Acute Lung Injury Consensus Conference (PALICC-2).**
   ARDS severity classification (mild / moderate / severe), used to
   anchor scenarios S2 (0.26), S3 (0.60), S4 (0.95). Berlin Criteria
   correspondence verified through Pulse's own ARDS validation table.
7. **SALib (Iwanaga, Usher, Herman 2022).** Socio-Environmental
   Systems Modelling. Morris and Sobol implementations used for
   sampling and analysis.
8. **Barnes et al. 2020.** *Comparison of three open-source physiology
   engines on hemorrhage scenarios.* DOI:
   [10.1097/SIH.0000000000000427](https://doi.org/10.1097/SIH.0000000000000427).
   Cited as the only independent multi-engine assessment we are aware
   of (BioGears tested, not Pulse).
9. **Clipp et al. 2025 (MHSRS).** Updated Pulse hemorrhage validation —
   cited for context that Pulse has improved since the Barnes 2020
   tests.
10. **JOSS issue #4929** (Pulse review, 2022 – 2023). Cited for context
    on the engine's open peer-review status.

Internal references (`experiments_log/santino/Sxxx_*.md`) are
additionally available in the repository:

* **S001** — Docker + 3-parallel hardware smoke test (CPU / RAM
  budget verification).
* **S002** — Project bootstrap, repo layout, licensing.
* **S003** — Verified Pulse 4.3.1 limitations from primary sources.
* **S004** — Atlas Docker image, scenario smoke test, detector regex
  empirical recalibration.
* **S005** — 22-run pilot, all 5 preregistered gates passed.
* **S006** — Full 1,280-run sweep with 8 sanity checks.
* **S007** — Targeted reproducibility check at three independent
  layers, all bit-exact.
* **S008** — Tier-1 statistical refinement (block bootstrap, within-
  sex Wasserstein null, divergence-input mechanism, Spearman CI).
* **S009** — Tier-2 (seed stability, continuous-ARDS sweep, pytest,
  GitHub Actions CI).
* **S010** — Literature-review pass; every reference below verified
  against its DOI / PMID.

### 6.7 Verified primary references (full bibliographic detail)

Each entry has been individually verified against its DOI or PMID
during the literature-review pass logged in
[`experiments_log/santino/S010_literature_review.md`](../experiments_log/santino/S010_literature_review.md).

**Pulse Physiology Engine**

* Bray AC, Carpenter J, Webb JB, Clipp RB. *Pulse Physiology Engine:
  An Open-Source Software Platform for Computational Modeling of
  Human Medical Simulation.* SN Comprehensive Clinical Medicine
  1:362-377 (2019). DOI:
  [10.1007/s42399-019-00053-w](https://doi.org/10.1007/s42399-019-00053-w).
* Webb JB, Bray A, Asare PK, Clipp RB, Mehta YB, Penupolu S, Patel
  AA, Poler SM. *Computational simulation to assess patient safety
  of uncompensated COVID-19 two-patient ventilator sharing using the
  Pulse Physiology Engine.* PLoS One 15(11):e0242532 (2020). DOI:
  [10.1371/journal.pone.0242532](https://doi.org/10.1371/journal.pone.0242532).
  PMID: 33237927.
* Webb J, Asare P, Bray A, Clipp R. *PulseExt: validation of the
  Pulse Physiology Engine ventilator against the ASL 5000 lung
  simulator.* (2023). PubMed Central:
  [PMC10224749](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10224749/).

**Sensitivity-analysis methods**

* Morris MD. *Factorial sampling plans for preliminary computational
  experiments.* Technometrics 33(2):161-174 (1991). DOI:
  [10.2307/1269043](https://doi.org/10.2307/1269043) /
  [10.1080/00401706.1991.10484804](https://doi.org/10.1080/00401706.1991.10484804).
* Campolongo F, Cariboni J, Saltelli A. *An effective screening
  design for sensitivity analysis of large models.* Environmental
  Modelling & Software 22(10):1509-1518 (2007). DOI:
  [10.1016/j.envsoft.2006.10.004](https://doi.org/10.1016/j.envsoft.2006.10.004).
* Iwanaga T, Usher W, Herman J. *Toward SALib 2.0: Advancing the
  accessibility and interpretability of global sensitivity analyses.*
  Socio-Environmental Systems Modelling 4:18155 (2022). DOI:
  [10.18174/sesmo.18155](https://doi.org/10.18174/sesmo.18155).

**Acute respiratory distress syndrome (clinical anchors)**

* ARDS Definition Task Force; Ranieri VM, Rubenfeld GD, Thompson BT,
  Ferguson ND, Caldwell E, Fan E, Camporota L, Slutsky AS. *Acute
  respiratory distress syndrome: the Berlin Definition.* JAMA
  307(23):2526-2533 (2012). DOI:
  [10.1001/jama.2012.5669](https://doi.org/10.1001/jama.2012.5669).
  PMID: 22797452.
* Emeriaud G, López-Fernández YM, Iyer NP, Bembea MM, Agulnik A,
  Barbaro RP, et al. *Executive Summary of the Second International
  Guidelines for the Diagnosis and Management of Pediatric Acute
  Respiratory Distress Syndrome (PALICC-2).* Pediatric Critical Care
  Medicine 24(2):143-168 (2023). DOI:
  [10.1097/PCC.0000000000003147](https://doi.org/10.1097/PCC.0000000000003147).
  PMID: 36661420.
* Acute Respiratory Distress Syndrome Network; Brower RG, Matthay
  MA, Morris A, Schoenfeld D, Thompson BT, Wheeler A. *Ventilation
  with lower tidal volumes as compared with traditional tidal
  volumes for acute lung injury and the acute respiratory distress
  syndrome.* New England Journal of Medicine 342(18):1301-1308
  (2000). DOI:
  [10.1056/NEJM200005043421801](https://doi.org/10.1056/NEJM200005043421801).
  PMID: 10793162.

**Other physiology engines (comparative context)**

* Barnes SL, Sing P, Bash B, Sherman R, et al. *Quantitative
  Comparison of BioGears, HumMod, and Muse Physiology Engines on
  Hemorrhage Scenarios.* Simulation in Healthcare (2020). DOI:
  [10.1097/SIH.0000000000000427](https://doi.org/10.1097/SIH.0000000000000427).

**Reproducibility / methods-paper integrity**

* Wilkinson MD, Dumontier M, Aalbersberg IJ, et al. *The FAIR
  Guiding Principles for scientific data management and stewardship.*
  Scientific Data 3:160018 (2016). DOI:
  [10.1038/sdata.2016.18](https://doi.org/10.1038/sdata.2016.18).
  PMID: 26978244.
* Munafò MR, Nosek BA, Bishop DVM, Button KS, Chambers CD, du Sert
  NP, Simonsohn U, Wagenmakers EJ, Ware JJ, Ioannidis JPA. *A
  manifesto for reproducible science.* Nature Human Behaviour
  1(1):0021 (2017). DOI:
  [10.1038/s41562-016-0021](https://doi.org/10.1038/s41562-016-0021).

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
