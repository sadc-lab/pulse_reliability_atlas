"""Generate paper Figure 4 (sex-stratified divergence + BV-rescue
dose-response) for the npj submission package.

Panel A: per-cell divergence counts across the 1,280-run sweep,
         coloured by sex. Reads results/cell_flag_summary.csv directly
         to surface the 20/20 male-only divergence pattern.

Panel B: BV-rescue dose-response on the 20 originally-diverged male
         inputs. X-axis is the imposed BloodVolumeBaseline override
         (default 4802.63 -> bracket 4400 -> floor 4082.24 mL); y-axis
         is the divergence count out of 20. Reads
         data/runs/s018_blood_volume/{s018_classified.parquet,
         s018_floor_classified.parquet} for the dose-response counts.
         A dashed vertical at 3996.09 mL marks the female-equivalent
         BV that Pulse's allometric formula computes -- visible as
         falling 86 mL below the male floor, so a one-way BV transplant
         cannot make the two surrogates BV-equivalent.

Output: preprint_npj/figures/fig04_sex_bv_mechanism.pdf

Read-only with respect to monograph artefacts.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "preprint_npj" / "figures" / "fig04_sex_bv_mechanism.pdf"

cfs = pd.read_csv(REPO / "results/cell_flag_summary.csv")
s18_b = pd.read_parquet(REPO / "data/runs/s018_blood_volume/s018_classified.parquet")
s18_f = pd.read_parquet(REPO / "data/runs/s018_blood_volume/s018_floor_classified.parquet")

# Pulse-computed BV values verified against engine setup logs.
MALE_DEFAULT_BV_ML = 4802.63
MALE_FLOOR_BV_ML = 4082.24
BRACKET_BV_ML = 4400.0
FEMALE_DEFAULT_BV_ML = 3996.09

fig, (axA, axB) = plt.subplots(1, 2, figsize=(11.0, 5.0))

# ---- Panel A: per-cell divergence counts, M vs F
scenarios = ["S1", "S2", "S3", "S4"]
male_counts = [int(cfs[(cfs["scenario"] == sc) & (cfs["sex"] == "M")]["n_diverged"].iloc[0]) for sc in scenarios]
female_counts = [int(cfs[(cfs["scenario"] == sc) & (cfs["sex"] == "F")]["n_diverged"].iloc[0]) for sc in scenarios]

x = list(range(len(scenarios)))
width = 0.38
axA.bar([xi - width/2 for xi in x], male_counts, width, color="#4C72B0", edgecolor="black", linewidth=0.5, label="Male")
axA.bar([xi + width/2 for xi in x], female_counts, width, color="#DD8452", edgecolor="black", linewidth=0.5, label="Female")
for xi, mc in zip(x, male_counts):
    axA.text(xi - width/2, mc + 0.15, f"{mc}", ha="center", va="bottom", fontsize=9)
for xi, fc in zip(x, female_counts):
    axA.text(xi + width/2, fc + 0.15, f"{fc}", ha="center", va="bottom", fontsize=9, color="#666")
axA.set_xticks(x)
axA.set_xticklabels([f"{sc}\n(healthy)" if sc == "S1" else (f"{sc}\n(mild ARDS)" if sc == "S2" else (f"{sc}\n(moderate ARDS)" if sc == "S3" else f"{sc}\n(severe ARDS)")) for sc in scenarios])
axA.set_ylabel("Divergence count (out of 160 runs per cell)")
axA.set_title(r"(a) Per-cell solver divergence ($n = 1{,}280$, 160 per cell)", fontsize=10)
axA.set_ylim(0, max(male_counts) * 1.25 + 0.5)
axA.legend(loc="upper left", fontsize=9, frameon=True)
axA.grid(True, axis="y", alpha=0.25, linewidth=0.5)

# ---- Panel B: BV-rescue dose-response on the 20 originally-diverged male inputs
bracket_diverged = int(s18_b[s18_b["bv_label"] == "bracket"]["diverged"].sum())
floor_diverged = int(s18_f["diverged"].sum())

dose_bv = [MALE_DEFAULT_BV_ML, BRACKET_BV_ML, MALE_FLOOR_BV_ML]
dose_div = [20, bracket_diverged, floor_diverged]
dose_labels = [
    f"Default\n{MALE_DEFAULT_BV_ML:,.2f} mL",
    f"Bracket\n{BRACKET_BV_ML:,.0f} mL",
    f"Floor\n{MALE_FLOOR_BV_ML:,.2f} mL",
]

axB.plot(dose_bv, dose_div, marker="o", linewidth=2.0, markersize=10, color="#C44E52", markeredgecolor="black", markeredgewidth=0.6)
for bv, div in zip(dose_bv, dose_div):
    axB.text(bv, div + 0.8, f"{div} / 20", ha="center", va="bottom", fontsize=9, fontweight="bold")
axB.axvline(FEMALE_DEFAULT_BV_ML, color="#DD8452", linestyle="--", linewidth=1.2, alpha=0.85, label=f"Female default ({FEMALE_DEFAULT_BV_ML:,.2f} mL)")
axB.axvline(MALE_FLOOR_BV_ML, color="#937860", linestyle=":", linewidth=1.0, alpha=0.6, label="Pulse setup floor (male)")
axB.set_xlim(3850, 4900)
axB.set_ylim(-1, 22)
axB.set_xlabel(r"Imposed \texttt{BloodVolumeBaseline} override (mL)".replace(r"\texttt{", "").replace("}", ""))
axB.set_ylabel("Divergence count (out of 20 reruns)")
axB.set_title(r"(b) Blood-volume rescue ($n = 20$ originally-diverged male inputs)", fontsize=10)
axB.set_xticks(dose_bv)
axB.set_xticklabels(dose_labels, fontsize=8)
axB.legend(loc="upper left", fontsize=8, frameon=True)
axB.grid(True, alpha=0.25, linewidth=0.5)

fig.tight_layout()
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=200, bbox_inches="tight")
fig.savefig(OUT.with_suffix(".png"), dpi=200, bbox_inches="tight")
print(f"Wrote {OUT}")
print(f"Wrote {OUT.with_suffix('.png')}")
print(f"Per-cell divergence: M={male_counts}, F={female_counts}")
print(f"BV-rescue: default=20/20, bracket={bracket_diverged}/20, floor={floor_diverged}/20")
