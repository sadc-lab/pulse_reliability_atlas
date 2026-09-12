# Register — one published estimand is rounded up by 0.01 (Supplement Table S8)

**Status: OPEN.** Recorded 2026-09-12. Nothing in `supplement.tex` has been
modified. A published table value is a scientific claim, so the correction
waits on the maintainer's decision.

---

## The mismatch

`preprint_npj/supplement.tex` L705, Table `tab:s8-estimands`:

```
Ratio of group medians & 21.42 & 22.67 \\
```

Re-derived from `data/runs/` by `scripts/s033_cycle_resolved_vtcv.py`:

| quantity | value |
|---|---|
| median cycle-resolved Vt CV, default arm, 63 configurations | 0.337325 |
| median cycle-resolved Vt CV, locked arm, same 63 | 0.0148832 |
| ratio | **22.6648553684** |
| correct two-decimal display | **22.66** |
| published | 22.67 |

The 5-second column of the same row, 21.42, is correct
(21.419527311 → 21.42), as are the other six values in the table.

## Why it happened — most likely double rounding

22.6648553684 sits **0.00015 below** the 22.665 boundary that separates 22.66
from 22.67. Rounding once to three decimals gives 22.665, and rounding *that*
to two gives 22.67. The original computation ran through `awk` pipelines that
were not kept (see `experiments_log/santino/S033_cycle_resolved_vtcv.md`), so
the intermediate precision cannot be inspected; this is the mechanism the
arithmetic is consistent with, not an observed one.

## What was ruled out

* **A different subset.** The supplement declares "the same 63 configurations
  with a non-zero post-lockout cycle-level CV". On all 64, the ratio is
  0.33856 / 0.0148462 = **22.80**, which is not 22.67 either. No subset of the
  pairs produces 22.67.
* **A different estimand.** The other three summaries in the table, and the
  5-second column of this row, all reproduce to the published digit, so the
  estimand definitions are not in question.
* **A wider drift.** 36 further checks on this subsection pass, including the
  eight-cell table, the 2×2 agreement, the counterfactual and the relative-gap
  range. This is a single isolated digit.

## Population of the defect — measured, not assumed

One character, in one file:

| artefact | occurrences of `22.67` | occurrences of `22.66` |
|---|---|---|
| `preprint_npj/paper.tex` | 0 | 0 |
| `preprint_npj/supplement.tex` | **1** | 0 |
| `preprint/manuscript.md` | 0 | 0 |

The whole estimand table lives only in the supplement, so the correction has
no cascade. Verified 2026-09-12 on all three public artefacts, because
correcting the paper alone has been mistaken for correcting the work before.

## Does any claim depend on it?

No. The value supports the supplement's statement that "the relative gap
ranges from 0.6 % to 8.6 %, and its direction is not consistent". With 22.66
instead of 22.67:

* the relative gap for this row is 5.8140 %, which the published range already
  covers and which is computed from the unrounded values, not the display;
* the direction is unchanged — the cycle-resolved ratio still exceeds the
  5-second one, so the row still says the 5-second statistic understates the
  effect;
* the two-against-two split of directions is unchanged.

The defect is confined to the displayed digit.

## Decision required

Replace `22.67` with `22.66` at `preprint_npj/supplement.tex` L705, rebuild the
PDF and DOCX twins, or leave it. Four supervisors received the 2026-09-05 build
(`preprint_npj/dispatch_log.md`), so a change alters a value they hold; the
change is one digit in a supplementary table, in a row whose two other
published figures are unaffected.

## What holds the line meanwhile

`check_s033_cycle_resolved()` in `scripts/audit_claims.py` reports this row as
**OPEN** rather than silently tolerating it, and re-verifies its own premise on
every run: if `supplement.tex` stops carrying `21.42 & 22.67`, or starts
carrying `22.66`, or the artefact stops yielding 22.6648553684, the block
becomes a **FAIL** demanding its own deletion. Proven by reinjection on
2026-09-12: correcting the supplement to `22.66` turns the row into
`**stale OPEN exception**: the disputed literal is gone`.
