# PulseProbe

**The first open reliability atlas for the Pulse Physiology Engine.**

Pulse is the most-used open-source whole-body human physiology simulator (Kitware, Apache-2.0). Its developers state on the [Pulse FAQ](https://pulse.kitware.com/_f_a_q.html):

> We have not performed a systematic forward propagation or inverse quantification of model uncertainty, nor have we conducted a formal sensitivity analysis.

Every Pulse user — researchers, medical-device companies, educators — therefore operates blind to where the engine silently clamps inputs, where the solver diverges, and which inputs dominate which outputs. PulseProbe fills that gap.

## What PulseProbe delivers

1. **Open dataset** of hundreds of Pulse 4.3.1 simulations across the adult operational envelope, sampled via Morris elementary effects (and optionally Sobol indices).
2. **Interactive Streamlit dashboard** — move sliders for a patient + intervention, see green/yellow/red reliability for every output, a ranked bar of which inputs matter most, and warnings when inputs will be silently clamped or the solver will diverge.
3. **Preprint** — "First sensitivity and operational-envelope characterization of Pulse 4.3.1."
4. **Demo video** — 2-minute walkthrough.
5. **Conditional bonus chapter** (if the core lands early): prioritized proposed pediatric patches to Pulse's C++ source — diffs + literature citations. Not compiled, not tested; a roadmap informed by PulseProbe's sensitivity ranking.

## Why it exists

Built in 7 days for the *Built with Opus 4.7* Claude Code hackathon (Cerebral Valley, April 2026). The workload — hundreds of Docker simulations, crash recovery, CSV parsing, statistical aggregation, figure generation, dashboard code, preprint writing — is fundamentally agentic. Claude Code orchestrates it end to end.

## Status

Under active development. Preregistration and experiments log are the sources of truth:
- [`preregistration.md`](preregistration.md) — what we committed to measuring before any data was collected
- [`experiments_log.md`](experiments_log.md) — running log of every experiment

## License

Apache 2.0, matching the Pulse engine license.

## Citation

Preprint forthcoming.
