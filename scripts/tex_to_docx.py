#!/usr/bin/env python3
r"""Convert an npj-submission LaTeX source (paper.tex / supplement.tex) to .docx.

Why this exists
---------------
The Word (.docx) twin of each PDF is produced with pandoc. pandoc's LaTeX
reader does not understand the Springer Nature ``sn-jnl`` class front-matter
macros (``\author*{\fnm..\sur..}``, ``\affil``, ``\abstract{}``,
``\keywords``), so a naive ``pandoc paper.tex -o paper.docx`` silently drops
the author list and the abstract. This helper rewrites *only* that
front-matter region into plain LaTeX that pandoc captures faithfully, writes
the result to a throwaway ``*.docxsrc.tex`` in the build directory, then calls
pandoc on it.

It never touches the committed .tex source, and the PDF build
(``build_npj.ps1`` -> pdflatex) is completely unaffected.

Figures
-------
A Lua filter (``docx_pdf_to_png.lua``, alongside the .tex sources) swaps
``.pdf`` image references to their ``.png`` twins, because Word cannot embed
PDF figures. The two figures that ship only as PDF (fig01_traffic_light,
fig_s2_spearman) are rasterised to PNG by ``build_npj.ps1`` before this runs.

Citations
---------
Resolved with ``--citeproc`` against the paper ``.bib`` using the numbered
Nature CSL (``nature.csl``, vendored next to the .tex sources) so the .docx
in-text markers and reference list match the numbered PDF.

pandoc does not read the ``.bib`` itself but a retyped copy,
``*.docxsrc.bib`` in the build directory. ``nature.csl`` prints a URL only for
web pages and reports, and pandoc maps ``@misc`` to neither, so every
``@misc`` entry lost its ``howpublished`` field in Word: web pages printed no
link and conference papers no venue (found 2026-09-15; guarded by
``scripts/check_docx_structure.py``). ``paper.bib`` cannot be retyped itself,
because ``sn-nature.bst`` needs ``@misc`` for the PDF. In the copy, an
``@misc`` whose ``howpublished`` holds a ``\url`` becomes ``@online`` with that
``url``; any other ``@misc`` with ``howpublished`` becomes ``@inproceedings``
with it as a case-protected ``booktitle``. Word still omits what the CSL never
prints for those types: the ``note`` ("Accessed ...") and the "Technical
report" label.

Cross-references
----------------
pandoc cannot resolve ``xr-hyper`` *external*-document references (e.g. the
paper's ``\ref{sec:s16}`` into the supplement) -- it prints the raw label --
and it miscounts figures built from ``subcaption`` sub-panels (each sub-panel
advances its figure counter, so later ``\ref{fig:..}`` resolve to the wrong
number). Both are fixed here by pre-resolving *every* ``\ref`` / ``\pageref``
to the literal number recorded by LaTeX in the ``.aux`` files (the same numbers
the PDF shows) before handing the source to pandoc. The build's ``paper.aux``
and ``supplement.aux`` must therefore exist (they do: ``build_npj.ps1`` runs
pdflatex before this helper).

Usage
-----
    python scripts/tex_to_docx.py \
        --tex preprint_npj/paper.tex \
        --bib preprint_npj/paper.bib \
        --csl preprint_npj/nature.csl \
        --lua preprint_npj/docx_pdf_to_png.lua \
        --out preprint_npj/build/paper.docx
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

# Retyping of @misc entries for the Word build; see "Citations" in the docstring.
MISC_ENTRY_RE = re.compile(r"^@misc\{([^,]+),\n(.*?)^\}$", re.M | re.S)
HOWPUBLISHED_RE = re.compile(r"^([ \t]*)howpublished\s*=\s*\{(.*)\},[ \t]*$", re.M)
URL_ARG_RE = re.compile(r"\\url\{([^{}]*)\}")


def retype_misc_for_csl(bib: str) -> tuple[str, int, int]:
    """Copy of ``bib`` with each ``@misc`` that has ``howpublished`` retyped for CSL.

    A ``howpublished`` holding ``\\url{U}`` becomes ``@online`` with ``url = {U}``;
    any other becomes ``@inproceedings`` with ``booktitle = {{...}}``, braced so the
    style does not lower-case a conference name. Entries without ``howpublished``
    and all non-``@misc`` entries are returned unchanged. Also returns the number of
    entries retyped to each type.
    """
    counts = {"online": 0, "inproceedings": 0}

    def fix(m: re.Match) -> str:
        key, body = m.group(1), m.group(2)
        hp = HOWPUBLISHED_RE.search(body)
        if not hp:
            return m.group(0)
        indent, value = hp.group(1), hp.group(2)
        url = URL_ARG_RE.search(value)
        if url:
            kind, line = "online", f"{indent}url = {{{url.group(1)}}},"
        else:
            kind, line = "inproceedings", f"{indent}booktitle = {{{{{value}}}}},"
        counts[kind] += 1
        return f"@{kind}{{{key},\n{body[:hp.start()]}{line}{body[hp.end():]}}}"

    return MISC_ENTRY_RE.sub(fix, bib), counts["online"], counts["inproceedings"]


def _braced(s: str, open_idx: int) -> tuple[str, int]:
    r"""Return (content, index_after_closing_brace) for a balanced ``{...}``.

    ``s[open_idx]`` must be ``{``. Handles nested braces, which the SN
    abstract and affiliation arguments contain (e.g. ``1{,}280``,
    ``\orgaddress{\city{..}}``).
    """
    assert s[open_idx] == "{", "expected '{' at open_idx"
    depth = 0
    j = open_idx
    while j < len(s):
        c = s[j]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s[open_idx + 1 : j], j + 1
        j += 1
    raise ValueError("unbalanced braces starting at index %d" % open_idx)


def _collect_and_remove(tex: str, name: str) -> tuple[str, list[str]]:
    r"""Remove every ``\name`` / ``\name*`` (with optional ``[..]`` then one
    balanced ``{..}``) from ``tex``; return (new_tex, [arg_contents]) in order.
    """
    pat = re.compile(r"\\" + name + r"\*?\s*(?:\[[^\]]*\])?\s*\{")
    out: list[str] = []
    args: list[str] = []
    i = 0
    while True:
        m = pat.search(tex, i)
        if not m:
            out.append(tex[i:])
            break
        content, end = _braced(tex, m.end() - 1)
        args.append(content)
        out.append(tex[i : m.start()])
        i = end
    return "".join(out), args


def _strip_org_macros(affil_arg: str) -> str:
    r"""Collapse ``\orgdiv{X}\orgname{Y}\orgaddress{\city{C}..}`` to plain
    comma-joined text by repeatedly replacing innermost brace-free macros.
    """
    pat = re.compile(
        r"\\(?:orgdiv|orgname|orgaddress|city|state|postcode|street|country)"
        r"\s*\{([^{}]*)\}"
    )
    prev = None
    text = affil_arg
    while prev != text:
        prev = text
        text = pat.sub(lambda m: m.group(1), text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s*,\s*", ", ", text).strip().strip(",").strip()
    return text


def parse_aux_labels(build_dir: Path) -> dict[str, tuple[str, str]]:
    r"""Scan every ``*.aux`` in ``build_dir`` for hyperref ``\newlabel`` entries.

    Returns ``{label: (ref_string, page_string)}``. The hyperref 5-field form is
    ``\newlabel{LABEL}{{REF}{PAGE}{TITLE}{ANCHOR}{}}``; ``REF`` is what ``\ref``
    prints and ``PAGE`` is what ``\pageref`` prints. Loading *all* aux files
    (paper + supplement) means cross-document references resolve too. Cleveref
    helper entries (``LABEL@cref``) are skipped.
    """
    labels: dict[str, tuple[str, str]] = {}
    marker = "\\newlabel{"
    for aux in sorted(build_dir.glob("*.aux")):
        try:
            text = aux.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        i = 0
        while True:
            k = text.find(marker, i)
            if k < 0:
                break
            brace = k + len(marker) - 1  # points at the '{' of {LABEL}
            try:
                label, after = _braced(text, brace)
                j = after
                while j < len(text) and text[j] in " \t":
                    j += 1
                if j >= len(text) or text[j] != "{":
                    i = after
                    continue
                data, after2 = _braced(text, j)  # data = "{REF}{PAGE}{..}.."
                ref = page = ""
                if data.startswith("{"):
                    ref, d1 = _braced(data, 0)
                    while d1 < len(data) and data[d1] in " \t":
                        d1 += 1
                    if d1 < len(data) and data[d1] == "{":
                        page, _ = _braced(data, d1)
                if "@" not in label:
                    labels[label] = (ref.strip(), page.strip())
                i = after2
            except ValueError:
                i = k + len(marker)
    return labels


def resolve_refs(tex: str, labels: dict[str, tuple[str, str]]) -> str:
    r"""Replace ``\ref``/``\pageref``/``\autoref``/``\eqref``/``\cref``/``\Cref``
    with the literal number from the ``.aux`` so the .docx cross-references match
    the PDF exactly. Labels absent from every aux are left untouched for pandoc.
    Also strips the ``\externaldocument`` directive (its refs are now resolved).
    """
    def num(label: str) -> str | None:
        hit = labels.get(label.strip())
        return hit[0] if hit else None

    def page(label: str) -> str | None:
        hit = labels.get(label.strip())
        return hit[1] if hit else None

    def repl_num(m: "re.Match[str]") -> str:
        n = num(m.group(1))
        return n if n is not None else m.group(0)

    def repl_eq(m: "re.Match[str]") -> str:
        n = num(m.group(1))
        return f"({n})" if n is not None else m.group(0)

    def repl_page(m: "re.Match[str]") -> str:
        p = page(m.group(1))
        return p if p is not None else m.group(0)

    # \mainref{<label in paper.tex>}{<number>} -- cross-document reference to a
    # main-manuscript section, defined in supplement.tex. It must be unwrapped to
    # its literal number BEFORE the \ref family is handled below: the label it
    # carries belongs to paper.tex and is deliberately absent from this
    # document's .aux, so leaving it for repl_num would resolve nothing, and
    # leaving it for pandoc would drop an unknown two-argument macro and silently
    # strip 25 section numbers from the Word twin.
    tex = re.sub(r"\\mainref\s*\{[^{}]+\}\s*\{([^{}]+)\}", r"\1", tex)

    # \S\ref{...} to a SUPPLEMENT section resolves to "\SS3.13": the number starts
    # with a letter, so pandoc reads "\SS" as one unknown control word and drops it
    # together with the number. The PDF printed "§S3.13" and the Word twin printed
    # nothing, in 28 paper and 46 supplement call sites of that form (found
    # 2026-09-15, audit/number_inventory.md section 9, O-D1). An empty group ends
    # the control word without adding a space, so the twin now prints "§S3.13".
    tex = re.sub(r"\\S(?=\\(?:ref|autoref|cref|Cref)\s*\{)", r"\\S{}", tex)

    tex = re.sub(r"\\pageref\s*\{([^{}]+)\}", repl_page, tex)
    tex = re.sub(r"\\eqref\s*\{([^{}]+)\}", repl_eq, tex)
    tex = re.sub(r"\\(?:ref|autoref|cref|Cref)\s*\{([^{}]+)\}", repl_num, tex)
    tex = re.sub(
        r"\\externaldocument\s*(?:\[[^\]]*\])?\s*\{[^}]*\}", "", tex
    )
    return tex


def flatten_subfigures(tex: str) -> str:
    r"""Collapse ``subcaption`` sub-panels so pandoc emits ONE figure per
    ``figure`` environment (otherwise each sub-panel advances pandoc's figure
    counter and the auto-numbered captions drift out of step with the PDF).

    Each ``\begin{subfigure}..\includegraphics{img}..\caption{LBL}..\end{subfigure}``
    becomes ``\includegraphics{img} (LBL)`` -- the panel image followed by its
    short label in parentheses -- with the wrapping environment removed. The
    surrounding single ``figure`` + master ``\caption`` is preserved, so the
    block renders as one numbered figure whose panels are still labelled.
    """
    def repl(m: "re.Match[str]") -> str:
        body = m.group(1)
        img = re.search(r"\\includegraphics\s*(?:\[[^\]]*\])?\s*\{[^}]*\}", body)
        cap = re.search(r"\\caption\s*\{([^{}]*)\}", body)
        if not img:
            return ""
        panel = img.group(0)
        if cap and cap.group(1).strip():
            panel += " (" + cap.group(1).strip() + ")"
        return panel

    return re.sub(
        r"\\begin\{subfigure\}(.*?)\\end\{subfigure\}",
        repl,
        tex,
        flags=re.DOTALL,
    )


def transform_frontmatter(tex: str) -> str:
    r"""Rewrite the sn-jnl front matter into pandoc-friendly LaTeX.

    Title (``\title[..]{..}``) is left untouched -- pandoc reads it correctly.
    Authors, affiliations, abstract, and keywords are extracted and re-emitted
    as a plain ``\author{.. \and ..}`` line plus body sections after
    ``\maketitle``.
    """
    tex, author_args = _collect_and_remove(tex, "author")
    tex, affil_args = _collect_and_remove(tex, "affil")
    tex, abstract_args = _collect_and_remove(tex, "abstract")
    tex, keyword_args = _collect_and_remove(tex, "keywords")
    # Leftover \email{..} (trails each \author in the SN template).
    tex = re.sub(r"\\email\s*\{[^}]*\}", "", tex)

    names: list[str] = []
    for arg in author_args:
        fnm = re.search(r"\\fnm\s*\{([^}]*)\}", arg)
        sur = re.search(r"\\sur\s*\{([^}]*)\}", arg)
        if fnm and sur:
            names.append(f"{fnm.group(1).strip()} {sur.group(1).strip()}")
        else:
            # Fall back to the raw argument with macro wrappers stripped.
            cleaned = re.sub(r"\\[a-zA-Z]+\s*", "", arg).strip()
            if cleaned:
                names.append(cleaned)
    author_line = "\\author{" + " \\and ".join(names) + "}" if names else ""

    post_parts: list[str] = []
    if abstract_args:
        post_parts.append("\\section*{Abstract}\n" + abstract_args[0].strip())
    if keyword_args:
        post_parts.append(
            "\\noindent\\textbf{Keywords:} " + keyword_args[0].strip()
        )
    if affil_args:
        items = "\n".join(
            f"\\item {_strip_org_macros(a)}" for a in affil_args
        )
        post_parts.append(
            "\\section*{Author affiliations}\n"
            "\\begin{enumerate}\n" + items + "\n\\end{enumerate}"
        )
    post_block = "\n\n".join(post_parts)

    if "\\maketitle" in tex:
        # author def before \maketitle so pandoc's title block picks it up;
        # abstract/keywords/affiliations as body content right after it.
        tex = tex.replace(
            "\\maketitle",
            (author_line + "\n\n" if author_line else "")
            + "\\maketitle\n\n"
            + post_block,
            1,
        )
    else:
        # No \maketitle: drop the reconstructed block in after \begin{document}.
        inject = (author_line + "\n\n" + post_block) if post_block else author_line
        tex = tex.replace("\\begin{document}", "\\begin{document}\n" + inject, 1)
    return tex


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tex", required=True, type=Path)
    ap.add_argument("--bib", required=True, type=Path)
    ap.add_argument("--csl", required=True, type=Path)
    ap.add_argument("--lua", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument(
        "--pandoc", default="pandoc", help="pandoc executable (default: PATH)"
    )
    args = ap.parse_args()

    tex_path = args.tex.resolve()
    src_dir = tex_path.parent  # figures/ paths are relative to this dir
    out_path = args.out.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    original = tex_path.read_text(encoding="utf-8")
    munged = transform_frontmatter(original)
    # Collapse subcaption sub-panels to one figure each, then resolve every
    # cross-reference to the literal .aux number (fixes pandoc's inability to
    # resolve xr-hyper external refs and its sub-panel figure miscounting).
    munged = flatten_subfigures(munged)
    labels = parse_aux_labels(out_path.parent)
    if labels:
        munged = resolve_refs(munged, labels)
    else:
        print(
            "  WARNING: no .aux labels found in build dir; cross-references "
            "will fall back to pandoc (may be unresolved/miscounted).",
            file=sys.stderr,
        )

    # Throwaway preprocessed source -> build dir (gitignored).
    src_tex = out_path.parent / (tex_path.stem + ".docxsrc.tex")
    src_tex.write_text(munged, encoding="utf-8")

    # Retyped bibliography copy for pandoc -> build dir (gitignored).
    docx_bib_text, n_online, n_proc = retype_misc_for_csl(args.bib.read_text(encoding="utf-8"))
    docx_bib = out_path.parent / (tex_path.stem + ".docxsrc.bib")
    docx_bib.write_text(docx_bib_text, encoding="utf-8")
    print(f"  bibliography for Word: {n_online} @misc -> @online, "
          f"{n_proc} @misc -> @inproceedings ({docx_bib.name})")

    cmd = [
        args.pandoc,
        str(src_tex),
        "--citeproc",
        "--bibliography",
        str(docx_bib.resolve()),
        "--csl",
        str(args.csl.resolve()),
        "--lua-filter",
        str(args.lua.resolve()),
        "--metadata",
        "link-citations=true",
        "--resource-path",
        str(src_dir),
        "--standalone",
        "-o",
        str(out_path),
    ]
    print("  " + " ".join(cmd))
    result = subprocess.run(cmd, cwd=str(src_dir))
    if result.returncode != 0 or not out_path.exists():
        print(f"FAIL: pandoc did not produce {out_path}", file=sys.stderr)
        return 1
    print(f"OK -> {out_path}  ({out_path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
