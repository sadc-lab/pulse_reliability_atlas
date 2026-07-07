"""Empirical P/F (PaO2/FiO2) characterisation of the four ARDS scenarios
against the Berlin Definition severity bands (Supplement S5).

Read-only analysis on the canonical full-sweep aggregate. For each ARDS
scenario it computes the empirical arterial P/F ratio (PaO2_mean / FiO2) on the
clean steady-state runs that satisfy the Berlin ARDS PEEP >= 5 cmH2O inclusion
criterion, with FiO2 stratification. The P/F ratio is FiO2-dependent -- a known
property of the Berlin definition itself -- so the stratification is reported
explicitly rather than collapsed to a single number.

Berlin 2012 severity bands (PaO2/FiO2 on PEEP/CPAP >= 5 cmH2O):
    not-ARDS  : P/F > 300
    mild      : 200 < P/F <= 300
    moderate  : 100 < P/F <= 200
    severe    :       P/F <= 100

Output: results/pf_berlin_by_scenario.csv (one 'all' row per scenario plus one
row per FiO2 stratum). Consumed by the audit ledger to anchor the S5
empirical-P/F table so every reported number is reproducible from source.

Selection note: 'clean' excludes runs flagged implausible / not_steady_state /
diverged. At FiO2 = 1.0 healthy (S1) runs are frequently flagged implausible
(transient hyperoxia, PaO2 > 600), so clean S1 carries no high-FiO2 rows;
conversely severe (S4) carries few low-FiO2 rows. These structural gaps are
reported as empty cells in the S5 table.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AGG = ROOT / "data" / "runs" / "full_sweep" / "aggregated.parquet"
OUT = ROOT / "results" / "pf_berlin_by_scenario.csv"

BERLIN_PEEP_MIN = 5.0  # cmH2O -- Berlin ARDS inclusion criterion
FIO2_STRATA = [(0.21, 0.40, "low_0.21_0.40"), (0.40, 0.70, "mid_0.40_0.70"), (0.70, 1.001, "high_0.70_1.00")]
SCEN = {"S1": ("healthy", 0.00), "S2": ("mild", 0.26), "S3": ("moderate", 0.60), "S4": ("severe", 0.95)}


def berlin_band(pf: float) -> str:
    if not np.isfinite(pf):
        return "n/a"
    if pf > 300:
        return "not-ARDS"
    if pf > 200:
        return "mild"
    if pf > 100:
        return "moderate"
    return "severe"


def _summarise(sc: str, d: pd.DataFrame, stratum: str) -> dict:
    label, impair = SCEN[sc]
    if len(d) == 0:
        return dict(scenario=sc, severity_label=label, impairment=impair, fio2_stratum=stratum,
                    n=0, pf_median=np.nan, pf_q25=np.nan, pf_q75=np.nan, berlin_band_of_median="n/a")
    pf = d["pf"]
    return dict(scenario=sc, severity_label=label, impairment=impair, fio2_stratum=stratum,
                n=int(len(d)), pf_median=round(float(pf.median()), 1),
                pf_q25=round(float(pf.quantile(0.25)), 1), pf_q75=round(float(pf.quantile(0.75)), 1),
                berlin_band_of_median=berlin_band(pf.median()))


def main() -> None:
    df = pd.read_parquet(AGG)
    base = df[df["clean"] & (df["in_peep"] >= BERLIN_PEEP_MIN)].copy()
    base["pf"] = base["PaO2_mean"] / base["in_fio2"]
    rows: list[dict] = []
    for sc in ["S1", "S2", "S3", "S4"]:
        sub = base[base["scenario"] == sc]
        rows.append(_summarise(sc, sub, "all"))
        for lo, hi, nm in FIO2_STRATA:
            rows.append(_summarise(sc, sub[(sub["in_fio2"] >= lo) & (sub["in_fio2"] < hi)], nm))
    out = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    print(f"Population: clean runs with PEEP >= {BERLIN_PEEP_MIN} cmH2O -> n={len(base)}/{len(df)}")
    print(f"Artifact written: {OUT.relative_to(ROOT)}")
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
