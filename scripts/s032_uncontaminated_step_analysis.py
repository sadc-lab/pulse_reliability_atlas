"""S032 step 1 — uncontaminated-step sensitivity analysis (no new simulations).

Why
---
Pulse enforces DBP / SBP <= 0.75. The atlas applies that constraint when each
config is written, not when the Morris sample is drawn, so the sample geometry
stays intact (`src/sampler.py`, `src/scenario.py`). Supplement S3.7 quantifies
the cost: 9 of 20 diastolic steps are shortened, and in 8 of 20 systolic steps
the moving 0.75 x SBP ceiling drags the *applied* DBP along with SBP, so two
inputs change at once and the one-at-a-time assumption fails on those steps.

The published claim at risk is "output MAP is driven by SBP in every cell"
(paper Section 2.2): it rests partly on those contaminated steps. This script
tests whether the claim survives when they are removed. It answers only the
exclusion question; the signed decomposition of the contamination itself needs
the bridge probes (S032 step 4) and is not attempted here.

How
---
1. Calibration gate. Re-derive the nine published S3.7 counts from the
   canonical sample + master aggregate and abort unless all nine match. A
   silent disagreement here would mean this script and the audited ledger
   disagree about what "contaminated" means, and every number below would be
   plausible and wrong.
2. Contamination is derived from the *applied* values, never hard-coded.
3. Two estimators on the same clean-pair rule as the published Morris index:
     nominal        -- every clean pair (what the manuscript reports)
     uncontaminated -- clean pairs minus those where applied DBP co-varies
   and a stricter *paired* variant restricted to the trajectories whose
   systolic step is geometrically uncontaminated, so every input is estimated
   on the same trajectory subset.
4. Retention is reported per cell under both screens (strict four-flag clean
   and hard-failure-free), because a pooled count can hide a thin cell.

Usage::

    uv run python scripts/s032_uncontaminated_step_analysis.py

Exit status: 0 = calibration passed and the analysis ran; 1 = calibration
mismatch (nothing downstream is trustworthy); 2 = missing input artefact.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.aggregator import STAT_CHANNELS  # noqa: E402
from src.analysis_morris import derive_trajectory_pairs  # noqa: E402
from src.sampler import INPUT_NAMES, INPUT_SPECS  # noqa: E402
from src.scenario import PULSE_DBP_SBP_MAX_RATIO, iter_cells  # noqa: E402

SWEEP = REPO / "data" / "runs" / "full_sweep"
MASTER = SWEEP / "aggregated.parquet"
SAMPLE = SWEEP / "morris_sample.parquet"
OUT = REPO / "results" / "s032"

FLAGS = ["clamped", "diverged", "implausible", "not_steady_state"]
HARD_FLAGS = ["diverged", "implausible"]

# Published in Supplement S3.7, each one audited by a T5.clip.* ledger anchor.
# This script must reproduce all nine before any of its own numbers are read.
CALIBRATION = {
    "clipped_points": 35,
    "dbp_steps_shortened": 9,
    "dbp_steps_full": 11,
    "sbp_steps_contaminated": 8,
    "steps_intact": 123,
    "clean_dbp_pairs": 78,
    "clean_dbp_shortened": 41,
    "clean_sbp_pairs": 68,
    "clean_sbp_contaminated": 19,
}

SPEC = {s.name: (s.lo, s.hi) for s in INPUT_SPECS}


def _norm(name: str, v: float) -> float:
    lo, hi = SPEC[name]
    return (v - lo) / (hi - lo)


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Master aggregate + canonical Morris sample, with applied DBP attached."""
    if not MASTER.exists() or not SAMPLE.exists():
        print(f"[s032] missing artefact: {MASTER} / {SAMPLE}", file=sys.stderr)
        raise SystemExit(2)

    agg = pd.read_parquet(MASTER)
    if "clean" not in agg.columns:
        agg["clean"] = ~agg[FLAGS].any(axis=1)
    agg["hard_free"] = ~agg[HARD_FLAGS].any(axis=1)
    agg["idx"] = agg["case_id"].str.rsplit("_", n=1).str[1].astype(int)

    smp = pd.read_parquet(SAMPLE).sort_values(["trajectory", "point"]).reset_index(drop=True)
    smp["idx"] = range(len(smp))
    smp["dbp_applied"] = np.minimum(smp["dbp"], PULSE_DBP_SBP_MAX_RATIO * smp["sbp"])
    return agg, smp


def annotate_pairs(smp: pd.DataFrame) -> pd.DataFrame:
    """One row per Morris OAT step, tagged with how the clip touched it.

    ``shortened``   -- a diastolic step whose applied length differs from nominal.
    ``contaminated``-- a non-diastolic step during which applied DBP also moved,
                       i.e. a genuine one-at-a-time violation.
    """
    rows = []
    for p in derive_trajectory_pairs(smp):
        a, b = smp.loc[p.j_lo], smp.loc[p.j_hi]
        d_req = _norm("dbp", b["dbp"]) - _norm("dbp", a["dbp"])
        d_app = _norm("dbp", b["dbp_applied"]) - _norm("dbp", a["dbp_applied"])
        rows.append(
            {
                "trajectory": p.trajectory,
                "idx_lo": p.j_lo,
                "idx_hi": p.j_hi,
                "flipped": p.flipped_input,
                "delta": p.delta_normalized,
                "dbp_delta_requested": d_req,
                "dbp_delta_applied": d_app,
                # Applied-step denominator, matching audit_claims.py:3215 exactly:
                # only a diastolic flip gets the applied delta; every other input
                # is never clipped, so its applied step equals its nominal step.
                "delta_applied": d_app if p.flipped_input == "dbp" else p.delta_normalized,
                "shortened": p.flipped_input == "dbp" and abs(d_req - d_app) > 1e-9,
                "contaminated": p.flipped_input != "dbp" and abs(d_app) > 1e-9,
                "sbp_lo": float(a["sbp"]),
                "sbp_hi": float(b["sbp"]),
            }
        )
    return pd.DataFrame(rows)


def calibrate(agg: pd.DataFrame, smp: pd.DataFrame, pairs: pd.DataFrame) -> bool:
    """Reproduce the nine audited S3.7 counts. Print measured beside expected."""
    dbp_steps = pairs[pairs["flipped"] == "dbp"]
    sbp_steps = pairs[pairs["flipped"] == "sbp"]

    cd = cds = cs = css = 0
    for _, cell in agg.groupby(["scenario", "sex"]):
        ok = set(cell[cell["clean"]]["idx"])
        for r in pairs.itertuples():
            if r.idx_lo in ok and r.idx_hi in ok:
                if r.flipped == "dbp":
                    cd += 1
                    cds += int(r.shortened)
                elif r.flipped == "sbp":
                    cs += 1
                    css += int(r.contaminated)

    measured = {
        "clipped_points": int((smp["dbp_applied"] < smp["dbp"] - 1e-12).sum()),
        "dbp_steps_shortened": int(dbp_steps["shortened"].sum()),
        "dbp_steps_full": int((~dbp_steps["shortened"]).sum()),
        "sbp_steps_contaminated": int(sbp_steps["contaminated"].sum()),
        "steps_intact": int((~pairs["shortened"] & ~pairs["contaminated"]).sum()),
        "clean_dbp_pairs": cd,
        "clean_dbp_shortened": cds,
        "clean_sbp_pairs": cs,
        "clean_sbp_contaminated": css,
    }

    print("## Calibration gate — Supplement S3.7 (T5.clip.* ledger anchors)\n")
    print("| quantity | published | measured | |")
    print("|---|---|---|---|")
    ok_all = True
    for k, expected in CALIBRATION.items():
        got = measured[k]
        good = got == expected
        ok_all &= good
        print(f"| {k} | {expected} | {got} | {'PASS' if good else 'FAIL'} |")
    return ok_all


def elementary_effects(agg: pd.DataFrame, pairs: pd.DataFrame) -> pd.DataFrame:
    """Long-format clean elementary effects, one row per (cell, pair, output)."""
    rows = []
    for (sk, xk), cell in agg.groupby(["scenario", "sex"]):
        by_idx = cell.set_index("idx")
        clean = set(cell[cell["clean"]]["idx"])
        for r in pairs.itertuples():
            if r.idx_lo not in clean or r.idx_hi not in clean:
                continue
            lo, hi = by_idx.loc[r.idx_lo], by_idx.loc[r.idx_hi]
            for ch in STAT_CHANNELS:
                y_lo, y_hi = lo.get(f"{ch}_mean"), hi.get(f"{ch}_mean")
                if pd.isna(y_lo) or pd.isna(y_hi):
                    continue
                dy = float(y_hi) - float(y_lo)
                rows.append(
                    {
                        "scenario": sk,
                        "sex": xk,
                        "trajectory": r.trajectory,
                        "output": ch,
                        "input": r.flipped,
                        "ee": dy / r.delta,
                        "ee_app": (dy / r.delta_applied
                                   if abs(r.delta_applied) > 1e-9 else np.nan),
                        "contaminated": r.contaminated,
                    }
                )
    return pd.DataFrame(rows)


def mu_star(ee: pd.DataFrame, col: str = "ee") -> pd.DataFrame:
    """mu* = mean |EE| per (cell, output, input), with the pair count."""
    g = ee.dropna(subset=[col]).groupby(["scenario", "sex", "output", "input"])[col]
    return pd.DataFrame({"mu_star": g.apply(lambda s: s.abs().mean()), "n": g.size()}).reset_index()


def applied_table(ee: pd.DataFrame) -> pd.DataFrame:
    """Per (cell, output, input): mu* under the nominal and applied-step denominators.

    Mirrors ``audit_claims.py`` ``_clip_mu`` so the four audited applied-step
    figures can be reproduced before any new conclusion is drawn from it.
    """
    n = mu_star(ee, "ee").rename(columns={"mu_star": "nom"}).drop(columns="n")
    a = mu_star(ee, "ee_app").rename(columns={"mu_star": "app"}).drop(columns="n")
    return n.merge(a, on=["scenario", "sex", "output", "input"], how="inner")


def calibrate_applied(m: pd.DataFrame) -> bool:
    """Reproduce T5.clip.mustar_factor / dbp_enters_top3 / h1_applied_{median,min}."""
    dbp = m[m["input"] == "dbp"]
    factor = float((dbp["app"] / dbp["nom"]).median())
    enter, h1n, h1a = 0, [], []
    for _, g in m.groupby(["scenario", "sex", "output"]):
        if "dbp" in set(g.nlargest(3, "app")["input"]) and "dbp" not in set(
            g.nlargest(3, "nom")["input"]
        ):
            enter += 1
        h1n.append(g.nlargest(3, "nom")["nom"].sum() / g["nom"].sum())
        h1a.append(g.nlargest(3, "app")["app"].sum() / g["app"].sum())

    checks = [
        ("T5.clip.mustar_factor", 2.368, factor, 5e-4),
        ("T5.clip.dbp_enters_top3", 9, enter, 0),
        ("T5.clip.h1_applied_median", 0.9098, float(np.median(h1a)), 5e-5),
        ("T5.clip.h1_applied_min", 0.696, float(np.min(h1a)), 5e-4),
    ]
    print("## Calibration gate 2 — applied-step machinery (T5.clip.* anchors)\n")
    print("| anchor | audited | measured | |")
    print("|---|---|---|---|")
    ok = True
    for name, exp, got, tol in checks:
        good = abs(got - exp) <= tol
        ok &= good
        print(f"| {name} | {exp} | {got:.6g} | {'PASS' if good else 'FAIL'} |")
    return ok


def ranked(mu: pd.DataFrame, output: str) -> pd.DataFrame:
    """Rank inputs by mu* within each cell for one output (1 = most influential)."""
    sub = mu[mu["output"] == output].copy()
    sub["rank"] = sub.groupby(["scenario", "sex"])["mu_star"].rank(ascending=False, method="min")
    return sub


def main() -> int:
    agg, smp = load_inputs()
    pairs = annotate_pairs(smp)

    if not calibrate(agg, smp, pairs):
        print("\n[s032] CALIBRATION FAILED — this script disagrees with the audited")
        print("[s032] ledger about what 'contaminated' means. Nothing below is usable.")
        return 1
    print("\nCalibration passed on 9/9 quantities.\n")

    OUT.mkdir(parents=True, exist_ok=True)
    pairs.to_csv(OUT / "morris_step_contamination.csv", index=False)

    ee = elementary_effects(agg, pairs)
    mu_nom = mu_star(ee).assign(estimator="nominal")

    # Second calibration, against a different instrument. The nominal estimator
    # here must reproduce the published Morris index bit-for-bit; if it does
    # not, this script's EE machinery is wrong and every column below with it.
    published = REPO / "results" / "morris_indices.parquet"
    if published.exists():
        pub = pd.read_parquet(published)[["scenario", "sex", "output", "input", "mu_star"]]
        j = pub.merge(
            mu_nom[["scenario", "sex", "output", "input", "mu_star"]],
            on=["scenario", "sex", "output", "input"],
            suffixes=("_pub", "_here"),
            how="outer",
            indicator=True,
        )
        unmatched = int((j["_merge"] != "both").sum())
        both = j[j["_merge"] == "both"]
        worst = float((both["mu_star_pub"] - both["mu_star_here"]).abs().max())
        print("## Cross-instrument check vs results/morris_indices.parquet\n")
        print(f"- rows compared: {len(both)}   unmatched: {unmatched}")
        print(f"- max |mu*_published - mu*_here| = {worst:.3e}")
        if unmatched or not np.isclose(worst, 0.0, atol=1e-9):
            print("\n[s032] NOMINAL ESTIMATOR DOES NOT REPRODUCE THE PUBLISHED INDEX.")
            return 1
        print("- exact agreement; the EE machinery here is the published one.")
        # Account for every missing cell x output x input combination rather
        # than assuming which ones they are.
        full = {
            (sk, xk, o, i)
            for sk, xk in iter_cells()
            for o in STAT_CHANNELS
            for i in INPUT_NAMES
        }
        have = set(map(tuple, both[["scenario", "sex", "output", "input"]].to_numpy()))
        missing = sorted(full - have)
        inputs_missing = sorted({m[3] for m in missing})
        cells_missing = sorted({f"{m[0]}_{m[1]}" for m in missing})
        print(f"- grid is {len(full)}; {len(missing)} combinations absent, "
              f"all on input(s) {inputs_missing}, in cell(s) {cells_missing}.\n")
    else:
        print(f"[s032] WARNING: {published} absent -- cross-instrument check SKIPPED.\n")

    mu_unc = mu_star(ee[~ee["contaminated"]]).assign(estimator="uncontaminated")

    # Paired variant: keep only trajectories whose systolic step is
    # geometrically uncontaminated, then re-estimate every input on that same
    # subset, so SBP is not compared against inputs measured on more data.
    bad_traj = set(pairs[pairs["contaminated"]]["trajectory"])
    good_traj = sorted(set(pairs["trajectory"]) - bad_traj)
    mu_pair = mu_star(ee[ee["trajectory"].isin(good_traj)]).assign(estimator="paired")

    allmu = pd.concat([mu_nom, mu_unc, mu_pair], ignore_index=True)
    allmu.to_csv(OUT / "mu_star_by_estimator.csv", index=False)

    print(f"Trajectories with an uncontaminated systolic step: "
          f"{len(good_traj)} of {pairs['trajectory'].nunique()}\n")

    # ---- The claim under test: is SBP still rank 1 for MAP in every cell? ----
    print("## SBP -> MAP, per cell, under each estimator\n")
    print("A rank of 1 is only meaningful next to its margin, so the runner-up "
          "input and the mu* ratio to it are reported under each estimator.\n")
    print("| cell | clean SBP pairs | contaminated | remaining | SBP levels kept "
          "| mu* nominal | rank | mu* uncontam. | rank | runner-up | ratio "
          "| mu* paired | rank | runner-up | ratio |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")

    r_nom, r_unc, r_par = (ranked(m, "MAP") for m in (mu_nom, mu_unc, mu_pair))
    sbp_pairs = pairs[pairs["flipped"] == "sbp"]
    summary = []
    for sk, xk in iter_cells():
        cell = agg[(agg["scenario"] == sk) & (agg["sex"] == xk)]
        clean = set(cell[cell["clean"]]["idx"])
        kept = [r for r in sbp_pairs.itertuples() if r.idx_lo in clean and r.idx_hi in clean]
        contam = [r for r in kept if r.contaminated]
        rest = [r for r in kept if not r.contaminated]
        levels = sorted({r.sbp_lo for r in rest} | {r.sbp_hi for r in rest})

        def pick(tbl: pd.DataFrame) -> tuple[float, float, str, float]:
            """(mu* of SBP, its rank, the runner-up input, mu*_SBP / mu*_runner-up)."""
            c = tbl[(tbl["scenario"] == sk) & (tbl["sex"] == xk)].sort_values(
                "mu_star", ascending=False
            )
            row = c[c["input"] == "sbp"]
            if row.empty:
                return float("nan"), float("nan"), "-", float("nan")
            m, rk = float(row["mu_star"].iloc[0]), float(row["rank"].iloc[0])
            others = c[c["input"] != "sbp"]
            if others.empty:
                return m, rk, "-", float("nan")
            up, um = str(others["input"].iloc[0]), float(others["mu_star"].iloc[0])
            return m, rk, up, (m / um if um > 0 else float("inf"))

        mn, rn, _, _ = pick(r_nom)
        mu_, ru, up_u, ra_u = pick(r_unc)
        mp, rp, up_p, ra_p = pick(r_par)
        lv = "/".join(f"{v:g}" for v in levels)
        print(f"| {sk}_{xk} | {len(kept)} | {len(contam)} | {len(rest)} | {lv} "
              f"| {mn:.3g} | {rn:.0f} | {mu_:.3g} | {ru:.0f} | {up_u} | {ra_u:.1f}x "
              f"| {mp:.3g} | {rp:.0f} | {up_p} | {ra_p:.1f}x |")
        summary.append(
            {
                "scenario": sk, "sex": xk,
                "clean_sbp_pairs": len(kept), "contaminated": len(contam),
                "remaining": len(rest), "sbp_levels_kept": lv,
                "mu_star_nominal": mn, "rank_nominal": rn,
                "mu_star_uncontaminated": mu_, "rank_uncontaminated": ru,
                "runner_up_uncontaminated": up_u, "ratio_uncontaminated": ra_u,
                "mu_star_paired": mp, "rank_paired": rp,
                "runner_up_paired": up_p, "ratio_paired": ra_p,
                "delta_pct": 100.0 * (mu_ - mn) / mn if mn else float("nan"),
                "n_clean": int(cell["clean"].sum()),
                "n_hard_free": int(cell["hard_free"].sum()),
                "n_total": int(len(cell)),
            }
        )

    sm = pd.DataFrame(summary)
    sm.to_csv(OUT / "sbp_map_dominance.csv", index=False)

    print("\n## Retention per cell (both screens)\n")
    print("| cell | strict four-flag clean | hard-failure-free | total |")
    print("|---|---|---|---|")
    for r in sm.itertuples():
        print(f"| {r.scenario}_{r.sex} | {r.n_clean} | {r.n_hard_free} | {r.n_total} |")
    print(f"| **total** | **{sm['n_clean'].sum()}** | **{sm['n_hard_free'].sum()}** "
          f"| **{sm['n_total'].sum()}** |")

    print("\n## Verdict\n")
    for est, col in (("nominal", "rank_nominal"),
                     ("uncontaminated", "rank_uncontaminated"),
                     ("paired", "rank_paired")):
        first = int((sm[col] == 1).sum())
        print(f"- SBP ranks first for MAP in {first} of 8 cells under the {est} estimator.")

    # The SBP row is identical under 'uncontaminated' and 'paired' by
    # construction: each trajectory contains exactly one systolic step, so
    # dropping the contaminated pairs and dropping their trajectories remove the
    # same SBP elementary effects. The two differ only for the other six inputs,
    # which the paired estimator also restricts to those 12 trajectories -- that
    # is what makes the comparison fair, and it is why the runner-up can move.
    same = bool(np.allclose(sm["mu_star_uncontaminated"], sm["mu_star_paired"], equal_nan=True))
    print(f"- SBP mu* identical under uncontaminated and paired: {same} "
          "(expected: one systolic step per trajectory).")

    down = int((sm["delta_pct"] < 0).sum())
    print(f"- Removing the contaminated pairs LOWERS mu*(SBP->MAP) in {down} of 8 cells "
          f"(median change {sm['delta_pct'].median():+.1f}%, "
          f"range {sm['delta_pct'].min():+.1f}% to {sm['delta_pct'].max():+.1f}%).")
    print("  Direction is consistent with upward contamination, but it is NOT proof:")
    print("  the contaminated steps sit at the low-SBP end, so the change is confounded")
    print("  with position in the sampled space (the same confound Supplement S3.7 states")
    print("  for diastolic step length). Only the bridge probes can separate the two.")

    thin = sm[sm["remaining"] < 8]
    if len(thin):
        cells_s = ", ".join(f"{r.scenario}_{r.sex}({r.remaining})" for r in thin.itertuples())
        print(f"- THIN CELLS: {len(thin)} of 8 rest on fewer than 8 uncontaminated systolic")
        print(f"  pairs -- {cells_s}. mu* point estimates there are weak; the rank is")
        print("  carried by the margin to the runner-up, not by the pair count.")

    # ---------------- Combined estimator: the worst case for the claim ----------
    # SBP decontaminated AND DBP on the applied-step denominator, simultaneously.
    # Neither Supplement S3.7 nor the published index evaluates this pair together.
    m = applied_table(ee)
    print("\n")
    if not calibrate_applied(m):
        print("\n[s032] APPLIED-STEP CALIBRATION FAILED — combined estimator not reported.")
        return 1
    print("\nApplied-step calibration passed on 4/4 anchors.\n")

    mu_hyb = mu_star(ee[~ee["contaminated"]], "ee_app")
    mu_cpr = mu_star(ee[ee["trajectory"].isin(good_traj)], "ee_app")
    r_hyb, r_cpr = ranked(mu_hyb, "MAP"), ranked(mu_cpr, "MAP")

    def val(tbl: pd.DataFrame, sk: str, xk: str, inp: str, col: str = "mu_star",
            output: str | None = "MAP") -> float:
        """One scalar from a mu*/rank table.

        ``output`` MUST be given for any table that still holds every channel;
        pass None only for tables already restricted to a single output (the
        ``ranked()`` results). Omitting it silently returned the alphabetically
        first channel (HR) instead of MAP.
        """
        row = tbl[(tbl["scenario"] == sk) & (tbl["sex"] == xk) & (tbl["input"] == inp)]
        if output is not None:
            if "output" not in row.columns:
                raise KeyError(f"table has no 'output' column but output={output!r} requested")
            row = row[row["output"] == output]
        if len(row) != 1:
            return float("nan")
        return float(row[col].iloc[0])

    print("## Combined estimator on MAP — exact per-cell thresholds\n")
    print("DBP overtakes SBP exactly when f_c > f_flip, where "
          "f_c = mu*_applied(DBP) / mu*_nominal(DBP) and "
          "f_flip = mu*_uncontaminated(SBP) / mu*_nominal(DBP).\n")
    print("| cell | mu* SBP nom | mu* SBP uncont. | mu* DBP nom | mu* DBP applied "
          "| f_c | f_flip | flips? | SBP/DBP margin | runner-up | margin to runner-up "
          "| rank hybrid | rank paired |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")

    comb = []
    for sk, xk in iter_cells():
        s_nom = val(mu_nom, sk, xk, "sbp")
        s_unc = val(mu_unc, sk, xk, "sbp")
        d_nom = val(m[m["output"] == "MAP"].rename(columns={"nom": "mu_star"}), sk, xk, "dbp")
        d_app = val(m[m["output"] == "MAP"].rename(columns={"app": "mu_star"}), sk, xk, "dbp")
        f_c = d_app / d_nom if d_nom else float("nan")
        f_flip = s_unc / d_nom if d_nom else float("nan")
        flips = bool(f_c > f_flip)
        rh = val(r_hyb, sk, xk, "sbp", "rank")
        rp2 = val(r_cpr, sk, xk, "sbp", "rank")
        margin = s_unc / d_app if d_app else float("nan")
        # The SBP-to-DBP margin is only the decisive one if DBP is actually the
        # runner-up under this estimator. In two cells HR outranks DBP under the
        # nominal estimator, so the true margin must be taken against whichever
        # input is second, not against DBP by assumption.
        cell_h = mu_hyb[(mu_hyb["scenario"] == sk) & (mu_hyb["sex"] == xk)
                        & (mu_hyb["output"] == "MAP")].sort_values("mu_star", ascending=False)
        oth = cell_h[cell_h["input"] != "sbp"]
        up2 = str(oth["input"].iloc[0]) if len(oth) else "-"
        up2_mu = float(oth["mu_star"].iloc[0]) if len(oth) else float("nan")
        true_margin = s_unc / up2_mu if up2_mu else float("nan")
        print(f"| {sk}_{xk} | {s_nom:.4g} | {s_unc:.4g} | {d_nom:.4g} | {d_app:.4g} "
              f"| {f_c:.3f} | {f_flip:.3f} | {'**YES**' if flips else 'no'} "
              f"| {margin:.2f}x | {up2} | {true_margin:.2f}x | {rh:.0f} | {rp2:.0f} |")
        comb.append({"scenario": sk, "sex": xk, "mu_sbp_nominal": s_nom,
                     "mu_sbp_uncontaminated": s_unc, "mu_dbp_nominal": d_nom,
                     "mu_dbp_applied": d_app, "f_c": f_c, "f_flip": f_flip,
                     "dbp_overtakes": flips, "sbp_to_dbp_margin": margin,
                     "runner_up_combined": up2, "margin_to_runner_up": true_margin,
                     "rank_sbp_hybrid": rh, "rank_sbp_combined_paired": rp2})

    cdf = pd.DataFrame(comb)
    cdf.to_csv(OUT / "combined_estimator_MAP.csv", index=False)

    # Internal consistency: the f_c > f_flip test and the hybrid rank are two
    # independent routes to the same fact. A disagreement means one of them is
    # reading the wrong row -- which is exactly how the output-column bug in an
    # earlier revision of this script was caught. Never report past it.
    bad = cdf[(cdf["dbp_overtakes"]) != (cdf["rank_sbp_hybrid"] != 1)]
    if len(bad):
        print("\n[s032] INTERNAL CONTRADICTION between the f_c threshold test and the")
        print("[s032] hybrid rank, in cell(s): "
              + ", ".join(f"{r.scenario}_{r.sex}" for r in bad.itertuples()))
        return 1
    print("\n- Consistency: f_c > f_flip agrees with the hybrid rank in 8 of 8 cells.")
    # Applied-step alone. Supplement S3.7 asserts in prose that MAP stays
    # SBP-dominated under this estimator; it follows from the combined result,
    # but an inference is not a measurement, so measure it.
    r_app = ranked(mu_star(ee, "ee_app"), "MAP")
    app_first = sum(1 for sk, xk in iter_cells() if val(r_app, sk, xk, "sbp", "rank") == 1)
    print(f"\n- SBP ranks first for MAP in {app_first} of 8 cells under the applied-step "
          "estimator alone (independent check on the S3.7 prose claim).")
    print(f"- SBP ranks first for MAP in {int((cdf['rank_sbp_hybrid'] == 1).sum())} of 8 "
          "cells under the hybrid combined estimator (severe reviewer reconstruction).")
    print(f"- SBP ranks first for MAP in {int((cdf['rank_sbp_combined_paired'] == 1).sum())} "
          "of 8 cells under the paired combined estimator (like-for-like subsets).")
    print(f"- Cells where DBP overtakes: {int(cdf['dbp_overtakes'].sum())} of 8.")

    print(f"\nArtefacts written to {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
