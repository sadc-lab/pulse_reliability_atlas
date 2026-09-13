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
     is kept), and code in the Markdown monograph -- fenced or inline.
     ⚠️ A pandoc RAW block, ```` ```{=latex} ````, is **content, not code**: the
     monograph renders several published tables that way, and masking them cost
     301 literals including the atlas's per-cell flag breakdown. Raw blocks are
     kept; only their delimiters are blanked, because leaving the backticks in
     place lets the inline-code rule pair across the block and mask it anyway.
  2. Cross-references and machinery: the arguments of \\label, \\ref, \\eqref,
     \\mainref, \\cite*, \\includegraphics, \\input, \\usepackage,
     \\begin/\\end, \\pageref, \\autoref.
  3. URLs, DOIs and file paths, including ``name.py:123`` code locations.
  4. Version strings: three-part dotted numbers such as 4.3.1, and ``v``-prefixed
     versions.
  5. Typesetting lengths: a number with its unit GLUED to it (0.5cm, 2em, 12pt),
     or a fraction of \\textwidth / \\linewidth / \\columnwidth. A space between
     number and unit is prose, not a length: "163 cm" is a body height, and
     "160 in moderate ARDS" is a count. (Corrected 2026-09-13; see RE_LENGTH.)
  6. Source line references: ``line 41``, ``lines 120--128``, ``L41``.
  7. Year-like integers: exactly four bare digits, 1900-2100 inclusive. A
     thousands-separated count ("2{,}000", "2,000") is NOT a year.

⚠️ Rule 7 is the only lossy one: a genuine quantity written as four bare digits
in [1900, 2100] is dropped with the years. Every such row is therefore written
to ``masked_by_rule.csv`` under rule ``year_like``, with its context, so the
loss is inspectable instead of silent. (Until 2026-09-13 this paragraph claimed
that already, while the rows were only counted and written nowhere.)

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
# ⚠️ Corrected 2026-09-13 after an ultrareview finding. The first version let
# whitespace sit between the number and the unit and listed the English word
# "in" as a unit, so it masked prose: "144 of 160 in moderate", "0.6 in every
# draw", and body heights "163 cm", "176.2 cm". 110 literals were dropped, some
# of them from the paper, whose row-by-row audit was therefore run on an
# incomplete population. A typesetting length is now matched only when the
# unit is glued to the number, which is how LaTeX writes one (0.5cm, 2em); a
# number kept by mistake shows up in the residue, a number dropped by mistake
# never shows up anywhere, so the rule errs towards keeping.
RE_LENGTH = re.compile(
    r"(?<![\w.])\d*\.?\d+(?:pt|cm|mm|em|ex|in|bp|pc)\b"
    r"|\d*\.?\d+\s*\\(?:text|line|column)(?:width|height)"
)
RE_LINEREF = re.compile(r"\b(?:lines?|L)\s*\d+(?:\s*(?:--|-|–|,)\s*\d+)*", re.IGNORECASE)
RE_TEX_COMMENT = re.compile(r"(?<!\\)%.*$", re.MULTILINE)
# ⚠️ A fence is not automatically code. The monograph renders several published
# tables as pandoc RAW blocks, ```{=latex} ... ```, and the first version of
# this rule masked them wholesale: 301 literals vanished from the monograph's
# inventory, including the per-cell flag breakdown ("S1\_M & 160 & 0 & 4 & 11 &
# 107 & 49"), which is the atlas's core reliability table. Only a real code
# fence is masked; a raw-format block is content and stays.
RE_MD_FENCE = re.compile(r"```(?P<info>[^\n]*)\n(?P<body>.*?)```", re.DOTALL)
RAW_BLOCK_INFO = re.compile(r"^\s*\{=")


def _blank(s: str) -> str:
    """Replace every character with a space EXCEPT newlines.

    ⚠️ Corrected 2026-09-13 after an ultrareview finding. Masks used to replace
    a whole match with spaces, newlines included, so every multi-line mask
    removed lines from the text and every line number reported after it was
    wrong -- measured at +36 by line 1577 of the monograph and +58 by line 4591.
    A line-number column that silently drifts is worse than none: it sends the
    reader to the wrong sentence. Keeping the newlines keeps both the offsets
    and the line numbers exact.
    """
    return re.sub(r"[^\n]", " ", s)


def _mask_code_fence(m: re.Match) -> str:
    """Blank a code fence; keep a raw-format block's body, never its markers.

    ⚠️ Keeping the whole match for a raw block is not enough, and the
    calibration probe caught it: the ``` delimiters would survive, and the
    inline-code rule that runs next pairs backticks left to right, so it would
    span the block and mask the body anyway. The markers are therefore blanked
    and only the body kept. Lengths AND newlines are preserved.
    """
    if RAW_BLOCK_INFO.match(m.group("info")):
        head = _blank("```" + m.group("info")) + "\n"
        return head + m.group("body") + "   "
    return _blank(m.group(0))
RE_MD_CODE = re.compile(r"`[^`]*`")
RE_MD_LINK = re.compile(r"\]\([^)]*\)")

# A numeric literal: optional sign, digits with LaTeX or plain thousands
# separators, optional decimal part, optional exponent.
# ⚠️ The trailing guard used to be a bare (?![\w]), which rejects a number glued
# to letters -- so "the 95th percentile", "50th-percentile weight" and
# "5--10x real time" produced NO literal at all. That loss is invisible to the
# closed recall accounting, because the same pattern counts both the raw and
# the masked text: a literal this pattern cannot see disappears from both sides
# and the books still close. Found 2026-09-13 by reading, not by a check. An
# ordinal suffix (st, nd, rd, th) or a multiplier (x) is now allowed to follow;
# other glued letters -- hashes like 3b18bdc, CPU models, figure panels like
# 4a -- are still rejected, and those are not quantities.
RE_NUMBER = re.compile(
    r"(?<![\w.])"
    r"(\d{1,3}(?:(?:\{,\}|,)\d{3})+(?:\.\d+)?"
    r"|\d+\.\d+(?:[eE][-+]?\d+)?"
    r"|\d+(?:[eE][-+]?\d+)?)"
    r"(?=(?:st|nd|rd|th|x)\b|[^\w]|$)"
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


def mask_out(text: str, is_tex: bool, literal_cost: dict[str, int] | None = None,
             removed: list[dict] | None = None) -> tuple[str, dict[str, int]]:
    """Blank every excluded construct, keeping offsets stable for context.

    `literal_cost`, when supplied, receives how many numeric literals each rule
    removes. ⚠️ That is the number that matters, not the span count: a rule can
    match hundreds of spans and cost nothing, or match nine and swallow a
    paragraph of claims. The span count alone cannot tell the two apart, and
    reading it as if it could is how an over-broad rule stays invisible.
    """
    counts: dict[str, int] = {}

    def apply(name: str, rx: re.Pattern, s: str) -> str:
        n = len(rx.findall(s))
        counts[name] = counts.get(name, 0) + n
        spans_before = {m.start(): m.group(1) for m in RE_NUMBER.finditer(s)}
        repl = _mask_code_fence if name == "md_fence" else (
            lambda m: _blank(m.group(0)))
        new = rx.sub(repl, s)
        spans_after = {m.start() for m in RE_NUMBER.finditer(new)}
        lost = sorted(set(spans_before) - spans_after)
        if literal_cost is not None:
            literal_cost[name] = literal_cost.get(name, 0) + len(lost)
        # Which literals, not just how many. Offsets are preserved by _blank, so
        # a literal is lost exactly when its start offset no longer begins a
        # number. The context is taken from the text BEFORE this rule ran.
        if removed is not None:
            for pos in lost:
                removed.append({
                    "rule": name,
                    "literal": spans_before[pos],
                    "line": s.count("\n", 0, pos) + 1,
                    "context": re.sub(r"\s+", " ", s[max(0, pos - 60): pos + 60]).strip(),
                })
        return new

    if is_tex:
        text = apply("tex_comment", RE_TEX_COMMENT, text)
    else:
        for name, rx in (("md_fence", RE_MD_FENCE), ("md_inline_code", RE_MD_CODE),
                         ("md_link_target", RE_MD_LINK)):
            text = apply(name, rx, text)
    for name, rx in MASKS:
        text = apply(name, rx, text)
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


def recall_accounting(path: Path) -> dict:
    """Closed accounting: every literal in the raw text lands somewhere.

    ⚠️ Why this exists. The calibration probes test PRECISION -- that machinery
    is not mistaken for a claim. They say nothing about RECALL, and a literal
    that never enters the inventory at all is the dangerous failure: it cannot
    appear in any residue, so it is invisible rather than uncovered.

    This counts the literals in the raw text, then the literals that survive
    masking, and requires the difference to equal what the masks removed. If
    the two sides do not close, a literal is disappearing somewhere the
    exclusion table does not describe.
    """
    raw = path.read_text(encoding="utf-8")
    is_tex = path.suffix == ".tex"
    cost: dict[str, int] = {}
    removed: list[dict] = []
    masked, _ = mask_out(raw, is_tex, literal_cost=cost, removed=removed)
    n_raw = len(RE_NUMBER.findall(raw))
    n_masked = len(RE_NUMBER.findall(masked))
    return {
        "literals_in_raw_text": n_raw,
        "literals_after_masking": n_masked,
        "removed_by_masks": n_raw - n_masked,
        "literals_removed_per_rule": dict(sorted(cost.items(), key=lambda kv: -kv[1])),
        "removed_literals": removed,
    }


def is_year_like(lit: str, val: float) -> bool:
    """Rule 7: a bare integer in [1900, 2100] is set aside as year-like.

    A function of its own so the calibration probe calls the rule the
    inventory actually applies. ⚠️ The first probe did not: it compared two
    constants (`1900 <= 2026 <= 2100`) and never exercised this path, so it
    could not fail whatever the extractor did -- an ultrareview finding.

    ⚠️ Corrected again the same day, after a second ultrareview finding: the rule
    checked the VALUE, so a thousands-separated count such as "2{,}000" or
    "2,000" -- the bootstrap and permutation sizes in all three artefacts,
    including paper.tex:379 "2{,}000 relabellings" -- was read as 2000 and
    discarded as a year. A year is written as four bare digits; nobody writes
    "2,026". The literal must now be exactly that shape.
    """
    return (re.fullmatch(r"\d{4}", lit) is not None
            and YEAR_LO <= val <= YEAR_HI)


def extract(path: Path) -> tuple[list[dict], dict[str, int]]:
    return extract_text(path.read_text(encoding="utf-8"), path.suffix == ".tex")


def extract_text(raw: str, is_tex: bool) -> tuple[list[dict], dict[str, int]]:
    """The whole extraction on a string, so probes run the real code path."""
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
        if is_year_like(lit, val):
            n_year += 1
            # Context is kept: rule 7 is the one lossy rule, and its rows are
            # written to masked_by_rule.csv so a quantity dropped as a "year"
            # can be seen. They used to carry an empty context and be written
            # nowhere, although the docstring promised otherwise.
            yctx = masked[max(0, m.start() - 70): m.end() + 70].replace("\n", " ")
            rows.append({"literal": lit, "value": val, "line": line_of(m.start()),
                         "context": re.sub(r"\s+", " ", yctx).strip(),
                         "bucket": "year_like"})
            continue
        ctx = masked[max(0, m.start() - 70): m.end() + 70].replace("\n", " ")
        rows.append({"literal": lit, "value": val, "line": line_of(m.start()),
                     "context": re.sub(r"\s+", " ", ctx).strip(), "bucket": ""})
    excl["year_like"] = n_year
    return rows, excl


def parse_claims_table(stdout: str) -> tuple[set[float], int]:
    """Manuscript values and claim-row count from audit_claims' "All claims" table.

    ⚠️ Corrected 2026-09-13. The value was read at a fixed position from the
    left, parts[5]. Seven claim texts contain a literal "|" -- "median |EE|
    20.44 ..." in the S3.7 stratification table -- which shifts every column to
    their right, so the parse read "EE" as the value and 20.44, 15.74, 24.94,
    17.26, 20.32, 16.74 and 3 never entered the ledger set.

    The defect was LATENT, and that was measured, not assumed: every one of
    those values is also pinned by a guard, so each was already classified
    `guard` and the residue was identical before and after the fix (1,345
    either way). It would have bitten on the first value covered by the ledger
    alone whose claim text holds a "|". The row still ends
    "| manuscript | computed |", so the value is now read from the RIGHT, where
    its position does not depend on the free-text column.
    """
    vals: set[float] = set()
    n_claim_rows = 0
    in_table = False
    for line in stdout.splitlines():
        if line.startswith("## All claims"):
            in_table = True
            continue
        if in_table:
            if line.startswith("## ") or line.startswith("**"):
                in_table = False
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 7 and parts[1] not in ("claim_id", "") \
                    and not parts[1].startswith("---"):
                n_claim_rows += 1
                v = to_value(parts[-3])
                if v is not None:
                    vals.add(v)
    return vals, n_claim_rows


def validate_ledger_parse(stdout: str, stderr: str, returncode: int
                          ) -> tuple[set[float], dict]:
    """Parse the ledger output and refuse it if the parse is not the ledger.

    ⚠️ Corrected twice on 2026-09-13.

    First, after an ultrareview finding: the return code was never read, so a
    crash in audit_claims.py left the value set empty and every covered number
    fell silently into the working list, with this script still exiting 0. The
    exit code alone cannot separate a crash from a legitimate FAIL (audit_claims
    exits 1 for both), so the check is on what was parsed.

    Second, after a SECOND ultrareview finding against that fix: it compared the
    parsed row count with the DENOMINATOR of "Anchors verified: N / M". But
    audit_claims computes M = N + skipped (audit_claims.py:3857) and its
    "All claims" table prints only the N claims that ran (line 3905). On a clean
    public clone, where the gitignored raw S021 trajectories are absent and one
    anchor is documented as SKIPPED, the headline reads 393 / 394, the table
    holds 393 rows, and the fix refused to produce any inventory at all -- the
    exact supported case it should have accepted. The row count is now compared
    with N. Skipped anchors are not an error, but their values are missing from
    the ledger set, so their count is returned and written to summary.json
    rather than hidden: an inventory built with skipped anchors is labelled so.
    """
    vals, n_claim_rows = parse_claims_table(stdout)
    m = re.search(r"\*\*Anchors verified:\*\*\s*(\d+)\s*/\s*(\d+)", stdout)
    n_run = int(m.group(1)) if m else None
    n_expected = int(m.group(2)) if m else None
    if "Traceback (most recent call last)" in stderr or n_run is None \
            or n_claim_rows != n_run or not vals:
        tail = "\n".join(stderr.strip().splitlines()[-5:])
        raise SystemExit(
            "ledger parse FAILED -- refusing to classify against an incomplete "
            f"ledger (parsed {n_claim_rows} claim rows, headline {n_run} / "
            f"{n_expected}, {len(vals)} values, audit_claims exit {returncode})"
            + (f"\n{tail}" if tail else "")
        )
    info = {
        "anchors_run": n_run,
        "anchors_expected": n_expected,
        "anchors_skipped": n_expected - n_run,
        "claim_rows_parsed": n_claim_rows,
    }
    return vals, info


def ledger_values() -> tuple[set[float], dict]:
    """Manuscript values the ledger re-derives, read from its own output."""
    proc = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "audit_claims.py")],
        capture_output=True, text=True, cwd=str(REPO),
    )
    vals, info = validate_ledger_parse(proc.stdout, proc.stderr, proc.returncode)
    if info["anchors_skipped"]:
        print(f"WARNING: {info['anchors_skipped']} ledger anchor(s) SKIPPED in this "
              "checkout; their values are absent from the ledger set, so this "
              "inventory may differ from one built with every anchor running.",
              file=sys.stderr)
    return vals, info


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


# Calibration probes. Every probe runs the REAL extraction path, extract_text,
# and asserts where one literal lands: "kept" (inventoried), "dropped" (never
# inventoried), "year" (set aside by rule 7), or ("line", N) for the line number
# it is reported on.
#
# ⚠️ Rewritten 2026-09-13 after an ultrareview returned five defects in this
# instrument. The old probes called `mask_out` directly and tested only
# precision -- that machinery is not mistaken for a claim. They could not see a
# claim number dropped by an over-broad mask, a drifting line number, or a year
# rule that was never exercised (the old "2026" probe compared two constants).
# Each of those defects now has a probe that reproduces it and must fail if it
# returns.
SELF_TEST = [
    # -- claim numbers that must be inventoried ------------------------------
    ("tex", "1{,}280 simulations", "1{,}280", "kept"),
    ("tex", "median 0.928", "0.928", "kept"),
    ("tex", "21.42 & 22.66", "22.66", "kept"),
    ("tex", "98.3~\\% agreement", "98.3", "kept"),
    ("tex", "663 of the 1{,}280 runs", "663", "kept"),
    # the RE_LENGTH defect: prose "N in <word>" and "N cm" were masked
    # The literal watched is 160, not 144: the old rule masked the number
    # IMMEDIATELY before "in". A first version of this probe watched 144 and
    # passed against the reinjected defect -- a probe that cannot fail.
    ("tex", "from 144 of 160 in moderate ARDS", "160", "kept"),
    ("tex", "lower bound clears 0.6 in every draw", "0.6", "kept"),
    ("md", "the female body is 163 cm tall", "163", "kept"),
    ("md", "the CDC P50 stature of 176.2 cm", "176.2", "kept"),
    ("tex", "a count of 2150 runs", "2150", "kept"),
    # numbers glued to an ordinal or a multiplier were invisible to BOTH sides
    # of the recall accounting, so the books closed while they were lost
    ("tex", "placed the 95th percentile at 70~mmHg", "95", "kept"),
    ("tex", "runs at about 5--10x real time", "10", "kept"),
    ("md", "exceeding it by 2.4x the budget", "2.4", "kept"),
    ("md", "commit 3b18bdc08660 produced it", "3", "dropped"),
    ("tex", "see Figure~4a of the main text", "4", "dropped"),
    # the fence defect: a pandoc raw-LaTeX block is content
    ("md", "```{=latex}\n\\begin{center} S1 & 160 & 0 \\\\\n```", "160", "kept"),
    # -- machinery that must never be inventoried ----------------------------
    ("md", "```python\nthreshold = 4242\n```", "4242", "dropped"),
    ("tex", "\\affil[5]{\\orgdiv{UR 3450 DevAH}}", "3450", "dropped"),
    ("tex", "INSERM UMR\\_S 1256, Nutrition", "1256", "dropped"),
    ("tex", "Claude Opus 4.7 for the drafting", "4.7", "dropped"),
    ("tex", "OpenAI ChatGPT (GPT-5.6 Sol)", "5.6", "dropped"),
    ("tex", "Pulse v4.3.1 pinned", "4.3.1", "dropped"),
    ("tex", "see Table~\\ref{tab:s8-estimands}", "8", "dropped"),
    ("tex", "\\includegraphics[width=0.9\\textwidth]{figures/fig03.pdf}", "0.9", "dropped"),
    ("tex", "\\vspace{0.5cm} then text", "0.5", "dropped"),
    ("tex", "\\hspace{2em} then text", "2", "dropped"),
    ("tex", "lines 120--128 of the source", "120", "dropped"),
    ("tex", "% a comment mentioning 4242", "4242", "dropped"),
    ("tex", "scripts/detector.py:139", "139", "dropped"),
    # -- the year rule, through the function the inventory applies -----------
    ("tex", "published in 2026", "2026", "year"),
    # a thousands-separated count is not a year (second ultrareview finding)
    ("tex", "with 2{,}000 relabellings the smallest tail", "2{,}000", "kept"),
    ("md", "sub-sampling null (n_null = 2,000 splits)", "2,000", "kept"),
    # -- line numbers after multi-line masks (the newline defect) ------------
    ("md", "line one\n```python\na = 1\nb = 2\n```\nvalue 777 here", "777", ("line", 6)),
    ("md", "intro\n```{=latex}\nrow & 5\n```\nafter 888", "888", ("line", 5)),
    ("tex", "% comment 1\n% comment 2\nnumber 999", "999", ("line", 3)),
]


def self_test() -> tuple[int, int]:
    """Run every probe through extract_text. Returns (failures, probes)."""
    bad = 0
    print("## Extractor calibration\n")
    print("| probe | expectation | observed | verdict |")
    print("|---|---|---|---|")
    for kind, text, lit, expect in SELF_TEST:
        rows, _ = extract_text(text, is_tex=(kind == "tex"))
        hits = [r for r in rows if r["literal"] == lit]
        if expect == "kept":
            observed = "inventoried" if any(r["bucket"] != "year_like" for r in hits) else "absent"
            ok = observed == "inventoried"
        elif expect == "dropped":
            observed = "absent" if not hits else "inventoried"
            ok = not hits
        elif expect == "year":
            observed = "year_like" if any(r["bucket"] == "year_like" for r in hits) else (
                "inventoried" if hits else "absent")
            ok = observed == "year_like"
        else:
            want = expect[1]
            got = hits[0]["line"] if hits else None
            observed = f"line {got}"
            ok = got == want
        bad += 0 if ok else 1
        shown = text.replace("\n", "\\n")
        exp = expect if isinstance(expect, str) else f"line {expect[1]}"
        print(f"| `{shown}` ({kind}) | `{lit}` {exp} | {observed} | "
              f"{'PASS' if ok else '**FAIL**'} |")
    # The ledger parse, on a synthetic table whose second row carries a "|" in
    # its free text -- the exact shape that shifted the columns in the real one.
    table = (
        "## All claims (sorted)\n\n"
        "| claim_id | status | section | text | manuscript | computed |\n"
        "|---|---|---|---|---:|---:|\n"
        "| T.a | PASS | S1 | plain text | 663 | 663 |\n"
        "| T.b | PASS | S3.7 | median |EE| 20.44 for steps | 20.44 | 20.44 |\n"
        "\n**Anchors verified:** 2 / 2\n"
    )
    vals, n_rows = parse_claims_table(table)
    ok = n_rows == 2 and vals == {663.0, 20.44}
    bad += 0 if ok else 1
    print(f"| ledger table with `|EE|` in a claim text | 2 rows, values {{663, 20.44}} | "
          f"{n_rows} rows, values {sorted(vals)} | {'PASS' if ok else '**FAIL**'} |")

    # The acceptance rule on the ledger headline, three cases. The first is the
    # one the second ultrareview found refused: a clean clone reports
    # "Anchors verified: N / M" with M > N because an anchor is SKIPPED, and
    # the table then holds N rows. It must be accepted, and labelled.
    def _ledger_case(headline: str, rows: int, stderr: str = "") -> str:
        body = "".join(f"| T.{i} | PASS | S | text | {600 + i} | {600 + i} |\n"
                       for i in range(rows))
        out = ("## All claims\n\n| claim_id | status | section | text | manuscript "
               "| computed |\n|---|---|---|---|---:|---:|\n" + body
               + f"\n**Anchors verified:** {headline}\n")
        try:
            _, info = validate_ledger_parse(out, stderr, 0)
            return f"accepted, skipped={info['anchors_skipped']}"
        except SystemExit:
            return "refused"

    ledger_cases = [
        ("clean clone: headline 2 / 3, 2 rows (one anchor skipped)", "2 / 3", 2, "",
         "accepted, skipped=1"),
        ("table shorter than the headline's run count: 2 / 2, 1 row", "2 / 2", 1, "",
         "refused"),
        ("audit_claims crashed: traceback on stderr", "2 / 2", 2,
         "Traceback (most recent call last):\n  boom", "refused"),
    ]
    for label, headline, rows, err, want in ledger_cases:
        got = _ledger_case(headline, rows, err)
        ok = got == want
        bad += 0 if ok else 1
        print(f"| ledger headline -- {label} | {want} | {got} | "
              f"{'PASS' if ok else '**FAIL**'} |")

    n = len(SELF_TEST) + 1 + len(ledger_cases)
    print(f"\n**Calibration:** {n} probes, {bad} FAIL.\n")
    return bad, n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-test", action="store_true", help="run the extractor calibration only")
    args = ap.parse_args()

    # self_test returns (failures, probes). A tuple is always truthy, so the
    # failure count must be unpacked -- testing the tuple itself would abort
    # every run, or, written the other way, pass every run.
    n_fail, n_probes = self_test()
    if args.self_test:
        return 1 if n_fail else 0
    if n_fail:
        print("extractor calibration FAILED -- inventory not produced", file=sys.stderr)
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    led, ledger_info = ledger_values()
    guards = guard_literals()

    all_rows: list[dict] = []
    masked_rows: list[dict] = []
    per_doc: dict[str, dict] = {}
    for name, path in ARTEFACTS.items():
        rows, excl = extract(path)
        rec = recall_accounting(path)
        for r in rec.pop("removed_literals"):
            masked_rows.append({"artefact": name, **r})
        for r in rows:
            if r["bucket"] == "year_like":
                masked_rows.append({"artefact": name, "rule": "year_like",
                                    "literal": r["literal"], "line": r["line"],
                                    "context": r["context"]})
        kept = [r for r in rows if r["bucket"] != "year_like"]
        # The books must close: everything the masks left is either retained or
        # set aside as year-like. A mismatch means a literal vanished.
        rec["retained_plus_year_like"] = len(rows)
        rec["accounting_closes"] = rec["literals_after_masking"] == len(rows)
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
            "recall": rec,
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
        # The register quotes this rather than a hand-written number: its "16
        # probes" went stale when two were added, an ultrareview finding.
        "calibration": {"probes": n_probes, "failures": n_fail},
        "coverage_is_by_value_not_by_occurrence": True,
        "ledger_distinct_values": len(led),
        # Anchors that did not run in this checkout (e.g. a clean clone without
        # the gitignored raw S021 trajectories). Non-zero means the ledger set is
        # incomplete and the buckets may differ from a full checkout.
        "ledger": ledger_info,
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

    print("\n## Recall accounting -- every literal must land somewhere\n")
    print("| artefact | in raw text | removed by masks | after masking | inventoried | closes |")
    print("|---|---:|---:|---:|---:|---|")
    for name, d in per_doc.items():
        r = d["recall"]
        print(f"| {name} | {r['literals_in_raw_text']} | {r['removed_by_masks']} | "
              f"{r['literals_after_masking']} | {r['retained_plus_year_like']} | "
              f"{'yes' if r['accounting_closes'] else '**NO**'} |")
    print("\nLiterals removed **per rule** -- the span count cannot tell an "
          "over-broad rule from a harmless one:\n")
    for name, d in per_doc.items():
        c = {k: v for k, v in d["recall"]["literals_removed_per_rule"].items() if v}
        print(f"* **{name}** -- " + (", ".join(f"`{k}` {v}" for k, v in c.items())
                                     if c else "nothing removed"))

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
    # Every literal a mask removed, with its rule and context. The per-rule COUNT
    # was already printed when RE_LENGTH was dropping 110 claim literals; nobody
    # looked at WHICH ones. This file is what makes that loss readable.
    with (OUT_DIR / "masked_by_rule.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["artefact", "rule", "line", "literal", "context"])
        w.writeheader()
        for r in sorted(masked_rows, key=lambda r: (r["artefact"], r["rule"], r["line"])):
            w.writerow({k: r[k] for k in w.fieldnames})

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
