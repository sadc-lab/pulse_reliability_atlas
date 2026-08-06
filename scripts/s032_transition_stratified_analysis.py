"""S032 step 3 — SBP-transition-stratified sensitivity analysis (no new simulations).

Why
---
The exclusion analysis (`s032_uncontaminated_step_analysis.py`) showed mu*(SBP -> MAP)
falls in 8 of 8 cells once the contaminated systolic steps are dropped. That fall is
consistent with upward contamination, but it is confounded with position: the
contaminated steps sit at the low-SBP end of the domain, the same confound Supplement
S3.7 already states for diastolic step length.

This narrows that confound without new runs. Three systolic transitions carry both
contaminated and clean steps, so contaminated and clean elementary effects can be
compared *within* a transition, where the systolic start and end values are identical.

What it is NOT. This is not a controlled comparison. Only the systolic coordinates
match; the requested DBP, the other five inputs and the position within the trajectory
all differ between the two groups. With group sizes in the single digits the analysis is
descriptive: no significance test, no causal attribution. It answers one question only --
does the contaminated-versus-clean gap persist when the systolic transition is held
fixed?

How
---
The pair annotation, the calibration gate and the elementary-effect machinery are
imported from the exclusion analysis rather than reimplemented, so both scripts use one
definition of "contaminated" -- the one that reproduces the nine audited S3.7 counts.

Two population layers are reported and must not be conflated:
  design  -- the 20 systolic steps of the shared Morris plan, before any flag filtering
  clean   -- the pairs surviving the four-flag screen, pooled over the eight cells

Usage::

    uv run python scripts/s032_transition_stratified_analysis.py

Exit status: 0 = ran; 1 = calibration mismatch; 2 = missing input artefact.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from s032_uncontaminated_step_analysis import (  # noqa: E402
    OUT,
    annotate_pairs,
    calibrate,
    elementary_effects,
    load_inputs,
)


def label(lo: float, hi: float) -> str:
    return f"{int(lo)}->{int(hi)}"


# Audited in Supplement S3.7 (T5.clip.clean_sbp_total / clean_sbp_contaminated).
# The stratified population must reconstruct these exactly, or it is analysing
# some other set of pairs than the one the manuscript reports on.
EXPECTED_CLEAN_SBP = 68
EXPECTED_CONTAMINATED = 19


def main() -> int:
    agg, smp = load_inputs()
    pairs = annotate_pairs(smp)
    if not calibrate(agg, smp, pairs):
        print("\n[s032-strat] calibration failed; nothing below is usable.")
        return 1
    print("\nCalibration passed on 9/9 quantities.\n")

    OUT.mkdir(parents=True, exist_ok=True)
    sbp_steps = pairs[pairs["flipped"] == "sbp"].copy()
    sbp_steps["transition"] = [label(r.sbp_lo, r.sbp_hi) for r in sbp_steps.itertuples()]
    # Requested DBP is constant across a systolic step (DBP is not the flipped
    # input), so the low endpoint carries it. Reported per group below so the
    # residual confound is visible rather than merely asserted in prose.
    sbp_steps["dbp_req"] = [float(smp.loc[r.idx_lo, "dbp"]) for r in sbp_steps.itertuples()]
    # How far the applied DBP is dragged during the step, in mmHg. This is the
    # quantity that separates the two competing readings of any gap: a DBP-LEVEL
    # effect would be constant across transitions (every contaminated pair has
    # the same requested DBP), whereas contamination should scale with this
    # displacement, which is a property of the transition.
    dbp_span = 80.0 - 60.0
    sbp_steps["dbp_shift_mmhg"] = sbp_steps["dbp_delta_applied"] * dbp_span

    print("## Layer 1 — the design (20 systolic steps, before any flag filtering)\n")
    print("| transition | contaminated | clean |")
    print("|---|---|---|")
    design = (sbp_steps.groupby(["transition", "contaminated"]).size()
              .unstack(fill_value=0).rename(columns={True: "contaminated", False: "clean"}))
    for t, row in design.iterrows():
        print(f"| {t} | {row.get('contaminated', 0)} | {row.get('clean', 0)} |")

    ee = elementary_effects(agg, pairs)
    sub = ee[(ee["input"] == "sbp") & (ee["output"] == "MAP")].copy()
    tmap = sbp_steps.set_index("trajectory")["transition"]
    sub["transition"] = sub["trajectory"].map(tmap)
    sub["dbp_req"] = sub["trajectory"].map(sbp_steps.set_index("trajectory")["dbp_req"])
    sub["dbp_shift_mmhg"] = sub["trajectory"].map(sbp_steps.set_index("trajectory")["dbp_shift_mmhg"])
    sub["abs_ee"] = sub["ee"].abs()

    # Reconstruction gate. If the stratified population is not the audited one,
    # every table below describes some other set of pairs.
    n_c, n_k = int(sub["contaminated"].sum()), int((~sub["contaminated"]).sum())
    print("## Population gate — clean systolic pairs pooled over the eight cells\n")
    print("| quantity | audited | measured | |")
    print("|---|---|---|---|")
    for name, exp, got in (("clean SBP pairs", EXPECTED_CLEAN_SBP, len(sub)),
                           ("of which contaminated", EXPECTED_CONTAMINATED, n_c),
                           ("of which clean", EXPECTED_CLEAN_SBP - EXPECTED_CONTAMINATED, n_k)):
        print(f"| {name} | {exp} | {got} | {'PASS' if exp == got else 'FAIL'} |")
    if (len(sub), n_c) != (EXPECTED_CLEAN_SBP, EXPECTED_CONTAMINATED):
        print("\n[s032-strat] population does not reconstruct the audited counts; stopping.")
        return 1
    if sub["transition"].isna().any():
        print("\n[s032-strat] some pairs have no transition label; stopping.")
        return 1
    sub.to_csv(OUT / "transition_stratified_sbp_map.csv", index=False)

    print(f"\n## Layer 2 — clean pairs by transition (n = {len(sub)})\n")
    print("| transition | group | n | requested DBP | median signed EE | range signed | "
          "median abs EE | range abs |")
    print("|---|---|---|---|---|---|---|---|")
    for t in sorted(sub["transition"].dropna().unique()):
        for flag, name in ((True, "contaminated"), (False, "clean")):
            g = sub[(sub["transition"] == t) & (sub["contaminated"] == flag)]
            if g.empty:
                print(f"| {t} | {name} | 0 | - | - | - | - | - |")
                continue
            dbps = "/".join(f"{v:g}" for v in sorted(g["dbp_req"].unique()))
            print(f"| {t} | {name} | {len(g)} | {dbps} | {g['ee'].median():.4g} | "
                  f"[{g['ee'].min():.4g}, {g['ee'].max():.4g}] | "
                  f"{g['abs_ee'].median():.4g} | "
                  f"[{g['abs_ee'].min():.4g}, {g['abs_ee'].max():.4g}] |")

    print("\n## Within-transition contrast on |EE| (descriptive only)\n")
    print("| transition | n contam. | n clean | median abs contam. | median abs clean "
          "| difference | applied DBP shift (mmHg) | contaminated higher? |")
    print("|---|---|---|---|---|---|---|---|")
    contrasts = []
    for t in sorted(sub["transition"].dropna().unique()):
        c = sub[(sub["transition"] == t) & (sub["contaminated"])]["abs_ee"]
        k = sub[(sub["transition"] == t) & (~sub["contaminated"])]["abs_ee"]
        if c.empty or k.empty:
            print(f"| {t} | {len(c)} | {len(k)} | - | - | - | - | not evaluable |")
            continue
        d = float(c.median() - k.median())
        shift = float(sub[(sub["transition"] == t) & sub["contaminated"]]
                      ["dbp_shift_mmhg"].abs().median())
        contrasts.append({"transition": t, "n_contaminated": len(c), "n_clean": len(k),
                          "median_abs_contaminated": float(c.median()),
                          "median_abs_clean": float(k.median()), "difference": d,
                          "applied_dbp_shift_mmhg": shift})
        print(f"| {t} | {len(c)} | {len(k)} | {c.median():.4g} | {k.median():.4g} "
              f"| {d:+.4g} | {shift:.4g} | {'yes' if d > 0 else 'no'} |")

    cdf = pd.DataFrame(contrasts)
    cdf.to_csv(OUT / "transition_stratified_contrasts.csv", index=False)

    print("\n## Unstratified contrast, and leave-one-transition-out\n")
    print("| transitions included | n contam. | n clean | median abs contam. "
          "| median abs clean | difference |")
    print("|---|---|---|---|---|---|")

    def contrast(df: pd.DataFrame, tag: str) -> None:
        c = df[df["contaminated"]]["abs_ee"]
        k = df[~df["contaminated"]]["abs_ee"]
        if c.empty or k.empty:
            print(f"| {tag} | {len(c)} | {len(k)} | - | - | not evaluable |")
            return
        print(f"| {tag} | {len(c)} | {len(k)} | {c.median():.4g} | {k.median():.4g} "
              f"| {c.median() - k.median():+.4g} |")

    evaluable = sorted(cdf["transition"]) if len(cdf) else []
    contrast(sub, "all")
    for t in evaluable:
        contrast(sub[sub["transition"] != t], f"all except {t}")

    print("\n## Reading\n")
    if len(cdf):
        agree = int((cdf["difference"] > 0).sum())
        print(f"- The contaminated group has the higher median |EE| in {agree} of "
              f"{len(cdf)} evaluable transitions.")
        if agree == len(cdf):
            print("- The gap therefore persists when the systolic transition is held")
            print("  fixed: it is not explained by systolic position alone.")
        elif agree == 0:
            print("- No systematic inflation is detectable once the systolic transition")
            print("  is held fixed.")
        else:
            print("- The gap is not consistent across transitions; no directional")
            print("  reading is supported.")
    # The requested DBP is perfectly collinear with contamination here -- and
    # largely by construction, since at SBP = 100 only DBP = 80 clears the
    # 0.75 x SBP ceiling. Stratifying on the transition therefore does NOT
    # separate contamination from a DBP-level effect. What can separate them is
    # the applied-DBP displacement, which differs between transitions while the
    # requested DBP does not.
    if len(cdf) >= 2:
        def levels(mask: pd.Series) -> str:
            return "/".join(f"{v:g}" for v in sorted(sub[mask]["dbp_req"].unique()))

        print(f"\n- Requested DBP is perfectly collinear with contamination "
              f"({levels(sub['contaminated'])} vs {levels(~sub['contaminated'])} mmHg), "
              "so the")
        print("  stratification does not by itself rule out a DBP-level effect.")
        by_shift = cdf.groupby("applied_dbp_shift_mmhg")["difference"].median().sort_index()
        pairs_txt = ", ".join(f"{s:g} mmHg -> {d:+.3g}" for s, d in by_shift.items())
        print(f"- Gap versus applied-DBP displacement: {pairs_txt}.")
        if list(by_shift.values) == sorted(by_shift.values):
            print("  The gap increases with the displacement while the requested DBP is")
            print("  identical in all contaminated groups, which a pure DBP-level effect")
            print("  would not produce. This favours the contamination reading.")
        else:
            print("  The gap does not track the displacement, so the two readings are")
            print("  not separated by this comparison.")
        print(f"  Fragility: {len(cdf)} evaluable transitions over "
              f"{cdf['applied_dbp_shift_mmhg'].nunique()} distinct displacements, with "
              f"contaminated group sizes {sorted(cdf['n_contaminated'])}. This is one")
        print("  comparison, not a dose-response curve.")
    print("\n- Descriptive only. Requested DBP, the other five inputs and the position")
    print("  within the trajectory still differ between groups, and the group sizes are")
    print("  single-digit. No significance test and no causal attribution.")
    print(f"\nArtefacts written to {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
