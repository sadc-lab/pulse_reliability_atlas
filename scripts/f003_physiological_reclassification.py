"""F-003 supplementary reclassification under the physiology-anchored PaO2 bound.

The locked atlas classifier uses ``HARD_BOUNDS["PaO2"] = (20, 600)`` mmHg.
This script does **not** modify the locked classifier; it produces a side
table reporting how many runs would change classification under the wider
``HARD_BOUNDS_PHYSIOLOGICAL["PaO2"] = (20, 700)`` mmHg bound, which is
anchored to the alveolar-gas-equation ceiling at sea level (~ 655 mmHg in
healthy adult, FiO2 = 1.0).

The locked atlas figures and numbers in §3.2–§3.7 use ``HARD_BOUNDS``; this
side table powers the §3.8 sensitivity discussion only.

Outputs
-------
``results/f003_physiological_reclassification.csv``
    Per-run reclassification table with columns:
    - ``case_id``, ``scenario``, ``sex``, ``in_fio2``, ``PaO2_mean``
    - ``implausible_locked``           (locked classifier outcome, ``HARD_BOUNDS``)
    - ``implausible_physiological``    (supplementary, ``HARD_BOUNDS_PHYSIOLOGICAL``)
    - ``reclassified``                 (True iff locked says implausible but physio says clean)

``results/f003_physiological_reclassification_summary.json``
    Aggregate counts: how many runs change classification, stratified by
    (scenario, sex) and FiO2 bin.

Usage
-----
::

    uv run python scripts/f003_physiological_reclassification.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.detector import (  # noqa: E402
    HARD_BOUNDS,
    HARD_BOUNDS_PHYSIOLOGICAL,
    reclassify_implausible_against,
)


AGG_PATH: Path = REPO_ROOT / "data" / "runs" / "full_sweep" / "aggregated.parquet"
OUT_CSV: Path = REPO_ROOT / "results" / "f003_physiological_reclassification.csv"
OUT_JSON: Path = REPO_ROOT / "results" / "f003_physiological_reclassification_summary.json"


def main() -> None:
    df = pd.read_parquet(AGG_PATH)

    # Only runs with valid PaO2_mean can be reclassified; diverged runs have NaN.
    df = df.copy()
    df["implausible_locked"] = df["implausible"]
    df["implausible_pao2_under_physio_bounds"] = reclassify_implausible_against(
        df["PaO2_mean"], HARD_BOUNDS_PHYSIOLOGICAL
    )

    # Locked-implausible specifically due to PaO2 > 600: re-evaluate against 700
    pao2_locked_lo, pao2_locked_hi = HARD_BOUNDS["PaO2"]
    pao2_physio_lo, pao2_physio_hi = HARD_BOUNDS_PHYSIOLOGICAL["PaO2"]

    df["pao2_above_locked_bound"] = df["PaO2_mean"] > pao2_locked_hi
    df["pao2_above_physio_bound"] = df["PaO2_mean"] > pao2_physio_hi
    df["pao2_in_grey_zone"] = (
        (df["PaO2_mean"] > pao2_locked_hi) & (df["PaO2_mean"] <= pao2_physio_hi)
    )

    # Reclassified = locked says implausible by PaO2-only and physio says clean
    df["reclassified_pao2_locked_to_physio_clean"] = (
        df["pao2_above_locked_bound"] & ~df["pao2_above_physio_bound"]
    )

    keep = [
        "case_id", "scenario", "sex", "in_fio2",
        "PaO2_mean", "PaO2_slope_per_s", "PaO2_delta_60s",
        "implausible_locked",
        "pao2_above_locked_bound",
        "pao2_above_physio_bound",
        "pao2_in_grey_zone",
        "reclassified_pao2_locked_to_physio_clean",
    ]
    out = df[keep].copy()
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV, index=False)
    print(f"[F-003 reclass] wrote {OUT_CSV} ({len(out)} runs)")

    # Aggregate counts
    n_locked_implausible_pao2 = int(df["pao2_above_locked_bound"].sum())
    n_physio_implausible_pao2 = int(df["pao2_above_physio_bound"].sum())
    n_reclassified = int(df["reclassified_pao2_locked_to_physio_clean"].sum())

    # Stratified by FiO2 bin
    df["fio2_bin"] = pd.cut(
        df["in_fio2"],
        bins=[0.0, 0.4, 0.6, 0.8, 0.95, 1.001],
        include_lowest=True,
    )
    by_fio2 = (
        df.groupby("fio2_bin", observed=True)[
            ["pao2_above_locked_bound", "pao2_above_physio_bound",
             "reclassified_pao2_locked_to_physio_clean"]
        ]
        .sum()
        .to_dict(orient="index")
    )
    by_fio2_serial = {str(k): {kk: int(vv) for kk, vv in v.items()} for k, v in by_fio2.items()}

    # Stratified by (scenario, sex)
    by_cell = (
        df.groupby(["scenario", "sex"], observed=True)[
            ["pao2_above_locked_bound", "pao2_above_physio_bound",
             "reclassified_pao2_locked_to_physio_clean"]
        ]
        .sum()
        .to_dict(orient="index")
    )
    by_cell_serial = {
        f"{sc}_{sex}": {kk: int(vv) for kk, vv in v.items()}
        for (sc, sex), v in by_cell.items()
    }

    summary = {
        "n_total_runs": int(len(df)),
        "locked_PaO2_bound_hi_mmHg": pao2_locked_hi,
        "physiological_PaO2_bound_hi_mmHg": pao2_physio_hi,
        "n_runs_PaO2_above_locked_600": n_locked_implausible_pao2,
        "n_runs_PaO2_above_physio_700":   n_physio_implausible_pao2,
        "n_reclassified_locked_to_physio_clean": n_reclassified,
        "by_fio2_bin": by_fio2_serial,
        "by_scenario_sex": by_cell_serial,
        "alveolar_gas_equation_reference": (
            "PAO2 = FiO2 × (P_atm − P_H2O) − PaCO2/RQ "
            "= 1.0 × (760 − 47) − 40/0.8 ≈ 663 mmHg in healthy adult, "
            "PaO2 ≈ 650 mmHg after typical A-a gradient of 10 mmHg."
        ),
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2))

    print()
    print("=" * 70)
    print(f"  Locked PaO2 bound:  <= {pao2_locked_hi:.0f} mmHg -> {n_locked_implausible_pao2} runs above")
    print(f"  Physio PaO2 bound:  <= {pao2_physio_hi:.0f} mmHg -> {n_physio_implausible_pao2} runs above")
    print(f"  Reclassified (locked-implausible -> physio-clean): {n_reclassified}")
    print()
    print("  Reclassified runs by FiO2 bin:")
    for bin_label, counts in by_fio2_serial.items():
        n_rc = counts["reclassified_pao2_locked_to_physio_clean"]
        if n_rc > 0:
            print(f"    {bin_label}: {n_rc}")
    print()
    print("  Reclassified runs by (scenario, sex):")
    for cell, counts in by_cell_serial.items():
        n_rc = counts["reclassified_pao2_locked_to_physio_clean"]
        if n_rc > 0:
            print(f"    {cell}: {n_rc}")
    print("=" * 70)


if __name__ == "__main__":
    main()
