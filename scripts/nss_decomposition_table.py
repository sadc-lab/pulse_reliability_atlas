"""S022 — Per-cell `not_steady_state` attribution side-table.

For each cell, decompose the locked nss count by which trigger sub-mode
fired. This is a presentation transform of the existing classifier
output: the locked classifier is unchanged. Two sub-modes are tracked:

  n_nss_locked                       : locked-classifier nss count (Table 1).
  n_nss_excl_SpO2_saturation         : nss runs that would *still* fire
                                       after removing the SpO2 "flatline
                                       at ceiling with mean >= 0.999"
                                       trigger — i.e. treating healthy
                                       physiological oxygen saturation
                                       (SpO2 -> 1.0 on adequate FiO2) as
                                       not pinning. This sub-mode is the
                                       only detector edge case identified
                                       in S022.
  n_nss_excl_F004_dyssynchrony       : nss runs that would still fire
                                       after removing the Vt CV > 0.05
                                       trigger. NB: this trigger captures
                                       the F-004 patient-ventilator
                                       dyssynchrony signal already
                                       documented in §3.8 of the
                                       manuscript and causally confirmed
                                       in S014 (trigger-pressure
                                       intervention, 96 % CV collapse).
                                       The TidalVolume CSV channel is
                                       breath-integrated and held, so
                                       this is real per-breath variance,
                                       NOT a sampling-aliasing artefact
                                       (corrected from initial S022
                                       draft).
  n_nss_excl_both                    : residual after excluding both —
                                       runs flagged by some other channel
                                       (HR / MAP / PaO2 / PaCO2 drift or
                                       flatline-at-low-bound), e.g. S4
                                       severe-ARDS slow convergence.

This table is a side-table companion to §3.1 Table 1, following the
F-003 precedent of HARD_BOUNDS_PHYSIOLOGICAL.

Outputs:
  results/s022/nss_decomposition.csv
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PARQUET = ROOT / "data" / "runs" / "full_sweep" / "aggregated.parquet"
OUT_DIR = ROOT / "results" / "s022"
OUT_DIR.mkdir(parents=True, exist_ok=True)


SPO2_SAT_THRESHOLD = 0.999  # SpO2 mean at/above this is treated as
# physiological saturation, not numerical pinning

FLATLINE_RE = re.compile(r"(\w+) flatline at extreme \(mean=([0-9.eE+\-]+)\)")
CV_RE = re.compile(r"(\w+) CV=([0-9.eE+\-]+) > ([0-9.eE+\-]+)")
DRIFT_RE = re.compile(r"(\w+) Δ60s=([+\-0-9.eE]+) > ([0-9.eE+\-]+)")


def parse_reason(reason: str) -> dict:
    """Return the set of (channel, sub-mode) triggers in a nss reason string."""
    if not isinstance(reason, str) or not reason:
        return {"flatline": set(), "cv": set(), "drift": set()}
    flatlines = {(m.group(1), float(m.group(2))) for m in FLATLINE_RE.finditer(reason)}
    cvs = {m.group(1) for m in CV_RE.finditer(reason)}
    drifts = {m.group(1) for m in DRIFT_RE.finditer(reason)}
    return {"flatline": flatlines, "cv": cvs, "drift": drifts}


def would_still_fire(parsed: dict, exclude_spo2_sat: bool, exclude_vt_cv: bool) -> bool:
    """Does this nss run still fire after excluding the named edge-case triggers?"""
    # surviving flatlines (drop SpO2 flatlines at mean >= SPO2_SAT_THRESHOLD)
    flatlines = set()
    for ch, mean in parsed["flatline"]:
        if exclude_spo2_sat and ch == "SpO2" and mean >= SPO2_SAT_THRESHOLD:
            continue
        flatlines.add(ch)
    # surviving CV triggers (drop Vt CV)
    cvs = set()
    for ch in parsed["cv"]:
        if exclude_vt_cv and ch == "Vt":
            continue
        cvs.add(ch)
    drifts = set(parsed["drift"])
    return bool(flatlines or cvs or drifts)


def main() -> None:
    df = pd.read_parquet(PARQUET)
    df = df.copy()
    df["cell"] = df["scenario"] + "_" + df["sex"]

    rows = []
    cell_order = ["S1_M", "S1_F", "S2_M", "S2_F", "S3_M", "S3_F", "S4_M", "S4_F"]
    for cell in cell_order:
        sub = df[df["cell"] == cell]
        n_total = len(sub)
        nss = sub[sub["not_steady_state"]]
        n_nss = len(nss)
        n_clean = int(sub["clean"].sum())

        n_excl_spo2 = 0
        n_excl_f004 = 0
        n_excl_both = 0
        for _, r in nss.iterrows():
            parsed = parse_reason(r["not_steady_state_reason"])
            if would_still_fire(parsed, exclude_spo2_sat=True, exclude_vt_cv=False):
                n_excl_spo2 += 1
            if would_still_fire(parsed, exclude_spo2_sat=False, exclude_vt_cv=True):
                n_excl_f004 += 1
            if would_still_fire(parsed, exclude_spo2_sat=True, exclude_vt_cv=True):
                n_excl_both += 1

        rows.append(
            {
                "cell": cell,
                "n_total": n_total,
                "n_nss_locked": n_nss,
                "n_nss_excl_SpO2_saturation": n_excl_spo2,
                "n_nss_excl_F004_dyssynchrony": n_excl_f004,
                "n_nss_excl_both": n_excl_both,
                "n_clean_locked": n_clean,
                "n_clean_excl_both": n_clean + (n_nss - n_excl_both),
            }
        )

    totals_row = {
        "cell": "Total",
        "n_total": sum(r["n_total"] for r in rows),
        "n_nss_locked": sum(r["n_nss_locked"] for r in rows),
        "n_nss_excl_SpO2_saturation": sum(r["n_nss_excl_SpO2_saturation"] for r in rows),
        "n_nss_excl_F004_dyssynchrony": sum(r["n_nss_excl_F004_dyssynchrony"] for r in rows),
        "n_nss_excl_both": sum(r["n_nss_excl_both"] for r in rows),
        "n_clean_locked": sum(r["n_clean_locked"] for r in rows),
        "n_clean_excl_both": sum(r["n_clean_excl_both"] for r in rows),
    }
    rows.append(totals_row)

    out = pd.DataFrame(rows)
    out_path = OUT_DIR / "nss_decomposition.csv"
    out.to_csv(out_path, index=False)
    print(out.to_string(index=False))
    print(f"\nWrote {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
