"""Generate the npj paper's Figure 2 (curation and review-priority map), the
version that ships as ``preprint_npj/figures/fig01_traffic_light.{pdf,png}``.

Panel (a). Each (scenario, sex, output) cell is coloured green / yellow / red by
the locked classification (``src/analysis_compare.reliability_classification``
-> ``results/reliability_classification.csv`` -> ``reliability_traffic_light.csv``)
and *annotated with the clean-run mean of that output* rather than the (redundant)
colour word. Formatting is fixed for clinical legibility:

    * integers everywhere (sub-integer precision has no clinical meaning here);
    * SpO2 shown as an integer percent (98, not 0.98);
    * output units carried in the column headers, so the cells hold bare numbers.

The colour is a combined class -- the diverged/implausible flag rate together
with the deviation from the healthy-male S1_M baseline -- and NOT a reliability
verdict; the number encodes the value. These are complementary axes, so a
clinically normal value can sit on a yellow or red cell, as stated in the caption.

Panel (b). A compact strip giving the same 48 classifications by the criterion
that produced them, because the colour alone cannot say which of the two fired.
The full per-cell driver matrix lives in the Supplement; only the totals fit
here, for the page-geometry reason recorded at the figure construction below.

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


def _driver(row: pd.Series) -> str:
    """Which criterion put this cell in its class.

    Re-derived here from the same columns the classifier uses, never from a
    stored label, so panel B cannot drift from panel A. The thresholds are
    CLASS-RELATIVE and deliberately asymmetric, exactly as in
    ``src/analysis_compare.reliability_classification``:

        red     deviation fires above 30 %, hard-flag rate above 30 %
        yellow  deviation fires above 10 %, hard-flag rate above 0
        green   neither, by definition

    "neither" therefore coincides with the green set by construction; it is
    drawn as an empty cell rather than a fourth colour, which is what it means.
    """
    rate = (row["n_diverged"] + row["n_implausible"]) / row["n_total"]
    pct = row["pct_off_baseline"]
    if row["light"] == "red":
        dev, flag = pct > 0.3, rate > 0.3
    elif row["light"] == "yellow":
        dev, flag = pct > 0.1, rate > 0.0
    else:
        return "neither"
    if dev and flag:
        return "both"
    return "dev_only" if dev else "flag_only"


# Categorical, not status: green/yellow/red belong to panel A and are never
# reused here. Hues are slots 1, 2 and 7 of the validated reference palette and
# clear every gate under the strict all-pairs rule (worst normal-vision dE 16.3,
# worst CVD dE 13.0 deutan). Each cell also carries a glyph, so the category
# survives greyscale printing and colour-vision deficiency without the colour.
DRIVER_COLOR = {"neither": "#ffffff", "flag_only": "#2a78d6",
                "dev_only": "#eb6834", "both": "#4a3aa7"}
DRIVER_GLYPH = {"neither": "", "flag_only": "F", "dev_only": "D", "both": "FD"}
DRIVER_ORDER = ["neither", "flag_only", "dev_only", "both"]


def main() -> None:
    df = pd.read_csv(SRC)
    df["cell"] = df["scenario"] + "_" + df["sex"]
    df["light_score"] = df["light"].map(COLOR_SCORE)
    df["annot"] = df.apply(_annotate, axis=1)
    df["driver"] = df.apply(_driver, axis=1)

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
    # Geometry is measurement-driven, not preference. A full second panel was
    # built first and rejected: at width=0.95\textwidth the two-panel figure
    # requested 353.4 x 365.6 pt and LaTeX reported "Float too large for page by
    # 134.28268pt", i.e. the usable float height here is about 231 pt, so the
    # aspect ratio must stay above roughly 1.53. Panel A at its original 7.2 x 4
    # is 1.80 and fits; shrinking it enough to seat a second 48-cell matrix would
    # have cost panel A its legibility. The driver decomposition therefore ships
    # as a compact strip here and in full in the Supplement.
    # 4.6 -> 4.2 after the caption grew to describe panel (b): the FLOAT is
    # figure plus caption, and at 4.6 the pair overflowed by 17.2 pt, which
    # showed up as caption text colliding with the page folio. Trimming 0.4 in
    # of figure was preferred to cutting caption content that carries claims.
    fig, (ax, axb) = plt.subplots(
        2, 1, figsize=(7.2, 4.2), gridspec_kw={"height_ratios": [8, 1]})

    # --- panel A: the composite curation map, unchanged ------------------
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
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=8)
    ax.set_title("(a)  Curation and review-priority map per cell × output", loc="left")
    ax.set_xlabel("")
    ax.set_ylabel("cell")

    # --- panel B: which criterion produced the 48 classifications --------
    counts = df["driver"].value_counts()
    left = 0.0
    for k in DRIVER_ORDER:
        n = int(counts.get(k, 0))
        if not n:
            continue
        axb.barh(0, n, left=left, height=0.55, color=DRIVER_COLOR[k],
                 edgecolor="0.35", linewidth=0.6)
        axb.text(left + n / 2, 0, f"{DRIVER_GLYPH[k] or '--'}\n{n}",
                 ha="center", va="center", fontsize=7.5, weight="bold",
                 color="0.15" if k == "neither" else "white")
        left += n
    axb.set_xlim(0, 48)
    axb.set_ylim(-0.55, 0.55)
    axb.set_yticks([])
    axb.set_xticks([])
    for side in ("top", "right", "left", "bottom"):
        axb.spines[side].set_visible(False)
    axb.grid(False)
    # Kept short on purpose: the caption carries the thresholds, the red-cell
    # split and the interpretive guard, so repeating them here in 7.5 pt only
    # made the strip harder to read at print size.
    axb.set_title(
        "(b)  Classification drivers over the 48 cells:  "
        "F hard flags only · D deviation only · FD both · -- neither (= green)",
        loc="left", fontsize=8)

    fig.tight_layout()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / "fig01_traffic_light.png", dpi=200, bbox_inches="tight")
    fig.savefig(OUT_DIR / "fig01_traffic_light.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {(OUT_DIR / 'fig01_traffic_light.pdf').relative_to(REPO)} (+ .png)")


if __name__ == "__main__":
    main()
