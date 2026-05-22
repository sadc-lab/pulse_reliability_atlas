"""S015 P3.2 — negative control on detector.

Run the detector against a known-clean baseline Pulse run and assert
*no* flag fires. Picks the same case_id family as S007 used (S2_M
midrange healthy) but uses 5 known-clean cases from the full sweep so
this test is robust if any single CSV is later relocated.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from src.detector import classify  # noqa: E402

FULL_SWEEP = REPO / "data" / "runs" / "full_sweep"


def _safe(s: str) -> str:
    return s.encode("ascii", errors="replace").decode("ascii")


def main() -> int:
    print(_safe("=" * 70))
    print(_safe("S015 P3.2 - negative control on detector"))
    print(_safe("=" * 70))

    master = pd.read_parquet(FULL_SWEEP / "aggregated.parquet")
    clean_cases = master[master["clean"]]["case_id"].tolist()
    if len(clean_cases) < 5:
        print(_safe(f"FAIL: not enough clean cases in master ({len(clean_cases)})"))
        return 1

    # Pick 5 deterministically (one per scenario tier where possible)
    selected = []
    for sc in ("S1", "S2", "S3", "S4"):
        cands = [c for c in clean_cases if c.startswith(sc)]
        if cands:
            selected.append(cands[0])
    # Pad to 5
    for c in clean_cases:
        if c not in selected:
            selected.append(c)
        if len(selected) >= 5:
            break

    n_pass = 0
    for cid in selected:
        cell = "_".join(cid.split("_")[:2])
        rd = FULL_SWEEP / cell / cid
        csv = rd / "output.csv"
        log = rd / "pulse.log"
        meta = rd / "run_meta.json"
        if not csv.exists():
            print(_safe(f"FAIL {cid}: output.csv missing"))
            continue
        log_text = log.read_text(errors="replace") if log.exists() else ""
        import json

        exit_code = json.loads(meta.read_text())["exit_code"] if meta.exists() else 0

        result = classify(csv, pulse_log=log_text, exit_code=exit_code)
        flags = {
            "clamped": result.clamped.fired,
            "diverged": result.diverged.fired,
            "implausible": result.implausible.fired,
            "not_steady_state": result.not_steady_state.fired,
        }
        any_fired = any(flags.values())
        status = "PASS" if not any_fired else "FAIL"
        if status == "PASS":
            n_pass += 1
        # ASCII-safe stats summary
        means = ", ".join(f"{name}={s.mean:.3g}" for name, s in result.stats.items())
        print(_safe(f"[{status}] {cid}: flags={flags} primary={result.primary_flag} | {means}"))

    print()
    if n_pass == len(selected):
        print(_safe(f"All {n_pass}/{len(selected)} negative-control runs CLEAN as expected."))
        return 0
    print(_safe(f"FAIL: only {n_pass}/{len(selected)} ran clean."))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
