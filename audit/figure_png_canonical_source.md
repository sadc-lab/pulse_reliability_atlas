# Which producer owns `fig01_traffic_light.png`?

**Opened 2026-08-06. RESOLVED 2026-08-14: the PDF is canonical.** The body below
is the investigation as written on 2026-08-06 and is **superseded in its
premise** — see the dated block immediately following.

---

## ▶ Resolution, 2026-08-14 — and the 2026-08-06 premise was already false

**What the body below says is no longer what the repository contains.** Measured
before deciding anything:

- the committed `fig01_traffic_light.png` was **2135 × 1236, colour type 0x02
  (RGB)** — the pdftoppm signature, not the matplotlib one this register
  describes. `pdftoppm -png -r 300 -singlefile` on the committed PDF reproduced
  it **byte for byte** (MD5 `ed9c2a06…`, 105,881 bytes), which is why recent
  builds left the tree clean rather than dirty.
- the file had **alternated between the two producers four times in eight
  days**: matplotlib at `41e8c52`, `ed5259f`, `211daa8`, pdftoppm at `bca0e89`,
  matplotlib again at `63b99da` (a deliberate decision), pdftoppm again at
  `4e6c0b0` — which silently undid `63b99da`.

### The structural cause: two gates that cannot both be satisfied

`scripts/verify.py` regenerates the figure through `make_paper_fig01.py` under a
pinned `SOURCE_DATE_EPOCH` and requires a clean tree. `build_npj.ps1`
(`Build-Docx`) rasterises the same PNG from the PDF whenever poppler is on
`PATH`. Whichever ran last won. Meanwhile `scripts/tex_to_docx.py:22` already
documented the intended design: fig01 *"ships only as PDF"* and its PNG is
produced by the build, because Word cannot embed PDF figures.

### Two further defects found while measuring

- **`fig01_traffic_light.pdf` was not reproducible either.** Its
  `/CreationDate` was `D:20260812095309+02'00'` — a wall-clock stamp from a
  manual run at `4e6c0b0` — where the pinned path writes `D:20260422220508Z`.
  That is exactly the defect `63b99da` diagnosed and fixed on 2026-08-06,
  **recurred six days later**, because nothing checked it.
- **`fig_s3_hyperoxia_convergence.pdf`** carried the same defect from
  2026-08-06, and its generator *is* in the gate.
- **`fig00_study_design.pdf`** — the paper's Figure 1 — carries a wall-clock
  stamp *and* its generator `scripts/make_fig00_study_design.py` is absent from
  `verify.py::FIGURE_SCRIPTS`, so the gate never regenerates it. **Handled
  separately**; it is a coverage question, not a byte-drift one.
  → **Closed 2026-08-14, second commit. See the addendum at the end.**

### What was applied

1. **Option 2 adopted: the PDF is canonical.** `make_paper_fig01.py` no longer
   writes the `.png`; the build's `pdftoppm` derivative is the only producer.
2. Both defective PDFs regenerated through the pinned path.
3. **New guard** `check_figure_timestamps()` in `scripts/audit_claims.py`: every
   tracked figure PDF must carry the pinned `/CreationDate`, which is *derived*
   from `verify.py`'s own `REPRODUCIBLE_EPOCH` rather than duplicated. 26 PDFs
   examined, 24 pinned, 2 documented exceptions — and a **stale** exception is
   itself a FAIL, so the list cannot rot.

### Nothing scientific changed, and that was measured, not assumed

Both regenerated PDFs were rasterised at 300 dpi and compared against the
committed versions: **identical MD5** in both cases (`ed9c2a06…` for fig01,
`aca259a8…` for fig_s3). The only difference in either file is the embedded
timestamp — a 6-byte size change. The committed `fig01_traffic_light.png` did
not change at all: `pdftoppm` on the newly pinned PDF reproduces it exactly.

### The invariant now holds, verified in both directions

`uv run python scripts/verify.py` → figures OK, pdfs OK, audits OK, and the tree
carries only the intended edits. Then `build_npj.ps1` with poppler present →
the tree is unchanged. Neither gate dirties a file the other owns.

Guard calibrated negatively three ways, each injection verified before its
result was believed and each restoration checked by MD5: a timestamp drifted by
one digit → FAIL; a pinned file listed as an exception → FAIL, "exception is
obsolete"; a documented exception removed from disk → FAIL.

---

**Original 2026-08-06 investigation follows, unedited.** It was opened out of
the S021 clock reframing, where a routine `build_npj.ps1` run left the working
tree dirty without a single source edit, and it deliberately stated facts and
options without choosing.

## What happened

After a clean commit, running `preprint_npj/build_npj.ps1` modified a
version-controlled artefact:

```
 M preprint_npj/figures/fig01_traffic_light.png     102,570 -> 101,485 bytes
```

Restored from `HEAD`, because it is outside the S021 scope.

## Two producers write the same tracked file

| Producer | Locus | Output |
|---|---|---|
| matplotlib | `scripts/make_paper_fig01.py:176` | `savefig(..., dpi=200, bbox_inches="tight")` |
| poppler | `preprint_npj/build_npj.ps1:127` | `pdftoppm -png -r 300 -singlefile` from the committed PDF |

They disagree on **both** resolution and colour model, so the file's content
depends on which producer ran last. Measured signatures:

| File | Dimensions | Colour | Producer it came from |
|---|---|---|---|
| `fig01_traffic_light.png` (committed) | 1421 × 822 | **RGBA** | matplotlib, 200 dpi |
| `fig_s2_spearman.png` (committed) | 1821 × 1169 | **RGB** | pdftoppm |

`pdftoppm` emits RGB (no alpha); matplotlib's `savefig` here emits RGBA. The
committed `fig01` PNG therefore comes from the Python script, and every build
that finds poppler on `PATH` overwrites it with a 300 dpi RGB rasterisation.

## Why it surfaced only now

`build_npj.ps1:122` is conditional: it rasterises **only when `pdftoppm` is on
`PATH`**, and otherwise prints "using committed PNG figure twins". Repository
notes recorded poppler as *not installed* on this machine — that is no longer
true (TeX Live 2026). The conditional silently changed sides, which is why a
build that used to be inert on figures now rewrites two of them.

## Scope: one file, not two

`fig_s2_spearman.png` has **no** Python generator (`grep` finds it only in
`build_npj.ps1`, `tex_to_docx.py` and `verify.py`, none of which draw it). For
that figure the PDF is already the single source and the PNG is a derivative —
consistent, no conflict. **Only `fig01_traffic_light` has two producers.**

## The two coherent options

1. **Python is canonical.** `make_paper_fig01.py` writes both `.pdf` and
   `.png`; the build's rasteriser excludes `fig01_traffic_light` and keeps
   handling only figures with no generator. Keeps 200 dpi RGBA. Cheapest, and
   matches `63b99da`, which deliberately replaced this PNG with the
   reproducible build output after `bca0e89` had committed one from a manual run.
2. **PDF is canonical.** `make_paper_fig01.py` stops writing the `.png`, and
   the build's `pdftoppm` derivative becomes the committed twin at 300 dpi RGB.
   One rasteriser for every figure, but the PNG then only exists after a build
   on a machine with poppler, and its bytes depend on the poppler version.

Whichever is chosen, the invariant to enforce is the same: **exactly one
producer per tracked artefact**, and a build must not modify a version-controlled
file as a side effect.

## Not investigated

Whether `pdftoppm` output is byte-reproducible across poppler versions, and
whether the DOCX twins visibly differ at 200 vs 300 dpi. Neither is needed to
choose; both would matter if option 2 is taken.

---

## ▶ Addendum, 2026-08-14 — Figure 1 enters the reproducibility gate

The third defect above is closed. It needed two things settled first, both
measured rather than assumed.

**1. pdfTeX ignores `SOURCE_DATE_EPOCH`.** Unlike matplotlib, it stamps a
wall-clock `/CreationDate` unless **`FORCE_SOURCE_DATE=1`** is also set. That is
why this figure — a `pdflatex` generator, not a matplotlib one — could not have
been added to the gate as it stood: `verify.py` would have been permanently
dirty on it. With both variables set, two successive runs produce **byte-
identical** PDFs (`db11072e…`), verified before anything was changed.

**2. `pymupdf` was required but undeclared.** The generator rasterises its PNG
twin with pymupdf and exits if it is missing, and `verify.py` runs generators
with `sys.executable`, i.e. the declared project environment. Measured:
`pymupdf 1.28.0` was installed in the local `.venv` while **absent from both
`pyproject.toml` and `uv.lock` (0 occurrences)**. So the local environment had
silently diverged from the declared one, and on a clean clone `pdf_probe.py`,
`check_render.py` (pre-commit hook) and this generator would all have failed.
Declaring it fixes a pre-existing defect, not just this figure's.

**Applied:** `pymupdf>=1.24.0` declared and locked (the lock gained **20 lines,
0 deletions — no other pin moved**); `FORCE_SOURCE_DATE=1` added to
`REPRODUCIBLE_ENV`; `scripts/make_fig00_study_design.py` added to
`FIGURE_SCRIPTS`; `fig00_study_design.pdf` replaced by its pinned build; its
entry removed from the timestamp guard's exception list.

**Nothing scientific changed, measured:** the committed and pinned PDFs
rasterise at 300 dpi to the **same MD5** (`ce95970e…`); the only differences are
the timestamp and the `/ID` pdfTeX derives from it, 11 bytes. The PNG twin and
the `.tex` twin did not change at all — including across the pymupdf upgrade the
lock brought (1.28.0 → 1.28.2), which was checked because a rasteriser version
bump could have moved those bytes: it did not (108,325 bytes either way).

**Invariants re-verified after the change:** `verify.py` run twice → byte-
identical figure outputs and a tree carrying only the intended edits; then
`build_npj.ps1` → tree unchanged; Figure 1 renders in `paper.pdf` p.7 with its
caption.

**One maintenance item noted, not acted on:** `make_fig00_study_design.py`,
`pdf_probe.py` and `check_render.py` all `import fitz`, and pymupdf 1.28 warns
that this alias will be removed. Three one-line changes, whenever convenient.
