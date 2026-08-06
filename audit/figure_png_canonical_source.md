# Which producer owns `fig01_traffic_light.png`?

**Opened 2026-08-06**, out of the S021 clock reframing, where a routine
`build_npj.ps1` run left the working tree dirty without a single source edit.
**Deliberately not decided here** — this register states the facts and the
options; the choice is the maintainer's.

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
