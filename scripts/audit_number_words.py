#!/usr/bin/env python3
"""Inventory of the numbers WRITTEN IN WORDS in the three public artefacts.

Why this exists
---------------
`scripts/audit_number_inventory.py` inventories numeric literals: its unit is a
run of digits. A number written in words -- "three of the four pairs",
"eleven independent verification points" -- is not in that population at all,
so no bucket, residue or mask ever showed one. Three defects already corrected
in the number audit were of that shape (monograph MF-7 "eleven", MF-20 "three of
the four pairs", supplement F-S3 "three of the eight"), and each was found only
because it sat in a sentence being read for a digit. Found 2026-09-15; the
author decided the same day to read them all (audit/number_inventory.md).

It inventories, it does not verify. The verdicts live in the register.

THE POPULATION, DEFINED BEFORE ANYTHING IS COUNTED
---------------------------------------------------
A token is IN the population when it is one of these English number words,
matched case-insensitively on word boundaries:

  cardinal        zero ... nineteen, twenty ... ninety, hundred(s), thousand(s),
                  million(s), billion(s); a hyphenated compound such as
                  "twenty-four" is ONE token.
  ordinal         first ... twentieth, thirtieth ... ninetieth, hundredth,
                  thousandth, and their plurals ("thirds", "tenths").
                  "second" is kept even where it is a unit of time: reading
                  decides, the pattern does not.
  multiplicative  half, halves, halved, halving, twice, thrice, double(s/d/ing),
                  triple(s/d/ing), quadruple(s/d), dozen(s), quarter(s); a
                  number word glued to "fold" ("tenfold", "five-fold"); and a
                  hyphenated fraction ("two-thirds", "one-half"). Each of these
                  is ONE token, never also counted as its cardinal part.

NOT in the population, stated so the boundary is explicit: quantifiers and
determiners (no, none, both, all, each, every, several, few, many, most,
single, sole, once, pair). They carry quantity in a looser sense and would make
the population the whole prose.

The same masks as the digit inventory are applied, through its `mask_out`
(comments and code, cross-reference machinery, URLs and paths, versions,
typesetting lengths, line references, organisation identifiers, product
versions). Every token a mask removes is written, with its rule and context, to
`number_words_masked.csv`, and the books are closed per artefact: tokens in the
raw text = tokens kept + tokens masked.

Outputs, under results/number_audit/:
  number_words.csv          one row per kept token
  number_words_masked.csv   one row per masked token
  number_words_summary.json counts per artefact and class, recall accounting,
                            calibration
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter

from audit_number_inventory import ARTEFACTS, OUT_DIR, REPO, mask_out

_UNITS = "zero|one|two|three|four|five|six|seven|eight|nine"
_TEENS = "ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen"
_TENS = "twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety"
_BIG = "hundreds?|thousands?|millions?|billions?"
_ORD = ("first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|"
        "thirteenth|fourteenth|fifteenth|sixteenth|seventeenth|eighteenth|nineteenth|"
        "twentieth|thirtieth|fortieth|fiftieth|sixtieth|seventieth|eightieth|ninetieth|"
        "hundredth|thousandth")
_ORD_PLURAL = ("thirds|fourths|fifths|sixths|sevenths|eighths|ninths|tenths|twentieths|"
               "hundredths|thousandths")
_MULT = ("half|halves|halved|halving|twice|thrice|double|doubles|doubled|doubling|triple|"
         "triples|tripled|tripling|quadruple|quadruples|quadrupled|dozen|dozens|quarter|quarters")

# Order matters: at one position Python takes the FIRST alternative that
# matches, so every multi-word form comes before the single words it contains.
# Group 1 is the whole token (mask_out's contract); the named groups give the class.
# ⚠️ A hyphen BEFORE a word is allowed on purpose. The first version refused it,
# and the calibration caught "120-second" missing; "top-three" and "top-3" style
# prose would have been dropped silently with it. A hyphenated multi-word form
# is still one token, because scanning reaches its first word first.
RE_WORD = re.compile(
    r"(?<![\w])("
    r"(?P<fold>(?:" + _UNITS + "|" + _TEENS + "|" + _TENS + r"|hundred|thousand)-?fold)"
    r"|(?P<fraction>(?:" + _UNITS + "|" + _TEENS + r")-(?:half|halves|" + _ORD_PLURAL
    + "|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|quarters?))"
    r"|(?P<compound>(?:" + _TENS + ")-(?:" + _UNITS.replace("zero|", "") + "))"
    r"|(?P<ordinal>" + _ORD + "|" + _ORD_PLURAL + ")"
    r"|(?P<mult>" + _MULT + ")"
    r"|(?P<cardinal>" + _UNITS + "|" + _TEENS + "|" + _TENS + "|" + _BIG + ")"
    r")(?![\w])",
    re.IGNORECASE,
)

CLASS_OF = {"fold": "multiplicative", "fraction": "multiplicative", "compound": "cardinal",
            "ordinal": "ordinal", "mult": "multiplicative", "cardinal": "cardinal"}


def token_class(m: re.Match) -> str:
    for g, c in CLASS_OF.items():
        if m.group(g):
            return c
    raise AssertionError(m.group(0))


def extract_text(raw: str, is_tex: bool) -> list[dict]:
    """Kept tokens of one document, after the digit inventory's masks."""
    masked, _ = mask_out(raw, is_tex, token_rx=RE_WORD)
    rows = []
    for m in RE_WORD.finditer(masked):
        ctx = masked[max(0, m.start() - 80): m.end() + 80].replace("\n", " ")
        rows.append({"line": masked.count("\n", 0, m.start()) + 1, "word": m.group(1),
                     "class": token_class(m), "context": re.sub(r"\s+", " ", ctx).strip()})
    return rows


def recall(raw: str, is_tex: bool) -> tuple[dict, list[dict]]:
    cost: dict[str, int] = {}
    removed: list[dict] = []
    masked, _ = mask_out(raw, is_tex, literal_cost=cost, removed=removed, token_rx=RE_WORD)
    n_raw = len(RE_WORD.findall(raw))
    n_kept = len(RE_WORD.findall(masked))
    return ({"tokens_in_raw_text": n_raw, "tokens_kept": n_kept, "tokens_masked": n_raw - n_kept,
             "masked_per_rule": dict(sorted(cost.items(), key=lambda kv: -kv[1])),
             "accounting_closes": n_raw - n_kept == len(removed)}, removed)


# (kind, text, expected kept tokens as (word, class) in order)
SELF_TEST = [
    ("md", "all eleven passed with zero violations", [("eleven", "cardinal"), ("zero", "cardinal")]),
    ("md", "three of the four pairs there", [("three", "cardinal"), ("four", "cardinal")]),
    ("tex", "someone alone, a tone, a bone, money, phone, done, often, weight", []),
    ("tex", "a five-fold increase and a tenfold one", [("five-fold", "multiplicative"),
                                                       ("tenfold", "multiplicative"),
                                                       ("one", "cardinal")]),
    ("tex", "twenty-four hours", [("twenty-four", "cardinal")]),
    ("tex", "two-thirds of runs, one-half of cells", [("two-thirds", "multiplicative"),
                                                      ("one-half", "multiplicative")]),
    ("tex", "the sixteenth cell and the first two", [("sixteenth", "ordinal"), ("first", "ordinal"),
                                                     ("two", "cardinal")]),
    ("tex", "a two-sided test, one-at-a-time", [("two", "cardinal"), ("one", "cardinal")]),
    ("tex", "kept % three in a comment\nnext", []),
    ("tex", "the top-three inputs of a non-zero cell", [("three", "cardinal"), ("zero", "cardinal")]),
    ("tex", r"50\% of two runs", [("two", "cardinal")]),
    ("tex", r"\label{sec:two-regimes} Two regimes \cite[Ch.~one]{x}", [("Two", "cardinal")]),
    ("md", "`two cells` in code, then three outside", [("three", "cardinal")]),
    ("md", "```python\nfour = 4\n```\nfive", [("five", "cardinal")]),
    ("md", "```{=latex}\nTwo & three \\\\\n```", [("Two", "cardinal"), ("three", "cardinal")]),
    ("md", "[four](https://example.org/four-six)", [("four", "cardinal")]),
    ("md", "120-second window, twice", [("second", "ordinal"), ("twice", "multiplicative")]),
    ("md", "S1_two_cells and one_at a", []),
]


def self_test() -> tuple[int, int]:
    bad = 0
    print("## Number-word extractor calibration\n")
    print("| probe | expected | observed | verdict |")
    print("|---|---|---|---|")
    for kind, text, want in SELF_TEST:
        got = [(r["word"], r["class"]) for r in extract_text(text, kind == "tex")]
        ok = got == want
        bad += 0 if ok else 1
        print(f"| `{text[:60]!r}` ({kind}) | {want} | {got} | {'PASS' if ok else '**FAIL**'} |")
    # Line numbers survive a multi-line mask (mask_out keeps newlines).
    rows = extract_text("a\n% two\nb\nseven", True)
    ok = [(r["word"], r["line"]) for r in rows] == [("seven", 4)]
    bad += 0 if ok else 1
    print(f"| line number after a masked comment | [('seven', 4)] | "
          f"{[(r['word'], r['line']) for r in rows]} | {'PASS' if ok else '**FAIL**'} |")
    n = len(SELF_TEST) + 1
    print(f"\n**Calibration:** {n} probes, {bad} FAIL.\n")
    return bad, n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    n_fail, n_probes = self_test()
    if args.self_test or n_fail:
        return 1 if n_fail else 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    kept_rows, masked_rows, per_doc = [], [], {}
    for name, path in ARTEFACTS.items():
        raw = path.read_text(encoding="utf-8")
        is_tex = path.suffix == ".tex"
        rows = extract_text(raw, is_tex)
        rec, removed = recall(raw, is_tex)
        if not rec["accounting_closes"] or rec["tokens_kept"] != len(rows):
            print(f"recall accounting does not close for {name}: {rec}", file=sys.stderr)
            return 1
        kept_rows += [{"artefact": name, **r} for r in rows]
        masked_rows += [{"artefact": name, "rule": r["rule"], "line": r["line"],
                         "word": r["literal"], "context": r["context"]} for r in removed]
        per_doc[name] = {"path": str(path.relative_to(REPO)).replace("\\", "/"),
                         "kept_per_class": dict(sorted(Counter(r["class"] for r in rows).items())),
                         "kept_per_word": dict(sorted(Counter(r["word"].lower() for r in rows).items())),
                         "lines_with_a_kept_token": len({r["line"] for r in rows}),
                         "recall": rec}

    with open(OUT_DIR / "number_words.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["artefact", "line", "word", "class", "context"])
        w.writeheader()
        w.writerows(kept_rows)
    with open(OUT_DIR / "number_words_masked.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["artefact", "rule", "line", "word", "context"])
        w.writeheader()
        w.writerows(masked_rows)
    summary = {"calibration": {"probes": n_probes, "failures": n_fail},
               "unit": "one number-word token (see the module docstring)",
               "per_artefact": per_doc,
               "totals": {"kept": len(kept_rows), "masked": len(masked_rows),
                          "kept_per_class": dict(sorted(Counter(r["class"] for r in kept_rows).items()))}}
    (OUT_DIR / "number_words_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
                                                        encoding="utf-8")
    print(f"Wrote number_words.csv ({len(kept_rows)} kept), number_words_masked.csv "
          f"({len(masked_rows)} masked), number_words_summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
