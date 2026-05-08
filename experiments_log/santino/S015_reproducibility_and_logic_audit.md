---
id: S015
author: santino
date: 2026-05-04
status: done
tags: [reproducibility, verification, audit, pre-publication, docker, determinism, logic-validation]
linked_code:
  - src/detector.py
  - src/analysis_morris.py
  - src/scenario.py
  - src/sampler.py
  - src/aggregator.py
  - src/runner.py
  - engine/Dockerfile
  - tests/audit_S015/
linked_data:
  - data/runs/full_sweep/aggregated.parquet
  - data/runs/full_sweep/morris_sample.parquet
  - data/runs/s015_subset_repro/  (new, 40-run audit subset)
  - results/  (audit re-aggregation target)
supersedes: ""
related: [S005, S006, S007, S013, S014]
---

# S015 — Reproducibility and Logic Audit (pre-publication double-check)

## Hypothesis

Every published number in the manuscript is reproducible from the
canonical inputs, by the *current* code on the *current* atlas Docker
image, with no silent drift since the artifact was generated. Beyond
bit-exact reproduction (already verified in S007), the analysis code
itself is correct under independent logic tests: known positives flag,
known negatives stay clean, the Morris μ\* arithmetic matches a
hand-computable reference, and the pipeline does not silently process
physiologically impossible inputs.

## Motivation (why)

The maintainer asked for a full audit before submission, on the
principle that *every paper should withstand the question "are you sure
none of these numbers are wrong?"*. S007 already established three-layer
bit-exact reproducibility (config regen, μ\* re-implementation, 5-run
Docker re-execution) but did not address two threats that have grown
since:

1. **Code drift between artifact creation and now.** S006/S008/S009/
   S011/S012/S013/S014 each touched parts of `src/` and `engine/`
   between their respective artifact dates and today (2026-05-04). The
   committed analysis parquets may no longer match what the *current*
   code produces from the *current* CSVs.
2. **Engine image rebuild side-effects.** `engine/Dockerfile` gained
   the S014 SDK sed-patch on 2026-04-28 (commit `ae76ca0`). The patch
   only fires when `InspirationPatientTrigger*` fields are explicitly
   set on a VC-AC action; the original 1,280-run sweep never sets
   them, so the patch *should* be a no-op. We need to verify this
   empirically by re-running a stratified subsample through the
   rebuilt image and bit-comparing CSVs.

This audit is also a logic check: even if every artifact reproduces
bit-exactly, the analysis code might be silently wrong. Phase 3
addresses that with hand-crafted positive controls, negative controls,
arithmetic isolation, and boundary fuzzing.

## Method (how)

### Phase 1 — Environment reset + Tier 0 (Integrity audit)

1. **Docker rebuild** from `engine/Dockerfile` with `--no-cache` to
   guarantee a clean baseline that includes the S014 SDK patch.
2. **Git-history integrity audit.** For every analysis artifact under
   `data/runs/*/aggregated.parquet` and `results/*.csv`, walk
   `git log --follow` on the source files (`src/analysis_*.py`,
   `src/detector.py`, `src/scenario.py`, `src/sampler.py`,
   `src/aggregator.py`) and flag any commit whose date is *after* the
   artifact's last-modified time. If any analysis-side file changed
   since an artifact was produced, that artifact is potentially stale
   under the current code path.
3. **Pytest run** — confirms the existing CI gate (S009) is still
   green on the current code.
4. **Re-run all analysis from existing CSVs.** Regenerate
   `aggregated.parquet`, the Morris indices, sex-vs-mass, S012, S014
   summaries. Byte-compare each regenerated file against the
   committed file. Any mismatch is a code-drift finding.

### Phase 2 — Tier 1 (S014 patch isolation)

1. Stratified random subsample of 40 runs from `full_sweep`: 5 per
   cell × 8 cells, fixed seed = 42 for audit reproducibility.
2. Re-execute each through the freshly-rebuilt `pulse-atlas-engine`
   image into `data/runs/s015_subset_repro/<case_id>/`.
3. Byte-compare each new `output.csv` against
   `data/runs/full_sweep/<cell>/<case_id>/output.csv`.
4. **Halt criterion:** if any single CSV diverges, stop and report
   which channels drifted before any further work.

### Phase 3 — AI logic validation tests

Four focused tests in `tests/audit_S015/`:

1. **Synthetic positive control.** Hand-craft a 10-row CSV that
   deliberately trips each of the four detector flags in turn
   (clamped via fake log, diverged via NaN, implausible via HR=300,
   not_steady_state via Vt CV > 5%). Assert the detector fires the
   expected flag in each case.
2. **Negative control.** Run the detector on a real `clean`-flagged
   `output.csv` from `data/runs/full_sweep/`. Assert all four flags
   stay false.
3. **Math isolation on Morris μ\*.** Construct a hand-computable
   trajectory pair set with known elementary effects, feed through
   `analysis_morris._morris_stats` and `_block_bootstrap_mu_star_ci`,
   compare to manual computation.
4. **Boundary fuzzing.** Pass impossible physiological values
   (negative weight, RR = 900, FiO2 = -0.5, SBP = 0) through the
   pipeline. Document whether the code raises, silently propagates,
   or relies on Pulse-side rejection.

## What we tried (chronological)

### 2026-05-04 — kickoff

* Tasks 6–15 created (TaskList).
* `pulse-atlas-engine:latest` exists from 5 days ago (built around
  S014 work, image hash `3b18bdc08660`, 5.54 GB). Initiated
  `--no-cache` rebuild for clean baseline.
* Working tree clean; `main` synced to `origin/main` after commit
  `ae76ca0`.

### Phase 1 — Tier 0 integrity audit

#### P1.1 Docker rebuild
* `docker build --no-cache -t pulse-atlas-engine engine/` succeeded
  (~7 min). New image hash `b2e0e807803d`, 5.54 GB. Includes the S014
  SDK sed-patch.

#### P1.2 Git-history integrity audit
Source-file commit timeline since each artifact was generated:

| Source file | Last touched | Commit |
|---|---|---|
| `src/detector.py` | 2026-04-27 | 439e01e (S011), 390ea4a (S009) |
| `src/analysis_morris.py` | 2026-04-27 | 390ea4a (S009) |
| `src/analysis_compare.py` | 2026-04-26 | c8e892c (S008) |
| `src/scenario.py` | 2026-05-04 | ae76ca0 (S014) |
| `src/sampler.py` | 2026-04-26 | 741d490 (initial) |
| `src/aggregator.py` | 2026-04-26 | 741d490 (initial) |
| `src/runner.py` | 2026-04-26 | 741d490 (initial) |

**Drift candidates (artifact older than its source code):**

| Artifact | Generated | Source modified after | Drift risk |
|---|---|---|---|
| `data/runs/full_sweep/aggregated.parquet` | 2026-04-26 | detector 2026-04-27 (S009/S011), scenario 2026-05-04 (S014) | YES — detector changed (additive only per diff inspection) |
| `results/morris_indices.parquet` | 2026-04-26 | analysis_morris 2026-04-27 (S009) | possible — diff shows new `trajectory`/`n_trajectories` cols, same point-estimate algorithm |

**Diff inspection (decisive):**
* `src/detector.py` 741d490 → HEAD: removed unused `import math`,
  added `primary_flag` property and one column to `summary()`. **No
  flag-decision code path changed.** Drift is purely additive (one new
  column `primary_flag`).
* `src/analysis_morris.py` 741d490 → HEAD: added `_block_bootstrap_mu_star_ci`,
  rewired `morris_indices` to use it, added `trajectory` /
  `n_trajectories` cols to outputs. The block-bootstrap change *was*
  applied during commit `c8e892c` (S008), and the committed
  `morris_indices.parquet` is dated 2026-04-26 (same commit); so the
  parquet on disk was already produced by the block-bootstrap path.

#### P1.3 Pytest run
`uv run pytest -q` → **69 passed in 10.26 s**. CI gate green.

#### P1.4 Re-run analysis from existing CSVs + compare
Audit driver: `tests/audit_S015/regen_compare.py`. Regenerates each
artifact into `data/audit_S015/` (never touches `results/` or the
committed parquets), then compares column-by-column to a tolerance of
`atol=1e-9, rtol=1e-9`.

| Artifact | Status | Notes |
|---|---|---|
| `data/runs/full_sweep/aggregated.parquet` | DRIFT | extra col `primary_flag` (expected, additive); 5/1280 `wall_time_s` differ — see below |
| `results/cell_flag_summary.csv` | EXACT | 8 rows, 0 diff |
| `results/morris_indices.parquet` | EXACT | 318 rows, 0 diff |
| `results/h1_top3_fraction.csv` | EXACT | 48 rows, 0 diff |
| `results/sobol_promotion.csv` | EXACT | 144 rows, 0 diff |
| `results/wasserstein_male_vs_female.csv` | EXACT | 24 rows, 0 diff |
| `results/spearman_mu_star.csv` | EXACT | 24 rows, 0 diff |
| `results/clamp_grid.parquet` | EXACT | 1624 rows, 0 diff |
| `results/diverged_grid.parquet` | EXACT | 1624 rows, 0 diff |
| `results/reliability_classification.csv` | EXACT | 48 rows, 0 diff |

**9 / 10 publication artifacts EXACT.** The block-bootstrap CIs in
`morris_indices.parquet` regenerate to `0.00e+00` absolute difference.

The single drift line is on `wall_time_s` — a non-scientific operational
metric — for exactly the 5 case_ids that S007 re-executed (`S1_M_0021`,
`S2_M_0106`, `S2_M_0151`, `S4_M_0002`, `S4_M_0150`). S007's re-runs
overwrote those `run_meta.json` files with new wall-times; their CSV
outputs are bit-exact (verified by S007). The committed
`aggregated.parquet` predates the S007 re-runs and so holds the original
wall-times. **No manuscript number depends on `wall_time_s`.**

### Phase 2 — Tier 1 (S014 patch isolation)

40-run stratified subsample (5 / cell × 8 cells, seed=42),
re-executed through the freshly rebuilt `pulse-atlas-engine` image
into `data/runs/s015_subset_repro/<case_id>/`. Wall time: ~24 min on
the i5-11400H with 2 parallel workers.

| Outcome | Count | Notes |
|---|---|---|
| BIT_EXACT (CSV) | 38 / 40 | `output.csv` byte-identical to the S006 original |
| NEW_CSV_MISSING + originally diverged | 2 / 40 | `S1_M_0159`, `S4_M_0024` |

The 2 "missing CSV" cases are runs that originally diverged in S006 with
`exit_code=1` (no CSV written by Pulse on solver failure). The audit
re-execution **also** produced `exit_code=1` on both — divergence
reproduces exactly:

| case_id | original exit_code | audit exit_code | match |
|---|---|---|---|
| `S1_M_0159` | 1 (diverged) | 1 (diverged) | YES |
| `S4_M_0024` | 1 (diverged) | 1 (diverged) | YES |

**Reframed: 40 / 40 reproduction-consistent.** The S014 sed-patch in
`engine/Dockerfile` has zero observable side-effect on the original
1,280-run sweep. Manuscript numbers from S006 / S008 / S009 / S011 /
S012 are safe under the rebuilt image.

Detail in `data/audit_S015/subset_repro_report.json`.

### Phase 3 — AI logic validation

#### P3.1 Synthetic positive control on detector

Driver: `tests/audit_S015/test_p31_positive_control.py`.

| Test | Expected | Result |
|---|---|---|
| T1   | `clamped` fires on real Pulse error log | PASS (matched 2 patterns) |
| T1b  | `clamped` does NOT fire on `Resetting the target...` solver text | PASS |
| T2   | `diverged` fires on NaN at row 5 | PASS |
| T2b  | `diverged` fires on `exit_code=1` | PASS |
| T3   | `implausible` fires on HR mean = 300 (above 220 hard bound) | PASS |
| T4   | `not_steady_state` fires on Vt alternating 250/750 (CV ≈ 0.518) | PASS |
| T5   | `classify()` integration: extreme HR → primary_flag = `implausible` | PASS |
| T6   | Priority ordering: clamped + implausible → primary = `clamped` | PASS |
| T7   | Drift: HR linspace(70, 80) over 60 s → not_steady_state fires (Δ60s = +10 > 5) | PASS |

7 / 7 PASS. Detector wiring verified end-to-end against deliberately
constructed positives.

#### P3.2 Negative control

Driver: `tests/audit_S015/test_p32_negative_control.py`. Picked 5
known-clean cases from the master parquet (one per scenario tier where
possible: `S1_M_0000`, `S2_M_0000`, `S3_M_0000`, `S4_M_0002`,
`S1_M_0001`), re-classified each with the *current* detector, and
asserted all four flags stayed false.

5 / 5 stayed clean. Steady-state means within physiological ranges
(e.g. S1_M_0000: HR=99.1, MAP=87.9, Vt=319, SpO2=0.996). Detector
does not produce false positives on real clean Pulse runs.

#### P3.3 Morris μ\* math isolation

Driver: `tests/audit_S015/test_p33_math_isolation.py`. Hand-built EE
array `[+10, -6, +8, -4, +12, -2]`:
* Expected μ = 3.0, μ\* = 7.0, σ = 7.874008 (ddof=1).
* `_morris_stats` returned (3.0, 7.0, 7.874008) — diff `0.0 / 0.0 / 0.0`.
* Edge cases: single EE → (5, 5, 0); empty EE → (NaN, NaN, NaN). Both pass.
* Block bootstrap (3 trajectories × 2 EE, B=5000, α=0.05):
  CI = `[6.0000, 8.0000]`, brackets the 7.0 point estimate.
* Single-trajectory block bootstrap correctly returns NaN CI (Morris
  is not estimable on one trajectory).
* Independent OAT cross-check: hr → μ\* = 5.0, vt → μ\* = 10.0 — matches
  hand math.

All 6 sub-tests PASS. Morris arithmetic is correct in isolation.

#### P3.4 Boundary fuzzing

Driver: `tests/audit_S015/test_p34_boundary_fuzz.py`. Behaviour table:

| Input | Where | Outcome | Detail |
|---|---|---|---|
| `trajectories=0` | `sample_morris` | RAISES | `ValueError: trajectories must be >= 1` |
| `levels=1` | `sample_morris` | RAISES | `ValueError: levels must be >= 2` |
| `hr=-50` | `build_config` | SILENT | passes through to Pulse |
| `rr=900` | `build_config` | SILENT | passes through to Pulse |
| `fio2=-0.5` | `build_config` | SILENT | passes through to Pulse |
| `sbp=0, dbp=0` | `build_config` | SILENT | passes through to Pulse |
| `vt=5000` | `build_config` | SILENT | passes through to Pulse |
| `scenario='S99'` | `build_config` | RAISES | `KeyError: "unknown scenario 'S99'"` |
| `sex='X'` | `build_config` | RAISES | `KeyError: "unknown sex 'X'"` |
| `clip_dbp(sbp=100, dbp=90)` | `clip_dbp_to_pulse_constraint` | OK | clipped to 75.0, was_clipped=True |
| `HR=1000` (steady-state mean) | `check_implausible` | FIRED | hard bound rejection observed |

**Finding (audit-relevant, not a defect):** `build_config` does NOT
validate physiological bounds on `hr`, `rr`, `vt`, `fio2`, `peep`,
`sbp`, `dbp`. This is the *documented* atlas design choice (see
`src/scenario.py` lines 7–13 + 64–68): Morris geometry must stay
intact, so atlas-side validation would corrupt the EE structure.
Defense in depth = (i) Morris sampler bounds (locked in
`preregistration.md` §Inputs), (ii) Pulse-side rejection emitting
loud `[ERROR]` lines and `exit_code != 0` (caught by
`detector.check_clamped` + `check_diverged`), (iii) detector
`check_implausible` rejecting any output mean outside hard
physiological bounds.

Path that *should* raise (scenario / sex keys) does raise. Path that
*should* clip (DBP/SBP ratio) clips. Path that *should* fire
(implausible) fires. The only "SILENT" outcomes are the
physiological-value pass-throughs, which are intended and audited.

## Results

**One-line summary:** every published number reproduces; the analysis
code is correct in isolation; the S014 sed-patch has zero side-effect on
the original sweep; the only drift is metadata (`wall_time_s` for 5
S007-rerun cases) which does not affect any manuscript claim.

**Detailed:**

| Phase | Result |
|---|---|
| P1.1 Docker rebuild | OK, new image `b2e0e807803d` |
| P1.2 Git-history integrity | additive drift in detector + analysis_morris (new columns), no algorithm change in flag decisions or μ\* point estimates |
| P1.3 Pytest | 69 passed |
| P1.4 Re-run analysis + compare | 9/10 EXACT, 1 metadata-only drift on `wall_time_s` (5 cases, S007 attribution) |
| P2 Stratified 40-run subset re-execution | 38/40 BIT_EXACT CSV; 2/40 originally-diverged runs reproduce divergence with same `exit_code=1` → 40/40 reproduction-consistent |
| P3.1 Detector positive control | 7/7 PASS |
| P3.2 Detector negative control | 5/5 PASS |
| P3.3 Morris math isolation | 6/6 PASS |
| P3.4 Boundary fuzzing | as designed: keys raise, ratio clips, physiological values pass through to Pulse + detector |

## Decision

**The pre-publication double-check passes.** No new experiment is
required. No manuscript number needs revision. Specifically:

* `morris_indices.parquet` regenerates EXACT (point estimates and
  block-bootstrap CIs to `0.00e+00`).
* H1 / H3 / H4 / clamp / divergence / reliability-classification
  artifacts all regenerate EXACT.
* The 38 + 2 = 40 re-execution sample confirms that the rebuilt
  S014-patched image produces bit-identical outputs on clean runs and
  reproduces divergence on the same 2 originally-diverged inputs.
* Detector logic: positives fire on hand-crafted positives; negatives
  stay clean on real clean runs; Morris arithmetic matches hand math;
  boundary fuzzing confirms the documented defense-in-depth contract.

**Two notes for the maintainer to consider before submission:**

1. **`wall_time_s` provenance.** Five rows in
   `data/runs/full_sweep/aggregated.parquet` have a `wall_time_s` value
   that does not match the current `run_meta.json` on disk for the same
   case. Cause: S007 re-ran those 5 cases and overwrote
   `run_meta.json`. CSV outputs are bit-exact (S007 verified). Options:
   (a) accept (current state, no scientific impact), (b) regenerate
   `aggregated.parquet` to refresh the metadata-only column. Recommend
   (a) — `wall_time_s` is operational, not scientific.

2. **Boundary-fuzz disclosure (optional manuscript edit).** Section
   2.6 / Limitations could note that atlas-side scenario validation is
   restricted to scenario/sex keys; physiological-bound enforcement is
   delegated to the Morris sampler ranges + Pulse-side rejection +
   detector `implausible` flag. This is currently implicit in the
   `clamped` flag rationale; an explicit one-line disclosure would
   strengthen reviewer defense without changing any number.

No other actions warranted. Halting per the audit's pre-registered
"halt and report" rule.

## Artifacts produced (all under `data/audit_S015/`)

* `regen_compare.log` — full P1.4 stdout
* `full_sweep_aggregated.parquet` — regenerated master (audit copy, NOT
  a publication artifact)
* `cell_flag_summary.csv`, `morris_indices.parquet`,
  `h1_top3_fraction.csv`, `sobol_promotion.csv`,
  `wasserstein_male_vs_female.csv`, `spearman_mu_star.csv`,
  `clamp_grid.parquet`, `diverged_grid.parquet`,
  `reliability_classification.csv` — all audit copies, used only for
  comparison
* `subset_repro.log` + `subset_repro_report.json` — Phase 2 detail
* `p31_positive_control.log`, `p32_negative_control.log`,
  `p33_math_isolation.log`, `p34_boundary_fuzz.log` — Phase 3 logs
* `data/runs/s015_subset_repro/` — 40 re-execution dirs (per-case
  `output.csv`, `pulse.log`, `run_meta.json`, `config.json`)
* `tests/audit_S015/` — driver scripts, all callable by future
  maintainers to re-run the audit

## What was NOT touched (per audit rule)

* `preprint/manuscript.md`
* `preprint/interim_findings.md`
* Any file under `results/`
* Any file under `data/runs/full_sweep/` (read only)
* Any file under `data/runs/{continuous_ards, sex_vs_mass,
  seed_stability_S2M_seed43, s014_trigger_lockout}` (read only)
* Pre-existing committed artifacts of any kind

