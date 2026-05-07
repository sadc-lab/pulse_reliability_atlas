# PulseProbe Lab Notebook

Shared experiments log for Santino and a second contributor. This is the source of truth for *why* we did something, *how* we did it, and *what happened*. Git history is the source of truth for *who* did what and *when*.

---

## Conventions

### 1. Folders = ownership (no merge conflicts)

- `santino/` — Santino writes here, nobody else.
- `contributor2/` — the second contributor writes here, nobody else.
- `shared/` — joint experiments only; list both authors in frontmatter.

Because each person writes only in their own folder, individual experiment files cannot conflict at the git level. The only file both people touch — `INDEX.md` — is auto-generated (see below), not hand-edited.

### 2. ID prefixes

- `S###` — Santino (solo).
- `M###` — second contributor (solo).
- `E###` — **E**nsemble (joint / shared).

Zero-padded to 3 digits: `S001`, `S012`, `M007`, `E002`. Increment from the highest existing ID **in your own folder** (or in `shared/` for E-entries).

### 3. One file per experiment

Filename: `{ID}_{short_slug}.md` — e.g. `S001_docker_smoke_test.md`, `E003_cross_validation.md`. Keep the slug short and descriptive.

### 4. Use the template

Copy [`TEMPLATE.md`](TEMPLATE.md). Every experiment file has:

1. **Hypothesis** — what you expect, and why.
2. **Motivation** — why this experiment is worth running *now*.
3. **Method** — setup, params, seeds, commit SHA if useful. Reproducible from this page.
4. **What we tried** — including dead ends. Dead ends are data.
5. **Results** — numbers, plot links, observations. Raw enough to re-interpret.
6. **Interpretation** — what it means. Confirms / rejects hypothesis. Limitations.
7. **Next steps** — follow-ups, or "none — question closed."

Never just action + result. This rule comes from `CLAUDE.md` (global project rule).

### 5. Status lifecycle

`planned` → `in-progress` → `done` / `abandoned` / `superseded`.

If an experiment is superseded by a later one, set `status: superseded` and fill `supersedes` with the new ID — or use the `supersedes` field on the new entry to point back to the old one.

### 6. Link, don't copy

Reference code, data, and figures by path:

- `linked_code: [src/run_morris.py]`
- `linked_data: [data/runs/S001/results.parquet]`
- Figures: link from the body with `![](../../figures/S001_wall_time.png)`.

### 7. Commits are single-author

Per `CLAUDE.md`: no `Co-authored-by:` trailers, not for Claude, not between Santino and the second contributor. Each commit has exactly one author, and that author is the person who ran the experiment described. Git blame is the attribution.

---

## Shared (`E###`) entries

For experiments where you and the second contributor both contributed substantively (e.g., one designed the stats test, the other implemented it).

- Put the file in `shared/`.
- Frontmatter `author:` lists both, comma-separated: `author: santino, contributor2`.
- Talk before editing — Slack/WhatsApp beats a merge conflict.
- If you find yourselves conflict-resolving a shared file more than once, **split it** into two solo entries that cross-reference each other via the `related` frontmatter field.

---

## INDEX.md is auto-generated

[`INDEX.md`](INDEX.md) is regenerated from every experiment's frontmatter by `scripts/regenerate_index.py`, which runs automatically as a pre-commit hook. **Do not edit `INDEX.md` by hand** — your edits will be overwritten on the next commit.

### One-time setup (each clone, each person)

From the repo root:

```
git config core.hooksPath .githooks
```

That's it. After this, every commit:

1. Auto-regenerates `experiments_log/INDEX.md` and stages the update into the same commit.
2. Runs `ruff check src/ scripts/ tests/ engine/` (mirrors the GitHub Actions tests workflow) and **blocks the commit** if any violation remains. Auto-fix safe violations with `uv run ruff check --fix src/ scripts/ tests/ engine/`, then re-stage and re-commit. This is the same gate that runs in CI, just enforced locally so you don't push a red build.

If the hook is not set, the index will drift and lint failures will only appear on push. If it drifts, run the generator manually:

```
python scripts/regenerate_index.py
git add experiments_log/INDEX.md
git commit -m "Regenerate experiments index"
```

---

## Frontmatter fields (full reference)

```yaml
---
id: S001                          # required. S / M / E + 3 digits
author: santino                   # required. santino | contributor2 | santino, contributor2
date: 2026-04-21                  # required. ISO date of the experiment
status: done                      # required. planned | in-progress | done | abandoned | superseded
tags: [docker, hardware, pilot]   # optional. free-form, lowercase, hyphenated
linked_code: [src/run_morris.py]  # optional. relative paths from repo root
linked_data: [data/runs/S001/]    # optional. relative paths from repo root
supersedes: ""                    # optional. ID of a previous experiment this replaces
related: []                       # optional. IDs of related experiments
---
```

Only `id`, `author`, `date`, `status` are required. Missing optional fields are fine — the index handles them.

---

## Migration note

The old `experiments_log.md` (single flat file) has been migrated:

- E0.1 → `santino/S001_docker_smoke_test.md`
- E0.2 → `santino/S002_project_bootstrap.md`
- E0.3 → `santino/S003_pulse_limitations_verified.md`

The old file is kept at the repo root as a short redirect stub for one week, then removed. Do not write new entries there.
