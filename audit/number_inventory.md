# Register — exhaustive inventory of the published numbers

**Opened 2026-09-13.** Producer: `scripts/audit_number_inventory.py`
(calibrated, 16 probes, 0 FAIL). Artefacts: `results/number_audit/inventory.csv`
and `summary.json`. This file carries the judgement the script cannot: what each
residual number is, and what it was checked against.

**Why.** The ledger re-derives the numbers written *into* it. A published number
that was never registered is verified by nothing, and nothing reports its
absence. On 2026-09-10 twelve values entered Supplement S8 and S13 with no
anchor and surfaced only because the maintainer asked. This register exists so
the question stops depending on someone asking.

---

## 1. The population, fixed before anything was counted

The exclusion rule is in the producer's docstring and is applied mechanically;
every exclusion is counted per artefact so the denominator is auditable rather
than trusted. Nine rules: comments, cross-reference machinery, URLs and file
paths, three-part versions, typesetting lengths, source line references,
year-like integers, organisation identifiers, product versions.

⚠️ **Rules 8 and 9 were added after the first inventory, not before it.** The
paper's residue contained `3450` ("UR 3450 DevAH"), `1256` ("INSERM UMR\_S
1256") and the model versions `4.7`, `4.8`, `5.6`. They are not quantities. The
rule was extended and the calibration extended with it, rather than the rows
being waved away one at a time.

## 2. What the instrument measures

| artefact | retained | distinct | guard | ledger | ambiguous small | none | distinct none |
|---|---:|---:|---:|---:|---:|---:|---:|
| paper | 514 | 141 | 155 | 15 | 301 | **43** | 31 |
| supplement | 1820 | 475 | 417 | 26 | 928 | **449** | 213 |
| monograph | 2945 | 457 | 543 | 13 | 1690 | **699** | 259 |
| **all** | **5279** | **638** | | | **2919** | **1191** | **350** |

⚠️ **These buckets are coverage by VALUE, not by occurrence**, and they bound
risk from below, never from above. Two known distortions, both measured rather
than suspected:

* **A bare by-value match is meaningless for a small integer.** In the first
  version, 3,764 occurrences landed in `ledger`; **3,171 of them had a value
  under 100**, median 8. A match now counts only for a distinctive literal
  (three significant digits, or ≥ 1000); the rest go to `ambiguous_small` so the
  ambiguity is visible instead of being counted as coverage.
* **A guard match was a substring test.** `"8" in guard_string` put 2,561 of the
  monograph's 2,954 occurrences in `guard` — a document the guards barely touch.
  Matching is now on digit boundaries.

And one distortion in the opposite direction, stated so a `none` row is read as
a candidate and not as an accusation: a number pinned as a Python float rather
than a quoted string is invisible to the sieve. `check_input_ranges.py` holds
the swept input bounds that way, which is why `0.21` and `110` sit in `none`
although they are gated.

## 3. The paper's residue, audited row by row — 43 occurrences, 31 values

**No defect found.** Every row falls into one of four classes.

**(i) Locked constants, derivable from `src/detector.py` or the preregistration.**
`0.05` ×4 (the CV threshold, L198/259/280/292), `0.1` and `99.9` (the flatline
tolerance, L365), `13` (samples in the window, L357), `0.21` and `110` (swept
bounds, L353, gated by `check_input_ranges.py`), `95` (bootstrap CI level),
`0.001` (the `p <` reporting convention), `14` (the exponent in $10^{-14}$).

⚠️ Note that the `0.05` at L379 is **not** the CV threshold: it is the
Benjamini–Hochberg level *q*. Same value, different quantity — a reminder in
one document of why by-value coverage proves nothing.

**(ii) Externally sourced.** `12{,}642` and `70` (the cited ventilator-sharing
study), `71` mL kg⁻¹ (cited clinical estimate), `18` and `163` (CDC P50 body
dimensions, additionally gated by `check_cdc_weight_provenance`).

**(iii) Our own measurements, traceable to an artefact.** `36`, `25`, `1{,}400`,
`37`, `84.1`, `13`, `4{,}400` ×2, `8.4`, `86`, `0.879`, `0.945` ×4, `22`, `18`,
`4.1`, `5.5`, `93`, `0.625`, `0.12`, `3{,}348`.

**(iv) Checked arithmetically in this pass**, because they are cheap to settle
and a claim that can be checked should be:

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
**3,348**. Characterised before being called a defect:

* `data/runs/` holds **exactly 3,348** — the published number.
* The 3,349th is in `data/clamp_probe/`, a probe directory that `.gitignore`
  excludes and that is not a sweep run.

**My population was wrong, not the paper's.** The claim says "all 3,348 recorded
setup logs", and the recorded setup logs are those under `data/runs/`. Recorded
because this is the fourth over-broad instrument in this work to raise a false
alarm, and the only reason it did not become a "correction" is that the
directory breakdown was looked at before the conclusion was drawn.

## 4. The supplement's residue — characterised, not cleared

449 occurrences over 213 values, and it is **concentrated**: the ten most
frequent literals account for 125 of the 449. The frequency table is written by
the producer to `results/number_audit/residue_by_literal.csv`.

The bulk belongs to the same families the paper's audit already settled — the
ARDS instability band (`0.945` ×24, `0.879` ×10), the swept input bounds
(`110` ×16, `0.21`, `0.25`, `0.20`, `0.4`), the CV threshold (`0.05` ×14), the
bootstrap level (`95` ×14), and the ledger's own head-line count (`394` ×8,
gated by `check_audit_counters`, invisible to the sieve because it is computed
rather than quoted).

The tail was inspected and classified, and four of its members were settled
arithmetically in this pass:

| claim | derivation | verdict |
|---|---|---|
| BV male `4{,}802.63` mL | 65.6 × 67.3^1.02, Pulse's own allometric relation | 4802.63 ✓ |
| BV female `3{,}996.09` mL | 65.6 × 56.2^1.02 | 3996.09 ✓ |
| sex BV gap `16.8 %` | (4802.63 − 3996.09) / 4802.63 | 16.79 ✓ |
| DBP clip ceiling `75` mmHg | 0.75 × 100, the pulse-pressure rule | 75 ✓ |

Others identified but not re-derived here: `94` (a Cornish et al. 2023
denominator, external), `96` (P/F at severity 0.95, from `results/s030_pf_by_arm.csv`),
`633.3` and `0.737` (design levels from the Morris sample), `686` (mean female
PaO₂), `6.84` (the host-suspension wall-time gap).

⚠️ **This is characterisation, not clearance.** Roughly half the occurrences map
to a settled family; the rest are identified but unverified. The supplement is
**not** closed.

## 5. What remains

| artefact | residue | status |
|---|---:|---|
| paper | 43 occurrences / 31 values | **audited row by row, no defect** |
| supplement | 449 / 213 | **characterised, four values verified, not cleared** |
| monograph | 699 / 259 | not worked |

⚠️ **A lesson about this register's own numbers.** Three successive hand-rolled
`grep | cut | uniq` passes over `inventory.csv` each miscounted the supplement's
residue — 413, then 450, against the true 449 — because the `context` column
carries commas, so field positions are not what a line-oriented tool assumes.
The frequency table is now produced by the versioned script. **No count in this
register may come from an ad-hoc pipeline.**

The supplement and the monograph are the outstanding work. Two things are worth
knowing before starting them:

* The monograph is Markdown, so a LaTeX pattern returns zero on it by
  construction (`1{,}280` against `1,280`). The producer handles this, but any
  hand search must test both syntaxes.
* The monograph's residue is the largest and it is the artefact **not** sent to
  the supervisors, so it is the lowest-urgency column — but it is public, and
  the rule that three public artefacts are three columns applies.

## 6. What this register does not claim

It does not claim the published numbers are correct. It claims that the
population is defined, that the instrument is calibrated in both directions,
that the paper's residue has been examined row by row, and that nothing in that
residue is a defect. The supplement and monograph residues are listed, not
cleared.
