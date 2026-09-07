"""Measure the manuscript's elementary-effect pair counts against the artefact.

WHY THIS EXISTS. Section 2.2 of the paper states how much data each published
Morris index actually rests on: how many of the 144 top-three entries are
computed from a single elementary-effect pair, how many from three or fewer,
and what the median is. Those five numbers are re-derived from
``results/sobol_ci_buckets.csv``. Nothing re-measured them against that file,
so they were an assumption the moment they were typed.

WHY A GUARD AND NOT A LEDGER ANCHOR. Both were tried. Five ledger anchors were
written first and the audit went green at 387/387 -- and then failed, because
25 places across README.md, supplement.tex and manuscript.md quote the ledger's
own total. One added anchor cascades into all of them; a guard carries its own
counter and cascades nowhere. See audit/ and the project rule: guard by default
as soon as more than one number is involved.

THE UNIT, stated before any count. One entry = one (cell, output, input) row
among the 144 top-three entries, i.e. 48 cell x output combinations x 3 ranked
inputs. Not runs, not combinations, not trajectories -- though on this design
n_clean_pairs equals n_trajectories on every row, because one Morris trajectory
contributes exactly one step per input.

WHAT IT CHECKS.
  CHECK A: the sentence is found. It is delimited by two literals, and if
  either stops matching the guard FAILS rather than silently checking nothing.
  A rewrite therefore forces re-registration instead of quietly disarming.
  CHECK B: every count in that sentence equals the value re-derived from the
  CSV, matched as a whole phrase so an unrelated digit elsewhere cannot
  satisfy it.
  CHECK C: n_total_pairs is 20 on every row. "7 of the 20 possible" is one
  number only while the denominator is uniform.

Usage:
      python scripts/check_pair_counts.py              (measure)
      python scripts/check_pair_counts.py --list       (print the population)
      python scripts/check_pair_counts.py --self-test  (calibrate)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
PAPER = REPO / "preprint_npj" / "paper.tex"
BUCKETS = REPO / "results" / "sobol_ci_buckets.csv"

# The sentence under guard, delimited rather than pattern-matched.
SENTENCE_OPEN = "The same mechanism sets how much data each index rests on"
SENTENCE_CLOSE = "The ranking is cross-verified"

# The manuscript spells this one count as a word, so the guard must too.
NUM_WORDS = {
    1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
    6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
}


def measure(df: pd.DataFrame) -> dict[str, int]:
    """Re-derive every count the sentence states, from the released artefact."""
    ncp = df["n_clean_pairs"]
    median = float(ncp.median())
    if median != int(median):
        raise SystemExit(
            f"  FAIL  median n_clean_pairs is {median}, not an integer; the "
            f"sentence writes it as one and must be re-derived by hand"
        )
    return {
        "population": int(len(df)),
        "total_pairs": int(df["n_total_pairs"].iloc[0]),
        "median": int(median),
        "le3": int((ncp <= 3).sum()),
        "single": int((ncp == 1).sum()),
        "single_rank1": int(((ncp == 1) & (df["rank"] == 1)).sum()),
    }


def expected_phrases(m: dict[str, int]) -> list[tuple[str, str]]:
    """(label, phrase) the sentence must contain, built from the measurement."""
    return [
        ("population",
         f"across the {m['population']} top-three entries"),
        ("median",
         f"the median index is computed from {m['median']} of the "
         f"{m['total_pairs']} possible elementary-effect pairs"),
        ("le3",
         f"{m['le3']} rest on three or fewer"),
        ("single",
         f"{m['single']} rest on a single pair"),
        ("single_rank1",
         f"{NUM_WORDS[m['single_rank1']]} of those being their "
         f"combination's rank-1 input"),
    ]


def extract_sentence(paper_text: str) -> str:
    """CHECK A. A missing delimiter FAILS; it never yields an empty passage."""
    start = paper_text.find(SENTENCE_OPEN)
    if start == -1:
        raise LookupError(
            f"opening delimiter not found: {SENTENCE_OPEN!r}. The guarded "
            f"sentence was rewritten or removed; re-register it here."
        )
    end = paper_text.find(SENTENCE_CLOSE, start)
    if end == -1:
        raise LookupError(
            f"closing delimiter not found after the opening one: "
            f"{SENTENCE_CLOSE!r}. Re-register the passage."
        )
    return paper_text[start:end]


def check(paper_text: str, df: pd.DataFrame) -> list[str]:
    """Return the list of problems; empty means the manuscript agrees."""
    problems: list[str] = []

    # CHECK C first: every later number is quoted against this denominator.
    totals = set(df["n_total_pairs"].unique())
    if totals != {20}:
        problems.append(
            f"n_total_pairs is no longer uniformly 20 (found {sorted(totals)}); "
            f"'N of the 20 possible' has stopped being one number"
        )
        return problems

    m = measure(df)

    try:
        sentence = extract_sentence(paper_text)
    except LookupError as exc:
        problems.append(str(exc))
        return problems

    for label, phrase in expected_phrases(m):
        if phrase not in sentence:
            problems.append(f"{label}: paper does not state {phrase!r}")
    return problems


def self_test(paper_text: str, df: pd.DataFrame) -> int:
    """Calibrate on the EXACT defects this guard exists to catch."""
    print("## Self-test\n")
    failures: list[str] = []
    m = measure(df)

    # Positive controls: each count, wrong by one, must be caught.
    mutations = [
        (f"{m['single']} rest on a single pair",
         f"{m['single'] - 1} rest on a single pair", "single-pair count"),
        (f"{m['le3']} rest on three or fewer",
         f"{m['le3'] - 1} rest on three or fewer", "three-or-fewer count"),
        (f"across the {m['population']} top-three entries",
         f"across the {m['population'] - 1} top-three entries", "population"),
        (f"from {m['median']} of the {m['total_pairs']} possible",
         f"from {m['median'] + 1} of the {m['total_pairs']} possible", "median"),
        (NUM_WORDS[m["single_rank1"]] + " of those being",
         NUM_WORDS[m["single_rank1"] - 1] + " of those being", "rank-1 subset"),
    ]
    for old, new, label in mutations:
        if old not in paper_text:
            failures.append(f"mutation target absent, cannot calibrate: {old!r}")
            continue
        if not check(paper_text.replace(old, new, 1), df):
            failures.append(f"guard did NOT catch a wrong {label}")
        else:
            print(f"  ok    catches a wrong {label}")

    # A removed delimiter must FAIL, not silently pass on an empty passage.
    gutted = paper_text.replace(SENTENCE_OPEN, "The same mechanism sets how", 1)
    if not check(gutted, df):
        failures.append("guard passed with its opening delimiter removed")
    else:
        print("  ok    fails loudly when the sentence is rewritten away")

    # Negative controls.
    if check(paper_text, df):
        failures.append("guard fails on the unmodified manuscript")
    else:
        print("  ok    unmodified manuscript passes")

    # A digit elsewhere in the document must not satisfy a phrase check.
    decoyed = paper_text.replace(
        f"{m['single']} rest on a single pair",
        f"{m['single'] - 1} rest on a single pair", 1,
    ) + f"\n% decoy {m['single']} rest on a single pair\n"
    if not check(decoyed, df):
        failures.append("a decoy outside the guarded sentence satisfied the check")
    else:
        print("  ok    a matching phrase outside the sentence does not count")

    if failures:
        print("\n  FAIL  self-test")
        for f in failures:
            print(f"        {f}")
        return 1
    print("\n  Self-test passed.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list", action="store_true", help="print the watched population")
    ap.add_argument("--self-test", action="store_true", help="calibrate the guard")
    args = ap.parse_args()

    if not BUCKETS.exists():
        print(f"  FAIL  artefact missing: {BUCKETS.relative_to(REPO)}")
        return 1
    df = pd.read_csv(BUCKETS)
    paper_text = PAPER.read_text(encoding="utf-8")

    if args.self_test:
        return self_test(paper_text, df)

    m = measure(df)
    if args.list:
        print("## Watched population\n")
        print(f"  source      {BUCKETS.relative_to(REPO)}")
        print("  unit        one (cell, output, input) top-three entry")
        print(f"  population  {m['population']} entries, "
              f"{m['population'] // 3} combinations x 3\n")
        for label, phrase in expected_phrases(m):
            print(f"  {label:<13} {phrase}")
        print("\n  n_clean_pairs distribution:")
        for value, count in sorted(df["n_clean_pairs"].value_counts().items()):
            print(f"    {value:>3} pair(s): {count:>3} entries")
        return 0

    print("## Manuscript pair counts vs results/sobol_ci_buckets.csv\n")
    problems = check(paper_text, df)
    if problems:
        print(f"  FAIL  {len(problems)} disagreement(s):")
        for p in problems:
            print(f"        {p}")
        print("\n  These numbers describe how much data each published index")
        print("  rests on. Re-derive them from the artefact rather than editing")
        print("  the prose to match:  python scripts/check_pair_counts.py --list")
        return 1
    print(f"  ok    {len(expected_phrases(m))} counts agree with the artefact")
    print(f"  ok    n_total_pairs uniform at {m['total_pairs']} on "
          f"{m['population']} entries")
    print("\n  PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
