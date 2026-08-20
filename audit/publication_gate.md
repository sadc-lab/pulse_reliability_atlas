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
Reversing steps 2 and 3 would publish five false statements.

## 2. The five loci, verbatim positions

| file | line | claim |
|---|---|---|
| `preprint_npj/paper.tex` | 454 | the sampler, driver, classifier, pipeline and ledger "are released open-source" |
| `preprint_npj/paper.tex` | 475 | code, ledger and lab-notebook entries "are already openly available in the public code repository" |
| `preprint_npj/paper.tex` | 479 | the codebase "is released under the Apache-2.0 license at <URL>" |
| `preprint_npj/supplement.tex` | 941 | the experiment-log entries "are openly available under `experiments_log/`" |
| `preprint/manuscript.md` | 3579 | the numbers, figures and tables "are openly available in the …" |

Line numbers drift with editing; the guard in `scripts/audit_claims.py` counts
the loci rather than trusting these positions, and fails if the count changes.

## 3. Last verified state of the repository

**Private** (state: **Private**), verified 2026-08-18 by an unauthenticated request returning 404
against a control repository returning 200. Re-verify immediately before step 2
and again after it; a 404 for an unauthenticated reader is what "still private"
looks like, and a 200 is what "now public" looks like.

## 4. What must be checked at the gate

- [ ] arXiv deposit accepted and its identifier known.
- [ ] Repository visibility flipped to public, and confirmed by an
      unauthenticated fetch returning 200.
- [ ] Zenodo DOI minted, and the availability statements updated to carry the
      DOI and the arXiv identifier — both currently say they will be added.
- [ ] `preprint_npj/dispatch_log.md` carries an entry for whatever build is
      deposited, pinned to the commit whose sources produced it.
- [ ] Sensitive files still absent from the history: `TODO_*.md`,
      `ROADMAP_*.md`, `NEXT_SESSION*.md` and reviewer-feedback files are
      gitignored and guarded by `.githooks/pre-commit`; going public makes any
      past leak permanent, so re-check the history, not only the working tree.

## 5. Not a licensing question

Making the repository public does not change the licensing already stated: code
and lab-notebook entries under Apache-2.0, deposited data and the authors' own
monograph content under CC-BY-4.0, third-party verbatim excerpts under their
original terms. See the Data availability statement.
