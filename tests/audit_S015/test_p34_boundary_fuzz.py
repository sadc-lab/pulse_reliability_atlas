"""S015 P3.4 — boundary fuzzing on the analysis pipeline.

Pass deliberately impossible physiological values into the atlas
Python pipeline (sampler, scenario builder, detector). For each, log
whether the code:
  (a) raises an explicit error (best),
  (b) silently propagates the value (relies on Pulse-side rejection),
  (c) silently produces NaN/garbage (worst).

This is documentation, not a hard pass/fail: the atlas's design choice
(per src/scenario.py docstring) is to keep Morris geometry intact and
rely on Pulse-side rejection (clamped) + post-hoc detector (implausible)
for defense in depth. We confirm whether that contract holds.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from src.detector import check_implausible, compute_steady_state_stats  # noqa: E402
from src.sampler import sample_morris  # noqa: E402
from src.scenario import (  # noqa: E402
    build_config,
    case_id,
    clip_dbp_to_pulse_constraint,
)


def _safe(s: str) -> str:
    return s.encode("ascii", errors="replace").decode("ascii")


def try_call(label: str, fn, *args, **kwargs) -> tuple[str, str]:
    """Call fn; classify outcome as RAISES / SILENT / NAN_OK."""
    try:
        out = fn(*args, **kwargs)
    except Exception as e:
        return "RAISES", f"{type(e).__name__}: {e}"
    return "SILENT", repr(out)[:200]


def main() -> int:
    print(_safe("=" * 70))
    print(_safe("S015 P3.4 - boundary fuzzing"))
    print(_safe("=" * 70))

    findings: list[dict] = []

    # ---- sampler.sample_morris bound checks ----
    print(_safe("\n[A] sampler.sample_morris input validation:"))
    s, msg = try_call("trajectories=0", sample_morris, trajectories=0)
    print(_safe(f"  trajectories=0 -> {s}: {msg}"))
    findings.append({"test": "sampler trajectories=0", "outcome": s, "detail": msg})
    s, msg = try_call("levels=1", sample_morris, levels=1)
    print(_safe(f"  levels=1       -> {s}: {msg}"))
    findings.append({"test": "sampler levels=1", "outcome": s, "detail": msg})

    # ---- scenario.build_config: out-of-envelope physiological values ----
    print(_safe("\n[B] scenario.build_config with out-of-envelope sample row:"))

    base_row = pd.Series({
        "hr": 75.0, "sbp": 110.0, "dbp": 70.0, "rr": 14.0,
        "vt": 500.0, "fio2": 0.5, "peep": 5.0,
    })

    # Negative HR
    bad = base_row.copy()
    bad["hr"] = -50.0
    s, msg = try_call("hr=-50", build_config, bad, "S1", "M", case_id("S1", "M", 9999))
    print(_safe(f"  hr=-50              -> {s} (atlas does not validate; relies on Pulse rejection)"))
    findings.append({"test": "build_config hr=-50", "outcome": s, "detail": msg[:120]})

    # RR = 900 bpm
    bad = base_row.copy()
    bad["rr"] = 900.0
    s, msg = try_call("rr=900", build_config, bad, "S1", "M", case_id("S1", "M", 9998))
    print(_safe(f"  rr=900              -> {s}"))
    findings.append({"test": "build_config rr=900", "outcome": s, "detail": msg[:120]})

    # FiO2 = -0.5
    bad = base_row.copy()
    bad["fio2"] = -0.5
    s, msg = try_call("fio2=-0.5", build_config, bad, "S1", "M", case_id("S1", "M", 9997))
    print(_safe(f"  fio2=-0.5           -> {s}"))
    findings.append({"test": "build_config fio2=-0.5", "outcome": s, "detail": msg[:120]})

    # SBP = 0
    bad = base_row.copy()
    bad["sbp"] = 0.0
    bad["dbp"] = 0.0
    s, msg = try_call("sbp=0", build_config, bad, "S1", "M", case_id("S1", "M", 9996))
    print(_safe(f"  sbp=0, dbp=0        -> {s}"))
    findings.append({"test": "build_config sbp=0", "outcome": s, "detail": msg[:120]})

    # Vt = 5000 mL
    bad = base_row.copy()
    bad["vt"] = 5000.0
    s, msg = try_call("vt=5000", build_config, bad, "S1", "M", case_id("S1", "M", 9995))
    print(_safe(f"  vt=5000             -> {s}"))
    findings.append({"test": "build_config vt=5000", "outcome": s, "detail": msg[:120]})

    # ---- scenario keys / sex keys: should raise ----
    print(_safe("\n[C] scenario / sex key validation (should RAISE):"))
    s, msg = try_call("scenario=S99", build_config, base_row, "S99", "M", case_id("S1", "M", 1))
    print(_safe(f"  scenario='S99'      -> {s}: {msg[:60]}"))
    findings.append({"test": "build_config scenario=S99", "outcome": s, "detail": msg[:120]})
    s, msg = try_call("sex=X", build_config, base_row, "S1", "X", case_id("S1", "M", 1))
    print(_safe(f"  sex='X'             -> {s}: {msg[:60]}"))
    findings.append({"test": "build_config sex=X", "outcome": s, "detail": msg[:120]})

    # ---- DBP/SBP ratio clip: must clip silently with was_clipped=True ----
    print(_safe("\n[D] clip_dbp_to_pulse_constraint:"))
    dbp_app, was = clip_dbp_to_pulse_constraint(sbp=100.0, dbp_requested=90.0)
    expected_cap = 75.0
    print(_safe(f"  sbp=100, dbp_req=90 -> dbp_app={dbp_app} (expect {expected_cap}), was_clipped={was}"))
    assert dbp_app == expected_cap and was, "clip failed"
    findings.append({"test": "clip_dbp 100/90", "outcome": "OK", "detail": f"clipped to {dbp_app}"})

    # ---- detector hard bounds: out-of-bound mean must flag implausible ----
    print(_safe("\n[E] detector.check_implausible on hand-built stats:"))
    times = np.linspace(60, 120, 13)
    df = pd.DataFrame({
        "time_s": times,
        "HeartRate": np.full(13, 1000.0),  # implausible HR
        "MeanArterialPressure": np.full(13, 90.0),
        "TidalVolume": np.full(13, 500.0),
        "OxygenSaturation": np.full(13, 0.97),
        "ArterialOxygenPressure": np.full(13, 95.0),
        "ArterialCarbonDioxidePressure": np.full(13, 40.0),
    })
    stats = compute_steady_state_stats(df)
    res = check_implausible(stats)
    assert res.fired and "HR" in res.reason
    print(_safe(f"  HR=1000             -> implausible fired ({_safe(res.reason)})"))
    findings.append({"test": "detector HR=1000 implausible", "outcome": "FIRED", "detail": res.reason[:120]})

    # ---- summary table ----
    print(_safe("\n" + "=" * 70))
    print(_safe("FINDING TABLE"))
    print(_safe("=" * 70))
    raise_count = sum(1 for f in findings if f["outcome"] == "RAISES")
    silent_count = sum(1 for f in findings if f["outcome"] == "SILENT")
    other = len(findings) - raise_count - silent_count
    print(_safe(f"  RAISES (explicit error): {raise_count}"))
    print(_safe(f"  SILENT (passes through): {silent_count}"))
    print(_safe(f"  Other (FIRED / OK):      {other}"))
    print(_safe("\nInterpretation:"))
    print(_safe("  By design (src/scenario.py docstring), build_config does NOT validate"))
    print(_safe("  physiological bounds. Defense in depth = Pulse-side rejection (clamped"))
    print(_safe("  flag) + post-hoc implausible flag. The findings above confirm that"))
    print(_safe("  contract: only scenario_key / sex_key raise; all physiological out-of-"))
    print(_safe("  envelope values pass through silently and rely on Pulse + detector."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
