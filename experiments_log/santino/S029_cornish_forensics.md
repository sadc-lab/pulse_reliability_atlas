---
id: S029
author: santino
date: 2026-05-28
status: done
tags: [cornish, falsification, forensics, value-recomputation, manuscript-discussion, audit]
linked_code: []
linked_data: []
supersedes: ""
related: [S017]
---

# S029 — Cornish 2023 hypothesis-count forensics: reconciling the 1,442-vs-1,522 main-text-vs-appendix discrepancy

## Hypothesis

The total-hypothesis count attributed to Cornish et al. 2023 in the atlas
manuscript (§4.4 and §6.7) is internally inconsistent with the
per-channel denominators reproduced in our own Table 2 and supplement
Table S7. Specifically: the prose cited "1,442 hypotheses across 15
physiological quantities," but if there are genuinely 15 channels and the
per-channel hypothesis counts sum to the figure our tables encode, the
total should not be 1,442. One of the two figures (the headline total or
the channel count) must be wrong.

This is a desk-audit / forensic reconciliation, not a Pulse experiment —
no engine runs, no compute.

## Motivation (why now)

Surfaced during the **Standalone Active Supplement Audit, Pass B**
(2026-05-28) under **Rule D.8 (Value Recomputation)**: when the stated
aggregate (1,442) was checked against the sum of the per-channel
denominators rather than accepted typographically, the arithmetic did not
close. Left unfixed, this is a predictable peer-reviewer trap — a reviewer
who opens Cornish's main text sees "1,442 across 14 quantities" and could
flag *our* 15-channel framing as a transcription error. Resolving it
before submission converts a vulnerability into a demonstration of
source-level forensic competence (Zero-Hallucination policy).

## Method (how)

1. **D.8 recomputation (assistant, this audit).** During Supplement Pass
   B the stated total 1,442 was tested against the per-channel hypothesis
   denominators encoded in manuscript Table 2 and supplement Table S7.
   Those denominators sum to **1,522**, not 1,442 — an internal
   inconsistency in the manuscript prose, independent of what Cornish's
   own text says.

2. **Source verification (maintainer).** The maintainer consulted the
   Cornish 2023 v4 PDF directly:
   - **Main text, p.15:** states "1,442 hypotheses across **14**
     physiological quantities."
   - **Appendix Table 4, p.47:** reports the full results on **15**
     quantities, explicitly including an **Arterial-pH** row with **80
     hypotheses and 0 rejections**.
   - Arithmetic closes: **1,442 + 80 = 1,522.**

   The assistant did **not** re-open Cornish's PDF in this session; the
   main-text-vs-appendix source split is the maintainer's verified
   reading. The assistant independently confirms only the arithmetic
   (1,442 + 80 = 1,522) and the internal table-denominator sum (1,522).

3. **Disposition (Scenario A-defended).** Cornish's main-text 1,442 is a
   channel-omission **drafting error** by the Cornish authors: the
   Arterial-pH channel was dropped from the headline count but retained
   in their own results table. Since the atlas transcribes the full
   15-channel results, the mathematically correct total is **1,522**. The
   manuscript is corrected to 1,522 **with a forensic parenthetical** that
   documents the discrepancy (the "A-defended" variant) rather than a bare
   number swap — so a reviewer checking Cornish's main text is pre-empted.

## What we tried (including dead ends)

- **Bare number swap (rejected).** Simply changing 1,442 → 1,522 with no
  explanation would itself look like a transcription error to any reviewer
  who reads Cornish's main text (which says 1,442). Rejected in favour of
  the A-defended variant.
- **Leaving 1,442 and changing "15" → "14" (rejected).** This would match
  Cornish's main text but contradict our own Table 2 / Table S7, which
  tabulate all 15 channels (pH included). It would propagate Cornish's
  error into our work rather than correcting it.

## Results

- **Manuscript fix — commit `1ca8611` `[MONOGRAPH-ONLY]`** (preprint/manuscript.md):
  - §4.4 main prose (L2499): "tested **1,522** hypotheses across 15
    physiological quantities … (Cornish's main-text figure of 1,442
    across 14 quantities omits the Arterial-pH channel — 80 hypotheses, 0
    rejections — that appears in their Appendix Table 4; we report the
    full 15-channel total)."
  - §6.7 reference annotation (L3230): "on **1,522** hypotheses across 15
    physiological quantities" (number-only; explanation lives in §4.4).
  - The single remaining literal "1,442" (L2501) is the *contextualized*
    mention of Cornish's erroneous figure — deliberately preserved.
- **Supplement fix — commit `a7d844f` `[SCIENTIFIC]`, finding SP-B.D1**
  (preprint_npj/supplement.tex §S7 Table S7 caption): corrected the
  Cornish-rejection arithmetic from "80 fall on the 11 channels outside
  the panel" to "82 fall outside the four-channel overlap — 80 on the
  eight not-assessed channels + 2 on SysBP." This fix concerns **rejection**
  counts (80/82/85), a *separate* arithmetic locus from the hypothesis
  total; both were surfaced by the same D.8 sweep.
- Both commits pushed to origin/main (verified: local == origin, 0 ahead /
  0 behind).

## Interpretation

The hypothesis-count discrepancy is a **source-paper drafting error**, not
an atlas error. The atlas's tables were already correct (15 channels,
denominators summing to 1,522); only the headline prose figure had
inherited Cornish's main-text 1,442. The reconciliation:

- **Confirms** the hypothesis: the stated total (1,442) was inconsistent
  with our own 15-channel tables; the correct total is 1,522.
- **Scope:** affects only the *hypothesis-count* claim. The **rejection**
  totals (85 Hoeffding / 281 bootstrap, S017) are unaffected — those were
  already counted across the full 15-channel panel including pH (pH = 0
  rejections in both Cornish tables).
- **Supports** the §4.4 cross-mapping narrative unchanged; the
  complementarity argument (Cornish's failures fall mostly outside the
  atlas's panel) does not depend on the hypothesis total.

**Limitation / provenance honesty:** the main-text-vs-appendix page-level
source claims (p.15, p.47) rest on the maintainer's reading of Cornish's
v4 PDF, not on an independent re-extraction in this session. The
assistant's contribution is the D.8 internal-consistency catch and the
arithmetic confirmation (1,442 + 80 = 1,522). A future verifier wanting
full closure should re-open Cornish v4 and confirm the Arterial-pH row in
Appendix Table 4 (80 hypotheses, 0 rejections) verbatim.

## Next steps

None — question closed. The 1,522 figure is locked in manuscript §4.4 and
§6.7, the memory card `pulse_cornish_2023_falsification.md` is updated to
USE 1,522, and this entry is the durable forensic record. Future sessions
must not regress the count to 1,442.

## Related artifacts

- Manuscript: `preprint/manuscript.md` §4.4 (L2499–2503), §6.7 (L3230) —
  commit `1ca8611`.
- Supplement: `preprint_npj/supplement.tex` §S7 Table S7 caption —
  commit `a7d844f` (finding SP-B.D1).
- Prior cross-mapping: [S017](S017_cornish_2023_cross_mapping.md) —
  established the 15-channel panel and the 85/281 rejection counts.
- Memory: `pulse_cornish_2023_falsification.md` (Cornish reference card;
  hypothesis-count forensics section added 2026-05-28).
- Source: `https://arxiv.org/abs/2301.07210` v4 (main text p.15;
  Appendix Table 4 p.47) — maintainer-verified.
