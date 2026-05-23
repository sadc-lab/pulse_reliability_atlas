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

- paper_section: 'Abstract'
  paper_context: 'Total Morris simulations across the sweep'
  monograph_claim_id: 'T1.01'
  expected_value: 1280
  format_in_paper: '1{,}280'
  expected_occurrences: 2
  notes: 'Appears twice in the abstract: standalone in sentence 2 "(1{,}280 simulations)" and as the denominator of "20/1{,}280 runs" in sentence 5. Both occurrences contribute to this count. When subsequent sections (Results §2.1 overview, Methods §4.3 sweep design) cite the total, this expected_occurrences will be incremented.'

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
