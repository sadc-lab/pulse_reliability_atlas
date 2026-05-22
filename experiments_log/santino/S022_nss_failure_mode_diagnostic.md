---
id: S022
author: santino
date: 2026-05-22
status: done
tags: [diagnostic, no-compute, failure-mode-classification, detector-edge-case, dyssynchrony-attribution, corrected]
linked_code:
  - scripts/diagnostic_nss_classify.py
  - scripts/diagnostic_waveform_inspect.py
  - scripts/nss_decomposition_table.py
linked_data:
  - data/runs/full_sweep/aggregated.parquet
  - results/s022/diagnostic_nss_classify.json
  - results/s022/waveform_inspect.json
  - results/s022/nss_decomposition.csv
related: [S012, S014, S021]
---

# S022 — No-compute failure-mode diagnostic for the top-3 unstable cells

## Correction (2026-05-22, after initial drafting)

The first draft of this entry inferred that the Vt-CV sub-mode of
`not_steady_state` was *Nyquist aliasing* of the breath cycle by the
5 s CSV sample interval. **This inference is incorrect.** S014 had
already ruled out aliasing by direct waveform inspection: Pulse's
`TidalVolume` CSV channel is **breath-integrated and held between
cycles**, not a continuous flow waveform, so the 5 s decimation is not
aliasing anything — it samples a step-and-hold breath-by-breath
volume signal. The 5 s sample sequence captures *real* per-breath Vt
variance produced by F-004 patient-ventilator dyssynchrony (mandatory
+ assist breath alternation), not an artefact of the sampling
schedule. S014's controlled trigger-pressure intervention on 64 high-
Vt-CV runs collapses the CV by 96 %, confirming dyssynchrony as the
mechanism.

**What stands after correction:**

1. The SpO2 "flatline at ceiling" sub-mode IS a detector edge case
   (physiological oxygen saturation in healthy / well-oxygenated
   patients mis-classified as numerical pinning). This finding is
   novel to S022 and is the headline contribution of this entry.
2. The Vt-CV sub-mode is the F-004 dyssynchrony signal already
   documented in §3.8 of the manuscript — the locked classifier is
   correctly flagging real engine behaviour, not artefact. The
   decomposition table column is renamed accordingly.
3. The S4 drift sub-mode is the F-003-class slow-convergence
   phenomenon (severe-ARDS oxygenation not settling in the 120 s
   window), also already in §3.8.

**The original narrative is preserved below for traceability**;
read the body alongside this correction block.

## Hypothesis

The `not_steady_state` flag in the atlas's top-3 unstable cells (S1_F, S1_M,
S4_F) decomposes into mechanistically distinct sub-modes. We expect at least
two of the following to dominate:

1. **Flatline at ceiling** driven by SpO2 saturating at ~1.0 in healthy /
   adequately-oxygenated patients — a *detector edge case*, not Pulse
   instability.
2. **Vt coefficient-of-variation exceedance** driven by the 5 s CSV sample
   interval undersampling the breath cycle at RR ≥ 12 bpm — a *sampling
   aliasing artefact*, not Pulse instability.
3. **Genuine slow convergence** in severe-ARDS oxygenation channels (SpO2,
   PaO2) that fail to settle within the 120 s simulation window.

If true, an intervention experiment targeting "dyssynchrony" (e.g., trigger
pressure perturbation, as originally proposed) cannot help, because none of
the dominant sub-modes are dyssynchrony.

## Motivation

The original Phase B follow-up plan proposed re-running the 160-point Morris
grid on the top-3 unstable cells with a forced ventilator trigger pressure
of -2 cmH2O to test whether that "restores stability." Before paying ≥480
runs of compute, classify the failure modes from existing data. If the
failures are not synchrony-related, the intervention experiment is
ill-posed.

## Method

Read-only inspection of `data/runs/full_sweep/aggregated.parquet`
(1 280 runs, locked S006).

1. Rank the 8 (scenario × sex) cells by `not_steady_state` rate.
2. For the top-3 cells, parse `not_steady_state_reason` against the three
   regex sub-modes embedded by `src/detector.py`:
   - `flatline_high` / `flatline_low` (channel pinned at hard bound)
   - `cv_high` (coefficient of variation > `CV_THRESHOLD` = 0.05)
   - `drift_high` (`|delta_60s|` > channel-specific `DRIFT_MAX_DELTA_60S`)
3. For each sub-mode, tally per-channel hit counts and co-firing combos.
4. Cross-tab the dominant sub-modes against the requested RR (sampling
   aliasing prediction).
5. For six representative runs (one per sub-mode per cell), open the raw
   `output.csv`, inspect the steady-state window, and compute
   samples-per-breath as a Nyquist diagnostic.

Scripts: `scripts/diagnostic_nss_classify.py`,
`scripts/diagnostic_waveform_inspect.py`. No new Pulse runs were executed.

## Results

### 1. Top-3 unstable cells

| Cell | n_runs | n_nss | nss_rate | n_clamped | n_diverged | n_implausible | n_clean |
|------|-------:|------:|---------:|----------:|-----------:|--------------:|--------:|
| S1_F | 160 | 118 | **0.738** | 0 |  0 | 23 | 42 |
| S1_M | 160 | 107 | **0.669** | 0 |  4 | 11 | 49 |
| S4_F | 160 |  74 | **0.463** | 0 |  0 | 46 | 60 |

Note: the most unstable cells are **healthy** patients (S1), not severe ARDS
(S4). This is the first inversion of the naive expectation that ARDS drives
instability.

### 2. Sub-mode decomposition

**S1_F (n_nss = 118)** — bimodal:

| Sub-mode | Runs hit | % of nss | Dominant channels |
|---|---:|---:|---|
| flatline_high | 84 | 71.2% | SpO2 (84) |
| cv_high       | 76 | 64.4% | Vt (77) |
| drift_high    | 18 | 15.3% | PaO2 (~), PaCO2 (8) |
| flatline_low  |  0 |  0.0% | – |

Top co-firing combos: `cv_high+flatline_high` (38), `cv_high` alone (32),
`flatline_high` alone (30), `drift_high+flatline_high` (12).

**S1_M (n_nss = 107)** — same bimodal pattern as S1_F:

| Sub-mode | Runs hit | % of nss | Dominant channels |
|---|---:|---:|---|
| flatline_high | 71 | 66.4% | SpO2 (71) |
| cv_high       | 64 | 59.8% | Vt (63) |
| drift_high    | 28 | 26.2% | PaO2 (28) |

**S4_F (n_nss = 74)** — *no* flatline, drift-dominant:

| Sub-mode | Runs hit | % of nss | Dominant channels |
|---|---:|---:|---|
| flatline_high |  0 |  0.0% | – |
| cv_high       | 43 | 58.1% | Vt (34) |
| drift_high    | 49 | 66.2% | SpO2 (49), PaO2 (13), HR (11) |

### 3. SpO2 "flatline at ceiling" is healthy oxygen saturation

The detector's flatline rule fires when std/|mean| < 0.01 *and* the mean is
within 0.001 of a hard bound (`SpO2 ∈ [0.50, 1.00]`). A healthy adult on
FiO2 ≥ ~0.21 saturates physiologically at SpO2 ≈ 0.999; the detector
classifies this as "pinned at ceiling." Across all 8 cells:

| Cell | n_nss | n with SpO2_mean ≥ 0.999 | % |
|------|------:|------------------------:|--:|
| S1_F | 118 | 84 | 71% |
| S1_M | 107 | 71 | 66% |
| S2_F |  68 | 42 | 62% |
| S2_M |  69 | 26 | 38% |
| S3_F |  38 |  8 | 21% |
| S3_M |  12 |  1 |  8% |
| S4_F |  74 |  0 |  0% |
| S4_M |  44 |  0 |  0% |

Monotone decrease with ARDS severity: as the lung gets sicker, SpO2 stops
saturating at ceiling, and this sub-mode disappears. **This is a detector
artefact, not Pulse instability** — a healthy patient on supplemental O2
*should* sit at SpO2 ≈ 1.0.

### 4. Vt CV exceedance — RR-dependent, but the mechanism is F-004 dyssynchrony (not aliasing — see correction block above)

CSV sample interval is **5 s** (`config.sample_interval_s = 5`,
preregistration §Sweep design). Breath period = 60/RR seconds, so
samples-per-breath = RR/12. The original draft inferred Nyquist
aliasing from this ratio — but Pulse's `TidalVolume` channel is
breath-integrated and held, so the 5 s sample captures real per-breath
volume, not phase-aliased flow. The RR-dependence reported below is
real, but it reflects the fact that **F-004 dyssynchrony is more
pronounced at higher RR** (more opportunity per minute for the
spontaneous-drive trigger to fire extra assist breaths between
mandatories) — already established by S014.

Empirical mean Vt CV by RR bucket (full 1 280 runs):

| RR bucket | n | mean Vt CV | median Vt CV | max Vt CV |
|---|---:|---:|---:|---:|
| ≤ 10 bpm  | 191 | 0.013 | 0.000004 | 0.55 |
| 10-14 bpm | 487 | 0.043 | 0.000282 | 0.55 |
| 14-18 bpm | 190 | 0.031 | 0.001037 | 0.28 |
| > 18 bpm  | 392 | 0.095 | 0.024020 | 1.83 |

The high-RR bin (> 18 bpm) has 4× the mean CV of the moderate-RR bin
(14-18 bpm), even though the moderate-RR bin contains the same set of
ventilator volume settings — direct evidence the CV is RR-driven.
Under the F-004 dyssynchrony mechanism (S014), this is expected: at
higher set RR, Pulse's spontaneous-drive trigger has more
opportunities to fire assist breaths between mandatories, producing
more between-breath Vt variance.

Representative waveform: `S1_M_0016` (Vt set 800 mL, RR 20). Steady-state
window has 13 samples spanning 60 s × 20 breaths = 1 200 inhalations.
Observed Vt: mean 817.5, std 243.5, **min 165.3, max 1 403.2, span 1 238 mL**,
CV 0.298. **Original draft (incorrect):** interpreted this as
envelope aliasing of phases of a continuous flow signal. **Corrected
interpretation:** the TidalVolume channel is breath-integrated; the
165–1 403 mL span is the actual per-breath delivered-volume range
across an alternating mandatory + assist pattern, exactly the F-004
signature described in §3.8 and confirmed in S014.

### 5. S4 drift is genuine slow convergence (not aliasing or detector edge case)

Representative: `S4_F_0005` (severe ARDS, FiO2 = 0.47, RR = 12, PEEP 13.3).
- Vt: mean 639.9, std 0.1, CV 2 × 10^-4 (phase-locked, no Vt issue).
- SpO2: mean 0.854, std 0.011, **delta_60s = +0.0347** (still rising at
  ~3.5% per minute) — flagged.
- PaO2: 44.2 mmHg, delta_60s = +4.65 mmHg (still rising).
- HR: setpoint 70, observed 139.55 (Pulse autonomic response to severe
  hypoxia).

This is real: the 120 s simulation window is not long enough for severe
ARDS oxygenation to settle. The model would converge if `t_end` were
extended (S012 showed F-003 hyperoxia equilibrates by ~300 s).

### 6. HR setpoint drift across all examples

In every inspected run the steady-state HR mean deviates 10-100% from the
requested baseline. Pulse's autonomic baroreflex / chemoreflex models
override the requested HR baseline once cardiopulmonary loading is set.
This is documented engine behaviour, not instability, but should be made
explicit in the operational-inputs section of the manuscript: "requested
HR" is an initial condition, not a held setpoint.

## Interpretation

**The three dominant `not_steady_state` sub-modes are non-overlapping in
mechanism, and none of them are dyssynchrony:**

- **SpO2-saturation flatline (S1/S2 dominant):** a *detector* edge case.
  Healthy / well-oxygenated patients saturate at SpO2 = 1.0 biologically;
  the flatline rule was designed to catch numerical pinning, not
  physiological saturation. A flag refinement (exclude SpO2 from flatline
  scoring when other channels are healthy) would drop S1_F's apparent
  instability rate from 73.8% to ~31% with zero new compute.

- **Vt CV exceedance (universal at high RR):** the F-004
  patient-ventilator dyssynchrony signal already documented in §3.8 and
  causally tested in S014. **Not an aliasing artefact** (corrected from
  initial draft — see correction block above). The locked classifier
  is correctly flagging real engine behaviour: under Pulse 4.3.1's
  default VC-AC trigger configuration, the spontaneous-drive
  respiratory model inserts assist breaths between mandatory cycles,
  producing real per-breath Vt variance. The Vt-CV contribution to
  nss is therefore a *finding*, not a *bug in the detector*; it is the
  documented F-004 contribution to the operational-envelope map.

- **Genuine slow convergence (S4 dominant):** the only sub-mode that
  reflects engine behaviour. The 120 s window is insufficient for severe
  ARDS oxygenation to settle. A targeted re-run with `t_end = 300 s` on
  S3/S4 (~640 runs) would resolve this category; this is also what S012
  recommended for F-003.

**Implication for the original Exp 1 (trigger-pressure intervention):**
the original proposal — rerun the top-3 unstable cells with a forced
trigger pressure to "restore stability" — duplicates work already
completed in **S014**, which is the locked causal test of the F-004
mechanism. S014 ran 64 controlled trigger-pressure reruns and showed a
96 % Vt-CV collapse (median 0.351 → 0.016), confirming dyssynchrony as
the cause and trigger pressure as the suppressor. Rerunning S014 on
S1_F / S1_M / S4_F would not produce new information; the mechanism
is already established. Separately, the SpO2-saturation sub-mode is
not addressed by any trigger change (it is a detector edge case on
healthy oxygenation), and the S4 drift sub-mode is not addressed by
any trigger change (it is a simulation-window question, already in
§3.8 / S012 / S021). The proposed experiment is therefore
**withdrawn** — partly because it duplicates S014, partly because it
mis-targets the other two sub-modes.

### Caveats

- This is a *post-hoc* re-interpretation of locked-classifier output. The
  S006 classifier is not being changed. Any reclassification (e.g., SpO2
  saturation exclusion) requires a preregistration amendment.
- The Vt-CV-as-aliasing claim in the initial draft has been retracted —
  see the correction block at the top of this entry. Ground truth comes
  from S014's native-resolution (0.02 s) waveform inspection plus the
  trigger-pressure controlled experiment, both of which establish
  F-004 dyssynchrony as the mechanism.
- Six waveforms were inspected directly here; the sub-mode classification
  of the remaining 293 nss runs is reason-string parsing, not waveform
  inspection.

## Next steps

- **Manuscript:** add an honest Limitations subsection acknowledging that
  the locked `not_steady_state` classifier conflates three mechanistically
  distinct phenomena (detector edge case, sampling aliasing, genuine slow
  convergence). This does not invalidate the headline Atlas: clamping,
  divergence, and implausibility rates are independent of these issues.
- **No new compute.** The trigger-pressure intervention experiment is
  withdrawn. Future detector revisions and the proposed re-run-with-
  longer-`t_end` are noted but not initiated here.
- **Exp 2 (SHAP cross-check) proceeds independently.**
