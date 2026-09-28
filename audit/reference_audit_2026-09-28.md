# Reference audit — full pass on the 49 cited references (2026-09-28)

**Asked by the author (2026-09-28):** check the 49 references cited by
`preprint_npj/paper.tex` and `preprint_npj/supplement.tex` — that each is real
and correctly described, that it supports what it is cited for (source read, not
a summary), that it is cited in the right place, and that the paper and the
supplement use each reference for the same thing, without contradiction.

**Why now:** Methods §4.7 now states "Every cited reference was checked against
its source." That sentence is true only when this register is complete.

**Rules (autonomy pact):** a MISMATCH or OVERCLAIM is recorded here and brought
back for a joint decision; nothing in `paper.tex` / `supplement.tex` is changed
on the strength of this audit alone. A source that cannot be obtained is marked
`UNVERIFIABLE`, never replaced by a proxy. The earlier register
`audit/reference_audit.md` is used as a pointer to where to look, never as
evidence: every verdict below rests on a source opened on 2026-09-28.

## 1. Population

- Cited keys: **30** in `paper.tex`, **32** in `supplement.tex`, **49** distinct,
  all resolved in `preprint_npj/paper.bib` (54 entries, 5 retired with recorded
  reasons). Two instruments agree: `scripts/check_citations.py` and an
  independent extractor (session scratchpad `refs_extract.py`).
- Citation occurrences: **46** in the paper, **53** in the supplement (99).
- Paper and supplement share one bibliography (`paper.bib`).
- **The monograph does not cite the same set.** `preprint/manuscript.md` cites
  **34** keys from `preprint/references.bib` (39 entries): 31 shared with the
  submission, 18 submission keys absent from it (mostly the September
  additions), 3 monograph-only (`emeriaud2023`, `munafo2017`, `wilkinson2016`,
  retired from the submission with recorded reasons). For the 39 keys present in
  both bib files, the identifying fields (author, title, year, venue, volume,
  number, pages, DOI, URL) agree except two truncated author lists in
  `paper.bib` (`blanch2015`, `thille2006`: "and others" where the monograph
  lists more names) — not a contradiction.

## 2. Metadata against Crossref (the DOI registry's own record)

31 of the 49 carry a DOI; all 31 resolve. Positive control: a deliberately wrong
year on a copy of `morris1991` is flagged. Differences found:

| key | field | paper.bib | Crossref | reading |
|---|---|---|---|---|
| `ards2012` | title | "…: the Berlin Definition" | "Acute Respiratory Distress Syndrome" | Crossref drops the subtitle; to confirm on PubMed |
| `campolongo2007` | journal | `Environmental Modelling \& Software` | `…&amp;…` | encoding only |
| `mancia2023esh` | title | short title | adds "The Task Force for …" | subtitle only |
| `singer2016` | pages | 801--810 | 801 | Crossref gives first page; to confirm |
| `sinnige2026active` | title, pages | ": A Randomized Clinical Trial", 874--884 | no subtitle, 874 | to confirm |
| `ward2024ventilator` | pages | missing | 192-198 | **metadata gap** |
| `webb2022vent` | pages | missing | 282-293 | **metadata gap** |

The 18 without a DOI are checked by hand in §3.

## 3. Per-reference verdicts

Legend: **MATCH** the source says what we say · **OVERCLAIM** it supports
something weaker · **WRONG** it contradicts us · **UNVERIFIABLE** it could not be
obtained. "Read" states how much of the source was read.

_(filled reference by reference below)_

### `baird2020biogears` — **MATCH** (identity citation)
- Cited: paper L331, to name BioGears ("no comparable … atlas … has been
  published for either BioGears or HumMod").
- Source: JOSS PDF, joss.theoj.org, 4 pages, read in full. Title, five authors
  (Baird, McDaniel, White, Tatum, Marin), JOSS 5(56):2645, published
  14 Dec 2020 — all as in `paper.bib`.
- The citation only identifies the engine; the "no comparable atlas" half is a
  search result of ours, not something this source could support, and the
  sentence does not attribute it to the source. Placement correct.

### `bakkes2023asynchrony` — **MATCH**
- Cited: paper L339 (with `bikia2020aortic`): models "trained only on simulated
  data and tested on data from real patients … performed reasonably, though
  below models trained on such data".
- Source: Version of Record PDF (CC BY) from pure.tue.nl, read in full.
  Approach 3 = trained on the simulated dataset, tested on the clinical one
  (15 patients); Discussion: "even when the method is trained on only
  simulated data we still achieve a reasonable performance". Table 8 (read
  row by row; `pdftotext` shifts the row labels by one): approach 3 against
  approach 1 (trained and tested on clinical data), F1 74.3 vs 81.9 (DI),
  82.2 vs 92.0 (LC), 86.9 vs 87.3 (EC), 86.3 vs 91.7 (IE), 69.9 vs 80.8
  (normal); accuracy also lower for all five classes.
- Caution kept in mind: one centre, 15 patients, pressure support only; the
  sentence claims no more than that.

### `bikia2020aortic` — **MATCH**
- Cited: paper L339, same sentence.
- Source: Europe PMC full text (PMC7490416), read in full. "an SVR model was
  trained with the totality of the in-silico data (n = 4,018) and, then, was
  tested on the in-vivo data (n = 783)"; Table 11: RMSE 5.34 mmHg trained in
  silico vs 3.53 mmHg trained in vivo; "The aSBP predictions were found to be
  precise in the both investigated scenarios … The accuracy was slightly higher
  in the second scenario".
- Caution: only aortic systolic pressure was validated in vivo; the sentence
  says "aortic pressure estimation", which is what was tested.

### `blanch2015` — **MATCH in the paper; supplement wording AMBIGUOUS** → joint decision
- Cited: paper L286 ("a form of patient–ventilator dyssynchrony that is
  clinically undesirable"); supplement L740 ("…corresponding in a real patient
  to a shift from patient-responsive assist-control toward controlled
  ventilation --- clinically undesirable").
- Source: peer-reviewed post-print, arts.units.it (institutional repository),
  read in full; metadata ICM 41(4):633–641, 2015, as in `paper.bib`. Title:
  "Asynchronies during mechanical ventilation are associated with mortality".
  Table 2: AI > 10 % → ICU mortality 67 % vs 14 %, hospital 67 % vs 23 %.
  Discussion: "the AI is associated with mortality, although further studies
  are needed to know whether an elevated AI is an indicator of severity or
  constitutes a biomarker…". Also: "By definition, no asynchrony occurs during
  controlled ventilation in patients paralyzed or without spontaneous
  ventilation".
- **Finding.** The paper attaches "clinically undesirable" to the dyssynchrony,
  which the source supports (association with mortality; the source does not
  claim causation and neither does the paper). The supplement's dash clause
  sits right after "a shift … toward controlled ventilation" and can be read
  as calling that shift undesirable, which the source does not address.
  Suggested alignment (not applied): mirror the paper's order —
  "a form of patient–ventilator dyssynchrony~\cite{thille2006} that is
  clinically undesirable~\cite{blanch2015}, corresponding in a real patient to
  a shift …". Needs the author's decision (wording of a clinical statement).

### `thille2006` — **MATCH**
- Cited: paper L286 and supplement L740: sub-threshold efforts left
  unrewarded are "a form of patient–ventilator dyssynchrony".
- Source: full text via Firecrawl (Springer PDF), read: abstract, introduction,
  results headings. "ineffective triggering occurs when the patient's
  inspiratory effort fails to trigger a ventilator breath"; it is one of the
  two main asynchrony patterns and is "associated with a less sensitive
  inspiratory trigger" — the exact mechanism of a fixed −2 cmH₂O threshold.
  Assist-control was one of the two studied modes. ICM 32(10):1515–1522, 2006.
- Paper and supplement use it identically.

### `nin2017` — **MATCH**
- Cited: supplement L233: "1,899 patients across 927 ICUs in 40 countries …
  categorised the maximum PaCO₂ recorded in the first 48 h …; its cutoffs place
  approximately the 95th percentile at 70 mmHg".
- Source: PMC5630225 full text (via Firecrawl), read in full. "We included
  1899 patients with ARDS"; "ARDS patients from 927 intensive care units
  (ICUs) in 40 countries"; "Maximum PaCO2 in the first 48 h … was categorized
  into six groups (<30, 30–39, 40–49, 50–59, 60–69, and >70 mmHg); the cutoffs
  corresponded approximately to the 5th, 35th, 70th, 85th, and 95th
  percentiles". Supplement only.

### `brower2000` — **MATCH (L227); WEAK SUPPORT on the Vt drift row (L274)** → joint decision
- Source: NEJM full text via Firecrawl, read in full; 342(18):1301–1308.
  Predicted body weight, verbatim: "50 + 0.91(centimeters of height – 152.4)"
  (men), "45.5 + 0.91(…)" (women); lower-tidal-volume arm "reduced to 6 ml per
  kilogram of predicted body weight"; delivered "6.2 ± 0.8 … ml per kilogram of
  predicted body weight" on days 1–3 (SD across patients).
- L227 (Vt upper bound): "6 mL/kg PBW ≈ 450 and 330 mL on the male and female
  reference bodies". Recomputed with the source's formula: 180 cm → 75.12 kg →
  450.7 mL; 163 cm → 55.15 kg → 330.9 mL. **MATCH.**
- L274 (Table of drift thresholds, Vt 50 mL / 60 s): "Approximately
  0.7–0.9 mL/kg ideal body weight … — within the noise band of breath-to-breath
  Vt measurement at ARDS Network protective ventilation (6 mL/kg predicted body
  weight)~\cite{brower2000}". The arithmetic holds (50/75.1 = 0.67;
  50/55.1 = 0.91). **But the source says nothing about breath-to-breath
  measurement noise**; it supports only the 6 mL/kg target. The neighbouring HR
  and SpO₂ rows say honestly "A preregistered convention, not a sourced
  threshold"; this row reads as sourced when its key clause is not. Also
  "ideal body weight" and "predicted body weight" name the same quantity twice
  in one sentence. Suggested (not applied): present it like the HR/SpO₂ rows —
  a preregistered convention, 0.7–0.9 mL/kg PBW on the two bodies, small next
  to the 6 mL/kg protective target~\cite{brower2000}.

### `evans2021sepsis` — **MATCH** (both uses)
- Source: Crit Care Med full text (journals.lww.com, via Firecrawl), 58,000
  words; 49(11):e1063–e1143. Recommendation 9: "we recommend an initial target
  mean arterial pressure (MAP) of 65 mm Hg over higher MAP targets".
  Rationale: "MAPs below a threshold, usually understood to be approximately
  60 mm Hg, are associated with decreased organ perfusion, which tracks
  linearly with MAP".
- Supplement L225 ("initial MAP target of 65 mmHg") and L272 ("targets 65 mmHg
  on resuscitation, and organ perfusion declines below approximately 60 mmHg,
  tracking linearly with MAP") both say what the source says. The earlier
  register's two findings (superseded "≥ 65"; drift threshold resting on it)
  no longer apply to the current text: the 5 mmHg step is now stated as our
  own inference from landmarks the sources do give.

### `singer2016` — **MATCH**
- Source: Version of Record PDF (Amsterdam UMC repository), read in full;
  JAMA 2016;315(8):801–810 (Crossref gives only the first page).
- Table 1 (SOFA), cardiovascular row: 0 = MAP ≥ 70 mm Hg, 1 = MAP < 70 mm Hg.
  Supplement L225 and L272 ("registers organ dysfunction below 70 mmHg") agree.

### `mancia2023esh` — **MATCH**
- Source: J Hypertens full text (journals.lww.com, via Firecrawl), 173,000
  words; 41(12):1874–2071. Read: the classification table and §16.2
  (hypertensive urgencies and emergencies).
- "Hypertension emergencies are conditions in which severe hypertension
  (grade 3) is associated with acute symptomatic HMOD"; grade 3 = SBP ≥ 180
  and/or DBP ≥ 110. Supplement L225 says exactly this.

### Pulse documentation pages (9 keys) — fetched live from pulse.kitware.com on 2026-09-28, and every quoted sentence re-found in the v4.3.1 sources (`git grep` at tag `REL_4_3_1`, local clone `Pulse_engine_adults_Gitlab/engine`, `docs/`)

| key | claim in paper / supplement | source, verbatim | verdict |
|---|---|---|---|
| `pulsefaq` | paper L146 quote; paper L331 "no formal sensitivity or uncertainty quantification … on user-facing operational inputs"; supp L129 "about 5–10× real time"; supp L154 table source | "We have not performed a systematic forward propagation or inverse quantification of model uncertainty, nor have we conducted a formal sensitivity analysis"; "about 5 to 10 times real time, depending on your machine's specifications" (FAQ.md at REL_4_3_1) | **MATCH** (L331 narrows the statement to operational inputs, which the broader statement entails) |
| `pulseabout` | supp L129: C++ with bindings for Java, C#, Unity; deploys on Windows, Mac, Linux, ARM | "easy cross-platform deployment on all standard operating systems (Windows, Mac, Linux, and ARM) and multiple languages (C++, C#, Java, Unity)" (About.md) | **MATCH** |
| `pulsesystem` | supp L131: fixed time step 0.02 s (50 Hz), every state recalculated; supp L135 quotes | "transient analysis time step of 0.02 s (50 Hz). All system states are recalculated every time step"; "The engine uses a low fidelity clinical approach and is not necessarily for high fidelity predictive purposes" (SystemMethodology.md) | **MATCH** — minor: the clause after the citation in L135, "intended for training simulation rather than patient-specific clinical prediction", is our gloss; no Pulse page states an intended use (About lists none; Pulse in Action shows training *and* research uses) |
| `pulsecircuit` | supp L131: paths with idealised elements, non-linear networks, one generic solver for all systems | "Paths are ideal conductor branches that may contain elements (i.e., resistors, capacitors, inductors, diodes, etc.)"; "DC transient analysis must be performed on nonlinear networks"; generic solver "Leverageable by all physiological systems" | **MATCH** |
| `pulserespmethod` | paper L347 + supp L129: 5-compartment lung (carina, L/R dead space, L/R alveoli); supp L131: severity on [0,1], piecewise-linear, nodes 0.0/0.3/0.6/0.9/1.0; supp L172 (limitations row 11): no inertance, linear resistance only, idealised valves | "five major functional units, or compartments, … the carina, right and left anatomic dead space, and right and left alveoli"; "piecewise linear functions, calibrated at key transition points: 0.0 …, 0.3 (mild), 0.6 (moderate), 0.9 (severe), and 1.0"; "Inertance is not included in the model"; laminar Ohm's-law flow assumed | **MATCH** — minor placement: "idealised valves" in row 11 is a *cardiovascular* statement ("The engine uses ideal valves", CardiovascularMethodology); row 11 cites only `pulserespmethod`. Adding `pulsecardiomethod` to row 11 would source it |
| `pulsecardiomethod` | supp L174 (row 12): no dicrotic notch, no retrograde flow, P and T waves merge at high HR | "This is the dicrotic notch … This is not currently being modeled in the engine"; "We assume the valves are perfect Booleans … a small amount of retrograde flow may be present" (not modelled); "Due to the high heart rate, the engine output is summing together the P and T waves" | **MATCH** |
| `pulsepatientmethod` | supp L131: allometric baselines bounded by hard limits; supp L812: BV = 65.6·W^1.02 mL | Table 1: "Bv[mL] = 65.6W[kg]^1.02", lower bound "Bv * 0.85", upper "Bv * 1.15" (PatientMethodology.md, identical at REL_4_3_1) | **MATCH** |
| `pulsevent` | supp L164 (row 7): PC-AC deviates 11.3–25.3 % across healthy / restrictive / obstructive, VC-AC 0.07–2.25 %, per Pulse's validation tables | Tables 3/10/17 (VC-AC, mode read from Tables 2/9/16): 0.0681 %, 1.01 %, 2.25 %; Tables 5/12/19 (PC-AC, Tables 4/11/18): 11.3 %, 25.3 %, 15.3 %; the CPAP rows (15.9/35.7/13.5 %) are correctly left out | **MATCH** — caveat: the numeric tables are inserted at documentation build time (`@insert ./test_results/tables/…`), so they cannot be re-derived from the tag; what was read is the live page, labelled "v4.3.1 documentation" in `paper.bib`. REL_4_3_2 changed no physiology |
| `pulseinaction` | paper L142: education and simulation training on virtual-patient and emergency-medicine platforms; paper L327: named training products presenting learners with real-time physiological and pharmacological data | VRescue, "The VR training simulation for emergency medicine"; SimPulse "presenting healthcare learners with real-time, physiological and pharmacological patient data" | **MATCH** |

### `bray2019` — **MATCH as the engine's reference; two weak uses in the supplement** → joint decision
- Source: the author-supplied PDF in `local_sources/` (not open access), read
  in full; SN Compr Clin Med 1:362–377, 2019.
- MATCH: paper L142 (Pulse is an open-source, Apache-2.0 whole-body simulator;
  "general-purpose computational physiology"), paper L347 (the engine used).
  Verbatim: "The Pulse Physiology Engine is a fork of BioGears. It was created
  by the original developers of BioGears"; "BioGears is a Department of
  Defense program"; "a permissible Apache 2.0 license".
- **Weak 1 — supplement L129 "an interface for Python~\cite{bray2019}".** The
  only "Python" in Bray 2019 is the list of languages Google Protocol Buffers
  supports (data serialisation), not an interface to the engine. A direct
  source exists in the audited set: `webb2022vent` — "provides bindings to
  various popular programming languages including C, C#, Java, and Python".
- **Weak 2 — paper and supplement do not say the same thing.** Paper L142:
  Pulse "is one such actively maintained open-source whole-body simulator";
  supplement L129: "among the **most** actively maintained". Neither half is
  something a 2019 paper can attest for 2026, and the comparative "most" has
  no source anywhere in the audited set. Aligning the supplement on the
  paper's wording removes the difference.
- **Uncited sentence next to it — supplement L133.** "Pulse was forked in 2017
  from the U.S. Department of Defense–funded BioGears engine by the original
  BioGears core developers (Clipp, Bray, Webb) and is now maintained by
  Kitware, Inc. under the Apache-2.0 license." No citation. `bray2019` supports
  the fork, the original developers, the DoD origin and Apache-2.0; it gives
  neither the year 2017 nor the three names as "the original core
  developers". Options: add `\cite{bray2019}` and drop "in 2017" and the names,
  or find a source for both.

### `webb2020` — **MATCH**
- Source: Europe PMC full text (PMC7688119), read in full; PLoS One 2020.
- Paper L142 ("ventilator-safety what-if analysis") and L144, every detail
  checked: "12,642 unique patient and ventilator combinations"; parameter
  space = static compliance 10–50, DIF 0.3–0.9, PEEP 10–20; respiratory rate
  "Fixed at 20", I:E "Fixed at 1:2", resistance "Fixed at 5"; "Two equal-sized
  70 kg patients are modeled"; pressure-mode ventilation (PIP derived); a
  green/yellow/red composite score; outcome "most closely correlated to lung
  compliance, oxygenation index…".

### `webb2022vent` — **MATCH**; supplement L164 slightly understates it; metadata gap
- Source: PMC author manuscript (PMC10224749, via Firecrawl), read in full.
- Paper L142/L144 MATCH: "Proper functionality was validated by simulating the
  same patient pathophysiology and ventilator settings virtually in Pulse as a
  physical lung simulator and ventilator setup" (ASL 5000 + Dräger V500).
- Supplement L164: "that paper reports qualitative ASL-5000 waveform agreement,
  not these quantitative percentages". Its text is qualitative ("match well",
  "good agreement") and gives no percentage errors, but Figure 7 carries a
  table per run (RR, Pmean, TV) and the text notes "Discrepancies with the TV
  outputs for the PC-AC and CPAP modes". Not wrong; "qualitative" is a little
  narrower than the paper. Low priority.
- `paper.bib` lacks the pages (Crossref: 282–293).

### `ward2024ventilator` — **MATCH**; metadata gap
- Source: arXiv:2411.07971v1 (the authors' version of the CBMS 2024 paper; the
  IEEE version is closed), read in full.
- Paper L142 / L341 and supplement L191: a ventilator-management MDP "built on
  top of the Pulse Physiology Engine", Pulse used to "benchmark, gather
  simulated data", neural networks learning the dynamics; action vector of
  **6** settings — "FiO2, inspiratory pressure (Pinsp), inspiratory time
  (Tinsp), respiratory rate (RR), positive end-expiratory pressure (PEEP), and
  slope" — so pressure-targeted, and FiO₂/RR/PEEP are the three the atlas
  sweeps. All three uses agree.
- `paper.bib` lacks the pages (Crossref: 192–198).

### `hester2011hummod` — **MATCH** (identity citation)
- Source: Europe PMC full text (PMC3082131), read; Front Physiol 2:12, 2011,
  seven authors. Cited once (paper L331) only to name HumMod.

### Methods and software (4 keys) — **MATCH**
| key | use | source (read 2026-09-28) | verbatim |
|---|---|---|---|
| `herman2017salib` | paper L363, SALib generated the sample | JOSS PDF, full (2 pages) | "SALib contains Python implementations of commonly used global sensitivity analysis methods, including … Morris (Morris 1991, Campolongo, Cariboni, and Saltelli (2007))" |
| `iwanaga2022` | same sentence | SESMO article page (title, authors, abstract; via Firecrawl; the host timed out on direct download) | "Toward SALib 2.0: Advancing the accessibility and interpretability of global sensitivity analyses", SESMO vol. 4, 2022 — identity citation for the software version line |
| `lundberg2017` | supp L1007, SHAP named | NeurIPS 2017 proceedings PDF, full | "SHAP (SHapley Additive exPlanations)" |
| `lundberg2020tree` | supp L1011, TreeExplainer computes SHAP exactly for trees, not by sampling | PMC7326367 (via Firecrawl), full | "computes local explanations based on exact Shapley values in polynomial time"; model-agnostic methods "suffer from sampling variability" |

### `cornish2023` — **MATCH**; one wording difference inside the paper
- Source: JMLR PDF (27(152):1–52, 2026, confirmed on the JMLR landing page),
  read in full; tables read with `pdftotext -raw` because `-layout`
  interleaves them. JMLR prints each caption *below* its table, so the rows
  above "Table 4" are the Hoeffding table: Chloride 24, Sodium 21, Potassium 13,
  Temp 10, Calcium 5, Glucose 5, paCO2 3, HCO3 2, SysBP 2, and 0 for paO2, pH,
  DiaBP, MeanBP, RR, HR — **15 quantities, 85 rejections** (the text: "281 vs.
  85 rejections in total" for bootstrap vs Hoeffding). Multiple testing: "the
  method of Holm (1979) (which we use in our case study)". MIMIC-III, Sepsis-3
  cohort.
- Paper L333 (85; 82 outside HR/MAP/PaO₂/PaCO₂; 80 on unassessed channels; 2
  on SysBP; 3 on the four) and supplement L647 (80 of 85; Table 4 Hoeffding,
  Table 5 bootstrap, Holm–Bonferroni) all re-derive from the table.
- Minor: the paper names the same channel group twice differently — L146
  "electrolyte, metabolic, acid–base and **dermal** outputs", L333 "chemistry
  and **thermoregulation** outputs". The quantity is skin temperature;
  "thermoregulation" (or "skin temperature") is the more accurate of the two.

### `deepseek2026v41flash` — **MATCH** (technical report, not peer reviewed; the paper says "technical report")
- Source: the PDF at the pinned Hugging Face commit, read (abstract, §5.1).
- L140: "a multimodal Mixture-of-Experts (MoE) model"; "under a fixed and
  unremarkable optimization procedure, systematic improvements in the scale,
  diversity, and verifiability of synthesized data and environments account
  for essentially all of the observed gains" — the paper's "most of the gains"
  is weaker than the source, so on the safe side.
- L327: "We formalize each task as a triplet (problem, environment,
  verification system)".

### `hwang2025sim2real` — **MATCH**
- Source: PMC12531325, read in full; npj Digit Med 2025.
- L140: pre-training "on virtual patient data generated by the UVA/Padova
  simulator"; simulated scenarios include "adverse and infrequent conditions …
  often underrepresented in real-world datasets"; "model performance was
  ultimately evaluated on real-world datasets".
- L339: "assessing the distributional shifts between training and external
  datasets. Kullback–Leibler (KL) divergence was computed".

### `katsoulakis2024digitaltwins` — **MATCH**
- Source: PMC10960047, read in full (scoping review, npj Digit Med 2024).
- L140: "requires access to longitudinal data. This data is often scarce and
  may have gaps"; "Inaccurate or incomplete data can lead to incorrect digital
  twin representations".

### `viceconti2021insilico` — **MATCH**
- Source: PMC7883933, read in full (Methods 2021).
- L325: credibility rests on "verification, validation (including uncertainty
  quantification), and applicability"; "A second element of validation is the
  degree to which sensitivities and uncertainties of the computational model …
  are understood"; applicability = "the range for the model input parameters
  that characterize or bound the validation activities"; "there is no
  validation in the absence of comparator data".

### `kuczmarski2002cdc` — **MATCH on the values** (against the CDC data files); report not re-opened
- Cited: paper L353, supplement L309 ("50th-percentile weight-for-age values
  … taken from the CDC row at Agemos = 216.5"), L311 (female height = CDC P50).
- Source today: the CDC growth-chart data files `wtage.csv` and `statage.csv`
  (cdc.gov, via Firecrawl; direct download returned 403). Row sex 1,
  Agemos 216.5: P50 = 67.28992603 kg; sex 2: 56.22969564 kg → 67.3 and
  56.2 kg. Stature, sex 2, Agemos 216.5: P50 = 163.1307866 cm → 163 cm.
- Report metadata confirmed at PubMed (Vital Health Stat 11(246):1–190, May
  2002). The 190-page report itself was not re-opened today (403). The
  "Agemos" row is the data file's label; the report's own tables label the
  same numbers differently (earlier register, 2026-07-26), so the data file is
  what a reader should open. Suggestion, low priority: cite the data file's
  URL next to the report.

### `sinnige2026active` — **MATCH**
- Source: PMC12687210 full text (via Firecrawl; PubMed gives the PMCID), read
  in full; JAMA 2026;335(10):874–884.
- Paper L341: "a recent multicentre randomised trial of closed-loop
  ventilation improved overall ventilation quality yet showed no difference in
  patient-centred outcomes". Source: 7 ICUs, Netherlands and Switzerland;
  ventilator-free days 16.7 vs 16.3 (P = .23); "There were no differences in
  secondary outcomes except for ventilation quality, which was higher with
  closed-loop". (The authors add that the quality outcome "should also be
  interpreted cautiously"; the sentence does not lean on it.)

### Checked today at abstract depth only (full text closed) — what the abstract settles, and what it does not
| key | abstract settles | still needs the full text |
|---|---|---|
| `ards2012` (PubMed 22797452) | the three bands: mild 200 < P/F ≤ 300, moderate 100 < P/F ≤ 200, severe ≤ 100 — paper L164, supp L231/L481 | "at PEEP ≥ 5 cmH₂O" (paper L164) is in the definition table, not in the abstract. Also supp L278 (PaO₂ drift row): "15–71 % of one Berlin P/F band" re-derives (15/1.0 = 15; 15/0.21 = 71.4; band width 100) but "clinically meaningful oxygenation change over a 60-second window~\cite{ards2012}" is our judgement, not the source's — same pattern as the `brower2000` Vt row |
| `severinghaus1979` (PubMed 35496) | the abstract prints Eq. 1, S = ((23,400/(PO₂³ + 150·PO₂)) + 1)⁻¹. Recomputed: S(27) = 0.5035, S(20) = 0.3198 → supp L229 ("SpO₂ = 50 % at PaO₂ ≈ 27") and L231 ("≈ 0.32") **MATCH** | nothing for these two uses |
| `akoumianaki2014` (PubMed 24467647) | "clinicians rely mostly on Paw and flow waveforms. However, these measurements may mask profound patient-ventilator asynchrony and do not allow respiratory muscle effort assessment" → supp L740 **MATCH** | nothing essential |
| `figueroacasas2016` (PubMed 27598383) | "Lower Vts during VC ventilation result in higher patient-ventilator dyssynchrony" → paper L284, supp L740 (×2) **MATCH** | nothing essential |
| `roza1984metabolic` (PubMed 6741850) | the revision of the Harris–Benedict equations exists (additional Benedict subjects, n = 98) | the constant **88.362** (supp L867) is on p. 171, not in the abstract. Pulse side verified today in the v4.3.1 code: `SetupPatient.cpp:771` = `88.632 + 13.397·W + 4.799·H − 5.677·A`, with `\cite roza1984metabolic` |
| `campolongo2007` (ScienceDirect abstract, via Firecrawl) | elementary-effects screening, revised measure and sampling, set against "local analyses varying one factor at a time around a baseline point", "lower computational cost" | "cost linear in the number of inputs" (paper L363) is in the body |
| `vanbreugel2024synthetic` (nature.com abstract + key points + reference list) | paper L140 **MATCH**: "generative-model-based data augmentation can address data scarcity; synthetic data can improve data fairness … by accounting for underrepresented groups; and unseen scenarios may be simulated"; key point "Synthetic data is generated by deep generative models or mechanistic simulators"; the reference list cites Bray 2019 (ref. 19) and Webb 2020 (ref. 20) | *where* Pulse is presented as "an example of a mechanistic generator" (paper L142) is in the body |
| `victoriano2026sim2real` (nature.com abstract) | paper L140, in substance: "multilayered validation frameworks … hybrid validation … an essential step towards digital twins" | the **five-stage** scheme named stage by stage in paper L325 is in the body |

### Not verifiable today — no text obtainable
| key | why | earlier record |
|---|---|---|
| `morris1991` | Technometrics (T&F) — the page returned 25 words | **never read at source** (earlier register: "metadata only") |
| `sinderby1999` | Nat Med, closed; PubMed has no abstract | earlier register: full text, MATCH |
| `nadler1962` | Surgery 1962; the PTAB exhibit copy is no longer on the machine | primary scan read 2026-07-26; verbatim range and equations recorded in `paper.bib`. Recomputed today from those equations: 72.96 and 63.78 mL/kg — supp L834's 73.0 and 63.8 |
| `west2020respiratory`, `marino2013icu`, `marini2018critical` | textbooks; the supplied copies are no longer on the machine | read in primary text 2026-07-27 (chapter titles and verbatim fragments in `paper.bib`) |

### Update, same evening — full texts supplied by the author in `local_sources/`
Identity of each file confirmed on its own title / masthead page before use.
An extra file, `jlt120134_1321a_1322.pdf`, is a JAMA letter-and-reply about the
Berlin Definition; it is not a cited reference and was not used.

| key | file (identity) | verdict | verbatim |
|---|---|---|---|
| `morris1991` | `Morris-FactorialSamplingPlans-1991.pdf` — JSTOR cover: Technometrics 33(2):161–174, May 1991 | **MATCH** (first reading at source ever) | "individually randomized one-factor-at-a-time designs"; "a design in which the number of runs is proportional to k (rather than k²)"; "a total number of runs, which is a linear function of k"; base value "randomly chosen", r "random orientations". "Global" is not Morris's word; the design samples the whole region of experimentation, which is what the label means |
| `campolongo2007` | `1-s2.0-S1364815206002805-main.pdf` — EMS 22 (2007) 1509–1518 | **MATCH** | "r trajectories of (k+1) points in the input space, each providing k elementary effects … The total cost of the experiment is thus r(k+1)"; "individually randomised OAT experiments"; set against local OAT "around a baseline point" |
| `ards2012` | `jsc120003_2526_2533.pdf` — JAMA 2012;307(23):2526–2533 | **MATCH** (PEEP condition now read) | Table 3: Mild 200 < PaO₂/FiO₂ ≤ 300 "with PEEP or CPAP ≥ 5 cm H2O"; Moderate 100 < … ≤ 200 "with PEEP ≥ 5"; Severe ≤ 100 "with PEEP ≥ 5" (the ≤/≥ glyphs are lost by `pdftotext`; the abstract prints them). The L278 finding (our "clinically meaningful" judgement placed before the citation) stands |
| `roza1984metabolic` | `1-s2.0-S0002916523243592-main.pdf` — "The American Journal of Clinical Nutrition 40: JULY 1984, pp 168-182" | **MATCH** | Equation 3 (men, n = 168): "REE = 88.362 + 4.799 (ht) + 13.397 (wt) − 5.677 (age)", printed twice; Equation 6 (women): 447.593 + 3.098 ht + 9.247 wt − 4.330 age; 1919 originals: Equation 1 = 66.473 …, Equation 4 = 655.096 … — supp L181 and L867 exact; Pulse's female equation is identical, its male intercept 88.632 |
| `sinderby1999` | `nm1299_1433-1.pdf` — Nature Medicine 5(12), Dec 1999, p. 1433 | **MATCH** | Fig. 1b: "the onset of inspiratory effort, indicated by the beginning of diaphragmatic electrical activity … and the negative deflection in esophageal pressure"; "a completely wasted inspiratory effort where the patient effort failed to trigger the ventilator" |
| `vanbreugel2024synthetic` | `Synthetic-data-in-biomedicine-via-generative-artificial-intelligence.pdf` — Nat Rev Bioeng, DOI 10.1038/s44222-024-00245-7 | **MATCH** (both uses) | Box 2 "Mechanistic and hybrid simulators": "interacting physiological models can be applied to study whole-body responses to diseases and injuries" with ref. 19 = Bray et al., *Pulse physiology engine* — paper L142 |

| `victoriano2026sim2real` | `s42256-026-01244-6-1.pdf` (deposited later the same evening) — Nat Mach Intell 8, June 2026, 866–879, Perspective, six authors as in `paper.bib` | **MATCH** (both uses) | Paper L325: "we propose a five-stage validation method …: (1) Stage 1: internal plausibility … (2) Stage 2: downstream task utility … (3) Stage 3: OOD generalization … (4) Stage 4: sim2real transfer … (5) Stage 5: biological or clinical coupling". Paper L140: "The value of synthetic data will likely depend less on generation alone and more on careful integration with real-world data, layered validation and digital twin systems" — **minor: our sentence is a near-verbatim paraphrase (about twenty words in the source's order) without quotation marks**; consider quoting it or rewording |

Still not obtainable, as of this update: `nadler1962`, `west2020respiratory`,
`marino2013icu`, `marini2018critical`.

## 4. Status of the Methods §4.7 sentence

"Every cited reference was checked against its source." — **state after the
author's deposit (same evening), by depth of reading on 2026-09-28** (unit:
cited key; denominator 49):

| depth today | n | keys |
|---|---|---|
| full text (or, for the 173,000-word ESH guideline and the DeepSeek report, the full relevant sections) | **40** | all others (incl. `victoriano2026sim2real`, deposited last) |
| the part of the source that carries the cited fact, and only that | **5** | `severinghaus1979` (abstract prints the equation used), `akoumianaki2014` and `figueroacasas2016` (abstract states the cited finding), `iwanaga2022` (article page: identity citation), `kuczmarski2002cdc` (the CDC data files the values come from; report identity via PubMed) |
| not re-opened today | **4** | `nadler1962`, `west2020respiratory`, `marino2013icu`, `marini2018critical` (read at source in July 2026, extracts in `paper.bib`) |

`morris1991` is now read at source for the first time. Two keys have never
been read in full at any date: `akoumianaki2014` and `iwanaga2022`; for both,
the cited use is carried by the part that was read.

So the §4.7 sentence holds in the sense "every cited claim was checked against
its source" (full text, or the part of the source stating it), provided the
four not re-opened today count on their recorded July extracts.
Stated plainly for the author to decide.

(Earlier state of this section, kept for the record: before the deposit,
`morris1991` had never been read at source, and five others rested on
passages outside their abstracts.)

Two ways to close it: obtain the texts (author's institutional access, or PDFs
deposited in `local_sources/`), or state the scope honestly in §4.7. Decision
pending with the author; nothing is built until then.

## 6. Applied on the author's decision (2026-09-28); built the same day (npj 14:00, monograph 14:00), committed with this register

The author approved findings 1, 3, 4, 5, 6a, 6b, 7, 8, 9 and left 2 and 6c
alone; plus one clause in Methods §4.6 on why Morris. Each edit was
double-checked before writing, and the same defect was fixed in every public
copy (paper, supplement, monograph) per the rule "a decision holds for all
copies".

| # | paper / supplement | monograph mirror |
|---|---|---|
| Morris | paper §4.6: "…whose cost is linear in the number of inputs, so that the same runs both map where the engine fails across the envelope and rank which inputs drive each output." | — (not requested) |
| 1 | supp L740: "a form of patient--ventilator dyssynchrony~\cite{thille2006} that is clinically undesirable~\cite{blanch2015}, corresponding in a real patient to a shift … toward controlled ventilation; such dyssynchrony is detectable on …" — every element of the M.S.-validated caveat kept | same reordering at the §4.2 caveat |
| 3a | supp L129: Python → `\cite{webb2022vent}` | same (`[@webb2022vent]`) |
| 3b | supp L129: "is an actively maintained open-source whole-body human physiology simulator" | already "an actively maintained" |
| 4 | supp L133: "by members of the original BioGears team", `\cite{pulseabout,pulsefaq}` added; "in 2017" kept — Pulse's own release notes date v1.0.0 "September 2017" (`docs/Markdown/Versioning.md` at REL_4_3_1) and the repository's first commit is 2017-04-19 | the monograph's own fork sentence was uncited too: `[@pulseabout; @pulsefaq]` added |
| 5 | supp row 11: `\cite{pulserespmethod,pulsecardiomethod}` | no such row |
| 6a | supp L135: clause "intended for training simulation rather than patient-specific clinical prediction" removed | the monograph attributed that intent to the maintainers themselves; replaced by the two verbatim quotations the page does contain |
| 6b | paper L333: "chemistry and dermal outputs" | "chemistry-and-dermal" |
| 7 | **corrected finding**: `ward2024ventilator` already carried its pages inside `howpublished` ("pp. 192--198"); my Crossref check compared only the `pages` field — a false positive. Only `webb2022vent` changed: ", pp. 282--293" appended to `howpublished` | same in `references.bib` |
| 8 | paper L140: the source's sentence now quoted verbatim ("the value of synthetic data will likely depend less on generation alone and more on careful integration with real-world data, layered validation and digital twin systems") — string-compared to the PDF text, with a one-word-changed control that fails as it should | not cited in the monograph |
| 9 | supp row 10: `\cite{pulserespmethod,pulsepatientmethod}` | no such row |

Gate after the edits, without a build: `audit_claims.py` 0 FAIL/WARN in all four
variants; `check_citations` 30 / 32 / 49 keys, gate passed; `check_stale_counts`,
`check_backrefs`, `check_input_ranges`, `check_pair_counts`,
`check_figure_freshness`, `check_publication_gate` exit 0; pytest 80 passed;
ruff clean. Old wordings re-searched in paper, supplement, monograph and README:
0 each, with a positive control on the new wording.

## 5. Findings for joint decision — double-checked the same night (now applied, see §6)

Each finding was re-checked against the source and against the git history of
the sentence (`git log -S`), so that no earlier decision is undone unknowingly.

1. **`blanch2015`, supplement L740 — confirmed, with context.** The caveat was
   written from M.S.'s clinical interpretation and validated by M.S. (commit
   `89fe865` records the caveat's elements as clinician-validated, including
   the "shift toward controlled ventilation"). The clinical content stands; only the citation
   placement is at issue: Blanch supports "dyssynchrony … clinically
   undesirable", not "a shift toward controlled ventilation … clinically
   undesirable". Suggested: keep every element of M.S.'s sentence and move
   "clinically undesirable~\cite{blanch2015}" onto the dyssynchrony, as the
   paper already does.
2. **Drift-rationale rows (Vt L274, PaO₂ L278) — DOWNGRADED to minor.** The
   table caption already says "The citations frame that monitoring context
   rather than endorse the specific magnitudes, which are atlas-internal
   calibration choices", and the S3.5 text says the same (commit `22c284c`).
   Residual only: "within the noise band of breath-to-breath Vt measurement"
   is an unsourced characterisation. Optional.
3. **`bray2019`, supplement L129 — confirmed on both halves.**
   (a) Bray 2019 names Python once, in the list of languages Protocol Buffers
   serialises; its engine control frameworks are "implemented in both Java and
   C#". The July commit `acb9480` ("Python stays on Bray, which is where it
   actually comes from") misread this. `webb2022vent` states it: "bindings to
   … C, C#, Java, and Python".
   (b) "among the **most** actively maintained" is the only such comparative
   in the corpus; abstract (L128), paper L142 and monograph (L33, L451) all say
   "an actively maintained". Already noted in June
   (`audit/factcheck_paper_supplement_vs_monograph.md`: "a 4th prominence
   variant … worth harmonizing"), never done.
4. **Supplement L133 (uncited fork sentence) — REFINED: sourceable with keys
   already cited.** `pulseabout`: "a significantly improved and extended fork
   from the DoD-funded BioGears program. The Pulse repository is maintained by
   the Kitware team that includes the original core BioGears creators";
   `pulsefaq`: "started as a forked of the BioGears 6.1.1 Physiology Engine by
   members of its original team". The year: the Pulse repository's first
   commit is dated 2017-04-19 ("Initial Organization"), and Pulse's own release
   notes open with "Pulse v1.0.0 (September 2017)" (`docs/Markdown/Versioning.md`
   at REL_4_3_1) — neither is a bib entry. The three names are an inference (they are
   Bray 2019 authors); no source names them as "the original core
   developers". Suggested: add `\cite{pulseabout,pulsefaq}`; drop the names or
   write "by members of the original BioGears team".
5. **Limitations row 11 ("idealised valves") — confirmed.** "The engine uses
   ideal valves" is in the cardiovascular page; Bray 2019 also models the valve
   as a diode. Add `pulsecardiomethod` to row 11.
6. **Minor wording — two items refined.**
   (a) L135 gloss "intended for training simulation rather than
   patient-specific clinical prediction": Bray 2019's abstract does state an
   intended use — "for improved medical training **and clinical
   decision-making tools**". So "training" is sourced (Bray), but "rather than
   patient-specific clinical prediction" is our reading and sits uneasily with
   "clinical decision-making tools". Cite Bray and trim, or drop the clause.
   (b) "dermal" vs "thermoregulation": supplement S7 groups skin temperature
   under "Dermal" (Table S-Cornish, L668–669; L651), as does paper L146; paper
   L333 ("chemistry and thermoregulation outputs") is the odd one out.
   (c) `webb2022vent` "qualitative" (L164): unchanged, low priority.
7. **Metadata — confirmed.** `ward2024ventilator` pages 192–198 (Crossref;
   arXiv's own comment "CBMS … 7 pages" agrees); `webb2022vent` pages 282–293
   (Crossref only; PMC does not print them).
8. **`victoriano2026sim2real`, paper L140 — confirmed.** 17 of about 20 words
   follow the source's closing sentence in order, without quotation marks.
9. **NEW — limitations row 10 has no citation.** Its source column reads
   "Pulse documentation" with no `\cite`. The content is right:
   `pulserespmethod` "V_C = 4.93 L. Typical values of V_C reported in the
   literature are around 4.6 L" (+7.2 %); `pulsepatientmethod` validation
   table "Patient-VitalCapacity(mL) 4819.2" for the standard male (+4.8 % on
   4.6 L). Add `\cite{pulserespmethod,pulsepatientmethod}`.
