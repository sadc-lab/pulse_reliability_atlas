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
