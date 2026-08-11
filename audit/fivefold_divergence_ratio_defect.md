# Defect: the "~5× / fivefold" male-vs-female divergence ratio

**Opened** 2026-08-11. **Status: MISMATCH recorded. Nothing modified.**
Per the autonomy pact, a mismatch is registered and brought back for a joint
decision; no manuscript file was touched.

---

## 1. The claim, at two loci

| Locus | Text |
|---|---|
| `preprint_npj/supplement.tex:523` | the input-driven regime "produces an **approximately fivefold higher** divergence rate on the male body than on the female" |
| `preprint/manuscript.md:2205` | "**~ 5×** higher than female" (bullet: **Input-driven regime** (S006)) |

Both sentences scope the number to the **input-driven regime**, i.e. the S006
Morris sweep reported as the main-manuscript headline.

## 2. What the data say

Rebuilt from `results/cell_flag_summary.csv` (column `n_diverged`):

| scenario | male | female |
|---|---:|---:|
| S1 | 4 | 0 |
| S2 | 4 | 0 |
| S3 | 4 | 0 |
| S4 | 8 | 0 |
| **total** | **20** | **0** |

Corroborated by `experiments_log/santino/S006_full_morris_sweep.md:168`
("Total diverged: 20 / 1,280 (1.6 %), all male") and by `paper.tex:315`, which
already states the fact correctly: "*all 20 fell on the male reference body* …
with zero divergences across the 640 runs on the female reference body".

**A ratio against a zero denominator is undefined, not "approximately five".**
The female count is zero in every cell of this regime, so no sub-region of it
can yield 5×.

## 3. Provenance — traced, and there is none

- **Introduced** in `e736d0d` (S009, Tier-2), directly into
  `preprint/manuscript.md`, **with no derivation shown**, in a bullet describing
  the *S006* regime while the commit itself delivered the *S009* continuous
  sweep.
- The **neighbouring number in the same bullet was later audited and corrected**
  (blood-volume difference 20 % → ~17 %, with an explicit formula added). The
  "~5×" beside it was never revisited.
- **Propagated** to `supplement.tex` in `df821f3` (S028 Phase 9.B), under a
  commit message stating "All Phase 9.B claims use existing ledger entries; no
  new constants extracted" — i.e. copied from the monograph, not re-derived.

Searched: `git log -S "fivefold"`, `-S "5×"`, `-G "higher than female"` across
the repository. No derivation, no source artefact, no ledger entry.

## 4. Why every layer missed it

- **Unanchored.** `grep -rc "fivefold" scripts/*.py` → 0 in every script
  (positive control: 1 hit in `supplement.tex`). The 382-anchor claims audit
  never evaluated it.
- **The fact-check register marked it ✅** at
  `audit/factcheck_paper_supplement_vs_monograph.md:336` — but that register's
  contract is *paper/supplement ↔ monograph agreement*, not *number ↔ data*.
  The two documents agree with each other, both carrying the same unverifiable
  value. See `feedback_read_the_artifact_contract`.

## 5. Reviewer exposure

The main paper states "all 20 fell on the male reference body … zero
divergences" while the supplement states "approximately fivefold higher …
than on the female". These are incompatible descriptions of the same regime,
in the same submission package.

## 6. Proposed replacements — NOT APPLIED, awaiting decision

`supplement.tex:523`, replacing only the trailing clause and keeping the regime
subject intact:

> … and produces divergence **exclusively on the male reference body: 20 events
> across the four male cells against zero across the 640 runs on the female
> body.**

`manuscript.md:2205`:

> * **Input-driven regime** ([S006](#s006)): male reference surrogate at low HR
>   + low SBP + high RR + FiO2 = 1.0. **20 divergence events on the male body,
>   0 on the female (640 runs).**

Rationale for not writing "20 / 0": a slashed pair reads as a rate and
re-introduces the undefined comparison the defect consists of.

**The regime scope must be preserved in both.** In the *severity-driven* regime
(§S5 continuous sweep) female divergences do occur — F = 19, M = 14 — so an
unscoped "none occurred on the female body" would contradict the adjacent
section.

## 7. Follow-up if the replacement is accepted

Add a ledger anchor binding the male and female divergence counts to
`results/cell_flag_summary.csv`, so the property is re-measured rather than
re-verified once. See `feedback_verification_is_not_an_invariant`.
