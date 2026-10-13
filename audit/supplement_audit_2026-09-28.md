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
