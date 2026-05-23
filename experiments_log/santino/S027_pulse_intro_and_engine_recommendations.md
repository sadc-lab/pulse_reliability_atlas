---
id: S027
author: santino
date: 2026-05-23
status: done
tags: [manuscript-additions, pulse-explainer, engine-recommendations, traceability, post-arxiv-polish]
linked_code:
  - preprint/manuscript.md
  - preprint/references.bib
  - scripts/audit_claims.py
linked_data: []
supersedes: ""
related: [S006, S016, S018, S021, S024, S025, S026]
---

# S027 — §1.1 Pulse-in-a-nutshell explainer + §4.7 engine-side recommendations

## Hypothesis

Two additive content improvements to the (otherwise arXiv-ready)
manuscript will measurably raise its value to the Pulse research
community without re-litigating any audited claim:

1. A short "Pulse in a nutshell" paragraph in §1.1 lowers the
   on-ramp for cross-disciplinary readers (clinicians, ML
   practitioners) who are not already familiar with Pulse's
   electrical-circuit-analogue / ODE-based design and therefore
   currently have to chase the `@bray2019` citation before they can
   read the rest of the introduction.

2. A new §4.7 subsection containing six evidence-anchored,
   infrastructure-level suggestions for the Pulse maintainers
   converts the seven months of operational experience accumulated
   during the atlas build into a small, structured contribution
   back to the engine — visible to Pulse users and to the Kitware
   team as a concrete, actionable artefact rather than diffuse
   "lessons learned."

The hypothesis additionally requires: (a) the two additions can be
made *without modifying any previously audited prose*; (b) every
new quantitative claim slots cleanly into the existing
`audit_claims.py` ledger; (c) the resulting PDF builds without
unresolved-citation warnings; and (d) the additions remain within
the guard rails agreed in the planning conversation — collaborative
tone, no physiology-level prescriptions to Pulse, and every
recommendation anchored to a specific experiment-log entry.

## Motivation (why now)

S026 closed the arXiv-blocking surface (B-1 / B-2 / B-3) and the
should-fix surface (S-1 / S-2 / S-4 / S-5). At that point the
manuscript was technically submission-ready, but two readability /
contribution items had been intentionally kept out of S026 scope
because they reopen the door to manuscript edits and so warrant
their own preregistered traceability commit:

* **The "what is Pulse" gap.** §1.1's existing one-line description
  of Pulse ("0-dimensional lumped-parameter model of the
  cardiovascular, respiratory, gas-exchange, and pharmacological
  systems") is sufficient for biomedical-engineering readers but
  insufficient for a clinician or an ML researcher who has never
  used Pulse — and the atlas is explicitly written for a
  cross-disciplinary audience (see Reader's roadmap, "clinicians,
  biomedical engineers, statisticians, machine-learning
  practitioners").
* **The "engine-side recommendations" contribution gap.** §4.2 of
  the manuscript addresses *downstream Pulse users* (the VC-AC
  trigger configuration finding). There is no section addressed to
  the *Pulse maintainers themselves* with constructive,
  evidence-anchored suggestions for engine-side / infrastructure
  improvements that would lower the friction for the next
  reliability-style study on Pulse. Converting our seven months of
  operational experience (S004 / S005 / S014 / S017 / S018 / S021)
  into a structured short list is a low-cost, high-signal
  contribution back to the community.

Both items had been validated in a planning conversation with three
explicit guard rails on the §4.7 content (collaborative tone, stay
in the tooling / documentation / validation lane, every item traces
to an S0xx entry).

## Method (how)

Four-commit series, all on `main`:

* **Commit A — `6c11b32`** — Insert a ~150-word "*Pulse in a
  nutshell.*" paragraph in §1.1 between the existing one-line
  technical description and the three-community bullet list. Add a
  new `@pulsenervous` reference entry to §9.7 'Verified primary
  references'. Edit confined to two `Edit` tool calls; no existing
  prose modified.

* **Commit B — `1b6664a`** — Insert a new §4.7 "Engine-side
  enhancements that would benefit future atlas users" subsection
  between §4.6 and the `---` / §5 Conclusion separator, containing
  the six-item numbered list. Update the Reader's roadmap §4 bullet
  with a half-sentence mention of §4.7. Edit confined to two `Edit`
  tool calls; no §4.1–§4.6 prose modified.

* **Commit C — `9ec6e8b`** — Extend `scripts/audit_claims.py` with
  five new TIER 3 claim entries pinning the new quantitative claims
  (20 ms timestep, 10× and 15× real-time bounds, 4082.24 mL BV
  floor, 4802.63 mL BV default). The §1.1 documentation values are
  pinned against `PULSE_DOC_*` constants with verification-date
  citations to `pulse_engine_literature_review.md` §1.5; the §4.7
  BV constants are pulled out of `scripts/s018_bv_falsification.py`
  via regex at audit time so any drift between the experiment
  script and the ledger triggers an explicit `AssertionError`.

* **Commit D — `b6dccbe`** — Add the `@pulsenervous` BibTeX entry
  to `preprint/references.bib` so pandoc citeproc resolves the
  inline `[@pulsenervous]` citation introduced by Commit A. Rebuild
  the PDF (`scripts/build_paper.ps1`) to confirm clean render.

## Result

* `audit_claims.py` exit code 0, **195 / 195 PASS** (was 190 / 190
  before S027; +5 new entries, all PASS). The five new entries are
  T3.s027.timestep_ms, T3.s027.speed_lower, T3.s027.speed_upper,
  T3.s027.bv_floor, T3.s027.bv_default.
* `scripts/build_paper.ps1` exits "Build complete." on the first
  try; both `manuscript.tex` and `manuscript.pdf` (1.28 MB)
  regenerate; no unresolved-citation warnings.
* `git diff --stat` total for the four commits:
  `preprint/manuscript.md` +135 −2,
  `scripts/audit_claims.py` +88 −0,
  `preprint/references.bib` +8 −0.
  No file outside this scope was touched.
* Tone audit per the agreed guard rails:
  * §1.1 paragraph contains zero imperatives addressed to Pulse;
    frames the engine on its own design terms.
  * §4.7 prose uses "would benefit / would lower the friction /
    would have saved" throughout; no "Pulse should..."; the closing
    paragraph explicitly disclaims physiology-level prescription.
* Scope audit: all six §4.7 items are in tooling / documentation /
  validation infrastructure; zero items touch lumped-parameter
  circuit topology, the ODE solver, or sub-model design.
* Experiment-trace audit: every §4.7 item names ≥1 specific S0xx
  entry, all of which are catalogued in §1.4 and Appendix A.

### Drafting correction worth flagging

In the tracked-changes preview I drafted for the §1.1 paragraph, I
described the 5-compartment lung as "trachea, left and right bronchi,
left and right alveoli". A pre-commit verification against
`pulse_engine_literature_review.md` L188–189 corrected this to
"carina, left and right anatomic dead space, left and right alveoli",
which is the topology Pulse actually models (trachea = upper airway
above the carina, modelled as a single resistance per L820–824 of the
same document). The corrected description shipped in Commit A. This
is recorded here so the discrepancy between the preview text and the
committed text is traceable.

## Interpretation

The hypothesis is confirmed on all four counts:

* (a) No previously audited prose was modified — the diff for
  `manuscript.md` is purely additive (137 insertions, 2 deletions,
  where the 2 deletions are the two anchor lines re-emitted with
  trailing periods).
* (b) Every new quantitative claim is now in the audit ledger and
  passes; the ledger total grew from 190 to 195.
* (c) The PDF builds clean; the rendered §1.1 paragraph and §4.7
  subsection both appear at the expected file locations
  (`manuscript.tex` L415 for §1.1, L3511 for §4.7).
* (d) All three guard rails — collaborative tone, scope discipline,
  experiment traceability — hold on inspection.

The two additions raise the manuscript's contribution surface
without reopening any audited number. The §4.7 list also doubles
as a roadmap fragment: a future "Pulse Reliability Atlas v2" paper
or a co-authored engineering note with the Kitware team can use the
six items as a structured backlog.

## Traceability table (mirrors S025 / S026 conventions)

| # | Commit | File:line range | Category | Before | After | Rationale | Risk |
|---|---|---|---|---|---|---|---|
| 1 | A `6c11b32` | preprint/manuscript.md §1.1 L236–237 | Manuscript addition | One-line technical description of Pulse, immediately followed by three-community bullet list | Same one-line description + new ~150-word *"Pulse in a nutshell."* paragraph + bullet list | Gives cross-disciplinary readers a fast on-ramp to Pulse's design (electrical-circuit analogue, 20 ms ODE timestep, 5-compartment lung topology, multi-domain sub-models, language bindings, BioGears lineage, maintainer-stated "low-fidelity clinical approach") | Low — single new paragraph, every fact sourced; lung-topology correction caught pre-commit |
| 2 | A `6c11b32` | preprint/manuscript.md §9.7 (`@pulserespmethod` / `@pulsenervous` boundary) | Reference addition | `@pulserespmethod` followed by `@cornish2023` | `@pulserespmethod` followed by new `@pulsenervous` entry, then `@cornish2023` | Resolves the new inline `[@pulsenervous]` citation introduced in §1.1 to a human-readable §9.7 record | Low — single-bullet insert, mirrors existing entry format |
| 3 | B `1b6664a` | preprint/manuscript.md §4.7 (new subsection between §4.6 end and `---`) | Manuscript addition | §4.6 followed immediately by `---` / `## 5. Conclusion` | §4.6, then new ~620-word §4.7 "Engine-side enhancements" subsection (6-item numbered list + collaborative-tone framing paragraph + closing scope disclaimer), then `---` / §5 | Adds six evidence-anchored infrastructure-level suggestions for the Pulse maintainers, converting seven months of atlas-build experience into a structured contribution | Low — fully additive; collaborative tone audit and scope-guard audit both pass on inspection |
| 4 | B `1b6664a` | preprint/manuscript.md Reader's roadmap §4 bullet | Manuscript addition | "(§4.5), and downstream research hooks." | "(§4.5), downstream research hooks (§4.6), and a short, evidence-anchored list of engine-side infrastructure enhancements offered back to the Pulse maintainers (§4.7)." | Keeps the roadmap synchronised with the new section | Low — half-sentence addition |
| 5 | C `9ec6e8b` | scripts/audit_claims.py top-of-file imports | Code edit | `import json` then `import sys` | `import json`, `import re`, `import sys` | `re` is required by the new TIER 3 block to extract BV constants from the S018 script at audit time | Low — single-line add, alphabetical-imports convention respected |
| 6 | C `9ec6e8b` | scripts/audit_claims.py (new TIER 3 block before the output renderer, ~88 lines) | Code addition | No TIER 3 block | Five new `add(...)` calls (T3.s027.timestep_ms, T3.s027.speed_lower, T3.s027.speed_upper, T3.s027.bv_floor, T3.s027.bv_default) + regex extraction of MALE_FLOOR_BV_ML and MALE_DEFAULT_BV_ML from scripts/s018_bv_falsification.py with hard `assert`s if either constant cannot be located | Pin the five new quantitative claims introduced by Commits A and B; BV regex check keeps the audit script and the S018 experiment script in lock-step | Low — assertions fail loud; ledger total grew from 190 to 195 PASS on first try |
| 7 | D `b6dccbe` | preprint/references.bib (after `@pulserespmethod`, before `@cornish2023`) | Bibliography addition | `@pulserespmethod` entry, then `@cornish2023` | `@pulserespmethod`, new `@pulsenervous` entry (URL + note pointing to Pulse Nervous System Methodology page, verification date 2026-05-23), then `@cornish2023` | Required so pandoc citeproc resolves the new `[@pulsenervous]` citation; without it the PDF renders the citation as a literal "@pulsenervous?" | Low — single new `@misc` entry; build verifies cleanly |

## Verification artefacts

* `git log --oneline -n 4` head: `b6dccbe` → `9ec6e8b` → `1b6664a` → `6c11b32`.
* `uv run python scripts/audit_claims.py 2>&1 | head -3` shows
  "Total claims audited: **195 (195 PASS, 0 WARN, 0 FAIL)**".
* `powershell -ExecutionPolicy Bypass -File scripts/build_paper.ps1`
  ends with "Build complete."; `preprint/build/manuscript.pdf`
  is 1,284,731 bytes (rendered 2026-05-23 18:04 local time).
* `grep -E "Pulse in a nutshell|Engine-side enhancements|pulsenervous" preprint/build/manuscript.tex`
  matches at L415 (§1.1 paragraph), L3511 (§4.7 heading), and
  L4006 (rendered `@pulsenervous` reference) — confirming both
  inserts and the reference all reached the rendered output.

### Limitations

1. **The §1.1 paragraph cites Pulse documentation values
   (20 ms timestep, 10–15× real-time speed) that are not derivable
   from atlas data.** They are pinned against constants declared
   inside `audit_claims.py` with verification-date citations to
   `pulse_engine_literature_review.md` §1.5. If Pulse silently
   updates its docs page to a different value, this ledger does not
   detect the drift — only the next manual re-verification of the
   Pulse docs page (the same way `@pulsefaq` and `@pulserespmethod`
   are maintained) does. The constants carry a `last verified
   2026-05-23` comment as a maintenance anchor.

2. **The §4.7 paragraph is necessarily speculative about how the
   Pulse maintainers will receive these suggestions.** It is framed
   as a contribution back to the community, not as an endorsement
   or a guaranteed acceptance. If the Kitware team responds (whether
   adopting, deferring, or rejecting any of the six items), a
   future S028 entry should record the response and update the
   manuscript text accordingly.

3. **Visual inspection of the rendered PDF for §4.7 layout is a
   manual step.** The build script succeeded and the textual
   anchors all match, but confirming that the six numbered items
   render with the expected indentation and that the heading
   appears at the right hierarchy level in the table of contents
   requires opening `preprint/build/manuscript.pdf`. That visual
   check is the maintainer's responsibility before any subsequent
   arXiv upload.

## Next steps

1. **Push S027 commits A–D to `origin/main`** (final step of this
   series).
2. **Re-upload to arXiv** once the maintainer has visually inspected
   the rendered PDF; the underlying numerical content is unchanged
   from the S026 audit state plus the five S027 additions.
3. **If Pulse maintainers respond to §4.7,** open an S028 entry to
   record their reception and adapt the manuscript wording (or, if
   they implement any item, cite the upstream change and downgrade
   the recommendation to a "now landed in v4.x.y" historical
   footnote).
4. **Question closed for the §1.1 / §4.7 axis.** The Pulse-explainer
   and engine-recommendations contributions are now in place;
   subsequent improvements to either should be filed as separate
   experiment-log entries.
