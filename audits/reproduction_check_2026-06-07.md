# Reproduction check — full 1,280-run sweep vs. paper artifacts

**Date:** 2026-06-07
**Reproducer:** Yassir Mamouni (WSL2 / Linux), branch `feat/contribution-ym`
**Original (reference):** the artifacts committed at `HEAD` — these are the exact
files the npj submission (`preprint_npj/paper.tex`, `supplement.tex`) was written
from.
**Rerun wall time:** 23h01m21s (2 Docker workers; the original estimate of ~9.4 h
assumed 3 workers — see `MAX_PARALLEL_LAPTOP`).

## Verdict

**The paper reproduces.** Every conclusion-bearing artifact is **bit-identical**
to the committed original, including all per-run steady-state values. The only
differences anywhere are (a) a benign added `primary_flag` column in the master
parquet and (b) sub-`1e-13` floating-point round-off in three derived H4
statistics — neither changes any number reported in the paper, and the H4
survivor set is identical.

## Method

Read-only extraction of the committed originals (no `checkout`/`stash`/`reset`;
the working-tree reproduction was never touched):

```bash
git show HEAD:data/runs/full_sweep/aggregated.parquet > /tmp/repro_orig/...
git show HEAD:results/<artifact>                      > /tmp/repro_orig/results/...
```

then numerical diff of original vs. working tree, aligned on `case_id` /
`(scenario, sex, output, input)`.

## 1. Flag classification — exact match

Per-run booleans aligned on `case_id`:

| flag | orig | repro | Δ | per-run mismatches /1280 |
|---|---|---|---|---|
| clamped | 0 | 0 | 0 | 0 |
| diverged | 20 | 20 | 0 | 0 |
| implausible | 126 | 126 | 0 | 0 |
| not_steady_state | 530 | 530 | 0 | 0 |
| clean | 663 | 663 | 0 | 0 |

**All 5 flags identical on 1280/1280 runs (100.00%).** Inputs (`in_*`) byte-equal,
confirming the same locked Morris sample drove both sweeps.

Per-cell breakdown (`cell_flag_summary.csv`, byte-identical orig vs repro):

| cell | diverged | implausible | not_steady_state | clean |
|---|---|---|---|---|
| S1_F | 0 | 23 | 118 | 42 |
| S1_M | 4 | 11 | 107 | 49 |
| S2_F | 0 | 0 | 68 | 92 |
| S2_M | 4 | 0 | 69 | 87 |
| S3_F | 0 | 0 | 38 | 122 |
| S3_M | 4 | 0 | 12 | 144 |
| S4_F | 0 | 46 | 74 | 60 |
| S4_M | 8 | 46 | 44 | 67 |

Divergence is **all-male** (S1_M 4 + S2_M 4 + S3_M 4 + S4_M 8 = 20; every female
cell = 0) — the paper's sex-stratification claim reproduces exactly.

## 2. Continuous steady-state values — bit-identical

Max absolute difference over all 1,280 runs, for every channel × statistic
(`*_mean`, `*_std`, `*_cv`, `*_delta_60s`):

> **max |Δ| = 0.0 for every column; 0 rows differ.**

Pulse v4.3.1 is **fully deterministic across hardware** (original laptop → WSL2):
the engine output is reproduced to the bit, well within the preregistered
`1e-6` determinism tolerance (paper §Methods / pilot gate).

## 3. Deterministic analysis artifacts — bit-identical

| artifact | orig vs repro |
|---|---|
| `cell_flag_summary.csv` | identical |
| `reliability_classification.csv` | identical (7 green / 29 yellow / 12 red) |
| `h1_top3_fraction.csv` | identical (H1 pass 48/48, median top-3 frac 0.928) |
| `sobol_promotion.csv` | identical |
| `morris_indices.parquet` (`mu_star`) | identical (bit-equal) |

Because `morris_indices.parquet` is bit-equal, the downstream Morris-derived
claims — 48/48 H1, σ/μ\* linearity counts, bootstrap CIs — reproduce by
construction.

## 4. H4 sex-comparison files — float round-off only (conclusions identical)

Three files showed as modified in `git status`; the differences are
machine-epsilon, not real:

| file | columns that differ | max \|Δ\| |
|---|---|---|
| `wasserstein_male_vs_female.csv` | `wasserstein`, `wasserstein_null_p50`, `wasserstein_null_p95` | 2.8e-14 |
| `spearman_mu_star.csv` | `spearman_p` | 9.7e-17 |
| `bh_fdr_survivors.csv` | same wasserstein cols | 2.8e-14 |

All other columns identical. **BH-FDR survivors (q=0.05) are the same set in both:**

```
S1/PaCO2, S2/PaCO2, S3/PaCO2, S4/SpO2, S4/PaO2   (5 of 24, all gas-exchange)
```

This matches the paper abstract verbatim ("5 of 24 ... all five are gas-exchange
(PaCO2 ×3, SpO2 ×1, PaO2 ×1)"). The round-off arises from summation-order
differences in the Wasserstein null across BLAS builds; it is below any reported
precision and flips no decision.

## 5. Three-way check against the locked paper

| paper.tex claim | original artifact | reproduction |
|---|---|---|
| 0 / 1,280 clamped | 0 | **0** ✓ |
| 20 / 1,280 diverged, all male | 20, all male | **20, all male** ✓ |
| 663 / 1,280 clean (51.8 %) | 663 | **663** ✓ |
| 126 implausible | 126 | **126** ✓ |
| 530 not_steady_state (S1+S4 concentration) | 530 | **530** ✓ |
| H1: 48/48, median 0.928 (range 0.658–0.998) | 48/48, 0.928 | **48/48, 0.928** ✓ |
| H4: 5/24 BH-FDR survivors, all gas-exchange | 5/24 | **5/24, same cells** ✓ |
| Morris μ\* heatmaps | — | **bit-identical** ✓ |

## 6. Figures

`figures/*.png|pdf` show as modified, as expected: matplotlib/PDF embeds
build timestamps and rendering is not byte-deterministic. They were **not**
pixel-compared. Their scientific content is reproduced because every figure
derives from a bit-identical results file (fig01/02/03/06) or from the
H4 files that differ only at `~1e-14` (fig04/05).

## Caveats / scope of this check

- **Morris sample reuse.** `run_full_sweep.py` loads the committed
  `morris_sample.parquet` when present rather than regenerating from `seed=42`,
  so this rerun reuses the locked sample (inputs confirmed byte-equal). It
  validates *sweep → detector → analysis* determinism, **not** sample
  *generation* from seed. To close that gap: delete `morris_sample.parquet`,
  regenerate, and confirm byte-equality against the committed sample.
- The `34 of 126` PaO2>600 sub-count and the F-003 300 s rerun
  (`S021`, supplement §S9) are produced by separate scripts not run here; only
  the parent `implausible=126` count was reproduced.
- Reproduction ran with 2 Docker workers (≈23 h) vs. the 3-worker estimate.

## Reproduce this comparison

```bash
mkdir -p /tmp/repro_orig/results /tmp/repro_orig/data/runs/full_sweep
git show HEAD:data/runs/full_sweep/aggregated.parquet > /tmp/repro_orig/data/runs/full_sweep/aggregated.parquet
for f in cell_flag_summary reliability_classification h1_top3_fraction \
         wasserstein_male_vs_female spearman_mu_star bh_fdr_survivors sobol_promotion; do
  git show HEAD:results/$f.csv > /tmp/repro_orig/results/$f.csv
done
git show HEAD:results/morris_indices.parquet > /tmp/repro_orig/results/morris_indices.parquet
# then diff /tmp/repro_orig vs the working tree (see this file's §1–4)
```
