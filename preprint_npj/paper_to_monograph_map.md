# Paper-to-Monograph Crosswalk Map (`paper_to_monograph_map.md`)

**Purpose.** This file is the single source of truth for **which numerical
claims appear in both `preprint_npj/paper.tex` and `preprint/manuscript.md`
(the monograph)**. The audit script `scripts/audit_claims.py` reads this
file under the `--check-paper-sync` opt-in flag and verifies that every
mapped value still appears in `paper.tex` with the expected occurrence
count and is consistent with the monograph value behind the same
`claim_id`.

**Why this exists.** The atlas's monograph (~100 pages) is audited at
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

- paper_section: 'paper.tex full + supplement.tex S3/S4/S5/S16'
  paper_context: 'Total Morris simulations across the sweep'
  monograph_claim_id: 'T1.01'
  expected_value: 1280
  format_in_paper: '1{,}280'
  expected_occurrences: 45
  notes: 'Bumped 46 -> 45 (2026-08-20): paper.tex §4.4 no longer prints the four clamp regexes, and the sentence introducing that listing ("the set with which the 1{,}280-run sweep was classified") went with it. The regexes now live only in Supplement §S3.3, where an anchor holds them character-identical to src/detector.py; the paper keeps the count, the epistemic scope of the log-based test, and a pointer. Earlier history: Bumped 44 -> 46 (2026-08-05, second change that day), Supplement Figure S5 added: its caption states the calibration gate that licenses the exhaustive trigger attribution, "reproduces the stored \texttt{not\_steady\_state} flag on 1{,}280 of 1{,}280 runs", which carries the canonical literal twice in one clause -- numerator and denominator. The clause is load-bearing rather than decorative: the panel it justifies differs from the detector''s own recorded reasons, so the figure has to say on what basis the reconstruction is trusted. Bumped 38 -> 44 (2026-08-05), screening-retention block added to §2.1 as part of the Figure 2 reframing: six new occurrences of the canonical literal, each counted by hand against the added text before the map was edited. Prose: "663 of 1{,}280 simulations (51.8~\%) are clean" (1) and the empty-category sentence "\texttt{clamped} is a provided category that is empty here (0 / 1{,}280)" (1). Table 4 caption: the two whole-sweep percentages are quoted in full to show neither is a rounding tie, "663/1{,}280 = 51.796875~\%" (1) and "1{,}134/1{,}280 = 88.59375~\%" (1). Table 4 body, the All-cells row: "663/1{,}280 (51.8~\%)" (1) and "1{,}134/1{,}280 (88.6~\%)" (1). Note that "1{,}134" does not itself match this literal; only the denominators do. Bumped 37 -> 38 (2026-08-04), sex/blood-volume correction in supplement S2: the rewritten clause (ii) scopes its own limitation to the sweep rather than to the atlas as a whole -- "Because the 1{,}280-run sweep varies sex jointly with body mass and height, it cannot on its own quantify the independent effect of the sex flag". The scoping is load-bearing, not decorative: supplement S9 credits the controlled 2x2 design of S011 with a fixed-mass sex effect on S1 PaO2, so an unscoped sentence would have contradicted it. The literal is therefore kept rather than reworded away. Bumped 39 -> 37 (2026-08-02, second change that day), N-1 removal of Supplementary Methods: two supplement subsections were deleted as duplicates of the main Methods text, each carrying one occurrence of the canonical literal. §S3.1 "Engine wrapper, Docker pinning, and reproducibility" stated that "bit-exact reproduction of the canonical 1{,}280-run sweep was verified at three independent layers" -- paper.tex §4.1 already names those three layers, and the wrapper description it uniquely held has moved there. §S3.2 "Morris sampler implementation" stated "1{,}280 evaluations across the full sweep"; paper.tex §4.3 already carried the sampler settings, the seven ranges, the clip rationale and that same total, so only a short code-provenance note survives, under the label sec:s3-morris. Bumped 38 -> 39 (2026-08-02), N-1 removal of Supplementary Methods: Methods §4.4 now prints the four clamp regular expressions themselves, which the main text previously described only by their count ("any of 4 documented input-rejection patterns"). Their lead-in names the set as the one "with which the 1{,}280-run sweep was classified", adding one occurrence of the canonical literal. The patterns move because npj does not permit Supplementary Methods; the four-pattern set printed is the one recovered from 708efb1^, i.e. the set as executed, not the current five-pattern set in src/detector.py. Bumped 37 -> 38 (2026-07-29): the §2.1 Overview paragraph now states the verdicts of the preregistered hypotheses, giving H2 as "the observed rate is 0 of 1{,}280", which adds one occurrence of the canonical literal. The same null is already counted at the Table 3 caption and once in the Discussion; this third instance is the one that names it as the H2 outcome (hypothesis not supported). Bumped 36 -> 37 (2026-07-28, second change that day): the Figure 1 caption title was changed from "One grid, eight times." to "Study design of the 1{,}280-run sweep." at the author''s request, which adds one occurrence of the canonical literal. Bumped 35 -> 36 (2026-07-28): the Table 3 caption gains an opening sentence stating the silent-clamping null as read off that table, "the clamped column is empty in all eight cells, 0 of 1{,}280", adding one occurrence. This is the same null already counted once in the Discussion, reported here at its own table. Bumped 36 -> 35 (2026-07-27, second change that day): the study-design figure was externalised from an inline tikzpicture to preprint_npj/figures/fig00_study_design.tex, because pinning it with [H] after the full-page Table 1 overflowed the page by 410 pt and swallowed its caption, and because pandoc drops TikZ so it was missing from paper.docx. Its node text "8 x 160 = 1,280 simulations" therefore left paper.tex. The claim still renders in the figure; only the file holding it changed, and scripts/make_fig00_study_design.py regenerates that file so it cannot drift. Earlier that day, bumped 35 -> 36 (2026-07-27): the Supplement §S3 body-dimension paragraph gains the CDC-lookup provenance declaration, whose closing clause states that the two preregistered bodies "are exactly the two bodies simulated in all 1{,}280 runs" (1). Earlier history: Total occurrences of "1{,}280" across paper.tex + supplement.tex as of Phase 9.B: paper.tex 12 (abstract 2, §2.1 5, §2.5+Fig4 2, §4 Discussion 1, Methods §4.1+§4.3 2) + supplement.tex 5 (S3.2 Morris sampler, S4 NSS table prose "1{,}280-run sweep" + Table S1 total row + "1{,}008 / 1{,}280" + "663 / 1{,}280" repeats). Bumped 14 -> 17 in Phase 9.B for the S4 extended-Table-1 additions. Bumped 23 -> 24 in Phase H (2026-05-31): the new Supplement §S16 "Summary of supplementary findings and discoveries" intro paragraph uses "The 1{,}280-run atlas" as its opening descriptor, so the canonical formatted string appears once more. Bumped 24 -> 28 in the cross-platform reproduction round (2026-06-11): the new Supplement §S12 "Independent reproduction on separate hardware" subsection plus the Code-availability sentence add four "1{,}280" substring occurrences --- paper.tex "full 1{,}280-run sweep" (1), supplement.tex "full 1{,}280-run Morris sweep" (1), and "matched on 1{,}280/1{,}280 runs" (2). Bumped 28 -> 30 (2026-06-24): the new study-design Figure 1 adds two "1{,}280" occurrences --- figure caption ("8 x 160 = 1,280 simulations in total") + figure body ("8 x 160 = 1,280 simulations"). Bumped 30 -> 31 (2026-07-05): the §4 Discussion ML-pipeline paragraph now surfaces the silent-clamping null as "0 of 1{,}280 runs", adding one occurrence. Bumped 31 -> 33 (2026-07-24), Methods §4.1 clarity rewrite + S-G-1 resolution: paper.tex §4.1 now names the first verification layer as "the 1{,}280-row table of input combinations" (1), and supplement.tex §S12.1 gains the compute-effort sentence "the full 1{,}280-run sweep was carried out end-to-end three times in total" (1).'

- paper_section: 'Abstract + §2.3 VC-AC'
  paper_context: 'VC-AC trigger-dyssynchrony primary-flag rate (Vt CV > 0.05 under not_steady_state)'
  monograph_claim_id: 'T1.02a'
  expected_value: 20.6
  format_in_paper: '20.6~\%'
  expected_occurrences: 3
  notes: 'paper (2): abstract sentence 5 "in 20.6~\% of runs", §2.3 opening sentence "20.6~\% of runs". supplement (1): the S3 detector-convention paragraph, which names this rate as an example of a prevalence estimate conditioned on the 0.05 CV convention. Format standardised in Step 4 to use ~ (LaTeX non-breaking space) between number and unit; the abstract was retroactively updated for consistency. Bumped 2 -> 3 when the detector-convention provenance sentence was added.'

- paper_section: 'Abstract + §2.4 hyperoxia'
  paper_context: 'Hyperoxia 300s plateau median (S1)'
  monograph_claim_id: 'T1.23'
  expected_value: 643
  format_in_paper: '643~mmHg'
  expected_occurrences: 3
  notes: 'Appears 3 times: paper.tex abstract sentence 6, which since 2026-08-18 reads "300-second healthy-lung reruns give a median 643~mmHg" (1) + paper.tex §2.4 prose "the converged S1 plateau median was 643~mmHg" (1) + supplement §S9 prose "converged-subset median PaO2 of 643~mmHg" (1). The supplement Figure-S3 caption trajectory endpoint was changed 643 -> 639 in Supplement Pass C (SP-C.D2: figure median recomputed over the 38 physiological-converged runs, excluding the 3 numerical runaways), dropping the expected count from 4 to 3. All use ~ non-breaking space.'

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
  expected_occurrences: 2
  notes: 'Bumped 1 -> 2 (2026-08-05), screening-retention block added to §2.1: the new paragraph opens the two-screen comparison by restating the strict definition, "Under the strict four-flag definition, 663 of 1{,}280 simulations (51.8~\%) are clean", so the literal now appears twice in §2.1. The restatement is deliberate rather than redundant: the paragraph exists to contrast that figure with the 1{,}134 hard-failure-free count, and the contrast is unreadable if the first term is only available several paragraphs earlier. Originally: appears once in §2.1 prose as "663 of 1{,}280 simulations (51.8~\%) are flag-clean".'

- paper_section: '§2.1 + supplement S4 attribution prose'
  paper_context: 'Clean rate (percentage form)'
  monograph_claim_id: 'T1.29'
  expected_value: 51.8
  format_in_paper: '51.8~\%'
  expected_occurrences: 4
  notes: 'Bumped 2 -> 4 (2026-08-05), screening-retention block added to §2.1: two new occurrences, both alongside the 663 count they qualify -- the new prose sentence "663 of 1{,}280 simulations (51.8~\%) are clean" (1) and the All-cells row of Table 4 (1). The percentage is quoted in these two places, and only these two, because 663/1{,}280 = 51.796875~\% is not a rounding tie; the sixteen per-cell values are given as counts out of 160 precisely because nine of them are. Originally: paper §2.1 prose (1) + supplement S4 attribution prose "raises the implied clean count from 663 / 1{,}280 (51.8~\%)" (1). Bumped 1 -> 2 in Phase 9.B.'

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

## Step 3 — Results §2.1 Figure 2 traffic-light caption

- paper_section: '§2.1 Figure 2 caption + §4.5 deviation declaration'
  paper_context: 'Reliability traffic-light aggregate breakdown'
  monograph_claim_id: 'T1.25'
  expected_value: 7
  format_in_paper: '7 green / 29 yellow / 12 red'
  expected_occurrences: 2
  notes: 'Bumped 1 -> 2 (2026-08-04), post hoc deviation declaration: Methods §4.5 now restates the primary counts at the point where the 7 / 3 / 38 sensitivity is introduced, so a reader meets both distributions together instead of having to hold one from §2.1. The canonical slash form was used deliberately rather than a comma variant, which would have escaped this check while leaving two spellings of the same anchored quantity in the paper. Also corrected in this entry: paper_section said "Figure 1 caption"; the traffic-light map is Figure 2 (fig00_study_design was inserted as Figure 1 on 2026-06-24 and this label was not renumbered). Single literal-string check covering all three traffic-light counts (T1.25=7 green, T1.26=29 yellow, T1.27=12 red). Anchored on T1.25 for value-cross-check; 29 and 12 are co-validated by literal presence.'

## Step 3 — Results §2.2 Morris rankings (prose + Figure 3 caption)

- paper_section: '§2.2 Morris (prose + Figure 3 caption)'
  paper_context: 'H1 verdict — top-3 fraction >= 0.5 on all 48 cell x output combinations'
  monograph_claim_id: 'T1.07'
  expected_value: 48
  format_in_paper: '48 of 48'
  expected_occurrences: 4
  notes: 'Appears three times: once in §2.2 prose ("the data support this on 48 of 48 cell $\times$ output combinations"), once in Figure 3 caption ("48 of 48 cell $\times$ output combinations"), and (bumped 2 -> 3, 2026-07-05) once in the §4 Discussion, where the H1 skewed-sensitivity result is surfaced at the FAQ-gap sentence. Bumped 3 -> 4 (2026-07-24): the new Supplement §S3.3 subsection on the pulse-pressure-clip cost states that H1 "holds in 48 of 48 cell--output combinations under either estimator", adding a fourth occurrence.'

- paper_section: '§2.2 Morris (prose)'
  paper_context: 'H1 median top-3 fraction (prose form)'
  monograph_claim_id: 'T1.08'
  expected_value: 0.928
  format_in_paper: 'median top-3 fraction of 0.928'
  expected_occurrences: 1
  notes: 'Appears once in §2.2 prose as "with a median top-3 fraction of 0.928".'

- paper_section: '§2.2 Figure 3 caption'
  paper_context: 'H1 median top-3 fraction (figure caption form)'
  monograph_claim_id: 'T1.08'
  expected_value: 0.928
  format_in_paper: 'median 0.928'
  expected_occurrences: 1
  notes: 'Appears once in Figure 3 caption as ", median 0.928".'

- paper_section: 'Abstract + §3 Discussion'
  paper_context: 'H1 median top-3 fraction (rounded-percentage display form)'
  monograph_claim_id: 'T1.08'
  expected_value: 0.928
  format_in_paper: 'median 93~\%'
  expected_occurrences: 2
  notes: 'Added 2026-08-01 (finding F-1 of the step-wise fact-check). Same underlying value as the two rows above, in its rounded-percentage display form: T1.08 = 0.9277 -> 92.77 % -> 93 %. Appears twice, both in paper.tex: the Abstract ("median 93~\% of total sensitivity") and the Discussion ("a median 93~\% of summed $\mu^{*}$"). Before this row, a future correction to 0.928 would have updated the two guarded loci and silently left these two behind, because the crosswalk guards the fraction and not its percentage form.'

- paper_section: '§2.2 Morris (prose)'
  paper_context: 'H1 top-3 fraction range across cells'
  monograph_claim_id: 'T1.09'
  expected_value: 0.658
  format_in_paper: '0.658--0.998'
  expected_occurrences: 1
  notes: 'Appears once in §2.2 prose as "(range 0.658--0.998)". The endash (--) is LaTeX source; anchored on T1.09 (min=0.658); T1.10 (max=0.998) is co-validated by literal presence.'

- paper_section: '§2.2 Morris (prose)'
  paper_context: 'H1 lowest top-3 fraction (S4_F SpO2 = lower endpoint of the S4 gas-exchange range)'
  monograph_claim_id: 'T2.h1.S4_F.SpO2'
  expected_value: 0.658
  format_in_paper: 'from 0.658 to 0.727'
  expected_occurrences: 1
  notes: 'Appears once in §2.2 prose as "(SpO$_2$ and PaO$_2$ in S4, from 0.658 to 0.727)"; 0.658 is the lower endpoint = S4_F SpO2 top-3 fraction. Reworded 2026-07-18 from the earlier "S4\_F SpO$_2$ at 0.658" when the sentence was corrected to a shunt-driven range over the four S4 gas-exchange cells (the earlier "only cells where the property weakens" / saturation-ceiling framing was an overstatement, now aligned with the monograph).'

- paper_section: '§2.2 Morris (prose)'
  paper_context: 'H1 highest of the S4 gas-exchange top-3 fractions (S4_M PaO2 = upper endpoint of the S4 gas-exchange range)'
  monograph_claim_id: 'T2.h1.S4_M.PaO2'
  expected_value: 0.727
  format_in_paper: 'from 0.658 to 0.727'
  expected_occurrences: 1
  notes: 'Appears once in §2.2 prose as "(SpO$_2$ and PaO$_2$ in S4, from 0.658 to 0.727)"; 0.727 is the upper endpoint = S4_M PaO2 top-3 fraction. Repointed 2026-07-18 from the earlier "S4\_M SpO$_2$ at 0.703" (S4_M SpO2) when the sentence was corrected to a shunt-driven range over the four S4 gas-exchange cells; 0.703 (S4_M SpO2) and 0.707 (S4_F PaO2) are no longer cited verbatim in the paper but remain validated as monograph claims T2.h1.S4_M.SpO2 / T2.h1.S4_F.PaO2 in the anchor ledger.'

## Step 4 — Results §2.3 VC-AC trigger correction

- paper_section: '§2.3 + §2.4 caption + abstract'
  paper_context: 'Median Vt CV original (S014 paired comparison)'
  monograph_claim_id: 'T1.03'
  expected_value: 0.351
  format_in_paper: '0.351'
  expected_occurrences: 4
  notes: 'paper (2): §2.3 prose ("collapses the median Vt CV from 0.351 to 0.016") and Figure 4 caption ("Median CV collapses from 0.351 to 0.016"). supplement (2): S8 opening and the S3 detector-convention paragraph, which cites the same collapse to bound the 0.05 CV convention. All downstream of T1.03 (S014 paired_comparison.parquet). Bumped 3 -> 4 when the detector-convention provenance sentence was added; the previous note said "Appears twice" while the count was already 3.'

- paper_section: '§2.3 + §2.4 caption'
  paper_context: 'Median Vt CV after -2 cmH2O trigger lock'
  monograph_claim_id: 'T1.04'
  expected_value: 0.016
  format_in_paper: '0.016'
  expected_occurrences: 4
  notes: 'paper (2): §2.3 prose and Figure 4 caption. supplement (2): S8 opening and the S3 detector-convention paragraph. Same contexts as T1.03. Bumped 3 -> 4 when the detector-convention provenance sentence was added.'

- paper_section: '§2.3 VC-AC (prose)'
  paper_context: 'Worst-case Vt CV original'
  monograph_claim_id: 'T1.05'
  expected_value: 1.826
  format_in_paper: '1.826'
  expected_occurrences: 2
  notes: 'Appears in §2.3 prose ("reduces the worst-case Vt CV from 1.826 to 0.018") and the Supplement Fig S8 caption.'

- paper_section: '§2.3 VC-AC (prose)'
  paper_context: 'Worst-case Vt CV after lock (paired same-run S1_F_0117)'
  monograph_claim_id: 'T1.s014.worstcase_locked_vtcv'
  expected_value: 0.018
  format_in_paper: '0.018'
  expected_occurrences: 2
  notes: 'Paired same-run worst-case (S1_F_0117): 1.826 -> 0.018. Appears in §2.3 prose and the Supplement Fig S8 caption.'

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
  expected_occurrences: 3
  notes: 'Appears twice: §2.3 prose ("78.1~\% of locked-trigger reruns drop below the 0.05 steady-state threshold") and Figure 4 caption ("78.1~\% of locked reruns drop below the threshold"). New ledger claim T1.06c added in Step 4.'

- paper_section: 'Abstract + §2.3 subsection title + §2.3 prose ×2 + §2.4 caption + Supplement §S5 Berlin-calibration caveat + Supplement §S8 contribution-claim sentence'
  paper_context: 'Inspiration-trigger pressure for VC-AC lockout fix'
  monograph_claim_id: 'T1.06d.s14_trigger_pressure'
  expected_value: -2
  format_in_paper: '$-2$~cmH$_2$O'
  expected_occurrences: 13
  notes: '2026-07-26: bumped 12 -> 13 --- the S030b Berlin-calibration caveat added to Supplement §S5 (sec:s5-berlin) states the trigger lock once more, when contrasting the free-trigger and trigger-locked arms at impairment 0.95. Verified by direct count: paper.tex 7 + supplement.tex 6 = 13. Prior 2026-07-20: bumped 13 -> 12 --- the Figure 4 (fig:corrections) caption reformulation replaced a repeated "$-2$~cmH$_2$O trigger lock" with "it" (concision only; the -2 cmH2O value is still stated once earlier in the same caption), so that caption now carries 1 occurrence, not 2, giving paper.tex 7 + supplement.tex 5 = 12. Prior 2026-07-06: bumped 12 -> 13 (was paper.tex 8 + supplement.tex 5 = 13); +1 from the Figure 3a clinical-caveat sentence added in the §2.4 pedagogical retouch, so the Figure 3 caption now carries 2 occurrences (was 1). Historical breakdown (paper.tex 7): abstract sentence 3 (1), §2.3 subsection title "VC-AC tidal-volume dyssynchrony and the $-2$~cmH$_2$O fix" (1; this was missed in the initial Step 4 count and revealed by the audit), §2.3 prose ×4 (1 + 3), Figure 3 caption (was 1, now 2). New ledger claim T1.06d (regex-extracted from scripts/run_s014_trigger_lockout.py TRIGGER_PRESSURE_CMH2O constant).'

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
  expected_occurrences: 2
  notes: 'Appears once in §2.4 prose immediately after the 41-of-44 count.'

## Step 5 — Results §2.5 sex-stratified divergence + BV mechanism

- paper_section: '§2.5 prose + Figure 5 caption'
  paper_context: 'All 20 divergence events on male surrogate (anchor for the sex-stratification claim)'
  monograph_claim_id: 'T1.12'
  expected_value: 20
  format_in_paper: '20 divergence events'
  expected_occurrences: 2
  notes: 'Appears twice: §2.5 prose "The 20 divergence events are not spread uniformly" (1) and Figure 5 caption "All 20 divergence events fall on the male surrogate" (1).'

- paper_section: '§2.5 prose'
  paper_context: 'Female surrogate divergence count (zero across 4 cells x 160 runs)'
  monograph_claim_id: 'T1.14b'
  expected_value: 0
  format_in_paper: '640 runs on the female reference body'
  expected_occurrences: 2
  notes: 'Appears once in §2.5 prose: "zero divergences across the 640 runs on the female reference body". Anchored on T1.14b (the value 0 for female divergence count); the 640 denominator is co-validated. Format updated 2026-05-30 in the surrogate -> reference body terminology change: from "640 female-surrogate" to "640 runs on the female reference body" (the natural English phrasing for the new terminology, avoiding the awkward hyphenated form "female-reference body"). Count 1 -> 2 on 2026-08-11: supplement S5 replaced the unverifiable "approximately fivefold higher ... than on the female" ratio with the measured counts, which restate the same 640-run female denominator (see audit/fivefold_divergence_ratio_defect.md).'

- paper_section: '§2.5 + S018 follow-up prose (×2)'
  paper_context: 'S018 rerun sample size for BV-rescue dose-response'
  monograph_claim_id: 'T1.12'
  expected_value: 20
  format_in_paper: '20 originally-diverged'
  expected_occurrences: 2
  notes: 'Appears twice in §2.5 prose: ¶2 "We re-executed the 20 originally-diverged male inputs with an explicit BloodVolumeBaseline override" (1) and Figure 4 caption "20 originally-diverged male inputs" (1).'

- paper_section: '§2.5 prose + supplement S2 limitations table footer'
  paper_context: 'Default BV dose-response starting point: 20 diverged out of 20'
  monograph_claim_id: 'T1.12'
  expected_value: 20
  format_in_paper: '20 / 20'
  expected_occurrences: 4
  notes: 'paper §2.5 prose dose-response chain (1) + supplement S2 limitations-table closing prose "20 / 20 clean with this regex set" (1). Bumped 1 -> 2 in Phase 9.A.'

- paper_section: '§2.5 prose (BV-rescue dose-response)'
  paper_context: 'Bracket BV (4400 mL) dose-response: 0 diverged out of 20 (corrected 2026-06-16; the prior "2" was a classification-time race artifact on the two slowest runs, now re-classified clean)'
  monograph_claim_id: 'T2.bv.bracket.diverged'
  expected_value: 0
  format_in_paper: '0 / 20'
  expected_occurrences: 9
  notes: 'Bracket now clears to 0 / 20 (same as floor). The corrected §2.5 prose reads "20 / 20 ... to 0 / 20 at both reductions"; "0 / 20" total across paper+supplement = 9 (string shared with T2.bv.floor.diverged, which expects the same count).'

- paper_section: '§2.5 + supplement S3/S5'
  paper_context: 'Floor BV (4082.24 mL) dose-response: 0 diverged out of 20'
  monograph_claim_id: 'T2.bv.floor.diverged'
  expected_value: 0
  format_in_paper: '0 / 20'
  expected_occurrences: 9
  notes: 'paper §2.5 (2) + supplement S3.7 (1) + supplement S5 continuous-severity table "0 / 20" rows (the (0.5, 0.85] bin counts) (2). Bumped 3 -> 5 in Phase 9.B.'

- paper_section: 'paper.tex prose, rounded mL (Tier 3 id8/54): §2.5 (x2) + Figure 5 caption'
  paper_context: 'Male reference body BloodVolumeBaseline default, rounded to whole mL in the paper'
  monograph_claim_id: 'T3.s027.bv_default'
  expected_value: 4802.63
  format_in_paper: '4{,}803~mL'
  expected_occurrences: 3
  notes: 'Tier 3 split (Sauthier id8/54): paper prose rounds 4,802.63 -> 4,803 mL (3x); expected_value stays the exact 4802.63 for the value-check; supplement keeps the exact 4{,}802.63 form (8x, the paired row).'

- paper_section: 'paper.tex prose, rounded mL (Tier 3 id8/54): Abstract + §2.5 (x2) + Figure 5 caption'
  paper_context: 'Male reference body BloodVolumeBaseline floor, rounded to whole mL in the paper'
  monograph_claim_id: 'T3.s027.bv_floor'
  expected_value: 4082.24
  format_in_paper: '4{,}082~mL'
  expected_occurrences: 4
  notes: 'Tier 3 split (Sauthier id8/54): paper prose rounds 4,082.24 -> 4,082 mL (4x); expected_value stays the exact 4082.24; supplement keeps the exact 4{,}082.24 form (5x, the paired row).'

- paper_section: 'paper.tex prose, rounded mL (Tier 3 id8/54): §2.5 (x2) + Figure 5 caption'
  paper_context: 'Female reference body BloodVolumeBaseline default, rounded to whole mL in the paper'
  monograph_claim_id: 'T3.s028.bv_female_default'
  expected_value: 3996.09
  format_in_paper: '3{,}996~mL'
  expected_occurrences: 3
  notes: 'Tier 3 split (Sauthier id8/54): paper prose rounds 3,996.09 -> 3,996 mL (3x); expected_value stays the exact 3996.09; supplement keeps the exact 3{,}996.09 form (5x, the paired row).'

- paper_section: '§2.5 + Figure 5 + supplement S3.6 (exact-precision occurrences; paper prose moved to the rounded-mL row above)'
  paper_context: 'Male reference body BloodVolumeBaseline default'
  monograph_claim_id: 'T3.s027.bv_default'
  expected_value: 4802.63
  format_in_paper: '4{,}802.63'
  expected_occurrences: 8
  notes: 'Figure 5 caption + supplement S3.6 body-dimension provenance + supplement S10 prose. Count 8 -> 6 on 2026-06-16: the S018 dose-response rewording (20->0->0) removed two "4,802.63" mentions from supplement S10. Count 6 -> 8 on 2026-08-11: the new S10 paragraph documenting the BloodVolumeBaseline CEILING (allometric x 1.15) adds two mentions -- the male default as the level the female reference body cannot reach, and the same default recomputed for a female-configured body at 67.3 kg.'

- paper_section: 'Abstract + §2.5 prose (×2) + Figure 5 caption'
  paper_context: 'Male reference body BloodVolumeBaseline floor (Pulse setup-time minimum)'
  monograph_claim_id: 'T3.s027.bv_floor'
  expected_value: 4082.24
  format_in_paper: '4{,}082.24'
  expected_occurrences: 5
  notes: 'Appears 4 times as of Step 5: abstract sentence 5 "4{,}082.24~mL floor" (1), §2.5 prose ¶2 "the engine''s setup-time minimum for this body (4{,}082.24~mL, a 15.0~\% reduction)" (1), §2.5 prose ¶3 "4{,}082.24~mL on this male body" (1), Figure 4 caption "4{,}082.24~mL Pulse setup-time floor on this body" (1). Bumped from 1 (Step 1, abstract-only format "4{,}082.24~mL") to 4 (Step 5). Format simplified to just "4{,}082.24" to match all four occurrences regardless of trailing unit/context.'

- paper_section: '§2.5 + Figure 5 + supplement S3.6'
  paper_context: 'Female reference body BloodVolumeBaseline default (Pulse allometric for 56.2 kg)'
  monograph_claim_id: 'T3.s028.bv_female_default'
  expected_value: 3996.09
  format_in_paper: '3{,}996.09'
  expected_occurrences: 5
  notes: 'paper §2.5 (×2) + Figure 5 caption (1) + supplement S3.6 body-dimension provenance (1). Bumped 3 -> 4 in Phase 9.A.'

- paper_section: '§2.5 prose + Figure 5 caption'
  paper_context: 'Intermediate BV bracket in S018 dose-response (4400 mL = 8.4% reduction from male default)'
  monograph_claim_id: 'T2.bv.bracket.diverged'
  expected_value: 0
  format_in_paper: '4{,}400'
  expected_occurrences: 4
  notes: 'Appears twice: §2.5 prose "an intermediate bracket (4{,}400~mL, a 8.4~\% reduction)" (1), Figure 5 caption "4{,}400~mL intermediate bracket" (1). Anchored on T2.bv.bracket.diverged (value corrected 2026-06-16 to 0 diverged at this BV setting; the "4400" value itself is the experimental BV override, declared in scripts/s018_bv_falsification.py as BV_BRACKETS["bracket"]).'

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

- paper_section: 'supplement S7 prose (L347)'
  paper_context: 'Cornish 2023 non-overlap Hoeffding rejections (channels outside atlas) -- supplement quote'
  monograph_claim_id: 'T3.s028.cornish_non_overlap_hoeffding'
  expected_value: 80
  format_in_paper: '80 of 85'
  expected_occurrences: 1
  notes: 'supplement S7 prose direct quote "80 of 85 Hoeffding rejections fall on channels..." (1). Dropped 2 -> 1 in the [SCIENTIFIC] final-fixes pass: paper §2.6 ¶3 was reworded from "80 of 85 fall on channels" to the self-consistent "82 of 85 fall outside ... 80 on channels ... plus 2 ... only 3 of 85 on the overlap" decomposition (D.8 sweep finding A1: 80 + 3 did not sum to 85). The paper-side value 80 is now tracked by the "80 on channels the present atlas does not assess" row below.'

- paper_section: '§2.6 secondary observations (Cornish complementarity)'
  paper_context: 'Cornish 2023 non-overlap Hoeffding rejections -- paper-side wording after A1 rewrite'
  monograph_claim_id: 'T3.s028.cornish_non_overlap_hoeffding'
  expected_value: 80
  format_in_paper: '80 on channels the present atlas does not assess'
  expected_occurrences: 1
  notes: 'paper §2.6 ¶3 after the A1 rewrite: "80 on channels the present atlas does not assess (electrolyte, metabolic, acid--base, dermal)". Same ledger value (80) as the supplement "80 of 85" row above; tracked under a distinct literal because the two documents now phrase it differently.'

- paper_section: '§2.6 secondary observations (Cornish complementarity)'
  paper_context: 'Cornish 2023 total Hoeffding rejections across 15 quantities'
  monograph_claim_id: 'T3.s028.cornish_total_hoeffding'
  expected_value: 85
  format_in_paper: '85 total Hoeffding-inequality rejections'
  expected_occurrences: 1
  notes: 'Appears once in §2.6 ¶3: "reported 85 total Hoeffding-inequality rejections across 15 physiological quantities".'

- paper_section: '§2.6 secondary observations (Cornish complementarity)'
  paper_context: 'Cornish 2023 rejections OUTSIDE the four-channel overlap (80 not-assessed + 2 SysBP partial)'
  monograph_claim_id: 'T3.s028.cornish_outside_overlap'
  expected_value: 82
  format_in_paper: '82 of 85'
  expected_occurrences: 1
  notes: 'Added in the [SCIENTIFIC] final-fixes pass (D.8 sweep finding A1). Appears once in paper §2.6 ¶3: "82 of 85 fall outside the four-channel overlap". The supplement S7 caption (L351) states the same decomposition as "82 fall outside" (no "of 85" literal), so this row is paper-only. Ledger anchor 82 = 80 not-assessed + 2 SysBP-partial, asserted to sum with 3 (overlap) to 85.'

- paper_section: '§2.6 + supplement S7 caption'
  paper_context: 'Cornish 2023 rejections ON the four-channel overlap (all PaCO2)'
  monograph_claim_id: 'T3.s028.cornish_overlap_hoeffding'
  expected_value: 3
  format_in_paper: '3 of 85'
  expected_occurrences: 2
  notes: 'Added in the [SCIENTIFIC] final-fixes pass (D.8 sweep finding A1). paper §2.6 ¶3 "only 3 of 85 fall on the four-channel overlap" (1) + supplement S7 caption L351 "only 3 of 85 fall on the four-channel overlap" (1). This number was present in both documents before but untracked; now guarded.'

- paper_section: '§2.4 Figure 4b caption (npj paper)'
  paper_context: 'Worst-case S1 hyperoxia numerical-runaway plateau, off the [0,760] visible range'
  monograph_claim_id: 'T1.24d.s021_s1_max_runaway_plateau'
  expected_value: 1408
  format_in_paper: '1{,}408'
  expected_occurrences: 2
  notes: 'Added in the [SCIENTIFIC] final-fixes pass (D.8 sweep finding A2). Appears once in the Figure 4 caption: "plateau off-scale (up to $\\approx$1{,}408~mmHg ...)". Verified against data/runs/s021_hyperoxia_convergence/plateau_stats.parquet (max S1 PaO2_plateau_mmHg = 1408.49); approx_round tolerance because the caption uses an explicit "~". Count raised 1 -> 2 on 2026-07-25: Supplement S9 now also cites the maximum as the upper end of the 1,169-1,408 mmHg female runaway range, in the corrected hyperoxia-signature paragraph. The sync corpus is paper.tex + supplement.tex, so both occurrences count; both state the same re-derived value (max S1 PaO2_plateau_mmHg = 1408.49).'

## Step 7 — Methods reproducibility constants

- paper_section: '§2 Results Terms box + §5 Methods §4.3 + supplement S3.2'
  paper_context: 'Morris design: number of trajectories per cell'
  monograph_claim_id: 'T1.06e.morris_trajectories'
  expected_value: 20
  format_in_paper: '20 trajectories'
  expected_occurrences: 6
  notes: 'Bumped 6 -> 5 (2026-07-27): the study-design figure was externalised to preprint_npj/figures/fig00_study_design.tex (see the T1.01 note for why), taking its arrow label "20 trajectories x 8 = 160 runs/cell" out of paper.tex. The label still renders in the figure. Earlier history: paper §5 Methods §4.3 (1) + supplement S3.2 Morris sampler description (1) + paper §2 Results "Terms used in this paper" box, Trajectory row (1). Bumped 1 -> 2 in Phase 9.A. Bumped 2 -> 3 in Phase G3 (2026-05-31): the new Terms box in §2 Results defines "Trajectory" with the literal "20 trajectories per cell yield 160 simulations" formulation, so the canonical formatted string appears once more. The box is the canonical scannable-terminology anchor placed at top of §2 Results immediately before §2.1 Overview. Bumped 3 -> 4 (2026-06-24): the new study-design Figure 1 caption ("20 trajectories of 7+1 = 8 simulations each") adds one more occurrence. Bumped 4 -> 5 (2026-06-24, pedagogy round): the new N=20 justification sentence in §5 Methods §4.3 adds one substring occurrence of the canonical "20 trajectories" string. (2026-06-25 correction: that sentence was reworded from an unsourced "typically 10--20 trajectories" convention to the preregistered rationale "These 20 trajectories were fixed in preregistration: enough to give stable mu* rankings, yet few enough to keep the full sweep feasible..."; still contains "20 trajectories" once, so count stays 5.) Bumped 5 -> 6 (2026-07-17): the study-design Figure 1 arrow label was expanded from "Morris sampling: 160 runs/cell" to "Morris sampling: 20 trajectories x 8 = 160 runs/cell" to show where the 160 runs/cell come from (20 trajectories x 8 points), adding one more occurrence of the canonical string. Bumped 5 -> 6 (2026-08-06): the Supplement §S3.7 addendum reporting the uncontaminated-step and combined estimators describes the trajectory-matched variant as restricting every input to "the 12 of 20 trajectories whose systolic step is uncontaminated", adding one occurrence.'

- paper_section: '§5 Methods §4.3 + supplement S3.2'
  paper_context: 'Morris design: number of grid levels per input'
  monograph_claim_id: 'T1.06f.morris_levels'
  expected_value: 4
  format_in_paper: '4 grid levels'
  expected_occurrences: 2
  notes: 'paper §5 Methods §4.3 (1) + supplement S3.2 (1). Bumped 1 -> 2 in Phase 9.A.'

- paper_section: '§5 Methods §4.3 + supplement S3.2'
  paper_context: 'Random seed for the canonical Morris sample'
  monograph_claim_id: 'T1.06g.morris_seed'
  expected_value: 42
  format_in_paper: 'seed 42'
  expected_occurrences: 3
  notes: 'paper §5 Methods §4.3 (1) + supplement S3.2 (1) + supplement S3 sampling-stability subsection (1), which names the canonical seed to contrast it with the seed-44 resampling. Bumped 1 -> 2 in Phase 9.A, then 2 -> 3 when that subsection was added.'

- paper_section: '§5 Methods + Supplement S3.Sobol'
  paper_context: 'Bootstrap resamples for Morris mu* CI (1,000)'
  monograph_claim_id: 'T1.06h.bootstrap_n'
  expected_value: 1000
  format_in_paper: '1{,}000'
  expected_occurrences: 3
  notes: 'Bumped 1 -> 3 (2026-07-29, second change that day): the post-hoc ratio-aware bootstrap was harmonised from 2,000 to 1,000 resamples so that a single resample count appears throughout the manuscript. The harmonisation is result-neutral: the stable set of 23 top-three combinations is identical at 1,000, 2,000 and 4,000 resamples (22 at 500), which the supplement now states as a sensitivity clause. The literal therefore gains one occurrence in paper 4.5 and one in Supplement S3-sobol, on top of the existing mu*-CI mention. Earlier history: Bumped 2 -> 1 (2026-07-29): Supplement §S3-sobol was rewritten around the ratio-aware bootstrap, which uses 2,000 resamples, so the literal 1,000 no longer appears there. It remains once in paper §4.5, where it still describes the mu* confidence intervals computed by morris_indices at n_bootstrap=1000. Earlier history: paper §5 Methods Statistical analyses Morris bootstrap (1) + supplement §S3-sobol Sobol bolt-on CI-aware re-evaluation (1). Bumped 3 -> 7 in Phase 9.B for the S6 Spearman additions; reverted to 2 in Pass 10 D16 (2026-05-27): the 5 Spearman bootstrap occurrences (1 paper + 4 supplement) corrected from 1,000 to 2,000 to match the actual function default in src/analysis_compare.py L96. Bumped 2 -> 3 in Phase G (2026-05-31): the Supplement §S3-sobol new subsection reports the CI-aware Sobol-trigger bootstrap with the same n=1,000 trajectory-level resamples as the mu* CI (identical RNG seed). Reverted 3 -> 2 on 2026-07-02: the §2.2 occurrence was removed when the H1 top-3 fraction wording was corrected from a 1,000-resample bootstrap confidence interval claim to a point-estimate framing (the top-3 fraction is a point estimate; the bootstrap CI attaches to mu*, not to H1). The Spearman + Wasserstein 2,000 occurrences are tracked under the row below.'

- paper_section: '§5 Methods + supplement S6'
  paper_context: 'Bootstrap / permutation N = 2,000 (Spearman rho input-resamples + Wasserstein within-sex permutation null)'
  monograph_claim_id: 'T2.analysis.spearman_n_bootstrap'
  expected_value: 2000
  format_in_paper: '2{,}000'
  expected_occurrences: 9
  notes: 'Bumped 10 -> 9 (2026-07-29, second change that day): two occurrences left when the post-hoc ratio-aware bootstrap was harmonised to 1,000 resamples, and one was added by the new sensitivity clause in Supplement S3-sobol, which reports that repeating the procedure at 2,000 and at 4,000 resamples returns the same 23 combinations. Net -1. The Wasserstein relabelling and Spearman input-resample mentions are untouched. Earlier history: Bumped 8 -> 10 (2026-07-29): the Sobol rewrite adds one occurrence in paper §4.5 and one in Supplement §S3-sobol, both stating that the post-hoc ratio-aware bootstrap resamples trajectories 2,000 times per combination. Earlier history: Bumped 6 -> 8 (2026-07-29): the Methods §4.5 Hypothesis-4 sentence was rewritten. The Wasserstein null is renamed from "2{,}000 random within-sex splits" to "2{,}000 random relabellings" -- the label within-sex misdescribed a null that pools the male and female clean runs and re-splits them at the two original group sizes, which is a relabelling of the combined sample, not a split inside one sex. That rename is count-neutral. Two further occurrences come from the new sentence declaring the resolution floor of the permutation p-value: "With 2{,}000 permutations the smallest empirical p-value the null can resolve is 1/2{,}000". Earlier history: paper §5 Methods Statistical analyses (2: "2{,}000 input-resamples" Spearman + "2{,}000 random within-sex splits" Wasserstein) + supplement S6 (4: intro prose, Table S2 caption, Table S2 column header "$n = 2{,}000$", Figure S2 caption "$n = 2{,}000$ input-resamples"). Five of the six are Spearman bootstrap; one (paper Wasserstein splits) uses the same literal 2,000 by coincidence (both function defaults are 2000 in src/analysis_compare.py: spearman_mu_star_male_vs_female n_bootstrap=2000 at L96 + wasserstein_per_output n_null=2000 at L32). Added in [METHODOLOGY] ledger expansion 2026-05-28 to close the audit gap surfaced by Pass 10 D16. The Wasserstein ledger anchor (T2.analysis.wasserstein_n_null) is separately defined in scripts/audit_claims.py; both anchors share the same numerical value but track distinct statistical methodologies.'

- paper_section: '§5 Methods Steady-state classifier (representative bounds) + Supplement S3.4 rationale table'
  paper_context: 'HR representative hard-bound range cited in paper L266 AND in supplement S3.4 per-bound rationale table row'
  monograph_claim_id: 'T1.06p.hr_low'
  expected_value: 20
  format_in_paper: 'HR [20, 220]~bpm'
  expected_occurrences: 2
  notes: 'paper L266 cites "representative bounds: HR [20, 220]~bpm" as the HR pair from the locked HARD_BOUNDS dict in src/detector.py L55 (HR: (20.0, 220.0)). Pass 10 D14 corrected the original wrong [30, 200] to the source-truth [20, 220]. Added in [METHODOLOGY] ledger expansion 2026-05-28; bumped from 1 -> 2 in the bounds-rationale expansion (2026-05-30) when supplement S3.4 added a per-bound primary-literature rationale row using the same literal. Supplement S3 Table S2 uses a different format ("HR (bpm) & 20 & 220") tracked by separate T1.06p anchors.'

- paper_section: '§5 Methods Steady-state classifier (representative bounds) + Supplement S3.4 rationale table'
  paper_context: 'PaO2 representative hard-bound range cited in paper L266 AND in supplement S3.4 per-bound rationale table row'
  monograph_claim_id: 'T1.06p.pao2_low'
  expected_value: 20
  format_in_paper: 'PaO$_2$ [20, 600]~mmHg'
  expected_occurrences: 2
  notes: 'paper L266 cites "PaO$_2$ [20, 600]~mmHg" as the PaO2 pair from the locked HARD_BOUNDS dict. Added in [METHODOLOGY] ledger expansion 2026-05-28; bumped from 1 -> 2 in the bounds-rationale expansion (2026-05-30) when supplement S3.4 added a per-bound primary-literature rationale row using the same literal. Supplement S3 Table S2 uses a different format ("PaO$_2$ (mmHg) & 20 & 600") tracked separately.'

- paper_section: '§5 Methods Steady-state classifier (representative bounds) + Supplement S3.4 rationale table'
  paper_context: 'SpO2 representative hard-bound range cited in paper L266 AND in supplement S3.4 per-bound rationale table row'
  monograph_claim_id: 'T1.06p.spo2_low'
  expected_value: 0.5
  format_in_paper: 'SpO$_2$ [50, 100]~\%'
  expected_occurrences: 2
  notes: 'paper L266 cites "SpO$_2$ [50, 100]~\%" as the SpO2 pair from the locked HARD_BOUNDS dict in src/detector.py L58 (SpO2: (0.50, 1.00)). Note: Pulse reports SpO2 as fraction 0-1 in source code; paper uses percent display convention (50-100%). Added in [METHODOLOGY] ledger expansion 2026-05-28; bumped from 1 -> 2 in the bounds-rationale expansion (2026-05-30) when supplement S3.4 added a per-bound primary-literature rationale row using the same literal.'

- paper_section: 'Supplement S3.4 per-bound rationale table'
  paper_context: 'MAP per-bound rationale row in supplement S3.4 tab:hard-bounds-rationale'
  monograph_claim_id: 'T1.06p.map_low'
  expected_value: 30
  format_in_paper: 'MAP [30, 180]~mmHg'
  expected_occurrences: 2
  notes: 'Added 2026-05-30 in the strict-crosswalk-coverage pass following the bounds-rationale expansion. Anchors the MAP row of the new supplement S3.4 tab:hard-bounds-rationale, whose rationale cites Sepsis-3 organ-perfusion failure threshold + Surviving Sepsis Campaign MAP target $\geq$ 65 mmHg (lower) and ESH 2023 hypertensive emergency at SBP $>$ 180 mmHg (upper). Paper §4.4 now lists MAP among the six locked hard bounds (2026-07-06 in-text expansion of the former 3-bound representative subset), so this literal appears twice in the npj corpus (paper §4.4 + supplement S3.4 rationale). Supplement S3 Table S2 uses a different format ("MAP (mmHg) & 30 & 180") tracked by a separate T1.06p anchor.'

- paper_section: 'Supplement S3.4 per-bound rationale table'
  paper_context: 'Vt per-bound rationale row in supplement S3.4 tab:hard-bounds-rationale'
  monograph_claim_id: 'T1.06p.vt_low'
  expected_value: 50
  format_in_paper: 'Vt [50, 1{,}500]~mL'
  expected_occurrences: 2
  notes: 'Added 2026-05-30 in the strict-crosswalk-coverage pass following the bounds-rationale expansion. Anchors the Vt row of the new supplement S3.4 tab:hard-bounds-rationale, whose rationale cites adult anatomical dead space $\sim$ 150 mL (lower, West 2020 Ch.2) and $\sim$ 4x ARDSnet lung-protective ventilation 6 mL/kg PBW (upper, Brower 2000). Paper §4.4 now lists Vt among the six locked hard bounds (2026-07-06 in-text expansion of the former 3-bound representative subset), so this literal appears twice in the npj corpus (paper §4.4 + supplement S3.4 rationale). Supplement S3 Table S2 uses a different format ("Vt (mL) & 50 & 1500") tracked by a separate T1.06p anchor.'

- paper_section: 'Supplement S3.4 per-bound rationale table'
  paper_context: 'PaCO2 per-bound rationale row in supplement S3.4 tab:hard-bounds-rationale'
  monograph_claim_id: 'T1.06p.paco2_low'
  expected_value: 10
  format_in_paper: 'PaCO$_2$ [10, 120]~mmHg'
  expected_occurrences: 2
  notes: 'Added 2026-05-30 in the strict-crosswalk-coverage pass following the bounds-rationale expansion. Anchors the PaCO2 row of the new supplement S3.4 tab:hard-bounds-rationale, whose rationale cites profound respiratory alkalosis from sustained maximal hyperventilation (lower) and CO2 narcosis threshold incompatible with conscious steady-state (upper), via Marino 2013 Ch.21 + West 2020 Ch.4. Paper §4.4 now lists PaCO2 among the six locked hard bounds (2026-07-06 in-text expansion of the former 3-bound representative subset), so this literal appears twice in the npj corpus (paper §4.4 + supplement S3.4 rationale). Supplement S3 Table S2 uses a different format ("PaCO$_2$ (mmHg) & 10 & 120") tracked by a separate T1.06p anchor.'

- paper_section: 'supplement S15 (Compensatory tachycardia)'
  paper_context: 'S1 output HR mean +/- std from monograph Section 3.4.1'
  monograph_claim_id: 'T2.s15.s1_output_hr_mean'
  expected_value: 73.8
  format_in_paper: '73.8 \pm 20.4'
  expected_occurrences: 1
  notes: 'supplement Section S15 Table S15 row for S1 healthy scenario: $73.8 \pm 20.4$. Added in [METHODOLOGY] ledger expansion 2026-05-28 (closing the Pass 7 D9 Concern 2(i) deferment).'

- paper_section: 'supplement S15 (Compensatory tachycardia)'
  paper_context: 'S2 output HR mean +/- std from monograph Section 3.4.1'
  monograph_claim_id: 'T2.s15.s2_output_hr_mean'
  expected_value: 87.3
  format_in_paper: '87.3 \pm 24.3'
  expected_occurrences: 1
  notes: 'supplement Section S15 Table S15 row for S2 mild ARDS: $87.3 \pm 24.3$. Added in [METHODOLOGY] ledger expansion 2026-05-28.'

- paper_section: 'supplement S15 (Compensatory tachycardia)'
  paper_context: 'S3 output HR mean +/- std from monograph Section 3.4.1'
  monograph_claim_id: 'T2.s15.s3_output_hr_mean'
  expected_value: 155.7
  format_in_paper: '155.7 \pm 34.7'
  expected_occurrences: 1
  notes: 'supplement Section S15 Table S15 row for S3 moderate ARDS: $155.7 \pm 34.7$. Added in [METHODOLOGY] ledger expansion 2026-05-28.'

- paper_section: 'supplement S15 (Compensatory tachycardia)'
  paper_context: 'S4 output HR mean +/- std from monograph Section 3.4.1'
  monograph_claim_id: 'T2.s15.s4_output_hr_mean'
  expected_value: 147.1
  format_in_paper: '147.1 \pm 31.8'
  expected_occurrences: 1
  notes: 'supplement Section S15 Table S15 row for S4 severe ARDS: $147.1 \pm 31.8$. Added in [METHODOLOGY] ledger expansion 2026-05-28.'

- paper_section: '§5 Methods §4.3 (scenario definitions)'
  paper_context: 'S2 mild ARDS impairment fraction'
  monograph_claim_id: 'T1.06i.ards_S2_severity'
  expected_value: 0.26
  format_in_paper: 'impairment = 0.26'
  expected_occurrences: 1
  notes: 'Appears once in §5 Methods §4.3: "S2, mild, impairment = 0.26". New ledger claim added in Step 7 (regex-extracted from src/scenario.py SCENARIOS).'

- paper_section: '§5 Methods §4.3 (scenario definitions)'
  paper_context: 'S3 moderate ARDS impairment fraction'
  monograph_claim_id: 'T1.06j.ards_S3_severity'
  expected_value: 0.60
  format_in_paper: 'impairment = 0.60'
  expected_occurrences: 1
  notes: 'Appears once in §5 Methods §4.3.'

- paper_section: '§5 Methods §4.3 (scenario definitions)'
  paper_context: 'S4 severe ARDS impairment fraction'
  monograph_claim_id: 'T1.06k.ards_S4_severity'
  expected_value: 0.95
  format_in_paper: 'impairment = 0.95'
  expected_occurrences: 1
  notes: 'Appears once in §5 Methods §4.3.'

- paper_section: '§5 Methods §4.3 (simulation duration)'
  paper_context: 'Each run simulation length in seconds'
  monograph_claim_id: 'T1.06n.sim_duration_seconds'
  expected_value: 120
  format_in_paper: '120 seconds of simulated time'
  expected_occurrences: 1
  notes: 'Appears once in §5 Methods §4.3: "Each run executed for 120 seconds of simulated time". New ledger claim added in Step 7 (regex-extracted from src/scenario.py DURATION_HOURS). Note: the related "120-second" hyphenated form appears multiple times elsewhere (§2.3, §2.4, §2.6, Figure 3 caption) but those occurrences refer to the window descriptor rather than the duration constant; no separate map row needed because both forms trace to the same SIM_DURATION_SECONDS constant.'

- paper_section: '§5 Methods §4.3 (output sampling)'
  paper_context: 'CSV output sample interval in seconds'
  monograph_claim_id: 'T1.06o.sample_interval_seconds'
  expected_value: 5
  format_in_paper: '5-second intervals'
  expected_occurrences: 3
  notes: 'Appears once in §5 Methods §4.3: "output channels sampled at 5-second intervals". New ledger claim added in Step 7 (regex-extracted from src/scenario.py SAMPLE_INTERVAL_S).'

## Phase 9.A - Supplement S3 Tables S2 + S3 (HARD_BOUNDS + DRIFT row literals)

## RETIRED 2026-08-02 (N-1, removal of Supplementary Methods) — the six
## HARD_BOUNDS table-row entries.
##
## They guarded the row literals of supplement.tex tab:hard-bounds -- 'HR (bpm)
## & 20 & 220', 'MAP (mmHg) & 30 & 180', 'Vt (mL) & 50 & 1500', 'SpO$_2$
## (fraction) & 0.50 & 1.00', 'PaO$_2$ (mmHg) & 20 & 600', 'PaCO$_2$ (mmHg) &
## 10 & 120'. That table was deleted: §4.4 of the main manuscript already listed
## all six pairs inline, so under npj's rule against Supplementary Methods the
## supplement's copy was a duplicate of the main text rather than provenance.
##
## No bound loses its guard. Each is still checked twice, in the inline form,
## by the six T1.06p.* entries above (expected_occurrences = 2): once in
## paper.tex §4.4 and once in the first column of tab:hard-bounds-rationale,
## which stays in the supplement. Verified after deletion: 'HR [20, 220]~bpm',
## 'MAP [30, 180]~mmHg', 'Vt [50, 1{,}500]~mL', 'SpO$_2$ [50, 100]~\%',
## 'PaO$_2$ [20, 600]~mmHg' and 'PaCO$_2$ [10, 120]~mmHg' each occur exactly
## once in paper.tex and once in supplement.tex. The values are additionally
## regex-extracted from src/detector.py HARD_BOUNDS by the 289-anchor layer,
## which this deletion does not touch.
##
## These six were NOT replaced by a literal built from the ledger-anchor names.
## Such a literal would have kept the entry count at 98 while guarding no
## number, which is a cosmetic audit rather than a real one. The count drops to
## 92 and that is the honest figure.

- paper_section: 'Supplement S3 Table S3 DRIFT HR row'
  paper_context: 'HR drift threshold per 60 s = 5 bpm'
  monograph_claim_id: 'T1.06q.hr_drift'
  expected_value: 5
  format_in_paper: 'HR (bpm) & 5 &'
  expected_occurrences: 1
  notes: 'Full S3 row literal (drift table). Pattern includes trailing ampersand to disambiguate from the HARD_BOUNDS HR row "HR (bpm) & 20 & 220".'

- paper_section: 'Supplement S3 Table S3 DRIFT MAP row'
  paper_context: 'MAP drift threshold per 60 s = 5 mmHg'
  monograph_claim_id: 'T1.06q.map_drift'
  expected_value: 5
  format_in_paper: 'MAP (mmHg) & 5 &'
  expected_occurrences: 1
  notes: 'Full S3 row literal; trailing & disambiguates from HARD_BOUNDS row.'

- paper_section: 'Supplement S3 Table S3 DRIFT Vt row'
  paper_context: 'Vt drift threshold per 60 s = 50 mL'
  monograph_claim_id: 'T1.06q.vt_drift'
  expected_value: 50
  format_in_paper: 'Vt (mL) & 50 & \texttt{T1.06q.vt\_drift}'
  expected_occurrences: 1
  notes: 'Vt drift threshold (50) and Vt hard lower bound (50) are coincidentally identical, so the shorter pattern "Vt (mL) & 50 &" matched both rows. Disambiguated by including the trailing ledger-anchor column (\texttt{T1.06q.vt\_drift}) so the pattern uniquely matches the DRIFT row.'

- paper_section: 'Supplement S3 Table S3 DRIFT SpO2 row'
  paper_context: 'SpO2 drift threshold per 60 s = 0.02 fraction (2 percentage points)'
  monograph_claim_id: 'T1.06q.spo2_drift'
  expected_value: 0.02
  format_in_paper: 'SpO$_2$ (fraction) & 0.02 &'
  expected_occurrences: 1
  notes: 'Full S3 row literal; trailing & disambiguates from HARD_BOUNDS row.'

- paper_section: 'Supplement S3 Table S3 DRIFT PaO2 row'
  paper_context: 'PaO2 drift threshold per 60 s = 15 mmHg'
  monograph_claim_id: 'T1.06q.pao2_drift'
  expected_value: 15
  format_in_paper: 'PaO$_2$ (mmHg) & 15 &'
  expected_occurrences: 1
  notes: 'Full S3 row literal; trailing & disambiguates from HARD_BOUNDS row.'

- paper_section: 'Supplement S3 Table S3 DRIFT PaCO2 row'
  paper_context: 'PaCO2 drift threshold per 60 s = 5 mmHg'
  monograph_claim_id: 'T1.06q.paco2_drift'
  expected_value: 5
  format_in_paper: 'PaCO$_2$ (mmHg) & 5 &'
  expected_occurrences: 1
  notes: 'Full S3 row literal; trailing & disambiguates from HARD_BOUNDS row.'

## 2026-05-30 - Supplement S3.5 tab:drift-rationale per-channel literals

- paper_section: 'Supplement S3.5 tab:drift-rationale HR row'
  paper_context: 'HR drift threshold + clinical-meaningfulness anchor in Supplement S3.5 tab:drift-rationale'
  monograph_claim_id: 'T1.06q.hr_drift'
  expected_value: 5
  format_in_paper: 'HR (5 bpm / 60~s)'
  expected_occurrences: 1
  notes: 'Added 2026-05-30 in the drift-rationale expansion. Supplement S3.5 tab:drift-rationale row for HR, anchored to standard ICU bedside monitoring practice (marini2019critical Ch.1). The "5 bpm" magnitude itself is an atlas-internal calibration choice, not endorsed as a specific threshold by the cited reference. Supplement S3 Table S3 drift row uses a different format ("HR (bpm) & 5 &") tracked separately.'

- paper_section: 'Supplement S3.5 tab:drift-rationale MAP row'
  paper_context: 'MAP drift threshold + clinical-meaningfulness anchor in Supplement S3.5 tab:drift-rationale'
  monograph_claim_id: 'T1.06q.map_drift'
  expected_value: 5
  format_in_paper: 'MAP (5 mmHg / 60~s)'
  expected_occurrences: 1
  notes: 'Added 2026-05-30 in the drift-rationale expansion. Supplement S3.5 tab:drift-rationale row for MAP, anchored to Sepsis-3 + Surviving Sepsis Campaign hemodynamic instability framing (singer2016, evans2021sepsis). The "5 mmHg" magnitude itself is an atlas-internal calibration choice, not endorsed as a specific threshold by the cited references. Supplement S3 Table S3 drift row uses a different format ("MAP (mmHg) & 5 &") tracked separately.'

- paper_section: 'Supplement S3.5 tab:drift-rationale Vt row'
  paper_context: 'Vt drift threshold + clinical-meaningfulness anchor in Supplement S3.5 tab:drift-rationale'
  monograph_claim_id: 'T1.06q.vt_drift'
  expected_value: 50
  format_in_paper: 'Vt (50 mL / 60~s)'
  expected_occurrences: 1
  notes: 'Added 2026-05-30 in the drift-rationale expansion. Supplement S3.5 tab:drift-rationale row for Vt, anchored to ARDS Network protective ventilation 6 mL/kg PBW (brower2000); 50 mL is approximately 1 mL/kg PBW on the atlas surrogates, within the noise band of breath-to-breath measurement at ARDSnet Vt. Supplement S3 Table S3 drift row uses a different format tracked separately.'

- paper_section: 'Supplement S3.5 tab:drift-rationale SpO2 row'
  paper_context: 'SpO2 drift threshold + clinical-meaningfulness anchor in Supplement S3.5 tab:drift-rationale'
  monograph_claim_id: 'T1.06q.spo2_drift'
  expected_value: 0.02
  format_in_paper: 'SpO$_2$ (2 percentage points / 60~s)'
  expected_occurrences: 1
  notes: 'Added 2026-05-30 in the drift-rationale expansion. Supplement S3.5 tab:drift-rationale row for SpO2, anchored to Severinghaus 1979 dissociation curve + Marino 2013 Ch.26 (Mechanical Ventilation) for the conventional noteworthy desaturation framing. The "2 percentage points" magnitude is an atlas-internal calibration choice, not endorsed as a specific drift threshold by the cited references. Supplement S3 Table S3 drift row uses a different format ("SpO$_2$ (fraction) & 0.02 &") tracked separately.'

- paper_section: 'Supplement S3.5 tab:drift-rationale PaO2 row'
  paper_context: 'PaO2 drift threshold + clinical-meaningfulness anchor in Supplement S3.5 tab:drift-rationale (with corrected Berlin P/F band framing)'
  monograph_claim_id: 'T1.06q.pao2_drift'
  expected_value: 15
  format_in_paper: 'PaO$_2$ (15 mmHg / 60~s)'
  expected_occurrences: 1
  notes: 'Added 2026-05-30 in the drift-rationale expansion. Supplement S3.5 tab:drift-rationale row for PaO2, anchored to Berlin ARDS Definition (ards2012). The rationale was rewritten in this same pass from the mathematically loose "Roughly one Berlin P/F band" (monograph L821) to the corrected "A 15-71 % fraction of one Berlin P/F band depending on FiO2" framing applied in both this supplement and the monograph drift table. The "15 mmHg" magnitude is an atlas-internal calibration choice. Supplement S3 Table S3 drift row uses a different format ("PaO$_2$ (mmHg) & 15 &") tracked separately.'

- paper_section: 'Supplement S3.5 tab:drift-rationale PaCO2 row'
  paper_context: 'PaCO2 drift threshold + clinical-meaningfulness anchor in Supplement S3.5 tab:drift-rationale'
  monograph_claim_id: 'T1.06q.paco2_drift'
  expected_value: 5
  format_in_paper: 'PaCO$_2$ (5 mmHg / 60~s)'
  expected_occurrences: 1
  notes: 'Added 2026-05-30 in the drift-rationale expansion. Supplement S3.5 tab:drift-rationale row for PaCO2, anchored to West 2020 Ch.4 (Blood Gas Transport) for the alveolar-ventilation framing. The "5 mmHg" magnitude is an atlas-internal calibration choice, not endorsed as a specific drift threshold by the cited reference. Supplement S3 Table S3 drift row uses a different format ("PaCO$_2$ (mmHg) & 5 &") tracked separately.'

- paper_section: 'paper.tex §2.5 + supplement S6.2'
  paper_context: 'Female-over-male tidal-volume excess per kilogram of actual body weight at any matched absolute setting'
  monograph_claim_id: 'T1.dose.excess_actual_pct'
  expected_value: 19.8
  format_in_paper: '19.8~\%'
  expected_occurrences: 2
  notes: 'Added 2026-08-04 with the ventilation-dose caveat. The sweep varies Vt in absolute mL over the same 300-800 mL range on both reference bodies, so a matched input vector is not a matched dose per kg; 67.3 / 56.2 = 1.1975. Appears once in paper.tex §2.5 (the sex-comparison caveat paragraph) and once in supplement S6.2 (the numeric expansion). The monograph carries the same figure in §3.6 but in Markdown form (19.8 %), which this crosswalk does not count.'

- paper_section: 'paper.tex §2.5 + supplement S6.2'
  paper_context: 'Female-over-male tidal-volume excess per kilogram of Pulse-computed ideal body weight at any matched absolute setting'
  monograph_claim_id: 'T1.dose.excess_ideal_pct'
  expected_value: 36.1
  format_in_paper: '36.1~\%'
  expected_occurrences: 2
  notes: 'Added 2026-08-04 with the ventilation-dose caveat. Ideal body weight is Pulse own quantity, computed at patient setup by the sex-specific Devine relation in SetupPatient.cpp:136-146 (74.99 kg at 180 cm, 55.10 kg at 163 cm); 74.99 / 55.10 = 1.3611. Deliberately NOT called ARDSnet predicted body weight: the metric coefficients usually attributed to that protocol could not be verified against an accessible primary source on 2026-08-04, recorded in audit/reference_audit.md. Appears once in paper.tex §2.5 and once in supplement S6.2.'
