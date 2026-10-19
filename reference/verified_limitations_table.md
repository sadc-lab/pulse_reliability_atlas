# Verified Pulse 4.3.1 limitations: the table formerly kept in `CLAUDE.md`

This file is a verbatim copy, made on 2026-10-19, of the section "Verified
Pulse 4.3.1 limitations" of `CLAUDE.md`, the instruction file of the AI
coding assistant used on this project. That file is not part of the public
repository (see [`HISTORY.md`](../HISTORY.md)). Dated registers and log
entries that cite "`CLAUDE.md` limitation #N", "`CLAUDE.md` item N" or a
`CLAUDE.md` row number refer to the table below. Its numbering (1 to 12)
has not changed since the table was first written on 2026-04-19; the
wording and evidence of several items were refined later, and this copy
carries the latest wording. The longer, sourced write-up of the same
limitations is [`pulse_limitations_verified.md`](pulse_limitations_verified.md),
whose section numbers differ from this table's.

---

# Verified Pulse 4.3.1 limitations (as of 2026-04-19, GitLab re-audit 2026-05-07 in S016)

Use this list. Do not add claims without evidence.

> **Pulse `REL_4_3_2` (2025-08-12)** is build-system-only (7 files / +46 −17, web-WASM dockcross + .NET binding). **No physiology changed.** **`REL_4_4_0` (2026-09-30) changes the physiology** (ARDS shunt mapping rewritten, Eigen 5.0.1, respiratory / cardiovascular / nervous code changed; no `kitware/pulse:4.4.0` Docker image as of 2026-10-13). Atlas stays pinned to 4.3.1; results apply identically to 4.3.2 and may not carry over unchanged to 4.4.0. See Supplement §S1 and `audit/supplement_audit_2026-09-28.md` rows S1.8–S1.20. Re-confirm by re-fetching the GitLab repo before paper submission.

| # | Limitation | Evidence |
|---|---|---|
| 1 | No formal SA / UQ on **user-facing operational inputs** (HR, BP, RR, Vt, FiO2, PEEP). Pulse's 2020 `STUDY_SENSITIVITY_ANALYSIS_1_0_0` tag did Sobol on **internal lumped-parameter circuit values (cardiovascular and respiratory resistances and compliances)** for model calibration — different parameter class. Its code is still in the 4.3.x source tree (17 commits on the folder 2021–2024, two touching the study's own code); no published re-run on 4.3.x was found. | Pulse FAQ verbatim (still current 2026-05-07) + 2020 study tag at `src/cpp/study/sensitivity_analysis/` (S016 GitLab audit; its "not ported" corrected by the S016 note of 2026-09-27). Core motivation of this project: first SA on operational inputs. |
| 2 | BP gate: SBP outside 90–120 or DBP outside 60–80 rejected **loudly** at setup (explicit `[ERROR]` log + exit code 1) — not silent. Pulse-pressure ratio DBP/SBP ≤ 0.75 also enforced. | Pulse_translation_new E10 + source audit + S005 deliberate-clamp probes + manuscript §3.4 (H2 NOT supported, 0 / 1,280). The probes tested the upper bounds only; the lower bounds (SBP < 90, DBP < 60) rest on `SetupPatient.cpp` (REL_4_3_1 L493–517, same error path), re-read 2026-09-27 |
| 3 | Adult-only: age>=18 hard-gated in `SetupPatient.cpp` L41–64 | Source audit 2026-04-07 |
| 4 | ARDS solver instability zone 0.91–0.945 | Pulse_translation_new E6 + E10 + original calibration (3 independent sources) |
| 5 | HR init acceptance 50–110 bpm only | Pulse_translation_new HR initialisation boundary probe, 11/11 Docker runs matched |
| 6 | RR init acceptance 8–20 bpm only | Pulse_translation_new RR initialisation boundary probe, 9/9 Docker runs matched |
| 7 | **Two distinct referents, do not merge them.** (a) PC-AC delivers 24–59% MORE Vt than **VC-AC within Pulse** (PIP=20). (b) PC-AC deviates 11.3–25.3% from the **physical ASL-5000 reference**, in the *under*-delivery direction. | (a) Pulse_translation_new PC-AC-vs-VC-AC tests: male 594.5 vs 479.6 mL (+24.0%), female 635.3 vs 399.7 mL (+58.9%). (b) Pulse validation Tables 5/12/19: engine 935/409/490 mL vs expected 1047/528/571 mL; corroborated by Webb 2022 (PMC10224749). The two are **not concordant and not in conflict** — they compare different pairs. |
| 8 | Upper airway = single trachea resistance (no nose; the pharynx is a 1 mL gas compartment with no resistance of its own) | Source audit 2026-04-07, pharynx corrected 2026-09-28 (`SetupCircuitsAndCompartments.cpp` L2991–2994, L3066–3068, L3146 at `REL_4_3_1`); `Upper*ResistanceMultiplier` scales that trachea resistance (`RespiratoryModel.cpp` L3624–3641) and is the only handle |
| 9 | No regional V/Q mismatch | Structural (5-compartment lumped parameter) |
| 10 | Vital capacity +7% vs literature | Pulse's own validation table |
| 11 | Lumped-parameter limits: no inertance, linear resistance, idealized valves | Pulse docs / Bray 2019 |
| 12 | No dicrotic notch, no retrograde flow, ECG P/T wave merge at high HR | Pulse docs / Bray 2019 |

**Withdrawn claims** (do NOT cite as limitations):
- ~~FiO2 crash at 1.0~~ — disproved by the companion FiO2 = 1.0 crash probe (Apr 2026). Pulse accepts FiO2=1.0.
- ~~No sex-specific physiology beyond weight/height~~ — unverified. Pulse has sex-specific hemoglobin/body composition; do not assert until source-checked.

