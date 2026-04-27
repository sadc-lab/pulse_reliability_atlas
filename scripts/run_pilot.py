"""S005 pilot: 22-run gate before the full Morris sweep.

Implements `preregistration.md` §Pilot gate strictly. The pilot consists of:

    * 16 unique Morris-sampled points on cell (S1, Male) — from
      `sampler.sample_morris(trajectories=2, levels=4, seed=42)`. Trajectories=2
      is the smallest Morris geometry that still yields elementary effects
      across all 7 inputs and exercises grid extremes. Total 2 × (7+1) = 16
      unique points.
    * 4 reproducibility reruns: 2 picked points × 2 repeats each. The
      preregistration requires reruns of "2 pilot points"; running each of
      those 2 points twice gives a strict superset of the requirement and
      exercises Pulse determinism harder. Re-run case_ids live in a disjoint
      namespace (run_idx >= 9000) so they cannot collide with unique points.
    * 2 deliberate clamp probes: SBP=140 and DBP=85, both above Pulse's
      verified ceilings. The locked Morris ranges keep ALL sampled points
      inside Pulse's acceptance envelope by construction, so satisfying gate
      G4 (`clamped` regex actually fires) requires explicit out-of-range
      probes. The clamp probes are NOT part of the Morris sample and do not
      contaminate elementary effects — they live in their own case_id range
      (run_idx >= 9900).

Total: 22 runs (16 + 4 + 2). Output under ``data/runs/pilot_S1_M/``.

Pilot gate (all five must pass before the full sweep):

    G1. Success rate >= 50%  on the 16 Morris points (`diverged` <= 8/16)
    G2. Detector self-consistent (no run flagged both `clamped` AND
        `implausible` solely on the clamped value)
    G3. Steady-state window contains 13 rows on every clean Morris run
    G4. Log parser raises `clamped` flag on the explicit clamp probes
    G5. Reproducibility: rerun outputs match original within 1e-6 relative
        tolerance for all 6 outputs (stats means).

Usage::

    uv run python scripts/run_pilot.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.aggregator import STAT_CHANNELS, aggregate_under, write_parquet  # noqa: E402
from src.runner import run_many  # noqa: E402
from src.sampler import sample_morris, save_sample  # noqa: E402
from src.scenario import build_config, case_id  # noqa: E402


PILOT_SCENARIO = "S1"
PILOT_SEX = "M"
PILOT_TRAJECTORIES = 2
PILOT_LEVELS = 4
PILOT_SEED = 42

RERUN_INDICES: tuple[int, ...] = (0, 8)  # one early, one mid-trajectory
RERUNS_PER_INDEX: int = 2

# Disjoint case_id namespaces so reruns and probes never collide with the
# unique Morris points (which use run_idx ∈ [0, 15]).
RERUN_RUN_IDX_OFFSET: int = 9000   # rerun cid = 9000 + src_idx*10 + k
PROBE_RUN_IDX_OFFSET: int = 9900   # probe cid = 9900 + probe_idx

RUNS_ROOT = REPO_ROOT / "data" / "runs" / "pilot_S1_M"
SAMPLE_PATH = RUNS_ROOT / "morris_sample.parquet"


# Out-of-range clamp probes. Each entry overrides exactly one input outside the
# Pulse acceptance envelope to verify the `clamped` regex fires in practice.
CLAMP_PROBES: tuple[dict[str, float], ...] = (
    # Probe 1: SBP=140 above the Pulse ceiling (120). Verified to log
    # "is too high" + "Maximum systolic pressure baseline allowed is 120".
    {"hr": 80, "sbp": 140, "dbp": 75, "rr": 14, "vt": 550, "fio2": 0.6, "peep": 10},
    # Probe 2: DBP=85 above the Pulse ceiling (80). Symmetric probe — should
    # also fire `clamped` via the same regex set.
    {"hr": 80, "sbp": 110, "dbp": 85, "rr": 14, "vt": 550, "fio2": 0.6, "peep": 10},
)


def _rerun_case_id(src_idx: int, k: int) -> str:
    return case_id(
        PILOT_SCENARIO, PILOT_SEX, run_idx=RERUN_RUN_IDX_OFFSET + src_idx * 10 + k
    )


def _probe_case_id(probe_idx: int) -> str:
    return case_id(PILOT_SCENARIO, PILOT_SEX, run_idx=PROBE_RUN_IDX_OFFSET + probe_idx)


def _build_jobs() -> tuple[list[tuple[dict, str]], pd.DataFrame, list[str], list[str]]:
    """Return (jobs, sample_df, rerun_case_ids, probe_case_ids)."""
    sample = sample_morris(
        trajectories=PILOT_TRAJECTORIES, levels=PILOT_LEVELS, seed=PILOT_SEED
    )
    SAMPLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    save_sample(sample, SAMPLE_PATH)

    jobs: list[tuple[dict, str]] = []

    # 16 unique Morris points
    for i, row in sample.iterrows():
        cid = case_id(PILOT_SCENARIO, PILOT_SEX, run_idx=int(i))
        cfg = build_config(row, PILOT_SCENARIO, PILOT_SEX, cid)
        jobs.append((cfg, cid))

    # 4 reproducibility reruns (disjoint namespace)
    rerun_ids: list[str] = []
    for src_idx in RERUN_INDICES:
        src_row = sample.iloc[src_idx]
        for k in range(1, RERUNS_PER_INDEX + 1):
            cid = _rerun_case_id(int(src_idx), k)
            cfg = build_config(src_row, PILOT_SCENARIO, PILOT_SEX, cid)
            jobs.append((cfg, cid))
            rerun_ids.append(cid)

    # 2 deliberate clamp probes (disjoint namespace, DBP clip bypassed)
    probe_ids: list[str] = []
    for p_idx, probe in enumerate(CLAMP_PROBES):
        cid = _probe_case_id(p_idx)
        cfg = build_config(
            pd.Series(probe), PILOT_SCENARIO, PILOT_SEX, cid, clip_dbp=False
        )
        jobs.append((cfg, cid))
        probe_ids.append(cid)

    return jobs, sample, rerun_ids, probe_ids


def _evaluate_gates(
    df: pd.DataFrame,
    sample: pd.DataFrame,
    rerun_ids: list[str],
    probe_ids: list[str],
) -> dict[str, dict]:
    gates: dict[str, dict] = {}

    # Restrict G1, G2, G3 to the 16 Morris-sampled points (run_idx in [0, 15])
    morris_cids = {
        case_id(PILOT_SCENARIO, PILOT_SEX, run_idx=int(i)) for i in range(len(sample))
    }
    morris_df = df[df["case_id"].isin(morris_cids)]
    probe_df = df[df["case_id"].isin(probe_ids)]

    # G1 — Morris success rate >= 50%
    n_diverged = int(morris_df["diverged"].sum())
    n_morris = len(morris_df)
    gates["G1_success_rate"] = {
        "pass": n_diverged <= n_morris // 2,
        "n_morris": n_morris,
        "n_diverged": n_diverged,
        "criterion": "Morris diverged <= 50%",
    }

    # G2 — Detector self-consistent (across the entire pilot)
    bad = df[df["clamped"] & df["implausible"]]
    gates["G2_detector_self_consistent"] = {
        "pass": bad.empty,
        "n_double_flagged": int(len(bad)),
        "case_ids": list(bad["case_id"]),
        "criterion": "no run is both clamped AND implausible",
    }

    # G3 — Steady-state window has 13 rows on every clean Morris run
    clean = morris_df[morris_df["clean"]]
    n_points_cols = [f"{ch}_n_points" for ch in STAT_CHANNELS]
    if clean.empty:
        bad_n = pd.Series(dtype=int)
    else:
        bad_mask = (clean[n_points_cols] != 13).any(axis=1)
        bad_n = clean.loc[bad_mask, "case_id"]
    gates["G3_steady_state_13_rows"] = {
        "pass": bad_n.empty if not clean.empty else False,
        "n_clean": int(len(clean)),
        "violators": list(bad_n),
        "criterion": "13 rows in [60,120] for every channel of every clean Morris run",
    }

    # G4 — Clamp probes must fire `clamped`
    if probe_df.empty:
        gates["G4_clamped_fires"] = {
            "pass": False, "criterion": "clamp probes fired", "note": "no probes recorded",
        }
    else:
        n_probe_clamped = int(probe_df["clamped"].sum())
        gates["G4_clamped_fires"] = {
            "pass": n_probe_clamped == len(probe_df),
            "n_probes": int(len(probe_df)),
            "n_clamped": n_probe_clamped,
            "criterion": "every clamp probe fires the `clamped` regex",
        }

    # G5 — Reproducibility: each rerun matches its source within 1e-6 relative
    rep_violations: list[dict] = []
    for src_idx in RERUN_INDICES:
        src_cid = case_id(PILOT_SCENARIO, PILOT_SEX, run_idx=int(src_idx))
        if src_cid not in df["case_id"].values:
            continue
        src_row = df[df["case_id"] == src_cid].iloc[0]
        for k in range(1, RERUNS_PER_INDEX + 1):
            r_cid = _rerun_case_id(int(src_idx), k)
            if r_cid not in df["case_id"].values:
                continue
            r_row = df[df["case_id"] == r_cid].iloc[0]
            for ch in STAT_CHANNELS:
                a = src_row[f"{ch}_mean"]
                b = r_row[f"{ch}_mean"]
                if pd.isna(a) or pd.isna(b):
                    rep_violations.append(
                        {"src": src_cid, "rerun": r_cid, "channel": ch, "issue": "NaN"}
                    )
                    continue
                if abs(a) < 1e-12:
                    diff = abs(a - b)
                else:
                    diff = abs(a - b) / abs(a)
                if diff > 1e-6:
                    rep_violations.append(
                        {
                            "src": src_cid,
                            "rerun": r_cid,
                            "channel": ch,
                            "rel_diff": diff,
                            "src_val": a,
                            "rerun_val": b,
                        }
                    )
    gates["G5_reproducibility"] = {
        "pass": not rep_violations,
        "n_violations": len(rep_violations),
        "violations": rep_violations,
        "criterion": "reruns within 1e-6 relative for all 6 outputs",
    }

    return gates


def _print_gates(gates: dict[str, dict]) -> bool:
    print("\n=== Pilot gate evaluation ===")
    all_pass = True
    for name, info in gates.items():
        ok = info["pass"]
        all_pass = all_pass and ok
        marker = "PASS" if ok else "FAIL"
        print(f"  [{marker}] {name}: {info['criterion']}")
        for k, v in info.items():
            if k in ("pass", "criterion"):
                continue
            print(f"           {k} = {v}")
    print()
    return all_pass


def main() -> int:
    print(
        f"[pilot] cell=(S1,M)  trajectories={PILOT_TRAJECTORIES} "
        f"levels={PILOT_LEVELS} seed={PILOT_SEED}"
    )
    jobs, sample, rerun_ids, probe_ids = _build_jobs()
    print(
        f"[pilot] {len(jobs)} runs ({len(sample)} unique morris + "
        f"{len(rerun_ids)} reruns + {len(probe_ids)} clamp probes)"
    )

    run_many(jobs, runs_root=RUNS_ROOT, overwrite=True)

    df = aggregate_under(RUNS_ROOT)
    parquet = RUNS_ROOT / "aggregated.parquet"
    write_parquet(df, parquet)

    cols = [
        "case_id", "in_hr", "in_sbp", "in_dbp", "in_rr", "in_vt", "in_fio2",
        "in_peep", "exit_code", "diverged", "clamped", "implausible",
        "not_steady_state", "clean",
    ]
    print("\n=== Per-run summary ===")
    print(df[cols].to_string(index=False))

    gates = _evaluate_gates(df, sample, rerun_ids, probe_ids)
    all_pass = _print_gates(gates)

    if all_pass:
        print("[pilot] ALL GATES PASS — full sweep cleared.")
        return 0
    print("[pilot] FAIL — diagnose, amend preregistration if needed, re-pilot.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
