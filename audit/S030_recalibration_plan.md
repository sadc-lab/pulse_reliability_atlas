# S030 — in-repo replication of the ARDS severity → Berlin calibration

**Status as of 2026-07-26: PLANNED, script written, NOT YET RUN.**
Script: `scripts/run_s030_ards_berlin_recalibration.py` (committed, never executed).

---

## Why

The impairment fractions {0.26, 0.60, 0.95} → P/F 256 / 150 / 96, and the
demonstration that Pulse's documented {0.3, 0.6, 0.9} → 199 / 150 / 119 (all
*moderate*), are a headline contribution. They rest entirely on the companion
project and are **not re-derivable in this repo**: our severity runs use
Vt 550 mL at FiO2 0.60; the calibration needs Vt 403.8 mL at FiO2 0.40, and
P/F is ventilation-dependent.

## Protocol — retrieved verbatim, not guessed

From `Pulse_translation_new/data/engine_runs/e6_ards_calibration/results.json`:

```
baselines : age 18, 67.3 kg, 180 cm, Male, HR 70, RR 16, SBP 118, DBP 70
ventilator: VC-AC, Vt 403.8 mL, set_rr 16, PEEP 10, FiO2 0.40
settle 60 s, duration 0.03 h (~108 s), sampling 10 s
```

Female check used Vt 337.2 mL (6 mL/kg × 56.2 kg).

## What the companion actually ran (60 runs, two campaigns)

**March 2026 — original calibration, 28 runs**
- coarse 0.1–0.9 step 0.1 · fine 0.20–0.30 step 0.01 · high-end 0.90–0.99

| fraction | PaO2 | P/F | Berlin |
|---|---|---|---|
| 0.22 | 123.2 | 307.9 | no-ARDS |
| 0.23 | 118.3 | 295.8 | mild |
| 0.26 | 102.4 | **256.0** | mild |
| 0.29 | 85.9 | 214.7 | mild |
| 0.30 | 79.7 | **199.3** | moderate |
| 0.60 | 60.0 | **150.1** | moderate |
| 0.80 | 52.5 | 131.2 | moderate |
| 0.90 | 47.5 | **118.7** | moderate |
| 0.92 / 0.94 | — | — | **ENGINE FAILURE** |
| 0.95 | 38.4 | **96.1** | severe |

**April 2026 — E6 refinement, 32 runs**
mild_fine 0.240–0.280 step 0.005 · moderate_fine 0.55–0.65 step 0.01 ·
severe_fine 0.93–0.97 step 0.005 · reproducibility 0.26/0.60/0.95

Note E6 at 0.24 gives P/F 276.1 where March gave 281.5 — the two campaigns are
not identical, ~5 mmHg apart.

## ⚠️ CRITICAL FINDING, 2026-07-26 — the set rate is not the effective rate

Across the 28 successful E6 runs:

| quantity | commanded | actually measured |
|---|---|---|
| respiratory rate | **16** | **21.65 – 37.17**, median **27.25** |
| tidal volume | 403.8 mL | 416.0 – 419.5, median 418.7 (**+3.7 %**) |
| PaCO2 | — | 43.0 – 44.5 mmHg |

**The patient triggers far above the set rate**, and the excess is
severity-dependent (up to 37 breaths/min at high impairment). Minute
ventilation is therefore *not* controlled by `set_rr`. Since
V_A = (V_T − V_D) × RR and P_AO2 = P_IO2 − PaCO2/R, the P/F values inherit
that variability directly.

This is the same F-004 patient–ventilator dyssynchrony the atlas documents,
and S014 showed that locking `InspirationPatientTriggerPressure` to −2 cmH2O
collapses it (median Vt CV 0.351 → 0.016).

**Consequence for the design:** the replication must run BOTH arms —
free-trigger (faithful to the companion) and trigger-locked (controlled
ventilation). Only the locked arm can support a threshold claim resting on a
0.7 mmHg margin. If the two arms disagree on which Berlin band a fraction
occupies, that is itself a publishable result and the current thresholds must
be restated.

## Design (to run)

Runs last **300 s**, not ~108 s, with P/F reported over two windows —
atlas-canonical [60, 120] s and late [240, 300] s. If they disagree, the band
assignment is window-dependent and the 0.7 mmHg margin is meaningless.

| block | grid | n |
|---|---|---|
| anchors (male) | 0.26, 0.30, 0.60, 0.90, 0.92, 0.95 | 6 |
| 300-crossing | 0.220, 0.225, 0.230, 0.235 | 4 |
| 200-crossing **(critical)** | 0.285, 0.290, 0.295 | 3 |
| 100-crossing + instability | 0.910, 0.930, 0.940, 0.945 | 4 |
| female | 0.26, 0.60, 0.95 (Vt 337.2) | 3 |

17 male + 3 female = **20 runs per arm**; two arms (free / locked) = **40 runs**.
3 parallel, 300 s each → roughly 70 minutes.

**Not yet decided with the author:** whether to run both arms or start with the
free-trigger arm alone.

## Second experiment, also pending — HR / RR acceptance bounds

The paper asserts three times that Pulse accepts HR only in 50–110 bpm and RR
only in 8–20 bpm, citing companion boundary probes. Our 1,280-run sweep proves
those values are *accepted* (every run used them) but never that 49 or 111 are
*rejected*. Eight runs would close it: HR 49/50/110/111, RR 7/8/20/21.

Companion results to reproduce: HR — 45/48/49 fail, 50–110 pass, 111/115 fail
(11 runs). RR — 5/7 fail, 8–20 pass, 21/25 fail (9 runs).

## Guard rails

Nothing in this experiment edits any manuscript. Per the autonomy pact
(`CLAUDE.md`), findings are recorded and brought back for a joint decision
before any text changes.
