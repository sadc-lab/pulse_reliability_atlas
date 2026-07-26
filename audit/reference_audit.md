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

**No source document was modified.** Per the stop protocol, this is recorded
for joint evaluation before anything is touched.

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
