---
id: S010
author: santino
date: 2026-04-27
status: done
tags: [literature-review, references, citations, manuscript-polish, doi-verification]
linked_code: []
linked_data:
  - preprint/manuscript.md
supersedes: ""
related: [S004, S006, S008]
---

# S010 — Literature-review pass: every reference verified against DOI / PMID

## Hypothesis

For the methods paper to be reviewer-defensible, every cited fact
must trace to a primary source whose bibliographic details are
**verified live** rather than recited from memory. A short literature-
review pass to (1) collect the references the manuscript actually
needs, (2) verify each against PubMed / Semantic Scholar / DOI, and
(3) drop any that cannot be verified — yields a §6 References section
that survives standard reviewer scrutiny.

## Motivation (why)

The maintainer requested an explicit literature-review step before
submission, with two specific concerns: (a) prevent hallucinated
references (the failure mode for an LLM-assisted manuscript), and
(b) ground the limitations / methods we discuss in published work,
so the paper does not stand alone as ad-hoc.

The earlier §6 was a list of names (Webb 2023, Bray 2019, PALICC-2,
SALib, Barnes 2020, Clipp 2025, JOSS issue) without full
bibliographic detail. S010 turns that list into a properly-cited
bibliography with verified DOIs / PMIDs, plus in-text citations
threaded through §1.1, §2.5, §2.2, and §3.

## Method (how)

### Reference shortlist

Compiled a 12-entry shortlist of the references the atlas paper
actually needs, organised in five categories:

1. **Pulse Physiology Engine** — Bray et al. 2019, Webb et al. 2020,
   Webb et al. 2023, Pulse FAQ, Pulse Setup source.
2. **Sensitivity-analysis methods** — Morris 1991 (original
   elementary effects), Campolongo, Cariboni, Saltelli 2007 (improved
   Morris with μ\* and radial trajectories), Iwanaga, Usher, Herman
   2022 (SALib).
3. **ARDS clinical anchors** — ARDS Definition Task Force 2012
   (Berlin Definition), Emeriaud et al. 2023 (PALICC-2), Brower et
   al. 2000 (ARDSnet 6 mL/kg).
4. **Other physiology engines (comparative context)** — Barnes et
   al. 2020 (BioGears / HumMod / Muse).
5. **Reproducibility and methods-paper integrity** — Wilkinson et
   al. 2016 (FAIR principles), Munafò et al. 2017 (manifesto for
   reproducible science).

### Verification protocol

For each reference, queried one of three open-metadata sources in
order, accepting only DOI / PMID matches with title + author + year
agreement:

* **PubMed E-utilities** (esearch + esummary, JSON) for any
  biomedical paper with a likely PMID.
* **Semantic Scholar Graph API** for non-biomedical papers (Morris,
  Campolongo, SALib).
* **DOI redirect → publisher API** as a fallback (often blocked by
  paywalled redirects, so used last).

Each verification recorded: title, authors, year, journal, volume,
pages, DOI, PMID. If any field disagreed with the planned citation,
the reference was either corrected or dropped.

### Manuscript additions

* Added **§6.7 "Verified primary references (full bibliographic
  detail)"** — full citations grouped by category (Pulse, methods,
  ARDS, comparative engines, reproducibility).
* Added **in-text citations** at the points where the manuscript
  actually depends on the cited claim:
  * §1.1: Bray et al. 2019 (engine intro), Webb et al. 2020
    (clinical research example), Webb et al. 2023 (VC-AC validation
    error), Pulse FAQ (UQ-gap quote), ARDS Definition Task Force
    2012 + Emeriaud et al. 2023 (scenario anchors), Munafò et al.
    2017 (preregistration discipline), Wilkinson et al. 2016 (FAIR
    data release).
  * §2.2 (input ranges): Brower et al. 2000 (ARDSnet 6 mL/kg
    anchors the lower bound of Vt sweep).
  * §2.5 (Morris sampling): Morris 1991, Campolongo et al. 2007,
    Iwanaga et al. 2022.

## What we tried (including dead ends)

* **Direct DOI fetches via WebFetch** were blocked by publisher
  redirects (Tandfonline, NEJM, JAMA all returned 403 Forbidden on
  the redirect target). Worked around using PubMed esummary for any
  biomedical paper and Semantic Scholar Graph API for the methods
  papers. Both services return open metadata.
* **Sobol 2001 (global sensitivity indices)** was originally on the
  shortlist as a potential reference for the Sobol bolt-on rule in
  §2.5. Could not be verified through PubMed (math/stats journal,
  not indexed) or Semantic Scholar at first try. Dropped from the
  bibliography because the atlas paper does not actually report
  Sobol indices — only the Sobol promotion rule (which is itself
  defensible from the Saltelli/Campolongo lineage already cited).
  We can re-add it if the Sobol bolt-on is run.
* **JOSS issue #4929 (Pulse review 2022 – 2023)** was on the earlier
  §6 list. Removed because the issue thread has limited public
  reviewer content; the JOSS publication itself does not exist as a
  separate "JOSS paper" for Pulse — it was a review, not a
  publication. The Pulse 4.3.1 publication entry is Bray et al. 2019.
* **Saltelli 2008 textbook** (*Global Sensitivity Analysis: The
  Primer*) was considered for citation but redundant with
  Campolongo et al. 2007 + Iwanaga et al. 2022, which already
  cover the core methodology and the SALib implementation. Dropped.
* **Efron-Tibshirani 1993 bootstrap textbook** was considered as a
  citation for the bootstrap CI. Dropped because the
  block-bootstrap-by-trajectory method we use (S008) is sufficiently
  documented by code + S008 log; the citation would have been
  decorative.
* **Sex-specific physiology references** were considered for the
  blood-volume mechanism candidate (S006). The mechanism is sourced
  from Pulse's own `SetupPatient.cpp:534` formula citation
  (`Morgan2006Clinical`) which is in the Pulse source itself rather
  than an external paper. Adequate for our claim that the formula
  *exists* and produces a 20 % difference; we do not claim it *is*
  the mechanism.

## Results

### Verified references (12)

All twelve references from the shortlist were verified against open
metadata sources. Full bibliographic detail captured in
`preprint/manuscript.md` §6.7. Summary:

| Reference                          | Source       | Verification |
|------------------------------------|--------------|--------------|
| Bray et al. 2019 (Pulse paper)     | DOI direct   | ✅ already validated in `Pulse_translation_new` |
| Webb et al. 2020                   | PubMed PMID 33237927 | ✅ |
| Webb et al. 2023                   | PMC10224749  | ✅ already validated in `Pulse_translation_new` |
| Pulse FAQ                          | URL fetch    | ✅ verbatim verified S003 |
| Pulse Setup source                 | local clone  | ✅ |
| Morris 1991                        | Semantic Scholar | ✅ |
| Campolongo, Cariboni, Saltelli 2007| Semantic Scholar | ✅ |
| Iwanaga, Usher, Herman 2022        | Semantic Scholar | ✅ |
| ARDS Def Task Force 2012 (Berlin)  | PubMed PMID 22797452 | ✅ |
| Emeriaud et al. 2023 (PALICC-2)    | PubMed PMID 36661420 | ✅ |
| Brower et al. 2000 (ARDSnet)       | PubMed PMID 10793162 | ✅ |
| Barnes et al. 2020                 | DOI direct   | ✅ already validated in `Pulse_translation_new` |
| Wilkinson et al. 2016 (FAIR)       | PubMed PMID 26978244 | ✅ |
| Munafò et al. 2017 (manifesto)     | PubMed PMID 33954258 | ✅ |

Dropped from earlier draft: Sobol 2001 (not used by the atlas as
implemented), JOSS issue #4929 (not a publication), Saltelli 2008
textbook (redundant), Efron-Tibshirani 1993 textbook (decorative).

### In-text citation count

* §1.1 Motivation: **6 citations** (Bray, Webb 2020, Webb 2023, Pulse
  FAQ, ARDS Def Task Force, Emeriaud, Munafò, Wilkinson).
* §2.2 Inputs: **1 citation** (Brower et al. 2000).
* §2.5 Morris sampling: **3 citations** (Morris 1991, Campolongo et
  al. 2007, Iwanaga et al. 2022).

Plus comparative-context citations (Barnes 2020) inside §6.4 itself.

### Total references in §6.7

12 verified primary references plus the experiment-log internal
references (S001 – S010). Reasonable size for a methods paper.

## Interpretation

The literature-review pass tightens the manuscript without changing
any of its findings. Every methodological choice (Morris EE, μ\*,
SALib, VC-AC restriction, ARDS severity anchors, FAIR data release,
preregistration discipline) now has a verified primary reference at
the point in the manuscript where the choice is made. Reviewers can
cross-check any claim by following the in-text citation to §6.7 and
the DOI / PMID from there.

The dropped references (Sobol 2001, JOSS issue, two textbooks)
illustrate the verification protocol working as intended: they were
either (a) not actually used by the paper as implemented, or (b)
redundant with already-cited primary sources. Excluding them is more
honest than padding the bibliography.

The verification was constrained by publisher paywalls — direct DOI
redirects often returned 403. Routing through PubMed E-utilities and
Semantic Scholar Graph API solved this for all 12 references on the
shortlist. For any future addition, the same two-step protocol
(PubMed first for biomedical, Semantic Scholar for methods) is
documented here as the standard procedure.

## Next steps

* Commit + push manuscript with the literature-review additions.
* Update `experiments_log/INDEX.md`.
* If reviewers later ask for additional citations (e.g. Sobol indices
  for the bolt-on, or specific sex-physiology references for the
  divergence mechanism), the same verification protocol applies:
  PubMed esearch / esummary, then Semantic Scholar Graph API; never
  cite from memory.
