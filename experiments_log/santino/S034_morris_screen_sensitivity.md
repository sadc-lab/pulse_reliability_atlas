---
id: S034
author: santino
date: 2026-09-12
status: done
tags: [morris, screening, clean-pairs, rank-stability, reviewer-response, post-hoc, sensitivity]
linked_code:
  - scripts/s034_morris_screen_sensitivity.py
  - src/analysis_morris.py
  - preprint_npj/supplement.tex
  - preprint_npj/paper.tex
linked_data:
  - results/s034/mu_star_by_screen.csv
  - results/s034/rank_comparison.csv
  - results/s034/s034_summary.json
  - results/morris_indices.parquet
related: [S023, S033]
---

# S034 — Do the Morris rankings depend on the clean-pair screen?

---

## Why this session happened

The published Morris indices use only elementary-effect pairs whose **both**
endpoints are four-flag clean (`src/analysis_morris.py:139`, preregistration
§A.2). That keeps 663 of 1,280 runs. The most serious methodological objection
available against this atlas is therefore: *are the rankings a property of the
engine, or of the screen?*

It is answerable on data already recorded, and nothing else in the repository
answers it. The SHAP cross-check of S023 cannot: that surrogate is trained on
the same 663 runs. The paper already flags the problem qualitatively —
`paper.tex` §2.2 says the map "is therefore bounded by run survival — the
regime that destabilises delivered volume most is the one in which that
instability is least measurable" — but nothing quantified the bound.

Pre-specified on 2026-08-25, executed 2026-09-12. Three criteria per
(cell, output): top-1 preserved; top-three **set** preserved; top-three
**order** preserved. **The raw counts are the result** — no "acceptable
stability" threshold was introduced afterwards.

## Method

A **parallel** calculation, never a replacement. The clean screen is
preregistered; `results/morris_indices.parquet` stays the reference, and
`scripts/s034_morris_screen_sensitivity.py` writes only under `results/s034/`.

The audited derivation is reused verbatim: `derive_trajectory_pairs` and
`compute_ee_for_cell` from `src/analysis_morris.py`. Only the screen changes.
`compute_ee_for_cell` emits `both_clean` but not the raw endpoint flags, so the
second screen is built by re-joining `diverged` and `implausible` from
`aggregated.parquet` onto the `j_lo_case` / `j_hi_case` columns it does emit.
No bootstrap: the three criteria need only μ\*, which is deterministic.

Everything runs from `data/runs/full_sweep/aggregated.parquet`, which is
git-tracked — so unlike `results/s033/`, **this artefact is regenerable on a
clean clone** and its guard is checkable in CI.

## Calibration — five published quantities reproduced exactly

Recomputing under the **locked** screen reproduces:

| quantity | published | re-derived |
|---|---|---|
| μ\* rows | 318 | 318, max abs delta **0** |
| H1 combinations passing | 48 / 48 | 48 / 48 |
| H1 top-3 fraction range | 0.658–0.998 | 0.6580637848 – 0.9984529095 |
| H1 median | 0.928 | 0.9276880248 |
| single-pair triples | "Twelve cells are outlined" | 12: `vt` in S1\_F ×6, `fio2` in S4\_M ×6 |
| of those, in a top three | 9, "five … rank-1" | 9, of which 5 are rank-1 |

The script aborts if the first two fail. The comparison is therefore between
two screens, not between two pipelines.

## Result

The relaxed screen (neither `diverged` nor `implausible`) keeps **1,134** runs
and **969** of the 1,120 pairs, against **663** and **454**. Gain: **3,090**
elementary-effect observations, of which **1,152** in S1.

**What does not change.**

- **H1 holds 48/48 under both screens.** 0.658–0.998 (median 0.928) →
  0.695–0.994 (median 0.901). The **minimum rises**. The concentration on which
  the paper's headline rests is not an artefact of run survival.
- **Rank-1 preserved 30/30** on the combinations whose candidate set is
  unchanged.

**What changes.**

- FiO₂ becomes estimable in S1\_M, S1\_F and S4\_F → 318 → 336 triples, so
  **18 of 48** combinations gain a seventh candidate and are no longer
  like-for-like.
- On the 30 like-for-like: top-three **set** 19/30, **order** 15/30.
- Over all 48, candidate changes counted as changes: **41, 26, 21**.

**These are reorderings, not ties.** Median gap between the 3rd and 4th μ\* is
**39 %** of the third under the locked screen; only **1 of 30** combinations has
a gap below 10 %. I had assumed the opposite before measuring; the measurement
refuted it.

**Seed comparator** (`results/phase4b_top3_comparison_seed44.csv`, read rather
than recalled): replaying S2\_M under an independent Morris seed preserves
**6/6, 4/6, 3/6**; the screen change gives **6/6, 2/6, 2/6** on the same six
outputs. One cell, six outputs — a landmark, not an equivalence. It places the
screen effect alongside a perturbation the design already carries.

**Reading.** Rank 1 is resolved by this design; the ordering below it is not,
under either perturbation. That is why Figure 3 is a map of where influence
concentrates, not a stable ordering.

## The framing is mandatory, and it is in the script and the supplement

The 471 runs the relaxed screen admits are exactly those whose **only** flag is
`not_steady_state` — runs whose steady-state mean is not a valid summary of the
run. **This trades a selection bias for a measurement error; it does not reduce
bias, and must never be reported as a less-biased estimator.** The extra data is
most abundant where it is least trustworthy: 1,152 of the 3,090 gained
observations are in S1, the scenario whose delivered-volume oscillation is worst.

## Published, on the maintainer's decision (2026-09-12)

- New subsection `sec:s13-screen` in Supplement §S13. A **subsection**, not a
  section: inserting a `\section` would renumber S14–S17, and
  `preprint/manuscript.md` cites "Supplementary §S13" as literal text in two
  places, so numbering is load-bearing outside LaTeX's label resolution.
  ⚠️ Alternative rejected: retitling §S13 from "SHAP cross-check…" to
  "Robustness of the Morris top-three input sets", which would have fitted
  better but changes a published heading that the §S17 index table also carries.
- One sentence appended to `paper.tex` §2.2, on the sentence that already
  pointed at §S13 for the SHAP cross-check.
- The Morris heatmap caption now states that the white cells withhold the
  **dominant** input for gas exchange: FiO₂ is rank-1 for PaO₂ and SpO₂ in all
  three affected cells under the relaxed screen. Verified as exactly 6 of the 7
  rank-1 changes; the 7th is S1\_M PaCO₂, `rr` → `vt`.

## Guard

`check_s034_screen_sensitivity()` in `scripts/audit_claims.py`, **23 checks**,
in three layers: transcription against both documents; the artefact's own
arithmetic (the 30 + 18 = 48 split, the 318 → 336 growth being exactly 3 cells
× 6 outputs, observations = distinct pairs × 6 outputs, and no combination
losing pairs); and a cross-instrument layer that reads the seed comparator and
the published indices from artefacts S034 did not write.

Calibrated by reinjection, MD5 checked before, during and after:

1. supplement "preserved in 19" → "20" turns that row into a FAIL;
2. setting the producer's recorded calibration delta from `0.0` to `1e-09` in
   `s034_summary.json` — a stale artefact — fails the calibration row.

## Two corrections to the pre-specification itself

The pre-spec was written on 2026-08-25 and carried two factual errors, both
found by measurement before execution:

- **"The denominator is NOT 48"** — it is 48. All 48 (cell × output) rankings
  are estimable under the locked screen; the paper says so twice ("H1 is
  supported in 48 of 48"). What is true, and what the pre-spec was reaching
  for, is that **18 of the 48 draw their top three from six candidates rather
  than seven**, which is why both denominators are reported.
- **"No Vt combination is estimable in S1"** — ⚠️ I first recorded this as
  false, because `vt` has all 48 μ\* rows. **I was wrong and the pre-spec was
  right**: in `paper.tex` §2.2 "estimable" means *σ estimable* — the σ/μ\*
  trigger needs at least two pairs — as the same sentence confirms three
  clauses later ("9 rest on a single pair … no bootstrap interval is
  estimable"). I read the wrong unit while claiming to apply the rule about
  defining units. Recorded because the reflex failed exactly where it was being
  invoked.

## Limits

- Post hoc. The preregistered screen, the published indices and every
  published count are unchanged.
- The seed comparator is one cell and six outputs. It bounds nothing; it gives
  scale.
- The relaxed screen is not the only alternative one could choose. Nothing here
  claims it is the right screen — only that the ranking's rank-1 level survives
  it and the finer ordering does not.
