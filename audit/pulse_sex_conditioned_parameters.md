# Sex-conditioned parameters in Pulse v4.3.1 — active-configuration inventory

**Purpose.** An auditable inventory answering one question: *in the configuration
actually executed by the atlas sweep and by S011, which quantities are
conditioned on the patient sex flag — directly or indirectly — and does that
conditioning survive as far as a physiologically used quantity?* Opened
2026-08-15.

**Why a register rather than a grep pass.** Because three successive grep passes
in one session produced three different, each-time-plausible inventories: 3
parameters, then 9, then 30+. Each widening was triggered by chance, not by
method. A register records which surfaces were swept, with which instrument, and
why the sweep is (or is not) closed — so the next reader can re-check the
*completeness*, not just the result.

> ⚠️ **Do not use the parameter count from this register as a manuscript claim
> unless the inventory is revalidated against the referenced Pulse revision and
> configuration.** The manuscript claim must rest on the structural statement
> (sex switches many parameters across several subsystems), never on a counter.

---

## Completeness condition — **NOT SATISFIED** (2026-08-15)

The register closes only when all five sweeps below have been run *independently*
and every surviving item is classified as active / overwritten / inactive /
out-of-scope.

| # | Sweep | Status |
|---|---|---|
| 1 | Syntactic: enum, `Male`, `Female`, ternaries, **and derived intermediate variables** | **partial** — engine `src/cpp/engine/` + `src/cpp/cdm/` done; `bool male` propagation done for `SetupCircuitsAndCompartments.cpp` only |
| 2 | Semantic propagation of derived quantities (IBW, BMR/TMR, Hb/Hct, cardiac output, tissue masses, regional flows, dead space) | **partial** — IBW and BMR traced; Hb, CO, tissue masses, regional flows **not** traced to consumers |
| 3 | Non-code sources (data files, protobuf defaults, serialized defaults, config) | **not started** |
| 4 | Condition-application path (ARDS — 6 of our 8 cells) | **not started** |
| 5 | Equipment path actually used by the atlas (VC-AC mechanical ventilator) | **not started** |
| ⊥ | Transversal: for every retained quantity, setup-time vs runtime | **partial** — done for BMR only |

**Scope.** Pulse v4.3.1 (`pulse-atlas-engine`, image identical for the 1,280-run
sweep and for S011). Atlas configuration: `src/scenario.py` supplies age, weight,
height, sex, HR, RR, SBP, DBP + ventilator settings only. It never supplies
`IdealBodyWeight`, `BodyFatFraction`, `BasalMetabolicRate`, or any engine
configuration override (verified: no match for those names in `src/`).

**Exhaustiveness claimed here is bounded**: "exhaustive for this pattern, in this
file, for this revision and configuration" — never "exhaustive in Pulse".

---

## Method rules (fixed before the inventory)

1. **Never stop at the first surface that answers the question.** Every partial
   result must trigger a search for alternative surfaces: other files,
   intermediate variables, external data/config.
2. **Separate discovery from exhaustiveness.** Closing `male ? `, `male?`,
   `!male` and bare `male` inside one file proves exhaustiveness *for that
   pattern in that file*. It proves nothing about the engine.
3. **The closure condition is convergence of methods, not a final number.**

### Negative calibration — the false stops that produced plausible wrong answers

Kept deliberately: these document *which partial instruments yield a
complete-looking inventory*.

| # | Instrument used | Inventory obtained | What it missed |
|---|---|---|---|
| 1 | `ePatient_Sex::Female` in `SetupPatient.cpp` | **3** active branches | everything outside one file |
| 2 | + `ePatient_Sex::Male`, engine-wide | **9** sites | the derived `bool male` variable |
| 3 | + `male ? :` derived-variable propagation | **30+** introduction sites | **the propagation class entirely** (a quantity with no branch of its own can still be sex-conditioned), plus sweeps 3, 4, 5 |

**Five** self-corrections in the same session, all the same failure mode —
concluding from a partial read: (a) `SetupPatient.cpp` only; (b) `::Female` only;
(c) reading Supplement §S12-independent and missing §S12-scope; (d) asserting all
four BMR consumers propagate sex conditioning when three cancel it; (e) writing
into *this register* that nine regional-flow lines were sex-neutral, when all of
them inherit the sex-conditioned cardiac output (§B).

(e) is the most instructive: it was committed to the register **minutes after**
the trap taxonomy below was written, and it is precisely the case that taxonomy
describes. Knowing a trap by name does not stop you falling into it; only
re-deriving each claim against the source does.

### The three structural traps this inventory must not fall into

| Trap | Produces | Proof case |
|---|---|---|
| **Overwrite** — a sex-conditioned value is overwritten later, but by *another* sex-conditioned quantity | false **negative** | `AdiposeTissueMass` (§B) |
| **Propagation** — a quantity carries **no sex branch of its own** yet inherits the dependence from a factor upstream | false **negative** | every `VascularFlowTarget*`, via `cardiacOutputTarget` (§B) |
| **Cancellation** — a consumer reads a sex-conditioned quantity but its arithmetic eliminates the dependence | false **positive** | BMR ratio consumers (§D) |

A "who reads what" inventory would have produced **three false positives out of
four** on the BMR alone. A "who has a `male ?` branch" inventory misses the whole
propagation class — which is how self-correction (e) happened.

---

## Schema

| Column | Meaning |
|---|---|
| Source | `file:line` where the sex dependence is introduced |
| M / F | value or formula per sex |
| Phase | setup-time / runtime / both |
| Overwrite chain | what later overwrites or transforms it |
| Sex-dep after overwrite | `survives` / `removed` / `conditional` / `unknown` |
| Consumer | first physiologically meaningful consumer reached |
| Consumer arithmetic | how the consumer combines it (absolute / ratio / gated branch) |
| **Effective sex-dep in executed regime** | `YES` / `NO — algebraic cancellation` / `NO — branch not reached` / `CONDITIONAL` / `UNKNOWN` |
| Scenario dep. | does it differ across S1–S4? |
| Gas relevance | established / plausible / none / not assessed |
| Status | verified / open / excluded |

---

## A. `SetupPatient.cpp` — 4 sex branches (exhaustive for `ePatient_Sex::` in this file)

| Source | M / F | Active here? | Notes |
|---|---|---|---|
| L80–86 | height min/max/standard: M 163/190/177, F 151/175.5/163 cm | **not for value-setting** | only used to *set* height when absent; we always supply it. The bounds still **gate** — see §A.1 |
| L136–144 | IBW Devine: M `50.0 + 2.3(h_in−60)`, F `45.5 + …` → constant **−4.5 kg** for F at any height | YES | always recomputed; a supplied value is explicitly ignored (L132–133) |
| L217–223 | body-fat fraction standard **0.21 M / 0.28 F** (min/max also sex-specific) | YES | we never supply it → sex-specific standard used |
| L772–775 | BMR, Roza–Shizgal revised Harris–Benedict | YES | see §D and §E |

### A.1 The sex-specific height bounds warn — they do **not** clamp

`SetupPatient.cpp` L117–125: a height below `heightMin_cm` or above
`heightMax_cm` emits `patient.Warning(...)` — *"outside of typical ranges … No
guarantees of model validity"* — and **leaves the value unchanged**. Only the
sex-independent "outrageous" gate (4.5–7.0 ft = 137.2–213.4 cm) is a hard
`Error`. Source comment: *"From CDC values for 20 year olds. Mins are 3rd
percentile, Maxs are 97th percentile, and standard is 50th percentile."*

Two consequences, both verified on run logs rather than inferred:

- **The atlas sweep is untouched.** M 180 cm ∈ [163, 190]; F 163 cm ∈ [151,
  175.5]. Full scan of **0 / 3,340** atlas `pulse.log` files carry the warning,
  with S011 as positive control returning 2 — so the zero is a real zero, not a
  broken search.
- **S011's 67.3-kg arm is affected.** Its synthetic female is at 180 cm, i.e.
  4.5 cm above `heightMaxFemale_cm`. `SVM_S1_F_67.3kg/pulse.log:60` and the S4
  counterpart carry the warning; the other six cells are clean. So
  `sex_effect_at_67.3` (PaCO₂ −7.21, PaO₂ +21.3 mmHg) is measured with one body
  Pulse itself declares outside its typical range, whereas
  `sex_effect_at_56.2` (−2.60, +13.7 mmHg) is entirely in-envelope.

**Neither arm is percentile-matched**, and this is structural rather than a flaw
in S011: `heightMinMale_cm = 163.0` and `heightStandardFemale_cm = 163.0` are the
same number, so the 56.2-kg contrast compares a male at his **3rd percentile**
with a female at her **50th**. Holding mass and height fixed across sexes cannot
also keep both bodies at the centre of their own reference distribution, because
those distributions differ.

## B. `SetupCircuitsAndCompartments.cpp` — 27 `male ? :` parameters

Exhaustive **for this pattern in this file**: `male ? ` = 27 lines = 27
occurrences (no line carries two); `male?` = 0; `!male` = 0; 30 lines contain the
word `male` = 27 ternaries + 3 `bool male` declarations (L286, L1323, L2110). No
inline `ePatient_Sex::` ternary in this file.

| Source | Parameter | M / F |
|---|---|---|
| L293 | cardiac output target | 5600 / 4900 mL·min⁻¹ |
| L314–330 | **7** regional vascular flow fractions | Fat .05/.085 · Kidney .085/.075 · LargeIntestine .04/.05 · Muscle .17/.12 · Myocardium .04/.05 · SmallIntestine .1/.11 · Liver .255/.27 |
| L363, L370 | volume fractions | Fat .05/.085 · Muscle .14/.105 |
| L1338 | renal artery resistance factor | .025 / .055 |
| L2153–2165 | **13** tissue masses | Adipose 14.5/19.0 · Bone 10.5/7.8 · Brain 1.45/1.3 · Gut 1.02/.96 · R/L Kidney .155/.1375 · Liver 1.8/1.4 · **R/L Lung 0.5/0.42 × lung ratio** · Muscle 29.0/17.5 · Myocardium .33/.25 · Skin 3.3/2.3 · Spleen .15/.13 |
| L2174–2175 | standard-patient reference body (skin scaling) | 170/130 lb · 71/64 in |
| L2182 | standard fat fraction (**third copy** of 0.21/0.28) | 0.21 / 0.28 |

### ⚠️ The ternary count is a **lower bound**, not the inventory

L293–294: `cardiacOutputTarget_mL_Per_min = male ? 5600.0 : 4900.0`, then
`cardiacOutputTarget_mL_Per_s = …_min / 60`. **Every** `VascularFlowTarget*` in
this function is a fraction of that value — Aorta, Arm, Bone, Brain, Leg, Skin,
Splanchnic, Spleen and the pulmonary targets included, none of which carries a
`male ?`. They are therefore **all sex-conditioned by propagation**. The 7
ternary flows carry a *second*, independent sex conditioning on their fraction,
on top of the sex-conditioned total.

`VascularFlowTargetPortalVein` (L329) is a third case: no ternary of its own, but
it sums `LargeIntestine` (L316, ternary) + `SmallIntestine` (L326, ternary) +
`Splanchnic` + `Spleen`, so it inherits sex conditioning twice over.

*Recorded as self-correction (e) above: an earlier version of this register stated
"L317, L320–325, L327–329 are not sex-conditioned". That was flatly wrong, and it
was written minutes after the trap taxonomy above, which describes exactly this
case. Counting sex branches counts **introduction sites**, never the set of
sex-conditioned quantities.*

**Indirect, same file:** L2979 `anatomicDeadSpaceVolume_L = 0.002 × IdealBodyWeight_kg`
(`\cite Levitzky2013pulmonary`). No sex branch here; sex enters **via IBW**. F is
−4.5 kg IBW → −9 mL dead space at any height.

### Overwrite trap — worked example

`AdiposeTissueMass` is set at **L2153** (`male ? 14.5 : 19.0`), never read before
**L2170**, then **unconditionally** overwritten by
`BodyFatFraction × Weight`. The L2153 constant is therefore dead — *but*
`BodyFatFraction` is itself sex-conditioned (0.21/0.28), so at 67.3 kg the
overwrite yields 14.13 (M) / 18.84 (F) against the hard-coded 14.5/19.0.

→ **Sex-dep after overwrite: `survives`, source changed.** `overwritten = yes`
must never be read as `sex dependence removed`.

## C. Other engine sites

| Source | Parameter | M / F | Status |
|---|---|---|---|
| `SubstanceManager.cpp:336` | **haemoglobin** → haematocrit (`Hb/34`) | **15.0 / 14.0 g·dL⁻¹** | verified; consumers **not yet traced** |
| `CardiovascularModel.cpp:314` | cardiac output initialisation | 5600 / 4900 mL·min⁻¹ | verified; consumers **not yet traced** |

## D. BMR consumers — the cancellation calibration witnesses

`EnergyModel.cpp:104` initialises `TotalMetabolicRate = BasalMetabolicRate`, so at
rest **TMR == BMR** and any `TMR/BMR` ratio equals exactly 1.0 — two identically
sex-conditioned quantities cancel on division.

| Consumer | Arithmetic | Effective sex-dep (our regime) |
|---|---|---|
| `TissueModel.cpp:721` `CalculateMetabolicConsumptionAndProduction` | `ATPUseRate = TMR / EnergyPerATP` — **absolute** | **YES** |
| `RespiratoryModel.cpp:4893` `UpdateTargetVentilation` | `1.0 + 0.2·(TMR/BMR − 1.0)` → 1.0 | **NO — algebraic cancellation** |
| `CardiovascularModel.cpp:2558` `MetabolicToneResponse` | ratio, then `if (metabolicFraction == 1.0) return;` | **NO — branch not reached** |
| `EndocrineModel.cpp:157` `ReleaseEpinephrineAndNorepinephrine` | `if (currentMetabolicRate_W > basalMetabolicRate_W)` | **NO — branch not reached** |

**One of four** propagates sex conditioning to physiology at rest.

### TMR write sites (why TMR stays equal to BMR here)

| Site | Gate | Reached? |
|---|---|---|
| `EnergyModel.cpp:104` | none (Initialize) | yes → TMR = BMR |
| `EnergyModel.cpp:468` | `HasExercise()`; set-point is `BMR + workRate` (**additive** — the one form that would *not* cancel) | **no** — no exercise action in any atlas or S011 run |
| `EnergyModel.cpp:615, 623, 630, 635` | core temperature < 36.8 °C (hypothermia / shivering) | **presumed no** — core temperature initialised at 37.0 °C, **not verified on artefact** |
| `EnergyModel.cpp:228` | — | commented out |

## E. Excluded — with reason

| Item | Reason |
|---|---|
| `SetupExpandedCardiovascular.cpp` L30, 1859, 2677, 2703, 2723 (5 branches) | **inactive**: gated by `UseExpandedVasculature() == eSwitch::On`; default `m_UseExpandedVasculature = eSwitch::NullSwitch` (`PulseConfiguration.cpp:68`), never set by the atlas |
| `SetupExpandedCardiovascular.cpp:2716` | commented out |
| `EnergyModel.cpp:751` (duplicate BMR equations) | **dead code** — sole call site commented out at `EnergyModel.cpp:227` |
| `SetupPatient.cpp` L80–86 height bounds | excluded **only** as a value-setter (we always supply height); **not excluded** as a gate — see §A.1 |
| `study/`, `howto/`, `test/` trees | not on the atlas execution path |

## F. Upstream Pulse observations (no scientific weight claimed)

1. **BMR male intercept.** Pulse uses `88.632`; Roza & Shizgal (1984) *Am J Clin
   Nutr* 40:168–182, **Equation 3, p. 171** (printed twice on that page), report **`88.362`**
   — confirmed by rendering the page image, not by OCR alone (the OCR of this PDF
   demonstrably confuses B and 8). The seven other coefficients match exactly. The
   transposition appears **twice**: `SetupPatient.cpp:771` (live) and
   `EnergyModel.cpp:752` (dead). Effect on the male reference body:
   +0.27 kcal·day⁻¹, **0.015 %**. Immaterial to every comparison here.
   *Never transcribe Pulse's equation and attribute it as-is to Roza & Shizgal.*
2. **Height warning prints the wrong bound.** The `else if (height_cm > heightMax_cm)`
   branch prints `heightMin_cm`. Observed in a real run log: *"above 97th
   percentile(151 cm)"* for a female body whose ceiling is 175.5 cm.
3. **Source-comment nuance.** The height percentiles are commented *"From CDC
   values for 20 year olds"*; the atlas bodies are 18. Upstream approximation,
   **impact not assessed**.
4. **What Roza & Shizgal themselves conclude.** *"Resting energy expenditure is
   directly related to the size of the BCM and is independent of age and sex. The
   variables of height, weight, age, and sex in the HBE reflect the relationship
   between body weight and the BCM."* The sex term is a body-composition proxy —
   so "Pulse models a sex-specific metabolism" would misdescribe the cited source.

## G. Open items

| # | Question | Status |
|---|---|---|
| G1 | Under S2/S3/S4, do the expressions consuming TMR and BMR **actually become sex-dependent**, given how TMR is modified and which branches are reached? A uniform multiplicative change (`TMR = k·BMR`) leaves the ratio sex-neutral; only a non-proportional increment reintroduces it. | **OPEN — not measured.** Neither TMR nor core temperature is recorded in the atlas CSVs (six channels: HR, MAP, Vt, SpO₂, PaO₂, PaCO₂), so this cannot be settled from existing artefacts |
| G2 | Consumers of haemoglobin / haematocrit — does the 15.0/14.0 difference reach PaO₂/SpO₂? | **OPEN — not traced** |
| G3 | Consumers of the sex-specific cardiac output and the 7 regional flow fractions — note `TissueModel` distributes metabolic consumption by **blood-flow fraction** | **OPEN — not traced** |
| G4 | Does the VC-AC mechanical ventilator path consume IBW (precedent: `BagValveMaskModel.cpp:549` does)? | **OPEN — not swept** |
| G5 | Does the ARDS condition-application path introduce or modify sex conditioning? | **OPEN — not swept** |
| G6 | Non-code sources | **OPEN — not swept** |

---

## What the manuscript may already say

Supported by §A–§E as they stand:

> Pulse uses sex as a setup switch for numerous physiological parameters spanning
> body composition, energy metabolism, oxygen-carrying capacity, cardiovascular
> initialization, regional perfusion, tissue properties, and — via ideal body
> weight — anatomic dead space. Consequently S011 isolates the combined effect of
> this sex-conditioned parameterization at fixed mass and height, not any
> individual physiological mechanism.

**Not** supported, and not to be written until this register closes: any statement
attributing the observed PaCO₂/PaO₂ contrast to BMR, haemoglobin, cardiac output
or any single pathway; any parameter count; any claim that a given pathway
*dominates*, which would require a dedicated ablation experiment.
