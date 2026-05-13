---
id: S019
author: santino
date: 2026-05-13
status: draft
tags: [sobol, variance-decomposition, reviewer-defense, phase-b, draft, not-executed]
linked_code: [scripts/s019_sobol_bolton.py]
linked_data: []
supersedes: ""
related: [S006, S008, S017, S018]
---

# S019 — Sobol bolt-on (Phase B item B3): DRAFT, ready-to-fire, not executed

## Status

**Draft. Not executed.** This entry documents a ready-to-fire
implementation of the preregistered Sobol variance decomposition on
the 6 Group-B point-estimate-promote cells (manuscript §3.3.1). The
script is `scripts/s019_sobol_bolton.py`; it is preserved in the
repository for future reviewers or practitioners who request the
analysis. It has not been run as part of the current paper because
§3.3.1 already closes the Sobol bolt-on by *redundancy* (the
trajectory-level σ block-bootstrap CI shows 0 / 48 cells are
CI-robustly nonlinear, so Sobol indices would quantify variance
already classified as bootstrap-noise-dominated).

## Hypothesis

If we run Sobol variance decomposition on the 6 Group-B cells, the
resulting S₁ / S_t indices will:

1. Re-confirm the dominant input per cell already identified by
   Morris μ\* (FiO₂ for the 4 PaO₂ cells; RR for (S1_M, PaCO₂);
   V_t for (S4_F, PaCO₂)).
2. Show small but non-negligible interactions on the 6 cells driven
   by the established physiological nonlinearities (shunt-fraction
   kinetics on PaO₂; alveolar-ventilation identity on PaCO₂).
3. Show negligible interactions on the 42 non-Group-B cells (Group A
   noise-dominated cells excluded; 31 cells already CI-robustly
   linear; 11 cells straddling 0.6 with no physiological prior on
   interactions).

The hypothesis is *predicted* by physiology, not *novel* — that is
exactly why §3.3.1 deems Sobol redundant.

## Motivation (why draft-only)

Phase A's σ block-bootstrap CI analysis (`src.analysis_morris.
_block_bootstrap_sigma_ci`) resolved the σ / μ\* ≥ 0.6 trigger at
full evidential weight: 0 / 48 cells are CI-robustly nonlinear.
The preregistered Sobol bolt-on was conditioned on a *signal*
trigger, not a *point-estimate* trigger; the signal is absent.
Running Sobol on cells whose nonlinearity-trigger status is
bootstrap-borderline produces S₁ / S_t indices that quantify
bootstrap noise, not a physiological interaction.

The §3.3.1 closure argument is therefore:

* The preregistered trigger fires 0 / 48 times CI-robustly.
* The interaction structure on the 6 Group-B cells is *a priori*
  physiologically established (shunt kinetics + alveolar-
  ventilation identity).
* The qualitative input rankings are already in §3.2 Morris main
  effects.

A reviewer requesting Sobol anyway can fire this script. A reviewer
who reads §3.3.1 will not, because the evidential argument closes
the bolt-on before compute is necessary.

## Method (what `scripts/s019_sobol_bolton.py` will do when fired)

### Sample generation

`SALib.sample.sobol.sample(problem, N=256, calc_second_order=False, seed=42)`
on the locked 7-input problem (`src.sampler.salib_problem()`). With
`calc_second_order=False`, the SALib row count is N × (D + 2) =
256 × 9 = **2,304 rows per cell**. Total: 6 cells × 2,304 = **13,824
Pulse runs**.

(The protocol can be raised to `calc_second_order=True` for full
second-order S_{ij} indices; row count then doubles to ~28k. Not
recommended for the first run.)

### Cell × sample → atlas configs

Each Sobol sample row is materialised as a per-cell atlas config via
`src.scenario.build_config()` — exactly the same code path as the
Morris sweep, so any clamping / divergence behaviour is attributable
to the engine, not to a wrapper artefact. Each run gets:

* `case_id = f"sobol_{cell_tag}_{run_idx:05d}"` (e.g.
  `sobol_S2_M_00000`).
* DBP/SBP ≤ 0.75 ratio enforced by `clip_dbp_to_pulse_constraint`
  (same as S006).
* `atlas_meta.sobol_meta` recording cell, primary output,
  dominant input, run_idx.

### Execution

`src.runner.run_many(...)` at 2 parallel workers (laptop budget;
raise on cluster after re-verifying RAM/CPU headroom). Per-run wall
time ~30 s — total ~58 h on laptop at 2 workers, hence
cluster-required.

The script is **resume-safe**: it skips cases whose `output.csv`
already exists, so interrupted sweeps can be continued.

### Analysis

`SALib.analyze.sobol.analyze(problem, Y, calc_second_order=False)`
on each cell's per-output mean (HR_mean, MAP_mean, V_t_mean,
SpO2_mean, PaO2_mean, PaCO2_mean). Writes one row per (scenario,
sex, output, input) tuple to `results/sobol_indices.parquet` with
columns S1, ST, S1_conf, ST_conf, n_runs.

## The 6 Group-B cells

Defined in `scripts/s019_sobol_bolton.py` `GROUP_B_CELLS`:

| Cell    | Primary output | Dominant input (point-estimate) | Source nonlinearity                          |
|---------|----------------|----------------------------------|-----------------------------------------------|
| S2_M    | PaO₂           | FiO₂                             | shunt-fraction kinetics in ARDS              |
| S2_F    | PaO₂           | FiO₂                             | shunt-fraction kinetics in ARDS              |
| S3_M    | PaO₂           | FiO₂                             | shunt-fraction kinetics in ARDS              |
| S3_F    | PaO₂           | FiO₂                             | shunt-fraction kinetics in ARDS              |
| S1_M    | PaCO₂          | RR                               | alveolar-ventilation identity (V̇A = RR · V_A) |
| S4_F    | PaCO₂          | V_t                              | alveolar-ventilation identity (V̇A = RR · V_A) |

The 2 Group-A cells excluded:

* (S1, F, SpO2, PEEP) — μ\* = 0.0037, σ = 0.0068. SpO2 at hemoglobin
  saturation ceiling; σ is floating-point noise.
* (S1, M, SpO2, V_t) — μ\* = 0.028, σ = 0.023. Same reason.

## Findings — *[empty by design; this is a draft]*

When the script fires, results go in `results/sobol_indices.parquet`
and a results paragraph would join this log under F-S019-A, B, C
(per-cell S₁ / S_t tables, comparison to Morris μ\* rankings,
agreement with the §3.3.1 redundancy argument).

## What this log entry does for the manuscript

Nothing right now. §3.3.1 closes the Sobol bolt-on with a
forward-reference to `scripts/s019_sobol_bolton.py` so a reviewer
can verify the script exists and read the protocol without leaving
the repository. If the script is fired in the future and produces
S₁ / S_t indices that *contradict* the §3.3.1 closure (e.g., a
S_t value significantly above the trajectory-bootstrap-implied σ /
μ\* on a cell classified as CI-robust linear), §3.3.1 would need
revision — but this is not expected based on the physiological
priors.

## Caveats

* The script consumes the locked Morris-sample input bounds
  (`src.sampler.salib_problem()`), so the Sobol indices are
  comparable to the Morris μ\*/σ in `results/morris_indices.parquet`
  cell-for-cell. If the bounds change in a future paper, the script
  must be re-validated.
* RNG seed is fixed at 42, matching the Morris sweep. Different
  seed → different Sobol sample → small numerical differences in
  S₁ / S_t (within S1_conf / ST_conf bands).
* The aggregator's clean-only filter is *not* applied before Sobol
  analysis — Sobol expects all-rows with NaN propagation for
  diverged runs. SALib v1.5+ drops incomplete rows internally; check
  the SALib version in the cluster environment before firing.
* Per-cell N = 256 yields S1_conf / ST_conf bands of width ≈ ±0.05
  for first-order indices; raising N to 512 narrows by ~√2 but
  doubles compute. The current default (N = 256) is the minimum
  for "publishable" S1 / ST with bootstrap confidence intervals.

## Related artifacts

* Manuscript: `preprint/manuscript.md` §3.3.1 (closure-by-redundancy
  with forward-reference to this script).
* Script: `scripts/s019_sobol_bolton.py` (CLI: sample → run → analyse).
* Roadmap: `ROADMAP_PHASE_B.md` §B3 (canonical protocol).
* Phase A CI evidence: `results/morris_indices.parquet` columns
  `sigma_lo`, `sigma_hi` and the σ / μ\* bootstrap distribution
  described in §3.3.1.
* Morris analysis pipeline: `src/analysis_morris.py` (the same
  module reused for Sobol).

## Ready-to-fire checklist (for the future operator)

1. Confirm Docker image: `pulse-atlas-engine:latest` (the original
   sweep image; not the `:bv-override` S018 variant — S019 uses the
   default BV path).
2. Confirm cluster / Colab compute budget: ≥ 24 h continuous, ≥ 4 GB
   RAM headroom, ≥ 12 CPU.
3. Dry-run on one cell with N = 8: `--dry-run --cells S2_M --N 8`.
4. Full sweep: `--N 256 --workers 2 --output-root data/runs/s019_sobol`.
   On a real cluster, `--workers` can rise after re-verifying RAM
   headroom (each Pulse container is `--memory=1g --cpus=3`).
5. Analyse: `--analyse-only --indices-out results/sobol_indices.parquet`.
6. Fill F-S019-A/B/C in this log. Update §3.3.1 to either confirm
   the redundancy argument with the empirical Sobol indices or
   to surface any contradiction.
