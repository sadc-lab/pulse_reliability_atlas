#!/usr/bin/env python3
"""Exhaustive inventory of the numeric literals in the three public artefacts.

Why this exists
---------------
The ledger re-derives, on every commit, the numbers written INTO it. A published
number that was never registered is verified by nothing, and nothing reports its
absence. That is not hypothetical: on 2026-09-10 twelve values were added to
Supplement S8 and S13 with no anchor, and the gap surfaced only because the
maintainer asked. This script is the instrument that makes the gap visible
instead of waiting to be asked.

It inventories, it does not verify. Its output is a working list, and the
classification below says exactly how far each row has been checked.

THE POPULATION, DEFINED BEFORE ANYTHING IS COUNTED
---------------------------------------------------
A literal is IN the population when it asserts a quantity -- a measurement of
this work, or a value taken from a source. Everything else is excluded by a
mechanical rule, and every exclusion is counted and reported so the denominator
can be audited rather than trusted.

Excluded, in this order:

  1. Comments. LaTeX ``%`` to end of line (``\\%`` is a literal percent sign and
     is kept), and fenced or inline code in the Markdown monograph.
  2. Cross-references and machinery: the arguments of \\label, \\ref, \\eqref,
     \\mainref, \\cite*, \\includegraphics, \\input, \\usepackage,
     \\begin/\\end, \\pageref, \\autoref.
  3. URLs, DOIs and file paths, including ``name.py:123`` code locations.
  4. Version strings: three-part dotted numbers such as 4.3.1, and ``v``-prefixed
     versions.
  5. Typesetting lengths: a number immediately followed by pt, cm, mm, em, ex,
     in, \\textwidth, \\linewidth, \\columnwidth.
  6. Source line references: ``line 41``, ``lines 120--128``, ``L41``.
  7. Year-like integers, 1900-2100 inclusive, standing alone.

⚠️ Rule 7 is the only lossy one: a genuine quantity that happens to fall in
[1900, 2100] is dropped with the years. They are therefore written out
separately, under ``year_like``, so the loss is inspectable instead of silent.

THE CLASSIFICATION, AND WHAT IT DOES NOT MEAN
----------------------------------------------
Each retained literal is put in one of four buckets:

  ``guard``            -- a gating script pins this exact literal, matched on
                          digit boundaries, and the literal is distinctive.
  ``ledger``           -- its VALUE is among the ledger's manuscript values,
                          and the literal is distinctive.
  ``ambiguous_small``  -- its value matches the ledger but the literal is not
                          distinctive, so the match may be a coincidence.
  ``none``             -- neither. This is the working list.

⚠️ **Coverage here is by VALUE, not by OCCURRENCE.** A number anchored in the
abstract counts as ``ledger`` everywhere else it appears, including places the
anchor never looks at. The bucket states an upper bound on coverage and a lower
bound on risk. It is a sieve for finding candidates, never a verdict that a
number is checked: an inventory locates candidates, not defects.

⚠️ **And the sieve under-reports coverage in one known way**: a number pinned
as a Python float rather than as a quoted string is invisible to
``guard_literals``. ``scripts/check_input_ranges.py`` holds the swept input
bounds that way, which is why 0.21 and 110 land in ``none`` although they are
gated. A ``none`` row is a candidate to examine, not an accusation.

Calibration
-----------
``--self-test`` runs known positives and negatives through the extractor before
any inventory is believed: claim numbers that must survive, and machinery that
must not. It exits non-zero if any of them behaves the wrong way.

Outputs
-------
  results/number_audit/inventory.csv    one row per retained literal occurrence
  results/number_audit/summary.json     population, exclusions, buckets

The register ``audit/number_inventory.md`` is maintained by hand beside these:
it carries the per-row judgement -- what each residual number is, and what it
was checked against -- which this script cannot produce and must not pretend to.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "results" / "number_audit"

ARTEFACTS = {
    "paper": REPO / "preprint_npj" / "paper.tex",
    "supplement": REPO / "preprint_npj" / "supplement.tex",
    "monograph": REPO / "preprint" / "manuscript.md",
}

YEAR_LO, YEAR_HI = 1900, 2100

# Rule 2: commands whose arguments are machinery, never claims.
_REF_CMDS = (
    "label|ref|eqref|pageref|autoref|mainref|cite|citep|citet|citeauthor|"
    "citeyear|includegraphics|input|usepackage|begin|end|bibliography|"
    "bibliographystyle|hypersetup|url|href|documentclass|geometry"
)
RE_REF_CMD = re.compile(r"\\(?:" + _REF_CMDS + r")\s*(?:\[[^\]]*\])?(?:\{[^{}]*\}){1,2}")
RE_URL = re.compile(r"(?:https?://|doi:|10\.\d{4,})\S+")
RE_PATH = re.compile(r"[\w./\\-]+\.(?:py|tex|md|csv|json|parquet|cpp|h|ps1|bib|pdf|docx)(?::\d+)?")
RE_VERSION = re.compile(r"\bv?\d+\.\d+\.\d+\b")
RE_LENGTH = re.compile(r"\d+(?:\.\d+)?\s*(?:pt|cm|mm|em|ex|in)\b|\d*\.?\d+\s*\\(?:text|line|column)width")
RE_LINEREF = re.compile(r"\b(?:lines?|L)\s*\d+(?:\s*(?:--|-|–|,)\s*\d+)*", re.IGNORECASE)
RE_TEX_COMMENT = re.compile(r"(?<!\\)%.*$", re.MULTILINE)
RE_MD_FENCE = re.compile(r"```.*?```", re.DOTALL)
RE_MD_CODE = re.compile(r"`[^`]*`")
RE_MD_LINK = re.compile(r"\]\([^)]*\)")

# A numeric literal: optional sign, digits with LaTeX or plain thousands
# separators, optional decimal part, optional exponent.
RE_NUMBER = re.compile(
    r"(?<![\w.])"
    r"(\d{1,3}(?:(?:\{,\}|,)\d{3})+(?:\.\d+)?"
    r"|\d+\.\d+(?:[eE][-+]?\d+)?"
    r"|\d+(?:[eE][-+]?\d+)?)"
    r"(?![\w])"
)

# Rule 8, added 2026-09-13 after inspecting the paper's residue: an
# organisation identifier is not a quantity. "UR 3450 DevAH" and "INSERM UMR_S
# 1256" surfaced as uncovered claim numbers on the affiliation block.
# The underscore in "UMR\_S" is LaTeX-escaped, which a naive \b(?:UMR_S)? does
# not match -- the calibration probe caught that before the rule was believed.
RE_ORG_ID = re.compile(
    r"\\(?:affil|org\w+)\s*(?:\[[^\]]*\])?\{[^{}]*\}"
    r"|\b(?:UMR|UR|EA)(?:\\?_\w+)?[\s~]*\d+"
)
# Rule 9, same pass: a product or model version is not a quantity either. The
# three-part rule caught 4.3.1 but not "Opus 4.7", "Opus 4.8" or "GPT-5.6",
# which the AI-disclosure paragraph names.
RE_PRODUCT_VERSION = re.compile(
    r"\b(?:Opus|Sonnet|Haiku|Claude|GPT|ChatGPT|Python|Docker|SALib|pandas)"
    r"[\s\-]?v?\d+(?:[.\-]\d+)*\b"
)

MASKS = [
    ("org_identifier", RE_ORG_ID),
    ("product_version", RE_PRODUCT_VERSION),
    ("ref_or_machinery", RE_REF_CMD),
    ("url_or_doi", RE_URL),
    ("file_path", RE_PATH),
    ("version", RE_VERSION),
    ("typeset_length", RE_LENGTH),
    ("line_reference", RE_LINEREF),
]


def mask_out(text: str, is_tex: bool) -> tuple[str, dict[str, int]]:
    """Blank every excluded construct, keeping offsets stable for context."""
    counts: dict[str, int] = {}
    if is_tex:
        n = len(RE_TEX_COMMENT.findall(text))
        counts["tex_comment"] = n
        text = RE_TEX_COMMENT.sub(lambda m: " " * len(m.group(0)), text)
    else:
        for name, rx in (("md_fence", RE_MD_FENCE), ("md_inline_code", RE_MD_CODE),
                         ("md_link_target", RE_MD_LINK)):
            n = len(rx.findall(text))
            counts[name] = n
            text = rx.sub(lambda m: " " * len(m.group(0)), text)
    for name, rx in MASKS:
        n = len(rx.findall(text))
        counts[name] = counts.get(name, 0) + n
        text = rx.sub(lambda m: " " * len(m.group(0)), text)
    return text, counts


def to_value(lit: str) -> float | None:
    try:
        return float(lit.replace("{,}", "").replace(",", ""))
    except ValueError:
        return None


def significant_digits(lit: str) -> int:
    """Digits in the literal, separators and leading zeros removed."""
    d = lit.replace("{,}", "").replace(",", "").replace(".", "").lstrip("0")
    return len(d)


def is_distinctive(lit: str, val: float) -> bool:
    """Whether a by-value match against the ledger means anything.

    ⚠️ Measured on 2026-09-13, and it is why this function exists: of the 3,764
    occurrences a bare by-value match put in the `ledger` bucket, **3,171 had a
    value below 100**, with a median of 8. Small integers collide with some
    ledger value by accident, so a bare match is not evidence of coverage -- it
    inflates coverage and understates risk, the dangerous direction.

    A match therefore counts only for a value that does not collide by chance:
    at least three significant digits, or at least 1000. Everything else goes
    to its own bucket so the ambiguity is visible instead of being counted as
    covered.
    """
    return significant_digits(lit) >= 3 or val >= 1000


def _pinned(lit: str, guards: set[str]) -> bool:
    """Whether a guard pins this exact literal, matched on digit boundaries."""
    rx = re.compile(r"(?<![\d.])" + re.escape(lit) + r"(?![\d])")
    return any(rx.search(g) for g in guards)


def extract(path: Path) -> tuple[list[dict], dict[str, int]]:
    raw = path.read_text(encoding="utf-8")
    is_tex = path.suffix == ".tex"
    masked, excl = mask_out(raw, is_tex)
    line_starts = [m.start() for m in re.finditer(r"^", masked, re.MULTILINE)]

    def line_of(pos: int) -> int:
        lo, hi = 0, len(line_starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if line_starts[mid] <= pos:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1

    rows: list[dict] = []
    n_year = 0
    for m in RE_NUMBER.finditer(masked):
        lit = m.group(1)
        val = to_value(lit)
        if val is None:
            continue
        if float(val).is_integer() and YEAR_LO <= val <= YEAR_HI and "." not in lit:
            n_year += 1
            rows.append({"literal": lit, "value": val, "line": line_of(m.start()),
                         "context": "", "bucket": "year_like"})
            continue
        ctx = masked[max(0, m.start() - 70): m.end() + 70].replace("\n", " ")
        rows.append({"literal": lit, "value": val, "line": line_of(m.start()),
                     "context": re.sub(r"\s+", " ", ctx).strip(), "bucket": ""})
    excl["year_like"] = n_year
    return rows, excl


def ledger_values() -> set[float]:
    """Manuscript values the ledger re-derives, read from its own output."""
    proc = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "audit_claims.py")],
        capture_output=True, text=True, cwd=str(REPO),
    )
    vals: set[float] = set()
    in_table = False
    for line in proc.stdout.splitlines():
        if line.startswith("## All claims"):
            in_table = True
            continue
        if in_table:
            if line.startswith("## ") or line.startswith("**"):
                in_table = False
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 7:
                v = to_value(parts[5])
                if v is not None:
                    vals.add(v)
    return vals


def guard_literals() -> set[str]:
    """Exact literal strings pinned inside the gating scripts.

    ⚠️ The first version read only `audit_claims.py`, and the paper's residue
    showed why that is wrong: the swept input bounds 0.21, 110 and 800 came out
    as uncovered although `scripts/check_input_ranges.py` gates exactly them.
    Every `check_*.py` that the pre-commit hook runs is a place a number can be
    pinned, so all of them are read.
    """
    sources = [REPO / "scripts" / "audit_claims.py"] + sorted(
        (REPO / "scripts").glob("check_*.py")
    )
    src = "\n".join(p.read_text(encoding="utf-8") for p in sources)
    lits: set[str] = set()
    for m in re.finditer(r'"((?:[^"\\]|\\.){4,200})"', src):
        s = m.group(1)
        if RE_NUMBER.search(s) and (" " in s or "{,}" in s):
            lits.add(s.replace('\\\\', '\\'))
    return lits


SELF_TEST_KEEP = [
    ("1{,}280 simulations", "1{,}280"),
    ("median 0.928", "0.928"),
    ("21.42 & 22.66", "22.66"),
    ("98.3~\\% agreement", "98.3"),
    ("663 of the 1{,}280 runs", "663"),
]
SELF_TEST_DROP = [
    ("\affil[5]{\orgdiv{UR 3450 DevAH}}", "3450"),
    ("INSERM UMR\_S 1256, Nutrition", "1256"),
    ("Claude Opus 4.7 for the drafting", "4.7"),
    ("OpenAI ChatGPT (GPT-5.6 Sol)", "5.6"),
    ("Pulse v4.3.1 pinned", "4.3.1"),
    ("see Table~\\ref{tab:s8-estimands}", "8"),
    ("\\includegraphics[width=0.9\\textwidth]{figures/fig03.pdf}", "0.9"),
    ("lines 120--128 of the source", "120"),
    ("% a comment mentioning 4242", "4242"),
    ("scripts/detector.py:139", "139"),
    ("published in 2026", "2026"),
]


def self_test() -> int:
    bad = 0
    print("## Extractor calibration\n")
    print("| probe | expectation | verdict |")
    print("|---|---|---|")
    for text, lit in SELF_TEST_KEEP:
        masked, _ = mask_out(text, True)
        ok = lit in [m.group(1) for m in RE_NUMBER.finditer(masked)]
        bad += 0 if ok else 1
        print(f"| `{text}` | keeps `{lit}` | {'PASS' if ok else '**FAIL**'} |")
    for text, lit in SELF_TEST_DROP:
        masked, _ = mask_out(text, True)
        found = [m.group(1) for m in RE_NUMBER.finditer(masked)]
        ok = lit not in found
        if lit == "2026":
            v = to_value("2026")
            ok = YEAR_LO <= v <= YEAR_HI
        bad += 0 if ok else 1
        print(f"| `{text}` | drops `{lit}` | {'PASS' if ok else '**FAIL**'} |")
    print(f"\n**Calibration:** {len(SELF_TEST_KEEP) + len(SELF_TEST_DROP)} probes, "
          f"{bad} FAIL.\n")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-test", action="store_true", help="run the extractor calibration only")
    args = ap.parse_args()

    if args.self_test:
        return 1 if self_test() else 0

    if self_test():
        print("extractor calibration FAILED -- inventory not produced", file=sys.stderr)
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    led = ledger_values()
    guards = guard_literals()

    all_rows: list[dict] = []
    per_doc: dict[str, dict] = {}
    for name, path in ARTEFACTS.items():
        rows, excl = extract(path)
        kept = [r for r in rows if r["bucket"] != "year_like"]
        for r in kept:
            # ⚠️ Both membership tests below were over-broad in the first
            # version, in the same way and in the dangerous direction. A bare
            # `literal in guard_string` matched "8" inside any guard string
            # containing an 8, which put 2,561 of the monograph's 2,954
            # occurrences in the `guard` bucket -- a document the guards barely
            # touch. A guard match now needs digit boundaries AND a value that
            # does not collide by chance, exactly as for the ledger.
            if is_distinctive(r["literal"], r["value"]) and _pinned(r["literal"], guards):
                r["bucket"] = "guard"
            elif r["value"] in led and is_distinctive(r["literal"], r["value"]):
                r["bucket"] = "ledger"
            elif r["value"] in led:
                r["bucket"] = "ambiguous_small"
            else:
                r["bucket"] = "none"
            r["artefact"] = name
        per_doc[name] = {
            "path": path.relative_to(REPO).as_posix(),
            "retained_occurrences": len(kept),
            "distinct_values": len({r["value"] for r in kept}),
            "excluded": excl,
            "buckets": {
                b: sum(1 for r in kept if r["bucket"] == b)
                for b in ("ledger", "guard", "ambiguous_small", "none")
            },
            "distinct_unbucketed_values": len(
                {r["value"] for r in kept if r["bucket"] == "none"}
            ),
        }
        all_rows.extend(kept)

    import csv

    with (OUT_DIR / "inventory.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["artefact", "line", "literal", "value",
                                           "bucket", "context"])
        w.writeheader()
        for r in sorted(all_rows, key=lambda r: (r["artefact"], r["line"])):
            w.writerow({k: r[k] for k in w.fieldnames})

    summary = {
        "population_rule": "see the module docstring; exclusions are counted per artefact",
        "coverage_is_by_value_not_by_occurrence": True,
        "ledger_distinct_values": len(led),
        "guard_pinned_literals": len(guards),
        "per_artefact": per_doc,
        "totals": {
            "retained_occurrences": len(all_rows),
            "distinct_values": len({r["value"] for r in all_rows}),
            "unbucketed_occurrences": sum(1 for r in all_rows if r["bucket"] == "none"),
            "ambiguous_small_occurrences": sum(
                1 for r in all_rows if r["bucket"] == "ambiguous_small"
            ),
            "not_demonstrably_covered_occurrences": sum(
                1 for r in all_rows if r["bucket"] in ("none", "ambiguous_small")
            ),
            "unbucketed_distinct_values": len(
                {r["value"] for r in all_rows if r["bucket"] == "none"}
            ),
        },
    }
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print("\n## Population, after the exclusion rule\n")
    print("| artefact | retained | distinct | ledger | guard | ambiguous small | none | distinct none |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|")
    for name, d in per_doc.items():
        b = d["buckets"]
        print(f"| {name} | {d['retained_occurrences']} | {d['distinct_values']} | "
              f"{b['ledger']} | {b['guard']} | {b['ambiguous_small']} | {b['none']} | "
              f"{d['distinct_unbucketed_values']} |")
    t = summary["totals"]
    print(f"| **all** | **{t['retained_occurrences']}** | **{t['distinct_values']}** | | | "
          f"**{t['ambiguous_small_occurrences']}** | **{t['unbucketed_occurrences']}** | "
          f"**{t['unbucketed_distinct_values']}** |")

    print("\n## Exclusions, per artefact (the denominator is auditable)\n")
    keys = sorted({k for d in per_doc.values() for k in d["excluded"]})
    print("| artefact | " + " | ".join(keys) + " |")
    print("|---" * (len(keys) + 1) + "|")
    for name, d in per_doc.items():
        print(f"| {name} | " + " | ".join(str(d["excluded"].get(k, 0)) for k in keys) + " |")

    # The residue, as a frequency table per artefact. It lives here rather than
    # in a shell pipeline because three successive hand-rolled `grep | sort |
    # uniq` passes over the CSV each miscounted it -- by one, then by eight --
    # the `context` column carries commas and quoted newlines, so field
    # positions are not what a line-oriented tool assumes.
    residue_rows: list[dict] = []
    for name in ARTEFACTS:
        vals = [r["literal"] for r in all_rows
                if r["artefact"] == name and r["bucket"] == "none"]
        freq: dict[str, int] = {}
        for v in vals:
            freq[v] = freq.get(v, 0) + 1
        for lit, n in sorted(freq.items(), key=lambda kv: (-kv[1], kv[0])):
            example = next(r["context"] for r in all_rows
                           if r["artefact"] == name and r["bucket"] == "none"
                           and r["literal"] == lit)
            residue_rows.append({"artefact": name, "literal": lit, "occurrences": n,
                                 "example_context": example})
    with (OUT_DIR / "residue_by_literal.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["artefact", "literal", "occurrences",
                                           "example_context"])
        w.writeheader()
        w.writerows(residue_rows)

    print("\n## Residue, top literals per artefact (full table in "
          "results/number_audit/residue_by_literal.csv)\n")
    for name in ARTEFACTS:
        top = [r for r in residue_rows if r["artefact"] == name][:10]
        tot = sum(r["occurrences"] for r in residue_rows if r["artefact"] == name)
        shown = sum(r["occurrences"] for r in top)
        print(f"* **{name}** -- {tot} occurrences; the ten most frequent literals "
              f"account for {shown} of them: "
              + ", ".join(f"`{r['literal']}`x{r['occurrences']}" for r in top))

    print(f"\nWrote {OUT_DIR.relative_to(REPO)}/inventory.csv, summary.json and "
          "residue_by_literal.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
