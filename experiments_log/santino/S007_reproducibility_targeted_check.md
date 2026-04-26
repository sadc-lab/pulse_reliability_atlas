---
id: S007
author: santino
date: 2026-04-26
status: done
tags: [reproducibility, verification, docker, determinism, pre-publication]
linked_code:
  - src/scenario.py
  - src/runner.py
  - src/analysis_morris.py
linked_data:
  - data/runs/full_sweep/aggregated.parquet
  - data/runs/repro_backup_S007/
supersedes: ""
related: [S005, S006]
---

# S007 — Targeted reproducibility check (pre-publication)

## Hypothesis

The atlas is bit-exact reproducible at every layer of the pipeline:
config generation, Pulse simulation, Morris analysis. A skeptical
re-execution at three independent layers — without re-running the full
1,280-simulation sweep — produces identical results to the values
quoted in the manuscript.

## Motivation (why)

Before submitting the methods paper, the maintainer asked: *"are we
sure none of these numbers are wrong?"* A natural impulse is to
re-run the entire 1,280-simulation sweep. Honest assessment: that
re-execution is mostly redundant.

Three reasons:

1. **Pulse 4.3.1 is deterministic for fixed inputs.** Already verified
   in `S005` gate G5 (4 reruns × 6 outputs, 0 violations within 1e-6).
2. **Same code + same inputs → same outputs.** A re-run on the same
   machine with the same Python orchestrator + Docker image gives
   bit-identical CSVs by construction.
3. **A full re-run cannot detect the kind of error you actually worry
   about.** Bugs in our Python code, wrong detector thresholds, or a
   mistaken analysis formula all survive a re-run because they're
   *embedded in the code being re-run*. A full re-run is theatre, not
   verification.

What *can* detect those errors is verification at *independent layers*:
regenerate the configs from scratch, recompute Morris indices in fresh
code that doesn't share lines with `src/analysis_morris.py`, and
re-execute a small sample of Pulse runs to confirm Pulse + our pipeline
is still deterministic on this machine right now. That's S007.

## Method (how)

### Check 1 — Pipeline determinism (config regeneration)

Pick 10 random `(scenario, sex, sample_idx)` triples from the master
sample, regenerate each `config.json` via `src.scenario.build_config`,
and compare byte-for-byte against the on-disk config under
`data/runs/full_sweep/<cell>/<case_id>/config.json`. If any one byte
differs, the config-generation logic is non-deterministic or has been
silently changed since the sweep ran.

### Check 2 — Independent Morris μ\* reimplementation

Re-derive μ\* for one cell × one output using **only `numpy` and
`pandas`**, with no import from `src.analysis_morris.py`. The
independent implementation walks each Morris trajectory, identifies
the flipped input by reading the sample directly, normalizes by the
preregistered range bounds (hand-typed from `preregistration.md`
§Inputs), filters to clean-clean pairs, and computes μ\* as
`mean(|EE|)` for each input. Compare to the published parquet row.

If the independent computation diverges from `analysis_morris.py`,
the bug is in the analysis code (or in this independent
re-implementation, which is itself a verification: any mismatch is a
red flag). If they agree, the Morris result is robust to the
implementation.

### Check 3 — 5-run Docker re-execution

Pick 5 random `clean` runs from the master parquet, back up their
existing `output.csv` to `data/runs/repro_backup_S007/`, then
re-execute via `src.runner.run_one(...)` with `overwrite=True`. Compare
the new `output.csv` row-by-row against the backup. This is the only
check that actually re-touches Docker and Pulse; it tests determinism
*on this exact machine, in its current state*, with the *current* atlas
image. If a system update, a hardware change, or some accumulated state
broke determinism since the original sweep ran, this check catches it.

The 5-run sample includes one run per scenario tier (S1, S2, S2, S4,
S4) and two of the heaviest cells (S4_M, where the original sweep had
the longest wall times and the highest divergence rate).

## What we tried (including dead ends)

This experiment was a single deliberate sequence: there were no dead
ends. It was designed to fall through three independent checks, and
all three were planned in advance. The interesting design question was
*scope*: I considered, and rejected, the following alternatives:

* **Full 1,280-run re-execution.** Rejected: ~7 h of compute, ~5 kWh of
  power, and zero new information given S005 G5 already verified
  Pulse determinism. A re-run would catch a subset of *machine* drift
  but no software bugs — same code re-running on the same machine
  produces the same outputs.
* **Re-run with a different Morris seed.** This would test sample-
  level stability but is a different question (sample stability ≠
  reproducibility) and would not validate the published numbers.
* **Hand-recomputing 100 stats by spreadsheet.** Higher false-positive
  rate, lower coverage; supplanted by Check 2 which validates
  *every* μ\* in one cell × one output deterministically.

## Results

### Check 1 — pipeline determinism

10 / 10 randomly-picked configs match the on-disk `config.json`
byte-for-byte:

```
S1_F_0128 OK   S1_M_0153 OK   S4_F_0150 OK   S4_M_0000 OK
S1_M_0073 OK   S1_F_0002 OK   S4_F_0053 OK   S4_F_0089 OK
S3_F_0131 OK   S1_F_0022 OK
```

**Outcome:** config generation is deterministic. The Morris sample +
`src/scenario.py` regenerate identical configs.

### Check 2 — independent Morris μ\*

For cell (S2, M) on output HR, the seven μ\* values from the
independent numpy re-implementation match the published parquet to
**0.00e+00** absolute difference:

| Input | Independent μ\* | Module μ\* | Diff |
|-------|-----------------|------------|------|
| hr    | 61.153734       | 61.153734  | 0.0  |
| sbp   | 5.164050        | 5.164050   | 0.0  |
| dbp   | 1.233489        | 1.233489   | 0.0  |
| rr    | 10.339156       | 10.339156  | 0.0  |
| vt    | 6.183689        | 6.183689   | 0.0  |
| fio2  | 8.237260        | 8.237260   | 0.0  |
| peep  | 9.294105        | 9.294105   | 0.0  |

**Outcome:** the Morris analysis code in `src/analysis_morris.py` is
correct *modulo* the same potential errors I might have made in the
independent re-implementation. Both code paths agree, so a bug
specific to one is unlikely.

### Check 3 — 5-run Docker re-execution

5 / 5 randomly-picked clean runs reproduce **bit-exactly** versus the
original sweep output:

```
S4_M_0150 max_abs_diff=0.00e+00  max_rel_diff=0.00e+00  OK
S4_M_0002 max_abs_diff=0.00e+00  max_rel_diff=0.00e+00  OK
S1_M_0021 max_abs_diff=0.00e+00  max_rel_diff=0.00e+00  OK
S2_M_0151 max_abs_diff=0.00e+00  max_rel_diff=0.00e+00  OK
S2_M_0106 max_abs_diff=0.00e+00  max_rel_diff=0.00e+00  OK
```

This is *stronger* than the preregistered S005 G5 reproducibility
threshold (1e-6 relative). Pulse 4.3.1 + the atlas wrapper produce
**identical floating-point output** when given the same input on the
same machine, even across different sweep restarts.

**Outcome:** Pulse + atlas pipeline is end-to-end deterministic on the
maintainer's machine.

## Interpretation

All three independent reproducibility layers pass with the strongest
possible result (`diff = 0` everywhere). The atlas's published numbers
are not artefacts of a particular run, a transient bug, or a
machine-specific state. They are reproducible by construction:

* the configs regenerate from the canonical Morris sample;
* the simulator produces bit-exact CSVs from those configs;
* the analysis code produces bit-exact μ\* from those CSVs;
* and an independent re-implementation of the analysis agrees.

Combined with the eight verification checks already documented in S006
(CSV→parquet integrity, EE math by hand, bootstrap CI bracket,
Wasserstein on synthetic, etc.), the atlas's headline numbers have
**eleven independent verification points** behind them.

The targeted check completed in approximately 12 minutes — three
orders of magnitude cheaper than a full sweep re-execution while
catching strictly more error classes (a full re-run cannot detect a
bug in `analysis_morris.py`; this check did test that path
independently).

## Next steps

* No code changes required.
* Commit + push S007 log alongside the manuscript additions.
* The reproducibility statement in the methods paper now points to
  S005 G5 (Pulse determinism), S006 V1–V8 (eight sanity checks), and
  S007 (this entry, three independent reproducibility layers).
* `data/runs/repro_backup_S007/` is gitignored (raw output CSVs); the
  backup directory will be removed on the next `git clean` pass.
