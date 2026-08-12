# Does the atlas measure the absence of silent input clamping?

**Opened** 2026-08-12. **Status: OPEN — read-only, nothing modified.**
Scope: the `clamped` flag (`src/detector.py::check_clamped`), the published
claim `0 / 1,280`, and preregistered hypothesis H2.

Loci under audit:

| document | locus | text |
|---|---|---|
| paper | `paper.tex:169` | "H2 predicted that at least 5 % of the Morris sample would hit a silent clamp; the observed rate is 0 of 1,280, so H2 is *not* supported: Pulse rejects an out-of-envelope setup input loudly or not at all." |
| paper | `paper.tex:371` | "`clamped` fires when Pulse's setup-rejection log contains any of 4 documented input-rejection patterns […], indicating that Pulse silently bent a setup input out of its acceptance band." |
| paper | `paper.tex:343` | "silent input clamping never occurs (0 of 1,280 runs)" |
| paper | `paper.tex:202` (Table 1 caption) | "No run was silently clamped: the `clamped` column is empty in all eight cells, 0 of 1,280." |

This register establishes facts. It changes no document, no flag and no number.

---

## 0. Correction to this register's own first draft

The first pass of this audit treated Pulse's `Resetting the target for
TidalVolume to Y` log line as a new discovery. **It is not.** It was found,
analysed and deliberately excluded during detector calibration, and the
reasoning is recorded in `preprint/manuscript.md:1124-1129`: an earlier
over-broad regex matched that line and produced 100 % false-positive `clamped`
flags, so it was replaced by four Pulse-specific setup-rejection patterns
calibrated on the S004 SBP = 140 boundary probe.

What survives is not "this was missed" but a narrower and still-open question,
stated in §3 below: whether that exclusion is *correct*.

---

## 1. What the instrument actually reads

`check_clamped(pulse_log)` matches regexes against Pulse's stdout/stderr. The
five current patterns (`src/detector.py`, post-2026-07-26 patch; the four-pattern
set classified the 1,280 published runs) all target **setup-rejection strings**
that `SetupPatient.cpp` emits when it refuses a baseline.

**Consequence.** The flag detects *loud rejection*. A genuinely silent
substitution writes no rejection string, so it cannot fire the flag. The
absence of silent clamping is therefore **inferred from the absence of a
rejection message**, not measured.

### 1.1 The positive control validates the other direction

`clamp_probe_sbp140` (S004) establishes:

> explicit rejection log ⇒ detector fires.

It does not, and cannot, establish:

> silent value substitution ⇒ detector fires.

The pilot gate named "clamp-regex reachability" (`paper.tex:371`) is a
reachability check on the first implication only.

---

## 2. The sweep rarely gives the instrument a chance to fire

Preregistered ranges (`preregistration.md` §Inputs swept) against the verified
acceptance gates (`CLAUDE.md` limitations 2, 5, 6):

| input | swept range | verified acceptance gate | headroom |
|---|---|---|---|
| HR | 50–110 bpm | 50–110 bpm | **none — the range IS the gate** |
| RR | 8–20 bpm | 8–20 bpm | **none — the range IS the gate** |
| SBP | 90–120 mmHg | ≤ 120 mmHg | none above |
| DBP | 60–80 mmHg | ≤ 80 mmHg, and DBP/SBP ≤ 0.75 | none above |
| Vt | 300–800 mL | no documented setup gate | n/a |
| FiO₂ | 0.21–1.0 | none (1.0 accepted) | n/a |
| PEEP | 0–20 cmH₂O | no documented setup gate | n/a |

For the four gated inputs the design never requests an out-of-envelope value.
`0 / 1,280` is therefore, for those four limits, **substantially a property of
the sampling design rather than a discovered property of the engine.**

This does not make H2 unreasonable *ex ante*: undocumented interactions,
internal projections or hidden constraints were plausible before the sweep.
It means the null result is weaker evidence about the four known gates than
its current phrasing suggests.

### 2.2 Correction: H2 never named out-of-envelope values

Verbatim, `preregistration.md:63`:

> **H2.** Silent clamping occurs for a measurable fraction of inputs sampled
> from **plausible adult-ICU ranges**. Specifically: ≥5 % of the Morris sample
> hits at least one silent clamp.

An earlier draft of §2 framed the objection as "the sweep never submits an
out-of-envelope value". H2 never asked it to. Its domain is *plausible
adult-ICU ranges*, and it predicts that Pulse silently bends values drawn from
inside that clinical range.

The objection survives, but only in a narrower and more defensible form: the
swept ranges were set to **Pulse's acceptance envelope**, which is narrower
than the clinical range H2 names. HR is swept 50–110 bpm because that is what
Pulse accepts, whereas a plausible adult-ICU heart rate reaches well beyond
110. H2 is therefore tested on the intersection of its stated domain with
Pulse's acceptance envelope, not on its stated domain.

**Consequence for wording.** Any H2 conclusion must be scoped to the swept
envelope. It cannot be generalised to "Pulse rejects an out-of-envelope setup
input loudly or not at all", because no out-of-envelope setup input was ever
submitted in the 1,280 runs.

### 2.3 The setup-time bounding is itself a post hoc reading

H2 says "silent clamp" and does not distinguish setup-time ingestion from
runtime controller behaviour. Bounding it to setup-time is defensible — the
`clamped` detector reads the setup log, and the manuscript operationalises the
flag on setup inputs throughout — but it is **an interpretive decision taken
after the data existed**, structurally identical to D2 in
`audit/preregistration_traffic_light_deviation.md`, where "any flag" was read
as the two hard flags. It should be declared in the same way and with the same
words: a reading, offered as such, not presented as what the hypothesis said.

### 2.1 The atlas wrapper does clip one input, and records it

`config.json` carries an `atlas_meta` block per run, e.g. `S1_F_0000`:

```json
"dbp_requested": 80.0, "dbp_applied": 75.0, "dbp_was_clipped": true
```

This is the pulse-pressure clip, already characterised in Supplement §S3
(clip cost on diastolic elementary effects). It is **our** clip, applied
before Pulse sees the value, and it is recorded per run. It is named here only
so it is not confused with an engine-side clamp.

---

## 3. The open question: is the excluded log line "convergence" or "substitution"?

`Resetting the target for TidalVolume to Y, the last target value was Z`
appears in **1,280 / 1,280 run logs** (measured: `find … -name pulse.log | wc -l`
= 1280; `grep -rl … | wc -l` = 1280).

Measured requested-versus-final-target on four sampled runs:

| run | requested Vt | resets | last logged target | Δ vs requested |
|---|---:|---:|---:|---|
| S1_F_0000 | 300.0 mL | 14 | 300.59 mL | +0.2 % (returns to target) |
| S2_M_0100 | 800.0 mL | 84 | 728.17 mL | −9.0 % |
| S3_M_0007 | 633.3 mL | 100 | 516.23 mL | **−18.5 %** |
| S4_F_0042 | 800.0 mL | 152 | **0 mL** | **−100 %** |

Two defensible readings, and this register picks neither:

- **Reading A — control-loop behaviour, correctly excluded.** This is the VC-AC
  controller retargeting *during* the run, not a *setup* clamp. H2 and the
  `clamped` flag are about setup. The phenomenon is separately characterised as
  VC-AC tidal-volume dyssynchrony (main §2.2; trigger lockout collapses the
  delivered-Vt CV from 0.351 to 0.016), and its runs are caught by
  `not_steady_state`. Nothing is hidden.
- **Reading B — silent substitution of a user-set operational input.** A target
  moving from 633 mL to 516 mL, or to 0, is not obviously "normal solver
  convergence text". Under this reading the engine does bend a user-set input
  without an error, in every run, and the paper's "Pulse rejects an
  out-of-envelope setup input loudly or not at all" is scoped too widely.

**Not established either way by this audit.** Settling it requires deciding
whether "clamping" in H2 meant setup-time only. That is the author's call.

### 3.1 What must NOT be used to settle it

The tracked *output* Vt cannot prove the input was preserved. The atlas has
already established that Pulse's outputs evolve away from their inputs by
design (compensatory tachycardia decouples input HR from output HR, main §2.6).
The comparison has to be requested-value versus **instantiated/configured**
value, never versus a settled physiological output.

---

## 4. Good news: the instantiated state is already on disk, for all 1,280 runs

Each run directory holds `config.json` (requested), `pulse.log` (21 kB),
`output.csv`, `output_pulse_native.csv` and `run_meta.json`. The log contains
Pulse's own post-setup serialisation of the patient, including
`SystolicArterialPressureBaseline`, `DiastolicArterialPressureBaseline` and
`TidalVolumeBaseline`, plus an explicit tuning trace:

```
Tuning to patient parameters : HeartRate(bpm):110 Systolic(mmHg):100 Diastolic(mmHg):75
Successfully tuned circuit (No Tissues). Final values : HeartRate(bpm):110
    Systolic(mmHg):100.084 Diastolic(mmHg):75.531
```

Requested 100 / 75 versus instantiated 100.084 / 75.531 — a tuning residual of
0.08 and 0.53 mmHg on this run, not a clamp.

**This is the user's "Case 1": the applied values are already recorded.** An
exhaustive Δᵢ = xᵢ,applied − xᵢ,requested over all 1,280 runs and every gated
input is therefore computable **from artefacts already committed, with no
re-run of the sweep and no new Docker image.** That is the single highest-value
next step, and it would turn H2 from inferred to measured.

---

## 5. A wording defect that holds under either reading

`paper.tex:371` reads:

> `clamped` fires when Pulse's setup-rejection log contains any of 4 documented
> input-rejection patterns […], indicating that Pulse **silently** bent a setup
> input out of its acceptance band.

A present rejection message is by definition a **loud** rejection. The sentence
makes the flag's evidence contradict its stated conclusion. This is independent
of §3 and should be corrected whatever §3 concludes. **Not corrected here:** it
touches a Methods claim, so it is a stop-and-ask item.

---

## 6. Measurement pass 1 — raw results (2026-08-12)

`scripts/audit_input_instantiation.py`, run over the committed artefacts. No
re-execution of the sweep, no Docker image. Output:
`results/input_instantiation_long.csv`, 10,240 rows = 8 contracts × 1,280 runs.

**No verdict is recorded in this section.** The words "clamp", "no clamp" and
"H2 supported/refuted" are deliberately withheld until the distributions below
have been read.

### 6.1 The eight contracts

Extraction is keyed on (block, field). Respiration rate has two contracts
because it is two objects; `TidalVolumeBaseline` (patient) is never read, as it
is the patient's spontaneous Vt, not the ventilator setting.

| contract | block | field |
|---|---|---|
| `HR_patient_baseline` | `[Patient]` JSON | `HeartRateBaseline` |
| `RR_patient_baseline` | `[Patient]` JSON | `RespirationRateBaseline` |
| `SBP_patient_baseline` | `[Patient]` JSON | `SystolicArterialPressureBaseline` |
| `DBP_patient_baseline` | `[Patient]` JSON | `DiastolicArterialPressureBaseline` |
| `Vt_ventilator` | `[Action]` → `EquipmentAction.MechanicalVentilatorVolumeControl` | `TidalVolume` |
| `RR_ventilator` | idem | `RespirationRate` |
| `FiO2_ventilator` | idem | `FractionInspiredOxygen` |
| `PEEP_ventilator` | idem | `PositiveEndExpiratoryPressure` |

Layers: `sampled` = `morris_sample.parquet`; `wrapper_applied` =
`aggregated.parquet` `in_*`; `pulse_instantiated` = parsed from `pulse.log`.
Δ_wrapper = applied − sampled; Δ_setup = instantiated − applied. The runtime
layer is not measured in this pass.

### 6.2 Blocking assertions, all passed

- 1,280 `config.json` and 1,280 `pulse.log` present.
- The pulse-pressure clip fires on **exactly 35 points in each of the 8 cells**
  (= 280 / 1,280). Asserted per cell, not on the total: a total alone would
  survive a bug that moved clips between cells.
- The sampled→run mapping is row order, **proven** on 7,680 comparisons
  (6 unclipped inputs × 160 points × 8 cells), not assumed.

### 6.3 Result

| contract | parsed | missing | Δ_wrapper ≠ 0 | Δ_setup ≠ 0 | max abs Δ_setup |
|---|---:|---:|---:|---:|---:|
| `HR_patient_baseline` | 1280 | 0 | 0 | **0** | 0 |
| `RR_patient_baseline` | 1280 | 0 | 0 | **0** | 0 |
| `SBP_patient_baseline` | 1280 | 0 | 0 | **0** | 0 |
| `DBP_patient_baseline` | 1280 | 0 | **280** | **0** | 0 |
| `Vt_ventilator` | 1260 | 20 | 0 | **0** | 0 |
| `RR_ventilator` | 1260 | 20 | 0 | **0** | 0 |
| `FiO2_ventilator` | 1260 | 20 | 0 | **0** | 0 |
| `PEEP_ventilator` | 1260 | 20 | 0 | **0** | 0 |

Δ_setup is **exactly zero — not small, zero** — on all 10,160 parsed rows. The
set of distinct non-zero Δ_setup values is empty for every contract. Δ_wrapper
is non-zero on 280 rows and only for DBP: our clip, not Pulse's.

### 6.4 The 80 unparsed rows are 20 runs, and they are the 20 divergences

All 80 carry `missing_vent_block`: 20 runs × 4 ventilator contracts. Those 20
runs are **all `diverged`, all `exit_code ≠ 0`, all on the male reference
body**, distributed S1 = 4, S2 = 4, S3 = 4, S4 = 8. That is exactly the
divergence cluster of main §2.5 (20 male / 0 female), recovered here from log
*structure* rather than from the flags — an independent reconfirmation.

Their logs stop before the ventilator action is applied, so the four ventilator
contracts carry no value on those 20 runs.

> **Corrected 2026-08-12, same day, by the pass in §6.5.** This paragraph first
> read: *"the four ventilator contracts are unmeasured on precisely the 20 runs
> where the engine failed. This is the population in which a substitution would
> be most plausible, and it is the one this pass cannot see."* That was wrong,
> and wrong in the direction that overstates the gap. The timeline pass shows
> the 20 runs stop **before the ventilator action is ever submitted**: those
> four values were never offered to the engine, so there is no population in
> which an unobserved ventilator substitution could hide. `NOT_REACHED`, not
> `REACHED_BUT_UNOBSERVABLE` — a distinction that decides how the result may be
> stated. The superseded wording is quoted above rather than deleted, so the
> correction is auditable.

### 6.5 Where the 20 diverged runs stop — timeline pass

`scripts/audit_divergence_timeline.py`. Eight stage markers, each a literal read
out of a run that completed (S1_F_0000) in its emission order, never invented.
Every one of the 1,280 logs is assigned the last stage it reaches.

| # | stage | marker |
|---|---|---|
| 1 | `config_submitted` | `[Provided Patient]` |
| 2 | `patient_instantiated` | `[Patient]` |
| 3 | `circuit_tuning_started` | `Tuning to patient parameters` |
| 4 | `circuit_tuned` | `Successfully tuned circuit with tissue resistances` |
| 5 | `vent_setup_begun` | `Setting Up MechanicalVentilator` |
| 6 | `vent_action_ingested` | `"MechanicalVentilatorVolumeControl"` |
| 7 | `vent_connected` | `Ventilator connected (VC-AC)` |
| 8 | `airway_switched` | `Airway Mode : MechanicalVentilator` |

**Calibration.**
- Staircase contiguity **1,280 / 1,280**: no log ever shows a later stage while
  missing an earlier one, so the assumed ordering is not violated anywhere.
- Negative control: **1,260 / 1,260** non-diverged runs reach stage 8. A
  staircase exercised only on the failures would prove nothing about the order.

**Result: all 20 diverged runs stop at stage 5, identically.** None reaches
stage 6. All 20 carry both `Could not converge to provided Convergence` and the
wrapper's `RuntimeError: Pulse engine failed to stabilise for case …`, raised
inside `initialize_engine`.

Stage 5 is Pulse building its own equipment circuits during engine
initialisation; the *user's* ventilator action is submitted later, at stage 6.
The 20 failures are therefore **patient-stabilisation failures occurring before
ventilation**, not ventilation failures.

Two consequences worth separating:

1. **For this dossier.** The four ventilator contracts on those 20 runs are
   `NOT_REACHED`. Every input Pulse actually ingested was measured: the four
   patient contracts on 1,280 / 1,280 runs (the diverged ones reach stage 2),
   and the four ventilator contracts on 1,260 / 1,260 of the runs that reached
   ingestion. Δ_setup is exactly zero throughout.
2. **For the divergence cluster of main §2.5.** The 20 failing input vectors are
   indices **119, 157, 158, 159 in every one of the four scenarios**, plus 24,
   82, 137 and 138 in S4 only — and all 20 die at the same stage. That is a
   structural characterisation of the cluster obtained without re-running
   anything, and it is consistent with a blood-volume mechanism acting at
   patient setup rather than with anything ventilator-related. **Not pursued
   here**; recorded because it was measured.

The `Resetting the target for TidalVolume` lines present in these logs at
t ≈ 1,000 s are therefore Pulse's *spontaneous* tidal volume during
stabilisation, with no ventilator attached — a third confirmation that this
literal must never be read as the ventilator setpoint (§0, §6.1).

### 6.6 Calibration of the instrument — four positive controls

"Zero everywhere" is what a vacuous instrument returns, so it was calibrated
before being believed (`scratchpad/calibrate_instantiation.py`, read-only):

1. **Values vary and span the swept ranges.** HR 50–110, RR 8–20, SBP 90–120,
   DBP 60–80, Vt 300–800, FiO₂ 0.21–1.0, PEEP 0–20 — the preregistered ranges,
   4 Morris levels each (DBP shows 6 distinct values, the clip adding 67.5 and
   75.0).
2. **Decisive.** On the 280 clipped runs, sampled DBP is {73.33, 80.0} and our
   clipped value is {67.5, 75.0}. Pulse instantiated **{67.5, 75.0}** — equal
   to the clipped value on 280/280, equal to the pre-clip value on 0/280. The
   extractor therefore reads Pulse's number and tracks our input; it is not
   echoing the sampled value back.
3. **The arithmetic can fire.** Perturbing a comparison by +1 mL yields
   Δ = −1.0.
4. **The missing set is structural**, not a parser miss: §6.4.

### 6.7 What this pass does not establish

- Nothing about the 20 diverged runs' ventilator inputs — but §6.5 shows those
  values were never submitted to the engine, so this is an absence of an event,
  not an unobserved one.
- Nothing about the runtime layer: the VC-AC tidal-volume retargeting of §3 is
  posterior to ingestion and was excluded by design.
- Nothing about values the solver may use internally downstream of the stored
  configuration. The measurement is of what Pulse *recorded as configured*.
- Coverage is the sweep's own 4-level Morris grid per input, not a continuum,
  and never a value outside the acceptance envelope (§2).

---

## 7. Open questions carried forward

1. Did the four gated inputs ever land on a value Pulse altered at setup?
   Answerable now from §4's artefacts.
2. Is the `TidalVolume` target reset in scope for H2? Author's call (§3).
3. Is the S4_F_0042 reset-to-zero run flagged by another flag, and by which?
   Not checked.
4. Do PEEP and FiO₂ have undocumented setup gates? Not checked against
   `SetupPatient.cpp`.
