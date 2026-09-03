"""Forbid hard-coded ledger-anchor and crosswalk-row counts in live files.

Why this exists
---------------
Three live files advertised "the 247-anchor ledger" and "85-row crosswalk" long
after the ledger reached 382 anchors and the crosswalk 94 rows. A fourth, in
`scripts/provenance_check.py`, had gone unnoticed by the register that tracked
the other three. Nothing re-measured any of them, so all four rotted quietly and
a reader was told a number that had been wrong for months.

`scripts/audit_claims.py` already refuses to do this to itself. Its own comment,
above the total it prints, reads: "Computed dynamically so the ratio cannot go
stale if anchors are added or removed later. Deliberately no illustrative value
of N here." This guard extends that rule to every file a reader might believe.

The fix these literals needed was not a corrected number -- that only resets the
same clock -- but no number at all. "The claims-ledger audit guarantees ..." is
true forever; "the 247-anchor claims-ledger audit ..." is true until the next
anchor lands.

What it accepts
---------------
Counts that are not ledger sizes: a fixture described as a "13-row CSV", the
sweep's own "1,280-row table of input combinations" (including the LaTeX
thousands separator, `1{,}280-row`). The pattern requires the digits to start on
a boundary that is not itself part of a larger number.

Dated records under audit/, audits/ and experiments_log/ are exempt: a register
that says "247 anchors on 2026-07-14" is correct as history and must not be
rewritten. tests/ and attic/ are exempt too.

Known limitation, written down rather than discovered later:
`preprint_npj/dispatch_log.md` is a dated record of the same kind, but it lives
in a scanned directory. Its 2026-08-25 entry states the gate state at dispatch
as "382 anchors, 94 crosswalk rows" -- prose with a space, which this pattern
does not match, so it passes today. A future entry that wrote "382-anchor"
would be blocked for stating a historical fact correctly. If that happens, the
fix is to exempt that one file by path, not to reword the history.

Usage
-----
    python scripts/check_stale_counts.py        # exit 1 if any live file carries one
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Directories whose contents are dated records or fixtures, not live prose.
EXEMPT_PREFIXES = ("audit/", "audits/", "experiments_log/", "attic/", "tests/")

# A ledger-size literal: digits immediately followed by -anchor or -row, where
# the digits are not the tail of a longer number. "1{,}280-row" and "1,280-row"
# are therefore not matched; "247-anchor" and "85-row" are.
COUNT_RE = re.compile(r"(?<![\d,}])(\d+)-(anchor|row)\b")

# This file names the very literals it forbids, in the docstring above.
SELF = "scripts/check_stale_counts.py"


def tracked_files() -> list[str]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                         text=True, check=True).stdout
    return [p for p in out.splitlines() if p and not p.startswith(EXEMPT_PREFIXES)
            and p != SELF]


def self_test() -> list[str]:
    """Calibrate the pattern on the exact strings that motivated it."""
    must_match = ["the 247-anchor ledger", "85-row crosswalk", "the 289-anchor layer"]
    must_not = ['the "1{,}280-row table of input combinations"', "a 1,280-row table"]
    problems = []
    for s in must_match:
        if not COUNT_RE.search(s):
            problems.append(f"pattern missed a real stale literal: {s!r}")
    for s in must_not:
        if COUNT_RE.search(s):
            problems.append(f"pattern flagged a legitimate count: {s!r}")
    return problems


def main() -> int:
    print("## Ledger-count literals in live files\n")

    problems = self_test()
    if problems:
        print("  FAIL  pattern self-test")
        for p in problems:
            print(f"        {p}")
        return 1
    print("  ok    pattern self-test (3 stale forms matched, 2 legitimate counts spared)")

    hits: list[tuple[str, int, str]] = []
    for rel in tracked_files():
        path = ROOT / rel
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeError):
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for m in COUNT_RE.finditer(line):
                hits.append((rel, lineno, m.group(0)))

    if hits:
        print(f"\n  FAIL  {len(hits)} hard-coded ledger count(s) in live files:")
        for rel, lineno, lit in hits:
            print(f"        {rel}:{lineno}  {lit}")
        print("\n  These go stale silently. The ledger computes its own total at run")
        print("  time and deliberately hard-codes no N; live prose should not either.")
        print("  Drop the number ('the claims-ledger audit'), or point at the audit")
        print("  output. Dated records under audit/, audits/ and experiments_log/ are")
        print("  exempt and must keep their historical figures.")
        return 1

    print(f"\n  {len(tracked_files())} tracked live files, no hard-coded ledger count. PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
