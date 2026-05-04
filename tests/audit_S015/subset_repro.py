"""S015 P2 — stratified 40-run subset re-execution + bit-exact compare.

Picks 5 case_ids per (scenario × sex) cell from the original 1280-run
sweep using a fixed seed (42 — audit reproducibility), re-executes each
through the freshly rebuilt ``pulse-atlas-engine`` Docker image, and
compares the new ``output.csv`` byte-by-byte against the committed one.

Halt criterion: if any single CSV diverges, stop and report which channels
drifted before any further work.
"""

from __future__ import annotations

import filecmp
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from src.runner import run_many  # noqa: E402

SWEEP = REPO / "data" / "runs" / "full_sweep"
AUDIT_RUNS = REPO / "data" / "runs" / "s015_subset_repro"
AUDIT_LOG_DIR = REPO / "data" / "audit_S015"
AUDIT_LOG_DIR.mkdir(parents=True, exist_ok=True)

CELLS = [(s, x) for s in ("S1", "S2", "S3", "S4") for x in ("M", "F")]
N_PER_CELL = 5
SEED = 42
IMAGE = "pulse-atlas-engine"


def _file_sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def _csv_drift_detail(orig: Path, new: Path) -> dict:
    """Compare two CSVs row-by-row and column-by-column; return drift summary."""
    a = pd.read_csv(orig)
    b = pd.read_csv(new)
    out: dict = {
        "rows_orig": len(a),
        "rows_new": len(b),
        "cols_orig": list(a.columns),
        "cols_new": list(b.columns),
    }
    if len(a) != len(b) or list(a.columns) != list(b.columns):
        out["status"] = "STRUCTURAL_MISMATCH"
        return out
    drift_cols: list[dict] = []
    for c in a.columns:
        if a[c].dtype.kind in "fc":
            ma = a[c].to_numpy()
            mb = b[c].to_numpy()
            nan_ok = np.array_equal(np.isnan(ma), np.isnan(mb))
            close = np.isclose(ma, mb, atol=0.0, rtol=0.0, equal_nan=True)
            if not nan_ok or not close.all():
                bad = ~close
                idx = int(np.where(bad)[0][0]) if bad.any() else -1
                drift_cols.append({
                    "column": c,
                    "n_diff": int((~close).sum()),
                    "first_row": idx,
                    "first_orig": float(ma[idx]) if idx >= 0 else None,
                    "first_new": float(mb[idx]) if idx >= 0 else None,
                    "max_abs_diff": float(np.nanmax(np.abs(ma - mb))),
                })
        else:
            if not (a[c] == b[c]).all():
                drift_cols.append({"column": c, "type": "non-numeric mismatch"})
    out["drift_cols"] = drift_cols
    out["status"] = "DRIFT" if drift_cols else "BIT_EXACT"
    return out


def main() -> int:
    rng = np.random.default_rng(SEED)

    # Pick the subsample
    selection: list[tuple[str, str, str, dict, Path]] = []
    for sk, xk in CELLS:
        cell_dir = SWEEP / f"{sk}_{xk}"
        case_dirs = sorted([p for p in cell_dir.iterdir() if p.is_dir()])
        chosen = rng.choice(len(case_dirs), size=N_PER_CELL, replace=False)
        for ci in sorted(chosen.tolist()):
            d = case_dirs[ci]
            with open(d / "config.json") as f:
                cfg = json.load(f)
            selection.append((sk, xk, d.name, cfg, d / "output.csv"))

    print(f"[subset_repro] selected {len(selection)} runs (seed={SEED}):")
    for sk, xk, cid, _, _ in selection:
        print(f"  {cid}")

    # Wipe + rebuild audit run root
    if AUDIT_RUNS.exists():
        import shutil
        shutil.rmtree(AUDIT_RUNS)
    AUDIT_RUNS.mkdir(parents=True, exist_ok=True)

    # Re-execute via run_many (parallel up to 2 workers per S001 budget)
    jobs = [(cfg, cid) for _, _, cid, cfg, _ in selection]
    print(f"\n[subset_repro] re-running {len(jobs)} jobs through fresh {IMAGE} image ...")
    results = run_many(jobs, runs_root=AUDIT_RUNS, image=IMAGE)
    print(f"[subset_repro] all {len(results)} runs completed.")

    # Compare each output.csv
    report: list[dict] = []
    for sk, xk, cid, _, orig_csv in selection:
        new_csv = AUDIT_RUNS / cid / "output.csv"
        if not new_csv.exists():
            report.append({"case_id": cid, "status": "NEW_CSV_MISSING"})
            continue
        if not orig_csv.exists():
            report.append({"case_id": cid, "status": "ORIG_CSV_MISSING"})
            continue
        # Byte-exact via filecmp
        byte_exact = filecmp.cmp(orig_csv, new_csv, shallow=False)
        sha_orig = _file_sha256(orig_csv)
        sha_new = _file_sha256(new_csv)
        if byte_exact:
            report.append({
                "case_id": cid,
                "status": "BIT_EXACT",
                "sha256": sha_orig,
            })
        else:
            detail = _csv_drift_detail(orig_csv, new_csv)
            report.append({
                "case_id": cid,
                "status": detail["status"],
                "sha_orig": sha_orig,
                "sha_new": sha_new,
                "detail": detail,
            })

    # Save full report
    rep_path = AUDIT_LOG_DIR / "subset_repro_report.json"
    rep_path.write_text(json.dumps({
        "seed": SEED,
        "n_runs": len(selection),
        "image": IMAGE,
        "results": report,
    }, indent=2, default=str))

    # Summary
    print("\n" + "=" * 70)
    print("SUBSET RE-EXECUTION SUMMARY")
    print("=" * 70)
    by_status: dict[str, list[str]] = {}
    for r in report:
        by_status.setdefault(r["status"], []).append(r["case_id"])
    for s, cids in sorted(by_status.items()):
        print(f"  {s:>20s}: {len(cids):2d}")
        for c in cids:
            print(f"     - {c}")

    n_drift = sum(1 for r in report if r["status"] not in ("BIT_EXACT",))
    if n_drift > 0:
        print(f"\nFAILED — {n_drift} runs not bit-exact. Detail in {rep_path.relative_to(REPO)}.")
        return 1
    print(f"\nPASS — 40/40 runs bit-exact. Detail in {rep_path.relative_to(REPO)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
