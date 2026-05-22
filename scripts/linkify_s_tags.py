"""One-shot: rewrite bare S0NN and existing [S0NN](path) refs in
preprint/manuscript.md to internal anchor links pointing at Appendix A.

Skips:
  - The two S0NN tables themselves (section 1.4 and Appendix A).
  - Fenced code blocks (between ``` lines).
  - Inline code spans (between backticks).
  - The link-target (URL) portion of existing [text](url) markdown links.

Run manually after editing the manuscript; the rewrite is idempotent.
"""

from __future__ import annotations

import re
from pathlib import Path


MANUSCRIPT = Path(__file__).resolve().parent.parent / "preprint" / "manuscript.md"


S0NN_RE = re.compile(r"\bS0[0-9]{2}\b")
EXISTING_LINK_RE = re.compile(r"(\[S0([0-9]{2})\])\([^)]*\)")
ALL_MD_LINK_RE = re.compile(r"\[[^\]]*\]\([^)]*\)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")


def find_table_ranges(lines: list[str]) -> list[tuple[int, int]]:
    """Return inclusive line-index ranges (0-based) of the two S0NN tables.

    Table 1: section 1.4 (header "### 1.4 Experiment log nomenclature ...").
    Table 2: Appendix A ("## Appendix A ...").
    Each table is recognised by the leading pipe-table header within ~4 lines
    of the section heading and ends at the first blank line after the data
    rows."""
    ranges: list[tuple[int, int]] = []
    section_starts = []
    for i, line in enumerate(lines):
        if line.startswith("### 1.4 ") or line.startswith("## Appendix A"):
            section_starts.append(i)
    for start in section_starts:
        # Find first pipe-table header anywhere up to next section/EOF.
        # Section 1.4 has ~18 lines of intro prose before the table starts,
        # so a narrow look-ahead window misses it.
        section_end = len(lines)
        for j in range(start + 1, len(lines)):
            if lines[j].startswith("## ") or lines[j].startswith("### "):
                section_end = j
                break
        table_start = None
        for j in range(start, section_end):
            if lines[j].lstrip().startswith("| ID") or lines[j].lstrip().startswith("| Tag"):
                table_start = j
                break
        if table_start is None:
            continue
        table_end = table_start
        for j in range(table_start, len(lines)):
            if lines[j].strip() == "":
                table_end = j - 1
                break
            table_end = j
        ranges.append((table_start, table_end))
    return ranges


def linkify_line(line: str) -> str:
    """Apply S0NN linkification to a single line, respecting links and code."""
    # Pass 1: redirect existing [S0NN](anything) -> [S0NN](#s0nn).
    line = EXISTING_LINK_RE.sub(lambda m: f"{m.group(1)}(#s0{m.group(2)})", line)

    # Pass 2: stash every remaining markdown link (text + url) AND every
    # inline code span. After this, no markdown link or code span content
    # is exposed to the S0NN regex.
    placeholders: dict[str, str] = {}

    def stash(match: re.Match[str]) -> str:
        key = f"\x00P{len(placeholders)}\x00"
        placeholders[key] = match.group(0)
        return key

    line = ALL_MD_LINK_RE.sub(stash, line)
    line = INLINE_CODE_RE.sub(stash, line)

    # Pass 3: linkify any remaining bare S0NN occurrences.
    line = S0NN_RE.sub(lambda m: f"[{m.group(0)}](#{m.group(0).lower()})", line)

    # Restore the stashed pieces.
    for key, val in placeholders.items():
        line = line.replace(key, val)

    return line


def main() -> None:
    src = MANUSCRIPT.read_text(encoding="utf-8")
    lines = src.splitlines(keepends=True)

    protected = find_table_ranges(lines)
    print(f"Protected table ranges (0-based, inclusive): {protected}")

    in_fence = False
    out: list[str] = []
    rewrites = 0
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        if any(start <= i <= end for start, end in protected):
            out.append(line)
            continue
        new_line = linkify_line(line)
        if new_line != line:
            rewrites += 1
        out.append(new_line)

    MANUSCRIPT.write_text("".join(out), encoding="utf-8")
    print(f"Rewrote {rewrites} lines.")


if __name__ == "__main__":
    main()
