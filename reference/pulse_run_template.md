# Pulse Run Template — verified syntax

> **Note, 2026-09-27.** Parts of this April note are out of date; the code is the authority. (1) The atlas runs the `pulse-atlas-engine` image (`src/runner.py`, `DEFAULT_IMAGE`), not `pulse-pediatric-engine`, and the Docker call lives in `src/runner.py` (there is no `src/run_morris.py`). (2) The detection criteria under *Clamp / divergence detection* predate the detector's calibration of 2026-04-25: none of the four strings listed there occurs in the Pulse 4.3.1 engine source, and a value outside the physiological bounds makes a run `implausible`, not `diverged`. See `src/detector.py`.

This is the exact Docker invocation verified to work on the maintainer's machine (2026-04-19). Copy into `src/run_morris.py` and similar scripts.

## Single run

```bash
MSYS_NO_PATHCONV=1 docker run --rm --memory=1g --cpus=3 \
  -v "$(pwd -W)/RUNDIR:/data" \
  pulse-pediatric-engine \
  --config //data/config.json \
  --output //data/output.csv
```

**On Linux / macOS** (no MSYS path conversion issue):
```bash
docker run --rm --memory=1g --cpus=3 \
  -v "$(pwd)/RUNDIR:/data" \
  pulse-pediatric-engine \
  --config /data/config.json \
  --output /data/output.csv
```

## 3× parallel (verified safe on i5-11400H + 8 GB RAM)

Resource budget: 3 × 1 GB = 3 GB (fits in Docker's 3.95 GB allocation). 3 × 3 = 9 CPUs (leaves 3 for host OS). Total for 3× parallel: ~3 GB RAM, ~9 CPU cores.

See `experiments_log.md` E0.1 for the verification.

## Config schema

Working minimal config (copy from `Pulse_translation_new/data/engine_runs/smoke_test/config.json`):

```json
{
  "case_id": "example",
  "condition": "Healthy",
  "duration_hours": 0.033,
  "sample_interval_s": 30,
  "baselines": {
    "age_yr": 18,
    "weight_kg": 67.3,
    "height_cm": 180.0,
    "sex": "Male",
    "hr": 72,
    "rr": 15,
    "sbp": 114,
    "dbp": 73
  },
  "ventilator": {
    "mode": "VC-AC",
    "tidal_volume_ml": 500,
    "set_rr": 15,
    "peep_cmh2o": 5,
    "fio2": 0.4
  }
}
```

**Duration:** `duration_hours: 0.033` = ~2 min simulated. Gives steady-state readings. Extend to 0.05 (3 min) if longer settling is needed. Do NOT shorten below 0.025 — risk of capturing transient values.

## Safety rules (do not remove)

- Always use `--rm` — containers clean up automatically.
- Always cap `--memory` and `--cpus` — prevents RAM thrashing on 8 GB machines.
- Never run more than 3 parallel containers on the i5-11400H / 8 GB machine. On hospital cluster, scale up proportional to available RAM (1 GB per container).
- Check `docker ps` between batches — ensure no zombie containers.
- Use `docker system prune -f` weekly to reclaim space (Pulse image + intermediate layers).

## Clamp / divergence detection

A run is **clamped** if the Pulse log contains:
- `"too large"`, `"too small"`, `"outside the valid range"`, `"use a condition to model"` strings.
- The patient setup completes but with input values silently changed.

A run is **diverged** if:
- CSV contains NaN or ±Inf.
- CSV output is missing or empty after container exit.
- Exit code ≠ 0.
- Physiological values outside plausible bounds (e.g., HR > 300, MAP < 10).

Both conditions should be logged as metadata alongside each run, not discarded.
