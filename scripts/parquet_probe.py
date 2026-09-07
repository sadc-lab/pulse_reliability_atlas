#!/usr/bin/env python3
"""Read-only inspector for a local parquet or CSV artefact.

Why this exists
---------------
Several manuscript numbers are stated in prose but are not re-derived by any
ledger anchor, so answering "is this figure still true?" means looking inside
the artefact. Running an ad-hoc interpreter for that would mean allowlisting
arbitrary code execution, which `CLAUDE.md` forbids. This script is the
least-privilege alternative, and the exact twin of `scripts/pdf_probe.py`: a
fixed, versioned, auditable tool that can only read a table and print rows.

It was written on 2026-09-07, after a stale figure was found by accident: the
S021 plateau data was repaired on 2026-09-02 and one tracked figure that reads
it was last regenerated on 2026-08-04, so the minimum of the six runaway
plateaus moved from 779 to 770 mmHg while the supplement kept saying 779.
Settling which of that sentence's three numbers is wrong needs the rows.

Guarantees, by construction
---------------------------
* It never writes a file: no `open(..., 'w')`, no `os.remove`, no `Path.write_*`.
* It never touches the network: no socket, requests, urllib or subprocess import.
* It never evaluates user input: filters are a fixed operator table, never
  `eval`, `query()` or `getattr` on a user string.
* Its only side effect is printing to stdout.

Anyone extending this file must preserve those four properties.

Usage
-----
    uv run python scripts/parquet_probe.py <file> --columns
    uv run python scripts/parquet_probe.py <file> --select a,b --limit 20
    uv run python scripts/parquet_probe.py <file> \
        --where scenario eq S1 --where PaO2_plateau_mmHg gt 760 \
        --select case_id,PaO2_plateau_mmHg --sort PaO2_plateau_mmHg
    uv run python scripts/parquet_probe.py <file> --describe PaO2_plateau_mmHg

    --columns          list the columns and dtypes, then stop
    --select A,B       print only these columns
    --where COL OP VAL filter (repeatable); OP in eq ne lt le gt ge contains
    --sort COL         sort ascending by COL
    --desc             sort descending instead
    --limit N          print at most N rows (default 50, 0 means all)
    --describe COL     print count/min/median/max for one numeric column
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

# Fixed operator table. User input selects a key; it is never evaluated.
OPS = {
    "eq": lambda s, v: s.astype(str) == v,
    "ne": lambda s, v: s.astype(str) != v,
    "lt": lambda s, v: pd.to_numeric(s, errors="coerce") < float(v),
    "le": lambda s, v: pd.to_numeric(s, errors="coerce") <= float(v),
    "gt": lambda s, v: pd.to_numeric(s, errors="coerce") > float(v),
    "ge": lambda s, v: pd.to_numeric(s, errors="coerce") >= float(v),
    "contains": lambda s, v: s.astype(str).str.contains(v, regex=False, na=False),
}


def load(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    if path.suffix.lower() in (".csv", ".tsv"):
        return pd.read_csv(path, sep="\t" if path.suffix.lower() == ".tsv" else ",")
    raise SystemExit(f"  FAIL  unsupported extension: {path.suffix!r}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("file", help="path to a .parquet, .csv or .tsv file")
    ap.add_argument("--columns", action="store_true", help="list columns and stop")
    ap.add_argument("--select", default="", help="comma-separated columns to print")
    ap.add_argument(
        "--where", nargs=3, action="append", metavar=("COL", "OP", "VAL"), default=[]
    )
    ap.add_argument("--sort", default="", help="sort by this column")
    ap.add_argument("--desc", action="store_true", help="sort descending")
    ap.add_argument("--limit", type=int, default=50, help="max rows (0 = all)")
    ap.add_argument("--describe", default="", help="count/min/median/max of a column")
    args = ap.parse_args()

    path = Path(args.file)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[1] / path
    if not path.exists():
        print(f"  FAIL  not found: {path}")
        return 1

    df = load(path)
    print(f"## {path.name}: {len(df)} rows x {len(df.columns)} columns\n")

    if args.columns:
        for name, dtype in df.dtypes.items():
            print(f"  {name:<32} {dtype}")
        return 0

    for col, op, val in args.where:
        if col not in df.columns:
            print(f"  FAIL  no such column: {col!r}")
            return 1
        if op not in OPS:
            print(f"  FAIL  unknown operator {op!r}; use one of {sorted(OPS)}")
            return 1
        df = df[OPS[op](df[col], val)]
        print(f"  filter {col} {op} {val}  -> {len(df)} rows")

    if args.describe:
        if args.describe not in df.columns:
            print(f"  FAIL  no such column: {args.describe!r}")
            return 1
        s = pd.to_numeric(df[args.describe], errors="coerce").dropna()
        print(
            f"\n  {args.describe}: n={len(s)}  min={s.min():.6g}  "
            f"median={s.median():.6g}  max={s.max():.6g}"
        )
        return 0

    if args.sort:
        if args.sort not in df.columns:
            print(f"  FAIL  no such column: {args.sort!r}")
            return 1
        df = df.sort_values(args.sort, ascending=not args.desc)

    if args.select:
        cols = [c.strip() for c in args.select.split(",") if c.strip()]
        missing = [c for c in cols if c not in df.columns]
        if missing:
            print(f"  FAIL  no such column(s): {missing}")
            return 1
        df = df[cols]

    shown = df if args.limit == 0 else df.head(args.limit)
    print()
    with pd.option_context("display.max_columns", None, "display.width", 200):
        print(shown.to_string(index=False))
    if args.limit and len(df) > args.limit:
        print(f"\n  ({len(df) - args.limit} more rows not shown; --limit 0 for all)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
