# Build the Pulse Reliability Atlas preprint from preprint/manuscript.md.
#
# Outputs:
#   preprint/build/manuscript.tex
#   preprint/build/manuscript.pdf
#
# Usage:
#   .\scripts\build_paper.ps1            # build both .tex and .pdf
#   .\scripts\build_paper.ps1 -TexOnly   # skip PDF compilation
#
# Requires:
#   - pandoc 3.x  (winget install --id JohnMacFarlane.Pandoc)
#   - xelatex via TeX Live or MiKTeX (Unicode-safe; the manuscript uses
#     mu, sigma, rho, nu, pi, le, ge, Rightarrow, ...)
#
# Bibliography handling:
#   - preprint/references.bib holds the BibTeX entries (citekeys match
#     [@key] form used in manuscript.md, e.g., @morris1991, @webb2023).
#   - pandoc --citeproc resolves inline citations to "(Author Year)" form.
#   - suppress-bibliography=true tells citeproc NOT to auto-append a
#     reference section -- the manuscript's section 6.7 "Verified primary
#     references" already serves that role in human-readable form.

[CmdletBinding()]
param(
    [switch]$TexOnly
)

$ErrorActionPreference = 'Stop'

# --- Paths (resolved relative to the script itself, so it works from any CWD).
$RepoRoot   = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Manuscript = Join-Path $RepoRoot 'preprint\manuscript.md'
$BibFile    = Join-Path $RepoRoot 'preprint\references.bib'
$BuildDir   = Join-Path $RepoRoot 'preprint\build'
$TexOut     = Join-Path $BuildDir 'manuscript.tex'
$PdfOut     = Join-Path $BuildDir 'manuscript.pdf'

if (-not (Test-Path $Manuscript)) { throw "Manuscript not found: $Manuscript" }
if (-not (Test-Path $BibFile))    { throw "Bibliography not found: $BibFile" }
if (-not (Test-Path $BuildDir))   { New-Item -ItemType Directory -Path $BuildDir | Out-Null }

# --- Resolve pandoc (PATH first, fall back to winget's per-user install location).
$PandocCmd = Get-Command pandoc.exe -ErrorAction SilentlyContinue
if ($PandocCmd) {
    $PandocPath = $PandocCmd.Source
} else {
    $Fallback = Join-Path $env:LOCALAPPDATA 'Pandoc\pandoc.exe'
    if (Test-Path $Fallback) {
        $PandocPath = $Fallback
    } else {
        throw "pandoc not found on PATH and not at $Fallback. Install with: winget install --id JohnMacFarlane.Pandoc"
    }
}
Write-Host "Using pandoc: $PandocPath" -ForegroundColor DarkGray

# --- Common args (reader, citeproc, metadata, standalone).
# DejaVu Serif / DejaVu Sans Mono are used because the manuscript contains
# Greek letters (mu, sigma, rho, nu) and math symbols (le, ge, approx, etc.)
# that are NOT in the default LM Roman font. DejaVu ships with TeX Live and
# has the needed Unicode coverage; switching produces a warning-free build.
$CommonArgs = @(
    '--from', 'markdown+yaml_metadata_block',
    '--citeproc',
    '--bibliography', $BibFile,
    '--metadata', 'suppress-bibliography=true',
    '--metadata', 'link-citations=true',
    '--standalone'
)
$PdfFontArgs = @(
    '--variable', 'mainfont=DejaVu Serif',
    '--variable', 'monofont=DejaVu Sans Mono'
)

# --- .tex output (raw LaTeX source -- no font overrides; the font setup is
#     a PDF-engine concern and would clutter the .tex with non-portable
#     fontspec calls. Anyone compiling the .tex separately should set
#     fonts via their own preamble or compile with xelatex + the same
#     fontspec block used here for the PDF build).
Write-Host "Building $TexOut..." -ForegroundColor Cyan
& $PandocPath $Manuscript @CommonArgs '-o' $TexOut
if ($LASTEXITCODE -ne 0) { throw "pandoc .tex build failed (exit $LASTEXITCODE)" }
Write-Host "OK -> $TexOut" -ForegroundColor Green

# --- .pdf output via xelatex (Unicode-safe, DejaVu fonts).
if (-not $TexOnly) {
    Write-Host "Building $PdfOut..." -ForegroundColor Cyan
    & $PandocPath $Manuscript @CommonArgs @PdfFontArgs '--pdf-engine=xelatex' '-o' $PdfOut
    if ($LASTEXITCODE -ne 0) { throw "pandoc .pdf build failed (exit $LASTEXITCODE)" }
    Write-Host "OK -> $PdfOut" -ForegroundColor Green
}

Write-Host "`nBuild complete." -ForegroundColor Green
