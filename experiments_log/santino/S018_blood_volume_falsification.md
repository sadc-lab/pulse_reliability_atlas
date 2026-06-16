---
id: S018
author: santino
date: 2026-05-13
status: done
tags: [mechanism-test, falsification, divergence, blood-volume, sex-stratification, phase-b]
linked_code: [engine/run_atlas_engine.py, scripts/s018_bv_falsification.py]
linked_data: [data/runs/s018_blood_volume/]
supersedes: ""
related: [S006, S008, S011, S017]
---

# S018 — Blood-volume mechanism falsification test (Phase B item B2): dose-response bracket on the 20 originally-diverged male inputs

## Hypothesis (preregistered in §3.5 of the manuscript)

> "Pulse's `SetupPatient.cpp` computes blood-volume baseline as
> `computedBloodVolume_mL = 65.6 × weight_kg^1.02`. For the standard
> male (67.3 kg) this yields ≈ 5,060 mL; for the standard female
> (56.2 kg) ≈ 4,200 mL. [...] The 20 % blood-volume difference is the
> most plausible candidate for the divergence asymmetry: it directly
> enters the cardiovascular circuit's stabilization and shifts the
> operating-point neighborhood between the two sexes. We do not claim
> this is the mechanism — confirming it would require a targeted
> source-level experiment manipulating only blood-volume baseline —
> but it is the falsifiable hypothesis to test in follow-up work."

S018 is that follow-up.

**Prediction:** if the blood-volume baseline is the divergence
mechanism, re-running the 20 originally-diverged male inputs with the
male blood-volume reduced toward the female value should bring the
divergence rate from 20 / 20 down toward 0 / 20. If divergence
persists at 20 / 20 (or near it), blood volume is not the (sole)
mechanism within Pulse's allowed BV range, and the hypothesis is
falsified.

## Motivation (why now)

Phase B item B1 (Cornish cross-mapping, S017) shipped 2026-05-13.
Phase B item B2 is the no-cluster Docker compute test that completes
the §3.5 mechanism discussion. ROADMAP_PHASE_B.md §B2 specifies the
protocol. The mechanism claim in §3.5 is currently the most reviewer-
vulnerable paragraph in the manuscript (a "falsifiable hypothesis we
did not test" is a clear ask); running S018 lets the manuscript move
to either *mechanism confirmed* or *alternative mechanism candidate*
phrasing.

## Method

### Engine wrapper patch

`engine/run_atlas_engine.py` was extended with an optional
`baselines.blood_volume_ml` override path. When present, it is
injected via:

```python
p.get_blood_volume_baseline().set_value(bv_ml, VolumeUnit.mL)
```

before engine initialization. Docker image rebuilt as
`pulse-atlas-engine:bv-override`.

### Smoke test discovery (F-S018-A) — Pulse hard-rejects BV transplants below a per-patient floor

The preregistered first attempt set BV to the female-computed value
(3,996.09 mL — Pulse's own log output on female runs). Pulse rejected
this at setup with:

> `[WARN] Specified patient blood volume baseline of 3996.09 mL differs from computed value of 4802.63 mL. No guarantees of model validity and there is a good chance the patient will not reach a starting homeostatic point.`
>
> `[ERROR] Patient blood volume baseline of 3996.09 mL is too low. Hypovolemia must be modeled by adding/using a condition. Minimum blood volume baseline allowed is 4082.24 mL.`

The male standard surrogate (67.3 kg, 180 cm) has an explicit BV floor
of **4,082.24 mL** below which Pulse exits with code 1 at setup.
The female-computed BV (3,996.09 mL) falls 86.15 mL below this floor.
This is itself a finding (F-S018-A below): the manuscript's "20 %
difference" framing in §3.5 *cannot* be replicated as a one-way
transplant onto the male surrogate — the engine itself enforces a
sex/weight-derived BV floor.

### Revised protocol (after F-S018-A)

Two-point dose-response bracket on the male surrogate:

1. **Floor bracket — BV = 4,082.24 mL** (Pulse's stated floor; 15.0 %
   reduction vs the male default 4,802.63 mL). The strongest BV-only
   reduction Pulse will accept.
2. **Intermediate bracket — BV = 4,400 mL** (~8.4 % reduction;
   roughly halfway between male default and floor).

Total: 20 originally-diverged inputs × 2 brackets = 40 runs. Same
Pulse seed, same atlas image hash chain (`b2e0e807803d` → child
`pulse-atlas-engine:bv-override`), same wrapper code path apart
from the BV-override injection.

### The 20 inputs (manuscript §3.5)

16 shared Morris indices repeated across S1 / S2 / S3 / S4_M (run_idx
0119, 0157, 0158, 0159 × 4 scenarios) plus 4 unique S4_M inputs
(run_idx 0024, 0082, 0137, 0138). All 20 diverged in the original
S006 sweep with `exit_code = 1` and no CSV emitted.

### Classification

Each run was classified by `src.detector` exactly as in S006. The
four flags (clamped / diverged / implausible / not_steady_state) and
the steady-state stats were computed identically.

## Findings

### F-S018-A — Pulse enforces a per-patient blood-volume floor at setup

The male standard surrogate (67.3 kg, 180 cm, age 18, sex Male) has
a hard-enforced BV floor of **4,082.24 mL** at setup. The floor is
emitted as an `[ERROR]` (not `[WARN]`) and yields exit code 1, i.e.
Pulse refuses to initialize. The corresponding `[WARN]` line for
non-fatal BV deviations is emitted whenever the override differs
from the weight-derived computed value, regardless of whether the
override falls within the allowed range.

This finding refines §3.5's mechanism discussion: the "20 % blood-
volume gap" between male and female surrogates is *not* a free
parameter that can be transplanted across sexes on the same body —
the engine's setup logic enforces sex/weight-conditional bounds.
The floor for the female surrogate at 56.2 kg is separately
discoverable (we did not need to discover it for S018 since the
test is on the male model).

### F-S018-B — Mechanism confirmed: blood-volume reduction eliminates the male divergence cluster

> **CORRECTION (2026-06-16).** This finding originally reported **2 / 20** diverged
> at the 4,400 mL bracket and built a "per-input threshold structure" on it. That
> was wrong. The two "divergences" (S4_M_0158, S4_M_0159 — the two slowest runs,
> ~325 s each) were a **classification-time race**: the classifier ran before those
> two finished writing `run_meta.json`, and `aggregator.build_row` defaults a
> missing `run_meta` to `exit_code = 1` → diverged. Both runs in fact completed
> normally (exit 0) and re-classify as **clean**. Confirmed three independent ways:
> the committed `s018_run_index.parquet` records all 20 bracket runs at exit 0; a
> controlled Tier-2 re-run (`scripts/verify_s018_tier2.py`, 80 runs, N = 2, 0 flaky)
> gives bracket 0 / 20 and default 20 / 20; and re-aggregating the now-complete run
> dirs gives the corrected table below. Corrected bracket = **0 / 20**; dose-response
> **20 → 0 → 0**. Independently traced and confirmed by Y. Mamouni. The two
> interpretive paragraphs that rested on the spurious "2" (per-input threshold;
> per-case difference between brackets) are retracted and corrected below.

The corrected dose-response:

| BV (mL)         | Reduction vs male default | Diverged | Implausible | not_steady_state | Clean |
|-----------------|---------------------------|----------|-------------|------------------|-------|
| 4,802.63        | 0 % (default)             | 20 / 20  | n/a         | n/a              | 0     |
| 4,400.00        | 8.4 %                     | **0 / 20** | 1 / 20      | 8 / 20           | 12    |
| 4,082.24        | 15.0 % (Pulse floor)      | **0 / 20** | 1 / 20      | 8 / 20           | 12    |

The §3.5 falsifiable hypothesis is **confirmed**: the male divergence cluster is
mediated by the engine's blood-volume baseline, and **even an 8.4 % reduction
(to 4,400 mL)** toward the female value already eliminates the entire regime.

**No per-input threshold [corrected 2026-06-16].** All 20 inputs clear at the
4,400 mL bracket; there is no BV × ARDS × FiO₂ per-input threshold. The original
claim that two severe-ARDS / FiO₂ = 1.0 cases (S4_M_0158 / 0159) "need deeper BV
reduction" was the classification-race artifact described in the correction note
above — those two runs do not diverge at 4,400 mL.

**Per-case consistency between brackets.** All 20 originally-diverged inputs now
produce the same flag combination at both BV = 4,082 and BV = 4,400 mL
(S4_M_0024 clean at both; S1_M_0119 not_steady_state at both; S1_M_0159
implausible at both — the PaO₂ > 600 mmHg hyperoxia overshoot is independent of
BV; S4_M_0158 / 0159 clean at both). The BV manipulation lifts the divergence
flag uniformly on the inputs that were failing at the default BV.

### F-S018-C — The "not_steady_state" residue reflects input-profile incoherence, not a BV side-effect

Of the 20 floor-batch runs (BV = 4,082.24 mL):

* **12 clean** — full normal completion within steady-state bounds
  and drift thresholds.
* **8 not_steady_state** — completed (no divergence) but failed the
  drift / variance / flatline tests.
* **1 implausible** — PaO₂ exceeded the 600 mmHg upper bound
  (S1_M_0159 at FiO₂ = 1.0; this is the F-003 hyperoxia overshoot
  on a healthy adult, unrelated to BV).

The not_steady_state runs are concentrated in **S1_M (4 / 4) and
S2_M (3 / 4)** — the milder ARDS scenarios. In S3_M only 1 / 4 is
not_steady_state and all of S4_M (8 / 8) is clean.

**Interpretation.** The 16 shared Morris indices (run_idx 119 / 157 /
158 / 159 across scenarios) have a fixed input profile: HR = 50,
RR = 20, SBP = 90, DBP = 67.5, with FiO₂ = 1.0 in three of the four.
This profile is *physiologically inconsistent* on a healthy adult
(S1) — bradycardic and hypotensive but tachypneic and on full
oxygenation. As ARDS severity rises (S2 → S3 → S4), the profile
makes increasingly more clinical sense (a hypotensive, fully-
oxygenated patient with severe ARDS is recognizable as septic-pre-
arrest), and the runs become clean. The BV manipulation has revealed
that the not_steady_state classifications are not artefacts of the
BV reduction but rather a property of the input profile itself,
previously hidden behind the divergence flag. With BV high enough,
Pulse cannot solve the input combination at all; with BV reduced, it
solves but oscillates. Either way, the runs are not contributing
trustworthy physiology — the underlying input is the issue, not the
engine.

### F-S018-D — Replacement physiology is dominated by elevated FiO₂ rather than BV

Across the 40 re-runs, steady-state means (clean runs only) are:

* HR: ~98 bpm (vs the input HR = 50 set on the 16 shared inputs)
* MAP: ~91 mmHg
* V_t delivered: ~525 mL
* SpO₂: ~0.95 – 0.96
* PaO₂: ~221 – 234 mmHg (bracket vs floor — bracket runs slightly
  higher because more runs at FiO₂ = 1.0 survive)
* PaCO₂: ~39 mmHg

The dominant feature of the re-run physiology is **the persistent
compensatory tachycardia** (§3.4.1) decoupling input HR from output
HR — even with BV reduced, Pulse drives HR to ~98 bpm rather than the
input baseline 50 bpm. This is consistent with §3.4.1's finding that
input HR is silently disregarded under hypoxemic stress in S3 / S4;
S018 shows the decoupling extends down to mild scenarios when the
underlying input profile is incoherent.

## What this changes in the manuscript

### Confirmed before run completion

* §3.5 paragraph beginning "Pulse's `SetupPatient.cpp` computes
  blood-volume baseline" gets the actual Pulse-computed numbers
  (male 4,802.63 mL, female 3,996.09 mL — direct from pulse.log)
  instead of the rounded "5,060 / 4,200" approximations.
* §3.5 acquires F-S018-A: Pulse's per-patient BV floor of 4,082.24
  mL on the male surrogate, with the implication that the
  "20 % difference" framing is bounded by the engine's own setup
  rules.

### Confirmed after run completion

* The §3.5 "falsifiable hypothesis to test in follow-up work"
  sentence is replaced with a mechanism verdict: **mechanism
  confirmed — BV reduction eliminates the divergence cluster
  (20 → 0 → 0 across BV = 4,803 → 4,400 → 4,082 mL; even the 8.4 %
  reduction to 4,400 mL already clears all 20)**.
* New compact result paragraph after the existing §3.5 mechanism
  candidate paragraph reports the S018 numbers. (The per-input
  threshold structure originally written here was based on two
  classification-race artifacts and is retracted — see the F-S018-B
  correction note.)
* Caveat paragraph reports F-S018-C (the not_steady_state residue
  reflects input-profile incoherence on the 16 shared Morris
  inputs, not a BV side-effect; the underlying input combination
  HR = 50 + RR = 20 + SBP = 90 on healthy lungs is itself
  unsteady, previously hidden behind the divergence flag).

## What this does NOT change

* No changes to the original 1,280-run sweep classification.
* No changes to H1, H2, H3, H4 hypothesis verdicts elsewhere in
  §3 — S018 is a §3.5 mechanism refinement, not a re-classification.
* No data deletions. The original diverged runs remain in
  `data/runs/full_sweep/*/S*_M_*/`; S018 adds re-runs in
  `data/runs/s018_blood_volume/runs/`.

## Caveats

* The BV floor (4,082.24 mL) is for the male standard surrogate
  only. A separate floor exists for the female surrogate but was
  not characterized here (out of scope — H4 sex-stratification is
  already pinned in §3.6).
* If the divergence rate at the floor bracket is 0 / 20, this is
  *consistent with* but does not prove the BV mechanism — other
  weight-coupled parameters (cardiac-output baseline, etc.) could
  co-move with the BV override.
* The "intermediate bracket" at 4,400 mL is a halfway-house point,
  not a preregistered value; the dose-response inference depends on
  a clean signal between three BV levels
  (default / intermediate / floor).

## Related artifacts

- Manuscript: `preprint/manuscript.md` §3.5 (mechanism refinement
  pending run completion).
- Roadmap: `ROADMAP_PHASE_B.md` §B2 (this experiment fulfills B2).
- Memory: `phase_b_compute_sprint_2026_05.md` (Phase B index; B2 →
  to be marked completed once S018 lands).
- Engine patch: `engine/run_atlas_engine.py` (new
  `baselines.blood_volume_ml` override path, documented in module
  docstring).
- Docker image: `pulse-atlas-engine:bv-override` (built from the
  patched wrapper; sha256 to be recorded once the bracket runs
  complete).
- Run sweep script: `scripts/s018_bv_falsification.py`.
