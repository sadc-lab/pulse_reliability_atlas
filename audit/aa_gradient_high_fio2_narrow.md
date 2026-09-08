# Deferred observation: Pulse's A-a difference at FiO2 = 1.0 is narrow

**Opened** 2026-09-08, during the paranoid re-check of the answer to reviewer
points 3.6-3.8. **Status: PARTIALLY ACTED ON.** The circular framing was removed
from the monograph the same day; the physiological observation itself is
**deferred**, because the reference range it would rest on was not established
from a primary source in this session.

Per the autonomy pact, what is verified is written down and what is not is
labelled as such. No claim about human physiology was added to any manuscript
file.

---

## 1. What triggered this

Reviewer point 3.6 argues that the hyperoxia result is read too optimistically.
Checking that led to the alveolar-gas-equation framing, which is stated in the
monograph at five loci in the form:

> ... median 643 mmHg, ~20 mmHg *below* the alveolar-gas-equation sea-level
> ceiling (≈663 mmHg) — **consistent with Pulse's modelled A-a gradient** ...

Two problems with the emphasised clause, independent of each other:

1. **It is circular.** Pulse's output is trivially consistent with Pulse's own
   model. The clause carries no evidence.
2. **It reads as physiological endorsement.** A reader takes it to mean the
   *size* of the gap has been checked against physiology. It has not.

`preprint_npj/paper.tex` contains **0** occurrences of `A-a` or
`alveolar-arterial` (verified by grep, 2026-09-08). The paper states only that
the plateau sits ~20 mmHg *below* the prediction and explicitly adds "It does
not establish that the plateau level itself is right, which would take
validation against measured arterial data". The paper was therefore already
correct and was not touched.

## 2. What was measured internally

| Quantity | Value | Source |
|---|---|---|
| S1 plateau median, 40 drift-converged runs | 642.87 -> 643 mmHg | `plateau_stats.parquet` |
| S1 PaCO2 median, 120 s window, n = 44 | 41.89 mmHg | `aggregated.parquet` |
| S1 PaCO2 range, 120 s window | 22.49 - 52.81 mmHg | `aggregated.parquet` |

The nominal PaCO2 = 40 used in the monograph's alveolar-gas equation is
therefore close to what these runs actually produce. Recomputing with the
measured median:

    PAO2 = 1.0 x (760 - 47) - 41.89 / 0.8 = 660.6 mmHg
    A-a  = 660.6 - 643 = 17.6 mmHg

against the 663 and ~20 mmHg the monograph states. **The published figures
stand**; the hypothesis that hyperventilation in this cohort would move them
was tested and is false.

**One measurement limit, stated rather than hidden.** The PaCO2 above is the
120-second classifier window, not the 240-300 s plateau window that produces the
643 mmHg. `trajectories.parquet` carries `PaO2_mmHg` only, so the plateau-window
PaCO2 is not measurable from the released artefacts. Supplement S9 states that
PaCO2 settles well under 120 s at FiO2 = 1.0, which makes the substitution
reasonable but does not measure it.

## 3. The observation, and exactly how far it is supported

At FiO2 = 1.0 a healthy adult's A-a difference is expected to be **much wider**
than at room air, where 5-15 mmHg is normal. Pulse produces ~18-20 mmHg at
FiO2 = 1.0 — an essentially room-air-sized difference at 100 % oxygen. If that
expectation holds, Pulse under-represents venous admixture at high inspired
oxygen, which would be consistent with limitation 9 of `CLAUDE.md` (no regional
V/Q mismatch; five-compartment lumped parameter).

**ESTABLISHED, source opened 2026-09-08.** The direction. StatPearls, NCBI
Bookshelf, "Oxygenation Status and Pulse Oximeter Analysis", Pesola G.R. &
Sankari A., last update 11 June 2023, `https://www.ncbi.nlm.nih.gov/books/NBK592401/`,
verbatim: "if the A-a gradient is calculated with inspired oxygen greater than
room air, the alveolar PA02 will increase faster than the arterial PaO2,
resulting in an increasing A-a gradient. This is normal."

**NOT ESTABLISHED.** The magnitude. No primary study reporting a *measured* A-a
difference at FiO2 = 1.0 in healthy adults was opened. Two non-primary figures
were seen and are recorded as leads, not as evidence:

* Tertiary sources give 100-150 mmHg on 100 % oxygen. Not traced to a primary.
* Wagner et al., MIGET, healthy subjects: shunt ~2-3.2 % on 100 % oxygen. Seen
  in a search result summary; **the article was not opened**.

**OWN DERIVATION, not a source.** Applying the shunt equation to a 2-5 % shunt
(Hb 15 g/dL, a-v content difference 5 mL/dL, PcO2 660 mmHg) gives an arterial
PaO2 of roughly 572-626 mmHg, i.e. an A-a difference of roughly 34-88 mmHg. This
is arithmetic performed here, it depends on assumed Hb and cardiac output, and
it must not be cited. It is recorded only because it agrees in direction with
the tertiary figures while disagreeing with them in magnitude, which is itself a
reason not to write either number into the manuscript.

## 4. What was applied

The circular clause was removed at all five monograph loci (lines ~73, ~146,
~335, ~2798, ~3644 before the edit). The load-bearing reasoning is untouched at
every one of them: the plateau lands **below**, not above, the alveolar
prediction, so the original flag reflects a window-length artefact and not an
oxygenation runaway. That argument never depended on the size of the gap.

The factual arithmetic survives at the S021 locus, reworded from "A-a gradient
... consistent with Pulse's modelled alveolar-arterial difference rather than an
oxygenation defect" to "A-a difference of ~20 mmHg", followed by the existing
sentence "Pulse *under-shoots* the alveolar prediction and does not overshoot."

## 5. What would be needed to act on section 3

1. A primary source giving a measured A-a difference, or a measured PaO2, at
   FiO2 = 1.0 in healthy adults at steady state. Anaesthetic preoxygenation
   series are **not** a clean comparator: atelectasis and incomplete
   denitrogenation depress PaO2 for reasons unrelated to steady-state gas
   exchange, and one such series reports 293 +/- 86 mmHg, far below anything
   relevant here.
2. Pulse's own shunt fraction at FiO2 = 1.0, read from the engine source or its
   validation documentation rather than inferred from the A-a difference.
3. A decision on where such an observation belongs. It is a reliability finding
   about the engine at a specific operating point, so Supplement S9 or S5 is the
   natural home, not the paper.

Not to be reopened before the four supervisors reply. Nothing here blocks the
current revision.
