# Cover letter — npj Digital Medicine

---

[date of submission]

The Editors
*npj Digital Medicine*

Dear Editors,

We are pleased to submit our original research article, **"An Open Reliability Atlas of Sensitivity and Failure Modes in the Pulse Physiology Engine,"** for
consideration as an Article in *npj Digital Medicine*.

*npj Digital Medicine* lists **digital twins** explicitly within its scope, at
the intersection of digital health, synthetic data, and reproducible
computational methodology. What has not been established is how reliable they
are as a source of data. **Our object of study is therefore not human
physiology but the data-generating instrument itself.** The Pulse Physiology
Engine (Kitware, Apache-2.0) is an actively maintained open-source whole-body
physiology simulator whose synthetic patient trajectories are applied to
device-validation studies and to computational physiology research; yet the
engine's own maintainers state on their public FAQ that they "have not [...]
conducted a formal sensitivity analysis" of the model. Every downstream user
has therefore been operating without a map of how the engine behaves across
its user-facing operational envelope — and the stakes are no longer
hypothetical: an independent group has already used the engine's respiratory
dynamics as a source of simulated data to learn and benchmark
ventilator-control policies for ARDS (Ward et al., *IEEE CBMS* 2024), and any
model fitted to that output absorbs whatever artefacts the envelope contains as
though they were physiology. **Our manuscript provides that map — the first
open reliability atlas of Pulse, with a preregistered core design, across the
adult critical-care envelope (1,280 Morris elementary-effects simulations of seven operational
inputs, balanced across eight cells of 160 runs: four ARDS severities crossed
with two patient reference bodies).**

The journal has also published on the credibility and use of computational
physiological models: a cardiac digital-twin surrogate spanning 43 model
parameters and used for global sensitivity analysis and parameter estimation
with uncertainty quantification (Salvador et al., 2024), and a survey and
perspective on verification, validation and uncertainty quantification of
digital twins for precision medicine (Sel et al., 2025). Our study addresses a
complementary upstream problem: before outputs from a mechanistic physiology
engine are used to generate synthetic cohorts or train downstream models, its
operational input space and failure modes need to be characterised. We
therefore present the atlas as a reproducible curation and review-priority
instrument, not as external physiological validation or a formal regulatory
credibility assessment.

Three findings make this contribution timely for the *npj Digital Medicine*
readership:

1. **A reusable, open curation instrument for synthetic-cohort science.**
   The per-cell traffic-light curation map is a principal deliverable of the
   atlas: under the stated criteria, it sets cell-level review priority. A
   separate run-level four-flag classifier, needed in every cell whatever its
   colour, supports exclusion, remediation, or stratified handling; neither
   layer is a distribution-neutral automatic filter. We also surface two
   operator-actionable fixes — a one-line VC-AC trigger setting (−2 cmH₂O) that
   collapses tidal-volume variability consistent with patient–ventilator
   dyssynchrony, and a steady-state-window correction for
   hyperoxia simulation at FiO₂ = 1.0.

2. **A previously uncharacterised, sex-stratified solver-divergence cluster
   with an identified mechanism.** All 20 of the 1,280 divergent runs fell on
   the *male* reference body. We trace the effect to Pulse's allometric
   blood-volume baseline: reducing the male baseline toward its setup-time
   floor (4,082.24 mL) eliminated divergence at both bracket reductions (20/20 → 0/20). This
   is a structural artefact, not a clinical phenomenon — and it means that
   pooling male and female synthetic cohorts at input extremes silently injects
   a spurious sex covariate into any downstream model.

3. **To our knowledge, the first systematic characterisation of an ARDS
   impairment-fraction solver-instability band ([0.879, 0.946]).** Published
   Pulse validation work and HowTo examples sample at most up to severity 0.9
   and do not examine impairment fractions inside 0.91–0.945. Our
   continuous-severity sweep resolves two distinct divergence regimes — an
   input-driven regime on the male body and a severity-driven regime affecting
   both sexes — and gives downstream users a concrete band to avoid when stable
   steady-state output is required.

The work directly addresses a stated gap acknowledged by the engine's
maintainers; its methodology (Morris screening plus a categorise-don't-discard
steady-state classifier) transfers to sibling lumped-parameter engines such as
BioGears and HumMod; and the entire pipeline — preregistration, Docker image,
fixed seed, and a machine-checked audit ledger of the computed quantitative
claims — is released open-source under Apache-2.0 for full reproducibility.

This manuscript is original, has not been published previously, and is not
under consideration for publication elsewhere. All named authors have
contributed to and approved the submission. The authors declare no competing interests, and author contributions are specified in the manuscript (CRediT taxonomy). All data and code are openly available; the data-availability
statement will cite the repository and the archived dataset DOI.

We believe the reliability atlas offers foundational infrastructure that will
benefit the growing community building digital-health and clinical-AI systems
on synthetic physiology, and we hope you will find it suitable for *npj Digital
Medicine*.

On behalf of all authors,

**Santino Nanini** (corresponding author)
Pediatric Intensive Care Unit, CHU Sainte-Justine / Université de Montréal;
Clinical Decision Support System (PE-DIATRICS) Cluster, CHU Sainte-Justine;
Research Center, Sainte-Justine University Hospital; Pediatric Intensive Care
Unit, Children Hospital, CHRU Nancy; UR 3450 DevAH, Université de Lorraine, Nancy
santino.nanini@umontreal.ca
