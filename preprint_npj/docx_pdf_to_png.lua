-- Pandoc Lua filter: rewrite figure image sources from .pdf to .png.
--
-- Why: Word/.docx cannot embed PDF figures, so the LaTeX -> .docx route
-- (paper.tex / supplement.tex) must point at the PNG twins that ship in
-- preprint_npj/figures/. The PDFs referenced by \includegraphics remain the
-- canonical figures for the PDF build; this rewrite affects the .docx only.
--
-- Every figure has a PNG twin in preprint_npj/figures/ (fig01_traffic_light
-- and fig_s2_spearman are rasterised from their PDFs by build_npj.ps1 before
-- this filter runs; the rest are emitted as PNG by scripts/make_*.py).
function Image(el)
  el.src = string.gsub(el.src, "%.pdf$", ".png")
  return el
end
