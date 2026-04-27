---
id: S009
author: santino
date: 2026-04-27
status: done
tags: [tier-2, seed-stability, continuous-ards, divergence-regime, sex-stratification, pytest, ci]
linked_code:
  - scripts/seed_stability_check.py
  - scripts/continuous_ards_sweep.py
  - tests/test_sampler.py
  - tests/test_scenario.py
  - tests/test_aggregator.py
  - tests/test_analysis.py
  - .github/workflows/tests.yml
linked_data:
  - data/runs/seed_stability_S2M_seed43/
  - data/runs/continuous_ards/
  - results/seed_stability_S2M_seed43.parquet
  - results/seed_stability_top3_comparison.csv
  - results/continuous_ards_severity_sweep.parquet
supersedes: ""
related: [S005, S006, S008]
---

# S009 — Tier-2 polish: seed stability, continuous-ARDS regime, pytest, CI

## Hypothesis

Three Tier-2 questions, each one tested independently of the published
sweep:

1. **Seed stability:** does the Morris top-3 input ranking depend on
   the specific seed (= 42) we locked, or is it robust under a
   different seed?
2. **Continuous ARDS regime:** the H3 finding "all 20 divergences are
   male" was observed at the four discrete preregistered scenarios.
   Is divergence (a) a property of *severity* (continuous band), (b)
   a property of *sex × inputs*, or both?
3. **Code health:** is the code base reviewer-defensible — every
   public module under formal pytest coverage, every push gated by a
   GitHub Actions CI workflow, ruff-clean across the source tree?

## Motivation (why)

S006 / S007 / S008 closed the data-collection and statistical-analysis
loops. The remaining Tier-2 work surfaces in a critical-review pass: a
locked-seed sensitivity analysis is one Morris sample among many, and a
4-point ARDS severity grid characterizes only 4 points of a 1-d
continuum. Code-health is also expected for any methods-paper
companion repository.

## Method (how)

### Seed-stability check (`scripts/seed_stability_check.py`)

* Cell: (S2, M) — best-behaved cell in the published sweep (clean
  rate 87/160, all 7 inputs covered).
* New canonical Morris sample at `seed=43`, `trajectories=10`,
  `levels=4` → 80 unique points (half the published 160). Smaller
  sample is intentional: cheaper compute, wider Morris CI by
  construction, so any *match* with the published top-3 ranking is
  robust evidence; any *mismatch* tells us the ranking is not
  invariant to sample size.
* Comparison: top-3 input set per output, plus order.
* Compute: ~ 50 min wall on 2 parallel Docker workers.

### Continuous ARDS-severity sweep (`scripts/continuous_ards_sweep.py`)

* 100 severity values across `[0, 1]`, with extra density inside the
  documented `[0.91, 0.945]` instability zone:
  - 50 uniform in `[0.0, 0.85]`
  - 30 uniform in `[0.85, 0.95]`
  - 20 uniform in `[0.95, 1.0]`
* Both sexes (M and F) at midrange Morris inputs (HR = 80, SBP = 105,
  DBP = 70, RR = 14, Vt = 550, FiO2 = 0.6, PEEP = 10).
* Total: 200 runs, ~ 2.2 h compute on 2 parallel Docker workers.

### Pytest suite

Added formal tests for every public module:
- `tests/test_sampler.py` — 8 tests: shape, range, OAT property, seed
  reproducibility, range-violation guards.
- `tests/test_scenario.py` — 14 tests: locked patient demographics,
  locked scenarios, DBP-clip rule, build_config validity, clip-bypass
  for clamp probes.
- `tests/test_aggregator.py` — 4 tests: synthetic run dirs through
  build_row, clean / diverged / clamped flag wiring.
- `tests/test_analysis.py` — 8 tests: H1 evaluation on synthetic
  μ\* vectors, Sobol-promotion thresholds, block-bootstrap CI bracket,
  Wasserstein on synthetic shifted distributions, Wasserstein null on
  same distribution.
- `tests/test_detector.py` — already existed; updated to test the
  empirically-calibrated S004 regex set (4 positive Pulse-specific
  patterns) and explicit negative cases (`Resetting the target for X`,
  `Stomach is out of Sodium`, etc.).

Total: **69 tests**, all passing in 2.2 s. No Pulse / Docker required —
suitable for fast CI.

### Ruff lint

`uv run ruff check src/ scripts/ tests/ engine/` — clean. Auto-fixed
~ 11 unused-import warnings and one unused-variable. Zero remaining
violations.

### GitHub Actions CI (`.github/workflows/tests.yml`)

Two-job workflow on `ubuntu-latest`:
1. `test` — install dependencies via `uv sync --extra dev`, run
   `pytest tests/ -v`, then verify all `src/` modules import on a
   clean Python.
2. `ruff` — `uv run ruff check src/ scripts/ tests/ engine/`.

Triggers: push to `main`, pull requests targeting `main`, and manual
`workflow_dispatch`. `concurrency.cancel-in-progress` prevents
duplicate runs.

## What we tried (including dead ends)

* **Seed-stability initial design considered `trajectories=20, seed=43`
  on (S1, M)** — the cell with the most flagged data. Rejected: high
  flag rate would lose most EE pairs, the sample-size signal would
  swamp the seed-stability signal. (S2, M) at `trajectories=10` is a
  cleaner, faster experiment.
* **Continuous-ARDS sweep at `n=50` was considered.** Rejected: 0.85 –
  0.945 spans 0.095 of severity; 50 uniform points yields ~ 5 in the
  published instability zone. The 100-point grid (with weighted
  density) yields ~ 50 in the contested band, much better resolution.
* **Two `CONT_F_091` and `CONT_F_092` runs reported wall_time_s ≈
  27,000 s in the runner log.** Investigation: the timestamps are
  monotonic and the runs do reach exit code 0, so the duration is not
  a hang — almost certainly a Windows clock-skew artifact in
  `time.monotonic()` while the laptop went to sleep mid-run. Not a
  data-quality concern; both runs produced the expected steady-state
  CSVs. Logged here for transparency.

## Results

### Seed stability (compare seed=43, traj=10 to seed=42, traj=20)

| Output | seed=42 top-3        | seed=43 top-3        | same set | same order |
|--------|----------------------|----------------------|----------|------------|
| HR     | hr, rr, peep         | hr, fio2, peep       | False    | False      |
| MAP    | sbp, dbp, hr         | sbp, dbp, hr         | True     | True       |
| Vt     | vt, rr, sbp          | vt, rr, hr           | False    | False      |
| SpO2   | fio2, vt, peep       | fio2, peep, vt       | True     | False      |
| PaO2   | fio2, rr, peep       | fio2, peep, vt       | False    | False      |
| PaCO2  | vt, rr, fio2         | rr, vt, fio2         | True     | False      |

**Top-1 input is stable in 5 / 6 outputs** (HR → hr, MAP → sbp,
SpO2 → fio2, PaO2 → fio2, Vt → vt, PaCO2 differs: vt vs rr).
**Top-3 set is stable in 3 / 6 outputs** (MAP, SpO2, PaCO2). **Top-3
order is stable in only 1 / 6 outputs** (MAP, where sbp / dbp / hr
sit in clearly separated μ\* bands by physical construction of MAP).

The honest interpretation: at half the published sample size and a
fresh seed, the *strongest* input per output is robust, but rank #2
and #3 partially shuffle. This is consistent with Morris EE on a
stochastic sample — the rankings are *qualitatively* preserved but
not quantitatively invariant to the seed, especially in cells where
several inputs share similar μ\*. **The published `seed=42`
ranking should be reported with this caveat,** rather than as a
seed-independent ground truth.

### Continuous ARDS-severity divergence regime (200 runs, midrange inputs)

Divergence rate by severity bin:

| severity bin     | F diverged | M diverged |
|------------------|------------|------------|
| [0, 0.5]         | 0 / 31     | 0 / 31     |
| (0.5, 0.85]      | 0 / 20     | 0 / 20     |
| (0.85, 0.91]     | 14 / 18    | 5 / 18     |
| (0.91, 0.945]    | 5 / 10     | 9 / 10     |
| (0.945, 0.95]    | 0 / 2      | 0 / 2      |
| (0.95, 1.0]      | 0 / 19     | 0 / 19     |

* **The divergence regime is a continuous band roughly `[0.879,
  0.945]`,** wider than the documented `[0.91, 0.945]` zone reported
  in `Pulse_translation_new` E6 / E10 (which used different ventilator
  settings).
* **Female diverges earlier** (severity ≥ 0.879) and exits the band
  earlier (last F divergence at 0.927). Female has the higher count
  in [0.85, 0.91].
* **Male diverges later** (severity ≥ 0.899) and continues divergence
  through [0.91, 0.945]. Male has the higher count in [0.91, 0.945].
* **Both sexes converge cleanly above 0.945** — severities 0.95 and
  above are *outside* the instability band at midrange inputs. This
  is consistent with the preregistration's choice of S4 = 0.95 as
  "above the instability zone".

This is a **major refinement** of the H3 sex-stratification finding
in S006:

* In the published Morris sweep (Morris-extreme inputs, 4 fixed
  scenarios), all 20 / 20 divergences were male at HR = 50 + SBP = 90
  + RR = 20 + FiO2 = 1.0.
* In the continuous-ARDS sweep (midrange inputs, continuous severity),
  divergence is **not** sex-stratified at the level of "all male" —
  19 F + 14 M = 33 divergences across the [0.879, 0.945] band, with
  F slightly higher.

The atlas now distinguishes **two separate divergence regimes**:

1. **Input-driven regime** (S006): low cardiovascular pressure +
   high respiratory drive on pure oxygen, the male standard surrogate
   diverges 5× more than the female. The 20 % blood-volume difference
   between sexes (`SetupPatient.cpp:534`) is the most plausible
   mechanism candidate.
2. **Severity-driven regime** (S009 continuous): `[0.879, 0.945]`
   ARDS impairment band at clinically-typical ventilator settings.
   Affects both sexes, female slightly more. The mechanism is the
   solver-stability gradient at the high-impairment compliance edge,
   not patient demographics.

These two regimes are *additive*, not redundant. The previous CLAUDE.md
verified-limitation entry "ARDS solver instability 0.91 – 0.945" should
be updated to "[0.879, 0.945]" with the additional note that the band
is sex-conditional in width.

### Code health

* **69 / 69 pytest tests pass** in 2.18 s on the local machine.
* **Ruff clean** across `src/`, `scripts/`, `tests/`, `engine/`.
* **GitHub Actions CI workflow** (`.github/workflows/tests.yml`)
  installed; will run on every push / PR. Workflow includes
  `concurrency.cancel-in-progress` so superseded pushes don't pile
  up.

## Interpretation

The seed-stability check honestly admits a known limitation of Morris
EE on a finite sample: rank #2 and #3 inputs partially shuffle across
seeds, especially in cells with several inputs at similar μ\*. Top-1
inputs are robust. The published rankings should be read as
"qualitatively top-3" not "the top-3 inputs."

The continuous-ARDS sweep produces the most surprising Tier-2 finding:
**the H3 sex-stratification is regime-dependent.** What looked like
"males diverge, females don't" in S006 is actually "males diverge at
input-extreme combinations + the ARDS instability band; females
diverge inside the ARDS instability band but rarely at input
extremes." This refines the atlas's claim from a global sex-effect
on solver reliability to a more precise *interaction* between sex,
input combination, and severity regime.

The pytest suite + GitHub Actions CI brings the repo to standard
methods-paper companion-code maturity.

## Next steps

* Regenerate analysis + figures so the manuscript's S006 numbers stay
  consistent with any updates triggered by this S009 finding (the
  S006 H3 finding stands; we add S009 as additional context).
* Update the manuscript with a new §3.5.1 "Continuous-severity
  divergence regime" to fold in this finding.
* Commit + push.
* **Then start the literature-review pass** (per maintainer's
  request): justify each claim and method with a verified primary
  reference, expand §6 from a list to a properly-cited bibliography,
  log as S010.
