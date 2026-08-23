"""Verify the eight present-tense public-availability statements, by content.

Why this exists
---------------
Nine statements in the submission package assert, in the present tense, that the
code and data are already publicly available. Each is false while the GitHub
repository is private, so the release order is fixed: public repository first,
submission second.

The prose gate this replaces said EIGHT. The ninth -- paper.tex's "The pipeline is
preregistered, reproducible from a single Docker image with a fixed seed, and
released open-source under Apache-2.0" -- sits in the Introduction, not in a
Code/Data availability section, and was missed by an enumeration that searched
where such sentences are expected to live.

Deliberately excluded, recorded so it is not re-raised: paper.tex's "the deposited
data and the authors' own monograph content are released under the Creative
Commons Attribution 4.0 licence". Its own paragraph says the data "will be
deposited at Zenodo", so it declares the licence of a deposit that has not
happened. That is a licensing statement, not a claim of present availability.

That gate was written as prose listing eight FILE:LINE positions. By 2026-08-23
six of the eight numbers were wrong -- paper.tex 409/430/434 had become 454/475/479,
a +45 shift, and supplement.tex 809/939 had become 811/943. The claims had not
moved; the addressing had aged. A gate that opens the wrong line is worse than no
gate, because it reports success.

Design
------
Loci are identified by **content**, never by position. Two cases only:

* a unique anchor must occur **exactly once** in its file;
* a deliberately repeated anchor declares its expected count, and every
  occurrence is printed before the row passes.

There is no "first match wins". If a unique anchor resolves 0 or 2 times the row
FAILS, because an instrument that silently picks one of two candidates is
choosing the claim it audits.

The anchors are the tensed phrases themselves -- "are released", "already openly
available", "is released". Rewriting a statement into the future tense therefore
breaks its anchor and fails the gate, which is the intended behaviour: the gate's
premise has changed and a human should look.

What this does NOT verify
-------------------------
That the surrounding sentence still *means* what the proposition column says. A
count is not a semantics check. The propositions are printed so a human reads them
at submission time; the script guarantees only that each anchor is present, in its
declared number, in its declared file.

Usage
-----
    python scripts/check_publication_gate.py                  # anchors only
    python scripts/check_publication_gate.py --verify-public  # + repository status
"""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

REPO = pathlib.Path(__file__).resolve().parents[1]
SLUG = "santinon/pulse_reliability_atlas"
CONTROL = "torvalds/linux"

# file, anchor, expected occurrences, the proposition the anchor stands for
CLAIMS: list[tuple[str, str, int, str]] = [
    # Found 2026-08-23 while measuring anchor margins, NOT in the original list of
    # eight. It sits in the Introduction rather than in a Code/Data availability
    # section, which is why an enumeration that looked where such sentences are
    # expected missed it. Finding one occurrence never measures the population.
    ("preprint_npj/paper.tex", "and released open-source under Apache-2.0", 1,
     "Introduction: the pipeline itself is public NOW."),
    ("preprint_npj/paper.tex", "are released open-source", 1,
     "Code availability: the artefacts are public NOW."),
    ("preprint_npj/paper.tex", "already openly available in the public code repository", 1,
     "Data availability: the repository is public NOW, pre-deposit."),
    ("preprint_npj/paper.tex", "released under the Apache-2.0 license at", 1,
     "Code availability: a resolvable public URL is given."),
    ("preprint_npj/supplement.tex", "released under the Apache-2.0 license at", 1,
     "Supplement repeats the public URL claim."),
    ("preprint_npj/supplement.tex", "openly available under", 1,
     "Supplement: the experiment logs are public NOW."),
    ("preprint_npj/cover_letter.md", "is released open-source under Apache-2.0", 1,
     "Cover letter: the whole pipeline is public NOW."),
    ("preprint_npj/cover_letter.md", "All data and code are openly available", 1,
     "Cover letter: blanket present-tense availability."),
    ("preprint_npj/reporting_summary_draft.md", "All analysis code is released under Apache-2.0 at", 1,
     "Reporting summary: public URL for the analysis code."),
]


def occurrences(path: pathlib.Path, anchor: str) -> list[tuple[int, str]]:
    hits = []
    for n, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
        start = 0
        while (i := line.find(anchor, start)) != -1:
            hits.append((n, line[max(0, i - 30) : i + len(anchor) + 30].strip()))
            start = i + 1
    return hits


def http_status(slug: str) -> str:
    try:
        r = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
             f"https://api.github.com/repos/{slug}"],
            capture_output=True, text=True, timeout=30,
        )
        return r.stdout.strip() or "?"
    except Exception as e:  # noqa: BLE001
        return f"error: {e}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify-public", action="store_true",
                    help="also query GitHub for the repository's visibility")
    args = ap.parse_args()

    print("## Publication gate -- present-tense availability statements\n")
    failures = 0
    for rel, anchor, expected, proposition in CLAIMS:
        path = REPO / rel
        if not path.exists():
            print(f"  FAIL  {rel}: file missing")
            failures += 1
            continue
        hits = occurrences(path, anchor)
        ok = len(hits) == expected
        mark = "ok  " if ok else "FAIL"
        print(f"  {mark}  {rel}")
        print(f"        anchor   {anchor!r}")
        print(f"        found    {len(hits)} (expected {expected})"
              + ("" if ok else "   <-- the gate does not choose between candidates"))
        for n, ctx in hits:
            print(f"          L{n}: ...{ctx}...")
        print(f"        asserts  {proposition}")
        if not ok:
            failures += 1

    print(f"\n  {len(CLAIMS) - failures} / {len(CLAIMS)} anchors resolve as declared.")
    if failures:
        print("\n  A missing anchor means the statement was reworded, moved or deleted.")
        print("  Re-read the locus and update CLAIMS here -- do not weaken the count.")
        return 1

    if not args.verify_public:
        print("\n  Repository visibility NOT checked. Re-run with --verify-public")
        print("  before submitting; every statement above is false while it is private.")
        return 0

    print("\n## Repository visibility\n")
    repo, control = http_status(SLUG), http_status(CONTROL)
    print(f"  {SLUG}: {repo}")
    print(f"  control {CONTROL}: {control}   (a bare 404 proves nothing if the network is down)")
    if control != "200":
        print("\n  INCONCLUSIVE: the control did not return 200, so the network or the")
        print("  API is the variable, not the repository. Re-run.")
        return 1
    if repo != "200":
        print(f"\n  BLOCKED: repository is not public ({repo}); the control confirms the")
        print("  network is fine. All eight statements above are false today.")
        print("  Make the repository public BEFORE submitting, per the release order.")
        return 1
    print("\n  CLEAR: repository is public and all eight statements are true.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
