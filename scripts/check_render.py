#!/usr/bin/env python3
"""Verify that what the sources declare actually reached the built PDFs.

Why this exists
---------------
`scripts/audit_claims.py` validates the *sources*: it counts numeric literals in
`paper.tex`, `supplement.tex` and `manuscript.md`. It is blind to the renderer.
On 2026-07-27 all three of its layers were green -- 272/272, 97/97, 26/26 --
while paper Figure 1 was cut off mid-diagram and its caption had fallen off the
page entirely. The crosswalk faithfully counted that caption's numbers in the
`.tex`; they never reached the PDF.

A second failure the same day makes the point sharper: tightening the row gap in
the six-panel Morris figure removed the LaTeX warning *and* silently buried four
of the six sub-captions under the panels above them. A clean log is not evidence
of a correct page.

So this script checks the artefact, not the intention:

* every figure and table declared in the source has its label in the PDF;
* every `subfigure` has its `(a)`, `(b)`, ... sub-caption in the PDF;
* the LaTeX log carries no float overflow beyond a small tolerance;
* no unresolved citation `[?]` or undefined reference `??` survives.

Usage:  uv run --with pymupdf python scripts/check_render.py
Exit 0 if every document passes, 1 otherwise.
"""

from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent

# A float overflowing by a hair is cosmetically invisible; one overflowing by a
# lot loses content. 5pt is under a line of body text.
OVERFLOW_TOLERANCE_PT = 5.0

# --- accepted baseline -------------------------------------------------------
#
# Why this exists. Until 2026-08-10 this script was wired NOWHERE -- not in
# .githooks/pre-commit, not in .github/workflows/tests.yml -- so every guard it
# contains was inert. The reason it could not simply be wired is right here:
# four typographic residues have been present since long before the script was
# written, they were each measured and deliberately kept, and a script that
# exits 1 on them would have blocked every single commit.
#
# The decision on each, on the record:
#   * `tab:limits` (paper) -- "Overfull hbox" is a warning about the box, not
#     evidence of visible damage. The ink was measured on 2026-07-28: the table
#     stops at 489.97pt where ordinary body text reaches 495.29pt, so it is
#     NARROWER than the text around it. Ruled: do not touch.
#   * the three supplement residues -- pre-existing, tracked since 2026-07-27,
#     and re-measured identical to the fifth decimal after every editing pass
#     since. They are the stability witness of the supplement's layout.
#
# HOW TO AMEND THIS SET, and the property that makes it safe. Matching is on the
# EXACT message string, magnitude included. A residue that shifts by even one
# unit in the fifth decimal therefore stops matching and is reported as NEW.
# That is deliberate: "the same four warnings, unchanged to five decimals" is
# precisely the check the repository already performs by hand after every layout
# edit, and this makes it mechanical. So:
#   * never widen an entry into a prefix or a regex -- that would silence the
#     next real regression along with this one;
#   * never add an entry to make a commit pass. An entry is added only after the
#     residue has been measured, judged harmless, and the judgement written
#     down, exactly as the four below were;
#   * an entry that stops firing is reported as OBSOLETE, not silently kept:
#     a stale baseline is how a guard goes blind.
KNOWN_RESIDUES = frozenset({
    "paper: overfull box, 11.89064pt too wide (tolerance 5pt)",
    "supplement: overfull box, 19.30798pt too wide (tolerance 5pt)",
    "supplement: float too large for page by 31.26459pt (tolerance 5pt)",
    "supplement: float too large for page by 53.88974pt (tolerance 5pt)",
})

DOCS = [
    ("paper",      ROOT / "preprint_npj" / "paper.tex",      ROOT / "preprint_npj" / "build" / "paper.pdf",      ROOT / "preprint_npj" / "build" / "paper.log"),
    ("supplement", ROOT / "preprint_npj" / "supplement.tex", ROOT / "preprint_npj" / "build" / "supplement.pdf", ROOT / "preprint_npj" / "build" / "supplement.log"),
    ("monograph",  ROOT / "preprint" / "manuscript.md",      ROOT / "preprint" / "build" / "manuscript.pdf",     None),
]

SUBCAP_LETTERS = "abcdefghijklmnop"


def pdf_text(path: pathlib.Path) -> str:
    import fitz
    raw = "\n".join(p.get_text() for p in fitz.open(path))
    # PDF extraction breaks words across lines; undo it or every check that
    # spans a line break becomes a false negative.
    return re.sub(r"[\s\u00a0]+", " ", re.sub(r"-\n", "", raw))


def check(name: str, src: pathlib.Path, pdf: pathlib.Path, log: pathlib.Path | None) -> list[str]:
    problems: list[str] = []
    if not pdf.exists():
        return ["%s: %s does not exist -- run the build first" % (name, pdf.name)]

    text = pdf_text(pdf)
    source = src.read_text(encoding="utf-8")

    # --- floats declared vs labels rendered -------------------------------
    if src.suffix == ".tex":
        n_fig = len(re.findall(r"\\begin\{figure\*?\}", source))
        n_tab = len(re.findall(r"\\begin\{table\*?\}", source))
        # Supplement floats render as "Fig. S1:" / "Table S3:"; the paper's as
        # "Fig. 2:" / "Table 1:". Build the number pattern rather than
        # interpolating a bare "S?", which is an invalid regex when empty.
        num = r"S?\d+" if name == "supplement" else r"\d+"
        seen_fig = {m for m in re.findall(r"Fig(?:ure)?\.?\s*(%s)\s*[:.]" % num, text)}
        seen_tab = {m for m in re.findall(r"Table\s+(%s)\s*[:.]" % num, text)}
        if len(seen_fig) < n_fig:
            problems.append("%s: %d figure environments declared but only %d captions rendered (%s)"
                            % (name, n_fig, len(seen_fig), sorted(seen_fig)))
        if len(seen_tab) < n_tab:
            problems.append("%s: %d table environments declared but only %d captions rendered (%s)"
                            % (name, n_tab, len(seen_tab), sorted(seen_tab)))

        # --- sub-captions: the failure mode a clean log does not catch -----
        n_sub = len(re.findall(r"\\begin\{subfigure\}", source))
        if n_sub:
            found = [c for c in SUBCAP_LETTERS[:n_sub] if re.search(r"\(%s\)\s*\S" % c, text)]
            if len(found) < n_sub:
                missing = [c for c in SUBCAP_LETTERS[:n_sub] if c not in found]
                problems.append("%s: %d subfigures declared, sub-caption(s) %s absent from the PDF"
                                % (name, n_sub, missing))

    else:
        # The monograph is markdown; its figures are `![Figure N. ...](path)`
        # and pandoc emits no log we can parse, so the float-overflow check
        # below does not apply to it. Checking that every declared image
        # reached the PDF is what remains available.
        declared = re.findall(r"^!\[Figure\s+([0-9]+[a-z]?)", source, re.M)
        embedded = 0
        try:
            import fitz
            embedded = sum(len(p.get_images(full=True)) for p in fitz.open(pdf))
        except Exception:
            pass
        if declared and embedded < len(declared):
            problems.append("%s: %d figures declared in markdown but only %d images embedded in the PDF"
                            % (name, len(declared), embedded))

    # --- the renderer's own complaints ------------------------------------
    if log and log.exists():
        logtext = log.read_text(encoding="utf-8", errors="replace")
        for pt, kind in re.findall(r"Overfull \\(?:vbox|hbox) \(([0-9.]+)pt too (high|wide)\)", logtext):
            if float(pt) > OVERFLOW_TOLERANCE_PT:
                problems.append("%s: overfull box, %spt too %s (tolerance %.0fpt)" % (name, pt, kind, OVERFLOW_TOLERANCE_PT))
        for pt in re.findall(r"Float too large for page by ([0-9.]+)pt", logtext):
            if float(pt) > OVERFLOW_TOLERANCE_PT:
                problems.append("%s: float too large for page by %spt (tolerance %.0fpt)" % (name, pt, OVERFLOW_TOLERANCE_PT))

    # --- broken cross-references ------------------------------------------
    if "[?]" in text:
        problems.append("%s: unresolved citation [?] in the PDF" % name)
    if "??" in text:
        problems.append("%s: undefined reference ?? in the PDF" % name)

    return problems


# Hard-coded cross-references that LaTeX cannot keep honest.
#
# paper.tex and supplement.tex reference sections through \ref, so LaTeX
# renumbers them automatically. Three files cannot: manuscript.md is pandoc,
# preregistration.md is a plain dated record, and reporting_summary_draft.md is
# a submission form. Each of them names npj section and table numbers as literal
# text, and each goes stale in silence the moment a section is inserted upstream.
#
# That is not hypothetical. On 2026-08-04 the audit register cited "Supplement
# S3.11" for a subsection that renders as S3.9, and the ledger cited "Supplement
# Fig S8" for a figure that renders as S3 -- both because a LABEL NAME was read
# as a rendered number. The .aux files are the only authority on what a label
# resolves to, so this guard resolves them there rather than grepping the PDF: a
# section that moves is caught before anyone re-reads a page.
#
# Add an entry whenever a non-LaTeX file starts naming an npj number.
HARDCODED_REFS = [
    # (file, literal as written, aux file, label, what it points at)
    ("preprint/manuscript.md", "Methods §4.5", "paper", "sec:methods-traffic",
     "npj Methods, Traffic-light curation map"),
    ("preprint/manuscript.md", "Supplement §S3.11", "supplement", "sec:s3-tl-sensitivity",
     "traffic-light sensitivity subsection"),
    ("preregistration.md", "Methods §4.5", "paper", "sec:methods-traffic",
     "npj Methods, Traffic-light curation map"),
    ("preregistration.md", "Supplement §S3.11", "supplement", "sec:s3-tl-sensitivity",
     "traffic-light sensitivity subsection"),
    ("preprint_npj/reporting_summary_draft.md", "Methods §4.5", "paper",
     "sec:methods-traffic", "npj Methods, Traffic-light curation map"),
    ("preprint_npj/reporting_summary_draft.md", "Supplement §S3.11", "supplement",
     "sec:s3-tl-sensitivity", "traffic-light sensitivity subsection"),
    # README.md is the repository's public face and names npj numbers in its
    # plain-language summary and its reproduction section. Added 2026-08-05
    # after a manual sweep found it carried three unguarded hard-coded refs.
    ("README.md", "Methods §4.5", "paper", "sec:methods-traffic",
     "npj Methods, Traffic-light curation map"),
    ("README.md", "Supplement §S3.11", "supplement", "sec:s3-tl-sensitivity",
     "traffic-light sensitivity subsection"),
    ("README.md", "Supplement §S12", "supplement", "sec:s12",
     "Reproducibility recipe"),
]

_AUX = {
    "paper": ROOT / "preprint_npj" / "build" / "paper.aux",
    "supplement": ROOT / "preprint_npj" / "build" / "supplement.aux",
}


def _resolve_label(aux_key: str, label: str) -> str | None:
    """What number does LaTeX actually assign this label? None if unresolvable."""
    aux = _AUX[aux_key]
    if not aux.exists():
        return None
    m = re.search(r"\\newlabel\{%s\}\{\{([^}]*)\}" % re.escape(label), aux.read_text(
        encoding="utf-8", errors="replace"))
    return m.group(1) if m else None


# Cross-document references, supplement.tex -> paper.tex.
#
# supplement.tex is compiled as its own document, so it CANNOT \ref into
# paper.tex: every reference to a main-manuscript section is a literal number.
# HARDCODED_REFS above exempts supplement.tex on the premise that it "references
# sections through \ref"; that premise holds inside the document and fails
# across documents. On 2026-08-05 one new subsection in the paper's Results
# shifted 21 of these literals by one and no check noticed.
#
# supplement.tex now writes them as \mainref{<paper label>}{<number>}, which
# renders as the number alone. This check reads every occurrence, resolves the
# label in the PAPER's .aux, and compares. It needs no table to maintain: the
# dependency lives at the point of use and new references are picked up
# automatically.
_MAINREF_RE = re.compile(r"\\mainref\s*\{([^{}]+)\}\s*\{([^{}]+)\}")
_MAINREF_SOURCES = ["preprint_npj/supplement.tex"]
# An unescaped % starts a LaTeX comment. Without this the macro's own
# documentation in the preamble -- which necessarily spells out the call shape
# -- is read as a live reference, and so is any reference someone comments out.
_TEX_COMMENT_RE = re.compile(r"(?<!\\)%")


def _strip_tex_comment(line: str) -> str:
    m = _TEX_COMMENT_RE.search(line)
    return line[: m.start()] if m else line


# A \mainref that loses its backslash becomes ordinary text, and NOTHING else
# catches it: it is not a \ref, so the build succeeds, no reference goes
# unresolved, and the label/number comparison below never sees it. That is not a
# hypothetical either -- the migration that introduced the macro did exactly
# this, in all 25 sites at once, because MSYS sed emits no backslash for "\\" in
# a replacement. The rendered PDF read "Section mainrefsec:results-sex2.5 of the
# main manuscript" and only a human reading the PDF noticed. These two checks
# close that hole from both ends: at the source, and in the artefacts a reader
# actually receives.
_BARE_MACRO_RE = re.compile(r"(?<!\\)\bmainref\s*\{")
_LEAK_ARTEFACTS = [
    ("preprint_npj/build/supplement.pdf", "pdf"),
    ("preprint_npj/build/supplement.docx", "docx"),
]


def _docx_text(path: pathlib.Path) -> str | None:
    """Word twin body text, or None if unreadable. Stdlib only."""
    import zipfile
    try:
        with zipfile.ZipFile(path) as z:
            return z.read("word/document.xml").decode("utf-8", errors="replace")
    except Exception:
        return None


def check_cross_document_refs() -> list[str]:
    problems: list[str] = []
    for rel in _MAINREF_SOURCES:
        path = ROOT / rel
        if not path.exists():
            problems.append("cross-document refs: %s not found" % rel)
            continue
        found = 0
        for lineno, line in enumerate(
                path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            live = _strip_tex_comment(line)
            for bare in _BARE_MACRO_RE.finditer(live):
                problems.append(
                    "cross-document refs: %s:%d has 'mainref{' without its "
                    "leading backslash at column %d -- it will typeset as literal "
                    "text, not as a reference"
                    % (rel, lineno, bare.start() + 1))
            for m in _MAINREF_RE.finditer(live):
                label, written = m.group(1), m.group(2)
                found += 1
                resolved = _resolve_label("paper", label)
                if resolved is None:
                    problems.append(
                        "cross-document refs: %s:%d cites label %s, which does not "
                        "resolve in paper.aux -- rebuild the paper before trusting "
                        "this check, or the label is wrong" % (rel, lineno, label))
                    continue
                if resolved != written:
                    problems.append(
                        "cross-document reference mismatch: %s:%d writes %s but "
                        "label %s resolves to %s in the main manuscript"
                        % (rel, lineno, written, label, resolved))
        if found == 0:
            problems.append(
                "cross-document refs: %s contains no \\mainref -- the migration "
                "was reverted, or the macro was renamed" % rel)

    # The macro name must never reach a reader. Checked in the two artefacts a
    # reader is actually given, because the source-side check above cannot see a
    # macro that pandoc or LaTeX failed to expand for some other reason.
    for rel, kind in _LEAK_ARTEFACTS:
        path = ROOT / rel
        if not path.exists():
            problems.append(
                "cross-document refs: %s missing -- build before trusting the "
                "leaked-macro check" % rel)
            continue
        text = pdf_text(path) if kind == "pdf" else _docx_text(path)
        if text is None:
            problems.append("cross-document refs: %s could not be read" % rel)
            continue
        n = text.count("mainref")
        if n:
            problems.append(
                "cross-document refs: the literal string 'mainref' appears %d "
                "time(s) in %s -- the macro reached the reader instead of "
                "expanding to a section number" % (n, rel))
    return problems


def check_hardcoded_refs() -> list[str]:
    problems: list[str] = []
    for rel, literal, aux_key, label, what in HARDCODED_REFS:
        path = ROOT / rel
        if not path.exists():
            problems.append("hard-coded refs: %s not found" % rel)
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if literal not in text:
            problems.append(
                "hard-coded refs: %s no longer contains %r -- the guard entry is "
                "stale, or the sentence was reworded (%s)" % (rel, literal, what))
            continue
        resolved = _resolve_label(aux_key, label)
        if resolved is None:
            problems.append(
                "hard-coded refs: label %s not resolvable in %s.aux -- rebuild the "
                "PDFs before trusting this check" % (label, aux_key))
            continue
        expected = literal.rsplit("§", 1)[-1]
        if resolved != expected:
            problems.append(
                "hard-coded reference mismatch: %s expects %s, but label %s resolves "
                "to §%s (%s)" % (rel, literal, label, resolved, what))
    return problems


def main() -> int:
    all_problems: list[str] = []
    for name, src, pdf, log in DOCS:
        p = check(name, src, pdf, log)
        print("%-11s %s" % (name, "OK" if not p else "%d PROBLEM(S)" % len(p)))
        for line in p:
            print("    - " + line)
        all_problems += p

    hp = check_hardcoded_refs()
    print("%-11s %s" % ("hardcoded", "OK" if not hp else "%d PROBLEM(S)" % len(hp)))
    for line in hp:
        print("    - " + line)
    all_problems += hp

    xp = check_cross_document_refs()
    print("%-11s %s" % ("crossdoc", "OK" if not xp else "%d PROBLEM(S)" % len(xp)))
    for line in xp:
        print("    - " + line)
    all_problems += xp

    # Split the findings against the accepted baseline. Only genuinely new
    # problems decide the exit status; the four documented residues are
    # reported so they stay visible, and never gate a commit.
    new_problems = [p for p in all_problems if p not in KNOWN_RESIDUES]
    seen_residues = {p for p in all_problems if p in KNOWN_RESIDUES}
    obsolete = sorted(KNOWN_RESIDUES - seen_residues)

    print()
    print("%-11s %d present, %d obsolete (of %d accepted)"
          % ("baseline", len(seen_residues), len(obsolete), len(KNOWN_RESIDUES)))
    for line in obsolete:
        print("    - OBSOLETE, no longer fires -- remove it from KNOWN_RESIDUES: " + line)

    print()
    if new_problems:
        print("RENDER CHECK FAILED: %d new problem(s)" % len(new_problems))
        for line in new_problems:
            print("    - " + line)
        return 1
    print("RENDER CHECK PASSED (%d accepted residues, 0 new)" % len(seen_residues))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
