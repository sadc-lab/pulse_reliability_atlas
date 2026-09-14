"""Re-derive the S030 values that Supplement §S5 publishes but no artefact holds.

Why this script exists
----------------------
`results/s030_pf_by_arm.csv` carries the S030 replication at the atlas window
[60, 120] s and at [240, 300] s. Supplement §S5 additionally publishes:

  * P/F at the *companion's* measurement window [108, 168] s -- 256.5, 150.5
    and 96.6 mmHg, plus 199.8 and 121.0 behind the "within 2 %" claim;
  * an alveolar chain -- alveolar PO2 231.4 -> 230.7 mmHg and alveolar-arterial
    gradients 196.6 / 185.6 (free arm) and 184.9 mmHg (locked arm).

None of those numbers exists in a committed artefact: `abd1e5f` wrote them into
a register only, and `results/s030b_analysis.csv` carries a [108, 168] column
for impairment 0.96-0.99 alone. This script recomputes them from the S030 run
CSVs and writes `results/s030_published_value_provenance.csv`, so the published
literals become traceable inside the repository.

Availability limit, deliberately not hidden
-------------------------------------------
`data/runs/s030_ards_berlin_recalibration/**` is gitignored (`.gitignore:19-23`
excludes every `output.csv`, `pulse.log`, `config.json` and `run_meta.json`
under `data/runs/`). This script therefore runs only where the raw runs exist.
The artefact it writes IS committed, so the guard in `audit_claims.py`
(`check_s030_provenance`) stays live on every clone -- but on a clone without
the raw runs, nothing re-checks the artefact against the runs. Full public
reproducibility waits on the raw-data deposit planned with the release.

Conventions, all declared before the first number was computed
--------------------------------------------------------------
* Window membership reproduces the producing scripts EXACTLY, which since
  2026-08-13 means the atlas rule: `time_s >= lo - 1e-6` and
  `time_s <= hi + 1e-6`, i.e. `src/detector.py::_steady_state_window`, the
  window every published mean of the 1,280-run sweep already used
  (`scripts/analyze_s030.py`, `scripts/analyze_s030b.py`).
  This is not cosmetic. The recorded grid drifts: a nominal t = 120 s is stored
  as 120.0000000000557 and a nominal t = 300 s as 299.99999999991473. Without
  the slack the first is dropped, so the same nominal window held 12 samples in
  S030 and 13 in the main sweep, and the free 0.95 run read P/F 86.83 instead
  of 87.34. The two conventions never disagreed on a Berlin band; they
  disagreed on which samples "the atlas window" names. The drift is recorded
  per row (`n_samples`, `t_first_s`, `t_last_s`) so the effective window stays
  visible rather than assumed.
* P/F = mean(PaO2 over the window) / FiO2, with FiO2 read per run from
  `config.json` -- never assumed.
* Alveolar PO2 uses the repository's own alveolar-gas convention: dry
  barometric pressure 760 - 47 = 713 mmHg and respiratory quotient R = 0.8,
  i.e. PAO2 = FiO2 * 713 - mean(PaCO2) / 0.8. That is the same convention that
  yields the 663 mmHg sea-level ceiling quoted at FiO2 = 1.0 in the paper.
* Alveolar-arterial gradient = PAO2 - mean(PaO2).
* AGREEMENT TOLERANCE = 0.05 mmHg against each published literal: the published
  values carry one decimal, so 0.05 means "rounds to the same printed value".
  A miss is reported and exits non-zero. It is never silently retuned.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
RUNS = REPO / "data" / "runs" / "s030_ards_berlin_recalibration"
OUT = REPO / "results" / "s030_published_value_provenance.csv"

DRY_BAROMETRIC_MMHG = 760.0 - 47.0
RESPIRATORY_QUOTIENT = 0.8
TOLERANCE_MMHG = 0.05
TIME_SLACK_S = 1e-6  # src/detector.py::_steady_state_window

WINDOWS: dict[str, tuple[float, float]] = {
    "atlas_60_120": (60.0, 120.0),
    "calibration_108_168": (108.0, 168.0),
    "late_240_300": (240.0, 300.0),
}

# Companion anchors, transcribed from audit/S030_recalibration_plan.md. They are
# the ORIGINAL March 2026 28-run calibration, recorded in
# Pulse_translation_new/experiments_log.md ("ARDS Severity Calibration --
# Impairment Fraction Sweep (March 2026)"). They are NOT in
# data/engine_runs/e6_ards_calibration/results.json: that file is the April E6
# refinement, which gave 251.9 / 148.2 / 74.8 at 0.26 / 0.60 / 0.95 and is only
# the source of the settle/duration timing used for the [108, 168] s window.
# Corrected 2026-09-14 (audit/number_inventory.md section 4.1, F-S1).
COMPANION_PF: dict[float, float] = {
    0.26: 256.0,
    0.30: 199.3,
    0.60: 150.1,
    0.90: 118.7,
    0.95: 96.1,
}

# What the manuscript publishes. (locus, arm, severity, window, quantity, value)
PUBLISHED: list[tuple[str, str, float, str, str, float]] = [
    ("supplement.tex:421", "free", 0.26, "calibration_108_168", "pf", 256.5),
    ("supplement.tex:421", "free", 0.60, "calibration_108_168", "pf", 150.5),
    ("supplement.tex:421,440", "free", 0.95, "calibration_108_168", "pf", 96.6),
    ("S030_recalibration_plan.md §1", "free", 0.30, "calibration_108_168", "pf", 199.8),
    ("S030_recalibration_plan.md §1", "free", 0.90, "calibration_108_168", "pf", 121.0),
    ("supplement.tex:440", "free", 0.95, "atlas_60_120", "alveolar_po2", 231.3),
    ("supplement.tex:440", "free", 0.95, "late_240_300", "alveolar_po2", 230.7),
    ("supplement.tex:440", "free", 0.95, "atlas_60_120", "aa_gradient", 196.4),
    ("supplement.tex:440", "free", 0.95, "late_240_300", "aa_gradient", 185.7),
    ("supplement.tex:440", "locked", 0.95, "late_240_300", "aa_gradient", 185.1),
    ("supplement.tex:440", "free", 0.95, "atlas_60_120", "pf", 87.3),
    ("supplement.tex:440", "free", 0.95, "late_240_300", "pf", 112.6),
    ("supplement.tex:440", "locked", 0.95, "atlas_60_120", "pf", 69.4),
    ("supplement.tex:440", "locked", 0.95, "late_240_300", "pf", 91.5),
]

ARM_PREFIX = {"free": "fr", "locked": "lk"}


def _fail(msg: str) -> None:
    print(f"\nBLOCKING ASSERTION FAILED: {msg}")
    sys.exit(1)


def _case_name(arm: str, sex: str, severity: float) -> str:
    """S030 directory naming: s030_<fr|lk>_<M|F>_0p260."""
    return f"s030_{ARM_PREFIX[arm]}_{sex}_" + f"{severity:.3f}".replace(".", "p")


def measure(arm: str, sex: str, severity: float) -> list[dict[str, object]]:
    case = _case_name(arm, sex, severity)
    d = RUNS / case
    if not d.is_dir():
        _fail(f"missing run directory {d}")

    cfg = json.loads((d / "config.json").read_text(encoding="utf-8"))
    fio2 = float(cfg["ventilator"]["fio2"])
    if not 0.0 < fio2 <= 1.0:
        _fail(f"{case}: implausible FiO2 {fio2}")

    df = pd.read_csv(d / "output.csv")
    for col in ("time_s", "ArterialOxygenPressure", "ArterialCarbonDioxidePressure"):
        if col not in df.columns:
            _fail(f"{case}: column {col} absent from output.csv")

    rows: list[dict[str, object]] = []
    for window, (lo, hi) in WINDOWS.items():
        # Exactly the producing scripts' comparison -- see the module docstring.
        w = df[(df["time_s"] >= lo - TIME_SLACK_S) & (df["time_s"] <= hi + TIME_SLACK_S)]
        if w.empty:
            _fail(f"{case}: window {window} contains no sample")
        pao2 = float(w["ArterialOxygenPressure"].mean())
        paco2 = float(w["ArterialCarbonDioxidePressure"].mean())
        alveolar = fio2 * DRY_BAROMETRIC_MMHG - paco2 / RESPIRATORY_QUOTIENT
        rows.append(
            {
                "case_id": case,
                "arm": arm,
                "sex": sex,
                "severity": severity,
                "fio2": fio2,
                "window": window,
                "t_lo_s": lo,
                "t_hi_s": hi,
                "n_samples": int(len(w)),
                "t_first_s": round(float(w["time_s"].min()), 3),
                "t_last_s": round(float(w["time_s"].max()), 3),
                "pao2_mmhg": round(pao2, 4),
                "paco2_mmhg": round(paco2, 4),
                "pf_mmhg": round(pao2 / fio2, 4),
                "alveolar_po2_mmhg": round(alveolar, 4),
                "aa_gradient_mmhg": round(alveolar - pao2, 4),
            }
        )
    return rows


def main() -> int:
    if not RUNS.is_dir():
        print(
            "S030 raw runs absent (gitignored). Nothing recomputed; the committed\n"
            f"artefact {OUT.relative_to(REPO)} is what the audit guard reads."
        )
        return 0

    records: list[dict[str, object]] = []
    for arm in ("free", "locked"):
        for severity in sorted(COMPANION_PF):
            records.extend(measure(arm, "M", severity))
    out = pd.DataFrame.from_records(records)
    out.to_csv(OUT, index=False)
    print(f"wrote {OUT.relative_to(REPO)}  ({len(out)} rows)\n")

    print("| locus | arm | sev | window | quantity | published | recomputed | delta |")
    print("|---|---|---:|---|---|---:|---:|---:|")
    n_bad = 0
    for locus, arm, severity, window, quantity, published in PUBLISHED:
        sel = out[
            (out["arm"] == arm) & (out["severity"] == severity) & (out["window"] == window)
        ]
        if len(sel) != 1:
            _fail(f"{arm}/{severity}/{window}: expected exactly one row, got {len(sel)}")
        col = {"pf": "pf_mmhg", "alveolar_po2": "alveolar_po2_mmhg",
               "aa_gradient": "aa_gradient_mmhg"}[quantity]
        got = float(sel.iloc[0][col])
        delta = got - published
        ok = abs(delta) <= TOLERANCE_MMHG
        n_bad += 0 if ok else 1
        print(
            f"| {locus} | {arm} | {severity} | {window} | {quantity} | {published} "
            f"| {got:.2f} | {delta:+.3f} {'' if ok else '**MISS**'} |"
        )

    # The two tolerance statements §S5 makes about the companion comparison.
    def pct(sev: float) -> float:
        row = out[
            (out["arm"] == "free")
            & (out["severity"] == sev)
            & (out["window"] == "calibration_108_168")
        ].iloc[0]
        return 100.0 * (float(row["pf_mmhg"]) - COMPANION_PF[sev]) / COMPANION_PF[sev]

    three = max(abs(pct(s)) for s in (0.26, 0.60, 0.95))
    five = max(abs(pct(s)) for s in COMPANION_PF)
    print(f"\nmax deviation, three published fractions: {three:.3f} %  (published bound 0.6 %)")
    print(f"max deviation, all five fractions:        {five:.3f} %  (published bound 2 %)")
    if three > 0.6:
        n_bad += 1
        print("**MISS** the 0.6 % bound does not hold")
    if five > 2.0:
        n_bad += 1
        print("**MISS** the 2 % bound does not hold")

    print(f"\n{len(PUBLISHED) + 2 - n_bad} / {len(PUBLISHED) + 2} checks agree "
          f"(tolerance {TOLERANCE_MMHG} mmHg).")
    return 1 if n_bad else 0


if __name__ == "__main__":
    sys.exit(main())
