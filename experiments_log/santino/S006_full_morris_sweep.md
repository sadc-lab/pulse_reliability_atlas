---
id: S006
author: santino
date: 2026-04-26
status: done
tags: [sweep, morris, full-1280-runs, sex-comparison, h1, h2, h3, h4, atlas-finished]
linked_code:
  - scripts/run_full_sweep.py
  - scripts/analyze_sweep.py
  - scripts/make_figures.py
  - src/analysis_morris.py
  - src/analysis_compare.py
linked_data:
  - data/runs/full_sweep/aggregated.parquet
  - data/runs/full_sweep/morris_sample.parquet
  - data/runs/full_sweep/<cell>/aggregated.parquet
  - results/morris_indices.parquet
  - results/cell_flag_summary.csv
  - results/h1_top3_fraction.csv
  - results/wasserstein_male_vs_female.csv
  - results/spearman_mu_star.csv
  - results/reliability_classification.csv
  - results/sobol_promotion.csv
  - results/clamp_grid.parquet
  - results/diverged_grid.parquet
supersedes: ""
related: [S004, S005]
---

# S006 — Full 1,280-run Morris sweep + post-sweep analysis

## Hypothesis

The four preregistered hypotheses (H1 – H4) can be evaluated cleanly on
the full sweep without any post-hoc modification of locked thresholds,
inputs, scenarios, or analysis plan.

## Motivation (why)

This is the data-collection event of the methods paper. Five
preregistered pilot gates were cleared in S005; three Tier-1 risks
(CSV channel coverage, FiO2 wrapper cap, DBP/SBP ratio enforcement)
were dissolved in S004. The full sweep produces the dataset that
populates Table 1, all six figures, and every quoted number in the
preprint manuscript.

## Method (how)

Single-script orchestration via `scripts/run_full_sweep.py`, which:

1. Reads the canonical Morris sample at
   `data/runs/full_sweep/morris_sample.parquet` (regenerated if absent
   from `sample_morris(trajectories=20, levels=4, seed=42)` ⇒ 160 unique
   input points). The same 160 points drive every cell, so EE rankings
   are directly comparable across cells.
2. For each (scenario, sex) cell, builds 160 Pulse configs through
   `src/scenario.build_config` — with the locked DBP-clip rule applied
   at submission time and `(dbp_requested, dbp_applied)` persisted.
3. Submits 2 (post-amendment) parallel Docker containers running
   `pulse-atlas-engine`. Each run takes 45 – 115 s; the cell takes
   45 – 100 min depending on scenario.
4. Aggregates per-cell to `<cell>/aggregated.parquet` via
   `src/aggregator.aggregate_under` (which calls `src/detector.classify`
   on every CSV + log).
5. Concatenates per-cell aggregates into the master
   `data/runs/full_sweep/aggregated.parquet`.

Resume protocol: `scripts/run_full_sweep.py --resume` skips runs whose
`run_meta.json` records `exit_code == 0`. Used once mid-sweep when the
parallelism cap was lowered from 3 → 2 to control laptop thermal load
on user request — no data lost.

Post-sweep analysis pipeline:

* `scripts/analyze_sweep.py` → 9 artifacts in `results/`.
* `scripts/make_figures.py` → 6 figures (PNG + PDF) in `figures/`.

Sweep run: 2026-04-25 18:04 → 2026-04-26 12:26 (≈ 18 h calendar; ≈ 7 h
compute, the rest a sweep restart at lower parallelism). Total Pulse-
container CPU time ≈ 31 h aggregated.

## What we tried (including dead ends)

### Sweep-level

* **First sweep at 3 parallel workers.** Started 2026-04-25 18:04. Hit
  S2_F mid-cell where the orchestrator silently died (no stack trace in
  the log). Pulse containers continued to completion; orchestrator did
  not relaunch new ones. Recovered via `--resume`. Likely cause: Windows
  Git Bash + nohup + Docker desktop behaviour (cause not pinpointed; not
  a code defect because resume worked cleanly).
* **Mid-sweep parallelism reduction.** User requested lowering CPU
  pressure on the laptop. Killed orchestrator (PID 4396), edited
  `src/runner.py:MAX_PARALLEL_LAPTOP 3 → 2`, relaunched with `--resume`.
  Lowered throughput from ~13 runs / min → ~9 runs / min. Sweep finished
  cleanly.
* **Output buffering.** First launch used `nohup uv run python ... > log
  &`. Python's stdout buffered when redirected to a file (no terminal),
  so the log appeared frozen for hours despite real progress visible in
  per-run `run_meta.json` writes. Second launch added
  `PYTHONUNBUFFERED=1` and the log streamed in real-time.

### Verification (run before any results were quoted in the preprint)

We ran 8 sanity checks against the analysis artifacts to catch
hallucinations / off-by-one / unit errors. All 8 passed:

1. **CSV → Parquet integrity.** Picked 3 random clean runs, recomputed
   `HR_mean` from the raw CSV's [60, 120] s window by hand, compared to
   the Parquet's `HR_mean` column. All three matched exactly (diff =
   0.0e+00).
2. **F-003 PaO2 > 600.** Of 126 implausibly-flagged runs across the full
   sweep, 34 have `PaO2_mean > 600`. **91 % of those are at FiO2 ≥ 0.95**.
   Spot-checked 3 raw CSVs (S1_M_0131, S1_M_0025, S1_F_0015): two have
   PaO2 above 600 across the entire window; one (S1_M_0025) had min PaO2
   = 592, mean 608, indicating drift across the bound during the window
   (mean correctly exceeds 600).
3. **F-004 Vt CV > 5 %.** Spot-checked 3 not_steady_state runs flagged
   on Vt CV. All three agreed with the Parquet to 0.0e+00.
4. **Morris EE math.** Took trajectory 0, points 0 → 1 of the canonical
   sample (which flips PEEP from 0 to 13.33 at the OAT step,
   normalized delta = 0.667). Hand-computed
   `EE_HR = (HR_mean[0001] − HR_mean[0000]) / 0.667 = 0.334`. Module
   returned 0.334 — match.
5. **Bootstrap CI bracket.** 0 / 318 Morris-index rows have a CI that
   does not bracket the point estimate. CIs widen as expected for inputs
   with few clean EE pairs.
6. **Wasserstein synthetic.** N(0, 1) vs N(5, 1) → distance 5.06
   (expected ~ 5.0). N(0, 1) vs N(0, 1) → 0.06 (expected ~ 0). SciPy
   implementation behaves correctly.
7. **Reliability traffic-light thresholds.** Spot-checked 5 random
   classifications against the formula:
   `red iff (n_diverged + n_implausible)/n_total > 0.3 OR pct_off >
   0.3`; `yellow iff pct_off > 0.1 OR (n_diverged + n_implausible) > 0`;
   `green` otherwise. All five agreed.
8. **H1 calculation.** S1_M HR by hand: top-3 inputs = (hr, vt, dbp)
   with summed μ\* / total μ\* = 0.9467. Parquet reports 0.9467. Match.

### Limitations surfaced during verification

* **FiO2 has no clean elementary-effect pairs in 18 / 48 cell × output
  combinations** (all six outputs in S1_M, S1_F, S4_F). At FiO2 = 1.0,
  SpO2 saturates and PaO2 either implausibly overshoots (S1) or sits at
  the lower physiological bound (S4_F), flagging the trajectory step.
  Result: μ\*(FiO2) is unavailable for those cells; H1 is computed on
  6 inputs there instead of 7, and Spearman M-vs-F is non-computable
  in S1 / S4. This is a real limitation of Morris elementary effects on
  systems with output-dependent flagging — and the atlas reports it
  honestly rather than imputing.

## Results

### Cell flag summary (Table 1 in manuscript)

| Cell  | n_total | clamped | diverged | implausible | not_steady_state | clean |
|-------|---------|---------|----------|-------------|------------------|-------|
| S1_M  | 160     | 0       | 4        | 11          | 107              | 49    |
| S1_F  | 160     | 0       | 0        | 23          | 118              | 42    |
| S2_M  | 160     | 0       | 4        | 0           | 69               | 87    |
| S2_F  | 160     | 0       | 0        | 0           | 68               | 92    |
| S3_M  | 160     | 0       | 4        | 0           | 12               | 144   |
| S3_F  | 160     | 0       | 0        | 0           | 38               | 122   |
| S4_M  | 160     | 0       | 8        | 46          | 44               | 67    |
| S4_F  | 160     | 0       | 0        | 46          | 74               | 60    |

* **Total clean: 663 / 1,280 (51.8 %)**
* **Total clamped: 0 / 1,280 (0.0 %)**
* **Total diverged: 20 / 1,280 (1.6 %), all male**

### Hypothesis evaluations (manuscript headline)

* **H1 — skewed sensitivity:** **PASS, 48 / 48** cell × output
  combinations. Median top-3 μ\* fraction = 0.928, range 0.658 – 0.998.
* **H2 — silent clamping ≥ 5 %:** **NOT supported**, 0 / 1,280 = 0 %.
  Pulse rejects out-of-envelope inputs loudly with `[ERROR]` log lines
  + exit code 1 (verified in the S005 clamp probes), not silently. The
  upstream verbal description of "BP clamping silently rejected at
  setup" is revised: rejection is loud and observable.
* **H3 — divergence outside ARDS 0.91 – 0.945:** **PASS** (1.6 % overall
  rate), with the additional unanticipated finding that **all 20 divergent
  runs are in male cells**.
* **H4 — sex-specific reliability:** **PASS.** Wasserstein distances
  M-vs-F are non-zero and substantial for Vt (13.8 – 36.3 mL) and PaO2
  (4.6 – 16.1 mmHg) across all four scenarios. Spearman ρ on Morris μ\*
  rankings is 0.75 – 1.00 in S2 / S3 (where computable), indicating that
  *input importance ordering* is preserved across sex even as
  *magnitudes* differ.

### Two structural Pulse 4.3.1 findings (full-sweep numbers)

* **F-003** Pulse PaO2 > 600 mmHg at FiO2 = 1.0 healthy adults: 34
  implausibly-flagged runs (91 % at FiO2 ≥ 0.95). The hyperoxia
  overshoot scales up cleanly from the pilot (3 / 16) to the full sweep.
* **F-004** Pulse VC-AC delivered Vt CV > 5 % within steady-state window:
  264 / 1,280 runs (20.6 %), including healthy adults at standard
  ventilator settings. Pulse's "preferred mode" is not steady-state for
  one in five sampled (PEEP, Vt, RR) combinations.

### Reliability traffic light (Figure 6)

12 green / 24 yellow / 12 red across 48 cells. Best cells: (S2, F),
(S3, F). Worst cell: (S4, M) — red on all six outputs.

### Sobol promotion preview

For each cell × output, the top-3 Morris inputs were classified by
σ / μ\* ratio per the preregistered rule (`promote ≥ 0.6`,
`skip ≤ 0.4`, otherwise `gray`). Result: **72 promote, 55 skip, 17
gray** (out of 144 cell × output × top-3 input combinations). Sobol
bolt-on would meaningfully refine the picture for ~ half of the
top-ranked inputs, particularly on the gas-exchange channels in
S2 / S3 / S4 where σ / μ\* tends to be high.

## Interpretation

The atlas works as designed. Every preregistered hypothesis can be
evaluated. The strongest support is for H1 (48 / 48 pass) and the
strongest *non-finding* is H2 (0 / 1,280 silent clamping under locked
acceptance ranges) — both of which are themselves valuable for the
literature: Pulse is sensitivity-skewed *and* clean-rejection at its
setup boundary.

The most striking unexpected finding is H3's sex stratification: every
single one of the 20 divergence events is in a male cell, with the same
160 input combinations in both sexes. This is a paper-worthy discovery
and is the first quantitative sex-specific reliability finding for
Pulse 4.3.1.

The preregistration's Decision-vs-Data integrity is preserved: no
threshold was modified mid-sweep; no input range was relaxed; no flag
was redefined. The two amendments to preregistration (2026-04-22
rescope; 2026-04-22-b flatline tolerance) both happened *before* any
atlas data was collected.

## Next steps

1. Generate figures (`scripts/make_figures.py`) — done.
2. Fill manuscript headline numbers in `preprint/manuscript.md` —
   done.
3. Update `preprint/interim_findings.md` with full-sweep findings.
4. Polish `README.md` for a broad audience (doctors, engineers,
   students).
5. Single detailed git commit + push to `https://github.com/santinon/pulse_probe.git`.
6. Optional Sobol bolt-on (preregistration §Sampling method) — 72
   promotions × ~50 runs each ≈ 3,600 runs, ~ 13 h compute. Defer
   unless reviewers request.
7. Zenodo deposit of the full Parquets + raw CSVs after the preprint
   is on arXiv.
