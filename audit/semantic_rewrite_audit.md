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

## What this register does not cover

Rewrites **before 2026-07-24**, which is where `6403787` — the defect that
prompted this audit — actually sits. The author scoped this pass to the skill's
lifetime. The earlier rewrites remain unaudited on this axis, and that is a
known, deliberate gap rather than a clean bill of health.
