#!/usr/bin/env python3
"""S034 -- Do the Morris rankings depend on the clean-pair screen?

The question
------------
The published Morris indices use only elementary-effect pairs whose *both*
endpoints are four-flag clean: 663 of the 1,280 runs survive that screen
(`src/analysis_morris.py` line 139, preregistration section A.2). A reviewer can
reasonably ask whether the input rankings are an artefact of that screen rather
than a property of the engine, because the screen removes 471 runs whose only
flag is `not_steady_state` -- runs that did produce interpretable output.

This script answers it on data already recorded, by recomputing the same
rankings under a second screen and comparing. It is the only probe available
against that objection without new simulation, and the SHAP cross-check in
Supplement S13 cannot answer it: that surrogate is trained on the same 663 runs.

What this is NOT
----------------
**A parallel calculation, never a replacement.** The clean screen is
preregistered. `results/morris_indices.parquet` and every published index stay
the reference; this script writes only under `results/s034/` and never opens the
published artefact except to calibrate against it.

**Not a less-biased estimator, and it must never be reported as one.** The 471
runs the relaxed screen admits are exactly those whose steady-state mean is not
a valid summary of the run -- that is what `not_steady_state` means. Including
them trades a selection bias for a measurement error; it does not reduce bias.
The honest framing is: *sensitivity of the ranking to the treatment of
non-stationary runs.* The gain in pairs concentrates in S1, where Vt
oscillation is worst, so the extra data is most abundant exactly where it is
least trustworthy.

Pre-specification, fixed before running
---------------------------------------
Three criteria per (cell, output) combination, from the seed-44 stability
precedent:

  1. top-1 input preserved;
  2. top-three *set* preserved (order ignored);
  3. top-three *order* preserved.

**The raw counts are the result.** No "acceptable stability" threshold is
introduced afterwards. Change in estimability is reported separately from
change in ranking, never merged into one number.

Two denominators are reported, and neither is chosen over the other
-------------------------------------------------------------------
All 48 (cell x output) combinations are estimable under the published screen:
six of the seven inputs have a mu* in all 48, and FiO2 has one in 30 -- it is
unestimable only in S1_M, S1_F and S4_F, where every FiO2 pair has a flagged
endpoint (main paper, Morris heatmap caption; 6 x 48 + 30 = 318 rows, which is
exactly the published artefact's row count).

So in 18 of the 48 combinations the top three is drawn from six candidates
rather than seven. If the relaxed screen makes FiO2 estimable there, the
candidate set itself changes and "rank preserved" is not a like-for-like
comparison. Both denominators are therefore printed:

  * **all 48**, with candidate-set changes counted as changes;
  * **the subset whose candidate set is identical under both screens**.

Reporting both is not a post-hoc choice between them; choosing one after seeing
the counts would be.

Calibration
-----------
`--strict` (the default) aborts unless recomputing under the *clean* screen
reproduces `results/morris_indices.parquet` exactly: the same 318
(cell, output, input) rows, and mu* equal to double precision. If this script's
own derivation cannot reproduce the published numbers, its comparison means
nothing.

Outputs
-------
  results/s034/mu_star_by_screen.csv    mu* and pair counts, per triple, per screen
  results/s034/rank_comparison.csv      one row per (cell, output): the 3 criteria
  results/s034/s034_summary.json        every headline number, one place
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from src.analysis_morris import (  # noqa: E402
    compute_ee_for_cell,
    derive_trajectory_pairs,
    evaluate_h1,
)
from src.scenario import case_id  # noqa: E402

SWEEP = REPO / "data" / "runs" / "full_sweep"
PUBLISHED = REPO / "results" / "morris_indices.parquet"
OUT_DIR = REPO / "results" / "s034"

CELLS = [(f"S{i}", s) for i in (1, 2, 3, 4) for s in ("M", "F")]
TOP_K = 3

# A published third-to-fourth mu* gap below this counts as a "narrow" top-three
# cut: the design does not resolve which input is third. Descriptive only --
# the raw margins are written to the CSV, and both groups are reported.
NARROW_CUT = 0.10

# Values established elsewhere, used here as positive controls.
EXPECTED_PUBLISHED_ROWS = 318
EXPECTED_CLEAN_RUNS = 663
EXPECTED_HFF_RUNS = 1134
EXPECTED_COMBINATIONS = 48


def fmt(x: float) -> str:
    return "%.12g" % x


def mu_star_table(ee: pd.DataFrame, screen: str) -> pd.DataFrame:
    """mu* and pair count per (output, input) under one screen column."""
    kept = ee[ee[screen]].dropna(subset=["ee"])
    if kept.empty:
        return pd.DataFrame(columns=["output", "input", "mu_star", "n_pairs"])
    g = kept.groupby(["output", "input"])["ee"]
    out = pd.DataFrame(
        {
            "mu_star": g.apply(lambda s: float(np.mean(np.abs(s.to_numpy())))),
            "n_pairs": g.size(),
        }
    ).reset_index()
    return out


def cut_margin(sub: pd.DataFrame, k: int = TOP_K) -> float:
    """Relative gap between the kth and (k+1)th mu* -- the top-k cut margin.

    Why this exists: a "top-three set changed" verdict means something very
    different when the third and fourth inputs differ by 40 % than when they
    differ by 0.5 %. In the second case the design simply does not resolve
    their order, and calling the change an instability of the screen would be
    attributing to the screen what belongs to the estimator's resolution.
    Returned as (mu*_k - mu*_{k+1}) / mu*_k, NaN when there is no (k+1)th input.
    """
    s = sub.sort_values(["mu_star", "input"], ascending=[False, True])["mu_star"].to_numpy()
    if s.size <= k or s[k - 1] <= 0:
        return float("nan")
    return float((s[k - 1] - s[k]) / s[k - 1])


def top_k_inputs(sub: pd.DataFrame, k: int = TOP_K) -> list[str]:
    """The k inputs with the largest mu*, ties broken by input name.

    A deterministic tie-break matters: without one, two runs of this script
    could report a different "order preserved" verdict on identical numbers.
    """
    s = sub.sort_values(["mu_star", "input"], ascending=[False, True])
    return s["input"].tolist()[:k]


def analyse(strict: bool) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    master = pd.read_parquet(SWEEP / "aggregated.parquet")
    sample = pd.read_parquet(SWEEP / "morris_sample.parquet")
    published = pd.read_parquet(PUBLISHED)

    n_clean = int(master["clean"].sum())
    n_hff = int((~master["diverged"] & ~master["implausible"]).sum())

    pairs = derive_trajectory_pairs(sample)
    flags = master.set_index("case_id")[["diverged", "implausible", "clean"]]

    rows: list[dict] = []
    problems: list[str] = []
    for sk, xk in CELLS:
        cell_df = master[(master["scenario"] == sk) & (master["sex"] == xk)]
        if cell_df.empty:
            raise SystemExit(f"cell {sk}_{xk} is empty in the master table")
        idx_to_case = {int(i): case_id(sk, xk, run_idx=int(i)) for i in sample.index}
        ee = compute_ee_for_cell(cell_df, pairs, idx_to_case)
        if ee.empty:
            raise SystemExit(f"no elementary-effect pairs derived for {sk}_{xk}")

        # The second screen, built from the endpoint flags rather than from
        # `both_clean`, so the audited EE derivation is reused untouched.
        lo = flags.reindex(ee["j_lo_case"])
        hi = flags.reindex(ee["j_hi_case"])
        hff_lo = (~lo["diverged"].to_numpy(dtype=bool)) & (~lo["implausible"].to_numpy(dtype=bool))
        hff_hi = (~hi["diverged"].to_numpy(dtype=bool)) & (~hi["implausible"].to_numpy(dtype=bool))
        ee = ee.assign(both_hff=hff_lo & hff_hi)

        # Control: the relaxed screen must be a strict superset of the locked
        # one. `clean` implies neither diverged nor implausible by definition,
        # so any pair passing `both_clean` must pass `both_hff`.
        violations = int((ee["both_clean"] & ~ee["both_hff"]).sum())
        if violations:
            problems.append(
                f"{sk}_{xk}: {violations} pair(s) pass the clean screen but not the "
                "hard-failure-free screen, which is impossible by definition"
            )

        for screen, label in (("both_clean", "clean"), ("both_hff", "hff")):
            t = mu_star_table(ee, screen)
            for r in t.to_dict(orient="records"):
                rows.append(
                    {
                        "scenario": sk,
                        "sex": xk,
                        "cell": f"{sk}_{xk}",
                        "screen": label,
                        "output": r["output"],
                        "input": r["input"],
                        "mu_star": float(r["mu_star"]),
                        "n_pairs": int(r["n_pairs"]),
                    }
                )

    long = pd.DataFrame(rows)

    # ---- calibration against the published artefact ---------------------- #
    mine = long[long["screen"] == "clean"].set_index(["scenario", "sex", "output", "input"])
    theirs = published.set_index(["scenario", "sex", "output", "input"])
    if len(theirs) != EXPECTED_PUBLISHED_ROWS:
        problems.append(
            f"published artefact has {len(theirs)} rows, expected {EXPECTED_PUBLISHED_ROWS}"
        )
    only_mine = sorted(set(mine.index) - set(theirs.index))
    only_theirs = sorted(set(theirs.index) - set(mine.index))
    if only_mine or only_theirs:
        problems.append(
            f"clean-screen triples differ from the published set: "
            f"{len(only_mine)} extra, {len(only_theirs)} missing"
        )
    common = sorted(set(mine.index) & set(theirs.index))
    max_delta = float(
        (mine.loc[common, "mu_star"] - theirs.loc[common, "mu_star"]).abs().max()
    ) if common else float("nan")
    if not (max_delta == max_delta and max_delta <= 1e-12):
        problems.append(f"recomputed clean-screen mu* differs from published (max |delta| = {max_delta})")
    if n_clean != EXPECTED_CLEAN_RUNS:
        problems.append(f"clean run count is {n_clean}, expected {EXPECTED_CLEAN_RUNS}")
    if n_hff != EXPECTED_HFF_RUNS:
        problems.append(f"hard-failure-free run count is {n_hff}, expected {EXPECTED_HFF_RUNS}")

    if problems and strict:
        for p in problems:
            print(f"CALIBRATION FAILED: {p}", file=sys.stderr)
        raise SystemExit(1)

    # ---- the three pre-specified criteria -------------------------------- #
    comp_rows: list[dict] = []
    for (cell, output), _ in long.groupby(["cell", "output"]):
        sub = long[(long["cell"] == cell) & (long["output"] == output)]
        c = sub[sub["screen"] == "clean"]
        h = sub[sub["screen"] == "hff"]
        set_c, set_h = set(c["input"]), set(h["input"])
        top_c, top_h = top_k_inputs(c), top_k_inputs(h)
        comp_rows.append(
            {
                "cell": cell,
                "output": output,
                "n_inputs_clean": len(set_c),
                "n_inputs_hff": len(set_h),
                "candidate_set_identical": set_c == set_h,
                "inputs_gained": "|".join(sorted(set_h - set_c)),
                "inputs_lost": "|".join(sorted(set_c - set_h)),
                "top1_clean": top_c[0] if top_c else "",
                "top1_hff": top_h[0] if top_h else "",
                "top1_preserved": bool(top_c[:1] == top_h[:1]),
                "top3_clean": "|".join(top_c),
                "top3_hff": "|".join(top_h),
                "top3_set_preserved": bool(set(top_c) == set(top_h)),
                "top3_order_preserved": bool(top_c == top_h),
                "n_pairs_clean": int(c["n_pairs"].sum()),
                "n_pairs_hff": int(h["n_pairs"].sum()),
                "cut_margin_clean": cut_margin(c),
                "cut_margin_hff": cut_margin(h),
            }
        )
    comp = pd.DataFrame(comp_rows).sort_values(["cell", "output"]).reset_index(drop=True)

    def counts(sub: pd.DataFrame) -> dict:
        return {
            "n": int(len(sub)),
            "top1_preserved": int(sub["top1_preserved"].sum()),
            "top3_set_preserved": int(sub["top3_set_preserved"].sum()),
            "top3_order_preserved": int(sub["top3_order_preserved"].sum()),
        }

    same_set = comp[comp["candidate_set_identical"]]
    s2m = comp[comp["cell"] == "S2_M"]

    # Is a changed top-three set a fragile ranking, or an unresolved one? Split
    # the like-for-like combinations by whether their published third/fourth
    # margin is narrow, and report both groups' preservation rates. The cut is
    # descriptive and the raw margins ship in the CSV beside it.
    narrow = same_set[same_set["cut_margin_clean"] < NARROW_CUT]
    wide = same_set[same_set["cut_margin_clean"] >= NARROW_CUT]

    # H1 under both screens. This is the paper's headline claim and it is about
    # the *concentration* of mu*, not the *identity* of the top three -- so it
    # can hold while the ranking moves. Reusing `evaluate_h1` rather than
    # reimplementing the fraction keeps the published definition.
    h1 = {}
    for label in ("clean", "hff"):
        sub = long[long["screen"] == label][
            ["scenario", "sex", "output", "input", "mu_star"]
        ]
        ev = evaluate_h1(sub, top_k=TOP_K)
        h1[label] = {
            "n_combinations": int(len(ev)),
            "n_pass": int(ev["h1_pass"].sum()),
            "fraction_min": float(ev["top3_fraction"].min()),
            "fraction_median": float(ev["top3_fraction"].median()),
            "fraction_max": float(ev["top3_fraction"].max()),
        }

    summary = {
        "script": "scripts/s034_morris_screen_sensitivity.py",
        "h1_by_screen": h1,
        "framing": (
            "Sensitivity of the Morris ranking to the treatment of non-stationary "
            "runs. The relaxed screen trades a selection bias for a measurement "
            "error; it is NOT a less-biased estimator and must not be reported as "
            "one."
        ),
        "n_runs_clean_screen": n_clean,
        "n_runs_hard_failure_free": n_hff,
        "calibration_problems": problems,
        "calibration_max_abs_mu_star_delta_vs_published": max_delta,
        "n_published_rows_reproduced": len(common),
        "n_combinations_total": int(len(comp)),
        "n_combinations_candidate_set_identical": int(len(same_set)),
        "combinations_with_candidate_change": comp.loc[
            ~comp["candidate_set_identical"], ["cell", "output", "inputs_gained", "inputs_lost"]
        ].to_dict(orient="records"),
        "criteria_all_combinations": counts(comp),
        "criteria_identical_candidate_set_only": counts(same_set),
        "criteria_S2_M_only": counts(s2m),
        "narrow_cut": NARROW_CUT,
        "criteria_narrow_cut_margin": counts(narrow),
        "criteria_wide_cut_margin": counts(wide),
        "median_cut_margin_clean": float(comp["cut_margin_clean"].median()),
        "median_cut_margin_hff": float(comp["cut_margin_hff"].median()),
        # ⚠️ UNIT. `n_pairs` is the pair count for one (cell, output): each
        # elementary-effect pair flips one input and is scored on all six
        # outputs, so summing over the 48 combinations counts every pair six
        # times. The sum is therefore in pair x output units -- elementary-effect
        # observations -- and the distinct-pair figure is that divided by six.
        # The theoretical ceiling is 8 cells x 6 outputs x 20 trajectories x 7
        # steps = 6,720 observations, i.e. 1,120 distinct pairs.
        "n_outputs": 6,
        "ee_observations_clean": int(comp["n_pairs_clean"].sum()),
        "ee_observations_hff": int(comp["n_pairs_hff"].sum()),
        "ee_observation_gain": int(comp["n_pairs_hff"].sum() - comp["n_pairs_clean"].sum()),
        "distinct_pairs_clean": int(comp["n_pairs_clean"].sum()) // 6,
        "distinct_pairs_hff": int(comp["n_pairs_hff"].sum()) // 6,
        "distinct_pair_gain": (
            int(comp["n_pairs_hff"].sum()) - int(comp["n_pairs_clean"].sum())
        ) // 6,
        "distinct_pairs_ceiling": 8 * 20 * 7,
        "ee_observation_gain_by_scenario": {
            sc: int(
                comp[comp["cell"].str.startswith(sc)]["n_pairs_hff"].sum()
                - comp[comp["cell"].str.startswith(sc)]["n_pairs_clean"].sum()
            )
            for sc in ("S1", "S2", "S3", "S4")
        },
        "estimable_triples_clean": int((long["screen"] == "clean").sum()),
        "estimable_triples_hff": int((long["screen"] == "hff").sum()),
    }
    return long, comp, summary


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument(
        "--no-strict",
        dest="strict",
        action="store_false",
        help="report calibration failures without aborting (diagnosis only)",
    )
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("S034 -- Morris ranking under the clean vs hard-failure-free screen")
    long, comp, summary = analyse(args.strict)

    long.sort_values(["cell", "output", "screen", "input"]).to_csv(
        OUT_DIR / "mu_star_by_screen.csv", index=False, float_format="%.12g"
    )
    comp.to_csv(OUT_DIR / "rank_comparison.csv", index=False, float_format="%.12g")
    (OUT_DIR / "s034_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    s = summary
    print(f"\nRuns: clean screen {s['n_runs_clean_screen']}, "
          f"hard-failure-free {s['n_runs_hard_failure_free']}")
    print(f"Calibration: {s['n_published_rows_reproduced']} published rows reproduced, "
          f"max |delta| mu* = {s['calibration_max_abs_mu_star_delta_vs_published']:.3g}")
    print(f"Elementary-effect observations gained: {s['ee_observation_gain']} "
          f"(by scenario {s['ee_observation_gain_by_scenario']})")
    print(f"  Distinct pairs: {s['distinct_pairs_clean']} -> {s['distinct_pairs_hff']} "
          f"of a possible {s['distinct_pairs_ceiling']} (+{s['distinct_pair_gain']})")
    print(f"Estimable triples: clean {s['estimable_triples_clean']} -> "
          f"hff {s['estimable_triples_hff']}")
    print(f"\nCandidate set identical in {s['n_combinations_candidate_set_identical']} "
          f"of {s['n_combinations_total']} combinations")
    for r in s["combinations_with_candidate_change"]:
        print(f"    {r['cell']:<6} {r['output']:<6} gained [{r['inputs_gained']}] "
              f"lost [{r['inputs_lost']}]")

    print("\n  denominator                          n   top-1   top-3 set   top-3 order")
    for label, key in (
        ("all combinations", "criteria_all_combinations"),
        ("identical candidate set only", "criteria_identical_candidate_set_only"),
        ("S2_M only (seed-44 comparator)", "criteria_S2_M_only"),
        ("  of the 30: narrow 3rd/4th cut", "criteria_narrow_cut_margin"),
        ("  of the 30: wide 3rd/4th cut", "criteria_wide_cut_margin"),
    ):
        c = s[key]
        print(f"  {label:<34} {c['n']:>3} {c['top1_preserved']:>7} "
              f"{c['top3_set_preserved']:>11} {c['top3_order_preserved']:>13}")

    print(f"\n  Median 3rd/4th mu* cut margin: clean {s['median_cut_margin_clean']:.3f}, "
          f"relaxed {s['median_cut_margin_hff']:.3f} -- a changed top three is a "
          "reordering, not a tie")
    print("\n  H1 (top three carry at least half the summed mu*), by screen:")
    for label in ("clean", "hff"):
        h = s["h1_by_screen"][label]
        print(f"    {label:<5} {h['n_pass']}/{h['n_combinations']} pass, fraction "
              f"{h['fraction_min']:.3f} to {h['fraction_max']:.3f}, "
              f"median {h['fraction_median']:.3f}")

    print("\n" + s["framing"])
    print(f"\nWrote 3 artefacts to {OUT_DIR.relative_to(REPO)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
