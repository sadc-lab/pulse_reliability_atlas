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
| paper | 525 | 142 | 159 | 18 | 305 | **43** | 31 |
| supplement | 1846 | 478 | 419 | 31 | 940 | **456** | 214 |
| monograph | 3339 | 560 | 606 | 28 | 1859 | **846** | 348 |
| **all** | **5710** | **722** | | | **3104** | **1345** | **432** |

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
| paper | 580 | 51 | 529 | yes |
| supplement | 1948 | 86 | 1862 | yes |
| monograph | 3745 | 255 | 3490 | yes |

Literals removed per rule now: paper — comments 27, typesetting lengths 11
(all `\textwidth` fractions and `[-0.6em]` spacings, read), product versions 7,
machinery 4, organisation identifiers 2. Supplement — machinery 54, comments 12,
versions 7, typesetting lengths 6 (all column widths, read), line references 2
(`lines 120--128`, read). Monograph — inline code 89, versions 55, link targets
42, URLs 42, line references 13, product versions 7, code fences 3.

⚠️ **Open:** inline code still costs the monograph 89 literals, some of them
real values rendered in backticks (`[0.879, 0.945]`, `0.02`, `0.425`). To be
settled when the monograph is worked.

### 2.2 Defects found in this instrument, and what each one cost

Recorded in order, because each was a false negative on risk and several were
found only by reading, not by any check.

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
verified one by one. The paper is not closed.

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

## 5. What remains

| artefact | `none` residue | `ambiguous_small` | status |
|---|---:|---:|---|
| paper | 43 / 31 values | 305 | **`none` audited row by row, no defect**; small values not verified |
| supplement | 456 / 214 | 940 | characterised, four values verified, not cleared |
| monograph | 846 / 348 | 1859 | not worked; inline code still costs 89 literals |

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
paper's small values, and the supplement and monograph residues, are listed,
not cleared.
