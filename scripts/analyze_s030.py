"""S030 analysis -- P/F by arm and window, with Berlin band assignment.

Reads every S030 run, computes mean PaO2 over two windows (the atlas-canonical
[60, 120] s and a late [240, 300] s), converts to P/F at the fixed FiO2 = 0.40,
and assigns the Berlin band.  Also reports the *measured* respiratory rate and
tidal volume, which is how we verify that the trigger lock actually took
effect rather than being silently ignored.

Writes results/s030_pf_by_arm.csv.  Touches no manuscript.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
RUNS = REPO / "data" / "runs" / "s030_ards_berlin_recalibration"
FIO2 = 0.40
W_ATLAS = (60.0, 120.0)
W_LATE = (240.0, 300.0)


def berlin(pf: float) -> str:
    if pf != pf:
        return "n/a"
    if pf > 300:
        return "no-ARDS"
    if pf > 200:
        return "mild"
    if pf > 100:
        return "moderate"
    return "severe"


# Matches src/detector.py::_steady_state_window, which is what the 1,280-run
# sweep uses for every published steady-state mean. Without this slack the
# recorded grid's float drift silently excludes the nominal upper endpoint
# (t = 120 s is stored as 120.0000000000557), so the same nominal window held
# 12 samples here and 13 in the main sweep. Aligned 2026-08-13; the numeric
# consequence is documented in audit/s030_published_value_provenance.md §4.
TIME_SLACK_S = 1e-6


def window_mean(df: pd.DataFrame, col: str, lo: float, hi: float) -> float:
    m = df[(df.time_s >= lo - TIME_SLACK_S) & (df.time_s <= hi + TIME_SLACK_S)]
    return float(m[col].mean()) if len(m) else float("nan")


rows = []
for d in sorted(RUNS.iterdir()):
    if not d.is_dir():
        continue
    parts = d.name.split("_")           # s030 / fr|lk / M|F / 0p300
    arm = {"fr": "free", "lk": "locked"}[parts[1]]
    sex, sev = parts[2], float(parts[3].replace("p", "."))
    csv = d / "output.csv"
    if not csv.exists():
        rows.append({"arm": arm, "sex": sex, "severity": sev, "status": "FAILED"})
        continue
    df = pd.read_csv(csv)
    pao2_a = window_mean(df, "ArterialOxygenPressure", *W_ATLAS)
    pao2_l = window_mean(df, "ArterialOxygenPressure", *W_LATE)
    rows.append({
        "arm": arm, "sex": sex, "severity": sev, "status": "ok",
        "PaO2_60_120": pao2_a, "PF_60_120": pao2_a / FIO2,
        "band_60_120": berlin(pao2_a / FIO2),
        "PaO2_240_300": pao2_l, "PF_240_300": pao2_l / FIO2,
        "band_240_300": berlin(pao2_l / FIO2),
        "RR_meas": window_mean(df, "RespirationRate", *W_LATE),
        "Vt_meas": window_mean(df, "TidalVolume", *W_LATE),
        "PaCO2": window_mean(df, "ArterialCarbonDioxidePressure", *W_LATE),
        "SpO2": window_mean(df, "OxygenSaturation", *W_LATE),
    })

out = pd.DataFrame(rows).sort_values(["sex", "arm", "severity"])
out.to_csv(REPO / "results" / "s030_pf_by_arm.csv", index=False)

pd.set_option("display.width", 200)
print("=" * 96)
print("A. LE VERROU DE TRIGGER A-T-IL AGI ?  (fréquence et Vt mesurés, fenêtre 240-300 s)")
print("=" * 96)
ok = out[out.status == "ok"]
print(ok.groupby("arm")[["RR_meas", "Vt_meas", "PaCO2"]]
      .agg(["min", "median", "max"]).round(2).to_string())

print()
print("=" * 96)
print("B. MALE -- P/F PAR BRAS ET PAR FENETRE")
print("=" * 96)
m = ok[ok.sex == "M"].pivot_table(
    index="severity", columns="arm",
    values=["PF_60_120", "PF_240_300", "RR_meas"]).round(1)
print(m.to_string())

print()
print("=" * 96)
print("C. BANDES DE BERLIN -- LES DEUX BRAS S'ACCORDENT-ILS ?")
print("=" * 96)
for sex in ("M", "F"):
    s = ok[ok.sex == sex]
    if s.empty:
        continue
    p = s.pivot_table(index="severity", columns="arm",
                      values="band_60_120", aggfunc="first")
    p2 = s.pivot_table(index="severity", columns="arm",
                       values="band_240_300", aggfunc="first")
    p.columns = [f"{c}_[60,120]" for c in p.columns]
    p2.columns = [f"{c}_[240,300]" for c in p2.columns]
    j = p.join(p2)
    j["DESACCORD"] = [
        "<<<" if len(set(r.dropna())) > 1 else "" for _, r in j.iterrows()
    ]
    print(f"\n--- sexe {sex} ---")
    print(j.to_string())

print()
print("=" * 96)
print("D. ECHECS MOTEUR")
print("=" * 96)
f = out[out.status == "FAILED"]
print(f[["arm", "sex", "severity"]].to_string(index=False) if len(f) else "aucun")
print(f"\n-> results/s030_pf_by_arm.csv ({len(out)} lignes)")
