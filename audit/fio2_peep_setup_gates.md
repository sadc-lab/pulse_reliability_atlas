# Do PEEP and FiO₂ pass through Pulse unchanged?

**Opened 2026-08-13.** Status: **READ-ONLY — one finding, nothing modified.**
This closes question 4 of `audit/silent_clamping_instrument.md` §7, the last
input-integrity question that register left open.

**The question, kept narrow.** For a PEEP or FiO₂ value sampled by the Morris
design and submitted by the wrapper, is there anywhere between submission and
effective instantiation in Pulse a validation, saturation, normalisation or
substitution that can make `requested ≠ instantiated`? The chain followed, for
each input separately: Morris value → wrapper → serialised Pulse action →
setter/validation → engine ingestion → value the engine actually runs with.
Out of scope by construction: the later physiological evolution of either
quantity, and the plausibility bounds on outputs.

---

## 1. PEEP — no gate, at any layer

| step | what happens | locus |
|---|---|---|
| wrapper → action | value passed through, no clamp | `engine/run_atlas_engine.py:197-199` |
| action → settings | `s.GetPositiveEndExpiratoryPressure().Set(GetPositiveEndExpiratoryPressure())` — a straight copy | `SEMechanicalVentilatorVolumeControl.cpp:103` |
| settings → model | read as the expiratory baseline and as the driver pressure, unmodified | `MechanicalVentilatorModel.cpp:706, 734, 890` |
| type | `SEScalarPressure`, no range restriction | — |

The only pressure limit in the ventilator model is the **relief valve**, whose
threshold defaults to **1000 cmH₂O** (`MechanicalVentilatorModel.cpp:228-229`).
It acts on circuit pressure at runtime, not on the submitted setting, and it
sits **50×** above the swept maximum of 20 cmH₂O.

Empirically: `PEEP` and `end expiratory` appear in **zero** lines of the 1,280
published run logs, and the setup-instantiation audit already measured
Δ_setup = 0 on all 1,260 parsed `PEEP_ventilator` contracts
(`audit/silent_clamping_instrument.md` §6.3).

**Verdict: no gate exists, so none can have affected a published run.**

---

## 2. FiO₂ — two gates. One is unreachable; the other fires in 195 published runs

### 2.1 The type gate: hard, loud, never reached

`SEScalar0To1::SetValue` **throws** `CommonDataModelException("SEScalar0To1 must
be between [0,1]")` outside [0, 1] (`src/cpp/cdm/properties/SEScalar0To1.cpp:12-17`).
FiO₂ is that type both on the action (`m_FractionInspiredOxygen`) and on the
settings' fraction amount. The bypass `ForceValue` exists but is used **nowhere**
in the ventilator action, settings or model files. The swept range is
0.21–1.0, so this gate is never approached.

### 2.2 The gate that fires: FiO₂ = 1.0 is instantiated as 0.9996

`MechanicalVentilatorModel.cpp` (block at lines ~240-290) writes each requested
fraction onto the ventilator compartment, then balances the mixture with
nitrogen. When the requested FiO₂ plus the non-N₂ ambient fractions exceeds 1,
it takes this branch:

```cpp
m_ss << "FiO2 setting + ambient fractions other than N2 is greater than 1.0. "
     << "Setting FiO2 to max value of " << FiO2 + currentN2Fraction + gasFractionDiff << ".";
Error(m_ss);
N2->GetVolumeFraction().SetValue(0.0);
O2->GetVolumeFraction().SetValue(FiO2 + currentN2Fraction + gasFractionDiff);
```

**The submitted value is overwritten.** Measured across the published sweep:

| measurement | value |
|---|---|
| runs whose log carries the message | **195 / 1,280** |
| runs requesting FiO₂ = 1.0 | **208** |
| of those, runs that reach the ventilator action | **195** (the 13 others are diverged runs whose logs stop earlier) |
| so, share of reachable FiO₂ = 1.0 runs affected | **195 / 195 = 100 %, deterministic** |
| requested FiO₂ values that trigger it | **1.0 and no other** (0.21, 0.4733, 0.7367 never do) |
| substituted value | **0.9996**, identical in all 195 |
| occurrences per run | exactly **1**, at `[0(s)]`, when the action is applied |
| relative change | **−0.04 %** |

Repository-wide, the same behaviour, same value:

| campaign | logs | affected |
|---|---:|---:|
| `full_sweep` | 1,280 | 195 |
| `full_sweep_repro` (independent reproduction) | 1,280 | **195** |
| `s021_hyperoxia_convergence` | 60 | **60 / 60** |
| `s018_bracket_repro` | 10 | 10 |
| `s018_blood_volume` | 40 | 26 |
| `s018_tier2_repro` | 80 | 26 |
| `phase4b_seed44_S2M` | 160 | 30 |
| `seed_stability_S2M_seed43` | 80 | 27 |
| `s014_trigger_lockout` | 64 | 8 |
| `pilot_S1_M` | 22 | 6 |
| `s030`, `s030b`, `continuous_ards`, `scenario_smoke`, `sex_vs_mass` | 124 | **0** (no FiO₂ = 1.0 there) |

### 2.3 What this is, stated precisely

- **It is a substitution of a submitted operational input.** The engine runs
  with 0.9996 where 1.0 was asked for.
- **It is not silent.** It is logged `[ERROR]`, once, per run.
- **It is not a rejection.** The run continues to completion.
- **It is not a setup-ingestion defect.** The serialised action still carries
  1.0, which is why Δ_setup = 0 held on all 10,160 contracts — the substitution
  happens one layer later, when settings are applied to the gas compartment.
  The two measurements are consistent, not contradictory.
- **FiO₂ = 1.0 is inside Pulse's accepted range.** The cause is not an
  out-of-range input: it is that the ventilator compartment already holds trace
  CO₂ and H₂O, so a fraction of exactly 1.0 for oxygen is unrealisable.
- **The magnitude is physiologically negligible.** On the alveolar gas equation
  the ceiling moves from 663.0 to 662.7 mmHg (0.3 mmHg); the paper writes that
  ceiling as "≈663".
- **The `clamped` flag cannot see it**, by construction: its four patterns are
  `SetupPatient.cpp` rejection strings (`src/detector.py::check_clamped`).

---

## 3. The disclosure question — DECIDED AND APPLIED 2026-08-13

> **Resolution.** The author chose to disclose, without touching the detector,
> the classifications, or H2. Applied the same day:
>
> - **`paper.tex` §2.1** — the binary sentence was replaced by what was
>   measured: *"the preregistered `clamped` category remained empty at setup
>   (0 / 1,280 across every cell). Pulse does make one explicit downstream
>   adjustment: where FiO₂ = 1.0 was requested and the ventilator action was
>   reached, the ventilator model caps the inspired oxygen fraction at 0.9996
>   — the ambient mixture already carries CO₂ at 4 × 10⁻⁴, so a fraction of
>   exactly 1.0 cannot be composed — with a logged error on all 195 runs
>   concerned (Supplement §S3.3)."*
>   Two deliberate wording choices: **"the preregistered `clamped` category
>   remained empty"** rather than "silent clamping never happens", because the
>   detector reads rejection strings and cannot by itself establish an absence
>   of substitution — the same circularity `65c1cc9` had removed from §2.2; and
>   **"the ventilator action was reached"**, because 208 runs request
>   FiO₂ = 1.0 while 195 reach the action.
> - **`supplement.tex` §S3.3** (`sec:s3-clamp`, where the flag's patterns are
>   defined) — a paragraph carrying the verbatim log line, the mechanism, the
>   208 / 195 / 13 split, the 0.04 %, the 663.0 → 662.7 mmHg check, and the two
>   non-consequences (no reclassification; H2 untouched).
> - **Removed and not replaced:** *"Pulse rejects an out-of-range input loudly,
>   with a setup error, instead of quietly bending it back into range."* The
>   sweep submits no out-of-envelope value (§2.2 of
>   `audit/silent_clamping_instrument.md`), so the paper cannot generalise from
>   it; the measured setup-layer facts remain stated in §2.1's H2 passage.
> - **Not done, by decision:** no change to `src/detector.py`, no run
>   reclassified, `≈663 mmHg` kept (662.7 rounds to the same approximation).
>
> Verified after the edit: audit exit 0 (382/382 · 94/94 · 26/26); both PDFs
> rebuilt; render-probed — `paper.pdf` p.8 carries the new sentence and
> resolves the cross-reference to "Supplement § S3.3", the string
> "quietly bending" appears on none of its 35 pages, the supplement paragraph
> renders on p.7 inside §S3.3, and both LaTeX logs report zero undefined
> references.
>
> **Guarded, same day.** `scripts/audit_fio2_adjustment.py` rebuilds every
> figure from the run configs and logs into the committed artefact
> `results/fio2_adjustment_provenance.csv` (1,280 rows: requested FiO₂, whether
> the ventilator action was reached, whether the adjustment fired, its value),
> and `check_fio2_adjustment()` in `scripts/audit_claims.py` binds them in
> **17 checks**. It re-derives the two negative facts rather than restating
> them — that no run below FiO₂ = 1.0 is ever adjusted, and that the 13
> unadjusted runs at 1.0 are unadjusted *because they never reach the action* —
> and it re-derives the alveolar ceiling arithmetic (663.00 and 662.71 mmHg)
> instead of matching the printed strings. The published sentences are pinned
> as **phrases on whitespace-normalised text**, not as bare numbers: "195"
> occurs 2 / 3 / 9 times across the three documents, and every phrase spans a
> line break in the hard-wrapped monograph.
>
> Calibrated in four directions, each injection verified independently before
> the result was believed: a substituted value changed to 0.999 → 3 FAIL; one of
> the 13 marked as having reached the action → FAIL; a published phrase drifted
> by one digit (662.7 → 662.8) → FAIL; the artefact removed → FAIL, with no skip
> path. All restorations verified by MD5 rather than by trusting the copy.
>
> ⚠️ **A defect in the guard itself, found by that calibration and fixed:** the
> three derived checks (relative adjustment, both ceilings) sat inside
> `if len(values) == 1`, so a degraded artefact made the guard report **14
> checks instead of 17** — three checks vanishing rather than failing, the
> "skip counted as pass" pattern. They now fail explicitly and the count is
> constant.
>
> **The availability limit is unchanged:** `data/runs/full_sweep/**` is
> gitignored, so the artefact and guard make the figures auditable in-repo, but
> the re-derivation runs only where the logs exist.

### The question as it was originally posed (kept)

`preprint_npj/paper.tex:198` reads:

> silent clamping never happens (0 / 1,280 across every cell): Pulse rejects an
> out-of-range input loudly, with a setup error, instead of quietly bending it
> back into range.

**This sentence is not falsified**, and the claim should not be described as
wrong: the phenomenon above is loud, and FiO₂ = 1.0 is not an out-of-range
input. What the sentence does is offer a **binary** — reject loudly, or bend
quietly — that omits the third behaviour the engine actually exhibits on 195 of
the 1,280 published runs: **accept, adjust by 0.04 %, and say so.**

For an atlas whose subject is where the engine bends operational inputs, that
omission is a disclosure question. The sentence occurs **once**, in `paper.tex`
only (0 occurrences in `supplement.tex` and `manuscript.md`).

Two things that should **not** be done without deliberate discussion:

1. **Do not add this string to `check_clamped`.** The flag's trigger conditions
   are locked at preregistration; widening them post hoc would change a
   preregistered instrument and would reclassify 195 published runs.
2. **Do not restate H2.** H2 concerns silent clamping; this is not silent.

---

## 4. Two observations outside this question, recorded so they are not lost

Both surfaced while enumerating every distinct `[ERROR]` line of the 1,280 logs.
Neither was investigated.

- **`Ventilator driver pressure or flow must be set. Using a pressure of 0.`**
  — 17 runs, once each (`MechanicalVentilatorModel.cpp:450`). 16 of the 17 are
  S4 (severe ARDS), one is S3_F; they span every PEEP and FiO₂ level, so this
  is not tied to a submitted value. It is an internal driver state, not a
  submitted input, but it is the engine substituting a default and continuing.
- **`Pulse needs stabilization criteria, none provided in configuration file`**
  — exactly 20 runs, i.e. the divergence count, which invites a wrong reading.
  In `S1_M_0157` the order is: `Could not converge to provided Convergence`
  (1025.02 s) → `TidalVolume is not converging` → **then** the criteria message.
  It is **downstream of** the convergence failure, not its cause, so it does not
  disturb the published blood-volume mechanism (whose evidence is the 20 → 0
  dose-response, not a log line).

## 5. Inventory of every distinct `[ERROR]` in the 1,280 published logs

| count | message |
|---:|---|
| 1,280 | `Unable to find substance directory : ./` (benign path notice, every run) |
| 195 | `FiO2 setting + ambient fractions other than N2 is greater than 1.0. Setting FiO2 to max value of 0.9996.` |
| 20 | `Could not converge to provided Convergence` |
| 20 | `Pulse needs stabilization criteria, none provided in configuration file` |
| 17 | `Ventilator driver pressure or flow must be set. Using a pressure of 0.` |
| 19 lines | `TidalVolume`/`OxygenSaturation is not converging` (stabilization convergence; line count, not run count — the other rows are one line per run) |
