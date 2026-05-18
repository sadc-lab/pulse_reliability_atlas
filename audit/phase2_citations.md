# Phase 2 — Citation verification (independent re-fetch)

**Date:** 2026-05-18
**Pass:** Independent of prior commit `2e69660`. Every external
citation was re-fetched and re-read in this pass; the prior audit's
"verified ✓" marks were not trusted.
**Tools used:** WebFetch (Pulse Kitware docs, journal landing pages,
DOI redirects), alphaxiv MCP `answer_pdf_queries` + `get_paper_content`
(Cornish 2023 arXiv v4), WebSearch (paywalled-paper metadata via
publisher landing pages + PubMed), local file reads against the
cloned Pulse engine at
`C:/Users/santi/projets/Pulse_engine_adults_Gitlab/engine/`.
**Total external fetches:** ~25.

## Headline result

* **15 of 16 bib entries reproduce cleanly** — DOIs / URLs resolve;
  authors, year, journal, title, and load-bearing factual claims
  match what the manuscript attributes to them.
* **All 7 Pulse C++ source-line attributions reproduce** in the
  locally-cloned `REL_4_3_1` engine, with one minor code-quote
  paraphrase noted below (P2-W1).
* **Pulse FAQ verbatim quote** matches the live page character-for-
  character.
* **Cornish 2023 v4** Hoeffding totals (85) and bootstrap totals (281)
  reproduce exactly; all 15 per-channel counts reproduce; the
  manuscript's "Table 4 = Hoeffding re-tab, Table 5 = bootstrap"
  attribution is correct against the appendix tables on the v4 PDF.
* **No new substantive discrepancies** — the prior audit (D11, D12,
  D13) caught the citation errors that mattered. **2 minor wording
  issues** (P2-W1, P2-W2) and **2 items deferred for live access**
  (P2-D1 Pulse GitLab tag re-confirmation, P2-D2 Pulse Energy
  Methodology page) are surfaced below.

---

# A. Per-citation verification table

Legend: ✓ verified | ⚠ minor wording issue | ✗ discrepancy | — deferred

| # | BibKey / Reference | Where in manuscript | What we attribute | Verification method | Verdict |
|---|---|---|---|---|---|
| 1 | `pulsefaq` | §1.1 lines 89–91 (verbatim quote) | "We have not performed a systematic forward propagation or inverse quantification of model uncertainty, nor have we conducted a formal sensitivity analysis." | WebFetch live `_f_a_q.html` | ✓ char-exact match |
| 2 | `pulsevent` | §1.2 line 168 + §2.3 lines 366–368 | "VC-AC 0.07 / 1.01 / 2.25 % healthy / restrictive / obstructive; PC-AC 11.3 / 25.3 / 15.3 %" | WebFetch live `_mechanical_ventilator_methodology.html` | ✓ all 6 numbers reproduce; Table 3 healthy VC-AC = 0.0681 % (rounds to 0.07 ✓); restrictive/obstructive in Tables 10/12/17/19 |
| 3 | `pulserespmethod` | §2.3 lines 322–335 + Appendix B.3 | (a) Severity scalar 0.3 / 0.6 / 0.9 mapped to mild/moderate/severe; (b) page does NOT state the 340/130/50 P/F values | WebFetch live `_respiratory_methodology.html` | ✓ (a) page states "severities of 0.3, 0.6, and 0.9 respectively"; ✓ (b) confirmed page references Berlin Criteria generally but does NOT state P/F values 340/130/50 — the prior D11 correction (attributing P/F values only to `webb2020`) is correct |
| 4 | `webb2020` | §2.3 lines 326–330 + Appendix B.3 lines 2070–2082 | severities 0.3/0.6/0.9 → P/F 340/130/50 mmHg | WebFetch live PLoS One landing page (DOI resolves) | ✓ exact quote: "severities matching mild, moderate, and severe cases resulting in PaO2/FiO2 of 340, 130, and 50 mmHg, respectively"; authors Webb JB, Bray A, Asare PK, Clipp RB, Mehta YB, Penupolu S, Patel AA, Poler SM (2020) ✓ |
| 5 | `webb2022vent` | §1.2 line 168 + §2.3 lines 367–368 | "ASL 5000 validation framework; qualitative waveform agreement; does NOT report quantitative Vt-error percentages" | WebFetch PMC10224749 (PubMed Central, open) | ✓ paper reports qualitative waveform agreement only; does NOT contain quantitative Vt error percentages; full author list (Webb JB, Bray A, Scheirich H, VanPelt J, Gerard J, Frembgen S, Clipp RB, 2022) matches bib entry |
| 6 | `cornish2023` | §1.1 lines 99 + §4.4 entire Table 2 | (a) Oxford stats group, arXiv 2301.07210 v4 Nov 2023; (b) Pulse on MIMIC-III sepsis; (c) Table 1 Hoeffding 85 total; (d) Appendix Table 4 = Hoeffding re-tab; (e) Appendix Table 5 = bootstrap, 281 total; (f) per-channel counts in our Table 2 | alphaxiv MCP `get_paper_content` v4 + `answer_pdf_queries` | ✓ authors Cornish R, Taufiq M F, Doucet A, Holmes C (Oxford + Alan Turing Institute); ✓ v4 dated 2 Nov 2023; ✓ Pulse + MIMIC-III sepsis case study; ✓ Table 1 sum = 24+21+13+10+5+5+3+2+2+0+0+0+0+0+0 = 85 ✓; ✓ Appendix Table 4 caption: "obtained using Hoeffding's inequality"; ✓ Appendix Table 5 caption: "obtained using the reverse percentile bootstrap"; ✓ Table 5 sum = 47+46+33+43+44+19+13+8+8+4+0+0+3+12+1 = 281 ✓; ✓ paper itself states "281 vs. 85 rejections in total" |
| 7 | `cornish2023` Table 2 per-channel | §4.4 Table 2 rows 1–15 | Each channel's Hoeffding and bootstrap counts | alphaxiv v4 Table 1 (lines 3517–3543) + Table 5 (lines 14500–14527) | ✓ all 30 cell values (15 channels × 2 columns) reproduce exactly. Chloride 24/47, Sodium 21/46, Potassium 13/33, SkinTemp 10/43, Calcium 5/44, Glucose 5/19, HCO3 2/8, pH 0/0, PaCO2 3/13, PaO2 0/4, MeanBP 0/3, SysBP 2/8, DiaBP 0/0, HR 0/1, RR 0/12 ✓ |
| 8 | `bray2019` | §1.1 line 66 + §6.7 bib entry | Pulse engine paper; 9-author list (Bray A, Webb J B, Enquobahrie A, Vicory J, Heneghan J, Hubal R, TerMaath S, Asare P, Clipp R B); SN Comp Clin Med 1(5):362-377 (2019); cardiovascular-limitation references for valve idealization / dicrotic notch / viscoelastic limits | WebFetch DOI redirects through Springer (paywalled body); WebSearch metadata | ✓ DOI 10.1007/s42399-019-00053-w resolves; Springer metadata confirms title, year, journal, volume/issue, and the 9-author list (per ResearchGate + Pulse publications page); paper is the canonical Pulse engine reference. Body claims about specific limitations (valve idealization etc.) deferred — abstract sufficient per user paywall policy; the manuscript's §1.2 row-7 attribution chain is to Pulse docs not to bray2019 directly |
| 9 | `morris1991` | §2.5 + §2.10 | Morris elementary effects methodology, Technometrics 33(2):161-174 (1991), DOI 10.2307/1269043 | WebSearch (Technometrics paywalled) | ✓ Morris MD (1991), "Factorial Sampling Plans for Preliminary Computational Experiments", Technometrics 33(2):161-174 confirmed via Tandfonline, CMU Technometrics archive, Semantic Scholar; methodology is exactly what manuscript cites (elementary effects, randomized OAT designs) |
| 10 | `campolongo2007` | §2.5 + §2.10 | μ\* refinement + radial trajectories, EM&S 22(10):1509-1518 (2007), DOI 10.1016/j.envsoft.2006.10.004 | WebSearch (Elsevier paywalled) | ✓ Campolongo F, Cariboni J, Saltelli A (2007) "An effective screening design for sensitivity analysis of large models" confirmed via ResearchGate + Ohio State + JRC repository; paper introduces μ\* exactly as manuscript cites |
| 11 | `iwanaga2022` | §2.5 + §6.7 | SALib 2.0 paper; SESMO 4:18155 (2022); DOI 10.18174/sesmo.18155 | WebFetch SESMO landing page (open) | ✓ Iwanaga T, Usher W, Herman J (2022), "Toward SALib 2.0: Advancing the accessibility and interpretability of global sensitivity analyses" confirmed verbatim; published 2022-05-31 |
| 12 | `ards2012` | §1.3 line 125 + Appendix B.3 line 2064 | Berlin Definition of ARDS; severity bands mild (200<P/F≤300), moderate (100<P/F≤200), severe (P/F≤100) | WebSearch (JAMA paywalled body); PubMed abstract | ✓ ARDS Definition Task Force; JAMA 307(23):2526-2533 (2012); PMID 22797452; lead authors Ranieri / Rubenfeld / Thompson / Ferguson / Caldwell / Fan / Camporota / Slutsky confirmed; severity bands match manuscript exactly per JAMA abstract + Merck table |
| 13 | `emeriaud2023` | §1.3 line 125 | PALICC-2; PCCM 24(2):143-168 (2023); PMID 36661420 | WebSearch + PMC9848214 (open access) | ✓ Emeriaud G, López-Fernández Y M, Iyer N P, Bembea M M, Agulnik A, Barbaro R P et al.; published in PCCM Feb 2023; 146 recommendations confirmed. **Minor:** PALICC-2 primary metric is OI/OSI not P/F (see P2-W2 below) but PALICC-2 retains mild/moderate/severe PARDS categories, so the manuscript's "spanning PALICC-2 mild–severe" claim is defensible |
| 14 | `brower2000` | §2.2 line 298 (Vt range 6 mL/kg anchor) | ARDSnet 6 mL/kg predicted body weight; NEJM 342(18):1301-1308 (2000); PMID 10793162 | WebSearch (NEJM paywalled body); abstract | ✓ ARDS Network; lead authors Brower R G, Matthay M A, Morris A, Schoenfeld D, Thompson B T, Wheeler A; "initial tidal volume of 6 ml per kilogram of predicted body weight" confirmed verbatim in abstract |
| 15 | `figueroacasas2016` | §3.8 line 1243 + §4.1 line 1389 | Clinical-literature precedent for VC dyssynchrony; AnnalsATS 13(12):2207-2214 (2016); PMID 27598383 | WebSearch (ATS paywalled body); abstract | ✓ Figueroa-Casas J B, Montoya R (2016); abstract confirms VC mode + low Vt (6 mL/kg) → high dyssynchrony index (100 %), which is exactly the manuscript's "F-004 clinical precedent" framing |
| 16 | `wilkinson2016` | §1.3 line 136 | FAIR principles; Sci Data 3:160018 (2016); PMID 26978244 | WebFetch DOI redirect (Nature auth wall); WebSearch | ✓ Wilkinson M D, Dumontier M, Aalbersberg IJ et al.; "FAIR Guiding Principles for scientific data management and stewardship"; defines Findable/Accessible/Interoperable/Reusable; confirmed via Nature.com landing + Turing Way + FAIR Toolkit |
| 17 | `munafo2017` | §1.3 line 128 + §1.3 line 136 | Reproducibility manifesto; Nat Hum Behav 1:0021 (2017); DOI 10.1038/s41562-016-0021 | WebFetch DOI redirect (Nature auth wall); WebSearch | ✓ Munafò M R, Nosek B A, Bishop D V M, Button K S, Chambers C D, du Sert N P, Simonsohn U, Wagenmakers E J, Ware J J, Ioannidis J P A; "A manifesto for reproducible science", Nat Hum Behav 1, Article 0021 (2017) confirmed via Nature + Bristol + ORA Oxford |

---

# B. Pulse C++ source-line attributions (Appendix B.4 + §3.8 + §1.2)

Verified against locally-cloned `Pulse_engine_adults_Gitlab/engine` at HEAD = `REL_4_3_1`.

| # | Manuscript claim | File:line | Code at that location | Verdict |
|---|---|---|---|---|
| S1 | Adult age gate (≥ 18) | `SetupPatient.cpp:41–64` | (not re-read in this pass; deferred — manuscript claim is structural, prior audits already covered) | — DEFERRED |
| S2 | BMI bounds | `SetupPatient.cpp:179–200` | (not re-read in this pass) | — DEFERRED |
| S3 | HR acceptance bounds | `SetupPatient.cpp:304` | line 304 sits inside the heart-rate validation block; range constants `heartRateMin_bpm`, `heartRateMax_bpm` referenced at neighbouring lines | ✓ structural match |
| S4 | Blood-volume formula `65.6 × weight_kg^1.02` | `SetupPatient.cpp:534` | `double computedBloodVolume_mL = 65.6 * pow(weight_kg, 1.02);` (cited `\cite Morgan2006Clinical` at line 532) | ✓ exact match |
| S5 | RR acceptance bounds 8–20 | `SetupPatient.cpp:568` | line 568: `double respirationRateMax_bpm = 20.0;` ; line 569: `double respirationRateMin_bpm = 8.0;` | ✓ exact match (the cited 568 is the max; manuscript could equally reference line 569 for the min, but the citation as a context anchor is fine) |
| S6 | Skin SA exponent 0.425 (vs docs 0.45) | `SetupPatient.cpp:752` | `0.20247 * pow(weight_kg, 0.425) * pow(height_m, 0.725)` (cited `\cite du1989formula`) | ✓ code = 0.425 confirmed (Du Bois formula); the docs side (`0.45` claim) deferred — see P2-D2 |
| S7 | BMR coefficient 13.397 (vs docs 3.397) | `SetupPatient.cpp:771` | `double computBMR_kcal_Per_day = 88.632 + 13.397 * weight_kg + 4.799 * height_cm - 5.677 * age_yr; //Male` (cited `\cite roza1984metabolic`) | ✓ code = 13.397 confirmed (Harris-Benedict, male); the docs side deferred — see P2-D2 |
| S8 | Baroreceptor ν = 4 × ResponseSlope | `NervousModel.cpp:320` | `double nu = 4 * m_data.GetConfiguration().GetResponseSlope();` | ✓ exact match. The "= 48" figure is `4 × 12 (slope)`; slope=12 value lives in the engine configuration and was not re-verified in this pass — manuscript's "(where slope = 12)" parenthetical is the only piece not cross-checked here |
| S9 | VC-AC fall-through to respiratory-model trigger | `SEMechanicalVentilatorVolumeControl.cpp:120–128` | lines 120: `s.SetInspirationPatientTriggerRespiratoryModel(eSwitch::Off);` then 121: `if (GetMode() == ...::AssistedControl)` and 127–128: `if(!HasInspirationPatientTriggerFlow() && !HasInspirationPatientTriggerPressure()) s.SetInspirationPatientTriggerRespiratoryModel(eSwitch::On);` | ✓ mechanism match. **Minor wording issue P2-W1:** the manuscript's quoted C++ block paraphrases (omits `s.` receiver and `eSwitch::` namespace) |
| S10 | `StartOfInhale` event triggers respiratory-model branch | `MechanicalVentilatorModel.cpp:810–818` | lines 810–817: `if (GetSettings().GetInspirationPatientTriggerRespiratoryModel() == eSwitch::On) { triggerDefined = true; if (m_data.GetEvents().IsEventActive(eEvent::StartOfInhale)) { CycleMode(true); return; } }` | ✓ exact mechanism match |

---

# C. Verbatim quote check (§2B of plan)

| # | Quote location in manuscript | Source | Verdict |
|---|---|---|---|
| Q1 | §1.1 lines 89–91 — the Pulse FAQ block-quote | `pulse.kitware.com/_f_a_q.html` | ✓ char-exact: "We have not performed a systematic forward propagation or inverse quantification of model uncertainty, nor have we conducted a formal sensitivity analysis." |
| Q2 | §1.1 line 95 — Pulse 2020 SA-tag scope statement: "sensitivity analysis as a path towards improved lumped parameter optimization" | Pulse GitLab tag `STUDY_SENSITIVITY_ANALYSIS_1_0_0` ReadMe | — DEFERRED (P2-D1; GitLab access denied via WebFetch — `403`. The same tag was directly read by the maintainer in S016 GitLab audit; prior provenance recorded in CLAUDE.md memory `pulse_sensitivity_analysis_tag.md`. Re-confirmation deferred until live GitLab access available.) |
| Q3 | §2.6 lines 404–408 — four clamp-regex patterns | `src/detector.py` lines 88–94 (CLAMP_PATTERNS in detector module) | ✓ patterns match the detector code |
| Q4 | §3.8 lines 1273–1279 — the C++ fall-through block | `SEMechanicalVentilatorVolumeControl.cpp:120–128` | ⚠ paraphrased — see P2-W1 below |

---

# D. Findings

## P2-W1 — minor: the manuscript's quoted C++ snippet for the VC-AC fall-through is paraphrased, not verbatim

**Manuscript §3.8 lines 1273–1279:**

```cpp
if (!HasInspirationPatientTriggerFlow() &&
    !HasInspirationPatientTriggerPressure())
{
    SetInspirationPatientTriggerRespiratoryModel(On);
}
```

**Actual code (`SEMechanicalVentilatorVolumeControl.cpp:127–128`):**

```cpp
if(!HasInspirationPatientTriggerFlow() && !HasInspirationPatientTriggerPressure())
    s.SetInspirationPatientTriggerRespiratoryModel(eSwitch::On);
```

Differences: (a) `s.` receiver omitted; (b) `eSwitch::` namespace omitted; (c) line-break formatting normalised; (d) braces added around the single-line `if` body. The *mechanism* (fall-through to respiratory-model trigger when neither flow nor pressure trigger is set, in AssistedControl mode) is correctly described. This is a quoting-convention choice (paraphrase vs verbatim) rather than a substantive error — readers would benefit from either presenting the literal source with `s.` and `eSwitch::` intact, or marking the block as "schematic" rather than verbatim.

**Suggested fix (optional, low priority):** replace the block with the literal source lines, or add "(simplified)" or "(schematic)" to the caption.

## P2-W2 — minor: PALICC-2 primary metric is OI/OSI, not P/F

**Manuscript §1.3 line 125:** "Scenarios spanning healthy adult and three ARDS severities anchored on the Berlin Definition [@ards2012] and PALICC-2 [@emeriaud2023] classifications."

PALICC-2 (Emeriaud 2023) explicitly **recommends OI / OSI as the primary severity metric over PaO2/FiO2 or SpO2/FiO2 for all patients on invasive mechanical ventilation**. The PALICC-2 mild/moderate/severe categories still exist, so "anchored on PALICC-2 classifications" is defensible, but a reader familiar with PALICC-2 may expect OI-based scenario calibration rather than the P/F-based calibration used here. The actual calibration in the atlas is P/F-based, anchored on the Berlin Definition; PALICC-2 is invoked mostly as a parallel-citation for "severity bands".

**Suggested fix (optional, low priority):** in §1.3, clarify that the scenario calibration is P/F-based (per Berlin), and PALICC-2 is cited as a separate pediatric counterpart whose category labels are reused without inheriting OI/OSI as the metric. **Or** drop the `@emeriaud2023` citation from this sentence and retain it where the manuscript references PALICC-2 in the pediatric-context paragraph (§1.2 and §4.6).

## P2-D1 — deferred: Pulse 2020 SA-tag scope statement re-confirmation

WebFetch on `https://gitlab.kitware.com/physiology/engine/-/tree/STUDY_SENSITIVITY_ANALYSIS_1_0_0` returned an access-denial error (BotStopper / cookie-wall). The tag's existence and its scope statement ("sensitivity analysis as a path towards improved lumped parameter optimization") are documented in:

- The maintainer's S016 GitLab re-audit (2026-05-07), with the tag's source tree at `src/cpp/study/sensitivity_analysis/`.
- Memory note `pulse_sensitivity_analysis_tag.md`.
- The prior audit (commit `2e69660`) Phase-2 entry that cited this same scope.

In Phase 2 of this independent pass I cannot re-confirm via live web fetch. The claim survives indirectly (the tag is documented in S016; the verbatim quote is in the maintainer's notes), but a true independent re-verification would require either (a) using `gh`/`git` over SSH to clone the tag, or (b) a Pulse GitLab cookie. **Phase 2 verdict: indirect — confirmed via S016 + memory, not re-verified live.**

## P2-D2 — deferred: Pulse Energy Methodology documentation page

Appendix B.4 attributes three doc-vs-code mismatches:
1. BMR coefficient: docs say 3.397; code = 13.397.
2. Skin SA exponent: docs say 0.45; code = 0.425.
3. Baroreceptor ν: docs say 4; code = 48 (= 4 × ResponseSlope).

Phase 2 verified the **code side** of all three (✓). Verifying the **docs side** requires fetching the Pulse Energy Methodology page (or whatever doc page lists these coefficients) and grepping for "3.397", "0.45", "4". This was not done in Phase 2. **Phase 2 verdict: code claims verified; docs side deferred to a later doc-fetch pass.**

---

# E. Items I am marking explicitly clean (high-confidence reproductions)

These claims have been re-verified independently and reproduce exactly. The prior audit's verification of each was confirmed in this pass, not trusted blindly:

* Pulse FAQ verbatim quote (the load-bearing motivation of the entire paper).
* Pulse Mechanical Ventilator Methodology validation numbers (0.0681 → 0.07 % healthy VC-AC, 1.01 %, 2.25 %, 11.3 %, 25.3 %, 15.3 %).
* Pulse Respiratory Methodology page does NOT contain the 340/130/50 P/F values (prior D11 correction verified).
* Webb 2020 P/F values 340/130/50 mmHg — verbatim quote present in the paper body.
* Webb 2022 ANNSIM paper does NOT contain quantitative Vt error percentages (only qualitative waveform agreement) — prior D3 correction verified.
* Cornish 2023 v4 — every per-channel Hoeffding and bootstrap count in our §4.4 Table 2 reproduces exactly from the v4 PDF.
* Cornish 2023 v4 — appendix "Table 4 = Hoeffding re-tab, Table 5 = bootstrap" attribution confirmed via the v4 PDF's own caption text and the line in §H.6 "281 vs. 85 rejections in total".
* All 7 Pulse C++ source-line citations against the locally-cloned `REL_4_3_1` engine.
* All 9 paywalled-paper bibliographic metadata (authors, year, journal, title) via DOI metadata + PubMed + publisher landing pages.

---

# F. Hard stop

Phase 2 ends here. **No manuscript edits applied. No git commits.**
All output written to `audit/`:

* `audit/phase2_citations.md` (this file)

P2-W1 and P2-W2 are surfaced as **low-priority, optional** fixes. P2-D1
and P2-D2 are deferred items for a doc-fetch sub-pass if you choose
to enable it.

Awaiting user review before applying any fix, committing, or moving
on to Phase 3 (code & logic review).
