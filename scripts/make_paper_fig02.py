"""Generate the six npj Figure 2 panels: Morris mu* heatmaps per output channel.

Each panel is one of the six steady-state outputs (HR, MAP, Vt, SpO2, PaO2,
PaCO2). Rows of every panel are the seven swept inputs (HR, SBP, DBP, RR, Vt,
FiO2, PEEP); columns are the eight (scenario x sex) cells (Healthy-M,
Healthy-F, ..., Severe-M, Severe-F; data codes S1_M ... S4_F). The npj LaTeX preamble assembles the six panels into a 2x3
subfigure grid in paper.tex Section 2.2.

Data source: results/morris_indices.parquet -- the canonical Morris
elementary-effects artifact produced by scripts/analyze_sweep.py from the
1,280-run sweep aggregated.parquet.

This script closes the previously-flagged reproducibility gap on the npj
Figure 2 panels: they used to ship as PDFs without an in-repo generator
(documented in preprint_npj/README_FIGURES.md MISSING_GENERATORS).

Usage::

    uv run python scripts/make_paper_fig02.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.patches import Rectangle


def smart_fmt(v: float) -> str:
    """Compact, space-efficient annotation for one mu* value.

    Hard constraint: every cell must fit in at most four digits (the SpO2
    panel is the only one where the value range pushes against this; the
    other five outputs are comfortably within budget). Notation policy:

      * |v| >= 10        -> integer ('55', '91')
      * 1 <= |v| < 10    -> one decimal ('5.2', '9.6')
      * 0.01 <= |v| < 1  -> two decimals ('0.27', '0.06')
      * 0.001 <= |v| < 0.01 -> three decimals ('0.005', '0.009'). If the
                                rounded display is the pure power '0.001'
                                we collapse to '10^-3' for consistency.
      * |v| < 0.001       -> compact LaTeX mathtext: '10^e' if the value is
                              essentially a pure power of ten, otherwise
                              'm*10^e' with a one-digit mantissa.
      * NaN              -> '' (blank cell; no clean Morris pair)

    Matplotlib renders plain text with the annot fontweight (we use 'bold',
    which thickens the decimal point so it stays visible at small sizes).
    Mathtext rendering is *not* affected by fontweight, so the '10^e' and
    'm*10^e' forms come out at regular (non-bold) weight automatically --
    that is desired (bold mathtext looks too heavy at this size).
    """
    if pd.isna(v):
        return ""
    if v == 0:
        return "0"
    av = abs(v)
    sign = "-" if v < 0 else ""

    if av >= 10:
        return f"{v:.0f}"
    if av >= 1:
        return f"{v:.1f}"
    if av >= 0.01:
        return f"{v:.2f}"

    # |v| < 0.01: compute exp/mantissa once, decide between mathtext (pure
    # power), 3-decimal plain (non-power in [0.001, 0.01)), or compact
    # mathtext mantissa form (non-power below 0.001).
    exp = int(np.floor(np.log10(av)))
    mantissa = av / (10.0 ** exp)
    if round(mantissa) >= 10:  # 9.97 -> 10 -> carry to next exp
        mantissa = 1.0
        exp += 1

    if 0.95 <= mantissa <= 1.05:
        return rf"${sign}10^{{{exp}}}$"

    if av >= 0.001:
        s = f"{v:.3f}"
        # Boundary case: 0.00149 rounds to '0.001' at 3dp -> same compact form.
        if s.lstrip("-") == "0.001":
            return rf"${sign}10^{{-3}}$"
        return s

    return rf"${sign}{mantissa:.0f}{{\cdot}}10^{{{exp}}}$"

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "results" / "morris_indices.parquet"
OUT_DIR = REPO / "preprint_npj" / "figures"

# Six panels, one per output channel.
OUTPUT_CHANNELS: tuple[str, ...] = ("HR", "MAP", "Vt", "SpO2", "PaO2", "PaCO2")

# Inputs in the canonical physiology presentation order used throughout the
# paper (Methods Section 4.3). The parquet stores keys in lowercase; we map to
# the display labels expected in the figure y-axis.
INPUT_ORDER_DISPLAY: tuple[tuple[str, str], ...] = (
    ("hr", "HR"),
    ("sbp", "SBP"),
    ("dbp", "DBP"),
    ("rr", "RR"),
    ("vt", "Vt"),
    ("fio2", r"FiO$_2$"),
    ("peep", "PEEP"),
)

# Cell column order: S1_M, S1_F, S2_M, S2_F, S3_M, S3_F, S4_M, S4_F.
CELL_ORDER: list[str] = [
    f"{sc}_{sx}" for sc in ("S1", "S2", "S3", "S4") for sx in ("M", "F")
]
# Scenario labels shown to the reader (M. Sauthier review round, 2026-10-06).
# The data keep the codes S1-S4; Table 1 of the paper gives the correspondence.
# "Moderate-M" is too wide for one column at this panel width, so the axis is
# labelled on two levels: M / F under each column, the scenario under each pair.
SCENARIO_LABEL: dict[str, str] = {"S1": "Healthy", "S2": "Mild", "S3": "Moderate", "S4": "Severe"}

# Output channel display labels (LaTeX-aware for the subscripts).
OUTPUT_LABEL: dict[str, str] = {
    "HR": "HR",
    "MAP": "MAP",
    "Vt": "Vt",
    "SpO2": r"SpO$_2$",
    "PaO2": r"PaO$_2$",
    "PaCO2": r"PaCO$_2$",
}


def make_panel(df: pd.DataFrame, channel: str) -> None:
    """Render one Morris mu* heatmap for a single output channel.

    Rows = seven inputs (canonical order). Columns = eight cells. NaN cells
    (no clean elementary-effect pairs in that cell-input combination) are
    rendered as blank by seaborn's default mask-friendly behaviour.
    """
    sub = df[df["output"] == channel].copy()
    if sub.empty:
        print(f"  WARN: no rows for output={channel}; skipping panel")
        return
    sub["cell"] = sub["scenario"] + "_" + sub["sex"]
    pivot = sub.pivot_table(
        index="input", columns="cell", values="mu_star", aggfunc="first"
    )
    input_keys = [k for k, _ in INPUT_ORDER_DISPLAY]
    pivot = pivot.reindex(index=input_keys, columns=CELL_ORDER)
    # Replace lowercase input keys with display labels.
    pivot.index = [label for _, label in INPUT_ORDER_DISPLAY]

    # Per-cell annotation strings, computed with the smart formatter so big
    # numbers go to integer, mid-range to 1-2 decimals, and very small values
    # to compact LaTeX scientific (never matplotlib's 'E+0X' style).
    annot_strs = pivot.map(smart_fmt)

    # Which cells rest on a SINGLE elementary-effect pair. Their mu* is one
    # finite difference: sigma is 0 by construction rather than by measurement
    # and no bootstrap interval exists, yet nothing in the heatmap told them
    # apart from an index averaged over eighteen pairs. Twelve of the 318
    # entries qualify, and they fall in exactly two (cell, input) positions.
    pairs = (
        sub.pivot_table(index="input", columns="cell", values="n_clean_pairs", aggfunc="first")
        .reindex(index=input_keys, columns=CELL_ORDER)
    )

    # Width 6.6 in, height 2.8 in. The HEIGHT is the constrained dimension and
    # must not change: 5b3b54b cut it from 3.0 to 2.8 because the caption's last
    # line collided with the sn-jnl page number, and 82a652b left the float
    # 2.50 pt overfull inside a 5 pt tolerance. Widening only trades the 25 % of
    # \textwidth that the old 0.375 layout wasted in the inter-column gutter for
    # panel area, at constant rendered height: 0.375 x (192.5/361) = 0.480 x
    # (192.5/462). Change the width and paper.tex's subfigure fraction together
    # or the figure will grow vertically and the float will be deferred.
    fig, ax = plt.subplots(figsize=(6.6, 2.8))
    sns.heatmap(
        pivot,
        annot=annot_strs,
        fmt="",
        cmap="viridis",
        cbar_kws={"label": r"$\mu^{*}$"},
        annot_kws={"size": 9, "weight": "bold"},
        linewidths=0.3,
        linecolor="white",
        ax=ax,
    )
    # Box the single-pair cells. The edge colour is READ BACK from the cell's
    # own annotation, which seaborn already picks light or dark from the
    # background luminance, so the box carries exactly the contrast the number
    # carries -- legible on dark violet and on bright yellow alike, and it
    # survives greyscale for the same reason the digits do. Texts are matched
    # by POSITION, never by their order in ax.texts, because NaN cells make
    # that order depend on how seaborn skips them.
    text_colour = {
        (int(round(t.get_position()[0] - 0.5)), int(round(t.get_position()[1] - 0.5))): t.get_color()
        for t in ax.texts
    }
    for row, input_label in enumerate(pivot.index):
        for col, cell_label in enumerate(pivot.columns):
            n = pairs.iat[row, col]
            if pd.isna(n) or n > 1:
                continue
            ax.add_patch(
                Rectangle(
                    (col, row),
                    1,
                    1,
                    fill=False,
                    edgecolor=text_colour.get((col, row), "white"),
                    linewidth=1.4,
                    zorder=5,
                )
            )

    # No in-figure title -- the LaTeX subfigure caption already labels each panel
    # (HR, MAP, Vt, SpO2, PaO2, PaCO2). Skipping the title gives the heatmap area
    # the full panel for legibility once the 3x2 LaTeX grid scales the panel to
    # 0.48\textwidth.
    # Two-level x axis: the sex under each column, the scenario under each pair.
    # The scenario row takes the place of the former "Cell (scenario x sex)"
    # axis label, so the panel height does not grow.
    ax.set_xticks([i + 0.5 for i in range(len(CELL_ORDER))])
    ax.set_xticklabels([cell.split("_")[1] for cell in CELL_ORDER], rotation=0)
    scenario_axis = ax.secondary_xaxis("bottom")
    scenario_axis.set_xticks([2 * i + 1 for i in range(len(SCENARIO_LABEL))])
    scenario_axis.set_xticklabels(list(SCENARIO_LABEL.values()))
    scenario_axis.tick_params(axis="x", length=0, pad=19, labelsize=10)
    scenario_axis.spines["bottom"].set_visible(False)
    ax.set_xlabel("")
    ax.set_ylabel("Input", fontsize=10)
    ax.tick_params(axis="x", labelsize=10)
    # Smaller y-tick font so the stacked input labels (notably FiO2 and PEEP,
    # which otherwise collide because of the FiO2 subscript) stay legible.
    ax.tick_params(axis="y", labelsize=8)
    fig.tight_layout()

    pdf_path = OUT_DIR / f"fig02_morris_{channel}.pdf"
    png_path = OUT_DIR / f"fig02_morris_{channel}.png"
    fig.savefig(pdf_path, dpi=200, bbox_inches="tight")
    fig.savefig(png_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {pdf_path.name} + {png_path.name}")


def main() -> None:
    df = pd.read_parquet(SRC)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Reading {SRC.relative_to(REPO)} ({len(df)} rows)")
    for ch in OUTPUT_CHANNELS:
        make_panel(df, ch)


if __name__ == "__main__":
    main()
