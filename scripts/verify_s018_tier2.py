"""S018 Tier-2 full re-run (2026-06-16): all 20 originally-diverged male cases,
two arms, controlled isolation.

Questions:
  (A) do all 20 cases clear at BV=4,400 (bracket)?  -> bracket dose-response point
  (B) do the 20 cases reproducibly diverge at the DEFAULT (allometric) BV?
      -> H3 robustness check (Yassir's bar #3): are the headline divergences
      genuine deterministic Pulse rejections, not transient/race artifacts?

Both arms use the SAME final image (pulse-atlas-engine:bv-override) so BV is the
only variable: the "default" arm runs the original full_sweep config as-is (no
blood_volume_ml field -> Pulse uses the allometric default); the "bracket" arm
injects blood_volume_ml=4,400. The bv-override engine code only injects BV when
the field is present, so the default arm reproduces the base engine behavior.

Default arm runs FIRST (the contested result), so a mid-run interruption still
leaves the H3 evidence. Writes ONLY to data/runs/s018_tier2_repro/ (fresh dir);
does not touch any canonical artifact.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.s018_bv_falsification import DIVERGED_CASES, build_override_config  # noqa: E402
from scripts.verify_raw_rederivation import classify_run  # noqa: E402
from src.runner import run_one  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
SWEEP = REPO / "data" / "runs" / "full_sweep"
OUT_ROOT = REPO / "data" / "runs" / "s018_tier2_repro"
IMAGE = "pulse-atlas-engine:bv-override"
BV_BRACKET_ML = 4400.0
N_REPS = 2


def run_arm(arm: str, results: list[dict]) -> None:
    """Run all 20 cases for one arm (default | bracket), N_REPS each."""
    print(f"\n########## ARM = {arm} ##########", flush=True)
    for cell, case_id in DIVERGED_CASES:
        orig = SWEEP / cell / case_id
        if arm == "default":
            base_cfg = json.loads((orig / "config.json").read_text())
            base_cfg.pop("atlas_meta", None)  # keep it a clean default config
            label = "def"
        else:
            base_cfg, _ = build_override_config(orig, BV_BRACKET_ML, "bracket")
            label = "brk"
        for k in range(1, N_REPS + 1):
            cfg = json.loads(json.dumps(base_cfg))
            cid = f"{case_id}_{label}_rep{k}"
            cfg["case_id"] = cid
            res = run_one(cfg, cid, OUT_ROOT, image=IMAGE, timeout_s=600.0)
            flags = classify_run(res.run_dir)
            rec = {
                "arm": arm, "case": case_id, "rep": k,
                "exit_code": res.exit_code,
                "diverged": flags["diverged"],
                "primary": flags["primary"],
                "csv_present": res.csv_path is not None,
                "wall_s": round(res.wall_time_s, 1),
            }
            results.append(rec)
            print(f"[{arm}] {case_id} rep{k}: exit={res.exit_code} "
                  f"diverged={flags['diverged']} primary={flags['primary']} "
                  f"({res.wall_time_s:.0f}s)", flush=True)
            # incremental save so a mid-run interruption keeps partial evidence
            (OUT_ROOT / "_tier2_progress.json").write_text(json.dumps(results, indent=2))


def summarize(results: list[dict]) -> None:
    print("\n\n=== TIER-2 SUMMARY ===", flush=True)
    for arm in ("default", "bracket"):
        arm_recs = [r for r in results if r["arm"] == arm]
        if not arm_recs:
            print(f"\n[{arm}] (not run / no results)")
            continue
        by_case: dict[str, list[dict]] = {}
        for r in arm_recs:
            by_case.setdefault(r["case"], []).append(r)
        n_cases = len(by_case)
        # a case "diverges" in this arm if it diverged in ALL its reps (deterministic);
        # flag any case that is inconsistent across reps.
        all_div = sum(1 for recs in by_case.values() if all(x["diverged"] for x in recs))
        none_div = sum(1 for recs in by_case.values() if not any(x["diverged"] for x in recs))
        flaky = [c for c, recs in by_case.items()
                 if any(x["diverged"] for x in recs) and not all(x["diverged"] for x in recs)]
        print(f"\n[{arm}] {n_cases} cases x {N_REPS} reps")
        print(f"   diverged in ALL reps   : {all_div}/{n_cases}")
        print(f"   clean in ALL reps      : {none_div}/{n_cases}")
        print(f"   FLAKY (rep-inconsistent): {len(flaky)}  {flaky if flaky else ''}")
    print("\nInterpretation key:")
    print("  default arm all-diverged ~20/20 -> headline divergences are genuine"
          " deterministic rejections (H3 robust).")
    print("  bracket arm none-diverged ~0/20 -> committed 20->2->0 '2' is an"
          " artifact; true dose-response 20->0->0.")
    print("  any FLAKY case -> genuine non-determinism, needs its own look.")


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    print(f"[tier2] image={IMAGE}  reps={N_REPS}  cases={len(DIVERGED_CASES)}  "
          f"arms=default(first),bracket", flush=True)
    print(f"[tier2] output: {OUT_ROOT}  (canonical data untouched)", flush=True)
    results: list[dict] = []
    run_arm("default", results)   # contested H3 check first
    run_arm("bracket", results)
    summarize(results)
    (OUT_ROOT / "_tier2_summary.json").write_text(json.dumps(results, indent=2))
    print(f"\n[tier2] full results -> {OUT_ROOT / '_tier2_summary.json'}", flush=True)


if __name__ == "__main__":
    main()
