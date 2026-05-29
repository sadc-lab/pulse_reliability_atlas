# README — npj Paper Figures: Provenance and Regeneration

## Status

Three figures shipped in `preprint_npj/figures/` have **no generator script
anywhere in this repository**. They were produced ad hoc during S028 npj
typesetting and committed as PDFs only. This file documents (a) the canonical
data each derives from, (b) the closest in-repo generator (which produces
equivalent content but in monograph styling), and (c) the manual recipe for
recreating or restyling them when the underlying data changes.

`scripts/verify.py` lists these three in its `MISSING_GENERATORS` block, so
the reproducibility gap is visible at every `verify` run rather than silent.
This README is the canonical reference for what to do about it.

## The three orphan figures

| npj PDF | Used in | Data source (tracked, audited) | Closest in-repo generator |
|---|---|---|---|
| `fig01_traffic_light.pdf` | `paper.tex` Figure 1 | `results/reliability_classification.csv` (48 rows; `light` column = green/yellow/red) | `scripts/make_figures.py` → `fig_reliability_traffic_light()` (writes `figures/fig06_reliability_traffic_light.{pdf,png}`) |
| `fig02_morris_{HR,MAP,Vt,SpO2,PaO2,PaCO2}.pdf` (six panels) | `paper.tex` Figure 2 (six `subfigure`s) | `results/morris_indices.parquet` (μ* per scenario × sex × input × output) | `scripts/make_figures.py` → `fig_morris_mu_star()` (writes per-channel `figures/fig02_morris_mu_star_{ch}.{pdf,png}`) |
| `fig_s2_spearman.pdf` | `supplement.tex` Figure S2 | `results/spearman_mu_star.csv` (ρ per scenario × output, M-vs-F μ* vectors) | `scripts/make_figures.py` → `fig_h4_spearman()` (writes `figures/fig05_h4_spearman_mu_star.{pdf,png}`) |

Every data source is git-tracked and `scripts/audit_claims.py` already
audits the numerical content (`T1.25/26/27` for the traffic-light tallies;
`T1.07/T1.08/T1.09/T2.h1.*` for Morris top-3; `T1.19/T1.20/T2.sp.*` for
Spearman ρ). The **data** behind each figure is therefore fully guarded;
only the **rendering** is currently unscripted into `preprint_npj/figures/`.

## How each one differs from its in-repo equivalent

### `fig01_traffic_light` vs `fig_reliability_traffic_light()`

* Same data, same per-cell × per-output heatmap of green/yellow/red.
* npj version differs in title, axis labels, font sizes, and typography to
  match the rest of the npj figure set. The frozen PDF in
  `preprint_npj/figures/` is the visual reference.

### `fig02_morris_*` vs `fig_morris_mu_star()`

* **Critical structural difference: the orientation is transposed.** The
  in-repo function pivots with `index="cell", columns="input"` (rows = the
  8 cells, columns = the 7 inputs). The npj caption (`paper.tex` L186)
  explicitly states *"Rows of each panel are the seven swept inputs … ;
  columns are the eight (scenario × sex) cells"* — the inverse layout.
* Both produce six per-channel files (one per output), but the in-repo
  filename is `fig02_morris_mu_star_{ch}` and the npj filename is
  `fig02_morris_{ch}`.
* In-repo uses the `viridis` colormap and matplotlib defaults; the npj
  version's exact styling (colormap, fonts, annotation format) is preserved
  in the frozen PDFs and must be matched by visual inspection when restyling.

### `fig_s2_spearman` vs `fig_h4_spearman()`

* Same heatmap content (rows = scenario, columns = output, value = Spearman ρ
  between male and female μ* vectors).
* npj version differs in title, axis labels, font sizes, and typography. The
  frozen PDF is the visual reference.

## Manual regeneration recipe

When the underlying data changes and a figure needs to be regenerated, the
recipe is:

1. **Start from the in-repo function.** Copy `fig_reliability_traffic_light`,
   `fig_morris_mu_star`, or `fig_h4_spearman` from `scripts/make_figures.py`
   into a new dedicated script under `scripts/` (suggested names:
   `scripts/make_paper_fig01.py`, `scripts/make_paper_fig02.py`,
   `scripts/make_paper_figs2.py`).

2. **Re-target the output path** to
   `preprint_npj/figures/<npj-name>.{pdf,png}`. The dedicated script should
   read the same canonical CSV/parquet listed in the table above — no new
   data sources, no recomputation from raw runs.

3. **Apply the npj-specific styling.**
   * **`fig02_*` only**: transpose the pivot so rows = inputs, columns =
     cells (swap `index=` and `columns=` in the `pivot(...)` call).
   * For all three: render once, open the new PDF next to the frozen
     `preprint_npj/figures/<npj-name>.pdf`, and iterate on colormap, font
     sizes, title, axis labels, and figure dimensions until they match.
     The frozen PDF is the typographic reference; do not invent a new look.

4. **Visual-approval gate.** Before overwriting the frozen PDF, confirm with
   the maintainer that the regenerated version is acceptable. Silently
   swapping a restyled figure into a typeset paper is exactly the kind of
   subtle change that erodes reviewer trust.

5. **Register the new generator in `scripts/verify.py`.** Add the new script
   path to `FIGURE_SCRIPTS` and remove the corresponding entry from
   `MISSING_GENERATORS`. The end-to-end `verify` pipeline will then cover
   the figure automatically on every run.

6. **Re-run `uv run python scripts/verify.py`** and confirm green: figures
   regenerate, PDFs rebuild, 247-anchor monograph audit + 85-row crosswalk
   sync remain PASS.

## Why this is a README, not three generator scripts

Per the maintainer's *"no over-engineering"* constraint
(2026-05-29 robustness round): writing generators today would risk silently
changing a paper that is essentially frozen, because the in-repo equivalents
produce content-identical but visually-different figures. Documenting the
exact recipe and keeping the gap explicit in `verify.py`'s output is the
minimum responsible action: methodology preserved, frozen artefacts
unchanged, recovery path crisp for the moment the underlying data does
change.
