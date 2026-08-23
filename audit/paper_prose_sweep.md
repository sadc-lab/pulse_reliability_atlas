# Paper prose sweep — `preprint_npj/paper.tex`

Companion to `audit/supplement_prose_sweep.md`, which covered §S1–§S17 of the
supplement and closed at 30 signals. This register covers the **main manuscript**
by the same method, and adds a fourth question dedicated to paper↔supplement
coherence.

**Started 2026-08-23. No manuscript edit is made during this sweep.** Signals are
recorded and left for a later, separate correction pass.

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

**Marked for the citation pass, not opened:**

| locus | trigger | what to check |
|---|---|---|
| L142 `webb2020` | (a) attributed figures | "12,642 unique patient and ventilator combinations", "two equal-sized 70 kg bodies", "respiratory rate, I:E ratio and respiratory resistance held fixed" |
| L144 `pulsefaq` | (c) verbatim quotation | the FAQ sentence, quoted in full |
| L144 `cornish2023` | (a) attributed result | "errors concentrated on electrolyte, metabolic, acid–base and dermal outputs" |
| L146 `pulserespmethod` | (a) attributed figures | the five nodes — **now independently confirmed in the engine source**, so this one is discharged |
| L146 `pulsesystem` | (c) verbatim quotation | "a low fidelity clinical approach… not necessarily for high fidelity predictive purposes" |
