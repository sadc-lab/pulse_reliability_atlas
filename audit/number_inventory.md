# Register — exhaustive inventory of the published numbers

**Opened 2026-09-13.** Producer: `scripts/audit_number_inventory.py`. Artefacts
under `results/number_audit/`: `inventory.csv`, `summary.json`,
`residue_by_literal.csv`, `masked_by_rule.csv`. This file carries the judgement
the script cannot: what each residual number is, and what it was checked against.

**Calibration** is not written here by hand — read
`summary.json` → `calibration` (probes and failures). A hand-written "16 probes"
went stale in this very register when two probes were added, which an
ultrareview caught.

**Why.** The ledger re-derives the numbers written *into* it. A published number
that was never registered is verified by nothing, and nothing reports its
absence. On 2026-09-10 twelve values entered Supplement S8 and S13 with no
anchor and surfaced only because the maintainer asked. This register exists so
the question stops depending on someone asking.

---

## 1. The population, fixed before anything was counted

The exclusion rule is in the producer's docstring and is applied mechanically;
every exclusion is counted per artefact so the denominator is auditable rather
than trusted. Nine rules: comments and code, cross-reference machinery, URLs and
file paths, three-part versions, typesetting lengths, source line references,
year-like integers, organisation identifiers, product versions.

⚠️ **Rules 8 and 9 were added after the first inventory, not before it.** The
paper's residue contained `3450` ("UR 3450 DevAH"), `1256` ("INSERM UMR\_S
1256") and the model versions `4.7`, `4.8`, `5.6`. They are not quantities. The
rule was extended and the calibration extended with it, rather than the rows
being waved away one at a time.

⚠️ **The unit is a run of digits** (noted 2026-09-15). A number written in words
("three of the four pairs", "eleven") is not in this population at all, so no
bucket, residue or mask ever shows it. See §9.

## 2. What the instrument measures

| artefact | retained | distinct | guard | ledger | ambiguous small | none | distinct none |
|---|---:|---:|---:|---:|---:|---:|---:|
| paper | 527 | 143 | 168 | 15 | 307 | **37** | 29 |
| supplement | 1887 | 490 | 490 | 26 | 960 | **411** | 210 |
| monograph | 3370 | 564 | 676 | 22 | 1878 | **794** | 334 |
| **all** | **5784** | **730** | | | **3145** | **1242** | **418** |

(Re-read from `summary.json` on 2026-09-15, after the monograph corrections
(`d9201de`, `441355e`), GL-S1 and GL-S2 (§6). The table first read 5,757 / 728 after
the §4.2 corrections; every movement since is explained in §5 "Resolution" and
§6.)

⚠️ **These buckets are coverage by VALUE, not by occurrence**, and they bound
risk from below, never from above.

* **`ambiguous_small` is not coverage.** A bare by-value match is meaningless for
  a small integer: in the first version, 3,764 occurrences landed in `ledger`, of
  which **3,171 had a value under 100**, median 8. A match now counts only for a
  distinctive literal (three significant digits, or ≥ 1000); the rest go to
  `ambiguous_small`. `summary.json` counts them under
  `not_demonstrably_covered_occurrences` together with `none`, and that is the
  honest reading.
* **A guard match was a substring test.** `"8" in guard_string` put 2,561 of the
  monograph's 2,954 occurrences in `guard`. Matching is now on digit boundaries.
* **In the other direction**, a number pinned as a Python float rather than a
  quoted string is invisible to the sieve: `check_input_ranges.py` holds the
  swept input bounds that way, which is why `0.21` and `110` sit in `none`
  although they are gated. A `none` row is a candidate, not an accusation.

### 2.1 Recall is accounted for, not assumed

The first calibration probes tested only **precision** — that machinery is not
mistaken for a claim. **Recall** is the worse failure: a literal that never
enters the inventory cannot appear in any residue. The producer closes the
books per artefact, and since 2026-09-13 also writes **every** removed literal,
with its rule and context, to `masked_by_rule.csv`.

| artefact | in raw text | removed by masks | inventoried | closes |
|---|---:|---:|---:|---|
| paper | 582 | 51 | 531 | yes |
| supplement | 1990 | 85 | 1905 | yes |
| monograph | 3778 | 255 | 3523 | yes |

(Monograph row re-read 2026-09-15; it read 3,749 / 3,494 before the §5
corrections added and removed wording. The paper and supplement rows are
unchanged.)

Literals removed per rule now: paper — comments 27, typesetting lengths 11
(all `\textwidth` fractions and `[-0.6em]` spacings, read), product versions 7,
machinery 4, organisation identifiers 2. Supplement — machinery 53, comments 12,
versions 7, typesetting lengths 6 (all column widths, read), file paths 2, line
references 2 (`lines 120--128`, read), organisation identifiers 2, product
versions 1; machinery was 54 until the F-S8 correction removed
`\mainref{sec:results-vcac}{2.3}`. Monograph — inline code 89, versions 55, link targets
42, URLs 42, line references 13, product versions 7, code fences 3.

✅ **Settled 2026-09-14, on the author's decision:** inline code cost the
monograph 89 literals, some of them real values rendered in backticks
(`[0.879, 0.946]` since the F-S5 correction, `0.02`, `0.425`). The instrument is
unchanged; the 89 were read apart, from `masked_by_rule.csv`, as a third
population (§5).

### 2.2 Defects found in this instrument, and what each one cost

Recorded in order, because several were found only by reading, not by any
check. They are not all of one kind. Four dropped published numbers silently,
the worst case, since a literal that never enters the inventory cannot appear in
any residue (1, 2, 6, 9). Two would have emptied part of the ledger set, which
overstates the residue rather than hiding it (4, 7). One misplaced literals on
the wrong line (3), one made a probe unable to fail (5), and one refused a
supported run outright (8).

1. **Fence rule** (commit `56ad746`). Every ```` ``` ```` block was masked as
   code, but five of the monograph's nine are pandoc raw-LaTeX blocks holding
   published tables, among them the per-cell flag breakdown
   (`S1\_M & 160 & 0 & 4 & 11 & 107 & 49`). **301 literals dropped silently.**
2. **Typesetting-length rule** (ultrareview, 2026-09-13). Whitespace was allowed
   between number and unit, and the English word "in" was a unit, so prose was
   masked: "144 of 160 **in** moderate", "0.6 **in** every draw", body heights
   "163 cm", "176.2 cm". **110 literals dropped, 8 of them from the paper**, whose
   row-by-row audit had therefore run on an incomplete population. Now only a
   glued unit (`0.5cm`, `2em`) is a length.
3. **Newlines erased by masks** (ultrareview). Every multi-line mask removed
   lines, so line numbers drifted: **+36 by monograph line 1577, +58 by line
   4591**. Masks now keep newlines.
4. **Ledger parse unchecked** (ultrareview). A crash in `audit_claims.py` would
   have emptied the ledger set silently and still exited 0. The parse now
   requires exactly as many claim rows as "Anchors verified: N / N" announces,
   and refuses to classify otherwise.
5. **Tautological year probe** (ultrareview). It compared two constants and never
   exercised the year rule. Probes now run the real extraction path.
6. **Numbers glued to an ordinal or a multiplier** (found by reading, same day).
   "the 95**th** percentile", "50**th**-percentile", "5--10**x** real time"
   produced no literal at all. ⚠️ **This one was invisible to the closed
   accounting**, because the same number pattern counts both the raw and the
   masked text: a literal it cannot see vanishes from both sides and the books
   still close. Ordinals and `x` are now allowed; hashes (`3b18bdc`), CPU models
   and figure panels (`4a`) are still rejected.

7. **Ledger values read at a fixed column** (found by a column-integrity check,
   same day). Seven claim texts contain a literal `|` ("median |EE| 20.44 …" in
   the S3.7 stratification table), which shifted the columns, so 20.44, 15.74,
   24.94, 17.26, 20.32, 16.74 and 3 never entered the ledger set. **Latent, and
   measured as such**: every one is also guard-pinned, so each was already in
   `guard` and the residue was 1,345 before and after. It would have bitten on
   the first ledger-only value with a `|` in its text. The value is now read
   from the right of the row.

8. **The ledger check refused the supported clean-clone case** (third
   ultrareview, run on `review-part3` against `review-part2`). The fix for
   defect 4 compared the parsed row count with the **denominator** of
   "Anchors verified: N / M", but audit_claims computes M = N + skipped
   (`audit_claims.py:3857`) and prints only the N claims that ran
   (`audit_claims.py:3905`). On a clean public clone — S021 raw trajectories
   gitignored, one anchor documented as SKIPPED, "393 / 394" — the inventory
   refused to run at all. It now compares with N, and records the skipped count
   in `summary.json` → `ledger`. **Measured, not assumed:** the one anchor that
   skips there, `T1.06u`, has the value 180, which `T1.06p.map_high` also
   carries, and all 25 occurrences of 180 are in `guard`; a clean-clone
   inventory would classify identically.
9. **Thousands-separated counts were discarded as years** (same review,
   classed pre-existing). The year rule tested the value, so "2{,}000" and
   "2,000" — bootstrap and permutation sizes in **all three** artefacts, the
   paper included (L379, "2{,}000 relabellings") — were read as 2000 and
   dropped. A year is now exactly four bare digits. **And the docstring's promise
   that dropped years are "written out separately" was false**: they were only
   counted. They now go to `masked_by_rule.csv` under rule `year_like`, with
   context. **All 171 rows were read one by one** (paper 4, supplement 16,
   monograph 151): 168 years or dates (publication years, "2000 CDC Growth
   Charts", the "1919" Harris–Benedict originals, "Severinghaus 1979",
   2026-MM-DD audit dates), 2 occurrences of the programme name "France 2030",
   and 1 page number ("1874-2071", ESH bibliography entry). No quantity is
   dropped. *(A first version of this paragraph claimed the full reading on the
   strength of the suspicious values alone; the row-by-row reading was done
   afterwards, before the commit was pushed.)*

**Every fix was calibrated by reinjecting the original defect** and confirming
its probe fails: 4 failures for rule 2, 1 for rule 3 (a literal reported on line
3 instead of 6), 1 for rule 5, 3 for rule 6, 1 for rule 7 (a synthetic table with
`|EE|` in a claim text), 1 for rule 8 (a synthetic "2 / 3" headline with two
rows, refused by the old check), 2 for rule 9, and an explicit refusal (exit 1)
for rule 4.

**Two review findings deliberately not applied**, both graded nit: running the
masks twice per artefact, and compiling a regex per literal in `_pinned`.
Measured: the whole inventory takes 5.3 s, of which 3.2 s is audit_claims
itself, so both together cost about two seconds. Refactoring an instrument that
has just been reviewed, to save two seconds, would add unreviewed code for no
measurable gain.

**The third review was incomplete** — it hit its 29-minute limit after four
findings. Its silence on the rest of the diff is not a certificate.

⚠️ **One claim was withdrawn before it shipped.** Rule 7 was first described,
in the code comment, as having made those anchored numbers "reported as
uncovered". Checking their buckets in the previous commit showed they never
were. A defect that is real is not thereby consequential; the comment now says
latent. Three of those reinjections first **failed to apply** — a `sed` or `perl`
pattern that matched nothing — and were caught only because the MD5 was checked
after injection; they were redone with an exact editor. And one probe was itself
wrong: it watched `144` in "144 of 160 in moderate", but the old rule masked
`160`, the number right before "in", so the probe could not fail. It now
watches `160`.

## 3. The paper's `none` residue, audited row by row — 43 occurrences, 31 values

**No defect found in these 43.** After the corrections above the paper's `none`
residue is the **same multiset** as before them. The 8 literals the corrections
recovered — `160` ×4 (L175 ×2, L204, L302, each "… of 160 in …"), `20` (L357),
`0.6` (L381), and `50` ×2 (L347, "50th-percentile") — all landed in `guard` or
`ambiguous_small`, not in `none`. The count is 514 → 522 retained. The later
year-rule fix (defect 9) recovered three more, all `2{,}000` on L379, all in
`ledger`: 522 → 525, `none` still 43. The list was checked against the old
pattern's matches rather than recalled: the
neighbouring `144`, `122` and `42` were already inventoried, and the old
pattern's one other prose match, at L53, is inside a comment.

⚠️ **What "audited" does and does not cover.** An earlier version of this
register called the paper **closed**. That overstated it: only the `none` bucket
was examined row by row. The paper's **305 `ambiguous_small` occurrences** —
small values whose ledger match may be a coincidence — have **not** been
verified one by one. The paper is not closed. *(Update: they were read row by
row later the same day. See §3.2, which finds one wording defect and still
does not close the paper.)*

Every one of the 43 falls into one of four classes.

**(i) Locked constants, derivable from `src/detector.py` or the preregistration.**
`0.05` (the CV threshold), `0.1` and `99.9` (the flatline tolerance), `13`
(samples in the window), `0.21` and `110` (swept bounds, gated by
`check_input_ranges.py`), `95` (bootstrap CI level), `0.001` (the `p <`
reporting convention), `14` (the exponent in $10^{-14}$).

⚠️ One of the `0.05` occurrences is **not** the CV threshold: it is the
Benjamini–Hochberg level *q*. Same value, different quantity — a reminder in one
document of why by-value coverage proves nothing.

**(ii) Externally sourced.** `12{,}642` and `70` (the cited ventilator-sharing
study), `71` mL kg⁻¹ (cited clinical estimate), `18` and `163` (CDC P50 body
dimensions, additionally gated by `check_cdc_weight_provenance`).

**(iii) Our own measurements, traceable to an artefact.** `36`, `25`, `1{,}400`,
`37`, `84.1`, `13`, `4{,}400` ×2, `8.4`, `86`, `0.879`, `0.945` ×4, `22`, `18`,
`4.1`, `5.5`, `93`, `0.625`, `0.12`, `3{,}348`.

*(Update 2026-09-14: `0.879` and two of the four `0.945` are the edges of the
continuous-severity band. Their artefact was computed on truncated severity
labels, so "traceable to an artefact" was true of the wrong artefact. The paper
now reads $[0.879, 0.946]$; see §4.1, F-S5.)*

**(iv) Checked arithmetically**, because they are cheap to settle:

| claim | derivation | verdict |
|---|---|---|
| `0.625` | 100 / 160 | 0.6250 ✓ |
| 13 samples | 60 / 5 + 1 | 13 ✓ |
| `84.1 %` | 37 / 44 | 84.09 ✓ |
| `86` mL | 4082 − 3996 | 86 ✓ |
| `8.4 %` | (4803 − 4400) / 4803 | 8.39 ✓ |
| `15.0 %` | (4803 − 4082) / 4803 | 15.01 ✓ |
| `93 %` | median top-3 fraction 0.928 | 92.8 → 93 ✓ |
| `18` combinations | S034 `rank_comparison.csv` | 18 ✓ |
| `3{,}348` setup logs | count on disk | **see below** |

### 3.1 The one apparent discrepancy, and why the paper is right

Counting `pulse.log` under `data/` gives **3,349**, against the published
**3,348**. `data/runs/` holds exactly 3,348; the 3,349th is in
`data/clamp_probe/`, a gitignored probe directory that is not a sweep run.
**My population was wrong, not the paper's.**

### 3.2 The paper's `ambiguous_small` residue, read row by row — 305 occurrences (2026-09-13)

**Population.** `inventory.csv`, `artefact = paper`, `bucket = ambiguous_small`:
305 rows, extracted with `scripts/parquet_probe.py` and sorted by line. Every row
was read with its context. `paper.tex` is unchanged since `063b122`.

**57 rows are not quantities.** These are sieve precision failures: they
overstate the residue and hide nothing. Counted per line with `parquet_probe`,
not by hand.

| what | lines | rows |
|---|---|---:|
| author and affiliation markers `\author[1,2,3]`, `\affil[n]` | 95–117 | 24 |
| enumeration labels (1)–(4) | 140 | 4 |
| licence and product versions: `Apache-2.0` ×6, `CC-BY-4.0` ×3, `claude-opus-4-7`/`4-8`/`5` ×5, Gemini `3.1`, Ryzen `5` | 140, 148, 341, 389, 404, 408 | 16 |
| hypothesis labels ("Hypothesis~1" ×2, "Hypotheses 2, 3 and 4", "Hypothesis-4") | 272, 377, 408 | 6 |
| notation: `SpO$_{2}$` subscript, `kg$^{-1}$` and `min$^{-1}$` exponents, the base of $10^{-14}$ | 272, 300, 353, 408 | 4 |
| grant identifier `ANR-23-IACL-0004` | 412 | 2 |
| the day in the date "3~August~2026" | 389 | 1 |
| **total** | | **57** |

The instrument is **not** modified for these rows. None of its nine exclusion
rules catches hyphenated versions, bracketed author markers or braced
subscripts. A
rule change is guard code, and it would reach `main` only after review.
Counting the rows here costs nothing and changes no conclusion.

**248 rows are quantities, all verified.** "Verified" means one of the
following, and the table names which.

- **(S) Source.** `preregistration.md`, code under `src/` or `scripts/`, or
  Pulse's own documentation, read this session.
- **(A) Artefact.** A results file read directly this session.
- **(L) Semantic anchor.** A ledger anchor or guard whose text names the
  **same quantity in the same sentence**, not merely the same value, with the
  paper literal read to equal it. A ledger anchor compares its own literal with
  the artefact. Only some anchors are also tied to the paper's text, through
  the sync map. For the rest, reading the paper supplies the missing half.
- **(X) Arithmetic.**

| family | lines | how | detail |
|---|---|---|---|
| Table 1, per-cell flag counts, and "42 of 160" quoted from it | 175, 204, 210–220 | A + L | every cell equals `results/cell_flag_summary.csv` (written by `analyze_sweep.py`); anchors `T1.T1-*` |
| Table 2, retention | 238–248 | L + X | `T1.30r.clean.*` and `.hardfree.*` re-derived from `data/runs/full_sweep/aggregated.parquet`; hard-failure-free = 160 − diverged − implausible in all eight cells; sums 663 and 1,134 |
| swept ranges, MAP $/3$ | 353 | S | preregistration L91, L95–101; `src/scenario.py:86` |
| severities 0.00 / 0.26 / 0.60 / 0.95, band 0.91–0.945 | 160, 181, 355, 377 | S + L | preregistration L76, L109–112; `T1.06i–k` |
| design: 20 trajectories, 4 levels, seed 42, $7+1=8$, 160, $4\times2=8$, 7 inputs, 5 s sampling, 120 s, final 60 s, $[60,120]$ | 162, 164, 181, 198, 278, 357, 365, 367 | S | preregistration L83–84, L170–171; `scripts/run_full_sweep.py:60` (`SWEEP_SEED = 42`) |
| hard bounds; flatline 1 % and 0.1 %; CV 5 % | 292, 363, 365 | S | `src/detector.py:54–61`, `FLATLINE_STD_RATIO = 0.01`, `FLATLINE_BOUND_TOL = 0.001`, `CV_THRESHOLD = 0.05`; preregistration table |
| 5 rejection patterns, 4 in force during the sweep | 361 | S | `CLAMP_PATTERNS` has 5; at `708efb1^`, the parent of the commit that added the "minimum" twin, it had 4 |
| every diverged run carries "Could not converge…", no completed run does | 361 | A | `grep` over all 1,280 `pulse.log` under `data/runs/full_sweep/`: 20 files, the same 20 case IDs as `diverged = True` |
| traffic light: bands 10 / 30 / 30 %; 7 / 29 / 12; drivers 7 / 23 / 9 / 9; red split 6 / 4 / 2; literal reading 7 / 3 / 38 | 227, 371, 373 | S + A + L | preregistration L205; `results/reliability_traffic_light.json`; `T1.25–27`, `T1.30d.*`, `T1.tl.literal_*` |
| setup: 0 of 1,280 clamped; 80 ventilator contracts in 20 runs; FiO$_2$ = 1.0 as a setting, and "exactly 1.0 cannot be composed" | 128, 173, 204, 282, 286, 292, 319, 321 | S + L | `T1.11`; setup-input instantiation guard (10,160 and 80 recomputed); FiO$_2$ adjustment guard; FiO$_2$ upper bound 1.0 in preregistration L100 |
| H1 48 of 48, top-3, "at least half"; H2 ≥ 5 % | 257, 272, 377 | S + L | preregistration L74–75; `T1.07` |
| σ/μ\* 0.6; 23 of 144; 17 of 48; Vt 8 of 23; 72 of 144; 43 of 48; Sobol $64\times(2k+2)$ | 259, 381 | S + L | preregistration L180–183; `T2.sobol.*` |
| cost factor "2.4 to 4.1" | 381 | X | 3,584 / 1,500 = 2.39 and 6,144 / 1,500 = 4.10, from anchors `T2.sobol.runs_reduced_*` and `.budget_preregistered`. ⚠️ The ledger's other 2.4 (`T5.clip.mustar_factor`) is a **different quantity**: exactly the by-value coincidence §2 warns about |
| index support: median 7 of 20 pairs; 25 on ≤ 3; 9 on a single pair, 5 of them rank-1; all nine are $V_t$ in S1\_F or FiO$_2$ in S4\_M | 259 | A | `results/sobol_ci_buckets.csv` (144 rows): median `n_clean_pairs` 7, `n_total_pairs` 20, `le 3` → 25, `eq 1` → 9 rows, 5 at rank 1, σ = 0 |
| S1 Vt CV > 0.05 on 139 of 320; S3 on 36 of 320 | 259 | L | Vt-CV scenario-split guard |
| relaxed screen: H1 48 under both; 30 like-for-like; rank-1 kept in 30; 11 sets change; FiO$_2$ gained in S1\_M, S1\_F, S4\_F, rank-1 for PaO$_2$ and SpO$_2$ | 259, 272 | L | S034 guard (25 checks) |
| trigger lockout: $-2$ cmH$_2$O, 64 reruns, 0.016 | 128, 276, 280, 292 | L | `T1.06d`, `T1.06b`, `T1.04` |
| hyperoxia: 34 of 126, 91 %, FiO$_2 \geq 0.95$; 60 reruns (S1 44 + S3 8 + S4 8); plateau window 240–300 s; 40 of 44; 643; about 20 mmHg below the AGE prediction; axes $[0, 760]$ | 284, 292 | A + L | `data/runs/s021_hyperoxia_convergence/summary.json` (`n_runs` 60, per-scenario n, `plateau_window_s`); `T1.21–24`, `T1.23b`; S021 guards; `scripts/make_paper_fig03.py:75` (`PANEL_B_AXIS_HI = 760.0`) |
| divergence: 20, 1.6 %, all male, 8 vectors; FiO$_2$ = 1.0 in 13 of 20 | 128, 173, 298, 308 | A + L | sex-stratified divergence guard; `aggregated.parquet`, `diverged = True`: 13 of 20 at `in_fio2` 1.0, 7 at 0.7367 |
| blood-volume rescue: 20 / 20 → 0 / 20 at 4,400 mL and at the floor; 12 of 20 clean at both, 8 flagged; reductions 0 / 8.4 / 15.0 % | 300, 308 | L + X | `T2.bv.bracket.*`, `T2.bv.floor.*`; 8.4 and 15.0 in §3 (iv) |
| sex comparison: 24 tests; ρ 0.75–1.00 over 12 cells; 1/2,000; two tests at zero; ±1 | 300, 379 | S + A + L | `T1.15`, `T1.19–20`, `T2.sp.*`; `src/analysis_compare.py` computes `np.mean(null >= w)`, so 1/2,000 is the smallest non-zero value; `results/wasserstein_male_vs_female.csv` has exactly 2 zeros |
| Cornish: 85; 82 of 85 outside, 80 + 2; 3 of 85 inside | 327 | L | `T3.s028.cornish_*` |
| limitation (vi): DBP/SBP ≤ 0.75; 9 of 20 DBP steps | 331 | S + L | preregistration L97; `T5.robust.paper_dbp_shortened` |
| Morris step on $[0,1]$ | 377 | S | `src/analysis_morris.py:146`: elementary effect = Δy / `delta_normalized` |
| external: 5-compartment lung; CDC 50th percentile | 341, 347 | S | Pulse `docs/Methodology/RespiratoryMethodology.md:116–118` in the local clone at `REL_4_3_2`, docs unchanged since `REL_4_3_1` (empty diff); CDC provenance guard |
| scale and conversion: SpO$_2$ on 0–1, so 0.12 is 12 points; μ\* = 0 | 272 | S + X | `HARD_BOUNDS["SpO2"] = (0.50, 1.00)` |

#### 🟢 One finding: a correct number under a wrong label (L259). Corrected on the author's decision.

> **Resolution, 2026-09-13.** Three wordings were put to the author, who chose
> to align the sentence with the supplement. `paper.tex:259` now reads
> *"… on 139 of 320 runs and none of those 8 falls there, against 36 of 320
> runs and 3 of the 8 in S3."* "Those 8" is the "8 of the 23" earlier in the
> same sentence. No number is new: 8 is anchored (`T2.sobol.core_output_vt`),
> and 0 and 3 were re-counted from the CSV rows.
>
> The Vt-CV scenario-split guard in `scripts/audit_claims.py` now also pins
> the figures (13 → 18 checks):
> - the 8 is re-counted from the CSV rows and must equal the JSON value;
> - the split 0 in S1 and 3 in S3 is pinned;
> - a negative control requires that the single-seed criterion gives a
>   different split, (1, 3);
> - the new paper text is required.
>
> **Reinjection.** The old sentence and a wrong split (S3 = 2) were put back
> temporarily. The guard failed on both, exit 1. MD5 of both files was
> identical before and after.
>
> **Rebuild.** In `build/paper.pdf` (25 pages) and `paper.docx`, the new text
> is on p. 7 and the old text is found nowhere.
>
> **Counts.** The sentence adds two `8` literals, both `ambiguous_small`, so
> the paper's bucket goes from 305 to 307 and its retained total from 525 to
> 527. §2 is updated from `summary.json`. The two new rows are the quantity
> just described.
>
> **The same paragraph, a second wording, also the author's choice
> (2026-09-13).** *"retaining only combinations that clear it … leaves 23 of
> the 144, spread over 17 of the 48 combinations"* used "combinations" for two
> units in one sentence. It now reads *"retaining only those that clear it"*.
> "Those" refers to the cell's top-three inputs, the unit the supplement
> (L345) and the monograph (L1905) already name: "23 of the 144 top-three
> inputs". No digit changes. `summary.json` is unchanged, and `inventory.csv`
> differs by one context string.
>
> The finding as recorded before the decision follows.

> *"in S1 the delivered-Vt coefficient of variation exceeds the 0.05 threshold
> on 139 of 320 runs and **no Vt combination is estimable**, against 36 of 320
> runs and **3 estimable combinations in S3**."* (`paper.tex:259`, added in
> `d88a1ca`)

- **The numbers are right under one reading.** In `results/sobol_ci_buckets.csv`,
  the $V_t$ top-three entries in the stable non-linear set
  (`nonlinear_all_seeds`) number **0 of 6 in S1** and **3 of 6 in S3**
  (S3\_F `peep`, S3\_M `fio2`, S3\_M `rr`).
- **"Estimable" is the wrong word.** In S1, 5 of the 6 $V_t$ entries *have*
  an estimable interval (`no_estimable_ci` = False); only S1\_F `vt` does not.
  They are estimable, but not stably non-linear.
- **"Combination" clashes with the paper's own unit.** Everywhere else a
  combination is cell × output, 48 in total. S3 has only two $V_t$
  combinations, so "3 estimable combinations in S3" cannot be read in that
  unit.
- **No anchor or guard covers the 0 or the 3.** The supplement's version of the
  sentence (`supplement.tex:347`) says it differently: *"none of those 8 falls
  in S1"*.

This is the hedging of a scientific claim, not a typo, so under the
repository's rules the wording is the author's call.

**What this does not cover.** The paper's `guard` (159) and `ledger` (18)
occurrences are covered **by value**. §2 says that bounds risk from below only.
A distinctive value can still carry a different meaning at a second locus. The
paper is therefore **not closed**. What is now true: its `none` residue (43) and
its `ambiguous_small` residue have been read row by row. That residue was 305
at the reading and is 307 after the correction, whose two new rows were read
too. The one wording finding is corrected.

## 4. The supplement's residue — characterised, not cleared

456 occurrences over 214 values, **concentrated**: the ten most frequent
literals account for 128 of them (`residue_by_literal.csv`). The bulk belongs to
families already settled for the paper — the ARDS instability band (`0.945` ×24,
`0.879` ×10), the swept input bounds (`110` ×16), the CV threshold (`0.05` ×14),
the bootstrap level (`95` ×17), and the ledger's own head-line count (`394` ×8,
gated by `check_audit_counters`, invisible to the sieve because it is computed).

Four tail values settled arithmetically:

| claim | derivation | verdict |
|---|---|---|
| BV male `4{,}802.63` mL | 65.6 × 67.3^1.02, Pulse's own allometric relation | 4802.63 ✓ |
| BV female `3{,}996.09` mL | 65.6 × 56.2^1.02 | 3996.09 ✓ |
| sex BV gap `16.8 %` | (4802.63 − 3996.09) / 4802.63 | 16.79 ✓ |
| DBP clip ceiling `75` mmHg | 0.75 × 100, the pulse-pressure rule | 75 ✓ |

Identified but not re-derived: `94` (a Cornish et al. 2023 denominator,
external), `96` (P/F at severity 0.95), `633.3` and `0.737` (Morris design
levels), `686` (mean female PaO₂), `6.84` (the host-suspension wall-time gap).

⚠️ **Characterisation, not clearance.** The supplement is **not** closed.

> **Update 2026-09-14.** The paragraph above calls the ARDS instability band
> (`0.945`, `0.879`) a family "already settled for the paper". §4.1 finding
> **F-S5** shows it was not: the band edges come from truncated severity labels.
> The characterisation is kept as the dated record.

### 4.1 The supplement's `none` residue, read row by row — 456 occurrences (2026-09-14)

**Population.** `inventory.csv`, `artefact = supplement`, `bucket = none`: 456
rows over 161 source lines, extracted with `scripts/parquet_probe.py`.
- Every row was read with its context. `supplement.tex` is unchanged since
  `d46dfdf`.
- The audited line set was compared mechanically with the population's line
  set: 161 of 161, none missing, none extra.

**6 rows are not quantities:**
- `4.3` in the release name "4.3.x" (L139);
- `5000` in the product name "ASL-5000" (L149);
- `3050` in the product name "RTX 3050" (L886);
- `13` in the archive path date `reproduction_macos_2026-06-13` (L976);
- `22` in the amendment identifier "2026-04-22-b" (L357);
- `3.8` in the section number "Section~3.8" (L357).

**450 rows are quantities.** Each was checked against a named source. Unlike
§3.2, many of the sources here are external or experimental, so the method is
stated per family.
- **(S)** A source read this session: code, preregistration, a primary
  publication, or Pulse's own source or documentation.
- **(A)** An artefact read or recomputed this session. Where a script was
  needed it was written read-only in the session scratchpad and checked
  against a known anchored value first.
- **(L)** A ledger anchor or guard naming the same quantity.
- **(X)** Arithmetic.
- **(P)** A verification recorded in an earlier session and **not** repeated
  here. It is labelled wherever it is the only support.

| family | lines | how | detail |
|---|---|---|---|
| limitations table, bound probes | 139–164 | S + A | age gate `SetupPatient.cpp:43` (18.0); ranges preregistration L95, L98; PC-AC 11.3 / 25.3 / 15.3 % and VC-AC 0.0681 / 1.01 / 2.25 % **re-scraped** from pulse.kitware.com (mechanical-ventilator methodology, 2026-09-14), the printed % being a symmetric relative difference (111.783 / 991.1 = 11.28 %); S030b probes `hr49/hr111/rr7/rr21` exit 1 with no CSV and the rejection text in `pulse.log`, `hr50/hr110/rr8/rr20` exit 0 |
| hard-bound justification table | 208–218, 257, 263 | S + X | Marini 2018 PDF p. 21, verbatim "(220 - age)/min", and p. 20 bradycardia; West 11th ed. p. 25/30 "about 150 ml"; Marino 2013 PDF p. 510 "10 to 15 mL/kg", in *Positive Pressure Ventilation* (Ch. 25); Sepsis-3 SOFA MAP < 70 (PMC4968574); SSC 2021 MAP 65 and "approximately 60 mm Hg … tracks linearly" (PMC8486643); ESH 2023 §16.2.1 grade 3 ≥ 180/110 with acute HMOD; Nin 2017 (PMC5630225) 1899 patients / 927 ICUs / 40 countries / 48 h / 70 mmHg ≈ 95th percentile; Severinghaus equation gives S = 0.5 at 26.86 mmHg and S = 0.3198 at 20 mmHg; 15 / 0.21 = 71 %. **F-S2** (below) |
| detector wording | 225, 270, 306, 423, 427, 450, 458, 677 | S + L | `src/detector.py` constants; preregistration amendment 2026-04-22-b; SpO₂ ceiling 0.999 at `nss_decomposition_table.py:58`; 530 − 360 = 170 |
| FiO₂ adjustment, bodies, CDC | 286–294 | L + S + X | FiO₂ guard (13, 0.04 %); the six CDC P50 decimals re-read in the official `wtage.csv` (Firecrawl, 2026-09-14), the CDC guard transcribes all six and exercises five in its checks (the female 218.5 value is transcribed but never compared); 67.3 / 1.8² = 20.77; Pulse height constants 177.0 / 163.0 / 175.5 / male floor 163.0 (`SetupPatient.cpp:70–75`) |
| S032 clip | 312–334 | A + X | `results/s032/morris_step_contamination.csv`: 9 of 20 DBP steps shortened, 5 at 6.25 % (0.83 mmHg), 1 at 56.25 %, 3 at 62.5 %; 8 contaminated; 123/140; all 11 full steps at SBP ≥ 100; the transition table equals `transition_stratified_contrasts.csv`; the **max factor 15.4** was never anchored and is re-derived: median 2.3676 reproduces anchor `T5.clip.mustar_factor`, max 15.392 (S1_F, Vt) |
| Sobol | 341–345 | S + A + X | k per cell 3–6 and costs from `sobol_ci_buckets.json`; 3,584 / 1,500 and 8,192 / 1,500; `s019_sobol_bolton.py` 6 cells × 256 × 9 = 13,824; resample robustness (1,000 / 2,000 / 4,000 equal, 22 at 500) **(P)** S031 log |
| F-003 reclassification | 357 | A + X | `f003_physiological_reclassification.csv`: 34 → 32 reclassified, 31 at FiO₂ 1.0, 21 F / 11 M; exception S1_F_0056 (FiO₂ 0.737, 678.6 mmHg, PaCO₂ 16.2) gives 0.737 × 713 − 16.2 / 0.8 = 505; the two non-reclassified runs (Vt 800, RR 20) sit at 475–483 mmHg to t = 60–75 s, then about 1,000 in raw `output.csv` |
| seed sample dependence | 404 | A | ratio 0.667 → 0.547 (seed-44 parquet); ra_lo 0.287–0.309; S2_M divergence 7/160 vs 4/160 |
| S030 Berlin calibration | 462–496 | A + L | 40 runs, 0.910–0.945 exit 1 in both arms, 0.900 / 0.950 exit 0; trigger arms at [240, 300] s: 30.6 / 418 / 43.6 against 20.0 / 50.8 / 91.5; the Berlin sweep table equals `pf_berlin_by_scenario.csv` cell by cell, and the producer re-run gives a byte-identical file; the companion anchors are read in `Pulse_translation_new/experiments_log.md`. **F-S1** |
| severity mapping table | 513–521 | S + X | `RespiratoryModel.cpp` nodes, linearly interpolated: 8.8 / 15 / 22.5, 0.70 / 0.55 / 0.45, 0.57 / 0.20 / 0.075, 0.22 / 0.20 / 0.125, in the four functions named in the caption |
| companion instability probes | 527 | S | companion log: March 28-run sweep fails at 0.92 / 0.94; E10 fine subset of 10 runs, 8 consecutive failures; E6 severe fine sweep of 9 runs, 4 failures and 5 passes |
| continuous severity sweep | 531–566 | A | midrange inputs read from the parquet; **F-S5** |
| Spearman CI table | 576–608 | A + L | equals `spearman_mu_star.csv` in all 12 rows |
| ventilation dose | 614–618 | S + X | Devine `SetupPatient.cpp:139/144`; 74.99 / 55.10 kg; 4.46–11.89, 5.34–14.23, 4.0–10.67, 5.44–14.52 mL/kg; +19.8 %, +36.1 % |
| Cornish table | 639–668 | S + X | arXiv 2301.07210v4 Tables 4–5 (p. 47–48) re-read: all 15 rows in both columns, totals 85 / 281; 13/70, 4/78, 3/92, 1/162 |
| S033 cycle resolution | 685–726 | A + L | `s033_summary.json`: 15 / 6 / 6 / 3, 530 → 536 (+1.13 %), gaps 0.59–8.65 % (2 each way), S1_F_0016 at 819.027985, 1,251 runs with median 5.38 %, p95 38.2 %, max 94.9 %, 126 above 20 %, 4 verdict-split runs all cycle-only; S4_F_0003 and S4_F_0089 are exactly equidistant from the median 0.350867 (the id breaks the tie), locked CV 0.0054, native Vt median 640.07 mL over native [180, 240] s |
| S021 extended hyperoxia | 745–781 | A + L | six runaways of 44 (13.6 %), all at Vt 633.3 (6 of 20; 0 of 24 elsewhere), VE 12.67 ×5 and 10.13; 3 non-runaways at VE 12.67; pairs F 5/5 and M 1/5, male 770 against 1,126–1,408; 686.0 vs 662.6; table S4 72.6 [70.8, 75.5]; median trajectory over the 37 runs 530.2 → 641.1, 95 % at 180 s; clean-S1 OLS n 91, R² 0.902, 81.1 ± 11.0 / 214.2 ± 29.9, 505.5·FiO₂ − 25.1, 480 at 1.0; S011 guard |
| blood volume and S018 | 789–827 | S + A + X | `SetupPatient.cpp:534–536` (65.6·w^1.02, ×0.85, ×1.15); all subtractions and ratios; Nadler equations give 72.96 / 63.78 (coefficients **(P)** from the register's verbatim scan quote); S018 parquets: the same 8 flagged cases at both levels, 656.99 / 686.42 mmHg, 0.737 ×3 and 1.0 ×5, SpO₂ flatline 7, PaO₂ drift 3. **F-S3**, **F-S4** |
| sex-conditioned parameters | 836–848 | S + X | Pulse source: fat 0.21 / 0.28; Hb 15 / 14 so Hct = Hb/34 = 0.4412 / 0.4118; CO 5,600 / 4,900; dead space 0.002 × IBW with the 4.5 kg intercept gap = 9 mL; lung tissue 0.50·W/77.11 vs 0.42·W/58.97 gives +9.8 % at equal weight and −8.3 % native; BMR 88.632, where Roza–Shizgal's 88.362 is **(P)**, and 0.27 / 1,751.9 = 0.015 % |
| compute effort | 886–890, 931 | A | canonical parquet 41.12 h naive, 27.39 h without S4_M_0123/0124; each of those runs minus the S4_M median = 6.838 h; `run_meta.json` mtime span 20.78 h; Intel re-execution 45.97 h, or 27.0 h without S3_M_0002/0003; independent host 45.96 h; `phase4a_run.log` 23h01m12s and `reproduction_check_2026-06-07.md` 23h01m21s |
| reproductions | 962–976 | A + L | head-line guard; ThinkPad pilot max\|Δ\| = 0 with 22/22 flags and 20 CSVs; macOS max\|Δ\| = 2.9 × 10⁻⁹ with 0/110 flag cells; full-sweep H4 round-off 2.8 × 10⁻¹⁴ |
| SHAP surrogate | 995–1044 | L + A | S023 and S034 guards; distinct top-3 sets per cell × output: Morris 25, SHAP **9**. **F-S6** |
| HR decoupling | 1076–1092 | A | clean-run output HR per scenario re-derived: 73.8 ± 20.4, 87.3 ± 24.3, 155.7 ± 34.7, 147.1 ± 31.8; the ledger anchors only transcribe these from the monograph |
| S012 window tolerance | 1109 | A | `s012_*` CSVs, plus the hyperoxia PaCO₂ row that no CSV carries, recomputed as 7/195 = 3.59 %, median 0.575 (HR 2.56 % reproduced as control) |
| summary table | 1134–1140 | L | repeats of verified figures, and F-S5 |

**Uncited general statements met on the way**, not number defects: adult
breathing "approximately 0.25 Hz"; a minute-ventilation "physiological norm of
6–8 L/min".

#### Findings — nothing modified; all brought to the author

- **F-S1 — L462 attributes the Berlin calibration to E6.** The numbers 256 /
  150 / 96 and 199 / 150 / 119 come from the companion's **March 2026 28-run
  sweep**, which has no E-number: 256.0 / 150.1 / 96.1 / 199.3 / 118.7 in
  `Pulse_translation_new/experiments_log.md` L586ff.
  - E6 (April), run with the protocol in its `results.json`, gave **251.9 /
    148.2 / 74.8**.
  - The table caption (L468) and the monograph (L4347) attribute the numbers
    correctly.
  - Unresolved: the in-repo replication adopted E6's protocol as "the
    companion's measurement window" and reproduces the **March** values,
    whereas E6 under that protocol gave 75 at 0.95. The "within 0.6 %" is
    numerically true, but the window equivalence is not established.
  - Two code comments misattribute the provenance: `audit_claims.py:5112` and
    `audit_s030_provenance.py`, which says the values were "retrieved verbatim
    from … e6_ards_calibration/results.json"; they are not in that file.
  - ✅ **Corrected on the author's decision, 2026-09-14** (option B, correct
    and qualify).
    - **L462** now credits "the original ARDS severity calibration, a 28-run
      impairment sweep of 2026-03" (monograph Appendix B.3 was re-read and
      documents that campaign: 120 s settle, 10 s sampling, 5 min runs). It
      adds that E6 (2026-04) re-ran the three fractions and obtained 252, 148
      and 75 mmHg, in the same three bands.
    - **L464** now states the replication window as "a [108, 168] s window
      derived from the timing recorded with E6". It says that E6 averaged its
      last five 10-s samples, which was **read in
      `Pulse_translation_new/pipeline/tests/test_e4_e6.py` L61–63 and
      L143–144**. A first draft said "whose final 60 s are averaged", and it
      was corrected before commit. The sentence also states that the agreement
      is empirical, not a protocol match.
    - **Code:** both provenance comments are corrected, and `T1.06u`'s label
      now says 37 runs.
    - **Guards:** the S030 provenance guard (34/34) still finds every pinned
      phrase; `audit_s030_provenance.py` passes 16/16.
    - **New supplement literals:** 252, 148 and 75 (E6), 28 (runs), 108 ×2
      and 168 (the window), 120, 60, 10 and 5 (timings), and the date fragments
      03 and 04 (2026-03, 2026-04). Each was read in the companion log, the E6
      code or the monograph. `148` lands in `ledger` by value coincidence
      only.
- **F-S2 — L212, and monograph L1213: "6 mL/kg PBW ≈ 400 mL on the atlas
  reference bodies".**
  - PBW is 74.99 kg (male), giving 450 mL, and 55.10 kg (female), giving
    331 mL; the supplement computes both weights itself at L618.
  - 403.8 mL is 6 mL/kg of *actual* male weight. "~4×" then becomes 3.3× or
    4.5×.
  - The bound is unchanged. `brower2000` supports "6 mL/kg PBW" only.
  - ✅ **Corrected, author's choice 2026-09-14.** Re-verified with both PBW
    formulas before editing: ARDSnet gives 75.12 / 55.15 kg, i.e. 450.7 /
    330.9 mL; Devine gives 74.99 / 55.10 kg, i.e. 450.0 / 330.6 mL;
    1500 / 450 = 3.33 and 1500 / 331 = 4.53. Supplement L212 and monograph
    L1213 now read "~3–4.5×" and "≈ 450 and 330 mL on the male and female
    reference bodies / surrogates".
- **F-S3 — L827: "three of the eight on the delivered-Vt oscillation".** The
  count is 3 at the 4,400 mL bracket and **4 at the floor**: S2_M_0119_floor
  adds Vt CV 0.071. Every other count in that paragraph holds at both levels.
  Introduced in `e93a750`; no anchor.
  - ✅ **Corrected, author's choice 2026-09-14.** Re-counted with a second
    script over both classified parquets (bracket 3, floor 4; SpO₂ flatline 7,
    PaO₂ drift 3 and implausible 1 at both levels). The sentence now reads
    "three of the eight at the 4,400 mL bracket (four at the floor)".
- **F-S4 — L815, citation mismatch (`nadler1962`): "averaging 75 in men".** Per
  the verbatim quote recorded in `reference_audit.md`, Nadler's 75 mL/kg is the
  **overall** average and 66 is the women's. This wording exists in the
  supplement only (`20ea152`). Recorded in `reference_audit.md`; nothing
  modified, as the citation-audit rule requires.
  - ✅ **Corrected on the author's decision, 2026-09-14:** "averaging 75
    overall and 66 in women". `reference_audit.md` is marked RESOLVED.
- **F-S5 — the continuous-severity band and bin table use truncated severity
  labels.**
  - Pulse ran the exact severity (`config.json`, e.g. 0.9458464400964033), but
    the run directory is labelled `int(sev*1000)`
    (`continuous_ards_sweep.py:118`), and `make_supp_fig_s1.py` parses severity
    from that label.
  - On the simulated values, divergence spans **0.87977–0.94585**. The
    containing interval at 3 dp is **[0.879, 0.946]**, so the published upper
    edge 0.945 excludes one male divergence.
  - Bin counts per sex are **31 / 19 / 19 / 9 / 2 / 20**, against a published
    31 / 20 / 18 / 10 / 2 / 19. Female / male divergences per bin are 14/19 vs
    5/19, 5/9 vs 8/9, and **0/2 vs 1/2** in (0.945, 0.95], where 0/2 was
    published for both. "0 / 51" becomes 0 / 50.
  - Totals (19 F, 14 M) and the qualitative reading hold: no divergence ≤ 0.85
    or > 0.95, female-dominated low band, male-dominated high band.
  - The band appears in the paper (L329 contribution sentence, L355), in the
    supplement ×7, the monograph ×9 and the README ×1. No anchor pins it. §3
    above classed the paper's `0.879` as an artefact-traceable measurement, and
    that artefact is the truncated one.
  - ✅ **Corrected on the author's decision, 2026-09-14.** Option A, recompute
    on the simulated severity, was chosen.
    - **Re-verified first with a second instrument**, from the 200 raw run
      directories (`config.json`, `run_meta.json`, `output.csv`) without the
      parquet. The label equals `floor(sev·1000)/1000` for all 200 runs; the
      raw data and the parquet agree run by run. Binning on the truncated
      label reproduces the published table exactly, which is the positive
      control that pins the cause. Exactly six runs change bin, three per sex
      (0.85018, 0.94585, 0.95064).
    - **Figure S1** is regenerated from `config.json` severities by the fixed
      `make_supp_fig_s1.py`, under the pinned `SOURCE_DATE_EPOCH`; two
      successive runs are byte-identical.
    - **Text:** paper ×2, supplement (L145, table caption, table, reading
      guides, figure caption, "0 / 50", regimes, L867, L1135), monograph ×11
      including the per-sex ranges 0.879–0.928 and 0.899–0.946, the README,
      and the cover letter. The S009 notebook gets a dated correction note.
    - **New guard `check_continuous_severity_band`** (21 checks) re-derives the
      band, the per-sex ranges and both bin tables from the parquet's
      simulated column. It requires the corrected text and bans the truncated
      figures in five files. A negative control requires the truncated column
      to give a different band and table.
    - **Reinjection:** the old band put back into `paper.tex` → 2 FAIL, exit 1;
      MD5 restored.
    - **Rebuilt:** paper 25 p., supplement **62 p.**, and the monograph, all
      PDF + DOCX, with no old figure rendered.
  - **Bucket movement caused by this correction** (the register's §2 is
    re-read from `summary.json`):
    - The new guard pins `0.879`, `0.945`, `0.946`, `0.899` and `0.928` as
      literals, so every occurrence of those values now lands in `guard`. That
      includes the *documented* 0.91–0.945 zone, which the guard does not
      check. This is the by-value limit of §2, made larger by a guard's
      banned-string list: paper `none` 43 → 37, supplement 456 → 423,
      monograph 846 → 806.
    - The rows audited above were audited as `none` and stay audited.
    - New `none` literals, each verified in the re-derivation: `0.001` and
      `0.031` (edge gaps 0.946 − 0.945 and 0.91 − 0.879), `0.09` ×2 (Wilson
      lower bound for 1/2), and `0.9458` (the male divergence).
- **F-S6 — L1030: "about a dozen" distinct SHAP top-three sets.** The measured
  count is 9, in the unit that gives Morris its 25. `5a6b201` records 9–10
  across forest seeds. The imprecision runs in the conservative direction.
  - ✅ **Corrected, author's choice 2026-09-14.** Re-counted with pandas, a
    second instrument after the first awk pass: 9 distinct (output, SHAP set)
    against 25 for Morris, full-set agreement 23/48. The 9–10 seed range lives
    in a commit message only and no artefact records it, so the text states
    the verifiable value: "take nine distinct values in total".

**Tooling notes.** Guard code, so not changed without review:
- `T1.06u`'s `manuscript_text` says "38 physiological-converged S1 runs"; it
  computes on 37, which is also what the supplement says.
- The two provenance comments of F-S1.
- F-S5's root cause was in `make_supp_fig_s1.py`; it is fixed with the
  correction above.
- `continuous_ards_sweep.py` still writes a parquet column named
  `ards_severity_continuous` that holds the **truncated** label, because it is
  rebuilt from the directory name. The producer was not changed and not
  re-run: the column is left as recorded, and the new guard documents and
  exercises the trap.

**Not covered.** The supplement's `ambiguous_small` (940) and its by-value
`guard` / `ledger` occurrences are not read here. The supplement is **not
closed**.

> **Update 2026-09-14.** `ambiguous_small` is now read row by row in §4.2. The
> by-value `guard` / `ledger` occurrences are still not read.

### 4.2 The supplement's `ambiguous_small` residue, read row by row — 957 occurrences (2026-09-14)

**Population.** `inventory.csv`, `artefact = supplement`, `bucket =
ambiguous_small`: 957 rows over 289 source lines, extracted with
`scripts/parquet_probe.py`.
- `supplement.tex` is unchanged since `32bdea7`. The inventory was re-run before
  counting and produced no diff.
- Every row was read with its context.
- **Line coverage is mechanical.** A read-only scratchpad script over
  `inventory.csv` attributes each of the 289 lines to exactly one family below
  or to a line holding only non-quantities: 919 + 38 = 957 rows.
- The script's first run failed on its own mapping: one line (388) had no
  owner, and five (752, 957, 958, 1008, 1133) had two, from overlapping line
  ranges. The ranges were corrected before anything was counted.

**134 rows are not quantities.** Each (line, literal) pair was checked against
the population as a multiset: every claimed pair is present, and none is
claimed more often than it occurs.

| what | rows |
|---|---:|
| LaTeX macro arguments `\numberline[1]`, `\mainref[2]` (L48, L72) | 4 |
| author and affiliation markers (L78–100) | 24 |
| figure, table, section, item and layer references | 24 |
| notation: $R^2$, unit exponents $^{-1}$, bases of powers of ten | 19 |
| date fragments: release, commit and archive-path dates | 17 |
| limitations-table row labels 1–12, and "rows 5–6", "row 4" | 15 |
| LaTeX column spans `\multicolumn`, `\cmidrule` | 14 |
| code-listing step numbers 1–5, and the `MSYS_NO_PATHCONV=1` switch | 7 |
| licence and product versions: Apache-2.0 ×2, CC-BY-4.0 ×2, Windows 11, Ryzen 5 | 6 |
| names and identifiers: Sepsis-3 ×2, F-003, "Hypothesis~1" | 4 |
| **total** | **134** |

These were checked anyway, because a wrong pointer or date misleads just as a
wrong number does:
- **Dates.** The `REL_4_3_2` tag is dated 2025-08-12. "2026-07-26" matches the
  `run_meta.json` mtimes (S030 20:24–21:10, S030b 23:23–23:34) and commit
  `708efb1`. The three archive directories exist.
- **Pointers.** Paper figure numbers were read in the rendered `paper.pdf`: Fig. 2
  is the curation map, Fig. 3 the Morris heatmaps, Fig. 4 the corrections. Table
  numbers too: Table 1 is the terms, Table 3 the per-cell flags. Monograph
  Figure 5 is the Spearman figure. "Item 7" is preregistration L205. "Items
  1–6" count six `\item`. Three pointers are wrong: **M-1**, and the two in
  **F-S8** below.

**823 rows are quantities.** The method codes (S / A / L / X / P) are those of
§4.1. Rows per family below include the 96 non-quantity rows that share a line
with a quantity. Families already verified in §3.2 or §4.1 are cited, not
re-derived. What was newly opened this session is named.

| family | lines | rows | how | detail |
|---|---|---:|---|---|
| F01 engine description | 114–166 | 23 | S | Pulse clone at `REL_4_3_2`: 20 ms (`About.md:22`); 0.02 s / 50 Hz (`SystemMethodology.md:117`); "5 to 10 times real time" (`FAQ.md:31`); nodes 0.0/0.3/0.6/0.9/1.0 on $[0, 1]$ (`RespiratoryMethodology.md:1176`); `git diff --shortstat REL_4_3_1 REL_4_3_2` = 7 files, +46, −17; FiO₂ = 1.0 accepted (withdrawn claim; 195 runs complete at 1.0, FiO₂ guard) |
| F02 limitations table, bound probes | 141–164 | 26 | S + A | SBP 120 / DBP 80 / pulse factor 0.75 (`SetupPatient.cpp:354–358`); 0.91 / 0.95 and 50–110 / 8–20 (preregistration); 5 compartments (§3.2); S030b probes (§4.1). **F-S9** on the 7 % |
| F03 limitations (v)–(vi) | 178–182 | 11 | L + A | seed 44, 4/160 → 7/160 (§4.1); 9 of 20 DBP and 8 of 20 SBP steps (`T5.clip.dbp_shortened`, `.oat_violations`); SBP rank 1 under six estimators (`T5.robust.*`). **M-1** |
| F04 hard bounds, drift thresholds | 194–270 | 67 | S + X + L | §4.1 hard-bound table; `DRIFT_MAX_DELTA_60S` = 5 / 5 / 50 / 0.02 / 15 / 5 (`src/detector.py:102–108`), row by row; 13 samples on [60, 120] s at 5 s; 0.02 = 2 points; 50 / 74.99 = 0.67 and 50 / 55.10 = 0.91 mL/kg IBW ("≈ 0.7–0.9"); 70 − 65 = 65 − 60 = 5 mmHg; CV 5 %, 64 reruns, 0.016 (`T1.06b`, `T1.04`) |
| F05 clamp patterns, FiO₂ adjustment, bodies | 284–294 | 21 | S + A + X | HR floor 50 and range [50, 110]; ambient CO₂ 4 × 10⁻⁴ = 1 − 0.9996, since the logged maximum is FiO₂ + N₂ + (1 − Σ fractions) (`MechanicalVentilatorModel.cpp:268–282`; Pulse HowTo files set CO₂ 4.0E-4); Agemos 214.5 = 17 y 10 m and 218.5 = 18 y 2 m; 17 % = 16.79 %. **F-S7** on L284 |
| F06 design constants | 302, 306, 409, 411, 957, 958, 1008 | 18 | S + X | 20 / 4 / 42 (§3.2); $7+1=8$, $20\times8=160$; the 8 per-cell `aggregated.parquet` files exist |
| F07 S032 clip | 312–334 | 58 | L + A | `T5.clip.*` (35, 9, 8, 123, 78 / 41, 68 / 19, 11, 90, 100, 2.4, 9 of 48, 48 of 48); per-cell retained 4, 4, 7, 6, 10, 9, 4, 5 in the printed cell order equals `CLIP_RETAINED_EXPECTED` (sum 49); 12 of 20 (`T5.robust.matched_trajectories`); table: §4.1 |
| F08 Sobol trigger | 341–347 | 25 | L + A | `T2.sobol.*` (72, 43, 23, 17, PEEP 8, RR 5, Vt 8); from `sobol_ci_buckets.csv`: sex split **12 F / 11 M**; Vt stable-set rows S2 3, S3 3, S4 2 (none in S1); **median top-three input 3 clean trajectories in S1 and 16 in S3** (`n_trajectories`, 36 rows per scenario, control: 144 top-three rows). This closes the note left open at supplement.tex:347 |
| F09 curation map | 351–392, 668, 752 | 43 | S + L + A | 10 / 30 % (preregistration L205); 7/29/12 and 7/3/38 (§3.2); 0/0/48 and 26 (`T1.tl.literal_four_red`, `T1.tl.yellow_to_red`); minimum 12 not-steady-state runs in S3_M (`cell_flag_summary.csv`); red cells: PaO₂ and HR 4 each (S3 and S4, both sexes), MAP, PaCO₂, SpO₂ and Vt 1 each (S4_M); 54 / 160 (8 diverged + 46 implausible, overlap 0) and 46 / 160; 918, 133, 3 (`T1.30n.*`); 130 = drift-exceeding Vt channels with CV > 0.05, re-counted (control 133). **"0 of 24"**: `baseline_robustness_check.py` re-run gives 0; that script has no positive control, so one was added in the scratchpad: the S1_M baseline reproduces all 48 published colours; ×1.25 baseline changes 11 (negative control) |
| F10 F-003 | 357 | 17 | A | §4.1 |
| F11 seed resampling | 400–404, 1133 | 14 | A | `phase4b_top3_comparison_seed44.csv`: rank 1 kept on 6 of 6; order changed on HR (ranks 2–3), PaO₂ (2↔3), Vt (rank 3), so "confined to ranks 2 and 3" holds; 4/160 → 7/160 (§4.1) |
| F12 NSS attribution table | 427–450 | 36 | L + X | the 48 printed cell values (8 rows × 6 columns) equal `nss_man_table` (`T2.nssC.*`), and the column order equals `col_map`; 76 = 530 − 454 = Σ(n_nss − excl. SpO₂) |
| F13 Berlin calibration S030 | 458–496 | 51 | A + L | §4.1; S030 config RR 16, FiO₂ 0.4, PEEP 10; "within 0.6 %" and "within 2 %" re-checked by the S030 guard against the March anchors at 1 dp; `BERLIN_PEEP_MIN = 5.0` (`pf_berlin_analysis.py:39`); Berlin PEEP ≥ 5 definition **(P)**, not re-read this session |
| F14 severity mapping, probes | 503–531 | 29 | S | §4.1; $[0, 1]$ in Pulse docs |
| F15 continuous severity | 535–566 | 73 | L + X | `check_continuous_severity_band` (21 checks, F-S5); Wilson 95 % for 1/2 = [0.0945, 0.9055] and for 0/2 = [0, 0.6576]; 20 events vs 0 of 640 (sex-divergence guard) |
| F16 Spearman | 576–608 | 23 | A | §4.1 |
| F17 ventilation dose | 616–618 | 12 | S + X | §4.1 |
| F18 Cornish | 628–663 | 59 | S | §4.1 (arXiv Tables 4–5 re-read this session) |
| F19 S014, S033 | 677–726 | 54 | L + A | `T1.04`, `T1.06d`; `paired_comparison.parquet`: S1_F_0117 1.825742 → 0.017750; 64 pairs over seven cells, S3_M none (S1 26, S2 19, S4 14, S3 5); S033 guard pins L715 (295 / 945 / 12 / 8, 98.4 %, 9 of 1,260, 533); rest §4.1. **F-S8** |
| F20 S021 | 736–781 | 82 | A + L | §4.1; 40/44 = 90.9 %; 663 − 643 = 20; **all 60 reruns byte-identical to their 120-s runs over t = 0–120 s**: the 120-s file is an exact byte prefix of the 300-s file (60 of 60; negative control with a different case: not a prefix). A first text-level comparison gave 0 of 60, because it excluded the last sample at t = 120.0000000000557 s; this was an instrument error, not a data finding. The 163 cm female 50th-percentile standard is also the male 3rd-percentile floor (`SetupPatient.cpp:68–75`). Known open item on L758 below |
| F21 blood volume, S018, sex parameters | 789–848 | 36 | S + A + X | §4.1 |
| F22 recommendations | 867–874 | 6 | S | band row 4; six items |
| F23 licences, hardware, compute, recipe | 882–948 | 31 | S + A + X | the machine running this session (an MSI GF63 Thin 11UC, assumed to be the canonical laptop that `CLAUDE.md` describes), queried read-only: i5-11400H with 6 cores / 12 threads, 8.28 GB, RTX 3050 Laptop 4 GB, 25H2; `DOCKER_MEMORY = "1g"`, `DOCKER_CPUS = "3"` (`src/runner.py:43–44`) and `reference/pulse_run_template.md`; ~14 h / ~9 h = 27.4 h ÷ 2 and ÷ 3 (§4.1); ~23 h = 23 h 01 m; 46 h (§4.1); 394/394 and 94/94 (head-line guard, sync map) |
| F24 reproductions | 954–976 | 19 | L + A | §4.1 |
| F25 SHAP, screen sensitivity | 984–1042 | 44 | L + A | `T2.s023.*`; clean runs per cell min 42 (S1_F) and max 144 (S3_M) (`cell_flag_summary.csv`); the S034 guard pins every number at L1038–1042, including seed 6/4/3 and screen 6/2/2 |
| F26 HR decoupling | 1054–1092 | 16 | A + X | §4.1; Morris HR grid 50/70/90/110; 74 ≈ 73.8; 155.7 − 80 = 75.7 and 147.1 − 80 = 67.1 ("≈ 70") |
| F27 window drift | 1105–1111 | 16 | L | `T5.window.*` (2.6 / 0.0 / 3.6 and 2.3 / 0.7 / 2.0); 5 bpm and 15 mmHg from `detector.py` |
| F28 summary table | 1131–1147 | 9 | L | repeats of verified figures |

#### Findings — nothing modified; all brought to the author

- **F-S7 — L284: a validation that did not exercise what it is cited for.** The
  sentence: *"Detector validation on twenty reference runs in the companion
  translation repository was 20 / 20 clean with the four-pattern set, which is
  the surface that survives the false-positive elimination from the original
  regex."* The monograph says the same at L1170–1172.
  - `scripts/validate_detector_on_existing_runs.py` calls
    `d.classify(csv, pulse_log="", …)`, unchanged since `19945f6`.
    `check_clamped` returns False on an empty log before any pattern is tried
    (`src/detector.py:280–281`). **The pattern set was never evaluated.**
  - Its output, `results/detector_validation_summary.csv`, has 20 rows, all
    `clean` and none `clamped`. Counted over all six channels:
    - 12 rows have no window statistic at all;
    - 7 report a CV of 0 on every channel that has a value;
    - only 1 (`f_s4_toddler_spontaneous`) carries non-zero statistics.
  - The runs are Paper 1 runs (neonate, infant, child and toddler scenarios,
    HR/RR boundary probes, smoke and output tests), not adult references.
  - A first draft of this entry said 11 and 8, read off the HR columns alone;
    it was re-counted before commit.
  - Our own log already says so. `experiments_log/santino/S005_pilot_S1_male.md`
    L75–79: *"The '20/20 clean' pass was a false positive on the entire window."*
  - **What did test the patterns**, re-read in the artefacts:
    - the two pilot clamp probes S1_M_9900 (SBP 140) and S1_M_9901 (DBP 85) are
      `clamped = True`, exit 1, with the rejection text in `pulse.log`;
    - the 8 `scenario_smoke` runs, with non-empty logs of 25–177 kB, are all
      `clamped = False`;
    - the replay over all Pulse logs reported at L286.
  - **Options:** (A) delete the sentence in both artefacts; (B) replace it with
    the probe and smoke evidence above.
  - ✅ **Corrected on the author's decision, 2026-09-14** (option B).
    - **Re-verified before editing with a second instrument.** The four patterns
      as they stood at `708efb1^` were replayed over the logs themselves: they
      fire on S1_M_9900 and S1_M_9901, and on none of the 8 `scenario_smoke`
      logs. Both probes are recorded in S005 (pilot) and the smoke set in S004.
    - **Supplement L284:** *"On the calibration runs, the four-pattern set fired
      on both deliberate-clamp probes of the pilot (SBP = 140 and DBP = 85 mmHg,
      each rejected at setup with exit code 1) and on none of the eight
      smoke-test runs; its behaviour on every Pulse log on disk is replayed in
      the note below."*
    - **Monograph:** the same sentence, linked to [S005] and [S004].
- **F-S8 — L681 and L726: a tie, and two pointers.**
  - **The tie.** *"Its effect on the single worst-affected configuration
    (S1_F_0117 …) is to take the delivered Vt CV from 1.826 to 0.018."*
    S1_F_0117 and S1_F_0118 share the maximum pre-lock CV exactly,
    1.825741858351 (= √(10/3)). Locked, they reach 0.0178 and 0.0242. S1_F_0117
    is unique only as the **largest reduction** (1.808 against 1.802).
  - `T1.05` pins only the maximum value, which the tie does not affect. The
    anchors `T1.s014.worstcase_*` take the `idxmax` row, so the tie is broken by
    parquet row order, while the label says "largest before/after delta".
  - The same pairing, "worst-case 1.826 → 0.018", appears in the monograph ×5
    (L55, L135, L332, L2981, L3644) and the README (L176).
  - **L726 pointer.** *"The worst-affected configuration, named in
    Section 2.3 … of the main manuscript"*. `paper.tex` §2.3 names no
    configuration; its L280 points back to Supplement §S8.
  - **L681 pointer.** *"most reruns occurring in the healthy (S1) and mild-ARDS
    (S2) cells (Table 1 of the main manuscript)"*. Table 1 is the terms table,
    and no paper table gives the rerun distribution. This is the half of
    `supplement_prose_sweep.md` signal #5 that is still open.
  - **Options:** name the criterion ("the configuration with the largest
    reduction; S1_F_0118 shares its pre-lock value and falls to 0.024"), or
    drop "single"; and repoint both references.
  - ✅ **Corrected on the author's decision, 2026-09-14** ("name both").
    - **Re-verified before editing.** The window of both tied runs, read in
      `output.csv`, holds 3 non-zero Vt samples and 10 zero respiratory-rate
      samples out of 13, so the population CV is exactly √(10/3). Their locked
      reruns hold Vt 818.6–873.6 and 818.6–893.4 mL. Both configurations are
      S1_F with Vt 800, RR 20, PEEP 13.3, differing only in FiO₂ (0.21 against
      0.737).
    - **Supplement L681:** *"(26 and 19 of the 64)"* replaces the Table 1
      pointer. *"Two configurations share the highest pre-lock delivered Vt
      coefficient of variation, 1.826 (S1_F_0117 and S1_F_0118 …); the lock
      takes them to 0.018 and 0.024."*
    - **Supplement L726:** *"The two worst-affected configurations, named
      earlier in this section and forming the two rightmost points of
      Figure 4a …"*. "Rightmost" was written instead of the proposed
      "extreme": on Figure 4a's other axis the extreme is S1_F_0008 (locked CV
      0.112), so "extreme" was ambiguous.
    - **Paper L280:** "the worst-affected configuration" becomes "the two
      worst-affected configurations", so the pointer still matches its target.
    - **Left as they are, as the author chose:** the monograph ×5 and README
      "worst-case 1.826 → 0.018". They are true of one of the two runs.
    - ⚠️ **For the author, not written anywhere:** both tied runs reach a CV of
      1.826 because ventilation stops in the window, not because tidal volume
      oscillates. `make_supp_fig_s4.py` already says so of S1_F_0117; this
      reading confirms it for both. The headline "worst-case" is therefore a
      different failure mode from the dyssynchrony it illustrates.
- **F-S9 — L155: "approximately 7 % above literature values per Pulse's own
  validation table".** Both Pulse pages were scraped 2026-09-14.
  - The 7 % is in Pulse's **methodology prose**, not a validation table:
    "VC = 4.93 L … Typical values of VC reported in the literature are around
    4.6 L". 4.93 / 4.6 = +7.2 %.
  - Pulse's patient **validation tables** compare the engine with its own
    computed expectation, VC error ≈ 0 %. They list StandardMale VC 4,819.2 mL
    and TLC 6,024 mL, against the prose's TLC 6.16 L. That gives **+4.8 %**
    against 4.6 L.
  - Supplement only; not in the paper, the monograph, the README or the
    preregistration. It is a citation-attribution mismatch, so nothing was
    modified. (`CLAUDE.md` limitation #10 carries the same attribution.)
  - ✅ **Corrected on the author's decision, 2026-09-14** ("attribute and give
    both values").
    - **Re-verified:** the prose "VC=4.93 L … around 4.6 L" is also in the
      local clone at `REL_4_3_2` (`RespiratoryMethodology.md:655`), so it is not
      web-only. 4.93 / 4.6 = +7.17 % and 4,819.2 / 4,600 = +4.77 %.
    - **L155** now reads: *"Pulse's respiratory methodology reports a
      standard-patient vital capacity of 4.93 L against a literature value of
      about 4.6 L (about 7 % higher); its current patient validation table lists
      4,819 mL for the standard male (about 5 % higher)."*
    - **Not changed:** `CLAUDE.md` limitation #10. It is a project instruction
      file, outside this audit's write scope, and it still says "Pulse's own
      validation table".
- **M-1 — L178, a mechanical pointer.** *"the FiO₂ rows of Figure 2 of the main
  manuscript are left blank"*. The blank FiO₂ entries are in the Morris heatmaps,
  Figure 3 (`paper.tex:331` uses `\ref{fig:morris}`). The sentence entered in
  `d88a1ca`, when the numbering was already this one. The monograph's own
  Figure 2 is its Morris figure, which is the likely source of the slip.
  - Ready: "Figure~2" → "Figure~3".
  - Held back only so that it goes in the same supplement edit and rebuild as
    F-S7 and F-S8. The alternative, a separate commit now, was rejected because
    it costs a second rebuild and the push needs a go either way.
  - ✅ **Applied 2026-09-14** with the three findings above.

**Two items already recorded in `audit/supplement_prose_sweep.md`**, re-measured
here:
- **#15, L758, still open.** *"within approximately 5 % of the asymptote"*,
  where "asymptote" is the last observed value at t = 300 s (`audit_claims.py`
  comment). Re-measured on the 37 physiological-converged runs, the earlier
  record having used 38:
  - ~~the median trajectory's [240, 300] s mean is 0.09 % from it; per run,
    the median is 0.12 % and the maximum 1.48 %~~ — **wrong: that script's
    `time_s >= 240` dropped the t = 240 s sample (239.99999…)**. That is the same
    defect the S021 window fix of 2026-09-01 removed.
  - With the atlas window slack of 1e-6, 13 samples per run: **median
    trajectory 0.105 %; per run, median 0.130 % and maximum 1.565 %.**
  - The claim is true but loose: about 50 times the median trajectory's
    deviation, and about 3 times the worst single run's.
  - The wording put to the author ("within 0.1 % … within 1.5 %") was drafted on
    the wrong figures and **would have been false**. The error was caught by the
    pre-edit re-verification, before anything was written.
  - ✅ **Corrected on the author's decision, 2026-09-14** ("measured figures"),
    with the corrected figures. **L758** now reads: *"puts the PaO₂ estimate
    within about 0.1 % of the value reached at t = 300 s on the median trajectory
    of those runs, and within 1.6 % for any one of them."* "Asymptote" is gone:
    the reference is the last recorded value.
- **#7, L464, closed by F-S1.** The sentence now says "March anchors", and the
  S030 guard compares against those at 1 dp (worst 0.52 %).

**Tooling notes.** Guard or script code, so not changed without review:
- `validate_detector_on_existing_runs.py` passes an empty log (F-S7);
- `baseline_robustness_check.py` has no positive control;
- the S014 worst-case anchors break a tie by row order (F-S8);
- `supplement_prose_sweep.md` still lists #11, #21 and #27 as OPEN, although
  the current text no longer carries those defects ("seven of the eight",
  "160-point Morris design", "four-level Morris grid").
- `make_supp_fig_s4.py`'s docstring still says the worst case is "the extreme
  dot in paper Figure 3a" and that "Section 2.3 still quotes it by name". Both
  are stale. It is left unchanged, because editing the producer would disturb
  the figure-freshness check for no rendered change.
- **The crosswalk counts by literal substring.** `0 / 20` had been counting the
  "20 / 20" of the removed F-S7 sentence. Two entries go 9 → 8 and T1.13
  (`1.6~\%`) goes 1 → 2, a coincidence with the #15 wording. Each entry carries
  a dated note.

**Guard.** `check_supplement_small_audit` in `scripts/audit_claims.py`, wired
into the exit status, 22 checks:
- it re-derives the pilot probes, the smoke set, the S014 tie with both locked
  values, the rerun split, and the two vital-capacity percentages;
- for #15, it re-derives the median and per-run deviations from the S021
  traces, and skips cleanly when those gitignored traces are absent;
- it requires the nine corrected wordings and bans the eleven old ones.

**Reinjection.** The old sentences were written back into supplement, paper and
monograph at once:
- the guard failed **8** checks and the audit exited 1;
- all three files were restored and their MD5 checked identical.

A first `sed`-based reinjection silently failed to apply one of its three
substitutions (a `\%` escape); it was redone with a literal-replacement
script that aborts unless each target occurs exactly once.

**Bucket movement caused by these corrections** (multiset diff of
`inventory.csv` against `921a8b6`):
- **Supplement:** 1,876 → 1,887 retained.
  - New: `4.93`, `4{,}819`, `118`, `300`, `140` (guard); `4.6`, `0.024`, `0.1`
    (none); `26`, `19`, `64`, `85`, `1.6`, `3` (ambiguous_small).
  - Gone: `20` ×2, `2` (ambiguous_small).
  - The rows `1` (exit code for Table 1) and `5` (L155 for L758) swap one for
    one.
  - Every new value is one verified above.
- **Monograph:** `20` ×3 gone; `140`, `85` and `1` new.
- **Guard pinning.** The guard pins the string "140", so every other
  occurrence of 140 moved from `none` to `guard` by value: supplement 2,
  monograph 4. This is the §2 by-value limit again, as in F-S5.
- **Masks.** Supplement masks 86 → 85: the only removed mask is
  `\mainref{sec:results-vcac}{2.3}` (diff of `masked_by_rule.csv`).
- **Rebuilt:** paper 25 p., supplement 63 p., monograph; PDF and DOCX.
  - New wording found and old wording absent in the rendered PDFs.
  - The only remaining "own validation table" hit is row 7's "tables" (PC-AC),
    verified in §4.1.
  - `\_` extracts as a space, so "S1 F 0118" is the rendered form.
- **A render regression, caught by the pre-commit hook, which refused the first
  commit.** The longer row 10 (F-S9) grew Table S1's accepted overflow from
  31.26 pt to 53.26 pt.
  - The alternatives were rejected: accepting 53 pt would hide a real
    degradation, and shortening row 10 would drop values the author chose.
  - Fix: a local `\footnotesize` on `tab:limits`, as on 2026-08-25. The overflow
    is gone.
  - The table's overfull hbox moved from 19.31 to 17.39 pt. Measured before the
    baseline entry was replaced: its rules stay inside the caption's full text
    width, as they did at HEAD (rebuilt in a clean worktree). The page was also
    read as an image.
  - `scripts/check_render.py` `KNOWN_RESIDUES` is amended with that judgement
    written beside it, per its own amendment rule.
  - The table already floated far from Section S2 at HEAD (p. 51); it is now on
    p. 48, still 63 pages.

**Not covered.** The supplement's by-value `guard` / `ledger` occurrences.

## 5. The monograph's residue, read row by row — 803 + 1,864 occurrences and 89 inline-code literals (2026-09-14)

**Populations.** `inventory.csv`, `artefact = monograph`:
- `none`: 803 rows over 537 source lines;
- `ambiguous_small`: 1,864 rows over 1,086 lines;
- inline code: the 89 literals that `masked_by_rule.csv` removes under
  `md_inline_code`, read apart on the author's decision (§2.1).

`manuscript.md` is unchanged since `828ef84`. The inventory was re-run before
counting and produced no diff. Every row was read with its context. Hand
searches tested both `1,280` and `1{,}280`, since the monograph is Markdown.

**Line coverage is mechanical.** A read-only scratchpad script attributes every
row to exactly one `##` / `###` section, rows before the first heading going to
the front matter. The per-section totals add back to the population: 803 rows
over 53 sections, 1,864 over 56.

| part of the monograph | lines holding rows | `none` | `ambiguous_small` |
|---|---|---:|---:|
| front matter, abstract, key findings, roadmap, contributions, notation | 3–419 | 47 | 245 |
| §1 introduction | 426–674 | 28 | 59 |
| §2 methods | 678–1550 | 161 | 313 |
| §3 results | 1555–3030 | 288 | 649 |
| §4 discussion | 3039–3618 | 65 | 190 |
| §5–§9 conclusion, data, acknowledgements, AI, references | 3623–4221 | 133 | 228 |
| appendices A–C | 4239–4656 | 81 | 180 |
| **total** | | **803** | **1,864** |

**Quantities against non-quantities: not counted, and why.** In §3.2 and §4.2
the non-quantities were counted by hand, as a multiset. Here a rule-based first
pass split them: 192 non-quantities in `none`, 513 in `ambiguous_small`. A
precision pass then printed every row the rules had called a non-quantity. The
rules were wrong in both directions:
- all 7 `none` rows filed as list numbers are quantities that end a sentence
  ("… below 0.05. Use", "… as 3.397. The");
- "95th percentile" and "CDC 50th-percentile" were filed as editions;
- "5 · 0.05 / 24" and "5 of 24 cells" were filed as journal issue numbers.

The quantity side was not re-read for the opposite error. So no split is
reported. What this section claims rests on every row having been read, not on
a count of quantities.

The non-quantities met are:
- heading and section numbers;
- bibliographic volume, issue, page, PMID, ISBN, chapter and edition numbers;
- dates;
- author and affiliation markers;
- F-003 / F-004;
- figure, table, Paper, Tier, Phase, quadrant and item numbers, and list
  numbers;
- names: Apache-2.0, CC-BY-4.0, PALICC-2, COVID-19, Sepsis-3, IEEE-754,
  ASL 5000, ANR-23-IACL-0004, Gemini Pro 3.1, 1-Wasserstein, 2-D;
- notation: R², powers of ten, "0-dimensional".

They were checked anyway, because a wrong pointer or date misleads just as a
wrong number does:
- **Section pointers.** All 180 internal `§` and "Appendix" pointers were
  listed, each with the words announcing it and the heading it lands on. All
  resolve, and each was read against its target. **Four are wrong: MF-16,
  MF-17.**
  - The pointers into other documents hold. Paper §2.1 carries the FiO₂ 0.9996
    cap (`paper.tex:173`). Paper Methods §4.5 carries the post hoc traffic-light
    declaration (`paper.tex:373`). Supplement §S3.3 carries the same cap
    (`supplement.tex:288`).
  - The supplement pointers §S3.4, §S3.7, §S3.11, §S3.12, §S12 and §S13 land on
    the sections they name.
  - Two further pointers are wrong: **MF-19** and **O-11**.
- **"Cited in §X" in the reference entries.** Each claim was checked by locating
  the key's `[@key]` occurrences by section. Control: `figueroacasas2016`, found
  in monograph §3.8 and §4.1. The nine keyed claims hold. The SA-tag entry has no key and
  was read against §1.1 L495–496.
- **Reference metadata.** All 34 entries' volume, issue, page, PMID, ISBN and
  year tokens are present in both `references.bib` and `paper.bib`. The
  comparison script caught two errors injected as a positive control (179,
  22797453). **O-6** records what a token comparison cannot see.
- **Dates.**
  - The Pulse clone gives the `STUDY_SENSITIVITY_ANALYSIS_1_0_0` tag as
    2020-07-20 and its last functional commit, `4fafaf715`, as 2020-08-24.
  - The arXiv v4 page says "revised 2 Nov 2023".
  - `REL_4_3_2` is dated 2025-08-12 (§4.2).
  - The AI-tool dates in monograph §7 and §8 are the author's record and were
    **not** verified.
- **Other numbered pointers.**
  - "preregistration.md §Analysis plan item 7" is preregistration L205 (§4.2).
  - "Validation Tables 3 / 5 / 10 / 12 / 17 / 19" are the VC-AC and PC-AC tables
    of Pulse's ventilator page.
  - "Cornish Appendix Tables 4 and 5" hold in arXiv v4, arXiv v5 and the JMLR
    version.
  - "entry 6" is the numbered reference list's Webb 2022.
  - "items 1–6" are the six recommendations of monograph §4.7.

**Sources, by part.** Codes as in §4.1: S source, A artefact, L ledger or guard,
X arithmetic, P companion or secondary record. The table names what was opened
in this pass. A quantity not named here repeats one verified in §3.2, §4.1 or
§4.2, or a guard / ledger value.

| part | how | opened this pass |
|---|---|---|
| front matter to notation | A + L + X + S | `sobol_ci_buckets.csv`, dominant input (rank 1): 40 of 48 point estimates below 0.6, 31 CI-robustly linear, 1 CI-robustly non-linear, 5 without a CI (**MF-3**). S014 `paired_comparison.parquet`: median CV 0.35087 → 0.01563, a 95.5 % reduction printed as "96 %"; 78.1 % of locked reruns below 0.05. S021 `plateau_stats.parquet`: the three converged runaways plateau at 1,408.1 / 1,408.1 / 1,402.5 mmHg. 37 / 44 = 84.1 %. FiO₂ = 1.0 in 13 of 20 divergences against a 208 / 1,280 base rate, 4.0 times. HR 50, SBP 90 and RR 20 hold in 32 runs, and all 16 male ones diverged. 4,082.24 − 3,996.09 = 86 mL. S023 mean overlap 2.3958. Webb 2020 340 / 130 / 50 mmHg (PMC7688119, full text re-read). L6 1.35 is `\arraystretch`. **O-8** |
| §1 introduction | S + A + L | Pulse ventilator tables as re-scraped in §4.1: 0.07–2.25 % and 11.3–25.3 %, engine against expected 935.217 / 1,047, 409.439 / 528 and 490.087 / 571 mL. Companion log L870, L1025, L1558: PC-AC 594.5 mL (+24.0 %) and 635.3 mL (+58.9 %) against VC-AC **(P)**. Age 18 and HR 110 (§4.1); S005 22-run pilot, five gates; 394 / 394 and 393 / 394 (head-line guard); §1.4 table, 24 rows (**O-9**); the §1.2 pointers (**MF-16**) |
| §2 methods | S + A + L + X | Input ranges 0.21 and 110 (preregistration; `check_input_ranges.py`, §2). The S032 clip values and the stratified table, as in supplement S3.7 (§4.1, `T5.clip.*`, `T5.strat.*`). S034 318 / 318 (guard). Median −10.4 % in 8 of 8 cells: `T5.robust.mu_drop_median_pct`, and all eight `delta_pct` in `results/s032/sbp_map_dominance.csv` are negative, median (−10.80 − 10.01) / 2. 202 = 220 − 18. SpO₂ 0.40 ↔ PaO₂ 22.98. `FLOAT_EPS` 1e-9. Phase 4a `sha_compare.json`: 1,260 `BIT_EXACT`, 20 `BOTH_DIVERGED` with exit code 1 on both sides, 0 in the four other counters (**O-10**). Phase 4b seed 44: 1 h 34 m 14 s; 7 divergences, all HR 50 and SBP 90 (**MF-9**). S015 40 / 40 = 38 bit-exact + 2 diverged. S006 went from 3 to 2 workers mid-sweep. Hardware queried read-only (**MF-4**). **MF-5, MF-7, MF-15** |
| §3 results | A + L + X + S | Table 1 = `cell_flag_summary.csv`. `morris_indices.parquet`: HR←HR μ* 55.3–55.8, rising to 94.0 / 95.1; MAP←SBP 17.2–20.2; SpO₂ maximum 0.1247; PaO₂←FiO₂ S2 133.1 / 146.7, S3 84.5 / 93.2, S4_M 30.7; Vt←Vt 488.6–503.1; top-three summed μ* via `src.analysis_morris`. σ / μ*: 0.0037 / 0.0068; 0.028 / 0.023 (σ = 0.02348); ratios 0.637–0.942, 0.873, 0.655. Divergence input pattern (`aggregated.parquet`). The 24-row Wasserstein table (`wasserstein_male_vs_female.csv`, half-up rounding). Clean HR means in S3 / S4 146.5–157.9 against 76.08. Greens S2_F ×4 + S3_F ×3; 471 + 20 + 126 = 617. "Nine of the sixteen" = 4 ties at 1 dp + 5 at 2 dp (rationale of `baad15f`). S012: Vt 17 / 195 = 8.72 %, median 0.087; PaO₂ 38 / 195 = 19.49 %, median 4.31, p95 40.18; 93.3 % positive slope; intersection 33. S014: median delta +0.326, 8.1 times 0.04; the 64 pairs are the top 64 by Vt CV. 303 − 264 = 39. S018 S4_M clean at both BV levels. **MF-2, MF-12, O-1, O-2, O-4, O-7**; prose-sweep #38 at L2316 |
| §4 discussion | S + A + P | Cornish Table 2 against arXiv v4 Tables 4–5: 80 / 85 and 240 / 281 on the seven non-cardiorespiratory channels. Companion E4: 74 runs, elasticity 1.32 → 0.26. S012 arm drift rates (**MF-11**). **MF-18, MF-19** |
| §5–§9 | A + S | tree and file sizes (**MF-13, O-5**); the 34 reference entries against both `.bib` (see above); Pulse validation tables; **O-6** |
| appendices | S + A + P + X | Pulse clone at `REL_4_3_2`: `SetupPatient.cpp:771` 13.397 and `:752` 0.425; ν = 4 × `ResponseSlope` 12 = 48 (`NervousModel.cpp:320`, `PulseConfiguration.cpp:596`); BMI below 16 or above 30 is an Error; heights 163–190. Pulse web methodology: BMR "3.397", exponent 0.45, "ν to 4". Pulse scenarios 0.3 → 0.6 → 0.9, 0.6 and 0.8. Companion March sweep 9 + 11 + 8 = 28. FiO₂ probe, 9 runs, ≈ 7.8 mmHg per 0.01. 0.756 = 68 / 90. CDC `statage.csv` (**MF-6**). Appendix C table = `nss_decomposition.csv` (**MF-1, MF-14**). **O-3** |

**The 89 inline-code literals.** 21 are not quantities: `kitware/pulse:4.3.1`
×4, seven `file:line` references and ten `claude-opus-*` tokens. The 68
quantities all hold, apart from one stale pointer:
- `heightStandardMale_cm = 177.0` (`SetupPatient.cpp` L72) and
  `heightStandardFemale_cm = 163.0` (L75);
- `exit_code = 1`;
- the Morris calls, seeds, trajectories and levels (`sampler.py` L99–101; S009
  seed 43 with 10 trajectories; Phase 4b seed 44);
- `CV_THRESHOLD = 0.05`, `ddof=0`, the window 60–120 s, `std/|mean| < 0.01`,
  `0.02`;
- the FiO₂ messages 1.0 and 0.9996;
- `65.6 × weight^1.02` (`computedBloodVolume_mL`, `SetupPatient.cpp:534`);
- `[0.879, 0.946]` (guard), `[0.91, 0.945]` and `[0.91, 0.946]`;
- `5 · 0.05 / 24 ≈ 0.0104`;
- `HARD_BOUNDS_PHYSIOLOGICAL` PaO₂ (20, 700);
- −2 cmH₂O;
- 13.397, 0.425 and `4 × ResponseSlope`.

The code pointers `RespiratoryModel.cpp:3774`, `:4388` and `:4503`,
`SetupPatient.cpp:771` and `:752`, and `NervousModel.cpp:320` land on the named
code. `src/detector.py:338` does not (**MF-15**).

#### Findings — all brought to the author; nothing was modified while they were recorded

L-numbers and section numbers in a finding refer to `manuscript.md` **as it was
read, before the corrections**; the corrections shifted later lines by up to 11.
§4.1 and §4.2 with an F-S identifier refer to this register. What was done with
each finding, and the current line numbers, are in "Resolution" at the end of
this section. MF-22 was found during that resolution and was then corrected
too, on the author's decision.

MF-1 to MF-15 were each re-derived a second time before being written here.
Where the second derivation used a different instrument, it is named in the
entry; otherwise it was a second read of the same source. The later findings
came from three other checks:
- MF-16, MF-17 and MF-19 from this pass's pointer check;
- MF-18 from reading §4.4's ledger-pinned numbers against Table 2;
- MF-20 and MF-21 from measuring the elementary effects behind O-2 while
  drafting the options for the author.

Each was confirmed in git history, in a second file, or by a control that
reproduces a published value.

Numbering is kept from the working notes: MF-8 was the second locus of MF-4 and
is merged into it; MF-10 was downgraded to O-7 by its second reading.

- **MF-1 — L4643, Appendix C.** *"Dominated by S4 (104 / 185 of the
  residual)"*. The `excl. both` column gives S4 39 + 52 = **91**, S1 53, S2 30
  and S3 11, total 185. S1's "53 / 185" in the same sentence is right. Second
  instrument: the monograph's own Appendix C LaTeX table, parsed and checked
  equal to `nss_decomposition.csv`. The parse first matched Table 1 as well; its
  row-count control (16 against 8) caught that before any number was read.
- **MF-2 — L4309 and L2768–2769.** *"over the full FiO₂ ∈ [0.21, 1.0] range"*
  and *"multi-input averaged across [0.21, 1.0]"*.
  - The clean S1 runs sit at only two FiO₂ levels: 0.21 (47) and 0.4733 (44). L2761
    says "[0.21, 0.47]" itself.
  - Fit: slope 505.45, intercept −25.07, R² 0.902.
  - Minor: L2771 "≈ 481 at FiO₂ = 1.0" against 480.4 from the fit and "≈480"
    at `supplement.tex:781`. 481 is 228 + 0.5 × 505.5, from the rounded 228.
  - Second instrument: `scipy.stats.linregress` instead of `polyfit`.
- **MF-3 — L61–62, abstract.** *"the remaining 17 cells have either bootstrap
  CI straddling 0.6 (12) or insufficient clean trajectories for a CI (5;
  FiO2-edge cells in S1 and S4_F)"*. Two defects:
  - **The 12.** It is 11 straddling cells plus the 1 CI-robustly non-linear
    cell, (S3, M, PaO₂, FiO₂). The monograph's own note (L1852–1853 and L1877–1879)
    says a "straddling count of twelve" was wrong and gives 31 / 1.
  - **The 5.** They are S1_F × {PaCO₂, PaO₂, Vt}, where the dominant input is
    Vt, and S4_M × {PaO₂, SpO₂}, where it is FiO₂. They are neither "FiO₂-edge
    cells in S1" nor in S4_F, as L1858–1862 itself says. The wording matches the
    Spearman gap of L3370 (S1 and S4_F), a different statistic.
  - The second defect was found by the second instrument, a direct read of
    `linear_all_seeds`, `nonlinear_all_seeds` and `no_estimable_ci` on the 48
    rank-1 rows, with no overlap between the three.
  - Monograph only.
- **MF-4 — L1299 and L1307.** *"8 GB RAM, no GPU"*. The machine carries Intel
  UHD Graphics and an NVIDIA RTX 3050 Laptop GPU with 4 GB. Neither is used,
  which is how `supplement.tex:886` puts it. Second instrument:
  `Win32_VideoController` queried again, read-only, alongside
  `TotalPhysicalMemory` 8,277,110,784 and the i5-11400H.
- **MF-5 — L1051–1054.** *"NHANES P50 anchors … median HR 70 / 74, SBP
  118 / 113, DBP 70 / 69"*.
  - The companion's `lookup_tables_literature_validation.md` attributes HR
    70 / 74 to NHANES (Ostchega 2011). It attributes SBP 118 / DBP 70 (M) and
    113 / 69 (F) to the AAP 2017 age-17 tables at the 50th height percentile
    (L196, L405, L524, L526).
  - **(P):** read through the companion's record. Ostchega 2011 was not opened.
  - Monograph only, and uncited: no reference entry names NHANES, Ostchega or
    Flynn / AAP 2017.
  - ⚠️ **Primary source opened after the first commit of this entry.**
    - AAP 2017 (Flynn et al., *Pediatrics* 140(3):e20171904) is not in PMC.
      Its publisher page was scraped with Firecrawl on 2026-09-14
      (`.firecrawl/aap2017_flynn_2026-09-14.md`). Each table appears twice on
      the page, with identical rows.
    - Table 4, boys aged 17, 50th BP percentile, by height percentile 5–95 %:
      SBP 114 / 115 / 116 / **117** / 117 / 118 / 118 and DBP 65 / 66 / 67 /
      **68** / 69 / 70 / 70. At the 50th height percentile (175.8 cm) that is
      **117 / 68**; 118 / 70 appears only at the 90th–95th height percentiles.
    - Table 5, girls aged 17: SBP 107 / 108 / 109 / **110** / 110 / 110 / 111 and
      DBP 64 / 64 / 65 / **66** / 66 / 66 / 67. At the 50th height percentile
      (163.0 cm) that is **110 / 66**. The female **113 / 69** matches no
      height-percentile column of the 50th-BP-percentile row.
    - The companion also cites a Singapore screening study (PMC12331881, males
      only) as cross-validation; it was not opened.
    - So the BP half is neither NHANES, as the monograph says, nor the AAP 2017
      cell the companion names. The discrepancy lies in `Pulse_translation_new`,
      which is read-only for this repository.
    - Not cross-checked against the guideline PDF.
- **MF-6 — L4531, B.5.** *"CDC P50 ≈ 177 cm"* for male stature at 18 years.
  CDC `statage.csv` (Firecrawl, 2026-09-14) gives P50 176.13 at Agemos 215.5
  and 176.19 at 216.5. L722 and L1045 say 176.2, which is right. 177 is Pulse's
  `heightStandardMale_cm`, quoted in the next line.
- **MF-7 — L1300, L1312, L1316, L1323.** *"eleven independent verification
  points (Pulse determinism, …) detailed in Supplementary S10"*.
  - The linked `preprint/supplementary.md` S10 table has **12** rows: S005 G5,
    S006 V1–V8 and S007 1–3.
  - S007's "eleven" counts 8 + 3 and does not include S005 G5. The monograph's
    parenthetical names "Pulse determinism", which is S005 G5.
  - Two readings: eleven without G5, or twelve with it. The parenthetical makes
    the first inconsistent.
  - `supplementary.md` is outside this register's population.
- **MF-9 — L1351.** Phase 4b *"was run on the moderate-ARDS male cell"*, while
  the same paragraph names cell (S2, M). S2 is mild ARDS, 0.26
  (`src/scenario.py:59`). The directory is `phase4b_seed44_S2M`.
- **MF-11 — L3383, §4.5.** *"HR, MAP, and PaCO2 drift rates stay below 3 % in
  both vulnerable populations"*.
  - Hyperoxia arm: PaCO₂ 7 / 195 = **3.59 %**. L3009 says 3.6 % itself.
  - The other rates: hyperoxia HR 2.56 %, MAP 0; Vt arm HR 2.31 %, MAP 0.66 %,
    PaCO₂ 1.98 %; intersection HR 3.03 %.
  - L3024 "below 4 %" is right. The paper was corrected for exactly this upper
    bound (`T5.window` comment).
  - Second instrument: thresholds imported from `src.detector`, not parsed by
    regex.
- **MF-12 — L2942.** *"the worst-CV run S1_F_0008"* in the full-sweep F-004
  paragraph.
  - Before the lock S1_F_0008 has CV 0.759, **rank 6**. The worst are S1_F_0117
    and S1_F_0118, tied at 1.826 (§4.2 F-S8). S1_F_0008 is the worst **after**
    the lock (0.112).
  - Compliance 0.090003 with a half-range of 1.3 × 10⁻⁶ fits the stated
    ± 5 × 10⁻⁶ on the 5-s CSV. RR 20 → 46.9 fits "~46 bpm".
- **MF-13 — L3674.** *"1,280 raw CSVs plus ~50 MB of engine logs"*.
  - The 1,280 full-sweep `pulse.log` files total **105.1 MB** (100.2 MiB). All
    1,280 carry a modification date of 2026-04-26.
  - The sentence entered in `6eeced5` on 2026-08-17, so it was wrong when
    written; this is not a staleness defect.
  - Second instrument: `os.walk`, with the 1,280 `config.json` as control.
- **MF-14 — L4627, Appendix C.** *"Concentrated in S1/S2 (74 / 76 of those
  runs; 30 in S1_F, 16 in S1_M, 16 in S2_F, 9 in S2_M, plus 5 trickle in S3)"*.
  The four values it lists sum to **71**. S3 1 + 4 = 5 and the total of 76 are
  right. Second instrument: the Appendix C table (locked − excl. SpO₂ per cell).
- **MF-15 — L1449.** *"`src/detector.py:338`"* for the `std(ddof=0)` line. It is
  at L413 now, and L338 is `lo, hi = HARD_BOUNDS[name]`. At `4771e9b`, L338 was
  the std line. The method described is right.
- **MF-16 — L599, L1864, L2515: three pointers to "§4.3" for limitations.**
  Limitations is §4.5; §4.3 is the machine-learning implications section.
  - At `be4c671` (2026-05-08) §4.3 *was* "Limitations". By `4a1a0bc`
    (2026-05-13), the commit that added §4.4, Limitations had become §4.5.
  - L1864 has "§4.3 / §4.5 limitations", only half stale.
  - Mechanical.
- **MF-17 — L415, notation table.** *"BV = 65.6 · weight^1.02 (§3.6)"*. The
  formula is at L2098 and L2111, in §3.5. §3.6 does not mention blood volume.
  Mechanical.
- **MF-18 — L3348, §4.4 quadrant 2.** *"Cornish, with PaCO2 as the only flagged
  channel (3 / 70 Hoeffding, 13 / 70 bootstrap)"*.
  - The monograph's own Table 2 (L3250–3256) gives non-zero bootstrap rejections
    on three more direct-overlap channels: PaO₂ 4 / 78, MeanBP 3 / 92 and
    HR 1 / 162. `supplement.tex:668` ranks exactly those four channels.
  - The claim holds only for Hoeffding, and only among the four overlap
    channels: SysBP carries 2 / 154 Hoeffding rejections.
  - Entered in `4a1a0bc`. Found while reading §4.4's numbers, which are
    ledger-pinned; the sentence itself carries no residue number.
  - Monograph only.
- **MF-19 — L3581, §4.7.** *"documented in our preregistration limitations
  table (entry #4)"*.
  - No version of `preregistration.md` has ever contained the word
    "limitation"; every commit touching the file was searched.
  - The twelve-row limitations table, with the instability zone at entry 4, is
    monograph §1.2 and Supplement S2.
  - The preregistration does document the zone, in its scenario table (L112,
    row S4, "E6 + E10") and in H3 (L76).
  - Entered in `93e87b8`, 2026-05-23.
- **MF-20 — L1818–1826, §3.3.1 "Group A — noise-dominated".** *"μ\* sits at
  numerical-noise level because the output is pinned at physiological
  saturation … SpO2 … sits at ≈ 0.997 … so the Morris elementary effects are
  floating-point fluctuation"*, for (S1, F, SpO₂, PEEP) and (S1, M, SpO₂, Vt).
  Found while turning O-2 into an option; O-2 is folded in here.
  - Measured from the clean elementary-effect pairs, rebuilt with
    `s032_uncontaminated_step_analysis.load_inputs` / `annotate_pairs`.
    Control: the mean |EE| reproduces the published μ\* 0.028086 and 0.003702.
  - **(S1, M, SpO₂, Vt), 3 pairs.** At FiO₂ 0.4733, 0.99664 → 0.99852 (EE
    +0.0028). At FiO₂ 0.21, **0.96232 → 0.92950 (EE +0.0492)** and **0.96358 →
    0.98505 (EE +0.0322)**.
  - **(S1, F, SpO₂, PEEP), 4 pairs.** At FiO₂ 0.4733, changes of −3.6 × 10⁻⁴ and
    −6.1 × 10⁻⁵. At FiO₂ 0.21, −3.9 × 10⁻⁴ and **0.95373 → 0.96279 (EE
    +0.0136)**.
  - So no pair is floating-point noise: the engine is deterministic, and even
    the smallest change, 6 × 10⁻⁵, is far above round-off. The pairs at FiO₂ 0.21
    are not at the saturation ceiling (SpO₂ 0.95–0.96), and they carry the
    effect. The high σ / μ\* comes from mixing ceiling pairs with non-ceiling
    pairs, i.e. an FiO₂-dependent effect measured on 3–4 clean pairs.
  - Clean S1 SpO₂ is ≈ 0.997 only at FiO₂ 0.4733 (0.9976 F, 0.9966 M). At 0.21
    it is 0.9702 F and 0.9556 M.
  - Monograph only: the paper and the supplement carry no Group A text.
- **MF-21 — L1677–1679, §3.2.** *"SpO2 is also ventilator-driven but at a tiny
  absolute scale (μ\* ≤ 0.13) because the output sits at the hemoglobin
  saturation ceiling"*.
  - The largest SpO₂ μ\* are S3_F ← FiO₂ 0.1247, S3_M ← FiO₂ 0.1236 and
    S4_M ← FiO₂ 0.1145.
  - Clean SpO₂ in those cells spans 0.755–0.9985 (S3_F, mean 0.930), 0.698–0.999
    (S3_M, mean 0.916) and 0.846–0.967 (S4_M, mean 0.906): not at the ceiling.
  - The scale is small because SpO₂ is recorded as a fraction. μ\* 0.12 is 12
    saturation points.
  - Control: the maximum reproduces 0.1247. Monograph only.
- **MF-22 — L1052–1055 as of `d9201de`, §2.3. Found 2026-09-14 while
  resolving MF-5. ✅ Removed on the author's decision, 2026-09-14.** *"NHANES resting heart-rate
  anchors (Ostchega 2011, as tabulated in the companion `Pulse_translation_new`
  reference tables) further confirm the surrogates' vital-sign profile … is
  representative of healthy adults: median HR 70 bpm (M) / 74 bpm (F)."*
  - This is the half of MF-5 that the author kept when the BP half was removed.
    At that point Ostchega 2011 had not been opened.
  - Ostchega et al., *National Health Statistics Reports* 41 (2011), opened in
    this session (Firecrawl, `.firecrawl/ostchega2011_nhsr041_2026-09-14.md`).
    Tables 2 (males) and 3 (females), 50th percentile:
    - males: 16–19 years **69** (mean 72); 20–39 years **69** (mean 71);
    - females: 16–19 years **77** (mean 79); 20–39 years **74** (mean 76).
  - So the male 70 is neither median nor mean of either male band that covers
    ages 18 to 39. The female 74 is the 20–39 median; the band that contains
    18-year-olds gives 77.
  - The companion records the same quantity three ways:
    - "Ostchega mean ~70 for 18–39 yr" (`lookup_tables_literature_validation.md`
      L109);
    - "Age 16–19 yr: mean ≈ 72 bpm" (L91);
    - "female P50 = 74 bpm vs male P50 = 70 bpm" (L510).
  - The sentence never states the surrogates' own heart rate, so "confirm" has
    nothing to be compared against.
  - Monograph only. Searched for "NHANES" and "Ostchega": `paper.tex`,
    `supplement.tex`, both `.bib` files, `supplementary.md` and `README.md` give
    nothing. Control: "Cornish" is found 3 times in `paper.tex`.
  - It is a scientific claim, so the decision was the author's. The author
    chose to remove the sentence: it confirms nothing measurable, and no other
    passage relies on it. The monograph's other "70 bpm" and "74 bpm"
    (L2022, L2030, L2032, L3084) are engine output heart rates, unrelated.
    The paragraph now runs from Appendix B.5 straight to "Companion
    verification" (L1050–1052).

#### Observations — low, recorded

- **O-1 — L2877–2880.** The runaway trajectory described is exactly
  S1_F_0130 / 0131: plateau about 690, onset 195 s, 95 % reached at 220 s,
  PaCO₂ minimum 16.0 / 16.9. The other runaways start at 175, 140, 245 and
  285 s. The text describes one case as if it were the pattern.
- **O-2 — L1823, folded into MF-20.** "SpO₂ in the healthy respiratory
  envelope sits at ≈ 0.997". In clean S1 runs this holds at FiO₂ 0.4733
  (0.9976 F, 0.9966 M), not at 0.21 (0.9702 F, 0.9556 M). Measuring the
  elementary effects behind it turned this into MF-20.
- **O-3 — L4439, B.3** (first written "B.4"; corrected 2026-09-14 against the
  headings, B.3 runs from L4326 to L4490 after the corrections). "3,304 files /
  23 MB" describes two different sets.
  - 3,304 is every file, including `.git` (353 MB).
  - 23 MB is the text files only: 23.3–23.4 MB, about 2,900–3,000 files
    depending on the binary heuristic (NUL in the first 8 kB, or `grep -I`).
  - Without `.git` the tree holds 3,225 files and 110 MB.
  - The term counts are line counts; the zeros hold.
- **O-4 — L2795.** "[580, 680] mmHg (alveolar-gas-equation prediction
  ± 75 mmHg)" reproduces the dated S021 rule verbatim (log L139–140). But
  [580, 680] has centre 630 and half-width 50, so it is "± 75" around no single
  prediction. The band is what was committed and applied; the rule is not to be
  edited.
- **O-5 — L3730.** "~ 2.2 GB total" is attached to "output.csv / pulse.log /
  config.json / run_meta.json".
  - Those four file types weigh 0.13–0.14 GB, depending on whether the two S018
    reproduction directories count.
  - The mass is `output_pulse_native.csv`: 2.21–2.29 GB, which the sentence does
    not name.
  - The total is 2.34–2.43 GB. The sentence is dated "measured 2026-07-29".
  - Re-measured over exactly the four named directories (`full_sweep`,
    `s014_trigger_lockout`, `s018_blood_volume`, `s021_hyperoxia_convergence`):
    the five file types total 2,343,583,972 bytes, of which the native CSV is
    2,214,917,236. That is 2.34 GB, or **2.18 GiB**, which `du -h` prints as
    "2.2G".
  - So the total is right in binary units; the defect is only that the file list
    omits the native CSV, which carries 95 % of it.
  - MF-13's "~50 MB" is not a unit effect: 100.2 MiB.
- **O-6 — `cornish2023` is now a journal article.**
  - arXiv v5 was posted 2026-08-08. Its header reads "Journal of Machine
    Learning Research 27 (2026) 1-52 … Published 8/26".
  - `jmlr.org/papers/v27/24-1752.html` (Firecrawl, 2026-09-14) and its BibTeX
    give JMLR 27(152):1–52, 2026. The JMLR page shows no DOI, and a Crossref
    bibliographic query returned no match.
  - The JMLR PDF was downloaded and compared with v5, whitespace-normalised:
    74 diff lines, all section-number punctuation and math glyph extraction.
    Against v4 the control gives 3,210. Tables 4–5 "Ours" are unchanged from v4
    (85 / 281), the text still says 1,442, and v5 adds Manski columns.
  - So every number the atlas takes from Cornish holds. But the citation form
    is stale:
    - both `.bib` files say `arXiv preprint`, year 2023;
    - the monograph gives "arXiv:2301.07210 (November 2023)" at L3862 and
      "(November 2023, v4)" at L4034;
    - the labels read "Cornish et al. 2023";
    - `reference_audit.md` M-2 says "still a preprint".
  - Citation-audit rule: recorded in `audit/reference_audit.md`, nothing
    modified.
- **O-7 (was MF-10) — L2305–2311.** "The `Pulse_translation_new` E6 audit
  reported an instability zone at [0.91, 0.945] … about 90 % of the original E6
  width".
  - E6's own severe sweep covered 0.930–0.970; only 0.930–0.945 failed. The 0.91
    edge is E10's (companion log L1952).
  - E6's text does state the combined zone ("Combined with E10 … 0.91–0.945"),
    so the sentence is defensible. The monograph's own B.3, L991 and L3588
    attribute the zone to E10 and E6 jointly.
  - 0.031 / 0.035 = 88.6 %.
- **O-8 — L118.** "8 cells (4 ARDS severities S1/S2/S3/S4 × 2 …)": S1 is
  healthy. Same class as prose-sweep #48.
- **O-9 — §1.4.** "24 experiment-log entries cited throughout", while S025 and
  S026 are cited elsewhere in the monograph.
- **O-10 — L1337.** "1,260 / 1,280 bit-identical clean runs": "clean" there
  means "completed" (exit code 0). The atlas's `clean` class, unflagged runs,
  holds 663. The count is right; the word collides with a defined term.
- **O-11 — L421, notation table.** "§S1 – §S16" for the npj supplement's
  sections. The supplement has 17 numbered sections: S17 is the summary,
  rendered as such, and there were 17 already when the row was written
  (`7b2049e`).

**Second derivation, and what it changed.** The second pass over MF-1 to MF-15
changed the record four times:
- it downgraded MF-10 to O-7;
- it found MF-3's second defect;
- it raised O-6 from "v5 exists" to "published";
- it caught its own Appendix C parse matching Table 1.

It also started the pointer pass, which found MF-16, MF-17, MF-19 and O-11.
Instruments that failed and were caught:
- the rule-based quantity split (above);
- the Appendix C regex;
- `grep -c "^\\section{"` returned 0 on both the old and the current supplement,
  while the fixed-string count gave 17 on both, matching the `Grep` tool.

**Not covered.**
- The monograph's by-value `guard` / `ledger` occurrences.
- Qualitative sentences that carry no number. MF-18, MF-20 and MF-21 were found
  in passing, so the monograph's prose is not claimed clean.
- The AI-tool dates.
- For MF-5: the Singapore study and the AAP 2017 PDF; only its HTML tables were
  read. Ostchega 2011 was opened on 2026-09-14, during the resolution (MF-22).

#### Resolution — 2026-09-14 (night)

**Who decided.**
- **The author, in three rounds of questions:**
  - MF-1, MF-2, MF-3, MF-11, MF-12 and MF-18, as proposed;
  - MF-5: remove the BP half;
  - MF-7: "twelve";
  - Cornish: cite JMLR;
  - MF-20 and MF-21: rewrite to the measurement;
  - O-7: attribute to E10 + E6;
  - O-3, O-5, O-8, O-9 and O-10;
  - third round: MF-22, remove the heart-rate sentence; MF-20, say that the
    large effects are three of the four pairs at FiO₂ 0.21.
- **Not selected:** O-1. **Not to be edited:** O-4, a dated rule.
- **Applied as mechanical under the autonomy pact, without a question:** MF-4,
  MF-6, MF-9, MF-13, MF-14, MF-15, MF-16, MF-17, MF-19 and O-11. Each is a
  literal or a pointer that drifted from its own artefact, and none changes a
  claim.

**What the monograph now reads.** L-numbers are current as of the MF-22 commit.

| finding | now reads | re-derived by the guard |
|---|---|---|
| MF-1 | L4651 "Largest in S4 (91 / 185 of the residual)" | `nss_decomposition.csv`: S4 91, S1 53, total 185 |
| MF-2 | L2770 "[0.21, 0.47] vs single-input"; L2772 "PaO2 ≈ 480 mmHg"; L4317 "S1 clean runs, whose FiO2 spans only [0.21, 0.47], gives a flatter slope" | clean S1 FiO₂ levels are exactly 0.21 and 0.4733; the OLS fit at 1.0 rounds to 480 |
| MF-3 | L61–64 "of the remaining 17 cells, 11 have a bootstrap CI straddling 0.6, 1 is CI-robustly non-linear (S3_M, PaO2 ← FiO2), and 5 have too few clean trajectories for a CI (S1_F where Vt dominates, S4_M where FiO2 dominates)" | `sobol_ci_buckets.csv` rank 1: 31 / 11 / 1 / 5, the six cells named |
| MF-4 | L1297 "(i5-11400H, 8 GB RAM, CPU-only)"; L1304–1305 "Pulse is CPU-only, so neither of the laptop's two GPUs (Intel UHD, NVIDIA RTX 3050) is used" | text |
| MF-5 | L1050–1052: the SBP / DBP values were removed first; the heart-rate sentence left behind was removed too, under MF-22. The paragraph goes from Appendix B.5 straight to "Companion verification" | text: that junction is required; "SBP 118 mmHg (M)", "NHANES P50 anchors", "NHANES resting heart-rate anchors" and "median HR 70 bpm (M) / 74 bpm (F)" are banned |
| MF-6 | L4539 "(CDC P50 ≈ 176.2 cm)" | text |
| MF-7 | "twelve" at L1298, L1311, L1315, L1322; `supplementary.md` S10 heading "(twelve independent layers)" and "12 independent verification points" | the S10 table has 12 rows |
| MF-9 | L1350 "mild-ARDS male cell" | `src/scenario.py`: S2 is Mild ARDS, 0.26 |
| MF-11 | L3386–3387 "HR and MAP drift rates stay below 3 % and PaCO2 below 4 %" | per-arm rates against `_WIN_TH`; hyperoxia PaCO₂ is at least 3 % (3.59 %) |
| MF-12 | L2943 "for run S1_F_0008" | rank 6 before the lock; worst after it |
| MF-13 | L3678 "~105 MB of engine logs" | the 1,280 `pulse.log` total 105.1 MB, rounding to 105; skips when the logs are absent, fails when partial |
| MF-14 | L4635 "(71 / 76 of those runs" | S1 + S2 = 71 of 76 |
| MF-15 | L1448 "`src/detector.py:413`" | line 413 holds `std(ddof=0)` |
| MF-16 | L600 "discussed in §4.5."; L1865 "in the §4.5 limitations"; L2516 "(§4.5 limitations)" | §4.5 is Limitations; no §4.3 is |
| MF-17 | L416 "(§3.5)" | the blood-volume formula sits under §3.5 |
| MF-18 | L3349–3352 "of the four channels shared with the atlas, PaCO2 is the only one flagged under Hoeffding (3 / 70) and the most flagged under the bootstrap (13 / 70, against PaO2 4 / 78, MeanBP 3 / 92, HR 1 / 162)" | the four overlap rows of Table 2 |
| MF-19 | L3584–3585 "documented in our preregistration (scenario table and H3) and in the §1.2 limitations list (entry 4)" | text |
| MF-20 | L1817–1827, "Group A — saturation-boundary cells": 3–4 clean pairs; at FiO2 ≈ 0.47, SpO2 0.997–0.999 and effects of at most 0.003; "the large effects (\|EE\| 0.014–0.049) all come from pairs taken at FiO2 = 0.21, where SpO2 is 0.95–0.96 — three of the four pairs there (one Vt step moves SpO2 from 0.962 to 0.929)"; "not floating-point noise" | 3 + 4 pairs; max \|EE\| at 0.47 is 0.0028, SpO₂ 0.99664–0.99891; at 0.21 the effects are 0.0006, 0.0136, 0.0322 and 0.0492 (4 pairs, 3 above 0.005), from SpO₂ 0.95373–0.96358; one step rounds exactly to 0.962 → 0.929 |
| MF-21 | L1676–1678 "on a small numerical scale (μ\* ≤ 0.13) because it is recorded as a fraction: the largest value, 0.12 in S3, would read 12 in percentage points" | the largest SpO₂ μ\* rounds to 0.12, in S3; clean SpO₂ there falls below 0.8 |
| O-3 | L4448 "3,304 files, 23 MB of them text" | text |
| O-5 | L3732 the file list names `output_pulse_native.csv` | text |
| O-7 | L2306 "E10 boundary probe, confirmed by E6, reported an instability zone"; L2310 "of the original width" | text |
| O-8 | L119 "8 cells (4 scenarios, healthy S1 and ARDS S2/S3/S4, × 2 reference bodies M/F)" | text |
| O-9 | L634–635 "24 core experiment-log entries (S001–S024)" | text |
| O-10 | L1337 "completed runs and 20 / 20" | `sha_compare.json`: BIT_EXACT 1,260, BOTH_DIVERGED 20 |
| O-11 | L422 "§S1 – §S17" | `supplement.tex` has 17 `\section` |
| Cornish | both `.bib` files cite JMLR 27(152):1–52, 2026; labels read 2026; reference 4 (L3867) and §9.7 (L4039–4042). Details in `audit/reference_audit.md`, "Resolution 2026-09-14 (night)" | the JMLR fields in both `.bib` files |

Every row also has its new wording required and its old wording banned, on
whitespace-normalised text. The bans for O-5 and O-9 were missing from the
first guard and were added before the commit.

**Kept on purpose:**
- the S017 title "Cornish 2023 cross-mapping" at L668, L4259 and
  `README.md:468`;
- the six `source_file` strings "Cornish et al. 2023" in
  `scripts/audit_claims.py`.

**Defects in my own application, caught before the commit.**
- **MF-2's third locus was missing from the edit list.** It was then at L4309.
  It was found while writing the banned list.
- **Two Cornish labels wrap across a line break.** They are "Cornish\n2023" and
  "Cornish\net al. 2023". The line-based search missed both, and so did the
  first guard. The rendered-PDF check found them. Banned wordings are now
  matched on whitespace-normalised text; a targeted reinjection gave 2 FAIL.
- **MF-20 first read "from 0.962 to 0.930".** The endpoint is 0.9294957, which
  prints as 0.92950 at five decimals (this register, MF-20 above) and was then
  rounded a second time. The first guard compared with a tolerance of 6 × 10⁻⁴
  and passed it. A full-precision re-read during the gate found it.
  - The wording now reads 0.929.
  - The guard now uses exact rounding. It also tests what its label claimed but
    did not check: the 3 + 4 split, SpO₂ 0.997–0.999 at 0.47, and 0.95–0.96 at
    0.21.
  - Reinjection of text and constant: 3 FAIL.
- **§9.7 first said Cornish's "Tables 4 and 5 are unchanged in the published
  version".** Both tables gain Manski columns in JMLR (pp. 39–40), which
  `reference_audit.md` had already recorded. It now reads "keep the same counts
  and add Manski-bound columns". The 15 "Ours" rows of both tables were
  re-checked against v4. Reinjection: 2 FAIL.
- **The MF-13 check first rounded to the nearest 5 MB.** It now rounds to 1 MB
  (105.1).
- **Two labels in this register and in `reference_audit.md` were wrong.** O-3
  said "B.4"; it is B.3. The Cornish addendum said "Table S7"; the table renders
  as S13. Both are corrected in place with a note.

**A nuance on MF-20, resolved on the author's decision.** The first rewrite,
"the pairs taken at FiO2 = 0.21 … carry the large ones", was true of where the
large effects sit. But one of the four pairs at 0.21 is small (\|EE\| 0.0006,
S1_F, trajectory 11), and the approved option had described the effects the
same way. It now reads "the large effects (\|EE\| 0.014–0.049) all come from
pairs taken at FiO2 = 0.21, where SpO2 is 0.95–0.96 — three of the four pairs
there". The guard counts the pairs: 4 at 0.21, 3 of them above 0.005.

**Instrument defects.**
- **`audit_number_inventory.py` decoded the ledger's output in the Windows
  locale.** `audit_claims.py` writes UTF-8, but the inventory read it with
  `text=True` and no encoding, so as cp1252.
  - Non-ASCII came through as mojibake, and "←" (E2 86 90) in a new guard label
    crashed the reader.
  - Fixed with `encoding="utf-8"`.
  - Measured on the same bytes under both decodings: 394 claim rows and the same
    203 values, with no value cell holding non-ASCII. The fix moves nothing.
  - Committed separately.
- **`grep -c $'\r'` in Git Bash counted 0 on files that carry CRLF.**
  - Python byte counts showed CRLF in the working copies of
    `supplementary.md`, `paper.bib` and `references.bib`.
  - They were normalised to LF, as `.gitattributes` requires; the index was
    already LF.
  - The npj pair was rebuilt after that normalisation: identical text, 25 and
    63 pages.

**Guard.** `check_monograph_number_audit` in `scripts/audit_claims.py`: 62
checks, wired into the exit status.

| reinjection | FAIL |
|---|---:|
| all old wordings (61 checks at that time) | 43 |
| again at the end: the five source files restored to HEAD `cf67974`, 62 checks; the new O-5 and O-9 bans both fire | 44 |
| the two wrapped labels | 2 |
| 0.930 | 3 |
| "Tables 4 and 5 are unchanged" | 2 |
| MF-22 and the MF-20 precision: the monograph restored to `d9201de` | 3 |
| the MF-20 large-pair count faked to 4 in the check | 1 |

The MD5 was restored after each one.

**Gate.**
- `audit_claims.py --check-paper-sync --check-monograph`:
  - 394 / 394 anchors;
  - 26 / 26 monograph anchors;
  - 25 / 25 headline counters;
  - 62 / 62 guard checks;
  - 0 FAIL in either form.
- pytest: 80 passed.
- Inventory: 39 probes, 0 FAIL.
- `check_render.py`: PASS, with 1 accepted residue.
- **Rebuilt:** monograph 121 pages; paper 25; supplement 63; PDF and DOCX.
- **Rendered monograph, checked on whitespace-normalised `pdftotext` output:**
  - 31 new wordings present;
  - 29 old ones absent, including 0.930, "unchanged", the NHANES sentence and
    "carry the large ones". Two of the 29
    ("§4.3 limitations", "§S1 – §S16") hold glyphs that `pdftotext` mangles,
    so their absence proves nothing; the source-text guard covers them.

**Bucket movement.** Occurrences, HEAD `cf67974` → now, read from
`summary.json` and `inventory.csv`.

| artefact | `none` | `ambiguous_small` | `guard` | `ledger` | retained |
|---|---|---|---|---|---|
| paper | 37 | 307 | 165 | 18 | 527 |
| supplement | 432 → 412 | 960 | 463 → 484 | 32 → 31 | 1,887 |
| monograph | 803 → 795 | 1,864 → 1,879 | 648 → 670 | 28 | 3,343 → 3,372 |

- **Paper:** unchanged.
- **Supplement:** no number in its text changed.
  - All 21 moves are the by-value limit of §2: the new guard strings pin 65.6,
    1.02, 480, 481, 105, 162, 3050, 0.930 and 0.999.
  - 481 and 0.930 are held by the guard only as banned wordings.
  - The supplement's own 481 (L493, a table range) is unrelated, and was read
    in §4.1 as `none`.
  - Its 0.930 (L464) is unrelated too. It was `ledger`, covered by value only,
    and is still not read one by one.
- **Monograph:** the literal sequences, aligned in document order, give 16
  literals removed and 45 added. Each falls on an intended edit.
  - 14 unchanged occurrences moved by value, into `guard`.
  - The new `none` literals are each re-derived by a guard check or read from
    the source:
    - 0.47 ×3, 0.21, 0.003, 0.014 and 0.049 (MF-2, MF-20);
    - 0.12 (MF-21), 3.5 (MF-17), 1.2 (MF-19), 71 (MF-14);
    - 27 ×2 (JMLR volume).
  - They stay `none` because `guard` needs a distinctive literal.
- **Totals:**
  - retained 5,757 → 5,786;
  - distinct values 728 → 730;
  - guard-pinned literals 927 → 1,031.
- **Then MF-22 and the MF-20 precision (`d9201de` → the next commit):**
  - monograph `none` 795 → 794 and `ambiguous_small` 1,879 → 1,878: the
    removed 70 and 74. Its 2011 leaves the year-like set;
  - retained 3,372 → 3,370, and 5,786 → 5,784 in total;
  - guard-pinned literals 1,031 → 1,034;
  - 0.014 and 0.049 only move within the rewritten sentence;
  - paper and supplement unchanged; no occurrence changed bucket by value.

## 6. The `guard` and `ledger` occurrences, read one by one — 1,396 occurrences (2026-09-15)

**Why.** `guard` and `ledger` are coverage by *value* (§2). An occurrence lands
there when some gating string or ledger anchor holds the same literal or value,
whether or not that source is about this occurrence. A published "160" that
means 160 bpm is "covered" by the 160 runs per cell. Until now these rows were
counted as covered and never read.

**Population, unit, denominator.** Every `inventory.csv` row whose bucket is
`guard` or `ledger`, at HEAD `441355e`. Unit: one retained literal occurrence.

| artefact | guard | ledger | read |
|---|---:|---:|---:|
| paper | 165 | 18 | 183 |
| supplement | 484 | 31 | 515 |
| monograph | 670 | 28 | 698 |
| **all** | **1,319** | **77** | **1,396** |

These equal `summary.json`, which is the positive control on the population.

**Instrument** (scratchpad, session `2b7e8306`).
- **`gl_worksheet.py` builds one worksheet per artefact, grouped by literal.**
  For each literal it lists:
  - the ledger claims with the same value (394 claims parsed);
  - every quoted string in `audit_claims.py` and `check_*.py` holding the
    literal, 1,091 in all, each with the enclosing constant or function;
  - the 94 crosswalk rows and the 26 monograph anchors;
  - every occurrence with its context.
- **The locus tag is only a hint.** An occurrence is tagged LOCUS when a
  non-banned, non-label pinning string holding the literal matches the
  whitespace-normalised text across that occurrence's line.
  - Calibrated on 8 known cases, 8 PASS (`gl_calibrate.py`): 176.2 at L4539 and
    L723, 480, 3050 and 0.929 in the monograph; 0.930, 481 and 3050 in the
    supplement.
  - Tags: paper 90 / 183, supplement 185 / 515, monograph 63 / 698.
- **Verdicts come from reading every row's context.** Each occurrence is
  either the quantity its bucket source pins (SAME), or a different quantity (or
  a non-quantity) checked against its own source (EXCEPTION).
- **`gl_completeness.py` accounts for every row exactly once**, and every listed
  exception must match a real row:
  - 1,396 = 264 exceptions + 1,132 SAME;
  - paper 16 + 167, supplement 122 + 393, monograph 126 + 572;
  - 0 bad keys;
  - negative control: a line number shifted by one gives BAD.

**What the by-value buckets were hiding.** 264 occurrences, 19 %, are a
different quantity from the one that "covers" them. Examples:
- **"160":** runs per cell, but also 145–160 bpm output HR.
- **"454":** the excl-SpO₂ total, and 454 of 1,120 clean pairs.
- **"120":** simulation length, the BP gate, and the 120-s settle of the March
  calibration.
- **"640":** female runs, and 640 mL delivered volume on one waveform.
- **"256":** a companion P/F, a Sobol base sample, and SHA-256.
- **"100":** "over 100 pages".
- **"2301.07210":** an arXiv identifier.

Each was checked; none of these particular collisions was wrong.

**Re-derived today, in memory, nothing written to the repository.**
- **P/F table `tab:s5-berlin-sweep`** (26 numeric cells): recomputed with
  `pf_berlin_analysis`'s own functions from `aggregated.parquet`, 0 differences
  from `results/pf_berlin_by_scenario.csv`.
- **S021.** As `make_supp_fig_s3.py` computes them:
  - median trajectory 530.2 at t = 0 and 641.1 at t = 300 s;
  - final-60-s medians S3 143.6 [93, 218], S4 72.6 [71, 76];
  - converged S1 40 / 44, S3 8 / 8, S4 8 / 8;
  - locked-window PaO₂ over the four input-identical RR = 20 pairs: male 662.6,
    female 686.0;
  - runaway trajectories of S1_F_0130 / 0131: ≈ 690 → 1,358–1,380 at 220 s →
    1,404 at 240 s;
  - the two remaining F-003 runaways S1_F_0118 / 0119: 475–482 mmHg to 60 s,
    then 1,000–1,008.
- **Clean S1 PaO₂:** 81.1 ± 11.0 at FiO₂ 0.21 (n 47) and 214.2 ± 29.9 at
  0.4733 (n 44).
- **Clean HR_mean per cell:** S4_M 146.515, S4_F 147.658, S3_F 153.173, S3_M
  157.880, against S1_M 76.083. The text says "147 – 158 vs 76".
- **Waveform S4_F_0003, pre-lock.**
  - Classifier CV 0.35084. The median 0.350867 is the midpoint of S4_F_0003 and
    S4_F_0089, an exact tie broken on case id, as the caption says. Lock CV
    0.00544.
  - Native delivered Vt over the classifier window, using the figure script's
    120 s clock offset: median 640.1, IQR 637.6–643.6.
- **μ\*:** Vt←Vt 488.6–503.1 across cells; PaO₂←FiO₂ S2 133.1 / 146.7.
  Diverged male run indices: S1 = S2 = S3 = {119, 157, 158, 159}; S4_M adds
  {24, 82, 137, 138}.
- **S030** (`s030_run_index.csv`, `s030_pf_by_arm.csv`):
  - fractions 0.910–0.945 exit 1 in both arms; 0.900 and 0.950 exit 0;
  - locked M 0.95: RR 19.95, PaCO₂ 50.78, P/F 91.49;
  - free M 0.95: RR 30.57, Vt 418.2, PaCO₂ 43.57.
- **Wasserstein table rows:** S1 PaO₂ 11.02 / 12.57 / 28.38; S2 HR null p50
  3.596; S4 Vt null p50 28.958.
- **Spearman table:** all 12 CI upper bounds 1.0.
- **Sobol stable set at 500 / 1,000 / 2,000 / 4,000 resamples: GL-S2 below.**

**Primary sources opened today.**
- Berlin Definition, JAMA 2012: PubMed 22797452 abstract, bands 200–300 /
  100–200 / ≤ 100. The PEEP ≥ 5 criterion sits in the full-text table, not
  opened.
- Pulse `SetupPatient.cpp` L139 / L144: the Devine relation 45.5 / 50.0 + 2.3 ×
  (in − 60).
- The companion `experiments_log.md`:
  - L612 (5 min, 120 s settle);
  - E10 table L1950–1970 (0.90 pass, eight failures 0.91–0.945, 0.95 pass);
  - E6 severe sweep L2309–2326;
  - E6 calibrated fractions L2279 / L2299 / L2348 (252 / 148 / 75);
  - coarse sweep L618–632 (199.3 / 150.1 / 118.7);
  - FiO₂ = 1.0 crash probe L1790–1815 (nine runs, all in 0.95–1.00).
- `src/detector.py` L120–121 (flatline tolerance 0.001) and S004 L96–100 (8 / 8
  false-positive `clamped`, SBP 140 message).

**Relied on as recorded in this repository's registers, not re-opened today.**
- `reference_audit.md`:
  - ESH grade 3 ≥ 180 / ≥ 110 (full text 2026-09-14);
  - Marini Ch. 1 (MATCH 2026-09-14);
  - West Ch. 2 chapter (OK; the "~150 mL" value itself not re-read);
  - page ranges of `nin2017`, `emeriaud2023`, `sinderby1999`, `bray2019`
    (field by field).
- §5 O-1 (runaway timing), MF-4 (GPU), MF-6 (CDC 176.2).
- `pulse_sex_conditioned_parameters.md` (Hb 15.0 / 14.0, Hct Hb / 34).
- The companion PC-AC figures behind +24.0 % / +58.9 %: 594.5 / 479.6 and
  635.3 / 399.7.

**Findings.**
- **GL-S1 — `supplement.tex` L867.**
  - It read: *"The narrower 0.91--0.945 zone was recorded in our preregistration
    limitations table (Supplement §S2 row 4)"*.
  - `preregistration.md` has never contained the word "limitation"
    (`git log -S`: 0 commits). The zone is in its scenario table (L112) and in
    H3 (L76), and the twelve-row table is Supplement §S2, row 4.
  - Same defect as monograph MF-19. The paper, `supplementary.md` and README
    carry no such wording.
  - ✅ **Corrected as a mechanical pointer fix**, under the autonomy pact, as
    MF-19 was. It now reads *"was documented in our preregistration (scenario
    table and hypothesis H3) and in the verified-limitations table (Supplement
    §S2, row 4)"*.
  - Guarded: new wording required, old one banned in `supplement.tex`. Guard 63
    checks. Reinjection with the supplement restored to HEAD: 2 FAIL.
  - Rebuilt: supplement 63 pages. Dehyphenated render: new wording 1, old 0.
    DOCX carries the new wording.
- **GL-S2 — `supplement.tex` L345, and the `scripts/sobol_ci_buckets.py`
  L73–74 comment. ✅ Corrected on the author's decision, 2026-09-15.**
  - It reads: *"Repeating the whole procedure at 2,000 and at 4,000 resamples
    returns the same 23 combinations, and at 500 one combination is lost"*.
  - Re-measured with the versioned generator (`build_table()`, module
    `N_BOOTSTRAP` set to 500, 1,000, 2,000 and 4,000), in memory: 23 / 23 / 23 /
    23, identical sets.
  - N = 1,000 equals the committed `sobol_ci_buckets.csv`; runtime scales with N
    (11 / 20 / 38 / 75 s).
  - Since `d639747` the script changed only in `summarise()`'s cost model
    (`5a6b201`), and its tracked inputs (`results/morris_indices.parquet`,
    `src/analysis_morris.py`) did not change. The raw per-run `output.csv` it
    also reads are git-ignored, so git cannot vouch for them; the N = 1,000 run
    reproducing the committed CSV exactly is the evidence that they give the same
    result. A first draft of this entry said "the code and its inputs are
    unchanged", which git could not show for the ignored files.
  - The "22 at 500" of S031 (decision 6, 2026-07-28) does not reproduce with the
    versioned generator, and how it was obtained is not recorded. S031's
    32-convention sweep (Finding 3) concerns a different count. A first draft
    here said it "predates the versioned generator", which the record does not
    show: `d639747` already carries the sentence.
  - Direction: conservative. The set does not lose a combination at 500 either.
  - Only locus: supplement L345.
  - **Resolution.** The author chose to state the measurement.
    - L345 now reads *"Repeating the whole procedure at 500, 2{,}000 and 4{,}000
      resamples returns the same 23 combinations, so the stable set does not
      depend on the resample count."*
    - The script comment now says the set is identical at 500 / 1,000 / 2,000 /
      4,000, re-measured 2026-09-15, and that the earlier statement does not
      reproduce.
    - S031 gains a dated correction note; decision 6 is kept as written.
    - Guard: the new supplement wording is required; the old clause is banned
      in `supplement.tex`, and "one combination is lost at 500" in
      `scripts/sobol_ci_buckets.py`.
    - No data check re-runs the bootstrap, which takes about two minutes. The
      measurement is recorded here and reproducible with
      `sobol_nboot_sensitivity.py`.
    - Checks: gate 394 / 394, sync 94 / 94, 26 / 26, guards 22 / 22 and 65 / 65,
      0 FAIL. Reinjection of both files at `ba214ec`: 3 FAIL. Supplement 63
      pages. Dehyphenated render: new sentence 1, old clause 0. The DOCX carries
      the new sentence.
    - Inventory: 39 probes, 0 FAIL. One `500` moves within L345. The new
      required string holds "2{,}000" and "4{,}000", so every occurrence of
      those values moves by value alone: paper `2{,}000` ×3 and supplement ×5
      ledger → guard, monograph `2,000` ×6 ledger → guard, supplement
      `4{,}000` ×1 none → guard. This is GL-O2's by-value effect; all were
      read above as the same quantity.

**Observations.**
- **GL-O1.** `tab:s5-berlin-sweep` (26 numeric cells) has no ledger anchor and
  no guard. Recomputed today with 0 differences, but nothing would catch a
  future drift.
- **GL-O2 — instrument.** `guard_literals()`'s quoted-string regex also captures
  the code between two string literals. Examples are `'): (160, 0, 4, 11, 107,
  49),\n    ('` and `manuscript_value=51.8, computed_value=100.0 * …`.
  - `guard` therefore holds pinned code constants, which is intended, but also
    incidental ones: `100.0 *`, `663e10` in an arithmetic encoding of several
    values for one comparison, "530d281" in a commit id.
  - The inventory also splits "4 802.63" (thin space) into two literals. The
    value was verified.
- **GL-O3.** L867 "corroborated by three independent boundary probes" against
  §S5-prov "within the same companion project rather than independent
  third-party replications".
  - The companion's own log says "3 independent sources"; §S5-prov says
    "run-by-run independent execution".
  - Two senses, both defensible. No change.

**Defects in my own instruments, caught before any conclusion.**
- **Two calibration cases carried stale line numbers** (722 / 1826 for 723 /
  1825). The instrument was right.
- **A C14 filter used `case_id` where `plateau_stats` has `case_id_orig`.** It
  first pooled all 21 S1 pairs instead of the S021 cohort's 4.
- **The first waveform measure (median 666.4 mL) read the native file on its own
  clock**, which is the settling phase. Corrected by reading
  `make_supp_fig_s4.py`'s offset rule.
- **Three fixed-string counts returned 0** because of shell escaping; re-run
  with `grep -F`.
- **A `sed` turned `\n` into a real newline in a scratch script.** It failed to
  parse and ran nothing.

**Not covered by this section.**
- **Year-like literals, set aside by rule 7:** paper 4, supplement 18,
  monograph 153. The Cornish "2023" label in §5 was one of them. Read in §7.
- **Literals masked as non-quantities by the other rules** (§2.1 counts): tex
  comments, versions, link targets, URLs, machinery, file paths, organisation
  identifiers.
- **Prose that carries no number.**

## 7. The year-like literals, read one by one — 175 occurrences (2026-09-15)

**Why.** Rule 7 sets year-like integers aside, so no residue ever showed them. §5's
stale "Cornish 2023" citation label was one of them.

**Population.** Every `masked_by_rule.csv` row with rule `year_like`: paper 4,
supplement 18, monograph 153, for 175 occurrences on 163 lines. These equal
`summary.json` (inventoried minus retained, per artefact), which is the positive
control. Unit: one literal occurrence.

**Instrument** (scratchpad, session `2b7e8306`).
- **`yl_worksheet.py` builds one worksheet per artefact**, grouped by literal,
  with each occurrence's own context.
  - A first version cut its snippet around a literal's first match on the line,
    so the supplement's second "2017" on L118 and second "2026" on L462 printed
    as copies of the first.
  - It was rebuilt on each row's own context before any verdict. The `sed` edit
    of that fix first broke the script with a syntax error, so nothing ran on
    the broken version.
- **`yl_refyears.py` compares the monograph's 34 reference-list entries with
  `references.bib`**: the final "(YYYY)" and the page range. Result: 0
  differences. Title-embedded years ("2000 CDC Growth Charts", "… Septic Shock
  2021", "2023 ESH Guidelines") were checked against the bib titles.
- **`yl_completeness.py` gives every line holding a year-like row exactly one
  verdict** and rejects any verdict key without a row.
  - Result: 175 classified; 0 unclassified, 0 bad keys.
  - A wrong key (L4105 for an entry whose year sits on L4107) was caught by the
    checker itself.

**What the years were checked against.**
- **Citation years and author-year labels:** `references.bib` (reference-audited)
  and the JMLR record for Cornish.
- **Pulse history:**
  - the GitLab API gives `physiology/engine` a `created_at` of 2017-05-02 (the
    "forked in 2017" statement);
  - tag dates: `STUDY_SENSITIVITY_ANALYSIS_1_0_0` is 2020-07-20, `REL_4_3_2` is
    2025-08-12;
  - `docs/Markdown/Versioning.md`: "Pulse v4.2.0 (October 2023) … iOS build
    support";
  - S016 L123 records the study's last functional commit, 2020-08-24.
- **Harris–Benedict "1919 originals":** the record "Carnegie Institution of
  Washington; 1919. Publication No. 279". It was seen only as a search-result
  citation next to the J Am Diet Assoc article on those studies
  (`S0002-8223(98)00100-X`); the 1919 monograph itself was not opened.
  - Pulse `SetupPatient.cpp` L771–774 carries the Roza–Shizgal constants
    (88.632 + 13.397 W + 4.799 H − 5.677 A), not the originals.
- **Dated records:**
  - experiment-log headers: S003, S006, S014, S016, S017, S018, S020, S024;
  - `preregistration.md`: the 2026-04-22 amendment with MAP removed, the
    2026-04-22-b amendment, and the 2026-05-19 erratum;
  - `reference_audit.md` entries dated 2026-07-26, 07-27 and 07-28;
  - the companion log's section headings: calibration March 2026, E6 / E10 April
    2026, crash probe April 2026;
  - the companion internals file (2026-04-07);
  - the commit that introduced each dated sentence, which matched its date in
    every case. Examples: "added 2026-08-06" is `ffdd5c8` of 2026-08-06; the
    re-execution "2026-05-16 → 2026-05-18" is `4771e9b` of 2026-05-18; "re-pointed
    2026-06-05" is `8a5411f` at 2026-06-06 00:15.
- **AI-tool dates** (monograph §7 and §8, paper L389): the author's record, not
  verifiable here. They are consistent between the two documents.
- **"France 2030":** a programme name, not a quantity.

**Findings.**
- **YL-M2 — `manuscript.md` L4527–4528.**
  - It read: *"The audit trail is recorded in that project's experiments log (CDC
    weight audit step, 2026-03)"*.
  - The only CDC weight audit step in the companion log ("Step 1: CDC Weight
    Audit", L721) sits in the section "Female Pediatric Population —
    Implementation (April 2026)". The commit that added it is `a7fa508`, dated
    2026-04-01, in the read-only companion repository.
  - The sentence entered this repository in `2487cf7` (2026-05-19). The
    supplement and the paper carry no such date.
  - ✅ **Corrected as a mechanical pointer fix** (a literal that drifted from its
    own source): it now reads "2026-04".
  - Guarded: new wording required, old banned (66 checks). Reinjection: 2 FAIL.
  - Monograph rebuilt, 121 pages. Dehyphenated render: new date 1, old 0.
- **YL-M1 — `manuscript.md` L4, the title-page date. ✅ Corrected on the
  author's decision (2026-09-15; resolution at the end of this item).**
  - The YAML header reads `date: "2026-05-26"`. It was set by `65097a1` on
    2026-05-26 and has not changed since, and it renders on the PDF title page.
  - The same document was last revised on 2026-09-15. It carries dated entries
    up to "Verified verbatim 2026-08-25", "measured 2026-08-13" and "re-read
    2026-08-20", so the displayed date precedes the document's own content.
  - The paper and the supplement set no `\date`. Their rendered first page
    (`pdftotext`, 42 and 41 lines) shows no year, so they display no date.
  - Which date belongs there (release date, last revision, or first version plus
    a revision line) is a presentation choice with more than one defensible
    answer, so it is brought to the author.
  - **Resolution.** The author chose the revision date, to be updated at each
    deposit. The header now reads `date: "2026-09-15"`.
    - Nothing else depends on it: `git grep 2026-05-26` outside `audit/` and
      `experiments_log/` finds only this line and an unrelated dated sentence in
      `preprint_npj/README.md` (L210). `CITATION.cff` carries its own
      `date-released: 2026-05-22` for software v0.1.0, left to its
      deposit-time update.
    - Guarded in `check_monograph_number_audit` (68 → 69 checks). The check is
      the defect itself, not a pinned day: the title date must not be earlier
      than the latest ISO date in the body (2026-08-25, L4018), so a later
      revision date still passes. Dates written in words are not compared.
    - Reinjection of the previous monograph: 1 FAIL (title 2026-05-26, latest in
      body 2026-08-25). MD5 restored.
    - Monograph rebuilt, 121 pages. PDF page 1: new date 1, old 0, title
      present; whole PDF: old 0. DOCX: new 1, old 0.
    - Inventory: 39 probes, 0 FAIL, `summary.json` unchanged. The title-date
      tokens stay in `ambiguous_small` (L4 "05" → "09", "26" → "15").

**Movement.**
- Inventory: 39 probes, 0 FAIL. Buckets are unchanged.
- The month token of the corrected date moves inside `ambiguous_small`
  (monograph "03" 3 → 2, "04" 13 → 14).
- Guard-pinned literals 1,039 → 1,042.

## 8. The remaining masked literals, read one by one — 283 occurrences (2026-09-15)

**Why.** A mask removes a literal before any bucket sees it, so a masked quantity
could never appear in a residue. §2.1 had read some masked groups: the paper's and
the supplement's typesetting lengths, the supplement's two line references and
the monograph's 89 inline-code literals. §7 read the year-like literals. This
section reads everything else.

**Population.** Every `masked_by_rule.csv` row except `year_like` (§7) and the
four groups §2.1 records as read. Unit: one literal occurrence.
- Paper 40: comments 27, product versions 7, machinery 4, organisation
  identifiers 2.
- Supplement 77: machinery 53, comments 12, versions 7, file paths 2,
  organisation identifiers 2, product versions 1.
- Monograph 166: versions 55, link targets 42, URLs and DOIs 42, line references
  13, product versions 7, code fences 3, organisation identifiers 2, machinery 1,
  typesetting lengths 1.
- Positive control: per artefact, `summary.json` → `literals_removed_per_rule`
  minus the groups already read gives 51 − 11 = 40, 85 − 8 = 77 and
  255 − 89 = 166.

**Instrument** (scratchpad, session `04199c63`, not committed).
- **`mk_worksheet.py`** prints each row with its full source line, not the
  producer's snippet. It also checks that the literal occurs on the stated line:
  283 of 283 do.
- **`mk_mono_checks.py`** resolves the monograph's three-part section pointers to
  their headings. It compares each DOI link's text with its target, and with the
  `doi` field of the `references.bib` entry the line belongs to. Positive control:
  an altered DOI is flagged.
- **`mk_completeness.py`** gives every row exactly one verdict class, and each
  class carries a structural test on the row's own source line.
  - Result: 283 classified, 0 unclassified, 0 test failures, 0 bad keys.
  - Negative controls: a bogus line key is reported, and forcing a wrong class on
    the version rows fails 62 tests.
  - Its first run failed 48 rows. The fault was in my tests, not in the
    documents. The DOI pattern consumed the "10." prefix before looking for the
    literal. The line-range pattern accepted only the first number of a range
    split by a line break ("810–818" at the start of a line). Both were fixed and
    the run repeated.

**What each class was checked against.**

| class | rows | checked against |
|---|---:|---|
| LaTeX comments | 39 (paper 27, supplement 12) | Not rendered. Each sits after an unescaped `%`. Their content was not verified, for instance the word counts in the paper's title and abstract comment banners. |
| `\mainref` section numbers | 43 (supplement) | The 11 distinct labels, resolved by hand in `preprint_npj/build/paper.aux`: every typed number agrees. Second instrument: `check_render.py`, crossdoc OK. |
| Chapter locators | 5 (supplement L208 ×2, L212 ×2, L216) | The cited editions, opened this session: Marini & Dries Ch. 1, West & Luks Ch. 2 and Ch. 5, Marino Ch. 25. All MATCH. Quotations, pages and one precision on the 2026-09-14 page evidence are in `audit/reference_audit.md`, addendum 2026-09-15. |
| Figure widths, title-block layout | 11 (paper 4, supplement 5, monograph 2) | `\includegraphics[width=…]`, and the monograph's `minipage` and `\vskip`: not quantities. |
| Organisation identifiers | 6 | UR 3450 and INSERM UMR_S 1256, identical in the three affiliation lists. |
| AI product versions | 13 (paper 7, monograph 6) | Claude Opus 4.7, 4.8 and 5, and GPT-5.6: the same in the paper (L389, L391) and the monograph (L3770–L3811). At paper L389 each Claude version sits next to its model id (L391 names the versions without ids). The dates are the author's record (§7). |
| Other versions | 3 | Python 3.12+ (supplement L886) against `pyproject.toml`, `requires-python = ">=3.12"`. "SALib 2.0" (monograph L4068) is part of the Iwanaga et al. 2022 title. macOS 26.5.1 (supplement L976) against the `sw_vers` row of `audits/reproduction_macos_2026-06-13/README.md` (L48), the record from co-author Y.M.'s host. |
| Pulse 4.3.1 / 4.3.2 | 30 (supplement 6, monograph 24) | The pinned version. In the local Pulse clone, `git diff --stat REL_4_3_1 REL_4_3_2` gives 7 files, +46 −17, as monograph L807 states. |
| File paths | 2 (supplement L972) | `audits/reproduction_2026-06-07/`, `audits/reproduction_check_2026-06-07.md` and `audits/reproduction_thinkpad_2026-06-10/` exist. |
| Three-part section pointers | 26 (monograph) | Each resolves to exactly one heading (§3.3.1, §3.4.1, §3.5.1 or §3.8.1). The words announcing each were read against its target. |
| Three-part headings | 5 (monograph) | The headings themselves, L1801, L2002, L2267, L2655 and L2993. |
| Code fence | 3 (monograph L1425–L1431) | "thresholds locked per §2.6" lands on "### 2.6 Detector". `csv_path`, `pulse_log` and `exit_code` match `classify()` in `src/detector.py` (L432–436). "5 s-sampled" is the CSV interval of `preregistration.md` (L58, L84). `exit_code=0` is an argument value. |
| DOIs | 84 (42 link texts + 42 link targets, monograph) | 23 DOI links on 23 lines, for 22 reference entries. Every link text equals its target, and 22 equal the `doi` of their `references.bib` entry. The 23rd is Morris 1991's second DOI, `10.1080/00401706.1991.10484804`, which the bib does not carry. Crossref gives it as Morris, "Factorial Sampling Plans for Preliminary Computational Experiments", Technometrics 33(2):161–174. The doi.org handle record of the bib's `10.2307/1269043` lists it as its `HS_ALIAS`. One article under two DOIs, not a defect. |
| Source line references | 11 (monograph) | Pulse `REL_4_3_1` in the local clone (`git show REL_4_3_1:…`). `SEMechanicalVentilatorVolumeControl.cpp` L120–128, inside `ToSettings` (L64): the respiratory-model trigger is switched off, then on when neither trigger flow nor trigger pressure is set. `MechanicalVentilatorModel.cpp` L810–818: with that trigger on, a `StartOfInhale` event cycles the ventilator. `SetupPatient.cpp`: L41–64 age gate, L179–200 BMI bounds, L534 `65.6 * pow(weight_kg, 1.02)`. The supplement's `lines 120--128` (L721), read in §2.1 as a non-quantity, holds on the same source. |
| Preregistration line range | 2 (monograph L714) | **MK-M1**, below. |

**Finding.**
- **MK-M1 — `manuscript.md` L713–714.**
  - It read: *"(`preregistration.md`, erratum of 2026-05-19, lines 9–34)"*.
  - The erratum is the blockquote on lines 9–36 of `preregistration.md`. Line
    34 ends mid-sentence ("… Appendix B.5. The"), and lines 35–36 finish it
    ("original wording below is preserved verbatim for preregistration
    integrity.").
  - The extent was the same at `219a13a` (2026-07-25), the commit that
    introduced the pointer. `git blame` gives lines 30–36 to `2487cf7`
    (2026-05-19), which wrote the erratum.
  - The paper, the supplement and `README.md` carry no line range for it.
  - ✅ **Corrected as a mechanical pointer fix** (precedent YL-M2): it now reads
    "lines 9–36".
  - Guarded in `check_monograph_number_audit`, 66 → 68 checks. The text check
    requires the new range and bans the old one. A second check re-reads the
    erratum's extent in `preregistration.md` (read only) and compares it with the
    cited range.
  - Reinjection of the previous monograph: 3 FAIL (extent, required, banned),
    MD5 restored.
  - Monograph rebuilt, 121 pages. Rendered PDF: new range 1, old 0. DOCX: new 1,
    old 0. `check_render.py` PASSED (1 accepted residue, 0 new).
  - ⚠️ `pdftotext` wrote this en dash as the byte 0xAD, so a UTF-8 "9–36"
    pattern returned 0 for the new range **and** the old one. The count was
    redone byte-wise, with "lines 9.3x" as a positive control (1 hit).

**Movement.**
- Inventory: 39 probes, 0 FAIL.
- `inventory.csv` is unchanged, so no bucket moves.
- `masked_by_rule.csv`: the L714 row's literal is now 36 instead of 34.
- Guard-pinned literals: 1,042 → 1,047.

## 9. Numbers written in words, read one by one — 1,350 tokens (2026-09-15)

**Why.** The digit inventory's unit is a run of digits (§1). A number written
in words never entered any bucket, residue or mask. Three defects already
corrected in this audit had that shape: MF-7 "eleven", MF-20 "three of the four
pairs" and F-S3 "three of the eight". Each was found only because it sat in a
sentence being read for a digit. The author decided on 2026-09-15 to read them
all.

**Population, fixed before counting** (producer docstring).
- **Words counted**, case-insensitive, whole word:
  - cardinals: zero to nineteen, the tens, hundred(s), thousand(s), million(s),
    billion(s); a hyphenated compound such as "twenty-four" is one token;
  - ordinals: first to twentieth, the tens, hundredth, thousandth, and plural
    fractions ("thirds"). "second" is kept even as a unit of time; reading
    decides;
  - multiplicatives: half, twice, thrice, double, triple, quadruple, dozen,
    quarter and their inflections; a number word glued to "fold"; a hyphenated
    fraction ("two-thirds"). Each is one token, never also counted as its
    cardinal.
- **Excluded, stated so the boundary is explicit:** quantifiers and determiners
  (no, none, both, all, each, every, several, few, many, most, single, sole,
  once, pair).
- **Masks:** the digit inventory's own `mask_out`, reused unchanged. Every
  masked token is written to `number_words_masked.csv`, and the books close per
  artefact (raw = kept + masked).
- **Counts at read time** (`number_words_summary.json`, unit = one token):

  | artefact | raw | kept | masked | lines with a kept token | cardinal / ordinal / multiplicative |
  |---|---:|---:|---:|---:|---|
  | paper | 238 | 233 | 5 (comments) | 65 | 195 / 33 / 5 |
  | supplement | 565 | 559 | 6 (comments) | 180 | 465 / 83 / 11 |
  | monograph | 547 | 546 | 1 (code fence) | 476 | 468 / 65 / 13 |
  | **all** | **1,350** | **1,338** | **12** | **721** | **1,128 / 181 / 29** |

  After W-M2 (below), the monograph reads 470 / 65 / 11; the totals do not
  move.

**Instrument.**
- **`scripts/audit_number_words.py`** (versioned) writes `number_words.csv`,
  `number_words_masked.csv` and `number_words_summary.json`. Calibration: 19
  probes, 0 FAIL.
  - They cover recall (the MF-7 and MF-20 shapes, "top-three", raw LaTeX blocks,
    text after `\%`) and precision ("someone", "alone", "tone", comments, inline
    code, link targets, `\label` and `\cite` arguments, "S1_two_cells").
  - They also cover single-token forms (five-fold, twenty-four, two-thirds) and
    the line number after a masked comment.
- **The calibration caught a defect in my own first version.** The pattern
  refused a word preceded by a hyphen, so "120-second" was missing, and
  "top-three" would have been dropped silently with it.
  - Fixed, then reinjected: 2 FAIL (top-three, 120-second), MD5 restored.
  - ⚠️ The first reinjection, by `sed`, did not apply; the line was unchanged
    and the probes passed on an unmodified file. It was caught by printing the
    line and redone with the exact editor.
- **`mask_out` gained a `token_rx` parameter**, defaulting to the numeric
  literal, so both instruments apply the same masks. The digit inventory
  re-ran byte-identical: MD5 of its four outputs unchanged, 39 probes, 0 FAIL.
- **Reading** (scratchpad, session `04199c63`).
  - `nw_worksheet.py` prints each source line holding a kept token, with its
    tokens.
  - Every line of the three worksheets was read: 65 + 180 + 476.
  - Claims that needed more than their own sentence were re-derived by
    `nw_verify_paper.py`, `nw_verify_supp.py`, `nw_verify_supp2.py`,
    `nw_verify_mono.py` and `nw_condense_len.py`.
  - ⚠️ **No per-token verdict table was kept**, unlike §7 and §8. Most tokens
    count a list given in the same sentence ("Seven … inputs" followed by the
    seven) or a design constant (7 inputs, 6 outputs, 4 scenarios, 2 bodies, 8
    cells, 4 flags). Those were checked in place and are not listed one by one.

**What the other claims were checked against** (loci are source lines at read
time).
- **Artefacts.**
  - `sobol_ci_buckets.csv` / `SEEDS`: five seeds; the stable 23 span all seven
    inputs, all four scenarios and 17 combinations.
  - Pair counts over the 144: median 7, 25 at three or fewer, 9 single-pair
    (only Vt in S1_F and FiO2 in S4_M), five of them rank 1.
  - `sobol_promotion.csv`: 72 fires, 43 combinations, eight cells, three to six
    promoted inputs per cell.
  - `morris_indices.parquet`: twelve single-pair entries.
  - `s034/`: FiO2 estimable and rank 1 for PaO2 and SpO2 in S1_M, S1_F, S4_F
    under the relaxed screen; 30 / 19 / 15; median third-to-fourth gap 39 %,
    one gap below 10 %; S2_M 6 / 2 / 2.
  - Seed-44 comparison: rank 1 in six of six, set in four, order in three.
  - S021 `plateau_stats`: six runaways above 760 mmHg, three drift-converged;
    three converged above 1,400; 37 converged below 700. By Vt level: six of 20
    at 633.3 mL, none of the 24 at the other three. Five of the six at RR = 20,
    with three non-runaways at the same level. Female 5 of 5, male 1 of 5 in
    the five RR ≥ 16 pairs.
  - H4: six raw, five BH survivors, two empirical p = 0; Spearman CI including
    zero only for S2 Vt.
  - `s032/`: shortened DBP steps five, one and three; eight of 140 SBP steps;
    three evaluable transitions, the contaminated median higher in each.
    SBP rank 1 for MAP in all eight cells under the nominal, uncontaminated,
    paired, hybrid and matched-combined columns, and derived for applied-step.
    DBP runner-up in all eight under the hybrid combined estimator.
  - S014: seven of eight cells (S3_M none); S1 26, S2 19. S4_F_0003 and
    S4_F_0089 tie on distance to the median pre-lock CV; the id breaks the tie.
  - S018 at both levels: 12 clean (the same 12), 8 flagged, one implausible
    (S1_M_0159), seven SpO2 flatline, three of those also on PaO2 drift, Vt CV
    three (bracket) and four (floor), FiO2 0.737 three times and 1.0 five
    times. The four S4_M-only divergent inputs run clean at both.
  - F-003 reclassification: 21 S1_F + 11 S1_M; the remaining two are both
    healthy-female.
  - Traffic light: red HR and PaO2 in four cells each, MAP and PaCO2 only in
    S4_M; green 4 in S2_F and 3 in S3_F; only S2_F and S3_F carry no hard flag.
  - Retention table, continuous-severity bins (31 + 19 = 50 per sex), Cornish
    Table S7 (eight unassessed channels, 80 rejections), SHAP (9 sets against
    25; MAP, PaCO2, SpO2 invariant), S033 summary (ten below the cut, nine of
    them constant).
  - `sha_compare.json`: DIFFERS, ASYMMETRY and both MISSING counters 0.
- **Pulse `REL_4_3_1` source.**
  - `SetupPatient.cpp` builds ten "allowed is" rejection strings. Nine write
    the unit after the value; the heart-rate lower bound (L311) is the sole
    exception.
  - BMR consumers: see W-S3.
  - At `REL_4_3_2` the tree has zero "surfactant", "surface tension",
    "derecruit", "alveolar stability" and "opening/closing pressure" matches.
- **Registers and records.**
  - `preregistration.md`: H1–H4 (L74–77) and the five pilot gates.
  - `audit/pulse_sex_conditioned_parameters.md`: seven flow fractions, thirteen
    tissue masses, ten normalised masses.
  - `reference_audit.md` (webb2020) and the `paper.bib` note (Ward 2024,
    six-setting action vector, full text read 2026-08-10).
  - S006 (workers three to two); the phase-4a log ("23h01m12s") and
    `reproduction_check_2026-06-07.md` ("23h01m21s").
  - `audits/reproduction_2026-06-07/README.md` (AMD Ryzen 5 PRO 4650U).
  - S014 (RR alternating 20 and ~46).
  - Monograph reference list: nine authors (Bray 2019), seven (Webb 2022).
  - Ledger anchors for "the same seven green / twelve red".

**Not verified here.**
- DBP as runner-up under the matched-combined estimator: no artefact records
  that ranking.
- "Stable across three independent forest seeds" (supplement L1030): the
  artefact holds one seed; the record is the `5a6b201` commit message.
- "Two to three smaller assist breaths" (monograph L2938): S014 records the
  ~46-per-minute assist rate, not the count.
- The content of the eleven LaTeX-comment tokens, which do not render.

**Findings.**
- **W-P1 — `paper.tex` L232 and monograph L2689–2690. ✅ Corrected on the author's decision (resolution below).**
  - The text says "nine of the sixteen values below fall on an exact rounding
    tie".
  - With the 16 counts k, each percentage is 0.625k. Ties at one decimal
    (k ≡ 2 mod 4): 4. At two decimals (k odd): 5. At the integer (k ≡ 4 mod 8):
    4.
  - `baad15f` (2026-08-05) wrote "at one or two decimals", and 4 + 5 = 9 was
    true. The legend compression `7e1a1ff` (2026-09-02) dropped that qualifier.
  - Without it, "nine" is not determined: 4, 4 or 5 at any single precision,
    13 across all three. The monograph sentence never carried the qualifier.
  - The ledger's code comment said "multiple of 0.125". That was corrected in
    the manuscripts by `bfc3de5` but not in the comment; the comment is now
    corrected (a comment, no claim).
- **W-P2 — `paper.tex` L391 (AI disclosure). ✅ Corrected on the author's decision (resolution below).**
  - The text says the condensation pass rewrote the "Introduction, Results,
    Discussion, Methods, figure legends and abstract … to about half their
    length".
  - Measured from `f2ac374` to `e361c2a` with two instruments:
    - instrument 1 (prose tokens, floats removed, captions apart): abstract 154
      → 154 (1.00); legends 0.73; Introduction 0.55; Results 0.35; Discussion
      0.52; Methods without the AI section 0.54; total 13,676 → 6,834 (0.50);
    - instrument 2 (`wc -w` by line range): abstract 143 → 143; Introduction,
      Discussion and Methods 0.52–0.55; Results 0.52 with its tables; captions
      0.73.
  - Taken together the parts halve. Taken one by one, the abstract (already at
    the 150-word cap) and the legends do not.
- **W-S2 — supplement L1004. ✅ Corrected on the author's decision (resolution below).**
  - "Two limits … The surrogate … carries no out-of-sample evaluation, so its
    predictive accuracy is not established here" is followed by the
    subsection `sec:s13-oos`, which computes two out-of-sample estimates.
  - Both came in the same commit, `5a6b201`.
  - Reading A: "here" means this paragraph's SHAP fit. Reading B: a
    contradiction.
- **W-S3 — supplement L844. ✅ Corrected on the author's decision (resolution below).**
  - The text says "three of the four runtime consumers of basal metabolic rate
    combine it as a ratio of total to basal metabolic rate that equals one at
    rest".
  - In `REL_4_3_1`, `RespiratoryModel.cpp` L4894 and `CardiovascularModel.cpp`
    L2558 form that ratio. `EndocrineModel.cpp` L164 instead tests
    `currentMetabolicRate_W > basalMetabolicRate_W`, which is false at rest.
  - The sex term drops out of all three, but "as a ratio" holds for two. The
    register's §D says the same.
- **W-M1 — monograph L3551. ✅ Corrected on the author's decision (resolution below).**
  - Recommendation 1 says "instead of pattern-matching the four-pattern regex
    set. Anchored in the atlas's `src/detector.py` clamp-pattern catalogue".
  - That catalogue holds five patterns since the 2026-07-26 patch. `1865fd4`
    separated the published four-pattern set from the patched five-pattern one
    elsewhere but not here; the sentence dates from `28ef9a7` (2026-06-15).
  - The supplement's copy (L861) names no count. Reading A: the sweep's
    historical set, still four. Reading B: the current catalogue, five.
- **W-M2 — monograph L1512–1514 and L2372–2373. ✅ Corrected (mechanical).**
  - The permutation null was described as splitting the pooled runs "into
    halves the same size as the original M and F groups" and "into halves of
    the original sizes".
  - `src/analysis_compare.py` L72–73 shuffles and cuts at `n_m` (for example
    49 against 42), so the groups are not halves, and the sentence contradicted
    its own qualifier. It now reads "two groups". The paper already said "at
    the two original group sizes".
  - Guarded (69 → 71 checks). Reinjection: 3 FAIL, MD5 restored.
  - Monograph rebuilt, 121 pages. PDF: both new wordings 1, "halves" 0. DOCX:
    new 1, "halves" 0. `check_render.py` PASSED (1 accepted residue, 0 new).

**Resolution of W-P1, W-P2, W-S2, W-S3 and W-M1 (2026-09-15, author's
decisions).**
- **⚠️ My first W-P2 proposal was wrong, and the re-verification the author
  asked for caught it before anything was edited.** It put the Results among
  the parts "rewritten to about half their length", against my own 0.35. A
  second float-removing instrument (`nw_results_len.py`) gave 4,653 → 1,583
  words (0.34). The first awk version of that instrument removed nothing and
  was discarded. The corrected wording was put to the author again.
- **⚠️ Precision found in the double-check after the push (2026-09-15).**
  - The applied W-P2 wording rests on the Methods WITHOUT the "Use of AI tools"
    subsection, which the pass did not shorten (383 → 383 raw words; 384 → 384
    tokens). That exclusion was stated here but not in the question put to the
    author, nor in the `c3aeb0f` commit message ("Methods 0.54").
  - With that subsection, Methods go from 3,679 to 2,177 raw words (0.59;
    instrument 1: 3,762 → 2,212, 0.588). Without it: 3,296 → 1,794 (0.54;
    instrument 1: 0.541). Line ranges: L398–L457 / L458–L474 at `f2ac374`, and
    L343–L390 / L391–L407 at `e361c2a`.
  - ⚠️ `nw_results_len.py` gave an AI subsection of 791 words. That value is
    wrong: the script ended the subsection at the first line *starting* with
    `\bmhead`, but the first one is
    `\hypertarget{tgt:data-avail}{}\bmhead{Data availability}`, so it also
    swallowed Data and Code availability. Its Results figure (0.34) is not
    affected, and the 791 was never used.
  - Brought back to the author, who chose to state the scope.
  - The paper now reads "the Introduction, the Discussion and the Methods other
    than this disclosure were rewritten to about half their length" (0.55,
    0.52, 0.54).
  - The guard requires the new wording and bans "the Introduction, Discussion
    and Methods were rewritten" (79 checks). Reinjection: 2 FAIL, MD5 restored.
  - Paper rebuilt, 25 pages. PDF and DOCX: new wording 1, old 0.
    `check_render.py` PASSED. No number word added (1,345 kept).
- **Applied wordings.**
  - W-P1, paper: "… fall on an exact rounding tie at one or two decimals, and
    their last digit would be set by a convention …". Monograph: "… fall on an
    exact rounding tie at one or two decimals." (kept on one line, so no
    monograph line number moves).
  - W-P2, paper: "… the Introduction, Discussion and Methods were rewritten to
    about half their length and the Results to about a third, the figure
    legends were shortened by about a quarter and the abstract was revised
    within its 150-word cap, with the displaced material migrated …".
  - W-S2, supplement: "The surrogate is fitted on all of the clean subset, so
    its training fit says nothing about predictive accuracy; out-of-sample
    estimates follow in §S13.4; and the comparison is of selected inputs, not
    of their order." (`\S\ref{sec:s13-oos}`, which renders as §S13.4 in the
    PDF.)
  - W-S3, supplement: "… cancel the sex term exactly at rest, where total
    metabolic rate equals basal --- two divide one by the other, and the third
    acts only when total exceeds basal."
    - The approved text had a colon. A dash was used because the sentence
      already carries one (presentation; the alternative, a second colon, was
      rejected).
    - The condition "at rest" is kept as it was. The sex-conditioned register
      notes that TMR = BMR is presumed, not verified on artefact, for the
      hypothermia branch.
  - W-M1, monograph: "… instead of pattern-matching the regex set documented in
    §2.6." §2.6 documents both the four-pattern set used by the sweep and the
    five-pattern patch.
- **Scope checked before editing.** `git grep` outside `audit/`,
  `experiments_log/` and `results/` found no other public copy of any of the
  five sentences.
  - Two dated notes in `preprint_npj/paper_to_monograph_map.md` (L81, L149)
    mention the rounding ties. They are working notes, not public, and are left
    as written.
- **Guarded** in `check_monograph_number_audit`, 71 → 79 checks:
  - six required wordings, and the replaced ones banned in the paper, the
    supplement and the monograph;
  - a dynamic W-P1 check that recounts the ties from the sixteen ledger
    retention counts (4 at one decimal + 5 at two = 9) and requires the
    qualified sentence in both documents.
  - Reinjection of the three previous manuscripts: 10 FAIL, MD5 restored.
- **Not dynamically guarded:** the W-P2 ratios. They come from two historical
  commits, which a shallow CI checkout cannot read. The W-S3 source lines are
  outside this repository.
- **Built.** Paper 25 pages, supplement 63 pages, monograph 122 pages (121
  before: the added words move a page break; the extra page is ordinary text,
  and pages 49–51, 54 and 75 are figure or table pages).
  - Every new wording is present once, and every replaced one absent, in the
    three PDFs and the three DOCX.
  - `check_render.py` PASSED (1 accepted residue, 0 new).
- **The corrections themselves add seven number words** (paper 4, supplement 2,
  monograph 1). Each was checked: "one or two decimals", "a third" (0.34–0.35),
  "a quarter" (0.73), "two … one … the third" (Pulse source), and the "§2.6"
  pointer (the Detector section).

**Observations** (no correction proposed unless the author asks).
- **O-P3** (paper L408, supplement L968) "three derived Hypothesis-4
  statistics". The reproduction record says exactly that, but its table lists
  three files and four distinct columns (three Wasserstein columns at 2.8e-14,
  `spearman_p` at 9.7e-17).
- **O-S1** (supplement L462, L562) "the four scenario impairment fractions were
  assigned by forward calibration" / "four discrete scenario calibration
  points". Only S2–S4 were calibrated against Berlin bands; S1 = 0 is the
  healthy baseline.
- **O-S2** (supplement L968, L970, L976) "five run-level flags" / "five-flag
  concordance" counts `clean` as a fifth flag, against "four flags" everywhere
  else. The reproduction records use five.
- **O-S3** (supplement L523, monograph L4452) "zero … Laplace": one match in the
  tree, inside the third-party binary `src/java/jar/commons-math3-3.6.1.jar`;
  zero in text files.
- **O-S4** (supplement L265, monograph L1256, L2462) "one alveolar-ventilation
  step … per minute" has no defined quantity to check it against. The
  `west2020respiratory` citation without a chapter is already listed as
  outstanding in the monograph's reference list.
- **O-S5, found in passing** (supplement L357 "the only preregistration
  amendment (2026-04-22-b …)"; monograph L1152–1153 "only one amendment").
  `preregistration.md` records two 2026-04-22 amendments, a 2026-05-21
  documentation amendment and a 2026-08-04 post hoc deviation record. Read as
  "the only threshold amendment", both are true; read literally, the
  supplement's is not.
- **O-M1, found in passing** (monograph L59, L60, L195, L198, L1814, L2570,
  L2604, L2649, L2653, L2673): "48 cells" for the 48 cell × output combinations,
  while the monograph's own notation table defines a cell as a (scenario, sex)
  slice, of which there are eight.
- **O-M4** (monograph L1880) "occasional further cells appearing in individual
  draws but none surviving all five": one further dominant-input cell (S3_F,
  PaO2 ← FiO2) clears 0.6 in two of five seeds.
- **O-M5, found in passing** (monograph L3472): "reported in supplementary
  section S11" names section S11 of `preprint/supplementary.md` (the SHAP
  cross-check is its S11), while L674 and L4265 name "Supplementary §S13" of the
  *npj* SI for the same analysis. Both pointers land. Two documents with
  different numbering are cited for one analysis without saying which is which
  at L3472.
- **O-D1, found while checking these corrections in the Word twins. ✅ Fixed
  (converter and guard; resolution at the end of this item). A rendering
  defect, not a claim.**
  - In both *npj* DOCX files, a `\S\ref{…}` to a supplement section prints
    nothing. Examples: the supplement DOCX reads "sample-dependent ()" where the
    PDF reads "(§S3.13)"; the paper DOCX reads "tables are in Supplement and ."
    where the PDF reads "§S3.1 and §S3.2".
  - `scripts/tex_to_docx.py` `resolve_refs` replaces `\ref{…}` by the number
    from the `.aux`. A supplement number begins with "S", so `\S\ref{sec:s3-…}`
    becomes `\SS3.13`, which pandoc reads as an unknown command. That mechanism
    is inferred from the output and not yet reproduced.
  - References to paper sections ("Methods §4.4") print correctly. The source
    holds 28 `\S\ref{` in the paper and 46 in the supplement, of all targets.
  - The `\S\,\ref{` form (34 and 14) separates the two tokens.
  - **Resolution.**
    - Mechanism reproduced on a minimal file with the build's pandoc 3.9.0.2:
      `(\SS3.13)` → "()"; `(\S{}S3.13)` → "(§S3.13)"; `(\S4.4)` → "(§4.4)".
    - `resolve_refs` now writes `\S{}` before a `\ref`-family command. The
      empty group ends the control word without adding a space.
    - `scripts/check_docx_structure.py` gained a section-sign check. For every
      `\S\ref`, `\S\,\ref` or `\S~\ref` in the source, it resolves the label in
      the build's `.aux` and requires "§" + that number at least as many times
      in the DOCX text.
      - Calibrated on the defective build before rebuilding: FAIL, with 2
        numbers short in the paper twin and 30 in the supplement twin.
      - After the rebuild: 0 and 0.
      - Limit: the count is per number, so a number printed elsewhere can mask
        one lost call site.
      - ⚠️ Its first version skipped a label missing from the `.aux`, so a
        build without its `.aux` would have passed with nothing checked. Found
        in the double-check the same day. An unresolved label now fails.
        Calibrated by moving both `.aux` files out of the build directory: 122
        problems (62 + 60 unresolved); files restored: PASS.
    - Measured on the twins: accolated "§S" references went from 0 to 3 (paper)
      and from 0 to 46 (supplement). A word-level diff of the DOCX text before
      and after shows only those numbers replacing the empty "()" or "."; the
      spaced `§ S…` form was never affected.
    - PDFs unchanged in content: 25 and 63 pages.
    - ⚠️ The four supervisors received `.pdf` and `.docx` on 2026-09-05, 22:08
      (`preprint_npj/dispatch_log.md` L571–L590, source commit `0f275e0`). At
      that commit the converter had no such fix, and `supplement.tex` carried
      `\S\ref{sec:s…` on 29 lines. Their Word copies therefore most likely lack
      these numbers. The dispatched files themselves were not re-read; only
      their hashes are recorded.

**Code comments corrected in the same pass** (no claim, no output change):
- `scripts/s032_uncontaminated_step_analysis.py` said "eight" S3.7 counts in
  three comments, while its `CALIBRATION` gate has held nine since it was
  written (`9c5cc50`). The monograph's "nine S3.7 counts" (L972) is right.
- The ledger comment of W-P1.

**Movement.**
- Digit inventory: 39 probes, 0 FAIL, `summary.json` unchanged; one
  `inventory.csv` context string moves.
- Number-word inventory: 1,338 kept and 12 masked before and after W-M2; the
  monograph's classes move as stated above.
- After the five resolutions:
  - Number words: 1,345 kept (paper 237, supplement 561, monograph 547), 12
    masked.
  - Digit inventory: 5,786 retained (paper 528, monograph 3,371). The additions
    are "150" of the 150-word cap and the "2.6" of §2.6.
  - Guard-pinned literals 1,047 → 1,049. Calibrations 39 / 0 and 19 / 0.

**Addendum 2026-09-15 (evening) — four number words added with the
synthetic-data framing.** On the author's decision of 2026-09-15, seven
sentences were added to `paper.tex` (Introduction, Discussion) with four new
references. They carry no digit and four number words, each read against its
source:
- "a five-stage validation scheme": Victoriano et al. 2026, Fig. 4, names five
  stages (internal plausibility, downstream task utility, OOD generalization,
  sim2real transfer, biological or clinical coupling). Full text read. Correct.
- "only part of the first stage": stage 1 of that figure is internal
  plausibility. The claim is restricted to part of it because stage 1 also
  covers fidelity to real-world distributions, which the atlas does not test.
  Correct.
- "with one difference": the sentence states exactly one difference (the
  classifier checks the simulator's behaviour, not agreement with patients).
  Correct.
- "one sim-to-real study": a single study is cited (`hwang2025sim2real`).
  Correct.

**Movement.**
- Number words: 1,349 kept (paper 241, supplement 561, monograph 547), 12
  masked. The paper's rows for "four-flag" and "doubles" change only their
  context string.
- Digit inventory: 5,786 retained (paper 528, supplement 1,887, monograph
  3,371), unchanged. With the line field removed, `inventory.csv` is
  row-for-row identical to the previous commit, and so is `masked_by_rule.csv`
  once each pair is matched on literal and context: the paragraph split shifts
  later paper lines by two. `summary.json` moves only the paper's `excluded`
  span count for `ref_or_machinery`, 219 → 227: the eight new `\cite`
  commands. Its literal cost for the paper stays at 4, since a year glued to
  letters inside a key is not a numeric literal, so no row joins
  `masked_by_rule.csv`.
- Calibrations 39 / 0 and 19 / 0.

## 10. What remains

| artefact | `none` residue | `ambiguous_small` | status |
|---|---:|---:|---|
| paper | 37 / 29 (43 / 31 when read) | 307 | **both read row by row** (§3, §3.2). `none`: no defect. `ambiguous_small`: 57 not quantities, 248 + 2 verified, **1 wording finding, corrected** (L259, author's choice, guarded). **`guard` and `ledger` read one by one** (§6): 183 occurrences, 16 of them a different quantity, all verified, no defect. **Year-like and masked literals read** (§7: 4; §8: 40), no defect |
| supplement | 431 / 218 (456 when read) | 957 | **`none` read row by row** (§4.1): 6 not quantities, 450 verified; **all six findings corrected** on the author's decisions (F-S1 to F-S6, 2026-09-14). **`ambiguous_small` read row by row** (§4.2): 134 not quantities, 823 verified; **3 findings, 1 mechanical pointer and prose-sweep #15 all corrected** on the author's decisions (2026-09-14), guarded (22 checks). Counts now 411 / 960 (432 → 411 is by value only: §5 Resolution, §6 GL-S2). **`guard` and `ledger` read one by one** (§6): 515 occurrences, 122 a different quantity; **GL-S1 corrected** (mechanical pointer, guarded), **GL-S2 corrected** (author's decision, 2026-09-15, guarded). **Year-like and masked literals read** (§7: 18; §8: 77, the five chapter locators re-opened in the cited editions), no defect |
| monograph | 803 / 344 when read; 794 / 334 after the corrections | 1864 when read; 1878 after | **both read row by row, plus the 89 inline-code literals** (§5); section pointers and "Cited in §X" checked. **19 findings (MF-1 … MF-21, MF-8 merged, MF-10 downgraded) and 11 observations. All 19 findings, O-3/5/7/8/9/10/11 and the Cornish citation corrected 2026-09-14** (author's decisions, or mechanical under the pact), guarded (63 checks, one of them GL-S1's; 66 after GL-S2 and YL-M2). O-1 not selected, O-4 not to be edited. MF-22 (HR anchors against Ostchega 2011), found during the resolution, removed on the author's decision, together with a precision on MF-20. Quantities against non-quantities not counted: the rule-based split failed its precision pass. **`guard` and `ledger` read one by one** (§6): 698 occurrences, 126 a different quantity, all verified, no defect. **Year-like literals read one by one** (§7): 153 occurrences; **YL-M2 corrected** (mechanical pointer, guarded), **YL-M1 corrected** (title-page date = revision date, author's decision, guarded). **Masked literals read one by one** (§8): 166 occurrences; **MK-M1 corrected** (line-range pointer, mechanical, guarded; the guard has 68 checks after MK-M1, 69 after YL-M1). **Numbers written in words read** (§9, all three artefacts: 233 / 559 / 546 kept when read, 12 masked): **W-M2 corrected** (mechanical), **W-P1, W-P2, W-S2, W-S3 and W-M1 corrected on the author's decisions**, all guarded (79 checks); monograph 122 pages. O-D1 (supplement section numbers missing from both DOCX twins) fixed in the converter and guarded. Prose without numbers not audited |

⚠️ **No count in this register may come from an ad-hoc pipeline.** Three
successive `grep | cut | uniq` passes over `inventory.csv` each miscounted the
supplement's residue, because the `context` column carries commas. Every figure
above was read from the producer's own output.

The monograph is Markdown, so a LaTeX pattern returns zero on it by construction
(`1{,}280` against `1,280`); any hand search must test both syntaxes.

**Year-like literals: read one by one** (§7, 175 occurrences). YL-M2 is
corrected, and **YL-M1**, the monograph's title-page date, is corrected on the
author's decision.

**Masked literals: read one by one** (§8, 283 occurrences). MK-M1 is corrected.
With §2.1, §5 and §7, all 566 rows of `masked_by_rule.csv` have now been read:
`summary.json` gives 51 + 85 + 255 = 391 literals removed by masks, plus
4 + 18 + 153 = 175 year-like.

**Numbers written in words: read** (§9, 1,350 tokens, second producer
`scripts/audit_number_words.py`). W-M2 is corrected as mechanical; W-P1, W-P2,
W-S2, W-S3 and W-M1 are corrected on the author's decisions. **O-D1**, the
supplement section numbers missing from both DOCX twins, is fixed in
`scripts/tex_to_docx.py` and guarded in `scripts/check_docx_structure.py`.

**Still unread, in all three artefacts (2026-09-15):**
- **prose that carries no number.** Quantifiers ("only", "none", "both", "all")
  are part of it: O-S5 and O-M1 were found in passing, not by enumeration.

## 11. What this register does not claim

It does not claim the published numbers are correct. It claims that the
population is defined; that the instrument is calibrated in both directions,
with every known defect reinjected and caught; that the paper's `none` residue
has been examined row by row; and that nothing in that residue is a defect. The
paper's `ambiguous_small` residue has also been read row by row (§3.2). Every
quantity in it was checked against a named source. One sentence carried a
correct number under a wrong label, and it was corrected on the author's
decision. The paper's `guard` and `ledger` occurrences were then read one by one
(§6) and carry no defect. The supplement's `none` residue has been
read row by row (§4.1). It carried six findings, one of which (F-S5) moved
a band edge that the paper also states; all six are corrected on the author's
decisions. The supplement's `ambiguous_small` residue has been read row by row
(§4.2): three findings, one wrong pointer and one loose bound were found, and
all are corrected on the author's decisions and guarded. Its `guard` and
`ledger` occurrences were then read one by one (§6): one wrong pointer (GL-S1)
is corrected and guarded, and one resample-count statement that the versioned
generator does not reproduce (GL-S2) is restated to the measurement on the
author's decision.
The monograph's `none` and `ambiguous_small` residues and its 89 inline-code
literals have been read row by row (§5). Nineteen findings and eleven
observations are recorded there. All nineteen findings, seven observations and
the Cornish citation are corrected, on the author's decisions or as mechanical
fixes, and guarded. A twentieth finding, MF-22, came up while resolving MF-5; it
is corrected too. The monograph's `guard` and `ledger` occurrences were then
read one by one (§6) and carry no defect. Its sentences that carry no number
are not audited: three such defects (MF-18, MF-20, MF-21)
were found in passing, so its prose is not claimed clean.

The year-like literals were then read one by one (§7). One date pointer is
corrected, and the monograph's title-page date is corrected on the author's
decision. The other
masked literals were then read one by one (§8), and one line-range pointer is
corrected. The content of the LaTeX comments, which does not render, was not
verified.

The numbers written in words were then read line by line (§9). Six wordings are
corrected (one mechanical, five on the author's decisions), and no per-token
verdict table was kept for that population. The Word twins were checked for the corrected
wordings and, after O-D1, for section-sign references; nothing else in them was
compared number by number with the PDFs.

Nor does it claim anything about prose without numbers, quantifiers included,
listed at the end of §10: it has not been read.
