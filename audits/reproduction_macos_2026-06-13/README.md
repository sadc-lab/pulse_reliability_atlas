# Apple Silicon (MacBook Air M2 / ARM64 host) reproduction of the S1_M pilot — via **emulated x86_64**

**Date:** 2026-06-13
**Operator:** Yassir Mamouni
**Branch base:** `main`

## TL;DR

The canonical 22-run S1_M pilot was re-executed on a MacBook Air M2 (ARM64).
Continuous steady-state outputs reproduce the committed canonical aggregate to
**max|Δ| = 2.9 × 10⁻⁹** with **100 % five-flag concordance** (0 / 110 flag-cells).

**Important scope limit — read before citing.** The Pulse engine here ran as an
**emulated x86_64** binary, **not** native ARM64. `kitware/pulse:4.3.1` is
published for `linux/amd64` only (no arm64 image exists), so Docker Desktop runs
it under x86→ARM emulation inside its Linux VM. The container reports `x86_64`.
**This artifact therefore does NOT close Supplement §S12's native-ARM64
cross-architecture gap.** What it does establish is (a) the atlas pipeline runs
end-to-end on Apple Silicon, and (b) the engine, executed as emulated x86 on ARM
hardware, reproduces the canonical x86 results to ~3 × 10⁻⁹. See "What this does
and does not show" below.

## Why this is *not* a native-ARM64 test

| | ThinkPad artifact (2026-06-10) | **This artifact** |
|---|---|---|
| Host arch | x86_64 (AMD Ryzen 5) | **ARM64 (Apple M2)** |
| Engine binary arch | x86_64 (native) | **x86_64 (emulated on ARM)** |
| Base image | `kitware/pulse:4.3.1` (amd64) | `kitware/pulse:4.3.1` (amd64) |
| max\|Δ\| vs canonical | **0** (bit-identical) | **2.9 × 10⁻⁹** (near machine precision) |

The ThinkPad confirmed *cross-vendor* bit-identity within native x86_64
(Intel ↔ AMD). This Mac run is different: the engine is still an x86_64 binary,
but its instructions are translated to ARM64 by the emulation layer. The small
non-zero residual (~3 × 10⁻⁹, vs the ThinkPad's exact 0) is attributable to
floating-point handling in that x86→ARM emulation layer — **not** to a
natively-compiled ARM64 build. A true native-ARM64 test would require compiling
Pulse 4.3.1 from source for `linux/arm64`, which was not done here.

## Environment (captured on this machine)

| Field | Value | Source |
|---|---|---|
| Chassis | MacBook Air (`Mac14,2`) | `sysctl hw.model` |
| Chip | **Apple M2** (8 cores) | `sysctl machdep.cpu.brand_string` |
| RAM | 16 GB | `sysctl hw.memsize` |
| Host architecture | **arm64** | `uname -m` |
| OS | **macOS 26.5.1** (build 25F80) | `sw_vers` |
| Docker client | 24.0.2 | `docker version` |
| Docker server (VM) | arch **arm64**, OS linux | `docker version` |
| Pulse image tag | `pulse-atlas-engine:latest` | local build from `engine/Dockerfile` |
| Pulse image id (local) | `sha256:675f1b6bb43f33eabad83dd89789470afe914462062d38c0db58231f194f1381` | `docker image inspect` |
| Base image | `kitware/pulse:4.3.1`, platform **`linux/amd64` only** | `docker manifest inspect` |
| Base image registry digest | `sha256:fb9b43b769e9898c8b0c09569fa12f63d38e9ef078bb5c89088e990cad2ac486` | `docker buildx imagetools inspect` |
| Engine runtime arch | **`x86_64` (emulated)** | `docker run --entrypoint uname … -m` |
| Pulse engine version | 4.3.1 | atlas pin (CLAUDE.md) |

At `docker run`, Docker emits:
`WARNING: The requested image's platform (linux/amd64) does not match the
detected host platform (linux/arm64/v8) and no specific platform was requested`
— i.e. emulation is in force.

## Commands used

```bash
# 0. Environment + emulation evidence
sw_vers; uname -m; sysctl -n machdep.cpu.brand_string hw.model hw.memsize
docker manifest inspect --verbose kitware/pulse:4.3.1 | grep architecture   # -> amd64 (single-platform)
docker build -t pulse-atlas-engine:latest engine/
docker run --rm --entrypoint uname pulse-atlas-engine:latest -m             # -> x86_64 (emulated)

# 1. Preserve the canonical reference before the runner overwrites the pilot dir
git show HEAD:data/runs/pilot_S1_M/aggregated.parquet > /tmp/ref.parquet

# 2. Re-run the pilot from scratch (overwrite=True; 22 Docker runs), lid kept open
#    NOTE: one temporary, physics-neutral edit (see "Deviation" below).
caffeinate -dimsu uv run python scripts/run_pilot.py > pilot_macos_run.log 2>&1

# 3. Compare new aggregate vs /tmp/ref.parquet on case_id (tables below)

# 4. Restore the canonical working tree + revert the temporary edit
git restore data/runs/pilot_S1_M
git checkout scripts/run_pilot.py
```

### Deviation from the verbatim canonical procedure

The per-run Docker kill-deadline in `scripts/run_pilot.py` was temporarily
raised from **600 s → 1800 s** (`run_many(..., timeout_s=1800)`) and reverted
immediately after the run. Rationale: emulated x86 execution takes **359–488 s
per run** on this M2 (median 416 s) versus ~40 s native, which sits dangerously
close to the native-tuned 600 s cap. (A first attempt at the default 600 s was
derailed when the laptop lid was closed mid-run: the Docker VM slept, in-flight
runs blew past 600 s on resume, and were killed → `exit 124` → spurious
`diverged`.) The change affects **only** the subprocess timeout; Morris sampling,
seeds (42), scenario, patient, and all physics are byte-for-byte unchanged — the
100 % flag concordance and ~1e-9 agreement below confirm the run is otherwise
identical to canonical.

## Result — pilot gates

`scripts/run_pilot.py` reported **ALL GATES PASS** (full log: `pilot_macos_run.log`):

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
the continuous comparison but included in the flag comparison). The new aggregate
carries one extra column (`primary_flag`, added to `src/detector.py` after the
canonical parquet was written); it is excluded from the continuous diff. The five
flags below are present in both frames.

### Continuous — `max|Δ|` per `{channel}_mean`

| Channel | n (finite pairs) | max\|Δ\| |
|---|---|---|
| HR | 20 | 3.043e-10 |
| MAP | 20 | 5.105e-11 |
| Vt | 20 | 3.492e-10 |
| SpO₂ | 20 | 5.340e-14 |
| PaO₂ | 20 | 2.896e-09 |
| PaCO₂ | 20 | 1.240e-09 |

**Overall max|Δ| = 2.896e-09** (near machine precision; scientifically negligible
— far below any clinical bound or steady-state threshold).

### Discrete — five-flag concordance

| Flag | Mismatches / 22 |
|---|---|
| diverged | 0 |
| clamped | 0 |
| implausible | 0 |
| not_steady_state | 0 |
| clean | 0 |

**100 % flag concordance** — all 5 flags identical on 22 / 22 runs (0 / 110 flag-cells).

## Emulation performance note

Per-run wall time under emulation: **359–488 s** (median 416 s), ~69 min total
for the 20 runs on 2 parallel workers — roughly **10× slower than native**
(~40 s/run). This is the practical cost of running the amd64 image on Apple
Silicon and is the reason the timeout had to be raised; it is a tooling/throughput
observation only and has no bearing on the numerical results.

## What this does and does not show

**Does show:**
- The atlas pipeline (sampler → scenario → runner → aggregator → detector →
  gates) runs end-to-end on macOS / Apple Silicon.
- The Pulse 4.3.1 engine, run as emulated x86 on ARM hardware, reproduces the
  canonical steady-state outputs to **~3 × 10⁻⁹** with **100 % flag concordance**.

**Does NOT show:**
- Native ARM64 reproducibility. The engine binary was x86_64 (emulated). The
  `x86_64 → ARM64` cross-architecture question in **Supplement §S12 remains
  open** and should keep its current caveat. Closing it would require building
  and running a natively-compiled `linux/arm64` Pulse 4.3.1 binary.

## Contents of this directory

| File | What |
|---|---|
| `aggregated_macos_m2.parquet` | The M2 pilot aggregate (22 rows) produced by this run |
| `output_csv/S1_M_*.csv` | The 20 per-run Pulse output CSVs (clamp probes write none) |
| `pilot_macos_run.log` | Full `run_pilot.py` execution log incl. gate evaluation |
| `README.md` | This provenance document |
