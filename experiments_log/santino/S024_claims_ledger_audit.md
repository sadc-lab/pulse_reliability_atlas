---
id: S024
author: santino
date: 2026-05-22
status: done
tags: [claims-ledger, pre-submission, manuscript-polish, reviewer-defense, audit, reproducibility]
linked_code:
  - scripts/audit_claims.py
linked_data:
  - data/runs/full_sweep/aggregated.parquet
  - results/cell_flag_summary.csv
  - results/h1_top3_fraction.csv
  - results/bh_fdr_survivors.csv
  - results/spearman_mu_star.csv
  - results/reliability_classification.csv
  - results/s022/nss_decomposition.csv
  - results/s023/topk_overlap.csv
  - results/s023/topk_overlap_per_cell.csv
  - results/f003_physiological_reclassification_summary.json
  - data/runs/s014_trigger_lockout/paired_comparison.parquet
  - data/runs/s014_trigger_lockout/summary.json
  - data/runs/s021_hyperoxia_convergence/plateau_stats.parquet
  - data/runs/s021_hyperoxia_convergence/summary.json
  - data/runs/s018_blood_volume/s018_classified.parquet
  - data/runs/s018_blood_volume/s018_floor_classified.parquet
supersedes: ""
related: [S006, S012, S014, S017, S018, S020, S021, S022, S023]
---

# S024 — Pre-submission claims-ledger audit

## Hypothesis

After ~5 weeks of iterative manuscript editing across 23 prior experiments,
every Tier-1 and Tier-2 quantitative claim in `preprint/manuscript.md`
still matches the underlying frozen parquets / CSVs / JSON summaries —
i.e., the manuscript has not accumulated transcription drift, stale
numbers from earlier sweep runs, or off-by-one arithmetic since the
2026-05-12 pre-submission audit (`9192fbb..1f3d034`).

If the hypothesis holds the manuscript is data-integrity-clean and can
go to arXiv as soon as the Phase-3 polish lands. If it fails, the script
flags the specific lines that need a one-character edit before
submission.

## Motivation (why now)

The manuscript has crossed three reframe events since the last
load-bearing audit:

* **S017** (2026-05-13) added the Cornish 2023 cross-tab (Table 2);
* **S018** (2026-05-13) replaced the §3.5 "mechanism candidate"
  paragraph with the BV dose-response (20 / 20 → 2 / 20 → 0 / 20);
* **S021** (2026-05-21) reframed F-003 from "oxygenation overshoot" to
  "transient hyperoxia regime + AGE undershoot" and added the 643 mmHg
  S1 plateau number to the Abstract / Key Contributions / §3.8;
* **S022** (2026-05-22) added Appendix C with the 530 / 76 / 170 / 185
  NSS decomposition;
* **S023** (2026-05-22) added the 17 / 18 + 23 / 48 SHAP-Morris
  cross-check to §4.5.

The 2026-05-22 iterative-debt audit (commits c456118 / 2abfb58 / cc4bcae)
fixed five framing leaks (§1.4 boundary, H3 regime qualifier, BV
"floor → gap" noun correction, F-003 AGE-undershoot clause, §3.2 lexical
sweep), but it did *not* re-verify the **numerical** content. S024 fills
that gap. Pre-submission is the right moment for a claims-ledger pass
because every quoted number will be scrutinized by reviewers and the
cost of a one-line fix before submission is far below the cost of a
post-submission corrigendum.

## Method (how)

Read-only verification, no recomputation from raw CSVs. The script
loads the same derived artifacts the manuscript was built from, so it
does not re-seed any bootstraps and does not drift away from the
2026-04-26 / 2026-05-13 / 2026-05-21 / 2026-05-22 locked numbers.

### Scope

Tier 1 (~30 headline claims): Abstract, Key Contributions, hypothesis
verdicts (H1 48/48, H2 0/1280, H3 20/1280 + sex stratification, H4 5/24
BH-FDR survivors), Table 1 cell counts, §3.7 traffic-light (7 / 29 / 12),
total clean (663 / 1,280 = 51.8 %).

Tier 2 (~60 deeper numbers): §3.3 top-3 fraction extrema, §3.4.1
compensatory tachycardia HR per scenario, §3.5 BV dose-response table,
§3.6 Wasserstein + Spearman per cell × output, §3.8 F-003 plateau
(643 mmHg) + F-003 reclassification (32 / 34) + shunt depression
(143.6 / 72.6 mmHg) + solver-instability tail (6 / 44), §3.8.1
cross-output drift, Appendix C NSS decomposition (per-cell + totals +
counterfactual 78.7 %), §4.5 S023 SHAP overlap (17 / 18 + 23 / 48).

Tier 3 (~hundreds of literature-quoted numbers and preregistration
thresholds) explicitly excluded — already verified in S010 + the
2026-05-12 pre-submission audit.

### Tolerance rules

* `exact_int` (0): integer counts must match exactly.
* `pct_1dp` (±0.05): percentages displayed to 1 decimal.
* `pct_whole` (±0.5): percentages displayed as whole numbers.
* `whole_unit` (±0.5): floats displayed to whole units.
* `displayed_1dp` (±0.05): floats displayed to 1 decimal.
* `displayed_2dp` (±0.005): floats displayed to 2 decimals.
* `displayed_3dp` (±0.0005): floats displayed to 3 decimals.
* `approx_round` (PASS ≤ 1.0, WARN ≤ 2.0): numbers with explicit "~"
  or rounded-to-tens display.

Tolerance is checked with a 1e-9 epsilon to avoid IEEE-754 noise at
exact half-precision boundaries (e.g., 0.0215 → 0.022 round-half-up,
where the binary diff is 0.0005000000000000004).

### Triage codes for discrepancies

* **Type A** — Transcription / rounding drift. Manuscript text needs a
  one-character edit; the underlying data is correct.
* **Type B** — Orphaned number. Manuscript number does not match any
  source artifact; needs forensic tracing.
* **Type C** — Derivation mismatch. Manuscript number was computed with
  a different threshold / filter / seed than the canonical artifact.

### Implementation

`scripts/audit_claims.py`. 187 → 190 claims registered as `Claim`
records (`claim_id`, `section`, `manuscript_text`, `source_file`,
`manuscript_value`, `computed_value`, `tolerance_rule`); each evaluated
against its tolerance rule; output as a markdown table to stdout,
sorted FAIL → WARN → PASS.

Run: `uv run python scripts/audit_claims.py`. Exit code is 0 if zero
FAILs, 1 otherwise (suitable for piping into CI later).

## What we tried (including dead ends)

* **First pass — too-strict tolerance rules.** Used `displayed_2dp`
  (±0.005) for all single-decimal floats in §3.4.1 (compensatory
  tachycardia HR) and §3.8 (shunt-depression plateaus). Result: 11
  FAILs that were all manuscript-correctly-rounded numbers (e.g.,
  manuscript 143.6 mmHg vs computed 143.578 mmHg, diff 0.022 — within
  the ±0.05 tolerance the manuscript's 1-decimal display deserves).
  Added a `displayed_1dp` tolerance rule (±0.05) and reclassified.
* **Second pass — IEEE-754 boundary issue on BH p-value.** S2 SpO2 p =
  0.022 (manuscript) vs 0.0215 (computed) failed under `displayed_3dp`
  because `abs(0.022 - 0.0215) = 0.0005000000000000004` in IEEE 754
  double precision, just above the 0.0005 tolerance. Added a 1e-9
  epsilon to the comparison; this now PASSes (and the manuscript's
  rounding 0.0215 → 0.022 is correct under round-half-up).
* **Considered (and rejected)** recomputing the H4 within-sex
  Wasserstein null from `aggregated.parquet`. The null is built from
  2,000 random splits with a fixed RNG seed; recomputing without the
  seed would produce slightly different p-values and flag a Type-C
  derivation mismatch on every row. Used `results/bh_fdr_survivors.csv`
  (the canonical artifact the manuscript was built from) instead. This
  matches the design principle that the audit verifies *the manuscript
  matches the artifacts it was built from*, not *the manuscript matches
  a fresh recomputation of the analysis pipeline*.
* **Considered** auditing every "at a glance" box numerically. Most
  "at a glance" boxes repeat numbers from the immediately preceding
  table; auditing them would double-count claims already verified.
  Kept the audit scoped to the underlying tables; the prose boxes are
  manually consistent by construction.

## Results

**190 claims audited; 188 PASS, 1 WARN, 1 FAIL.**

### F-003.drift\_exceed\_v38 (FAIL — Type A internal inconsistency)

Manuscript at `preprint/manuscript.md:1927` (§3.8 main paragraph) says
*"93.3 % of FiO2 ≥ 0.95 valid-CSV runs have positive slope over
[60, 120] s and **18.5 %** exceed the 15 mmHg / 60 s drift threshold
(full audit in §3.8.1)."*

Manuscript at `preprint/manuscript.md:2135` (§3.8.1, F-003 arm) says
about the same population (n = 195, FiO2 ≥ 0.95 valid-CSV runs):
*"PaO2 is the only severely affected channel: **19.5 %** exceed the
15 mmHg drift threshold (median 4.3 mmHg, p95 = 40.2 mmHg)."*

Recomputed value from `data/runs/full_sweep/aggregated.parquet`
(filter: `in_fio2 >= 0.95 & PaO2_n_points > 0`, denominator 195;
predicate: `abs(PaO2_delta_60s) > 15`): **19.49 %, rounds to 19.5 %**.

§3.8.1 is correct. §3.8 main paragraph is iterative-debt residue —
presumably from an earlier sweep iteration before S012 / §3.8.1
landed. **Proposed fix:** one-character edit at L1927,
`18.5 %` → `19.5 %`.

Sibling claims that PASS in the same population:

* `T2.f003.pos_slope`: 93.3 % positive slope (matches).
* `T2.f003.arm_n_total`: n = 208 at FiO2 ≥ 0.95 (matches §3.8.1).
* `T2.f003.arm_n_valid`: 195 valid CSV (matches §3.8.1).

So the §3.8 paragraph has exactly one off-iteration number; everything
else in the same paragraph matches the canonical artifact and §3.8.1.

### S023.ge2\_pct (WARN — soft rounding drift, Type A)

Manuscript at `preprint/manuscript.md:2580` (§4.5 limitations) says
*"23 / 48 per-cell cases at full 3 / 3 agreement (**90 %** of per-cell
comparisons at ≥ 2 / 3)."*

Recomputed: 44 / 48 = **91.67 %** at ≥ 2 / 3. The 23 / 48 full-match
number is correct; the "90 %" rounded-down framing of the ≥ 2 / 3
number is 1.67 percentage points off. Defensible as "approximately
90 %" but `"92 %"` or `"≥ 90 %"` would be tighter. **Soft fix** — not
load-bearing for any claim in the paper, but worth a one-character
edit to remove the WARN.

### All other 188 claims PASS

Including:

* All 8 cells × 6 columns = 48 numbers in Table 1.
* All 8 cells × 6 columns = 48 numbers in Appendix C.
* All 12 Spearman ρ point estimates in §3.6.
* All 4 F-003 reclassification numbers (32, 31, 21, 11).
* All 8 BV dose-response numbers (4 bracket + 4 floor).
* All 14 hypothesis-verdict numbers (48 / 48, 0 / 1280, 20 / 1280,
  1.6 %, 5 / 24, 3.1 %, etc.).
* Traffic light 7 / 29 / 12.
* F-003 S1 plateau 643.3 mmHg (rounds to 643).
* F-003 S3 plateau 143.6 mmHg, S4 plateau 72.6 mmHg.
* F-003 solver-instability tail 6 / 44.
* F-004 collapse 0.351 → 0.016, worst-case 1.826 → 0.112.
* NSS counterfactual 78.7 %.
* S023 17 / 18 pooled and 23 / 48 per-cell full match.

## Interpretation

The manuscript is **data-integrity-clean to 188/190 (99.0 %) of the
audited claims** under the tolerance rules above. Of the two
discrepancies, one is a strict FAIL (Type A internal inconsistency
inside §3.8 that needs a one-character `18.5 → 19.5` edit) and one is
a soft WARN (Type A rounding drift inside §4.5 worth a `90 % → 92 %`
or `≥ 90 %` polish).

Neither discrepancy invalidates any headline claim, hypothesis
verdict, table, or figure. The manuscript's load-bearing numbers all
trace cleanly to the canonical artifacts. The audit is therefore a
**green-light** for submission with two trivial pre-submission edits.

**What this audit does NOT verify** (and why it does not need to):

1. Literature-quoted numbers (Webb 2020 P/F values, Cornish 2023
   rejection counts, Severinghaus dissociation curve, etc.) — already
   verified in S010 + the 2026-05-12 pre-submission audit.
2. Preregistration-quoted thresholds (locked pre-data) — verified at
   preregistration lock and unchanged since.
3. Numerical reproducibility of the *analysis pipeline* (fresh
   recomputation from raw CSVs through `src/analysis_*.py` to
   `results/*.csv`) — already verified by S007 bit-exact reproduction
   and S015 logic audit.

What it does verify is the *transcription* layer between the canonical
artifacts and the manuscript prose, which is exactly the surface that
iterative editing across 23 sub-experiments could (and did, in one
spot) drift on.

### Limitations

1. The audit verifies that the *manuscript text* matches the *frozen
   artifacts*; it does not verify that the frozen artifacts are
   themselves correct. That validation lives in S006 (sweep
   integrity), S007 (bit-exact reproduction), S008 (statistical
   refinement), S015 (logic audit), S017 (Cornish cross-mapping), and
   S012 (steady-state window cross-output audit).
2. The audit is necessarily limited to *quoted numbers*. Qualitative
   claims (e.g., "Pulse correctly captures the regime where shunt
   physiology pins PaO2") are not verifiable by this script and were
   handled by the S015 logic audit.
3. The audit does not check for *omitted* numbers — e.g., a number
   that should be cited from a parquet but is missing from the
   manuscript. That kind of gap-finding is what the iterative-debt
   audit (commits c456118 / 2abfb58 / cc4bcae) was designed to catch.

## Next steps

1. **Apply the two flagged edits** if the user authorizes:
   * `preprint/manuscript.md:1927`: `18.5 %` → `19.5 %` (Type A FAIL).
   * `preprint/manuscript.md:2580`: `90 %` → `92 %` or `≥ 90 %`
     (Type A WARN).
   Both are one-character / one-token edits; PDF build will need a
   re-run.
2. **Optional**: wire `uv run python scripts/audit_claims.py` into CI
   so future manuscript edits that break a quoted number against the
   parquets fail the build.
3. **Question closed.** No further pre-submission audit needed on
   numerical content; remaining pre-submission work is editorial
   (Phase-3 polish on prose flow, final reference verification).
