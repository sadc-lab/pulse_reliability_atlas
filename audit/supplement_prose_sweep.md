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
| 1 | §S1 ¶116 | "…that are not present in BioGears" — comparative claim of ABSENCE about a third-party project, uncited | **OPEN — needs primary source or removal** |
| 2 | §S2 Table row 4 | "a continuous-severity micro-sweep **confirms** the band" where §S5, Fig. S1 and the Discussion all say the sweep **extends** it to [0.879, 0.945] | ✅ **CLOSED `04d6f0f`** — now "confirms it and extends the low edge to 0.879" |
| 3 | §S3 | Four prose uses of "detector" for the object `paper.tex` calls "classifier" 33 times | **OPEN — needs per-occurrence semantic arbitration** |
| 4 | §S3 clamp patch note | "all **3,348** Pulse logs on disk" — a `find data -name pulse.log` today returns **3,349** | **OPEN — low severity, unresolved** |
| 5 | §S4 ¶392 and §S8 ¶650 (+ §S4 title, to arbitrate) | Two hard-coded references send the reader to "**Table 1** of the main manuscript" for per-cell flag counts. Paper Table 1 is the terminology glossary; the per-cell breakdown is **Table 3**. ⚠️ Three OTHER `Table~1` references are CORRECT and must not be swept | **OPEN — wrong pointer** |
| 6 | supplement p52 | The last page of the supplement carries **no page number**; it is the only such page in 52. It holds Table S16, a `[h]` float that LaTeX defers to the end | **OPEN — cosmetic but visible** |
| 7 | §S5 ¶433 | "reproduces the published anchors to **within 0.6 %**" — on the displayed integers (256, 150, 96) the worst case is 96 -> 96.6 = **0.625 %** | **OPEN — low severity, likely a rounding artefact** |
| 8 | §S6, **2 loci** | Calls S2 and S3 "the **moderate**-ARDS scenarios", and the pair "the moderate-ARDS **regime**". S2 is **mild** ARDS (0.26) everywhere else — 11 loci say so. Mild and moderate are distinct Berlin bands (P/F 200-300 vs 100-200) | **OPEN — clearest internal contradiction found; clinical category** |
| 9 | §S7 ¶597 | Quotes the Discussion as ``80 of 85 Hoeffding rejections fall on channels the present atlas does not assess''. That string occurs **0 times** in `paper.tex`; the Discussion says "82 of 85 fall outside the four-channel overlap: 80 on channels the present atlas does not assess" | **OPEN — quotation marks around a paraphrase** |
| 10 | §S7 ¶597 vs its table caption | Prose says "**Cornish's Table~4**" and "their **Appendix** Table~5"; the caption says "Cornish **Appendix Tables~4 and~5**". Same document, two accounts of where Cornish's Table 4 lives | **OPEN — internal contradiction; needs the source** |
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
| 23 | §S12 ¶903 | "`kitware/pulse:4.3.1` is published for `linux/amd64` **only**" and "**no** prebuilt ARM64 image exists" | OPEN — two absence claims, **trigger criterion (b)** |
| 24 | §S13 ¶931 | "The SHAP cross-verification works **because the underlying physiology is real**, not the other way round" — two readings, one of which contradicts the Figure S5 disclaimer | OPEN — ambiguous epistemic premise |
| 25 | §S13 ¶931 | "input dependencies that **any reasonable statistical method** would identify on the same data" — an unbounded universal from **two** methods | OPEN — **downgraded**: wording only; the "undercut by its own numbers" reading was mine and is withdrawn |
| 26 | §S14 ¶939 | Of eight claims about what the monograph **contains**, two overclaim: "the **full preregistration document** with its amendment history" (§2.0 reproduces only §Primary hypotheses) and "the **complete experiment-log entries**" (Appendix A is a 43-line index) | **OPEN — checkable by anyone who downloads the Zenodo deposit** |

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

Not resolvable from inside the repository: it is a claim about the cited paper's
structure, and `audit/reference_audit.md` records the Cornish figures (85
Hoeffding, 281 bootstrap, 15 channels) without locating the tables. Escalation
needs the source opened.

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

**This is the first signal to trigger criterion (b) of the citation rule agreed
this session** — open the primary source when the sentence asserts an absence,
exclusivity or negation. The source to open is `pulsepatientmethod`, which §S10
already cites for the allometric formula. Deferred to the combined citation pass.

Consequence if wrong is bounded: the recommendation to the maintainers becomes
moot, and no scientific result moves.

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
emulated rather than native — rests on them. Deferred to the combined citation
pass; the check is a Docker Hub manifest query.

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
