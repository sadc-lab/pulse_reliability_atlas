#!/usr/bin/env python3
"""Fail when a tracked figure was last built before the data it draws.

WHY THIS EXISTS, and it is not hypothetical. On 2026-09-02 da5bd97 repaired the
S021 window selection and recomputed the window-dependent columns of
data/runs/s021_hyperoxia_convergence/plateau_stats.parquet. It regenerated the
two figures it reasoned depended on the converged set. A third,
preprint_npj/figures/fig03_actionable_corrections.pdf, reads the same file and
was not in that reasoning. Its in-plot annotation is computed at generation
time, so it kept printing a minimum of 779 mmHg where the repaired data gives
770. The stale figure shipped to four co-authors on 2026-09-05 and was found on
2026-09-07 only because an unrelated layout change happened to regenerate
everything.

WHY NOTHING SAW IT. audit_claims.check_figure_timestamps verifies that every
tracked figure carries the PINNED SOURCE_DATE_EPOCH, which is by construction
identical whether the file was built in August or this morning: pinning the
timestamp for byte-reproducibility removed the only signal that would have
betrayed the age. It passed 29 of 29 while the figure was five days stale.
scripts/verify.py would have caught it -- regenerating must leave a clean tree
-- but it runs in neither CI nor the pre-commit hook.

WHY THIS SHAPE AND NOT ANOTHER. Three designs were tried and measured first.

  1. "Regenerate in CI, fail if the tree moves." Rejected: CI is ubuntu-latest
     and the tracked figures are built on Windows, so a byte comparison can
     fail for font and path reasons that have nothing to do with staleness.
  2. "No tracked figure may predate any data commit", with no per-figure
     mapping. Rejected after measuring: a figure that IS regenerated but comes
     out byte-identical receives no new commit, so its commit date stays old
     and the rule reports it stale. That is most figures, most of the time.
  3. Deriving the mapping by parsing the producers. Rejected: of the eleven
     scripts in verify.py's FIGURE_SCRIPTS, five expose no readable input path,
     one yields "utf-8" from a read_text encoding argument, and several name a
     bare filename with the directory in a separate constant.

What survives is an EXPLICIT manifest, below, plus a completeness check: every
script verify.py regenerates must appear here, so a new figure cannot join the
repository without declaring what it reads.

THE TEST IS GIT ANCESTRY, not dates. For each output, the last commit touching
any of its declared inputs must be an ancestor of the last commit touching that
output. Ancestry is exact, immune to clock skew and rebases, needs no
regeneration, and gives the same answer on Windows and on Linux.

Usage:
      python scripts/check_figure_freshness.py             (measure)
      python scripts/check_figure_freshness.py --list      (print the manifest)
      python scripts/check_figure_freshness.py --self-test (calibrate)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
VERIFY = REPO / "scripts" / "verify.py"

# producer -> (data it reads, artefacts it writes). Paths are repo-relative and
# expanded against the git index, so a directory entry covers every tracked file
# under it. Resolved by reading each producer, because parsing them is not
# reliable enough to trust (see design note 3 above).
MANIFEST: dict[str, tuple[list[str], list[str]]] = {
    "scripts/make_figures.py": (
        [
            "results/cell_flag_summary.csv",
            "results/h1_top3_fraction.csv",
            "results/morris_indices.parquet",
            "results/reliability_classification.csv",
            "results/spearman_mu_star.csv",
            "results/wasserstein_male_vs_female.csv",
        ],
        [
            "figures/fig01_flag_summary",
            "figures/fig02_morris_mu_star_",
            "figures/fig03_h1_top3_fraction",
            "figures/fig04_h4_wasserstein",
            "figures/fig05_h4_spearman_mu_star",
            "figures/fig06_reliability_traffic_light",
            # verify.py's FIGURE_COPIES propagates fig05 here under another name.
            "preprint_npj/figures/fig_s2_spearman",
        ],
    ),
    # A pdflatex + pymupdf flowchart. It reads no artefact, so it can never go
    # stale this way; it is listed so the completeness check stays meaningful.
    "scripts/make_fig00_study_design.py": ([], ["preprint_npj/figures/fig00_study_design"]),
    "scripts/make_paper_fig01.py": (
        ["results/reliability_traffic_light.csv"],
        ["preprint_npj/figures/fig01_traffic_light"],
    ),
    "scripts/make_paper_fig02.py": (
        ["results/morris_indices.parquet"],
        ["preprint_npj/figures/fig02_morris_"],
    ),
    "scripts/make_paper_fig03.py": (
        [
            "data/runs/s014_trigger_lockout/paired_comparison.parquet",
            "data/runs/s021_hyperoxia_convergence/plateau_stats.parquet",
        ],
        ["preprint_npj/figures/fig03_actionable_corrections"],
    ),
    "scripts/make_paper_fig04.py": (
        [
            "data/runs/s018_blood_volume/s018_classified.parquet",
            "data/runs/s018_blood_volume/s018_floor_classified.parquet",
            "results/cell_flag_summary.csv",
        ],
        ["preprint_npj/figures/fig04_sex_bv_mechanism"],
    ),
    "scripts/make_supp_fig_s1.py": (
        [],  # see BLIND_SPOTS: everything it reads is untracked
        ["preprint_npj/figures/fig_s1_continuous_severity"],
    ),
    "scripts/make_supp_fig_s3.py": (
        ["data/runs/s021_hyperoxia_convergence"],
        ["preprint_npj/figures/fig_s3_hyperoxia_convergence"],
    ),
    "scripts/make_supp_fig_s4.py": (
        ["data/runs/s014_trigger_lockout"],
        ["preprint_npj/figures/fig_s4_vt_waveform"],
    ),
    "scripts/make_supp_fig_s5_decomposition.py": (
        ["results/reliability_traffic_light.csv"],
        ["preprint_npj/figures/fig_s5_decomposition"],
    ),
    # Not a figure, but the same hazard: it derives one tracked artefact from
    # another, and two figures read its output. Checking it closes the chain
    # reliability_classification.csv -> traffic_light.csv -> fig01 / fig_s5.
    "scripts/export_traffic_light.py": (
        ["results/reliability_classification.csv"],
        ["results/reliability_traffic_light."],
    ),
}


# Declared, not hidden. Git ancestry can only reason about tracked files, so a
# producer whose real input is raw run output that .gitignore excludes is NOT
# covered by this guard. Printing that on every run is the point: an uncovered
# figure must be visible, because a guard that silently passes on what it cannot
# see is exactly the failure this file exists to stop repeating.
BLIND_SPOTS: dict[str, str] = {
    "scripts/make_supp_fig_s1.py": (
        "reads data/runs/continuous_ards/CONT_*/ raw run output only; that tree "
        "has 0 tracked files, so nothing here can date it"
    ),
    "scripts/make_supp_fig_s3.py": (
        "plateau_stats.parquet IS checked -- the file that went stale in the "
        "first place -- but it also reads "
        "data/runs/s021_hyperoxia_convergence/<case>_long/output.csv for the "
        "trajectories, and those per-run CSVs are untracked"
    ),
    "scripts/make_supp_fig_s4.py": (
        "the s014 parquet IS checked, but it also reads "
        "data/runs/full_sweep/<cell>/<case>/output_pulse_native.csv, and only "
        "the aggregated parquets of full_sweep are tracked"
    ),
}


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO, capture_output=True, text=True, check=False
    ).stdout.strip()


def tracked(prefix: str) -> list[str]:
    """Tracked files whose path starts with `prefix`."""
    return [p for p in git("ls-files").splitlines() if p.startswith(prefix)]


def last_commit(paths: list[str]) -> str:
    """The most recent commit touching any of `paths`, or '' if none."""
    if not paths:
        return ""
    return git("log", "-1", "--format=%H", "--", *paths)


def is_ancestor(older: str, newer: str) -> bool:
    if not older or not newer:
        return True
    return (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", older, newer],
            cwd=REPO,
            capture_output=True,
            check=False,
        ).returncode
        == 0
    )


def verify_scripts() -> set[str]:
    """The producers verify.py regenerates. Empty means the parse broke.

    A completeness check whose population is empty passes vacuously, so this is
    separated out and printed by --list: the number it returns is the only
    evidence that the check has anything to compare against.
    """
    if not VERIFY.exists():
        return set()
    text = VERIFY.read_text(encoding="utf-8")
    block = text.split("FIGURE_SCRIPTS", 1)[-1].split("]", 1)[0]
    return {
        line.split('"')[1]
        for line in block.splitlines()
        if line.count('"') >= 2 and "scripts/" in line
    }


def check(manifest: dict[str, tuple[list[str], list[str]]]) -> list[str]:
    problems: list[str] = []

    # Completeness: verify.py's list is the authority on what gets regenerated.
    declared = set(manifest)
    listed = verify_scripts()
    if VERIFY.exists():
        if not listed:
            problems.append(
                "FIGURE_SCRIPTS no longer parses out of scripts/verify.py; the "
                "completeness check has no population and would pass vacuously"
            )
        for missing in sorted(listed - declared):
            problems.append(
                f"{missing} is regenerated by verify.py but declares no inputs here"
            )

    for script, (inputs, outputs) in sorted(manifest.items()):
        in_files = [f for pre in inputs for f in tracked(pre)]
        if inputs and not in_files:
            problems.append(f"{script}: declared inputs match no tracked file: {inputs}")
            continue
        data_commit = last_commit(in_files)
        for pre in outputs:
            out_files = tracked(pre)
            if not out_files:
                problems.append(f"{script}: declared output matches no tracked file: {pre}")
                continue
            fig_commit = last_commit(out_files)
            if not is_ancestor(data_commit, fig_commit):
                when_data = git("log", "-1", "--format=%h %ad", "--date=short", data_commit)
                when_fig = git("log", "-1", "--format=%h %ad", "--date=short", fig_commit)
                problems.append(
                    f"{pre}* was built at {when_fig}, but its data moved at "
                    f"{when_data} -- regenerate through scripts/verify.py"
                )
    return problems


def self_test() -> int:
    print("## Self-test\n")
    failures: list[str] = []

    # Positive control on the real defect, read out of history rather than
    # simulated: at 7e7933f, fig03 had not been rebuilt since da5bd97 moved
    # plateau_stats.parquet. The rule must reject that pairing.
    data_c = git("log", "-1", "--format=%H", "7e7933f", "--",
                 "data/runs/s021_hyperoxia_convergence/plateau_stats.parquet")
    fig_c = git("log", "-1", "--format=%H", "7e7933f", "--",
                "preprint_npj/figures/fig03_actionable_corrections.pdf")
    if not data_c or not fig_c:
        failures.append("historical control unavailable: 7e7933f not in this clone")
    elif is_ancestor(data_c, fig_c):
        failures.append("rule did NOT reject the real 2026-09-02 staleness")
    else:
        print("  ok    rejects the historical fig03 staleness (the defect it exists for)")

    # Negative control: the same pairing at HEAD must now pass.
    if not is_ancestor(
        last_commit(["data/runs/s021_hyperoxia_convergence/plateau_stats.parquet"]),
        last_commit(["preprint_npj/figures/fig03_actionable_corrections.pdf"]),
    ):
        failures.append("rule still rejects fig03 at HEAD, where it was repaired")
    else:
        print("  ok    accepts the same figure once repaired")

    # Completeness control: dropping an entry must be caught.
    trimmed = {k: v for k, v in MANIFEST.items() if k != "scripts/make_paper_fig03.py"}
    if not any("make_paper_fig03" in p for p in check(trimmed)):
        failures.append("completeness check did NOT catch an undeclared producer")
    else:
        print("  ok    catches a producer that verify.py runs but the manifest omits")

    # Negative control: the manifest as it stands must pass.
    live = check(MANIFEST)
    if live:
        failures.append(f"manifest does not pass as committed: {live}")
    else:
        print("  ok    the manifest passes on the current tree")

    if failures:
        print("\n  FAIL  self-test")
        for f in failures:
            print(f"        {f}")
        return 1
    print("\n  Self-test passed.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list", action="store_true", help="print the manifest")
    ap.add_argument("--self-test", action="store_true", help="calibrate the guard")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    if args.list:
        print("## Figure freshness manifest\n")
        listed = verify_scripts()
        print(f"  verify.py regenerates {len(listed)} producers; "
              f"the manifest declares {len(MANIFEST)}")
        for extra in sorted(listed - set(MANIFEST)):
            print(f"    UNDECLARED  {extra}")
        print()
        for script, (inputs, outputs) in sorted(MANIFEST.items()):
            print(f"  {script}")
            for i in inputs or ["(reads no artefact)"]:
                print(f"      reads  {i}")
            for o in outputs:
                print(f"      writes {o}*")
        return 0

    print("## Tracked figures vs the data they draw\n")
    problems = check(MANIFEST)
    if problems:
        print(f"  FAIL  {len(problems)} stale or undeclared:")
        for p in problems:
            print(f"        {p}")
        print("\n  A figure older than its data prints numbers the data no longer")
        print("  holds. Regenerate with:  uv run python scripts/verify.py")
        return 1
    print(f"  ok    {len(MANIFEST)} producers, every output at or after its data")
    print(f"\n  NOT COVERED ({len(BLIND_SPOTS)}), because git cannot date untracked input:")
    for script, why in sorted(BLIND_SPOTS.items()):
        print(f"        {script}\n          {why}")
    print("\n  PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
