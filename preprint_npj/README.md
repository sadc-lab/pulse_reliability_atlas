# npj Digital Medicine submission package

This directory holds the journal version of the Pulse Reliability Atlas: the
article and its Supplementary Information, prepared for arXiv and for
*npj Digital Medicine*. The 123-page companion monograph
([`../preprint/manuscript.md`](../preprint/manuscript.md)) remains the
audited source of truth; this is its condensed, journal-formatted
derivative. The article drops the lab-notebook codes (`S006`, `F-003`, …)
that the monograph uses; the supplement keeps them as cross-references. The
project overview, the audit layers and the reproduction recipe are in the
[root README](../README.md).

**Status.** Re-freeze 63 (2026-10-19) is the version sent to the co-authors
and the one to post on arXiv and submit. Every freeze, with its hashes, gate
state and dispatch, is recorded in [`dispatch_log.md`](dispatch_log.md).

## Contents

```
preprint_npj/
├── paper.tex                   the article (sn-jnl class, sn-nature option)
├── supplement.tex              the Supplementary Information
├── paper.bib                   the bibliography of both documents
├── paper_to_monograph_map.md   crosswalk: each number of the article and its ledger entry
├── figures/                    figure sources (PDF preferred)
├── README_FIGURES.md           how each figure is produced
├── cover_letter.md             letter to the editor (date and preprint details added on submission)
├── submission_metadata.txt     portal fields (title, abstract, authors, ORCID, contributions)
├── reporting_summary_draft.md  working draft of the Nature Portfolio reporting summary
├── dispatch_log.md             every freeze: hashes, gate state, dispatch
├── build_npj.ps1               build script (PDF and Word)
├── sn-jnl.cls, sn-nature.bst   template class and reference style used by the build
├── nature.csl, docx_pdf_to_png.lua   used by the Word conversion
├── template/                   Springer Nature LaTeX template (see below)
└── build/                      gitignored outputs (.pdf, .docx) and frozen copies (freezeNN/)
```

## Build

```powershell
# From the repository root. Builds the supplement first (the paper reads
# supplement.aux through \externaldocument), then the paper, each as PDF
# and as a Word twin.
powershell -NoProfile -ExecutionPolicy Bypass -File preprint_npj/build_npj.ps1
```

`-MainOnly` and `-SupplementOnly` build a single document. The build is
native LaTeX (`\documentclass[pdflatex,sn-nature]{sn-jnl}`, `sn-nature.bst`),
not the pandoc pipeline of the monograph. It is not byte-reproducible, so
every version that leaves the repository is frozen first: its four files are
hashed, copied to `build/freezeNN/`, and the hashes are recorded in
`dispatch_log.md`.

## Keeping the article and the monograph in step

A number that appears in both documents changes in both, in one commit.
Three guard rails:

1. `paper_to_monograph_map.md`: one row per number, with where it appears,
   the ledger entry behind it, its expected value and its expected number of
   occurrences.
2. `uv run python scripts/audit_claims.py --check-paper-sync`: counts each
   number across the combined `paper.tex` + `supplement.tex` and fails on a
   missing or extra occurrence, on a value that disagrees with the map, or on
   a ledger entry that is missing or has drifted. It runs in CI on every push.
3. Rebuild after every edit: `build/` is ignored by git, so a stale PDF does
   not show in `git status`.

## Citation rule

Every reference must exist, with exact bibliographic detail, and its content
must support the sentence that cites it. Pulse's own publications
(`bray2019`, `webb2020`, `webb2022vent`) document what the Pulse team did,
not adoption by others; the third-party work cited is one assessment of
Pulse (`cornish2023`) and one use of Pulse-generated data
(`ward2024ventilator`). The verification record is
[`../audit/reference_audit.md`](../audit/reference_audit.md).

## Springer Nature template

The class file and reference style come from the Springer Nature LaTeX
template, a ZIP dated 2024-12-13 fetched on 2026-05-23 from:

```
https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/18782940/data/v12
```

The ZIP is gitignored (`template/sn-template.zip`); its extracted contents in
`template/sn-article-template/` (class file, reference styles, example
article, user manual) are committed. `sn-jnl.cls` declares
`\ProvidesClass{sn-jnl} [2019/11/18 v0.1: An authoring template for Springer
Journal articles]`.
