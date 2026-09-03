# Provenance Spot-Check Protocol

**Purpose.** Verify that one row of `data/runs/full_sweep/aggregated.parquet`
faithfully represents what the Pulse Physiology Engine v4.3.1 would produce
*today* for the same inputs. The `scripts/audit_claims.py` claims ledger
guarantees that the manuscript text matches the frozen parquet; this protocol
closes the "garbage-in" gap from the **other** end -- parquet vs a fresh
Pulse run.

**Honest caveat.** This is a **spot-check on a single cell**. It catches
wrapper / serializer / runner drift on the cell you choose. It does **not**
detect a systematic solver change across the full sweep; only a complete
re-run does. A good default cell is the worst-case S014 trigger-lockout run
`S1_F_0117` (Vt CV = 1.826 in the original sweep), because its anomalous
Vt-mean signature is instantly recognisable. Pick a different cell when a
specific finding is in question.

## Protocol (≈ 10 minutes)

### 1. Read the cell's exact configuration

```sh
uv run python scripts/provenance_check.py --cell S1_F_0117
```

This prints, for the chosen cell:

* `scenario`, `sex`, `condition`, `ards_severity`;
* the **seven swept inputs** verbatim (`in_hr`, `in_rr`, `in_sbp`, `in_dbp`,
  `in_vt`, `in_fio2`, `in_peep`);
* the aggregated steady-state means for HR, MAP, Vt, SpO₂, PaO₂, PaCO₂;
* the four flags + the `clean` rollup.

For `S1_F_0117` you should see Vt setpoint = 800 mL but a steady-state Vt
mean of ~100 mL and `not_steady_state = True` -- the worst-case trigger-
dyssynchrony fingerprint. If those characteristic numbers do not appear,
the parquet itself has already drifted from the cell you expected, and the
rest of the protocol is moot.

### 2. Build a single-cell Pulse config

Use the seven inputs above plus the patient + scenario constants for the
selected `(scenario, sex)` cell (defined in `src/scenario.py`) to assemble a
Pulse `config.json`. For VC-AC the locked configuration sets
`InspirationPatientTriggerPressure = -2 cmH2O`. Omit / leave it at Pulse's
default if you are testing the pre-S014 baseline behaviour (this is the
configuration that produces the `S1_F_0117` Vt CV = 1.826 signature; the
locked-trigger reruns live separately under `data/runs/s014_trigger_lockout/`).

### 3. Run Pulse Docker (reviewer's machine)

Follow the verified template in `reference/pulse_run_template.md`:

```sh
MSYS_NO_PATHCONV=1 docker run --rm --memory=1g --cpus=3 \
  -v "$(pwd -W)/RUNDIR:/data" \
  pulse-atlas-engine \
  --config //data/config.json \
  --output //data/output.csv
```

Save the resulting `RUNDIR/output.csv`.

### 4. Diff the fresh output against the parquet row

```sh
uv run python scripts/provenance_check.py \
    --cell S1_F_0117 \
    --fresh-output RUNDIR/output.csv
```

The script recomputes the steady-state mean (final 60 s window, `[60, 120]`)
for each of the six channels from the fresh `output.csv` and compares it to
the parquet row's `<channel>_mean` within relative tolerance (`--tol-rel`,
default `0.001` = 0.1 %). It prints a per-channel table with absolute and
relative diffs and a PASS / FAIL verdict, and exits non-zero on any FAIL.

## Interpreting the result

| Outcome | What it means |
|---|---|
| All six PASS at `tol_rel = 1e-3` | The parquet faithfully represents Pulse's current output for this cell. Spot-check passes. |
| 1–2 FAIL at `1e-3` but PASS at `1e-2` | Probable floating-point or column-rename drift; investigate the runner / aggregator before trusting downstream analyses for this cell. |
| ≥ 1 FAIL at `1e-2` | Real divergence. Either Pulse changed behaviour or the parquet was produced from a different config than the one `--cell` reports. **Stop and investigate** before publishing further work that depends on the parquet. |

## What this protocol does NOT cover

* **Cross-cell consistency.** Cell B may have drifted even if cell A passes.
* **Trajectory shape.** Only the steady-state mean is compared; transient
  dynamics are not.
* **Engine determinism across re-runs.** That is the pilot's `1e-6` check
  (`scripts/run_pilot.py`).
* **Systematic solver change.** Only a complete re-run of the 1,280-cell
  sweep would detect that.

Use this spot-check as a **fast, high-confidence sanity test** on a critical
cell before relying on the parquet for new analyses. Run it on a second cell
(e.g. the cell of any new finding) before any external claim that depends on
the parquet.
