# P.J. round 2026-08-27 — synthesis pass (paper down to ~20 pages)

**Status: NOTHING APPLIED TO THE REPOSITORY.** The drafts in section 7 await the
author's go, section by section. HEAD while drafting: `613f2a6`, working tree
clean.

## 1. What P.J. asked

Email 2026-08-27 plus the tracked-changes docx `Adult Pulse model
2026-08-25_PJdocx.docx` (byte-identical copies in the repo root and in
`~/Downloads`, sha256 prefix `bb4ea0a9`).

> [Text of a private message removed from the public history; see HISTORY.md.]

Directives: introduction halved with the study objective **last**; a paragraph
introducing the Methods subsections; Methods halved with the detail pushed to
the supplement; Results reduced to facts without interpretation; figures kept
but legends simplified to one main point each; **the Discussion is good**.

Author's decisions (2026-08-27 / 2026-08-28):

- Target about **20 pages, ~5,300 words of body text**; 21 pages acceptable.
- Do P.J.'s pass first, **then** send the new version to the other three chiefs.
- **Keep our own title.** P.J.'s proposed title is rejected.
- Validate **section by section** before applying anything.
- Everything cut from the paper lands in the supplement where it reads
  naturally; no invention; pedagogical but academic.
- Everything stated in the abstract must also appear in the paper body.

## 2. Measured baseline (paper.tex, prose only, floats excluded)

Two independent instruments (the LaTeX source, and the docx to markdown round
trip) agree within 9 words on every section.

| section | words |
|---|---:|
| 1 Introduction | 1,417 |
| 2 Results (6 subsections) | 4,611 |
| 3 Discussion | 2,176 |
| 4.1-4.6 Methods | 3,279 |
| 4.7 Use of AI tools | 383 |
| **body total** | **11,866** |
| backmatter declarations, out of scope | 818 |
| 5 figure legends | 1,302 (195 / 332 / 309 / 261 / 205) |
| 4 tables, glossary about 470-507 | about 1,300 |

Paper PDF 38 pages, supplement 52 pages (`build/*.log`). Audits green at
baseline: 382/382 anchors, 94/94 crosswalk sync, every guard PASS.

**Budget adopted**

| section | now | target |
|---|---:|---:|
| 1 Introduction | 1,417 | ~750 |
| 2 Results | 4,611 | 1,900 |
| 3 Discussion | 2,176 | 1,500 |
| 4.1-4.6 Methods | 3,279 | 1,150 |
| 4.7 AI tools | 383 | 383 |
| **total** | **11,866** | **about 5,700, i.e. ~21 pages** |

## 3. P.J.'s tracked changes: exact inventory

**14 passages touched** (corrected 2026-09-01 from "13": the enumeration in the
next paragraph already listed 14 items, and an independent re-derivation from
`word/document.xml` counts 14 paragraphs carrying a `w:ins` or `w:del`), 59
insertion runs and 59 deletion runs at character level, every authored attribute
naming P.J. **Zero edits in Methods, zero in any figure or table caption,
zero inside a table.** His base document is content-identical to our HEAD build
`preprint_npj/build/paper.docx`, verified by an independent pandoc round trip
(141 residual token differences, all anchor and caption-placement artefacts) and
re-confirmed 2026-09-01 by a direct `word/document.xml` comparison: 301
paragraphs on both sides, 17,610 words in our build against 17,460 in his copy,
the -150 being his net deletions.

Locations: title, abstract, Introduction paragraphs 1/2/3/5/6, section 2.3
heading plus paragraphs 1 and 4, section 2.4 paragraphs 2 and 3, section 2.5
paragraph 2, Discussion clause (iv).

### 3.1 His three comments

| id | anchor | comment | our answer |
|---|---|---|---|
| 68 | abstract, blood-volume sentence | asks whether his rewrite of the sentence is correct | **No, it is not correct.** See 3.2 item 3. |
| 70 | abstract, last sentence | finds the last sentence unclear | rewrite in plainer terms |
| 100 | section 2.1, `implausible` definition | asks where the acceptable maximum and minimum values are reported | The six bounds are in Methods 4.4 (HR [20,220] bpm, MAP [30,180] mmHg, Vt [50,1500] mL, SpO2 [50,100] %, PaO2 [20,600] mmHg, PaCO2 [10,120] mmHg) and Supplement S3.1. A pointer exists only in the Table 2 caption, none at the sentence he annotated. Add one. |

### 3.2 Edits to refuse or repair (each verified verbatim in the accepted text)

1. Abstract: "of its **operational inputs**" is replaced by a vaguer wording.
   Not demonstrably false, but vague where the original was precise: section 1
   itself documents the 2020 `STUDY_SENSITIVITY_ANALYSIS_1_0_0` tag, so the
   unqualified phrasing reopens the over-claim section 1 corrects. Two further
   defects in the same sentence: one changed verb is not idiomatic, and
   renaming the "reliability **atlas**"
   desynchronises the abstract from the title, from
   section 2.1 and from the Discussion, which all call the deliverable an atlas.
2. Abstract: "two bodies" is queried with a gendered wording. Pulse carries a *sex*
   flag, not a gender.
3. Abstract, the blood-volume and hyperoxia sentence. His version **deletes**
   "Solver divergence fell entirely on the male body (20/1,280)", so headline
   finding 3 disappears from the abstract, and replaces it with a sentence that
   gives the 643 mmHg median for the female body alone and, for the male body,
   ties the same result to the lowest blood-volume baseline,
   4,082 mL. **Factually wrong twice**, and
   verified on the data rather than inferred:
   `data/runs/s021_hyperoxia_convergence/` holds 22 `S1_F` plus 22 `S1_M`, i.e.
   44 S1 reruns, so 643 mmHg is the median of a **mixed-sex** healthy cohort and
   not of the female body alone. And `4{,}082` appears in the paper only in the
   abstract, in section 2.5 and in the Figure 5 caption, always about **solver
   divergence**, never about PaO2.
4. Abstract: an inserted word breaks "three inputs dominate".
5. Section 1: "which **lie** largely outside" is put in the past tense.
6. Section 2.4: "makes ... underestimate" is put in an ungrammatical past tense;
   "plateau**s**" is made singular, although six reruns make the plural right.
7. Section 2.5: "mL kg^-1" gains a full stop between the units, which is not SI.
8. Discussion clause (iv): his deletion leaves the sentence broken, with a stray
   full stop before the colon and emptied math markup,
   and drops both explanations.
9. Title: his proposed title presents Pulse as a **cardiovascular** simulator.
   **Rejected by the author.** It would also misdescribe
   Pulse (Methods 4.1: a whole-body engine solving cardiovascular, respiratory,
   gas-exchange, endocrine, renal and drug sub-models) and misdescribe this
   paper, whose two operator-actionable findings are respiratory.
10. His empty PaO2 placeholder in the abstract: there is **no audited anchor**
    for a cohort-level "PaO2 under the 120-second window". Either leave it out,
    which is the recommendation since the abstract sits at its 150-word cap, or
    derive and audit a new anchor.

### 3.3 Edits to accept

The six colon-to-full-stop splits, which are exactly his density complaint; the
(1)-(4) numbering of Pulse's applications; "Yet despite this footprint" becoming
"Yet" with the redundant parenthetical dropped; and "lever" becoming "trigger
level" in the section 2.3 heading.

**Added 2026-09-01.** He makes the same `lever` to `level` repair **twice**, not
once: the section 2.3 heading (docx paragraph 177, `lever` to `trigger level`)
and **Introduction paragraph 5** (docx paragraph 25, a single-character `r` to
`l`). Only the first was recorded. Both are correct and both are accepted.

**Correction of 3.2 item 6, same date.** That item attributed
the past-tense change to "makes ... underestimate" to section 2.4. It
is in the **abstract** (docx paragraph 8). Section 2.4 carries only the
`plateaus` to `plateau` deletion (docx paragraph 185), and that one is
**refused**: the sentence reads "six of the 44 S1 reruns relaxed to PaO$_2$
plateaus above 700~mmHg", where six runs make the plural correct.

## 4. Redundancies measured

- The four flags are defined **three times**: section 2.1 paragraph 1 prose,
  Table 2, and Methods 4.4.
- "663 / 51.8 %" is stated **twice inside section 2.1 alone** (paper.tex L221
  and L254), plus the Table 4 caption and the Table 4 body.
- The cell-label key is repeated in **6 floats** (5 "Cell-label key", 1
  "Scenario key").
- The glossary, Table 1, about 470-507 words, re-defines terms that Methods 4.3
  and 4.6 and three captions already define.
- Interpretation inside Results, which is his explicit point: section 2.3
  paragraphs 3-4, section 2.4 paragraph 3, section 2.5 last paragraph, and most
  of section 2.6.

## 5. Section 1: drafted, awaiting go

Introduction **1,417 to 772 words, minus 45.5 %**, objective last. The
supplement gains 188 plus 122 words. Net paper change: minus 645.

### 5.1 Verification battery, all green

- Crosswalk literals introduced: exactly **one**, `1{,}280` once, so
  `T1.01 expected_occurrences` goes **46 to 47**. Current count remeasured:
  paper 25 plus supplement 21 equals 46. This is the only crosswalk edit needed.
- Guard literals, 1,236 quoted strings of 15 characters or more harvested from
  `audit_claims.py`, matched by the new text: **zero**. Positive control on the
  same instrument: 7 hits in the abstract, 5 in the Discussion.
- `DETECTOR_BANNED` vocabulary: zero occurrences. The draft says "four-flag
  steady-state **classifier**", never "detector".
- LaTeX: braces balanced, dollar count even, quote pairs matched.
- All six `\ref` targets exist. `\ref{sec:s1}` resolves through
  `\externaldocument{supplement}` (xr package, paper.tex L33), a mechanism
  already used at paper.tex L404.
- All 14 cite keys exist in `paper.bib`.

### 5.2 Citation policy (author's question, 2026-08-28)

**No citation is dropped.** A citation travels with the sentence it supports.
Three cases: the sentence moves to the supplement and the citation moves with
it; the sentence is deleted as a strict duplicate and the citation survives at
the retained occurrence; or the claim genuinely leaves the paper and the
citation legitimately leaves too.

Mechanical invariant checked after every section: the union of bib keys over
`paper.tex` and `supplement.tex` must stay at **45**. For section 1: **45 to 45,
zero keys lost.** `pulsecircuit`, `pulsesystem` and `pulsepatientmethod` migrate
from the paper to the supplement; `pulserespmethod` stays in the paper via
Methods 4.1.

Consequence to communicate: the paper's own list goes from **40 to 37 keys**, so
**every reference number renumbers**. The three other chiefs annotate against
the current numbering.

### 5.3 Content-loss audit (calibrated instrument)

A first vocabulary-diff instrument was **discarded as uncalibrated**: it flagged
`medical`, `training`, `pulsepatientmethod`, `five nodes`, `body size` and
`generic circuit solver` as lost when all six are present. Pure false positives.

Replacement instrument: the 400 content words of length 7 or more in the old
Introduction, each grepped against the union of {new drafts, paper minus the old
Introduction, supplement}, with `ZZZNOTAWORDZZZ` appended as a negative control.
The control was correctly reported missing.

Result: **16 real words missing out of 400**, each triaged:

- `answers`, `crucially`, `footprint`, `important`, `unaddressed`: discourse
  markers and structural sentences, no fact behind them.
- `assessments`, `falsifying`, `intervention--outcome`: the paragraph-1 forward
  mention of Cornish, fully described in paragraph 2.
- `categorises`: false positive of inflection, "categorised" is present.
- `worthwhile`: the low-fidelity follow-up. Supplement S1 paragraph 3 already
  carries the same point ("This self-description frames the present atlas's
  contribution...").
- `protective-ventilation`: Methods 4.3 says "a reference ventilation setting
  based on the ARDSnet low-tidal-volume framework", and S5.1 has the full table.
- `prioritise`: the downstream-users sentence. The Discussion carries both the
  green / yellow / red triage (verified present) and "without re-running the
  present sweep" (verified present).
- `arbitrary`: **the one tracked deferred item**, see 5.5.
- `virtual-patient`, `emergency-medicine`, `platforms`: **the only genuine
  residual loss**, namely the detail of Pulse's application (3). Present in the
  monograph, 2 and 1 occurrences, but it would leave the paper and supplement
  pair. Author's call: accept the loss, or restore six words.

Three further losses were found earlier in the same audit and are **already
repaired in the draft**: Webb's swept dimensions ("respiratory compliance,
diffusion impairment and positive end-expiratory pressure", sole occurrence in
the whole repository), the circuit "paths carrying idealised elements
(resistances, capacitances, diodes)" (sole occurrence), and **the definition of
the term "sweep"** (sole occurrence, while the word is used 39 times in
paper.tex).

### 5.4 Cross-references checked, none broken

`supplement.tex:118` is the only place pointing back to `\ref{sec:intro}` ("This
self-description frames the present atlas's contribution (Section 1)"). The new
paragraph 4 still states that contribution, so the pointer holds.

All five supplement and Methods labels the old Introduction referenced are still
referenced elsewhere in paper.tex: `sec:s5-berlin` twice, `sec:methods-sweep`
four times, `sec:s4` once, `sec:s12` twice, `sec:methods-detector` twice. No
section is orphaned.

### 5.5 Deferred, tracked

"An atlas cell is therefore anchored to a clinically recognisable state rather
than to an arbitrary engine setting." To be placed in **Methods 4.3** during the
Methods pass. Not lost, not yet placed.

### 5.6 Residual risk, to be measured after the build

`scripts/check_render.py` holds three accepted typographic residues matched on
the **exact** magnitude: `paper: overfull box, 11.89064pt too wide`,
`supplement: overfull box, 19.30798pt too wide`, `supplement: float too large
for page by 31.26459pt`. Shortening section 1 by about 645 words reflows the
paper. These are intrinsic box and float dimensions rather than positions, so
they are expected to hold, but that **must be measured after the rebuild, never
assumed**.

## 6. Side finding, verified against the primary source

`supplement.tex:118` quotes "low-**fidelity** clinical approach" with a hyphen
that is **absent from the source**, and **without a citation**. Re-opened this
session in the local clone
`C:\Users\santi\projets\Pulse_engine_adults_Gitlab\engine`:
`docs/Methodology/SystemMethodology.md` L261 reads "The engine uses **a low
fidelity clinical approach** and is not necessarily for high fidelity predictive
purposes."; L117 reads "of 0.02 s (50 Hz). All system states are recalculated
every time step." The replacement sentence is in 7.4 below.

## 7. The drafts

Four units. This register is the durable copy; the session scratchpad copies do
not survive a new session.

### 7.1 Replacement for paper.tex lines 138-157 (the whole Introduction)

```latex
\section{Introduction}\label{sec:intro}

Longitudinal health data of the kind needed to represent a patient's evolving state are often scarce and incomplete~\cite{katsoulakis2024digitaltwins}, and digital twins for health (virtual, often mechanistic models of human physiology used for in-silico trials, medical-device design, and synthetic-patient generation) are proliferating across healthcare~\cite{katsoulakis2024digitaltwins}. Mechanistic simulators supply physiological time series from explicitly specified inputs, with model-internal states accessible by construction; mechanistic origin does not, however, make their outputs automatically reliable. The Pulse Physiology Engine (Kitware, Apache-2.0) is one such actively maintained open-source whole-body simulator~\cite{bray2019}. It models each physiological system as a small network of coupled compartments rather than full three-dimensional anatomy (a lumped-parameter approach), delivering real-time cardiovascular, respiratory, gas-exchange, and pharmacological simulation (Supplement~\S\,\ref{sec:s1}). Pulse has been applied to (1)~ventilator-safety what-if analysis~\cite{webb2020}, (2)~validation of its own mechanical-ventilator model against a physical reference simulator~\cite{webb2022vent}, (3)~medical education and simulation training~\cite{pulseinaction}, and (4)~general-purpose computational physiology~\cite{bray2019}; its respiratory dynamics have also been used independently as a source of simulated data for learning and benchmarking ventilator-control policies in Acute Respiratory Distress Syndrome (ARDS)~\cite{ward2024ventilator}.

Yet no public map of how the engine responds across its user-facing \emph{input} envelope has been published: most of that work probes Pulse's \emph{outputs}, validating them against reference data. Webb et al.'s ventilator-sharing study~\cite{webb2020} does sweep inputs (12{,}642 unique patient and ventilator combinations spanning respiratory compliance, diffusion impairment and positive end-expiratory pressure) and rank parameters by outcome correlation, but over the \emph{mismatch} between two equal-sized 70~kg bodies sharing one ventilator, scored against a single composite safety outcome under pressure-mode ventilation with respiratory rate, I:E ratio and respiratory resistance held fixed; it resolves neither each input's influence on each physiological output, nor input clamping, nor solver divergence. The maintainers state on the project's public FAQ that ``we have not performed a systematic forward propagation or inverse quantification of model uncertainty, nor have we conducted a formal sensitivity analysis''~\cite{pulsefaq}. The upstream repository does carry a single 2020 sensitivity study in its source tree, tagged \texttt{STUDY\_SENSITIVITY\_ANALYSIS\_1\_0\_0}, but it targets internal lumped-parameter circuit values --- cardiovascular and respiratory resistances and compliances, which cannot be measured clinically --- for model calibration: a different parameter class from the user-facing operational inputs downstream applications actually specify. A prior external assessment of Pulse on a clinical dataset, by Cornish et al.~\cite{cornish2023}, applied a causal-falsification framework to MIMIC-III sepsis trajectories and reported intervention-response errors concentrated on electrolyte, metabolic, acid--base and dermal outputs, largely outside the present atlas's six-output cardio-respiratory panel. Each downstream user therefore re-encounters the same engine limitations independently, and each validation pipeline re-derives its own working envelope by trial and error.

We centre this work on the ARDS severity axis for two reasons. First, ventilating an impaired lung is a main use of Pulse's respiratory model, and a regime whose downstream reliability remains incompletely characterised. Second, mapping the adult engine's sensitivity and failure modes is the prerequisite for adapting it to pediatric ARDS, the setting in which we ultimately want simulated cohorts to support machine-learning prediction of ventilation-dependent blood gases in critically ill children; an adaptation cannot be assessed against an adult substrate whose own sensitivity and failure modes are unmapped.

The objective of this study was therefore to build the first open reliability atlas across Pulse's adult critical-care operational envelope, organised around three questions: \emph{how} strongly each input drives each output and where that influence turns non-linear; \emph{whether} the engine runs a submitted setting as given; and \emph{whether} the solver diverges or never reaches steady state. Seven user-facing operational inputs --- heart rate (HR), systolic and diastolic blood pressure (SBP, DBP), respiratory rate (RR), tidal volume (Vt), inspired oxygen fraction (FiO$_2$) and positive end-expiratory pressure (PEEP) --- were varied across their accepted ranges with a Morris elementary-effects design~\cite{morris1991,campolongo2007}, a one-at-a-time screening method; the resulting batch of runs is what we call the \emph{sweep}. Six steady-state outputs were tracked: HR, mean arterial pressure (MAP), delivered tidal volume, peripheral oxygen saturation (SpO$_2$), arterial oxygen partial pressure (PaO$_2$) and arterial carbon dioxide partial pressure (PaCO$_2$). Four clinical scenarios (a healthy baseline and three ARDS severities) crossed with two adult reference patient bodies, male and female, gave 1{,}280 simulations. Every run was then labelled by a four-flag steady-state classifier recording a refused setup input, a diverged solver, a steady-state output outside hard physiological bounds, or a run that never settled within the simulation window; failures are categorised rather than discarded, so the atlas stays complete. The deliverable is not a benchmark score but a per-cell curation and review-priority map with a reusable run-level classifier. Neither layer constitutes external physiological validation, and neither is a distribution-neutral automatic filter. The pipeline is preregistered, reproducible from a single Docker image with a fixed seed, and released open-source under Apache-2.0.
```

### 7.2 New paragraph in supplement.tex section S1, inserted after L114 (188 words)

```latex
Four further implementation choices bear directly on how this atlas is read. First, those circuits are built from paths carrying idealised elements (resistances, capacitances, diodes), and the resulting non-linear networks are solved by one generic circuit solver shared across all systems~\cite{pulsecircuit}. Second, the engine advances on a fixed transient-analysis time step of 0.02~s (50~Hz), recalculating every system state at each step~\cite{pulsesystem}; the 0.02~s here and the 20~ms above are the same quantity from two independent sources, not two separate facts. Third, execution is deterministic, so one configuration replays to one trajectory --- which is what allows a per-cell curation map to be reproduced rather than merely reported (\S\ref{sec:s12}). Fourth, patients and diseases enter at setup rather than continuously: body dimensions drive allometric baselines (quantities that scale with body size) bounded by hard acceptance limits~\cite{pulsepatientmethod}, and a single ARDS severity scalar on $[0,\,1]$ drives the respiratory modifiers through piecewise-linear functions calibrated at five nodes --- 0.0, 0.3, 0.6, 0.9 and 1.0~\cite{pulserespmethod}. That five-node calibration is why the main design fixes severity at scenario points rather than sweeping it (\S\ref{sec:s5-mapping}); the continuous-severity micro-sweep of \S\ref{sec:s5-cont} is a separate, targeted experiment.
```

### 7.3 New opening paragraph in supplement.tex section S16, inserted after L993 (122 words)

```latex
Each run in the atlas is reduced to one value per output: the mean over the final 60~s of the 120~s simulation. That reduction is only meaningful in a window where the output has settled --- neither drifting, nor still oscillating, nor frozen against a physiological bound. A mean taken while an output is still moving records \emph{when} the run was sampled rather than \emph{how} the input acted, and a mean taken from an output frozen against a bound may reflect numerical pinning rather than physiology; where the bound is itself physiologically attainable, the classifier cannot distinguish the two (\S\ref{sec:s4}). Runs failing any of these tests are therefore flagged rather than discarded (Section~\mainref{sec:methods-detector}{4.4} of the main manuscript), which keeps the assumption auditable.
```

A final sentence was drafted and then **cut**: it duplicated the existing
sentence "A natural concern is whether these localised instabilities contaminate
the other steady-state channels the Morris screen relies on", which opens the
paragraph immediately below.

### 7.4 Replacement for supplement.tex L118 (quote form and missing citation)

```latex
The Pulse documentation explicitly characterises the engine as using ``a low fidelity clinical approach'' and states it is ``not necessarily for high fidelity predictive purposes''~\cite{pulsesystem}, intended for training simulation rather than patient-specific clinical prediction.
```

### 7.5 Crosswalk edit that must ship in the same commit

`preprint_npj/paper_to_monograph_map.md`, entry `T1.01`:
`expected_occurrences: 46` becomes `47`, with a note recording that the
Introduction rewrite of 2026-08-28 introduces one occurrence of the canonical
`1{,}280` literal in the objective paragraph.

## 8. Order of work after section 1

2. Methods 4.1-4.6, 3,279 to about 1,150 words, with the introductory paragraph
   P.J. asked for, and the deferred sentence of 5.5 placed in 4.3.
3. Results, 4,611 to about 1,900 words: facts only, interpretation moved to the
   Discussion or the supplement. Table 1 (glossary) moves to the supplement.
   The three-times-defined four flags collapse to one definition.
4. Discussion, 2,176 to about 1,500 words: remove restatement only, not argument.
5. Abstract: repair P.J.'s three factual defects, answer comment 70, keep the
   150-word cap.
6. Figure legends, 1,302 to about 400 words, one main point each. The
   `Figure-legend length guard` caps at 350 words, so shortening cannot trip it.
7. Rebuild PDF and DOCX for both documents, then run `audit_claims.py
   --check-paper-sync` and `check_render.py`, and report the residues.

---

# Addendum, 2026-09-01

Everything below was established in a single session, with the repository at
`613f2a6` and the working tree clean. **Still nothing applied to `paper.tex`,
`supplement.tex` or the monograph.**

## 9. P.J.'s email of 2026-08-27, verbatim

The primary source was missing from this register: section 1 quoted only the
length complaint, and the directive list was an English rendering. The email in
full, as supplied by the author:

> [Text of a private message removed from the public history; see HISTORY.md.]

Three things this register had not recorded, all consequential.

1. **Two deliverables, not one.** [text of a private message removed from the public history; see HISTORY.md]
   His tracked changes target the **arXiv** deposit; the synthesis
   to 20 pages targets the **journal** version. The word `arXiv` appeared zero
   times in this register before today. Author's decision, 2026-09-01: **one
   clean version serving both**, because the arXiv track is blocked upstream
   anyway (the GitHub repository is still private -- its API endpoint returns
   404 against a control repository returning 200, checked 2026-09-01).
2. **He lifts the supplement constraint explicitly**: [text of a private message removed from the public history; see HISTORY.md]
   His remark on the supplement was a description of his reading
   experience, not a limit. An earlier objection raised during this pass -- that
   moving material into the supplement would worsen his own complaint -- is
   therefore **withdrawn**.
3. **He asks an open question about section order**, he does not instruct:
   [text of a private message removed from the public history; see HISTORY.md] Answerable from npj's own Article table, see
   section 11.

Note also: **the title is not mentioned in the email**. His alternative title
exists only inside the docx, i.e. in the arXiv-suggestion bucket.

## 10. The 14 tracked-change paragraphs

Re-derived 2026-09-01 directly from `word/document.xml` with a positive control
(paragraph 0 must show exactly one deletion and one insertion; it does). `P<n>`
is the zero-based paragraph index in the docx body.

| P | locus | deleted | inserted |
|---|---|---|---|
| 0 | title | `An Open Reliability Atlas of Sensitivity and Failure Modes in the Pulse Physiology Engine` | his proposed title (3.2 item 9) |
| 8 | abstract | 25 runs incl. `operational inputs`, `atlas`, `published`, `bodies`, `reflects`, `locking`, `makes`, `reproducible`, `Solver divergence fell entirely on the male body (20/1,280);`, `its`, `floor eliminated it` | 33 runs: the changes of 3.2 items 1-4 and 6, and the two notes of 10.1 |
| 18 | intro 1 | -- | the (1)-(4) numbering (accepted, 3.3) |
| 19 | intro 2 | `despite this footprint`, `(which inputs dominate which outputs, where inputs are silently clamped, and where the solver diverges)`, `that`, `work`, `does` x2 | 3 runs: one wording and two tense changes |
| 20 | intro 3 | `:` | 3 runs: a sentence split and two tense changes |
| 25 | intro 5 | `r` | `l` (`lever` to `level`) |
| 26 | intro 6 | `:`, `a` | `.`, `A` |
| 177 | 2.3 heading | `lever` | `trigger level` |
| 178 | 2.3 para 1 | `:`, `i` | `.`, `I` |
| 181 | 2.3 para 4 | `:`, `p` | `.`, `P` |
| 184 | 2.4 para 2 | `:`, `a` | `.`, `A` |
| 185 | 2.4 para 3 | `s` (`plateaus` to `plateau`) | -- |
| 190 | 2.5 para 2 | -- | `.` (between the units of `mL kg^-1`) |
| 211 | Discussion (iv) | `: t`, `(driven not_steady_state or implausible by SpO`, `-saturation pinning and, at FiO`, `, transient hyperoxia, S2.4),`, `(driven implausible or not_steady_state by severe hypoxemia)` | `.: t` |

### 10.1 Five open questions from him, not three

Section 3.1 recorded the three formal Word comments. Two further open questions
sit inside the abstract insertions themselves and were not recorded:

- an inserted phrase that ends with an unresolved French
  editorial note; he is asking us to choose between two wordings.
- an empty PaO2 placeholder he left in the abstract. See section 13.

Two of his insertions also carry question marks (3.2 items 2 and 3),
so they are queries, not assertions.

## 11. npj rules, re-read at source on 2026-08-30

`www.nature.com` 303-redirects a plain fetch through `idp.nature.com`, exactly
as `audit/npj_format_compliance.md` records; retrieved with the Firecrawl CLI.
Both pages authenticated by a negative control (no 404 body, no login wall) and
a positive one (8 occurrences of the journal name).

**The Methods rule, stated twice, verbatim:**

> "All descriptions of Methods should be provided in the main manuscript file
> and not in the Supplementary Information" -- *Content types*, Article table,
> Methods row.

> "The journal does not permit Supplementary Methods, all Methods should be
> reported in the main manuscript file." -- *Submission guidelines*,
> *Supplementary information*.

**This collides with P.J.'s directive** to move the more detailed
explanations to the supplement. The collision is bounded, on four
counts:

1. It binds the journal version only; arXiv has no such rule.
2. Halving the Methods is not in conflict -- npj itself asks that "The Methods
   section should be written as concisely as possible".
3. It bites only on *method description*. Provenance tables, rationale registers
   and robustness analyses may sit in Supplementary Information; that is what
   Supplement S3 already is, since the N-1 restructure of 2026-08-02.
4. npj sets the floor in the same sentence: Methods "should contain all elements
   necessary to allow interpretation and replication of the results".

**Consequence for the budget.** Section 2 of this register targets Methods at
~1,150 words, i.e. -65% from the measured 3,264. That is very unlikely to be
reachable by density alone without deleting method description. **Revised
target: ~1,500 words**, on the authority of the npj floor above.

**The rest of the Article table, all verbatim:** title up to 15 words; abstract
"No subheadings permitted and up to 150 words in length"; Introduction "No
subheadings permitted"; Results "Subheadings should be used"; Discussion "No
subheadings, limitations, or conclusions sections are permitted"; Methods
"Subheadings should be used"; References "Limited to 60 references, though not
strictly enforced"; Figure legends "Limited to 350 words per figure".

**No word or page limit exists for the Article main text.** The 1,000-1,500 word
limit visible on that page belongs to the *Brief Communication* table. P.J.'s
20 pages are his editorial standard, not a journal requirement.

Also relevant: "Manuscripts submitted to *npj Digital Medicine* do not need to
adhere to our formatting requirements at the point of initial submission", but
"Manuscripts published in the npj Series journals are not subject to in-depth
copy editing" -- what we submit is close to what is published.

**Section order** is Title, Abstract, Introduction, Results, Discussion,
Methods, then the declarations. That is our current order, and it answers
P.J.'s question directly.

**One item to re-check during the Discussion pass.** The Discussion rule forbids
a "limitations" section. Our Discussion carries "Six scope limits bound the
conclusions. (i)...(vi)". `audit/npj_format_compliance.md` entry C-5 judged this
compliant on the grounds that the Discussion contains zero heading macros -- but
it made that judgement when the Discussion was **1,602 words**; it is **2,171**
today. The judgement is stale, not necessarily wrong.

## 12. Scientific debts found during this pass

### 12.1 "makes Vt reproducible" is an over-claim -- correction mandatory

**Where:** `paper.tex:128` (abstract) and `paper.tex:317` (section 2.3). Two
occurrences, **guarded by nothing** -- zero hits in `scripts/audit_claims.py`,
zero in `preprint_npj/paper_to_monograph_map.md`.

**Why it is too strong.** The intervention "brings 78.1 % of reruns below the
threshold" (`paper.tex:315`, `:332`, `supplement.tex:646`; ledger
`T1.06c.s14_frac_below`). 78.1 % of 64 is 50 runs, the only integer that rounds
to 78.1, so **14 of the 64 reruns remain at or above the 0.05 threshold**. That
count of 14 is arithmetic from published values, not itself a published figure.
Section 2.3 says as much in its own words: the lock is "an exploration lever,
not a clinical recommendation", it "carries a cost", and Pulse's default is
"physiologically the more faithful regime".

**A second, independent problem: the word does not have one meaning here.**
Inventory of `deterministic` in `paper.tex`:

| line | section | sense |
|---|---|---|
| 146 | Introduction | engine determinism: "Execution is deterministic, so one configuration replays to one trajectory" |
| 289 | 2.2 | input-output coupling: "Output Vt tracks input Vt near-deterministically" |
| 317, 319 | 2.3 | Vt delivery under the trigger lock |
| 332 | Figure 4 caption | same |
| 386 | Discussion | ordinary English, unrelated to the engine |

and section 4.1 adds a fifth sense with "Re-running the pipeline reproduces the
canonical outputs bit-for-bit", which is pipeline reproduction. Under the only
sense that is measurable at this locus -- breath-to-breath stability -- the
claim holds for 78.1 % of runs, not all.

**Decision (author, 2026-09-01):** record the debt now; repair the section 2.3
occurrence during the **Results** pass and the abstract occurrence during the
**abstract** pass, where the 150-word cap has to be managed.

**Wording to use, not yet frozen.** Abandon the `reproducible` / `deterministic`
vocabulary at this locus and describe the measured effect. Results: "reduced the
median breath-to-breath Vt CV from 0.351 to 0.016". Abstract: "markedly reduced
breath-to-breath Vt variability" if the numbers cost too many words.
**Mechanical cost if the numbers do go into the abstract:** `0.351` is a ledger
literal with `expected_occurrences: 5` and `0.016` with `expected_occurrences:
4`; both would need bumping to 6 and 5 in the same commit.

### 12.2 "plateau" and "converged" across Supplement S9.3 and Table S14

**What is certain, read from `data/runs/s021_hyperoxia_convergence/summary.json`:**

| statistic | population | value |
|---|---|---|
| `S1_plateau_median_mmHg` | all **44** S1 reruns | **643.3063280389815**, IQR [592.2080, 668.2195] |
| `S1_converged_plateau_median_mmHg` | the **41** drift-converged | **642.8715636969404**, published as 643 |
| figure trajectory endpoint | the **38** physiological-converged | **639** |

The 44 partition as 38 physiological-converged + 3 runaway-converged + 3
runaway-non-converged, exactly as the supplement itself states and as the
`S021 converged-plateau claim` guard checks. **The numbers in Table S14 are
therefore correct**, and its printed IQR `[592, 668]` matches the stored values.

**What is wrong is the vocabulary, and it is wider than the table.**

- Table S14 title: "**Converged** PaO2 plateau by ARDS scenario" -- announced
  over n = 44, a set that provably contains 3 runs the same section calls
  non-converged.
- Its two column headers: "Plateau median (mmHg)", "Plateau IQR (mmHg)".
- An orphaned caption sentence, "Convergence is judged by the preregistered
  drift criterion", when no column of the table reports convergence. This is
  what makes the title look justified.
- **Subsection S9.3 itself**, `sec:s9-shunt`, is titled "**Oxygenation plateau**
  across ARDS severity, and the clean-regime FiO2 dose response", and its prose
  reads "The **plateau** (per-run mean over the final 60 s of the 300 s rerun,
  t = 240-300 s) falls monotonically with severity" -- again over the full
  44-run set.
- The same section also writes "six of the 44 S1 reruns relaxed to PaO2
  **plateaus** above 700 mmHg" and "six reruns (14 %) developed unphysical PaO2
  **plateaus**", where three of those six are the non-converged runs.

**Rule proposed by the author, 2026-09-01, and adopted:** reserve *plateau* for
runs in which convergence is actually established, and say **"final-60-s PaO2"**
or **"final-60-s mean PaO2"** wherever the quantity is aggregated over the full
44. Candidate title for Table S14: "Final-60-s PaO2 by ARDS scenario in the S021
300-second reruns".

**Mechanically safe:** `plateau` appears in **no** `format_in_paper` field of
the crosswalk (positive control on the same query: `643~mmHg` is found).
Renaming breaks no guard. **The values must not change.**

**Not applied. The whole of S9.3 is to be audited during the supplement pass.**

### 12.3 Knock-on effect of the section 1 rewrite, newly noticed

The draft of section 7.2 moves the engine-determinism sentence out of the
Introduction (`paper.tex:146`) and into Supplement S1. After that move, a reader
of the paper alone meets "deterministic Vt delivery" in section 2.3 with **no
prior sentence in the paper body defining engine determinism**. Not blocking; to
be resolved together with 12.1 during the Results pass.

## 13. The 120-second PaO2 estimand -- registered BEFORE computation

Answering P.J.'s empty PaO2 placeholder in the abstract, which asks
for the PaO2 observed under the locked 120-second window, to contrast with the
643 mmHg reached at 300 s.

**Status of the quantity today: it does not exist.** No audited anchor carries a
cohort-level PaO2 for the 120-second window (checked across all 24 PaO mentions
in the crosswalk). Supplement S9 gives ~552 mmHg at t = 0 of the recorded window
and ~639 mmHg at t = 300 s, but nothing at t = 120.

**Estimand, fixed before any computation is run.**

1. **Population:** the same **41** S1 reruns that are drift-converged at 300 s,
   i.e. `abs(drift) < 15.0` mmHg per 60 s, with drift the OLS slope times 60
   over t = 240-300 s. The identity of the 41 must be verified to be the same
   set on both sides.
2. **Per-run 120-second statistic:** mean of `PaO2_mmHg` over
   `60 <= time_s <= 120`, inclusive at both ends. This is the exact analogue of
   the stored 300-second statistic (`plateau_stats` in
   `scripts/run_s021_hyperoxia_convergence.py`, window `240 <= time_s <= 300`,
   `pao2.mean()`), and it also matches the atlas's own convention in
   `src/detector.py` (`STEADY_STATE_T_LO = 60.0`, `STEADY_STATE_T_HI = 120.0`,
   inclusive with a 1e-6 tolerance). The two conventions coincide, so the
   quantity computed here is also the value the atlas actually recorded.
3. **Cohort aggregation:** pandas `.median()`, and `.quantile(0.25)` /
   `.quantile(0.75)` with the default linear interpolation -- identical to the
   calls that produced `summary.json`.
4. **Kill gate, mandatory.** Recompute the 300-second statistic through the same
   code path. If it does not reproduce **642.8715636969404**, the pipeline is
   wrong, the 120-second number is discarded and nothing is reported.
5. **Two independent routes**, which must agree: (A) recomputed from
   `s021_hyperoxia_convergence/trajectories.parquet`; (B) read from the original
   sweep, `data/runs/full_sweep/aggregated.parquet`, for the same
   configurations. Agreement between A and B is also the empirical test of the
   supplement's claim that the reruns are byte-identical to the 120-second runs
   over the shared recorded interval -- a stronger test than comparing files.

**Interpretive constraint, binding on any future wording.** The 41 runs are
converged *as judged at 300 s*. Their 60-120 s window is by construction **not**
converged -- that is the finding being reported. The quantity defined above is
therefore *the atlas's steady-state estimator applied to a window in which PaO2
is still rising*. It is **not** "the PaO2 at 120 s" and it is **not** a plateau.
Any sentence that ever carries this number must say so, or it states a
steady-state value for a state that is not steady.

**Decision rule for the abstract, set in advance.** If the median falls below
600 mmHg, the median run would not have tripped the `implausible` bound and
P.J.'s sentence no longer says what he intends. If it lands near 620, the gap
to 643 is about 3.6 %, probably too small to spend words on in an abstract
already at exactly 150 of 150. **The decision follows the number; the number
does not follow the decision.**

**No text is to be modified on the strength of this computation without the
author's explicit go.**

## 14. Result of the section 13 computation, 2026-09-01

Run read-only on `data/runs/s021_hyperoxia_convergence/trajectories.parquet` and
`data/runs/full_sweep/aggregated.parquet`. **No manuscript file touched.**

### 14.1 Kill gate: PASSED

| control | recomputed | stored | verdict |
|---|---|---|---|
| 41 drift-converged S1, mean over t = 240-300 s, median | `642.8715636969404` | `642.8715636969404` | exact |
| all 44 S1, same statistic | `643.3063280389815` | `643.3063280389815` | exact |

The transcription of `plateau_stats()` is faithful to the last binary digit, so
the pipeline used below is the same one that produced the published 643 mmHg.

### 14.2 A defect the kill gate exposed: the executed window is 55 s, not 60 s

The time column of `trajectories.parquet` carries accumulated floating-point
error. Two samples land just outside their nominal value:

- the sample nominally at t = 120 s is stored as **120.0000000000557**
- the sample nominally at t = 240 s is stored as **239.99999999996928**

The repository then handles this in **two incompatible ways**:

| code | comparison | samples in a 60 s window |
|---|---|---|
| `scripts/run_s021_hyperoxia_convergence.py` | `lo <= t <= hi`, strict | **12** |
| `src/detector.py` | `lo - 1e-6 <= t <= hi + 1e-6` | **13** |

So the S021 statistic described everywhere as "per-run mean over the final 60~s
of the 300~s rerun ($t = 240$--$300$~s)" is in fact computed over
**t = 245-300 s, a 55-second window**: the strict `>= 240.0` silently drops the
first sample. The atlas's own sweep is unaffected -- `PaO2_n_points` is **13** in
every row of `full_sweep/aggregated.parquet`.

**What this does not change.** Recomputing the published statistic over the
intended 13-sample window gives **642.8703527464863** against the published
`642.8715636969404`: a difference of **0.0012 mmHg**. The rounded value **643
mmHg is unchanged**, as are the abstract, section 2.4 and Supplement S9 prose
that carry it.

**What this does change, and it is not cosmetic.** The convergence test
`abs(drift) < 15.0` mmHg per 60 s is evaluated on the same window, and the extra
sample moves one run across the threshold:

| run | drift, 12-sample window | drift, 13-sample window |
|---|---:|---:|
| `S1_F_0106_long` | **-14.111446** (converged) | **-15.339612** (not converged) |

No other run is within 1.2 mmHg per 60 s of the threshold. Consequently, under
the window the documents actually describe, the converged count is **40 of 44
(90.9 %)**, not 41 of 44 (93.2 %).

**Ledger entries that rest on this:** `T1.24` (S1 frac converged 93.2 %) and
`T1.24b` (S1 converged 41 / 44). Both are correct descriptions of what the code
computed; what is wrong is the **stated window**, in the paper, the supplement
and the script's own docstring. The `S021 converged-plateau claim` guard checks
the value against the stored artefacts, so it cannot see this: it verifies
consistency between code and text, not between the window and its description.

**Nothing corrected. This is a scientific claim and it goes back to the author.**

### 14.3 The 120-second figure P.J. asked for

Both conventions reported, because neither is obviously the right one: the first
is strictly comparable to the published 643, the second is what the atlas
actually recorded.

| convention | population | 120 s median | IQR | 300 s median | gap |
|---|---|---:|---|---:|---|
| strict, 12 samples (matches the published 643) | 41 converged | **607.66** mmHg | [543.49, 657.09] | 642.87 | **35.21** mmHg, 5.48 % |
| epsilon, 13 samples (atlas convention) | 40 converged | **611.16** mmHg | [542.63, 658.83] | 642.87 | **31.71** mmHg, 4.93 % |

**Independent cross-check, and it is exact.** Under the epsilon convention the
recomputed per-run 60-120 s means reproduce the atlas's own recorded
`PaO2_mean` in `full_sweep/aggregated.parquet` with a maximum absolute
difference of **0.000e+00 mmHg** across all 40 runs, with `PaO2_n_points = 13`
in every row. Route A and route B are therefore the same measurement, and this
also settles empirically what Supplement S9 asserts about the reruns being
identical to the 120-second runs over the shared recorded interval.

**Consequences for the abstract decision rule set in section 13.**

- The median is **above 600 mmHg** under both conventions (607.7 / 611.2), so the
  median run does trip the `implausible` bound. P.J.'s sentence survives:
  **24 of the 41** (or 40) runs have a 120-second mean above 600 mmHg while the
  true late value is higher still.
- The gap is **31.7 to 35.2 mmHg, about 5 %**, not the ~3.6 % feared. Larger than
  the threshold considered too small to be worth abstract words, so the case for
  including it is now open rather than closed.
- **Any wording must carry the constraint from section 13:** this is the atlas's
  steady-state estimator applied to a window in which PaO2 is still rising. It is
  not a plateau and not "the PaO2 at 120 s".

**No anchor created, no text modified.** Creating one requires first settling
14.2, since the population (41 or 40) depends on it.

### 14.4 Correction to 14.2 and 14.3, same day: the truncation is asymmetric

Section 14.3 presented the two conventions as neutral alternatives. They are
not, and the reason matters.

Both windows lose exactly one sample under the strict comparison, but **at
opposite ends**, verified across all 60 reruns (strict gives 12 samples and the
epsilon 13, with no run departing from that):

| nominal window | what the strict comparison actually selects | end lost |
|---|---|---|
| t = 240-300 s | **245-300 s** | the first |
| t = 60-120 s | **60-115 s** | the last |

Both spans are 55 s, not 60 s.

**The consequence differs because the curve differs.** Over 240-300 s PaO2 is
essentially flat, so dropping the first sample costs **0.0012 mmHg** -- the
published 643 is untouched. Over 60-120 s PaO2 is still **rising**, which is the
entire finding, so dropping the last sample removes the highest value in the
window and biases the mean **downward by 1.15 mmHg**.

**The 607.66 mmHg reported in 14.3 is therefore an artefact and must not be
used.** It answers "what does the S021 script's convention give on the early
window", which is a question nobody asked.

**The defensible figure keeps the published population and uses the values the
atlas actually recorded:**

| quantity | value |
|---|---|
| population | the **41** drift-converged S1 reruns, exactly as published |
| 120-second median PaO2 | **608.81 mmHg** |
| IQR | [544.27, 657.24] |
| 300-second median, same runs | 642.87 mmHg |
| gap | **34.06 mmHg, 5.30 %** |
| runs whose 120 s mean exceeds the 600 mmHg bound | **24 of 41** |

These per-run values reproduce `PaO2_mean` in
`data/runs/full_sweep/aggregated.parquet` with a maximum absolute difference of
**0.000e+00 mmHg**, so this is not a recomputation but the atlas's own recorded
measurement, retrieved.

### 14.5 Two corrections of detail, and one independent validation

- 14.2 said `PaO2_n_points` is 13 "in every row" of the full sweep. It is 13 in
  every row **that carries output**; **20 rows of 1,280 carry 0**.
- The nearest other run to the convergence threshold is at **1.21** mmHg per
  60 s, not 1.2.

**Independent validation, unplanned.** Those 20 zero-output rows are exactly the
20 rows with `diverged == True`, and they fall on **S4_M 8, S1_M 4, S2_M 4,
S3_M 4 -- 20 male, 0 female**. That reproduces, from a different column of a
different artefact, the published headline "Solver divergence fell entirely on
the male body (20/1,280)".

## 15. The window fix, applied to code and data, 2026-09-01

Author's decision: option 2 of section 14.2 -- repair the selection rather than
rewrite the method as 245-300 s. Grounds, verified on two independent documents:
`preregistration.md` states 13 points five times (L58, L83, L84, L116, L135) and
at L191 makes "fewer than 13 rows in t in [60, 120]" an explicit failure
condition; `experiments_log/santino/S021_hyperoxia_convergence.md:121` declares
the S021 window as `mean PaO2 over [240, 300] s`. Rewriting the description
would have put the paper in contradiction with its own preregistration.

### 15.1 Not a protocol change: an unfinished migration

`scripts/audit_s030_provenance.py` documents this defect **since 2026-08-13**,
with the same float values re-derived independently this session
(`120.0000000000557`, `299.99999999991473`), and names the epsilon rule "the
atlas rule". S030 was migrated then; S021 predates it and never was. The
original S021 commit `a7db0d5` even states the intent -- drift over [240,300] s
"matching the locked atlas `DRIFT_MAX_DELTA_60S["PaO2"]`" -- so the code has
always disagreed with its own stated design.

### 15.2 Three scripts patched

| script | what it did | proof after the patch |
|---|---|---|
| `run_s021_hyperoxia_convergence.py` | 12 samples in a window documented as 60 s | selects **13** |
| `provenance_check.py` | compared a 12-sample mean against a 13-sample aggregate | now returns the aggregate value **exactly**, difference `0.00e+00` |
| `make_supp_fig_s4.py` | verified 12 probes while its message, its comment and commit `82a652b` all claimed 13 | verifies **13** |

Measured before the fix on 160 runs, 20 per cell across all eight cells, the
`provenance_check.py` mismatch exceeded its own 1e-3 tolerance on the I:E ratio
in **98 %** of runs, respiratory rate **69 %**, PaO2 **49 %**, PaCO2 **42 %**,
tidal volume **23 %**. It reported FAIL on faithful reproductions.

**Deliberately not patched:** the plotting slice of `make_supp_fig_s4.py`
(lines 149-152). It runs on the 50 Hz native grid, where the effect is one
sample in 3,001 and invisible in the render, and changing it would force the
regeneration of a published PDF for no scientific gain. The figure therefore
stays exactly reproducible from its script. Alternative rejected: aligning it
for stylistic consistency.

### 15.3 Data regenerated without re-running Pulse

`main()` re-executes all 60 runs through Docker. That was not done: the defect
is in the analysis, not the simulation, execution is deterministic, and the
trajectories are stored. Only the three window-dependent columns of
`plateau_stats.parquet` were recomputed, **through the patched `plateau_stats()`
itself**, and `summary.json` was rebuilt with the script's own decision logic.
Verified before writing: the seven untouched columns are identical, column order
is preserved, the summary's key set is unchanged and its `thresholds` block was
carried over rather than recomputed.

| field | before | after |
|---|---|---|
| `S1_frac_converged` | 0.9318181818181818 | **0.9090909090909091** |
| `S1_plateau_median_mmHg` | 643.3063280389815 | 643.2457645725224 |
| `S1_converged_plateau_median_mmHg` | 642.8715636969404 | 642.8703527464863 |
| `decision` | HYPOTHESIS_II | **HYPOTHESIS_II, unchanged** |
| aux S1 | med 643.3063, IQR [592.2080, 668.2195] | med 643.2458, IQR [592.1672, 668.0844] |
| aux S3 | med 143.5783, IQR [93.0331, 218.4896] | med 143.5946, IQR [92.9300, 218.4785] |
| aux S4 | med 72.5634, IQR [70.8287, 75.5612] | med 72.5555, IQR [70.7831, 75.5090] |
| S1 converged | 41 | **40** |

One run flips: `S1_F_0106_long`, drift -14.111446 under 12 samples,
-15.339612 under 13, against a threshold of 15. No other run lies within 1.21 of
the threshold.

**Every value matches the read-only impact audit of section 14 exactly**, which
was computed through a separate code path. Two instruments, one result.

**The preregistered decision is unchanged.** `S1_frac_converged` 0.909 still
clears the 0.75 floor and the plateau median still falls inside the
[580, 680] mmHg band, so HYPOTHESIS_II_TRANSIENT_REGIME_SUPPORTED stands.

### 15.4 Audit state: exactly the two anchors predicted

382 anchors: **380 PASS, 2 FAIL**. Sync: **92 PASS, 2 FAIL**. The two are
`T1.24` (93.2 against a computed 90.91) and `T1.24b` (41 against 40) -- the two
named in advance in section 14. The other seven S021 anchors still pass, and
nothing outside the S021 branch moved.

### 15.5 The 552 mmHg question, closed without a separate work item

Re-checked on three points. The 43.3 mmHg gap the median falls into is the
second largest of 37 consecutive gaps, and 34 % of an IQR of 128.4 mmHg over a
range of 307-660: large, but ordinary in a sample this dispersed, so the median
is imprecise rather than defective. The value is **not an audited anchor** -- one
occurrence, in the Figure S4 caption. And the one quantity that depends on it,
the 95 %-of-gain time, stays at **180 s** under both conventions. The number
changes anyway with this fix (552 to 530), so it is repaired in the same pass.

### 15.6 Still to do, nothing applied

- **12 lines across three documents**, inventoried in 14.3 as corrected: `41` to
  `40` (supplement 6, paper 1, monograph 3), `93.2` to `90.9` (3), `93 %` to
  `91 %` (monograph 1), `38` to `37` (4), `552` to `530` (1), `639` to `641` (1),
  the partition sentence, and the clause "the only three non-converged S1
  reruns" -- which becomes four.
- **Figure S4** (`figures/fig_s3_hyperoxia_convergence.pdf`, produced by
  `make_supp_fig_s3.py`) is drawn over the physiological-converged set, now 37
  instead of 38. Regenerating it changes a published artefact, so it waits.
- `PROVENANCE_CHECK.md` advertises "the **247-anchor** ledger"; the ledger holds
  **382**. Stale, unrelated to this fix.

## 16. Step 1 applied and closed, 2026-09-01

All of it applied on the author's go. Audits green, PDFs rebuilt, nothing
committed.

### 16.1 Twelve manuscript loci, and the guarded values behind them

| file | edits |
|---|---|
| `supplement.tex` | 10 edits over 6 lines: `41` to `40` in **three different phrasings** (`40 of 44 S1 reruns`, `40 drift-converged` x3, `40 converged`), `93.2~\%` to `90.9~\%`, `38` to `37` twice, `552~mmHg` to `530~mmHg`, `639~mmHg` to `641~mmHg`, Table S14 median `643.3` to `643.2`, and the partition sentence rewritten |
| `paper.tex` | `41 of 44 reruns (93.2~\%)` to `40 of 44 reruns (90.9~\%)`; `38 physiologically converged` to `37` |
| `manuscript.md` | `41/44` to `40/44`; `643.3` to `643.2` twice; `41 / 44 runs (93.2 %)` to `40 / 44 runs (90.9 %)`; the table row's `41 / 44 (93 %)` to `40 / 44 (91 %)` |

**Not 12 lines in three files, as first proposed: 20 edits in five.** The values
also live in the guards themselves, which the first inventory missed:

- `scripts/audit_claims.py`: `T1.24` `manuscript_value` 93.2 to 90.9 and its
  `manuscript_text`; `T1.24b` 41 to 40 and its text. Both carry a dated comment
  naming the cause.
- `preprint_npj/paper_to_monograph_map.md`: `T1.24` and `T1.24b`
  `expected_value` and `format_in_paper`, with notes recording the change.
  **`expected_occurrences` is unchanged in both** -- verified by counting the new
  literals: `40 of 44 reruns` occurs once, `90.9~\%` twice, exactly as before.
- `scripts/make_supp_fig_s3.py`: its docstring stated 41 and 38.

**A search-and-replace trap, avoided.** `scripts/audit_claims.py:3146` also
holds `manuscript_value=41`, for `T5.clip.clean_dbp_shortened`, "41 of 78 clean
diastolic elementary-effect pairs". Unrelated to S021 and left alone.

**Verification after the edits:** a sweep for the old values across the three
documents returns **zero** residuals, and the new values appear with exactly the
counts the inventory predicted -- including the six occurrences of the converged
count in the supplement.

### 16.2 Both figures regenerated, and one lesson from the guard

`fig_s3_hyperoxia_convergence.pdf`, rendered as **Figure S4**, is drawn over the
converged set and had to follow. Its own diagnostics confirm the numbers from a
third independent code path: `n_converged = 40`, `n_physio = 37`, median PaO2
`530.2` at t = 0 and `641.1` at t = 300, time-to-95 % still `180 s`.

**First attempt was wrong and the repository caught it.** Regenerating directly
stamped a wall-clock `/CreationDate`, and the figure-timestamp guard failed
28/29. `scripts/verify.py` says so in a comment written long before: "Running a
generator directly ... still produces a timestamped PDF. verify.py is the
canonical path." Redone with `SOURCE_DATE_EPOCH=1776895508` and
`FORCE_SOURCE_DATE=1`; the guard returned to 29/29.

`fig_s4_vt_waveform.pdf`, rendered as **Figure S3**, was regenerated too. Its
plotting slice had been left strict on purpose in section 15.2, on the grounds
that the effect is one sample in 3,001 on the 50 Hz grid. **The new guard of
16.4 removed that exception**: an undocumented deliberate exception is
indistinguishable from the defect. The slice now carries the tolerance and the
window holds 3,001 rows instead of 3,000.

### 16.3 Table S14 and section S9.3 renamed

The values were correct; the vocabulary was not. `plateau` is now reserved for
runs whose convergence is established.

- Subsection title: "Oxygenation **plateau** across ARDS severity" to
  "**Final-60-s oxygenation** across ARDS severity".
- Table S14 title: "**Converged PaO2 plateau** by ARDS scenario" to
  "**Final-60-s PaO2** by ARDS scenario".
- Column headers: "Plateau median / IQR" to "Final-60-s median / IQR".
- The prose "The plateau (per-run mean over the final 60 s...)" to "The
  final-60-s mean PaO2 (per run, over t = 240-300 s...)".
- The orphaned caption sentence "Convergence is judged by the preregistered
  drift criterion" replaced by one that says why the word is avoided: the
  quantity covers every run, converged or not, and **four** of the 44 S1 reruns
  do not meet the criterion.
- "the elevated S1 **plateau**" to "the elevated S1 **final-60-s oxygenation**",
  for consistency inside the renamed section.

**A false cross-reference caught in my own new caption.** It first claimed the
per-run convergence status is given in S9.1. S9.1 gives the count, not a per-run
listing; reworded to "as stated in".

**One residual, deliberately not changed:** S9.2 still reads "six of the 44 S1
reruns relaxed to PaO2 **plateaus** above 700 mmHg", where three of the six are
non-converged. Loose, but the sentence's own point is that those values are
unphysical, and it sits outside the renamed subsection. Flagged, not touched.

### 16.4 A guard, so this cannot happen a third time

`check_window_tolerance()` in `scripts/audit_claims.py`. It scans every
`scripts/*.py` and `src/*.py` for a comparison of `time_s` against a bound and
fails on any that carries no tolerance term.

It ships with both controls: a **positive** one, that the finder actually sees
the comparisons in `src/detector.py`, and a **negative** one, that a synthetic
strict line is rejected. `audit_claims.py` itself is excluded, since the strings
it matches are the guard's own pattern and its own control.

Result on arrival: **11 checks, 11 PASS, 72 files scanned, 9 carrying a
time-window comparison.** On its first run it failed two files -- itself, and the
deliberate exception of 15.2 -- and both were repaired rather than allowlisted.

### 16.5 Final state, verified end to end

| | |
|---|---|
| anchors | **382 / 382 PASS** |
| paper-monograph sync | **94 / 94 PASS** |
| figure timestamps | **29 / 29 PASS** |
| window tolerance | **11 / 11 PASS** |
| total FAIL | **0** |
| `check_render.py` | PASSED, 3 accepted residues, 0 new |
| build | paper 38 pages, supplement 52; **0 undefined references** in either log |
| rendered PDF | the paper reads "S1 (healthy) cohort, **40 of 44 reruns (90.9 %)** converged to a stable plateau" |

The chain is verified at every link: stored trajectories, the patched code, the
regenerated artefacts, the manuscript text, the guards, and the built PDF.

**Nothing is committed and nothing is pushed.** `git status` shows the five
files of section 15 plus `paper.tex`, `supplement.tex`, `manuscript.md`, the
crosswalk, `make_supp_fig_s3.py`, and the two figure pairs.

### 16.6 Frozen, found but not fixed

- `PROVENANCE_CHECK.md` advertises "the 247-anchor ledger"; it holds 382.
- `T2.f003.shunt_s4` now sits at 89 % of its 0.05 tolerance, against 73 % before.
- `audit/npj_format_compliance.md` entry C-5 judged the Discussion compliant with
  the "no limitations section" rule when it was 1,602 words; it is 2,171 today.
- Supplement S9.2's "plateaus above 700 mmHg", see 16.3.

## 17. What the rewrite must not lose -- the standing checklist, 2026-09-01

Compiled by going back to the sources, not from memory. Every item verified
against the repository on the date of writing.

### 17.1 Correction: section 14.3 and 14.4 are superseded

Those sections recommended the 120-second figure computed over **41** runs
(608.81 mmHg), on the grounds that 41 was the published population. After the
step-1 fix it is **40**. The current figures, recomputed on the regenerated
artefacts:

| quantity | value |
|---|---|
| population | the **40** drift-converged S1 reruns |
| 120-second median PaO2 | **611.16 mmHg** |
| IQR | [542.63, 658.83] |
| 300-second median, same runs | 642.87 mmHg |
| gap | **31.71 mmHg, 4.93 %** |
| runs above the 600 mmHg bound | **24 of 40** |

Cross-checked a fourth time: these per-run values equal the
`PaO2_mean_orig_120s` column of `plateau_stats.parquet`, carried over from the
original sweep aggregate, to **0.000e+00 mmHg**. Each window holds 13 samples,
asserted in the computation.

The interpretive constraint of section 13 stands: this is the atlas's
steady-state estimator applied to a window in which PaO2 is still rising. Not a
plateau, not "the PaO2 at 120 s".

### 17.2 Content that the Introduction rewrite would delete

**The one that must move in the same commit.** `paper.tex:150` carries

> "An atlas cell is therefore anchored to a clinically recognisable state rather
> than to an arbitrary engine setting (Methods~\S\ref{sec:methods-sweep};
> Supplement~\S\,\ref{sec:s5-berlin})."

It sits inside the Introduction, and the draft of section 7.1 **does not carry
it**. Section 5.5 deferred it to "the Methods pass", but the Methods pass comes
several sections later: between the two the sentence, and its two cross-
references, would simply be absent from the paper. **Place it in Methods 4.3 at
the same time as applying the Introduction, not afterwards.**

**Already handled:** the engine-determinism sentence of `paper.tex:146` is
carried by the supplement draft 7.2. Verified present.

**Open decision D1:** `virtual-patient`, `emergency-medicine`, `platforms`. The
author's shorter form, agreed in principle, is "(3) medical education and
simulation training **on virtual-patient and emergency-medicine platforms**" --
10 words against 13, keeping all five notions. An earlier proposal of mine
dropped "simulation training", which occurs **once in the whole paper**; that
version is withdrawn.

**Open decision D2:** verb tense. npj states no rule; the draft already follows
the ordinary convention (present for standing facts, past for what was done).
P.J.'s past-tense change to `lie` is moot -- the draft rewrote that sentence -- so
only his past-tense change to "does sweep" remains.

### 17.3 Scientific debts, still open

- **"makes Vt reproducible"**, `paper.tex:128` (abstract) and `:317` (2.3), two
  occurrences, guarded by nothing. Bounded at 78.1 % of reruns below threshold,
  i.e. 14 of 64 remain above. Repair 2.3 in the Results pass, the abstract in
  the abstract pass. Wording to describe the measured effect, not to assert
  reproducibility; note `0.351` and `0.016` are ledger literals with
  `expected_occurrences` 5 and 4, so putting them in the abstract costs a
  crosswalk bump.
- **The determinism antecedent.** Once the Introduction rewrite moves
  `paper.tex:146` to the supplement, section 2.3's "deterministic Vt delivery"
  has no sentence in the paper body defining engine determinism. Resolve with
  the item above, in the Results pass.

### 17.4 P.J.'s open items

| item | status |
|---|---|
| comment 68 (is his rewrite correct) | answer: no, with the evidence of 3.2 item 3 |
| comment 70 (the sentence is unclear to him) | rewrite it plainly |
| comment 100 (where the bounds are reported) | add a pointer at `paper.tex:187`; the bounds are at `:426` and Supplement S3 |
| his note on the Vt wording (10.1) | his unresolved note; decide in the abstract pass |
| his empty PaO2 placeholder | the number now exists, 17.1; decide whether it earns abstract words |
| his section-order question | answer from npj's own Article table: Introduction, Results, Discussion, Methods |
| the edits to accept | six colon splits, the (1)-(4) numbering, `lever` to `level` **twice**, "Yet despite this footprint" to "Yet" |
| the edits to refuse | the title, the three abstract wording changes, the blood-volume rewrite, the inserted word, the tense changes, the unit notation, the broken clause (iv), `plateaus` to `plateau` |

### 17.5 npj rules that bind every pass

Abstract at most 150 words and it currently sits at exactly 150 · Introduction
no subheadings · Results subheadings expected · **Discussion: no subheadings, no
limitations section, no conclusions section** · Methods entirely in the main
file, as concisely as possible but carrying every element needed for
interpretation and replication · figure legends at most 350 words each, longest
is 335 · at most 60 references, currently 40 going to 37.

⚠️ The Discussion rule needs re-checking during that pass:
`audit/npj_format_compliance.md` entry C-5 judged it compliant when the
Discussion was 1,602 words; it is 2,171 today.

### 17.6 The narrative to preserve

The author's instruction, 2026-09-01: this is a reliability check of a simulator
used **for education** and **for generating synthetic training data for machine
learning**. Verified present in the Introduction draft: *education*,
*simulation training*, *synthetic*, *machine-learning*, *cohort*,
*digital twin* -- all six. No pass may thin this framing out for length.

### 17.7 Mandatory before submission, not during the rewrite

- **Section 4.7 must declare a second supervisor-review phase** (Opus 5 and
  GPT-5.6). Two phrases at `paper.tex:462` become literally false: "through
  **the** supervisor-review phase" and "for **the final rounds**". The loci
  drifted from L460 to L462 since the note was written, so locate them by text.
- The standing pre-submission cleanup sweep, and the per-reference citation
  audit on two axes: source actually read, and claim genuinely supported.

### 17.8 Frozen, found but not fixed

Carried from 16.6, unchanged: `PROVENANCE_CHECK.md` says 247 anchors against
382 · `T2.f003.shunt_s4` at 89 % of its tolerance · the stale C-5 judgement
above · Supplement S9.2's "plateaus above 700 mmHg" over a set of six of which
three are non-converged.

## 18. Step 2 applied: the Introduction, 2026-09-01

Applied on the author's go, with decisions D1 and D2 settled. Audits green,
both documents rebuilt, nothing committed.

### 18.1 What went in

| unit | destination | result |
|---|---|---|
| draft 7.1 | `paper.tex` lines 138-157, replaced | Introduction **1,417 to 777 words, minus 45.2 %**; 20 source lines to 10 |
| the deferred sentence of 5.5 | Methods 4.3 | moved in the **same** edit, not deferred to a later pass |
| draft 7.2 | Supplement S1, after the opening paragraph | 188 words |
| draft 7.3 | Supplement S16, new opening paragraph | 122 words |
| draft 7.4 | Supplement S1, **first sentence only** of the low-fidelity line | quote corrected against the primary source, citation added |
| crosswalk `T1.01` | `expected_occurrences` 46 to 47 | measured before and after: paper 25 to 26, supplement 21 unchanged |

**D1, settled by the author.** "(3)~medical education and simulation training
**on virtual-patient and emergency-medicine platforms**" -- 10 words against the
original 13, keeping all five notions. The earlier proposal that dropped
"simulation training" stays withdrawn. Cost: **+5 words**, not the +6 first
stated.

**D2, settled by the author.** Present tense kept. P.J.'s change of "does
sweep" to the past tense is declined; his change to `lie` was already moot.

### 18.2 The two traps that were avoided, and the evidence they were

**The deferred sentence would have vanished.** `paper.tex:150`, "An atlas cell
is therefore anchored to a clinically recognisable state rather than to an
arbitrary engine setting", sat inside the Introduction and is absent from draft
7.1. Section 5.5 had deferred it to "the Methods pass", four sections later.
Moved now instead. Two adaptations were needed and are recorded here rather than
made silently: its `Methods~\S\ref{sec:methods-sweep}` pointer would have
referred to the section it now lives in, and its `Supplement~\S\,\ref{sec:s5-berlin}`
pointer duplicated the sentence it now follows. Both dropped; the sentence sits
directly after the Berlin-calibration sentence, where its "therefore" finally
has an antecedent.

**7.4 is a sentence, not a line.** The line it sits on also carries the only
pointer in the repository back to Section 1 of the paper, and the REL_4_3_2
paragraph. The application asserted both survived before writing, and the built
PDF confirms it: "...``a low fidelity clinical approach'' and states it is ``not
necessarily for high fidelity predictive purposes'' [6] ... **This
self-description frames the present atlas's contribution (Section 1 of the main
manuscript)**".

### 18.3 Verification, before and after

Before applying, on the final text with D1 in it: 10 cite keys all present in
`paper.bib` with a negative control; the single `\ref{sec:s1}` resolves;
braces 25/25, dollars even, quotes paired, no non-ASCII; **zero** of the 1,050
guard segments matched, against a positive control that fires on the Discussion;
exactly one crosswalk literal introduced, `1{,}280`, and none lost; no banned
vocabulary.

After applying:

| | |
|---|---|
| anchors | **382 / 382 PASS** |
| sync | **94 / 94 PASS** |
| figure timestamps | **29 / 29 PASS** |
| window tolerance | **11 / 11 PASS** |
| total FAIL | **0** |
| `check_render.py` | PASSED, the same 3 accepted residues, **0 new** |
| build | 0 undefined references in either log |

**The citation invariant holds: the union over paper and supplement is still 45.**
The paper's own list falls 40 to 37, the supplement rises 22 to 24, and
`pulsecircuit`, `pulsesystem` and `pulsepatientmethod` are exactly the three
that moved. Consequence for the co-authors, unchanged from 5.2: 32 of 37
reference numbers shift.

**Pagination: paper 38 to 36 pages, supplement 52 to 53.** The three accepted
typographic residues of section 5.6 held at their exact magnitudes despite the
reflow, which 5.6 said had to be measured rather than assumed.

**In the rendered PDF:** the objective is the last idea of the Introduction, as
P.J. asked; "virtual-patient and emergency-medicine platforms" is present;
"does sweep" is present; the old "Several implementation choices" paragraph is
gone; and Supplement S1 and S16 carry their new paragraphs.

### 18.4 Still open, carried forward

Everything in section 17 that is not the Introduction. Nearest: the first real
pagination in double spacing, to calibrate words per page before Results.

## 19. Results pass: drafts held for the author's go, 2026-09-02

Budget fixed at **22 Word pages** = 5,314 words of .tex prose, measured at
**241.6 prose words per double-spaced Word page** (11,353 words rendering to 47
pages; control 25 pages single-spaced, ratio 1.88). Results is allocated ~890.
Nothing below is applied.

### 19.1 Section 2.1 draft

```latex
The atlas comprises 1{,}280 simulations spanning eight cells of 160 runs each, one cell per clinical scenario (S1 healthy, S2 mild, S3 moderate, S4 severe ARDS) and patient sex (Figure~\ref{fig:design}). Every run carries the four preregistered flags defined in Methods~\S\ref{sec:methods-detector}, whose hard physiological bounds are listed there and their provenance in Supplement~\S\,\ref{sec:s3-hard-bounds}.

Three of the four preregistered hypotheses are settled by Table~\ref{tab:flag_summary} alone. H2, silent input clamping, is \emph{not supported}: the \texttt{clamped} category is empty in every cell, 0 of 1{,}280, so Pulse either accepts a submitted setup value or rejects it loudly. H3 is supported: solver divergence appears outside the previously characterised ARDS instability band. H4 is supported: failure modes are cell-dependent rather than uniform. H1 is settled in \S\ref{sec:results-morris}.

Retention is strongly cell-dependent and depends on which screen is applied. Under the four-flag screen 663 of 1{,}280 runs (51.8~\%) are clean, ranging 3.43-fold across cells, from 144 of 160 in moderate ARDS on the male body down to 42 of 160 in the healthy female cell. Under the hard-failure-free screen, which admits runs flagged only \texttt{not\_steady\_state}, 1{,}134 of 1{,}280 (88.6~\%) survive, a 1.51-fold spread. The two screens deplete opposite ends of the severity axis, and the per-cell breakdown is in Table~\ref{tab:screen_retention}; Supplement~\S\,\ref{sec:s4} decomposes which runs each screen removes and why.
```

### 19.2 Section 2.2 draft

```latex
Figure~\ref{fig:morris} shows the Morris $\mu^{*}$, the input-importance metric, for the six outputs across the eight cells and seven swept inputs. H1 is supported in 48 of 48 cell $\times$ output combinations: the top-three inputs account for 0.658--0.998 of the summed $\mu^{*}$, with a median top-3 fraction of 0.928. The lowest values, from 0.658 to 0.727, all fall in severe-ARDS gas-exchange cells, where shunt physiology blunts every oxygenation input at once. Which inputs dominate depends on the output. Cardiovascular outputs are cardio-input dominated, output HR by input HR and MAP by SBP in every cell with no measurable ventilator cross-talk, while gas-exchange outputs are ventilator-driven: FiO$_2$ dominates PaO$_2$ in mild and moderate ARDS and collapses to a near-flat dependence in severe ARDS.

Influence is not proportionality. Applying the preregistered $\sigma / \mu^{*} > 0.6$ threshold to each cell's top-three inputs, and retaining only combinations that clear it in all five bootstrap draws, leaves 23 of the 144, spread over 17 of the 48 cell $\times$ output combinations; all seven inputs and all four scenarios appear, so non-linearity is common rather than localised. Delivered tidal volume is the most affected output, in 8 of the 23, and is also the channel whose breath-to-breath oscillation dominates the \texttt{not\_steady\_state} flags (\S\ref{sec:results-vcac}); the two findings therefore cannot appear on the same runs. The ranking is cross-verified against a SHAP surrogate in Supplement~\S\,\ref{sec:s13}.
```

### 19.3 Section 2.3 draft

```latex
Across the full sweep, the single largest source of \texttt{not\_steady\_state} flags is tidal-volume (Vt) oscillation under VC-AC ventilation, quantified as the delivered Vt coefficient of variation over the final 60~s of the 120~s simulation. Vt oscillation is the \emph{primary} such flag on 20.6~\% of runs: the delivered breath volume never settles to a single value but keeps changing from breath to breath, a genuinely oscillating output rather than a solver failure. The effect concentrates in healthy adults and falls markedly with increasing ARDS severity, strongest where the set respiratory rate is high and lung compliance is normal. This is the in-silico signature of \emph{patient--ventilator dyssynchrony}, well documented clinically in volume-control ventilation~\cite{figueroacasas2016}; the specific conditions that produce it here are our own in-silico finding.

A preregistered follow-up experiment isolated the mechanism. Re-running 64 of the affected configurations with Pulse's \texttt{InspirationPatientTriggerPressure} set to $-2$~cmH$_2$O collapses the median Vt CV from 0.351 to 0.016, and 78.1~\% of the locked-trigger reruns drop below the 0.05 steady-state threshold (Figure~\ref{fig:corrections}a). The lock is an exploration lever for deterministic Vt delivery, not a clinical recommendation: it decouples breath delivery from the engine's modelled respiratory drive, whose coupling is what reproduces effort-dependent breath-to-breath variability in Pulse's default configuration. The full protocol, the worst-affected configuration and the per-run values are in Supplement~\S\,\ref{sec:s8}.
```

### 19.4 Section 2.4 draft

```latex
A second cluster of preregistered classifier flags concentrates on the highest inspired-oxygen settings. Within the locked 120-second simulation window, Pulse's steady-state mean PaO$_2$ exceeds the classifier's upper bound of 600~mmHg on 34 of the 126 \texttt{implausible}-flagged runs, and 91~\% of these excursions occur at FiO$_2 \geq 0.95$. A preregistered 60-run rerun at 300 seconds discriminated an engine defect from a window-length artefact, and supports the latter: in the S1 (healthy) cohort, 40 of 44 reruns (90.9~\%) converged to a stable plateau (Figure~\ref{fig:corrections}b), and the converged S1 plateau median was 643~mmHg, sitting approximately 20~mmHg \emph{below} the alveolar-gas-equation prediction rather than above it, which rules out a cohort-wide oxygenation runaway. It does not establish that the plateau level itself is right, which would take validation against measured arterial data and is outside the scope of a curation map.

The practical consequence is direct: hyperoxia studies on Pulse should record at least 300 seconds of simulation before extracting a steady-state plateau. The 120-second window remains adequate for cardiovascular and ventilation outputs. Extended-window runs on healthy lungs at FiO$_2$ = 1.0 can additionally enter a separate solver-instability regime, affecting the female reference body far more often than the male, so users running them should screen each PaO$_2$ trajectory individually. The full protocol, the time-to-plateau statistic and the instability characterisation are in Supplement~\S\,\ref{sec:s9}.
```

### 19.5 Section 2.5 draft

```latex
Across the full 1{,}280-run sweep, solver divergence is rare but strikingly sex-stratified. 20 runs (1.6~\%) failed to complete with finite output, and \emph{all 20 fell on the male reference body}, against zero divergences across the 640 runs on the female reference body (Figure~\ref{fig:sex_bv}a). The 20 divergence events are not spread uniformly through the input space: they span only 8 distinct operational-input vectors, and FiO$_2$ sat at its 1.0 boundary in 13 of the 20.

A preregistered follow-up experiment isolated the mechanism. Pulse's \texttt{SetupPatient.cpp} computes blood-volume baseline from a sex-independent allometric relation on body weight, yielding 4{,}803~mL for the 67.3~kg male reference body and 3{,}996~mL for the 56.2~kg female body. The two bodies therefore share essentially the same blood volume per kilogram, so what separates them is absolute volume rather than sex-specific physiology. Re-executing the 20 originally-diverged male inputs with an explicit \texttt{BloodVolumeBaseline} override took the divergence count from 20 / 20 at the default to 0 / 20 at both an intermediate 4{,}400~mL bracket and the engine's own setup floor of 4{,}082~mL (Figure~\ref{fig:sex_bv}b). Divergence is one axis of sex-stratified behaviour and the steady-state values are far less separated; the per-output comparison against its within-sex null, and the full override protocol, are in Supplement~\S\,\ref{sec:s10}.
```


## 20. The Results package: what must ship in one commit, 2026-09-02

Drafted and verified, **not applied**. Every element below was measured against
the repository on the date of writing, not carried over from an earlier message.

### 20.1 Why it is one commit and not several

Adding the worst-case sentence to Supplement S8 on its own was tried and
**reverted**: with the old section 2.3 still in the paper, `1.826` and `0.018`
then occurred twice each against an expected 1, and `audit_claims.py` returned
`exit=1` on exactly those two rows and nothing else. The prose replacement, the
supplement additions and the crosswalk edits are therefore a single unit.

### 20.2 The six drafts

| subsection | before | after | anchors |
|---|---:|---:|---|
| 2.1 Overview | 1,041 | **218** | keeps `(0 / 1{,}280 across every cell)` and `20 / 1{,}280`, which live nowhere else |
| 2.2 Rankings | 677 | **214** | 4 of 4 kept, including `median top-3 fraction of 0.928` in its own prose form |
| 2.3 VC-AC | 600 | **213** | 6 of 8; `1.826` and `0.018` move to S8 |
| 2.4 Hyperoxia | 499 | **217** | 6 of 6 |
| 2.5 Sex / blood volume | 1,109 | **201** | 11 of 13 |
| 2.6 becomes a pointer | 640 | **77** | 4 tachycardia anchors move to S15 |
| **total** | **4,606** | **1,140** | **-75.2 %** |

Global check across the whole of Results rather than subsection by subsection:
39 anchors in the current prose, **31 carried by the drafts, 8 relocated, none
invented**.

The section 2.6 pointer names all four secondary observations with verified
targets: `sec:s5` (ARDS instability zone), `sec:s15` (compensatory tachycardia),
`sec:s3-sobol` (Sobol decision), `sec:s4` (not_steady_state attribution), indexed
at `sec:s17-summary`. Each label was opened and read before the sentence was
written.

### 20.3 Supplement additions

One sentence at the end of `sec:s8-protocol`, carrying the two literals the
paper gives up:

> Its effect on the single worst-affected configuration (S1\_F\_0117, run index
> 117 in the healthy-female cell) is to take the delivered Vt coefficient of
> variation from 1.826 to 0.018.

Supplement S15 already carries the four tachycardia values, in its table, as
`$73.8 \pm 20.4$`, `$155.7 \pm 34.7$` and `$147.1 \pm 31.8$`. Nothing to add
there; only the crosswalk rows move.

### 20.4 Crosswalk edits

**A correction of an earlier reading.** The field description says
`format_in_paper` is "the exact LaTeX-rendered formatting used in `paper.tex`",
and on that basis these rows were first slated for retirement. Measured instead:
**38 of the 94 rows already point at the supplement**, and `check_paper_sync`
counts occurrences "across the COMBINED paper.tex + supplement.tex corpus". The
rows are therefore **repointed, not retired**, and the guard survives.

| claim | now | becomes | occurrences |
|---|---|---|---|
| `T1.05` | `1.826`, §2.3 prose | same literal, Supplement S8 | 1 |
| `T1.s014.worstcase_locked_vtcv` | `0.018`, §2.3 prose | same literal, Supplement S8 | 1 |
| `T2.hr.S4.mean` | `147.1~bpm`, §2.6 | `147.1 \pm 31.8`, Supplement S15 | 1 |
| `T2.hr.S3.mean` | `155.7~bpm`, §2.6 | `155.7 \pm 34.7`, Supplement S15 | 1 |
| `T2.hr.S1.mean` | `73.8~bpm`, §2.6 | `73.8 \pm 20.4`, Supplement S15 | 1 |
| `T2.hr.S1.std` | `\sigma = 20.4$~bpm`, §2.6 | `\pm 20.4`, Supplement S15 | 1 |

Each replacement form was counted in the live documents before being proposed:
all four S15 forms occur exactly once in the combined corpus, and zero times in
the paper.

Three counters fall rather than move: `1.6~\%` from 2 to 1 (section 2.1 gives it
up, section 2.5 keeps it), and `19.8~\%` and `36.1~\%` from their current values,
both already present once in the supplement.

**Not affected:** the `T2.hr.*` ledger anchors, which are generated in a loop
from `data/runs/full_sweep/aggregated.parquet` and attached to monograph section
3.4.1, not to the paper. They keep guarding the four values against the data
whatever happens to section 2.6, and the monograph carries each of them two or
three times.

### 20.5 Still to settle before applying

**107 words over budget.** The allocation for 22 Word pages gives Results 1,033;
the drafts total 1,140. The section 2.6 pointer is the obvious lever: 77 words
because it names each observation and its target, reducible to about 40 by
naming only the themes and letting `sec:s17-summary` carry the routing.

Legend work is unaffected by this: measured after the rewrite, only **one**
anchor would live solely in a caption, `median 0.928` in the Figure 2 caption,
and section 2.2 keeps its own prose form of the same value.
### 19.6 Section 2.6 pointer draft

```latex
Four further observations bear on downstream interpretation and are stated in full in the Supplementary Information: the first public characterisation of Pulse's ARDS impairment-fraction solver-instability band (\S\,\ref{sec:s5}); a compensatory tachycardia that decouples output heart rate from input heart rate under hypoxemia (\S\,\ref{sec:s15}); a preregistered Sobol bolt-on that was triggered but not executed (\S\,\ref{sec:s3-sobol}); and a limitation of the flatline rule itself, which does not always separate physiological saturation from numerical pinning (\S\,\ref{sec:s4}). They are indexed in \S\,\ref{sec:s17-summary}.
```


## 21. Methods, Discussion and the supplement migration: drafts, 2026-09-02

Written and verified, **not applied**. Every count below was measured on the
file, not carried over from an earlier message.

| unit | before | after | crosswalk anchors | guard literals |
|---|---:|---:|---|---|
| Methods 4.1 | 339 | 154 | 1/1 | - |
| Methods 4.2 | 310 | 218 | - | `216.5` restored |
| Methods 4.3 | 597 | 358 | 9/9 | - |
| Methods 4.4 | 867 | 314 | 6/6 | 5 carried, 3 rescued from 2.6 |
| Methods 4.5 | 506 | 323 | 1/1 | - |
| Methods 4.6 | 647 | 384 | 2/2 | 2 |
| **Methods total** | **3,283** | **1,751** | **18/18** | **8 carried** |
| Discussion | 2,171 | 1,128 | 7/7 | 5/5 |
| Supplement S2 new subsection | - | 565 | - | carries `clipping shortened 9 of 20 DBP steps` |

### 21.x draft `met41`

```latex
All simulations used Pulse v4.3.1 (Kitware, Apache-2.0)~\cite{bray2019}, a real-time-capable lumped-parameter whole-body physiology engine whose respiratory sub-model is a 5-compartment lung~\cite{pulserespmethod}. The engine was executed inside a single \texttt{pulse-atlas-engine} Docker image, pinned for the entire 1{,}280-run sweep so that every simulation runs against bit-identical engine binaries. Runs were orchestrated by a thin Python layer around Pulse's command-line interface, which writes one JSON configuration per Morris input vector --- reference body, ARDS scenario condition, ventilator action set, and the seven operational inputs at their sampled values --- and spawns a container against that image.

Re-running the pipeline reproduces the canonical outputs bit-for-bit at three successive stages, each checked against its own committed artefact: the input sample, the per-cell aggregate tables, and the derived statistics. Mechanical ventilation was restricted to volume-controlled assist-control (VC-AC) mode so that all runs remain directly comparable; pressure-targeted modes lie outside the atlas's scope. The dispatch hardware and the full environment are given in Supplement~\S\,\ref{sec:s12-env}.
```

### 21.x draft `met42`

```latex
Two adult reference bodies were used: a male body (age 18, 67.3~kg, 180~cm) and a female body (age 18, 56.2~kg, 163~cm). Both weights are U.S.\ Centers for Disease Control and Prevention (CDC) growth-chart 50th-percentile weight-for-age values for each sex~\cite{kuczmarski2002cdc}, taken from the CDC row at \texttt{Agemos}~=~216.5. The female height matches the CDC 50th percentile and Pulse's own standard female height; the male height is researcher-fixed. Supplement~\S\ref{sec:s3-bodies} carries the full provenance.

Pulse also refuses some setup values outright. Two of those constraints act on inputs swept here, a gate on systolic and diastolic blood pressure and acceptance bands on the initial heart and respiratory rates; both were verified against the Pulse source and by boundary-probe runs before the sweep (Supplement~\S\,\ref{sec:s2}), and the sampler ranges were set inside them. A third, Pulse's limit on the pulse-pressure ratio, is deliberately not imposed on the Morris sample, because that would distort the sample geometry the elementary-effect estimator depends on; it is applied one step later, when each configuration is written, and every run records the requested value, the applied value and a clip flag (\S\ref{sec:methods-sweep}). Every configuration actually submitted to Pulse therefore lies inside the accepted envelope. A fourth constraint, a hard per-patient floor on the male body's blood-volume baseline, is never exercised by the sweep and is characterised separately in \S\ref{sec:results-sex}.
```

### 21.x draft `met43`

```latex
Seven user-facing operational inputs were swept across their verified Pulse acceptance ranges: heart rate (HR, 50--110~bpm), systolic and diastolic blood pressure (SBP 90--120~mmHg, DBP 60--80~mmHg with the post-clip pulse-pressure constraint), respiratory rate (RR, 8--20~breaths\,min$^{-1}$), tidal volume (Vt, 300--700~mL), inspired oxygen fraction (FiO$_2$, 0.21--1.0) and positive end-expiratory pressure (PEEP, 0--15~cmH$_2$O). Each range is anchored to a primary verification source, table by table, in Supplement~\S\,\ref{sec:s2}. Mean arterial pressure was derived as $\mathrm{DBP} + (\mathrm{SBP} - \mathrm{DBP})/3$ rather than swept independently. The swept heart-rate and blood-pressure values are setup interventions honoured at ingestion rather than setpoints maintained against the engine's own reflexes: Pulse re-baselines those fields to the stabilised state at the end of stabilisation, and no action used here rewrites them afterwards.

Four scenarios spanned the adult critical-care severity range: a healthy baseline (S1, ARDS impairment fraction = 0) and three ARDS severities (S2, mild, impairment = 0.26; S3, moderate, impairment = 0.60; S4, severe, impairment = 0.95). At a reference ventilation setting based on the ARDSnet low-tidal-volume framework, these impairment fractions place each scenario in a Berlin P/F band, and both that calibration and its sweep-wide FiO$_2$ dependence are tabulated in Supplement~\S\,\ref{sec:s5-berlin}. An atlas cell is therefore anchored to a clinically recognisable state rather than to an arbitrary engine setting. The three severities also bracket the 0.91--0.945 solver-instability zone documented at design time (Supplement~\S\,\ref{sec:s5}); the atlas's own continuous-severity sweep subsequently widened that band to $[0.879, 0.945]$ (\S\ref{sec:results-secondary}). Pulse represents severity as a single per-lung scalar driving four hard-coded, adult-calibrated interpolation curves, mapped in Supplement~\S\,\ref{sec:s5-mapping}.

Sensitivity was screened with the Morris elementary-effects design~\cite{morris1991, campolongo2007}, a global screening method whose cost is linear in the number of inputs. The sample was generated with SALib~\cite{iwanaga2022,herman2017salib} using 20 trajectories at 4 grid levels per input and random seed 42. Each trajectory contributes $7 + 1 = 8$ model evaluations, giving 160 runs per (scenario $\times$ sex) cell and 1{,}280 runs across the full sweep. The trajectory count was fixed at 20 in preregistration as a computationally tractable design; it was not selected through a trajectory-count convergence analysis. Each run executed for 120 seconds of simulated time, with output channels sampled at 5-second intervals (13 samples in the final 60-second steady-state window).
```

### 21.x draft `met44`

```latex
Every simulation was classified by a four-flag steady-state classifier before any statistical analysis. \texttt{clamped} is the preregistered label for a run whose Pulse setup log matches any of 4 documented input-rejection patterns. This log-based detector identifies \emph{explicit} setup rejection and cannot by itself detect a silent substitution; a post hoc input-instantiation audit closes that gap and is reported in \S\ref{sec:results-overview}. \texttt{diverged} fires when the simulation failed to complete with finite output, the CSV is missing, or the engine exited with a non-zero status.

\texttt{implausible} fires when any steady-state output mean exceeds the locked hard physiological bounds: HR [20, 220]~bpm, MAP [30, 180]~mmHg, Vt [50, 1{,}500]~mL, SpO$_2$ [50, 100]~\%, PaO$_2$ [20, 600]~mmHg, PaCO$_2$ [10, 120]~mmHg. Unlike the swept inputs, the six tracked outputs have no acceptance envelope in Pulse: the engine reports whatever its solver produces and never rejects an output value. These bounds are therefore ours, a plausibility standard applied after the run rather than a constraint the engine enforces, and each is anchored to primary critical-care and respiratory-physiology literature in Supplement~\S\,\ref{sec:s3-hard-bounds}.

\texttt{not\_steady\_state} fires when, over the final 60-second window, any tracked output flatlines, drifts beyond its per-channel clinical threshold, or varies beyond its coefficient-of-variation threshold. A flatline is variability below 1~\% of the mean \emph{and} a mean within 0.1~\% of a hard bound --- $\geq$~99.9~\% for the SpO$_2$ ceiling --- a rule written to catch a solver that has pinned an output and stopped advancing; the drift thresholds are tabulated in Supplement~\S\,\ref{sec:s3-drift}.

The four flags are independent presence counts, so a single simulation can fire several. Analyses that need one category per run resolve it by a fixed priority order, \texttt{clamped} $>$ \texttt{diverged} $>$ \texttt{implausible} $>$ \texttt{not\_steady\_state} $>$ \texttt{clean}, following the chronology of failure within a run. The [60, 120]~s window was preregistered before any sweep data was collected, and a 22-run pilot on the healthy-male cell verified five preregistered gating criteria, among them detector self-consistency and Pulse determinism.
```

### 21.x draft `met45`

```latex
The per-cell curation map (Figure~\ref{fig:traffic_light}) reduces each (scenario, sex, output) cell to one green / yellow / red verdict, built from two locked ingredients: the cell's combined diverged-plus-implausible flag rate, and its deviation from a baseline. The baseline for each output is that output's mean over the clean runs of the healthy-male (S1, M) cell, and the $10~\%$ and $30~\%$ deviation bands were preregistered before any data were collected; the full colour criteria are stated in the legend to Figure~\ref{fig:traffic_light}. Scoring every cell against a single (S1, M) baseline keeps male and female cells on one comparable scale, at the cost of folding legitimate male--female differences into the female cells' deviation term; Supplement~\S\,\ref{sec:s3-traffic} reports the re-scoring check that verifies this choice does not drive the classification.

\textbf{Post hoc deviation from the preregistered traffic-light rule.} The four-flag run-level classifier and its thresholds were preregistered, but the traffic-light aggregation was not implemented exactly as written. The preregistration stated that a cell would be red when its deviation exceeded $30~\%$ or when ``any flag'' was raised; the implemented rule treats \texttt{diverged} and \texttt{implausible} as hard flags, assigns yellow whenever their combined rate exceeds zero, and reserves red for a combined hard-flag rate above $30~\%$. The repository establishes that this implementation was committed after preregistration but not whether it was defined before or after the sweep outputs were inspected, so we record the altered yellow--red boundary as a material deviation. Under the implemented rule the map contains 7 green / 29 yellow / 12 red combinations; under the literal reading it would contain 7 green / 3 yellow / 38 red, with the same seven green and the same twelve red. We retain the implemented rule as the primary display because it preserves a graded distinction without creating a single additional green verdict, and neither the classifier, the map nor the reported counts were changed in response to this finding. The preregistered reading is reported alongside them as a sensitivity analysis in Supplement~\S\,\ref{sec:s3-tl-sensitivity}.
```

### 21.x draft `met46`

```latex
Morris $\mu^{*}$ and $\sigma$ were computed per (scenario, sex, input, output) from the SALib sample~\cite{iwanaga2022,herman2017salib}. Each elementary effect divides the change in the output by the size of the input step expressed on that input's swept range mapped to $[0,1]$, so a $\mu^{*}$ is an output change per full-range move of its input. Indices carry non-parametric 95~\% bootstrap confidence intervals from 1{,}000 trajectory-level resamples. Hypothesis~1 was evaluated per cell $\times$ output on the point-estimate top-3 fraction of summed $\mu^{*}$; hypotheses 2 and 4 are resolved in \S\ref{sec:results-overview}.

Sex differences in the steady-state distributions were measured by per-(scenario $\times$ output) Wasserstein distances between the male and female clean-run distributions, tested against a permutation null of 2{,}000 random relabellings at the two original group sizes. The resulting 24-test family was corrected by Benjamini--Hochberg control of the false-discovery rate at $q = 0.05$; with 2{,}000 relabellings the smallest non-zero empirical tail proportion is 1/2{,}000, and two tests reaching zero are reported conservatively as $p < 0.001$. Cross-sex agreement of input-importance rankings was quantified by the Spearman rank correlation between male and female $\mu^{*}$ vectors per (scenario, output).

A Sobol bolt-on was preregistered as a conditional escalation on any top-three input whose $\sigma / \mu^{*}$ ratio reaches 0.6. Applied as preregistered, the trigger fires on 72 of the 144 top-three inputs, spanning 43 of the 48 combinations, while the same preregistration fixed the bolt-on's compute envelope at 1{,}500 additional runs; because Sobol needs an independent sample per cell, even the narrowest reading of the cost formula puts 43 cells at 11{,}008 runs. The bolt-on was therefore infeasible within the budget its own protocol declared, and is reported rather than executed. Because the preregistered trigger rests on the point ratio alone, we add a post hoc sensitivity analysis in which trajectories are resampled 1{,}000 times per combination and $\sigma / \mu^{*}$ is recomputed jointly on each draw; combinations whose lower bound clears 0.6 in all five draws are characterised in \S\ref{sec:results-morris}, and the full decomposition is in Supplement~\S\,\ref{sec:s3-sobol}.

The full sampler, sweep driver, four-flag classifier, statistical-analysis pipeline and audit ledger are released open-source. The sampling design, the input ranges, the four flags and their thresholds, and the analysis plan were preregistered before data collection; the audit ledger was developed afterwards, to re-derive the computed claims in this paper from the canonical output artefacts.
```

### 21.x draft `disc`

```latex
This work delivers the first open, preregistered reliability atlas for the Pulse Physiology Engine across several adult critical-care operational scenarios. Two operator-actionable corrections and a sex-specific reliability axis emerge from the 1{,}280-run sweep: a single configuration setting that makes VC-AC tidal-volume delivery consistent and repeatable for synthetic-cohort generation, at the cost of removing the effort-dependent dyssynchrony Pulse models, so it is a data-generation tool rather than a clinical ventilation recommendation (\S\ref{sec:results-vcac}); a steady-state-window correction for hyperoxia simulation at FiO$_2 = 1.0$ (\S\ref{sec:results-hyperoxia}); and, on a separate axis, a previously uncharacterised sex-stratified solver-divergence cluster with an identified blood-volume mechanism (\S\ref{sec:results-sex}). The accompanying per-cell traffic-light curation map (Figure~\ref{fig:traffic_light}) is the principal deliverable for downstream users, and its criteria carry a material post hoc deviation from the preregistered wording at the yellow--red boundary, declared with its sensitivity analysis in \S\ref{sec:methods-traffic}. It is a curation and review-priority instrument, not a general physiological validation of the engine: credibility frameworks in biomedical modelling treat sensitivity analysis and a bounded domain of applicability as components of assessment, while validation itself requires comparison against measured data this work does not perform.

For machine-learning pipelines that train on Pulse-generated synthetic patient cohorts, the four-flag classifier doubles as a run-level data-quality contract. That contract rests on a null result bounded to the sampled envelope: within Pulse's accepted setup envelope, no submitted input was silently altered at ingestion. The preregistered rejection-log detector fired on 0 of 1{,}280 runs, and the post hoc instantiation audit found exact agreement between the value submitted and the value Pulse serialised. This concerns setup-time input handling only; it does not imply that physiological states stay fixed once the simulation runs, nor establish Pulse's behaviour outside the sampled envelope. Green cells in Figure~\ref{fig:traffic_light} are eligible for default inclusion under the stated criteria, subject to use-case-specific validation; yellow cells should be filtered to the clean subset. Green denotes eligibility under both non-degenerate readings of the rule; it does not establish physiological validity.

Three traps documented here merit explicit attention. The sex-stratified divergence cluster (\S\ref{sec:results-sex}) means that pooling male and female runs from the input-extreme regime without flag-stratified filtering ingests a spurious sex covariate. The compensatory-tachycardia decoupling (\S\ref{sec:results-secondary}) means the input heart rate and the output heart rate are not interchangeable in ARDS scenarios: a model trained on Pulse cohorts would otherwise learn a compensatory response as a steady-state feature rather than as an active response to hypoxemia. The third trap survives flag-based curation altogether, and is set out with the other two in Supplement~\S\,\ref{sec:s17-summary}.

For the computational-physiology community, the atlas matters in two ways. First, it directly addresses the Pulse maintainers' own statement that no formal sensitivity or uncertainty quantification has been performed on user-facing operational inputs~\cite{pulsefaq}: the Morris screen shows sensitivity concentrated in a few inputs, with the top-three inputs carrying at least half of the summed $\mu^{*}$ in 48 of 48 cell $\times$ output combinations (median 93~\%). Second, the method carries over to other engines. It pairs a Morris screen of the operational inputs with a four-flag classifier that sorts every run into a category instead of discarding any. To our knowledge no comparable publicly available reliability atlas has been published for either BioGears or HumMod~\cite{hester2011hummod}, and the same recipe could be applied to them by wrapping each engine's own inputs and outputs.

\textbf{Complementarity with prior external falsification work on MIMIC-III.} Cornish et al.~\cite{cornish2023} applied a causal-falsification framework to Pulse on MIMIC-III sepsis trajectories and reported 85 total Hoeffding-inequality rejections. Of these, 82 of 85 fall outside the four-channel overlap with this atlas (HR, MAP, PaO$_2$, PaCO$_2$): 80 on channels the present atlas does not assess, plus 2 on partial-overlap pressure channels; only 3 of 85 fall inside it. The two studies therefore expose different weaknesses of Pulse rather than the same one. Cornish et al.\ test its chemistry and thermoregulation outputs against a real patient cohort undergoing clinical interventions; the present atlas tests its cardio-respiratory response to operational inputs. Neither maps how operational inputs drive the electrolyte channels Cornish's test flags most often, so a metabolic-and-renal reliability atlas is the natural next step.

Beyond guidance for downstream users, the atlas also serves the engine's maintainers: it provides, to our knowledge, the first systematic characterisation of an ARDS impairment-fraction solver-instability band ($[0.879, 0.945]$), together with further engine-level observations that target tooling, documentation and validation infrastructure rather than Pulse's underlying physiology.

Six scope limits bound the conclusions; each is set out with its evidence in Supplement~\S\,\ref{sec:s2-scope}. (i)~The atlas pins to Pulse v4.3.1, results applying identically to the build-only v4.3.2. (ii)~Patient anatomy is two adult reference bodies, so mass and height variation within sex is uncharacterised. (iii)~The envelope covers adult VC-AC ventilation only; pediatric translation, pressure-targeted modes and transient within-run dynamics are out of scope by design. (iv)~The Morris estimator discards any input pair containing a flagged run, which eliminates every clean FiO$_2$ pair in the healthy and severe-ARDS female cells, so the FiO$_2$ rows of Figure~\ref{fig:morris} are left blank. (v)~The hard physiological bounds judge whether a \emph{sustained} steady-state mean is plausible, not whether a value is instantaneously attainable; they are a screening standard, not a claim that exceptional clinical trajectories are impossible. (vi)~Pulse enforces DBP/SBP $\leq$ 0.75, and configuration-time clipping shortened 9 of 20 DBP steps, so some SBP and DBP effects are not strict fixed-step Morris estimates. Two further caveats are of evidence rather than scope: no trajectory-count convergence analysis was performed, and shunt fraction was not recorded, so shunt-mediated interpretations throughout this work remain physiologically motivated rather than directly tested. Together, these limitations define the scope within which the atlas's conclusions should be interpreted.

The atlas is intended as foundational infrastructure rather than a terminal deliverable. The four-flag classifier and the per-cell traffic-light are reusable instruments that downstream users can apply to their own configurations without re-running the present sweep, and the pipeline is preregistered, reproducible and openly licensed. By characterising the adult operational envelope first, the atlas provides the methodological basis a pediatric translation layer would need, though whether these adult-model reliability patterns transfer to pediatric physiology remains an open question. A complementary metabolic-and-renal atlas would cover the electrolyte channels Cornish et al.~\cite{cornish2023} flag most often, and validating the cell-level classifications against real-world clinical databases such as MIMIC-IV would test them against recorded care. Simulated and recorded cohorts are complementary rather than interchangeable: mechanistic simulation provides controlled inputs and directly accessible model states, whereas recorded clinical data retain the messiness of real practice.

Ultimately, because Pulse-generated cohorts are already used as machine-learning training data, and because ventilation automation is already reaching the bedside --- a recent multicentre randomised trial of closed-loop ventilation improved overall ventilation quality yet showed no difference in patient-centred outcomes~\cite{sinnige2026active} --- knowing where a simulator is reliable is a precondition for using it to train the models that will inform such care.
```

### 21.x draft `supp_scope`

```latex
\subsection{Scope limits of the present atlas}\label{sec:s2-scope}

The limitations tabulated above are Pulse's, verified against its source and its own documentation. Those below are the present study's: they bound what the atlas establishes, and are summarised in the Discussion of the main manuscript.

\textbf{(i) Engine version.} The atlas pins to Pulse v4.3.1. Results apply identically to the build-only v4.3.2 release; newer physiology branches will require re-mapping.

\textbf{(ii) Patient anatomy.} Anatomy is restricted to two adult reference bodies, male and female. The atlas does not characterise body-mass or height variation within sex.

\textbf{(iii) Operational envelope.} The envelope covers adult critical-care ventilation in VC-AC mode only. Three things are out of scope by design: pediatric translation; pressure-targeted ventilator modes such as pressure-controlled and pressure-support; and transient within-run dynamics, particularly in runs that never reach a stable steady state. The mode restriction also bounds transfer to the ventilator-control application of Ward et al.~\cite{ward2024ventilator}, which drives the engine through a pressure-targeted action space: of its six ventilator settings, only FiO$_2$, respiratory rate and PEEP are inputs this atlas sweeps.

\textbf{(iv) Discarded input pairs.} The Morris elementary-effect estimator discards any input pair where either run is flagged (Section~\mainref{sec:methods-detector}{4.4} of the main manuscript). This eliminates all clean FiO$_2$ pairs in the healthy (S1) and severe-ARDS (S4\_F) cells, as every FiO$_2$ step contains at least one flagged endpoint: the high-FiO$_2$ runs in healthy lungs, driven \texttt{not\_steady\_state} or \texttt{implausible} by SpO$_2$-saturation pinning and, at FiO$_2$ = 1.0, transient hyperoxia; or the low-FiO$_2$ runs in severe-ARDS S4\_F, driven \texttt{implausible} or \texttt{not\_steady\_state} by severe hypoxemia. As a result the FiO$_2$ rows of Figure~2 of the main manuscript are left blank, and the cross-sex Spearman comparison is limited to S2 and S3 (\S\ref{sec:s6-rho}). These effects are deterministic consequences of the preregistered implausibility bound and steady-state window applied at the edges of the operational envelope, not a Pulse defect. Adding more trajectories cannot recover the discarded pairs, and re-running the whole grid with the 300-second window that resolves the hyperoxia plateau would break preregistration integrity. No trajectory-count convergence analysis was performed, so the stability of $\mu^{*}$, $\sigma$ and the full top-three ordering under a larger trajectory count is not established.

\textbf{(v) What the hard bounds judge.} The hard physiological bounds behind the \texttt{implausible} flag (\S\ref{sec:s3-hard-bounds}) judge whether a \emph{sustained steady-state mean} is biologically plausible over the evaluation window, not whether a value is instantaneously attainable; rare clinical extremes, often transient or peri-mortem, can legitimately exceed them. Rather than discarding such runs, the classifier keeps each one and records the flag it fired. The bounds are moreover treated as adjustable choices rather than fixed biological constants: the deliberately conservative PaO$_2$ ceiling was re-examined by a threshold-sensitivity analysis (\S\ref{sec:s3-pao2-sensitivity}) that recomputes the \texttt{implausible} flag under a wider, physiologically anchored limit. They therefore provide a run-level screening standard for synthetic training cohorts, not a claim that exceptional clinical trajectories are impossible.

\textbf{(vi) A non-rectangular input domain.} Pulse enforces DBP/SBP $\leq$ 0.75, which makes the sampled SBP--DBP domain non-rectangular. Configuration-time clipping shortened 9 of 20 DBP steps and caused applied DBP to co-vary in 8 of 20 SBP steps, so those effects are not strict fixed-step, one-at-a-time Morris estimates. Nevertheless, SBP remained rank 1 for MAP in all eight cells under six sensitivity estimators (\S\ref{sec:s3-clip-cost}), which isolates the clipping contribution. Shunt fraction was not recorded in the atlas, so shunt-mediated interpretations throughout this work remain physiologically motivated rather than directly tested mechanistic explanations.
```

