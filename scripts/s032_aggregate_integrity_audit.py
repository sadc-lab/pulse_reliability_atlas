"""S032 step 2 — integrity audit of the frozen aggregate against the raw CSVs.

Why
---
`data/runs/full_sweep/aggregated.parquet` is the single artefact behind the
Morris indices, the traffic-light map and 350 audited manuscript anchors. The
claims ledger checks the manuscript against that parquet; `provenance_check.py`
checks one cell against a fresh engine run. Nothing has ever checked the parquet
against the raw `output.csv` files it was built from, at full scale.

This closes that gap from the "garbage-in" end. It was originally specified as a
gate before reading raw systolic/diastolic channels for the bridge probes; those
probes are deferred, so it now stands alone as a repository integrity check.

How
---
- Reads `output.csv`, never `output_pulse_native.csv`. The native trace runs on a
  different clock (t_native = t_pipeline + 120 s, 0.02 s steps over 240 s) and a
  different cadence, so a mean taken there would not reproduce `map_mean` and the
  audit would fail for the wrong reason.
- Calls `src.detector.compute_steady_state_stats`, which owns the window rule
  (`time_s` in [60, 120] with a +/-1e-6 tolerance that captures the last sample at
  120.0000000000557). Re-implementing that filter without the tolerance silently
  drops one of the 13 points in every run.
- Every one of the 1,280 expected runs is accounted for: present and reproduced,
  or absent and matched one-to-one against the recorded divergences.

Pass criterion, fixed before running: 1,260 of 1,260 exact reproductions and
exactly 20 absences, all of them `diverged`. Any non-zero residual stops the
audit and prints diagnostics; no tolerance is chosen after seeing the numbers.

Usage::

    uv run python scripts/s032_aggregate_integrity_audit.py

Exit status: 0 = pass; 1 = any mismatch, missing-set disagreement or residual;
2 = missing input artefact.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.aggregator import STAT_CHANNELS  # noqa: E402
from src.detector import classify  # noqa: E402
from src.scenario import case_id, iter_cells  # noqa: E402

SWEEP = REPO / "data" / "runs" / "full_sweep"
MASTER = SWEEP / "aggregated.parquet"
RUNS_PER_CELL = 160
EXPECTED_TOTAL = 8 * RUNS_PER_CELL
EXPECTED_PRESENT = 1260
EXPECTED_ABSENT = 20


def main() -> int:
    if not MASTER.exists():
        print(f"[s032-audit] missing {MASTER}", file=sys.stderr)
        return 2
    agg = pd.read_parquet(MASTER).set_index("case_id")

    expected = [
        (sk, xk, case_id(sk, xk, run_idx=i))
        for sk, xk in iter_cells()
        for i in range(RUNS_PER_CELL)
    ]
    print(f"## Aggregate integrity audit\n\n- expected runs: {len(expected)}")
    if len(expected) != EXPECTED_TOTAL:
        print(f"[s032-audit] expected-run enumeration is {len(expected)}, not {EXPECTED_TOTAL}")
        return 1

    missing_from_parquet = [c for _, _, c in expected if c not in agg.index]
    if missing_from_parquet:
        print(f"[s032-audit] {len(missing_from_parquet)} expected runs absent from the parquet: "
              f"{missing_from_parquet[:5]}")
        return 1
    print(f"- all {len(expected)} present as parquet rows")

    absent_csv: list[str] = []
    residuals: list[tuple[str, str, float, float, float, int]] = []
    # Checking all six channels costs nothing beyond the MAP check: the same CSV
    # read and the same stats object serve them all, and it leaves no column of
    # the frozen aggregate unverified.
    reproduced = {ch: 0 for ch in STAT_CHANNELS}
    npoints: set[int] = set()

    # The five flag fields are re-derived too, not just the means. The parquet
    # was frozen on 2026-04-26; src/detector.py has changed five times since,
    # including 708efb1 (2026-07-26), which widened the clamp patterns. That
    # commit states the sweep is unaffected; this measures it independently.
    FLAG_FIELDS = ["clamped", "diverged", "implausible", "not_steady_state", "clean"]
    flag_agree = {f: 0 for f in FLAG_FIELDS}
    flag_diffs: list[tuple[str, str, object, object]] = []

    for sk, xk, cid in expected:
        run_dir = SWEEP / f"{sk}_{xk}" / cid
        csv = run_dir / "output.csv"
        log_p, meta_p = run_dir / "pulse.log", run_dir / "run_meta.json"
        log = log_p.read_text(encoding="utf-8", errors="replace") if log_p.exists() else ""
        exit_code = 0
        if meta_p.exists():
            exit_code = int(json.loads(meta_p.read_text(encoding="utf-8")).get("exit_code", 0))

        res = classify(csv if csv.exists() else None, pulse_log=log, exit_code=exit_code)
        summ = res.summary()
        for f in FLAG_FIELDS:
            here, there = bool(summ[f]), bool(agg.loc[cid, f])
            if here == there:
                flag_agree[f] += 1
            else:
                flag_diffs.append((cid, f, here, there))

        if not csv.exists():
            absent_csv.append(cid)
            continue
        stats = res.stats
        for ch in STAT_CHANNELS:
            s = stats.get(ch)
            there = agg.loc[cid, f"{ch}_mean"]
            if s is None:
                if pd.isna(there):
                    reproduced[ch] += 1
                else:
                    residuals.append((cid, ch, float("nan"), float(there), float("nan"), 0))
                continue
            npoints.add(s.n_points)
            d = abs(s.mean - float(there))
            if d == 0.0:
                reproduced[ch] += 1
            else:
                residuals.append((cid, ch, s.mean, float(there), d, s.n_points))

    present = len(expected) - len(absent_csv)
    print(f"- output.csv present: {present}   absent: {len(absent_csv)}")
    print(f"- steady-state window sizes observed: {sorted(npoints)}")
    print("\n| channel | exact reproductions | of |")
    print("|---|---|---|")
    for ch in STAT_CHANNELS:
        print(f"| {ch}_mean | {reproduced[ch]} | {present} |")

    print("\n| flag | agreements | of |")
    print("|---|---|---|")
    for f in FLAG_FIELDS:
        print(f"| {f} | {flag_agree[f]} | {len(expected)} |")

    ok = True
    if flag_diffs:
        ok = False
        print(f"\n[s032-audit] {len(flag_diffs)} flag disagreement(s) vs the frozen parquet:\n")
        print("| case_id | flag | today's detector | parquet |")
        print("|---|---|---|---|")
        for cid, f, here, there in flag_diffs[:20]:
            print(f"| {cid} | {f} | {here} | {there} |")

    # The absences must be exactly the recorded divergences -- same set, not just
    # the same count. A matching count with a different membership would mean a
    # CSV was lost from a run the pipeline believed had succeeded.
    diverged = set(agg.index[agg["diverged"].astype(bool)])
    absent = set(absent_csv)
    print(f"- recorded divergences: {len(diverged)}   absent CSVs: {len(absent)}")
    if absent != diverged:
        only_absent = sorted(absent - diverged)
        only_div = sorted(diverged - absent)
        print(f"[s032-audit] SET MISMATCH. Absent but not diverged: {only_absent}. "
              f"Diverged but CSV present: {only_div}.")
        ok = False
    else:
        print("- the two sets are identical (not merely equal in size)")

    if len(absent) != EXPECTED_ABSENT or any(v != EXPECTED_PRESENT for v in reproduced.values()):
        print(f"[s032-audit] counts differ from the pre-registered criterion "
              f"({EXPECTED_PRESENT} reproduced / {EXPECTED_ABSENT} absent)")
        ok = False

    if residuals:
        ok = False
        worst = sorted(residuals, key=lambda r: -(r[4] if r[4] == r[4] else 0.0))[:10]
        print(f"\n[s032-audit] {len(residuals)} run(s) did NOT reproduce. Worst offenders:\n")
        print("| case_id | channel | recomputed | parquet | abs diff | n points |")
        print("|---|---|---|---|---|---|")
        for cid, ch, here, there, d, n in worst:
            print(f"| {cid} | {ch} | {here!r} | {there!r} | {d:.6e} | {n} |")
        print("\nInspect the run, the window, the columns and the numeric dtype before")
        print("considering any tolerance. Do not choose one after seeing these numbers.")

    print(f"\n## Verdict: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
