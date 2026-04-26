"""S006 full Morris sweep: 1,280 runs across 4 scenarios × 2 sexes × 160 points.

Implements `preregistration.md` §Sampling method:

    * One canonical Morris sample (trajectories=20, levels=4, seed=42)
      drives every cell. Sample lives at
      ``data/runs/full_sweep/morris_sample.parquet``. Locked across all 8
      cells so every cell sees the same 160 input points and Morris
      elementary effects can be computed cell-by-cell on the same geometry.
    * Per cell: 160 runs in ``data/runs/full_sweep/<scenario>_<sex>/<case_id>/``.
    * Master aggregated table at ``data/runs/full_sweep/aggregated.parquet``.

The sweep is resumable: pass ``--resume`` to skip case_ids whose
``run_meta.json`` already records ``exit_code == 0``. Runs that exited
non-zero are re-attempted (cheap probes, never hang).

Usage::

    uv run python scripts/run_full_sweep.py            # fresh sweep
    uv run python scripts/run_full_sweep.py --resume   # continue interrupted run
    uv run python scripts/run_full_sweep.py --cells S1_M S2_F  # subset

Wall-time estimate (S004 timing × 3 workers):

    S1: 160 × ~48 / 3 ≈ 42 min/sex
    S2: 160 × ~72 / 3 ≈ 64 min/sex
    S3: 160 × ~88 / 3 ≈ 78 min/sex
    S4: 160 × ~113 / 3 ≈ 100 min/sex
    Total: ~9.4 h for all 8 cells.
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
from src.sampler import sample_morris, save_sample  # noqa: E402
from src.scenario import (  # noqa: E402
    PATIENTS,
    SCENARIOS,
    build_config,
    case_id,
    iter_cells,
)


SWEEP_TRAJECTORIES = 20
SWEEP_LEVELS = 4
SWEEP_SEED = 42

SWEEP_ROOT = REPO_ROOT / "data" / "runs" / "full_sweep"
SAMPLE_PATH = SWEEP_ROOT / "morris_sample.parquet"
MASTER_PARQUET = SWEEP_ROOT / "aggregated.parquet"


def _cell_dir(scenario_key: str, sex_key: str) -> Path:
    return SWEEP_ROOT / f"{scenario_key}_{sex_key}"


def _is_run_complete(run_dir: Path) -> bool:
    meta = run_dir / "run_meta.json"
    csv = run_dir / "output.csv"
    if not (meta.exists() and csv.exists()):
        return False
    try:
        m = json.loads(meta.read_text())
        return int(m.get("exit_code", 1)) == 0
    except (json.JSONDecodeError, OSError):
        return False


def _build_or_load_sample() -> pd.DataFrame:
    """Generate the canonical Morris sample once; reuse on later runs."""
    if SAMPLE_PATH.exists():
        sample = pd.read_parquet(SAMPLE_PATH)
        print(f"[sweep] loaded canonical sample from {SAMPLE_PATH} ({len(sample)} rows)")
        return sample
    sample = sample_morris(
        trajectories=SWEEP_TRAJECTORIES, levels=SWEEP_LEVELS, seed=SWEEP_SEED
    )
    save_sample(sample, SAMPLE_PATH)
    print(f"[sweep] wrote canonical sample to {SAMPLE_PATH} ({len(sample)} rows)")
    return sample


def _build_jobs_for_cell(
    sample: pd.DataFrame,
    scenario_key: str,
    sex_key: str,
    resume: bool,
) -> list[tuple[dict, str]]:
    cell_root = _cell_dir(scenario_key, sex_key)
    cell_root.mkdir(parents=True, exist_ok=True)
    jobs: list[tuple[dict, str]] = []
    for i, row in sample.iterrows():
        cid = case_id(scenario_key, sex_key, run_idx=int(i))
        run_dir = cell_root / cid
        if resume and _is_run_complete(run_dir):
            continue
        cfg = build_config(row, scenario_key, sex_key, cid)
        jobs.append((cfg, cid))
    return jobs


def _aggregate_cell(scenario_key: str, sex_key: str) -> Path:
    cell_root = _cell_dir(scenario_key, sex_key)
    df = aggregate_under(cell_root)
    p = cell_root / "aggregated.parquet"
    write_parquet(df, p)
    return p


def _aggregate_master(cells: list[tuple[str, str]]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for sk, xk in cells:
        p = _cell_dir(sk, xk) / "aggregated.parquet"
        if p.exists():
            frames.append(pd.read_parquet(p))
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    write_parquet(df, MASTER_PARQUET)
    return df


def _format_hms(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h}h{m:02d}m{s:02d}s"


def _parse_cells(arg: list[str] | None) -> list[tuple[str, str]]:
    if not arg:
        return list(iter_cells())
    out: list[tuple[str, str]] = []
    for token in arg:
        try:
            sk, xk = token.split("_", 1)
        except ValueError:
            raise SystemExit(f"bad --cells token {token!r}; expected like 'S1_M'")
        if sk not in SCENARIOS or xk not in PATIENTS:
            raise SystemExit(f"unknown cell {token!r}")
        out.append((sk, xk))
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the full Morris sweep.")
    parser.add_argument(
        "--resume", action="store_true",
        help="skip runs whose run_meta.json already records exit_code=0",
    )
    parser.add_argument(
        "--cells", nargs="+", default=None,
        help="restrict to a subset of cells, e.g. --cells S1_M S2_F (default: all 8)",
    )
    parser.add_argument(
        "--timeout-s", type=float, default=600.0,
        help="per-run Docker timeout in seconds (default: 600)",
    )
    args = parser.parse_args(argv)

    SWEEP_ROOT.mkdir(parents=True, exist_ok=True)
    sample = _build_or_load_sample()
    cells = _parse_cells(args.cells)

    print(f"[sweep] cells: {[f'{s}_{x}' for s, x in cells]}")
    print(f"[sweep] resume={args.resume}  timeout_s={args.timeout_s}")

    overall_start = time.monotonic()

    for sk, xk in cells:
        cell_start = time.monotonic()
        jobs = _build_jobs_for_cell(sample, sk, xk, resume=args.resume)
        skipped = len(sample) - len(jobs)
        print(
            f"\n[sweep] === cell {sk}_{xk} === {len(jobs)} runs "
            f"({skipped} skipped via --resume)"
        )
        if jobs:
            run_many(
                jobs, runs_root=_cell_dir(sk, xk),
                timeout_s=args.timeout_s, overwrite=False,
            )
        agg_path = _aggregate_cell(sk, xk)
        elapsed = time.monotonic() - cell_start
        print(
            f"[sweep] cell {sk}_{xk} done in {_format_hms(elapsed)} "
            f"-> {agg_path.relative_to(REPO_ROOT)}"
        )

    df = _aggregate_master(cells)
    overall = time.monotonic() - overall_start
    print(f"\n[sweep] master aggregate -> {MASTER_PARQUET.relative_to(REPO_ROOT)}")
    print(f"[sweep] total runs in master: {len(df)}")
    print(f"[sweep] total wall time: {_format_hms(overall)}")

    if not df.empty:
        for col in ("clamped", "diverged", "implausible", "not_steady_state", "clean"):
            print(f"[sweep] {col}: {int(df[col].sum())}/{len(df)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
