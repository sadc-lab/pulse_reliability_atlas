"""S009 — seed-stability check (Tier 2).

Re-runs the Morris sweep with a different seed on a single cell and
compares the resulting mu_star ranking to the published one. Tests whether
the Morris analysis is robust to the specific Morris sample drawn.

Design:
    * Cell: (S2, M) — the best-behaved cell in the published sweep
      (S2_M had clean rate 87/160, all 7 inputs covered).
    * Trajectories: 10 (half the published 20) — keeps compute under
      ~50 min at 2-worker parallelism while still giving 80 EEs per
      input on average.
    * Seed: 43 (vs published seed = 42).
    * Levels: 4 (matching published).

Output:
    data/runs/seed_stability_S2M_seed43/
    results/seed_stability_S2M_seed43.parquet  (Morris indices)
    results/seed_stability_top3_comparison.csv (ranking diff)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.aggregator import aggregate_under, write_parquet  # noqa: E402
from src.analysis_morris import morris_indices  # noqa: E402
from src.runner import run_many  # noqa: E402
from src.sampler import sample_morris, save_sample  # noqa: E402
from src.scenario import build_config, case_id  # noqa: E402

SEED_NEW = 43
TRAJECTORIES = 10
LEVELS = 4
SCENARIO = "S2"
SEX = "M"

RUN_ROOT = REPO_ROOT / "data" / "runs" / "seed_stability_S2M_seed43"
SAMPLE_PATH = RUN_ROOT / "morris_sample.parquet"
RESULTS = REPO_ROOT / "results"


def main() -> int:
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    sample = sample_morris(trajectories=TRAJECTORIES, levels=LEVELS, seed=SEED_NEW)
    save_sample(sample, SAMPLE_PATH)
    print(
        f"[seed-stability] new sample: traj={TRAJECTORIES} seed={SEED_NEW} "
        f"levels={LEVELS} -> {len(sample)} unique points"
    )

    jobs = []
    for i, row in sample.iterrows():
        cid = case_id(SCENARIO, SEX, run_idx=int(i))
        cfg = build_config(row, SCENARIO, SEX, cid)
        jobs.append((cfg, cid))

    run_many(jobs, runs_root=RUN_ROOT, overwrite=False)

    df = aggregate_under(RUN_ROOT)
    cell_parquet = RUN_ROOT / "aggregated.parquet"
    write_parquet(df, cell_parquet)

    # Compute Morris indices on this fresh sample
    morris_new = morris_indices(df, sample, [(SCENARIO, SEX)], n_bootstrap=1000)
    out_parquet = RESULTS / "seed_stability_S2M_seed43.parquet"
    morris_new.to_parquet(out_parquet, index=False)
    print(f"[seed-stability] new Morris indices -> {out_parquet.relative_to(REPO_ROOT)}")
    print(f"[seed-stability]    rows: {len(morris_new)}")

    # Compare top-3 rankings
    morris_old = pd.read_parquet(RESULTS / "morris_indices.parquet")
    morris_old = morris_old[
        (morris_old.scenario == SCENARIO) & (morris_old.sex == SEX)
    ]

    rows = []
    for ch in morris_new["output"].unique():
        old_ch = morris_old[morris_old.output == ch].sort_values("mu_star", ascending=False)
        new_ch = morris_new[morris_new.output == ch].sort_values("mu_star", ascending=False)
        old_top3 = list(old_ch["input"].head(3))
        new_top3 = list(new_ch["input"].head(3))
        same_set = set(old_top3) == set(new_top3)
        same_order = old_top3 == new_top3
        rows.append({
            "scenario": SCENARIO,
            "sex": SEX,
            "output": ch,
            "old_top3": old_top3,
            "new_top3": new_top3,
            "same_set": same_set,
            "same_order": same_order,
        })
    cmp_df = pd.DataFrame(rows)
    cmp_path = RESULTS / "seed_stability_top3_comparison.csv"
    cmp_df.to_csv(cmp_path, index=False)
    print("\n=== top-3 ranking comparison (seed=42 vs seed=43) ===")
    print(cmp_df.to_string(index=False))
    print(f"\n[seed-stability] same set: {int(cmp_df.same_set.sum())}/{len(cmp_df)}")
    print(f"[seed-stability] same order: {int(cmp_df.same_order.sum())}/{len(cmp_df)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
