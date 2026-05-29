"""One-command reproducibility gate for the Pulse Reliability Atlas.

Runs the full local verification pipeline in three stages:

    [1/3] Regenerate every data-derived figure + the traffic-light artefacts
          from the frozen data tree.
    [2/3] Build the npj PDFs (supplement first, then paper) -- best-effort:
          skipped with a clear note if no LaTeX toolchain is on PATH.
    [3/3] Run both claims-ledger audits (monograph ledger + paper crosswalk)
          as a hard gate.

Cross-platform: invoked the same way on the Windows laptop and on CI/Linux.

    uv run python scripts/verify.py      # or:  make verify

Exit status is non-zero if any figure script errors or either audit FAILs.
The PDF build is best-effort and never fails the run when the TeX toolchain
is absent (it does fail if the toolchain is present but a build breaks).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PY = sys.executable

# Figure / data-artefact generators that are data-derived and live in the repo.
FIGURE_SCRIPTS = [
    "scripts/make_figures.py",          # monograph figure set -> figures/
    "scripts/make_paper_fig03.py",      # npj Figure 3 (actionable corrections)
    "scripts/make_paper_fig04.py",      # npj Figure 4 (sex / blood-volume)
    "scripts/make_supp_fig_s1.py",      # npj Figure S1 (continuous severity)
    "scripts/make_supp_fig_s3.py",      # npj Figure S3 (hyperoxia convergence)
    "scripts/make_supp_fig_s4.py",      # npj Figure S4 (Vt waveform)
    "scripts/export_traffic_light.py",  # reliability traffic-light CSV + JSON
]

# npj paper figures that have NO generator script anywhere in the repo (they
# were produced ad hoc). verify CANNOT regenerate them; this is surfaced as a
# warning rather than a silent pass, so the reproducibility gap stays visible.
MISSING_GENERATORS = [
    "preprint_npj/figures/fig01_traffic_light.pdf",
    "preprint_npj/figures/fig02_morris_{HR,MAP,Vt,SpO2,PaO2,PaCO2}.pdf",
    "preprint_npj/figures/fig_s2_spearman.pdf",
]

# Build order matters: supplement first so paper.tex can read supplement.aux
# for xr-hyper cross-document references (mirrors preprint_npj/build_npj.ps1).
LATEX_DOCS = ["supplement", "paper"]


def _run(cmd, cwd=REPO, quiet=False):
    if not quiet:
        print(f"    $ {' '.join(str(c) for c in cmd)}")
    kw = {"cwd": str(cwd)}
    if quiet:
        kw["stdout"] = subprocess.DEVNULL
        kw["stderr"] = subprocess.DEVNULL
    return subprocess.run(cmd, **kw).returncode


def regen_figures() -> list[str]:
    print("\n[1/3] Regenerating figures + data artefacts from frozen data ...")
    failed = []
    for script in FIGURE_SCRIPTS:
        print(f"  - {script}")
        if _run([PY, script], quiet=True) != 0:
            print(f"    FAIL: {script} exited non-zero")
            failed.append(script)
    print("\n  NOTE: the following npj figures have no generator in the repo and")
    print("        were NOT regenerated (produced ad hoc -- reproducibility gap):")
    for missing in MISSING_GENERATORS:
        print(f"          - {missing}")
    return failed


def build_pdfs():
    print("\n[2/3] Building npj PDFs (best-effort) ...")
    if not (shutil.which("pdflatex") and shutil.which("bibtex")):
        print("  SKIP: pdflatex/bibtex not on PATH -- install TeX Live or MiKTeX")
        print("        to build PDFs locally. (Stage skipped, not failed.)")
        return None
    npj = REPO / "preprint_npj"
    (npj / "build").mkdir(exist_ok=True)
    ok = True
    for stem in LATEX_DOCS:
        if not (npj / f"{stem}.tex").exists():
            print(f"  SKIP: {stem}.tex not present.")
            continue
        print(f"  - building {stem}.pdf (pdflatex x3 + bibtex)")
        pdflatex = ["pdflatex", "-interaction=nonstopmode", "-output-directory=build", f"{stem}.tex"]
        _run(pdflatex, cwd=npj, quiet=True)
        _run(["bibtex", f"build/{stem}"], cwd=npj, quiet=True)
        _run(pdflatex, cwd=npj, quiet=True)
        _run(pdflatex, cwd=npj, quiet=True)
        pdf = npj / "build" / f"{stem}.pdf"
        if pdf.exists():
            print(f"    OK -> {pdf.relative_to(REPO)} ({pdf.stat().st_size} bytes)")
        else:
            print(f"    FAIL: {stem}.pdf not produced (see preprint_npj/build/{stem}.log)")
            ok = False
    return ok


def run_audits() -> bool:
    print("\n[3/3] Running claims-ledger audits (hard gate) ...")
    both_ok = True
    for label, args in [
        ("monograph ledger", ["scripts/audit_claims.py"]),
        ("paper crosswalk sync", ["scripts/audit_claims.py", "--check-paper-sync"]),
    ]:
        res = subprocess.run([PY, *args], cwd=str(REPO), capture_output=True, text=True)
        for line in res.stdout.splitlines():
            if "Total claims audited" in line or "Sync check" in line:
                print(f"  [{label}] {line.strip().replace('*', '')}")
        if res.returncode != 0:
            both_ok = False
            print(f"  FAIL: {label} audit reported a FAIL. Discrepancies:")
            grab = False
            for line in res.stdout.splitlines():
                if line.startswith("## Discrepancies"):
                    grab = True
                elif line.startswith("## ") and grab:
                    break
                if grab and line.startswith("|"):
                    print(f"    {line}")
    return both_ok


def main() -> int:
    print("=" * 70)
    print("Pulse Reliability Atlas -- reproducibility verification")
    print("=" * 70)

    fig_failed = regen_figures()
    pdf_ok = build_pdfs()
    audits_ok = run_audits()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print(f"  figures : {'FAIL (' + ', '.join(fig_failed) + ')' if fig_failed else 'OK'}")
    print(f"  pdfs    : {'SKIPPED (no TeX toolchain)' if pdf_ok is None else ('OK' if pdf_ok else 'FAIL')}")
    print(f"  audits  : {'OK' if audits_ok else 'FAIL'}")
    print("=" * 70)

    failed = bool(fig_failed) or (pdf_ok is False) or (not audits_ok)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
