"""Measure the paper's non-linearity paragraph (2.2) against what produced it.

WHY THIS EXISTS. Section 2.2 states how much data each published Morris index
actually rests on: how many of the 144 top-three entries are computed from a
single elementary-effect pair, how many from three or fewer, and what the
median is. Those five numbers are re-derived from
``results/sobol_ci_buckets.csv``. Nothing re-measured them against that file,
so they were an assumption the moment they were typed.

The same paragraph also states the preregistered non-linearity trigger and the
resampling design, and both had drifted from the code by the time this guard
was written (fixed 2026-09-07):

  * it said the threshold was ``sigma/mu* > 0.6`` while the preregistration,
    Methods 4.6, Supplement S3 and BOTH implementations use ``>= 0.6``. Four
    statements of one trigger and this was the only one excluding equality.
  * it said "in all five bootstrap draws". There are N_BOOTSTRAP draws per
    seed and five SEEDS. The identical conflation had already been corrected
    in Methods 4.6 by 83da8a2 earlier the same day -- that sweep found one
    locus and the population was two, which is exactly the failure a guard
    exists to stop repeating.
  * the 2026-09-07 fix wrote "in every draw under each of five independent
    seeds", which is false as read: a draw is ONE of the N_BOOTSTRAP
    resamples, and the criterion is that the 2.5th percentile of those draws
    is >= 0.6 under each seed. On 2026-09-27, 16 of the 23 stable inputs were
    measured to have draws below 0.6 (up to 1.9 % of them). The same wording
    stood in Methods 4.6 and Supplement S3-sobol; all three now state the
    per-seed lower bound, and CHECK F bans "every draw" in both files.

Those three are therefore checked here against ``scripts/sobol_ci_buckets.py``,
read as text rather than imported, so that running this guard never executes
the bootstrap.

WHY A GUARD AND NOT A LEDGER ANCHOR, and where the line actually falls. Five
ledger anchors were written first and the audit went green -- then failed,
because 25 places across README.md, supplement.tex and manuscript.md quote the
ledger's own total. One added anchor cascades into all of them; a guard carries
its own counter and cascades nowhere.

That is the cost side. The correctness side decides first, and it was learned
the hard way the same day: a guard pins a LITERAL, so it can only catch a
number that was typed wrong. It cannot catch a number that was typed RIGHT and
was later falsified when its source moved -- which is exactly what happened to
Supplement S9's "779 mmHg" when da5bd97 repaired the S021 window 39 days after
it was written. Only re-derivation survives a moving source, so those two
numbers got ledger anchors and the cascade was paid.

The numbers guarded here have no upstream that can move independently of them:
they describe the shape of a fixed sweep. A guard is the right instrument for
that, an anchor for the other.

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
  CHECK D: the trigger sentence states the threshold and the seed count that
  scripts/sobol_ci_buckets.py actually uses. The seed count is cross-checked
  against the CSV's own per-seed ra_lo_* columns, so two instruments have to
  agree before the paper is judged.
  CHECK E: Figure 3's caption states how many cells it outlines, measured
  against results/morris_indices.parquet. That is a DIFFERENT population from
  the sentence above -- the figure draws every entry, the sentence counts
  inside the top three only -- so the two legitimately disagree, and each is
  measured on its own table.
  CHECK F: "every draw" appears nowhere in paper.tex or supplement.tex. The
  monograph is not read: its own "linear in every draw" (manuscript.md, 31 of
  48) uses a draw for one whole seed run and is true under either reading.

Usage:
      python scripts/check_pair_counts.py              (measure)
      python scripts/check_pair_counts.py --list       (print the population)
      python scripts/check_pair_counts.py --self-test  (calibrate)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
PAPER = REPO / "preprint_npj" / "paper.tex"
SUPPLEMENT = REPO / "preprint_npj" / "supplement.tex"
BUCKETS = REPO / "results" / "sobol_ci_buckets.csv"

# CHECK F. A draw is one bootstrap resample; the stable-set criterion is a
# per-seed lower bound, which no single draw has.
DRAW_DEFECT = "every draw"

# The sentences under guard, delimited rather than pattern-matched.
# Re-registered 2026-10-06 after the M. Sauthier review split the Results paragraph
# in three; the counts and the phrases they must appear in are unchanged in content.
SENTENCE_OPEN = "Run survival also limits the data behind each index"
SENTENCE_CLOSE = "Per-entry pair counts are released"

TRIGGER_OPEN = "Influence is not proportionality"
TRIGGER_CLOSE = "Delivered tidal volume is the most affected output"

BUCKETS_SRC = REPO / "scripts" / "sobol_ci_buckets.py"

# CHECK E's source. The Results sentence counts inside the 144 top-three
# entries; Figure 3 draws every entry, so its outlined-cell count is a DIFFERENT
# population and must be measured on the full table, not on the top-three one.
MORRIS = REPO / "results" / "morris_indices.parquet"
# "tiles", not "cells", since 2026-09-23: a heatmap square is a (cell, output)
# combination, and "cell" is reserved for the (scenario, sex) slice of Table 1.
CAPTION_OPEN = "White tiles mark combinations with no estimable"
CAPTION_CLOSE = "Cell-label key"
THRESHOLD_RE = re.compile(r"^PROMOTE_THRESHOLD\s*=\s*([\d.]+)", re.M)
SEEDS_RE = re.compile(r"^SEEDS\s*=\s*\(([^)]*)\)", re.M)

# The manuscript spells this one count as a word, so the guard must too.
NUM_WORDS = {
    1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
    7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve",
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


def read_trigger_design(src_text: str, df: pd.DataFrame) -> dict[str, object]:
    """Parse the trigger constants from source text; never import the module.

    Importing scripts/sobol_ci_buckets.py would run a bootstrap. The seed count
    is cross-checked against the CSV's own per-seed columns so the number rests
    on two instruments rather than on one regex.
    """
    thr = THRESHOLD_RE.search(src_text)
    seeds = SEEDS_RE.search(src_text)
    if not thr or not seeds:
        raise LookupError(
            "PROMOTE_THRESHOLD or SEEDS no longer parse out of "
            "scripts/sobol_ci_buckets.py; re-register this guard"
        )
    n_seeds = len([s for s in seeds.group(1).split(",") if s.strip()])
    n_seed_cols = len([c for c in df.columns if c.startswith("ra_lo_")])
    if n_seeds != n_seed_cols:
        raise LookupError(
            f"seed count disagrees between the script ({n_seeds}) and the "
            f"CSV's ra_lo_* columns ({n_seed_cols}); one of them is stale"
        )
    return {"threshold": thr.group(1), "n_seeds": n_seeds}


def expected_phrases(m: dict[str, int]) -> list[tuple[str, str]]:
    """(label, phrase) the sentence must contain, built from the measurement."""
    return [
        ("population",
         f"the {m['population']} top-three entries"),
        ("median",
         f"the median index is computed from {m['median']} of the "
         f"{m['total_pairs']} possible elementary-effect pairs"),
        ("le3",
         f"{m['le3']} rest on three or fewer"),
        ("single",
         f"{m['single']} on a single pair"),
        ("single_rank1",
         f"{NUM_WORDS[m['single_rank1']]} of them their "
         f"combination's rank-1 input"),
    ]


def extract_sentence(
    paper_text: str,
    opener: str = SENTENCE_OPEN,
    closer: str = SENTENCE_CLOSE,
) -> str:
    """CHECK A. A missing delimiter FAILS; it never yields an empty passage."""
    start = paper_text.find(opener)
    if start == -1:
        raise LookupError(
            f"opening delimiter not found: {opener!r}. The guarded "
            f"sentence was rewritten or removed; re-register it here."
        )
    end = paper_text.find(closer, start)
    if end == -1:
        raise LookupError(
            f"closing delimiter not found after the opening one: "
            f"{closer!r}. Re-register the passage."
        )
    return paper_text[start:end]


def check(paper_text: str, df: pd.DataFrame, supplement_text: str = "") -> list[str]:
    """Return the list of problems; empty means the manuscript agrees."""
    problems: list[str] = []

    # CHECK F first, so no early return below can skip it.
    for name, text in (("paper.tex", paper_text), ("supplement.tex", supplement_text)):
        if DRAW_DEFECT in text:
            problems.append(
                f"{name} says {DRAW_DEFECT!r}: a draw is one resample, and the "
                f"criterion is a per-seed lower bound"
            )

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

    # CHECK D: the trigger sentence, against the code that applies the trigger.
    try:
        design = read_trigger_design(BUCKETS_SRC.read_text(encoding="utf-8"), df)
        trigger = extract_sentence(paper_text, TRIGGER_OPEN, TRIGGER_CLOSE)
    except LookupError as exc:
        problems.append(str(exc))
        return problems

    threshold_phrase = (
        rf"$\sigma / \mu^{{*}} \geq {design['threshold']}$ threshold"
    )
    seeds_phrase = f"{NUM_WORDS[design['n_seeds']]} independent seeds"
    for label, phrase in [
        ("threshold", threshold_phrase),
        ("seeds", seeds_phrase),
    ]:
        if phrase not in trigger:
            problems.append(f"{label}: paper does not state {phrase!r}")

    # CHECK E: Figure 3's caption counts the outlined cells, and it counts them
    # over EVERY entry, not only the top-three ones the sentence above uses. Nine
    # twelve are top-three entries; the other three are not, and marking only
    # those nine would have left three single-pair cells looking solid.
    if not MORRIS.exists():
        problems.append(f"artefact missing: {MORRIS.relative_to(REPO)}")
        return problems
    n_outlined = int((pd.read_parquet(MORRIS)["n_clean_pairs"] == 1).sum())
    if n_outlined not in NUM_WORDS:
        problems.append(f"outlined-cell count {n_outlined} has no word form here")
        return problems
    try:
        caption = extract_sentence(paper_text, CAPTION_OPEN, CAPTION_CLOSE)
    except LookupError as exc:
        problems.append(str(exc))
        return problems
    outlined_phrase = f"Outlined tiles ({NUM_WORDS[n_outlined]})"
    if outlined_phrase not in caption:
        problems.append(f"outlined: Figure 3 caption does not state {outlined_phrase!r}")
    return problems


def self_test(paper_text: str, df: pd.DataFrame, supplement_text: str) -> int:
    """Calibrate on the EXACT defects this guard exists to catch."""
    print("## Self-test\n")
    failures: list[str] = []
    m = measure(df)
    supp = supplement_text

    # Positive controls: each count, wrong by one, must be caught.
    mutations = [
        (f"{m['single']} on a single pair",
         f"{m['single'] - 1} on a single pair", "single-pair count"),
        (f"{m['le3']} rest on three or fewer",
         f"{m['le3'] - 1} rest on three or fewer", "three-or-fewer count"),
        (f"the {m['population']} top-three entries",
         f"the {m['population'] - 1} top-three entries", "population"),
        (f"from {m['median']} of the {m['total_pairs']} possible",
         f"from {m['median'] + 1} of the {m['total_pairs']} possible", "median"),
        (NUM_WORDS[m["single_rank1"]] + " of them their",
         NUM_WORDS[m["single_rank1"] - 1] + " of them their", "rank-1 subset"),
    ]
    for old, new, label in mutations:
        if old not in paper_text:
            failures.append(f"mutation target absent, cannot calibrate: {old!r}")
            continue
        if not check(paper_text.replace(old, new, 1), df, supp):
            failures.append(f"guard did NOT catch a wrong {label}")
        else:
            print(f"  ok    catches a wrong {label}")

    # CHECK D and CHECK F calibrated on the three defects that were live in this
    # paragraph (two until 2026-09-07, one until 2026-09-27), reproduced
    # verbatim rather than by a plausible stand-in.
    historical = [
        (r"$\sigma / \mu^{*} \geq 0.6$", r"$\sigma / \mu^{*} > 0.6$",
         "the threshold written as a strict inequality"),
        ("at or above it under each of five independent seeds",
         "clear it in all five bootstrap draws",
         "a seed count passed off as a draw count"),
        (r"with a 95~\% bootstrap interval at or above it under each of five independent seeds",
         "that clear it in every draw under each of five independent seeds",
         "a per-seed lower bound passed off as every draw"),
    ]
    for old, new, label in historical:
        if old not in paper_text:
            failures.append(f"historical defect target absent: {old!r}")
            continue
        if not check(paper_text.replace(old, new, 1), df, supp):
            failures.append(f"guard did NOT catch {label}")
        else:
            print(f"  ok    catches {label}")

    # CHECK F on the supplement, with its own 2026-09-27 wording reinjected.
    supp_old = "keep the lower bound of this joint interval at or above 0.6"
    supp_new = "keep a lower bound at or above 0.6 in every draw"
    if supp_old not in supp:
        failures.append(f"supplement defect target absent: {supp_old!r}")
    elif not check(paper_text, df, supp.replace(supp_old, supp_new, 1)):
        failures.append("guard did NOT catch the supplement's every-draw wording")
    else:
        print("  ok    catches the supplement's every-draw wording")

    # CHECK E calibrated on its own count, measured from the full table
    # rather than assumed from the 144 the sentence above uses.
    n_out = int((pd.read_parquet(MORRIS)["n_clean_pairs"] == 1).sum())
    old_out = f"Outlined tiles ({NUM_WORDS[n_out]})"
    new_out = f"Outlined tiles ({NUM_WORDS[n_out - 1]})"
    if old_out not in paper_text:
        failures.append(f"outlined-count target absent, cannot calibrate: {old_out!r}")
    elif not check(paper_text.replace(old_out, new_out, 1), df, supp):
        failures.append("guard did NOT catch a wrong outlined-cell count")
    else:
        print("  ok    catches a wrong outlined-cell count")

    # A removed delimiter must FAIL, not silently pass on an empty passage.
    for opener, stub, which in [
        (SENTENCE_OPEN, "Run survival also limits the", "pair-count"),
        (TRIGGER_OPEN, "Influence is not", "trigger"),
        (CAPTION_OPEN, "White tiles mark combinations with no", "caption"),
    ]:
        if not check(paper_text.replace(opener, stub, 1), df, supp):
            failures.append(
                f"guard passed with the {which} opening delimiter removed"
            )
        else:
            print(f"  ok    fails loudly if the {which} sentence is rewritten away")

    # Negative controls.
    if check(paper_text, df, supp):
        failures.append("guard fails on the unmodified manuscript")
    else:
        print("  ok    unmodified manuscript passes")

    # A digit elsewhere in the document must not satisfy a phrase check.
    decoyed = paper_text.replace(
        f"{m['single']} on a single pair",
        f"{m['single'] - 1} on a single pair", 1,
    ) + f"\n% decoy {m['single']} on a single pair\n"
    if not check(decoyed, df, supp):
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
    supplement_text = SUPPLEMENT.read_text(encoding="utf-8")

    if args.self_test:
        return self_test(paper_text, df, supplement_text)

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
    problems = check(paper_text, df, supplement_text)
    if problems:
        print(f"  FAIL  {len(problems)} disagreement(s):")
        for p in problems:
            print(f"        {p}")
        print("\n  These numbers describe how much data each published index")
        print("  rests on. Re-derive them from the artefact rather than editing")
        print("  the prose to match:  python scripts/check_pair_counts.py --list")
        return 1
    design = read_trigger_design(BUCKETS_SRC.read_text(encoding="utf-8"), df)
    print(f"  ok    {len(expected_phrases(m))} counts agree with the artefact")
    print(f"  ok    n_total_pairs uniform at {m['total_pairs']} on "
          f"{m['population']} entries")
    print(f"  ok    trigger stated as >= {design['threshold']}, matching "
          f"sobol_ci_buckets.PROMOTE_THRESHOLD")
    print(f"  ok    {design['n_seeds']} seeds in the paper, in the script and "
          f"in the CSV's ra_lo_* columns")
    print(f"  ok    no {DRAW_DEFECT!r} in paper.tex or supplement.tex")
    morris = pd.read_parquet(MORRIS)
    n_out = int((morris["n_clean_pairs"] == 1).sum())
    print(f"  ok    Figure 3 caption outlines {n_out} cells, matching the "
          f"single-pair rows of morris_indices.parquet ({len(morris)} entries)")
    print("\n  PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
