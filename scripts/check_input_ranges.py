#!/usr/bin/env python3
"""Gate the manuscript's statement of the swept input ranges against src/sampler.py.

Why this exists
---------------
On 2026-09-07 the author, re-reading the mailed PDFs, found that Methods 4.3 of `paper.tex` stated

    tidal volume (Vt, 300--700~mL) ... PEEP, 0--15~cmH$_2$O

while the sweep that produced every number in the paper actually ran on

    Vt   300--800 mL     (levels 300 / 466.67 / 633.33 / 800)
    PEEP   0--20 cmH2O   (levels 0 / 6.67 / 13.33 / 20)

Four sources agreed against the manuscript: `src/sampler.py`, `preregistration.md`,
`supplement.tex` (three loci), and -- decisively -- `results/input_instantiation_long.csv`,
which records the values actually submitted to the engine.

The defect was introduced by commit d88a1ca while SHORTENING that sentence. The
version mailed to the co-authors in August (613f2a6) was correct. Two numeric
literals were silently rewritten during a prose-compression edit, and every gate
stayed green, because structurally each had to:

  * `audit_claims.py` DOES parse `InputSpec` bounds out of `src/sampler.py`
    (see the T5.clip block) -- but only to normalise the clip computation. No
    anchor ever compared those bounds to the sentence that states them.
  * `check_render.py` reads structure, not constants.
  * A numeric diff of the August and September papers cannot see it either:
    "700" and "15" already occurred elsewhere in the document, so the corruption
    introduced no new token. That instrument is blind to exactly this defect.

The swept domain is the definition of what every mu* in the paper means. A
constant that is transcribed into prose, and never re-measured against its own
source, is an assumption. This guard turns it back into a measurement.

How it works
------------
`src/sampler.py` is the single source of truth: the sampler that generated the
design is the only artefact that can be wrong in a way that matters.

  CHECK A -- the enumerating sentence.
      Methods 4.3 carries one sentence listing all seven ranges. The set of
      numeric ranges inside it must equal the set of InputSpec bounds exactly.
      The passage is delimited by two literals; if either has been reworded the
      guard FAILS rather than silently checking nothing, which forces a human
      to re-register the passage.

  CHECK B -- every unit-bearing range in both documents.
      Each swept input is identified by its (low bound, LaTeX unit) pair. Those
      pairs are collision-free against the rest of the corpus: other mL and bpm
      ranges exist (64--79.3~mL, 145--160~bpm, 10--15~mL ...) but none of them
      shares a low bound AND a unit with a swept input. So wherever
      "<lo>--<x>~<unit>" occurs for a swept pair, x must be that input's high
      bound. This catches a drifted range anywhere in either document, not only
      in the sentence CHECK A pins.

Calibration
-----------
`--self-test` reproduces the EXACT defect that motivated the guard (Vt 800->700
and PEEP 20->15) and requires both checks to fail on it, plus two negative
controls that must stay green. A guard never observed to fail is an assumption,
not a test.

Run:  python scripts/check_input_ranges.py
      python scripts/check_input_ranges.py --list       (print the population)
      python scripts/check_input_ranges.py --self-test  (calibrate)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SAMPLER = REPO / "src" / "sampler.py"
PAPER = REPO / "preprint_npj" / "paper.tex"
SUPPLEMENT = REPO / "preprint_npj" / "supplement.tex"

# The two literals delimiting the Methods 4.3 enumeration. If either stops
# matching, the passage was rewritten and this guard must be re-registered
# against the new wording -- so a miss is a FAILURE, never a silent pass.
# Re-registered 2026-09-27: the sentence no longer calls all seven ranges
# "verified Pulse acceptance ranges" (Vt, FiO2 and PEEP are clinical ranges
# fixed in the preregistration); the closing anchor did not change.
SENTENCE_OPEN = "swept across the following ranges"
SENTENCE_CLOSE = "Each range is anchored"

# LaTeX unit tokens per swept input, as they appear after "~" in the sources.
# fio2 is dimensionless and carries no unit token, so CHECK B cannot address it;
# CHECK A covers it.
UNIT_TOKENS: dict[str, tuple[str, ...]] = {
    "hr": ("bpm",),
    "sbp": ("mmHg",),
    "dbp": ("mmHg",),
    "rr": ("bpm", "breaths"),
    "vt": ("mL",),
    "fio2": (),
    "peep": ("cmH",),
}

RANGE_RE = re.compile(r"(\d[\d.]*)--(\d[\d.]*)")
INPUTSPEC_RE = re.compile(r"InputSpec\(\"(\w+)\",\s*([\d.]+),\s*([\d.]+)")


def read_specs(sampler_text: str) -> dict[str, tuple[float, float]]:
    """The swept bounds, read from the sampler that generated the design."""
    specs = {m[0]: (float(m[1]), float(m[2])) for m in INPUTSPEC_RE.findall(sampler_text)}
    if len(specs) != 7:
        raise SystemExit(
            f"  FAIL  expected 7 InputSpec rows in {SAMPLER}, found {len(specs)}.\n"
            "        The sampler changed shape; this guard must be re-derived."
        )
    missing = set(specs) - set(UNIT_TOKENS)
    if missing:
        raise SystemExit(
            f"  FAIL  sampler declares input(s) this guard does not know: {sorted(missing)}.\n"
            "        Add their unit tokens to UNIT_TOKENS before shipping."
        )
    return specs


def _fmt(lo: float, hi: float) -> str:
    def one(v: float) -> str:
        return str(int(v)) if float(v).is_integer() else str(v)

    return f"{one(lo)}--{one(hi)}"


def check_sentence(paper_text: str, specs: dict[str, tuple[float, float]]) -> list[str]:
    """CHECK A: the Methods enumeration must state exactly the sampler's bounds."""
    start = paper_text.find(SENTENCE_OPEN)
    if start < 0:
        return [
            f"the ranges passage is gone from paper.tex (anchor: {SENTENCE_OPEN!r}). "
            "Re-register this guard against the new wording."
        ]
    end = paper_text.find(SENTENCE_CLOSE, start)
    if end < 0:
        return [
            f"the ranges passage no longer closes with {SENTENCE_CLOSE!r}. "
            "Re-register this guard against the new wording."
        ]

    window = paper_text[start:end]
    stated = {(float(a), float(b)) for a, b in RANGE_RE.findall(window)}
    expected = set(specs.values())

    problems = []
    for name, (lo, hi) in sorted(specs.items()):
        if (lo, hi) not in stated:
            wrong = [s for s in stated if s[0] == lo and s not in expected]
            got = f"states {_fmt(*wrong[0])}" if wrong else "absent from the passage"
            problems.append(
                f"{name}: sampler says {_fmt(lo, hi)}, Methods 4.3 {got}"
            )
    for pair in sorted(stated - expected):
        problems.append(
            f"Methods 4.3 states the range {_fmt(*pair)}, which no swept input carries"
        )
    return problems


def check_corpus(
    docs: dict[str, str], specs: dict[str, tuple[float, float]]
) -> list[str]:
    """CHECK B: every unit-bearing occurrence of a swept range must be correct."""
    problems = []
    for doc_name, text in docs.items():
        for name, (lo, hi) in sorted(specs.items()):
            for unit in UNIT_TOKENS[name]:
                lo_lit = str(int(lo)) if float(lo).is_integer() else str(lo)
                pat = re.compile(
                    re.escape(lo_lit) + r"--(\d[\d.]*)~" + re.escape(unit)
                )
                for m in pat.finditer(text):
                    if float(m.group(1)) != hi:
                        line = text[: m.start()].count("\n") + 1
                        problems.append(
                            f"{doc_name}:{line}  {name}: sampler says {_fmt(lo, hi)}, "
                            f"text says {lo_lit}--{m.group(1)}~{unit}"
                        )
    return problems


def population(docs: dict[str, str], specs: dict[str, tuple[float, float]]) -> int:
    """Print what the guard actually watches, so its coverage is auditable."""
    print("  Source of truth: src/sampler.py InputSpec bounds\n")
    watched = 0
    for name, (lo, hi) in sorted(specs.items()):
        units = ", ".join(UNIT_TOKENS[name]) or "(dimensionless)"
        hits = 0
        for text in docs.values():
            for unit in UNIT_TOKENS[name]:
                lo_lit = str(int(lo)) if float(lo).is_integer() else str(lo)
                hits += len(
                    re.findall(re.escape(lo_lit) + r"--\d[\d.]*~" + re.escape(unit), text)
                )
        watched += hits
        print(f"    {name:5s} {_fmt(lo, hi):12s} units: {units:18s} occurrences watched: {hits}")
    print(f"\n  CHECK A pins the {len(specs)} ranges in the Methods enumeration.")
    print(f"  CHECK B watches {watched} unit-bearing occurrence(s) across both documents.")
    return watched


def self_test(specs: dict[str, tuple[float, float]], paper_text: str, supp_text: str) -> int:
    """Calibrate on the exact defect that motivated the guard, plus two controls."""
    print("  Calibrating on the 2026-09-07 defect (d88a1ca) and two controls.\n")
    failures = []

    # Positive control 1: the exact corruption, in the Methods enumeration.
    mutated = paper_text.replace("300--800~mL", "300--700~mL").replace(
        "0--20~cmH", "0--15~cmH"
    )
    if mutated == paper_text:
        failures.append(
            "could not reproduce the defect: the literals it rewrote are absent. "
            "The guard is not calibrated against anything."
        )
    else:
        a = check_sentence(mutated, specs)
        b = check_corpus({"paper.tex": mutated}, specs)
        if not a:
            failures.append("CHECK A passed the Vt 800->700 / PEEP 20->15 corruption")
        if not b:
            failures.append("CHECK B passed the Vt 800->700 / PEEP 20->15 corruption")
        print(f"    positive control: CHECK A raised {len(a)}, CHECK B raised {len(b)}")

    # Positive control 2: a drifted range OUTSIDE the enumeration, supplement only.
    supp_mut = supp_text.replace("300--800~mL", "300--750~mL", 1)
    if supp_mut == supp_text:
        failures.append("supplement carries no 300--800~mL range to mutate")
    else:
        b2 = check_corpus({"supplement.tex": supp_mut}, specs)
        if not b2:
            failures.append("CHECK B passed a drifted Vt range in the supplement")
        print(f"    positive control (supplement): CHECK B raised {len(b2)}")

    # Negative control 1: a non-swept mL range must NOT be flagged.
    benign = paper_text + "\n% guard control: an unrelated dose of 10--15~mL per kilogram.\n"
    if check_corpus({"paper.tex": benign}, specs):
        failures.append("CHECK B flagged an unrelated 10--15~mL range (false positive)")
    else:
        print("    negative control: unrelated 10--15~mL range correctly ignored")

    # Negative control 2: the corpus as it stands must be clean.
    if check_sentence(paper_text, specs) or check_corpus(
        {"paper.tex": paper_text, "supplement.tex": supp_text}, specs
    ):
        failures.append("the unmodified corpus does not pass; fix that before trusting a failure")
    else:
        print("    negative control: unmodified corpus passes")

    if failures:
        print("\n  SELF-TEST FAILED:")
        for f in failures:
            print(f"        {f}")
        return 1
    print("\n  SELF-TEST PASSED: the guard fails on the defect and stays quiet otherwise.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list", action="store_true", help="print the watched population")
    ap.add_argument("--self-test", action="store_true", help="calibrate the guard")
    args = ap.parse_args()

    specs = read_specs(SAMPLER.read_text(encoding="utf-8"))
    paper_text = PAPER.read_text(encoding="utf-8")
    supp_text = SUPPLEMENT.read_text(encoding="utf-8")
    docs = {"paper.tex": paper_text, "supplement.tex": supp_text}

    print("\n  INPUT-RANGE GATE -- manuscript prose against src/sampler.py")

    if args.list:
        population(docs, specs)
        return 0
    if args.self_test:
        return self_test(specs, paper_text, supp_text)

    problems = check_sentence(paper_text, specs)
    if problems:
        print("\n  FAIL  CHECK A -- Methods 4.3 enumeration disagrees with the sampler:")
        for p in problems:
            print(f"        {p}")

    corpus = check_corpus(docs, specs)
    if corpus:
        print(f"\n  FAIL  CHECK B -- {len(corpus)} unit-bearing range(s) disagree with the sampler:")
        for p in corpus:
            print(f"        {p}")

    if problems or corpus:
        print("\n        The swept domain defines what every mu* in the paper means.")
        print("        Fix the prose to match src/sampler.py, or, if the sampler itself")
        print("        changed, stop: that invalidates the sweep, not the sentence.")
        print(f"\n  INPUT-RANGE GATE FAILED ({len(problems) + len(corpus)} problem(s)).")
        return 1

    watched = population(docs, specs)
    print(f"\n  INPUT-RANGE GATE PASSED ({watched} occurrence(s) verified).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
