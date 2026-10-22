# Zenodo deposit — plan (2026-10-22)

Status: **prepared, nothing deposited.** Decisions already taken in earlier sessions are
marked *decided*; the open ones are listed at the end for the maintainer.

## What the record holds (*decided*: code, data and monograph together; engine image too)

| File in the record | Source | Size (measured 2026-10-22) |
|---|---|---|
| `pulse_reliability_atlas-<tag>.zip` | `git archive` of the tag that carries the reserved DOI | small |
| `data_runs_<folder>.tar.gz`, one per folder of `data/runs/` (16), plus `data_runs_top_level_files.tar.gz` for the files at its root | `data/runs/` (16,514 files; derived parquet files included) | 5.0 GB in total before compression |
| `pulse_reliability_atlas_monograph.pdf` (companion monograph) | `preprint/build/manuscript.pdf`, 123 pages, built 2026-10-19 13:11:10 from the sources of `05e8e12` (last change of `preprint/manuscript.md`) | 1.4 MB |
| `pulse-atlas-engine_b2e0e807803d.tar.gz` | `docker save pulse-atlas-engine:latest` (image `sha256:b2e0e807803d…`, built 2026-05-04), then gzip | 1,465,620,992 bytes before compression (measured 2026-10-21) |
| `README_zenodo.md`, `SHA256SUMS.txt` | written for the record | small |

Zenodo limits (help.zenodo.org, read 2026-10-22): at most 100 files and 50 GB per record, so
`data/runs/` must be packed into archives; a draft can be previewed and deleted before publishing; once
published, files cannot be changed (the help pages give 30 days in one place and 45 days in
another for minor corrections); a DOI can be reserved before publishing ("Get a DOI now!"),
lost if the draft is deleted; several licences can be declared on one record; a new version is
a new record with its own DOI.

## Steps

1. *Agent, local and reversible.* Scan `data/runs/` for personal information (user names in
   paths, e-mail addresses): it never went through the pre-public audit because it is not in
   git. *Done 2026-10-22:* 16,514 files (6,702 json, 6,421 csv, 3,352 log, 37 parquet); no
   e-mail address (pattern checked on a known positive); 3,345 files carry absolute Windows
   paths of the form `C:\Users\santi\projets\pulse_reliability_atlas\...` (13,273 occurrences,
   in `run_meta.json` and logs); no other user name appears.
   Then build the archives and the checksums in `preprint_npj/build/zenodo_staging/` (ignored by
   git), and check each archive against its source (file count, checksums).
   *Done 2026-10-22, 12:46–12:50:* 17 data archives (one per folder, plus the 5 files at the
   root of `data/runs/`), 0.56 GB in total; file counts equal to the source for every archive
   (16,514 in total, no difference); engine image exported as `pulse-atlas-engine:latest`, image
   ID `sha256:b2e0e807803d…` read before and after the export, gzip archive of 1,454,718,524
   bytes passing `gzip -t`; monograph copy byte-identical to `preprint/build/manuscript.pdf`.
   Checksums are written once the code archive exists (step 3).
2. *Maintainer.* Create the Zenodo draft and reserve the DOI.
3. *Agent.* Put the reserved DOI into `CITATION.cff` (`doi`, `version`, `date-released`) and
   `README.md`; commit; tag; push on the maintainer's go; rebuild the code zip from that tag.
4. *Maintainer.* Upload the files, paste the metadata the agent prepared (title, six authors
   with ORCID where known, description, licences, related identifiers: arXiv DOI
   `10.48550/arXiv.2610.28517`, GitHub repository), preview, publish.
5. *Later, at revision or proof.* The paper's Data availability statement
   (`preprint_npj/paper.tex`, the only mention of Zenodo in the paper) says the deposit "will
   be" made, together with the code and the monograph; the Code availability statement points
   to GitHub only. The DOI goes in at revision or proof, as a re-freeze; the submitted version
   is not touched.

## Decisions taken by the maintainer (2026-10-22)

- Deposit **now**, before the npj review, as **one record built by hand**, one DOI (D6, D1).
- Licences: **Apache-2.0** for the code, **CC BY 4.0** for the data and the monograph (D2).
- The raw data are deposited **as they are**: the absolute paths carrying the maintainer's
  Windows user name stay (no third party appears; raw data are never edited).

## Open decisions (maintainer)

- **D3 — version label of the tag**, e.g. `v1.0.0`.
- **D4 — Zenodo account and community**: which account deposits (yours, signed in with
  ORCID?), and whether a SADC community exists on Zenodo (not known).
- **D5 — the engine image** contains third-party software (the base system and Pulse,
  Apache-2.0). Kitware itself distributes `kitware/pulse` publicly; whether redistributing our
  derived image raises any licence question is not known.
