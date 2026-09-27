# Pulse 4.3.1 — Verified Limitations (as of 2026-04-19, GitLab re-audit 2026-05-07)

Every claim here is traceable. Use this list when writing the preprint, preparing the demo, or designing experiments. Do NOT add items without re-verifying against a primary source or a logged experiment.

> **Version-pin status (S016, 2026-05-07).** Pulse `REL_4_3_2` (2025-08-12) is on the public `stable` branch but its full diff vs `REL_4_3_1` is **7 files / +46 −17 lines, all build-system** (CMake, dockcross, web-WASM, .NET binding). No physiology, validation, patient-setup, or solver code changed. Our atlas's `pulse-pediatric-engine:latest` (built from 4.3.1) and `kitware/pulse:4.3.1` remain the correct evaluation targets — re-running on 4.3.2 would yield numerically identical results. Re-confirm before paper submission.

---

## 1. No formal sensitivity analysis / uncertainty quantification on operational inputs

**Verbatim from the [Pulse FAQ](https://pulse.kitware.com/_f_a_q.html) (verified 2026-04-19, still current 2026-05-07):**

> We have not performed a systematic forward propagation or inverse quantification of model uncertainty, nor have we conducted a formal sensitivity analysis. We plan to begin this type of analysis in the near future.

**Version history check.** v3.0.0 listed a sensitivity/correlation framework as a "planned improvement." v4.2.0 did not deliver it. v4.3.0 added "initial architecture for automated validation" — regression-testing templates, not uncertainty quantification. v4.3.1 (Sept 2024) and v4.3.2 (Aug 2025) still ship with no formal SA or UQ pipeline.

**Important nuance from the GitLab re-audit (S016, 2026-05-07).** The Pulse repo carries a tag `STUDY_SENSITIVITY_ANALYSIS_1_0_0` (2020-07-20), with code at `src/cpp/study/sensitivity_analysis/` (SARunner.cpp, ~56 KB) and `src/python/pulse/study/sensitivity_analysis/` (analysis.py, ml_surrogate.py, …). Its `ReadMe.md` states: *"This study uses sensitivity analysis as a path towards improved lumped parameter optimization."* It computes Sobol S1 / ST indices, directly or through an ML surrogate, over **internal lumped-parameter circuit values (cardiovascular and respiratory resistances and compliances)** (Aorta1ToBrain1, Aorta1ToFat1, Bone1ToBone2, AbdominalCavity1ToGround, …) — i.e. model-calibration parameters that override the engine's learned values during simulation. Its code is still in the 4.3.x source tree: 17 commits on the C++ folder between 2021-08 and 2024-08 are reachable from REL_4_3_1, mostly build maintenance, two of them touching the study's own code (2021-11; see the S016 note of 2026-09-27, which corrects the earlier "last functional commit 2020-08-24" and "not ported"). No published re-run on 4.3.x was found.

This means the literal FAQ statement is correct (no formal SA on the shipped engine), but the framing for our paper must be precise:

> Kitware released a one-off Sobol study in 2020 (`STUDY_SENSITIVITY_ANALYSIS_1_0_0`) on internal circuit-element values for parameter optimization. No systematic sensitivity analysis on **user-facing operational inputs** (HR, BP, RR, Vt, FiO2, PEEP) has been published, and the FAQ continues to state that no formal SA exists for the engine as currently shipped.

**This — operational-input SA, missing — is the core gap our atlas fills.** The 2020 study tag is complementary work on a different parameter class (internal calibration), not a substitute.

---

## 2. Blood pressure init rejection (loud, not silent)

- **SBP > 120 or DBP > 80** at patient setup is rejected **loudly** with an explicit `[ERROR]` log line and exit code 1 — *not* a silent substitution. Error message says "use a condition to model hypertension" but no hypertension condition exists in v4.3.1.
- **Pulse-pressure ratio DBP/SBP ≤ 0.75** is also enforced at init.
- *Earlier characterization of this gate as "silent" was overstated.* The atlas's H2 hypothesis (silent clamping ≥ 5 %) returned 0 / 1,280 runs (manuscript §3.4); rejection is observable from `pulse.log` alone with no special instrumentation. Update made 2026-05-08 from the deliberate-clamp probes in S005 and the H2 null result.

**Evidence:** Pulse_translation_new experiments E10 (100 Docker runs mapping all input boundaries) + source audit 2026-04-07.

**Available conditions in v4.3.1:** ARDS, ChronicAnemia, COPD, ChronicVentricularSystolicDysfunction, ChronicPericardialEffusion, ChronicRenalStenosis, ImpairedAlveolarExchange, Pneumonia, PulmonaryFibrosis, PulmonaryShunt, Sepsis, Dehydration. **No hypertension.**

---

## 3. Adult-only hard age gate

`src/cpp/engine/human_adult/whole_body/controller/SetupPatient.cpp` lines 41–64 explicitly reject `age < 18`:

```cpp
double ageMin_yr = 18.0;
if (age_yr < ageMin_yr) {
  ss << "Patient age of " << age_yr << " years is too young. "
     << "We do not model pediatrics. Minimum age allowed is "
     << ageMin_yr << " years.";
```

**Evidence:** direct C++ source audit 2026-04-07 (cloned `gitlab.kitware.com/physiology/engine.git`).

---

## 4. HR init acceptance: 50–110 bpm only

**Evidence:** Pulse_translation_new experiment E29. 11 Docker runs, 11/11 matched expectations. HR 45/48/49 rejected; 50–110 accepted; 111/115 rejected.

---

## 5. RR init acceptance: 8–20 bpm only

**Evidence:** Pulse_translation_new experiment E28. 9 Docker runs. RR 5,7 rejected; 8–20 accepted; 21,25 rejected.

---

## 6. ARDS solver instability zone: 0.91–0.945

ARDS severity multiplier in this range causes solver divergence. Calibrated severity values: **mild = 0.26, moderate = 0.60, severe = 0.95** (severe has only 0.005 margin above instability — use with care).

**Evidence (three independent sources):**
- E6 (32 Docker runs, refined calibration)
- E10 (10 runs, cross-check)
- Original Pulse calibration (28 runs)

---

## 7. PC-AC over-delivers tidal volume 24–59%

PC-AC mode significantly over-delivers Vt versus VC-AC. Pulse's own validation reports 11–25% error in PC-AC Vt; our probing pushed to 24–59% at wider configurations.

**Evidence:** Pulse_translation_new experiment (see Pulse translation experiments_log.md) + Webb et al. 2023, PMC10224749, concordant.

**Operational consequence:** use **VC-AC** (Vt error 0.07–2.25% across healthy/restrictive/obstructive) for any analysis where delivered Vt matters.

---

## 8. Upper airway simplified to single trachea resistance

No separate nose/pharynx compartments. The entire upper airway is one resistor. Runtime scaling available via `UpperInspiratoryResistanceMultiplier` and `UpperExpiratoryResistanceMultiplier` APIs — can approximate stridor, laryngospasm, post-extubation edema, but cannot model dead-space partitioning or heat/humidity exchange.

**Evidence:** source audit 2026-04-07.

---

## 9. No regional V/Q mismatch

Inherent to the lumped-parameter architecture (5-compartment respiratory circuit: carina, left/right anatomic dead space, left/right alveoli). Cannot model regional ventilation-perfusion heterogeneity. Matters especially in severe ARDS.

**Source:** Pulse design documentation; Bray et al. 2019 (DOI [10.1007/s42399-019-00053-w](https://doi.org/10.1007/s42399-019-00053-w)).

---

## 10. Vital capacity +7% vs literature

Pulse's own validation shows VC = 4.93 L vs ~4.6 L literature, attributed to weight-based scaling methodology. Not a blocker for ventilated scenarios but a known offset.

**Source:** Pulse documentation validation table.

---

## 11. Lumped-parameter physical simplifications

- **No airway inertance** — unsuitable for high-frequency ventilation (>40 Hz). Not relevant to VC-AC.
- **Linear resistance** — airway resistance independent of flow rate at normal conditions.
- **Idealized one-way valves** — no retrograde flow, no regurgitation modeling.
- **Linear compliance** — constant-compliance equations, not viscoelastic.

**Source:** Pulse documentation + Bray 2019.

---

## 12. Cardiovascular waveform simplifications

- **No dicrotic notch** — ideal valve model.
- **ECG P/T wave merge at high HR** — P and T waves less distinct than real ECG data.
- **Right heart diastolic pressure** falls ~10% below physiological due to zero unstressed volume assumption.
- **Aorta volume** substantially below literature due to compliance tuning trade-off.

**Source:** Pulse documentation validation; Bray 2019.

---

## Validation quality baseline (for context)

From Pulse's official validation (male patient, 474 scenarios):
- Good (<10% deviation): 397 scenarios (83.7%)
- Fair (10–30% deviation): 51 scenarios (10.8%)
- Poor (>30% deviation): 26 scenarios (5.5%)

VC-AC is Pulse's strongest ventilation mode (Vt error 0.07–2.25%). This is the mode PulseProbe uses.

---

## Withdrawn claims — do NOT cite these as limitations

- **FiO2 crash at 1.0** — disproved by Pulse_translation_new experiment E20 (Apr 2026). Pulse accepts FiO2 = 1.0 fine. Previous precautionary cap of 0.95 was unnecessary.
- **"No sex-specific physiology beyond weight/height"** — unverified. Pulse has sex-specific hemoglobin and body composition handling. Do not assert this until source-checked.

---

## Sources

- Pulse FAQ — https://pulse.kitware.com/_f_a_q.html
- Pulse Version History — https://pulse.kitware.com/version.html
- Pulse 4.3 Release — https://www.kitware.com/pulse-4-3-release/
- Bray et al. 2019 — https://doi.org/10.1007/s42399-019-00053-w
- Webb et al. 2023 (ventilator validation) — https://pmc.ncbi.nlm.nih.gov/articles/PMC10224749/
- Pulse_translation_new experiments_log.md (E6, E10, E20, E28, E29)
- Pulse GitLab source — https://gitlab.kitware.com/physiology/engine
- `STUDY_SENSITIVITY_ANALYSIS_1_0_0` tag (2020-07-20) — `src/cpp/study/sensitivity_analysis/` and `src/python/pulse/study/sensitivity_analysis/` (S016 audit, 2026-05-07)
- Pulse `REL_4_3_2` tag (2025-08-12) — diffed vs `REL_4_3_1`, build-system only (S016 audit)
