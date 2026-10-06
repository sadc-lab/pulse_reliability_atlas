#!/usr/bin/env python3
"""Gate the supplement's assertions ABOUT the main manuscript.

Why this exists
---------------
`supplement.tex` repeatedly tells the reader what the main manuscript says:
"Section 2.5 of the main manuscript reports that ...", "Table 3 of the main
manuscript reports per-cell counts ...". Those sentences are claims about
another document, and nothing in the repository measured them.

On 2026-09-04 an audit found one that had gone false. The September
condensation pass deleted the cross-sex Spearman result from the paper's
Results; `supplement.tex` S6 kept opening with "The Discussion of the main
manuscript reports that the cross-sex Spearman rank correlation ... is
computable only for S2 and S3". The paper no longer reported it anywhere.

Every existing gate stayed green throughout, and structurally had to:

  * `check_render.py`'s `crossdoc` check reads `\\mainref{label}{number}` and
    verifies only that the NUMBER matches the paper's section number. A
    back-reference can point at the right section and still describe it wrongly.
  * `audit_claims.py` verifies numeric literals against artefacts. A sentence
    with no number in it is invisible to it.
  * The 2026-09-03 semantic cross-reference sweep walked the pointers that
    exist in `paper.tex`. A pointer the paper no longer carries cannot appear
    in that population at all.

So this guard runs the other way: it enumerates the supplement's assertions
about the paper, and requires each one to name a probe that must still be
findable in `paper.tex`.

How it works
------------
Semantic agreement cannot be checked mechanically, so this does what
`check_citations.py` does with the bibliography: it converts the semantic
question into a registration question.

  A. Every back-reference in `supplement.tex` is registered in
     `audit/backref_manifest.txt`, keyed by line content.
  B. Each registered entry carries a PROBE: a literal string that must be
     present in `paper.tex` for the assertion to still hold. An entry that
     only points at a section, without asserting content, is registered
     POINTER and carries no probe.
  C. A back-reference that appears in the supplement and is not registered
     fails the gate, so a new one cannot ship unreviewed.

The probe is chosen by a human when the entry is registered. The guard does
not judge the wording; it detects the moment the paper stops carrying what
the supplement says it carries.

Run:  python scripts/check_backrefs.py
      python scripts/check_backrefs.py --list   (print the current population)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUPPLEMENT = ROOT / "preprint_npj" / "supplement.tex"
PAPER = ROOT / "preprint_npj" / "paper.tex"
MANIFEST = ROOT / "audit" / "backref_manifest.txt"

# A back-reference is a mention of the main document followed, within the same
# sentence, by a verb that attributes content to it. The window is capped so a
# later unrelated verb in a long paragraph does not pull a pointer in.
BACKREF_RE = re.compile(
    r"main\s+(?:manuscript|paper)\b[^.]{0,80}?"
    # defines / mentions / summarises added 2026-10-06: the M. Sauthier review
    # round reworded three supplement back-references with these verbs, which
    # silently took them out of the gate (a missed match is not a failure).
    r"\b(?:reports?|states?|records?|says?|gives?|describes?|notes?|shows?|carries|quotes?|keeps?"
    r"|defines?|mentions?|summari[sz]es?)\b"
    r"[^.]{0,70}",
    re.IGNORECASE,
)

# Some sentences mention the main document only to point at a section. They are
# registered POINTER in the manifest and assert nothing to probe.
POINTER_TOKEN = "POINTER"


def normalise(text: str) -> str:
    """Collapse whitespace so a hard-wrapped probe still matches."""
    return re.sub(r"\s+", " ", text).strip()


def find_backrefs(supplement_text: str) -> list[tuple[int, str]]:
    """Return (line number, matched clause) for every back-reference."""
    found = []
    for lineno, line in enumerate(supplement_text.splitlines(), start=1):
        for match in BACKREF_RE.finditer(line):
            found.append((lineno, normalise(match.group(0))))
    return found


def load_manifest() -> dict[str, str]:
    """Return {clause key: probe}. Blank lines and # comments are ignored."""
    entries: dict[str, str] = {}
    if not MANIFEST.exists():
        return entries
    for raw in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, _, probe = line.partition("\t")
        entries[normalise(key)] = probe.strip()
    return entries


def self_test() -> list[str]:
    """Calibrate on the defect that motivated the guard, plus controls.

    A guard that has never been shown to fire is an assumption. The first
    witness below is the exact sentence that went false in September 2026.
    """
    failures = []

    witness = (
        "The Discussion of the main manuscript reports that the cross-sex "
        "Spearman rank correlation is computable only for S2 and S3"
    )
    if not BACKREF_RE.search(witness):
        failures.append("self-test: the S6-rho witness was NOT matched")

    # The three verbs added on 2026-10-06, each on the exact clause that escaped.
    for verb_witness in (
        "Table 1 of the main manuscript defines the three terms needed to read its figures",
        "The Discussion of the main manuscript mentions engine-side suggestions",
        "The Discussion of the main manuscript summarises the complementarity",
    ):
        if not BACKREF_RE.search(verb_witness):
            failures.append(f"self-test: verb witness NOT matched: {verb_witness!r}")

    # A \mainref that merely points at a section asserts nothing about content.
    # It is still matched (so it must be registered), which is deliberate: a
    # human decides POINTER, the regex does not guess.
    pointer = (
        "flagged rather than discarded (Section 4.4 of the main manuscript), "
        "which keeps the assumption auditable"
    )
    if not BACKREF_RE.search(pointer):
        failures.append("self-test: the pointer form was NOT matched")

    # Negative control: the supplement talking about itself must not match.
    negative = "This supplement section provides the full rho table with bootstrap intervals."
    if BACKREF_RE.search(negative):
        failures.append("self-test: a supplement-internal sentence WAS matched")

    # Negative control: naming the paper without attributing content to it.
    negative2 = "The main manuscript and this supplement share one bibliography."
    if BACKREF_RE.search(negative2):
        failures.append("self-test: a non-attributing mention WAS matched")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--list",
        action="store_true",
        help="print every back-reference found, with its line number, and exit",
    )
    args = parser.parse_args()

    supplement_text = SUPPLEMENT.read_text(encoding="utf-8")
    paper_text = normalise(PAPER.read_text(encoding="utf-8"))

    backrefs = find_backrefs(supplement_text)

    if args.list:
        print(f"## Back-references in {SUPPLEMENT.relative_to(ROOT)}\n")
        for lineno, clause in backrefs:
            print(f"  {lineno:>5}  {clause}")
        print(f"\n  {len(backrefs)} found.")
        return 0

    print("## Supplement back-references to the main manuscript\n")

    problems = []

    st_failures = self_test()
    if st_failures:
        for failure in st_failures:
            print(f"  FAIL  {failure}")
        problems.extend(st_failures)
    else:
        print("  ok    pattern self-test (2 attributing forms matched, 2 controls spared)")

    manifest = load_manifest()
    if not manifest:
        print(f"  FAIL  no manifest at {MANIFEST.relative_to(ROOT)}")
        return 1

    unregistered = []
    broken = []
    pointers = 0
    probed = 0

    for lineno, clause in backrefs:
        if clause not in manifest:
            unregistered.append((lineno, clause))
            continue
        probe = manifest[clause]
        if probe == POINTER_TOKEN:
            pointers += 1
            continue
        if normalise(probe) not in paper_text:
            broken.append((lineno, clause, probe))
        else:
            probed += 1

    stale = [key for key in manifest if key not in {c for _, c in backrefs}]

    if unregistered:
        print(f"\n  FAIL  {len(unregistered)} back-reference(s) not in the manifest:")
        for lineno, clause in unregistered:
            print(f"        supplement.tex:{lineno}  {clause}")
        print("\n        Register each with a probe -- a literal string that must")
        print("        stay present in paper.tex -- or with POINTER if it asserts")
        print(f"        nothing. File: {MANIFEST.relative_to(ROOT)}")
        problems.extend(unregistered)

    if broken:
        print(f"\n  FAIL  {len(broken)} back-reference(s) whose probe is GONE from paper.tex:")
        for lineno, clause, probe in broken:
            print(f"        supplement.tex:{lineno}  {clause}")
            print(f"          probe not found: {probe}")
        print("\n        The supplement says the paper reports something the paper")
        print("        no longer reports. Restore it in paper.tex, or reword the")
        print("        supplement and update the probe.")
        problems.extend(broken)

    if stale:
        print(f"\n  FAIL  {len(stale)} manifest entr(y/ies) no longer present in the supplement:")
        for key in stale:
            print(f"        {key}")
        print("\n        Remove them, so the manifest keeps measuring the real population.")
        problems.extend(stale)

    if problems:
        print(f"\n  BACK-REFERENCE GATE FAILED ({len(problems)} problem(s)).")
        return 1

    print(f"\n  {len(backrefs)} back-references: {probed} probed against paper.tex, "
          f"{pointers} registered as pointers.")
    print("  BACK-REFERENCE GATE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
