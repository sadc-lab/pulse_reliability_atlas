"""S019 — restricted exploratory Sobol demonstrator: DRAFT, NOT EXECUTED.

This script is NOT an implementation of the preregistered Sobol bolt-on
and must not be cited as one. It is a restricted exploratory
demonstrator, written in May 2026 under a reading of the preregistered
trigger that has since been withdrawn, and it is preserved for
provenance rather than as a runnable version of the preregistered
design.

----------------------------------------------------------------------
What it does, and how that differs from the preregistration
----------------------------------------------------------------------

                    preregistration           this script
  cells             every cell with a top-3   the 6 cells fixed
                    input at sigma/mu* >=     below, chosen on the
                    0.6: 43 of 48 cell x      DOMINANT input, with
                    output combinations,      2 more excluded
                    falling in all 8 cells
  inputs            "Sobol on that input";    all 7 swept inputs
                    cost k = inputs promoted
  base sample       64                        256, first-order only

The costs follow from that. A Sobol sample is shared across the six
outputs of one cell but not across cells, so the preregistered design
costs 64 x (2k + 2) summed over the 8 cells, with k = 3 to 6 distinct
promoted inputs per cell: 6,144 runs, or 3,584 at 64 x (k + 2) for the
first-order and total indices only. Those are the figures the manuscript
quotes (Supplement S3-sobol; sobol_ci_buckets.py). An earlier reading
billed 43 "cells" at 256 runs = 11,008; it counted cell x output
combinations as cells and is withdrawn (sobol_ci_buckets.json,
"sobol_runs_unshared_k1_withdrawn"). This script is 6 cells at
N x (D + 2) = 256 x 9 = 2,304 rows each = 13,824 runs.

What it does share with the sweep is the locked input-space definition
(`src.sampler.salib_problem()`) and RNG seed 42, so any indices it
produced would be comparable to the Morris mu*/sigma in
`results/morris_indices.parquet` cell-for-cell.

----------------------------------------------------------------------
Provenance, and why the framing changed
----------------------------------------------------------------------

The 6-cell scope comes from the Group-A / Group-B split of an earlier
dominant-input analysis. The script was written to support a conclusion
that S031 has since withdrawn: that the bolt-on could be settled on the
bootstrap CI evidence rather than on cost. The current reason it was not
executed is compute budget -- the design the trigger selects exceeds the
preregistered 1,500-run envelope. See manuscript S3.3.1 and
experiments_log/santino/S031_sobol_reframe_and_nonlinearity.md.

One part of the older reasoning survives that withdrawal, and is why the
2 Group-A cells stay excluded below: SpO2 sits at its saturation ceiling
(~0.997) in the healthy respiratory envelope, which makes sigma/mu*
mathematically large and physiologically empty. That is a property of
the physiology, not of the retracted CI argument.

At the default N = 256 the cost is ~13,824 Pulse runs; at ~30 s/run on
2 parallel laptop workers, ~58 hours wall time — laptop-infeasible.
Cluster or Colab is required.

----------------------------------------------------------------------
The 6 Group-B cells (manuscript §3.3.1)
----------------------------------------------------------------------

Cells where the dominant input exhibits σ / μ* ≥ 0.6 (point
estimate) AND the dominant input is part of an established
physiological nonlinearity (not numerical-saturation noise like
the 2 Group-A SpO2 cells, which are excluded):

    (S2, M, PaO2, dominant input FiO2)
    (S2, F, PaO2, dominant input FiO2)
    (S3, M, PaO2, dominant input FiO2)
    (S3, F, PaO2, dominant input FiO2)
    (S1, M, PaCO2, dominant input RR)
    (S4, F, PaCO2, dominant input V_t)

The Sobol sample is over the full 7-input space (HR, SBP, DBP, RR,
V_t, FiO_2, PEEP); the "dominant input" labels above identify which
input drove each cell into the σ / μ* > 0.6 regime, but Sobol
returns S₁ / S_t for *every* input so the dominant-input ranking
in §3.2 can be independently re-validated per cell.

----------------------------------------------------------------------
How to execute (when cluster compute is available)
----------------------------------------------------------------------

    # 1. Build the BV-untouched atlas image (the original sweep image).
    docker pull pulse-atlas-engine:latest          # or rebuild locally

    # 2. Dry-run on a single cell to verify the protocol on small N.
    uv run --no-project --with pandas --with pyarrow --with SALib python \\
        scripts/s019_sobol_bolton.py \\
        --dry-run \\
        --cells S2_M \\
        --N 8

    # 3. Full N=256 sweep on the 6 cells (cluster).
    uv run --no-project --with pandas --with pyarrow --with SALib python \\
        scripts/s019_sobol_bolton.py \\
        --N 256 \\
        --workers 2 \\
        --output-root data/runs/s019_sobol

    # 4. Aggregate + compute S₁ / S_t indices.
    uv run --no-project --with pandas --with pyarrow --with SALib python \\
        scripts/s019_sobol_bolton.py \\
        --analyse-only \\
        --output-root data/runs/s019_sobol \\
        --indices-out results/sobol_indices.parquet

----------------------------------------------------------------------
Cluster / Colab notes
----------------------------------------------------------------------

* The script consumes the locked Morris-sample input bounds
  (`src.sampler.salib_problem()`) so the Sobol indices are
  comparable to the Morris μ*/σ in `results/morris_indices.parquet`
  cell-for-cell.
* RNG seed is fixed at 42 (consistent with the Morris sweep) for
  reproducibility.
* Each Sobol sample point is materialised as a per-cell atlas config
  via `src.scenario.build_config()` — exactly the same code path
  as the Morris sweep, so any clamping / divergence behaviour is
  attributable to the engine, not a wrapper artefact.
* The script writes per-cell run directories under
  ``data/runs/s019_sobol/<cell>/<case_id>/`` so the existing
  `src.aggregator` and `src.detector` work without modification.
* Resume-safe: skips cases whose `output.csv` already exists.

----------------------------------------------------------------------
DO NOT EXECUTE WITHOUT EXPLICIT USER AUTHORIZATION ON A MACHINE WITH
A 24 + HOUR COMPUTE BUDGET. The laptop default is 2 parallel workers
(`src.runner.MAX_PARALLEL_LAPTOP`); raising it requires re-verifying
the RAM / CPU headroom (see S001).
----------------------------------------------------------------------
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from src.runner import run_many
from src.sampler import INPUT_NAMES, NUM_INPUTS, salib_problem
from src.scenario import build_config


ROOT = Path(__file__).resolve().parents[1]


# ----------------------------------------------------------------------
# The 6 Group-B cells — manuscript §3.3.1.
# ----------------------------------------------------------------------


@dataclass(frozen=True)
class GroupBCell:
    scenario: str  # "S1".."S4"
    sex: str  # "M" or "F"
    output: str  # "PaO2" or "PaCO2"
    dominant_input: str  # "fio2" / "rr" / "vt" — what drove the σ / μ* > 0.6 trigger


GROUP_B_CELLS: tuple[GroupBCell, ...] = (
    GroupBCell("S2", "M", "PaO2", "fio2"),
    GroupBCell("S2", "F", "PaO2", "fio2"),
    GroupBCell("S3", "M", "PaO2", "fio2"),
    GroupBCell("S3", "F", "PaO2", "fio2"),
    GroupBCell("S1", "M", "PaCO2", "rr"),
    GroupBCell("S4", "F", "PaCO2", "vt"),
)


# ----------------------------------------------------------------------
# Sample generation
# ----------------------------------------------------------------------


def sample_sobol(
    N: int = 256,
    calc_second_order: bool = False,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate a Sobol sample over the locked 7-input space.

    Returns a DataFrame with `num_inputs` columns (one per swept
    input) plus an integer index column ``run_idx`` for stable case
    identifiers downstream.

    Row count per the SALib convention:

        calc_second_order = False :  N × (D + 2)
        calc_second_order = True  :  N × (2 D + 2)

    For D = 7, N = 256, first-order-only → 2,304 rows per cell.
    """
    from SALib.sample import sobol as sobol_sampler  # local import (optional dep)

    problem = salib_problem()
    arr = sobol_sampler.sample(
        problem,
        N=N,
        calc_second_order=calc_second_order,
        seed=seed,
    )
    expected_rows = N * (2 * NUM_INPUTS + 2 if calc_second_order else NUM_INPUTS + 2)
    if arr.shape != (expected_rows, NUM_INPUTS):
        raise RuntimeError(
            f"unexpected SALib output shape {arr.shape}; expected ({expected_rows}, {NUM_INPUTS})"
        )

    df = pd.DataFrame(arr, columns=list(INPUT_NAMES))
    df.insert(0, "run_idx", np.arange(expected_rows))
    return df


# ----------------------------------------------------------------------
# Per-cell sweep
# ----------------------------------------------------------------------


def build_cell_jobs(
    cell: GroupBCell,
    sample: pd.DataFrame,
) -> list[tuple[dict, str]]:
    """Materialise (config, case_id) tuples for one cell."""
    cell_tag = f"{cell.scenario}_{cell.sex}"
    jobs: list[tuple[dict, str]] = []
    for _, row in sample.iterrows():
        cid = f"sobol_{cell_tag}_{int(row['run_idx']):05d}"
        cfg = build_config(
            sample_row=row,
            scenario_key=cell.scenario,
            sex_key=cell.sex,
            case_id=cid,
        )
        cfg.setdefault("atlas_meta", {})["sobol_meta"] = {
            "cell": cell_tag,
            "primary_output": cell.output,
            "dominant_input": cell.dominant_input,
            "run_idx": int(row["run_idx"]),
        }
        jobs.append((cfg, cid))
    return jobs


def run_cell(
    cell: GroupBCell,
    sample: pd.DataFrame,
    output_root: Path,
    image: str,
    workers: int,
    timeout_s: float,
    dry_run: bool,
) -> int:
    """Submit one cell's Sobol jobs. Returns the number of jobs submitted."""
    cell_dir = output_root / f"{cell.scenario}_{cell.sex}"
    cell_dir.mkdir(parents=True, exist_ok=True)

    # Resume-safety: skip cases whose output.csv already exists.
    jobs = build_cell_jobs(cell, sample)
    remaining: list[tuple[dict, str]] = []
    for cfg, cid in jobs:
        out_csv = cell_dir / cid / "output.csv"
        if out_csv.exists():
            continue
        remaining.append((cfg, cid))

    print(
        f"[s019] cell {cell.scenario}_{cell.sex} "
        f"(primary={cell.output}, dominant={cell.dominant_input}): "
        f"{len(remaining)} remaining of {len(jobs)} total"
    )
    if dry_run:
        print(f"[s019] DRY RUN — not launching {len(remaining)} jobs")
        return 0

    if not remaining:
        return 0

    results = run_many(
        remaining,
        runs_root=cell_dir,
        image=image,
        max_workers=workers,
        timeout_s=timeout_s,
    )
    n_ok = sum(1 for r in results if r.exit_code == 0)
    print(f"[s019] cell {cell.scenario}_{cell.sex} done: {n_ok}/{len(results)} exit 0")
    return len(results)


# ----------------------------------------------------------------------
# Index analysis
# ----------------------------------------------------------------------


def analyse(output_root: Path, cells: list[GroupBCell]) -> pd.DataFrame:
    """Aggregate all cells and compute Sobol S₁ / S_t per (cell, output, input)."""
    from SALib.analyze import sobol as sobol_analyser  # local import

    from src.aggregator import aggregate_under

    problem = salib_problem()
    rows: list[dict] = []
    for cell in cells:
        cell_dir = output_root / f"{cell.scenario}_{cell.sex}"
        if not cell_dir.exists():
            print(f"[s019] missing cell dir: {cell_dir}; skipping")
            continue
        df = aggregate_under(cell_dir)
        df = df.sort_values("case_id").reset_index(drop=True)
        # The aggregator's clean-only filter would skew the Sobol moments;
        # we keep ALL rows here and let the analyst decide whether to
        # winsorise. NaNs (from diverged runs) propagate; SALib's variance
        # estimator handles this by dropping incomplete rows in v1.5+.
        for ch_name, ch_col in [
            ("HR", "HR_mean"),
            ("MAP", "MAP_mean"),
            ("Vt", "Vt_mean"),
            ("SpO2", "SpO2_mean"),
            ("PaO2", "PaO2_mean"),
            ("PaCO2", "PaCO2_mean"),
        ]:
            Y = df[ch_col].to_numpy(dtype=float)
            if np.isnan(Y).all():
                continue
            try:
                indices = sobol_analyser.analyze(
                    problem, Y, calc_second_order=False, print_to_console=False
                )
            except Exception as e:
                print(f"[s019] sobol_analyse failed for {cell.scenario}_{cell.sex}/{ch_name}: {e}")
                continue
            for i, inp in enumerate(INPUT_NAMES):
                rows.append(
                    {
                        "scenario": cell.scenario,
                        "sex": cell.sex,
                        "output": ch_name,
                        "input": inp,
                        "S1": float(indices["S1"][i]),
                        "ST": float(indices["ST"][i]),
                        "S1_conf": float(indices["S1_conf"][i]),
                        "ST_conf": float(indices["ST_conf"][i]),
                        "n_runs": int(np.sum(~np.isnan(Y))),
                    }
                )
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="S019 — Sobol bolt-on (DRAFT)")
    p.add_argument(
        "--N",
        type=int,
        default=256,
        help="SALib N (rows per cell = N × (D+2) with calc_second_order=False). Default 256.",
    )
    p.add_argument(
        "--calc-second-order",
        action="store_true",
        help="Also compute second-order S2 indices (doubles run count).",
    )
    p.add_argument("--seed", type=int, default=42, help="RNG seed for Sobol sampling.")
    p.add_argument(
        "--image",
        default="pulse-atlas-engine",
        help="Docker image (pulse-atlas-engine:latest by default).",
    )
    p.add_argument(
        "--workers",
        type=int,
        default=2,
        help="Parallel Docker workers. Laptop cap is 2 (src.runner.MAX_PARALLEL_LAPTOP).",
    )
    p.add_argument("--timeout-s", type=float, default=600.0)
    p.add_argument(
        "--output-root",
        type=Path,
        default=ROOT / "data" / "runs" / "s019_sobol",
        help="Root directory for per-cell run trees.",
    )
    p.add_argument(
        "--cells",
        nargs="+",
        default=None,
        help="Optional subset of cell tags (e.g. S2_M S3_F). Default: all 6.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the job count per cell but do not launch Docker.",
    )
    p.add_argument(
        "--analyse-only",
        action="store_true",
        help="Skip sampling/running; aggregate existing output dirs and emit Sobol indices.",
    )
    p.add_argument(
        "--indices-out",
        type=Path,
        default=ROOT / "results" / "sobol_indices.parquet",
        help="Output parquet for the S1 / ST table.",
    )
    args = p.parse_args(argv)

    # Resolve cell subset
    cells: list[GroupBCell]
    if args.cells:
        wanted = set(args.cells)
        cells = [c for c in GROUP_B_CELLS if f"{c.scenario}_{c.sex}" in wanted]
        if not cells:
            raise SystemExit(f"no matching cells in {args.cells}")
    else:
        cells = list(GROUP_B_CELLS)

    args.output_root.mkdir(parents=True, exist_ok=True)

    if args.analyse_only:
        df = analyse(args.output_root, cells)
        if df.empty:
            print("[s019] no rows analysed; check that the run dirs exist.")
            return 1
        args.indices_out.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(args.indices_out, index=False)
        print(f"[s019] wrote {len(df)} index rows -> {args.indices_out}")
        print(df.head(20).to_string(index=False))
        return 0

    # Sample once; reuse for every cell.
    sample = sample_sobol(
        N=args.N,
        calc_second_order=args.calc_second_order,
        seed=args.seed,
    )
    print(
        f"[s019] sampled {len(sample)} rows over D={NUM_INPUTS} inputs "
        f"(N={args.N}, calc_second_order={args.calc_second_order}, seed={args.seed})"
    )

    # Persist the sample alongside the run dirs for reproducibility.
    sample_path = args.output_root / "sobol_sample.parquet"
    if not sample_path.exists():
        sample.to_parquet(sample_path, index=False)
        print(f"[s019] wrote sample -> {sample_path}")

    total = 0
    for cell in cells:
        total += run_cell(
            cell=cell,
            sample=sample,
            output_root=args.output_root,
            image=args.image,
            workers=args.workers,
            timeout_s=args.timeout_s,
            dry_run=args.dry_run,
        )
    print(f"[s019] total jobs handled: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
