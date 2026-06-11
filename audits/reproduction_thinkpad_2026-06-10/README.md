# Independent x86_64 (cross-vendor AMD/Intel, cross-OS) reproduction of the S1_M pilot — Lenovo ThinkPad (AMD Ryzen 5 / x86_64)

**Date:** 2026-06-10
**Operator:** Yassir Mamouni
**Branch base:** `origin/main` (up-to-date `main`)

## Purpose

This adds an independent reproduction datapoint for the npj submission. It
re-executes the canonical 22-run S1_M pilot (`scripts/run_pilot.py`) from
scratch on an independent x86_64 system with an **AMD** CPU — a different vendor
from the Intel reference environment — under a different host OS (Ubuntu/WSL2 vs
Windows), and compares the result against the committed canonical aggregate.

Scope note: this is a *same-architecture-family* (x86_64) reproduction across
CPU vendor and host OS. It does **not** test cross-architecture portability
(e.g. x86_64 -> ARM64), which Supplement §S12 explicitly leaves as future work.

## Environment (captured on this machine)

| Field | Value | Source |
|---|---|---|
| Chassis | Lenovo ThinkPad | operator-reported |
| CPU | **AMD Ryzen 5 PRO 4650U** with Radeon Graphics (`AuthenticAMD`) | `lscpu` (verified) |
| Architecture | **x86_64** | `uname -m` (verified) |
| OS | **Ubuntu 24.04.4 LTS** (Noble Numbat) | `/etc/os-release` (verified) |
| Kernel | `6.6.87.2-microsoft-standard-WSL2` — **runs under WSL2** | `uname -a` (verified) |
| Docker | `29.5.3, build d1c06ef` | `docker --version` |
| Pulse image tag | `pulse-atlas-engine:latest` | `docker image ls` |
| Pulse image id / digest | `sha256:4c433053a931b20c0154953c8eee8a3f843a01d61675fb693f8c729348973c7f` | `docker image inspect` |
| Pulse engine version | 4.3.1 | atlas pin (CLAUDE.md) |

**Honest scope note.** This is Ubuntu 24.04 running under **WSL2** on Windows,
not bare-metal Linux. It is a genuine x86_64 Linux userspace and a different CPU
*vendor* (AMD) from the Intel reference environment in which the canonical pilot
was generated, so it is a valid independent reproduction point; the WSL2 layer
is disclosed for completeness.

## Commands used

```bash
# 0. Environment capture
uname -m; uname -a; lscpu | grep -iE "Model name|Vendor ID"
cat /etc/os-release; docker --version
docker image inspect pulse-atlas-engine --format '{{.RepoDigests}} {{.Id}}'

# 1. Preserve the canonical reference before the runner overwrites the pilot dir
git show HEAD:data/runs/pilot_S1_M/aggregated.parquet > /tmp/canon_pilot_reference.parquet

# 2. Re-run the pilot from scratch (overwrite=True; 22 Docker runs)
uv run python scripts/run_pilot.py > /tmp/pilot_thinkpad_run.log 2>&1

# 3. Compare against the canonical aggregate on case_id (see table below)

# 5. Restore the canonical pilot working tree
git restore data/runs/pilot_S1_M
```

## Result — pilot gates

`scripts/run_pilot.py` reported **ALL GATES PASS** (full log:
`pilot_thinkpad_run.log`):

| Gate | Criterion | Result |
|---|---|---|
| G1 | Morris `diverged` ≤ 50 % | PASS — 0 / 16 diverged |
| G2 | no run both `clamped` and `implausible` | PASS — 0 double-flagged |
| G3 | 13 steady-state rows on every clean Morris run | PASS — 5 clean, 0 violators |
| G4 | clamp probes fire `clamped` | PASS — 2 / 2 |
| G5 | reruns reproducible within 1e-6 (intra-machine) | PASS — 0 violations |

22 runs executed: 20 completed (`exit 0`), 2 deliberate clamp probes
(`S1_M_9900`, `S1_M_9901`) rejected loudly at setup (`exit 1`) as designed —
these write no `output.csv`, so 20 per-run CSVs are archived here.

## Result — cross-platform comparison vs. canonical aggregate

Aligned on `case_id` across all 22 runs (continuous values compared on the 20
runs with finite means; the 2 clamp probes have NaN means and are excluded from
the continuous comparison but included in the flag comparison).

### Continuous — `max|Δ|` per `{channel}_mean`

| Channel | n (finite pairs) | max\|Δ\| |
|---|---|---|
| HR | 20 | 0.000e+00 |
| MAP | 20 | 0.000e+00 |
| Vt | 20 | 0.000e+00 |
| SpO₂ | 20 | 0.000e+00 |
| PaO₂ | 20 | 0.000e+00 |
| PaCO₂ | 20 | 0.000e+00 |

**Overall max|Δ| = 0.000e+00 (bit-identical).**

### Discrete — five-flag concordance

| Flag | Mismatches / 22 |
|---|---|
| diverged | 0 |
| clamped | 0 |
| implausible | 0 |
| not_steady_state | 0 |
| clean | 0 |

**100 % flag concordance** — all 5 flags identical on 22 / 22 runs.

## Conclusion

The S1_M pilot reproduces on an independent x86_64 (AMD Ryzen 5) platform with
**max|Δ| = 0 (bit-identical)** continuous outputs and **100 % flag
concordance** — stronger than the near-machine-precision agreement anticipated;
**no residual floating-point differences were observed**. Any residual
floating-point differences across operating systems, compilers, runtime
libraries, or hardware implementations would have been acceptable, but none
arose: the Pulse 4.3.1 engine (CPU-only) produced byte-identical steady-state
output across the Intel reference environment and this AMD Ryzen system.
**Reproducibility on an independent x86_64 Linux platform is confirmed.**

This is consistent with the full-1,280-run steady-state reproduction
(`audits/reproduction_check_2026-06-07.md`), which likewise found bit-identical
continuous values.

## Contents of this directory

| File | What |
|---|---|
| `aggregated_thinkpad_ryzen5.parquet` | The ThinkPad pilot aggregate (22 rows) produced by this run |
| `output_csv/S1_M_*.csv` | The 20 per-run Pulse output CSVs (clamp probes write none) |
| `pilot_thinkpad_run.log` | Full `run_pilot.py` execution log incl. gate evaluation |
| `README.md` | This provenance document |
