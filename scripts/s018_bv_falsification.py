"""S018 — Blood-volume mechanism falsification test (Phase B item B2).

Re-execute the 20 originally-diverged male Morris inputs with two
BloodVolumeBaseline overrides:

* 4,082.24 mL — Pulse's stated minimum baseline for the male standard
  surrogate (67.3 kg, 180 cm); 15.0 % reduction vs the male default
  (4,802.63 mL). Setting BV below this triggers an explicit Pulse
  ``[ERROR]`` and exit 1 at setup. We use it as the largest BV-only
  reduction Pulse will accept on this body.
* 4,400 mL — intermediate bracket, ~8.4 % reduction. Gives a
  dose-response signal alongside the floor run.

Total: 20 × 2 = 40 runs. ~5-7 min/run × 40 / 2 parallel workers
≈ 100-140 min wall time.

Output: ``data/runs/s018_blood_volume/{floor,bracket}/<case_id>/``
plus ``data/runs/s018_blood_volume/s018_aggregated.parquet`` after
classification.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from src.runner import run_many

ROOT = Path(__file__).resolve().parents[1]

# The 20 originally-diverged runs (from results inspection; see also
# manuscript §3.5). 16 shared run_idx (119/157/158/159) across S1..S4_M
# plus 4 unique S4_M (24/82/137/138).
DIVERGED_CASES = [
    ("S1_M", "S1_M_0119"),
    ("S1_M", "S1_M_0157"),
    ("S1_M", "S1_M_0158"),
    ("S1_M", "S1_M_0159"),
    ("S2_M", "S2_M_0119"),
    ("S2_M", "S2_M_0157"),
    ("S2_M", "S2_M_0158"),
    ("S2_M", "S2_M_0159"),
    ("S3_M", "S3_M_0119"),
    ("S3_M", "S3_M_0157"),
    ("S3_M", "S3_M_0158"),
    ("S3_M", "S3_M_0159"),
    ("S4_M", "S4_M_0024"),
    ("S4_M", "S4_M_0082"),
    ("S4_M", "S4_M_0119"),
    ("S4_M", "S4_M_0137"),
    ("S4_M", "S4_M_0138"),
    ("S4_M", "S4_M_0157"),
    ("S4_M", "S4_M_0158"),
    ("S4_M", "S4_M_0159"),
]

# Resolved at setup time on the male standard surrogate (67.3 kg / 180 cm
# / age 18). Pulse computes the weight-derived default and prints the
# floor for the same body in pulse.log; both values are reproducible from
# any run with patient sex=Male.
MALE_DEFAULT_BV_ML = 4802.63
MALE_FLOOR_BV_ML = 4082.24

BV_BRACKETS = {
    "floor": MALE_FLOOR_BV_ML,
    "bracket": 4400.0,
}

SWEEP_DIR = ROOT / "data" / "runs" / "full_sweep"
S018_DIR = ROOT / "data" / "runs" / "s018_blood_volume"


def build_override_config(orig_case_dir: Path, bv_ml: float, label: str) -> tuple[dict, str]:
    """Read original config, inject blood_volume_ml override, return (cfg, new_case_id)."""
    cfg = json.loads((orig_case_dir / "config.json").read_text())
    orig_case_id = cfg["case_id"]
    new_case_id = f"{orig_case_id}_BV_{label}"
    cfg["case_id"] = new_case_id
    cfg["baselines"]["blood_volume_ml"] = bv_ml
    cfg.setdefault("atlas_meta", {})
    cfg["atlas_meta"]["bv_override_label"] = label
    cfg["atlas_meta"]["bv_override_ml"] = bv_ml
    cfg["atlas_meta"]["bv_male_default_ml"] = MALE_DEFAULT_BV_ML
    cfg["atlas_meta"]["bv_reduction_pct"] = 100.0 * (1 - bv_ml / MALE_DEFAULT_BV_ML)
    cfg["atlas_meta"]["original_case_id"] = orig_case_id
    cfg["atlas_meta"]["sex_override"] = f"M_with_BV_{label}_{int(bv_ml)}"
    return cfg, new_case_id


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="S018 — BV mechanism falsification")
    p.add_argument(
        "--image",
        default="pulse-atlas-engine:bv-override",
        help="Docker image with the BV-override patch (engine/run_atlas_engine.py).",
    )
    p.add_argument(
        "--bracket",
        choices=["floor", "bracket", "both"],
        default="both",
        help="Which BV value(s) to test. 'both' = full 40-run sweep.",
    )
    p.add_argument(
        "--workers",
        type=int,
        default=2,
        help="Parallel Docker workers (capped at 2 by src/runner.py for laptop budget).",
    )
    p.add_argument(
        "--timeout-s",
        type=float,
        default=600.0,
        help="Per-run timeout in seconds.",
    )
    args = p.parse_args(argv)

    labels_to_run = ["floor", "bracket"] if args.bracket == "both" else [args.bracket]

    jobs: list[tuple[dict, str]] = []
    for label in labels_to_run:
        bv_ml = BV_BRACKETS[label]
        for cell_dir, orig_case_id in DIVERGED_CASES:
            orig = SWEEP_DIR / cell_dir / orig_case_id
            if not (orig / "config.json").exists():
                raise FileNotFoundError(f"Missing original config: {orig / 'config.json'}")
            cfg, new_case_id = build_override_config(orig, bv_ml, label)
            jobs.append((cfg, new_case_id))

    runs_root = S018_DIR / args.bracket if args.bracket != "both" else S018_DIR
    runs_root.mkdir(parents=True, exist_ok=True)

    # If "both", we still want one flat dir, with case_id distinguishing label.
    target_root = S018_DIR / "runs"
    target_root.mkdir(parents=True, exist_ok=True)

    print(f"[s018] running {len(jobs)} job(s) (BV brackets: {labels_to_run})")
    print(f"[s018] image: {args.image}")
    print(f"[s018] output root: {target_root}")

    results = run_many(
        jobs,
        runs_root=target_root,
        image=args.image,
        max_workers=args.workers,
        timeout_s=args.timeout_s,
    )

    # Compact summary parquet alongside the run dirs.
    rows = []
    for r in results:
        cfg = json.loads(r.config_path.read_text())
        rows.append(
            {
                "case_id": r.case_id,
                "original_case_id": cfg["atlas_meta"].get("original_case_id"),
                "scenario": cfg["atlas_meta"].get("scenario"),
                "sex": cfg["atlas_meta"].get("sex"),
                "bv_override_label": cfg["atlas_meta"].get("bv_override_label"),
                "bv_override_ml": cfg["atlas_meta"].get("bv_override_ml"),
                "bv_reduction_pct": cfg["atlas_meta"].get("bv_reduction_pct"),
                "exit_code": r.exit_code,
                "wall_time_s": r.wall_time_s,
                "csv_present": r.csv_path is not None,
                "image": r.image,
            }
        )
    df = pd.DataFrame(rows)
    out_parquet = S018_DIR / "s018_run_index.parquet"
    df.to_parquet(out_parquet, index=False)
    print(f"[s018] wrote run index -> {out_parquet}")
    print(df.groupby(["bv_override_label", "exit_code"]).size())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
