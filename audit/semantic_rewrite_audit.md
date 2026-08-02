# Semantic audit of the rewritten passages

**Question this register answers.** The claim audit (`audit_claims.py`) verifies
that numeric literals still match their artefacts. It is blind to a passage
whose numbers survive verbatim while its *meaning* changes. This register closes
that gap for the rewrite window the author asked about.

**Why it was commissioned.** On 2026-08-01 a real instance of exactly this
failure was found in the abstract. The passage originally read *"median 643
mmHg"*. Commit `6403787`, trimming the abstract to npj's 150-word limit,
rewrote it as *"near the alveolar-gas ceiling (643 mmHg)"* — which labels 643 as
the alveolar-gas ceiling. That ceiling is **663 mmHg**; 643 is the measured
plateau sitting ~20 mmHg below it, a gap the paper attributes in §2.4 to Pulse's
modelled alveolar-arterial difference. The literal never moved, so no audit
layer saw it. The defect stood for weeks.

---

## Scope

**2026-07-24 to 2026-07-30**, set by the author: 2026-07-24 is the day the
`scientific-rewrite` skill was created, and 2026-07-30 the last working day of
that stretch. The most recent rewrite in the window is `5675f52` (2026-07-29);
nothing after it touches prose.

**Whether the skill was used cannot be determined mechanically.** Its invocation
is recorded nowhere — not in git, not in the repository. Two commits carry its
signature in their message (`7380408`, *"28/28 information atoms preserved"*;
`5675f52`, *"with no claim, hedge or literal touched"*), but the rest are
indistinguishable. Every prose rewrite in the window was therefore audited,
skill or no skill.

## Detection method

A **pure rewrite** is the dangerous case: prose changed, every numeric literal
identical. For each commit touching `preprint_npj/paper.tex`,
`preprint_npj/supplement.tex` or `preprint/manuscript.md`, the deleted and added
lines were extracted and their literal sets compared. Equal sets, with at least
one substantive paragraph (≥ 12 words) on each side, marks a pure rewrite.

Measured over the window: **48 commits, 60 paragraph-level rewrites** —
27 in `paper.tex`, 28 in `supplement.tex`, 5 in `manuscript.md`.

## Audit grid

Each before/after pair was read twice: once against the original, once against
ground truth. Drift classes looked for: scope widened or narrowed · hedge
dropped or hardened · referent displaced by a sentence split · ellipsis resolved
the wrong way · causal link invented out of a sequence · statistic relabelled
(a *median of paired differences* is not a *difference of medians*) · and a
fluent rewrite of a true claim turning false.

---

## Result: 56 paragraphs audited, **0 semantic drift**

| commit | § | verdict |
|---|---:|---|
| `5675f52` readability pass | 18 | **CLEAN**. All eighteen are sentence splits, parenthesis-to-apposition moves, or em-dash asides promoted to their own sentence. Two are repairs: *"it flags the runs"* → *"the detector flags the runs"* gives an orphan pronoun its antecedent, and *"cannot meet on the same runs"* → *"cannot appear"* removes an idiom. |
| `6ca93f2` caption title bolding | 26 | **CLEAN — markup only.** Stripping `\textbf{}` from both sides leaves byte-identical prose in all 26. |
| `af1d2fa` Berlin-band correction | 5 | **CLEAN.** Not a style rewrite but a factual repair, and it is correct: the Berlin severe band is ≤ 100 mmHg, open-ended below, so it has no centre. Our 96 mmHg sits just inside its ceiling, while 256 and 150 are at the mild and moderate centres. Two monograph loci were still loose at that commit; both were repaired later and now read correctly (`manuscript.md` L230, L347, L905). |
| `f39211c` | 1 | **CLEAN.** Panel references removed from a legend title. |
| `e42f656` bounds taxonomy 3 → 2 | 2 | **CLEAN, and it carries two real corrections.** *"physical or thermodynamic ceiling"* → *"physical or definitional ceiling"*: the SpO2 upper bound is definitional, not thermodynamic. *"a threshold **below** which"* → *"**beyond** which"*: the bounds are (lower, upper) pairs, so "below" was wrong for every upper bound. |
| `d409080` title | 2 | **CLEAN.** *Divergence* leaves the title but *Failure Modes* subsumes it; npj caps titles at 15 words with no punctuation. |
| `ecea6f1` | 1 | **CLEAN.** The gloss added for *allometric* ("quantities that scale with body size") is correct, and *"is mapped onto"* → *"then drives"* matches the verb §4 already uses for the same mechanism. |
| `6e224cd` | 1 | **CLEAN.** Bold removed from a legend title. |

### The one thing worth recording

`5675f52`, §4.6: the rewrite introduces *"It covered **four** items"*, a number
absent from the original. It is exact — four items are listed — and it is a
structural announcement rather than a new fact. Noted because introducing a
number is normally outside a rewrite's remit.

### A false alarm from the audit's own tooling

The bold-only checker first reported 9 paragraphs in `6ca93f2` as having changed
prose. All nine were artefacts: the regex `\\textbf\{[^{}]*\}` cannot strip a
`\textbf{}` whose content holds a nested `\texttt{}`. The prose was identical.
Recorded so the alarm is not raised again.

---

---

# Pass 2 — before 2026-07-24 (added 2026-08-02)

The author asked for the earlier window to be closed too, since `6403787` sits
in it.

## The method above has a blind spot, and `6403787` falls straight into it

`6403787` **is not a pure rewrite**: it also *added* literals (it introduced
"median 93~\%" into the abstract). The literal sets therefore differ, and the
pure-rewrite filter classifies it as "mixed" and never surfaces it. The very
defect that motivated this register would have been missed by the register's own
detector. Recorded plainly, because it bounds what Pass 1 proves.

Volume in the earlier window, for the record: 185 commits, **72 pure-rewrite
paragraphs** (43 paper, 18 supplement, 11 monograph) — plus 152 "mixed" commits
that the filter cannot triage.

## A different instrument for this pass

Diffing history cannot find this class of defect reliably. Reading the **current
text** can. The 643/663 failure has a specific shape: a sentence that *attributes*
a number to a named concept, where the number is right and the noun is wrong.

So every sentence in `paper.tex` and `supplement.tex` that pins a number to a
named quantity was extracted — patterns `<noun> (N unit)`, `<noun> of/at N`,
`N, the <noun>` — and each attribution was checked against the artefact rather
than against the number. 19 fragments in `paper.tex`, 14 in `supplement.tex`.

## 🔴 One real defect found, same shape as 643/663

`supplement.tex` §S3, on the two runs that stay `implausible` under the wider
700 mmHg bound:

> "…stable near **the alveolar ceiling** ($\approx$480~mmHg) for the first 60~s,
> then climbing to a physically impossible plateau above the 760~mmHg sea-level
> barometric pressure…"

Re-derived from the artefacts:

| | S1_F_0118 | S1_F_0119 |
|---|---:|---:|
| FiO2 | 0.7367 | 0.7367 |
| PaCO2 mean | 15.7 mmHg | 14.3 mmHg |
| **own alveolar ceiling** = FiO2·713 − PaCO2/0.8 | **505.6** | **507.4** |
| observed PaO2, mean over t ≤ 60 s | 478.0 | 480.6 |
| observed PaO2, plateau 30–60 s | 479.3 | 481.0 |

**480 is an observed arterial value and is correct.** What is wrong is the noun
it is pinned to: their alveolar ceiling is ~506 mmHg, and they sit ~27 mmHg
below it — the ordinary alveolar-arterial difference, exactly the same physics
that puts the paper's 643 about 20 mmHg under 663. Neither of these runs is at
FiO2 = 1.0 (the reclassification JSON puts both in the 0.6–0.8 bin), so the
663 mmHg figure never applied to them either.

Note the near-coincidence that makes this easy to misread: §S9 fits
`PaO2 ≈ 505·FiO2 − 25` and reports that a naive linear extrapolation "would
predict $\approx$480~mmHg at FiO2 = 1.0". That 480 is a *different* 480,
correctly labelled at its own locus.

**Repaired** to "stable at $\approx$480~mmHg for the first 60~s" — the false
label removed, no number added, the runaway point of the sentence intact.

## Everything else checked clean

The other 32 attribution fragments each name the right quantity: the 600 mmHg
locked bound, the 0.928 median top-3 fraction, the 0.05 CV threshold, 41/44
reruns at 93.2 %, 20/1,280 at 1.6 %, 663/1,280 at 51.8 %, the 3,996 mL female
and 4,803 mL male blood volumes, the 289-anchor ledger target, and the
216.5-months provenance erratum — which the supplement already declares as a
misstatement rather than asserting.

## What neither pass covers

The 152 "mixed" commits before 2026-07-24 were not diffed one by one. The
attribution scan above is what covers that ground instead, and it covers it on
the axis that matters — what the current text asserts — rather than on the axis
of who changed what when. Sentences carrying a number but making no attribution
(531 in total across both documents) were not re-read here; 159 of them were
checked against their artefacts in the step-wise fact-check of 2026-08-01.
