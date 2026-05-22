"""S022 — No-compute diagnostic: classify not_steady_state failure modes.

For the top-3 unstable cells (by not_steady_state rate), parse the
`not_steady_state_reason` field to attribute each flagged run to one or more
sub-modes:

    flatline_high   — channel pinned at hard-bound ceiling
    flatline_low    — channel pinned at hard-bound floor
    cv_high         — coefficient of variation > CV_THRESHOLD
    drift_high      — |delta_60s| > DRIFT_MAX_DELTA_60S

Per channel.

Inputs: data/runs/full_sweep/aggregated.parquet
Output: results/s022/diagnostic_nss_classify.json (and stdout summary)
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import pandas as pd

from src.detector import HARD_BOUNDS

ROOT = Path(__file__).resolve().parents[1]
PARQUET = ROOT / "data" / "runs" / "full_sweep" / "aggregated.parquet"
OUT_DIR = ROOT / "results" / "s022"
OUT_DIR.mkdir(parents=True, exist_ok=True)


CHANNELS = ["HR", "MAP", "Vt", "SpO2", "PaO2", "PaCO2"]

# Patterns in `not_steady_state_reason` (delta is unicode Δ in source)
FLATLINE_RE = re.compile(r"(\w+) flatline at extreme \(mean=([0-9.eE+\-]+)\)")
CV_RE = re.compile(r"(\w+) CV=([0-9.eE+\-]+) > ([0-9.eE+\-]+)")
DRIFT_RE = re.compile(r"(\w+) Δ60s=([+\-0-9.eE]+) > ([0-9.eE+\-]+)")


def classify_reason(reason: str) -> dict[str, list[tuple[str, str]]]:
    """Return per-submode list of (channel, value) tuples for a single reason string."""
    out = {"flatline_high": [], "flatline_low": [], "cv_high": [], "drift_high": []}
    if not isinstance(reason, str) or not reason:
        return out
    for m in FLATLINE_RE.finditer(reason):
        ch, val = m.group(1), float(m.group(2))
        lo, hi = HARD_BOUNDS.get(ch, (float("-inf"), float("inf")))
        # near upper bound vs lower bound
        if abs(val - hi) <= abs(val - lo):
            out["flatline_high"].append((ch, m.group(2)))
        else:
            out["flatline_low"].append((ch, m.group(2)))
    for m in CV_RE.finditer(reason):
        out["cv_high"].append((m.group(1), m.group(2)))
    for m in DRIFT_RE.finditer(reason):
        out["drift_high"].append((m.group(1), m.group(2)))
    return out


def main() -> None:
    df = pd.read_parquet(PARQUET)
    df = df.copy()
    df["cell"] = df["scenario"] + "_" + df["sex"]

    # cell-level rates
    cell_stats = (
        df.groupby("cell")
        .agg(
            n=("case_id", "count"),
            n_nss=("not_steady_state", "sum"),
            n_clamped=("clamped", "sum"),
            n_diverged=("diverged", "sum"),
            n_implausible=("implausible", "sum"),
            n_clean=("clean", "sum"),
        )
        .reset_index()
    )
    cell_stats["nss_rate"] = cell_stats["n_nss"] / cell_stats["n"]
    cell_stats = cell_stats.sort_values("nss_rate", ascending=False).reset_index(drop=True)

    top3 = cell_stats.head(3)["cell"].tolist()
    print("Top-3 unstable cells (by not_steady_state rate):")
    print(cell_stats.head(3).to_string(index=False))
    print()

    per_cell_report: dict[str, dict] = {}

    for cell in top3:
        sub = df[(df["cell"] == cell) & (df["not_steady_state"])]
        n_nss = len(sub)

        # per-submode counters: how many flagged runs hit each submode
        run_hit_submode = {
            "flatline_high": 0,
            "flatline_low": 0,
            "cv_high": 0,
            "drift_high": 0,
        }
        # per-submode per-channel counters
        submode_channel = {
            "flatline_high": Counter(),
            "flatline_low": Counter(),
            "cv_high": Counter(),
            "drift_high": Counter(),
        }
        # combinations seen on a single run (e.g. cv_high + flatline_high)
        combo_counter: Counter = Counter()
        # which channel dominates this cell overall
        channel_total: Counter = Counter()

        for reason in sub["not_steady_state_reason"]:
            parts = classify_reason(reason)
            active_submodes = []
            for sm, items in parts.items():
                if items:
                    run_hit_submode[sm] += 1
                    active_submodes.append(sm)
                    for ch, _ in items:
                        submode_channel[sm][ch] += 1
                        channel_total[ch] += 1
            combo_counter[tuple(sorted(active_submodes))] += 1

        # Cross-check: is the dominant Vt-CV story being driven by a particular
        # operational input bin? Bucket by RR (high RR is a known driver of
        # ventilator/patient timing mismatch under VC-AC).
        rr_buckets = pd.cut(
            sub["in_rr"],
            bins=[0, 10, 14, 18, 25],
            labels=["≤10", "11-14", "15-18", ">18"],
        )
        rr_x_submode = sub.assign(rr_bucket=rr_buckets)
        rr_summary = {}
        for bucket, idx in rr_x_submode.groupby("rr_bucket", observed=False).groups.items():
            chunk = sub.loc[idx]
            n = len(chunk)
            if n == 0:
                continue
            cv_hits = chunk["not_steady_state_reason"].str.contains(
                "CV=", regex=False, na=False
            ).sum()
            fl_hits = chunk["not_steady_state_reason"].str.contains(
                "flatline at extreme", regex=False, na=False
            ).sum()
            dr_hits = chunk["not_steady_state_reason"].str.contains(
                "Δ60s=", regex=True, na=False
            ).sum()
            rr_summary[str(bucket)] = dict(n=n, cv=int(cv_hits), flatline=int(fl_hits), drift=int(dr_hits))

        per_cell_report[cell] = dict(
            n_nss=int(n_nss),
            run_hit_submode={k: int(v) for k, v in run_hit_submode.items()},
            submode_channel={
                sm: dict(cnt) for sm, cnt in submode_channel.items()
            },
            channel_total=dict(channel_total),
            combo_counter={
                "+".join(k) if k else "none": int(v)
                for k, v in combo_counter.items()
            },
            rr_bucket_summary=rr_summary,
        )

    out = {
        "top3_cells": top3,
        "cell_stats": cell_stats.to_dict(orient="records"),
        "per_cell": per_cell_report,
        "notes": (
            "flatline_high/low classified by proximity of the reported mean to "
            "the upper vs lower HARD_BOUNDS for that channel. A run can hit "
            "multiple sub-modes on different channels; counts in run_hit_submode "
            "and submode_channel are not mutually exclusive."
        ),
    }

    out_path = OUT_DIR / "diagnostic_nss_classify.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"Wrote {out_path.relative_to(ROOT)}")
    print()
    print("=== Failure-mode classification by cell ===")
    for cell in top3:
        rep = per_cell_report[cell]
        nss = rep["n_nss"]
        print(f"\n--- {cell}  (n_nss={nss}) ---")
        print("  Sub-mode incidence (runs hit, may overlap):")
        for sm, n in rep["run_hit_submode"].items():
            pct = 100 * n / nss if nss else 0
            print(f"    {sm:<14s}: {n:>4d}  ({pct:5.1f}%)")
        print("  Per-channel hit counts (across all sub-modes):")
        for ch, n in sorted(rep["channel_total"].items(), key=lambda kv: -kv[1]):
            print(f"    {ch:<6s}: {n}")
        print("  Top combos (sub-modes co-firing on same run):")
        for combo, n in sorted(rep["combo_counter"].items(), key=lambda kv: -kv[1])[:5]:
            print(f"    {n:>4d}  {combo}")
        print("  By RR bucket:")
        for bucket, d in rep["rr_bucket_summary"].items():
            print(f"    RR {bucket:<6s} n={d['n']:>3d}  cv={d['cv']:>3d}  flatline={d['flatline']:>3d}  drift={d['drift']:>3d}")


if __name__ == "__main__":
    main()
