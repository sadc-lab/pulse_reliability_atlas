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

from tex_to_docx import parse_aux_labels

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

    print(f"\nRESULT: "
          f"{'ALL STRUCTURAL CHECKS PASSED' if fails == 0 else f'*** {fails} PROBLEM(S) ***'}")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
