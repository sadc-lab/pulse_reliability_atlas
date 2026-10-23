# Zenodo deposit — plan (2026-10-22)

Status: **published.** Record **`10.5281/zenodo.23572721`** (concept DOI `10.5281/zenodo.23572720`):
files published 2026-10-22, descriptive metadata added 2026-10-23; checks under *Published
record* below, with the one open item. Decisions already taken are marked *decided*, and the
maintainer's decisions are listed at the end.

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
   *Done 2026-10-22:* `d872524`; code archive `pulse_reliability_atlas-v1.0.0.zip` with 495
   files, the 495 files tracked at the tag; `SHA256SUMS.txt` with 21 entries (all the files of
   the record but itself).
4. *Maintainer.* Upload the files, paste the metadata the agent prepared
   (`preprint_npj/build/zenodo_metadata_a_coller.txt`, ignored by git), compare the MD5 that
   Zenodo shows with the agent's list, preview, publish.
   *Done 2026-10-22:* 21 files uploaded in the browser; the engine image (1,454,718,524 bytes)
   did not complete in the browser and was uploaded through the Zenodo API by a script the
   maintainer ran; the MD5 and sizes of all 22 files equalled the agent's list before
   publishing; published at 22:21:53 UTC with files, title, type, date, creator (ORCID) and
   both licences. *Completed 2026-10-23:* the prepared metadata were sent through the Zenodo API
   into an edit draft (script run by the maintainer, nothing published by it), read back, then
   published by the maintainer in the browser at 17:05:33 UTC. The API token was revoked
   afterwards.
5. *Agent, after publication and on the maintainer's go.* Push `main` and the tag `v1.0.0` to
   both remotes. Publishing before pushing keeps a dead DOI out of the public repository if the
   publication failed; the GitHub link in the record (`tree/v1.0.0`) answers once the tag is
   pushed. The tag is the same object either way.
   *Done 2026-10-22:* `main` at `d872524` and the tag pushed to both remotes. The annotated tag
   was re-created on the same commit before the push (tag object `a065ecd`); the code archive
   depends on the commit only, and the archive rebuilt from the new tag has the deposited MD5
   (`c6eb78ca…`).
6. *Later, at revision or proof.* The paper's Data availability statement
   (`preprint_npj/paper.tex`, the only mention of Zenodo in the paper) says the deposit "will
   be" made, together with the code and the monograph; the Code availability statement points
   to GitHub only. The DOI goes in at revision or proof, as a re-freeze; the submitted version
   is not touched.

## Published record (checked 2026-10-23)

Read on the public API in the InvenioRDM format (revision 6, updated 2026-10-23 17:05:33 UTC),
on the public page and at DataCite. The default API answer and the answer to the edit request
use an older format that shows only the first affiliation, the first licence and the funding
entries that carry an award number; every check below uses the InvenioRDM format.

- DOI unchanged; title, type Dataset, publication date 2026-10-22, version `v1.0.0`, language
  English; public, no embargo; no new version created.
- Description identical to the text prepared (string comparison; a one-character change is
  caught). Its abstract equals the arXiv abstract word for word (arXiv API, 147 words), and its
  "16,514 files" equals the count of files in `data/runs/` (`find`, 2026-10-23).
- Creator Santino Nanini, ORCID, two affiliations by ROR identifier (CHU Sainte-Justine,
  Université de Lorraine). Contributors: Y.M. (Researcher); A.W., C.S., P.J. and M.S.
  (Supervisor).
- Licences CC BY 4.0 and Apache-2.0. Eight keywords.
- Funding, four entries: Agence Nationale de la Recherche with award ANR-23-IACL-0004 (not in
  Zenodo's award list, so entered by title and number; the same search finds a known ANR
  award); Région Grand Est (ROR); CHU Sainte-Justine Foundation and R-SADC by name (not in
  Zenodo's funder list).
- Related works, both "is supplement to": the arXiv DOI and `tree/v1.0.0` on GitHub. Software
  fields: repository URL, Python, active.
- 22 files; MD5 equal to the agent's list, none missing and none extra (an altered MD5 is
  caught).
- Links answer: `tree/v1.0.0` and the repository (200), the arXiv DOI (302 to the abstract
  page, 200), the record DOI (302 to Zenodo).
- DataCite updated at the same second: two affiliations, four funders, one award number,
  five contributors (1 Researcher, 4 Supervisor), eight subjects, two rights, three related
  identifiers (two IsSupplementTo, one IsVersionOf the concept DOI).

**Open: the engine image ID.** The description and `README_zenodo.md` name the image
`sha256:b2e0e807803d…`. In the deposited archive that digest is the image index listed in
`index.json`; `manifest.json` gives the configuration digest `sha256:eddbac488c01…`. The
maintainer's Docker (28.4.0, containerd image store) shows `b2e0e807803d…` as the image ID
(`docker image inspect`, 2026-10-23). A Docker using the classic image store is expected to
show the configuration digest instead after `docker load`; this was not tested. Not an error,
but a reader may not find the announced ID. *Decided 2026-10-23:* recorded here; a sentence
giving both digests goes into the record's description at its next update.

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
