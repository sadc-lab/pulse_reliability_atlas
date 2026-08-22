"""Generate the supplement's per-breath tidal-volume waveform figure at
Pulse's native 50 Hz sampling rate, comparing one paired configuration
before and after the trigger-lockout intervention (VC-AC
InspirationPatientTriggerPressure set to -2 cmH2O).

WHICH RUN, AND WHY THE RULE IS FIXED IN CODE
The configuration is selected deterministically as the one whose
pre-lock classifier Vt CV is closest to the median across the 64 paired
reruns, ties broken on case_id. The rule is stated here rather than
applied by eye so that the illustration cannot be chosen after seeing
which run looks most convincing.

This replaces an earlier largest-delta selection, which picked the
single worst-affected run. That run is worst because ventilation stops
(TidalVolume, RespirationRate and I:E all report 0 across most of the
steady-state window), not because it oscillates, so it illustrated a
different failure mode from the one this figure is for. The worst case
remains visible as the extreme dot in paper Figure 3a, and Section 2.3
still quotes it by name.

TIME BASE -- THE DEFECT THIS HEADER EXISTS TO PREVENT
output.csv carries RECORDING-RELATIVE time (0 to 120 s); Pulse's own
output_pulse_native.csv carries ABSOLUTE simulation time, which leads by
the ventilator-settle phase. A window written for one is wrong for the
other. An earlier version of this script applied the classifier's
relative [60, 120] s window to the native file and therefore plotted the
settle phase -- before recording begins -- while labelling it with a
statistic computed over the real window. The offset is now derived from
the data and asserted at both ends instead of assumed.

IMPORTANT data-availability caveat (per maintainer-audited Phase 9.C):
Pulse's standard CSV output does not expose airway Pressure (P_aw) or
Respiratory Flow (Q_dot) as top-level columns. The per-breath
TidalVolume(mL) channel, sampled at the native 50 Hz, is the
directly-observable proxy of the trigger dyssynchrony signal that the
locked steady-state classifier flags as not_steady_state on 20.6 %
of the full sweep (see Section 2.3 of the main manuscript).

50 Hz native sampling is a 200x oversample of the ~0.25 Hz adult
respiratory-rate signal, so the per-breath Vt waveform shown here is
fully Nyquist-safe and shows genuine breath-by-breath dynamics rather
than aliasing artefact.

Matplotlib aesthetic copied verbatim from scripts/make_paper_fig04.py
per the visual-consistency guardrail.

Output: preprint_npj/figures/fig_s4_vt_waveform.{pdf,png}
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
S014_DIR = REPO / "data" / "runs" / "s014_trigger_lockout"
OUT = REPO / "preprint_npj" / "figures" / "fig_s4_vt_waveform.pdf"

# Deterministic selection: the run whose PRE-LOCK classifier Vt CV sits
# closest to the median over the 64 pairs. With an even count the median
# falls between the two central runs, so both are equidistant; case_id
# ascending breaks that tie reproducibly. Stated as code, not chosen by
# eye, so the illustration cannot be picked after seeing the waveforms.
paired = pd.read_parquet(S014_DIR / "paired_comparison.parquet")
median_cv = paired["Vt_cv_orig"].median()
paired["dist_to_median"] = (paired["Vt_cv_orig"] - median_cv).abs()
top = paired.sort_values(["dist_to_median", "case_id"]).iloc[0]
print(f"  median pre-lock classifier Vt CV over {len(paired)} pairs = {median_cv:.6f}")
print(f"  selected {top['case_id']} (Vt CV = {top['Vt_cv_orig']:.6f}, "
      f"distance {top['dist_to_median']:.6f})")
case_id_orig = top["case_id"]
case_id_lock = top["case_id_lock"]

# The corresponding paired full-sweep run lives in
# data/runs/full_sweep/<scenario>_<sex>/<case_id>/output_pulse_native.csv
# (the canonical pre-intervention configuration). The locked rerun is in S014_DIR.
scenario_sex = f"{top['scenario']}_{top['sex']}"
ORIG_DIR = REPO / "data" / "runs" / "full_sweep" / scenario_sex / case_id_orig
LOCK_DIR = S014_DIR / case_id_lock

orig_csv = ORIG_DIR / "output_pulse_native.csv"
lock_csv = LOCK_DIR / "output_pulse_native.csv"
assert orig_csv.exists(), f"full_sweep native CSV not found at {orig_csv}"
assert lock_csv.exists(), f"S014 lock native CSV not found at {lock_csv}"

orig = pd.read_csv(orig_csv)
lock = pd.read_csv(lock_csv)

# Keep the relevant columns and rename for plotting.
def prep(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns={
        "Time(s)": "time_s",
        "TidalVolume(mL)": "Vt_mL",
    })[["time_s", "Vt_mL"]]

orig = prep(orig)
lock = prep(lock)

# The classifier's steady-state window is RECORDING-RELATIVE [60, 120] s.
# The native waveform is on Pulse's ABSOLUTE clock, which leads it by the
# ventilator-settle phase, and it also covers that phase -- so the two
# series are not a translation of one another, the native one is a
# superset. Comparing their start times would therefore compare the
# simulation start against the recording start and prove nothing.
#
# The offset is taken from the end, where both series stop at the same
# real instant, and then VERIFIED ON VALUES: at probe points inside the
# window, the native sample at t+offset must equal the recorded sample at
# t. A clock check can be satisfied by a wrong offset; a value check
# cannot. This is the guard for the defect that produced the earlier
# version of this figure.
WINDOW_LO, WINDOW_HI = 60.0, 120.0
VALUE_TOL_ML = 1e-6


def settle_offset(run_dir: Path) -> float:
    rec = pd.read_csv(run_dir / "output.csv")
    nat = pd.read_csv(run_dir / "output_pulse_native.csv").rename(
        columns={"Time(s)": "time_s", "TidalVolume(mL)": "Vt_mL"})
    offset = float(nat["time_s"].max() - rec["time_s"].max())
    if offset < 0:
        raise AssertionError(f"{run_dir.name}: native clock trails the recorded one")

    probes = rec[(rec["time_s"] >= WINDOW_LO) & (rec["time_s"] <= WINDOW_HI)]
    if probes.empty:
        raise AssertionError(f"{run_dir.name}: no recorded samples in the window")
    for _, row in probes.iterrows():
        target = row["time_s"] + offset
        hit = nat.iloc[(nat["time_s"] - target).abs().argmin()]
        if abs(hit["Vt_mL"] - row["TidalVolume"]) > VALUE_TOL_ML:
            raise AssertionError(
                f"{run_dir.name}: offset {offset:.3f} s does not align the two "
                f"clocks -- recorded t={row['time_s']:.2f} gives "
                f"{row['TidalVolume']:.6f} mL, native t={hit['time_s']:.2f} "
                f"gives {hit['Vt_mL']:.6f} mL")
    return offset


off_orig = settle_offset(ORIG_DIR)
off_lock = settle_offset(LOCK_DIR)
print(f"  settle offset: orig {off_orig:.2f} s, lock {off_lock:.2f} s "
      f"(value-verified on {int(WINDOW_HI - WINDOW_LO) // 5 + 1} probe samples each)")

# Slice on the absolute clock, then re-express the x-axis in recording-
# relative time so the panel reads 60-120 s, the window the caption and
# the classifier both name.
orig_win = orig[(orig["time_s"] >= WINDOW_LO + off_orig)
                & (orig["time_s"] <= WINDOW_HI + off_orig)].copy()
lock_win = lock[(lock["time_s"] >= WINDOW_LO + off_lock)
                & (lock["time_s"] <= WINDOW_HI + off_lock)].copy()
orig_win["time_s"] -= off_orig
lock_win["time_s"] -= off_lock

fig, (axA, axB) = plt.subplots(2, 1, figsize=(11.0, 6.5), sharex=True)

axA.plot(orig_win["time_s"], orig_win["Vt_mL"],
         color="#C44E52", linewidth=1.1, alpha=0.85,
         label=f"Default trigger configuration (classifier CV, 5-s sampling = {top['Vt_cv_orig']:.3f})")
axA.set_ylabel("Delivered $V_T$ (mL)")
axA.set_title(
    "(a) Default VC-AC trigger configuration: per-breath delivered tidal volume",
    fontsize=10,
)
axA.legend(loc="upper right", fontsize=9, frameon=True)
axA.grid(True, alpha=0.25, linewidth=0.5)

axB.plot(lock_win["time_s"], lock_win["Vt_mL"],
         color="#4C72B0", linewidth=1.1, alpha=0.85,
         label=f"Trigger pressure = $-2$ cmH$_2$O (classifier CV, 5-s sampling = {top['Vt_cv_lock']:.3f})")
axB.set_xlabel("Recorded simulation time $t$ (s) -- final 60-s steady-state window of the 120-s recording")
axB.set_ylabel("Delivered $V_T$ (mL)")
axB.set_title(
    "(b) Locked trigger configuration ($-2$ cmH$_2$O): per-breath delivered tidal volume",
    fontsize=10,
)
axB.legend(loc="upper right", fontsize=9, frameon=True)
axB.grid(True, alpha=0.25, linewidth=0.5)

# Common y-axis for direct visual comparison.
y_lo = min(orig_win["Vt_mL"].min(), lock_win["Vt_mL"].min()) * 0.95
y_hi = max(orig_win["Vt_mL"].max(), lock_win["Vt_mL"].max()) * 1.05
axA.set_ylim(y_lo, y_hi)
axB.set_ylim(y_lo, y_hi)

fig.tight_layout()
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=200, bbox_inches="tight")
fig.savefig(OUT.with_suffix(".png"), dpi=200, bbox_inches="tight")
print(f"Wrote {OUT}")
print(f"Wrote {OUT.with_suffix('.png')}")
print(f"  Median-selected case: {case_id_orig}")
print(f"  Default Vt CV = {top['Vt_cv_orig']:.3f}, Locked Vt CV = {top['Vt_cv_lock']:.3f}")
print(f"  Native CSV rows: orig={len(orig)}, lock={len(lock)}; window rows: orig={len(orig_win)}, lock={len(lock_win)}")
