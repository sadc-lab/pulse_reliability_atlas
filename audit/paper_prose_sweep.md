# Paper prose sweep — `preprint_npj/paper.tex`

Companion to `audit/supplement_prose_sweep.md`, which covered §S1–§S17 of the
supplement and closed at 30 signals. This register covers the **main manuscript**
by the same method, and adds a fourth question dedicated to paper↔supplement
coherence.

**Started 2026-08-23. No manuscript edit is made during this sweep.** Signals are
recorded and left for a later, separate correction pass.

---

## ▶▶ COMBINED STATE — refreshed 2026-08-23, after the visual pass and citation pass 1

⚠️ **This block was stale for several hours** — it still read "35 signals, 34
open" while the registers had reached 43. That is the exact defect this audit
diagnoses elsewhere: a summary shorter than the truth it summarises. It is
refreshed here, and **must be refreshed with every batch**, or this register
becomes what it criticises.

| | signals |
|---|---|
| supplement (`audit/supplement_prose_sweep.md`), ids 1–38 | **38** |
| paper (this file), P-1 … P-5 | **5** |
| **total** | **43 — 39 open, 4 off the table** |

**Verified by enumeration, not by regex**: supplement ids 1–38 with no gaps,
paper P-1…P-5. The class partition below was checked for completeness and
overlap — 43 assigned, 43 distinct, no duplicate, none missing, none extra.

**By class:**

- **Scientific — a claim outruns its evidence (6):** 17 (what the alveolar-gas
  equation predicts) · 24 ("the underlying physiology is real") · 28 (the S3→S4
  dip and its survivorship confound) · **38** (sex-balanced flattens a
  sign-reversing effect) · **P-2** (Berlin vs PALICC-2) · **P-4** (cross-output
  μ\*).
- **Factual, established, cheap to repair (17):** 5, 8, 11, 12, 18, 19, 21, 26,
  27, 30, **31** (the fresh-clone recipe cannot run), **33** (313/313 pinned in a
  live criterion), **34** (S001…S031 where the log reaches S032), **35**
  ("detector" baked into the Figure S5 legend), **37** (34 at FiO₂ = 1.0), **P-1**,
  **P-3**.
- **Arbitrated against a source, repair still to write (4):** **1** (four
  sub-claims: 2 supported, 1 source-insufficient, 1 overclaimed) · **20**
  (escalated — the Pulse docs *do* carry the rule) · **23** (SUPPORTED; bound the
  unbounded negative) · **P-5** (source-insufficient universal, but the BioGears
  half is now citable).
- **Low, legibility or cosmetic (13):** 3, 4, 6, 7, 9, 13, 14, 15, 16, 22, 25,
  29, **36** (running-title case).
- **Off the table (3):** 2 closed · 10 resolved from the source · 32 withdrawn as
  my error.

**Nothing has been corrected in any manuscript.**

**Where the paper is the model, not the patient** — repairs should copy it:
signal 13 → §2.3's median of paired differences; signals 21, 22(a), 29 → Table 1;
signal 26 → the Data-availability statement's "consolidates"; signal 37 →
`supplement.tex:339`, which carries the full 34/31/32/2 decomposition.

⚠️ **Paragraph totals are deliberately absent**, because they are
instrument-dependent and were mis-stated once: three rules give 193, 281 and 253
for the same supplement, and the paper gives 120 whole-file against 112 body-only
under one rule. A first version summed a body count and a whole-file count as
"305 paragraphs". **Coverage is the claim, and it is complete** — §S1 through
§S17, abstract through back matter, and all 14 figures inspected as images.

---

## ▶ SUMMARY — read this first (sweep complete, 2026-08-23)

**Every section swept**, abstract through back matter, including both tables of
the Results opening, all six Results subsections, the fourteen Discussion
paragraphs, all seven Methods subsections and the back matter. **5 signals.** No
manuscript edit made; nothing pushed.

⚠️ See the paragraph-count caveat above: the "112" quoted while this sweep was
running is the body-only count under a >120-character rule, and it is not
comparable to the supplement's figure. Coverage, not the count, is the claim.

| # | locus | one line | class |
|---|---|---|---|
| **P-4** | `paper.tex:289` | Cross-output μ\* comparisons are unit artifacts, and **§4.6 licenses comparability across inputs only** | **established (a) + interpretation to arbitrate (b)** |
| **P-2** | monograph L44, L954 | Severity bands credited to **PALICC-2** where the same document says Berlin "not on PALICC-2" | **established — contradiction, monograph-only** |
| **P-3** | `paper.tex:187` | `not_steady_state` defined with 2 triggers; Table 2 gives 3, and the omitted one is the largest | **established — internal** |
| **P-1** | `paper.tex:359` | Five severities called an illustrative "convention"; the source shows hard-coded calibration nodes | **established — understates the paper's own finding** |
| **P-5** | `paper.tex:372` | "No comparable open atlas yet exists" for BioGears/HumMod — unsourced, unhedged | **needs investigation — citation trigger (b)** |

**The two that matter scientifically** are P-4 (a comparison the paper's own
Methods does not license, with a recoverable mechanism claim) and P-2 (an
adult-vs-pediatric definition mix-up that pediatric intensivist reviewers will
see). P-3 and P-1 are precise and cheap to repair. P-5 needs a source or a hedge.

**Awaiting a decision before any edit:** all five, plus the 29 open supplement
signals. Nothing has been corrected.

**Three findings that run the other way** — places where the paper is the
*better-stated* document and should be the model for repairing the supplement:

1. §2.3 uses the **median of paired differences** (0.325724) where §S8 ¶665 is
   ambiguous → supplement **signal 13** should follow the paper.
2. Table 1 states "160 simulations per cell" and "the four failure flags"
   correctly → supplement **signals 21, 22(a), 29** are localised, not systemic.
3. The Data-availability statement says the monograph "**consolidates**" the
   lab-notebook entries — the weaker, accurate verb that supplement **signal 26**
   finds missing from §S14 ¶939's "carries".

**Two things recorded that are not signals:**

- ⚠️ **`CLAUDE.md` misstates a preregistered threshold** — it summarises the Sobol
  trigger as σ/μ\* > 0.5 where `preregistration.md:168` says ≥ 0.6. The paper is
  right; the instruction file is wrong, and it nearly caused a false signal.
- 🔜 **Deferred, already dated elsewhere**: `paper.tex:460` says "**the**
  supervisor-review phase" and "the **final** rounds". Both become false once the
  second supervisor round happens.

**Not verified, and marked rather than assumed**: `paper.tex:388`'s "applied DBP
to co-vary in **8 of 20** SBP steps" (its 9/20 companion is a ledger anchor; this
one is not, and was not measured).

---

## Method

Four questions per paragraph:

1. **Internal contradiction** — does the paragraph contradict something else in
   `paper.tex`?
2. **External contradiction** — does it contradict the supplement, the monograph,
   a table, or a figure?
3. **A claim that outruns the data** — is the assertion stronger than what was
   measured?
4. **An unusual fact or figure** — anything a reader would stop on, re-derived
   from its source.

Citations are **not opened** in this pass. A sentence is marked for the later
citation pass when it meets one of four triggers: (a) it attributes a specific
number or result to a source; (b) it asserts an absence, exclusivity or negation;
(c) it uses quotation marks or presents itself as a close paraphrase; (d) the
reference carries a conceptual distinction the argument depends on.

## Population, measured before starting

**112 prose paragraphs, ~15,000 words**, from `\abstract` through the back
matter. For comparison the supplement, already swept, holds 193 paragraphs and
18,080 words — so the paper is 57 % of it in paragraphs but 84 % in words. Its
paragraphs are denser.

⚠️ **Segmentation caveat, recorded before any per-section statistic is used.** A
first pass matched only lines *beginning* with `\section`/`\subsection`/`\bmhead`
and so mis-attributed two blocks: `Data availability` (L473) and `Code
availability` (L477) both begin with `\hypertarget{...}{}` and were folded into
*Use of AI tools*. **The 112 total is unaffected**; the per-section breakdown is
not to be quoted until re-attributed.

## Reserved zone — read, never modified

`Acknowledgements` (L481), `Author contributions` (L486), `Competing interests`
(L490), `Ethics approval` (L494), and anything concerning funding. These are the
author's exclusive domain. They are read for contradictions like everything else;
anything found is recorded **with no proposed action**.

---

## Signals

| # | locus | signal | status |
|---|---|---|---|
| P-1 | `paper.tex:359` vs `:146` and §S5-mapping | The five ARDS severities are called an illustrative "round-tenths **convention**" at L359 and "five **calibration nodes**" at L146. The source says calibration nodes. | **OPEN — understates, and understates the paper's own finding** |
| P-5 | `paper.tex:372` | "**No comparable open atlas yet exists** for … BioGears … or HumMod" | ⚠️ **SOURCE INSUFFICIENT for the universal form 2026-08-23** — but the **BioGears half is now anchorable to a primary source** |
| P-4 | `paper.tex:289` | Two cross-output μ\* magnitude comparisons. μ\* carries its output's unit, and SpO₂ is on the 0–1 fractional scale: converted to percentage points its **median μ\* (1.66) exceeds MAP's (0.84) and PaCO₂'s (1.23)**, reversing "smallest overall". | **OPEN — the causal explanation rests on a unit artifact** |
| P-3 | `paper.tex:187` vs Table 2 (`:216`) | `not_steady_state` is defined with **two** triggers (drift, variance) fifteen lines before Table 2 gives **three** (flatline, CV, drift). The omitted flatline is the **largest** sub-mode, 232 occurrences. | **OPEN — internal, and it loses the biggest contributor** |
| P-2 | monograph `L44` and `L954` vs `L509` and `L3808` | **XDOCCONFLICT — contradiction.** The severity bands are attributed to **PALICC-2** in the monograph's abstract and scenario list, while the same document states twice that they are anchored on the **Berlin Definition**, "not on PALICC-2". Paper and supplement are clean. | **OPEN — monograph-internal; clinically a category error (adult P/F vs pediatric OI/OSI)** |

### P-1 — "round-tenths convention" versus the source's calibration nodes

Three descriptions of one object:

- `paper.tex:146` — "piecewise-linear functions **calibrated at five nodes**: 0.0,
  0.3, 0.6, 0.9 and 1.0"
- `paper.tex:359` — "Pulse's own methodology … **exemplifies the range with the
  round-tenths convention** {0.0, 0.3, 0.6, 0.9, 1.0}"
- supplement §S5-mapping — "linear interpolations of the hard-coded source
  **calibration nodes**"

**Primary source, opened this session.**
`RespiratoryModel.cpp:3724–3731` in the local Pulse clone:

```cpp
std::vector<std::pair<double, double>> interpolatorPoints =
{
  {0.0,  1.0}, //None
  {0.3, 10.0}, //Mild
  {0.6, 15.0}, //Moderate
  {0.9, 20.0}, //Severe
  {1.0, 25.0}  //Max
};
```

Five hard-coded interpolation nodes at exactly those severities, carrying the
engine's own labels. L146 and the supplement are right; **L359's "convention" is
the outlier**.

**Why the correction strengthens the paper rather than weakening it.** L359's
argument is that published Pulse work "sample[s] at most up to severity 0.9 and
do[es] not examine impairment fractions inside the interval 0.91--0.945". If the
round tenths are merely an illustrative convention, that gap is a sampling
oversight. If they are the *calibration grid*, then everything between two nodes
is uncalibrated interpolation by construction — which is a far stronger reason to
characterise 0.91--0.945.

**Triple confirmation obtained while checking, of §S5-mapping's resistance
table.** The three published multipliers reproduce exactly from these nodes:

| scenario | severity | interpolation | published |
|---|---|---|---|
| S2 | 0.26 | 1.0 + (0.26/0.3) × 9.0 = **8.8** | 8.8× ✓ |
| S3 | 0.60 | exact node = **15.0** | 15× ✓ |
| S4 | 0.95 | 20 + (0.05/0.1) × 5 = **22.5** | 22.5× ✓ |

### P-4 — cross-output μ\* comparisons are unit artifacts (¶289)

> SpO$_2$ shows the smallest $\mu^{*}$ magnitudes overall **because** the output
> sits at the hemoglobin-saturation ceiling across most of the swept range.

μ\* carries the unit of its output. Measured over `morris_indices.parquet`:

| output | median μ\* | max μ\* | unit |
|---|---|---|---|
| SpO₂ | 0.0166 | 0.1247 | **fraction, 0–1** |
| MAP | 0.8435 | 20.25 | mmHg |
| PaCO₂ | 1.2330 | 20.02 | mmHg |
| HR | 3.2906 | 95.12 | bpm |
| PaO₂ | 9.6704 | 146.69 | mmHg |
| Vt | 1.7250 | **503.05** | mL |

**Convert SpO₂ to percentage points — the scale Figure 3's own caption says a
reader should use — and the ordering reverses.** Its median μ\* becomes **1.66
pp**, which is *larger* than MAP's 0.84 and larger than PaCO₂'s 1.23. "Smallest
magnitudes overall" holds only on the fractional scale.

The ceiling effect is probably real; SpO₂ does saturate. **But the evidence
offered does not establish it** — the observation it rests on is an artifact of
the unit, and the paper knows this elsewhere: the Figure 3 caption states "For
SpO$_2$, $\mu^{*}$ is expressed on the fractional scale reported by Pulse (0--1),
so 0.12 corresponds to 12 percentage points."

**Second instance, same paragraph, same class**: "Output Vt tracks input Vt at
far higher $\mu^{*}$ magnitudes than any other input--output pair". Vt is in mL,
where 503 is an ordinary number; PaO₂'s 147 mmHg is not a smaller *effect*, it is
a different quantity. Comparing μ\* across outputs of different physical
dimension has no scale-free meaning.

**What is untouched.** Every *within-output* statement in §2.2 is sound, and
that is where the paper's actual claims live: top-3 fractions are dimensionless
ratios, so the 48/48, the median 0.928 and the 0.658–0.998 range are all immune
to this.

#### P-4 in three levels

**(a) Established defect.** A cross-output μ\* magnitude ranking is not
interpretable. It is not merely that the ordering happens to hold on the
fractional scale — mmHg→kPa would divide PaO₂'s numbers by 7.5 and mL→L would
divide Vt's by 1,000, with no change to the model. The superlative has no
unit-free meaning.

**(b) The mechanism is recoverable — by different evidence.** A *within-SpO₂*
analysis does support ceiling compression. Per cell, summed μ\* against the
clean-run mean saturation:

| cell | Σμ\* (SpO₂) | mean SpO₂ | share ≥ 0.99 |
|---|---|---|---|
| S1_F | 0.0103 | 0.9833 | 50.0 % |
| S1_M | 0.0409 | 0.9757 | 51.0 % |
| S2_F | 0.1751 | 0.9680 | 34.8 % |
| S2_M | 0.2317 | 0.9555 | 25.3 % |
| S3_F | 0.2755 | 0.9300 | 18.0 % |
| S4_F | 0.1354 | 0.9223 | 0 % |
| S3_M | 0.3179 | 0.9164 | 11.1 % |
| S4_M | 0.2507 | 0.9060 | 0 % |

Spearman ρ = **−0.762** against mean saturation, **−0.587** against the share at
the ceiling. And the ordering holds **within every scenario**: in all four, the
cell with the higher mean SpO₂ carries the lower Σμ\*.

**(c) ⚠️ Why that is still only an association, and the design cannot fix it.**
The within-scenario contrast looks like it removes the severity confound. It does
not: with 8 cells structured as 4 severities × 2 sexes, **the only contrast at
constant severity is the sex contrast**, and in all four pairs it is the female
cell that carries both the higher saturation and the lower μ\*. So saturation
level is never varied independently of either severity or sex. n = 8, no formal
test, descriptive only.

**Consequence for the correction pass.** The mechanism claim survives if it is
scoped within SpO₂ and stated as an association — e.g. "within SpO₂, sensitivity
was lowest in the cells with the highest mean saturation, consistent with
compression near the saturation ceiling". The cross-output superlative and the
word "because" do not survive.

**XDOCCONFLICT scan — provisionally negative.** No other locus in the three
documents makes a cross-output μ\* magnitude comparison. The other μ\* comparisons
found are **within-output and therefore dimensionless**: the "smallest SBP-to-DBP
μ\* ratio was 1.22" appearing at `paper.tex:388`, `supplement.tex:298` and
monograph L897, and the monograph's L1738 ordering of inputs within each output.
⚠️ The net was lexical (`smallest|largest|far higher|magnitudes overall|than any
other`) and was calibrated on the known locus, which it recovered — but it is
narrow, so "isolated to `paper.tex:289`" is a provisional finding, not proof of
absence.

### P-3 — `not_steady_state` has three triggers; ¶187 names two

Fifteen lines apart, inside one subsection:

- **¶187** — "`not_steady_state` flags a run that never settled: over its final
  60-second measurement window the output is still trending (*drift*) or still
  oscillating (*variance*)". **Two** triggers.
- **Table 2 (L216)** — "at least one tracked output **flatlines at a hard bound**
  (frozen with near-zero variation), **varies too much** (coefficient of
  variation > 0.05; most often tidal volume), or **drifts** past its locked
  per-channel limit". **Three**, in the classifier's own evaluation order.

The omitted trigger is **the largest**. The ledger anchor
`T1.30n.spo2_flatline` puts SpO₂ flatline at **232** exhaustive occurrences,
against 303 for the Vt CV trigger and 133 for Vt drift. A reader who takes ¶187's
definition cannot account for the biggest single sub-mode of the flag, and §S4 of
the supplement decomposes the 530 into exactly those three.

Same family as supplement signals 22(a) and 29 — an enumeration that loses a
member — but here the lost member carries real weight rather than none.

### P-2 — Berlin Definition or PALICC-2? The monograph answers both ways

**Found from the paper side**, checking `paper.tex:150` ("calibrated so that …
Pulse's arterial PaO₂/FiO₂ falls in the matching **Berlin Definition** band")
against this project's own `CLAUDE.md`, whose scenario table reads "S2 | 0.26 |
Mild ARDS (**PALICC-2**)".

**Counts, all three documents:**

| document | "Berlin" | "PALICC" |
|---|---|---|
| `paper.tex` | 5 | **0** |
| `supplement.tex` | 13 | **0** |
| `manuscript.md` | 20 | **9** |

**Paper and supplement are clean and mutually consistent** — Berlin only.

**The monograph contradicts itself**, and its own correction is the better half:

- ✅ L509 — "Scenarios … **calibrated on the Berlin Definition's PaO₂/FiO₂
  bands**. PALICC-2 … is cited as the **parallel pediatric** severity framework;
  note that PALICC-2 itself favours Oxygenation Index (OI) / Oxygen Saturation
  Index (OSI) **over P/F**."
- ✅ L3808 — "The atlas's adult scenarios S2 (0.26), S3 (0.60), S4 (0.95) are
  anchored on the Berlin Definition P/F bands, calibrated empirically at
  ARDSnet-protective ventilation (Appendix B.3) — **not on PALICC-2**."
- ⚠️ **L44, the monograph's own abstract** — "three ARDS severities, **spanning
  PALICC-2 mild–severe**".
- ⚠️ **L954, the scenario list** — "**S2** Mild ARDS, impairment 0.26 (**PALICC-2
  mild**)".

**Why this is not cosmetic.** Berlin is the **adult** definition and grades on
PaO₂/FiO₂; PALICC-2 is the **pediatric** one and, as the monograph itself notes,
grades on OI/OSI rather than P/F. Attributing a P/F-calibrated adult scenario to
a pediatric OI-based framework is a category error, and three of the four
supervising reviewers are pediatric intensivists.

**Supporting measurement already in the monograph**: impairment {0.26, 0.60,
0.95} lands P/F ≈ **256 / 150 / 96 mmHg** (L239), which sits in Berlin mild
(200–300), moderate (100–200) and severe (≤100) respectively. The calibration is
unambiguously Berlin.

**XDOCCONFLICT state: `contradiction`** — but scoped to the monograph. No action
proposed on the paper or supplement, which say the right thing.

---

## Swept so far

### Abstract (L128) — no signal

Every quantity re-derived or already anchored: seven inputs, four scenarios, two
bodies, 1,280 simulations; median 93 % top-three share; the four flags named in
full; "two operator-actionable, a third sex-dependent", consistent with L154,
L332 and L368 and with the monograph; 20.6 % Vt instability (= 264/1,280,
reproduced); the −2 cmH₂O lever; median 643 mmHg at 300 s (reproduced as 642.87
over the 41 drift-converged runs); 20/1,280 divergences all male; the 4,082 mL
floor (4,082.24 rounded).

### Introduction ¶140–146 — one signal (P-1)

Verified: "actively maintained" rather than any citation-count claim — the
formulation this project settled on; the 0.02 s / 50 Hz timestep, confirmed
directly against a native Pulse CSV today; the five-compartment lung, matching
verified limitation #9; the Cornish channels described as "concentrated on …
largely outside", which is the softened wording an earlier audit asked for and
which is now in place at both loci.

### Results, Table 1 (glossary) and Table 2 (flag definitions) — no signal

**Table 1 independently confirms the scoping of three supplement signals**, by
stating correctly what those loci state wrongly:

- "The mild/moderate/severe labels are **Berlin Definition bands**" — unambiguous,
  which is what makes P-2 a monograph-only conflict.
- "20 trajectories per cell yield 20 × 8 = **160 simulations per cell**" — the
  right unit, so supplement signal 21 is localised to `paper.tex:402` and
  `supplement.tex:884` rather than being a general confusion.
- "neither fired any of the **four** failure flags" — four, so supplement signals
  22(a) and 29 are localised too.

Verified in Table 1: the Morris step of "**two-thirds** of that input's swept
range" is exactly Δ = p/(2(p−1)) = 4/6 for the p = 4 grid, and it checks against
the data — HR spans [50, 110] = 60 bpm, so Δ = 40 bpm, exactly two intervals of
the measured four-level grid {50, 70, 90, 110}.

### Results ¶187–193 — one signal (P-3), everything else exact

| claim | measured |
|---|---|
| "10{,}160 input contracts that reached ingestion" | `input_instantiation_long.csv` holds **10,240** rows = 1,280 runs × **8** contracts each (min = max = 8); 10,240 − 80 = **10,160** ✓ |
| "The remaining 80 ventilator contracts belong to 20 runs" | 20 × 4 ventilator fields = **80** ✓ |
| "divergence occurs on 20 runs spread across all four scenarios, including the healthy baseline and both sub-severe ARDS settings" | **S1 4, S2 4, S3 4, S4 8**, total 20, **all four scenarios** ✓ |
| "All 20 fall on the male reference body" | 20/20 male ✓ |
| "PaO₂ upper bound of 600 mmHg … set below the alveolar-gas-equation value of ≈663 mmHg" | 600 < 663 ✓, and 663 re-derived |
| "The four flags are independent presence counts (a single run can fire several)" | matches the project's non-exclusivity rule ✓ |

**Not a signal, checked because it looked like one**: ¶191 uses "detector" three
times. All three are scoped to the *preregistered* object — "its preregistered
operational detector", "That detector reads the setup log", "what that detector
measured" — which is the legitimate use the supplement's signal 3 explicitly
protects. The vocabulary guard passes on every commit, which corroborates it.

### §2.3 VC-AC dyssynchrony — no signal, and more precise than its supplement twin

| claim | measured |
|---|---|
| "median paired Vt CV drop of at least 0.04 (met, **+0.326**)" | **median of the per-pair differences = 0.325724** ✓ |
| "collapses the median Vt CV from 0.351 to 0.016" | 0.350867 → 0.015631 ✓ |
| "S1\_F\_0117 … from 1.826 to 0.018" | **1.825742 → 0.017750** ✓ |
| "50 of the 64 reruns … below 0.05 … (78.1 %)" | 50/64 = 78.125 % ✓ |
| "20.6 % of runs" (Vt oscillation as primary flag) | 264/1,280 ✓ |
| "`SEMechanicalVentilatorVolumeControl.cpp` lines 120--128" | line-exact in the clone ✓ |
| "strongest where the set respiratory rate is high" | share of S1 runs above 0.05 rises monotonically with RR: **8.3 % at RR = 8, 43.4 % at 12, 45.8 % at 16, 58.8 % at 20** ✓ |
| "the single largest source of `not_steady_state` flags" | Vt CV = 303 exhaustive triggers vs SpO₂ flatline 232 and Vt drift 133 ✓ |

💡 **Worth carrying to the correction pass**: §2.3 uses the **median of paired
differences** (0.325724), which is the correct statistic for a paired gate — the
difference of medians is a different number, 0.335236. This is exactly the
distinction supplement signal 13 leaves ambiguous in §S8 ¶665. **The paper is the
better-stated of the two**, so signal 13's repair should follow the paper, not
rewrite it.

Attribution hygiene noted as exemplary: "The dyssynchrony itself is well
documented clinically…~\cite{figueroacasas2016}; the specific conditions that
produce it here … are **our own in-silico finding, not a claim drawn from that
source**."

### §2.4 transient hyperoxia — no signal

| claim | measured |
|---|---|
| "exceeds … 600 mmHg on **34 of the 126** `implausible`-flagged runs" | 126 implausible, **34** with PaO₂ > 600 ✓ |
| "**91 %** of these excursions occur at FiO₂ ≥ 0.95" | **31/34 = 91.18 %** ✓; the other 3 sit at FiO₂ = 0.7367 |
| "60-run longer-rerun experiment" · "41 of 44 (93.2 %)" · "median 643 mmHg" · "≈663 mmHg" · "38 … 95 % … by t = 180 s" · "six … above 700 mmHg, four … near 1,400" · "five of five female, one of five male" | all re-derived under §S9 earlier tonight ✓ |

Bonus reconciliation: the 126 `implausible` runs decompose exactly into **92
SpO₂-driven + 34 PaO₂-driven**.

**Cross-document coherence: consistent.** §2.4 and §S9 agree on population,
protocol and every shared number, and the paper's hedging matches the
supplement's — "It does not establish that the plateau level itself is right,
which would take a validation against measured arterial data and is outside the
scope of a curation map" sits at the same epistemic level as the Figure S5
caption's refusal of external physiological validation.

### §2.5 sex-stratified divergence — no signal, and it is the most solid section swept

Recorded at length because this is the **coupling hotspot**: 15 of the 39
supplement→paper cross-references point at `sec:results-sex`, and 6 more at
`sec:results-secondary`. Rewording it would put twenty-one supplement loci at
risk, so its soundness matters more than most.

**¶338, the divergence signature — six claims, six exact:**

| claim | measured |
|---|---|
| "20 runs (1.6 %) … 4 in each of S1_M, S2_M, S3_M and 8 in S4_M" | 4/4/4/8 = 20, 20/1,280 = 1.5625 % ✓ |
| "zero divergences across the 640 runs on the female body" | 0/640 ✓ |
| "span only **8 distinct operational-input vectors**" | **8** distinct 7-tuples ✓ |
| "4 vectors that diverge in all four male cells and 4 that diverge only in S4_M" | exactly **4 vectors at multiplicity 4** and **4 at multiplicity 1**, the latter all in S4_M ✓ |
| "**16 of the 20** … HR = 50, SBP = 90 … RR = 20" | **16** ✓; the other four sit at HR 90, 90, 90, 110 → "HR 90--110" ✓ |
| "FiO₂ … 1.0 in **13** of the 20 (the other **7** near ≈ 0.74)" | 13 at 1.0, **7 at 0.7367** ✓ |

💡 This paragraph makes the **events-versus-configurations** distinction
explicitly — "supported by 8 distinct input vectors, not by one per divergence
event" — which is the discipline this project's own method notes demand. It is
the cleanest handling of that distinction in either document.

**¶340–342, the blood-volume mechanism:**

- 4,803 / 3,996 mL, ≈71 mL·kg⁻¹, 16.8 %, the 4,082 mL floor and the 86 mL gap —
  all re-derived earlier tonight ✓
- "an intermediate bracket (4,400 mL, an **8.4 %** reduction)" → 402.63/4,802.63
  = **8.383 %** ✓
- **"Nadler's sex-specific equations give 73.0 and 63.8 mL·kg⁻¹" — recomputed by
  hand from the published formulas and both exact.** Male, H = 1.80 m, W = 67.3:
  0.3669(5.832) + 0.03219(67.3) + 0.6041 = 4.910 L → **72.96** → 73.0 ✓. Female,
  H = 1.63 m, W = 56.2: 0.3561(4.3307) + 0.03308(56.2) + 0.1833 = 3.585 L →
  **63.78** → 63.8 ✓. This claim is guarded by nothing and it is right.
- "comparable to the upper bound of a **Class I hemorrhage** (ATLS)… up to 15 %"
  — clinically correct; ATLS Class I is a loss below 15 % ✓ (citation
  `atls2018`, criterion (a), marked below)

**¶344, the three sex axes:**

| claim | measured |
|---|---|
| "24 (scenario × output) comparisons" | 4 × 6 = 24 ✓ |
| "exceeds its permutation null on **six**, of which **five** survive BH" | 6 → 5 ✓ |
| "PaCO₂ in S1, S2 and S3 … SpO₂ and PaO₂ in S4" | the exact five survivors ✓ |
| "**12** scenario–output cells where the comparison is computable" | **12** — S2 and S3 only; every S1 and S4 cell is NaN ✓ |
| "ρ point estimates **0.75--1.00**" | min **0.7500** (S2 Vt), max **1.0000** (S2 MAP) ✓ |
| "the **mild-ARDS delivered-tidal-volume** cell is the only one whose CI includes zero" | S2 Vt has lo = **−0.0588**; every other lower bound ≥ 0.3433 ✓ **the only one** ✓ |

### §2.6 secondary observations — no new signal (carries P-1)

| claim | measured |
|---|---|
| Sobol trigger "σ/μ\* ratio reached **0.6**" | **the preregistration says 0.6** (`preregistration.md:168`), in a three-band rule: ≤0.4 no Sobol, ≥0.6 Sobol, 0.4–0.6 gray zone ✓ |
| "fired on **43 of the 48**" | **43** combinations have a top-3 input at σ/μ\* ≥ 0.6; 4 more are gray-zone-only ✓ |
| "more than **sevenfold** its preregistered compute envelope" | 11,008 / 1,500 = 7.34 ✓, and the preregistration's envelope is "≤1,500 extra runs" ✓ |
| "variability falls below **1 %** of the mean" | `FLATLINE_STD_RATIO = 0.01` ✓ |
| "the mean lies within **0.1 %** of a hard bound — ≥ 99.9 % for SpO₂" | `FLATLINE_BOUND_TOL = 0.001` ✓ |
| "SpO₂ flatline accounts for **232** trigger occurrences … second only to the delivered-Vt CV" | 232 < 303 ✓ |
| "lowers the `not_steady_state` count from **530 to 454**" | exactly **76** runs carry SpO₂ flatline as their sole recorded reason; 530 − 76 = **454** ✓ |
| HR means 73.8 / 155.7 / 147.1 with σ = 20.4 | re-derived under §S15 ✓ |

⚠️ **A trap that nearly produced a false signal, recorded so it does not recur.**
This project's own `CLAUDE.md` summarises the Sobol trigger as "σ/μ\* **> 0.5**".
The preregistration says **≥ 0.6**. The paper follows the preregistration and is
right; **the instruction file is the document that is wrong.** It is not
published, so this is not a manuscript defect — but it is a live source of error
for anyone working from it, and it came within one step of making me flag a
correct claim. `CLAUDE.md` sits at the repository root, outside the Edit
allowlist, so this is reported and left to the maintainer.

💡 **§2.6 strengthens P-3.** ¶365 discusses the SpO₂-flatline sub-mode at length
— its rule, its 232 occurrences, its effect on the total. So the paper plainly
knows flatline is one of the three triggers; ¶187's two-trigger definition is an
oversight, not a definitional choice.

**Cross-document check on the compensatory-tachycardia paragraph**: §2.6 ¶361
gives the same four means as §S15 and stops there. It does **not** carry §S15's
attribution of the S3→S4 dip to "incipient cardiovascular decompensation".
Supplement signal 28 is therefore **supplement-only**; the paper does not need
the same repair.

### Step-back re-audit of P-1 … P-4 (after finishing Results)

All four verdicts hold. One scope refinement:

⚠️ **P-1** — the `interpolatorPoints` I quoted live on the **restrictive-severity**
pathway, which ARDS feeds through a `MAX` with other restrictive conditions.
They are hard-coded calibration nodes, so the verdict stands, but they are **not
ARDS-exclusive**. `paper.tex:146` is unaffected: it says the ARDS scalar *drives*
functions calibrated at those nodes, which is true of a shared function.

**P-2, P-3, P-4** re-read against their evidence and unchanged. P-3 is
strengthened by §2.6 as noted above.

### Discussion (¶368–394) — one signal (P-5), and the most careful hedging in the paper

**P-5, ¶372** — "**No comparable open atlas yet exists** for related
lumped-parameter engines such as BioGears (Pulse's predecessor) or HumMod." An
unsourced, **unhedged** claim of absence about two third-party engines. The
contrast inside the same paper is instructive: its other absence claim, "no
formal sensitivity analysis of its operational inputs has been published", is
backed by the Pulse maintainers' own FAQ admission. This one has no such anchor
and carries no "to our knowledge". Same family as supplement signals 1 and 20 —
and signal 1 is *also* an unsourced BioGears absence claim, so the two should be
repaired together. Trigger (b) for the citation pass.

**Everything else in the Discussion re-derived or already anchored:**

| claim | measured |
|---|---|
| ¶372 "median 93 % … on 48 of 48" | 0.9277, 48/48 ✓ |
| ¶374 Cornish "85 rejections across 15 quantities; 82 of 85 outside the four-channel overlap: 80 + 2; only 3 … all on PaCO₂" | internally exact (82+3 = 85, 80+2 = 82) and consistent with this project's recorded reading of that source ✓ |
| ¶376 the six recommendations | 1:1 with §S11, same order ✓ |
| ¶382 limit (iv): FiO₂ pairs lost "in the healthy (S1) and severe-ARDS (S4_F) cells" | **exactly 18 of 48 combinations are short an input; the cells are S1_M, S1_F, S4_F, six outputs each; and the missing input is `fio2` in all 18.** S4_M keeps all seven ✓ |
| ¶384 resampling S2_M | top-1 preserved **6/6**; top-3 *set* preserved **4/6**; top-3 *order* preserved **3/6** ✓. And "disagreements involving only the second- and third-ranked inputs" holds: HR [hr,rr,peep]→[hr,fio2,rr], PaO₂ [fio2,rr,peep]→[fio2,peep,rr], Vt [vt,rr,sbp]→[vt,rr,fio2] ✓ |
| ¶388 "clipping shortened **9 of 20** DBP steps" | a **ledger anchor**, re-derived at every gate run ✓ |
| ¶388 "SBP remained rank 1 for MAP in all eight cells … smallest ratio 1.22 in S2_M" | consistent with the closed S032 dossier ✓ |

⚠️ **Not verified**: ¶388's companion figure, "caused applied DBP to co-vary in
**8 of 20** SBP steps". The 9/20 has a ledger anchor; no anchor for the 8/20 was
located in this scan, and it was not measured. Marked rather than assumed.

**Hedging recorded as exemplary**, because it is the standard the rest of the
corpus should be held to: "it does not imply that physiological states or
controller targets stay fixed once the simulation runs"; "Green … does not
establish physiological validity"; "These comparisons establish a sex-conditioned
distributional signal **without identifying a single physiological mechanism or a
scenario-independent direction of effect**"; "**No trajectory-count convergence
analysis was performed**"; "These analyses establish **ranking robustness, not
causal isolation**"; "whether these adult-model reliability patterns transfer to
pediatric physiology **remains untested**". A material post hoc deviation at the
yellow–red boundary is declared in ¶368 rather than buried.

---

## Citation inventory for the later pass — listed, not opened

**Population measured**: 105 citation occurrences over 44 distinct keys across
`paper.tex` and `supplement.tex`. A lexical screen flagged 41 occurrences firing
two or more of the agreed triggers.

⚠️ **The screen over-fires and is not a verdict.** Its "absence" pattern matches
any `no|not|only|first`, so it catches ordinary prose. The ranking below is
judgement applied on top of it, not the score.

### ✅ PASS 1 COMPLETE — the four positive-claim citations, all SUPPORTED

Format per the agreed protocol: claim → primary source → supporting passage →
verdict. **No manuscript edit follows from any of these.**

#### `sinnige2026active` (ACTiVE) — `paper.tex:394` — **SUPPORTED**

Source opened in this session: PubMed E-utilities, PMID 41361939 (JAMA 2026;
335(10):874–884). PubMed's HTML is blocked by a cookie wall; the E-utilities
endpoint returns the abstract clean.

| clause | source passage |
|---|---|
| "improved overall ventilation quality" | "There were no differences in secondary outcomes **except for ventilation quality, which was higher with closed-loop ventilation**" |
| "no difference in ventilator-free days" | median **16.7 vs 16.3 days**, OR 0.91 (95 % CI 0.77–1.06), **P = .23**; conclusion "did not increase ventilator-free days at day 28" |
| "or **mortality**" | "There were no differences between groups in components of the primary outcome, ie, duration of ventilation in survivors and **28-day mortality**" |

⚠️ **Two corrections for the `.bib` `internal_note`, not for the paper**: the note
covers only the VFD outcome and ventilation quality, so it does **not** record the
mortality result the paper relies on; and its "n = 1,201" is the **modified
intention-to-treat** population, where **1,514** were randomised.

#### `webb2020` — `paper.tex:142` — **SUPPORTED on every clause**

Source opened: PLoS One 15(11):e0242532.

| clause | source |
|---|---|
| "**12,642** unique patient and ventilator combinations" | 12,642 ✓ |
| "spanning respiratory compliance, diffusion impairment and PEEP" | compliance 10–50 mL/cmH₂O, DIF 0.3–0.9, PEEP 10–20 ✓ |
| "two equal-sized **70 kg** bodies" | "Two equal-sized 70 kg patients are modeled" ✓ verbatim |
| "**pressure-mode** ventilation" | PC-CMV ✓ |
| "RR, I:E ratio and respiratory resistance **held fixed**" | RR 20/min, I:E 1:2, resistance 5 cmH₂O·s/L ✓ all three |
| "does rank parameters by **outcome correlation**" | one-way ANOVA then Pearson: "Five parameters were found to be most correlated to outcomes: Cstat, EtCO₂, A-a gradient, OSI, and OI" ✓ |
| "that ranking … is over the **mismatch**" | the ranked quantities are *differences* between the paired patients (compliance difference, OSI difference) ✓ |

#### `cornish2023` — `paper.tex:374` — **SUPPORTED, verified against the source's own Table 4**

PDF downloaded (arXiv:2301.07210) and read; `pdftotext -layout` mangled the
table columns, `-raw` resolved them. Table 4 lists all 15 assessed quantities.

- "**85** total Hoeffding rejections" → Table 4's rejection column sums to **85** ✓
- "across **15** physiological quantities" → Table 4 lists exactly **15** ✓ (nine
  with non-zero rejections, six at zero: paO₂, arterial pH, DiaBP, MeanBP, RR, HR)
- "**80** on channels the present atlas does not assess (electrolyte, metabolic,
  acid–base, dermal)" → Chloride 24 + Sodium 21 + Potassium 13 + Calcium 5 +
  Glucose 5 + HCO₃ 2 = 70, plus Skin Temperature 10 = **80** ✓
- "plus **2** on partial-overlap pressure channels" → SysBP 2 ✓
- "only **3** of 85 fall on the four-channel overlap, **all on PaCO₂**" → paCO₂ 3,
  and HR, MeanBP, paO₂ are all at **0** ✓
- "four-channel overlap (HR, MAP, PaO₂, PaCO₂)" → those four are exactly the
  intersection of our six outputs with Cornish's 15; Vt and SpO₂ are absent
  from theirs ✓
- "MIMIC-III sepsis trajectories" → abstract: "the MIMIC-III dataset of ICU
  patients", "a large-scale, real-world case study involving sepsis modelling" ✓

Also computed from Table 4 rather than taken on trust: the hypothesis column sums
to **1,522**, confirming this project's recorded figure independently.

⚠️ **A defect in the source, recorded so nobody "corrects" our paper toward it.**
Cornish's own prose reads "we obtained rejections for hypotheses corresponding to
**10** different physiological quantities shown in Table 1", while Tables 1 and 4
both show **nine** with non-zero rejections. Our paper does not repeat the error.

#### `ward2024ventilator` — `paper.tex:380`, `:394` — **DISCHARGED**

Not re-opened, and the reason is recorded: its `.bib` `internal_note` carries
"**FULL TEXT READ 2026-08-10** (7 pages, arXiv:2411.07971v1)" and documents both
claims the paper makes — the six-setting pressure-targeted action vector of which
only FiO₂, RR and PEEP are swept here, and the latent model "used *in lieu of*
Pulse", judged against "Pulse's respiratory dynamics", with real-data validation
listed as future work. Both paper sentences match that note.

### P-5 — arbitrated: the repair is to **anchor** it, not merely to soften it

> No comparable open atlas yet exists for related lumped-parameter engines such
> as BioGears (Pulse's predecessor) or HumMod.

**The BioGears half has a primary source, found this session.** The BioGears FAQ
(`biogearsengine.com/documentation/_f_a_q.html`, downloaded and read; the page
mentions "biogears" 66 times and "pulse" **zero** times, so there is no
contamination) states verbatim:

> "We have not performed a systematic forward propagation or inverse
> quantification of model uncertainty, **nor do we have the resources to conduct
> a formal sensitivity analysis.**"

⚠️ **Not a copy of the Pulse FAQ, and the difference matters.** Pulse writes "nor
**have we conducted** a formal sensitivity analysis"; BioGears writes "nor **do we
have the resources to** conduct" one. Two related but distinct texts, consistent
with the fork history — so the two engines admit it **separately**, and the
BioGears admission is independently citable.

**This changes the repair.** The sentence is today an unsourced universal
negative. It can become a *sourced* one for the engine it names first, cited
exactly as `pulsefaq` already is in the same paper.

**The HumMod half is not established.** A literature search returned nothing
HumMod-specific — ⚠️ **but that search was not calibrated**, so its emptiness
distinguishes nothing between "no such work exists" and "the query was wrong".
Recorded as unknown, not as absent.

**Verdict: SOURCE INSUFFICIENT for the universal form.** "No comparable open
atlas **yet exists**" quantifies over the whole literature and cannot be
established by any search. The defensible form bounds the claim to what was
looked at — "we did not identify a comparable open atlas for …" — while the
BioGears clause gains a citation rather than losing force.


### Highest value — open these first

| key | locus | what to check | trigger |
|---|---|---|---|
| `sinnige2026active` | `paper.tex:394` | ACTiVE "improved overall ventilation quality yet showed **no difference in ventilator-free days or mortality**" — an attributed RCT outcome, and the four supervising reviewers will know this trial | (a) |
| `ward2024ventilator` | `:380`, `:394` | "of its **six** ventilator settings, only FiO₂, RR and PEEP are inputs this atlas sweeps"; and "assessed **against Pulse rather than against patient data**" | (a)(d) |
| `webb2020` | `:142` | "**12,642** unique patient and ventilator combinations"; "two equal-sized **70 kg** bodies"; "RR, I:E ratio and respiratory resistance **held fixed**" | (a) |
| `cornish2023` | `:374` | "**85** Hoeffding rejections across **15** quantities", and the **80 / 2 / 3** split | (a) |
| `kuczmarski2002cdc` | `:406` | CDC row at `Agemos = 216.5` giving **67.28992603** and **56.22969564** kg | (a) |
| `ards2012` | `:414` | the Berlin band boundaries the calibration targets | (d) |
| — | `:372` | **P-5**: "No comparable open atlas yet exists" for BioGears/HumMod — **no citation at all** | (b) |
| — | §S11 item 2 | **signal 20**: the BV floor "is not currently exposed in the public patient-setup documentation" → `pulsepatientmethod` | (b) |
| — | §S12 ¶903 | **signal 23**: `kitware/pulse:4.3.1` published "for `linux/amd64` **only**"; "**no** prebuilt ARM64 image exists" → a Docker Hub manifest query | (b) |
| — | §S1 ¶116 | **signal 1**: "not present in BioGears" | (b) |

### Verbatim quotations — trigger (c)

`pulsefaq` (`:144`, the FAQ sentence quoted in full) and `pulsesystem` (`:146`,
"a low fidelity clinical approach… not necessarily for high fidelity predictive
purposes"). Plus supplement **signal 9**, the §S7 ¶597 paraphrase carried inside
quotation marks.

### Hard-bound provenance — trigger (d), one sentence each

`brower2000`, `severinghaus1979`, `singer2016`, `evans2021sepsis`,
`mancia2023esh`, `nin2017`, `west2020respiratory` — each anchors one
`implausible` bound in §4.4.

### ✅ Already discharged during this sweep — do not re-open

- **`nadler1962`** — the 73.0 and 63.8 mL·kg⁻¹ were recomputed by hand from the
  published sex-specific formulas and both are exact.
- **`pulserespmethod`** (the five severity nodes) — confirmed directly in
  `RespiratoryModel.cpp:3724–3731`, which is stronger than the citation.

**Marked for the citation pass, not opened:**

| locus | trigger | what to check |
|---|---|---|
| L142 `webb2020` | (a) attributed figures | "12,642 unique patient and ventilator combinations", "two equal-sized 70 kg bodies", "respiratory rate, I:E ratio and respiratory resistance held fixed" |
| L144 `pulsefaq` | (c) verbatim quotation | the FAQ sentence, quoted in full |
| L144 `cornish2023` | (a) attributed result | "errors concentrated on electrolyte, metabolic, acid–base and dermal outputs" |
| L146 `pulserespmethod` | (a) attributed figures | the five nodes — **now independently confirmed in the engine source**, so this one is discharged |
| L146 `pulsesystem` | (c) verbatim quotation | "a low fidelity clinical approach… not necessarily for high fidelity predictive purposes" |
