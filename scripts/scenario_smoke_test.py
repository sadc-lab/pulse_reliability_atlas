"""Tier 1.2 scenario-init smoke test (8 runs).

Mid-range Morris inputs across all 4 × 2 cells. Catches:
    * per-scenario init failures (esp. S4 ARDS=0.95 above the 0.91–0.945
      instability zone)
    * wrapper / image issues that would block the full pilot
    * confirms PaO2/PaCO2 emit on every cell

Usage::

    uv run python scripts/scenario_smoke_test.py

Writes runs into ``data/runs/scenario_smoke/`` and an aggregated Parquet at
``data/runs/scenario_smoke/aggregated.parquet``. A short text summary is
printed to stdout. Re-running overwrites all 8 runs.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.aggregator import aggregate_under, write_parquet  # noqa: E402
from src.runner import run_many  # noqa: E402
from src.scenario import (  # noqa: E402
    PATIENTS,
    SCENARIOS,
    build_config,
    case_id,
    iter_cells,
)


# Mid-range values for each Morris input, taken from the locked ranges
# (see preregistration §Inputs). DBP=70 satisfies 0.75*SBP=78.75 so no clip.
MIDRANGE: dict[str, float] = {
    "hr":   80.0,
    "sbp":  105.0,
    "dbp":  70.0,
    "rr":   14.0,
    "vt":   550.0,
    "fio2": 0.6,
    "peep": 10.0,
}

RUNS_ROOT = REPO_ROOT / "data" / "runs" / "scenario_smoke"


def main() -> int:
    sample_row = pd.Series(MIDRANGE)
    jobs: list[tuple[dict, str]] = []
    for scenario_key, sex_key in iter_cells():
        cid = case_id(scenario_key, sex_key, run_idx=0)
        cfg = build_config(sample_row, scenario_key, sex_key, cid)
        jobs.append((cfg, cid))

    print(f"[smoke] {len(jobs)} cells x 1 mid-range run each -> {RUNS_ROOT}")
    results = run_many(jobs, runs_root=RUNS_ROOT, overwrite=True)

    # Aggregate
    df = aggregate_under(RUNS_ROOT)
    parquet_path = RUNS_ROOT / "aggregated.parquet"
    write_parquet(df, parquet_path)

    # Summary
    print("\n=== Scenario smoke summary ===")
    cols = [
        "case_id", "scenario", "sex", "exit_code",
        "diverged", "clamped", "implausible", "not_steady_state",
        "HR_mean", "MAP_mean", "Vt_mean", "SpO2_mean", "PaO2_mean", "PaCO2_mean",
    ]
    df_summary = df[cols].copy()
    print(df_summary.to_string(index=False))

    n_total = len(df)
    n_clean = int(df["clean"].sum())
    n_diverged = int(df["diverged"].sum())
    print(
        f"\n[smoke] total={n_total}  clean={n_clean}  "
        f"diverged={n_diverged}  parquet={parquet_path.relative_to(REPO_ROOT)}"
    )

    # Hard fail if every scenario didn't even initialize. Single-cell failures
    # are *expected* on S4 (severe ARDS) and surface a real preregistration
    # decision; we surface them but don't crash.
    if n_diverged == n_total:
        print("[smoke] ERROR: all 8 cells diverged. Investigate before pilot.")
        return 2
    if n_clean == 0:
        print(
            "[smoke] WARNING: zero clean runs; all flagged. Pilot can still "
            "proceed but inspect individual flags."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
