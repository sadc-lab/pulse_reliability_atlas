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
2. *Maintainer.* Create the Zenodo draft and reserve the DOI. *Done 2026-10-22:* reserved DOI
   **`10.5281/zenodo.23572721`**, read on the maintainer's screenshot and then pasted by the
   maintainer as text (both agree); draft saved with type Dataset and the title above.
3. *Agent.* Put the reserved DOI into `CITATION.cff` (`doi`, `version`, `date-released`) and
   `README.md`; commit; annotated tag `v1.0.0`, both **local**; build the code archive from the
   local tag (`git archive`), `README_zenodo.md` and the checksums.
4. *Maintainer.* Upload the files, paste the metadata the agent prepared
   (`preprint_npj/build/zenodo_metadata_a_coller.txt`, ignored by git), compare the MD5 that
   Zenodo shows with the agent's list, preview, publish.
5. *Agent, after publication and on the maintainer's go.* Push `main` and the tag `v1.0.0` to
   both remotes. Publishing before pushing keeps a dead DOI out of the public repository if the
   publication failed; the GitHub link in the record (`tree/v1.0.0`) answers once the tag is
   pushed. The tag is the same object either way.
6. *Later, at revision or proof.* The paper's Data availability statement
   (`preprint_npj/paper.tex`, the only mention of Zenodo in the paper) says the deposit "will
   be" made, together with the code and the monograph; the Code availability statement points
   to GitHub only. The DOI goes in at revision or proof, as a re-freeze; the submitted version
   is not touched.

## Decisions taken by the maintainer (2026-10-22)

- Deposit **now**, before the npj review, as **one record built by hand**, one DOI (D6, D1).
- Licences: **Apache-2.0** for the code, **CC BY 4.0** for the data and the monograph (D2).
- The raw data are deposited **as they are**: the absolute paths carrying the maintainer's
  Windows user name stay (no third party appears; raw data are never edited).
- Tag and version label: **`v1.0.0`** (D3).
- Deposited from the maintainer's **own Zenodo account**; no community (D4).
- The **engine image is included** (D5). The record's description states that the third-party
  software inside it (the Pulse Physiology Engine, Apache-2.0, and its base system) keeps its
  own licence, as the paper's Data availability statement does for third-party excerpts.
  Whether redistributing the derived image raises any further licence question is not known.
- **Creator: Santino Nanini** alone, as in the `authors` of `CITATION.cff`. **Contributors:**
  Y.M. (reproduced the full sweep), A.W., C.S., P.J. and M.S. (supervision), the five
  co-authors of the paper. The six-author paper is linked through its arXiv DOI.
