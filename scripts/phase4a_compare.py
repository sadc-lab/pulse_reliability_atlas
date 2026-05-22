"""Phase 4a — bit-exact comparison of repro vs canonical full_sweep.

Walks every (scenario, sex, case_id) under data/runs/full_sweep_repro/ and
compares the output.csv SHA-256 to the canonical at data/runs/full_sweep/.
For originally-diverged runs (no CSV in either), checks exit_code parity.

Writes a per-run report to data/runs/full_sweep_repro/sha_compare.json and
prints a summary.

Usage::

    uv run python scripts/phase4a_compare.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_ROOT = REPO_ROOT / "data" / "runs" / "full_sweep"
REPRO_ROOT = REPO_ROOT / "data" / "runs" / "full_sweep_repro"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if not REPRO_ROOT.exists():
        print(f"[compare] {REPRO_ROOT} missing — run phase4a_full_repro.py first")
        return 1

    results: list[dict] = []
    counters = {
        "BIT_EXACT": 0,
        "DIFFERS": 0,
        "BOTH_DIVERGED": 0,
        "ASYMMETRY": 0,
        "CANON_MISSING": 0,
        "REPRO_MISSING": 0,
    }

    for cell_dir in sorted(REPRO_ROOT.iterdir()):
        if not cell_dir.is_dir():
            continue
        canonical_cell = CANONICAL_ROOT / cell_dir.name
        if not canonical_cell.exists():
            print(f"[compare] WARN: no canonical for {cell_dir.name}", file=sys.stderr)
            continue
        for run_dir in sorted(cell_dir.iterdir()):
            if not run_dir.is_dir():
                continue
            cid = run_dir.name
            canon_run = canonical_cell / cid
            canon_csv = canon_run / "output.csv"
            repro_csv = run_dir / "output.csv"
            canon_meta = canon_run / "run_meta.json"
            repro_meta = run_dir / "run_meta.json"

            def _exit(p: Path) -> int | None:
                if not p.exists():
                    return None
                try:
                    return int(json.loads(p.read_text()).get("exit_code", 1))
                except (json.JSONDecodeError, OSError, ValueError):
                    return None

            canon_rc = _exit(canon_meta)
            repro_rc = _exit(repro_meta)

            entry: dict = {"case_id": cid, "canon_exit": canon_rc, "repro_exit": repro_rc}

            if canon_rc is None:
                entry["status"] = "CANON_MISSING"
            elif repro_rc is None:
                entry["status"] = "REPRO_MISSING"
            elif canon_rc != 0 and repro_rc != 0:
                entry["status"] = "BOTH_DIVERGED"
            elif (canon_rc == 0) != (repro_rc == 0):
                entry["status"] = "ASYMMETRY"
            else:
                # Both clean → compare CSV
                if not canon_csv.exists():
                    entry["status"] = "CANON_MISSING"
                elif not repro_csv.exists():
                    entry["status"] = "REPRO_MISSING"
                else:
                    canon_sha = sha256(canon_csv)
                    repro_sha = sha256(repro_csv)
                    entry["canon_sha"] = canon_sha
                    entry["repro_sha"] = repro_sha
                    entry["status"] = "BIT_EXACT" if canon_sha == repro_sha else "DIFFERS"

            counters[entry["status"]] = counters.get(entry["status"], 0) + 1
            results.append(entry)

    total = sum(counters.values())
    report = {"counters": counters, "total": total, "results": results}
    out = REPRO_ROOT / "sha_compare.json"
    out.write_text(json.dumps(report, indent=2))

    print(f"[compare] total compared: {total}")
    for k, v in counters.items():
        print(f"  {k}: {v}")
    print(f"[compare] report -> {out.relative_to(REPO_ROOT)}")

    return 0 if counters.get("DIFFERS", 0) == 0 and counters.get("ASYMMETRY", 0) == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
