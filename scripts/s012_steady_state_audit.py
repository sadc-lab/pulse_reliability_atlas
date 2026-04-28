"""S012 — Dual steady-state audit.

Two sibling vulnerabilities in the [60, 120] s steady-state window:

* F-003 arm: at FiO2 >= 0.95, PaO2 drifts. Question — do HR / MAP / Vt also
  drift, or is the cardiovascular / ventilator loop stable while only gas
  exchange is unsettled?
* F-004 arm: at Vt_cv > 0.05, the ventilator-delivered tidal volume oscillates.
  Question — does that oscillation propagate to HR / MAP and to gas exchange
  (PaO2, PaCO2), or does Pulse buffer it?

For each arm, computes the distribution of |Delta_60s| against the
preregistered drift thresholds (DRIFT_MAX_DELTA_60S in src/detector.py):

    HR=5.0, MAP=5.0, Vt=50.0, SpO2=0.02, PaO2=15.0, PaCO2=5.0

Outputs:
    results/s012_f003_hyperoxia_audit.csv
    results/s012_f004_vt_oscillation_audit.csv
    results/s012_summary.csv
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.detector import DRIFT_MAX_DELTA_60S

REPO = Path(__file__).resolve().parent.parent
PARQUET = REPO / "data" / "runs" / "full_sweep" / "aggregated.parquet"
OUT = REPO / "results"


def _has_steady_state_data(df: pd.DataFrame, output: str) -> pd.Series:
    return df[f"{output}_n_points"].fillna(0) >= 10


def _audit_outputs(df: pd.DataFrame, outputs: list[str]) -> pd.DataFrame:
    rows: list[dict] = []
    for out in outputs:
        col = f"{out}_delta_60s"
        threshold = DRIFT_MAX_DELTA_60S[out]
        mask_has = _has_steady_state_data(df, out)
        sub = df.loc[mask_has].copy()
        if sub.empty:
            rows.append(
                {
                    "output": out,
                    "n_runs_with_data": 0,
                    "threshold": threshold,
                    "mean_abs_delta": float("nan"),
                    "median_abs_delta": float("nan"),
                    "p95_abs_delta": float("nan"),
                    "max_abs_delta": float("nan"),
                    "n_exceed_threshold": 0,
                    "frac_exceed_threshold": float("nan"),
                }
            )
            continue
        abs_delta = sub[col].abs()
        rows.append(
            {
                "output": out,
                "n_runs_with_data": int(mask_has.sum()),
                "threshold": threshold,
                "mean_abs_delta": abs_delta.mean(),
                "median_abs_delta": abs_delta.median(),
                "p95_abs_delta": abs_delta.quantile(0.95),
                "max_abs_delta": abs_delta.max(),
                "n_exceed_threshold": int((abs_delta > threshold).sum()),
                "frac_exceed_threshold": float((abs_delta > threshold).mean()),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    if not PARQUET.exists():
        raise FileNotFoundError(f"Aggregated parquet not found: {PARQUET}")

    df = pd.read_parquet(PARQUET)
    print(f"Loaded {len(df)} runs from {PARQUET.relative_to(REPO)}")

    # Drop runs with no usable data (diverged with NaN delta values).
    # Vt_n_points is a proxy for "did we get any steady-state CSV at all".

    # ----- F-003 arm: hyperoxia (FiO2 >= 0.95) -----
    f003 = df[df["in_fio2"] >= 0.95].copy()
    print(f"\nF-003 arm (FiO2 >= 0.95): {len(f003)} runs")
    f003_audit = _audit_outputs(f003, ["HR", "MAP", "Vt", "PaO2"])
    f003_audit.insert(0, "arm", "F-003 hyperoxia")
    f003_audit.insert(1, "filter", "in_fio2 >= 0.95")
    f003_audit.insert(2, "n_total_runs", len(f003))
    f003_audit.to_csv(OUT / "s012_f003_hyperoxia_audit.csv", index=False)
    print(f003_audit.to_string(index=False))

    # ----- F-004 arm: Vt oscillation (Vt_cv > 0.05) -----
    has_vt_cv = df["Vt_cv"].notna()
    f004 = df[has_vt_cv & (df["Vt_cv"] > 0.05)].copy()
    print(f"\nF-004 arm (Vt_cv > 0.05): {len(f004)} runs")
    f004_audit = _audit_outputs(f004, ["HR", "MAP", "PaO2", "PaCO2"])
    f004_audit.insert(0, "arm", "F-004 Vt oscillation")
    f004_audit.insert(1, "filter", "Vt_cv > 0.05")
    f004_audit.insert(2, "n_total_runs", len(f004))
    f004_audit.to_csv(OUT / "s012_f004_vt_oscillation_audit.csv", index=False)
    print(f004_audit.to_string(index=False))

    # ----- Combined summary -----
    summary = pd.concat([f003_audit, f004_audit], ignore_index=True)
    summary.to_csv(OUT / "s012_summary.csv", index=False)
    print(f"\nWrote {OUT / 's012_summary.csv'}")

    # ----- Cross-check: any run that is BOTH hyperoxic AND Vt-oscillating? -----
    both = df[(df["in_fio2"] >= 0.95) & (df["Vt_cv"] > 0.05)]
    print(f"\nRuns satisfying BOTH F-003 and F-004: {len(both)} / {len(df)}")
    if len(both):
        for out in ["HR", "MAP", "Vt", "PaO2", "PaCO2"]:
            col = f"{out}_delta_60s"
            thr = DRIFT_MAX_DELTA_60S[out]
            n_exceed = int((both[col].abs() > thr).sum())
            print(f"  {out:6} |Delta_60s| > {thr}: {n_exceed} / {len(both)}")


if __name__ == "__main__":
    main()
