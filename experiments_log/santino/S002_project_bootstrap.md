---
id: S002
author: santino
date: 2026-04-19
status: done
tags: [bootstrap, infrastructure, repo-setup]
linked_code: []
linked_data: []
supersedes: ""
related: [S001, S003]
---

# S002 — Project bootstrap (separate repo, skeleton, licensing)

## Hypothesis

Creating a clean, separately-licensed repo with a fixed skeleton *before* the hackathon opens will let D1 be spent on science rather than plumbing. The alternative — bootstrapping during the event — consistently blows time budgets.

## Motivation (why now)

The hackathon opens Tue 2026-04-21. Mode A requires Morris design, orchestrator, post-processor, stats, dashboard, preprint — all within 7 days. Any time spent on repo hygiene during the event directly subtracts from science time. D0 is the cheapest moment to pay this cost.

## Method (how)

Created `C:\Users\santi\projets\Hackathon_Claude_2026\` with:

- `CLAUDE.md` — project rules, verified Pulse limitations, Mode A/B/C plan, budget, scope-change rules.
- `README.md` — public-facing summary (what PulseProbe is, why it exists, connection to the 3 PhD papers).
- `preregistration.md` — analysis commitments locked pre-data (research question, H1/H2/H3, input ranges, scenarios, outputs, sampling, analysis plan, stop rules).
- `experiments_log.md` — this lab notebook (later migrated to `experiments_log/` directory structure — see README there).
- `.gitignore` — standard Python + data + IDE exclusions.
- Directory skeleton: `src/`, `data/`, `dashboard/`, `preprint/`, `figures/`, `notebooks/`.
- Apache 2.0 `LICENSE` file.

The sister PhD project (`C:\Users\santi\projets\Pulse_translation_new`) is referenced by link, not copied. CLAUDE.md lists the four read-only files in that project that inform PulseProbe without duplicating them.

## What we tried (including dead ends)

- Considered putting PulseProbe as a subdirectory of `Pulse_translation_new`. Rejected: the hackathon needs its own license, its own repo, its own judging-ready README, and its own git history. Cross-contamination between hackathon artifacts and the PhD paper would be hard to untangle later.

## Results

Repo directory ready for `git init`. All D0 setup files present. Skeleton is empty but structured — D1 can start writing code immediately.

## Interpretation

Bootstrap cost ≈ 1 h on D0, recovered as D1 not spent on plumbing. The "separate repo, reference the sister project" choice keeps both codebases clean and makes the hackathon output self-contained for judges (no one has to `cd` into a different repo to understand the deliverable).

## Next steps

- D0: `git init`, first commit, push to GitHub (private during dev, flip to public before judging — tracked in memory).
- D0: draft hackathon application and `HOW_CLAUDE_CODE_WAS_USED.md` transparency doc.
- D1: start writing `run_morris.py` in `src/`.
