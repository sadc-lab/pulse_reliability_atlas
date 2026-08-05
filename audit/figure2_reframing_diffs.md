# Figure 2 reframing — drafted diffs, NOT APPLIED

**Opened** 2026-08-05. **Status: DRAFT — no manuscript file modified.**

Scope: reframe the cell-level traffic light from a *reliability verdict* to a
*curation and review-priority map*, add the classification-driver decomposition,
publish both screening retentions, and remove the residual `trustworthy` /
`safe to ingest` vocabulary.

Origin: external reader's critique, relayed 2026-08-05. Prior work on the same
defect: `e271f02` (colour glosses removed), `982114c` → `1eaeff9`
(preregistration deviation declared). See
`audit/preregistration_traffic_light_deviation.md`.

---

## 0. Calibration, run before drafting

`scripts/calibrate_nss_attribution.py`, read-only, re-derives everything from
`data/runs/full_sweep/aggregated.parquet` — one level *above*
`reliability_classification.csv` and `cell_flag_summary.csv`, both of which are
outputs of the chain under audit (dossier §8.2 requirement).

**Gate: reconstructed `not_steady_state` vs stored `not_steady_state` =
1280 / 1280.** The exhaustive attribution may be built.

Threshold constants verified byte-identical between the sweep commit
`e068544` (2026-04-26) and HEAD: `HARD_BOUNDS`, `DRIFT_MAX_DELTA_60S`,
`CV_THRESHOLD` = 0.05, `FLATLINE_STD_RATIO` = 0.01, `FLATLINE_BOUND_TOL` =
0.001. The one post-sweep detector change that altered behaviour (`708efb1`,
2026-07-26) touched only the `clamped` log regex, which does not enter
`not_steady_state`; its own commit message records that replaying it over 3,348
logs flips exactly one run, the s030b probe, outside the 1,280 sweep.

Re-derived and confirmed: clean 663, hard-failure-free 1,134, clamped 0,
diverged 20, implausible 126, **`diverged ∩ implausible` = 0 (disjoint,
measured not assumed)**, `not_steady_state`-sole 471, non-clean 617, traffic
light 7 / 29 / 12, drivers 7 / 23 / 9 / 9. Vt CV > 0.05 = 303, matching the
anchored claim at `scripts/audit_claims.py:621`.

### 0.1 Two findings from the calibration

**(a) The persisted reason strings under-report drift by a factor of 44 on Vt.**

| output | flatline | CV | drift (exhaustive) | drift (first-cause) | masked |
|---|---:|---:|---:|---:|---:|
| HR | 0 | 1 | 17 | 16 | 1 |
| MAP | 0 | 0 | 2 | 2 | 0 |
| Vt | 0 | 303 | **133** | **3** | **130** |
| SpO₂ | 232 | 4 | 83 | 80 | 3 |
| PaO₂ | 0 | 28 | 85 | 69 | 16 |
| PaCO₂ | 0 | 16 | 14 | 8 | 6 |
| | | | 918 total | 762 total | **156** |

Vt CV fires first and masks Vt drift in 130 of 133 cases. A supplement panel
built from `not_steady_state_reason` would have reported that Vt essentially
never drifts. This is the decisive argument for the exhaustive reconstruction.

`skipped` = 20 per channel = exactly the 20 diverged runs, which have no CSV and
therefore no per-channel statistics. Consistent by construction.

**(b) Per-cell percentages have no safe one-decimal form.** Since
`x / 160 × 100 = 5x / 8`, every per-cell percentage terminates in **at most**
three decimals, and any value ending `.125`, `.375`, `.625` or `.875` is an
exact tie at both one and two decimals:

| cell | fraction | exact % | tie at 1 dp | tie at 2 dp |
|---|---|---:|:--:|:--:|
| S1_F, four-flag | 42 / 160 | 26.25 | yes | no |
| S1_M, four-flag | 49 / 160 | 30.625 | no | **yes** |
| S3_F, four-flag | 122 / 160 | 76.25 | yes | no |
| S2_M, four-flag | 87 / 160 | 54.375 | no | **yes** |
| S4_M, four-flag | 67 / 160 | 41.875 | no | **yes** |
| S1_F, hard-free | 137 / 160 | 85.625 | no | **yes** |
| S1_M, hard-free | 145 / 160 | 90.625 | no | **yes** |
| S4_F, hard-free | 114 / 160 | 71.25 | yes | no |
| S4_M, hard-free | 106 / 160 | 66.25 | yes | no |

Two decimals does **not** solve it — it moves the tie to a different set of
cells. **Decision taken 2026-08-05: option (b).** Per-cell values are published
as **fractions only**; percentages are used only for the two aggregates, which
are unambiguous at one decimal because the following digit is 9 in both cases:

- 663 / 1,280 = 51.796875 % → **51.8 %**
- 1,134 / 1,280 = 88.59375 % → **88.6 %**

Spread ratios are quoted from the counts, not the percentages:
144/42 = 3.42857… → **3.43×**; 160/106 = 1.50943… → **1.51×**.

### 0.2 A defect found while reading the loci

`paper.tex:311` — *"the four-flag classifier doubles as a **per-cell**
data-quality contract"*. The subject is the four-flag classifier, which is
**run-level**; its per-cell aggregate is the map, a different object. Diff D1.5.

> **Corrected 2026-08-05, before commit 2.** This finding first listed three
> loci, adding `manuscript.md:2857` and `manuscript.md:92`. Re-read in context,
> **both are correct as written**: at `:2857` the subject is *"The atlas's
> reliability map"* and at `:92` it is the atlas's deliverable, and the map
> genuinely *is* per-cell. The original finding matched the string
> `per-cell data-quality` without checking the grammatical subject. What those
> two loci actually carry is the `filter` / `reliability map` vocabulary, which
> belongs to LOT 5 (D5.6, D5.7), not to the run/cell fix. **Commit 2 therefore
> touches one locus, not three.**

---

## LOT 1 — Abstract, and the `trustworthy` / `safe to ingest` vocabulary

### D1.1 — `preprint_npj/paper.tex:118`, abstract, final sentence

Word budget: the abstract is at **147 strict / 150 whitespace tokens** against
npj's "up to 150 words", zero margin (`audit/npj_format_compliance.md` N-2).
Old sentence 18 words, new sentence 18 words — **budget-neutral on both
conventions**; no `%`, `=` or `~` introduced.

```diff
-The atlas maps where Pulse is trustworthy and ships an Apache-2.0-licensed data-quality filter for synthetic machine-learning training cohorts.
+The atlas maps operational sensitivity and review-priority regions, and releases an Apache-2.0-licensed curation layer for synthetic cohort construction.
```

*Kept deliberately:* "We present the first **reliability atlas**…" earlier in
the abstract. It names the artefact and matches the title. It is now the only
`reliability` token left in the abstract.

### D1.2 — `preprint_npj/paper.tex:138`, Introduction, two edits in one line

```diff
-Second, mapping where the adult engine is trustworthy is the prerequisite for adapting it to pediatric ARDS,
+Second, mapping the adult engine's sensitivity and failure modes is the prerequisite for adapting it to pediatric ARDS,
```

```diff
-The result is therefore not a single benchmark score but a per-cell reliability map and a reusable run classifier. Downstream users, including the machine-learning and clinical-AI pipelines that draw on synthetic patient cohorts~\cite{ward2024ventilator}, can apply it as a data-quality filter without re-running the sweep.
+The result is therefore not a single benchmark score but a per-cell curation map and a reusable run-level classifier. Downstream users, including the machine-learning and clinical-AI pipelines that draw on synthetic patient cohorts~\cite{ward2024ventilator}, can use the run-level labels to identify simulations requiring exclusion, remediation or review, and the cell-level map to prioritise scenario-specific curation, without re-running the sweep. Neither layer constitutes external physiological validation, and neither is a distribution-neutral automatic filter (\S\ref{sec:results-flags}).
```

### D1.3 — `preprint_npj/paper.tex:198`

```diff
-and the per-cell traffic-light map (Figure~\ref{fig:traffic_light}) gives the reliability picture at a glance.
+and the per-cell traffic-light map (Figure~\ref{fig:traffic_light}) gives the combined curation and review-priority picture at a glance.
```

### D1.4 — `preprint_npj/paper.tex:307`, Discussion opening

```diff
-The accompanying per-cell traffic-light reliability map (Figure~\ref{fig:traffic_light}) is the principal deliverable for downstream Pulse users: it summarises which combinations of patient reference body, ARDS severity, and steady-state output are trustworthy as-is, which require flag-stratified handling, and which warrant per-channel justification before being ingested into downstream analyses.
+The accompanying per-cell traffic-light curation map (Figure~\ref{fig:traffic_light}) is the principal deliverable for downstream Pulse users: it summarises which combinations of patient reference body, ARDS severity, and steady-state output are default-eligible under the stated criteria, which require flag-stratified handling, and which warrant per-channel justification before being ingested into downstream analyses. It is a curation and review-priority instrument, not a general physiological validation of the engine.
```

### D1.5 — `preprint_npj/paper.tex:311`, Discussion (includes the §0.2 defect)

```diff
-For machine-learning pipelines that train on Pulse-generated synthetic patient cohorts, the four-flag classifier doubles as a per-cell data-quality contract.
+For machine-learning pipelines that train on Pulse-generated synthetic patient cohorts, the four-flag classifier doubles as a run-level data-quality contract.
```

```diff
-Green cells in Figure~\ref{fig:traffic_light} are safe to ingest; yellow cells should be filtered to the clean subset with the per-cell flag rate reported in training-set metadata; red cells require per-channel and per-input justification.
+Green cells in Figure~\ref{fig:traffic_light} are eligible for default inclusion under the stated criteria, subject to use-case-specific validation; yellow cells should be filtered to the clean subset with the per-cell flag rate reported in training-set metadata; red cells require per-channel and per-input justification. Green denotes default eligibility under the implemented rule and under the non-degenerate literal hard-flag interpretation; it does not establish physiological validity.
```

### D1.6 — `preprint_npj/paper.tex:383`, Data availability

```diff
-so that downstream users can apply it directly as a data-quality filter on synthetic patient cohorts without re-running the sweep.
+so that downstream users can apply it directly as a curation and review-priority layer on synthetic patient cohorts without re-running the sweep. Neither the run-level labels nor the cell-level map is a distribution-neutral automatic filter; per-cell retention under both screens is reported in \S\ref{sec:results-flags}.
```

---

## LOT 2 — Retention paragraph

**Insertion point:** `preprint_npj/paper.tex`, §2.2, immediately after the
paragraph at `:198` (the one discussing Table 1). New paragraph, no table —
the per-cell numbers already exist in Table 1; only a `retention` column and
this paragraph are new.

> Screening retention is strongly cell-dependent, and depends on which screen is
> applied. Under the strict four-flag definition, 663 of 1{,}280 simulations
> (51.8~\%) are clean, with per-cell retention ranging from 42/160 in S1\_F to
> 144/160 in S3\_M, a 3.43-fold spread. Treating \texttt{not\_steady\_state} as
> a review-and-remediation label rather than an automatic exclusion leaves
> 1{,}134 hard-failure-free simulations (88.6~\%), with per-cell retention
> ranging from 106/160 in S4\_M to 160/160 in S2\_F and S3\_F, a 1.51-fold
> spread. The two
> screens deplete opposite ends of the severity axis: the four-flag screen is
> most restrictive on the healthy cells (S1\_F, S1\_M), the hard-failure-free
> screen on the severe-ARDS cells (S4\_M, S4\_F). Choosing a screening rule
> therefore changes which clinical regimes a downstream cohort
> under-represents. Neither subset is distribution-neutral, so downstream
> studies should report per-cell retention and cohort composition before and
> after screening. The 1{,}134-run subset must not be called clean: it still
> contains non-stationary trajectories, usable only after review, extension or
> protocol correction.

**Method note, for the Supplement or a footnote:**

> The 471 runs gained by moving from the strict-clean to the hard-failure-free
> subset are exactly those carrying \texttt{not\_steady\_state} as their sole
> flag; together with 20 \texttt{diverged} and 126 \texttt{implausible} runs
> they account for all 617 non-clean runs, which also establishes that
> \texttt{diverged} and \texttt{implausible} are disjoint in this sweep.
> \texttt{clamped} is a provided category that is empty here (0 / 1{,}280); a
> clamped run would be unfit to represent the requested input point had one
> occurred.

---

## LOT 3 — Figure 2: caption reframe + panel B

### D3.1 — Caption, opening (bold lead sentence)

```diff
-\textbf{Cell colour encodes a combined flag-and-baseline-deviation class, not the physiological value it annotates.}
+\textbf{A curation and review-priority map: cell colour encodes a combined flag-and-baseline-deviation class, not the physiological value it annotates, and not a reliability verdict.}
```

### D3.2 — Caption, replace the middle clause

```diff
-Per-cell reliability traffic-light map across the 8 (scenario $\times$ sex) cells
+Per-cell curation and review-priority map across the 8 (scenario $\times$ sex) cells
```

### D3.3 — Caption, panel B text to append

> \textbf{(b)} Classification drivers on the same 48 cells: which criterion
> placed each cell in its class. Counts are 7 \emph{neither} (all green),
> 23 \emph{hard flags only} (19 yellow, 4 red), 9 \emph{deviation only}
> (3 yellow, 6 red) and 9 \emph{both} (7 yellow, 2 red). The thresholds are
> class-relative and not symmetric: for deviation, yellow is $>10~\%$ and red
> $>30~\%$; for hard flags, yellow is any positive rate and red $>30~\%$. The
> \emph{neither} category coincides exactly with the green set by construction.
> These are classification drivers, not failure causes: deviation from a healthy
> reference is not in itself a failure. Directionally expected changes under
> ARDS do not validate their magnitude; the signed deviations are descriptive
> and do not constitute external physiological validation.

### D3.4 — Figure code

`scripts/make_paper_fig01.py` gains a second panel. Panel A unchanged (verified
in `e271f02`: it draws colours only, no legend text, so caption and figure
cannot disagree). Panel B is a 48-cell categorical matrix on the same axes.

---

## LOT 4 — Supplement: three descriptive views

New figure, three panels, all from tracked data, **no new simulations**.

1. **Hard-failure rate per cell** — `diverged` + `implausible` over 160, per
   (scenario × sex). 8 values; not duplicated per output, because these flags
   are run-level.
2. **`not_steady_state` triggers per output** — exhaustive, multi-label, the
   table of §0.1(a).
3. **Signed deviation from the (S1, M) baseline per output** — reconstructed as
   `(clean_mean − baseline_s1m) / baseline_s1m` from the deposited CSV. Diverging
   colour scale, not ordinal.

### D4.1 — Caption clause for panel 2

> Trigger attribution was reconstructed exhaustively from the stored
> per-channel statistics by re-applying the registered thresholds; the
> reconstruction reproduces the stored \texttt{not\_steady\_state} flag on
> 1{,}280 of 1{,}280 runs. A channel may satisfy more than one trigger, so
> counts are non-mutually-exclusive and their total exceeds the number of
> \texttt{not\_steady\_state} runs. The persisted
> \texttt{not\_steady\_state\_reason} records, for each failing channel, the
> first trigger reached by the implementation's ordered checks (flatline, then
> CV, then drift); reasons from different channels are then joined into a
> semicolon-separated string. It can therefore retain multiple channel-level
> entries per run, but at most one trigger per channel, and is not an
> exhaustive attribution field. On Vt the difference is large: 133 channels
> exceed the drift threshold, of which 130 are masked in the recorded reason by
> a CV trigger reached first.

---

## LOT 5 — Artefacts, monograph, cover letter, metadata, README

| # | locus | current | proposed |
|---|---|---|---|
| D5.1 | `results/reliability_traffic_light.json`, `description` | "Green = trustworthy as-is; yellow = filter to the clean subset…; red = per-channel justification required" | "Green = default-eligible under the stated composite criteria; yellow and red = increasing levels of scenario-specific review required. Colours do not constitute external physiological validation." |
| D5.2 | `scripts/export_traffic_light.py:77` | same string | same replacement (must stay identical to D5.1) |
| D5.3 | `preprint_npj/cover_letter.md:26` | "operational envelope is trustworthy" | "operational envelope is characterised" |
| D5.4 | `preprint_npj/cover_letter.md:42` | "which Pulse configurations are safe to ingest" | "which Pulse configurations are default-eligible under the stated criteria" |
| D5.5 | `preprint_npj/submission_metadata.txt:30` | "These results map where Pulse is trustworthy and provide an…" | "These results map Pulse's operational sensitivity and review-priority regions and provide an…" |
| D5.6 | `preprint/manuscript.md:92` | "provides a per-cell data-quality filter for downstream" | "provides a per-cell curation and review-priority map for downstream" — `per-cell` is **correct here** (subject is the map); only `filter` changes |
| D5.7 | `preprint/manuscript.md:2857` | "The atlas's reliability map … doubles as a **per-cell data-quality filter for synthetic…**" | "The atlas's curation map … doubles as a **per-cell curation layer for synthetic…**" — `per-cell` **correct here** too; `reliability map` and `filter` change |
| D5.8 | `preprint/manuscript.md:522, 528` | "where adult Pulse is trustworthy" | "where adult Pulse's behaviour is characterised" |
| D5.9 | `preprint/manuscript.md:2853` | "data-quality filter — green cells ingest as-is, yellow ingest…" | "curation map — green cells are default-eligible, yellow…" |
| D5.10 | `preprint/manuscript.md:2892` | "**Green cells:** safe to ingest into training cohorts without" | "**Green cells:** eligible for default inclusion, subject to use-case-specific validation, without" |
| D5.11 | `preprint/manuscript.md:3331` | "delivers an immediate, actionable data-quality filter for" | "delivers an immediate, actionable curation and review-priority layer for" |
| D5.12 | `README.md:75` | "without a map of where the engine is reliable" | "without a map of where the engine's behaviour is characterised" |
| D5.13 | `README.md:136` | "**Clinician / domain expert** wanting to know where Pulse is safe" | "…wanting to know which regimes require scenario-specific review" |

`README.md:6` ("The first open reliability atlas…"), `:105`, `:109`, `:127`,
`:156`, `:215`, `:245`, `:368` and the title all use `reliability` as the
artefact's name, consistent with D1.1's decision to keep it. **Not proposed for
change.**

---

## Decisions taken 2026-08-05

1. **Rounding — option (b).** Per-cell values as fractions; percentages only for
   the two aggregates. Resolved in §0.1(b).
2. **Cross-references.** Do not point at an approximate existing section. Create
   dedicated labels `\label{sec:results-screening-retention}` and
   `\label{tab:screening-retention}`, add both to the `.aux` cross-reference
   guard (`e95c343`), and prefer `Table~\ref{tab:screening-retention}` where the
   numbers are invoked; reserve the section reference for interpretive passages.
   The `\S\ref{sec:results-flags}` placeholders in D1.2 and D1.6 are to be
   replaced by these.
3. **Abstract — keep lowercase** "the first reliability atlas". Capitalising it
   mid-sentence would read as a product name. Scope is bounded immediately by
   the operational-sensitivity / failure-and-instability / review-priority
   wording instead.
4. **Panel B in the main figure, with a fallback.** Build Figure 2 with both
   panels, rebuild the npj PDF, and measure float displacement, legibility,
   minimum type size, continuity with the introducing text, and any near-empty
   page. Panel A must not be shrunk to the point of degrading its legibility in
   order to keep panel B. If it does not fit cleanly, the fallback is: main
   figure keeps panel A plus a compact inset carrying 7/23/9/9 and the 6/4/2
   split of the reds, and the full driver matrix moves to the Supplement.
5. **Ledger — anchors land WITH the text, not before.** `audit_claims.py:252`
   fails an anchor whose literal is absent (`count == 0 AND
   expected_occurrences >= 1`), so anchors added ahead of the prose would leave
   the ledger red. They go in commit 3. `T1.25/26/27` (7/29/12) do not move.
   New anchors required: 663, 1,134, 471, 617, 20, 126,
   `diverged ∩ implausible = 0`, the 16-cell retention table, drivers
   7/23/9/9 and their colour breakdown, the 1280/1280 boolean agreement, the
   exhaustive output × trigger matrix, Vt CV = 303, SpO₂ flatline = 232,
   Vt drift 133 exhaustive vs 3 recorded, and 156/918 masked *if that figure
   reaches the text*. **`0 clamped` is already anchored** at
   `audit_claims.py:764` (`"0 of 1,280 silent-clamping flags"`) — reuse or
   extend it, do not create a second.
   Preferred implementation: the calibration script emits a structured audit
   CSV/JSON and `audit_claims.py` verifies that output and its totals, rather
   than each value being transcribed independently into two scripts.
6. **Run/cell conflation — separate commit, first.** Treated as an independent
   factual defect even though it surfaced during this work.

## Commit order

1. ✅ **audit** — calibration script + this dossier. No new anchors. → `9586b06`
2. ✅ **`[PAPER] Distinguish run-level labels from cell-level curation`** — the
   single genuine locus of §0.2. → `7765aa4`. Ledger after: 313/313 anchors,
   94/94 crosswalk, 26/26 monograph, 25/25 head-line counters, exit 0.
3. **scientific** — split into three, because these are three different kinds of
   change and a single commit would make a regression impossible to isolate:
   - **3a — text only.** D1.1 (abstract), D1.2, D1.3, D1.4, D1.6, and the 13
     rows of LOT 5. No new number, no code. Fully checkable by the ledger.
   - **3b — retention.** The LOT 2 paragraph and table, the two new labels
     (`sec:results-screening-retention`, `tab:screening-retention`), their entry
     in the `.aux` cross-reference guard (`e95c343`), and the new anchors. This
     is where every new number enters, so anchors land here with their prose.
     **Run a targeted LaTeX compile before committing** — not to ship a PDF, but
     to prove the two labels actually reach `.aux` and that the guard resolves
     them, with zero unresolved references. No restore step is needed
     afterwards: `preprint_npj/build/` is gitignored (`.gitignore:68`), so the
     compile leaves no tracked change and 3b is source-only by construction.
     Watch the known trap: if the PDF is open in a viewer the build fails
     silently and bibtex reports "0 entries", so confirm the compile actually
     ran rather than trusting the exit code.
   - **3c — figures.** Figure 2 panel B (LOT 3) and the Supplement's
     three-panel view (LOT 4). Code, then a real render measurement, then the
     §4 fallback if the page does not hold.
4. regeneration of artefacts + render checks. **`build/paper.pdf` is knowingly
   one word stale from commit 2 onwards**; a single rebuild at the end of 3c
   covers commits 2, 3a, 3b and 3c.
5. cumulative review before any push.

## Out-of-band changes, recorded here because git cannot see them

`preprint_npj/pre_submission_inquiry.txt` is covered by `.gitignore:127`. Two
edits were applied to it on 2026-08-05 as part of 3a-bis and will never appear
in any commit:

- `:46` "yields a per-cell traffic-light **data-quality filter** for synthetic
  cohorts" → "yields a per-cell traffic-light **curation and review-priority
  map** for synthetic cohorts";
- the same sentence reflowed, no further change of sense.

If that file is ever regenerated from a template, both edits are lost.



`.claude/settings.json` is covered by `.gitignore:48`, so the following leaves
no trace in the history. On **2026-08-05**, with the maintainer's explicit
authorisation, `"Bash(git push)"` and `"Bash(git push origin main)"` were
removed from the `allow` list. `"Bash(git push --dry-run origin main)"` is
kept, and the `deny` on `git push --force` / `-f` is untouched.

Effect: `git push` now prompts, because on this installation the `ask` key is
inoperative and "prompt" is obtained by absence from `allow`. This makes the
guarantee mechanical rather than merely a policy in `CLAUDE.md` (async protocol,
rule 5), and it makes the file's own comment at `:19` — which already listed
`git push` among what is deliberately not in `allow` — true for the first time.
`git add`, `commit`, `checkout`, `stash` and `mv` are unchanged, so no friction
is added to the intermediate steps.
