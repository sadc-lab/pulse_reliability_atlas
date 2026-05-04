"""S015 P3.1 — synthetic positive control on detector.

Hand-crafts inputs that should deliberately trip each detector flag in
turn. Asserts the right flag fires (and only that flag, modulo
interactions with the steady-state stats which we treat as expected).

Detector flags (ordered by primary_flag priority):
    clamped > diverged > implausible > not_steady_state > clean
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from src.detector import (  # noqa: E402
    HARD_BOUNDS,
    classify,
    check_clamped,
    check_diverged,
    check_implausible,
    check_not_steady_state,
    compute_steady_state_stats,
)


def _safe(s: str) -> str:
    """Strip non-cp1252 chars so console.print never crashes on Windows."""
    return s.encode("ascii", errors="replace").decode("ascii")


def _baseline_csv(tmp: Path) -> Path:
    """13-row CSV in [60, 120] s window, all healthy values."""
    times = np.linspace(60, 120, 13)
    df = pd.DataFrame({
        "time_s": times,
        "HeartRate": np.full(13, 75.0),
        "MeanArterialPressure": np.full(13, 90.0),
        "TidalVolume": np.full(13, 500.0),
        "OxygenSaturation": np.full(13, 0.97),
        "ArterialOxygenPressure": np.full(13, 95.0),
        "ArterialCarbonDioxidePressure": np.full(13, 40.0),
    })
    p = tmp / "baseline.csv"
    df.to_csv(p, index=False)
    return p


def _csv_with_nan(tmp: Path) -> Path:
    p = _baseline_csv(tmp)
    df = pd.read_csv(p)
    df.loc[5, "HeartRate"] = float("nan")  # row 5 NaN
    df.to_csv(p, index=False)
    return p


def _csv_with_extreme_hr(tmp: Path) -> Path:
    """All-extreme HR=300 → mean outside HR hard bound (20, 220) → implausible."""
    p = _baseline_csv(tmp)
    df = pd.read_csv(p)
    df["HeartRate"] = 300.0
    df.to_csv(p, index=False)
    return p


def _csv_with_high_vt_cv(tmp: Path) -> Path:
    """Vt oscillating 250 / 750 alternating → CV ≈ 0.5 >> 0.05 → not_steady_state."""
    p = _baseline_csv(tmp)
    df = pd.read_csv(p)
    df["TidalVolume"] = [250.0 if i % 2 == 0 else 750.0 for i in range(len(df))]
    df.to_csv(p, index=False)
    return p


def main() -> int:
    tmp = REPO / "data" / "audit_S015" / "p31_synthetic"
    tmp.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print(_safe("S015 P3.1 - synthetic positive control on detector"))
    print("=" * 70)

    # --- Test 1: clamped via fake log ---
    fake_log = (
        "[ERROR] Patient systolic pressure baseline of 140 mmHg is too high. "
        "Maximum systolic pressure baseline allowed is 120 mmHg.\n"
    )
    r = check_clamped(fake_log)
    assert r.fired, f"clamped should fire on real Pulse error log; got {r}"
    print(_safe(f"[PASS] T1 clamped: regex matched on Pulse error log -> {r.reason}"))

    r = check_clamped("Resetting the target for X to Y. Solver normal text.")
    assert not r.fired, f"clamped MUST NOT fire on normal solver convergence text; got {r}"
    print(_safe(f"[PASS] T1b clamped: did NOT match normal solver text (regression test)"))

    # --- Test 2: diverged via NaN ---
    csv = _csv_with_nan(tmp)
    df = pd.read_csv(csv)
    r = check_diverged(csv, df, exit_code=0)
    assert r.fired and "NaN" in r.reason, f"diverged should fire on NaN row; got {r}"
    print(_safe(f"[PASS] T2 diverged: NaN at row 5 -> {r.reason}"))

    # diverged via exit_code != 0
    r = check_diverged(csv, df, exit_code=1)
    assert r.fired and "exit_code=1" in r.reason, f"diverged should fire on exit_code=1; got {r}"
    print(_safe(f"[PASS] T2b diverged: exit_code=1 -> {r.reason}"))

    # --- Test 3: implausible via HR=300 (above hard bound 220) ---
    csv = _csv_with_extreme_hr(tmp)
    df = pd.read_csv(csv)
    stats = compute_steady_state_stats(df)
    r = check_implausible(stats)
    assert r.fired and "HR" in r.reason, f"implausible should fire on HR=300; got {r}"
    print(_safe(f"[PASS] T3 implausible: HR=300 outside [20,220] -> {r.reason}"))

    # --- Test 4: not_steady_state via Vt CV > 5% ---
    csv = _csv_with_high_vt_cv(tmp)
    df = pd.read_csv(csv)
    stats = compute_steady_state_stats(df)
    cv = stats["Vt"].cv
    r = check_not_steady_state(stats)
    assert r.fired and "Vt" in r.reason, f"not_steady_state should fire on Vt CV high; got {r}"
    print(_safe(f"[PASS] T4 not_steady_state: Vt CV={cv:.3f} > 0.05 -> {r.reason}"))

    # --- Test 5: full classify() integration on extreme HR ---
    csv = _csv_with_extreme_hr(tmp)
    full = classify(csv, pulse_log="", exit_code=0)
    assert full.implausible.fired, "classify() should mark implausible"
    assert not full.diverged.fired, "classify() should not mark diverged"
    assert full.primary_flag == "implausible", f"primary_flag should be implausible; got {full.primary_flag}"
    print(_safe(f"[PASS] T5 classify integration: extreme HR -> primary={full.primary_flag}"))

    # --- Test 6: priority ordering — clamped beats implausible ---
    csv = _csv_with_extreme_hr(tmp)
    full = classify(csv, pulse_log=fake_log, exit_code=0)
    assert full.primary_flag == "clamped", f"clamped should beat implausible; got {full.primary_flag}"
    print(_safe(f"[PASS] T6 priority: clamped+implausible -> primary={full.primary_flag}"))

    # --- Test 7: drift detection ---
    p = _baseline_csv(tmp)
    df = pd.read_csv(p)
    # Inject a HR that drifts +10 bpm/60s — exceeds threshold of 5 bpm
    df["HeartRate"] = np.linspace(70, 80, len(df))  # +10 over 60 s
    df.to_csv(p, index=False)
    df = pd.read_csv(p)
    stats = compute_steady_state_stats(df)
    delta = stats["HR"].delta_60s
    r = check_not_steady_state(stats)
    assert r.fired and "HR" in r.reason, f"drift on HR should fire; got {r}"
    print(_safe(f"[PASS] T7 drift: HR delta_60s={delta:.2f} > 5 -> {r.reason}"))

    print("\nAll 7 positive-control tests PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
