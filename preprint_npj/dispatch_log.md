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

---

## 2026-08-19 — co-author review round, third build (paper + supplement, DOCX)

Supersedes both entries above. The `b5ce9f9` artefacts were never dispatched
either: four more reading blocks landed after them (`bfc3de5`, `f71c812`,
`466a21c`), so their hashes are stale. Keep the earlier entries for traceability,
use this one for anything actually sent.

| Field | Value |
|---|---|
| Source commit | `466a21c5fc3441c54e0e8b6cbd1b43ad0942c410` |
| Commit date | 2026-08-19 00:57:25 +0200 |
| Built | 2026-08-19, working tree clean at build time (both `build/` trees are gitignored) |
| Format sent | `.docx` (annotation-friendly); `.pdf` twins from the same run |

| Artefact | SHA-256 | Bytes |
|---|---|---|
| `preprint_npj/build/paper.docx` | `68f1b403d6bff2d7283e42f46b1566dcc9cd2e668a76f0e5266addd839abde98` | 960,436 |
| `preprint_npj/build/supplement.docx` | `35a99711ba9159d9b1b639d4c78866f43054141701462526836d67e473847d8e` | 743,153 |
| `preprint_npj/build/paper.pdf` | `eb4e9cac0dba8e774f9c057693ae5d19a9f1919c250e8fcefe6b9dc3dd6da750` | 711,348 |
| `preprint_npj/build/supplement.pdf` | `a9942b642292ebfdcf37e6f7ff9636bfd9d86dc4a6ce837169103562ec2af636` | 669,127 |

The companion monograph was rebuilt in the same pass (`preprint/build/manuscript.pdf`
and `.docx`), because `manuscript.md` also changed; it is not part of the
co-author dispatch and is not hashed here.

**State of the manuscript at this commit.**

- Claims ledger: 382 / 382 anchors PASS, 0 FAIL, script exit 0.
- New guard since the last entry: `check_vtcv_scenario_split`, 9 / 9 PASS. It
  re-derives Section 2.2's "139 of 320" and "36 of 320" from the aggregated
  parquet with columns resolved by name, checks the quoted denominators, proves
  its own sensitivity to the 0.05 threshold with a negative control, and was
  falsified before being trusted (a wrong expected value makes it FAIL and the
  script exit 1).
- Render check: PASSED, 4 accepted pre-existing residues, 0 new.
- Abstract: 150 / 147 words under the register's two conventions (npj cap 150).
- Paper: 36 pages, thinnest qualifying body page 433 words.
- Supplement: 52 pages, thinnest qualifying body page 287 words.
- `paper.docx` carries 10 media objects for 10 `\includegraphics` and locates 8
  of 9 captions uniquely (the ninth, "figure: hr", is ambiguous by string
  matching, not missing). `supplement.docx` carries 5 for 5 and all 21 captions.
  Both in source order; the checker was calibrated on a known-present and a
  known-absent control before its output was believed.

**⚠️ The reading pass was NOT complete when this build was made.** Sections
reviewed so far: Abstract, Introduction, Results §2 / §2.1 / §2.2 including their
tables, figures and legends, and the closing Discussion paragraphs. Sections
§2.3 through §2.6, the Methods and the Supplement body have not yet had the same
line-by-line pass. Reviewer comments on those sections are expected and are not
duplicates of anything already found.

**Closed since the previous entry** — do not re-report:

- Three announced cardinals that did not match what followed them: "Three
  implementation choices" (Introduction), "Four cross-output patterns" (§2.2)
  and "Two implausibility bounds" (§2.1). The first two became "Several"; the
  third became "channels", because there the count is exactly right at the
  channel level. Three instances in three sections suggests a writing habit
  rather than three accidents; remaining sections should be read with that in
  mind.
- The `not_steady_state` "two regimes" sentence, which read as a claim about
  counts that Table 3 contradicts (S2 carries 137 flags against S4's 118). It
  now states what was actually meant, about mechanisms at opposite ends of the
  severity axis.
- The Cornish attribution: his 15-channel panel contains no renal channel, and
  glucose carries 5 of 85 Hoeffding rejections against 63 for the electrolytes.
- The rounding-granularity constant in Table 4's legend, 0.125 -> 0.625, in the
  paper and the monograph both.

**Known open items at dispatch time:**

- Mean sentence length is 30.6 words against a typical 20-25.
- Supplement Figure S5 renders 13 pages after its single call; closed without
  action by maintainer decision on 2026-08-18, because moving the block would
  renumber all five supplement figures and `Figure S5` is hard-coded in nine
  ledger anchors, two prose documents and three generator filenames.
- The Zenodo DOI and arXiv identifier are not yet minted; the availability
  statements say so.

---

## 2026-08-20 — co-author review round, fourth build (paper + supplement, DOCX)

Supersedes every entry above. The 2026-08-19 artefacts were not dispatched
either: §2.3, §2.4, §2.5 and §2.6 were read after them and five commits landed
(`6d2ba12`, `306dd22`, `44024b0`, `3ef081c`, `2139743`).

| Field | Value |
|---|---|
| Source commit | `2139743` |
| Built | 2026-08-20, before the dispatch entry was written |
| Format sent | `.docx`; `.pdf` twins from the same run |

| Artefact | SHA-256 | Bytes |
|---|---|---|
| `preprint_npj/build/paper.docx` | `ef9ea834b0cbc8c5f9390ed463ec7e869c30374961256899ecf48a12b7dac284` | 961,477 |
| `preprint_npj/build/supplement.docx` | `e2b607fb055f1baa2e842c58d61710d9dd581945d4333d0eee39d7c6bc11dacc` | 743,152 |
| `preprint_npj/build/paper.pdf` | `be0d3fb5dbeddb2c9dee9c4c14d8b763bb78412df34bfa425a40574eb556e339` | 714,976 |
| `preprint_npj/build/supplement.pdf` | `bed84c43b28b25c23c4604f8311bdf79ffaabcaa32df21fdb21d08e68c192a4a` | 669,127 |

The monograph was rebuilt in the same pass; it is not part of the co-author
dispatch and is not hashed here.

**State at this commit.** Claims ledger 382 / 382, 0 FAIL, exit 0. Render check
PASSED, 4 accepted residues, 0 new. Build logs carry 0 undefined citations and 0
undefined references. Abstract 150 / 147 against the npj cap of 150. Paper **37
pages** (36 in the previous build; §2.6 gained two items), thinnest qualifying
body page 433 words. Supplement 52 pages, thinnest 287. DOCX structure check
passed with its calibration controls green.

**Guards added since the previous entry**, each falsified on the value that would
actually be wrong rather than an arbitrary one:

- Vt-CV scenario split (139 / 36) plus the S014 gate statistic (+0.326, kept
  distinguishable from the 0.335 difference of medians that was once quoted in
  its place), and a reported-not-pinned per-scenario profile.
- The 38 physiologically converged S1 reruns, with the partition 38 + 3 + 3 = 44
  and 38 + 3 = 41, and a check that the 38-run and 41-run populations stay
  distinct.
- The Wasserstein raw-exceedance count (6), under BOTH readings of "exceeds its
  permutation null", with the BH-removed comparison named.

**⚠️ The reading pass is still incomplete.** Read so far: Abstract,
Introduction, §2 and §2.1 through §2.6 with their tables, figures and legends,
and the closing Discussion paragraphs. NOT yet read line by line: the Methods
§4, and the Supplement body. Reviewer comments there are expected.

**Substantive corrections since the previous entry** — do not re-report:

- §2.5 attributed the BH-survivor count to the raw permutation test. Six
  comparisons clear the raw null; five survive correction; S2 SpO2 is removed at
  p = 0.0215 against a BH critical value of 0.0125. Both counts are now stated.
- §2.4 said the 20 mmHg gap "rules out a runaway" while the same section reports
  six runaway reruns, three of them inside the very median quoted. Bounded to
  "a cohort-wide oxygenation runaway".
- §2.4 attributed the t = 180 s statistic to "the healthy cohort"; it belongs to
  the 38 physiologically converged reruns, and excluding the runaways is what
  makes the statistic meaningful.
- §2.3's "fades as ARDS severity rises" implied a monotonicity the data does not
  show (139, 89, 36, 39); now "falls markedly with increasing ARDS severity".
- §2.6 gained the preregistered Sobol deviation (triggered on 43 of 48
  combinations, 11,008 runs against a 1,500-run cap) and the SpO2 flatline edge
  case (232 trigger occurrences, not 232 runs). The cross-sex Spearman rho moved
  from a Discussion limitation into §2.5.

**Known open items:** mean sentence length 30.6 words; Supplement Figure S5 at 13
pages from its call, closed without action; Zenodo DOI and arXiv identifier not
yet minted.

---

## 2026-08-20 (second build) — co-author review round

Supersedes the entry above, made a few hours earlier the same day: §2.2's SHAP
sentence and §2.3's run-identifier gloss landed afterwards in `6b78aa3`.

| Field | Value |
|---|---|
| Source commit | `6b78aa3` |
| Format sent | `.docx`; `.pdf` twins from the same run |

| Artefact | SHA-256 | Bytes |
|---|---|---|
| `preprint_npj/build/paper.docx` | `95943ccf02e517814a29a73e6b38a9bb1414e4f203f9da6e4208d48a56ef6833` | 961,600 |
| `preprint_npj/build/supplement.docx` | `7323375ef2df64d4455cc0e8be0757d632607ae90a14757b2cc5b799951f7a28` | 743,152 |
| `preprint_npj/build/paper.pdf` | `520bd94aad5f2723aa189bae9856090ea90db914327d30784046c1006e7bb100` | 715,354 |
| `preprint_npj/build/supplement.pdf` | `81e739263f3e02205861a4f602b74bfe165832b50103dbdb2982886c2b5251ce` | 669,127 |

**State.** Claims ledger 382 / 382, 0 FAIL, exit 0. Render check PASSED, 4
accepted residues, 0 new. Build logs: 0 undefined citations, 0 undefined
references — checked specifically because this build adds the first citation of
`lundberg2017` in the paper, and `Lundberg` is present in the rendered
bibliography. Paper 37 pages; supplement 52. DOCX structure check passed with its
calibration controls green.

**Corrections since the previous entry.** §2.2 described a SHAP cross-check with
no citation, at an unstated level of agreement, and concluded with a causal
attribution the Supplement does not license. It now cites `lundberg2017`, states
that SHAP places 17 of the 18 Morris top-three inputs in its own top three across
the six outputs, and concludes only that the skew is unlikely to be specific to
the elementary-effects design. §4's "independently cross-verified" became "also
supported by the secondary SHAP analysis". §2.3's `S1_F_0117` is glossed as
"run index 117 in the healthy-female cell".

**Guard added:** the SHAP pooled-agreement UNIT, not its value. The statistic is
a set intersection summed over six outputs, maximum 18; it ignores order inside
the top three. Two candidate rewrites of the sentence would have described a
rank-based measurement the code does not perform, and a guard on the value 17
alone would have accepted both.

**⚠️ The reading pass remains incomplete.** Methods §4 and the Supplement body
have not been read line by line.

---

## 2026-08-20 (third build) — co-author review round

Supersedes the two entries above from the same day. Four commits landed after the
second build: `f237bfd`, `67ad7b7`, `7c3676d` and this entry's own predecessor.

| Field | Value |
|---|---|
| Source commit | `7c3676d` |
| Format sent | `.docx`; `.pdf` twins from the same run |

| Artefact | SHA-256 | Bytes |
|---|---|---|
| `preprint_npj/build/paper.docx` | `29faacbbc5eb1e1b7100678a9dcf6ce0994f0ae4efcba85ae504eade6aaec5d4` | 961,613 |
| `preprint_npj/build/supplement.docx` | `ab98b86bbd9e22f2f3e47fbfc5f906f9f91d9d965ab6b08bce1fceeab18d76cd` | 743,152 |
| `preprint_npj/build/paper.pdf` | `4935a80c072d640df59735ba2197846408f03781c1d36c2ec7007b9e00951fe9` | 715,487 |
| `preprint_npj/build/supplement.pdf` | `5b12b47a5e56301a2cfb52da5c5fdd86392db5f773d6f36e9de8fb3ae24b297b` | 669,127 |

**State.** Claims ledger 382 / 382, 0 FAIL, exit 0. Render check PASSED, 4
accepted residues, 0 new. Build logs: 0 undefined citations, 0 undefined
references. DOCX structure check passed with calibration controls green. Paper 37
pages, supplement 52.

**Corrections since the previous entry.**

- §4.4's opening sentence still called the four-flag object a "detector" while
  the subsection title called it a "classifier"; two further loci said the same
  (§2.4 and Code availability). All three now say classifier. One locus was
  deliberately left alone: "detector self-consistency" quotes preregistered pilot
  criterion 2, which preregistration.md:178 names "Detector self-consistent" and
  which that document forbids editing silently.
- §2.5 now points at Methods §4.6 for the Wasserstein and Benjamini-Hochberg
  definitions. The Results referenced the Supplement constantly and the Methods
  never, although the plain-language glosses live in the Methods.
- `audit/patient_baseline_rebaselining.md` carried a header saying its disclosure
  was "drafted, not applied" while its own §7 recorded it as applied on
  2026-08-14 and the sentence was live in the paper.

**Guards added:** a detector/classifier vocabulary guard that checks BOTH
directions -- banned phrasings absent, legitimate senses present, and the
preregistration still carrying the criterion name the paper quotes.

**Sections read so far:** Abstract, Introduction, §2 and §2.1-§2.6, §4.1-§4.4,
and the closing Discussion paragraphs, with their tables, figures and legends.
**NOT yet read line by line: §4.5 onward, and the Supplement body.**

---

## 2026-08-20 (fourth build) — co-author review round

Supersedes every entry above. Built from a clean working tree at `f5ed1db`, with
the complete gate run before hashing.

| Field | Value |
|---|---|
| Source commit | `f5ed1db5950420ec7767dd71cca6851b01d52a98` |
| Format sent | `.docx`; `.pdf` twins from the same run |

| Artefact | SHA-256 | Bytes |
|---|---|---|
| `preprint_npj/build/paper.docx` | `a2db1089b67ff4292121096e4729850a64f980556252157f07889920d5398c41` | 961,557 |
| `preprint_npj/build/supplement.docx` | `7a0e6c58e02acddcfc5d6bb9ea5aa9bfb4ffd19ffb561bb41cbc16dc1687e321` | 743,476 |
| `preprint_npj/build/paper.pdf` | `93fabfa7e711da1988a7d5f8b48c4cd5d8d0bcba8dd268bbd5978a46d23c5c30` | 702,452 |
| `preprint_npj/build/supplement.pdf` | `bc8686da3dc6a0e9512852d28ec9eacfea2d650598e2ebc23d08fb49c50300ce` | 669,690 |

**On what the pinned SHA means.** `f5ed1db` is the commit whose SOURCES produced
these files. It is not a commit containing them: `preprint_npj/build/` and
`preprint/build/` are gitignored (`.gitignore:68` and `:60`), so no commit ever
carries a built artefact. The SHA identifies the source; the hash identifies the
file. The commit that adds this entry is deliberately NOT the pinned one.

**Gate run before hashing, in full rather than the bare claims script.**

- Claims ledger 382 / 382, sync 94 / 94, monograph anchors 26 / 26, exit 0.
- Fifteen guards, all green, including the four added during this reading pass:
  Vt-CV scenario split (13), SHAP pooled-agreement unit (5),
  detector/classifier vocabulary (18) and CDC body-weight provenance (12).
- Render check PASSED, 4 accepted residues, 0 new.
- DOCX structure check passed with its calibration controls green.
- 0 undefined citations and 0 undefined references in both build logs.
- Paper 37 pages, thinnest qualifying body page 433 words; supplement 52 pages,
  thinnest 298. All nine figures render within their call-distance bound.
- All six artefacts verified present, non-empty, and newer than every source
  file that feeds them.

The monograph was rebuilt in the same pass. It is not part of the co-author
dispatch and is not hashed here.

**Substantive corrections since the previous entry.**

- The CDC body-weight provenance was wrong in three documents, and wrongly
  declared the preregistration's erratum inaccurate. The weights ARE the CDC P50
  at exactly 18.0 years (`Agemos` = 216.5, the 216.0-216.99-month interval);
  67.64 / 56.41 kg belong to `Agemos` = 218.5, that is 18 y 2 m. No simulated
  quantity changes. See `audit/cdc_weight_provenance_mismatch.md`.
- §2.6's flatline paragraph attributed SpO2 pinning to health alone; a healthy
  subject on room air sits near 96 % and does not trigger. The rule needs
  variability below 1 % of the mean AND a mean within 0.1 % of a bound, and the
  ceiling is reached as inspired oxygen rises.
- §2.2's SHAP sentence gained its citation, named what the 17-of-18 agreement
  counts, and dropped a causal attribution the Supplement does not license.
- §4.4 no longer prints the clamp regexes; they have one guarded home in
  Supplement §S3.3.

**⚠️ The reading pass is still incomplete.** Read: Abstract, Introduction,
§2 and §2.1-§2.6, §4.1-§4.5, and the closing Discussion paragraphs, with their
tables, figures and legends. NOT read line by line: §4.6 onward, and the
Supplement body. Reviewer comments there are expected rather than duplicates.

## 2026-08-25 — co-author review round (paper + supplement + monograph, PDF + DOCX)

Supersedes every entry above. This is the dispatch the co-authors are reading.

| Field | Value |
|---|---|
| Sent | 2026-08-25, 19:18 France time, from Paris |
| Recipients | the four supervising co-authors |
| Source commit | `613f2a621803489f1b7ffa157a5e33eec48d864c` |
| Format sent | `.pdf` and `.docx` |
| Artefacts | paper, supplement, and the companion technical monograph |
| Pages at dispatch | 38 (paper) / 52 (supplement) / 119 (monograph) |
| Gate state at dispatch | green: 382 anchors, 94 crosswalk rows |

**No SHA-256 hashes for this dispatch, and they cannot be recovered.** Every
earlier entry pins the artefacts by hash; this one cannot. `preprint_npj/build/`
and `preprint/build/` are gitignored, so no commit carries a built file, and both
directories have since been overwritten by later rebuilds. Rebuilding `613f2a6`
today would produce hashes of a *reproduction*, not of the files that were sent,
and recording those in this column would assert something false. The source
commit is pinned instead, which is what identifies the content; the bytes that
left the machine are no longer identifiable.

**Entry written 2026-09-03**, from the author's own record of the send, nine days
after the fact. The delay is itself the reason the hashes are gone: the log was
not filled at dispatch time, and the build directories did not survive the wait.
Later dispatches should be logged before the next build runs.

**The manuscript has moved since.** Anything in the copies the co-authors hold is
pinned to `613f2a6` and no longer matches the working tree: as of 2026-09-03 the
paper renders 24 pages against 38, and its reference list 21 entries against the
40 distinct keys the dispatched source cites. Every numbered citation in their
copy therefore points at a different work than the same number does in the
current build. The 40 is counted from `613f2a6:preprint_npj/paper.tex`, not read
off the dispatched PDF, which is gone with the hashes.

---

## 2026-09-05 — note to P.J., no artefacts attached

| | |
|---|---|
| Sent | 2026-09-05, 15:30 France time |
| Recipient | P.J. only |
| Content | a question on extent; **no files were attached** |
| Figures quoted | 43 → ~24 pages (paper), 52 → 56 (supplement) |
| Source commit | `06e0149` |
| Build the figures describe | paper 24 p. / supplement 56 p. / monograph 121 p. |

**This is not a dispatch.** No artefact left the machine; the note asks P.J.
whether 24 pages is acceptable before the version itself is sent. The hashes
below are recorded anyway, because the note quotes page counts that describe
specific files: if the build changes before he replies, the figures he was given
stop describing what would be sent.

**Provenance of the two figures quoted.** The `43` is not a measurement made in
this repository — it is Word's own count, stored in the `.docx` P.J. returned on
2026-08-27, and it is quoted as his number rather than ours. The `~24` is the
`pdfinfo` page count of `preprint_npj/build/paper.pdf`, measured here.

### Hashes, in two states

The artefacts were rebuilt after the send, at the author's request. Page counts
are unchanged — 24 / 56 / 121 before and after — because no source changed; only
the embedded creation timestamps differ, since the build does not set
`FORCE_SOURCE_DATE=1`. Both states are recorded so neither is mistaken for the
other.

**At the moment of the send** (build of 15:16–15:17, the bytes the quoted page
counts were read from):

| artefact | SHA-256 |
|---|---|
| `paper.pdf` | `74b1de8144ffa04f6a1f9566d3f501c14e872beb5dc6fe1334dc39b0d84f0357` |
| `supplement.pdf` | `778e1dcde47f833d73e5696f4bb4f580cb97c58d566c22e123498e7945c90c8f` |
| `manuscript.pdf` | `98cf53555ea4d9926d8aa296a85b5ad7b657ed35e13353d60ff6d3d7366f63b4` |

**After the post-send rebuild** (same commit, same content, superseded within
the hour by the repair below):

| artefact | SHA-256 |
|---|---|
| `paper.pdf` | `99c931a4ca93ea32d627befe6915567a6458c4498998de4fc4ff270c7c807bb4` |
| `supplement.pdf` | `c2f5d428ceedbe8d20762f69825130753aa2fb343b7465d38b3b6e504e55a821` |
| `manuscript.pdf` | `5ec6ae3435ba7921c43de655f38bd8c93a9d633131120d36bbd1e366544187d1` |

**After the cross-reference repair in `supplement.tex`**, the same afternoon:
`the table above` became `Table~\ref{tab:limits}`, because the table it named
renders on page 45 while the sentence renders on page 5 — forty pages forward,
not above. Content of the paper is unchanged; its hash moves only because the
rebuild restamps every PDF. Page counts are identical throughout: 24 / 56 / 121.

| artefact | SHA-256 |
|---|---|
| `paper.pdf` | `fce29dca8e8d9d05abfe50882e51721fdc71da007ae84616e97047b5ec361af9` |
| `supplement.pdf` | `81fa5a7a831107c0daf5eec6f9e07423ae48cbc38e1a5796713c405431662199` |
| `manuscript.pdf` | `5ec6ae3435ba7921c43de655f38bd8c93a9d633131120d36bbd1e366544187d1` |

Three hash states in one day is churn, and it is recorded rather than tidied:
only the first block describes the bytes the quoted page counts were read from,
and that is the one this entry exists to preserve.

**No block here claims to be current.** Later the same day, answering P.J.'s
reply asking for fluidity and the absence of repetition, three long sentences
were split and the Discussion's restatement of H1 removed, so the artefacts were
rebuilt again and every hash above moved once more. Page counts did not: 24 / 56
/ 121 throughout. Hashes for the version actually sent to the four supervisors
will be taken at that dispatch and recorded in its own entry, before the next
build runs.

**Written the same day, 15 minutes after the send** — the discipline the
2026-08-25 entry could not follow, and the reason its hashes are gone for good.

### Structural verification of the build, same day

`scripts/check_render.py` PASSED (2 accepted residues, 0 new).
`scripts/check_docx_structure.py` PASSED, self-calibrated: paper 10 of 10
`\includegraphics` present as media files, 9 captions with 0 missing;
supplement 5 of 5 images, 21 captions with 0 missing; both in source order.
Paper renders 5 figures and 4 tables in order, section order 1–4 intact, back
matter complete, and the reference list numbers 1–21 with no gap, matching the
21 distinct keys `paper.tex` cites.

**The `.docx` page counts cannot be read here.** `docProps/app.xml` reports
`<Pages>1</Pages>` and `<Words>83</Words>` identically for both files: a pandoc
placeholder, not a measurement. Word computes pagination when it opens the file,
which is why P.J.'s `43` exists at all and why no `.docx` page count is claimed
in this entry.

---

## 2026-09-05 — sent to the four supervisors (paper + supplement)

**Status: SENT.** 2026-09-05, 22:08 France time, four attachments. The entry was
written before the files left the machine and dated afterwards, which is the whole
point. The 2026-08-25 entry was
written nine days late, by which time `preprint_npj/build/` had been overwritten
and its hashes were unrecoverable. Here the hashes are taken first and the send
date is filled in when the author confirms it.

| | |
|---|---|
| Sent | 2026-09-05, 22:08 France time |
| Recipients | the four supervising co-authors (A.W., C.S., P.J., M.S.) |
| Source commit | `0f275e00493c65271799334a91c0bbb6854e9cf2` |
| Format | `.pdf` and `.docx` |
| Artefacts sent | paper and supplement only |
| Pages | 24 (paper) / 56 (supplement) |
| Not sent | the companion technical monograph, by author's decision of 2026-09-05 |

### Hashes, frozen before any further build

| artefact | SHA-256 | bytes |
|---|---|---|
| `preprint_npj/build/paper.pdf` | `af242625dccefbfeee5d59321dd97d78eddb1ccd7c09c6fc4bf61d6d66f2a5b5` | 608,570 |
| `preprint_npj/build/paper.docx` | `0d6eddcd403d6f0565ba59c7ce661f4279e460c8b45a29dcc90f172a6b0b8993` | 947,320 |
| `preprint_npj/build/supplement.pdf` | `ca2dfe3090749ad799fe35efe7ff1e628d58c62268e405ed7ae9d86a74886970` | 700,782 |
| `preprint_npj/build/supplement.docx` | `6988f99ea52543d7ef5c7464b36202b9810e58bce6f128fa41064dd8f7e257c6` | 735,540 |

The monograph was rebuilt at the same commit but **is not part of this
dispatch**. Its hashes are recorded below so that build stays identifiable if it
is sent later, and are kept out of the table above so that table lists only what
left the machine.

| built, not sent | SHA-256 | bytes |
|---|---|---|
| `preprint/build/manuscript.pdf` | `cb76f635013bb353d09d0c9704b27cefd2ceac8b14bd8d1903afe615758259c5` | 1,353,957 |
| `preprint/build/manuscript.docx` | `de64954f111ba1f32fedb89a0b81e12cd080cd3dfa5c50cb7227c10f6803b338` | 1,014,894 |

All six artefacts were rebuilt at the author's request immediately before this
hashing, so that the four that are sent carry the same clock as the send, and
every one of the six was then verified to postdate its source. **No build has run since these hashes
were taken, and none may run before the files leave.**

**One content change since**, made before the send and re-hashed with it: the
Discussion's credibility-framework sentence had lost its source in the
compression and stood as an attribution to the literature with none. The
citation is restored, so the paper cites 22 references rather than 21 and
`paper.pdf` grew by 383 bytes. `supplement.pdf` and `supplement.docx` came back
at identical sizes, their hashes moving on the timestamp alone; the monograph
was not rebuilt and its two hashes are unchanged. Pages did not move: 24 / 56.
The source was re-opened in session to check this rather than trusted from its
own note -- Europe PMC PMC7883933, HTTP 200 -- and each clause of the sentence
matched to text in it, including "there is no validation in the absence of
comparator data" and "Applicability refers to the range for the model input
parameters that characterize or bound the validation activities". The rebuild changed no
content: `paper.pdf`, `paper.docx`, `supplement.pdf` and `supplement.docx` came
back byte-for-byte the same SIZE as the previous build, only their embedded
timestamps differing, which is why every hash above moved while 24 / 56 / 121
pages did not.

### The accompanying message, as sent

Recorded verbatim, because a returning annotation is read against what its
reader was told:

> [Text of a private message removed from the public history; see HISTORY.md.]

**Two paragraphs of the drafted message were not sent**, by the author's choice,
and the omission is recorded because it changes what the recipients know:

1. **The citation-numbering warning.** The draft said the paper now cites 22
   references against 40 in their copy, and the supplement 32 against 24, so the
   same bracketed number no longer points at the same work, and asked them to
   annotate on the new files. Without it, an annotation of the form "reference
   [12] is wrong" may be reporting the numbering of the August copy rather than
   a defect in this one. Both counts were re-derived immediately before the send.
2. **The list of what is new**: the clinical cost of the -2 cmH2O trigger lock,
   the sentence on Pulse's teaching use, and the two claims that now carry a
   source (blood volume per kilogram, and the alveolar-gas-equation prediction).

Nothing in either omitted paragraph was inaccurate; they were dropped for
brevity. A one-line follow-up can restore the numbering warning if a returning
comment suggests it is needed.

### What changed since the version the four last received (`613f2a6`, 2026-08-25)

The paper went from 38 to 24 rendered pages, the supplement from 52 to 56, and
the monograph, which they received in August but which is not resent here, from
119 to 121. **Their copies are pinned to `613f2a6` and no
longer match**: the reference list is 21 entries against the 40 distinct keys
the dispatched source cited, so every citation number in their copy points at a
different work than the same number does here.

Substantively, since their copy: the September condensation pass and the audits
that followed it; five citations restored to claims that had outlived them and a
citation-manifest gate wired to stop that recurring; the cross-sex Spearman
result restored to Results after the compression left it declared in Methods and
reported nowhere; H3 and H4 regraded against the hypotheses as preregistered,
across the paper, the README and the monograph, which had carried three
different verdicts; and, answering P.J.'s reply of this afternoon, three of the
densest sentences split and the Discussion's restatement of H1 removed.

### Gate state at dispatch

Nine invocations green: `audit_claims.py` bare, `--check-paper-sync`,
`--check-monograph`, and both flags together (382 / 382 anchors on the authors'
full tree; 381 / 382 with 1 SKIPPED on a clean checkout, `T1.06u` reading
gitignored raw trajectories); `check_citations.py` (41 keys); `check_backrefs.py`
(12 back-references, 10 probed, 2 pointers); `check_stale_counts.py`;
`check_render.py` (2 accepted residues, 0 new); `check_docx_structure.py`
(self-calibrated: paper 10 of 10 images, supplement 5 of 5, all captions in
source order). Plus 80 pytest and `ruff`. CI green on this exact commit, `0f275e0`, run `33980343328`, with all seven
gate steps individually confirmed executed rather than inferred from a green job.

---

## 2026-09-19 — prepared for the four supervisors (paper + supplement)

**Status: PREPARED, NOT YET SENT.** The hashes below were frozen before the
files left the machine, which is the whole point of this entry existing at this
moment rather than afterwards. **The `Sent` row stays empty until the author
confirms the send**, and is filled in then. This is the discipline the
2026-08-25 entry failed: it was written nine days late, `preprint_npj/build/`
had been overwritten, and its hashes were unrecoverable.

| | |
|---|---|
| Sent | *(pending author confirmation)* |
| Recipients | the four supervising co-authors (A.W., C.S., P.J., M.S.) |
| Source commit | `a0fb250`, re-freeze 28 (see the freeze table below; this row had stayed at re-freeze 12's `ff09c92` through re-freezes 13 to 22) |
| Format | `.pdf` and `.docx` |
| Artefacts to send | paper and supplement only |
| Pages | 26 (paper; 25 until re-freeze 18) / 64 (supplement) |
| Not sent | the companion technical monograph (122 pages), by the author's decision of 2026-09-19, repeating the decision of 2026-09-05 |

### Hashes, frozen before any further build

| artefact | SHA-256 | bytes |
|---|---|---|
| `preprint_npj/build/paper.pdf` | `589c8fbf0d3c24285cfa71b37621ee72aebd51534bbd4d2ec663daab4c5d3e5f` | 633,077 |
| `preprint_npj/build/paper.docx` | `a9f6ad8662d778d18364a8565b384e530147a6fd95f1d9204fa863b34ce87830` | 975,278 |
| `preprint_npj/build/supplement.pdf` | `33bac37733c156812a6402e6da52b0bab4b0a87199896572ca4a5f26a764d213` | 726,017 |
| `preprint_npj/build/supplement.docx` | `690d7b1a3b78d1b72b9cac6041410be4bee4b8f882b5fe2599bb7c1f3cfb3719` | 747,762 |

The monograph **is not part of this dispatch**. It was rebuilt with
re-freeze 24, at `cabc29c`, which carries the one re-freeze 24 repair it
needed (the §4.3 use-case caveat); `27a012c` had aligned it on the
re-freeze 23 wording, as `78396c0` and `026df18` did for re-freezes 20 to 22.
Re-freezes 25 to 28 do not touch it. It was rebuilt again after re-freeze 28,
at `1cc0708`, which removes its two claims that the flag priority order was
preregistered: it now says the order was fixed after the sweep, as the paper
does since re-freeze 27. The npj artefacts are not affected. Its hashes are
recorded so that build stays identifiable:
`preprint/build/manuscript.pdf`
`bfb8cec519a94965c88fef6b5ab6d2e424757a7e21ce587469e98800f1c20391` (1,358,081
bytes) and `preprint/build/manuscript.docx`
`03a5f1e8fcbbf29937b2b2c26dd85e6a0d754673ed4853f55913767ded910b39` (1,016,694
bytes), still 122 pages.
Apart from that provenance, the wording of re-freezes 26 and 27 was **not**
carried to it: the monograph still has phrases they replaced (rows 26 and 27
below), deferred with it. The two sentences re-freeze 28 corrects do not
occur in it.

⚠️ **These hashes are valid for this build only.** Any further edit to
`paper.tex` or `supplement.tex` invalidates them, and they must be re-frozen
before the send. (The abstract decision recorded below is closed: kept as is.)

⚠️ **The supplement's two hashes changed at re-freeze 13, and again at 14, 15, 16, 17, 18 and 19, although
`supplement.tex` did not.** Verified: `git diff 3765872..a064d14^ --
preprint_npj/supplement.tex` is empty, the supplement still renders 64 pages,
and every structural check passes. **At re-freeze 20 they changed for a real
reason:** `a064d14` edits `supplement.tex` (11 edits on 10 lines; still 64
pages). At re-freeze 21 they moved again with `supplement.tex` unchanged
since `a064d14` (`git diff a064d14..a92496f --` on it is empty), and again
at re-freeze 22 (`supplement.tex` still unchanged since `a064d14`). **At
re-freeze 23 they changed for a real reason again:** `c4efe6c` edits
`supplement.tex` (still 64 pages), and so does `ada9659` at re-freeze 24 (one
cross-reference; still 64 pages). At re-freeze 25 they moved again with
`supplement.tex` unchanged since `ada9659` (`git diff ada9659..629d3a0 --`
on it is empty; byte counts identical, 725,801 and 747,729). **At
re-freeze 26 they changed for a real reason:** `cf3ef7c` edits
`supplement.tex` (9 lines edited; still 64 pages), **and so does
`3e925e6` at re-freeze 27** (one line; still 64 pages) **and `a0fb250` at
re-freeze 28** (two sentences; still 64 pages). At re-freeze 28 it is the
*paper's* two hashes that moved with the content unchanged: `paper.tex` is
untouched since `97b13e1` and both byte counts are identical (633,077 and
975,278), so the build timestamp alone moved them. For
re-freezes 13 to 19, 21, 22 and 25 the cause is the build, not the content:
pdfTeX stamps a wall-clock `CreationDate` into the PDF (`18:47:46` for the
re-freeze 22 supplement) and the pandoc DOCX moved by one byte, 747,727 to 747,726, so a rebuild
never reproduces the previous digest. `build/` is untracked, so the earlier
artefacts cannot be recovered for comparison. Read a changed supplement hash as
*rebuilt*, never as *edited*; `supplement.tex` in git is the authority on
whether the content moved. The monograph hashes above changed at re-freezes 16
and 17, again after 21, at 22, 23 and 24, and again after 28, for a real
reason, unlike the supplement's at 13 to 19, 21, 22 and 25: `manuscript.md`
was edited (`1d684c7`, then `f9e3bb7`, then `78396c0` and `026df18`, then
`27a012c`, then `cabc29c`, then `1cc0708`) and rebuilt
with `scripts/build_paper.ps1`. They did not change at re-freezes 25 to 28,
which leave `manuscript.md` untouched.
`build_npj.ps1` alone never rebuilds it.

**Re-frozen twenty-eight times.** The first three were one-token abstract edits
made before the files left the machine; re-freezes 4 to 19 and 21 to 28 leave
the abstract untouched, and re-freeze 20 rewords three of its phrases at an
unchanged count:

| | source commit | what changed | words |
|---|---|---|---:|
| first freeze | `3765872` | — | 150 / 147 |
| re-freeze 1 | `c562e4c` | comma after the introductory phrase: "At FiO$_2$ = 1.0, transient hyperoxia" | 150 / 147 |
| re-freeze 2 | `e8b4124` | "A four-flag classifier **reveals** failure modes" for "surfaces" | 150 / 147 |
| re-freeze 3 | `3a8b01c` | "**Runs** and flags are released openly" for "All runs and flags" | **149 / 146** |
| re-freeze 4 | `575c5bc` | the 87-word Webb sentence in the Introduction split in three (no claim touched, abstract untouched) | 149 / 146 |
| re-freeze 5 | `a3ee4c0` | "That **work**" for "That sweep" in that split: it had narrowed a conjunction's scope and moved a pronoun's antecedent | 149 / 146 |
| re-freeze 6 | `d0110e4` | the 2020-study sentence loses its em-dashes and its colon, aligning on the form the supplement already used | 149 / 146 |
| re-freeze 7 | `fe66bac` | the same sentence split in three: the punctuation fix had not made it readable, a missing "that" was the real cause | 149 / 146 |
| re-freeze 8 | `5cae746` | **a claim, not a wording**: the unsourced "a main use of Pulse's respiratory model" replaced by "Pulse models mechanical ventilation of an impaired lung", and guarded | 149 / 146 |
| re-freeze 9 | `08f3643` | Introduction: the three questions become three questions, "linear" glossed where used, and the advance echo of the same three axes removed — 936 → 928 words | 149 / 146 |
| re-freeze 10 | `3afea21` | Introduction: the four flags put in one grammatical shape — 928 → 926 words | 149 / 146 |
| re-freeze 11 | `d8d7b5b` | Table 1 caption: "pointers" for "section references", and Berlin's PEEP condition restored; the Introduction's first use of "distribution-neutral" glossed | 149 / 146 |
| re-freeze 12 | `ff09c92` | §2.1: the hypothesis paragraph split so the four verdicts are visible — 229 → 224 words | 149 / 146 |
| re-freeze 13 | `6205cd3` | §2.1: the instantiation paragraph reframed and "contract" glossed — 138 → 155 words | 149 / 146 |
| re-freeze 14 | `20e03fa` | §2.1: the flag-definitions table adopted — 0 references → 2, and the four flags named at first use | 149 / 146 |
| re-freeze 15 | `4fc3ee8` | §2.1: design total 10{,}240 added and guarded; the log-test claim aligned on the monograph | 149 / 146 |
| re-freeze 16 | `8f2adc2` | seven commits from `1d684c7`, all author decisions. Morris called "a global screening method that varies one input at a time"; the Berlin Definition cited in Table 1 (paper list 26 → 27); H1–H4 pointed to Methods §4.6; **one scope change**: the Berlin calibration bounded to the male reference body; "a linear, additive response"; §2.2's pair-count and screen sentences rewritten, with the cell labels defined in Table 1; Figure 1 redrawn in the order the code runs, with the Morris branch | 149 / 146 |
| re-freeze 17 | `c9fd377` | Methods §4.3: "The impairment fractions are therefore anchored…" for "An atlas cell is therefore anchored…", completing the male-body scoping. The monograph was aligned in `f9e3bb7` (6 loci; not dispatched) | 149 / 146 |
| re-freeze 18 | `34fcef2` | Figure 1 caption: "clean pairs" defined where the figure first uses them (124 → 144 words) | 149 / 146 |
| re-freeze 19 | `fa3e869` | eight terms made readable where figures and tables use them: σ defined; five screen names cut to two; "frozen at saturation", "blood volume" and VC-AC spelled out; Table 3 "Runs"; "tile" for a heatmap square (Figure 2b's false "48 cells" fixed); Figure 4b's "AGE" replaced. The paper reflows to **26 pages** | 149 / 146 |
| re-freeze 20 | `a064d14` | **claims, not wording**: seven narrowed to what their experiments show. One unsupported supplement inference removed (a divergence-only sweep cannot show Morris-rank robustness); dyssynchrony "consistent with"; "sex-stratified" for "sex-dependent"/"sex-specific"; blood-volume "dependence" for "mechanism", including the §2.5 and §S10 titles; rank 1 "more stable", not "resolved"; the ARDS labels stated as calibration bands; the monograph "gives further detail" rather than being "the source of truth". Paper and supplement both edited; still 26 / 64 pages | 149 / 146 |
| re-freeze 21 | `a92496f` | "preregistered" dropped from the three follow-up experiments (trigger lockout, 300-s hyperoxia rerun, blood volume): none is in `preregistration.md`, and protocol and results entered git in the same commit for each. Paper only; still 26 / 64 pages | 149 / 146 |
| re-freeze 22 | `4a9286c` | two residual sentences of the same two themes: §2.5 "Sex therefore moves where the solver fails…" becomes "Across the two reference bodies, where the solver fails therefore differs…", and the Discussion's "effort-dependent dyssynchrony Pulse models" becomes "effort-dependent variability". Paper only; still 26 / 64 pages. The monograph and README were aligned in the same round (`78396c0`, `026df18`, `3f5ad9e`; not dispatched) | 149 / 146 |
| re-freeze 23 | `c4efe6c` | **claims, not wording**: eighteen statements narrowed to what the documents' own figures, tables and data show. H2 no longer "settled by Table 3 alone"; "no measurable ventilator cross-talk" removed; FiO$_2$ in severe ARDS no longer "near-flat"; the FiO$_2$ = 1.0 of the divergent runs "requested", never applied; the blood-volume sentence bounded to Pulse's calculation; heart rate no longer "decouples" from its input; the Cornish ordinal paragraph deleted; the 120-s window verdict bounded to the two audited populations; runs "recorded for 120 s after a 120-s ventilator-settling phase"; the SHAP 17 / 18 unit and the Spearman rationale corrected; dyssynchrony no longer asserted ("instability" in the §2.3 title, "consistent with" at six supplement loci); Table 2's not_steady_state meaning, "five flags", preregistration scope, "fully balanced factorial", "causal-mechanistic" and two shunt statements narrowed; the green-tile guidance replaced by run-level screening in every cell. Paper and supplement both edited; still 26 / 64 pages. The monograph, README, cover letter and traffic-light JSON legend were aligned in the same round (`27a012c`, `e9ac421`; not dispatched) | 149 / 146 |
| re-freeze 24 | `ada9659` | three repairs to re-freeze 23's own wording, found on re-reading it before any push: the H2 verdict no longer rests on the log flag alone ("…the input-instantiation audit below provides the complementary check, and together they leave H2 not supported"); the traffic-light caveat moved to the end of its sentence ("every use remains subject to use-case-specific validation"); S5.5's "all 20 divergences occur during patient stabilisation" now points to §2.1, which states it, instead of S3, which states it for 13. Paper and supplement both edited; still 26 / 64 pages. The monograph's copy of the traffic-light caveat was repaired in the same round (`cabc29c`; not dispatched) | 149 / 146 |
| re-freeze 25 | `629d3a0` | five sentences said more plainly, on the author's decision after a read of the paper for density; no claim, number, figure or table changes. Introduction: "We provide a reusable run-level classifier and a per-cell map that sets review priority", both caveats kept (not a validation; the screened runs are not a representative subset). Discussion: "data-quality contract" becomes "can also be used to screen Pulse-generated synthetic patient cohorts…"; "Three traps … merit explicit attention" becomes "Three findings call for care when Pulse-generated data are reused"; "foundational infrastructure rather than a terminal deliverable" becomes "meant as a baseline for further work". Code availability: the reproduction host's model and OS and the $10^{-14}$ round-off detail left to Supplement S12, "x86\_64" kept. Paper only; still 26 / 64 pages. The cover letter was aligned in the same commit; the monograph was not (not dispatched) | 149 / 146 |
| re-freeze 26 | `cf3ef7c` | **claims, not wording**: phrases on 14 lines (5 paper, 9 supplement) narrowed to what the code, the data or a primary source show, after a read-through before dispatch; no number, figure, table or reference changes. The trigger lock no longer "decouples" breath delivery nor restores "metronomic" delivery: Pulse's pressure trigger still fires on strong efforts, and at least 11 of the 64 lock reruns deliver two or more breaths above the set rate; hence "lower-variability", "markedly stabilises", "largely removed", "strongly reduces". The calibration setting is no longer "based on the ARDSnet framework" (6 mL/kg of actual, not predicted, body weight). The last sentence reads "characterising a simulator's operational limits", its closed-loop trial citation kept. The hard bounds are a "screening standard" in S3.1 and S3.6, and the PaO$_2$ 20 mmHg "incompatible with a stable steady state" clause is removed (Grocott 2009: 19.1–29.5 mmHg in climbers at 8,400 m). S3.10's 32 runs "no longer exceed the widened bound" instead of becoming "physiologically clean"; S3.8 says "bootstrap seeds". Paper and supplement both edited; still 26 / 64 pages. Not carried to the monograph or to `src/detector.py` (not dispatched) | 149 / 146 |
| re-freeze 27 | `97b13e1` | wording made plainer on 7 lines (6 paper, 1 supplement), on the author's questions, with one provenance fact stated; no result, table value, figure or reference changes. Methods §4.4: the flag priority order is "fixed after the sweep" (it is not in `preregistration.md`; the sweep ended 2026-04-26 and the order was first written on 2026-04-27, `a8111fa`). §2.3: `InspirationPatientTriggerPressure` glossed as "the airway-pressure drop below PEEP at which a patient effort triggers a breath" (Pulse source, identical in 4.3.1 and 4.3.2). Table 3, Figure 2 and Figure 3 captions rewritten more plainly: Figure 2 names the six deviation-only red tiles (HR and PaO$_2$ in S3\_M, S3\_F and S4\_F) and says "lower PaO$_2$" for "ARDS hypoxemia"; Figure 3 defines μ\* as "the average absolute change in the panel's output per full-range move of that input" and says that each panel has its own colour scale. §2.4: "wider 700 mmHg upper bound" for "physiology-anchored 700 mmHg ceiling". S3.10: the runaway run's 679 mmHg is a "mean over the final 60 s", not a "steady-state mean". Still 26 / 64 pages. Not carried to the monograph (not dispatched), except the flag-order provenance, carried later by `1cc0708` | 149 / 146 |
| re-freeze 28 | `a0fb250` | **a claim, not a wording**: two supplement sentences said that heart rate rises with ARDS severity, which the data do not show (clean-run mean output HR 153–158 bpm in S3, 147–148 in S4) and which the supplement's own S15.2 contradicts ("output HR peaks at S3 … and eases at S4"). Figure S5(c) caption: "in every ARDS cell, HR sits above and PaO$_2$ below the healthy-male baseline". S15 opening: it now repeats §2.6's own wording, "in moderate and severe ARDS, a compensatory tachycardia lifts Pulse's mean output heart rate above the sampled input range". The back-reference manifest entry for that sentence was updated with it. Supplement only; still 26 / 64 pages. The paper was rebuilt but not edited | 149 / 146 |

Re-freezes 9 and 10 are the two that shortened a section rather than a
sentence: **the Introduction goes 936 → 926 words**, and the abstract is
untouched throughout. For the record, since it bears on what the four received:
the Introduction stood at 1,417 words in their August copy and 804 in the
September one, the difference being the deliberate synthetic-data framing added
on 2026-09-15 (`e34ec07`, four sentences and four citations). That framing was
**kept**, on the author's decision of 2026-09-21.

The third is the only one that moved the count: the abstract now holds one word
of margin under the npj cap, for the first time since the cap was reached. What
the dropped "All" carried — that the release is complete, failures included —
is recorded in that commit and survives in the body at L150.

**Across re-freezes 1 to 3 the supplement's two hashes never moved**, which
was not a detail but the check: it proved each of those rebuilds reached the
paper only (later re-freezes did move them; see the note above the table).
Page counts stayed at 25 and 64 through those three, and the abstract measured
150 words / 147 strict at re-freezes 1 and 2 — a comma attaches to the token
before it, and one verb replaces one verb.

⚠️ **Convention note, stated rather than hidden.** This file's header says
entries are "appended, never edited in place", and the practice for a build that
moved before dispatch has been to append a superseding entry — as the three
2026-08-18/19 entries do. This entry was instead **edited in place**: twice
when this note was written, and again at every re-freeze since. The
reason: it records nothing sent (`Sent` is empty), so there is no dispatch to
preserve, and three near-identical entries for a dispatch that has not happened
would bury the one that matters. The rule protects the record of what was *sent*;
that record is still untouched. **Once this entry's `Sent` row is filled, it is
frozen and any later build gets a new, superseding entry.**

### What changed since the version the four last received (`0f275e0`, 2026-09-05)

**92 commits** up to the preparation build (`3765872`), 156 up to re-freeze 22,
161 up to re-freeze 23, 167 up to re-freeze 24, 172 up to re-freeze 25,
175 up to re-freeze 26, 180 up to re-freeze 27, 183 up to re-freeze 28.
The paper goes from 24 to **26** rendered pages (25 until re-freeze 18), the
supplement from 56 to **64**. The monograph, which they did not receive in September
either, stands at 122.

By tag, the 92 split as 27 `[AUDIT]`, 10 `[MANUSCRIPT+GUARD]`, 10
`[MANUSCRIPT]`, 6 `[GUARD]`, 5 `[SCIENTIFIC]`, 4 `[MONOGRAPH]`, 4 `[LOG]` and
26 mixed. Substantively:

- **The exhaustive number audit was carried to its end.** Every numeric literal,
  every number written in words, every year-like and masked literal, and every
  `guard`/`ledger` occurrence across the three artefacts was read row by row and
  its findings resolved on the author's decisions (register
  `audit/number_inventory.md` §3–§9).
- **Then the population no instrument could see: prose that carries no number.**
  1,922 quantifier and absolute-claim occurrences enumerated and read (§12).
  Four claims were found stronger than their evidence and corrected on the
  author's decisions the same day, including two in surfaces a reader meets
  alone — the abstract and a figure legend.
- **Six `[SCIENTIFIC]` corrections**, each from data already recorded: the
  continuous-severity band re-binned on the severity Pulse actually ran
  (`[0.879, 0.946]`); the Morris rankings re-derived under a relaxed clean-pair
  screen (rank 1 holds, ranks 2–3 move); the Sobol cost model corrected; a
  merging-bias figure corrected; a denominator named; and one sentence deleted
  because the measurement refuted it.
- **The September condensation pass and its repairs**: four closing statements
  shortened and the AI-use disclosure split, with the detail moved to
  Supplement §S18; then two claims the compression had dropped restored, with a
  guard paired to each.

After those 92, re-freeze 20 (`a064d14`) narrows seven claims to what their
experiments show (row 20 of the table above). A reader of the September copy
will see it in the abstract and in two section titles: §2.5 now ends "and
blood-volume dependence", §S10 begins "Blood-volume dependence". Re-freeze 21
(`a92496f`) then stops calling three follow-up experiments "preregistered"
(§2.3, §2.4, §2.5), and re-freeze 22 (`4a9286c`) rewords one sentence each
in §2.5 and the Discussion. No number, figure or table moved.

Re-freeze 23 (`c4efe6c`) narrows eighteen further statements (row 23 above).
A reader of the September copy will see it in the paper's §2.1 (H2), §2.2,
§2.3 (its title and one sentence), §2.4, §2.5, §2.6, the Discussion and
Methods §4.3, in the
wording of Tables 1 and 2 and of Figure 1's caption, and in supplement S4,
S5, S7, S8, S10, S12, S13, S15, S16 and S17. No result changes and no figure
moves; S7 loses one paragraph, with the four Cornish bootstrap percentages it
compared against the atlas's red tiles. Re-freeze 24 (`ada9659`) repairs three
of those sentences (§2.1 H2, the Discussion's traffic-light caveat, one S5.5
cross-reference). Re-freeze 25 (`629d3a0`) rewords five paper sentences (one
in the Introduction, three in the Discussion, one in Code availability)
without changing a claim. Re-freeze 26 (`cf3ef7c`) narrows phrases on 14
lines (row 26 above): a reader of the September copy will see it in §2.3,
Figure 4's caption, the Discussion (two sentences, including the last) and
Methods §4.3, and in supplement S3.1 (with its bound table), S3.6, S3.8,
S3.10, S5.4, S8 and S8.4 (with its figure caption). No result changes and no
figure moves. Re-freeze 27 (`97b13e1`) makes wording plainer on 7 lines (row
27 above): a reader of the September copy will see it in the captions of
Table 3 and Figures 2 and 3, in §2.3 (one parenthesis), §2.4 (one phrase) and
Methods §4.4, and in supplement S3.10. No result changes and no figure moves.
Re-freeze 28 (`a0fb250`) corrects two supplement sentences (row 28 above): a
reader of the September copy will see it in the Figure S5 caption, panel (c),
and in the opening of S15. No result changes and no figure moves.

### What the covering message must say

1. **The reference numbering has moved.** The citation gate records **46 cited
   keys** on this build against **41** at their dispatch, so the same bracketed
   number no longer points at the same work. Annotations of the form
   "reference [12] is wrong" must be made **on the new files**, not on the
   September copy. ⚠️ This warning was drafted for the 2026-09-05 send and
   **dropped for brevity**; dropping it again would be the second time.
   Re-freeze 16 adds one more shift inside the paper: the Berlin Definition
   now enters its list at [15] (26 → 27 entries), moving the former 15–26 up
   by one. The 46 does not move, because the gate counts the paper and
   supplement together and the supplement already cited it.
2. **Page and line references have moved** (24 → 26 and 56 → 64 pages).
3. **The repository is still private, deliberately.** The author's plan of
   2026-09-19: it goes public with the arXiv deposit, *after* this review round
   and the corrections it produces. Until then the availability sentences in
   both documents read in the present tense and their links do not resolve —
   `scripts/check_publication_gate.py` holds all 10 such anchors, and
   `--verify-public` is the pre-submission step that will check the visibility
   itself.

### Gate state at preparation

All nine invocations green, measured on this commit rather than carried over
from the previous entry: `audit_claims.py` bare, `--check-paper-sync`,
`--check-monograph` (**394 / 394 anchors**, 0 WARN, 0 FAIL, 0 SKIPPED on the
authors' full tree; **26** monograph anchors; **94** crosswalk; **25** head-line
counters; **17** README science anchors); `check_citations.py` (**46** cited
keys, all resolved and recorded); `check_backrefs.py` (**13** back-references,
11 probed against `paper.tex`, 2 registered as pointers);
`check_stale_counts.py`; `check_render.py` (**1 accepted residue, 0 new**);
`check_docx_structure.py` (self-calibrated); `check_publication_gate.py`
(**10 / 10** anchors). Plus 80 pytest and `ruff` clean on the CI scope. CI green
on this exact commit, `3765872`, run `35460101524`, three jobs — and that run
executed the new prose-audit guard on a fresh Linux clone, not only locally.

### Open decision carried into this dispatch

**The abstract's hyperoxia sentence.** "300-second healthy-lung reruns give a
median 643 mmHg" does not name the population the median is taken over. The
repository's own guard partitions the 44 S1 reruns as 37 + 3 + 3 + 1, and the
published 643 (642.8704) is the median over the **40 drift-converged** runs,
i.e. 37 physiologically converged plus 3 runaway-but-converged. Two consequences
were put to the author on 2026-09-19:

- Naming "the six runaways" in the abstract would **misdescribe the exclusion**:
  three of the six are inside the median. The screen is convergence, not
  runaway status.
- Naming the denominator instead was measured and does not fit: "a converged
  median 643 mmHg" gives 151 words and "a drift-converged median of 643 mmHg"
  gives 152, against a cap of 150 that the abstract already sits at exactly.

Not decided on 2026-09-19. The median over all 44 reruns has **not** been re-measured in that
session; an August note recorded it as 643.3063, but the same note gave
"642.8716 on 41" where the guard measures 642.8704 on **40**, so that note is
not relied on here.

**Decided 2026-09-24 by the author: the sentence is kept as is.** Measured the
same day from the tracked `data/runs/s021_hyperoxia_convergence/summary.json`:
`S1_plateau_median_mmHg` = 643.2458 over the 44 reruns (its `n` = 44) and
`S1_converged_plateau_median_mmHg` = 642.8704 over the 40 drift-converged.
Both round to the published 643, so the sentence is true under either
population; the August 643.3063 is not what the file holds. For the record,
the 151 / 152 word counts above were taken while the abstract stood at 150
words, before re-freeze 3; on the current 149-word abstract (portal text from
`sync_submission_metadata.py --print`, split on whitespace as the script
does), "a converged median 643 mmHg" gives 150, at the cap, and "a
drift-converged median of 643 mmHg" gives 151. The decision does not depend
on it.
