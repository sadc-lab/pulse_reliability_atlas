"""Generate Supplement Figure S1: ARDS continuous-severity divergence
dumbbell plot with Wilson 95% confidence intervals.

Visualises the per-bin male vs female divergence rates from the
continuous-severity micro-sweep (200 runs total across 6 impairment-
fraction bins at midrange Morris inputs). Each impairment bin is a
single x-axis position with a male dot and a female dot connected by
a vertical line (dumbbell), emphasising the within-bin sex divergence
delta. Error bars are Wilson 95% binomial confidence intervals on the
divergence proportion.

Per-bin counts and the empirical instability-band edges are derived
DYNAMICALLY from the raw run directories under
data/runs/continuous_ards/ (see ``load_divergence`` / ``build_bins``)
rather than hardcoded, so the figure cannot silently go stale if the
underlying sweep is regenerated. Divergence is determined run-by-run
using the locked atlas definition: non-zero exit code, missing CSV, or
any non-finite value in the numeric output columns.

The matplotlib aesthetic is copied verbatim from the main-paper figure
scripts (figsize, palette, dpi=200, grid alpha, font sizes) per the
S028 visual-consistency guardrail.

Output: preprint_npj/figures/fig_s1_continuous_severity.pdf + .png
"""

from __future__ import annotations

import glob
import json
import math
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
CONT_DIR = REPO / "data" / "runs" / "continuous_ards"
OUT = REPO / "preprint_npj" / "figures" / "fig_s1_continuous_severity.pdf"

# Bin DEFINITIONS (half-open impairment-fraction intervals) are fixed; the
# per-bin sample sizes and divergence COUNTS are derived from raw data below.
BIN_EDGES = [
    ("[0, 0.5]",       0.25,   0.0,   0.5),
    ("(0.5, 0.85]",    0.675,  0.5,   0.85),
    ("(0.85, 0.91]",   0.880,  0.85,  0.91),
    ("(0.91, 0.945]",  0.9275, 0.91,  0.945),
    ("(0.945, 0.95]",  0.9475, 0.945, 0.95),
    ("(0.95, 1.0]",    0.975,  0.95,  1.0),
]


def wilson_ci(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score 95 percent CI for a binomial proportion.

    No external dependency. z=1.96 corresponds to the 95 percent two-sided
    interval. Matches statsmodels.stats.proportion.proportion_confint(
    successes, n, method='wilson') to within numerical precision.
    """
    if n == 0:
        return (0.0, 1.0)
    p = successes / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, centre - half), min(1.0, centre + half))


def load_divergence() -> pd.DataFrame:
    """Parse every continuous_ards run: (sex, impairment fraction, diverged).

    Severity is encoded in the directory name as ``...sevXXXX`` (XXXX / 1000).
    Divergence follows the locked atlas definition: exit code != 0, missing
    output.csv, or any non-finite numeric value in output.csv.
    """
    rows: list[tuple[str, float, bool]] = []
    for d in sorted(glob.glob(str(CONT_DIR / "CONT_*"))):
        parts = os.path.basename(d).split("_")
        sex = parts[1]
        sev = int(parts[3].replace("sev", "")) / 1000.0
        meta = json.loads((Path(d) / "run_meta.json").read_text())
        diverged = meta.get("exit_code", 1) != 0
        csv = Path(d) / "output.csv"
        if not diverged:
            if not csv.exists():
                diverged = True
            else:
                out = pd.read_csv(csv)
                num = out.select_dtypes(include=[np.number])
                diverged = (len(out) == 0) or (not np.isfinite(num.to_numpy()).all())
        rows.append((sex, sev, bool(diverged)))
    return pd.DataFrame(rows, columns=["sex", "sev", "diverged"])


def build_bins(df: pd.DataFrame) -> list[dict]:
    """Aggregate the per-run divergence frame into the fixed bins.

    The male and female sweeps share the same severity grid, so the per-sex
    sample size is identical within each bin; this is asserted so a future
    data change that breaks the assumption fails loudly rather than silently.
    """
    bins: list[dict] = []
    for label, mid, lo, hi in BIN_EDGES:
        mask = (df["sev"] >= lo) & (df["sev"] <= hi) if lo == 0.0 else (df["sev"] > lo) & (df["sev"] <= hi)
        f = df[mask & (df["sex"] == "F")]
        m = df[mask & (df["sex"] == "M")]
        assert len(f) == len(m), f"bin {label}: nF={len(f)} != nM={len(m)} (severity grid mismatch)"
        bins.append({
            "label": label,
            "mid": mid,
            "n": len(f),
            "m_div": int(m["diverged"].sum()),
            "f_div": int(f["diverged"].sum()),
        })
    return bins


_df = load_divergence()
BINS = build_bins(_df)
_dv = _df[_df["diverged"]]
_band_lo = float(_dv["sev"].min()) if len(_dv) else float("nan")
_band_hi = float(_dv["sev"].max()) if len(_dv) else float("nan")
print(f"continuous_ards: {len(_df)} runs; "
      f"F diverged = {int(_df[_df['sex'] == 'F']['diverged'].sum())}, "
      f"M diverged = {int(_df[_df['sex'] == 'M']['diverged'].sum())}")
print(f"empirical instability band (min/max diverged severity) = [{_band_lo:.3f}, {_band_hi:.3f}]")

fig, ax = plt.subplots(1, 1, figsize=(9.5, 5.0))

# Wilson 95% binomial CI on each proportion.
xs = [b["mid"] for b in BINS]
m_props = [b["m_div"] / b["n"] for b in BINS]
f_props = [b["f_div"] / b["n"] for b in BINS]
m_lo, m_hi = zip(*[wilson_ci(b["m_div"], b["n"]) for b in BINS])
f_lo, f_hi = zip(*[wilson_ci(b["f_div"], b["n"]) for b in BINS])

# Draw the dumbbell connecting lines first (so dots sit on top).
for x, m, f in zip(xs, m_props, f_props):
    ax.plot([x, x], [m, f], color="#999999", linewidth=1.2, alpha=0.5, zorder=1)

# Male and female dots with Wilson 95% CI error bars.
ax.errorbar(
    xs, m_props,
    yerr=[[m - lo for m, lo in zip(m_props, m_lo)],
          [hi - m for m, hi in zip(m_props, m_hi)]],
    fmt="o", markersize=10, color="#4C72B0",
    markeredgecolor="black", markeredgewidth=0.5,
    ecolor="#4C72B0", elinewidth=1.4, capsize=4, capthick=1.2,
    alpha=0.75, label="Male", zorder=3,
)
ax.errorbar(
    xs, f_props,
    yerr=[[f - lo for f, lo in zip(f_props, f_lo)],
          [hi - f for f, hi in zip(f_props, f_hi)]],
    fmt="o", markersize=10, color="#DD8452",
    markeredgecolor="black", markeredgewidth=0.5,
    ecolor="#DD8452", elinewidth=1.4, capsize=4, capthick=1.2,
    alpha=0.75, label="Female", zorder=3,
)

# Reference shading for the documented 0.91-0.945 instability zone (from
# the literature; the atlas extends the empirical band to [0.879, 0.945]).
ax.axvspan(0.91, 0.945, color="#C44E52", alpha=0.10, zorder=0,
           label="Documented 0.91--0.945 instability zone")

# Per-bin sample-size annotations under the x-axis.
for x, b in zip(xs, BINS):
    ax.annotate(
        f"n={b['n']}", xy=(x, -0.06), xycoords=("data", "axes fraction"),
        ha="center", va="top", fontsize=8, color="#666666",
    )

ax.set_xlim(0.15, 1.05)
ax.set_ylim(-0.05, 1.05)
ax.set_xlabel("ARDS impairment-fraction bin (continuous-severity micro-sweep)")
ax.set_ylabel("Divergence rate (Wilson 95\\% CI)")
ax.set_title(
    "Continuous-severity divergence regime: sex-stratified, midrange Morris inputs",
    fontsize=10,
)
ax.legend(loc="upper left", fontsize=9, frameon=True)
ax.grid(True, axis="y", alpha=0.25, linewidth=0.5)

fig.tight_layout()
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=200, bbox_inches="tight")
fig.savefig(OUT.with_suffix(".png"), dpi=200, bbox_inches="tight")
print(f"Wrote {OUT}")
print(f"Wrote {OUT.with_suffix('.png')}")
for b, m, f in zip(BINS, m_props, f_props):
    print(f"  bin {b['label']:<16} n={b['n']:>3}  M={b['m_div']}/{b['n']} ({m:.3f})  F={b['f_div']}/{b['n']} ({f:.3f})")
