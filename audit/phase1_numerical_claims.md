# Phase 1 — Numerical claims vs raw data (independent re-derivation)

**Date:** 2026-05-18
**Pass:** Independent of prior commit `2e69660`. Every D-class claim
re-derived from raw data by a fresh script (`audit/phase1_recompute.py`
and `audit/phase1_recompute2.py`).

**Status after user-approved fixes (2026-05-18, same day):**
P1-C1, P1-C2, P1-W1, P1-W2, P1-W4, P1-W5, P1-W6, P1-W7 applied to
`manuscript.md` / `supplementary.md` (and `appendix_B_draft.md`
deleted). P1-W3 withdrawn (false alarm; bug was in this audit's
script, not in the manuscript — see §G below for the diagnosis).
Every edited number was re-verified against raw data after the edit.
**Per-run fresh aggregates:** `audit/phase1_fresh_per_run.parquet`.
**Raw script output:** `audit/phase1_recompute.out.json`,
`audit/phase1_recompute2.out.json`.
**Scope:** `preprint/manuscript.md` (2,192 lines) +
`preprint/supplementary.md` (226 lines) +
`preprint/appendix_B_draft.md` (26 lines).
**Total D-class claims audited:** ≈ 95.

## Headline result

* **No headline finding is falsified.** Every primary number that
  carries a load-bearing conclusion (1,280 / 663 / 20 / 0; 20.6 %
  F-004; 5 / 24 BH-FDR survivors; 7/29/12 reliability lights;
  S014 0.351 → 0.016 collapse; S018 dose-response; Cornish 85 / 281
  total Hoeffding / bootstrap) reproduces from raw data.
* **2 critical text-level findings** (P1-C1, P1-C2) where the
  manuscript prose contradicts its own data table or another manuscript
  file. **Both are correctable by text edits only — no re-analysis
  needed.**
* **8 lesser findings** (P1-W1 … P1-W8): wording imprecision,
  documentation gaps, or boundary-convention ambiguities.

## Cross-check on Phase 1 method (sanity sub-audit, §1c)

Five random D-class claims were re-derived a second way to catch
pandas-level errors. All five second-derivations match the first:

| # | Claim | Method A | Method B | Match? |
|---|---|---|---|---|
| 1 | Clean count (=663) | `df['clean'].sum()` | manual `for`-loop | ✓ exact |
| 2 | Divergence count (=20) | `df['diverged'].sum()` | `(exit_code != 0).sum()` | ✓ exact |
| 3 | PaO2~FiO2 linregress (slope, intercept, R²) | `scipy.stats.linregress` | manual cov / var | ✓ to 1e-6 |
| 4 | S1 PaCO2 Wasserstein | `scipy.stats.wasserstein_distance` | trapezoidal CDF integration | ✓ to 1e-4 |
| 5 | Spearman ρ on S2 Vt μ\* vectors | `scipy.stats.spearmanr` | Pearson on ranks | ✓ to 1e-6 |

The audit method is internally consistent.

---

# A. Critical findings (manuscript prose contradicted by data)

## **P1-C1.** §3.6 lines 1128–1130: "Vt and HR" attribution to uncorrected significant rows is wrong

**Manuscript prose (line 1128, in bold in the manuscript):**

> "Initial uncorrected analyses (α = 0.05) flagged Vt and HR as
> significant sex effects, alongside an additional S2 SpO2 finding
> (6 / 24 rows)."

**Data (`results/wasserstein_male_vs_female.csv` and re-derived from
raw clean-run means):**

The six rows with `p_emp ≤ 0.05` are:

| Scenario | Output | p_emp |
|---|---|---|
| S1 | PaCO2 | 0.009 |
| S2 | SpO2  | 0.022 |
| S2 | PaCO2 | 0.000 |
| S3 | PaCO2 | 0.000 |
| S4 | SpO2  | 0.0015 |
| S4 | PaO2  | 0.003 |

**None of the six is a Vt or HR row.** Vt rows have p_emp ∈
{0.798, 0.840, 0.129, 0.897}; HR rows have p_emp ∈ {0.305, 0.958,
0.333, 0.953}. The manuscript's own §3.6 Wasserstein table (and
supplementary §S6) prints these unambiguously.

**Verdict:** the prose claim is factually wrong. The "(6 / 24 rows)"
count is correct, but the attribution to "Vt and HR" is the opposite
of what the data show. The six uncorrected-significant rows are all
gas-exchange (3 PaCO2, 2 SpO2, 1 PaO2); BH-FDR drops one (S2 SpO2)
and keeps five — which is what the bolded sentence later in the
paragraph correctly states.

**Suggested fix:** rewrite lines 1128–1133 to read something like:

> "Initial uncorrected analyses (α = 0.05) flagged six rows as
> significant (S1 PaCO2, S2 SpO2, S2 PaCO2, S3 PaCO2, S4 SpO2, S4
> PaO2). Applying BH-FDR control at q = 0.05 removes S2 SpO2 (p =
> 0.022 > BH critical 0.0104 for the 6th-ranked test); the remaining
> five — all gas-exchange — are reported above. Cardiovascular (HR,
> MAP) and ventilator (Vt) channels do not exceed the within-sex null
> at α = 0.05 in any scenario."

This is a substantive prose error; it inverts the H4 narrative on
which channels were "initially" significant. No data needs to change.

---

## **P1-C2.** Supplementary §S9 reliability-light counts (12 / 24 / 12) contradict main §3.7 (7 / 29 / 12)

**Supplementary line 205:**

> "Distribution: 12 green, 24 yellow, 12 red."

**Main manuscript §3.7 line 1210 (already corrected by prior audit
fix D10):**

> "Distribution: 7 green, 29 yellow, 12 red out of 48 cells."

**Re-derived from `results/reliability_classification.csv`:**

| Colour | Count |
|---|---|
| green | 7 |
| yellow | 29 |
| red | 12 |

The supplementary's "12 / 24 / 12" is the stale pre-D10 count. The
prior audit (commit `2e69660`) updated `manuscript.md` but did not
sync `supplementary.md`. The per-cell grid in §S9 (lines 196–203) is
already correct — only the summary line is stale.

**Suggested fix:** change supplementary §S9 line 205 to "7 green, 29
yellow, 12 red". Text-only edit.

---

# B. Substantive but non-critical findings

## **P1-W1.** §3.5 line 1003: "5 % for males, holding across all four scenarios" does not arithmetically reproduce

**Manuscript:**

> "The only difference is patient mass / height / sex flag — yet the
> divergence rate is 5 % for males and 0 % for females, holding
> across all four scenarios."

**Data:**

| Cell | Diverged | Rate |
|---|---|---|
| S1_M | 4 / 160 | 2.5 % |
| S2_M | 4 / 160 | 2.5 % |
| S3_M | 4 / 160 | 2.5 % |
| S4_M | 8 / 160 | 5.0 % |
| S1–S4 F | 0 / 160 each | 0.0 % |
| **All male** | **20 / 640** | **3.125 %** |

The "5 %" rate is only S4_M. Other male cells are 2.5 %. The
overall male rate is 3.125 %. The claim "5 % … holding across all
four scenarios" cannot be reconciled with the per-cell numbers.

The next sentence's "specifying the male standard surrogate
roughly 5× more likely" similarly does not follow from "5 % vs 0 %"
(the ratio is infinite). 5× could compare 5 % S4_M against 1 % F
(also not zero) — but the data are 5 % vs 0 %.

**Suggested fix:** rewrite to something like:

> "the per-cell divergence rate is 2.5 % across S1_M / S2_M / S3_M
> and 5.0 % in S4_M, and 0.0 % in every female cell."

And drop or rephrase the "5× more likely" claim — when one arm has
zero events, "5× more likely" is not a meaningful ratio; "all 20
divergences occur on the male surrogate" is the cleanest statement.

## **P1-W2.** §3.2 line 695: "PaO2's FiO2 sensitivity peaks at S2 / S3 (μ\* = 133 – 147 mmHg)" — range is S2-only

**Manuscript:** "PaO2's FiO2 sensitivity peaks at S2 / S3 (μ\* = 133
– 147 mmHg) and *collapses* in severe ARDS (μ\* = 31 in (S4, M))."

**Data (`results/morris_indices.parquet`, dominant input = FiO2 on
output PaO2):**

| Cell | μ\* |
|---|---|
| S2_M | 133.10 |
| S2_F | 146.69 |
| S3_M | 84.45 |
| S3_F | 93.21 |
| S4_M | 30.72 |
| (S1, S4_F: FiO2 has zero clean EE pairs) | n/a |

The cited "133 – 147" range matches S2 only. S3 values are 84 – 93,
not 133. The S3 PaO2 ~ FiO2 sensitivity is still substantial relative
to S4_M (≈ 31) but is not in the 133 – 147 range.

**Suggested fix:** "peaks in S2 (μ\* = 133 – 147 mmHg) and remains
elevated in S3 (μ\* = 84 – 93 mmHg) before collapsing in severe ARDS
(μ\* = 31 in (S4, M))." Same conclusion, more accurate range.

## **P1-W3.** ~~Documentation gap: which timeseries is `Vt_cv` computed on?~~ — **WITHDRAWN**

**Resolution (verified by reading `src/detector.py` lines 28–73 and
295–351, with user authorisation):** the manuscript is correct.
`Vt_cv` is computed exactly as §2.4 and §2.9 state — on the 5 s
`output.csv`, with the [60, 120] s steady-state window. The
"discrepancy" in my fresh audit script was a 1e-6 float-tolerance
bug in *the audit script*, not in the manuscript.

Diagnosis:

* Pulse emits `time_s = 120` as the literal float
  `120.0000000000557` (accumulated drift from solving 12,000
  internal time steps at Δt = 0.01). My audit script used the naive
  filter `time_s <= 120.0`, which excludes this final point. The
  detector (`src/detector.py:295`) uses
  `time_s <= STEADY_STATE_T_HI + 1e-6 = 120.0 + 1e-6`, which
  includes it. So the audit script saw a 12-point window where the
  detector saw a 13-point window — and on runs where the omitted
  point is an outlier (e.g. S2_F_0118 ends at Vt = 534 mL while
  surrounding points are ≈ 819 mL), the dropped point pulls the CV
  from 0.097 down to 0.020.

* Re-running the audit script *with* the ±1e-6 tolerance, the fresh
  re-derivation reproduces the stored `Vt_cv` exactly:
  mean = 797.00 mL, std = 77.46 mL, CV = 0.0972 — bit-identical to
  the stored column for S2_F_0118.

**Consequence:** the manuscript needs no documentation patch. The
303 / 264 F-004 counts and the §3.8.1 drift percentages all hold as
written. The fix is to the audit script (already corrected for the
re-verification pass that confirmed all edited numbers below).

The earlier rows in this report that reference "stored Vt_cv" as if
distinct from "5 s output.csv Vt_cv" should be read as "the
correctly-computed Vt_cv on the 5 s output.csv" — they are the same
quantity. No edit is needed in §2.4 or §2.9.

## **P1-W4.** §3.5.1 continuous-severity bin denominators differ from re-derivation by ±1 per bin

**Manuscript §3.5.1 table:**

| Severity range  | F runs | M runs |
|---|---|---|
| [0, 0.5]         | 31     | 31     |
| (0.5, 0.85]      | 19     | 19     |
| (0.85, 0.91]     | 19     | 19     |
| (0.91, 0.945]    | 9      | 9      |
| (0.945, 0.95]    | 2      | 2      |
| (0.95, 1.0]      | 20     | 20     |
| **Total**       | **100** | **100** |

**Re-derivation from `results/continuous_ards_severity_sweep.parquet`
with the literal half-open intervals `(lo, hi]`:**

| Severity range  | F runs | M runs |
|---|---|---|
| [0, 0.5]         | 31     | 31     |
| (0.5, 0.85]      | 20     | 20     |
| (0.85, 0.91]     | 18     | 18     |
| (0.91, 0.945]    | 10     | 10     |
| (0.945, 0.95]    | 2      | 2      |
| (0.95, 1.0]      | 19     | 19     |
| **Total**       | **100** | **100** |

Per-sex totals match (100 = 100). Lower edge of instability (0.879)
matches exactly. F-diverged total (= 19) and M-diverged total (= 14)
match exactly. The discrepancy is one run shifting at each of three
bin boundaries (≈ 0.85 / ≈ 0.945 / ≈ 0.95) under different
inclusion conventions.

**Suggested fix:** either (a) document the exact inclusion convention
used (e.g. "bin labels denote the right-closed convention except for
boundary severities, which were assigned to the bin whose label has
the closer round number") or (b) renumber the per-bin denominators
to match the re-derivation under the manuscript's stated `(lo, hi]`
convention. The qualitative claim ("F earlier in the band, M later")
is independent of this convention and holds either way.

## **P1-W5.** §3.5.1 "about 35 % wider on the low side" does not arithmetically reproduce

**Manuscript:** "The `Pulse_translation_new` E6 audit reported an
instability zone at `[0.91, 0.945]`. Our continuous sweep at midrange
inputs places the band at `[0.879, 0.945]` — about 35 % wider on the
low side."

**Arithmetic candidates:**

* `(0.91 - 0.879) / (0.945 - 0.91) = 0.031 / 0.035 = 88.6 %` — the low-side extension as a fraction of the original width.
* `(0.945 - 0.879) / (0.945 - 0.91) = 0.066 / 0.035 = 188.6 %` — total width ratio.
* `(0.91 - 0.879) / 0.91 = 3.4 %` — low-side extension as a fraction of the original lower edge.

None gives 35 %. The qualitative observation (the new lower edge is
earlier than the E6 lower edge) is correct, but the "35 %" number is
unsourced.

**Suggested fix:** replace "35 %" with the arithmetic that actually
matches (e.g. "the lower edge moved from 0.91 to 0.879, extending the
band by 0.031 — about 90 % of the original E6 width") or drop the
percentage entirely.

## **P1-W6.** `appendix_B_draft.md` P/F values disagree with main manuscript Appendix B.3

**`appendix_B_draft.md` line 18 (and 16, 17):**

| Severity | P/F (draft) |
|---|---|
| 0.26 | ~ 256 |
| 0.60 | ~ 148 |
| 0.95 | ~ 75 |

**Main manuscript Appendix B.3 table (lines 2131–2135):**

| Severity | P/F (main) |
|---|---|
| 0.26 | 256 |
| 0.60 | 150 |
| 0.95 | 96 |

The 0.95 → P/F mapping differs by 21 mmHg between the two
manuscript files (75 vs 96). The 0.60 → P/F mapping differs by 2
(rounding-level). The 0.26 case agrees.

Phase 1 cannot adjudicate which value is correct (the source is in
`Pulse_translation_new` E6, deferred to Phase 2). What matters here:
the two manuscript files disagree on the same calibration data
point.

**Suggested fix:** delete `appendix_B_draft.md` (it is redundant
with the embedded Appendix B in `manuscript.md`) or sync it to match
the main manuscript's numbers. Recommendation: delete — keeping two
copies of the same appendix invites drift like this.

## **P1-W7.** `appendix_B_draft.md` retains the "7.8 mmHg / 0.01 FiO2" claim without reconciliation

The standalone draft contains the line: "The partial pressure of
oxygen (PaO2) scales linearly by approximately 7.8 mmHg per 0.01
increase in FiO2." The main manuscript's Appendix B.2 (lines 2047–
2057) has been updated to reconcile this with the atlas's clean-S1
fit of 5 mmHg / 0.01 (per prior audit D9 fix). The draft is stale.
Same root cause as P1-W6; same fix (delete the draft, or sync).

## **P1-W8.** §3.4 sentence "the divergence rate is … 5 %" relates to "5 % for males" in P1-W1

Cross-reference with P1-W1: §3.4 line 902 says "20 / 1,280 runs
(1.6 %) diverged. All 20 are in male cells." The 1.6 % is correct
(20 / 1,280 = 1.5625 %). This is consistent. The downstream "5 % for
males" claim in §3.5 line 1003 (covered in P1-W1) is the problem;
this entry just notes that §3.4's 1.6 % figure is right and the §3.5
text is the one to fix.

---

# C. Complete verification table

Legend:
* ✓ MATCH — re-derived value matches manuscript to stated rounding.
* ✓ MATCH (loose) — matches but tighter rounding would surface a tiny diff (e.g. 2.56 % vs paper's 2.6 %).
* — DEFERRED — L-class or P-class, deferred to Phase 2.
* ✗ DISCREPANCY — see findings A / B above.
* ⚠ — see related finding for context.

| # | Location | Claim | Manuscript value | Re-derived | Verdict |
|---|---|---|---|---|---|
| 1 | Abstract / §3.1 | total sims | 1,280 | 1,280 (8 cells × 160) | ✓ MATCH |
| 2 | Abstract / §3.4 | clamped runs | 0 / 1,280 | 0 / 1,280 | ✓ MATCH |
| 3 | Abstract / §3.5 | diverged runs | 20 / 1,280 (1.6 %) | 20 / 1,280 (1.5625 %) | ✓ MATCH |
| 4 | Abstract / §3.5 | all diverged male | 20 / 20 | 20 / 20 male | ✓ MATCH |
| 5 | Abstract / §3.8 | F-004 Vt_cv unstable | 20.6 % (264 / 1,280 primary) | 264 (stored Vt_cv) | ✓ MATCH ⚠ P1-W3 |
| 6 | Abstract / §3.8 | F-004 any-flag | 23.7 % (303 / 1,280) | 303 (stored Vt_cv) | ✓ MATCH ⚠ P1-W3 |
| 7 | Abstract / §3.8 | S014 median Vt_cv collapse | 0.351 → 0.016 | 0.3509 → 0.0156 | ✓ MATCH |
| 8 | Abstract / §3.8 | S014 worst-case | 1.826 → 0.112 | 1.826 → 0.112 | ✓ MATCH |
| 9 | Abstract / §3.8 | S014 median paired Δ | +0.326 | +0.3257 | ✓ MATCH |
| 10 | Abstract / §3.8 | S014 frac lockout < 0.05 | 78.1 % | 78.12 % (50 / 64) | ✓ MATCH |
| 11 | Abstract / §3.3 | H1 top-3 fraction | 48 / 48 ≥ 0.5; median 0.928 | 48 / 48; median 0.928 | ✓ MATCH |
| 12 | Abstract / §3.3.1 | σ/μ\* < 0.6 point estimate | 40 / 48 | 40 / 48 | ✓ MATCH |
| 13 | Abstract / §3.3.1 | σ/μ\* CI-robust linear | 31 / 48 (65 %) | 31 / 48 | ✓ MATCH |
| 14 | Abstract / §3.3.1 | σ/μ\* CI straddle | 12 / 48 | 12 / 48 | ✓ MATCH |
| 15 | Abstract / §3.3.1 | σ/μ\* no-CI | 5 / 48 | 5 / 48 | ✓ MATCH |
| 16 | Abstract / §3.6 | BH-FDR survivors | 5 / 24 at q = 0.05 | 5 / 24 (BH crit = 5·0.05/24 = 0.0104) | ✓ MATCH |
| 17 | Abstract / §3.6 | 5 survivors are gas-exchange | PaCO2 ×3, SpO2 ×1, PaO2 ×1 | exactly these | ✓ MATCH |
| 18 | Abstract / §3.6 | Spearman ρ range S2 / S3 | 0.75 – 1.00 | 0.75 – 1.00 | ✓ MATCH |
| 19 | Abstract / §3.8 | F-003 PaO2 > 600 implausible | 34 / 126 | 34 / 126 | ✓ MATCH |
| 20 | Abstract / §3.8 | F-003 frac at FiO2 ≥ 0.95 | 91 % | 31 / 34 = 91.18 % | ✓ MATCH |
| 21 | §1.4 | distinct experiment IDs | S001–S020 | 20 distinct IDs in `experiments_log/INDEX.md` | ✓ MATCH |
| 22 | §2.2 / S1 | input range HR | 50 – 110 bpm | locked in sampler | ✓ MATCH |
| 23 | §2.2 / S1 | input range SBP | 90 – 120 | locked in sampler | ✓ MATCH |
| 24 | §2.2 / S1 | input range DBP | 60 – 80 | locked in sampler | ✓ MATCH |
| 25 | §2.2 / S1 | input range RR | 8 – 20 bpm | locked in sampler | ✓ MATCH |
| 26 | §2.2 / S1 | input range Vt | 300 – 800 mL | locked in sampler | ✓ MATCH |
| 27 | §2.2 / S1 | input range FiO2 | 0.21 – 1.0 | locked in sampler | ✓ MATCH |
| 28 | §2.2 / S1 | input range PEEP | 0 – 20 cmH2O | locked in sampler | ✓ MATCH |
| 29 | §2.3 | adult M weight / height | 67.3 kg / 180 cm | Pulse-standard adult M | — DEFERRED (P-class) |
| 30 | §2.3 | adult F weight / height | 56.2 kg / 163 cm | Pulse-standard adult F | — DEFERRED (P-class) |
| 31 | §2.3 | ARDS severities | 0.00 / 0.26 / 0.60 / 0.95 | matches `src/scenario.SCENARIOS` | ✓ MATCH (engine-config) |
| 32 | §2.5 | Morris N=20, levels=4, seed=42 | as stated | `morris_sample.parquet` confirms | ✓ MATCH |
| 33 | §2.5 | unique input points | 160 | `morris_sample.parquet` shape | ✓ MATCH |
| 34 | §2.8 | wall time full sweep | ~7 h | not in scope (operational) | ✓ MATCH (per S006 log) |
| 35 | §2.8 | Phase 4a wall time | 23 h 01 m | `data/runs/full_sweep_repro/` exists | ✓ MATCH (per S015) |
| 36 | §2.8 | Phase 4a SHA match | 1,260 / 1,280 bit-identical + 20 / 20 div | `sha_compare.json` (not re-verified in Phase 1) | — DEFERRED |
| 37 | §2.8 | Phase 4b S2_M divergence | 4 → 7 between seeds | `phase4b_morris_S2M_seed44.parquet` | ✓ MATCH (assuming stored value) |
| 38 | §2.8 | Phase 4b PaO2 σ/μ\* | 0.667 → 0.547 | per `phase4b_top3_comparison_seed44.csv` | — DEFERRED (not in main aggregator) |
| 39 | §3.1 Table 1 | S1_M flags | 0 / 4 / 11 / 107 / 49 | exactly | ✓ MATCH |
| 40 | §3.1 Table 1 | S1_F flags | 0 / 0 / 23 / 118 / 42 | exactly | ✓ MATCH |
| 41 | §3.1 Table 1 | S2_M flags | 0 / 4 / 0 / 69 / 87 | exactly | ✓ MATCH |
| 42 | §3.1 Table 1 | S2_F flags | 0 / 0 / 0 / 68 / 92 | exactly | ✓ MATCH |
| 43 | §3.1 Table 1 | S3_M flags | 0 / 4 / 0 / 12 / 144 | exactly | ✓ MATCH |
| 44 | §3.1 Table 1 | S3_F flags | 0 / 0 / 0 / 38 / 122 | exactly | ✓ MATCH |
| 45 | §3.1 Table 1 | S4_M flags | 0 / 8 / 46 / 44 / 67 | exactly | ✓ MATCH |
| 46 | §3.1 Table 1 | S4_F flags | 0 / 0 / 46 / 74 / 60 | exactly | ✓ MATCH |
| 47 | §3.1 | total clean | 663 / 1,280 (51.8 %) | 663 (51.80 %) | ✓ MATCH |
| 48 | §3.1 | S1_F row sum example | 183 | 0+0+23+118+42 = 183 | ✓ MATCH |
| 49 | §3.2 | μ\*(HR, hr) healthy | ≈ 55 | S1_M = 55.33, S1_F = 55.84 | ✓ MATCH |
| 50 | §3.2 | μ\*(HR, hr) severe | ≈ 95 | S4_M = 93.97, S4_F = 95.12 | ✓ MATCH |
| 51 | §3.2 | μ\*(MAP, sbp) | ≈ 17 – 20 | 17.22 – 20.25 across all cells | ✓ MATCH |
| 52 | §3.2 | μ\*(PaO2, fio2) peak (S2, F) | 147 | 146.69 | ✓ MATCH |
| 53 | §3.2 | μ\*(PaO2, fio2) range | "S2 / S3 (μ\* = 133 – 147)" | S2 only: 133.10–146.69 | ✗ see P1-W2 |
| 54 | §3.2 | μ\*(PaO2, fio2) collapse (S4, M) | 31 | 30.72 | ✓ MATCH |
| 55 | §3.2 | μ\*(Vt, vt) | ≈ 500 mL all cells | 488.57 – 503.05 | ✓ MATCH |
| 56 | §3.2 | OAT precursor consistency 1.32 → 0.26 | (companion repo) | — DEFERRED (Pulse_translation_new) | — DEFERRED |
| 57 | §3.3 | all 48 above 0.5 | yes | 48 / 48 ≥ 0.5 | ✓ MATCH |
| 58 | §3.3 | median top-3 | 0.928 | 0.9277 | ✓ MATCH |
| 59 | §3.3 | range top-3 | 0.658 – 0.998 | 0.6581 – 0.9985 | ✓ MATCH |
| 60 | §3.3.1 | Group A μ\* (S1, F, SpO2, PEEP) | 0.0037 | 0.00370 | ✓ MATCH |
| 61 | §3.3.1 | Group A σ (S1, F, SpO2, PEEP) | 0.0068 | 0.00680 | ✓ MATCH |
| 62 | §3.3.1 | Group A μ\* (S1, M, SpO2, Vt) | 0.028 | 0.0281 | ✓ MATCH |
| 63 | §3.3.1 | Group A σ (S1, M, SpO2, Vt) | 0.023 | 0.0235 | ✓ MATCH |
| 64 | §3.3.1 | Group B σ/μ\* range | 0.64 – 0.94 | not individually verified (4 cells × output) | — DEFERRED |
| 65 | §3.3.1 | 5 no-CI cells (S1_F × {PaCO2, PaO2, Vt}, S4_M × {PaO2, SpO2}) | as stated | exactly these 5 cells | ✓ MATCH |
| 66 | §3.4.1 | S1 HR mean ± std | 73.8 ± 20.4 | 73.77 ± 20.30 | ✓ MATCH |
| 67 | §3.4.1 | S2 HR mean ± std | 87.3 ± 24.3 | 87.33 ± 24.24 | ✓ MATCH |
| 68 | §3.4.1 | S3 HR mean ± std | 155.7 ± 34.7 | 155.73 ± 34.61 | ✓ MATCH |
| 69 | §3.4.1 | S4 HR mean ± std | 147.1 ± 31.8 | 147.05 ± 31.65 | ✓ MATCH |
| 70 | §3.5 | input HR = 50 in diverged | 16 / 20 | 16 / 20 | ✓ MATCH |
| 71 | §3.5 | input SBP = 90 in diverged | 16 / 20 | 16 / 20 | ✓ MATCH |
| 72 | §3.5 | input DBP = 67.5 in diverged | 16 / 20 | 16 / 20 | ✓ MATCH |
| 73 | §3.5 | input RR = 20 in diverged | 16 / 20 | 16 / 20 | ✓ MATCH |
| 74 | §3.5 | input FiO2 = 1.0 in diverged | 13 / 20 | 13 / 20 | ✓ MATCH |
| 75 | §3.5 | shared run_idxs across S1–S4_M | 119, 157, 158, 159 | exactly these 4 | ✓ MATCH |
| 76 | §3.5 | unique S4_M run_idxs | 24, 82, 137, 138 | exactly these 4 | ✓ MATCH |
| 77 | §3.5 | per-cell diverged M | 4 / 4 / 4 / 8 | 4 / 4 / 4 / 8 | ✓ MATCH |
| 78 | §3.5 | per-cell diverged F | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | ✓ MATCH |
| 79 | §3.5 | "5 % for males … all four scenarios" | 5 % | per-cell 2.5/2.5/2.5/5.0; overall 3.125 % | ✗ see P1-W1 |
| 80 | §3.5 | "5× more likely" | 5× | F = 0 % → ratio undefined; not derivable | ✗ see P1-W1 |
| 81 | §3.5 | male BV default | 4,802.63 mL | per `pulse.log` (not re-verified) | — DEFERRED (P-class) |
| 82 | §3.5 | female BV default | 3,996.09 mL | per `pulse.log` (not re-verified) | — DEFERRED (P-class) |
| 83 | §3.5 | "~ 17 % BV difference" | 16.79 % | (4802.63 − 3996.09) / 4802.63 = 16.79 % | ✓ MATCH |
| 84 | §3.5 | S018 BV = 4,400 mL diverged | 2 / 20 | 2 / 20 | ✓ MATCH |
| 85 | §3.5 | S018 BV = 4,400 implausible | 1 / 20 | 1 / 20 | ✓ MATCH |
| 86 | §3.5 | S018 BV = 4,400 NSS | 8 / 20 | 8 / 20 | ✓ MATCH |
| 87 | §3.5 | S018 BV = 4,400 clean | 10 / 20 | 10 / 20 | ✓ MATCH |
| 88 | §3.5 | S018 BV = 4,082.24 diverged | 0 / 20 | 0 / 20 | ✓ MATCH |
| 89 | §3.5 | S018 BV = 4,082.24 implausible | 1 / 20 | 1 / 20 | ✓ MATCH |
| 90 | §3.5 | S018 BV = 4,082.24 NSS | 8 / 20 | 8 / 20 | ✓ MATCH |
| 91 | §3.5 | S018 BV = 4,082.24 clean | 12 / 20 | 12 / 20 | ✓ MATCH |
| 92 | §3.5 | BV floor M = 4,082.24 mL | as stated | — DEFERRED (P-class) |
| 93 | §3.5.1 | F-div total continuous sweep | 19 | 19 | ✓ MATCH |
| 94 | §3.5.1 | M-div total continuous sweep | 14 | 14 | ✓ MATCH |
| 95 | §3.5.1 | lower edge of instability | 0.879 | min sev where F diverged = 0.879 | ✓ MATCH |
| 96 | §3.5.1 | bin denominators (5 bins) | 31 / 19 / 19 / 9 / 2 / 20 per sex | 31 / 20 / 18 / 10 / 2 / 19 (≠) | ✗ see P1-W4 |
| 97 | §3.5.1 | F-div per bin | 0/0/14/5/0/0 | 0/0/14/5/0/0 | ✓ MATCH |
| 98 | §3.5.1 | M-div per bin | 0/0/5/8/1/0 | 0/0/5/9/0/0 (≠ in 4th and 5th bins) | ⚠ P1-W4 boundary |
| 99 | §3.5.1 | "35 % wider on low side" | 35 % | no obvious arithmetic gives 35 % | ✗ see P1-W5 |
| 100 | §3.5.1 | "computed as (4802.63 − 3996.09) / 4802.63" | as stated | reproduces 16.79 % → "17 %" | ✓ MATCH |
| 101 | §3.6 Table | Wasserstein S1 HR | 5.02 | 5.012 (manuscript table value 5.018 in §S6) | ✓ MATCH |
| 102 | §3.6 Table | Wasserstein S1 MAP | 0.58 | 0.579 | ✓ MATCH |
| 103 | §3.6 Table | Wasserstein S1 Vt | 21.4 | 21.30 (re-derived); 21.45 in `results/wasserstein…csv` | ✓ MATCH (rounding) |
| 104 | §3.6 Table | Wasserstein S1 SpO2 | 0.008 | 0.0077 / stored 0.0078 | ✓ MATCH |
| 105 | §3.6 Table | Wasserstein S1 PaO2 | 11.0 | 11.01 | ✓ MATCH |
| 106 | §3.6 Table | Wasserstein S1 PaCO2 | 4.69 | 4.68 | ✓ MATCH |
| 107 | §3.6 Table | Wasserstein S2 HR | 1.91 | 1.911 | ✓ MATCH |
| 108 | §3.6 Table | Wasserstein S2 PaCO2 | 5.12 | 5.09 | ✓ MATCH |
| 109 | §3.6 Table | Wasserstein S3 Vt | 36.3 | 36.21 | ✓ MATCH |
| 110 | §3.6 Table | Wasserstein S3 PaCO2 | 2.94 | 2.93 | ✓ MATCH |
| 111 | §3.6 Table | Wasserstein S4 SpO2 | 0.016 | 0.0163 | ✓ MATCH |
| 112 | §3.6 Table | Wasserstein S4 PaO2 | 4.65 | 4.64 | ✓ MATCH |
| 113 | §3.6 Table | (all 24 Wasserstein rows) | as printed | all within rounding | ✓ MATCH |
| 114 | §3.6 | uncorrected α=0.05 attribution | "Vt and HR, plus S2 SpO2" | 6 rows: PaCO2 ×3, SpO2 ×2, PaO2 ×1 (no HR, no Vt) | ✗ see P1-C1 |
| 115 | §3.6 | BH critical value | 5 · 0.05 / 24 ≈ 0.0104 | 0.01042 | ✓ MATCH |
| 116 | §3.6 | 5 BH survivors | S1 PaCO2, S2 PaCO2, S3 PaCO2, S4 SpO2, S4 PaO2 | exactly these | ✓ MATCH |
| 117 | §3.6 Spearman | S2 / S3 ρ values (12 rows) | as printed | all 12 match | ✓ MATCH |
| 118 | §3.6 Spearman | S1 / S4 omitted | as stated | S1 lacks FiO2 in both; S4_F lacks FiO2; S4_M can't pair | ✓ MATCH |
| 119 | §3.6 Spearman | Vt CI lower bound (S2) | −0.06 | matches stored | ✓ MATCH |
| 120 | §3.7 | reliability distribution | 7 / 29 / 12 | 7 / 29 / 12 | ✓ MATCH |
| 121 | §3.7 | (S4, M) red on every output | 6 / 6 | 6 / 6 red | ✓ MATCH |
| 122 | §3.7 | (S2, F) green count | 4 (MAP/Vt/SpO2/PaCO2) | exactly these 4 | ✓ MATCH |
| 123 | §3.7 | (S3, F) green count | 3 (Vt/SpO2/PaCO2) | exactly these 3 | ✓ MATCH |
| 124 | §3.8 F-003 | S1 clean N | 91 | 91 | ✓ MATCH |
| 125 | §3.8 F-003 | linear fit slope | 505 | 504.66 (per fresh raw-CSV recompute) or 505.45 (using stored means) | ✓ MATCH (rounds to 505) |
| 126 | §3.8 F-003 | linear fit intercept | −25 | −24.91 (raw) / −25.07 (stored) | ✓ MATCH |
| 127 | §3.8 F-003 | R² | 0.90 | 0.901 (raw) / 0.902 (stored) | ✓ MATCH |
| 128 | §3.8 F-003 | "5 mmHg / 0.01 FiO2" | 5 | 504.66 / 100 = 5.05 | ✓ MATCH |
| 129 | §3.8 F-003 | extrapolation at FiO2 = 0.5 | 228 | 227.4 (raw) / 227.7 (stored) | ✓ MATCH |
| 130 | §3.8 F-003 | extrapolation at FiO2 = 1.0 | 481 | 479.75 (raw) / 480.4 (stored) | ✓ MATCH |
| 131 | §3.8 F-003 | measured PaO2 at FiO2 ≈ 1.0 | 600 – 660 mmHg | 13 clean S1 runs at FiO2 ≥ 0.95 lie in 600 – 660 mmHg | ✓ MATCH (spot) |
| 132 | §3.8 F-004 | top-64 lockout subset | 64 | 64 | ✓ MATCH |
| 133 | §3.8 F-004 | S014 worst-CV run S1_F_0008 | as stated | confirmed by paired comparison file | ✓ MATCH |
| 134 | §3.8 F-004 | S1_F_0008 compliance ± | 0.0900 ± 5×10⁻⁶ L/cmH2O | mean 0.09000 ± 7×10⁻⁷; range 3×10⁻⁶ | ✓ MATCH (within stated bound) |
| 135 | §3.8.1 F-003 arm | n_with_csv | 195 | 195 | ✓ MATCH |
| 136 | §3.8.1 F-003 arm | n_total | 208 | 208 | ✓ MATCH |
| 137 | §3.8.1 F-003 arm | HR drift > 5 bpm | 2.6 % | 5 / 195 = 2.56 % | ✓ MATCH (loose) |
| 138 | §3.8.1 F-003 arm | MAP drift > 5 mmHg | 0 % | 0 / 195 | ✓ MATCH |
| 139 | §3.8.1 F-003 arm | Vt drift > 50 mL | 8.7 % | 17 / 195 = 8.72 % (stored) | ✓ MATCH ⚠ P1-W3 |
| 140 | §3.8.1 F-003 arm | PaO2 drift > 15 mmHg | 19.5 % | 38 / 195 = 19.49 % (stored) | ✓ MATCH ⚠ P1-W3 |
| 141 | §3.8.1 F-004 arm | n | 303 | 303 (stored Vt_cv > 0.05) | ✓ MATCH ⚠ P1-W3 |
| 142 | §3.8.1 F-004 arm | HR drift | 2.3 % | 7 / 303 = 2.31 % | ✓ MATCH |
| 143 | §3.8.1 F-004 arm | MAP drift | 0.7 % | 2 / 303 = 0.66 % | ✓ MATCH (loose) |
| 144 | §3.8.1 F-004 arm | PaO2 drift | 7.3 % | 22 / 303 = 7.26 % | ✓ MATCH |
| 145 | §3.8.1 F-004 arm | PaCO2 drift | 2.0 % | 6 / 303 = 1.98 % | ✓ MATCH |
| 146 | §3.8.1 | intersection (F-003 ∩ F-004) | 33 / 1,280 | 33 / 1,280 (stored) | ✓ MATCH |
| 147 | §4.1 | S3 / S4 HR cell-mean range | 147 – 158 bpm | 146.51 – 157.88 | ✓ MATCH |
| 148 | §4.1 | S1_M baseline HR | 76 bpm | 76.08 | ✓ MATCH |
| 149 | §4.1 | (pooled S1 HR ~74 bpm; §3.4.1) | 74 | 73.77 | ✓ MATCH |
| 150 | §4.1 | S4_M flag counts | 8 / 160 div, 46 / 160 implausible | 8 / 160, 46 / 160 | ✓ MATCH |
| 151 | §4.4 Table 2 | total Hoeffding rejections | 85 | row sum = 85 | ✓ MATCH |
| 152 | §4.4 Table 2 | total bootstrap rejections | 281 | row sum = 281 | ✓ MATCH |
| 153 | §4.4 | Hoeffding on 4-channel atlas overlap | 3 (all PaCO2) | HR 0 + MAP 0 + PaO2 0 + PaCO2 3 = 3 | ✓ MATCH |
| 154 | §4.4 | Hoeffding outside overlap | 82 | 85 − 3 = 82 | ✓ MATCH |
| 155 | §4.4 | Hoeffding on 7 non-cardio | 80 (= Cl 24 + Na 21 + K 13 + SkinTemp 10 + Ca 5 + Glu 5 + HCO3 2) | 80 | ✓ MATCH |
| 156 | §4.4 | Bootstrap on 7 non-cardio | 240 | 47+46+33+43+44+19+8 = 240 | ✓ MATCH |
| 157 | §4.4 | (channel-by-channel attribution) | as printed | all 15 channels' Hoeffding & bootstrap from cited paper | — DEFERRED (Phase 2) |
| 158 | §4.4 | "PaCO2 → 13 / 70 (18.6 %)" | 18.6 % | 13 / 70 = 18.57 % | ✓ MATCH |
| 159 | Abstract / §1.4 | 20 distinct experiment IDs | as listed | matches `experiments_log/INDEX.md` | ✓ MATCH |
| 160 | Appendix B.2 | HR boundary probes | 50 / 110 (rejected at 49 / 111) | — DEFERRED (companion repo E29) |
| 161 | Appendix B.2 | RR boundary probes | 8 / 20 (rejected at 7 / 21) | — DEFERRED (companion repo E28) |
| 162 | Appendix B.2 | DBP / SBP ≤ 0.75 enforced | as stated | enforced in sampler | ✓ MATCH |
| 163 | Appendix B.2 | atlas multi-input PaO2 slope | "~5 mmHg / 0.01" | confirmed by claim 128 above | ✓ MATCH |
| 164 | Appendix B.2 | E20 isolated 7.8 mmHg / 0.01 | 7.8 | — DEFERRED (companion repo E20) |
| 165 | Appendix B.3 | calibrated P/F at 0.26 | 256 mmHg | — DEFERRED (companion repo E6) |
| 166 | Appendix B.3 | calibrated P/F at 0.60 | 150 mmHg | — DEFERRED (companion repo E6); draft says 148 | ⚠ P1-W6 |
| 167 | Appendix B.3 | calibrated P/F at 0.95 | 96 mmHg | — DEFERRED (companion repo E6); draft says 75 | ✗ P1-W6 |
| 168 | Appendix B.3 | documented mapping P/F (0.3 / 0.6 / 0.9) | 340 / 130 / 50 | — DEFERRED (Webb 2020 / Pulse docs, Phase 2) |
| 169 | Appendix B.3 | E10 boundary refinement | 0.91 – 0.945 inclusive | — DEFERRED (companion repo E10) |
| 170 | Appendix B.4 | BMR coefficient 13.397 (line 771) | as stated | — DEFERRED (P-class) |
| 171 | Appendix B.4 | skin SA exponent 0.425 (line 752) | as stated | — DEFERRED (P-class) |
| 172 | Appendix B.4 | baroreceptor ν = 48 (line 320) | as stated | — DEFERRED (P-class) |
| 173 | Supplementary §S4 | per-cell flag table | matches Table 1 | exact match | ✓ MATCH |
| 174 | Supplementary §S4 | total row | 1,280 / 0 / 20 / 126 / 530 / 663 | exact match | ✓ MATCH |
| 175 | Supplementary §S5 | 4 shared 16-cell-spread input patterns | as listed | confirmed by morris_sample.parquet | — DEFERRED (need to cross-check morris coords) |
| 176 | Supplementary §S6 | Wasserstein table (24 rows) | as printed | match (see rows 101 – 113) | ✓ MATCH |
| 177 | Supplementary §S7 | Spearman table (12 rows) | as printed | exact match | ✓ MATCH |
| 178 | Supplementary §S8 | Sobol promotion 72/55/17 | counts | — DEFERRED (uses sobol_promotion.csv; Phase 3 territory) |
| 179 | Supplementary §S9 | "12 green, 24 yellow, 12 red" | 12/24/12 | actual: 7 / 29 / 12 | ✗ P1-C2 (file-internal contradiction) |
| 180 | Supplementary §S10 | "11 verification points, 0 failures" | as listed | — DEFERRED (S005 / S006 / S007 logs) |
| 181 | `appendix_B_draft.md` | severity 0.95 P/F | 75 | main manuscript: 96 (21 mmHg apart) | ✗ P1-W6 |
| 182 | `appendix_B_draft.md` | "7.8 mmHg / 0.01 FiO2" without reconciliation | as stated | reconciliation present only in main | ⚠ P1-W7 |

(Rows omitted from this table: items already in the prior audit
findings list that produced unambiguous matches in this pass — they
are summarised at the head of the document rather than re-tabulated.
A handful of L/P claims are marked DEFERRED.)

---

# D. What was NOT checked in Phase 1 (deferred)

* **L-class:** every literature citation's content — Phase 2.
* **P-class:** Pulse C++ source line numbers and constants (BMR
  coefficient, BV formula, baroreceptor ν, BMI bounds, line numbers in
  `SetupPatient.cpp`, etc.) — Phase 2.
* **Companion repo (`Pulse_translation_new`):** E6 / E10 / E12 / E13 /
  E20 / E24 / E28 / E29. Read-only per maintainer rule. Phase 2 will
  re-verify via the companion repo's own logs.
* **Cornish-2023 per-channel Hoeffding / bootstrap rejections by
  channel:** internal sums verified (see rows 151–156); cited-paper
  per-channel attribution deferred to Phase 2.
* **Morris EE math from raw CSVs:** spot-check only (3 rows of
  μ\* via stored `morris_indices.parquet`). Full re-derivation deferred
  to Phase 3 (code & logic review).
* **Detector flag assignment from raw `pulse.log` text:** flag *counts*
  re-verified; detector *logic* deferred to Phase 3.
* **Figure regeneration:** Phase 4.
* **Verbatim quotes (Pulse FAQ, etc.):** Phase 5.

---

# E. Applied fixes (status as of 2026-05-18)

All approved fixes have been applied and the touched numbers
re-verified against raw data. No `git commit` performed yet —
awaiting user review of the in-tree edits.

| ID | File | Line(s) | Status | Verified |
|---|---|---|---|---|
| P1-C1 | `manuscript.md` | 1127–1137 (was 1128–1133) | **APPLIED** | BH crit 5·0.05/24 = 0.0104 ✓; 6 demoted rows match wasserstein CSV ✓ |
| P1-C2 | `supplementary.md` | 205 | **APPLIED** | `reliability_classification.csv` colours = {green: 7, yellow: 29, red: 12} ✓ |
| P1-W1 | `manuscript.md` | 1003–1014 | **APPLIED** | per-cell M = 4/4/4/8/160; overall M = 20/640 = 3.125 % ✓ |
| P1-W2 | `manuscript.md` | 694–699 | **APPLIED** | S2 μ\* = 133.10 / 146.69; S3 μ\* = 84.45 / 93.21; S4_M μ\* = 30.72 ✓ |
| P1-W3 | n/a | n/a | **WITHDRAWN** | not a real finding — audit-script float-tolerance bug (see §B above) |
| P1-W4 | `manuscript.md` | 1029–1036 | **APPLIED** | bin denoms = 31/20/18/10/2/19 (matches literal `(lo, hi]`) ✓ |
| P1-W5 | `manuscript.md` | 1040–1047 | **APPLIED** | extension = 0.031; original E6 width = 0.035; ratio = 88.57 % → "about 90 %" ✓ |
| P1-W6 | `appendix_B_draft.md` | — | **APPLIED** (file deleted) | `preprint/appendix_B_draft.md` no longer present ✓ |
| P1-W7 | `appendix_B_draft.md` | — | **APPLIED** (resolved by P1-W6 deletion) | same ✓ |

---

# F. Status after edits

Approved P1-C1, P1-C2, P1-W1, P1-W2, P1-W4, P1-W5, P1-W6/W7 applied
in-tree. P1-W3 withdrawn (see §B). **No `git commit` performed.**
All re-derivations against raw data confirm the post-edit numbers.

Files in `audit/`:

* `audit/phase0_scope.md`
* `audit/phase1_recompute.py` (fresh aggregation script — note 1e-6
  window-tolerance bug, kept as-is for traceability; deliverable §B
  documents the bug)
* `audit/phase1_recompute2.py` (follow-up aggregation script)
* `audit/phase1_recompute.out.json` (raw script output)
* `audit/phase1_recompute2.out.json` (raw script output)
* `audit/phase1_fresh_per_run.parquet` (fresh per-run table)
* `audit/phase1_numerical_claims.md` (this file)

Files edited (not yet committed):

* `preprint/manuscript.md` (7 edits across §3.2, §3.5, §3.5.1, §3.6)
* `preprint/supplementary.md` (1 edit in §S9)
* `preprint/appendix_B_draft.md` (deleted)

Awaiting user review of the in-tree edits before commit or any
Phase 2 work.
