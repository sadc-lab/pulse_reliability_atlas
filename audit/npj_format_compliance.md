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
and the built `preprint_npj/build/paper.pdf` and `build/supplement.pdf`.

Rendered page counts are **descriptive only, never a compliance threshold**, and
they move with every content revision: 31 and 45 pages at commit `5675f52`, 35 and
49 pages at commit `87ec439`. No npj page-count limit is recorded anywhere in this
register: the extent limits it does carry are word counts (title 15, abstract 150,
figure legends 350) and a cap of 60 references. Do not read a page figure here as
an invariant.

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

### 🟢 N-2 — Abstract: **146 words, or 149** since 2026-08-17 (was 145 / 148, and 147 / 150 before that). **Compliant under both readings.** First resolved 2026-08-03, superseded 2026-08-16, superseded again 2026-08-17.

> "No subheadings permitted and up to 150 words in length" — `CT`.

Subheadings: **none** ✓.

Length: the count depends on whether three standalone symbols are words.

| Convention | Count | Verdict |
|---|---:|---|
| Tokens containing a letter or digit | **147** | 3 under the limit |
| All whitespace-delimited tokens (what a word processor reports) | **150** | exactly at the limit |

> ### ❌ Correction, 2026-08-03 — this finding previously recorded 150 / 153, and that was wrong
>
> Commit `3fc08ad`, titled *"Correct the abstract word count: it is 150/153, not
> the 147/150 previously reported"*, **replaced a correct figure with an
> incorrect one**. The 147 / 150 reported on 2026-08-01 was right all along.
>
> **Cause: three PDF-extraction artefacts were counted as words.** The abstract
> straddles the page-1/page-2 break in this template, and PyMuPDF returns:
>
> | artefact | what the extraction contains | what it actually is |
> |---|---|---|
> | page number | `…643 mmHg.` `\n` **`1`** `\n` `Solver…` | the page-1 folio, not a word |
> | line-break split | `patient–` `\n` `ventilator` | **one** word, `patient--ventilator` |
> | line-break split | `blood-` `\n` `volume` | **one** word, `blood-volume` |
>
> 153 raw − 3 = **150** whitespace tokens; minus the three non-alphanumeric
> tokens (`%`, `%`, `=`) = **147** strict. Note that the ORIGINAL 2026-07-29
> measurement, recorded above, already named two of these three artefacts and
> subtracted them; the 2026-08-02 re-measurement stopped subtracting.
>
> **Both instruments now agree exactly**, which the 2026-08-02 pass never
> achieved: rendered `build/paper.pdf` with the three artefacts removed →
> 147 / 150; LaTeX source macro-expanded, zero leftover LaTeX tokens →
> 147 / 150.
>
> **Status: compliant under both conventions.** 147 is three under npj's cap;
> 150 is exactly at *"up to 150 words"*. There is no non-conformity here and
> nothing needs to be cut. The author decided on 2026-08-03 to change nothing:
> the abstract keeps its content, and the only cost is zero margin under the
> word-processor reading, so any future addition must be paid for by a removal.
>
> **Method lesson.** A word count taken from a rendered PDF is not a word count
> until page furniture and hyphenation splits are removed, and the check that
> catches it is instrument agreement: two methods that disagree by exactly 3
> are reporting an artefact, not a measurement.

> ### 🔄 2026-08-16 — the 2026-08-03 decision is superseded, not erased
>
> **Chronology, both entries true of their date:**
>
> - **2026-08-03** — abstract left unchanged at **150 / 147**, compliant under
>   both conventions, zero margin under the word-processor reading.
> - **2026-08-16** — superseded by two grammatical compound-modifier
>   hyphenations; the abstract now counts **148 / 145** under the same
>   conventions, restoring a margin of 2.
>
> **What changed, and only that:** `adult physiology simulator` →
> `adult-physiology simulator`, and `synthetic cohort construction` →
> `synthetic-cohort construction`. Both are compound modifiers preceding their
> head noun, where hyphenation is the standard form; the head noun stays outside
> the compound, exactly as the abstract already writes
> *"an **Apache-2.0-licensed** curation layer"*. No scientific content changed,
> and no claim was touched.
>
> This is a correction of typography before it is a saving of words. Both open
> forms were ambiguous: *adult physiology simulator* also parses as an adult
> simulator of physiology, and *synthetic cohort construction* as synthetic
> construction of cohorts. The hyphen removes each reading. The abstract already
> carried 16 hyphenated compounds, so these two were the outliers.
>
> **Rejected in the same pass:** `formal sensitivity analysis` →
> `formal-sensitivity-analysis`. Here `analysis` IS the head noun, with no
> following noun to modify, so the open form is the correct one. The paper's own
> usage settles it: `sensitivity-analysis` appears hyphenated 5 times and every
> one precedes a head noun (*recipe*, *reclassification* ×2, *pattern*,
> *wrappers*), while the open form is used wherever `analysis` is itself the
> head. Hyphenating it in the abstract would have been the single violation of a
> rule the manuscript otherwise applies consistently — and would have read as
> word-count gaming.
>
> **Verified with the instrument that produced the 150.** It first reproduced
> the registered baseline on the committed file (150 / 147); the working tree
> then measured 148 / 145; and reverting *only* those two hyphens restored the
> committed abstract **byte-for-byte** and the count to 150 — so no other edit
> is hiding inside the difference. `git diff --numstat` on `paper.tex`: one line.
>
> ⚠️ **Scope of the claim.** 148 is the count **under this repository's counting
> convention** (whitespace-delimited tokens, hyphenated compounds counting as
> one — the reading the 150 was measured under). npj's own counting method has
> not been verified at source. The margin is real relative to the convention
> this register has used throughout; it is not a statement about what the
> submission portal will report.

> ### 🔄 2026-08-17 — superseded again: **149 / 146**, and the illustrative
> quotation above no longer exists in the abstract
>
> The abstract's closing clause changed from *"an **Apache-2.0-licensed**
> curation layer"* to *"an **openly licensed** curation layer"*, costing one
> word: **149 / 146** under the same two conventions, one under the cap.
>
> **Why, and it is not a typographic matter this time.** The clause attached a
> *software* licence to the artefact the paper's own Data availability statement
> describes as a machine-readable CSV/JSON map — a data artefact, and one the
> same statement licenses CC-BY-4.0 in the Zenodo deposit. An enumeration of all
> 9 `Apache` occurrences in `paper.tex` + `supplement.tex` found this to be the
> **only** locus in the submission sources where Apache-2.0 qualified a data
> artefact; the other 8 refer to Pulse itself, to the pipeline, or to the two
> statements that carry the split correctly. `openly licensed` is true under
> both regimes and defers the exact terms to Data/Code availability, which now
> state a four-class policy (code + lab-notebook entries Apache-2.0; deposited
> data + the authors' own monograph content CC-BY-4.0; third-party excerpts
> unchanged).
>
> **What this invalidates in the entry above.** The 2026-08-16 block cites
> *"an Apache-2.0-licensed curation layer"* as the worked example of a compound
> modifier keeping its head noun outside the compound. The example is gone; the
> rule it illustrated is not, and `synthetic-cohort construction` still
> demonstrates it. The counts `148 / 145` there are superseded by `149 / 146`.
>
> The margin is now 1 word, deliberately. A search for a free word to reclaim it
> found none: every remaining candidate carries a bound, a denominator or a
> substantive qualification (`actively maintained`, `entirely`, `transient`,
> `severity`, `of total sensitivity`, `review-priority`). Buying margin would
> have cost a claim. Measured by `scripts/audit_claims.py` (abstract extent
> guard), which fails only above 150.

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

> **⚠️ SUPERSEDED 2026-08-03 — the block below is the erroneous re-measurement.**
> Kept verbatim as a dated record of how the error was reasoned, per the
> verify-then-remove principle. Its numbers are wrong; see the correction above.
>
> **Re-measured 2026-08-02 at `ddddc06`, and the abstract is still at the cap.**
>
> The abstract was edited on 2026-08-01 (`91d705d`) to remove a mis-attributed
> ceiling, and that session reported the result as **147 / 150**. That figure is
> **not reproducible** and should not be relied on. *(This sentence is the
> error: 147 / 150 was correct, and is reproducible with the artefacts removed.)*
>
> Two instruments, run today:
>
> | instrument | letter-or-digit tokens | all whitespace tokens |
> |---|---:|---:|
> | rendered `build/paper.pdf`, extraction bounded from *"Pulse is an actively maintained"* to *"…training cohorts."* | **150** | **153** |
> | LaTeX source, macro-expanded | **150** | 156 |
>
> The two agree on **150** under the strict reading. The rendered PDF's three
> non-alphanumeric tokens are `%`, `%`, `=` — the same three this finding names
> above, so the structure is unchanged from the original measurement.
>
> **Status: 150 is exactly at npj's cap** (*"up to 150 words"* — compliant, zero
> margin) **and 153 is three over** under the word-processor reading an editor
> is likely to apply.
>
> A third attempt, reimplementing this finding's own macro-expansion recipe,
> **failed its calibration**: it returned 153 / 159 on `5675f52` where this
> table records 150 / 153. It is therefore not reproducing the original
> convention and its numbers are discarded rather than reported. The original
> counting script lived in a session scratchpad and no longer exists, so the
> 2026-07-29 numbers cannot be re-derived; only the current state can be, and
> the two instruments above are what it rests on.
>
> **Author decision, reopened.** The abstract has zero margin. Any future edit
> that adds a word puts it over on both readings.

### 🟢 N-3 — The funder's role is not declared. **Fixed in `91d705d` (2026-08-02).**

> **Resolution, recorded 2026-09-13.** `paper.tex:412` now ends the
> acknowledgements with *"The funders played no role in study design, data
> collection, analysis and interpretation of data, or the writing of this
> manuscript."* This is npj's sentence, verbatim except for the plural. It was
> added in `91d705d`, whose message records that the author confirmed the
> institutions held no review right. It sits after all four funders.
>
> One later change. `bc34f0b` (2026-09-07) thanks the BIOSE Doctoral School of
> the Université de Lorraine "for its support", placed between the Région
> Grand Est and CHU Sainte-Justine sentences, so still before the no-role
> sentence. The text does not call BIOSE a funder. The author's confirmation
> predates this addition, so the question was put to the author on
> 2026-09-13. **Answer: BIOSE gave support, not funding.** Nothing to change.
>
> The finding as originally recorded on 2026-07-29 follows. Its line
> reference `paper.tex:372` is stale.

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

### 🟡 N-4 — Web-page references sit in the numbered reference list. **Author decision 2026-09-13: kept as numbered entries.**

> **Decision, 2026-09-13.** The author chose to change nothing, from three
> options put to them on the facts below:
>
> - **A (chosen):** keep all 3 + 8 numbered entries;
> - **B:** paper only, 5 cite sites to parenthetical URLs;
> - **C:** paper and supplement, 20 sites.
>
> The rule stays breached as written. The risk accepted is an editor's request,
> at the technical check or at proof, to move them. If that request comes, the
> work is the 20 cite sites counted below. Re-grep them first, because line
> numbers move. The yellow status marks a known
> departure kept on purpose, not an open question.
>
> **Update 2026-09-13.** The count "six" and the key list below are stale.
>
> **The rule was re-read at source today** (`SG`, scraped 2026-09-13, page
> identity checked). Its wording is unchanged. The sentence just before it is
> stricter: *"Only papers that have been published or accepted by a named
> publication or recognized preprint server should be in the numbered list."*
> The *Online material* example format (a blog post, a figshare dataset) is
> also unchanged.
>
> **Current state**, from the built `.bbl` files and counted by `\bibitem`:
>
> - **Paper:** 3 of 22 entries are web pages. They are `pulsefaq` (the FAQ
>   statement that motivates the paper, cited at `paper.tex:144` and `:325`),
>   `pulseinaction` (`:140`, `:321`) and `pulserespmethod` (`:341`).
> - **Supplement:** 8 of 32 entries are web pages, cited at 15 sites. The
>   sites per key are `pulseabout` 2, `pulsecardiomethod` 1, `pulsecircuit` 1,
>   `pulsefaq` 2, `pulsepatientmethod` 2, `pulserespmethod` 3, `pulsesystem` 2,
>   `pulsevent` 2.
> - **Positive control:** "Accessed" occurs 3 and 8 times in the two `.bbl`
>   files, one per web entry.
>
> No script depends on these cite keys. `scripts/audit_claims.py` carries the
> Kitware URLs only inside provenance strings.
>
> **Supplementary Information.** `SG` says nothing about references cited in
> the SI. It does say that SI *"is not edited, typeset or proofed"* and that
> *"The journal does not edit Supplementary Information files"*. Whether the
> reference rule is meant to apply there is not stated.
>
> **The journal's own practice was measured.**
>
> - **Sample.** The first 40 hits, in default order, for the Europe PMC query
>   `JOURNAL:"NPJ Digit Med" AND PUB_YEAR:2026 AND OPEN_ACCESS:y AND
>   PUB_TYPE:"research-article"` (480 hits in total), retrieved 2026-09-13.
>   This is a convenience sample, not a random one.
> - **Unit.** One numbered reference entry (a JATS `<ref>`). There are 2,371
>   across the 40 articles, and the parsed row count matches the tag count.
>   The JATS heading gives the content type "Article" for 20 papers and is
>   absent for the other 20.
> - **Result.** An entry whose citation string has an `http(s)://` or `www.`
>   URL other than `doi.org` occurs 161 times, in 23 of the 40 articles. Among
>   the 20 confirmed Articles, 8 carry such an entry once arXiv links are
>   excluded:
>   - 4 carry plain web pages: PMC13282478 (FDA web pages, formatted *"Accessed
>     May 6, 2025"*), PMC13332067 (model cards on llama.com and Hugging
>     Face), PMC13338390 (a GitHub repository and two blog posts), and
>     PMC13493897 (OpenAI blog posts, and web pages of a charity, WHO and the
>     FDA);
>   - the other 4 are an OpenReview, a ResearchGate or a workshop link, and a
>     clinical guideline.
> - **Checked on nature.com**, not only on the mirror. Article
>   `10.1038/s41746-026-02692-5` is labelled "Article", published 17 June 2026,
>   and its reference 1 reads *"US Food and Drug Administration. FDA Launches
>   the Digital Health Center of Excellence. FDA. September 22, 2020. Accessed
>   May 6, 2025."* with the URL.
>
> **What this does and does not show.** Web-page references do reach print in
> npj Digital Medicine Articles, in our own format. It does not show whether
> editors asked other authors to remove theirs, or whether the technical check
> at submission looks for them. That part is not known.
>
> The finding as originally recorded on 2026-07-29 follows.

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
| E-1 | **Nature Portfolio Reporting Summary** — "You will be asked to complete and submit [it] together with the revised version of your manuscript after peer-review… Authors are encouraged to include both completed forms at the time of submission." | `SG` | **draft prepared 2026-08-02**: `preprint_npj/reporting_summary_draft.md`, built against the official flat form. The deliverable remains Nature's interactive PDF. |
| E-2 | **Editorial Policy Checklist** — "must be received by the Editors before the paper can be sent for peer-review" | `SG` | 🟢 **RETIRED BY THE PUBLISHER — no action possible or needed.** See below. |

### E-2 no longer exists, and npj's own page has not caught up

Checked at source 2026-08-02. The URL npj links to for this form,
<https://www.nature.com/documents/nr-editorial-policy-checklist.pdf>, returns a
one-page PDF whose entire content (217 characters, verified in full) is:

> "This form is no longer required for Nature Portfolio submissions and has
> been removed.
>
> Please review all current Nature Portfolio policy details here:
> https://www.nature.com/nature-portfolio/editorial-policies"

The retirement stub is dated **2026-01-23**. Corroboration: the current
Nature Portfolio *reporting standards* page lists six Reporting Summary
variants and does not mention an Editorial Policy Checklist anywhere.

So the npj submission-guidelines page still carries three sentences demanding a
form its own publisher withdrew — including *"must be received by the Editors
before the paper can be sent for peer-review"*, which this register had
recorded as the single hard gate on submission. **It is not a gate. There is
nothing to submit.**

Note the direction of the staleness: the Reporting Summary PDF still dates from
2023-08-02 and its own preamble still refers readers to "the Editorial Policy
Checklist". The retired form is referenced by both the journal page and the
live form; only the artefact itself records that it is gone. Recorded so this
is not re-derived, and re-checked before submission in case npj updates its
page.
| E-3 | **Cover letter** — mandatory; "please avoid repeating information that is already present in the abstract and introduction" | `CT`, `SG` | `cover_letter.md` exists, has placeholders |
| E-4 | **ORCID for the corresponding author** — "it is not possible to add/modify ORCID details at proof stage" | `SG` | tracked in `TODO_publication_roadmap.md`. **Re-read at source 2026-08-02, see below.** |

### E-4, restated after re-reading the source

Two things this register implied, and that a status report on 2026-08-02
repeated, are wrong:

- **ORCID does not go in the manuscript file.** `SG` describes linking it to
  the Springer Nature account inside the submission portal ("Modify My Springer
  Nature Account" → "Personal Profile" → "Create/link an Open Researcher
  Contributor ID"). Reporting that `paper.tex` contains zero occurrences of
  "ORCID" was therefore a meaningless measurement: it never belongs there.
- **It is not an initial-submission blocker.** The requirement binds "all
  corresponding authors of **accepted** papers" and must be satisfied "before
  submitting the final version of the manuscript". Non-corresponding authors
  are encouraged, not required.

The proof-stage sentence quoted above is accurate and is the real constraint:
the link must exist before acceptance, because it cannot be added afterwards.
That makes E-4 a few minutes of portal work with a deadline at acceptance, not
a gate on submission.

---

## C — Requirements met

Each row states the rule as npj words it, then what was measured.

| # | Rule (source) | Our state | ✓ |
|---|---|---|---|
| C-1 | Title "up to 15 words in length and free of punctuation, idioms, and puns" (`CT`) | 14 words, zero punctuation characters: *An Open Reliability Atlas of Sensitivity and Failure Modes in the Pulse Physiology Engine* | ✓ |
| C-2 | Abstract "No subheadings permitted" (`CT`) | no sectioning macro inside `\abstract{}` | ✓ |
| C-3 | Introduction "No subheadings permitted" (`CT`) | single `\section`, no `\subsection` | ✓ |
| C-4 | Results "Subheadings should be used" (`CT`) | 6 subsections | ✓ |
| C-5 | Discussion "No subheadings, limitations, or conclusions sections are permitted" (`CT`) | **0** heading macros in the **1,602**-word Discussion; the words *limitation* and *conclusion* each appear once, in prose, never as a heading. Re-measured 2026-08-03; was 1,584, the drift is the abbreviation expansion of `ddddc06`. The load-bearing measurements — 0 headings, 1 + 1 in prose — are unchanged. | ✓ |
| C-6 | Methods "Subheadings should be used… subdivided by short bold headings" (`CT`, `SG`) | 6 subsections at `5675f52`; **7 since the N-1 restructuring** (`sec:methods-traffic` added) | ✓ |
| C-7 | Section order with Methods last (`CT` table order) | Title → Abstract → Intro → Results → Discussion → Methods → back matter | ✓ |
| C-8 | Data availability "Mandatory"; "provided as a separate section after the Methods section before the References" (`CT`, `SG`) | `\bmhead{Data availability}` at `paper.tex:362`, after Methods, before `\bibliography` | ✓ |
| C-9 | Code availability "Where applicable" (`CT`) | `paper.tex:366`, Apache-2.0 repository URL, reproducibility recipe pointer | ✓ |
| C-10 | Acknowledgements: funding declared here, "a separate Funding statement is not permitted" (`CT`) | funding in Acknowledgements; no Funding section anywhere | ✓ |
| C-11 | Author contributions "Mandatory, the statement should refer to all authors individually, denoted by their initials" (`CT`, `SG`) | all seven contributors by initials (S.N., M.S., Y.M., A.W., C.S., P.J.) | ✓ |
| C-12 | Competing interests "Mandatory… If there are no competing interests to declare, this should be stated" (`CT`) | "The authors declare no competing interests." (until 2026-09-15: "…, financial or otherwise."; the qualifier was dropped in the lossless condensation pass, "no competing interests" already covering every kind) | ✓ |
| C-13 | References "Limited to 60 references, though not strictly enforced" (`CT`) | **30** rendered entries in `paper.pdf`; **32** in the supplement. Re-measured 2026-09-25 at re-freeze 33 (`build/paper.bbl`: 30 `\bibitem`; rendered `[1]`–`[30]`): `baird2020biogears` entered the Discussion for BioGears, on the author's decision. At re-freeze 31, 29 (`build/paper.bbl`: 29 `\bibitem`; rendered `[1]`–`[29]`): `bakkes2023asynchrony` and `bikia2020aortic` entered the Discussion on the author's decision. Before that, 27 and 32, re-measured the same day as the `\bibitem` counts of `build/paper.bbl` (27) and `build/supplement.bbl` (32), at re-freeze 30: the paper went 26 → 27 at re-freeze 16 (`8f2adc2`, the Berlin Definition `ards2012` cited in Table 1, as `preprint_npj/dispatch_log.md` row 16 records), and this row had not followed. Until then it read **26** / **32**, re-measured 2026-09-15 from the built PDFs: entries `[1]`–`[26]` and `[1]`–`[32]`, both contiguous, each equal to the `\bibitem` count of its `.bbl`. **This row had gone stale.** Before the synthetic-data framing, at `e91c8ad`, the paper carried **22** (`.bbl`, source keys and rendered `[1]`–`[22]` agree; the same key counters return 34 and 23 on `63e887e`, the last `paper.tex` commit of 2026-08-03, matching the earlier measurement) and the supplement **32** (`.bbl`, and source keys once `\cite[Ch.~2]{…}` is matched). The 2026-08/09 synthesis pass moved or removed citations (docstring of `scripts/check_citations.py`, `[RETIRED]` block of `audit/citation_manifest.txt`); the per-commit path from 34 / 23 to 22 / 32 is not re-derived here. The paper then went 22 → 26 on the author's decision of 2026-09-15 with `vanbreugel2024synthetic`, `hwang2025sim2real`, `deepseek2026v41flash` and `victoriano2026sim2real`; the supplement did not change. History: re-measured 2026-08-03 as 34 / 23 from the built PDFs, entries `[1]`–`[34]` and `[1]`–`[23]`, both contiguous. Was recorded as 33 / 25: the paper gained `ward2024ventilator` (`5b4ad8c`), and the supplement lost two when `23c0d7b` dissolved §S3 and removed 106 lines of citation-bearing prose — that second change had never been re-measured. | ✓ |
| C-14 | "Figure legends — Limited to 350 words per figure" (`CT`); "this guidance also applies to any supplementary figures" (`SG`) | **15** figure legends measured; **maximum 322 words**, in the traffic-light map — which is **Figure 2**, not Figure 1 as this row said until 2026-08-03: Figure 1 is the study-design schematic, confirmed against the rendered PDF (`Fig. 1 \| Study design…`, `Fig. 2 \| Cell colour encodes reliability…`). **0 legends over the 350 cap.** Counted from LaTeX source, which over-counts inline math, so the rendered counts are lower still. Re-measured 2026-08-03; was recorded as 319, and the +3 is within the variance between two source-side counters — the original script lived in a session scratchpad and no longer exists, so the two figures are not strictly comparable. The compliance verdict does not depend on it. | ✓ |
| C-15 | "multi-panel figures should be presented on a single page with each panel labeled using an a), b), c) convention" (`CT`) | panel labels (a)–(f) present in the render | ✓ |
| C-16 | "Figure lettering should be in a clear, sans-serif typeface… the same typeface in the same font size… for all figures" (`SG`) | enforced in the generators; commits `bf85cd8` and `b3caa1c` | ✓ |
| C-17 | "Thousands should be separated by commas (1,000)" (`SG`) | `1{,}280`, `4{,}082`, `11{,}008` throughout | ✓ |
| C-18 | Statistics: "Use of the word 'significant' should always be accompanied by a P value; otherwise, use 'substantial,' 'considerable,' etc." (`SG`) | **one** occurrence of the stem in the whole corpus — `supplement.tex:506`, *"reverse-percentile bootstrap rejections at the same significance level"*, a technical term describing Cornish's test, not a claim about our data. Zero occurrences in `paper.tex` | ✓ |
| C-19 | Statistics: multiple comparisons — "authors should explain how they adjusted the alpha level to avoid an inflated Type I error rate" (`SG`) | Benjamini–Hochberg FDR, described in Methods §4.5 at `5675f52`, **§4.6 since the N-1 restructuring** | ✓ |
| C-20 | AI: "Use of an LLM should be properly documented in the Methods section"; LLMs "do not currently satisfy our authorship criteria" (`AI`) | Methods §4.6 *Use of AI tools* (**§4.7 since the N-1 restructuring**) names every model and phase; no LLM in the author list; Author contributions restates the scope. **Since 2026-09-15** (review comment: disclosure disproportionate): §4.7 keeps the tasks, the loop, every model by name and version, human supervision, code verification and responsibility, and points to **Supplement §S18**, which holds the model identifiers, settings and the phase-by-phase tasks, moved there without loss. **Primary source re-read 2026-09-15** (page downloaded, text extracted): the policy is now a Green / Amber / Red risk framework; neither quoted sentence is on the page any more (0 hits for "Methods section", "documented in", "authorship criteria"; positive control "Disclose AI use": 2 hits). It asks authors to "Disclose AI use for trust and transparency", files "Extensive copy editing or writing support" under Amber ("Permitted with human oversight, verification, and transparency through disclosure"), and lists "Assigning authorship or accountability to AI systems or tools" as not permitted. The split disclosure meets that text; the quotations in the requirement column are the earlier wording, kept as recorded. | ✓ |
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
