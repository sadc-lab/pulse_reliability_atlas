"""Structural check of the .docx twins against their LaTeX sources.

The co-author review round is dispatched as .docx, not as PDF, so the question
"did every figure, table and caption survive the pandoc conversion, and in the
right order?" is not answered by check_render.py, which only reads the PDFs.

WHY THE MATCHING IS THE WAY IT IS. A first version of this check reported seven
defects, all false. Each fix below is named after the false positive that forced
it, because a checker that produces plausible-looking noise is worse than no
checker at all:

  - zero-width spaces and subscripts: pandoc renders PaO2 as 'PaO \u200b 2',
    so a naive substring search for the caption text fails;
  - the +/- sign survives conversion as a different codepoint;
  - short keys collide. Matching a caption by its first two words made the
    key 'HR' match 114 times, including inside the abstract. Keys are now built
    from the first 8, 6 or 5 words and are REQUIRED to be unique; a caption
    whose key still collides is reported as ambiguous and explicitly NOT
    judged, rather than silently counted as a pass or a failure.

CALIBRATION. The script ends by looking for a string known to be present and a
string known to be absent. If either control comes out wrong, the matching layer
is broken and every verdict above it is meaningless, whatever it says.

Usage:  python scripts/check_docx_structure.py
Exit:   0 if every structural check passes, 1 otherwise.
"""
import re
import sys
import unicodedata
import zipfile
from collections import Counter
from pathlib import Path

from tex_to_docx import _braced, parse_aux_labels

REPO = Path(__file__).resolve().parent.parent
NPJ = REPO / "preprint_npj"
PAIRS = [
    ("paper", NPJ / "paper.tex", NPJ / "build/paper.docx"),
    ("supplement", NPJ / "supplement.tex", NPJ / "build/supplement.docx"),
]

# Controls. The first must appear in paper.docx, the second must not appear in
# any document. Both are checked at the end; see CALIBRATION above.
CONTROL_PRESENT = "study design of the"
CONTROL_ABSENT = "zzz not in this document zzz"


def norm(s: str) -> str:
    """Fold away the conversion artefacts that made the first version lie."""
    s = unicodedata.normalize("NFKD", s)
    s = s.replace("\u200b", "").replace("\u00b1", "+-")
    s = re.sub(r"[^A-Za-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    return norm(re.sub(r"<[^>]+>", " ", xml))


def captions(tex: str) -> list[tuple[str, str]]:
    """Return (kind, normalised caption) in source order."""
    order: list[list] = []
    for m in re.finditer(r"\\begin\{(figure|table)\}|\\caption\{", tex):
        if m.group(1):
            order.append([m.group(1), None])
            continue
        i, depth, buf = m.end(), 1, []
        while depth and i < len(tex):
            depth += {"{": 1, "}": -1}.get(tex[i], 0)
            if depth:
                buf.append(tex[i])
            i += 1
        text = re.sub(r"\\textbf\{([^}]*)\}", r"\1", "".join(buf))
        text = re.sub(r"\\[a-zA-Z]+\*?", " ", text)
        if order and order[-1][1] is None:
            order[-1][1] = norm(text)
    return [(k, c) for k, c in order if c]


# Section-sign references. Added 2026-09-15 (audit/number_inventory.md section 9,
# O-D1): every \S\ref to a supplement section printed NOTHING in both Word twins,
# because the resolved number starts with "S" and "\SS3.13" is one unknown control
# word to pandoc. Captions and images were intact, so the checks above passed.
SREF = re.compile(r"\\S(?:\\,|~)?\\ref\s*\{([^{}]+)\}")


def section_ref_numbers(tex: str, labels: dict[str, tuple[str, str]]) -> tuple[Counter, list[str]]:
    """How many times each section number is announced with a section sign, and
    the labels that did not resolve. ⚠️ An unresolved label must fail, not be
    skipped: the first version skipped it, so a build without its .aux passed
    this check with nothing checked."""
    tex = re.sub(r"(?<!\\)%.*", "", tex)
    wanted: Counter = Counter()
    unresolved: list[str] = []
    for m in SREF.finditer(tex):
        hit = labels.get(m.group(1).strip())
        if hit and hit[0]:
            wanted[hit[0]] += 1
        else:
            unresolved.append(m.group(1).strip())
    return wanted, unresolved


def section_sign_count(raw: str, number: str) -> int:
    """Occurrences of '§' + optional (thin, no-break) space + the exact number."""
    return len(re.findall("§[\\s   ]*" + re.escape(number) + r"(?![\d.]\d)", raw))


# Reference links and venues. Added 2026-09-15: every @misc entry of paper.bib
# lost its `howpublished` field in both Word twins. The nine Kitware pages and the
# DeepSeek report printed no URL, and three conference papers no venue, because
# nature.csl prints a URL only for web pages and reports and pandoc maps @misc to
# neither. The PDFs were right, so every check above passed.
BIB = NPJ / "paper.bib"
MISC_RE = re.compile(r"^@misc\{([^,]+),\n(.*?)^\}$", re.M | re.S)
HOWPUB_RE = re.compile(r"^\s*howpublished\s*=\s*\{(.*)\},\s*$", re.M)
URL_RE = re.compile(r"\\url\{([^{}]*)\}")
# Same citation forms as scripts/check_citations.py, locator form included.
CITE_RE = re.compile(r"\\cite[tp]?\*?(?:\[[^\]]*\]){0,2}\{([^}]*)\}")


def misc_expectations(bib: str) -> dict[str, str]:
    """For each @misc entry with a howpublished field, what its Word reference must
    carry: the URL when howpublished holds one, otherwise the venue text."""
    out: dict[str, str] = {}
    for m in MISC_RE.finditer(bib):
        hp = HOWPUB_RE.search(m.group(2))
        if hp:
            url = URL_RE.search(hp.group(1))
            out[m.group(1)] = url.group(1) if url else hp.group(1)
    return out


def reference_entry(xml: str, key: str) -> str | None:
    """Normalised text of the bibliography paragraph pandoc bookmarks as ref-<key>."""
    for para in xml.split("</w:p>"):
        if f'w:name="ref-{key}"' in para:
            return norm(re.sub(r"<[^>]+>", " ", para))
    return None


# Numbering. Added 2026-10-06, after M. Sauthier read the Word twins and asked
# whether the missing figure, table and section numbers were intended: pandoc
# printed every caption and heading without its number, dropped the \bmhead
# back-matter headings and the supplement's contents, and gave the reference list
# no heading. Every check above passed, because none of them read a number.
FLOAT_LABEL = re.compile(r"\\begin\{(figure|table)\*?\}.*?\\label\{((?:fig|tab):[^{}]+)\}", re.S)
HEADING_LABEL = re.compile(r"\\(?:section|subsection|subsubsection)\{.*?\}\s*\\label\{([^{}]+)\}")
BMHEAD = re.compile(r"\\bmhead\{([^{}]*)\}")
CAPTION_NUMBER = re.compile(r"^(Figure|Table) (S?\d+)\.")


def paragraphs(xml: str) -> list[tuple[str, str]]:
    """(paragraph style id, plain text) for every paragraph of document.xml."""
    out = []
    for para in xml.split("</w:p>"):
        style = re.search(r'<w:pStyle w:val="([^"]+)"', para)
        text = re.sub(r"<[^>]+>", "", para)
        text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        out.append((style.group(1) if style else "", re.sub(r"\s+", " ", text).strip()))
    return out


def numbering_problems(paras: list[tuple[str, str]], want_floats: Counter,
                       want_headings: set[str], want_titles: list[str]) -> list[str]:
    """What the Word twin fails to number or title, against what the .tex announces."""
    problems = []
    got_floats = Counter()
    for style, text in paras:
        if "Caption" in style:
            m = CAPTION_NUMBER.match(text)
            if m:
                got_floats[f"{m.group(1)} {m.group(2)}"] += 1
            elif text:
                problems.append(f"caption without a number: {ascii(text[:60])}")
    for key in sorted(set(want_floats) | set(got_floats)):
        if got_floats[key] != want_floats[key]:
            problems.append(f"'{key}.' caption: {want_floats[key]} in .tex, {got_floats[key]} in .docx")
    heads = [text for style, text in paras if style.startswith("Heading")]
    starts = {h.split(" ", 1)[0] for h in heads}
    for number in sorted(want_headings - starts):
        problems.append(f"no heading numbered {number}")
    for title in want_titles:
        if title not in heads:
            problems.append(f"no heading {ascii(title)}")
    return problems


# Table structure. Added 2026-10-07: two-line \shortstack header cells broke
# Table 3, Table S7 and Table S10 in Word -- pandoc read the \\ inside the cell
# as a row break, added a row and lost the first line of the cell -- while
# every check above passed, because none of them counted table rows. Each
# LaTeX tabular must reach Word with the same number of rows; a Word table that
# holds images is pandoc's layout for a multi-panel figure and is not counted.
def latex_row_counts(tex: str) -> list[int]:
    """Rows of each tabular: top-level \\\\ only, so a \\\\ inside a cell's braces is not a row."""
    counts = []
    for m in re.finditer(r"\\begin\{tabular\}(.*?)\\end\{tabular\}", tex, re.S):
        body = m.group(1)
        if body.startswith("{"):  # the column specification
            depth = 0
            for j, c in enumerate(body):
                depth += {"{": 1, "}": -1}.get(c, 0)
                if depth == 0:
                    body = body[j + 1:]
                    break
        depth, rows, i = 0, 0, 0
        while i < len(body):
            if body[i] == "{":
                depth += 1
            elif body[i] == "}":
                depth -= 1
            elif body.startswith("\\\\", i) and depth == 0:
                rows += 1
                i += 2
                continue
            i += 1
        counts.append(rows)
    return counts


def word_row_counts(xml: str) -> list[int]:
    """Rows of each Word data table, in document order."""
    return [len(re.findall(r"<w:tr[ >]", t)) for t in re.findall(r"<w:tbl>.*?</w:tbl>", xml, re.S)
            if "<w:drawing" not in t]


AFFIL = re.compile(r"\\affil\*?\s*\[[^\]]*\]\s*\{")


def affiliation_problems(live: str, paras: list[tuple[str, str]]) -> list[str]:
    r"""Every affiliation must carry a city and a country, and reach Word whole.

    npj asks for "institution, city, and country" (content-types page, Article
    table); affiliation 6 had no city until 2026-10-07. When it was added as
    ``\city{Vand\oe{}uvre-l\`es-Nancy}``, the converter could not expand the
    braced argument and the Word file lost the city and the country while the
    PDF stayed correct. So: in the .tex, each ``\affil`` has ``\city`` and
    ``\country``; in the .docx, the i-th paragraph under "Author affiliations"
    ends with the i-th country.
    """
    problems, countries = [], []
    for n, m in enumerate(AFFIL.finditer(live), 1):
        arg, _ = _braced(live, m.end() - 1)
        country = re.search(r"\\country\{([^{}]*)\}", arg)
        if not re.search(r"\\city\{", arg):
            problems.append(f"affiliation {n}: no \\city in the .tex")
        if not country:
            problems.append(f"affiliation {n}: no \\country in the .tex")
        countries.append(country.group(1) if country else None)
    start = next((i for i, (_, t) in enumerate(paras) if t == "Author affiliations"), None)
    if countries and start is None:
        return problems + ["no 'Author affiliations' heading in the .docx"]
    for n, country in enumerate(countries, 1):
        text = paras[start + n][1] if start is not None and start + n < len(paras) else ""
        if country and not text.endswith(country):
            problems.append(f"affiliation {n} in Word does not end with '{country}': ...{text[-60:]!r}")
    return problems


def main() -> int:
    fails = 0
    labels = parse_aux_labels(NPJ / "build")
    for name, tex_path, docx_path in PAIRS:
        if not docx_path.exists():
            print(f"*** {name}.docx not built -- run preprint_npj/build_npj.ps1 first")
            return 1
        tex = tex_path.read_text(encoding="utf-8")
        body = docx_text(docx_path)
        caps = captions(tex)
        with zipfile.ZipFile(docx_path) as z:
            media = [n for n in z.namelist() if n.startswith("word/media/")]
        n_inc = len(re.findall(r"\\includegraphics", tex))

        print(f"\n=== {name}.docx ===")
        ok_media = len(media) >= n_inc
        print(f"  images: {n_inc} \\includegraphics -> {len(media)} media files  "
              f"{'OK' if ok_media else '*** MISSING ***'}")
        fails += 0 if ok_media else 1

        located, missing, ambiguous = [], [], []
        for kind, cap in caps:
            words = cap.split()
            key = next((" ".join(words[:n]) for n in (8, 6, 5)
                        if body.count(" ".join(words[:n])) == 1), None)
            if key is None:
                longest = " ".join(words[:8])
                hits = body.count(longest)
                (missing if hits == 0 else ambiguous).append((kind, longest, hits))
                continue
            located.append((kind, key, body.find(key)))

        print(f"  captions: {len(caps)} in .tex, {len(located)} located uniquely, "
              f"{len(ambiguous)} ambiguous, {len(missing)} MISSING")
        for kind, cap, _ in missing:
            print(f"  *** MISSING {kind}: {cap!r}")
            fails += 1
        for kind, cap, hits in ambiguous:
            print(f"  (ambiguous, {hits} matches, not judged) {kind}: {cap[:50]!r}")

        in_order = all(located[i][2] < located[i + 1][2] for i in range(len(located) - 1))
        print(f"  located captions in source order: "
              f"{'OK' if in_order else '*** OUT OF ORDER ***'}")
        fails += 0 if in_order else 1

        with zipfile.ZipFile(docx_path) as z:
            raw = re.sub(r"<[^>]+>", "", z.read("word/document.xml").decode("utf-8"))
        wanted, unresolved = section_ref_numbers(tex, labels)
        short = {n: (k, section_sign_count(raw, n)) for n, k in wanted.items()
                 if section_sign_count(raw, n) < k}
        print(f"  section-sign refs: {sum(wanted.values())} resolved in .tex to {len(wanted)} numbers, "
              f"{len(short)} number(s) printed fewer times than announced, "
              f"{len(unresolved)} label(s) unresolved in the build's .aux "
              f"{'OK' if not short and not unresolved else '*** MISSING ***'}")
        for n, (k, got) in sorted(short.items()):
            print(f"  *** '§{n}': {k} in .tex, {got} in .docx")
        for lab in sorted(set(unresolved)):
            print(f"  *** unresolved label: {lab}")
        fails += len(short) + len(unresolved)

        with zipfile.ZipFile(docx_path) as z:
            xml = z.read("word/document.xml").decode("utf-8")
        cited = {k.strip() for m in CITE_RE.finditer(re.sub(r"(?<!\\)%.*", "", tex))
                 for k in m.group(1).split(",")}
        expected = {k: v for k, v in misc_expectations(BIB.read_text(encoding="utf-8")).items()
                    if k in cited}
        bad = []
        for key, want in sorted(expected.items()):
            entry = reference_entry(xml, key)
            if entry is None or norm(want) not in entry:
                bad.append((key, want, entry is None))
        print(f"  reference links/venues: {len(expected)} cited @misc entries, "
              f"{len(bad)} missing their URL or venue "
              f"{'OK' if not bad else '*** MISSING ***'}")
        for key, want, absent in bad:
            print(f"  *** {key}: {'no reference entry' if absent else 'lacks'} {want[:70]!r}")
        fails += len(bad)

        live = re.sub(r"(?<!\\)%.*", "", tex)
        # A figure's own label, not its first sub-panel's (Figure 3 is not "3a").
        floats_only = re.sub(r"\\begin\{subfigure\}.*?\\end\{subfigure\}", "", live, flags=re.S)
        want_floats = Counter(
            f"{'Figure' if m.group(1) == 'figure' else 'Table'} {labels.get(m.group(2), ('?',))[0]}"
            for m in FLOAT_LABEL.finditer(floats_only))
        want_headings = {labels.get(lab, ("?",))[0] for lab in HEADING_LABEL.findall(live)}
        want_titles = BMHEAD.findall(live) + ["References"]
        if "\\tableofcontents" in live:
            want_titles.append("Contents")
        problems = numbering_problems(paragraphs(xml), want_floats, want_headings, want_titles)
        print(f"  numbering: {sum(want_floats.values())} float captions, {len(want_headings)} "
              f"numbered headings, {len(want_titles)} titled headings expected; "
              f"{len(problems)} problem(s) {'OK' if not problems else '*** MISSING ***'}")
        for p in problems:
            print(f"  *** {p}")
        fails += len(problems)

        tex_rows, word_rows = latex_row_counts(live), word_row_counts(xml)
        broken_tables = [(n + 1, a, b) for n, (a, b) in enumerate(zip(tex_rows, word_rows)) if a != b]
        same_count = len(tex_rows) == len(word_rows)
        print(f"  tables: {len(tex_rows)} tabulars in .tex, {len(word_rows)} data tables in .docx, "
              f"{len(broken_tables)} with a different row count "
              f"{'OK' if same_count and not broken_tables else '*** BROKEN ***'}")
        if not same_count:
            print("  *** the number of tables differs")
        for n, a, b in broken_tables:
            print(f"  *** table #{n}: {a} rows in .tex, {b} in .docx")
        fails += len(broken_tables) + (0 if same_count else 1)

        affil = affiliation_problems(live, paragraphs(xml))
        print(f"  affiliations: {len(AFFIL.findall(live))} in .tex, each with city and country and "
              f"whole in Word: {'OK' if not affil else '*** ' + str(len(affil)) + ' PROBLEM(S) ***'}")
        for p in affil:
            print(f"  *** {p}")
        fails += len(affil)

    print("\n--- CALIBRATION ---")
    probe = docx_text(NPJ / "build/paper.docx")
    found_present = CONTROL_PRESENT in probe
    found_absent = CONTROL_ABSENT in probe
    print(f"  known-present string found : {found_present}")
    print(f"  known-absent string found  : {found_absent}")
    if not found_present or found_absent:
        print("  *** CALIBRATION FAILED -- the matching layer is broken, "
              "so no verdict above can be believed")
        fails += 1

    # The reference matcher must reject the exact defect it was written for (the
    # Word entry as pandoc printed it before the fix) and accept the repaired one.
    faq_url = misc_expectations(BIB.read_text(encoding="utf-8")).get("pulsefaq", "")
    broken = norm("Kitware, Inc. Pulse FAQ: Have you done UQ / SA? (2026).")
    repaired = norm(f"Kitware, Inc. Pulse FAQ: Have you done UQ / SA? {faq_url} (2026).")
    ref_ok = bool(faq_url) and norm(faq_url) not in broken and norm(faq_url) in repaired
    print(f"  reference matcher rejects the URL-less entry and accepts the repaired one: {ref_ok}")
    if not ref_ok:
        print("  *** CALIBRATION FAILED -- the reference-link check cannot be believed")
        fails += 1

    # The row counter must not count a \\ inside a cell's braces -- the exact
    # construct that broke the Word tables -- and must count every real row.
    snippet = ("\\begin{tabular}{lr}\nCell & \\shortstack[r]{hard-failure-\\\\free} \\\\\n"
               "A & 1 \\\\\nAll & \\shortstack[r]{663\\\\(51.8~\\%)} \\\\\n\\end{tabular}")
    rows_ok = latex_row_counts(snippet) == [3]
    print(f"  row counter ignores \\\\ inside a stacked cell and counts the 3 real rows: {rows_ok}")
    if not rows_ok:
        print("  *** CALIBRATION FAILED -- the table-structure check cannot be believed")
        fails += 1

    # The numbering check must flag the exact defect it was written for -- the
    # first caption of paper.docx as pandoc printed it before the fix, a heading
    # without its number -- and accept the repaired form.
    defect = [("ImageCaption", "Study design of the 1,280-run sweep."), ("Heading2", "Overview")]
    repaired = [("ImageCaption", "Figure 1. Study design of the 1,280-run sweep."),
                ("Heading2", "2.1 Overview")]
    want = Counter({"Figure 1": 1})
    num_ok = (bool(numbering_problems(defect, want, {"2.1"}, []))
              and not numbering_problems(repaired, want, {"2.1"}, []))
    print(f"  numbering check flags the unnumbered caption and heading and accepts the repaired ones: {num_ok}")
    if not num_ok:
        print("  *** CALIBRATION FAILED -- the numbering check cannot be believed")
        fails += 1

    # The affiliation check must flag the exact defect it was written for -- the
    # Word paragraph cut after "de Nancy," -- and a .tex affiliation without a
    # city, and accept the repaired forms.
    tex_ok = ("\\affil[6]{\\orgname{Fac}, \\orgaddress{\\city{Vand\\oe{}uvre-l\\`es-Nancy}, "
              "\\country{France}}}")
    tex_no_city = "\\affil[6]{\\orgname{Fac}, \\orgaddress{\\country{France}}}"
    cut = [("Heading1", "Author affiliations"), ("", "Fac, Faculté de Médecine de Nancy,")]
    whole = [("Heading1", "Author affiliations"), ("", "Fac, Vandœuvre-lès-Nancy, France")]
    affil_ok = (bool(affiliation_problems(tex_ok, cut))
                and bool(affiliation_problems(tex_no_city, whole))
                and not affiliation_problems(tex_ok, whole))
    print(f"  affiliation check flags the cut Word paragraph and the missing city, "
          f"and accepts the repaired form: {affil_ok}")
    if not affil_ok:
        print("  *** CALIBRATION FAILED -- the affiliation check cannot be believed")
        fails += 1

    print(f"\nRESULT: "
          f"{'ALL STRUCTURAL CHECKS PASSED' if fails == 0 else f'*** {fails} PROBLEM(S) ***'}")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
