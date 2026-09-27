---
id: S003
author: santino
date: 2026-04-19
status: done
tags: [literature, verification, pulse, limitations]
linked_code: []
linked_data: []
supersedes: ""
related: []
---

# S003 — Verified Pulse 4.3.1 limitations (primary-source re-check)

## Hypothesis

The claim "Pulse has no formal sensitivity analysis or uncertainty quantification" — the entire motivation of PulseProbe — is still accurate in the current release (v4.3.1, Sept 2024). It has *not* been silently resolved in a recent version that we missed.

## Motivation (why now)

The preregistration, the hackathon pitch, the chef-de-département approval request, and the preprint all lean on this one claim. If it is already obsolete (Pulse shipped SA in, say, v4.3.1 minor update), the whole project's novelty collapses. Memory is unreliable for version-specific facts — we need a primary-source re-check before locking the preregistration.

## Method (how)

Phased research (internal → MCP/web → source):

1. Fetched the Pulse FAQ directly: `https://pulse.kitware.com/_f_a_q.html`. Read the UQ/SA paragraph verbatim.
2. Cross-checked against the version history page: `https://pulse.kitware.com/version.html`. Walked every release from v3.0.0 → v4.3.1 looking for SA / UQ / sensitivity features.
3. Read the v4.3 release notes for any post-release additions.
4. Re-audited each previously-cited limitation in `CLAUDE.md` against the current engine behavior.

## What we tried (including dead ends)

Also re-audited two limitations that had been asserted in earlier working notes but lacked primary-source support:

- **FiO2 crash at 1.0.** Tested in PhD experiment E20 (Apr 2026). Pulse actually accepts FiO2 = 1.0 cleanly. Claim **withdrawn**.
- **"No sex-specific physiology beyond weight and height."** Checked the Pulse docs: the engine does have sex-specific hemoglobin and body-composition models. Claim was overstated. Withdrawn pending a proper source-code audit.

## Results

**Core gap confirmed.** From the FAQ (quoted verbatim in CLAUDE.md):

> "We have not performed a systematic forward propagation or inverse quantification of model uncertainty, nor have we conducted a formal sensitivity analysis."

Version walk:

- **v3.0.0** — *planned* a sensitivity framework. Never delivered.
- **v4.2.0** — still no SA/UQ.
- **v4.3.0** — added "initial architecture for automated validation" = regression templates. Not UQ, not SA.
- **v4.3.1** (Sept 2024, current) — still no formal SA/UQ.

The 12-item verified-limitations table in CLAUDE.md was finalized. Two previously-asserted claims were withdrawn (FiO2, sex-specific).

## Interpretation

The pitch holds. PulseProbe's core premise — "first systematic reliability atlas for Pulse" — is current, not stale. The gap is reproducible from a primary source: any reviewer can fetch the FAQ and verify.

Two lessons:

1. **Claims must be re-verified before the preregistration locks.** The two withdrawn claims would have embarrassed the preprint.
2. **Distinguish documented limitations from assumed ones.** The 12 confirmed limitations in CLAUDE.md each trace to: the Pulse FAQ, Pulse docs, Pulse source audit, or our own PhD experiments. The two withdrawn claims traced to neither.

## Next steps

- Lock `preregistration.md` (done on same day).
- **Rule going forward:** no new limitation added to CLAUDE.md without a traceable source (DOI, Pulse FAQ URL, source file + line number, or own experiment ID).

---

## Update 2026-05-07 — see [S016](S016_pulse_gitlab_audit_may2026.md)

Re-audit of `gitlab.kitware.com/physiology/engine` surfaced one nuance that **does not invalidate any finding above** but sharpens limitation #1's wording:

- The Pulse repo carries a tag `STUDY_SENSITIVITY_ANALYSIS_1_0_0` (2020-07-20) with code at `src/cpp/study/sensitivity_analysis/` (C++ ~56 KB) and `src/python/pulse/study/sensitivity_analysis/` (analysis.py, ml_surrogate.py, …). Its ReadMe defines the scope as *"sensitivity analysis as a path towards improved lumped parameter optimization"* — Sobol indices over internal vascular-circuit resistance multipliers (model-calibration parameters), not user-facing operational inputs. Last functional commit 2020-08-24; not ported to 4.3.x.
- The literal FAQ statement quoted above remains correct (no SA on the shipped engine). The framing across CLAUDE.md, README, `reference/pulse_limitations_verified.md`, `reference/pulse_engine_summary.md`, and `preprint/manuscript.md` was updated to say "no formal SA / UQ on **user-facing operational inputs**" rather than the broader "no SA" claim.
- Pulse `REL_4_3_2` (2025-08-12, current `stable` head) was diffed vs `REL_4_3_1` and is build-system only (7 files, +46 / −17, web-WASM + .NET binding); no physiology / validation / patient-setup / solver code changed. Our 4.3.1 pin remains the correct evaluation target.

S003's central finding — Pulse 4.3.1 ships with no formal SA / UQ on operational inputs and the FAQ is still current — is unchanged. S016 documents the audit in full.

**Note (2026-09-27).** The 2026-05-07 update above says the 2020 study's last functional commit was 2020-08-24 and that it was "not ported to 4.3.x". Both are corrected in the dated note of 2026-09-27 at the end of [S016](S016_pulse_gitlab_audit_may2026.md): the code is still in the 4.3.x source tree, and two of the 17 later commits on its C++ folder change the study's own code. The text above is kept as written.
