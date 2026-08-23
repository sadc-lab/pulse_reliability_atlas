"""Generate the portal-paste block of submission_metadata.txt from paper.tex.

Why this exists
---------------
`preprint_npj/submission_metadata.txt` is the text pasted into the npj Digital
Medicine submission portal. Its header claimed the content was "extracted verbatim
from paper.tex"; on 2026-08-23 an audit found that not one sentence of the abstract
matched, that it ran to 155 words against npj's 150-word cap, that it omitted the
H1 headline result, and that five of the paper's thirteen keywords were missing.
Nothing re-derived it, so the drift was invisible.

`paper.tex` is the canonical source. This script regenerates the four derived
regions -- title, running title, abstract, keywords -- and never touches the
hand-maintained blocks below them (corresponding author, author list,
affiliations, ORCID iDs, CRediT contributions).

Usage
-----
    python scripts/sync_submission_metadata.py            # rewrite the block
    python scripts/sync_submission_metadata.py --check    # verify only, exit 1 on drift

Safety property
---------------
The transform FAILS on any LaTeX construct it does not recognise rather than
emitting it. A backslash reaching the submission portal is worse than a crash.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

REPO = pathlib.Path(__file__).resolve().parents[1]
PAPER = REPO / "preprint_npj" / "paper.tex"
META = REPO / "preprint_npj" / "submission_metadata.txt"

BEGIN = "BEGIN GENERATED BLOCK -- regenerate with scripts/sync_submission_metadata.py"
END = "END GENERATED BLOCK"
RULE = "-" * 78

# LaTeX -> portal plain Unicode. Order matters: longest and most specific first.
# The house style of the portal file, measured 2026-08-23: no subscripts, a
# comma thousands separator, a space before %, and U+2212 for a true minus.
SUBSTITUTIONS: list[tuple[str, str]] = [
    (r"\{,\}", ","),           # 1{,}280 -> 1,280
    (r"~\\%", " %"),           # 93~\% -> 93 %
    (r"\\%", " %"),
    (r"\$-(\d)\$", "\u2212\\1"),  # $-2$ -> minus-2 (U+2212, not a hyphen)
    (r"cmH\$_2\$O", "cmH2O"),
    (r"FiO\$_2\$", "FiO2"),
    (r"PaO\$_2\$", "PaO2"),
    (r"PaCO\$_2\$", "PaCO2"),
    (r"SpO\$_2\$", "SpO2"),
    (r"--", "\u2013"),          # patient--ventilator -> en dash
    (r"~", " "),
]

# Constructs that must never survive into the portal text.
RESIDUE = re.compile(r"[\\{}$]|\\\\")


def de_latex(s: str, what: str) -> str:
    for pattern, repl in SUBSTITUTIONS:
        s = re.sub(pattern, repl, s)
    s = " ".join(s.split())
    if RESIDUE.search(s):
        bad = RESIDUE.findall(s)
        raise SystemExit(
            f"FAIL: unhandled LaTeX in {what}: {sorted(set(bad))}\n"
            f"       add a rule to SUBSTITUTIONS rather than letting it reach the portal.\n"
            f"       text: {s[:200]}"
        )
    return s


def strip_comments(src: str) -> str:
    """Drop LaTeX comments, so a commented-out draft can never be harvested.

    paper.tex carries two commented `\\title[...]` drafts above the live one. The
    first version of this script took the first match and produced an abandoned
    title -- which would have been pasted into the submission portal. A `%` opens a
    comment unless escaped as `\\%`, and the abstract genuinely contains `\\%`.
    """
    out = []
    for line in src.split("\n"):
        cut = None
        i = 0
        while i < len(line):
            if line[i] == "\\":
                i += 2
                continue
            if line[i] == "%":
                cut = i
                break
            i += 1
        out.append(line if cut is None else line[:cut])
    return "\n".join(out)


def braced(src: str, macro: str) -> str:
    """Extract the balanced {...} argument of a macro, tolerating nesting."""
    i = src.index("\\" + macro)
    j = src.index("{", i)
    depth, k = 0, j
    while k < len(src):
        if src[k] == "{":
            depth += 1
        elif src[k] == "}":
            depth -= 1
            if depth == 0:
                return src[j + 1 : k]
        k += 1
    raise SystemExit(f"FAIL: unbalanced braces after \\{macro}")


# Tokens that must never start a line: a value and its unit stay together, so a
# reader pasting into the portal never meets "20.6" at one line end and "%" at the
# next.
GLUE_LEFT = {"%", "mmHg", "mL", "cmH2O", "bpm", "mmHg;", "%)", "%,"}


def wrap(text: str, width: int = 78) -> str:
    words = text.split()
    # Pre-join each value with a unit that must not be orphaned.
    joined: list[str] = []
    for w in words:
        if joined and w in GLUE_LEFT:
            joined[-1] = f"{joined[-1]} {w}"
        else:
            joined.append(w)
    out, line = [], ""
    for word in joined:
        if line and len(line) + 1 + len(word) > width:
            out.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    if line:
        out.append(line)
    return "\n".join(out)


def build() -> str:
    src = strip_comments(PAPER.read_text(encoding="utf-8"))

    m = re.search(r"\\title\[([^\]]*)\]", src)
    if not m:
        raise SystemExit("FAIL: no \\title[short] found in paper.tex")
    running = de_latex(m.group(1), "running title")
    title = de_latex(braced(src, "title"), "title")
    abstract = de_latex(braced(src, "abstract"), "abstract")
    kw_raw = de_latex(braced(src, "keywords"), "keywords")
    keywords = "; ".join(k.strip() for k in kw_raw.split(",") if k.strip())

    n_words = len(abstract.split())
    if n_words > 150:
        raise SystemExit(f"FAIL: abstract is {n_words} words, over npj's 150-word cap")

    return "\n".join(
        [
            RULE,
            "TITLE",
            RULE,
            title,
            "",
            f"(Running title / short title: {running})",
            "",
            RULE,
            f"ABSTRACT  ({n_words} words, npj cap 150)",
            RULE,
            wrap(abstract),
            "",
            RULE,
            f"KEYWORDS  ({keywords.count(';') + 1})",
            RULE,
            wrap(keywords),
        ]
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify only; exit 1 on drift")
    ap.add_argument("--print", action="store_true", dest="show",
                    help="print the generated block and write nothing")
    args = ap.parse_args()

    generated = build()

    if args.show:
        print(generated)
        return 0
    current = META.read_text(encoding="utf-8")

    if BEGIN not in current or END not in current:
        print("  submission_metadata.txt carries no generated-block markers yet.")
        if args.check:
            print("  FAIL: run without --check once to install them.")
            return 1
        # The old header asserted the block was "extracted verbatim from
        # paper.tex" and that the file was an uncommitted draft. Neither was
        # true: nothing re-derived the block, and the file is git-tracked. It is
        # replaced rather than preserved.
        header = (
            "=" * 78 + "\n"
            "npj Digital Medicine -- submission metadata\n"
            "\n"
            "Title, running title, abstract and keywords are GENERATED from\n"
            "preprint_npj/paper.tex, which is their only source of truth. Do not edit\n"
            "them here: run scripts/sync_submission_metadata.py, or --check to verify.\n"
            "Everything below the generated block is hand-maintained.\n"
            + "=" * 78 + "\n\n"
        )
        idx = current.index("CORRESPONDING AUTHOR") - len(RULE) - 1
        tail = current[idx:]
        META.write_text(
            header + f"*** {BEGIN} ***\n\n" + generated + f"\n\n*** {END} ***\n\n" + tail,
            encoding="utf-8",
        )
        print("  header replaced, markers installed, block generated.")
        return 0

    start = current.index(f"*** {BEGIN} ***") + len(f"*** {BEGIN} ***") + 2
    stop = current.index(f"*** {END} ***")
    present = current[start:stop].strip("\n")

    if present == generated:
        print(f"  PASS: portal block matches paper.tex ({len(generated.splitlines())} lines).")
        return 0

    if args.check:
        print("  FAIL: submission_metadata.txt has drifted from paper.tex.")
        import difflib

        for line in list(difflib.unified_diff(
            present.splitlines(), generated.splitlines(),
            "submission_metadata.txt", "regenerated from paper.tex", lineterm="", n=1,
        ))[:40]:
            print("   ", line)
        return 1

    META.write_text(current[:start] + generated + "\n\n" + current[stop:], encoding="utf-8")
    print("  block regenerated from paper.tex.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
