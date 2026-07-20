"""Generate the six npj Figure 2 panels: Morris mu* heatmaps per output channel.

Each panel is one of the six steady-state outputs (HR, MAP, Vt, SpO2, PaO2,
PaCO2). Rows of every panel are the seven swept inputs (HR, SBP, DBP, RR, Vt,
FiO2, PEEP); columns are the eight (scenario x sex) cells (S1_M, S1_F, ...,
S4_M, S4_F). The npj LaTeX preamble assembles the six panels into a 2x3
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

    fig, ax = plt.subplots(figsize=(5.2, 3.0))
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
    # No in-figure title -- the LaTeX subfigure caption already labels each panel
    # (HR, MAP, Vt, SpO2, PaO2, PaCO2). Skipping the title gives the heatmap area
    # the full panel for legibility once the 3x2 LaTeX grid scales the panel to
    # 0.48\textwidth.
    ax.set_xlabel(r"Cell (scenario $\times$ sex)", fontsize=10)
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
