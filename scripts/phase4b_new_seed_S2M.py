"""Phase 4b — new-seed Morris on cell (S2, M).

Generates a fresh Morris sample at seed=44 (different from canonical seed=42
and from S009's seed=43), trajectories=20, levels=4 → 160 unique points
matching the canonical sweep size. Runs cell (S2, M) and compares mu*/sigma
rankings to canonical.

This is a stronger statistical-stability check than S009 (which used
trajectories=10 → 80 points). If the top-3 input ranking by mu* matches
canonical at full sample size, the published Morris ranking is robust to
sampling, not a seed artifact.

Usage::

    uv run python scripts/phase4b_new_seed_S2M.py
    uv run python scripts/phase4b_new_seed_S2M.py --resume
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
from src.analysis_morris import morris_indices  # noqa: E402
from src.runner import run_many  # noqa: E402
from src.sampler import sample_morris, save_sample  # noqa: E402
from src.scenario import build_config, case_id  # noqa: E402


SEED_NEW = 44
TRAJECTORIES = 20
LEVELS = 4
SCENARIO = "S2"
SEX = "M"

RUN_ROOT = REPO_ROOT / "data" / "runs" / "phase4b_seed44_S2M"
SAMPLE_PATH = RUN_ROOT / "morris_sample.parquet"
RESULTS = REPO_ROOT / "results"


def _is_run_complete(run_dir: Path) -> bool:
    meta = run_dir / "run_meta.json"
    csv = run_dir / "output.csv"
    if not meta.exists():
        return False
    try:
        rc = int(json.loads(meta.read_text()).get("exit_code", 1))
    except (json.JSONDecodeError, OSError, ValueError):
        return False
    if rc != 0:
        return True
    return csv.exists()


def _format_hms(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h}h{m:02d}m{s:02d}s"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 4b — new-seed Morris on (S2, M).")
    parser.add_argument(
        "--resume", action="store_true", help="skip runs whose run_meta.json already exists"
    )
    parser.add_argument("--timeout-s", type=float, default=600.0)
    args = parser.parse_args(argv)

    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    if SAMPLE_PATH.exists():
        sample = pd.read_parquet(SAMPLE_PATH)
        print(f"[phase4b] loaded existing sample: {len(sample)} rows")
    else:
        sample = sample_morris(trajectories=TRAJECTORIES, levels=LEVELS, seed=SEED_NEW)
        save_sample(sample, SAMPLE_PATH)
        print(
            f"[phase4b] new sample: traj={TRAJECTORIES} seed={SEED_NEW} levels={LEVELS} -> {len(sample)} points"
        )

    jobs: list[tuple[dict, str]] = []
    for i, row in sample.iterrows():
        cid = case_id(SCENARIO, SEX, run_idx=int(i))
        if args.resume and _is_run_complete(RUN_ROOT / cid):
            continue
        cfg = build_config(row, SCENARIO, SEX, cid)
        jobs.append((cfg, cid))
    skipped = len(sample) - len(jobs)
    print(f"[phase4b] launching {len(jobs)} runs ({skipped} skipped)")

    start = time.monotonic()
    if jobs:
        run_many(jobs, runs_root=RUN_ROOT, timeout_s=args.timeout_s, overwrite=False)
    elapsed = time.monotonic() - start
    print(f"[phase4b] runs done in {_format_hms(elapsed)}")

    # Aggregate
    df = aggregate_under(RUN_ROOT)
    cell_agg = RUN_ROOT / "aggregated.parquet"
    write_parquet(df, cell_agg)
    print(f"[phase4b] aggregated -> {cell_agg.relative_to(REPO_ROOT)}")

    # Morris indices on new sample
    morris_new = morris_indices(df, sample, [(SCENARIO, SEX)], n_bootstrap=1000)
    out_parquet = RESULTS / f"phase4b_morris_S2M_seed{SEED_NEW}.parquet"
    out_parquet.parent.mkdir(parents=True, exist_ok=True)
    morris_new.to_parquet(out_parquet, index=False)
    print(
        f"[phase4b] Morris indices -> {out_parquet.relative_to(REPO_ROOT)} ({len(morris_new)} rows)"
    )

    # Compare top-3 ranking vs canonical
    morris_canon = pd.read_parquet(REPO_ROOT / "data" / "audit_S015" / "morris_indices.parquet")
    morris_canon = morris_canon[(morris_canon.scenario == SCENARIO) & (morris_canon.sex == SEX)]

    rows = []
    for ch in morris_new["output"].unique():
        canon_ch = morris_canon[morris_canon.output == ch].sort_values("mu_star", ascending=False)
        new_ch = morris_new[morris_new.output == ch].sort_values("mu_star", ascending=False)
        canon_top3 = list(canon_ch["input"].head(3))
        new_top3 = list(new_ch["input"].head(3))
        rows.append(
            {
                "scenario": SCENARIO,
                "sex": SEX,
                "output": ch,
                "canon_top3": canon_top3,
                "new_top3": new_top3,
                "same_set": set(canon_top3) == set(new_top3),
                "same_order": canon_top3 == new_top3,
            }
        )
    cmp_df = pd.DataFrame(rows)
    cmp_path = RESULTS / f"phase4b_top3_comparison_seed{SEED_NEW}.csv"
    cmp_df.to_csv(cmp_path, index=False)
    print(f"\n=== top-3 ranking comparison (canonical seed=42 vs new seed={SEED_NEW}) ===")
    print(cmp_df.to_string(index=False))
    print(f"\n[phase4b] same set: {int(cmp_df.same_set.sum())}/{len(cmp_df)}")
    print(f"[phase4b] same order: {int(cmp_df.same_order.sum())}/{len(cmp_df)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
