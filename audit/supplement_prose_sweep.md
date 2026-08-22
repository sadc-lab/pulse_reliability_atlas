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
| 2 | §S2 Table row 4 | "a continuous-severity micro-sweep **confirms** the band" where §S5, Fig. S1 and the Discussion all say the sweep **extends** it to [0.879, 0.945] | **OPEN — wording agreed, not yet applied** |
| 3 | §S3 | Four prose uses of "detector" for the object `paper.tex` calls "classifier" 33 times | **OPEN — needs per-occurrence semantic arbitration** |
| 4 | §S3 clamp patch note | "all **3,348** Pulse logs on disk" — a `find data -name pulse.log` today returns **3,349** | **OPEN — low severity, unresolved** |
| 5 | §S4 ¶392 and §S8 ¶650 (+ §S4 title, to arbitrate) | Two hard-coded references send the reader to "**Table 1** of the main manuscript" for per-cell flag counts. Paper Table 1 is the terminology glossary; the per-cell breakdown is **Table 3**. ⚠️ Three OTHER `Table~1` references are CORRECT and must not be swept | **OPEN — wrong pointer** |

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
