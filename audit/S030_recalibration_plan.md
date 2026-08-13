# S030 — in-repo replication of the ARDS severity → Berlin calibration

**Status: CLOSED (2026-08-13). The experiment ran, was analysed, and shipped.**

## ⚠️ Correction of this file's own 2026-08-12 header

That header read, verbatim:

> **What is NOT asserted here: the scientific outcome, or whether the plan below
> was completed as written.** […] Closing this properly requires the author to
> read the three artefacts against the plan.

**That statement was false when written.** The outcome was already in this very
file, 130 lines further down (`# RÉSULTATS (2026-07-26, 40 runs terminés)`, five
numbered findings, then `# S030b — RÉSULTATS (16 runs terminés, 16/16)`), and
the work had already shipped:

| commit | what it did |
|---|---|
| `5fa148c` | launched the two-arm replication (40 runs) |
| `63c8c65` | recorded the results: window-dependent calibration, severe band depends on patient–ventilator interaction |
| `abd1e5f` | the 9.7 % gap was a window-definition artefact; replication exact within 2 %; variance study cancelled |
| `3875e07`, `b38cbd1` | S030b: 16 runs, HR/RR bounds re-derived in-repo, severe-band robustness |
| `9dc079e` | **wrote it into the manuscript**: Supplement §S2 and §S5 |

The correction pass of 2026-08-12 read the top of the file, found a stale
"running in the background" line, and declared an absence without reading on.
It is the same failure as the "Status: DRAFT" field of
`audit/figure2_reframing_diffs.md`, in the opposite direction: **a status field
is not a measurement, and neither is its correction.**

## Verification performed at closure (2026-08-13), read-only

Plan → data → analysis, with every CSV accessed by column name:

- **The five replication values match exactly.** This file's "notre [60,120]"
  column (255.2 / 199.1 / 149.8 / 116.4 / 86.8) equals the `free`, `M` rows of
  `results/s030_pf_by_arm.csv` at fractions 0.26 / 0.30 / 0.60 / 0.90 / 0.95.
- **The instability band reproduces.** `status = FAILED` on exactly 10 rows:
  fractions 0.910, 0.920, 0.930, 0.940, 0.945, in **both** arms; 0.900 and
  0.950 completed.
- **The 0.95 chain matches the supplement.** Free arm: P/F 86.8 → 112.8,
  RR 30.5, Vt 418.2 mL, PaCO₂ 43.6. Locked: 69.1 → 91.8, RR 20.0, PaCO₂ 50.9.
- **S030b is 16/16**: 8 severity rows (0.96–0.99 × 2 arms) and 8 acceptance
  probes in `results/s030b_analysis.csv`, the probes carrying Pulse's own
  rejection strings for HR 49/111 and RR 7/21 and acceptance for 50/110/8/20.
- **The published tolerance is the right one.** §S5's "within 0.6 %" holds and
  "within 0.5 %" would not: 96.6 against the companion's 96.1 is +0.52 %.

**Scientifically, nothing here is open.** One traceability gap was found during
this verification and is filed separately, because it is a provenance problem
and not a result: three published values (256.5 / 150.5 / 96.6, at the
companion's [108, 168] s window) and the alveolar chain of §S5 exist in no
committed artefact. See `audit/s030_published_value_provenance.md`.
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

---

# S030b — RÉSULTATS (2026-07-26, 16 runs terminés, 16/16)

Script : `scripts/run_s030b_severe_and_bounds.py` · analyse :
`scripts/analyze_s030b.py` → `results/s030b_analysis.csv`.
Les fenêtres de S030 ont été **re-calculées avec le même code** pour que les
deux expériences soient comparables ; elles reproduisent exactement les
valeurs déjà consignées plus haut.

## Bloc 2 — bornes d'acceptation HR / RR : 8 / 8

| sonde | attendu | exit | CSV | observé |
|---|---|---|---|---|
| HR 49 | rejet | 1 | non | **REJETÉ** |
| HR 50 | accept | 0 | oui | **ACCEPTÉ** |
| HR 110 | accept | 0 | oui | **ACCEPTÉ** |
| HR 111 | rejet | 1 | non | **REJETÉ** |
| RR 7 | rejet | 1 | non | **REJETÉ** |
| RR 8 | accept | 0 | oui | **ACCEPTÉ** |
| RR 20 | accept | 0 | oui | **ACCEPTÉ** |
| RR 21 | rejet | 1 | non | **REJETÉ** |

Le rejet est **bruyant** (exit 1 + `[ERROR]`), jamais silencieux — même
régime que la porte BP (H2). Pulse **nomme lui-même la borne** :

- « Patient heart rate baseline of 49 is too low. Minimum heart rate baseline
  allowed is 50 bpm. »
- « Patient heart rate baseline of 111 bpm is too high. Maximum heart rate
  baseline allowed is 110 bpm. »
- « Patient respiration rate baseline of 7 bpm is too low. Non-healthy values
  must be modeled by adding/using a condition. Minimum respiration rate
  baseline allowed is 8 bpm. »
- « Patient respiration rate baseline of 21 bpm is too high. […] Maximum
  respiration rate baseline allowed is 20 bpm. »

Les bornes 50–110 bpm et 8–20 bpm cessent d'être héritées du projet
compagnon : elles sont **re-dérivées en première main**, avec les mots du
moteur.

`[ERROR] Unable to find substance directory : ./` apparaît dans **tous** les
runs, y compris ceux qui réussissent : avertissement de démarrage bénin, à ne
pas confondre avec un rejet.

### ⚠️ DÉFAUT TROUVÉ DANS `src/detector.py` — le rejet HR-trop-bas échappe à `clamped`

Testé empiriquement (`check_clamped` sur les vrais logs) :

| sonde | `clamped` |
|---|---|
| HR 49 | **False** ← trou |
| HR 111 | True |
| RR 7 | True |
| RR 21 | True |

**Cause, lue dans la source C++** — `SetupPatient.cpp` du clone local
(`engine/src/cpp/engine/human_adult/whole_body/controller/`) : sur les
**10** messages de rejet de baseline, **un seul omet l'unité**, celui-là :

```cpp
L297  "… baseline of " << heartRate_bpm << " bpm is too high. Maximum …"
L311  "… baseline of " << heartRate_bpm << " is too low. Minimum …"   // <-- pas d'unité
L495-514  systolic / diastolic : " mmHg is too low/high"
L552-558  blood volume        : " mL is too low/high"
L580-586  respiration rate    : " bpm is too high/low"
```

Notre motif `baseline of [\d\.]+ \S+ is too (?:high|low)` exige un jeton entre
le nombre et « is » ; il couvre 9 messages sur 10 et manque exactement
celui-là. Le second motif ne rattrape pas : il dit `maximum`, or ce message
dit « Minimum ». Et les messages HR ne contiennent pas la clause
« must be modeled by adding/using a condition ».

**Portée sur les résultats publiés : nulle.** Vérifié sur les 1 280 runs
(`audits/reproduction_2026-06-07/aggregated.parquet`) : `in_hr` min = 50,000 /
max = 110,000 et `in_rr` min = 8 / max = 20. Aucun run n'a jamais demandé
HR < 50 ; le motif n'avait donc jamais à se déclencher. De plus le run reste
attrapé : `check_diverged` retourne True (exit 1, pas de CSV). La
mésclassification déplacerait un run de `clamped` vers `diverged`, elle ne le
laisserait pas passer.

C'est donc un **trou latent**, pas une erreur dans un chiffre publié.

## Bloc 1 — la bande sévère devient-elle robuste ?

P/F à FiO2 = 0,40, trois fenêtres. Aucun échec moteur (cohérent : 0,96–0,99
est au-dessus de la zone [0,879 – 0,945]).

| bras | cran | [60,120] | [108,168] | [240,300] | verdict |
|---|---|---|---|---|---|
| libre | 0,96 | 77,4 sév | 85,9 sév | **104,8 mod** | dépend de la fenêtre |
| libre | 0,97 | 70,1 | 77,0 | 94,3 | **sévère partout** |
| libre | 0,98 | 63,9 | 69,3 | 83,1 | sévère partout |
| libre | 0,99 | 58,4 | 62,6 | 72,9 | sévère partout |
| verrouillé | 0,96 | 64,2 | 69,6 | 84,6 | **sévère partout** |
| verrouillé | 0,97 | 59,6 | 64,4 | 77,1 | sévère partout |
| verrouillé | 0,98 | 54,8 | 59,0 | 69,5 | sévère partout |
| verrouillé | 0,99 | 50,1 | 53,5 | 61,7 | sévère partout |

**Réponse à la question posée.** Sous trigger libre, « sévère » ne survit aux
trois fenêtres qu'à partir de **0,97** ; à 0,95 et 0,96 l'étiquette dépend de
la fenêtre. Sous trigger verrouillé, « sévère » tient dès **0,95**.
L'étiquette de Berlin au cran extrême est donc gouvernée par l'interaction
patient-machine autant que par le modèle ARDS.

Chaîne causale, fenêtre [240,300] — monotone et cohérente :

| bras | cran | RR | Vt | PaCO2 | PaO2 | P/F | SpO2 |
|---|---|---|---|---|---|---|---|
| libre | 0,96 | 31,5 | 417,9 | 43,6 | 41,9 | 104,8 | 0,812 |
| libre | 0,99 | 34,3 | 416,6 | 43,7 | 29,2 | 72,9 | 0,620 |
| verrouillé | 0,96 | 21,2 | 406,5 | 50,0 | 33,9 | 84,6 | 0,678 |
| verrouillé | 0,99 | 21,3 | 407,0 | 52,5 | 24,7 | 61,7 | 0,460 |

L'hyperpnée compensatrice du bras libre (RR 31–34 vs 21–24) achète ~6 mmHg de
PaCO2 et ~8 mmHg de PaO2 : c'est tout l'écart entre les deux bras.

**Deux irrégularités notées, non lissées :**

1. Bras verrouillé, RR mesurée 21,2 / 22,3 / 23,6 puis **21,3** à 0,99 — la
   monotonie casse au dernier cran (PaCO2 remonte à 52,5 en miroir).
   **CORRECTION 2026-07-26 :** j'avais d'abord écrit « probable artefact
   d'alignement de phase en bord de fenêtre ». C'est **faux**, et vérifié
   comme tel : sur [120, 300] s au cran 0,99 verrouillé la RR est
   rigoureusement constante à 21,3 (écart-type 0,00, min = max), alors que le
   cran 0,98 varie entre 22,7 et 24,6. Ce n'est donc ni du bruit ni un effet
   de fenêtre. **Je ne sais pas expliquer cette baisse.** Consigné comme
   inexpliqué ; aucune conclusion n'en dépend, et rien n'en est tiré dans le
   manuscrit.

2. Verrouillé 0,99 → SpO2 = 0,460, soit **46 %**, sous la borne basse
   `implausible` de l'atlas (50 %). Ce cran déclencherait notre propre drapeau.
   **Ce n'est pas une défaillance du moteur.** Quatre relations vérifiées sur
   ce run : équation des gaz alvéolaires (tient à 0,1 mmHg entre les bras),
   gradient A-a inchangé entre bras (188,7 vs 188,8), courbe de dissociation
   (Severinghaus donne 44,5 % à PaO2 = 24,7 ; observé 46,0 %), et
   Henderson-Hasselbalch (pH prédit 7,304 pour HCO3 25,2 en acidose
   respiratoire aiguë ; observé **7,306**). La SpO2 franchit **notre** standard
   de plausibilité clinique, pas une limite numérique du solveur. Ces quatre
   contrôles établissent la cohérence interne de la chaîne d'échange gazeux et
   acide-base **sur ce run** — ils ne constituent pas un audit du solveur et ne
   prouvent pas une robustesse globale ; l'anomalie de RR ci-dessus reste
   d'ailleurs sans explication.

## Ce que le papier affirme, et si ça tient

Methods (`paper.tex` L338) : « these impairment fractions place Pulse's
arterial PaO2/FiO2 **near the centres** of the Berlin mild and moderate bands
and **just inside the upper boundary** of the severe band ».

Re-dérivé ici, protocole et fenêtre du compagnon : 256,5 (centre mild = 250) ·
150,5 (centre moderate = 150) · 96,6 (juste sous 100). **La formulation est
exacte, y compris sa prudence.** Rien à corriger.

Ce qui n'est pas dit : la marge à 0,95 est de 3,4 mmHg, la trajectoire n'a pas
convergé à 300 s, et l'étiquette bascule en « moderate » si l'on mesure
au-delà de la fenêtre de l'atlas sous trigger libre. L'atlas ne mesure jamais
au-delà de 120 s, donc ce régime lui est extérieur — mais un relecteur qui
rallongerait le run trouverait « moderate » et croirait à une erreur.

## Guard rail

Aucun fichier de manuscrit n'a été touché. Décisions de rédaction à prendre
conjointement.
