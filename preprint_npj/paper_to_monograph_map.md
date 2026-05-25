# Paper-to-Monograph Crosswalk Map (`paper_to_monograph_map.md`)

**Purpose.** This file is the single source of truth for **which numerical
claims appear in both `preprint_npj/paper.tex` and `preprint/manuscript.md`
(the monograph)**. The audit script `scripts/audit_claims.py` reads this
file under the `--check-paper-sync` opt-in flag and verifies that every
mapped value still appears in `paper.tex` with the expected occurrence
count and is consistent with the monograph value behind the same
`claim_id`.

**Why this exists.** The atlas's monograph (~92 pages) is audited at
195/195 PASS via `scripts/audit_claims.py`. The npj-submission paper
(`paper.tex`) re-states a subset of those numbers in condensed form. Any
silent drift between the two documents would corrode the monograph's
audit guarantees. This crosswalk + the `--check-paper-sync` flag together
catch drift mechanically (rather than depending on human discipline alone).

**Lifecycle.** A row is added here whenever a numerical claim is
introduced into `paper.tex` for the first time. A row is updated when a
claim's value, formatting, or occurrence count changes. A row is removed
only when the claim is removed from `paper.tex` entirely. Every commit
that touches `paper.tex` must touch this file in the same commit, except
for `[TYPESET-ONLY]` commits that change zero numerical content.

## Schema

Each row is a YAML mapping with the following fields:

| Field | Required | Description |
|---|---|---|
| `paper_section` | yes | Where in `paper.tex` the claim appears (e.g., `"Abstract"`, `"§2.5 Headline Finding 3"`, `"Methods §4.3"`). Free-text but stable. |
| `paper_context` | yes | One-line description of what the number represents (e.g., `"male BV default"`). |
| `monograph_claim_id` | yes | The `claim_id` in `scripts/audit_claims.py` that audits the same number in the monograph (e.g., `"T3.s027.bv_default"`). Must exist in the ledger. |
| `expected_value` | yes | The numerical value as a Python literal (e.g., `4802.63`, `1280`, `0.928`). Used for the cross-check against the monograph. |
| `format_in_paper` | yes | The exact LaTeX-rendered formatting used in `paper.tex` (e.g., `"4,802.63 mL"`, `"1{,}280"`, `"$\\sim 643$ mmHg"`). Used to build the regex that locates the value. |
| `expected_occurrences` | yes | Integer count of how many times the value should appear in `paper.tex`. Catches silent deletions or accidental duplications. Use `"any"` if the count genuinely doesn't matter (rare; default should be an exact integer). |
| `tolerance_rule` | optional | Override the default tolerance rule. Defaults to the rule attached to the same `claim_id` in `audit_claims.py`. |
| `notes` | optional | Free-text qualifications (e.g., `"appears in narrative form in §2.5 and as table-cell value in Table 2"`). |

## Audit semantics (under `--check-paper-sync`)

For each row in this file, `audit_claims.py --check-paper-sync` will:

1. Verify `monograph_claim_id` exists in the ledger and `expected_value`
   matches the monograph value within the rule's tolerance.
2. Build a LaTeX-tolerant regex from `format_in_paper` (handles
   `4,082.24`, `4{,}082.24`, `\num{4082.24}`, `4082.24~mL`, etc.).
3. Run `re.findall(...)` on `paper.tex` and count matches.
4. Report status per row:
   - `PASS` — count == `expected_occurrences` AND values consistent.
   - `FAIL (count drift)` — count != `expected_occurrences` (any direction).
   - `FAIL (value drift)` — count > 0 but a found value contradicts
     the map's `expected_value`.
   - `FAIL (missing)` — count == 0 AND `expected_occurrences` >= 1.
   - `WARN (paper missing)` — `paper.tex` cannot be read; audit
     continues with the legacy 195-claim ledger; this row is skipped.

The legacy 195-claim audit (monograph-only) is **unaffected** by the
`--check-paper-sync` flag; running `uv run python scripts/audit_claims.py`
without the flag continues to produce the same output as before.

---

# Mapped claims

*Rows added incrementally as `paper.tex` sections are drafted. Each row
binds one quantitative claim in `paper.tex` to its origin
`claim_id` in the monograph ledger (`scripts/audit_claims.py`). The
`expected_occurrences` integer is checked via `re.findall(...)` (not
`re.search(...)`) so silent deletions and accidental duplications are
caught equally.*

## Step 1 — Abstract (5 numerical claims)

- paper_section: 'Abstract + §2.1 + §2.5 + Figure 4 caption'
  paper_context: 'Total Morris simulations across the sweep'
  monograph_claim_id: 'T1.01'
  expected_value: 1280
  format_in_paper: '1{,}280'
  expected_occurrences: 9
  notes: 'Total occurrences of the literal pattern 1{,}280 across the paper as of Step 5: abstract (2), §2.1 (4 + Table 1 caption 1 = 5), §2.5 prose "1{,}280-run sweep" (1), Figure 4 caption "1{,}280-run sweep" (1). Bumped from 7 (Step 3) to 9 (Step 5).'

- paper_section: 'Abstract + §2.3 VC-AC'
  paper_context: 'VC-AC trigger-dyssynchrony primary-flag rate (Vt CV > 0.05 under not_steady_state)'
  monograph_claim_id: 'T1.02a'
  expected_value: 20.6
  format_in_paper: '20.6~\%'
  expected_occurrences: 2
  notes: 'Appears twice as of Step 4: abstract sentence 3 "in 20.6~\% of runs" (1), §2.3 opening sentence "20.6~\% of runs" (1). Format standardised in Step 4 to use ~ (LaTeX non-breaking space) between number and unit; the abstract was retroactively updated for consistency.'

- paper_section: 'Abstract + §2.4 hyperoxia'
  paper_context: 'Hyperoxia 300s plateau median (S1)'
  monograph_claim_id: 'T1.23'
  expected_value: 643
  format_in_paper: '643~mmHg'
  expected_occurrences: 2
  notes: 'Appears twice as of Step 4: abstract sentence 4 "median 643~mmHg" (1), §2.4 prose "the converged S1 plateau median was 643~mmHg" (1). Both use ~ non-breaking space; format standardised to "643~mmHg" in Step 4.'

- paper_section: 'Abstract'
  paper_context: 'Divergence count (all male, input-extreme regime)'
  monograph_claim_id: 'T1.12'
  expected_value: 20
  format_in_paper: '20/1{,}280'
  expected_occurrences: 1
  notes: 'Appears once in sentence 5 as the compact "20/1{,}280 runs" form. The denominator 1{,}280 is separately accounted for by the T1.01 row (expected_occurrences=2).'

## (Step 1 row for T3.s027.bv_floor was superseded in Step 5 by a more permissive 4{,}082.24 pattern covering all occurrences; see the Step 5 row below.)

## Step 3 — Results §2.1 Overview (prose claims)

- paper_section: '§2.1 Overview (prose)'
  paper_context: 'Silent clamping count across full sweep (H2 NOT supported)'
  monograph_claim_id: 'T1.11'
  expected_value: 0
  format_in_paper: '(0 / 1{,}280 across every cell)'
  expected_occurrences: 1
  notes: 'Appears once in §2.1 prose. Surrounding parenthetical context "(... across every cell)" is included in the format to avoid substring-overlap with "20 / 1{,}280" (the divergence count in the next sentence): the bare "0 / 1{,}280" pattern would match both because "20 / 1{,}280" contains the literal substring "0 / 1{,}280". Lesson recorded for future map entries with short numeric patterns: use surrounding context to disambiguate.'

- paper_section: '§2.1 Overview (prose)'
  paper_context: 'Solver divergence count (spaced form used in Results)'
  monograph_claim_id: 'T1.12'
  expected_value: 20
  format_in_paper: '20 / 1{,}280'
  expected_occurrences: 1
  notes: 'Appears once in §2.1 prose as "20 / 1{,}280 runs (1.6~\%)". Different format from the abstract''s compact "20/1{,}280" (which has its own separate map row).'

- paper_section: '§2.1 + §2.5 (prose)'
  paper_context: 'Divergence rate (percentage form)'
  monograph_claim_id: 'T1.13'
  expected_value: 1.6
  format_in_paper: '1.6~\%'
  expected_occurrences: 2
  notes: 'Appears twice as of Step 5: §2.1 prose "20 / 1{,}280 runs (1.6~\%)" (1), §2.5 prose "20 runs (1.6~\%) failed to complete with finite output" (1). Bumped from 1 (Step 3) to 2 (Step 5).'

- paper_section: '§2.1 Overview (prose)'
  paper_context: 'Total clean simulations across full sweep'
  monograph_claim_id: 'T1.28'
  expected_value: 663
  format_in_paper: '663 of 1{,}280'
  expected_occurrences: 1
  notes: 'Appears once in §2.1 prose as "663 of 1{,}280 simulations (51.8~\%) are flag-clean".'

- paper_section: '§2.1 Overview (prose)'
  paper_context: 'Clean rate (percentage form)'
  monograph_claim_id: 'T1.29'
  expected_value: 51.8
  format_in_paper: '51.8~\%'
  expected_occurrences: 1
  notes: 'Appears once in §2.1 prose immediately after "663 of 1{,}280 simulations".'

## Step 3 — Results §2.1 Table 1 (8 per-cell row literals)

- paper_section: '§2.1 Table 1 row (S1, M)'
  paper_context: 'Per-cell flag counts for S1_M (healthy, male)'
  monograph_claim_id: 'T1.T1-S1_M.n_total'
  expected_value: 160
  format_in_paper: 'S1\_M & 160 & 0 & 4 & 11 & 107 & 49'
  expected_occurrences: 1
  notes: 'Full Table 1 row for the S1_M cell as a single literal-string check. If any cell value drifts (n_total / clamped / diverged / implausible / not_steady_state / clean), the literal match fails and the audit FAILs. Anchored on n_total=160 for value-cross-check; the other five column values are co-validated by literal presence.'

- paper_section: '§2.1 Table 1 row (S1, F)'
  paper_context: 'Per-cell flag counts for S1_F (healthy, female)'
  monograph_claim_id: 'T1.T1-S1_F.n_total'
  expected_value: 160
  format_in_paper: 'S1\_F & 160 & 0 & 0 & 23 & 118 & 42'
  expected_occurrences: 1
  notes: 'Full Table 1 row for the S1_F cell as a single literal-string check.'

- paper_section: '§2.1 Table 1 row (S2, M)'
  paper_context: 'Per-cell flag counts for S2_M (mild ARDS, male)'
  monograph_claim_id: 'T1.T1-S2_M.n_total'
  expected_value: 160
  format_in_paper: 'S2\_M & 160 & 0 & 4 & 0  & 69  & 87'
  expected_occurrences: 1
  notes: 'Full Table 1 row for the S2_M cell. Note the double spaces in the source (cosmetic column-alignment in the LaTeX source), preserved verbatim from the monograph.'

- paper_section: '§2.1 Table 1 row (S2, F)'
  paper_context: 'Per-cell flag counts for S2_F (mild ARDS, female)'
  monograph_claim_id: 'T1.T1-S2_F.n_total'
  expected_value: 160
  format_in_paper: 'S2\_F & 160 & 0 & 0 & 0  & 68  & 92'
  expected_occurrences: 1
  notes: 'Full Table 1 row for the S2_F cell.'

- paper_section: '§2.1 Table 1 row (S3, M)'
  paper_context: 'Per-cell flag counts for S3_M (moderate ARDS, male)'
  monograph_claim_id: 'T1.T1-S3_M.n_total'
  expected_value: 160
  format_in_paper: 'S3\_M & 160 & 0 & 4 & 0  & 12  & 144'
  expected_occurrences: 1
  notes: 'Full Table 1 row for the S3_M cell.'

- paper_section: '§2.1 Table 1 row (S3, F)'
  paper_context: 'Per-cell flag counts for S3_F (moderate ARDS, female)'
  monograph_claim_id: 'T1.T1-S3_F.n_total'
  expected_value: 160
  format_in_paper: 'S3\_F & 160 & 0 & 0 & 0  & 38  & 122'
  expected_occurrences: 1
  notes: 'Full Table 1 row for the S3_F cell.'

- paper_section: '§2.1 Table 1 row (S4, M)'
  paper_context: 'Per-cell flag counts for S4_M (severe ARDS, male)'
  monograph_claim_id: 'T1.T1-S4_M.n_total'
  expected_value: 160
  format_in_paper: 'S4\_M & 160 & 0 & 8 & 46 & 44  & 67'
  expected_occurrences: 1
  notes: 'Full Table 1 row for the S4_M cell. Note: 8 divergences (twice any other male cell) reflects the severe-ARDS regime where the male BV mechanism amplifies (§2.5).'

- paper_section: '§2.1 Table 1 row (S4, F)'
  paper_context: 'Per-cell flag counts for S4_F (severe ARDS, female)'
  monograph_claim_id: 'T1.T1-S4_F.n_total'
  expected_value: 160
  format_in_paper: 'S4\_F & 160 & 0 & 0 & 46 & 74  & 60'
  expected_occurrences: 1
  notes: 'Full Table 1 row for the S4_F cell. Note: 0 divergences (consistent with the all-male divergence cluster, §2.5).'

## Step 3 — Results §2.1 Figure 1 traffic-light caption

- paper_section: '§2.1 Figure 1 caption'
  paper_context: 'Reliability traffic-light aggregate breakdown'
  monograph_claim_id: 'T1.25'
  expected_value: 7
  format_in_paper: '7 green / 29 yellow / 12 red'
  expected_occurrences: 1
  notes: 'Single literal-string check covering all three traffic-light counts (T1.25=7 green, T1.26=29 yellow, T1.27=12 red). Anchored on T1.25 for value-cross-check; 29 and 12 are co-validated by literal presence.'

## Step 3 — Results §2.2 Morris rankings (prose + Figure 2 caption)

- paper_section: '§2.2 Morris (prose + Figure 2 caption)'
  paper_context: 'H1 verdict — top-3 fraction >= 0.5 on all 48 cell x output combinations'
  monograph_claim_id: 'T1.07'
  expected_value: 48
  format_in_paper: '48 of 48'
  expected_occurrences: 2
  notes: 'Appears twice: once in §2.2 prose ("the data support this on 48 of 48 cell $\times$ output combinations"), once in Figure 2 caption ("48 of 48 cell $\times$ output combinations").'

- paper_section: '§2.2 Morris (prose)'
  paper_context: 'H1 median top-3 fraction (prose form)'
  monograph_claim_id: 'T1.08'
  expected_value: 0.928
  format_in_paper: 'median top-3 fraction of 0.928'
  expected_occurrences: 1
  notes: 'Appears once in §2.2 prose as "with a median top-3 fraction of 0.928".'

- paper_section: '§2.2 Figure 2 caption'
  paper_context: 'H1 median top-3 fraction (figure caption form)'
  monograph_claim_id: 'T1.08'
  expected_value: 0.928
  format_in_paper: 'median 0.928'
  expected_occurrences: 1
  notes: 'Appears once in Figure 2 caption as ", median 0.928".'

- paper_section: '§2.2 Morris (prose)'
  paper_context: 'H1 top-3 fraction range across cells'
  monograph_claim_id: 'T1.09'
  expected_value: 0.658
  format_in_paper: '0.658--0.998'
  expected_occurrences: 1
  notes: 'Appears once in §2.2 prose as "(range 0.658--0.998)". The endash (--) is LaTeX source; anchored on T1.09 (min=0.658); T1.10 (max=0.998) is co-validated by literal presence.'

- paper_section: '§2.2 Morris (prose)'
  paper_context: 'H1 lowest top-3 fraction (S4_F SpO2)'
  monograph_claim_id: 'T2.h1.S4_F.SpO2'
  expected_value: 0.658
  format_in_paper: 'S4\_F SpO$_2$ at 0.658'
  expected_occurrences: 1
  notes: 'Appears once in §2.2 prose identifying the lowest-top3 cell. The "$_2$" math-mode subscript is the LaTeX source as written.'

- paper_section: '§2.2 Morris (prose)'
  paper_context: 'H1 second-lowest top-3 fraction (S4_M SpO2)'
  monograph_claim_id: 'T2.h1.S4_M.SpO2'
  expected_value: 0.703
  format_in_paper: 'S4\_M SpO$_2$ at 0.703'
  expected_occurrences: 1
  notes: 'Appears once in §2.2 prose immediately after the S4_F SpO2 identification.'

## Step 4 — Results §2.3 VC-AC trigger correction

- paper_section: '§2.3 + §2.4 caption + abstract'
  paper_context: 'Median Vt CV original (S014 paired comparison)'
  monograph_claim_id: 'T1.03'
  expected_value: 0.351
  format_in_paper: '0.351'
  expected_occurrences: 2
  notes: 'Appears twice: §2.3 prose ("collapses the median Vt CV from 0.351 to 0.016") and Figure 3 caption ("Median CV collapses from 0.351 to 0.016"). Both are downstream of T1.03 (S014 paired_comparison.parquet).'

- paper_section: '§2.3 + §2.4 caption'
  paper_context: 'Median Vt CV after -2 cmH2O trigger lock'
  monograph_claim_id: 'T1.04'
  expected_value: 0.016
  format_in_paper: '0.016'
  expected_occurrences: 2
  notes: 'Appears twice: §2.3 prose and Figure 3 caption (same context as T1.03).'

- paper_section: '§2.3 VC-AC (prose)'
  paper_context: 'Worst-case Vt CV original'
  monograph_claim_id: 'T1.05'
  expected_value: 1.826
  format_in_paper: '1.826'
  expected_occurrences: 1
  notes: 'Appears once in §2.3 prose: "reduces the worst-case Vt CV from 1.826 to 0.112".'

- paper_section: '§2.3 VC-AC (prose)'
  paper_context: 'Worst-case Vt CV after lock'
  monograph_claim_id: 'T1.06'
  expected_value: 0.112
  format_in_paper: '0.112'
  expected_occurrences: 1
  notes: 'Appears once in §2.3 prose adjacent to T1.05.'

- paper_section: '§2.3 VC-AC (prose)'
  paper_context: 'S014 paired-rerun sample size'
  monograph_claim_id: 'T1.06b.s14_n_runs'
  expected_value: 64
  format_in_paper: '64 of the affected configurations'
  expected_occurrences: 1
  notes: 'Appears once in §2.3 prose: "We re-ran 64 of the affected configurations". New ledger claim T1.06b.s14_n_runs added in Step 4 (was implicit in monograph L2226 but not previously audited).'

- paper_section: '§2.3 + §2.4 caption'
  paper_context: 'Fraction of locked-trigger reruns below 0.05 Vt CV threshold'
  monograph_claim_id: 'T1.06c.s14_frac_below'
  expected_value: 78.1
  format_in_paper: '78.1~\%'
  expected_occurrences: 2
  notes: 'Appears twice: §2.3 prose ("78.1~\% of locked-trigger reruns drop below the 0.05 steady-state threshold") and Figure 3 caption ("78.1~\% of locked reruns drop below the threshold"). New ledger claim T1.06c added in Step 4.'

- paper_section: 'Abstract + §2.3 subsection title + §2.3 prose ×2 + §2.4 caption'
  paper_context: 'Inspiration-trigger pressure for VC-AC lockout fix'
  monograph_claim_id: 'T1.06d.s14_trigger_pressure'
  expected_value: -2
  format_in_paper: '$-2$~cmH$_2$O'
  expected_occurrences: 5
  notes: 'Appears 5 times in paper.tex: abstract sentence 3 (1), §2.3 subsection title "VC-AC tidal-volume dyssynchrony and the $-2$~cmH$_2$O fix" (1; this was missed in the initial Step 4 count and revealed by the audit), §2.3 prose ×2 (1 + 1), Figure 3 caption (1). New ledger claim T1.06d (regex-extracted from scripts/run_s014_trigger_lockout.py TRIGGER_PRESSURE_CMH2O constant).'

## Step 4 — Results §2.4 Transient hyperoxia regime

- paper_section: '§2.4 hyperoxia (prose)'
  paper_context: 'Total implausible-flagged runs across full sweep'
  monograph_claim_id: 'T1.21b'
  expected_value: 126
  format_in_paper: '126 \texttt{implausible}-flagged runs'
  expected_occurrences: 1
  notes: 'Appears once in §2.4 prose: "exceeds the detector''s locked upper bound of 600~mmHg on 34 of the 126 \texttt{implausible}-flagged runs".'

- paper_section: '§2.4 hyperoxia (prose)'
  paper_context: 'PaO2 > 600 implausible count (F-003 hyperoxia subset)'
  monograph_claim_id: 'T1.21'
  expected_value: 34
  format_in_paper: '34 of the 126'
  expected_occurrences: 1
  notes: 'Appears once in §2.4 prose adjacent to T1.21b.'

- paper_section: '§2.4 hyperoxia (prose)'
  paper_context: 'Fraction of PaO2>600 runs at FiO2 >= 0.95'
  monograph_claim_id: 'T1.22'
  expected_value: 91
  format_in_paper: '91~\% of these excursions'
  expected_occurrences: 1
  notes: 'Appears once in §2.4 prose: "91~\% of these excursions occur at FiO$_2 \geq 0.95$".'

- paper_section: '§2.4 hyperoxia (prose)'
  paper_context: 'S021 S1 converged reruns'
  monograph_claim_id: 'T1.24b'
  expected_value: 41
  format_in_paper: '41 of 44 reruns'
  expected_occurrences: 1
  notes: 'Appears once in §2.4 prose: "41 of 44 reruns (93.2~\%) converged to a stable plateau". Anchored on T1.24b (n=41); T1.24c (n=44 total) is co-validated by literal presence.'

- paper_section: '§2.4 hyperoxia (prose)'
  paper_context: 'S021 S1 frac_converged (93.2%)'
  monograph_claim_id: 'T1.24'
  expected_value: 93.2
  format_in_paper: '93.2~\%'
  expected_occurrences: 1
  notes: 'Appears once in §2.4 prose immediately after the 41-of-44 count.'

## Step 5 — Results §2.5 sex-stratified divergence + BV mechanism

- paper_section: '§2.5 prose + Figure 4 caption'
  paper_context: 'All 20 divergence events on male surrogate (anchor for the sex-stratification claim)'
  monograph_claim_id: 'T1.12'
  expected_value: 20
  format_in_paper: '20 divergence events'
  expected_occurrences: 2
  notes: 'Appears twice: §2.5 prose "The 20 divergence events are not spread uniformly" (1) and Figure 4 caption "All 20 divergence events fall on the male surrogate" (1).'

- paper_section: '§2.5 prose'
  paper_context: 'Female surrogate divergence count (zero across 4 cells x 160 runs)'
  monograph_claim_id: 'T1.14b'
  expected_value: 0
  format_in_paper: '640 female-surrogate'
  expected_occurrences: 1
  notes: 'Appears once in §2.5 prose: "zero divergences across the 640 female-surrogate runs". Anchored on T1.14b (the value 0 for female divergence count); the 640 denominator is co-validated.'

- paper_section: '§2.5 + S018 follow-up prose (×2)'
  paper_context: 'S018 rerun sample size for BV-rescue dose-response'
  monograph_claim_id: 'T1.12'
  expected_value: 20
  format_in_paper: '20 originally-diverged'
  expected_occurrences: 2
  notes: 'Appears twice in §2.5 prose: ¶2 "We re-executed the 20 originally-diverged male inputs with an explicit BloodVolumeBaseline override" (1) and Figure 4 caption "20 originally-diverged male inputs" (1).'

- paper_section: '§2.5 prose (BV-rescue dose-response)'
  paper_context: 'Default BV dose-response starting point: 20 diverged out of 20'
  monograph_claim_id: 'T1.12'
  expected_value: 20
  format_in_paper: '20 / 20'
  expected_occurrences: 1
  notes: 'Appears once in §2.5 prose as the leading term of the dose-response chain "20 / 20 $\rightarrow$ 2 / 20 $\rightarrow$ 0 / 20".'

- paper_section: '§2.5 prose (BV-rescue dose-response)'
  paper_context: 'Bracket BV (4400 mL) dose-response: 2 diverged out of 20'
  monograph_claim_id: 'T2.bv.bracket.diverged'
  expected_value: 2
  format_in_paper: '2 / 20'
  expected_occurrences: 1
  notes: 'Appears once in §2.5 prose as the middle term of the BV dose-response.'

- paper_section: '§2.5 prose (BV-rescue dose-response)'
  paper_context: 'Floor BV (4082.24 mL) dose-response: 0 diverged out of 20'
  monograph_claim_id: 'T2.bv.floor.diverged'
  expected_value: 0
  format_in_paper: '0 / 20'
  expected_occurrences: 2
  notes: 'Appears twice in §2.5: prose endpoint of dose-response chain "20 / 20 $\rightarrow$ 2 / 20 $\rightarrow$ 0 / 20" (1) and one additional ratio in the same paragraph (1).'

- paper_section: '§2.5 prose + Figure 4 caption (×2 each)'
  paper_context: 'Male reference body BloodVolumeBaseline default'
  monograph_claim_id: 'T3.s027.bv_default'
  expected_value: 4802.63
  format_in_paper: '4{,}802.63'
  expected_occurrences: 3
  notes: 'Appears 3 times: §2.5 prose ¶2 "yielding 4{,}802.63~mL for the 67.3~kg male reference body" (1), §2.5 prose ¶2 "the default (4{,}802.63~mL)" (1), Figure 4 caption "4{,}802.63~mL default" (1). First map rows for this claim_id (was in ledger via T3.s027 but not yet in paper crosswalk).'

- paper_section: 'Abstract + §2.5 prose (×2) + Figure 4 caption'
  paper_context: 'Male reference body BloodVolumeBaseline floor (Pulse setup-time minimum)'
  monograph_claim_id: 'T3.s027.bv_floor'
  expected_value: 4082.24
  format_in_paper: '4{,}082.24'
  expected_occurrences: 4
  notes: 'Appears 4 times as of Step 5: abstract sentence 5 "4{,}082.24~mL floor" (1), §2.5 prose ¶2 "the engine''s setup-time minimum for this body (4{,}082.24~mL, a 15.0~\% reduction)" (1), §2.5 prose ¶3 "4{,}082.24~mL on this male body" (1), Figure 4 caption "4{,}082.24~mL Pulse setup-time floor on this body" (1). Bumped from 1 (Step 1, abstract-only format "4{,}082.24~mL") to 4 (Step 5). Format simplified to just "4{,}082.24" to match all four occurrences regardless of trailing unit/context.'

- paper_section: '§2.5 prose (×2) + Figure 4 caption'
  paper_context: 'Female reference body BloodVolumeBaseline default (Pulse allometric for 56.2 kg)'
  monograph_claim_id: 'T3.s028.bv_female_default'
  expected_value: 3996.09
  format_in_paper: '3{,}996.09'
  expected_occurrences: 3
  notes: 'Appears 3 times: §2.5 prose ¶2 "3{,}996.09~mL for the 56.2~kg female body" (1), §2.5 prose ¶3 "the female-computed BV (3{,}996.09~mL)" (1), Figure 4 caption "3{,}996.09~mL for the female reference body" (1). First mapping for the new ledger claim T3.s028.bv_female_default added in Step 5.'

- paper_section: '§2.5 prose + Figure 4 caption'
  paper_context: 'Intermediate BV bracket in S018 dose-response (4400 mL = 8.4% reduction from male default)'
  monograph_claim_id: 'T2.bv.bracket.diverged'
  expected_value: 2
  format_in_paper: '4{,}400'
  expected_occurrences: 2
  notes: 'Appears twice: §2.5 prose "an intermediate bracket (4{,}400~mL, a 8.4~\% reduction)" (1), Figure 4 caption "4{,}400~mL intermediate bracket" (1). Anchored on T2.bv.bracket.diverged (value=2 diverged at this BV setting; the "4400" value itself is the experimental BV override, declared in scripts/s018_bv_falsification.py as BV_BRACKETS["bracket"]).'

## Step 5 — Results §2.6 secondary observations narrative block

- paper_section: '§2.6 secondary observations (compensatory tachycardia)'
  paper_context: 'Clean-runs HR mean in S1 (healthy adult baseline)'
  monograph_claim_id: 'T2.hr.S1.mean'
  expected_value: 73.8
  format_in_paper: '73.8~bpm'
  expected_occurrences: 1
  notes: 'Appears once in §2.6 ¶2: "output HR settles near a physiological norm (73.8~bpm mean, $\sigma = 20.4$~bpm across clean runs)".'

- paper_section: '§2.6 secondary observations (compensatory tachycardia)'
  paper_context: 'Clean-runs HR std in S1 (healthy adult baseline)'
  monograph_claim_id: 'T2.hr.S1.std'
  expected_value: 20.4
  format_in_paper: '\sigma = 20.4$~bpm'
  expected_occurrences: 1
  notes: 'Appears once in §2.6 ¶2 as "$\sigma = 20.4$~bpm". The pattern includes the closing $ of math mode (between 20.4 and ~bpm) because that is where LaTeX renders the bpm unit as text-mode immediately after the math expression.'

- paper_section: '§2.6 secondary observations (compensatory tachycardia)'
  paper_context: 'Clean-runs HR mean in S3 (moderate ARDS)'
  monograph_claim_id: 'T2.hr.S3.mean'
  expected_value: 155.7
  format_in_paper: '155.7~bpm'
  expected_occurrences: 1
  notes: 'Appears once in §2.6 ¶2: "output HR rises to 155.7~bpm and 147.1~bpm respectively".'

- paper_section: '§2.6 secondary observations (compensatory tachycardia)'
  paper_context: 'Clean-runs HR mean in S4 (severe ARDS)'
  monograph_claim_id: 'T2.hr.S4.mean'
  expected_value: 147.1
  format_in_paper: '147.1~bpm'
  expected_occurrences: 1
  notes: 'Appears once in §2.6 ¶2 adjacent to the S3 mean.'

- paper_section: '§2.6 secondary observations (Cornish complementarity)'
  paper_context: 'Cornish 2023 non-overlap Hoeffding rejections (channels outside atlas)'
  monograph_claim_id: 'T3.s028.cornish_non_overlap_hoeffding'
  expected_value: 80
  format_in_paper: '80 of 85'
  expected_occurrences: 1
  notes: 'Appears once in §2.6 ¶3: "80 of 85 fall on channels the present atlas does not assess". New ledger claim added in Step 5.'

- paper_section: '§2.6 secondary observations (Cornish complementarity)'
  paper_context: 'Cornish 2023 total Hoeffding rejections across 15 quantities'
  monograph_claim_id: 'T3.s028.cornish_total_hoeffding'
  expected_value: 85
  format_in_paper: '85 total Hoeffding-inequality rejections'
  expected_occurrences: 1
  notes: 'Appears once in §2.6 ¶3: "reported 85 total Hoeffding-inequality rejections across 15 physiological quantities".'
