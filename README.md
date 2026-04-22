# Pulse Reliability Atlas

**The first open reliability atlas for the Pulse Physiology Engine (v4.3.1).**

Pulse is the most-used open-source whole-body human physiology simulator (Kitware, Apache-2.0). Its developers state on the [Pulse FAQ](https://pulse.kitware.com/_f_a_q.html):

> We have not performed a systematic forward propagation or inverse quantification of model uncertainty, nor have we conducted a formal sensitivity analysis.

Every Pulse user — researchers, medical-device companies, educators — therefore operates blind to where the engine silently clamps inputs, where the solver diverges, and which inputs dominate which outputs. This repository fills that gap.

## What this repo produces

1. **Open dataset** — Pulse 4.3.1 simulations across the adult operational envelope, sampled via Morris elementary effects (targeted Sobol indices conditional on Morris σ/μ* ratios). Released on Zenodo as CSV + Parquet.
2. **Short methods paper (preprint on arXiv)** — "First sensitivity and operational-envelope characterization of Pulse 4.3.1," including the first male-vs-female reliability comparison for the standard Pulse patient.
3. **Automated reliability classifier** — every run is flagged on four failure modes: silent input clamping, solver divergence, physiologically implausible output, and non-steady-state output. No run discarded; each categorized.
4. **Interactive Streamlit dashboard** (optional, post-atlas) — sliders for patient + intervention, green/yellow/red reliability per output, clamp warnings.

## Scope (locked in preregistration)

- **Inputs swept (7):** HR, SBP, DBP, RR, Vt, FiO2, PEEP.
- **Scenarios (4):** healthy, mild/moderate/severe ARDS (PALICC-2 impairments 0.00 / 0.26 / 0.60 / 0.95).
- **Patients (2):** Pulse standard adult male and adult female.
- **Ventilator:** VC-AC only (validated best per Webb 2023).

## Status

Under active development. Preregistration and experiments log are the sources of truth:
- [`preregistration.md`](preregistration.md) — commitments locked before any data was collected
- [`experiments_log/INDEX.md`](experiments_log/INDEX.md) — running log of every experiment

## Connection to the maintainer's PhD

- This repo delivers a short **methods paper** — the first publishable output.
- The maintainer's **Paper 1** (pediatric translation layer, `Pulse_translation_new/`) will cite this repo for baseline Pulse behavior.
- The planned **Paper 2** (native pediatric Pulse fork) will use this repo's Morris μ* ranking to prioritize which adult-tuned C++ equations to patch first.

## Origin note

This repository began as a 7-day Cerebral Valley "Built with Opus 4.7" hackathon entry (PulseProbe). The hackathon credit application was not granted; the scientific scope survived, now executed as a methods-paper contribution to the PhD. Hackathon-era framing documents are preserved in [`attic/`](attic/) for historical traceability.

## License

Apache 2.0, matching the Pulse engine license.

## Citation

Preprint forthcoming.
