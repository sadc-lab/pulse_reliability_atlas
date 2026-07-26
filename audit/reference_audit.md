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

Discrepancy: 0.35 kg male (0.5 %) and 0.21 kg female (0.4 %) — physiologically
trivial, but the sentence "50th-percentile values for 18-year-olds" is
inaccurate as written.

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
