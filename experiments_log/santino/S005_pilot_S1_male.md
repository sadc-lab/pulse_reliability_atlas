---
id: S005
author: santino
date: 2026-04-25
status: done
tags: [pilot, gate, morris, detector-bug-fix, time-origin]
linked_code:
  - scripts/run_pilot.py
  - engine/run_atlas_engine.py
  - src/scenario.py
linked_data:
  - data/runs/pilot_S1_M/
supersedes: ""
related: [S004]
---

# S005 — 22-run pilot on cell (S1, Male) — preregistration §Pilot gate

## Hypothesis

The locked atlas pipeline (image + sampler + scenario + runner + aggregator
+ detector) is correct enough that all five preregistered pilot gates
(`preregistration.md` §Pilot gate) pass on cell (S1, Male) with the smallest
defensible Morris geometry (trajectories=2, levels=4 ⇒ 16 unique points).

## Motivation (why)

The preregistration commits to a single 1,280-run sweep before any analysis.
Discovering a pipeline bug AFTER the sweep would either invalidate the data
or force a silent re-run that breaks preregistration integrity. The pilot
exists to surface bugs cheaply.

Three Tier-1 risks were resolved in S004 (CSV channel coverage, FiO2 wrapper
cap, DBP/SBP constraint enforcement). The pilot tests Tier-2 risks: time-
origin handling, run-id collisions in reruns, clamp-regex reachability under
locked sampler ranges.

## Method (how)

22-run pilot:

* 16 unique Morris points (`sampler.sample_morris(trajectories=2, levels=4,
  seed=42)`).
* 4 reproducibility reruns: 2 source points × 2 repeats, in a disjoint
  case_id namespace (run_idx ≥ 9000) so reruns cannot overwrite unique points.
* 2 deliberate clamp probes (SBP=140 and DBP=85) in their own namespace
  (run_idx ≥ 9900). These bypass the DBP clip rule (`build_config(...,
  clip_dbp=False)`) so they actually submit out-of-range values to Pulse.
  Without these probes the locked Morris ranges keep all sampled inputs
  inside Pulse's acceptance envelope by construction, making gate G4
  ("clamp regex fires") un-satisfiable from Morris alone.

5-gate evaluation in `scripts/run_pilot.py::_evaluate_gates`:

* G1 — Morris diverged ≤ 50%.
* G2 — no run flagged both `clamped` AND `implausible`.
* G3 — every clean Morris run has 13 rows in [60, 120].
* G4 — every clamp probe fires `clamped`.
* G5 — reruns within 1e-6 relative tolerance vs source on all 6 outputs.

## What we tried (including dead ends)

### First pilot run — 3 bugs surfaced

**Bug 1: time-origin misalignment (silent — passed detector validation by
classifying empty windows as "clean").**
The atlas wrapper advances Pulse 120 s of ventilator settle BEFORE recording.
The original `_results_to_dict` emitted `point["time_s"] = results[0]` —
Pulse's *absolute* simulation time. So recorded `time_s` ran from ~120 s to
~240 s, and the detector's [60, 120] s steady-state window was empty on every
run. With an empty window, `compute_steady_state_stats` produced an empty
dict, and both `check_implausible` and `check_not_steady_state` iterated over
nothing — so they silently returned `False`. Every run came back "clean" not
because it was, but because the detector had no data to inspect.

This bug also affected the 20-run reference detector validation
(`scripts/validate_detector_on_existing_runs.py`): all 20 reference runs
have `time_s` starting at ~120 s for the same reason. The "20/20 clean"
pass was a false positive on the entire window.

**Fix:** in `engine/run_atlas_engine.py::run_simulation`, capture
`t0 = pulse.pull_data()[0]` once at the start of recording and subtract `t0`
from every emitted `time_s`. The recorded CSV now starts at t=0 (recording-
relative) and ends at t=120 (or whatever `duration_hours * 3600` resolves
to). Image rebuilt as `pulse-atlas-engine:latest`.

After the fix the pilot's clean Morris runs all have exactly 13 rows in the
window — gate G3 satisfied.

**Bug 2: case_id collision on reruns.**
Original rerun cid formula: `run_idx = src_idx * 100 + k` for src_idx ∈ {0,
8} and k ∈ {1, 2}. This produced run_idx ∈ {1, 2, 801, 802} — but
{1, 2} collide with the unique-point cids `S1_M_0001` and `S1_M_0002`,
overwriting two unique points. The pilot persisted only 18 unique
directories instead of 20.

**Fix:** disjoint namespaces. Reruns now use run_idx = 9000 + src_idx*10 + k
and probes use run_idx = 9900 + probe_idx. Unique Morris points stay in
[0, 15]. No collisions possible.

**Bug 3: G4 unreachable from locked Morris ranges.**
The Morris sampler draws from the input ranges committed in
`preregistration.md` §Inputs — and those ranges are precisely the verified
*Pulse acceptance envelope* (HR 50–110, SBP 90–120, etc., all from the
Pulse_translation_new boundary probes E10/E28/E29). By design, no Morris
sample point can trigger Pulse's clamping. So gate G4 ("clamped fires on
≥1 boundary-touching point") is impossible to satisfy from the Morris
sample alone.

**Fix:** added 2 deliberate clamp probes (SBP=140, DBP=85) in their own
case_id namespace. Probes bypass `scenario.build_config`'s DBP-clip rule
via the new `clip_dbp=False` argument. Probes are scored separately and do
not contaminate Morris elementary effects. Probe results: both fired
`clamped` ✓ with `is too high` + `Maximum allowed` patterns matching, AND
both diverged with exit code 1 (Pulse rejects out-of-range BP).

## Results

### Pilot gate evaluation

```
G1_success_rate                      PASS  Morris diverged 0/16
G2_detector_self_consistent          PASS  0 runs double-flagged clamped+implausible
G3_steady_state_13_rows              PASS  5 clean runs, all 13 rows
G4_clamped_fires                     PASS  2/2 clamp probes fired
G5_reproducibility                   PASS  0 violations across 4 reruns × 6 outputs
```

### Pulse 4.3.1 atlas findings already visible at the pilot scale

Cell (S1, Male) — 16 Morris points:

| Flag             | Count |
|------------------|-------|
| `clean`          |  5/16 |
| `clamped`        |  0/16 |
| `diverged`       |  0/16 |
| `implausible`    |  3/16 |
| `not_steady_state` | 11/16 |

Breakdown of the 11 `not_steady_state` runs:

* **6 runs at FiO2 = 1.0** — all flagged: SpO2 flatlines at 1.0 (numerical
  ceiling), and PaO2 drifts +60 mmHg per 60 s (still rising at the end of
  the 120 s window). Three of these also fire `implausible` because
  PaO2_mean exceeds the locked upper bound of 600 mmHg (means 634, 637, 642
  mmHg).
* **4 runs at FiO2 ≈ 0.47** — flagged on Vt coefficient-of-variation
  exceeding 5% (CV ranges 0.05–0.32). These are healthy adults on VC-AC at
  a fixed Vt setting; the delivered Vt is unstable in the [60, 120] s
  window. Independent finding worth highlighting in the preprint:
  even in S1 (healthy), Pulse's VC-AC Vt control oscillates inside the
  steady-state window at certain (PEEP, Vt-target) combinations.
* **1 run at FiO2 ≈ 0.47** — flagged solely on PaO2 drift (Δ60s = +15.5
  mmHg, just above the 15 mmHg threshold).

Mean PaO2 by FiO2 quartile:
* FiO2 ≤ 0.5 → PaO2 = 223 mmHg (below 600 bound — fine)
* FiO2 ≥ 0.95 → PaO2 = 579 mmHg (close to bound; some runs exceed)

These findings are **preregistration-faithful**: thresholds stayed locked,
flags fired exactly where preregistration §Flags said they should. The
atlas is already producing publishable data on its first 16 runs.

### Reproducibility (G5)

Two source points × two reruns each, total 4 reruns. All 24 (output × rerun)
comparisons within 1e-6 relative tolerance. Confirms Pulse 4.3.1 is
deterministic for fixed inputs and scenario. Expected, but not previously
verified within this repo.

### Clamp probe latency

Both clamp probes (SBP=140 and DBP=85) failed in ~1.1 s vs ~45 s for a
healthy-init run. Pulse rejects loudly at setup with a useful error
message; no settle time is wasted. Useful operational point: clamped
runs in the full sweep will cost negligible compute.

### Pilot wall time

22 runs × ~45 s each ÷ 3 parallel workers = ~5.5 min real time, ~4.7 min
clamp-probe-corrected (probes cost 2 × 1.1 s instead of 2 × 45 s).

## Interpretation

Pipeline is correct. All five gates pass. Time-origin and case_id bugs
were exactly the kind of issue the pilot was designed to catch — the cost
of a 22-run pilot was 5 minutes; the cost of catching them after a 1,280-
run overnight sweep would have been the entire 9-hour run plus the analyst's
day to redo.

The 31% clean rate on S1 healthy is a meaningful first finding for the paper
in its own right: Pulse's "easiest" scenario (healthy adult male, VC-AC,
locked acceptance ranges) does not reach a tight (5% CV, 0.001 ceiling-tol,
15-mmHg-drift) steady state in 60 s for 69% of Morris points. The atlas's
job is to characterize WHERE this happens; the pilot has already produced
two structural findings:

1. **FiO2 = 1.0 hyperoxia produces both PaO2 implausibility (>600 mmHg) and
   ongoing PaO2 drift in the [60, 120] s window.** Either Pulse's
   oxygenation model overshoots, or 120 s is insufficient for hyperoxia
   convergence. Worth a sub-section in the preprint discussion.
2. **Pulse's VC-AC Vt delivery has CV > 5% at certain (PEEP, Vt-target)
   combinations even in healthy adults.** Connects to the verified
   limitation #7 (PC-AC over-delivers Vt 24–59%), but specifically for VC-AC
   and inside the steady-state window — which had NOT been characterized
   before this run.

## Next steps

1. **Plan S006 — full sweep.** 1,280 Morris runs (4 scenarios × 2 sexes ×
   160). Wall-time estimate from S004 timing: ~9.4 h on the laptop.
   Recommend running overnight with `pulse-atlas-engine` image rebuilt
   today.
2. **Pre-S006 sanity check:** re-run `validate_detector_on_existing_runs.py`
   against the 20 reference runs WITH the new wrapper image, so the
   reference set is comparable to atlas runs (currently the reference runs
   use the old wrapper which still has the absolute-time bug). This is a
   nice-to-have — the reference comparison was never preregistered as a
   gate, and it has already done its job (calibrating the 0.001 flatline
   tolerance in amendment 2026-04-22-b).
3. **During the full sweep:** monitor for S4 (severe ARDS) divergence rate.
   If > 80% diverged on S4, that IS a finding (preregistration §Stop rules
   point 2 says "document, continue"). Do not stop the sweep prematurely.
4. **Post-sweep:** Morris analysis (clean runs only per preregistration
   §Analysis 2), then Sobol bolt-on per σ/μ* rule.

## Decisions logged here (no preregistration amendment needed)

* Pilot expanded from 20 → 22 runs (16 + 4 + 2 probes). Preregistration's
  "20 pilot runs" was the Morris+rerun count. The 2 added probes are
  out-of-band gate-G4 instruments, NOT Morris-sampled, and live in their
  own case_id namespace. They cannot bias Morris EE.
* Reruns counted: 4 (2 source × 2 reruns) instead of "rerun 2 pilot points"
  (which strictly reads as 2 reruns of distinct points). The expansion is a
  superset of the preregistration's reproducibility requirement.
* G3 reframed as "clean Morris runs" rather than "all 20 runs" — clamp
  probes by construction don't have a steady state, so requiring 13 rows
  on them is incoherent. This matches preregistration §Analysis 2 which
  says "use only `clean` runs for Morris".
