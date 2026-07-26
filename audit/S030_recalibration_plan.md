# S030 — in-repo replication of the ARDS severity → Berlin calibration

**Status: LAUNCHED 2026-07-26, running in the background.**
Script: `scripts/run_s030_ards_berlin_recalibration.py`.
Launched with `nohup uv run python scripts/run_s030_ards_berlin_recalibration.py`,
log at `data/runs/s030_run.log` (stdout is buffered; follow progress by counting
subdirectories of `data/runs/s030_ards_berlin_recalibration/` instead).

**40 runs = 2 arms x (17 male + 3 female), 300 s each, 2 workers -> ~100 min.**
`max_workers` is 2, not 3: `src/runner.py` hard-caps it at
`MAX_PARALLEL_LAPTOP = 2` and raises rather than silently over-subscribing.

**IF THE SESSION DIED MID-RUN:** count the subdirectories. If fewer than 40,
re-launch the same command -- the runner skips nothing, so delete the run
directory first or accept overwrite semantics (check `run_many(overwrite=)`).
Nothing downstream has been written yet, so a restart costs only compute.

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

---

# RÉSULTATS (2026-07-26, 40 runs terminés)

## 1. La réplication est exacte — l'écart de 9,7 % était un artefact de fenêtre

Le protocole compagnon dit « settle_s: 60, duration_h: 0.03 ». Ce n'est **pas**
un run de 108 s mesuré à partir de t = 60 : c'est 60 s de stabilisation **puis**
un run de 108 s, dont les 60 dernières secondes sont la mesure. En temps absolu
leur fenêtre est **[108, 168]**, pas [60, 120].

| cran | compagnon | notre [60,120] | notre [108,168] |
|---|---|---|---|
| 0,26 | 256,0 | 255,2 (−0,3 %) | **256,5 (+0,2 %)** |
| 0,30 | 199,3 | 199,1 (−0,1 %) | **199,8 (+0,3 %)** |
| 0,60 | 150,1 | 149,8 (−0,2 %) | **150,5 (+0,2 %)** |
| 0,90 | 118,7 | 116,4 (−2,0 %) | **121,0 (+1,9 %)** |
| 0,95 | 96,1 | 86,8 (−9,6 %) | **96,6 (+0,5 %)** |

**Aucun désaccord entre les deux projets.** Seulement une frontière qui bouge
avec le protocole.

## 2. Zone d'instabilité confirmée indépendamment

10 échecs = les 5 crans 0,910 / 0,920 / 0,930 / 0,940 / 0,945, **dans les deux
bras**. 0,900 et 0,950 passent partout. La zone [0,91 – 0,945] est re-dérivée
ici, plus héritée.

## 3. Le P/F ne converge pas à 120 s — le cran 0,30 bascule

Tranches de 60 s : 199,1 → 199,9 → 200,2 → 200,4 (libre) ; 198,8 → 200,4
(verrouillé). La bande *mild* ouvre au-dessus de 200 : **modéré à 120 s, léger
à 300 s**.

## 4. La bande sévère dépend de l'interaction patient-machine

Cran 0,950 : libre 86,8 → 112,8 (**sévère puis MODÉRÉ**) ; verrouillé 69,1 →
91,8 (**sévère partout**).

Chaîne causale fermée, fenêtre [240,300] :

| | RR | V̇E | PaCO2 | PaO2 | P/F | SpO2 |
|---|---|---|---|---|---|---|
| libre | 30,5 | 12,77 L/min | 43,6 | 45,1 | 112,8 | 0,841 |
| verrouillé | 20,0 | 8,13 L/min | 50,9 | 36,7 | 91,8 | 0,720 |

## 5. Le verrou a agi

RR mesurée : libre 22,4–37,2 · verrouillé 20,0–25,1.

## Runs annulés, et pourquoi

L'étude de variance au cran 0,95 (3 répétitions × 2 bras) est **annulée** :
S007 établit que Pulse est déterministe et bit-exact pour des entrées fixées,
donc des configs identiques rendent des sorties identiques. L'écart était
structurel, pas stochastique, et il est expliqué.

**Reste : 16 runs** — grille de robustesse sévère (0,96–0,99 × 2 bras) et
bornes d'acceptation HR/RR.
