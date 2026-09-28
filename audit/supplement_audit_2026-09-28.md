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
`preprint_npj/paper_to_monograph_map.md`). The row-by-row table is still to be
copied here from that message.

Consequence noted after the rebuild: citing `pulsecardiomethod` in §S1 makes it
reference [2] of the supplement, so the supplement's reference numbers shift
(automatic, BibTeX). The paper's numbering is unchanged.

