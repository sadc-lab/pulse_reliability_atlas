# Monograph Anchor Map (`monograph_anchor_map.md`)

**Purpose.** This file locks numerical claims that live **only** in
`preprint/manuscript.md` — results derived from the atlas's own sweep data
that have no anchor in the claims ledger (`scripts/audit_claims.py`) and no
row in the paper crosswalk (`preprint_npj/paper_to_monograph_map.md`). The
audit script reads this file under the `--check-monograph` opt-in flag and
verifies that every declared pattern still occurs in the monograph at least
`min_occurrences` times.

---

## What this guard does — and what it does not do

**It detects drift.** Once a value has been verified by hand, this map stops
it changing silently afterwards. If someone edits one of the locked loci, the
occurrence count falls below the declared floor and the audit FAILs.

**It does not verify correctness.** A presence check cannot tell a right
number from a wrong one — only that the number is still there. The 26 patterns
below are trustworthy because each was **re-derived from the canonical
artefacts on 2026-07-25** before being locked, not because the guard says so.

That distinction is not theoretical. On the same day, re-derivation found that
the SHAP per-cell agreement rate had been wrong in three documents for two
months (90 % / 43 of 48 against a true 44 of 48 = 91.67 %). Every document
agreed with every other; a presence check would have passed every single day.
The value of the guard begins *after* verification, never before it.

**Corollary for whoever adds a row here.** Do not add a value you have not
re-derived yourself from the artefact named in `derivation`. Locking an
unverified number is worse than leaving it unlocked, because the lock lends
it the appearance of having been checked.

---

## Two deliberate divergences from `--check-paper-sync`

**1. Whitespace-normalised matching.** Both the monograph text and every
pattern are passed through `re.sub(r"\s+", " ", ...)` before comparison.
`manuscript.md` is hard-wrapped at roughly 70 columns, so any pattern longer
than a couple of words would otherwise straddle a newline and break the moment
an unrelated edit reflows the paragraph. The paper crosswalk does a raw
`re.escape` on raw text; `paper.tex` tolerates that, this file cannot.

**2. `min_occurrences` is a floor, not an equality.** The paper crosswalk
asserts an exact count and consequently needed 20 documented count bumps
across 38 commits for 97 entries. The monograph is edited far more freely, and
an exact count would fire on every legitimate *addition* of a correct mention.
A floor catches what actually matters — a locus being deleted or altered —
while staying silent when a value is correctly cited one more time.

---

## The substring hazard

Two of the locked values are substrings of unrelated numbers elsewhere in the
monograph:

| Value | Also matches inside | Mitigation |
|---|---|---|
| `8.7 %` | `78.7 %` (clean-rate decomposition, ×2) | pattern carries its sentence context |
| `2.5 %` | `62.5 %` (DBP-clip step ratio) | pattern carries its sentence context |

Any new row whose pattern is a bare short number must be checked the same way
before it is added. Digits alone are not a safe pattern.

---

## Schema

| Field | Required | Description |
|---|---|---|
| `anchor_id` | yes | Stable identifier, `M.T<target>.<slug>`. The target number refers to `audit/monograph_t1_anchor_candidates.md`. |
| `monograph_section` | yes | Where the claim appears. Free text, stable. |
| `claim` | yes | One line saying what the number is. |
| `pattern` | yes | Literal string searched for, after whitespace normalisation on both sides. Not a regex — it is `re.escape`d. |
| `min_occurrences` | yes | Integer floor. The audit FAILs below it and PASSes at or above it. |
| `derivation` | yes | Artefact path plus the arithmetic that produces the value, so a human can re-derive it without reading the source of this file. |
| `verified_on` | yes | ISO date on which the value was last re-derived from the artefact. |
| `notes` | optional | Qualifications — rounding, display form, known co-occurrences. |

## Audit semantics (under `--check-monograph`)

- **PASS** — count at or above `min_occurrences`.
- **FAIL (missing)** — count is 0.
- **FAIL (below floor)** — count is above 0 but below `min_occurrences`.
- **WARN** — the map or `manuscript.md` is absent, or a row fails to parse.

FAILs contribute to the script's exit code; WARNs do not.

---

## Anchors

- anchor_id: 'M.T02.shap_pooled'
  monograph_section: '§1.2 Key contributions; §3.8.1 nss cross-validation'
  claim: 'SHAP/Morris pooled top-3 agreement'
  pattern: '17 / 18'
  min_occurrences: 2
  derivation: 'results/s023/topk_overlap.csv — sum of overlap_size across the 6 outputs = 17, out of 6 x 3 = 18'
  verified_on: '2026-07-25'

- anchor_id: 'M.T02.shap_mean_overlap'
  monograph_section: '§1.2 Key contributions'
  claim: 'mean per-cell top-3 overlap'
  pattern: '2.40 / 3'
  min_occurrences: 1
  derivation: 'results/s023/topk_overlap_per_cell.csv — mean(overlap_size) over 48 rows = 2.39583'
  verified_on: '2026-07-25'
  notes: 'displayed to 2 dp'

- anchor_id: 'M.T02.shap_ge2_pct'
  monograph_section: '§1.2 Key contributions; §3.8.1 nss cross-validation'
  claim: 'share of per-cell comparisons agreeing at >= 2 of 3'
  pattern: '92 %'
  min_occurrences: 2
  derivation: 'results/s023/topk_overlap_per_cell.csv — 44 of 48 rows with overlap_size >= 2 = 91.6667 %'
  verified_on: '2026-07-25'
  notes: 'displayed as a whole percent. Was wrong (90 % / 43 of 48) in this document, in Supplement S13 and in the S023 log until commit 70b6078.'

- anchor_id: 'M.T03.floor_female_gap'
  monograph_section: '§3.6 blood-volume mechanism (F-S018-A)'
  claim: 'gap between the male BV floor and the female computed default'
  pattern: '86 mL'
  min_occurrences: 2
  derivation: '4082.24 - 3996.09 = 86.15 mL; both operands are ledger anchors (T3.s027 male floor, T3.s028 female default)'
  verified_on: '2026-07-25'
  notes: 'stated once as "86 mL above the female default" and once as "86 mL below the male floor" — same quantity, opposite direction'

- anchor_id: 'M.T04.cluster_hr'
  monograph_section: '§3.5 divergence input-combination signature'
  claim: 'heart-rate composition of the four S4_M-unique divergences'
  pattern: 'one HR at 110 bpm, three at 90 bpm'
  min_occurrences: 1
  derivation: 'data/runs/full_sweep/aggregated.parquet — diverged runs at run_idx 24 / 82 / 137 / 138 hold in_hr = 110, 90, 90, 90'
  verified_on: '2026-07-25'

- anchor_id: 'M.T04.cluster_vt'
  monograph_section: '§3.5 divergence input-combination signature'
  claim: 'tidal-volume composition of the four S4_M-unique divergences'
  pattern: 'two Vt at 300 mL, one at 633.3 mL, one at 800 mL'
  min_occurrences: 1
  derivation: 'data/runs/full_sweep/aggregated.parquet — same four runs hold in_vt = 633.3333, 800, 300, 300'
  verified_on: '2026-07-25'
  notes: '633.3 is a 1-dp display of 633.3333..., the third level of the Morris 4-level grid on [300, 800] with delta = 2/3. Harmonised from "633 mL" in commit 3540ddd.'

- anchor_id: 'M.T05.female_per_kg'
  monograph_section: '§3.6 absolute vs weight-normalized BV'
  claim: 'female weight-normalised blood volume'
  pattern: '71.1 mL/kg'
  min_occurrences: 1
  derivation: '3996.09 / 56.2 = 71.1048 mL/kg'
  verified_on: '2026-07-25'

- anchor_id: 'M.T05.per_kg_gap'
  monograph_section: '§3.6 absolute vs weight-normalized BV'
  claim: 'per-kg blood-volume gap between the two reference bodies'
  pattern: '~0.4 % per-kg'
  min_occurrences: 1
  derivation: '(4802.63/67.3 - 3996.09/56.2) / (4802.63/67.3) = 0.3597 %'
  verified_on: '2026-07-25'
  notes: 'the point of the sentence is that the gap is negligible, so the approximate form is the claim'

- anchor_id: 'M.T06.floor_per_kg'
  monograph_section: '§3.6 absolute vs weight-normalized BV'
  claim: 'male BV floor expressed per kilogram'
  pattern: '60.7 mL/kg'
  min_occurrences: 1
  derivation: '4082.24 / 67.3 = 60.6574 mL/kg'
  verified_on: '2026-07-25'

- anchor_id: 'M.T07.bracket_pct'
  monograph_section: '§3.6 S018 dose-response table and its narrative'
  claim: 'BV reduction at the intermediate override bracket'
  pattern: '8.4 %'
  min_occurrences: 2
  derivation: '(4802.63 - 4400) / 4802.63 = 8.3835 %'
  verified_on: '2026-07-25'

- anchor_id: 'M.T07.bracket_level'
  monograph_section: '§1.2, §3.6 S018 dose-response'
  claim: 'the intermediate BloodVolumeBaseline override level in mL'
  pattern: '4,400'
  min_occurrences: 6
  derivation: 'protocol constant of S018; the override actually submitted to Pulse, logged at setup in data/runs/s018_blood_volume'
  verified_on: '2026-07-25'
  notes: 'all six occurrences are the S018 bracket; none is an unrelated 4,400'

- anchor_id: 'M.T08.divergence_rate'
  monograph_section: '§3.6 sex-stratified divergence'
  claim: 'per-cell divergence rate in the three non-severe male cells'
  pattern: '2.5 % in S1_M, S2_M, and S3_M'
  min_occurrences: 1
  derivation: 'data/runs/full_sweep/aggregated.parquet — 4 diverged of 160 runs in each of S1_M, S2_M, S3_M = 2.5 %'
  verified_on: '2026-07-25'
  notes: 'context-anchored: a bare "2.5 %" also matches inside "62.5 %" in the DBP-clip passage'

- anchor_id: 'M.T08.divergence_frac'
  monograph_section: '§3.6 sex-stratified divergence; §3.9 seed stability'
  claim: 'divergence count per non-severe male cell'
  pattern: '4 / 160'
  min_occurrences: 3
  derivation: 'data/runs/full_sweep/aggregated.parquet — 4 diverged of 160 in each of S1_M, S2_M, S3_M'
  verified_on: '2026-07-25'

- anchor_id: 'M.T12.runaway_frac'
  monograph_section: '§3.8 solver-instability tail'
  claim: 'runaway count in the S021 healthy-S1 extended cohort'
  pattern: '6 / 44'
  min_occurrences: 1
  derivation: 'data/runs/s021_hyperoxia_convergence/plateau_stats.parquet — 6 of the 44 S1 rows have PaO2_plateau_mmHg > 700'
  verified_on: '2026-07-25'

- anchor_id: 'M.T12.runaway_pct'
  monograph_section: '§3.8 solver-instability tail'
  claim: 'runaway rate in the S021 healthy-S1 extended cohort'
  pattern: '14 %'
  min_occurrences: 1
  derivation: '6 / 44 = 13.64 %'
  verified_on: '2026-07-25'
  notes: 'displayed as a whole percent'

- anchor_id: 'M.T13.runaway_vt'
  monograph_section: '§3.5 divergence signature; §3.8 solver-instability tail'
  claim: 'the tidal-volume level shared by all six runaways'
  pattern: '633.3 mL'
  min_occurrences: 3
  derivation: 'plateau_stats.parquet joined to full_sweep/aggregated.parquet — all six runs above 700 mmHg hold in_vt = 633.3333; 6 of the 20 S1 reruns at that level, 0 of the 24 at the other three'
  verified_on: '2026-07-25'
  notes: 'the earlier claim that all six also shared RR = 20 was false (five of six) and was corrected in commit 10f2279 together with the withdrawn ~12 L/min guidance'

- anchor_id: 'M.T16.vtcv_pair_arrow'
  monograph_section: '§1.2, §2.x, §4.x trigger-lockout mentions (arrow form)'
  claim: 'median delivered-Vt CV before and after the -2 cmH2O trigger lock'
  pattern: '0.351 → 0.016'
  min_occurrences: 4
  derivation: 'data/runs/s014_trigger_lockout/paired_comparison.parquet — median(Vt_cv_orig) = 0.350867, median(Vt_cv_lock) = 0.015631 over 64 pairs'
  verified_on: '2026-07-25'
  notes: 'the same pair is written with a prose "to" in three further places; see M.T16.vtcv_pair_to. A bare "0.016" also occurs once as an unrelated S4 SpO2 table cell, which is why the pair is locked rather than the endpoints.'

- anchor_id: 'M.T16.vtcv_pair_to'
  monograph_section: '§1.2, §3.8, §4.x trigger-lockout mentions (prose form)'
  claim: 'median delivered-Vt CV before and after the -2 cmH2O trigger lock'
  pattern: '0.351 to 0.016'
  min_occurrences: 3
  derivation: 'same as M.T16.vtcv_pair_arrow'
  verified_on: '2026-07-25'

- anchor_id: 'M.T16.vtcv_reduction'
  monograph_section: '§3.8, §4.x trigger-lockout guidance'
  claim: 'relative reduction in median delivered-Vt CV under the trigger lock'
  pattern: '96 %'
  min_occurrences: 3
  derivation: '1 - 0.015631 / 0.350867 = 95.545 %'
  verified_on: '2026-07-25'
  notes: 'displayed as a whole percent'

- anchor_id: 'M.T17.drift_map'
  monograph_section: '§3.8.1 steady-state window audit (S012)'
  claim: 'median MAP drift over the final 60 s, hyperoxia arm'
  pattern: '0.05 mmHg'
  min_occurrences: 1
  derivation: 'S012 audit over data/runs/full_sweep — median absolute MAP drift = 0.0495 mmHg / 60 s at FiO2 >= 0.95'
  verified_on: '2026-07-25'

- anchor_id: 'M.T17.drift_paco2'
  monograph_section: '§3.8.1 steady-state window audit (S012)'
  claim: 'median PaCO2 drift over the final 60 s, hyperoxia arm'
  pattern: '0.58 mmHg'
  min_occurrences: 1
  derivation: 'S012 audit — median absolute PaCO2 drift = 0.575 mmHg / 60 s at FiO2 >= 0.95'
  verified_on: '2026-07-25'

- anchor_id: 'M.T17.drift_vt'
  monograph_section: '§3.8.1 steady-state window audit (S012)'
  claim: 'median delivered-Vt drift over the final 60 s, hyperoxia arm'
  pattern: '0.09 mL'
  min_occurrences: 1
  derivation: 'S012 audit — median absolute Vt drift = 0.0869 mL / 60 s at FiO2 >= 0.95'
  verified_on: '2026-07-25'

- anchor_id: 'M.T18.vt_exceedance'
  monograph_section: '§3.8.1 steady-state window audit (S012)'
  claim: 'share of hyperoxia-arm runs exceeding the locked 50 mL Vt drift threshold'
  pattern: 'Vt exceeds 50 mL in **8.7 %**'
  min_occurrences: 1
  derivation: 'S012 audit — 8.72 % of the n = 195 runs at FiO2 >= 0.95 exceed DRIFT_MAX_DELTA_60S["Vt"] = 50.0'
  verified_on: '2026-07-25'
  notes: 'context-anchored: a bare "8.7 %" also matches inside "78.7 %" in the clean-rate decomposition, twice'

- anchor_id: 'M.T19.pao2_exceedance'
  monograph_section: '§3.8.1 steady-state window audit (S012)'
  claim: 'share of Vt-oscillation-arm runs exceeding the locked 15 mmHg PaO2 drift threshold'
  pattern: '7.3 %'
  min_occurrences: 1
  derivation: 'S012 audit — 7.26 % of the n = 303 runs with Vt CV > 0.05 exceed DRIFT_MAX_DELTA_60S["PaO2"] = 15.0'
  verified_on: '2026-07-25'

- anchor_id: 'M.T20.cornish_pct'
  monograph_section: '§4 Cornish cross-comparison'
  claim: 'PaCO2 bootstrap rejection rate in Cornish 2023'
  pattern: '18.6 %'
  min_occurrences: 1
  derivation: '13 / 70 = 18.571 %. The counts are Cornish 2023 Appendix Table 4, maintainer-verified against the PDF in S029; the percentage is our arithmetic on them.'
  verified_on: '2026-07-25'

- anchor_id: 'M.T20.cornish_frac'
  monograph_section: '§4 Cornish cross-comparison (overlap table and narrative)'
  claim: 'PaCO2 bootstrap rejection count in Cornish 2023'
  pattern: '13 / 70'
  min_occurrences: 3
  derivation: 'Cornish 2023 Appendix Table 4, PaCO2 row: "Arterial CO2 Pressure (paCO2)  3  70"; Table 5 (bootstrap): "... 13  70". Not re-derivable from atlas data; locked against transcription drift only.'
  verified_on: '2026-07-26'
  notes: 'Verified at source on 2026-07-26 -- arXiv:2301.07210v4 retrieved and text-extracted, both appendix tables transcribed in full, all 9 Cornish-attributed claims MATCH (audit/reference_audit.md). This was the one anchor whose correctness rested on a human reading of an external PDF rather than on atlas data; that reading is now confirmed verbatim.'
