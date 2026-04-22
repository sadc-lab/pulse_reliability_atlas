# Proposed Pediatric Patches to the Pulse C++ Engine (Paper 2 Input)

**Status:** SEED DOCUMENT for PhD Paper 2 (native pediatric Pulse fork). Populated incrementally as the Pulse Reliability Atlas produces Morris μ* rankings per output.

**Role in the PhD pipeline:**
1. **Methods paper (this repo)** delivers Morris μ* rankings — which inputs dominate which outputs.
2. **Paper 1 (`Pulse_translation_new/`)** uses the rankings to justify translator priorities and limitations.
3. **Paper 2 (native pediatric Pulse fork)** uses this file as the prioritized patch list, driven by the μ* rankings: highest μ* → biggest leverage → patch first.

This file is **not** a methods-paper deliverable. It is an input to Paper 2. It is versioned here because the code targets live in the adult Pulse source, and the μ*-ranking logic is specific to this repo.

---

## Disclaimers (apply to every patch below)

- **NOT compiled.** Proposals are on paper only.
- **NOT tested.** No validation has been performed.
- **NOT using real patient data.** PICU data from Sainte-Justine Hospital remains inside the PhD project and is never touched by this methods-paper deliverable.
- **NOT a native pediatric engine.** These are candidate edits to seed PhD Paper 2, not a shipped pediatric Pulse.
- **Open-source only.** Pulse is Apache-2.0; reading and proposing diffs is legally and ethically clean.

---

## Methodology

1. Read the open-source Pulse C++ at `C:\Users\santi\projets\Pulse_engine_adults_Gitlab\engine`.
2. Target formula sites that are adult-fit and dominate pediatric error, as identified by the Pulse Reliability Atlas Morris μ* sensitivity ranking (candidate sites: `SetupPatient.cpp` age/sex gate, BMR equation, blood-volume equation, max-HR equation, baroreflex gain).
3. For each site, produce:
   - Current (adult-fit) code excerpt.
   - Proposed pediatric replacement as a code diff.
   - ≥2 independent literature citations justifying the replacement (two-references rule).
   - Priority rank from the atlas Morris analysis.

---

## Patches

_(Populated incrementally as the atlas Morris rankings land. Structure below is the template.)_

### Patch 1 — [name]

- **File:** `engine/src/...`
- **Function / lines:** `...`
- **Morris μ* rank (from atlas):** _e.g. #1 for Vt delivered_
- **Current (adult-fit):**
  ```cpp
  // placeholder
  ```
- **Proposed (pediatric):**
  ```cpp
  // placeholder
  ```
- **Literature justification (≥2 independent sources):**
  - [citation 1]
  - [citation 2]
- **Expected impact if applied:** [short prose]

### Patch 2 — [name]

_(same structure)_

### Patch 3 — [name]

_(same structure)_

---

## Cross-references

- PulseProbe Morris ranking: `figures/morris_mu_star_ranking.png` (generated D3)
- PhD source audit of Pulse C++: `Pulse_translation_new/pulse_engine_internals_for_future_paper.md`
- PhD Paper 2 plan: `Pulse_translation_new/publication_plan.md` section 2

## References

_(populated with each patch)_
