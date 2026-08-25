# Supplement prose sweep — contradiction pass over all 253 paragraphs

**Opened 2026-08-22.** The ledger re-derives 382 anchored values, the crosswalk
checks 94 more across documents, and 16 guards watch specific literals. None of
them reads prose. This register covers what they cannot: a paragraph-level pass
asking three questions, and nothing else.

1. **Internal contradiction** — a cardinal, population, unit, causal or temporal
   claim that the next sentence contradicts.
2. **External contradiction** — with `paper.tex`, the monograph, a table, a
   figure, or a supplement section already verified.
3. **Unrecognised claim** — a number, mechanism, qualifier or cross-reference
   that matches nothing already measured. These escalate immediately to a
   full re-derivation: primary source, unit and population, recompute, scope.

**What this pass can and cannot establish.** It is one reading, by one reader
whose first reading was wrong repeatedly on 2026-08-22 (five uncalibrated
patterns, two false alarms, one self-inflicted layout regression). It does not
certify the prose. It produces candidates; the escalation settles them. Entries
below therefore include *signal → verified → not a defect*, which are not
findings and must not be reported as such.

---

## Signals raised

| # | Locus | Signal | Status |
|---|---|---|---|
| 1 | §S1 ¶116 | "…that are **not present in BioGears**" — four sub-claims, four different statuses | ✅ **CLOSED 2026-08-24** — two supported claims kept, the source-insufficient and overclaimed ones dropped, and the absence bounded to a corpus **re-measured today** |
| 2 | §S2 Table row 4 | "a continuous-severity micro-sweep **confirms** the band" where §S5, Fig. S1 and the Discussion all say the sweep **extends** it to [0.879, 0.945] | ✅ **CLOSED `04d6f0f`** — now "confirms it and extends the low edge to 0.879" |
| 3 | §S3 | Four prose uses of "detector" for the object `paper.tex` calls "classifier" 33 times | **OPEN — needs per-occurrence semantic arbitration** |
| 4 | §S3 clamp patch note | "all **3,348** Pulse logs on disk" — a `find data -name pulse.log` today returns **3,349** | **OPEN — low severity, unresolved** |
| 5 | §S4 ¶392 and §S8 ¶650 (+ §S4 title, to arbitrate) | Two hard-coded references send the reader to "**Table 1** of the main manuscript" for per-cell flag counts. Paper Table 1 is the terminology glossary; the per-cell breakdown is **Table 3**. ⚠️ Three OTHER `Table~1` references are CORRECT and must not be swept | **OPEN — wrong pointer** |
| 6 | supplement p52 | The last page of the supplement carries **no page number**; it is the only such page in 52. It holds Table S16, a `[h]` float that LaTeX defers to the end | **OPEN — cosmetic but visible** |
| 7 | §S5 ¶433 | "reproduces the published anchors to **within 0.6 %**" — on the displayed integers (256, 150, 96) the worst case is 96 -> 96.6 = **0.625 %** | **OPEN — low severity, likely a rounding artefact** |
| 8 | §S6, **2 loci** | Calls S2 and S3 "the **moderate**-ARDS scenarios", and the pair "the moderate-ARDS **regime**". S2 is **mild** ARDS (0.26) everywhere else — 11 loci say so. Mild and moderate are distinct Berlin bands (P/F 200-300 vs 100-200) | **OPEN — clearest internal contradiction found; clinical category** |
| 9 | §S7 ¶597 | Quotes the Discussion as ``80 of 85 Hoeffding rejections fall on channels the present atlas does not assess''. That string occurs **0 times** in `paper.tex`; the Discussion says "82 of 85 fall outside the four-channel overlap: 80 on channels the present atlas does not assess" | **OPEN — quotation marks around a paraphrase** |
| 10 | ✅ **RESOLVED 2026-08-23** — §S7 ¶597 vs its table caption | Prose says "**Cornish's Table~4**" and "their **Appendix** Table~5"; the caption says "Cornish **Appendix Tables~4 and~5**". Same document, two accounts of where Cornish's Table 4 lives | **OPEN — internal contradiction; needs the source** |
| 11 | §S8 ¶650 | "The 64 paired reruns sampled **all eight** (scenario, sex) cells" — **S3_M has zero pairs**; the 64 cover **seven** cells | **OPEN — factual, overstates experimental coverage** |
| 12 | §S8 caption (¶659) | "Pulse's standard CSV output **does not natively expose** airway Pressure or Respiratory Flow as top-level columns" — **Pulse does expose them**; our data-request list does not ask for them | **OPEN — misattributes our configuration to the engine** |
| 13 | §S8 ¶665 | "by a factor of **approximately twenty** in the median paired comparison" — three defensible readings give 22.45, 28.16 and 64.5 | OPEN — low: ambiguous, and conservative under every reading |
| 14 | §S9 ¶673 vs ¶697 | **663 mmHg means two unrelated things in one section**: the alveolar-gas-equation prediction, and the measured male 120-s mean (662.57) | OPEN — collision hazard, both values correct |
| 15 | §S9 ¶695 | "within **approximately 5 %** of the asymptote" — the measured deviation is **0.05 %** (0.33 mmHg) | OPEN — low: true but ~100x too loose, and it is downstream guidance |
| 16 | §S9 ¶701 | "an **order-of-magnitude** drop … to 144 mmHg at moderate and 73 mmHg at severe" — 4.48x and 8.87x | OPEN — correct for severe, wrong for moderate |
| 17 | §S9 ¶701 | "the shunt-fraction kinetics **the alveolar-gas equation predicts** under increasing venous admixture" — that equation predicts alveolar PAO2, not shunt | OPEN — physiological attribution, needs author arbitration |
| 18 | §S11 ¶787 | "**each** is anchored in a specific experiment from this work" — items **3 and 6 carry no cross-reference at all** | OPEN — universal quantifier false on 2 of 6 |
| 19 | §S11 ¶787 | "The Discussion of the main manuscript **closes with** a forward-looking note on engine-side infrastructure" — it is paragraph **5 of 14**, with 9 after it | OPEN — positional claim, checkable and wrong |
| 20 | §S11 item 2 | "this constant **is not currently exposed** in the public patient-setup documentation" — unsourced absence claim about external documentation | OPEN — same class as signal 1; **triggers criterion (b)** of the citation rule |
| 21 | §S12 ¶884 **and `paper.tex:402`** | "The **1,280-row** Morris sample … matches the committed `morris_sample.parquet` byte-for-byte" — that file has **160 rows** | **OPEN — wrong figure in the reproducibility recipe** |
| 22 | §S12 ¶895/897/899 | "**five** run-level flags" against the paper's "four-flag classifier"; and a "22-run pilot … 22/22" against "the **20** per-run output CSVs" | OPEN — both accurate, neither bridged for the reader |
| 23 | §S12 ¶903 | "`kitware/pulse:4.3.1` … `linux/amd64` **only**" and "**no** prebuilt ARM64 image exists" | ✅ **SUPPORTED 2026-08-23** — registry queried; recommend **bounding** the second clause |
| 24 | §S13 ¶931 | "The SHAP cross-verification works **because the underlying physiology is real**, not the other way round" — two readings, one of which contradicts the Figure S5 disclaimer | OPEN — ambiguous epistemic premise |
| 25 | §S13 ¶931 | "input dependencies that **any reasonable statistical method** would identify on the same data" — an unbounded universal from **two** methods | OPEN — **downgraded**: wording only; the "undercut by its own numbers" reading was mine and is withdrawn |
| 26 | §S14 ¶939 | Of eight claims about what the monograph **contains**, two overclaim: "the **full preregistration document** with its amendment history" (§2.0 reproduces only §Primary hypotheses) and "the **complete experiment-log entries**" (Appendix A is a 43-line index) | **OPEN — checkable by anyone who downloads the Zenodo deposit** |
| 27 | §S15 table caption ¶963 | "Input HR is sampled **uniformly** from $[50, 110]$~bpm" — it takes exactly **four** values, 50/70/90/110, the Morris grid | OPEN — contradicts §S12's own `levels = 4` |
| 28 | §S15 ¶979 | The S3→S4 dip attributed to "incipient cardiovascular decompensation" with no mention of the **survivorship confound**: clean survival is 83.1 % in S3 against 39.7 % in S4 | **OPEN — scientific, an available alternative is unaddressed** |
| 29 | §S15 ¶959 | Names "the **four**-flag steady-state classifier" then lists **three** flags, omitting `clamped` | OPEN — zero numerical impact (`clamped` = 0/1,280) |
| 30 | §S17 ¶1022 | "**Six** engine-side infrastructure recommendations" — the six listed are **not the same six** as §S11: item 1 is dropped, item 3 is split in two | **OPEN — an index wrong about what it indexes** |
| 31 | §S12 ¶842–877 | "The **minimal command sequence** … from a **fresh clone**" **omits the Docker image build**. `src/runner.py:35` sets `DEFAULT_IMAGE = "pulse-atlas-engine"`, a locally-built image; step 2 fails on a fresh clone. | **OPEN — reproducibility, breaks for any outside user** |
| 32 | §S12 vs `README.md` | ~~The two public recipes diverge~~ | **WITHDRAWN — my error; the README does cover the ledger, in a separate section** |
| 33 | `TODO_publication_roadmap.md` -- **5 loci**: L44, L49, L51, L58, **L143** | The ledger count pinned at **313** where it is now **382**. L143 is a **live acceptance criterion**: "must stay 313/313 · 94/94 · 26/26 · 25/25 (currently green)". Population confined to this one file | **OPEN -- count corrected from 1 locus to 5; nothing re-measures it** |
| 34 | `README.md:357` | "santino/ **S001 … S031** entries" where the log reaches **S032**. The same locus previously read S001…S025 and was corrected to S031 — **it has drifted again** | **OPEN — recurrence, nothing re-measures it** |
| 35 | Figure S5 legend, from `make_supp_fig_s5_decomposition.py:137` | The legend reads "as recorded by the **detector**" — a term the project retired, **baked into a rendered PDF**, so invisible to both a `grep` of `supplement.tex` and to the vocabulary guard | **OPEN — recurrence of the Figure 1 defect, one scope out** |
| 36 | `paper.tex:77` vs `submission_metadata.txt:12` | Running title case differs: "Reliability **A**tlas: Pulse Physiology Engine" against "Reliability **a**tlas: …" | OPEN — cosmetic, two submission artefacts |
| 37 | **3 loci**: `README.md:161`, monograph **L71**, monograph **L320** | "34 … **at FiO₂ = 1.0**" over-attributes: **31** are at 1.0, 3 at 0.7367. Four other loci state it correctly | **OPEN — count corrected; the monograph says it both ways** |
| 38 | **5 loci**: `README.md:108`, `:156`, monograph **L338**, **L2007**, **L2231** | "divergence approximately **sex-balanced**" flattens a sign-reversing effect. `paper.tex` and `supplement.tex` are **clean** — their single occurrences mean *cohort design*, a different claim | **OPEN — count corrected after a homonym false alarm** |
| 39 | **2 loci, monograph only**: `manuscript.md:1271`, `:3314` | "Wall time for the full sweep ~ 7 h" at two workers. Corrected aggregate is **27.43 h**, so the floor is **13.72 h at two workers** and **9.14 h at three**. 7 h is below both. **README, supplement and paper are all CORRECT and must not be touched** | OPEN -- **factual, ground truth established; scope shrank from 7 loci to 2** |
| 40 | `README.md:261-266` | Announces "Manuscript S2.8 names **two** image hashes" and then prints **one**. The canonical sweep image `3b18bdc08660` is named in `manuscript.md:744` but dropped from the README bullet, which reads "Initial atlas image" with no hash. Not the S032 irrecoverable-image problem: the hash is recorded, it just fell out of the README | OPEN -- a promise the text does not keep |
| 41 | **3 loci**: `README.md:141`, `:323`, `:398` | "the silent FiO2 cap" stated with no scope, on a page whose headline says H2 NOT supported, Pulse "does **not** silently clamp" (0/1,280). Both are true and the monograph says why at S2.1 -- the cap is at the **wrapper layer**, and the atlas deliberately raises FiO2_MAX from 0.95 to 1.0 so the boundary reaches Pulse. The README never states wrapper != engine | OPEN -- legibility, not a factual error |
| 42 | `README.md:370` | Link text `Pulse_translation_new/` resolves to `https://github.com/santinon/` -- a user profile, not a repository. Public-facing broken pointer | OPEN -- cosmetic but visible to every reader |
| 43 | `README.md:255-257` | "Pulse 4.3.1 is bit-exact deterministic ... **so** reruns reproduce upstream values to 1e-6 relative tolerance" derives a weaker claim from a stronger one. Bit-exact implies tolerance 0. The correct scoping -- bit-exact *within* an image, 1e-6 *across* rebuilds -- is stated correctly 16 lines later at L271-274 | OPEN -- low; the same file already carries the right form |
| 44 | `data/runs/full_sweep/S4_M/S4_M_0123`, `_0124` + `src/runner.py:113` | **Data-integrity, not prose.** Two `wall_time_s` values are inflated by a host suspension (24{,}722.296 s and 24{,}722.282 s -- **14 ms apart after 6.87 h**). The `timeout_s = 600.0` guard did not fire, which is only possible if the Python process was suspended with its containers. Scientific outputs verified unaffected. Any future re-derivation of compute cost from this metadata is wrong by 50 % unless these two are excluded | OPEN -- **no manuscript claim depends on it; wire a guard** |
| 45 | `README.md:89` -- **1 locus** | "2 patient surrogates (**Pulse standard** adult male and female)" where `paper.tex:406` says the male height "**is not** Pulse's `heightStandardMale_cm = 177.0`" | ✅ **CLOSED 2026-08-23** -- now "2 adult reference surrogates (male and female)", propagating `CITATION.cff:37` |
| 46 | **10 loci**, 1 defective | "**reliability** traffic-light" surviving the curation/review-priority reframing | ✅ **CLOSED 2026-08-23** -- `CITATION.cff:42` only; `paper.tex:475` and `README:216` **arbitrated clean**, monograph x6 deferred |
| 47 | `CITATION.cff:22-23` | `version: "0.1.0"` / `date-released: 2026-05-22`, three months before submission and unchanged since. Covered in spirit by the file's own "blank until deposit" note, which does not mention these two fields | OPEN -- low; refresh at deposit |
| 48 | `cover_letter.md:34` | "four ARDS severities". `paper.tex` says "four severity scenarios (**a healthy baseline plus three ARDS severities**, impairment fractions 0.00 / 0.26 / 0.60 / 0.95)". S1 at 0.00 is healthy, not ARDS | OPEN -- **factual, contradicts the paper** |
| 49 | `cover_letter.md:60-62` | "Published Pulse validation work samples ARDS severity **only on round tenths** and **never probes inside this interval**." Outruns `paper.tex:359` on **two** axes -- see the dossier | OPEN -- ⚠️ **an absence claim outrunning its source** |
| 50 | `cover_letter.md:15` | "*npj Digital Medicine* lists **digital twins** explicitly within its scope" | ✅ **CLOSED 2026-08-23 -- VERIFIED TRUE at the primary source.** "Digital twins" is a topic bullet on the journal's own Aims and scope page |
| 51 | `cover_letter.md:31-32` | "the **first** open, preregistered reliability atlas of Pulse" -- a priority claim, but scoped to Pulse rather than universal | OPEN -- low; far more defensible than P-5's universal form |
| 52 | `submission_metadata.txt` | Portal abstract stale in every sentence, 155 words against a 150 cap, H1 absent, hyperoxia scope widened | ✅ **CLOSED 2026-08-23** -- block now **generated** from `paper.tex` by `scripts/sync_submission_metadata.py`, guarded in the pre-commit hook |
| 53 | `submission_metadata.txt` header | "Draft, **uncommitted**" on a git-tracked file | ✅ **CLOSED 2026-08-23** -- header replaced; it now names the generator as the source of truth |
| 54 | `TODO_publication_roadmap.md:284` | "(**✅ synced**)" certifying a file that was not | ✅ **CLOSED 2026-08-23** -- tick removed and replaced by a pointer to the mechanical check; the file is gitignored, so no guard can verify a claim made in it |
| 55 | `TODO_publication_roadmap.md:206-210` -- 6 of 8 line numbers wrong | The HARD GATE addressed its eight loci by `FILE:LINE`; `paper.tex` 409/430/434 had become 454/475/479, `supplement.tex` 809/939 had become 811/943 | ✅ **CLOSED 2026-08-23** -- replaced by `scripts/check_publication_gate.py`, which locates by **content**, refuses first-match-wins, and is wired into the pre-commit hook |
| 56 | `TODO_publication_roadmap.md:114-117` vs `submission_metadata.txt:52-53` | Two incompatible affiliation schemes: the roadmap records **4 affiliations** "[1]-[4]" dated 2026-06-11; the metadata records a **6-affiliation scheme** dated 2026-07-06 | OPEN -- ⚠️ **author data: flagged, deliberately NOT touched** |
| 57 | `preprint_npj/README.md` -- **3 loci**: L9, L78, L155 | Ledger pinned at "**195**/195 PASS" and "the legacy **195**-claim ledger" where the live total is **382**. A **third** stale ledger figure in the repository, distinct from the 313 of signal 33 | OPEN -- **factual, and this file is public** |
| 58 | `preprint_npj/README.md` -- **4 loci**: L6, L20, L66, L71 | Every page count is wrong, and two contradict each other in the same file. Monograph "**~92**-page" (L6, L66) against "**~100** pages" (L71); measured **118**. Supplement "**~22** pages"; measured **52**. Main "~12 pages"; `paper.pdf` is **37** | OPEN -- ⚠️ **`paper.tex:475` and `supplement.tex:941` say "over 100 pages" and are CORRECT** |
| 59 | `preprint_npj/README.md:53-54` | "A `build_npj.ps1` PowerShell wrapper **will be added** once the LaTeX sources stabilise (Step 1)." The file has existed since **2026-06-01** and was run twice today | OPEN -- low, stale future tense |
| 60 | `preprint_npj/README.md:248-252` | Status block: "Step 0 ✓ complete (**this commit**) · Step 1 -- Title + Abstract + Methods stub: **in progress** · Steps 2--10: **scheduled**". The package is submission-ready | OPEN -- low but conspicuous on a public page |
| 61 | `preprint_npj/README.md:106-110` | "The phrase 'clinical-AI training' applied to Pulse has **no verified citation** ... **as of 2026-05-23**. Do **not** write it without first adding a verified citation." The date-stamp makes the sentence honest, but it reads as a **live prohibition** whose premise has since been met: `ward2024ventilator` sits at `paper.bib:448` with a full-text-read verification note, and `cover_letter.md:27` uses it for exactly that | OPEN -- low; dated, not false |
| 62 | `paper.tex:372`, `manuscript.md:3388` | HumMod named with no citation, and characterised as "lumped-parameter" / "cardiopulmonary" against a source supporting neither | ✅ **CLOSED 2026-08-24** -- both qualifiers removed, `hester2011hummod` added to **both** `.bib` files |

### 1 — BioGears (§S1 ¶116)

> Pulse v4.3.1 includes respiratory calibration for ventilated patients,
> mechanoreceptor feedback, lung-recruitment modelling, and improved hemorrhage
> response **that are not present in BioGears**.

Measured: "biogears" occurs **0 times** in `audit/reference_audit.md`; no `.bib`
note documents the comparison; the sentence carries no citation. `git log -S`
**and** `-G` both return exactly one commit, `036d320`, the S028 skeleton — so it
has never been revised since it was first written. `--grep BioGears` finds
`c412d03`, but that touches the *paper's* Discussion ("BioGears is Pulse's
predecessor"), a different and sourced claim.

Note the whole sentence is uncited, not only the comparative clause: "Pulse
v4.3.1 includes [four features]" has no source either.

Proving a third party LACKS four features needs either BioGears source or an
explicit upstream statement of divergence. That is expensive for a background
sentence that carries no result. Author decision recorded 2026-08-22: verify at
primary source; if the absence is demonstrable, cite it precisely; if not,
**remove the comparison rather than soften it** — this is not a load-bearing
claim and does not justify a bibliographic debt.

### 2 — "confirms" versus "extends" (§S2, limitations table row 4)

Row 4 currently ends: "a continuous-severity micro-sweep confirms the band
(Supplement §S5)". Three other loci say the opposite thing about the same sweep:

- Fig. S1 caption: "the continuous sweep **extends the empirical band to
  [0.879, 0.945] on the low edge**";
- §S5, twice: "slightly wider on the low edge than the documented 0.91--0.945
  band";
- Discussion: "the first public characterisation of an ARDS impairment-fraction
  solver-instability band **([0.879, 0.945])**".

Not an overclaim — the reverse. Row 4 **understates the study's own finding**,
and is the only one of four loci to do so. Divergence appears at the 0.88 bin,
below the documented 0.91 edge, which is why the band was widened.

⚠️ The replacement must NOT say "preregistered band". Measured:
`preregistration.md` H3 calls it "the **previously characterized** ARDS zone
(0.91–0.945)" — it was documented before, and the preregistration referenced it
as the thing to look beyond. "documented" is the established term, used three
times in the supplement already.

Agreed replacement: "…the locked S4 scenario at 0.95 is intentionally above this
band; a continuous-severity micro-sweep **confirms the instability and extends
its empirical low edge to 0.879**".

### 3 — "detector" for the four-flag object (§S3)

`paper.tex` uses "classifier" 33 times, titles §4.4 "Steady-state classifier",
and `check_detector_vocabulary` bans four "…detector" phrases. That guard reads
`preprint_npj/paper.tex` **and nothing else**, so the supplement has never been
swept.

Supplement counts: classifier 21, detector 15. **None of the four banned phrases
appears.** The 15 break down as:

- **9 legitimate**: 5 × the filename `src/detector.py`, 4 × the label names
  `sec:methods-detector` and `sec:s3-detector-order`. Labels and filenames are
  identifiers, not prose, and are not renamed.
- **2 faithful to the preregistration and to be KEPT**: "preregistered detector
  conventions" and "Detector validation on twenty reference runs".
  `preregistration.md` itself uses "detector" 6 times for named items —
  "**Detector self-consistent**" is the G2 gate name that `DETECTOR_REQUIRED`
  protects, and "detector validation" is its own phrase.
- **4 candidates**, to be arbitrated one at a time, never in bulk:
  1. "**The detector's** flag priority order" — ⚠️ the subsection two lines
     above is titled "Four-flag **classifier**: priority order and rationale".
     Same subsection, two names, one object. The clearest of the four.
  2. "users adopting **this detector** do not inherit the gap" — reads as the
     whole object.
  3. "a **detector** edge case" — reads as the whole object.
  4. "the `not_steady_state` **detector** uses" — ⚠️ may legitimately denote the
     drift sub-check rather than the four-flag object. Author flagged this one
     as possibly correct as written.

**Never apply a blanket replacement.** `DETECTOR_REQUIRED` exists precisely to
fail on that, and was falsified on it on 2026-08-22: renaming "log-based
detector" makes the gate exit 1.

### 4 — the 3,348 log denominator (§S3, clamp-patch note)

The note says: "Replaying both pattern sets over all **3,348** Pulse logs on disk
flips exactly one run --- the probe written to expose the gap --- and no run in
the published sweep".

Measured 2026-08-22: `find data -name "pulse.log"` returns **3,349**. The figure
3,348 also appears in `audit/figure2_reframing_diffs.md` and
`audit/n1_methods_restructure.md`, both tracing it to a commit message written
when the patch was made on 2026-07-26.

**Could not be resolved, and the reason is worth recording.** File mtimes cannot
date these runs: a checkout, a copy or a regeneration rewrites them. Splitting
the corpus at 2026-07-26 by mtime gives 3,293 before and 56 after, which matches
neither figure, so mtime archaeology is not evidence here.

**Low severity, and deliberately left open rather than "corrected" to 3,349.**
The load-bearing claim is "flips exactly one run, and no run in the published
sweep" — a numerator and an exclusion, neither of which depends on the exact
denominator. Rewriting 3,348 to today's 3,349 would replace a figure traceable to
a dated commit with one traceable to nothing, which is worse. Settling it
properly means re-running the replay and recording the count with its date.

Corroborating detail: the newest logs on disk are `s030b_bound_hr49`, `hr50`,
`hr110` and `hr111` — the heart-rate boundary probes. The note's mechanism is
exactly that a heart rate below 50 bpm was rejected by Pulse at setup without
raising `clamped`, so the probe it describes does exist.

### 5 — "Table 1 of the main manuscript" points at the glossary (§S4, §S8)

Read out of the built PDF rather than counted from source, the paper's tables are:

| | caption |
|---|---|
| Table 1 | Terms used in this paper, with section references |
| Table 2 | Definitions and trigger conditions of the four steady-state flags |
| **Table 3** | **Per-cell flag breakdown across the eight scenario × sex cells** |
| Table 4 | Per-cell retention under the two screening definitions |

The supplement holds **seven** hard-coded `Table~N` references. Enumerated in
full before counting, because the first pass of this very entry got it wrong:

| line | reference | verdict |
|---|---|---|
| 392 | "Table~1 … reports per-cell counts under the locked four-flag classifier" | ⚠️ **wrong — wants Table 3** |
| 650 | "cells where the dyssynchrony signal is densest (Table~1 of the main manuscript)" | ⚠️ **wrong — wants Table 3** |
| 396 | "Cell-label key (see main paper Table~1 for **full definitions**)" | ✅ correct |
| 504 | "Scenario key (see main paper Table~1 for **full definitions**)" | ✅ correct |
| 577 | "Cell-label key (see main paper Table~1 for **full definitions**)" | ✅ correct |
| 597 | "**Cornish's** Table~4" and "their **Appendix** Table~5" | ✅ correct — these are the cited study's tables, not ours |

So **two of seven** are wrong, not three or more. Three other `Table~1`
references are right, because Table 1 *is* the glossary and they ask for
definitions. ⚠️ **A blanket replacement of `Table~1` would break all three.**

Also to arbitrate, separately: §S4 is titled "Extended **Table 1**:
not_steady_state attribution" while what it extends is the per-cell breakdown,
i.e. Table 3. Possibly a legacy name from when the paper carried fewer tables.

**A false alarm this entry raised and must not leave behind**: "Table~5" looked
like a dangling pointer, the paper having only four tables. It is Cornish's
appendix table, correctly attributed in the same sentence.

**Structural cause, and why it will recur.** The supplement hard-codes paper
table and figure numbers. Its `\mainref{label}{number}` macro exists for
**sections only** — 35 uses, none on a table or a figure. So these pointers
cannot follow a table inserted upstream, which is the most likely way they went
stale. The three "Figure~2 of the main manuscript" references are, by contrast,
**correct**: Figure 2 is the traffic-light map, and each context is about it.

Escalation note for the fix: correcting the numbers is not enough on its own if
nothing re-measures them. Either extend `\mainref` to floats, or guard the
mapping the way `check_detector_vocabulary` guards vocabulary.

### 6 — the supplement's last page has no page number

Raised by the author on 2026-08-22, and not by any check: `check_render.py`
counts pages and float placement, not whether a folio is printed.

Measured across all 52 pages: **p52 is the only page without its number**, and it
is not blank -- 455 words. The paper does not share the defect; its last page,
37, prints its number. `supplement.tex` contains no `	hispagestyle` or
`\pagestyle` command, so nothing suppresses it explicitly.

Page 52 holds Table S16, the index of supplementary findings, declared `[h]`
rather than `[p]`. Being the last content and too large for the remaining space,
it is deferred and flushed at `\end{document}` onto a float page, whose style
drops the folio.

⚠️ Any fix must be MEASURED, not assumed. On 2026-08-22 two float interventions
in this repository behaved unexpectedly: tightening subfigure spacing cleared an
overflow while silently pushing rows over their own subcaptions, and a longer
caption deferred three supplement figures to the end of the document. Rebuild and
re-read the pages after whatever is tried.

### 7 — the 0.6 % replication tolerance (§S5)

"Evaluated over the companion's measurement window, the replication reproduces
the published anchors to within 0.6 % at the three scenario fractions (0.26 ->
256.5, 0.60 -> 150.5, 0.95 -> 96.6 mmHg)".

Table `tab:s5-berlin-calib` prints the published anchors as integers: 256, 150,
96. Computed on those, the relative differences are 0.195 %, 0.333 % and
**0.625 %** — the last one just over the stated 0.6 %.

**Unresolved, and honestly so.** The displayed 96 is rounded, so the comparison
was presumably made on unrounded values, where it may well hold. The artefact
`results/s030_pf_by_arm.csv` carries unrounded P/F but over two windows,
[60,120] and [240,300], giving 255.27 / 258.63 for 0.26 and 87.34 / 112.64 for
0.95. The section's figures fall *between* those windows, consistent with the
third "companion's measurement window" it names, which is not in this artefact.
Settling it needs that window's definition.

**Verified in the same pass and NOT a defect** — the band re-derivation of ¶433
is confirmed directly in the raw artefact. `results/s030_pf_by_arm.csv` shows
impairment 0.91, 0.92, 0.93, 0.94 and 0.945 all `FAILED` on **both** the free and
locked arms, with 0.90 and 0.95 completing, exactly as the paragraph claims. That
0.90 completes here while Figure S1's micro-sweep diverges at the 0.88 bin is not
a contradiction: this is one fixed reference setting, the micro-sweep is midrange
Morris inputs, and §S5 states the instability is input-dependent.

### 8 — S2 called "moderate" where 11 other loci call it "mild" (§S6 ¶545)

> …is computable only for the **moderate-ARDS scenarios S2 and S3** (the
> gas-exchange and severe-ARDS cells S1 and S4_F have no clean FiO2
> elementary-effect pairs…)

Measured across `supplement.tex` and `paper.tex`: **"S2 mild ARDS" 8 times,
"S2 mild" 3 more — 11 loci.** Against them, **two** loci in §S6, both found only
after widening the pattern past the first one:

- "computable only for the **moderate-ARDS scenarios S2 and S3**" — unambiguous,
  it labels both scenarios moderate;
- "rankings are preserved across sex in the **moderate-ARDS regime**" — weaker,
  since "regime" could denote the mid-severity region taken as a whole.

No hyphenated "mild-ARDS" form exists anywhere; the documents write "S2 mild
ARDS".

This is not a style slip. S2 is impairment 0.26, calibrated in §S5 to a P/F of
256 mmHg, which is the **mild** Berlin band (200--300). Moderate is 100--200,
where S3 sits at 150. Calling S2 moderate moves a scenario between two distinct
diagnostic categories, in a paper whose ARDS severities are calibrated *to those
very bands*. A clinician reviewer reads this immediately.

The sentence is otherwise correct: ρ really is computable only for S2 and S3, and
Figure S2 shows exactly that — the S1 and S4 rows are empty, which
`results/spearman_mu_star.csv` confirms with blank entries.

Secondary, same sentence, lower confidence: "the **gas-exchange** and severe-ARDS
cells S1 and S4_F". S1 is the healthy baseline, not a gas-exchange cell. The
*reason* S1 has no clean FiO2 pairs is gas-exchange-related — SpO2 saturation
pinning — so the descriptor is loose rather than wrong, but it reads oddly beside
the precise scenario names used everywhere else.

### 9 and 10 — §S7's quotation and its Cornish table locations

**9. The quotation is a paraphrase.** §S7 opens by summarising the Discussion
"as ``80 of 85 Hoeffding rejections fall on channels the present atlas does not
assess''". Measured: that string occurs **0 times** in `paper.tex`. The
Discussion reads "Of these, 82 of 85 fall outside the four-channel overlap (HR,
MAP, PaO2, PaCO2): 80 on channels the present atlas does not assess (electrolyte,
metabolic, acid--base, dermal), plus 2 on partial-overlap pressure channels".

The content is faithful — 80 really do fall on unassessed channels — so this is
not a misstatement of fact. But quotation marks promise verbatim, and in a paper
whose subject is verification discipline, quoting its own Discussion loosely is
the kind of thing a reviewer notices. Applied to an external source the same
habit would be serious.

**10. Where does Cornish's Table 4 live?** The prose distinguishes them:
"``Hoeffding'' counts come from **Cornish's Table~4**" and "``Bootstrap'' counts
come from their **Appendix Table~5**". The caption of the very table that prose
introduces says "(Cornish **Appendix Tables~4 and~5**)".

~~Not resolvable from inside the repository~~ — **✅ RESOLVED 2026-08-23, source
opened.** The PDF was downloaded (arXiv:2301.07210) and read.

**Cornish states the location twice, in his own words:**

> L806 — "(see **Table 4 in the Appendix** for a complete list)"
> L848 — "(**Table 4 in the Appendix** shows all hypotheses we tested, including
> those not rejected.)"

And both tables sit physically in the appendix, adjacent, from page 39: **Table
4** (Hoeffding) then **Table 5**, whose caption reads "obtained using the
**reverse percentile bootstrap**", immediately followed by section *I.7
Bootstrapping Details*.

**Verdict: the caption is right, the prose is misleading.** "Cornish
**Appendix Tables 4 and 5**" is correct. §S7 ¶597's "Cornish's Table~4" followed
by "their **Appendix** Table~5" implies by contrast that Table 4 is in the main
text; both are in the appendix. The *content* attribution is correct on both
sides — Hoeffding counts do come from Table 4, bootstrap counts from Table 5.
Only the location wording is wrong.

**Repair, for the correction pass**: "Cornish's Table~4" → "Cornish's **Appendix**
Table~4". One word, no claim changes.

⚠️ **A source-side defect found while resolving this, recorded so no future
reading treats Cornish's narrative as authority over his own tables**: his prose
says "we obtained rejections for hypotheses corresponding to **10** different
physiological quantities shown in Table 1", while Tables 1 and 4 both show
**nine** with non-zero rejections. Our documents follow the tabulated data and do
not repeat the error.

**Independently recomputed from Table 4 during the same read**, confirming the
figures this register already carried: **15** assessed quantities; rejection
column summing to **85**; hypothesis column summing to **1,522**; and the
80 / 2 / 3 split — Chloride 24 + Sodium 21 + Potassium 13 + Calcium 5 + Glucose 5
+ HCO₃ 2 + arterial pH 0 + Skin Temperature 10 = **80** across the eight
unassessed channels, SysBP **2**, paCO₂ **3**, with HR, MeanBP and paO₂ all at
zero.

**Verified in the same pass and correct** — the caption's arithmetic. "80 on the
**eight** channels the atlas does not assess" matches the table exactly:
Chloride, Sodium, Potassium, Calcium, Glucose, HCO3, arterial pH and skin
temperature, and their Hoeffding numerators sum to 80. "Plus 2 on the
partial-overlap pressure channel SysBP" matches SysBP 2 / DiaBP 0, and 80 + 2 + 3
= 85. The whole table sums to 15 channels, 85 rejections and 1,522 hypotheses —
1,522 being the correct figure, not the 1,442 typo carried by Cornish's own main
text, which appears nowhere in our three documents.

### 11 — the S014 pairs cover seven cells, not eight (§S8 ¶650)

> The 64 paired reruns sampled **all eight** (scenario, sex) cells, with most
> coverage concentrated on the healthy-S1 and mild-ARDS-S2 cells…

Enumerated cell by cell from `data/runs/s014_trigger_lockout/*_lock`, all eight
named explicitly rather than counted from whatever the listing happened to show:

| cell | pairs | | cell | pairs |
|---|---|---|---|---|
| S1_M | 6 | | S3_M | **0** |
| S1_F | 20 | | S3_F | 5 |
| S2_M | 10 | | S4_M | 1 |
| S2_F | 9 | | S4_F | 13 |

Total 64 ✓, over **seven** cells. **S3_M is empty.**

This is factual, not terminological: it overstates the experiment's coverage. A
reader takes "all eight cells" to mean every cell is represented in the paired
design, and one is not.

**The supplement contradicts its own upstream experiment log.**
`experiments_log/santino/S014_trigger_pressure_lockout.md` states at L204:

> S3_M is absent from the top-64 (S3_M's three flagged runs have lower `Vt_cv`
> than the cutoff).

and at L76: "Stratification across cells is sacrificed for paired-test power."
The selection is `pool.nlargest(64, "Vt_cv")` in
`scripts/run_s014_trigger_lockout.py:114` — a top-64 ranking over the whole
sweep, **deliberately not stratified**. So "sampled … all eight cells"
misstates the design twice: the coverage is not eight, and coverage was never a
design property to begin with.

**The log's explanation, verified directly** (reproducing the top-64 from
`data/runs/full_sweep/aggregated.parquet`, 1,280 rows, eligible pool 1,260 after
the 20 diverged):

- cutoff = min `Vt_cv` of the top-64 = **0.284786**
- S3_M's highest `Vt_cv` = **0.222869** → below the cutoff ✓
- S3_M runs at `Vt_cv` ≥ 0.05 = **3 of 160** ✓ — the log's "three flagged runs"
  is the CV-threshold flag, **not** `not_steady_state`, which is 12 for that
  cell. Two different referents; the earlier draft of this entry cited the wrong
  one.

The reproduced distribution — 6/20/10/9/**0**/5/1/13 — matches the directory
listing, `selection.parquet` and `paired_comparison.parquet` exactly. Four
instruments, one answer.

**In fairness to the sentence**: its second clause, "most coverage concentrated
on the healthy-S1 and mild-ARDS-S2 cells where the dyssynchrony signal is
densest", is honest about the unevenness and about what drives it. The defect is
localised to "all eight".

**Verified correct in the same paragraph and sentence**: "most coverage
concentrated on the healthy-S1 and mild-ARDS-S2 cells" — S1 holds 26 pairs and S2
holds 19, so 45 of 64 ✓. And note it writes "**mild**-ARDS-S2" here, which
strengthens signal 8: §S6's "moderate" is the outlier, not the norm.

### 12 — Pulse does expose airway pressure and flow (§S8 caption, ¶659)

> Pulse's standard CSV output does not natively expose airway Pressure
> ($P_{	ext{aw}}$) or Respiratory Flow ($\dot{Q}$) as top-level columns, so the
> per-breath delivered tidal-volume waveform shown here is the directly
> observable proxy of the trigger-coupling dynamics.

The archived CSV indeed carries neither: 13 columns, every pressure match
arterial (`SystolicArterialPressure`, `DiastolicArterialPressure`,
`MeanArterialPressure`, `ArterialCarbonDioxidePressure`,
`ArterialOxygenPressure`), zero matches on flow. That part is true of the file.

**But the engine does expose them.** In the Pulse clone,
`src/cpp/cdm/system/physiology/SERespiratorySystem.h` declares as first-class
scalars:

| line | property |
|---|---|
| 37–39 | `AirwayPressure` |
| 81–83 | `ExpiratoryFlow` |
| 113–115 | `InspiratoryFlow` |
| 145–147 | `MeanAirwayPressure` |
| 241–243 | `TotalPulmonaryVentilation` |

And the atlas requests its channels by name from a hard-coded list:
`engine/run_atlas_engine.py:101–111` loops over `OUTPUT_VARIABLES` calling
`SEDataRequest.create_physiology_request(name)`. `AirwayPressure` is one entry in
that list away.

So the CSV lacks those channels because of **our data-request set**, not because
Pulse cannot produce them. The sentence attributes a configuration choice of ours
to a limitation of the engine.

**Why this one matters more than its size suggests.** It is a factual claim about
Pulse's capabilities, in a paper whose subject is characterising Pulse, and its
most likely reader is a Pulse maintainer. It also does work in the argument: it
is the stated reason the waveform figure uses Vt as a *proxy*. Remove the false
premise and the justification has to be restated — truthfully, and just as
defensibly: the archived runs do not carry those channels, so showing them would
require re-running the sweep.

No result changes. **Escalation A is not needed** — the ground truth is in the
source and in our own runner.

### 13 — "a factor of approximately twenty" (§S8 ¶665)

> …dropping the Vt CV by a factor of approximately twenty in the median paired
> comparison.

Three readings of "in the median paired comparison", measured over the 64 pairs:

| reading | value |
|---|---|
| ratio of the medians (0.350867 / 0.015631) | **22.45** |
| median of the per-pair ratios | **28.16** |
| the pair at the median, S4_F_0003 (0.350839 / 0.005442) | **64.51** |

"Approximately twenty" is defensible for the first, marginal for the second,
wrong for the third. The first is also the one that matches the neighbouring
sentence in ¶646, which quotes the two medians 0.351 and 0.016.

**Low severity, and worth saying why**: every reading exceeds twenty, so the
phrasing understates the effect in all three. It is never an overclaim. The
defect is ambiguity, not inaccuracy.


### 14 — 663 mmHg carries two unrelated referents in §S9

- ¶673: "approximately 20~mmHg below the simple alveolar-gas-equation prediction
  at sea level of ~663~mmHg" — a **theoretical** value, 1.0(760-47) - 40/0.8 = 663.
- ¶697: "mean 686 versus **663**~mmHg in the locked 120-second window across the
  four RR = 20 pairs" — a **measured** male mean. Reproduced: 662.57.

Both are right. They sit 0.43 mmHg and roughly twenty lines apart, and they
measure nothing in common. The hazard is the inference a reader can draw
unaided: that the male body "matches theory" while the female body exceeds it.
The text neither makes that claim nor supports it — the agreement is a
coincidence.

Verified correct here: the female mean 685.96 → "686", the five input-identical
pairs, female runaway 5/5, male 1/5, male plateau 779.20 → "779", female range
1168.94–1408.49 → "1,169--1,408".

### 15 — "within approximately 5 % of the asymptote" (§S9 ¶695)

Guidance to downstream users: record 300 s and average over t = 240--300 s, which
"puts the PaO2 estimate within approximately 5 % of the asymptote".

Measured on the 38 physiological-converged median trajectory: asymptote 639.34
mmHg, window mean 639.01 mmHg, deviation **0.33 mmHg = 0.05 %**. Even reading
"5 %" as 5 % of the *gain* (87.5 mmHg) gives 4.37 mmHg = 0.68 % of the asymptote.

True, therefore, but about two orders of magnitude too loose — and the two
denominators, asymptote and gain, are not the same quantity. It matters because
it is a recipe: "approximately 5 %" of 639 mmHg reads as ±32 mmHg of residual
error, which a reader could reasonably judge too imprecise for a blood-gas
endpoint, and so reject a recommendation that is in fact excellent.

### 16 — "an order-of-magnitude drop" (§S9 ¶701)

> …an order-of-magnitude drop from the healthy S1 median to 144~mmHg at moderate
> and 73~mmHg at severe ARDS…

From the table's own medians: 643.31 / 143.58 = **4.48x**, and 643.31 / 72.56 =
**8.87x**. The descriptor is defensible for severe (8.87 is within 11 % of ten)
and wrong for moderate, where the drop is under half an order of magnitude. One
magnitude word is attached to two values and fits only one.

Verified correct in the same sentence and table: 143.58 → "143.6" → "144",
72.56 → "72.6" → "73", n = 8 and 8 (four paired Morris vectors x two bodies),
n = 44, and 8 + 8 + 44 = 60, matching the rerun total stated in ¶677.

### 17 — what the alveolar-gas equation predicts (§S9 ¶701)

> This reproduces the shunt-fraction kinetics the alveolar-gas equation predicts
> under increasing venous admixture…

The alveolar gas equation, PAO2 = FiO2(Pb - PH2O) - PaCO2/R, predicts **alveolar**
oxygen tension. It says nothing about venous admixture: the fall in *arterial*
PaO2 with increasing shunt is described by the shunt (Berggren) equation, and
shows up as a widening A–a gradient. As written, the equation is the grammatical
subject doing the predicting, which attributes to it a behaviour it does not
model.

A defensible weaker reading exists — "the kinetics that follow from the alveolar
gas equation *together with* increasing venous admixture" — so **two readings**,
which by this project's own rule means presenting both rather than silently
picking one. Author arbitration required: it is a physiological attribution, not
a typo.

The underlying result is untouched and correct: the plateau falls monotonically
with severity, and the S1 elevation is a healthy-lung property.


### §S10 — swept, no signal

Recorded because a clean section is a result, not an absence of work. Every
numeric claim in §S10 was re-derived, and the two source claims were opened in
the Pulse clone in this session.

**Arithmetic, all exact** (recomputed from the two reference-body masses):

| claim | text | recomputed |
|---|---|---|
| BV male | 4,802.63 | 4802.6308 |
| BV female | 3,996.09 | 3996.0865 |
| difference | 806.54 | 806.5443 |
| gap as % of male | 16.8 % | 16.794 % |
| male floor ×0.85 | 4,082.24 | 4082.2362 |
| male − floor | 720.39 | 720.3946 |
| floor − female | 86.15 | 86.1497 |
| female ceiling ×1.15 | 4,595.50 | 4595.4995 |
| male − ceiling | 207.13 | 207.1314 |
| mL/kg male | 71.4 | 71.3615 |
| mL/kg female | 71.1 | 71.1047 |
| normalised gap | 0.3 mL/kg, ≈0.4 % | 0.2568, 0.360 % |
| body-mass gap | 16.5 % | 16.493 % |

**Primary source, opened this session** —
`SetupPatient.cpp` in the local Pulse clone:

- L534 `computedBloodVolume_mL = 65.6 * pow(weight_kg, 1.02)` — the formula as
  printed, and **no sex term**, which is what "not sex-branched" asserts.
- L535–536 `* 0.85 //Stage 1 Hypovolemia` and `* 1.15`.
- L550–561: **both** bounds raise `patient.Error(ss)` and set `err = true`. The
  supplement's "rejects any baseline above … with an `[ERROR]` and exit, exactly
  as it rejects one below the floor" is exact, including the symmetry.
- Incidental cross-check: L567–569 gives RR standard 12, max 20, min 8,
  independently reconfirming the project's verified limitation #6.

**§S10-breadth**, traced to `audit/pulse_sex_conditioned_parameters.md` (the file
the text names, 52 KB, present):

- body fat 0.21 / 0.28 — confirmed at `SetupPatient.cpp:207–208`
- Hb 15.0 / 14.0 → Hct via `Hb/34`: 0.44118 → **0.4412**, 0.41176 → **0.4118** ✓
- cardiac output 5,600 / 4,900 at `SetupCircuitsAndCompartments.cpp:293`
- **seven** regional flow fractions (L314–330) and **thirteen** tissue masses
  (L2153–2165) — both counts as printed
- lung tissue mass **+9.8 %** at equal weight and **−8.3 %** at native masses,
  both reproduced from the inventory's worked case
- dead space: Devine intercepts 50.0 vs 45.5 → 4.5 kg, × 0.002 L/kg = **9 mL** ✓
- Roza–Shizgal: 88.632 − 88.362 = **0.270** kcal·day⁻¹; on a male-body BMR of
  1,751.6 kcal·day⁻¹ that is **0.0154 %** → "0.015 %" ✓

**Cross-references checked**: `\S\ref{sec:s2}` does document the sex-conditioned
BMR pathway (§S2 closing paragraph, Roza–Shizgal); `\S\ref{sec:s9}` does carry
the 2×2 sex×mass check (§S9 ¶697).

⚠️ **Not verified in this session**: the Roza & Shizgal 1984 primary source itself
(that 88.362 is what the paper prints). The value matches the equation as
universally cited, and the reference audit closed Tiers 1–3 in an earlier
campaign, but that is a recorded claim, not a measurement made here.


### 18 — "each is anchored in a specific experiment from this work" (§S11 ¶787)

Counted per item, printed before counting, with `grep -o 'ref{...}'` after an
`awk` attempt returned 0 for every item and was discarded as broken (its escape
warnings gave it away — item 1 visibly carries a reference):

| item | cross-references |
|---|---|
| 1 structured input-rejection events | `sec:s3-clamp` |
| 2 blood-volume floor | `sec:results-sex` |
| **3 sensitivity-analysis recipe** | **none** |
| 4 ARDS band warning | `sec:s2`, `sec:s5-prov`, `sec:s5-cont` |
| 5 per-channel drift column | `sec:results-hyperoxia`, `sec:s3-drift` |
| **6 field-attributed error messages** | **none** |

Four of six are anchored; two are not. Item 3 points only at Pulse's own 2020
study tag, and item 6 at nothing.

**In fairness**: the *substance* of both is anchored in this work — item 3 in the
atlas's sampler and runner, item 6 in the same setup-rejection experience as item
1. What is missing is the reference, not the experience. But "each" is a
universal quantifier over an enumerable population of six, and it is false as
written.

### 19 — the Discussion does not close with the infrastructure note (§S11 ¶787)

> The Discussion of the main manuscript **closes with** a forward-looking note on
> engine-side infrastructure suggestions for the Pulse maintainers.

The Discussion runs `paper.tex` 366--395 and holds **14 paragraphs**. The
infrastructure note is **paragraph 5** (L376). Nine paragraphs follow it: the six
scope limits (L378--L388), the foundational-infrastructure paragraph (L390), the
extensions (L392), and the actual closing paragraph (L394), which is about
Pulse-generated cohorts being used as machine-learning training data.

Low stakes, but it is a positional claim any reader can check in ten seconds, and
it is wrong.

### 20 — an unsourced absence claim about Pulse's public documentation (§S11 item 2)

> Pulse hard-enforces a 4,082.24 mL blood-volume floor at setup … but **this
> constant is not currently exposed in the public patient-setup documentation**.

Same class as signal 1 (BioGears): a claim of **absence** about a document
outside this repository, carrying no citation. The floor itself is verified
(§S10, `SetupPatient.cpp:535`); what is unverified is that Pulse's public patient
methodology does not mention it.

**✅ SOURCE OPENED 2026-08-23 — verdict: PARTIALLY OVERCLAIMED, and it is worse
than the original entry assumed.**

Pulse's public *Patient Methodology* page, Table 1, read this session:

> formula **`Bv[mL] = 65.6W[kg]^1.02`** · lower bound **`Bv * 0.85`** · upper
> bound `Bv * 1.15` · annotation "Above Stage 1 Hypovolemia."

And, checked explicitly: the page **does not** state that a baseline below that
fraction is *rejected at setup*.

So the claim splits three ways:

| clause | verdict |
|---|---|
| "**this constant** is not currently exposed" — i.e. the 4,082.24 mL value for the male body | ✅ **true**; it is body-specific and derived, and does not appear |
| "a one-line note in the **patient-baseline reference table** would have saved the investigation" | ⚠️ **wrong about the table it names** — that table already carries `Bv * 0.85`, which is the rule that produces the floor |
| what is genuinely undocumented | ✅ that the bounds are **hard-enforced, with an `[ERROR]` and exit**, rather than advisory — the page presents them as bounds without saying they gate setup |

**Why this one matters more than its size.** It is a recommendation *addressed to
the maintainers of the very documentation it mischaracterises*, in a paper whose
subject is verification discipline. Its most expert reader is the person best
placed to notice.

**The repair is available and makes the recommendation stronger, not weaker**:
ask for the *enforcement* to be documented, not the constant. The rule is already
public; the fact that violating it aborts the run is not.

**The paper is the better-stated document again.** `paper.tex:376` says only "(2)
documentation of the male reference body's blood-volume floor" and makes no claim
about what the table lacks.

**Unaffected**: §S10's and §2.5's use of `pulsepatientmethod` for the allometric
formula. The formula is on that page verbatim, as quoted above.

### §S11 — verified correct

- The six items map **1:1 and in the same order** onto the six enumerated in
  `paper.tex:376`, down to the parenthetical "one typed record per rejected
  field" in item 1. Cross-document consistency here is exact.
- "items 1--6" in ¶803 matches the six-item list.
- `paper.tex:221` independently says "six concrete engineering recommendations".
- Item 2's 4,082.24 and 4,802.63 mL — re-derived in §S10.
- Item 4's `[0.879, 0.945]`, the narrower 0.91--0.945 zone, and "three
  independent boundary probes" — consistent with the project's verified
  limitation #4 and with the now-closed signal 2.
- Item 3's `STUDY_SENSITIVITY_ANALYSIS_1_0_0` characterisation matches verified
  limitation #1.
- Item 1's pointer to §S3-clamp is correct: that subsection does print the
  pattern set in a `lstlisting`.


### Census of the paper-supplement coupling, and what actually guards it

Added because "the two documents must agree" is only actionable once the
population is enumerated. Measured with a calibrated pattern (a known-present
reference is asserted before any count is believed).

| direction | occurrences | distinct targets | numbering guarded? | semantics guarded? |
|---|---|---|---|---|
| supplement → paper (`\mainref`) | **39** | 10 | **yes** — `check_cross_document_refs()` | **no** |
| paper → supplement (`\ref` to `sec:s*`) | **51** | 30 | resolved by `xr-hyper` at build | **no** |

**What `check_cross_document_refs()` actually does** (`scripts/check_render.py`
L274--305): for each `\mainref{label}{written}` it checks the backslash is
present, that `label` resolves in `paper.aux`, and that the hard-coded `written`
number matches what the label resolves to. It is a **numbering** check. It scans
`_MAINREF_SOURCES = ["preprint_npj/supplement.tex"]` — **the supplement only**.

**Three consequences, stated plainly:**

1. The **paper → supplement** direction has no equivalent scan. It cannot carry a
   wrong number (LaTeX resolves it), but nothing checks the 51 references at all.
2. **Semantics is guarded in neither direction.** Nothing verifies that the
   target says what the citing sentence claims it says. Signal 19 is exactly
   this: the `\mainref` numbering is correct, and the sentence about what that
   target *contains* is wrong.
3. A supplement-driven sweep sees a paper/supplement disagreement **only where
   the supplement raises the topic**. Anything asserted only in the paper is
   structurally invisible to it. This is a second, independent argument for the
   paper's own B sweep, distinct from the "the ledger sees numbers, not prose"
   one.

**Hotspot worth knowing before any edit**: 15 of the 39 supplement→paper
references point at `sec:results-sex` alone, and 6 more at
`sec:results-secondary`. Rewording §2.5 of the paper puts fifteen supplement loci
at risk in one move.

**One artefact, not a defect**: the census counts one `\mainref{<label in
paper.tex>}` occurrence. That is the macro's own documentation in the preamble;
the guard strips `%` comments before scanning, and `crossdoc` reports OK.

This table is the population for the semantic pass. 39 + 51 = **90
cross-references** to walk, each asking one question: does the target say what
the sentence claims?


### 21 — the Morris sample has 160 rows, not 1,280 (§S12 ¶884)

> The **1,280-row** Morris sample is regenerated deterministically from the SALib
> sampler with `trajectories = 20, levels = 4, seed = 42`; the regenerated sample
> matches the committed `data/runs/full_sweep/morris_sample.parquet`
> byte-for-byte.

Three independent confirmations that the named file is 160 rows:

1. **The artefact**: `morris_sample.parquet` has shape **(160, 9)**.
2. **The arithmetic**: Morris gives `r(k+1)` rows; `20 × (7+1) = 160`.
3. **The code's own docstring**, `src/sampler.py:9` — "7 inputs, 20 trajectories,
   4 grid levels → **N = 20 \* (7 + 1) = 160 rows**". And
   `src/analysis_morris.py:10` states the sample is "**locked across all 8
   cells**", i.e. one 160-row design reused eight times.

1,280 is the number of **runs** (160 × 8 cells), not the number of rows in the
file the sentence names.

**Why this one is worse than its size.** It sits in the reproducibility recipe
and names a specific file with a specific expected shape. An independent
reproducer regenerates 160 rows, compares against a stated 1,280, and concludes
the reproduction failed. It is the one place in the document where a wrong number
actively misleads someone doing the right thing.

**Verified exact in the same sentence**: `trajectories = 20`, `levels = 4` and
`seed = 42` all match `src/sampler.py` (`seed: int | None = 42`), and the four
grid levels were independently confirmed today by the four distinct Vt values in
the S021 cohort (300, 466.7, 633.3, 800 mL).

### 22 — two legibility gaps in §S12, both statements accurate

Neither is an error. Both are places where a reader who counts gets a different
number than the text, with no bridge provided.

**(a) "all five run-level flags" (¶895) and "five-flag concordance" (¶897)**
against the main manuscript's "**four**-flag classifier", used 33 times. Measured:
`aggregated.parquet` carries five classification booleans — `clamped`,
`diverged`, `implausible`, `not_steady_state` **and `clean`**. The fifth is
`clean`. Correct, and nowhere stated.

**(b) "the 22-run S1_M pilot … 22/22 runs" (¶897) against "the 20 per-run output
CSVs" (¶899).** Measured: the canonical pilot holds 22 rows —
`S1_M_0000`--`0015` (16 Morris), `9001/9002/9081/9082` (4 probes), and
`9900/9901`. The last two carry `clamped=True, diverged=True, exit_code=1` and
**no `output.csv` on disk**: they are deliberate-clamp probes that Pulse rejects
at setup, exactly as §S3-clamp describes ("a setup rejection exits non-zero with
no CSV, so `diverged` fires instead"). So 22 runs minus 2 CSV-less rejections =
20 archived CSVs. Both reproduction archives hold exactly 20, and exactly those
20. Correct, and nowhere stated.

### 23 — two absence claims about the upstream Docker image (§S12 ¶903)

> the pinned base image `kitware/pulse:4.3.1` is published for `linux/amd64`
> **only** … (**no** prebuilt ARM64 image exists)

Two claims of exclusivity/absence about a third-party registry, uncited. Same
class as signals 1 and 20, and they trigger criterion (b) of the citation rule.
They are load-bearing: the whole ARM64 argument — that the Apple Silicon run is
emulated rather than native — rests on them.

**✅ VERDICT 2026-08-23 — SUPPORTED. Registry queried this session.**

Docker Hub API, `kitware/pulse` tags, read as **raw JSON** rather than through a
summariser:

- `"count":10` — the listing is complete, no pagination
- the ten tags are 3.0.0, 3.0.1, jupyter_3.0.1, 4.1.0, 4.2.0, **4.3.1**,
  8168c942, bfd8b1a, bfd8b1aJ, d7655177
- **ten `"architecture"` entries, every one `"amd64"`**
- **zero** occurrences of `arm64` or `aarch64` in the whole document

So "published for `linux/amd64` only" is exact, and no ARM64 image is published
in that repository.

⚠️ **Recommended repair anyway, and it is about scope, not truth.** "No prebuilt
ARM64 image exists" is an unbounded negative: the evidence covers the official
`kitware/pulse` repository, not every registry on earth. Bounding it costs
nothing and removes the only attackable part — e.g. "no ARM64 image is published
in the official `kitware/pulse` repository". This is the general treatment the
four absence claims need: **bound the claim rather than try to prove the
negative.**

**Recorded as a process failure of mine**: this verification was performed and
reported to the maintainer, but not written here for twenty minutes. A result
that lives only in conversation is not a result. Persist before reporting.

### §S12 — verified correct

- Hardware envelope in ¶815 matches the project's recorded machine exactly, down
  to "Windows 11 Home, version 25H2" and the CPU-only statement.
- Docker template in ¶821--836 matches the project's canonical template,
  including `MSYS_NO_PATHCONV=1`, `--memory=1g --cpus=3` and the `//data/...`
  double-slash forms.
- The 23 h 01 m coincidence in ¶817 is genuine and was already adjudicated:
  reference machine 23h01m12s (`data/runs/phase4a_run.log`), independent host
  23h01m21s (`audits/reproduction_check_2026-06-07.md:8`) — **9 seconds apart**.
  Register entry S-G-1, resolved 2026-07-24. The container times "approximately
  27 h" and "46 h" match the register's robust 27.4 h and its 27/46 pair.
- 382 ledger anchors and the T1.06u skip on a public clone are consistent with
  the ledger and with §S9's use of that same anchor.
- All three reproduction archives exist; the thinkpad one holds exactly the 20
  CSVs claimed.
- The 20 ms ODE timestep is consistent with the 0.02 s native sampling interval
  measured directly today.

**Not verified here**: the macOS `max|Δ| = 2.9×10⁻⁹`.

### Three older cross-document items, re-checked against the repository

`audit/factcheck_paper_supplement_vs_monograph.md` still lists P0-1, P1-1 and
P2-1 under "Medium (cross-document drift)". All three are **extinct in the
current text**, verified rather than taken on trust:

- **P0-1** ("three" vs "one/two" operator-actionable): every occurrence enumerated
  and displayed — 4 in `paper.tex`, all "two"; 5 in the monograph, all "two" or
  naming exactly F-003 and F-004; 0 in the supplement. No "three" anywhere.
- **P1-1** (Cornish channels "do not overlap"): the paper now reads "concentrated
  on … lie largely outside" at both loci; 0 occurrences of the old wording in
  paper or monograph.
- **P2-1** ("no flags raised"): 0 occurrences in all three documents.

⚠️ **A false alarm of mine, retracted.** A grep found "do not overlap" surviving
in `supplement.tex:43`. It is a **LaTeX layout comment** — "% S-prefixed
two-digit numbers (S10-S15) do not overlap the following title" — with no
relation to Cornish. The pattern matched a string, not a claim, and it was
announced before the context was read. Sequence to hold: match → read → *then*
characterise.


### 21 (extended) — the row/run confusion is twinned, and the paper contradicts itself

The first pass found one locus. Widening the net found a second, in the other
document. Recorded as its own block because the enumeration, not the first hit,
is the result.

**Method.** Wide net first: every spelling of 1,280 within 90 characters of a
word denoting the *sample* artefact (`row|sample|table of input|input
table|point|design|combination`), across all three documents, with a positive
control asserting the known locus is inside the net before any count is
believed. **13 windows. 2 defects. 11 correct.**

| document | locus | text | verdict |
|---|---|---|---|
| paper | **L402** | "the input sample (the **1,280-row** table of input combinations, regenerated from the fixed sampler seed)" | ⚠️ **defect** |
| supplement | **L884** | "The **1,280-row** Morris sample … matches the committed `morris_sample.parquet` byte-for-byte" | ⚠️ **defect** |
| paper | L198 | "The same **160-point** Morris design is executed in each of the eight cells"; "$8 \times 160 = 1{,}280$ simulations in total" | ✅ correct |
| paper | L258 | "0 / 1,280" | ✅ run count |
| supplement | L379 | "1,280 of 1,280 runs" | ✅ run count |
| monograph | L3592 | "`aggregated.parquet` (**1,280 rows** × all outputs + flags + meta)" | ✅ correct — that file *does* have 1,280 rows |
| monograph | **L3595** | "`morris_sample.parquet` (seed = 42, 20 trajectories, 4 levels ⇒ **160 unique input points**)" | ✅ **the ground truth, correctly stated** |
| monograph | L310, L813, L1245, L1290, L1910, L2010 | run counts | ✅ correct |

**The paper contradicts itself.** Its Figure 1 caption (L198) says the Morris
design is **160-point** and that 8 × 160 = 1,280; its Methods (L402) calls the
same object a **1,280-row** table. Two hundred lines apart, same document.

**The monograph already carries the right phrasing** and it is worth borrowing
rather than reinventing: *seed = 42, 20 trajectories, 4 levels ⇒ 160 unique input
points*.

**⚠️ A repair that must not drop the sampler parameters.** A candidate rewrite
discussed with the maintainer removed `levels = 4` and `seed = 42` while fixing
the row count. Those are the only two facts in the sentence that make the sample
regenerable; deleting the seed from a reproducibility recipe trades one defect
for a worse one. Both proposed repairs below keep them.

- **Supplement L884** → "The locked 160-row Morris sample — `trajectories = 20`,
  `levels = 4`, `seed = 42`, giving 20 × (7+1) = 160 input points — is
  regenerated deterministically from the SALib sampler and reused across all
  eight cells, yielding the 1,280 runs of the full sweep; the regenerated sample
  matches the committed `morris_sample.parquet` byte-for-byte."
- **Paper L402** → "the input sample (the **160-row** table of input
  combinations, reused across the eight cells and regenerated from the fixed
  sampler seed)".

**Class, for the guard phase**: this is a *unit* error — rows counted where runs
were meant. It is the same shape as the events-versus-configurations error
already recorded in this project's method notes, and it is the kind that recurs.
A guard should assert the row count of `morris_sample.parquet` against whatever
number the two documents print next to that filename.


### 24 — "because the underlying physiology is real" (§S13 ¶931)

> The SHAP cross-verification works because the underlying physiology is real,
> not the other way round.

**Two readings, and they are not equivalent.**

- *Engine-internal*: "the underlying physiology" = the dependencies Pulse
  actually implements, so the agreement reflects genuine input–output structure
  in the engine. Modest, defensible, almost certainly what is meant.
- *External*: "the underlying physiology" = human physiology, asserted as real
  and offered as the *explanation* of the agreement. That is an external-validity
  premise, and §S9's Figure S5 caption states in terms that "nothing here
  constitutes external physiological validation".

The second reading puts the sentence in direct conflict with a disclaimer
elsewhere in the same document. "Real" is doing load-bearing work without a
stated referent, and "not the other way round" leaves the reader to reconstruct
which direction is being denied.

Naming the referent would settle it — e.g. "…because the input dependencies Pulse
implements are genuine structure in the engine, not an artefact of either
method".

### 25 — "any reasonable statistical method" (§S13 ¶931) — DOWNGRADED

> …they correspond to input dependencies that **any reasonable statistical
> method** would identify on the same data.

**What survives.** A universal claim over an unbounded, undefined class
("reasonable"), extrapolated from a comparison of exactly **two** methods. That
is a wording defect, of the same family as signal 18's "each".

**⚠️ What I withdraw, and why it matters.** This entry first asserted that the
section's own numbers undercut the claim, citing the per-cell full 3-of-3
agreement of 23 of 48. **That objection does not hold.** Re-reading ¶929, which
immediately precedes the sentence, the author has already done the scoping work
explicitly:

- "The strong pooled-level agreement (17 of 18) **is the central
  cross-verification**"
- "The lower per-cell full-match rate (23 of 48) **is expected**", with the
  reason given (per-cell n of 42--144, and dependence on which trajectories
  landed clean)
- "The 92 % $\geq$ 2-of-3 agreement at the per-cell level **is the appropriate
  level of comparison**"

So "input dependencies" in ¶931 most naturally refers to the pooled dominant
dependencies the previous paragraph designated as central. Citing 23/48 against
it ignores scoping the author had already performed in the adjacent sentence.

**The error class, recorded because it is mine and it recurs**: I quoted a number
from the section against a sentence in the same section without reading the two
paragraphs as one argument. A figure is not a counter-example until the
neighbouring text has been read for the scope it already sets. The same
discipline as "characterise before explaining", applied to prose rather than
data.

**Consequence for the correction pass**: this is a light-touch rewording at most,
not a claim change. Something like "…dependencies that a second, observational
method recovers on the same data" would say exactly what was measured.

### §S13 — verified correct

All measured against `data/runs/full_sweep/aggregated.parquet`:

| claim | text | measured |
|---|---|---|
| `not_steady_state` total | 530 of 1,280 | **530** |
| clean subset | n = 663 | **663** |
| per-cell clean range | 42--144 | **min 42 (S1_F), max 144 (S3_M)** |
| ≥2-of-3 per-cell rate | 92 % (44 of 48) | 44/48 = **91.67 %** |

Per-cell clean counts in full: S1_M 49, S1_F 42, S2_M 87, S2_F 92, S3_M 144,
S3_F 122, S4_M 67, S4_F 60 — summing to 663.

The three agreement statistics (17/18, 23/48, 44/48) each carry a ledger anchor
(`T2.s023.pooled`, `T2.s023.fullmatch`, `T2.s023.ge2_pct`), so they are
re-derived at every gate run. The §S4 cross-reference is correct: that section
does decompose the 530 into three named sub-modes.

The epistemological framing in ¶915 — Morris as interventional, SHAP as
observational, the two answering different questions, SHAP kept explicitly
secondary — is careful and correct, and `TreeExplainer` is accurately described
as exact for tree ensembles rather than sampled.


### 26 — what §S14 says the monograph contains, against what it contains

§S14 ¶939 lists five things the companion monograph "carries", and ¶941 names
three more a reader might consult it for. Each was checked against
`preprint/manuscript.md` by section heading, not by keyword.

| # | claim in §S14 | where it lives in the monograph | verdict |
|---|---|---|---|
| 1 | "the **full preregistration document** with its amendment history" | §2.0 *Preregistered hypotheses* — which states it reproduces "**verbatim from `preregistration.md` §Primary hypotheses**"; amendments appear only as in-text notes (L519, L606, L816, L1121, L1196) | ⚠️ **overclaim** |
| 2 | "the **complete experiment-log entries** for every analytical decision" | Appendix A — *Experiment log **index***, 43 lines of `ID | Title`, stating the entries themselves are "in `experiments_log/santino/`" | ⚠️ **overclaim** |
| 3 | "the full bibliography with per-reference DOI / PMID verification trail" | §9 References + **§9.7 *Verified primary references (full bibliographic detail)*** | ✅ |
| 4 | "the per-experiment forensic chains … verified Pulse 4.3.1 limitations table" | §1.2 *Verified limitations of Pulse 4.3.1* + Appendix B | ✅ |
| 5 | "the full source-code map of the Pulse 4.3.1 audit" | **§B.4 *Source-code audit findings and discrepancies*** | ✅ |
| 6 | "per-experiment statistical-test selection rationale" | **§2.10 *Statistical methods overview*** | ✅ |
| 7 | "calibration trace for the empirical {0.26, 0.60, 0.95} ARDS-severity mapping" | **§B.3 *ARDS severity calibration and solver instability*** | ✅ |
| 8 | "the bit-exact reproduction protocol at the engine-binary level" | **§2.8 *Hardware and reproducibility*** | ✅ |

Six of eight are backed by a dedicated section. Two are not.

**Why the two matter.** They describe a **public deposit**. A reader who downloads
the Zenodo monograph expecting "the complete experiment-log entries" receives a
43-line index of titles, and expecting "the full preregistration document"
receives four hypotheses. Both are trivially checkable from outside.

**A defensible weaker reading exists**, and ¶941 supplies it: "the complete
experiment-log entries **it consolidates** are openly available under
`experiments_log/`". So the author's model may be *consolidates*, not *contains*.
But ¶939's verb is "carries", and a reader applies the literal one.

**Verified correct in the same section**: "over 100 pages" — the built monograph
is **118 pages** (`preprint/build/manuscript.pdf`). And the ARDS severities
{0.26, 0.60, 0.95} match the locked scenario definitions exactly.

**⚠️ Instrument failure of mine, recorded because it nearly produced a false
report.** A first pass searched the monograph for eight keyword patterns and
returned 1 hit for "statistical-test selection", 3 for "forensic chains" and
scattered hits for "source-code map" — which read as a *cluster of five
overclaims*. It was wrong. The section headings, read afterwards, located §2.10,
§B.4, §9.7, §B.3 and §2.8, each a dedicated home for the claim its keywords had
missed. **For a claim of the form "document X contains Y", the table of contents
is the instrument; a keyword search is not.** Absence of a phrase is not absence
of a section.


### 27 — "sampled uniformly from [50, 110] bpm" (§S15 caption)

Measured on all 1,280 runs: `in_hr` takes **four** values — **50, 70, 90, 110** —
with counts 336 / 320 / 304 / 320. That is the Morris 4-level grid, and the
counts are not even equal.

"Sampled uniformly from [50, 110]" invites a continuous-uniform reading, which
changes how a reader interprets the table's means and standard deviations. §S12
¶884 states `levels = 4` for the same sampler, so the two sections describe the
same design differently.

### 28 — the S3→S4 dip, and the confound the text does not mention (§S15 ¶979)

> …the overshoot is non-monotonic in severity: output HR peaks at S3 (moderate)
> and eases at S4 (severe), **plausibly reflecting incipient cardiovascular
> decompensation** at 95 % alveolar impairment…

The observation is real and exactly reproduced: 155.72 bpm at S3 against 147.06
at S4, a difference of **8.7 bpm**.

**But the two populations are not comparable in the way the sentence assumes.**
Clean-run survival by scenario:

| scenario | clean / 320 | rate |
|---|---|---|
| S1 | 91 | 28.4 % |
| S2 | 179 | 55.9 % |
| S3 | **266** | **83.1 %** |
| S4 | **127** | **39.7 %** |

S3's mean rests on 83 % of its cell; S4's on 40 %. A 43-point difference in
survival is a **selection effect** available to explain an 8.7 bpm difference,
and the text offers a physiological mechanism without mentioning it.

**What is and is not established here.** I have *not* shown that selection
explains the dip — that would need the flagged S4 runs' HR, which by construction
are not steady-state and so have no comparable mean. What is established is that
an alternative explanation exists, is quantified, and is unaddressed. "Plausibly"
hedges the mechanism but not the comparison.

The S1→S3 contrast is untouched by this: 73.8 against 155.7 bpm is far too large
for a selection effect of this size to account for.

### 29 — three flags named where four are claimed (§S15 ¶959)

> …all clean Morris runs (those passing the **four**-flag steady-state classifier
> without firing `diverged`, `implausible`, or `not_steady_state`)…

`clamped` is missing from the list. **Zero numerical consequence**: recomputing
the table both ways — with and without `clamped` in the exclusion — gives
identical values to two decimals in all four scenarios, because `clamped` is
0/1,280. A wording gap, not an error, and of the same family as signal 22(a).

### §S15 — the table is exact

| scenario | text | measured | n |
|---|---|---|---|
| S1 | 73.8 ± 20.4 | 73.77 ± 20.41 | 91 |
| S2 | 87.3 ± 24.3 | 87.33 ± 24.30 | 179 |
| S3 | 155.7 ± 34.7 | 155.72 ± 34.67 | 266 |
| S4 | 147.1 ± 31.8 | 147.06 ± 31.78 | 127 |

Eight values, eight exact. The "approximately 70 bpm overshoot above the
[50,110] midpoint" spans 75.7 (S3) and 67.1 (S4) — defensible for both.

### §S16 — swept, no signal, twelve values exact

Recomputed with the thresholds read from `src/detector.py`
(`DRIFT_MAX_DELTA_60S`), on the two arms the text defines:

| arm | n | HR | MAP | PaCO₂ | PaO₂ | Vt |
|---|---|---|---|---|---|---|
| hyperoxia (FiO₂ ≥ 0.95) | **195** | 2.56 → 2.6 % | 0.00 → 0 % | 3.59 → 3.6 % | 19.49 → 19.5 % | 8.72 → **8.7 %** |
| Vt-oscillation (Vt CV > 0.05) | **303** | 2.31 → 2.3 % | 0.66 → 0.7 % | 1.98 → 2.0 % | 7.26 → 7.3 % | — |

Medians also exact: 0.197 → "0.20 bpm", 0.049 → "0.05 mmHg", 0.575 → "0.58
mmHg", 4.312 → "4.3 mmHg"; and the 95th percentile 40.177 → "40.2 mmHg".

**A cross-section coincidence that is not one.** The hyperoxia arm's n = 195 is
the same 195 as §S3-clamp's "195 of them reach the ventilator action": the Morris
FiO₂ levels are 0.21 / 0.4733 / 0.7367 / 1.0, so "≥ 0.95" selects exactly
FiO₂ = 1.0, and 208 requesting minus 13 diverging before the action leaves 195.
The two sections agree exactly.

**Guard coverage, measured**: six anchors `T5.window.*` cover HR, MAP and PaCO₂ in
both arms — with thresholds read from `src/detector.py` rather than hardcoded,
and an assert that exactly six thresholds were parsed. `T2.f003.*` covers the
PaO₂ rate and both arm sizes. ⚠️ **The 8.7 % delivered-Vt rate in the hyperoxia
arm is covered by no anchor** (`8.7` appears zero times in `audit_claims.py`).
Correct today; a guard candidate, not a defect.

Not a defect either: the Vt-oscillation paragraph lists four channels and omits
Vt itself, which sits at 42.9 %. Vt is that arm's *defining* variable, so listing
it would be circular; the claim is about propagation to other channels.

### 30 — §S17's six recommendations are not §S11's six (¶1022)

Both say "six". They enumerate different sets.

| §S11 | §S17 |
|---|---|
| 1. **Structured input-rejection events** | ⚠️ **absent** |
| 2. Male `BloodVolumeBaseline` floor | 4. documentation of the male BV floor |
| 3. Reference SA recipe for operational inputs | 5. reference SA recipe for operational inputs |
| 4. Setup-time warning, ARDS band | 1. setup-warning for the ARDS instability zone |
| 5. Per-channel convergence diagnostic | 2. per-channel steady-state convergence diagnostic |
| 6. Field-attributed setup-error messages | 3. field-attributed setup-error messages |
| — | 6. ⚠️ **companion Morris / Sobol implementation** |

Item 1 is dropped; item 3 is split into two entries ("reference SA recipe" and
"companion Morris / Sobol implementation", both facets of §S11 item 3's single
paragraph). **The count survives only because the two errors cancel.**

The dropped item is the one `paper.tex:376` lists **first**, and §S17 states its
own purpose as an index "so that a skim reader, or an automated indexing agent,
can locate each finding in one place". A skim reader takes this list as the six.

### §S17 — verified correct, and one row better written than its own section

- "**Twelve** verified Pulse 4.3.1 limitations" ✅ — the §S2 table has **11
  physical rows for 12 limitations**, because the row labelled "5--6" carries two
  (HR init 50--110 bpm and RR init 8--20 bpm). A first count returned 10 because
  the pattern `^[0-9]+ &` cannot match `5--6 &`; the table was then read.
- 43 of 48 Sobol trigger, 1,500 vs 11,008 runs, Cornish's 15 channels, the
  200-run continuous-severity sweep, `[0.879, 0.945]`, three `not_steady_state`
  sub-modes — all consistent with what the cited sections state.
- "the **20-event** male-only divergence cluster" ✅ — the careful noun, matching
  this project's own events-versus-configurations rule.
- 💡 The §S13 row says the SHAP agreement confirms "the rankings are an **engine
  property** rather than an artefact of the elementary-effects design". That is
  precisely the referent **signal 24** finds missing from §S13's own ¶931. The
  index already contains the fix.


### 31 — the "minimal command sequence from a fresh clone" cannot run on a fresh clone

§S12 ¶842 introduces its listing as "**The minimal command sequence to regenerate
the canonical sweep + audit ledger from a fresh clone**". The listing is:

1. `uv sync`
2. `uv run python scripts/run_full_sweep.py`
3. `uv run python scripts/analyze_sweep.py`
4. `uv run python scripts/audit_claims.py`
5. `uv run python scripts/audit_claims.py --check-paper-sync`

**Step 2 cannot succeed on a fresh clone.** `scripts/run_full_sweep.py` delegates
to `src.runner.run_many`, and `src/runner.py:35` sets

```python
DEFAULT_IMAGE: str = "pulse-atlas-engine"
```

which is a **locally built** image, not one pulled from a registry. The step that
creates it exists — `engine/Dockerfile` is present, and `README.md:241` gives
`docker build -t pulse-atlas-engine engine/` — but §S12 never mentions it. No
pre-flight existence check was found in `src/runner.py`, so the failure surfaces
as a raw Docker error rather than a diagnostic.

**Directly relevant to outside reproduction**, which is what §S12 exists for: an
independent reproducer following the supplement literally stops at step 2.

**Verified present, so the repair is one line**: `pyproject.toml`, `uv.lock`,
`engine/Dockerfile`, `scripts/run_full_sweep.py`, `scripts/analyze_sweep.py`,
`scripts/audit_claims.py`, `scripts/make_figures.py`, `README.md` and `LICENSE`
all exist, and `--check-paper-sync` and `--check-monograph` are real flags of
`audit_claims.py`.

### 32 — the two public reproduction recipes diverge

| step | `README.md` L239–251 | §S12 ¶854–877 |
|---|---|---|
| build the Docker image | ✅ `docker build -t pulse-atlas-engine engine/` | ❌ absent |
| `uv sync` | ❌ (only in prose, for the optional `--extra ml`) | ✅ step 1 |
| run the sweep | ✅ **with `--resume`** | ✅ without |
| analyse | ✅ | ✅ |
| generate figures | ✅ `scripts/make_figures.py` | ❌ absent |
| audit ledger | ❌ absent | ✅ steps 4–5 |

Neither recipe alone regenerates what the paper releases. They are not in
conflict — each is a valid subset — but a community member will follow **one** of
them, and both are public-facing.

The README's `--resume` flag is worth keeping in whichever recipe survives: §S12
itself reports a 23-hour wall time, and the README explains that `--resume` makes
that crash-safe via per-run `run_meta.json`.

**Checked while comparing, and correct**: the README's `uv sync --extra ml` is
valid — `pyproject.toml` defines an `ml` extra with `scikit-learn>=1.5.0` and
`shap>=0.46.0`. A first look missed it because the listing was truncated, not
because it was absent.

### Reference integrity — checked mechanically, clean

Run with the **calibrated** citation pattern, the one that also matches
`\cite[Ch.~1]{key}`; the naïve form produced a false "2 uncited entries" in an
earlier session.

- `paper.tex` cites **37** keys, `supplement.tex` **24**, union **44**
- `paper.bib` defines **44**
- **0 cited-but-undefined** (a build breaker) · **0 defined-but-uncited**
- `preprint/references.bib`: 33 entries, 32 shared with `paper.bib`, and **0 DOI
  divergence** across the shared keys — the drift this project recorded three
  times is currently absent


### 32 — WITHDRAWN

The entry claimed the README omits the audit ledger and that neither public
recipe is complete. **Both halves are wrong.**

- `README.md:278–297` carries a dedicated section, *Verifying everything is
  wired up*, running `audit_claims.py`, `--check-paper-sync` and
  `--check-monograph`, with a three-layer table stating what each layer does
  **and does not** do. The ledger is not omitted; it is in a different section
  from the four-step reproduction block.
- §S12 promises "the canonical sweep **+ audit ledger**", not figures, so its
  omission of `make_figures.py` is inside its stated scope.
- The README's missing `uv sync` step is immaterial: its step 2 is
  `uv run …`, which resolves dependencies itself.

Nothing specific to this entry survives. What remains is entirely contained in
**signal 31**, whose defect is §S12's own completeness claim.

**How the error was made, since it is the second of its kind tonight**: I
compared the two recipes as *lists of commands* without reading what each
document *promises*. The same failure as the withdrawn half of signal 25 —
quoting a number or a list against a passage without reading the passage's own
scoping. Read the promise before comparing the delivery.

### 33 — a live acceptance criterion pinned to a stale count

`TODO_publication_roadmap.md:143`:

> `audit_claims.py --check-paper-sync --check-monograph` → **must stay
> 313/313 · 94/94 · 26/26 · 25/25** (currently green)

The ledger is at **382**. Every gate run in this session printed 382 anchors, and
`README.md` prints 381/382 and 382/382 correctly at five loci.

⚠️ **Not the same as L51**, which reads "Last run 2026-08-04. On a clean public
clone expect 312/313 …". That one is a **dated record** and legitimately keeps
its original value, per this checklist's own rule. L143 is an instruction for the
future, and it is wrong.

### 34 — the experiments-log range has drifted again

`README.md:357` prints "`santino/` **S001 … S031** entries (one .md each)".
Measured on disk: the highest entry is **S032**.

**This is a recurrence.** The same locus previously read "S001 … S025" and was
corrected to S031 on 2026-08-05. One new experiment later it is stale again.

### Why 33 and 34 drifted and the README's counters did not

The README's ledger counters are **correct** at all five loci — 381/382, 382/382,
26/26 — because they were wired to the ledger (`8cae68c`, "17 chiffres liés au
ledger"). The two values that drifted are precisely the two that **nothing
re-measures**: a prose range bound and a hand-written acceptance criterion.

That is this project's own rule restated by a fresh example: **finding a drift
means wiring a guard when nothing re-measures it.** A range bound of the form
`S001 … SNNN` and a counter target inside a TODO are both mechanically checkable.

### Anti-recurrence checklist — the rest came back clean

| check | result |
|---|---|
| 1. the retracted S018 value "2 / 20" | ✅ **zero occurrences** across all seven public files |
| 2. withdrawn vocabulary ("widely/most used", "increasingly used") | ✅ five hits, **all legitimate** — a dated archive warning in `pre_submission_inquiry.txt:21–24` and its archived body, a description of the withdrawal in the roadmap, and the house rule at `preprint_npj/README.md:104` that forbids the phrase |
| 2b. other retracted claims (FiO₂ crash, no sex-specific physiology, CO₂ narcosis, "clinical-AI training") | ✅ one hit, the house rule itself |
| 3. article title consistency | not separately tested in this pass |
| 4. range bounds | ⚠️ **signal 34** |
| 5. full read of each file | README read in the sections the checklist targets; not line-by-line end to end |

**Files covered**: `README.md`, `CITATION.cff`, `preprint_npj/cover_letter.md`,
`preprint_npj/submission_metadata.txt`, `preprint_npj/pre_submission_inquiry.txt`,
`TODO_publication_roadmap.md`, `preprint_npj/README.md` — all seven present.

⚠️ **Two checklist points are not fully discharged** and are marked rather than
claimed: title consistency across loci (point 3), and the full end-to-end read of
each file (point 5) — the checklist warns that the two S018 defects sat at lines
155 and 420 of a 475-line file, so a targeted read is not a substitute.


## Visual figure pass — 9 remaining figures inspected against their captions (2026-08-23)

The only blind spot no guard covers: **what the pixels show versus what the
caption says.** Figures 1 and 2 and four of Figure 3's six panels had been done
earlier; this pass closes the remaining nine. Each figure PDF was rendered to PNG
at 140 dpi and read.

| figure | verdict |
|---|---|
| **Fig. 3 panel PaO₂** | ✅ OK |
| **Fig. 3 panel PaCO₂** | ✅ OK |
| **Fig. 4** `fig03_actionable_corrections` | ✅ OK |
| **Fig. 5** `fig04_sex_bv_mechanism` | ✅ OK |
| **Fig. S1** `fig_s1_continuous_severity` | ✅ OK (but surfaced signal 38, in the README) |
| **Fig. S2** `fig_s2_spearman` | ✅ OK |
| **Fig. S3** `fig_s4_vt_waveform` | ✅ OK — **tonight's window fix is visible** |
| **Fig. S4** `fig_s3_hyperoxia_convergence` | ✅ OK |
| **Fig. S5** `fig_s5_decomposition` | ⚠️ **signal 35** |

**What the images independently confirmed** — each of these was measured from
data earlier and is now corroborated by the picture:

- Fig. 3 PaO₂: the **three blank FiO₂ cells are exactly S1_M, S1_F, S4_F**, the
  same three the data showed as short an input. FiO₂ dominant in all four S2/S3
  columns; magnitude collapsing 133/147 → 31 in S4.
- Fig. 3 PaCO₂: **Vt first and RR second in all eight cells**, an order of
  magnitude above the third input — exactly the two terms of
  $\dot{V}_A = \mathrm{RR}(V_T - V_D)$.
- Fig. 4a: the extreme point sits at x ≈ 1.83, y ≈ 0.02 — **S1_F_0117, 1.826 →
  0.018**. Every point below the diagonal.
- Fig. 4b: legend **44 + 8 + 8 = 60**; annotation "**779-1408 mmHg**", the exact
  runaway range measured; S3 and S4 clusters far below the 600 line.
- Fig. 5a: bars **4 · 4 · 4 · 8** male, **0** female; labels say "S2 (**mild**
  ARDS)", so the figure is on the correct side of signal 8.
- Fig. 5b: **20/20 → 0/20 → 0/20**. The retracted "2/20" is absent. And the
  female-default line is drawn **left of** the male floor, encoding the 86 mL
  shortfall geometrically.
- Fig. S1: the per-bin counts are **per sex** (100 + 100 = 200), as the caption
  and the table header both state.
- Fig. S2: **all twelve ρ values match `spearman_mu_star.csv` exactly**; S1 and
  S4 rows blank; min 0.75, max 1.00.
- Fig. S3: x-axis now reads **60–120 s recorded time**; trace min ≈ 136 and max
  ≈ 1180 mL; both panels on one y-scale, so the contrast is not inflated.
- Fig. S4: y-axis **[350, 760]**; median from **≈ 552** to **≈ 639**; three
  traces exiting the top; both reference lines at 600 and ≈ 663.
- Fig. S5: all eight hard-failure rates; only S4_M above the 30 % line; the
  **232 / 303 / 133** anchors visible and correctly placed, with the recorded
  inner bar for Vt drift visibly tiny against 133; **23 + 9 + 9 + 7 = 48**;
  glyphs present for greyscale; traffic-light colours not reused.

### 35 — "detector" baked into the Figure S5 legend

`make_supp_fig_s5_decomposition.py:137`:

```python
label="as recorded by the detector" if j == 0 else None
```

That string is rendered into `fig_s5_decomposition.pdf` and appears in the
supplement's printed legend.

**Why no existing check sees it.** `check_detector_vocabulary` sweeps
`paper.tex` plus `preprint_npj/figures/*.tex`, and its own comment records the
scope decision verbatim: *"Supplement figure sources are deliberately NOT swept:
the defect was at the paper/externalised-figure boundary, and an instrument
should stay the size of the claim it protects."* A `grep` of `supplement.tex`
cannot find it either — the word is in a PDF, not in the LaTeX.

**This is the Figure 1 defect recurring one scope out.** The same guard's comment
describes that precedent: the flowchart's boxes "read 'Four-flag steady-state
detector' … for weeks, without this check ever seeing them". The repair then
widened the corpus to `.tex` figure sources. Python-generated **supplement**
figures were left outside it.

**Distinct from signal 3**, which is four prose uses in §S3. This one is in an
image, so no textual sweep of the supplement will ever surface it.

**Guard candidate, and a cheap one**: extend the corpus to the figure
*generators* — `scripts/make_*fig*.py` — rather than only to `.tex` sources.


### 37 and 38 — loci recounted, after two errors of mine in five minutes

Both entries were first written from a single hit and a single comparison. Both
counts were wrong, in **opposite directions**. The corrected populations:

#### 37 — "34 … at FiO₂ = 1.0"

| locus | wording | verdict |
|---|---|---|
| `paper.tex:323` | "on 34 of the 126 … and **91 % of these excursions** occur at FiO₂ ≥ 0.95" | ✅ |
| monograph **L140** | "in **34 of 126** … ; **91 %** at FiO₂ ≥ 0.95" | ✅ |
| monograph **L2674** | "**34 of 126** … with **91 % of those** at FiO₂ ≥ 0.95" | ✅ |
| `supplement.tex:339` | carries the full decomposition — see below | ✅ **canonical** |
| `README.md:161` | "34 … **at FiO₂ = 1.0** (91 % at ≥ 0.95)" | ⚠️ self-contradicting |
| monograph **L320** | "600 mmHg **at FiO₂ = 1.0 in 34** … (91 % at ≥ 0.95)" | ⚠️ self-contradicting, identical shape |
| monograph **L71** | "600 mmHg **at FiO₂ = 1.0 in 34 of 126**" | ⚠️ over-attributes, no contradicting parenthetical |

**Three defective, four correct — and the monograph states it both ways, twice
each.** That is useful rather than alarming: a canonical formulation already
exists inside the same document, so the repair is propagation, not invention.

**`supplement.tex:339` is the best source of all**, because it carries the
decomposition rather than a summary: "**32 of the 34** … become physiologically
clean (**31 at FiO₂ ≥ 0.95**; **21 on the female and 11 on the male**); the
remaining **two** are healthy-female runs at maximal minute ventilation (**Vt 800
mL × RR 20 = 16 L/min**)". Checked: 21 + 11 = 32 ✓, 32 + 2 = 34 ✓, and 1 + 2 = 3
at FiO₂ = 0.737, which is exactly the 31/3 split measured from the data. Its
run-specific alveolar computation also checks: 0.737 × (760 − 47) − 16.2/0.8 =
**505.3** ✓.

⚠️ **A false alarm of mine, caught before reporting**: "31 at ≥ 0.95; 2 remaining"
looked like 31 + 2 = 33 ≠ 32. It is not a partition — the 31 is a *subset of the
32*.

#### 38 — "divergence approximately sex-balanced"

**⚠️ The first entry claimed this was README-only. Then a string count across the
corpus made it look like a seven-locus claim spanning all four documents. Both
were wrong.** "Sex-balanced" carries **two unrelated meanings**:

| sense | loci | status |
|---|---|---|
| a **sex-balanced synthetic cohort** — a design goal | `paper.tex:342`, `supplement.tex:1021` | ✅ **not this claim at all** |
| divergence rates **approximately sex-balanced** — an empirical claim | `README.md:108`, `README.md:156`, monograph **L338**, **L2007**, **L2231** | ⚠️ **the signal, 5 loci** |

So the paper and supplement are clean, and the drift is README + monograph.

**Why it is a defect**: the Figure S1 caption states "**Female divergence
dominates the lower band; male divergence dominates the upper band**". That is a
sex effect that **reverses sign** across the band, and "approximately
sex-balanced" reads as *no effect*. `README.md:108` is partly self-correcting —
it appends "the sex effect is regime-dependent" — while `:156` leaves the claim
bare. `paper.tex` says only "both sexes diverge", which is neutral and correct.

**The lesson, stated so it is not over-generalised**: a shared string never
establishes a shared claim. Compare the whole proposition and its referent. Three
times tonight a string count was mistaken for a claim count — "do not overlap",
then this entry twice.

### Guard design constraint for signal 35, recorded before anyone builds it

Scanning `scripts/make_*fig*.py` wholesale **would fail on the very file it is
meant to protect**: `make_supp_fig_s5_decomposition.py` contains "detector"
twice — at **L137** inside a rendered `label=`, and at **L15** inside a
**docstring that is never drawn**.

The instrument must therefore read only string constants that reach a drawing
primitive — `label=`, `set_title` / `title` / `suptitle`, `set_xlabel` /
`set_ylabel` / `xlabel` / `ylabel`, `text`, `annotate`, tick labels — extracting
constants recursively from the passed expression, so that

```python
label="as recorded by the detector" if j == 0 else None
```

is caught inside its `IfExp` while the docstring is ignored. **Calibration the
guard must pass before it is trusted**: L137 as it stands → FAIL; L15's docstring
→ PASS; the corrected L137 → PASS; and `detector` re-injected into any `label=`
→ FAIL.


### 1 — BioGears absence claim, arbitrated four ways (2026-08-23)

The sentence bundles **four** sub-claims under one "not present in BioGears".
They do not share a status, so no single rewrite can carry them.

> Pulse v4.3.1 includes **respiratory calibration for ventilated patients**,
> **mechanoreceptor feedback**, **lung-recruitment modelling**, and **improved
> hemorrhage response** that are not present in BioGears.

| sub-claim | verdict |
|---|---|
| mechanoreceptor feedback | ✅ **SUPPORTED on the examined corpus** |
| lung-recruitment modelling | ✅ **SUPPORTED on the examined corpus** |
| respiratory calibration for ventilated patients | ⚠️ **SOURCE INSUFFICIENT** |
| improved hemorrhage response | ⚠️ **OVERCLAIMED** |

**Corpus examined, named so the verdict can be re-tested.** BioGears primary
sources, fetched this session: four system implementations from
`raw.githubusercontent.com/BioGearsEngine/core/master` — `Respiratory.cpp`
(149 KB), `Nervous.cpp` (82 KB), `Cardiovascular.cpp` (130 KB), `Drugs.cpp`
(83 KB) — plus four methodology pages from `biogearsengine.com`.

**Calibrated before being believed**: `chemoreceptor` returns **30** in
`Nervous.cpp` and 15 in the nervous methodology page; `hemorrhage` returns **21**
in `Cardiovascular.cpp` and 48 in its documentation. The instrument finds what is
there.

| term | Pulse `RespiratoryModel.cpp` | BioGears, all four sources |
|---|---|---|
| mechanoreceptor | **18** (`m_MechanoreceptorsDyspneaFactor`, `targetTidalVolumeMechanoreceptorMultiplier` at L1445) | **0** |
| recruit | **16** (`recruitedFraction`, `recruitmentScalingFactor`, `recruitment`) | **0** |

**Why "improved hemorrhage response" is overclaimed, and it needs no external
source to see.** An *improvement* cannot be "not present in" the system it
improves. BioGears plainly models hemorrhage — 21 occurrences in its
cardiovascular implementation, 48 in its documentation. Only the *revision* is
Pulse's. The sentence tests the wrong property.

**Why the ventilated-patient calibration is source-insufficient.** It is not a
feature-presence claim but a calibration claim, and it does not reduce to a term
search. BioGears has ventilation — "ventilat" returns 52 on its respiratory page.
Presence of ventilation neither proves nor disproves a calibration specific to
ventilated patients.

⚠️ **Scope, stated rather than implied**: four system files of a larger
repository, plus four documentation pages. Supported *on the corpus examined* is
not proof of absence across BioGears' whole history.

⚠️ **A near-miss recorded with the finding.** A web-search summary for these
terms returned a confident description of BioGears mechanoreceptor feedback and
lung recruitment — text that in fact came from the **Pulse** pages returned by
the same query. Fetching the BioGears page directly gave **0** for both. A search
summary that mixes two sites cannot settle a claim about one of them.


### README read line by line, 2026-08-23 -- 5 signals raised, 5 suspicions dissolved

All 491 lines read, not grepped. **The dissolutions are recorded with the
findings**, because each was a plausible defect that a later reader would
otherwise re-raise, and each was killed by opening the full source rather than a
truncated window.

| suspicion | why it is NOT a defect |
|---|---|
| README cites "S4.5" for two different contents (L114 traffic-light deviation, L234/L427 SHAP) | **Two different documents.** `paper.tex` S4.5 = "Traffic-light curation map"; monograph S4.5 = "Limitations", and the SHAP cross-check is indeed there (`manuscript.md:3371`). Confirmed independently by `supplement.tex:343`, which resolves the main-text pointer to 4.5 for the traffic light |
| 23 h 01 m attributed to the reference machine at `supplement.tex:817` and to Y.M.'s AMD host at `:895` | **The supplement flags its own coincidence**: L817 reads "once on the independent host ..., whose elapsed time, **by coincidence, also totalled 23 h 01 m**". Read on a 300-character window this looked like a contradiction; read whole it is a deliberate note |
| `README.md:138` sends the reader to "Table 1 -- failure breakdown per scenario x sex" -- signal 5's defect | **Correct here.** The monograph's Table 1 (`manuscript.md:1557`) *is* "Per-cell flag counts", and the README refers to the monograph throughout. Signal 5 stays what it was: the *supplement* pointing at "Table 1 **of the main manuscript**" |
| `README.md:353` says "Figures 1-6" where `figures/` holds 11 PDFs | Figure 2 has six per-output variants (`fig02_morris_mu_star_{HR,MAP,PaCO2,PaO2,SpO2,Vt}.pdf`). 6 numbers, 11 files -- the numbering is right |
| "F-001..F-013" | Exact: `preprint/interim_findings.md` reaches F-013 |

**Also checked and exact**: `README.md:231`'s "~27-46 h of aggregate Pulse
container time" matches `supplement.tex:817` verbatim (27 h reference, 46 h
independent host); the 382 / 381+1-skipped / 94 / 26 audit figures; H1's median
0.928 and range 0.658-0.998; H4's 5-of-24 with the 6-to-5 BH demotion of S2 SpO2;
264 / 1,280 = 20.6 %; the 643-vs-663 mmHg hyperoxia pair.

**Signal 34 gains three loci**: `README.md:357` and `:384` both say "S001 ...
S031" where `experiments_log/santino/` reaches **S032**, and `:431` calls S025
"(this release)".

⚠️ **Signal 39 is the one that matters** and it is a *factual* claim, so nothing
is corrected here. It is also the first number a reviewer meets --- `README.md:31`
budgets "~9-23 h on a laptop" in the **For peer reviewers** block --- and that
range excludes the monograph's own ~7 h.


### 39 -- re-derived from the run metadata, which overturns my own first report

⚠️ **I first reported this as the monograph's ~7 h being the outlier against a
coherent README/supplement ~14 h. That was wrong: both are impossible.** The
error came from arbitrating between two prose claims instead of re-deriving the
quantity. Recorded because the correction is the finding.

**What settled it.** Every run directory carries `run_meta.json` with
`wall_time_s`, which `src/runner.py:138-162` computes as `time.monotonic()`
around the `subprocess.run` of the `docker run` invocation -- i.e. per-container
wall clock, exactly the quantity the supplement calls "Pulse container time".

**Provenance checked before the numbers were believed**: all 1,280 metadata files
are dated **2026-04-26**, a single execution, matching the canonical sweep date.
`--resume` skips completed runs without rewriting their metadata, so no later
re-execution could have contaminated the tree. 1,280 / 1,280 carry the field;
none missing.

**Two independent instruments, identical result**: a JSON parse over the tree,
and a raw text extraction with no JSON parser. Both give n = 1,280, 148,038 s,
**41.12 h**, mean 115.7 s per run.

| claim | locus | verdict against the data |
|---|---|---|
| "approximately 27~h per sweep on the reference machine" | `supplement.tex:817` | ⚠️ **measured 41.12 h** |
| "~7 h" wall at two workers | `manuscript.md:1271`, `:3314` | ⚠️ **below the 20.56 h floor** |
| "~14 h on the canonical laptop with 2 workers" | `README.md:229`, `supplement.tex:858` | ⚠️ below the floor |
| "~9 h with 3" | `README.md:229`, `supplement.tex:859` | ⚠️ below the 13.71 h floor |
| "~9-23 h on a laptop" | `README.md:31`, `:228` | ⚠️ only the top of the range survives |
| "wall time 23~h~01~m" | `supplement.tex:817`, `:895` | ✅ **consistent** -- 20.56 h ideal plus idle across resume points |
| "46~h on the slower independent host" | `supplement.tex:817` | not re-derivable from this tree; plausible for slower hardware |

⚠️ **The floor is a floor, not an estimate.** Wall time at *w* workers is at least
aggregate / *w*, because no schedule packs better than perfect. 20.56 h at two
workers is therefore a hard lower bound, and 7 h and 14 h are not merely
optimistic -- they are arithmetically unreachable given the recorded per-run
durations. The sweep is described as starting at three workers and dropping to
two mid-run, which places its true wall time between 13.71 h and 20.56 h plus
idle. **The canonical sweep's own wall time appears to be recorded nowhere; every
figure for it in the corpus is an estimate.**

**A substantive by-product, offered but not acted on.** The cost is extremely
concentrated: **S4_M alone is 18.45 h of the 41.12 h, 44.9 % of all container
time**, at a mean of 415.2 s per run against 42-106 s in the other seven cells.

| cell | aggregate | mean/run |
|---|---|---|
| S1_F | 1.87 h | 42.2 s |
| S1_M | 2.12 h | 47.7 s |
| S2_F | 3.24 h | 72.9 s |
| S2_M | 3.13 h | 70.3 s |
| S3_F | 3.64 h | 82.0 s |
| S3_M | 3.96 h | 89.0 s |
| S4_F | 4.71 h | 106.0 s |
| **S4_M** | **18.45 h** | **415.2 s** |

That is the severe-ARDS male cell -- the same cell holding all 20 solver
divergences and the worst traffic-light row. Compute time rising ~4x there is
consistent with a solver struggling, and would be an independent quantitative
signal of the same phenomenon. ⚠️ **Whether that belongs in the paper is a
scientific-content decision and is not taken here.**


### 39 -- rewritten a third time, and this time against a decontaminated aggregate

⚠️ **I got this wrong twice, in opposite directions, and the second error made the
maintainer abandon a correct answer.** The sequence is recorded because the
failure mode is the finding.

1. First report: "the monograph's ~7 h is the outlier; README/supplement's ~14 h
   is coherent." Built by arbitrating between two prose claims.
2. Second report: "re-derived 41.12 h aggregate, so ~7 h, ~9 h, ~14 h are *all*
   below the floor and the 27 h is wrong too." Built by summing `wall_time_s`
   over 1,280 runs **without inspecting the distribution**.
3. This one: the 41.12 h was contaminated. **The maintainer's original arbitration
   was right all along.**

**What contaminated it.** Exactly two runs of 1,280 exceed the 600 s timeout:

| run | `wall_time_s` | exit | `output.csv` |
|---|---|---|---|
| `S4_M_0122` | 107.375 s | 0 | 26 lines |
| **`S4_M_0123`** | **24{,}722.295999999973 s** | 0 | 26 lines |
| **`S4_M_0124`** | **24{,}722.281999999960 s** | 0 | 26 lines |
| `S4_M_0125` | 106.359999999986 s | 0 | 26 lines |

The two anomalies differ by **14 milliseconds after 6.87 hours**. Two independent
Docker containers do not finish 14 ms apart; two processes **frozen and resumed
together** do. `src/runner.py:113` sets `timeout_s = 600.0` and passes it to
`subprocess.run(timeout=...)`; a 24,722 s run should have been recorded as
`exit_code = 124`. It was not, which is only possible if the interpreter enforcing
the timeout was suspended alongside its children. Two runs in flight also matches
the documented drop "from three mid-sweep to two".

**Decontaminated, with the two artefacts imputed at the healthy mean:**

| quantity | measured | what the corpus says | verdict |
|---|---|---|---|
| aggregate container time | **27.43 h** | "approximately 27~h per sweep on the reference machine" (`supplement.tex:817`) | ✅ **correct** |
| floor at 2 workers | **13.72 h** | "~14 h with 2" (`README:229`, `supplement.tex:858`) | ✅ **correct** |
| floor at 3 workers | **9.14 h** | "~9 h with 3" (`README:229`, `supplement.tex:859`) | ✅ **correct** |
| -- | -- | "~9-23 h on a laptop" (`README:31`, `:228`) | ✅ **correct** |
| -- | -- | "46~h on the slower independent host" (`supplement.tex:817`) | ✅ consistent: 46 / 2 = 23 h = its own observed 23~h~01~m |
| -- | -- | "wall time 23~h~01~m" (`supplement.tex:817`, `:895`) | ✅ correct |
| -- | -- | **"~7 h" (`manuscript.md:1271`, `:3314`)** | ⚠️ **below both floors -- the only defect** |

**Signal 39 therefore shrinks from seven loci to two, all in the monograph.**
README, supplement and `paper.tex` are correct and must not be edited.

### The canonical sweep's wall time, recovered -- a third independent confirmation

Earlier versions of this entry said the canonical sweep's own wall time was
recorded nowhere. **It is recoverable from the metadata timestamps.** Every
`run_meta.json` under `data/runs/full_sweep/` is dated 2026-04-26; the first was
written at **00:01:41** and the last at **20:48:21**, an elapsed span of
**20.78 h**. Subtracting the 6.87 h host suspension leaves **~13.9 h of actual
elapsed running time**, against a computed floor of **13.72 h at two workers** --
a 98.6 % packing efficiency, and an independent confirmation of "~14 h with 2"
arrived at without using the aggregate at all.

Three routes now agree: the decontaminated aggregate divided by two workers
(13.72 h), the timestamp span minus the suspension (13.9 h), and the prose in
`README:229` and `supplement.tex:858` (~14 h).

⚠️ **Trust conditions for the timestamp route, stated rather than assumed**: it
holds only if the mtimes are original. `data/runs/` is gitignored, so git never
rewrote them, and the spread is a plausible single working day. It measures
first-write to last-write, so it omits the first run's own duration (~40 s,
negligible). And exactly two runs carry inflated durations, which is what fixes
the concurrency during the suspension at two -- had three workers been active,
three runs would show it.

⚠️ **What remains genuinely unrecorded** is narrower than before: the split
between the three-worker and two-worker phases. The sweep is described as
starting at three and dropping to two; the measured 13.9 h sits almost exactly on
the all-two-worker floor, which suggests the three-worker phase was short, but
nothing in the repository pins it.

**The 23~h~01~m figures still belong to the two re-executions**, not to the
canonical sweep. `supplement.tex:817` says so explicitly
("the canonical sweep, **and** a later re-execution logged at 23~h~01~m"), so a
repair writing "23 h 01 m observed wall time on the canonical execution" would
introduce a **new** factual error.

### S4_M -- the finding is fully withdrawn

**There is no compute concentration.** With the two suspension artefacts removed,
S4_M costs **4.72 h** against S4_F's **4.71 h** -- mean 107.5 s vs 106.0 s, median
106.7 s vs 104.0 s. Twins.

| cell | aggregate | mean | median |
|---|---|---|---|
| S1_F / S1_M | 1.87 h / 2.12 h | 42.2 s / 47.7 s | 40.9 s / 43.2 s |
| S2_F / S2_M | 3.24 h / 3.13 h | 72.9 s / 70.3 s | 71.3 s / 67.5 s |
| S3_F / S3_M | 3.64 h / 3.96 h | 82.0 s / 89.0 s | 80.4 s / 84.2 s |
| S4_F / S4_M | 4.71 h / **4.72 h** | 106.0 s / **107.5 s** | 104.0 s / **106.7 s** |

The "44.9 % of aggregate compute", the "5.70x", the "4x" and the reading
"consistent with a solver struggling" are **all withdrawn**. They were the shadow
of a laptop going to sleep. Nothing goes to the paper, nothing goes to the
supplement, and the hedged descriptive sentence drafted for the audit is
withdrawn too, because its premise is false.

⚠️ **Two independent facts killed the mechanistic reading before the artefact was
even found**, and both should have stopped it: the 20 divergent runs total
**0.47 h** at a mean of **84.8 s**, i.e. they are *faster* than the sweep mean of
116.1 s -- divergence is cheap, it fails fast; and the ratio of **medians** was
1.46x where the ratio of means was 5.70x. The maintainer's instruction to
harmonise the statistic was correct and I dismissed it as already-harmonised.

**What the cell table does show**, cleanly and symmetrically, is a severity
gradient: ~2 h at S1 rising to ~4.7 h at S4, about 2.5x, with the two sexes
within a few percent at every severity. That is unremarkable and not a finding.

### 44 -- the suspension artefacts, as a data-integrity item

The scientific outputs are **verified unaffected**, and not by inspection:
`manuscript.md:1297-1300` records the S015 re-execution comparing SHA-256 of every
`output.csv` against canonical, giving **1,260 / 1,280 bit-identical clean runs
and 20 / 20 diverged runs reproducing divergence**. 1,260 + 20 = 1,280, and both
artefact runs carry `exit_code = 0`, so both are inside the bit-identical 1,260.
The suspension corrupted the timing metadata only.

⚠️ **But `timeout_s = 600.0` silently failed to bound anything**, and no artefact
in the repository records that two runs exceeded it by a factor of 41. Whoever
next re-derives compute cost from `run_meta.json` -- as I just did -- gets 41.12 h
instead of 27.43 h, a 50 % overstatement, with no warning.


### 39 / 44 -- maintainer's decisions of 2026-08-23, and three measurements they forced

The maintainer settled (a) wording, (b) guard design, (c) public disclosure.
**Two of the three needed correcting, and the corrections came from measurements
their own phrasing forced.**

**(a) -- one factual error in the proposed sentence.** The draft reads "the
canonical **two-worker** execution". `manuscript.md:3315` describes the sweep as
three workers "lowered from three mid-sweep to control thermal load". Calling it a
two-worker execution would put a new defect inside the sentence written to remove
one. It also forward-references "a **documented** host suspension", which is not
documented anywhere yet -- so (a) **depends on (c)** and cannot be written first.

**Only one suspension occurred, which is what makes the singular safe.** The
healthy maximum across 1,278 runs is **141.7 s**; there are **zero** runs between
150 s and 600 s. The distribution jumps from 141.7 s straight to 24,722.3 s. The
eight longest healthy runs are 132.1, 132.3, 133.2, 133.5, 133.8, 133.9, 134.6,
141.7 s -- a tight tail with no second population. A suspension shorter than a few
seconds would be invisible, which is immaterial against a 14 h figure.

**(c) -- the conclusion is right; the stated mechanism is not, and the correction
makes it more urgent, not less.** The maintainer argued the note is needed because
"les `run_meta.json` sont publics". They are **not**: `.gitignore:22` covers
`data/runs/**/run_meta.json`. But **`data/runs/full_sweep/aggregated.parquet` is
git-tracked**, carries 1,280 rows and a **`wall_time_s` column**, and on the public
clone `df.wall_time_s.sum() / 3600` returns **41.12 h** against a published ≈27.4 h.
The exposure is real and present on any clone today -- it does not wait for the
Zenodo deposit. Contaminated rows: `S4_M_0123`, `S4_M_0124`.

| derivation on the public parquet | value |
|---|---|
| naive sum | **41.12 h** |
| excluding the two artefacts (n = 1,278) | **27.39 h** |
| imputing the two at the healthy mean | **27.43 h** |

Both treatments round to **27.4 h**, and both give ≈13.7 h at two workers and
≈9.1 h at three. **Exclusion is preferable**, because it matches the disclosure
sentence's own verb and needs no imputation rule; the runtime aggregate is then
over n = 1,278 while all 1,280 runs stay in every scientific analysis.

**(b) -- adopted unchanged, and it is better than what I proposed.** I suggested
excluding runs above the timeout from cost computations. The maintainer's design
**fails** the computation unless the run is explicitly qualified as
timing-contaminated, on the grounds that a silent drop would let the instrument
erase the very performance regression it exists to detect. That is correct and the
weaker design should not be built.

⚠️ **The guard has no existing home.** `audit_claims.py` contains zero occurrences
of `wall_time`, `container-hour`, `aggregate container` or `elapsed`: the 27.4 h,
14 h and 9.1 h figures are currently guarded by nothing at all. Per the repository's
own rule -- a guard once there is more than one number -- this is a guard with its
own counter, not a ledger anchor.

**Calibration, with the negative control measured rather than assumed**: positive
controls are the two 24,722.3 s runs, which must FAIL while unqualified and PASS
once qualified; the negative control is **141.7 s**, the true healthy maximum,
which sits 4.2x below the 600 s timeout and must never fire. The timeout must be
read from `src/runner.py`, not duplicated as a literal.

**S4_M**: agreed, nothing published, no ratio, no mechanism.

⚠️ **Nothing applied.** (a) is blocked on the maintainer confirming the corrected
wording, and blocked behind (c) regardless.


### 39 -- diffs prepared, not applied (2026-08-23)

Arithmetic re-verified to the millesimal before drafting: span 20.777 h, minus a
suspension inflation of 6.837 h (24{,}722.296 s recorded against a 107.5 s healthy
mean), gives **13.940 h** active elapsed. The maintainer's 13.9 h is exact.

**The "two-worker" objection is withdrawn.** Locus 2 already reads "with two
parallel Docker workers (**lowered from three mid-sweep** to control thermal
load)". The proposed wording restates the existing detail in the other order; the
objection only ever applied to the bare phrase without the qualifier.
`paper.tex:402` independently says "**2--3 parallel Docker workers**", the safest
form of all, and is untouched.

**Order is (c) then (a)**, because (a) cites a note that (c) creates.

**(c) -- supplement `\S`S12, appended after the three-executions sentence at L817:**

> Two otherwise valid runs (`S4_M_0123`, `S4_M_0124`) carry wall-time metadata
> spanning a suspension of the reference machine and are excluded from the runtime
> aggregation; a naive sum over all 1,280 records in `aggregated.parquet` returns
> 41.1 h instead. Their simulation outputs are unaffected and are retained in every
> scientific analysis.

Two refinements on the maintainer's draft: "**documented** host suspension" is
self-referential inside the section that documents it, so it becomes "a suspension
of the reference machine"; and the two identifiers **plus the 41.1 h** are stated
in-line, which is what makes the 41.1 -> 27.4 derivation reproducible without
leaving the document -- the maintainer's own stated requirement.

**(a) locus 1 -- `manuscript.md:1271`, in the terse `\S`2.8 register:**

> ~~Wall time for the full sweep ~ 7 h on this hardware.~~
> The full sweep consumed ~ 27.4 aggregate container-hours and required ~ 13.9 h of
> active elapsed time on this hardware, after excluding the host suspension
> documented in Supplement S12.

**(a) locus 2 -- `manuscript.md:3314-3316`:**

> ~~The 1,280-run sweep took ~7 h on the maintainer's i5-11400H laptop with two
> parallel Docker workers (lowered from three mid-sweep to control thermal load;
> resume-safe).~~
> The 1,280-run sweep consumed ~ 27.4 aggregate container-hours and required
> ~ 13.9 h of active elapsed time on the maintainer's i5-11400H laptop, using three
> parallel Docker workers reduced to two mid-sweep to control thermal load
> (resume-safe), after excluding the host suspension documented in Supplement S12.
> The aggregate gives a theoretical ~ 9.1 h lower bound under ideal three-worker
> parallelism.

⚠️ **"Theoretical lower bound" is the right term and beats my "would project to".**
The makespan lower bound for n jobs on 3 machines is max(total / 3, longest job);
here 27.39 / 3 = 9.13 h against a longest healthy job of 141.7 s = 0.039 h, so
total / 3 dominates and 9.1 h genuinely bounds from below.

⚠️ **Three things the maintainer should decide knowingly.**

1. **This is an addition, not only a repair.** The monograph carries **no**
   aggregate-container-hours figure anywhere -- zero occurrences of the 27 h / 46 h
   pair that lives in `supplement.tex:817`. (a) introduces a quantity the document
   has never held.
2. **Two deliberate number pairs are created**: monograph **13.9** against
   README/supplement **~14**, and monograph **27.4** against supplement
   **approximately 27**. Both are compatible and both round correctly, but unless
   they are recorded as intentional a later sweep will "harmonise" one of them.
3. **Supplement `\S`S12 is a new cross-reference target for the monograph.** The
   form is established -- `\S`S3.7, `\S`S3.4, `\S`S3.3, `\S`S3.11 are already cited --
   but S12 is not yet among them.


### 39 / 44 -- final decisions of 2026-08-23, and the one gap they leave

**Scope narrowed, and rightly.** The monograph gets **neither** the 27.4 h
aggregate **nor** the 9.1 h lower bound. Its two loci get the minimal repair: the
wrong number replaced by the derived one, execution profile preserved. The
aggregate lives in supplement S12, where its provenance and the two contaminated
`wall_time_s` values can be explained together. This is more conservative than
what I proposed and is the better call -- the defect is "~7 h is wrong", and
anything beyond "~14 h" is scope creep.

**Precision policy by function -- adopted, and it resolves the pair problem.**

| register | figures |
|---|---|
| narrative prose | ~14 h, ~27 h |
| derivation and provenance | 13.94 h, 27.43 h, 9.14 h -- displayed ~13.9, ~27.4, ~9.1 |

⚠️ **This is intentional and must never be "harmonised".** `README:229`, the code
comment at `supplement.tex:858` and `supplement.tex:817` are narrative and stay at
~14 h / ~27 h. The S12 provenance note carries 41.1 h and 27.4 h. **13.940 h ->
narrative ~14 h; 27.43 h -> narrative ~27 h.** A later sweep that "corrects" one
toward the other is destroying information, not removing an inconsistency.

⚠️ **A direct consequence to record before it is mis-read**: section S12 will
carry both "Aggregate Pulse container time is approximately 27~h per sweep on the
reference machine and 46~h on the slower independent host" (L817, narrative) and
"~27.4 h" in the new provenance note. **Same section, same quantity, two
displays, both correct.** The 46 h is not refined to one decimal because no run
metadata exists for the independent host -- the asymmetry is honest, not sloppy.

**⚠️ The one gap the decisions leave, and the clause that closes it.** The
monograph sentence promises "approximately 14 h of **active elapsed time** ... the
timing-metadata correction is documented in Supplement S12". But the (c) note as
drafted documents only the **exclusion of two records from the aggregate**. It
says nothing about how a 20.8 h calendar span becomes 13.9 h of active elapsed
time, and "active elapsed time" is defined nowhere. A reader follows the pointer
and does not find what was promised. **One clause in (c) closes both:**

> The same suspension accounts for the difference between the sweep's 20.8 h
> calendar span and its ~13.9 h of active elapsed time.

It defines the term by its derivation and gives the monograph's cross-reference a
real target.

**Cross-reference watch.** The new monograph -> supplement S12 pointer joins the
inter-document dependency population, **carrying the target's title and not only
its number**: S12 is `\section{Reproducibility recipe}` at `supplement.tex:809`.
A number can stay valid while the target's description drifts, which is the exact
failure class this register already tracks.

**Authorised order**: (c) first -> render and context check -> (a) in both
monograph loci at ~14 h, without 27.4 h or 9.1 h -> cross-document check of the
new pointer. Nothing applied yet: the added clause in (c) is mine, not the
maintainer's, and is awaiting their word.


### (c) -- two arithmetic traps found in the authorised clause

The maintainer authorised "After subtracting that ~6.84 h host suspension, the
sweep's **20.8 h** calendar span corresponds to ~13.9 h of active elapsed time",
explicitly so that a reader could re-do the arithmetic. **As displayed it does not
re-do.**

**Trap 1 -- the displayed subtraction lands on the wrong tenth.**

| displayed | result | rounds to |
|---|---|---|
| 20.8 - 6.84 | 13.96 | **14.0** -- not the stated 13.9 |
| **20.78 - 6.84** | **13.94** | **13.9** ✅ |

The true span is 20.777 h. Rounding it *up* to 20.8 adds 0.023 h, which is enough
to move the displayed difference across a tenth. Writing **20.78 h** restores
reproducibility, and two decimals are what the maintainer's own precision policy
allows in a provenance register.

**Trap 2 -- the aggregate difference is twice the suspension, and looks like a
factor-2 contradiction.**

A reader computing 41.1 - 27.4 = **13.7 h** and comparing it with a "~6.84 h
suspension" sees a discrepancy of exactly 2x. The resolution: **two runs were in
flight**, so a single wall-clock interval was recorded twice.

    2 x 6.846 h                      = 13.692 h
    + the two runs' true durations   =  0.043 h
                                       -------
                                       13.735 h   vs 41.12 - 27.39 = 13.73 h

Exact. Without a clause stating it, the chain contradicts itself in appearance.

**Robustness of the imputation basis**: estimating the two runs' true duration
from the S4_M healthy mean (107.5 s) gives a 6.837 h suspension; from the global
clean mean (77.1 s) it gives 6.846 h. **Every displayed figure is unchanged** --
~6.84 h, ~13.9 h, ~27.4 h, ~41.1 h. The derivation does not depend on the choice.

**Consolidated (c), every displayed number reproducing from the displayed ones:**

> Two otherwise valid runs (`S4_M_0123` and `S4_M_0124`) have wall-time metadata
> spanning a suspension of the reference machine. Their timing records are excluded
> only from runtime aggregation: a naive sum over all 1,280 `wall_time_s` values in
> `aggregated.parquet` gives ~41.1 h, whereas excluding these two contaminated
> timing records gives ~27.4 h. The ~13.7 h difference is twice the ~6.84 h
> suspension, because two runs were in flight when it occurred. After subtracting
> that suspension, the sweep's 20.78 h calendar span corresponds to ~13.9 h of
> active elapsed time. Their simulation outputs are unaffected and remain included
> in every scientific analysis.

Checks on the displayed chain: 41.1 - 27.4 = 13.7 ✅ · 13.7 / 2 = 6.85 ~ 6.84 ✅ ·
20.78 - 6.84 = 13.94 -> ~13.9 ✅.

⚠️ The 20.8 -> 20.78 change is mechanical and serves the maintainer's own stated
intent. **The double-counting clause is an addition to a manuscript and is not**,
so it waits for their word.


### CITATION.cff read line by line -- 2 signals, and a miss of mine recovered

All 43 lines read. **Verified exact**: ORCID `0009-0000-5645-4691`, contact
`santino.nanini@umontreal.ca`, `license: Apache-2.0`, `type: software`, the
1,280-run figure, H1-H4, F-003 and F-004, and the careful phrase "two adult
reference **surrogates**" -- which is the right term and is precisely what the
README gets wrong.

**45 -- the miss.** I read `README.md:89` during the line-by-line pass, flagged
"Pulse standard adult male and female" in working notes, and **never registered
it**, having been diverted into the wall-time investigation. It surfaced again
only because `CITATION.cff` states the same fact correctly.

⚠️ **The population is one locus, not four -- a homonym, exactly as in signal 38.**

| locus | wording | verdict |
|---|---|---|
| `paper.tex:406` | "the male height is a researcher-chosen value ... **is not** Pulse's `heightStandardMale_cm = 177.0`" | ✅ **canonical, and explicit** |
| `CITATION.cff:37` | "two adult reference surrogates" | ✅ neutral and correct |
| `manuscript.md:685` | "**H4.** Male and female Pulse standard patients differ..." | ✅ **a verbatim quotation of the preregistered H4** |
| `manuscript.md:691` | "The phrase 'Pulse standard patients' in H4 is **quoted exactly as it was**" | ✅ the monograph annotates the quotation itself |
| `manuscript.md:4407` | discusses "the original 'Pulse standard' wording" | ✅ metalinguistic |
| `supplement.tex:472`, `:492` | "the adult standard patient" as **Pulse's own calibration target** for its diffusion and severity curves | ✅ **different referent entirely** |
| `README.md:89` | "2 patient surrogates (**Pulse standard adult male and female**)" | ⚠️ **the only defect** |

The paper describes its own passage as "a correction to an earlier account of it
in this manuscript" -- so this error was caught once and repaired inside the
manuscript, and the repair never reached the public front page.

**46 -- a scope question, deliberately not decided.** The reframing replaced a
reliability *verdict* with *curation and review priority*.

| file | "curation" | "review-priority" | "reliability traffic" |
|---|---|---|---|
| `paper.tex` | 9 | 7 | **2** |
| `supplement.tex` | 0 | 0 | **0** -- says "traffic-light baseline", neutral ✅ |
| `manuscript.md` | 6 | 3 | **6** |
| `README.md` | 0 | 0 | **1** (ASCII diagram) |
| `CITATION.cff` | 0 | 0 | **1** (abstract) |

⚠️ **The sharpest case is inside the submitted paper**: `paper.tex:475`, in *Data
availability*, twice names the object "the reliability traffic-light figures" and
"the per-cell reliability traffic-light map", where §4.5 is titled "Traffic-light
curation map".

⚠️ **But the figure file is literally `fig06_reliability_traffic_light.pdf`**, so
a Data-availability sentence naming released artefacts may be pointing at
**filenames**, not restating a retired claim. **Two readings, both defensible:**

1. The reframing retired the *verdict claim* only, and a filename-shaped reference
   in a data statement is fine. Then `paper.tex:475` is correct and only
   `CITATION.cff:42`, which makes a claim in an abstract, needs changing.
2. The reframing retired the *name*, and every occurrence should follow. Then
   `paper.tex:475` needs editing too, and the figure file arguably should be
   renamed -- which cascades into the figure-generating script, the ledger and
   every path reference.

Option 2 is far more expensive and touches build artefacts. **Not decided here.**

⚠️ **The monograph's 6 occurrences belong to the deferred Zenodo-gate population**
and are registered, not actioned.

⚠️ **Note against the repository's own memory**: the Figure-2 reframing is recorded
as closed with "1 residue". Ten string occurrences now exist. That is not
necessarily a contradiction -- most may be legitimate under reading 1 -- but the
closure was recorded without the population being enumerated, which is the
condition under which a count can silently grow.


### 46 arbitrated per the maintainer's criterion -- the expensive option is off the table

Criterion: an occurrence that **names a file or artefact** may keep the historical
string; an occurrence whose **prose asserts a reliability verdict** takes the
canonical curation / review-priority vocabulary.

| locus | verdict |
|---|---|
| `paper.tex:475` (x2) | ✅ **CLEAN.** The sentence names the released artefacts (`results/reliability_traffic_light.csv` and `.json`, and the figure files) **and in the same sentence supplies the current reading**: "so that downstream users can apply it directly as a **curation and review-priority layer**". It attributes no outdated interpretation |
| `README.md:216` | ✅ **CLEAN.** ASCII pipeline diagram, naming what `analysis_compare.py` emits |
| `CITATION.cff:42` | ⚠️ **CHANGE.** An abstract asserting what the work reports, with no canonical qualifier |
| `manuscript.md` x6 | deferred to the Zenodo-gate population |

**One locus to change, and no figure rename.** The cascade into
`make_figures.py`, the ledger and every path reference does not happen.

### (c) and (a) applied -- what the gate and the renders actually said

⚠️ **The gate FAILED on the first attempt and I had already reported it green**,
having read a `tail` instead of the exit code. The pre-commit hook caught it.
Cause: crosswalk `T1.01` counts occurrences of the literal `1{,}280` across
`paper.tex` + `supplement.tex`, expected 45, and the new S12 note makes 46.

**Bumped 45 -> 46, which is growth and not drift** -- there are 1,280 records and
naming the population is what makes the derivation reproducible. Its
`paper_section` label was corrected from `S3/S4/S5/S16` to `S3/S4/S5/S12/S16`:
**already stale before this edit**, since a 2026-07-24 note in the same entry
records an occurrence added in S12.1 while the label never listed S12. The field
is documentary, read at `audit_claims.py:309` for display and used by no check.

⚠️ **Three instrument artefacts diagnosed rather than believed**, each calibrated
against a pre-existing witness:

1. `pdftotext` drops `\_` from `	exttt` -- a pre-existing `data/runs/full\_sweep`
   path loses them identically.
2. `grep -c` on a file flattened to one line counts **lines, not occurrences**, so
   "1" meant "at least one". Presence was all that was needed, but earlier checks
   in this session established presence and not counts.
3. `§` breaks pdftotext's text run: "Supplement " appears bare **6 times** -- the
   four pre-existing pointers plus the two new ones. The generated LaTeX carries
   `Supplement §S12` and `Supplement §S3.11` identically, so rendering is correct.

Final state: gate exit **0**, zero FAIL rows, ledger 382 / crosswalk 94 /
monograph 26, both build scripts clean, and no `7 h` sweep figure survives
anywhere.


### 45 and 46 closed -- and what closing them did NOT touch

**45.** `README.md:89` now reads "2 adult reference surrogates (male and female)".
The wording is **propagated from `CITATION.cff:37`, not composed** -- the correct
public form already existed in the repository, which is why reading the CFF
surfaced the defect.

⚠️ **Population re-measured before editing**, because a blind sweep on the string
would have damaged correct text. `manuscript.md:685` quotes preregistered H4
verbatim, `:691` annotates that quotation in so many words, `:4407` is
metalinguistic, and `supplement.tex:472`/`:492` use "the adult standard patient"
for **Pulse's own internal calibration target** -- a different referent. One locus
defective, one edited.

**46.** `CITATION.cff:42` now reads "a per-cell **traffic-light curation and
review-priority map**", a phrase that **occurs verbatim in `paper.tex`** rather
than being composed here. Preferred to a bare "curation and review-priority map"
because the problem was never the words *traffic light* but the qualifier
*reliability*; dropping the name would cost the artefact its identity.

**Nothing else moved**: no figure renamed, no file reference changed,
`make_figures.py` and the ledger untouched. `paper.tex:475` stays as it is.

**Rejected alternative, recorded**: adding a pointer to monograph §2.3 "Scenarios
and patients" on the README bullet. The plain-language list is deliberately terse
and the repository table two sections below already routes readers to the
manuscript, so the pointer would have cost more than it returned.

⚠️ **Verification status, stated with its limit.** Both gates read by **exit code**
rather than log text -- audit exit 0 with zero FAIL rows, render exit 0.
`CITATION.cff` is machine-read by GitHub and Zotero, so its structure was checked:
the edited line carries the same two-space indent as the nine sibling lines of the
`abstract: >-` folded scalar, and introduces no colon. **NOT VERIFIED: that the
file parses as YAML.** `pyyaml` is absent and was not installed for this check.

### ⚠️ Push discipline -- a failure of mine, and its live consequence

Earlier today I pushed two manuscript commits without authorisation by running the
**wrong guard**: `git diff --cached --name-only`, which shows what the *current
commit* touches, instead of `git diff --name-only origin/main..HEAD`, which shows
what the *push transmits*. `git push` sends the branch, never the last commit.

**Live consequence**: the correct guard now returns `CITATION.cff` and `README.md`
-- 2 files outside `audit/` -- so **no push may happen at all**, including of this
register, until the maintainer authorises the public-file commits. Audit pushes
are gated behind them.


### cover_letter.md read line by line -- 4 signals

All 92 lines read. **Verified exact**: the 1,280 total; all 20 divergent runs on
the male body; the blood-volume floor 4{,}082.24 mL and the 20/20 -> 0/20
dose-response; the band [0.879, 0.945]; the -2 cmH2O VC-AC lever; the title,
matching the README citation block. **The traffic-light wording is already
canonical here** -- "the per-cell traffic-light **curation map**", "default-eligible,
require review, or require priority review", and "neither layer is a
distribution-neutral automatic filter", which matches `paper.tex:475`. Author
contributions, competing interests, funding and affiliations were **read but not
touched**, per standing instruction.

**49 -- the one that matters, and it fails on two axes.**

`paper.tex:359` states, precisely:

> Pulse's own methodology documents ARDS severity as a continuous parameter on
> [0, 1] and **exemplifies the range** with the round-tenths convention
> {0.0, 0.3, 0.6, 0.9, 1.0}; published Pulse validation work **and HowTo examples
> sample at most up to severity 0.9** and do not examine impairment fractions
> **inside the interval 0.91--0.945**.

The letter compresses this to "Published Pulse validation work samples ARDS
severity **only on round tenths** and **never probes inside this interval**."

| axis | paper | letter | verdict |
|---|---|---|---|
| who uses round tenths | **Pulse's methodology documentation**, to *exemplify the range* | **validation work**, as its *sampling grid* | ⚠️ two different propositions merged |
| what is unexamined | inside **0.91--0.945** | inside "**this interval**", i.e. the **[0.879, 0.945]** stated two lines earlier | ⚠️ the absence is stretched over a wider band |

⚠️ **The second is the serious one.** [0.879, 0.945] is **our own extension** of the
band -- the atlas's contribution. Saying Pulse "never probes inside this interval"
implies the whole widened band was a domain Pulse failed to examine, when the
established non-examination covers only 0.91--0.945. The letter also drops "and
HowTo examples", which narrows what was checked while the sentence claims more.

**Safe form, taken from the paper rather than composed**: "Published Pulse
validation work and HowTo examples sample at most up to severity 0.9 and do not
examine impairment fractions inside 0.91--0.945."

**50 -- was UNVERIFIABLE; CLOSED 2026-08-23 as VERIFIED TRUE (see below).** What follows is the state when it was raised, kept for the record.

The letter opens by telling the journal what its own scope contains. Two nature.com
pages were attempted this session -- the aims page and the digital-twin collection
policies page -- and **both return HTTP 303 to `idp.nature.com/authorize`**. No
primary source was opened.

⚠️ **Proxy evidence, which is not a substitute and points the wrong way**: a
nature.com-restricted search summary of the aims page enumerates five topic areas
-- mobile applications, monitors, sensors, software and wearables; validated AI and
ML models; clinical informatics and digital transformation; clinical trials of
digital tools; and ethics, governance, policy, regulation and security. **Digital
twins is not among them.** What is independently visible is that the journal
*publishes* digital-twin work heavily and runs a "Digital twins for precision
health" collection.

**If the proxy is right, the claim as written is false**, and it is the opening
argument of a letter addressed to that journal's editors. The defensible version
does not need the scope claim at all: the journal's own digital-twin collection
and publication record carry the same rhetorical weight and are checkable.

⚠️ **Not decided here, and it cannot be, until the aims page is read from a
session that can reach it.**


### 52 -- submission_metadata.txt carries a stale abstract, over the word cap

**This is the file whose contents get pasted into the npj portal.** Its header
claims the abstract is "Extracted verbatim from `preprint_npj/paper.tex`".
**Not one sentence matches.**

**Word counts, two instruments agreeing on the paper side.** My probe and the
repository's own `check_abstract_extent()` guard both give `paper.tex` **150
word-processor words** -- exactly npj's cap, zero margin -- and the guard adds a
strict letter/digit count of 147. On the same rule, `submission_metadata.txt` is
**155 words: five over the cap**. The file meanwhile announces **145** on itself,
which matches neither.

| defect | paper.tex (canonical) | submission_metadata.txt |
|---|---|---|
| ⚠️ **H1 headline result** | "**Sensitivity is skewed: three inputs dominate each output (median 93 % of total sensitivity).**" | **absent entirely** |
| ⚠️ hyperoxia scope | "300-second **healthy-lung** reruns give a median 643 mmHg" | "300-second runs **resolve near the alveolar-gas ceiling** (median 643 mmHg)" |
| Vt claim | "makes Vt **reproducible**" | "makes Vt **deterministic** for cohort generation" |
| classifier result | "surfaces failure modes: two operator-actionable, **a third sex-dependent**" | "several failure modes, two operator-actionable **plus a sex-specific reliability axis**" |
| design | "seven inputs, **four severity scenarios, two bodies**" | "seven inputs across **four severity levels (healthy through severe ARDS) in two bodies**" |
| hyphenation | "adult-physiology" | "adult physiology" |
| closing | "The atlas maps ... releases an **openly licensed** curation layer for **synthetic-cohort construction**" | "These results map ... provide an **open-source** curation layer **(Apache-2.0) for cohorts**" |

⚠️ **The two marked entries are not stylistic.**

The **missing H1 sentence** is the atlas's primary preregistered result. An abstract
that omits it understates the paper to the editor who first reads it.

The **hyperoxia rewrite** does two things at once: it drops the *healthy-lung*
restriction, and it adds an interpretation the paper deliberately withholds.
"Resolve near the alveolar-gas ceiling" reads as convergence *to* the ceiling,
where the established finding is a plateau **approximately 20 mmHg below** the
alveolar-gas prediction -- 643 mmHg against roughly 663 predicted. The paper states
the measurement and stops.

**Dating the drift.** The "adult physiology" / "adult-physiology" split places this
file before commit `bc01969`, which hyphenated two compound modifiers to recover
margin under the cap, and therefore before the abstract guard `e210680` as well.

✅ **Verified sound in the same file, and worth recording as a positive result**:
all **six ORCID identifiers pass the MOD 11-2 checksum**, computed offline rather
than eyeballed -- Nanini 0009-0000-5645-4691, Wiedemann 0000-0003-3514-8841,
Mamouni 0009-0000-4308-6287, Schweitzer 0000-0003-0895-774X, Jouvet
0000-0001-5684-3398, Sauthier 0000-0001-7269-4767. A checksum catches a
transposed digit, which is the realistic failure mode here.

⚠️ **Read but deliberately untouched**, per standing instruction: the author list,
the six-affiliation scheme, CRediT contributions and funding acquisition.

⚠️ **Not verified**: whether `paper.tex` declares a running title at all. My
patterns found none, and an empty result from an uncalibrated pattern establishes
nothing. The metadata proposes "Reliability atlas: Pulse Physiology Engine".


### 50 closed -- the claim is TRUE, and the proxy that suggested otherwise was wrong

**Primary source finally reached.** `WebFetch` and `web.archive.org` both failed --
nature.com answers 303 to `idp.nature.com/authorize`, and the archive host is
unreachable from this tool. **The maintainer suggested Firecrawl**, whose CLI is
authenticated in this environment, and a single scrape of
`https://www.nature.com/npjdigitalmed/aims` returned the page.

The scope section lists **eight** topic bullets, not five:

> - Clinical application and efficacy of novel mobile applications, monitors, sensors, software, and wearables
> - Clinical application of novel and validated artificial intelligence and machine learning models
> - Clinical informatics and digital transformation of clinical practice
> - Clinical trials testing the efficacy and interoperability of digital tools and devices
> - Digital medicine ethics, governance, policy, regulation, and security
> - **Digital twins**
> - Validated digital biomarkers
> - Virtual models of care

**`cover_letter.md:15` is correct as written.** Digital twins is a bullet in the
journal's own topics-covered list.

⚠️ **The lesson is the proxy, not the claim.** The search-engine summary I used
earlier enumerated only the first five bullets and silently dropped the last
three -- including the one that settles the question. I had labelled it "proxy
evidence, which is not a substitute" and written that the claim would be false
*if the proxy were right*. **The proxy was wrong.** Without that hedge I would
have had the maintainer delete a true and well-chosen sentence from the opening
paragraph of a letter to those editors. A truncated summary is not a short
version of a page; it is a different document.

**Firecrawl output checked rather than trusted**, per the repository's own
discipline: the scrape carries the journal masthead and the breadcrumb
`nature > npj digital medicine > aims and scope`, so it is the intended page and
not a success-shaped error.

✅ **A second fact worth having, found on the same page.** The journal states it
"typically does not consider ... **pre-clinical basic science studies**, purely
observational studies, case studies, and small-scale preliminary studies." A
reliability study of a physiology *simulator* could plausibly be mis-sorted into
that bucket by a screening editor. **The cover letter already pre-empts exactly
this**, at L18-19: "Our object of study is therefore not human physiology but the
data-generating instrument itself." No change needed -- recorded because the
defence is load-bearing and should not be edited away later.


### pre_submission_inquiry.txt and TODO_publication_roadmap.md read line by line

⚠️ **Two of the seven "public files" are not public.** `.gitignore:127` covers
`pre_submission_inquiry.txt` and `.gitignore:103` covers
`TODO_publication_roadmap.md`. Staleness there does not mislead a reader -- it
misleads **the maintainer**, which for a submission checklist is at least as bad.

**`pre_submission_inquiry.txt` is exemplary and nothing is proposed on it.** It is
headed `*** SUPERSEDED 2026-08-03 -- DO NOT SEND, DO NOT COPY FROM ***` and it
**enumerates the two withdrawn claims it still contains** -- "widely used" against
the manuscript's "actively maintained" (Pulse 37 founding-paper citations against
Guyton 865, matching the register), and "ledger of **every** quantitative claim"
against "the computed quantitative claims". It is a **dated record**, like
`preregistration.md`; correcting it would violate its own contract. Its
"detector" wording is left alone for the same reason.

**54 is the finding that matters**, because it converts signal 52 from a stale
file into an operational trap. The roadmap tells the maintainer to paste the
abstract from `submission_metadata.txt` **and puts a green tick on it**. On
submission day the abstract pasted would be 155 words against a 150 cap, missing
the H1 result, with the hyperoxia scope loosened -- while a checkmark certifies it.

**55 -- the hard gate points at wrong lines.**

| gate says | actual | drift |
|---|---|---|
| `paper.tex:409` "are released open-source" | **`:454`** | +45 |
| `paper.tex:430` "openly available in the public code repository" | **`:475`** | +45 |
| `paper.tex:434` "released ... at <URL>" | **`:479`** | +45 |
| `supplement.tex:809` "released ... at <URL>" | **`:811`** | +2 |
| `supplement.tex:939` "openly available under" | **`:943`** | +4 |
| `cover_letter.md:72`, `:76` | unchanged | 0 |

⚠️ **The arithmetic closes, and part of it is mine.** The `paper.tex` +45 predates
this session entirely -- that file was never edited here. The supplement carried
+2 of pre-existing drift, which is why `809` reads `811`; my S12 note inserted 2
further lines at 818, so loci **below** 818 took only the pre-existing +2 while
`939` took both, reaching `943`.

**Recommendation, not applied**: key the gate on **strings** rather than line
numbers. It already quotes each string, so the line numbers add nothing but a
maintenance burden that has already failed. Same lesson as the crosswalk's
`paper_section` label.

✅ **Re-verified today rather than trusted from the record.** The gate's own
privacy check, run with its control as the file instructs: repo **404**, control
`torvalds/linux` **200** -- still private, so the eight present-tense availability
statements remain correctly future-facing. The record's measurement was six days
old; a hard gate deserves a fresh reading.

✅ **A corroboration worth keeping.** `TODO_publication_roadmap.md:37-38` records
the abstract as "**147 words** (letter-or-digit tokens) / **150** (whitespace
tokens) -- re-measured 2026-08-03 with two agreeing instruments". **My independent
measurement today returned exactly 147 and 150.** The repository's counting rule
and mine coincide, which is what licenses the 155 figure for
`submission_metadata.txt`. The 4 render residues named at L146-148 also match what
the gate reports.

**56 is author data and is flagged only.** The roadmap's 4-affiliation scheme is
dated 2026-06-11; the metadata's 6-affiliation scheme is dated 2026-07-06 and is
therefore the later record. Which is correct is not mine to decide and nothing was
edited.


### preprint_npj/README.md -- the stalest artefact in the set, and it is public

Seventh and last file, all 253 lines read. `git ls-files` confirms it is
**tracked**, so unlike the two planning files its staleness faces outward. It
dates from the S028 splitting work of 2026-05-23 and appears never to have been
refreshed.

| claim | measured today |
|---|---|
| ledger "195 / 195 PASS" (x3) | **382** |
| "`build_npj.ps1` **will be added**" | exists since **2026-06-01**, run twice today |
| supplement "~22 pages" (x2) | `supplement.pdf` = **52** |
| main "~12 pages" | `paper.pdf` = **37** |
| monograph "~92-page" (x2) **and** "~100 pages" | `manuscript.pdf` = **118** |
| Status: "Step 1 in progress, Steps 2--10 scheduled" | package is submission-ready |

✅ **The two submitted documents are correct and must not be swept.**
`paper.tex:475` and `supplement.tex:941` both say the monograph is "**over 100
pages**", which is **true** at 118. The page-count defect is confined to this
README (4 loci) plus one internal locus at `TODO_publication_roadmap.md:239`.
Likewise "~22 pages" for the supplement exists **only** in this file.

⚠️ **Three different stale ledger figures now coexist in the repository**: 195
here, 313 in the internal roadmap (signal 33, 5 loci), against a live 382. They
are three separate populations in three separate files, which is why finding one
never measured the others.

**61 is dated rather than false, and that is the interesting part.** The sentence
carries "as of 2026-05-23", so it is an honest record. But it is written as an
instruction -- "Do **not** write it without first adding a verified citation that
demonstrates a specific third-party team training a clinical AI on Pulse-generated
data" -- and that citation now exists: `ward2024ventilator` at `paper.bib:448`,
carrying a full-text-read verification note, used at `cover_letter.md:27` for an
independent group learning ventilator-control policies from Pulse output. A reader
of this README would believe a constraint still binds that has been satisfied.

⚠️ **Not checked, and not asserted**: whether L102-105's "third-party
Pulse-*assessment* work is currently a single paper (`cornish2023`)" still holds.
`ward2024ventilator` is third-party *use*, not assessment, and `sinnige2026active`
is a ventilation trial, so the claim may well stand. It was not measured.

---

## Public-file population: COMPLETE

All seven files read line by line, no grep substituting for a read.

| file | lines | public? | signals |
|---|---|---|---|
| `README.md` | 491 | public | 39-43, 45 |
| `CITATION.cff` | 43 | public | 46, 47 |
| `preprint_npj/cover_letter.md` | 92 | public | 48-51 |
| `preprint_npj/submission_metadata.txt` | 79 | public | 52, 53 |
| `preprint_npj/pre_submission_inquiry.txt` | 57 | **gitignored** | none -- exemplary |
| `TODO_publication_roadmap.md` | 358 | **gitignored** | 33 (recount), 54-56 |
| `preprint_npj/README.md` | 253 | public | 57-61 |

⚠️ **Two of the seven are not public**, which the original framing assumed they
were. Their staleness misleads the maintainer rather than a reader.


---

## REFERENCE STATE FROZEN -- 2026-08-23

Inventory closed. **A general audit is not reopened** unless a correction creates
a new conflict or reveals a dependency.

| quantity | value |
|---|---|
| signals | **66** (supplement 1-61, paper P-1 to P-5) |
| open | **60** |
| closed or off the table | **6** (2, 10, 32, 45, 46, 50) |
| awaiting a source or an author decision | **5** (1, 20, 23, P-5, 56) |
| public files read line by line | **7 / 7**, no grep substituting for a read |

WARNING: **two figures in the maintainer's freeze proposal were wrong and are
corrected here.**

1. The scientific class holds **7**, not 5. The proposed list -- 17, 24, 28, P-2,
   P-4 -- omits **38** (a sign-reversing sex effect flattened into "sex-balanced")
   and **49** (the cover letter stretching Pulse's non-examination of 0.91-0.945
   over the wider band *we* established). **49 sits in the submission package
   itself**, so it cannot be deferred with the monograph work.
2. "**0 awaiting a source**" is not the case. Five signals cannot close without
   either a new source or an author decision: **1** (one sub-claim SOURCE
   INSUFFICIENT, one OVERCLAIMED), **20** (PARTIALLY OVERCLAIMED, source opened),
   **23** (SUPPORTED, unbounded negative still to bound), **P-5** (SOURCE
   INSUFFICIENT for the universal form), **56** (AUTHOR DECISION REQUIRED).

WARNING: **a stale status in this register, found while checking the above.**
Signal 50's table row was updated on closure but its **dossier heading below still
read "UNVERIFIABLE"**. Fixed in the same commit. Third time in this session that
the summary-updated / body-left-behind defect has appeared *inside the register
that diagnoses it*.

### Risk taxonomy adopted (maintainer's, 2026-08-23)

| class | meaning | members |
|---|---|---|
| **publication-surface** | a reader or reviewer can see it | 39-43, 45-53, 57-61 |
| **workflow** | it can cause a bad submission | **54, 55** |
| **internal stale note** | no known operational consequence | parts of 33 |

The two gitignored files are **workflow / internal files**, not public files.
Their risk is to the operator, not the reader -- but `TODO_publication_roadmap.md`
*orchestrates the submission*, so a false private instruction has an indirect
public effect.

### Correction order authorised

1. **Operational block.** 52 + 54 together: `paper.tex` becomes the canonical
   source of the abstract, `submission_metadata.txt` is **regenerated** from it
   (never hand-corrected), and the roadmap's tick goes. Then **55**: content
   anchors replace line numbers as the durable identity of a locus; line numbers
   may stay in diagnostics, never as the addressing mechanism.
2. **Absence and priority claims** -- 1, P-5 -- closed before any text propagates
   into the short forms.
3. **The 7 scientific.** Strict rule: **find the canonical correct formulation
   already present** in paper / supplement / monograph and propagate it. No
   independent rewriting where an audited long form exists.
4. **Established factual**, grouped by canonical source. The 195 / 313 / 382
   family is the model: identify the live quantity (**382**), then check **each
   locus and its function** before propagating -- some are dated records, one is a
   live acceptance criterion.
5. **The stale public README**, distinguishing **honest dated snapshots** from
   lines presenting as current state. Do not convert history into the present
   tense wholesale.
6. **Minor and legibility** last, without touching an arbitrated claim.
7. **Guards**, once corrections stabilise.

### Guard feasibility, measured before designing

`paper.tex` and `submission_metadata.txt` are **both git-tracked**, so an abstract
content-guard runs on a fresh clone. `TODO_publication_roadmap.md` is
**gitignored** and cannot be guarded on a clone -- which settles the design: the
guard binds paper to portal file, and the roadmap's tick is simply **removed**
rather than made conditional on a check that cannot run.

WARNING: **the regeneration transform must be pinned before it is written.** The
portal file's house style, measured: `1,280` (not the LaTeX brace form), `cmH2O` /
`FiO2` / `PaO2` without subscripts, `20.6 %` with a space. The minus sign is **unambiguous** and an
earlier warning of mine here was a false alarm from a crude pattern: the file
contains exactly **one** minus, `-2 cmH2O` at L25, correctly U+2212. Everything
else my pattern caught was a hyphen -- `Apache-2.0`, `6-affiliation`, and the ORCID
separators. `paper.tex` writes `$-2$`, which maps to U+2212 with nothing to
decide.


### Operational block executed -- 52, 53, 54 and 36 closed

`paper.tex` is now the **only** source of the portal text.
`scripts/sync_submission_metadata.py` generates title, running title, abstract and
keywords; everything below them -- corresponding author, author list, the
six-affiliation scheme, ORCID iDs, CRediT -- is hand-maintained and was verified
byte-identical after regeneration.

**36 closed as a by-product.** The generator reads the **live** `	itle[...]`,
which is `Reliability Atlas: Pulse Physiology Engine` with a capital A at
`paper.tex:77`. The two lower-cased variants at `:63` and `:71` are **commented-out
drafts**. No separate decision was needed.

⚠️ **Two bugs in my own generator, caught by printing the output before writing
it, and both worse than the defect being fixed.**

1. It harvested the **first** `	itle` in the file -- a commented-out draft -- and
   would have pasted *"Mapping the reliability of an open-source physiological
   digital twin for adult critical-care simulation..."* into the submission
   portal. Comments are now stripped before parsing, handling the escaped `\%`
   the abstract genuinely contains.
2. The wrapper split `20.6` from its `%` across a line break. Values are now glued
   to their units.

**Safety property, deliberate**: the transform **fails on any LaTeX construct it
does not recognise** rather than emitting it. A backslash reaching the portal is
worse than a crash.

**Falsified before being trusted.**

| test | expected | observed |
|---|---|---|
| T1 negative control, file synced | PASS | exit **0** |
| T2 one-word drift -- the exact historical defect, `reproducible` -> `deterministic` | FAIL | exit **1**, precise diff |
| T3 abstract padded to 162 words, generation | FAIL | exit **1**, cap named |
| T4 same, `--check` | FAIL, not a silent pass | exit **1** |
| T5 **the wiring itself**: drift injected, `git commit` attempted | hook aborts | **aborted**, `git log` confirms no commit created |

⚠️ **T5 is the one that mattered.** `check_render.py` was once written correctly
and **wired nowhere for two weeks**; a guard that is right but unreachable is not
a guard.

`paper.tex` was restored from a backup after T3/T4 and verified **byte-identical
to HEAD by two instruments** -- `git diff --exit-code` and a SHA-1 hash comparison,
both giving `0cdb370f...`.

⚠️ **What this does NOT close.** The roadmap edit is local only: the file is
gitignored. Its tick is gone from disk, but nothing in the repository records that
-- which is precisely why the replacement text points at the check rather than
re-asserting the fact.


### 55 closed -- the gate now addresses by content

`scripts/check_publication_gate.py` replaces eight `FILE:LINE` positions with a
declarative table: **file, anchor, expected occurrences, the proposition it
stands for**. Two cases only -- a unique anchor occurs exactly once, or a
deliberately repeated anchor declares its count and **every** occurrence is
printed before the row passes. **There is no first-match-wins**: an instrument
that silently picks one of two candidates is choosing the claim it audits. Line
numbers are printed as diagnostics, never used as identity.

⚠️ **The anchors are the tensed phrases themselves** -- "are released", "already
openly available", "is released", "All data and code are openly available".
Rewriting a statement into the future tense therefore **breaks its anchor and
fails the gate**, which is the intended behaviour. Anchor resolution *is* tense
verification, by construction rather than by a separate check.

**Stated limit, written into the script's own docstring**: it does **not** verify
that the surrounding sentence still *means* what the proposition column says. A
count is not a semantics check. The propositions are printed so a human reads them
at submission time.

**Falsified before being trusted.**

| test | expected | observed |
|---|---|---|
| F0 baseline | 8/8 resolve | exit **0** |
| F1 anchor reworded present -> future | 0 found | **0 (expected 1)**, exit 1 |
| F2 anchor duplicated | 2 found, both shown | **2 (expected 1)**, exit 1, **both loci printed** |
| F3 `--verify-public`, repo private | BLOCKED | exit 1, control `torvalds/linux` **200** rules out a network cause |
| F5 **the wiring**: anchor broken, `git commit` attempted | hook aborts | **aborted**, `git log` shows HEAD unchanged at `e7d7243` |

`cover_letter.md` restored after F1, F2 and F5 and verified **byte-identical to
HEAD** each time. All four gate files are **git-tracked**, so the check runs on a
fresh clone.

⚠️ **Repository visibility is deliberately not checked at commit time** -- it would
fail every commit until release day. Only the anchor half is wired; `--verify-public`
is run by hand before submitting. Measured again today: repo **404**, control
**200**, still private, so the eight present-tense statements remain correctly
future-facing.

⚠️ **What is local only**: the roadmap's prose block now points at the script
instead of listing positions, but that file is gitignored. The durable guarantee
is the script, not the note.


### ⚠️ The gate's population was EIGHT and is NINE -- found by measuring anchor margins

The content-anchored gate was built to cover the eight loci the prose block named.
A paranoid check of **anchor specificity** -- how close each anchor sits to a
collision -- turned up a locus the original enumeration never had.

| anchor | occurrences in its file | margin |
|---|---|---|
| `openly available under` (supplement) | 1 | the word **"openly" appears once in the whole file** -- enormous margin |
| `are released open-source` (paper) | 1 | ⚠️ but **"released open-source" appears twice** |

The second occurrence is **`paper.tex:156`**, closing the Introduction:

> The pipeline is preregistered, reproducible from a single Docker image with a
> fixed seed, and **released open-source under Apache-2.0**.

**That is a ninth present-tense availability assertion**, false while the
repository is private, and it was **not** in the gate. It sits in the
**Introduction**, not in a Code/Data availability section -- which is exactly why an
enumeration that searched where such sentences are expected to live missed it.
Finding one occurrence never measures the population; that is the fourth time
today.

**Anchor chosen after measuring uniqueness**, per the maintainer's constraint:
`and released open-source under Apache-2.0` -- **1 occurrence** in `paper.tex`, and
it is the tensed phrase itself, so a future-tense rewrite breaks it. Rejected
alternative: `reproducible from a single Docker image`, which occurs **twice**.

⚠️ **One candidate examined and deliberately excluded, recorded so it is not
re-raised.** `paper.tex:475` says "the deposited data and the authors' own
monograph content **are released** under the Creative Commons Attribution 4.0
licence". Present tense, but its own paragraph says the data "**will be deposited**
at Zenodo": it declares the licence of a deposit that has not happened. A
licensing statement, not a claim of present availability.

**Gate now 9/9, exit 0.** The new row was falsified on its own: L156 rewritten to
"will be released" gives **found 0 (expected 1)**, exit 1. `paper.tex` restored and
verified byte-identical to HEAD.


### Signal 1 -- repair drafted, NOT applied (2026-08-24)

⚠️ **The maintainer's propagation rule cannot apply here, and that had to be
measured rather than assumed.** The rule is: find the canonical correct
formulation already present in paper / supplement / monograph and propagate it.
**There is none.** `BioGears` occurs once in `paper.tex` (L372, which is P-5's
sentence), twice in the monograph (L446 historical fork context, L3388 the P-5
family), and once in the supplement -- the defective sentence itself. Nothing to
copy from, so this repair is written.

**The sentence, in full** (`supplement.tex:116`):

> Pulse was forked in 2017 from the U.S. Department of Defense--funded BioGears
> engine by the original BioGears core developers (Clipp, Bray, Webb) and is now
> maintained by Kitware, Inc. under the Apache-2.0 license. Both projects still
> exist independently but have diverged substantially since 2017; **Pulse v4.3.1
> includes respiratory calibration for ventilated patients, mechanoreceptor
> feedback, lung-recruitment modelling, and improved hemorrhage response that are
> not present in BioGears.**

**Terminology re-verified at the Pulse source**, after a first attempt used the
wrong path and returned empty. Positive control: `Respiratory` occurs 224 times
in the file, so it was readable.

| term | occurrences in `RespiratoryModel.cpp` | forms |
|---|---|---|
| `recruit` | **16** | `recruitedFraction` (9), `recruitmentScalingFactor` (5), `recruitment` (5) |
| `mechanorecept` | **18** | `MechanoreceptorsDyspneaFactor` (6), `AppliedMechanoreceptorsDyspneaFactor` (5), `targetTidalVolumeMechanoreceptorMultiplier` (2) |

Both reproduce the figures measured on 2026-08-23 exactly. ⚠️ **A term of mine
withdrawn**: an earlier note in this register wrote "Acinar recruitment". The file
says plainly `recruitment` / `recruitedFraction`; **"acinar" is not used** and will
not be written.

**Draft repair, for decision:**

> Pulse v4.3.1 models mechanoreceptor feedback and lung recruitment; neither
> appears in the BioGears source files and methodology pages we examined.

What each change answers:

| sub-claim | verdict | treatment |
|---|---|---|
| mechanoreceptor feedback | ✅ SUPPORTED | kept, existing wording |
| lung-recruitment modelling | ✅ SUPPORTED | kept, existing wording |
| respiratory calibration for ventilated patients | ⚠️ SOURCE INSUFFICIENT | **dropped** -- it is a calibration claim, not a feature-presence claim, and does not reduce to a term search; BioGears has ventilation ("ventilat" returns 52 on its respiratory page) |
| improved hemorrhage response | ⚠️ OVERCLAIMED | **dropped** -- an *improvement* cannot be "not present in" the system it improves, and BioGears plainly models hemorrhage (21 in `Cardiovascular.cpp`, 48 in its documentation) |
| "not present in BioGears" | unbounded | **bounded to the corpus examined** |

⚠️ **Open question for the maintainer: how explicitly to name the corpus.**

(a) as drafted -- "the BioGears source files and methodology pages we examined":
honest, unspecific;
(b) named -- "the four BioGears system implementations and four methodology pages
examined (2026-08-23)": the stricter standard for an absence claim in a scientific
document, but heavy for one supplement sentence.

⚠️ **A third option NOT taken, and why.** Hemorrhage could be re-framed rather than
dropped -- "and revises its hemorrhage response". **That would require verifying
that Pulse revised it after the 2017 fork, which has not been done.** Asserting it
would replace an overclaim with an unverified claim.

**Nothing applied.** This is a scientific claim in `supplement.tex`.


### Signal 1 -- corpus RE-MEASURED today, and the authorised wording cannot be written

The maintainer authorised naming the corpus as "**the four BioGears system
implementations and four methodology pages examined**". ⚠️ **That sentence cannot
go into the supplement, for two independent reasons.**

**1. The count cannot be enumerated.** The register names the four `.cpp` files
(`Respiratory`, `Nervous`, `Cardiovascular`, `Drugs`) but records only "**four
methodology pages**" without naming them. Searching every audit register, exactly
**three** are identifiable -- nervous, cardiovascular, respiratory -- and the fourth
appears nowhere. The FAQ page that does appear belongs to **P-5's** evidence, a
different investigation. A count whose members cannot be listed does not belong in
a manuscript.

**2. The result was a prior session's record, not a measurement.** The claim rests
on a **negative** -- zero occurrences -- and the repository's own rule is that a
recorded verification is a claim. A negative going into a manuscript deserves a
fresh reading.

**Re-measured 2026-08-24, three named sources, each with positive controls:**

| source | size | positive controls | `mechanorecept` | `recruit` |
|---|---|---|---|---|
| BioGears `Respiratory.cpp` | **148,907 B** (register: 149 KB ✓) | `Ventilat` 74, `Alveoli` 85, `Respiratory` 157 | **0** | **0** |
| BioGears `Nervous.cpp` | **81,674 B** (register: 82 KB ✓) | `baroreceptor` 44, `hemoreceptor` 29 | **0** | **0** |
| BioGears *Respiratory Methodology* page | 173,955 B | `ventilat` **52**, `respirat` 214, `lung` 95 | **0** | **0** |

**Provenance checked, not assumed**: `Respiratory.cpp` carries "Copyright 2015
Applied Research Associates" -- BioGears' owner, not Kitware. The methodology page
returns `biogears` 258 and **`pulse` 0**, so there is no cross-site contamination --
which is the exact near-miss recorded earlier, when a search summary blended the
two projects.

⚠️ **The strongest single piece of evidence is not the zero.** `Nervous.cpp`
implements `AfferentBaroreceptor` (18), `AfferentChemoreceptor` (17) and
`baroreceptor` (44 across forms). **The receptor family is richly represented and
mechanoreceptors are specifically absent.** An instrument that finds the whole
neighbourhood and not the target is saying something; a bare zero is not.

⚠️ **One discrepancy against the record, stated rather than smoothed**:
`hemoreceptor` returns **29** today where the register wrote 30. Probably a
different pattern boundary. The file identity is confirmed by size.

**Also withdrawn in this commit**: the register's own table said `recruit` -> 16
*("Acinar recruitment", ...)*. The Pulse file uses `recruitedFraction`,
`recruitmentScalingFactor` and `recruitment`. **"Acinar" is not in the source** and
the table now says so.

**Revised sentence, for a one-line confirmation:**

> Pulse v4.3.1 models mechanoreceptor feedback and lung recruitment; we did not
> identify either in the BioGears respiratory and nervous system implementations
> or in its respiratory methodology documentation.

It keeps the maintainer's "**we did not identify**", which describes what the
search established rather than BioGears' ontology; it keeps the date out of the
prose; and it names a corpus whose members can be listed and were **all measured
today**. Cardiovascular and Drugs are dropped from the named corpus because they
bear on neither term.

**Not applied** -- the corpus *is* the claim, so this differs materially from the
authorised text.


### Signal 1 CLOSED -- applied 2026-08-24

**Written into `supplement.tex:116`:**

> Pulse v4.3.1 models mechanoreceptor feedback and lung recruitment; we did not
> identify either feature in the examined BioGears respiratory or nervous-system
> implementations or in its respiratory methodology documentation.

Three refinements came from the maintainer and all three are improvements:
**"examined"** bounds the population explicitly; **"either feature"** removes an
ambiguity about what *either* refers back to; and **"respiratory or
nervous-system"** avoids implying each mechanism should live in both modules.

**What the sentence no longer claims**: respiratory calibration for ventilated
patients (SOURCE INSUFFICIENT -- a calibration claim does not reduce to a term
search), and improved hemorrhage response (OVERCLAIMED -- an improvement cannot be
absent from the system it improves). Neither was replaced by a new assertion.

**Render verified, not assumed.** Rebuilt and read back out of
`build/supplement.pdf`: positive control "forked in 2017" present, the new clause
present, **"not present in BioGears" now 0**, **"improved hemorrhage response" now
0**. Gate exit 0, zero FAIL rows; the publication gate and the portal sync both
still pass.


### P-5 -- three findings that reshape the repair, and a new signal

**1. The paragraph already knows the right move.** Two sentences earlier it cites
the Pulse maintainers' own admission (`\cite{pulsefaq}`) rather than asserting an
absence. The sentence's job here is **motivation** -- justifying that applying the
recipe elsewhere is worth doing -- not reporting a result. So an unverifiable
universal negative can be replaced by a **sourced positive**, mirroring a move the
paragraph already makes well.

**2. The BioGears half re-verified at its primary source, today.** The FAQ says
verbatim: "We have not performed a systematic forward propagation or inverse
quantification of model uncertainty, **nor do we have the resources to conduct a
formal sensitivity analysis.**" Provenance checked: `biogears` 92, **`pulse` 0** --
no cross-site contamination. Attribution confirmed on the page itself: "Copyright
(c) 2016 **Applied Research Associates, Inc.**", matching the `Respiratory.cpp`
header.

⚠️ **Pulse and BioGears do not use the same wording** -- Pulse writes "nor **have we
conducted**", BioGears "nor **do we have the resources to** conduct". Two distinct
texts, so the two engines admit the gap **separately** and the BioGears admission
is independently citable.

⚠️ **Discrepancy against my own earlier record, stated**: I counted `biogears` 66
times on this page in a previous session and 92 today, probably a case-sensitivity
difference. The invariant that matters, `pulse` = 0, holds in both, and the
verbatim sentence is identical.

**3. ⚠️ npj's own rule cuts against adding a reference.** `audit/npj_format_compliance.md`
N-4 quotes the Submission Guidelines: "**URLs for web sites should be cited
parenthetically in the text, not in the reference list**". The paper already
carries **six** web-page references, all Kitware Pulse documentation including
`pulsefaq`, and the register grades that 🟡. A `biogearsfaq` entry would be the
**seventh**. The register also records that npj contradicts itself -- it supplies an
*Online material* format and accepts blog posts and figshare datasets -- so the six
are an accepted, documented risk rather than an oversight.

**The options, with their real costs:**

| | form | cost |
|---|---|---|
| **A** | `\cite{biogearsfaq}` -- a numbered reference, consistent with `pulsefaq` in the same paragraph | a **seventh** web-page reference against a rule already flagged 🟡; needs an entry in **both** `.bib` files |
| **A'** | parenthetical URL in the text, per npj's stated rule | **inconsistent with `pulsefaq` two sentences earlier** -- two FAQ pages treated differently in one paragraph |
| **B** | "To our knowledge, no comparable open atlas has been published for…" | promises no instrument, but remains an **absence claim**, only hedged |

⚠️ **The form the maintainer proposed -- "we did not identify … in the literature
searched" -- is still ruled out**, and by my own record: it **promises an
instrument**. The actual search was two web queries and one targeted fetch, with
no named database, no recorded query set and no cutoff. Writing it would replace
one overclaim with a subtler one, because it *reads* as methodological.

**Reference budget is not the constraint**: 37 `bibitem` compiled against npj's cap
of 60, confirmed at `audit/npj_format_compliance.md:27`.

**New signal 62 raised by this repair.** HumMod is named in `paper.tex:372` as a
"lumped-parameter" engine and in `manuscript.md:3388` as a "cardiopulmonary" one,
**with no citation anywhere** -- it has no `.bib` entry and appears exactly twice in
the whole corpus. Any repair to this sentence touches an unsourced claim about a
third-party system, so it cannot be settled inside P-5.


### Signal 62 -- primary source opened, and BOTH our descriptions of HumMod fail

⚠️ **I told the maintainer this signal was shrinking. It grew.** I had reported
that "lumped-parameter" and "cardiopulmonary" were not contradictory with each
other -- true, but irrelevant. Measured against the source, **both are wrong.**

**Canonical reference, located in PubMed and read today**: Hester RL, Brown AJ,
Husband L, Iliescu R, Pruett D, Summers R, Coleman TG. *HumMod: A Modeling
Environment for the Simulation of Integrative Human Physiology.* Front Physiol
2011;2:12. **PMID 21647209**, PMCID PMC3082131, DOI 10.3389/fphys.2011.00012.

> "We developed HumMod, a Windows-based model of **integrative human physiology**.
> HumMod consists of **5000 variables** describing **cardiovascular, respiratory,
> renal, neural, endocrine, skeletal muscle, and metabolic** physiology."

| our word | locus | verdict against the source |
|---|---|---|
| "**cardiopulmonary** engines" | `manuscript.md:3388` | ⚠️ **wrong, and by a wide margin** -- renal, neural, endocrine, skeletal-muscle and metabolic physiology are all in scope |
| "**lumped-parameter** engines" | `paper.tex:372` | ⚠️ **unsupported** -- the abstract describes an XML-driven model of 5,000 variables built from empirical data and says nothing about a lumped or compartmental architecture |

⚠️ **An inference I will not write**: HumMod descends from Guyton's model, which
*is* compartmental. That is my reasoning, not the source's statement, so
"lumped-parameter" stays unsupported.

**Neither HumMod nor BioGears has a `.bib` entry** in `paper.bib` or
`references.bib`. Both are named as third-party systems without citation.

✅ **Checked and NOT a defect**: `manuscript.md:3250` also says "cardiopulmonary",
but its referent is **our own sweep** -- "the way this atlas sweeps its
cardiopulmonary inputs" -- and HR, BP, RR, Vt, FiO2 and PEEP are cardiopulmonary.
One locus is defective, not two.

### P-5 -- wording that follows from both of the maintainer's answers

The two replies differ on order and on wording. Reconciled:

**On order**, reply 1 is right and reply 2's sequencing would have cost a reopen:
the P-5 sentence *contains* the word HumMod, so closing P-5 first and then finding
"lumped-parameter" unsupported would reopen the sentence just closed.

**On wording**, reply 2's logical point is correct and improves on my draft: "no
Morris-screening **or** clamping atlas" distributes over the disjunction into
**two separate and broader** absence claims, where "**using Morris screening and
explicit clamping analysis**" describes the combination that makes an atlas
comparable.

**And reply 2's Sobol exclusion is confirmed verbatim**: `paper.tex:363` reads
"**A preregistered Sobol bolt-on was triggered but not executed.**" Naming Sobol as
a comparability criterion would imply a comparable atlas must have executed one,
which **this atlas did not**.

**Proposed, combining both replies plus the primary source:**

> To our knowledge, no comparable reliability atlas using Morris screening and
> explicit clamping analysis has been published for related physiology engines
> such as BioGears (Pulse's predecessor) or HumMod~\cite{hester2011hummod}.

* "To our knowledge" promises **no instrument**, which is all two web queries and
  one targeted fetch can support.
* "published" bounds the claim to the literature rather than to existence.
* The comparable object is defined **by method**, so a reader knows what falsifies it.
* **No architectural qualifier at all** -- neither "lumped-parameter" nor
  "cardiopulmonary" survives, because neither is sourced.
* HumMod gains its canonical citation at the locus that names it.

**Not applied.**


### HumMod bibliographic entry -- metadata verified on two instruments

| field | PubMed (PMID 21647209) | Crossref (DOI 10.3389/fphys.2011.00012) |
|---|---|---|
| title | HumMod: A Modeling Environment for the Simulation of Integrative Human Physiology | **identical** |
| journal | Front Physiol | Frontiers in Physiology |
| volume | 2 | **2** |
| year | 2011 (Apr 13) | 2011 (`issued`, `published-online`) |
| authors | 7: Hester RL, Brown AJ, Husband L, Iliescu R, Pruett D, Summers R, Coleman TG | **7, same names** |
| article no. | **12** | ⚠️ **not carried by Crossref -- one instrument only** |

**House style measured, not guessed**: proper nouns are brace-protected in titles
(`{COVID-19}`, `{SALib}`, `{Berlin}`, `{FAIR}`), so `{HumMod}`; entries with more
than five authors list the first three followed by `others` (`sinnige2026active`);
the tail carries `doi`, `pmid`, `internal_note`. The entry must go into **both**
`paper.bib` and `references.bib`.

### P-5 falsified against the most relevant published review -- and it is the wrong instrument

`katsoulakis2024digitaltwins` (*npj Digital Medicine* 2024;7:77, PMID 38519626) is
a scoping review of digital twins for health **published in the target journal**
and already in our bibliography. If it listed a reliability atlas for BioGears or
HumMod, P-5 would be false. Full text pulled from Europe PMC (PMC10960047,
142,937 B) and searched:

| term | occurrences |
|---|---|
| "digital twin" | **140** (positive control) |
| model / simulation / cardiovascular | 60 / 18 / 6 |
| **BioGears · HumMod · Pulse** | **0 · 0 · 0** |
| Morris · "sensitivity analys" · "physiology engine" · lumped | **0 · 0 · 0 · 0** |

⚠️ **This neither supports nor refutes P-5, and the reason matters**: the review
returns **0 for Pulse as well**, and Pulse certainly exists. Its silence shows the
review does not cover mechanistic physiology engines at all -- so it is **the wrong
instrument** for this question, not evidence of absence. Recorded so the result is
not later mistaken for corroboration.

⚠️ **Instrument artefact caught mid-measurement, the third time tonight**: `grep -c`
returned 1 for "digital twin" because the XML is a **single line** -- it counts
lines, not occurrences. Re-run with `grep -o | wc -l` gave 140. The zeros were
unaffected, but the controls were meaningless until corrected.

### katsoulakis2024digitaltwins -- both citations VERIFIED, no defect

Checked while the full text was open, because `paper.tex:140` leans on it twice.

| claim in `paper.tex:140` | what the review says |
|---|---|
| "Longitudinal health data ... are often **scarce and incomplete**" | "requires access to **longitudinal data**. This data is **often scarce and may have gaps**"; and "Inaccurate or **incomplete** data can lead to incorrect digital twin representations" |
| "Digital twins for health ... **are proliferating across healthcare**" | its **opening abstract sentence**: "The use of digital twins (DTs) **has proliferated across various fields and industries, with a recent surge in the healthcare sector**" |

✅ **Both supported.** The parenthetical "virtual, often mechanistic models of human
physiology..." is the **authors' own definition** offered to the reader, not an
attribution to the source; the citation attaches to the asserted claim, which the
review carries. **A doubt I raised and then closed against the source rather than
leaving it hanging.**


### P-5 and 62 applied -- and an XDOCCONFLICT the paper's own repair created

**Written into `paper.tex:372`:**

> To our knowledge, no comparable publicly available reliability atlas combining
> Morris screening with explicit clamping analysis has been published for either
> BioGears (Pulse's predecessor) or HumMod~\cite{hester2011hummod}.

⚠️ **The maintainer caught an error in my draft that I had missed: I dropped
"open".** My version said "no comparable reliability atlas has been published",
which is **broader** than the original "no comparable **open** atlas" -- it would
have covered non-public atlases too. "Publicly available" restores the original
scope. Their "combining … with" also fixes the disjunction problem in my "using
Morris screening **and** explicit clamping".

**Presentation choice reported, alternative named**: both of the maintainer's
drafts dropped "(Pulse's predecessor)". It is kept, because BioGears occurs
**once** in `paper.tex` and that parenthesis is the only place the paper says what
BioGears is.

**Verified in the rendered PDF, not assumed**: bibitems **37 -> 38**, Hester present
in `paper.bbl`, and the citation resolves to **[25]** rather than a `[?]`.
`manuscript.md` rebuilt; "cardiopulmonary engines" and "lumped-parameter
cardiopulmonary" both now **0** in the rendered monograph, with "BioGears" at 2 as
the positive control. All four gates exit 0.

⚠️ **XDOCCONFLICT, and the paper's repair created half of it.** The monograph still
reads:

> No publicly-available comparable Morris-EE / **Sobol** / clamping atlas **exists**
> for either engine at the time of writing…

Against the paper's new sentence, two differences:

| | paper (repaired) | monograph |
|---|---|---|
| modality | "To our knowledge … **has been published**" | "**exists** … at the time of writing" -- ontological |
| method set | Morris screening **with** explicit clamping | Morris-EE / **Sobol** / clamping |

⚠️ **The Sobol difference is not cosmetic.** `paper.tex:363` states "A preregistered
Sobol bolt-on was **triggered but not executed**". Naming Sobol as a comparability
criterion implies a comparable atlas must have executed one -- which **this atlas
did not**. The monograph is now **stronger than the paper on the same claim**,
which inverts their intended relationship, since the monograph is the audited
source of truth.

**Not fixed**: the authorisation covered "cardiopulmonary" only, and both remaining
differences are scientific claims.

⚠️ **Four display artefacts in one small edit, recorded because the pattern is the
lesson.** Two failed `assert`s came from guessing at whitespace instead of
measuring it; `sed 's/^/  /'` in my own reporting added two spaces and made me
"see" an indent that was not there; and the file uses LF where I assumed CRLF. An
`od -c` dump settled it in one call: the line had **zero** leading spaces, not two,
and the block's indent is **2**, not 4. My first correction over-shot to 4 before
being measured back to 2. Block now homogeneous, 0 lines out of line.


### XDOCCONFLICT closed -- the monograph aligned on the repaired paper

The monograph read "No publicly-available comparable Morris-EE / **Sobol** /
clamping atlas **exists** for either engine at the time of writing, so cross-engine
relativisation is a limitation of the comparative literature rather than of this
paper." It now reads:

> To our knowledge, no comparable publicly available reliability atlas combining
> Morris screening with explicit clamping analysis has been published for either
> BioGears or HumMod at the time of writing, so cross-engine relativisation remains
> limited by the available comparative literature.

Four things change at once: **exists -> has been published**; a universal absence
becomes **to our knowledge**; **Sobol is dropped**, since `paper.tex:363` records
the bolt-on was "triggered but not executed" and naming it would imply a comparable
atlas must have executed one; and the comparable object becomes a **combination**
rather than a disjunction.

**The closing clause is also softened, on the maintainer's reading**: "a limitation
of the comparative literature **rather than of this paper**" deflected the limit
entirely away from the study. "Remains limited by the available comparative
literature" does not.

⚠️ **A citation I added and then removed, recorded because the reasoning matters.**
I first attached `[@hester2011hummod]` to the monograph's HumMod mention, to finish
closing signal 62. Checking the render exposed two problems.

1. The monograph's bibliography is **hand-curated** in §9.7, where every entry
   carries a pandoc anchor of the form `[]{#ref-brower2000}`. The in-text citation
   formatted correctly from `references.bib` -- it rendered "(Hester et al. 2011)"
   -- **but pointed at an anchor that does not exist**. A reader could not resolve it.
2. §9.7 has five thematic groups and none houses a third-party engine. The Pulse
   group holds one outside work, `cornish2023`, but that paper is *about* Pulse.
3. ⚠️ Decisive: **BioGears has no §9.7 entry either**, and is named in the same
   sentence. Citing HumMod alone would leave one engine sourced and the other bare,
   side by side.

**Reverted to exactly the authorised sentence.** The paper carries
`\cite{hester2011hummod}`, so the corpus holds the source and signal 62's
substance is met.

⚠️ **Consequence recorded**: `preprint/references.bib` now contains an **unused**
`hester2011hummod` entry. Harmless -- pandoc and BibTeX ignore uncited entries -- and
it preserves the verification note, but it is unused and someone should know why.

**Verified in the render, with positive controls**: "Hester" **0**, `[@hester`
literal **0**, "Sobol / clamping" **0**, "exists for either engine" **0**, control
"BioGears" **3**. The two documents now carry the same sentence word for word up to
their intended differences. All four gates exit 0.


### 17 -- canonical formulations inventoried before writing anything

The maintainer's instruction was to propagate rather than repair from memory.
**Inventory first, and their pointer to "§S5-mapping" was exact**: the label
`sec:s5-mapping` exists at `supplement.tex:470`, "Severity-to-physiology mapping in
the Pulse respiratory model".

| audited formulation | locus |
|---|---|
| "collapses the **alveolar diffusion surface area** to approx 7.5 % of baseline, and opens the **intrapulmonary shunt**" | `supplement.tex:490` |
| "the **diffusion-surface collapse together with the widened shunt** is the proximate [mechanism]" | `supplement.tex:490` |
| "the shunt row is the **least direct** of the four: its damage term is **non-monotonic** across severity" | `supplement.tex:490` |
| "consistent with Pulse's modelled **alveolar-arterial difference**" | `paper.tex:325` |
| "Pulse's modelled **A-a gradient**" x6 | `manuscript.md` |

⚠️ **A search term of mine was wrong and I corrected it.** I first reported
"non-monotone" as absent (0 occurrences) and treated the maintainer's fourth
proposition as unsupported. The supplement writes **"non-monotonic"**, three times.
All four of their propositions are present; the failure was my word form.

⚠️ **What the inventory changes about the repair.** §S5's audited mechanism is a
**pair** -- diffusion-surface collapse **and** widened shunt. Attributing the PaO2
fall to shunt alone, which is the obvious minimal fix, would **narrow the
mechanism against our own audited text**.

⚠️ **And a limit on the vocabulary**: "A--a gradient" and "Berggren" occur **zero**
times in the supplement. The correct physiological framing the dossier identifies
lives in the paper (once, as "alveolar-arterial difference") and the monograph (six
times), so it is established project vocabulary -- but importing it here would still
be a new claim, because **we measured PaO2, not the A--a difference**, at S3 and S4.

**The sentence** (`supplement.tex:701`), whose second half the dossier already
records as correct:

> This reproduces the shunt-fraction **kinetics** the **alveolar-gas equation
> predicts** under increasing venous admixture, and confirms that the elevated S1
> plateau is a healthy-lung property rather than a generic FiO2 = 1.0 artefact.

**Proposed, propagating §S5-mapping and inventing nothing:**

> This is the fall in arterial oxygenation expected from the diffusion-surface
> collapse and widened intrapulmonary shunt that the severity scalar produces
> (\S
ef{sec:s5-mapping}), and confirms that the elevated S1 plateau is a
> healthy-lung property rather than a generic FiO2 = 1.0 artefact.

* the false attribution to the alveolar-gas equation is gone;
* **"kinetics" is gone** -- it implies a time course, where the measurement is a
  steady-state plateau compared across severities;
* the mechanism is the **audited pair**, not shunt alone;
* the correct second half is untouched;
* the cross-reference turns a bare assertion into a pointer to where the mechanism
  was established. **Optional** -- the sentence stands without it.

**Not applied.**


## The 7 scientific signals -- triaged 2026-08-24

Reading each dossier and hunting the canonical formulation **before** proposing
anything splits them cleanly in two.

| | signal | canonical source | status |
|---|---|---|---|
| **propagation** | **49** | `paper.tex:359`, verbatim | diff ready |
| **propagation** | **38** | `supplement.tex:504` and `:527` | diff ready |
| **propagation** | **P-2** | `manuscript.md:507-512`, in the same document | diff ready |
| arbitration | **17** | §S5-mapping found; **two readings** | presented, awaiting |
| arbitration | **24** | ambiguous epistemic premise | to inventory |
| arbitration | **28** | survivorship confound unaddressed | to inventory |
| arbitration | **P-4(b)** | (a) established, (b) interpretation | partly |

### 49 -- cover letter, propagate `paper.tex:359`

`cover_letter.md:60-62` reads "Published Pulse validation work samples ARDS
severity **only on round tenths** and **never probes inside this interval**."

`paper.tex:359` is precise where the letter is not:

> Pulse's own methodology documents ARDS severity as a continuous parameter on
> [0, 1] and **exemplifies the range** with the round-tenths convention {0.0, 0.3,
> 0.6, 0.9, 1.0}; published Pulse validation work **and HowTo examples sample at
> most up to severity 0.9** and **do not examine impairment fractions inside the
> interval 0.91--0.945**.

⚠️ Two defects, and the second is the serious one. The letter moves the
round-tenths convention from **Pulse's documentation**, where it exemplifies a
range, onto **validation work**, where it becomes a sampling grid. And "this
interval" refers to the **[0.879, 0.945]** stated two lines earlier in the same
bullet -- **our own extension** -- where the established non-examination covers only
**0.91--0.945**.

**Proposed**: "Published Pulse validation work and HowTo examples sample at most up
to severity 0.9 and do not examine impairment fractions inside 0.91–0.945."

### 38 -- five loci, propagate the supplement's crossover finding

The audited statement is that the pattern **reverses**:

> `supplement.tex:504` -- "the per-bin sex pattern **crosses over**: female
> divergence dominates the (0.85, 0.91] bin while male divergence dominates the
> (0.91, 0.945] bin"
> `supplement.tex:527` -- "Female divergence dominates the lower band; male
> divergence dominates the upper band"

`paper.tex` says only "both sexes diverge" -- neutral and correct. **"Approximately
sex-balanced" flattens a sign-reversing effect into no effect** at
`README.md:108`, `README.md:156`, `manuscript.md:338`, `:2008`, `:2232`.
`README.md:108` is partly self-correcting, appending "the sex effect is
regime-dependent"; the other four are bare.

### P-2 -- two loci, and the monograph refutes itself 465 lines apart

⚠️ **`paper.tex` and `supplement.tex` mention PALICC **zero** times.** Both attribute
the bands exclusively to the Berlin Definition, three times in the paper: "The
mild/moderate/severe labels are **Berlin Definition** bands, set by the arterial
PaO$_2$/FiO$_2$ ratio" (`paper.tex:168`).

The monograph carries **five** PALICC mentions, and only two are defects:

| locus | text | verdict |
|---|---|---|
| `manuscript.md:44` | "three ARDS severities, **spanning PALICC-2 mild–severe**" | ⚠️ credits the bands |
| `manuscript.md:954` | "**S2** Mild ARDS, impairment 0.26 (**PALICC-2 mild**)" | ⚠️ credits the band |
| `manuscript.md:384` | glossary row defining the acronym | ✅ definition, not a credit |
| `manuscript.md:507-512` | "calibrated on the **Berlin Definition's** PaO2/FiO2 bands…; **PALICC-2** … is cited as the **parallel pediatric** severity framework; note that PALICC-2 itself favours Oxygenation Index" | ✅ **canonical, and correct** |

**The monograph therefore contains its own repair.** L44 and L954 should credit
Berlin, exactly as L509 does.

⚠️ **Recorded, not actioned**: `CLAUDE.md` also lists "S2 0.26 Mild ARDS
(PALICC-2)". It is project rules rather than a manuscript, so it is out of the
manuscript population -- but it is plausibly where the two defective loci came from.

**None of the three applied.**


---

## Sections swept, and to what depth

| Section | Depth | Result |
|---|---|---|
| §S1 | full prose, 3 paragraphs | 1 signal (BioGears) |
| §S2 | full prose + all 12 table rows untruncated | 1 signal (confirms/extends); cardinal "twelve" verified — rows 5–6 are merged, so 11 physical rows carry 12 numbered limitations; all 12 match the repository's reference table one-to-one |
| §S3 sampler constants | full | clean — 20 trajectories / 4 levels / seed 42, ledger-extracted from `run_full_sweep.py` |
| §S3 flag priority | full | signal 3 |
| §S3 traffic-light sensitivity | full + recomputed | clean, and exemplary: three readings each sum to 48; the implemented row 7/29/12 matches a manual cell-by-cell count of Figure 2; the green set is invariant because only S2_F and S3_F carry zero hard flags, which `cell_flag_summary.csv` confirms |
| §S3 baseline robustness | full | clean — 0 of 24 female cells change colour under an (S1,F) baseline; 4 scenarios × 6 outputs = 24 |
| §S3 PaO2 ceiling | full + recomputed | clean — 32 + 2 = 34; 21 F + 11 M = 32; Vt 800 mL × RR 20 = 16 L/min; the paper's 91 % is 31/34; the 126 implausible total matches `cell_flag_summary.csv` |

Remaining: the rest of §S3, then §S4 through §S17.


---

## Bloc scientifique appliqué -- 2026-08-24

Sept dossiers appliqués après arbitrage de l'auteur. Gates : `audit_claims.py
--check-paper-sync --check-monograph` **382/382 ancres, 94/94 crosswalk, 26/26
monographie, 15 gardes à 0 FAIL, exit 0** ; `check_render.py` **PASSED** (paper
37 p., supplement 52 p., inchangé) ; les trois builds OK.

### Source primaire ouverte : PALICC-2 (Emeriaud 2023)

Téléchargée et lue dans la session (`pdftotext -layout`), p. 147-148 :

- **DS 1.4.1** -- « Oxygenation index (OI) or oxygen saturation index (OSI), **in
  preference to** Pao2/Fio2 or Spo2/Fio2, should be the **primary metric of lung
  disease severity** to define PARDS for all patients treated with **invasive
  mechanical ventilation** (IMV) » (Ungraded DS, 90 % agreement).
- **DS 1.4.2** -- P/F ou S/F pour NIV / HFNC.
- Table de stratification : **IMV-PARDS = mild/moderate (OI < 16 ou OSI < 12) vs
  severe (OI >= 16 ou OSI >= 12)** ; NIV-PARDS = mild/moderate (P/F > 100) vs
  severe (P/F <= 100).

Trois conséquences :

1. `manuscript.md:511` (« PALICC-2 itself favours OI/OSI over P/F ») est
   **vérifié correct**, et même prudent.
2. `Pulse_translation_new/experiments_log.md:604` (« PALICC-2 uses the same
   PaO2/FiO2 cutoffs ») est **faux pour l'IMV**. ⚠️ Consigné ici seulement :
   **NO-GO** de l'auteur sur toute écriture dans le dépôt Paper 1.
3. ⚠️ **Décisif** : pour l'IMV, PALICC-2 **ne sépare pas « mild » de
   « moderate »**. Les deux étiquettes distinctes de `preregistration.md:108-109`
   désignent donc des strates qui n'existent pas dans ce cadre pour un patient
   ventilé invasivement -- ce que l'atlas simule (VC-AC).

### Ce qui a été appliqué

| # | dossier | loci |
|---|---|---|
| D1 | erratum daté, **append-only** | `preregistration.md` +10 lignes, 0 supprimée ; texte historique intact |
| P-2 | étiquettes Berlin | `manuscript.md` L44, L954 ; PALICC monographie 9 -> 7 |
| 49 | portée 0,91--0,945 propagée de `paper.tex:359` | `cover_letter.md` L60-62 |
| 38 | « aggregate near-balance + sex asymmetry reversed » | README 108/156 ; `manuscript.md` 338/2008/2232 |
| 17 | mécanisme audité de §S5.2, sans « kinetics » ni équation prédictive | `supplement.tex:701` |
| B3 | titre + légende descriptifs | `supplement.tex:699`, `:705` |
| jumeaux | « shunt-fraction kinetics » éliminé | `manuscript.md` 1634, 1796, 1871, 2751 (2751 = réparation propositionnelle complète) |

⚠️ **Le quatrième jumeau était coupé par un retour à la ligne** (« shunt-fraction »
/ « kinetics » sur deux lignes) : un grep sur la locution complète n'en trouvait
que 3 sur 4. Contre-mesure : chercher le radical, pas la locution.

### Mesure d'audit, non publiée

Différence alvéolo-artérielle calculée sur les 16 runs S3/S4 (moyenne t >= 240 s,
12 points, PAO2 = 713 - PaCO2/0,8, constantes de `paper.tex:325`) :

| | PaCO2 mesurée | PAO2 calculée | PaO2 mesurée | A-a |
|---|---|---|---|---|
| S1 (publié) | 40 (hypothèse) | 663 | 643,3 | ~20 |
| S3 (8 runs) | 42,0--66,8 | 629,6--660,5 | 85,6--282,9 | **377--553** |
| S4 (8 runs) | 39,6--64,9 | 631,9--663,4 | 67,1--79,3 | **557--592** |

Le plafond calculé ne bouge que de ~34 mmHg pendant que PaO2 chute de ~570 : la
formulation qualitative de `supplement.tex:701` est vraie et robuste. **Décision
de l'auteur : ces chiffres restent au registre**, aucun ajout au SI (ils
exigeraient script, provenance et ancre de ledger).

### Signaux ouverts créés par ce bloc, non actionnés

- **63** -- `manuscript.md:1763` : « mechanism: shunt-fraction caps FiO2's
  marginal effect » (texte alternatif de figure). Famille shunt large, NO-GO.
- **64** -- « Shunt depression confirms... » `manuscript.md` L2731/L2827 (à
  re-localiser après décalage) et `paper.tex:289` (« the same shunt physiology
  that flattens PaO2 »). Deux lectures défendables pour le locus du papier.
- **65** -- `manuscript.md:2748` « The same FiO2 = 1.0 + **identical input
  vector** » : la médiane S1 publiée porte sur 44 runs (22 index x 2 corps), les
  médianes S3/S4 sur 4 index. La comparaison appariée existe dans les données
  (index 0006/0007/0012/0013 sur les 6 cellules, entrées identiques vérifiées)
  mais n'est pas celle qui est publiée.
- **66** -- `experiments_log.md` S021 : la prédiction préenregistrée du carnet est
  `S1 > S2 > S3 > S4`, or **aucun bras S2 n'a été exécuté** (44/8/8).

### D2 appliqué -- convention à deux étages (2026-08-24)

**Population énumérée et affichée avant toute édition**, à la demande de
l'auteur : **24 occurrences d'« ARDSnet », 16 dans le périmètre, 8 hors.**
Partition complète, sans recouvrement.

⚠️ **Deux corrections de mon propre classement, faites en lisant le contexte :**

1. `4261` disait « at **the same** … settings » : c'est un **référent**, pas un
   définisseur. Le définisseur du bloc est la puce `4233`, qui porte
   l'arithmétique. Définisseurs = `975` et `4233`, pas trois.
2. Le contrôle d'antécédent exigé par l'auteur a fait passer **deux loci de plus**
   à la forme complète : `92` (résumé exécutif, aucun antécédent) et `4195`
   (introduction d'annexe : les réglages n'arrivent que 28 lignes **plus bas**,
   donc renvoi vers l'avant).

Répartition finale : **4 loci en forme complète ou auto-suffisante** (`975`,
`4233`, `92`, `4195`) · **3 en forme courte avec pointeur explicite**
(`supplement.tex:496` → `\S\ref{sec:s5-berlin}` ; `3820` et `3904` → Appendix
B.3) · **9 en forme courte à antécédent local**.

**Une édition supplémentaire, imposée par le contrôle d'antécédent** :
`manuscript.md:359` portait « Vt 6 mL/kg » sans référent de poids dans la puce
même qui sert d'antécédent à `355`. Corrigé en « 6 mL/kg actual body weight ».

✅ **Le nom court n'est pas une invention** : `supplement.tex:431` employait déjà
« a fixed **reference ventilation setting** ». La convention propage le
vocabulaire existant du document, pas une étiquette neuve.

**Vérification, avec témoins :** « ARDSnet-protective » **0** · « ARDSnet
lung-protective » **0** · « at ARDSnet settings » **0** · « ARDSnet anchor »
**0**. Population ARDSnet **24 → 12** (11 lignes ; `803` en porte deux) : les 9
occurrences hors périmètre intactes, plus 3 qui conservent le lien historique
sous la forme hedgée « based on the ARDSnet framework ». Les 14 usages de la
forme courte ont tous un antécédent résoluble -- **aucun référent flottant**.

**Gates après application :** `audit_claims.py --check-paper-sync
--check-monograph` **382/382 · 94/94 · 26/26 · 19 gardes à 0 FAIL · exit 0** ;
`check_render.py` **PASSED** (paper 37 p., supplement 52 p., pagination
inchangée) ; les trois builds OK, zéro référence non définie.

**Rien poussé.**


### Provenance du `8 of 20` de `paper.tex:388` -- dérivé 2026-08-25

La phrase : « Configuration-time clipping shortened **9 of 20** DBP steps and
caused applied DBP to co-vary in **8 of 20** SBP steps ». Le 9/20 était ancré au
ledger, le 8/20 ne l'était pas et n'avait jamais été re-mesuré. **Les deux le
sont maintenant**, sur un artefact committé.

**L'unité, définie avant de compter.** Les « 20 pas » sont les pas élémentaires
du plan Morris partagé : 20 trajectoires x 8 points = 160, rejouées à
l'identique dans chaque cellule. Ce n'est PAS 20 par cellule. Dans
`results/input_instantiation_long.csv`, l'index de `run_id` (`S1_F_0000` ..
`S1_F_0159`) reproduit ce plan ; la trajectoire *t* occupe les runs 8t..8t+7.

**Les deux prédicats, posés avant le comptage.**

- *pas DBP raccourci* : sur la transition où le DBP échantillonné varie et le
  SBP ne varie pas, `|delta appliqué| < |delta échantillonné|`.
- *co-variation dans un pas SBP* : sur la transition où le SBP varie et le DBP
  échantillonné ne varie pas, le DBP **appliqué** change malgré tout -- le clip
  `DBP <= 0.75 x SBP` dépendant de SBP.

**Résultat** : 20 pas DBP identifiés dont **9 raccourcis** ; 20 pas SBP
identifiés dont **8 à co-variation**. Conforme au texte publié.

**Trois témoins.**

| témoin | attendu | obtenu |
|---|---|---|
| positif -- le clip est actif | > 0 | **35 des 160 points** ont DBP appliqué < échantillonné |
| croisé -- le plan est partagé, donc toute cellule doit donner la même chose | 9 et 8 | **S4_M : 9 et 8** ; **S2_F : 9 et 8** |
| négatif -- groupement volontairement faux (trajectoires de 7 au lieu de 8) | pas 20/20 | **18 pas DBP, 22 pas SBP** |

Le témoin structurel est le plus fort : la décomposition correcte trouve
**exactement** 20 pas DBP et 20 pas SBP, ce qu'un plan à 20 trajectoires doit
donner. Une hypothèse fausse sur le groupement produit autre chose, comme le
témoin négatif le montre.

⚠️ **Non ancré au ledger, délibérément.** Ajouter une ancre exigerait de
modifier `scripts/audit_claims.py` -- un changement d'outillage disproportionné
à la veille d'un envoi. La dérivation est reproductible en une commande `awk`
sur un CSV committé ; la décision d'automatiser cette classe de résultats est
séparée et reste ouverte.

---

## Décision de périmètre — le contrôle de stabilité seed 43 n'est pas rapporté (2026-08-25)

**Ce qui existe.** S009 a produit un second contrôle de stabilité du classement
Morris, distinct de celui que le papier rapporte :
`results/seed_stability_S2M_seed43.parquet` et
`results/seed_stability_top3_comparison.csv`.

**Ce qu'il dit, et il est moins favorable.** Sur la cellule S2_M :

| contrôle | design | top-3 conservés | ordre conservé | rang 1 conservé |
|---|---|---|---|---|
| seed 44 (rapporté, §S3.13) | 160 points, taille égale | **4 / 6** | **3 / 6** | 6 / 6 |
| seed 43 (S009, non rapporté) | 80 points, demi-taille | **3 / 6** | **1 / 6** | 5 / 6 — PaCO2 passe de `vt` à `rr` |

**Pourquoi ce n'est pas un rapport sélectif.** Les deux ne mesurent pas la même
chose. S009 déclare le sous-dimensionnement comme intentionnel : « *New
canonical Morris sample at `seed=43`, `trajectories=10`, `levels=4` → 80 unique
points (half the published 160). Smaller sample is intentional: cheaper compute,
wider Morris CI by construction, so any match with the published top-3 ranking
is robust evidence; any mismatch tells us the ranking is not invariant to sample
size.* » Le contrôle seed 44 teste la graine à taille constante ; le contrôle
seed 43 teste la sensibilité à la taille d'échantillon. Un désaccord du second
est un résultat attendu de sa conception, pas une contradiction du premier.

**Mesure de l'absence.** Le supplément ne mentionne le contrôle demi-taille sous
aucune forme : `seed 43` = 0, `80 points` = 0, `80 unique` = 0,
`10 trajectories` = 0, `ten trajectories` = 0, `half the` = 0. Seul `seed 44`
apparaît, une fois.

**Décision.** Ne pas rouvrir le manuscrit pour l'ajouter avant l'envoi aux
relecteurs. Décision de périmètre assumée par le mainteneur, consignée ici pour
que l'absence soit traçable et non un oubli. Si un relecteur demande la
sensibilité du classement à la taille d'échantillon, la donnée existe et la
réponse est ci-dessus.
