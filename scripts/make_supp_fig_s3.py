"""Generate Supplement Figure S3: PaO2 late-phase convergence trajectories
from the S021 hyperoxia 300-second rerun cohort.

IMPORTANT framing (corrected 2026-08-06; see
audit/s021_clock_reframing_diffs.md):
The x-axis is the rerun's own recorded simulation time, t = 0 to 300 s.
Each rerun is a separate re-execution of the same configuration from time
zero, with the recorded duration raised from 120 s to 300 s -- NOT a
saved-state continuation. PaO2 is already hyperoxic at t = 0 because the
configured FiO2 = 1.0 applies through the unchanged 120 s ventilator-settle
phase that precedes recording (VENT_SETTLE_S in engine/run_atlas_engine.py),
so one rerun spans 420 s of Pulse-internal time. The figure therefore
visualises the LATE-PHASE CONVERGENCE of PaO2 toward its true plateau, not a
fresh wash-in from an atmospheric-air baseline.

Visualises the 40 drift-converged S1 (healthy) S021 reruns as overlapping
thin trajectories. Three of those 40 are drift-converged but relax to
unphysical >700 mmHg plateaus (numerical runaways); they are plotted but
EXCLUDED from the highlighted median, which is taken over the remaining 37
physiological-converged runs (Supplement Pass C corrections SP-C.D2 / C1).
Counts were 41 and 38 until 2026-09-01, when the S021 window-selection fix
moved one run across the drift threshold; see audit/synthesis_pass_2026_08.md
section 15.
Horizontal references mark the locked classifier upper bound (600 mmHg)
and the alveolar-gas-equation sea-level prediction (alveolar PAO2,
~663 mmHg). The vertical axis is limited to [350, 760] mmHg; the runaway
traces continue off-scale to ~1,400 mmHg.

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

# Drift-converged runs whose plateau exceeds this are numerically unstable
# (relax to ~1,400 mmHg) and are excluded from the physiological median.
RUNAWAY_PLATEAU_MMHG = 700.0

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
    df["plateau"] = row["PaO2_plateau_mmHg"]
    trajectories.append(df)

all_traj = pd.concat(trajectories, ignore_index=True)
# All drift-converged runs (plotted as thin traces).
converged = all_traj[all_traj["converged"]]
# Physiological-converged subset (drift-converged AND plateau <= 700):
# the median and kinetic anchor are computed over these only.
physio = converged[converged["plateau"] <= RUNAWAY_PLATEAU_MMHG]
n_converged = converged["run_id"].nunique()
n_physio = physio["run_id"].nunique()
n_total = all_traj["run_id"].nunique()
n_runaway = n_converged - n_physio

# Median trajectory across the physiological-converged runs at each timepoint.
median_traj = physio.groupby("time_s")["ArterialOxygenPressure"].median()

fig, ax = plt.subplots(1, 1, figsize=(10.0, 5.5))

# Overlapping individual trajectories (all drift-converged runs; the
# runaway traces run off the top of the [350, 760] window).
for run_id, sub in converged.groupby("run_id"):
    ax.plot(sub["time_s"], sub["ArterialOxygenPressure"],
            color="#4C72B0", alpha=0.20, linewidth=0.9, zorder=1)

# Highlight median across the physiological-converged runs.
ax.plot(median_traj.index, median_traj.values,
        color="#4C72B0", linewidth=2.6, alpha=0.95, zorder=3,
        label=f"Median trajectory ({n_physio} physiological-converged of {n_converged} converged)")

# Reference horizontals.
ax.axhline(600, color="#8172B2", linestyle=":", linewidth=1.0, alpha=0.85,
           label="600 mmHg locked classifier upper bound")
ax.axhline(663, color="#937860", linestyle="-.", linewidth=1.0, alpha=0.85,
           label=r"$\approx$ 663 mmHg alveolar-gas-equation prediction (alveolar P$_A$O$_2$)")

ax.set_xlim(0, 300)
ax.set_ylim(350, 760)
ax.annotate(
    f"{n_runaway} drift-converged runs run off-scale\n"
    r"to $\approx$1,400 mmHg (numerical runaway; excluded from median)",
    xy=(0.97, 0.97), xycoords="axes fraction", ha="right", va="top",
    fontsize=8, color="#555555", style="italic",
)
ax.set_xlabel(r"Recorded simulation time $t$ (s), 300-s rerun")
ax.set_ylabel(r"Arterial PaO$_2$ (mmHg)")
ax.set_title(
    "Hyperoxia late-phase convergence (S021 reruns, FiO$_2$ = 1.0, Healthy)",
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
print(f"  n_total = {n_total}, n_converged = {n_converged}, n_physio = {n_physio}, n_runaway = {n_runaway}")
print(f"  PaO2 at t=0   (recorded clock): median {median_traj.iloc[0]:.1f} mmHg")
print(f"  PaO2 at t=300 (recorded clock): median {median_traj.iloc[-1]:.1f} mmHg")

# Compute time to 95 percent of plateau (physiological median trajectory).
asymptote = median_traj.iloc[-1]
floor_val = median_traj.iloc[0]
target = floor_val + 0.95 * (asymptote - floor_val)
above_target = median_traj[median_traj >= target]
if not above_target.empty:
    t_95 = above_target.index[0]
    print(f"  Time-to-95% (physiological median, t=0 floor to t=300 late plateau): {t_95:.0f} s")
