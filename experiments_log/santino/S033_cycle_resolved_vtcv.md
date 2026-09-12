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
  (24 vs 25.7 /min; 26 vs 25.4; 22 vs 20.7 — within 7 %). ⚠️ **Those three runs
  are a favourable sample.** On all 1,251 non-constant runs the median
  disagreement is 5.4 %, the 95th percentile 38 % and the maximum 95 %; see the
  2026-09-12 addendum, which also measures whether any verdict rests on it.
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
| ratio of group medians | 21.42 | 22.66 † | 5.81 % |
| median of paired ratios | 27.84 | 25.63 | 8.65 % |
| difference of group medians | 0.3345 | 0.3224 | 3.73 % |
| median of paired differences | 0.3256 | 0.3275 | 0.59 % |

† Re-derivation on 2026-09-12 gives 22.6648553684, which displays as **22.66**.
Supplement Table S8 publishes **22.67**; that discrepancy is open and
registered in `audit/s033_estimand_rounding_mismatch.md`. The two relative-gap
figures in the last column that were corrected on the same date (3.75 → 3.73,
0.58 → 0.59) are documented in the 2026-09-12 addendum below.

**The direction is not consistent**: two summaries make the 5-second statistic
overstate the intervention effect, two make it understate it. Reporting only
the most concordant summary (0.59 %) would have been a post-hoc selection of
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
  ⚠️ **The nine are not the whole affected population.** Segmentation also
  merges two consecutive breaths that deliver a numerically identical volume,
  which under-counts cycles without the run being constant: 126 runs disagree
  with the reported respiration rate by more than 20 %. The 2026-09-12 addendum
  measures the consequence and finds the published split robust to it.
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

---

## Addendum 2026-09-12 — the analysis is now reproducible, and one published digit is wrong

The two blocks above were computed with `awk` pipelines in a session scratchpad
that was not kept. On 2026-09-10 that was recorded as a reproducibility debt:
twelve published values with no versioned producer, no artefact under
`results/`, and no entry in the ledger. This addendum closes it.

### What was built

* `scripts/s033_cycle_resolved_vtcv.py` — re-derives everything from
  `data/runs/`. It reads no value back from the supplement, so it can
  contradict it.
* `results/s033/` — five artefacts: `sweep_cycle_vt_cv.csv` (one row per
  analysed run), `sweep_confusion.json`, `lockout_paired_cv.csv`,
  `lockout_estimands.csv`, `s033_summary.json`.
* `check_s033_cycle_resolved()` in `scripts/audit_claims.py` — **38 checks**,
  in three layers: transcription against `supplement.tex`, internal arithmetic
  of the artefact, and cross-instrument comparison against
  `data/runs/full_sweep/aggregated.parquet`, which this script did not write.
  A guard rather than ledger anchors, because the subsection carries more than
  twenty numbers and each anchor forces a rewrite of the 25 head-line counters
  in two documents.

The script carries four calibration controls and aborts on any of them: the
reconstructed four-flag classification equals the stored flags on all 1,280
runs; the stored `not_steady_state` total is 530; the 20 runs without CSVs are
exactly the stored `diverged` set; and the 64 lockout pairs reproduce the three
published S014 headline values. The recomputed 5-second Vt CV also equals the
stored `Vt_cv` on all 1,260 runs — two independent code paths agreeing, which
is worth more than one careful path.

### Everything published reproduces, except one digit

Re-derived and identical to the published figures: 1,260 runs with both files;
297 / 942 / 15 / 6; 1,239 of 1,260 = 98.3 %; the factor list, whose substantial
five are 4.03, 6.69, 7.10, 15.77 and 113.93 and are all female; nine
constant-volume runs; 6 already flagged otherwise and 3 that would lose the
flag, so 530 → 536 (+1.13 %); 64/64 decreases at both resolutions; the 63/64
split; S1\_F\_0016's 819.027985 mL; and seven of the eight table values.

**The eighth is wrong.** The cycle-resolved ratio of group medians is
0.337325 / 0.0148832 = **22.6648553684**, which displays as **22.66**, not the
published 22.67. It sits 0.00015 below the 22.665 boundary, so rounding once to
three decimals and again to two produces 22.67. Recorded in
`audit/s033_estimand_rounding_mismatch.md`; `supplement.tex` is **unmodified**,
pending the maintainer's decision, and the guard reports the row as OPEN with a
premise it re-verifies every run.

### Two figures in this notebook were wrong, and are corrected above

Two of the four entries in the "relative gap" column are wrong. That is the
measured fact. The *mechanism* below is reconstructed, not observed — the awk
pipelines are gone — but the arithmetic is consistent with only one story:
recomputing each gap from the **displayed** two- and four-decimal values
reproduces the published 3.75 % and 0.58 % exactly, while the unrounded values
give 3.73 % and 0.59 %. Two of the four entries therefore appear to have been
taken from the table's own display rather than from the data behind it, and the
other two (5.81 %, 8.65 %) from the unrounded values:

| summary | was | is |
|---|---|---|
| difference of group medians | 3.75 % | **3.73 %** |
| median of paired differences | 0.58 % | **0.59 %** |

Both are corrected in the table above. Neither reaches the supplement, which
states only the range: with the corrected values that range is 0.59 % to
8.65 %, which still rounds to the published "0.6 % to 8.6 %".

### The cycle-count validation was weaker than it reads

The Method section above says the recovered cycle count "was validated against
the measured respiratory rate on three runs (24 vs 25.7 /min; 26 vs 25.4;
22 vs 20.7 — within 7 %)". Over all **1,251** non-constant runs the median
relative disagreement is **5.4 %**, but the 95th percentile is **38 %** and the
maximum **95 %**. Three runs within 7 % was a favourable sample, not a bound.

The mechanism is not noise: change-point segmentation merges two consecutive
breaths that deliver a numerically identical volume, so it recovers fewer
values than there were breaths, and it under-weights a repeated — that is,
stable — volume. That biases the CV **upward**. The per-run
`rr_mean_5s` and `n_cycles` columns are now in the artefact, so this is
checkable on every run rather than on three.

**126 runs** disagree by more than 20 %, and **4 of the 21** verdict
disagreements fall on them (S1\_F\_0074, S1\_F\_0077, S2\_F\_0110,
S3\_F\_0118), all four cycle-only crossings.

### Sensitivity analysis — the published split is not an artefact of merging

Scoring the same window on **every** native 50 Hz sample weights each recorded
volume by how long it persists, which at a fixed breath length is per-breath
weighting and is immune to the merging bias above. Result:

| | published (change-point) | sensitivity (all samples) |
|---|---|---|
| flagged by both | 297 | 295 |
| flagged by neither | 942 | 945 |
| cycle-only | 15 | 12 |
| 5-second-only | 6 | 8 |
| agreement | 98.33 % | **98.41 %** |

The two cycle-level estimators disagree on **9 of 1,260 runs**. Had the
published 15 / 6 split been manufactured by merging, this estimator would have
collapsed it; it does not. The published conclusion is also conservative in the
right direction: correcting the upward bias moves agreement *up* and the
counterfactual delta *down*.

Kept in `results/s033/` and here, **deliberately not carried into the
supplement**: it answers a question the reviewer did not ask, and adding a
third estimator to a subsection whose point is that the choice of estimand
matters would need the maintainer's decision, not mine. The column is
`cv_native_all` / `flag_native_all` in `sweep_cycle_vt_cv.csv`.

### One phrasing to settle, not a number

The caption of Table `tab:s8-estimands` says "The two rows built from ratios
and the two built from differences disagree on which resolution overstates the
effect". Read as group-against-group that is not what the data show: within the
ratio pair the two rows already disagree with each other, and so do the two
difference rows. Read as "each pair disagrees internally" it is exactly right.
The body text is unambiguous and correct ("two summaries make the 5-second
statistic overstate the effect, two make it understate it"). Left untouched —
two readings are defensible, so it is the maintainer's call.

### Guard calibration — proven by reinjection, not asserted

1. Drifting a published count in `supplement.tex` (297 → 298) turns that row
   into a FAIL. Reverted; MD5 identical.
2. Correcting the disputed value to `22.66` turns the OPEN row into
   `**stale OPEN exception**: the disputed literal is gone`, so the exception
   cannot outlive its own motive. Reverted; MD5 identical.
3. Altering one 5-second CV in the artefact (0.2947… → 0.1947…) is caught by
   the cross-instrument layer, naming the run and both values. Restored; MD5
   identical.

The cross-instrument layer compares **decimal strings**, not parsed floats:
pandas' C parser is not correctly rounded and reads `8.79569357191e-12` back as
`8.795693571910001e-12`, which made an earlier tolerance-based version of this
check fail on two runs whose CV is numerically zero. Comparing the 12
significant digits the artefact actually promises needs no tolerance at all.

### Limite de reproductibilité, mesurée après coup le 2026-09-12

`results/s033/` **n'est pas régénérable sur un clone propre.**
`scripts/s033_cycle_resolved_vtcv.py` a besoin de `output.csv` et
`output_pulse_native.csv`, que `.gitignore` L19-L20 exclut (≈ 2 Go ; seul
`aggregated.parquet` est versionné). Vingt scripts du dépôt sont dans le même
cas, donc ce n'est pas une régression — mais le mot « reproductible » doit
porter cette borne.

C'est précisément pourquoi les deux gardes ne lisent **que** du versionné
(`results/s033/*`, `results/s023/rf_metrics.csv`, `aggregated.parquet`,
`supplement.tex`) : vérifié par énumération des chemins, et les quatre
invocations exactes de la CI sortent en 0. La moitié cycle-résolue n'est
re-vérifiée que par une relance locale du script, jamais par la CI.

⚠️ **Une différence avec `results/s023/`**, qui ne se lit pas sur la forme des
deux dossiers : `s023` est régénérable depuis le seul `aggregated.parquet`,
donc depuis le dépôt. `s033` ne l'est pas. Les deux dossiers se ressemblent et
n'ont pas le même contrat.
