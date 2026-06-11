# Pulse 4.3.1 — How the ARDS severity scalar maps to respiratory physiology

**Purpose.** Canonical, source-traced note on *how* Pulse translates a single ARDS
"impairment fraction" (the atlas scenario knob: S1 0.00, S2 0.26, S3 0.60, S4 0.95)
into respiratory-mechanics and gas-exchange changes. Written in response to a
co-author question (C.S., 2026-06) and to seed the pediatric papers
(Paper 1 translation layer, Paper 2 native pediatric fork).

This is the **single source of truth**. The manuscript supplement carries a compact
version; the atlas + pediatric agent memories carry pointers back here.

Verified 2026-06-11 by direct read of the pinned Pulse v4.3.1 source clone at
`C:\Users\santi\projets\Pulse_engine_adults_Gitlab\engine`. Physiology file:
`src/cpp/engine/common/system/physiology/RespiratoryModel.cpp`.

---

## 1. It is ONE knob

Pulse models ARDS as a **single `Severity` scalar in [0, 1] per lung compartment**
(`AcuteRespiratoryDistressSyndrome` condition). There is **no independent control**
of resistance vs. compliance vs. diffusion — that one number is fed separately into
several **hard-coded piecewise-linear interpolation tables**, each in a different
`RespiratoryModel` method, all calibrated against the **adult** standard patient.

The atlas sets it **bilaterally and symmetrically** (LeftLung = RightLung = scenario
value):
- `src/scenario.py:190-195` emits `ards_severity {left, right}`.
- `engine/run_atlas_engine.py:153-157` →
  `get_acute_respiratory_distress_syndrome().get_severity(LeftLung/RightLung).set_value(...)`.

So the atlas's "ARDS impairment fraction" **is** the Pulse `Severity` scalar.

---

## 2. The four effects (severity → multiplier on a baseline value)

Severity is `MAX`-combined with any other restrictive condition (pneumonia,
fibrosis) before each table is applied; in the atlas only ARDS is set, so the
combination is clean.

| Respiratory property | Direction | Calibration nodes (severity → factor) | **0.26** | **0.60** | **0.95** | Pulse method (`RespiratoryModel.cpp`) |
|---|---|---|---|---|---|---|
| Alveolar-duct (distal) **resistance** | **increases** | 0→1, 0.3→10, 0.6→15, 0.9→20, 1.0→25 | ×8.8 | ×15 | ×22.5 | `UpdateResistances` (table L3724–3731, applied L3733–3737, on `cpt.ResistancePath`) |
| Alveolar **compliance** | **decreases** | 0→1, 0.3→0.65, 0.6→0.55, 0.9→0.5, 1.0→0.4 | ×0.70 | ×0.55 | ×0.45 | `UpdateAlveolarCompliances` (restrictive table L3845–3852, ARDS→`restrictiveSeverity` L3884–3896, applied L3899–3905) |
| Alveolar **diffusion surface area** | **decreases** | 0→1, 0.3→0.5, 0.6→0.2, 0.9→0.1, 1.0→0.05 | ×0.57 | ×0.20 | ×0.075 | `UpdateDiffusion` (table L4248–4255, applied L4295–4305 on `DiffusionSurfaceArea`) |
| Pulmonary **shunt** path resistance | **decreases** → ↑ venous admixture | damage term 0→1, 0.3→0.1, 0.6→0.2, 0.9→0.15, 1.0→0.1 | ≈×0.22 | ×0.20 | ≈×0.125 | `UpdatePulmonaryShunt` (damage table L4479–4487, applied L4568–4583) |

**Atlas-level multipliers** (0.26 / 0.60 / 0.95 columns) are my own linear
interpolations of the source tables; the 0.60 column hits exact calibration nodes.

### Important caveat on the shunt row
The shunt damage term is **non-monotonic** (0.3→0.1 then 0.6→0.2; the code comment
itself flags mild "likely the only one hit instead of the recruitment factor") and
is combined via `MIN` with an alveolar-**recruitment** term (function of actual
alveolar volume, which PEEP raises) and a left/right calibration factor before being
applied. So the *effective* shunt resistance is not simply the damage value — treat
the ≈×0.22 / ≈×0.125 figures as the ARDS-driven damage component only.

### Secondary effects (smaller)
Severity also feeds the **driver pressure** (restrictive term, `UpdateDriverPressure`,
ARDS block L4668), lung **volumes**, and the **I:E ratio** — minor relative to the
four above.

---

## 3. Why this matters for our atlas result

At S4 (0.95): resistance ×22.5, compliance ×0.45, **diffusion surface collapsed to
7.5 % of normal**, shunt wide open. The diffusion + shunt collapse is what drives the
severe arterial hypoxemia that **explains the input-HR / output-HR decoupling**
reported in main-manuscript §2.6 (chemoreflex/baroreflex asserting against hypoxemia).
The four curves are smooth; the 0.91–0.945 solver-instability band (Supplement §S5)
is an **emergent** numerical property of the combined stiff state, not a discontinuity
in any single table.

---

## 4. No surfactant model — confirmed (multi-criteria audit, 2026-06-11)

**Audit method.** Case-insensitive search of the **complete** engine tree — 3,304
files / 23 MB, *including git-ignored and hidden files* — at tag `REL_4_3_2`
(commit `e8a3649`). Not just `src/cpp`: code, `data/`, `docs/` (Methodology,
Validation, `Sources.bib`), everything.

**Direct term.** `surfactant` → **0 / 3,304 files**.

**Disguised-model check (all zero):** `surface tension`, `surface-tension`,
`Laplace`, `derecruitment`, `alveolar stability`, `opening`/`closing pressure`.

**Non-zero terms, each inspected (not surfactant):** `recruit` (86), `collapse`
(154), `atelectasis` (2), `hysteresis` (3), `inflection` (3), `alveolar compliance`
(3) — trace to mechanical collapse (pneumothorax/hemothorax), the empirical
recruitment→shunt map, or phenomenological compliance. (This is why "alveolar
collapse" was *dropped* from the published zero-list: Pulse does model collapse,
just not via surfactant.)

**External.** Discourse forum `surfactant` → 0 topics; `surface tension` → 0
relevant. Public docs → no mention.

**Version traceability (4.3.1 ↔ 4.3.2).** Ran on `REL_4_3_2`; applies to 4.3.1:
`git diff REL_4_3_1 REL_4_3_2` touches **no** respiratory/CDM source (delta = 7
build-system files, +46/−17). Re-run this diff on the next Pulse release before
re-asserting.

**What Pulse models instead (phenomenological, not surfactant):** P–V hysteresis
(emergent, no routine); recruitment = acinar-volume→shunt map, PEEP-calibrated,
`UpdatePulmonaryShunt()` (`RespiratoryModel.cpp:4388`, interp `:4503`); compliance =
lumped element w/ disease multipliers, `UpdateAlveolarCompliances()` (`:3774`).

**Verdict.** Neonatal RDS (hyaline membrane disease) — surfactant-deficiency
disease, incl. instillation response — **not representable**. **Missing-physics**
gap, not calibration. Surfactant = module to *add* (Paper 2), not retune.

---

## 5. Implications for the pediatric papers

- **Single-knob + adult calibration.** Both the *baseline* R / C / diffusion-surface
  values **and** the severity→effect curves above are tuned to the adult standard
  patient. Forcing pediatric-scale bodies into the adult engine applies ×22
  resistance / ×0.075 surface on top of adult baselines — mis-scaled absolute
  consequences, with no way to retune R vs. C vs. diffusion independently.
- **Pulse hard-gates age ≥ 18** (atlas limitation #3, `SetupPatient.cpp`), which is
  precisely why Paper 1 (translation layer) and Paper 2 (native fork) exist.
- **Paper 2 priority.** These four interpolation tables are a prime target to
  re-derive against pediatric mechanics; surfactant is a missing module to add for
  any neonatal ambition.
- This is the substance behind C.S.'s intuition that ventilatory-mechanics
  changes "test the limits of the model" harder in pediatrics, and his point that
  neonatal ARDS + surfactant is currently unimaginable in the engine.

---

## 6. Source pointers

- Mechanism: `Pulse_engine_adults_Gitlab/engine/src/cpp/engine/common/system/physiology/RespiratoryModel.cpp`
  (`UpdateResistances`, `UpdateAlveolarCompliances`, `UpdateDiffusion`, `UpdatePulmonaryShunt`, `UpdateDriverPressure`).
- Atlas wiring: `src/scenario.py:190-195`, `engine/run_atlas_engine.py:153-157`.
- Manuscript: compact version in `preprint_npj/supplement.tex` §S5 (`sec:s5-mapping`),
  one Methods sentence in `preprint_npj/paper.tex` §Sweep design.
