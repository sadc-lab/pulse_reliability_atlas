---
id: S001
author: santino
date: 2026-04-19
status: done
tags: [docker, hardware, smoke-test, pilot]
linked_code: []
linked_data: []
supersedes: ""
related: []
---

# S001 — Docker + hardware smoke test (3× parallel Pulse)

## Hypothesis

Three Pulse Docker containers can run in parallel on the laptop (8 GB RAM, Docker allocated 3.95 GB / 12 CPUs) without RAM thrashing, provided each container is capped at `--memory=1g --cpus=3`. If true, the Mode A scope of ~350 runs is feasible on laptop-only compute within a few hours.

## Motivation (why now)

The Mode A plan assumes 3× parallel Docker throughput. Writing `run_morris.py` before verifying this assumption risks committing to a scope the hardware cannot sustain. A 30-minute smoke test here saves a day of backtracking later.

## Method (how)

- **Hardware.** i5-11400H (6 physical / 12 logical cores), 8 GB RAM, Intel UHD (no GPU). Docker Desktop allocation: 3.95 GB RAM, 12 CPUs (verified 2026-04-19).
- **Scenario.** Healthy VC-AC, 2 min simulated, output CSV sampled every 30 s.
- **Caps.** `--memory=1g --cpus=3` per container. Total under load: 3 GB RAM, 9 CPUs — leaves headroom inside the 3.95 GB Docker allocation and 3 host cores free.
- **Procedure.**
  1. Single-container baseline: one `docker run` with the smoke_test scenario. Record wall time and CSV integrity.
  2. 3× parallel: spawn three `docker run` processes simultaneously. Confirm all three CSVs land with identical output shapes.

## What we tried (including dead ends)

1. First attempt ran with the path argument `/data/config.json`. **Failed silently** — Git Bash on Windows auto-converts absolute Unix-style paths to Windows paths, so `/data/config.json` became `C:/Program Files/Git/data/config.json` inside the Docker invocation, which the container could not resolve.
2. Fix: set `MSYS_NO_PATHCONV=1` in the shell environment and use the double-slash form `//data/config.json` inside the `docker run` command. This disables Git Bash's path translation for that argument. Works consistently.

## Results

- **Single-container baseline:** 43 s for a 2-minute (0.033 h simulated) healthy VC-AC scenario. Output CSV correct: 1,449 bytes, 5 sample rows at 30 s intervals.
- **3× parallel:** all three containers completed successfully. All three CSVs produced with identical output shapes and timestamps within 1 s of each other.
- **Extrapolation.** 350 runs × 43 s / 3 parallel ≈ **85 min of Docker compute** for the full Mode A batch. Add overhead for container start/stop, I/O, stats → budget 2–4 h on D2.

## Interpretation

Mode A scope is hardware-feasible. The 3× parallel ceiling is confirmed, not assumed. Two takeaways the run harness must bake in:

1. **Safety caps are mandatory.** `--memory=1g --cpus=3` per container prevents RAM thrashing on the 8 GB machine. Without them, three uncapped Pulse containers can oversubscribe RAM and crash. `run_morris.py` must apply these flags to every invocation.
2. **Git Bash path handling.** The `MSYS_NO_PATHCONV=1` + `//data/...` fix must be part of the harness — otherwise every run on this machine fails with the same silent path error.

Limits: this is a 2-min simulated scenario, not the full Mode A run length. Longer simulations may hit different bottlenecks (I/O, memory growth over sim time). To be re-verified on the D1 pilot batch.

## Next steps

- D1: write `run_morris.py` with the safety caps and path fix baked in.
- D1 pilot (20 runs): re-measure wall time at realistic simulation length; update the 85-min extrapolation if it drifts.
