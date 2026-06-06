# Pulse Reliability Atlas — Preregistration

**Originally committed:** 2026-04-19 (as PulseProbe hackathon).
**Amended:** 2026-04-22 — rescoped from 7-day hackathon to methods paper. See revision log below.
**Purpose:** lock the analysis plan before any data is collected, so the final preprint can be compared against this document to verify no plan-changing-after-seeing-data.

---

> **ERRATUM — 2026-05-19 (terminology only, no design change).**
>
> The phrase "Pulse standard" applied to the male and female surrogates
> in this document (e.g., §Revision log "Pulse standards", §H4 "Pulse
> standard patients", §Patient surrogates "(Pulse standard male)" /
> "(Pulse standard female)") is, on later source-level audit, a
> **misnomer**. The two surrogates used in the atlas — M = 18 yr /
> 67.3 kg / 180 cm and F = 18 yr / 56.2 kg / 163 cm — are not Pulse's
> source-code "Standard" patients. Their actual provenance is:
>
> - **Weights** (67.3 kg M, 56.2 kg F): CDC 50th-percentile
>   weight-for-age values at 18 years (216.5 months), inherited from
>   the companion `Pulse_translation_new` pediatric-translation
>   pipeline.
> - **Female height** (163 cm): CDC P50 stature, coincidentally
>   identical to Pulse's internal `heightStandardFemale_cm = 163.0`
>   (`SetupPatient.cpp` L75).
> - **Male height** (180 cm): a researcher-fixed rounded value chosen
>   to yield a healthy baseline BMI of 20.8. It is **not** Pulse's
>   internal `heightStandardMale_cm = 177.0` (`SetupPatient.cpp` L72)
>   and is ≈ 3 cm above the CDC P50.
>
> The numeric definitions in this document are correct and unchanged;
> only the label "Pulse standard" was inaccurate. The final manuscript
> uses the term **"reference surrogate"** instead, and the full
> engine-source comparison is in manuscript §2.3 and Appendix B.5. The
> original wording below is preserved verbatim for preregistration
> integrity.

---

## Revision log

**2026-04-22 amendment.** Rescope from PulseProbe hackathon deliverable to standalone methods paper (first publishable output in PhD series). Changes:
- Scenarios extended from 2 primary + 1 optional → **4 fixed** (healthy + 3 ARDS severities).
- Patient surrogate extended from male-only → **both male and female** (Pulse standards).
- Inputs reduced from 8 → **7** (MAP removed; derived from SBP/DBP as `DBP + (SBP−DBP)/3`). MAP was redundant with SBP+DBP and caused constraint-violation noise during independent sampling.
- CSV sample interval reduced from 30 s → **5 s** (13 points in final 60 s). Enables meaningful variance, flatline, and drift detection at steady state.
- Flags extended from 2 → **4**: added `implausible` (physiology bounds check) and `not_steady_state` (flatline + variance + drift).
- Sobol trigger: made explicit conditional rule on Morris σ/μ* ratios (was vague "Mode B/C bolt-on").
- Pilot gate: explicit numeric criteria (was "diagnose and adjust").
- Drift detection: **not** p-value based. Uses per-variable clinical effect-size thresholds on linear-regression slope × 60 s. Rationale in §Flags.

No data had been collected at the time of this amendment; preregistration integrity is preserved.

---

## Research question

Where does the Pulse Physiology Engine (v4.3.1) behave reliably, where does it silently clamp inputs, and where does its solver diverge — across the adult operational envelope relevant to critical care, for both sexes?

## Primary hypotheses

- **H1.** A small subset of inputs dominates each output's variance (skewed sensitivity). Specifically: for each of HR, MAP, Vt-delivered, SpO2, PaO2, PaCO2, the top-3 inputs (Morris μ*-ranked) account for ≥50% of summed μ*.
- **H2.** Silent clamping occurs for a measurable fraction of inputs sampled from plausible adult-ICU ranges. Specifically: ≥5% of the Morris sample hits at least one silent clamp.
- **H3.** At least one solver-divergence zone exists outside the previously characterized ARDS zone (0.91–0.945) within the 7-input adult envelope.
- **H4.** Male and female Pulse standard patients differ in reliability behavior (clamping, divergence, or Morris μ* ranking) on at least one output. Direction of difference is not prespecified — this is the **first** sex-specific comparison for Pulse.

## Design

- **Simulator:** Pulse 4.3.1 via Docker image `pulse-pediatric-engine:latest` (local build) or upstream `kitware/pulse:4.3.1`.
- **Ventilator mode:** VC-AC only (validated best, Webb 2023).
- **Simulation length:** 120 s total. Steady-state window = final 60 s (t = 60–120 s).
- **CSV sample interval:** 5 s → **13 points in steady-state window** (t = 60, 65, …, 120).
- **Patient surrogates:**
  - **Adult male:** age 18, weight 67.3 kg, height 180 cm (Pulse standard male).
  - **Adult female:** age 18, weight 56.2 kg, height 163 cm (Pulse standard female).

## Inputs swept (7)

MAP is **derived** from SBP/DBP (DBP + (SBP−DBP)/3), not swept independently.

| Input | Range | Units | Justification |
|---|---|---|---|
| HR baseline | 50–110 | bpm | Pulse init acceptance (verified E29, 11/11 Docker runs) |
| SBP baseline | 90–120 | mmHg | Pulse init acceptance (E10) |
| DBP baseline | 60–80 | mmHg | Pulse init acceptance (E10); pulse-pressure ratio DBP/SBP ≤ 0.75 enforced |
| RR baseline | 8–20 | bpm | Pulse init acceptance (E28, 9/9 Docker runs) |
| Vt target | 300–800 | mL | Spans ARDSnet 6 mL/kg to pre-ARDSnet 10 mL/kg for 67-kg adult |
| FiO2 | 0.21–1.0 | fraction | Room air to pure O2 (FiO2=1.0 verified non-crashing, E20) |
| PEEP | 0–20 | cmH2O | Clinical range from spontaneous to high PEEP |

Ranges come from: our own boundary probes (E10, E28, E29), ARDSnet protocol, and clinical practice. **Ranges are a commitment** — they will not change after data collection.

## Scenarios (4)

| ID | Condition | ARDS impairment | Rationale |
|---|---|---|---|
| S1 | Healthy ventilated adult | 0.00 | Reference envelope |
| S2 | Mild ARDS | 0.26 | PALICC-2 mild (E6 calibrated) |
| S3 | Moderate ARDS | 0.60 | PALICC-2 moderate (E6 calibrated) |
| S4 | Severe ARDS | 0.95 | Above 0.91–0.945 instability zone (E6 + E10) |

## Outputs measured (6) + flags (4)

### Outputs (steady-state mean over final 60 s, 13 samples)

| Output | Source | Purpose |
|---|---|---|
| HR | Pulse CV system | Cardiovascular response |
| MAP | Pulse CV system | Cardiovascular response |
| Vt delivered | Pulse vent system | Ventilator fidelity |
| SpO2 | Pulse blood chemistry | Gas exchange |
| PaO2 | Pulse blood chemistry | Gas exchange |
| PaCO2 | Pulse blood chemistry | Gas exchange |

### Flags (per run, defined in `src/detector.py`)

1. **`clamped`** — Pulse log contains rejection strings (e.g. "out of range"); setup values silently changed between requested and applied.
2. **`diverged`** — any of: NaN/Inf in CSV, missing CSV, non-zero exit code, simulation did not reach t = 120 s.
3. **`implausible`** — steady-state mean outside **hard physiological bounds** (see table below). Values within these bounds are plausible; values outside are not.
4. **`not_steady_state`** — the final 60 s window fails at least one of:
   - **Flatline:** std(values) < 0.01 × |mean(values)| **AND** mean is within **0.1%** of a hard bound (detects solver pinned numerically to extreme). Tolerance tightened from 1% → 0.1% on 2026-04-22 after detector validation on existing Pulse runs showed that healthy SpO2 (≈0.996) sits naturally within 1% of the upper bound, producing physiological false positives. 0.1% keeps genuine numerical pinning (mean = bound to float precision) flagged without conflating ceiling physiology.
   - **Variance too high:** coefficient of variation > **5%** (output is not settled).
   - **Drift:** linear regression on 13 points: |slope × 60 s| exceeds per-variable clinical threshold (see table). R² logged as diagnostic metadata but **not** used as a threshold.

### Hard physiological bounds (for `implausible` flag)

| Output | Lower | Upper | Source |
|---|---|---|---|
| HR | 20 | 220 | Physiological extremes; below/above incompatible with life [Marino 2013 Ch.5; Marini & Dries 2018 Ch.1] |
| MAP | 30 | 180 | Shock / hypertensive crisis bounds [Lower: Singer 2016 / Sepsis-3 organ-perfusion threshold; Upper: Mancia 2023 ESH hypertensive emergency] |
| Vt delivered | 50 | 1500 | Technical range (below 50 mL = below anatomical dead space, no alveolar ventilation [West & Luks 2020 Ch.2]; above 1500 mL = ~4× ARDSnet [Brower 2000] / equipment impossibility [Marino 2013 Ch.26]) |
| SpO2 | 50 | 100 | SpO2 < 50 ↔ PaO2 ≈ 27 mmHg on the Severinghaus 1979 dissociation curve, below cellular O2 extraction; 100 is hemoglobin saturation ceiling [Severinghaus 1979; Marini & Dries 2018 Ch.1] |
| PaO2 | 20 | 600 | 20 mmHg = severe hypoxemia floor (SpO2 ≈ 0.30, lethal in minutes) [Severinghaus 1979; Berlin Definition / ARDS Task Force 2012]; 600 mmHg = conservative classifier ceiling below alveolar-gas-equation ~663 mmHg [West & Luks 2020 Ch.5] -- supplementary HARD_BOUNDS_PHYSIOLOGICAL at 700 in atlas §3.8 |
| PaCO2 | 10 | 120 | 10 = profound hypocapnia (respiratory alkalosis); 120 = CO2 narcosis floor for survival [Marino 2013 Ch.21; West & Luks 2020 Ch.4] |

**Documentation amendment 2026-05-21:** Literature citations for the
bounds in the table above added in the manuscript bibliography
(`preprint/references.bib` + manuscript §2.6 table). **No threshold
value was changed.** Original qualitative justifications retained verbatim
inside the Source column with citation keys appended; the bounds are
unchanged from the 2026-04-22 lock.

### Drift thresholds (per-variable, clinical effect size)

Rationale: Pulse outputs are high-frequency; p-value on linear slope would be significant for microscopic drifts at 13 points. Thresholds are clinical (what a clinician would consider "still changing meaningfully").

| Output | Max |Δ| over 60 s | Units |
|---|---|---|
| HR | 5 | bpm |
| MAP | 5 | mmHg |
| Vt delivered | 50 | mL |
| SpO2 | 2 | % |
| PaO2 | 15 | mmHg |
| PaCO2 | 5 | mmHg |

## Sampling method

**Primary:** Morris elementary effects via SALib (`morris.sample`, trajectories=20, levels=4).
- N per scenario per sex = trajectories × (inputs + 1) = 20 × 8 = **160 runs**.
- 4 scenarios × 2 sexes = **1,280 Morris runs**.
- Plus pilot: 20 runs (S1 male only) before committing to the full sweep.

**Rationale:** Morris delivers ranked sensitivity (μ*, σ) efficiently at this input count. 1,280 runs is laptop-feasible via 3× parallel Docker (~5 h compute on i5-11400H).

**Sobol bolt-on (conditional).** For each output in each scenario-sex cell, the top-3 Morris μ*-ranked inputs are evaluated against their σ/μ* ratio:

- σ/μ* ≤ 0.4 → linear / monotonic → Morris result is sufficient, **no Sobol**.
- σ/μ* ≥ 0.6 → strong interactions or nonlinearity → **Sobol on that input**.
- 0.4 < σ/μ* < 0.6 → gray zone. Run Sobol only if interpretation matters for the preprint.

Sobol cost estimate: base sample 64 × (2 × k + 2) where k = inputs promoted. Budget envelope: ≤1,500 extra runs.

## Pilot gate (must pass all before full sweep)

20 pilot runs on scenario S1, male surrogate, Morris-sampled. Proceed only if:

1. **Success rate ≥50%** — i.e. `diverged` ≤ 10/20. Otherwise diagnose input ranges.
2. **Detector self-consistent** — no run is flagged both `clamped` and `implausible` from the clamped value alone (would indicate bounds mis-configured).
3. **Sample interval confirmed** — inspect one CSV: 13 rows in t ∈ [60, 120]. If fewer, sample interval is wrong.
4. **Log parser works** — at least one `clamped` flag is raised on a pilot run that touches an extreme boundary; otherwise the log regex is wrong.
5. **Reproducibility** — rerun 2 pilot points and confirm output-level bit-exact or within 1e-6 relative tolerance for all 6 outputs. Pulse is deterministic; reruns must match.

If any fail, pause, diagnose, log amendment, re-pilot. Do **not** silently edit pilot criteria.

## Analysis plan

1. **Pre-filter counts.** Per scenario-sex cell: N total, N clamped, N diverged, N implausible, N not_steady_state, N clean. Report table.
2. **Morris indices** (μ*, σ) per input per output per scenario-sex cell. Rank inputs by μ*. **Use only `clean` runs** (no flag raised) for Morris — flagged runs violate the Morris sample structure and would contaminate indices.
3. **Sobol** on promoted inputs (per σ/μ* rule above). Report S1, ST.
4. **Clamp map.** Which input combinations trigger silent clamping (per input, per scenario-sex cell). Report as 2D heatmap in input-pair space.
5. **Divergence map.** Same treatment for `diverged` flag.
6. **Sex comparison (H4).** For each output: Wasserstein distance between male vs female clean-run distributions, per scenario. Rank-correlation (Spearman) between male μ* and female μ* vectors per output. Report all; no alpha threshold since this is descriptive.
7. **Reliability classification.** Per output per input cell: green (<10% deviation from cell baseline), yellow (10–30%), red (>30% or any flag raised).

## Stop rules

- Pilot gate failure (see §Pilot gate). Stop → diagnose → amend.
- Any single input's sweep range triggers ≥80% clamping in the full sweep: document, **continue**; this IS the finding.
- Docker instability (> 5% of runs crash on container level, not Pulse level): pause, check host resources, resume.

## What we do NOT commit to here

- Streamlit dashboard (post-atlas deliverable, not preregistered analysis).
- Paper 2 pediatric patches (separate PhD output, out of scope for this preprint).
- Specific p-value thresholds for hypothesis tests. Morris is a screening method, not a hypothesis test. H1–H4 use effect-size counts and rank statistics (see §Analysis plan).

## Deliverables

1. Open dataset on Zenodo (CSV + Parquet).
2. Methods paper preprint on arXiv.
3. Code on GitHub (this repo) under Apache 2.0.
4. Optional post-atlas: Streamlit dashboard.

## Amendments (append-only, no silent edits)

**2026-04-22.** Rescope from hackathon to methods paper. See revision log at top. No data was collected before this amendment; preregistration integrity preserved.

**2026-04-22-b.** Detector calibration amendment. Flatline-bound tolerance tightened from 1% → 0.1% of the relevant hard bound, after dogfooding the detector on 20 pre-existing Pulse runs in `Pulse_translation_new/data/engine_runs/`. Under the original 1% tolerance, 3 healthy runs with naturally-saturated SpO2 (≈0.995–0.996) were flagged as "flatline at extreme" — a physiological ceiling, not a solver pathology. Tightening to 0.1% limits the flag to genuinely pinned cases (mean exactly at bound). No atlas data had been collected. The validation script is at `scripts/validate_detector_on_existing_runs.py`.
