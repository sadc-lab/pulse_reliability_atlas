# npj Digital Medicine Submission Package

This directory holds the **journal-submission version** of the Pulse
Reliability Atlas, targeted at *npj Digital Medicine* as an Original
Article. It is **separate from, and a strict subset of**, the audited
~92-page monograph at [`../preprint/manuscript.md`](../preprint/manuscript.md).

The monograph remains the canonical, audited, single source of truth
(195/195 PASS at the locked tolerance band). This directory contains
the condensed, journal-formatted derivative used for peer review.

---

## File layout

```
preprint_npj/
├── paper.tex                      # main manuscript (sn-jnl class, sn-nature option)
├── paper.bib                      # full copy of ../preprint/references.bib (pruned at Step 8)
├── supplement.tex                 # supplementary information document (~22 pages)
├── paper_to_monograph_map.md      # numerical-claim crosswalk for audit sync
├── figures/                       # main + supplement figure source files (PDF preferred)
├── template/                      # upstream Springer Nature LaTeX template
│   ├── sn-template.zip            # gitignored; redownloadable from Springer CMS
│   └── sn-article-template/       # extracted: sn-jnl.cls, sn-nature.bst, sample, user-manual
├── build/                         # gitignored compiled outputs (.tex aux, .pdf)
└── README.md                      # this file
```

## Build pipeline (Native LaTeX, NOT pandoc)

The npj submission is built with native LaTeX (not the
pandoc-markdown pipeline used by the monograph). This is intentional:
the Springer Nature template uses class-specific macros that pandoc
cannot generate cleanly, and the npj review process expects a
LaTeX-native submission at acceptance.

```bash
# From the repository root, build the main paper:
cd preprint_npj
pdflatex -output-directory=build paper.tex
bibtex   build/paper
pdflatex -output-directory=build paper.tex
pdflatex -output-directory=build paper.tex

# Build the supplement the same way:
pdflatex -output-directory=build supplement.tex
bibtex   build/supplement
pdflatex -output-directory=build supplement.tex
pdflatex -output-directory=build supplement.tex
```

A `build_npj.ps1` PowerShell wrapper will be added once the LaTeX
sources stabilise (Step 1).

**Document class.** `\documentclass[pdflatex,sn-nature]{sn-jnl}` —
confirmed by the upstream Springer Nature template (`sn-article.tex`
line 31) as the correct option for Nature Portfolio journals,
including the *npj* family.

**Bibliography style.** `sn-nature.bst` (Nature numbered style with
list-all-authors).

---

## The 92-page monograph vs the npj submission

| Aspect | Monograph (`../preprint/manuscript.md`) | npj submission (`paper.tex`) |
|---|---|---|
| Audience | PhD committee, Pulse community, deep technical readers | npj Digital Medicine reviewers, clinical and ML audience |
| Length | ~92 pages (markdown → PDF via pandoc) | ~12 pages main + ~22 pages supplement |
| Word count (main text) | unconstrained | ~4,200 target (npj DM concise recommendation) |
| Structure | Comprehensive: Intro → Methods → Results (8 subsections) → Discussion (7 subsections) → Conclusion → Appendices A/B/C | npj IMRaD: Abstract → Intro → Results → Discussion → Methods → closing sections |
| Internal codes (`S006`, `S018`, `F-003`, `H1`) | used throughout as cross-references to the lab notebook | **expunged** from main paper (descriptive names instead); allowed in supplement as lab-notebook cross-references |
| Lab-notebook chronology | preserved | translated to synthesized scientific prose |
| Reference style | hand-curated section §9.7 | `sn-nature.bst` formatted |
| Build pipeline | pandoc-markdown → xelatex | native pdflatex |
| Audit | `scripts/audit_claims.py` → 195/195 PASS | `scripts/audit_claims.py --check-paper-sync` (opt-in) verifies the subset that appears in paper.tex against the monograph ledger |

**Neither document is the master.** The monograph is the audited
source of scientific truth. The submission is the version that
publishes. **A change to one must propagate to the other**; see
the *Sync discipline* section below.

---

## Three-layer sync discipline

A change to a numerical claim, a methods description, or a finding
interpretation in either document is a **load-bearing scientific
edit** and must be propagated to both documents in a single atomic
commit. Three guard rails enforce this:

### Layer 1 — `paper_to_monograph_map.md` (this directory)

A crosswalk file that records every numerical claim appearing in
both documents. One row per claim: `paper_section`, `paper_context`,
`monograph_claim_id`, `expected_value`, `format_in_paper`,
`expected_occurrences`. Hand-maintained; lives in git; reviewed
on every commit that touches `paper.tex`.

### Layer 2 — `scripts/audit_claims.py --check-paper-sync`

Read-only audit extension. Opt-in flag (does not affect the default
audit invocation, which continues to verify the monograph alone).
When invoked, reads the crosswalk, regex-extracts each value from
`paper.tex` with LaTeX-tolerant patterns
(`4,082.24` / `4{,}082.24` / `\num{4082.24}` / `4082.24~mL`), uses
`re.findall(...)` to count occurrences, and FAILs on any of:

* count != `expected_occurrences` (catches silent deletions and
  accidental duplications)
* found value contradicts `expected_value`
* `monograph_claim_id` doesn't exist in the ledger or the monograph
  value has drifted

Graceful degradation: if `paper.tex` or the map file is missing,
the audit emits a `WARN` and continues with the legacy 195-claim
ledger unaffected.

### Layer 3 — atomic dual-commit convention

Every commit that changes scientific content in either document
follows one of three tagged patterns in the commit message:

* `S0XX [SCIENTIFIC]: <summary>` — a load-bearing scientific change
  that **must** touch both `preprint/manuscript.md` and
  `preprint_npj/paper.tex` (and the crosswalk map). Commit body
  must explicitly describe:
  * What changed in the monograph prose (with section ref).
  * What changed in the paper prose (with section ref).
  * Which crosswalk-map rows were added/updated.
  * Whether the audit total changed.
* `S0XX [TYPESET-ONLY]: <summary>` — typography, LaTeX-macro,
  formatting, or layout changes that touch **only** `paper.tex`
  (or the template) and do **not** change any numerical value or
  interpretive claim. Audit must verify no map-tracked values
  changed.
* `S0XX [MONOGRAPH-ONLY]: <summary>` — change confined to the
  monograph (`preprint/manuscript.md`) that the map says is **not**
  mirrored in `paper.tex`. Audit verifies `paper.tex` is
  byte-untouched.

Commits that violate the convention (e.g., scientific change in one
document without the corresponding update in the other) are caught
by the audit at the next `--check-paper-sync` invocation.

---

## Sourcing the upstream LaTeX template

The Springer Nature template is shipped at:

```
https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/18782940/data/v12
```

(direct ZIP download, ~880 KB, dated 2024-12-13, fetched and
verified 2026-05-23 during Step 0 of the npj-splitting work). The
class file `sn-jnl.cls` declares
`\ProvidesClass{sn-jnl} [2019/11/18 v0.1: An authoring template for
Springer Journal articles]`.

The ZIP is gitignored (`preprint_npj/template/sn-template.zip`);
its extracted contents under `preprint_npj/template/sn-article-template/`
are committed because they include the class file, bibliography
styles, the example article, and the user manual that
`paper.tex` depends on. The example
(`sn-article-template/sn-article.tex`) and the user manual
(`sn-article-template/user-manual.pdf`) are the canonical references
for macro syntax.

---

## Status

* **Step 0 — Scaffold + template + crosswalk:** ✓ complete
  (this commit).
* **Step 1 — Title + Abstract + Methods stub + author block:** in
  progress.
* **Steps 2–10:** scheduled per the S028 splitting blueprint.
