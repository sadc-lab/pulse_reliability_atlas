# Interim findings — for paper traceability

**Status:** working draft, updated as experiments complete. Each finding
points to its source experiment log entry. The preprint will pull from
this file once the full sweep is analysed.

**Locked context:** 7 inputs, 4 scenarios, 2 sexes, VC-AC, 120 s sims,
13-point steady-state window in [60, 120] s. See
[`../preregistration.md`](../preregistration.md) for the full design.

---

## Findings stream — chronological

### F-001 — `pulse-pediatric-engine` wrapper silently caps FiO2 at 0.95

**Status:** addressed (atlas-local image built without the cap).
**Source:** [S004](../experiments_log/santino/S004_scenario_smoke_and_atlas_image.md).

The upstream Pulse_translation_new wrapper hardcodes `FIO2_MAX = 0.95`. PhD
experiment E20 (April 2026, 9-run probe) already verified Pulse 4.3.1
accepts FiO2 = 1.0 cleanly, so the wrapper cap is a residual conservative
guard. Atlas raises this to 1.0 in `engine/run_atlas_engine.py`. Without the
fix, ~17% of preregistered Morris samples (FiO2 > 0.95) would have been
silently capped at a layer ABOVE Pulse, polluting the atlas's
silent-clamping characterization with a wrapper artifact. **Implication for
the paper's methods section:** all reported clamping is Pulse-engine-
attributed, not wrapper-attributed.

### F-002 — Detector validation script gave silent false positives via empty steady-state windows

**Status:** addressed (time-origin fix in wrapper, regex empirically
recalibrated). **Source:** [S005](../experiments_log/santino/S005_pilot_S1_male.md).

The atlas wrapper advances Pulse 120 s of ventilator-settle BEFORE recording.
Original `_results_to_dict` emitted Pulse's *absolute* simulation time, so
recorded `time_s` ran from ~120 s to ~240 s — and the detector's [60, 120] s
window was empty on every run. Empty stats meant `check_implausible` and
`check_not_steady_state` iterated over nothing and silently returned
`False`. Every run came back "clean" not because it was, but because the
detector had no data to inspect. The same bug affected the 20-run reference
detector validation in `Pulse_translation_new`.

**Fix:** subtract the recording-start time `t0` in
`run_atlas_engine.run_simulation`. Recorded CSV now starts at t=0
recording-relative.

**Independent fix (same experiment):** Pulse log regex calibrated against a
real boundary probe (SBP = 140 → "Patient systolic pressure baseline of 140
mmHg is too high. Maximum systolic pressure baseline allowed is 120 mmHg").
The previous regex set was over-broad (matched solver convergence text
"Resetting the target for X to Y" 52 times per healthy run, false-positive
flagging 100% of the sweep). Replaced with 4 verified patterns; 0/16 false
positives on Morris pilot, 2/2 true positives on clamp probes.

### F-003 — Pulse 4.3.1 produces PaO2 > 600 mmHg at FiO2 = 1.0 on healthy adults

**Status:** observed in pilot (3/16 Morris points at S1, Male).
**Source:** [S005](../experiments_log/santino/S005_pilot_S1_male.md).

At FiO2 = 1.0, healthy adult VC-AC runs reached steady-state PaO2 = 634,
637, 642 mmHg — exceeding the locked physiological upper bound of 600 mmHg
(based on pure-O2 ceiling). All three runs flagged `implausible`. Whether
the hyperoxia overshoot is a Pulse modelling artifact or a tolerance
mismatch is a paper discussion point. The atlas reports the observation
faithfully without changing the bound.

### F-004 — VC-AC delivered Vt has CV > 5% inside the [60, 120] s window for some (PEEP, Vt-target) combinations on HEALTHY adults

**Status:** observed in pilot (4/16 Morris points at S1, Male, FiO2 ≈ 0.47).
**Source:** [S005](../experiments_log/santino/S005_pilot_S1_male.md).

VC-AC is preregistered as the "validated best" mode (per Webb 2023 and the
Pulse validation table). Yet four pilot points show Vt CV ranging 0.05 to
0.32 inside the 60 s steady-state window. Connects to the verified
limitation #7 (PC-AC over-delivers Vt 24–59%) but specifically points the
finger at VC-AC steady-state oscillation, which had not been previously
characterized. To watch in the full sweep: whether the CV > 5% pattern
clusters in particular (PEEP, Vt) corners.

### F-005 — Pulse 4.3.1 is bit-exact deterministic for fixed inputs and scenario

**Status:** verified in pilot. **Source:**
[S005](../experiments_log/santino/S005_pilot_S1_male.md).

4 reruns × 2 source points × 6 outputs = 24 (output, rerun) comparisons.
All within 1e-6 relative tolerance. Justifies sample-once-and-report
analysis — no need for repeated runs at the same input.

### F-006 — S4 (severe ARDS, severity = 0.95) initialises cleanly at mid-range Morris inputs

**Status:** verified in 4 × 2 scenario smoke (S004); to be re-tested across
the full sweep. **Source:**
[S004](../experiments_log/santino/S004_scenario_smoke_and_atlas_image.md).

Pre-pilot concern: `Pulse_translation_new/experiments_log.md` documents an
ARDS solver instability zone at impairment 0.91–0.945. Severity 0.95 sits
above this zone. Preregistration §Scenarios chose 0.95 specifically to be
above the instability — but if every S4 init diverged regardless, the
preregistered design would have needed amendment.

In the 4 × 2 scenario smoke: both S4 cells (M and F) initialised at mid-range
inputs (HR=80, SBP=105, DBP=70, RR=14, Vt=550, FiO2=0.6, PEEP=10) with mean
PaO2 ≈ 43 mmHg, SpO2 ≈ 0.83 — physiologically appropriate severe-hypoxemia
response. Sweep-level S4 stability remains a question the atlas itself
answers in S006.

---

## Findings stream — full sweep (S006, 1,280 runs)

### F-007 — H1 (skewed sensitivity) supported, 48 / 48 cell × output combinations

**Status:** confirmed on the full sweep.
**Source:** [S006](../experiments_log/santino/S006_full_morris_sweep.md),
artifact `results/h1_top3_fraction.csv`.

Every cell × output combination has ≥ 50 % of its summed μ\* concentrated
in its top-3 ranked inputs. Median top-3 fraction 0.928, range 0.658 –
0.998. Pulse 4.3.1 is, in the operational region we sampled, dominated
by a small handful of inputs per output. Cardiovascular outputs (HR,
MAP) are dominated by their direct cardio baselines; gas-exchange
outputs (SpO2, PaO2, PaCO2) by ventilator settings. Physiologically
sensible.

### F-008 — H2 (silent clamping ≥ 5 %) NOT supported; Pulse rejects loudly, not silently

**Status:** confirmed null on the full sweep.
**Source:** [S006](../experiments_log/santino/S006_full_morris_sweep.md),
flag column `clamped` of `data/runs/full_sweep/aggregated.parquet`.

**0 / 1,280 Morris runs fired the `clamped` regex.** The locked input
ranges (derived from the verified Pulse acceptance envelope per E10 /
E28 / E29) keep every sampled point inside the engine's input
acceptance. The deliberate clamp probes in S005 separately verified
that Pulse rejects out-of-envelope inputs *loudly* with explicit
`[ERROR]` log lines and exit code 1.

**Implication:** the previous verbal description of "BP clamping
silently rejected at setup" (CLAUDE.md verified-limitations item 2) is
revised. Pulse's setup-time rejection is observable from logs, not
silent. We recommend updating the upstream limitation list.

### F-009 — H3 (solver divergence) supported with sex stratification

**Status:** confirmed; sex stratification is unanticipated.
**Source:** [S006](../experiments_log/santino/S006_full_morris_sweep.md),
flag column `diverged`.

20 / 1,280 (1.6 %) Morris runs diverged. Per-cell:

| Cell  | diverged |
|-------|----------|
| S1_M  | 4        |
| S2_M  | 4        |
| S3_M  | 4        |
| S4_M  | 8        |
| S1_F  | 0        |
| S2_F  | 0        |
| S3_F  | 0        |
| S4_F  | 0        |

**All 20 are male.** Same 160 Morris input points in both sexes; only
the patient demographics + sex flag differ. Specifying the male
standard surrogate makes Pulse roughly **5× more likely** to push into
divergence at any given Morris point inside the locked envelope. First
quantitative sex-specific reliability finding for Pulse 4.3.1.

### F-010 — H4 (sex-specific reliability) supported on magnitudes; rankings preserved

**Status:** confirmed on the full sweep.
**Source:** [S006](../experiments_log/santino/S006_full_morris_sweep.md),
artifacts `results/wasserstein_male_vs_female.csv` and
`results/spearman_mu_star.csv`.

* **Wasserstein distance M-vs-F is largest for Vt (13.8 – 36.3 mL across
  scenarios) and PaO2 (4.6 – 16.1 mmHg)** — the two outputs most
  sensitive to body composition (Vt directly via predicted Vt from body
  weight, PaO2 indirectly via alveolar volume).
* **Spearman ρ on M-vs-F μ\* rankings is 0.75 – 1.00** in S2 / S3 (the
  cells where every input has clean EE pairs in both sexes). Input
  importance *ordering* is preserved across sex; *effect magnitudes*
  differ.
* S1 and S4_F are not Spearman-computable because FiO2 has zero clean
  EE pairs in those cells (see F-003 for the cause).

The atlas thus reports both convergent (input ranking) and divergent
(effect magnitude, divergence rate, implausibility rate) sex effects.

### F-011 — F-003 confirmed at scale: 34 implausible runs at FiO2 ≥ 0.95 with PaO2 > 600 mmHg

**Status:** confirmed and quantified.
**Source:** [S006](../experiments_log/santino/S006_full_morris_sweep.md),
implausible flag analysis.

Of 126 implausibly-flagged runs across the full sweep, 34 have
PaO2_mean > 600 mmHg and 91 % of those are at FiO2 ≥ 0.95. Spot checks
of raw CSVs confirm PaO2 is still drifting upward at t = 120 s in these
runs. The hyperoxia-overshoot finding scales cleanly from pilot (3 / 16)
to full sweep.

### F-012 — F-004 confirmed at scale: 20.6 % of runs fail VC-AC steady-state in [60, 120] s

**Status:** confirmed and quantified.
**Source:** [S006](../experiments_log/santino/S006_full_morris_sweep.md),
not_steady_state reason analysis.

264 / 1,280 (20.6 %) Morris runs are flagged `not_steady_state`
specifically on the Vt CV > 5 % criterion. This includes runs in S1
(healthy adults at standard ventilator settings). Pulse's preferred
ventilator mode (VC-AC, validated in Webb 2023) does not produce a
steady delivered tidal volume in 60 s for one in five sampled (PEEP,
Vt, RR) combinations. Operationally: users should report VC-AC Vt as
mean ± CV over a window, not as a steady-state point estimate.

### F-013 — Sobol bolt-on would refine ~ 50 % of top-ranked inputs

**Status:** evaluated on the full sweep (decision deferred — not yet
executed). **Source:**
[S006](../experiments_log/santino/S006_full_morris_sweep.md), artifact
`results/sobol_promotion.csv`.

Of 144 (cell × output × top-3 input) combinations, the σ / μ\* ratio
classifies 72 as `promote` (≥ 0.6), 55 as `skip` (≤ 0.4), and 17 as
`gray`. A targeted Sobol analysis on the 72 promoted entries would
yield first-order and total-order indices for the inputs whose Morris
μ\* hides nonlinearity / interactions — particularly on gas-exchange
channels in S2 – S4. Cost: ~ 64 × (2 × k + 2) base samples per
promoted combo, budget ≈ 3,600 additional Pulse runs (~ 13 h compute
at 2 parallel workers).

We defer the Sobol bolt-on pending reviewer interest. The atlas's
core message is already complete with the Morris results.

### Sub-questions for the discussion section

- Does the FiO2 = 1.0 hyperoxia overshoot (F-003) cluster only in S1, or
  does it persist into ARDS scenarios where the lung-impairment fraction
  should attenuate alveolar PO2?
- Does the VC-AC Vt instability (F-004) correlate with specific PEEP
  values, or with the Vt-target itself? The Morris EE structure will
  isolate this directly.
- Is the male-vs-female reliability difference (H4) most pronounced for
  gas-exchange channels (where alveolar volume per kg differs most by
  sex) or cardiovascular channels?

---

## How this file is used

- **During experiments:** every new experiment that produces a publishable
  observation appends an `F-NNN` entry pointing back to the experiment log.
- **Pre-preprint:** the Findings sections are folded into the
  Results / Discussion of the paper, with each `F-NNN` becoming one
  paragraph or one sub-figure.
- **Post-preprint:** the entries become the natural references for any
  follow-up comments, reviewer responses, or replication notes.

The discipline: nothing goes into the preprint that doesn't have an `F-NNN`
entry here, and nothing in this file lacks a link back to a logged
experiment. That is the traceability requirement.
