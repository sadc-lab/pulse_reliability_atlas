"""Generate the preprint figures from the analysis artifacts.

Reads everything in `results/` and writes PNG + PDF (and underlying CSV
where useful) into `figures/`. Each figure has a docstring above its
function with the paper figure number it maps to.

Usage::

    uv run python scripts/make_figures.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.aggregator import STAT_CHANNELS  # noqa: E402
from src.sampler import INPUT_NAMES  # noqa: E402

RESULTS_DIR = REPO_ROOT / "results"
FIG_DIR = REPO_ROOT / "figures"
sns.set_context("paper")
sns.set_style("whitegrid")
# seaborn puts Arial at the head of font.sans-serif. npj asks for one sans-serif
# typeface across all figures in a paper, and the rest of ours are DejaVu Sans,
# so pin it back after seaborn has had its say. Font only.
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]


def _save(fig: plt.Figure, stem: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_DIR / f"{stem}.png", dpi=200, bbox_inches="tight")
    fig.savefig(FIG_DIR / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)


def fig_flag_summary() -> None:
    """Figure 1 — stacked bar: per-cell n_total broken down by flag."""
    df = pd.read_csv(RESULTS_DIR / "cell_flag_summary.csv")
    df["cell"] = df["scenario"] + "_" + df["sex"]

    cats = ["n_clean", "n_clamped", "n_diverged", "n_implausible", "n_not_steady_state"]
    palette = {
        "n_clean": "#4c9a4c",
        "n_clamped": "#d97706",
        "n_diverged": "#dc2626",
        "n_implausible": "#7c3aed",
        "n_not_steady_state": "#0891b2",
    }

    fig, ax = plt.subplots(figsize=(9, 4))
    bottoms = np.zeros(len(df))
    for cat in cats:
        ax.bar(df["cell"], df[cat], bottom=bottoms, color=palette[cat], label=cat[2:])
        bottoms += df[cat].values
    ax.set_ylabel("Number of runs")
    ax.set_xlabel("Cell (scenario × sex)")
    ax.set_title("Per-cell flag breakdown across the full Morris sweep")
    ax.legend(loc="upper right", fontsize=8, ncol=3)
    _save(fig, "fig01_flag_summary")


def fig_morris_mu_star() -> None:
    """Figure 2 — mu_star heatmap per output × input, faceted by scenario, sex on y."""
    morris = pd.read_parquet(RESULTS_DIR / "morris_indices.parquet")
    if morris.empty:
        return

    for ch in STAT_CHANNELS:
        sub = morris[morris["output"] == ch]
        if sub.empty:
            continue
        pivot = (
            sub.assign(cell=lambda d: d["scenario"] + "_" + d["sex"])
            .pivot(index="cell", columns="input", values="mu_star")
            .reindex(columns=list(INPUT_NAMES))
        )
        if pivot.empty or pivot.isna().all().all():
            continue
        fig, ax = plt.subplots(figsize=(7, 4))
        sns.heatmap(
            pivot,
            annot=True,
            fmt=".2g",
            cmap="viridis",
            cbar_kws={"label": "μ*"},
            ax=ax,
        )
        ax.set_title(f"Morris μ* for output {ch} — clean runs only")
        ax.set_xlabel("Input")
        ax.set_ylabel("Cell")
        _save(fig, f"fig02_morris_mu_star_{ch}")


def fig_h1_evaluation() -> None:
    """Figure 3 — H1 stacked: top-3 fraction of summed mu_star per cell × output."""
    h1 = pd.read_csv(RESULTS_DIR / "h1_top3_fraction.csv")
    h1["cell"] = h1["scenario"] + "_" + h1["sex"]

    fig, ax = plt.subplots(figsize=(9, 4))
    pivot = h1.pivot(index="cell", columns="output", values="top3_fraction")
    sns.heatmap(
        pivot.reindex(columns=list(STAT_CHANNELS)),
        annot=True,
        fmt=".2f",
        vmin=0,
        vmax=1,
        cmap="RdYlGn",
        cbar_kws={"label": "top-3 μ* / total μ*"},
        ax=ax,
    )
    ax.set_title("H1 — fraction of mu_star explained by top-3 inputs (>=0.5 = pass)")
    _save(fig, "fig03_h1_top3_fraction")


def fig_h4_wasserstein() -> None:
    """Figure 4 — Wasserstein male-vs-female per scenario × output."""
    df = pd.read_csv(RESULTS_DIR / "wasserstein_male_vs_female.csv")
    if df.empty:
        return
    fig, ax = plt.subplots(figsize=(7, 4))
    pivot = df.pivot(index="scenario", columns="output", values="wasserstein").reindex(
        columns=list(STAT_CHANNELS)
    )
    sns.heatmap(pivot, annot=True, fmt=".2f", cmap="rocket_r", ax=ax)
    ax.set_title("H4 — Wasserstein distance (M vs F clean-run distributions)")
    _save(fig, "fig04_h4_wasserstein")


def fig_h4_spearman() -> None:
    """Figure 5 — Spearman ρ on Morris mu_star vectors M-vs-F."""
    df = pd.read_csv(RESULTS_DIR / "spearman_mu_star.csv")
    if df.empty:
        return
    fig, ax = plt.subplots(figsize=(7, 4))
    pivot = df.pivot(index="scenario", columns="output", values="spearman_rho").reindex(
        columns=list(STAT_CHANNELS)
    )
    sns.heatmap(
        pivot,
        annot=True,
        fmt=".2f",
        vmin=-1,
        vmax=1,
        cmap="RdBu",
        cbar_kws={"label": "Spearman ρ"},
        ax=ax,
    )
    ax.set_title("H4 — Spearman ρ between M and F μ* rankings (1 = same ranking)")
    _save(fig, "fig05_h4_spearman_mu_star")


def fig_reliability_traffic_light() -> None:
    """Figure 6 — green/yellow/red reliability per cell × output."""
    df = pd.read_csv(RESULTS_DIR / "reliability_classification.csv")
    if df.empty:
        return
    df["cell"] = df["scenario"] + "_" + df["sex"]
    color_map = {"green": 2, "yellow": 1, "red": 0}
    df["light_score"] = df["light"].map(color_map)
    pivot = df.pivot(index="cell", columns="output", values="light_score").reindex(
        columns=list(STAT_CHANNELS)
    )
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.heatmap(
        pivot,
        annot=df.pivot(index="cell", columns="output", values="light").reindex(
            columns=list(STAT_CHANNELS)
        ),
        fmt="",
        cmap="RdYlGn",
        vmin=0,
        vmax=2,
        cbar=False,
        ax=ax,
    )
    ax.set_title("Reliability traffic-light per cell × output")
    _save(fig, "fig06_reliability_traffic_light")


def main() -> int:
    if not RESULTS_DIR.exists():
        print(f"[figures] no results dir at {RESULTS_DIR}")
        return 1
    fig_flag_summary()
    fig_morris_mu_star()
    fig_h1_evaluation()
    fig_h4_wasserstein()
    fig_h4_spearman()
    fig_reliability_traffic_light()
    print(f"[figures] all figures in {FIG_DIR.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
