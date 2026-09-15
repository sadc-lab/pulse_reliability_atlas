---
id: S031
author: santino
date: 2026-07-29
status: done
tags: [statistics, sobol, bootstrap, preregistration-fidelity, non-linearity, survivorship-bias, manuscript-correction, ratio-aware-bootstrap, retraction]
linked_code:
  - preprint_npj/paper.tex
  - preprint_npj/supplement.tex
  - preprint/manuscript.md
  - preprint_npj/paper_to_monograph_map.md
  - src/analysis_morris.py
  - preregistration.md
---

# S031 — Sobol trigger reframe, systemic non-linearity, and the survivorship censoring on delivered Vt

---

## Why this session happened

A read-only audit of Methods §4.5 (*Statistical analyses*) was requested. The
audit was meant to confirm that the six statistical implementations were sound.
They are — `tests/test_analysis.py` still passes, BH re-derived by hand returns
the same 5 survivors, H1 re-derives from the raw artefacts to 1e-16. What the
audit found instead was a **framing** defect that had propagated from the
monograph into the paper and the supplement, plus two factually false statements
that had been sitting in the monograph since Phase G (2026-05-31).

---

## Finding 1 — the preregistered Sobol trigger had been silently narrowed

`preregistration.md` §Sampling method states the rule on the **top-three**
μ\*-ranked inputs of each cell × output. The paper and Supplement §S3-sobol both
attributed to the preregistration a **narrower** rule, on the dominant input
alone, and reported its consequences as if they were the preregistered result.

The gap is not cosmetic:

| Framing | Cells firing at the point estimate |
|---|---|
| Dominant input (what was published) | 8 / 48 |
| Top-three (what was preregistered)  | **43 / 48** |

The monograph §3.3.1 was honest about this in two steps — it stated the rule,
then said "applying this rule to the dominant input" — but the two sentences
were merged at porting time, and the restriction became invisible.

**Decision (with the maintainer):** report the preregistered rule as written.

## Finding 2 — the closure argument did not survive the correct rule

The published claim was "zero of the 48 cells satisfy this trigger, so the
bolt-on is closed by evidential redundancy". Under the top-three rule this is
false under every bootstrap draw tested.

The real closure argument was available from the start and does not depend on
any bootstrap formula: **the preregistration capped the bolt-on at 1,500 extra
runs**, and the preregistered cost model (`64 × (2k + 2)`, one Sobol sample per
cell because each scenario–sex cell is a different model) puts 43 cells at
**11,008 runs** — sevenfold over. It also exceeded the cap under the narrower
dominant-input reading (8 cells, 2,048 runs).

**Decision:** replace "closed by evidential redundancy" with the budget ceiling
everywhere. It is factual, preregistered, and unattackable.

## Finding 3 — two false statements in the monograph

Monograph §3.3.1 stated, of the fully ratio-aware bootstrap:

> "yields a slightly different decomposition (30 / 48 CI-robustly linear)"
> "zero cells are CI-robustly non-linear **under either formula**"

Both are wrong. Swept across **32 convention combinations** (sequential vs
re-seeded RNG × 1,000/4,000 resamples × α 0.05/0.10 × strict/non-strict
threshold × with/without the two noise-dominated cells), the count is **31**
linear in every single combination, never 30; and the non-linear count is
between 1 and 3, never 0.

Neither statement was in the paper. Both are now explicitly retracted in the
monograph rather than silently edited.

## Finding 4 — the CI bucketing was never preregistered

The preregistration conditions the trigger on the **point ratio** and attaches
no uncertainty qualifier: no "bootstrap", "confidence", "interval", "resample",
"percentile" or "robust" anywhere in that section (verified on a correctly
delimited slice — see *Verification defects* below). The whole CI bucketing is
therefore a **post-hoc sensitivity analysis** and is now labelled as such.
Presenting it as the preregistered decision would have repeated the very error
being corrected.

## Finding 5 (new result) — non-linearity is systemic, not anecdotal

Under the preregistered top-three rule and the ratio-aware bootstrap, **23 of
the 144 top-three inputs** hold a lower CI bound at or above 0.6 in all five
independent seeds, spanning **17 of the 48 cells**.

| Inputs | Outputs | Scenarios | Sex |
|---|---|---|---|
| PEEP 8 · RR 5 · SBP 3 · Vt 3 · FiO₂ 2 · HR 1 · DBP 1 | Vt 8 · PaO₂ 7 · HR 4 · SpO₂ 3 · PaCO₂ 1 | S3 12 · S2 5 · S4 4 · S1 2 | F 12 · M 11 |

All seven swept inputs, all four scenarios, both reference bodies at near
parity. PEEP is the most frequent single input (8/23, 35 %) without being
exclusive.

This honours a promise the Introduction already made — "where that influence
turns non-linear" — and which the paper did not previously deliver.

## Finding 6 (mechanism) — informative censoring on delivered Vt

Delivered Vt is the most affected **output** (8/23), and it is also the channel
whose oscillation dominates the `not_steady_state` flags. The two cannot meet on
the same runs, and the gradient is exact:

| | Vt CV > 0.05 | median clean trajectories | Vt combinations in the core |
|---|---|---|---|
| S1 | 139 / 320 | 3 | **0** |
| S2 | 89 / 320 | 8 | 3 |
| S3 | **36 / 320** | **16** | 3 |
| S4 | 39 / 320 | 6 | 2 |

The elementary-effect estimator uses only unflagged runs, so a regime unstable
enough to flag its own runs cannot supply the pairs needed to characterise it.
**The instability destroys the sample required to measure it.** Non-linearity is
easiest to establish where the engine is most stable — the opposite of where it
matters most.

An earlier framing ("the sensitivity analysis converges on the same mechanical
fragility as the VC-AC dyssynchrony") was **proposed and then withdrawn**: the
two phenomena are geographically disjoint, and claiming convergence would have
been false. What survives is convergence *of channel*, not of region.

---

## Decisions taken, in order

| # | Decision | Rationale |
|---|---|---|
| 1 | Report the top-three rule as preregistered | fidelity to the dated record |
| 2 | Close the bolt-on on the budget ceiling, not on redundancy | factual and preregistered |
| 3 | Adopt the **ratio-aware** bootstrap | bootstrapping the quantity of interest is standard; the σ_hi/μ̂\* variant ignores the σ–μ\* covariance |
| 4 | **Roll back** the PEEP/S3 finding injected earlier the same day | it was an artefact of the σ_hi/μ̂\* formula; keeping it to save a paragraph would have been narrative-hacking |
| 5 | Report `p = 0` as `p < 0.001`, **without touching the code** | p_emp = 0 is the observed fraction, not an error; (b+1)/(m+1) is a convention. Corrected reporting contradicts no artefact and preserves Y.M.'s cross-reproduction |
| 6 | Harmonise the post-hoc bootstrap to **1,000** resamples | the stable set is identical at 1,000 / 2,000 / 4,000 (22 at 500), so one number suffices and the canonical artefact stays untouched |
| 7 | **Drop the union figure** (25/26/27 depending on the knob) from paper and supplement | it documents sampling noise, not physiology, and invites scrutiny of an artefact |
| 8 | Name H2 and H3 in the Results and state their verdicts | a refuted preregistered hypothesis is a result, not a silence |
| 9 | Report the H4 Wasserstein result in the paper | the method was described in Methods and the result appeared nowhere |
| 10 | Rename the "within-sex" null to pooled/re-split relabelling | the label misdescribed a correctly implemented permutation test |

## Verification defects found in my own audit scripts

Recorded because they were the dominant error mode, not the results.

| Defect | Mechanism | Consequence |
|---|---|---|
| `pre.index("Pilot gate")` | marker occurs 3×; the first precedes the section | empty slice → six absence tests passed **vacuously** |
| `cand[0]` | filtered list began with `Vt_std`, not `Vt_cv` | two plausible but meaningless numbers (never published) |
| `GroupBy.first()` | returns first non-null **per column**, not the first row | chimeric table on the 5 no-CI cells (verdict unaffected) |
| two-axis comparison | resample count **and** RNG mode varied together | a false claim about 1,000 vs 2,000; corrected |

**Root cause:** an absence test fails silently in the reassuring direction. Five
rules adopted: (a) a positive control beside every absence test; (b) assertions
on intermediates; (c) no implicit selection — name the column, check uniqueness;
(d) measure before narrating; (e) re-derive from source files, never from a
previous message.

## Artefacts

- Text injected into `preprint_npj/paper.tex`, `preprint_npj/supplement.tex`,
  `preprint/manuscript.md`.
- `preprint_npj/paper_to_monograph_map.md`: six occurrence counts bumped with
  dated notes.
- Audit after every step: **277/277 anchors · 97/97 sync · 26/26 monograph**.

## Closed in the same session

1. **Terminology purged.** `within-sex` eliminated on all three remaining
   surfaces (monograph 18 → 0, README 3 → 0, captions 2 → 0) in favour of
   *permutation null* / *pooled and re-split relabellings*, matching the paper.
   The two `p_emp = 0.000` table cells now read `$<$ 0.001`, which is honest for
   a permutation p-value whose resolution floor is 1/N.
2. **Generator versioned.** `scripts/sobol_ci_buckets.py` implements the
   ratio-aware bootstrap and writes `results/sobol_ci_buckets.{csv,json}`. Its
   three inputs are git-tracked, so it runs on a fresh clone. It reproduces all
   thirteen figures the manuscript quotes, and keeps the historical
   `sigma_hi / mu_hat*` formula as `legacy_*` columns so the pre-S031 buckets
   stay checkable. Closes the defect that the 31/12/5 buckets had been published
   since Phase G with **no generator in the repository**.
3. **Ledger anchored.** Twelve new anchors (`T2.sobol.*`) pin 72, 43, 11,008,
   1,500, 23, 17, 31, 1, 1,000 and the per-input/per-output breakdown against
   the regenerated artefact rather than against typed numbers. Ledger went from
   277 to **289 anchors, all passing**.
4. **Rebuilt and render-verified.** paper / supplement / monograph PDFs and
   DOCX rebuilt. The four residual typography warnings were shown to be
   **identical to a recompilation of HEAD, to five decimal places**, so no
   layout regression was introduced.

## Still open

Nothing from this session. The remaining work is the publication logistics
tracked in `TODO_publication_roadmap.md`.

## Correction note — 2026-09-15 (decision 6, "22 at 500")

Decision 6 records the stable set as identical at 1,000 / 2,000 / 4,000
resamples and "22 at 500". On 2026-09-15 the versioned generator
(`scripts/sobol_ci_buckets.py`, `d639747`) was re-run in memory with
`N_BOOTSTRAP` set to 500, 1,000, 2,000 and 4,000. It returned the same
23-entry set at all four, and the 1,000 run reproduced the committed
`results/sobol_ci_buckets.csv` exactly. The "22 at 500" does not reproduce
with the published generator, and how it was obtained is not recorded here: the
32-convention sweep of Finding 3 concerns a different count. The entry above is
kept as written. Supplement S3-sobol and the script comment now state the
re-measured result, on the author's decision (`audit/number_inventory.md` §6,
GL-S2).
