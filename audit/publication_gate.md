# Publication gate — the repository must be public before the paper is sent

**Opened 2026-08-20.** This register exists because the constraint it records had
no home inside git: it lived only in `TODO_publication_roadmap.md`, which
`.gitignore:103` excludes. A rule that survives only in an untracked file, or in
a conversation, is not a rule.

## 1. The constraint

The manuscript asserts, in the present tense, that the code, the audit ledger and
the per-experiment lab-notebook entries **are** openly available at
`https://github.com/santinon/pulse_reliability_atlas`.

Those sentences are true from the moment the repository is made public, and false
before it. The maintainer's decision, recorded 2026-08-17 and restated
2026-08-20, is that the release order is:

1. arXiv deposit of `paper.tex` + `supplement.tex`;
2. GitHub repository made **public**, at the same time — explicitly **before**
   npj acceptance or review, not after;
3. npj Digital Medicine submission.

Under that order the sentences are true at every moment a reader can read them.
Reversing steps 2 and 3 would publish four false statements (five before
2026-09-28, see §2).

**2026-10-20 — the public URL moved to the `sadc-lab` organisation.** On the
author's decision of 2026-10-19, the repository made public at step 2 is
`https://github.com/sadc-lab/pulse_reliability_atlas`, which received the same
`main` branch and the same six `review-*` tags on 2026-10-20 (refs compared
with the private copy: identical). `santinon/pulse_reliability_atlas` stays
private and identical. The URL quoted above is the one this register was
opened with; the paper, the supplement, `README.md`, `CITATION.cff`, the
reporting-summary draft and `SLUG` in `scripts/check_publication_gate.py` now
carry the `sadc-lab` URL. The constraint is unchanged and now applies to the
`sadc-lab` repository.

## 2. The four loci, verbatim positions

| file | line | claim |
|---|---|---|
| `preprint_npj/paper.tex` | 393 | the sampler, driver, classifier, pipeline and ledger "are released open-source" |
| `preprint_npj/paper.tex` | 414 | the codebase, including the ledger, "is released under the Apache-2.0 license at <URL>, together with the per-experiment lab-notebook entries" |
| `preprint_npj/supplement.tex` | 1073 | the experiment-log entries "are openly available under `experiments_log/`" |
| `preprint/manuscript.md` | 3690 | the numbers, figures and tables "are openly available in the …" |

Line numbers drift with editing; the guard in `scripts/audit_claims.py` counts
the loci rather than trusting these positions, and fails if the count changes.
Positions re-read on 2026-09-28.

**2026-09-28 — five loci became four.** Data availability used to say that the
code, the audit ledger and the lab-notebook entries "are already openly available
in the public code repository", while Code availability said the codebase "is
released under the Apache-2.0 license at <URL>". Both closing statements were
shortened on the author's request, and the repetition removed: the code, the
ledger and the lab-notebook entries are now stated once, in Code availability.
The present-tense claim did not disappear; it moved into that sentence, which the
gate already anchored. The constraint of §1 is unchanged.

## 3. Last verified state of the repository

**Private** (state: **Private**), verified 2026-08-18 by an unauthenticated request returning 404
against a control repository returning 200. Re-verify immediately before step 2
and again after it; a 404 for an unauthenticated reader is what "still private"
looks like, and a 200 is what "now public" looks like.

**2026-10-20 — Public.** `sadc-lab/pulse_reliability_atlas` was made public at
16:40 UTC (12:40 Montreal time), on the author's instruction, after the
co-authors were told and before the arXiv submission. Verified immediately
after: `scripts/check_publication_gate.py --verify-public` reports CLEAR (the
repository 200, the control 200, 9 / 9 anchors); unauthenticated fetches of
the repository page, of `README.md` on `main`, of `paper.tex` at the tag
`review-2026-10-19` and of the CI run cited in `HISTORY.md` return 200. The
private copy `santinon/pulse_reliability_atlas` still returns 404 to an
unauthenticated reader, as intended. Branch protection on `main`: force pushes
and deletion refused, administrators included; no pull request or status
check required.

## 4. What must be checked at the gate

- [x] arXiv deposit accepted and its identifier known. *2026-10-21:*
      arXiv:2610.28517v1 [q-bio.QM], submitted 2026-10-20, announced in the
      q-bio.QM new listings for 2026-10-21; verified against the abstract page
      (see `preprint_npj/dispatch_log.md`).
- [x] Repository visibility flipped to public, and confirmed by an
      unauthenticated fetch returning 200. *2026-10-20, section 3.*
- [ ] Zenodo DOI minted, and the availability statements updated to carry the
      DOI and the arXiv identifier — both currently say they will be added.
      *2026-10-21: the arXiv identifier is now in `README.md` and
      `CITATION.cff`; the paper's Data availability statement still says the
      preprint is on arXiv without the identifier, and the Zenodo DOI is not
      minted.*
- [x] `preprint_npj/dispatch_log.md` carries an entry for whatever build is
      deposited, pinned to the commit whose sources produced it. *Re-freeze
      64, source commit `8ff53a2`.*
- [x] Sensitive files still absent from the history: `TODO_*.md`,
      `ROADMAP_*.md`, `NEXT_SESSION*.md` and reviewer-feedback files are
      gitignored and guarded by `.githooks/pre-commit`; going public makes any
      past leak permanent, so re-check the history, not only the working tree.
      *Re-checked on 2026-10-21 over every path ever committed on every ref
      (496 distinct paths): none matches these names, `retours_chefs/` or a
      Word-family extension; the pattern caught 4 of 4 planted positives.*

## 5. Not a licensing question

Making the repository public does not change the licensing already stated: code
and lab-notebook entries under Apache-2.0, deposited data and the authors' own
monograph content under CC-BY-4.0, third-party verbatim excerpts under their
original terms. See the Data availability statement.
