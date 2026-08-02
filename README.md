# Pulse Reliability Atlas

> **Note:** This repository (`pulse_reliability_atlas`) hosts the code and data for the
> paper: *"An Open Reliability Atlas of Sensitivity and Failure Modes in the Pulse Physiology Engine."*

**The first open reliability atlas for the Pulse Physiology Engine
(v4.3.1).** This repository tells you — clinician, engineer, researcher,
educator — *where Pulse can be trusted*, *where it silently bends inputs
out of acceptance*, *where its solver gives up*, and *which inputs
actually drive each output*.

The full result is [`preprint/manuscript.md`](preprint/manuscript.md). The
short answer: see [Section "Plain-language summary"](#plain-language-summary)
below.

---

## For peer reviewers

This repository is the data-and-code companion to the *npj Digital Medicine*
submission. The three fastest entry points for verifying the work:

- **Preregistration** (commitments locked before any data was collected):
  [`preregistration.md`](preregistration.md).
- **Audit ledger** (every quantitative claim in the manuscript is
  machine-checked against the data):
  `uv run python scripts/audit_claims.py` — on a fresh public clone
  this prints `266/267 PASS ... 1 SKIPPED` (the T1.06u anchor is
  auto-skipped because it needs the gitignored raw S021 trajectories;
  with the authors' full `data/runs/` tree it prints `267/267 PASS`).
- **One-command reproduction** (Docker, fixed seed, ~9-23 h on a laptop
  depending on hardware and worker count):

  ```bash
  docker build -t pulse-atlas-engine engine/
  uv run python scripts/run_full_sweep.py --resume
  uv run python scripts/analyze_sweep.py
  uv run python scripts/make_figures.py
  ```

  A 5-minute smoke test (`uv run python scripts/run_pilot.py`, 22 runs)
  exercises the whole pipeline end-to-end. Full detail in
  [Reproducing the atlas](#reproducing-the-atlas) below.

---

## What is Pulse?

[Pulse](https://pulse.kitware.com) is the most-used open-source whole-body
human physiology simulator (Kitware, Apache-2.0). It models cardiovascular,
respiratory, gas-exchange, and pharmacology dynamics. People use it for:

- **Clinical research** (hypothesis generation, virtual-patient cohorts).
- **Medical-device validation** (testing ventilators, pumps, monitors against
  a virtual patient instead of human subjects in early-stage trials).
- **Teaching** (anaesthesia, ICU, paramedic training).

Pulse is widely cited and downloaded — but its developers themselves state
on the [Pulse FAQ](https://pulse.kitware.com/_f_a_q.html) (verified verbatim
2026-04-19, still current 2026-05-07):

> "We have not performed a systematic forward propagation or inverse
> quantification of model uncertainty, nor have we conducted a formal
> sensitivity analysis."

A 2020 study tag (`STUDY_SENSITIVITY_ANALYSIS_1_0_0`) in the Pulse repo did
apply Sobol indices to a different parameter class — **internal
lumped-parameter circuit values (cardiovascular and respiratory resistances and compliances)** used for model calibration — but no
sensitivity analysis on **user-facing operational inputs** (HR, BP, RR, Vt,
FiO2, PEEP) has been published, and that 2020 study has not been ported to
the 4.3.x release line (audit logged in
[`experiments_log/santino/S016`](experiments_log/santino/S016_pulse_gitlab_audit_may2026.md)).

That means **every Pulse user driving the engine from operational settings
has been operating without a map of where the engine is reliable** — until
this repository.

---

## Plain-language summary

We ran Pulse 4.3.1 **1,280 times** across:

- **7 inputs** (heart rate, blood pressures, breathing rate, tidal volume,
  inspired oxygen, PEEP) — sampled with Morris elementary effects.
- **4 scenarios** (healthy ventilated adult; mild, moderate, and severe
  acute respiratory distress syndrome — ARDS).
- **2 patient surrogates** (Pulse standard adult male and female).

Every run was classified by a four-flag detector:

- **clamped** — Pulse silently substituted an input we asked for.
- **diverged** — solver crashed / NaN / Inf.
- **implausible** — output ended up outside hard physiological bounds.
- **not_steady_state** — output didn't settle in the final 60 seconds.

What the atlas says, in one paragraph:

> Pulse 4.3.1 is **strongly skewed**: a handful of inputs dominate each
> output (top 3 inputs explain 93 % of sensitivity, on median). It does
> **not silently clamp** at the verified acceptance ranges — it rejects
> out-of-range inputs *loudly* with explicit error logs. Its solver
> diverges in **1.6 %** of our runs, and **all 20 divergent runs are in
> male patient cells in the Morris input-extreme regime** — the first
> quantitative sex-specific reliability finding for Pulse. (At midrange
> inputs, a complementary continuous-severity sweep shows divergence is
> approximately sex-balanced — the sex effect is regime-dependent; see
> manuscript §3.5.1.) Severe ARDS on the male surrogate is the worst
> reliability cell — every output unreliable. Healthy male and female
> adults at FiO2 = 1.0 produce **PaO2 above 600 mmHg, still drifting at
> the end of the locked 120 s window** — a *transient hyperoxia regime*
> (S021): under a 300 s rerun, PaO2 converges to a plateau ~ 20 mmHg
> below the alveolar-gas-equation prediction (~ 643 mmHg vs ~ 663 mmHg
> predicted), consistent with Pulse's modelled A-a gradient — not an
> overshoot. And Pulse's preferred ventilator mode (VC-AC) fails to
> deliver a steady tidal volume inside the 60-second window in
> **20.6 %** of healthy or ARDS configurations.

The detailed numbers, figures, and discussion live in
[`preprint/manuscript.md`](preprint/manuscript.md). The traffic-light grid
([Figure 6](figures/fig06_reliability_traffic_light.png)) is the most
actionable single artifact.

---

## What you get from this repo

| You are a … | Read this first | Then this |
|---|---|---|
| **Clinician / domain expert** wanting to know where Pulse is safe | [`preprint/manuscript.md`](preprint/manuscript.md) §3.7 (traffic-light table) and [Figure 6](figures/fig06_reliability_traffic_light.png) | [§4.1](preprint/manuscript.md) practical recommendations |
| **Engineer / device developer** building a Pulse-based validation pipeline | [`preprint/interim_findings.md`](preprint/interim_findings.md) (every finding linked to data) | [`results/cell_flag_summary.csv`](results/cell_flag_summary.csv) (Table 1 — failure breakdown per scenario × sex) |
| **Researcher / reviewer** auditing the methodology | [`preregistration.md`](preregistration.md) (commitments locked before data collection) and [`experiments_log/INDEX.md`](experiments_log/INDEX.md) | [`src/detector.py`](src/detector.py) (locked-threshold classifier) |
| **Student** wanting to learn how Pulse and Morris-EE sensitivity work | this README + [`src/sampler.py`](src/sampler.py) (~50 lines, well commented) | [`scripts/run_pilot.py`](scripts/run_pilot.py) (the 22-run gate study) |
| **Future Pulse user** running their own simulations | [`engine/run_atlas_engine.py`](engine/run_atlas_engine.py) (drop-in wrapper without the silent FiO2 cap) | [`reference/pulse_run_template.md`](reference/pulse_run_template.md) |

---

## Headline results

(All numbers from the 1,280-run Morris sweep. Source artifacts in
[`results/`](results/) and figures in [`figures/`](figures/). See
[`experiments_log/santino/S006_full_morris_sweep.md`](experiments_log/santino/S006_full_morris_sweep.md)
for the lab-notebook entry.)

| Hypothesis | Outcome |
|---|---|
| **H1 — top-3 inputs explain ≥ 50 % of sensitivity** | **PASS, 48 / 48** cell × output combos. Median 0.928, range 0.658 – 0.998. |
| **H2 — silent clamping ≥ 5 %** | **NOT supported**, 0 / 1,280. Pulse rejects out-of-range inputs *loudly* (verified by explicit clamp probes in S005). |
| **H3 — divergence outside ARDS 0.91 – 0.945** | **PASS** — 1.6 % overall divergence rate. **All 20 divergent runs are male in the Morris input-extreme regime** (the complementary continuous-severity sweep at midrange inputs shows divergence approximately sex-balanced inside the [0.879, 0.945] band — see §3.5.1). Mechanism confirmed (S018): mediated by Pulse's `BloodVolumeBaseline` gap (male default 4,802.63 mL vs female 3,996.09 mL); reducing the male BV monotonically eliminates divergence (20 / 20 → 2 / 20 → 0 / 20 across BV = 4,802.63 → 4,400 → 4,082.24 mL). |
| **H4 — sex-specific reliability** | **Partially supported (gas-exchange only)** — under Benjamini–Hochberg FDR control at q = 0.05, **5 of 24** cell × output Wasserstein distances survive the permutation null; all 5 are gas-exchange (PaCO2 × 3, SpO2 × 1, PaO2 × 1). The naive-α = 0.05 analysis would flag 6; S2 SpO2 (p_emp = 0.022) is demoted by BH-FDR. Cardiovascular (HR, MAP) and Vt sex effects do not exceed the permutation-null baseline at our sample size. Input-importance rankings are similar between sexes (Spearman ρ 0.75 – 1.00 in S2 / S3, wide CIs). |

Two structural Pulse findings, independent of the hypotheses:

- **F-003** — 34 implausibly-flagged runs produce PaO2 > 600 mmHg at
  FiO2 = 1.0 (91 % at FiO2 ≥ 0.95), still drifting at t = 120 s.
  *Transient hyperoxia regime*: under a 300 s rerun (S021), PaO2
  converges to a plateau ~ 20 mmHg below the alveolar-gas-equation
  prediction (S1 median 643 mmHg vs ~ 663 mmHg predicted) — consistent
  with Pulse's modelled A-a gradient. The original flag reflects (a)
  the locked 120 s window being insufficient for hyperoxia convergence
  and (b) the conservative classifier bound, *not* an overshoot.
  See `preprint/manuscript.md` §3.8.
- **F-004** — 264 / 1,280 (20.6 %) of runs fail VC-AC's tidal-volume
  steady-state test in 60 s. **Mechanism causally identified (S014):**
  patient-ventilator dyssynchrony at the inspiration trigger.
  **Operator fix:** set inspiration trigger pressure to −2 cmH2O
  (collapses *median* Vt CV from 0.351 → 0.016; worst-case from 1.826
  → 0.018; lock-below-0.05 fraction = 78.1 %). See
  `preprint/manuscript.md` §3.8 + §4.2.

---

## How the data was produced (in one diagram)

```
              ┌────────────────────────────────────┐
              │  preregistration.md (locked plan)  │
              └────────────────────────────────────┘
                              │
                              ▼
       ┌──────────────────────────────────────────────────┐
       │  src/sampler.py  ──→  Morris N=20, levels=4      │
       │                       7 inputs, 160 unique pts   │
       └──────────────────────────────────────────────────┘
                              │
                              ▼   (× 4 scenarios × 2 sexes = 8 cells)
       ┌──────────────────────────────────────────────────┐
       │  src/scenario.py  ──→  builds 1,280 configs      │
       │                       enforces DBP/SBP ratio     │
       └──────────────────────────────────────────────────┘
                              │
                              ▼
       ┌──────────────────────────────────────────────────┐
       │  src/runner.py  ──→  Docker pulse-atlas-engine   │
       │                       2 parallel containers      │
       └──────────────────────────────────────────────────┘
                              │
                              ▼   (per-run: output.csv + pulse.log)
       ┌──────────────────────────────────────────────────┐
       │  src/detector.py ─→ 4 flags per run              │
       │  src/aggregator.py → one parquet row per run     │
       └──────────────────────────────────────────────────┘
                              │
                              ▼
       ┌──────────────────────────────────────────────────┐
       │  src/analysis_morris.py  + src/analysis_compare.py│
       │   → Morris μ*, σ, bootstrap CI                   │
       │   → H1 / H2 / H3 / H4 evaluation                 │
       │   → reliability traffic light                    │
       └──────────────────────────────────────────────────┘
                              │
                              ▼
              figures/  +  preprint/manuscript.md
```

---

## Reproducing the atlas

You need: Docker, [uv](https://github.com/astral-sh/uv), a machine with
≥ 8 GB RAM and ≥ 3 CPU cores, and roughly 9-23 hours of compute:
~ 9 h on the reference laptop with 3 parallel Docker workers, ~ 14 h
with 2, and 23 h as actually measured on a slower laptop. The full
1,280-run sweep represents ~ 27-46 h of aggregate Pulse container time
depending on host speed (Supplement §S12).

To also reproduce the supplementary S023 SHAP cross-check (manuscript
§4.5), install Python deps with `uv sync --extra ml` (adds
`scikit-learn` and `shap` to the environment); the core atlas
pipeline does not require these.

```bash
# 1. Build the atlas Pulse image (Apache-2.0 from kitware/pulse:4.3.1)
docker build -t pulse-atlas-engine engine/

# 2. Run the 1,280-simulation sweep
uv run python scripts/run_full_sweep.py --resume

# 3. Compute Morris indices, sex comparison, reliability classification
uv run python scripts/analyze_sweep.py

# 4. Generate paper figures
uv run python scripts/make_figures.py
```

`--resume` makes the sweep crash-safe: every successful run writes
`run_meta.json` with `exit_code = 0`, and the next launch skips them.
Pulse 4.3.1 is bit-exact deterministic for fixed inputs (verified by
S005, gate G5), so reruns reproduce upstream values to 1e-6 relative
tolerance for all 6 outputs.

### Pinned image hashes (for byte-level reproducibility)

Manuscript §2.8 names two `pulse-atlas-engine` image hashes that bound
the sweep's exact provenance:

* Initial atlas image — produced the S006 1,280-run sweep
  (`data/runs/full_sweep/`, 2026-04-26).
* `b2e0e807803d` — post-S014 SDK sed-patch rebuild; produced the
  S015 audit re-execution (38 / 40 runs bit-exact, 2 expected
  pre-patch divergences). Atlas results are reproducible under either
  hash because Pulse's solver is deterministic.

A fresh `docker build` from this repo will not match these hashes
byte-for-byte (base layers and pip caches differ over time), but the
*simulation outputs* match to 1e-6 relative tolerance across rebuilds
sharing the same `kitware/pulse:4.3.1` upstream base. See manuscript
§2.8 and S007 (targeted reproducibility check) / S015 (logic audit)
for the verification protocol.

### Verifying everything is wired up

After the pilot completes (or in lieu of running the full sweep for a
quick canary check), confirm the pipeline by running:

```bash
uv run pytest tests/ -v                       # S009/S015 unit tests
uv run python scripts/audit_claims.py          # S024 -- fresh clone prints 266/267 PASS (1 SKIPPED: T1.06u, gitignored raw S021 data); 267/267 with full local data
uv run python scripts/audit_claims.py --check-paper-sync --check-monograph   # + 98 paper crosswalk entries and 26 monograph anchors
```

The audit has three layers, all gated by the pre-commit hook and by CI:

| Layer | Flag | What it checks |
|---|---|---|
| Claims ledger | *(default)* | Re-derives 267 numerical claims from the canonical data artifacts and compares them against the value printed in the manuscript. This is the layer that verifies **correctness**. |
| Paper crosswalk | `--check-paper-sync` | 98 entries: every number the npj paper and supplement restate from the monograph still appears there, with the expected occurrence count (`preprint_npj/paper_to_monograph_map.md`). |
| Monograph anchors | `--check-monograph` | 26 anchors: numerical claims that live **only** in the monograph, with no ledger anchor and no crosswalk row (`preprint/monograph_anchor_map.md`). A presence guard — it detects a verified value silently drifting; it does **not** verify correctness, so every anchor is re-derived by hand before being locked. |

The pilot gate study itself is a runnable smoke test on cell (S1, M):

```bash
uv run python scripts/run_pilot.py     # 22 runs, ~5 minutes
```

It exercises everything end-to-end with reproducibility reruns and
deliberate clamp probes — useful as a wider smoke test on a new
machine.

---

## Repository layout

```
pulse_reliability_atlas/
├── CLAUDE.md                    project rules (AI sparring partner mode)
├── preregistration.md           commitments locked before data collection
├── README.md                    you are here
├── preprint/
│   ├── manuscript.md            the methods paper draft
│   ├── interim_findings.md      every finding (F-001..F-013) traced to its experiment
├── engine/
│   ├── Dockerfile               atlas-only Pulse image
│   ├── run_atlas_engine.py      wrapper without the silent FiO2 cap
├── src/
│   ├── sampler.py               Morris (SALib)
│   ├── scenario.py              sample row → Pulse config
│   ├── runner.py                Docker exec, parallel, --resume
│   ├── aggregator.py            CSVs → parquet, applies detector
│   ├── detector.py              4-flag classifier (clamped / diverged / implausible / not_steady_state)
│   ├── analysis_morris.py       μ*, σ, bootstrap CI, H1, Sobol promotion
│   ├── analysis_compare.py      H4 Wasserstein, Spearman, traffic light, flag heatmaps
├── scripts/
│   ├── run_pilot.py             22-run preregistration §Pilot gate (S005)
│   ├── run_full_sweep.py        1,280-run Morris sweep (S006)
│   ├── analyze_sweep.py         all post-sweep analyses
│   ├── make_figures.py          figures for the preprint
│   ├── scenario_smoke_test.py   8-cell mid-range smoke test (S004)
│   ├── validate_detector_on_existing_runs.py
│   ├── regenerate_index.py      rebuilds experiments_log/INDEX.md from frontmatter
├── data/runs/
│   ├── full_sweep/              S006 — 1,280-run Morris sweep (headline)
│   │   ├── morris_sample.parquet   canonical 160-point sample (seed=42)
│   │   ├── aggregated.parquet      1,280 rows × all outputs + flags + meta
│   │   └── <cell>/aggregated.parquet  per-cell mirror
│   ├── full_sweep_repro/        S007 / S015 reproducibility re-runs
│   ├── s014_trigger_lockout/    S014 — F-004 mechanism causal test
│   ├── s018_blood_volume/       S018 — BV dose-response (H3 mechanism)
│   └── s021_hyperoxia_convergence/  S021 — F-003 300 s window rerun
├── results/
│   ├── (top-level)              core analysis artifacts (csv + parquet)
│   ├── s022/                    NSS sub-mode attribution side-table
│   └── s023/                    SHAP-vs-Morris cross-check (ml extras)
├── figures/                     Figures 1–6 (PNG + PDF)
├── experiments_log/
│   ├── INDEX.md                 auto-regenerated table of all experiments
│   ├── README.md                lab-notebook conventions
│   └── santino/                 S001 … S025 entries (one .md each)
└── reference/                   verified Pulse run templates and limits
```

---

## Project context

This atlas is the **first publishable output** in the maintainer's PhD
pipeline. Two downstream papers will cite it:

- **Paper 1** — pediatric translation layer for Pulse 4.3.1. Cites this
  atlas for baseline adult Pulse behaviour and the verified reliability
  envelope. [`Pulse_translation_new/`](https://github.com/santinon/) (separate repo, in progress).
- **Paper 2** — native pediatric Pulse fork. Will use this atlas's Morris
  μ\* ranking to prioritize which adult-tuned C++ equations to patch first.

Origin note: this repository began as a 7-day Cerebral Valley "Built with
Opus 4.7" hackathon entry (PulseProbe). The hackathon credit application
was not granted; the scientific scope survived, executed as a methods-paper
contribution to the PhD. Hackathon-era framing documents are preserved in
[`attic/`](attic/) for historical traceability.

---

## How to read the experiments log

`experiments_log/santino/S001` … `S025` are individual lab-notebook
entries. Every entry follows the same template — *hypothesis →
motivation → method → what we tried (incl. dead ends) → results →
interpretation → next steps* — so a reviewer can audit any decision
without prior context.

Quick map (highlights — full audit trail in
[`experiments_log/INDEX.md`](experiments_log/INDEX.md)):

- **S001** Docker + hardware smoke test (3-parallel verified safe).
- **S002** Project bootstrap.
- **S003** 12 verified Pulse 4.3.1 limitations (every claim → a primary
  source).
- **S004** Atlas Docker image + 8-cell scenario smoke + detector regex
  recalibration (this is where we discovered the upstream silent FiO2
  cap and the false-positive `clamped` regex).
- **S005** Pilot gate (22 runs, S1_M, all 5 preregistered criteria pass,
  3 pipeline bugs surfaced + fixed).
- **S006** Full sweep + analysis + 8-step verification (the paper's
  data-collection event).
- **S007** Targeted reproducibility check at three independent layers,
  all bit-exact (pre-publication).
- **S008** Tier-1 statistical refinement (block bootstrap on σ,
  Wasserstein permutation null, Spearman CI, divergence mechanism).
- **S009** Tier-2 robustness (seed stability, continuous-ARDS
  micro-sweep, pytest, GitHub Actions CI).
- **S010** Literature-review pass; every reference DOI/PMID-verified.
- **S012** Steady-state window cross-output audit (does F-003 / F-004
  contaminate other channels? — no, see §3.8.1).
- **S013** Lexical lockdown (manuscript failure-mode taxonomy
  normalisation).
- **S014** Trigger-pressure lockout — causally identifies F-004 as
  VC-AC patient-ventilator dyssynchrony (median Vt CV 0.351 → 0.016).
- **S017** Cornish 2023 cross-mapping against the atlas's 6-output
  panel (Table 2).
- **S018** Blood-volume mechanism falsification — confirms BV gap
  mediates the all-male divergence cluster
  (20 / 20 → 2 / 20 → 0 / 20 across BV brackets).
- **S021** Hyperoxia convergence — 60-run 300 s rerun reframes F-003
  from "overshoot" to "transient hyperoxia regime + AGE undershoot."
- **S022** No-compute failure-mode attribution audit of
  `not_steady_state` (Appendix C).
- **S023** Supplementary ML/SHAP cross-check of Morris μ\* rankings
  (manuscript §4.5; requires `uv sync --extra ml`).
- **S024** Pre-submission claims-ledger audit (266 / 267 PASS on a
  public clone — 1 anchor auto-skipped, needs gitignored raw S021 data;
  267 / 267 with the authors' full data tree).
- **S025** Pre-release OSS code-hygiene audit + fixes (this release).

---

## Citation

Plain text:

```
Nanini, S., et al. (2026). An open reliability atlas for the Pulse
Physiology Engine: sensitivity, divergence, and sex-stratified failure modes.
Preprint forthcoming on arXiv. Code: https://github.com/santinon/pulse_reliability_atlas
```

BibTeX:

```bibtex
@misc{nanini2026pulseatlas,
  author       = {Nanini, Santino and others},
  title        = {An Open Reliability Atlas of Sensitivity and Failure Modes in the Pulse Physiology Engine},
  year         = {2026},
  howpublished = {\url{https://github.com/santinon/pulse_reliability_atlas}},
  note         = {Preprint forthcoming on arXiv; arXiv identifier and Zenodo DOI added on deposit.}
}
```

A machine-readable [`CITATION.cff`](CITATION.cff) is also provided —
GitHub renders a "Cite this repository" button from it, and reference
managers (Zotero, Mendeley) import it directly.

(arXiv preprint identifier added on upload. Zenodo DOI — covering code, data, and the companion monograph — added when the repository archive is deposited.)

---

## License

Apache 2.0, matching the upstream Pulse engine licence. See [LICENSE](LICENSE).

---

## Contact

Santino Nanini · santino.nanini@umontreal.ca

PhD work conducted under the maintainer's PhD programme; this repo is
self-contained and runs without any other internal dependencies.
