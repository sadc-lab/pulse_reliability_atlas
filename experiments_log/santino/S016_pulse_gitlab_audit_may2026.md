---
id: S016
author: santino
date: 2026-05-07
status: done
tags: [literature, verification, pulse, gitlab, sensitivity-analysis, version-tracking]
linked_code: []
linked_data: []
supersedes: ""
related: [S003, S010]
---

# S016 — Pulse GitLab + literature re-audit (May 2026): version state, V&V infrastructure, and the 2020 sensitivity-analysis study tag

## Hypothesis

Two parts:

1. The Pulse FAQ statement that "we have not performed a systematic forward propagation or inverse quantification of model uncertainty, nor have we conducted a formal sensitivity analysis" is still **literally accurate** in the current public release.
2. There has been **no recent change** to the Pulse codebase (since the 2026-04-07 source audit logged in S003 / S010) that would invalidate this paper's premise or require us to update our pinned version.

## Motivation (why now)

The methods paper draft is approaching submission. Two specific risks need to be ruled out before locking the preprint:

- **Version drift.** Our project pins Pulse 4.3.1 (Sept 2024). If Kitware shipped a 4.3.2 (or later) that contains physiology changes, our 1,280-run Morris sweep would be measuring a stale engine.
- **Claim drift.** The premise *"first sensitivity analysis on Pulse"* is the spine of the paper's motivation. If this is overstated — if Kitware has done any kind of SA we've missed — the framing has to be corrected before peer review catches it.

We also wanted a complete map of how Kitware itself tests the engine, so the paper's discussion can position our atlas precisely against existing V&V coverage rather than claiming a gap that isn't really one.

## Method (how)

Phased, per the project rule (internal → MCP → web). All against the local clone at `C:\Users\santi\projets\Pulse_engine_adults_Gitlab\engine` and the remote at `gitlab.kitware.com/physiology/engine`.

1. **Re-verify the local clone state.** `git log -1` on the local checkout, `git remote -v`, `git branch -a`, then `git fetch --all --tags --dry-run`.
2. **Expand the refspec** (the local clone was tracking only `stable`) and `git fetch origin "+refs/heads/*:refs/remotes/origin/*"` to pull every active branch.
3. **Diff REL_4_3_1..REL_4_3_2** with `git diff --shortstat` and `git diff --stat` to characterize what changed between the version we pin and the latest stable tag.
4. **List branch tips** for `stable`, `integration`, all `feature/*`, `study/itm`. Date and one-line summary for each.
5. **Inspect the V&V update** on `integration` (commit `26f05360e`, "V&V Updates", 2026-05-03): file list and short stat.
6. **Inspect `feature/ventilator_investigation`** (relevant to our PC-AC vs VC-AC findings): `git diff origin/integration...origin/feature/ventilator_investigation --stat`.
7. **Map the V&V infrastructure.** Locate validation tables, scoring code, test drivers, HTML report generators across the C++/Java/Python sides. Cross-check against `pulse_engine_internals_for_future_paper.md`.
8. **Inspect the `STUDY_SENSITIVITY_ANALYSIS_1_0_0` tag** (2020-07-20): read `src/cpp/study/sensitivity_analysis/ReadMe.md` verbatim, list the Python and C++ source files, look at `analysis.py` to identify the parameters being analyzed.

## What we tried (including dead ends)

- **DeepWiki on `kitware/pulse` and `kitware/PulsePhysiologyEngine`** — both return "Repository not found." Pulse's primary remote is `gitlab.kitware.com`, not GitHub, so DeepWiki has no index.
- **AlphaXiv search** for "Pulse Physiology Engine validation Bray Webb mechanical ventilator simulation" returned zero results — Pulse's primary venue (SN Comprehensive Clinical Medicine, MDPI Bioengineering, PLoS One) is not indexed by alphaXiv (computer-science / arXiv only). Falling back to in-repo references for Bray 2019 and Webb 2023 was sufficient since both are already verified in S010.
- The local clone's refspec was `+refs/heads/stable:refs/remotes/origin/stable`, so the first dry-run fetch only announced new tags and made it look like nothing had changed remote-side. Expanded the refspec to `+refs/heads/*:refs/remotes/origin/*` to actually see the full branch picture.

## Results

### Pulse stable release state (as of 2026-05-07)

| Tag | Date | What's in it |
|---|---|---|
| `REL_4_3_1` | 2025-01-24 | The version this project pins. |
| `REL_4_3_2` | 2025-08-12 | The current `stable` head. |

`REL_4_3_1..REL_4_3_2` diff: **7 files, +46 / −17 lines**, all build-system. Touched files: `.gitignore`, `CMakeLists.txt`, `cmake/external/External_Eigen3.cmake`, `dockcross.cmake`, `xcompile.bat`, `xcompile.cmake`, and one .NET binding (`src/csharp/pulse/engine/PulseEngine.cs`, 4 lines). Commit message: *"Support web-wasm dockcross builds."*

**No physiology, validation, patient-setup, solver, or model-parameter code changed.** Re-running our 1,280-run sweep on 4.3.2 would produce numerically identical results.

### Active development branches

State of `gitlab.kitware.com/physiology/engine` after expanding refspec:

| Branch | Tip date | Substance |
|---|---|---|
| `stable` | 2025-08-12 | REL_4_3_2 (build-system patch only). |
| `integration` | **2026-05-03** | "V&V Updates" by Aaron Bray — V&V infrastructure expansion (see below). |
| `feature/ECMO_updates` | **2026-05-06** | Most recent commit anywhere on the repo. |
| `feature/ventilator_investigation` | 2026-04-03 | New `study/ventilator/` study comparing `MechanicalVentilator` system vs `MechanicalVentilation` action — relevant to our PC-AC findings. |
| `feature/sepsis` | 2026-02-26 | Sepsis updates. |
| `feature/burn` | 2026-01-25 | Lund-Browder chart added to automated validation. |
| `study/itm` | 2026-03-25 | DARPA "In The Moment" program work. |
| `feature/cxx20`, `feature/drug_fixes`, `feature/engine_pool` | ≥ 2024 | Stale. |

### V&V Updates commit on `integration` (2026-05-03)

23 files, **+923 / −316**. Touches `SEValidationTarget.{h,cpp}`, `Validation.proto`, the Python validation pipeline (`patient_validation.py`, `segment_validation.py`, `timeseries_validation.py`, `cdm/io/validation.py`, `cdm/validation.py`), Java testing classes, and method docs. Commit message lists six concrete additions:

- "Add support to baseline the validation data associated with automated validation spreadsheets."
- "Create html validation tables that compare and easily show the baseline validation data to the validation of the current build."
- "Updated the validation proto definition to support all this."
- "Fix support for validation spreadsheets to reference values calculated on different tabs."
- "Update Dehydration docs now that its inter-referenced tables are working."
- "Add support to validate a single patient via run script."

Reading: this is regression-detection tooling improvement, not a methodology change. Kitware's V&V philosophy is unchanged — they're making it easier to baseline and diff per-build validation results. **No new sensitivity analysis or uncertainty quantification capability** is introduced.

### `feature/ventilator_investigation` overlap with our work

Branch adds 818 net lines across 4 files, primarily `src/python/pulse/study/ventilator/ventilator_vs_ventilation.py` (515 lines) and `ventilation_log_plotting.py` (257 lines). The study compares Pulse's **`MechanicalVentilator` system** (the full equipment model) against the **`MechanicalVentilation` action** (the simpler-action interface). The branch was last updated 2026-04-03 — Kitware is currently looking at ventilator behavior, which is directly adjacent to our F-004 findings (Vt steady-state failures in 20.6 % of VC-AC runs).

### Pulse V&V infrastructure (full map)

For the discussion section of the paper. Layered as four tiers:

1. **Solver verification.** BiCG circuit solver compared against an external third-party circuit solver (`docs/Methodology/CircuitMethodology.md`). C++ unit tests in `src/cpp/cdm/test/` (BasicCircuitTest, GasCompartmentTest, LiquidCompartmentTest, …) and `src/cpp/engine/human_adult/whole_body/test/` (CardiovascularCircuit, RenalCircuit, AcidBaseTests, …). Eigen tolerance ~1e-16. Drivers: `src/cpp/test_driver/main.cpp`; Java `ScenarioTestDriver` and `CDMUnitTestDriver`.
2. **Per-organ-system clinical validation.** Per-system `.xlsx` validation tables in `data/human/adult/validation/Scenarios/` (Cardiovascular, Respiratory, Pharmacokinetic, …) plus `PatientValidationData.xlsx`. Each row is a published reference value with citation, the Pulse output, and a comparison type (`SEValidationTarget`: `EqualToValue`, `Range`, `GreaterThan`, `TrendsTo`).
3. **Scenario / patient regression.** `data/config/ScenarioVerification.config` runs the validation scenario JSONs (Patient-Validation, StandardMale, StandardFemale, ~30 CSTARS patients) with a 2 % percent-difference tolerance vs SHA512-locked baseline CSVs.
4. **Drug PK validation.** 15+ drug PK scenarios under `data/human/adult/scenarios/validation/drug_pk/` compared to per-drug reference CSVs.

**Scoring scheme** (`src/python/pulse/cdm/utils/math_utils.py` — `percent_difference` and `generate_percentage_span`): three bins — success ≤ 10 % (green), warning 10–30 % (yellow), danger > 30 % (red). These are the same bins Bray 2019 reports as "good / fair / poor" — the 474-scenario adult-male table (83.7 % / 10.8 % / 5.5 %) uses this exact rubric.

**HTML aggregator.** `src/python/pulse/pipelines/full_html_report.py` merges `CDMUnitTests.html`, `EngineUnitTests.html`, `ScenarioVerification.html`, `DrugPKVerification.html`, `PatientVerification.html`, `PatientValidation.html` into `PulseTestReport.html`. Published at `pulse.kitware.com`.

**Verification ≠ validation in their vocabulary.** Verification = numerical/solver correctness (regression vs locked baselines, BiCG tolerance). Validation = clinical match to literature ranges. Pulse does both at the unit / scenario / patient / drug level. They do **not** propagate input uncertainty or systematically sample the operational envelope — exactly the gap our atlas fills.

### The 2020 sensitivity-analysis study tag (this is the consequential finding)

`gitlab.kitware.com/physiology/engine` carries a tag `STUDY_SENSITIVITY_ANALYSIS_1_0_0` dated 2020-07-20. Code lives at:

- `src/cpp/study/sensitivity_analysis/` — `SARunner.cpp` (56 KB), `main.cpp`, `ReadMe.md`, `CMakeLists.txt`.
- `src/python/pulse/study/sensitivity_analysis/` — `analysis.py` (16 KB), `analysis_utils.py` (8 KB), `ml_surrogate.py` (24 KB), `engine.py`, `utils.py`.

`ReadMe.md` says verbatim:

> "The work performed here focuses specifically on the coupled cardiovascular-respiratory systems. The systems in Pulse are represented with lumped parameter models, consisting of discrete circuit elements analogous to an electrical circuit. The values of these circuit elements influence simulation results, but these values cannot be measured clinically. **This study uses sensitivity analysis as a path towards improved lumped parameter optimization.**"

`analysis.py` (top of file) confirms the parameter set: it computes Sobol indices (`S1`, `ST`) over **internal vascular-circuit resistance multipliers** — names like `Aorta1ToBrain1`, `Aorta1ToFat1`, `Bone1ToBone2`, `AbdominalCavity1ToGround`, etc. These are model-calibration parameters that override the engine's learned values during the simulation, **not** user-facing operational inputs (HR, SBP, DBP, RR, Vt, FiO2, PEEP).

`git log` on the directory shows the last functional commit on the analysis code itself was 2020-08-24 (`Update controller accessibility`). Everything since (5 commits between 2021 and 2025) is build-system: namespace cleanup, protobuf updates, library reorganization, web-WASM build support. **The 2020 SA study has not been re-run for Pulse 4.3.x.**

Multiplex-ventilation has the same pattern: `STUDY_MULTIPLEX_VENTILATION_1_0_0` tag (2020-04-28) tied to Webb et al. 2020 (PMID 33237927), one-off study, no re-run.

### Implication for the paper's framing

The literal FAQ statement remains **factually correct**: there is no formal sensitivity analysis or uncertainty quantification on the engine **as currently shipped**. The 2020 study tag is a separate one-off published study on internal-circuit-element model calibration (not part of the regular release V&V), and it has not been ported to 4.3.x. So the FAQ does not contradict its existence.

However, our project's framing — *"Pulse has never had a sensitivity analysis"* — is **overstated**. The defensible statement is sharper and actually stronger:

> Kitware released a one-off Sobol study (2020) on internal circuit-element values for parameter optimization (`STUDY_SENSITIVITY_ANALYSIS_1_0_0`). That study addressed model-calibration parameters, not user-facing operational inputs. No systematic sensitivity analysis on operational inputs (HR, BP, RR, Vt, FiO2, PEEP) has been published, and the Pulse FAQ continues to state that no formal SA exists for the engine as currently shipped. Our atlas is the first such operational-input atlas.

This sharpened framing does not weaken the paper. It strengthens it: an opponent who would have flagged the 2020 study tag in peer review now has nothing to point to.

## Interpretation

1. **Version pin is safe.** Keep `pulse-pediatric-engine:latest` (built from 4.3.1) as the atlas Docker image. Add a footnote in §6 (Pulse references) noting that 4.3.2 is a build-system patch with no physiology change. Do not spend compute on a 4.3.2 re-sweep.
2. **The premise survives, sharpened.** Rewrite limitation #1 across CLAUDE.md, README, `reference/pulse_limitations_verified.md`, `reference/pulse_engine_summary.md`, and the manuscript intro to capture the operational-vs-internal-circuit distinction explicitly. Add a citation entry for the 2020 study tag in §6 of the manuscript.
3. **Frame our work as timely, not duplicative.** `feature/ventilator_investigation` (Apr 2026) shows Kitware is also currently examining ventilator behaviour — our F-004 findings on VC-AC steady-state failure are concurrent with their own investigation, not a contradiction or scoop.
4. **Cite Kitware's V&V layers explicitly in §6.** This positions our operational-input atlas as the missing tier, not a substitute for what they already do well (per-system literature comparison, drug PK, scenario regression).

## Next steps

- Edit limitation #1 across `CLAUDE.md`, `README.md`, `reference/pulse_limitations_verified.md`, `reference/pulse_engine_summary.md` (in this commit). Add the operational-vs-internal-circuit distinction.
- Edit `preprint/manuscript.md` §1.1 (FAQ paragraph), §1.2 (limitation #1 bullet), and §6 (add `STUDY_SENSITIVITY_ANALYSIS_1_0_0` reference + 4.3.2 footnote).
- Add a small forward-pointer in S003: "see S016 for the May 2026 nuance."
- Re-fetch the GitLab repo before paper submission to capture any new merges to `integration` or `stable`. If a new `stable` tag lands, re-diff vs 4.3.1 to confirm physiology is still unchanged before claiming our results apply.
- (Optional, post-submission.) Open a Discourse / GitLab issue politely flagging that the FAQ wording could mention the 2020 study tag explicitly to avoid future confusion. Not required for the paper.

## Sources

- Local clone: `C:\Users\santi\projets\Pulse_engine_adults_Gitlab\engine` (HEAD `e8a3649`, fetched 2026-05-07).
- Remote: <https://gitlab.kitware.com/physiology/engine>.
- Pulse FAQ: <https://pulse.kitware.com/_f_a_q.html> (last verified verbatim 2026-04-19, S003).
- Bray et al. 2019: DOI [10.1007/s42399-019-00053-w](https://doi.org/10.1007/s42399-019-00053-w).
- Webb et al. 2020 (multiplex): DOI [10.1371/journal.pone.0242532](https://doi.org/10.1371/journal.pone.0242532), PMID 33237927 — corresponds to `STUDY_MULTIPLEX_VENTILATION_1_0_0`.
- Webb et al. 2023 (ventilator): [PMC10224749](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10224749/).
- `STUDY_SENSITIVITY_ANALYSIS_1_0_0` tag: 2020-07-20, code at `src/cpp/study/sensitivity_analysis/` and `src/python/pulse/study/sensitivity_analysis/` — no associated peer-reviewed publication identified in this audit.

---

**Note (amendement daté, 2026-06-23).** La terminologie « internal vascular-circuit resistance multipliers » employée ci-dessus (notamment au niveau de l'analyse de `analysis.py`) est **historiquement inexacte** sur trois points, vérifiés depuis directement dans la source (ReadMe + `main.cpp` + `analysis.py`) : l'étude 2020 balaie en réalité (i) le circuit **cardiovasculaire ET respiratoire** (pas seulement « vascular »), (ii) des **résistances ET des compliances** (`*ToGround` = compliances en mL/mmHg, p. ex. `Fat1ToGround`), (iii) via des **overrides de valeurs absolues**, pas des multiplicateurs. Formulation correcte retenue dans les documents vivants : « internal lumped-parameter circuit values (cardiovascular and respiratory resistances and compliances) ». Voir `reference/pulse_engine_summary.md` et `reference/pulse_limitations_verified.md`. Le texte original ci-dessus est conservé tel quel (archive datée) ; cet amendement le corrige sans le réécrire.
