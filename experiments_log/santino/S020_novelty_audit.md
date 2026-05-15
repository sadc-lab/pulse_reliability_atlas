---
id: S020
author: santino
date: 2026-05-15
status: done
tags: [literature, novelty-audit, pre-submission, citation-verification, manuscript-discussion]
linked_code: []
linked_data:
  - preprint/manuscript.md
  - preprint/references.bib
supersedes: ""
related: [S010, S016, S017]
---

# S020 — Pre-submission novelty audit: verifying that every "first" / "novel" claim in the manuscript survives a literature double-check

## Hypothesis

Each novelty claim in the methods paper (the title's "first", the §1.1
motivation framing, the §1.3 Contributions bullets, the §3.5 "first
quantitative sex-specific reliability finding for Pulse 4.3.1", and
the F-003 / F-004 findings) traces to a unique, previously
unaddressed gap rather than to a published prior result we have
missed.

The expectation going in was that the operational-input sensitivity-
analysis gap is genuine (because the Pulse FAQ literally says so, and
S016 already audited the GitLab repo) but that at least one finding
— most likely F-004 (VC-AC patient-ventilator dyssynchrony at low
tidal volume) — has a clinical-literature precedent that the
manuscript currently fails to cite. That clinical precedent would
not invalidate the *Pulse-engine* novelty of F-004; it would,
however, leave the paper exposed to a reviewer asking "do you know
this is a real-world phenomenon?".

## Motivation (why now)

The pre-submission audit performed on 2026-05-12 (Phase A close-out)
verified *citation accuracy* for the references already in the
bibliography (S010 protocol). It did not perform a systematic
"has anyone else done this before?" sweep across each individual
novelty claim. The maintainer requested an explicit double-check
before submission. The risk we wanted to retire: a reviewer
discovers a paper that has already done part of our work and that
we failed to cite, which would either weaken a contribution claim
or force a mid-review revision cycle.

S016 (May 2026 GitLab + literature re-audit) already covered the
Pulse-internal landscape and ruled out a hidden SA study by
Kitware. S017 (Cornish cross-mapping) ruled out a methodological
collision with the only known external assessment. S020 closes the
remaining gap: third-party academic work on Pulse that neither S016
nor S017 surfaced.

## Method (how)

Phased, per CLAUDE.md (internal → MCP → web). MCPs (AlphaXiv,
DeepWiki) were disconnected at the time of audit, so the protocol
collapsed to internal-first + web-second with a structured PubMed
verification step on any candidate citation.

1. **Internal pass.** Re-read S010 (verifies citations against
   DOI / PMID), S016 (audits Pulse GitLab + the 2020 SA study tag
   + Kitware V&V infrastructure + active dev branches), and S017
   (re-tabulates Cornish 2023 Table 1 + Table 4 against the atlas's
   6-output panel). Enumerated every "first" / "novel" claim in
   `preprint/manuscript.md` via `grep -nE "first|novel|never
   been|has not been|no prior|previously unaddressed|gap"`.

2. **Web search pass (6 queries).** Targeted each novelty claim
   individually rather than running one broad query, to surface any
   single paper that might cover any one of our claims:
   - `"Pulse Physiology Engine" sensitivity analysis Morris elementary effects`
   - `"Pulse Physiology Engine" uncertainty quantification operational inputs Kitware reliability`
   - `BioGears HumMod sensitivity analysis Morris Sobol cardiopulmonary virtual patient`
   - `"Pulse Physiology Engine" VC-AC ventilator dyssynchrony tidal volume instability`
   - `"Pulse Physiology Engine" hyperoxia PaO2 FiO2 1.0 simulation overshoot`
   - `"Pulse Physiology Engine" sex specific male female divergence reliability adult patient`
   - `"Pulse Physiology Engine" validation external assessment 2024 2025 third-party clinical`
   - `"Pulse Physiology Engine" synthetic data machine learning training cohort virtual patient`

3. **PubMed verification of any candidate citation.** For each
   external paper surfaced by the web pass that we considered citing,
   queried PubMed E-utilities `esummary.fcgi?db=pubmed&id=<PMID>`
   (JSON) for verbatim title, full author list, year, journal,
   volume, issue, pages, DOI. Accept only on exact match against
   the candidate's PMID.

## What we tried (including dead ends)

- **AlphaXiv MCP and DeepWiki MCP** were disconnected for the entire
  audit window. Both would have given a faster, more structured
  search than WebSearch — particularly AlphaXiv for any arXiv-only
  SA paper. Fallback: WebSearch surfaces arXiv hits indirectly via
  Google indexing, and S016 already ran a full AlphaXiv pass in
  May 2026 with zero results for Pulse-related queries (Pulse's
  primary publication venues are not indexed by AlphaXiv anyway).
  Acknowledged this as a coverage caveat in the audit summary.

- **Author-attribution slip caught by PubMed.** During the web-search
  pass, the candidate clinical-literature citation for F-004
  (Annals ATS 2016, "Effect of Tidal Volume Size and Its Delivery
  Mode on Patient-Ventilator Dyssynchrony", PMID 27598383) was
  initially recalled with the author surname "Kallet" from working
  memory. The PubMed `esummary` verification step returned the
  actual authors as **Figueroa-Casas JB, Montoya R**. The candidate
  was re-attributed against the verified record before any text was
  added to the manuscript. This is exactly the failure mode the
  S010 verification protocol exists to prevent.

## Results

### Per-claim novelty verdict

| # | Claim (location) | Verdict | Evidence |
|---|---|---|---|
| 1 | "First sensitivity analysis on Pulse user-facing operational inputs" (title, §1.1, §1.3) | ✅ Holds | Pulse FAQ still verbatim states "no formal sensitivity analysis." 2020 `STUDY_SENSITIVITY_ANALYSIS_1_0_0` tag did Sobol on *internal vascular-circuit resistance multipliers* (model-calibration parameters), not operational inputs (already qualified in §1.1 per S016). Zero third-party Pulse SA papers surfaced. |
| 2 | "First open reliability atlas / clamping / divergence map for Pulse 4.3.1" (title, §1.1, §1.3) | ✅ Holds | No prior published work classifies Pulse runs by clamp / divergence / implausibility / non-steady-state across an operational envelope. Kitware's own V&V (mapped in S016) is per-system clinical validation vs literature ranges, not envelope-wide reliability mapping. |
| 3 | "First quantitative sex-specific reliability finding for Pulse 4.3.1" (§3.5, line 884) | ✅ Holds | No prior Pulse-specific sex-stratified reliability paper found. Sex differences in real cardiopulmonary physiology are well-documented in PubMed but no overlap on the *Pulse-engine reliability* dimension. |
| 4 | F-003 hyperoxia overshoot (PaO2 > 600 at FiO2 = 1.0) (§3.8) | ✅ Novel for Pulse | No prior Pulse-specific publication documents this. |
| 5 | F-004 VC-AC patient-ventilator dyssynchrony (§3.8) | ⚠️ Pulse novelty ✅, clinical-precedent citation **missing** | The clinical phenomenon is well-documented in real ICU patients (Figueroa-Casas & Montoya 2016, PMID 27598383). The Pulse-engine manifestation, the 20.6 % atlas-wide flag rate, and the −2 cmH2O corrective setting are all novel. Citation added to §3.8 and §4.1 to make the precedent explicit. |
| 6 | Four-flag classifier as a reusable instrument (§2.6, §2.9) | ✅ Novel synthesis | The individual flag types (regex on logs, exit-code, hard bounds, drift) are generic; no prior Pulse-specific synthesis exists. |
| 7 | Blood-volume mechanism for the all-male divergence cluster (§3.5, S018) | ✅ Novel | No prior publication characterizes this. |
| 8 | Cornish 2023 cross-mapping (§4.4 Table 2) | ✅ Novel synthesis | Cornish is the only prior external assessment; the per-channel cross-tab against an operational-sweep atlas is unique to this paper (S017 documents this). |
| 9 | ML-pipeline data-quality framing (§4.3) | ✅ Holds | Kitware actively promotes Pulse for synthetic ML training data, but no prior publication produces a per-cell data-quality filter for ML training cohorts. |

### Citations added to the manuscript (single addition, verified)

| Citation key | Citation | Verification | Inserted at |
|---|---|---|---|
| `figueroacasas2016` | Figueroa-Casas JB, Montoya R. *Effect of Tidal Volume Size and Its Delivery Mode on Patient-Ventilator Dyssynchrony.* Annals of the American Thoracic Society 13(12):2207-2214 (2016). DOI: 10.1513/AnnalsATS.201605-362OC. | PubMed esummary returned verbatim record; PMID 27598383 confirms title + journal + volume + issue + pages + DOI. | §3.8 (F-004 introduction, anchors the clinical-precedent line) and §4.1 (VC-AC dyssynchrony refines rather than indicts Pulse). Full bibliographic entry added to §8.7 and to `preprint/references.bib`. |

### Search coverage caveat

- Pulse's primary publication venues are SN Comprehensive Clinical
  Medicine, MDPI Bioengineering, PLOS One, and PMC — biomedical
  rather than arXiv-indexed — so a missing AlphaXiv MCP did not
  meaningfully narrow our visible search surface for Pulse.
- WebSearch hits PubMed and PMC indirectly but is not a structured
  PubMed E-utilities pass. An eventual S010-style PubMed esearch
  with the exact query set (e.g.
  `("Pulse Physiology Engine"[Title/Abstract] OR ...) AND
  (sensitivity[Title/Abstract] OR uncertainty[Title/Abstract])`)
  would close the residual coverage gap if a reviewer later asks
  for the verbatim search log.

## Interpretation

All novelty claims in the manuscript survive the audit. The single
change required before submission was adding the Figueroa-Casas &
Montoya 2016 citation to anchor F-004's clinical-phenomenon
precedent. This citation **strengthens** F-004 rather than
weakening it: the atlas is now positioned as the *Pulse-engine
manifestation of a clinically known issue*, with the new
contributions being (a) the operational-envelope quantification
inside Pulse and (b) the corrective trigger configuration. A
reviewer who would have asked "do you know this is a real-world
phenomenon?" now has nothing to point at.

The PubMed-verification step also caught an attribution slip
("Kallet" → actually Figueroa-Casas, Montoya) before any text
reached the manuscript. This is direct evidence that the S010
verification protocol (PubMed esummary on every external citation,
no citing from memory) is the correct policy for an LLM-assisted
manuscript pipeline. The same protocol applies to any future
citation: never cite from memory; always verify against PubMed for
biomedical work and Semantic Scholar for methods work.

S020's verdict can be summarised in one sentence: **the
manuscript's "first" claims hold, the F-004 clinical precedent is
now cited, and no other novelty risk was identified by an
8-search literature double-check on 2026-05-15.**

## Next steps

- Commit the manuscript and `references.bib` edits + this experiment
  log + `INDEX.md` update + the §1.4 glossary extension to S020.
- When the AlphaXiv MCP comes back online, run one more targeted
  pass on `"sensitivity analysis" "lumped parameter" "physiology
  engine"` and `"Pulse" "Morris" "Sobol"` to fully close the
  arXiv coverage gap; update this log with the findings.
- (Optional, post-submission.) Run a structured PubMed esearch
  with the audit's query set and store the raw JSON responses in
  `data/S020/pubmed_responses/` as a reviewer-verifiable record.
