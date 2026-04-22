# Experiments Log — moved

**This file has moved.** The lab notebook is now a folder, not a single file.

See [`experiments_log/README.md`](experiments_log/README.md) for conventions and
[`experiments_log/INDEX.md`](experiments_log/INDEX.md) for the full index of entries.

## Why the change

With two people writing (Santino and a second contributor), a single flat file would produce
constant merge conflicts. The new structure is:

- `experiments_log/santino/` — one file per experiment, prefix `S###`.
- `experiments_log/contributor2/` — one file per experiment, prefix `M###`.
- `experiments_log/shared/`  — joint experiments, prefix `E###` (ensemble).

Each person writes only in their own folder → zero conflicts on individual entries.
`INDEX.md` is auto-regenerated from frontmatter by a pre-commit hook.

## Migration

The D0 entries that used to live here have been migrated:

- `E0.1` → [`experiments_log/santino/S001_docker_smoke_test.md`](experiments_log/santino/S001_docker_smoke_test.md)
- `E0.2` → [`experiments_log/santino/S002_project_bootstrap.md`](experiments_log/santino/S002_project_bootstrap.md)
- `E0.3` → [`experiments_log/santino/S003_pulse_limitations_verified.md`](experiments_log/santino/S003_pulse_limitations_verified.md)

This stub is kept for one week so any outstanding links still resolve, then removed.
