# Build the Pulse Reliability Atlas npj Digital Medicine submission package.
#
# Outputs:
#   preprint_npj/build/paper.pdf        -- main manuscript
#   preprint_npj/build/paper.docx       -- Word twin of the main manuscript
#   preprint_npj/build/supplement.pdf   -- supplementary information (when supplement.tex exists)
#   preprint_npj/build/supplement.docx  -- Word twin of the supplement
#
# Usage:
#   .\preprint_npj\build_npj.ps1                  # build main + supplement (if present)
#   .\preprint_npj\build_npj.ps1 -MainOnly        # main paper only
#   .\preprint_npj\build_npj.ps1 -SupplementOnly  # supplement only
#
# Requires:
#   - TeX Live or MiKTeX with pdflatex + bibtex on PATH (verified TeX Live 2026
#     at C:\texlive\2026\bin\windows\pdflatex.exe during Step 1 of S028).
#   - For the .docx twins: pandoc on PATH + uv/python (the converter is
#     scripts/tex_to_docx.py, pure-stdlib). Optional: poppler's pdftoppm to
#     refresh the two PNG-only figures from their PDFs. The .docx step is
#     best-effort -- it warns but never fails the PDF build.
#
# Class + bibliography:
#   - sn-jnl.cls   (Springer Nature template, ships in preprint_npj/ alongside paper.tex)
#   - sn-nature.bst (Nature numbered reference style, ships in preprint_npj/)
#   Both files are copied from preprint_npj/template/sn-article-template/ at
#   Step 1 of S028 and committed to the repository. Authoritative upstream
#   archive at preprint_npj/template/ for traceability.
#
# Sync discipline:
#   - This wrapper rebuilds the paper deterministically; it does NOT enforce
#     the paper-monograph claim crosswalk. Run the audit separately:
#       uv run python scripts/audit_claims.py --check-paper-sync
#     (See preprint_npj/README.md, "Keeping the article and the monograph in step".)

[CmdletBinding()]
param(
    [switch]$MainOnly,
    [switch]$SupplementOnly
)

$ErrorActionPreference = 'Stop'

# --- Paths (resolved relative to the script itself, so it works from any CWD).
$NpjDir   = $PSScriptRoot
$RepoRoot = (Resolve-Path (Join-Path $NpjDir '..')).Path
$BuildDir = Join-Path $NpjDir 'build'
$PaperTex = Join-Path $NpjDir 'paper.tex'
$SuppTex  = Join-Path $NpjDir 'supplement.tex'

if (-not (Test-Path $BuildDir)) { New-Item -ItemType Directory -Path $BuildDir | Out-Null }

# --- Resolve pdflatex + bibtex (PATH first).
$PdflatexCmd = Get-Command pdflatex.exe -ErrorAction SilentlyContinue
if (-not $PdflatexCmd) {
    throw "pdflatex not found on PATH. Install TeX Live or MiKTeX."
}
$BibtexCmd = Get-Command bibtex.exe -ErrorAction SilentlyContinue
if (-not $BibtexCmd) {
    throw "bibtex not found on PATH. Install TeX Live or MiKTeX."
}
Write-Host "Using pdflatex: $($PdflatexCmd.Source)" -ForegroundColor DarkGray
Write-Host "Using bibtex:   $($BibtexCmd.Source)"   -ForegroundColor DarkGray

# --- Build helper. Runs pdflatex -> bibtex -> pdflatex -> pdflatex
#     (standard 3-pass build for cross-refs + bibliography).
function Build-LatexDocument {
    param([string]$TexFile)

    $stem = [System.IO.Path]::GetFileNameWithoutExtension($TexFile)
    Write-Host "Building $stem.pdf ..." -ForegroundColor Cyan

    Push-Location $NpjDir
    try {
        # Pass 1: collect aux + cite keys.
        & pdflatex -interaction=nonstopmode -output-directory=build "$stem.tex" | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  pdflatex pass 1 reported errors; check build/$stem.log" -ForegroundColor Yellow
        }
        # bibtex on the aux file.
        & bibtex "build/$stem" | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  bibtex reported issues; check build/$stem.blg" -ForegroundColor Yellow
        }
        # Pass 2: resolve cite refs.
        & pdflatex -interaction=nonstopmode -output-directory=build "$stem.tex" | Out-Null
        # Pass 3: final layout pass.
        & pdflatex -interaction=nonstopmode -output-directory=build "$stem.tex" | Out-Null

        $pdfOut = Join-Path $BuildDir "$stem.pdf"
        if (Test-Path $pdfOut) {
            $size = (Get-Item $pdfOut).Length
            Write-Host "OK -> $pdfOut  ($size bytes)" -ForegroundColor Green
        } else {
            Write-Host "FAIL: $stem.pdf not produced. See build/$stem.log" -ForegroundColor Red
            exit 1
        }
    } finally {
        Pop-Location
    }
}

# --- .docx companion build (Word twin of each PDF).
#
# Word cannot embed PDF figures, so this:
#   1. rasterises the two PNG-only figures (fig01_traffic_light,
#      fig_s2_spearman) from their PDFs when poppler's pdftoppm is on PATH
#      (otherwise the committed PNG twins in figures/ are used as-is); and
#   2. hands the .tex to scripts/tex_to_docx.py, which rewrites the sn-jnl
#      front matter (\author*{\fnm..\sur..}, \affil, \abstract, \keywords)
#      into pandoc-friendly LaTeX -- pandoc would otherwise silently drop the
#      author list and abstract -- then runs pandoc with --citeproc (numbered
#      nature.csl) and the docx_pdf_to_png.lua image-swap filter.
#
# Best-effort: a failure here warns but does NOT fail the build, since the PDF
# is the primary submission artefact.
function Build-Docx {
    param([string]$TexFile)

    $stem = [System.IO.Path]::GetFileNameWithoutExtension($TexFile)
    Write-Host "Building $stem.docx ..." -ForegroundColor Cyan

    $pdftoppm = Get-Command pdftoppm.exe -ErrorAction SilentlyContinue
    if ($pdftoppm) {
        foreach ($fig in @('fig01_traffic_light', 'fig_s2_spearman')) {
            $figPdf = Join-Path $NpjDir "figures\$fig.pdf"
            if (Test-Path $figPdf) {
                & pdftoppm -png -r 300 -singlefile $figPdf (Join-Path $NpjDir "figures\$fig") | Out-Null
            }
        }
    } else {
        Write-Host "  pdftoppm not on PATH; using committed PNG figure twins." -ForegroundColor DarkGray
    }

    $docxOut = Join-Path $BuildDir "$stem.docx"
    & uv run --project $RepoRoot python (Join-Path $RepoRoot 'scripts\tex_to_docx.py') `
        --tex $TexFile `
        --bib (Join-Path $NpjDir 'paper.bib') `
        --csl (Join-Path $NpjDir 'nature.csl') `
        --lua (Join-Path $NpjDir 'docx_pdf_to_png.lua') `
        --out $docxOut
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $docxOut)) {
        Write-Host "  WARNING: $stem.docx not produced (pandoc/uv/python issue) -- PDF is unaffected." -ForegroundColor Yellow
    } else {
        $size = (Get-Item $docxOut).Length
        Write-Host "OK -> $docxOut  ($size bytes)" -ForegroundColor Green
    }
}

# --- Drive build of the requested targets.
#
# Build order: SUPPLEMENT FIRST, then paper. This is mandatory for the
# xr-hyper cross-document references (Step 10 of S028) so that paper.tex
# can read supplement.aux to resolve dynamic supplement section / figure
# / table numbers. If supplement.tex is absent, the paper still builds
# (xr-hyper warns but does not fail).
if (-not $MainOnly) {
    if (Test-Path $SuppTex) {
        Build-LatexDocument $SuppTex
        Build-Docx $SuppTex
    } else {
        Write-Host "supplement.tex not present yet -- skipping (build paper-only)." -ForegroundColor DarkGray
    }
}

if (-not $SupplementOnly) {
    if (-not (Test-Path $PaperTex)) { throw "Main manuscript not found: $PaperTex" }
    Build-LatexDocument $PaperTex
    Build-Docx $PaperTex
}

Write-Host ""
Write-Host "Build complete." -ForegroundColor Green
