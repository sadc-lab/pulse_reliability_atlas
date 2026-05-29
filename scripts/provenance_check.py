"""Provenance spot-check: verify one cell's aggregated.parquet row against a
fresh Pulse Docker output.csv.

The 247-anchor claims-ledger audit (scripts/audit_claims.py) guarantees that
the manuscript text matches the frozen parquet artefacts; this script closes
the "garbage-in" gap from the *other* end: parquet vs fresh Pulse engine.

This is a SPOT-CHECK on a single cell. It catches wrapper / serializer /
runner drift on that one cell. Detecting a systematic solver change across
the full sweep requires a full re-run -- see PROVENANCE_CHECK.md.

Usage::

    # 1. Read a cell's exact inputs + the aggregated steady-state means
    uv run python scripts/provenance_check.py --cell S1_F_0117

    # 2. After a fresh Pulse Docker run, diff its output.csv vs the parquet:
    uv run python scripts/provenance_check.py --cell S1_F_0117 \\
        --fresh-output /path/to/fresh/output.csv

Exit status: 0 = all six channels within tolerance (or no fresh output supplied
and the inspection succeeded); 1 = at least one channel outside tolerance;
2 = bad arguments (cell unknown, file missing, columns absent).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from src.detector import OUTPUT_COLUMNS  # noqa: E402  -- HR -> "HeartRate", etc.

AGG_PARQUET = REPO / "data" / "runs" / "full_sweep" / "aggregated.parquet"

INPUT_COLS: tuple[str, ...] = (
    "in_hr", "in_rr", "in_sbp", "in_dbp", "in_vt", "in_fio2", "in_peep",
)
FLAG_COLS: tuple[str, ...] = (
    "clamped", "diverged", "implausible", "not_steady_state", "clean",
)


def steady_state_mean(
    df: pd.DataFrame, col: str, window_lo: float, window_hi: float
) -> float:
    sub = df[(df["time_s"] >= window_lo) & (df["time_s"] <= window_hi)]
    if sub.empty:
        raise RuntimeError(
            f"fresh output.csv has no samples in window [{window_lo}, "
            f"{window_hi}] s; cannot compute steady-state mean for '{col}'"
        )
    return float(sub[col].mean())


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Spot-check one aggregated.parquet row against a fresh Pulse "
            "Docker output.csv. See PROVENANCE_CHECK.md for the full protocol."
        )
    )
    parser.add_argument(
        "--cell",
        required=True,
        help="case_id in aggregated.parquet, e.g. 'S1_F_0117'.",
    )
    parser.add_argument(
        "--fresh-output",
        type=Path,
        default=None,
        help=(
            "Optional path to a fresh Pulse output.csv. Without this flag the "
            "script only prints the cell's inputs + aggregated values so a "
            "reviewer knows what to run in Docker."
        ),
    )
    parser.add_argument(
        "--tol-rel",
        type=float,
        default=1e-3,
        help=(
            "Relative-difference tolerance per channel (default 0.001 = 0.1%%). "
            "Pulse is deterministic given the same config, so a tight bound "
            "is appropriate; loosen only when investigating known drift."
        ),
    )
    parser.add_argument("--window-lo", type=float, default=60.0)
    parser.add_argument("--window-hi", type=float, default=120.0)
    args = parser.parse_args()

    if not AGG_PARQUET.exists():
        print(f"ERROR: {AGG_PARQUET.relative_to(REPO)} not found.", file=sys.stderr)
        return 2

    agg = pd.read_parquet(AGG_PARQUET)
    row_df = agg[agg["case_id"] == args.cell]
    if row_df.empty:
        print(
            f"ERROR: cell '{args.cell}' not in case_id column of "
            f"{AGG_PARQUET.relative_to(REPO)}.",
            file=sys.stderr,
        )
        return 2
    row = row_df.iloc[0]

    print(f"=== Cell {args.cell} ===")
    print(f"  scenario      : {row['scenario']}")
    print(f"  sex           : {row['sex']}")
    print(f"  condition     : {row.get('condition', '-')}")
    print(f"  ards_severity : {row.get('ards_severity', '-')}")
    print("  inputs (use these verbatim in the Pulse Docker config.json):")
    for col in INPUT_COLS:
        print(f"    {col:<10} = {row[col]}")
    print("  aggregated steady-state means (final 60 s window):")
    for ch in OUTPUT_COLUMNS:
        print(f"    {ch:<6} {float(row[f'{ch}_mean']):>12.4f}")
    print("  flags:")
    for flag in FLAG_COLS:
        print(f"    {flag:<18} = {bool(row[flag])}")

    if args.fresh_output is None:
        print()
        print("Next step: run Pulse Docker on the inputs above (see")
        print("reference/pulse_run_template.md), then rerun:")
        print(
            f"  uv run python scripts/provenance_check.py --cell {args.cell} "
            f"--fresh-output <path/to/output.csv>"
        )
        return 0

    if not args.fresh_output.exists():
        print(f"ERROR: --fresh-output path not found: {args.fresh_output}", file=sys.stderr)
        return 2

    fresh = pd.read_csv(args.fresh_output)
    for needed in ("time_s", *OUTPUT_COLUMNS.values()):
        if needed not in fresh.columns:
            print(
                f"ERROR: required column '{needed}' missing in {args.fresh_output}. "
                f"Is this a Pulse v4.3.1 output.csv?",
                file=sys.stderr,
            )
            return 2

    print()
    print(
        f"=== Comparison: fresh output.csv vs aggregated row "
        f"(tol_rel={args.tol_rel}, window=[{args.window_lo}, {args.window_hi}] s) ==="
    )
    header = f"  {'ch':<6} {'aggregated':>12}  {'fresh':>12}  {'|diff|':>10}  {'rel_diff':>10}  status"
    print(header)
    any_fail = False
    for ch, col in OUTPUT_COLUMNS.items():
        agg_val = float(row[f"{ch}_mean"])
        fresh_val = steady_state_mean(fresh, col, args.window_lo, args.window_hi)
        diff = abs(fresh_val - agg_val)
        rel = diff / abs(agg_val) if abs(agg_val) > 1e-12 else diff
        status = "PASS" if rel <= args.tol_rel else "FAIL"
        if status == "FAIL":
            any_fail = True
        print(
            f"  {ch:<6} {agg_val:>12.4f}  {fresh_val:>12.4f}  "
            f"{diff:>10.4g}  {rel:>10.4g}  {status}"
        )

    print()
    if any_fail:
        print("RESULT: FAIL -- at least one channel exceeds the tolerance.")
        print("This is a real divergence between the frozen parquet and the engine's")
        print("current output for this cell. Investigate before relying on the parquet.")
    else:
        print("RESULT: PASS -- all six channels within tolerance.")
        print("Spot-check confirms the parquet faithfully represents Pulse's output")
        print(f"for cell {args.cell}. (This does NOT prove the rest of the sweep.)")
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main())
