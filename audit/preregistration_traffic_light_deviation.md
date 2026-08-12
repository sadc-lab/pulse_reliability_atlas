# Preregistration ↔ implementation: the traffic-light classification rule

**Opened** 2026-08-04. **Status: CLOSED — recommendation adopted the same day in
`1eaeff9` (2026-08-04 16:11 -0400), pushed to `origin/main`.** Closure header
added 2026-08-12; the body below is the investigation as written on 2026-08-04,
unedited apart from one dated adoption pointer appended under the §7 heading.
§7's "for decision, not applied" framing was true when it was written and is
kept, not rewritten.

Scope: `preregistration.md` §Analysis plan item 7 versus
`src/analysis_compare.py::reliability_classification`, and the published
7 / 29 / 12 traffic-light distribution that follows from the latter.

This dossier establishes facts and quantifies consequences. It changed no
classifier and no number; the declaration it recommended was then written into
the manuscript, the supplement and the preregistration (§7 below, and the
adoption table here).

## Adoption — what §7 asked for, and what shipped

| §7 asked for | shipped | locus |
|---|---|---|
| deviation statement in Methods §4.5 naming D1 and D2, quoting the preregistered sentence, giving 7 / 3 / 38 | ✅ | `preprint_npj/paper.tex:390` (rendered §4.5, p. 27), plus the retention rationale at `:392` |
| sensitivity matrix in the Supplement | ✅ | `preprint_npj/supplement.tex:337-358` → §S3.11, Table **S6** (p. 43); the three readings are rebuilt from the eight run-level `aggregated.parquet`, not from the derived table |
| §4.5's 26-cell transition table in the Supplement | ⚠️ **partial, deliberate** | the per-cell table stayed **here** (§4.5 of this register); `supplement.tex:358` cites it rather than reproducing it |
| append-only entry in `preregistration.md`, dated 2026-08-04, not backdated | ✅ | `preregistration.md:222-289`, filed separately from the two 2026-04-22 amendments and saying so |
| no change to the classifier, the figure, or the 7 / 29 / 12 counts | ✅ | `results/reliability_classification.csv` still counts 7 / 29 / 12 over its 48 rows (re-counted 2026-08-12) |

A sixth item was added later, on 2026-08-12: the Discussion calls the map "the
principal deliverable" (`paper.tex:339`) twelve pages before §4.5 declares the
deviation. A forward reference to §4.5 was added at that locus so the deviation
cannot read as buried.

> **Why this header exists.** Until 2026-08-12 the two lines above said
> `Status: OPEN — nothing modified`, eight days after the recommendation had
> been adopted in full. That is the second time in this repository that a stale
> declared status caused a false report — the first was
> `audit/figure2_reframing_diffs.md`, whose "DRAFT — NOT APPLIED" header
> produced a wrong hand-off on 2026-08-10. **A status field is not a
> measurement.** Nothing in `scripts/audit_claims.py` checks a register header
> against the repository, so these headers are re-read by hand or not at all.

---

## 1. The two rules, quoted exactly

### 1.1 Preregistered

`preregistration.md:193`, the seventh and last entry of `## Analysis plan`
(the section begins at `:185`; `## Stop rules` follows at `:195`):

> 7. **Reliability classification.** Per output per input cell: green (<10%
>    deviation from cell baseline), yellow (10–30%), red (>30% or any flag
>    raised).

### 1.2 Implemented

`src/analysis_compare.py:240-244`, the branch that assigns every cell colour:

```python
pct_off = abs(mean_clean - baseline) / abs(baseline)
hard_failure_rate = (n_diverged + n_implausible) / max(n_total, 1)
if hard_failure_rate > 0.3 or pct_off > 0.3:
    light = "red"
elif pct_off > 0.1 or hard_failure_rate > 0.0:
    light = "yellow"
else:
    light = "green"
```

### 1.3 The three differences

| # | Preregistered | Implemented | Materiality |
|---|---|---|---|
| **D1** | red on **any flag raised**; the rule carries **no flag term in yellow at all** | **two indissociable changes**: red only when the hard-flag **rate exceeds 30 %**, *and* yellow whenever that rate is strictly positive (`hard_failure_rate > 0.0`) | **Material deviation.** This is the whole of the 12 → 38 change. |
| **D2** | "any **flag**" — the atlas has four (`clamped`, `diverged`, `implausible`, `not_steady_state`) | only two enter the rule: `diverged` + `implausible` | **Operational clarification.** The four-flag reading is degenerate (48 / 48 red, §4.3); the hard-flag reading is usable and gives 7 / 3 / 38 (§4.2). The preregistered text is therefore **ambiguous, not globally unusable**. Defensible, but it must be declared. |
| **D3** | deviation from "**cell** baseline" | deviation from a single **(S1, M)** baseline for every cell | **Ambiguity of reading; no deviation established.** See §1.4. |

**Why D1's two components must be declared together.** Taken alone, "red now
needs a 30 % rate" would predict that cells leaving red land wherever their
deviation puts them, including green. They do not, because the second component
sends every cell with a non-zero hard-flag rate to yellow. That is the
mechanism behind the invariance of the green set (§4.4), and the invariance is
the strongest evidence that the change did not manufacture a favourable
result. Reporting the first component without the second would make that
invariance look like a coincidence.

### 1.4 D3: two defensible readings, and the repository does not settle it

- **Reading A** — "cell baseline" means *a baseline proper to each cell*. Under
  this reading the implementation deviates. Note that a literal per-cell
  baseline makes every deviation zero by construction, so Reading A is
  degenerate as an analysis even though it is a grammatical reading of the
  sentence.
- **Reading B** — "cell baseline" means *the baseline cell*, i.e. (S1, M).
  Under this reading the implementation **conforms**. This is not a
  reconstruction after the fact: the function's own docstring, contemporaneous
  with the code, uses the phrase in exactly that sense — "Cell baseline is the
  mean of clean S1_M runs".

Nothing in the repository establishes which reading the preregistered sentence
intended. D3 is therefore recorded as a **terminological ambiguity, not a third
material deviation**.

**Supplement §S3.9 must not be cited in support of D3.** That check re-scores
the 24 female cells against a sex-specific **(S1, F)** baseline and finds 0 of
24 colour changes. It varies the *sex* of the baseline while holding the
scenario at S1. It never scores an S4 cell against an S4 baseline — and it is
precisely that healthy-versus-scenario axis which produces the six
deviation-only reds of §4.1. Invoking §S3.9 for D3 would be an overclaim a
reader can falsify in one minute.

---

## 2. Chronology

All dates from `git log`, timezone as recorded in the commits (-0400).

| Fact | Commit | Timestamp | Evidence |
|---|---|---|---|
| Preregistered rule text enters the repository | `19945f6` "first commit" | **2026-04-22 18:05:08** | `git log -S "any flag raised" -- preregistration.md` returns this commit and **no other** — the sentence has never been edited since. |
| `hard_failure_rate` enters the repository | `e068544` "Pulse Reliability Atlas — full 1,280-run Morris sweep, analysis, and methods-paper draft" | **2026-04-26 13:20:06** | `git log -S "hard_failure_rate" -- src/analysis_compare.py` returns this commit and no earlier one. |
| The sweep's tracked data arrives | `e068544` — **the same commit** | 2026-04-26 13:20:06 | `git log --diff-filter=A -- data/runs/full_sweep` returns exactly one commit; 10 tracked files (the eight per-cell `aggregated.parquet` plus two). |

**Gap: 3 days 19 h 15 min.** The implemented rule is unambiguously *posterior*
to the preregistered text.

### 2.1 What the chronology cannot settle

Git records when code was **committed**, not when it was **written**, and here
the rule and the data landed in one commit. It is therefore not established
whether the rule was authored before or after the sweep output was inspected.
This dossier does not assert either. It is the single most consequential open
question and no artefact in the repository answers it.

### 2.2 The amendments log does not cover it

`preregistration.md` carries an append-only `## Amendments` section (`:214`)
and, separately, an `ERRATUM` note (`:9`, dated 2026-05-19, self-described as
"terminology only, no design change") and a "Documentation amendment"
(`:136`, 2026-05-21).

The amendments log has **exactly two entries**, both dated **2026-04-22** —
i.e. both *before* the implemented rule existed — and both explicitly note that
no data had been collected:

1. `2026-04-22` — rescope from hackathon to methods paper.
2. `2026-04-22-b` — detector calibration (flatline tolerance 1 % → 0.1 %).

Neither concerns the traffic light. The file ends at line 218; there is no
third entry. **No amendment, erratum or documentation note anywhere in the
repository records the classification-rule change.**

---

## 3. Ground-truth inputs to the recomputation

From `results/cell_flag_summary.csv` (n = 160 per cell):

| cell | diverged | implausible | **hard** | hard-rate | not_steady_state |
|---|---:|---:|---:|---:|---:|
| S1_F | 0 | 23 | 23 | 14.38 % | 118 |
| S1_M | 4 | 11 | 15 | 9.38 % | 107 |
| S2_F | 0 | 0 | **0** | 0 % | 68 |
| S2_M | 4 | 0 | 4 | 2.50 % | 69 |
| S3_F | 0 | 0 | **0** | 0 % | 38 |
| S3_M | 4 | 0 | 4 | 2.50 % | 12 |
| S4_F | 0 | 46 | 46 | 28.75 % | 74 |
| S4_M | 8 | 46 | **54** | **33.75 %** | 44 |

Two facts do all the work:

- **Only S4_M exceeds the 30 % hard-flag rate** (54 / 160 = 33.75 %).
- **Only S2_F and S3_F have zero hard flags.** The other six cells each have
  at least one.
- **Every cell has `not_steady_state` runs** (minimum 12, in S3_M). No cell is
  free of all four flags.

Deviations from the (S1, M) baseline are read from
`results/reliability_classification.csv`, column `pct_off_baseline`.

---

## 4. The three classification matrices

### 4.1 Implemented rule — the published state

**7 green / 29 yellow / 12 red** of 48.

Cross-checked two ways: by counting the `light` column of
`results/reliability_classification.csv`, and against the figure caption in
`paper.tex:226` ("7 green / 29 yellow / 12 red"). They agree.

The 12 red decompose by *which* criterion fired:

| trigger | count | cells |
|---|---:|---|
| deviation > 30 % only (hard-rate below threshold) | 6 | S3_F HR (+101.3 %), S3_M HR (+107.5 %), S4_F HR (+94.1 %), S3_F PaO₂ (−39.0 %), S3_M PaO₂ (−43.6 %), S4_F PaO₂ (−56.6 %) |
| hard-rate > 30 % only (deviation small) | 4 | S4_M MAP (15.4 %), S4_M Vt (17.0 %), S4_M SpO₂ (7.1 %), **S4_M PaCO₂ (0.22 %)** |
| both | 2 | S4_M HR (+92.6 %), S4_M PaO₂ (−59.9 %) |

### 4.2 Literal preregistered rule, hard-flag reading of "any flag"

Red if deviation > 30 % **or** the cell contains ≥ 1 `diverged`/`implausible`
run; green if deviation < 10 % and not red; yellow otherwise.

**7 green / 3 yellow / 38 red** of 48.

Derivation: six cells carry ≥ 1 hard flag → 36 red. Of the remaining 12
combinations (S2_F and S3_F), two exceed 30 % deviation — S3_F HR (101.3 %) and
S3_F PaO₂ (39.0 %) → 38 red. Of the last 10, seven are below 10 % → 7 green;
three sit in 10–30 % → 3 yellow (S2_F HR 15.1 %, S2_F PaO₂ 17.5 %, S3_F MAP
13.3 %).

### 4.3 Literal preregistered rule, four-flag reading of "any flag"

**0 green / 0 yellow / 48 red.**

Every cell contains `not_steady_state` runs, so every cell is red. The rule is
degenerate under this reading and carries no information. It is reported here
because it demonstrates that the word "flag" in the preregistered sentence is
**ambiguous**, not because it is a defensible analysis.

### 4.4 The green set is identical under both non-degenerate rules

The same seven combinations are green under §4.1 and §4.2: **S2_F** MAP, Vt,
SpO₂, PaCO₂ and **S3_F** Vt, SpO₂, PaCO₂.

This is not a coincidence. Green requires ≤ 10 % deviation under either rule,
and additionally zero hard flags under the implementation; S2_F and S3_F are
the only cells with zero hard flags, so the flag term is inert on exactly the
cells that could be green. **The implemented rule's leniency never manufactures
a green cell.** It moves cells between yellow and red only.

### 4.5 The 26 combinations that move yellow → red

All 12 red cells of §4.1 remain red in §4.2, so red grows by exactly 26 and
yellow shrinks by exactly 26. The 26 are every yellow combination that sits in
a cell carrying at least one hard flag:

| cell | outputs moved | n |
|---|---|---:|
| S1_F | HR, MAP, Vt, SpO₂, PaO₂, PaCO₂ | 6 |
| S1_M | HR, MAP, Vt, SpO₂, PaO₂, PaCO₂ | 6 |
| S2_M | HR, MAP, Vt, SpO₂, PaO₂, PaCO₂ | 6 |
| S3_M | MAP, Vt, SpO₂, PaCO₂ | 4 |
| S4_F | MAP, Vt, SpO₂, PaCO₂ | 4 |
| | **total** | **26** |

The three that stay yellow are the three in flag-free cells: S2_F HR, S2_F
PaO₂, S3_F MAP.

Note what the move implies. **S1_M — the healthy male reference body, the
baseline cell itself — becomes red on all six outputs** under the literal rule,
at zero deviation by construction, on the strength of 15 hard-flagged runs out
of 160. That outcome is a fair statement of why the rule was tightened; it is
not a fair statement of the engine's behaviour.

---

## 5. Effect on published claims

### 5.1 Loci that quote the distribution

| document | locus | text |
|---|---|---|
| paper | `paper.tex:226` (Fig. 2 caption) | "7 green / 29 yellow / 12 red, i.e. 7/48 (15 %), 29/48 (60 %), and 12/48 (25 %)" |
| monograph | `manuscript.md:119-120` | "**7 green / 29 yellow / 12 red** of the 48 cell × output combinations" |
| monograph | `manuscript.md:2379` | "7 green, 29 yellow, 12 red out of 48 cells" |
| monograph | `manuscript.md:2409` | "**7 green, 29 yellow, 12 red** out of 48 cells" |
| monograph | `manuscript.md:2431` | "**Key takeaway:** 7 green, 29 yellow, 12 red out of 48 cells" |
| supplement | — | does not quote the distribution |
| README | — | does not quote the distribution; §"traffic-light grid" refers to the figure only |

Six loci, all in the paper caption and the monograph.

### 5.2 The ledger cannot detect this class of defect

The counts are anchored — `T1.25` (7 green), `T1.26` (29 yellow), `T1.27`
(12 red) in `scripts/audit_claims.py`. Each compares the manuscript literal
against a `computed_value` derived from `results/reliability_classification.csv`,
i.e. **from the artefact the implemented rule produced**.

The ledger therefore verifies that the paper faithfully reports what the code
computed. It cannot, and does not, verify that the code implements the
protocol. This dossier's finding sits in exactly that blind spot, and the same
blind spot covers every other anchored claim whose `computed_value` is read
from a derived artefact rather than re-derived from the protocol.

### 5.3 What does *not* change

- **H1, H2, H3, H4 are untouched.** None depends on the traffic light. H2 is a
  clamping rate (0 / 1,280), H3 an existence claim, H4 the divergence
  asymmetry plus the Wasserstein family.
- **The four flags and their per-cell counts are untouched.** Table 1 is the
  primary flag report and it is rule-independent.
- **The 10 % / 30 % deviation bands really were preregistered.** The Fig. 2
  caption claims exactly that and nothing more, so the caption as it stands
  today is *incomplete*, not false. The word "preregistered" was deliberately
  not extended to the combination rule when the caption was revised on
  2026-08-04 (commit `e271f02`).
- **The traffic-light figure and the classifier code are unchanged by this
  dossier.**

---

## 6. Classification of the finding

Against the three hypotheses set at the opening of this dossier:

| hypothesis | verdict |
|---|---|
| Drafting error in the preregistration, demonstrated by an earlier implementation | **Refused.** The implementation is 3 d 19 h posterior and no earlier variant exists in the history. |
| Clarification of an ambiguous protocol sentence | **Partly supported, insufficient alone.** The word "flag" *is* genuinely ambiguous (§4.3), and disambiguating it to the two hard flags is defensible. But D1 — moving "any flag" from the red criterion to the yellow criterion and gating red behind a 30 % rate — is not a reading of the preregistered sentence. It is a different rule. |
| **Material, undocumented deviation** | **Supported for D1, and this is the dominant reading of the finding as a whole.** The rule changed, after the lock, without an amendment, and the change moves 26 of 48 combinations. |

The honest formulation is therefore: **one material deviation (D1, itself made
of two indissociable changes), bundled with one defensible operational
clarification (D2), and one terminological ambiguity that is not an established
deviation at all (D3). Neither D1 nor D2 is recorded anywhere.**

Stated as a scope sentence for the eventual declaration: *the change did not
affect which cells are identified as green, but it substantially altered the
yellow–red boundary.*

---

## 7. Recommendation — for decision, not applied

> **Appended 2026-08-12: this recommendation was ADOPTED on 2026-08-04 in
> `1eaeff9`, hours after this section was written.** The heading and the text
> below are the state at drafting time and are deliberately not rewritten; see
> the adoption table in the closure header for what shipped and where, including
> the one item (the 26-cell transition table) that stayed in this register
> rather than moving to the Supplement.

**Keep the implemented rule as the primary analysis, declare the deviation
explicitly, and report the literal rule as a sensitivity analysis.**

Reasons, in order of weight:

1. **Reverting is not neutral.** The literal rule turns the healthy male
   reference cell red on all six outputs at zero deviation (§4.5). A map whose
   baseline cell is red does not communicate reliability; it communicates the
   rule's own coarseness.
2. **The deviation is one-directional and its direction is disclosable.** The
   implemented rule is *more lenient* on red. Saying so plainly, with the
   7 / 3 / 38 sensitivity beside it, gives a reader everything they need to
   apply the stricter rule themselves.
3. **Nothing else in the paper moves.** §5.3.
4. **The green set is invariant** (§4.4), so the "which cells are safe as-is"
   reading — the map's main use for downstream users — is identical under both
   rules. That is the strongest single argument that the deviation did not
   manufacture a favourable result.

What that would require, if adopted:

- a short, dated deviation statement in Methods §4.5 naming D1 and D2, quoting
  the preregistered sentence, and giving the 7 / 3 / 38 figure;
- the sensitivity matrix in the Supplement, with §4.5's 26-cell table;
- an append-only entry in `preregistration.md` §Amendments recording the
  deviation *as a deviation*, dated 2026-08-04, explicitly not backdated;
- no change to the classifier, the figure, or the 7 / 29 / 12 counts.

**Rejected alternative:** silently keeping the current text. The 10 % / 30 %
sentence is true but incomplete, and a reader comparing `preregistration.md`
against the published caption would find the gap unaided — as this dossier did.

---

## 8. Open questions carried forward

1. **Was the rule written before or after the sweep output was seen?** Not
   answerable from the repository (§2.1). Only the author can state it, and the
   statement would rest on recollection, not artefact.
2. **How should D3 read in the declaration?** Recorded here as a
   terminological ambiguity (§1.4). One line naming both readings and stating
   that the repository does not settle them is the conservative form; whether
   it belongs in the published declaration at all is not decided.
3. Whether the same blind spot (§5.2) affects other anchored claims whose
   `computed_value` is read from a derived artefact. **Not surveyed**, and
   deliberately not made a precondition for closing this dossier.

### 8.1 The classifier docstring has drifted from its own code

Internal, unpublished, and **not probative** of intent or chronology — recorded
because it is the most plausible origin of the preregistration's vocabulary.
`reliability_classification()` carries a docstring that its body contradicts on
three points:

| docstring says | code does |
|---|---|
| "Cell baseline is the mean of clean S1_M runs **at that input bin**" | `baseline = s1m_clean[f"{ch}_mean"].mean()` — averages **all** clean S1_M runs; there is no input-bin term |
| "Per cell × output × **input bin**" | the loop is `df_master.groupby(["scenario", "sex"])` — **scenario × sex only** |
| "Green: **no flags raised** AND …" | green requires only `hard_failure_rate == 0`, i.e. `diverged` + `implausible`; `clamped` and `not_steady_state` never enter |

The first two suggest the design once carried a per-input-bin baseline that was
simplified away, which would explain why "cell baseline" reads naturally as
"per-cell" in the preregistered sentence while the code's own author used the
same phrase for the S1_M reference (§1.4). The third mirrors D2 exactly: the
docstring says "flags", the code means the two hard flags.

**What this does not establish.** It does not show what the preregistered
sentence intended, and it does not date any decision. It is a lead, not
evidence.

### 8.2 Requirement on the independent recomputation, if one is built

A check that re-derives the three matrices must start **above**
`reliability_classification.csv` *and* above `cell_flag_summary.csv`: both are
outputs of the very chain under audit, and `mean_clean` is computed inside the
audited function itself. The run-level artefacts are tracked —
`data/runs/full_sweep/` holds **eight per-cell `aggregated.parquet` files**,
plus a pooled `aggregated.parquet` and `morris_sample.parquet` (the input
design, not run output). Rebuilding the flags, the clean-run means, the
deviations from (S1, M) and all three classifications from the eight per-cell
files would close the §5.2 blind spot for this claim, without waiting on the
general survey.
