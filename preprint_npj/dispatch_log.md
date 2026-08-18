# Dispatch log — which build was sent, and when

The `.docx` and `.pdf` twins are build artefacts: `preprint_npj/build/` is
gitignored, so nothing in git records *which* rendering a reader actually
received. If `paper.tex` moves on afterwards, an annotated copy becomes
impossible to place in the history.

This file closes that gap. One entry per outgoing dispatch, appended, never
edited in place. Each entry pins the artefact to a commit by content hash, so a
returned copy can always be matched back to the source that produced it.

**Verifying an entry.** From the repository root:

```bash
sha256sum preprint_npj/build/paper.docx preprint_npj/build/supplement.docx
git log -1 --format=%H
```

Rebuild the same commit with `preprint_npj/build_npj.ps1` if the files are gone.
Note that a rebuild does **not** have to reproduce the hash byte-for-byte —
pandoc and pdfTeX embed timestamps unless `SOURCE_DATE_EPOCH` and
`FORCE_SOURCE_DATE=1` are set. The hash proves *identity of a specific file*,
the commit SHA proves *identity of the source*. Use both together.

---

## 2026-08-18 — co-author review round (paper + supplement, DOCX)

| Field | Value |
|---|---|
| Source commit | `530d281940087e5563134c90234d4fdc37f18078` |
| Commit date | 2026-08-18 11:59:10 +0200 |
| Built | 2026-08-18 11:56 (sources unchanged between build and commit; working tree clean at commit) |
| Format sent | `.docx` (annotation-friendly); `.pdf` twins built from the same run |

| Artefact | SHA-256 | Bytes |
|---|---|---|
| `build/paper.docx` | `cd27fe7b29de980f2928373117ea68783984488da225a8ba2ecd52145c8a8fb2` | 960,464 |
| `build/supplement.docx` | `f0cdea31be91bf8c0704db302ce47c272198990195400cce8905c9912d0286c0` | 743,106 |
| `build/paper.pdf` | `e4ce57040e3a34617960d539bcb48c81c020cb72d134aa0eb3320ba0e5af47f0` | 711,520 |
| `build/supplement.pdf` | `97979bbcfdab0f91812e568021d527153c4557d6edeae825da38190529c2623e` | 668,908 |

**State of the manuscript at this commit.**

- Claims ledger: 382 / 382 anchors PASS, 94 / 94 paper-sync entries, 0 FAIL.
- Render check: PASSED, 4 accepted pre-existing residues, 0 new.
- Abstract: 149 / 146 words under the register's two conventions (npj cap 150).
- Paper: 36 pages, no near-empty page, minimum body page 263 words.
- `paper.docx` carries 10 media objects for 10 `\includegraphics`, 9 captions,
  all located and in source order. `supplement.docx` carries 5 for 5, and all
  21 captions, in order.

**Known open items at dispatch time**, so returning comments can be read against
them rather than re-reporting them:

- `supplement.tex` §S5 states that pediatric compliance per kilogram, airway
  resistance and gas-exchange surface "differ substantially" without a citation;
  `paper.bib` holds no pediatric source. Left standing deliberately — it needs a
  reference read in full, not a hedge.
- The four-flag classifier is called a "steady-state detector" throughout, but
  only two of its four flags are computed on the steady-state window; `clamped`
  reads the setup log and `diverged` reads the exit status. A rename to
  "run classifier" is pending a separate pass (11 occurrences plus `src/detector.py`).
- Mean sentence length is 30.6 words against a typical 20–25. The paragraph
  structure was fixed on 2026-08-17; sentence length was not, because shortening
  sentences is rewriting and cannot be verified by a token-identity check.
- The Zenodo DOI and arXiv identifier are not yet minted; availability statements
  say so.

---

## 2026-08-18 — co-author review round, second build (paper + supplement, DOCX)

Supersedes the entry above. The four artefacts sent on 2026-08-18 at 11:56 were
never dispatched; a joint reading pass with the maintainer landed 27 corrections
first (commit `b5ce9f9`), so the earlier hashes are stale. Keep the entry above
for traceability, use this one for anything actually sent.

| Field | Value |
|---|---|
| Source commit | `b5ce9f9749a6c97c0f3c20609fa876f3e43f18c7` |
| Commit date | 2026-08-18 16:47:00 +0200 |
| Built | 2026-08-18, from a tree identical to the commit (only the four edited sources differed from `530d281`, and all four are in the commit) |
| Format sent | `.docx` (annotation-friendly); `.pdf` twins built from the same run |

| Artefact | SHA-256 | Bytes |
|---|---|---|
| `build/paper.docx` | `1c51fb5911cd2008744326dd4c6011d5c18dbc1507b2c889d762cf65374f5ff3` | 960,461 |
| `build/supplement.docx` | `7a7c6fdefbfb2e24f40cbf0880e6287c68834f71071bf9ba1a7c253752fefd37` | 743,153 |
| `build/paper.pdf` | `8dfe7726bbd0915217e4e57e10d7f508d6749422f8d435008a998318f8a2e090` | 711,514 |
| `build/supplement.pdf` | `9e34b466526e3a9ade1553d6c247239eabcf2450c4e23b890f899a3149e504a1` | 669,127 |

**State of the manuscript at this commit.**

- Claims ledger: 382 / 382 anchors PASS, 0 FAIL, every guard green.
- Render check: PASSED, 4 accepted pre-existing residues, 0 new.
- Build logs: 0 undefined citations, 0 undefined references, both documents.
- Abstract: 150 / 147 words under the register's two conventions (npj cap 150).
- Paper: 36 pages, thinnest qualifying body page 433 words; all five figures
  render within the call-to-figure bound.
- Supplement: 52 pages, thinnest qualifying body page 287 words.
- `paper.docx` carries 10 media objects for 10 `\includegraphics` and locates 8
  of 9 captions uniquely (the ninth, "figure: hr", is ambiguous by string
  matching, not missing), all in source order. `supplement.docx` carries 5 for 5
  and all 21 captions, in order. The checking script was calibrated on a
  known-present and a known-absent control before its output was believed.

**Closed since the previous entry** — do not re-report these:

- The pediatric mechanics claim in `supplement.tex` §S5 and its two counterparts
  in the monograph were **removed**, not hedged. Papastamelos et al. 1995 shows
  the per-kilogram developmental difference is in *chest-wall* compliance and
  converges to the adult relationship by the second year of life, so a blanket
  pediatric-vs-adult statement was wrong rather than merely unsourced.
- The `detector` / `classifier` naming is harmonised. The four-flag object is now
  "classifier" throughout the prose; "detector" survives only where it names the
  narrower log-based rejection detector, a LaTeX label, or the `src/detector.py`
  module.

**Known open items at dispatch time**, so returning comments can be read against
them rather than re-reporting them:

- Mean sentence length is 30.6 words against a typical 20–25. Paragraph structure
  was fixed on 2026-08-17; sentence length was not, because shortening sentences
  is rewriting and cannot be verified by a token-identity check.
- Supplement Figure S5 renders 13 pages after its single call. Closed without
  action by maintainer decision on 2026-08-18: moving the figure block would
  renumber all five supplement figures, and `Figure S5` is hard-coded in nine
  ledger anchors, two prose documents and three generator filenames. The
  pagination guard prints the distance at every run but does not gate it in the
  supplement.
- The Zenodo DOI and arXiv identifier are not yet minted; the availability
  statements say so.
