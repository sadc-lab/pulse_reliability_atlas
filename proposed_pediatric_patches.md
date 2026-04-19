# Proposed Pediatric Patches to the Pulse C++ Engine (D6 Bonus)

**Status:** EMPTY TEMPLATE — skeleton only. This file is populated **only if the D6 trigger fires**:
Mode A must be 100% locked (dataset landed, dashboard MVP running, preprint skeleton
started, demo outline clear) by end of D5 Saturday night. Otherwise this file stays empty
and D6 is spent on core polish.

See `CLAUDE.md` section "D6 conditional bonus chapter" for the full trigger rule.

---

## Disclaimers (apply to every patch below)

- **NOT compiled.** Proposals are on paper only.
- **NOT tested.** No validation has been performed.
- **NOT using real patient data.** PICU data from Sainte-Justine Hospital remains
  inside the PhD project and is never touched by this hackathon deliverable.
- **NOT a native pediatric engine.** These are candidate edits to seed PhD Paper 2,
  not a shipped pediatric Pulse.
- **Open-source only.** Pulse is Apache-2.0, so reading and proposing diffs is
  legally and ethically clean.

---

## Methodology

1. Claude Code reads the open-source Pulse C++ at
   `C:\Users\santi\projets\Pulse_engine_adults_Gitlab\engine`.
2. Targets 2–3 formula sites that are adult-fit and dominate pediatric error,
   as identified by PulseProbe's Morris μ* sensitivity ranking (typically:
   `SetupPatient.cpp` age/sex gate, BMR equation, blood-volume equation,
   max-HR equation, baroreflex gain).
3. For each site, produces:
   - Current (adult-fit) code excerpt.
   - Proposed pediatric replacement as a code diff.
   - ≥2 independent literature citations justifying the replacement
     (two-references rule from `CLAUDE.md`).
   - Priority rank from PulseProbe's own Morris analysis.

---

## Patches

_(Populated only if D6 triggers. Structure below is the template.)_

### Patch 1 — [name]

- **File:** `engine/src/...`
- **Function / lines:** `...`
- **Morris μ* rank (from PulseProbe):** _e.g. #1 for Vt delivered_
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
