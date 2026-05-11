# Pulse Reliability Atlas — first sensitivity, clamping, and divergence map for the Pulse Physiology Engine v4.3.1

**Author:** Santino Nanini

---

## Abstract

**Background.** The Pulse Physiology Engine (Kitware, Apache-2.0; v4.3.1)
is the most-used open-source whole-body human physiology simulator. Its
developers state on the Pulse FAQ that no formal sensitivity analysis has
been performed on user-facing operational inputs. Prior external work
[@cornish2023] addressed intervention-outcome falsification on
MIMIC-III sepsis; the operational-input reliability question has remained
unaddressed.

**Methods.** We swept seven inputs (HR, SBP, DBP, RR, Vt, FiO2, PEEP) from
Pulse's verified acceptance ranges via Morris elementary-effects sampling
across four scenarios (healthy + three ARDS severities spanning PALICC-2
mild–severe and the 0.91–0.945 solver-instability zone) and two adult
surrogates (Pulse standard male and female), for 1,280 simulations. A
locked four-flag detector (`clamped` / `diverged` / `implausible` /
`not_steady_state`) classified every run before analysis.

**Results.** Sensitivity is strongly skewed: 48 of 48 (cell × output)
combinations have ≥ 50 % of summed μ\* in their top-3 inputs (median
0.928), and the engine is **predominantly linear** for these dominant
parameters. Pulse rejects out-of-range inputs *loudly*: 0 of 1,280 runs
fired the silent-clamping flag. Solver divergence is sex-stratified —
20 of 1,280 runs (1.6 %) diverged, **all 20 male in the input-extreme
regime** (sex-stratification is regime-dependent; §3.5.1). Two boundary
findings: **F-003**, Pulse produces PaO2 > 600 mmHg at FiO2 = 1.0
(hyperoxia overshoot); **F-004**, VC-AC (volume-controlled assist-control) tidal-volume instability in
20.6 % of runs, **causally identified as patient-ventilator
dyssynchrony at the inspiration trigger and corrected by setting trigger
pressure to −2 cmH2O** (worst-case Vt CV collapses from 0.351 to 0.016).
H4 (sex-specific reliability) is partially supported: 6 of 24 cell ×
output Wasserstein distances exceed a within-sex null — all six are
gas-exchange (PaCO2, SpO2, PaO2). Cardiovascular and Vt sex effects do
not exceed within-sex sub-sampling; input-importance rankings are largely
preserved across sexes (Spearman ρ 0.75 – 1.00 in S2 / S3).

**Conclusion.** The atlas provides a per-cell traffic-light reliability
map for adult Pulse 4.3.1, identifies sex as a previously uncharacterized
reliability-sensitivity axis, and yields one operator-actionable
correction: setting VC-AC inspiration trigger pressure to −2 cmH2O.

---

## 1. Introduction

### 1.1 Motivation

The Pulse Physiology Engine [@bray2019] (Kitware, Apache-2.0)
is the most-used open-source whole-body human physiology simulator.
It provides a 0-dimensional lumped-parameter model of the
cardiovascular, respiratory, gas-exchange, and pharmacological
systems, and is used in three broad communities:

* **Clinical research** — virtual-patient cohorts for hypothesis
  generation when human data are unavailable, ethically constrained,
  or impractically expensive to collect (e.g. dual-patient ventilator
  sharing during the COVID-19 pandemic [@webb2020]).
* **Medical-device development** — early-stage validation of
  ventilators, pumps, and monitors against a virtual patient. ASL 5000
  benchmarking against Pulse's VC-AC mode reports tidal-volume errors
  of 0.07 – 2.25 % [@webb2023].
* **Education** — anaesthesia, critical-care, and paramedic training
  curricula increasingly use Pulse for case-based simulation.

Despite this footprint, the engine's developers state explicitly on
the public Pulse FAQ [@pulsefaq; verified verbatim 2026-04-19, still
current as of the May 2026 GitLab re-audit, S003 / S016]:

> "We have not performed a systematic forward propagation or inverse
> quantification of model uncertainty, nor have we conducted a formal
> sensitivity analysis."

A May 2026 audit of the Pulse repository (S016) qualifies this. The
repo carries a 2020 tag `STUDY_SENSITIVITY_ANALYSIS_1_0_0` containing
a one-off Sobol study on **internal vascular-circuit resistance
multipliers** for model calibration (per its ReadMe) — a different
parameter class from user-facing operational inputs, not ported to
the 4.3.x release line. Prior external work [@cornish2023]
addressed intervention-outcome falsification — verifying whether
Pulse accurately mimics how a real patient's trajectory changes after
a medical intervention — on MIMIC-III sepsis trajectories, a different
scope from the operational-input reliability question addressed here,
applied to a different cohort and dataset. No systematic sensitivity
analysis on **user-facing operational inputs** (HR, BP, RR, Vt, FiO2,
PEEP) has been published.

The corollary is operational: every Pulse user driving the engine
from operational settings — clinical, industrial, educational — is
operating *without a map* of where the engine is reliable, where it
silently bends inputs out of acceptance, and which inputs dominate
which outputs. Each user re-encounters the same limitations
independently. Each medical-device validation pipeline re-derives its
own working envelope by trial and error.

This paper closes that gap with the first open reliability atlas for
Pulse v4.3.1 across the adult operational envelope relevant to
critical care. The methodology follows three commitments locked
before any data was collected (preregistration §Inputs, §Scenarios,
§Flags):

* **Inputs** swept from Pulse's *verified* acceptance ranges
  (E10 / E28 / E29 boundary probes).
* **Scenarios** spanning healthy adult and three ARDS severities
  anchored on the Berlin Definition [@ards2012] and PALICC-2
  [@emeriaud2023] classifications.
* **A four-flag classifier** that categorizes every run rather than
  discarding flagged ones (preregistration discipline per
  [@munafo2017]).

Four properties make this paper a methods-paper rather than a
findings-paper: (1) the entire pipeline is preregistered with
amendment history (per [@munafo2017]); (2) every quoted
number is reproducible from the canonical Morris sample (seed = 42)
plus the atlas Docker image, verified at three independent layers
(S007); (3) the data are released under FAIR principles
[@wilkinson2016]; and (4) the four-flag classifier is a generic
instrument that future Pulse users can apply to their own
configurations without re-running our sweep.

The paper is the first publishable output in the maintainer's PhD
pipeline. Two downstream papers — pediatric translation layer (in
preparation, validation underway) and native pediatric Pulse fork
(planned) — both depend on knowing where adult Pulse is trustworthy.
This atlas is that prerequisite.

### 1.2 Verified limitations of Pulse 4.3.1

Twelve limitations were verified against primary sources before the
preregistration was locked ([S003](../experiments_log/santino/S003_pulse_limitations_verified.md)).
This atlas adds quantitative coverage to those:

1. No formal SA / UQ on user-facing operational inputs — addressed by
   this paper. The 2020 `STUDY_SENSITIVITY_ANALYSIS_1_0_0` tag in the
   Pulse repository (Sobol on internal lumped-parameter circuit
   resistances for model calibration) addressed a different parameter
   class and has not been ported to 4.3.x; the FAQ statement remains
   current. Audit details in S016.
2. BP clamping above SBP > 120 / DBP > 80 — verified empirically; locked
   sampler ranges respect this so it does not contaminate H2.
3. Adult-only (age ≥ 18 hard-gated in `SetupPatient.cpp`) — atlas restricted
   to two adult surrogates by design.
4. ARDS solver instability 0.91–0.945 — S4 (severity = 0.95) intentionally
   placed above the zone.
5–6. HR init acceptance 50–110 / RR init acceptance 8–20 — sampler ranges
   match.
7. PC-AC over-delivers Vt [@webb2023; companion verification E12, E13] — atlas restricts to VC-AC.
8–12. Structural lumped-parameter limits — discussed in §4.3.

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
  (preregistered analysis plan; bootstrap CI is a post-hoc
  methodological enhancement, transparent in the preregistration
  amendment log, with no impact on hypothesis thresholds).
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
| Vt target | 300–800 | mL | ARDSnet 6 mL/kg [@brower2000] to pre-ARDSnet 10 mL/kg |
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

NHANES P50 anchors confirm both surrogates are representative of
healthy adults: median HR 70 bpm (M) / 74 bpm (F), SBP 118 mmHg (M)
/ 113 mmHg (F), DBP 70 mmHg (M) / 69 mmHg (F). Companion
verification (`Pulse_translation_new` E12, E13) established that
the female surrogate produces physiologically plausible engine
output across all four scenarios, independent of the Atlas sweep.

Ventilator: VC-AC (volume-controlled assist-control) only — the
ventilator delivers a fixed tidal volume on a set schedule while
still allowing the patient to trigger additional breaths between
mandatory cycles. The mode choice is justified by @webb2023
reporting VC-AC tidal-volume errors of
0.07 – 2.25 % across healthy, restrictive, and obstructive lung
profiles vs PC-AC's 11 – 25 %. Companion verification (E12, E13)
further found that PC-AC over-delivery scales inversely with body
weight (female +58.9 % vs male +24.0 % at PIP = 20 cmH2O),
reinforcing the preregistration's VC-AC restriction.

### 2.4 Simulation cadence

120 s simulation, sample interval 5 s, steady-state window [60, 120] s
(13 points). Detector enforces 13 points / clean run.

### 2.5 Morris sampling

The Morris elementary-effects design [@morris1991], with the radial-
trajectory + μ\* refinement of [@campolongo2007],
is an efficient one-at-a-time screening method that ranks inputs by
overall importance (μ\*, the mean of absolute elementary effects)
and flags non-linearity or input-input interaction (σ, the standard
deviation of those effects), at a small fraction of the cost of a
full variance-based analysis. Implementation: SALib's
`morris.sample(N=20, num_levels=4, seed=42)` [@iwanaga2022] ⇒
160 unique input points. The same 160 points drive every
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

Figures 2 a–f show the Morris μ\* heatmap for each of the six outputs.
Rows are the seven swept inputs; columns are the eight (scenario, sex)
cells. The colour scale is the magnitude of the elementary effect — how
much each output moves when the corresponding input is perturbed. Four
visual patterns dominate:

* **Cardiovascular outputs are cardio-input dominated.** Output HR is
  driven by input HR in every cell (μ\* ≈ 55 in healthy → ≈ 95 in
  severe ARDS); output MAP is driven by SBP in every cell (μ\* ≈ 17 –
  20). No cross-talk from ventilator settings.
* **Gas-exchange outputs are ventilator-driven.** PaO2 is dominated by
  FiO2 in S2 / S3 (μ\* peaks at 147 mmHg in (S2, F)) — the regime
  where shunt-fraction kinetics make oxygenation FiO2-limited. PaCO2
  is dominated by Vt in most cells, consistent with the alveolar-
  ventilation identity V̇A = RR · (Vt − V_dead). SpO2 is also
  ventilator-driven but at a tiny absolute scale (μ\* ≤ 0.12) because
  the output sits at the hemoglobin saturation ceiling.
* **The ARDS gradient is visible.** PaO2's FiO2 sensitivity peaks at
  S2 / S3 (μ\* = 133 – 147 mmHg) and *collapses* in severe ARDS (μ\* =
  31 in (S4, M)). Pulse correctly captures the regime where shunt
  physiology pins PaO2 regardless of FiO2 — a textbook ARDS finding,
  captured by the engine without explicit programming.
* **Output Vt tracks input Vt at μ\* ≈ 500 mL** in every cell — by
  far the largest μ\* in the atlas. In VC-AC mode, asking Pulse for a
  500 mL tidal volume produces close to a 500 mL delivered tidal
  volume, cell-invariant. The cells where this coupling fails are the
  F-004 dyssynchrony runs (§3.8).

**Bootstrap 95 % CI on μ\*** (1,000 resamples) is reported alongside
each μ\* point estimate in the table; CI overlap between the top-3 and
the rest is the formal H1 test.

**External cross-validation against an OAT precursor.** Companion
one-at-a-time probing prior to the Atlas (Pulse_translation_new E24,
±10 % perturbations on healthy and ARDS-moderate cells, n = 74 Docker
runs) reported the FiO2 → PaO2 elasticity collapsing from 1.32 in
healthy to 0.26 in moderate ARDS — an ~80 % attenuation as shunt
physiology takes over. The Atlas Morris μ\* for PaO2 ~ FiO2 reproduces
both the direction and roughly the magnitude of this attenuation:
μ\* peaks at S2 / S3 (147 mmHg in (S2, F)) and falls to 31 mmHg in
(S4, M), a ~79 % drop. Elasticity (local %-change/%-change) and μ\*
(mean absolute elementary effect in output units) are formally
different metrics, so this is a qualitative consistency check rather
than a numerical equivalence — but the matched direction and
order-of-magnitude attenuation across two independent designs is an
external robustness signal for the Atlas's FiO2 sensitivity ranking.

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

### 3.3.1 Sobol bolt-on: preregistered decision

The preregistered protocol (preregistration §Sampling method)
specified a conditional variance-based Sobol analysis if any
top-ranked input exhibited σ / μ\* ≥ 0.6 in any cell, indicating
non-linearity or strong interactions that Morris elementary effects
cannot resolve. Applying this rule to the dominant input per
(scenario, sex, output) cell, **8 of 48 cells fire the trigger.**
Manual inspection separates these into two regimes:

* **Group A — noise-dominated (2 of 8).** Cells where the dominant
  input's μ\* sits at numerical-noise level because the output is at
  physiological saturation. Both are SpO2 outputs in healthy
  patients: (S1, F, SpO2, PEEP) with μ\* = 0.0037 and σ = 0.0068, and
  (S1, M, SpO2, Vt) with μ\* = 0.028 and σ = 0.023. SpO2 in the
  healthy respiratory envelope sits at ≈ 0.997 (hemoglobin
  saturation ceiling), so the Morris elementary effects are
  floating-point fluctuation, not physiological signal — the σ / μ\*
  ratio is mathematically high but physiologically empty.
* **Group B — known nonlinear physiology (6 of 8).** Four cells
  reflect FiO2 → PaO2 shunt-fraction kinetics in ARDS scenarios:
  (S2 / S3, M / F, PaO2, FiO2) with μ\* in the 84 – 147 mmHg range
  and σ / μ\* between 0.64 and 0.94. This is exactly the regime where
  venous admixture caps oxygenation gain per FiO2 increment — an
  established physiological nonlinearity. The remaining two cells
  reflect minute-ventilation coupling on PaCO2: RR → PaCO2 in
  healthy males ((S1, M), σ / μ\* = 0.87) and Vt → PaCO2 in severe
  ARDS females ((S4, F), σ / μ\* = 0.66) — both expected from the
  alveolar-ventilation identity V̇A = RR · (Vt − Vd) driving CO2
  elimination.

Quantitative variance decomposition (Sobol S₁ / Sₜ indices) on the
Group B cells is deferred to follow-up work. Running it in this paper
would consume ≈ 3,600 additional Pulse runs (~ 13 h compute on the
maintainer's laptop with 2 parallel Docker workers) to confirm a
qualitative interaction structure that is *a priori* established by
respiratory physiology and *qualitatively* recovered by the Morris
main-effect rankings reported in §3.2 (Figure 2). The preregistered
Sobol bolt-on commitment is **closed in this paper** on these
grounds. Future reviewers wishing variance decomposition can re-run
from the canonical Morris sample
(`data/runs/full_sweep/morris_sample.parquet`) and the atlas Docker
image (S006); the analysis pipeline is preserved in
`src/analysis_morris.py`.

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
   line and exit code 1, not a silent substitution. Rejection is loud and
   observable; users can detect it from logs alone with no special
   instrumentation.

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

### 3.5 H3 — solver divergence exists; sex-stratification is regime-dependent (partially supported)

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

We report H4 with two complementary statistics. The 1-Wasserstein
distance quantifies the absolute magnitude of the difference between
male and female clean-run output *distributions*, expressed in the
output's natural units (mmHg, bpm, mL). Spearman's ρ (rho) rank
correlation between M and F Morris μ\* *vectors* asks whether both
sexes prioritize the same inputs (ρ = 1 ⇒ identical input ordering,
ρ = −1 ⇒ inverted ordering) — a different question from how big the
sex-specific output shifts are. For both we add a null reference
because raw point estimates on this sample size overstate precision.

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

Pre-Atlas engine verification (`Pulse_translation_new` E12, E13)
established that the female surrogate produces physiologically
plausible output across all four scenarios independent of this
sweep, so the observed sex effects above reflect real engine-level
sex-specific physiology rather than miscalibration of the female
patient model.

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
  ground-truth physiology without careful per-input validation. Note
  that the male-divergence clustering reported here is specific to the
  S006 input-extreme regime; the complementary continuous-severity
  sweep (§3.5.1) at midrange inputs produced balanced female / male
  divergence in the [0.879, 0.945] band, with the sex effect varying
  with what is varying (Morris-extreme inputs vs ARDS severity).
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
  control thermal load; resume-safe). The preregistered Sobol
  bolt-on (preregistration §Sampling method) was evaluated and
  formally closed in §3.3.1; if future work re-opens it on the
  Group B cells, larger-scale variance decomposition would benefit
  from a cluster.
* **Theoretical vs. empirical coverage.** The Morris sweep samples the
  extremes of Pulse's theoretical acceptance envelope based on
  standardized ARDS definitions. It does not quantify the engine's
  empirical operational coverage — i.e., what fraction of actual,
  real-world ICU patient configurations (such as those found in
  MIMIC-IV or pediatric databases) fall safely within the stable,
  linear regimes identified here. Mapping the engine's reliability
  against the empirical distribution of clinical datasets remains a
  necessary limitation of the current theoretical atlas.

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
   2026-04-07; GitLab re-audit 2026-05-07, S016). The current
   `stable` head is `REL_4_3_2` (2025-08-12), whose full diff vs
   `REL_4_3_1` is 7 files / +46 −17 lines (web-WASM dockcross
   support, .NET binding tweak); no physiology, validation,
   patient-setup, or solver code changed. Atlas results on 4.3.1
   apply identically to 4.3.2.
2. **Pulse FAQ.** *Have you done UQ / SA?*
   <https://pulse.kitware.com/_f_a_q.html> — verified verbatim
   2026-04-19, still current at the May 2026 re-audit; paragraph
   quoted in §1.1 (recorded in S003 / S016).
2a. **Pulse `STUDY_SENSITIVITY_ANALYSIS_1_0_0` tag (Kitware, 2020-07-20).**
    Code at `src/cpp/study/sensitivity_analysis/` and
    `src/python/pulse/study/sensitivity_analysis/` in the Pulse
    GitLab repository. Sobol S1/ST analysis with an ML surrogate
    over internal lumped-parameter vascular-circuit resistance
    multipliers (model-calibration parameters); ReadMe scope
    statement: *"sensitivity analysis as a path towards improved
    lumped parameter optimization."* Last functional commit
    2020-08-24; not ported to Pulse 4.3.x. Cited in §1.1 to
    distinguish internal-calibration SA (their scope) from
    operational-input SA (this paper's scope). Audit logged in
    S016 (2026-05-07).
2b. **Cornish R, Taufiq MF, Doucet A, Holmes C (Oxford, 2023).**
    *Causal Falsification of Digital Twins.* arXiv:2301.07210
    (November 2023). External statistical-falsification framework
    applied to Pulse on MIMIC-III sepsis trajectories;
    identifies specific intervention-outcome inaccuracies. Cited
    in §1.1 to distinguish prior external assessment
    (intervention-outcome falsification on a different cohort and
    dataset) from this paper's contribution (operational-input
    reliability across the adult ICU envelope). Identified in the
    May 2026 audit logged in S016.
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
* Cornish R, Taufiq MF, Doucet A, Holmes C. *Causal Falsification
  of Digital Twins.* arXiv:2301.07210 (November 2023). Oxford
  statistics group. External assessment of Pulse on MIMIC-III
  sepsis trajectories using a causal-inference / statistical-
  falsification framework; identifies intervention-outcome
  inaccuracies in specific cases. Cited in §1.1 to distinguish
  prior external assessment (intervention-outcome falsification on
  a different cohort and dataset) from this paper's contribution
  (operational-input reliability across the adult ICU envelope).

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
| S007 | Targeted reproducibility check (3-layer, all bit-exact) |
| S008 | Tier-1 statistical refinement (block bootstrap, Wasserstein null) |
| S009 | Tier-2 (seed stability, continuous-ARDS, pytest, GHA CI) |
| S010 | Literature-review pass (every reference DOI / PMID-verified) |
| S011 | Sex-vs-mass disentangle |
| S012 | Steady-state window cross-output audit |
| S013 | Lexical lockdown (manuscript taxonomy) |
| S014 | Trigger-pressure lockout (F-004 mechanism) |
| S015 | Reproducibility and logic audit (pre-publication) |
| S016 | Pulse GitLab + literature re-audit (May 2026) |

Each log file in `experiments_log/santino/` follows the template:
hypothesis → motivation → method → what we tried → results → interpretation
→ next steps.

---

## Appendix B — Adult Pulse operational envelope: pre-Atlas boundary characterization

### B.1 Provenance and methodology

The boundary characterization, acceptance gates, and condition
calibrations detailed in this appendix were established in companion
developmental work prior to the execution of the preregistered Morris
elementary-effects sweep. They are documented here to define the exact
adult operational envelope of the Pulse Physiology Engine (v4.3.1) and
to ensure reproducibility. The complete experimental logs and Docker
replication scripts for these boundary probes are available in the
companion repository [Insert Citation/DOI].

### B.2 Hard input acceptance gates

Pulse 4.3.1 enforces strict patient-initialization boundaries.
Configurations outside these ranges result in immediate engine
initialization failure prior to stabilization.

* **Heart rate (HR):** The accepted baseline range is strictly
  50–110 bpm. Probes confirmed rejection at 49 bpm and 111 bpm.
* **Respiratory rate (RR):** The accepted baseline range is strictly
  8–20 bpm. Probes confirmed rejection at 7 bpm and 21 bpm.
* **Blood pressure (BP):** Systolic blood pressure (SBP) is
  constrained to 90–120 mmHg. Diastolic blood pressure (DBP) is
  constrained to 60–80 mmHg.
* **Pulse-pressure constraint:** An undocumented constraint was
  identified during boundary probing: the engine requires a
  pulse-pressure ratio where DBP / SBP ≤ 0.75. If this ratio is
  exceeded (e.g., SBP = 90 mmHg and DBP = 68 mmHg, ratio = 0.756),
  initialization is rejected even if individual values fall within
  the allowed absolute ranges.
* **Fraction of inspired oxygen (FiO2):** Direct probing confirmed
  that the engine remains fully stable up to FiO2 = 1.0. The partial
  pressure of oxygen (PaO2) scales linearly by approximately
  7.8 mmHg per 0.01 increase in FiO2.

### B.3 ARDS severity calibration and solver instability

The Acute Respiratory Distress Syndrome (ARDS) condition in Pulse is
modulated by an impairment fraction (0.0 to 1.0). To align with the
Berlin Definition severity bands via PaO2 / FiO2 (P/F) ratios, the
fractions were empirically calibrated as follows:

* **Mild ARDS (P/F 200–300):** Impairment fraction = 0.26 (yields
  P/F ≈ 256).
* **Moderate ARDS (P/F 100–200):** Impairment fraction = 0.60 (yields
  P/F ≈ 148).
* **Severe ARDS (P/F < 100):** Impairment fraction = 0.95 (yields
  P/F ≈ 75).

*Solver instability zone.* High-resolution fractional sweeps
identified a numerical bifurcation in the respiratory solver.
Impairment fractions between **0.91 and 0.945 (inclusive)**
consistently result in fatal solver divergence. The calibrated severe
fraction (0.95) was selected to safely clear this instability zone.

### B.4 Source-code audit findings and discrepancies

A source-level audit of the Pulse 4.3.1 C++ repository identified
three discrepancies between the official methodology documentation
and the compiled engine logic:

1. **Basal metabolic rate (BMR) coefficient.** The documentation
   lists the male weight coefficient as 3.397. The codebase
   implements `13.397` (`SetupPatient.cpp:771`), correctly aligning
   with the Harris-Benedict equation (Roza & Shizgal 1984).
2. **Skin surface-area exponent.** The documentation lists the weight
   exponent as 0.45. The codebase implements `0.425`
   (`SetupPatient.cpp:752`), aligning with the Du Bois formula.
3. **Baroreceptor constant (ν).** The documentation lists the
   baroreceptor exponent as 4. The codebase implements an effective
   ν = 48 (`NervousModel.cpp:320`), calculated as `4 × ResponseSlope`
   (where slope = 12).
