"""Methodology-descriptor check (pre-submission manual-verification gate).

The numeric audit ledger (scripts/audit_claims.py) verifies NUMBERS -- it checks
that "48/48", "0.928", "1{,}000", etc. match the computed artefacts. It does NOT
verify *method descriptors*: sentences that assert HOW a statistic was produced
("evaluated on the bootstrap CI", "computed via ...", "point estimate", ...).
Those sentences are the highest-risk, lowest-coverage claims in the manuscript.

This was born from the 2026-07-02 bug: the paper stated H1 (top-3 fraction >=50%)
"was evaluated on the bootstrap CI rather than the point estimate" while the code
(`evaluate_h1`) evaluates it on the POINT ESTIMATE (no CI on the fraction). The
numbers around the false phrase all passed the audit; only a manual code cross-
check caught it.

This script does NOT verify anything itself -- it just LISTS every method-
descriptor sentence with file:line so a human can re-confront each one against
the source code before submission.

Usage:
    uv run python scripts/methodology_descriptor_check.py
    uv run python scripts/methodology_descriptor_check.py --high-only
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FILES = [
    REPO / "preprint_npj" / "paper.tex",
    REPO / "preprint_npj" / "supplement.tex",
    REPO / "preprint" / "manuscript.md",
]

# HIGH = the exact failure class: a claim about how a statistic was produced
# (bootstrap vs point estimate, CI, resampling, permutation, "evaluated/computed").
HIGH = [
    r"bootstrap", r"\bCIs?\b", r"confidence interval", r"point[- ]estimate",
    r"\bevaluated\b", r"\bcomputed\b", r"\bestimated\b", r"\bestimator\b",
    r"\bcalculated\b", r"re-?evaluat\w*", r"resampl\w*", r"permutation",
]
# REVIEW = method names / knobs worth a glance but lower risk.
REVIEW = [
    r"\bderived\b", r"\bseed\b", r"\bRNG\b", r"Benjamini", r"\bFDR\b",
    r"Wasserstein", r"Spearman", r"Sobol", r"SHAP", r"RandomForest",
    r"\bnull\b", r"\bp-?values?\b", r"trajectory-level",
]

HIGH_RE = re.compile("|".join(HIGH), re.IGNORECASE)
REVIEW_RE = re.compile("|".join(REVIEW), re.IGNORECASE)
ANY_RE = re.compile("|".join(HIGH + REVIEW), re.IGNORECASE)
BREAK_RE = re.compile(r"[.:]\s+|\n\s*\n")


def blank_tex_comments(text: str) -> str:
    """Blank full-line LaTeX comments while preserving line numbers."""
    return "\n".join("" if re.match(r"\s*%", ln) else ln for ln in text.splitlines())


def sentence_window(text: str, pos: int, span: int = 380) -> tuple[int, int]:
    lo = max(0, pos - span)
    last = None
    for m in BREAK_RE.finditer(text, lo, pos):
        last = m
    left = last.end() if last else lo
    hi = min(len(text), pos + span)
    m = BREAK_RE.search(text, pos, hi)
    right = (m.start() + 1) if m else hi
    return left, right


def triggers_in(fragment: str) -> list[str]:
    found = sorted({m.group(0).lower() for m in ANY_RE.finditer(fragment)})
    return found


def scan(path: Path, high_only: bool) -> list[dict]:
    raw = path.read_text(encoding="utf-8")
    text = blank_tex_comments(raw) if path.suffix == ".tex" else raw
    seen: set[tuple[int, int]] = set()
    rows: list[dict] = []
    for m in ANY_RE.finditer(text):
        left, right = sentence_window(text, m.start())
        if (left, right) in seen:
            continue
        seen.add((left, right))
        frag = re.sub(r"\s+", " ", text[left:right]).strip()
        is_high = bool(HIGH_RE.search(frag))
        if high_only and not is_high:
            continue
        rows.append(
            {
                "line": text.count("\n", 0, left) + 1,
                "priority": "HIGH" if is_high else "review",
                "triggers": triggers_in(frag),
                "text": frag,
            }
        )
    rows.sort(key=lambda r: r["line"])
    return rows


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # Windows cp1252 chokes on μ/≥/×
    except Exception:
        pass
    high_only = "--high-only" in sys.argv
    grand_high = grand_total = 0
    for path in FILES:
        if not path.exists():
            print(f"\n### {path.relative_to(REPO)} -- NOT FOUND\n")
            continue
        rows = scan(path, high_only)
        n_high = sum(1 for r in rows if r["priority"] == "HIGH")
        grand_high += n_high
        grand_total += len(rows)
        print(f"\n{'='*100}")
        print(f"### {path.relative_to(REPO)}  --  {len(rows)} sentences ({n_high} HIGH)")
        print("=" * 100)
        for r in rows:
            tag = "!!" if r["priority"] == "HIGH" else "  "
            trg = ", ".join(r["triggers"])
            print(f"\n{tag} L{r['line']:<5} [{trg}]")
            print(f"     {r['text']}")
    print(f"\n{'='*100}")
    print(f"TOTAL: {grand_total} descriptor sentences  ({grand_high} HIGH-priority)")
    print("Re-confront each HIGH sentence against the source code before submission.")
    print("=" * 100)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
