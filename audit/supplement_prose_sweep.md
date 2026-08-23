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
| 1 | §S1 ¶116 | "…that are **not present in BioGears**" — **four sub-claims, four different statuses** | ⚠️ **PARTIALLY ARBITRATED 2026-08-23** — 2 SUPPORTED · 1 SOURCE INSUFFICIENT · 1 **OVERCLAIMED** |
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
| 33 | `TODO_publication_roadmap.md:143` | A **live acceptance criterion** pinned to a stale count: "must stay **313/313** · 94/94 · 26/26 · 25/25 (currently green)" where the ledger is at **382** | **OPEN — nothing re-measures it** |
| 34 | `README.md:357` | "santino/ **S001 … S031** entries" where the log reaches **S032**. The same locus previously read S001…S025 and was corrected to S031 — **it has drifted again** | **OPEN — recurrence, nothing re-measures it** |
| 35 | Figure S5 legend, from `make_supp_fig_s5_decomposition.py:137` | The legend reads "as recorded by the **detector**" — a term the project retired, **baked into a rendered PDF**, so invisible to both a `grep` of `supplement.tex` and to the vocabulary guard | **OPEN — recurrence of the Figure 1 defect, one scope out** |
| 36 | `paper.tex:77` vs `submission_metadata.txt:12` | Running title case differs: "Reliability **A**tlas: Pulse Physiology Engine" against "Reliability **a**tlas: …" | OPEN — cosmetic, two submission artefacts |
| 37 | **3 loci**: `README.md:161`, monograph **L71**, monograph **L320** | "34 … **at FiO₂ = 1.0**" over-attributes: **31** are at 1.0, 3 at 0.7367. Four other loci state it correctly | **OPEN — count corrected; the monograph says it both ways** |
| 38 | **5 loci**: `README.md:108`, `:156`, monograph **L338**, **L2007**, **L2231** | "divergence approximately **sex-balanced**" flattens a sign-reversing effect. `paper.tex` and `supplement.tex` are **clean** — their single occurrences mean *cohort design*, a different claim | **OPEN — count corrected after a homonym false alarm** |
| 39 | **7 loci** across README, supplement and monograph | Sweep compute cost. **Re-derived from all 1,280 `run_meta.json`: aggregate container time is 41.12 h, not the 27 h stated.** Ideal wall floor 20.56 h at 2 workers, 13.71 h at 3. Every estimate in the corpus (~7 h, ~9 h, ~14 h) is **below the floor**; only the measured 23 h 01 m survives | OPEN -- **UPGRADED: not a disagreement between two documents, a corpus-wide contradiction with the data** |
| 40 | `README.md:261-266` | Announces "Manuscript S2.8 names **two** image hashes" and then prints **one**. The canonical sweep image `3b18bdc08660` is named in `manuscript.md:744` but dropped from the README bullet, which reads "Initial atlas image" with no hash. Not the S032 irrecoverable-image problem: the hash is recorded, it just fell out of the README | OPEN -- a promise the text does not keep |
| 41 | **3 loci**: `README.md:141`, `:323`, `:398` | "the silent FiO2 cap" stated with no scope, on a page whose headline says H2 NOT supported, Pulse "does **not** silently clamp" (0/1,280). Both are true and the monograph says why at S2.1 -- the cap is at the **wrapper layer**, and the atlas deliberately raises FiO2_MAX from 0.95 to 1.0 so the boundary reaches Pulse. The README never states wrapper != engine | OPEN -- legibility, not a factual error |
| 42 | `README.md:370` | Link text `Pulse_translation_new/` resolves to `https://github.com/santinon/` -- a user profile, not a repository. Public-facing broken pointer | OPEN -- cosmetic but visible to every reader |
| 43 | `README.md:255-257` | "Pulse 4.3.1 is bit-exact deterministic ... **so** reruns reproduce upstream values to 1e-6 relative tolerance" derives a weaker claim from a stronger one. Bit-exact implies tolerance 0. The correct scoping -- bit-exact *within* an image, 1e-6 *across* rebuilds -- is stated correctly 16 lines later at L271-274 | OPEN -- low; the same file already carries the right form |

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
| recruit | **16** ("Acinar recruitment", `recruitmentScalingFactor`) | **0** |

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
