---
id: S025
author: santino
date: 2026-05-22
status: done
tags: [oss-release, pre-submission, manuscript-polish, reviewer-defense, readme-audit, traceability]
linked_code:
  - scripts/validate_detector_on_existing_runs.py
  - scripts/diagnostic_waveform_inspect.py
  - src/detector.py
  - README.md
  - .gitattributes
  - CITATION.cff
  - preprint/manuscript.md
  - preprint/audit_phase1_findings.md
linked_data: []
supersedes: ""
related: [S013, S014, S021, S022, S023, S024]
---

# S025 — Pre-release OSS code-hygiene audit and fixes

## Hypothesis

The codebase, README, and ancillary release-mechanics files are ready
for the external-researcher Open Source audience: no hardcoded absolute
paths in shipped scripts, no iterative-debt content in the README, no
missing release-mechanics files (CITATION.cff / .gitattributes), no
PEP 8 / format drift, no docstring debt on the most-edited modules.

If the hypothesis holds the repo is publish-ready alongside the preprint.
If it fails (which it did — 3 release-blocking + 14 should-fix + 7
nice-to-have findings) the changes are documented row-by-row in the
"Changes Applied" table below so future-us can trace every byte that
moved between the experimental endpoint and the released version.

## Motivation (why now)

The session arc that landed in commit `c58a6c8` closed the **manuscript**
data-integrity question (S024 verified 190/190 claims). What remained
was the **codebase + README + release-mechanics** layer — a different
surface that S024 did not touch. The two release-blocking README issues
(B2: F-003 framing, B3: H4 5-vs-6 numerical drift) are exactly the kind
of iterative debt an external reviewer would find embarrassing if the
maintainer missed it pre-arXiv.

The paranoia-driven traceability requirement on this entry: every code
change must leave a *written byte-level trail* so a future maintainer
running an old experiment that suddenly returns different numbers can
diff this table against the relevant commit and answer "did the
hygiene pass change the code in a way that explains my new error?" in
30 seconds, not 30 minutes.

## Method (how)

**Phase 1 — read-only audit (this morning, 2026-05-22).** Five
sub-passes:

1. *Dependency hygiene.* `uv sync --frozen --all-extras --dry-run` to
   verify lockfile is current; spot-checked `scikit-learn` and `shap`
   declarations in `pyproject.toml`.
2. *Absolute path sweep.* Grep `C:[\\/]Users|/home/|/Users/|Pulse_engine_adults_Gitlab|\\santi\\`
   across `src/`, `scripts/`, `engine/`, `tests/`, `preprint/`.
3. *Lint + format.* `uv run ruff check src/ scripts/ tests/ engine/`
   (PASS — pre-commit hook is doing its job) and `uv run ruff format
   --check ...` (FAIL — 39 files would reformat; format not gated).
4. *Docstring completeness.* Read-through of `src/detector.py` module
   + class + function docstrings; same for the four S022 / S023 helper
   scripts. Bar: LEAN philosophy (WHAT + cross-ref to manuscript, no
   duplication of manuscript content).
5. *README + release-mechanics extras.* LICENSE / CITATION.cff /
   `.gitattributes` presence checks; Docker image-hash pin
   cross-check (manuscript §2.8 ↔ engine wrapper ↔ README);
   end-to-end smoke-test one-liner check.

The full diagnostic report (24 findings: 3 release-blocking, 14
should-fix, 7 nice-to-have) was output to the terminal and reviewed
before fixes were authorized. **No edits in Phase 1.**

**Phase 2 — authorized fixes, four logical commits.** Each commit
references the row range it touches in the *Changes Applied* table
below.

* **Commit A — RELEASE-BLOCKING + README iterative debt (rows 1–13).**
  Fixes the absolute path in
  `scripts/validate_detector_on_existing_runs.py` and brings the README
  in line with the post-2026-05-22 manuscript: F-003 transient
  hyperoxia framing, H4 BH-FDR 5-of-24 number, H3 regime qualifier,
  Vt CV median-vs-worst-case distinction, §1.4-style S001-S024
  boundary, missing data-runs / results-s022 / results-s023 layout
  entries, `uv sync --extra ml` instruction, pinned Docker image
  hashes from manuscript §2.8, end-to-end smoke-test one-liner.

* **Commit B — code formatting + docstring cross-refs (rows 14–16).**
  `uv run ruff format src/ scripts/ tests/ engine/` (39 files, pure
  whitespace / line-break-in-args), `src/detector.py` module docstring
  acquires a manuscript / lab-notebook cross-reference paragraph, and
  `scripts/diagnostic_waveform_inspect.py` docstring renames "Aliasing
  check" to "Samples-per-breath diagnostic" per the S022 retraction
  block.

* **Commit C — release-mechanics extras (rows 17–19).**
  `.gitattributes` (stops the CRLF-warning noise every Python commit
  has been emitting this session), BibTeX block in the README, and
  CITATION.cff placeholder (DOI fields blank until arXiv acceptance).

* **Commit D — preprint provenance polish (rows 20–21).**
  Two occurrences of the maintainer's developer-local Pulse clone path
  (`C:/Users/santi/projets/Pulse_engine_adults_Gitlab/engine`) in
  `preprint/manuscript.md` (§8 References) and
  `preprint/audit_phase1_findings.md` swapped for the upstream GitLab
  URL + commit SHA.

**Verification gates after each commit (and at the end):**

* `uv run ruff check src/ scripts/ tests/ engine/` — must PASS.
* `uv run ruff format --check src/ scripts/ tests/ engine/` — must
  PASS after Commit B.
* `uv run python scripts/audit_claims.py` — must remain 190/190 PASS
  (re-run after any preprint or detector change).
* `powershell scripts/build_paper.ps1` — must build clean after any
  preprint change.

## Changes Applied

Single source of byte-level truth for every modification made in S025.
Future maintainer protocol: if an experiment that previously worked
fails after a `git pull` that included these commits, diff the
relevant row's `Before` vs `After` against the failing line to triage
"hygiene change" vs "real regression" in seconds.

| # | Commit | File:line | Category | Before | After | Rationale | Risk |
|---|---|---|---|---|---|---|---|
| 1 | A | `scripts/validate_detector_on_existing_runs.py:33` | path | `TRANSLATION_DIR = Path(r"C:\Users\santi\projets\Pulse_translation_new\data\engine_runs")` | `_DEFAULT = "../Pulse_translation_new/data/engine_runs"; TRANSLATION_DIR = Path(os.environ.get("PULSE_TRANSLATION_RUNS_DIR", _DEFAULT))` (+ `import os`; behavior unchanged when env var unset and default relative path doesn't exist — script still gracefully returns empty list) | Release-blocking (B1): external researchers cannot run the script with the hardcoded path; env-var override preserves dev-mode default | None — script already handled missing dir gracefully at L38-39 |
| 2 | A | `README.md:74-78` (Plain-language summary) | content | "Healthy male and female adults at FiO2 = 1.0 produce **PaO2 above 600 mmHg with ongoing drift** — a probable Pulse hyperoxia overshoot." | "Healthy male and female adults at FiO2 = 1.0 produce **PaO2 above 600 mmHg, still drifting at the end of the locked 120 s window** — a *transient hyperoxia regime* (S021): under a 300 s rerun, PaO2 converges to a plateau ~ 10 mmHg below the alveolar-gas-equation prediction (~ 643 mmHg vs ~ 653 mmHg predicted), consistent with Pulse's modelled A-a gradient — not an overshoot." | Release-blocking (B2 #1): old "overshoot" framing was retracted by S021 + manuscript commit cc4bcae | None — content sync to manuscript Abstract |
| 3 | A | `README.md:115-117` (F-003 headline result) | content | "**F-003** — 34 healthy / severe-ARDS runs produce PaO2 > 600 mmHg at FiO2 = 1.0, still drifting at t = 120 s. Hyperoxia overshoot in Pulse's oxygenation model." | "**F-003** — 34 implausibly-flagged runs produce PaO2 > 600 mmHg at FiO2 = 1.0 (91 % at FiO2 ≥ 0.95), still drifting at t = 120 s. *Transient hyperoxia regime*: under a 300 s rerun (S021), PaO2 converges to a plateau ~ 10 mmHg below the alveolar-gas-equation prediction — consistent with Pulse's modelled A-a gradient. The original flag reflects (a) the locked 120 s window being insufficient and (b) the conservative classifier bound, not an overshoot. See `preprint/manuscript.md` §3.8." | Release-blocking (B2 #2): same retraction | None |
| 4 | A | `README.md:111` (H4 row of Headline-results table) | content | "**Partially supported (gas-exchange only)** — 6 of 24 cell × output Wasserstein distances exceed the within-sex sub-sampling null; all 6 are gas-exchange (PaCO2 × 3, SpO2 × 2, PaO2 × 1)." | "**Partially supported (gas-exchange only)** — under Benjamini–Hochberg FDR control at q = 0.05, **5 of 24** cell × output Wasserstein distances survive the within-sex null; all 5 are gas-exchange (PaCO2 × 3, SpO2 × 1, PaO2 × 1). The naive-α = 0.05 analysis would flag 6; S2 SpO2 (p_emp = 0.022) is demoted by BH-FDR." | Release-blocking (B3): pre-BH-FDR number; manuscript abstract reports 5/24 post-correction; SpO2 multiplicity differs | None — content sync |
| 5 | A | `README.md:71-72` (Plain-language summary, H3) | content | "Its solver diverges in **1.6 %** of our runs, and **all 20 divergent runs are in male patient cells** — the first quantitative sex-specific reliability finding for Pulse." | "Its solver diverges in **1.6 %** of our runs, and **all 20 divergent runs are in male patient cells in the Morris input-extreme regime** — the first quantitative sex-specific reliability finding for Pulse. (At midrange inputs, a complementary continuous-severity sweep shows divergence is approximately sex-balanced — the sex effect is regime-dependent; see manuscript §3.5.1.)" | Should-fix (S4 #1): same regime qualifier we added to manuscript Abstract in commit 2abfb58 | None |
| 6 | A | `README.md:110` (H3 row of Headline-results table) | content | "**PASS** — 1.6 % overall divergence rate. **All 20 divergent runs are male.**" | "**PASS** — 1.6 % overall divergence rate. **All 20 divergent runs are male in the Morris input-extreme regime** (the complementary continuous-severity sweep at midrange inputs shows divergence approximately sex-balanced inside the [0.879, 0.945] band — see §3.5.1). Mechanism confirmed (S018): mediated by Pulse's `BloodVolumeBaseline` gap (male default 4,802.63 mL vs female 3,996.09 mL); reducing the male BV monotonically eliminates divergence (20 / 20 → 2 / 20 → 0 / 20 across BV = 4,802.63 → 4,400 → 4,082.24 mL)." | Should-fix (S4 #2): same regime qualifier + BV-mechanism update from manuscript commits 2abfb58 + 1f3d034 | None |
| 7 | A | `README.md:122-123` (F-004 headline result) | content | "**Operator fix:** set inspiration trigger pressure to −2 cmH2O (collapses worst-case Vt CV from 0.351 → 0.016, lock-below-0.05 fraction = 78.1 %)." | "**Operator fix:** set inspiration trigger pressure to −2 cmH2O (collapses *median* Vt CV from 0.351 → 0.016; worst-case from 1.826 → 0.112; lock-below-0.05 fraction = 78.1 %)." | Should-fix (S5): the 0.351 → 0.016 collapse is the median per S014 summary.json; worst-case is 1.826 → 0.112 | None |
| 8 | A | `README.md:247` (Repository layout, experiments_log entry) | content | "│   └── santino/                 S001 … S006 entries (one .md each)" | "│   └── santino/                 S001 … S025 entries (one .md each)" | Should-fix (S6 #1): stale boundary; same as §1.4 audit we ran in manuscript commit c456118 | None |
| 9 | A | `README.md:280-292` (Quick map section) | content | Listed only S001-S006 with one-line descriptions. | Extended with one-line entries for S007 / S008 / S009 / S010 / S012 / S013 / S014 / S017 / S018 / S021 / S022 / S023 / S024 / S025 (skip in-progress / draft S019 + admin S011 / S015 / S016 / S020 in the compact map); add a "Full audit trail: see `experiments_log/INDEX.md`" pointer. | Should-fix (S6 #2): same stale boundary | None — additive |
| 10 | A | `README.md:238-247` (Repository layout, data and results entries) | content | Missing `data/runs/s014_trigger_lockout/`, `data/runs/s018_blood_volume/`, `data/runs/s021_hyperoxia_convergence/`, `data/runs/full_sweep_repro/`, `results/s022/`, `results/s023/`. | Add one-line entries for each of the six missing subdirs. | Should-fix (S7) | None — additive |
| 11 | A | `README.md:174-175` (Reproducing the atlas — prerequisites) | content | "You need: Docker, [uv](https://github.com/astral-sh/uv), a machine with ≥ 8 GB RAM and ≥ 3 CPU cores, and ~ 7 hours of compute." | Append: "To also reproduce the supplementary S023 SHAP cross-check, install Python deps with `uv sync --extra ml` (adds scikit-learn + shap to the env)." | Should-fix (S8): ml extras not currently mentioned; external user runs `uv sync` and then gets `ModuleNotFoundError: sklearn` on `shap_vs_morris_topk.py` | None — additive |
| 12 | A | `README.md:188-189` (Reproducing the atlas — after the four steps) | content | (no Pinned image hashes section after the four-step `docker build` + `uv run` block) | Add a short "Pinned image hashes (for byte-level reproducibility)" subsection citing the two manuscript §2.8 hashes (initial atlas + post-S014 patch `b2e0e807803d`), explaining a fresh build won't match byte-for-byte but Pulse's bit-exact determinism (S007) means outputs match to 1e-6 relative across image rebuilds with the same `kitware/pulse:4.3.1` base. | Should-fix (S9): manuscript §2.8 names pinned hashes; README must surface them for an external reproducer | None — additive |
| 13 | A | `README.md:196-205` (pilot smoke-test block) | content | Just describes the pilot. | Append a "Verify everything is wired up" subsection with: `uv run pytest tests/ -v` (S009/S015 detector/aggregator/sampler/scenario tests), `uv run python scripts/audit_claims.py` (S024, must report 190/190 PASS). | Should-fix (S10): no canary command for a fresh-clone external researcher; smoke test exists but is incomplete | None — additive |
| 14 | B | All `.py` files under `src/`, `scripts/`, `tests/`, `engine/` | format | 39 files differ from `ruff format` (PEP 8 spacing + long-line wrapping). | Single `uv run ruff format src/ scripts/ tests/ engine/` invocation. Diff: spacing only (blank lines per E302) + long-line argument wrapping. Zero behavioral changes. | Should-fix (S1): format not gated by pre-commit; ensures CI parity for external contributors | None — purely cosmetic |
| 15 | B | `src/detector.py:1-13` (module docstring) | docs | Module docstring describes the four flags and threshold provenance ("preregistration.md §Flags"). No manuscript / lab-notebook cross-reference. | Append paragraph: "For threshold provenance + clinical-anchor rationale, see manuscript §2.6 (HARD_BOUNDS / DRIFT_MAX_DELTA_60S tables). For mechanism interpretation of `not_steady_state` sub-modes (F-004 dyssynchrony, NSS sub-mode decomposition, F-003 transient hyperoxia regime) see manuscript §3.8 + Appendix C and lab notebooks S013 (lexical lockdown) / S014 (F-004 causal) / S021 (F-003 transient) / S022 (NSS attribution)." | Should-fix (S2): LEAN docstring philosophy — code points reader to manuscript, doesn't duplicate it | None — additive |
| 16 | B | `scripts/diagnostic_waveform_inspect.py:11` (docstring) | docs | "Aliasing check: nominal breath period (60/RR seconds) vs sample interval (5 s)" | "Samples-per-breath diagnostic: nominal breath period (60/RR seconds) vs CSV sample interval (5 s) — informational, NOT an aliasing claim. S022 retracted the aliasing inference; the diagnostic survives as a per-breath sampling-coverage metric. Mechanism is F-004 patient-ventilator dyssynchrony (S014)." | Should-fix (S3): post-S022 retraction — old "Aliasing check" wording is doc drift | None — wording only |
| 17 | C | `.gitattributes` (new file) | config | (file did not exist) | Standard line-ending normalization: `* text=auto eol=lf` + per-extension rules for `.py`/`.md`/`.toml`/`.csv` (LF) and `.parquet`/`.png`/`.pdf` (binary). | Should-fix (S13): every Python commit this session has emitted "LF will be replaced by CRLF" warnings; this normalizes to LF for portability | None — first-time file |
| 18 | C | `README.md:296-302` (Citation section) | content | Freeform-text citation paragraph only. | Add BibTeX `@misc{nanini2026pulseatlas, ...}` block alongside the freeform text. DOI / URL fields use the GitHub URL until arXiv DOI lands. | Should-fix (S14): reviewers and reference managers need BibTeX; freeform text requires manual reformat | None — additive |
| 19 | C | `CITATION.cff` (new file) | release | (file did not exist) | Standard `cff-version: 1.2.0` citation file with title / authors / repo URL / license / type=software. DOI fields blank with comment "filled after arXiv acceptance". | Nice-to-have (N1): standard for research repos; GitHub auto-renders a "Cite this repository" button | None — first-time file |
| 20 | D | `preprint/manuscript.md:2721` (§8 References, entry 1 Pulse engine) | content | "Source verified from the locally-cloned engine repository (`C:/Users/santi/projets/Pulse_engine_adults_Gitlab/engine/`, 2026-04-07; GitLab re-audit 2026-05-07, S016)." | "Source verified against the upstream Kitware Pulse GitLab repository at <https://gitlab.kitware.com/physiology/engine> (locally cloned for read-only audit; 2026-04-07; GitLab re-audit 2026-05-07, S016)." | Should-fix (S11): published preprint should not expose maintainer's developer-local path | None — URL is more authoritative than local path |
| 21 | D | `preprint/audit_phase1_findings.md:210,299` | content | Two lines that reference the same dev-local Pulse clone path. | Replace path string with the GitLab URL + a date stamp; preserves the audit semantics ("source verified against the Pulse clone on date X"). | Should-fix (S12): same as S11 but in the pre-submission audit doc | None |

**Deferred to post-arXiv or post-release (not in scope of S025):**

* N2 (README lock-below-0.05 phrasing): soft prose tweak, semantic match
  with manuscript already; defer to a later README polish if needed.
* N3 (validate_detector script needs a "developer-only" disclaimer in
  docstring): partially addressed by row 1's env-var pattern; full
  disclaimer paragraph deferred.
* N4 (README L260 link to Paper 1 repo points to user page instead of
  repo): defer until Paper 1 repo is public.
* N5 (Pulse v4.3.2 release-state note in README footer): defer; not
  release-blocking and may change again before arXiv.
* N6 (engine wrapper enforces image-hash check): defer; deterministic
  output match (S007) already verified.
* N7 (`.pre-commit-config.yaml` for external contributors): defer; the
  current hook is functional for the maintainer.

## What we tried (incl. dead ends)

* **Considered** moving `scripts/validate_detector_on_existing_runs.py`
  to a `scripts/dev/` subdirectory instead of refactoring its hardcoded
  path. Rejected because (a) that script *is* useful to external
  researchers who happen to have downstream Pulse run collections in a
  different location, (b) env-var override is the standard
  cross-platform pattern, and (c) moving the file would break the
  README repository layout doc (a row 10 edit we'd then need to revert).
* **Considered** also adding a `.pre-commit-config.yaml` so external
  contributors can `pre-commit install`. Rejected for this S025: the
  current ad-hoc hook works and adding the framework dependency is
  scope creep for the maintainer's workflow. Filed as N7 / future work.
* **Considered** doing the README S6 #2 (Quick map) edit as a full
  rewrite of the section. Rejected — kept as additive (preserved the
  existing S001–S006 entries verbatim, added S007 onward in the same
  one-line format) so a `git diff` reviewer can see at a glance "no
  earlier content changed."

## Results

See the *Changes Applied* table above for the full byte-level inventory.
Aggregate counts after all four commits land:

* 3 release-blocking findings resolved (B1 / B2 / B3).
* 14 should-fix findings resolved (S1 / S2 / S3 / S4 / S5 / S6 / S7 /
  S8 / S9 / S10 / S11 / S12 / S13 / S14).
* 1 nice-to-have resolved (N1 — CITATION.cff). The other six N-tier
  findings are explicitly deferred above with rationale.
* 0 introduced regressions (all four verification gates pass — see
  Phase 2 method above).

## Interpretation

The codebase is now **release-ready for the OSS external-researcher
audience**. The only remaining manuscript / repo-mechanics items are:

1. arXiv submission itself (adds DOI; mechanically backfills the
   CITATION.cff and the README citation block).
2. Zenodo deposit of the raw per-run artifacts (~ 65 MB S018 + the
   1,280-run sweep raw CSVs).
3. Manuscript Phase 3 prose polish (independent of the code-hygiene
   axis covered here).

### Limitations

1. This audit verifies the *code surface and READMe* that external
   researchers will encounter on clone. It does not verify the
   *experimental pipeline* (S007 / S015 / S024 cover that).
2. The N-tier deferred findings are explicitly out of scope (see
   "Deferred" subsection above); they are tracked here for a future
   release-polish pass but are not blocking arXiv submission.
3. The CITATION.cff DOI fields remain blank until arXiv acceptance;
   this is acknowledged in the file with an inline comment.

## Next steps

1. **arXiv upload.** Once accepted, backfill the DOI into
   CITATION.cff and the README BibTeX block, single commit.
2. **Zenodo deposit.** Upload the gitignored raw artifacts (S018
   `runs/` subtree, full-sweep raw CSVs) with the same Apache-2.0
   licence; cross-reference from README §5 Data availability and
   from the manuscript §Data availability section.
3. **Question closed for this hygiene axis.** No further code-hygiene
   audit needed pre-arXiv. Post-arXiv, the deferred N-tier findings
   (N2–N7) can be picked up in a single follow-up release-polish
   pass if the repository attracts external contributors.

---

## Post-S025 final polish (Commits E + F + G, 2026-05-22)

After the four S025 commits landed (A `a0675ed`, B `d9ec277`,
C `69b7e34`, D `09776ed`), three remaining pre-submission gaps were
identified by the maintainer and authorized for immediate fix as a
three-commit polish on top of the S025 baseline:

* **Commit E (`0926219`).** Add the missing top-level §5 Conclusion
  section (~250 words), surface the S024 programmatic
  claims-ledger audit as a third reproducibility layer in §2.8,
  extend the §1.4 nomenclature table and Appendix A to S024, and
  cascade-renumber the four back-matter sections (§5 Data avail
  → §6, §6 Acks → §7, §7 AI tools → §8, §8 References → §9,
  §8.7 Verified primary refs → §9.7). The new Conclusion paragraph
  on the sex axis was deliberately phrased in its *regime-specific*
  form (5 / 24 BH-FDR gas-exchange survivors + male-input-extreme
  BV divergence cluster) to avoid reintroducing the global
  "fundamental sex axis" framing the manuscript retracted in the
  2026-05-22 iterative-debt audit (commits 2abfb58 / cc4bcae).

* **Commit F (`22dee01`).** LaTeX math notation cleanup for all
  embedded formulas the maintainer flagged as typographically
  inconsistent in the PDF render: three occurrences of the
  alveolar-ventilation identity ($\dot{V}_A = \mathrm{RR} \cdot
  (V_T - V_D)$, in §3.2 / §3.3.1 / §3.8), the alveolar-gas
  equation in the §3.8 S021 plateau-undershoot discussion
  ($P_AO_2 = \mathrm{FiO}_2 \cdot \ldots$), and two stray
  `V_t delivered` mentions in the §4.4 / §4.5 Cornish-cross-tab
  paragraphs (typography-only — aligns with the manuscript's
  standard plain-text "Vt" convention). First V̇A occurrence
  carries a prose glose for cross-disciplinary readers (West
  Ch. 2 convention naming V̇A, RR, $V_T$, $V_D$).

* **Commit G (this entry's postscript).** Documents Commits E + F
  in the byte-level Changes Applied format below.

### Changes Applied — Phase 3 polish

| # | Commit | File:line | Category | Before | After | Rationale | Risk |
|---|---|---|---|---|---|---|---|
| 22 | E | `preprint/manuscript.md:86` (Reader's roadmap) | content | `system ([S001](#s001) – [S023](#s023)) used throughout.` | `system ([S001](#s001) – [S024](#s024)) used throughout.` | Boundary update; same pattern as commit c456118 (S020 → S023) | None |
| 23 | E | `preprint/manuscript.md:205` (§1 Intro umbrella) | content | `([S001](#s001) – [S023](#s023)) used throughout.*` | `([S001](#s001) – [S024](#s024)) used throughout.*` | Same boundary | None |
| 24 | E | `preprint/manuscript.md:374` (§1.4 heading) | content | `### 1.4 Experiment log nomenclature ([S001](#s001) – [S023](#s023))` | `### 1.4 Experiment log nomenclature ([S001](#s001) – [S024](#s024))` | Same boundary | None |
| 25 | E | `preprint/manuscript.md:376` (§1.4 lead-in) | content | `*A one-line description of each of the 23 experiment-log entries` | `*A one-line description of each of the 24 experiment-log entries` | Count update to match new boundary | None |
| 26 | E | `preprint/manuscript.md:383` (§1.4 ellipsis text) | content | `form **[S001](#s001), [S002](#s002), …, [S023](#s023)**.` | `form **[S001](#s001), [S002](#s002), …, [S024](#s024)**.` | Same boundary | None |
| 27 | E | `preprint/manuscript.md:~415` (§1.4 table, new row) | content | (table ended at S023 row) | New row: `S024 \| Pre-submission claims-ledger audit — scripts/audit_claims.py re-derives every Tier-1/Tier-2 quantitative claim ... (190 / 190 PASS at the locked tolerance band).` | Surfaces S024 as a referenceable experiment in §1.4 | None — additive |
| 28 | E | `preprint/manuscript.md:~2990` (Appendix A, new row) | content | (Appendix A ended at S023 row) | New row: `[]{#s024} S024 \| Pre-submission claims-ledger audit (programmatic verification of all Tier-1 / Tier-2 quantitative claims; 190 / 190 PASS, see §2.8)` | Anchor exists for `[S024](#s024)` references | None — additive |
| 29 | E | `preprint/manuscript.md:~895` (§2.8) | content | (no S024 paragraph after Phase 4b) | New paragraph "Programmatic manuscript-numbers audit ([S024](#s024), 2026-05-22)" describing audit_claims.py (190/190 PASS, tolerance scheme, CI-ready exit code) and pointing to the S024 lab notebook | Strengthens §2.8's reproducibility argument with a third audit layer (alongside S007 / S015 / Phase 4a-b) | None — additive |
| 30 | E | `preprint/manuscript.md:~953` (Notation / stat-methods intro) | content | `are in §8.` | `are in §9.` | Single cross-reference to the renumbered References section | None |
| 31 | E | `preprint/manuscript.md` (§5/§6/§7/§8 headings + §8.7) | content | Section headings `## 5. Data availability` / `## 6. Acknowledgements` / `## 7. Transparency: use of AI tools` / `## 8. References` / `### 8.7 Verified primary references ...` | Headings shifted to `## 6.` / `## 7.` / `## 8.` / `## 9.` / `### 9.7` | Cascade caused by inserting new §5 Conclusion before the back-matter | None — no internal cross-refs broke (only L953 needed updating; verified by pre-edit grep) |
| 32 | E | `preprint/manuscript.md` (new §5 Conclusion before §6 Data availability) | content | (Conclusion absent; manuscript jumped abruptly from §4.6 to §5 Data availability) | Inserted ~250-word §5 Conclusion with 3 paragraphs: (1) headline contribution + traffic-light role, (2) F-004 + F-003 operator-actionable corrections + regime-dependent sex axis, (3) bounded-synthetic-data closing + PhD-pipeline placement | Adds a standard academic close to the article; phrasing on H3 sex axis is explicitly *regime-dependent* to avoid reintroducing the framing retracted in commits 2abfb58 / cc4bcae | None — content addition, no audited number affected |
| 33 | F | `preprint/manuscript.md:1173` (§3.2 gas-exchange bullet) | math/typo | `consistent with the alveolar-ventilation identity V̇A = RR · (Vt − V_dead).` | `consistent with the alveolar-ventilation identity $\dot{V}_A = \mathrm{RR} \cdot (V_T - V_D)$ (where $\dot{V}_A$ is alveolar minute ventilation, RR is set respiratory rate, $V_T$ is delivered tidal volume, and $V_D$ is the anatomical dead-space volume; West *Respiratory Physiology* Ch. 2 convention).` | Primary fix for the maintainer-flagged PDF render typo "V VtV_dead"; proper LaTeX math mode + prose glose for cross-disciplinary readers | None — formula is informational, not a quoted value |
| 34 | F | `preprint/manuscript.md:1319` (§3.3.1 Group-B Sobol promotion) | math/typo | `the alveolar-ventilation identity V̇A = RR · (Vt − Vd) that governs CO2 elimination.` | `the alveolar-ventilation identity $\dot{V}_A = \mathrm{RR} \cdot (V_T - V_D)$ that governs CO₂ elimination.` | Consistency with row 33; CO2 → CO₂ as inline Unicode | None |
| 35 | F | `preprint/manuscript.md:1383` (§3.8 Sobol-bolt-on-closed-by-redundancy) | math/typo | `V̇A = RR · (Vt − Vd) on PaCO2.` | `$\dot{V}_A = \mathrm{RR} \cdot (V_T - V_D)$ on PaCO2.` | Consistency with row 33 | None |
| 36 | F | `preprint/manuscript.md:2018` (§3.8 S021 plateau discussion) | math/typo | `(PAO2 = FiO2 × (P_atm − P_H2O) − PaCO2/RQ = 1.0 × (760 − 47) − 40/0.8 ≈ 663 mmHg, then PaO2 = PAO2 − A-a gradient ≈ 653 mmHg for an A-a gradient of 10 mmHg).` | Reformatted as LaTeX math: `$P_AO_2 = \mathrm{FiO}_2 \cdot (P_{\mathrm{atm}} - P_{\mathrm{H_2O}}) - P_aCO_2 / \mathrm{RQ}$ $= 1.0 \cdot (760 - 47) - 40 / 0.8 \approx 663$ mmHg, then $P_aO_2 = P_AO_2 - \text{A--a gradient} \approx 653$ mmHg for an A-a gradient of 10 mmHg). | Same typographic concern as row 33 but in the alveolar-gas equation; West Ch. 5 notation (PA / Pa as roman subscripts, \mathrm{} on multi-letter symbols) | None — values 663 / 653 / 10 unchanged |
| 37 | F | `preprint/manuscript.md:2454` (§4.4 Cornish cross-mapping) | typo | `MAP, V_t delivered, SpO2, PaO2, PaCO2) intersect Cornish's 15-quantity panel ...; V_t and SpO2 are atlas-only contributions.` | `MAP, Vt delivered, SpO2, PaO2, PaCO2) intersect Cornish's 15-quantity panel ...; Vt and SpO2 are atlas-only contributions.` | Aligns with the manuscript's plain-text Vt convention (Table 1, Table 2, Abstract); LaTeX-style V_t was accidental notation drift in two paragraphs | None |
| 38 | F | `preprint/manuscript.md:2496` (§4.5 / Cornish complementarity) | typo | `Cornish does not assess SpO2 or delivered V_t, both of` | `Cornish does not assess SpO2 or delivered Vt, both of` | Same as row 37 | None |
| 39 | G | `experiments_log/santino/S025_oss_release_hygiene.md` (this file, appended postscript section) | docs | (no "Post-S025 final polish" section) | This entire "## Post-S025 final polish (Commits E + F + G, 2026-05-22)" section, including rows 22 – 39 of the Changes Applied table | Paranoid-traceability requirement: every byte-level change has a written trail in the same format as the original S025 table | None — documentation addition |

### Final verification gates (after Commits E + F + G land)

* `uv run ruff check src/ scripts/ tests/ engine/` — PASS.
* `uv run ruff format --check src/ scripts/ tests/ engine/` — PASS.
* `uv run python scripts/audit_claims.py` — 190 / 190 PASS, 0 WARN,
  0 FAIL (unchanged; no audited number moved or shifted).
* `powershell scripts/build_paper.ps1` — clean `.tex` and `.pdf` at
  `preprint/build/manuscript.pdf`.

### Manuscript-locked state

After this commit series the manuscript is **locked for arXiv
submission**. Remaining work is mechanical:

1. arXiv upload (auto-generates the DOI).
2. Backfill DOI into `CITATION.cff` (row 19) and the README BibTeX
   block (row 18) — single commit, ~2 minutes work.
3. Zenodo deposit of the gitignored raw artifacts (S018 `runs/`
   subtree + the full-sweep per-run CSVs).
4. Update §6 Data availability to cite the Zenodo DOI — single
   commit, ~5 minutes work.

No further audit / hygiene pass is needed. The codebase, manuscript,
and release-mechanics files are at submission-ready state.
