#!/usr/bin/env python3
"""Read-only full-text probe for a local PDF.

Why this exists
---------------
Verifying a citation against a book means searching its whole text, which the
native file reader cannot do (it is capped at a few pages per call). Running an
ad-hoc interpreter for that would mean allowlisting arbitrary code execution,
which `CLAUDE.md` forbids. This script is the least-privilege alternative: a
fixed, versioned, auditable tool that can only read a PDF and print matches.

Guarantees, by construction
---------------------------
* It never writes a file: no `open(..., 'w')`, no `os.remove`, no `Path.write_*`.
* It never touches the network: no socket, requests, urllib or subprocess import.
* Its only side effect is printing to stdout.

Anyone extending this file must preserve those three properties, because a
permission rule pins this exact path and grants it silent execution.

Usage
-----
    uv run --with pymupdf python scripts/pdf_probe.py <pdf> --pattern <regex>
    uv run --with pymupdf python scripts/pdf_probe.py <pdf> --toc
    uv run --with pymupdf python scripts/pdf_probe.py <pdf> --identity

    --pattern REGEX   case-insensitive regex to search across every page
    --context N       characters of context either side of a hit (default 180)
    --limit N         stop after N hits (default 20; 0 means no limit)
    --pages A-B       restrict the search to a page range (1-indexed, inclusive)
    --identity        print page count, metadata, and the first pages that look
                      like title / copyright pages -- use this FIRST, because a
                      filename is not evidence of which edition a file is
    --toc             print the embedded outline, or the first page that looks
                      like a table of contents

Exit codes: 0 = at least one hit (or an informational mode ran), 1 = no hit,
2 = bad input.
"""

from __future__ import annotations

import argparse
import io
import re
import sys

# stdout is forced to UTF-8: medical and physiology PDFs are full of glyphs
# (ligatures, Greek letters, en dashes) that crash the Windows cp1252 default.
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

try:
    import fitz  # PyMuPDF
except ImportError:  # pragma: no cover
    sys.exit("pymupdf is required: uv run --with pymupdf python scripts/pdf_probe.py ...")


def collapse(text: str) -> str:
    """Flatten whitespace and undo end-of-line hyphenation.

    PDF extraction breaks words across lines ("diffu-\\nsion"), which silently
    defeats a naive substring search. Undoing it is what makes a negative
    result trustworthy.
    """
    return re.sub(r"\s+", " ", re.sub(r"-\n(?=[a-z])", "", text)).strip()


def main() -> int:
    ap = argparse.ArgumentParser(description="Search a local PDF. Read-only.")
    ap.add_argument("pdf")
    ap.add_argument("--pattern")
    ap.add_argument("--context", type=int, default=180)
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--pages")
    ap.add_argument("--identity", action="store_true")
    ap.add_argument("--toc", action="store_true")
    args = ap.parse_args()

    try:
        doc = fitz.open(args.pdf)
    except Exception as exc:
        print("cannot open: %s" % exc)
        return 2

    first, last = 1, doc.page_count
    if args.pages:
        m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", args.pages.strip())
        if not m:
            print("--pages expects the form A-B")
            return 2
        first, last = int(m.group(1)), min(int(m.group(2)), doc.page_count)

    if args.identity:
        print("pages: %d" % doc.page_count)
        print("metadata: %s" % {k: v for k, v in doc.metadata.items() if v})
        for i in range(min(14, doc.page_count)):
            t = doc[i].get_text().strip()
            if re.search(r"edition|copyright|©|ISBN|published", t, re.I):
                print("\n--- pdf page %d ---\n%s" % (i + 1, t[:1200]))
        return 0

    if args.toc:
        outline = doc.get_toc()
        if outline:
            for level, title, page in outline[:120]:
                print("%s%s  ... p.%d" % ("  " * (level - 1), title, page))
            return 0
        print("(no embedded outline; scanning for a contents page)")
        for i in range(min(24, doc.page_count)):
            t = doc[i].get_text()
            if re.search(r"^\s*contents\s*$", t, re.I | re.M) or re.search(r"Chapter\s+1\b", t):
                print("--- pdf page %d ---\n%s" % (i + 1, t.strip()[:1600]))
                return 0
        print("no contents page found")
        return 1

    if not args.pattern:
        print("nothing to do: pass --pattern, --identity or --toc")
        return 2

    try:
        rx = re.compile(args.pattern, re.I)
    except re.error as exc:
        print("bad regex: %s" % exc)
        return 2

    hits = 0
    for i in range(first - 1, last):
        flat = collapse(doc[i].get_text())
        for m in rx.finditer(flat):
            lo = max(0, m.start() - args.context)
            print("p.%-5d %s" % (i + 1, flat[lo:m.end() + args.context]))
            hits += 1
            if args.limit and hits >= args.limit:
                print("\n-- stopped at --limit %d --" % args.limit)
                return 0

    if hits == 0:
        # A negative is a real finding in a citation audit, so say so loudly.
        print("*** NO MATCH for /%s/ in pages %d-%d of %d ***"
              % (args.pattern, first, last, doc.page_count))
        return 1

    print("\n-- %d hit(s) --" % hits)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
