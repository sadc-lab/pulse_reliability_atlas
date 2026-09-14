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

## 2. What the instrument measures

| artefact | retained | distinct | guard | ledger | ambiguous small | none | distinct none |
|---|---:|---:|---:|---:|---:|---:|---:|
| paper | 527 | 143 | 165 | 18 | 307 | **37** | 29 |
| supplement | 1873 | 484 | 456 | 32 | 956 | **429** | 217 |
| monograph | 3341 | 560 | 643 | 28 | 1864 | **806** | 344 |
| **all** | **5741** | **724** | | | **3127** | **1272** | **430** |

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
| supplement | 1977 | 86 | 1891 | yes |
| monograph | 3747 | 255 | 3492 | yes |

Literals removed per rule now: paper — comments 27, typesetting lengths 11
(all `\textwidth` fractions and `[-0.6em]` spacings, read), product versions 7,
machinery 4, organisation identifiers 2. Supplement — machinery 54, comments 12,
versions 7, typesetting lengths 6 (all column widths, read), line references 2
(`lines 120--128`, read). Monograph — inline code 89, versions 55, link targets
42, URLs 42, line references 13, product versions 7, code fences 3.

⚠️ **Open:** inline code still costs the monograph 89 literals, some of them
real values rendered in backticks (`[0.879, 0.946]` since the F-S5 correction, `0.02`, `0.425`). To be
settled when the monograph is worked.

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
- **F-S3 — L827: "three of the eight on the delivered-Vt oscillation".** The
  count is 3 at the 4,400 mL bracket and **4 at the floor**: S2_M_0119_floor
  adds Vt CV 0.071. Every other count in that paragraph holds at both levels.
  Introduced in `e93a750`; no anchor.
- **F-S4 — L815, citation mismatch (`nadler1962`): "averaging 75 in men".** Per
  the verbatim quote recorded in `reference_audit.md`, Nadler's 75 mL/kg is the
  **overall** average and 66 is the women's. This wording exists in the
  supplement only (`20ea152`). Recorded in `reference_audit.md`; nothing
  modified, as the citation-audit rule requires.
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

## 5. What remains

| artefact | `none` residue | `ambiguous_small` | status |
|---|---:|---:|---|
| paper | 37 / 29 (43 / 31 when read) | 307 | **both read row by row** (§3, §3.2). `none`: no defect. `ambiguous_small`: 57 not quantities, 248 + 2 verified, **1 wording finding, corrected** (L259, author's choice, guarded). Not closed: `guard` and `ledger` are covered by value only |
| supplement | 429 / 217 (456 when read) | 956 | **`none` read row by row** (§4.1): 6 not quantities, 450 verified; F-S5 corrected, F-S1–F-S4 and F-S6 decided by the author; `ambiguous_small` not yet read |
| monograph | 806 / 344 | 1864 | not worked; inline code still costs 89 literals |

⚠️ **No count in this register may come from an ad-hoc pipeline.** Three
successive `grep | cut | uniq` passes over `inventory.csv` each miscounted the
supplement's residue, because the `context` column carries commas. Every figure
above was read from the producer's own output.

Before working the monograph: it is Markdown, so a LaTeX pattern returns zero on
it by construction (`1{,}280` against `1,280`); any hand search must test both
syntaxes.

## 6. What this register does not claim

It does not claim the published numbers are correct. It claims that the
population is defined; that the instrument is calibrated in both directions,
with every known defect reinjected and caught; that the paper's `none` residue
has been examined row by row; and that nothing in that residue is a defect. The
paper's `ambiguous_small` residue has also been read row by row (§3.2). Every
quantity in it was checked against a named source. One sentence carried a
correct number under a wrong label, and it was corrected on the author's
decision. The paper's by-value `guard` and `ledger`
occurrences are not read one by one. The supplement's `none` residue has been
read row by row (§4.1). It carries six open findings, one of which (F-S5) moves
a band edge that the paper also states. The supplement's `ambiguous_small` and
the monograph residues are listed, not cleared.
