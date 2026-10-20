"""Merge paper.tex and supplement.tex into one arXiv source package, compile it,
and check that the upload set compiles on its own.

Why this exists
---------------
arXiv builds one PDF per submission, and the paper refers to the supplement
through xr-hyper (\\externaldocument{supplement}), which needs supplement.aux
at compile time. The June 2026 package therefore merged the two documents by
hand into a single arxiv_main.tex. Every later edit of either source made that
hand merge stale, and the merge had to be redone from scratch. This script
redoes it mechanically from the current sources, so that a new freeze only
needs one command.

What the merge does
-------------------
- Preamble: paper.tex's, without xr-hyper and \\externaldocument (inside one
  document the paper's \\ref{sec:s*} resolve directly), plus the supplement's
  \\mainref macro, kept as "print the number as written" so the supplement's
  text is the frozen text.
- Body: the paper, then \\clearpage and the supplement from after its
  \\maketitle, with sections, figures and tables restarted and prefixed "S",
  hyperref anchors prefixed too (otherwise a link to S1 lands on Section 1),
  and the supplement's float-page fraction and wider TOC number box.
- The supplement's table of contents lists only the S sections: tocdepth is
  set to -10 in the .toc before the paper's entries and restored before the
  supplement's.
- One bibliography, at the end, as in the June package.

What it does not do: change any text. Run it on a frozen tree, and record the
freeze it was built from.

Usage
-----
    uv run python scripts/build_arxiv_package.py --out C:/path/to/new/folder
    uv run python scripts/build_arxiv_package.py --out ... --no-flafter

The output folder must not exist or be empty. It receives work/ (the compile
folder), upload/ (the files to send to arXiv), upload_check/ (upload/ compiled
again on its own, without bibtex) and arxiv_upload.zip (upload/ zipped).
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import shutil
import subprocess
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8")

REPO = pathlib.Path(__file__).resolve().parents[1]
SRC = REPO / "preprint_npj"
MAIN = "arxiv_main"


def take_once(text: str, needle: str, what: str) -> int:
    n = text.count(needle)
    if n != 1:
        sys.exit(f"merge: expected 1 occurrence of {what!r}, found {n}")
    return text.index(needle)


def drop_line(text: str, needle: str) -> str:
    lines = text.splitlines(keepends=True)
    hits = [i for i, line in enumerate(lines) if needle in line]
    if len(hits) != 1:
        sys.exit(f"merge: expected 1 line containing {needle!r}, found {len(hits)}")
    del lines[hits[0]]
    return "".join(lines)


def merge(flafter: bool) -> str:
    paper = (SRC / "paper.tex").read_text(encoding="utf-8")
    supp = (SRC / "supplement.tex").read_text(encoding="utf-8")

    begin = "\\begin{document}"
    bib = "\\bibliography{paper}"

    preamble = paper[: take_once(paper, begin, begin)]
    preamble = drop_line(preamble, "\\usepackage{xr-hyper}")
    preamble = drop_line(preamble, "\\externaldocument{supplement}")
    extra = [
        "",
        "%% arXiv merge (scripts/build_arxiv_package.py): the supplement's macros.",
        "\\newcommand{\\mainref}[2]{#2}% number as written in the supplement",
    ]
    if flafter:
        extra.append("\\usepackage{flafter}% loaded by supplement.tex; applies to the whole document")
    preamble = preamble.rstrip("\n") + "\n" + "\n".join(extra) + "\n\n"

    p0 = take_once(paper, begin, begin) + len(begin)
    paper_body = paper[p0 : take_once(paper, bib, "paper " + bib)]

    s0 = take_once(supp, "\\maketitle", "\\maketitle") + len("\\maketitle")
    supp_body = supp[s0 : take_once(supp, bib, "supplement " + bib)]
    take_once(supp_body, "\\tableofcontents", "\\tableofcontents")

    toc_off = "\\addtocontents{toc}{\\protect\\setcounter{tocdepth}{-10}}%\n"
    toc_on = "\\addtocontents{toc}{\\protect\\setcounter{tocdepth}{\\arabic{tocdepth}}}%\n"

    seam = (
        "\n%%%%%%%%%% SUPPLEMENTARY INFORMATION (merged for the arXiv single-PDF deposit) %%%%%%%%%%\n"
        "\\clearpage\n"
        "\\setcounter{section}{0}\\setcounter{figure}{0}\\setcounter{table}{0}\n"
        "\\renewcommand{\\thesection}{S\\arabic{section}}\n"
        "\\renewcommand{\\thefigure}{S\\arabic{figure}}\n"
        "\\renewcommand{\\thetable}{S\\arabic{table}}\n"
        "\\renewcommand{\\theHsection}{S\\arabic{section}}\n"
        "\\renewcommand{\\theHfigure}{S\\arabic{figure}}\n"
        "\\renewcommand{\\theHtable}{S\\arabic{table}}\n"
        "\\renewcommand{\\floatpagefraction}{0.7}\n"
        "\\makeatletter\n\\renewcommand\\numberline[1]{\\hb@xt@ 3em{#1\\hfil}}\n\\makeatother\n"
        + toc_on
        + "\\section*{Supplementary Information}\n"
    )

    return (
        "\\pdfoutput=1\n"
        + preamble
        + begin
        + "\n"
        + toc_off
        + paper_body
        + seam
        + supp_body
        + "\n"
        + bib
        + "\n\n\\end{document}\n"
    )


def run(cmd: list[str], cwd: pathlib.Path) -> None:
    subprocess.run(cmd, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)


def compile_dir(d: pathlib.Path, with_bibtex: bool) -> str:
    pdflatex = ["pdflatex", "-interaction=nonstopmode", f"{MAIN}.tex"]
    run(pdflatex, d)
    if with_bibtex:
        run(["bibtex", MAIN], d)
    log = ""
    for _ in range(4):
        run(pdflatex, d)
        log = (d / f"{MAIN}.log").read_text(encoding="latin-1")
        if "Rerun to get" not in log and "Label(s) may have changed" not in log:
            break
    return log


def log_problems(log: str) -> dict[str, int]:
    return {
        "undefined reference/citation": len(re.findall(r"(Reference|Citation) `[^']*' on page \d+ undefined", log)),
        "multiply defined label": len(re.findall(r"Label `[^']*' multiply defined", log)),
        "duplicate hyperref destination": log.count("destination with the same identifier"),
        "rerun still requested": int("Rerun to get" in log or "Label(s) may have changed" in log),
        "LaTeX error": log.count("\n! "),
    }


def pages(pdf: pathlib.Path) -> str:
    out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=False).stdout
    m = re.search(r"^Pages:\s+(\d+)", out, re.M)
    return m.group(1) if m else "?"


def sha256(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True, type=pathlib.Path)
    ap.add_argument("--no-flafter", action="store_true", help="do not load flafter")
    args = ap.parse_args()

    out = args.out.resolve()
    if out.exists() and any(out.iterdir()):
        sys.exit(f"{out} exists and is not empty; choose a new folder")
    work, upload, check = out / "work", out / "upload", out / "upload_check"
    for d in (work, upload / "figures"):
        d.mkdir(parents=True)

    tex = merge(flafter=not args.no_flafter)
    (work / f"{MAIN}.tex").write_text(tex, encoding="utf-8")
    figures = sorted(set(re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}", tex)))
    (work / "figures").mkdir()
    for name in ("sn-jnl.cls", "sn-nature.bst", "paper.bib"):
        shutil.copy2(SRC / name, work / name)
    for f in figures:
        shutil.copy2(SRC / f, work / f)

    log = compile_dir(work, with_bibtex=True)
    print(f"work/{MAIN}.pdf: {pages(work / f'{MAIN}.pdf')} pages, {len(figures)} figures")
    problems = log_problems(log)
    for k, v in problems.items():
        print(f"  {'ok  ' if v == 0 else 'FAIL'}  {k}: {v}")

    sent = [f"{MAIN}.tex", f"{MAIN}.bbl", "sn-jnl.cls", "sn-nature.bst", *figures]
    for f in sent:
        shutil.copy2(work / f, upload / f)
    shutil.copytree(upload, check)
    clog = compile_dir(check, with_bibtex=False)
    cproblems = log_problems(clog)
    print(f"upload_check/{MAIN}.pdf (upload set alone, no bibtex): {pages(check / f'{MAIN}.pdf')} pages")
    for k, v in cproblems.items():
        print(f"  {'ok  ' if v == 0 else 'FAIL'}  {k}: {v}")

    with zipfile.ZipFile(out / "arxiv_upload.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for f in sent:
            z.write(upload / f, f)
    print("upload set (SHA-256):")
    for f in sent:
        print(f"  {sha256(upload / f)}  {f}")
    print(f"  {sha256(out / 'arxiv_upload.zip')}  arxiv_upload.zip")
    return 0 if not any(problems.values()) and not any(cproblems.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
