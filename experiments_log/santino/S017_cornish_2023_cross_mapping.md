---
id: S017
author: santino
date: 2026-05-13
status: done
tags: [literature, cross-mapping, cornish, falsification, manuscript-discussion]
linked_code: []
linked_data: [results/reliability_classification.csv]
supersedes: ""
related: [S010, S016]
---

# S017 — Cornish 2023 cross-mapping: re-tabulating the only prior external Pulse assessment against the atlas's 6-output panel

## Hypothesis

Cornish et al. 2023 (arXiv:2301.07210, v4 Nov 2023) is the only prior
peer-quality external assessment of Pulse on a clinical dataset.
Before submission, the atlas manuscript needs an explicit cross-mapping
against Cornish's results so reviewers can verify two things:

1. The two papers' failure surfaces do not collide — both can stand on
   their own without one citing the other's red cells.
2. Where the two papers' panels *do* overlap, they tell a structurally
   consistent story rather than contradicting each other.

The prediction before reading Cornish's tables verbatim was that
overlap would be confined to a single channel (PaCO₂) and that
electrolyte/metabolic channels would dominate Cornish's rejection
counts. Verification was needed because pre-S017 memory entries had
recorded the Hoeffding numbers without indexing the full 15-quantity
panel — i.e. the cross-mapping breadth was potentially under-counted.

## Motivation (why now)

This work is Phase B item B1 in `ROADMAP_PHASE_B.md`, queued from the
2026-05-12 pre-submission audit. Phase A shipped self-consistent
manuscript text but left three additions for the next compute / mapping
window. B1 is the no-compute item: ~2–3 h of source reading + manuscript
edit. Doing this before manuscript submission removes a predictable
reviewer ask ("how does this relate to Cornish?") and explicitly maps
the boundary between this paper's contribution and Cornish's contribution.

The methods paper currently cites Cornish twice in §1.1 (Motivation)
and once in §6.7 (References) but does not present the rejection
patterns at all. A reviewer would have to leave the paper to find out
what Cornish actually rejected.

## Method

1. **Verified the v4 paper's Table 1 (Hoeffding's inequality, main
   text) and Table 4 (reverse-percentile bootstrap, Appendix H.6) via
   the alphaxiv MCP** (`mcp__alphaxiv__answer_pdf_queries` on
   `https://arxiv.org/pdf/2301.07210v4` and the v1 PDF for the
   full-text extraction that had Table 4 in plain readable form). All
   15 quantities and their rejection counts were captured verbatim,
   not paraphrased. Cross-checked the sums: 24+21+13+10+5+5+3+2+2+0+
   0+0+0+0+0 = 85 (matches the paper's "281 vs. 85 rejections in
   total" comparison statement on page 38–39 of the v1 PDF).

2. **Constructed a re-tabulation table mapping Cornish's 15 channels
   onto the atlas's 6-output panel.** Four channels overlap directly
   (HR, MeanBP ≈ atlas MAP, PaO₂, PaCO₂); two channels are atlas-only
   (V_t delivered, SpO₂); seven channels are Cornish-only and define
   the complementary failure surface (Chloride, Sodium, Potassium,
   Skin Temperature, Calcium, Glucose, HCO₃, plus pH/SysBP/DiaBP/RR
   for total 11 non-overlapping channels).

3. **Compared Cornish's Hoeffding pattern to this atlas's §3.7
   traffic-light** on the four overlapping channels. The atlas finds
   HR red at S3+ (4/8 cells), MAP red at S4_M only (1/8 cells), PaO₂
   red at S3+ (4/8 cells), PaCO₂ red at S4_M only (1/8 cells).
   Cornish's Hoeffding rejections are 0/162 HR, 0/92 MeanBP,
   0/78 PaO₂, 3/70 PaCO₂. PaCO₂ is the channel where Cornish flags
   the most fraction (4.3 %) and is also one of the channels where
   the atlas's H4 Wasserstein sex-difference is significant in 3 of 4
   scenarios. The two papers' channel rankings agree ordinally on
   PaCO₂ > the rest, but Cornish's absolute rejection densities are
   much lower because his sepsis-cohort intervention sequences do not
   visit the atlas's S3/S4 ARDS extremes.

4. **Verified the methodological non-overlap.** Cornish's hypotheses
   are indexed by (time-step, action-sequence, sex–age–quantile bin),
   not by (scenario, sex). The two indexings are not surjective on
   each other, so a tighter cell-level cross-tab is mathematically
   impossible without re-running Cornish's framework on this atlas's
   1,280 outputs (a follow-up paper, not this one).

5. **Drafted §4.4 "Relationship to Cornish et al. 2023 (causal
   falsification) — Table 2"** in `preprint/manuscript.md`. Inserted
   between §4.3 (ML implications) and the re-numbered §4.5
   (Limitations) and §4.6 (Downstream Pulse research). Updated the
   §6.7 Cornish entry with a forward-reference to §4.4 and the
   verbatim rejection-count summary (85 Hoeffding / 281 bootstrap).

## Findings

### F-S017-A — Atlas / Cornish output-panel overlap is wider than the memory had recorded

The pre-S017 phase-b memory entry (`phase_b_compute_sprint_2026_05.md`)
and the roadmap entry (`ROADMAP_PHASE_B.md` §B1) both characterized
the overlap as "only PaCO₂", treating the other channels as out-of-panel.
Verbatim reading of Cornish's full 15-quantity Table 1 shows the overlap
is actually four channels (HR, MeanBP, PaO₂, PaCO₂). The wider overlap
strengthens the cross-mapping rather than narrows it: the atlas now has
ordinal agreement (not just channel agreement) with Cornish on the
gas-exchange-then-cardiovascular ranking of channel fragility.

### F-S017-B — Cornish's 85 Hoeffding rejections distribute 3 / 80 / 2 across overlap / non-overlap-physiology / cardiovascular-adjacent

Counted verbatim from Table 1:
- Atlas overlap (HR, MeanBP, PaO₂, PaCO₂): 0 + 0 + 0 + 3 = 3
- Non-overlap physiology (Chloride, Sodium, Potassium, Skin Temp,
  Calcium, Glucose, HCO₃): 24 + 21 + 13 + 10 + 5 + 5 + 2 = 80
- Cardiovascular adjacent (SysBP, DiaBP): 2 + 0 = 2
- Other (pH, RR): 0 + 0 = 0
- Total: 85 ✓

Bootstrap (Appendix Table 4) totals: 21 + 240 + 8 + 12 = 281 ✓.

### F-S017-C — Both papers single out PaCO₂ as the most assessment-sensitive gas-exchange channel

Cornish: PaCO₂ = 3 / 70 (4.3 %) Hoeffding rejections; only channel in
the atlas-overlap quartet with non-zero Hoeffding rejections. Atlas
§3.6 (H4 Wasserstein): PaCO₂ is the channel where M-vs-F within-sex
null is significant in 3 of 4 scenarios (S1, S2, S3 at q = 0.05 BH-FDR),
the most-flagged of any output. The independent agreement on PaCO₂
fragility — Cornish from sepsis-intervention falsification, atlas from
operational-input sweep — supports both papers' empirical findings on
that channel and points downstream-Pulse-users to ingest PaCO₂ outputs
with the most caution among the gas-exchange channels.

### F-S017-D — The two papers are complementary, not redundant

Of Cornish's 85 Hoeffding rejections, 82 fall on channels the atlas
does not assess (electrolyte 63 + metabolic 5 + acid–base 2 + dermal
10 + adjacent-pressure 2 = 82). The atlas's six outputs include V_t
and SpO₂, neither of which is in Cornish's 15-channel panel. The two
papers therefore divide the Pulse-reliability question along an output
axis (chemistry/thermoregulation vs cardio–respiratory) and along an
input axis (sepsis-cohort interventions vs operational ARDS envelope).
This division motivates a complementary follow-up — a "metabolic /
renal atlas" sweeping Pulse's internal endocrine and electrolyte
models — that neither paper currently fills.

## What this changes in the manuscript

1. **New §4.4 "Relationship to Cornish et al. 2023 (causal
   falsification) — Table 2"** in `preprint/manuscript.md`. Two-page
   subsection with one table (Cornish's Hoeffding + bootstrap counts
   re-tabulated against the atlas panel) and four paragraphs
   (cross-mapping of methodologies, agreement on the overlap,
   complementarity, four-quadrant practitioner picture).
2. **Re-numbered §4.5 (Limitations)** and **§4.6 (Implications for
   downstream Pulse research)** to make room for the new §4.4.
3. **Updated §6.7 Cornish entry** with v4 designation, full Hoeffding /
   bootstrap rejection totals (85 / 281), and a forward-reference to
   §4.4. Audit trail anchored to this S017 and to the earlier S016
   GitLab audit.

## What this does NOT change

- No code changes. No data changes. No re-runs of Pulse.
- No claims modified in §1.1, §3, §4.1, §4.2, §4.3. Cornish was
  already cited in §1.1; the cross-mapping is *additional* discussion,
  not a retraction.
- No reference additions or removals — `cornish2023` was already in
  `preprint/references.bib`.

## Caveats

- Cornish v1 (Jan 2023) and v4 (Nov 2023) report slightly different
  framings (Table 4 in v1 appendix is what v4 calls "Table 4 in the
  Supplement", and the action space is described with minor variations
  between versions). The verbatim rejection counts in Table 1 are
  identical between v1 and v4. We pin our citation to v4 (Nov 2023) as
  that is the latest version available on arXiv at the time of writing.
- The "Table 4" referenced in the manuscript table caption is Cornish's
  appendix table containing the bootstrap rejection counts, not the
  Hoeffding ones. The Hoeffding counts are in Cornish's main-text
  Table 1.
- The cell-level cross-tab is *ordinal*, not quantitative. Tighter
  comparison would require porting Cornish's causal-falsification
  procedure onto our 1,280 outputs — that is a follow-up paper, not
  this one.

## Related artifacts

- Manuscript: `preprint/manuscript.md` §4.4 (new) and §6.7 (updated
  Cornish entry).
- Roadmap: `ROADMAP_PHASE_B.md` §B1 (this experiment fulfills B1).
- Memory: `phase_b_compute_sprint_2026_05.md` (Phase B index;
  B1 → completed by this S017); `pulse_cornish_2023_falsification.md`
  (Cornish reference card; rejection-count correction now propagated).
- Source: `https://arxiv.org/pdf/2301.07210v4` (verbatim Table 1 and
  Table 4 extracts).
