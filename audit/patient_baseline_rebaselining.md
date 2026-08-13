# Does Pulse keep the swept patient baselines at their submitted values?

**Opened and measured 2026-08-13. Status: MEASURED — no document, flag or
number was modified.** Disclosure is an author decision and is drafted, not
applied, in §7.

Found while verifying `audit/silent_clamping_instrument.md` §3. It is a
different question from that register's, and is filed separately for that
reason: §3 asks whether Pulse alters a value **at ingestion** (answer: no,
Δ_setup = 0 on 10,160 contracts). This register asks what happens to the
patient *baseline fields* **after stabilization and before the recorded
window**.

Scope: the four swept patient inputs (HR, RR, SBP, DBP), plus
`TidalVolumeBaseline` because Pulse's own source flags it.

---

## 1. What the source does

`CardiovascularModel::AtSteadyState()`
(`src/cpp/engine/common/system/physiology/CardiovascularModel.cpp:822`, local
`REL_4_3_2` clone) overwrites four patient baseline fields with the **measured**
values reached at the end of a stabilization stage (`:831-834`):

```cpp
m_data.GetCurrentPatient().GetHeartRateBaseline().Set(GetHeartRate());
m_data.GetCurrentPatient().GetDiastolicArterialPressureBaseline().Set(GetDiastolicArterialPressure());
m_data.GetCurrentPatient().GetSystolicArterialPressureBaseline().Set(GetSystolicArterialPressure());
m_data.GetCurrentPatient().GetMeanArterialPressureBaseline().Set(GetMeanArterialPressure());
```

Three properties of this block matter, and they are not symmetrical:

| field | overwritten at | source |
|---|---|---|
| HR, SBP, DBP, MAP baselines | **both** stabilization stages | `CardiovascularModel.cpp:831-834` |
| `TidalVolumeBaseline`, `InspiratoryReserveVolume` | **initial stage only** (`if (state == AtInitialStableState)`) | `RespiratoryModel.cpp:591-601` |
| `RespirationRateBaseline` | **never re-written after setup** | only non-test write is `SetupPatient.cpp:573` |

- The single guard on the cardiovascular block is
  `!(state > AtInitialStableState && HasDehydration())`. The atlas applies no
  dehydration condition, so the overwrite always executes.
- When the engine state is `Active` — the recorded window — the same method
  **prints only** (`typeString = "Starting "`). The fields are therefore
  re-baselined once, before recording, and then held.
- Pulse says so itself: `SetupPatient.cpp:707` carries the comment
  `//This is overwritten after stabilization`.
- Call sequence (`src/cpp/engine/common/controller/Controller.cpp:505-538`):
  resting stabilization → `m_InitialPatient->Copy(*m_CurrentPatient)` →
  conditions applied → `AtSteadyState(AtInitialStableState)` → condition
  stabilization if any → `AtSteadyState(AtSecondaryStableState)`.
  `AtSteadyState(AtSecondaryStableState)` is called **unconditionally**, which
  is why S1 runs also print a "Secondary Stabilization Homeostasis" line
  although they apply no condition.

The homeostasis log lines print `GetHeartRate()` etc. (`:857-864`), i.e. the
same measured values that were just written into the baseline fields.

---

## 2. Measurement across the published sweep

Per run: submitted HR (`config.json` → `baselines.hr`) versus the HR reported at
the end of stabilization (`Secondary Stabilization Homeostasis: Patient heart
rate`, falling back to the initial-stage line when no secondary line exists).

| cell | n measured | mean \|ΔHR\| (bpm) | max \|ΔHR\| (bpm) | runs > 5 bpm |
|---|---:|---:|---:|---:|
| S1_F | 160 | **0.00** | **0.00** | 0 |
| S1_M | 156 | **0.00** | **0.00** | 0 |
| S2_F | 160 | 14.46 | 35.74 | 160 |
| S2_M | 156 | 13.31 | 29.22 | 156 |
| S3_F | 160 | 82.90 | 105.40 | 160 |
| S3_M | 156 | 82.74 | 105.40 | 156 |
| S4_F | 160 | 84.05 | 105.40 | 160 |
| S4_M | 156 | 82.05 | 105.40 | 152 |

**Reading.** Without a condition (S1), the submitted heart rate survives
stabilization **exactly**, on 316 runs. With an ARDS condition it does not: the
value the engine carries into the recorded window is up to **105.40 bpm** away
from the submitted one. In S4 the stabilized HR spans **111.493 – 195.4 bpm**
for submitted values of 50 – 110 bpm. The largest single deviation is submitted
90.0 → 195.4 (`S3_F_0153`, `S3_F_0154`, `S3_F_0155`). A stabilized rate near
195 bpm in an 18-year-old is extreme but not outside a modelled compensatory
tachycardia; it is a pre-ventilation stabilization state, not a reported result.

**Worked example, `S3_M_0007`.** Submitted HR 70 → setup patient block
`"HeartRateBaseline": 70` → `Initial Stabilization Homeostasis: Patient heart
rate = 70` → ARDS applied → `Secondary Stabilization Homeostasis: 151.377` →
recorded window mean HR ≈ 138. The log also shows `Activating Baroreceptors`
only at the end of stabilization (Pulse-internal 789.48 s), which is consistent
with the exact-zero S1 result: during stabilization the rate sits at its
baseline.

### Method, instruments and limits

Two independent pipelines agree:

```bash
# instrument 1 — join by run directory
{ grep -rn --include=config.json '"hr":' data/runs/full_sweep;
  grep -rn --include=pulse.log "Stabilization Homeostasis: Patient heart rate" \
       data/runs/full_sweep; } | awk '…'   # table above

# instrument 2 — per-run loop, S3_F, sorted by |Δ|
for d in data/runs/full_sweep/S3_F/S3_F_*; do … done | sort -rn | head
# 105.400  S3_F_0155  90.0 → 195.4
```

and a positional check on S1_F (160 pairs, **0 mismatches** between submitted
and stabilized HR).

Limits, all of them stated rather than smoothed:

1. **16 runs carry no homeostasis line at all** and are outside the measurement;
   4 further runs (S4_M) have the initial-stage line only and were compared on
   that stage, which **understates** their Δ. These 20 are the divergence
   cluster. This is why S4_M reads 82.05 against S4_F 84.05 — a measurement
   artefact, **not** a sex difference.
2. Pulse prints ~6 significant digits; "0.00" means agreement to that precision.
3. Only **HR** was quantified. SBP, DBP and MAP are overwritten by the same
   block and were **not** measured run-by-run.
4. The shell pipelines above are recorded so the numbers are re-derivable. They
   are **not** a guard: no layer of `scripts/audit_claims.py` watches them.

---

## 3. What this is not

- **Not a clamp.** The submitted values are honoured at ingestion: Δ_setup is
  exactly zero on all 10,160 parsed contracts
  (`audit/silent_clamping_instrument.md` §6.3). What changes afterwards is the
  physiological consequence of the condition the scenario applies.
- **Not a defect in the Morris design.** The elementary effect is computed
  between a submitted input and a recorded output; the re-baselining is part of
  the engine's response, not a corruption of the design. What it changes is the
  *reading*: the swept patient values are setup interventions, not setpoints
  held against the conditions applied afterwards.
- **Not visible to the atlas wrapper's own log line.**
  `engine/run_atlas_engine.py:177` prints `get_initial_patient()`, the patient
  copied **before** conditions are applied, so it reports the pre-condition
  state by construction. (Unexplained and not investigated: it printed
  `HR=70.01` for `S3_M_0007` where the engine's initial-stage line reads `70`.)

---

## 4. Does any published number depend on the re-baselined fields?

**No, as far as measured.** Every analysis artefact derives from `output.csv`
(engine data requests), `config.json` (requested values) or the setup-time
patient block of `pulse.log`. A grep over `src/`, `scripts/` and `engine/`
finds no consumer of the post-stabilization baselines: the only
`*Baseline` hits are the deliberate `BloodVolumeBaseline` overrides of S018,
the wrapper's *setter* for the submitted HR (`run_atlas_engine.py:130`) and the
cosmetic print at `:177`. The traffic-light rule likewise compares clean-run
**output** means against the (S1, M) cell, not baseline fields.

---

## 5. Does any manuscript sentence claim the baselines stay fixed?

**No.** Measured 2026-08-13 across `paper.tex` and `supplement.tex`: the three
"held fixed" loci are Webb's pressure-mode study (`paper.tex:130`), the Morris
design in the Table 1 caption (`:175`, "within a trajectory, each simulation
holds all seven inputs fixed" — true of the submitted configuration, which is
never changed mid-run) and the bootstrap (`:398`); the supplement's "set point"
(`:164`) is the metabolic-rate regulation target. **Nothing to correct.** A
disclosure would be an addition, not a repair.

---

## 6. Where this already appears, indirectly

The paper reports the consequence without naming the mechanism: §2.6
characterises the decoupling between input HR and output HR, and the
traffic-light map puts the S3/S4 HR cells in the non-green classes. This
register supplies the mechanism behind that observation.

---

## 7. Candidate disclosure — DRAFTED, NOT APPLIED

For the author. If adopted, Methods (not Results), one sentence:

> Pulse re-baselines the patient's heart-rate, systolic, diastolic and mean
> arterial pressure baseline fields to the stabilized physiological state at
> the end of each stabilization stage, before the recorded window begins; they
> are then held for the recorded run. The swept patient values are therefore
> setup interventions, honoured at ingestion, rather than setpoints maintained
> against the conditions applied afterwards.

Conditions attached to adopting it:

1. **No number from §2 may enter the manuscript until it is re-derived by a
   committed script and bound to a guard** (`check_*()` in
   `scripts/audit_claims.py`, not a ledger anchor — a guard has its own counter
   and does not cascade onto the 25 cited occurrences of the anchor total).
2. If the sentence quantifies anything, SBP/DBP/MAP must be measured too
   (limit 3 above).

---

## 8. Open questions

1. Same measurement for SBP, DBP and MAP — not done.
2. Does the initial-stage `TidalVolumeBaseline` overwrite matter anywhere? The
   atlas's tidal-volume input is the *ventilator* setting, so it touches no
   swept input directly.
3. Why does the wrapper's `get_initial_patient()` HR print 70.01 where the
   engine's initial-stage line prints 70 (`S3_M_0007`)? A 0.01 bpm residual,
   unexplained, no known consequence.
