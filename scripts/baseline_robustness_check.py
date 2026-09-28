"""Robustness check: does the reliability traffic-light depend on scoring every
cell against a single healthy-MALE (S1_M) baseline?

The locked classifier (``src/analysis_compare.reliability_classification``)
scores every (scenario, sex, output) cell as a fractional deviation from a
common S1_M baseline. This script re-scores the 24 FEMALE cells against a
sex-specific S1_F baseline instead, holding the flag-rate logic unchanged, and
reports how many female cells change colour.

Result (Pulse v4.3.1 canonical sweep): 0 of 24 female combinations change
colour. Female yellow/red colours are set either by the diverged/implausible
flag rate or by ARDS-scale deviations (13.3 % and above) that exceed the
healthy-cell male-female differences (0.3 to 11.3 %). Only S1_F PaCO2 crosses
10 % on the sex difference alone, and its cell's hard flags already make it
yellow. Referenced from Supplement S3.9 (traffic-light baseline robustness).

Usage::

    uv run python scripts/baseline_robustness_check.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "results" / "reliability_classification.csv"


def _color(pct_off: float, n_div: int, n_imp: int, n_tot: int) -> str:
    """Locked green/yellow/red rule from src/analysis_compare.py (verbatim logic)."""
    hard_failure_rate = (n_div + n_imp) / max(n_tot, 1)
    if not np.isfinite(pct_off):
        return "red"
    if hard_failure_rate > 0.3 or pct_off > 0.3:
        return "red"
    if pct_off > 0.1 or hard_failure_rate > 0.0:
        return "yellow"
    return "green"


def main() -> None:
    df = pd.read_csv(SRC)
    fem = df[df["sex"] == "F"].copy()
    # sex-specific baseline = the S1_F clean-run mean per output
    s1f_baseline = df[(df["scenario"] == "S1") & (df["sex"] == "F")].set_index("output")["mean_clean"]

    changed = 0
    for _, r in fem.iterrows():
        base_f = float(s1f_baseline[r["output"]])
        pct_f = abs(r["mean_clean"] - base_f) / abs(base_f) if base_f else float("nan")
        color_f = _color(pct_f, int(r["n_diverged"]), int(r["n_implausible"]), int(r["n_total"]))
        if color_f != r["light"]:
            changed += 1

    n = len(fem)
    print(f"Female cells re-scored against a sex-specific (S1_F) baseline: {changed} of {n} change colour.")
    assert changed == 0, f"Expected 0 colour changes, got {changed}"


if __name__ == "__main__":
    main()
