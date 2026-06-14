"""Prop 1 (2026-06-14): scrape manuscript.md and verify every audited number
is literally present (read-only). Closes hole (a).

audit_claims.py compares each claim's HARD-CODED `manuscript_value` against a
value recomputed from the frozen artifacts. It never opens manuscript.md, so it
cannot catch the case where the monograph PRINTS a different digit than the
audit assumes (a hand-transcription gap). This script formats each audited
value per its display precision and checks it appears in manuscript.md.

Output: list of audited numbers NOT found verbatim in the monograph (the
actionable signal) + counts. Read-only; writes nothing but stdout.

LIMITATION (stated honestly): substring presence is strong evidence for
DISTINCTIVE values (decimals, >=3 digits, comma-grouped) but weak for small
integers (0, 4, 5, 160), which appear in the prose for unrelated reasons. The
not-found list and the distinctive-value occurrence counts are the real output.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

# audit_claims.py builds its `claims` ledger at module level, then prints a
# report and calls sys.exit(). We load it via importlib with our own module
# reference + sys.exit neutralized, so `claims` stays accessible even though the
# module would otherwise exit during import. stdout suppressed (the report is noise).
sys.argv = ["audit_claims.py"]
_spec = importlib.util.spec_from_file_location(
    "audit_claims_loaded", REPO / "scripts" / "audit_claims.py"
)
audit_claims = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = audit_claims  # @dataclass needs the module registered
_real_exit = sys.exit
sys.exit = lambda *a, **k: None  # no-op so the module finishes loading
try:
    with contextlib.redirect_stdout(io.StringIO()):
        _spec.loader.exec_module(audit_claims)
except SystemExit:
    pass  # claims is built before any exit; our `audit_claims` ref is populated
finally:
    sys.exit = _real_exit

CLAIMS = audit_claims.claims  # list[Claim]
MANU = (REPO / "preprint" / "manuscript.md").read_text(encoding="utf-8")
# Normalize unicode minus / non-breaking + thin spaces so "-2" matches "−2" etc.
NORM = (MANU.replace("−", "-").replace(" ", " ")
            .replace(" ", " ").replace(" ", " "))


def variants(value: float, rule: str) -> list[str]:
    """Generous formatted-string candidates for an audited value.

    We deliberately over-generate (precisions 0-3, with/without comma grouping,
    trailing-zero stripped) so a number printed in ANY reasonable format counts
    as 'found'. The audit already proved the DATA supports each value; this
    script only asks 'is it printed somewhere in the monograph', so minimizing
    false-negatives is what matters. The remaining not-found list is then real.
    """
    v = value
    out: list[str] = []
    for p in (0, 1, 2, 3):
        s = f"{v:.{p}f}"
        out.append(s)
        out.append(f"{v:,.{p}f}")          # comma-grouped
        if "." in s:
            out.append(s.rstrip("0").rstrip("."))  # trailing-zero stripped
    out.append(str(v))
    seen, uniq = set(), []
    for s in out:
        if s not in seen:
            seen.add(s)
            uniq.append(s)
    return uniq


def best_count(cands: list[str]) -> tuple[int, str]:
    """Max occurrences across candidate strings; returns (count, which)."""
    best_n, best_s = 0, cands[0] if cands else ""
    for s in cands:
        n = NORM.count(s)
        if n > best_n:
            best_n, best_s = n, s
    return best_n, best_s


def is_distinctive(value: float, rule: str) -> bool:
    """Heuristic: decimals or >=3-digit integers are unambiguous enough that
    a zero-count is a real red flag (not just prose-noise ambiguity)."""
    if rule in ("displayed_2dp", "displayed_3dp", "pct_1dp", "displayed_1dp"):
        return True
    return abs(value) >= 100


def main() -> None:
    checked = found = notfound = 0
    notfound_rows = []
    distinctive_rows = []
    for c in CLAIMS:
        if c.manuscript_value is None:
            continue
        checked += 1
        cands = variants(c.manuscript_value, c.tolerance_rule)
        n, which = best_count(cands)
        if n >= 1:
            found += 1
        else:
            notfound += 1
            notfound_rows.append((c.claim_id, c.manuscript_value, c.tolerance_rule,
                                  cands, c.manuscript_text[:70]))
        if is_distinctive(c.manuscript_value, c.tolerance_rule):
            distinctive_rows.append((c.claim_id, which or cands[0], n, c.section[:34]))

    print("# Prop 1 — manuscript.md number-presence scrape\n")
    print(f"claims with a manuscript_value : {checked}")
    print(f"  found verbatim in monograph  : {found}")
    print(f"  NOT found (review these)     : {notfound}\n")

    if notfound_rows:
        print("## NOT FOUND verbatim in manuscript.md (candidate transcription gaps)\n")
        for cid, val, rule, cands, txt in notfound_rows:
            print(f"  [{cid}] value={val} rule={rule}")
            print(f"      tried: {cands}")
            print(f"      claim: {txt}")
    else:
        print("## NOT FOUND: none — every audited value appears verbatim. ✅\n")

    print("\n## Distinctive-value occurrence counts (manual eyeball of headline numbers)\n")
    # show the ones with count 0 or unusually placed first
    distinctive_rows.sort(key=lambda r: r[2])
    for cid, s, n, sec in distinctive_rows[:60]:
        flag = "  <-- ZERO" if n == 0 else ("  <-- once" if n == 1 else "")
        print(f"  {n:3d} x '{s}'  [{cid}] {sec}{flag}")


if __name__ == "__main__":
    main()
