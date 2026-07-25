# T1 anchor candidates — values to lock in the monograph

**Date:** 2026-07-25
**Purpose:** the nominative list the ledger extension will lock. Scope agreed:
T1 only (results derived from our own sweep data), presence-check only, in a
`monograph_anchor_map.md` separate from the paper crosswalk.

**How this list was built.** All numeric literals carrying a unit (%, mmHg, mL,
bpm, runs, cmH2O) were extracted from `preprint/manuscript.md`, code blocks
excluded. Each was matched **numerically** (1 % tolerance, to absorb display
rounding) against the ledger's anchor values. Matches were dropped, as were
lines carrying a citation marker, naming an external source, or stating a
methodological parameter.

> **Method correction, 2026-07-25.** The first pass of this list was wrong and
> was caught by its own spot-check. It collected anchored values from the
> ledger's `manuscript_value` column only, missing every value that appears in
> the `computed_value` column — so it flagged as "unanchored" a set of values
> that are in fact locked. Five of thirteen sampled entries were false
> positives (0.703 / 0.707 / 0.727, 143.6, 72.6, 0.351, 40.2). Reading both
> columns raises the collected anchor set from 143 to **184 values** and the
> triage below is rebuilt on that basis. The lesson is the one this project
> keeps relearning: a triage tool needs its own verification before its output
> is trusted.

**Counts (corrected).** 393 literals with units in the monograph · 184 distinct
anchored values collected from both ledger columns · **56 distinct candidates**
after numeric matching and the external/methodological filters · of these,
roughly **30 are genuine T1** once the remaining false positives are removed by
hand (Pulse validation tables at L442/L855/L3282-3284, NHANES vitals at L915,
the companion project at L2271, literature-bound rationale at L1002/L1054/L1060,
and inline derived arithmetic at L811-L815).

The groups below list the retained T1 values. **Entries struck from the first
pass because they turned out to be already anchored: 0.703 / 0.707 / 0.727,
143.6, 72.6, 0.351, 40.2.**

---

## Group A — Sensitivity structure (§3.2, §3.3)

| Line | Value | Claim |
|---|---|---|
| 60, 1636 | 31 / 48 cells (65 %) | CI-robustly linear (upper bootstrap CI below 0.6) |
| 1441, 1472, 1474 | μ* ≈ 500 mL | output Vt tracks input Vt in every cell |
| 1535 | 0.703 / 0.707 / 0.727 | lowest top-3 fractions (S4_M SpO2, S4_F PaO2, S4_M PaO2) |
| 217, 2882 | 17 / 18 · 2.40 / 3 · 90 % | SHAP-vs-Morris top-3 overlap |

## Group B — Divergence and the sex axis (§3.5, §3.6)

| Line | Value | Claim |
|---|---|---|
| 1748, 1755 | ~70 bpm | sympathetic overshoot above the input-range midpoint |
| 1800, 1801 | 110 / 90 bpm · 300 / 633 / 800 mL | composition of the mixed divergence cluster |
| 1827, 1828, 1835 | 71.4 · 71.1 · 60.7 mL/kg · ~0.4 % | per-kg blood volume, male vs female, and the floor |
| 1869, 1888 | 8.4 % · 4,400 mL | S018 BV bracket level |
| 1905 | 86 mL | female default below the male floor |
| 1954 | 2.5 % (4 / 160) | divergence rate in S1_M, S2_M, S3_M |
| 2008 | ~90 % | low-side extension of the instability band |

## Group C — Hyperoxia regime (§3.8, S021)

| Line | Value | Claim |
|---|---|---|
| 2268 | 505 · −25 mmHg · R² 0.90 | PaO2 vs FiO2 linear fit |
| 2275, 2276 | 228 · 481 mmHg | extrapolation from FiO2 = 0.5 to 1.0 |
| 2323, 2324 | 143.6 [93, 218] · 72.6 [71, 76] | S3 / S4 plateau medians and ranges |
| 2327 | 643 · 73 mmHg | plateau, healthy vs severe |
| 2335–2337 | 6 / 44 (14 %) · >700 · ~1,400 mmHg | runaway population |
| 2338 | Vt 633.3 mL × RR 20 | shared input signature of the six |
| 2342, 2343 | ~690 mmHg · 195 s · 220 s | runaway onset trajectory |
| 2538 | 600 – 650 mmHg | convergence band |

## Group D — VC-AC dyssynchrony (§3.8, S014)

| Line | Value | Claim |
|---|---|---|
| 2434, 2435, 3865 | 0.351 → 0.016 (96 %) · 1.826 → 0.018 | Vt CV collapse under the trigger lockout |

## Group E — Steady-state window audit (§3.8.1, S012)

| Line | Value | Claim |
|---|---|---|
| 2459–2465 | 0.20 bpm · 0.05 mmHg · 0.58 mmHg · 8.7 % · 0.09 mL · 4.3 mmHg · 40.2 mmHg | per-arm drift medians and rates |
| 2469 | 7.3 % | PaO2 drift exceedance, Vt-oscillation arm |
| 2526 | 147 – 158 bpm | mean HR in the >30 %-from-baseline cells |

## Group F — Cornish cross-comparison (§4)

| Line | Value | Claim |
|---|---|---|
| 2733 | 13 / 70 (18.6 %) · 4 / 78 | per-channel rejection counts |

## Group G — Steady-state deltas (§3.6)

| Line | Value | Claim |
|---|---|---|
| 2095 | 1 – 5 bpm · 13 – 36 mL | sex deltas, no larger than within-sex spread |
| 2104 | 4.7 – 5.1 mmHg | observed clinical-meaningfulness context |

---

## Rejected, with the reason

**Methodological parameters, not results (do not lock).** "95 % CI" (8
occurrences), the preregistered "≥ 75 %" convergence threshold, the flatline
tolerance "0.1 %", figure-caption percentages. These are settings, already
locked in the preregistration and in `src/detector.py`; a ledger anchor would
duplicate a guard that already exists at the source.

**External sources (out of scope by design).** Pulse's own validation tables
(0.07 / 1.01 / 2.25 % VC-AC; 11.3 / 15.3 / 25.3 % PC-AC), NHANES P50 vitals
(70 / 74 bpm, 118 / 113 mmHg), Pulse's documented default mapping
(199 / 150 / 119 mmHg), the companion project's ~7.8 mmHg per 0.01 FiO2, and
the literature values behind the hard bounds (22 / 18 / 25 mmHg). These cannot
be re-derived from our data. They need citation verification, a different tool.

**Arithmetic shown inline (already implied by anchored operands).** 71.4 =
4,802.63 / 67.3 · 403.8 = 6 × 67.3 · 13.33 = ⅔ × 20 · 0.8333 / 13.3333 =
0.0625. Both operands are anchored, so the quotient cannot drift without the
audit already failing.

**Definitional or physical constants.** SpO2 ≤ 100 %, the 760 mmHg sea-level
barometric pressure, the 700 mmHg alternative PaO2 ceiling.

---

## What this does not cover

The check confirms a value is **present** in the monograph. It does not confirm
the value is attached to the **right claim** — the failure mode found in the E6
misattribution, where correct numbers pointed at the wrong experiment. No static
text check can catch that. This list reduces the risk of silent numeric drift;
it does not replace critical reading.


---

# ARBITRATION (2026-07-25) — scope frozen at 14 targets

The author reviewed the groups above and retained 14 targets (~22 distinct
literals). Rejected: the rounded orders of magnitude (mu* ~= 500 mL, the
~600-650 mmHg convergence band), the illustrative clinical-context deltas
(1-5 bpm, 13-36 mL, 4.7-5.1 mmHg), the linear extrapolation (228 / 481 mmHg)
and the plateau read off a trajectory plot (~690 mmHg). Rationale: mechanically
freezing an approximation defeats the purpose of the guard.

| # | Target | Status |
|---|---|---|
| 2 | SHAP-vs-Morris top-3 overlap (90 %, 17/18, 2.40/3) | to verify — S023 |
| 3 | 86 mL, male floor vs female default | to verify — S018 |
| 4 | divergence-cluster composition (110/90 bpm, 633/800 mL) | **AMBIGUOUS — see below** |
| 5 | 71.1 mL/kg female, ~0.4 % per-kg gap | to verify — S018 |
| 6 | 60.7 mL/kg at the enforced floor | to verify — S018 |
| 7 | 8.4 % / 4,400 mL S018 bracket level | to verify — S018 |
| 8 | 2.5 % (4/160) divergence in S1_M, S2_M, S3_M | **VERIFIED EXACT** |
| 12 | 14 % (6/44) runaway population | to verify — S021 |
| 13 | Vt 633.3 mL x RR 20 runaway signature | to verify — S021 |
| 16 | 96 % Vt-CV reduction under trigger lockout | to verify — S014 |
| 17 | drift medians 0.05 / 0.58 / 0.09 | **VERIFIED** (0.0495 / 0.575 / 0.0869) |
| 18 | 8.7 % Vt exceedance, hyperoxia arm | **VERIFIED EXACT** |
| 19 | 7.3 % PaO2 exceedance, Vt-oscillation arm | **VERIFIED EXACT** |
| 20 | 18.6 % (13/70) Cornish rejection rate | to verify — S017 |

## Why each target must be re-derived before it is locked

An anchor freezes a value **and lends it the appearance of having been
verified**. Locking a wrong number is therefore worse than leaving it
unlocked: it converts an error into a permanent one carrying false
confidence. None of these 14 has ever been re-derived — that is precisely
why they are unanchored. Verification is a precondition, not a formality.

## The target-4 ambiguity, unresolved

Re-derivation confirms the diverged population holds HR in {50, 90, 110} bpm
and Vt in {300, **633.3**, 800} mL. Two problems before it can be locked:

1. The monograph writes "one at **633** mL"; the value is **633.3 mL**. The
   same quantity is written 633.3 elsewhere (target 13). One of the two is a
   rounding the guard would have to accommodate, or the text should be
   harmonised.
2. The sentence describes a **subset of four runs** ("one HR at 110 bpm, three
   at 90 bpm; two Vt at 300 mL, one at 633 mL, one at 800 mL") out of the 20
   diverged. Which four has not been established. Locking the numbers without
   confirming the subset would freeze a possibly-wrong description.

## Next session — resume here

1. Re-derive targets 2, 3, 5, 6, 7, 12, 13, 16, 20 against their artefacts
   (S018 blood volume, S021 hyperoxia, S014 trigger lockout, S023 SHAP,
   S017 Cornish).
2. Resolve target 4: identify the four-run subset and settle 633 vs 633.3.
3. Only then write `monograph_anchor_map.md` and the `--check-monograph`
   option, on the presence-check model agreed in the plan.
