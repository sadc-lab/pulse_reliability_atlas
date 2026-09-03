"""Gate the citation set of the npj submission against a recorded manifest.

Why this exists
---------------
During the 2026-08/09 synthesis pass, eleven bibliography keys left
`preprint_npj/paper.tex` and `supplement.tex` unnoticed. Three took their sentence
with them, which is correct behaviour; six left a claim standing with no source,
one of them a clinical over-claim that a reference this manuscript itself cites
contradicts. Every gate in the repository stayed green throughout, because nothing
measured the citation set.

The invariant existed, in prose, on a handoff card: "a citation is never deleted,
it travels with the sentence it supports". Prose does not run. This does.

A second failure is encoded here too. The extractor used during that pass was
`\\cite[tp]*{`, which silently drops `\\cite[Ch.~1]{key}`; two keys were invisible
to the very audit that found the problem, and the reported totals were wrong by
two. The self-test below exercises the locator form on a literal witness, so that
blind spot cannot come back unnoticed.

Invariants
----------
A. Every cited key resolves to an entry in `preprint_npj/paper.bib`.
B. Every entry in `paper.bib` is either cited somewhere in the submission, or
   listed under [RETIRED] in the manifest with a reason. Dropping the last
   citation of a key therefore costs one line of writing -- which is the point.
C. Every cited key is listed under [ACTIVE] in the manifest, so a citation added
   without recording it is caught as well.

Scope
-----
The npj submission only: `paper.tex`, `supplement.tex`, `paper.bib`. The
technical monograph (`preprint/manuscript.md`) uses `[@key]` marks against a
hand-maintained reference list and is NOT covered here; do not read a green run
as a statement about it.

Usage
-----
    python scripts/check_citations.py             # verify, exit 1 on any violation
    python scripts/check_citations.py --update    # rewrite the manifest from the corpus

`--update` never invents a retirement reason: a key that has left the corpus is
written under [RETIRED] with the placeholder REASON-NOT-RECORDED, which keeps
failing the next verify run until a human replaces it with the actual reason.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "preprint_npj" / "paper.tex"
SUPPLEMENT = ROOT / "preprint_npj" / "supplement.tex"
BIB = ROOT / "preprint_npj" / "paper.bib"
MANIFEST = ROOT / "audit" / "citation_manifest.txt"

PLACEHOLDER = "REASON-NOT-RECORDED"

# natbib forms, with up to two optional arguments: \cite{a,b}, \cite[Ch.~1]{a},
# \citep[see][p.~5]{a}, \citet*{a}. The leading backslash is what separates a
# citation from the English word "cited"; the self-test asserts both directions.
CITE_RE = re.compile(r"\\cite[tp]?\*?(?:\[[^\]]*\]){0,2}\{([^}]*)\}")
BIB_KEY_RE = re.compile(r"^@[A-Za-z]+\{([^,]+),", re.MULTILINE)

_SELFTEST_TEXT = (
    r"\cite{alpha} \cite[Ch.~1]{beta} \citep[see][p.~5]{gamma} "
    r"\citet*{delta} \cite{epsilon, zeta} and the word cited{notakey}"
)
_SELFTEST_EXPECTED = {"alpha", "beta", "gamma", "delta", "epsilon", "zeta"}


def keys_in(text: str) -> set[str]:
    """Every bibliography key cited in `text`, one entry per key."""
    found: set[str] = set()
    for group in CITE_RE.findall(text):
        for key in group.split(","):
            key = key.strip()
            if key:
                found.add(key)
    return found


def self_test() -> list[str]:
    """Calibrate the extractor before trusting it. Returns a list of failures."""
    got = keys_in(_SELFTEST_TEXT)
    problems = []
    missing = _SELFTEST_EXPECTED - got
    if missing:
        problems.append(
            f"extractor missed {sorted(missing)} -- the locator form "
            r"(\cite[Ch.~1]{key}) is exactly the blind spot this gate exists to prevent"
        )
    extra = got - _SELFTEST_EXPECTED
    if extra:
        problems.append(f"extractor matched non-citations {sorted(extra)}")
    return problems


def read_manifest() -> tuple[dict[str, str], dict[str, str]]:
    """Parse the manifest into ({active key: note}, {retired key: reason})."""
    active: dict[str, str] = {}
    retired: dict[str, str] = {}
    if not MANIFEST.exists():
        return active, retired
    section = None
    for raw in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.upper() == "[ACTIVE]":
            section = active
            continue
        if line.upper() == "[RETIRED]":
            section = retired
            continue
        if section is None:
            continue
        key, _, note = line.partition(" ")
        section[key.strip()] = note.strip()
    return active, retired


def write_manifest(cited: dict[str, set[str]], bib_keys: set[str],
                   retired: dict[str, str]) -> None:
    """Rewrite the manifest from the corpus, preserving recorded retirement reasons."""
    all_cited = set().union(*cited.values()) if cited else set()
    lines = [
        "# Citation manifest for the npj submission -- gated by scripts/check_citations.py",
        "#",
        "# [ACTIVE]  <key>  <documents that cite it>",
        "# [RETIRED] <key>  <why it no longer appears -- a real reason, never a placeholder>",
        "#",
        "# Regenerate with:  python scripts/check_citations.py --update",
        "# A key that leaves the corpus lands in [RETIRED] with a placeholder that keeps",
        "# failing the gate until the reason is written by hand.",
        "",
        "[ACTIVE]",
    ]
    for key in sorted(all_cited):
        where = [doc for doc, keys in cited.items() if key in keys]
        lines.append(f"{key}  {'+'.join(sorted(where))}")
    lines += ["", "[RETIRED]"]
    for key in sorted(bib_keys - all_cited):
        lines.append(f"{key}  {retired.get(key) or PLACEHOLDER}")
    lines.append("")
    MANIFEST.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--update", action="store_true",
                        help="rewrite the manifest from the current corpus")
    args = parser.parse_args()

    print("## Citation gate (npj submission)\n")

    problems = self_test()
    if problems:
        print("  FAIL  extractor self-test")
        for problem in problems:
            print(f"        {problem}")
        return 1
    print(f"  ok    extractor self-test ({len(_SELFTEST_EXPECTED)} forms, "
          "including the locator form and one negative control)")

    for path in (PAPER, SUPPLEMENT, BIB):
        if not path.exists():
            print(f"  FAIL  missing file: {path.relative_to(ROOT)}")
            return 1

    cited = {
        "paper": keys_in(PAPER.read_text(encoding="utf-8")),
        "supplement": keys_in(SUPPLEMENT.read_text(encoding="utf-8")),
    }
    bib_keys = set(BIB_KEY_RE.findall(BIB.read_text(encoding="utf-8")))
    union = cited["paper"] | cited["supplement"]
    print(f"  ok    {len(cited['paper'])} keys in paper.tex, "
          f"{len(cited['supplement'])} in supplement.tex, {len(union)} distinct, "
          f"{len(bib_keys)} entries in paper.bib")

    if args.update:
        _, retired = read_manifest()
        retired = {k: v for k, v in retired.items() if v and v != PLACEHOLDER}
        write_manifest(cited, bib_keys, retired)
        print(f"\n  manifest rewritten: {MANIFEST.relative_to(ROOT)}")
        placeholders = sorted(bib_keys - union - set(retired))
        if placeholders:
            print("  Retirement reasons still to write by hand, one line each:")
            for key in placeholders:
                print(f"    {key}")
        return 0

    active, retired = read_manifest()
    if not active and not retired:
        print(f"\n  FAIL  no manifest at {MANIFEST.relative_to(ROOT)}")
        print("        Create it once:  python scripts/check_citations.py --update")
        return 1

    failures = 0

    dangling = sorted(union - bib_keys)
    if dangling:
        failures += len(dangling)
        print("\n  FAIL  cited but absent from paper.bib (invariant A):")
        for key in dangling:
            print(f"        {key}")

    unrecorded = sorted(union - set(active))
    if unrecorded:
        failures += len(unrecorded)
        print("\n  FAIL  cited but not in the manifest's [ACTIVE] block (invariant C):")
        for key in unrecorded:
            print(f"        {key}")
        print("        A citation was added without recording it. Re-run with --update.")

    orphans = sorted(bib_keys - union)
    unexplained = [k for k in orphans if not retired.get(k) or retired[k] == PLACEHOLDER]
    if unexplained:
        failures += len(unexplained)
        print("\n  FAIL  entry in paper.bib cited nowhere, with no reason recorded "
              "(invariant B):")
        for key in unexplained:
            print(f"        {key}")
        print("        A key stops being cited for one of two reasons: its sentence left")
        print("        too (fine), or the claim is standing without support (a defect).")
        print("        Decide which, then write the reason under [RETIRED] in")
        print(f"        {MANIFEST.relative_to(ROOT)}.")

    explained = [k for k in orphans if k not in unexplained]
    if explained:
        print(f"\n  ok    {len(explained)} retired entries, each with a recorded reason:")
        for key in explained:
            print(f"        {key}  {retired[key]}")

    if failures:
        print(f"\n  {failures} violation(s). CITATION GATE FAILED.")
        return 1

    print(f"\n  {len(union)} cited keys, all resolved and all recorded. "
          "CITATION GATE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
