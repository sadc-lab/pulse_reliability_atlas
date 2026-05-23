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

- paper_section: 'Abstract + §2.1 Overview + Table 1 caption'
  paper_context: 'Total Morris simulations across the sweep'
  monograph_claim_id: 'T1.01'
  expected_value: 1280
  format_in_paper: '1{,}280'
  expected_occurrences: 7
  notes: 'Total occurrences of the literal pattern 1{,}280 across the paper as of Step 3: abstract sentence 2 standalone (1), abstract sentence 5 "20/1{,}280" denominator (1), §2.1 prose "1{,}280 simulations spanning" (1), §2.1 prose "0 / 1{,}280" (1), §2.1 prose "20 / 1{,}280" (1), §2.1 prose "663 of 1{,}280" (1), §2.1 Table 1 caption "1{,}280 total" (1) = 7. Bumped from 2 (Step 1) to 7 (Step 3). When Methods §4.3 sweep design cites the total, this will be incremented again.'

- paper_section: 'Abstract'
  paper_context: 'F-004 primary-flag rate (Vt CV > 0.05 under not_steady_state)'
  monograph_claim_id: 'T1.02a'
  expected_value: 20.6
  format_in_paper: '20.6\%'
  expected_occurrences: 1
  notes: 'Appears once in the abstract sentence 3 "in 20.6\% of runs". Will recur in Results §2.3 (Headline Finding 1).'

- paper_section: 'Abstract'
  paper_context: 'S021 hyperoxia 300s plateau median (S1)'
  monograph_claim_id: 'T1.23'
  expected_value: 643
  format_in_paper: 'median 643~mmHg'
  expected_occurrences: 1
  notes: 'Appears once in the abstract sentence 4. The "~" between number and unit is a LaTeX non-breaking space; re.escape() handles it. Will recur in Results §2.4 (Headline Finding 2).'

- paper_section: 'Abstract'
  paper_context: 'Divergence count (all male, input-extreme regime)'
  monograph_claim_id: 'T1.12'
  expected_value: 20
  format_in_paper: '20/1{,}280'
  expected_occurrences: 1
  notes: 'Appears once in sentence 5 as the compact "20/1{,}280 runs" form. The denominator 1{,}280 is separately accounted for by the T1.01 row (expected_occurrences=2).'

- paper_section: 'Abstract'
  paper_context: 'Male BloodVolumeBaseline floor on standard surrogate'
  monograph_claim_id: 'T3.s027.bv_floor'
  expected_value: 4082.24
  format_in_paper: '4{,}082.24~mL'
  expected_occurrences: 1
  notes: 'Appears once in sentence 5 as the BV-mechanism punchline. Will recur in Results §2.5 (Headline Finding 3) and Methods §4.2 (patient surrogates).'

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

- paper_section: '§2.1 Overview (prose)'
  paper_context: 'Divergence rate (percentage form)'
  monograph_claim_id: 'T1.13'
  expected_value: 1.6
  format_in_paper: '1.6~\%'
  expected_occurrences: 1
  notes: 'Appears once in §2.1 prose immediately after "20 / 1{,}280 runs".'

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
