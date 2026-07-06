# Cover letter — npj Digital Medicine

*Draft, uncommitted. Pending maintainer review before submission.*

---

1 June 2026

The Editors
*npj Digital Medicine*

Dear Editors,

We are pleased to submit our original research article, **"An Open Reliability Atlas for the Pulse Physiology Engine: Sensitivity,
Divergence, and Sex-stratified Failure Modes,"** for
consideration as an Article in *npj Digital Medicine*.

The Pulse Physiology Engine (Kitware, Apache-2.0) is a prominent
open-source whole-body physiology simulator, and its synthetic patient
trajectories increasingly feed device-validation studies, computational
physiology research, and machine-learning pipelines. Yet the engine's own
maintainers state on their public FAQ that they "have not [...] conducted a
formal sensitivity analysis" of the model. Every downstream user has therefore
been operating without a map of where the engine's user-facing operational
envelope is trustworthy. **Our manuscript provides that map — the first open,
preregistered reliability atlas of Pulse across the adult critical-care
envelope (1,280 Morris elementary-effects simulations spanning seven
operational inputs, four ARDS severities, and two patient reference bodies).**

Three findings make this contribution timely for the *npj Digital Medicine*
readership:

1. **A previously uncharacterised, sex-stratified solver-divergence cluster
   with an identified mechanism.** All 20 of the 1,280 divergent runs fell on
   the *male* reference body. We trace the effect to Pulse's allometric
   blood-volume baseline: reducing the male baseline toward its setup-time
   floor (4,082.24 mL) eliminated divergence at both bracket reductions (20/20 → 0/20). This
   is a structural artefact, not a clinical phenomenon — and it means that
   pooling male and female synthetic cohorts at input extremes silently injects
   a spurious sex covariate into any downstream model.

2. **The first public characterisation of an ARDS impairment-fraction
   solver-instability band ([0.879, 0.945]).** Published Pulse validation work
   samples ARDS severity only on round tenths and never probes inside this
   interval. Our continuous-severity sweep resolves two distinct divergence
   regimes — an input-driven regime on the male body and a severity-driven
   regime affecting both sexes — and gives downstream users a concrete band to
   avoid when stable steady-state output is required.

3. **A reusable, open data-quality instrument for synthetic-cohort science.**
   The per-cell, four-flag traffic-light map is the atlas's principal
   deliverable: a drop-in filter that tells a clinical-AI or ML practitioner
   which Pulse configurations are safe to ingest, which require flag-stratified
   handling, and which need per-channel justification. We also surface two
   operator-actionable fixes — a one-line VC-AC trigger setting (−2 cmH₂O) that
   collapses tidal-volume dyssynchrony, and a steady-state-window correction for
   hyperoxia simulation at FiO₂ = 1.0.

The work sits squarely within *npj Digital Medicine*'s scope at the
intersection of digital health, synthetic data, and reproducible computational
methodology. It directly addresses a stated gap acknowledged by the engine's
maintainers; its methodology (Morris screening plus a categorise-don't-discard
steady-state classifier) transfers to sibling lumped-parameter engines such as
BioGears and HumMod; and the entire pipeline — preregistration, Docker image,
fixed seed, and a machine-checked audit ledger of every quantitative claim — is
released open-source under Apache-2.0 for full reproducibility.

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
