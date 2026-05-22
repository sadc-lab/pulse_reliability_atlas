"""Morris elementary-effects sampler for the Pulse Reliability Atlas.

Wraps SALib's `morris.sample` with the 7-input problem locked in
`preregistration.md` §Inputs. Returns a `pandas.DataFrame` with one row per
Morris point; ordering preserves trajectory structure (rows 0..k define
trajectory 0, rows k+1..2k+1 define trajectory 1, etc., with k = num_inputs).

Locked design:
    7 inputs, 20 trajectories, 4 grid levels  →  N = 20 * (7 + 1) = 160 rows.

The constraint ``DBP / SBP <= 0.75`` is *not* applied here — Morris requires
its sample geometry to remain intact for elementary effects to be valid. The
constraint is enforced by `scenario.build_config` at submission time, which
also records the applied (post-clip) value alongside the requested value.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from SALib.sample import morris as morris_sampler


@dataclass(frozen=True)
class InputSpec:
    """One swept Morris input."""

    name: str
    lo: float
    hi: float
    units: str


# Locked by preregistration §Inputs (2026-04-22). Order is significant —
# SALib uses the index of each name to derive elementary effects.
INPUT_SPECS: tuple[InputSpec, ...] = (
    InputSpec("hr", 50.0, 110.0, "bpm"),
    InputSpec("sbp", 90.0, 120.0, "mmHg"),
    InputSpec("dbp", 60.0, 80.0, "mmHg"),
    InputSpec("rr", 8.0, 20.0, "bpm"),
    InputSpec("vt", 300.0, 800.0, "mL"),
    InputSpec("fio2", 0.21, 1.0, "fraction"),
    InputSpec("peep", 0.0, 20.0, "cmH2O"),
)

INPUT_NAMES: tuple[str, ...] = tuple(s.name for s in INPUT_SPECS)
NUM_INPUTS: int = len(INPUT_SPECS)

# Locked by preregistration §Sampling method.
DEFAULT_TRAJECTORIES: int = 20
DEFAULT_LEVELS: int = 4


def salib_problem() -> dict[str, Any]:
    """SALib problem dict matching the locked preregistration."""
    return {
        "num_vars": NUM_INPUTS,
        "names": list(INPUT_NAMES),
        "bounds": [[s.lo, s.hi] for s in INPUT_SPECS],
    }


def sample_morris(
    trajectories: int = DEFAULT_TRAJECTORIES,
    levels: int = DEFAULT_LEVELS,
    seed: int | None = 42,
) -> pd.DataFrame:
    """Generate a Morris sample.

    Parameters
    ----------
    trajectories
        Number of Morris trajectories (each contributes ``num_inputs + 1`` rows).
    levels
        Number of grid levels per dimension.
    seed
        RNG seed; ``None`` ⇒ non-deterministic.

    Returns
    -------
    pandas.DataFrame
        One row per sample point; columns are the input names. A
        ``trajectory`` column tags each row with its trajectory index, and a
        ``point`` column gives the position (0..num_inputs) within the
        trajectory. Both are useful when reconstructing elementary effects.
    """
    if trajectories < 1:
        raise ValueError("trajectories must be >= 1")
    if levels < 2:
        raise ValueError("levels must be >= 2")

    problem = salib_problem()
    arr = morris_sampler.sample(
        problem,
        N=trajectories,
        num_levels=levels,
        seed=seed,
    )
    expected_rows = trajectories * (NUM_INPUTS + 1)
    if arr.shape != (expected_rows, NUM_INPUTS):
        raise RuntimeError(
            f"unexpected SALib output shape {arr.shape}; expected ({expected_rows}, {NUM_INPUTS})"
        )

    df = pd.DataFrame(arr, columns=list(INPUT_NAMES))
    points_per_traj = NUM_INPUTS + 1
    df.insert(0, "trajectory", np.arange(expected_rows) // points_per_traj)
    df.insert(1, "point", np.arange(expected_rows) % points_per_traj)
    return df


def save_sample(df: pd.DataFrame, path: Path | str) -> Path:
    """Persist a sample to Parquet (reproducibility artifact)."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(p, index=False)
    return p


def load_sample(path: Path | str) -> pd.DataFrame:
    """Load a previously persisted sample."""
    return pd.read_parquet(path)


__all__ = [
    "DEFAULT_LEVELS",
    "DEFAULT_TRAJECTORIES",
    "INPUT_NAMES",
    "INPUT_SPECS",
    "InputSpec",
    "NUM_INPUTS",
    "load_sample",
    "salib_problem",
    "sample_morris",
    "save_sample",
]
