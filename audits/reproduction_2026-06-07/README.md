# Reproduction artifacts — 2026-06-07

Outputs of an independent re-run of the full 1,280-run Morris sweep
(`scripts/run_full_sweep.py` → `analyze_sweep.py` → `make_figures.py`) on a
WSL2/Linux machine, branch `feat/contribution-ym`.

**These are kept separate on purpose.** The canonical paper artifacts under
`results/` and `data/runs/full_sweep/` remain the originals the npj submission
was written from; this directory holds the *reproduction* copies so the two can
be compared without overwriting the originals.

| file | reproduction copy of |
|---|---|
| `aggregated.parquet` | `data/runs/full_sweep/aggregated.parquet` (master, 1,280 runs) |
| `results/*.csv`, `results/morris_indices.parquet` | the corresponding `results/` analysis outputs |

Full numerical comparison, method, and verdict:
**`../reproduction_check_2026-06-07.md`**.

Summary: flags and all continuous steady-state values are **bit-identical** to
the originals; only three H4 statistics differ, at `~1e-14` floating-point
round-off, with an identical BH-FDR survivor set. Figures are regenerable and
scientifically identical, so they are not duplicated here.
