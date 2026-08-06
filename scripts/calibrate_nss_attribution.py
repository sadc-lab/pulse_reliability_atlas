"""Read-only calibration of the exhaustive not_steady_state attribution.

Opened 2026-08-05 for the Figure 2 reframing dossier. This script WRITES
NOTHING. It reads the run-level sweep parquet and answers one question before
any attribution figure is drawn:

    Does re-applying the registered thresholds to the *stored per-channel
    statistics* reproduce the *stored* ``not_steady_state`` boolean on all
    1,280 runs?

If the answer is not 1280/1280 the stored statistics and the stored flag no
longer come from the same regime, and no per-output attribution built on those
statistics can be trusted.

Why this is not circular. ``src/analysis_compare.py`` and
``results/*.csv`` are outputs of the very chain under audit. This script starts
one level above them, at ``data/runs/full_sweep/aggregated.parquet``, the
run-level artefact, and re-derives the flags, the clean set, the (S1, M)
baseline, the traffic light and the driver decomposition from it.

Usage::

    uv run python scripts/calibrate_nss_attribution.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.detector import (  # noqa: E402
    CV_THRESHOLD,
    DRIFT_MAX_DELTA_60S,
    FLATLINE_BOUND_TOL,
    FLATLINE_STD_RATIO,
    HARD_BOUNDS,
)

AGG = REPO / "data" / "runs" / "full_sweep" / "aggregated.parquet"
CHANNELS = ("HR", "MAP", "Vt", "SpO2", "PaO2", "PaCO2")


def attribution(df: pd.DataFrame):
    """Per-channel not_steady_state triggers, both ways of counting them.

    Returns ``(exhaustive, first_cause, skipped, reconstructed_flag)``.

    ``exhaustive`` evaluates all three tests on every channel, so a channel that
    both oscillates and drifts is counted in both. ``first_cause`` replicates
    the detector's own record, which stops at the first test that fires
    (``continue`` after each branch, order flatline > CV > drift) and therefore
    undercounts co-occurring mechanisms -- by a factor of 44 on Vt.

    This is the single implementation. The figure script imports it rather than
    re-applying the thresholds, so the published panel cannot drift from the
    calibration that licensed it.
    """
    n = len(df)
    exhaustive = {ch: {"flatline": 0, "cv": 0, "drift": 0} for ch in CHANNELS}
    first_cause = {ch: {"flatline": 0, "cv": 0, "drift": 0} for ch in CHANNELS}
    skipped = {ch: 0 for ch in CHANNELS}
    recon = np.zeros(n, dtype=bool)

    for ch in CHANNELS:
        lo, hi = HARD_BOUNDS[ch]
        max_delta = DRIFT_MAX_DELTA_60S[ch]
        m = df[f"{ch}_mean"].to_numpy()
        s = df[f"{ch}_std"].to_numpy()
        c = df[f"{ch}_cv"].to_numpy()
        d = df[f"{ch}_delta_60s"].to_numpy()
        npts = df[f"{ch}_n_points"].to_numpy()

        for i in range(n):
            # A channel absent from the detector's `stats` dict is never
            # tested. build_row writes None/0 for exactly those channels.
            if not np.isfinite(m[i]) or npts[i] == 0:
                skipped[ch] += 1
                continue
            std_ratio = (s[i] / abs(m[i])) if abs(m[i]) > 0 else 0.0
            near_lo = abs(m[i] - lo) <= FLATLINE_BOUND_TOL * max(abs(lo), 1.0)
            near_hi = abs(m[i] - hi) <= FLATLINE_BOUND_TOL * max(abs(hi), 1.0)
            flat = bool(std_ratio < FLATLINE_STD_RATIO and (near_lo or near_hi))
            cvh = bool(c[i] > CV_THRESHOLD)
            dri = bool(abs(d[i]) > max_delta)

            if flat:
                exhaustive[ch]["flatline"] += 1
            if cvh:
                exhaustive[ch]["cv"] += 1
            if dri:
                exhaustive[ch]["drift"] += 1

            # detector's ordered checks: flatline > cv > drift, first wins
            if flat:
                first_cause[ch]["flatline"] += 1
            elif cvh:
                first_cause[ch]["cv"] += 1
            elif dri:
                first_cause[ch]["drift"] += 1

            if flat or cvh or dri:
                recon[i] = True

    return exhaustive, first_cause, skipped, recon


def main() -> None:
    df = pd.read_parquet(AGG)
    n = len(df)
    print(f"rows in {AGG.relative_to(REPO)}: {n}")

    exhaustive, first_cause, skipped, recon = attribution(df)

    stored = df["not_steady_state"].to_numpy().astype(bool)
    agree = int((recon == stored).sum())
    print("\n=== CALIBRATION: not_steady_state ===")
    print(f"  reconstructed True : {int(recon.sum())}")
    print(f"  stored        True : {int(stored.sum())}")
    print(f"  AGREEMENT          : {agree} / {n}")
    if agree != n:
        bad = df.index[recon != stored].tolist()[:20]
        print(f"  *** MISMATCH on {n - agree} runs, first 20 index: {bad}")

    print("\n=== per-output triggers: EXHAUSTIVE (non-exclusive) ===")
    print(f"{'output':>6} {'flatline':>9} {'CV>thr':>8} {'drift':>7} {'skipped':>8}")
    for ch in CHANNELS:
        e = exhaustive[ch]
        print(f"{ch:>6} {e['flatline']:>9} {e['cv']:>8} {e['drift']:>7} {skipped[ch]:>8}")

    print("\n=== per-output triggers: FIRST CAUSE ONLY (detector's record) ===")
    print(f"{'output':>6} {'flatline':>9} {'CV>thr':>8} {'drift':>7}")
    for ch in CHANNELS:
        f = first_cause[ch]
        print(f"{ch:>6} {f['flatline']:>9} {f['cv']:>8} {f['drift']:>7}")

    tot_e = sum(sum(v.values()) for v in exhaustive.values())
    tot_f = sum(sum(v.values()) for v in first_cause.values())
    print(f"\n  total trigger instances  exhaustive={tot_e}  first-cause={tot_f}"
          f"  (difference = {tot_e - tot_f} masked by the detector's `continue`)")

    # ---------- 2. flag partition, re-derived ---------- #
    clean = df["clean"].to_numpy().astype(bool)
    div = df["diverged"].to_numpy().astype(bool)
    imp = df["implausible"].to_numpy().astype(bool)
    clamp = df["clamped"].to_numpy().astype(bool)
    hard = div | imp | clamp
    print("\n=== flag partition, re-derived from run level ===")
    print(f"  clean                       : {int(clean.sum())} / {n}"
          f"  ({100 * clean.sum() / n:.1f} %)")
    print(f"  hard-failure-free (~hard)   : {int((~hard).sum())} / {n}"
          f"  ({100 * (~hard).sum() / n:.1f} %)")
    print(f"  clamped                     : {int(clamp.sum())}")
    print(f"  diverged                    : {int(div.sum())}")
    print(f"  implausible                 : {int(imp.sum())}")
    print(f"  diverged AND implausible    : {int((div & imp).sum())}  (0 => disjoint)")
    print(f"  nss as SOLE flag            : {int(((~hard) & ~clean).sum())}")
    print(f"  non-clean                   : {int((~clean).sum())}")

    print("\n=== per-cell retention, both screens ===")
    print(f"{'cell':>6} {'n':>5} {'clean':>6} {'4flag%':>8} {'hardfree':>9} {'hard%':>7}")
    for (sk, xk), g in df.groupby(["scenario", "sex"]):
        gh = (g["diverged"] | g["implausible"] | g["clamped"]).sum()
        nc = int(g["clean"].sum())
        hf = len(g) - int(gh)
        print(f"{sk}_{xk:>1} {len(g):>5} {nc:>6} {100 * nc / len(g):>7.1f}%"
              f" {hf:>9} {100 * hf / len(g):>6.1f}%")

    # ---------- 3. traffic light + driver decomposition ---------- #
    s1m = df[(df["scenario"] == "S1") & (df["sex"] == "M") & df["clean"]]
    counts = {"green": 0, "yellow": 0, "red": 0}
    drivers = {k: {"green": 0, "yellow": 0, "red": 0}
               for k in ("neither", "flag_only", "dev_only", "both")}
    for ch in CHANNELS:
        baseline = float(s1m[f"{ch}_mean"].mean())
        if not np.isfinite(baseline) or baseline == 0:
            continue
        for (_sk, _xk), g in df.groupby(["scenario", "sex"]):
            n_tot = len(g)
            n_hard = int(g["diverged"].sum() + g["implausible"].sum())
            gc = g[g["clean"]]
            mean_clean = float(gc[f"{ch}_mean"].mean()) if len(gc) else float("nan")
            if not np.isfinite(mean_clean):
                counts["red"] += 1
                continue
            pct_off = abs(mean_clean - baseline) / abs(baseline)
            rate = n_hard / max(n_tot, 1)
            if rate > 0.3 or pct_off > 0.3:
                light, dev_f, flg_f = "red", pct_off > 0.3, rate > 0.3
            elif pct_off > 0.1 or rate > 0.0:
                light, dev_f, flg_f = "yellow", pct_off > 0.1, rate > 0.0
            else:
                light, dev_f, flg_f = "green", False, False
            counts[light] += 1
            key = ("both" if dev_f and flg_f else
                   "dev_only" if dev_f else
                   "flag_only" if flg_f else "neither")
            drivers[key][light] += 1

    print("\n=== traffic light, re-derived from run level ===")
    print(f"  green={counts['green']}  yellow={counts['yellow']}  red={counts['red']}"
          f"  total={sum(counts.values())}")
    print("\n=== classification drivers ===")
    print(f"{'driver':>10} {'green':>6} {'yellow':>7} {'red':>5} {'total':>6}")
    for k, v in drivers.items():
        print(f"{k:>10} {v['green']:>6} {v['yellow']:>7} {v['red']:>5}"
              f" {sum(v.values()):>6}")


if __name__ == "__main__":
    main()
