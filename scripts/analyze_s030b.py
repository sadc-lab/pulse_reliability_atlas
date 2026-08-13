"""S030b analysis -- severe-band robustness, and HR/RR acceptance bounds.

BLOCK 1.  S030 left one question open.  Fraction 0.95 is *severe* at the
atlas-canonical window but *moderate* by [240, 300] s once the patient is free
to trigger above the set rate (86.8 -> 112.8 P/F), while the trigger-locked arm
stays severe throughout (69.1 -> 91.8).  Fractions 0.96-0.99 x both arms ask
whether any fraction below 1.0 puts "severe" beyond the reach of both the
longer window and the free trigger.  P/F is reported over three windows: the
atlas-canonical [60, 120], the companion's true measurement window [108, 168],
and the late [240, 300].

BLOCK 2.  The paper asserts three times that Pulse accepts HR only in
50-110 bpm and RR only in 8-20 bpm.  The 1,280-run sweep proves those values
are ACCEPTED; it never tested rejection.  Expect 49 / 111 / 7 / 21 to fail at
setup and 50 / 110 / 8 / 20 to complete.  The engine log is read directly so a
rejection is attributed to the right input rather than inferred from an exit
code alone.

Writes results/s030b_analysis.csv.  Touches no manuscript.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
RUNS = REPO / "data" / "runs" / "s030b_severe_and_bounds"
FIO2 = 0.40

WINDOWS = {
    "60_120": (60.0, 120.0),      # atlas-canonical
    "108_168": (108.0, 168.0),    # companion's true window (60 s settle + 108 s run)
    "240_300": (240.0, 300.0),    # late
}


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


# See scripts/analyze_s030.py: the same slack as
# src/detector.py::_steady_state_window, so this side experiment and the
# 1,280-run sweep read the same samples from the same nominal window.
TIME_SLACK_S = 1e-6


def wmean(df: pd.DataFrame, col: str, lo: float, hi: float) -> float:
    m = df[(df.time_s >= lo - TIME_SLACK_S) & (df.time_s <= hi + TIME_SLACK_S)]
    return float(m[col].mean()) if len(m) else float("nan")


def read_meta(d: Path) -> dict | None:
    """None when the run has not finished.

    The runner creates the directory at launch and writes run_meta.json only on
    completion, so an absent meta means "still running", not "failed".  These
    two states must never be merged: reading an in-flight run as a failure
    would have manufactured an engine-instability finding out of nothing.
    """
    p = d / "run_meta.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


# Pulse announces a setup rejection on stderr/stdout as an [ERROR] line naming
# the offending quantity.  We keep the raw line rather than a boolean so the
# register can quote it.
ERR_RE = re.compile(r"^.*\[ERROR\].*$", re.MULTILINE)


def error_lines(d: Path, limit: int = 4) -> list[str]:
    log = d / "pulse.log"
    if not log.exists():
        return []
    txt = log.read_text(encoding="utf-8", errors="replace")
    seen, out = set(), []
    for m in ERR_RE.findall(txt):
        s = m.strip()
        if s not in seen:
            seen.add(s)
            out.append(s)
        if len(out) >= limit:
            break
    return out


severe_rows, bound_rows, incomplete = [], [], []
EXPECTED_RUNS = 16

for d in sorted(RUNS.iterdir()):
    if not d.is_dir():
        continue
    meta = read_meta(d)
    if meta is None:
        incomplete.append(d.name)
        continue
    exit_code = meta.get("exit_code")
    csv = d / "output.csv"
    has_csv = csv.exists()

    if d.name.startswith("s030b_bound_"):
        probe = d.name.replace("s030b_bound_", "")     # hr49 / rr21 ...
        kind, val = probe[:2].upper(), int(probe[2:])
        row = {
            "probe": kind, "value": val,
            "exit_code": exit_code,
            "csv_written": has_csv,
            "outcome": "ACCEPTED" if (has_csv and exit_code == 0) else "REJECTED",
            "errors": " || ".join(error_lines(d)) or "-",
        }
        if has_csv:
            df = pd.read_csv(csv)
            col = "HeartRate" if kind == "HR" else "RespirationRate"
            if col in df.columns:
                row["measured"] = round(wmean(df, col, 60.0, 120.0), 2)
        bound_rows.append(row)
        continue

    # severe block: s030b_{fr|lk}_M_0p960
    parts = d.name.split("_")
    arm = {"fr": "free", "lk": "locked"}[parts[1]]
    sev = float(parts[3].replace("p", "."))
    if not has_csv:
        severe_rows.append({"arm": arm, "severity": sev, "status": "FAILED",
                            "exit_code": exit_code,
                            "errors": " || ".join(error_lines(d)) or "-"})
        continue
    df = pd.read_csv(csv)
    row = {"arm": arm, "severity": sev, "status": "ok", "exit_code": exit_code}
    for tag, (lo, hi) in WINDOWS.items():
        pao2 = wmean(df, "ArterialOxygenPressure", lo, hi)
        row[f"PaO2_{tag}"] = round(pao2, 1)
        row[f"PF_{tag}"] = round(pao2 / FIO2, 1)
        row[f"band_{tag}"] = berlin(pao2 / FIO2)
    lo, hi = WINDOWS["240_300"]
    row["RR_meas"] = round(wmean(df, "RespirationRate", lo, hi), 1)
    row["Vt_meas"] = round(wmean(df, "TidalVolume", lo, hi), 1)
    row["PaCO2"] = round(wmean(df, "ArterialCarbonDioxidePressure", lo, hi), 1)
    row["SpO2"] = round(wmean(df, "OxygenSaturation", lo, hi), 3)
    severe_rows.append(row)

pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 40)

sv = pd.DataFrame(severe_rows).sort_values(["arm", "severity"]) if severe_rows else pd.DataFrame()
bd = pd.DataFrame(bound_rows).sort_values(["probe", "value"]) if bound_rows else pd.DataFrame()

print("=" * 110)
print("BLOC 1 -- BANDE SEVERE 0,96-0,99 : P/F PAR FENETRE ET PAR BRAS  (FiO2 = 0,40)")
print("=" * 110)
if len(sv):
    cols = ["arm", "severity", "status", "PF_60_120", "PF_108_168", "PF_240_300",
            "band_60_120", "band_108_168", "band_240_300"]
    print(sv[[c for c in cols if c in sv.columns]].to_string(index=False))

    print("\n--- la bande severe survit-elle aux trois fenetres ? ---")
    ok = sv[sv.status == "ok"]
    for _, r in ok.iterrows():
        bands = {r.get(f"band_{t}") for t in WINDOWS}
        verdict = ("SEVERE PARTOUT" if bands == {"severe"}
                   else f"DEPEND DE LA FENETRE {sorted(bands)}")
        print(f"  {r['arm']:>7}  sev {r['severity']:.2f}  -> {verdict}")

    print("\n--- chaine causale, fenetre [240,300] ---")
    c = ["arm", "severity", "RR_meas", "Vt_meas", "PaCO2", "PaO2_240_300",
         "PF_240_300", "SpO2"]
    print(ok[[x for x in c if x in ok.columns]].to_string(index=False))

    f = sv[sv.status == "FAILED"]
    print(f"\n--- echecs moteur : {len(f)} ---")
    if len(f):
        print(f[["arm", "severity", "exit_code", "errors"]].to_string(index=False))

print()
print("=" * 110)
print("BLOC 2 -- BORNES D'ACCEPTATION HR / RR")
print("=" * 110)
if len(bd):
    print(bd.to_string(index=False))
    print("\n--- attendu vs observe ---")
    EXPECT = {("HR", 49): "REJECTED", ("HR", 50): "ACCEPTED",
              ("HR", 110): "ACCEPTED", ("HR", 111): "REJECTED",
              ("RR", 7): "REJECTED", ("RR", 8): "ACCEPTED",
              ("RR", 20): "ACCEPTED", ("RR", 21): "REJECTED"}
    n_ok = 0
    for _, r in bd.iterrows():
        exp = EXPECT.get((r["probe"], r["value"]), "?")
        match = exp == r["outcome"]
        n_ok += match
        print(f"  {r['probe']} {r['value']:>3}  attendu {exp:>8}  "
              f"observe {r['outcome']:>8}  {'OK' if match else '<<< DESACCORD'}")
    print(f"\n  {n_ok}/{len(bd)} concordent avec les sondes du projet compagnon")

print()
print("=" * 110)
n_done = len(severe_rows) + len(bound_rows)
if incomplete:
    print(f"!! LECTURE PARTIELLE : {n_done}/{EXPECTED_RUNS} runs termines, "
          f"{len(incomplete)} encore en cours -- ne rien conclure sur ceux-la")
    for name in incomplete:
        print(f"     en cours : {name}")
elif n_done < EXPECTED_RUNS:
    print(f"!! {n_done}/{EXPECTED_RUNS} runs presents : {EXPECTED_RUNS - n_done} "
          f"jamais lances (repertoire absent)")
else:
    print(f"LOT COMPLET : {n_done}/{EXPECTED_RUNS} runs termines")

out = REPO / "results" / "s030b_analysis.csv"
pd.concat([sv, bd], ignore_index=True).to_csv(out, index=False)
print(f"-> {out}")
