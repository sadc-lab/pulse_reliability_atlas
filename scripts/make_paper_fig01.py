"""Generate the npj paper's Figure 2 (reliability traffic-light), the version
that ships as ``preprint_npj/figures/fig01_traffic_light.{pdf,png}``.

Each (scenario, sex, output) cell is coloured green / yellow / red by the
locked reliability verdict (``src/analysis_compare.reliability_classification``
-> ``results/reliability_classification.csv`` -> ``reliability_traffic_light.csv``)
and *annotated with the clean-run mean of that output* rather than the (redundant)
colour word. Formatting is fixed for clinical legibility:

    * integers everywhere (sub-integer precision has no clinical meaning here);
    * SpO2 shown as an integer percent (98, not 0.98);
    * output units carried in the column headers, so the cells hold bare numbers.

The colour still encodes the reliability verdict (diverged/implausible flag rate
plus deviation from the healthy-male S1_M baseline); the number encodes the value.
These are complementary axes -- a clinically normal value can sit on a yellow or
red cell -- as stated in the figure caption.

Usage::

    uv run python scripts/make_paper_fig01.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "results" / "reliability_traffic_light.csv"
OUT_DIR = REPO / "preprint_npj" / "figures"

OUTPUTS = ["HR", "MAP", "Vt", "SpO2", "PaO2", "PaCO2"]
COL_LABELS = ["HR (bpm)", "MAP (mmHg)", "Vt (mL)", "SpO2 (%)", "PaO2 (mmHg)", "PaCO2 (mmHg)"]
COLOR_SCORE = {"green": 2, "yellow": 1, "red": 0}


def _annotate(row: pd.Series) -> str:
    """Clean-run mean as an integer; SpO2 as an integer percent."""
    v = row["clean_mean"]
    return f"{round(v * 100)}" if row["output"] == "SpO2" else f"{round(v)}"


def main() -> None:
    df = pd.read_csv(SRC)
    df["cell"] = df["scenario"] + "_" + df["sex"]
    df["light_score"] = df["light"].map(COLOR_SCORE)
    df["annot"] = df.apply(_annotate, axis=1)

    score = df.pivot(index="cell", columns="output", values="light_score").reindex(columns=OUTPUTS)
    annot = df.pivot(index="cell", columns="output", values="annot").reindex(columns=OUTPUTS)

    sns.set_context("paper")
    sns.set_style("whitegrid")
    # seaborn puts Arial at the head of font.sans-serif, which made this the only
    # figure in the paper not set in DejaVu Sans. npj asks for one typeface across
    # all figures, so pin it back after seaborn has had its say. Font only --
    # nothing else about the figure changes.
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
    fig, ax = plt.subplots(figsize=(7.2, 4))
    sns.heatmap(
        score,
        annot=annot,
        fmt="",
        cmap="RdYlGn",
        vmin=0,
        vmax=2,
        cbar=False,
        annot_kws={"fontsize": 11},
        linewidths=0.5,
        linecolor="white",
        ax=ax,
    )
    ax.set_xticklabels(COL_LABELS, rotation=0, fontsize=8)
    ax.set_title("Reliability traffic-light per cell × output")
    ax.set_xlabel("output")
    ax.set_ylabel("cell")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / "fig01_traffic_light.png", dpi=200, bbox_inches="tight")
    fig.savefig(OUT_DIR / "fig01_traffic_light.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {(OUT_DIR / 'fig01_traffic_light.pdf').relative_to(REPO)} (+ .png)")


if __name__ == "__main__":
    main()
