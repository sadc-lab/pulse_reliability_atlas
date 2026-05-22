---
header-includes:
  - \renewcommand{\arraystretch}{1.35}
---

# Pulse Reliability Atlas: first sensitivity, clamping, and divergence map for the Pulse Physiology Engine v4.3.1

**Author:** Santino Nanini

---

## Abstract

**Background.** The Pulse Physiology Engine (Kitware, Apache-2.0; v4.3.1)
is among the most-cited open-source whole-body human physiology
simulators. Its
developers state on the Pulse FAQ that no formal sensitivity analysis has
been performed on user-facing operational inputs. Prior external work
[@cornish2023] addressed intervention-outcome falsification on
MIMIC-III sepsis; the operational-input reliability question has remained
unaddressed.

**Methods.** We swept seven user-facing inputs (HR, SBP, DBP, RR, Vt,
FiO2, PEEP) from Pulse's verified acceptance ranges using Morris
elementary-effects sampling. The sweep spanned four scenarios (healthy
and three ARDS severities, spanning PALICC-2 mild–severe and bracketing
the 0.91–0.945 solver-instability zone) across two adult surrogates
(CDC weight-anchored male and female), yielding 1,280 total simulations. A
locked four-flag detector (`clamped` / `diverged` / `implausible` /
`not_steady_state`) classified every run before analysis.

**Results.** The headline operator-actionable result: VC-AC
(volume-controlled assist-control) tidal-volume instability appears in
20.6 % of runs (finding **F-004**), and is **causally identified as
patient-ventilator dyssynchrony at the inspiration trigger and corrected
by setting trigger pressure to −2 cmH2O** (median Vt CV collapses from
0.351 to 0.016; worst-case from 1.826 to 0.112). Sensitivity is
strongly skewed: 48 of 48 (cell × output) combinations have ≥ 50 % of
summed μ\* in their top-3 inputs (median 0.928), and the engine is
**predominantly linear** for these dominant parameters — point-estimate
σ/μ\* < 0.6 in 40 of 48 cells, and under trajectory-level bootstrap
31 of 48 cells (65 %) are CI-robustly linear (upper bootstrap CI
< 0.6); the remaining 17 cells have either bootstrap CI straddling
0.6 (12) or insufficient clean trajectories for a CI (5; FiO2-edge
cells in S1 and S4_F). Pulse rejects out-of-range inputs *loudly*:
0 of 1,280 runs fired the silent-clamping flag. Solver divergence is
sex-stratified — 20 of 1,280 runs (1.6 %) diverged, **all 20 male in
the input-extreme regime** (sex-stratification is regime-dependent;
§3.5.1). A second boundary finding (**F-003**): under the
preregistered 120 s window, Pulse PaO2 exceeds the locked classifier
upper bound of 600 mmHg at FiO2 = 1.0 in 34 of 126 implausibly-flagged
runs; an extended 300 s rerun ([S021](#s021)) shows PaO2 converges
to a plateau (median 643 mmHg in S1) that sits ~ 10 mmHg *below* the
simple alveolar-gas-equation prediction (≈ 653 mmHg) — consistent
with Pulse's modelled A-a gradient — supporting a transient-regime
explanation rather than a Pulse oxygenation overshoot. H4 (sex-specific
reliability) is partially supported under Benjamini–Hochberg FDR
control (q = 0.05): 5 of 24 cell × output Wasserstein distances
survive the within-sex null — all five are gas-exchange (PaCO2 ×3,
SpO2 ×1, PaO2 ×1). Cardiovascular and Vt sex effects do not exceed
within-sex sub-sampling; input-importance rankings are largely
preserved across sexes (Spearman ρ 0.75 – 1.00 in S2 / S3).

**Conclusion.** The atlas provides a per-cell traffic-light reliability
map for adult Pulse 4.3.1, identifies sex as a previously uncharacterized
reliability-sensitivity axis, yields one operator-actionable correction
(setting VC-AC inspiration trigger pressure to −2 cmH2O), delivers an
empirical Pulse-severity → P/F calibration table that lands Pulse's
ARDS defaults at Berlin band centers under ARDSnet-protective
ventilation, and provides a per-cell data-quality filter for downstream
machine-learning pipelines that train on Pulse-generated synthetic
cohorts.

---

## Reader's roadmap

*This paper is written for a cross-disciplinary readership — clinicians,
biomedical engineers, statisticians, machine-learning practitioners, and
generally curious scientific readers. The sections are organised so that
each can be entered independently.*

* **§1 — Introduction.** Why an open reliability atlas is needed for
  Pulse 4.3.1, the twelve verified engine limitations the atlas builds on,
  and the contribution catalogue. §1.4 explains the experiment-log tag
  system ([S001](#s001) – [S024](#s024)) used throughout.
* **§2 — Methods.** Engine wrapper, the seven swept operational inputs,
  the four scenarios × two patients design, Morris sampling, the
  four-flag detector (`clamped` / `diverged` / `implausible` /
  `not_steady_state`), the pilot gate, and the statistical-methods overview.
* **§3 — Results.** Per-cell flag breakdown (Table 1), Morris
  sensitivity rankings (H1), silent-clamping audit (H2), solver-divergence
  characterisation (H3), sex-specific comparison (H4), and the cell-level
  traffic-light reliability map (Figure 6).
* **§4 — Discussion.** Practical user guidance, implications for
  machine-learning pipelines that train on Pulse synthetic cohorts, a
  side-by-side mapping against Cornish et al. 2023 causal falsification
  (Table 2), explicit limitations (§4.5), and downstream research hooks.
* **§5 — Conclusion.** Short closing summary: headline contribution,
  operator-actionable F-003 / F-004 corrections in their final
  framings, the regime-dependent sex axis, and the PhD-pipeline
  placement.
* **Appendices.** Appendix A is the experiment-log index; Appendix B
  carries the pre-Atlas boundary characterisations (hard input gates,
  ARDS-severity calibration, source-code audit).

A skimmer wanting the headline can read the abstract, the *Key
contributions* below, Table 1, Figure 6, §4.5, and §5 (Conclusion).
A reader interested in reproducing or extending the work should
additionally read §2.6 (detector), §2.8 (reproducibility), and
Appendix A.

---

## Key contributions

*Seven artifacts a downstream Pulse user, ML practitioner, or device
developer can pick up and apply without re-running the 1,280-simulation
sweep.*

* **First open reliability atlas for Pulse v4.3.1** — a per-cell
  traffic-light map across 8 patient × scenario cells × 6 outputs
  (48 combinations, 1,280 simulations), released Apache-2.0 alongside
  the engine.
* **Operator-actionable VC-AC correction (F-004).** Tidal-volume
  instability in 20.6 % of runs is *causally identified* as
  patient-ventilator dyssynchrony at the inspiration trigger and
  *resolved* by setting trigger pressure to −2 cmH2O (median Vt
  coefficient of variation collapses 0.351 → 0.016; worst-case
  1.826 → 0.112).
* **Transient hyperoxia regime (F-003).** Under the preregistered 120 s
  window, Pulse PaO2 exceeds the locked classifier upper bound of
  600 mmHg at FiO2 = 1.0 in 34 implausibly-flagged runs (91 % at
  FiO2 ≥ 0.95). An extended 300 s rerun ([S021](#s021)) shows PaO2
  converges to a plateau ~ 10 mmHg *below* the simple
  alveolar-gas-equation prediction (S1 median 643 mmHg vs ≈ 653 mmHg
  predicted) — consistent with Pulse's modelled A-a gradient. The
  original flag therefore reflects (a) the locked 120 s window being
  insufficient for hyperoxia convergence and (b) the conservative
  classifier bound, not a Pulse oxygenation overshoot. A supplementary `HARD_BOUNDS_PHYSIOLOGICAL`
  reclassification (PaO2 upper 700 mmHg) is reported as a sensitivity
  analysis in §3.8.
* **Sex as a reliability-sensitivity axis** — the first sex-stratified
  reliability comparison in the Pulse literature. Under
  Benjamini–Hochberg FDR control (q = 0.05), 5 of 24 cell × output
  Wasserstein tests survive the within-sex null, *all five in
  gas-exchange channels*.
* **Sex-stratified solver-divergence cluster in the input-extreme regime.**
  20 of 1,280 runs (1.6 %) diverge, *all 20 on the male surrogate in the
  Morris input-extreme regime*; the complementary continuous-severity
  sweep at midrange inputs (§3.5.1) shows approximately sex-balanced
  divergence inside the [0.879, 0.945] band — the sex effect is
  regime-dependent. The [S006](#s006) cluster is mechanistically
  confirmed ([S018](#s018)) to be mediated by Pulse's
  `BloodVolumeBaseline` (male default 4,802.63 mL vs female default
  3,996.09 mL, a ~17 % gap): reducing the male surrogate's BV
  monotonically eliminates divergence
  (20 / 20 → 2 / 20 → 0 / 20 across BV = 4,802.63 → 4,400 → 4,082.24 mL).
  A separate engine-level finding (F-S018-A) is the per-surrogate BV
  floor at 4,082.24 mL that bounds how far the gap can be closed by a
  one-way transplant.
* **A reusable four-flag classifier**
  (`clamped` / `diverged` / `implausible` / `not_steady_state`) that
  future Pulse users can apply to their own scenario configurations
  without re-running this sweep.
* **Reusable ARDS-severity → P/F calibration table at ARDSnet ventilation.**
  Empirical mapping {0.26, 0.60, 0.95} lands Pulse's per-lung severity
  scalar at Berlin band centers (P/F ≈ 256 / 150 / 96 mmHg) under VC-AC +
  Vt 6 mL/kg + PEEP 10 + FiO2 0.4; Pulse's documented {0.3, 0.6, 0.9}
  defaults yield 199 / 150 / 119 mmHg at the same settings (vs. published
  340 / 130 / 50 mmHg, Webb 2020) — calibration is *ventilation-setting-dependent*.

---

## Notation and abbreviations

*Sixteen symbols and acronyms used throughout the paper. Defined here
so cross-disciplinary readers do not need to chase definitions through
the prose.*

| Symbol / acronym | Meaning |
|---|---|
| Morris EE | Morris *elementary effects* — a screening method that perturbs each input one at a time along randomised trajectories, producing per-input importance and non-linearity diagnostics. |
| μ\* | Mean of absolute elementary effects. Morris importance metric: larger μ\* means the input has a larger average influence on the output. |
| σ | Standard deviation of elementary effects across a Morris design. Proxy for *non-linearity and interactions*. |
| σ/μ\* | Linearity ratio. Values < 0.6 indicate a predominantly linear output response to that input over the swept range. |
| EE | A single elementary effect — one perturbation step in one Morris trajectory. |
| HR / SBP / DBP / MAP | Heart rate / systolic, diastolic, and mean arterial blood pressure (MAP derived as DBP + (SBP − DBP)/3). |
| RR / Vt / PEEP | Respiratory rate / tidal volume / positive end-expiratory pressure. |
| FiO2 | Inspired oxygen fraction (0 – 1). |
| PaO2 / PaCO2 / SpO2 | Arterial partial pressure of oxygen / arterial partial pressure of CO2 / peripheral oxygen saturation. |
| VC-AC / PC-AC | Volume-controlled and pressure-controlled assist-control ventilator modes. The atlas restricts to VC-AC. |
| ARDS | Acute Respiratory Distress Syndrome. |
| PALICC-2 | Pediatric Acute Lung Injury Consensus Conference, 2nd edition (severity framework). |
| V/Q | Ventilation–perfusion ratio. |
| BV | Blood volume (Pulse field `BloodVolumeBaseline`). |
| BH / FDR | Benjamini–Hochberg false-discovery-rate control at q = 0.05. |
| CV | Coefficient of variation — standard deviation divided by the mean — used here for steady-state Vt stability. |

---

## 1. Introduction

*This section frames the gap the atlas closes. Pulse 4.3.1's
developers state on the public FAQ that no formal sensitivity
analysis on user-facing operational inputs has been performed; this
paper produces that map. The introduction catalogues the twelve
verified engine limitations the atlas builds on, summarises the
contributions, and introduces the experiment-log tag system
([S001](#s001) – [S024](#s024)) used throughout.*

### 1.1 Motivation

*Why this paper exists. Pulse is widely used in clinical research,
medical-device development, and education, yet no public sensitivity /
clamping / divergence map of its user-facing operational envelope has
been published — every user re-encounters the same limitations
independently. This section sources that gap directly from the Pulse
FAQ and frames the atlas as the first open answer.*

The Pulse Physiology Engine [@bray2019] (Kitware, Apache-2.0)
is among the most-cited open-source whole-body human physiology
simulators. It provides a 0-dimensional lumped-parameter model of the
cardiovascular, respiratory, gas-exchange, and pharmacological
systems, and is used in three broad communities:

* **Clinical research** — virtual-patient cohorts for hypothesis
  generation when human data are unavailable, ethically constrained,
  or impractically expensive to collect (e.g. dual-patient ventilator
  sharing during the COVID-19 pandemic [@webb2020]).
* **Medical-device development** — early-stage validation of
  ventilators, pumps, and monitors against a virtual patient. Pulse's
  own ventilator-validation tables report ASL 5000-referenced
  tidal-volume errors of 0.07 – 2.25 % for VC-AC (volume-controlled
  assist-control) across healthy, restrictive, and obstructive lung
  profiles [@pulsevent]; the
  surrounding validation framework is described in [@webb2022vent].
* **Education** — anaesthesia, critical-care, and paramedic training
  curricula increasingly use Pulse for case-based simulation.

Despite this footprint, the engine's developers state explicitly on
the public Pulse FAQ [@pulsefaq; verified verbatim 2026-04-19, still
current as of the May 2026 GitLab re-audit, [S003](#s003) / [S016](#s016)]:

> "We have not performed a systematic forward propagation or inverse
> quantification of model uncertainty, nor have we conducted a formal
> sensitivity analysis."

The 2026 GitLab re-audit ([S016](#s016)) qualifies the FAQ claim slightly:
the repo carries a 2020 tag `STUDY_SENSITIVITY_ANALYSIS_1_0_0` with a
one-off Sobol study on internal vascular-circuit resistance multipliers
for model calibration. That study targets a different parameter class
(internal lumped-parameter resistors, not user-facing operational
inputs) and was not ported to the 4.3.x release line. Prior external work [@cornish2023]
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
* **Scenarios** spanning healthy adult and three ARDS severities,
  calibrated on the Berlin Definition's PaO2/FiO2 bands [@ards2012].
  PALICC-2 (Pediatric Acute Lung Injury Consensus Conference, 2nd
  ed.) [@emeriaud2023] is cited as the parallel pediatric severity
  framework; note that PALICC-2 itself favours Oxygenation Index
  (OI) / Oxygen Saturation Index (OSI) over P/F.
* **A four-flag classifier** that categorizes every run rather than
  discarding flagged ones (preregistration discipline per
  [@munafo2017]).

Four properties make this paper a methods-paper rather than a
findings-paper: (1) the entire pipeline is preregistered with
amendment history (per [@munafo2017]); (2) every quoted
number is reproducible from the canonical Morris sample (seed = 42)
plus the atlas Docker image, verified at three independent layers
([S007](#s007)); (3) the data are released under FAIR principles
[@wilkinson2016]; and (4) the four-flag classifier is a generic
instrument that future Pulse users can apply to their own
configurations without re-running our sweep.

The paper is the first publishable output in the maintainer's PhD
pipeline. Two downstream papers — pediatric translation layer (in
preparation, validation underway) and native pediatric Pulse fork
(planned) — both depend on knowing where adult Pulse is trustworthy.
This atlas is that prerequisite.

*Scope and limitations preview.* The atlas characterises adult
Pulse v4.3.1 under VC-AC ventilation across 7 operational inputs and
6 steady-state outputs, on two adult reference surrogates (male and
female) — the configuration most directly relevant to
critical-care research and medical-device validation. Pediatric
translation, alternative ventilator modes (PC-AC, PSV), and within-run
non-steady-state dynamics are *out of scope* by construction. The full
inventory of structural and methodological limitations — lumped-parameter
assumptions, single-trachea upper airway, no V/Q mismatch, no dicrotic
notch, and the practical implications for downstream pipelines — is
consolidated in §4.5.

### 1.2 Verified limitations of Pulse 4.3.1

*The twelve Pulse limitations the atlas is calibrated against, each
tied to a primary source (FAQ, source-code audit, or our own
boundary experiments — see [S003](#s003) / [S010](#s010) / [S016](#s016)). Two previously
asserted but unverified claims — FiO2 = 1.0 crashes the solver, and
Pulse has no sex-specific physiology — were withdrawn before
preregistration locked.*

Twelve limitations were verified against primary sources before the
preregistration was locked ([S003](#s003)).
This atlas adds quantitative coverage to those:

1. No formal SA / UQ on user-facing operational inputs — addressed by
   this paper. The 2020 `STUDY_SENSITIVITY_ANALYSIS_1_0_0` tag in the
   Pulse repository (Sobol on internal lumped-parameter circuit
   resistances for model calibration) addressed a different parameter
   class and has not been ported to 4.3.x; the FAQ statement remains
   current. Audit details in [S016](#s016).
2. BP clamping above SBP > 120 / DBP > 80 — verified empirically; locked
   sampler ranges respect this so it does not contaminate H2.
3. Adult-only (age ≥ 18 hard-gated in `SetupPatient.cpp`) — atlas restricted
   to two adult surrogates by design.
4. ARDS solver instability 0.91–0.945 — S4 (severity = 0.95) intentionally
   placed above the zone. See Appendix B.3 for the three-sweep
   characterisation and the empirical impairment-fraction calibration
   table.
5–6. HR init acceptance 50–110 / RR init acceptance 8–20 — sampler ranges
   match.
7. PC-AC over-delivers Vt 11.3 – 25.3 % across healthy / restrictive / obstructive lung profiles per Pulse's own validation tables [@pulsevent]; the surrounding validation framework is described in [@webb2022vent]. Companion experiments in `Pulse_translation_new` (entries #12 / #13) corroborate the *direction* — PC-AC over-delivers tidal volume in both sexes — but find a larger magnitude under different ventilator settings (female +58.9 % vs male +24.0 % at PIP = 20 cmH2O; see §2.3). The atlas restricts to VC-AC.
8–12. Structural lumped-parameter limits — discussed in §4.3.

The two previously asserted but unverified claims (FiO2 solver-divergence at 1.0 and
absence of sex-specific physiology) were withdrawn before the
preregistration locked. The atlas wrapper deliberately raises FiO2_MAX from
0.95 to 1.0 ([S004](#s004))
so the FiO2 = 1.0 boundary actually reaches Pulse rather than being
silently capped at the wrapper layer.

### 1.3 Contributions

*The five methodological contributions of the paper, in prose form:
the atlas itself, the four-flag classifier, Morris EE with bootstrap
CI, the first sex-specific comparison in the Pulse literature, and
the cell-level traffic-light reliability map. (See also the
artifact-focused 'Key contributions' bullet list near the top of the
paper, which highlights the same work as reusable deliverables.)*

* The first open reliability atlas for Pulse 4.3.1 across two patient
  surrogates and four scenarios.
* A four-flag classifier (`clamped` / `diverged` / `implausible` /
  `not_steady_state`) calibrated against real Pulse logs ([S004](#s004)) — every
  threshold locked before data collection (preregistration §Flags).
* Morris elementary-effects sensitivity with bootstrap-CI on μ\*
  (preregistered analysis plan; bootstrap CI is a post-hoc
  methodological enhancement, transparent in the preregistration
  amendment log, with no impact on hypothesis thresholds).
* Sex-specific comparison (Wasserstein, Spearman ρ on μ\* vectors) — the
  first such comparison in the Pulse literature.
* A traffic-light reliability map (green / yellow / red) per cell ×
  output, suitable for direct user consumption.

### 1.4 Experiment log nomenclature ([S001](#s001) – [S024](#s024))

*A one-line description of each of the 24 experiment-log entries
cited throughout the paper. Skim this table once to make every later
'S0xx' reference interpretable on first encounter; the full audit
trail lives in Appendix A and the underlying notebooks in the
repository.*

Throughout this paper we reference experiments by short tags of the
form **[S001](#s001), [S002](#s002), …, [S024](#s024)**. Each tag corresponds to a self-contained
lab-notebook entry under `experiments_log/santino/` that records the
*hypothesis, motivation, method, result, and interpretation* of one
discrete piece of work. The tags are introduced here so that any
reference in §2 – §4 to e.g. "[S005](#s005) pilot" or "[S014](#s014) trigger lockout"
is interpretable on first encounter. A compact one-line description
of every entry follows; the full audit trail is in Appendix A and the
underlying files are in the repository.

| Tag | One-line description |
|---|---|
| S001 | Docker + 3-parallel hardware smoke test (CPU/RAM budget). |
| S002 | Project bootstrap (repo layout, licensing). |
| S003 | Verified the 12 Pulse 4.3.1 limitations against primary sources. |
| S004 | Built the atlas Docker image; scenario smoke test; calibrated the detector clamp regex against real Pulse rejection logs. |
| S005 | 22-run pilot on cell (S1, M); passed all 5 preregistered gates. |
| S006 | Full 1,280-run Morris sweep (the headline experiment). |
| S007 | Targeted reproducibility check at three independent layers, all bit-exact. |
| S008 | Tier-1 statistical refinement (block bootstrap on σ, within-sex Wasserstein null, Spearman CI, divergence-input mechanism). |
| S009 | Tier-2 robustness (seed stability, continuous-ARDS micro-sweep, pytest suite, GitHub Actions CI). |
| S010 | Literature-review pass; every reference DOI / PMID-verified. |
| S011 | Sex-vs-mass disentangling experiment. |
| S012 | Steady-state window cross-output audit (does F-003 / F-004 contaminate other channels? — answer: no). |
| S013 | Lexical lockdown (manuscript taxonomy normalization). |
| S014 | Trigger-pressure lockout (causally identifies F-004 as VC-AC dyssynchrony). |
| S015 | Reproducibility and logic audit before publication. |
| S016 | Re-audit of the Pulse GitLab + literature (May 2026). |
| S017 | Cornish 2023 cross-mapping against the atlas's 6-output panel. |
| S018 | Blood-volume mechanism falsification (explains the all-male divergence cluster). |
| S019 | Sobol bolt-on draft script (ready-to-fire; not executed — see §3.3.1 for the closed-by-redundancy argument). |
| S020 | Pre-submission novelty audit; verified that every "first" / "novel" claim in the manuscript survives a literature double-check (single citation added: Figueroa-Casas & Montoya 2016 for the F-004 clinical precedent). |
| S021 | Hyperoxia convergence: 60-run pre-registered rerun at 300 s vs locked 120 s sweep window — tests whether F-003 PaO2 > 600 mmHg at FiO2 = 1.0 reflects oxygenation overshoot or transient non-convergence. |
| S022 | No-compute failure-mode attribution audit of the locked `not_steady_state` count (Appendix C). |
| S023 | Supplementary ML/SHAP cross-check of the Morris μ\* rankings on the clean subset (Supplementary §S11). |
| S024 | Pre-submission claims-ledger audit — `scripts/audit_claims.py` re-derives every Tier-1/Tier-2 quantitative claim in §3 / §4 / Appendix C from the canonical parquets/CSVs and verifies it against the manuscript text (190 / 190 PASS at the locked tolerance band). |

---

## 2. Methods

*This section is the engineering layer of the atlas: which Pulse
version, which inputs, which scenarios, which patient surrogates,
which Morris design, which flags. Every threshold, every range, and
every priority order was locked in the preregistration before the
1,280-run sweep launched.*

### 2.1 Engine and atlas wrapper

*The exact Pulse version, Docker image, and atlas wrapper layered on
top — including the deliberate raising of `FiO2_MAX` from 0.95 to 1.0
so the upper boundary actually reaches Pulse rather than being silently
capped at the wrapper layer. Pinned image hashes and the
version-pinning rationale appear at the end so any future reader can
reproduce the sweep bit-exactly.*

* Pulse 4.3.1 (Kitware, Apache-2.0).
* Atlas-local Docker image `pulse-atlas-engine` built from
  `engine/Dockerfile` (FROM `kitware/pulse:4.3.1`). The wrapper at
  `engine/run_atlas_engine.py` is a fork of
  `Pulse_translation_new/engine/run_validation_engine.py` with two
  documented changes (see §2.6 and [S004](#s004)):
  1. `FIO2_MAX` raised 0.95 → 1.0 (justified by PhD experiment E20, April
     2026: 9-run probe, no Pulse solver-divergence at FiO2 = 1.0).
  2. Recording-relative time origin ([S005](#s005)): wrapper now subtracts the
     ventilator-settle time so emitted `time_s` starts at 0, allowing the
     locked steady-state window [60, 120] s to capture data.

**Pinned image hashes (reproducibility).** Two `pulse-atlas-engine`
image hashes are relevant for full reproducibility:

* `3b18bdc08660` — produced the original 1,280-run Morris sweep at
  `data/runs/full_sweep/` ([S006](#s006), 2026-04-26).
* `b2e0e807803d` — produced the [S015](#s015) audit re-execution and includes
  the [S014](#s014) SDK sed-patch (`InspirationPatientTrigger*` fall-through
  guard, 2026-04-28).

[S015](#s015) Phase 2 verified 40 / 40 reproduction-consistent CSVs under the
rebuilt `b2e0e807803d` image (38 clean runs bit-exact; 2
originally-diverged runs reproduce divergence with the same
`exit_code = 1`). The [S014](#s014) patch is therefore a verified no-op for the
original sweep, and the atlas's published numbers apply identically
under either image hash. Upstream pin: `kitware/pulse:4.3.1`
(`REL_4_3_2`, the current upstream `stable` head, is build-system-only;
physiology unchanged per [S016](#s016) GitLab audit 2026-05-07).

A source-level audit of the Pulse 4.3.1 C++ repository conducted
alongside the wrapper work revealed three undocumented deviations
between the official methodology pages and the compiled engine logic
— a BMR coefficient, a skin surface-area exponent, and an effective
baroreceptor constant that all differ from the public documentation.
The compiled values are physiologically defensible (they align with
Harris–Benedict and Du Bois), but the documentation gap matters for
anyone reproducing Pulse from its published equations rather than its
source. Full audit detail and source-line citations are in
Appendix B.4.

**Version-pinning rationale.** This atlas is pinned to Pulse 4.3.1.
The current upstream `stable` head, `REL_4_3_2` (released 2025-08-12),
differs from 4.3.1 by 7 files (+46 / −17 lines) covering build-system
changes only; no physiology, validation, patient-setup, or solver
code changed, verified by source audit in [S016](#s016) (2026-05-07). Atlas
numerics therefore apply identically to 4.3.2. While future releases
will inevitably alter underlying physiology, the atlas's methodology
— the four-flag classifier, Morris sweep, and traffic-light map — is
engine-version-agnostic and designed to be re-applied to any future
Pulse release.

### 2.2 Inputs

*The seven user-facing operational inputs and the verified acceptance
ranges they were swept over. MAP is *derived* from SBP and DBP rather
than swept independently, to avoid redundant sampling and constraint
violation. The DBP / SBP ≤ 0.75 ratio is enforced at the scenario
builder, not the sampler, so Morris geometry stays intact for
elementary-effects computation.*

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

*Input-ranges table — at a glance.*
**What:** the 7 user-facing operational inputs swept by Morris, their
ranges (units), and the verification source for each acceptance window.
**How to read it:** each row is one Morris-sampled input; the range
column lists the [min, max] interval; the source column points at the
boundary probe (E10 / E28 / E29 / E20) or literature reference that
established the range.
**Key takeaway:** all 7 ranges sit *inside* Pulse's verified acceptance
envelope by construction — so no Morris point should ever silently
clamp, a claim §3.4 (H2) confirms empirically (0 / 1,280 clamp events).

MAP is *derived* from SBP / DBP, never sampled independently
(preregistration amendment 2026-04-22).

The DBP / SBP ≤ 0.75 ratio is enforced *at the scenario builder*
(`src/scenario.clip_dbp_to_pulse_constraint`), not at the sampler, so
Morris geometry stays intact for elementary-effects computation. Both the
requested DBP (Morris coordinate) and the applied DBP (post-clip, sent to
Pulse) are persisted in the master Parquet.

### 2.3 Scenarios and patients

*The 4 scenarios × 2 patient surrogates = 8 cells of the atlas.
Healthy and three ARDS severities, calibrated on the Berlin
definition's PaO2 / FiO2 bands and bracketing Pulse's 0.91 – 0.945
solver-instability zone, each run on the male and female reference
bodies. Ventilator mode is VC-AC only — the configuration
Pulse's own validation table reports as most accurate (0.07 – 2.25 %
Vt error vs PC-AC's 11.3 – 25.3 %).*

Four scenarios × two patients = 8 cells:

* **S1** Healthy ventilated adult, ARDS impairment 0.00.
* **S2** Mild ARDS, impairment 0.26 (PALICC-2 mild).
* **S3** Moderate ARDS, impairment 0.60.
* **S4** Severe ARDS, impairment 0.95 (above the 0.91–0.945 solver-
  instability zone documented in `Pulse_translation_new` E6/E10).

**Impairment-fraction calibration.** Pulse modulates ARDS via a
per-lung `Severity` scalar in [0, 1]. The Atlas's scenarios use
`Severity` = 0.0 (S1, healthy), 0.26 (S2, mild), 0.60 (S3, moderate),
and 0.95 (S4, severe) rather than Pulse's documented {0.3, 0.6, 0.9}
defaults [@pulserespmethod]. The Pulse-team peer-reviewed COVID-19
multiplex paper [@webb2020] reports verbatim that these severity
defaults produce P/F ratios of 340 / 130 / 50 mmHg respectively
(quoted as Pulse's published validation, not as an independent
measurement). The companion Respiratory Methodology page
[@pulserespmethod] documents the severity-to-modifier mapping
calibrated at 0.3 / 0.6 / 0.9 but does not state these P/F values
directly; the quantitative validation claim is anchored on
[@webb2020] alone (citation attribution corrected in pre-submission
Phase-2 audit, [S020](#s020) follow-up). Under
the ARDSnet-protective ventilation regime that the Atlas sweep is
built around (VC-AC, Vt = 6 mL/kg, PEEP = 10 cmH2O, FiO2 = 0.4),
direct measurement of the documented mapping in a 28-run impairment
sweep (`Pulse_translation_new` E6) produced P/F ratios of
199 / 150 / 119 mmHg — leaving Pulse's "mild" fraction (0.3) at the
moderate / mild boundary and its "severe" fraction (0.9) well inside
the Berlin moderate band. The empirically calibrated mapping
{0.26, 0.60, 0.95} used here was selected to land at Berlin band
centers (P/F ≈ 256 / 150 / 96 mmHg) under the same ventilation
settings. The calibration is therefore *ventilation-setting-dependent*
rather than a global correction; Pulse's documented mapping may
reproduce its claimed P/F values under different Vt / PEEP / FiO2
combinations, but does not at ARDSnet-protective settings. Full
contrast table, ventilation-setting disclosure, three-source
convergence for the 0.91 – 0.945 solver-instability zone, and the
E6 calibration provenance are in Appendix B.3.

* **Male reference surrogate:** age 18, weight 67.3 kg, height 180 cm (BMI 20.8).
* **Female reference surrogate:** age 18, weight 56.2 kg, height 163 cm (BMI 21.1).

*Provenance.* Body weights are the CDC 50th-percentile weight-for-age
values at 18 years (67.29 kg boys, 56.23 kg girls; CDC growth-chart
tables, <https://www.cdc.gov/growthcharts/>), inherited unchanged from
the companion `Pulse_translation_new` pediatric-translation pipeline
where they form the 18-year endpoint of its CDC progression. The
female height (163 cm) is the CDC P50 stature for 18-year-old girls.
The male height (180 cm) is a researcher-fixed rounded value chosen
to yield a healthy baseline BMI of 20.8; this is ≈ 3 cm above the CDC
P50 and is reported here transparently rather than retro-fitted to a
citation. The full engine-source comparison — including Pulse's
own internal `heightStandardMale_cm` / `heightStandardFemale_cm`
constants — is in Appendix B.5.

NHANES P50 anchors further confirm the surrogates' *vital-sign* profile
(not their body dimensions) is representative of healthy adults: median
HR 70 bpm (M) / 74 bpm (F), SBP 118 mmHg (M) / 113 mmHg (F), DBP 70
mmHg (M) / 69 mmHg (F). Companion verification
(`Pulse_translation_new` E12, E13) established that the female
surrogate produces physiologically plausible engine output across all
four scenarios, independent of the Atlas sweep.

Ventilator: VC-AC (volume-controlled assist-control) only — the
ventilator delivers a fixed tidal volume on a set schedule while
still allowing the patient to trigger additional breaths between
mandatory cycles. The mode choice is justified by Pulse's own
validation tables [@pulsevent] reporting VC-AC tidal-volume errors
of 0.07 – 2.25 % across healthy, restrictive, and obstructive lung
profiles vs PC-AC's 11.3 – 25.3 %; the surrounding ASL 5000
validation framework is described in [@webb2022vent]. Companion
verification (`Pulse_translation_new` E12, E13) further found
that PC-AC over-delivery scales inversely with body weight (female
+58.9 % vs male +24.0 % at PIP = 20 cmH2O), reinforcing the
preregistration's VC-AC restriction.

### 2.4 Simulation cadence

*Temporal sampling decisions: 120 s simulation, 5 s CSV sample
interval, locked steady-state window [60, 120] s — 13 points per
clean run, enough resolution to compute steady-state mean, variance,
drift, and flatline diagnostics for the detector without storing
high-frequency time-series.*

120 s simulation, sample interval 5 s, steady-state window [60, 120] s
(13 points). Detector enforces 13 points / clean run.

### 2.5 Morris sampling

*Why Morris elementary effects is the right screening method here: it
ranks inputs by overall importance (μ\*) and flags non-linearity (σ)
at a small fraction of the cost of a full variance-based analysis.
Implementation uses SALib's `morris.sample(N=20, num_levels=4,
seed=42)` → 160 unique input points, identical across cells so
elementary-effect rankings are directly comparable.*

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

*The four orthogonal flags that classify every run: `clamped` (Pulse
silently bent the input), `diverged` (NaN / Inf / exit code ≠ 0),
`implausible` (steady-state mean outside hard physiological bounds),
and `not_steady_state` (flatline, drift, or excess variance). All
thresholds were locked in preregistration before data collection,
with priority order `clamped > diverged > implausible >
not_steady_state > clean` for primary-flag analyses.*

**Why this priority order.** The four flags trace the chronology of
failure modes a Pulse simulation could exhibit, from input handling
through solver execution to output evaluation against biological and
dynamic criteria:

1. **`clamped` — input-contract breach.** Pulse has silently
   substituted at least one setup input. The simulation no longer
   corresponds to the Morris grid point that was requested, so any
   downstream flag would refer to a different input than the one
   being studied. Disqualifying the run at this layer is
   non-negotiable; this is why `clamped` outranks every other flag.
2. **`diverged` — mathematical failure.** The solver could not
   produce a complete, finite output trajectory: non-zero exit code,
   NaN / Inf in the CSV, missing CSV, or simulation truncated before
   the recorded window ends. No biological interpretation is
   possible because there is nothing to interpret.
3. **`implausible` — biological failure.** The mathematics ran
   cleanly but the steady-state mean falls outside the hard
   physiological bounds (`HARD_BOUNDS` table below): the output is
   mathematically valid but biologically incompatible with a viable
   60 s steady-state — e.g. SpO2 = 0.40, which on the Severinghaus
   1979 dissociation curve corresponds to PaO2 ≈ 22 mmHg, below the
   cellular oxygen-extraction threshold.
4. **`not_steady_state` — dynamic failure.** The output is
   mathematically valid and biologically coherent, but the
   trajectory has not settled in the 60 s window: flatline at a
   bound, excess variance (CV > 5 %), or drift exceeding the per-channel
   `DRIFT_MAX_DELTA_60S` thresholds (table below). The result is
   interpretable as a *transient*, not as steady-state physiology.

The order is therefore the order in which a simulation lifecycle
could fail (input handling → solver → biology → dynamics), and is
preregistered in `preregistration.md` §Flags. Each flag's underlying
thresholds and their clinical anchors are described in the two
tables below.

Four flags locked in preregistration §Flags; thresholds calibrated on real
Pulse runs without modifying preregistration thresholds (only one
amendment, 2026-04-22-b, tightened the flatline-bound tolerance from 1 % →
0.1 % BEFORE any atlas data was collected). Clamp regex empirically
calibrated against an SBP = 140 boundary probe in [S004](#s004); the over-broad
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

**Hard physiological bounds for the `implausible` flag.** The table
below was committed in `preregistration.md` §Flags before any atlas
data was collected, and is reproduced here for reader convenience.
Each `(lower, upper)` pair encodes one of three logical categories:
(a) a physical / thermodynamic ceiling for which no citation is
needed because the bound is definitional, (b) an equipment /
engineering limit, or (c) a clinical *"incompatible with a 60 s
steady-state in the locked window"* threshold. Only category (c) is
a judgment call within the cited literature; categories (a) and (b)
follow directly from physics or hardware specs.

| Output | Lower | Upper | Source (lower / upper) |
|--------|------:|------:|------------------------|
| HR (bpm)    |  20 |  220 | Survival-incompatibility thresholds for bradycardia / tachycardia [@marino2013icu Ch.5; @marini2019critical Ch.1] |
| MAP (mmHg)  |  30 |  180 | Lower: Sepsis-3 organ-perfusion failure threshold (well below 65 mmHg shock target) [@singer2016; @evans2021sepsis]; upper: ESH 2023 hypertensive emergency [@mancia2023esh] |
| Vt (mL)     |  50 | 1500 | Lower: below anatomical dead space (~150 mL adult) [@west2020respiratory Ch.2] — alveolar ventilation impossible; upper: ~4× ARDSnet protective ventilation (6 mL/kg PBW [@brower2000] ≈ 400 mL for atlas surrogates) and at the edge of adult-ventilator delivery capability [@marino2013icu Ch.26] |
| SpO2 (%)    |  50 |  100 | Lower: oxyhemoglobin dissociation curve P50 (SpO2 = 50 % ↔ PaO2 ≈ 27 mmHg [@severinghaus1979]) — below cellular oxygen extraction threshold [@marini2019critical Ch.1]; upper: hemoglobin saturation ceiling (definitional) |
| PaO2 (mmHg) |  20 |  600 | Lower: SpO2 ≈ 0.30 on the Severinghaus 1979 dissociation curve [@severinghaus1979] — incompatible with cellular respiration over a 60 s steady-state window, well inside Berlin severe-ARDS oxygenation territory [@ards2012]; upper: classifier-conservative choice below the alveolar-gas-equation ceiling [@west2020respiratory Ch.5] — supplementary `HARD_BOUNDS_PHYSIOLOGICAL` sensitivity analysis at 700 mmHg reported in §3.8 |
| PaCO2 (mmHg) | 10 |  120 | Profound respiratory alkalosis (lower) and CO2 narcosis (upper) survival thresholds [@marino2013icu Ch.21; @west2020respiratory Ch.4] |

The bound is therefore a *time-window-conditional* operational
threshold, not a raw biology threshold: a real patient transiently
crossing PaO2 = 18 mmHg during cardiac arrest is biologically
possible, but a Pulse simulation reporting a 60 s steady-state mean
PaO2 = 18 mmHg at FiO2 = 0.21 on a *resting healthy adult* indicates
that the engine has produced an output incompatible with the
simulation's own input setup. The `implausible` flag isolates that
class of inconsistency. Within category (c), the exact numerical
choice (e.g., PaO2 lower 20 vs 25 mmHg) is a defensible judgment
call rather than a unique biological constant; §4.5 acknowledges
this and §3.8 demonstrates the sensitivity-analysis pattern on the
single most contestable bound (PaO2 upper, raised from 600 to 700
mmHg per the alveolar-gas-equation ceiling). No locked threshold has
been adjusted post-hoc — the only preregistration amendment
(2026-04-22-b, flatline tolerance 1 % → 0.1 %) was made *before* the
sweep launched.

**Drift thresholds for the `not_steady_state` flag.** The
`DRIFT_MAX_DELTA_60S` constant in `src/detector.py` complements the
hard bounds above: it sets the maximum tolerated `|Δ| = |slope × 60 s|`
that a channel may exhibit across the final 60 s of the steady-state
window before the run is flagged `not_steady_state` for drift. These
are *clinical-meaningfulness* thresholds — beyond them, a bedside
clinician would read the trajectory as actively changing rather than
at homeostasis. They are atlas-internal calibration choices rather
than biological limits, so the per-channel magnitudes are anchored in
standard critical-care monitoring practice
[@marino2013icu Ch.5, Ch.21, Ch.26; @marini2019critical Ch.1] rather
than in mortality-incompatibility primary literature.

| Output | Drift threshold per 60 s | Clinical-meaningfulness anchor |
|--------|--------------------------|--------------------------------|
| HR     | 5 bpm                    | Threshold for a clinically "meaningful" tachy / brady excursion under continuous bedside monitoring [@marini2019critical Ch.1] |
| MAP    | 5 mmHg                   | Lower edge of what a clinician would call ongoing hemodynamic instability vs settled perfusion [@singer2016; @evans2021sepsis] |
| Vt     | 50 mL                    | ~ 1 mL/kg PBW on the atlas surrogates — within the noise band of breath-to-breath measurement at ARDSnet Vt [@brower2000] |
| SpO2   | 2 percentage points      | One bedside-monitor display step; conventional "noteworthy" desaturation threshold over a 60 s window [@severinghaus1979; @marino2013icu Ch.26] |
| PaO2   | 15 mmHg                  | Roughly one Berlin P/F band (e.g., 80 → 95 mmHg at constant FiO2) per minute — clinically meaningful oxygenation change [@ards2012] |
| PaCO2  | 5 mmHg                   | Roughly one alveolar-ventilation step under ARDSnet protective ventilation per minute — clinically meaningful CO2 change [@west2020respiratory Ch.4] |

These thresholds are evaluated on an OLS linear regression of the 13
sample points in the [60, 120] s window (5 s sample interval); only
`|slope × 60 s|` gates the flag (the R² of the fit is logged as
diagnostic metadata but does *not* trigger anything). Two further
`not_steady_state` triggers (the coefficient-of-variation threshold
`CV_THRESHOLD = 0.05` and the flatline-at-bound criterion
`std/|mean| < 0.01` **AND** mean within 0.1 % of a hard bound) are
documented in `src/detector.py` and `preregistration.md` §Flags. SpO2
is reported by Pulse as a fraction in [0, 1], so the listed drift
threshold of "2 percentage points" corresponds to `0.02` in the code
constant.

Atlas-side input validation in `src/scenario.py` is restricted to
scenario and sex keys; physiological-bound enforcement is delegated to
the locked Morris sampler ranges (§2.2), Pulse's setup-time rejection
(captured by the `clamped` flag), and the detector's `implausible`
hard-bound check on the steady-state mean. This three-layer
defense-in-depth contract was verified end-to-end in
[S015](#s015).

### 2.7 Pilot gate ([S005](#s005))

*The five preregistered gates the 22-run pilot on cell (S1, M) had to
pass before the full 1,280-run sweep launched: success rate, detector
self-consistency, 13-point steady-state window, clamp-regex
reachability, and Pulse determinism. The pilot also surfaced and
resolved three pipeline bugs before the compute budget was spent.*

A 22-run pilot on cell (S1, M) with 16 unique Morris points + 4
reproducibility reruns + 2 deliberate clamp probes verified all five
preregistered gate criteria: success rate, detector self-consistency,
13-point steady-state window, clamp regex reachability (probes), and Pulse
determinism (1e-6 relative tolerance across 24 (output × rerun)
comparisons). Pilot also surfaced and resolved three pipeline bugs (time-
origin, case_id collision, G4 unreachability from locked Morris ranges)
*before* the full sweep launched.

### 2.8 Hardware and reproducibility

*The laptop hardware envelope (i5-11400H, 8 GB RAM, no GPU), the 2–3
parallel Docker throughput verified in [S001](#s001), and the eleven
independent verification points that make the published numbers
reproducible bit-exactly. A pre-submission Phase-4 re-execution
(1,280 / 1,280 runs) extends bit-exact reproduction from the
[S015](#s015) 40-run audit to the full envelope.*

i5-11400H (6 physical / 12 logical cores), 8 GB RAM, no GPU. Docker
allocation 3.95 GB / 12 CPU. Two-to-three parallel containers per the
verified [S001](#s001) budget. Pulse is bit-exact deterministic for fixed
inputs ([S005](#s005) G5). Wall time for the full sweep ≈ 7 h on this hardware.

The atlas's published numbers have eleven independent verification
points (Pulse determinism, pipeline + analysis correctness, and
independent reproducibility layers) detailed in
[Supplementary S10](../preprint/supplementary.md#s10);
all eleven passed with zero violations. [S007](#s007) deliberately rejected a
full 1,280-simulation re-execution because re-running the same code
gives identical CSVs by construction and cannot detect bugs in the
code being re-run; the independent-layer approach catches strictly
more error classes at ~ 1 % of the compute cost.

**Phase-4 audit-driven re-execution (2026-05-16 → 2026-05-18).** As a
pre-submission belt-and-braces check on top of the eleven verification
points above, two complementary re-executions were performed under the
current `pulse-atlas-engine` image (hash `b2e0e807803d`, the
post-[S014](#s014)-patch rebuild — a different image hash than the
`3b18bdc08660` build that produced the canonical sweep on 2026-04-26):

* **(i) Phase 4a — same-seed full re-execution.** All 1,280 runs of the
  canonical Morris sweep were re-executed from the locked sample
  (`data/runs/full_sweep/morris_sample.parquet`; `seed=42`,
  `trajectories=20`, `levels=4`) against the current image, with output
  written to a parallel directory tree (`data/runs/full_sweep_repro/`)
  so the canonical artifact was not touched. Wall time: **23 h 01 m** on
  the maintainer's i5-11400H laptop at 2 parallel Docker workers — the
  verified-safe hardware cap (§2.8). SHA-256 comparison of every
  `output.csv` against canonical gave **1,260 / 1,280 bit-identical
  clean runs and 20 / 20 originally-diverged runs reproducing
  divergence with `exit_code = 1`** (i.e. the same 20-run male-extreme
  cluster that §3.5 attributes to the blood-volume mechanism). **Zero
  deviations, zero clean-↔-diverged asymmetries, zero missing files.**
  The [S015](#s015) audit's 40-run bit-exact result is therefore extended to
  the full 1,280-run envelope, and the [S014](#s014) SDK sed-patch is
  empirically a no-op on the canonical sweep at every cell. Full report
  in `data/runs/full_sweep_repro/sha_compare.json`.

* **(ii) Phase 4b — new-seed Morris stability on cell (S2, M).** A
  fresh Morris sample at `seed=44`, `trajectories=20`, `levels=4` (160
  unique points, matching canonical sample size; different seed from
  both canonical `seed=42` and the prior [S009](#s009) stability check at
  `seed=43, trajectories=10`) was run on the moderate-ARDS male cell.
  Wall time: 1 h 34 m. **The dominant input by μ\* was preserved for
  all 6 outputs**, and top-3 input sets matched canonical in 4 / 6
  outputs (top-3 orders in 3 / 6); disagreements were confined to the
  position-3 tertiary input where μ\* magnitudes are similar across
  competing inputs — consistent with the trajectory-bootstrap CI
  reported in §3.3.1 and the Spearman ρ analysis in §3.6.
  In full transparency, two sample-dependent quantities surfaced:
  **(a)** the S2_M divergence count went from 4 / 160 (canonical
  `seed=42`) to 7 / 160 (`seed=44`), with all 7 new-seed divergences
  in the same low-HR + low-SBP + high-FiO2 regime that §3.5 / §3.5.1
  identify as the input-driven mechanism — i.e. the *regime* is
  preserved while the *count* is sample-dependent, exactly as the
  manuscript's regime-vs-count nuance predicts; and **(b)** the
  PaO2 σ / μ\* point estimate on FiO2 moved from 0.667 (canonical, in
  the §3.3.1 Group-B "promote" set) to 0.547 (new-seed, below the
  preregistered 0.6 trigger), empirically confirming the §3.3.1
  closed-by-redundancy argument: the point-estimate trigger is
  bootstrap-borderline, no cell is CI-robustly nonlinear, and the
  Sobol bolt-on adds no evidential weight. Per-run timings,
  `phase4b_morris_S2M_seed44.parquet`, and the top-3 comparison are
  in `results/`.

Neither phase falsified a manuscript claim. Phase 4a strengthens the
determinism statement to the full sample size; Phase 4b empirically
confirms the bootstrap-CI-aware story §3.3.1 already tells.

**Programmatic manuscript-numbers audit ([S024](#s024), 2026-05-22).**
Independently of the bit-exact re-execution above, a third
verification layer closes the data-integrity loop at the *manuscript*
level. The read-only Python script
[`scripts/audit_claims.py`](../scripts/audit_claims.py) registers
every Tier-1 (Abstract, Key Contributions, hypothesis verdicts,
Table 1, Figure 6 traffic-light) and Tier-2 (per-cell numbers in §3.3
/ §3.4.1 / §3.5 / §3.6 / §3.8 / §3.8.1, plus Appendix C and §4.5
S023) quantitative claim as a `Claim` record (manuscript value,
source artifact, computed value, tolerance rule), re-derives the
computed value from the canonical parquets / CSVs / JSON summaries,
and verifies the manuscript text against each computed value under
an explicit per-class tolerance band (`exact_int` for integer counts;
`pct_1dp` / `pct_whole` for percentages at their displayed precision;
`displayed_1dp` / `displayed_2dp` / `displayed_3dp` for floats at
their displayed precision; a 1 × 10⁻⁹ IEEE-754 epsilon protects
against half-precision rounding boundaries). The current report on
the locked manuscript is **190 / 190 PASS, 0 WARN, 0 FAIL**. The
script exits non-zero on any FAIL and is therefore CI-ready: future
manuscript edits that drift a quoted number against its source
artifact will fail the script's exit code. Full audit method and the
per-row claim ledger are in
[`experiments_log/santino/S024_claims_ledger_audit.md`](../experiments_log/santino/S024_claims_ledger_audit.md).

### 2.9 Using the four-flag classifier independently

*The minimal public API for re-using the four-flag classifier on
someone else's Pulse output, without re-running the atlas sweep.
Future Pulse users can import `src.detector.classify`; thresholds and
steady-state-window constants are module-level so they can be
overridden in a wrapper module rather than by editing the classifier
itself.*

The detector is a stand-alone instrument; any Pulse user can apply it
to their own output CSVs without re-running the atlas sweep. Calling
contract for `src/detector.py`:

```python
# Public API; thresholds locked per §2.6.
from src.detector import classify

result = classify(
    csv_path="path/to/pulse_output.csv",  # Pulse 5 s-sampled CSV
    pulse_log=open("pulse.log").read(),   # stdout + stderr text
    exit_code=0,                          # container exit code
)

# result is a DetectorResult with four orthogonal flags.
print(result.clamped.fired,         result.clamped.reason)
print(result.diverged.fired,        result.diverged.reason)
print(result.implausible.fired,     result.implausible.reason)
print(result.not_steady_state.fired, result.not_steady_state.reason)

# Priority order:
#   clamped > diverged > implausible > not_steady_state > clean
print(result.primary_flag)
```

Hard physiological bounds (`HARD_BOUNDS`), drift thresholds
(`DRIFT_MAX_DELTA_60S`), the CV threshold (`CV_THRESHOLD = 0.05`,
computed as `numpy.std(ddof=0) / |mean|` — population-std divisor on
the 13-point steady-state window; `src/detector.py:338`), and the
steady-state window (`STEADY_STATE_T_LO = 60 s`, `STEADY_STATE_T_HI
= 120 s`) are module-level constants exposed at the top of
`src/detector.py` and locked in `preregistration.md` §Flags. To apply
the classifier to a sweep at a different operational envelope (e.g.
pediatric ranges or different ventilator modes), override these
constants in a wrapper module rather than editing `detector.py` in
place; the preregistration discipline (lock thresholds before data
collection) should transfer to any downstream sweep that uses this
instrument.

### 2.10 Statistical methods overview

*A plain-language definition of every statistical tool used in §3
(Results) and §4 (Discussion) — Morris EE, block bootstrap, Sobol
(preregistered but closed-by-redundancy; see §3.3.1), 1-Wasserstein
distance, the within-sex sub-sampling null, Spearman ρ, BH-FDR
control, and Hoeffding / Holm–Bonferroni (external; used by Cornish
2023, §4.4). First appearance of each test in §3 is therefore
immediately interpretable.*

Several distinct statistical tools are used in §3 (Results) and §4
(Discussion). We define each here in plain language so the first
appearance of a test name in the results section is immediately
interpretable. Implementation references and bibliographic details
are in §9.

* **Morris elementary effects (μ\*, σ).** A *screening* sensitivity
  method: it ranks inputs by their average absolute effect on an output
  (μ\*) and flags inputs whose effect varies a lot across the input
  space (σ, suggesting non-linearity or interactions). Cheap compared
  with full variance-based methods, well suited to "which inputs
  matter at all?" questions. Detailed in §2.5; see [@morris1991;
  @campolongo2007].

* **Block bootstrap (trajectory-level resampling).** A non-parametric
  way to attach a confidence interval (CI) to a statistic computed
  from data with internal structure. Instead of resampling individual
  data points (which would break correlations within a Morris
  trajectory), we resample whole *trajectories* with replacement and
  recompute the statistic on each resample (1,000 resamples here).
  The 2.5 / 97.5 percentiles of the resampled statistics give a 95 %
  CI. Used in §3.3.1 to put a CI on σ / μ\* and decide whether
  apparent non-linearity is signal or noise.

* **Sobol variance-based decomposition.** A *quantitative* sensitivity
  method that splits the variance of an output into contributions
  from each input (first-order index S₁) and from each input's
  interactions with all others (total-order index S_T). It is more
  informative than Morris but costs roughly an order of magnitude more
  simulations. We preregistered a conditional Sobol bolt-on if Morris
  flagged non-linearity, and discuss in §3.3.1 why the bootstrap
  evidence renders that bolt-on statistically redundant here.

* **1-Wasserstein distance.** A distance between two probability
  *distributions* on a one-dimensional output. Intuitively: the
  minimum "work" needed to transport one histogram onto the other,
  in the output's natural units (e.g. mmHg, mL, bpm). Larger value
  = more separation; zero means the two distributions are identical.
  Used in §3.6 to quantify how different male vs female clean-run
  output distributions actually are.

* **Within-sex sub-sampling null (permutation-style).** A reference
  distribution built by randomly splitting the *combined* M + F clean
  runs into halves the same size as the original M and F groups, then
  computing the same Wasserstein distance on the split (n = 2,000
  splits). The empirical p-value p_emp is the fraction of nulls that
  exceed the observed M-vs-F distance. The logic: if sex actually
  matters, the observed M-vs-F distance should be larger than what
  random sub-sampling of the *same* population produces; if it sits
  inside the null, the apparent sex effect is sample-size noise.

* **Spearman's rank correlation ρ.** Measures whether two paired
  rankings agree (ρ = 1: identical ordering; ρ = 0: no monotonic
  relationship; ρ = −1: reversed ordering). Used in §3.6 on the
  M and F vectors of μ\* values (one entry per input) to ask whether
  both sexes order the seven inputs the same way. We attach a
  paired-input bootstrap 95 % CI by resampling the seven inputs with
  replacement and re-ranking.

* **Benjamini–Hochberg (BH) false-discovery-rate (FDR) control.** A
  multiple-comparisons correction. When many tests are run (here, 24
  Wasserstein tests on 6 outputs × 4 scenarios), the naive α = 0.05
  threshold over-counts significant results. BH-FDR sorts the p-values
  ascending and accepts the k-th smallest if it is below k · q / N,
  where N is the number of tests and q is the target false-discovery
  rate (we use q = 0.05). Result: the *expected* fraction of false
  positives among the rejected null hypotheses is at most q. Less
  conservative than Bonferroni; standard in genomics and increasingly
  in physiology-simulation work.

* **Hoeffding's inequality and Holm–Bonferroni (external; Cornish
  2023).** Used by [@cornish2023] in their causal-falsification
  framework. *Hoeffding's inequality* gives a distribution-free
  confidence interval for the mean of a bounded random variable from a
  finite sample; the interval is wide but assumption-light. *Holm–
  Bonferroni* is a step-down family-wise-error-rate (FWER)
  correction stricter than BH-FDR — it controls the probability of
  *any* false positive across the test family rather than the expected
  fraction. We reference these only when discussing Cornish's
  channel-by-channel results in §4.4; the atlas itself does not use
  them.

---

## 3. Results

*This section reports the headline numerical outputs of the
1,280-run sweep: the per-cell flag breakdown, Morris μ\* sensitivity
rankings, the four hypothesis tests (H1 – H4), and the cell-level
reliability traffic light. Each subsection corresponds to one
bounded result rather than to one experimental phase.*

*All numerical results are sourced from `results/` artifacts and
auto-updated when the analysis script re-runs.*

### 3.1 Per-cell flag breakdown (Table 1)

*The headline counts: how many runs in each of the 8 cells fired each
of the four flags, and how many were clean. Flag columns are
*independent* presence counts (one run can fire several flags), so
row sums can exceed `n_total`; `primary_flag` resolves runs to a
single category via the §2.6 priority order.*

```{=latex}
\begin{center}
\begin{tabular}{lrrrrrr}
\toprule
Cell & n\_total & clamped & diverged & implausible & not\_steady\_state & clean \\
\midrule
S1\_M & 160 & 0 & 4 & 11 & 107 & 49 \\
S1\_F & 160 & 0 & 0 & 23 & 118 & 42 \\
\midrule
S2\_M & 160 & 0 & 4 & 0  & 69  & 87 \\
S2\_F & 160 & 0 & 0 & 0  & 68  & 92 \\
\midrule
S3\_M & 160 & 0 & 4 & 0  & 12  & 144 \\
S3\_F & 160 & 0 & 0 & 0  & 38  & 122 \\
\midrule
S4\_M & 160 & 0 & 8 & 46 & 44  & 67 \\
S4\_F & 160 & 0 & 0 & 46 & 74  & 60 \\
\bottomrule
\end{tabular}
\end{center}
```

*Table 1.* Per-cell flag counts. The flag columns (`clamped`, `diverged`,
`implausible`, `not_steady_state`) are **independent presence counts**: a
single run can fire `implausible` and `not_steady_state` simultaneously and
is counted in both columns. Only `clean` is mutually exclusive of the four
flags. Row sums therefore exceed `n_total` (e.g. S1_F sums to 183) when
runs trigger multiple non-priority flags. The detector's *primary flag*
follows the priority order `clamped > diverged > implausible >
not_steady_state > clean` (§2.6) and is recorded as `primary_flag` in the
master Parquet for partition-style analyses.

*Table 1 — at a glance.*
**What:** per-cell counts of the four detector flags and `clean`
across the 8 (scenario, sex) cells (160 runs each).
**How to read it:** flag columns are *independent* presence counts —
one run can fire several flags simultaneously, so row sums can exceed
`n_total` (e.g. S1_F sums to 183); the §2.6 priority order
`clamped > diverged > implausible > not_steady_state > clean`
resolves each run to a single `primary_flag` for partition-style
analyses.
**Key takeaway:** `clamped` = 0 across the entire sweep (H2 NOT
supported); `diverged` is all-male (H3 supported, with
sex-stratification); `implausible` concentrates in S1 (F-003 transient
hyperoxia regime — PaO2 above the locked classifier bound at FiO2 = 1.0,
shown by [S021](#s021) to converge into the physiological band by 300 s)
and S4 (severe hypoxemia); 663 / 1,280 (51.8 %) runs are `clean`.

* `clamped` is **0 across the entire sweep** (locked ranges respect
  Pulse acceptance — H2 not supported).
* `diverged` is **all-male** (H3 supported, with sex stratification).
* `implausible` is concentrated in S1 (FiO2 = 1.0 transient hyperoxia
  regime, F-003 — see §3.8) and S4 (severe hypoxemia at the lower
  physiological bound: PaO2 < 20 mmHg or SpO2 < 50 % in some Morris
  combinations).
* `not_steady_state` is highest in S1 (107 + 118) — VC-AC Vt is
  unstable on healthy adults (F-004) — and lowest in S3 — moderate
  ARDS dampens oscillation. S4 not-steady-state rate climbs again as
  severe-impairment dynamics dominate.
* The total clean count is **663 / 1,280 (51.8 %)**.

*Figure 1 (`fig01_flag_summary`) — at a glance.*
**What:** stacked bar chart of run counts per detector flag, faceted
by the 8 (scenario, sex) cells (160 runs each). Visual counterpart
to Table 1.
**How to read it:** each bar is one cell; segment colours give counts
of `clean` and the four flag classes. Flag categories are
*independent* presence counts so a single run can appear in several
segments.
**Key takeaway:** the gradient from S1 → S4 in `not_steady_state` and
`implausible` is the primary operational-envelope map the atlas
claims as its first deliverable; `clamped` is empty everywhere.

![Figure 1. Per-cell flag breakdown — stacked bars of run counts per detector flag, faceted by the 8 (scenario, sex) cells (n = 160 per cell). Flag categories are independent presence counts (one run can fire several flags); `clean` is mutually exclusive of the four flag classes. The S1 → S4 gradient in `not_steady_state` and `implausible` is the primary operational-envelope map of the atlas. Source: `results/cell_flag_summary.csv` (S006).](../figures/fig01_flag_summary.png)

### 3.2 Morris sensitivity (Figures 2 a–f)

*The Morris μ\* heatmaps per output — which inputs dominate which
outputs in which cells. Four visual patterns emerge: cardiovascular
outputs are cardio-driven, gas-exchange outputs are ventilator-driven,
FiO2 sensitivity collapses in severe ARDS as shunt physiology
dominates, and output Vt tracks input Vt at μ\* ≈ 500 mL across every
cell.*

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
  is dominated by Vt in most cells, consistent with the
  alveolar-ventilation identity
  $\dot{V}_A = \mathrm{RR} \cdot (V_T - V_D)$
  (where $\dot{V}_A$ is alveolar minute ventilation, RR is set
  respiratory rate, $V_T$ is delivered tidal volume, and $V_D$ is
  the anatomical dead-space volume; West *Respiratory Physiology*
  Ch. 2 convention). SpO2 is also ventilator-driven but at a tiny
  absolute scale (μ\* ≤ 0.13) because the output sits at the
  hemoglobin saturation ceiling.
* **The ARDS gradient is visible.** PaO2's FiO2 sensitivity peaks in
  S2 (μ\* = 133 – 147 mmHg), remains substantial in S3 (μ\* = 84 – 93
  mmHg), and *collapses* in severe ARDS (μ\* = 31 in (S4, M)). Pulse
  correctly captures the regime where shunt physiology pins PaO2
  regardless of FiO2 — a textbook ARDS finding, captured by the engine
  without explicit programming.
* **Output Vt tracks input Vt at μ\* ≈ 500 mL** in every cell — by
  far the largest μ\* in the atlas. In VC-AC mode, asking Pulse for a
  500 mL tidal volume produces close to a 500 mL delivered tidal
  volume, cell-invariant. The cells where this coupling is disrupted
  are the F-004 dyssynchrony runs (§3.8).

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

*Figures 2 a–f (`fig02_morris_mu_star_<output>`) — at a glance.*
**What:** six heatmaps (HR, MAP, Vt, SpO2, PaO2, PaCO2) of Morris μ\*
across inputs × cells.
**How to read it:** rows are the seven swept inputs; columns are the
8 (scenario, sex) cells (S1_M … S4_F); colour intensity is the
magnitude of the mean absolute elementary effect, i.e. the input's
average influence on that output. Bootstrap 95 % CIs on each μ\* are
recorded in `results/morris_indices.parquet` but elided from the
heatmaps for legibility.
**Key takeaway:** in every cell, 1 – 3 inputs dominate each output —
the diagonal pattern visually supports H1's "skewed sensitivity"
claim (formal test in §3.3).

![Figure 2a — Morris μ\* heatmap, HR. Rows are the 7 swept inputs, columns are the 8 (scenario, sex) cells; colour intensity is the mean absolute elementary effect. Source: `results/morris_indices.parquet` (S006).](../figures/fig02_morris_mu_star_HR.png)

![Figure 2b — Morris μ\* heatmap, MAP. Same layout as 2a. Source: `results/morris_indices.parquet` (S006).](../figures/fig02_morris_mu_star_MAP.png)

![Figure 2c — Morris μ\* heatmap, Vt delivered. Same layout as 2a. Source: `results/morris_indices.parquet` (S006).](../figures/fig02_morris_mu_star_Vt.png)

![Figure 2d — Morris μ\* heatmap, SpO2. Same layout as 2a. Source: `results/morris_indices.parquet` (S006).](../figures/fig02_morris_mu_star_SpO2.png)

![Figure 2e — Morris μ\* heatmap, PaO2. Same layout as 2a. Source: `results/morris_indices.parquet` (S006).](../figures/fig02_morris_mu_star_PaO2.png)

![Figure 2f — Morris μ\* heatmap, PaCO2. Same layout as 2a. Source: `results/morris_indices.parquet` (S006).](../figures/fig02_morris_mu_star_PaCO2.png)

### 3.3 H1 — skewed sensitivity (PASS, 48 / 48)

*The first hypothesis test: in every cell × output combination, do
the top-3 inputs account for at least 50 % of summed μ\*? Answer —
yes, 48 / 48, median 0.928. Section 3.3.1 then addresses the
preregistered Sobol bolt-on and explains why CI-aware bootstrap
evidence closes it by redundancy.*

Top-3 fraction of summed μ\* per cell × output:
* All 48 combinations are ≥ 0.5 (the preregistered threshold).
* Median 0.928; range 0.658 – 0.998.
* Lowest fractions are in S4 (severe ARDS), and concentrate on the
  gas-exchange outputs PaO2 and SpO2: S4_F SpO2 (0.658), S4_M SpO2
  (0.703), S4_F PaO2 (0.707), S4_M PaO2 (0.727). Mechanism: at 95 %
  alveolar impairment the dominant shunt fraction caps FiO2's marginal
  effect on arterial oxygenation, so the residual sensitivity
  redistributes across PEEP, RR, and Vt rather than concentrating on a
  single dominant input.

The dominant inputs by output (μ\* summed across all 8 cells, top 3 per
output — `src.analysis_morris.dominant_inputs_per_output` on
`results/morris_indices.parquet`):

| Output | Top-3 inputs (by summed μ\*) |
|--------|------------------------------|
| HR     | hr, fio2, peep              |
| MAP    | sbp, dbp, hr                |
| Vt     | vt, rr, fio2                |
| SpO2   | fio2, vt, peep              |
| PaO2   | fio2, peep, rr              |
| PaCO2  | vt, rr, fio2                |

*Top-3-inputs table — at a glance.*
**What:** the three most influential inputs (by Morris μ\*) for each of
the 6 atlas outputs, ranked by μ\* summed across the 8 (scenario, sex)
cells.
**How to read it:** each row is one output; the three inputs listed are
those with the largest cumulative mean absolute elementary effect in the
canonical Morris sample, ordered by summed μ\*.
**Key takeaway:** cardiovascular outputs (HR, MAP) are *cardio-input
dominated*; gas-exchange outputs (SpO2, PaO2, PaCO2) are
*ventilator-driven* — exactly the physiologically expected pattern,
which supports Pulse's input-output mapping in clean cells.

Cardiovascular outputs (HR, MAP) are dominated by their direct cardio
baselines; gas-exchange outputs (SpO2, PaO2, PaCO2) are dominated by
ventilator settings. This is physiologically sensible and supports the
overall correctness of Pulse's input-output mapping in the *clean*
operational region.

*Figure 3 (`fig03_h1_top3_fraction`) — at a glance.*
**What:** heatmap of the top-3 fraction of summed μ\* per cell × output
(48 combinations).
**How to read it:** colour palette is RdYlGn with the crossover at
0.5 (the preregistered H1 threshold); cells above 0.5 (green-side)
support skewed sensitivity, cells below (red-side) would not.
**Key takeaway:** all 48 combinations exceed 0.5 (median 0.928, range
0.658 – 0.998); H1 passes 48 / 48 across the full atlas.

![Figure 3. H1 — top-3 fraction of summed μ\* per cell × output (48 combinations). Heatmap with RdYlGn palette, crossover at 0.5 (the preregistered H1 threshold). Lowest fractions are in S4 (severe ARDS) gas-exchange outputs (S4_F SpO2 0.658; mechanism: shunt-fraction caps FiO2's marginal effect). Source: `results/h1_top3_fraction.csv` (S006).](../figures/fig03_h1_top3_fraction.png)

### 3.3.1 Sobol bolt-on: preregistered decision

*Why a Sobol bolt-on was preregistered.* Morris elementary effects
rank inputs by their average influence (μ\*), but they cannot tell us
*how much* of that influence comes from non-linearity or input–input
interactions. The σ / μ\* ratio is the standard proxy: large values
flag cells where the response is non-linear or interaction-driven,
and where a more expensive variance-based analysis (Sobol) would be
informative. The preregistered protocol (preregistration §Sampling
method) committed in advance: if any top-ranked input exhibited σ / μ\*
≥ 0.6 in any cell, we would run Sobol on it.

Applying this rule to the dominant input per (scenario, sex, output)
cell, **8 of 48 cells fire the trigger.** Manual inspection separates
these into two regimes:

* **Group A — noise-dominated (2 of 8 cells).** The dominant input's
  μ\* sits at numerical-noise level because the output is pinned at
  physiological saturation. Both are SpO2 in healthy patients: (S1, F,
  SpO2, PEEP) with μ\* = 0.0037 and σ = 0.0068, and (S1, M, SpO2, Vt)
  with μ\* = 0.028 and σ = 0.023. SpO2 in the healthy respiratory
  envelope sits at ≈ 0.997 — the hemoglobin saturation ceiling — so
  the Morris elementary effects are floating-point fluctuation, not
  physiological signal. The σ / μ\* ratio is mathematically high but
  physiologically empty.

* **Group B — known nonlinear physiology (6 of 8 cells).** Four of
  these are the FiO2 → PaO2 cells in ARDS scenarios: (S2 / S3, M / F,
  PaO2, FiO2), with μ\* in the 84 – 147 mmHg range and σ / μ\* between
  0.64 and 0.94. This is the regime where venous admixture caps
  oxygenation gain per FiO2 increment — an established physiological
  non-linearity (shunt-fraction kinetics). The remaining two cells
  reflect minute-ventilation coupling on PaCO2: RR → PaCO2 in healthy
  males ((S1, M), σ / μ\* = 0.87), and Vt → PaCO2 in severe-ARDS
  females ((S4, F), σ / μ\* = 0.66). Both are predicted by the
  alveolar-ventilation identity
  $\dot{V}_A = \mathrm{RR} \cdot (V_T - V_D)$ that governs CO₂
  elimination.

**CI-aware re-evaluation of the trigger.** The 8 / 48 promotion count
above is a *point* estimate. To attach a confidence interval to it,
we resampled trajectories (block bootstrap, 1,000 resamples, same
RNG seed as the μ\* CI) and recomputed σ / μ\* on each resample.
Per-cell `sigma_lo` / `sigma_hi` columns are persisted in
`results/morris_indices.parquet`. Under this bootstrap, the 48 cells
distribute into four buckets:

* **CI-robust *non-linear*: 0 / 48 cells.** No cell's *lower*
  bootstrap CI bound on σ / μ\* sits at or above 0.6 — i.e. no cell
  satisfies the trigger when evaluated at full evidential weight.
* **CI-robust *linear*: 31 / 48 cells (65 %).** Upper bootstrap CI
  bound on σ / μ\* strictly below 0.6.
* **Straddles 0.6: 12 / 48 cells.** Their non-linearity classification
  is bootstrap-borderline. Eight are the point-estimate "promote"
  cells (Groups A + B above). The other four are *point-estimate-below*
  but *upper-CI-above* 0.6: two PEEP-edge cells in (S4, F): PaO2 and
  SpO2; two FiO2-on-SpO2 cells in (S2_M, S3_M).
* **No estimable CI: 5 / 48 cells.** Three lie in S1_F where the
  dominant input is Vt — the Vt one-at-a-time (OAT) step has only
  one clean trajectory pair (S1_F × {PaCO2, PaO2, Vt}). Two lie in
  S4_M where the dominant input is FiO2 — the FiO2 OAT step has
  only one clean trajectory pair (S4_M × {PaO2, SpO2}). The
  *which-input-lacks-pairs* differs between the two groups (Vt in
  S1_F vs FiO2 in S4_M); per-input gaps are summarised at cell level
  in §4.3 / §4.5 limitations.

*Methodological note (σ / μ\* CI formula).* The upper CI bound
reported in the bucketing above is σ_hi / μ̂\*, where σ_hi is the
upper 97.5-percentile of the trajectory-level block bootstrap on σ
(1,000 resamples; implementation: `_block_bootstrap_sigma_ci` in
`src/analysis_morris.py`). The μ̂\* in the denominator is the point
estimate, treated as fixed. A fully ratio-aware bootstrap — one
that resamples trajectories and recomputes σ_b / μ\*_b *jointly*
per draw — yields a slightly different decomposition (30 / 48
CI-robustly linear under that formula). The qualitative conclusion
is unchanged either way: **zero cells are CI-robustly non-linear
under either formula.**

**The Sobol bolt-on is statistically redundant under the CI-aware
evidence.** *In one sentence: the trigger that was supposed to
motivate Sobol does not survive its own confidence interval.* The
preregistered trigger σ / μ\* ≥ 0.6 was designed to flag cells whose
non-linearity is *evidentially* established — not cells whose point
estimate merely happens to land above threshold. The trajectory-level
bootstrap above resolves the trigger at full evidential weight.
**Zero of the 48 cells satisfy the trigger CI-robustly:** no cell has
a *lower* bootstrap CI bound on σ / μ\* at or above 0.6. Of the
remaining cells, 31 are CI-robustly linear, 12 straddle 0.6, and 5
have no estimable σ / μ\* CI (the FiO2- and Vt-edge cells described
above).

Running a variance decomposition on cells whose non-linearity-trigger
status is *itself* bootstrap-borderline cannot tighten the evidential
picture. Sobol S₁ / Sₜ indices on cells that are not CI-robustly
non-linear would simply quantify the proportion of an
already-bootstrap-noise-dominated variance.

The interaction structure on the 6 Group B cells is additionally
*a priori* established by respiratory physiology: shunt-fraction
kinetics on PaO2, and the alveolar-ventilation identity
$\dot{V}_A = \mathrm{RR} \cdot (V_T - V_D)$ on PaCO2. Both are qualitatively recovered by
the Morris main-effect rankings reported in §3.2. A quantitative
Sobol decomposition would re-derive the same ordering at
substantially higher compute cost.

The preregistered Sobol bolt-on is therefore **closed by redundancy,
not by compute-shortage.** A reviewer or practitioner who wants the
variance decomposition anyway will find a ready-to-fire SALib
implementation in
[`scripts/s019_sobol_bolton.py`](../scripts/s019_sobol_bolton.py) —
N = 256, 6 Group-B cells, ~14 k Pulse runs, cluster-friendly. The
script consumes the canonical Morris sample
(`data/runs/full_sweep/morris_sample.parquet`) and the atlas Docker
image ([S006](#s006)), writes per-cell S₁ / Sₜ tables, and is verified to
produce the same sample-grid that this paper's deferral argument
references. The downstream analysis pipeline is preserved in
`src/analysis_morris.py`.

### 3.4 H2 — silent clamping rate (NOT supported, 0 / 1,280)

*The second hypothesis test: does Pulse silently clamp out-of-range
inputs at setup? Answer — no, zero silent clamps across the entire
sweep. Pulse rejects out-of-envelope inputs *loudly*, with explicit
`[ERROR]` log lines and exit code 1 (confirmed by the [S005](#s005)
deliberate clamp probes).*

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
   probes in [S005](#s005) confirmed this: SBP = 140 produces an explicit `[ERROR]`
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

*Compensatory-tachycardia table — at a glance.*
**What:** for each scenario, the input HR range that Morris sampled
versus the output HR mean ± std that Pulse actually returns at steady
state.
**How to read it:** the input range is fixed at [50, 110] bpm across
all scenarios; the gap between that range and the output mean
quantifies the engine's compensatory reflex gain.
**Key takeaway:** in S3 / S4 the output HR sits at 145 – 160 bpm
despite inputs drawn from [50, 110] — a ~60 bpm sympathetic overshoot
driven by Pulse's baroreceptor / chemoreceptor reflex, not a numerical
artefact.

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

*The third hypothesis test: are solver divergences sex-stratified?
Answer — partially. In the [S006](#s006) input-extreme regime, all 20 / 20
divergences are male and zero female, with the asymmetry
mechanistically confirmed ([S018](#s018)) to be mediated by Pulse's
`BloodVolumeBaseline` gap on the two surrogates — male default
4,802.63 mL vs female default 3,996.09 mL, a ~17 % difference — and
with a separate F-S018-A side-finding that Pulse enforces a
per-surrogate BV floor (4,082.24 mL on this male body) which bounds
how far the gap can be closed by a one-way transplant. In the §3.5.1
continuous-severity regime at midrange inputs, divergence is
approximately sex-balanced inside the [0.879, 0.945] band — so the
original sex effect varies with *what is varying*, not sex per se.*

20 / 1,280 runs (1.6 %) diverged. **All 20 are in male cells.**

**Input-combination signature.** The 20 divergence events are not
spread uniformly across the input space — they cluster on a specific
input pattern. Of the 20:

* **HR = 50** (the locked low boundary) appears in 16 / 20 runs.
* **SBP = 90** (locked low boundary) appears in 16 / 20 runs.
* **DBP = 67.5** (= 0.75 × 90, the post-clip value) appears in 16 / 20.
* **RR = 20** (locked high boundary) appears in 16 / 20 runs.
* **FiO2 = 1.0** appears in 13 / 20.
* The 16 shared cases correspond to **the same 4 Morris sample
  indices repeated across S1 / S2 / S3 / S4_M** — `run_idx` 119, 157,
  158, 159 in the canonical sample.
* The remaining 4 are unique to (S4, M), at `run_idx` 24 / 82 /
  137 / 138. They form a mixed cluster: one HR at 110 bpm, three at
  90 bpm; two Vt at 300 mL, one at 633 mL, one at 800 mL. This is a
  *partial second regime* — one the locked Morris sample explores
  only at the most severe ARDS impairment.

The signature reads cleanly: **low cardiovascular output (low HR +
low SBP) combined with high respiratory drive (high RR + high FiO2)
on the male reference surrogate** drives Pulse to a numerical edge
case. The compound input is *clinically plausible* — a hypotensive,
tachypneic, fully oxygenated patient, recognizable as a septic /
pre-arrest configuration — and sits inside Pulse's verified
acceptance ranges. Users should treat this corner of the envelope
as fragile when running the male surrogate.

**Mechanism candidate (Pulse source audit).** Pulse's
`SetupPatient.cpp` computes blood-volume baseline as
`computedBloodVolume_mL = 65.6 × weight_kg^1.02`. Verified against
the engine's setup log on the atlas sweep, this gives
**4,802.63 mL** for the male reference surrogate (67.3 kg) and
**3,996.09 mL** for the female (56.2 kg) — a ~17 % difference.
(Pulse logs both values at setup time on every run.)

Several other parameters are sex-conditional: ideal-body-weight
(Devine formula coefficient 50.0 vs 45.5), fat-fraction standard
(0.21 vs 0.28), height bounds (151 – 176 cm vs 163 – 190 cm). Among
these, the BV gap is the most plausible candidate for the divergence
asymmetry. It enters the cardiovascular circuit's stabilisation
directly, and shifts the operating-point neighborhood between the
two sexes.

**Mechanism confirmed ([S018](#s018), 2026-05-13).** *In one sentence:
forcing the male surrogate's BV down to the female-equivalent range
eliminates the divergence cluster.* We re-executed the 20
originally-diverged male inputs, this time injecting an explicit
`BloodVolumeBaseline` override via
`SEPatient.get_blood_volume_baseline().set_value(mL)`. The atlas
wrapper was extended to accept an optional `baselines.blood_volume_ml`
field for this purpose. Pulse logs the resolved BV at setup, so every
override is verifiable post hoc from `pulse.log`. The protocol used
two override points to map a dose-response curve:

| Override BV (mL) | Reduction vs default | Diverged | Implausible | not_steady_state | Clean |
|------------------|----------------------|----------|-------------|------------------|-------|
| 4,802.63 (default, original sweep) | 0 %  | 20 / 20 | n/a (no CSV) | n/a    | 0      |
| 4,400  | 8.4 %  | **2 / 20** | 1 / 20 | 8 / 20 | 10 / 20 |
| 4,082.24 (Pulse-stated floor on this surrogate) | 15.0 % | **0 / 20** | 1 / 20 | 8 / 20 | 12 / 20 |

*BV-override dose-response table — at a glance.*
**What:** outcomes for the 20 originally-diverged male inputs when
re-executed with an explicit `BloodVolumeBaseline` override at three
levels (default 4,802.63 mL → 4,400 mL → 4,082.24 mL, the
Pulse-stated floor on this surrogate).
**How to read it:** each row is one BV override level; columns count
the four detector outcomes plus `Clean` across the 20 reruns.
**Key takeaway:** divergence rate falls *monotonically* with BV
reduction — 20 / 20 → 2 / 20 → 0 / 20 — mechanistically confirming
that the all-male divergence cluster is mediated by Pulse's
blood-volume baseline.

The divergence rate falls *monotonically* with BV reduction. The
mechanism is therefore confirmed: the all-male divergence cluster is
mediated by the engine's blood-volume baseline.

Severe-ARDS / FiO2 = 1.0 inputs require deeper BV reduction to clear.
The two cases still divergent at 4,400 mL are both S4_M with
FiO2 = 1.0; the milder inputs are already clean at 4,400 mL.

**A separate engine-level finding (F-[S018](#s018)-A** in
[`S018_blood_volume_falsification.md`](../experiments_log/santino/S018_blood_volume_falsification.md)**)
emerged from the same test: Pulse hard-enforces a per-patient BV
floor at setup.** For the male reference surrogate (67.3 kg, 180 cm,
age 18, sex Male), the floor sits at **4,082.24 mL**. Setting
`BloodVolumeBaseline` below this triggers an explicit `[ERROR]` and
exit 1: *"Patient blood volume baseline … is too low. Hypovolemia
must be modeled by adding/using a condition."*

A practical consequence for sex-comparison experiments: the
female-computed BV (3,996.09 mL) sits 86 mL *below* the male floor.
The two surrogates therefore cannot be made BV-equivalent by a
one-way transplant — the strongest BV-only reduction Pulse will
accept on the male surrogate is 4,082.24 mL (a 15.0 % reduction
from default).

The eight `not_steady_state` classifications at both BV brackets are
concentrated in S1_M / S2_M. They reflect input-profile incoherence
on the 16 shared Morris indices: HR = 50 + RR = 20 + SBP = 90 on
healthy lungs is physiologically inconsistent. BV reduction lifts
the *divergence* flag but exposes the *underlying oscillatory
regime* — the inputs were always going to misbehave, and the BV
change just makes the misbehaviour visible at a different flag.

The all-S4_M unique inputs (`run_idx` 24 / 82 / 137 / 138) run clean
at both brackets. These are the four runs where input
low-cardiac-output + high-respiratory-drive is clinically coherent
(septic ARDS pattern); once BV is reduced, Pulse solves them without
complaint.

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

*Per-cell diverged-counts table — at a glance.*
**What:** the number of diverged runs in each of the 8 (scenario, sex)
cells, with the same 160 Morris input points submitted to every cell.
**How to read it:** scenarios on rows, separated by sex; the diverged
column is the `diverged` column of Table 1, isolated for direct
sex comparison.
**Key takeaway:** male cells diverge at 4 – 8 runs each (3.1 %
overall); female cells, run on the *identical* input grid, never
diverge in this regime — the first quantitative sex-specific
reliability finding for Pulse 4.3.1.

The same 160 Morris input points were submitted to both M and F cells.
Patient bodies: M = 67.3 kg / 180 cm; F = 56.2 kg / 163 cm. Same
physics engine, same condition string, same ventilator settings. The
only difference is patient mass / height / sex flag.

Yet the divergence rate is **2.5 % in S1_M, S2_M, and S3_M** (4 / 160
each), **5.0 % in S4_M** (8 / 160), and **0 % in every female cell**.
The overall male rate is 20 / 640 = 3.1 %; the female rate is 0 / 640.

This is the first quantitative sex-specific reliability finding for
Pulse 4.3.1, and is consequential for any device-validation pipeline
that uses Pulse as a virtual patient. **All 20 divergences occur on
the male surrogate; the female surrogate, run on the *identical*
input grid, never diverges within the locked envelope.** The
diverged-run input combinations are catalogued in
`results/diverged_grid.parquet` (a 2-D heatmap of divergence rate
per input-pair × cell).

H3 is therefore **partially supported** with a stronger qualifier:
a divergence regime exists outside the documented 0.91 – 0.945 ARDS
zone *and* the regime is sex-conditioned.

### 3.5.1 Continuous-severity divergence regime (Tier-2 follow-up)

The [S006](#s006) sweep used four fixed ARDS severities. A complementary
200-run sweep at continuous severity (Tier-2 follow-up,
[S009](#s009))
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

*Continuous-severity divergence table — at a glance.*
**What:** divergence counts per ARDS-severity bin in a 200-run
continuous-severity micro-sweep at midrange inputs (HR 80, SBP 105,
DBP 70, RR 14, Vt 550, FiO2 0.6, PEEP 10).
**How to read it:** each row is one severity bin; F-diverged and
M-diverged columns show divergences per sex (denominators differ
because runs distribute non-uniformly across severities).
**Key takeaway:** divergences concentrate in `[0.879, 0.945]` —
wider than the previously reported `[0.91, 0.945]` zone — and are
approximately sex-balanced at midrange inputs. The original [S006](#s006)
"all-male divergences" claim is therefore *regime-specific*
(Morris-extreme inputs), not a global sex effect on solver reliability.

Two refinements of the literature picture:

1. **The instability band is wider than previously reported.** The
   `Pulse_translation_new` E6 audit reported an instability zone at
   `[0.91, 0.945]`. Our continuous sweep at midrange inputs places
   the band at `[0.879, 0.945]` — the lower edge moves down by 0.031,
   extending the band on the low side by about 90 % of the original
   E6 width. The discrepancy is consistent with input dependence: E6
   used ventilator settings tailored to ARDS calibration; the atlas's
   midrange settings reach instability earlier.

2. **The [S006](#s006) sex-stratification is regime-dependent.** In the
   continuous-severity sweep (midrange inputs), the divergences are
   approximately balanced (F = 19, M = 14), with F diverging at
   *lower* severities (0.879 onwards) and M continuing into
   `[0.91, 0.945]`. So the original [S006](#s006) claim "all 20 male
   divergences" is a property of the *input-extreme + 4-scenario*
   combination, not a global sex effect on solver reliability.

The atlas therefore distinguishes **two separate divergence regimes**:

* **Input-driven regime** ([S006](#s006)): male reference surrogate at low HR
  + low SBP + high RR + FiO2 = 1.0. ~ 5× higher than female.
  Mechanism candidate: ~17 % blood-volume difference (§3.5, computed
  as (4 802.63 − 3 996.09) / 4 802.63 against the male default).
* **Severity-driven regime** ([S009](#s009)): both sexes, midrange inputs,
  severity in the band `[0.879, 0.945]`. F slightly higher overall;
  F earlier in the band, M later. Mechanism: solver-stability
  gradient at the high-impairment compliance edge.

Together these regimes give a more honest H3 picture: divergence
exists, it is partially sex-conditional, but the sex effect varies
by *what is varying* (Morris-extreme inputs vs ARDS severity), not
sex per se.

### 3.6 H4 — sex-specific reliability (partially supported, gas-exchange only)

*The fourth hypothesis test: do male and female trajectories differ
at the cell level? Answer — partially. Under Benjamini–Hochberg FDR
control (q = 0.05), 5 of 24 cell × output Wasserstein distances
survive — *all five on gas-exchange channels* (PaCO2 × 3, SpO2 × 1,
PaO2 × 1). Cardiovascular and Vt distances fall within the within-sex
sub-sampling null; input-importance rankings are largely preserved
across sexes (Spearman ρ 0.75 – 1.00 in S2 / S3).*

H4 is reported with two complementary statistics, each answering a
different question.

*How different are the output distributions?* The **1-Wasserstein
distance** quantifies the absolute magnitude of the M-vs-F gap on
clean-run output distributions, expressed in the output's natural
units (mmHg, bpm, mL).

*Do both sexes prioritise the same inputs?* **Spearman's ρ (rho)**
is a rank correlation between the M and F Morris μ\* vectors. ρ = 1
means identical input ordering; ρ = −1 means inverted; intermediate
values mean partial agreement.

Both statistics need a null reference: raw point estimates on this
sample size would overstate precision.

**Wasserstein distance with within-sex null.** The observed value is
the M-vs-F distance on clean runs. The reference null is built by
repeatedly splitting the *combined* M+F clean runs randomly into
halves of the original sizes (n_null = 2,000 splits).

```{=latex}
\begin{center}
\begin{tabular}{llrrrrc}
\toprule
Scenario & Output & M-vs-F & null p50 & null p95 & p\_emp & Sig.? (BH-FDR) \\
\midrule
S1 & HR    & 5.02  & 3.91  & 8.56  & 0.305 &   \\
S1 & MAP   & 0.58  & 1.38  & 2.78  & 0.995 &   \\
S1 & Vt    & 21.4  & 34.4  & 76.6  & 0.798 &   \\
S1 & SpO2  & 0.008 & 0.004 & 0.010 & 0.123 &   \\
S1 & PaO2  & 11.0  & 12.6  & 28.4  & 0.598 &   \\
S1 & \textbf{PaCO2} & \textbf{4.69} & 1.65 & 3.56 & \textbf{0.009} & * \\
\midrule
S2 & HR    & 1.91  & 3.60  & 7.72  & 0.958 &   \\
S2 & MAP   & 0.88  & 1.03  & 2.11  & 0.652 &   \\
S2 & Vt    & 13.8  & 25.1  & 55.4  & 0.840 &   \\
S2 & SpO2  & 0.012 & 0.006 & 0.011 & 0.022 &   \\
S2 & PaO2  & 16.1  & 8.90  & 17.2  & 0.073 &   \\
S2 & \textbf{PaCO2} & \textbf{5.12} & 1.07 & 2.13 & \textbf{0.000} & * \\
\midrule
S3 & HR    & 4.77  & 3.86  & 8.61  & 0.333 &   \\
S3 & MAP   & 0.94  & 0.98  & 2.02  & 0.538 &   \\
S3 & Vt    & 36.3  & 20.8  & 45.9  & 0.129 &   \\
S3 & SpO2  & 0.014 & 0.009 & 0.017 & 0.119 &   \\
S3 & PaO2  & 8.82  & 6.57  & 12.8  & 0.245 &   \\
S3 & \textbf{PaCO2} & \textbf{2.94} & 0.75 & 1.33 & \textbf{0.000} & * \\
\midrule
S4 & HR    & 1.38  & 4.73  & 11.2  & 0.953 &   \\
S4 & MAP   & 1.50  & 1.44  & 2.82  & 0.460 &   \\
S4 & Vt    & 14.1  & 29.0  & 64.1  & 0.897 &   \\
S4 & \textbf{SpO2} & \textbf{0.016} & 0.006 & 0.011 & \textbf{0.002} & * \\
S4 & \textbf{PaO2} & \textbf{4.65} & 1.91 & 3.38 & \textbf{0.003} & * \\
S4 & PaCO2 & 1.05  & 0.61  & 1.13  & 0.083 &   \\
\bottomrule
\end{tabular}
\end{center}
```

\* survives Benjamini–Hochberg FDR control at q = 0.05 across all 24
tests. The BH critical value for the 5th-ranked p-value is
`5 · 0.05 / 24 ≈ 0.0104`; the 5 rows marked above all have
p_emp ≤ 0.009. The naive-α = 0.05 analysis would have flagged 6 rows;
the demoted row (**S2 SpO2**, p_emp = 0.022) does not survive
multiple-comparisons control and is therefore reported *unbolded* in
the table.

**Honest interpretation.** Five of 24 (cell × output) Wasserstein
distances survive BH-FDR control at q = 0.05 against a within-sex
sub-sampling null. **All five are gas-exchange channels:** PaCO2 ×3,
SpO2 ×1, PaO2 ×1.

Before any multiple-comparisons correction (naive α = 0.05), six
rows are flagged as significant — all on gas-exchange channels:
S1 PaCO2, S2 SpO2, S2 PaCO2, S3 PaCO2, S4 SpO2, and S4 PaO2.

Applying Benjamini–Hochberg FDR control at q = 0.05 demotes one of
these: **S2 SpO2** (p_emp = 0.022) sits above the BH critical value
of `5 · 0.05 / 24 ≈ 0.0104` for the 5th-ranked test. The corrected
survivor count is therefore **5 / 24**, and that figure — not the
uncorrected 6 / 24 — is what we report.

The cardiovascular and ventilator outputs (HR, MAP, Vt) do not even
reach significance *without* correction. The observed M-vs-F gaps —
~ 1 – 5 bpm on HR and ~ 13 – 36 mL on Vt — are no larger than what
random sub-sampling of the *same* combined M+F population produces.

The surviving sex-stratified effect concentrates exactly where
sex-specific physiology *should* matter most: gas exchange. This is
the regime where alveolar volume scaling and lung-volume-to-body-mass
ratios diverge by sex. PaCO2 is the strongest signal — significant
in 3 of 4 scenarios, with very small p_emp values in S2 and S3.

*Clinical-meaningfulness context.* The observed 4.7 – 5.1 mmHg
M-vs-F PaCO2 Wasserstein in S1 and S2 is comparable to one
alveolar-ventilation step under ARDSnet protective ventilation —
the same magnitude §2.6 anchors as "clinically meaningful CO2
change" (5 mmHg / 60 s drift threshold). The sex separation is
therefore *detectable at the bedside* but not survival-defining
under typical ICU monitoring tolerances.

*Figure 4 (`fig04_h4_wasserstein`) — at a glance.*
**What:** 1-Wasserstein distance between male and female clean-run
output distributions, per scenario × output, in each output's native
units (bpm, mmHg, mL, %).
**How to read it:** each bar is one (scenario, output) cell; the
observed M-vs-F distance is compared against a within-sex
sub-sampling null (n = 2,000 random splits of the combined M+F clean
runs); cells flagged with `*` exceed the 95th-percentile of the null.
**Key takeaway:** 5 of 24 cells survive BH-FDR control at q = 0.05 —
*all five on gas-exchange channels* (PaCO2 × 3, SpO2 × 1, PaO2 × 1).
Cardiovascular and Vt distances fall within the within-sex baseline
at this sample size.

![Figure 4. H4 — 1-Wasserstein distance, M vs F clean-run outputs, per scenario × output, in each output's native units. Bars marked `*` exceed the within-sex sub-sampling null (n = 2,000 splits) at the 95th percentile; under BH-FDR control at q = 0.05, **5 of 24** survive — all 5 on gas-exchange channels (PaCO2 × 3, SpO2 × 1, PaO2 × 1). S2 SpO2 (p_emp = 0.022) is the BH-demoted row. Source: `results/wasserstein_male_vs_female.csv` + `results/bh_fdr_survivors.csv` (S006 / S008).](../figures/fig04_h4_wasserstein.png)

**Spearman ρ on μ\* rankings with paired-input bootstrap CI.** ρ is
computed wherever both sexes have clean elementary-effect pairs
across all 7 inputs.

```{=latex}
\begin{center}
\begin{tabular}{llcc}
\toprule
Scenario & Output & ρ & 95\% CI \\
\midrule
S2 & HR    & 0.96 & [0.70, 1.00] \\
S2 & MAP   & 1.00 & [1.00, 1.00] \\
S2 & Vt    & 0.75 & [−0.06, 1.00] \\
S2 & SpO2  & 0.96 & [0.70, 1.00] \\
S2 & PaO2  & 0.93 & [0.41, 1.00] \\
S2 & PaCO2 & 0.89 & [0.35, 1.00] \\
\midrule
S3 & HR    & 0.96 & [0.70, 1.00] \\
S3 & MAP   & 0.96 & [0.70, 1.00] \\
S3 & Vt    & 0.86 & [0.34, 1.00] \\
S3 & SpO2  & 0.96 & [0.70, 1.00] \\
S3 & PaO2  & 0.93 & [0.41, 1.00] \\
S3 & PaCO2 & 0.89 & [0.41, 1.00] \\
\bottomrule
\end{tabular}
\end{center}
```

S1 and S4_F have no computable ρ. FiO2 has zero clean
elementary-effect pairs in those cells: every Morris trajectory step
that flips FiO2 between 0.21 and 1.0 has at least one endpoint
flagged — predominantly by SpO2 ceiling pinning at FiO2 ≈ 1.0. This
non-computability is itself a finding (§4.3 limitations).

The bootstrap CI on ρ is wide for output Vt (S2 lower bound −0.06),
meaning the input-importance ranking for Vt is not clearly preserved
across sex. For the other outputs, the lower CI bound sits at ≥ 0.34
— qualitative support for "rankings preserved across sex", though
not high-precision support.

A complementary engine-level verification is relevant here. Pre-Atlas
experiments (`Pulse_translation_new` E12, E13) established that the
female surrogate produces physiologically plausible output across all
four scenarios, independent of this sweep. The sex effects we observe
above therefore reflect real engine-level sex-specific physiology,
not miscalibration of the female patient model.

*Figure 5 (`fig05_h4_spearman_mu_star`) — at a glance.*
**What:** Spearman rank correlation ρ between male and female Morris
μ\* vectors, per scenario × output, with paired-input bootstrap 95 %
CI (n = 1,000 input-resamples).
**How to read it:** ρ = 1 means identical input ranking across sexes;
ρ = 0 no monotonic relationship; ρ = −1 inverted. Computed only for
S2 and S3 — S1 and S4_F have no clean FiO2 elementary-effect pairs
(every FiO2 OAT step has at least one endpoint flagged).
**Key takeaway:** point estimates 0.75 – 1.00 in S2 / S3 — input-importance
rankings are qualitatively preserved across sexes. Vt is the
exception (S2 CI [−0.06, 1.00]), reflecting that the input ranking
driving Vt is not clearly preserved across sex.

![Figure 5. H4 — Spearman ρ on Morris μ\* rankings, M vs F, per scenario × output, with paired-input bootstrap 95 % CI (n = 1,000 input-resamples). Computed only for S2 and S3; S1 and S4_F have no clean FiO2 elementary-effect pairs (§4.5 limitations). Source: `results/spearman_mu_star.csv` (S006 / S008).](../figures/fig05_h4_spearman_mu_star.png)

**Combined H4 picture:**

* H4 is **partially supported**, with the strong signal concentrated
  on gas-exchange outputs.
* **Sex effect is real on PaCO2 (S1, S2, S3), SpO2 (S4), and PaO2 (S4)** —
  these survive the within-sex null under BH-FDR control at q = 0.05.
* **Sex effect on HR, MAP, Vt is not distinguishable from
  within-sex sub-sampling** at our sample size. Either it does not
  exist, or it is below the detection floor of 49 – 144 clean runs
  per cell.
* **Input-importance rankings are similar by sex** (Spearman ρ
  point estimates 0.75 – 1.00 in S2 / S3) but the CIs are wide —
  the ranking-similarity claim is qualitative, not high-precision.

### 3.7 Reliability traffic-light (Figure 6)

*The user-facing summary of the entire atlas: per cell × output, one
of {green, yellow, red}, anchored to preregistered baseline-percentage
thresholds (10 % / 30 % deviation; 30 % hard-failure rate). The final
distribution is 7 green, 29 yellow, 12 red out of 48 cells — and
(S4, M) is red on every output.*

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

*Reliability-traffic-light table — at a glance.*
**What:** textual rendering of the per cell × output classification
across 8 cells × 6 outputs = 48 classifications (the visual version
is Figure 6).
**How to read it:** each row is one (scenario, sex) cell; each column
is one of the 6 atlas outputs; the cell value is the preregistered
classification (green / yellow / red — definitions in the Figure 6
W/H/T block).
**Key takeaway:** the (S2_F, S3_F) cluster is the most reliable region;
(S4, M) is red on every output — the worst single cell in the atlas —
and HR + PaO2 turn red across both sexes from S3 onwards.

Distribution: **7 green, 29 yellow, 12 red** out of 48 cells.

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

*Figure 6 (`fig06_reliability_traffic_light`) — at a glance.*
**What:** per cell × output classification into {green, yellow, red}.
The user-facing summary of the entire atlas and the figure most
likely to be consulted by Pulse practitioners.
**How to read it:** green = no flags raised in the cell *and*
clean-run mean within 10 % of the (S1, M) baseline; yellow = any
flag raised *or* mean 10 – 30 % off baseline; red = mean > 30 % off
baseline *or* diverged + implausible rate > 30 %.
**Key takeaway:** 7 green, 29 yellow, 12 red out of 48 cells. Green
cluster: (S2, F) + (S3, F). Red cluster: HR and PaO2 in S3 / S4.
(S4, M) is red on every output — the worst single cell in the atlas.

![Figure 6. Reliability traffic light — per cell × output, one of {green, yellow, red}. Green = no flags raised in the cell AND clean-run mean within 10 % of the (S1, M) baseline. Yellow = any flag raised OR mean 10 – 30 % off baseline. Red = mean > 30 % off baseline OR diverged + implausible rate > 30 %. Distribution: 7 green / 29 yellow / 12 red across 48 cells; the user-facing summary of the entire atlas. Source: `results/reliability_classification.csv` (S006).](../figures/fig06_reliability_traffic_light.png)

### 3.8 Two structural findings carried from pilot to full sweep

*Two findings that surfaced in the 22-run pilot and held through the
1,280-run sweep. **F-003**: under the preregistered 120 s window,
Pulse PaO2 exceeds the locked 600 mmHg classifier upper bound at
FiO2 = 1.0 on healthy adults — a *transient hyperoxia regime + conservative
preregistered classifier bound*, **not** an oxygenation overshoot, as
shown by a pre-registered 300 s rerun ([S021](#s021)) on the same
input combinations. **F-004**: VC-AC tidal-volume instability in
20.6 % of runs, causally identified in [S014](#s014) as
patient-ventilator dyssynchrony at the inspiration trigger and
corrected by setting trigger pressure to −2 cmH2O.*

* **F-003 — Transient hyperoxia regime in the locked 120 s window.**
  Across the full sweep, **34 of 126 implausibly-flagged runs exceed
  the locked 600 mmHg PaO2 upper bound (`HARD_BOUNDS["PaO2"]` in
  `src/detector.py`), with 91 % of those at FiO2 ≥ 0.95**. PaO2 was
  still drifting upward at the end of the locked 120 s window in
  these runs: 93.3 % of FiO2 ≥ 0.95 valid-CSV runs have positive
  slope over [60, 120] s and 19.5 % exceed the 15 mmHg / 60 s drift
  threshold (full audit in §3.8.1).
  In the *clean* S1 healthy runs (N = 91; clean FiO2 range [0.21,
  0.47]), PaO2 is well-approximated by a linear function of FiO2:
  PaO2 ≈ 505 × FiO2 − 25 mmHg (R² = 0.90), i.e. roughly **5 mmHg
  PaO2 per 0.01 FiO2** in the clean range (Appendix B.2 /
  `Pulse_translation_new` E20 reports a steeper ~7.8 mmHg / 0.01
  slope on a focused single-input probe at FiO2 0.95 – 1.0; the two
  figures reflect different regimes — multi-input averaged across
  [0.21, 1.0] vs single-input near the FiO2 = 1.0 boundary).
  Linear extrapolation from FiO2 = 0.5 (PaO2 ≈ 228 mmHg) predicts
  PaO2 ≈ 481 mmHg at FiO2 = 1.0; the locked 120 s S1 means at
  FiO2 = 1.0 sit higher than this linear extrapolation, but this
  deviation is the *physiologically expected non-linearity* in the
  FiO2 → PaO2 relationship (hemoglobin saturation maxes out and
  dissolved-oxygen kinetics take over above FiO2 ≈ 0.6) — not an
  overshoot.

  **Two competing interpretations.** The original 120 s pattern
  admits either (i) Pulse's oxygenation model overshoots at pure
  oxygen, or (ii) the 120 s window is insufficient for hyperoxia
  convergence and the apparently-implausible 120 s values are
  transient. The interpretations have observable consequences that
  distinguish them at longer windows.

  **The transient-regime interpretation is supported ([S021](#s021)).**
  A pre-registered controlled experiment reran 60 matched-input cases
  at FiO2 = 1.0 with the simulation extended from 120 s to 300 s
  (sample interval 5 s; 22 paired Morris indices × S1 (M + F) =
  44 S1 runs; 4 paired indices × {S3, S4} × {M, F} = 16 ARDS runs).
  All thresholds were committed before any S021 Pulse run was
  observed. The pre-registered decision rule on the S1 subset
  required *frac converged ≥ 75 %* (plateau drift over [240, 300] s
  below the locked 15 mmHg / 60 s threshold) **and** *median plateau
  ∈ [580, 680] mmHg* (alveolar-gas-equation prediction ± 75 mmHg).
  Both were met by very large margins:

    * **S1 (n = 44):** plateau median 643.3 mmHg (decision band
      [580, 680] mmHg); 41 / 44 runs (93.2 %) converged.
    * Plateau median of 643 mmHg sits ~10 – 20 mmHg below the simple
      alveolar-gas-equation prediction
      ($P_AO_2 = \mathrm{FiO}_2 \cdot (P_{\mathrm{atm}} - P_{\mathrm{H_2O}}) - P_aCO_2 / \mathrm{RQ}$
      $= 1.0 \cdot (760 - 47) - 40 / 0.8 \approx 663$ mmHg, then
      $P_aO_2 = P_AO_2 - \text{A--a gradient} \approx 653$ mmHg for an
      A-a gradient of 10 mmHg).
      Pulse therefore *under-shoots* the simple alveolar-gas
      prediction by ~10 mmHg — consistent with a modelled A-a
      gradient — and does not overshoot. The pre-registered decision
      is `HYPOTHESIS_II_TRANSIENT_REGIME_SUPPORTED`.

  **Shunt depression confirms the physiological mapping ([S021](#s021)
  auxiliary, descriptive — not part of the (i)-vs-(ii) decision).**
  On the 4 paired input combinations replayed across all three
  scenarios at FiO2 = 1.0, the [240, 300] s median plateau decreases
  monotonically with ARDS severity (S1 → S3 → S4):

  | Scenario | n | Plateau median (mmHg) | Plateau IQR (mmHg) | Converged |
  |----------|---|------------------------|---------------------|-----------|
  | S1       | 44 |  643.3 | [592, 668] | 41 / 44 (93 %) |
  | S3       |  8 |  143.6 | [ 93, 218] |  8 /  8 (100 %) |
  | S4       |  8 |   72.6 | [ 71,  76] |  8 /  8 (100 %) |

  The same FiO2 = 1.0 + identical input vector therefore produces
  PaO2 ≈ 643 mmHg in healthy lungs and PaO2 ≈ 73 mmHg in severe
  ARDS — an order-of-magnitude depression mediated entirely by the
  ARDS severity scalar. This is exactly the shunt-fraction kinetics
  the alveolar-gas equation predicts under increasing venous
  admixture; Pulse reproduces it correctly.

  **Solver-instability tail at extended windows ([S021](#s021),
  additional sub-finding).** A separate phenomenon emerges *only*
  with the 300 s window: 6 / 44 S1 runs (14 %) develop unphysical
  PaO2 plateaus > 700 mmHg (4 stabilising near 1,400 mmHg, above
  the sea-level barometric pressure of 760 mmHg). All six share a
  specific input signature: **Vt = 633.3 mL combined with RR = 20**
  (and FiO2 = 1.0), i.e. an excessive minute ventilation of
  V̇E ≈ 12.6 L/min, ~ 2× the physiological norm of 6 – 8 L/min.
  Inspection of the per-run trajectories shows a stable
  ~ 690 mmHg PaO2 plateau through ~ 195 s, then an abrupt numerical
  runaway between 195 s and 220 s, plateauing at ~ 1,400 mmHg by
  240 s (concurrent unphysical PaCO2 collapse to < 17 mmHg). The
  locked 120 s atlas window stops the simulation *before* this
  runaway and therefore protects the headline atlas classification
  from it. This is not a transient regime; it is a separate
  solver-instability mode that an *extended-window* user of Pulse
  should be aware of at extreme minute ventilation on healthy lungs.

  **Supplementary physiology-anchored classifier.** The 600 mmHg
  upper bound on PaO2 in `HARD_BOUNDS` is a conservative classifier
  choice that remains *locked* — the preregistered atlas
  classification uses it for all headline numbers (§3.2 – §3.7,
  Table 1, Figure 6). A sensitivity analysis with a wider
  physiology-anchored bound,
  `HARD_BOUNDS_PHYSIOLOGICAL["PaO2"] = (20, 700)` (anchored to the
  alveolar-gas-equation ceiling at sea level), is reported in
  [`results/f003_physiological_reclassification.csv`](../results/f003_physiological_reclassification.csv)
  (committed code:
  [`scripts/f003_physiological_reclassification.py`](../scripts/f003_physiological_reclassification.py)):
  **32 of the 34 implausibly-flagged-by-PaO2 runs become
  physiologically clean under the wider bound** (31 at FiO2 ≥ 0.95,
  21 in S1_F + 11 in S1_M); the remaining two stay implausible
  under either classifier and correspond to the
  solver-instability-tail input signature above.

  **Practitioner takeaway.** Under the locked 120 s atlas window at
  FiO2 ≥ 0.95, treat PaO2 as a transient — the steady-state
  detector is correctly flagging an unfinished trajectory. Under an
  extended ≥ 300 s window, use a plateau window in the final 60 s of
  the simulation; expect a physiological plateau in healthy lungs
  (~ 640 mmHg) and graded shunt depression in ARDS (~ 144 mmHg at
  60 % severity, ~ 73 mmHg at 95 % severity). Avoid Vt × RR
  combinations exceeding ~ 12 L/min minute ventilation on healthy
  lungs at FiO2 = 1.0 — extended-window simulations enter a
  separate solver-instability regime at this corner. Full S021
  protocol and per-run paired data:
  [`experiments_log/santino/S021_hyperoxia_convergence.md`](../experiments_log/santino/S021_hyperoxia_convergence.md);
  raw artefacts in `data/runs/s021_hyperoxia_convergence/`.
* **F-004 — Patient-ventilator dyssynchrony in VC-AC at extreme inputs.**
  Patient-ventilator dyssynchrony in volume-control ventilation at low
  tidal volume is a well-documented bedside phenomenon
  [@figueroacasas2016], so the relevant question for the atlas is not
  *whether* dyssynchrony exists in Pulse but how often the engine's
  default trigger configuration enters that regime under operational
  sweeps. Across the full sweep, 303 / 1,280 (23.7 %) Morris runs
  satisfy `Vt_cv > 5 %` in the [60, 120] s window. Of those,
  264 / 1,280 (20.6 %) carry it as their *primary* flag — the
  remaining 39 also trip the higher-priority `implausible` or
  `diverged` flag for a separate reason and are categorized there per
  the detector priority order (§2.6). The 303-run population is the
  one analysed by the §3.8.1 cross-output drift audit; the 264-run
  subset is the F-004-only steady-state-failure rate.
  Inspecting the
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
  identifies the mechanism. Pulse's VC-AC mode sets
  `InspirationPatientTriggerRespiratoryModel` to `eSwitch::Off` at the
  top of `ToSettings`, then in `AssistedControl` mode flips it back to
  `eSwitch::On` when the action specifies neither
  `InspirationPatientTriggerFlow` nor `InspirationPatientTriggerPressure`:

  ```cpp
  s.SetInspirationPatientTriggerRespiratoryModel(eSwitch::Off);
  if (GetMode() == eMechanicalVentilator_VolumeControlMode::AssistedControl)
  {
    if (HasInspirationPatientTriggerFlow())
      s.GetInspirationPatientTriggerFlow().Set(GetInspirationPatientTriggerFlow());
    if (HasInspirationPatientTriggerPressure())
      s.GetInspirationPatientTriggerPressure().Set(GetInspirationPatientTriggerPressure());
    if(!HasInspirationPatientTriggerFlow() && !HasInspirationPatientTriggerPressure())
      s.SetInspirationPatientTriggerRespiratoryModel(eSwitch::On);
  }
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

  **Causal confirmation ([S014](#s014)).** A pre-registered controlled experiment
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

### 3.8.1 Steady-state window cross-output audit ([S012](#s012))

To ensure the steady-state window remains valid despite F-003 and
F-004, we audited cross-output contamination — i.e. whether the same
runs that show PaO2 drift or Vt oscillation also exhibit drift in the
cardiovascular and gas-exchange channels we use for Morris analysis.
A targeted audit ([S012](#s012))
computes |Δ60s| (drift over the recorded window) for HR / MAP / Vt /
SpO2 / PaO2 / PaCO2 in both vulnerable populations and compares
against the preregistered drift thresholds (see §2.6 Drift-threshold
table for the full `DRIFT_MAX_DELTA_60S` constant and per-channel
clinical-meaningfulness anchors).

* **F-003 arm — hyperoxia (FiO2 ≥ 0.95, n = 208 runs; 195 with valid CSV).**
  Percentages below are computed against the n = 195 subset (the 13
  diverged runs in the arm emitted no CSV). HR exceeds the
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

*This section places the atlas's numerical findings in their
clinical, machine-learning, and Pulse-development context, compares
the atlas to the only prior external falsification study (Cornish
et al. 2023; Table 2), and consolidates the structural limitations of
the work in §4.5.*

### 4.1 What the atlas tells Pulse users

*A practitioner-oriented summary of which cells and which outputs are
trustworthy, marginal, or unreliable — and the specific reasons:
F-003 transient hyperoxia regime, F-004 trigger dyssynchrony,
severe-ARDS solver behaviour, and the sex-stratified divergence
cluster in the input-extreme regime.*

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
  [S006](#s006) input-extreme regime; the complementary continuous-severity
  sweep (§3.5.1) at midrange inputs produced balanced female / male
  divergence in the [0.879, 0.945] band, with the sex effect varying
  with what is varying (Morris-extreme inputs vs ARDS severity).
* **Cardiovascular outputs (HR, MAP) become red at and below moderate
  ARDS regardless of sex.** The S3_M, S3_F, S4_M, S4_F cells all show
  HR > 30 % away from the S1_M healthy baseline (mean HR 147 – 158 bpm
  vs 76 bpm; the S1_M-clean HR_mean used as the reliability-classification
  baseline in §3.7, distinct from the pooled S1 output-HR mean of ~74 bpm
  reported in §3.4.1). This is physiologically expected (tachycardic
  compensation for hypoxemia), but is *not* an artefact: Pulse's
  cardiovascular response to ARDS is large in magnitude, so users
  building closed-loop simulations on this output should account for
  this.
* **FiO2 = 1.0 requires a longer steady-state window.** F-003 — PaO2
  above the locked classifier bound at FiO2 = 1.0, with ongoing
  upward drift in the [60, 120] s window — is *not* an oxygenation
  overshoot: under a 300 s rerun ([S021](#s021)), Pulse PaO2
  converges into the alveolar-gas-equation band (~600 – 650 mmHg)
  with sub-threshold drift in the [240, 300] s plateau. Practitioner
  guidance: at FiO2 ≥ 0.95, either lengthen the simulation window to
  ≥ 300 s and use a plateau window in the final 60 s of that
  simulation, or treat PaO2 as a transient, not steady-state, output.
* **VC-AC dyssynchrony refines rather than indicts Pulse's
  implementation.** The F-004 finding (Vt CV > 5 % in 20.6 % of runs) is
  not a controller pathology: patient-ventilator dyssynchrony at extreme
  settings is a real intensive-care phenomenon [@figueroacasas2016] and
  Pulse models it correctly. The atlas's preregistered steady-state detector simply
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
  4.2 recommends the −2 cmH2O setting validated by [S014](#s014) as a sensible
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

*A short list of recommendations for downstream Pulse users — the
most consequential being: always set `InspirationPatientTriggerPressure`
(recommended default −2 cmH2O) on VC-AC actions, otherwise Pulse
enables a respiratory-model-driven patient trigger that produces
realistic but non-steady tidal volumes at the very ventilator-stress
points where validation matters most.*

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
setting and is the configuration validated by [S014](#s014) in this paper
(median Vt_cv collapses from 0.351 to 0.016, a 96 % reduction; 78.1 %
of locked runs fall below the 0.05 steady-state threshold).

### 4.3 Implications for machine-learning pipelines using Pulse

*Why this atlas matters for anyone training models on Pulse synthetic
cohorts: 51.8 % of runs are clean, but the flagged 48.2 % follow
non-random patterns that can leak into supervised labels and inflate
apparent generalisation. The per-cell traffic light gives an immediate
data-quality filter — green cells ingest as-is, yellow ingest
clean-only with metadata, red cells require per-channel justification.*

The atlas's reliability map is not only an instrument for direct Pulse
users; it doubles as a **per-cell data-quality filter for synthetic
training cohorts** generated by Pulse for machine-learning research.
This is non-trivial because Pulse is increasingly used as a synthetic-
data generator for digital-twin research, reinforcement learning for
ventilation, virtual-patient cohorts in medical-AI development, and
data augmentation for clinical decision-support models. A model trained
on outputs from this atlas's red cells without filtering will
internalise simulator artefacts as if they were physiology:

* The 600 + mmHg PaO2 transient at FiO2 = 1.0 within the locked 120 s
  steady-state window (F-003, §3.8) becomes "what hyperoxia looks like"
  to the model — even though Pulse converges into the physiological
  alveolar-gas-equation band when given a 300 s window ([S021](#s021)).
* The 20.6 % VC-AC tidal-volume oscillation arising from inspiration-
  trigger dyssynchrony (F-004, §3.8) becomes "ventilator behaviour" to
  the model, even though it is corrected by a single configuration
  flag.
* The compensatory tachycardia decoupling input HR from output HR in
  S3 / S4 (§3.4.1) is a particularly insidious feature-engineering
  trap: a neural network trained on these outputs will learn an
  *active physiological reflex* (the baroreceptor / chemoreceptor
  tachycardic response to hypoxemia) as if it were a baseline
  steady-state feature of the cohort. Down-stream this becomes a
  learned input-output relation that does not exist in real patients
  with set heart-rate baselines, and the model will silently
  generalise the reflex gain as a population property.
* The all-male divergence cluster (§3.5) becomes a "clinical pattern"
  if synthetic male / female cohorts are pooled without flag-stratified
  filtering.

The four-flag detector (§2.6) and the per-cell traffic-light map
(§3.7) together support a defensible ML-pipeline contract:

1. **Green cells:** safe to ingest into training cohorts without
   per-run filtering.
2. **Yellow cells:** ingest only the `clean`-flagged runs; report the
   clean-rate per cell with the training-set metadata.
3. **Red cells:** do not ingest into supervised-learning training sets
   without per-channel and per-input justification. Where red cells
   must be used (e.g. learning that PaO2 saturates at extreme FiO2),
   the cell-level reliability rationale should be reproduced in the
   model card.

Adopting this contract converts Pulse from a "use at your own risk"
synthetic-data source into a *bounded* synthetic-data source whose
known failure modes are documented and addressable. The four-flag
detector is general — it can be applied to any Pulse output CSV
without re-running the atlas — and the traffic-light map is portable
to other operational envelopes once a sweep at the new envelope is
completed.

### 4.4 Relationship to Cornish et al. 2023 (causal falsification) — Table 2

*A side-by-side mapping of the atlas's six-output reliability panel
against Cornish et al.'s causal-falsification rejection counts on
MIMIC-III sepsis. The two studies target different scopes
(intervention-outcome falsification vs operational-input sensitivity)
and are complementary; the cross-mapping identifies four channels of
direct overlap (HR, MAP, PaO2, PaCO2) where the two papers' ordinal
rankings agree even though absolute rates differ.*

[@cornish2023] is the only prior external assessment of Pulse on a
clinical dataset. Their framework — causal falsification with
Holm–Bonferroni-adjusted Hoeffding's-inequality confidence intervals
(family-wise error rate 0.05) — tested 1,442 hypotheses across 15
physiological quantities on MIMIC-III sepsis trajectories, with
intravenous-fluid and vasopressor doses as the intervention space.
Table 2 reproduces their per-quantity results re-tabulated against
this atlas's 6-output panel.

```{=latex}
\begin{center}
\begin{tabular}{lllc}
\toprule
Cornish-2023 channel & Hoeffding rejections / hypotheses & Bootstrap (Cornish Appendix Table 5) & Maps to atlas output? \\
\midrule
Chloride            & 24 / 94 & 47 / 94 & No (electrolyte) \\
Sodium              & 21 / 94 & 46 / 94 & No (electrolyte) \\
Potassium           & 13 / 94 & 33 / 94 & No (electrolyte) \\
Skin Temperature    & 10 / 86 & 43 / 86 & No (dermal) \\
Calcium             & 5 / 88  & 44 / 88 & No (electrolyte) \\
Glucose             & 5 / 96  & 19 / 96 & No (metabolic) \\
HCO₃ (Bicarbonate)  & 2 / 90  & 8 / 90  & No (acid–base) \\
Arterial pH         & 0 / 80  & 0 / 80  & No (acid–base) \\
\midrule
\textbf{PaCO2}      & \textbf{3 / 70}  & \textbf{13 / 70} & \textbf{Yes (direct)} \\
\textbf{PaO2}       & \textbf{0 / 78}  & \textbf{4 / 78}  & \textbf{Yes (direct)} \\
\textbf{MeanBP}     & \textbf{0 / 92}  & \textbf{3 / 92}  & \textbf{Yes (≈ atlas MAP)} \\
SysBP               & 2 / 154 & 8 / 154 & Partial (MAP input) \\
DiaBP               & 0 / 72  & 0 / 72  & Partial (MAP input) \\
\textbf{HR}         & \textbf{0 / 162} & \textbf{1 / 162} & \textbf{Yes (direct)} \\
RR                  & 0 / 172 & 12 / 172 & Atlas input, not output \\
\bottomrule
\end{tabular}
\end{center}
```

*Table 2.* Cornish 2023 Table 1 (Hoeffding's inequality, main text) and
Table 5 (reverse-percentile bootstrap, Appendix H.6) re-tabulated
against this atlas's six-output panel. (Cornish's *Table 4* in the
appendix re-tabulates the Hoeffding results from main-text Table 1;
the bootstrap rejections used here are in their Table 5. Citation
label corrected 2026-05-17 in pre-submission Phase-2 audit.) Bold rows mark the four channels
that overlap directly with HR / MAP / PaO2 / PaCO2.

*Table 2 — at a glance.*
**What:** Cornish et al. (2023) per-channel rejection counts from
their causal-falsification framework on MIMIC-III sepsis trajectories,
re-tabulated against this atlas's six-output panel.
**How to read it:** each row is one Cornish quantity; the first
numeric column gives Hoeffding-inequality rejections (their main-text
Table 1), the second column the reverse-percentile bootstrap
rejections (their Appendix Table 5); the rightmost column maps each
channel to an atlas output (Yes / Partial / No). Bold rows are the
four-channel direct overlap.
**Key takeaway:** 80 of 85 Hoeffding rejections fall on Cornish's 11
channels *outside* the atlas's six-output panel (electrolyte,
metabolic, acid-base, dermal). The four-channel overlap (HR, MAP,
PaO2, PaCO2) is in ordinal agreement — PaCO2 is the most
assessment-sensitive channel in both papers — even though absolute
rejection rates differ.

**Cross-mapping the methodologies.** The atlas's six outputs (HR,
MAP, Vt delivered, SpO2, PaO2, PaCO2) intersect Cornish's
15-quantity panel on four channels (HR, MeanBP ≈ atlas MAP, PaO2,
PaCO2); Vt and SpO2 are atlas-only contributions. Cornish's 11
remaining channels divide into electrolyte (Chloride, Sodium,
Potassium, Calcium), metabolic (Glucose), acid–base (HCO₃, pH),
dermal (Skin Temperature), and ventilation-input or
non-overlapping-pressure channels (RR, SysBP, DiaBP). Of Cornish's
85 total Hoeffding rejections, **only 3 fall on the
four-channel atlas overlap (all on PaCO2); the remaining 82 fall on
channels outside the atlas's output panel**. This non-overlap is the
load-bearing observation: the two papers' failure surfaces are
*complementary*, not redundant.

**The agreement on the overlap.** Within the four-channel overlap,
Cornish's Hoeffding results report 3 / 70 rejections (4.3 %) for
PaCO2 and zero rejections for HR, MAP (MeanBP), and PaO2. The
atlas's §3.7 traffic-light shows a structurally compatible picture
on the same four channels: PaO2 goes red at S3 and S4 across both
sexes (4 / 8 cells), HR likewise goes red at S3+ (4 / 8 cells), and
MAP and PaCO2 each have exactly one red cell (S4_M). The two papers
therefore disagree on absolute rates — the atlas exposes
boundary-region failure that Cornish's sepsis-cohort intervention
sequences do not visit — but agree on the *ordinal* pattern: PaCO2
is the channel where Hoeffding rejections concentrate in Cornish,
and PaCO2 is also the channel where the atlas finds within-sex
Wasserstein significance (§3.6 H4); both papers single it out as
the most assessment-sensitive gas-exchange variable. Cornish's
bootstrap counts (Appendix Table 5) reinforce this: PaCO2 rises to
13 / 70 (18.6 %), PaO2 acquires 4 / 78 rejections, and MAP picks up
3 / 92 — a rank ordering (PaCO2 > PaO2 > MAP > HR) that mirrors
the red-cell density of the atlas's gas-exchange-then-cardiovascular
column ordering. The cell-level cross-tab cannot be tighter than
this: Cornish's rejections are indexed by (time-step,
action-sequence, sex–age–quantile bin) over sepsis trajectories,
not by (scenario, sex) over the operational acceptance envelope,
and the two indexings are not surjective on each other.

**The complementarity.** The 11 / 15 Cornish channels that do not
map to the atlas (Chloride 24, Sodium 21, Potassium 13, Skin
Temperature 10, Calcium 5, Glucose 5, HCO₃ 2, plus SysBP / DiaBP /
pH / RR) define Pulse's electrolyte, metabolic, acid–base, and
dermal failure surface. The atlas does not assess any of these.
Conversely, Cornish does not assess SpO2 or delivered Vt, both of
which are load-bearing for ventilator-cohort research. The two
papers therefore divide the Pulse-reliability question along an
output axis: Cornish covers chemistry-and-thermoregulation
intervention-outcome accuracy on a real cohort; the atlas covers
cardio–respiratory operational-input reliability on the engine's
theoretical acceptance envelope. The natural follow-up that neither
paper does is a *metabolic and renal atlas* — sweeping Pulse's
internal endocrine and electrolyte models the way this atlas sweeps
its cardiopulmonary inputs.

**Why this matters for downstream Pulse users.** A practitioner
combining the two assessments now has a four-quadrant reliability
picture:

1. *Cardio–respiratory outputs under operational sweeps* — the
   atlas (§3.7 traffic-light).
2. *Cardio–respiratory outputs under clinical-intervention
   sequences* — Cornish, with PaCO2 as the only flagged channel
   (3 / 70 Hoeffding, 13 / 70 bootstrap).
3. *Electrolyte / metabolic / dermal outputs under operational
   sweeps* — not assessed by either paper.
4. *Electrolyte / metabolic / dermal / acid–base outputs under
   clinical-intervention sequences* — Cornish, where the bulk of
   Pulse's rejections concentrate (80 of 85 Hoeffding rejections on
   the seven non-cardiorespiratory channels Chloride, Sodium,
   Potassium, Skin Temperature, Calcium, Glucose, HCO₃; 240 of 281
   bootstrap rejections on the same set).

Quadrants 1 and 4 are now mapped; quadrants 2 and 3 remain
underspecified. Until quadrant 3 is mapped, electrolyte and
metabolic outputs from Pulse should not be ingested into ML
training pipelines without per-quantity validation against an
external source — Cornish's quadrant-4 evidence (high rejection
density on those channels even within sepsis-cohort interventions)
makes this a hard requirement, not a soft warning.

### 4.5 Limitations

*The structural and methodological limitations of the atlas: adult-only,
VC-AC only, lumped-parameter physiology, the FiO2-edge gaps that make
S1 and S4_F Spearman ρ uncomputable, the 120 s simulation window that
may be insufficient for hyperoxia convergence, and the
theoretical-vs-empirical coverage gap (the atlas does not yet
cross-reference real ICU databases). Every limitation is sourced and
bounded.*

* Atlas restricted to VC-AC adults; pediatric and PC modes out of scope
  (Paper 2 / Paper 1).
* 120 s simulation may be insufficient for hyperoxia convergence (F-003).
  We do not extend simulation length post hoc — the locked window IS the
  paper's measurement; longer windows are explicit future work. The
  [S012](#s012) cross-output audit (§3.8.1) bounds this limitation to PaO2 and
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
* **Implausibility bounds are clinically anchored but not unique
  within the clinical-judgment category.** The `HARD_BOUNDS` table
  (§2.6) categorizes each bound as either physical
  (e.g., SpO2 ≤ 100 %), equipment (Vt range), or a clinical
  *"incompatible-with-60-s-steady-state-in-window"* threshold. Within
  the third category, the exact numerical choice (e.g., PaO2 lower
  20 vs 25 mmHg, MAP lower 30 vs 35 mmHg) is a defensible judgment
  call rather than a unique biological constant — different clinical
  philosophies, anchored in the same Severinghaus / Berlin /
  Sepsis-3 / ICU-textbook literature [@severinghaus1979; @ards2012;
  @singer2016; @marino2013icu; @marini2019critical], could land on
  modestly different numbers. The locked classifier used for all
  headline numbers in this paper is conservative. The precedent for a
  sensitivity analysis on a single bound is the
  `HARD_BOUNDS_PHYSIOLOGICAL` table in §3.8 (PaO2 upper raised from
  600 to 700 mmHg per the alveolar-gas-equation sea-level ceiling
  [@west2020respiratory Ch.5]); a downstream researcher with a
  different clinical philosophy can replicate this pattern on any
  other bound by reusing `src/detector.py::reclassify_implausible_against`.
* **Theoretical vs. empirical coverage.** The Morris sweep samples the
  extremes of Pulse's theoretical acceptance envelope based on
  standardized ARDS definitions. It does not quantify the engine's
  empirical operational coverage — i.e., what fraction of actual,
  real-world ICU patient configurations (such as those found in
  MIMIC-IV or pediatric databases) fall safely within the stable,
  linear regimes identified here. Mapping the engine's reliability
  against the empirical distribution of clinical datasets remains a
  necessary limitation of the current theoretical atlas.
* **`not_steady_state` is a composite flag — its 530 / 1,280 share is
  not a single phenomenon.** A post-hoc trigger-attribution audit
  ([S022](#s022)) shows that the locked `not_steady_state` count
  bundles three distinct contributions: (i) **76 runs** flagged because
  of physiological SpO2 saturation on healthy / well-oxygenated
  patients (a detector edge case on the flatline rule — SpO2 = 1.0 is
  the expected steady-state on adequate FiO2, not pinning); (ii)
  **170 runs** flagged because of F-004 patient-ventilator
  dyssynchrony (§3.8, documented finding causally confirmed by
  [S014](#s014)); and (iii) a **185-run residual** dominated by S4
  severe-ARDS slow convergence and S1 transient hyperoxia drift
  (the F-003 phenomenon documented in §3.8 / [S012](#s012) /
  [S021](#s021)). Of these, only (i) is a detector classification
  edge case; (ii) and (iii) are real Pulse engine behaviours that
  the locked classifier is correctly identifying. The headline atlas
  numbers in §3.1 Table 1 stand under the locked classifier; the
  per-cell sub-mode attribution table is reported in
  [Appendix C](#appendix-c-not_steady_state-attribution-side-table-s022)
  for readers who want to score "engine instability" separately from
  "detector edge case on healthy oxygenation." Under the joint
  exclusion the clean rate would rise from 51.8 % to 78.7 % — this is
  presented as a decomposition, not a re-classification.
* **`not_steady_state` cross-validation by ML/SHAP surrogate.** A
  supplementary RandomForest + SHAP ranking on the n = 663 clean
  subset ([S023](#s023)) recovers the Morris μ\* top-3 in 17 / 18
  pooled (output × top-3) cases and in 23 / 48 per-cell cases at full
  3 / 3 agreement (92 % of per-cell comparisons at ≥ 2 / 3). The
  cross-check is reported in supplementary section S11 with the
  honest caveats it requires (clean-subset bias, OAT non-uniform
  design); see [`results/s023/`](../results/s023/) for artefacts.
* **No comparable open atlas exists for sibling engines.** The atlas
  reports Pulse-specific reliability behaviour; it does not establish
  whether the patterns reported here (sex-stratified divergence,
  VC-AC dyssynchrony at default trigger settings, transient hyperoxia
  regime at FiO2 = 1.0 in a 120 s steady-state window) are unique to
  Pulse or generic to lumped-parameter
  cardiopulmonary engines such as BioGears or HumMod. No
  publicly-available comparable Morris-EE / Sobol / clamping atlas
  exists for either engine at the time of writing, so cross-engine
  relativisation is a limitation of the comparative literature rather
  than of this paper. A multi-engine reliability atlas remains an
  open opportunity for the broader physiology-simulation community.

### 4.6 Implications for downstream Pulse research

*The two downstream research lines this atlas opens hooks for: the
pediatric translation layer (Paper 1, in preparation; validation
underway with the Sainte-Justine PICU cohort) and the native pediatric
Pulse fork (Paper 2, planned). Both depend on the atlas's μ\* rankings
and reliability traffic-light grid as the backdrop for what scope they
can target.*

This atlas is positioned as foundational infrastructure for two
downstream lines of work, both currently in preparation:

* **Pediatric translation layer (Paper 1, in preparation; validation
  underway with the Sainte-Justine PICU cohort).** Maps pediatric
  vital signs onto Pulse's adult engine via quantile matching, and
  uses the atlas's μ\* rankings and reliability traffic-light grid as
  the backdrop for what the translation layer is allowed to do —
  explicitly, the translation layer must keep its output baselines
  inside the green / yellow cells of Figure 6.
* **Native pediatric Pulse fork (Paper 2, planned).** Modifies
  Pulse's C++ source for paediatric physiology. Source-code patch
  ordering is prioritised by the atlas's input-importance ranking:
  equations driving high-μ\* inputs (heart-rate baseline, FiO2 / PEEP,
  Vt) are patched first; equations driving low-μ\* inputs are deferred.

Neither downstream paper is required for this atlas's claims. The
atlas stands independently on Pulse's public documentation, the
publicly-cloned Pulse v4.3.1 source, and the experiments logged in
this repository.

---

## 5. Conclusion

*A short closing summary of the atlas's headline contribution, the
two operator-actionable findings, the sex-as-reliability-axis result
(in its regime-specific form), and the downstream-research role this
paper plays in the maintainer's PhD pipeline.*

This reliability atlas provides the first open, preregistered
sensitivity and divergence map for the Pulse Physiology Engine
(v4.3.1) across the adult operational envelope. By sweeping seven
user-facing inputs across four ARDS severities and two adult
reference surrogates ([S006](#s006), 1,280 simulations), we
identified both the engine's stable operational regimes and its
boundary-failure modes. The resulting per-cell traffic-light map
(Figure 6) delivers an immediate, actionable data-quality filter for
clinical researchers, device developers, and machine-learning
practitioners using Pulse for synthetic cohort generation.

Beyond mapping the envelope, this work yielded two
operator-actionable corrections — resolving VC-AC tidal-volume
dyssynchrony (F-004) via an explicit
`InspirationPatientTriggerPressure = −2 cmH2O` setting
([S014](#s014); median Vt CV collapses 0.351 → 0.016, worst-case
1.826 → 0.112) and reframing the apparent FiO2 = 1.0 PaO2 overshoot
as a transient hyperoxia regime (F-003), with the 300 s plateau
landing ~ 10 mmHg below the alveolar-gas-equation prediction
([S021](#s021); median 643 mmHg vs ~ 653 mmHg predicted) —
consistent with Pulse's modelled A-a gradient rather than an
oxygenation defect. We also established patient sex as a
previously uncharacterized, *regime-dependent* reliability-sensitivity
axis: concentrated on gas-exchange outputs under within-sex BH-FDR
control (5 of 24 cell × output Wasserstein survivors, §3.6) and on
the male input-extreme divergence cluster mediated by Pulse's
blood-volume baseline ([S018](#s018); 20 / 20 → 2 / 20 → 0 / 20 BV
dose-response across §3.5 / §3.5.1).

Ultimately, this atlas transforms adult Pulse from a
"use-at-your-own-risk" simulator into a bounded synthetic-data
source with documented, addressable failure modes. It stands as the
rigorously validated baseline and foundational infrastructure for
the maintainer's two downstream papers: a pediatric translation
layer (Paper 1, in preparation) and a native pediatric Pulse fork
(Paper 2, planned).

---

## 6. Data availability

All data, code, and lab notebooks needed to reproduce every number,
figure, and table in this paper are openly available in the repository
under Apache License 2.0.

* **Master aggregated table:**
  `data/runs/full_sweep/aggregated.parquet` (1,280 rows × all outputs
  + flags + meta; [S006](#s006)).
* **Canonical Morris sample:**
  `data/runs/full_sweep/morris_sample.parquet`
  (seed = 42, 20 trajectories, 4 levels ⇒ 160 unique input points;
  §2.5).
* **Per-cell aggregates:**
  `data/runs/full_sweep/<scenario>_<sex>/aggregated.parquet`.
* **Mechanism-test artifacts:** `data/runs/s014_trigger_lockout/`
  (F-004 causal test, [S014](#s014)),
  `data/runs/s018_blood_volume/` (BV dose-response, [S018](#s018)),
  `data/runs/s021_hyperoxia_convergence/` (F-003 300 s rerun,
  [S021](#s021)).
* **Analysis artifacts:** `results/` (Morris indices, BH-FDR
  survivors, Spearman ρ, reliability classification, NSS sub-mode
  decomposition `results/s022/`, SHAP cross-check `results/s023/`).
* **Figures:** `figures/` (Figures 1 – 6, PNG + PDF;
  `figures/captions.md` for the figure-generation pipeline metadata).
* **Code:** this repository (Apache License 2.0). Source layout per
  §2.9; full reproduction recipe in `README.md`.
* **Programmatic claims-ledger audit:**
  [`scripts/audit_claims.py`](../scripts/audit_claims.py) — read-only
  Python script verifying that every Tier-1 and Tier-2 quantitative
  claim in §3 / §4 / Appendix C matches the canonical artifacts
  under explicit per-class tolerance rules; current state 190 / 190
  PASS ([S024](#s024); see §2.8 for protocol).
* **Pinned Docker image hashes (byte-level reproducibility):**
  `pulse-atlas-engine:3b18bdc08660` (canonical sweep, 2026-04-26)
  and `pulse-atlas-engine:b2e0e807803d` (post-[S014](#s014) rebuild,
  2026-04-28). Upstream base: `kitware/pulse:4.3.1`. Outputs are
  bit-exact across rebuilds for fixed inputs ([S005](#s005) G5 /
  [S007](#s007) / [S015](#s015) / §2.8 Phase 4a).
* **Atlas-version compatibility:** results on Pulse 4.3.1 apply
  identically to `REL_4_3_2` (2025-08-12); the upstream diff is
  build-system-only, no physiology changed ([S016](#s016)).
* **Lab-notebook provenance:** every commit on the main branch ties
  to one of the experiment-log entries S001 – S024 + the OSS
  release-hygiene entries S025 / S026; full audit trail in
  [`experiments_log/INDEX.md`](../experiments_log/INDEX.md).
* **Zenodo deposit:** the raw per-run artifacts excluded from git
  history by `.gitignore` (per-run output.csv / pulse.log /
  config.json / run_meta.json across the 1,280-run sweep + S014 +
  S018 + S021; ~ 1.5 GB total) will be uploaded to Zenodo at the
  time of arXiv submission; DOI added here on upload.

---

## 7. Acknowledgements

This work benefited from government funding managed by the National
Research Agency under France 2030 via the ENACT AI Cluster
(ANR-23-IACL-0004).

This work also relies on the financial support provided by the Région
Grand Est, France, for which we express our gratitude.

We gratefully acknowledge the support of the CHU Sainte-Justine
Foundation in Montreal and the Artificial Intelligence Applied to
Pediatric Acute Care Research Group (R-SADC) in Montreal, Canada.

**Author contributions.** S.N. designed the study, performed all
analyses, wrote all of the manuscript, and is solely responsible
for the scientific claims and statistical interpretations contained
herein. AI tooling (Claude Code, `claude-opus-4-7`) provided
drafting / refactoring / reviewer-style critique assistance on text
and code only, as detailed in §8.

**Competing interests.** The author declares no competing
interests, financial or otherwise.

---

## 8. Transparency: use of AI tools

In the interest of full methodological transparency, parts of this
work were carried out with the assistance of AI tools.

* **Coding assistance.** Portions of the analysis and pipeline code
  in this repository were drafted, edited, refactored, or debugged
  with the assistance of **Claude Code** (Anthropic; model
  `claude-opus-4-7`). Every AI-assisted code change was reviewed,
  tested, and committed by the human author; all preregistered
  thresholds, hypotheses, and experimental decisions were authored
  and locked by the human author before the corresponding analyses
  were run. AI tooling did not modify preregistration content or
  finalised numerical results.
* **Manuscript drafting and editing.** Portions of this manuscript
  were drafted and edited with the assistance of Claude Code. All
  scientific claims, statistical interpretations, and citations
  were authored, verified, and accepted by the human author. Every
  numerical claim in the paper traces to a primary source or an
  experiment log entry under `experiments_log/santino/`, and the
  references were individually verified against their DOI / PMID
  in [S010](#s010) and the 2026-05-12 pre-submission audit.
* **What AI tools were *not* used for.** AI tooling did not run
  Pulse simulations, did not generate or alter raw output data, did
  not author the preregistration or hypotheses, and did not select
  which experiments to run or which results to report. The
  experimental design and the statistical-test choices are the
  author's; the AI tools provided drafting, refactoring, and
  reviewer-style critique support on text and code only.

No AI attribution is included in commits, code comments, or the
authorship line, consistent with this repository's contribution
policy. This transparency note is the single canonical disclosure of
AI tool involvement in the project.

---

## 9. References

Primary sources only — every cited fact in this paper traces to one of
the following or to an experiment-log entry in this repository.

1. **Pulse Physiology Engine v4.3.1 (Kitware, Apache-2.0).**
   Distributed at <https://pulse.kitware.com>. Source verified against
   the upstream Kitware Pulse GitLab repository at
   <https://gitlab.kitware.com/physiology/engine> (locally cloned for
   read-only audit on 2026-04-07; GitLab re-audit 2026-05-07,
   [S016](#s016)). The current
   `stable` head is `REL_4_3_2` (2025-08-12), whose full diff vs
   `REL_4_3_1` is 7 files / +46 −17 lines (web-WASM dockcross
   support, .NET binding tweak); no physiology, validation,
   patient-setup, or solver code changed. Atlas results on 4.3.1
   apply identically to 4.3.2.
2. **Pulse FAQ.** *Have you done UQ / SA?*
   <https://pulse.kitware.com/_f_a_q.html> — verified verbatim
   2026-04-19, still current at the May 2026 re-audit; paragraph
   quoted in §1.1 (recorded in [S003](#s003) / [S016](#s016)).
3. **Pulse `STUDY_SENSITIVITY_ANALYSIS_1_0_0` tag (Kitware, 2020-07-20).**
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
    [S016](#s016) (2026-05-07).
4. **Cornish R, Taufiq MF, Doucet A, Holmes C (Oxford, 2023).**
    *Causal Falsification of Digital Twins.* arXiv:2301.07210
    (November 2023). External statistical-falsification framework
    applied to Pulse on MIMIC-III sepsis trajectories;
    identifies specific intervention-outcome inaccuracies. Cited
    in §1.1 to distinguish prior external assessment
    (intervention-outcome falsification on a different cohort and
    dataset) from this paper's contribution (operational-input
    reliability across the adult ICU envelope). Identified in the
    May 2026 audit logged in [S016](#s016).
5. **Pulse Setup audit.**
   `engine/src/cpp/engine/human_adult/whole_body/controller/SetupPatient.cpp`
   — referenced for adult age gate (lines 41 – 64), BMI bounds (lines
   179 – 200), blood-volume formula (line 534), HR / SBP / DBP
   acceptance bounds (verified by E10 / E28 / E29).
6. **Webb et al. 2022 (ANNSIM).** *Implementation of a dynamic and
   extensible mechanical ventilator model for real-time physiological
   simulation.* PubMed Central article PMC10224749. Describes Pulse's
   ASL 5000 + Dräger Evita validation framework across nine cases
   (healthy / restrictive / obstructive × PC-AC / VC-AC / CPAP);
   reports qualitative waveform agreement. (Pre-submission audit
   2026-05-12: a previous draft cited this paper as "Webb et al.
   2023" with an invented "PulseExt" title and an incorrect author
   list; corrected here against the actual PMC10224749 metadata.)
7. **Pulse Mechanical Ventilator Methodology page (Kitware, v4.3.1
    documentation).** <https://pulse.kitware.com/_mechanical_ventilator_methodology.html>.
    Validation Tables 3 / 5 / 10 / 12 / 17 / 19 report Pulse vs ASL
    5000 + Dräger Evita tidal-volume errors for VC-AC (0.07 % healthy,
    1.01 % restrictive, 2.25 % obstructive) and PC-AC (11.3 % healthy,
    25.3 % restrictive, 15.3 % obstructive). Source of the numerical
    Vt-accuracy claims used to justify the atlas's VC-AC restriction;
    the surrounding validation framework is in entry 6 (Webb et al.
    2022 ANNSIM).
8. **Bray et al. 2019.** Cardiovascular limitations of the
   lumped-parameter model — referenced for valve idealization,
   dicrotic-notch absence, and viscoelastic limitation.
9. **Pediatric Acute Lung Injury Consensus Conference (PALICC-2).**
   ARDS severity classification (mild / moderate / severe), used to
   anchor scenarios S2 (0.26), S3 (0.60), S4 (0.95). Berlin Criteria
   correspondence verified through Pulse's own ARDS validation table.
10. **SALib (Iwanaga, Usher, Herman 2022).** Socio-Environmental
    Systems Modelling. Morris and Sobol implementations used for
    sampling and analysis.
Internal references (`experiments_log/santino/Sxxx_*.md`) are
additionally available in the repository:

* **[S001](#s001)** — Docker + 3-parallel hardware smoke test (CPU / RAM
  budget verification).
* **[S002](#s002)** — Project bootstrap, repo layout, licensing.
* **[S003](#s003)** — Verified Pulse 4.3.1 limitations from primary sources.
* **[S004](#s004)** — Atlas Docker image, scenario smoke test, detector regex
  empirical recalibration.
* **[S005](#s005)** — 22-run pilot, all 5 preregistered gates passed.
* **[S006](#s006)** — Full 1,280-run sweep with 8 sanity checks.
* **[S007](#s007)** — Targeted reproducibility check at three independent
  layers, all bit-exact.
* **[S008](#s008)** — Tier-1 statistical refinement (block bootstrap, within-
  sex Wasserstein null, divergence-input mechanism, Spearman CI).
* **[S009](#s009)** — Tier-2 (seed stability, continuous-ARDS sweep, pytest,
  GitHub Actions CI).
* **[S010](#s010)** — Literature-review pass; every reference below verified
  against its DOI / PMID.

### 9.7 Verified primary references (full bibliographic detail)

Each entry has been individually verified against its DOI or PMID
during the literature-review pass logged in
[`experiments_log/santino/S010_literature_review.md`](../experiments_log/santino/S010_literature_review.md).

**Pulse Physiology Engine**

* []{#ref-bray2019} Bray A, Webb JB, Enquobahrie A, Vicory J, Heneghan J, Hubal R,
  TerMaath S, Asare P, Clipp RB. *Pulse Physiology Engine: An
  Open-Source Software Platform for Computational Modeling of Human
  Medical Simulation.* SN Comprehensive Clinical Medicine 1(5):362-377
  (2019). DOI:
  [10.1007/s42399-019-00053-w](https://doi.org/10.1007/s42399-019-00053-w).
  *(Author list and issue number corrected 2026-05-12 in
  pre-submission audit; the previous draft listed a four-author
  reduction including a non-existent "Carpenter J" — full nine-author
  list confirmed against the Springer record and the Pulse
  publications page.)*
* []{#ref-webb2020} Webb JB, Bray A, Asare PK, Clipp RB, Mehta YB, Penupolu S, Patel
  AA, Poler SM. *Computational simulation to assess patient safety
  of uncompensated COVID-19 two-patient ventilator sharing using the
  Pulse Physiology Engine.* PLoS One 15(11):e0242532 (2020). DOI:
  [10.1371/journal.pone.0242532](https://doi.org/10.1371/journal.pone.0242532).
  PMID: 33237927.
* []{#ref-webb2022vent} Webb JB, Bray A, Scheirich H, VanPelt J, Gerard J, Frembgen S,
  Clipp RB. *Implementation of a Dynamic and Extensible Mechanical
  Ventilator Model for Real-Time Physiological Simulation.*
  Proceedings of the 2022 Annual Modeling and Simulation Conference
  (ANNSIM). PubMed Central:
  [PMC10224749](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10224749/).
  *(Bibliographic entry corrected 2026-05-12 in pre-submission audit;
  the previous draft cited this paper as "Webb et al. 2023, PulseExt:
  validation of the Pulse Physiology Engine ventilator against the
  ASL 5000 lung simulator" with author list "Webb J, Asare P, Bray A,
  Clipp R" — the year, title, and author list were all incorrect.
  The actual PMC10224749 paper is the 2022 ANNSIM mechanical-ventilator
  implementation paper with the seven-author list above. The
  qualitative ASL 5000 validation framework is described in this
  paper; the quantitative VC-AC / PC-AC tidal-volume error percentages
  cited elsewhere in this manuscript come from Pulse's own validation
  tables, see next entry.)*
* []{#ref-pulsevent} Kitware, Inc. *Mechanical Ventilator Methodology — Pulse Physiology
  Engine documentation (v4.3.1).*
  <https://pulse.kitware.com/_mechanical_ventilator_methodology.html>.
  Validation Tables 3 / 5 / 10 / 12 / 17 / 19. Source of the 0.07 –
  2.25 % VC-AC and 11.3 – 25.3 % PC-AC tidal-volume error numbers
  cited in §1.1 and §2.3. Verified 2026-05-12.
* []{#ref-pulserespmethod} Kitware, Inc. *Respiratory Methodology — Pulse Physiology Engine
  documentation (v4.3.1).*
  <https://pulse.kitware.com/_respiratory_methodology.html>.
  Source of the documented ARDS severity-to-impairment-fraction
  mapping (mild = 0.3, moderate = 0.6, severe = 0.9) and the
  associated P/F-ratio claim (340 / 130 / 50 mmHg). Cited in §2.3
  and Appendix B.3 as the canonical documentation against which the
  empirically calibrated mapping {0.26, 0.60, 0.95} is contrasted at
  ARDSnet-protective ventilation. Verified verbatim 2026-05-15.
* []{#ref-cornish2023} Cornish R, Taufiq MF, Doucet A, Holmes C. *Causal Falsification
  of Digital Twins.* arXiv:2301.07210 (November 2023, v4). Oxford
  statistics group. External assessment of Pulse on MIMIC-III
  sepsis trajectories using a causal-inference / statistical-
  falsification framework with Holm–Bonferroni-adjusted Hoeffding's
  inequality confidence intervals (FWER 0.05) on 1,442 hypotheses
  across 15 physiological quantities; identifies intervention-outcome
  inaccuracies in specific cases (Table 1: 85 total Hoeffding
  rejections; Appendix Table 5: 281 reverse-percentile-bootstrap
  rejections; Appendix Table 4 is a re-tabulation of the Hoeffding
  counts). Cited in §1.1 to distinguish prior external assessment
  (intervention-outcome falsification on a different cohort and
  dataset) from this paper's contribution (operational-input
  reliability across the adult ICU envelope); the channel-by-channel
  cross-mapping against the atlas's 6-output panel is presented in
  §4.4 (Table 2). Identified in the May 2026 audit logged in [S016](#s016)
  and verified against the v4 PDF in [S017](#s017) (2026-05-13).

**Sensitivity-analysis methods**

* []{#ref-morris1991} Morris MD. *Factorial sampling plans for preliminary computational
  experiments.* Technometrics 33(2):161-174 (1991). DOI:
  [10.2307/1269043](https://doi.org/10.2307/1269043) /
  [10.1080/00401706.1991.10484804](https://doi.org/10.1080/00401706.1991.10484804).
* []{#ref-campolongo2007} Campolongo F, Cariboni J, Saltelli A. *An effective screening
  design for sensitivity analysis of large models.* Environmental
  Modelling & Software 22(10):1509-1518 (2007). DOI:
  [10.1016/j.envsoft.2006.10.004](https://doi.org/10.1016/j.envsoft.2006.10.004).
* []{#ref-iwanaga2022} Iwanaga T, Usher W, Herman J. *Toward SALib 2.0: Advancing the
  accessibility and interpretability of global sensitivity analyses.*
  Socio-Environmental Systems Modelling 4:18155 (2022). DOI:
  [10.18174/sesmo.18155](https://doi.org/10.18174/sesmo.18155).

**Acute respiratory distress syndrome (clinical anchors)**

* []{#ref-ards2012} ARDS Definition Task Force; Ranieri VM, Rubenfeld GD, Thompson BT,
  Ferguson ND, Caldwell E, Fan E, Camporota L, Slutsky AS. *Acute
  respiratory distress syndrome: the Berlin Definition.* JAMA
  307(23):2526-2533 (2012). DOI:
  [10.1001/jama.2012.5669](https://doi.org/10.1001/jama.2012.5669).
  PMID: 22797452.
* []{#ref-emeriaud2023} Emeriaud G, López-Fernández YM, Iyer NP, Bembea MM, Agulnik A,
  Barbaro RP, et al. *Executive Summary of the Second International
  Guidelines for the Diagnosis and Management of Pediatric Acute
  Respiratory Distress Syndrome (PALICC-2).* Pediatric Critical Care
  Medicine 24(2):143-168 (2023). DOI:
  [10.1097/PCC.0000000000003147](https://doi.org/10.1097/PCC.0000000000003147).
  PMID: 36661420.
* []{#ref-brower2000} Acute Respiratory Distress Syndrome Network; Brower RG, Matthay
  MA, Morris A, Schoenfeld D, Thompson BT, Wheeler A. *Ventilation
  with lower tidal volumes as compared with traditional tidal
  volumes for acute lung injury and the acute respiratory distress
  syndrome.* New England Journal of Medicine 342(18):1301-1308
  (2000). DOI:
  [10.1056/NEJM200005043421801](https://doi.org/10.1056/NEJM200005043421801).
  PMID: 10793162.
* []{#ref-figueroacasas2016} Figueroa-Casas JB, Montoya R. *Effect of Tidal Volume Size and Its
  Delivery Mode on Patient-Ventilator Dyssynchrony.* Annals of the
  American Thoracic Society 13(12):2207-2214 (2016). DOI:
  [10.1513/AnnalsATS.201605-362OC](https://doi.org/10.1513/AnnalsATS.201605-362OC).
  PMID: 27598383. Cited in §3.8 and §4.1 as clinical-literature
  precedent for the patient-ventilator dyssynchrony phenomenon that
  F-004 quantifies inside Pulse. Identified and verified via PubMed
  esummary during the 2026-05-15 novelty audit ([S020](#s020)); the atlas's
  contribution is the Pulse-engine manifestation and the corrective
  trigger setting (−2 cmH2O), not the discovery of dyssynchrony.

**Reproducibility / methods-paper integrity**

* []{#ref-wilkinson2016} Wilkinson MD, Dumontier M, Aalbersberg IJ, et al. *The FAIR
  Guiding Principles for scientific data management and stewardship.*
  Scientific Data 3:160018 (2016). DOI:
  [10.1038/sdata.2016.18](https://doi.org/10.1038/sdata.2016.18).
  PMID: 26978244.
* []{#ref-munafo2017} Munafò MR, Nosek BA, Bishop DVM, Button KS, Chambers CD, du Sert
  NP, Simonsohn U, Wagenmakers EJ, Ware JJ, Ioannidis JPA. *A
  manifesto for reproducible science.* Nature Human Behaviour
  1(1):0021 (2017). DOI:
  [10.1038/s41562-016-0021](https://doi.org/10.1038/s41562-016-0021).

---

## Appendix A — Experiment log index

| ID | Title |
|---|---|
| []{#s001} S001 | Docker + hardware smoke test |
| []{#s002} S002 | Project bootstrap |
| []{#s003} S003 | Verified Pulse 4.3.1 limitations |
| []{#s004} S004 | Atlas image + scenario smoke + detector recalibration |
| []{#s005} S005 | 22-run pilot on (S1, M) |
| []{#s006} S006 | Full Morris sweep (1,280 runs) |
| []{#s007} S007 | Targeted reproducibility check (3-layer, all bit-exact) |
| []{#s008} S008 | Tier-1 statistical refinement (block bootstrap, Wasserstein null) |
| []{#s009} S009 | Tier-2 (seed stability, continuous-ARDS, pytest, GHA CI) |
| []{#s010} S010 | Literature-review pass (every reference DOI / PMID-verified) |
| []{#s011} S011 | Sex-vs-mass disentangle |
| []{#s012} S012 | Steady-state window cross-output audit |
| []{#s013} S013 | Lexical lockdown (manuscript taxonomy) |
| []{#s014} S014 | Trigger-pressure lockout (F-004 mechanism) |
| []{#s015} S015 | Reproducibility and logic audit (pre-publication) |
| []{#s016} S016 | Pulse GitLab + literature re-audit (May 2026) |
| []{#s017} S017 | Cornish 2023 cross-mapping (Phase B item B1) |
| []{#s018} S018 | Blood-volume mechanism falsification (Phase B item B2) |
| []{#s019} S019 | Sobol bolt-on draft (Phase B item B3 — not executed; ready-to-fire) |
| []{#s020} S020 | Pre-submission novelty audit (literature double-check on every "first" claim; one citation added) |
| []{#s021} S021 | Hyperoxia convergence (60-run rerun at 300 s vs locked 120 s window; F-003 mechanism test) |
| []{#s022} S022 | No-compute failure-mode attribution audit of the locked `not_steady_state` count (see Appendix C) |
| []{#s023} S023 | Supplementary ML/SHAP cross-check of Morris μ\* rankings on the clean subset (see Supplementary §S11) |
| []{#s024} S024 | Pre-submission claims-ledger audit (programmatic verification of all Tier-1 / Tier-2 quantitative claims; 190 / 190 PASS, see §2.8) |

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
companion repository (`Pulse_translation_new`, the maintainer's
downstream PhD repository; GitHub URL to be filled at arXiv
submission once Paper 1 publishes).

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
  that the engine remains fully stable up to FiO2 = 1.0. In the focused
  single-input probe (`Pulse_translation_new` entry #20, 9 runs sweeping
  FiO2 ∈ {0.95, …, 1.00} on a healthy male surrogate at fixed
  ventilation), PaO2 scales linearly by approximately 7.8 mmHg per
  0.01 increase in FiO2. The atlas's multi-input Morris fit on the
  S1 clean runs over the full FiO2 ∈ [0.21, 1.0] range gives a flatter
  slope of ~5 mmHg per 0.01 FiO2 (§3.8, F-003): the difference reflects
  the averaging across a wider FiO2 envelope and across the seven
  perturbed inputs rather than a per-step single-input perturbation
  near the FiO2 = 1.0 boundary.

### B.3 ARDS severity calibration and solver instability

The Acute Respiratory Distress Syndrome (ARDS) condition in Pulse is
modulated by a per-lung `Severity` scalar in [0, 1]. This appendix
documents the calibration of that scalar against the Berlin
Definition [@ards2012] severity bands at ARDSnet-protective
ventilation [@brower2000], and the solver-instability zone
encountered above the moderate-band ceiling.

**Pulse's documented mapping (prior claim).** Pulse's official
Respiratory Methodology documentation [@pulserespmethod] specifies a
piecewise-linear severity-to-modifier mapping calibrated at the key
transition points 0.0, 0.3, 0.6, 0.9, and 1.0, with the prose claim
that 0.3, 0.6, and 0.9 correspond to Berlin mild, moderate, and
severe ARDS respectively. The same claim — including specific P/F
ratio values for each band — is repeated verbatim in the
peer-reviewed [@webb2020] Pulse-team-authored COVID-19 multiplex
paper:

| Berlin band               | Documented `Severity` | Documented P/F claim (mmHg) |
|---------------------------|-----------------------|-----------------------------|
| Mild  (200 < P/F ≤ 300)   | 0.3                   | 340                          |
| Moderate (100 < P/F ≤ 200)| 0.6                   | 130                          |
| Severe (P/F ≤ 100)        | 0.9                   | 50                           |

Pulse's own verification suite uses the same fractions:
`ARDSExacerbation.json` progresses 0.3 → 0.6 → 0.9;
`ARDSModerateBothLungs.json` uses 0.6; `ECMOARDSOxygenation.json`
uses 0.8 (between the documented moderate and severe transition
points). Two independent prior sources (the Respiratory Methodology
page and Webb 2020) therefore converge on the same documented
mapping and the same P/F claim.

**Empirical calibration at ARDSnet-protective ventilation.** The
documented mapping was tested directly against the male reference
surrogate (age 18, 67.3 kg, 180 cm) in a 28-run impairment-
fraction sweep (`Pulse_translation_new` experiment E6,
2026-03; the full log is the canonical record of the calibration).
The ventilation regime was held constant across all 28 runs:

* Mode: VC-AC (volume-control assist-control).
* Tidal volume: 403.8 mL = 6 mL/kg on the 67.3 kg male standard
  (ARDSnet lung-protective ventilation, [@brower2000]).
* PEEP: 10 cmH2O.
* FiO2: 0.4.
* Settle time before measurement: 120 s.
* Sampling interval: 10 s.
* Total per-run duration: 5 min.

The sweep was structured in three passes: a coarse 0.1–0.9 sweep
(step 0.1, 9 runs), a fine 0.20–0.30 sweep around the mild-band
transition (step 0.01, 11 runs), and a high-end 0.90–0.99 sweep
across the severe-band candidates (8 runs). Under this regime the
documented mapping does not reproduce the documented P/F claim:

| `Severity` | Documented P/F (mmHg) | Measured P/F at ARDSnet settings (mmHg) | Berlin classification of measured value |
|------------|------------------------|------------------------------------------|------------------------------------------|
| 0.3        | 340  (Mild claim)      | 199                                       | Moderate (at the mild / moderate boundary) |
| 0.6        | 130  (Moderate claim)  | 150                                       | Moderate (matches band)                   |
| 0.9        | 50   (Severe claim)    | 119                                       | Moderate (well inside the moderate band) |

Only the 0.6 → moderate mapping holds. The documented mild fraction
(0.3) lands at the mild / moderate boundary rather than the
mild-band centre, and the documented severe fraction (0.9) sits
roughly 50 mmHg above the severe-band ceiling — i.e. still
moderate by Berlin.

**Corrected mapping used by the Atlas.** From the same E6 sweep, the
fractions that produce P/F values at the Berlin band centres
(or, for severe, immediately below the band ceiling) at the same
ARDSnet-protective ventilation settings are:

| Berlin band               | Atlas `Severity` | Measured P/F (mmHg) | Position in Berlin band            |
|---------------------------|------------------|---------------------|------------------------------------|
| Mild  (200 < P/F ≤ 300)   | **0.26**         | 256                 | Centre of mild band                |
| Moderate (100 < P/F ≤ 200)| **0.60**         | 150                 | Centre of moderate band            |
| Severe (P/F ≤ 100)        | **0.95**         | 96                  | Just inside the severe band ceiling |

**Ventilation-setting dependence.** This calibration is anchored
to the ARDSnet-protective ventilation regime above. Pulse's
documented mapping may reproduce its claimed P/F values under
different combinations of Vt, PEEP, and FiO2 — we have not tested
that. The Atlas's reliability sweep is preregistered to vary all
seven operational inputs around the ARDSnet anchor, so the
calibration applies precisely to the regime the Atlas characterises.
Reliability of the documented mapping at other ventilation regimes
is out of scope.

**Solver instability zone.** Three convergent sweeps within the
companion `pulse_translation_new` project (same engine version,
same surrogate, same researcher, but with non-overlapping
impairment-fraction grids and independent run-by-run execution)
characterise the same numerical-bifurcation range in the
respiratory solver:

* **E6** (the 28-run impairment sweep above, 2026-03): fractions 0.92
  and 0.94 fail to stabilise at ARDSnet settings.
* **E10** (a 10-run high-resolution boundary probe, 2026-04,
  testing 0.90, 0.91, 0.915, 0.92, 0.925, 0.93, 0.935, 0.94,
  0.945, 0.95): 0.90 PASS, 0.91 – 0.945 all FAIL (8 consecutive),
  0.95 PASS. Refines the failure range to **0.91 – 0.945 (inclusive)**.
* **E6 calibration refinement** (a 9-run high-resolution sweep,
  2026-04, testing 0.93 – 0.97 in 0.005 steps): 0.93 – 0.945 all
  FAIL (4 runs), 0.95 – 0.97 all PASS (5 runs). Confirms the upper
  edge of the failure range, giving the calibrated severe fraction
  (0.95) a 0.005 margin.

All three sweeps are within the same companion project rather than
independent third-party replications, so the convergence is
evidence of reproducibility under the same engine version and
surrogate, not of generalisation across labs. Impairment fractions
in this zone consistently result in fatal solver divergence at
ARDSnet-protective ventilation. The Atlas's calibrated severe
fraction (0.95) was selected to clear the upper edge of the zone
with a 0.005 margin. Pulse's documentation [@pulserespmethod] does
not flag this zone.

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

### B.5 Reference-surrogate body-dimension provenance

The two adult surrogates used throughout the atlas (M: 18 yr / 67.3 kg
/ 180 cm; F: 18 yr / 56.2 kg / 163 cm) were originally labelled "Pulse
standard male / female" in early drafts of this work. A 2026-05-19
source-level audit established that this label is technically a
misnomer. The actual provenance, by dimension, is as follows:

* **Weights (67.3 kg M, 56.2 kg F).** CDC weight-for-age 50th-percentile
  values at 18 years (216.5 months) — 67.29 kg for boys, 56.23 kg for
  girls (CDC growth-chart tables; cross-verified against the CDC
  z-score files `wtage.csv` from
  <https://www.cdc.gov/growthcharts/data/zscore/>). These anchors were
  taken directly from the companion `Pulse_translation_new`
  pediatric-translation pipeline, where they form the adult (18 yr)
  endpoint of the CDC progression used for its pediatric strata
  (1 mo / 6 mo / 18 mo / 5 yr / 10 yr / 18 yr). The audit trail is
  recorded in that project's experiments log (CDC weight audit step,
  2026-03).

* **Female height (163 cm).** Matches the CDC P50 stature for
  18-year-old girls. By coincidence it is also identical to Pulse's
  own internal `heightStandardFemale_cm = 163.0` constant
  (`SetupPatient.cpp` L75; cited internally to Centers2016clinical).
  Both anchors therefore agree on this value.

* **Male height (180 cm).** This is a researcher-fixed rounded value
  chosen by the maintainer of `Pulse_translation_new` to yield a clean
  healthy baseline BMI of 20.8 in combination with the 67.3 kg weight.
  It is **not** the CDC P50 male stature at 18 years (CDC P50 ≈ 177
  cm) and it does **not** match Pulse's own internal
  `heightStandardMale_cm = 177.0` constant (`SetupPatient.cpp` L72).
  The 180 cm value sits inside Pulse's accepted male height envelope
  (163–190 cm, with overall BMI 16–30 enforced) and is therefore
  engine-legal: Pulse accepts it without warnings, the setup completes,
  and weight-derived quantities (`computedBloodVolume_mL`, lean body
  mass, BMR, skin surface area) are computed normally. It is, however,
  not anchored to a literature anthropometric source; we disclose this
  here rather than retro-fitting a citation.

**Consequence for the atlas.** The 3 cm male-height offset has no
material effect on the operational-envelope sweep we report (Pulse
does not gate any input on height beyond the 163–190 cm envelope, and
the BMI of 20.8 is centrally inside the 16–30 valid range). The
finding has been carried forward by relabelling the surrogates as
"reference surrogates" throughout the manuscript and the project's
internal documentation; the original "Pulse standard" wording in the
preregistration is preserved verbatim and flagged via a dated erratum
block at the top of that document.

## Appendix C — `not_steady_state` attribution side-table ([S022](#s022))

The locked classifier's `not_steady_state` flag (§2.6) fires when any
output channel violates one of three sub-mode rules in the
[60, 120] s steady-state window: flatline at a hard bound, coefficient
of variation > 5 %, or drift |Δ60s| above the per-channel threshold.
Across the 1,280-run sweep 530 runs fire `not_steady_state`. A
post-hoc trigger-attribution audit ([S022](#s022)) decomposes those
530 by which sub-mode contributed; the locked classifier is unchanged,
the table below is a presentation transform that gives readers a
finer-grained read on what the flag is doing per cell.

The two sub-modes audited are:

* **SpO2 "flatline at ceiling" with mean ≥ 0.999.** A *detector edge
  case*: under the locked flatline rule (std/|mean| < 0.01 *and* mean
  within 0.001 of a hard bound), a healthy or well-oxygenated patient
  whose SpO2 saturates physiologically at 1.0 is classified as
  "pinned at the ceiling." This is correct numerically (std is tiny,
  mean is at the bound) but not pathological — it is exactly the
  expected hemoglobin saturation on adequate FiO2. The locked
  classifier was designed to catch solver-pinning, not physiological
  saturation; the two coincide numerically.
* **Vt CV > 5 %.** The F-004 patient-ventilator dyssynchrony signal
  described in §3.8 and causally tested in [S014](#s014). Pulse's
  default VC-AC trigger configuration leaves the spontaneous-drive
  respiratory model on, which inserts assist breaths between mandatory
  cycles and produces real per-breath Vt variance. S014 confirmed that
  supplying an explicit `InspirationPatientTriggerPressure` collapses
  the Vt CV by 96 % (median 0.351 → 0.016) on 64 controlled reruns.
  The `TidalVolume` CSV channel is breath-integrated and held between
  cycles (S014, native 0.02 s waveform inspection), so the 5 s atlas
  sampling is *not* aliasing — it captures real breath-to-breath
  delivered volume.

Per-cell attribution counts (locked nss preserved; remaining columns
show the residual nss count after excluding the named sub-mode from
the trigger criterion):

```{=latex}
\begin{center}
\begin{tabular}{lrrrrrr}
\toprule
Cell & n\_total & n\_nss & n\_nss excl. & n\_nss excl. & n\_nss excl. & n\_clean excl. \\
     &          &        & SpO2 sat.    & F-004        & both         & both         \\
\midrule
S1\_M & 160 & 107 & 91 & 74 & 29 & 127 \\
S1\_F & 160 & 118 & 88 & 87 & 24 & 136 \\
\midrule
S2\_M & 160 & 69  & 60 & 45 & 23 & 133 \\
S2\_F & 160 & 68  & 52 & 44 & 7  & 153 \\
\midrule
S3\_M & 160 & 12  & 11 & 9  & 8  & 148 \\
S3\_F & 160 & 38  & 34 & 10 & 3  & 157 \\
\midrule
S4\_M & 160 & 44  & 44 & 39 & 39 & 72 \\
S4\_F & 160 & 74  & 74 & 52 & 52 & 82 \\
\midrule
\textbf{Total} & \textbf{1,280} & \textbf{530} & \textbf{454} & \textbf{360} & \textbf{185} & \textbf{1,008} \\
\bottomrule
\end{tabular}
\end{center}
```

*Appendix C Table.* Per-cell attribution of the locked
`not_steady_state` count by trigger sub-mode. Source:
[`results/s022/nss_decomposition.csv`](../results/s022/nss_decomposition.csv).
Generated by
[`scripts/nss_decomposition_table.py`](../scripts/nss_decomposition_table.py).
The locked classifier is unchanged; rows and columns of this table do
not feed §3.1 Table 1 or any of the headline figures.

**Reading the table.**

* **SpO2 saturation contribution (locked − excl. SpO2 = 76 runs).**
  Concentrated in S1/S2 (74 / 76 of those runs; 30 in S1_F, 16 in
  S1_M, 16 in S2_F, 9 in S2_M, plus 5 trickle in S3). Zero in S4 (in
  severe ARDS, SpO2 no longer saturates and this trigger never fires).
  This is the only *detector* edge case identified by [S022](#s022);
  it is not a Pulse limitation, it is a classification limitation of
  the locked flatline rule on healthy oxygenation. A downstream
  researcher who wants to score "engine instability" rather than
  "detector edge case + engine instability" can re-tally clean runs
  excluding this sub-mode using this table.
* **F-004 dyssynchrony contribution (locked − excl. F-004 = 170 runs).**
  Distributed across all cells, with the strongest contribution at
  high set RR (consistent with the S014 mechanism: more assist-breath
  insertions per minute). This sub-mode is a *finding*, not a
  detector edge case — it reflects the documented Pulse-4.3.1
  patient-ventilator-trigger default behaviour, and the locked
  classifier is correctly flagging it.
* **Residual (excl. both = 185 runs).** Dominated by S4 (104 / 185 of
  the residual), and a smaller S1 contribution (53 / 185). The S4
  residual is the F-003-class slow-convergence phenomenon
  ([S012](#s012), [S021](#s021)): severe-ARDS oxygenation has not
  settled within the locked 120 s window. The S1 residual is the
  F-003 transient hyperoxia regime (PaO2 drift at FiO2 = 1.0). Both
  categories are already discussed in §3.8 and are not new findings.
* **Counterfactual "clean" recount.** Under the joint exclusion
  (treat SpO2 saturation as physiological *and* re-attribute F-004
  dyssynchrony to its own documented finding), the clean count would
  rise from 663 / 1,280 (51.8 %) to 1,008 / 1,280 (78.7 %). This
  number is *not* a re-classification of the atlas — it is a
  decomposition of where the 51.8 % clean rate comes from. The
  headline locked-classifier numbers in §3.1 Table 1 stand.
