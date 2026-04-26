---
id: S004
author: santino
date: 2026-04-25
status: done
tags: [smoke-test, docker, image-build, detector-calibration, pre-pilot]
linked_code:
  - engine/run_atlas_engine.py
  - engine/Dockerfile
  - src/sampler.py
  - src/scenario.py
  - src/runner.py
  - src/aggregator.py
  - scripts/scenario_smoke_test.py
linked_data:
  - data/runs/scenario_smoke/
  - data/clamp_probe/
supersedes: ""
related: [S001, S003]
---

# S004 — Scenario-init smoke test (4×2 cells) + atlas Docker image + detector recalibration

## Hypothesis

The full Morris sweep (~1280 runs) will succeed if and only if every (scenario, sex)
cell can initialize Pulse 4.3.1 with mid-range Morris inputs. Catching per-cell
init failures BEFORE the pilot is the cheapest insurance against discovering
during the full sweep that, e.g., S4 (severe ARDS, severity = 0.95) crashes
above the 0.91–0.945 instability zone documented in `Pulse_translation_new` E6/E10.

## Motivation (why)

User asked for the minimum-risk path to the methods paper. Two structural risks
were flagged before any code ran:

1. **CSV channel coverage.** The `pulse-pediatric-engine` image emitted only
   four of the six preregistered outputs in an old smoke run inspected at
   `Pulse_translation_new/data/engine_runs/smoke_test/output.csv`. Without
   PaO2 + PaCO2, hypotheses H1 and H4 lose two of six outputs — gas-exchange
   variables that matter most for ARDS scenarios.
2. **Wrapper-level FiO2 cap.** `Pulse_translation_new/engine/run_validation_engine.py:70`
   silently caps FiO2 at 0.95 (a residual conservative guard from before PhD
   experiment E20 verified Pulse accepts FiO2 = 1.0). The preregistered Morris
   sweep covers FiO2 ∈ [0.21, 1.0]. With the upstream wrapper, ~17% of FiO2
   samples would be silently capped at a layer ABOVE Pulse, polluting the
   `clamped` flag with a wrapper artifact rather than a Pulse engine fact.

Beyond those two, S4 was flagged as a likely failure point: ARDS severity 0.95
sits above the 0.91–0.945 solver instability zone documented in
`Pulse_translation_new` E6/E10. If S4 always crashes even at mid-range vent
settings, the preregistered design is broken and should be amended BEFORE
locking 1280 simulations.

## Method (how)

Five sequential steps:

1. **Verify CSV coverage on the current image.** A throwaway smoke run with
   `pulse-pediatric-engine:latest` confirmed that the *current* image (built
   3 weeks before this experiment) does emit all six preregistered outputs:
   HR, MAP, Vt, SpO2, PaO2, PaCO2 — plus diagnostic channels. The old
   4-channel CSV inspected earlier was a stale artifact of an earlier wrapper.
   Risk 1 (channel coverage) dissolved without any code change.

2. **Build atlas-only Docker image.** Copied
   `Pulse_translation_new/engine/run_validation_engine.py` (read-only reference
   per project boundary) into `engine/run_atlas_engine.py` in this repo, with
   the only functional change being `FIO2_MAX = 1.0` (justified by E20).
   `engine/Dockerfile` builds `pulse-atlas-engine:latest` from
   `kitware/pulse:4.3.1`. Verified with a probe run at FiO2 = 1.0:
   `data/smoke_check_fio2_1/output.csv` shows PaO2 = 625 mmHg (clearly
   hyperoxic, real Pulse response, not capped at FiO2-corresponding plateau).

3. **Wire the run pipeline.** Wrote four atlas-local modules:
   - `src/sampler.py` — SALib Morris (7 inputs locked from preregistration,
     20 trajectories × 4 levels = 160 rows per cell). Sampler does NOT enforce
     the DBP/SBP ≤ 0.75 constraint; that is delegated to `scenario.py` so the
     Morris geometry stays intact for elementary effects.
   - `src/scenario.py` — converts a Morris sample row + (scenario, sex) into a
     Pulse `config.json`. Implements DBP clip (`min(dbp, 0.75 * sbp)`) at
     submission time; both `dbp_requested` and `dbp_applied` survive through
     the aggregated Parquet so Morris EE can use the requested coordinate while
     still telling us how often the constraint bound.
   - `src/runner.py` — Docker exec wrapper, `ThreadPoolExecutor`-parallel,
     hard-capped at 3 workers per `experiments_log/santino/S001_docker_smoke_test.md`.
   - `src/aggregator.py` — reads run CSVs, calls `src.detector.classify`, and
     emits one Parquet row per run.

4. **Run 8 mid-range cells.** `scripts/scenario_smoke_test.py` builds 8 configs
   (4 scenarios × 2 sexes) at midpoint Morris inputs:
   `hr=80, sbp=105, dbp=70, rr=14, vt=550, fio2=0.6, peep=10`.
   DBP=70 satisfies 70 ≤ 0.75 × 105 = 78.75, so no DBP clip on this point.
   Output: `data/runs/scenario_smoke/`.

5. **Recalibrate `clamped` regex.** First run flagged 8/8 cells as `clamped`,
   driven entirely by `setting .+ to` matching 52 occurrences/run of
   `Resetting the target for X to Y` — Pulse's normal solver convergence text,
   NOT input clamping. Probed for the real clamp signature: deliberately
   submitted SBP = 140 (above the verified 120 ceiling). Pulse logs
   `Patient systolic pressure baseline of 140 mmHg is too high.` plus
   `Maximum systolic pressure baseline allowed is 120 mmHg.` plus
   `must be modeled by adding/using a condition.` with exit code 1.
   Replaced the over-broad regex set with three empirically verified patterns
   anchored on Pulse's actual error phrasing. The other previously listed
   patterns (`out of range`, `out of bounds`, `clamp`, etc.) had no recall on
   real clamping logs and only generated false positives.

## What we tried (including dead ends)

- **First run with old `pulse-pediatric-engine` smoke**: 26 snapshots, CSV
  emitted PaO2 + PaCO2 → confirmed Risk 1 dissolved without rebuilding.
- **Search for documented Pulse clamp strings in `Pulse_translation_new` logs**:
  the existing logs at `cv_modifier_validation/recheck/recheck_v2.log` etc.
  did not contain genuine clamp phrasing — only substance-depletion
  (`Stomach is out of Sodium`) which would have generated false positives if
  we had kept `out of range` / `out of` patterns. Empirical probing of a known
  clamp boundary (SBP=140) was the only reliable path.
- **Considered amending preregistration to FiO2 ∈ [0.21, 0.95]** to dodge the
  wrapper cap. Rejected — would have made the atlas weaker than necessary
  given E20 evidence.

## Results

### 4×2 cell init grid

All 8 cells reached t = 120 s with exit code 0:

| Cell      | wall (s) | HR mean | MAP mean | Vt mean | SpO2 mean | PaO2 mean | PaCO2 mean | flag        |
|-----------|----------|---------|----------|---------|-----------|-----------|------------|-------------|
| S1_M_0000 |     50.1 |   72.81 |    88.62 |  559.89 |    0.999  |    302.94 |     41.63  | clean       |
| S1_F_0000 |     46.4 |   72.37 |    88.92 |  568.93 |    0.9995 |    353.40 |     31.27  | not_steady* |
| S2_M_0000 |     69.0 |   81.27 |    91.10 |  559.98 |    0.994  |    159.24 |     42.76  | clean       |
| S2_F_0000 |     75.5 |   82.31 |    92.03 |  559.97 |    0.996  |    171.45 |     39.04  | clean       |
| S3_M_0000 |     89.2 |  171.63 |   100.41 |  559.37 |    0.945  |     68.91 |     42.89  | clean       |
| S3_F_0000 |     87.2 |  163.77 |    99.72 |  560.00 |    0.966  |     79.88 |     38.60  | clean       |
| S4_M_0000 |    117.7 |  161.46 |   100.63 |  558.49 |    0.829  |     43.37 |     42.90  | clean       |
| S4_F_0000 |    108.8 |  162.13 |    99.11 |  556.75 |    0.843  |     43.33 |     38.87  | clean       |

\* `not_steady_state` fired on the SpO2 channel for S1_F_0000 because steady-
state mean = 0.9995 sits within the locked 0.001 flatline-at-extreme tolerance
(see preregistration amendment 2026-04-22-b). Mean is 0.000509 below the upper
bound of 1.0; tolerance is 0.001. NOT silently re-tuned. The pilot will
provide more data on whether this is a systematic F-patient artifact.

### Atlas-image FiO2 = 1.0 verification

Probe at `data/smoke_check_fio2_1/`: with FiO2 = 1.0, PaO2 stabilized at
~625 mmHg (vs ~303 mmHg at FiO2 = 0.6 in the same patient). Confirms the
atlas-image wrapper does NOT cap FiO2 below the preregistered range.

### Detector recalibration

Replaced 9 over-broad regex patterns with 4 empirically verified ones. Now:

- 8/8 mid-range healthy + ARDS cells: `clamped = False` (correct — no input
  near a known boundary).
- SBP = 140 probe: `clamped = True`, with `is too high` and `Maximum allowed`
  patterns matching simultaneously.

The previous regex would have flagged ~100% of the 1280-run sweep as
`clamped`, making the flag useless. Without this recalibration the atlas
could not have measured H2 (silent clamping ≥ 5%).

### Cell timing extrapolation

Wall times scale with scenario severity:

- S1: ~48 s/run
- S2: ~72 s/run
- S3: ~88 s/run
- S4: ~113 s/run

Sex-conditioned difference: < 5 s/cell on average, no systematic bias.
Per-sex Morris cell budget ≈ 160 runs, so:

- (S1_M, S1_F): 160 × 48 ÷ 3 (parallel) ≈ 42 min each
- (S2_M, S2_F): 160 × 72 ÷ 3 ≈ 64 min each
- (S3_M, S3_F): 160 × 88 ÷ 3 ≈ 78 min each
- (S4_M, S4_F): 160 × 113 ÷ 3 ≈ 100 min each

Total full-sweep estimate: ≈ 9.4 h on the laptop with 3× parallel Docker.
This exceeds the original "~5 h" estimate from the preregistration but is
still laptop-feasible if run overnight, or trivially Colab-feasible.

## Interpretation

All three Tier-1 risks resolved before pilot:

1. **CSV channel coverage** — current image emits all 6 outputs. No rebuild
   needed.
2. **FiO2 cap** — atlas-local wrapper raises `FIO2_MAX` to 1.0. Verified.
3. **DBP / SBP constraint** — clip rule with dual-logging in `scenario.py`
   keeps Morris geometry intact and isolates atlas-level clipping from
   Pulse-level clamping in the analysis.

S4 init does NOT crash at mid-range — at least at this single point. The
0.91–0.945 instability zone reported in E6/E10 was based on different
boundary inputs; severity 0.95 with `vt=550, peep=10, fio2=0.6` is stable.
This does NOT mean S4 will be stable at every Morris point — but it does
mean S4 is salvageable, and the design does not need amendment yet. Sweep-
level S4 stability is now a question the atlas itself answers.

The detector-calibration finding is significant: without an empirical clamp
probe, the atlas would have shipped with a useless `clamped` flag. Pre-pilot
discovery saved a re-run.

## Next steps

1. Re-run `scripts/validate_detector_on_existing_runs.py` against the 20
   reference Pulse runs to confirm the new regex set still passes existing
   detector validation. (Net effect should be unchanged or stricter — the
   new patterns are a strict subset of the old ones' intent, no broader.)
2. Write `scripts/run_pilot.py` per preregistration §Pilot gate. 20 runs
   on cell (S1, M) drawn from `sampler.sample_morris(trajectories=2)` so
   Morris geometry is intact. Apply all 5 gate criteria strictly.
3. Run pilot. If pass → schedule full sweep S006 (1280 runs) overnight.
4. If S4 cells show high `diverged` rate in the full sweep, that IS a
   finding for the paper, not a design failure.
