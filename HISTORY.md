# History of this repository

This repository was private while the work was carried out. Before it was
made public, in October 2026, its git history was rewritten once and pushed
to a new repository under the same name. The same history, unchanged, was
then pushed to this repository, in the `sadc-lab` organisation. This file
says what changed, why, and how the change can be checked.

## What was kept

Every commit of the `main` branch, in the same order, with the same parents,
the same author and committer names and the same dates. Commit messages,
code, data, results, figures, the manuscript sources and the audit registers
are unchanged apart from the edits listed below. Only the `main` branch was
published.

## What was edited

1. **Private correspondence.** Private messages quoted verbatim in a few working
   files (audit registers, the dispatch log, one script comment) and in a
   few commit messages are replaced by the mention "text of a private message
   removed from the public history; see HISTORY.md". The analysis around them
   is kept. Short phrases quoted from the same messages are replaced by a
   plain paraphrase.
2. **A co-author's annotations on a draft.** In the register of the August
   2026 synthesis pass and in a few commit messages, the wording of one
   co-author's comments, notes and tracked changes is replaced by a neutral
   description. The analysis, and the text of ours that it quotes, are kept.
3. **Names in working notes.** In commit messages and working files, two
   co-authors are referred to by their initials (P.J., C.S.). Author lists,
   affiliations, ORCID identifiers and contribution statements are
   unchanged. For the same reason the register of the August 2026 synthesis
   pass is `audit/synthesis_pass_2026_08.md` in every commit.
4. **Third parties.** A person who was planned as a second contributor and
   withdrew before contributing is referred to as "the second contributor"
   (lab-notebook folder `experiments_log/contributor2/`). The name of a person
   outside the author list is removed from one ignore rule and one commit
   message. A local user name in one reproduction log is replaced by
   `<user>`, and the e-mail address in the metadata of five commits by the
   address their author asked for.
5. **The AI assistant's instruction file.** `CLAUDE.md`, and an older copy of
   it kept in `attic/`, are removed from every commit. The seven commits that
   changed only these files are kept, now empty, with their messages. The
   file's table of verified Pulse limitations, which dated registers cite by
   number, is published unchanged as
   [`reference/verified_limitations_table.md`](reference/verified_limitations_table.md).

## Why a new repository

Rewriting a GitHub repository in place does not make its old history
disappear: old commits stay reachable through closed pull requests and the
list of past Actions runs until GitHub Support purges them. Pushing the
rewritten `main` branch to a new repository is the one way, under our own
control, to make sure that the public repository serves nothing else. The
original history is kept, private and unchanged, and can be made available
to editors and reviewers on request.

## Old and new commit identifiers

A rewrite changes every commit identifier. Identifiers quoted in commit
messages were translated to the new ones wherever they designate a commit of
this history. Identifiers quoted inside files (audit registers, the
experiment log, the dispatch log) are dated records and were not edited:
they are the former identifiers. The table
[`history/commit-map.txt`](history/commit-map.txt) gives, for each former
identifier, the new one. It also covers an earlier rewrite of the private
repository, in June 2026, which removed internal working files and a third
party's personal data, so identifiers quoted from before that date resolve
too.

## Fingerprints of the original history

- Last commit of the original `main` branch:
  `10d9440294313452fddcb7a3580a49439f13a1aa` (19 October 2026).
- SHA-256 of a git bundle of that branch, kept with the original:
  `29151d5e2bdca21c1bfde1937f31929fb97963c4f1a364ee8fc77f25a09656dd`.
- Every commit of the published history was compared with its original by
  an independent script: same parents, same names and dates, and content and
  messages identical byte for byte apart from the edits listed above and the
  translated commit identifiers. The script, and the test showing that it
  fails on a single changed byte, are kept with the original.
- The first run of the test workflow on this repository, on the rewritten
  history, passed:
  https://github.com/sadc-lab/pulse_reliability_atlas/actions/runs/39452105545
