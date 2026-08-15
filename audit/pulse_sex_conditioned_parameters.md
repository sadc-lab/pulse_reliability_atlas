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
| 1 | Syntactic: enum, `Male`, `Female`, ternaries, **and derived intermediate variables** | **closed** — engine + cdm swept; transitive closure done: all level-1 variables have traced consumers (§C.5) |
| 2 | Semantic propagation of derived quantities (IBW, BMR/TMR, Hb/Hct, cardiac output, tissue masses, regional flows, dead space) | **traced** — IBW, BMR, Hb (§C.1), cardiac output (§C.2), regional flows (§C.3), tissue masses per consumer (§C.4). One residual: metabolic distribution CONDITIONAL/UNKNOWN (§C.4) |
| 3 | Non-code sources (data files, protobuf defaults, serialized defaults, config) | **swept** — no state and no patient file loaded; proto3 default `Male=0` recorded (§H) |
| 4 | Condition-application path (ARDS — 6 of our 8 cells) | **swept** — multiplicative on sex-conditioned baselines; conditioning preserved (§H) |
| 5 | Equipment path actually used by the atlas (VC-AC mechanical ventilator) | **swept** — no direct branch; propagation confirmed (§H) |
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

**Six** self-corrections in the same session, all the same failure mode —
concluding from a partial read: (a) `SetupPatient.cpp` only; (b) `::Female` only;
(c) reading Supplement §S12-independent and missing §S12-scope; (d) asserting all
four BMR consumers propagate sex conditioning when three cancel it; (e) writing
into *this register* that nine regional-flow lines were sex-neutral, when all of
them inherit the sex-conditioned cardiac output (§B); (f) counting **105**
blood-gas compartments for our branch when the true figure is **38** — see below.

**(f) is a distinct instrument failure and deserves its own row.** The count came
from `grep -c "VascularCompartment::…"`, which **silently also matches
`ExpandedVascularCompartment::`** — a substring. So the number returned was the
sum of both branches (67 expanded + 38 standard = 105), i.e. it counted 67 calls
on a code path the atlas never executes. The line number was wrong in the same
pass: L354 is the `if`, the `else` is at L448.

> **Rule added:** when a count is used to characterise *one* branch, anchor the
> pattern so it cannot match the other, and verify the partition explicitly
> (here: 0 standard calls before L448, 38 after, 67 expanded inside [354, 448)).
> A substring match between two enum names is invisible in the output — the
> result looks like a clean number.

(e) is the most instructive: it was committed to the register **minutes after**
the trap taxonomy below was written, and it is precisely the case that taxonomy
describes. Knowing a trap by name does not stop you falling into it; only
re-deriving each claim against the source does.

### The four structural traps this inventory must not fall into

| Trap | Produces | Proof case |
|---|---|---|
| **Overwrite** — a sex-conditioned value is overwritten later, but by *another* sex-conditioned quantity | false **negative** | `AdiposeTissueMass` (§B) |
| **Propagation** — a quantity carries **no sex branch of its own** yet inherits the dependence from a factor upstream | false **negative** | every `VascularFlowTarget*`, via `cardiacOutputTarget` (§B) |
| **Cancellation** — a consumer reads a sex-conditioned quantity but its arithmetic eliminates the dependence | false **positive** | BMR ratio consumers (§D) |
| **Same literal, two fates** — one value appears at several loci with different lifetimes; merging them inherits whichever verdict was found first | **either** | cardiac output 5600/4900 (§C.2) |

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
| L2174–2175 | standard-patient reference body — feeds **both** `typicalSkinSurfaceArea` (L2177, uses both values) **and** `standardLeanBodyMass` (L2184, the normalisation in §B.1) | 170/130 lb · 71/64 in |
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

### B.1 Compound conditioning — the lungs, and why one ternary tells you nothing

L2182–2197 apply a second, sex-conditioned normalisation on top of the L2153–2165
constants:

```
standardFatFraction        = male ? 0.21 : 0.28                    // L2182
standardPatientWeight_lb   = male ? 170.0 : 130                    // L2174
standardLeanBodyMass_kg    = standardPatientWeight_lb→kg × (1 − standardFatFraction)
patientLeanBodyMass_kg     = weight_kg × (1 − fatFraction)         // SetupPatient.cpp:252
leanBodyMassFractionOfTypical = patientLeanBodyMass / standardLeanBodyMass
```

The fat fraction is the *same* value in numerator and denominator for a given
sex, so it cancels and the factor reduces to `weight / standardWeight(sex)`.
**The sex dependence therefore survives entirely through the 170 vs 130 lb
reference body**: 77.11 vs 58.97 kg, so at *equal patient weight* the female
factor is **1.308×** the male one.

It multiplies ten tissue masses (L2188–2197): Bone, Gut, R/L Kidney, Liver,
**R/L Lung**, Muscle, Myocardium, Spleen. (Adipose is excluded — already
overwritten at L2170; Brain and Skin are scaled on other bases.)

**Worked case — lung tissue mass at an identical 67.3 kg body:**

| | ternary (L2160) | × LBM factor | net |
|---|---|---|---|
| M | 0.50 | × 0.873 | **0.436** × lung ratio |
| F | 0.42 | × 1.141 | **0.479** × lung ratio |

The female body ends up with **~9.8 % more** lung tissue mass at equal weight,
although its ternary constant is the *smaller* of the two. **The normalisation
reverses the direction the ternary suggests.** Downstream this sets lung tissue
volume (L2209–2210), compartment total mass (L2515, L2755) and the
vascular–tissue resistance baselines `(1/LungTissueMass) × resistanceConstant`
(L2490, L2730).

> This is the register's central cautionary case: reading a mechanism off a
> single `male ? a : b` would have produced a claim with the **wrong sign**.

**The sign depends on which contrast you make — and it inverts twice.** The
complete expression is `LungTissueMass = ternary(sex) × lungRatio ×
weight / standardWeight(sex)`, with nothing further modifying it after L2194
(L2209–2210 only consume it). `lungRatio` is **not** sex-conditioned
(`rightLungRatioStandard = 0.525`, single value, never supplied by us), so it
cancels from every comparison.

| contrast | male | female | F vs M |
|---|---|---|---|
| **equal weight** (S011 sex arm) | `0.50·W/77.11` | `0.42·W/58.97` | **+9.8 %**, and `W` cancels — *weight-independent* |
| **atlas native** (M 67.3 kg, F 56.2 kg) | `0.50 × 0.8728` = 0.4364 | `0.42 × 0.9531` = 0.4003 | **−8.3 %** |

So: local ternary says female **lower**; equal-weight net says female **higher**;
the atlas's own native bodies say female **lower** again. *"Females have more/less
lung tissue in Pulse"* is not a well-formed statement — only a contrast-specific
one is. Any §S10 sentence must name the contrast it refers to.

## C. Other engine sites

| Source | Parameter | M / F | Status |
|---|---|---|---|
| `SubstanceManager.cpp:336` | **haemoglobin** → haematocrit (`Hb/34`) | **15.0 / 14.0 g·dL⁻¹** (F −6.7 %) | **traced — see §C.1** |
| `CardiovascularModel.cpp:314` | cardiac output initialisation | 5600 / 4900 mL·min⁻¹ | **traced — see §C.2** |

### C.1 Haemoglobin — traced to its consumers. **Effective sex dependence: YES**

`SubstanceManager.cpp:336–351`. The single ternary feeds **two** downstream paths,
both active in our configuration and neither of them a ratio:

1. **Saturation calculator body state.** `hematocrit = Hb_total_g_Per_dL / 34.0`
   → **0.4412 (M) / 0.4118 (F)** → passed to
   `GetSaturationCalculator().SetBodyState(albumin, hematocrit, bodyTemp, SID,
   phosphate)` (L342). The saturation calculator is what resolves O₂/CO₂ carriage,
   so this enters oxygen-carrying capacity directly.
2. **Initial blood gases of every compartment.**
   `Hb_total_mM = Hb_total_g_Per_dL / molarMass × 10.0` (L351) is passed to
   `InitializeBloodGases(...)` for **38** compartments in the **standard**
   vasculature branch — the `else` at **L448**, which is ours. The expanded arm
   (`if` at L354, 67 compartments) is gated `UseExpandedVasculature == On` and is
   never enabled here (§E). Verified partition: 0 standard calls before L448, 38
   after; 67 expanded calls inside [354, 448).

| Column | Value |
|---|---|
| Phase | setup-time (initialisation of body state and compartment gases) |
| Overwrite chain | none found |
| Consumer arithmetic | **absolute** — division by the constant 34.0 and by molar mass; no sex-conditioned denominator, so **no cancellation** |
| **Effective sex-dep in executed regime** | **YES** |
| Gas relevance | **established** — haematocrit and Hb concentration are direct inputs to O₂ carriage, not a plausibility argument |

> This makes haemoglobin the most directly gas-relevant sex conditioning found so
> far — more direct than BMR, three of whose four runtime consumers cancel (§D).
> **That is a statement about mechanism availability, not about attribution.**
> Nothing here licenses saying that Hb explains S011's PaO₂/SpO₂ contrast; that
> would still require an ablation.

### C.2 Cardiac output — the **same constant, two opposite verdicts**

`5600 / 4900 mL·min⁻¹` appears twice. The two occurrences do **not** have the same
fate, and treating them as one entry would be an error in either direction.

| # | Locus | Role | Verdict |
|---|---|---|---|
| 1 | `CardiovascularModel.cpp:314`, inside `Initialize()` | sets the `CardiacOutput` **field** | **NO — overwritten** |
| 2 | `SetupCircuitsAndCompartments.cpp:293` | `cardiacOutputTarget`, which **sizes the circuit** (every `VascularFlowTarget*`, §B) | **YES — structural** |

**(1) is an initial condition with a lifetime of one heartbeat.**
`RecordAndResetCardiacCycle()` (L1338) recomputes, at the end of **every cardiac
cycle**, `CardiacOutput = StrokeVolume × HeartRate` (L1367). Stroke volume and
heart rate are both emergent from the circuit. The sex-conditioned constant is
therefore gone within roughly one beat — well under 1.2 s at HR 50 — while the
recorded window is the final 60 s of a 120 s run, after stabilisation. Nothing of
the initialised value reaches the data.

This is exactly the failure mode the maintainer flagged: *a sex-conditioned setup
constant is not automatically a persistent difference in the recorded window.* It
is the same class as `CardiovascularModel::AtSteadyState()` overwriting four
patient baseline fields with measured values, already documented in
[`patient_baseline_rebaselining.md`](patient_baseline_rebaselining.md).

**(2) persists, because it is not a value but a sizing input.** It sets the flow
targets from which the circuit's resistances are derived; those are structural
circuit parameters, not patient baseline fields, and the rebaselining register
records only HR / SBP / DBP / MAP as overwritten at steady state.

| Column | (1) `CardiovascularModel.cpp:314` | (2) `SetupCircuits…:293` |
|---|---|---|
| Phase | setup-time only | setup-time, structural |
| Overwrite chain | `RecordAndResetCardiacCycle()` L1367, every cycle | none found |
| Consumer arithmetic | value replaced outright | multiplied into flow targets |
| **Effective sex-dep** | **NO — overwritten before the recorded window** | **YES** |
| Gas relevance | none (never reaches the data) | plausible, **not established** |

> **A fourth trap, and it is not any of the previous three:** the *same literal*
> can be sex-conditioned and irrelevant at one locus while sex-conditioned and
> structural at another. An inventory keyed on values rather than on loci would
> merge these two rows and inherit whichever verdict it happened to find first.

### C.3 Regional flows — net absolute values, not fractions

Two layers stack: **every** target is a fraction of a sex-conditioned
`cardiacOutputTarget` (F 4900 vs M 5600 mL·min⁻¹, i.e. **F −12.5 %**), and seven
of them carry a sex-conditioned fraction on top. Reading the fractions alone is
therefore not enough — the net value is `fraction(sex) × CO(sex)`.

**Threshold:** a female fraction must exceed the male one by more than
`5600/4900 = +14.29 %` for the *absolute* flow to end up higher. Below that, a
higher female fraction still yields a lower female flow.

| Target | fraction M / F | fraction F vs M | **net flow F vs M** |
|---|---|---|---|
| Fat | .05 / .085 | +70 % | **+48.8 %** |
| Large intestine | .04 / .05 | +25 % | **+9.4 %** |
| Myocardium | .04 / .05 | +25 % | **+9.4 %** |
| Small intestine | .10 / .11 | **+10 %** | **−3.8 %** ⚠ inverts |
| Kidney | .085 / .075 | −11.8 % | **−22.8 %** |
| Muscle | .17 / .12 | −29.4 % | **−38.2 %** |
| *(all sex-neutral fractions)* | — | 0 | **−12.5 %** |

Two of the five fractions that are *higher* for the female body sit below the
14.29 % threshold and therefore invert — small intestine here, and the portal
vein below. **The maintainer predicted this case before it was computed.**

**Liver is a third case, and it needs the subtraction.** L330 is
`VascularFlowTargetLiver = (male ? 0.255·CO : 0.27·CO) − VascularFlowTargetPortalVein`,
and L329 `PortalVein = LargeIntestine + SmallIntestine + Splanchnic + Spleen`
(the last two sex-neutral at .01 and .03).

| | M | F | F vs M |
|---|---|---|---|
| Portal vein | .18 × 5600 = 1008 | .20 × 4900 = 980 | **−2.8 %** ⚠ inverts (fraction sum +11.1 %) |
| Liver, net of portal | 1428 − 1008 = **420** | 1323 − 980 = **343** | **−18.3 %** |

Taking the liver ternary at face value gives −7.4 %; carrying the subtraction
gives **−18.3 %**, two and a half times larger. A register that recorded
"liver .255/.27" and stopped would have been wrong in magnitude while looking
right.

> **Effective sex-dep: YES for all regional flows** — but the *sign and size* are
> a property of the net computation, never of the fraction. And this is a
> statement about **parameter perturbation only**: no consequence for PaO₂/PaCO₂
> is established here.

### C.4 Tissue masses — **one verdict per consumer**, not one per mass

Prerequisite verified: every `*TissueDensity` is a plain constant (**0** of them
contain `male`) and `resistanceConstant = 20000.0` is sex-neutral, so each
conversion below is a sex-neutral operation on a sex-conditioned input.

Five distinct consumers, and they do **not** agree on sign.

| # | Consumer | Locus | Form | Verdict |
|---|---|---|---|---|
| 1 | tissue **volume** | L2209–2210 | `mass / density` | preserved, **same sign** |
| 2 | compartment **total mass** | L2515, L2755 | direct assignment | preserved, same sign |
| 3 | vascular–tissue **resistance** | L2490, L2730 | `(1/mass) × 20000` | preserved, **SIGN INVERTED** |
| 4 | vascular→EC **permeability** | `TissueModel.cpp:507` | `coeff_per_g × mass` | preserved, same sign |
| 5 | **capillary coverage area** | `TissueModel.cpp:516` | `coeff_cm²_per_g × mass` | preserved, same sign |

**Worked case — the lung, four signed statements from one ternary:**

| contrast | mass & volume & permeability & cap. area | resistance |
|---|---|---|
| equal weight | **F +9.8 %** | **F −9.0 %** |
| atlas native (M 67.3, F 56.2 kg) | **F −8.3 %** | **F +9.0 %** |

`0.42 < 0.50` in the source. The net answer is +9.8 %, −8.3 %, −9.0 % or +9.0 %
depending on *which contrast* and *which consumer* — all four simultaneously true
and none contradicting another.

#### Two of my earlier statements were wrong and are corrected here

- **Tissue mass does *not* drive the metabolic distribution.** I had said it did.
  `TissueModel.cpp:888` uses `LocalATPUseRate = BloodFlowFraction × ATPUseRate ×
  vascularVolumeMultiplier`, and `BloodFlowFraction` (L863) is
  `vascular->GetInFlow() / totalFlowRate` — **measured runtime flow**, not tissue
  mass. Mass reaches physiology through consumers 1–5 above, not through the
  metabolic budget.
- **The §C.3 setup flow targets are not the runtime fraction either.**
  `BloodFlowFraction` is a **ratio of measured flows**, so the −12.5 % cardiac
  output scaling appears in numerator *and* denominator and **cancels**. What
  could survive is the *relative* distribution, and whether the setup-time target
  ratios reach runtime through the circuit is **not established**.

| Column | metabolic distribution |
|---|---|
| Consumer arithmetic | ratio of measured flows |
| **Effective sex-dep** | **CONDITIONAL / UNKNOWN — not measured.** CO scaling cancels; survival of the relative distribution to runtime is unverified |

### C.5 Transitive closure — the four remaining level-1 variables

Sweep 1 had closed the `bool male` propagation for the 27 ternaries but not for
every *variable assigned from* them. Four had untraced consumers. Both
denominators they meet are sex-neutral, verified: `computedBloodVolume_mL =
65.6 × weight^1.02` (`SetupPatient.cpp:534`, no sex term — this is the same
allometric relation the main paper §2.5 already reports as sex-independent) and
`arteryTuningMultiplier = 1.25` (L1336, plain constant).

| variable | consumer | net F vs M |
|---|---|---|
| `VolumeFractionFat` .05/.085 | L496 `Fat1.VolumeBaseline = f × bloodVolume` | equal weight **+70 %**; atlas native (BV 4 803 / 3 996 mL) **+41.4 %** |
| `VolumeFractionMuscle` .14/.105 | L525 `Muscle1.VolumeBaseline = f × bloodVolume` | equal weight **−25 %**; atlas native **−37.6 %** |
| `renalArteryResistanceFactor` .025/.055 | L1340 renal artery resistance | **×2.2 (+120 %)** — weight-independent, no blood-volume term |
| `typicalSkinSurfaceArea_m2` (from the 170/130 lb, 71/64 in reference body) | L2179 `SkinTissueMass ×= patientSkinArea / typicalSkinArea` | **structure recorded, value not computed** — see caution below |

**The renal artery resistance factor is the largest single sex ratio in this
register: 2.2×.** Larger than haemoglobin (1.07×), cardiac output (1.14×) or any
tissue mass. It is recorded here as a *parameter* ratio; no renal or gas-exchange
consequence is claimed, and the atlas records no renal output.

Skin is the one mass **not** scaled by `leanBodyMassFractionOfTypical`; it is
normalised by a surface-area ratio instead, whose denominator is the
sex-conditioned reference body.

> ⚠️ **Deliberately not computed.** The skin figure needs four fractional powers
> (`0.20247 · W^0.425 · H^0.725`, evaluated for both the patient and the
> sex-specific reference). This register has no second instrument available to
> check such a hand computation, and a single wrong digit would look entirely
> plausible. The *structure* is established and sufficient for §S10; the number
> is left open rather than published unverified.

**Other carrier files carry no untraced level-1 variable.** `SubstanceManager`
(`Hb_total_g_Per_dL` → `hematocrit`, `Hb_total_mM`, both traced in §C.1),
`CardiovascularModel` (direct setter, §C.2), `EnergyModel` (dead code, §E),
`SetupPatient` (IBW, fat fraction, BMR — all traced in §A, §B.1, §D).

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

## H. Sweeps 4 and 5 — results (2026-08-15)

### Sweep 5 — VC-AC mechanical ventilator: **no direct branch, propagation confirmed**

`MechanicalVentilatorModel.cpp` contains **no** `ePatient_Sex`, no `GetSex()` and
no `GetIdealBodyWeight` — the ventilator itself is sex-blind. (Contrast
`BagValveMaskModel.cpp:549`, which *does* read IBW; that equipment is not on the
atlas path.)

But it ventilates a respiratory circuit that is sex-conditioned throughout:
anatomic dead space `0.002 × IBW` (L2979) → physiologic dead space; and lung
tissue mass → tissue volume, compartment mass, and vascular–tissue resistance
(§B.1). **A sex-blind ventilator delivering a fixed Vt into a sex-conditioned
lung still produces sex-conditioned alveolar ventilation.** Textbook propagation
class; a grep-only sweep of the equipment tree would have returned "not
sex-dependent" and been wrong.

### Sweep 4 — ARDS condition path: **partial**

ARDS severity is consumed at **12+ sites** in `RespiratoryModel.cpp` (3045, 3709,
3884, 4036, 4206, 4461, …). `RespiratoryModel.cpp` itself contains **no**
`ePatient_Sex` and no `GetIdealBodyWeight`, so ARDS introduces no new sex branch.
At each site the severity is combined as
`restrictiveSeverity = MAX(restrictiveSeverity, severity)`, pooling ARDS with the
other restrictive conditions.

**Answer — conditioning is PRESERVED, not erased.** Every application read is
purely multiplicative on the value already in the circuit, with a factor that is
a function of `restrictiveSeverity` alone and carries no sex term:

| Locus | Arithmetic |
|---|---|
| L3736–3737 | reads `GetNextResistance()`, writes `resistance × resistanceScalingFactor` |
| L3904–3905 | reads `GetNextCompliance()`, then `*= positivePressure × obstructive × restrictive` factors |
| L3078–3079 | `deadSpaceIncrement` / `alveoliIncrement`, each scaled by `alveoliVolumeRatio` |
| L4683 | `restrictiveModifier = LinearInterpolator(0, 1, 0, 0.8, restrictiveSeverity)` |

The baselines being multiplied are the sex-conditioned circuit values of §B.1
(lung tissue mass → resistance baselines L2490/L2730; compliances from lung
volumes). Multiplying a sex-conditioned baseline by a sex-neutral factor leaves
the **relative** sex difference exactly intact.

**The lead is therefore closed, negatively.** The earlier hypothesis — "ARDS may
overwrite sex-conditioned baselines with absolute values, which would explain why
S011's gas-exchange sex effects shrink from S1 to S4" — is **not supported by the
code**. It is recorded here so it is not re-proposed.

**What is still not established:** anything about the S1→S4 pattern itself. The
recorded outputs depend on the full non-linear system, and multiplicative
preservation of a *parameter* ratio does not imply preservation of an *output*
difference. Nothing here explains S011's scenario dependence, and no such
inference may leave this register.

### Sweep 3 — non-code sources: **swept, one finding**

The premise of this sweep was that sex conditioning could arrive through a route
no C++ grep reaches. Four surfaces checked:

1. **Serialized state — none loaded.** `engine/run_atlas_engine.py:168` calls
   `pulse.initialize_engine(pc, data_mgr)`, never `serialize_from_file`. The only
   `json.load` in the wrapper (L288) reads *our* `config.json`. **`SetupPatient`
   therefore executes on every run**, so no pre-stabilised per-sex state can carry
   hidden conditioning — which was this sweep's largest risk.
2. **Patient files — none loaded.** The patient is built programmatically from
   our config. Pulse's shipped patient assets
   (`data/human/adult/baselines/scenarios/…`) are its own V&V material and are not
   on the atlas path. `data/config/PatientVerification.config` is a test-runner
   manifest, not physiology.
3. **Protobuf default — a real finding.** `Patient.proto` declares
   `syntax = "proto3"` and `enum eSex { Male=0; Female=1; }`, so an **unset** sex
   field deserialises to the zero value: **a patient with no sex specified is
   silently male**.

   The deserialiser makes this sharper than generic proto3 semantics would.
   `PBPatient.cpp:24` reads `dst.SetSex((ePatient_Sex)src.sex());` with **no
   presence check** — while the two lines immediately following it *do* check,
   `if (src.has_age())` and `if (src.has_weight())`. So within one function,
   an absent age or weight stays unset (and `SetupPatient` later fills it with an
   explicit `Info` log), whereas an absent sex is silently resolved to Male with
   no log at all.

   This never bites the atlas — `src/scenario.py:159` always sets it explicitly —
   but it is exactly the class of thing this sweep existed to find, and no amount
   of C++ branch-grepping would have surfaced it.
4. **Image build layer.** `engine/Dockerfile` adds only a pandas install, a patch
   to the Python SDK's mechanical-ventilator serialiser (an upstream field-name
   bug, not sex-related) and the wrapper. No physiology data is added or replaced.

> **Bounded limitation.** Surfaces 2 and 4 were verified against the Pulse **source
> tree** and the atlas Dockerfile, not by listing `/pulse/bin/` inside the running
> `kitware/pulse:4.3.1` image. The image's data root is used for substance,
> environment and nutrition definitions, none of which is sex-typed by nature, and
> the patient never comes from it — but *"verified in the source tree"* is the
> honest scope of this row, not *"verified in the image"*.

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
