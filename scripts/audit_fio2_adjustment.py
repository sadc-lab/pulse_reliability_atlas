"""Re-derive the FiO2 downstream-adjustment figures published in §2.1, §S3.3 and §3.4.

Why this script exists
----------------------
The 2026-08-13 gate audit (`audit/fio2_peep_setup_gates.md`) established that
Pulse accepts a submitted FiO2 of 1.0, ingests it exactly, and then reduces the
ventilator compartment's oxygen fraction to 0.9996, announcing it with an
`[ERROR]` line. The counts that went into the three documents -- 208 runs
requesting FiO2 = 1.0, 195 adjusted, 13 diverging before the ventilator action,
the substituted value itself and the 0.04 % magnitude -- came from shell
one-liners over gitignored logs. This script recomputes them into a committed
artefact, `results/fio2_adjustment_provenance.csv`, so the guard
`check_fio2_adjustment` in `scripts/audit_claims.py` has something to bind the
published phrases to.

Availability limit, stated rather than hidden
---------------------------------------------
`data/runs/full_sweep/**` is gitignored (`.gitignore:19-23`). This script
therefore runs only where the raw logs exist; the artefact it writes IS
committed, so the guard stays live on every clone. On a clone without the logs
nothing re-checks the artefact against them. Full public reproducibility waits
on the raw-run deposit planned with the release.

Conventions, declared before the first number was computed
----------------------------------------------------------
* A run is "adjusted" iff its `pulse.log` contains the substring
  `FiO2 setting + ambient fractions other than N2 is greater than 1.0`.
* The substituted value is parsed from that same line's tail,
  `Setting FiO2 to max value of <x>.`, and kept verbatim as a float.
* A run "reached the ventilator action" iff its log contains an `[Action]`
  block. The 20 diverged runs stop before Pulse applies any action.
* The relative magnitude is (1 - value) / 1.0, expressed in per cent.
* The alveolar ceiling is re-derived, not restated: FiO2 * (760 - 47) - 40/0.8,
  the same convention that yields 663 mmHg at FiO2 = 1.0 in the manuscript.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
SWEEP = REPO / "data" / "runs" / "full_sweep"
OUT = REPO / "results" / "fio2_adjustment_provenance.csv"

CELLS = ["S1_F", "S1_M", "S2_F", "S2_M", "S3_F", "S3_M", "S4_F", "S4_M"]
N_PER_CELL = 160
N_RUNS = len(CELLS) * N_PER_CELL

ADJUST_MARKER = "FiO2 setting + ambient fractions other than N2 is greater than 1.0"
ADJUST_VALUE_RE = re.compile(r"Setting FiO2 to max value of ([0-9.]+)\.")
ACTION_MARKER = "[Action]"

DRY_BAROMETRIC_MMHG = 760.0 - 47.0
PACO2_MMHG = 40.0
RESPIRATORY_QUOTIENT = 0.8


def _fail(msg: str) -> None:
    print(f"\nBLOCKING ASSERTION FAILED: {msg}")
    sys.exit(1)


def alveolar_ceiling(fio2: float) -> float:
    return fio2 * DRY_BAROMETRIC_MMHG - PACO2_MMHG / RESPIRATORY_QUOTIENT


def main() -> int:
    if not SWEEP.is_dir():
        print(
            "full_sweep logs absent (gitignored). Nothing recomputed; the committed\n"
            f"artefact {OUT.relative_to(REPO)} is what the audit guard reads."
        )
        return 0

    rows: list[dict[str, object]] = []
    for cell in CELLS:
        for d in sorted((SWEEP / cell).iterdir()):
            if not d.is_dir():
                continue
            cfg_p, log_p = d / "config.json", d / "pulse.log"
            if not cfg_p.is_file() or not log_p.is_file():
                _fail(f"{d.name}: missing config.json or pulse.log")
            cfg = json.loads(cfg_p.read_text(encoding="utf-8"))
            log = log_p.read_text(encoding="utf-8", errors="replace")

            hits = [ln for ln in log.splitlines() if ADJUST_MARKER in ln]
            value = None
            if hits:
                m = ADJUST_VALUE_RE.search(hits[0])
                if m is None:
                    _fail(f"{d.name}: adjustment line without a parseable value")
                value = float(m.group(1))
            rows.append(
                {
                    "case_id": cfg["case_id"],
                    "cell": cell,
                    "requested_fio2": float(cfg["ventilator"]["fio2"]),
                    "action_reached": ACTION_MARKER in log,
                    "adjusted": bool(hits),
                    "n_adjust_lines": len(hits),
                    "adjusted_fio2": value,
                }
            )

    df = pd.DataFrame.from_records(rows)

    # Blocking assertions: structure before numbers.
    if len(df) != N_RUNS:
        _fail(f"expected {N_RUNS} runs, found {len(df)}")
    if not df.loc[df["adjusted"], "n_adjust_lines"].eq(1).all():
        _fail("an adjusted run carries more than one adjustment line")
    if not df.loc[df["adjusted"], "requested_fio2"].eq(1.0).all():
        _fail("a run with requested FiO2 < 1.0 was adjusted")

    OUT.parent.mkdir(exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"wrote {OUT.relative_to(REPO)}  ({len(df)} rows)\n")

    at_one = df[df["requested_fio2"] == 1.0]
    adjusted = df[df["adjusted"]]
    missed = at_one[~at_one["adjusted"]]
    values = sorted(adjusted["adjusted_fio2"].unique())
    pct = 100.0 * (1.0 - values[0]) if len(values) == 1 else float("nan")

    print(f"runs requesting FiO2 = 1.0            : {len(at_one)}")
    print(f"of those, adjusted                    : {len(adjusted)}")
    print(f"of those, not adjusted                : {len(missed)}")
    print(f"  all of them missed the action?      : {(~missed['action_reached']).all()}")
    print(f"runs with requested FiO2 < 1.0 adjusted: "
          f"{int((df['adjusted'] & (df['requested_fio2'] < 1.0)).sum())}")
    print(f"distinct substituted values           : {values}")
    print(f"relative adjustment                   : {pct:.4f} %")
    print(f"alveolar ceiling at 1.0000            : {alveolar_ceiling(1.0):.2f} mmHg")
    print(f"alveolar ceiling at {values[0]}          : "
          f"{alveolar_ceiling(values[0]):.2f} mmHg")
    return 0


if __name__ == "__main__":
    sys.exit(main())
