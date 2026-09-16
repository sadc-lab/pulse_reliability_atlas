# Reference audit — `preprint_npj/paper.bib`

**Purpose.** A per-reference, auditable record that every citation in
`paper.tex` and `supplement.tex` is (a) attached to a claim the cited work
actually supports, and (b) backed by a source we have genuinely read at the
depth the claim requires. Opened 2026-07-26.

**Why a register rather than a reading pass.** A visual sweep leaves no trace
and cannot be re-checked. This file records, for each reference, the exact
claim we make, the exact sentence or table cell that supports it, how deeply
the source was read, and a verdict — so a reviewer, a co-author, or a future
session can re-verify any row without repeating the whole audit.

---

## Schema

| Column | Meaning |
|---|---|
| **Key** | BibTeX key in `preprint_npj/paper.bib`. |
| **Our claim** | The assertion as it appears in our text, with its locus. |
| **Verbatim source** | The exact sentence, table row or cell in the cited work that supports it. Quoted, not paraphrased. |
| **Depth** | `full text` — the primary source was read end to end · `targeted` — the specific table/section carrying the claim was read at source · `abstract` — only the abstract was accessible · `not read`. |
| **Status** | `MATCH` — the source says what we say it says · `OVERCLAIM` — the source supports something weaker · `WRONG` — the source contradicts us · `UNVERIFIABLE` — the source could not be obtained. |

**Depth policy** (from the standing rule): an abstract suffices when our claim
is the paper's headline result. A nuanced or secondary claim requires the
discussion or the relevant table at source. Whichever was done must be stated
here honestly — "targeted" is not a euphemism for "skimmed", it means the
specific table or section carrying our number was opened and read.

---

## Audited

### `cornish2023` — Cornish, Taufiq, Doucet & Holmes, *Causal Falsification of Digital Twins*, arXiv:2301.07210v4

**Depth: `targeted`** — v4 PDF retrieved from arXiv on 2026-07-26 and text-extracted
(`pdftotext -layout`); Appendix Tables 4 and 5 (p. 47) transcribed in full,
main-text §5 hypothesis-count passage read at source.

| # | Our claim | Verbatim source | Status |
|---|---|---|---|
| 1 | "1,522 hypotheses across 15 physiological quantities" (monograph §4.4, §6.7) | Appendix Table 4 lists 15 quantities; its `# Hypotheses` column sums to **1,522** (94+94+94+86+88+96+70+90+154+78+80+72+92+172+162) | **MATCH** |
| 2 | Cornish's main text states 1,442 across 14 quantities, omitting the Arterial-pH channel (monograph §4.4, contextualised) | Main text: *"we chose 14 different"* … *"1,442 total hypotheses."* Appendix Table 4 additionally carries *"Arterial pH (Arterial pH)  0  80"*. 1,442 + 80 = 1,522 | **MATCH** |
| 3 | 85 Hoeffding rejections in total | Table 4 `# Rejections` column sums to **85** (24+21+13+10+5+5+3+2+2+0×6) | **MATCH** |
| 4 | 281 bootstrap rejections in total | Table 5 `# Rejections` column sums to **281** (47+46+33+43+44+19+13+8+8+4+0+0+3+12+1) | **MATCH** |
| 5 | PaCO2 **3 / 70** Hoeffding, **13 / 70** bootstrap → 18.6 % (monograph §4 table and narrative; anchor `M.T20.cornish_frac`, `M.T20.cornish_pct`) | Table 4: *"Arterial CO2 Pressure (paCO2)  3  70"*. Table 5: *"Arterial CO2 Pressure (paCO2)  13  70"*. 13/70 = 18.571 % | **MATCH** |
| 6 | PaO2 **0 / 78** and **4 / 78** → 5.1 % | Table 4: *"Arterial O2 Pressure (paO2)  0  78"*. Table 5: *"… 4  78"*. 4/78 = 5.128 % | **MATCH** |
| 7 | MeanBP **0 / 92** and **3 / 92** → 3.3 % | Table 4: *"Mean Arterial Pressure (MeanBP)  0  92"*. Table 5: *"… 3  92"*. 3/92 = 3.261 % | **MATCH** |
| 8 | HR **0 / 162** and **1 / 162** → 0.6 % | Table 4: *"Heart Rate (HR)  0  162"*. Table 5: *"… 1  162"*. 1/162 = 0.617 % | **MATCH** |
| 9 | The eleven non-overlapping channels and their Hoeffding counts (Chloride 24, Sodium 21, Potassium 13, Skin Temperature 10, Calcium 5, Glucose 5, HCO₃ 2, plus SysBP / DiaBP / pH / RR) | Table 4 rows, verbatim: Chloride 24/94, Sodium 21/94, Potassium 13/94, Temp 10/86, Calcium 5/88, Glucose 5/96, HCO₃ 2/90, SysBP 2/154, DiaBP 0/72, Arterial pH 0/80, RR 0/172 | **MATCH** |

**Outcome: 9 of 9 claims MATCH. Every number we attribute to Cornish is
verbatim in their Appendix Tables 4 and 5.**

**This closes two previously-open items.**

1. `S029_cornish_forensics.md` recorded explicitly that *"the assistant did not
   re-open Cornish's PDF in this session; the main-text-vs-appendix source
   split is the maintainer's verified reading"* and asked a future verifier to
   *"re-open Cornish v4 and confirm the Arterial-pH row in Appendix Table 4
   (80 hypotheses, 0 rejections) verbatim."* Confirmed: Table 4 carries
   `Arterial pH (Arterial pH)  0  80`.
2. `preprint/monograph_anchor_map.md` flagged `M.T20.cornish_frac` as the one
   anchor not re-derivable from atlas data, resting on a human reading of an
   external PDF. That reading is now verified at source and the residual risk
   is closed.

---

### `pulsefaq` — Pulse Physiology Engine, public FAQ

**Depth: `targeted`** — page fetched 2026-07-26, the uncertainty-quantification
question read at source.

| # | Our claim | Verbatim source | Status |
|---|---|---|---|
| 1 | Direct quotation, paper §1: *"we have not performed a systematic forward propagation or inverse quantification of model uncertainty, nor have we conducted a formal sensitivity analysis"* | Under the heading *"What kind of uncertainty quantification do you do perform in your physiology model?"*: **"We have not performed a systematic forward propagation or inverse quantification of model uncertainty, nor have we conducted a formal sensitivity analysis."** | **MATCH** |
| 2 | Paper §5 and supplement §S2 restate it as "no formal sensitivity or uncertainty quantification has been performed on user-facing operational inputs" | Same sentence. The qualifier "on user-facing operational inputs" is **ours**, added to distinguish the 2020 `STUDY_SENSITIVITY_ANALYSIS_1_0_0` Sobol study on internal circuit values; the supplement states that distinction explicitly in the same row | **MATCH** |

Word-for-word identical; only the leading capital is lowered for mid-sentence
insertion, which is standard quotation practice. A verbatim quotation is the
highest-risk citation class in the manuscript, and it is clean.

---

### `webb2022vent` — Webb et al., ANNSIM 2022 (PMC10224749)

**Depth: `targeted`** — PMC full text consulted 2026-07-26.

| # | Our claim | Verbatim source | Status |
|---|---|---|---|
| 1 | Paper §1: Pulse has been applied to "the validation of its own mechanical-ventilator model against a physical reference simulator" | Nine validation use cases comparing Pulse against "physical ventilator values and waveforms", ASL 5000 lung simulator driven by a Dräger ventilator | **MATCH** |
| 2 | Supplement §S2: "that paper reports qualitative ASL-5000 waveform agreement, not these quantitative percentages" | *"The waveforms created by the virtual ventilator match well with the displayed physical ventilator monitor values"*; no tidal-volume percentage errors are reported anywhere in the paper | **MATCH** |

---

### `pulsevent` — Pulse *Mechanical Ventilator Methodology*, v4.3.1 documentation

**Depth: `targeted`** — page downloaded 2026-07-26 and parsed from the **raw
HTML**, not from a summary. The six tidal-volume validation rows were read
cell by cell, because an initial model-mediated reading of the page returned
paired values that did not reconcile with the printed percentages.

**The six magnitudes and their table numbers are exact.** Verbatim rows:

| Mode | Profile | Expected | Engine (Pulse) | Printed % |
|---|---|---|---|---|
| VC-AC | healthy (Table 3) | 900 | Mean of 900.613 | 0.0681 % |
| VC-AC | restrictive (Table 10) | 550 | Mean of 555.570 | 1.01 % |
| VC-AC | obstructive (Table 17) | 493 | Mean of 504.243 | 2.25 % |
| PC-AC | healthy (Table 5) | 1047 | Mean of 935.217 | 11.3 % |
| PC-AC | restrictive (Table 12) | 528 | Mean of 409.439 | 25.3 % |
| PC-AC | obstructive (Table 19) | 571 | Mean of 490.087 | 15.3 % |

| # | Our claim | Verbatim source | Status |
|---|---|---|---|
| 1 | VC-AC tidal-volume errors of 0.07 – 2.25 % across healthy / restrictive / obstructive (monograph §2.3) | 0.0681 / 1.01 / 2.25 % — and the claim is stated as *"errors"*, direction-neutral | **MATCH** |
| 2 | PC-AC 11.3 – 25.3 % (the range spans all three profiles: 11.3, 25.3, 15.3) | 11.3 / 25.3 / 15.3 % | **MATCH** |
| 3 | Table numbers 3, 5, 10, 12, 17, 19 (bib `internal_note`) | Confirmed, all six | **MATCH** |
| 4 | **"PC-AC *over-delivers* tidal volume by 11.3 – 25.3 % … per Pulse's own validation tables"** (supplement §S2 row 7; monograph §2.2 item 7) | In all three PC-AC rows the Engine value is **below** the Expected value: 935.217 < 1047, 409.439 < 528, 490.087 < 571. Pulse delivers **less** than the physical reference, not more | **MISMATCH — direction** |

**On finding 4.** The magnitude range is correct and the source is the right
one; what the source does not support is the direction. The `Percent Error`
column is unsigned, so the direction must be read from the paired
Expected/Engine columns, and they point the other way.

Independently corroborated by `webb2022vent`, which describes the same
validation setup: *"the data shows that an extended inspiration time by the
physical ventilator translates to **higher TVs** than come from our ideal,
deterministic circuit model."* The physical ventilator produces the higher
tidal volumes; Pulse produces the lower ones.

**Blast radius, established read-only (nothing modified):**

- `preprint_npj/supplement.tex:124` — §S2 limitations table, row 7. Attributes
  the direction to `\cite{pulsevent}`. **Affected.**
- `preprint/manuscript.md:563` — same claim, and additionally asserts that the
  companion experiments *"corroborate the direction"*. **Affected.**
- `CLAUDE.md:56` — the project's verified-limitations table: "PC-AC
  over-delivers Vt 24–59% | Pulse\_translation\_new + Webb 2023 11–25%
  concordant". The magnitude ranges differ by referent; the word "concordant"
  additionally implies a shared direction. **Affected.**
- `preprint/manuscript.md:928–930` — **NOT affected.** It states
  "VC-AC tidal-volume errors of 0.07 – 2.25 % … vs PC-AC's 11.3 – 25.3 %",
  which is direction-neutral and correct as written.
- `preprint_npj/paper.tex` — **NOT affected.** Its single "over-delivering"
  occurrence is in §2.4 and concerns oxygenation at FiO$_2$ = 1.0, unrelated.

**Not settled here, and outside what `pulsevent` can settle:**
`preprint/manuscript.md:934` reports the companion project's own finding that
"PC-AC over-delivery scales inversely with body weight (female +58.9 % vs male
+24.0 % at PIP = 20 cmH2O)". That is a different experiment against a
different referent — plausibly delivered Vt against a target rather than
against the ASL 5000 — and it lives in `Pulse_translation_new`, which is
read-only. Whether it is direction-compatible with Pulse's own tables is a
separate question, and it is the hinge of the monograph's "corroborate the
direction" sentence.

**RESOLVED 2026-07-26.** The companion referent was retrieved under explicit
read-only authorisation from `Pulse_translation_new/experiments_log.md`
(L866–870), and it settles the question:

| Configuration | Female | Male |
|---|---|---|
| VC-AC commanded | 399.7 mL (1.60 % err) | 479.6 mL (1.81 % err) |
| PC-AC at PIP = 20 cmH2O | 635.3 mL (**+58.9 % vs VC-AC**) | 594.5 mL (**+24.0 % vs VC-AC**) |

Arithmetic confirms the referent: (635.3 − 399.7)/399.7 = 58.94 % and
(594.5 − 479.6)/479.6 = 23.96 %. **The companion's baseline is VC-AC inside
Pulse, not a physical reference.**

So the two results measure different pairs and **are not in conflict**:

- Pulse's validation tables compare **Pulse's PC-AC against physical hardware**
  (ASL 5000 / Dräger) → Pulse delivers *less*.
- The companion compares **PC-AC against VC-AC within Pulse** at a fixed
  driving pressure → PC-AC delivers *more*.

Both statements are true simultaneously. What was wrong is (a) the direction
attributed to Pulse's tables, and (b) the monograph's claim that the companion
experiments "corroborate the direction" — they cannot corroborate a
Pulse-vs-hardware direction, because they never measure it.

A genuine concordance does exist, on the other mode: the companion's VC-AC
commanded-volume errors (1.60 % female, 1.81 % male) sit inside Pulse's own
VC-AC validation band (0.07–2.25 %).

**Correction applied at four loci** (commit below), on the direction-neutral
formulation agreed in advance:

1. `supplement.tex` §S2 row 7 — "over-delivers … by 11.3–25.3 %" →
   "deviates from the physical reference by 11.3–25.3 % … against 0.07–2.25 %
   for VC-AC". The VC-AC contrast is added because it is the actual reason the
   atlas restricts to VC-AC.
2. `manuscript.md` §2.2 item 7 — same neutral wording, plus the paired columns
   spelled out (935 vs 1,047; 409 vs 528; 490 vs 571), plus the corrected
   description of what the companion measured, plus an explicit statement that
   the two results are not in conflict.
3. `CLAUDE.md` limitation 7 — rewritten to keep the two referents apart, with
   both sets of primary numbers and an explicit "not concordant and not in
   conflict".
4. `manuscript.md` §B — a surviving row-index citation, "`Pulse_translation_new`
   entry #20", replaced by the named probe. This is a **missed instance of the
   numbering purge in commit 7b2049e**, which targeted the `E20` form and did
   not catch the `entry #20` variant. The `#12 / #13` pair in locus 2 was the
   same defect and is fixed by the same edit. One `entry #4` reference remains
   and is legitimate — it points at our own preregistration table, not at the
   companion.

---

## Not yet audited

30 remaining entries. Order of attack: references carrying a **number** we
quote come first, since a wrong number is a factual error; references cited
for framing come last, since the failure mode there is a weaker one
(citing a real paper for a claim it does not quite make).

**Tier 1 — a number of ours depends on it**

`pulsevent` · `webb2022vent` · `brower2000` · `severinghaus1979` ·
`singer2016` · `evans2021sepsis` · `mancia2023esh` · `atls2018` ·
`nadler1962` · `kuczmarski2002cdc` · `ards2012` · `pulsefaq`

**Tier 2 — a qualitative claim of ours depends on it**

`bray2019` · `webb2020` · `figueroacasas2016` · `thille2006` · `blanch2015` ·
`akoumianaki2014` · `sinderby1999` · `sinnige2026active` ·
`katsoulakis2024digitaltwins` · `west2020respiratory` · `marino2013icu` ·
`marini2018critical`

**Tier 3 — methodological / framing**

`morris1991` · `campolongo2007` · `lundberg2017` · `iwanaga2022` ·
`wilkinson2016` · `munafo2017`

**Already partially checked elsewhere, still needs a row here:**
`sinnige2026active` (ACTiVE) — DOI, volume, pages and the "overall ventilation
quality" wording were fact-checked against JAMA 2026;335(10):874–884 on
2026-07-24; the row below must record that verbatim rather than point at a
commit message.

The `pmid` fields added to `paper.bib` in commit `7a46040` are the working
instrument for this audit: each is a direct handle to the primary record.

---

## Access probe on the 5 remaining Tier 1 references (2026-07-26)

**Nothing below is verified yet.** This section records only whether the
primary source is reachable, so the next session does not re-probe the same
dead ends. No claim status changes on the strength of an access probe.

| key | route tried | result |
|---|---|---|
| `evans2021sepsis` | Europe PMC `EXT_ID:34605781` | not open access · no PMCID · `inEPMC` false · no PDF |
| `evans2021sepsis` | Springer ICM co-publication `10.1007/s00134-021-06506-y` | 303 redirect to `idp.springer.com` auth portal |
| `kuczmarski2002cdc` | Europe PMC `EXT_ID:12043359` | not open access · no PMCID · no full-text URL listed |
| `kuczmarski2002cdc` | `cdc.gov/nchs/data/series/sr_11/sr11_246.pdf` | **HTTP 403** |
| `mancia2023esh` | Europe PMC `EXT_ID:37345492` | not open access (subscription) |
| `nadler1962` | — | not probed; *Surgery* 1962;51(2) predates digitisation, expect no full text |
| `atls2018` | — | printed course manual, 10th ed.; no online full text exists |

### What each reference actually has to support

Recorded now so the verification is against the *exact* wording, not a memory
of it.

- **`evans2021sepsis`** — two loci, both in Supplement §S3.
  (a) MAP lower bound: ``the Sepsis-3 organ-perfusion failure threshold and the
  Surviving Sepsis Campaign MAP target of $\geq 65$~mmHg''.
  (b) ``Lower edge of what a clinician would call ongoing hemodynamic
  instability rather than settled perfusion'' (co-cited with `singer2016`).
- **`mancia2023esh`** — Supplement §S3 MAP upper bound: ``ESH 2023 hypertensive
  emergency definition (SBP $>$ 180~mmHg with acute target-organ damage)''.
  ⚠️ `paper.bib`'s own `internal_note` says ``SBP greater than 180 mmHg
  **and/or DBP greater than 120 mmHg**''. The supplement states only the SBP
  limb. Check whether the omission is a simplification or a misstatement.
- **`nadler1962`** — paper §2.5: the two reference bodies share ``essentially
  the same blood volume per kilogram ($\approx$71~mL\,kg$^{-1}$), **within
  standard clinical estimates**'', and Pulse's formula ``does not reproduce the
  **modest male--female difference in volume per kilogram reported
  clinically**''. Two distinct things to verify: the per-kg range, and that
  Nadler does encode a sex difference.
- **`kuczmarski2002cdc`** — Methods + Supplement §S4: male 67.3~kg and female
  56.2~kg are CDC growth-chart **50th-percentile weights at 18 years**; female
  height 163~cm matches the **CDC 50th percentile**. ⚠️ Likely obstacle: this
  report is the *methods* document; the smoothed percentile values live in the
  separate NCHS data files, so the report may not contain the numbers at all.
  If so, the citation may need to point at the data file instead.
- **`atls2018`** — paper §2.5: the 15.0~\% blood-volume reduction ``is
  comparable to the upper bound of a Class~I hemorrhage in the ATLS trauma
  classification (a loss of up to 15~\% of blood volume)''.

### Standing policy

Per the autonomy pact: if a source cannot be reached, mark it `UNVERIFIABLE`
and never substitute a proxy. A secondary source that *quotes* the primary is
not a verification of the primary. The author has offered to supply PDFs
directly — that is the preferred route before any `UNVERIFIABLE` is recorded.

---

## Tier 1 — the last five, audited 2026-07-26

Sources supplied by the author from Universite de Montreal access, except
`nadler1962`, which the author could not obtain and which was located instead in
a public USPTO PTAB filing (Terumo v. Haemonetics, PGR2025-00077, Exhibit 1016).
That exhibit is a scan of the article itself: internal PDF title
`PII: 0039-6060(62)90166-6` — the publisher item identifier of the Surgery paper
— and 9 pages, matching pp. 224–232 exactly, every page stamped "Petitioner
Terumo Exhibit 1016". It is the primary source, not a secondary quotation.

### `atls2018` — ATLS Student Course Manual, 10th ed. — **MATCH**

**Our claim** (paper §2.5): the 15.0 % blood-volume reduction "is comparable to
the upper bound of a Class I hemorrhage in the ATLS trauma classification (a
loss of up to 15 % of blood volume)".

**Verbatim, Table 3-1 "Signs and symptoms of hemorrhage by class":**

> Approximate blood loss — CLASS I **<15%** · CLASS II (MILD) 15–30% ·
> CLASS III (MODERATE) 31–40% · CLASS IV (SEVERE) >40%

Section heading, same page: "Class I Hemorrhage: **<15% Blood Volume Loss**".

**Verdict MATCH.** ATLS writes "<15 %" where we write "up to 15 %"; equivalent
in ordinary usage. Our 15.0 % sits exactly on the Class I/II boundary, and the
sentence says "comparable to the **upper bound** of a Class I hemorrhage", which
handles that correctly rather than claiming our value *is* Class I. Nothing to
change.

### `nadler1962` — Nadler, Hidalgo & Bloch, *Surgery* 1962;51(2):224–232 — **MATCH**

**Our claim** (paper §2.5): the two reference bodies "share essentially the same
blood volume per kilogram (~71 mL/kg), **within standard clinical estimates**";
and Pulse's formula "does not reproduce the **modest male–female difference in
volume per kilogram reported clinically**".

**Verbatim, p. 226:**

> The normal circulating blood volume has been reported to range from **64 to
> 79.3 ml. per kilogram** of body weight with an **average of 75 ml. per
> kilogram**. **Women have smaller volumes than men with an average of 66 ml.
> per kilogram.** The sex difference has been explained on the basis of the
> relatively smaller ratio of metabolically active tissue to fat tissue in women.

**Verbatim, the prediction equations:**

> For men, PBV = 0.3669 H3 + 0.03219 W + 0.6041
> For women, PBV = 0.3561 H3 + 0.03308 W + 0.1833

**Both limbs verified.**

1. *Within standard clinical estimates.* Pulse gives 4,802.63 mL / 67.3 kg =
   **71.36** mL/kg and 3,996.09 mL / 56.2 kg = **71.10** mL/kg. Both sit
   comfortably inside Nadler's reported **64–79.3** mL/kg. Supported, precisely.
2. *A clinically reported sex difference Pulse does not reproduce.* Nadler
   states it in words (75 general vs 66 for women) and encodes it in two
   separate equations. Applied to our exact bodies those equations give
   **72.96** mL/kg male and **63.78** mL/kg female — a **12.6 %** gap — against
   Pulse's sex-independent ~71 for both. Supported.

⚠️ One word to weigh, not an error: we call the difference "modest". The
magnitude is 75 → 66 mL/kg in Nadler's cited literature (−12 %) and 72.96 →
63.78 on our bodies (−12.6 %). Defensible, but the author may prefer a neutral
word now that the figure is known.

### `evans2021sepsis` — Surviving Sepsis Campaign 2021 — **MINOR MISMATCH + one weak support**

Verified against the *Intensive Care Medicine* co-publication (47(11):1181–1247,
DOI 10.1007/s00134-021-06506-y), identical text to the *Crit Care Med* version
cited in `paper.bib`.

**Verbatim, Recommendation 9, p. 1185:**

> 9. For adults with septic shock on vasopressors, we recommend an initial
> target mean arterial pressure (MAP) of **65 mm Hg over higher MAP targets**
>
> *Strong recommendation, moderate-quality evidence*

**Rationale, same page:**

> MAPs below a threshold, usually understood to be approximately 60 mm Hg, are
> associated with decreased organ perfusion, which tracks linearly with MAP.
> **Previous SSC guidelines recommended targeting a MAP of greater than
> 65 mm Hg** for initial resuscitation.

**(a) MINOR MISMATCH.** Supplement §S3 writes "the Surviving Sepsis Campaign MAP
target of >= 65 mmHg". The 2021 guideline targets **65**, explicitly *over
higher targets*; the "greater than 65" formulation is the one the guideline
attributes to its own **previous** edition. Our ">=" therefore reproduces the
superseded wording. Impact on the argument: none — the sentence only needs
30 mmHg to be far below any acceptable MAP — but the quotation is not what the
2021 source says.

**(b) SUPPORT WEAK.** Supplement §S3 Table `tab:drift-rationale` cites this
reference for the MAP **drift** threshold (5 mmHg / 60 s): "Lower edge of what a
clinician would call ongoing hemodynamic instability rather than settled
perfusion". Neither SSC 2021 nor Sepsis-3 defines any drift or rate-of-change
criterion; both define absolute targets. The nearest supporting statement is
"decreased organ perfusion ... tracks linearly with MAP", which makes a small
absolute change meaningful but does not establish 5 mmHg / 60 s. The citation is
not wrong about the clinical frame, but it does not carry the specific
threshold. For joint decision.

### `mancia2023esh` — 2023 ESH Guidelines — **MISMATCH (two parts)**

**Verbatim, §16.2.1, p. 1975:**

> Hypertension emergencies are conditions in which **severe hypertension
> (grade 3)** is associated with **acute symptomatic HMOD**. [...] The rate of
> the increase in BP may be at least as important as the absolute BP level in
> determining the clinical severity of the situation.

**Table 1, p. 1886 — read from a rendered page image, not from text extraction**
(`pdftotext` shifted the systolic column down one row and dropped the ">="
glyphs; the rendered page is the ground truth):

| Category | Systolic | | Diastolic |
|---|---|---|---|
| Grade 2 hypertension | 160–179 | and/or | 100–109 |
| **Grade 3 hypertension** | **>= 180** | and/or | **>= 110** |

**(a) `paper.bib` `internal_note` is factually wrong.** It records the ESH
definition as "SBP greater than 180 mmHg **and/or DBP greater than 120 mmHg**".
ESH grade 3 diastolic is **>= 110**. No ESH grade uses 120 mmHg. The field does
not render in the PDF, but it is wrong and would mislead anyone re-checking.

**(b) Supplement §S3 writes "SBP > 180"**, ESH writes **>= 180**. Off by the
boundary value.

**(c) Note, not an error.** ESH defines the emergency by *grade* plus acute
symptomatic HMOD, and adds that a relatively modest BP rise can suffice. Our
one-line restatement as a numeric threshold is a simplification. Our use — a
ceiling for a post-hoc plausibility bound — is unaffected. Also worth recording
for the adult-scope requirement: Table 1's footnote states the same
classification applies to adolescents >= 16 years, i.e. it is the adult table
extended downward — appropriate for our 18-year-old bodies.

### `kuczmarski2002cdc` — CDC 2000 Growth Charts — **MISMATCH on the age**

Document identity confirmed: *Vital Health Stat* 11(246), May 2002,
ISBN 0-8406-0575-7. Note the cover erratum "Table 24 percentile column headings
aligned correctly 6/30/2010" — this report has itself had a column-alignment
defect, so every value below was taken only after checking that the **M column
equals the 50th-percentile column** on the same row, which is the defining
property of the LMS method and proves the columns are not shifted.

**Our claim** (Methods; Supplement §S4): male 67.3 kg and female 56.2 kg are the
CDC growth-chart **50th-percentile values for 18-year-olds**; female height
163 cm matches the CDC 50th percentile.

**Ground truth, Table 22 (weight, 2–20 years) and Table 23 (stature):**

| age interval | boys M = P50 (kg) | girls M = P50 (kg) |
|---|---|---|
| 214–214.99 months (17.83 y) | **67.28992603** | **56.22969564** |
| 215–215.99 months | 67.46863255 | 56.31922030 |
| **216–216.99 months (18.0 y)** | **67.64281378** | **56.40963105** |

**Both of our weights are the P50 at 214–214.99 months, i.e. 17 years
10 months — not at 18 years.** The match is exact to the rounding
(67.29 → 67.3; 56.23 → 56.2) and it is the *same* age point for both sexes, so
this is a systematic lookup offset, not a coincidence. The true CDC P50 at
18.0 years is **67.64 kg** and **56.41 kg**.

Discrepancy **against the weights actually used** (67.3 / 56.2 kg, which is the
basis the manuscripts state): 0.34 kg male (0.51 %) and 0.21 kg female
(0.37 %). Against the *unrounded* 214-month CDC values (67.28992603 /
56.22969564) the gaps are 0.35 and 0.18 kg, i.e. 0.52 % and 0.32 %.

⚠️ Corrected 2026-07-26: this line previously read "0.35 kg male (0.5 %) and
0.21 kg female (0.4 %)", which silently mixed the two bases — 0.35 is measured
against the unrounded CDC value, 0.21 against the rounded weight in use. Under
**either** basis the male gap exceeds 0.5 % (0.51 % or 0.52 %), which is why
the "within 0.5 %" wording carried by paper.tex, supplement.tex and
manuscript.md was replaced by the two absolute differences.

Physiologically trivial either way, but the sentence "50th-percentile values
for 18-year-olds" is inaccurate as written.

**Height is fine.** Girls' stature P50 at 216–216.99 months = **163.156 cm**,
rounding to the 163 cm we use, and independently matching Pulse's own
`heightStandardFemale_cm = 163.0`. Boys' stature P50 at the same age is
176.28 cm, which confirms the boys/girls block attribution.

⚠️ **Do not fix this by changing the bodies.** 67.3 kg and 56.2 kg are baked
into 1,280 completed runs and into the published blood-volume literals
(4,802.63 mL and 3,996.09 mL, both re-derived from these exact weights). Only
the *description* of their provenance is in question. For joint decision.

### Summary

| key | verdict |
|---|---|
| `atls2018` | MATCH |
| `nadler1962` | MATCH (one word, "modest", to weigh) |
| `evans2021sepsis` | MINOR MISMATCH (">= 65" is the superseded wording) + WEAK SUPPORT on the drift-threshold row |
| `mancia2023esh` | MISMATCH (bib note says DBP > 120, ESH says >= 110; "> 180" should be ">= 180") |
| `kuczmarski2002cdc` | MISMATCH (values are the P50 at 17.83 y, not 18 y) |

Per the stop protocol: recorded, **nothing modified**. Tier 1 is now 12/12
audited.

---

## Addendum 2026-07-26 — the CDC offset is exactly two rows, and the preregistration names the intended age

Found while sweeping for residual loci, after the corrections above were
applied.

`preregistration.md:19-22` (erratum of 2026-05-19) states the provenance:

> **Weights** (67.3 kg M, 56.2 kg F): CDC 50th-percentile weight-for-age
> values at 18 years **(216.5 months)**, inherited from the companion
> `Pulse_translation_new` pediatric-translation pipeline.

216.5 months is the CDC data-file `Agemos` midpoint of the interval that
Table 22 labels "216-216.99 months" — that is, the *correct* 18-year row, whose
M values are 67.64 and 56.41 kg. The weights actually in use, 67.3 and 56.2 kg,
are the row two earlier: "214-214.99 months", `Agemos` 214.5, M = 67.28992603
and 56.22969564.

**The offset is exactly two rows / two months**, identical for both sexes. That
is the signature of an off-by-N lookup in the source spreadsheet, inherited
from the pediatric pipeline, not a design choice.

### This is NOT a protocol deviation — do not describe it as one

What the preregistration committed to was the two bodies: 67.3 kg / 180 cm and
56.2 kg / 163 cm. Those are exactly what was run, in all 1,280 simulations.
Nothing about the experiment departed from what was registered.

What is wrong is only the *sentence explaining where the two weights came
from*, in the preregistration erratum and in every document that inherited it.
A provenance misstatement, not a design change. Any correction should say so
plainly, so a reader does not mistake it for an unregistered protocol change.

### Open question for the author

The corrections applied above state what the weights *are* (the 214-month P50,
within 0.5 % of the 18.0-year value). They do not yet mention that the
preregistration names 216.5 months. Whether to declare that explicitly --- as
was done for the "3 cm" referent confusion --- is undecided. Consistency argues
for declaring it; brevity argues for leaving the corrected provenance to speak
for itself.

### Addendum — decomposition of the Nadler sex gap (2026-07-26)

The word "modest" was removed from paper.tex and replaced by the two computed
values (73.0 and 63.8 mL/kg). A percentage was deliberately NOT used: the gap is
12.58 % on a male denominator but 14.39 % on a female one, so a bare percentage
would have been ambiguous.

One further caution, recorded so it does not migrate into the text later. The
9.18 mL/kg gap between the two bodies under Nadler is not wholly a sex effect.
Applying the MALE equation to the FEMALE body gives 71.21 mL/kg, so:

    72.96 (M body, M eq)
  - 71.21 (F body, M eq)  ->  1.75 mL/kg from body size
  - 63.78 (F body, F eq)  ->  7.43 mL/kg from the sex-specific coefficients
    total                      9.18 mL/kg

The sentence now in the paper states the two values and does not attribute the
whole gap to sex, so it is unaffected. But "a difference of about 9 mL/kg due to
sex" would overstate it by roughly 1.8 mL/kg.

---

## Tier 2 — `bray2019`, audited 2026-07-26 — **MISATTRIBUTION (six claims), true sources located**

Source read: the article PDF supplied by the author (Springer redirects to an
auth portal; Europe PMC returns `hitCount 0` for the DOI). Identity confirmed:
*SN Comprehensive Clinical Medicine* (2019) **1:362–377**, DOI
10.1007/s42399-019-00053-w, author list matching `paper.bib`. Extraction
completeness checked: 15 running heads for a 16-page article. Searched by
multiple synonyms for each claim, not by a single string.

**Depth:** full text.

### What Bray 2019 does support — MATCH

| Our claim | Verbatim |
|---|---|
| 20 ms fixed timestep | "The numerical models currently execute with a **time step of 20 ms** to ensure all physiology features of interest are captured, while maintaining real-time execution for the simulation." |
| real-time capable, lumped-parameter, open-source | Abstract, verbatim |
| Apache 2.0 | "adherence to an Apache 2.0 license" |
| C++ implementation, Java/C# secondary frameworks | "the Pulse Physiology engine is implemented in C++ … Secondary frameworks are implemented in both Java and C#" |
| data model language coverage | "supports a wide range of languages, including C++, Java, Python, C#, and JSON" |
| ARM single-board execution | Table 6, benchmark across ARM Cortex-A boards |

### What Bray 2019 does NOT contain — six claims we cite it for

Verified absent. **The claims themselves are correct; the attribution is not.**
True sources located in the Pulse engine tree and recorded here.

| # | Our claim | Our locus | **True source** |
|---|---|---|---|
| 1 | `BV = 65.6 · weight_kg^1.02` mL | `supplement.tex:627` | `SetupPatient.cpp:534`, carrying Pulse's own `/// \cite Morgan2006Clinical` |
| 2 | 5-compartment lung (carina, L/R anatomic dead space, L/R alveoli) | `paper.tex:328`, `supplement.tex:91` | `docs/Methodology/RespiratoryMethodology.md:115–122` |
| 3 | No inertance | `supplement.tex:132` (limitation 11) | `docs/Methodology/RespiratoryMethodology.md:1117–1119`, `:1150` |
| 4 | No dicrotic notch, no retrograde flow, idealised valves | `supplement.tex:134` (limitation 12) | `docs/Methodology/CardiovascularMethodology.md:614` |
| 5 | "roughly 10–15× real time" | `supplement.tex:91` | **not Bray** — ledger anchors `T3.s027.speed_lower/upper` attribute it to our own S027 measurement |
| 6 | Unity binding; Windows/Linux/macOS/Android/iOS | `supplement.tex:91` | **still open** — Unity, iOS, Android, macOS, Windows, Linux all absent from Bray 2019 |

### Verbatim for the four located in Pulse's own documentation

**(1) Blood volume — `src/cpp/engine/human_adult/whole_body/controller/SetupPatient.cpp:531–536`**

```cpp
//Blood Volume ---------------------------------------------------------------
/// \cite Morgan2006Clinical
double bloodVolume_mL;
double computedBloodVolume_mL = 65.6 * pow(weight_kg, 1.02);
double bloodVolumeMin_mL = computedBloodVolume_mL * 0.85; //Stage 1 Hypovolemia
double bloodVolumeMax_mL = computedBloodVolume_mL * 1.15;
```

Pulse's own primary source, from `engine/docs/Sources.bib:3467`:

> `@Book{Morgan2006Clinical}` — *Clinical Anesthesiology*, G. Edward Morgan Jr.,
> Maged S. Mikhail, Michael J. Murray; Lange Medical Books/McGraw-Hill, 2006, 4th ed.

**Bonus cross-validation.** The `* 0.85` on line 535 is the mechanism behind the
4,082.24 mL male blood-volume floor we report from S027: 4,802.63 × 0.85 =
4,082.24 exactly. Pulse labels it "Stage 1 Hypovolemia". Our empirical finding
and the engine source agree to the cent.

**(2) Five compartments — `docs/Methodology/RespiratoryMethodology.md:115–122`**

> "The current version of the %Respiratory Model represents the two lungs and
> associated airways as **five major functional units, or compartments, that are
> designated as the carina, right and left anatomic dead space, and right and
> left alveoli**. In the model, the carina compartment represents the anatomical
> region from the airway at the trachea. The right and left anatomic dead space
> compartments represent the bronchi and their branching bronchioles … The right
> and left alveoli compartments correspond to the collection of alveoli where gas
> exchange occurs."

Word-for-word our sentence. The attribution is the only thing wrong.

**(3) Inertance — `docs/Methodology/RespiratoryMethodology.md:1117–1119`, `:1150`**

> "One extension of the linear model is the addition of inertance in the lumped
> parameter model. **Inertance is not included in the model** on the assumption
> that inertia does not play a significant role under conventional tidal
> breathing …"
> "Airway inertance is assumed to be negligible at normal respiratory frequencies."

**(4) Dicrotic notch + retrograde flow + valves — `docs/Methodology/CardiovascularMethodology.md:614`**

> "This is the dicrotic notch, which occurs from slight flow reversal from the
> aorta back into the left ventricle before the valves close @cite
> korakianitis2005notch . **This is not currently being modeled in the engine**,
> but improvements in the circuit model, including the addition of inertance and
> **diodes that allow retrograde flow**, will likely enable the engine waveform
> to capture more detail."

One sentence supports all three limbs of our limitation-12 row. Note our
supplement already *labels* this row "Pulse documentation" while citing
`bray2019` — the text knew, the citation did not.

### Still open

- **ECG P-wave / T-wave merge at high heart rate** (second limb of limitation 12) —
  not yet located; not in the cardiovascular passage above.
- **Claim 6** (Unity binding, OS platform list) — no source found in Bray 2019.
  Must be traced to the Pulse website / repository README or dropped.
- **Claim 5** — confirm that "10–15×" is ours (S027) and re-attribute accordingly;
  citing Bray for our own measurement is the wrong direction of credit.

### Status and required decision

`bray2019` itself is a **MATCH** for what it does support. The six above are a
**MISATTRIBUTION**, not a factual error: nothing needs retracting, four need a
citation swap to the Pulse Methodology documentation, one to our own S027, one
still needs a source or must go.

Per the autonomy pact, no manuscript was modified. This needs a joint decision on
one point: the Pulse Methodology docs are not currently a bib entry. Adding
`pulsedocs` (or per-file entries) to `paper.bib` is a bibliography change, and
whether to cite Pulse's own source (`Morgan2006Clinical`) *in addition* for the
blood-volume formula is a judgement call worth making explicitly.

### Resolution of the six claims — decided and verified 2026-07-26

Author arbitration obtained on all points. The resolution below is verified, not
assumed; the manuscripts are still untouched pending the reattribution commit.

**Decision: cite the ONLINE rendered documentation, not the local clone.** The
`pulse.kitware.com` pages are the Doxygen render of the `docs/*.md` files. All four
passages were re-fetched from the live site on 2026-07-26 and compared against the
local tree: **character-identical**, modulo Doxygen turning `@cite key` into a
bracketed number. A reviewer can therefore check every quote without cloning the
repository, and this matches the convention already used by `pulsevent` and
`pulsefaq` in `paper.bib`.

| Claim | Page verified live 2026-07-26 |
|---|---|
| `BV = 65.6 · W^1.02`, floor `× 0.85`, ceiling `× 1.15` | `_patient_methodology.html` |
| 5-compartment lung | `_respiratory_methodology.html` |
| No inertance | `_respiratory_methodology.html` |
| No dicrotic notch / retrograde flow / valves; ECG P-T merge | `_cardiovascular_methodology.html` |

**Upgrade on claim 1.** The formula is not only in `SetupPatient.cpp`; it is a
documented table row in `docs/Methodology/PatientMethodology.md:56`, rendered at
`_patient_methodology.html`:

> `| Blood Volume Baseline | Optional | Bv[mL] = 65.6W[kg]^{1.02} | Bv * 0.85 | Bv * 1.15 | Above Stage 1 Hypovolemia. @cite Morgan2006Clinical |`

This is strictly better than citing a source line: the **0.85 floor is documented
engine behaviour**, not an implementation detail inferred from code. It independently
corroborates the 4,082.24 mL male floor measured in S027.

**Claim 4 — ECG P/T merge, source found.** `CardiovascularMethodology.md:287`
(figure caption), verbatim: *"Due to the high heart rate, the engine output is
summing together the P and T waves. In the image from PhysioNet, the output is not
summed together as dramatically, due to the slight physiological compression of the
waveform that the current ECG system and heart model do not support."* Mechanism at
`:175`: *"The waveform is not a calculated value; the current ECG system does not
model the electrical activity of the heart."*
**This is NOT our observation.** The atlas measures no ECG waveform — its six outputs
are steady-state means of HR, MAP, Vt, SpO2, PaO2, PaCO2. Attributing this to our
own experiments was considered and **rejected as fabrication**, notwithstanding that
the claim is true.

**Claim 6 — Unity / platform list, partially sourced, partially DROPPED.**
`docs/Markdown/About.md:13`: *"easy cross-platform deployment on all standard
operating systems (Windows, Mac, Linux, and ARM) and multiple languages (C++, C#,
Java, Unity)"*. Python is not there — it comes from `bray2019` (data-model languages).
**Android and iOS are absent from About.md.** They appear only in the changelog
(`Versioning.md:147`, iOS build support, **Pulse v4.2.0, October 2023**;
`:332-333`, Android ARMv7a/ARMv8a). A changelog records an addition; it does not
attest continued support, and the authoritative current-state page omits both.
Decision: **drop Android and iOS**, keep the rest with split attribution.

**Claim 5 — "10-15x real time" is ours.** Re-attributed to S027
(`T3.s027.speed_lower` / `speed_upper`); no bibliographic citation on that clause.

**Morgan2006Clinical — UNVERIFIABLE, stays OUT of the bibliography.**
Time-boxed search closed 2026-07-26. Findings: (a) the coefficients `65.6` / `1.02`
appear **nowhere** in the indexed literature — not in Nadler 1962, not in any
allometric blood-volume paper; (b) Morgan & Mikhail's *Clinical Anesthesiology* is
real and is the cited source of the QxMD / Medscape "Estimated Blood Volume"
calculator, which is built on **per-kilogram values by age and sex**, not a power
law; (c) the calculator page redirects to an authentication wall, so the table itself
could not be read.
Reading: Pulse most likely **fitted** a power law to Morgan's per-kg values — at
70 kg the formula returns ~71 mL/kg, squarely the textbook adult figure. That is an
inference, not a verified fact.
Consequence: we do not write "Morgan's allometric formula". We write the chain of
possession, which is verifiable end to end — the engine computes the formula and
*itself* attributes the underlying estimates to Morgan. `Morgan2006Clinical` is not
added to `paper.bib` or `references.bib`, because the rule is that we never cite a
document we have not opened.

**Bibliography mechanics.** One entry, `@misc{pulsedocs}` (`@misc` proven safe with
`sn-nature.bst`; `pulsevent` and `pulsefaq` already use it), titled *"Pulse Physiology
Engine: source code and documentation"* — broad enough to cover the methodology
pages, `About.md`, and the source tree. To be added to **both** `preprint_npj/paper.bib`
**and** `preprint/references.bib`. `note` pins release `REL_4_3_1` (tagged
2025-01-24) and the consultation date. Version safety verified directly:
`git diff REL_4_3_1 REL_4_3_2` touches 7 files, **none under `docs/`**.

Pending edits, held under HARD STOP until the single reattribution commit:
`supplement.tex:91` (split attribution, drop Android/iOS), `:132` and `:134`
(cite key on both, label on 132 only), `:627`/BV loci, the `pulsedocs` entry in the
two bib files, and the `bray2019` `number = {5}` metadata discrepancy.

---

## Tier 2 — seven references audited 2026-07-26

Metadata (title / authors / journal / volume / issue / pages / DOI) checked against
`preprint_npj/paper.bib` for each. All seven **MATCH** on metadata.

| Key | Our claim | Locus | Verdict | Depth |
|---|---|---|---|---|
| `katsoulakis2024digitaltwins` | digital twins for health "proliferating across healthcare"; in-silico trials, device design, synthetic patients | `paper.tex:130` | **MATCH** | full text (PMC10960047) |
| `webb2020` | Pulse "applied to ventilator-safety what-if analysis" | `paper.tex:130` | **MATCH** (but see OVERCLAIM below) | full text |
| `figueroacasas2016` | asynchrony "well documented clinically in volume-control ventilation" | `paper.tex:263`, `supplement.tex:572` | **MATCH** | full text |
| `thille2006` | trigger lock produces "a form of patient--ventilator dyssynchrony" | `paper.tex:267` | **MATCH, under-claimed** | full text |
| `blanch2015` | that dyssynchrony is "clinically undesirable" | `paper.tex:267` | **MATCH, correctly hedged** | full text |
| `akoumianaki2014` | esophageal pressure as specialised confirmation | `paper.tex:267` | **MATCH** | abstract (title-level claim) |
| `sinderby1999` | diaphragm electrical activity as specialised confirmation | `paper.tex:267` | **MATCH** | full text |

Notes worth keeping:

- **`thille2006` supports us more strongly than we claim.** Verbatim: *"Ineffective
  triggering was associated with a less sensitive inspiratory trigger."* Our
  intervention makes the trigger less sensitive (a fixed -2 cmH2O threshold replacing
  the modelled patient trigger), so the clinical literature predicts exactly the cost
  we describe. Our wording is conservative; no change required, but this is available
  if a reviewer challenges the mechanism.
- **`blanch2015` is correctly hedged on our side.** Its own Conclusions state:
  *"Further investigations would be necessary to establish a causal relationship
  between asynchrony and outcome."* We wrote "clinically undesirable", not "causes
  mortality", and Blanch's *"Diagnosing and correcting asynchronies should be a
  priority"* supports exactly that. Do **not** strengthen this wording later.
- **`figueroacasas2016`** verbatim: *"Lower tidal volumes during volume control
  ventilation resulted in more patient-ventilator dyssynchrony in most patients with
  or at risk for ARDS."* The driver differs from ours (Vt size vs. set rate on a
  normal-compliance lung); `paper.tex:263` already states the specific conditions are
  our own in-silico finding, so the distinction is already made in the text.
- **`akoumianaki2014`** verified at abstract depth only (AJRCCM paywall). The claim is
  title-level and the abstract confirms *"respiratory muscle effort assessment"*, so
  abstract depth is adequate. Full author list confirmed: 19 named authors + PLUG
  Working Group (ESICM); our bib's first three are correct.

### OVERCLAIM — `webb2020` vs. our novelty sentence — needs a joint decision

`webb2020` itself is a clean MATCH for "ventilator-safety what-if analysis". The
problem is the **next sentence**, `paper.tex:130`:

> "Yet despite this footprint, prior work has probed Pulse's *outputs* --- validating
> them against reference data, or, in one external study, falsifying
> intervention--outcome behaviour on a real cohort --- while no public map of how the
> engine responds across its user-facing *input* envelope (sensitivity, silent
> clamping, solver divergence) has been published."

Webb 2020 did **not** only probe outputs. Verbatim, p. 7: *"All possible combinations
of patient parameters for the final model required evaluation of 12,642 unique
patient and ventilator combinations defined by the following parameter space"* --
PEEP 10-20 step 5, static compliance 10-50 step 1, diffusion-impairment severity
0.3-0.9 step 0.1, two patients per simulation. That is a factorial **input** sweep,
and it is nine times larger in run count than our 1,280.

Why our novelty claim nevertheless survives, precisely:

| Webb 2020 | This atlas |
|---|---|
| pressure-mode ventilation | VC-AC |
| RR **fixed at 20**, I:E **fixed**, resistance **fixed at 5**, PIP derived, FiO2 solved for SpO2 > 90 % | 7 operational inputs swept (HR, SBP, DBP, RR, Vt, FiO2, PEEP) |
| sweeps **patient pathophysiology** (compliance, diffusion impairment) + PEEP | sweeps the **user-facing operational envelope** |
| two identical 70 kg patients | male/female reference bodies compared |
| ranks 9 parameters by outcome correlation (ANOVA, eta^2, Table 1) over the *difference* between the two patients, against one composite safety score; no clamping detection, no divergence mapping | Morris mu*/sigma per input per output, four-flag classifier, per-cell reliability map |
| a specific clinical question (ventilator sharing) | engine characterisation |

So the second half of our sentence ("no public map ... input envelope") **holds**. The
first half ("prior work has probed Pulse's *outputs*") is **imprecise as a blanket
statement**, because it silently includes `webb2020`, which swept inputs.

Risk: this is the most attackable sentence in the paper for a reviewer who knows
Webb 2020 -- and Webb is a Kitware first-party paper, so an npj reviewer plausibly
does. Opportunity: naming Webb's 12,642-run sweep and stating what it did *not*
characterise makes our contribution sharper and pre-empts the objection.

**Per the autonomy pact, nothing was modified.** This is a change to a scientific
claim (the novelty framing) and requires an explicit decision. It is **outside** the
scope of the authorised reattribution commit, which covers only the six Bray claims,
the `pulsedocs` entry, and the `bray2019` `number` metadata.

### `sinnige2026active` — register row

Claim at `paper.tex:322`: ACTiVE *"improved overall ventilation quality yet showed no
difference in ventilator-free days or mortality relative to protocolized conventional
ventilation."* Verified against the JAMA record on **2026-07-24** (Discussion
close-out, commit `d13fdcb`), where the wording was tightened from "several" to
"overall ventilation quality" and an orphan citation removed. **MATCH.** Not
re-verified on 2026-07-26; depth as recorded on 2026-07-24.

### Tier 2 remaining

Three book references -- `west2020respiratory`, `marino2013icu`, `marini2018critical`
-- have no online full text. To be handled separately.

---

## Reattribution applied 2026-07-26/27 — plus three corrections to this register

### Bibliography design — decision changed on evidence

The single-`pulsedocs`-entry plan was **abandoned before implementation**. Reason:
`preprint/references.bib` already carried `pulsevent`, `pulserespmethod` and
`pulsesystem`, and `preprint_npj/paper.bib` already carried `pulsevent` and
`pulsefaq` -- i.e. **both files already use one entry per cited documentation page**.
A single repo-wide entry would have broken that convention in both files and
duplicated `pulserespmethod`, which already points at the page sourcing our
respiratory claims. Author arbitration: follow the existing per-page convention.

Applied: `pulserespmethod`, `pulsecardiomethod`, `pulsepatientmethod`, `pulseabout`
added to `paper.bib` (4 new); `pulsecardiomethod`, `pulsepatientmethod`, `pulseabout`
added to `references.bib` (3 new, `pulserespmethod` reused and its note extended);
`ref-pulseabout` added to the monograph's manual reference list.
Every URL was fetched and the quoted sentence verified verbatim before being cited.
`_about_pulse.html` was found by navigating the site index after `about.html` 404'd.

### CORRECTION 1 — I mis-recorded claim 5. The 10--15x figure is NOT our measurement.

The earlier entry in this register stated that the ledger anchors
`T3.s027.speed_lower/upper` attribute "roughly 10--15x real time" to our own S027
work. **That is wrong.** Read from the source:

```
claim_id="T3.s027.speed_lower"
source_file="Pulse_translation_new/pulse_engine_literature_review.md §1.5"
computed_value=PULSE_DOC_SPEED_LO_X      # PULSE_DOC_..., not a measurement of ours
```

The true origin is the companion project's literature-review summary table, §1.5,
which reads: *"Speed: 10-15x real time on standard hardware / Languages: C++, with
bindings for Python, Java, C#, Unity / Platforms: Windows, Linux, macOS, Android,
iOS, ARM"*. **Our entire supplement sentence was copied from that table** -- the
speed figure, the Unity binding and the Android/iOS list all come from there, and
were then cited to `bray2019`.

**And the number itself is wrong.** Pulse's own FAQ (`docs/Markdown/FAQ.md:31`,
rendered at `_f_a_q.html`, which we already cite as `pulsefaq`) states:

> "The engine currently runs at about **5 to 10 times real time**, depending on your
> machine's specifications."

So the companion table overstates Pulse's own documented figure, and our supplement
and monograph inherited the overstatement.

**Action taken: NONE on the text.** Changing 10--15x to 5--10x is a magnitude change
to a published claim, which exceeds the authorised reattribution scope (that scope
covered re-attribution, not re-valuation). The clause was restored **verbatim** to
its pre-edit state in both `supplement.tex:91` and `manuscript.md:430`, still reading
"roughly 10--15x real time on commodity hardware" with no citation of its own.
**Decision required.** Options: correct to Pulse's documented 5--10x citing
`pulsefaq`; or drop the speed clause entirely (it is decorative, not load-bearing);
or measure it ourselves and cite that. Recommendation: cite `pulsefaq` with Pulse's
own figure -- it is the primary source, already in both bibliographies, and the
claim then costs nothing to defend.

**RESOLVED 2026-07-27.** Author arbitrated for the recommendation. Applied: the
clause now reads "at about 5--10x real time, depending on machine specifications"
citing `pulsefaq` in `supplement.tex:91` and `manuscript.md`. The FAQ sentence was
re-verified **online** at `_f_a_q.html` and against `docs/Markdown/FAQ.md:31` on
2026-07-27 -- identical, and the enclosing FAQ question is literally "How fast does
the physiology engine run?", so the metric matches our claim exactly. Rendering
confirmed in both PDFs; `10--15` now occurs **zero** times in either document.

Two consequences handled in the same change, neither optional:

- **The ledger anchors were carrying the wrong value and the wrong provenance.**
  `PULSE_DOC_SPEED_LO_X` / `HI_X` were 10.0 / 15.0 with `source_file` pointing at the
  companion literature review, under a comment asserting that review "itself cites
  Pulse's docs page" -- a hop that does not hold. Now 5.0 / 10.0, bound to the FAQ
  URL with the verbatim sentence. `T3.s027.timestep_ms` was repointed in the same
  pass from the same secondary record to Bray et al. 2019, which states "a time step
  of 20 ms" verbatim (value was already correct; only the provenance was wrong).
- **The `@pulsefaq` orphan had to be closed.** Citing `pulsefaq` in the monograph
  while it had no entry in the manual provenance appendix would have compounded the
  defect, so `ref-pulsefaq` was added. Note this appendix is a provenance list, not
  the rendered bibliography -- pandoc/citeproc generates the real one from
  `references.bib`, where `pulsefaq` was always present. The gap was therefore a
  completeness defect in the appendix, not a broken citation.

Verified after the change: audit **272/272 - 97/97 - 26/26, exit 0**; three PDFs and
three DOCX rebuilt; supplement reference numbering re-checked entry by entry
([2] respiratory, [3] FAQ, [4] About, [7] cardiovascular, [21] patient) and the
monograph's author-date label confirmed (`Kitware, Inc. 2026c` = Pulse FAQ).

---

## APPLIED 2026-07-27 — the `paper.tex:130` rewrite, in a CORRECTED form

### ⛔ The text banked below was FALSE and was NOT the text applied

The banked version ended `it reports no ranking of input influence`. Re-verification
against the **PLoS full-text XML** (downloaded and grepped locally, because a WebFetch
summary answered `sensitivity: NOT PRESENT` and fabricated a quotation) shows that
**Webb publishes exactly such a ranking**: Table 1, one-way ANOVA, `Outcome
Correlation (eta^2)`, nine rows, of which **two are his own swept inputs** —
`dCstat = 0.46` (**tied** highest of the nine, level with `dEtCO2 = 0.46`) and
`dDIF = 0.02`. Shipping the banked sentence
would have replaced an imprecise claim with a demonstrably false one, against a
Kitware first-party paper.

> **Correction, 2026-08-17 — `(highest of the nine)` was wrong, and the nine rows
> are now recorded in full.** Re-read from the PLoS full-text XML today, Table 1
> in its entirety: `dCstat 0.46`, `dEtCO2 0.46`, `dA-a gradient 0.18`,
> `dOSI 0.11`, `dOI 0.11`, `dP/F 0.08`, `dDIF 0.02`, `dMAP 0.02`,
> `dS/F 0.02`. There are **two ties**, not one clear maximum: `dCstat` shares the
> top with `dEtCO2`, and `dOSI` shares fourth with `dOI`. The earlier note also
> left `dOI` without a value. Webb's own text agrees: *"Five parameters were
> found to be most correlated to outcomes"* — a set, never a ranked winner.
>
> **No manuscript text changes.** This error lived only in the register: the
> sentence shipped to `paper.tex:139` says Webb *"does rank parameters by outcome
> correlation"* and never names a top parameter, so nothing published depended on
> the false superlative. Re-checked in the same pass, all seven of that sentence's
> clauses hold against the XML (12,642 verbatim; compliance 10–50 step 1;
> DIF 0.3–0.9 step 0.1; PEEP 10–20 step 5; "Two equal-sized 70 kg patients are
> modeled"; the ANOVA runs on "the absolute value of the difference … from patient
> one and patient two", i.e. the mismatch; one composite green/yellow/red scoring;
> RR fixed 20, I:E fixed 1:2, total respiratory resistance fixed 5).
>
> One nuance worth keeping for a future reader: only 2 of the 9 ranked rows are
> swept inputs (`dCstat`, `dDIF`); the other 7 are derived clinical measures.
> PIP and FiO2 also vary across Webb's grid but as *derived* quantities (PIP from
> 6 mL/kg given PEEP, FiO2 found by simulation for SpO2 > 90 %), which is why our
> sentence lists three swept axes and not five.

A second error in the same sentence: `two identical 70 kg bodies`. Webb writes
**`Two equal-sized 70 kg patients are modeled`** and the two patients deliberately
*differ* in compliance and DIF — `287 unique COVID-19 patients` (= 41 compliances x
7 DIF) are created and paired, and the Discussion says `conceivable **mismatched**
patient lung compliance and oxygenation`. "Identical" inverted his design.

Third: **12,642 is not reconstructible** from the published grid (41 x 7 x 3 = 861;
41 does not even divide 12,642 — the count is over patient *pairs*). It must
therefore be quoted as **Webb's own count**, never described as a product a reader
could recompute.

**Text actually applied** (author chose the long option, 2026-07-27):

> Webb et al.'s ventilator-sharing study~\cite{webb2020} does sweep inputs ---
> 12{,}642 unique patient and ventilator combinations spanning respiratory
> compliance, diffusion impairment and PEEP --- and does rank parameters by outcome
> correlation. That ranking, however, is over the \emph{mismatch} between two
> equal-sized 70~kg bodies sharing one ventilator, scored against a single composite
> safety outcome, under pressure-mode ventilation with respiratory rate, I:E ratio
> and respiratory resistance held fixed; it resolves neither each input's influence
> on each physiological output, nor input clamping, nor solver divergence.

Every clause re-checked line-by-line in the XML: RR `Fixed at 20`, I:E `Fixed at
1:2`, total respiratory resistance `Fixed at 5`, PEEP `10 to 20 in increments of 5`,
compliance `10 to 50 in increments of 1`, DIF `0.3 to 0.9 in increment of 0.1`,
`Mechanical ventilator (one per simulation)`, green/yellow/red composite scoring on
tidal volume and SpO2, and `pressure mode ventilation` as Webb's own phrase. On
divergence, Webb states a rule (`If a steady state cannot be achieved, those model
parameters are rejected`) but reports no map of it — hence "resolves", not "mentions".
Audit after application: **272/272 - 97/97 - 26/26, exit 0.**

### Superseded banked text (kept for traceability — DO NOT USE)

> Yet despite this footprint, no public map of how the engine responds across its
> user-facing \emph{input} envelope --- which inputs dominate which outputs, where
> inputs are silently clamped, and where the solver diverges --- has been published.
> Most of this work probes Pulse's \emph{outputs}: validating them against reference
> data, or, in one external study, falsifying intervention--outcome behaviour on a
> real cohort. Webb et al.'s ventilator-sharing study~\cite{webb2020} does sweep
> inputs --- 12{,}642 combinations of respiratory compliance, diffusion impairment
> and PEEP --- but under pressure-mode ventilation, with respiratory rate, I:E ratio
> and respiratory resistance held fixed, on two identical 70~kg bodies, and in
> service of a single clinical safety question: it reports no ranking of input
> influence, and characterises neither input clamping nor solver divergence.

Every assertion verified in Webb's PDF: 12,642 verbatim p. 7; compliance 10--50
step 1, DIF 0.3--0.9 step 0.1, PEEP 10--20 step 5; "pressure mode ventilation does
not enforce delivery of a set volume"; RR fixed 20, I:E fixed 1:2, total respiratory
resistance fixed 5; "Two equal-sized 70 kg patients are modeled".

**Two deliberate restraints, do not undo them later:** we do NOT write "no
sensitivity analysis" (Webb uses the phrase "rapid sensitivity evaluation" himself);
we write "reports no ranking of input influence", which is exact and checkable. And
we use no superlative such as "the largest published sweep" -- unverifiable.

Cost: about +55 words to the Introduction. After applying, re-run the audit: the
crosswalk anchor `T1.01` counts occurrences of "1{,}280" and is unaffected, but any
new numeric literal (12{,}642, 70~kg) may need a crosswalk entry -- check the exit
code rather than assuming.

## Tier 2 — the three textbooks: claims extracted 2026-07-27, verification NOT yet run

Method note first: **the earlier locus-mapping grep was defective.** It matched only
`\cite{key}` and missed `\cite[Ch.~5]{key}`, which is how all three textbooks are
cited. The defect surfaced only because `marino2013icu` rendered as [9] in the
supplement bibliography while the grep claimed it was uncited. **The eight Tier 2
references were re-checked with a corrected pattern and are unaffected** -- the loci
already audited are the only ones. Total distinct keys cited across paper + supplement: 35.

| Ref | Locus | Claim |
|---|---|---|
| `west2020respiratory` | `paper.tex:275`, `supplement.tex:580` | alveolar-gas-equation ceiling ~663 mmHg at sea level |
| `west2020respiratory` | `paper.tex:167` | same ceiling, justifying the deliberately conservative 600 mmHg PaO2 bound |
| `west2020respiratory` Ch. 4 | `supplement.tex:223` | CO2-narcosis threshold incompatible with a conscious steady state |
| `west2020respiratory` | `paper.tex:342` | cited generally among the sources of the detector's physiological bounds |
| `marino2013icu` Ch. 5 | `supplement.tex:213` | survival-incompatibility thresholds for extreme bradycardia / tachycardia in ICU practice |
| `marino2013icu` Ch. 21 | `supplement.tex:223` | CO2-narcosis threshold (with West Ch. 4) |
| `marini2018critical` Ch. 1 | `supplement.tex:213` | same heart-rate thresholds |
| `marini2018critical` Ch. 1 | `supplement.tex:219` | threshold for sustained cellular oxygen extraction (with Severinghaus P50) |
| `marini2018critical` | `paper.tex:167` | sustained SpO2 < 50 % incompatible with a stable simulated steady state |

**The largest block self-verifies and needs nothing.** The three West alveolar-gas
loci do not depend on reading the book: the paper prints its own inputs and the
arithmetic checks exactly. FiO2 1.0 x (760 - 47) = 713; 40 / 0.8 = 50;
713 - 50 = **663 mmHg**. The stated gap also checks: 663 - 643 = **20 mmHg**.
West is the canonical source for this equation.

**The clinical-threshold claims are low risk by construction.** They sit in the
*justification column* of a bounds table whose bounds are themselves preregistered.
The textbooks support a preregistered choice; they do not carry a result.

**Method note, recorded 2026-07-27:** the line that previously stood here read
"Planned verification (authorised? NOT YET -- ask before running)". That was a
**defect**. `CLAUDE.md`'s autonomy pact already exempts read-only investigation
("looking is not acting"); waiting for a go on a table-of-contents lookup cost a
session for nothing. Never bank "awaiting authorisation" on a read again.

### RESULT 2026-07-27 — metadata VERIFIED, chapter pointers largely WRONG

**Metadata (OpenLibrary by ISBN, machine-readable) — all three MATCH:**

| Key | Resolved record | Our bib | Verdict |
|---|---|---|---|
| `west2020respiratory` | West & Luks, LWW, **Oct 13 2020**, 232 pp, ISBN 9781975139186 | 2020, 11th, Wolters Kluwer/Lippincott | **MATCH** (nit: OpenLibrary and shop.lww.com give the 11th-edition title as *West's Respiratory Physiology*, without ": The Essentials"; the LWW ebook platform keeps the longer form — genuinely ambiguous, not corrected) |
| `marino2013icu` | Marino, LWW, **2013**, 1080 pp, LCCN 2013038977, OCLC 859374985, LC class `RC86.7 .M369 2014` | 2013, 4th, LWW | **MATCH** |
| `marini2018critical` | Marini & Dries, LWW, **Nov 03 2018**, 832 pp, ISBN 9781496302915 | 2018, 5th, Wolters Kluwer | **MATCH on edition/ISBN; year OPEN, see below** |

### Definitive identification of the three supplied copies (2026-07-27)

Six files were supplied for three works. Two were unusable and are recorded so
they are not mistaken for the books: one Marino file is a **1-page HTML error
page** ("503 Service Temporarily Unavailable") and one Marini file is **0 bytes**.
Every remaining file was identified from its own copyright page, never from its
filename -- which was wrong in two cases out of four.

| File label | Actually is | Cited edition | Usable for our citation? |
|---|---|---|---|
| West "2011" | **9th edition**, © 2012, ISBN 978-1-60913-640-6, LCCN 2011019298, sole author J. B. West | 11th, 2020, West & Luks | **No** -- wrong edition |
| West "2016" | **10th edition**, © 2016 Wolters Kluwer, West & Luks, 249 pp | 11th, 2020, West & Luks | **No** -- wrong edition |
| Marino "2013" | **4th edition**, "Preface to Fourth Edition", © 2014 Wolters Kluwer Health/LWW, **ISBN-13 9781451121186**, 1075 pp | 4th, 2013, ISBN 978-1-4511-2118-6 | **Yes** -- ISBN matches exactly |
| Marini "2018" | **Fifth edition**, **ISBN 978-1-4963-0291-5**, © **2019** Wolters Kluwer (copyright page read as a rendered image; that page carries no extractable text) | 5th, 2018, ISBN 978-1-4963-0291-5 | **Yes** -- ISBN matches exactly |

**Two year discrepancies, both benign but both worth recording.**

*Marino.* Our bib says 2013; the copyright page says © 2014. OpenLibrary gives
publish_date 2013 and the Library of Congress call number reads `RC86.7 .M369
2014`. This is the ordinary imprint-year / copyright-year gap and 2013 is
defensible.

*Marini.* Our bib says 2018; the copyright page says **© 2019 Wolters Kluwer**
and prints "2019" at its head, while OpenLibrary and the retailers give a
publication date of **3 November 2018**. A book released late in one year
routinely carries the following year's copyright. Either year is citable, but
they are not interchangeable and the choice should be deliberate: **2019**
follows the copyright page, **2018** follows the publication date. **Left as
2018, unchanged, pending a decision.**

The PDF page counts (1075 Marino, 1148 Marini) exceed the printed page counts
(1080 and 832) because these files are assembled per-chapter documents with
front matter; this is not a version discrepancy.

**Chapter-level verification:**

| Citation | Chapter actually is | Verdict |
|---|---|---|
| `[Ch.~2]{west2020respiratory}` — anatomical dead space | Ch 2 "Ventilation" | **OK** |
| `[Ch.~5]{west2020respiratory}` — alveolar-gas equation | Ch 5 "Ventilation-Perfusion Relationships---How Matching of Gas and Blood Determines Gas Exchange" | **OK** |
| `[Ch.~4]{west2020respiratory}` — CO2 narcosis | Ch 4 = "**Blood Flow and Metabolism**"; CO2 is Ch 6, ventilatory control Ch 8 | **WRONG** |
| `[Ch.~5]{marino2013icu}` — HR survival thresholds | Ch 5 = "**Alimentary Prophylaxis**" (Section II, Preventive Practices) | **WRONG** |
| `[Ch.~21]{marino2013icu}` — CO2 narcosis | Ch 21 = "Oximetry and Capnometry"; hypercapnia is Ch 20 | **WRONG** (off by one) |
| `[Ch.~26]{marino2013icu}` — Vt delivery capability | Ch 26 = "Conventional Modes of Ventilation" | **UNVERIFIABLE** (topically plausible, not confirmable) |
| `[Ch.~1]{marini2018critical}` — HR + O2 extraction | Ch 1 "Hemodynamics" (Section I) | **UNVERIFIABLE** (title plausible, content unreachable) |

**Evidence grade, stated honestly.** The Marino **3rd**-edition TOC is primary
(Library of Congress `catdir/toc/ecip0618/2006025971.html`, fetched in full): its
Ch 5 = "Venous Thromboembolism", Ch 21 = "Oxygen Inhalation Therapy" — neither
supports our claims either. The **4th**-edition and West 11th-edition chapter lists
come from **search-engine summaries of publisher pages**, which contradicted each
other once before converging; the 4th-edition list is corroborated by a coherent
`+2` offset from the LC-verified 3rd edition. `lwwhealthlibrary.com`,
`catdir.loc.gov` (direct), and the Villanova catalogue all returned 403 or an
anti-bot page. **No Library of Congress TOC exists for LCCN 2013038977** (four
catdir path patterns tried, all 404). Internet Archive holds **only older editions**
(Marino 1991/1997/1998; West 1995/2000/2005/2016; Marini 1989/1997/2006/2010) —
**none of the three cited editions**. Full text is therefore genuinely out of reach.

**Loci affected — the count is larger than first reported.** 11 chapter-pointed
citations in `supplement.tex` (L213, 217, 219, 221, 223, **262, 268, 272**) and
10 more in the monograph `manuscript.md` (L1091--1096, **1125, 1130, 1133, 1135**,
3049). Plus three `internal_note` fields in `paper.bib` (L264, L340, L351) whose
chapter *titles* exist in no edition ("Hemodynamic Drug Infusions and the
Cardiovascular Critical Patient"; "Chapter 21 (Acid-Base Disorders)" — that is a
*section* name covering Ch 28--30 in the 3rd edition). `references.bib` is clean.

**Cross-consensus with open sources is a safety net, not a substitute.** Finding an
open source that says the same thing does not prove the textbook says it; it would
replace one unverified citation with another. Use it only to *re-source* a threshold
that turns out to be doubtful.

### 2026-07-27 — West read in primary text, but in the WRONG EDITION (9th, 2012)

The author supplied a PDF of West's *Respiratory Physiology: The Essentials*. Its
filename says 2011; the copyright page says **Ninth Edition, copyright 2012**, sole
author John B. West, no Luks. We cite the **11th edition, 2020, West & Luks**. It
therefore **cannot verify `west2020respiratory`**. Three findings all the same, two
good and one serious.

**1. The chapter structure is stable, and this is now primary-source evidence.** The
9th-edition table of contents is **identical in chapter titles** to the 11th-edition
list that had until now rested only on two concordant search-engine summaries:
1 Structure and Function · **2 Ventilation** · 3 Diffusion · **4 Blood Flow and
Metabolism** · **5 Ventilation-Perfusion Relationships** · 6 Gas Transport by the
Blood · 7 Mechanics of Breathing · 8 Control of Ventilation · 9 Respiratory System
Under Stress · 10 Tests of Pulmonary Function. This independently confirms that
Ch. 4 is **not** a CO2 chapter, i.e. the removal of `[Ch.~4]{west2020respiratory}`
was correct.

**2. Both surviving West pointers are confirmed in running text.** Anatomical dead
space: *"The normal value is about 150 ml"*, under the heading `Anatomic Dead Space`
on book p. 19, inside Chapter 2 (which the TOC starts at p. 12). Alveolar-gas
equation: *"A simplified form of the alveolar gas equation is P_AO2 = P_IO2 -
P_ACO2/R + F"*, book p. 59, inside Chapter 5 (TOC: pp. 56-76), and applied again on
p. 74. `[Ch.~2]` and `[Ch.~5]` are therefore **correct in the 9th edition** and, given
the identical structure, near-certainly correct in the 11th.

**3. 🔴 CO2 narcosis does not appear in West at all.** Searched for `CO2 narcosis`
and `carbon dioxide narcosis`: **zero hits in the entire book**. The only occurrences
of `narcosis` are **inert gas narcosis** (nitrogen narcosis in diving), Chapter 9,
an unrelated phenomenon. Supplement §S3 cites `west2020respiratory` --- alongside
`marino2013icu`, itself unverifiable --- for the PaCO2 upper bound of 120 mmHg as a
"CO2 narcosis threshold incompatible with conscious steady-state". The chapter
pointer was already stripped; what this shows is that **the reference itself may not
support the claim**, which is a different and more serious problem than a wrong
chapter number.

⚠️ Caveat stated honestly: this is the 9th edition. The 11th was revised by Luks, a
clinician, and could in principle have added the term. But *The Essentials* is a
physiology primer whose clinical companion is a separate volume (*Pulmonary
Pathophysiology: The Essentials*), so its absence here is more likely structural than
edition-specific. **Nothing modified. For joint decision.**

#### Follow-up the same day — the 10th edition (2016) settles it as far as it can be settled

The author then supplied the **10th edition, copyright 2016 Wolters Kluwer, West &
Luks** (again not the cited 11th edition). This is the
decisive edition to check, because its own preface states that **Luks joined as
coauthor for this edition** and that *"another innovation of this new edition are
clinical vignettes for each of the first nine chapters"*. If a clinical notion such
as CO2 narcosis were going to enter the book, it would enter here.

**It does not.** `CO2 narcosis` / `carbon dioxide narcosis`: **zero hits**, exactly as
in the 9th. `narcosis` again occurs only as **inert gas narcosis** in the diving
section. `hypercapnia` occurs, but only as an *effect* to be explained --- Chapter 5
Key Concepts: *"The two causes of hypercapnia, or CO2 retention, are hypoventilation
and ventilation-perfusion inequality"* --- with no threshold and no link to
consciousness.

A wider sweep for the *concept* rather than the term (`unconscious|consciousness|
coma|stupor|obtund|somnolen|drowsi|narcotic|CNS depress`) returns six passages, and
**not one attributes loss of consciousness to CO2**: a vignette about a patient
already comatose; *"morphine and barbiturates that depress the central drive"*, i.e.
drugs causing hypoventilation, not CO2 causing coma; a **carbon monoxide** poisoning
vignette (not dioxide); unconsciousness from **hypoxia** at altitude; and coma from
**nitrogen** narcosis.

**Conclusion.** Across two consecutive editions, including the one that deliberately
added clinical content, West's *Essentials* contains no CO2-narcosis threshold and no
CO2--consciousness link at all. Citing `west2020respiratory` for *"CO2 narcosis
threshold incompatible with conscious steady-state"* is therefore very probably
**unsupported**, and the PaCO2 upper bound of 120 mmHg is left with **no verified
source**, since its only other citation, `marino2013icu`, is unverifiable.

**Two useful confirmations arrived with the same file**, both now resting on two
independent editions rather than on a search summary: anatomic dead space *"about
150 ml"* under the `Anatomic Dead Space` heading of **Chapter 2**, and the alveolar-gas
equation on a page whose running header reads verbatim **"66 CHAPTER 5"** --- direct
proof of the chapter, not an inference from a page range.

**Nothing modified. For joint decision.** Options: re-source the bound to a reference
that does state a hypercapnia/consciousness threshold; keep West only for the
alveolar-ventilation physics and drop the narcosis framing; or check the 11th edition
through legitimate institutional access before deciding. Note that the *bound itself*
is preregistered and is not in question --- only the sentence justifying it.

### CORRECTION 2 — the `bray2019` metadata flag was a FALSE POSITIVE

This register previously flagged `number = {5}` as a possible discrepancy because the
article PDF header prints only `1:362-377`. Crossref (`api.crossref.org`, the
authority for issue assignment) returns: container-title *SN Comprehensive Clinical
Medicine*, **volume 1, issue 5**, pages 362-377, 2019. **Our bib entry is correct**;
the PDF header simply omits the issue. Nothing to fix. The monograph's manual entry
(`manuscript.md:3539`) already reads `1(5):362-377` and is likewise correct.
Author list also confirmed against Crossref, 9 authors, order matching.

### CORRECTION 3 — pre-existing orphan citation found in the monograph

`@pulsefaq` is cited in `manuscript.md` but has **no** `[]{#ref-pulsefaq}` entry in
the manual reference list (the list has `ref-pulsevent`, `ref-pulserespmethod`,
`ref-pulsesystem`, and now `ref-pulseabout`). Pre-existing, unrelated to this work,
and deliberately **not** fixed here so as not to widen a bounded commit. To be
handled with the deferred reference-metadata pass.

### Observation for the deferred hyperlink pass

In the rendered PDFs the Kitware URLs extract as `https://pulse.kitware.com/ f a q.html`
(underscores appearing as spaces, and letter-spacing in the monograph). This affects
the pre-existing `pulsevent` and `pulsefaq` entries identically, so it is a rendering
or extraction artefact, not something introduced here -- but the hyperlink pass should
confirm the links are live in the actual PDF.

### Verification of the applied change

Audit **272/272 anchors, 97/97 paper crosswalk, 26/26 monograph anchors, exit 0.**
`paper.pdf`, `supplement.pdf`, `manuscript.pdf` and the three DOCX twins rebuilt.
Verified **in the rendered PDFs**, not in the source: zero unresolved `[?]` citations;
all four new references present in the reference lists; limitation rows 11 and 12 now
read "Pulse documentation [2]" and "Pulse documentation [7]"; the blood-volume formula
carries [21] = Patient methodology; the paper's 5-compartment sentence carries
[22] = Respiratory methodology; the platform sentence reads "Java, C#, and Unity [3]
and an interface for Python [1] ... Windows, Mac, Linux, and ARM"; and Android/iOS
occur nowhere except inside the new bibliographic note that explains their exclusion.

---

## Phase 3 completed 2026-07-28 — every assertion-bearing `note` / `internal_note` field re-read at source

The first pass (commit `f38e0c3`, 2026-07-27) fixed the textbook chapter maps that
had survived in `references.bib`. This pass finishes the sweep: **every remaining
bibliography field that asserts a fact** — not merely a PMID or an access date — was
checked against its primary source, in **both** `.bib` files.

**The direction of the twin defect reversed.** On 2026-07-27 a correction landed in
`paper.bib` and was forgotten in `references.bib`. This time `paper.bib` carried the
stale state: its three textbook notes still declared the editions unreachable ("the
4th-edition text is unreachable", "no full text is reachable", "verified at
table-of-contents level only, never against the full text") — statements the copies
supplied later the same day had already superseded in `references.bib`. Both files
now carry the same state.

### What was verified, and how

| Field | Assertion | How verified 2026-07-28 | Verdict |
|---|---|---|---|
| `pulsepatientmethod` (both) | BV = 65.6 W^1.02, min BV×0.85, max BV×1.15, "Above Stage 1 Hypovolemia", Morgan credit | Local clone, `docs/Methodology/PatientMethodology.md` **L56**, read cell by cell | **MATCH**, verbatim, including the `@cite Morgan2006Clinical` tag |
| `pulserespmethod` (paper) | 5-compartment lung; no-inertance limitation | Same clone, **L116–118** and **L1117–1120** | **MATCH**; the inertance sentence continues "as opposed to high-frequency ventilation" — our quote stops before that clause, which changes nothing |
| `pulserespmethod` (references) | ARDS severity map 0.3 / 0.6 / 0.9; piecewise-linear modifiers at 0.0/0.3/0.6/0.9/1.0; P/F values *not* on this page | **L1176** verbatim: "These severities are mapped to corresponding modifiers through piecewise linear functions, calibrated at key transition points: 0.0 (no change), 0.3 (mild), 0.6 (moderate), 0.9 (severe), and 1.0 (maximum)"; table caption **L1189**; the value 340 occurs nowhere on the page | **MATCH**, all three limbs |
| `pulsecardiomethod` (both) | dicrotic notch / retrograde flow; P- and T-wave merge | **L614** and **L287** | **MATCH** |
| `pulseabout` (both) | cross-platform sentence; Android/iOS not claimed | `docs/Markdown/About.md` **L13** | **MATCH** |
| `pulsesystem` (references) | "low fidelity clinical approach" | `docs/Methodology/SystemMethodology.md` **L261–263**, under "Assumptions and Limitations" | **MATCH** |
| `pulserespmethod` (paper) | "docs/ is byte-identical in REL_4_3_2" | `git diff REL_4_3_1..REL_4_3_2 -- docs/` returns **nothing**; the whole-tag diff is 7 files — `.gitignore`, `CMakeLists.txt`, `cmake/external/External_Eigen3.cmake`, `dockcross.cmake`, `xcompile.bat`, `xcompile.cmake`, and a 4-line change to the C# binding `src/csharp/pulse/engine/PulseEngine.cs`. **Not one file under `src/cpp`**, i.e. no physiology source | **MATCH** — and an independent re-confirmation of the 4.3.1 pin |
| `brower2000` (both) | "landmark 861-patient RCT", 6 mL/kg PBW | Primary abstract, PMID 10793162 | **MATCH**, with a nuance now recorded: "The trial was stopped after the enrollment of 861 patients" — 861 is enrolment at early stopping, not a planned sample size |
| `singer2016` (both) | septic shock, MAP ≥ 65 mmHg | Primary abstract, PMID 26903338: "a vasopressor requirement to maintain a mean arterial pressure of 65 mm Hg or greater **and serum lactate level greater than 2 mmol/L** … in the absence of hypovolemia" | **MATCH on the MAP limb**; the lactate limb was absent from both notes and has been added, so the criterion is never quoted as MAP-only |
| `atls2018` (paper) | "Class I as a loss of up to 15 %" | Table 3-1 and its section heading, re-read | **MATCH in substance**; ATLS's own wording is "**<15 %**", now recorded verbatim so "up to 15 %" is never re-quoted as ATLS's phrasing |
| `nadler1962` (paper) | standard per-kilogram range | Verbatim p. 226 and both prediction equations copied into the note from the primary scan | **MATCH** |
| `kuczmarski2002cdc` (both) | provenance of the two body weights | Tables 22 / 23; the 214-month finding written into the note itself | **MATCH on the values, MISMATCH on the age label** — pre-existing open question, unchanged |
| `severinghaus1979` (both) | P50 anchor | **The abstract prints the equations themselves** (PMID 35496); Eq. (1) evaluated numerically | **MATCH on 27 mmHg**, plus two findings below |
| `webb2022vent`, `pulsevent`, `nin2017`, `evans2021sepsis`, `mancia2023esh`, `herman2017salib`, `lundberg2020tree`, `lundberg2017`, `figueroacasas2016`, `thille2006`, `blanch2015`, `akoumianaki2014`, `sinderby1999`, `katsoulakis2024digitaltwins`, `sinnige2026active` | — | Audited 2026-07-24/26/27; re-read here for drift, none found | **unchanged** |
| `bray2019`, `webb2020`, `cornish2023`, `morris1991`, `campolongo2007`, `iwanaga2022`, `ards2012`, `wilkinson2016`, `munafo2017` | — | Metadata only, no assertion-bearing field | **nothing to sweep** |

### `severinghaus1979` — the source was reachable after all, and it settles two things

The note said "Severinghaus 1979 itself was not re-read for this figure". It never
needed hunting down: **the PubMed abstract prints all four equations in full.**
Evaluating Eq. (1), `S = (((Po2^3 + 150·Po2)^-1 × 23,400) + 1)^-1`:

| Point | Value from the equation |
|---|---|
| P50 | **26.86 mmHg** |
| S(27 mmHg) | 0.5035 |
| S(26.6 mmHg) | 0.4936 |
| S(20 mmHg) | **0.3198** |

1. **The manuscripts' "approximately 27 mmHg" is right on both sources** — the
   equation gives 26.86 mmHg, West's 11th ed. p. 200 gives "about 27 mm Hg".
2. **The 26.6 mmHg that `paper.bib` carried before 2026-07-27 was not invented.**
   26.6 appears in the paper's **Eq. (4)**, the Bohr-coefficient normalisation
   ("(Po2/26.6)(0.184) - 2.2"). It is simply not the P50 of Eq. (1). The 2026-07-27
   note called it "a figure never verified here", which was unfair to it. Both `.bib`
   files now record where it actually comes from — so nobody reinstates it as a P50,
   and nobody undoes the correction either.

### 🔴 OPEN — three decisions for the author; nothing was modified in the manuscripts

> ### ✅ STALE — OPEN-1 and OPEN-1b were CLOSED three hours after this block was written
>
> This block was committed in `0abca30` at **2026-07-28 10:11**. Commit
> **`49a62e6`, 2026-07-28 13:25**, *"Make the two Severinghaus-derived numbers
> match the equation we cite, and say which curve it is"*, fixed both loci and
> this register was never updated. Re-verified at source on **2026-08-01**:
>
> - `supplement.tex:223` now reads **"SpO$_2 \approx 0.32$"** — the value the
>   equation gives (0.3198). Zero occurrences of `0.30` remain in either file.
> - `manuscript.md:1029` now reads **"PaO2 ≈ 23 mmHg"** (equation: 22.99), and
>   the withdrawn *"below the cellular oxygen-extraction threshold"* clause is
>   gone from the source. It survives only in `preprint/build/mono.txt`, a
>   gitignored build artefact.
>
> That commit also went **further than this block asked**: all three loci now say
> *"the **standard** Severinghaus dissociation curve"*, because the paper's own
> abstract fits the *standard* curve (pH 7.40, 37 °C, PaCO2 40 mmHg) and these
> bounds are applied in severe ARDS, where acidosis and hypercapnia shift the
> curve rightward — so an acidotic patient's real saturation at PaO2 = 20 mmHg
> is **lower** than 0.32. Quoting two decimals without "standard" claimed a
> physiological precision that does not exist.
>
> **Do not re-open or re-apply either item.** Kept below for the record only.

**OPEN-1 — `severinghaus1979`, SpO2 at PaO2 = 20 mmHg.** `supplement.tex:221` and
`manuscript.md:1095` justify the PaO2 lower bound with "PaO2 = 20 mmHg corresponds to
SpO2 ≈ 0.30 on the Severinghaus dissociation curve". The cited equation gives
**0.3198**. Written as "0.30" it also claims two-decimal precision the sentence does
not need; "≈ 0.32" is exact and "≈ 0.3" would be defensible. Nothing downstream moves
— the bound is 20 mmHg either way — but a reviewer who recomputes lands on 0.32.
**A number in the body text is not mine to change.**

**OPEN-1b — `manuscript.md:1018-1020`, the `implausible` worked example, two defects in
one sentence.** The monograph illustrates the flag with "SpO2 = 0.40, which on the
Severinghaus 1979 dissociation curve corresponds to PaO2 ≈ 22 mmHg, below the cellular
oxygen-extraction threshold."

1. *Arithmetic.* By the cited equation, SpO2 = 0.40 corresponds to PaO2 = **22.99 mmHg**,
   i.e. ≈ 23. At 22 mmHg the equation gives SpO2 = 0.3735.
2. *Withdrawn justification, survived here.* "Below the cellular oxygen-extraction
   threshold" is the SpO2 rationale **withdrawn on 2026-07-27** by commit `0472424`:
   Marini's critical-oxygen-delivery concept has no number, sits in Ch. 2, and is about
   delivery rather than saturation. The paper was corrected in that same commit —
   `paper.tex:167` now reads "though briefly survivable in a real patient — is
   incompatible with a stable simulated steady state over the evaluation window" — but
   **the monograph locus was missed**.

Suggested replacement, aligned on the wording the paper already carries and asserting
nothing unsourced: "…corresponds to PaO2 ≈ 23 mmHg, a value no patient could hold in a
stable 60 s steady state." Not applied: it is body text.

**OPEN-2 — `west2020respiratory`, the year.** Unlike the notes swept above, `year` is
**rendered in the bibliography**. It reads 2020, the publication date (13 Oct 2020,
OpenLibrary and publisher); the supplied copy's copyright page reads **2021**. Both
are citable, they are not interchangeable, and the choice should be deliberate.

**OPEN-3 — `marini2018critical`, the year.** Same shape: `year` = 2018 (published
3 Nov 2018) against a copyright page reading **2019**. Recorded as open on 2026-07-27
and still open; both `.bib` files now carry the note, so it cannot be silently
resolved in one file only.

### Scope note — what this pass deliberately did not touch

`atls2018` and `nadler1962` exist only in `paper.bib`. That is **correct, not an
omission**: neither is cited in the monograph, whose blood-volume section states the
floor and the dose-response without invoking the ATLS classification or Nadler's
equations. Verified by grep over `preprint/manuscript.md`.




---

# Phase 4 — 2026-07-29 — **bibliographic METADATA** swept against external authorities

**A new axis, not a repeat.** Everything above this line audits whether each
source *says what we make it say*. This phase audits the **bibliographic
record itself**: authors, title, journal, year, volume, issue, pages, DOI,
PMID, edition, URL. Commissioned by the author on 2026-07-29 as point 3 of
the three final pre-submission audits.

Scope: **all 40 entries of `preprint_npj/paper.bib` and all 31 of
`preprint/references.bib`** (30 keys are shared, so 41 distinct works).

## Instruments

| Authority | Used for | Coverage |
|---|---|---|
| NCBI E-utilities `esummary` (db=pubmed) | every entry carrying a `pmid` | **18 / 18 records returned** |
| Crossref REST API | every entry carrying a `doi` | **25 / 25 records returned** |
| arXiv API `export.arxiv.org/api/query` | `cornish2023` | entry retrieved |
| DBLP publication API | `lundberg2017` (NeurIPS, absent from Crossref) | record retrieved |
| OpenLibrary | the four books, by ISBN | 3 by ISBN, 1 by title search |
| Local `Pulse_engine_adults_Gitlab` clone | Pulse release dating | `git log REL_4_3_1` |
| HTTP GET | the 9 URL-identified entries | **9 / 9 → HTTP 200** |

Scripts, kept in the session scratchpad and re-runnable: `bib_dump.py`,
`bib_metadata_verify.py` (fetch + cache to `bib_authority.json`),
`bib_metadata_compare.py` (field-by-field diff), `bib_followups.py`,
`bib_followups2.py`, `bib_url_and_atls.py`, `bib_note_leak.py`,
`bib_leak_locate.py`.

## Result

**45 entry-checks ran against an authority record. 28 came back clean on every
field. 17 raised a flag — and 16 of the 17 are artefacts of the comparison or
of the authority's own house style, not defects in our bibliography.**

### The 16 non-defects, itemised so nobody re-opens them

| Pattern | Entries | Why it is not a defect |
|---|---|---|
| PubMed truncates the end page (`520-31` for `520–531`) | `akoumianaki2014`, `ards2012`, `blanch2015`, `brower2000`, `nadler1962`, `sinderby1999`, `singer2016`, `thille2006` | PubMed's house abbreviation. **Our full ranges are the correct form and the one Nature style wants.** |
| Crossref stores only the first page | `singer2016` (`801`), `sinnige2026active` (`874`) | Crossref record is incomplete; PubMed gives `801-10` and `874-884`, matching us |
| PubMed splits a collective author, so the "first author" and the author count differ | `ards2012` (ARDS Definition Task Force), `brower2000` (ARDS Network) | We deliberately carry the collective name as the leading author, which is how both papers are cited |
| Crossref returns the journal name with an HTML entity, `Environmental Modelling &amp; Software` | `campolongo2007` | encoding, not content |
| Comparator split `Munaf{\`o}` into `munaf o` | `munafo2017` | defect **in the comparison script**, not in the `.bib` |
| Crossref truncates the title at the colon | `ards2012`, `sinnige2026active` | PubMed carries the full titles, and they match ours exactly |

### Verified correct, against an authority, field by field

`bray2019` · `evans2021sepsis` · `figueroacasas2016` · `herman2017salib` ·
`iwanaga2022` · `katsoulakis2024digitaltwins` · `kuczmarski2002cdc` ·
`lundberg2020tree` · `morris1991` · `nin2017` · `severinghaus1979` ·
`webb2020` · `webb2022vent` · `wilkinson2016` — in `paper.bib`; and
`bray2019` · `brower2000` · `emeriaud2023` · `evans2021sepsis` ·
`figueroacasas2016` · `herman2017salib` · `iwanaga2022` · `lundberg2020tree` ·
`morris1991` · `nin2017` · `severinghaus1979` · `webb2020` · `webb2022vent` ·
`wilkinson2016` — in `references.bib`.

---

## Findings

### ✅ M-1 — `lundberg2017`: page range confirmed at an authority

Absent from Crossref (NeurIPS proceedings are not deposited). **DBLP**:
*A Unified Approach to Interpreting Model Predictions*, venue NIPS, year 2017,
pages **4765-4774**, authors Scott M. Lundberg and Su-In Lee. Our
`howpublished` reads "Advances in Neural Information Processing Systems 30
(NeurIPS 2017), pp. 4765--4774". **Exact match.** No change.

### ✅ M-2 — `cornish2023`: still a preprint, so the citation form is right

> **Superseded 2026-09-14.** The paper has since been published in the Journal
> of Machine Learning Research, 27(152):1–52 (2026), and both `.bib` files now
> cite it there. See the addendum "`cornish2023` has been published in JMLR" and
> its resolution, at the end of this register. The finding below was true on
> its date and is kept as written.

arXiv API, entry `2301.07210`:

- `id` = `http://arxiv.org/abs/2301.07210v4` — **v4**, the version the content
  audit read
- title *Causal Falsification of Digital Twins* ✓
- authors Rob Cornish, Muhammad Faaiz Taufiq, Arnaud Doucet, Chris Holmes ✓
- published 2023-01-17, last updated **2023-11-02**
- **`arxiv:journal_ref` absent** → the paper has still not appeared in a
  journal, so citing it as an arXiv preprint remains correct
- no arXiv DOI registered (Crossref returns 404 for
  `10.48550/arXiv.2301.07210`), so its absence from our entry is right

The only thing not recorded is the **version**. The content audit above read
v4 specifically; the `.bib` says only `arXiv:2301.07210`. Optional
improvement, no error.

### ✅ M-3 — the four books check out

| Entry | ISBN in `.bib` | OpenLibrary record | Verdict |
|---|---|---|---|
| `west2020respiratory` | 978-1-9751-3918-6 | *West's Respiratory Physiology*, John B. West & Andrew M. Luks, LWW, **Oct 13 2020** | ✓ |
| `marini2018critical` | 978-1-4963-0291-5 | *Critical Care Medicine*, John J. Marini & David J. Dries, LWW, **Nov 03 2018** | ✓ |
| `marino2013icu` | 978-1-4511-2118-6 | *ICU Book*, Paul L. Marino, Lippincott Williams & Wilkins / Wolters Kluwer, **2013** | ✓ |
| `atls2018` | *(none recorded)* | *ATLS Advanced Trauma Life Support 10th Edition Student Course Manual*, first published **2018**; "American College of Surgeons. Committee on Trauma" is a recorded author form | ✓ |

### 🟩 M-4 — **OPEN-2 and OPEN-3 are resolved. Both years are already correct; change nothing.**

Both open items asked whether the `year` should follow the publication date or
the copyright page.

- **OPEN-2 `west2020respiratory`** — our `year = 2020`. Publisher and
  OpenLibrary both give **13 October 2020**. The supplied copy's copyright page
  reads 2021.
- **OPEN-3 `marini2018critical`** — our `year = 2018`. OpenLibrary gives
  **3 November 2018**. Copyright page reads 2019.

Both gaps are the standard next-year imprint convention on a book published
late in the calendar year. The publication date is the citable date, two
independent sources agree with what we already have, and **the rendered
bibliography is correct as it stands**. Recorded as resolved; nothing modified,
because nothing needed modifying.

### ✅ M-5 — all nine cited URLs are live

Every entry whose bibliographic identity is a URL was fetched: **9 / 9 returned
HTTP 200, none redirected.** `arxiv.org/abs/2301.07210` plus the eight Kitware
documentation pages (`_about_pulse`, `_cardiovascular_methodology`,
`_circuit_methodology`, `_f_a_q`, `_mechanical_ventilator_methodology`,
`_patient_methodology`, `_respiratory_methodology`, `_system_methodology`).

Also confirmed while checking: a PyMuPDF text extraction of `paper.pdf` renders
these as `pulse.kitware.com/ f a q.html`, which reads like broken underscores.
**It is an extraction artefact.** The page image and the PDF link annotations
both carry the underscores intact.

### 🟡 M-6 — `mancia2023esh`: our title is shorter than the authoritative one

Our entry: *2023 ESH Guidelines for the management of arterial hypertension*.

PubMed (PMID 37345492): *2023 ESH Guidelines for the management of arterial
hypertension The Task Force for the management of arterial hypertension of the
European Society of Hypertension: Endorsed by the International Society of
Hypertension (ISH) and the European Renal Association (ERA).*

Crossref carries the same long form, truncated slightly earlier.

Nature style says the title should be "written exactly as it appears in the
work cited" (`SG`, References). Two defensible readings, and this register does
not pick one:

1. **The long form is the record title.** Two independent authorities carry it.
2. **The short form is the article's actual title.** What follows it is the
   task-force byline, concatenated into the title field by the indexers — an
   artefact of how *Journal of Hypertension* deposits guideline documents, not
   part of the title on the page.

**Author decision. Nothing modified.**

### 🟡 M-7 — `sinnige2026active` has no `pmid` field, though its PMID is confirmed

Seventeen sibling entries in `paper.bib` carry a `pmid`. This one does not.

Resolved at source today: an `esearch` on `10.1001/jama.2025.24384[doi]`
returns exactly one hit, **PMID 41361939**, and its `esummary` confirms every
field we already carry — title including the `: A Randomized Clinical Trial`
subtitle, JAMA, 2026 Mar 10, **335(10)**, pp. **874-884**, six listed authors
with Sinnige JS, Buiteman-Kruizinga LA and Horn J leading.

Six authors is more than five, so the `and others` truncation is also correct
under Nature style ("more than five … only the first author … followed by
*et al.*").

The `pmid` field is never rendered (see M-9), so this is a completeness gap in
the working instrument, not a defect on the page. Ground truth re-derived and
unambiguous, no scientific claim touched → **applied**.

### 🟡 M-8 — the eight Kitware entries date to the access year, not the document year

All eight carry `year = {2026}` and render as `(2026)`.

**Pulse `REL_4_3_1` was tagged 2025-01-24** (`git log -1 REL_4_3_1` in the
local `Pulse_engine_adults_Gitlab/engine` clone; `REL_4_3_2` on 2025-08-12,
build-system only). So the documentation these entries cite is a 2025 artefact,
displayed with a 2026 date.

Only `pulsefaq` declares what 2026 means, through the one surviving rendering
note: `note = {Accessed April 2026.}`. The other seven say nothing.

Two defensible readings again:

1. **It is already correct.** Nature's own *Online material* example puts the
   access/retrieval year in the parentheses for web content, and these pages
   are living documents.
2. **It misleads.** A reader takes `(2026)` for the document's year and cannot
   tell that the object cited is v4.3.1, released January 2025.

A middle path exists that asserts nothing new: give the other seven the same
`note = {Accessed April 2026.}` that `pulsefaq` already carries. **Author
decision. Nothing modified.**

### 🟩 M-9 — the `note` fields in `references.bib` do **not** leak. Hypothesis raised and discarded.

`references.bib` carries a rendering `note` on **26 of its 31 entries**, some
very long (`pulserespmethod` 1,461 characters, `west2020respiratory` 1,241,
`marini2018critical` 1,192, `marino2013icu` 1,150 — including a dated internal
`WARNING [2026-07-27]` about a chapter mapping). `paper.bib`, fixed on
2026-07-25/26 by commits `64fe63b` and `7a46040`, has exactly **one** rendering
note left (`Accessed April 2026.`, genuinely bibliographic), plus 30
`internal_note` and 18 `pmid` fields that BibTeX never emits.

The obvious inference — that the twin defect had reappeared and the monograph
was printing PMIDs — **is wrong**, and it is written down here so nobody
re-derives it:

1. A first probe found 15 `PMID` strings in the rendered `manuscript.pdf`
   reference section. That looked conclusive.
2. Locating them precisely puts them inside **§9.7 "Verified primary references
   (full bibliographic detail)"**, a section whose own preamble says *"Each
   entry has been individually verified against its DOI or PMID during the
   literature-review pass logged in `experiments_log/santino/S010_literature_review.md`"*.
   It is hand-written prose in `manuscript.md` and deliberate scholarly
   transparency.
3. `scripts/build_paper.ps1` settles it: pandoc is invoked with
   `--citeproc --bibliography references.bib` **and
   `--metadata suppress-bibliography=true`**. Citeproc resolves inline `[@key]`
   citations to "(Author Year)" and **never emits a bibliography at all**.
   `manuscript.md` uses `[@key]` 55 times and `\cite{}` zero times.

So the only `references.bib` fields with any rendered consequence are `author`
and `year`, and the cross-file comparison found **no divergence** on either.

Standing risk worth recording: that safety rests entirely on
`suppress-bibliography=true` staying in the build script. If it is ever
removed, 26 internal annotations print at once.

Confirmed clean in the meantime: **0 `PMID` strings in the rendered
`paper.pdf` and `supplement.pdf` reference lists.** The supplement's three
`verified` hits are the words in the title of Table S1, *"Verified Pulse v4.3.1
limitations…"*, not notes.

### 🟡 M-10 — the two `.bib` files diverge on 12 keys, all the same way

Of the 30 keys present in both files, **12 differ, and every one of the 12 is
the same difference**: `paper.bib` carries `pmid = {…}` as its own field, while
`references.bib` keeps the same PMID inside its `note` string.

`ards2012` · `brower2000` · `evans2021sepsis` · `figueroacasas2016` ·
`kuczmarski2002cdc` · `mancia2023esh` · `munafo2017` · `nin2017` ·
`severinghaus1979` · `singer2016` · `webb2020` · `wilkinson2016`.

Same information, different structure — the consequence of applying the
2026-07-25/26 field rename to one file only. **No author, title, year, volume,
issue, page or DOI diverges between the two files.** Harmless while M-9 holds.

### 🟡 M-11 — two entries in `paper.bib` are cited nowhere in the paper or supplement

`marini2018critical` and `marino2013icu` appear in `paper.bib` but in no
`\cite` in either `paper.tex` or `supplement.tex`. Both are genuinely used in
the monograph (6 citations in `manuscript.md`, resolved through
`references.bib`). BibTeX simply omits uncited entries, so nothing renders and
nothing is broken; they are dead weight in the file.

Distinguish this from the scope note at the end of Phase 3: `atls2018` and
`nadler1962` live only in `paper.bib` **and are cited there** — correct, not an
omission. M-11 is the opposite case.

---

## What this phase deliberately did not do

The author routed the second half of point 3 — *"do the references make sense
where they are cited?"* — into the step-wise fact-check (point 2), so that each
`\cite` is judged with its own paragraph in view rather than in a second pass
over the same sections. Nothing about citation *placement* is decided here.

## Decisions carried forward

Open before this phase and still open: **OPEN-1** (`severinghaus1979`,
SpO2 ≈ 0.30 vs the equation's 0.3198, at `supplement.tex:221` and
`manuscript.md:1095`) and **OPEN-1b** (`manuscript.md:1018-1020`, PaO2 ≈ 22 vs
23, plus the withdrawn cellular-oxygen-extraction justification that survived
in the monograph after commit `0472424` corrected the paper).

Closed by this phase: **OPEN-2** and **OPEN-3** — see M-4, both already correct.

Newly open: **M-6** (`mancia2023esh` title form) and **M-8** (Kitware access
year).

---

# Phase 5 — 2026-08-04 — one `UNVERIFIABLE`, raised while writing the ventilation-dose caveat

## UNVERIFIABLE — exact metric coefficients of the ARDS Network predicted-body-weight equations

**What was needed.** Supplement §S6.2 and paper §2.5 quantify the relative
ventilation-dose mismatch between the two reference bodies. The first draft
expressed it per kilogram of ARDSnet *predicted* body weight, which requires
the equations

    male    PBW_kg = 50.0  + 0.91 * (height_cm - 152.4)
    female  PBW_kg = 45.5  + 0.91 * (height_cm - 152.4)

**Verification attempted 2026-08-04, four routes, all failed.**

| Route | Outcome |
|---|---|
| NEJM full text of `brower2000` (doi 10.1056/NEJM200005043421801) | HTTP 403 |
| `ardsnet.org` ventilator protocol card (PDF) | Fetched, but the PDF-to-text conversion lost the calculation box: the string "height" does not occur anywhere in the extracted text; only `= 6ml/kg PBW` and `>= 4 ml/kg PBW` survive |
| `ardsnet.org/tools.shtml` (the Network's own PBW calculator page) | Connection reset — the host is not serving |
| Moreault *et al.*, *Anesthesiology* 2017, "Calculating Ideal Body Weight: Keep It Simple" | HTTP 402 |

**One source was read and did not settle it.** Linares-Perdomo *et al.*
(PMC5442651), a peer-reviewed treatment of exactly these equations, presents
them graphically rather than in quoted text, and attributes them upstream to
McCarron MM, Devine BJ, *Ann Pharmacother* 1974;8:650–655 — i.e. the ARDS
Network equations are the Devine relation transcribed to metric
(2.3 kg/inch ÷ 2.54 = 0.9055 ≈ 0.91; 60 in = 152.4 cm).

**Why no proxy was accepted.** Search-result snippets did carry the
coefficients, and were not used: one widely-read secondary reproduction
(LITFL, *ARDSnet Ventilation Strategy*) states the female intercept as **45**
rather than 45.5. A coefficient that is wrong in a popular reproduction is
precisely the case the no-proxy rule exists for.

**Resolution — the claim was rewritten, not softened.** The manuscript does not
use the ARDSnet coefficients at all. Relative ventilation doses are computed
instead from the sex-specific ideal-body-weight relation implemented in Pulse
itself (`SetupPatient.cpp:136-146`, imperial Devine form), read in primary
source on 2026-08-04:

    male    IBW_kg = 50.0 + 2.3 * (height_in - 60)
    female  IBW_kg = 45.5 + 2.3 * (height_in - 60)

giving 74.99 kg and 55.10 kg on the two reference bodies. The manuscript says
"ideal body weight", never "ARDSnet predicted body weight". The two readings
differ by 0.1 percentage point on the reported excess (36.1 % vs 36.2 %), so
nothing scientific rests on which one is used — only the sourcing does.

**Status.** This entry is internal. It is not a limitation of the manuscript,
because the coefficients it concerns are not used there. Reopen only if the
ARDSnet metric form is ever quoted in the text; a reachable primary source
would then be required first.

**Left open deliberately.** `brower2000`'s `internal_note` still records
"Verified 2026-07-28 against the primary abstract". That remains accurate and
is enough for the two places that cite it — supplement §S3.5 and §S3.4, which
invoke the *clinical standard* (6 mL/kg PBW), not the equations. Those two
passages were reviewed during this phase and left untouched.

---

## ADDENDUM 2026-08-21 — the three Tier 1 `MISMATCH` rows are closed, verified against the repository

**Why this block exists.** The Tier 1 summary table above (the `evans2021sepsis`
/ `mancia2023esh` / `kuczmarski2002cdc` rows) still reads as three open defects,
and the CDC row further down still says "pre-existing open question, unchanged".
All three were fixed after that table was written. A register that keeps a
resolved defect in the present tense manufactures a false alarm for whoever reads
it next — which is exactly what happened during this session's sweep.

Each row below was re-tested **against the current text**, not against a later
entry in this register.

| row | what the audit required | current text | status |
|---|---|---|---|
| `evans2021sepsis` | drop the superseded ">= 65"; the 2021 guideline targets **65** | supplement §S3 now reads "initial MAP target of 65~mmHg" and "targets 65~mmHg on resuscitation" — **both** loci, no ">=" | **CLOSED** |
| `mancia2023esh` | ESH grade 3 is **>= 180** and/or **>= 110**, not "> 180" / "DBP > 120" | supplement §S3 now reads "grade~3 hypertension (SBP $\geq$ 180 and/or DBP $\geq$ 110~mmHg)" | **CLOSED** |
| `kuczmarski2002cdc` | the age label: values said to be the P50 at 17.83 y, not 18 y | superseded by the 2026-08-20 provenance work; see `audit/cdc_weight_provenance_mismatch.md` | **CLOSED** |

**On the CDC row specifically.** The "17.83 y" reading came from treating the row
used as a 214-month row. It is not one. The CDC dataset labels each row at the
half-month midpoint standing for the whole month, so `Agemos` = 216.5 is the
interval from exactly 18.0 years to 18 years 1 month — the values used are the
18.0-year P50 after all. The row that carries a 214-month label (214.5) holds
66.91783563 and 56.05304601 kg, which are used nowhere in this work. A guard in
`scripts/audit_claims.py` now pins all six CDC weights to ten digits.

**Do not read the surviving "214-month" strings as residue.** Three remain, one in
`preprint_npj/supplement.tex` and two in `preprint/manuscript.md`, and all three
are the corrective prose itself — a correction has to name the error it corrects.
Two of them are explicitly framed as "An earlier version of this passage".

**Counting note, recorded because it caused a wrong report during this session.**
Do not count verdicts in this file with a bare `grep -o "MATCH"`: `MATCH` is a
substring of `MISMATCH`, so the raw count inflates the positives and hides the
negatives. At the time of writing the file holds **61** raw `MATCH` strings =
**52** genuine `MATCH` + **9** inside `MISMATCH`. The schema table at the top of
this file also contributes one occurrence of each verdict word as a *definition*,
not as a finding, so every status count here is at least one too high unless the
schema line is excluded.

---

## Addendum 2026-09-14 — sources re-read during the supplement number audit

Recorded from `audit/number_inventory.md` §4.1, where each of these supports a
published number. Everything below was opened **in this session**; nothing is
carried over from an earlier row.

### One status change: `marini2018critical` Ch. 1 — UNVERIFIABLE → **MATCH**

The row at `[Ch.~1]{marini2018critical}` (HR + O2 extraction) was UNVERIFIABLE
because the content was unreachable. A copy of the 2018 LWW edition is in the
workspace at
`C:\Users\santi\projets\BRAIN_BIOLOGY_ML\raw\John J Marini , David J Dries -
Critical Care Medicine_ The Essentials and More (2018, LWW _ Wolters Kluwer)`.
It was searched with `scripts/pdf_probe.py` (PDF page numbers).

- PDF p. 21, verbatim: *"As a general rule, sinus heart rates exceeding (220 -
  age)/min reduce cardiac output and myocardial perfusion, even in the absence
  of ischemic disease or loss of atrial contraction."* It supports
  `supplement.tex:208`, "sinus rates exceeding (220 − age) per minute reduce
  cardiac output and myocardial perfusion".
- PDF p. 20, verbatim: *"Pathological bradycardias often depress cardiac
  output and O2 delivery"*. It supports the lower-bound clause of the same row.
- PDF p. 77 repeats the rule as *"HRmax = 220 - age"*.

The chapter is confirmed from the PDF outline: *Chapter 1 - Hemodynamics*
starts at PDF p. 12 and runs 26 pages, which places pp. 20–21 inside Ch. 1.
The pointer `[Ch.~1]` is therefore correct as well as the content.

### Re-verified, status unchanged

| key | what was re-read | result |
|---|---|---|
| `marino2013icu` Ch. 25 | 2013 copy in the same folder, PDF p. 510: *"Tidal volumes of 10 to 15 mL/kg (ideal body weight) became standard during mechanical ventilation"*; TOC: *Positive Pressure Ventilation* p. 503, *Conventional Modes of Ventilation* p. 521 (= Ch. 26) | MATCH, Ch. 25 correct |
| `west2020respiratory` Ch. 2 | 11th-edition copy (`Wests-Respiratory-Physiology-11th-edition-2021.pdf`), p. 25 and p. 30: anatomic dead space *"about 150 ml"*; p. 44 opens Ch. 2 *Ventilation* with "Anatomic Dead Space" | MATCH |
| `singer2016` | PMC4968574 (title *The Third International Consensus Definitions for Sepsis…*), SOFA table: cardiovascular *MAP ≥70 mm Hg* = 0, *MAP <70 mm Hg* = 1 | MATCH |
| `evans2021sepsis` | PMC8486643: *"we recommend an initial target mean arterial pressure (MAP) of 65 mm Hg"*; *"MAPs below a threshold, usually understood to be approximately 60 mm Hg, are associated with decreased organ perfusion, which tracks linearly with MAP"* | MATCH |
| `mancia2023esh` | journals.lww.com full text (Firecrawl): §16.2.1 *"Hypertension emergencies are conditions in which severe hypertension (grade 3) is associated with acute symptomatic HMOD"*; table: Grade 3 ≥180 and/or ≥110 | MATCH |
| `nin2017` | PMC5630225: 1,899 ARDS patients, 927 ICUs, 40 countries; maximum PaCO2 in the first 48 h; *"the cutoffs corresponded approximately to the 5th, 35th, 70th, 85th, and 95th percentiles"* | MATCH |
| `pulsevent` | mechanical-ventilator methodology page re-scraped: the six tidal-volume rows 0.0681 / 11.3 / 1.01 / 25.3 / 2.25 / 15.3 % with their Expected and Engine cells | MATCH; the printed % is a symmetric relative difference |
| `cornish2023` | arXiv 2301.07210v4, Tables 4 and 5 (PDF p. 47–48): all 15 quantities, both columns, totals 85 / 281 | MATCH |
| `kuczmarski2002cdc` | official `wtage.csv` (Firecrawl; a plain request returns "Access Denied"), P50 column at Agemos 214.5 / 216.5 / 218.5 for both sexes: 66.91783563, 67.28992603, 67.64281378, 56.05304601, 56.22969564, 56.40963105 | MATCH |

**Not re-read this session**, so each stays on its earlier record:
- `nadler1962`, the PTAB-exhibit scan (no local copy was found);
- Roza & Shizgal 1984, Eq. 3, recorded in `audit/pulse_sex_conditioned_parameters.md`.

### New MISMATCH, recorded and not acted on — `nadler1962` at `supplement.tex:815`

**Our claim** (supplement §S9, added in `20ea152`, 2026-09-03): *"against a
clinically reported range of 64--79.3~mL\,kg$^{-1}$ averaging **75 in men** and
66 in women~\cite{nadler1962}"*.

**Source, as quoted verbatim in this register's `nadler1962` entry above
(p. 226):** *"range from 64 to 79.3 ml. per kilogram of body weight with an
average of 75 ml. per kilogram. Women have smaller volumes than men with an
average of 66 ml. per kilogram."*

75 is Nadler's **overall** average, not the men's; the women's figure (66) is
correctly attributed. The paper and the monograph do not carry the "in men"
wording. The claim that Pulse does not reproduce the clinically reported
per-kilogram sex difference is unaffected.

**Status: MISMATCH — nothing modified.** Brought to the author, per the
citation-audit rule.

**Resolution, 2026-09-14.** The author chose to correct it. `supplement.tex:815`
now reads *"averaging 75 overall and 66 in women"*, which follows the verbatim
p. 226 quotation above. Nothing else in the sentence changed.
**Status: RESOLVED.**

## Addendum 2026-09-14 (evening) — `cornish2023` has been published in JMLR; the citation form is stale

Found during the monograph number audit (`audit/number_inventory.md` §5, O-6).
Everything below was opened **in this session**.

**What changed at the source.**
- arXiv posted **v5** on 2026-08-08, after this register's v4 verification. The
  v4 abstract page (Firecrawl, 2026-09-14) reads "revised 2 Nov 2023 (this
  version, v4), latest version 8 Aug 2026 (v5)".
- The v5 PDF's first line reads *"Journal of Machine Learning Research 27 (2026)
  1-52 Submitted 10/24; Revised 4/26; Published 8/26"*, with editor Ilya Shpitser
  and a CC-BY 4.0 licence pointing to `jmlr.org/papers/v27/24-1752.html`.
- That JMLR page (Firecrawl, `.firecrawl/jmlr_v27_24-1752_2026-09-14.md`) lists
  *Causal Falsification of Digital Twins*, Rob Cornish, Muhammad Faaiz Taufiq,
  Arnaud Doucet, Chris Holmes, **27(152):1−52, 2026**.
- Its BibTeX (`jmlr.org/papers/v27/24-1752.bib`): `journal = {Journal of Machine
  Learning Research}`, `year = {2026}`, `volume = {27}`, `number = {152}`,
  `pages = {1--52}`.
- The page shows no DOI, and a Crossref bibliographic query returned no match.
  The arXiv API answered "Rate exceeded" and was not read.

**What did not change.**
- The JMLR PDF was downloaded (HTTP 200, `application/pdf`) and compared with
  arXiv v5 after whitespace normalisation: 74 differing lines, all section-number
  punctuation ("1 Introduction" / "1. Introduction") and math-glyph extraction.
  Control, v4 against JMLR: 3,210 lines.
- The "Ours" columns of Tables 4 and 5 are identical in v4, v5 and JMLR.
  Hoeffding 24, 21, 13, 10, 5, 5, 3, 2, 2, 0, 0, 0, 0, 0, 0 sums to 85.
  Bootstrap 47, 46, 33, 43, 44, 19, 13, 8, 8, 4, 0, 0, 3, 12, 1 sums to 281.
  Hypotheses sum to 1,522.
- v5 and JMLR add "Manski" columns, 46 hypotheses per quantity, which the atlas
  does not use.
- The main text still reads "1,442" (JMLR text, L898).
- The appendix tables are still Tables 4 and 5; v5 says "Appendix" where v4 said
  "Supplement".

**So every number the atlas takes from Cornish still holds; the citation form
does not.**
- `paper.bib` and `references.bib` both give `journal = {arXiv preprint}`,
  `volume = {arXiv:2301.07210}`, `year = {2023}`. The rendered paper (ref. 8) and
  supplement (ref. 24) both read "arXiv preprint arXiv:2301.07210 (2023)".
- The monograph gives "arXiv:2301.07210 (November 2023)" (L3862) and
  "(November 2023, v4)" (L4034).
- The prose labels read "Cornish et al. 2023": supplement §S7 title and Table S13
  caption (first written "Table S7", corrected 2026-09-14 against the rendered
  supplement: the section is S7, its table renders as S13), monograph §4.4 title
  and Table 2.
- This register's **M-2**, *"`cornish2023`: still a preprint, so the citation
  form is right"*, was true on its date and is now stale.
- `paper.bib`'s `hennigs2026validation` note says it is "cited as a preprint
  deliberately, on the same footing as cornish2023". That footing no longer
  holds.

**Status: STALE CITATION FORM — nothing modified.** Brought to the author, per
the citation-audit rule. The options are:
- cite the JMLR article, keeping the arXiv version as a note or dropping it;
- keep the arXiv citation, pinned to v4, the version read.

Either option touches both `.bib` files, and possibly the "2023" labels.

### Resolution 2026-09-14 (night) — author's decision: cite the JMLR article

**Decision.** The author chose to cite the published article and to change the
"2023" labels to 2026.

**Applied.**
- **Both `.bib` files.** `paper.bib` and `references.bib`, entry `cornish2023`:
  - `journal = {Journal of Machine Learning Research}`, `volume = {27}`,
    `number = {152}`, `pages = {1--52}`, `year = {2026}`;
  - `url = {https://jmlr.org/papers/v27/24-1752.html}`;
  - the `volume = {arXiv:2301.07210}` field is gone.
- **The `hennigs2026validation` note** in `paper.bib` now reads "Cited as a
  preprint deliberately, as cornish2023 also was until its 2026 publication in
  the Journal of Machine Learning Research."
- **Labels "2023" → "2026".**
  - Supplement: §S7 title, Table S13 caption, "Cornish 2026 channel" column
    header, and the S17 summary row.
  - Monograph: "Key Findings at a Glance" bullet (L259), "Reader's roadmap"
    (L297), two lines of §2.10 Statistical methods overview (L1466, L1541), the
    §4 Discussion opening (L3045), the §4.4 title, Table 2 header and caption,
    and "Cornish et al. (2026)".
  - Two of those monograph labels wrap across a line break ("Cornish\n2023",
    "Cornish\net al. 2023"). A line-based search missed both; the
    rendered-PDF check found them.
- **Monograph reference 4 and the §9.7 entry.**
  - Both give JMLR 27(152):1–52 (2026).
  - Both name arXiv:2301.07210 v4 (November 2023) as the version read.
  - §9.7 adds that "the published Tables 4 and 5 keep the same counts and add
    Manski-bound columns". The first draft said the tables were "unchanged". That
    contradicted this addendum, which records the Manski columns. It was caught
    by re-reading the JMLR PDF (pp. 39–40) before the commit: the 15 "Ours" rows
    of both tables are identical to v4.

**Kept deliberately.**
- The BibTeX key `cornish2023`: renaming it would touch every citation call and
  change nothing a reader sees.
- The S017 experiment title "Cornish 2023 cross-mapping":
  - monograph L668 and L4259, and `README.md:468`;
  - it is a dated log title, not a citation label.
- The `source_file` provenance strings in `scripts/audit_claims.py` (six
  "Cornish et al. 2023" occurrences), which record the v4 read the ledger anchors
  were taken from.

**Rendered.**
- Paper ref. [8] and supplement ref. [24] read "Journal of Machine Learning
  Research 27, 1–52 (2026). URL https://jmlr.org/papers/v27/24-1752.html".
- The monograph renders "(Cornish et al. 2026)".
- The npj pair was rebuilt a second time after the line-ending normalisation of
  the two source files: identical text, 25 and 63 pages.

**Guarded.** `check_monograph_number_audit` in `scripts/audit_claims.py`:
- pins the five JMLR fields in both `.bib` files and rejects "arXiv preprint"
  there;
- requires the new labels, including the two wrapped ones;
- bans the 2023 labels on whitespace-normalised text.

A targeted reinjection of the two wrapped labels gave 2 FAIL.

**Status: RESOLVED (JMLR cited).** M-2 carries a superseded note.

## Addendum 2026-09-15 — the five chapter locators of `supplement.tex`, re-opened

**Why.** The number inventory masks `\cite[Ch.~N]{key}` as reference machinery,
so the chapter numbers never reached a residue. They were read one by one in
`audit/number_inventory.md` §8, against the cited editions opened this session
with `scripts/pdf_probe.py` (PDF page numbers, chapter ranges from the PDF
outline).

| locus | locator | what the edition shows | verdict |
|---|---|---|---|
| `supplement.tex:208` (upper bound) | `[Ch.~1]{marini2018critical}` | Ch. 1 *Hemodynamics* spans PDF pp. 12–37; p. 21: *"sinus heart rates exceeding (220 - age)/min reduce cardiac output and myocardial perfusion"* | MATCH |
| `supplement.tex:208` (lower bound) | `[Ch.~1]{marini2018critical}` | p. 20: *"Pathological bradycardias often depress cardiac output and O2 delivery"* | MATCH |
| `supplement.tex:212` | `[Ch.~2]{west2020respiratory}` | 11th edition: Ch. 2 *Ventilation* opens on p. 44, Ch. 1 on p. 18; p. 57: *"ANATOMIC DEAD SPACE This is the volume of the conducting airways … The normal value is about 150 ml"* | MATCH |
| `supplement.tex:212` | `[Ch.~25]{marino2013icu}` | p. 503 heading *"Chapter25 … POSITIVE PRESSURE VENTILATION"*, next chapter p. 521; p. 510: *"Tidal volumes of 10 to 15 mL/kg (ideal body weight) became standard during mechanical ventilation"* | MATCH |
| `supplement.tex:216` | `[Ch.~5]{west2020respiratory}` | Ch. 5 *Ventilation-Perfusion Relationships* runs from outline p. 142 to p. 187; pp. 148–149: *"A simplified form of the alveolar gas equation is …"* | MATCH |

**One precision on the 2026-09-14 addendum, verdict unchanged.** Its
`west2020respiratory` Ch. 2 row cites "p. 25 and p. 30" for *"about 150 ml"*.
Both pages fall in Chapter 1 (*Structure and Function*, pp. 18–43 by the running
text). The Chapter 2 statement that supports the pointer is on p. 57, quoted
above. The pointer and the MATCH stand; only the page evidence was imprecise.

Nothing was modified in the manuscripts.

## Addendum 2026-09-15 (evening) — four references added with the synthetic-data framing

**Why.** On 2026-09-15 the author asked for a synthetic-data framing in the
Introduction and Discussion, with a reference to the DeepSeek-V4.1-Flash
technical report. The draft came with a reference check produced outside this
repository, which was treated as a claim and redone here. The author chose the
wording and placement from options put to them (package E1–E7, `paper.tex`
only). Every source below was **read in full** before its sentence was
written; van Breugel and Victoriano from PDFs supplied by the author, after
the publisher page, OpenAlex and Semantic Scholar showed both closed.

| locus | key | what the source says | depth | verdict |
|---|---|---|---|---|
| `paper.tex:140` | `vanbreugel2024synthetic` | Abstract: *"generative-model-based data augmentation can address data scarcity; synthetic data can improve data fairness and reduce bias by accounting for underrepresented groups; and unseen scenarios may be simulated with synthetic data."* | full text | MATCH |
| `paper.tex:142` | `vanbreugel2024synthetic` | *"Generative models can be classified into mechanistic generators and data-driven generative models. Mechanistic generators17–20 (Box 2) are constructed from first principles"*; ref. 19 = Bray et al. 2019 (`bray2019`), ref. 20 = Webb et al. 2020 (`webb2020`) | full text, reference list read | MATCH |
| `paper.tex:140` | `hwang2025sim2real` | Fig. 1b *"pre-training the model on virtual patient data generated by the UVA/Padova simulator"*; Introduction *"This includes adverse and infrequent conditions … which are often underrepresented in real-world datasets"*; zero-shot evaluation on DiaTrend, OhioT1DM, ShanghaiT1DM | full text | MATCH |
| `paper.tex:335` | `hwang2025sim2real` | KL divergence *"to quantify the mismatch between each target dataset and the training domains"*; evaluation on the three public real-world datasets | full text | MATCH |
| `paper.tex:140` | `deepseek2026v41flash` | §5.1, p. 25: *"We find that, under a fixed and unremarkable optimization procedure, systematic improvements in the scale, diversity, and verifiability of synthesized data and environments account for essentially all of the observed gains."* | full text (body, appendices B–C) | MATCH, worded "attributes" |
| `paper.tex:323` | `deepseek2026v41flash` | §5.1.1 *"We formalize each task as a triplet (problem, environment, verification system)"* (agent tasks); §5.1 (iii) *"applies rigorous filtering, deduplication, and difficulty calibration"* | full text | MATCH, restricted to agent tasks |
| `paper.tex:140` | `victoriano2026sim2real` | Conclusion: *"The value of synthetic data will likely depend less on generation alone and more on careful integration with real-world data, layered validation and digital twin systems"* | full text | MATCH |
| `paper.tex:321` | `victoriano2026sim2real` | Fig. 4, five stages: internal plausibility; downstream task utility; OOD generalization; sim2real transfer; biological or clinical coupling. Stage 1: *"This includes fidelity to real-world distributions"*, which the atlas does not test, hence "only part of the first stage" | full text | MATCH |

**Metadata.** Crossref and the nature.com pages for the three articles; NCBI
esummary confirms PMID 41102316 for Hwang (a positive control on
`katsoulakis2024digitaltwins` returned 38519626). No PubMed record was found for
van Breugel or Victoriano, so neither carries a `pmid`. The DeepSeek URL is
pinned to Hugging Face commit `dba1be0a40aa45a94ad051997016db3960a90277`: HTTP
200 on 2026-09-15, same sha256 as the copy read, and the PDF link annotation
carries the underscores intact (`pdftohtml`, `pulsefaq` as control).

**Cautions recorded in the `internal_note` of each entry, not in the text.**
- DeepSeek: the attribution is the authors' own ("We find"), with no ablation.
  The same §5.1.2 reports gains from RL compute and model merging, and the
  Conclusion calls for "coordinated scaling of data, model capacity, and RL".
  "Curation" is not among the three named factors.
- van Breugel calls mechanistic generators "inherently robust", in the sense of
  stability against training randomness. It is not cited for reliability, and
  the atlas is not presented as contradicting it.
- Hwang: the animal arm (T2DM-induced rats, "an unexpected increase in TBR under
  GSL") is not cited.
- DeepSeek is a technical report, not peer reviewed. It is a numbered entry by
  the author's decision, one more instance of the web-reference departure N-4.

**Rendering.** PDF and DOCX both list the four entries as [2]–[5]. The DOCX
first printed "Breugel, B. van" and "Schaar, M. van der"; bracing the family
names fixed it in both outputs. **Pre-existing, not addressed:** the DOCX drops
`howpublished` for every `@misc` entry, including `pulsefaq`, `pulseinaction`
and `webb2022vent`. The DeepSeek entry therefore shows no URL in the Word twin;
the PDF shows it.

Only `paper.tex`, `paper.bib` and the citation manifest changed for these
references. The supplement and the monograph are untouched, by the author's
decision.

**Follow-up, same day (night) — the Word-twin defect is fixed, on the author's decision.**
`scripts/tex_to_docx.py` now hands pandoc a retyped copy of the bibliography
(`build/*.docxsrc.bib`, gitignored). It turns 10 `@misc` into `@online`
(`\url` moved to `url`) and 3 into `@inproceedings` (`howpublished` moved to a
braced `booktitle`). `paper.bib` and both PDFs are unchanged: the text extracted
from each PDF is byte-identical before and after. In `paper.docx` only the six
`@misc` entries changed, with numbering intact. The new check in
`scripts/check_docx_structure.py` failed on exactly the 17 cited
entry-document pairs (6 paper, 11 supplement) before the fix and passes after
it; its calibration rejects the URL-less entry. Word still omits the "Accessed"
note and the "Technical report" label, which `nature.csl` does not print for
these types.

---

## Addendum 2026-09-16 — the ARDS non-examination claim, verified true and re-attached

**The defect.** `paper.tex` §2.6 used to state that published Pulse validation
work and HowTo examples sample at most up to severity 0.9 and do not examine
impairment fractions inside 0.91--0.945. The 2026-09-02 compression (`d88a1ca`)
deleted it with the paragraph. `cover_letter.md` kept asserting it, as the third
of its novelty points, so for two weeks an editor-facing claim had no locus
anywhere in the submission. The supplement carried only "Pulse's own
documentation does not flag this zone", a weaker proposition.

**Verified 2026-09-16** in the local clone `Pulse_engine_adults_Gitlab/engine`
at `REL_4_3_2` (build-only release; docs identical to the pinned 4.3.1):

| artefact | ARDS severities it uses | max |
|---|---|---|
| `src/cpp/howto/HowTo-IsoShuntAnalysis.cpp:60` | `ARDSSeverityList = { 0.0, 0.3, 0.6, 0.9 }` | 0.9 |
| `src/cpp/howto/HowTo-CreateAPatient.cpp:76-77` | 0.9 both lungs | 0.9 |
| `src/cpp/howto/HowTo-COVID19Ventilated.cpp:70-71` | 0.6 both lungs | 0.6 |
| `src/cpp/howto/HowTo-VentilatorFeedbackLoop.cpp:111-112` | 0.6 both lungs | 0.6 |
| every shipped adult scenario carrying an ARDS action | 0.0, 0.02, 0.13, 0.2, 0.3, 0.35, 0.6, 0.8, 0.9 | 0.9 (`ARDSExacerbation.json`) |
| `docs/Methodology/RespiratoryMethodology.md:1746` | *"The ARDS condition was validated against a moderate severity scenario."* | -- |

Nothing lands inside 0.91--0.945. **The claim is true.**

**Action.** The wording this register's prose-sweep item 49 had already blessed
as the "safe form" was restored verbatim into `supplement.tex` §S5.3, appended
to the documentation sentence. Nothing was composed for the occasion.

**Not restored, and why.** The same deleted passage also said Pulse's
methodology "exemplifies the range with the round-tenths convention
{0.0, 0.3, 0.6, 0.9, 1.0}". The `1.0` is not sourced: the HowTo sweep list is
`{0.0, 0.3, 0.6, 0.9}`, the highest severity in any shipped scenario is 0.9, and
the methodology text gives the range as 0 to 1 without exemplifying it.
Restoring the sentence would have re-entered an unsourced element. Item 49 had
already flagged the same attribution as ambiguous, on a different axis.

**Guarded.** `CONT_TEXT_REQUIRED` in `scripts/audit_claims.py` now requires
`sample at most up to severity 0.9` in `supplement.tex` **and** in
`cover_letter.md`, one occurrence each. Pairing them is the point: what happened
was the two drifting apart. Calibration: deleting the clause from the supplement
gives 1 FAIL on that row alone; deleting it from the letter gives 1 FAIL on the
other row alone; both files were then restored to a byte-identical sha256.

**Second restoration, same pass.** The compression had also removed the gloss of
"Sobol" from §2.6, leaving the term of art undefined on its first appearance in
the paper -- "variance" then occurred zero times in `paper.tex`. The
pre-compression wording was put back, and `SOBOL_REQUIRED_PHRASES` now requires
it; removing it again gives 1 FAIL.

---

## Addendum 2026-09-16 — `deepseek2026v41flash` re-opened in primary source, and the sentence moderated

**Why.** The author asked to moderate the attribution and, separately, for a
last check that the reference says what we claim. Both were re-measured in this
session rather than read off the 2026-09-15 row.

The pinned Hugging Face PDF was re-downloaded (HTTP 200) and its sha256 is
`ba68e2e40408125ae6d2f63a9a241b61c73910691c74ec1a2a7023c851eac08d`, identical
to the hash the `.bib` note recorded, so this is the same file.

| locus | what the report says | verdict |
|---|---|---|
| `paper.tex:140` | §5.1, p. 25, verbatim: *"We find that, under a fixed and unremarkable optimization procedure, systematic improvements in the scale, diversity, and verifiability of synthesized data and environments account for essentially all of the observed gains."* | MATCH |
| `paper.tex:323` | §5.1.1: *"We formalize each task as a triplet (problem, environment, verification system)"*, stated for agent tasks, which is the restriction the sentence carries | MATCH |

The descriptor was re-checked too: pp. 1 and 5 call it *"a multimodal
Mixture-of-Experts (MoE) model"*, which is what "large multimodal model" rests on.

**Change made, author's decision.** "attributes essentially all of the gains"
becomes "attributes **most** of the gains". The source says "essentially all",
so "most" is strictly weaker than what the report claims for itself and cannot
overstate it. The literal edit first proposed -- delete "all of" -- was not
applied, because it leaves "attributes essentially the gains", which is
ungrammatical; the author chose "most" from four options put to them.

**Instrument note.** The first grep for the sentence returned zero hits:
`pdftotext` wraps it across three lines. The zero was readable as an artefact
only because a positive control ("synthesized", 5 hits) had been run on the same
extraction first.
