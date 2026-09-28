# Nature Portfolio Reporting Summary — working draft (E-1)

**This file is not the deliverable.** The deliverable is Nature's own interactive
PDF, filled in and uploaded with the manuscript:

- Interactive form: <https://nature.com/documents/nr-reporting-summary.pdf>
- Flat reference copy (what this draft was built against):
  <https://www.nature.com/documents/nr-reporting-summary-flat.pdf>
  (7 pages, form dated 2023-08-02, downloaded and read 2026-08-02)

This file exists so that filling that PDF is transcription rather than
composition. Every answer below is drawn from the repository; the fields only
the corresponding author can supply are marked **🔲 AUTHOR**.

> **Trap worth knowing before you start.** The form says *"Please do not
> complete any field with 'not applicable' or n/a."* That applies to the
> **free-text** fields. The checkbox grids have their own explicit `n/a`
> column, and ticking it there is the intended behaviour. So: tick `n/a` in the
> grids, but never *type* "n/a" in a text box — say what was done instead, or
> why the item cannot arise.

> **The form is final at submission.** *"For final submission: please carefully
> check your responses for accuracy; you will not be able to make changes
> later."*

---

## Header

| Field | Value |
|---|---|
| Corresponding author(s) | 🔲 **AUTHOR** |
| Last updated by author(s) | 🔲 **AUTHOR** (date of upload) |

---

## Statistics

Checkbox grid — tick *Confirmed* or *n/a* for each. Proposed answers, with
where a reviewer would find each one:

| Item | Proposal | Locus |
|---|---|---|
| Exact sample size (n) per group/condition | **Confirmed** | 1,280 simulations = 8 (scenario × sex) cells × 160; 160 = 20 Morris trajectories × (7 inputs + 1). Methods §4.3, Table 1 per cell. |
| Distinct samples vs the same sample measured repeatedly | **Confirmed** | Each run is an independent simulation from its own configuration; no run contributes twice. Methods §4.1 and §4.3. |
| Statistical test(s) used AND one- or two-sided | ⚠️ **see below** | Methods §4.6 names every test. It does **not** state sidedness anywhere. |
| Description of all covariates tested | **n/a** | No covariate-adjusted model is fitted. Scenario and sex are the design factors and every result is reported disaggregated by them, not adjusted for them. |
| Assumptions or corrections (normality, multiple comparisons) | **Confirmed** | Benjamini–Hochberg FDR at *q* = 0.05 over the 24-test family; all methods used are non-parametric, so no normality assumption is made. Methods §4.6. |
| Central tendency AND variation / uncertainty | **Confirmed** | Morris μ\* with non-parametric 95 % bootstrap CIs from 1,000 trajectory-level resamples; σ reported alongside μ\*. Methods §4.6. |
| Test statistic with CI, effect size, df, exact P | ⚠️ **partly** | The Wasserstein distance **is** the effect size and is reported per test. There are no degrees of freedom — the null is a permutation null, not a parametric family. Exact P values are given except at the resolution floor: with 2,000 permutations the smallest resolvable value is 1/2,000, and the two tests that reach it are reported as *P* < 0.001, which the Methods states explicitly. |
| Bayesian analysis — priors and MCMC settings | **n/a** | No Bayesian analysis. |
| Hierarchical/complex designs — level of testing | **Confirmed** | Tests are run per (scenario × output) cell, which is the level at which male and female distributions are comparable; the cell structure is stated in Methods §4.3. |
| Estimates of effect size, and how calculated | **Confirmed** | Wasserstein distance between male and female clean-run distributions; Spearman ρ for cross-sex rank agreement, with paired-input bootstrap 95 % CIs from 2,000 resamples. |

### ⚠️ One thing the form asks that the manuscript does not currently state

**Sidedness.** The form requires *"the statistical test(s) used AND whether they
are one- or two-sided"*. `paper.tex` §4.6 names the permutation test, the BH
correction and the Spearman correlation, but never says one- or two-sided.

**Confirmed in the implementation**, not inferred from the statistic's name.
`src/analysis_compare.py` computes the empirical p-value as

```python
p_emp = float(np.mean(null >= w))
```

which counts only null draws at or above the observed distance. Upper tail
only. This is forced by the design rather than chosen: a Wasserstein distance
is non-negative, so "more extreme" can only mean larger, and there is no lower
tail to test.

Two consequences worth stating on the form if there is room, since it asks for
the test statistic and its uncertainty:

- There are **no degrees of freedom** — the reference distribution is built by
  2,000 relabellings of the pooled sample, not drawn from a parametric family.
- The plain proportion above can return exactly 0 when no null draw reaches the
  observed distance. The manuscript already handles this by reporting such
  tests as *P* < 0.001. (Whether to use the (b+1)/(B+1) estimator instead is a
  known open nit, audited on 2026-07-06 and **deliberately held** by the author
  until peer review; it changes no conclusion, since 0 and 5 × 10⁻⁴ both
  survive the BH correction. Not reopened here.)

**This is a claim about the manuscript's statistics and I have not touched the
manuscript.** Two ways forward, author's call:

1. State the sidedness in the Reporting Summary only. Defensible — the form is
   where the question is asked.
2. Add four words to Methods §4.6. Cleaner for a reader, but it is a change to
   the statistical description of the paper, so it needs your decision and
   ideally passes in front of the four reviewers with everything else.

---

## Software and code

**Data collection**

> Simulations were produced by the Pulse Physiology Engine v4.3.1 (Kitware,
> Apache-2.0), executed inside a single pinned Docker image
> (`pulse-atlas-engine`) so that every run in the sweep used bit-identical
> engine binaries. Runs were orchestrated by a Python 3.12 layer around Pulse's
> command-line interface, which emitted each configuration as JSON and captured
> the resulting time-series CSV and engine setup log.

**Data analysis**

> Python 3.12. SALib ≥ 1.5.0 (Morris sampling and elementary effects);
> NumPy ≥ 1.26; SciPy ≥ 1.13; pandas ≥ 2.2 with pyarrow ≥ 16 (artefact
> storage); matplotlib ≥ 3.9 and seaborn ≥ 0.13 (figures); pydantic ≥ 2.8
> (configuration validation); tqdm ≥ 4.66. The supplementary SHAP
> cross-verification additionally used scikit-learn ≥ 1.5 and shap ≥ 0.46.
> All analysis code is released under Apache-2.0 at
> <https://github.com/santinon/pulse_reliability_atlas>.

Taken from `pyproject.toml` as declared. 🔲 **AUTHOR** — decide whether to give
the *resolved* versions from the lockfile instead of the declared floors. The
resolved versions are the reproducible ones and Nature prefers exact versions;
the floors are what the project actually commits to supporting.

---

## Data

A data availability statement is already in the manuscript. Its current
substance: raw simulation outputs, derived artefacts, figures and the audit
ledger **will be deposited at Zenodo**, with pre-deposit access from the
corresponding author; the traffic-light map is additionally released as CSV and
JSON.

🔲 **AUTHOR** — the Zenodo deposit is still future tense. The Reporting Summary
is uploaded at submission, so either the DOI exists by then or the statement
stays "will be deposited". Worth settling before upload rather than at proof.

---

## Research involving human participants, their data, or biological material

**No human participants, no human data, no biological material.** Every input
and output is generated by a physiology simulator. Nothing was recruited,
consented, or collected.

**Reporting on sex and gender** — this one deserves a real answer rather than a
dismissal, because the study is sex-stratified by design:

> The study involves no human participants. Sex enters as a simulator input:
> the engine is configured with two adult reference bodies, one male and one
> female, whose weights are CDC growth-chart 50th-percentile values and whose
> heights are stated in Methods §4.2. Within the engine, sex determines the
> allometric blood-volume baseline and body composition. Every result in the
> paper is reported disaggregated by sex rather than pooled, and a sex
> asymmetry in solver divergence is a primary finding. No claim is made about
> human sex differences; the finding is about the engine's behaviour on
> sex-specific parameterisations.

**Reporting on race, ethnicity, or other socially relevant groupings** — the
engine exposes no such parameter and none was varied. Say that, rather than
"n/a".

**Population characteristics / Recruitment / Ethics oversight** — no population,
no recruitment, no human-subjects oversight required. State the reason; do not
type "n/a".

---

## Field-specific reporting

Three choices: *Life sciences* · *Behavioural & social sciences* ·
*Ecological, evolutionary & environmental sciences*.

**Proposal: Life sciences.** 🔲 **AUTHOR to confirm.** None of the three fits a
pure in-silico study cleanly, but Life sciences is the closest and its five
disclosure points all have real answers here (below). npj Digital Medicine is a
health-sciences journal, which points the same way.

### Life sciences study design

*"All studies must disclose on these points even when the disclosure is
negative."*

**Sample size**

> 1,280 simulations: 8 (scenario × sex) cells × 160 runs, where 160 = 20 Morris
> trajectories × (7 inputs + 1). The 20 trajectories were fixed in the
> preregistration before any data were collected, chosen as enough to give
> stable μ\* rankings while keeping the full sweep tractable on a single
> machine. No power calculation applies: the design is a deterministic
> screening sweep, not a sampling of a population, so the sample size is set by
> the Morris design and the input dimension rather than by an effect size.

**Data exclusions**

> **No run was excluded from the atlas.** All 1,280 runs are reported and every
> one contributes; a preregistered four-flag classifier categorises each run's
> failure mode rather than discarding it.
>
> One analysis-level restriction, preregistered and stated in the manuscript:
> the Morris elementary-effect estimator uses only flag-clean run pairs,
> because an effect computed across a diverged or clamped run would not measure
> the input under study. The consequence is characterised in the paper rather
> than left implicit — a regime unstable enough to flag its own runs cannot
> supply the pairs needed to characterise it.

**Replication**

> The full 1,280-run sweep was executed end-to-end three times. Bit-exact
> reproduction was verified at three independent layers: the input sample
> regenerated from the fixed sampler seed, the per-cell aggregate tables
> re-obtained by re-executing against the pinned Docker image, and the derived
> statistics recomputed from those tables. The sweep and the pilot were
> additionally reproduced by a co-author on a second, independent x86_64 host
> (AMD Ryzen 5, Linux under WSL2). All replication attempts succeeded.

**Randomization**

> No allocation to experimental groups occurs; there is nothing to randomize in
> the clinical sense. The randomization present is the Morris trajectory
> generation, drawn by SALib at 20 trajectories and 4 grid levels per input
> under fixed seed 42, which makes the sample reproducible rather than
> arbitrary. Every (scenario × sex) cell receives the same input sample, so
> cells are compared on identical coordinates.

**Blinding**

> Blinding was not used and is not applicable to this design, for a stated
> reason rather than by omission: the outcome is deterministic simulator output
> classified by the four-flag algorithmic detector, whose flags and numerical
> thresholds were preregistered before any data were collected. No human
> judgement enters between the run and its classification, so there is no
> assessment for an observer's expectation to bias. The separate cell-level
> traffic-light aggregation is a downstream summary of those run-level
> classifications; its colour rule departs from the preregistered wording, and
> that departure is declared in Methods §4.5 with a sensitivity analysis in
> Supplement §S3.11.

**Field work** — No.

---

## Reporting for specific materials, systems and methods

Both grids: tick `n/a` throughout.

**Materials & experimental systems** — Antibodies ☐ · Eukaryotic cell lines ☐ ·
Palaeontology and archaeology ☐ · Animals and other organisms ☐ ·
**Clinical data ☐** · Dual use research of concern ☐ · Plants ☐

**Methods** — ChIP-seq ☐ · Flow cytometry ☐ · MRI-based neuroimaging ☐

*Clinical data is **not** involved:* no patient records are used. The MIMIC-IV
coverage cross-check is deferred to future work and forms no part of this
manuscript. Consequently no clinical-trial registration and no CONSORT
checklist arise.

---

## Still needed from the author

| | |
|---|---|
| 🔲 | Corresponding author name, and the date of upload |
| 🔲 | Confirm *Life sciences* as the field-specific category |
| 🔲 | Declared dependency floors, or resolved lockfile versions |
| 🔲 | Whether the Zenodo DOI will exist at submission |
| 🔲 | Decide the sidedness question above — Reporting Summary only, or also Methods §4.6 |

Nothing in `paper.tex`, `supplement.tex` or `manuscript.md` was modified to
produce this draft.
