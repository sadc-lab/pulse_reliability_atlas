"""Export the per-cell reliability traffic-light as clean, machine-readable
CSV + JSON artefacts for the paper's Data Availability statement.

The atlas provides a *conservative curation and review-priority layer* for
downstream Pulse users. This script turns the canonical classification
artefact (``results/reliability_classification.csv``, produced by
``src.analysis_compare.reliability_classification`` and consumed by the npj
paper's Figure 1) into two self-describing, deposit-ready files:

    results/reliability_traffic_light.csv   -- tidy table, rounded for display
    results/reliability_traffic_light.json  -- same rows + documented rule

This is a pure re-export: the ``light`` verdict for every (scenario, sex,
output) cell is copied VERBATIM from the canonical CSV. No thresholds are
recomputed or invented here -- the classification rule below is quoted from
``src/analysis_compare.py`` solely as machine-readable provenance, so the
JSON is interpretable without reading the source.

Usage::

    uv run python scripts/export_traffic_light.py
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "results" / "reliability_classification.csv"
OUT_CSV = REPO / "results" / "reliability_traffic_light.csv"
OUT_JSON = REPO / "results" / "reliability_traffic_light.json"

# Classification rule, quoted verbatim from
# src/analysis_compare.py::reliability_classification (do NOT diverge -- this
# is documentation of the canonical rule, not a re-implementation of it).
CLASSIFICATION_RULE = {
    "baseline": (
        "Per output channel, the mean of clean S1_M (healthy male) runs; all "
        "cells are scored as a fractional deviation from this common baseline."
    ),
    "hard_failure_rate": "(n_diverged + n_implausible) / n_total for the cell.",
    "green": "no diverged/implausible runs AND clean-run mean within 10% of baseline.",
    "yellow": "any diverged/implausible run OR clean-run mean 10-30% off baseline.",
    "red": "clean-run mean >30% off baseline OR hard_failure_rate >30% (or no clean runs).",
    "thresholds": {"green_max_pct_off": 0.10, "red_min_pct_off": 0.30,
                   "red_min_hard_failure_rate": 0.30},
}


def main() -> None:
    df = pd.read_csv(SRC)

    tidy = pd.DataFrame({
        "scenario": df["scenario"],
        "sex": df["sex"],
        "output": df["output"],
        "light": df["light"],
        "clean_mean": df["mean_clean"].round(2),
        "baseline_s1m": df["baseline_S1M"].round(2),
        "pct_off_baseline": df["pct_off_baseline"].round(4),
        "n_total": df["n_total"].astype(int),
        "n_diverged": df["n_diverged"].astype(int),
        "n_implausible": df["n_implausible"].astype(int),
    })
    tidy = tidy.sort_values(["scenario", "sex", "output"]).reset_index(drop=True)
    tidy.to_csv(OUT_CSV, index=False)

    counts = tidy["light"].value_counts().to_dict()
    payload = {
        "description": (
            "Per-cell curation and review-priority map for the Pulse Physiology "
            "Engine v4.3.1 adult operational envelope. One classification per "
            "(scenario, sex, output) combination; intended as a conservative "
            "curation layer on synthetic patient cohorts, not a "
            "distribution-neutral automatic filter. The colour sets cell-level "
            "review priority; run-level four-flag screening remains necessary "
            "irrespective of colour, because the colour does not count runs "
            "flagged not_steady_state. Red = per-channel justification "
            "required before downstream use. The colour combines "
            "the hard-flag rate with deviation from the healthy-male (S1, M) "
            "baseline, and does not constitute external physiological "
            "validation."
        ),
        "source_artifact": "results/reliability_classification.csv",
        "generated_by": "scripts/export_traffic_light.py",
        "pulse_version": "4.3.1",
        "classification_rule": CLASSIFICATION_RULE,
        "counts": {
            "green": int(counts.get("green", 0)),
            "yellow": int(counts.get("yellow", 0)),
            "red": int(counts.get("red", 0)),
            "total": int(len(tidy)),
        },
        "cells": tidy.to_dict(orient="records"),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_CSV.relative_to(REPO)}  ({len(tidy)} cells)")
    print(f"Wrote {OUT_JSON.relative_to(REPO)}")
    print(f"  traffic-light counts: {payload['counts']}")


if __name__ == "__main__":
    main()
