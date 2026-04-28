---
id: S013
author: santino
date: 2026-04-27
status: done
tags: [lexical-precision, manuscript-polish, taxonomy, reviewer-defense]
linked_code: []
linked_data:
  - preprint/manuscript.md
  - preprint/interim_findings.md
  - preprint/supplementary.md
supersedes: ""
related: [S006, S008, S012]
---

# S013 — Lexical lockdown (solver-divergence vs implausible-output taxonomy)

## Hypothesis

The atlas's failure-mode taxonomy is precise in code (four orthogonal
flags in `src/detector.py`) but the manuscript text uses imprecise
words like "crash", "breaks", "fails" interchangeably with the
strictly-defined `diverged` and `implausible` flags. A methods
reviewer will hunt for any such imprecision; eliminating it before
submission removes a free attack surface.

Strict definitions (locked in `src/detector.py`):

* `diverged` — solver mathematical failure: NaN/Inf in CSV, missing
  CSV, exit code ≠ 0.
* `implausible` — physiological-bound violation on steady-state mean
  (e.g. SpO2 < 50 %, PaO2 > 600 mmHg).
* `clamped` — Pulse rejects an out-of-envelope input at setup with a
  loud `[ERROR]` log line.
* `not_steady_state` — flatline at extreme, variance too high, or
  drift over final 60 s exceeds preregistered threshold.

These four flags are mutually orthogonal; `clean` is the absence of
all four.

## Motivation (why now)

Reviewer-anticipated critique. A pass after S010 (literature review)
+ S012 (steady-state audit) tightens the manuscript's lexical
precision so every claim about a Pulse failure points to one specific
flag, not to a vague "crash".

## Method (how)

1. **Grep audit.** `grep -rni "\b(crash|breaks|broke|broken|fails|failed|failing|fall over)\b"`
   over `preprint/`. Identified four hits: 2 in `manuscript.md`, 1 in
   `interim_findings.md`, 1 in `supplementary.md`.
2. **Targeted edits.** Replaced each occurrence with the specific
   strict flag the sentence is actually describing.
3. **§3.5 + §6 audit.** Re-read both sections in full to catch any
   imprecision the grep might miss. None found — both sections
   already use `diverged`, `divergence`, `numerical edge case`
   precisely; references in §6 are bibliographic and contain no
   engine-behaviour claims.
4. **Re-grep verification.** Final grep returns zero hits in `preprint/`
   for the imprecise vocabulary. Lexical lockdown achieved.

## What we tried (incl. dead ends)

1. Considered a broader regex including "die", "dies", "halts",
   "blow up". Manual re-read showed these terms do not appear in
   `preprint/`; the 4-word regex (`crash|breaks|fails|fall over` plus
   inflections) was sufficient.
2. Considered tightening the `experiments_log/` text similarly.
   Rejected — experiment logs are private working notes, not part of
   the published artifact. Lexical precision in the manuscript is
   load-bearing; lexical precision in the lab notebook would be
   over-engineering.
3. Considered renaming the four detector flags to enforce the
   taxonomy at code level. Rejected — flags are stable across S004 →
   S012 and any rename would invalidate already-published artifacts
   (parquets, reproducibility checks). The taxonomy is precise *via
   docs*, not via class hierarchy; the manuscript edits are the
   correct intervention.

## Results

### Edits applied

| File | Line | Before | After |
|------|------|--------|-------|
| `preprint/manuscript.md` | 191 | "FiO2 crash at 1.0" | "FiO2 solver-divergence at 1.0" |
| `preprint/manuscript.md` | 226 | "no Pulse crash at FiO2 = 1.0" | "no Pulse solver-divergence at FiO2 = 1.0" |
| `preprint/interim_findings.md` | 99 | "if every S4 init crashed regardless" | "if every S4 init diverged regardless" |
| `preprint/supplementary.md` | 19 | "no crash" | "no solver-divergence" |

### Re-grep verification

```
$ grep -rni "\b(crash|crashes|crashed|breaks|broke|broken|fails|failed|failing|fall over)\b" preprint/
(no matches)
```

Both contexts now use the strict failure-mode vocabulary:
`solver-divergence` for mathematical failures, `diverged` (the flag
name) for the categorical event, and `implausible` for physiological
bound violations.

### §3.5 + §6 audit

§3.5 ("H3 — solver divergence is sex-stratified") reviewed in full;
all references to engine failure use `diverged`, `divergence`, or
`numerical edge case`. No imprecise vocabulary present.

§6 (References) is bibliographic; no engine-behaviour claims; no
lexical issues.

## Interpretation

The manuscript now has a single failure-mode vocabulary tied to the
four detector flags. A reviewer reading any failure claim can trace
it to the exact flag and to the threshold that produced it. The
taxonomy holds at the level of:

* **Vocabulary.** Only the four flag names (`clamped`, `diverged`,
  `implausible`, `not_steady_state`) and their semantic equivalents
  (`solver-divergence`, `physiological-bound violation`) appear when
  describing engine behaviour.
* **Cross-references.** Each occurrence in the manuscript points back
  to the detector module, the threshold table, or the per-cell flag
  count in Table 1.

This is a small edit (4 occurrences, ~30 minutes of work) but
removes a predictable attack surface for methods reviewers.

### Limitations

1. The taxonomy is precise *given the four-flag classifier*. A
   reviewer who disputes the flag definitions themselves (e.g.
   argues SpO2 < 50 % is too lenient as an implausibility floor) is
   making a different argument; that is addressed by §2.6 (Detector)
   and the preregistration §Flags.
2. We did not introduce a glossary section. The vocabulary is
   defined in §2.6 and §3.1; adding a glossary was considered
   bureaucratic.

## Next steps

* Combined S012 + S013 commit + push.
* If a reviewer disputes a specific flag definition, point to §2.6
  and to `src/detector.py::DRIFT_MAX_DELTA_60S` /
  `HARD_BOUNDS` / `CLAMP_PATTERNS`.
