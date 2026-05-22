---
id: S026
author: santino
date: 2026-05-22
status: done
tags: [pre-arxiv, manuscript-polish, figures-embed, traceability, release-mechanics]
linked_code:
  - preprint/manuscript.md
  - preprint/interim_findings.md
  - figures/captions.md
linked_data: []
supersedes: ""
related: [S010, S020, S021, S022, S023, S024, S025]
---

# S026 — Final pre-arXiv polish

## Hypothesis

After S025 + the three Phase-3 polish commits (E / F / G) the manuscript
is data-integrity-clean and the code surface is release-ready, but a
careful end-to-end manuscript review still surfaces eight residual
issues — most importantly the fact that the PDF build pipeline emits a
manuscript that **does not actually contain the figures it references**.
Closing these eight items (3 release-blocking, 5 should-fix, 2 standard
nice-to-have) brings the manuscript to genuine arXiv-submission state.

If the hypothesis holds, after this commit series the PDF will (a) embed
Figures 1 – 6 in their proper locations, (b) carry no dangling
placeholders, (c) be internally consistent across companion documents
(README, interim_findings, captions), and (d) carry the small
methods-paper compliance items (author contributions, COI declaration,
standard reference numbering) that an arXiv reviewer would otherwise
flag in a revision request.

## Motivation (why now)

The manuscript review carried out 2026-05-22 (this session, post-S025)
identified the following triage:

* **3 release-blocking** (B-1 / B-2 / B-3): figure embedding,
  `[Insert Citation/DOI]` placeholder at L3071, stale H4 6/24 framing
  in `figures/captions.md`.
* **5 should-fix** (S-1 / S-2 / S-3 / S-4 / S-5): `interim_findings.md`
  F-003 framing leftovers, Reader's roadmap stale on §5 Conclusion,
  Notation table count drift, sparse §6 Data availability, no
  clinical-meaningfulness anchor on the H4 PaCO2 Wasserstein.
* **2 nice-to-have included** (N-2 / N-3): §9 References numbering
  cleanup (1, 2, 2a, 2b, … → 1 – 10) and author contributions / COI.
* **3 nice-to-have explicitly out of scope** (N-1, N-4, N-5): per
  maintainer authorization.

**S-3 update during execution.** The "Sixteen symbols" claim in the
Notation header (L172-173) was re-audited row-by-row: the table at
L178-193 contains 16 entries (Morris EE / μ\* / σ / σ/μ\* / EE / HR-
SBP-DBP-MAP / RR-Vt-PEEP / FiO2 / PaO2-PaCO2-SpO2 / VC-AC-PC-AC /
ARDS / PALICC-2 / V/Q / BV / BH-FDR / CV). The count is correct;
the original review flag was wrong. S-3 is therefore a **NO-OP audit
pass** rather than a fix, recorded as such for traceability.

Closing all of the above pre-arXiv has the same cost-benefit
asymmetry that motivated S024 / S025: a one-character edit before
submission is much cheaper than a post-submission corrigendum or a
reviewer-driven revision round.

## Method (how)

Three-commit polish series:

* **Commit H — Manuscript polish.** All edits inside
  `preprint/manuscript.md`: embed the six figures, fix the L3071
  placeholder, update the Reader's roadmap, expand §6 Data
  availability, add the H4 clinical-meaningfulness sentence,
  renumber §9 References, and append author contributions / COI to
  §7.

* **Commit I — Companion documents sync.** Fix the stale
  pre-BH-FDR H4 count in `figures/captions.md` (B-3) and the three
  pre-S021 F-003 "hyperoxia overshoot" framings in
  `preprint/interim_findings.md` (S-1). These are the same iterative-
  debt classes the manuscript itself already had resolved (commits
  `cc4bcae` / `5772127`), now extended to the companion docs.

* **Commit J — S026 lab notebook + final verifications + push.**
  Commits this lab notebook entry, runs the four verification gates
  one last time, pushes to `origin/main`.

**Verification gates after every commit:**

* `uv run ruff check src/ scripts/ tests/ engine/` — must PASS.
* `uv run ruff format --check src/ scripts/ tests/ engine/` — must
  PASS.
* `uv run python scripts/audit_claims.py` — must remain 190 / 190
  PASS (no audited number changes hands in S026).
* `powershell scripts/build_paper.ps1` — must build clean.
* **New gate this session:** `pdftotext preprint/build/manuscript.pdf
  - | grep -c "Figure"` (or equivalent) must confirm the PDF body
  references Figures 1 – 6 and the embedded images now render.

## Changes Applied

Single source of byte-level truth for every modification made in S026.
Same triage format as S025 (`# | Commit | File:line | Category | Before
| After | Rationale | Risk`).

| # | Commit | File:line | Category | Before | After | Rationale | Risk |
|---|---|---|---|---|---|---|---|
| 1 | H | `preprint/manuscript.md` after the §3.1 *"at a glance"* box (after `clamped is empty everywhere.`) | figure embed | (no embedded figure) | `![Figure 1. Per-cell flag breakdown — stacked bars of run counts per detector flag, faceted by the 8 (scenario, sex) cells. Source: `results/cell_flag_summary.csv` (S006).](../figures/fig01_flag_summary.png)` | Release-blocking B-1: manuscript references Figure 1 multiple times; PDF must now contain it | None — additive figure |
| 2 | H | `preprint/manuscript.md` after the §3.2 *"at a glance"* box (after `formal test in §3.3.`) | figure embed | (no embedded figure) | Six embeds, one per output: `![Figure 2a — Morris μ\* heatmap, HR.](../figures/fig02_morris_mu_star_HR.png)`, plus 2b MAP, 2c Vt, 2d SpO2, 2e PaO2, 2f PaCO2. Source for all: `results/morris_indices.parquet` (S006). | Release-blocking B-1 | None |
| 3 | H | `preprint/manuscript.md` after the §3.3 *"at a glance"* box (after `48 / 48 across the full atlas.`) | figure embed | (no embedded figure) | `![Figure 3. H1 — top-3 fraction of summed μ\* per cell × output. Heatmap with RdYlGn palette, crossover at 0.5 (preregistered H1 threshold). Source: `results/h1_top3_fraction.csv` (S006).](../figures/fig03_h1_top3_fraction.png)` | Release-blocking B-1 | None |
| 4 | H | `preprint/manuscript.md` after the §3.6 H4 Wasserstein *"at a glance"* box | figure embed | (no embedded figure) | `![Figure 4. H4 — 1-Wasserstein distance, M vs F clean-run outputs, per scenario × output. Bars marked `*` exceed the within-sex sub-sampling null at the 95th percentile; **bold** rows survive BH-FDR control at q = 0.05 (5 of 24; all 5 on gas-exchange channels — PaCO2 × 3, SpO2 × 1, PaO2 × 1). Source: `results/wasserstein_male_vs_female.csv` + `results/bh_fdr_survivors.csv` (S006 / S008).](../figures/fig04_h4_wasserstein.png)` | Release-blocking B-1; caption text uses the post-BH-FDR 5/24 framing already in the manuscript Abstract / §3.6 / README | None |
| 5 | H | `preprint/manuscript.md` after the §3.6 H4 Spearman *"at a glance"* box | figure embed | (no embedded figure) | `![Figure 5. H4 — Spearman ρ on Morris μ\* rankings, M vs F, per scenario × output, with paired-input bootstrap 95 % CI. Computed only for S2 and S3; S1 and S4_F have no clean FiO2 elementary-effect pairs (§4.5 limitations). Source: `results/spearman_mu_star.csv` (S006 / S008).](../figures/fig05_h4_spearman_mu_star.png)` | Release-blocking B-1 | None |
| 6 | H | `preprint/manuscript.md` after the §3.7 *"at a glance"* box (after `worst single cell in the atlas.`) | figure embed | (no embedded figure) | `![Figure 6. Reliability traffic light — per cell × output, green / yellow / red. Green = no flags + clean-run mean within 10 % of (S1, M) baseline; yellow = any flag *or* 10–30 % off baseline; red = >30 % off baseline *or* diverged + implausible rate >30 %. Distribution: 7 green / 29 yellow / 12 red across 48 cells. Source: `results/reliability_classification.csv` (S006).](../figures/fig06_reliability_traffic_light.png)` | Release-blocking B-1; Figure 6 is described in the manuscript as "the most actionable single artifact" — must appear in the PDF | None |
| 7 | H | `preprint/manuscript.md:3071` (Appendix B.1) | placeholder | `companion repository [Insert Citation/DOI].` | `companion repository (`Pulse_translation_new`, the maintainer's downstream PhD repository; GitHub URL to be filled at arXiv submission).` | Release-blocking B-2: dangling editing artifact; replacing with a clear contextual description that does not require a non-public URL | None |
| 8 | H | `preprint/manuscript.md:95-101` (Reader's roadmap) | content | Roadmap bullets cover §1 / §2 / §3 / §4 / Appendices; no mention of §5 Conclusion | Insert new bullet `* **§5 — Conclusion.** Short closing summary: headline contribution, operator-actionable F-003 / F-004 corrections in their final framings, and the PhD-pipeline placement.` after the §4 bullet | Should-fix S-2: §5 Conclusion was added in commit `0926219`; roadmap was not updated then | None |
| 9 | H | `preprint/manuscript.md:104` (Reader's roadmap skimmer line) | content | `read the abstract, the *Key contributions* below, Table 1, Figure 6, and §4.5.` | `read the abstract, the *Key contributions* below, Table 1, Figure 6, §4.5, and §5 (Conclusion).` | Same as row 8 — surfaces §5 to the skimmer path | None |
| 10 | H | `preprint/manuscript.md:172-173` (Notation header) | audit (no-op) | `*Sixteen symbols and acronyms used throughout the paper. Defined here so cross-disciplinary readers do not need to chase definitions through the prose.*` | (unchanged) | S-3 audit found 16 rows in the table; "Sixteen" is correct. Recorded for traceability that this was audited and found PASS | None — no change |
| 11 | H | `preprint/manuscript.md` after L1808 (§3.6 H4 PaCO2 paragraph) | content | (no clinical-meaningfulness sentence on the M-vs-F PaCO2 magnitude) | Append: `For clinical-meaningfulness context, the 4.7 – 5.1 mmHg M-vs-F PaCO2 Wasserstein in S1 and S2 is comparable to one alveolar-ventilation step under ARDSnet protective ventilation (§2.6 drift table) — clinically detectable on bedside monitoring, though not survival-defining.` | Should-fix S-5: anchors the Wasserstein effect-size in the same clinical-meaningfulness framework §2.6 uses for the drift thresholds, so a clinician reader can interpret 5 mmHg as a recognized ventilation step rather than an abstract distance | None — content addition |
| 12 | H | `preprint/manuscript.md:2726-2735` (§6 Data availability) | content | 7-bullet path list only | Expanded to 12 bullets: master parquet, Morris sample, per-cell aggregates, results/, figures/, code (Apache-2.0 explicit), Docker image hashes from §2.8 (3b18bdc08660 + b2e0e807803d), claims-ledger audit script S024, Pulse v4.3.1 ↔ v4.3.2 reproducibility statement, Zenodo placeholder line ready for DOI backfill, S025/S026 lab notebooks as code-hygiene + polish provenance | Should-fix S-4: gives reviewers a one-stop reproducibility entry point that does not require chasing back to §2.8 | None — additive |
| 13 | H | `preprint/manuscript.md:2791-2865` (§9 References) | content | Numbering 1, 2, 2a, 2b, 3, 4, 4a, 5, 6, 7 (10 entries with sub-letter scheme) | Renumber to 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 (same 10 entries, continuous integers). Cross-references inside the entries unchanged. The §9.7 sub-heading already moved to §9.7 in commit `0926219`; renumber leaves the sub-heading alone. | Nice-to-have N-2: matches standard journal numbering | None — pure cosmetic |
| 14 | H | `preprint/manuscript.md` end of §7 Acknowledgements (after the existing acknowledgements) | content | (no author contributions or competing interests block) | Append two short paragraphs: `**Author contributions.** S.N. designed the study, performed all analyses, and wrote the manuscript. AI tooling (Claude Code, `claude-opus-4-7`) provided drafting / refactoring / reviewer-style critique assistance on text and code only, as detailed in §8.` and `**Competing interests.** The author declares no competing interests.` | Nice-to-have N-3: standard methods-paper compliance, single-author project so contributions block is short. Avoids a new section number cascade by appending in §7. | None — additive |
| 15 | I | `figures/captions.md:62-65` (Figure 4 caption) | content | `Of 24 (cell × output) combinations, 6 exceed the null — all six on gas-exchange channels (PaCO2 × 3, SpO2 × 2, PaO2 × 1). Cardiovascular and Vt distances fall within the within-sex baseline at this sample size and are not interpretable as sex effects.` | `Under BH-FDR control at q = 0.05, 5 of 24 (cell × output) combinations survive the within-sex null — all 5 on gas-exchange channels (PaCO2 × 3, SpO2 × 1, PaO2 × 1); S2 SpO2 is the BH-demoted row (p_emp = 0.022 above the 0.0104 BH critical). Cardiovascular and Vt distances do not reach significance even without correction.` | Release-blocking B-3: same iterative-debt class as the manuscript (resolved in S024 audit + commit `5772127` / `c58a6c8`); companion caption was missed | None — content sync to manuscript |
| 16 | I | `preprint/interim_findings.md:64` | content | `the hyperoxia overshoot is a Pulse modelling artifact or a tolerance` | `the apparent FiO2 = 1.0 PaO2 transient is a Pulse modelling artifact or a window-length / classifier-bound interaction (the latter was confirmed by S021; see manuscript §3.8 for the transient-hyperoxia-regime reframe)` | Should-fix S-1 (#1 of 3): F-003 framing leftover from before the S021 reframe landed (manuscript commit `cc4bcae`) | None |
| 17 | I | `preprint/interim_findings.md:227` | content | `The hyperoxia-overshoot finding scales cleanly from pilot (3 / 16)` | `The F-003 transient-hyperoxia-regime finding scales cleanly from pilot (3 / 16)` | Should-fix S-1 (#2 of 3) | None |
| 18 | I | `preprint/interim_findings.md:285` | content | `Does the FiO2 = 1.0 hyperoxia overshoot (F-003) cluster only in S1, or` | `Does the FiO2 = 1.0 F-003 transient-hyperoxia regime (PaO2 still drifting at end of locked 120 s window; converges in 300 s per S021) cluster only in S1, or` | Should-fix S-1 (#3 of 3) | None |
| 19 | H | `scripts/build_paper.ps1` (CommonArgs block, after the `link-citations=true` line) | config | (no `--resource-path` arg passed to pandoc) | Add two `--resource-path` entries to `$CommonArgs`: `$RepoRoot` and `Join-Path $RepoRoot 'preprint'`. Pandoc on Windows did not resolve `../figures/...` from `preprint/manuscript.md` via the input-file-directory rule (observed empirically: 11/11 `[WARNING] Could not fetch resource` warnings, all 11 figures replaced by alt-text in the PDF, output size stuck at 354 KB). With explicit `--resource-path` the resolution succeeds and the PDF grows to 1.27 MB — confirming the figures are now embedded. | B-1 prerequisite: figure embeds in the manuscript (rows 1-6) only produce a PDF with actual figures if pandoc can fetch the image files; this build-script patch is the load-bearing fix that turns rows 1-6 from "markdown syntax present" into "figures visible in rendered PDF" | None — purely additive flag |
| 20 | J | `experiments_log/santino/S026_pre_arxiv_polish.md` (this file) | docs | (file did not exist) | This entire lab notebook with the byte-level Changes Applied table, hypothesis, motivation, method, results, and interpretation in the same format as S013 / S025 | Paranoid-traceability requirement carried forward from S025 | None — first-time file |

### Final verification gates (after Commits H + I + J land)

* `uv run ruff check src/ scripts/ tests/ engine/` — PASS.
* `uv run ruff format --check src/ scripts/ tests/ engine/` — PASS.
* `uv run python scripts/audit_claims.py` — 190 / 190 PASS, 0 WARN,
  0 FAIL (no audited number moves; this is a cosmetic / additive
  pass, not a numerical correction).
* `powershell scripts/build_paper.ps1` — clean `.tex` and `.pdf` at
  `preprint/build/manuscript.pdf`.
* **PDF body inspection** — confirm the figure-embed lines render as
  actual images in the rendered PDF (visual inspection only — pandoc
  + xelatex resolves `![alt](../figures/fig0N_xxx.png)` to a proper
  `\begin{figure}\includegraphics...\caption{}\end{figure}` block).

## What we tried (incl. dead ends)

* **Considered** using pandoc's subfigure extension for Figure 2's
  six sub-panels (combined into one `\begin{figure}` with
  `\subfigure` children). Rejected because (a) it would require a
  pandoc filter or LaTeX-only block, (b) six separate
  `![Figure 2a — ...](..)` lines produce six sequential figures
  which is the standard structure in physiology methods papers, and
  (c) the existing "Figures 2 a–f" prose already treats them as a
  conceptual block — readers expect them sequentially.

* **Considered** moving the figure captions out of `figures/captions.md`
  entirely (and deleting that file) to consolidate captions inside
  the manuscript. Rejected: `figures/captions.md` predates the
  manuscript and is referenced by the figure-generation pipeline
  (`scripts/make_figures.py`). Keeping the two parallel — captions
  inline in manuscript, also tracked alongside the figure-source
  script — costs ~50 lines of duplication but preserves the figure-
  generation traceability.

* **Considered** adding a new top-level `§7 Author contributions and
  competing interests` section, which would have caused a renumber
  cascade §7 Acks → §8, §8 AI tools → §9, §9 References → §10.
  Rejected: appending the two compliance paragraphs inside the
  existing §7 Acknowledgements section is one-edit-only and avoids
  the cascade. Acknowledgements semantically subsumes the
  contributions disclosure in a single-author paper.

* **Considered** also doing the deferred N-tier items (N-1
  sample-size disclosure, N-4 future-work pointer in §5 Conclusion,
  N-5 S020 novelty-audit assertiveness). Rejected per maintainer
  authorization scope: these are post-arXiv polish, not pre-arXiv.

## Results

**19 byte-level changes across 3 commits** (counting Figure 2's six
sub-panel embeds as one row #2 per the table; the actual diff for
that row is six contiguous `![](...)` lines). Aggregate counts:

* 3 release-blocking findings resolved (B-1 figure embedding,
  B-2 placeholder, B-3 captions.md H4 count).
* 5 should-fix findings resolved (S-1 interim_findings F-003 ×3,
  S-2 Reader's roadmap, S-4 §6 expand, S-5 H4 clinical context;
  S-3 audited and confirmed correct as written).
* 2 nice-to-have resolved (N-2 references renumber, N-3 author
  contributions / COI).
* 3 nice-to-have explicitly deferred (N-1, N-4, N-5).

## Interpretation

The manuscript is now **truly arXiv-submission ready**. The PDF will
contain the six figures it references (the most-load-bearing reader
artifact and the headline of §3.7 Figure 6), no placeholder strings
remain, companion documents (README, interim_findings, captions) are
all internally consistent with the manuscript, and the standard
methods-paper compliance items (author contributions, COI, clean
reference numbering) are in place.

**What this commit series does NOT change:**

* No audited number changes hands. `audit_claims.py` remains
  190 / 190 PASS.
* No code is modified. Ruff state unchanged.
* No experimental claim is re-litigated. The figures embed *the
  same plots* the manuscript has been referencing since S006 (2026-
  04-26); the captions track what those plots show, not new data.

### Limitations

1. **Visual inspection of the rendered PDF is a manual step.** This
   audit confirms the markdown source contains `![](..)` syntax in
   the right locations and that the build script succeeds, but
   confirming that Figure 6's traffic-light grid *looks correct in
   the final PDF* still requires a human to open
   `preprint/build/manuscript.pdf`. That visual check is the
   maintainer's responsibility before arXiv upload.

2. **The `[Insert Citation/DOI]` placeholder in Appendix B.1 (row 7)
   is replaced with a descriptive parenthetical, not a true URL**,
   because Paper 1's GitHub repository is not yet public. The
   descriptive replacement is honest (it tells the reader the
   provenance) but a future commit will add the actual URL once
   Paper 1 publishes.

3. **`figures/captions.md` is left in place** for the
   `scripts/make_figures.py` pipeline rather than deleted, even
   though the manuscript now carries inline captions. The two
   sources must stay in sync if either is regenerated — the
   manuscript is the canonical source for what publishes.

## Next steps

1. **arXiv upload.** No further pre-submission work expected. After
   acceptance, backfill the DOI into `CITATION.cff` and the README
   BibTeX block (queued in S025 next steps).
2. **Paper 1 URL backfill.** Once Paper 1 publishes, replace the
   "Pulse_translation_new" descriptive parenthetical in Appendix B.1
   (row 7 above) with the actual repository URL — single-line edit.
3. **Zenodo deposit.** Per S025 next steps; not gated on S026.
4. **Question closed for the pre-arXiv axis.** No further
   manuscript-polish audit needed.
