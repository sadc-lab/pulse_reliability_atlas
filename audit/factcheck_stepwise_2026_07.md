# Step-wise fact-check of `paper.tex` and `supplement.tex` — opened 2026-07-29

**Point 2 of the three final pre-submission audits**, commissioned by the author
on 2026-07-29. Method imposed by the author: **decomposition** — one unit at a
time, in document order, because the last days carried many edits and
everything must be re-verified.

Companion registers: `audit/npj_format_compliance.md` (point 1, closed) and
`audit/reference_audit.md` § *Phase 4* (point 3, closed).

## What this pass adds that the machine audit cannot

`scripts/audit_claims.py --check-paper-sync --check-monograph` is green at
**289 / 289 anchors · 97 / 97 crosswalk rows · 26 / 26 monograph anchors,
exit 0** (re-run 2026-07-29 as the baseline for this pass). But it only
re-derives **anchored numeric literals**. It is blind to:

1. a value **restated in a different display form** in another unit — the
   crosswalk guards `0.928`, not `93~\%`;
2. an **arithmetic consequence** stated in prose — a difference, a ratio, a BMI;
3. a **constant read from source** — Pulse C++ or `src/detector.py`;
4. every **cross-reference**: whether `\ref{}` resolves, and whether the target
   actually contains what the sentence announces;
5. every **citation placement**: whether the cited work supports *that* claim at
   *that* locus.

Layers 4 and 5 are the author's point 3, second half, deliberately routed here
so each `\cite` is judged with its own paragraph in view.

## Unit inventory

`paper.tex`, 16 units, with the count of numeric literals each carries and how
many the crosswalk does **not** guard (a screening figure — the test matches
value strings, so small integers are over-credited as "guarded"; the *unguarded*
column is the reliable signal):

| Unit | literals | unguarded |
|---|---:|---:|
| Abstract | 15 | 4 |
| 1 Introduction | 47 | 26 |
| 2.1 Overview | 152 | 10 |
| 2.2 Morris rankings | 85 | 18 |
| 2.3 VC-AC | 35 | 10 |
| 2.4 Hyperoxia | 75 | 23 |
| 2.5 Sex divergence | 77 | 27 |
| 2.6 Secondary | 29 | 18 |
| 3 Discussion | 54 | 19 |
| 4.1 Engine | 18 | 9 |
| 4.2 Bodies | 23 | 19 |
| 4.3 Sweep | 54 | 19 |
| 4.4 Classifier | 63 | 26 |
| 4.5 Stats | 33 | 11 |
| 4.6 AI tools | 14 | 8 |
| Back matter | 17 | 8 |

Then `supplement.tex`, S1 → S17.

---

# Layer 4 — cross-references: **complete, 0 defects**

Every `\ref{}` in both documents resolved to its `\label{}`, and each target's
enclosing heading compared against what the citing sentence announces.
**101 labels indexed; 89 references in `paper.tex`, all resolving; 0 missing
labels; 0 document mismatches** (no sentence says "Supplement" while pointing at
a paper label, or "Methods" while pointing at a supplement label).

Spot-read of the semantic half, on the references most likely to have drifted:

| Sentence says | Resolves to | ✓ |
|---|---|---|
| "reproduced rather than merely reported (Supplement §S12)" | supplement S12 *Reproducibility recipe* | ✓ |
| "a clinically recognisable state … (Methods §4.3; Supplement §S5.1)" | paper 4.3 *Sweep design*; supplement S5.1 *Berlin-band calibration* | ✓ |
| "cross-verified by SHAP (Supplement §S13)" | supplement S13 *SHAP cross-verification of the Morris sensitivity rankings* | ✓ |
| "characterised separately in §2.5" | paper 2.5 *Sex-stratified solver divergence and blood-volume mechanism* | ✓ |
| "the preregistered decision (Supplement §S3.4)" | supplement S3.4 *Sobol bolt-on: preregistered decision* | ✓ |
| "Cornish cross-comparison (Supplement §S7)" | supplement S7 *Cornish et al. 2023 per-channel cross-mapping* | ✓ |
| "the 120-second window (Supplement §S16)" | supplement S16 *Output stability across the 120-second measurement window* | ✓ |

Tool: `crossref_check.py` (session scratchpad), re-runnable.

---

# Unit 1 — Abstract

Fifteen numeric literals. Fourteen are covered by the crosswalk, whose
occurrence counts include the abstract instance: `T1.01` 1,280 · `T1.02a`
20.6 % · `T1.11` 0 of 1,280 · `T1.12` 20/1,280 · `T1.23` 643 mmHg ·
`T3.s027.bv_floor` 4,082 mL. All PASS.

**One literal is unguarded: `median 93~\%`.** See finding F-1.

Re-derived directly from `results/h1_top3_fraction.csv` (48 rows):

| Paper | Re-derived | ✓ |
|---|---|---|
| "median 93 % of total sensitivity" | median of `top3_fraction` = **0.9277** → 92.77 % → 93 % at two significant figures | ✓ |
| (§2.2) "median top-3 fraction of 0.928" | same column, **0.9277** | ✓ |
| (§2.2) "0.658--0.998" | min **0.6581**, max **0.9985** | ✓ |
| (§2.2, Fig 2) "48 of 48" | **48 of 48** rows above 0.5 | ✓ |

Non-numeric claims checked: "actively maintained" is the wording settled by the
citation-count evidence (see `physiology_simulator_citations`, decision P0-4);
"no formal sensitivity analysis of its operational inputs has been published" is
the Pulse FAQ verbatim plus the 2020 `STUDY_SENSITIVITY_ANALYSIS_1_0_0` nuance
already audited; the four flag names match `src/detector.py`.

---

# Unit 2 — Introduction

## The Webb 2020 clause — re-verified after the readability rewrite

This is the paragraph the reference audit flagged as the paper's most attackable
sentence, rewrote on 2026-07-27 after finding **three errors** in a banked
version (a false "no ranking of input influence"; "identical" for two patients
Webb deliberately makes *differ*; and 12,642 presented as recomputable when it
is not). It was then touched **again** by the 2026-07-29 readability pass.

**Verified today: the readability pass changed exactly one thing — a semicolon
became a full stop.** Every audited fact survives, word for word:

| Verified fact (source: PLoS full-text XML, 2026-07-27) | Present today | ✓ |
|---|---|---|
| "12{,}642 unique patient and ventilator combinations" — quoted as Webb's own count, never as a recomputable product | yes | ✓ |
| "spanning respiratory compliance, diffusion impairment and PEEP" | yes | ✓ |
| "does rank parameters by outcome correlation" | yes | ✓ |
| ranking is over the *mismatch* (emphasised) | yes | ✓ |
| "two equal-sized 70~kg bodies" — **not** "identical" | yes | ✓ |
| "a single composite safety outcome" | yes | ✓ |
| "pressure-mode ventilation" (Webb's own phrase) | yes | ✓ |
| "respiratory rate, I:E ratio and respiratory resistance held fixed" | yes | ✓ |
| "resolves neither … nor … nor" — "resolves", not "mentions" | yes | ✓ |

## Other Introduction claims

- **five nodes 0.0, 0.3, 0.6, 0.9, 1.0** — verified verbatim at
  `pulserespmethod` L1176 in the local clone (register Phase 3).
- **five compartments: carina, left and right anatomic dead space, left and
  right alveoli** — verified verbatim (register Phase 3).
- **"a low fidelity clinical approach…not necessarily for high fidelity
  predictive purposes"** — verified verbatim at `pulsesystem`
  `SystemMethodology.md` L261–263 (register Phase 3).
- **"a single 2020 sensitivity study"** — the tag `STUDY_SENSITIVITY_ANALYSIS_1_0_0`
  is dated 2020-07-20 (S016 GitLab audit).
- **0.02 s (50 Hz)** — the reciprocal is exact; the claim carries
  `\cite{pulsesystem,bray2019}`, and the register's Phase-3 sweep records the
  system-methodology page as the verified source for the solver description.

---

# Unit 2.2 — Morris rankings, and the Sobol non-linearity paragraph

Every number in the non-linearity paragraph re-derived from
`results/sobol_ci_buckets.json`:

| Paper | Artefact | ✓ |
|---|---|---|
| "leaves 23 of 144" | `core_nonlinear_all_seeds` = 23, `n_top3_rows` = 144 | ✓ |
| "These spread over 17 of the 48 cells" | `cells_touched_by_core` = 17, `n_cells` = 48 | ✓ |
| "12 combinations on the female body against 11 on the male" | `core_by_sex` = {F: 12, M: 11} | ✓ |
| "PEEP … in 8 of the 23, ahead of respiratory rate at 5" | `core_by_input` peep 8, rr 5 (full: dbp 1, fio2 2, hr 1, sbp 3, vt 3) | ✓ |
| "Delivered tidal volume … in 8 of the 23" | `core_by_output` Vt 8 (full: HR 4, PaO2 7, SpO2 3, PaCO2 1) | ✓ |
| "144" is 48 × 3 | 48 × 3 = 144 | ✓ (never stated — see F-2) |

Also confirmed present in the artefact and consistent with §2.2 / §S3.4:
`point_estimate_promotions` 72, `cells_firing_point_estimate` 43,
`promote_threshold` 0.6, `skip_threshold` 0.4, `n_bootstrap` 1000,
`sobol_base_sample` 64, `sobol_runs_required` 11008,
`sobol_budget_runs_preregistered` 1500.

---

# Unit 4.2 — Patient reference bodies

Every derived quantity re-computed, and both Pulse constants read from the
primary source rather than quoted from memory:

| Paper | Re-derived | ✓ |
|---|---|---|
| female "(BMI 21.2)" | 56.2 / 1.63² = **21.1525** → 21.2 | ✓ |
| male "fixes the body mass index (BMI) at 20.8" | 67.3 / 1.80² = **20.7716** → 20.8 | ✓ |
| "0.34 and 0.21~kg above the values used" | 67.64 − 67.3 = **0.34**; 56.41 − 56.2 = **0.21** | ✓ |
| "214 months (17~y 10~m)" | 214 = **17 y 10 m** | ✓ |
| `heightStandardMale\_cm = 177.0` | `SetupPatient.cpp:72` → **177.0** | ✓ |
| `heightStandardFemale\_cm = 163.0` | `SetupPatient.cpp:75` → **163.0** | ✓ |

Citation placement: both `\cite{kuczmarski2002cdc}` loci are correct — the first
carries the 50th-percentile weights, the second the female stature percentile.
The known **age-label mismatch** (CDC tables read at 214 months, the
preregistration naming 18.0 years) is already disclosed *in the paragraph
itself*, which states both the 214-month values and the 18.0-year values and the
0.34 / 0.21 kg gap between them. Nothing hidden.

---

# Findings

### 🟡 F-1 — `median 93~\%` is a guard gap, not an error

The percentage form appears **twice** in `paper.tex` — in the Abstract
("median 93 % of total sensitivity") and in the Discussion ("a median 93 % of
summed μ\* on 48 of 48 cell × output combinations") — and has **no row in
`paper_to_monograph_map.md`**.

The value is right: the artefact median is 0.9277, i.e. 92.77 %, which is 93 %
at two significant figures. The monograph never uses the percentage form; it
always writes 0.928.

The risk is drift, not error: a future correction to `0.928` would update the
two guarded loci and silently leave these two behind. The fix is to add a
crosswalk row against `T1.08` with `expected_occurrences: 2`.

**Not applied**, because it moves the audit's own headline count from 97 to 98,
and that count is quoted in `README`, in Supplement §S12 and in commit messages.
Author decision.

### 🟡 F-2 — "23 of 144" never says where 144 comes from

`paper.tex` §2.2 writes "leaves 23 of 144" with no prior statement that 144 =
48 cell × output combinations × 3 top-ranked inputs. Both factors appear in the
artefact (`n_top3_rows` 144, `n_cells` 48) and elsewhere in the paper, but the
product is never spelled out for the reader.

The supplement already does it correctly: *"72 of the 144 top-three inputs,
spanning 43 of the 48 cell × output combinations."*

Minimal repair, adding no new number: "leaves 23 of 144" → "leaves 23 of **the**
144". Author decision.

### 🟢 F-3 — the "48 cells" dossier: **measured, and the earlier framing was wrong**

Table 1 defines *Cell* as a (scenario, sex) slice, so there are **8**. Writing
"the 48 cells" contradicts that glossary.

The dossier had been deferred on the reasoning that the loose shorthand was the
corpus-wide convention, so "correcting one locus would create the inconsistency
rather than remove it." **Counted by hand today, that is not the case for the
two documents being submitted.**

| Document | loose "48 cells" | explicit "48 cell × output" |
|---|---:|---:|
| `paper.tex` | **2** | 5 distinct sentences |
| `supplement.tex` | **1** | 3 distinct sentences |
| `manuscript.md` | **18** | 7 |

In `paper.tex` and `supplement.tex` the explicit long form is already the
dominant convention. The three loose loci are the outliers:

1. `paper.tex` §2.2 — "all 48 cells clear the 50~\% bar (minimum 0.658)"
2. `paper.tex` §2.2 — "These spread over 17 of the 48 cells"
3. `supplement.tex` §S3.4 — "The stable set spans 17 of the 48 cells"

Repairing those three makes each submitted document agree with its own Table 1,
and **removes** an inconsistency rather than creating one. It is still a change
to how a claim is worded, so nothing was modified.

The monograph is the opposite case — 18 loose against 7 explicit, an entrenched
internal convention in a document that goes to Zenodo rather than to npj, and
which carries its own glossary. Treat it separately, or leave it.

*(Counting note: "48 of 48" yields two `\b48\b` matches, so the explicit column
above is given in distinct sentences, not raw matches.)*

---

# Unit 2.1 — Overview of the reliability atlas

152 numeric literals, the densest unit in the paper; 10 unguarded. Constants
read from the primary source rather than quoted:

| Paper | Re-derived | ✓ |
|---|---|---|
| "coefficient of variation $>$ 0.05" | `src/detector.py`: `CV_THRESHOLD: float = 0.05` | ✓ |
| "the PaO$_2$ upper bound of 600~mmHg" | `src/detector.py`: `HARD_BOUNDS["PaO2"] = (20.0, 600.0)` | ✓ |
| "the 8 (scenario × sex) cells and the 6 steady-state outputs" | 4 × 2 = 8; 8 × 6 = 48 | ✓ |
| "7 green / 29 yellow / 12 red" | `results/reliability_traffic_light.csv`, counted | ✓ |
| "7/48 (15 %), 29/48 (60 %), 12/48 (25 %)" | 14.58 → 15; 60.42 → 60; 25.00 → 25 | ✓ |

The alveolar-gas justification for the 600 mmHg bound ("at FiO₂ = 1.0 a healthy
lung's PaO₂ can legitimately climb toward the ≈663 mmHg ceiling, so real values
between 600 and 663 exist") is consistent with the comment block at
`src/detector.py` L65, which states the same reasoning in the code itself.

---

# Unit 2.3 — VC-AC dyssynchrony and the −2 cmH₂O lever

## The Pulse source citation, verified line by line

The paper cites `SEMechanicalVentilatorVolumeControl.cpp` **lines 120–128**
as "where the default patient trigger is configured". Opened in the local
clone:

```
120  s.SetInspirationPatientTriggerRespiratoryModel(eSwitch::Off);
121  if (GetMode() == eMechanicalVentilator_VolumeControlMode::AssistedControl)
122  {
123    if (HasInspirationPatientTriggerFlow())
124      s.GetInspirationPatientTriggerFlow().Set(GetInspirationPatientTriggerFlow());
125    if (HasInspirationPatientTriggerPressure())
126      s.GetInspirationPatientTriggerPressure().Set(GetInspirationPatientTriggerPressure());
127    if(!HasInspirationPatientTriggerFlow() && !HasInspirationPatientTriggerPressure())
128      s.SetInspirationPatientTriggerRespiratoryModel(eSwitch::On);
```

**The range is exact** — 120 is where the respiratory-model trigger is switched
off, 128 is the fall-through that switches it back on when neither explicit
threshold is set. That fall-through is precisely the mechanism the paper
describes.

## The rest of the unit

| Paper | Re-derived | ✓ |
|---|---|---|
| "50 of the 64 reruns … (met here, 78.1 %)" | 50 / 64 = 78.125 % | ✓ |
| "the experiment's preregistered acceptance gates" | `S014_trigger_pressure_lockout.md` L118–130, verbatim: *"The 0.04 / 0.75 thresholds are committed before any S014 run is observed."* | ✓ |
| "reduces the worst-case Vt CV from 1.826 to 0.018" | `paired_comparison.parquet`, row with the largest before/after delta: 1.8257 → 0.0178 | ✓ |

Note on the worst case: the S014 log separately reports a locked maximum of
**0.112**, which is the maximum of `Vt_cv_lock` over all 64 reruns (0.1123
re-derived). The paper's 0.018 is the *same-run* pairing. Two different
statistics, and the audit ledger already distinguishes them explicitly
(`T1.06` vs `T1.s014.worstcase_locked_vtcv`). Not a discrepancy.

Citation placement checked: `figueroacasas2016` carries the clinical precedent
for dyssynchrony under volume control, and the sentence explicitly fences off
what is ours — *"the specific conditions that produce it here … are our own
in-silico finding, not a claim drawn from that source."* `thille2006`,
`blanch2015`, `akoumianaki2014`, `sinderby1999` each sit on the clause they
support (asynchrony patterns, mortality association, esophageal pressure,
diaphragm EMG). All four were audited MATCH in the reference register.

---

# Unit 2.4 — Transient hyperoxia

| Paper | Re-derived | ✓ |
|---|---|---|
| "≈663 mmHg (FiO₂ = 1.0, P_B = 760, P_H₂O = 47, PaCO₂ = 40, R = 0.8)" | 1.0 × (760 − 47) − 40 / 0.8 = **663.0** | ✓ |
| "The ≈20 mmHg gap" | 663 − 643 = **20** | ✓ |
| "an additional 300 seconds (420 seconds of total simulated time)" | 120 + 300 = **420** | ✓ |
| "six of the 44 S1 reruns … above 700 mmHg, four … near 1,400 mmHg" | ledger `M.T12.runaway_frac` 6/44, `T1.24d` 1,408 mmHg | ✓ |

The equation is printed with all five of its inputs, so a reader can recompute
it — which is what makes this the best-evidenced number in the section.

---

# Unit 2.5 — Sex-stratified divergence and the blood-volume mechanism

Every quantity re-derived from the formula as printed, or from the artefact:

| Paper | Re-derived | ✓ |
|---|---|---|
| "BV = 65.6 · weight^1.02 … yielding 4,803 mL for the 67.3 kg male" | 65.6 × 67.3^1.02 = **4802.63 mL** | ✓ |
| "…and 3,996 mL for the 56.2 kg female" | 65.6 × 56.2^1.02 = **3996.09 mL** | ✓ |
| "essentially the same blood volume per kilogram (≈71 mL kg⁻¹)" | male **71.36**, female **71.10** | ✓ |
| "the resulting 17 % difference" | (4802.63 − 3996.09) / 4802.63 = **16.79 %** → 17 % | ✓ |
| "Nadler's sex-specific equations give 73.0 and 63.8 mL kg⁻¹" | male 0.3669·1.80³ + 0.03219·67.3 + 0.6041 = 4.9102 L → **72.96**; female 0.3561·1.63³ + 0.03308·56.2 + 0.1833 = 3.5846 L → **63.78** | ✓ |
| "an intermediate bracket (4,400 mL, a 8.4 % reduction)" | (4802.63 − 4400) / 4802.63 = **8.38 %** | ✓ |
| "the engine's setup-time minimum (4,082 mL, a 15.0 % reduction)" | (4802.63 − 4082.24) / 4802.63 = **15.00 %** | ✓ |
| "the floor sits 15.0 % below the computed default" | Pulse's documented minimum is BV × 0.85; 4802.63 × 0.85 = **4082.24 mL**, the stated floor exactly | ✓ |
| "falls 86 mL below the male floor" | 4082.24 − 3996.09 = **86.15 mL** | ✓ |
| "Across the 24 (scenario × output) comparisons" | 4 × 6 = **24** | ✓ |
| "FiO₂ at its 1.0 boundary in 13 of the 20 cases (the other 7 near ≈0.74)" | 13 + 7 = 20, and the total 20 is anchored (`T1.12`) | ✓ |

The 17 % figure deserves a note: it is computed against the **male default as
denominator** (16.79 %). Against the female value it would be 20.18 %. Figure 4b
plots reductions relative to the male default, so the paper's choice of
denominator is the one its own figure uses. Consistent.

Both `nadler1962` citations sit correctly: the first on the *clinical range*
that Pulse's shared per-kilogram value falls within, the second on the
*sex-specific* equations that Pulse's formula does not reproduce. The `atls2018`
citation carries the Class I hemorrhage comparison — with the caveat already
recorded in the reference register that ATLS's own wording is "<15 %" where the
paper writes "a loss of up to 15 %".

---

# Findings, continued

### 🟡 F-4 — §2.3 points at the wrong statistic for its own gate

The paper: *"clearing both of the experiment's preregistered acceptance gates:
a median Vt CV drop of at least 0.04 **(met by the collapse above)** and at
least 75 % of reruns below 0.05 (met here, 78.1 %)."*

"The collapse above" is the preceding sentence, "collapses the median Vt CV
from 0.351 to 0.016" — a **difference of medians** (0.335). The gate S014
actually preregistered is `median(CV_orig − CV_lock) ≥ 0.04`, a **median of
paired differences**, measured at **+0.326**.

Both clear 0.04 by roughly eight-fold, so **no conclusion moves**. But a
reviewer who recomputes lands on 0.335 where the log says 0.326 and cannot tell
which one the gate used. The monograph does distinguish them (`manuscript.md`
L2629–2633 states the paired median separately); the paper is here less precise
than its own source document.

Minimal repair introducing no new number: "(met by the collapse above)" →
"(met by a factor of eight)". **Author decision. Nothing modified.**

### 🟢 F-5 — "96 % reduction" is right, but only from the unrounded medians

Re-derived from `data/runs/s014_trigger_lockout/paired_comparison.parquet`
(64 rows):

| | value |
|---|---|
| median `Vt_cv_orig` | 0.350867213022344 |
| median `Vt_cv_lock` | 0.015631290782845753 |
| reduction, unrounded | **95.545 %** → rounds to **96** |
| reduction from the printed pair (0.351, 0.016) | 95.442 % → rounds to **95** |
| median of the per-run reductions (alternative reading) | 96.448 % → **96** |

So 96 is correct, and correct under two different readings. But a reader who
recomputes from the two numbers printed alongside it gets 95. The claim appears
**only in the monograph** — `manuscript.md` L2633, L2790, L4153 — and **not in
`paper.tex`**, which never states a percentage reduction.

Recorded rather than raised: the number is right, and its only cost is a
reviewer's double-take in a document that is not the submission.

### 🔴 F-6 — the `M.*` monograph anchors are string-occurrence checks, not value re-derivations

Discovered while chasing F-5. `--check-monograph` reports
`M.T16.vtcv_reduction | 96 % | 3 | 3 | PASS`. That PASS means only that **the
literal string "96 %" occurs three times in `manuscript.md`, as declared**. It
does **not** mean 96 was re-derived from data — and in this case nothing
anywhere re-derived it until today.

The same holds for the other `M.*` rows in that table (`M.T12.runaway_pct`
`14 %`, `M.T17.*`, `M.T18`, `M.T19`, `M.T20.cornish_pct` `18.6 %`, …): they
guard against a value being *silently deleted or duplicated*, which is real
value, but not against a value being *wrong*.

This is a genuine limit on what "26 / 26 monograph anchors PASS" certifies, and
it is worth stating wherever that figure is quoted. The `T1.*` / `T2.*` /
`T3.*` ledger anchors are different — those do re-derive from the artefacts.

### 🔵 Discarded hypothesis, recorded so it is not re-derived

I first raised a FAIL against `paper.tex` for the 96 % figure. **`paper.tex`
never makes that claim.** Its five occurrences of the digits `96` are all inside
`3{,}996` mL, the female blood volume. The check had put a claim in the paper's
mouth that belongs to the monograph, and the monograph's version turned out to
be correct. Both halves of the alarm were wrong.

---

# Unit 2.6 — Secondary observations

| Paper | Re-derived | ✓ |
|---|---|---|
| "the round-tenths convention {0.0, 0.3, 0.6, 0.9, 1.0}" | verbatim at `pulserespmethod` L1176 (register Phase 3) | ✓ |
| "the 200-run continuous-severity sweep" | `data/runs/continuous_ards/` contains **200** run directories | ✓ |
| "extends the empirical band to [0.879, 0.945] on the low edge" | 0.879 < 0.91, upper edge unchanged — "on the low edge" is exact | ✓ |
| "places severe ARDS (S4) at 0.95, above this band" | 0.95 > 0.945 | ✓ |
| "the same [50, 110] bpm range" | `preregistration.md` HR baseline = 50–110 bpm | ✓ |

Display consistency across the whole paper: `0.91--0.945` appears **4×**,
`$[0.879, 0.945]$` **5×**. Both forms are used deliberately — the first for the
*documented* band inherited from prior probes, the second for the band this
atlas *measured*. §2.6, §3 and §4.3 all keep that distinction.

---

# Unit 3 — Discussion

| Paper | Re-derived | ✓ |
|---|---|---|
| "Spearman ρ point estimates 0.75–1.00 across the 12 scenario–output cells" | `results/spearman_mu_star.csv`: **12** non-null rows, min **0.7500**, max **1.0000** | ✓ |
| "(1) … (6) field-attributed setup-error messages" | six markers, present and in order | ✓ |
| "the build-only v4.3.2 release" | `REL_4_3_2` tagged 2025-08-12, whole-tag diff 7 files, none under `src/cpp` | ✓ |
| "a median 93 % of summed μ*" | 0.9277 → 92.77 % → 93 % — see F-1 (unguarded) | ✓ |

The `cornish2023`, `wilkinson2016`, `munafo2017`, `pulsefaq` and
`sinnige2026active` citations each sit on the clause they support; all five were
audited MATCH in the reference register, and the ACTiVE wording was tightened at
source on 2026-07-24.

---

# Unit 4.1 — Pulse engine and configuration

| Paper | Re-derived | ✓ |
|---|---|---|
| Intro "0.02 s (50 Hz)" vs Methods "a 20 ms fixed timestep" | 0.02 s = 20 ms = 1/50 Hz — the three display forms of one constant agree | ✓ |
| "the subsequent v4.3.2 release (August 2025)" | `REL_4_3_2` tagged **2025-08-12** | ✓ |
| "a 6-core / 12-thread Intel i5-11400H laptop, 8 GB RAM, CPU-only" | `CLAUDE.md`: "i5-11400H (6 physical / 12 logical cores), 8 GB RAM"; "Pulse is CPU-only — neither GPU is used in any atlas computation" | ✓ |
| "5-compartment lung (carina, left and right anatomic dead space, left and right alveoli)" | verbatim at `pulserespmethod` (register Phase 3) | ✓ |

---

# Unit 4.3 — Sweep design

Every swept range checked against `preregistration.md` rather than against
memory:

| Paper | `preregistration.md` | ✓ |
|---|---|---|
| HR 50–110 bpm | 50–110 | ✓ |
| SBP 90–120 mmHg | 90–120 | ✓ |
| DBP 60–80 mmHg | 60–80 | ✓ |
| RR 8–20 bpm | 8–20 | ✓ |
| Vt 300–800 mL | "Vt target \| 300–800 \| mL" | ✓ |
| FiO₂ 0.21–1.0 | "FiO2 \| 0.21–1.0 \| fraction" | ✓ |
| PEEP 0–20 cmH₂O | "PEEP \| 0–20 \| cmH2O" | ✓ |
| "post-clip pulse-pressure ratio DBP/SBP ≤ 0.75 enforced" | DBP row carries the same constraint | ✓ |
| "5-second intervals (13 samples in the final 60-second window)" | 60 / 5 = 12 intervals → 13 points inclusive | ✓ |
| "cost is a linear function of the number of inputs, against the order-k² cost of a resolution V fractional factorial design" | the wording locked by commit `378e959`, which corrected an earlier "against exponential" | ✓ |
| ARDSnet reference setting "VC-AC, tidal volume 6 mL/kg, PEEP 10 cmH₂O, FiO₂ 0.4" | present verbatim; `ards2012` carries the Berlin band comparison | ✓ |

---

# Unit 4.4 — Steady-state classifier

| Paper | Re-derived | ✓ |
|---|---|---|
| "the locked threshold of 0.05" | `src/detector.py`: `CV_THRESHOLD: float = 0.05` | ✓ |
| "PaO₂ upper bound of 600 mmHg" | `HARD_BOUNDS["PaO2"] = (20.0, 600.0)` | ✓ |
| "`HARD_BOUNDS_PHYSIOLOGICAL` (PaO₂ upper raised to 700 mmHg)" | present in `src/detector.py` as a parallel dictionary, explicitly *not* replacing the locked classifier | ✓ |
| "OLS regression on the 13 sample points in the [60, 120] s window" | (120 − 60) / 5 = 12 intervals → 13 points | ✓ |
| hyperoxia arm: HR **2.6 %** | ledger `T5.window.hyperox_hr_pct` re-derives **2.564** | ✓ |
| hyperoxia arm: MAP **none** | `T5.window.hyperox_map_pct` re-derives **0** | ✓ |
| hyperoxia arm: PaCO₂ **3.6 %** | `T5.window.hyperox_paco2_pct` re-derives **3.59** | ✓ |
| Vt-oscillation arm: HR **2.3 %** | `T5.window.vtosc_hr_pct` re-derives **2.31** | ✓ |
| Vt-oscillation arm: MAP **0.7 %** | `T5.window.vtosc_map_pct` re-derives **0.6601** | ✓ |
| Vt-oscillation arm: PaCO₂ **2.0 %** | `T5.window.vtosc_paco2_pct` re-derives **1.98** | ✓ |

The seven `\cite` in the bounds sentence (`brower2000`, `severinghaus1979`,
`singer2016`, `evans2021sepsis`, `mancia2023esh`, `nin2017`,
`west2020respiratory`) each name the bound they anchor, and the sentence points
the reader to Supplement §S3 for the per-bound table rather than asserting the
values inline. All seven were audited in the reference register.

---

# Unit 4.5 — Statistical analyses

Re-derived from `results/bh_fdr_survivors.csv` (24 rows) and
`results/sobol_ci_buckets.json`:

| Paper | Re-derived | ✓ |
|---|---|---|
| "The resulting 24-test family" | 24 rows = 4 scenarios × 6 outputs | ✓ |
| "Benjamini–Hochberg … at q = 0.05" | `bh_critical` runs 0.002083 → 0.050000 across ranks 1 → 24, i.e. i·q/m with q = 0.05, m = 24 | ✓ |
| "With 2,000 permutations the smallest empirical p …" | 1 / 2000 = 0.0005 | ✓ |
| "the two tests that reach that floor are reported as p < 0.001" | exactly **two** rows at p ≤ 0.0005: **S2 PaCO₂** and **S3 PaCO₂** | ✓ |
| §2.5 "PaCO₂ in S1, S2 and S3 — the latter two at p < 0.001 — together with SpO₂ and PaO₂ in S4" | the BH survivor set is exactly **{S1 PaCO₂ (0.0090), S2 PaCO₂ (0.0000), S3 PaCO₂ (0.0000), S4 SpO₂ (0.0015), S4 PaO₂ (0.0030)}** — five, and "the latter two" are precisely the two at the floor | ✓ |
| "the point-estimate trigger fires on 72 of the 144 top-three inputs, spanning 43 of the 48" | `point_estimate_promotions` 72, `n_top3_rows` 144, `cells_firing_point_estimate` 43, `n_cells` 48 | ✓ |
| "a base sample of 64 with a single promoted input — puts 43 cells at 11,008 runs" | 64 × 4 = 256 per cell; 256 × 43 = **11,008** = `sobol_runs_required` | ✓ |
| "the bolt-on was therefore infeasible" | preregistered budget 1,500 runs against 11,008 required — **7.3× over** | ✓ |

This is the densest correctly-anchored unit in the paper: the §2.5 narrative and
the §4.5 method statement agree with the artefact row for row, including which
two of the five survivors sit at the permutation floor.

---

# Unit 4.6 — Use of AI tools

Four distinct models are named across three phases: `claude-opus-4-7` ×
Gemini Pro 3.1, then `claude-opus-4-8`, then `claude-opus-5`. The phrase "under
direct supervision by S.N." appears **3×**, once per phase. This satisfies the
Nature Portfolio AI policy verbatim requirement that "Use of an LLM should be
properly documented in the Methods section", and no LLM appears in the author
list.

Open item carried here from the deferred dossier: **"dual-LLM"** occurs once, in
Author contributions, pointing at this section — which now describes four
models. Not false (that pipeline existed and is the one S.N. supervised), but a
reader following the pointer finds more than two. Authorship-statement decision,
grouped with F-1/F-2/F-3.

---

# Unit — Back matter

| Requirement | State | ✓ |
|---|---|---|
| Data availability (npj: mandatory) | present | ✓ |
| Code availability | present, `https://github.com/santinon/pulse_reliability_atlas` | ✓ |
| Acknowledgements, with funding and grant number, no separate Funding section | present | ✓ |
| Author contributions, all authors by initials | present | ✓ |
| Competing interests | present | ✓ |
| "the code carries the Apache-2.0 licence" | repository `LICENSE` begins "Apache License" | ✓ |
| **Statement of the funders' role** | **absent** | ✗ — this is npj finding **N-3**, unchanged |

---

# Corrections to this register

### Two false alarms I raised and then disproved — recorded so they are not re-derived

Both came from the same mistake: **testing the paper against the wrong
artefact.**

1. **"96 % reduction" attributed to `paper.tex`.** The paper never makes that
   claim; its five `96` digits are all inside `3{,}996` mL. The claim belongs to
   the monograph, and it is correct (see F-5).
2. **"195 runs" and "303 runs" declared unverified.** I compared them against
   the row counts of `results/s012_f003_hyperoxia_audit.csv` and
   `s012_f004_vt_oscillation_audit.csv` — which are **per-channel summaries with
   four rows each**, not per-run files. The populations are carried in those
   files' own `n_runs_with_data` (195) and `n_total_runs` (303) columns, and
   every one of the six drift percentages is re-derived by a `T5.window.*`
   ledger anchor.

The lesson is worth keeping: an artefact whose *shape* differs from the claim's
shape will produce a confident, wrong verdict.

### Amendment to F-6

F-6 said the `M.*` anchors are string-occurrence checks and that "the `T1.*` /
`T2.*` / `T3.*` ledger anchors are different — those do re-derive". That list
was incomplete: the **`T5.*` family also re-derives**, and it is what actually
guards the six §4.4 drift percentages (`T5.window.hyperox_paco2_pct` declares
3.6 and computes 3.59). F-6's substance is unchanged — `M.*` really does only
count strings — but the coverage picture is better than the finding implied.

---

# `paper.tex` is complete

All **16 units** closed.

Scripted-check tally, counted at the moment of writing by re-running all three
batches and reading their own summary lines — not carried forward from an
earlier count:

| Batch | passed | flagged |
|---|---:|---:|
| `stepwise_rederive.py` (2.2, 4.2, Abstract/Discussion percentage form) | 16 | 0 |
| `stepwise_rederive2.py` (2.1, 2.3, 2.4, 2.5) | 22 | 1 |
| `stepwise_rederive3.py` (2.6, 3, 4.1, 4.3, 4.4, 4.5, 4.6, back matter) | 29 | 3 |
| **total** | **67** | **4** |

Of the four flagged, **three were my own scripts' errors** and are disproved
above (the invented "96 %" attribution, and the two wrong-artefact population
counts). **One is real and already recorded: N-3**, the missing statement of the
funders' role, which is an npj form requirement rather than a factual defect.

Verifications carried out outside those counters: the cross-reference layer
(89 `\ref` in `paper.tex`, 0 defects), the BH / permutation re-derivation
(24-test family, 5 survivors, 2 at the permutation floor, `bh_critical` ladder
checked against i·q/m), the hand count of the "48 cells" shorthand across three
documents, the S014 raw re-derivation of the 96 % reduction from
`paired_comparison.parquet`, and the line-by-line reading of
`SEMechanicalVentilatorVolumeControl.cpp` lines 120–128.

Findings raised: **F-1 … F-4** (none of them a false statement), **F-5** and
**F-6** (recorded, F-6 amended above).

Nothing in `paper.tex` was modified during this pass.

---

# `supplement.tex` — S1 → S17

## Method for this document

`supplement.tex` carries **1,750 numeric literals, 807 of them outside the
crosswalk** — more than twice the paper's density, because most of them are
table cells. Reading them one by one would be slower *and* weaker than
re-deriving each table wholesale from the artefact that generates it. So every
data table was compared **row by row against its source**, and every table with
a declared total had that total recomputed from its own rows.

One structural fact established while reading `scripts/audit_claims.py`
(L286–295) and worth recording: **the crosswalk runs its occurrence check on the
concatenated `paper.tex` + `supplement.tex` corpus**, and `expected_occurrences`
is the total across both documents. The 97 rows therefore already cover the
supplement — but only for the literals they name.

## S1 — Pulse engine in context

Prose and four citations (`bray2019`, `pulseabout`, `pulsefaq`,
`pulserespmethod`), all four audited MATCH in the reference register, with
`pulseabout` and `pulsesystem` re-read verbatim in that register's Phase 3.

## S2 — Verified Pulse 4.3.1 limitations

**Eleven table rows carrying the twelve locked limitations** (row "5–6" merges
the HR and RR initialisation gates). Each row was matched against the
corresponding entry in the project's locked list:

| Row | Marker(s) checked | ✓ |
|---|---|---|
| 1 | "No formal SA / UQ" + `STUDY\_SENSITIVITY\_ANALYSIS` | ✓ |
| 2 | "SBP > 120" + the 0.75 pulse-pressure ratio | ✓ |
| 3 | "age ≥ 18" + `SetupPatient` | ✓ |
| 4 | "0.91–0.945" | ✓ |
| 5–6 | "50–110" + "8–20" | ✓ |
| 7 | "11.3–25.3" + "0.07–2.25" | ✓ |
| 8 | "single trachea resistance" | ✓ |
| 9 | "ventilation–perfusion" | ✓ |
| 10 | "7 %" + "vital capacity" | ✓ |
| 11 | "inertance" | ✓ |
| 12 | "dicrotic notch" + "T-wave" | ✓ |

**The two PC-AC referents are not merged.** The project's locked list warns that
(a) PC-AC over-delivering relative to VC-AC *within Pulse* and (b) PC-AC
under-delivering relative to the *physical ASL-5000 reference* are different
comparisons that must never be conflated. Row 7 reports only (b), against the
VC-AC comparator from the same Pulse validation tables, and closes with an
explicit disclaimer: *"that paper reports qualitative ASL-5000 waveform
agreement, not these quantitative percentages."* Exactly the provenance
decision the reference register recorded.

## S3 — Full Methods detail

Both locked tables reproduced **cell for cell** from `src/detector.py`:

| `HARD_BOUNDS` | supplement | detector |
|---|---|---|
| HR (bpm) | 20 / 220 | (20.0, 220.0) ✓ |
| MAP (mmHg) | 30 / 180 | (30.0, 180.0) ✓ |
| Vt (mL) | 50 / 1500 | (50.0, 1500.0) ✓ |
| SpO₂ (fraction) | 0.50 / 1.00 | (0.50, 1.00) ✓ |
| PaO₂ (mmHg) | 20 / 600 | (20.0, 600.0) ✓ |
| PaCO₂ (mmHg) | 10 / 120 | (10.0, 120.0) ✓ |

| `DRIFT_MAX_DELTA_60S` | supplement | detector |
|---|---|---|
| HR | 5 | 5.0 ✓ |
| MAP | 5 | 5.0 ✓ |
| Vt | 50 | 50.0 ✓ |
| SpO₂ | 0.02 | 0.02 ✓ |
| PaO₂ | 15 | 15.0 ✓ |
| PaCO₂ | 5 | 5.0 ✓ |

Twelve rows, twelve matches. (This is also the section the npj audit flags as
**N-1**, Supplementary Methods — a form problem, not a content one.)

## S4 — `not_steady_state` attribution

Every column recomputed from the table's own eight cell rows:

| Column | Row sum | Declared total | ✓ |
|---|---:|---:|---|
| n_total | 1,280 | 1,280 | ✓ |
| n_nss | 530 | 530 | ✓ |
| excl. SpO₂ sat. | 454 | 454 | ✓ |
| excl. Vt CV | 360 | 360 | ✓ |
| excl. both | 185 | 185 | ✓ |
| n_clean | 1,008 | 1,008 | ✓ |

And each of the eight `n_nss` cells matched `results/cell_flag_summary.csv`
`n_not_steady_state` exactly (107, 118, 69, 68, 12, 38, 44, 74). Independently:
that file's `n_clean` column sums to **663**, which is ledger anchor `T1.28`;
1,008 / 1,280 = **78.75 %**, which is `T2.nss.counterfactual`. The two clean
counts are different statistics — locked classifier versus joint exclusion — and
both are right.

## S5 — ARDS instability zone

**Berlin sweep table against `results/pf_berlin_by_scenario.csv`, every cell:**

| Scenario | n | median P/F [IQR] | by FiO₂ stratum | ✓ |
|---|---|---|---|---|
| S1 | 61 = 61 | 431 [388–481] vs 431.0 [387.8, 481.4] | 390 / 481 / — vs 390.0 / 481.4 / no rows | ✓ |
| S2 | 114 = 114 | 304 [264–337] vs 303.5 [264.4, 336.6] | 309 / 282 / 287 vs 308.8 / 282.4 / 286.7 | ✓ |
| S3 | 192 = 192 | 184 [139–231] vs 183.8 [138.9, 231.2] | 228 / 163 / 160 vs 227.6 / 162.6 / 159.8 | ✓ |
| S4 | 91 = 91 | 75 [69–83] vs 74.6 [68.6, 82.7] | — / 99 / 74 vs no rows / 98.6 / 73.8 | ✓ |

The three em-dashes are correct: the artefact genuinely has no rows for S1 at
high FiO₂ or S4 at low FiO₂.

**Continuous-severity table, internal sums:** bin sizes 31 + 20 + 18 + 10 + 2 +
19 = **100** (declared 100); female divergences 0 + 0 + 14 + 5 + 0 + 0 = **19**
(declared 19); male 0 + 0 + 5 + 9 + 0 + 0 = **14** (declared 14). All three ✓.

**Severity-to-physiology mapping** at S4 = 0.95: resistance ×22.5, compliance
×0.45, diffusion surface ×0.075, shunt-path resistance ≈×0.125 — matching the
mechanism recorded in `reference/pulse_ards_severity_mechanism.md`.

## S6 — Spearman ρ on μ\* rankings

**All 12 table rows matched `results/spearman_mu_star.csv`, point estimate *and*
both confidence-interval bounds**, e.g. S2 Vt "0.75, [−0.06, 1.00]" against
0.7500, [−0.0588, 1.0000]. The same 12 rows are what §3 of the paper summarises
as "0.75–1.00 across the 12 scenario–output cells".

## S7 — Cornish per-channel cross-mapping

Three independent sums over the fifteen data rows:

| | Row sum | Declared / expected | ✓ |
|---|---:|---:|---|
| rows (assessed quantities) | 15 | 15 (Cornish Appendix Table 4) | ✓ |
| Hoeffding rejections | 85 | 85 | ✓ |
| bootstrap rejections | 281 | 281 | ✓ |
| **hypothesis denominators** | **1,522** | **1,522** | ✓ |

The last one is the strongest result in this pass. The denominators are **not
printed as a total anywhere in the supplement**, yet summing the fifteen of them
reproduces exactly the figure the reference register established by
transcribing Cornish's Appendix Table 4 verbatim — the same 1,522 that
reconciles their main text's 1,442 + 80. An independent arithmetic confirmation
of a number that was previously only a transcription.

## S8 — VC-AC trigger-lockout protocol

Verified with paper §2.3: the 64 paired reruns, the 0.351 → 0.016 median
collapse, the 1.826 → 0.018 worst case (re-derived from
`paired_comparison.parquet`), the two preregistered gates, and the
`SEMechanicalVentilatorVolumeControl.cpp` lines 120–128 citation read line by
line. See finding **F-4** for the gate-statistic imprecision, which lives in the
paper rather than here.

## S9 — Hyperoxia 300-second convergence

Plateau table: S1 n = 44, median **643.3** [592, 668] — the ledger's `T1.23`
(declares 643, computes 643.3) and `M.T12.runaway_frac` (6 / 44). S3 n = 8,
143.6; S4 n = 8, 72.6.

## S10 — Blood-volume framings

Every value re-derived in paper §2.5: 4,802.63 mL, 3,996.09 mL, 4,082.24 mL, the
4,400 mL bracket, the 17 % absolute gap, and BV = 65.6 · weight^1.02.

## S11 — Engine-side infrastructure recommendations

Prose; its four cross-references (`sec:s2`, `sec:s3-clamp`, `sec:s3-drift`,
`sec:s5-prov`) resolve correctly.

## S12 — Reproducibility recipe

| Claim | State | ✓ |
|---|---|---|
| "trajectories = 20, levels = 4, seed = 42" | present, and agrees with paper §4.3 "20 trajectories at 4 grid levels" | ✓ |
| the Docker image tag is fixed for the entire 1,280-run sweep | present | ✓ |
| second host: "AMD Ryzen 5 CPU running Linux under WSL2" — a different CPU vendor and OS | present | ✓ |
| flags "matched on 1,280/1,280 runs" | present | ✓ |
| residual float difference ~10⁻¹⁴ | present | ✓ |
| pilot reproduction bit-identical, max\|Δ\| = 0 | present | ✓ |
| ARM reproduction explicitly **not** bit-identical | present — the caveat is stated, not glossed | ✓ |
| sweep size follows from the sampler settings | 20 trajectories × (7 + 1) = 160 per cell; 160 × 8 = **1,280** | ✓ |

## S13 — SHAP cross-verification

| Claim | Re-derived | ✓ |
|---|---|---|
| "530 of 1,280 runs" fire `not_steady_state` | `cell_flag_summary.csv` sums to **530** | ✓ |
| "17 of 18 pooled cases agree" | ledger `T2.s023.pooled` = 17 | ✓ |
| "23 of 48 per-cell at full 3-of-3" | ledger `T2.s023.fullmatch` = 23 | ✓ |
| "92 % … (44 of 48)" | 44 / 48 = 91.67 % → 92; ledger `T2.s023.ge2_pct` declares 92, computes 91.67 | ✓ |

## S14 — Pointer to the companion monograph

The §S17-adjacent record rewritten in the 2026-07-29 readability pass; its
`sec:s2` reference resolves.

## S15 — Compensatory tachycardia

**Re-derived from the raw sweep parquet on the population the section itself
names** — "all clean Morris runs (those passing the four-flag steady-state
classifier without firing `diverged`, `implausible`, or `not_steady_state`)",
which is **663 rows**, matching ledger `T1.28`:

| Scenario | n | Supplement | Re-derived (ddof = 1) | ✓ |
|---|---:|---|---|---|
| S1 healthy | 91 | 73.8 ± 20.4 | **73.77 ± 20.41** | ✓ |
| S2 mild | 179 | 87.3 ± 24.3 | **87.33 ± 24.30** | ✓ |
| S3 moderate | 266 | 155.7 ± 34.7 | **155.72 ± 34.67** | ✓ |
| S4 severe | 127 | 147.1 ± 31.8 | **147.06 ± 31.78** | ✓ |

The four cell counts sum to 663 and match `cell_flag_summary.csv` per scenario
(91 = 42 + 49, 179 = 92 + 87, 266 = 122 + 144, 127 = 60 + 67).

Every prose claim in the section checked against those same numbers:

- "settles output HR near a physiological norm of approximately 74 bpm" →
  S1 = 73.77 ✓
- "drive output HR into the 145–160 bpm range" → 155.7 and 147.1, both inside ✓
- "approximately 70 bpm sympathetic overshoot above the [50, 110] midpoint" →
  +75.7 (S3) and +67.1 (S4) above 80 ✓
- "output HR peaks at S3 (moderate) and eases at S4 (severe)" → 155.7 > 147.1,
  non-monotonic exactly as stated ✓

## S16 — Output stability across the 120-second window

All six drift percentages re-derived by `T5.window.*` ledger anchors: hyperoxia
arm HR **2.6** (2.564), MAP **0** (0), PaCO₂ **3.6** (3.59); Vt-oscillation arm
HR **2.3** (2.31), MAP **0.7** (0.6601), PaCO₂ **2.0** (1.98). Plus PaO₂ 19.5 %
(`T2.f003.drift_exceed_v381`, computes 19.49) and Vt 8.7 %.

## S17 — Summary of supplementary findings

Sixteen cross-references, the densest in either document; all sixteen resolve to
the section they name.

---

# Supplement tally

| Batch | passed | failed |
|---|---:|---:|
| `supp_tables_verify.py` (S3 bounds, S3 drift, S6) | 24 | 0 |
| `supp_tables_verify3.py` (S4, S5, S7, S9, S13) | 41 | 0 |
| `supp_tables_verify4.py` (S2, S12, S15) | 27 | 0 |
| **total** | **92** | **0** |

Plus the four S15 prose claims checked in `s15_clean.py`, and the
cross-reference layer (**67 `\ref` in `supplement.tex`, 161 across both
documents, 0 unresolved, 0 document mismatches**).

**Nothing in `supplement.tex` was modified during this pass.**

# A fourth false alarm, and what the four have in common

`supp_tables_verify4.py` first reported all four S15 rows as mismatches, because
it aggregated every non-null row instead of the clean subset the section
explicitly names. Two more came from a `num()` helper that stripped LaTeX braces
*before* the thousands separator, turning `\textbf{1{,}280}` into `1`. And one
from a marker written with plain underscores where the source escapes them.

All four false alarms in this pass — including the two in the paper phase — are
the same failure: **the test disagreed with the document about what was being
measured**, not the document with the data. None of them was ever a defect in
the manuscripts. Every "FAIL" was traced to its cause before being written down,
which is the only reason none of them reached this register as a finding.

---

# Status

- Layer 4, cross-references: **complete for both documents**, 0 defects.
- `paper.tex`: **all 16 units closed** (2026-08-01).
- `supplement.tex`: **all 17 sections closed** (2026-08-01).
- Machine baseline re-confirmed after this session's two mechanical edits
  (`supplement.tex` header comment, `paper.bib` PMID): **289 / 289 · 97 / 97 ·
  26 / 26, exit 0.**

---

## Addendum 2026-08-03 — F-7: the PaO2 upper bound, checked against the sweep's own data

Opened while re-verifying the Results §2.1 sentence on the 600 mmHg PaO2
bound. **Nothing was modified in the manuscript. Two decisions are pending
with the author.**

### What was verified and holds

| Claim | Status | Evidence |
|---|---|---|
| 663 mmHg is the alveolar-gas-equation value at FiO2 = 1.0 | **CONFIRMED** | StatPearls, *Alveolar Gas Equation* (NCBI Bookshelf NBK482268), verbatim: "For 100% oxygen: PAO2 = [(760 − 47) × 1] − (40 / 0.8) = 663 mm Hg". Deranged Physiology (CICM primary, chapter 134) tabulates 662 at FiO2 100 %. The preregistration's own anchor (West & Luks 2020 Ch.5) is consistent. **Do not change 663.** |
| 34 runs exceed the 600 mmHg bound | **CONFIRMED** | `data/runs/full_sweep/aggregated.parquet`, `PaO2_mean > 600` = 34. Matches §2.4 exactly. |
| §2.4's "91 % at FiO2 >= 0.95" | **CONFIRMED** | 31 of 34 = 91.2 %. The 3 remaining are all S1_F at FiO2 = 0.7367. |

### F-7a — OVERCLAIM in Results §2.1 (not corrected, pending decision)

Current text: *"at FiO2 = 1.0 a healthy lung's PaO2 can legitimately climb
toward the alveolar-gas-equation ceiling of ≈663 mmHg, so **real values
between 600 and 663 mmHg occur**."*

663 is the **alveolar** value; arterial PaO2 sits below it by the A-a
difference. StatPearls NBK482268, verbatim: "A-a gradient typically increases
by 5 to 7 mm Hg for every 10% increase in FiO2". For an 18-year-old
(room-air normal (18+10)/4 ≈ 7 mmHg), FiO2 0.21 → 1.0 gives A-a ≈ 47–62 mmHg,
so arterial PaO2 ≈ 600–616 mmHg; the commonly quoted "up to 100 mmHg on 100 %
O2" gives ≈ 563. The sentence's range is therefore the optimistic edge of the
literature at best, and is stated as fact.

A replacement of the form "real values between 600 and ~650 occur" was
drafted and **rejected on the same grounds** — equally unsupported.

⚠️ Discarded source: a web search attributed "PaO2 587 mmHg in a healthy
subject after 20 min on 100 % O2" to PMC5587703. The article was opened: it
is a study of **anesthetized pigs**, PaO2 120–161 mmHg, no human 100 % O2
data. The number does not exist in that source and must not be cited.

### F-7b — the per-run alveolar ceiling is not flat (not corrected, pending)

663 is the ceiling **at FiO2 = 1.0 and PaCO2 = 40 only**. The sweep varies
both. Computing each run's own ceiling, FiO2 × (760 − 47) − PaCO2/0.8:

- 15 of 1,280 runs have `PaO2_mean` > 663; 2 exceed 700.
- **5 runs exceed their own per-run ceiling**, three of them grossly: S1_F at
  FiO2 = 0.7367 with PaO2 means of 845.0, 722.9 and 678.6 against a ceiling
  of ≈505 mmHg (excess +339, +216, +174). All five are flagged both
  `implausible` and `not_steady_state`.
- The other two (FiO2 = 1.0, PaO2 688.7 and 688.3 vs ceiling ≈683) exceed by
  ~5 mmHg, within model noise.

Caveat that keeps this from being a proven physics violation: all three large
cases are `not_steady_state`, and the alveolar gas equation is a
steady-state relation. A window mean of a signal that is still climbing is
not a steady state, so the equation does not strictly bind it.

**Already disclosed, and correctly:** Supplement §S3-pao2-sensitivity
identifies the two runs above 700 as "a genuine numerical runaway ... climbing
to a physically impossible plateau above the 760 mmHg sea-level barometric
pressure", and §S9 reports 6 of 44 extended reruns developing unphysical
plateaus above 700 mmHg. The engine's high-FiO2 misbehaviour is not a new
finding.

**What is new:** the F-003 supplementary reclassification raises the bound to
a **flat** 700 mmHg, a value derived at FiO2 = 1.0. Applied to the third
S1_F run (FiO2 = 0.7367, PaO2 678.6), that flat bound declares
"physiologically clean" a value 174 mmHg above what its own FiO2 permits. It
is one of the 32 runs the supplement reports as reclassified. An FiO2-aware
ceiling would keep it flagged. One sentence in §S3-pao2-sensitivity would
close this.

### F-7c — under-hedge in §2.4 (not corrected, pending)

Current text: the ≈20 mmHg gap between the converged S1 plateau (643 mmHg)
and 663 *"is consistent with Pulse's modelled alveolar-arterial difference
rather than an oxygenation defect, which would be expected to push PaO2 above
the theoretical ceiling, not below it."*

Staying below the ceiling rules out a **runaway**, not an **offset**. Pulse's
implied A-a difference at FiO2 = 1.0 is ≈20 mmHg against the ≈47–62 mmHg the
5–7 mmHg-per-10 %-FiO2 rule predicts, i.e. 2–3× smaller: the engine reads
high at high FiO2. Consistent with verified Pulse limitation #9 (no regional
V/Q mismatch; five-compartment lumped model).

Fair caveat, to be stated if this is written up: these runs are mechanically
ventilated with PEEP, which limits the shunt that widens the A-a difference
in a spontaneously breathing subject, so the comparison is not
like-for-like.

---

## Addendum 2026-08-03 — F-8: the pulse-pressure clip, re-examined after an external critique

An external methodological critique of the Morris design was brought in for
assessment. Every figure it cited (35 clipped points, 9/20 shortened diastolic
steps, 0.83 mmHg, 8 contaminated SBP steps, 41/78 and 19/68 clean pairs, mu*
factor 2.4 / 15.4, DBP entering the top three in 9 further combinations) proved
to be **verbatim from `supplement.tex` S3.7 itself**. The critique reproduced
the paper's own disclosure; it did not find anything the paper had not already
published. Recorded here because that fact is the useful signal: the disclosure
is legible enough to be mistaken for an external discovery.

### F-8a — CONFIRMED, and the paper was already right

Independent re-derivation from the Morris grid, done by hand *before* running
any code (SBP levels 90/100/110/120 -> ratio caps 67.5/75/82.5/90; DBP levels
60/66.67/73.33/80), reproduced all five structural counts exactly: 35/160,
9/20, the 5x6.25% / 1x56.25% / 3x62.5% split, 8/140, 123/140. A separate
pair-matching pass against `aggregated.parquet` independently returned
37 full + 17 partial + 24 shortest = 78 clean diastolic pairs, of which 41
shortened — matching the anchored 41/78. Three independent instruments, no
disagreement. **Nothing in S3.7's arithmetic required correction.**

### F-8b — the critique's proposed remedy is arithmetically worse — REJECTED

The critique proposed reparametrising to SBP + pulse pressure as
"intrinsically valid". Measured against Pulse's three gates
(SBP <= 120, DBP <= 80, DBP <= 0.75*SBP), the feasible region is a polygon with
an oblique edge covering 17.4 % of the preregistered box; no rectangle covers
it. Grid evaluation of the proposal:

| candidate | infeasible | which gate breaks | implied DBP span |
|---|---|---|---|
| PP in [30,50] | 8.3 % | DBP > 80 (100 %) | [40, 90] |
| PP in [25,45] | **19.4 %** (worse than now) | DBP > 80 | [45, 95] |
| PP in [30,60] | 5.6 % | DBP > 80 | [30, 90] |

DBP > 80 is Pulse's *loud* gate (`[ERROR]` + exit 1), so the proposal trades
shortened steps for dead runs plus a DBP range outside preregistration.
Separately, the applied-step recomputation the critique asked for repairs only
the denominator: the 8 contaminated SBP steps stay contaminated under either
estimator. No re-run was warranted and none was performed.

### F-8c — the supplement's *justification* was too strong — CORRECTED

S3.7 justified keeping the nominal estimator with "dividing by steps as small
as 6.25 % of nominal amplifies output noise, so it measures the distortion
rather than correcting it". Tested and **not supported as a general claim**.
For MAP the engine's proportional response is flat across step sizes
(median observed/predicted 1.289 at 13.33 mmHg, 1.334 at 7.5-8.33 mmHg,
1.379 at 0.83 mmHg; sign agreement 100 / 100 / 95.8 %), i.e. it resolves a
0.83 mmHg step cleanly. Corrected in `supplement.tex` S3.7 and
`preprint/manuscript.md` on 2026-08-03, replacing the unprovable noise
mechanism with three structural facts (persistent OAT violation; variable
effective step 0.83-13.33 mmHg is not a fixed-step Morris design; step length
confounded with systolic setting). New anchors `T5.clip.dbp_full_steps`,
`T5.clip.smallest_step_sbp`, `T5.clip.full_step_sbp_min` (ledger 289 -> 292).

### F-8d — a six-output robustness table was drafted and DISCARDED

A per-output step-scaling table (ratio of median |dy| at 13.33 mmHg to that at
0.83 mmHg; 16 = proportional response, 1 = none) was drafted for S3.7 and then
withdrawn as not publishable. Two defects, both found before publication:

1. **Pseudo-replication.** The 24 and 37 "pairs" are 5 and 11 *distinct* Morris
   steps replicated across 8 cells. Recomputing per cell moves four of the six
   ratios by factors of 2-4 (SpO2 14.9 pooled -> 3.6 per cell; PaO2 16.3 -> 28.1;
   HR spans 1.45-52.13 across cells). Only 3 of 8 cells hold enough clean pairs
   in both buckets to yield a ratio at all. The cell mix differs between buckets
   (S4_M: 7 full vs 1 shortest; S1_F: 1 vs 3), so the pooled medians compare
   severities, not step sizes — an aggregation artefact.
2. **Total confounding.** The 0.83 mmHg steps occur *only* at SBP = 90 and the
   full-length steps *only* at SBP >= 100. This is structural, not sampling
   luck: at SBP = 90 the cap is 67.5 mmHg, so no full-length diastolic step can
   exist there. Step size and location can never be separated in this design.

Only MAP survived both checks (pooled 15.0, per-cell 15.6, range 13.6-15.7,
expected 16) and it is the output whose ground truth is known a priori through
its arithmetic coupling to DBP — so it serves as an internal positive control,
not as a result. **Positive-control statement, for internal use only:** MAP
response scaled consistently with the applied DBP step across cells, indicating
numerical resolution of the smallest pressure perturbation; this does not
identify step-size effects for the other outputs, because DBP step size and SBP
location do not overlap. Deliberately kept out of the manuscript: it would add
a post-hoc analysis that the estimator choice does not need, and would reopen
F-8e below.

### F-8e — LEAD, not a finding: Pulse's MAP versus the configuration formula

Pulse's achieved MAP departs from `DBP + (SBP - DBP)/3` applied to the
requested pressures by a median of +14.3 mmHg (IQR 9.8-19.4, max 27.2, n = 663
clean runs), and the gap scales with severity: S1 +6.3, S2 +9.9, S3 +18.5,
S4 +19.2. **Not attributable with the aggregated data**, which record MAP but
not the achieved SBP/DBP. At least four readings remain open: a coherent
dynamic cardiovascular response; a gap between initial targets and realised
pressures; the one-third formula's known approximation as diastole shortens;
or an internal Pulse anomaly. Settling it needs SBP, DBP, MAP and HR recorded
together, with MAP ideally integrated over the pressure waveform. It does not
affect the elementary effects, which are differential and were shown above to
track the applied step correctly. Deferred to the monograph or Paper 2.
