"""Generate Supplement Figure S3: PaO2 late-phase convergence trajectories
from the S021 hyperoxia 300-second rerun cohort.

IMPORTANT framing (per maintainer-audited Phase 9.C decision):
t=0 on the plot corresponds to t=120s of the overall simulation timeline.
The S021 reruns continue from the saved Pulse state at the end of the
original locked 120-second window (where PaO2 was already in the
hyperoxia regime) out to t=300s of overall simulation time. The figure
therefore visualises the LATE-PHASE CONVERGENCE of PaO2 toward its true
plateau, not a fresh wash-in from atmospheric-air baseline.

Visualises the 44 S1 (healthy) S021 reruns as overlapping thin
trajectories, with the converged-subset median highlighted as a thick
line. Horizontal references mark the locked classifier upper bound
(600 mmHg) and the alveolar-gas-equation sea-level prediction
(~653 mmHg).

Matplotlib aesthetic copied verbatim from scripts/make_paper_fig04.py
per the visual-consistency guardrail.

Output: preprint_npj/figures/fig_s3_hyperoxia_convergence.{pdf,png}
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
S021_DIR = REPO / "data" / "runs" / "s021_hyperoxia_convergence"
OUT = REPO / "preprint_npj" / "figures" / "fig_s3_hyperoxia_convergence.pdf"

# Load the plateau-stats parquet to identify converged S1 runs.
plateau = pd.read_parquet(S021_DIR / "plateau_stats.parquet")
s1_runs = plateau[plateau["scenario"] == "S1"].copy()

# Read each S1 run's CSV.
trajectories: list[pd.DataFrame] = []
for _, row in s1_runs.iterrows():
    run_dir = S021_DIR / row["case_id_long"]
    csv = run_dir / "output.csv"
    if not csv.exists():
        continue
    df = pd.read_csv(csv)
    df = df[["time_s", "ArterialOxygenPressure"]].copy()
    df["run_id"] = row["case_id_long"]
    df["converged"] = row["converged"]
    trajectories.append(df)

all_traj = pd.concat(trajectories, ignore_index=True)
converged = all_traj[all_traj["converged"]]
n_converged = converged["run_id"].nunique()
n_total = all_traj["run_id"].nunique()

# Median trajectory across converged runs at each timepoint.
median_traj = converged.groupby("time_s")["ArterialOxygenPressure"].median()

fig, ax = plt.subplots(1, 1, figsize=(10.0, 5.5))

# Overlapping individual trajectories (converged runs).
for run_id, sub in converged.groupby("run_id"):
    ax.plot(sub["time_s"], sub["ArterialOxygenPressure"],
            color="#4C72B0", alpha=0.20, linewidth=0.9, zorder=1)

# Highlight median across converged runs.
ax.plot(median_traj.index, median_traj.values,
        color="#4C72B0", linewidth=2.6, alpha=0.95, zorder=3,
        label=f"S1 median trajectory ({n_converged} converged of {n_total} S1 reruns)")

# Reference horizontals.
ax.axhline(600, color="#8172B2", linestyle=":", linewidth=1.0, alpha=0.85,
           label="600 mmHg locked classifier upper bound")
ax.axhline(653, color="#937860", linestyle="-.", linewidth=1.0, alpha=0.85,
           label=r"$\approx$ 653 mmHg alveolar-gas-equation prediction")

ax.set_xlim(0, 300)
ax.set_xlabel(r"Extended-simulation time $t'$ (s); $t' = 0$ corresponds to $t = 120$ s of the original simulation")
ax.set_ylabel(r"Arterial PaO$_2$ (mmHg)")
ax.set_title(
    "Hyperoxia late-phase convergence (S021 reruns, FiO$_2$ = 1.0, S1 healthy)",
    fontsize=10,
)
ax.legend(loc="lower right", fontsize=8, frameon=True)
ax.grid(True, axis="y", alpha=0.25, linewidth=0.5)

fig.tight_layout()
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=200, bbox_inches="tight")
fig.savefig(OUT.with_suffix(".png"), dpi=200, bbox_inches="tight")
print(f"Wrote {OUT}")
print(f"Wrote {OUT.with_suffix('.png')}")
print(f"  n_total = {n_total}, n_converged = {n_converged}")
print(f"  PaO2 at t'=0   (= t=120 s original): median {median_traj.iloc[0]:.1f} mmHg")
print(f"  PaO2 at t'=300 (= t=300 s extended): median {median_traj.iloc[-1]:.1f} mmHg")

# Compute time to 95 percent of plateau (median trajectory).
asymptote = median_traj.iloc[-1]
floor_val = median_traj.iloc[0]
target = floor_val + 0.95 * (asymptote - floor_val)
above_target = median_traj[median_traj >= target]
if not above_target.empty:
    t_95 = above_target.index[0]
    print(f"  Time-to-95% (from t'=0 floor to t'=300 asymptote, median trajectory): {t_95:.0f} s")
