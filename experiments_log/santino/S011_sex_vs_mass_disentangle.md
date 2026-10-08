---
id: S011
author: santino
date: 2026-04-27
status: done
tags: [sex-vs-mass, h4, confounding, ards-instability, divergence, decomposition]
linked_code:
  - scripts/sex_vs_mass_check.py
  - src/detector.py
linked_data:
  - results/sex_vs_mass.parquet
  - results/sex_vs_mass_decomposition.csv
  - data/runs/sex_vs_mass/
supersedes: ""
related: [S006, S008, S009]
---

# S011 — Sex vs mass disentangling (controlled 2×2 design)

## Hypothesis

The H4 finding from S006/S008 (Wasserstein-significant M-vs-F separation
on PaO2 and PaCO2) **confounds the sex flag with the 11.1 kg mass
difference** between Pulse's standard adult surrogates (M = 67.3 kg
180 cm; F = 56.2 kg 163 cm). Pulse's `SetupPatient.cpp` contains both
sex-conditional branches *and* mass-driven equations, so the M-vs-F
distance we measure is a mixture of two effects.

A 2×2 controlled design at fixed midrange Morris inputs — sex {M, F} ×
mass {67.3 kg, 56.2 kg} — should decompose the H4 effect into a sex
component (held mass constant) and a mass component (held sex constant).
If the two effects are similar in magnitude, H4 is confounded; if the
sex component dominates, H4 is genuinely categorical.

## Motivation (why now)

- S010 (literature pass) is closed and the manuscript is reviewer-ready
  except for the H4 caveat. Reviewers will ask "is this sex or just
  size?" — we need an evidence-backed answer before submission.
- Cheap experiment: 8 runs (vs S006's 1,280). Laptop-feasible in a single
  evening, no Colab needed.
- Decomposition outcome directly shapes the H4 paragraph in §Discussion.

## Method (how)

- **Cells (4)** — each cell is a (sex, mass_kg, height_cm) tuple held
  at the body's native height to avoid Pulse rejecting unusual
  height/weight pairs:
  - `M_67.3kg` — Pulse standard male (180 cm)
  - `F_67.3kg` — synthetic: female metadata + male's mass (180 cm)
  - `M_56.2kg` — synthetic: male metadata + female's mass (163 cm)
  - `F_56.2kg` — Pulse standard female (163 cm)
- **Scenarios (2)** — S1 (healthy, ARDS=0.00) and S4 (severe ARDS,
  ARDS=0.95). S2/S3 omitted; the question is whether the confound exists
  at the extremes.
- **Inputs** — midrange Morris values held constant across all 8 runs:
  HR=80, SBP=105, DBP=70, RR=14, Vt=550, FiO2=0.6, PEEP=10. VC-AC.
- **Image** — `pulse-atlas-engine` (same as S006). Pulse 4.3.1.
- **Detector** — `src/detector.py` extended with a `primary_flag`
  property exposing the highest-priority flag (priority hierarchy locked
  in S013-prep: `clamped > diverged > implausible > not_steady_state >
  clean`). Used to give each cell a single flag in the summary.
- **Driver** — `scripts/sex_vs_mass_check.py`. 8 jobs through
  `src.runner.run_many`, then `aggregate_under` produces a summary
  parquet, then a decomposition step computes:
  - `sex_effect_at_M`  = F_M_kg − M_M_kg     (per output, per scenario)
  - `mass_effect_for_S`= S_67.3kg − S_56.2kg  (per output, per sex)
- **Commit base** — repo `main` at `44f6217` (chore: sync uv.lock).

## What we tried (incl. dead ends)

1. First sketch used the full Morris envelope at midrange inputs.
   Discarded — sweeping Morris under fixed inputs is wasted compute when
   the question is structural confounding.
2. Considered an Anova-style 2×2 sex×mass interaction term; rejected for
   N=8 (no inferential power). The decomposition above is descriptive,
   not inferential — sufficient to size the effects.
3. Considered varying height as a third axis; rejected — Pulse's
   `SetupPatient.cpp` rejects extreme height/mass pairs (BMI gate).
   Holding height at the body's native value keeps each cell inside
   Pulse's accepted envelope.
4. F_67.3kg @ S4 diverged after ~1025s of simulated time
   (`OxygenSaturation not converging`). Three other S4 cells converged.
   Decided to keep the divergence as a result rather than re-run with a
   different RNG hash — the divergence is itself a sex×mass×ARDS
   interaction worth reporting.

## Results

### Per-cell summary (steady-state means over final 60 s)

| case_id          | scenario | sex | mass_kg | primary_flag       | HR     | MAP    | Vt     | SpO2  | PaO2   | PaCO2  |
|------------------|----------|-----|---------|--------------------|--------|--------|--------|-------|--------|--------|
| SVM_S1_F_56.2kg  | S1       | F   | 56.2    | not_steady_state   | 72.22  | 88.67  | 550.03 | 0.999 | 358.07 | 32.05  |
| SVM_S1_F_67.3kg  | S1       | F   | 67.3    | not_steady_state   | 72.26  | 88.88  | 561.97 | 0.999 | 346.66 | 35.01  |
| SVM_S1_M_56.2kg  | S1       | M   | 56.2    | not_steady_state   | 72.37  | 88.69  | 571.54 | 0.999 | 344.39 | 34.65  |
| SVM_S1_M_67.3kg  | S1       | M   | 67.3    | not_steady_state   | 72.35  | 88.58  | 559.76 | 0.999 | 325.36 | 42.22  |
| SVM_S4_F_56.2kg  | S4       | F   | 56.2    | clean              | 159.95 | 99.88  | 559.22 | 0.890 |  50.01 | 38.19  |
| SVM_S4_F_67.3kg  | S4       | F   | 67.3    | **diverged**       | NaN    | NaN    | NaN    | NaN   | NaN    | NaN    |
| SVM_S4_M_56.2kg  | S4       | M   | 56.2    | clean              | 160.13 | 100.50 | 557.72 | 0.897 |  51.99 | 39.25  |
| SVM_S4_M_67.3kg  | S4       | M   | 67.3    | clean              | 160.70 | 100.54 | 559.26 | 0.875 |  49.82 | 43.04  |

S1 cells all flag `not_steady_state` because SpO2 saturates at the top
of its scale (≈0.999) under FiO2=0.6 with healthy lungs — flatline at
extreme triggers the steady-state CV check. PaO2 of 325–358 mmHg is
hyperoxic but mathematically consistent with FiO2=0.6 + healthy gas
exchange; SpO2 cannot resolve the spread because of the ceiling.
**Use PaO2 / PaCO2 / Vt for S1 interpretation, not SpO2.**

### Effect decomposition (saved to `results/sex_vs_mass_decomposition.csv`)

S1 (healthy) — full 4-cell matrix, decomposition complete:

| output | sex_effect_at_67.3 | sex_effect_at_56.2 | mass_effect_for_M | mass_effect_for_F |
|--------|-------------------:|-------------------:|------------------:|------------------:|
| HR     |   −0.09            |   −0.15            |   −0.02           |   +0.04           |
| MAP    |   +0.29            |   −0.02            |   −0.10           |   +0.21           |
| Vt     |   +2.21            |  −21.51            |  −11.78           |  +11.94           |
| SpO2   |   +0.0003          |   +0.0001          |   −0.0003         |   −0.0001         |
| PaO2   |  +21.30            |  +13.68            |  −19.03           |  −11.41           |
| PaCO2  |   −7.21            |   −2.60            |   +7.57           |   +2.96           |

S4 (severe ARDS) — partial; only one decomposition arm survives because
F_67.3kg diverged:

| output | sex_effect_at_67.3 | sex_effect_at_56.2 | mass_effect_for_M | mass_effect_for_F |
|--------|-------------------:|-------------------:|------------------:|------------------:|
| HR     |   _diverged_       |   −0.19            |   +0.56           |   _diverged_      |
| MAP    |   _diverged_       |   −0.62            |   +0.04           |   _diverged_      |
| Vt     |   _diverged_       |   +1.50            |   +1.54           |   _diverged_      |
| SpO2   |   _diverged_       |   −0.0074          |   −0.022          |   _diverged_      |
| PaO2   |   _diverged_       |   −1.97            |   −2.16           |   _diverged_      |
| PaCO2  |   _diverged_       |   −1.06            |   +3.79           |   _diverged_      |

### Divergence pattern at S4

Of the four S4 cells, only **F + 67.3 kg + ARDS=0.95** failed to
stabilise — `[ERROR] OxygenSaturation is not converging` after
1025 s of simulated time (`pulse.log` tail in
`data/runs/sex_vs_mass/SVM_S4_F_67.3kg/`). The three other S4 cells
(M_67.3, M_56.2, F_56.2) converged cleanly. ARDS=0.95 sits above the
0.91–0.945 known instability zone (CLAUDE.md item 4), so the engine
is on the edge across all S4 cells — but the edge tips into divergence
only for the synthetic Female-at-male-mass cell.

## Interpretation

**At S1 (healthy)**, the sex and mass effects are **the same order of
magnitude** for the gas-exchange outputs that matter:

- PaO2: sex_at_67.3 = +21.3 mmHg, mass_for_M = −19.0 mmHg. Roughly
  equal magnitude, opposite signs at the male anchor.
- PaCO2: sex_at_67.3 = −7.2 mmHg, mass_for_M = +7.6 mmHg. Same picture.
- Vt: sex_at_56.2 = −21.5 mL, mass_for_M = −11.8 mL. Comparable.

These are exactly the outputs on which the S006/S008 H4 result rests.
**The H4 finding is confounded** in the sense reviewers will worry
about: at fixed mass, switching sex changes PaO2 by ~21 mmHg; at fixed
sex, switching mass changes PaO2 by ~19 mmHg. The published M-vs-F
Wasserstein separation is partly sex per se and partly the 11 kg mass
gap that comes packaged with the sex flag in Pulse's surrogates.

**At S4 (severe ARDS)**, the surviving decomposition arm
(`sex_at_56.2`, `mass_for_M`) shows the gas-exchange sex/mass
sensitivities **collapse** — PaO2 effects shrink to ~2 mmHg, PaCO2 to
~1–4 mmHg, SpO2 ≤0.022. ARDS dominates the variance, masking both
sex-categorical and mass-driven differences. This is consistent with
S006/S009: H4 is a healthy-baseline phenomenon that fades under
severe injury.

**Divergence is itself a finding.** Pulse's stabiliser fails for one of
the four cells we constructed at S4 — the synthetic
Female-at-male-mass — but not for the other three. This shows the
sex×mass interaction extends past output values into solver
admissibility: a patient phenotype we synthesised inside Pulse's
nominal envelope is rejected at ARDS=0.95 while three nearby phenotypes
are not. Worth noting in the manuscript as evidence that Pulse's
adult surrogates are tuned per-pair, not per-input independently.

### Limitations

1. N=8. Decomposition is descriptive, not inferential; do not attach
   p-values to single cells.
2. SpO2 at S1 is flatlined at ceiling — cannot disentangle on SpO2 at
   healthy baseline.
3. S4 decomposition has one missing cell. We cannot tell whether the
   S4 sex effect at 67.3 kg is small (like at 56.2 kg) or large; the
   synthetic-female cell crashed before producing data.
4. We did not test stochasticity — divergence may or may not be
   deterministic. A single re-run with a different RNG hash would
   answer this; not done here.
5. Height was held at body-native (180 cm at 67.3 kg, 163 cm at 56.2 kg).
   **Corrected 2026-08-04 — this limitation was previously stated backwards.**
   It is the *mass* arm that is confounded, not the sex arm. The two cells of
   each sex contrast share a height (M_67.3 and F_67.3 are both at 180 cm;
   M_56.2 and F_56.2 are both at 163 cm), so `sex_effect_at_67.3` and
   `sex_effect_at_56.2` isolate the sex flag at fixed mass **and** fixed
   height. By contrast `mass_effect_for_M` and `mass_effect_for_F` each move
   height together with mass (180 → 163 cm), so this is strictly a
   sex vs mass-and-height decomposition. Pulse's mass-vs-height coupling
   means the mass arm cannot be separated from height without violating the
   BMI acceptance gate.

   The earlier wording ("the synthetic cells thus mix sex and height too")
   understated the design: it is the clean arm that it called confounded.
   Nothing computed in this log changes; only the reading of which arm carries
   the confound.

---

## Correction (2026-08-15) — envelope, percentile matching, determinism

Three statements above are superseded. Nothing computed in this log changes; the
numbers stand. What changes is what may be said about them.

**1. "inside Pulse's nominal envelope" (§Divergence pattern at S4) is false for
the 67.3 kg female cells.** `SetupPatient.cpp` sets `heightMaxFemale_cm = 175.5`
(the female 97th percentile, per the source comment). The synthetic female is at
**180 cm**, i.e. 4.5 cm above it. Pulse does **not** clamp — only the
sex-independent 4.5–7.0 ft gate is a hard error — but it emits a warning, present
in the run logs:

> `[WARN] [0(s)] Patient height of 180 cm is outside of typical ranges - above 97th percentile(151 cm). No guarantees of model validity.`
> — `data/runs/sex_vs_mass/SVM_S1_F_67.3kg/pulse.log:60`

**2 of 8 cells** carry it: `SVM_S1_F_67.3kg` and `SVM_S4_F_67.3kg`. The other six
are clean. So `sex_effect_at_67.3` (PaCO2 −7.21, PaO2 +21.3 mmHg) is measured with
one body Pulse itself declares outside its typical range, and the S4 divergence
described in that paragraph occurred on such a body. The atlas sweep is
unaffected: **0 of 3,340** atlas `pulse.log` files carry the warning (full scan,
with these two cells as positive control).

**2. Neither arm is percentile-matched, and this is structural.**
`heightMinMale_cm = 163.0` and `heightStandardFemale_cm = 163.0` are the same
number, so the 56.2 kg contrast — which *is* fully in-envelope on height and BMI —
compares a male at his **3rd percentile** with a female at her **50th**. Holding
mass and height fixed across sexes cannot also keep both bodies at the centre of
their own reference distribution, because those distributions differ. This is a
property of any such design, not a defect of S011.

**3. Limitation 4 ("may or may not be deterministic") is superseded**, not
contradicted — it was written 2026-04-27, before the reproduction audits of June.
Supplement §S12 records bit-identical reproduction of the 1,280-run sweep across
CPU vendor and host OS (`max|Δ| = 0`, five-flag concordance 1,280/1,280), no RNG
in the engine path, and a fixed 20 ms ODE timestep. The engine is reproducible for
identical inputs on the pinned image; S011 ran on that same image.

> **Correction (2026-10-08).** "across CPU vendor and host OS" overstated the
> second axis. On both hosts the engine ran in a Linux container under WSL2 (the
> reference machine's Docker Desktop uses its WSL2 backend), so for the engine
> only the CPU vendor changed; only the Python layer changed operating system.
> Supplement §S12.6 was corrected the same day.

*Cosmetic upstream note:* the warning above prints `151 cm` where the female
ceiling is 175.5 — the `else if (height_cm > heightMax_cm)` branch prints
`heightMin_cm`. A Pulse display bug, no effect on behaviour.

Full parameter inventory behind this correction:
[`audit/pulse_sex_conditioned_parameters.md`](../../audit/pulse_sex_conditioned_parameters.md).

---

### What this lets the manuscript claim / not claim

**Can claim:** the H4 M-vs-F gas-exchange separation at healthy
baseline is confounded by mass; sex per se accounts for at most
~half the observed effect; under severe ARDS the effect is small
on either decomposition arm.

**Cannot claim** (without more data): that sex per se has zero effect
at healthy baseline (point estimates are nonzero and similar to mass
effects, just not separable on N=8); that the F_67.3kg divergence is
a deterministic property of the engine (would need replication).

## Next steps

1. **Update §Discussion H4** — add a short paragraph using the S1 PaO2
   numbers above to acknowledge the confound and re-state the claim
   conservatively. (Manuscript edit, separate task.)
2. **Optional one-shot** — re-run F_67.3kg @ S4 with a different RNG
   hash to test deterministic vs stochastic divergence. ~2 minutes
   wall-clock. Parked, not blocking the paper.
3. **Sex-specific Pulse internals** — the divergence pattern motivates
   reading `SetupPatient.cpp` for sex-conditional stabilisation
   tolerances. Out of scope for this paper; carry into Paper 2.
