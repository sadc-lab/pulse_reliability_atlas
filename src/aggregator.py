"""Aggregate atlas Pulse runs into a single Parquet table.

For each run directory under ``data/runs/``, this module:

    1. Loads ``config.json`` (input parameters + atlas_meta).
    2. Loads ``run_meta.json`` (exit code, wall time, image).
    3. Loads ``output.csv`` (Pulse channels) if it exists.
    4. Loads ``pulse.log`` (combined stdout+stderr).
    5. Calls `src.detector.classify` to compute the four flags + steady-state stats.
    6. Emits one flat row per run.

The resulting Parquet is the single source of truth for downstream Morris
analysis, clamp / divergence maps, and the sex-comparison stats.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from src.detector import HARD_BOUNDS, classify, OUTPUT_COLUMNS


# Channels for which we expand stats into the final row.
STAT_CHANNELS: tuple[str, ...] = tuple(OUTPUT_COLUMNS.keys())  # HR, MAP, Vt, SpO2, PaO2, PaCO2

# Locked input names that we extract from config.baselines / config.ventilator.
INPUT_NAMES: tuple[str, ...] = ("hr", "rr", "sbp", "dbp", "vt", "fio2", "peep")


@dataclass
class RunRow:
    """Flat record for one Pulse run."""

    data: dict[str, Any]


# ---------- Loaders ---------- #


def _load_json(p: Path) -> dict[str, Any]:
    with open(p) as f:
        return json.load(f)


def _read_log(p: Path) -> str:
    if not p.exists():
        return ""
    return p.read_text(errors="replace")


# ---------- Per-run row construction ---------- #


def build_row(run_dir: Path) -> dict[str, Any]:
    """Build one flat dict for a run directory. Missing files are tolerated —
    the resulting row will have its `diverged` flag set by the detector.
    """
    cfg_path = run_dir / "config.json"
    meta_path = run_dir / "run_meta.json"
    csv_path = run_dir / "output.csv"
    log_path = run_dir / "pulse.log"

    cfg = _load_json(cfg_path)
    meta = _load_json(meta_path) if meta_path.exists() else {}
    log_text = _read_log(log_path)

    atlas_meta = cfg.get("atlas_meta", {})
    baselines = cfg.get("baselines", {})
    vent = cfg.get("ventilator", {})

    row: dict[str, Any] = {
        "case_id": cfg.get("case_id", run_dir.name),
        "scenario": atlas_meta.get("scenario"),
        "sex": atlas_meta.get("sex"),
        "condition": cfg.get("condition"),
        "ards_severity": (
            cfg.get("ards_severity", {}).get("left")
            if "ards_severity" in cfg else 0.0
        ),
        # Inputs (applied — what was sent to Pulse)
        "in_hr":   baselines.get("hr"),
        "in_rr":   baselines.get("rr"),
        "in_sbp":  baselines.get("sbp"),
        "in_dbp":  baselines.get("dbp"),
        "in_vt":   vent.get("tidal_volume_ml"),
        "in_fio2": vent.get("fio2"),
        "in_peep": vent.get("peep_cmh2o"),
        # Atlas metadata (requested vs applied DBP, derived MAP, clip flag)
        "dbp_requested":   atlas_meta.get("dbp_requested"),
        "dbp_applied":     atlas_meta.get("dbp_applied"),
        "dbp_was_clipped": atlas_meta.get("dbp_was_clipped"),
        "map_derived":     atlas_meta.get("map_derived"),
        # Run meta
        "exit_code":   meta.get("exit_code"),
        "wall_time_s": meta.get("wall_time_s"),
        "image":       meta.get("image"),
    }

    result = classify(
        csv_path=csv_path if csv_path.exists() else None,
        pulse_log=log_text,
        exit_code=int(meta.get("exit_code", 1)),
    )

    # Flatten flag results
    flag_summary = result.summary()
    row.update(flag_summary)

    # Per-channel steady-state stats
    for ch in STAT_CHANNELS:
        s = result.stats.get(ch)
        if s is None:
            row[f"{ch}_mean"] = None
            row[f"{ch}_std"] = None
            row[f"{ch}_cv"] = None
            row[f"{ch}_slope_per_s"] = None
            row[f"{ch}_slope_r2"] = None
            row[f"{ch}_delta_60s"] = None
            row[f"{ch}_n_points"] = 0
        else:
            row[f"{ch}_mean"] = s.mean
            row[f"{ch}_std"] = s.std
            row[f"{ch}_cv"] = s.cv
            row[f"{ch}_slope_per_s"] = s.slope_per_s
            row[f"{ch}_slope_r2"] = s.slope_r2
            row[f"{ch}_delta_60s"] = s.delta_60s
            row[f"{ch}_n_points"] = s.n_points

    # Bounds metadata so the Parquet is self-describing if loaded later.
    for ch in STAT_CHANNELS:
        lo, hi = HARD_BOUNDS[ch]
        row[f"{ch}_bound_lo"] = lo
        row[f"{ch}_bound_hi"] = hi

    return row


def aggregate(run_dirs: Iterable[Path]) -> pd.DataFrame:
    """Build one DataFrame from many run directories."""
    rows = [build_row(Path(d)) for d in run_dirs]
    return pd.DataFrame(rows)


def aggregate_under(runs_root: Path | str) -> pd.DataFrame:
    """Walk ``runs_root`` and aggregate every run directory it contains."""
    root = Path(runs_root)
    run_dirs = sorted(p for p in root.iterdir() if p.is_dir())
    return aggregate(run_dirs)


def write_parquet(df: pd.DataFrame, path: Path | str) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(p, index=False)
    return p


__all__ = [
    "INPUT_NAMES",
    "STAT_CHANNELS",
    "aggregate",
    "aggregate_under",
    "build_row",
    "write_parquet",
]
