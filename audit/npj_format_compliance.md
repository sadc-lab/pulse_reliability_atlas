# npj Digital Medicine — form-compliance audit

**Date of the source check: 2026-07-29.** Every rule below was re-read at
source on that date; nothing here is quoted from memory. The pages were
retrieved with the Firecrawl CLI because `www.nature.com` 303-redirects a
plain fetch through `idp.nature.com` (cookie handshake), which returns no
content.

Sources, verbatim rules quoted from:

| Key | Page | URL |
|---|---|---|
| `CT` | Content types | <https://www.nature.com/npjdigitalmed/content-types> |
| `SG` | Submission guidelines | <https://www.nature.com/npjdigitalmed/for-authors-and-referees/submission-guidelines> |
| `AI` | Nature Portfolio — Artificial Intelligence policy | <https://www.nature.com/nature-portfolio/editorial-policies/ai> |

Target content type: **Article** ("Articles should report substantial original
primary research", `CT`).

Artefacts measured: `preprint_npj/paper.tex`, `preprint_npj/supplement.tex`,
and the built `preprint_npj/build/paper.pdf` (31 pages) and
`build/supplement.pdf` (45 pages), at commit `5675f52`.

---

## Verdict at a glance

**20 requirements met. 3 genuine non-conformities. 6 items needing an author
decision or an external artefact. 1 mechanical fix, applied.**

The single material finding is **N-1**: npj states twice, in two separate
documents, that Supplementary Methods are not permitted, and our supplement
carries a 3,804-word section titled *Full Methods detail*.

> **Update 2026-08-02.** N-1 is resolved; see its entry below. The counts in
> this paragraph are those of the original audit at `5675f52` and are left as
> written, because this is a dated record of what was found.

---

## N — Non-conformities and risks

### 🟢 N-1 — Supplementary Methods are not permitted. §S3 was one. **Resolved 2026-08-02.**

> **Resolution.** Commits `72171e3` (main text), `29b8546` (a defect found on
> the way) and `23c0d7b` (supplement). The measurement that drove it, and the
> two revisions it forced on the original plan, are in
> `audit/n1_methods_restructure.md`.
>
> The premise of the obvious remedy was false: measured block by block, §4
> already carried most of §S3's science, several passages near-verbatim.
> Moving those blocks would have duplicated the main text rather than complied
> with anything. Four items were genuinely method living only in the SI, and
> those moved: the six drift thresholds, the flatline constants, the four
> clamp regular expressions, and the engine-wrapper description. A fifth
> addition was not required by the rule — §4 never described how the
> traffic-light map is built, so `sec:methods-traffic` was added.
>
> §S3 is now *Parameter provenance and supplementary analyses*: 3,818 → 3,497
> words, and neither its title nor its opening sentence announces Methods any
> longer. §4 is 2,547 → 2,968 words in 7 subsections. Every bare
> `\ref{sec:s3}` is repointed; the count is 0 in both documents.
>
> One consequence recorded rather than hidden: deleting `tab:hard-bounds` as a
> duplicate of §4.4's inline list retires six crosswalk entries that guarded
> its row literals. The crosswalk falls **98 → 92**. Each bound keeps two
> independent numeric guards and the 289-anchor layer is untouched, and the
> six were deliberately not replaced by anchor-name literals that would have
> preserved the count while guarding no number.
>
> **§S12 *Reproducibility recipe* is deliberately untouched** — see
> `audit/n1_methods_restructure.md` §10 for why.

The finding as originally recorded follows.


npj says it twice, in two different places, in near-identical words:

> "All descriptions of Methods should be provided in the main manuscript file
> and not in the Supplementary Information" — `CT`, Article table, *Methods* row.

> "The journal does not permit Supplementary Methods, all Methods should be
> reported in the main manuscript file." — `SG`, *Supplementary information*.

Our state, measured:

| | Words | Subsections |
|---|---:|---:|
| `paper.tex` §4 Methods | 2,512 | 6 |
| `supplement.tex` §S3 **Full Methods detail** | **3,804** | **10** |

§S3's own opening sentence makes the dependency explicit: *"This section
expands the condensed Methods section of the main manuscript (Section 4 of the
main manuscript) with the engine-wrapper architecture, the deterministic Docker
recipe, the complete physiological-bounds and drift-threshold tables …"*.

The ten subsections: engine wrapper / Docker pinning; Morris sampler
implementation; cost of the pulse-pressure clip; Sobol bolt-on decision;
four-flag classifier priority order; hard physiological bounds; drift
thresholds; clamp regex set; traffic-light cell-scoring rule; body-dimension
provenance.

Not every one of these is *method* in npj's sense — several are provenance
tables and rationale registers, which sit naturally in Supplementary
Information. But the section title, and the sentence above, both announce it as
Methods. **Author decision required.** Nothing modified.

### 🟠 N-2 — Abstract: 150 words, or 153, depending on the convention.

> "No subheadings permitted and up to 150 words in length" — `CT`.

Subheadings: **none** ✓.

Length: the count depends on whether three standalone symbols are words.

| Convention | Count | Verdict |
|---|---:|---|
| Tokens containing a letter or digit | **150** | at the limit, exactly |
| All whitespace-delimited tokens (what a word processor reports) | **153** | 3 over |

The three extra tokens are the two `%` in `93~\%` / `20.6~\%` and the `=` in
`FiO$_2$~=~1.0`. The `~` renders as a space, so a word processor sees
`93` `%` as two words. Writing `93\%` would render `93%` and remove the gap —
but that would break the typographic convention the rest of the paper uses.

Measured twice, from two directions: from the rendered PDF (152 tokens, of
which one was a stray page-number artefact and one an en-dash line-break split)
and from the LaTeX source with an audited macro expansion (`\{,\}`→`,`,
`$-2$`→`−2`, `X$_n$`→`Xn`, `~`→space, `--`→en dash, `\%`→`%`; leftover LaTeX
tokens after expansion: none). Both land on the same reading text.

**Author decision.** Nothing modified.

### 🟠 N-3 — The funder's role is not declared.

> "The role of the funding body in the design of the study and collection,
> analysis, and interpretation of data and in writing the manuscript should
> also be declared. If the funder has played no role in the research, this
> should be stated." — `SG`, *Acknowledgements*.

npj gives the exact sentence it expects:

> "This study was funded by \[funder name\] \[grant number where applicable\].
> The funder played no role in study design, data collection, analysis and
> interpretation of data, or the writing of this manuscript."

`paper.tex:372` names four funding sources (ANR France 2030 / ENACT AI Cluster
ANR-23-IACL-0004; Région Grand Est; CHU Sainte-Justine Foundation; R-SADC) and
declares no role for any of them. Grant number present ✓, no separate Funding
section ✓ (`CT` forbids one).

**This is a factual statement about the funding relationship, not a wording
choice.** It cannot be written without the author asserting it. Nothing
modified.

### 🟡 N-4 — Six web-page references sit in the numbered reference list.

> "URLs for web sites should be cited parenthetically in the text, not in the
> reference list; articles in formal, peer-reviewed online journals should be
> included in the reference list." — `SG`, *References*.

Rendered entries [6]–[10] and one more are Kitware Pulse documentation pages:
`pulsefaq`, `pulsecircuit`, `pulsesystem`, `pulsepatientmethod`,
`pulserespmethod`, and `pulseabout` / `pulsevent` where cited.

Against that rule, `SG` also gives an *Online material* example format and
accepts blog posts and figshare datasets in the reference list. The two
statements are not reconcilable from the page alone.

Verified while checking this: **the URLs render correctly.** A PyMuPDF text
extraction returns `pulse.kitware.com/ f a q.html`, which looks like broken
underscores; the page image and the PDF link annotations both carry
`https://pulse.kitware.com/_f_a_q.html` intact. Extraction artefact, not a
defect.

**Author decision** — these are load-bearing citations for the verified-
limitations table, so moving them to parenthetical in-text URLs is not free.

### 🟢 N-5 — Multi-panel legends do not describe each panel individually. **Fixed in `91d705d`.**

> The Figure 2 legend now reads *"The panels are Morris $\mu^{*}$ heatmaps, one
> per steady-state output: **(a)** HR, **(b)** MAP, **(c)** Vt delivered,
> **(d)** SpO$_2$, **(e)** PaO$_2$, **(f)** PaCO$_2$."* Verified in
> `paper.tex` on 2026-08-02. The finding as originally recorded follows.


> "Multi-panel figures should be presented on a single page and labeled using
> an a), b), c) convention and each panel should be described in the legend
> individually." — `SG`, *Figure legends*.

Figure 2 (Morris) has six panels, labelled (a)–(f) in the render ✓, on one page
✓. Its legend describes them collectively — *"The panels are Morris μ\*
heatmaps, one per steady-state output"* — and never says *a) HR, b) MAP …*.
Same shape for the other multi-panel figures.

Low risk (a copy-editor request at proof, at worst), but it is a stated rule.

### 🟡 N-6 — Two supplement floats overflow their page.

`scripts/check_render.py` reports, unchanged to five decimal places from the
2026-07-29 baseline:

```
paper       overfull box, 11.89064pt too wide
supplement  overfull box, 19.30798pt too wide
supplement  float too large for page by 31.26459pt
supplement  float too large for page by 53.88974pt
```

Pre-existing and long-tracked, not introduced here. It intersects the npj rule
only insofar as a float that does not fit its page cannot be "presented on a
single page". Recorded, not acted on.

> **Measured in the rendered PDFs, 2026-08-02 — none of the four manifests.**
> The warnings had never been checked against the pages they describe.
>
> The two floats are `tab:limits` (§S2, twelve limitation rows) and
> `tab:s16-index` (§S17). Both render **complete**: the last row of each is
> present in the extracted text.
>
> | | measured | normal text block | margin left |
> |---|---|---|---|
> | `tab:limits`, vertical | 654.9 pt | 654.9 pt — **+0.0** | 187.0 pt |
> | `tab:s16-index`, vertical | 663.4 pt | +8.6 pt | 178.5 pt |
> | Table 1 (paper), horizontal | 495.3 pt | +6.4 pt | 100.0 pt |
> | `tab:limits`, horizontal | 489.9 pt | +19.2 pt | 105.3 pt |
>
> Normals are the median text-block edge over every page of each document. The
> largest real excursion is 19.2 pt into a 124 pt margin. And the supplement's
> **widest page is 28, at +24.5 pt, which LaTeX does not flag at all** — so the
> warnings do not even rank the pages by how far their content actually
> reaches.
>
> The gap between "31.26 pt too large" and 0 pt of visible spill is normal:
> LaTeX measures the float box against `\textheight` when it tries to place it,
> caption and float glue included, and a dedicated float page then absorbs
> most of that.
>
> **Consequence: N-6 is a build-log tidiness item, not a render defect.**
> Converting the two tables to `longtable` would silence it and would change
> how two tables paginate. Not worth it before submission, and this note exists
> so the trade is made on the measurement.
>
> *This corrects a recommendation made the same day that N-6 was "the only real
> render defect" and "the best effort-to-result ratio". It was the least
> verified thing on that list.*

### 🟢 N-7 — Stale internal header. **Fixed.**

`supplement.tex:11` declared `Status: Complete supplement, sections S1-S16.`
The file carries **17** `\section` commands, through `\label{sec:s17-summary}`.
Mechanical, provably drifted from its own artefact, alters no claim — corrected
under the autonomy pact.

---

## E — External artefacts still to produce (not manuscript defects)

| | Requirement | Source | State |
|---|---|---|---|
| E-1 | **Nature Portfolio Reporting Summary** — "You will be asked to complete and submit [it] together with the revised version of your manuscript after peer-review… Authors are encouraged to include both completed forms at the time of submission." | `SG` | not in the repo |
| E-2 | **Editorial Policy Checklist** — "must be received by the Editors before the paper can be sent for peer-review" | `SG` | not in the repo |
| E-3 | **Cover letter** — mandatory; "please avoid repeating information that is already present in the abstract and introduction" | `CT`, `SG` | `cover_letter.md` exists, has placeholders |
| E-4 | **ORCID for the corresponding author** — "it is not possible to add/modify ORCID details at proof stage" | `SG` | tracked in `TODO_publication_roadmap.md` |

---

## C — Requirements met

Each row states the rule as npj words it, then what was measured.

| # | Rule (source) | Our state | ✓ |
|---|---|---|---|
| C-1 | Title "up to 15 words in length and free of punctuation, idioms, and puns" (`CT`) | 14 words, zero punctuation characters: *An Open Reliability Atlas of Sensitivity and Failure Modes in the Pulse Physiology Engine* | ✓ |
| C-2 | Abstract "No subheadings permitted" (`CT`) | no sectioning macro inside `\abstract{}` | ✓ |
| C-3 | Introduction "No subheadings permitted" (`CT`) | single `\section`, no `\subsection` | ✓ |
| C-4 | Results "Subheadings should be used" (`CT`) | 6 subsections | ✓ |
| C-5 | Discussion "No subheadings, limitations, or conclusions sections are permitted" (`CT`) | 0 heading macros in the 1,584-word Discussion; the words *limitation* and *conclusion* each appear once, in prose, never as a heading | ✓ |
| C-6 | Methods "Subheadings should be used… subdivided by short bold headings" (`CT`, `SG`) | 6 subsections at `5675f52`; **7 since the N-1 restructuring** (`sec:methods-traffic` added) | ✓ |
| C-7 | Section order with Methods last (`CT` table order) | Title → Abstract → Intro → Results → Discussion → Methods → back matter | ✓ |
| C-8 | Data availability "Mandatory"; "provided as a separate section after the Methods section before the References" (`CT`, `SG`) | `\bmhead{Data availability}` at `paper.tex:362`, after Methods, before `\bibliography` | ✓ |
| C-9 | Code availability "Where applicable" (`CT`) | `paper.tex:366`, Apache-2.0 repository URL, reproducibility recipe pointer | ✓ |
| C-10 | Acknowledgements: funding declared here, "a separate Funding statement is not permitted" (`CT`) | funding in Acknowledgements; no Funding section anywhere | ✓ |
| C-11 | Author contributions "Mandatory, the statement should refer to all authors individually, denoted by their initials" (`CT`, `SG`) | all seven contributors by initials (S.N., M.S., Y.M., A.W., C.S., P.J.) | ✓ |
| C-12 | Competing interests "Mandatory… If there are no competing interests to declare, this should be stated" (`CT`) | "The authors declare no competing interests, financial or otherwise." | ✓ |
| C-13 | References "Limited to 60 references, though not strictly enforced" (`CT`) | **33** rendered entries in `paper.pdf`; 25 in the supplement | ✓ |
| C-14 | "Figure legends — Limited to 350 words per figure" (`CT`); "this guidance also applies to any supplementary figures" (`SG`) | 15 figure legends measured; **maximum 319 words** (Figure 1, the traffic-light map). Counted from LaTeX source, which over-counts inline math, so the rendered counts are lower still | ✓ |
| C-15 | "multi-panel figures should be presented on a single page with each panel labeled using an a), b), c) convention" (`CT`) | panel labels (a)–(f) present in the render | ✓ |
| C-16 | "Figure lettering should be in a clear, sans-serif typeface… the same typeface in the same font size… for all figures" (`SG`) | enforced in the generators; commits `bf85cd8` and `b3caa1c` | ✓ |
| C-17 | "Thousands should be separated by commas (1,000)" (`SG`) | `1{,}280`, `4{,}082`, `11{,}008` throughout | ✓ |
| C-18 | Statistics: "Use of the word 'significant' should always be accompanied by a P value; otherwise, use 'substantial,' 'considerable,' etc." (`SG`) | **one** occurrence of the stem in the whole corpus — `supplement.tex:506`, *"reverse-percentile bootstrap rejections at the same significance level"*, a technical term describing Cornish's test, not a claim about our data. Zero occurrences in `paper.tex` | ✓ |
| C-19 | Statistics: multiple comparisons — "authors should explain how they adjusted the alpha level to avoid an inflated Type I error rate" (`SG`) | Benjamini–Hochberg FDR, described in Methods §4.5 at `5675f52`, **§4.6 since the N-1 restructuring** | ✓ |
| C-20 | AI: "Use of an LLM should be properly documented in the Methods section"; LLMs "do not currently satisfy our authorship criteria" (`AI`) | Methods §4.6 *Use of AI tools* (**§4.7 since the N-1 restructuring**) names every model and phase; no LLM in the author list; Author contributions restates the scope | ✓ |
| C-21 | AI images: "Springer Nature journals are unable to permit its use for publication" (`AI`) | every figure is generated by a versioned script in `scripts/` from atlas data; no generative-AI imagery | ✓ |
| C-22 | Supplementary Information "combined and supplied as a single, separate file, preferably in PDF format" (`CT`) | one `supplement.pdf` | ✓ |

### Colour accessibility — checked, and defensible

> "we ask authors to recolor green-and-red heatmaps, graphs and schematics
> **for which colours are chosen arbitrarily**" — `SG` (emphasis added).

Figure 1 is a red / amber / green traffic-light map. The colours are not
arbitrary — they *are* the finding, and the metaphor is named in the figure
title. Every cell additionally carries a numeric annotation, so colour is never
the sole channel: *"Each cell is annotated with the clean-run mean of that
output … the cell colour is the separate reliability verdict."* Recorded here
so the choice is on the record if a reviewer raises it.

### Formatting that only binds at acceptance

`SG`, *Format of manuscripts*: **"Manuscripts submitted to npj Digital Medicine
do not need to adhere to our formatting requirements at the point of initial
submission; formatting requirements only apply at the time of acceptance."**

So these are noted and deliberately not acted on now: tables at the end of the
document; figure legends placed after the references; figures uploaded as
individual files at ≥300 dpi; lower-case **bold** panel letters rather than
LaTeX's `(a)`; LaTeX source accepted only at acceptance stage (compiled PDF
before that).

### Back-matter sections npj does not ask for

`paper.tex` additionally carries *Ethics approval and consent to participate*,
*Consent for publication*, and *Materials availability*, each answered "Not
applicable". These are BMC-style headings, absent from npj's Article table.
They are not forbidden and they answer questions the Editorial Policy Checklist
asks anyway. Left in place; recorded so the decision is visible.

---

## Method note

Word counts were produced by three scripts, kept in the session scratchpad:
`npj_compliance_measure.py` (source-side: title, abstract, all 33 captions,
Discussion headings, `significant` sweep), `npj_abstract_count2.py` (audited
macro expansion of the abstract, both counting conventions),
`npj_render_probe.py` and `npj_section_sizes.py` (rendered PDF: reference
count, panel labels, link annotations; per-section word counts).

Caption counts are taken from the LaTeX source with `\cite`/`\label`/`\ref`
dropped and inline math collapsed to one token. That over-counts constructs
like `SpO$_2$`, so the true rendered legend lengths are **shorter** than the
numbers in C-14 — the margin against the 350-word cap is larger than reported,
never smaller.
