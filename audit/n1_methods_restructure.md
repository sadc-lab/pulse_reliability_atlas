# N-1 — Removing Supplementary Methods: measurement before restructuring

**The finding.** npj Digital Medicine states twice that Supplementary Methods
are not permitted (`audit/npj_format_compliance.md` §N-1). Our supplement
carries §S3 *Full Methods detail*, whose own opening sentence announces it as an
expansion of the main Methods section.

**Why this register exists.** The obvious remedy — move §S3 into §4 — rests on
a premise that turns out to be false: that §S3 contains method the main text
lacks. Measured block by block, most of it does not. This register records the
measurement, so the restructuring is driven by what is actually missing rather
than by the section's title.

Measured at `969b618`, 2026-08-02.

---

## 1. Volumes

Counting rule: LaTeX commands stripped, escaped `\%` protected from the comment
regex, tokens containing at least one alphanumeric character counted. Table and
`lstlisting` bodies counted separately from the prose that introduces them,
because a table moves as a unit and its cells are not prose.

| | prose | tables / listings | total |
|---|---:|---:|---:|
| `paper.tex` §4 Methods | 2,547 | 0 | **2,547** |
| `supplement.tex` §S3 | 2,845 | 973 | **3,818** |

The npj register quoted 2,512 and 3,804 from a different counter. The two agree
within 1.4 %; neither figure is used below for anything but scale.

Per block:

| block | lines | prose | tables |
|---|---|---:|---:|
| preamble | 148–150 | 62 | — |
| S3.1 `sec:s3-engine` | 151–154 | 149 | — |
| S3.2 `sec:s3-morris` | 155–158 | 193 | — |
| S3.3 `sec:s3-clip-cost` | 159–166 | 353 | — |
| S3.4 `sec:s3-sobol` | 167–176 | 514 | — |
| S3.5 `sec:s3-detector-order` | 177–180 | 198 | — |
| S3.6 `sec:s3-hard-bounds` | 181–231 | 344 | 525 |
| S3.7 `sec:s3-drift` | 232–280 | 254 | 419 |
| S3.8 `sec:s3-clamp` | 281–296 | 298 | 29 |
| S3.9 `sec:s3-traffic` | 297–302 | 196 | — |
| S3.10 `sec:s3-bodies` | 303–310 | 284 | — |

## 2. Token-overlap scan

For each block, every numeric literal, `\texttt{}` identifier and `\cite{}` key
was tested for presence in §4 and in `paper.tex` as a whole.

The scan is **substring-based on normalised text, so its "absent" verdicts are
reliable and its "present" verdicts are not** — a short numeral such as `5` or
`50` matches somewhere in any long document. Every "present" verdict used below
was therefore re-confirmed by reading the passage.

| block | tokens absent from §4 | what they are |
|---|---:|---|
| S3.1 engine | 0 | — |
| S3.2 morris | 9 | `SWEEP_TRAJECTORIES`, `SWEEP_LEVELS`, `SWEEP_SEED`, `scripts/run_full_sweep.py`, `morris.sample`, ledger anchors `T1.06e/f/g` |
| S3.3 clip-cost | 16 | the clip-cost result itself |
| S3.4 sobol | 7 | the bootstrap-stability result |
| S3.5 detector-order | 1 | the priority string's trailing `> clean` |
| S3.6 hard-bounds | 38 | ledger anchors `T1.06p.*`, `src/detector.py`, the rationale table, the F-003 reclassification paragraph |
| S3.7 drift | 19 | ledger anchors `T1.06q.*`, `DRIFT_MAX_DELTA_60S`, **`0.02`**, `CV_THRESHOLD = 0.05`, `std / \|mean\| < 0.01` |
| S3.8 clamp | 4 | `3,348` logs, `src/detector.py`, the `minimum … baseline allowed is` pattern |
| S3.9 traffic | 2 | `preregistration.md`, `scripts/baseline_robustness_check.py` |
| S3.10 bodies | 10 | `216.5`, `214.99`, unrounded weights, allometric constants, unrounded blood volumes |

## 3. What §4 already contains — verified by reading, not by the scan

| S3 block | status in §4 | locus |
|---|---|---|
| S3.1 engine | Docker pinning and the three-layer bit-exact reproduction: **present**. Wrapper architecture: **absent**. | §4.1 L325 |
| S3.2 morris | SALib, 20 trajectories, 4 levels, seed 42, 8 evaluations, 160/1,280, all seven ranges, the DBP-clip rationale, the requested/applied persistence, "every configuration lies inside the accepted envelope": **all present**, several near-verbatim. | §4.3 L335, §4.2 L331 |
| S3.5 detector-order | The order and a one-sentence rationale ("a breached input contract outranks a solver failure, which outranks a biologically impossible result, which outranks one that has simply not settled"): **present**. The four per-flag justifications: **compressed**. | §4.4 L339 |
| S3.6 hard-bounds | All six `(lower, upper)` pairs are listed inline and match `tab:hard-bounds` exactly (SpO₂ shown as 50/100 % where the table shows the 0.50/1.00 fraction). The 600-vs-700 mmHg sensitivity analysis: **present**. | §4.4 L339 |
| S3.7 drift | **Nothing.** `drift` occurs 7 times in `paper.tex` and never carries a threshold value — only "its own locked per-channel threshold". The OLS estimator and the 13-point window are present; the six magnitudes and the flatline constants are not. | §4.4 L339 |
| S3.8 clamp | "any of 4 documented input-rejection patterns" — the count, not the patterns. The 2026-07-26 five-pattern patch: **absent**. | §4.4 L339 |
| S3.9 traffic | The complete scoring rule — both ingredients, the (S1, M) baseline, the 10 % / 30 % bands, their preregistration, and all three colour criteria — is stated in the **Figure 2 legend**. | L226 |
| S3.10 bodies | Both bodies, both weights, the CDC 214-month provenance, the 18.0-year comparison, both height rationales: **present**. | §4.2 L329 |

## 4. Consequence: the gap is four items, not seven blocks

Genuine npj non-compliance — method that exists **only** in Supplementary
Information:

1. **Drift thresholds** (S3.7): the six per-channel magnitudes and
   `DRIFT_MAX_DELTA_60S`. Hard gap — the classifier's calibration constants
   appear nowhere in the main text.
2. **Flatline criterion** (S3.7 closing paragraph): `std / |mean| < 0.01` and
   the within-0.1 %-of-bound condition. Hard gap, same reason.
3. **Clamp regex set** (S3.8): the five patterns and the four-pattern set the
   sweep was classified with. Hard gap — the main text gives the count only.
4. **Engine-wrapper architecture** (S3.1): soft gap, two sentences.

Everything else in §S3 is one of three things, none of which npj's rule reaches:
already in the main text (S3.2, S3.6 bounds, S3.9 rule, S3.10 bodies), a
**result** rather than a method (S3.3, S3.4, S3.9 robustness check, S3.6
reclassification paragraph), or **provenance and rationale** (the two rationale
tables, S3.10's erratum).

Moving the already-present blocks would duplicate the main text rather than
comply with anything. Recorded here so that decision is made on the measurement.

---

## 5. Does the destination accept what we want to put in it?

Re-read at source on **2026-08-02**, same two pages as the npj register, same
303-redirect handling through `idp.nature.com`.

| Question | Answer at source |
|---|---|
| Main-text word limit for an Article? | **Absent.** Neither page states one. |
| Cap on the number of display items? | **Absent.** Neither page states one. |
| Where do tables go? | `SG`: *"Please submit tables at the end of your text document (in Word or TeX/LaTeX, as appropriate)."* Placement only, and the register already files placement under *binds at acceptance only*. |
| The rule N-1 rests on | `CT`, Methods row, verbatim: *"All descriptions of Methods should be provided in the main manuscript file and not in the Supplementary Information"*. `SG`, verbatim: *"The journal does not permit Supplementary Methods, all Methods should be reported in the main manuscript file."* Both confirmed word for word. |

So moving a table and a code listing into §4 breaks no npj rule. `paper.tex`
currently carries 3 tables and 5 figures; nothing caps that.

**One real constraint does exist**, from the register's own C-14: the
traffic-light legend is the longest in the paper at **319 words against npj's
350-word cap**. Only ~31 words of headroom. Nothing may be added there.

## 6. Second pass — the claims of §3 re-verified at phrase level

The token scan of §2 is substring-based. Each verdict below was re-checked with
a phrase-level search, which is what the conclusions actually rest on.

| claim | verdict | evidence |
|---|---|---|
| S3.2's science is already in §4 | **holds** | Sentence by sentence, 5 of its 6 atoms appear in §4.2/§4.3, one near-verbatim (*"Every configuration … lies inside the accepted envelope"*). `one-at-a-time` occurs in `paper.tex`. Unique: the three sweep constants, `scripts/run_full_sweep.py`, `morris.sample`, `T1.06e/f/g`. |
| The six bound pairs are inline in §4.4 | **holds** | Read at L339; all six match `tab:hard-bounds` exactly, SpO₂ in percent where the table uses the fraction. |
| The traffic-light rule is in the Figure 2 legend | **holds** | Read at L226: both ingredients, the (S1, M) baseline, the 10 %/30 % bands, their preregistration, all three colour criteria. |
| The bodies are in §4.2 | **holds, and more so** | The allometric relation `BV = 65.6 · weight^1.02` is also in the main text, at L285 in §2.5. |
| The drift thresholds are absent from the paper | **holds** | `drift` occurs 7× in `paper.tex` and never carries a value. The single `0.02` in the file is the engine's 0.02 s timestep at L134, not the SpO₂ drift threshold. |
| The clamp patterns are absent | **holds** | The paper gives the count only: *"any of 4 documented input-rejection patterns"*. |

### 🔧 Two corrections to the first pass

**(i) The F-003 reclassification is not in the paper at all.** §3 above recorded
the 600-vs-700 mmHg sensitivity analysis as "present" in §4.4. What §4.4 carries
is the *pointer* — the alternative dictionary and the 700 mmHg value. The
result itself (*"32 of the 34 runs"*, the 31 / 21 / 11 breakdown, the two
runaway runs) occurs **0 times** in `paper.tex`. It is a supplementary result,
which is where it belongs; the row overstated the main text's coverage.

**(ii) The cross-reference count is 18, not 11.** The earlier cartography
counted subsection-level references only.

| target | in `paper.tex` | in `supplement.tex` |
|---|---:|---:|
| bare `sec:s3` | **7** | 0 |
| `sec:s3-clip-cost` | 2 | 0 |
| `sec:s3-sobol` | 1 | 1 |
| `sec:s3-hard-bounds` | 1 | 0 |
| `sec:s3-drift` | 1 | 2 |
| `sec:s3-bodies` | 1 | 0 |
| `sec:s3-detector-order` | 0 | 1 |
| `sec:s3-clamp` | 0 | 1 |
| **total** | **13** | **5** |

The seven bare `\ref{sec:s3}` all point at *Full Methods detail*, the one label
guaranteed to disappear. They are the largest mechanical risk in the operation.

### Two items neither pass had classified

- **The bound taxonomy** (S3.6, L203): *"Each bound falls into one of two
  logical categories … No bound rests on an equipment specification."* Absent
  from the paper (`hemoglobin saturation` 0× there, 4× in the supplement). It
  is justification, not a constant.
- **The single-baseline trade-off** (S3.9, L299): *"Scoring every cell against a
  single (S1, M) baseline keeps male and female cells on one comparable scale,
  at the cost of folding legitimate male–female physiological differences into
  the female cells' deviation term."* Absent from the paper. It is a stated
  limitation of a scoring rule the Methods section never describes.

### An observation the audit did not set out to make

`paper.tex` §4 has six subsections — engine, patients, sweep, detector,
statistics, AI. **None of them describes how the traffic-light map is built.**
The rule lives in a figure legend and in §S3.9. A figure legend is inside the
main manuscript file, so this is compliant as it stands; it is recorded because
the map is the paper's primary deliverable and its construction is the one
method the Methods section does not state.

Two rationale-table citations, `marini2018critical` and `marino2013icu`, appear
in `supplement.tex` only. If either rationale table moved to the paper, both
would have to be added to `paper.bib` and to the main reference list.

## 7. What deleting the duplicated blocks would cost the audit

`--check-paper-sync` counts literal occurrences over the **combined** corpus.
A guarded literal living inside a deleted block loses an occurrence and the
entry fails. Measured against all 98 crosswalk entries before deleting
anything:

| block proposed for deletion | crosswalk entries hit |
|---|---|
| S3.2 Morris sampler | 4 — `1{,}280` 39→38, `20 trajectories` 5→4, `4 grid levels` 2→1, `seed 42` 2→1. Each literal survives elsewhere; only the count moves. |
| `tab:hard-bounds` | 6 — `HR (bpm) & 20 & 220`, `MAP (mmHg) & 30 & 180`, `Vt (mL) & 50 & 1500`, `SpO$_2$ (fraction) & 0.50 & 1.00`, `PaO$_2$ (mmHg) & 20 & 600`, `PaCO$_2$ (mmHg) & 10 & 120`. **All six drop to zero** — the table is their only witness. |
| S3.9 scoring-rule paragraph | **0.** Nothing guarded lives in it. |

The six table-row entries would have to be struck from the crosswalk, not
decremented: the audit surface would fall from 98 to 92. That is a real loss of
coverage, and it is avoidable — see the revision below.

Note that each bound is guarded twice, in two shapes: the table-row form above,
and an inline form (`HR [20, 220]~bpm`, expected 2 — once in `paper.tex` §4.4,
once in `tab:hard-bounds-rationale`). Only the table-row guard is at risk.

## 8. Three revisions to the plan, forced by §7 and by the SI's actual shape

**(a) Merging `tab:hard-bounds` must carry the numbers, not drop them.**
The merged `tab:hard-bounds-rationale` should gain Lower / Upper columns and
the `T1.06p.*` anchors, and the six crosswalk literals should be **repointed to
the new row shape** rather than struck. The audit stays at 98 entries and every
bound keeps two independent guards.

**(b) S3.2 should shrink, not vanish.** Its unique payload — the three sweep
constants in `scripts/run_full_sweep.py` and the `T1.06e/f/g` anchors — is real
provenance. A short code-provenance note keeps it; the duplicated 190 words of
sampler description go.

**(c) A "Supplementary Results" umbrella section was the wrong idea.** The SI
is *already* mostly supplementary results: S4, S5, S6, S7, S8, S9, S10, S13,
S15 and S16 all report findings. Gathering three blocks under a new umbrella
would leave ten result sections outside it, and promoting them to top-level
sections would renumber S4–S17 and every reference into them.

**Lower-risk structure: keep §S3 as one section, retitled, and regroup its
subsections** — provenance first, then the analyses that are not method. This
keeps the `sec:s3` label alive, renumbers nothing, and still removes both
things N-1 objects to: the title *Full Methods detail* and the opening sentence
that announces the section as an expansion of §4.

## 9. 🔴 A pre-existing defect found while checking the cross-references

`paper.tex` §2.2, on the Morris heatmaps:

> "Four cross-output patterns emerge directly from Figure~\ref{fig:morris}
> (**full per-cell tables in Supplement~\S\,\ref{sec:s3}**)."

**No such table exists.** `supplement.tex` carries 15 tables — `tab:drift`,
`tab:drift-rationale`, `tab:hard-bounds`, `tab:hard-bounds-rationale`,
`tab:limits`, `tab:s4-nss`, `tab:s5-berlin-calib`, `tab:s5-berlin-sweep`,
`tab:s5-cont`, `tab:s5-mapping`, `tab:s6-rho`, `tab:s7-cornish`, `tab:s9-shunt`,
`tab:s15-comphr`, `tab:s16-index` — and not one of them is a per-cell $\mu^{*}$
table. The nearest, `tab:s6-rho`, reports cross-sex Spearman $\rho$ on the
rankings, not the per-cell $\mu^{*}$ values themselves. §S3 in particular holds
only the bounds and drift tables.

The sentence promises the reader a table the supplement does not contain. This
predates the present work and is **not** a consequence of it.

Per the project's standing rule on a mismatch: recorded, **nothing modified**,
brought back for a joint decision.

## 10. A scope question N-1 did not ask

§S12 *Reproducibility recipe* carries the Docker invocation template and the
sweep, analysis and audit commands. Read maximally, npj's *"All descriptions of
Methods should be provided in the main manuscript file"* reaches that too. The
npj register flagged §S3 alone, because §S3 is the section that calls itself
Methods.

Recommendation: leave §S12 alone. A reproducibility recipe is an executable
appendix rather than a methods description, §4.1 already carries the pinning
and the three verification layers in prose, and Nature Portfolio actively asks
for this material. Recorded so the choice is deliberate rather than an
oversight.

## 11. Execution state

Nothing in `paper.tex` or `supplement.tex` has been modified. This register is
measurement only; the restructuring plan built on it awaits author approval.
