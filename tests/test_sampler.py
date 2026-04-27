"""Tests for src/sampler.py.

Verifies preregistered Morris geometry: shape, ranges, trajectory
structure, seed reproducibility.
"""

from __future__ import annotations

import pandas as pd

from src import sampler as s


def test_input_specs_match_preregistration():
    """Locked ranges from preregistration §Inputs."""
    expected = {
        "hr": (50.0, 110.0),
        "sbp": (90.0, 120.0),
        "dbp": (60.0, 80.0),
        "rr": (8.0, 20.0),
        "vt": (300.0, 800.0),
        "fio2": (0.21, 1.0),
        "peep": (0.0, 20.0),
    }
    assert len(s.INPUT_SPECS) == 7
    for spec in s.INPUT_SPECS:
        lo, hi = expected[spec.name]
        assert spec.lo == lo and spec.hi == hi, f"{spec.name} bounds drifted"


def test_sample_morris_shape():
    """Morris sample shape: trajectories * (k+1) rows × k input columns + meta."""
    df = s.sample_morris(trajectories=2, levels=4, seed=42)
    assert len(df) == 2 * (s.NUM_INPUTS + 1)  # 16
    for inp in s.INPUT_NAMES:
        assert inp in df.columns
    assert "trajectory" in df.columns
    assert "point" in df.columns


def test_sample_morris_in_range():
    """Every sampled value within its preregistered range."""
    df = s.sample_morris(trajectories=5, levels=4, seed=42)
    for spec in s.INPUT_SPECS:
        col = df[spec.name].to_numpy()
        assert col.min() >= spec.lo - 1e-9, f"{spec.name} below lo"
        assert col.max() <= spec.hi + 1e-9, f"{spec.name} above hi"


def test_sample_morris_seed_reproducibility():
    """Same seed → identical sample (locked-seed reproducibility)."""
    a = s.sample_morris(trajectories=3, levels=4, seed=42)
    b = s.sample_morris(trajectories=3, levels=4, seed=42)
    pd.testing.assert_frame_equal(a, b)


def test_sample_morris_different_seeds_differ():
    """Different seeds → different samples (sanity check on RNG)."""
    a = s.sample_morris(trajectories=3, levels=4, seed=42)
    b = s.sample_morris(trajectories=3, levels=4, seed=43)
    # At least one column differs
    diffs = [(a[col] != b[col]).any() for col in s.INPUT_NAMES]
    assert any(diffs), "two different seeds produced identical samples"


def test_sample_morris_oat_property():
    """Within a trajectory, each consecutive pair differs by exactly one input."""
    df = s.sample_morris(trajectories=3, levels=4, seed=42)
    for traj_id, group in df.groupby("trajectory"):
        rows = group.sort_values("point").reset_index(drop=True)
        for k in range(len(rows) - 1):
            diffs = (
                (rows.iloc[k + 1][list(s.INPUT_NAMES)]
                 - rows.iloc[k][list(s.INPUT_NAMES)])
                .abs()
                > 1e-9
            )
            assert diffs.sum() == 1, (
                f"trajectory {traj_id} step {k}->{k+1}: "
                f"expected 1 input flip, got {int(diffs.sum())}"
            )


def test_invalid_trajectories_raises():
    import pytest
    with pytest.raises(ValueError):
        s.sample_morris(trajectories=0)


def test_invalid_levels_raises():
    import pytest
    with pytest.raises(ValueError):
        s.sample_morris(levels=1)
