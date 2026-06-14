"""S018 bracket reproducibility test (2026-06-14 paranoia audit).

QUESTION
--------
The frozen s018_classified.parquet + manuscript + S018 log record 2/20
divergences at the BV=4,400 mL bracket (runs S4_M_0158, S4_M_0159,
`exit_code=1`). But those 2 run dirs on disk were re-executed minutes after
the parquet was frozen and now show `exit_code=0` + clean CSV, so raw
re-derivation gives 0/20. Were the 2 original failures:

  (A) transient infrastructure failures (Docker/OOM at the 1 GB cap on the
      heaviest S4-severe + FiO2=1.0 runs) -> not reproducible, real answer 0/20; or
  (B) a reproducible build-dependent failure -> the final bv-override image
      fails these configs deterministically.

METHOD
------
Re-run EXACTLY the two disputed bracket configs (rebuilt from the original
full_sweep configs via the same `build_override_config` S018 used), with the
final `pulse-atlas-engine:bv-override` image, BV=4,400 mL, N reps each, in
ISOLATION (one container at a time -> no parallel memory contention). If all
reps pass, the failure is not a deterministic property of (config, final image)
-> supports (A). If reps fail, inspect the logs.

Writes ONLY into data/runs/s018_bracket_repro/ (fresh dir). Does NOT touch the
canonical S018 artifacts.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.s018_bv_falsification import build_override_config  # noqa: E402
from src.runner import run_one  # noqa: E402
from verify_raw_rederivation import classify_run  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
SWEEP = REPO / "data" / "runs" / "full_sweep"
OUT_ROOT = REPO / "data" / "runs" / "s018_bracket_repro"
IMAGE = "pulse-atlas-engine:bv-override"
BV_BRACKET_ML = 4400.0
N_REPS = 5
CASES = [("S4_M", "S4_M_0158"), ("S4_M", "S4_M_0159")]


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    print(f"[repro] image={IMAGE}  BV={BV_BRACKET_ML} mL  reps={N_REPS}  "
          f"cases={[c for _, c in CASES]}")
    print(f"[repro] output root: {OUT_ROOT}  (canonical S018 data untouched)\n")

    summary: dict[str, list[dict]] = {}
    for cell, orig_case_id in CASES:
        orig_dir = SWEEP / cell / orig_case_id
        cfg_base, base_case_id = build_override_config(orig_dir, BV_BRACKET_ML, "bracket")
        summary[orig_case_id] = []
        for k in range(1, N_REPS + 1):
            cfg = json.loads(json.dumps(cfg_base))  # deep copy
            rep_case_id = f"{base_case_id}_rep{k}"
            cfg["case_id"] = rep_case_id
            res = run_one(cfg, rep_case_id, OUT_ROOT, image=IMAGE, timeout_s=600.0)
            flags = classify_run(res.run_dir)
            rec = {
                "rep": k,
                "exit_code": res.exit_code,
                "wall_time_s": round(res.wall_time_s, 1),
                "csv_present": res.csv_path is not None,
                "diverged": flags["diverged"],
                "primary": flags["primary"],
            }
            summary[orig_case_id].append(rec)
            print(f"[repro] {orig_case_id} rep{k}: exit={res.exit_code} "
                  f"diverged={flags['diverged']} primary={flags['primary']} "
                  f"({res.wall_time_s:.0f}s)")

    print("\n=== SUMMARY ===")
    verdict_lines = []
    for case_id, recs in summary.items():
        n_div = sum(r["diverged"] for r in recs)
        n = len(recs)
        print(f"\n{case_id}: {n_div}/{n} diverged across reps")
        for r in recs:
            print(f"   rep{r['rep']}: exit={r['exit_code']} "
                  f"diverged={r['diverged']} ({r['wall_time_s']}s)")
        verdict_lines.append(f"{case_id}: {n_div}/{n} diverged")

    total_div = sum(sum(r["diverged"] for r in recs) for recs in summary.values())
    total = sum(len(recs) for recs in summary.values())
    print(f"\nOVERALL: {total_div}/{total} reps diverged.")
    if total_div == 0:
        print("VERDICT -> all reps PASS with the final bv-override image. The original "
              "exit_code=1 failures are NOT reproducible in isolation -> consistent with "
              "(A) transient infra (likely OOM/contention at the 1 GB cap). The true "
              "bracket dose-response point is 0/20, not 2/20.")
    elif total_div == total:
        print("VERDICT -> all reps FAIL deterministically -> consistent with (B) a "
              "reproducible build/config failure; the post-freeze re-runs that succeeded "
              "need explaining (different image build?).")
    else:
        print("VERDICT -> MIXED pass/fail -> genuinely flaky/non-deterministic at the "
              "infra level on these heaviest runs. Inspect logs for OOM signatures.")

    (OUT_ROOT / "_repro_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\n[repro] summary JSON -> {OUT_ROOT / '_repro_summary.json'}")


if __name__ == "__main__":
    main()
