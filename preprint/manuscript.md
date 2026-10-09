---
title: "Pulse Reliability Atlas: first sensitivity, clamping, and divergence map for the Pulse Physiology Engine v4.3.1"
author: "Santino Nanini^1,2,3,4,5,\\*^, Arnaud Wiedemann^2,3,4,6^, Yassir Mamouni^3^, Cyril Schweitzer^4,5^, Philippe Jouvet^1,2,3^, Michael Sauthier^1,2,3^"
date: "2026-09-28"
header-includes:
  - \renewcommand{\arraystretch}{1.35}
  - \makeatletter\renewcommand{\@maketitle}{\newpage\null\vskip 2em\begin{center}\let\footnote\thanks{\LARGE\@title\par}\vskip 1.5em{\large\begin{minipage}{0.92\textwidth}\centering\@author\end{minipage}\par}\vskip 1em{\large\@date}\end{center}\par\vskip 1em}\makeatother
---

**Affiliations.**

^1^ Pediatric Intensive Care Unit, Department of Pediatrics, CHU Sainte-Justine, Université de Montréal, Montreal, QC, Canada.

^2^ Clinical Decision Support System Artificial Intelligence Health Cluster in Acute Child Care, PE-DIATRICS, CHU Ste-Justine Centre Hospitalier Universitaire Mère-Enfant, Montréal, Canada.

^3^ Research Center of Sainte-Justine University Hospital, Montreal, Quebec, Canada.

^4^ Pediatric Intensive Care Unit, Department of Pediatrics, Children Hospital, CHRU Nancy, Nancy, France.

^5^ UR 3450 DevAH, Université de Lorraine, Nancy, France.

^6^ Université de Lorraine, INSERM UMR_S 1256, Nutrition-Génétique et Exposition aux Risques Environnementaux, Faculté de Médecine de Nancy, Vandœuvre-lès-Nancy, France.

^\*^ Corresponding author.

**Correspondence.** santino.nanini@umontreal.ca

---

## Abstract

**Background.** The Pulse Physiology Engine (Kitware, Apache-2.0; v4.3.1)
is an actively maintained open-source whole-body human physiology
simulator. Its
developers state on the Pulse FAQ that no formal sensitivity analysis has
been performed on user-facing operational inputs. Prior external work
[@cornish2023] addressed intervention-outcome falsification on
MIMIC-III sepsis; the operational-input reliability question has remained
unaddressed.

**Methods.** We swept seven user-facing inputs (HR, SBP, DBP, RR, Vt,
FiO2, PEEP) over preregistered ranges (Pulse's verified setup bands for HR, SBP, DBP and RR; clinical ranges for Vt, FiO2 and PEEP) using Morris
elementary-effects sampling. The sweep spanned four scenarios (healthy
and three ARDS severities, spanning the Berlin Definition's mild–severe
bands and bracketing the 0.91–0.945 solver-instability zone) across two
adult surrogates (CDC weight-anchored male and female), yielding 1,280
total simulations. A locked four-flag detector (`clamped` / `diverged` /
`implausible` / `not_steady_state`) classified every run before analysis.

**Results.** The headline operator-actionable result: VC-AC
(volume-controlled assist-control) tidal-volume oscillation appears in
20.6 % of runs (finding **F-004**), and is **causally linked to the
inspiration trigger, consistent with patient-ventilator dyssynchrony, and
corrected by setting trigger pressure to −2 cmH2O** (median Vt CV collapses from
0.351 to 0.016; worst-case from 1.826 to 0.018). Sensitivity is
strongly skewed: 48 of 48 (cell × output) combinations have ≥ 50 % of
summed μ\* in their top-3 inputs (median 0.928), and the engine is
**predominantly linear** for these dominant parameters — point-estimate
σ/μ\* < 0.6 in 40 of 48 cells, and under trajectory-level bootstrap
31 of 48 cells (65 %) are CI-robustly linear (upper bootstrap CI
< 0.6); of the remaining 17 cells, 11 have a bootstrap CI straddling
0.6, 1 is CI-robustly non-linear (S3_M, PaO2 ← FiO2), and 5 have too few
clean trajectories for a CI (S1_F where Vt dominates, S4_M where FiO2
dominates). The preregistered `clamped` category stayed
empty: 0 of 1,280 runs, and the setup rejections Pulse does perform are
explicit; one explicit downstream adjustment (FiO2 1.0 → 0.9996, 195
runs) is documented in §3.4. Solver divergence is
sex-stratified — 20 of 1,280 runs (1.6 %) diverged, **all 20 male in
the input-extreme regime** (sex-stratification is regime-dependent;
§3.5.1). A second boundary finding (**F-003**): under the
preregistered 120 s window, Pulse PaO2 exceeds the locked classifier
upper bound of 600 mmHg at FiO2 = 1.0 in 34 of 126 implausibly-flagged
runs; an extended 300 s rerun ([S021](#s021)) shows PaO2 converges
to a plateau (median 643 mmHg in S1) that sits ~ 20 mmHg *below* the
simple alveolar-gas-equation prediction (≈ 663 mmHg) — supporting a
transient-regime explanation rather than a Pulse oxygenation overshoot. H4 (sex-specific
reliability) is supported: its preregistered criterion is a male–female
difference in clamping, divergence, or Morris μ\* ranking, and the
all-male divergence cluster satisfies it. The difference extends only
partially into the steady-state distributions, under Benjamini–Hochberg
FDR control (q = 0.05): 5 of 24 cell × output Wasserstein distances
survive the permutation null — all five are gas-exchange (PaCO2 ×3,
SpO2 ×1, PaO2 ×1). Cardiovascular and Vt sex effects do not exceed
the permutation null; input-importance rankings are largely
preserved across sexes (Spearman ρ 0.75 – 1.00 in S2 / S3).

**Conclusion.** The atlas provides a per-cell traffic-light reliability
map for adult Pulse 4.3.1, identifies a previously uncharacterized
sex-stratified reliability-sensitivity axis, yields two operator-actionable corrections
(setting the VC-AC inspiration trigger pressure to −2 cmH2O for
tidal-volume determinism, and extending the steady-state window to
300 s of total simulated time for FiO2 = 1.0 hyperoxia), delivers an
empirical Pulse-severity → P/F calibration table — Pulse's documented
severity defaults all land in the Berlin *moderate* band under the
low-tidal-volume reference ventilation used for that calibration
(6 mL/kg actual body weight, on the male reference body), and the table supplies corrected
fractions that reach the intended mild, moderate and severe bands —
and provides a per-cell curation and review-priority map for downstream
machine-learning pipelines that train on Pulse-generated synthetic
cohorts.

---

## Key Findings at a Glance

*A condensed, number-complete digest of everything the atlas established — the
single place to recover any headline or secondary result without reading the
full text (written to seed later thesis chapters). Each bullet is
self-contained; experiment-log tags (S0xx) point to provenance. The
seven reusable artifacts are listed separately under "Key contributions"
below; this section is the exhaustive findings digest.*

**Scope and scale.**

* First open, **preregistered** reliability atlas for the **Pulse Physiology
  Engine v4.3.1** (Kitware, Apache-2.0), VC-AC ventilation, adult
  critical-care envelope. Results apply identically to the build-only v4.3.2
  release.
* **1,280 simulations** = 8 cells (4 scenarios, healthy S1 and ARDS S2/S3/S4,
  × 2 reference bodies M/F) × 160 runs. Seven swept operational inputs (HR, SBP, DBP, RR,
  Vt, FiO2, PEEP); six steady-state outputs (HR, MAP, Vt, SpO2, PaO2, PaCO2);
  four-flag detector (`clamped` / `diverged` / `implausible` /
  `not_steady_state`).
* **Overall data quality:** 663 / 1,280 runs (**51.8 %**) are flag-clean under
  the locked classifier. Per-cell traffic-light map: **7 green / 29 yellow /
  12 red** of the 48 cell × output combinations (Figure 6).

**Primary finding 1 — VC-AC tidal-volume oscillation and the −2 cmH2O trigger lever (F-004).**

* Delivered-Vt coefficient of variation (CV) exceeds the 0.05 steady-state
  threshold in **20.6 %** of runs; concentrated on healthy lungs (S1), fading
  with ARDS severity.
* **Causally linked** to the inspiration trigger and consistent with
  patient–ventilator dyssynchrony, a clinically recognised asynchrony; not a
  solver artefact.
* Locking `InspirationPatientTriggerPressure` to **−2 cmH2O** ([S014](#s014))
  collapses **median Vt CV 0.351 → 0.016** and **worst-case 1.826 → 0.018**;
  **78.1 %** of locked reruns drop below 0.05. Use as a deterministic-cohort
  lever, *not* a clinical recommendation (it suppresses Pulse's
  effort-dependent breath-to-breath variability).

**Primary finding 2 — transient hyperoxia regime at FiO2 = 1.0 (F-003).**

* Under the locked 120 s window, steady-state PaO2 exceeds the 600 mmHg
  classifier bound in **34 of 126** implausible-flagged runs; **91 %** at
  FiO2 ≥ 0.95.
* Longer reruns ([S021](#s021); the same configurations re-executed at 300 s of recorded simulation instead of the locked 120 s) resolve it: S1 plateau
  **median 643 mmHg**, ~20 mmHg *below* the alveolar-gas-equation sea-level
  ceiling (≈663 mmHg) — i.e. a window-length artefact, not an oxygenation
  overshoot. 40/44 S1 reruns met
  the drift criterion, but 3 of those 40 plateau above 1,400 mmHg, beyond
  the 760 mmHg sea-level barometric pressure; 6 runs in all develop an
  off-scale numerical runaway, so 37/44 (84.1 %) converge below the
  physiology-anchored 700 mmHg ceiling, distinct from the locked 600 mmHg bound.
* **Practical rule:** simulate hyperoxia for ≥ 300 s of total simulated time before extracting a PaO2
  plateau; on healthy lungs at FiO2 = 1.0, screen each PaO2 trajectory
  individually — no input-side ventilation setting predicts the
  numerical runaway.

**Primary finding 3 — sex-stratified solver divergence and its blood-volume dependence.**

* **20 of 1,280 runs (1.6 %) diverged; all 20 on the male body** (per-cell
  4 / 4 / 4 / 8 across S1–S4_M; zero of the 640 female runs).
* **Two regimes** (independently re-derived and live-Docker-confirmed):
    * *Input-driven:* the compound hypotensive–tachypneic pattern
      **HR = 50 & SBP = 90 & RR = 20** accounts for **16 / 20** divergences
      (and every male run matching it diverges). **FiO2 = 1.0 is requested
      in 13 / 20** (enriched ~4× vs base rate) but is **not necessary** — the
      compound diverges at FiO2 = 0.737 as well — and it is never applied:
      every divergence occurs during patient stabilisation, before the
      ventilator action is submitted.
    * *Severity-driven* ([S009](#s009)): at midrange inputs **both sexes
      diverge across the [0.879, 0.946]** ARDS-impairment band (union; female
      0.879–0.928, male 0.899–0.946).
* **Blood-volume dependence** ([S018](#s018)): Pulse's allometric `BloodVolumeBaseline`
  (male default **4,802.63 mL** vs female **3,996.09 mL**, ~17 % gap).
  Reducing male BV eliminates divergence:
  **20/20 → 0/20** at both the 4,400 and 4,082.24 mL reductions (default 4,802.63 mL).
* Engine-level side-finding (**F-S018-A**): a hard per-patient BV floor at
  **4,082.24 mL** on the male body, 86 mL above the female default — the two
  bodies cannot be made BV-equivalent by a one-way transplant.

**Sensitivity structure (H1) — skewed and predominantly linear.**

* Top-3 inputs account for ≥ 50 % of summed μ\* on **48 / 48** cell × output
  combinations (median **0.928**, range 0.658–0.998; point-estimate top-3 fraction).
  That sum runs over the inputs carrying at least one clean pair, so it covers
  six inputs rather than seven in the 18 combinations where FiO2 carries none
  (S1_M, S1_F, S4_F); the fractions do not share a common denominator across
  cells.
  Lowest fractions in severe-ARDS gas-exchange (S4_F SpO2 0.658, S4_M 0.703).
* Cardiovascular outputs are cardio-input-driven (output HR ← input HR,
  MAP ← SBP in every cell); gas-exchange outputs are ventilator-driven
  (PaO2 ← FiO2 in mild/moderate ARDS; in severe ARDS the FiO2 μ\* falls
  sharply, still rank 1 in S4_M on a single elementary-effect pair and not
  estimable in S4_F under the four-flag screen; PaCO2 ← Vt via the
  alveolar-ventilation identity).
* **Linear on the dominant input, much less so on the top three:** the
  dominant input's point-estimate σ/μ\* stays below 0.6 in 40 / 48 cells, and
  31 / 48 are CI-robustly linear under the ratio-aware bootstrap. Applying the
  rule the preregistration actually states — the top-three inputs, not the
  dominant one alone — the trigger fires on 43 / 48 cells, and 23 of the 144
  top-three inputs hold a lower CI bound at or above 0.6 across five seeds. The
  bolt-on is **closed by its own preregistered budget** ([S019](#s019)): 6,144
  runs required against an envelope of 1,500, or 3,584 for first-order and
  total indices alone. A restricted exploratory Sobol
  demonstrator is preserved in the repository; it is not an implementation of
  that design.

**Silent clamping (H2) — not observed; one explicit downstream adjustment.**

* **0 of 1,280** runs fired the `clamped` flag: the preregistered category
  stayed empty, and no submitted setup input was refused. The setup rejections
  that Pulse does perform are explicit (`[ERROR]` + exit code 1, confirmed by
  the [S005](#s005) probes); the BP gate (SBP > 120 / DBP > 80;
  DBP/SBP ≤ 0.75) and the HR/RR/age bands are enforced at setup.
* One adjustment does occur, downstream of ingestion and announced in the log:
  where FiO2 = 1.0 was requested, the ventilator model caps the inspired
  oxygen fraction at **0.9996** (195 runs; see §3.4). It is neither silent nor
  a setup event, so it neither enters `clamped` nor bears on H2.

**Sex-stratified reliability (H4).**

* Under Benjamini–Hochberg FDR control (q = 0.05), **5 of 24** cell × output
  Wasserstein distances survive the permutation null — **all five
  gas-exchange** (PaCO2 ×3, SpO2 ×1, PaO2 ×1). Cardiovascular and Vt sex
  effects do not exceed the permutation null.
* Input-importance rankings are largely sex-preserved: **Spearman ρ
  0.75–1.00** in S2 / S3.
* Net: the sex effect is **regime-dependent** — strong at the male
  input-extreme divergence boundary, modest in clean gas-exchange
  distributions.

**Secondary findings.**

* **ARDS-impairment instability band — to our knowledge, the first systematic characterisation.** Three
  converging boundary probes first flagged 0.91–0.945; the 200-run
  continuous-severity sweep extends the empirical divergence band to
  **[0.879, 0.946]**. The locked sweep places S4 at 0.95, deliberately above
  it. Avoid [0.879, 0.946] when stable steady-state outputs are required.
* **Compensatory tachycardia shifts output HR upward under
  hypoxemia.** Output HR settles at **73.8 ± 20.4 bpm** in S1 but rises to
  **155.7 (S3)** and **147.1 (S4)** bpm despite the same [50, 110] input
  range — a scenario-dependent compensatory shift, consistent with Pulse's
  documented baroreflex/chemoreflex behaviour, while input HR remains the
  dominant within-scenario determinant of output HR.
  ML pipelines will internalise this as a steady-state feature, not an active
  response.
* **ML/SHAP cross-check of the Morris top-three sets** ([S023](#s023)): a
  RandomForest + SHAP surrogate on the 663 clean runs shares **17 / 18**
  possible input memberships with the Morris top-3 **sets** across the six
  pooled output-level comparisons (five outputs 3/3, PaO2 2/3; mean per-cell overlap 2.40 / 3; 92 % of
  48 comparisons ≥ 2/3, a partial overlap rather than a preserved order) —
  supporting the robustness of those sets
  to an alternative analysis route on the same Pulse-generated data.
  Supplementary only (training R² uninformative; clean-subset
  selection bias).
* **ARDS-severity → P/F calibration table** (ventilation-setting-dependent):
  impairment {0.26, 0.60, 0.95} lands P/F ≈ **256 / 150 / 96 mmHg** (near the
  Berlin mild and moderate band centres; just inside the severe band's
  upper boundary, which is open-ended below and has no centre) under VC-AC + Vt 6 mL/kg + PEEP 10 + FiO2 0.4 on the male reference body; Pulse's
  documented {0.3, 0.6, 0.9} defaults give 199 / 150 / 119 mmHg at the same
  settings.
* **Complementarity with Cornish et al. 2026** ([S017](#s017)): their
  causal-falsification on MIMIC-III reported **85 Hoeffding rejections** across
  15 channels; **82 / 85 fall outside** this atlas's four-channel
  cardio-respiratory overlap (only 3 / 85 overlap, all PaCO2). The two failure
  surfaces are complementary, not redundant.

**Reproducibility and release.**

* Bit-exact reproduction verified at three layers (canonical sample, per-cell
  aggregate parquets, derived statistics); fixed seed 42; single pinned Docker
  image; preregistered before data collection.
* Full pipeline + audit ledger (re-derives the computed quantitative claims from the
  canonical artefacts, [S024](#s024)) released Apache-2.0. Six engine-side
  infrastructure recommendations offered to the Pulse maintainers (§4.7).

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
  traffic-light curation map (Figure 6).
* **§4 — Discussion.** Practical user guidance, implications for
  machine-learning pipelines that train on Pulse synthetic cohorts, a
  side-by-side mapping against Cornish et al. 2026 causal falsification
  (Table 2), explicit limitations (§4.5), downstream research hooks
  (§4.6), and a short, evidence-anchored list of engine-side
  infrastructure enhancements offered back to the Pulse maintainers
  (§4.7).
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
  (48 combinations, 1,280 simulations), openly released alongside
  the engine.
* **Operator-actionable VC-AC correction (F-004).** Tidal-volume
  oscillation in 20.6 % of runs is *causally linked* to the
  inspiration trigger, consistent with patient-ventilator dyssynchrony, and
  *resolved* by setting trigger pressure to −2 cmH2O (median Vt
  coefficient of variation collapses 0.351 → 0.016; worst-case
  1.826 → 0.018).
* **Transient hyperoxia regime (F-003).** Under the preregistered 120 s
  window, Pulse PaO2 exceeds the locked classifier upper bound of
  600 mmHg at FiO2 = 1.0 in 34 implausibly-flagged runs (91 % at
  FiO2 ≥ 0.95). An extended 300 s rerun ([S021](#s021)) shows PaO2
  converges to a plateau ~ 20 mmHg *below* the simple
  alveolar-gas-equation prediction (S1 median 643 mmHg vs ≈ 663 mmHg
  predicted). The
  original flag therefore reflects (a) the locked 120 s window being
  insufficient for hyperoxia convergence and (b) the conservative
  classifier bound, not a Pulse oxygenation overshoot. A supplementary `HARD_BOUNDS_PHYSIOLOGICAL`
  reclassification (PaO2 upper 700 mmHg) is reported as a sensitivity
  analysis in §3.8.
* **A sex-stratified reliability-sensitivity axis** — the first male–female
  reliability comparison in the Pulse literature. Under
  Benjamini–Hochberg FDR control (q = 0.05), 5 of 24 cell × output
  Wasserstein tests survive the permutation null, *all five in
  gas-exchange channels*.
* **Sex-stratified solver-divergence cluster in the input-extreme regime.**
  20 of 1,280 runs (1.6 %) diverge, *all 20 on the male surrogate in the
  Morris input-extreme regime*; the complementary continuous-severity
  sweep at midrange inputs (§3.5.1) shows divergence approximately
  sex-balanced in aggregate inside the [0.879, 0.946] band, but with the
  sex asymmetry reversed between the two severity bands (female 14/19 vs
  male 5/19 in (0.85, 0.91]; female 5/9 vs male 8/9 in (0.91, 0.945])
  — the sex effect is regime-dependent. The [S006](#s006) cluster is
  shown ([S018](#s018)) to depend on Pulse's
  `BloodVolumeBaseline` (male default 4,802.63 mL vs female default
  3,996.09 mL, a ~17 % gap): reducing the male surrogate's BV
  eliminates divergence
  (20 / 20 → 0 / 20 at both the 4,400 and 4,082.24 mL reductions; default 4,802.63 mL).
  A separate engine-level finding (F-S018-A) is the per-surrogate BV
  floor at 4,082.24 mL that bounds how far the gap can be closed by a
  one-way transplant.
* **A reusable four-flag classifier**
  (`clamped` / `diverged` / `implausible` / `not_steady_state`) that
  future Pulse users can apply to their own scenario configurations
  without re-running this sweep.
* **Reusable ARDS-severity → P/F calibration table at the reference ventilation setting.**
  Empirical mapping {0.26, 0.60, 0.95} lands Pulse's per-lung severity
  scalar near the Berlin mild and moderate band centres, and just inside
  the severe band's upper boundary (P/F ≈ 256 / 150 / 96 mmHg), under VC-AC +
  Vt 6 mL/kg actual body weight + PEEP 10 + FiO2 0.4 on the male reference
  body; Pulse's documented {0.3, 0.6, 0.9}
  defaults yield 199 / 150 / 119 mmHg at the same settings (vs. published
  340 / 130 / 50 mmHg, Webb 2020) — calibration is *ventilation-setting-dependent*.

---

## Notation and abbreviations

*Thirty entries: the symbols and acronyms used throughout, the
document's own structural vocabulary, and the identifier families
(experiment codes, findings, hypotheses, audit anchors). Defined here so
that a reader — or a reading agent — entering at any point does not
need to chase definitions through the prose.*

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
| CV | Coefficient of variation — standard deviation divided by the mean. A single locked threshold of 0.05 is applied to **every** tracked output as one of the three steady-state criteria; tidal volume is simply where it fires most often (§2.6). |
| **Structural terms** | |
| Cell | One (scenario, sex) slice of the atlas — one severity scenario combined with one reference body. 4 scenarios × 2 bodies = 8 cells, each holding 160 runs. |
| Clean pair | A Morris elementary-effect step whose two endpoint runs both carry no flag. Only clean pairs enter the μ\* estimate. |
| `primary_flag` | When a run fires several flags, the single highest-priority one, resolved by the order `clamped > diverged > implausible > not_steady_state` (§2.6). |
| Traffic light | The per-cell curation map (§3.7): each cell scored green / yellow / red from its flag rates and its deviation from the healthy baseline. |
| Tier-1 / Tier-2 | Claim classes in the audit ledger. Tier-1 are headline claims of the main results; Tier-2 are follow-up and supplementary claims. |
| Sobol bolt-on | The preregistered option to escalate from Morris screening to a full Sobol variance decomposition if non-linearity warranted it. Evaluated and closed in §3.3.1. |
| Runaway | A run whose PaO2 keeps climbing past the plausibility ceiling instead of settling — the numerically unstable tail of the hyperoxia regime (§3.8). |
| Allometric | Scaling a physiological quantity by body size. Pulse sets blood volume allometrically as BV = 65.6 · weight^1.02 (§3.5). |
| **Identifier families** | |
| S001 – S026 | Atlas lab-notebook entries, one per experiment, in `experiments_log/santino/`. Indexed in Appendix A. |
| F-003 / F-004 | The two named boundary findings the atlas carried from pilot to full sweep: F-003 the transient hyperoxia regime at FiO2 = 1.0 (§3.8), F-004 the VC-AC tidal-volume oscillation, consistent with patient-ventilator dyssynchrony (§3.8). No other F-numbers are in use. |
| H1 – H4 | The four preregistered hypotheses, quoted verbatim in §2.0 and evaluated in §§3.3 – 3.6. |
| T1.\* / T2.\* / T3.\* / T5.\* | Anchor identifiers in the audit ledger (`scripts/audit_claims.py`). Each re-derives one manuscript number from the canonical data. |
| §S1 – §S18 | Sections of the *npj* submission's Supplementary Information, a separate document from this monograph. |
| `Pulse_translation_new` | The companion pediatric-translation project. Its own experiments are labelled E1 – E10; experiments of that project without an E-number are cited here by name. |

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

*Why this paper exists. Pulse is used in clinical research,
medical-device development, and education, yet to our knowledge no public
sensitivity / clamping / divergence map of its user-facing operational
envelope has been published. This section sources that gap directly from the Pulse
FAQ and frames the atlas as the first open answer.*

The Pulse Physiology Engine [@bray2019] (Kitware, Apache-2.0)
is an actively maintained open-source whole-body human physiology
simulator. It provides a 0-dimensional lumped-parameter model of the
cardiovascular, respiratory, gas-exchange, and pharmacological
systems.

*Pulse in a nutshell.* The engine represents the body as a network of
coupled electrical-circuit analogues — vascular resistances as
resistors, vessel and chamber compliances as capacitors, the heart as a
time-varying capacitor [@pulsecardiomethod] and the respiratory muscles
as a time-varying pressure source — solved as a
system of ordinary differential equations at a 20 ms fixed timestep
[@bray2019]. The cardiovascular, respiratory (a 5-compartment lung
model: carina, left and right anatomic dead space, left and right
alveoli) [@pulserespmethod], gas-exchange, endocrine, renal, and drug
sub-models share state at each step, producing a self-consistent
whole-body trajectory at about 5–10× real time, depending on machine
specifications [@pulsefaq]. The codebase is C++ with bindings for Java, C#, and Unity
[@pulseabout] and an interface for Python [@webb2022vent], and deploys on
Windows, Mac, Linux, and ARM [@pulseabout]. Pulse forked from the
DoD-funded BioGears engine in 2017 [@pulseabout; @pulsefaq] and is
described by its maintainers as using "a low fidelity clinical
approach" and as "not necessarily for high fidelity predictive
purposes" [@pulsesystem] — a self-description that motivates rather than
contradicts the present reliability mapping.

Pulse is used in three broad communities:

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
* **Education** — Pulse has been integrated into medical education and
  simulation-training applications, including virtual-patient and
  emergency-medicine training systems [@pulseinaction].

Despite this footprint, the engine's developers state explicitly on
the public Pulse FAQ [@pulsefaq; verified verbatim 2026-04-19, still
current as of the May 2026 GitLab re-audit, [S003](#s003) / [S016](#s016)]:

> "We have not performed a systematic forward propagation or inverse
> quantification of model uncertainty, nor have we conducted a formal
> sensitivity analysis."

The 2026 GitLab re-audit ([S016](#s016)) qualifies the FAQ claim slightly:
the repo carries a 2020 tag `STUDY_SENSITIVITY_ANALYSIS_1_0_0` with a
one-off Sobol study on internal lumped-parameter circuit values
(cardiovascular and respiratory resistances and compliances) for model calibration. That study targets a different parameter class
(internal circuit values, not user-facing operational
inputs). Prior external work [@cornish2023]
addressed intervention-outcome falsification — verifying whether
Pulse accurately mimics how a real patient's trajectory changes after
a medical intervention — on MIMIC-III sepsis trajectories, a different
scope from the operational-input reliability question addressed here,
applied to a different cohort and dataset. To our knowledge, no systematic
sensitivity analysis on **user-facing operational inputs** (HR, SBP, DBP, RR,
Vt, FiO2, PEEP) has been published.

The corollary is operational: every Pulse user driving the engine
from operational settings — clinical, industrial, educational — is
operating *without a published map* of how the engine behaves across its
operational envelope, whether it runs submitted inputs as given,
and which inputs dominate which outputs. Users may therefore need to establish
a use-case-specific working envelope independently.

This paper closes that gap with the first open reliability atlas for
Pulse v4.3.1 across the adult operational envelope relevant to
critical care. The methodology follows three commitments locked
before any data was collected (preregistration §Inputs, §Scenarios,
§Flags):

* **Inputs** swept over preregistered ranges: Pulse's *verified* setup bands
  for HR, SBP, DBP and RR (the companion E10 boundary probe and its HR / RR initialisation
  probes), and clinical ranges for Vt, FiO2 and PEEP.
* **Scenarios** spanning healthy adult and three ARDS severities,
  calibrated on the male reference body against the Berlin Definition's
  PaO2/FiO2 bands [@ards2012].
  PALICC-2 (Pediatric Acute Lung Injury Consensus Conference, 2nd
  ed.) [@emeriaud2023] is cited as the parallel pediatric severity
  framework; note that PALICC-2 itself favours Oxygenation Index
  (OI) / Oxygen Saturation Index (OSI) over P/F.
* **A four-flag classifier** that categorizes every run rather than
  discarding flagged ones (preregistration discipline per
  [@munafo2017]).

Four properties make this paper a methods-paper rather than a
findings-paper: (1) the core sampling design, classifier thresholds
and primary analysis plan are preregistered, with amendment history
and deviations reported explicitly (per [@munafo2017]); (2) every quoted
number is reproducible from the canonical Morris sample (seed = 42)
plus the atlas Docker image, verified at three independent layers
([S007](#s007)); (3) the data are released under FAIR principles
[@wilkinson2016]; and (4) the four-flag classifier is a generic
instrument that future Pulse users can apply to their own
configurations without re-running our sweep.

The paper is the first publishable output in the maintainer's PhD
pipeline. Two downstream papers — pediatric translation layer (in
preparation, validation underway) and native pediatric Pulse fork
(planned) — both depend on knowing how adult Pulse behaves across
its operational envelope.
Characterising the adult engine's operational envelope is therefore
a *methodological prerequisite* for the downstream pediatric
translation work: any pediatric adaptation of
Pulse must first establish how the adult engine itself behaves.
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
   Pulse repository (Sobol on internal lumped-parameter circuit values:
   cardiovascular and respiratory resistances and compliances, for model calibration) addressed a different parameter
   class; the FAQ statement remains
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
7. PC-AC delivered Vt deviates from the physical reference by 11.3 – 25.3 % across healthy / restrictive / obstructive lung profiles, against 0.07 – 2.25 % for VC-AC, per Pulse's own validation tables [@pulsevent]; the surrounding validation framework is described in [@webb2022vent]. Those tables print **unsigned** percentage errors, but their paired columns show Pulse delivering *less* than the physical reference in all three PC-AC profiles (935 vs 1,047 mL; 409 vs 528 mL; 490 vs 571 mL) — consistent with [@webb2022vent], which reports that the physical ventilator produces the higher tidal volumes. Companion experiments in `Pulse_translation_new` (the female-surrogate engine tests and the male/female side-by-side verification) measure a **different comparison**: PC-AC against *VC-AC within Pulse* at PIP = 20 cmH2O, where PC-AC delivers more (female +58.9 %, male +24.0 %; see §2.3). The two are not in conflict — one compares Pulse against physical hardware, the other compares two Pulse modes against each other. The atlas restricts to VC-AC.
8–12. Structural lumped-parameter limits — discussed in §4.5.

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
the cell-level traffic-light curation map. (See also the
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
* A traffic-light curation map (green / yellow / red) per cell ×
  output, suitable for direct user consumption.

### 1.4 Experiment log nomenclature ([S001](#s001) – [S024](#s024))

*A one-line description of each of the 24 core experiment-log entries
(S001–S024) cited throughout the paper. Skim this table once to make every later
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
| S005 | 22-run pilot on cell S1_M; passed all 5 preregistered gates. |
| S006 | Full 1,280-run Morris sweep (the headline experiment). |
| S007 | Targeted reproducibility check at three independent layers, all bit-exact. |
| S008 | Tier-1 statistical refinement (block bootstrap on σ, Wasserstein permutation null, Spearman CI, divergence-input mechanism). |
| S009 | Tier-2 robustness (seed stability, continuous-ARDS micro-sweep, pytest suite, GitHub Actions CI). |
| S010 | Literature-review pass; every reference DOI / PMID-verified. |
| S011 | Sex-vs-mass disentangling experiment. |
| S012 | Steady-state window cross-output audit (does F-003 / F-004 contaminate other channels? — answer: no). |
| S013 | Lexical lockdown (manuscript taxonomy normalization). |
| S014 | Trigger-pressure lockout (causally links F-004 to the VC-AC inspiration trigger). |
| S015 | Reproducibility and logic audit before publication. |
| S016 | Re-audit of the Pulse GitLab + literature (May 2026). |
| S017 | Cornish 2023 cross-mapping against the atlas's 6-output panel. |
| S018 | Blood-volume mechanism falsification (lowering male blood volume removes the all-male divergence cluster). |
| S019 | Restricted exploratory Sobol demonstrator, written under the earlier dominant-input reading; not executed, and not an implementation of the preregistered bolt-on — see §3.3.1. |
| S020 | Pre-submission novelty audit; verified that every "first" / "novel" claim in the manuscript survives a literature double-check (single citation added: Figueroa-Casas & Montoya 2016 for the F-004 clinical precedent). |
| S021 | Hyperoxia convergence: 60-run rerun at 300 s vs locked 120 s sweep window — tests whether F-003 PaO2 > 600 mmHg at FiO2 = 1.0 reflects oxygenation overshoot or transient non-convergence. |
| S022 | No-compute failure-mode attribution audit of the locked `not_steady_state` count (Appendix C). |
| S023 | Supplementary ML/SHAP cross-check of the Morris μ\* top-three input sets on the clean subset (Supplementary §S13). |
| S024 | Pre-submission claims-ledger audit — `scripts/audit_claims.py` re-derives every quantitative claim registered in the audit ledger from the canonical parquets/CSVs and verifies it against the manuscript text (394 / 394 PASS at the locked tolerance band on the authors' full data tree; 393 / 394 on a public clone, where the one anchor needing the gitignored raw S021 trajectories is auto-skipped). |

---

## 2. Methods

*This section is the engineering layer of the atlas: which Pulse
version, which inputs, which scenarios, which patient surrogates,
which Morris design, which flags. Every classifier threshold and every
input range was locked in the preregistration before the 1,280-run sweep
launched; the flag priority order was fixed after it (§2.6), and the
implemented traffic-light rule departs from the preregistered one (§3.7).*

### 2.0 Preregistered hypotheses

*The four hypotheses the atlas was built to test, reproduced verbatim
from `preregistration.md` §Primary hypotheses. They are stated here,
before the machinery, so that the rest of §2 reads as the apparatus
built to answer them; each is evaluated in §3.3 (H1), §3.4 (H2),
§3.5 (H3) and §3.6 (H4).*

> - **H1.** A small subset of inputs dominates each output's variance
>   (skewed sensitivity). Specifically: for each of HR, MAP, Vt-delivered,
>   SpO2, PaO2, PaCO2, the top-3 inputs (Morris μ\*-ranked) account for
>   ≥50% of summed μ\*.
> - **H2.** Silent clamping occurs for a measurable fraction of inputs
>   sampled from plausible adult-ICU ranges. Specifically: ≥5% of the
>   Morris sample hits at least one silent clamp.
> - **H3.** At least one solver-divergence zone exists outside the
>   previously characterized ARDS zone (0.91–0.945) within the 7-input
>   adult envelope.
> - **H4.** Male and female Pulse standard patients differ in reliability
>   behavior (clamping, divergence, or Morris μ\* ranking) on at least one
>   output. Direction of difference is not prespecified — this is the
>   **first** sex-specific comparison for Pulse.

**Erratum on the wording of H4 (terminology only, no design change).**
The phrase "Pulse standard patients" in H4 is quoted exactly as it was
registered, but it is a misnomer, and the preregistration carries its own
erratum saying so (`preregistration.md`, erratum of 2026-05-19, lines
9–36). The two bodies used here — male 18 yr / 67.3 kg / 180 cm and
female 18 yr / 56.2 kg / 163 cm — are **not** Pulse's source-code
"Standard" patients: the weights are CDC 50th-percentile
weight-for-age values at `Agemos` = 216.5, the row beginning at exactly
18.0 years, the female height is
the CDC P50 stature (coincidentally equal to Pulse's
`heightStandardFemale_cm = 163.0`), and the male height is a
researcher-fixed value chosen for a BMI of 20.8 — it is **not** Pulse's
`heightStandardMale_cm = 177.0`, but exactly 3 cm above it, and ≈ 3.8 cm
above the CDC P50 stature of 176.2 cm. (The preregistration attributes
that 3 cm gap to the CDC P50. Re-checked against the primary source, the
attribution is wrong: 3.00 cm is the distance to Pulse's own constant,
not to the CDC P50, which sits 3.8 cm below. Corrected beside the dated
record rather than inside it, on the same principle as this erratum.)
This manuscript therefore uses the term
**reference surrogate** throughout; the full provenance is in §2.3 and
Appendix B.5. The preregistered text is left unaltered above because a
preregistration is a dated record, not a living document: the correction
belongs beside it, not inside it.

The numeric criteria are unchanged by the erratum. Outcomes, stated in
full in the sections named above: H1 **PASS** (48 / 48), H2 **not
supported** (0 / 1,280), H3 **supported** (a divergence regime exists
outside 0.91 – 0.945; that it is also sex-conditioned is a finding
beyond what H3 asked), H4 **supported** (the all-male divergence
asymmetry satisfies the preregistered criterion on its own; the
gas-exchange Wasserstein result characterises how much further the
difference extends).

Each verdict is read against the hypothesis exactly as preregistered
and quoted above. H3 asks only whether a divergence zone exists outside
0.91 – 0.945; it says nothing about sex, so the sex-stratification
reported in §3.5 is an additional result and not a reason to qualify
the verdict. H4 asks for a male–female difference in **clamping,
divergence, or Morris μ\* ranking**; divergence answers it outright at
20 / 0. The Wasserstein distances on steady-state distributions, which
§3.6 reports in full, are the preregistered analysis plan's measurement
of *how far* the difference reaches — they are not the criterion the
hypothesis names, and a partial result there does not make H4 partially
supported.

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
  1. `FIO2_MAX` raised 0.95 → 1.0 (justified by the companion FiO2 = 1.0 crash probe, April
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

*The seven user-facing operational inputs and the
ranges they were swept over. MAP is *derived* from SBP and DBP rather
than swept independently, to avoid redundant sampling and constraint
violation. The DBP / SBP ≤ 0.75 ratio is enforced at the scenario
builder, not the sampler, so Morris geometry stays intact for
elementary-effects computation.*

Seven inputs swept; the HR, SBP, DBP and RR ranges were verified in Pulse boundary probes
(companion E10 boundary probe plus its HR / RR initialisation probes), the other three are clinical ranges:

| Input | Range | Units | Source |
|---|---|---|---|
| HR baseline | 50–110 | bpm | companion HR initialisation boundary probe (11 / 11 Docker runs) |
| SBP baseline | 90–120 | mmHg | E10 |
| DBP baseline | 60–80 | mmHg | E10; ratio DBP / SBP ≤ 0.75 enforced |
| RR baseline | 8–20 | bpm | companion RR initialisation boundary probe (9 / 9 Docker runs) |
| Vt target | 300–800 | mL | ARDSnet 6 mL/kg [@brower2000] to pre-ARDSnet 10 mL/kg |
| FiO2 | 0.21–1.0 | fraction | room air → pure O2 (companion FiO2 = 1.0 crash probe verifies 1.0 safe) |
| PEEP | 0–20 | cmH2O | clinical range |

*Input-ranges table — at a glance.*
**What:** the 7 user-facing operational inputs swept by Morris, their
ranges (units), and the source for each range.
**How to read it:** each row is one Morris-sampled input; the range
column lists the [min, max] interval; the source column points at the
boundary probe (companion E10, or its HR / RR initialisation and
FiO2 = 1.0 probes) or literature reference that
established the range.
**Key takeaway:** all 7 ranges sit *inside* what Pulse accepts (the four
patient ranges by construction; Pulse sets no setup bound on Vt or PEEP) — so no Morris point should ever silently
clamp, a claim §3.4 (H2) confirms empirically (0 / 1,280 clamp events).

MAP is *derived* from SBP / DBP, never sampled independently
(preregistration amendment 2026-04-22).

The DBP / SBP ≤ 0.75 ratio is enforced *at the scenario builder*
(`src/scenario.clip_dbp_to_pulse_constraint`), not at the sampler, so
Morris geometry stays intact for elementary-effects computation. Both the
requested DBP (Morris coordinate) and the applied DBP (post-clip, sent to
Pulse) are persisted in the master Parquet.

**Cost of that clip on diastolic elementary effects (quantified 2026-07-24).**
Keeping the ratio out of the sampler protects the Morris geometry, but it is
not free, and the price had never been measured. For the steps the clip
touches, the engine receives a smaller diastolic change than the Morris
coordinate records, while the elementary-effect estimator still divides by the
full nominal step.

Of the 160 sampled points, 35 carry a requested DBP above the 0.75 ratio. Two
consequences follow; both are fixed by the sample alone and are therefore
identical in all 8 cells.

* **Shortened steps.** 9 of the 20 diastolic steps are shortened. The nominal
  Morris step in DBP is 2/3 of the 20 mmHg range = 13.33 mmHg; five of the nine
  fall to 6.25 % of that (0.83 mmHg), one to 56.25 %, and three to 62.5 %. None
  is reduced to zero. The 6.25 % is exact rather than empirical: a single
  clipped endpoint at SBP = 90 caps DBP at 67.5 mmHg, so a requested step of
  13.3333 mmHg executes as 0.8333 mmHg, and 0.8333 / 13.3333 = 0.0625.
* **One-at-a-time violations.** In 8 of the 140 steps the flipped input is SBP.
  Moving SBP moves the 0.75 x SBP cap and therefore the applied DBP as well, so
  two inputs change at once and the one-at-a-time premise behind the elementary
  effect fails for those steps.

The remaining 123 / 140 steps (87.9 %) are untouched. After flag filtering,
41 / 78 clean diastolic pairs are shortened and 19 / 68 clean systolic pairs
are affected.

**Measured impact.** Recomputing the same elementary effects against the
applied step instead of the nominal one leaves the headline findings standing:
H1 holds on 48 / 48 cell x output combinations under either estimator (median
top-3 fraction 0.928 nominal vs 0.910 applied; minimum 0.658 vs 0.696), and
output MAP stays SBP-dominated in all 8 cells. What moves is DBP itself: its
mu* rises by a median factor of 2.4 (maximum 15.4), and it enters the top three
in 9 of the 48 combinations from which the reported ranking excludes it. **The
reported mu* for DBP is therefore a lower bound, not a point estimate.**

We did not substitute the applied-step estimator for the preregistered one.
Dividing by the applied step changes the finite-difference denominator on the
shortened diastolic transitions, but it does not restore the one-at-a-time
property on the eight systolic transitions where the ratio constraint moves DBP
as well, and the effective diastolic step then ranges from 0.83 to 13.33 mmHg,
which is no longer the fixed-step design the Morris index is defined on. Step
length is also structurally confounded with position in the sampled space: the
shortest steps occur only at SBP = 90 mmHg, whereas all 11 full-length
diastolic steps occur at SBP of 100 mmHg or above, so no step at the lowest
systolic setting is full length and no difference between the two estimators
can be attributed to step length alone. The applied-step mu* is therefore
reported as evidence on the direction of the clip's effect, not as a
term-by-term corrected index; and imposing the ratio at sampling time instead
would forfeit the very geometry the design exists to protect. The control for this analysis is that the
nominal-denominator recomputation reproduces `results/morris_indices.parquet`
exactly — 318 / 318 rows, relative deviation 0, identical clean-pair counts —
so the comparison is against the published pipeline rather than against a
re-implementation of it. Every figure above is re-derived from the canonical
artefacts by `scripts/audit_claims.py` (anchors `T5.clip.*`) and is reported to
readers in Supplement §S3.7.

**Robustness of the systolic ranking under six estimators (added 2026-08-06).**
The disclosure above prices the clip but leaves one question open: does the
published finding that MAP is SBP-driven in every cell depend on the affected
steps? Four further estimators answer it. The *uncontaminated-step* estimator
drops every clean pair in which the applied DBP co-varies with SBP. The
*trajectory-matched* variant additionally restricts every input to the 12 of 20
trajectories whose systolic step is uncontaminated, so that no input is
estimated on more data than another. Two *combined* estimators apply the
applied-step denominator and the contaminated-pair exclusion at once — a
pairing evaluated neither by the analysis above nor by the published index, and
the reconstruction a methodological reviewer is most likely to build.

SBP remains rank 1 for MAP in all eight cells under all six estimators
(nominal-step, applied-step, uncontaminated-step, trajectory-matched,
hybrid-combined, matched-combined). DBP is the runner-up in all eight cells
under the combined estimators — the applied-step denominator lifts it past HR
in S3_M and S3_F, where HR is second under the nominal estimator — so the
smallest margin is a 1.22-fold mu* ratio, in S2_M. Under the hybrid-combined
estimator DBP would overtake SBP in a cell only if its applied-to-nominal mu*
ratio exceeded that cell's uncontaminated-SBP-to-nominal-DBP ratio; the former
ranges from 1.131 to 3.289 across cells and the latter from 2.266 to 4.669, so
the condition is met in no cell.

**Transition-stratified comparison, and what it does not settle.** Dropping the
contaminated pairs lowers mu\*(SBP → MAP) in 8 of 8 cells (median −10.4 %),
which is consistent with upward contamination but confounded with position,
since the contaminated steps sit at the low-SBP end of the domain. Three
systolic transitions carry both contaminated and uncontaminated steps, so the
two groups can be compared where the systolic start and end values are
identical.

| SBP transition | Contam. pairs | Uncontam. pairs | Median \|EE\| contam. | Median \|EE\| uncontam. | Difference | Applied-DBP path (mmHg) |
|---|---:|---:|---:|---:|---:|---|
| 100-to-120 | 3 | 9 | 20.44 | 15.74 | +4.70 | 75 → 80 (midpoint 77.5) |
| 110-to-90 | 15 | 16 | 24.94 | 17.26 | +7.68 | 80 → 67.5 (midpoint 73.75) |
| 120-to-100 | 1 | 19 | 20.32 | 16.74 | +3.59 | 80 → 75 (midpoint 77.5) |
| 90-to-110 | 0 | 5 | — | — | not evaluable | — |

Counts are clean elementary-effect pairs pooled across the eight cells, not
trajectories of the shared 20-trajectory design. The contaminated group has the
higher median absolute effect in all three evaluable transitions, and the
stratified contrast stays positive in every leave-one-transition-out analysis.
Requested DBP is perfectly collinear with contamination: structurally for the
100-to-120 and 120-to-100 transitions, whose 75 mmHg ceiling no lower grid
level can exceed, and as an artefact of the realised Morris draw for 110-to-90.
The observed ordering does not support a simple monotonic explanation by mean
applied-DBP level alone — the largest contrast occurs for 110-to-90 despite its
lower mean endpoint DBP — and mean endpoint DBP is in any case only a coarse
proxy for the level at which the elementary effect is evaluated. These results
are consistent with an influence of applied-DBP co-variation but do not
establish a causal contribution. Separating the two would require re-running
each contaminated step along the one admissible rectangular path, holding the
applied DBP fixed while SBP moves; that probe campaign is specified and
deferred, because the ranking claim is already robust without it.

Both analyses are reproduced by `scripts/s032_uncontaminated_step_analysis.py`
and `scripts/s032_transition_stratified_analysis.py`, each gated on reproducing
the nine S3.7 counts and the 318 published Morris indices exactly before it
reports anything of its own.


### 2.3 Scenarios and patients

*The 4 scenarios × 2 patient surrogates = 8 cells of the atlas.
Healthy and three ARDS severities, calibrated on the male reference
body against the Berlin definition's PaO2 / FiO2 bands and bracketing
Pulse's 0.91 – 0.945
solver-instability zone, each run on the male and female reference
bodies. Ventilator mode is VC-AC only — the configuration
Pulse's own validation table reports as most accurate (0.07 – 2.25 %
Vt error vs PC-AC's 11.3 – 25.3 %).*

Four scenarios × two patients = 8 cells:

* **S1** Healthy ventilated adult, ARDS impairment 0.00.
* **S2** Mild ARDS, impairment 0.26 (Berlin mild band).
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
the reference ventilation setting that the Atlas sweep is built
around — based on the ARDSnet low-tidal-volume framework (VC-AC,
Vt = 6 mL/kg actual body weight, PEEP = 10 cmH2O, FiO2 = 0.4) —
direct measurement of the documented mapping on the male reference
body in a 28-run impairment sweep (`Pulse_translation_new`, original ARDS severity calibration)
produced P/F ratios of
199 / 150 / 119 mmHg — leaving Pulse's "mild" fraction (0.3) at the
moderate / mild boundary and its "severe" fraction (0.9) well inside
the Berlin moderate band. The empirically calibrated mapping
{0.26, 0.60, 0.95} used here was selected to land near the Berlin mild
and moderate band centres and just inside the severe band's upper
boundary (P/F ≈ 256 / 150 / 96 mmHg) under the same ventilation
settings. The calibration is therefore *ventilation-setting-dependent*
rather than a global correction; Pulse's documented mapping may
reproduce its claimed P/F values under different Vt / PEEP / FiO2
combinations, but does not at the reference ventilation setting. The
mild, moderate and severe labels name the band each scenario was
calibrated to, not a diagnosis of each run: individual runs vary FiO2
and PEEP across the sweep and need not meet that band's P/F and PEEP
criteria. Full
contrast table, ventilation-setting disclosure, three-source
convergence for the 0.91 – 0.945 solver-instability zone, and the
ARDS calibration provenance are in Appendix B.3.

* **Male reference surrogate:** age 18, weight 67.3 kg, height 180 cm (BMI 20.8).
* **Female reference surrogate:** age 18, weight 56.2 kg, height 163 cm (BMI 21.2).

*Provenance.* Body weights are the CDC 50th-percentile weight-for-age
values at `Agemos` = 216.5 (67.28992603 kg boys, 56.22969564 kg girls;
@kuczmarski2002cdc, <https://www.cdc.gov/growthcharts/>), rounded to 67.3 and
56.2 kg. CDC lists age at the half-month point standing for the whole month, so
that row denotes 216.0–216.99 months, the interval beginning at exactly 18.0
years, and the preregistration's provenance erratum is correct in naming 18
years. An earlier version of this passage placed the weights at a 214-month row
and treated the `Agemos` = 218.5 values (67.64 and 56.41 kg, in fact 18 y 2 m)
as the 18.0-year ones; both were wrong, and nothing registered or simulated
changes (§B.5; Supplement §S3.4, body-dimension provenance). They were inherited unchanged from
the companion `Pulse_translation_new` pediatric-translation pipeline
where they form the 18-year endpoint of its CDC progression. The
female height (163 cm) is the CDC P50 stature for 18-year-old girls [@kuczmarski2002cdc].
The male height (180 cm) is a researcher-fixed rounded value chosen
to yield a healthy baseline BMI of 20.8; this is ≈ 3.8 cm above the CDC
P50 stature of 176.2 cm (and exactly 3 cm above Pulse's own
`heightStandardMale_cm = 177.0`), and is reported here transparently
rather than retro-fitted to a citation. The full engine-source comparison — including Pulse's
own internal `heightStandardMale_cm` / `heightStandardFemale_cm`
constants — is in Appendix B.5.

Companion verification
(`Pulse_translation_new` female-surrogate engine tests and the
male/female side-by-side verification) established that the female
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
verification (`Pulse_translation_new` female-surrogate engine tests
and male/female side-by-side verification) further found
that PC-AC over-delivery scales inversely with body weight (female
+58.9 % vs male +24.0 % at PIP = 20 cmH2O), reinforcing the
preregistration's VC-AC restriction.

### 2.4 Simulation cadence

*Temporal sampling decisions: 120 s simulation, 5 s CSV sample
interval, locked steady-state window [60, 120] s — 13 points per
clean run, enough resolution to compute steady-state mean, variance,
drift, and flatline diagnostics for the detector without storing
high-frequency time-series.*

120 s recording, after Pulse's patient stabilisation and a 120 s
ventilator-settling phase; sample interval 5 s, steady-state window
[60, 120] s (13 points). Detector enforces 13 points / clean run.

### 2.5 Morris sampling

*Why Morris elementary effects is the right screening method here: it
ranks inputs by overall importance (μ\*) and flags non-linearity (σ)
at a small fraction of the cost of a full variance-based analysis.
Implementation uses SALib's `morris.sample(N=20, num_levels=4,
seed=42)` → 160 unique input points, identical across cells so
elementary-effect rankings are directly comparable.*

The Morris elementary-effects design [@morris1991], with the
μ\* refinement of [@campolongo2007],
is an efficient global screening method that varies one input at a
time along randomised trajectories; it ranks inputs by
overall importance (μ\*, the mean of absolute elementary effects)
and flags non-linearity or input-input interaction (σ, the standard
deviation of those effects), at a small fraction of the cost of a
full variance-based analysis. Implementation: SALib's
`morris.sample(N=20, num_levels=4, seed=42)` [@iwanaga2022; @herman2017salib] ⇒
160 unique input points. The same 160 points drive every
cell, so EE rankings are directly comparable across cells. The
trajectory count N = 20 was fixed in preregistration: large
enough to give stable μ\* rankings, small enough to keep the full
sweep laptop-feasible. Sample
persisted at `data/runs/full_sweep/morris_sample.parquet`.

### 2.6 Detector

*The four orthogonal flags that classify every run: `clamped` (Pulse's
setup log records a rejected setup input), `diverged` (NaN / Inf / exit code ≠ 0),
`implausible` (steady-state mean outside hard physiological bounds),
and `not_steady_state` (flatline, drift, or excess variance). All
thresholds were locked in preregistration before data collection. The
priority order `clamped > diverged > implausible > not_steady_state >
clean` for primary-flag analyses was fixed after the sweep, not
preregistered.*

**Why this priority order.** The four flags trace the chronology of
failure modes a Pulse simulation could exhibit, from input handling
through solver execution to output evaluation against biological and
dynamic criteria:

1. **`clamped` — input-contract breach.** Pulse did not accept at
   least one setup input as submitted (its setup log matches a
   rejection pattern). The simulation no longer
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
   60 s steady-state — e.g. SpO2 = 0.40, which on the standard
   Severinghaus 1979 dissociation curve corresponds to PaO2 ≈ 23 mmHg.
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
upstream regex was replaced with four patterns aimed at Pulse's rejection
messages:

```python
r"baseline of [\d\.]+ \S+ is too (?:high|low)"
r"maximum [\w\s]+ baseline allowed is"
r"must be modeled by adding/using a condition"
r"is outside the valid range"
```

The previous regex set generated 100 % false-positive `clamped` flags by
matching Pulse's normal solver convergence text (`Resetting the target for
X to Y`); this would have made the `clamped` flag useless across the entire
sweep. On the calibration runs, the four-pattern set fired on both
deliberate-clamp probes of the [S005](#s005) pilot (SBP = 140 and
DBP = 85 mmHg, each rejected at setup with exit code 1) and on none of the
eight [S004](#s004) smoke-test runs; the patch note below replays both
pattern sets over every Pulse log on disk. The pattern
`is outside the valid range` matches no message in the Pulse 4.3.1 source
and fired on no Pulse log on disk.

**Patch of 2026-07-26, applied after the sweep.** The four patterns above
are the set that classified all 1,280 published runs, and are left as
written for the historical record. Two changes were made afterwards, giving
the five-pattern set now in `src/detector.py`:

```python
r"baseline of [\d\.]+ (?:\S+ )?is too (?:high|low)"  # unit token now optional
r"maximum [\w\s]+ baseline allowed is"
r"minimum [\w\s]+ baseline allowed is"               # added, mirrors "maximum"
r"must be modeled by adding/using a condition"
r"is outside the valid range"
```

Pulse's `SetupPatient.cpp` builds ten baseline-rejection strings, nine of
which write the unit between the value and `is`; the heart-rate lower bound
(L311) is the sole exception. The original first pattern required that
token, so a heart rate below 50 bpm was rejected by Pulse at setup yet never
raised `clamped`. Replaying both pattern sets over all 3,349 Pulse logs on
disk flips exactly one run — the S030b probe written to expose the gap — and
no run in the published sweep, whose requested heart rates never leave
[50, 110] bpm. The published classification is therefore unchanged. The gap
never lost a run in any case: a setup rejection exits non-zero with no CSV,
so `diverged` fires instead.

**Hard physiological bounds for the `implausible` flag.** The table
below was committed in `preregistration.md` §Flags before any atlas
data was collected, and is reproduced here for reader convenience.
Each `(lower, upper)` pair encodes one of two logical categories:
(a) a physical / definitional ceiling for which no citation is
needed, or (b) a clinical *"incompatible with a 60 s steady-state
in the locked window"* threshold. Only the SpO2 upper bound falls
in category (a); every other bound is category (b), a judgment call,
cited where a source exists. No bound rests on an equipment
specification.

| Output | Lower | Upper | Source (lower / upper) |
|--------|------:|------:|------------------------|
| HR (bpm)    |  20 |  220 | Deliberately permissive at both extremes. Upper: sinus rates exceeding (220 − age)/min reduce cardiac output and myocardial perfusion [@marini2018critical Ch.1], which gives 202 bpm on the 18-year-old reference bodies, so the 220 bpm intercept sits above it; lower: pathological bradycardia depresses cardiac output and O2 delivery [@marini2018critical Ch.1], but no numeric floor is asserted there, so 20 bpm is a conservative outer bound |
| MAP (mmHg)  |  30 |  180 | Lower: well below both the 70 mmHg at which the Sepsis-3 SOFA cardiovascular score first registers organ dysfunction [@singer2016] and the Surviving Sepsis Campaign initial MAP target of 65 mmHg [@evans2021sepsis]; upper: ESH 2023 hypertensive emergency, i.e. grade 3 hypertension (SBP ≥ 180 and/or DBP ≥ 110 mmHg) with acute symptomatic organ damage [@mancia2023esh] |
| Vt (mL)     |  50 | 1500 | Lower: below anatomical dead space (~150 mL adult) [@west2020respiratory Ch.2] — alveolar ventilation impossible; upper: ~3–4.5× ARDSnet protective ventilation (6 mL/kg PBW [@brower2000] ≈ 450 and 330 mL on the male and female surrogates) and above the 10–15 mL/kg tidal volumes that were standard practice before lung-protective ventilation [@marino2013icu Ch.25] |
| SpO2 (%)    |  50 |  100 | Lower: oxyhemoglobin dissociation curve P50 (SpO2 = 50 % ↔ PaO2 ≈ 27 mmHg [@severinghaus1979]); upper: hemoglobin saturation ceiling (definitional) |
| PaO2 (mmHg) |  20 |  600 | Lower: SpO2 ≈ 0.32 on the standard Severinghaus 1979 dissociation curve [@severinghaus1979] — a value incompatible with a stable steady state sustained over the 60 s evaluation window, well inside Berlin severe-ARDS oxygenation territory [@ards2012]; upper: classifier-conservative choice below the alveolar-gas-equation ceiling [@west2020respiratory Ch.5] — supplementary `HARD_BOUNDS_PHYSIOLOGICAL` sensitivity analysis at 700 mmHg reported in §3.8 |
| PaCO2 (mmHg) | 10 |  120 | Lower: profound respiratory alkalosis from sustained maximal hyperventilation; upper: deliberately permissive rather than clinical — in a 1,899-patient ARDS cohort from 927 ICUs in 40 countries, the cutoffs categorising maximum PaCO2 in the first 48 h of ventilation placed approximately the 95th percentile at 70 mmHg [@nin2017], so a 120 mmHg ceiling leaves severe but clinically observed hypercapnia unflagged and marks only values well beyond the reported range |

The bound is therefore a *time-window-conditional* operational
threshold, not a raw biology threshold: a real patient transiently
crossing PaO2 = 18 mmHg during cardiac arrest is biologically
possible, but a Pulse simulation reporting a 60 s steady-state mean
PaO2 = 18 mmHg at FiO2 = 0.21 on a *resting healthy adult* indicates
that the engine has produced an output incompatible with the
simulation's own input setup. The `implausible` flag isolates that
class of inconsistency. Within category (b), the exact numerical
choice (e.g., PaO2 lower 20 vs 25 mmHg) is a defensible judgment
call rather than a unique biological constant; §4.5 acknowledges
this and §3.8 demonstrates the sensitivity-analysis pattern on the
single most contestable bound (PaO2 upper, raised from 600 to 700
mmHg per the alveolar-gas-equation ceiling). No locked threshold has
been adjusted post-hoc — the only amendment to a locked threshold
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
standard critical-care monitoring practice rather
than in mortality-incompatibility primary literature; where no
source states a numeric drift magnitude, the row says so.

| Output | Drift threshold per 60 s | Clinical-meaningfulness anchor |
|--------|--------------------------|--------------------------------|
| HR     | 5 bpm                    | A preregistered convention, not a sourced threshold: the smallest heart-rate excursion treated as an active trajectory rather than monitor noise. No numeric drift criterion for heart rate was found in the cited critical-care sources |
| MAP    | 5 mmHg                   | The clinically decisive MAP band is narrow: the Sepsis-3 SOFA cardiovascular score registers organ dysfunction below 70 mmHg [@singer2016], the Surviving Sepsis Campaign targets 65 mmHg on resuscitation, and organ perfusion declines below approximately 60 mmHg, tracking linearly with MAP [@evans2021sepsis]. These landmarks lie 5 mmHg apart, so a drift of that size is clinically consequential rather than nominal |
| Vt     | 50 mL                    | ~ 0.7–0.9 mL/kg ideal body weight across the two surrogates — within the noise band of breath-to-breath measurement at ARDSnet Vt, 6 mL/kg predicted body weight [@brower2000] |
| SpO2   | 2 percentage points      | A preregistered convention, not a sourced threshold: the smallest saturation change treated as a genuine desaturation rather than monitor noise. No numeric desaturation-drift criterion was found in the cited critical-care sources |
| PaO2   | 15 mmHg                  | A 15–71 % fraction of one Berlin P/F band depending on FiO2 — sub-band at the high-FiO2 end of the sweep but approaching one band at room air; clinically meaningful oxygenation change over a 60-second window [@ards2012] |
| PaCO2  | 5 mmHg                   | Roughly one alveolar-ventilation step under ARDSnet protective ventilation per minute — clinically meaningful CO2 change [@west2020respiratory] |

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

*The five preregistered gates the 22-run pilot on cell S1_M had to
pass before the full 1,280-run sweep launched: success rate, detector
self-consistency, 13-point steady-state window, clamp-regex
reachability, and Pulse determinism. The pilot also surfaced and
resolved three pipeline bugs before the compute budget was spent.*

A 22-run pilot on cell S1_M with 16 unique Morris points + 4
reproducibility reruns + 2 deliberate clamp probes verified all five
preregistered gate criteria: success rate, detector self-consistency,
13-point steady-state window, clamp regex reachability (probes), and Pulse
determinism (1e-6 relative tolerance across 24 (output × rerun)
comparisons). Pilot also surfaced and resolved three pipeline bugs (time-
origin, case_id collision, G4 unreachability from locked Morris ranges)
*before* the full sweep launched.

### 2.8 Hardware and reproducibility

*The laptop hardware envelope (i5-11400H, 8 GB RAM, CPU-only), the 2–3
parallel Docker throughput verified in [S001](#s001), and the twelve
independent verification points that make the published numbers
reproducible bit-exactly. A pre-submission Phase-4 re-execution
(1,280 / 1,280 runs) extends bit-exact reproduction from the
[S015](#s015) 40-run audit to the full envelope.*

i5-11400H (6 physical / 12 logical cores), 8 GB RAM; Pulse is CPU-only, so
neither of the laptop's two GPUs (Intel UHD, NVIDIA RTX 3050) is used. Docker
allocation 3.95 GB / 12 CPU. Two-to-three parallel containers per the
verified [S001](#s001) budget. Pulse is bit-exact deterministic for fixed
inputs ([S005](#s005) G5). The full sweep required approximately 14 h of
active elapsed time on this hardware (Supplement §S12).

The atlas's published numbers have twelve independent verification
points (Pulse determinism, pipeline + analysis correctness, and
independent reproducibility layers) detailed in
[Supplementary S10](../preprint/supplementary.md#s10);
all twelve passed with zero violations. [S007](#s007) deliberately rejected a
full 1,280-simulation re-execution because re-running the same code
gives identical CSVs by construction and cannot detect bugs in the
code being re-run; the independent-layer approach catches strictly
more error classes at ~ 1 % of the compute cost.

**Phase-4 audit-driven re-execution (2026-05-16 → 2026-05-18).** As a
pre-submission belt-and-braces check on top of the twelve verification
points above, two complementary re-executions were performed under the
current `pulse-atlas-engine` image (hash `b2e0e807803d`, the
post-[S014](#s014)-patch rebuild — a different image hash than the
`3b18bdc08660` build that produced the canonical sweep on 2026-04-26):

* **(i) Phase 4a — same-seed full re-execution.** All 1,280 runs of the
  canonical Morris sweep were re-executed from the locked sample
  (`data/runs/full_sweep/morris_sample.parquet`; `seed=42`,
  `trajectories=20`, `levels=4`) against the current image, with output
  written to a parallel directory tree (`data/runs/full_sweep_repro/`)
  so the canonical artifact was not touched. The re-execution ran on the
  maintainer's i5-11400H laptop at 2 parallel Docker workers (the
  verified-safe hardware cap, §2.8). SHA-256 comparison of every
  `output.csv` against canonical gave **1,260 / 1,280 bit-identical
  completed runs and 20 / 20 originally-diverged runs reproducing
  divergence with `exit_code = 1`** (i.e. the same 20-run male-extreme
  cluster that §3.5 links to blood volume). **Zero
  deviations, zero clean-↔-diverged asymmetries, zero missing files.**
  The [S015](#s015) audit's 40-run bit-exact result is therefore extended to
  the full 1,280-run envelope, and the [S014](#s014) SDK sed-patch is
  empirically a no-op on the canonical sweep at every cell. Full report
  in `data/runs/full_sweep_repro/sha_compare.json`.

* **(ii) Phase 4b — new-seed Morris stability on cell S2_M.** A
  fresh Morris sample at `seed=44`, `trajectories=20`, `levels=4` (160
  unique points, matching canonical sample size; different seed from
  both canonical `seed=42` and the prior [S009](#s009) stability check at
  `seed=43, trajectories=10`) was run on the mild-ARDS male cell.
  Wall time: 1 h 34 m. **The dominant input by μ\* was preserved for
  all 6 outputs**, and top-3 input sets matched canonical in 4 / 6
  outputs (top-3 orders in 3 / 6); disagreements were confined to the
  second- and third-ranked inputs, where μ\* magnitudes are similar across
  competing inputs — consistent with the trajectory-bootstrap CI
  reported in §3.3.1 and the Spearman ρ analysis in §3.6.
  In full transparency, two sample-dependent quantities surfaced.
  **(a)** The S2_M divergence count went from 4 / 160 (canonical
  `seed=42`) to 7 / 160 (`seed=44`). All 7 new-seed divergences
  occurred at HR = 50 and SBP = 90, with RR in the upper two grid
  levels (16 or 20) and FiO2 likewise in its upper two levels (0.737
  or 1.0); only 1 / 7 occurred at FiO2 = 1.0, against 13 / 20 in the
  canonical sweep. The broad input-space regime that §3.5 / §3.5.1
  identify is therefore preserved, whereas both the divergence count
  and the within-regime sampling pattern are sample-dependent.
  **(b)** The PaO2 σ / μ\* point estimate on FiO2 moved from 0.667 (canonical, in
  the §3.3.1 Group-B "promote" set) to 0.547 (new-seed, below the
  preregistered 0.6 trigger), showing that the point-estimate trigger
  is seed-sensitive at the threshold. That sensitivity is why §3.3.1
  reports a ratio-aware bootstrap alongside the point estimate; it
  carries no implication about whether the Sobol bolt-on was worth
  running, which §3.3.1 settles on compute budget. Per-run timings,
  `phase4b_morris_S2M_seed44.parquet`, and the top-3 comparison are
  in `results/`.

Neither phase falsified a manuscript claim. Phase 4a strengthens the
determinism statement to the full sample size; Phase 4b motivates the
uncertainty-aware reading of the trigger that §3.3.1 now adopts.

**Programmatic manuscript-numbers audit ([S024](#s024), 2026-05-22).**
Independently of the bit-exact re-execution above, a third
verification layer closes the data-integrity loop at the *manuscript*
level. The read-only Python script
[`scripts/audit_claims.py`](../scripts/audit_claims.py) registers
each quantitative claim it covers — Tier-1 (Abstract, Key
Contributions, hypothesis verdicts, Table 1, Figure 6 traffic-light)
and Tier-2 (per-cell numbers in §3.3 / §3.4.1 / §3.5 / §3.6 / §3.8 /
§3.8.1, plus Appendix C and §4.5 S023) among them — as a `Claim`
record (manuscript value,
source artifact, computed value, tolerance rule), re-derives the
computed value from the canonical parquets / CSVs / JSON summaries,
and verifies the manuscript text against each computed value under
an explicit per-class tolerance band (`exact_int` for integer counts;
`pct_1dp` / `pct_whole` for percentages at their displayed precision;
`displayed_1dp` / `displayed_2dp` / `displayed_3dp` for floats at
their displayed precision; a 1 × 10⁻⁹ IEEE-754 epsilon protects
against half-precision rounding boundaries). The current report on
the locked manuscript is **394 / 394 PASS, 0 WARN, 0 FAIL** on the
authors' full data tree. On a public clone, one anchor — T1.06u, the
S021 time-to-95%-plateau, which requires the heavy raw per-run
trajectories that are gitignored — is automatically skipped, so the
script reports **393 / 394 PASS** with one explicitly-flagged SKIPPED
(the headline target of 394 is computed dynamically as anchors-run
plus anchors-skipped, so it cannot go stale). The
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
the 13-point steady-state window; `src/detector.py:413`), and the
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
(preregistered but deferred on compute budget; see §3.3.1), 1-Wasserstein
distance, the permutation null, Spearman ρ, BH-FDR
control, and Hoeffding / Holm–Bonferroni (external; used by Cornish
2026, §4.4). First appearance of each test in §3 is therefore
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
  flagged non-linearity, and discuss in §3.3.1 why the design that
  trigger selected exceeded its own preregistered compute envelope, so
  the bolt-on is reported rather than executed.

* **1-Wasserstein distance.** A distance between two probability
  *distributions* on a one-dimensional output. Intuitively: the
  minimum "work" needed to transport one histogram onto the other,
  in the output's natural units (e.g. mmHg, mL, bpm). Larger value
  = more separation; zero means the two distributions are identical.
  Used in §3.6 to quantify how different male vs female clean-run
  output distributions actually are.

* **Permutation null (pooled and re-split).** A reference
  distribution built by randomly splitting the *combined* M + F clean
  runs into two groups the same size as the original M and F groups, then
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
  2026).** Used by [@cornish2023] in their causal-falsification
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
FiO2 sensitivity falls sharply in severe ARDS, and output Vt tracks input Vt at μ\* ≈ 500 mL across every
cell.*

Figures 2 a–f show the Morris μ\* heatmap for each of the six outputs.
Rows are the seven swept inputs; columns are the eight (scenario, sex)
cells. The colour scale is the magnitude of the elementary effect — how
much each output moves when the corresponding input is perturbed. Four
visual patterns dominate:

* **Cardiovascular outputs are cardio-input dominated.** Output HR is
  driven by input HR in every cell (μ\* ≈ 55 in healthy → ≈ 95 in
  severe ARDS); output MAP is driven by SBP in every cell (μ\* ≈ 17 –
  20). Ventilator settings still contribute smaller, non-zero effects.
* **Gas-exchange outputs are ventilator-driven.** PaO2 is dominated by
  FiO2 in S2 / S3 (μ\* peaks at 147 mmHg in S2_F). PaCO2 is dominated by Vt in most cells, consistent
  with the alveolar-ventilation identity
  $\dot{V}_A = \mathrm{RR} \cdot (V_T - V_D)$
  (where $\dot{V}_A$ is alveolar minute ventilation, RR is set
  respiratory rate, $V_T$ is delivered tidal volume, and $V_D$ is
  the anatomical dead-space volume; West *Respiratory Physiology*
  Ch. 2 convention). SpO2 is also ventilator-driven but on a small
  numerical scale (μ\* ≤ 0.13) because it is recorded as a fraction:
  the largest value, 0.12 in S3, would read 12 in percentage points.
* **The ARDS gradient is visible.** PaO2's FiO2 sensitivity peaks in
  S2 (μ\* = 133 – 147 mmHg), remains substantial in S3 (μ\* = 84 – 93
  mmHg), and falls sharply in severe ARDS (μ\* = 31 in S4_M, on a
  single elementary-effect pair; not estimable in S4_F under the
  four-flag screen). FiO2 nevertheless remains the rank-1 input wherever
  it is estimable. The fall is consistent with the model's
  severity-dependent gas-exchange changes; shunt fraction was not
  recorded, so a shunt-mediated reading is not directly tested.
* **Output Vt tracks input Vt at μ\* ≈ 500 mL** in every cell. In VC-AC
  mode, asking Pulse for a 500 mL tidal volume produces close to a
  500 mL delivered tidal volume, cell-invariant. The cells where this
  coupling is disrupted are the F-004 oscillation runs (§3.8).

**Bootstrap 95 % CI on μ\*** (1,000 resamples) is reported alongside
each μ\* point estimate in the table; CI overlap between the top-3 and
the rest is the formal H1 test.

**External cross-validation against an OAT precursor.** Companion
one-at-a-time probing prior to the Atlas (`Pulse_translation_new` E4,
±10 % perturbations on healthy and ARDS-moderate cells, n = 74 Docker
runs) reported the FiO2 → PaO2 elasticity collapsing from 1.32 in
healthy to 0.26 in moderate ARDS — an ~80 % attenuation, consistent
with rising shunt. The Atlas Morris μ\* for PaO2 ~ FiO2 reproduces
both the direction and roughly the magnitude of this attenuation:
μ\* peaks at S2 / S3 (147 mmHg in S2_F) and falls to 31 mmHg in
S4_M, a ~79 % drop resting on a single elementary-effect pair. Elasticity (local %-change/%-change) and μ\*
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
this concentration into a few dominant input rows visually supports H1's "skewed sensitivity"
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
preregistered Sobol bolt-on and explains why the design its trigger
selects exceeds the preregistered compute envelope, so it is reported
rather than executed.*

Top-3 fraction of summed μ\* per cell × output:
* All 48 combinations are ≥ 0.5 (the preregistered threshold).
* Median 0.928; range 0.658 – 0.998.
* Lowest fractions are in S4 (severe ARDS), and concentrate on the
  gas-exchange outputs PaO2 and SpO2: S4_F SpO2 (0.658), S4_M SpO2
  (0.703), S4_F PaO2 (0.707), S4_M PaO2 (0.727). Physiological
  interpretation: at 95 % alveolar impairment, increased venous
  admixture could limit FiO2's marginal effect on arterial oxygenation,
  consistent with established high-shunt physiology; the atlas did not
  record Pulse's shunt-fraction output, so this mechanism was not
  tested directly. The residual sensitivity
  redistributes across PEEP and the cardiovascular inputs (HR, SBP, DBP
  — arterial O2 becomes sensitive to mixed-venous content, and thus to
  cardiac output, under high shunt) rather than concentrating on a
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

![Figure 3. H1 — top-3 fraction of summed μ\* per cell × output (48 combinations). Heatmap with RdYlGn palette, crossover at 0.5 (the preregistered H1 threshold). Lowest fractions are in S4 (severe ARDS) gas-exchange outputs (S4_F SpO2 0.658; the reduced FiO2 effect is compatible with high-shunt physiology, but Pulse's shunt-fraction output was not recorded). Source: `results/h1_top3_fraction.csv` (S006).](../figures/fig03_h1_top3_fraction.png)

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

* **Group A — saturation-boundary cells (2 of 8 cells).** Both are SpO2
  in healthy patients: (S1, F, SpO2, PEEP) with μ\* = 0.0037 and
  σ = 0.0068, and (S1, M, SpO2, Vt) with μ\* = 0.028 and σ = 0.023, each
  estimated from only 3–4 clean elementary-effect pairs. The pairs taken
  at FiO2 ≈ 0.47 sit at the hemoglobin saturation ceiling (SpO2
  0.997–0.999) and carry effects of at most 0.003; the large effects
  (|EE| 0.014–0.049) all come from pairs taken at FiO2 = 0.21, where SpO2
  is 0.95–0.96 — three of the four pairs there (one Vt step moves SpO2
  from 0.962 to 0.929). The high
  σ / μ\* therefore reflects an effect that depends on FiO2, measured on
  very few pairs — not floating-point noise.

* **Group B — known nonlinear physiology (6 of 8 cells).** Four of
  these are the FiO2 → PaO2 cells in ARDS scenarios: (S2 / S3, M / F,
  PaO2, FiO2), with μ\* in the 84 – 147 mmHg range and σ / μ\* between
  0.64 and 0.94. This is the regime where venous admixture caps
  oxygenation gain per FiO2 increment — an established physiological
  non-linearity. The remaining two cells
  reflect minute-ventilation coupling on PaCO2: RR → PaCO2 in healthy
  males (S1_M, σ / μ\* = 0.87), and Vt → PaCO2 in severe-ARDS
  females (S4_F, σ / μ\* = 0.66). Both are predicted by the
  alveolar-ventilation identity
  $\dot{V}_A = \mathrm{RR} \cdot (V_T - V_D)$ that governs CO₂
  elimination.

**CI-aware re-evaluation of the trigger.** The 8 / 48 promotion count
above is a *point* estimate. To attach a confidence interval to it,
we resampled trajectories (block bootstrap, 1,000 resamples, same
RNG seed as the μ\* CI) and recomputed σ / μ\* on each resample.
Per-cell `sigma_lo` / `sigma_hi` columns are persisted in
`results/morris_indices.parquet`. What that bootstrap returns depends
on two choices that an earlier version of this subsection got wrong:
which of two σ / μ\* CI formulas is used, and whether the trigger is
read on the dominant input alone or on the top three the
preregistration actually names. Both are settled in the methodological
note below, which carries the current counts. The four-bucket table
that stood here reported a non-linear count of zero and a straddling
count of twelve; both were wrong, and the table is removed rather than
rebuilt, since the note below states what the corrected reading gives.

One of its buckets survives unchanged, because it reflects data
availability rather than any bootstrap formula: the cells with **no
estimable σ / μ\* CI at all**. Three lie in S1_F where the dominant
input is Vt — the Vt one-at-a-time (OAT) step has only one clean
trajectory pair (S1_F × {PaCO2, PaO2, Vt}). Two lie in S4_M where the
dominant input is FiO2 — the FiO2 OAT step has only one clean
trajectory pair (S4_M × {PaO2, SpO2}). The *which-input-lacks-pairs*
differs between the two groups (Vt in S1_F vs FiO2 in S4_M); per-input
gaps are summarised at cell level in the §4.5 limitations.

*Methodological note (σ / μ\* CI formula).* Two formulas are available once a
confidence interval is put on σ / μ\*, and they do not agree. The first divides
σ_hi — the upper 97.5-percentile of the trajectory-level block bootstrap on σ
(`_block_bootstrap_sigma_ci` in `src/analysis_morris.py`) — by the μ̂\* point
estimate, treating the denominator as fixed. The second, which this manuscript
now adopts, resamples trajectories and recomputes σ_b / μ\*_b *jointly* per draw,
so the interval covers the ratio itself. The first formula ignores the positive
covariance between σ and μ\*, which widens its interval in an uncontrolled
direction; it is retained here only as the historical variant.

The two do not lead to the same conclusion, and an earlier version of this
section stated otherwise. Under the ratio-aware formula the dominant-input
bucketing is 31 / 48 CI-robustly linear under every one of the five bootstrap
seeds, and one dominant input — FiO2 on PaO2 in S3_M — is CI-robustly
non-linear under all five; one other, FiO2 on PaO2 in S3_F, is non-linear
under two of the five seeds only. The count is not zero under either reading. Applying the rule the preregistration
actually states — the top-three inputs, not the dominant one alone — 23 of the
144 top-three inputs hold a lower bound at or above 0.6 across five independent
seeds. The earlier claim that "zero cells are CI-robustly non-linear under
either formula" was wrong on both counts and is withdrawn.

**The Sobol bolt-on was not executed because the design its own
trigger selects exceeds the preregistered compute envelope.** Applying
the rule the preregistration states — the top-three inputs of every
cell, not the dominant one alone — the point-estimate trigger fires on
72 of the 144 top-three inputs, spanning 43 of the 48 cell × output
combinations. The same preregistration capped the bolt-on at 1,500
additional runs. A Sobol sample cannot be shared across cells, because
each scenario–sex cell is a different model; it is shared across the six
outputs of one cell, because they all come from the same Pulse run. The
43 triggered combinations therefore fall in eight cells, carrying between
three and six distinct promoted inputs each, for 6,144 runs under the
preregistered 64 × (2k + 2) formula. Computing only the first-order and
total indices the analysis plan asks for, at 64 × (k + 2), lowers this to
3,584; a full seven-input design in every firing cell would cost 8,192
and 4,608 respectively.
The bolt-on exceeded its own preregistered envelope under every one of
these readings, by a factor of 2.4 to 5.5, and is therefore reported
rather than executed.

The reason is the budget, not an absence of non-linearity to decompose.
The post-hoc ratio-aware bootstrap is the stricter test of the two, and
23 of the 144 top-three inputs still hold a lower bound at or above 0.6
under each of five independent seeds, spanning 17 of the 48 combinations. What the atlas
reports here is a deferral under a declared budget, not a finding that
the variance decomposition would have been uninformative.

The interaction structure on the 6 Group B cells is additionally
*a priori* established by respiratory physiology: venous admixture
capping the oxygenation gain per FiO2 increment on PaO2, and the
alveolar-ventilation identity
$\dot{V}_A = \mathrm{RR} \cdot (V_T - V_D)$ on PaCO2. Both are qualitatively recovered by
the Morris main-effect rankings reported in §3.2. These mechanisms
provide a physiological interpretation of the dominant Morris
rankings. They do not stand in for the variance decomposition, and
they carry no prediction about what its indices would have been: Sobol
was not run.

The repository preserves a restricted exploratory Sobol demonstrator in
[`scripts/s019_sobol_bolton.py`](../scripts/s019_sobol_bolton.py). It is
**not** an implementation of the preregistered bolt-on costed above, and
should not be read as one. It was written under the earlier
dominant-input reading of the trigger, and its scope follows from that
reading: 6 Group-B cells selected on the dominant input, all seven swept
inputs, N = 256 with first-order indices only — 256 × (7 + 2) = 2,304
rows per cell, 13,824 runs in total. The preregistered design is a
different one, 43 triggered cell × output combinations spread over eight
cells, at a base sample of 64 on the promoted inputs,
and the 6,144-run figure above is its cost, not the demonstrator's. The
two are not comparable: the demonstrator costs more than twice as much
and answers a different question.

What the demonstrator does share with the sweep is the locked
input-space definition (`src.sampler.salib_problem()`) and RNG seed 42,
so any indices it produced would be comparable to the Morris μ\* / σ in
`results/morris_indices.parquet` cell-for-cell. It consumes the
canonical Morris sample
(`data/runs/full_sweep/morris_sample.parquet`) and the atlas Docker
image ([S006](#s006)), and writes per-cell S₁ / Sₜ tables. The
downstream analysis pipeline is preserved in `src/analysis_morris.py`.

### 3.4 H2 — silent clamping rate (NOT supported, 0 / 1,280)

*The second hypothesis test: does Pulse silently clamp out-of-range
inputs at setup? Answer — no silent clamp was observed anywhere in the
sweep. The setup rejections Pulse does perform are explicit, with
`[ERROR]` log lines and exit code 1 (confirmed by the [S005](#s005)
deliberate clamp probes). One adjustment does occur downstream of
ingestion, and Pulse announces it too: FiO2 = 1.0 is instantiated as
0.9996 (see the subsection below).*

The preregistered hypothesis was that ≥ 5 % of the Morris sample would
hit at least one silent clamp. **Zero runs out of 1,280 fired the
`clamped` regex.** That is a null result on the preregistered detector,
bounded to the sampled acceptance envelope. The detector reads Pulse's
setup log, so on its own it establishes the absence of an explicit
rejection rather than the absence of a silent substitution; the direct
setup-time evidence for the latter is the instantiation audit reported
below, which found every submitted value preserved in what Pulse
serialises after ingestion, on all 10,160 contracts that reached it.

Two implications:
1. The swept ranges (HR 50 – 110, SBP 90 – 120, DBP
   60 – 80, RR 8 – 20, Vt 300 – 800, FiO2 0.21 – 1.0, PEEP 0 – 20) all
   sit inside the ranges Pulse accepts without intervention. No input
   submitted strictly inside these envelopes was silently substituted
   anywhere in this sweep.
2. Pulse rejects out-of-envelope inputs *loudly* — the deliberate clamp
   probes in [S005](#s005) confirmed this: SBP = 140 produces an explicit `[ERROR]`
   line and exit code 1, not a silent substitution. Rejection is loud and
   observable; users can detect it from logs alone with no special
   instrumentation.

**One explicit downstream adjustment (measured 2026-08-13).** Inside the swept
envelope Pulse does make one deterministic change to a submitted ventilator
setting, and it announces that too. When the requested inspired-oxygen fraction
plus the non-nitrogen ambient fractions exceeds one, the ventilator model logs
`[ERROR] FiO2 setting + ambient fractions other than N2 is greater than 1.0.
Setting FiO2 to max value of 0.9996.` and writes 0.9996 onto the ventilator
compartment. The cause is compositional rather than a bound on the input:
Pulse's ambient gas mixture carries carbon dioxide at 4 × 10⁻⁴, so an oxygen
fraction of exactly 1.0 leaves no room for it. In the design, 208 runs request
FiO2 = 1.0; **195 reach the ventilator action and all 195 are adjusted**, once
each, at the moment the action is applied. The remaining 13 are not exceptions
to the mechanism: they diverge during patient stabilisation, before the action
is submitted. No requested FiO2 below 1.0 is affected, and the substituted value
is identical in every affected run. The adjustment is 0.04 % in relative terms
and moves the sea-level alveolar-gas ceiling from 663.0 to 662.7 mmHg, so the
≈ 663 mmHg used elsewhere in this document stands. It is neither silent nor a
setup event — the serialised ventilator action still carries FiO2 = 1.0, and
ingestion is exact for all 10,160 contracts that reached it — so it reclassifies
no run as `clamped` and does not bear on H2, which concerns *silent* clamping.
Full audit trail: `audit/fio2_peep_setup_gates.md`; the same fact appears in the
paper (§2.1) and in Supplement §S3.3.

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
quantifies the scenario-dependent upward shift of output HR; within each
scenario, input HR remains the dominant determinant of output HR (§3.2).
**Key takeaway:** in S3 / S4 the mean output HR sits at 145 – 160 bpm
despite inputs drawn from [50, 110] — a ~70 bpm overshoot above the input-range midpoint
consistent with Pulse's documented baroreceptor and chemoreceptor reflex
behaviour, though the atlas did not record or isolate the contribution of
those reflexes. The response occurs in runs that meet the atlas's clean-run
criteria, which argues against the classifier's predefined failure modes as
its explanation without excluding unmeasured numerical effects.

In S1 (healthy), mean output HR is ~74 bpm, and output HR
still follows the requested baseline: input HR is the rank-1 input for
output HR in every cell (§3.2). By S3 / S4, mean output HR is in the
145 – 160 bpm range *despite* the input being drawn from [50, 110] — a
~70 bpm overshoot above the input-range midpoint. This is
consistent with the engine's documented baroreceptor / chemoreceptor
reflex behaviour under hypoxemia, though the atlas did not record or
isolate the contribution of those reflexes. ARDS severity therefore
shifts the output-HR distribution strongly upward, while input HR
remains a dominant within-scenario determinant of output HR.

Operational implication: **Morris elementary effects on input HR in
ARDS scenarios describe how output HR responds to the input setting
within a scenario whose compensatory state is already shifted, not the
steady-state effect of resting HR.** The H1
support for HR-dominated cardiovascular outputs (HR, MAP) is robust;
the *interpretation* is that input HR remains a dominant within-scenario
determinant of output HR, not that "the input HR is the steady-state
HR." Users running Pulse for ARDS device-validation should treat
output HR as the engine's scenario-dependent steady-state response,
not a setpoint.

### 3.5 H3 — a divergence regime exists outside the documented ARDS zone (supported); its sex-stratification is regime-dependent

*The third hypothesis test: does at least one solver-divergence zone
exist outside the documented 0.91 – 0.945 ARDS zone? Answer — yes.
Divergence occurs at impairment fractions 0.00, 0.26, 0.60 and 0.95,
none of them inside that band, so H3 is supported outright. A second
question, which H3 does not ask, is whether those divergences are
sex-stratified: partially. In the [S006](#s006) input-extreme regime, all 20 / 20
divergences are male and zero female, with the asymmetry
shown ([S018](#s018)) to depend on Pulse's
`BloodVolumeBaseline` gap on the two surrogates — male default
4,802.63 mL vs female default 3,996.09 mL, a ~17 % difference — and
with a separate F-S018-A side-finding that Pulse enforces a
per-surrogate BV floor (4,082.24 mL on this male body) which bounds
how far the gap can be closed by a one-way transplant. In the §3.5.1
continuous-severity regime at midrange inputs, divergence is
approximately sex-balanced in aggregate inside the [0.879, 0.946] band,
though the sex asymmetry reverses between its two severity bands — so
the original sex effect varies with *what is varying*, not sex per se.*

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
* The remaining 4 are unique to S4_M, at `run_idx` 24 / 82 /
  137 / 138. They form a mixed cluster: one HR at 110 bpm, three at
  90 bpm; two Vt at 300 mL, one at 633.3 mL, one at 800 mL. This is a
  *partial second regime* — one the locked Morris sample explores
  only at the most severe ARDS impairment.

The signature reads cleanly: **low cardiovascular output (low HR +
low SBP) combined with high respiratory rate (high RR) on the male
reference surrogate** drives Pulse to a numerical edge case; the
high-oxygen boundary (FiO2 = 1.0) is requested in 13 of the 20 cases (not all 20 — the other 7 sit near FiO2 ≈ 0.74, so it is enriched but not necessary), and it is never applied: every divergence occurs during patient stabilisation, before the ventilator action is submitted. The compound input is *clinically plausible* — a hypotensive,
tachypneic patient, recognizable as a septic /
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

**Methodological disambiguation: absolute vs weight-normalized BV.**
The ~17 % absolute-mL sex gap is almost entirely driven by the
body-mass difference between the two reference surrogates (67.3 vs
56.2 kg, also a ~17 % difference). When normalized by body weight,
the per-kg blood-volume indices are essentially identical:
4,802.63 / 67.3 = **71.4 mL/kg** for the male body and
3,996.09 / 56.2 = **71.1 mL/kg** for the female (a ~0.4 % per-kg
gap). The allometric formula `BV = 65.6 × weight_kg^1.02` scales
blood volume nearly linearly with weight (the 1.02 exponent is close
to 1.0), so weight-normalized BV is approximately constant across
body masses by construction. The atlas's sex-stratified divergence
finding is therefore correctly stated in absolute-mL terms because
Pulse's internal `BloodVolumeBaseline` floor (4,082.24 mL on this
male body = 60.7 mL/kg) is parameterized on absolute volumes, not on
per-kg physiology; the BV-dependence characterisation in this section
is about how Pulse's solver responds to absolute-BV values near its
setup-time floor on the male reference body, not a claim about
per-kg blood-volume physiology in real patients. Pooling male and
female Pulse-generated synthetic cohorts in machine-learning
pipelines without flag-stratified filtering still introduces a
spurious sex covariate at the male surrogate's divergence boundary,
but downstream users adapting the result to clinical inference
should not extrapolate to a per-kg sex-physiology claim that the
data does not support.

Pulse's blood-volume baseline is not itself sex-conditional: it is
computed from body mass alone. Several other patient-setup parameters
are: ideal-body-weight (Devine formula coefficient 50.0 vs 45.5),
fat-fraction standard (0.21 vs 0.28), height bounds
(151 – 175.5 cm vs 163 – 190 cm), and the Harris–Benedict basal
metabolic rate, which the engine's energy model uses both to
initialise total metabolic rate and as the set point toward which it
is held under resting, normothermic conditions, and which therefore
drives tissue oxygen consumption and carbon-dioxide production
(`EnergyModel.cpp`, `TissueModel.cpp`). None of those is the
divergence mechanism. The BV gap remains the most plausible candidate
for the divergence asymmetry — it enters the cardiovascular circuit's
stabilisation directly, and shifts the operating-point neighborhood
between the two bodies — but it does so as a body-mass difference,
not as a sex difference.

**Causal lever identified ([S018](#s018), 2026-05-13).** *In one sentence:
forcing the male surrogate's BV down towards the female value
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
| 4,400  | 8.4 %  | **0 / 20** | 1 / 20 | 8 / 20 | 12 / 20 |
| 4,082.24 (Pulse-stated floor on this surrogate) | 15.0 % | **0 / 20** | 1 / 20 | 8 / 20 | 12 / 20 |

*BV-override dose-response table — at a glance.*
**What:** outcomes for the 20 originally-diverged male inputs when
re-executed with an explicit `BloodVolumeBaseline` override at three
levels (default 4,802.63 mL → 4,400 mL → 4,082.24 mL, the
Pulse-stated floor on this surrogate).
**How to read it:** each row is one BV override level; columns count
the four detector outcomes plus `Clean` across the 20 reruns.
**Key takeaway:** divergence is eliminated by BV
reduction — 20 / 20 → 0 / 20 at both brackets — establishing that lowering
Pulse's blood-volume baseline is sufficient to eliminate the all-male
divergence cluster.

The divergence cluster is eliminated by any BV reduction tested.
Lowering the baseline is therefore sufficient to eliminate it; the
experiment does not identify the numerical pathway by which the solver
fails at the default value, nor establish that the baseline is necessary
for the failure. Note also that removing the divergence does not make the
runs clean: 12 of 20 are clean at both brackets and 8 retain a flag, as
the dose-response table above records.

All 20 inputs are already cleared at the 4,400 mL bracket (8.4 %
reduction); none requires deeper reduction. (An earlier internal
classification recorded two S4_M / FiO2 = 1.0 cases as still divergent at
4,400 mL, but that was a classification-time race on the two slowest runs
— both completed normally and re-classify as clean; see the S018 log,
F-S018-B.)

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
diverge in this regime — the first quantitative sex-stratified
reliability finding for Pulse 4.3.1.

The same 160 Morris input points were submitted to both M and F cells.
Patient bodies: M = 67.3 kg / 180 cm; F = 56.2 kg / 163 cm. Same
physics engine, same condition string, same ventilator settings. The
only difference is patient mass / height / sex flag.

Yet the divergence rate is **2.5 % in S1_M, S2_M, and S3_M** (4 / 160
each), **5.0 % in S4_M** (8 / 160), and **0 % in every female cell**.
The overall male rate is 20 / 640 = 3.1 %; the female rate is 0 / 640.

This is the first quantitative sex-stratified reliability finding for
Pulse 4.3.1, and is consequential for any device-validation pipeline
that uses Pulse as a virtual patient. **All 20 divergences occur on
the male surrogate; the female surrogate, run on the *identical*
input grid, never diverges within the locked envelope.** The
diverged-run input combinations are catalogued in
`results/diverged_grid.parquet` (a 2-D heatmap of divergence rate
per input-pair × cell).

H3 is therefore **supported**, and with more than it asked for:
a divergence regime exists outside the documented 0.91 – 0.945 ARDS
zone *and* the regime is sex-conditioned. The second half is a finding
in addition to the hypothesis, not a qualification of it.

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
| (0.5, 0.85]      | 0 / 19     | 0 / 19     |
| (0.85, 0.91]     | **14 / 19**| 5 / 19     |
| (0.91, 0.945]    | 5 / 9      | **8 / 9**  |
| (0.945, 0.95]    | 0 / 2      | **1 / 2**  |
| (0.95, 1.0]      | 0 / 20     | 0 / 20     |

*Continuous-severity divergence table — at a glance.*
**What:** divergence counts per ARDS-severity bin in a 200-run
continuous-severity micro-sweep at midrange inputs (HR 80, SBP 105,
DBP 70, RR 14, Vt 550, FiO2 0.6, PEEP 10).
**How to read it:** each row is one severity bin; F-diverged and
M-diverged columns show divergences per sex (denominators differ
because runs distribute non-uniformly across severities). Each run is
binned on the impairment fraction it was simulated at, read from its
configuration.
**Key takeaway:** divergences concentrate in `[0.879, 0.946]`, the
smallest 3-decimal interval containing every diverged run —
wider than the previously reported `[0.91, 0.945]` zone — and are
approximately sex-balanced in aggregate at midrange inputs, though the
sex asymmetry reverses between the two bands above (female-dominated
in (0.85, 0.91], male-dominated in (0.91, 0.945]). The original
[S006](#s006) "all-male divergences" claim is therefore *regime-specific*
(Morris-extreme inputs), not a global sex effect on solver reliability.

Two refinements of the literature picture:

1. **The instability band is wider than previously reported.** The
   `Pulse_translation_new` E10 boundary probe, confirmed by E6, reported an
   instability zone at `[0.91, 0.945]`. Our continuous sweep at midrange inputs places
   the band at `[0.879, 0.946]` — the lower edge moves down by 0.031
   and the upper edge up by 0.001, extending the band on the low side
   by about 90 % of the original
   width. The discrepancy is consistent with input dependence: E6
   used ventilator settings tailored to ARDS calibration; the atlas's
   midrange settings reach instability earlier.

2. **The [S006](#s006) sex-stratification is regime-dependent.** In the
   continuous-severity sweep (midrange inputs), the divergences are
   approximately balanced (F = 19, M = 14), with F diverging at
   *lower* severities (0.879 onwards) and M continuing through
   `[0.91, 0.946]`. So the original [S006](#s006) claim "all 20 male
   divergences" is a property of the *input-extreme + 4-scenario*
   combination, not a global sex effect on solver reliability.

The atlas therefore distinguishes **two separate divergence regimes**:

* **Input-driven regime** ([S006](#s006)): male reference surrogate at low HR
  + low SBP + high RR + FiO2 = 1.0. 20 divergence events on the male
  body, versus zero across the 640 runs on the female body.
  Mechanism candidate: ~17 % blood-volume difference (§3.5, computed
  as (4 802.63 − 3 996.09) / 4 802.63 against the male default).
* **Severity-driven regime** ([S009](#s009)): both sexes, midrange inputs,
  severity in the band `[0.879, 0.946]`. F slightly higher overall;
  F earlier in the band, M later. Interpretation: the sex asymmetry shifts
  across the high-impairment band, consistent with a change in solver
  stability; the atlas did not record solver-conditioning metrics or isolate
  a compliance-edge mechanism.

Together these regimes give a more honest picture of what surrounds
H3: the divergence zone H3 predicted exists, and beyond that, the sex
effect varies by *what is varying* (Morris-extreme inputs vs ARDS
severity) rather than by sex per se.

### 3.6 H4 — sex-specific reliability (supported by divergence; the distributional difference is gas-exchange only)

*The fourth hypothesis test: do the male and female bodies differ in
clamping, divergence, or Morris μ\* ranking? Answer — yes, outright:
divergence is 20 / 0. How far does the difference extend into the
steady-state distributions? Partially. Under Benjamini–Hochberg FDR
control (q = 0.05), 5 of 24 cell × output Wasserstein distances
survive — *all five on gas-exchange channels* (PaCO2 × 3, SpO2 × 1,
PaO2 × 1). Cardiovascular and Vt distances fall within the permutation-based
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

**Wasserstein distance with permutation null.** The observed value is
the M-vs-F distance on clean runs. The reference null is built by
repeatedly splitting the *combined* M+F clean runs randomly into
two groups of the original sizes (n_null = 2,000 splits).

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
S2 & \textbf{PaCO2} & \textbf{5.12} & 1.07 & 2.13 & \textbf{$<$ 0.001} & * \\
\midrule
S3 & HR    & 4.77  & 3.86  & 8.61  & 0.333 &   \\
S3 & MAP   & 0.94  & 0.98  & 2.02  & 0.538 &   \\
S3 & Vt    & 36.3  & 20.8  & 45.9  & 0.129 &   \\
S3 & SpO2  & 0.014 & 0.009 & 0.017 & 0.119 &   \\
S3 & PaO2  & 8.82  & 6.57  & 12.8  & 0.245 &   \\
S3 & \textbf{PaCO2} & \textbf{2.94} & 0.75 & 1.33 & \textbf{$<$ 0.001} & * \\
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
distances survive BH-FDR control at q = 0.05 against a permutation-based
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

The surviving cross-body differences concentrate in the gas-exchange
outputs, but they cannot be read as isolated effects of the sex flag.
The two reference bodies differ jointly in sex, in morphology, and in
relative ventilation dose: because the sweep varies tidal volume in
absolute millilitres over the same 300–800 mL range on both bodies,
an identical absolute setting delivers 19.8 % more tidal volume per
kilogram of actual body weight, and 36.1 % more per kilogram of the
ideal body weight Pulse itself computes at setup (sex-specific Devine
relation, `SetupPatient.cpp`), to the female body. That difference
acts directly on alveolar ventilation.

PaCO2 is the strongest signal — significant in 3 of 4 scenarios, with
very small p_emp values in S2 and S3 — and that concentration is
exactly what the ventilation-dose mismatch predicts, since alveolar
ventilation is PaCO2's dominant determinant. It therefore cannot be
attributed to sex-specific physiology alone. Separating sex-dependent
physiology from morphology and from ventilatory dose would require
matched input configurations *together with* matched relative
ventilation doses; matching configurations alone does not suffice.

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
observed M-vs-F distance is compared against a permutation-based
sub-sampling null (n = 2,000 random splits of the combined M+F clean
runs); cells flagged with `*` exceed the 95th-percentile of the null.
**Key takeaway:** 5 of 24 cells survive BH-FDR control at q = 0.05 —
*all five on gas-exchange channels* (PaCO2 × 3, SpO2 × 1, PaO2 × 1).
Cardiovascular and Vt distances fall within the permutation-null baseline
at this sample size.

![Figure 4. H4 — 1-Wasserstein distance, M vs F clean-run outputs, per scenario × output, in each output's native units. Bars marked `*` exceed the permutation null (n = 2,000 splits) at the 95th percentile; under BH-FDR control at q = 0.05, **5 of 24** survive — all 5 on gas-exchange channels (PaCO2 × 3, SpO2 × 1, PaO2 × 1). S2 SpO2 (p_emp = 0.022) is the BH-demoted row. Source: `results/wasserstein_male_vs_female.csv` + `results/bh_fdr_survivors.csv` (S006 / S008).](../figures/fig04_h4_wasserstein.png)

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
flagged — predominantly by SpO2 ceiling pinning at high FiO2. This
non-computability is itself a finding (§4.5 limitations).

The bootstrap CI on ρ is wide for output Vt (S2 lower bound −0.06),
meaning the input-importance ranking for Vt is not clearly preserved
across sex. For the other outputs, the lower CI bound sits at ≥ 0.34
— qualitative support for "rankings preserved across sex", though
not high-precision support.

A complementary engine-level verification is relevant here. Pre-Atlas
experiments (`Pulse_translation_new` female-surrogate engine tests
and male/female side-by-side verification) established that the
female surrogate produces physiologically plausible output across all
four scenarios, independent of this sweep. The sex effects we observe
above therefore reflect the engine's behaviour on two reference bodies
that differ in sex, mass and height at once, not a miscalibration of
the female patient model.

*Figure 5 (`fig05_h4_spearman_mu_star`) — at a glance.*
**What:** Spearman rank correlation ρ between male and female Morris
μ\* vectors, per scenario × output, with paired-input bootstrap 95 %
CI (n = 2,000 input-resamples).
**How to read it:** ρ = 1 means identical input ranking across sexes;
ρ = 0 no monotonic relationship; ρ = −1 inverted. Computed only for
S2 and S3 — S1 and S4_F have no clean FiO2 elementary-effect pairs
(every FiO2 OAT step has at least one endpoint flagged).
**Key takeaway:** point estimates 0.75 – 1.00 in S2 / S3 — input-importance
rankings are qualitatively preserved across sexes. Vt is the
exception (S2 CI [−0.06, 1.00]), reflecting that the input ranking
driving Vt is not clearly preserved across sex.

![Figure 5. H4 — Spearman ρ on Morris μ\* rankings, M vs F, per scenario × output, with paired-input bootstrap 95 % CI (n = 2,000 input-resamples). Computed only for S2 and S3; S1 and S4_F have no clean FiO2 elementary-effect pairs (§4.5 limitations). Source: `results/spearman_mu_star.csv` (S006 / S008).](../figures/fig05_h4_spearman_mu_star.png)

**Combined H4 picture:**

* H4 is **supported**: its preregistered criterion is a male–female
  difference in clamping, divergence, or Morris μ\* ranking, and the
  20 / 0 divergence asymmetry satisfies it on its own.
* Beyond that criterion, the **distributional** difference is
  **partial**, with the strong signal concentrated on gas-exchange
  outputs.
* **Sex effect is real on PaCO2 (S1, S2, S3), SpO2 (S4), and PaO2 (S4)** —
  these survive the permutation null under BH-FDR control at q = 0.05.
* **Sex effect on HR, MAP, Vt is not distinguishable from
  the permutation null** at our sample size. Either it does not
  exist, or it is below the detection floor of 42 – 144 clean runs
  per cell.
* **Input-importance rankings are similar by sex** (Spearman ρ
  point estimates 0.75 – 1.00 in S2 / S3) but the CIs are wide —
  the ranking-similarity claim is qualitative, not high-precision.

### 3.7 Traffic-light curation map (Figure 6)

*The user-facing summary of the entire atlas: per cell × output, one
of {green, yellow, red}, anchored to preregistered baseline-percentage
thresholds (10 % / 30 % deviation; 30 % hard-failure rate). The final
distribution is 7 green, 29 yellow, 12 red out of 48 cells — and
S4_M is red on every output.*

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
**Key takeaway:** all seven green classifications fall in the
(S2_F, S3_F) cluster, the only two cells carrying no diverged and no
implausible run; S4_M is the only cell red on every output; and
HR + PaO2 turn red across both sexes from S3 onwards. Red marks a cell
for review, not a defect in the engine: six of the twelve are red on
the deviation criterion alone, in scenarios where a departure from the
healthy-male baseline is what the pathophysiology predicts.

Distribution: **7 green, 29 yellow, 12 red** out of 48 cells.

**Post hoc deviation from the preregistered traffic-light rule.** The colour
rule above is the implemented rule, not the rule written verbatim in
`preregistration.md` §Analysis plan item 7. The preregistration stated that a
cell would be red when its deviation exceeded 30 % or when "any flag" was
raised. The implementation instead uses only the two hard flags (`diverged`
and `implausible`): any positive combined rate yields yellow, whereas red
requires a combined rate above 30 %; the 10 % and 30 % deviation thresholds are
unchanged. Reconstructed from the eight run-level artefacts, the implemented
rule gives 7 green, 29 yellow, 12 red, whereas the literal hard-flag reading
gives **7 green, 3 yellow, 38 red**. The same seven green and twelve red
combinations are retained, with 26 combinations moving from yellow to red.
Reading "any flag" as all four flags gives 0 green, 0 yellow, 48 red and is
reported only to document the ambiguity. The phrase "cell baseline" is also
ambiguous; the implemented map uses the healthy-male S1_M reference. The
repository establishes that the implemented rule was committed after
preregistration, in the same commit as the tracked sweep artefacts, but does
not establish whether it was defined before or after inspection of the sweep
outputs. The formal declaration appears in Methods §4.5 of the npj manuscript,
the sensitivity analysis in Supplement §S3.11, and the full chronology and
rationale in `audit/preregistration_traffic_light_deviation.md`
([`scripts/audit_traffic_light_rule.py`](../scripts/audit_traffic_light_rule.py)
rebuilds all three readings).

* Green cells cluster in **S2_F + S3_F** — moderate ARDS in the
  female surrogate is, paradoxically, Pulse's most steady operational
  region within the atlas envelope.
* Red cells cluster in **S3 + S4 on HR + PaO2** — moderate-to-severe
  hypoxemia drives both heart-rate compensation and arterial-oxygen
  values far from the S1_M baseline.
* **S4_M is red on every output.** It is the only cell whose hard-failure
  rate exceeds 30 % (54 / 160 = 33.75 %), and it corresponds to severe ARDS on
  the larger male body habitus. Users running Pulse at this configuration
  should treat the engine output as a starting point, not a faithful
  steady-state physiology.

*Figure 6 (`fig06_reliability_traffic_light`) — at a glance.*
**What:** per cell × output classification into {green, yellow, red}.
The user-facing summary of the entire atlas and the figure most
likely to be consulted by Pulse practitioners.
**How to read it:** green = no diverged or implausible flags in the cell *and*
clean-run mean within 10 % of the S1_M baseline; yellow = any
diverged or implausible flag *or* mean 10 – 30 % off baseline; red = mean > 30 % off
baseline *or* diverged + implausible rate > 30 %.
**Key takeaway:** 7 green, 29 yellow, 12 red out of 48 cells. Green
cluster: S2_F + S3_F. Red cluster: HR and PaO2 in S3 / S4.
S4_M is red on every output — the worst single cell in the atlas.

![Figure 6. Reliability traffic light — per cell × output, one of {green, yellow, red}. Green = no diverged or implausible flags in the cell AND clean-run mean within 10 % of the S1_M baseline. Yellow = any diverged or implausible flag OR mean 10 – 30 % off baseline. Red = mean > 30 % off baseline OR diverged + implausible rate > 30 %. Distribution: 7 green / 29 yellow / 12 red across 48 cells — i.e. 7/48 (15 %), 29/48 (60 %), 12/48 (25 %) respectively, shares of the map distinct from the 10 %/30 % baseline-deviation thresholds that define the colours; the user-facing summary of the entire atlas. Source: `results/reliability_classification.csv` (S006).](../figures/fig06_reliability_traffic_light.png)

### 3.7.1 What the colour does not say, and what each screen costs

*Mirror of the npj reframing. The map is a conservative curation and
review-priority instrument, not a reliability verdict, and neither of
the two screens available to a downstream user is distribution-neutral.*

**Two levels, not one.** The four-flag classifier assigns labels to
**runs**; the traffic light is what you get by **aggregating** those
runs per cell and combining the result with a deviation term. They are
not interchangeable. Only two of the four flags enter the cell-level
rule — `diverged` and `implausible`; `clamped` and `not_steady_state`
never do — so the map is not a "four-flag map", and the run-level
classifier is not a per-cell contract.

**Why the colour alone is not a diagnosis.** Each colour is produced by
two independent criteria, on class-relative and deliberately asymmetric
thresholds: for deviation, yellow above 10 % and red above 30 %; for the
hard-flag rate, yellow at any positive value and red above 30 %.
Re-applying that rule to the 48 cells gives **7 neither** (which
coincides with the green set by construction), **23 hard flags only**,
**9 deviation only** and **9 both**. Among the 12 red cells the split is
**6 deviation-only, 4 flag-only, 2 both** — so half the red cells are red
because the clean-run mean sits far from a *healthy male*, in scenarios
where the compensatory tachycardia and the ARDS hypoxemia are exactly
what Pulse should produce. A red cell is a request for justification,
not a verdict that the physiology is wrong.

**The two screens, and what each removes.** Under the strict four-flag
definition, 663 / 1,280 simulations (51.8 %) are clean, with per-cell
retention from 42/160 in S1_F to 144/160 in S3_M — a 3.43-fold spread.
Treating `not_steady_state` as a review-and-remediation label rather
than an automatic exclusion instead leaves 1,134 / 1,280 (88.6 %)
hard-failure-free, from 106/160 in S4_M to 160/160 in S2_F and S3_F, a
1.51-fold spread. Retention is given as counts rather than percentages
because with *n* = 160 every per-cell percentage is a multiple of 0.625
and nine of the sixteen values fall on an exact rounding tie at one or two decimals.

| cell | four-flag clean | hard-failure-free |
|---|---:|---:|
| S1_M | 49/160 | 145/160 |
| S1_F | 42/160 | 137/160 |
| S2_M | 87/160 | 156/160 |
| S2_F | 92/160 | 160/160 |
| S3_M | 144/160 | 156/160 |
| S3_F | 122/160 | 160/160 |
| S4_M | 67/160 | 106/160 |
| S4_F | 60/160 | 114/160 |

**The two screens deplete opposite ends of the severity axis.** The
four-flag screen is harshest on the *healthy* cells (S1_F, S1_M); the
hard-failure-free screen is harshest on the *severe-ARDS* cells (S4_M,
S4_F). Choosing a screening rule therefore chooses which clinical
regime a downstream cohort under-represents. Neither subset is
distribution-neutral, and neither is an automatic filter: downstream
studies should report per-cell retention and cohort composition before
and after screening. The 1,134-run subset must not be called clean — it
still contains non-stationary trajectories.

**The partition closes exactly.** The 471 runs gained by moving from the
strict-clean subset to the hard-failure-free subset are precisely those
carrying `not_steady_state` as their sole flag; with 20 `diverged` and
126 `implausible` runs they account for all 617 non-clean runs
(471 + 20 + 126 = 617). That identity only closes if `diverged` and
`implausible` are disjoint in this sweep, which is measured rather than
assumed. `clamped` is a provided category that is empty here (0 / 1,280).

**Recorded reasons undercount co-occurring mechanisms.** The detector
stores, for each failing channel, only the *first* trigger its ordered
checks reach (flatline, then CV, then drift). Re-applying the registered
thresholds to the stored per-channel statistics instead gives an
exhaustive, multi-label attribution — and that reconstruction reproduces
the stored `not_steady_state` flag on 1,280 of 1,280 runs, which is what
licenses using it. The gap is large on delivered Vt: **133** channels
exceed the drift threshold but only **3** appear in the recorded reason,
because a CV trigger was reached first in 130 of them. Exhaustive counts
are non-mutually-exclusive channel-level occurrences (918 in total) and
must not be summed as independent runs.

**Where this is published.** The npj paper carries the driver totals as
a compact strip under Figure 2; the full per-cell driver matrix, the
per-cell hard-failure rates, the exhaustive trigger attribution and the
*signed* deviation from the S1_M baseline are Supplement Figure S1
(§S3.12). The signed panel is descriptive only: a directionally expected
change under ARDS does not validate its magnitude, and nothing in this
atlas is an external physiological validation.

### 3.8 Two structural findings carried from pilot to full sweep

*Two findings that surfaced in the 22-run pilot and held through the
1,280-run sweep. **F-003**: under the preregistered 120 s window,
Pulse PaO2 exceeds the locked 600 mmHg classifier upper bound at
FiO2 = 1.0 on healthy adults — a *transient hyperoxia regime + conservative
preregistered classifier bound*, **not** an oxygenation overshoot, as
shown by a 300 s rerun ([S021](#s021)) on the same
input combinations. **F-004**: VC-AC tidal-volume oscillation in
20.6 % of runs, causally linked in [S014](#s014) to the
inspiration trigger, consistent with patient-ventilator dyssynchrony, and
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
  the companion `Pulse_translation_new` FiO2 = 1.0 crash probe reports
  a steeper ~7.8 mmHg / 0.01
  slope on a focused single-input probe at FiO2 0.95 – 1.0; the two
  figures reflect different regimes — multi-input averaged across
  [0.21, 0.47] vs single-input near the FiO2 = 1.0 boundary).
  Linear extrapolation from FiO2 = 0.5 (PaO2 ≈ 228 mmHg) predicts
  PaO2 ≈ 480 mmHg at FiO2 = 1.0; the locked 120 s S1 means at
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
  A controlled experiment reran 60 matched-input cases
  at FiO2 = 1.0, each re-executed from time zero with the recorded
  simulation duration raised from the locked 120 s to 300 s
  (sample interval 5 s; 22 paired Morris indices × S1 (M + F) =
  44 S1 runs; 4 paired indices × {S3, S4} × {M, F} = 16 ARDS runs).
  The S021 notebook entry records all thresholds as fixed before any
  S021 Pulse run was observed. The decision rule on the S1 subset
  required *frac converged ≥ 75 %* (plateau drift over [240, 300] s
  below the locked 15 mmHg / 60 s threshold) **and** *median plateau
  ∈ [580, 680] mmHg* (alveolar-gas-equation prediction ± 75 mmHg).
  Both were met by very large margins:

    * **S1 (n = 44):** plateau median 643.2 mmHg (decision band
      [580, 680] mmHg); 40 / 44 runs (90.9 %) converged.
    * Plateau median of 643 mmHg sits ~20 mmHg below the simple
      alveolar-gas-equation prediction: alveolar
      $P_AO_2 = \mathrm{FiO}_2 \cdot (P_{\mathrm{atm}} - P_{\mathrm{H_2O}}) - P_aCO_2 / \mathrm{RQ}$
      $= 1.0 \cdot (760 - 47) - 40 / 0.8 \approx 663$ mmHg; the measured
      arterial $P_aO_2$ of 643 mmHg therefore implies an A-a difference
      of ~20 mmHg. Pulse *under-shoots*
      the alveolar prediction and does not overshoot. The
      decision is `HYPOTHESIS_II_TRANSIENT_REGIME_SUPPORTED`.

  **Severity-graded oxygenation depression, consistent with the
  documented physiological mapping ([S021](#s021) auxiliary,
  descriptive — not part of the (i)-vs-(ii) decision).**
  At FiO2 = 1.0, the [240, 300] s median PaO2 plateau decreases
  monotonically with ARDS severity (S1 → S3 → S4):

  | Scenario | n | Plateau median (mmHg) | Plateau IQR (mmHg) | Converged |
  |----------|---|------------------------|---------------------|-----------|
  | S1       | 44 |  643.2 | [592, 668] | 40 / 44 (91 %) |
  | S3       |  8 |  143.6 | [ 93, 218] |  8 /  8 (100 %) |
  | S4       |  8 |   72.6 | [ 71,  76] |  8 /  8 (100 %) |

  At FiO2 = 1.0, PaO2 spans from approximately 643 mmHg in the healthy
  S1 configuration to approximately 73 mmHg in severe ARDS (S4), an
  order-of-magnitude decrease across severity. The S3 and S4 summaries
  use the four paired Morris input vectors replayed on both reference
  bodies, whereas the S1 summary uses the full 44-run healthy hyperoxia
  set. Across the tested S1, S3 and S4 configurations this decrease is
  consistent with worsening gas exchange as the
  alveolar diffusion surface collapses and intrapulmonary-shunt
  behaviour changes under the severity scalar, increasingly separating
  arterial PaO2 from the calculated alveolar oxygen tension at
  unchanged FiO2 = 1.0.

  **Solver-instability tail at extended windows ([S021](#s021),
  additional sub-finding).** A separate phenomenon emerges *only*
  with the 300 s window: 6 / 44 S1 runs (14 %) develop unphysical
  PaO2 plateaus > 700 mmHg (4 stabilising near 1,400 mmHg, above
  the sea-level barometric pressure of 760 mmHg). All six sit at the
  single tidal-volume level **Vt = 633.3 mL** at FiO2 = 1.0 — 6 of the
  20 S1 reruns at that level, none of the 24 at the other three, and
  0 of 8 at the highest level Vt = 800 mL.

  **Minute ventilation does not separate them.** Five of the six carry
  RR = 20 (V̇E ≈ 12.7 L/min, ~ 2× the physiological norm of 6 – 8 L/min),
  but three further runs at that same V̇E do not run away; the sixth
  carries RR = 16 at PEEP = 0 (V̇E ≈ 10.1 L/min). No input-side
  ventilation threshold in this cohort separates affected from
  unaffected runs — the previously published “avoid > ~ 12 L/min”
  guidance both missed a case and over-fired, and has been withdrawn.

  **What does separate them is the reference body.** The 10 runs at
  Vt = 633.3 mL with RR ≥ 16 form five male/female pairs, verified
  input-identical on all seven Morris inputs. The female body ran away
  in **5 of 5**, the male in **1 of 5**, and the single male case
  plateaus at 770 mmHg against 1,126 – 1,408 mmHg across the five
  female cases. This is the opposite direction to the all-male
  input-extreme divergence cluster of §3.5, and a third instance of the
  regime-dependence that section establishes. It is consistent with the
  systematically higher PaO2 the female body reaches at identical
  inputs (mean 686 vs 663 mmHg in the locked 120 s window across the
  four RR = 20 pairs) and with the sex effect on S1 PaO2 measured by
  the controlled 2×2 sex×mass design ([S011](#s011)), which held body
  mass and height fixed across sexes. That design has two arms and they
  carry different weight: **+13.7 mmHg** in the 56.2 kg comparison,
  where both phenotypes lie inside Pulse's stated height and BMI
  ranges, against **+21.3 mmHg** in the 67.3 kg comparison, whose
  synthetic 180 cm female exceeds Pulse's nominal female height ceiling
  of 175.5 cm and carries the engine's own model-validity warning. The
  smaller, fully in-envelope figure is the one to weigh.
  **No mechanism is claimed**, and three limits bound the design even
  on its clean arm: the two bodies are not percentile-matched (163 cm is
  simultaneously Pulse's female 50th-percentile standard and its male
  3rd-percentile floor, so equal height cannot mean equal percentile);
  it was run at a single midrange operating point at FiO2 = 0.6; and
  Pulse's sex flag switches parameters across several subsystems at
  once. This cohort therefore cannot separate sex from the 11.1 kg
  body-mass difference in this regime.
  Inspection of the per-run trajectories shows a stable
  ~ 690 mmHg PaO2 plateau through ~ 195 s, then an abrupt numerical
  runaway between 195 s and 220 s, plateauing at ~ 1,400 mmHg by
  240 s (concurrent unphysical PaCO2 collapse to < 17 mmHg). The
  locked 120 s atlas window stops the simulation *before* this
  runaway and therefore protects the headline atlas classification
  from it. This is not a transient regime; it is a separate
  solver-instability mode that an *extended-window* user of Pulse
  should screen for run by run on the PaO2 trajectory, since no
  input-side ventilation setting predicts it.

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
  **32 of the 34 implausibly-flagged-by-PaO2 runs no longer
  exceed the wider PaO2 bound** (31 at FiO2 ≥ 0.95,
  21 in S1_F + 11 in S1_M); the remaining two stay implausible
  under either classifier and correspond to the
  solver-instability-tail input signature above.

  **Practitioner takeaway.** Under the locked 120 s atlas window at
  FiO2 ≥ 0.95, treat PaO2 as a transient — the steady-state
  detector is correctly flagging an unfinished trajectory. Under an
  extended window of ≥ 300 s total simulated time, use a plateau window in the final 60 s of
  the simulation; expect a plateau near 640 mmHg in healthy lungs
  and graded oxygenation depression in ARDS (~ 144 mmHg at
  60 % severity, ~ 73 mmHg at 95 % severity). On healthy lungs at
  FiO2 = 1.0, screen each run's PaO2 trajectory individually:
  extended-window simulations can enter a separate
  solver-instability regime there, and no input-side ventilation
  setting predicts which runs enter it (§3.8). Full S021
  protocol and per-run paired data:
  [`experiments_log/santino/S021_hyperoxia_convergence.md`](../experiments_log/santino/S021_hyperoxia_convergence.md);
  raw artefacts in `data/runs/s021_hyperoxia_convergence/`.
* **F-004 — Tidal-volume oscillation in VC-AC at extreme inputs,
  consistent with patient-ventilator dyssynchrony.**
  Patient-ventilator dyssynchrony in volume-control ventilation at low
  tidal volume is a well-documented bedside phenomenon
  [@figueroacasas2016], so the relevant question for the atlas is how
  often the engine's default trigger configuration produces a
  tidal-volume oscillation consistent with it under operational
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
  window (e.g. 0.0900 ± 5×10⁻⁶ L/cmH2O for run S1_F_0008),
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

  **Causal confirmation ([S014](#s014)).** A controlled experiment
  on the top-64 Vt-CV runs reran each with identical inputs but with an
  explicit `InspirationPatientTriggerPressure = −2 cmH2O`. Setting any
  explicit trigger threshold disables the respiratory-model branch (the
  fall-through guard becomes false). **Median (Vt_cv_original −
  Vt_cv_lockout) = +0.326** (decision threshold ≥ 0.04, exceeded
  8×); **proportion of locked runs with Vt_cv < 0.05 = 78.1 %**
  (decision threshold ≥ 75 %). Median Vt_cv collapses from 0.351
  to 0.016 (96 % reduction); worst-case from 1.826 to 0.018. Both
  thresholds were met, confirming that the trigger coupling
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
  in **0 %** (median 0.05 mmHg); PaCO2 in **3.6 %** (7 / 195, median
  0.58 mmHg — computed 2026-07-24; the original S012 pass did not
  tabulate PaCO2 for this arm). Vt exceeds 50 mL in **8.7 %** (median
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

In these audited populations, window-length sensitivity is concentrated
in PaO2 and delivered Vt, and threshold exceedances are uncommon for HR,
MAP and PaCO2; the audit does not cover the rest of the sweep. The
sensitive channels sit at the FiO2 ≥ 0.95 and high-oscillation
extremes, which is exactly what F-003 and F-004 already disclose. The F-003 / F-004
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
et al. 2026; Table 2), and consolidates the structural limitations of
the work in §4.5.*

### 4.1 What the atlas tells Pulse users

*A practitioner-oriented summary of which cells and which outputs are
green, yellow, or red under the combined flag-and-baseline-deviation
rule — and the specific reasons:
F-003 transient hyperoxia regime, F-004 tidal-volume oscillation,
severe-ARDS solver behaviour, and the sex-stratified divergence
cluster in the input-extreme regime.*

The traffic-light curation map (Figure 6) is the most actionable
artifact:

* **Every green classification in the atlas falls in moderate ARDS on
  the female surrogate (S2_F, S3_F).** Four of the six outputs are green
  in S2_F and three of six in S3_F; these are the only two cells with no
  diverged and no implausible run, and delivered Vt is green in both.
  Researchers running cohort-style validation studies may prefer this
  configuration when it suits their scientific question, subject to the
  use-case-specific validation that meeting the green criterion does not
  supply.
* **Severe ARDS on the male surrogate (S4_M) is the only cell red on
  every output.** Its divergence rate is doubled relative to the other
  male cells (8 / 160 vs 4 / 160) and 46 / 160 runs are implausible, so
  its 54 / 160 combined hard-failure rate is the only one in the atlas
  above the 30 % that makes a cell red on flags alone. Users should not
  interpret S4_M outputs as ground-truth physiology without careful
  per-input validation. Note
  that the male-divergence clustering reported here is specific to the
  [S006](#s006) input-extreme regime; the complementary continuous-severity
  sweep (§3.5.1) at midrange inputs produced balanced female / male
  divergence in the [0.879, 0.946] band, with the sex effect varying
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
  ≥ 300 s of total simulated time and use a plateau window in the final 60 s of that
  simulation, or treat PaO2 as a transient, not steady-state, output.
* **VC-AC tidal-volume oscillation refines rather than indicts Pulse's
  implementation.** The F-004 finding (Vt CV > 5 % in 20.6 % of runs) is
  not a controller pathology: patient-ventilator dyssynchrony at extreme
  settings is a real intensive-care phenomenon [@figueroacasas2016] and
  Pulse's behaviour is consistent with it. The atlas's preregistered steady-state detector simply
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
  4.2 details the −2 cmH2O setting validated by [S014](#s014) as a data-generation lever for deterministic sweeps (with the clinical caveat in §4.2). Second, the prevalence of
  oscillation events (20.6 % across the full 7-input sweep) bounds how
  much of Pulse's VC-AC behaviour at the default trigger configuration
  is steady-state interpretable. Sensitivity indices computed on the
  oscillation-flagged subset are not directly comparable to those on
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

*A short list of recommendations for downstream Pulse users. The most
consequential: for deterministic, steady-state-interpretable tidal
volume, set `InspirationPatientTriggerPressure` explicitly on VC-AC
actions (−2 cmH2O) — a data-generation lever, not a clinical
recommendation (see the caveat below); otherwise Pulse enables a
respiratory-model-driven patient trigger that produces realistic but
non-steady tidal volumes at the very ventilator-stress points where
validation matters most.*

**VC-AC trigger configuration.** When using Pulse 4.3.1's
`SEMechanicalVentilatorVolumeControl` action in *AssistedControl* mode,
always set `InspirationPatientTriggerPressure` or
`InspirationPatientTriggerFlow` explicitly. Leaving both unspecified
causes Pulse to enable a respiratory-model-driven patient trigger
(`SEMechanicalVentilatorVolumeControl.cpp` lines 120–128), which
produces effort-dependent tidal-volume variability consistent with patient-ventilator dyssynchrony but renders
delivered tidal volume non-steady at extreme input combinations. For sensitivity-analysis-style sweeps that require deterministic, steady-state-interpretable tidal volume, setting `InspirationPatientTriggerPressure = −2 cmH2O` collapses that variability (validated by [S014](#s014): median Vt_cv 0.351 to 0.016, a 96 % reduction; 78.1 % of locked runs below the 0.05 steady-state threshold). This is best read as a data-generation / exploration lever, not a clinical recommendation: locking the trigger to a fixed threshold leaves simulated inspiratory efforts below −2 cmH2O unrewarded, a form of patient-ventilator dyssynchrony [@thille2006] that is clinically undesirable [@blanch2015], corresponding in a real patient to a shift from patient-responsive assist-control toward controlled ventilation; such dyssynchrony is detectable on ventilator flow/pressure waveforms, though most directly confirmed with specialised monitoring such as esophageal pressure [@akoumianaki2014] or diaphragm electrical activity [@sinderby1999]. The −2 cmH2O lock is therefore an instrument for controlled software exploration and deterministic synthetic-data generation, not guidance for clinically realistic ventilation.

### 4.3 Implications for machine-learning pipelines using Pulse

*Why this atlas matters for anyone training models on Pulse synthetic
cohorts: 51.8 % of runs are clean, but the flagged 48.2 % follow
non-random patterns that can leak into supervised labels and inflate
apparent generalisation. The per-cell traffic light gives an immediate
curation map — the colour sets cell-level review priority, run-level
four-flag screening remains necessary in every cell, and red cells
require per-channel justification.*

The atlas's curation map is not only an instrument for direct Pulse
users; it doubles as a **per-cell curation layer for synthetic
training cohorts** generated by Pulse for machine-learning research.
This is non-trivial because Pulse has already been used as a
synthetic-data generator for machine-learning work on ventilation:
Ward et al. use the engine's respiratory dynamics simulator to gather
simulated data and to benchmark neural-network and optimal-control
ventilator policies for ARDS against the ARDSnet protocol
[@ward2024ventilator]. A model trained
on outputs from this atlas's red cells without filtering will
internalise simulator artefacts as if they were physiology:

* The 600 + mmHg PaO2 transient at FiO2 = 1.0 within the locked 120 s
  steady-state window (F-003, §3.8) becomes "what hyperoxia looks like"
  to the model — even though Pulse converges into the physiological
  alveolar-gas-equation band when given a 300 s window ([S021](#s021)).
* The 20.6 % VC-AC tidal-volume oscillation, consistent with inspiration-
  trigger dyssynchrony (F-004, §3.8), becomes "ventilator behaviour" to
  the model, even though it is corrected by a single configuration
  flag.
* The compensatory tachycardia that shifts output HR upward in
  S3 / S4 (§3.4.1) is a particularly insidious feature-engineering
  trap: a neural network trained on these outputs will learn an
  *active physiological response* (the engine's compensatory
  tachycardia under hypoxemia) as if it were a baseline
  steady-state feature of the cohort. Down-stream this becomes a
  learned input-output relation that does not exist in real patients
  with set heart-rate baselines, and the model will silently
  generalise this scenario-dependent compensation as a population
  property.
* The all-male divergence cluster (§3.5) becomes a "clinical pattern"
  if synthetic male / female cohorts are pooled without flag-stratified
  filtering.

The four-flag detector (§2.6) and the per-cell traffic-light map
(§3.7) together support a defensible ML-pipeline contract:

1. **Every cell:** apply the run-level four-flag screen irrespective of
   colour — the colour does not count runs flagged `not_steady_state` —
   and report the clean-rate per cell with the training-set metadata.
2. **Green and yellow cells:** the colour sets cell-level review
   priority; every use remains subject to use-case-specific validation.
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

### 4.4 Relationship to Cornish et al. 2026 (causal falsification) — Table 2

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
(family-wise error rate 0.05) — tested 1,522 hypotheses across 15
physiological quantities on MIMIC-III sepsis trajectories (Cornish's
main-text figure of 1,442 across 14 quantities omits the Arterial-pH
channel — 80 hypotheses, 0 rejections — that appears in their
Appendix Table 4; we report the full 15-channel total), with
intravenous-fluid and vasopressor doses as the intervention space.
Table 2 reproduces their per-quantity results re-tabulated against
this atlas's 6-output panel.

```{=latex}
\begin{center}
\begin{tabular}{lllc}
\toprule
Cornish-2026 channel & Hoeffding rejections / hypotheses & Bootstrap (Cornish Appendix Table 5) & Maps to atlas output? \\
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

*Table 2.* Cornish 2026 Table 4 (Hoeffding's inequality; the complete per-quantity
table listing all 15 assessed quantities) and Table 5 (reverse-percentile
bootstrap) re-tabulated against this atlas's six-output panel. Bold rows mark the four channels
that overlap directly with HR / MAP / PaO2 / PaCO2.

*Table 2 — at a glance.*
**What:** Cornish et al. (2026) per-channel rejection counts from
their causal-falsification framework on MIMIC-III sepsis trajectories,
re-tabulated against this atlas's six-output panel.
**How to read it:** each row is one Cornish quantity; the first
numeric column gives Hoeffding-inequality rejections (their main-text
Table 1), the second column the reverse-percentile bootstrap
rejections (their Appendix Table 5); the rightmost column maps each
channel to an atlas output (Yes / Partial / No). Bold rows are the
four-channel direct overlap.
**Key takeaway:** 82 of 85 Hoeffding rejections fall *outside* the
atlas's four-channel overlap: 80 on the eight channels the atlas does
not assess (electrolyte, metabolic, acid-base, dermal) plus 2 on
partial-overlap pressure channels. Only 3 (all PaCO2) fall on the
overlap. The four-channel overlap (HR, MAP,
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
four-channel atlas overlap (all on PaCO2); the remaining 82 fall outside
the four-channel direct overlap (80 on channels the atlas does not
assess at all + 2 on partial-input channels SysBP/DiaBP/RR)**. This non-overlap is the
central observation: the two papers' failure surfaces are
*complementary*, not redundant.

**The overlap.** Within the four-channel overlap, Cornish's Hoeffding
results report 3 / 70 rejections (4.3 %) for PaCO2 and zero
rejections for HR, MAP (MeanBP), and PaO2. No ordinal comparison
with the atlas's channel rankings is drawn here: Cornish's rejections
are indexed by (time-step, action-sequence, sex–age–quantile bin)
over sepsis trajectories, not by (scenario, sex) over the operational
acceptance envelope, and the two indexings are not surjective on each
other. The supported conclusion is the non-overlap above: the two
failure surfaces are complementary rather than redundant.

**The complementarity.** The 11 / 15 Cornish channels that do not
map to the atlas (Chloride 24, Sodium 21, Potassium 13, Skin
Temperature 10, Calcium 5, Glucose 5, HCO₃ 2, plus SysBP / DiaBP /
pH / RR) define Pulse's electrolyte, metabolic, acid–base, and
dermal failure surface. The atlas does not assess any of these.
Conversely, Cornish does not assess SpO2 or delivered Vt, both of
which are central to ventilator-cohort research. The two
papers therefore divide the Pulse-reliability question along an
output axis: Cornish covers chemistry-and-dermal
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
   sequences* — Cornish: of the four channels shared with the atlas,
   PaCO2 is the only one flagged under Hoeffding (3 / 70) and the most
   flagged under the bootstrap (13 / 70, against PaO2 4 / 78, MeanBP
   3 / 92, HR 1 / 162).
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
  Vt at FiO2 ≥ 0.95: HR and MAP drift rates stay below 3 % and PaCO2
  below 4 % in both vulnerable populations, so in those audited populations
  threshold exceedances are uncommon for HR, MAP and PaCO2, while delivered Vt
  is itself one of the two window-sensitive channels.
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
* On the reference machine, the canonical sweep required
  approximately 14 h of active elapsed time, using three parallel
  Docker workers initially and two after a mid-sweep reduction to
  control thermal load (resume-safe); the timing-metadata correction
  is documented in Supplement §S12. The preregistered Sobol
  bolt-on (preregistration §Sampling method) was evaluated and
  formally closed in §3.3.1; if future work re-opens it on the
  Group B cells, larger-scale variance decomposition would benefit
  from a cluster.
* **Implausibility bounds are clinically anchored but not unique
  within the clinical-judgment category.** The `HARD_BOUNDS` table
  (§2.6) categorizes each bound as either physical
  (e.g., SpO2 ≤ 100 %) or a clinical
  *"incompatible-with-60-s-steady-state-in-window"* threshold. Within
  the second category, the exact numerical choice (e.g., PaO2 lower
  20 vs 25 mmHg, MAP lower 30 vs 35 mmHg) is a defensible judgment
  call rather than a unique biological constant — different clinical
  philosophies, anchored in the same Severinghaus / Berlin /
  Sepsis-3 / ICU-textbook literature [@severinghaus1979; @ards2012;
  @singer2016; @marino2013icu; @marini2018critical], could land on
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
  **170 runs** flagged because of the F-004 tidal-volume
  oscillation (§3.8; its trigger dependence causally confirmed by
  [S014](#s014)); and (iii) a **185-run residual** dominated by S4
  severe-ARDS slow convergence and S1 transient hyperoxia drift
  (the F-003 phenomenon documented in §3.8 / [S012](#s012) /
  [S021](#s021)). Of these, only (i) is a detector classification
  edge case; (ii) and (iii) are real Pulse engine behaviours that
  the locked classifier is correctly identifying. The headline atlas
  numbers in §3.1 Table 1 stand under the locked classifier; the
  per-cell sub-mode attribution table is reported in
  [Appendix C](#appendix-c)
  for readers who want to score "engine instability" separately from
  "detector edge case on healthy oxygenation." Under the joint
  exclusion the clean rate would rise from 51.8 % to 78.8 % — this is
  presented as a decomposition, not a re-classification.
* **`not_steady_state` cross-validation by ML/SHAP surrogate.** A
  supplementary RandomForest + SHAP attribution on the n = 663 clean
  subset ([S023](#s023)) shares 17 / 18 possible input memberships with
  the Morris μ\* top-3 **sets** across the six pooled output-level
  comparisons (five outputs 3/3, PaO2 2/3), and matches 23 / 48 per-cell cases at full
  3 / 3 set agreement (92 % of per-cell comparisons share at least
  2 / 3 — a partial overlap, not a preserved order). The
  cross-check is reported in supplementary section S11 with the
  honest caveats it requires (clean-subset bias, OAT non-uniform
  design); see [`results/s023/`](../results/s023/) for artefacts.
* **To our knowledge, no comparable open atlas exists for sibling
  engines.** The atlas reports Pulse-specific reliability behaviour;
  it does not establish
  whether the patterns reported here (sex-stratified divergence,
  VC-AC tidal-volume oscillation at default trigger settings, transient hyperoxia
  regime at FiO2 = 1.0 in a 120 s steady-state window) are unique to
  Pulse or generic to related physiology
  engines such as BioGears or HumMod. To our
  knowledge, no comparable publicly available reliability atlas
  combining Morris screening with explicit clamping analysis has been
  published for either BioGears or HumMod at the time of writing, so
  cross-engine relativisation remains limited by the available
  comparative literature. A multi-engine reliability atlas remains an
  open opportunity for the broader physiology-simulation community.

### 4.6 Implications for downstream Pulse research

*The two downstream research lines this atlas opens hooks for: the
pediatric translation layer (Paper 1, in preparation; validation
underway with the Sainte-Justine PICU cohort) and the native pediatric
Pulse fork (Paper 2, planned). Both depend on the atlas's μ\* rankings
and traffic-light curation map as the backdrop for what scope they
can target.*

This atlas is positioned as foundational infrastructure for two
downstream lines of work, both currently in preparation:

* **Pediatric translation layer (Paper 1, in preparation; validation
  underway with the Sainte-Justine PICU cohort).** Maps pediatric
  vital signs onto Pulse's adult engine via quantile matching, and
  uses the atlas's μ\* rankings and traffic-light curation map as
  the backdrop for what the translation layer is allowed to do —
  explicitly, the translation layer must keep its output baselines
  inside the green / yellow cells of Figure 6. The present
  adult-envelope characterisation is the *methodological prerequisite*
  for this translation work: a pediatric adaptation cannot be safely
  derived from an unmapped substrate.
* **Native pediatric Pulse fork (Paper 2, planned).** Modifies
  Pulse's C++ source for paediatric physiology. Source-code patch
  ordering is prioritised by the atlas's input-importance ranking:
  equations driving high-μ\* inputs (heart-rate baseline, FiO2 / PEEP,
  Vt) are patched first; equations driving low-μ\* inputs are deferred.

Neither downstream paper is required for this atlas's claims. The
atlas stands independently on Pulse's public documentation, the
publicly-cloned Pulse v4.3.1 source, and the experiments logged in
this repository.

### 4.7 Engine-side enhancements that would benefit future atlas users

*A short set of infrastructure-level suggestions for the Pulse
maintainers, derived from operating the engine at scale during the
1,280-run sweep. These are framed as observations from atlas-user
experience, not as physiological prescriptions: every item targets
tooling, documentation, or validation infrastructure, and each traces
to a specific experiment-log entry. None of the items below recommend
changes to Pulse's underlying lumped-parameter physiology, which is
the domain of the Kitware biomedical-engineering team.*

The 1,280-run sweep ([S006](#s006)) and the surrounding
infrastructure work ([S004](#s004), [S014](#s014), [S017](#s017),
[S018](#s018), [S021](#s021)) surfaced six places where small
additions to Pulse's existing tooling, documentation, or validation
scaffolding would substantially lower the friction for downstream
users running reliability- or sensitivity-style work. We offer these
as a contribution back to the Pulse community in the same spirit as
the atlas itself: every item below is anchored in a concrete
experiment from this paper, and each is scoped to the tooling /
documentation / validation layer rather than the physiology layer.

1. **Structured input-rejection events.** Pulse currently surfaces
   input clamping (e.g. SBP > 120, DBP/SBP ratio out of range, HR / RR
   outside the initialization band) as `[ERROR]`-prefixed log lines
   that downstream tools must regex-parse. A small structured-event
   API — one typed record per rejected field, with the offending
   value, the enforced bound, and the field name — would let
   sensitivity-analysis wrappers detect clamping deterministically
   instead of pattern-matching the regex set documented in §2.6. Anchored in
   the atlas's `src/detector.py` clamp-pattern catalogue and the
   pilot / full-sweep experience ([S004](#s004), [S005](#s005),
   [S006](#s006)).

2. **Surface the male-surrogate `BloodVolumeBaseline` floor in user
   documentation.** Pulse hard-enforces a 4,082.24 mL blood-volume
   floor at setup on the 67.3 kg / 180 cm male reference body
   (default 4,802.63 mL), but this constant is not currently exposed
   in the public patient-setup documentation. We discovered it
   empirically while investigating the all-male divergence cluster
   ([S018](#s018)); a one-line note in the patient-baseline reference
   table would have saved the investigation. Anchored in
   [S018](#s018) and the verified BV-floor mechanism documented in
   §3.5 of this paper.

3. **A reference sensitivity-analysis recipe for user-facing
   operational inputs.** Pulse's repository already carries a 2020
   `STUDY_SENSITIVITY_ANALYSIS_1_0_0` tag that performs Sobol
   sensitivity on internal lumped-parameter circuit values
   (cardiovascular and respiratory resistances and compliances) for calibration; this is a different parameter class from the
   user-facing operational inputs (HR, SBP, DBP, RR, Vt, FiO2, PEEP) that
   sensitivity-conscious downstream users typically need to sweep. A
   companion recipe — Morris or Sobol over operational inputs,
   shipped alongside the existing study — would give the Pulse
   community a maintained reference implementation. The atlas's
   `src/sampler.py` and `src/runner.py` are an externally-developed
   prototype; a maintainer-blessed version would be more durable.
   Anchored in [S006](#s006) and the GitLab re-audit
   ([S016](#s016)).

4. **A setup-time warning for the ARDS impairment-fraction
   instability zone (~0.91–0.945).** This instability zone is
   documented in our preregistration (scenario table and H3) and in the
   §1.2 limitations list (entry 4), and corroborated by three independent
   sources, but Pulse does not
   currently emit a setup-time warning when an ARDS action lands in
   the zone. A single console notice — "impairment fraction in
   reported instability band, results may not be reliable" — would
   prevent downstream users from collecting unusable data without
   blocking legitimate edge-case research. Anchored in the
   `Pulse_translation_new` E6 / E10 boundary probes and the atlas's
   continuous-severity sweep (§3.5.1).

5. **Per-channel steady-state convergence diagnostic in CSV
   output.** Our F-003 finding (PaO2 still rising at the end of the
   locked 120 s window at FiO2 = 1.0, with full convergence at
   ~300 s — [S021](#s021)) suggests that an optional per-output
   "drift over final 60 s" column appended to result CSVs would let
   users detect non-steady-state runs without writing their own
   post-processing. The atlas's `src/detector.py` already implements
   exactly this calculation; promoting the same diagnostic upstream
   would generalise it. Anchored in F-003, [S012](#s012), and
   [S021](#s021).

6. **Field-attributed setup-error messages.** Current setup-time BP
   and pulse-pressure-ratio rejection messages (verified in the
   atlas's clamp-detection corpus, [S005](#s005)) require some
   domain knowledge to map back to the offending input field. A
   one-token prefix indicating which input was rejected
   (`[ERROR][SystolicArterialPressure]` rather than the unprefixed
   text) would let downstream users and CI pipelines route the
   message without reading it. Anchored in [S005](#s005).

These suggestions are deliberately infrastructure-level: none of
them touches Pulse's underlying physiology, ODE topology, or
lumped-parameter assumptions, all of which lie outside the scope of
what an external operational-reliability study can credibly
prescribe. We share them in the spirit of an open contribution to a
shared community tool — the atlas itself is offered to the Pulse
community in exactly the same spirit, and the present paper would
have been substantially easier to produce had each of items 1–6
already been in place.

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
(Figure 6) delivers an immediate, actionable curation and
review-priority layer for
clinical researchers, device developers, and machine-learning
practitioners using Pulse for synthetic cohort generation.

Beyond mapping the envelope, this work yielded two
operator-actionable corrections — resolving VC-AC tidal-volume
oscillation (F-004) via an explicit
`InspirationPatientTriggerPressure = −2 cmH2O` setting
([S014](#s014); median Vt CV collapses 0.351 → 0.016, worst-case
1.826 → 0.018) and reframing the apparent FiO2 = 1.0 PaO2 overshoot
as a transient hyperoxia regime (F-003), with the 300 s plateau
landing ~ 20 mmHg below the alveolar-gas-equation prediction
([S021](#s021); median 643 mmHg vs ~ 663 mmHg predicted) — an
undershoot rather than an oxygenation defect. We also established a
previously uncharacterized, *regime-dependent*, sex-stratified
reliability-sensitivity axis: concentrated on gas-exchange outputs under permutation-based BH-FDR
control (5 of 24 cell × output Wasserstein survivors, §3.6) and on
the male input-extreme divergence cluster, which depends on Pulse's
blood-volume baseline ([S018](#s018); 20 / 20 → 0 / 20 BV
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

All **derived** data, code, and lab notebooks needed to reproduce the
numbers, figures, and tables in this paper are openly available in the
repository. The raw per-run Pulse CSVs and setup logs are deliberately
excluded from git (1,280 raw CSVs plus ~105 MB of engine logs belong in
the Zenodo deposit, not in git history; see `.gitignore`) — which is
why one ledger anchor (`T1.06u`) auto-skips on a public clone, giving
393 / 394 there against 394 / 394 on the authors' full data tree.

Licensing follows the function of each artefact, not the folder it sits
in: code and the per-experiment lab-notebook entries under Apache
License 2.0; the deposited data and this monograph's own content under
CC-BY-4.0. Verbatim third-party excerpts — notably from the Pulse
documentation and source (Apache-2.0) — retain their original terms.

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
  Python script verifying that every quantitative
  claim registered in the ledger matches the canonical artifacts
  under explicit per-class tolerance rules; current state 394 / 394
  PASS on the authors' full data tree (393 / 394 on a public clone,
  where the one anchor needing the gitignored raw S021 trajectories
  is auto-skipped) ([S024](#s024); see §2.8 for protocol).
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
  history by `.gitignore` (per-run output.csv / output_pulse_native.csv /
  pulse.log / config.json / run_meta.json across the 1,280-run sweep + S014 +
  S018 + S021; ~ 2.2 GB total, measured 2026-07-29) will be uploaded to a public Zenodo
  archive upon acceptance; DOI added here on deposit.

---

## 7. Acknowledgements

This work benefited from government funding managed by the National
Research Agency under France 2030 via the ENACT AI Cluster
(ANR-23-IACL-0004).

This work also relies on the financial support provided by the Région
Grand Est, France, for which we express our gratitude.

We thank the BIOSE Doctoral School of the Université de Lorraine for
its support.

We gratefully acknowledge the support of the CHU Sainte-Justine
Foundation in Montreal and the Artificial Intelligence Applied to
Pediatric Acute Care Research Group (R-SADC) in Montreal, Canada.

We thank the Kitware Pulse engineering team for the open-source
release of the Pulse Physiology Engine and its accompanying
documentation, without which this work would not have been
possible.

We also thank Jama Hussein for productive and inspiring discussions
at the Mila — Quebec AI Institute.

**Author contributions.** S.N. conceived and led the study — whose overarching research
direction was shaped through clinical discussions with M.S. and
P.J. — designed the Morris sweep and the four-flag steady-state
classifier, performed all computational runs and statistical
analyses, and wrote the manuscript. M.S. provided detailed clinical review of the manuscript and contributed the clinical interpretation of the VC-AC inspiration-trigger caveat. Y.M. contributed to the cross-platform reproducibility validation of the simulation environment, and to the review and editing of the manuscript. A.W. contributed to the study's conceptualization and to the iterative scientific refinement of the analysis and its framing (notably the ARDS severity-to-Berlin calibration and the reliability-classification transparency) through sustained methodological discussion, in addition to clinical supervision and manuscript review. C.S., M.S., and P.J. provided clinical supervision, contributed to the interpretation of the findings in their clinical context, and reviewed the manuscript. C.S., M.S.,
and P.J. additionally secured the funding that supported this work.
All authors approved the final version. AI tooling (Claude Code,
`claude-opus-4-7` for the original drafting/refactoring, `claude-opus-4-8`, released 28 May 2026 and coinciding with the supervisor-review phase, for the subsequent supervisor-review revisions, and `claude-opus-5` from 24 July 2026 for the in-repository calibration replication and the primary-source reference audit, cross-checked against Gemini Pro 3.1 up to 2 August 2026 and against OpenAI ChatGPT (GPT-5.6 Sol, High reasoning level) from 3 August 2026) provided drafting / refactoring /
reviewer-style critique assistance on text and code only, as
detailed in §8.

**Competing interests.** The authors declare no competing
interests, financial or otherwise.

---

## 8. Transparency: use of AI tools

In the interest of full methodological transparency, parts of this
work were carried out with the assistance of AI tools, used within a
cross-checking loop between two large language models under direct
supervision by S.N.: Claude Opus 4.7/4.8, and from 24 July 2026
Claude Opus 5 (Anthropic), used locally
through the Claude Code agent at the `xhigh` thinking-effort default,
and, as the second model, Gemini Pro 3.1 (Google;
extended-thinking mode) through a separate web session up to and
including 2 August 2026, replaced from 3 August 2026 by OpenAI
ChatGPT (GPT-5.6 Sol, High reasoning level, browser session), with no further use of
Gemini thereafter. Prompt
engineering instructed each model to critique and cross-correct the
other's outputs at every iteration, mitigating hallucination by
verifying claims against the audit ledger and the source code.

* **Coding assistance.** Portions of the analysis and pipeline code
  in this repository were drafted, edited, refactored, or debugged
  within the dual-model cross-checking loop described above
  (**Claude Code** with `claude-opus-4-7` / `claude-opus-4-8` /
  `claude-opus-5`, and as second model **Gemini Pro 3.1** to
  2 August 2026, then **OpenAI ChatGPT** (GPT-5.6 Sol, High reasoning level)).
  Every AI-assisted code change was reviewed,
  tested, and committed by S.N.; all preregistered
  thresholds, hypotheses, and experimental decisions were authored
  and locked by S.N. before the corresponding analyses
  were run. AI tooling did not modify preregistration content or
  finalised numerical results.
* **Manuscript drafting and editing.** Portions of this manuscript
  were drafted and edited within the same dual-model cross-checking
  loop (Claude Code, with Gemini Pro 3.1 as second model to
  2 August 2026 and OpenAI ChatGPT (GPT-5.6 Sol, High reasoning level) thereafter). All
  scientific claims, statistical interpretations, and citations
  were authored, verified, and accepted by S.N. Every
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
    GitLab repository. Sobol S1/ST analysis, direct or through an ML surrogate,
    over internal lumped-parameter circuit values (cardiovascular and
    respiratory resistances and compliances; model-calibration parameters); ReadMe scope
    statement: *"sensitivity analysis as a path towards improved
    lumped parameter optimization."* The code is still in the
    4.3.x source tree; no published re-run on 4.3.x was found. Cited in §1.1 to
    distinguish internal-calibration SA (their scope) from
    operational-input SA (this paper's scope). Audit logged in
    [S016](#s016) (2026-05-07).
4. **Cornish R, Taufiq MF, Doucet A, Holmes C (Oxford, 2026).**
    *Causal Falsification of Digital Twins.* Journal of Machine Learning
    Research 27(152):1–52 (2026); preprint arXiv:2301.07210 (v4, November
    2023). External statistical-falsification framework
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
   acceptance bounds (verified by the companion E10 boundary probe and
   its HR / RR initialisation probes).
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
   Cited as the parallel pediatric ARDS-severity framework (PALICC-2
   itself favours the Oxygenation Index / Oxygen Saturation Index over
   P/F). The atlas's adult scenarios S2 (0.26), S3 (0.60), S4 (0.95)
   are anchored on the Berlin Definition P/F bands, calibrated
   empirically at the reference ventilation setting (Appendix B.3) — not
   on PALICC-2.
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
  mapping (mild = 0.3, moderate = 0.6, severe = 0.9). This page does
  not itself state the per-band P/F-ratio values (340 / 130 / 50 mmHg);
  those come from the peer-reviewed Webb 2020 Pulse-team COVID-19
  paper (Webb 2020 entry above), to which §2.3 and Appendix B.3
  correctly attribute them. Cited in §2.3
  and Appendix B.3 as the canonical documentation against which the
  empirically calibrated mapping {0.26, 0.60, 0.95} is contrasted at
  that appendix's reference ventilation setting. Verified verbatim
  2026-05-15.
  Also, from 2026-07-26, the source of the 5-compartment lung
  description (carina, right and left anatomic dead space, right and
  left alveoli) and of the no-inertance limitation, both verified
  verbatim; those two claims had been mis-attributed to Bray 2019,
  which contains neither.
* []{#ref-pulsecardiomethod} Kitware, Inc. *Cardiovascular Methodology — Pulse
  Physiology Engine documentation (v4.3.1).*
  <https://pulse.kitware.com/_cardiovascular_methodology.html>.
  Source of the heart modelled as a time-varying capacitor in "Pulse in a
  nutshell", verbatim: *"The heart model generates pressure that drives the
  hemodynamics through a variable capacitor that simulates the changing
  elastance of the myocardium throughout the cardiac cycle."* That sentence
  earlier called the heart a time-varying pressure source, which this page
  contradicts. Verified verbatim 2026-09-28 at tag `REL_4_3_1`
  (`docs/Methodology/CardiovascularMethodology.md`, L113).
* []{#ref-pulseabout} Kitware, Inc. *About Pulse — Pulse Physiology Engine.*
  <https://pulse.kitware.com/_about_pulse.html>.
  Source of the language-binding and platform list, verbatim: *"easy
  cross-platform deployment on all standard operating systems
  (Windows, Mac, Linux, and ARM) and multiple languages (C++, C#,
  Java, Unity)."* Android and iOS are not listed on this page — they
  appear only in the changelog (iOS build support, v4.2.0, October
  2023) — and are therefore no longer claimed. Previously
  mis-attributed to Bray 2019. Verified verbatim 2026-07-26.
* []{#ref-pulseinaction} Kitware, Inc. *Pulse in Action — Pulse Physiology
  Engine.* <https://pulse.kitware.com/pulse-in-action.html>.
  Source of the medical-education / simulation-training claim. Named
  integrations, verbatim: *"Pulse is of particular importance for emergency
  medical training simulations like VRescue"*; *"SimPulse utilizes Kitware's
  Pulse Physiology Engine"*, *"well-suited for use in lab, classroom, and
  remote settings"*, *"presenting healthcare learners with real-time,
  physiological and pharmacological patient data"*. The page separates these
  named integrations from a list introduced as *"a wide range of potential
  applications"* (serious games, manikin training); only the named
  integrations are cited. Verified verbatim 2026-08-25.
* []{#ref-pulsefaq} Kitware, Inc. *Pulse FAQ.*
  <https://pulse.kitware.com/_f_a_q.html>. Accessed April 2026; re-verified
  2026-07-27. Source of Pulse's own statement that it has performed no formal
  sensitivity analysis or uncertainty quantification, and — from 2026-07-27 — of
  the engine's documented execution speed, verbatim: *"The engine currently runs
  at about 5 to 10 times real time, depending on your machine's
  specifications."* This entry was cited in the body but missing from this list
  before 2026-07-27.
* []{#ref-pulsesystem} Kitware, Inc. *System Methodology — Pulse Physiology
  Engine documentation (v4.3.1).*
  <https://pulse.kitware.com/_system_methodology.html>.
  Source of Pulse's self-description, under "Assumptions and
  Limitations", that *"the engine uses a low fidelity clinical
  approach and is not necessarily for high fidelity predictive
  purposes"*; cited in §1.1 as the maintainer-stated design philosophy
  that frames the present reliability mapping. Citation re-pointed
  2026-06-05 from the Nervous System Methodology page (which does not
  carry this phrase) to the System Methodology page, where it appears
  verbatim.
* []{#ref-cornish2023} Cornish R, Taufiq MF, Doucet A, Holmes C. *Causal Falsification
  of Digital Twins.* Journal of Machine Learning Research 27(152):1–52
  (2026); first posted as arXiv:2301.07210 and read in its v4 (November
  2023); the published Tables 4 and 5 keep the same counts and add
  Manski-bound columns.
  Oxford statistics group. External assessment of Pulse on MIMIC-III
  sepsis trajectories using a causal-inference / statistical-
  falsification framework with Holm–Bonferroni-adjusted Hoeffding's
  inequality confidence intervals (FWER 0.05) on 1,522 hypotheses
  across 15 physiological quantities; identifies intervention-outcome
  inaccuracies in specific cases (Appendix Table 4: 85 total Hoeffding
  rejections; Appendix Table 5: 281 reverse-percentile-bootstrap
  rejections). Cited in §1.1 to distinguish prior external assessment
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
* []{#ref-herman2017salib} Herman J, Usher W. *SALib: An open-source Python
  library for Sensitivity Analysis.* Journal of Open Source Software 2(9):97
  (2017). DOI: [10.21105/joss.00097](https://doi.org/10.21105/joss.00097).
  SALib's documentation asks for both this paper and Iwanaga et al. 2022.
* []{#ref-lundberg2020tree} Lundberg SM, Erion G, Chen H, DeGrave A, Prutkin JM,
  Nair B, et al. *From local explanations to global understanding with
  explainable AI for trees.* Nature Machine Intelligence 2(1):56-67 (2020).
  DOI: [10.1038/s42256-019-0138-9](https://doi.org/10.1038/s42256-019-0138-9).
  TreeExplainer, the estimator used by the SHAP cross-check.

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
  precedent for the patient-ventilator dyssynchrony phenomenon with
  which the tidal-volume oscillation F-004 quantifies inside Pulse is
  consistent. Identified and verified via PubMed
  esummary during the 2026-05-15 novelty audit ([S020](#s020)); the atlas's
  contribution is a Pulse-engine oscillation consistent with it and the corrective
  trigger setting (−2 cmH2O), not the discovery of dyssynchrony.
* []{#ref-thille2006} Thille AW, Rodriguez P, Cabello B, Lellouche F, Brochard L.
  *Patient-ventilator asynchrony during assisted mechanical ventilation.*
  Intensive Care Medicine 32(10):1515-1522 (2006). DOI:
  [10.1007/s00134-006-0301-8](https://doi.org/10.1007/s00134-006-0301-8).
  PMID: 16896854. Cited in §4.2: sub-threshold inspiratory efforts left
  unrewarded are a form of patient-ventilator dyssynchrony. Its Measurements
  section also records that asynchrony was "detected visually on 30-min
  recordings of flow and airway pressure", which is why §4.2 no longer says
  specialised monitoring is the only way to see it.
* []{#ref-blanch2015} Blanch L, Villagra A, Sales B, et al. *Asynchronies during
  mechanical ventilation are associated with mortality.* Intensive Care
  Medicine 41(4):633-641 (2015). DOI:
  [10.1007/s00134-015-3692-6](https://doi.org/10.1007/s00134-015-3692-6).
  PMID: 25693449. Cited in §4.2 for "clinically undesirable". The study stops
  short of causation — its own conclusions call for further work on whether
  asynchrony is a marker or a cause — so this wording must not be strengthened
  into a mortality claim.
* []{#ref-akoumianaki2014} Akoumianaki E, Maggiore SM, Valenza F, et al. (PLUG
  Working Group, ESICM). *The application of esophageal pressure measurement in
  patients with respiratory failure.* American Journal of Respiratory and
  Critical Care Medicine 189(5):520-531 (2014). DOI:
  [10.1164/rccm.201312-2193CI](https://doi.org/10.1164/rccm.201312-2193CI).
  PMID: 24467647. Cited in §4.2: esophageal pressure as a specialised
  confirmation of inspiratory effort. Verified at abstract depth only
  (journal paywall).
* []{#ref-sinderby1999} Sinderby C, Navalesi P, Beck J, et al. *Neural control of
  mechanical ventilation in respiratory failure.* Nature Medicine
  5(12):1433-1436 (1999). DOI: [10.1038/71012](https://doi.org/10.1038/71012).
  PMID: 10581089. Cited in §4.2: diaphragm electrical activity (EAdi) as the
  other specialised confirmation.

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

**Critical-care and respiratory-physiology references (physiological-bound anchors)**

* []{#ref-severinghaus1979} Severinghaus JW. *Simple, accurate equations for human blood O2
  dissociation computations.* Journal of Applied Physiology:
  Respiratory, Environmental and Exercise Physiology 46(3):599-602
  (1979). DOI:
  [10.1152/jappl.1979.46.3.599](https://doi.org/10.1152/jappl.1979.46.3.599).
  PMID: 35496. Oxyhemoglobin dissociation curve (P50); anchors the
  SpO2 and PaO2 hard bounds.
* []{#ref-kuczmarski2002cdc} Kuczmarski RJ, Ogden CL, Guo SS, Grummer-Strawn LM, Flegal KM, Mei Z, Wei R, Curtin LR, Roche AF, Johnson CL. *2000 CDC Growth Charts for the United States: Methods and Development.* Vital and Health Statistics, Series 11, No. 246:1-190 (2002). PMID: 12043359. National Center for Health Statistics; source of the sex-specific 50th-percentile weight- and stature-for-age reference values for the atlas reference bodies.
* []{#ref-singer2016} Singer M, Deutschman CS, Seymour CW, Shankar-Hari M, Annane D,
  Bauer M, et al. *The Third International Consensus Definitions for
  Sepsis and Septic Shock (Sepsis-3).* JAMA 315(8):801-810 (2016).
  DOI: [10.1001/jama.2016.0287](https://doi.org/10.1001/jama.2016.0287).
  PMID: 26903338. Vasopressor-dependent MAP ≥ 65 mmHg; anchors the
  MAP lower bound.
* []{#ref-evans2021sepsis} Evans L, Rhodes A, Alhazzani W, Antonelli M, Coopersmith CM,
  French C, et al. *Surviving Sepsis Campaign: International Guidelines
  for Management of Sepsis and Septic Shock 2021.* Critical Care
  Medicine 49(11):e1063-e1143 (2021). DOI:
  [10.1097/CCM.0000000000005337](https://doi.org/10.1097/CCM.0000000000005337).
  PMID: 34605781. International initial resuscitation target MAP of
  65 mmHg, recommended over higher targets.
* []{#ref-mancia2023esh} Mancia G, Kreutz R, Brunström M, Burnier M, Grassi G,
  Januszewicz A, et al. *2023 ESH Guidelines for the management of
  arterial hypertension.* Journal of Hypertension 41(12):1874-2071
  (2023). DOI:
  [10.1097/HJH.0000000000003480](https://doi.org/10.1097/HJH.0000000000003480).
  PMID: 37345492. Hypertensive-emergency definition: grade 3 hypertension
  (SBP ≥ 180 and/or DBP ≥ 110 mmHg, Table 1 p. 1886) with acute
  symptomatic organ damage; anchors the MAP upper bound.
* []{#ref-nin2017} Nin N, Muriel A, Peñuelas O, Brochard L, Lorente JA,
  Ferguson ND, et al. *Severe hypercapnia and outcome of mechanically
  ventilated patients with moderate or severe acute respiratory distress
  syndrome.* Intensive Care Medicine 43(2):200-208 (2017). DOI:
  [10.1007/s00134-016-4611-1](https://doi.org/10.1007/s00134-016-4611-1).
  PMID: 28108768. Maximum-PaCO2 distribution in 1,899 ARDS patients from
  927 ICUs in 40 countries; anchors the PaCO2 upper bound.
* []{#ref-west2020respiratory} West JB, Luks AM. *West's Respiratory Physiology: The
  Essentials.* 11th ed. Philadelphia, PA: Wolters Kluwer Health /
  Lippincott (2020). ISBN: 978-1-9751-3918-6. Anatomical dead space
  (Ch. 2) and the alveolar-gas equation behind the PaO2 ceiling
  (≈ 663 mmHg at FiO2 = 1.0, Ch. 5). Both chapter pointers were
  verified against the cited edition on 2026-07-27. The work is also
  cited, without a chapter pointer, for the PaCO2 drift-threshold row
  of the steady-state table; that citation has not been pinned to a
  chapter and is the last one outstanding for this reference. The
  former "acid-base ranges" annotation was withdrawn on 2026-07-28:
  no locus in this monograph cites the work for one, and the
  CO2-narcosis justification it once supported was withdrawn on
  2026-07-27 after the 9th, 10th and 11th editions were searched and
  found not to contain the concept.
* []{#ref-marino2013icu} Marino PL. *Marino's The ICU Book.* 4th ed. Philadelphia, PA:
  Lippincott Williams & Wilkins / Wolters Kluwer (2013). ISBN:
  978-1-4511-2118-6. Pre-lung-protective tidal volumes of 10-15 mL/kg
  (Ch. 25), which anchor the Vt upper bound — the sole claim this work
  now carries. Its former HR and PaCO2 annotations were withdrawn on
  2026-07-27 after a full-text search of the cited edition: it states
  no extreme heart-rate threshold, and no CO2-narcosis threshold, and
  the PaCO2 upper bound is now anchored on Nin et al. instead.
* []{#ref-marini2018critical} Marini JJ, Dries DJ. *Critical Care Medicine: The Essentials
  and More.* 5th ed. Philadelphia, PA: Wolters Kluwer (Lippincott
  Williams & Wilkins) (2018). ISBN: 978-1-4963-0291-5. Upper heart-rate
  bound (Ch. 1: sinus rates exceeding (220 − age)/min reduce cardiac
  output and myocardial perfusion). The former SpO2 annotation was
  withdrawn on 2026-07-27: the critical-oxygen-delivery concept does
  appear in the cited edition, but in Ch. 2, without a number, and
  about delivery rather than saturation. (5th edition; LWW publisher
  date confirmed as 2018 in the 2026-06-05 re-audit — bib key updated
  to marini2018critical accordingly. The copyright page reads 2019;
  see audit/reference_audit.md, OPEN-3.)

---

## Appendix A — Experiment log index

*Every `S0xx` code used in this monograph is a lab-notebook entry in
`experiments_log/santino/`, numbered in the order the experiments were
run. The list below is complete. Codes of the form `E1` – `E10` belong
instead to the companion `Pulse_translation_new` project and are not
indexed here.*

| ID | Title |
|---|---|
| []{#s001} S001 | Docker + hardware smoke test |
| []{#s002} S002 | Project bootstrap |
| []{#s003} S003 | Verified Pulse 4.3.1 limitations |
| []{#s004} S004 | Atlas image + scenario smoke + detector recalibration |
| []{#s005} S005 | 22-run pilot on S1_M |
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
| []{#s019} S019 | Restricted exploratory Sobol demonstrator (Phase B item B3 — not executed; not the preregistered bolt-on) |
| []{#s020} S020 | Pre-submission novelty audit (literature double-check on every "first" claim; one citation added) |
| []{#s021} S021 | Hyperoxia convergence (60-run rerun at 300 s vs locked 120 s window; F-003 mechanism test) |
| []{#s022} S022 | No-compute failure-mode attribution audit of the locked `not_steady_state` count (see Appendix C) |
| []{#s023} S023 | Supplementary ML/SHAP cross-check of Morris μ\* top-three input sets on the clean subset (see Supplementary §S13) |
| []{#s024} S024 | Pre-submission claims-ledger audit (programmatic verification of the quantitative claims registered in the audit ledger; 394 / 394 PASS on the authors' full data tree, 393 / 394 on a public clone with one auto-skipped anchor, see §2.8) |
| []{#s025} S025 | Pre-release OSS code-hygiene audit and fixes |
| []{#s026} S026 | Final pre-arXiv polish |

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
downstream PhD repository; GitHub URL to be filled in once Paper 1 is
published).

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
  that Pulse accepts FiO2 = 1.0 and produces a stable trajectory; the
  transient hyperoxia regime and the extended-window solver-instability
  tail at that setting are characterised separately in §3.8. In the focused
  single-input probe (the companion `Pulse_translation_new` FiO2 = 1.0
  crash probe, 9 runs sweeping
  FiO2 ∈ {0.95, …, 1.00} on a healthy male surrogate at fixed
  ventilation), PaO2 scales linearly by approximately 7.8 mmHg per
  0.01 increase in FiO2. The atlas's multi-input Morris fit on the
  S1 clean runs, whose FiO2 spans only [0.21, 0.47], gives a flatter
  slope of ~5 mmHg per 0.01 FiO2 (§3.8, F-003): the difference reflects
  the averaging across a wider FiO2 envelope and across the seven
  perturbed inputs rather than a per-step single-input perturbation
  near the FiO2 = 1.0 boundary.

### B.3 ARDS severity calibration and solver instability

The Acute Respiratory Distress Syndrome (ARDS) condition in Pulse is
modulated by a per-lung `Severity` scalar in [0, 1]. This appendix
documents the calibration of that scalar against the Berlin
Definition [@ards2012] severity bands at a low-tidal-volume
reference ventilation setting based on the ARDSnet framework
[@brower2000], and the solver-instability zone
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

**Empirical calibration at the reference ventilation setting.** The
documented mapping was tested directly against the male reference
surrogate (age 18, 67.3 kg, 180 cm) in a 28-run impairment-
fraction sweep (`Pulse_translation_new`, the original ARDS severity
calibration, 2026-03; the full log is the canonical record of the
calibration — the later `E6` experiment is its April refinement).
The ventilation regime was held constant across all 28 runs:

* Mode: VC-AC (volume-control assist-control).
* Tidal volume: 403.8 mL = 6 mL/kg of **actual** body weight on the
  67.3 kg male standard — a low-tidal-volume setting based on the
  ARDSnet framework [@brower2000], which specifies 6 mL/kg of
  predicted body weight.
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

| `Severity` | Documented P/F (mmHg) | Measured P/F at the reference setting (mmHg) | Berlin classification of measured value |
|------------|------------------------|------------------------------------------|------------------------------------------|
| 0.3        | 340  (Mild claim)      | 199                                       | Moderate (at the mild / moderate boundary) |
| 0.6        | 130  (Moderate claim)  | 150                                       | Moderate (matches band)                   |
| 0.9        | 50   (Severe claim)    | 119                                       | Moderate (well inside the moderate band) |

Only the 0.6 → moderate mapping holds. The documented mild fraction
(0.3) lands at the mild / moderate boundary rather than the
mild-band centre, and the documented severe fraction (0.9) sits
19 mmHg above the severe-band ceiling — i.e. still
moderate by Berlin.

**Corrected mapping used by the Atlas.** From that same 28-run sweep, the
fractions that produce P/F values at the Berlin band centres
(or, for severe, immediately below the band ceiling) at the same
reference ventilation settings are:

| Berlin band               | Atlas `Severity` | Measured P/F (mmHg) | Position in Berlin band            |
|---------------------------|------------------|---------------------|------------------------------------|
| Mild  (200 < P/F ≤ 300)   | **0.26**         | 256                 | Centre of mild band                |
| Moderate (100 < P/F ≤ 200)| **0.60**         | 150                 | Centre of moderate band            |
| Severe (P/F ≤ 100)        | **0.95**         | 96                  | Just inside the severe band ceiling |

**Ventilation-setting dependence.** This calibration is anchored
to the reference ventilation setting above. Pulse's
documented mapping may reproduce its claimed P/F values under
different combinations of Vt, PEEP, and FiO2 — we have not tested
that. The Atlas's reliability sweep is preregistered to vary all
seven operational inputs around that reference setting, so the
calibration applies precisely to the regime the Atlas characterises.
Reliability of the documented mapping at other ventilation regimes
is out of scope.

**Solver instability zone.** Three convergent sweeps within the
companion `pulse_translation_new` project (same engine version,
same surrogate, same researcher, but with non-overlapping
impairment-fraction grids and independent run-by-run execution)
characterise the same numerical-bifurcation range in the
respiratory solver:

* **The original ARDS severity calibration** (the 28-run impairment
  sweep above, 2026-03): fractions 0.92
  and 0.94 fail to stabilise at the reference ventilation setting.
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
the reference ventilation setting. The Atlas's calibrated severe
fraction (0.95) was selected to clear the upper edge of the zone
with a 0.005 margin. Pulse's documentation [@pulserespmethod] does
not flag this zone.

**No surfactant model — multi-criteria audit (2026-06-11).** A direct
re-verification confirms Pulse models no pulmonary surfactant under any
name. A case-insensitive search of the complete engine tree — 3,304
files, 23 MB of them text, *including git-ignored and hidden files*, at tag
`REL_4_3_2` (commit `e8a3649`) — returns zero occurrences of
`surfactant`. Because such a model could hide behind other vocabulary,
the search was widened to the terms it would necessarily surface under;
every one returns zero: `surface tension`, `surface-tension`, `Laplace`,
`derecruitment`, `alveolar stability`, `opening`/`closing pressure`.
Terms that *do* appear — `recruit` (86), `collapse` (154),
`atelectasis` (2), `hysteresis` (3) — were each inspected and trace to
mechanical lung collapse (pneumothorax/hemothorax) or to phenomenological
compliance behaviour, not to a surface-tension submodel. The null result
holds beyond the source: the Kitware Pulse Discourse forum returns no
topic mentioning surfactant or alveolar surface tension, and the public
Respiratory Methodology and Mechanical-Ventilator-Recruitment pages
contain no such term. The audit ran on the `REL_4_3_2` checkout but
applies identically to the atlas's 4.3.1 pin: `git diff REL_4_3_1
REL_4_3_2` touches no respiratory or CDM source file (total delta seven
build-system files, +46/−17).

What Pulse reproduces instead are the *macroscopic* phenomena surfactant
governs, implemented phenomenologically rather than mechanistically.
(i) Pressure–volume hysteresis: the model "mimics the expected
hysteresis of the P–V curve" of the healthy lung, validated in Pulse's
own documentation [@pulserespmethod] against textbook physiology — but
as an emergent property of the dynamic compliance/driver-pressure cycle,
with no dedicated hysteresis routine. (ii) Alveolar recruitment: an
empirical mapping from acinar volume (the recruited fraction below FRC)
to a pulmonary-shunt scaling factor, calibrated to PEEP-response data
[@pulserespmethod], in `RespiratoryModel::UpdatePulmonaryShunt()`
(`RespiratoryModel.cpp:4388`, piecewise-linear interpolation at `:4503`),
combined by a `MIN` with the ARDS damage term — not governed by
surfactant-dependent alveolar stability. (iii) Alveolar compliance: a
lumped circuit element scaled by per-disease multipliers in
`RespiratoryModel::UpdateAlveolarCompliances()`
(`RespiratoryModel.cpp:3774`), with no surface-tension dependence. The
consequence is a missing-physics (not a calibration) gap: neonatal
respiratory distress syndrome — fundamentally a surfactant-deficiency
disease, including its response to surfactant instillation — is not
representable, one substantive reason the native pediatric-engine work
treats surfactant as a module to add rather than to retune.

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
  values at `Agemos` = 216.5 — 67.28992603 kg for boys, 56.22969564 kg for
  girls (CDC z-score file `wtage.csv`,
  <https://www.cdc.gov/growthcharts/data/zscore/>, re-read 2026-08-20 with
  columns resolved by name). CDC lists age at the half-month point standing
  for the whole month, so this row denotes 216.0–216.99 months, beginning at
  exactly 18.0 years. An earlier version of this entry placed the values at a
  214-month row and gave 67.64 and 56.41 kg as the 18.0-year figures; those
  belong to `Agemos` = 218.5, that is 18 y 2 m. These anchors were
  taken directly from the companion `Pulse_translation_new`
  pediatric-translation pipeline, where they form the adult (18 yr)
  endpoint of the CDC progression used for its pediatric strata
  (1 mo / 6 mo / 18 mo / 5 yr / 10 yr / 18 yr). The audit trail is
  recorded in that project's experiments log (CDC weight audit step,
  2026-04).

* **Female height (163 cm).** Matches the CDC P50 stature for
  18-year-old girls. By coincidence it is also identical to Pulse's
  own internal `heightStandardFemale_cm = 163.0` constant
  (`SetupPatient.cpp` L75; cited internally to Centers2016clinical).
  Both anchors therefore agree on this value.

* **Male height (180 cm).** This is a researcher-fixed rounded value
  chosen by the maintainer of `Pulse_translation_new` to yield a clean
  healthy baseline BMI of 20.8 in combination with the 67.3 kg weight.
  It is **not** the CDC P50 male stature at 18 years (CDC P50 ≈ 176.2
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

## Appendix C — `not_steady_state` attribution side-table ([S022](#s022)) {#appendix-c}

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
* **Vt CV > 5 %.** The F-004 tidal-volume oscillation, consistent with
  patient-ventilator dyssynchrony, described in §3.8 and causally tested in [S014](#s014). Pulse's
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
  Concentrated in S1/S2 (71 / 76 of those runs; 30 in S1_F, 16 in
  S1_M, 16 in S2_F, 9 in S2_M, plus 5 trickle in S3). Zero in S4 (in
  severe ARDS, SpO2 no longer saturates and this trigger never fires).
  This is the only *detector* edge case identified by [S022](#s022);
  it is not a Pulse limitation, it is a classification limitation of
  the locked flatline rule on healthy oxygenation. A downstream
  researcher who wants to score "engine instability" rather than
  "detector edge case + engine instability" can re-tally clean runs
  excluding this sub-mode using this table.
* **F-004 oscillation contribution (locked − excl. F-004 = 170 runs).**
  Distributed across all cells, with the strongest contribution at
  high set RR (consistent with the S014 mechanism: more assist-breath
  insertions per minute). This sub-mode is a *finding*, not a
  detector edge case — it reflects the documented Pulse-4.3.1
  patient-ventilator-trigger default behaviour, and the locked
  classifier is correctly flagging it.
* **Residual (excl. both = 185 runs).** Largest in S4 (91 / 185 of
  the residual), and a smaller S1 contribution (53 / 185). The S4
  residual is the F-003-class slow-convergence phenomenon
  ([S012](#s012), [S021](#s021)): severe-ARDS oxygenation has not
  settled within the locked 120 s window. The S1 residual is the
  F-003 transient hyperoxia regime (PaO2 drift at FiO2 = 1.0). Both
  categories are already discussed in §3.8 and are not new findings.
* **Counterfactual "clean" recount.** Under the joint exclusion
  (treat SpO2 saturation as physiological *and* re-attribute the F-004
  oscillation to its own documented finding), the clean count would
  rise from 663 / 1,280 (51.8 %) to 1,008 / 1,280 (78.8 %). This
  number is *not* a re-classification of the atlas — it is a
  decomposition of where the 51.8 % clean rate comes from. The
  headline locked-classifier numbers in §3.1 Table 1 stand.
