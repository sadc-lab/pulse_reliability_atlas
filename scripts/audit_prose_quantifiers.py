#!/usr/bin/env python3
"""Inventory of the ABSOLUTE PROSE CLAIMS in the three public artefacts.

Why this exists
---------------
`scripts/audit_number_inventory.py` inventories numeric literals; its unit is a
run of digits. `scripts/audit_number_words.py` inventories numbers written in
words. Both of them explicitly exclude quantifiers and determiners, and say so
in their docstrings. So a sentence that asserts something absolute while
carrying no number at all -- "all 20 fell on the male reference body", "no
public map has been published", "every user re-encounters the same limitations"
-- was in no population of the number audit, and no residue, bucket or mask
ever showed one.

That is not a hypothetical gap. Four defects of exactly this shape were
corrected in `c3f94e9` and `64c39d1` (paper abstract, Figure 5 legend, two
literature universals), and every one of them was found by reading a nearby
sentence, not by enumeration. This inventory is the enumeration.

It inventories, it does not verify. The verdicts live in
`audit/number_inventory.md` §12.

THE POPULATION, DEFINED BEFORE ANYTHING IS COUNTED
---------------------------------------------------
A token is IN the population when it matches one of the stem families below,
case-insensitively, on word boundaries. The families are grouped only to make
the list readable; the unit is one matched token.

  universal      all, every, everything, everyone, each, any, anything, both,
                 either, neither, no, none, nothing
  scope          only, most, sole, solely, exclusive(ly), entire(ly), whole,
                 wholly, complete(ly), total(ly), purely, single, alone
  frequency      always, never, invariably, universally, consistently,
                 systematically, uniformly, routinely
  identity       same, identical, unchanged, unaffected, unique
  priority       first
  strength       cannot, impossible, guarantee(s/d), ensure(s/d), prove(s/n/d),
                 inevitably, necessarily, conclusively, definitively,
                 unequivocally, regardless, irrespective
  extent         throughout, everywhere, anywhere, nowhere

A hyphen counts as a word boundary, so "all-male" enters as `all` and
"single-cell" as `single`. That is deliberate and it is the recall-safe side:
"all-male" is precisely the claim shape this instrument exists to find, and it
was written with a hyphen in the paper's own abstract. `audit_number_words.py`
made the same choice for the same reason, after its calibration caught
"120-second" going missing.

NOT in the population, stated so the boundary is explicit: hedged quantities
("some", "several", "few", "many", "often", "typically"), which weaken a claim
rather than make it absolute; comparatives ("more", "less", "higher"), which
are relative by construction and carry their own referent; and the bare modals
"must" and "will", which are frequent enough in method prose ("the file must be
regenerated") that including them would make the population the whole text --
the failure this docstring warns about below. Numbers, in digits or in words,
belong to the two inventories named above and are not re-counted here.

The same masks as the digit inventory are applied, through its `mask_out`
(comments and code, cross-reference machinery, URLs and paths, versions,
typesetting lengths, line references, organisation identifiers, product
versions), so the three instruments see the same rendered text. Every token a
mask removes is written, with its rule and context, to
`prose_quantifiers_masked.csv`, and the books are closed per artefact: tokens
in the raw text = tokens kept + tokens masked.

⚠️ A high count is not a defect count. Most occurrences are grammatical ("no
longer", "the first author", "each panel shows"). The inventory's job is to
make the population finite and enumerable so that every occurrence can be read
and given a verdict; it cannot decide which ones are claims.

Outputs, under results/number_audit/:
  prose_quantifiers.csv          one row per kept token
  prose_quantifiers_masked.csv   one row per masked token
  prose_quantifiers_summary.json counts per artefact and family, recall
                                 accounting, calibration
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter

from audit_number_inventory import ARTEFACTS, OUT_DIR, REPO, mask_out

_UNIVERSAL = ("all|every|everything|everyone|each|anything|any|both|either|neither|"
              "none|nothing|no")
_SCOPE = ("only|most|solely|sole|exclusively|exclusive|entirely|entire|wholly|whole|"
          "completely|complete|totally|total|purely|single|alone")
_FREQUENCY = ("always|never|invariably|universally|consistently|systematically|"
              "uniformly|routinely")
_IDENTITY = "same|identical|unchanged|unaffected|unique"
_PRIORITY = "first"
_STRENGTH = ("cannot|impossible|guarantees|guaranteed|guarantee|ensures|ensured|ensure|"
             "proven|proves|proved|prove|inevitably|necessarily|conclusively|"
             "definitively|unequivocally|regardless|irrespective")
_EXTENT = "throughout|everywhere|anywhere|nowhere"

# Order matters: at one position Python takes the FIRST alternative that
# matches, so every longer form comes before the shorter one it contains
# ("everything" before "every", "none" before "no", "entirely" before "entire").
# Group 1 is the whole token, which is `mask_out`'s contract.
RE_QUANT = re.compile(
    r"(?<![\w])("
    r"(?P<universal>" + _UNIVERSAL + ")"
    r"|(?P<scope>" + _SCOPE + ")"
    r"|(?P<frequency>" + _FREQUENCY + ")"
    r"|(?P<identity>" + _IDENTITY + ")"
    r"|(?P<priority>" + _PRIORITY + ")"
    r"|(?P<strength>" + _STRENGTH + ")"
    r"|(?P<extent>" + _EXTENT + ")"
    r")(?![\w])",
    re.IGNORECASE,
)

FAMILIES = ("universal", "scope", "frequency", "identity", "priority", "strength", "extent")


def token_family(m: re.Match) -> str:
    for f in FAMILIES:
        if m.group(f):
            return f
    raise AssertionError(m.group(0))


def extract_text(raw: str, is_tex: bool) -> list[dict]:
    """Kept tokens of one document, after the digit inventory's masks."""
    masked, _ = mask_out(raw, is_tex, token_rx=RE_QUANT)
    rows = []
    for m in RE_QUANT.finditer(masked):
        ctx = masked[max(0, m.start() - 110): m.end() + 110].replace("\n", " ")
        rows.append({"line": masked.count("\n", 0, m.start()) + 1, "word": m.group(1),
                     "family": token_family(m), "context": re.sub(r"\s+", " ", ctx).strip()})
    return rows


def recall(raw: str, is_tex: bool) -> tuple[dict, list[dict]]:
    cost: dict[str, int] = {}
    removed: list[dict] = []
    masked, _ = mask_out(raw, is_tex, literal_cost=cost, removed=removed, token_rx=RE_QUANT)
    n_raw = len(RE_QUANT.findall(raw))
    n_kept = len(RE_QUANT.findall(masked))
    return ({"tokens_in_raw_text": n_raw, "tokens_kept": n_kept, "tokens_masked": n_raw - n_kept,
             "masked_per_rule": dict(sorted(cost.items(), key=lambda kv: -kv[1])),
             "accounting_closes": n_raw - n_kept == len(removed)}, removed)


# (kind, text, expected kept tokens as (word, family) in order)
SELF_TEST = [
    # The four defect shapes this instrument exists to enumerate.
    ("tex", "all 20 fell on the male reference body", [("all", "universal")]),
    ("tex", "no public map has been published", [("no", "universal")]),
    ("md", "every user re-encounters the same limitations",
     [("every", "universal"), ("same", "identity")]),
    ("tex", "the first open reliability atlas", [("first", "priority")]),
    # Longest alternative wins at a position; a stem is never double-counted.
    ("tex", "none of them, and no other", [("none", "universal"), ("no", "universal")]),
    ("tex", "everything and every one", [("everything", "universal"), ("every", "universal")]),
    ("tex", "entirely and entire", [("entirely", "scope"), ("entire", "scope")]),
    ("tex", "exclusively exclusive solely sole",
     [("exclusively", "scope"), ("exclusive", "scope"), ("solely", "scope"), ("sole", "scope")]),
    # Substrings of a longer word are NOT tokens. "nonetheless" contains "none",
    # "allocate" contains "all", "firstly" contains "first", "management" -- none
    # of them may match, or the population is the whole prose.
    ("tex", "nonetheless allocate firstly management wholesale noise",
     []),
    # A hyphen is a word boundary, on purpose and on the recall-safe side: the
    # paper's own abstract writes the universal claim as "all-male", so a rule
    # that refused a hyphen would miss the exact defect shape this instrument
    # exists to find. The first version of this file refused it, and this probe
    # is what the decision was reversed against.
    ("tex", "an all-male result in a single-cell regime",
     [("all", "universal"), ("single", "scope")]),
    # Masks: the three instruments must see the same rendered text.
    ("tex", "kept % every in a comment\nnext all", [("all", "universal")]),
    ("tex", r"\label{sec:all-regimes} All regimes \cite[every]{x}", [("All", "universal")]),
    ("md", "`no cells` in code, then none outside", [("none", "universal")]),
    ("md", "```python\nall = 1\n```\nevery", [("every", "universal")]),
    ("md", "[all](https://example.org/all-six)", [("all", "universal")]),
    # Case is not information here; the reading decides, the pattern does not.
    ("tex", "All ALWAYS Never", [("All", "universal"), ("ALWAYS", "frequency"),
                                 ("Never", "frequency")]),
    # Hedges and comparatives are OUT of the population, by decision.
    ("tex", "some several few many often typically more less higher", []),
    # Strength family, including the inflections.
    ("tex", "cannot guarantee that it ensures proven results",
     [("cannot", "strength"), ("guarantee", "strength"), ("ensures", "strength"),
      ("proven", "strength")]),
    # The bare modals are OUT, by the decision recorded in the docstring; the
    # absolutes that travel with them are IN.
    ("tex", "it must hold and will necessarily apply throughout, regardless",
     [("necessarily", "strength"), ("throughout", "extent"), ("regardless", "strength")]),
]


def self_test() -> tuple[int, int]:
    bad = 0
    print("## Absolute-prose extractor calibration\n")
    print("| probe | expected | observed | verdict |")
    print("|---|---|---|---|")
    for kind, text, want in SELF_TEST:
        got = [(r["word"], r["family"]) for r in extract_text(text, kind == "tex")]
        ok = got == want
        bad += 0 if ok else 1
        print(f"| `{text[:60]!r}` ({kind}) | {want} | {got} | {'PASS' if ok else '**FAIL**'} |")
    # Line numbers survive a multi-line mask (mask_out keeps newlines).
    rows = extract_text("a\n% every\nb\nnever", True)
    ok = [(r["word"], r["line"]) for r in rows] == [("never", 4)]
    bad += 0 if ok else 1
    print(f"| line number after a masked comment | [('never', 4)] | "
          f"{[(r['word'], r['line']) for r in rows]} | {'PASS' if ok else '**FAIL**'} |")
    n = len(SELF_TEST) + 1
    print(f"\n**Calibration:** {n} probes, {bad} FAIL.\n")
    return bad, n


def dump(artefact: str, words: list[str] | None, start: int, count: int) -> int:
    """Print kept rows for reading, straight from the producer's own output.

    ⚠️ This exists so that no reading pass ever parses `prose_quantifiers.csv`
    with `cut` or `awk`. The context column carries commas; three successive
    ad-hoc `grep | cut | uniq` passes miscounted the supplement's residue in the
    number audit for exactly that reason (audit/number_inventory.md §10).
    """
    path = OUT_DIR / "prose_quantifiers.csv"
    if not path.exists():
        print(f"{path} does not exist; run without --dump first", file=sys.stderr)
        return 1
    # ⚠️ The monograph carries mu, section signs and en-dashes. On a Windows
    # console Python defaults to cp1252 and a dump of it dies mid-row with
    # UnicodeEncodeError -- after printing part of the population, which is the
    # dangerous shape: a truncated reading pass looks like a completed one.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    with open(path, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f)
                if r["artefact"] == artefact
                and (words is None or r["word"].lower() in words)]
    shown = rows[start: start + count] if count else rows[start:]
    for i, r in enumerate(shown, start=start + 1):
        print(f"[{i}/{len(rows)}] {r['artefact']}:{r['line']} <{r['word']}> ({r['family']})\n"
              f"    {r['context']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--dump", metavar="ARTEFACT", choices=sorted(ARTEFACTS),
                    help="print kept rows of one artefact for reading")
    ap.add_argument("--word", action="append", metavar="STEM",
                    help="restrict --dump to this stem (repeatable)")
    ap.add_argument("--start", type=int, default=0, help="--dump: skip this many rows")
    ap.add_argument("--count", type=int, default=0, help="--dump: print at most this many rows")
    args = ap.parse_args()
    if args.dump:
        return dump(args.dump, [w.lower() for w in args.word] if args.word else None,
                    args.start, args.count)
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
                         "kept_per_family": dict(sorted(Counter(r["family"] for r in rows).items())),
                         "kept_per_word": dict(sorted(Counter(r["word"].lower() for r in rows).items())),
                         "lines_with_a_kept_token": len({r["line"] for r in rows}),
                         "recall": rec}

    with open(OUT_DIR / "prose_quantifiers.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["artefact", "line", "word", "family", "context"])
        w.writeheader()
        w.writerows(kept_rows)
    with open(OUT_DIR / "prose_quantifiers_masked.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["artefact", "rule", "line", "word", "context"])
        w.writeheader()
        w.writerows(masked_rows)
    summary = {"calibration": {"probes": n_probes, "failures": n_fail},
               "unit": "one absolute-prose token (see the module docstring)",
               "per_artefact": per_doc,
               "totals": {"kept": len(kept_rows), "masked": len(masked_rows),
                          "kept_per_family": dict(sorted(Counter(r["family"] for r in kept_rows).items()))}}
    (OUT_DIR / "prose_quantifiers_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote prose_quantifiers.csv ({len(kept_rows)} kept), "
          f"prose_quantifiers_masked.csv ({len(masked_rows)} masked), "
          f"prose_quantifiers_summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
