---
id: S032
author: santino
date: 2026-08-06
status: done
tags: [morris, pulse-pressure-clip, one-at-a-time-violation, robustness, sensitivity-estimators, transition-stratification, integrity-audit, ledger-expansion, deferred-analysis]
linked_code:
  - scripts/s032_uncontaminated_step_analysis.py
  - scripts/s032_aggregate_integrity_audit.py
  - scripts/s032_transition_stratified_analysis.py
  - scripts/audit_claims.py
  - scripts/verify.py
  - preprint_npj/paper.tex
  - preprint_npj/supplement.tex
  - preprint/manuscript.md
  - preprint_npj/paper_to_monograph_map.md
---

# S032 — Does the pulse-pressure clip hold up the SBP → MAP conclusion?

---

## Why this session happened

A reader outside the project — a friend of the maintainer, reading the preprint
casually — argued that the pulse-pressure clip invalidates the systolic and
diastolic elementary effects, and that the affected simulations should be re-run
under a different parameterisation.

The three quantities in that objection (8 contaminated systolic steps, a median
μ\* factor of 2.4, a maximum of 15.4) are **the manuscript's own numbers**, taken
from Supplement §S3.7, which already quantifies the defect and audits every
figure in it. The objection was therefore not a new discovery. It was the
disclosure working: an external reader found the weakness exactly where it had
been placed.

What §S3.7 did **not** answer is the question the objection implies, and which
nothing in the repository had ever tested:

> **Hypothesis.** The published finding that MAP is SBP-driven in every cell
> could be resting on the contaminated steps. If it is, removing them should
> change the ranking.

---

## The defect, restated precisely

Pulse enforces DBP/SBP ≤ 0.75. The atlas applies that constraint when each
config is written (`src/scenario.clip_dbp_to_pulse_constraint`), not when the
Morris sample is drawn, so the sample geometry stays intact. The price, already
published:

| quantity | value |
|---|---|
| sampled points carrying a clipped DBP | 35 / 160 |
| diastolic steps shortened | 9 / 20 |
| systolic steps on which applied DBP also moves | 8 / 20 |
| steps untouched | 123 / 140 |
| clean diastolic pairs, of which shortened | 78, of which 41 |
| clean systolic pairs, of which contaminated | 68, of which 19 |

The second row is an attenuation. The third is a genuine one-at-a-time
violation: the moving 0.75 × SBP ceiling drags the applied DBP along with SBP,
so two inputs change in a step the estimator treats as one.

### Why the proposed re-parameterisations do not exist

The reader proposed SBP + pulse pressure, MAP + pulse pressure, or a constrained
Morris sample. The first two are geometrically impossible on the preregistered
envelope, and the reason is worth recording because it will come up again in
review.

The feasible region is

```
R = { 90 ≤ SBP ≤ 120,  60 ≤ DBP ≤ 80,  DBP ≤ 0.75·SBP }
```

whose vertices are (90, 60), (90, 67.5), (106.67, 80), (120, 80), (120, 60) —
**five of them**. An invertible affine map sends a rectangle to a
parallelogram, which has four. No affine change of variables turns R into a
Morris box. Concretely, for SBP + PP: at SBP = 90 the constraint forces PP ≤ 30,
at SBP = 120 it forces PP ≥ 40, and a rectangle needs one PP interval for both.
The intersection is empty.

The constrained-sampling route is not impossible, but it is worse here than the
clip. The standard equiprobable Morris step is Δ = p / (2(p−1)), which exceeds
1/2 for every number of levels p. The feasible diastolic window at SBP = 90 is
[60, 67.5], i.e. 0.375 of the 20 mmHg range. Since 0.375 < 0.5, **no diastolic
step of standard Morris length fits at SBP = 90, for any p**: a strictly
constrained design returns zero diastolic information at the lowest systolic
setting, where the current design still returns an attenuated estimate.

The only clean alternative is to shrink the envelope — SBP ∈ [106.7, 120], where
the ratio never binds — which discards more than half the systolic range. For an
atlas whose purpose is to map the operational envelope, that is the wrong trade.

---

## Method

Three analyses, none of them requiring a new simulation.

**1. Six estimators** (`scripts/s032_uncontaminated_step_analysis.py`).
Contamination is derived from the *applied* values, never hard-coded. Beyond the
published nominal-step and applied-step estimators: *uncontaminated-step* drops
every clean pair whose applied DBP co-varies with SBP; *trajectory-matched*
additionally restricts every input to the 12 of 20 trajectories whose systolic
step is uncontaminated, so no input is estimated on more data than another; and
two *combined* estimators apply both corrections at once — a pairing evaluated
neither by §S3.7 nor by the published index, and the reconstruction a
methodological reviewer is most likely to build.

**2. Integrity audit** (`scripts/s032_aggregate_integrity_audit.py`).
Originally specified as a gate before reading raw systolic/diastolic channels
for the bridge probes. Those probes were deferred, so it stands alone: it is the
first full-scale check of `aggregated.parquet` against the 1,260 `output.csv`
files it was built from.

**3. Transition-stratified comparison**
(`scripts/s032_transition_stratified_analysis.py`). Three systolic transitions
carry both contaminated and uncontaminated steps, so the two groups can be
compared where the systolic start and end values are identical.

Each script begins with calibration gates it must clear before reporting
anything of its own: the nine audited §S3.7 counts, and exact reproduction of
`results/morris_indices.parquet` (318 rows, max |Δ| = 0).

---

## Results

### The ranking is robust

**SBP is rank 1 for MAP in 8 of 8 cells under all six estimators.** DBP is the
runner-up in all eight under the combined estimators — the applied-step
denominator lifts it past HR in S3\_M and S3\_F, where HR is second under the
nominal estimator — so the smallest margin is a **1.22-fold μ\* ratio, in
S2\_M**.

The exact condition: DBP overtakes SBP in a cell only where its
applied-to-nominal μ\* ratio exceeds that cell's
uncontaminated-SBP-to-nominal-DBP ratio. Measured, the former spans **1.131 to
3.289** and the latter **2.266 to 4.669**. Met in no cell.

A screen using the global median factor of 2.4 had flagged S4\_M and S4\_F as
the exposed cells. That was wrong in both directions: their MAP-specific factors
are the two **lowest** (1.131, 1.149), and the tightest cell is S2\_M, whose
factor is the highest (3.289). The per-cell computation was necessary; the
median was actively misleading.

### The frozen aggregate is faithful

| check | result |
|---|---|
| expected runs present as parquet rows | 1,280 / 1,280 |
| channel means reproduced exactly (abs diff 0.0) | **7,560 / 7,560** (1,260 × 6) |
| flag fields reproduced | **6,400 / 6,400** (1,280 × 5) |
| absent CSVs vs recorded divergences | 20, **identical sets**, not merely equal counts |
| steady-state window size | **13 points in every one of the 1,260 runs** |

This is not circular. The parquet was frozen on 2026-04-26 (`e068544`), and
`src/detector.py` has changed five times since — including `708efb1`
(2026-07-26), which widened the clamp patterns after S030b found a false
negative. That commit states the published sweep is unaffected; this measures
the same conclusion independently, on the flags, for all 1,280 runs.

### The stratified comparison points one way but proves nothing

Dropping the contaminated pairs lowers μ\*(SBP → MAP) in **8 of 8 cells**,
median **−10.4 %** (range −14.3 % to −6.5 %). Consistent with upward
contamination, but confounded with position: the contaminated steps sit at the
low-SBP end.

Within a transition:

| transition | contam. | uncontam. | median \|EE\| contam. | median \|EE\| uncontam. | diff | applied-DBP path |
|---|---:|---:|---:|---:|---:|---|
| 100-to-120 | 3 | 9 | 20.44 | 15.74 | +4.70 | 75 → 80 |
| 110-to-90 | 15 | 16 | 24.94 | 17.26 | +7.68 | 80 → 67.5 |
| 120-to-100 | 1 | 19 | 20.32 | 16.74 | +3.59 | 80 → 75 |
| 90-to-110 | 0 | 5 | — | — | — | not evaluable |

Contaminated is higher in **3 of 3** evaluable transitions, and the contrast
stays positive in **every** leave-one-transition-out.

**But requested DBP is perfectly collinear with contamination** — every
contaminated pair sits at DBP = 80, every clean pair below. That is structural
for 100-to-120 and 120-to-100, whose 75 mmHg ceiling no lower grid level can
exceed, and an artefact of the realised draw for 110-to-90 (DBP = 73.33 would
contaminate there, and simply does not occur). So the stratification does not by
itself separate contamination from a diastolic-level effect. Reporting the
requested-DBP column is what made this visible; without it this session would
have claimed a clean separation it does not have.

What does discriminate is the **applied-DBP displacement**, which varies between
transitions while the requested DBP does not: 5 mmHg → gap +4.14, 12.5 mmHg →
gap +7.68. A pure level effect would give a similar gap in all three, since all
three sit at the same requested DBP. It also predicts the ordering backwards:
the largest gap belongs to 110-to-90, whose contaminated steps have the
**lowest** mean endpoint DBP (73.75 against 77.5).

Fragility, stated because the numbers invite over-reading: three evaluable
transitions over **two** distinct displacements, contaminated group sizes 1, 3
and 15. One comparison, not a dose-response curve. Descriptive throughout — the
other five inputs and position within the trajectory still differ between
groups. No significance test, no causal attribution.

---

## Decision

**No new simulation is needed to defend the published ranking.** It survives the
most severe estimator constructible from the existing data, and the residual
question — the signed size of the contamination — does not bear on it.

The manuscripts now carry the defect as paper limitation (vi), a §S3.7 addendum
with Table S5, and the matching monograph passage. Ledger 350 → 382 anchors.

---

## Deferred: the L-path bridge probes

The one construction that would *measure* the contamination rather than bound
it. For each contaminated pair, re-orient by increasing SBP so that
L = (SBP_low, DBP_low) and H = (SBP_high, DBP_high), then add the bridge point

```
C = (SBP_high, DBP_low)
```

which is always admissible, because DBP_low ≤ 0.75·SBP_low < 0.75·SBP_high. The
identity Y(H) − Y(L) = [Y(C) − Y(L)] + [Y(H) − Y(C)] then splits the step into a
pure SBP move at fixed DBP and a pure DBP move at fixed SBP. **One new run per
contaminated step**; L and H already exist.

Two properties worth recording:

- The fourth corner (SBP_low, DBP_high) is **always** forbidden, not sometimes:
  contamination implies DBP_low = 0.75·SBP_low and DBP_high > DBP_low, hence
  DBP_high > 0.75·SBP_low. The admissible L-path is therefore **unique**, which
  removes any "why this decomposition" objection — and also means the
  SBP × DBP interaction cannot be estimated symmetrically.
- The bias on μ\* is **not** the DBP term directly. μ\* uses |EE|, and
  |EE_diag| − |EE_SBP| equals the DBP term only when the two contributions agree
  in sign. Any future report must publish both signed contributions, their
  absolute values, their sign agreement, and the absolute gap.

**Scope if launched:** 8 contaminated design steps × 8 cells = at most 64 probe
runs (~45 min in series, ~15 min at 3× parallel, at the measured 41.7 s median),
preceded by 16 provenance sentinels — one L and one H per cell, chosen before
observing any result — and by a calibration of the raw-CSV extraction path
against `MAP_mean` on the runs that already exist.

**Condition that would justify launching:** a reviewer asking for a signed
quantification of the contamination. Not needed for the ranking claim.

⚠️ **Provenance caveat for whoever runs them.** The image that produced the
sweep is **not recoverable**: `run_meta.json` records only the bare name
`pulse-atlas-engine`, with no tag or digest, and the local `:latest` was rebuilt
on 2026-05-04, eight days after the sweep. The C++ engine is pinned
(`FROM kitware/pulse:4.3.1`) and the only wrapper change on the default VC-AC
path is an optional patient-trigger block the sweep never sets; the ThinkPad
reproduction of 2026-06-10 rebuilt the image independently and matched the
canonical pilot **bit-for-bit**. Behavioural continuity is therefore
well-supported but not provable from the record — hence the sentinels. **Do not
rebuild the image**: `:latest` is already out of sync with `run_atlas_engine.py`
(changed 2026-05-13 and 2026-05-22) and `pip install pandas` is unpinned, so a
rebuild yields a third variant and loses the only artefact whose equivalence is
documented.

---

## Incidents

Kept because each one produced a plausible, wrong result that nothing else
caught.

**The output column that was never filtered.** The combined-estimator table
reported μ\*(SBP) = 0.2687 for S1\_M where the true value is 17.31 — a factor of
64 — because a scalar accessor filtered on (cell, input) but not on *output*,
returning HR instead of MAP. The table looked entirely reasonable. It was caught
only because two independent routes to the same fact disagreed: the f_c > f_flip
test said DBP overtakes in 8/8 while the rank column said SBP is first in 8/8.
That cross-check is now a permanent guard that exits non-zero.

**Assuming DBP is the runner-up.** The "smallest margin" was computed against
DBP without checking that DBP is actually second under that estimator. It is —
but under the *nominal* estimator HR outranks DBP in S3\_M and S3\_F, so the
assumption could have put a wrong minimum into the paper. Now measured.

**Three instrument failures, same family.** A piped `grep -A1 | grep -oE` on the
build log reported "0 Overfull" while the new table overflowed by 136.55 pt. An
`awk` filter on `t <= 120` counted 12 window points instead of 13, because the
last timestamp is 120.0000000000557 and the detector carries a ±1e-6 tolerance
the filter did not. And `pdftotext` "lost" three phrases that were correctly
rendered — page folios and a math glyph interleaved into the extracted stream.
In all three the artefact was right and the measuring tool was wrong.

**Two false alarms retracted before they cost anything.** The crosswalk note
naming "§S3.3" for the clip-cost subsection is not stale: reconstructing the
supplement structure at `8998ac5` shows that subsection *was* S3.3 on the note's
own date. And three monograph references to "Supplementary §S11" point at
`preprint/supplementary.md`, the monograph's own supplementary document, whose
S11 is the ML/SHAP cross-check. Exactly one reference was genuinely stale
(`manuscript.md:870`), fixed in `24cf5b3`.

**Table renumbering.** Inserting Table S5 in §S3.7 shifts every later supplement
table by one: S5–S15 become S6–S16. No manuscript file hardcodes a table number;
the affected crosswalk and audit-register entries are dated records that also
name the section and the row. Nothing breaks, but reviewer notes citing a
supplement table by number are now off by one from S5 onward.

---

## Artefacts

`results/s032/` — `morris_step_contamination.csv`, `mu_star_by_estimator.csv`,
`sbp_map_dominance.csv`, `combined_estimator_MAP.csv`,
`transition_stratified_sbp_map.csv`, `transition_stratified_contrasts.csv`.

Commits: `9c5cc50` (six estimators), `e6eabb9` (integrity audit), `e08c9be`
(transition stratification), `094565c` (runner-up measured), `24cf5b3` (stale
monograph reference), `ffdd5c8` (manuscripts + ledger 350 → 377), `3d9309d`
(ledger 377 → 382, the five unanchored quantities).
