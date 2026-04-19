# Experiments Log — PulseProbe

Lab notebook. Every experiment, scope change, and finding is logged here.
Format: **why** (motivation) + **how** (method) + **what happened** (result). Never just action+result.

---

## D0 — 2026-04-19 (Sunday, setup day)

### E0.1 — Docker + hardware smoke test

- **Why.** Before committing to Mode A scope (350 runs, 3× parallel Docker), verify the laptop actually supports 3 simultaneous Pulse containers without RAM thrashing.
- **How.** Spawn 3 `docker run` containers in parallel, each executing the project smoke_test scenario (healthy VC-AC, 2 min simulated, 30 s compute). Measure wall time and success/failure.
- **Hardware.** i5-11400H (6 cores / 12 threads), 8 GB RAM. Docker allocation: 3.95 GB RAM, 12 CPUs.
- **Result.**
  - Single-container baseline: **43 s** for a 2-minute (0.033 h simulated) healthy VC-AC scenario, with `--memory=1g --cpus=3`. Output CSV produced correctly (1,449 bytes, 5 sample rows at 30 s intervals).
  - 3× parallel: **all 3 containers completed successfully**, all three output CSVs produced with identical timestamps. Safety caps applied: `--memory=1g --cpus=3` per container (total 3 GB RAM, 9 CPUs — fits inside the 3.95 GB Docker allocation and leaves 3 cores for host OS).
  - **Conclusion:** Mode A scope (350 runs, 3× parallel) is feasible on this hardware. Extrapolated wall time: 350 runs × 43 s / 3 parallel ≈ 85 minutes of Docker compute (plus overhead from container start/stop, I/O, stats). Budget 2–4 h on D2 for the full batch.
  - **Path handling note:** Git Bash on Windows auto-converts `/data/...` arguments to `C:/Program Files/Git/data/...`. Fix: set `MSYS_NO_PATHCONV=1` and use double-slash form `//data/config.json` inside the `docker run` command. Bake into the run harness.
  - **Resource caps** (`--memory=1g --cpus=3`) were the key safety measure. Without them, an 8 GB RAM machine can thrash under 3× uncapped Pulse containers. Always include these caps in `run_morris.py`.

### E0.2 — Project bootstrap

- **Why.** Hackathon starts Tue 2026-04-21. Need a clean, separately-licensed repo ready before the event opens so Day 1 is spent doing science, not plumbing.
- **How.** Created directory `C:\Users\santi\projets\Hackathon_Claude_2026\` with: `CLAUDE.md` (project rules, verified Pulse limitations, Mode A/B/C plan, budget), `README.md` (public-facing), `preregistration.md` (analysis commitments locked pre-data), this `experiments_log.md`, `.gitignore`, directory skeleton (src/, data/, dashboard/, preprint/, figures/, notebooks/).
- **Result.** Repo ready for git init. Context from the maintainer's PhD project (`Pulse_translation_new/`) is referenced, not copied — keeps the two projects clean.

### E0.3 — Verified Pulse 4.3.1 limitations

- **Why.** Pitch depends on the claim "no formal sensitivity analysis exists." Needed to re-verify that claim against a primary source, not rely on memory.
- **How.** Fetched `https://pulse.kitware.com/_f_a_q.html` directly, cross-checked against version history (`https://pulse.kitware.com/version.html`) and Pulse 4.3 release notes.
- **Result.** Claim verified verbatim. v3.0.0 *planned* a sensitivity framework; v4.2.0 did not deliver it; v4.3.0 added "initial architecture for automated validation" (regression templates, not UQ); v4.3.1 (Sept 2024, current) still has no formal SA/UQ. Keystone gap is real and current. Full verification table in `CLAUDE.md`. Two previously-cited limitations withdrawn (FiO2 crash, sex-specific physiology) — see CLAUDE.md for why.

---

## D1 — 2026-04-21 (Tuesday, hackathon opens)

_(to be written as work happens)_
