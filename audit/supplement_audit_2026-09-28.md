# Supplement audit, part by part — 2026-09-28

**Scope.** `preprint_npj/supplement.tex` in full (1,181 lines, 18 sections,
23 floats), read part by part. For each part: every claim, fact, number,
citation and cross-reference is checked against its ground truth (data
artefacts, code, Pulse source at `REL_4_3_1`, Pulse documentation, primary
literature, preregistration, experiment logs, `paper.tex`). Contradictions
with the rest of the supplement and with `paper.tex` are looked for.

**Rules applied** (project `CLAUDE.md`, autonomy pact):

- mechanical corrections (typos, broken pointers, a literal that drifted from
  its own artefact, harmonising two forms of one value) are applied;
- any change to a scientific claim (direction, magnitude, scope, hedging) is
  **not** applied: it is recorded here and brought back for decision;
- a citation MISMATCH or OVERCLAIM is recorded and nothing is modified.

**Baseline before any edit** (HEAD `8804917`):
`audit_claims.py --check-paper-sync --check-monograph` → ledger 394/394,
crosswalk 94/94, monograph 25/25 PASS.

**Prior register.** `audit/supplement_prose_sweep.md` (August 2026, 62
signals, many still marked OPEN). Each open signal is re-checked against the
current text in its own part below, never assumed open or closed from the
register.

Status legend: **OK** verified correct · **FIXED** mechanical correction
applied · **DECIDE** needs the author · **NOTE** true but worth knowing.

---

## Part 0 — header, authors, affiliations, opening paragraph (L1–121)

| # | Claim | Check | Status |
|---|---|---|---|
| 0.1 | Header comment "sections S1-S18" | 18 `\section` in the file | OK |
| 0.2 | Authors and affiliations | exact `diff` of the `\author`/`\affil` lines against `paper.tex` → identical | OK |
| 0.3 | Title | same full title as `paper.tex` | OK |
| 0.4 | "Every quantitative claim in this supplement traces to the same audit ledger" | Not true as stated. `audit/number_inventory.md` §2: 411 supplement numeric occurrences match neither a ledger anchor nor a guard. Witness: the `REL_4_3_2` diff size "7 files / +46 / -17" (§S1) is in no script (grep of `scripts/`, positive control: `REL_4_3_2` itself found 3 times). `paper.tex` §4.7 uses the careful form: "traceable, as applicable, to primary sources, the preregistration, or entries in the open audit ledger". | **DECIDE** (scope of a provenance claim) |
| 0.5 | "both the section number and the explicit phrase 'of the main manuscript' are given" | 49 `\mainref` uses. Deviations: "of the main paper" ×6 (L581, L1154, L1156, L1157, L1160, L1166), "main paper Section" (L581), "the main paper's Section 2 Results" (L1139), "main-manuscript Section 2.6" (L540), and **one bare "the Section 2.5 caveat" with no document named** (L1155). Paper numbering read from `build/paper.aux`. | see Part S16/S17 for the fix |
| 0.6 | Hard-coded paper float numbers (not guarded by `check_render`, which only resolves `\mainref`) | `paper.aux`: Table 1 = terms (cell key), Table 3 = per-cell flags, Figure 2 = traffic light, Figure 3 = Morris heatmaps, Figure 4a = trigger lockout. Every hard-coded use (L193, L397, L407, L442, L446, L554, L627, L745) is checked in its own part. | see parts |

## Part S1 — Pulse engine in context (L127–135)

Cited claims (FAQ 5–10× real time; About bindings and platforms; System 0.02 s
and the two quotes; Circuit solver; Resp 5 compartments and the five severity
nodes; Patient allometric bounds; fork by original BioGears team) were verified
verbatim at `REL_4_3_1` this morning: `audit/reference_audit_2026-09-28.md`,
Pulse documentation table and `bray2019`. Not repeated here.

| # | Claim | Check (2026-09-28) | Status |
|---|---|---|---|
| S1.1 | "heart and respiratory muscles as time-varying pressure sources" | **Wrong for the heart.** `CardiovascularMethodology.md:113` at `REL_4_3_1`: "The heart model generates pressure that drives the hemodynamics through a **variable capacitor** that simulates the changing elastance of the myocardium". Respiratory muscles are a pressure source (`RespiratoryMethodology.md:273`, "a time-dependent pressure source"). Bray 2019 (read, `local_sources/`) says resistors and capacitors only, never "pressure source" for the heart. Same sentence in the monograph (L458–459, attributed to `[@bray2019]`) and in `reference/pulse_engine_summary.md:22` (the likely origin). | **FIXED** in all three: "the heart as a time-varying capacitor [pulsecardiomethod] and the respiratory muscles as a time-varying pressure source". Repo-wide grep after the fix: 0 heart-as-pressure-source left. No atlas result depends on it. |
| S1.2 | "actively maintained" | GitLab API today: commits on `feature/documentation_updates` 2026-09-28, `integration` 2026-09-26, `study/itm` 2026-09-27; `last_activity_at` 2026-09-28. | OK |
| S1.3 | "The current upstream stable head is `REL_4_3_2` (released 2025-08-12)" | `git ls-remote --tags` on gitlab.kitware.com today: last tag `REL_4_3_2` (control: older tags listed). Annotated tag dated 2025-08-12 15:58 −0400; branch `stable` points at its commit. | OK |
| S1.4 | "7 files / +46 / -17 lines: web-WASM dockcross support and a .NET binding tweak; no physiology, validation, patient-setup, or solver code changed" | `git diff --shortstat REL_4_3_1 REL_4_3_2`: 7 files, 46+, 17−. Files: `.gitignore`, `CMakeLists.txt` (version string), `External_Eigen3.cmake`, `dockcross.cmake`, `PulseEngine.cs` (two `double`→`void` P/Invoke signatures), `xcompile.bat`, `xcompile.cmake`. The Eigen change is the archive MD5 only; same URL, Eigen 3.4.0 → solver library unchanged. | OK |
| S1.5 | "Both projects still exist independently" | GitHub API: `BioGearsEngine/core` not archived, last push 2026-01-17. | OK |
| S1.6 | "we did not identify either feature [mechanoreceptor feedback, lung recruitment] in the examined BioGears respiratory or nervous-system implementations or in its respiratory methodology documentation" | Re-measured today on `trunk`: `Respiratory.cpp` (148,907 B), `Nervous.cpp` (81,674 B), `share/doc/methodology/RespiratoryMethodology.md` (151,927 B). `mechanorecept` 0/0/0, `recruit` 0/0/0; controls `ventilat` 107/4/77, `barorecept` 1/55/0, `chemorecept` 2/38/4. Pulse side at `REL_4_3_1`: `mechanorecept` in docs ×2 and 3 source files; `recruit` docs ×8 ("lung recruitment is modeled based on acinar ventilation and volume"). | OK |
| S1.7 | Consistency with `paper.tex` L142, L347 | Same engine description (lumped-parameter, 5-compartment lung, real-time-capable). | OK |

Out of scope, noted: `reference/pulse_engine_summary.md:22` also says "Same
approach as BioGears, HumMod, Muse"; HumMod is not a circuit-analogue model
(signal 62 of the August sweep removed that qualifier from the paper). Internal
note, not a manuscript; left for the pre-public cleaning.

## Part S2 — Verified Pulse 4.3.1 limitations, Table S1, scope limits (L141–197)

All Pulse facts checked at tag `REL_4_3_1` in the local clone
(`Pulse_engine_adults_Gitlab/engine`); data facts on the canonical artefacts
(`data/runs/full_sweep/*/aggregated.parquet`, `morris_sample.parquet`) with
the repository's own pair definition (`src/analysis_morris.derive_trajectory_pairs`);
scripts in the session scratchpad (`s2_checks.py`, `s2_pair_cause.py`,
`s2_spo2_kind.py`).

| # | Claim | Check | Status |
|---|---|---|---|
| S2.1 | Row 1: 2020 tag `STUDY_SENSITIVITY_ANALYSIS_1_0_0`, Sobol on internal cardiovascular and respiratory resistances and compliances, for calibration | Tag dated 2020-07-20. `analysis.py` computes Sobol S1/ST; `engine.py:175–205` collects `Resistance` and `Compliance` paths of the `Cardiovascular` and `Respiratory` circuits; ReadMe: "sensitivity analysis as a path towards improved lumped parameter optimization". | OK |
| S2.2 | Row 2: SBP 90–120, DBP 60–80 rejected with `[ERROR]`; DBP/SBP ≤ 0.75 | `SetupPatient.cpp` L346–351 constants, L493–524 `patient.Error` + `err = true` for each bound and for `diastolic > 0.75·systolic`. | OK |
| S2.3 | Row 3: age ≥ 18 hard-gated | `ageMin_yr = 18.0`, `Error` below it (L42, L52–57). (Pulse also rejects age > 65; not claimed, not needed.) | OK |
| S2.4 | Row 4: band 0.91–0.945, widened to 0.879–0.946 | Same band at all 9 supplement and 2 paper loci; data check deferred to Part S5. | see S5 |
| S2.5 | Rows 5–6: HR 50–110, RR 8–20; "Sampler ranges match" | `SetupPatient.cpp` L276–311 (brady 50 / tachy 110 are the error thresholds), L568–590 (RR 8/20). `src/sampler.py:41–47`: HR 50–110, SBP 90–120, DBP 60–80, RR 8–20. | OK |
| S2.6 | Row 8: "single trachea resistance; there is no anatomically separate nose / pharynx compartment" | **Half wrong.** `SetupCircuitsAndCompartments.cpp`: node `Pharynx` (L2991–2994, 1 mL), paths `AirwayToPharynx` (no element) and `PharynxToCarina` (the only series resistance, `TracheaResistance`, L3066–3068), gas compartment `PulmonaryCompartment::Pharynx` (L3146). No nose anywhere (`nasal` only in the nasal-cannula device). The single-resistance statement is right; the pharynx-compartment statement is not. Same error in `reference/pulse_limitations_verified.md:90` and `CLAUDE.md:139`. | **FIXED** in the supplement ("Upper-airway resistance is a single fixed trachea resistance, between the pharynx and carina compartments; the nose is not modelled", source column now "Pulse circuit source + source audit (monograph S003)"; the file name `SetupCircuitsAndCompartments.cpp` was tried first and overflowed the 3.5 cm column by 25.7 pt, caught by `check_render.py`) and in the reference note. `CLAUDE.md:139` left to the author (instruction file). |
| S2.7 | Row 9: no regional V/Q mismatch | Pulse states it itself: "The model makes no distinction between different generations of bifurcating airways. Therefore, factors affecting the regional ventilation and perfusion of the lungs cannot be captured by the model" (`RespiratoryMethodology.md:1163–1165`). Row cited only "Structural design". | **FIXED** (source added: `\cite{pulserespmethod}`; claim unchanged) |
| S2.8 | Row 10: VC 4.93 L vs about 4.6 L (about 7 %); 4,819 mL (about 5 %) | `RespiratoryMethodology.md:655–656`; Patient methodology Table 4 StandardMale `Patient-VitalCapacity(mL) 4819.2` (live page, `.firecrawl/pulse_patient_method_2026-09-14.md:201`). 4.93/4.6 = +7.2 %; 4.8192/4.6 = +4.8 %. | OK |
| S2.9 | Rows 7, 11, 12 | Verified this morning (`reference_audit_2026-09-28.md`, Pulse documentation table); row 11 already carries both sources. | OK |
| S2.10 | Source-column pointers S003, S005, S016, Appendix B.3 | All present in the monograph (L660, L662, L673, App. B.3). | OK |
| S2.11 | Rows 5–6 re-derivation, 2026-07-26, eight probes, male body | `results/s030b_analysis.csv`: HR 49/111 and RR 7/21 `REJECTED`, exit 1, `csv_written False`; 50/110/8/20 `ACCEPTED`, exit 0, CSV written. `run_s030b_severe_and_bounds.py:46–52` uses `PATIENTS["M"]`. Rejection text "Maximum heart rate baseline allowed is 110 bpm" is in the CSV and in `SetupPatient.cpp:297`. | OK |
| S2.12 | "tested empirically before preregistration locked" (caption L147, text L181, index L1150) for both withdrawn assertions | True for FiO₂ = 1.0 (Docker probe). **Not** for the sex assertion: S003 records "Checked the Pulse docs"; nothing in `preregistration.md`; wording added 2026-05-31 (`56fb94d`). | **FIXED** at the 3 loci: "were checked … and could not be confirmed". The FiO₂ half still says "empirical Docker probing". |
| S2.13 | Blood-volume baseline from weight alone; Roza–Shizgal revision, not the 1919 originals | `SetupPatient.cpp:534` `65.6 * pow(weight_kg, 1.02)`, no sex term. L771/774: male `88.632 + 13.397W + 4.799H − 5.677A`, female `447.593 + 9.247W + 3.098H − 4.330A`. Roza & Shizgal 1984 (read, `local_sources/`), Eq. 3: **88.362** + 4.799H + 13.397W − 5.677A; Eq. 6 identical to the female code; Harris–Benedict 1919 constants (66.473 / 655.096 …) differ. The male intercept transposition is already disclosed at supplement L867 (§S10). | OK |
| S2.14 | BMR initialises total metabolic rate and is its set point at rest and normothermia; TMR drives O₂ consumption and CO₂ production | `EnergyModel.cpp:104` (TMR initialised to BMR); L625–630 (36.8–42.5 °C, no exercise: set point = BMR, first-order ramp); `TissueModel::CalculateMetabolicConsumptionAndProduction` converts TMR to an ATP rate, then O₂ and CO₂. | OK |
| S2.15 | (iii) Ward et al.: six settings, pressure-targeted; FiO₂, RR, PEEP swept here | Verified this morning (arXiv:2411.07971v1). | OK |
| S2.16 | (iv) zero clean FiO₂ pairs in S1_M, S1_F, S4_F; causes | Measured: 20 FiO₂ pairs per cell, both-clean 0/0/0 (others: S2_M 8, S2_F 7, S3_M 18, S3_F 16, S4_M 1). Every lost pair has an endpoint flagged on SpO₂ or PaO₂ (20/20 in each of the three cells). S1: all runs at FiO₂ 0.737 and 1.0 flagged (76/76 in both), SpO₂ reason always "flatline at extreme" → saturation pinning; PaO₂ > 600 on 11 (M) and 23 (F) of them. S4_F: all runs at 0.21 and 0.473 flagged (84/84), `implausible` = SpO₂ < 0.5 and PaO₂ < 20; SpO₂ `not_steady_state` = Δ60 s or CV (a drift). FiO₂ steps join levels 0↔2 or 1↔3 only, so "adding more trajectories cannot recover" is supported by 100 % flagging at the levels every step must touch. | OK. NOTE: for S4_F the supplement says "by severe hypoxemia" where the paper's Figure 3 caption says "severe hypoxemia or a still-drifting SpO₂"; not contradictory, the paper is more precise. |
| S2.17 | (vi) 9 of 20 DBP steps shortened; applied DBP co-varies in 8 of 20 SBP steps | Measured: 9/20 and 8/20; `dbp_applied` identical in all eight cells. SBP rank 1 for MAP: see Part S3 (clip cost). | OK |
| S2.18 | (vi) shunt fraction not recorded | `output.csv` and `output_pulse_native.csv` headers: no shunt column; no `shunt` request in `src/`. | OK |
| S2.19 | Consistency with `paper.tex:337` | Same six limits, same numbers (9 of 20), same two evidence caveats. | OK |

Noted, outside the supplement: `experiments_log/santino/S003_pulse_limitations_verified.md`
dates v4.3.1 to "Sept 2024"; the `REL_4_3_1` merge commit is dated
2025-01-24 (Sept 2024 is `REL_4_3_0`, 2024-09-10). No public document dates
4.3.1, so nothing to correct outside the log.

## Part S3 — Parameter provenance and supplementary analyses (L203–434)

Status at the end of 2026-09-28: audited in full; every check, instrument and
result is listed in the message of commit `a1d21e9` (fixes: "3,349" logs,
"the only amendment to a locked threshold", misplaced `%% S4` comment; a
signal on "any drift … is caught" withdrawn after finding the crosswalk rows in
`preprint_npj/paper_to_monograph_map.md`). Copied from that message on
2026-10-13 (the table was not re-measured today):

| # | Claim | Check (2026-09-28) | Status |
|---|---|---|---|
| S3.1 | "3,348 Pulse logs on disk" (paper L369, §S3.3, monograph L1211) | 3,349 under `data/`; the extra one is `data/clamp_probe/pulse.log`, the only log at depth 3, dated before the sentence was written. Replay of both pattern sets over all 3,349 still flips exactly one run (`s030b_bound_hr49`) | **FIXED** → 3,349 (three documents) |
| S3.2 | "the only preregistration amendment (2026-04-22-b …)" (§S3.10, monograph L1251) | `preregistration.md` has several (2026-04-22 rescope, 2026-04-22-b, 2026-05-21 documentation, errata, 2026-08-04 post hoc record); the claim meant thresholds | **FIXED** → "the only amendment to a locked threshold" (supplement + monograph) |
| S3.3 | `scripts/s019_sobol_bolton.py` docstring called the withdrawn 11,008-run figure "the figure the manuscript quotes" | §S3 Sobol and `sobol_ci_buckets.json` give 6,144 / 3,584 (8 cells, k = 3–6) | **FIXED** (docstring) |
| S3.4 | Misplaced `%% S4` comment block inside S3 | source comment only | **FIXED** (removed) |
| S3.5 | Hard bounds and drift thresholds | code, preregistration and crosswalk agree | OK |
| S3.6 | CV and flatline constants; clamp calibration and replay | `src/detector.py` constants; replay as in S3.1 | OK |
| S3.7 | FiO₂ cap 0.9996 | `Data.xlsx` ambient CO₂ 0.0004; 208 / 195 / 13 | OK |
| S3.8 | Input instantiation, 10,160 contracts | re-run | OK |
| S3.9 | CDC rows, BMI, blood volume, sampler constants | re-derived | OK |
| S3.10 | All of §S3.7 (clip cost) | `s032` scripts re-run; max factor 15.4 recomputed independently | OK |
| S3.11 | Sobol costs and the stable set | 23 at 500 / 1,000 / 2,000 / 4,000 resamples, re-measured | OK |
| S3.12 | §S3.9–§S3.13 | via their own scripts | OK |

Consequence noted after the rebuild: citing `pulsecardiomethod` in §S1 makes it
reference [2] of the supplement, so the supplement's reference numbers shift
(automatic, BibTeX). The paper's numbering is unchanged.


---

**Resumed 2026-10-13** at `54aa84a` (supplement 1,209 lines; re-freeze 58 =
the version to submit). Any change to the supplement from here on means a
re-freeze 59. Line numbers below are those of `54aa84a`.

## Part S4 — Extended Table 3: not_steady_state attribution (L451–480)

Instrument: an independent recompute from the per-channel statistics of
`data/runs/full_sweep/aggregated.parquet` (`*_mean`, `*_std`, `*_cv`,
`*_delta_60s`, `*_bound_lo/hi`), re-implementing the locked rule of
`src/detector.py::check_not_steady_state` rather than parsing the reason strings
that `scripts/nss_decomposition_table.py` parses. Positive control: the locked
`not_steady_state` flag is reproduced on 1,280 / 1,280 runs (530 / 530).
Script kept in the session scratchpad (`s4_recompute.py`); method as stated here.

| # | Claim | Check | Status |
|---|---|---|---|
| S4.1 | "Table 3 of the main manuscript" (title, L453); "Cell-label key: Table 1" | `build/paper.aux`: `tab:flag_summary` = 3, `tab:terms` = 1. Signal 5 of the August sweep (§S4 pointing to Table 1) no longer applies here | OK |
| S4.2 | Three sub-modes, pointer to §S3 (priority order) | §S3 "priority order" lists flatline, CV > 0.05 and drift (Table S-drift); `detector.py` L334–364 | OK |
| S4.3 | 530 `not_steady_state` runs; columns n_nss, excl. SpO₂ sat., excl. Vt CV, excl. both | Recompute matches every cell and the totals (530 / 454 / 360 / 185) | OK |
| S4.4 | Column "n_clean (excl. both)" and the text "Excluding both sub-modes raises the implied clean count from 663 / 1,280 (51.8 %) to 1,008 / 1,280 (78.8 %)" | **Wrong.** `nss_decomposition_table.py` L129 computes `n_clean + (n_nss − n_excl_both)`, which adds back every run that loses its `not_steady_state` flag, **including runs that are also `implausible`** (59 `not_steady_state` runs carry another flag). Such a run is never clean. Counting runs with no `clamped`, `diverged` or `implausible` flag and no remaining trigger: Healthy-M **119** (not 127), Healthy-F **122** (not 136), Severe-M **67** (not 72), Severe-F **67** (not 82), the four others unchanged; total **966 / 1,280 (75.5 %)**, not 1,008 (78.8 %). The 42 runs added back wrongly, measured: Healthy-M 8 and Healthy-F 14, all `implausible` on PaO₂ > 600 (the 34 Healthy `implausible` runs of Table 3 are all PaO₂ > 600, paper §2.4), with SpO₂ saturation as `not_steady_state` trigger (12 alone, 10 with Vt CV); Severe-M 5 and Severe-F 15, all `implausible` on SpO₂ < 0.5 and PaO₂ < 20, with Vt CV as the only trigger. The ledger (`T2.nssC.*`, `T2.nss.total.clean_excl_both`, `T2.nss.counterfactual`) passes because it compares the text with the CSV that the same formula wrote. Same figures in the monograph (Appendix C table L4674, L3481, L4717) | **DECIDE** (number change → re-freeze 59) |
| S4.5 | "The two 'excl.' columns count residual not_steady_state runs after removing each sub-mode from the trigger criterion" | **Two readings.** The detector records at most one sub-mode per channel: once flatline or CV fires on a channel, its later checks are skipped (`continue`). The script counts runs that keep **another recorded** trigger (reading A). A classifier **without** the sub-mode would test the skipped checks: then Vt drift fires on 62 more runs (excl. Vt CV 422, not 360; excl. both 287, not 185; clean 878 / 1,280, 68.6 %) (reading B). Those 62 are the same oscillation seen through the drift check, so A is the more meaningful decomposition, but the caption's wording describes B | **DECIDE** (wording of what is counted) |
| S4.6 | "76 runs" (SpO₂ saturation), "530 minus 360 = 170 runs" (Vt CV) | 530 − 454 = 76; 530 − 360 = 170; under reading A these are the runs whose only recorded trigger is that sub-mode | OK |
| S4.7 | "the locked flatline rule (std/\|mean\| < 0.01 and mean within 0.001 of a hard bound)" | Code: `abs(mean − bound) <= 0.001 × max(\|bound\|, 1)`, i.e. 0.001 absolute for SpO₂ (a fraction) and 0.1 % relative for bounds ≥ 1. Exact for the SpO₂ ceiling the sentence is about; the paper's "within 0.1 % of a hard bound" is exact for every bound except the SpO₂ floor (0.5, tolerance 0.2 %) | NOTE |
| S4.8 | "corrected there by setting the inspiration trigger pressure explicitly" | §2.3 calls the lock "a data-generation lever, not a clinical recommendation"; 78.1 % of reruns fall below 0.05, not all. Same word family as the letter's "fixes", changed to "adjustments" in `5fe2378`; the Figure 4 title keeps "corrections" | **DECIDE** (low; wording) |
| S4.9 | Paper §2.1: "In the Healthy cells, the low four-flag retention mostly reflects the tidal-volume oscillation of §2.3 and SpO₂ pinned at saturation (Supplement §S4)" | Re-checked with the corrected count: 150 of the 229 non-clean Healthy runs (65.5 %) become clean when both sub-modes are excluded (reading A); 119 (52.0 %) under reading B, where the extra residual is the oscillation seen through Vt drift. "Mostly" holds | OK, paper unaffected |
| S4.10 | Paper §2.3 "It is the primary flag on 20.6 % of runs"; §2.2 "139 of 320" (Healthy) and "36 of 320" (Moderate) | 264 runs have `not_steady_state` as primary flag with Vt CV > 0.05 (264 / 1,280 = 20.625 %); Vt CV > 0.05 on 139 / 320 and 36 / 320 | OK |

## Part S5 — ARDS impairment-fraction instability zone (L486–600)

Sources opened today: `results/s030_pf_by_arm.csv`, `results/s030_published_value_provenance.csv`,
`results/s030_run_index.csv` (40 runs), `results/pf_berlin_by_scenario.csv` (regenerated by its
script: identical), `results/continuous_ards_severity_sweep.parquet`, the sweep aggregate; Pulse at
`REL_4_3_1` / `REL_4_3_2` (local clone); companion `Pulse_translation_new` (read-only):
`experiments_log.md` L586–690 (March), L1905–1985 (E10), L2309–2330 (E6),
`data/engine_runs/e6_ards_calibration/results.json`, `pipeline/tests/test_e4_e6.py`; Kitware
Discourse search API.

| # | Claim | Check | Status |
|---|---|---|---|
| S5.1 | March calibration: 28 runs, male 67.3 kg / 180 cm, VC-AC, Vt 403.8 mL (6 mL/kg), PEEP 10, FiO₂ 0.4; 0.26 / 0.60 / 0.95 → 256 / 150 / 96; full log in monograph App. B.3 | Companion log L586–690: 9 + 11 + 8 = 28 runs; P/F 256.0 / 150.1 / 96.1; 0.92 and 0.94 failed; 6 × 67.3 = 403.8. Monograph §B.3 (L4379) carries the 28-run log | OK |
| S5.2 | E6 (2026-04), same settings, 252 / 148 / 75 | `results.json`: timestamp 2026-04-15, ventilation identical; reproducibility rows 251.9 / 148.2 / 74.8 | OK |
| S5.3 | "the March log records 5-minute runs after a 120-s settle without stating its averaging window"; E6 "a 60-s settle, then a 108-s recording; … its last five 10-s samples" | Companion log L612 ("5 min per run, 120s settle time, 10s sampling", no window); `test_e4_e6.py` L61–63 (settle 60 s, 0.03 h "108s", sampling 10 s) and L143–144 (`time_points[-5:]`) | OK |
| S5.4 | Replication: 40 runs 2026-07-26; [108, 168] s; 256.5 / 150.5 / 96.6; "within 0.6 %" at the three fractions; "within 2 %" across five | 40 rows in the run index. Calibration window: 256.537 / 150.458 / 96.598. Against the unrounded March values (256.0 / 150.1 / 96.1): +0.21 / +0.24 / +0.52 %; five fractions (with 199.3 and 118.7): max +1.91 % (0.9). Signal 7 of the August sweep (96.6 against 96 = 0.625 %) used the **rounded** 96: closed. A reader doing the same sum on the displayed 96 gets 0.625 % | OK; NOTE (rounding visible to readers) |
| S5.5 | Band re-derived in the replication: 0.910–0.945 failed, 0.900 and 0.950 completed | `s030_pf_by_arm.csv`: 0.91, 0.92, 0.93, 0.94, 0.945 FAILED in both arms; 0.90 and 0.95 ok | OK |
| S5.6 | Table caption: Pulse's documented {0.3, 0.6, 0.9} give 199 / 150 / 119 | `RespiratoryMethodology.md` L1402 (REL_4_3_1): "mild, moderate, and severe symptoms at severities of 0.3, 0.6, and 0.9"; March 199.3 / 150.1 / 118.7 | OK |
| S5.7 | Table S5 sweep-wide P/F (n, medians, IQR, strata, bands) and the reading text | Script re-run, CSV identical (n = 458 = 61 + 114 + 192 + 91); every cell matches after rounding; the mid-FiO₂ stratum recovers mild / moderate / severe (282 / 163 / 99) | OK |
| S5.8 | 0.95 protocol dependence: 87.3 / 96.6 / 112.6; alveolar PO₂ 231.3 → 230.7; A–a 196.4 → 185.7; RR 30.6 vs set 16; Vt 418 vs 403.8; PaCO₂ 43.6; lock: RR 20.0, PaCO₂ 50.8, P/F 91.5; A–a 185.7 vs 185.1; [60, 120]: 87.3 and 69.4 | All match `s030_pf_by_arm.csv` and `s030_published_value_provenance.csv`; set rate 16 in `run_s030_ards_berlin_recalibration.py` L71. "entirely the alveolar gas equation": PaO₂ differs by 8.46 mmHg, alveolar PO₂ by 9.01, A–a by 0.55 | OK |
| S5.9 | Mapping table (12 multipliers) and text (MIN with recruitment, left/right factor, non-monotonic shunt, driver pressure, volumes, I:E) | `RespiratoryModel.cpp` at REL_4_3_1: resistance nodes 1/10/15/20/25 → 8.8 / 15 / 22.5 on the alveoli resistance path; compliance 1/0.65/0.55/0.5/0.4 → 0.70 / 0.55 / 0.45; diffusion 1/0.5/0.2/0.1/0.05 → 0.57 / 0.20 / 0.075; shunt damage 1/0.1/0.2/0.15/0.1 → 0.22 / 0.20 / 0.125, `MIN` with a recruitment curve of alveolar volume, left/right factors 0.6 / 1.8; ARDS also enters `UpdateVolumes`, `UpdateInspiratoryExpiratoryRatio`, `UpdateDriverPressure`. The atlas sets both lungs to the scenario fraction (`src/scenario.py` L190–193) | OK |
| S5.10 | "each calibrated on the adult standard patient" | Pulse: parameters "tuned to meet validation data", on "the standard patient model of the engine (77 kg adult male)" (`RespiratoryMethodology.md` L423, L441); no line says so of the disease curves specifically | NOTE (supported in substance) |
| S5.11 | "which is one reason why Pulse hard-gates age ≥ 18" | Pulse's own reason: "We do not model pediatrics" (`SetupPatient.cpp` age gate) and "No pediatric or geriatric modeling" (`PatientMethodology.md` L50). Kept on purpose by `dad75bd` (the facts on Pulse stay) | OK |
| S5.12 | Surfactant absent: search of the whole tree at REL_4_3_2 (`e8a3649`) for surfactant, surface tension, Laplace, derecruitment, alveolar stability, opening/closing pressure; forum and methodology silent; P–V hysteresis and PEEP-calibrated recruitment | `git grep -i` at REL_4_3_2 (`e8a36497b`): 0 for every term except "laplace" ×2, both in a bundled binary (`src/java/jar/commons-math3-3.6.1.jar`, a maths library); control "recruit" 86. Discourse search API: "surfactant" 0 results, control "ARDS severity" 5 topics. Hysteresis: `RespiratoryMethodology.md` L855; recruitment "calibrated using empirical data … with varying levels of positive end-expiratory pressure" L993 | OK; NOTE ("no occurrence" holds for source and documentation, not for one third-party binary) |
| S5.13 | "Three convergent boundary probes … (same Pulse v4.3.1 engine and male reference body, **non-overlapping** impairment-fraction grids, independent runs)" | **Wrong.** The grids overlap: March high end 0.90, 0.92, 0.94, 0.95–0.99; E10 0.90, then 0.91–0.95 by 0.005; E6 0.93–0.97 by 0.005. 0.94 and 0.95 are in all three; 0.90 in March and E10. Same wording in the monograph (L4473), since `df821f3` (2026-05-26). The counts are right: E10 10 runs, 8 consecutive failures 0.91–0.945, 0.90 and 0.95 pass (companion L1959–1968); E6 9 runs, 4 fail at 0.93–0.945, 5 pass at 0.95–0.97 (L2309–2322) | **DECIDE** (e.g. "different impairment-fraction grids") |
| S5.14 | "published Pulse validation work and HowTo examples sample severities **up to 0.9 at most** (in `ARDSExacerbation.json` and `HowTo-IsoShuntAnalysis.cpp`) and do not examine impairment fractions within 0.91–0.945" | Both named files stop at 0.9 (0.3 / 0.6 / 0.9; {0.0, 0.3, 0.6, 0.9}). **But** `src/csharp/howto/HowTo_EngineUse.cs` L136–137 (REL_4_3_1 and REL_4_3_2) sets ARDS severity **1.0** on both lungs, in active code. Scan of the 39 files that mention ARDS: no severity inside 0.91–0.945. The "do not examine 0.91–0.945" half holds; the "up to 0.9 at most" half is false for the HowTo examples taken together. Same sentence in the cover letter (L74–76) | **DECIDE** (scope "at most 0.9" to the two files, or drop it and keep the band half) |
| S5.15 | Continuous sweep: 200 runs (100 + 100, same values), midrange inputs, seed 2026, strata 50 / 30 / 20; Table S5-cont; band [0.879, 0.946] = smallest 3-decimal interval; widening 0.031 / 0.001; 0.9458; Wilson [0.09, 0.91] and [0, 0.66]; 0 / 50 per sex below 0.85 | All recomputed on the configured `ards_severity` (not the truncated label): every cell of the table, totals 19 / 14, diverged min 0.87977 and max 0.94585, 0 diverged outside the band, Wilson 0.0945–0.9055 and 0–0.658; `continuous_ards_sweep.py` L63–66 | OK |
| S5.16 | Two regimes: input-driven at low HR, low SBP, high RR, requested FiO₂ 1.0; male only (20, and 0 of 640 female) | Diverged inputs: HR 50 in 16 / 20, SBP 90 in 16, RR 20 in 16, FiO₂ 1.0 in 13 (0.7367 in 7); 8 distinct vectors; 20 male, 0 / 640 female | OK |
| S5.17 | Cross-references §2.6, §2.5, §2.1, §4.3; consistency with the paper (band, regimes, "first systematic characterisation") | Paper §4.3 "documented at design time … widened to [0.879, 0.946]", §2.5 lower / upper part of the band, Discussion priority claim: same wording | OK |

## Part S6 — Sex-stratified comparisons (L606–654)

| # | Claim | Check | Status |
|---|---|---|---|
| S6.1 | Table S6: 12 ρ values and 95 % CIs; "seven entries per cell"; 2,000 paired-input resamples; text "0.75–1.00", Mild Vt lower bound −0.06 | Table = `results/spearman_mu_star.csv` cell by cell. ρ recomputed independently from `results/morris_indices.parquet` (scipy `spearmanr` on the 7 shared inputs): identical to 4 decimals for all 12. Bootstrap: `src/analysis_compare.py` L94–128 (`n_bootstrap = 2000`, resampling the input axis, paired) | OK |
| S6.2 | "the two Healthy cells and the Severe-F cell have no clean FiO₂ elementary-effect pairs: every Morris step that moves FiO₂ … has at least one endpoint flagged by SpO₂-saturation pinning, transient-hyperoxia drift or implausibility" | First half true: 0 / 20 clean FiO₂ pairs in Healthy-M, Healthy-F, Severe-F. Second half, pair by pair with the repository's pair definition (`derive_trajectory_pairs`): true for 20 / 20 pairs in each Healthy cell; **in Severe-F only 12 / 20**. The other **8** are lost only because the FiO₂ = 0.473 endpoint has a still-rising SpO₂ (mean 0.79–0.87, Δ60 s +0.028 to +0.063 against the 0.02 threshold), while the FiO₂ = 1.0 endpoint is clean (7 pairs) or flagged on Vt CV only (1). §S2 (iv) (L195) already says it right: "in Severe-F, low-FiO₂ runs flagged implausible or not_steady_state by severe hypoxemia or a still-drifting SpO₂" | **DECIDE** (align §S6.1 on §S2 (iv)) |
| S6.3 | Table caption "(see the Discussion of the main manuscript)" | Discussion scope limit (iv): FiO₂ pairs removed in Healthy-M, Healthy-F, Severe-F; Spearman confined to Mild and Moderate | OK |
| S6.4 | Figure S2 "Reproduced from the companion technical monograph (its Figure 5)"; S1 and S4 rows blank | Monograph L2572: "Figure 5. H4 — Spearman ρ on Morris μ\* rankings …"; S4 blank because Severe-F lacks FiO₂ | OK |
| S6.5 | Dose: 4.5–11.9 and 5.3–14.2 mL kg⁻¹; +19.8 %; Devine 50.0 / 45.5 + 2.3 (in − 60); 74.99 and 55.10 kg; 4.0–10.7 and 5.4–14.5; +36.1 % | `SetupPatient.cpp` L139, L144 (REL_4_3_1): the two Devine relations, set at setup. 300 / 67.3 = 4.46, 800 / 67.3 = 11.89; 300 / 56.2 = 5.34, 800 / 56.2 = 14.23; 67.3 / 56.2 = 1.1975. 180 cm = 70.866 in → 74.992; 163 cm = 64.173 in → 55.098; 300 / 74.99 = 4.00, 800 / 74.99 = 10.67; 300 / 55.10 = 5.44, 800 / 55.10 = 14.52; 74.992 / 55.098 = 1.3611 | OK |
| S6.6 | "PaCO₂ … accounts for three of the five surviving Wasserstein distances" | Paper §2.5: PaCO₂ in Healthy, Mild and Moderate among the five BH survivors | OK |
| S6.7 | Signal 8 of the August sweep (S2 and S3 called "the moderate-ARDS scenarios") | `grep -i "moderate-ARDS"` on the supplement: 0 (control: "Moderate" present); §S6 now says "Mild and Moderate" | closed |

## Part S7 — Cornish et al. 2026 per-channel cross-mapping (L660–702)

Source opened today: the published version cited by the paper, *JMLR* 27 (2026) 1–52
(`jmlr.org/papers/volume27/24-1752/24-1752.pdf`, 52 pages, downloaded to the session scratchpad;
`pdftotext -raw`). The July verification (`reference_audit.md`, `cornish2023`) was on arXiv v4.

| # | Claim | Check | Status |
|---|---|---|---|
| S7.1 | Table S7: 15 channels × Hoeffding and bootstrap counts | JMLR p. 40, Table 4 (Hoeffding) and Table 5 (reverse percentile bootstrap), read row by row in raw order: all 30 counts and all 15 denominators match | OK |
| S7.2 | Totals 85 and 281; 80 on the eight non-assessed channels; 2 on SysBP; 3 on the four overlapping channels, all PaCO₂ | 24 + 21 + 13 + 5 + 5 + 2 + 0 + 10 = 80; SysBP 2; HR 0, MeanBP 0, PaCO₂ 3, PaO₂ 0; DiaBP 0, RR 0 → 85. Bootstrap column sums to 281 | OK |
| S7.3 | "Holm–Bonferroni adjustment", family-wise error rate; bootstrap "at the same significance level" | JMLR §6.2: "Holm-Bonferroni method … family-wise error rate of 0.05"; bootstrap results "similar if less conservative" with all other aspects kept (§6.2, App. I.7) | OK |
| S7.4 | Prose "Cornish's Table 4 … their Appendix Table 5"; caption "Cornish Appendix Tables 4 and 5" (signal 10 of the August sweep) | In JMLR both tables are in Appendix I (p. 40); the main text says "Table 4 in the Appendix". The caption is right; the prose omits "Appendix" for Table 4 only | **MECH** (prose → "Cornish's Appendix Table 4"; no claim changes) |
| S7.5 | Paper Discussion sentence summarised: "80 of their 85 Hoeffding rejections fall on channels the atlas does not assess" (signal 9 of the August sweep: a quotation that did not exist) | No quotation marks any more; paper L318 says the same (80 / 2 / 3) | OK; signal 9 closed |
| S7.6 | Indexing "(time step, action sequence, sex–age–quantile bin)" | JMLR §6.1 and App. I.5: hypotheses indexed by (t, f, a₁:t, B₀:t), each Bt one of 16 bins: 2 sex × 4 age quartiles × 2 (quantity above / below its median) | OK |

## Part S8 — VC-AC trigger lockout (L709–768)

Sources: `data/runs/s014_trigger_lockout/` (`paired_comparison.parquet`, `summary.json`),
`results/s033/` (`s033_summary.json`, `sweep_confusion.json`, `sweep_cycle_vt_cv.csv`),
`scripts/s033_cycle_resolved_vtcv.py`, the native trace
`data/runs/full_sweep/S4_F/S4_F_0003/output_pulse_native.csv` (untracked, on disk), Pulse at
REL_4_3_1, Europe PMC, Crossref, nature.com (scraped).

| # | Claim | Check | Status |
|---|---|---|---|
| S8.1 | Median Vt CV 0.351 → 0.016 over 64 paired reruns; 78.1 % below 0.05 | 0.3509 → 0.0156; 50 / 64 = 78.125 % (`paired_comparison.parquet`, `summary.json`) | OK |
| S8.2 | Seven of eight cells, none from Moderate-M; Healthy 26, Mild 19 | Healthy-F 20 + Healthy-M 6 = 26; Mild-F 9 + Mild-M 10 = 19; Moderate-F 5, Severe-F 13, Severe-M 1; no Moderate-M. Signal 11 of the August sweep ("all eight") closed | OK |
| S8.3 | Top pre-lock CV 1.826 shared by S1_F_0117 and S1_F_0118, locked to 0.018 and 0.024 | 1.825742 for both; 0.017750 and 0.024182 | OK |
| S8.4 | Figure S4: S4_F_0003 is the configuration closest to the median pre-lock CV, ties broken on case identifier; CV 0.351 → 0.005; "holds near 640 mL", collapsed and oversized cycles | The median of 64 is the mean of S4_F_0003 (0.350839) and S4_F_0089 (0.350895): an exact tie, broken by identifier. Locked CV 0.005442. Native trace over [180, 240] s (= recording [60, 120] s, offset 120 s from `s033_summary.json`): 3,000 samples at 0.02 s, median 640.1 mL, min 136.3, max 1,177.4 (set Vt 633.3 mL) | OK |
| S8.5 | Native output every 0.02 s (50 Hz); 200-fold oversampling of 0.25 Hz; Nyquist 0.5 Hz | 0.02 s step measured on the trace; S033 records 50.0 Hz min and max over all runs; 50 / 0.25 = 200 | OK |
| S8.6 | "Pulse exposes airway pressure and inspiratory and expiratory flow as queryable properties, but the atlas data request did not include them" | `SEMechanicalVentilator.h` (REL_4_3_1) L33, L60, L80: `GetAirwayPressure`, `GetExpiratoryFlow`, `GetInspiratoryFlow`; the native CSV header has no pressure or flow column. Signal 12 of the August sweep closed | OK |
| S8.7 | Cycle-resolved: 1,239 / 1,260 (98.3 %); 297 / 942 / 15 / 6; 10 below a factor of 3, 5 substantial (4.0 to 113.9), all female; 9 constant-volume runs; 6 of 15 already flagged; 3 of 6 lose their flag; 530 → 536 (+1.1 %) | All in `sweep_confusion.json` (factors 4.028 … 113.934; substantial sex F 5; 530 + 9 − 3 = 536; 1.132 %) | OK |
| S8.8 | 64 pairs decrease at both resolutions; 63 in the summaries; Table S8 (eight values); gap 0.6 % to 8.6 %; two summaries each way | `s033_summary.json`: n_decrease 64 / 64; n_pairs_in_estimands 63; 21.42 / 22.66, 27.84 / 25.63, 0.3345 / 0.3224, 0.3256 / 0.3275; gaps 0.59–8.65 %; `cycle_overstates` true on two, false on two | OK |
| S8.9 | "Configuration S1_F_0016 is excluded from the **ratio summaries only** … the run remains in every summary where its CV is defined" | **Contradicted three times**: by the sentence before ("Four descriptive summaries were computed on the 63 configurations"), by the Table S8 caption ("Computed on the same 63 paired configurations (of 64)"), and by the code (`s033_cycle_resolved_vtcv.py` L663–666: "the ratio and difference summaries are computed on the same subset so the four rows are comparable"). It is excluded from all four summaries; it stays in the 64-pair counts and medians (0.351, 0.016, 78.1 %, "every pair"). 819.027985 mL matches | **MECH** (the text drifted from its own artefact) |
| S8.10 | Cycle count vs reported RR on 1,251 non-constant runs: median 5.4 %, 95th percentile 38 %, max 95 %; 126 runs above 20 %, 4 cycle-only crossings, none 5-second-only | 0.0538 / 0.3823 / 0.9487 on 1,251; 126; the 4 verdict-split runs (S1_F_0074, S1_F_0077, S2_F_0110, S3_F_0118) all have `flag_5s` False and `flag_cycle` True | OK |
| S8.11 | All-sample estimator: 1,250 runs differ by more than 10⁻⁶ (the other ten, nine constant); larger on 640, smaller on 610; median ratio 1.0005; 295 / 945 / 12 / 8 (98.4 %); 9 disagreements with the change-point estimator; 530 → 533 | `sweep_confusion.json` `merging_bias_direction` and `sensitivity_native_all`: all match | OK |
| S8.12 | "(SEMechanicalVentilatorVolumeControl.cpp, lines 120–128 of the upstream Pulse source)": the respiratory-model trigger is on when neither trigger flow nor pressure is supplied, in AssistedControl | REL_4_3_1 L120 `SetInspirationPatientTriggerRespiratoryModel(eSwitch::Off)`, L121 AssistedControl test, L127–128 switched On when neither is supplied | OK |
| S8.13 | "reduces the Vt CV about twentyfold in the median paired comparison" (signal 13 of the August sweep) | Readings: ratio of group medians 21.42 (63) or 22.45 (64); median of paired ratios 27.84 (5-s) or 25.63 (cycle). "In the median paired comparison" names the paired ratio (27.8), so "about twentyfold" understates; it is conservative under every reading. Only locus in the four documents | **DECIDE** (low; e.g. "more than twentyfold", true under all four) |
| S8.14 | Citations: figueroacasas2016 (lower Vt in volume control → more dyssynchrony), thille2006, blanch2015 (clinically undesirable), akoumianaki2014 (esophageal pressure), sinderby1999 (diaphragm electrical activity) | Re-opened today: Figueroa-Casas 2016 abstract "Lower Vts during VC ventilation result in higher patient-ventilator dyssynchrony"; Blanch 2015 abstract (mortality association, "marker for or a cause"); Akoumianaki 2014 abstract (respiratory muscle effort, masked asynchrony). Sinderby 1999: no abstract available (Crossref metadata; nature.com preview with Figure 3 "Neurally adjusted ventilatory assist" and diaphragm-EMG references); full text read 2026-08 (`reference_audit.md`, not re-read today). Thille 2006 full text re-read 2026-10-12 | OK |
| S8.15 | §S8.4 aligned on §2.3 (re-freeze 58) | Same sentences as paper §2.3: "data-generation … lever, not a clinical recommendation"; "ineffective triggering"; Thille and Blanch | OK |

## Part S9 — Hyperoxia 300-second convergence (L772–816)

Sources: `data/runs/s021_hyperoxia_convergence/` (`plateau_stats.parquet`, `selection.parquet` = the
original 120-s rows, `aggregated.parquet` = the 300-s reruns, `summary.json`, 60 per-run `output.csv`),
`data/runs/full_sweep/` (original CSVs and `aggregated.parquet`), `data/runs/sex_vs_mass/` (S011),
`engine/run_atlas_engine.py`, Pulse `SetupPatient.cpp` at REL_4_3_1. Time indexed on `time_s` rounded
to 0.01 s (61 points, 0–300 s, 37 runs at every point; the ledger's grouping on raw `time_s` gives the
same 61 groups of 37, so T1.06u is sound). Scripts: scratchpad `s9_full.py`, `s9_paco2.py`,
`s9_clean.py`, `s9_runaway120.py`, `s9_s011.py`.

| # | Claim | Check (2026-10-13) | Status |
|---|---|---|---|
| S9.1 | Opening: 40 of 44 (90.9 %) converged; median plateau 643 mmHg over the 40; about 20 mmHg below the sea-level alveolar-gas-equation value ≈ 663 | 40/44; median of the 40 converged plateaus 642.87; 713 × 1.0 − 40/0.8 = 663 (PaCO₂ 40, R 0.8), 663 − 643 = 20 | OK |
| S9.2 | 60 reruns = 22 non-divergent FiO₂ = 1.0 points × 2 Healthy cells + the first four (indices 6, 7, 12, 13) × Moderate and Severe cells | 26 points at FiO₂ 1.0, 22 diverge in no cell; first four in sample order 6, 7, 12, 13; 44 + 16 | OK |
| S9.3 | "byte-identical … over the shared interval t = 0–120 s" | All 60 rerun `output.csv` files start with the original file's 26 lines (header + 25 rows) byte for byte | OK |
| S9.4 | "one rerun spans 420 s of Pulse-internal time" | `VENT_SETTLE_S = 120.0` (`engine/run_atlas_engine.py` L92, advanced at L235) before the 300 s recording | OK |
| S9.5 | Figure S3 caption: median ≈ 530 at t = 0 → ≈ 641 at t = 300; 95 % of the gain at t = 180 s; 37 physiological-converged | 530.2 → 641.1; target 635.5 first reached at t = 180 s and never left; 37 = converged and plateau ≤ 700 | OK |
| S9.6 | "within about 0.1 % of the value at t = 300 s on the median trajectory, and within 1.6 % for any individual run" | Median trajectory: mean(240–300) 640.41 vs 641.08, −0.105 %. Per run, max 1.56 % over the 37 (and over the 40 converged); over all 44 it is 37.9 %, but the paragraph is about the 37 | OK |
| S9.7 | "HR, MAP, Vt and PaCO₂ all settle well within 120 seconds at FiO₂ = 1.0" | **Contradicts paper §2.4 and §S16**, which name delivered Vt, with PaO₂, as the window-sensitive channel. In the 44 Healthy reruns, 13 are flagged for Vt CV > 0.05 in the 120-s runs and 13 in the 300-s reruns (the oscillation of §S8, which a longer window does not remove). PaCO₂ meets its 5 mmHg / 60 s drift threshold in 44/44 within 120 s (max 4.2), but its level keeps rising: mean(240–300) − mean(60–120) = +1.0 mmHg median, IQR +0.3 to +3.2, max 9.7. HR: max change 3.6 bpm; MAP: max 0.2 %. Proposal: "The 120-second window of the locked classifier suits HR, MAP and PaCO₂, whose drift-threshold exceedances are uncommon at FiO₂ ≥ 0.95 (§S16), but is too short for PaO₂ at the inspired-oxygen boundary, …" (Vt left to §S8) | **DECIDE** |
| S9.8 | Runaways: 6/44 (14 %) above 700 mmHg, four near 1,400, all at Vt 633.3 (6 of 20; 0 of 24 elsewhere, 0 of 8 at 800); five at RR 20 (V̇E ≈ 12.7), three others at that V̇E do not run away; sixth RR 16, PEEP 0 (≈ 10.1); 37 / 3 / 3 / 1 | 1408.1, 1408.1, 1402.5, 1368.9, 1126.0, 770.2; S1_M_0130–0132 (662–672) same V̇E without runaway; 633.3 × 20 = 12.67, × 16 = 10.13 L/min | OK |
| S9.9 | "two runs at FiO₂ = 0.737 show the same runaway within the 120-s window (§S3 pao2-sensitivity)" | S1_F_0118 (845 mmHg) and S1_F_0119 (723 mmHg): FiO₂ 0.737, Vt 800, RR 20, PEEP 13.3 — the only two of the 34 > 600 mmHg that stay > 700 | OK |
| S9.10 | §S3 L376 calls those two "the same **high-minute-ventilation** solver instability seen at extended windows (§S9)" | **Contradicts §S9 L791** ("Minute ventilation does not separate them … no input-side ventilation threshold") and the monograph (L159, L2929: "no input-side ventilation setting predicts it"); the S021 runaways are at Vt 633.3 only, 0 of 8 at Vt 800. Not caught in Part S3. Proposal: "(the same solver-instability mode seen at extended windows, §S9-guidance)" | **DECIDE** |
| S9.11 | Female 5 of 5 vs male 1 of 5 runaways (RR ≥ 16 pairs at Vt 633.3); male 770 vs female 1,126–1,408 | As in S9.8 | OK |
| S9.12 | "mean 686 versus 663 mmHg in the locked 120-second window across the four RR = 20 pairs" | Pairs 0130–0133 (`selection.parquet`, original 120-s `PaO2_mean`): female 688.7 / 688.3 / 682.7 / 684.1, mean 686.0; male 657.2 / 665.5 / 669.3 / 658.1, mean 662.6 | OK |
| S9.13 | S011: +13.7 (56.2 kg) vs +21.3 (67.3 kg); Severe 56.2 kg −1.97 (−3.8 %) vs +3.97 % Healthy; 67.3 kg female diverged in Severe; FiO₂ 0.6; 175.5 cm ceiling and model-validity warning; 163 cm = female 50th and male 3rd percentile; 11.1 kg | Final-60-s PaO₂ from the eight `output.csv`: S1 F/M 56.2 kg 358.07 / 344.39 (+13.68, +3.97 %), 67.3 kg 346.66 / 325.36 (+21.30); S4 56.2 kg 50.01 / 51.99 (−1.97, −3.80 %); SVM_S4_F_67.3kg exit 1; all at FiO₂ 0.6. `SetupPatient.cpp` (REL_4_3_1) L70–75: heightMinMale 163.0, heightMaxFemale 175.5, heightStandardFemale 163.0 ("Mins are 3rd percentile, Maxs are 97th percentile, and standard is 50th percentile"); BMI 21.2 and 20.8, within 18.5–25. The 180-cm female's log carries the warning | OK |
| S9.14 | (side note) Pulse's height warnings print the wrong bound: "above 97th percentile(151 cm)" for the 180-cm female | `SetupPatient.cpp` L119 and L124 print `heightMax_cm` in the "below 3rd" branch and `heightMin_cm` in the "above 97th" branch. Upstream message bug, no effect on the run or on our text | NOTE (upstream) |
| S9.15 | "falls monotonically with severity …, by an order of magnitude from the Healthy median to 144 mmHg in Moderate and 73 mmHg in Severe" (signal 16 of the August sweep) | 643.2 / 143.6 = 4.5×; 643.2 / 72.6 = 8.9×. Monotonic: yes. "Order of magnitude" fits Severe at a stretch, not Moderate. Proposal: "nearly ninefold, from the Healthy median to 73 mmHg in Severe (144 mmHg in Moderate)" | **DECIDE** (low) |
| S9.16 | Table S9 | = `summary.json`: 643.2 [592, 668], 143.6 [93, 218], 72.6 [71, 76]; n 44 / 8 / 8 | OK |
| S9.17 | Clean regime: 91 flag-clean Healthy runs, R² = 0.90, 81 ± 11 at 0.21, 214 ± 30 at 0.47, 505·FiO₂ − 25, ≈ 480 at 1.0; clean only at the two lower levels | 91 (49 M, 42 F; 47 at 0.21, 44 at 0.473); OLS 505.5·FiO₂ − 25.1, R² 0.902, 480 at 1.0; 81 ± 11, 214 ± 30; 0 clean of 152 at 0.737 and 1.0 | OK |
| S9.18 | "(the two higher levels are flagged `implausible` or `not_steady_state`)" | 148 of the 152; the other 4 are `diverged` only. Add "or `diverged`" | **MECH** |
| S9.19 | "because hemoglobin saturation and dissolved-oxygen kinetics make the FiO₂ → PaO₂ relation non-linear above FiO₂ ≈ 0.6" (also monograph L2815–2818, stronger: "the *physiologically expected non-linearity* … not an overshoot") | **Unsourced cause, not tested here.** Without venous admixture PAO₂ is linear in FiO₂ (alveolar gas equation); a convex FiO₂ → PaO₂ curve is what a fixed admixture gives through the sigmoid oxyhaemoglobin dissociation curve (an equilibrium effect, not "kinetics"); the admixture of these runs was not measured; "≈ 0.6" has no source; and the comparison mixes the 120-s clean subset with the 300-s plateau of other inputs. Proposal: "…well below the healthy-lung plateau actually reached (Table S9); the relation is therefore not linear over the full FiO₂ range in these simulations, and the cause of this curvature is not analysed here." Monograph to match (keep "not an overshoot", which S021 supports: the plateau stays below 663) | **DECIDE** |
| S9.20 | "about twice the physiological norm of 6–8 L/min" | 12.7 / 6–8 = 1.6–2.1; norm uncited but textbook-standard | NOTE |

## Part S10 — Blood-volume dependence and sex-conditioned setup parameters (L822–886)

Sources: `data/runs/full_sweep/aggregated.parquet`, `data/runs/s018_blood_volume/s018_classified.parquet`
(20 bracket + 20 floor rows) and `s018_floor_classified.parquet`, run configs, Pulse `SetupPatient.cpp`,
`SetupCircuitsAndCompartments.cpp`, `CardiovascularModel.cpp` at REL_4_3_1, the closed register
`audit/pulse_sex_conditioned_parameters.md`, `audit/reference_audit.md` (Nadler). Scripts: scratchpad
`s10_check.py`, `s10_s018.py`.

| # | Claim | Check (2026-10-13) | Status |
|---|---|---|---|
| S10.1 | 20 input-extreme divergences, all male; 13 of them at FiO₂ = 1.0 | 20 diverged of 1,280, all M (S1 4, S2 4, S3 4, S4 8); 13 at FiO₂ 1.0 | OK |
| S10.2 | BV 4,802.63 / 3,996.09 mL; 806.54 (16.8 % of male); floor 4,082.24 (720.39 below male, 86.15 above female); female ceiling 4,595.50 (207.13 below the male default) | All reproduced to 0.01 mL; `SetupPatient.cpp` L534–556: `65.6 * pow(weight_kg, 1.02)`, ×0.85 and ×1.15, both bounds rejected with an error; no sex branch | OK |
| S10.3 | 71.4 vs 71.1 mL/kg, difference 0.3 (≈ 0.4 %); mass gap 16.5 % | 71.36 / 71.10, 0.257 mL/kg (0.36 %); 16.49 % | OK |
| S10.4 | Nadler: 73.0 and 63.8 mL/kg; clinical range 64–79.3, mean 75, women 66 | 72.96 / 63.78 from the sex-specific equations; the range sentence is verbatim Nadler p. 226 (`reference_audit.md`, MATCH, read in the primary scan) | OK |
| S10.5 | 20/20 → 0/20 at 4,400 and 4,082.24 mL | 0 diverged at either level; configs carry `blood_volume_ml` 4400.0 and 4082.24 | OK |
| S10.6 | Rescued runs: 12 of 20 clean at both levels, same 12, identical flag assignments; 8 flagged, all `not_steady_state`, one also `implausible`; 7 SpO₂ flatline, 3 of them PaO₂ drift; Vt oscillation 3 at 4,400, 4 at the floor; S1_M_0159 657 / 686 mmHg; FiO₂ 0.737 ×3, 1.0 ×5 | Same 12 clean ids; four-flag assignment identical in 20/20; 8 nss, 1 implausible; SpO₂ 7, all 3 PaO₂-drift runs among them; Vt 3 / 4; 656.99 / 686.42; FiO₂ 3 / 5 | OK |
| S10.7 | Sex-conditioned parameters: body fat 0.21 / 0.28; Hb 15.0 / 14.0, Hct 0.4412 / 0.4118; CO 5,600 / 4,900; 7 flow fractions; 13 tissue masses; dead space 0.002 × IBW, female Devine intercept 4.5 kg lower, 9 mL | `SetupPatient.cpp` L207–208 (fat), L139/L144 (Devine 45.5 / 50.0); CO at `SetupCircuitsAndCompartments.cpp` L293 and `CardiovascularModel.cpp` L314 (re-read with `git grep`); Hb/34 → 0.4412 / 0.4118; 7 and 13 per the closed register (L314–330, L2153–2165); 0.002 × 4.5 = 9 mL | OK |
| S10.8 | Lung tissue +9.8 % at equal mass, −8.3 % at native masses | (0.42/58.97)/(0.50/77.11) = 1.098; 0.4003 / 0.4364 = 0.917 (register §C) | OK |
| S10.9 | BMR intercept 88.632 vs 88.362; 0.27 kcal/day, 0.015 % | 1,751.88 vs 1,751.61 kcal/day on the male body; 0.0154 % | OK |
| S10.10 | "The reduction from 20/20 … to 0/20 … is an absolute-volume effect" | At fixed body mass, lowering the baseline lowers mL and mL/kg together, so S018 alone does not separate the two; the absolute framing rests on Pulse's parameterisation in mL and on the two bodies differing in absolute, not per-kg, volume, which the paragraph states | NOTE (reading; no change proposed) |

## Part S11 — Engine-side infrastructure recommendations (L893–911)

Sources: Pulse `SetupPatient.cpp` and `docs/Methodology/PatientMethodology.md` at REL_4_3_1 (local clone),
the live page `pulse.kitware.com/_patient_methodology.html` (fetched today), the ARDS condition and action
sources at REL_4_3_1 and REL_4_4_0, paper L320. Signals 18–20 of the August prose sweep re-checked.

| # | Claim | Check (2026-10-13) | Status |
|---|---|---|---|
| S11.1 | "The Discussion of the main manuscript mentions engine-side suggestions" (signal 19 was "closes with") | Paper L320: "engine-level observations that target tooling, documentation and validation infrastructure … (Supplement §S11)" | OK — signal 19 closed |
| S11.2 | "each is anchored in a specific experiment of this work" (signal 18) | Items 3 and 6 still carry no experiment pointer. Proposal: "and each arises from this work" | **DECIDE** (low) — signal 18 still open |
| S11.3 | Item 1: "Pulse currently reports input clamping (e.g. SBP > 120, DBP/SBP ratio out of range, HR or RR outside the initialisation band) as `[ERROR]`-prefixed log lines" | Every one of these is a `patient.Error` (HR L297–298, SBP/DBP L495–515, ratio L519–523, RR L580–587), i.e. a rejection, not a clamp; unchanged in REL_4_4_0. "input clamping" contradicts the item's own title ("input-rejection events") and §S3-clamp. → "reports input rejections", "detect rejections deterministically" | **MECH** |
| S11.4 | Item 2: the 4,082.24 mL floor "is not exposed in the public patient-setup documentation … a one-line note in the patient-baseline reference table would have avoided that investigation" (signal 20) | **False.** The table already carries the row: "Blood Volume Baseline \| Optional \| Bv * 0.85 \| Bv * 1.15 \| Above Stage 1 Hypovolemia" (`PatientMethodology.md` L56 at REL_4_3_1; live page today). Our own `pulsepatientmethod` entry quotes it, and §S10 L836 derives the floor from it. Only the body-specific number is not printed, as it depends on weight. Same text in the monograph L3593–3597. Proposal: delete item 2 (L911 "items 1–6" → "1–5"; "tooling, documentation or validation infrastructure" in L895 and paper L320 → "tooling and validation infrastructure"), or rewrite it as "log the computed admissible range at setup" (the log prints the default, and the bound only once violated, L541–556) | **DECIDE** |
| S11.5 | Monograph L4394: "**An undocumented constraint** was identified during boundary probing: … DBP / SBP ≤ 0.75" | **False.** `PatientMethodology.md` L60 at REL_4_3_1: "Diastolic Arterial Pressure Baseline … 60 mmHg \| 80 mmHg \| No hypotension or hypertension. Includes pressure fraction check: Dia > 0.75 Sys." (also on the live page). Paper and supplement do not call it undocumented | **DECIDE** (monograph only) |
| S11.6 | Item 3: the 2020 `STUDY_SENSITIVITY_ANALYSIS_1_0_0` tag runs Sobol on internal circuit values | As in CLAUDE.md row 1 (S016 GitLab audit) | OK |
| S11.7 | Item 4: "Pulse currently emits no setup-time warning when an ARDS action falls in this band" | True in REL_4_3_1 and REL_4_4_0: the ARDS condition and action sources contain no Warning or Error (calibrated: the same search finds the three unrelated `Warning(` calls of `RespiratoryModel.cpp`). But the band was measured on v4.3.1 and 4.4.0 rewrites the shunt mapping. Proposal: add "(measured on v4.3.1; untested under v4.4.0)" | **DECIDE** (low) |
| S11.8 | Item 5: "with full convergence at ∼300 s" | 40 of 44 converge, 6 run away (§S9). Proposal: "with convergence by about 300 s in 40 of 44 Healthy reruns" | **DECIDE** (low) |
| S11.9 | Item 6: "setup-time blood-pressure and pulse-pressure-ratio rejection messages require some domain knowledge to map back to the offending input field" | The blood-pressure messages name the field ("Patient systolic pressure baseline of … mmHg is too high", L495–515). Only the ratio message names neither field, and it states 0.75 as a "Minimum fraction allowed" although it caps DBP/SBP from above (L521). Proposal: restrict the sentence to the pulse-pressure-ratio message | **DECIDE** (low) |
| S11.10 | Closing paragraph | No physiology prescription in any item | OK |

## Part S12 — Reproducibility recipe (L917–1017)

Sources: `data/runs/full_sweep/aggregated.parquet` and `morris_sample.parquet`, `src/sampler.py`,
`scripts/analyze_sweep.py`, `data/runs/phase4a_run.log`, `experiments_log/santino/S006_full_morris_sweep.md`,
`audits/` (the three reproduction folders and `reproduction_check_2026-06-07.md`), Docker Hub API, Pulse
`PulseConfiguration.cpp` at REL_4_3_1. Scripts: scratchpad `s12_wall.py`, `s12_repro.py`, `s12_sample.py`
(writes only to the scratchpad). §S12.6 (WSL2 on both hosts) was decided on 2026-10-08 and is not reopened.

| # | Claim | Check (2026-10-13) | Status |
|---|---|---|---|
| S12.1 | L919: code "released under the Apache-2.0 license at github.com/…"; data "carry … CC-BY-4.0" (present tense) | True only once the repository is public; one of the present-tense sentences held by `check_publication_gate.py --verify-public` | NOTE (known, guarded) |
| S12.2 | Hardware; three workers reduced to two mid-sweep | As in the project CLAUDE.md; S006 log L70, L86–94 (`MAX_PARALLEL_LAPTOP 3 → 2`) | OK |
| S12.3 | Three end-to-end executions; 23 h 01 m on the reference machine and, "coincidentally", on the independent host; container time ≈ 27 h and 46 h | Two distinct logs: `phase4a_run.log` "23h01m12s", `reproduction_check_2026-06-07.md` "23h01m21s"; container time 27.39 h (canonical, without the two suspension records) and 46.0 h (reproduced aggregate) | OK |
| S12.4 | S4_M_0123 / 0124 span one ≈ 6.84 h suspension; 41.1 h naive vs 27.4 h; 20.78 h calendar span; ≈ 13.9 h active | 24,722 s each, 6.85 h above the 77-s median run; 41.12 h / 27.39 h; first-to-last output and log modification times span 20.78 h; 20.78 − 6.84 = 13.94 | OK |
| S12.5 | Docker template; "removing [the caps] does not change the simulation output (Pulse is single-threaded per run)" | Template as in CLAUDE.md. The single-thread statement was not checked today | NOTE (not independently verified) |
| S12.6 | Command block: 1,000 bootstrap resamples; 394/394, 393/394 on a public clone; 95/95; ~14 h with 2 workers, ~9 h with 3, ~23 h on slower hardware | `analyze_sweep.py` L78–79 `n_bootstrap=1000`; today's gate: ledger 394, crosswalk 95, 0 FAIL; 27.4 h / 2 ≈ 14, / 3 ≈ 9; 23 h 01 m | OK |
| S12.7 | Layer 1: the regenerated 160-point sample matches `morris_sample.parquet` byte for byte (signal 21 was "1,280-row") | Regenerated with `src.sampler.sample_morris(20, 4, 42)` + `save_sample`: 160 rows, values identical, SHA-256 `5d0803d4…` = committed file | OK — signal 21 closed |
| S12.8 | Independent full sweep: 1,280/1,280 flags; continuous values bit-identical; three H4 statistics at ~10⁻¹⁴; same BH-FDR set | 0 flag mismatches; max \|Δ\| = 0 over 59 float columns (wall time excluded); report: Wasserstein columns 2.8 × 10⁻¹⁴ (and `spearman_p` 9.7 × 10⁻¹⁷), 5/24 survivors, same cells | OK |
| S12.9 | Pilot "22/22 runs" (L1007) and "the 20 per-run output CSVs" (L1009) (signal 22) | 22 runs of which 2 are deliberate clamp probes that write no CSV (ThinkPad README L72–74); "five flags" of signal 22 is already fixed. Add "(the two deliberate clamp probes write none)" | **MECH** — signal 22 closes with it |
| S12.10 | L1009: `reproduction_2026-06-07/` "carries … a numerical comparison report (`reproduction_check_2026-06-07.md`)" | The report is `audits/reproduction_check_2026-06-07.md`, beside the folder, not inside it (`git ls-files`). Reword the path | **MECH** |
| S12.11 | macOS M2, macOS 26.5.1, emulated x86_64; `kitware/pulse:4.3.1` is `linux/amd64` only; max \|Δ\| 2.9 × 10⁻⁹, 22/22 | macOS README L45–53, L11; Docker Hub API today: one image, `linux` / `amd64` | OK |
| S12.12 | "Pulse's fixed 20 ms time step" | `PulseConfiguration.cpp` L474 at REL_4_3_1: `GetTimeStep().SetValue(1.0 / 50.0, TimeUnit::s)` | OK |
| S12.13 | (added while checking S17) "The minimal command sequence to regenerate the canonical sweep + audit ledger from a fresh clone" (signal 31 of the August sweep) | **Still open, missed above.** The sequence has no image build, but `src/runner.py` L35 runs `pulse-atlas-engine`, a locally built image (`engine/Dockerfile`, from `kitware/pulse:4.3.1`); step 2 fails on a fresh clone. The README has the step (L35, L245): `docker build -t pulse-atlas-engine engine/`. Add it as step 0 | **MECH** — closes signal 31 |

## Part S13 — SHAP cross-check and the clean-pair screen (L1023–1087)

Sources: `results/s023/` (`rf_metrics.csv`, `topk_overlap.csv`, `topk_overlap_per_cell.csv`,
`shap_vs_morris_summary.json`), `results/s034/` (`s034_summary.json`, `mu_star_by_screen.csv`,
`rank_comparison.csv`), `results/phase4b_top3_comparison_seed44.csv`, `results/seed_stability_top3_comparison.csv`,
the S009, S023 and S033 logs, Pulse `Saturation.cpp` at REL_4_3_1. Scripts: scratchpad `s13_check.py`,
`s13_single.py`. Ledger anchors already covering this part: `T2.s023.pooled`, `.fullmatch`, `.ge2_pct`,
`.r2_grouped_*` (PASS today).

| # | Claim | Check (2026-10-13) | Status |
|---|---|---|---|
| S13.1 | Signals 24 ("works because the underlying physiology is real") and 25 ("any reasonable statistical method") | Both phrasings gone from paper, supplement and monograph (0 hits; witness "cross-check" 7 hits) | OK — signals 24, 25 closed |
| S13.2 | n = 663 clean; one forest per output on the pooled subset with sex and scenario features; exact TreeExplainer values; per-cell n 42–144 | `shap_vs_morris_summary.json`: 663 of 1,280, 7 inputs + 2 sex + 4 scenario one-hot features; per-cell `n_runs_in_cell` 42–144. The artefact's own caveat still says "per-cell n=50-150" (stale, inside the JSON only) | OK |
| S13.3 | 17 of 18 pooled (five 3/3, PaO₂ 2/3); 23 of 48 full; 44 of 48 (92 %) ≥ 2 | Recomputed from `topk_overlap*.csv` | OK |
| S13.4 | "Pulse computes SpO₂ from the oxygen partial pressure through the haemoglobin dissociation relation, which also takes PaCO₂ and pH" | `Saturation.cpp` L90, L931: `CalculateHemoglobinSaturations(cs, O2PartialPressure, CO2PartialPressure, pH, temperature, hematocrit, …)` | OK |
| S13.5 | Table S13 and its prose: training 0.993–0.99997; out-of-bag 0.949–0.9998; grouped values ± SD; optimism 0.078–0.087 vs 0.0003 for Vt; blood gases average 0.87 | All values = `rf_metrics.csv` to the printed digits; OOB − grouped: PaO₂ 0.0778, SpO₂ 0.0842, PaCO₂ 0.0867, Vt 0.0003; mean 0.8728 | OK |
| S13.6 | "The three blood-gas channels average 0.87, with a spread ten to thirty times larger" (than Vt and HR) | Fold SD 0.053–0.071: 22–29 × HR's 0.0024, but 134–178 × Vt's 0.0004. Proposal: "twenty to thirty times that of heart rate" | **DECIDE** (low) |
| S13.7 | "the SHAP top-three sets take **nine** distinct values in total versus 25 for Morris"; MAP, SpO₂, PaCO₂ invariant over the eight cells | 9 and 25 at the locked forest seed (recomputed); the three invariant outputs confirmed at that seed. But the S033 log's seed test gives 9 (seed 42), 10 (seed 7), 10 (seed 999), and records the decision to state the contrast rather than the exact figure. Proposal: "nine (ten under two other forest seeds) … versus 25" | **DECIDE** (low) |
| S13.8 | "The 23 of 48 full-set agreement is stable across three independent forest seeds" | S033 log table: 23/48 at seeds 42, 7 and 999 (the artefacts keep only seed 42) | OK |
| S13.9 | S034: 663 runs / 454 of 1,120 pairs; 1,134 / 969; 471 extra runs, all `not_steady_state`-only; 3,090 extra observations, 1,152 Healthy; H1 48/48 both screens, 0.658–0.998 (median 0.928) and 0.695–0.994 (0.901); 18 of 48 gain FiO₂ (Healthy-M, Healthy-F, Severe-F); on 30: rank 1 30, set 19, order 15; median cut margin 39 %, one below 10 %; on 48: 41, 26, 21; 318 rows reproduced exactly; 12 single-pair entries, 9 in a top three | All equal to `s034_summary.json` (`criteria_*`, `h1_by_screen`, `median_cut_margin_clean` 0.393, `narrow_cut` n = 1, calibration Δ 0.0); single-pair entries recomputed from `mu_star_by_screen.csv` (S1_F Vt-input ×6, S4_M FiO₂-input ×6; 9 ranked ≤ 3) | OK |
| S13.10 | "Replaying cell Mild-M with an independent Morris sample seed preserves the rank-1 input in all 6 outputs, the top-three set in 4 and its order in 3; the screen change preserves 6, 2 and 2" | Comparator = seed 44, full size (`phase4b_top3_comparison_seed44.csv`): 6 / 4 / 3, recounted; screen: `criteria_S2_M_only` 6 / 2 / 2. ⚠️ Not to be confused with the older half-size seed-43 run of S009 (`seed_stability_top3_comparison.csv`: 5 / 3 / 1). Add "(seed 44, §S3-resample)" so the reader can tell them apart | **MECH** (cross-reference) |

## Part S14 — Pointer to the companion technical monograph (L1093–1097)

| # | Claim | Check (2026-10-13) | Status |
|---|---|---|---|
| S14.1 | "A companion technical monograph of over 100 pages" | `preprint/build/manuscript.pdf` rebuilt today: 123 pages | OK |
| S14.2 | Contents: preregistered hypotheses verbatim with amendment notes, experiment-log index, own reference list, sources of Table S1, boundary-probe summary, source-code audit; per-test rationale, ARDS calibration trace, engine-binary reproduction protocol | Monograph §2.0, Appendix A, §9, §1.2, Appendix B (B.3 ARDS calibration, B.4 source-code audit), §2.10, §2.8. Signal 26 (overclaims) already resolved | OK |
| S14.3 | "the experiment-log entries it consolidates are openly available under `experiments_log/` in the code repository" (present tense) | True once the repository is public (publication gate) | NOTE (known, guarded) |

## Part S15 — Compensatory tachycardia (L1109–1139)

Source: `data/runs/full_sweep/aggregated.parquet`, `results/morris_indices.parquet`. Script: scratchpad `s15_s16.py`.

| # | Claim | Check (2026-10-13) | Status |
|---|---|---|---|
| S15.1 | Table S15: 73.8 ± 20.4, 87.3 ± 24.3, 155.7 ± 34.7, 147.1 ± 31.8 over clean runs; input levels 50/70/90/110 | Clean n 91 / 179 / 266 / 127; means and SD (n − 1) identical to the printed digits; four HR levels | OK — signal 27 ("uniformly") closed |
| S15.2 | Input HR is rank 1 for output HR in every Healthy cell; 145–160 bpm in Moderate and Severe, about 70 above the 80-bpm midpoint | Rank 1 = HR in all eight cells; 155.7 − 80 = 75.7, 147.1 − 80 = 67.1 | OK |
| S15.3 | The Severe easing "may partly reflect differential clean-run retention" | 266 vs 127 clean (83.1 % vs 39.7 %); the confound is now stated | OK — signal 28 closed |
| S15.4 | "those firing none of the four flags" | Four flags named | OK — signal 29 closed |
| S15.5 | "Users running Pulse for ARDS device validation should treat output HR as …" | Advice, not a usage claim, but it presupposes device-validation use; the cover letter's "device-validation studies" (L8 of the letter review) is unsupported by the cited uses. Keep consistent with the author's decision on L8 (monograph L569, L2084, L2294, L3148 say the same) | NOTE (linked to letter L8) |

## Part S16 — Output stability across the 120-second window (L1148–1156)

Source: `data/runs/full_sweep/aggregated.parquet` (`*_delta_60s`), thresholds `src/detector.py`
`DRIFT_MAX_DELTA_60S` (HR 5, MAP 5, Vt 50, SpO₂ 0.02, PaO₂ 15, PaCO₂ 5). Script: scratchpad `s15_s16.py`.

| # | Claim | Check (2026-10-13) | Status |
|---|---|---|---|
| S16.1 | Hyperoxia arm (FiO₂ ≥ 0.95; 195 valid runs): HR 2.6 % (median 0.20), MAP 0 % (0.05), PaCO₂ 3.6 % (0.58), PaO₂ 19.5 % (4.3; p95 40.2), Vt 8.7 % | 195 non-diverged runs; 2.6 / 0.197; 0.0 / 0.0495; 3.6 / 0.575; 19.5 / 4.31 / 40.2; 8.7 % | OK |
| S16.2 | Oscillation arm (Vt CV > 0.05; 303 runs): HR 2.3 %, MAP 0.7 %, PaO₂ 7.3 %, PaCO₂ 2.0 % | 303; 2.3 / 0.7 / 7.3 / 2.0 | OK |
| S16.3 | "window-length sensitivity was thus concentrated in PaO₂ and delivered Vt … HR, MAP and PaCO₂ rarely exceed threshold" | Follows from S16.1–S16.2; §S9 contradicts it on Vt (S9.7) | OK (see S9.7) |

## Part S17 — Summary of supplementary findings (L1163–1192)

| # | Claim | Check (2026-10-13) | Status |
|---|---|---|---|
| S17.1 | Twelve verified limitations | Table S1 rows 1–12 (5–6 merged) | OK |
| S17.2 | Sobol: 43 of 48, all eight cells, 6,144 or 3,584 vs the 1,500 envelope | = §S3-sobol L360 | OK |
| S17.3 | Seed 44: rank 1 kept in all six outputs; Mild-M divergences 4/160 → 7/160 | = §S3-resample L428–432 and S13.10 | OK |
| S17.4 | §S4, §S5, §S6, §S7 (15 Cornish channels), §S10, §S13 (17 of 18), §S15, §S16 rows | Consistent with the parts above | OK |
| S17.5 | "**Six** engine-side infrastructure recommendations … documentation of the male reference body's blood-volume floor; …" (signal 30: the list did not match §S11) | The six now match §S11 item for item (signal 30 closed). But the row depends on S11.4: if item 2 goes, "Six" → "Five" and the documentation item leaves the list | OK — signal 30 closed; **linked to S11.4** |
| S17.6 | "of the main manuscript" harmonisation | 65 × "main manuscript", 0 × "main paper" in the supplement | OK |

**Double-check of the decision block (2026-10-13, evening).** Re-verified before the re-freeze 59 lot:
S4.4 recomputed again (966 / 1,280, 75.5 %, against the script's 1,008; positive control 530 / 530
`not_steady_state` runs reproduced); S5.14 re-read at source: the ARDS severities of Pulse's scenario files
stop at 0.9 (ARDSExacerbation 0.3 / 0.6 / 0.9, ECMOARDSOxygenation 0.8, others ≤ 0.6) and only the C#
HowTo goes to 1.0 (live code, `HowTo_EngineUse.cs` L136–137); nothing in 0.91–0.945. Twins found or
updated:
- **S11.4 propagates further than its row says.** Supplement: L895 ("tooling, documentation or validation
  infrastructure"), L900 (item 2), L911 ("items 1–6"), §S17 L1184 ("Six … documentation of the … floor").
  Paper: L320 ("tooling, documentation and validation infrastructure"). Monograph: key-facts bullet
  L277–278 ("Six engine-side infrastructure recommendations"), §4.7 introduction L3561–3569 ("six places",
  "tooling, documentation, or validation"), item 2 L3589–3597. Nuance for the wording of any fix: the
  documentation gives the rule (minimum = computed Bv × 0.85); only the body-specific number is not printed.
- **S11.3 (MECH) has a monograph twin:** §4.7 item 1, "Pulse currently surfaces input clamping" (L3577–3583).
- **S5.13 monograph twin** is now at L4508 (L4473 before today's monograph edits).
- No twin in the paper or monograph for S6.2, S9.7 or S9.10; S9.19's twin is monograph L2815–2818.

**Second double-check (2026-10-14).** Every row of the decision block re-opened at its source in this
session; line numbers below are those of `7e6676e` (supplement and paper as at `54aa84a`).
- **S4.4, second instrument.** Parsing the recorded `not_steady_state_reason` strings (separator "; ",
  checked on multi-trigger rows) instead of re-implementing the rule: a run is clean after the joint
  exclusion when it has no `clamped`, `diverged` or `implausible` flag and every recorded trigger is
  "Vt CV" or an SpO₂ flatline at saturation. Result identical to the first instrument: 119 / 122 / 133 /
  153 / 148 / 157 / 67 / 67, total 966 / 1,280 (75.47 %); the 42 wrongly added runs are Healthy-M 8,
  Healthy-F 14, Severe-M 5, Severe-F 15. First instrument re-run: positive control 1,280 / 1,280, the
  script formula still gives 1,008. Loci, re-derived: supplement Table S4 L463, L464, L472, L473 (four
  cells) and L475 (total), text L480; monograph L3495, Appendix C table L4698–4710 (same four cells and
  the total), L4753. The row's monograph line numbers (L3481, L4674, L4717) are those of the number
  inventory, not of the current file. Paper, cover letter and README: no occurrence.
- **S6.2, register precision.** The eight uncovered Severe-F pairs have Δ60 s from +0.027 to +0.063 at
  the FiO₂ = 0.473 endpoint (the eighth pair, whose FiO₂ = 1.0 endpoint carries Vt CV, is at +0.027; the
  row's "+0.028" is the minimum over the other seven). SpO₂ mean 0.786–0.873. 8 / 20 confirmed.
- **Monograph twins not listed above.** S11.7: §4.7 item 4 (L3616–3627) still quotes the narrower
  "~0.91–0.945" zone and "does not currently emit a setup-time warning". S11.8: item 5 "with full
  convergence at ~300 s" (L3631). S11.9: item 6 (L3640–3643), same sentence as the supplement. S11.4: the
  §4.7 introduction lists [S018] among the anchors, and only item 2 is anchored in S018. The monograph's
  items 3 and 6 do carry experiment pointers (S006/S016, S005), so S11.2 has no monograph twin. S9.10:
  the monograph statements it agrees with are now at L158 and L2956. S5.13 twin at L4509–4510. No twin
  for S8.13, S9.15 or S13.6 ("twentyfold", "order of magnitude", "ten to thirty": 0 hits besides an
  unrelated Sobol-cost sentence at L1534).
- **S11.3 is wording that matches the paper's own result** (H2: loud rejection, not silent clamping);
  kept as MECH, but the explanation to the author says so.
- Reconfirmed at source without change: S4.8 (78.125 %, `s014_trigger_lockout/summary.json`); S5.14
  (`HowTo_EngineUse.cs` L136–137, severity 1.0 on both lungs, uncommented, in the `PatientFile`
  initialisation branch); S8.9 (`s033_cycle_resolved_vtcv.py` L662–667, `n_pairs_in_estimands` 63);
  S8.13 (21.42 / 22.66 / 27.84 / 25.63; 22.45 on the 64 group medians); S9.7 (Vt 13 / 44 at 120 s and
  at 300 s; PaCO₂ +1.02 mmHg median, max 9.74); S9.15 (643.2 / 143.6 / 72.6); S9.18 (152 runs, 148
  `implausible` or `not_steady_state`, 4 `diverged` only); S11.4 and S11.5 (`PatientMethodology.md`
  L56 and L60 at REL_4_3_1); S12.9 (20 CSVs, README L72–74); S12.10 (`git ls-files`); S12.13 (README
  L245, and L275–279 already warns that a fresh build does not match the image hash but reproduces the
  outputs); S13.6 (grouped SD 0.0532 / 0.0562 / 0.0705 vs HR 0.00243 and Vt 0.00040).

**Applied (2026-10-14, `fbe90c8`, author's approval of the whole block the same day).** Every DECIDE
and MECH row of S4–S17 above, with the proposals as written, plus their twins. Choices made while
applying, none of which changes a claim beyond the approved rows:
- S4.5 also aligned in the monograph's Appendix C sentence that describes the columns (same wording).
- S4.4 is now measured by three instruments that agree: the rule re-implementation, the reason-string
  parse and the corrected `nss_decomposition_table.py` (966; 119 / 122 / 133 / 153 / 148 / 157 / 67 / 67).
- S11.5 names Pulse's Patient Methodology page in the monograph text instead of adding the
  `pulsepatientmethod` key: a new Kitware 2026 entry would shift the a/b/c letters of the other Kitware
  citations of the monograph. Alternative rejected: cite the key and re-letter.
- S11.4 also removed [S018] from the anchor list of the monograph's §4.7 introduction (only item 2 used
  it); items 3–6 renumbered 2–5 in the monograph source (LaTeX renumbers the supplement itself).
- S11.9 keeps the `[ERROR][SystolicArterialPressure]` example: it illustrates the prefix format, which
  applies to every setup error.
- Not applied, left to the author: the monograph's abstract and F-004 summary (L54, L2793) still say the
  oscillation is "corrected by setting trigger pressure to −2 cmH2O"; S4.8 concerned the supplement only.
- Guards moved with the text: the continuous-band guard re-pinned on the new HowTo sentence (supplement
  and letter); the SHAP spread guard now checks [20, 30] against heart rate; the back-reference manifest
  follows the paper's reworded L320; crosswalk counts 78.1 % 3 → 4, 4,802.63 8 → 7, 4,082.24 6 → 5.

**Double-check after the re-freeze (2026-10-14).** Re-run on `044b994`, nothing changed in the manuscripts:
- The frozen files: `build/` = `build/freeze59/` = the four hashes of `dispatch_log.md`; tree clean, no stash.
- The old figure in any form (1,008, 78.8, 78.75, "four in five", "nearly 80", "joint exclusion") in the
  paper, supplement, monograph, letter, README, experiment logs and `results/s022/`: only unrelated hits
  (11,008 Sobol runs; a 0.75 × 105 = 78.75 DBP bound in S004) and the corrected monograph bullet.
- **S5.14 / letter L11 now also hold for v4.4.0**, the current release, which the earlier checks (on 4.3.1
  and 4.3.2) did not cover. Tag `REL_4_4_0` fetched into the local clone (`5e29e5b`, the GitLab release
  commit; GitLab's compare endpoint timed out at 1,000 files with 888 empty diffs and could not be used).
  In the 78 files that mention ARDS (66 at 4.3.1, same pattern), the only literal in [0.91, 0.945] is an
  I:E tuning factor (`m_IERatioScaleFactor *= 0.94`, present in both tags: the positive control). ARDS
  severities in the 4.4.0 scenario files: 0.0–0.9 (max 0.9); C# HowTo 1.0; the new Python ECMO studies
  0.3 / 0.6 / 0.9, 0.7 and a fixed 0.9.
- §S1's source-level statements re-read on the local tag: the VC-AC default-trigger block is identical
  (4.3.1 L120–128 = 4.4.0 L156–164); `SetupPatient.cpp` differs by one line (L694, a tidal-volume
  variable), not in its acceptance limits; Eigen 3.4.0 → 5.0.1 (`External_Eigen3.cmake`); the 4.3.1 ARDS
  damage table on the shunt resistance (`{0.3, 0.100}, //Mild …`) is absent from 4.4.0.

## Addendum to Part S1 (2026-10-13) — Pulse 4.4.0 has been released

Flagged during a pre-submission review of the supplement; checked at the primary sources, twice
where possible.

| # | Claim | Check (2026-10-13) | Status |
|---|---|---|---|
| S1.8 | §S1 L135: "The current upstream stable head, `REL_4_3_2` (released 2025-08-12), differs from `REL_4_3_1` only in its build system" | `git ls-remote`: tag `REL_4_4_0` → `5e29e5b`, which is also `refs/heads/stable`; GitLab release "Pulse 4.4.0", `released_at` 2026-09-30 09:01 −04:00; tag commit "Merge branch 'integration' into 'stable' / 4.4.0 Release", parents `e8a3649` (= REL_4_3_2) and an integration commit; Kitware webinar "What's New in the Pulse Physiology Engine 4.4.0", 30 September 2026. The 4.3.2 half of the sentence stays true; "current stable head" has been false since 2026-09-30. Same statement in the monograph L801–802, L816, L3885–3886; true-but-incomplete in L117, L3745, in §S2 (i) L189 and in paper L322 (Discussion (i)) | **DECIDE** → author 2026-10-13: yes, with a softer final clause ("may not carry over unchanged to v4.4.0"); monograph applied and committed (L117–119, L802–804, §2.1 L815–838, L3759–3762, L3900–3907, line numbers after the edit); paper L322, §S1 L135, §S2 (i) L189 written and held in a named git stash until the re-freeze 59 build, which the pre-commit .docx check needs |
| S1.9 | Claim checked: 4.4.0 changes "the interactions between mechanoreceptors and chemoreceptors" | **False for 4.4.0.** "Updated the interactions between the respiratory mechanoreceptor and chemoreceptor models" is under **v4.3.1 (January 2025)** on `pulse.kitware.com/version.html` and in the GitLab release of REL_4_3_1 (2025-01-24): it is already in the version the atlas uses. The 4.4.0 notes contain no "receptor" term | **False for 4.4.0** (a 4.3.1 change) |
| S1.10 | Claim checked: 4.4.0 is a major release | Pulse's `Versioning.md` (REL_4_4_0): MAJOR = incompatible API, MINOR = backward-compatible functionality. 4.3 → 4.4 is a minor release, though large: 645 commits between the tags by GitLab's compare (543 dated after the 4.3.2 commit; two different units) | NOTE |
| S1.11 | What 4.4.0 changes that the atlas depends on | Release notes ("Physiology Model Improvements"): anatomic vs physiologic pulmonary shunting; respiratory resistance and compliance calculations; respiratory compartments refactored; CO₂ saturation inflection point removed; Eigen updated to 5.0.1. Measured in the source: Eigen 3.4.0 (REL_4_3_1 `External_Eigen3.cmake`) → 5.0.1; Eigen is the circuit solver's library (`SECircuitCalculator.cpp`: SparseLU, SparseQR, BiCGSTAB); the ARDS-severity → shunt curve is rewritten (4.3.1: multipliers 1 / 0.1 / 0.2 / 0.15 / 0.1 on the shunt resistance; 4.4.0: 0 / 0.4 / 0.4 / 0.5 / 0.6 / 1.0 with a new recruitment curve, applied to physiologic shunt flows); changed lines ignoring whitespace: `RespiratoryModel.cpp` 1,766, `CardiovascularModel.cpp` 1,110, `NervousModel.cpp` 348 (baro- and chemoreceptor baselines reorganised), `MechanicalVentilatorModel.cpp` 435 (including patient-trigger timing). The cardiovascular and nervous changes are not described in the release notes | measured |
| S1.12 | What 4.4.0 leaves unchanged | `SetupPatient.cpp`: one changed line in the whole file (baseline tidal volume uses the computed FRC); age 18–65, HR 50 / 110, RR 8–20, SBP 90–120, DBP 60–80, ratio 0.75, blood volume 65.6·W^1.02 and floor ×0.85 identical. `SEMechanicalVentilatorVolumeControl.cpp`: the rule that enables the respiratory-model trigger when neither trigger flow nor pressure is given is identical (now L156–164 instead of L120–128); how the ventilator model then executes a trigger has changed (row above) | measured |
| S1.13 | Re-running on 4.4.0 | Docker Hub: `kitware/pulse:4.4.0` → HTTP 404, `4.3.1` → 200 (control); a 4.4.0 run needs a source build, and the rewritten shunt curve means the scenario fractions would first need re-calibration | recommendation to the author: not before submission |
| S1.14 | The motivation (no formal SA) | FAQ re-read today with two tools (WebFetch and firecrawl): unchanged, "We have not performed a systematic forward propagation … nor have we conducted a formal sensitivity analysis. We plan to begin this type of analysis in the near future." | OK |

Kitware's What's New page heads the section "Pulse v4.4.0 (August 2026)" while the GitLab release and
the webinar are dated 30 September 2026: cite the dated GitLab release.

### Erratum to this addendum (2026-10-13, second double-check)

Re-checked from the files themselves: `REL_4_3_1` from the local clone (`git show`), `REL_4_4_0` from
the GitLab API (`repository/files/…/raw?ref=REL_4_4_0`, HTTP 200 for all nine files). Release, tag,
stable head, Docker Hub (404 / 200), FAQ, What's New page and webinar date re-confirmed today.

| # | Claim | Check (2026-10-13) | Status |
|---|---|---|---|
| S1.15 | S1.11 "`MechanicalVentilatorModel.cpp` 435 (including patient-trigger timing)" and S1.12 "how the ventilator model then executes a trigger has changed" | **Wrong.** The trigger-detection block (REL_4_3_1 L780–1010, REL_4_4_0 L786–1016) is identical except that `patientTriggered` is now passed to `CalculateExpiratoryRespiratoryParameters`, which only feeds a new time-since-patient-trigger counter read by a new apnea alarm. Of the 435 changed lines, 388 are appended alarm code (`CheckCyclingAlarms`, `CheckAlarms`, active only when alarm thresholds are set); the rest split the ventilator connection into mouth and nasal-cavity paths and edit comments and event signatures. The respiratory-model trigger fires on the `StartOfInhale` event set in `RespiratoryModel::ApplyDriver`: `CalculateDriver` + `ApplyDriver` change by 39 lines (GNU `diff -w`), the driver pressure / period updates by 46, partly cosmetic (event-time argument dropped, `M_PI`), partly an explicit-mechanics override. So the trigger rule and its detection are unchanged; the breathing drive that fires it, and the blood gases that feed it through the chemoreceptors, may change | corrected here |
| S1.16 | S1.11 changed-line counts | Instrument: GNU `diff -w` on the files at the two tags (1,766 / 1,110 / 348 / 435). The counts depend on the algorithm: `git diff --no-index -w --diff-algorithm` myers / minimal / patience / histogram give 1,754–1,818 / 1,052–1,108 / 346–350 / 435. In `CardiovascularModel.cpp` much of the diff is circuit-path registration renamed from `ExpandedCardiovascularPath` to `ComputationalLifeCardiovascularPath` (210 → 318 registrations) and the dropped event-time argument; 564 changed lines remain without them. In `NervousModel.cpp` (230 deleted / 126 added), `SetBaselines` is split into `SetBaroreceptorBaselines` + `SetChemoreceptorBaselines`, `InitializeBaroreceptors` is removed, and commented-out code is deleted. Whether behaviour changes cannot be told without running 4.4.0 | NOTE (an order of magnitude, not a measure of behaviour change) |
| S1.17 | §S8.4 L764: "(`SEMechanicalVentilatorVolumeControl.cpp`, lines 120--128 of the upstream Pulse source)" | The same block is at L156–164 in REL_4_4_0, so "the upstream Pulse source" no longer names a version; add "at `REL_4_3_1`". Only line-range citation of Pulse code in the paper and supplement (search calibrated on this very hit). Monograph twin L3174 (L2975 already says "Pulse 4.3.1"); seven other monograph line citations carry no version on the same line (L4532, L4537, L4552, L4556, L4559, L4589, L4597): check their paragraph context in the monograph alignment | **MECH** → monograph L3174 (now L3188) applied; supplement L764 written and held with the paper lot for re-freeze 59 |
| S1.18 | Wording of the release-note items for §S1 | The notes say "Removed inflection point in CO2 saturation calculation **for high dissolved CO2 values**" (keep the qualifier) and "Refactored respiratory compartments **and volume distribution**". The only "cardiopulmonary" item is an **optional** bronchopulmonary-segment model (18 segments); the default-model changes are the shunting, resistance / compliance and compartment items. Eigen 5.0.1 is listed under "Software Architecture Improvements", not physiology. REL_4_3_2 still uses Eigen 3.4.0 (its only Eigen change is the archive's MD5 hash) | NOTE |
| S1.19 | Other "current version" wording | None in the paper, supplement, cover letter, metadata or README (the cover letter names no Pulse version; positive control: "current upstream" → 1 hit in the supplement). Monograph L820–825 ("While future releases will inevitably alter underlying physiology") is now overtaken by 4.4.0: align with L816 | NOTE |
| S1.20 | Sweep date vs release | Every simulation predates 4.4.0: S006 (the 1,280-run sweep) 2026-04-26, latest experiment S034 2026-09-12; release 2026-09-30 | OK |
