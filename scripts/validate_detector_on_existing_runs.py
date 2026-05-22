"""Validate src/detector.py against existing Pulse runs in Pulse_translation_new.

Motivation
----------
The detector was designed for the atlas sweep: 120 s sims with 5 s sampling
(13 points in [60, 120]). The existing runs in `Pulse_translation_new` were
collected for Paper 1 with a different sampling cadence (often 30 s and
300 s total). We do NOT expect all of them to pass every check; the goal is
to see *which flags fire on which runs* and confirm the detector behaves
plausibly (clean runs look clean, known-bad runs get flagged).

Usage
-----
    uv run python scripts/validate_detector_on_existing_runs.py

Writes a summary CSV to `results/detector_validation_summary.csv` and prints
counts per flag to stdout.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import detector as d  # noqa: E402


# Path to the companion Pulse_translation_new repo's engine-runs directory.
# Default assumes a sibling checkout next to this repo; override with the
# PULSE_TRANSLATION_RUNS_DIR environment variable if it lives elsewhere.
# If neither the env var nor the default path resolves to an existing directory
# the script silently returns an empty run list (see find_runs() below), so
# external researchers without Paper 1's data can still execute this script
# without errors -- it simply has nothing to validate against.
_DEFAULT_TRANSLATION_DIR = ROOT.parent / "Pulse_translation_new" / "data" / "engine_runs"
TRANSLATION_DIR = Path(
    os.environ.get("PULSE_TRANSLATION_RUNS_DIR", str(_DEFAULT_TRANSLATION_DIR))
)
RESULTS_DIR = ROOT / "results"


def find_runs(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted([p.parent for p in root.glob("*/output.csv")])


def classify_one(run_dir: Path) -> dict[str, object]:
    csv = run_dir / "output.csv"
    # Relax expected_t_end so Paper 1's longer sims are not flagged "truncated".
    try:
        df = pd.read_csv(csv)
        expected = float(df["time_s"].max()) if "time_s" in df.columns else 120.0
    except Exception:
        expected = 120.0
    result = d.classify(csv, pulse_log="", exit_code=0, expected_t_end=expected)
    row: dict[str, object] = {"run": run_dir.name}
    row.update(result.summary())
    for name, s in result.stats.items():
        row[f"{name}_mean"] = s.mean
        row[f"{name}_cv"] = s.cv
        row[f"{name}_delta60s"] = s.delta_60s
    return row


def main() -> int:
    runs = find_runs(TRANSLATION_DIR)
    if not runs:
        print(f"No runs found under {TRANSLATION_DIR}")
        return 1

    rows = [classify_one(r) for r in runs]
    df = pd.DataFrame(rows)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = RESULTS_DIR / "detector_validation_summary.csv"
    df.to_csv(out_csv, index=False)

    print(f"Scanned {len(df)} runs under {TRANSLATION_DIR}")
    print(f"  clamped:          {int(df['clamped'].sum())}")
    print(f"  diverged:         {int(df['diverged'].sum())}")
    print(f"  implausible:      {int(df['implausible'].sum())}")
    print(f"  not_steady_state: {int(df['not_steady_state'].sum())}")
    print(f"  clean:            {int(df['clean'].sum())}")
    print(f"\nSummary written to {out_csv}")

    flagged = df[~df["clean"]].head(15)
    if not flagged.empty:
        print("\nFirst flagged runs (up to 15):")
        for _, row in flagged.iterrows():
            reasons = [
                f"{k}: {row[f'{k}_reason']}"
                for k in ["clamped", "diverged", "implausible", "not_steady_state"]
                if row[k] and row[f"{k}_reason"]
            ]
            print(f"  {row['run']}  ->  {' | '.join(reasons)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
