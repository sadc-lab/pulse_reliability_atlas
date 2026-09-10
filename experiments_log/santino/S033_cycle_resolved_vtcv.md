---
id: S033
author: santino
date: 2026-09-09
status: done
tags: [aliasing, steady-state-classifier, tidal-volume, trigger-lockout, reviewer-response, post-hoc, estimand-sensitivity]
linked_code:
  - preprint_npj/supplement.tex
  - src/detector.py
  - data/runs/full_sweep/*/output_pulse_native.csv
  - data/runs/s014_trigger_lockout/*_lock/output_pulse_native.csv
---

# S033 — Cycle-resolved check of the 5-second delivered-Vt CV

---

## Why this session happened

A reviewer objected (point 3.9) that the delivered-Vt coefficient of variation
that drives the `not_steady_state` flag is computed from samples taken every
5 s, i.e. at 0.2 Hz, on a signal whose breath rate is near 0.25 Hz. The
classifier statistic is therefore below the rate needed to resolve
breath-to-breath dynamics, and its magnitude may depend on sampling phase.
The reviewer asked for statistics computed per respiratory cycle rather than an
appeal to the Nyquist criterion on a figure.

The objection was answerable **without any new simulation**: Pulse's native
50 Hz output (`output_pulse_native.csv`) was already recorded for every run of
the sweep, and for all 64 trigger-lockout reruns of S014.

## Method

- Window: the locked steady-state window, [60, 120] s in classifier-relative
  time, which is **[180, 240] s in the native absolute time base**. The offset
  `t_native = t_relative + 120` was confirmed by value identity on two
  independent channels (HR and delivered Vt) in two different cells.
- Cycle segmentation: the native `TidalVolume` channel is a **step function**
  (constant within a breath), so cycles are recovered as change points. The
  count was validated against the measured respiratory rate on three runs
  (24 vs 25.7 /min; 26 vs 25.4; 22 vs 20.7 — within 7 %).
- Threshold: the locked `CV_THRESHOLD = 0.05`, strict `>`, unchanged. Float
  tolerance was applied **only** to the time-window comparison, never to the
  threshold. (Filtering on `t <= 120` excludes the last sample, stored as
  120.0000000000557, and shifts the CV from 0.3508 to 0.3654.)
- Instrument calibration: the pipeline reproduces the three published values —
  median default CV 0.3509 (published 0.351), median locked CV 0.0156
  (published 0.016), and 78.1 % of locked reruns below threshold (published
  78.1 %).

## Result — full sweep

1,260 runs carry both files (the 20 missing are the diverged runs, which
produce no CSV; all 20 are on the male body, matching the published count).

| | count |
|---|---|
| flagged by both resolutions | 297 |
| flagged by neither | 942 |
| crossing only at cycle resolution | 15 |
| crossing only under the 5-second statistic | 6 |

Agreement: **1,239 / 1,260 = 98.3 %**.

Of the 15 cycle-only crossings, ten fall below a factor of 3; five are
substantial (4.0, 6.7, 7.1, 15.8, 113.9).

**Counterfactual effect on the locked count.** Six of the 15 are already
flagged by another channel or criterion; three of the six 5-second-only
crossings would lose their flag entirely. Net **+6**: `not_steady_state` would
move from 530 to 536 (+1.1 %). The locked classification is unchanged.

## Result — 64 paired trigger-lockout configurations

Variability decreases after lockout in **64 of 64 pairs at both resolutions**.
Four descriptive summaries, on the same 63 configurations with a non-zero
post-lockout cycle-level CV:

| summary | 5-second | cycle-resolved | relative gap |
|---|---|---|---|
| ratio of group medians | 21.42 | 22.67 | 5.81 % |
| median of paired ratios | 27.84 | 25.63 | 8.65 % |
| difference of group medians | 0.3345 | 0.3224 | 3.75 % |
| median of paired differences | 0.3256 | 0.3275 | 0.58 % |

**The direction is not consistent**: two summaries make the 5-second statistic
overstate the intervention effect, two make it understate it. Reporting only
the most concordant summary (0.58 %) would have been a post-hoc selection of
the favourable estimand; all four are therefore reported.

`S1_F_0016` is excluded from the **ratio** summaries only. After lockout its
delivered volume is 819.027985 mL at every breath to the precision of the
recorded trace, so the post-lockout CV is zero at that resolution and no finite
ratio exists. It respires at 20 /min — the constancy is of the delivered
volume, not an absence of breaths. That zero is observed, not imputed.

## Recorded but NOT carried into the supplement

**Sex distribution of the disagreements.** Thirteen of the 15 cycle-only
crossings fall on the female reference body, against 2 on the male, on a base
of 640 female and 620 male runs analysed. The 6 five-second-only crossings
split 4 F / 2 M. All five substantial cases are female.

Only the last of these (all five substantial cases female) is stated in
Supplement §S8. The 13 / 2 split is recorded here and deliberately kept out of
the supplement: it is a new observation on an axis the paper already treats
separately (solver divergence, which is 20/20 male), no test was preregistered
for it, and grafting it onto a section answering an aliasing objection would
blur that answer. Decision taken with the maintainer, 2026-09-09.

## Limits

- Cycle counting is a change-point method: on runs whose delivered volume is
  numerically constant it recovers one plateau, and on near-flat runs it can
  count numerical noise. Nine runs across the sweep are in the constant class.
- The classifier criteria were **recomputed** here, not read back from the
  stored flags in `aggregated.parquet`. The supplement records that this
  reconstruction reproduces the stored flag on 1,280 / 1,280 runs, which
  validates the method, but a direct comparison against the stored flags was
  not run in this session.
- Everything here is post hoc. The preregistered classifier, its threshold and
  all published counts are unchanged.

## Defects found in this session's own work

- An awk array indexed by an uninitialised counter used the empty string as a
  key, silently dropping one of thirteen samples and producing a constant
  CV = 0.2887 across every channel. Caught because the value was physically
  impossible, not because the code looked wrong.
- An intermediate file written with `%.6f` rounded CVs of 1.66e-10 and 1.35e-07
  to `0.000000`, which excluded two configurations as division-by-zero and
  shifted the median of paired ratios from 25.63 to 23.33. Regenerated at
  `%.12g`.

---

## Addendum 2026-09-10 — out-of-sample evaluation of the SHAP surrogate (S023)

Reviewer point 3.11 objected that the RandomForest surrogate carried no
out-of-sample evaluation. It now does, and the trajectory grouping matters.

**Mapping, verified not assumed.** `morris_sample.parquet` holds the 160-point
design in sweep order, so the numeric suffix of `case_id` indexes it directly.
`attach_trajectory()` asserts this on all 1,280 rows across all seven inputs and
aborts otherwise. It DID abort on the first run: `dbp` disagreed on 280 rows.
That is not a mapping error — it is the preregistered pulse-pressure clip, which
Supplement S3-clip-cost puts at 35 of the 160 sampled points, identical in all
eight cells: 35 x 8 = 280 exactly. The guard now asserts that count rather than
waiving the input, so a real drift would still fail.

**Results.** Grouping withholds four complete trajectories at a time.

| output | training | out-of-bag | grouped (mean ± sd) | worst fold |
|---|---|---|---|---|
| Vt | 0.99997 | 0.9998 | 0.9995 ± 0.0004 | 0.9989 |
| HR | 0.9995 | 0.9964 | 0.9917 ± 0.0024 | 0.9880 |
| MAP | 0.9993 | 0.9952 | 0.9402 ± 0.0253 | 0.8949 |
| SpO2 | 0.9941 | 0.9578 | 0.8736 ± 0.0532 | 0.7743 |
| PaCO2 | 0.9942 | 0.9601 | 0.8734 ± 0.0705 | 0.7433 |
| PaO2 | 0.9930 | 0.9494 | 0.8716 ± 0.0562 | 0.7873 |

The out-of-bag optimism (0.0003 for Vt up to 0.087 for PaCO2) tracks the
fold-to-fold spread: negligible where one input nearly determines the output,
largest for the three blood-gas channels that depend on several inputs jointly.

**The worst-fold column is recorded here and deliberately NOT published.**
`GroupKFold` does not shuffle: it produces one deterministic partition, so 0.7433
is the worst of *that* split, not a bound. Reproducible is not the same as
robust. Only mean ± sd went into Supplement §S13. A defensible floor would need
repeated random group partitions (`GroupShuffleSplit`); decided against with the
maintainer on 2026-09-10, since the reviewer asked for an out-of-sample estimate,
not a floor, and that would add a protocol nobody preregistered.

**Seed-robustness of the "SHAP is near-constant per cell" finding.**

| RF seed | distinct SHAP top-3 sets over the 8 cells | full match |
|---|---|---|
| 42 (locked) | 9 | 23/48 |
| 7 | 10 | 23/48 |
| 999 | 10 | 23/48 |

Morris yields 25 distinct sets over the same cells. The exact count therefore
moves between 9 and 10 with the forest seed, so §S13 states the contrast ("about
a dozen against 25") rather than the exact figure. **The published 23/48 is
identical across all three seeds** — the agreement statistic itself does not
depend on the surrogate's randomness. Results at the locked seed were restored
and byte-compared against a backup after the test.

**Ledger.** Six anchors added, `T2.s023.r2_grouped_*`, one per output. Ledger
total 388 -> 394; the 25 head-line counters were updated in the same pass. Two
crosswalk counts were bumped for the new subsection (`1{,}280` 43 -> 44,
`20 trajectories` 6 -> 7), and the phrase "five-fold" was avoided because the
sex-divergence guard bans that literal outright after a withdrawn fold-change
claim.
