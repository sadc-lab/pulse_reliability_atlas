# PulseProbe — Preregistration

**Committed:** 2026-04-19 (Day 0, before hackathon opens).
**Purpose:** lock the analysis plan before any data is collected, so the final preprint can be compared against this document to verify no plan-changing-after-seeing-data.

---

## Research question

Where does the Pulse Physiology Engine (v4.3.1) behave reliably, where does it silently clamp inputs, and where does its solver diverge — across the adult operational envelope relevant to critical care?

## Primary hypotheses

- **H1.** A small subset of inputs dominates each output's variance (skewed sensitivity). Specifically: ≥50% of the variance for each output is explained by ≤3 inputs (Morris μ*-based ranking).
- **H2.** Silent clamping occurs for a measurable fraction of inputs sampled from plausible adult-ICU ranges (not just outliers). Specifically: ≥5% of the Morris sample will hit at least one silent clamp without being at the sampled distribution's tail.
- **H3.** At least one solver-divergence zone exists outside the previously characterized ARDS zone (0.91–0.945) within the 8-input adult envelope.

## Design

- **Simulator:** Pulse 4.3.1 (Docker image `pulse-pediatric-engine:latest`, built from Pulse source).
- **Ventilator mode:** VC-AC (validated best, Webb 2023).
- **Patient surrogate:** adult male, age 18, weight 67.3 kg, height 180 cm (Pulse standard male).

## Inputs swept (8)

| Input | Range | Units | Justification |
|---|---|---|---|
| HR baseline | 50–110 | bpm | Pulse init acceptance (verified E29) |
| MAP baseline | derived from SBP/DBP | mmHg | — |
| SBP baseline | 90–120 | mmHg | Pulse init acceptance (E10) |
| DBP baseline | 60–80 | mmHg | Pulse init acceptance (E10); pulse-pressure ratio DBP/SBP ≤ 0.75 |
| RR baseline | 8–20 | bpm | Pulse init acceptance (E28) |
| Vt target | 300–800 | mL | Spans ARDSnet 6 mL/kg to pre-ARDSnet 10 mL/kg for 67-kg adult |
| FiO2 | 0.21–1.0 | fraction | Room air to pure O2 (FiO2=1.0 verified non-crashing, E20) |
| PEEP | 0–20 | cmH2O | Clinical range from spontaneous to high PEEP |

Ranges come from: our own boundary probes (E10, E28, E29), ARDSnet protocol, and clinical practice. Ranges are a commitment — they will not change after data collection.

## Scenarios (2, primary)

- **S1 — Healthy ventilated adult.** No comorbidity. Used as reference envelope.
- **S2 — Moderate-ARDS ventilated adult.** ARDS impairment = 0.60 (calibrated, E6). Tests reliability under disease stress.

Optional third scenario (Mode C, cluster-only): **S3 — Severe-ARDS ventilated adult**, impairment = 0.95 (above the 0.91–0.945 instability zone).

## Outputs measured (6) + flags (2)

| Output | Source | Purpose |
|---|---|---|
| HR (mean, steady state) | Pulse CV system | Cardiovascular response |
| MAP (mean) | Pulse CV system | Cardiovascular response |
| Vt delivered (mean) | Pulse vent system | Ventilator fidelity |
| SpO2 (mean) | Pulse blood chemistry | Gas exchange |
| PaO2 (mean) | Pulse blood chemistry | Gas exchange |
| PaCO2 (mean) | Pulse blood chemistry | Gas exchange |
| `clamped?` | log parse | Silent input rejection |
| `diverged?` | CSV analysis | Solver failure (NaN, non-physiological values, non-completion) |

Steady-state = mean over final 60 s of a 120 s simulation (sample every 30 s).

## Sampling method

**Primary:** Morris elementary effects via SALib (`morris.sample`, trajectories=20, levels=4). Yields N = trajectories × (inputs + 1) = 20 × 9 = **180 runs per scenario**, total **360 runs** for S1+S2.

**Rationale:** Morris is the standard efficient screening method. It delivers ranked sensitivity (μ*, σ) without needing the full Sobol sample cost. With 8 inputs and 2 scenarios it fits the laptop budget.

**Optional Mode B/C bolt-on:** Sobol indices on the top-3 Morris-ranked inputs (not committed to here).

## Analysis plan

1. **Pre-filter:** separate successful, clamped, and diverged runs. Report counts for each.
2. **Morris indices** (μ*, σ) per input per output, per scenario. Rank inputs by μ*.
3. **Clamp map:** which input combinations trigger silent clamping. Report as heatmap.
4. **Divergence map:** which input combinations trigger solver failure. Report as heatmap.
5. **Reliability classification:** for each output in each input cell, assign green (<10% deviation from steady-state baseline), yellow (10–30%), red (>30% or diverged).

## Stop rules

- If pilot (first 20 runs) shows <50% success rate: pause, diagnose, adjust scenarios, re-pilot. Log all changes.
- If any input's sweep range triggers ≥80% clamping: document and continue; this IS the finding.

## What we do NOT commit to here

- Extended Sobol analysis, Mode C scenarios, live-simulator dashboard — these are bolt-ons that will be added only if safety allows (see scope rules in `CLAUDE.md`).
- **D6 pediatric-patches bonus chapter** — conditional, added only if Mode A is 100% locked by end of D5. Produces a `proposed_pediatric_patches.md` file with prioritized C++ diffs + literature citations for pediatric-friendly replacements of adult-fit Pulse formulas (BMR, blood volume, max HR, etc.). NOT compiled, NOT tested, NOT using real patient data. See CLAUDE.md for trigger rule and scope.
- Specific p-value thresholds. Morris is a screening method, not a hypothesis test.

## Deliverables

1. Open dataset on Zenodo (CSV + Parquet).
2. Streamlit dashboard (code on GitHub).
3. Preprint on arXiv.
4. 2-min demo video.

All under Apache 2.0.

## Amendments

Any change to this preregistration must be logged below with date, reason, and what was changed. No silent edits.

_(none yet)_
