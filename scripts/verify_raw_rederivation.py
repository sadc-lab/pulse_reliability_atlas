"""Independent raw re-derivation of the atlas's load-bearing pillars (read-only).

PURPOSE (paranoia audit, 2026-06-14)
------------------------------------
Close hole (c): "we trust the derived artifacts; we never re-derive from raw".
This script does NOT import src/detector.py and does NOT read
data/runs/full_sweep/aggregated.parquet to *compute* anything. It walks the
1,280 raw per-run directories, re-implements the four-flag contract from
scratch on the raw output.csv / pulse.log / run_meta.json, and reports the
headline numbers. It then cross-checks its own fresh counts against BOTH:

  (A) the stored aggregated.parquet  -> catches aggregation/serialization drift
  (B) the numbers printed in the manuscript -> catches the headline claims

If fresh == aggregated == manuscript on every pillar, the result is triangulated
across three independent renderings (raw files / fresh logic / final document).

Pillars covered here (1-4):
  1. Inventory: 1,280 runs across 8 cells x 160.
  2. Flag totals: 0 clamped, 20 diverged (all 20 male, 0 female),
     126 implausible, 663 clean.
  3. Table 1 per-cell breakdown (presence-count semantics).
  4. 20.6 % Vt instability = runs whose PRIMARY flag is not_steady_state AND
     Vt_cv > 0.05  (= 264 / 1,280).

Pillar 5 (BV floor 4,082.24 mL, experiment S018) is verified separately.

Read-only: writes nothing. Output to stdout only.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
SWEEP = REPO / "data" / "runs" / "full_sweep"
CELLS = ["S1_F", "S1_M", "S2_F", "S2_M", "S3_F", "S3_M", "S4_F", "S4_M"]

# ---- Locked contract constants, transcribed from preregistration (NOT imported
# from detector.py, so this is an independent second implementation). ----------
OUTPUT_COLUMNS = {
    "HR": "HeartRate",
    "MAP": "MeanArterialPressure",
    "Vt": "TidalVolume",
    "SpO2": "OxygenSaturation",
    "PaO2": "ArterialOxygenPressure",
    "PaCO2": "ArterialCarbonDioxidePressure",
}
HARD_BOUNDS = {
    "HR": (20.0, 220.0),
    "MAP": (30.0, 180.0),
    "Vt": (50.0, 1500.0),
    "SpO2": (0.50, 1.00),
    "PaO2": (20.0, 600.0),
    "PaCO2": (10.0, 120.0),
}
DRIFT_MAX_DELTA_60S = {
    "HR": 5.0, "MAP": 5.0, "Vt": 50.0, "SpO2": 0.02, "PaO2": 15.0, "PaCO2": 5.0,
}
CV_THRESHOLD = 0.05
FLATLINE_STD_RATIO = 0.01
FLATLINE_BOUND_TOL = 0.001
T_LO, T_HI = 60.0, 120.0
CLAMP_PATTERNS = [
    r"baseline of [\d\.]+ \S+ is too (?:high|low)",
    r"maximum [\w\s]+ baseline allowed is",
    r"must be modeled by adding/using a condition",
    r"is outside the valid range",
]


def ols_slope(t: np.ndarray, y: np.ndarray) -> float:
    if len(t) < 2:
        return 0.0
    dt = t - t.mean()
    denom = float((dt * dt).sum())
    if denom <= 0:
        return 0.0
    return float((dt * (y - y.mean())).sum()) / denom


def classify_run(run_dir: Path) -> dict:
    """Re-implement the four-flag contract from raw files. Returns flag dict."""
    csv_p = run_dir / "output.csv"
    log_p = run_dir / "pulse.log"
    meta_p = run_dir / "run_meta.json"

    # exit code from run_meta.json
    exit_code = 0
    if meta_p.exists():
        try:
            exit_code = int(json.loads(meta_p.read_text())["exit_code"])
        except Exception:
            exit_code = 0

    # ---- clamped: regex on pulse.log ----
    clamped = False
    if log_p.exists():
        log_txt = log_p.read_text(encoding="utf-8", errors="replace")
        clamped = any(re.search(p, log_txt, re.IGNORECASE) for p in CLAMP_PATTERNS)

    # ---- diverged: exit!=0 / missing / empty / NaN / Inf / truncated ----
    diverged = False
    df = None
    if exit_code != 0:
        diverged = True
    elif not csv_p.exists():
        diverged = True
    else:
        try:
            df = pd.read_csv(csv_p)
        except Exception:
            diverged = True
            df = None
        if df is not None:
            if df.empty or "time_s" not in df.columns:
                diverged = True
            else:
                num = df.select_dtypes(include=[np.number])
                if num.isna().any().any() or np.isinf(num.to_numpy()).any():
                    diverged = True
                elif float(df["time_s"].max()) + 1e-3 < T_HI:
                    diverged = True

    implausible = False
    not_steady = False
    vt_cv = float("nan")

    if not diverged and df is not None:
        win = df[(df["time_s"] >= T_LO - 1e-6) & (df["time_s"] <= T_HI + 1e-6)]
        t = win["time_s"].to_numpy(float)
        for name, col in OUTPUT_COLUMNS.items():
            if col not in win.columns:
                continue
            y = win[col].to_numpy(float)
            if len(y) == 0:
                continue
            mean = float(y.mean())
            std = float(y.std(ddof=0))
            cv = std / abs(mean) if mean != 0 else 0.0
            delta60 = ols_slope(t, y) * 60.0
            lo, hi = HARD_BOUNDS[name]
            if name == "Vt":
                vt_cv = cv
            # implausible
            if mean < lo or mean > hi:
                implausible = True
            # not_steady_state (flatline-at-extreme / variance / drift)
            std_ratio = std / abs(mean) if abs(mean) > 0 else 0.0
            near_lo = abs(mean - lo) <= FLATLINE_BOUND_TOL * max(abs(lo), 1.0)
            near_hi = abs(mean - hi) <= FLATLINE_BOUND_TOL * max(abs(hi), 1.0)
            if std_ratio < FLATLINE_STD_RATIO and (near_lo or near_hi):
                not_steady = True
            elif cv > CV_THRESHOLD:
                not_steady = True
            elif abs(delta60) > DRIFT_MAX_DELTA_60S[name]:
                not_steady = True

    # primary flag (locked hierarchy)
    if clamped:
        primary = "clamped"
    elif diverged:
        primary = "diverged"
    elif implausible:
        primary = "implausible"
    elif not_steady:
        primary = "not_steady_state"
    else:
        primary = "clean"

    return {
        "clamped": clamped,
        "diverged": diverged,
        "implausible": implausible,
        "not_steady_state": not_steady,
        "clean": primary == "clean",
        "primary": primary,
        "Vt_cv": vt_cv,
    }


def main() -> None:
    rows = []
    n_dirs = 0
    for cell in CELLS:
        scenario, sex = cell.split("_")
        cell_dir = SWEEP / cell
        run_dirs = sorted(d for d in cell_dir.iterdir() if d.is_dir())
        n_dirs += len(run_dirs)
        for rd in run_dirs:
            r = classify_run(rd)
            r["scenario"] = scenario
            r["sex"] = sex
            r["case_id"] = rd.name
            rows.append(r)
    fresh = pd.DataFrame(rows)

    print("# Raw re-derivation (independent of detector.py + aggregated.parquet)\n")

    # ----- Pillar 1: inventory -----
    print("## Pillar 1 - inventory")
    print(f"  run directories found : {n_dirs}")
    print(f"  runs classified       : {len(fresh)}")
    print("  manuscript claim       : 1,280")
    print(f"  -> {'MATCH' if len(fresh) == 1280 == n_dirs else 'MISMATCH'}\n")

    # ----- Pillar 2: flag totals -----
    tot = {k: int(fresh[k].sum()) for k in
           ["clamped", "diverged", "implausible", "not_steady_state", "clean"]}
    dv_m = int(fresh[(fresh.diverged) & (fresh.sex == "M")].shape[0])
    dv_f = int(fresh[(fresh.diverged) & (fresh.sex == "F")].shape[0])
    expect = {"clamped": 0, "diverged": 20, "implausible": 126,
              "not_steady_state": None, "clean": 663}
    print("## Pillar 2 - flag totals (fresh vs manuscript)")
    for k in ["clamped", "diverged", "implausible", "clean"]:
        exp = expect[k]
        tag = "MATCH" if tot[k] == exp else "MISMATCH"
        print(f"  {k:18s}: fresh={tot[k]:4d}  manuscript={exp}  -> {tag}")
    print(f"  diverged by sex   : fresh M={dv_m} / F={dv_f}  "
          f"manuscript M=20 / F=0  -> "
          f"{'MATCH' if dv_m == 20 and dv_f == 0 else 'MISMATCH'}")
    print(f"  not_steady_state  : fresh={tot['not_steady_state']} (primary-agnostic total)\n")

    # ----- Pillar 4: 20.6 % Vt instability -----
    nss_vt = int(((fresh.primary == "not_steady_state") & (fresh.Vt_cv > 0.05)).sum())
    pct = 100.0 * nss_vt / len(fresh)
    print("## Pillar 4 - 20.6 % Vt instability (primary==nss AND Vt_cv>0.05)")
    print(f"  fresh count : {nss_vt} / {len(fresh)} = {pct:.1f}%")
    print("  manuscript  : 264 / 1,280 = 20.6%")
    print(f"  -> {'MATCH' if nss_vt == 264 and abs(pct - 20.6) < 0.05 else 'MISMATCH'}\n")

    # ----- Pillar 3: Table 1 per cell -----
    table1 = {
        ("S1", "M"): (160, 0, 4, 11, 107, 49), ("S1", "F"): (160, 0, 0, 23, 118, 42),
        ("S2", "M"): (160, 0, 4, 0, 69, 87),   ("S2", "F"): (160, 0, 0, 0, 68, 92),
        ("S3", "M"): (160, 0, 4, 0, 12, 144),  ("S3", "F"): (160, 0, 0, 0, 38, 122),
        ("S4", "M"): (160, 0, 8, 46, 44, 67),  ("S4", "F"): (160, 0, 0, 46, 74, 60),
    }
    print("## Pillar 3 - Table 1 per cell (presence-count semantics)")
    print("  cell  | n_tot clmp dvg impl  nss clean | verdict")
    all_ok = True
    for (sc, sx), exp in table1.items():
        sub = fresh[(fresh.scenario == sc) & (fresh.sex == sx)]
        got = (len(sub), int(sub.clamped.sum()), int(sub.diverged.sum()),
               int(sub.implausible.sum()), int(sub.not_steady_state.sum()),
               int(sub.clean.sum()))
        ok = got == exp
        all_ok &= ok
        print(f"  {sc}_{sx} | {got}  {'ok' if ok else 'DIFF exp='+str(exp)}")
    print(f"  -> Table 1 {'ALL MATCH' if all_ok else 'HAS MISMATCH'}\n")

    # ----- Cross-check (B): against stored aggregated.parquet -----
    print("## Cross-check vs stored aggregated.parquet (catches aggregation drift)")
    agg = pd.read_parquet(SWEEP / "aggregated.parquet")
    for k in ["clamped", "diverged", "implausible", "not_steady_state", "clean"]:
        if k in agg.columns:
            a = int(agg[k].sum())
            f = tot[k]
            print(f"  {k:18s}: fresh={f:4d}  parquet={a:4d}  -> "
                  f"{'MATCH' if a == f else 'MISMATCH'}")
        else:
            print(f"  {k:18s}: (column absent in parquet)")
    if "Vt_cv" in agg.columns:
        # compare the 20.6% derivation against parquet too
        def prim(row):
            if row.get("clamped"):
                return "clamped"
            if row.get("diverged"):
                return "diverged"
            if row.get("implausible"):
                return "implausible"
            if row.get("not_steady_state"):
                return "not_steady_state"
            return "clean"
        agg_prim = agg.apply(prim, axis=1)
        agg_nss_vt = int(((agg_prim == "not_steady_state") & (agg["Vt_cv"] > 0.05)).sum())
        print(f"  20.6%-count       : fresh={nss_vt}  parquet={agg_nss_vt}  -> "
              f"{'MATCH' if agg_nss_vt == nss_vt else 'MISMATCH'}")


if __name__ == "__main__":
    main()
