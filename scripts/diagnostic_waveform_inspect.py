"""S022 — Open the actual waveform CSVs for representative not_steady_state runs
and characterize each sub-mode mechanistically.

For each picked run, we report on the steady-state window (t in [60, 120]):
    - HR steady-state mean / std / CV
    - Vt mean / std / CV / min / max / span
    - SpO2 mean / std / min / max
    - PaO2 mean / std / slope
    - RR setpoint
    - Number of breaths in the window (estimated from Vt zero-crossings)
    - Aliasing check: nominal breath period (60/RR seconds) vs sample interval (5 s)
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "data" / "runs" / "full_sweep"
OUT_DIR = ROOT / "results" / "s022"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PICKS = {
    "S1_F_flatcv":  ("S1_F", "S1_F_0002"),
    "S1_F_cv_only": ("S1_F", "S1_F_0001"),
    "S1_F_flatonly":("S1_F", "S1_F_0003"),
    "S1_M_flatcv":  ("S1_M", "S1_M_0016"),
    "S4_F_drift":   ("S4_F", "S4_F_0005"),
    "S4_F_cv":      ("S4_F", "S4_F_0018"),
}

def load_run(cell: str, case_id: str) -> tuple[pd.DataFrame, dict]:
    folder = RUN_DIR / cell / case_id
    df = pd.read_csv(folder / "output.csv")
    cfg = json.loads((folder / "config.json").read_text(encoding="utf-8"))
    return df, cfg


def window(df: pd.DataFrame, lo: float = 60, hi: float = 120) -> pd.DataFrame:
    return df[(df["time_s"] >= lo - 1e-6) & (df["time_s"] <= hi + 1e-6)].reset_index(drop=True)


def estimate_breaths(t: np.ndarray, vt: np.ndarray) -> int:
    """Crude breath count = number of upward zero-crossings of (vt - mean)."""
    if len(vt) < 3:
        return 0
    centered = vt - vt.mean()
    sign = np.sign(centered)
    crossings = int(((sign[:-1] < 0) & (sign[1:] > 0)).sum())
    return crossings


def report_run(label: str, cell: str, case_id: str) -> dict:
    df, cfg = load_run(cell, case_id)
    win = window(df)
    t = win["time_s"].to_numpy()

    out = {"label": label, "cell": cell, "case_id": case_id}

    baselines = cfg.get("baselines", {})
    vent = cfg.get("ventilator", {})
    rr = vent.get("set_rr", baselines.get("rr"))
    out["rr_set"] = rr
    out["vt_set"] = vent.get("tidal_volume_ml")
    out["fio2_set"] = vent.get("fio2")
    out["peep_set"] = vent.get("peep_cmh2o")
    out["hr_set"]  = baselines.get("hr")
    out["sbp_set"] = baselines.get("sbp")
    out["dbp_set"] = baselines.get("dbp")

    out["n_samples"] = int(len(win))
    out["sample_interval_s"] = float(np.median(np.diff(t))) if len(t) > 1 else float("nan")

    if rr:
        breath_period = 60.0 / float(rr)
        out["breath_period_s"] = breath_period
        out["samples_per_breath"] = breath_period / out["sample_interval_s"]
        # nyquist criterion: need sample_interval < breath_period/2
        out["nyquist_ok"] = out["sample_interval_s"] < breath_period / 2

    cols = {
        "HR": "HeartRate",
        "Vt": "TidalVolume",
        "SpO2": "OxygenSaturation",
        "PaO2": "ArterialOxygenPressure",
        "PaCO2": "ArterialCarbonDioxidePressure",
    }
    stats = {}
    for ch, col in cols.items():
        if col not in win.columns:
            continue
        y = win[col].to_numpy(float)
        stats[ch] = {
            "mean": float(y.mean()),
            "std": float(y.std(ddof=0)),
            "min": float(y.min()),
            "max": float(y.max()),
            "span": float(y.max() - y.min()),
            "cv": float(y.std(ddof=0) / abs(y.mean())) if y.mean() != 0 else float("nan"),
        }
        if len(y) > 1:
            slope = float(np.polyfit(t, y, 1)[0])
            stats[ch]["slope_per_s"] = slope
            stats[ch]["delta_60s"] = slope * 60.0

    # estimate breaths in window for Vt
    if "TidalVolume" in win.columns:
        stats["Vt"]["breaths_in_60s"] = estimate_breaths(t, win["TidalVolume"].to_numpy())

    out["channels"] = stats
    return out


def fmt(v, p=3):
    if v is None:
        return "-"
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, (int, np.integer)):
        return f"{int(v)}"
    if isinstance(v, float):
        if abs(v) < 1e-3 or abs(v) > 1e4:
            return f"{v:.{p}e}"
        return f"{v:.{p}f}"
    return str(v)


def main() -> None:
    all_reports = []
    for label, (cell, case_id) in PICKS.items():
        r = report_run(label, cell, case_id)
        all_reports.append(r)
    (OUT_DIR / "waveform_inspect.json").write_text(json.dumps(all_reports, indent=2), encoding="utf-8")

    print("=== Waveform-level inspection of representative not_steady_state runs ===\n")
    for r in all_reports:
        print(f"### {r['label']}  (case={r['case_id']})")
        print(f"  Requested inputs: HR={fmt(r['hr_set'],1)}  SBP={fmt(r['sbp_set'],0)}  DBP={fmt(r['dbp_set'],0)}  "
              f"RR={fmt(r['rr_set'],1)}  Vt={fmt(r['vt_set'],0)}  FiO2={fmt(r['fio2_set'],2)}  PEEP={fmt(r['peep_set'],1)}")
        if "samples_per_breath" in r:
            print(f"  Sample interval = {fmt(r['sample_interval_s'],2)} s  |  RR={fmt(r['rr_set'],1)} -> "
                  f"breath period = {fmt(r['breath_period_s'],2)} s -> samples/breath = {fmt(r['samples_per_breath'],2)}  "
                  f"|  Nyquist OK: {r['nyquist_ok']}")
        ch = r["channels"]
        if "Vt" in ch:
            v = ch["Vt"]
            print(f"  Vt   mean={fmt(v['mean'],1)}  std={fmt(v['std'],1)}  CV={fmt(v['cv'],3)}  "
                  f"min={fmt(v['min'],1)}  max={fmt(v['max'],1)}  span={fmt(v['span'],1)}  "
                  f"breath_zero_xings={v.get('breaths_in_60s','?')}")
        if "SpO2" in ch:
            v = ch["SpO2"]
            print(f"  SpO2 mean={fmt(v['mean'],4)}  std={fmt(v['std'],4)}  "
                  f"min={fmt(v['min'],4)}  max={fmt(v['max'],4)}  d60s={fmt(v.get('delta_60s', 0),4)}")
        if "PaO2" in ch:
            v = ch["PaO2"]
            print(f"  PaO2 mean={fmt(v['mean'],1)}  std={fmt(v['std'],2)}  d60s={fmt(v.get('delta_60s',0),3)}")
        if "PaCO2" in ch:
            v = ch["PaCO2"]
            print(f"  PaCO2 mean={fmt(v['mean'],2)}  std={fmt(v['std'],3)}  d60s={fmt(v.get('delta_60s',0),3)}")
        if "HR" in ch:
            v = ch["HR"]
            print(f"  HR   mean={fmt(v['mean'],2)}  std={fmt(v['std'],3)}  d60s={fmt(v.get('delta_60s',0),3)}")
        print()


if __name__ == "__main__":
    main()
