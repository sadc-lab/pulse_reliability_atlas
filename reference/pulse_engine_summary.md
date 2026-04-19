# Pulse Physiology Engine — Condensed Summary for PulseProbe

**Purpose:** a self-contained briefing so a new Claude Code session in this directory has enough Pulse context to work without going back to `Pulse_translation_new/`. For deeper detail, see the full reference there.

---

## What Pulse is

Open-source, C++ whole-body physiology simulator (Kitware, Apache-2.0). Forked from BioGears in 2017 by the original BioGears core developers (Clipp, Bray, Webb). Current version: **4.3.1** (released Sept 2024).

Primary citation: **Bray et al. (2019)**, "Pulse Physiology Engine: an Open-Source Software Platform for Computational Modeling of Human Medical Simulation," *SN Comprehensive Clinical Medicine*, [DOI:10.1007/s42399-019-00053-w](https://doi.org/10.1007/s42399-019-00053-w).

**Self-described fidelity:** the [Pulse documentation](https://pulse.kitware.com/_nervous_methodology.html) calls it a *"low fidelity clinical approach... not necessarily for high fidelity predictive purposes."* Designed for real-time training, not patient-specific prediction.

**Speed:** ~5–15× real time depending on hardware.
**Timestep:** 20 ms.

---

## Architecture

**Zero-dimensional lumped-parameter circuits.** Same approach as BioGears, HumMod, Muse. Electrical-circuit analogues: resistors = vascular resistance, capacitors = compliance, pressure sources = heart / respiratory muscles.

**11 physiology systems:** Cardiovascular, Respiratory, BloodChemistry, Nervous, Renal, Endocrine, Energy, Drug, Gastrointestinal, Hepatic, Tissue.

**Equipment:** Mechanical ventilator, anesthesia machine, ECMO, bag-valve-mask, inhaler.

**Patient model:** adults aged 18–65 only. Hard-gated in `SetupPatient.cpp`.

---

## Validation quality (from Pulse's own documentation, male standard patient)

| Agreement | Count (of 474) | % |
|---|---|---|
| Good (<10% dev) | 397 | 83.7 |
| Fair (10–30% dev) | 51 | 10.8 |
| Poor (>30% dev) | 26 | 5.5 |

Ventilator modes (VC-AC validated best, Webb 2023):
- VC-AC Vt error: **0.07–2.25%** across healthy / restrictive / obstructive.
- PC-AC Vt error: **11–25%** (Pulse validation) to **24–59%** (our probing).

**Critical gap (Pulse FAQ, verbatim):** *"We have not performed a systematic forward propagation or inverse quantification of model uncertainty, nor have we conducted a formal sensitivity analysis."*

---

## Input acceptance boundaries (from our Pulse_translation_new probing)

| Input | Accepts | Rejects |
|---|---|---|
| Age | 18–65 yr | <18 (pediatric gate) |
| HR | 50–110 bpm | <50, >110 (E29, 11/11 match) |
| RR | 8–20 bpm | <8, >20 (E28, 9/9 match) |
| SBP | 90–120 mmHg | >120 (silent rejection + error msg) |
| DBP | 60–80 mmHg | >80 (silent rejection) |
| DBP/SBP ratio | ≤0.75 | >0.75 (pulse-pressure ratio gate) |
| FiO2 | 0.21–1.0 | — (1.0 verified non-crash, E20) |
| ARDS severity | 0.0–0.91, 0.945–1.0 | 0.91–0.945 (solver instability) |

---

## Surrogate patients (from Pulse_translation_new; use the same for PulseProbe)

- **Adult male:** age 18, weight 67.3 kg, height 180 cm.
- **Adult female:** age 18, weight 56.2 kg, height 163 cm.

---

## Docker image

- **Local build:** `pulse-pediatric-engine:latest` (5.54 GB, built from Pulse 4.3.1 source)
- **Upstream:** `kitware/pulse:4.3.1` (5.35 GB)

**Run syntax (verified on this machine 2026-04-19):**
```bash
MSYS_NO_PATHCONV=1 docker run --rm --memory=1g --cpus=3 \
  -v "$(pwd -W)/RUNDIR:/data" \
  pulse-pediatric-engine \
  --config //data/config.json \
  --output //data/output.csv
```

Notes:
- `MSYS_NO_PATHCONV=1` + double-slash `//data/...` required on Git Bash (Windows) to prevent path mangling.
- `--memory=1g --cpus=3` are safety caps. Do not remove.
- Config schema: see `Pulse_translation_new/data/engine_runs/smoke_test/config.json` for a working example.

---

## Full context (if needed)

In `C:\Users\santi\projets\Pulse_translation_new\`:
- `pulse_engine_literature_review.md` — 600-line full review (cardiovascular, respiratory, ventilator, gas exchange, independent assessments)
- `pulse_engine_internals_for_future_paper.md` — C++ source code map from 2026-04-07 audit
- `experiments_log.md` — all 30+ experiments run on the engine

These are reference-only; PulseProbe does not modify them.
