"""Generate Supplement Figure S4: Per-breath tidal-volume waveform at
Pulse's native 50 Hz sampling rate, comparing one representative
configuration before and after the trigger-lockout intervention
(VC-AC InspirationPatientTriggerPressure set to -2 cmH2O).

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

# Use the S014 paired_comparison to pick the configuration with the
# largest before/after delta (most visually informative example).
paired = pd.read_parquet(S014_DIR / "paired_comparison.parquet")
paired["delta"] = paired["Vt_cv_orig"] - paired["Vt_cv_lock"]
top = paired.sort_values("delta", ascending=False).iloc[0]
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

# Restrict to the final 60-second steady-state window for direct
# breath-pattern comparison (this is the window the locked classifier
# computes Vt CV on).
WINDOW_LO, WINDOW_HI = 60.0, 120.0
orig_win = orig[(orig["time_s"] >= WINDOW_LO) & (orig["time_s"] <= WINDOW_HI)]
lock_win = lock[(lock["time_s"] >= WINDOW_LO) & (lock["time_s"] <= WINDOW_HI)]

fig, (axA, axB) = plt.subplots(2, 1, figsize=(11.0, 6.5), sharex=True)

axA.plot(orig_win["time_s"], orig_win["Vt_mL"],
         color="#C44E52", linewidth=1.1, alpha=0.85,
         label=f"Default trigger configuration (Vt CV = {top['Vt_cv_orig']:.3f})")
axA.set_ylabel("Delivered $V_T$ (mL)")
axA.set_title(
    "(a) Default VC-AC trigger configuration: per-breath delivered tidal volume",
    fontsize=10,
)
axA.legend(loc="upper right", fontsize=9, frameon=True)
axA.grid(True, alpha=0.25, linewidth=0.5)

axB.plot(lock_win["time_s"], lock_win["Vt_mL"],
         color="#4C72B0", linewidth=1.1, alpha=0.85,
         label=f"Trigger pressure = $-2$ cmH$_2$O (Vt CV = {top['Vt_cv_lock']:.3f})")
axB.set_xlabel("Simulation time $t$ (s) -- final 60-s steady-state window of the 120-s simulation")
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
print(f"  Representative case: {case_id_orig}")
print(f"  Default Vt CV = {top['Vt_cv_orig']:.3f}, Locked Vt CV = {top['Vt_cv_lock']:.3f}")
print(f"  Native CSV rows: orig={len(orig)}, lock={len(lock)}; window rows: orig={len(orig_win)}, lock={len(lock_win)}")
