"""Phase 4a — same-seed full Morris re-execution.

Re-runs all 1,280 runs of the canonical Morris sweep against the current
``pulse-atlas-engine:latest`` image (hash ``b2e0e807803d`` at audit time)
and writes results to ``data/runs/full_sweep_repro/``. Canonical artifacts
under ``data/runs/full_sweep/`` are NOT touched.

Post-run, ``scripts/phase4a_compare.py`` (or the inline comparison at the
bottom of this script) does a bit-exact SHA-256 diff of every output.csv
against the canonical one and an aggregated.parquet equality check.

Why this exists (and not run_full_sweep.py): the original sweep script writes
to the canonical location and would no-op under --resume. We need a parallel
target directory so the canonical artifact stays untouched.

Usage::

    uv run python scripts/phase4a_full_repro.py            # full 1,280 re-run
    uv run python scripts/phase4a_full_repro.py --resume   # continue interrupted run
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.aggregator import aggregate_under, write_parquet  # noqa: E402
from src.runner import run_many  # noqa: E402
from src.scenario import build_config, case_id, iter_cells  # noqa: E402


CANONICAL_ROOT = REPO_ROOT / "data" / "runs" / "full_sweep"
CANONICAL_SAMPLE = CANONICAL_ROOT / "morris_sample.parquet"

REPRO_ROOT = REPO_ROOT / "data" / "runs" / "full_sweep_repro"
REPRO_MASTER = REPRO_ROOT / "aggregated.parquet"


def _cell_dir(scenario_key: str, sex_key: str) -> Path:
    return REPRO_ROOT / f"{scenario_key}_{sex_key}"


def _is_run_complete(run_dir: Path) -> bool:
    meta = run_dir / "run_meta.json"
    csv = run_dir / "output.csv"
    if not meta.exists():
        return False
    try:
        m = json.loads(meta.read_text())
        rc = int(m.get("exit_code", 1))
    except (json.JSONDecodeError, OSError):
        return False
    # exit_code != 0 runs (originally diverged) won't have a CSV; treat as complete if meta says non-zero.
    if rc != 0:
        return True
    return csv.exists()


def _format_hms(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h}h{m:02d}m{s:02d}s"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 4a — full same-seed re-execution.")
    parser.add_argument("--resume", action="store_true",
                        help="skip runs whose run_meta.json already exists")
    parser.add_argument("--cells", nargs="+", default=None,
                        help="restrict to subset of cells, e.g. --cells S1_M S2_F")
    parser.add_argument("--timeout-s", type=float, default=600.0)
    args = parser.parse_args(argv)

    if not CANONICAL_SAMPLE.exists():
        print(f"[phase4a] canonical sample missing at {CANONICAL_SAMPLE}", file=sys.stderr)
        return 1

    REPRO_ROOT.mkdir(parents=True, exist_ok=True)
    sample = pd.read_parquet(CANONICAL_SAMPLE)
    print(f"[phase4a] loaded canonical sample: {len(sample)} rows")

    if args.cells is None:
        cells = list(iter_cells())
    else:
        cells = []
        from src.scenario import PATIENTS, SCENARIOS
        for token in args.cells:
            sk, xk = token.split("_", 1)
            if sk not in SCENARIOS or xk not in PATIENTS:
                print(f"[phase4a] unknown cell {token!r}", file=sys.stderr)
                return 2
            cells.append((sk, xk))

    print(f"[phase4a] cells: {[f'{s}_{x}' for s, x in cells]}")
    print(f"[phase4a] resume={args.resume} timeout_s={args.timeout_s}")
    print(f"[phase4a] target root: {REPRO_ROOT.relative_to(REPO_ROOT)}")

    overall_start = time.monotonic()

    for sk, xk in cells:
        cell_start = time.monotonic()
        cell_root = _cell_dir(sk, xk)
        cell_root.mkdir(parents=True, exist_ok=True)
        jobs: list[tuple[dict, str]] = []
        for i, row in sample.iterrows():
            cid = case_id(sk, xk, run_idx=int(i))
            if args.resume and _is_run_complete(cell_root / cid):
                continue
            cfg = build_config(row, sk, xk, cid)
            jobs.append((cfg, cid))
        skipped = len(sample) - len(jobs)
        print(f"\n[phase4a] === cell {sk}_{xk} === {len(jobs)} runs ({skipped} skipped via --resume)")
        if jobs:
            run_many(jobs, runs_root=cell_root, timeout_s=args.timeout_s, overwrite=False)

        # Aggregate this cell
        df_cell = aggregate_under(cell_root)
        cell_agg = cell_root / "aggregated.parquet"
        write_parquet(df_cell, cell_agg)
        elapsed = time.monotonic() - cell_start
        print(f"[phase4a] cell {sk}_{xk} done in {_format_hms(elapsed)} -> {cell_agg.relative_to(REPO_ROOT)}")

    # Master aggregate
    frames = []
    for sk, xk in cells:
        p = _cell_dir(sk, xk) / "aggregated.parquet"
        if p.exists():
            frames.append(pd.read_parquet(p))
    if frames:
        master = pd.concat(frames, ignore_index=True)
        write_parquet(master, REPRO_MASTER)

    overall = time.monotonic() - overall_start
    print(f"\n[phase4a] total wall time: {_format_hms(overall)}")
    print(f"[phase4a] repro master: {REPRO_MASTER.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
