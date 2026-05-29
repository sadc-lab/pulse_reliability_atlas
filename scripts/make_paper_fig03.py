"""Generate paper Figure 3 (two-panel actionable-corrections figure) for
the npj submission package.

Panel A: S014 trigger-lockout effect on VC-AC tidal-volume coefficient
         of variation. Each of the 64 paired runs is one dot; x-axis is
         the original Vt CV (default trigger configuration), y-axis is
         the Vt CV after locking inspiration trigger pressure to
         -2 cmH2O. The diagonal y = x marks "no effect"; the dashed
         horizontal at y = 0.05 marks the detector's steady-state
         threshold. Strong asymmetry below the diagonal visualises the
         intervention's effect.

Panel B: S021 hyperoxia 300-second convergence. Each of the 60 reruns
         is one dot; x-axis is the original 120-second mean PaO2, y-axis
         is the 300-second plateau PaO2. Diagonal y = x marks "no
         change". The horizontal at 600 mmHg marks the detector's
         locked upper bound; the horizontal at ~663 mmHg marks the
         alveolar-gas-equation prediction. Both axes are clamped to the
         physiological range [0, 760] mmHg to highlight the convergence
         structure; the 6 S1 numerical-runaway points (plateau up to
         ~1,408 mmHg) fall off-scale and are flagged by an in-plot
         annotation. The bulk of the S1 scatter sitting just below the
         AGE prediction confirms a transient hyperoxia regime rather
         than an oxygenation overshoot.

Output: preprint_npj/figures/fig03_actionable_corrections.pdf

Read-only with respect to monograph artefacts (this script reads
data/runs/s014_*/paired_comparison.parquet and
data/runs/s021_*/plateau_stats.parquet; it never modifies them).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "preprint_npj" / "figures" / "fig03_actionable_corrections.pdf"

s14 = pd.read_parquet(REPO / "data/runs/s014_trigger_lockout/paired_comparison.parquet")
s21 = pd.read_parquet(REPO / "data/runs/s021_hyperoxia_convergence/plateau_stats.parquet")

fig, (axA, axB) = plt.subplots(1, 2, figsize=(11.0, 5.0))

# ---- Panel A: S014 trigger-lockout effect on Vt CV
axA.scatter(s14["Vt_cv_orig"], s14["Vt_cv_lock"], s=28, alpha=0.75, edgecolor="black", linewidth=0.4, color="#4C72B0")
lim = max(s14["Vt_cv_orig"].max(), s14["Vt_cv_lock"].max()) * 1.05
axA.plot([0, lim], [0, lim], "k--", linewidth=0.8, alpha=0.4, label="$y = x$ (no effect)")
axA.axhline(0.05, color="#C44E52", linestyle=":", linewidth=1.0, alpha=0.8, label="$0.05$ steady-state threshold")
axA.set_xlim(0, lim)
axA.set_ylim(0, lim)
axA.set_xlabel(r"Original Vt CV (default trigger)")
axA.set_ylabel(r"Vt CV after $-2$ cmH$_2$O trigger")
axA.set_title(r"(a) Trigger-lockout effect on VC-AC Vt stability ($n = 64$ paired)", fontsize=10)
axA.legend(loc="upper left", fontsize=8, frameon=True)
axA.grid(True, alpha=0.25, linewidth=0.5)

# ---- Panel B: S021 hyperoxia 300s convergence
palette = {"S1": "#4C72B0", "S3": "#DD8452", "S4": "#C44E52"}
for sc in ("S1", "S3", "S4"):
    sub = s21[s21["scenario"] == sc]
    axB.scatter(
        sub["PaO2_mean_orig_120s"],
        sub["PaO2_plateau_mmHg"],
        s=28, alpha=0.75, edgecolor="black", linewidth=0.4,
        color=palette[sc], label=f"{sc} ($n = {len(sub)}$)",
    )
# Clamp panel-B axes to the physiological range to highlight the
# convergence structure; the S021 numerical-runaway points (plateau up
# to ~1,408 mmHg) fall off-scale above this cap and are flagged by the
# annotation below (Supplement S9).
PANEL_B_AXIS_HI = 760.0  # sea-level barometric pressure
lo, hi = 0.0, PANEL_B_AXIS_HI
offscale = s21[
    (s21["scenario"].isin(("S1", "S3", "S4"))) & (s21["PaO2_plateau_mmHg"] > PANEL_B_AXIS_HI)
]["PaO2_plateau_mmHg"]
axB.plot([lo, hi], [lo, hi], "k--", linewidth=0.8, alpha=0.4, label="$y = x$ (no change)")
axB.axhline(600, color="#8172B2", linestyle=":", linewidth=1.0, alpha=0.8, label="600 mmHg classifier bound")
axB.axhline(663, color="#937860", linestyle="-.", linewidth=1.0, alpha=0.8, label=r"$\approx$ 663 mmHg AGE prediction")
axB.set_xlim(lo, hi)
axB.set_ylim(lo, hi)
axB.annotate(
    f"{len(offscale)} S1 runaway points off-scale\n"
    f"(plateau {offscale.min():.0f}-{offscale.max():.0f} mmHg; numerical runaway)",
    xy=(0.97, 0.97), xycoords="axes fraction", ha="right", va="top",
    fontsize=8, color="#555555", style="italic",
)
axB.set_xlabel(r"Original 120-second mean PaO$_2$ (mmHg)")
axB.set_ylabel(r"300-second plateau PaO$_2$ (mmHg)")
axB.set_title(r"(b) Hyperoxia 300 s convergence ($n = 60$ reruns)", fontsize=10)
axB.legend(loc="lower right", fontsize=8, frameon=True)
axB.grid(True, alpha=0.25, linewidth=0.5)

fig.tight_layout()
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=200, bbox_inches="tight")
fig.savefig(OUT.with_suffix(".png"), dpi=200, bbox_inches="tight")
print(f"Wrote {OUT}")
print(f"Wrote {OUT.with_suffix('.png')}")
