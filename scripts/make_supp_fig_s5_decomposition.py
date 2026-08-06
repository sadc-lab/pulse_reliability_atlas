"""Supplement figure: the three descriptive views the composite map compresses.

Figure 2 of the main paper gives one colour per (scenario, sex, output) cell,
produced by two criteria at once. That is useful as a conservative curation
filter and useless as a diagnosis, because the colour cannot say which criterion
fired. This figure separates the ingredients and adds the per-cell driver matrix
that did not fit in the main figure's float budget.

    (a) hard-failure rate per cell -- diverged + implausible over 160. These
        flags are run-level, so there are eight values, not forty-eight; they
        are NOT duplicated across outputs to fill a grid.
    (b) not_steady_state triggers per output, exhaustive and multi-label. A
        channel may satisfy more than one trigger, so the bars are
        non-mutually-exclusive and their total exceeds the number of flagged
        runs. The paler inner bar is what the detector actually RECORDED, which
        stops at the first trigger per channel and therefore undercounts
        co-occurring mechanisms -- on Vt, 3 recorded against 133 real.
    (c) signed deviation of each clean-run mean from the healthy-male (S1, M)
        baseline. Signed, not absolute: the sign is the whole point, because it
        shows HR rising and PaO2 falling with severity, which is the expected
        direction under ARDS.
    (d) which criterion produced each of the 48 classifications.

Read (c) as descriptive only. A directionally expected change does not validate
its magnitude, and nothing here is an external physiological validation.

The trigger attribution is imported from scripts/calibrate_nss_attribution.py
rather than recomputed, so this figure cannot drift from the calibration that
licensed it (that script reproduces the stored not_steady_state flag on
1,280 of 1,280 runs).

Usage::

    uv run python scripts/make_supp_fig_s5_decomposition.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.calibrate_nss_attribution import (  # noqa: E402
    AGG,
    CHANNELS,
    attribution,
)

TL = REPO / "results" / "reliability_traffic_light.csv"
OUT_DIR = REPO / "preprint_npj" / "figures"

CELLS = ["S1_M", "S1_F", "S2_M", "S2_F", "S3_M", "S3_F", "S4_M", "S4_F"]
COL_LABELS = ["HR", "MAP", "Vt", "SpO$_2$", "PaO$_2$", "PaCO$_2$"]

# Same validated trio as the main figure's driver strip (reference palette slots
# 1, 2 and 7): worst normal-vision dE 16.3, worst CVD dE 13.0 deutan under the
# strict all-pairs rule. Green / yellow / red stay reserved for the composite
# map and are never reused here.
BLUE, ORANGE, VIOLET = "#2a78d6", "#eb6834", "#4a3aa7"
TRIGGERS = [("flatline", BLUE), ("cv", ORANGE), ("drift", VIOLET)]
DRIVER_COLOR = {"neither": "#ffffff", "flag_only": BLUE,
                "dev_only": ORANGE, "both": VIOLET}
DRIVER_GLYPH = {"neither": "", "flag_only": "F", "dev_only": "D", "both": "FD"}
DRIVER_ORDER = ["neither", "flag_only", "dev_only", "both"]


def _driver(row: pd.Series) -> str:
    """Class-relative driver, identical rule to scripts/make_paper_fig01.py."""
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


def main() -> None:
    tl = pd.read_csv(TL)
    tl["cell"] = tl["scenario"] + "_" + tl["sex"]
    tl["driver"] = tl.apply(_driver, axis=1)
    # Signed, not the stored absolute pct_off_baseline.
    tl["signed"] = (tl["clean_mean"] - tl["baseline_s1m"]) / tl["baseline_s1m"]

    per_cell = (tl.groupby("cell")[["n_diverged", "n_implausible", "n_total"]]
                .first().reindex(CELLS))
    hard_pct = 100.0 * (per_cell["n_diverged"] + per_cell["n_implausible"]) / per_cell["n_total"]

    exhaustive, first_cause, _skipped, _recon = attribution(pd.read_parquet(AGG))

    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
    # Height is measurement-driven. At 7.2 x 6.4 and width=0.95\textwidth LaTeX
    # reported "Float too large for page by 50.3889pt", so the usable float
    # height here is about 264 pt at 353 pt wide -- an aspect ratio above roughly
    # 1.34. 7.2 x 5.2 is 1.38 and fits.
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.2))
    (ax_a, ax_b), (ax_c, ax_d) = axes

    # --- (a) hard-failure rate per cell ------------------------------------
    ax_a.bar(range(len(CELLS)), hard_pct.to_numpy(), color=BLUE,
             edgecolor="0.3", linewidth=0.5, width=0.7)
    ax_a.axhline(30, color="0.35", linestyle="--", linewidth=0.9)
    ax_a.text(-0.4, 30.6, "30 % red threshold", ha="left",
              va="bottom", fontsize=6.5, color="0.3")
    ax_a.set_xticks(range(len(CELLS)))
    ax_a.set_xticklabels(CELLS, rotation=45, ha="right", fontsize=7)
    ax_a.set_ylabel("hard-failure rate (%)", fontsize=8)
    ax_a.set_title("(a)  Hard failures per cell (diverged + implausible),\n"
                   "run-level, 160 runs per cell", loc="left", fontsize=8)
    ax_a.tick_params(labelsize=7)
    ax_a.grid(axis="y", linewidth=0.4, alpha=0.4)
    ax_a.set_axisbelow(True)

    # --- (b) not_steady_state triggers per output --------------------------
    x = np.arange(len(CHANNELS))
    w = 0.26
    for j, (trig, colour) in enumerate(TRIGGERS):
        ex = [exhaustive[ch][trig] for ch in CHANNELS]
        fc = [first_cause[ch][trig] for ch in CHANNELS]
        pos = x + (j - 1) * w
        ax_b.bar(pos, ex, width=w, color=colour, edgecolor="0.3",
                 linewidth=0.5, label=f"{trig} (exhaustive)")
        ax_b.bar(pos, fc, width=w * 0.45, color="white", alpha=0.55,
                 edgecolor="0.3", linewidth=0.4,
                 label="as recorded by the detector" if j == 0 else None)
    ax_b.set_xticks(x)
    ax_b.set_xticklabels(COL_LABELS, fontsize=7)
    ax_b.set_ylabel("channel occurrences", fontsize=8)
    ax_b.set_title("(b)  not_steady_state triggers per output;\n"
                   "non-exclusive, so the total exceeds the flagged runs",
                   loc="left", fontsize=8)
    ax_b.tick_params(labelsize=7)
    ax_b.legend(fontsize=6, frameon=False, loc="upper left")
    ax_b.grid(axis="y", linewidth=0.4, alpha=0.4)
    ax_b.set_axisbelow(True)

    # --- (c) signed deviation from the (S1, M) baseline --------------------
    signed = (tl.pivot(index="cell", columns="output", values="signed")
              .reindex(index=CELLS, columns=["HR", "MAP", "Vt", "SpO2", "PaO2", "PaCO2"]))
    lim = float(np.nanmax(np.abs(signed.to_numpy())))
    im = ax_c.imshow(signed.to_numpy() * 100, cmap="PuOr_r",
                     vmin=-lim * 100, vmax=lim * 100, aspect="auto")
    ax_c.set_xticks(range(6))
    ax_c.set_xticklabels(COL_LABELS, fontsize=7)
    ax_c.set_yticks(range(len(CELLS)))
    ax_c.set_yticklabels(CELLS, fontsize=7)
    ax_c.set_title("(c)  Signed deviation from the healthy-male (S1, M)\n"
                   "baseline (%); descriptive, not a validation",
                   loc="left", fontsize=8)
    cb = fig.colorbar(im, ax=ax_c, fraction=0.046, pad=0.03)
    cb.ax.tick_params(labelsize=6)

    # --- (d) classification drivers, all 48 cells --------------------------
    drv = (tl.pivot(index="cell", columns="output", values="driver")
           .reindex(index=CELLS, columns=["HR", "MAP", "Vt", "SpO2", "PaO2", "PaCO2"]))
    codes = drv.replace({k: i for i, k in enumerate(DRIVER_ORDER)}).astype(float)
    ax_d.imshow(codes.to_numpy(), cmap=ListedColormap([DRIVER_COLOR[k] for k in DRIVER_ORDER]),
                vmin=-0.5, vmax=len(DRIVER_ORDER) - 0.5, aspect="auto")
    for i in range(len(CELLS)):
        for j in range(6):
            g = DRIVER_GLYPH[drv.to_numpy()[i, j]]
            if g:
                ax_d.text(j, i, g, ha="center", va="center", fontsize=6.5,
                          weight="bold", color="white")
    ax_d.set_xticks(range(6))
    ax_d.set_xticklabels(COL_LABELS, fontsize=7)
    ax_d.set_yticks(range(len(CELLS)))
    ax_d.set_yticklabels(CELLS, fontsize=7)
    counts = tl["driver"].value_counts()
    ax_d.set_title(
        "(d)  Classification drivers:  F hard flags only (n = %d) · "
        "D deviation only (n = %d)\nFD both (n = %d) · blank neither, "
        "which is the green set (n = %d)"
        % (int(counts.get("flag_only", 0)), int(counts.get("dev_only", 0)),
           int(counts.get("both", 0)), int(counts.get("neither", 0))),
        loc="left", fontsize=8)

    fig.tight_layout()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / "fig_s5_decomposition.png", dpi=200, bbox_inches="tight")
    fig.savefig(OUT_DIR / "fig_s5_decomposition.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {(OUT_DIR / 'fig_s5_decomposition.pdf').relative_to(REPO)} (+ .png)")


if __name__ == "__main__":
    main()
