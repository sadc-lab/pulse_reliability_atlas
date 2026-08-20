# MISMATCH — the CDC body-weight provenance correction is itself wrong

**Opened and measured 2026-08-20. Status: MEASURED — nothing modified.**
Per `CLAUDE.md`, a mismatch found during a source audit is recorded, nothing is
changed, and it returns to the author for a joint decision.

## 1. What the manuscript says

`preprint_npj/paper.tex` §4.2 and `preprint_npj/supplement.tex` §S3.4 both state:

> Both weights are CDC growth-chart 50th-percentile values **at 214 months
> (17 y 10 m)** for each sex; the corresponding CDC values **at exactly 18.0
> years are 67.64 and 56.41 kg**, 0.34 and 0.21 kg above the values used.

and the supplement adds:

> The preregistration's provenance erratum describes these weights as the CDC
> 50th-percentile values *at 18 years (216.5 months)*; **that description is
> inaccurate**. The weights in use are the 50th percentile of the
> **214–214.99-month row, two rows earlier** in the same CDC table, rounded from
> **67.28992603** and **56.22969564** kg. That off-by-two-rows lookup was
> inherited from the companion pediatric pipeline.

## 2. What the CDC data says

Source: `https://www.cdc.gov/growthcharts/data/zscore/wtage.csv`, the official
2000 CDC growth-chart weight-for-age file, downloaded 2026-08-20. Columns
resolved by NAME (`P50` is column 10; column 9 is `P25`, and reading it by
position is how a first pass here produced wrong figures).

| `Agemos` | Sex 1 (male) P50 | Sex 2 (female) P50 |
|---|---|---|
| 214.5 | 66.91783563 | 56.05304601 |
| **216.5** | **67.28992603** | **56.22969564** |
| **218.5** | **67.64281378** | **56.40963105** |

The two unrounded values the supplement attributes to the 214-month row match
`Agemos = 216.5` **exactly, to all ten digits**. The two values it calls "at
exactly 18.0 years" match `Agemos = 218.5`, also exactly.

CDC lists `Agemos` at the **midpoint of the month interval**: 216.5 covers
216.0–216.99 months, and 216.0 months is 18.00 years exactly. 218.5 covers
218.0–218.99 months, that is 18 y 2 m.

## 3. Consequence

1. **The weights in use (67.3 and 56.2 kg) ARE the CDC P50 at exactly 18.0
   years.** The preregistration's erratum, which says so, is **correct**.
2. **The supplement's correction of that erratum is wrong.** It mislabels the
   216.5 row as "214 months (17 y 10 m)" and the 218.5 row as "exactly 18.0
   years".
3. **There is no off-by-two-rows lookup in the pipeline.** The off-by-two is in
   the diagnosis. The chain follows from a single error: taking `Agemos = 218.5`
   to be the 18.0-year row. Once that is assumed, the row actually used (216.5)
   does sit two rows earlier, and gets mislabelled accordingly.
4. The manuscript therefore declares a preregistration document inaccurate when
   it was accurate, and publishes a provenance that the primary source
   contradicts.

Nothing in the simulated bodies changes: 67.3 kg / 180 cm and 56.2 kg / 163 cm
are what the preregistration names and what all 1,280 runs used. This is a
provenance statement, not a protocol deviation — the same category the
supplement itself assigns it, but pointing the other way.

## 4. Loci carrying the claim

| file | what it says |
|---|---|
| `preprint_npj/paper.tex` §4.2 | 214 months; 67.64 / 56.41 at 18.0 y; erratum names 18.0 y |
| `preprint_npj/supplement.tex` §S3.4 | the full "off-by-two-rows" account |
| `preprint/manuscript.md` | to be checked before any edit |
| `preregistration.md` erratum 2026-05-19 | states 18 years (216.5 months) — **correct, do not touch** |

## 5. How this was found, and why it had not been

The author's standing instruction is that values from the companion
`Pulse_translation_new` project are not sources, and that primary sources must be
checked directly. The erratum states in its own text that the weights were
"inherited from the companion `Pulse_translation_new` pediatric-translation
pipeline". No session had gone to the CDC file itself; `paper.bib`'s note for
`kuczmarski2002cdc` records a 2026-07-26 verification "against Tables 22 (weight)
and 23 (stature)", but that verification did not catch the age mislabelling, and
a recorded verification is a claim rather than a measurement.

## 6. Not fixed here

No manuscript file, figure, flag or number was modified. The correction touches a
scientific provenance claim and a statement about a dated preregistration
document, so it returns to the author.
