"""S015 P3.3 — Morris math isolation.

Hand-builds an EE array with known elementary effects and verifies the
internal `_morris_stats` and `_block_bootstrap_mu_star_ci` produce the
expected mu / mu_star / sigma. Independent of the full pipeline.

Hand-computed reference (3 trajectories x 1 input, OAT step delta=1.0):
    EEs:  [+10, -6, +8, -4, +12, -2]   (6 EEs across 3 trajectories)
    abs:  [ 10,  6,  8,  4,  12,  2]
    mu       = (10 - 6 + 8 - 4 + 12 - 2) / 6 = 18 / 6 = 3.0
    mu_star  = (10 + 6 + 8 + 4 + 12 + 2) / 6 = 42 / 6 = 7.0
    sigma    = std (ddof=1) of [10, -6, 8, -4, 12, -2]

Block bootstrap with 3 trajectories: each trajectory keeps its EE pair
together. We resample trajectory IDs with replacement.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from src.analysis_morris import _block_bootstrap_mu_star_ci, _morris_stats  # noqa: E402


def _safe(s: str) -> str:
    return s.encode("ascii", errors="replace").decode("ascii")


def main() -> int:
    print(_safe("=" * 70))
    print(_safe("S015 P3.3 - Morris math isolation"))
    print(_safe("=" * 70))

    # --- Hand-built EE array ---
    ees = np.array([10.0, -6.0, 8.0, -4.0, 12.0, -2.0])
    expected_mu = 3.0
    expected_mu_star = 7.0
    # sigma with ddof=1 (sample std)
    expected_sigma = float(np.std(ees, ddof=1))

    mu, mu_star, sigma = _morris_stats(ees)
    print(_safe(f"\nHand-built EEs: {ees.tolist()}"))
    print(_safe(f"  expected mu       = {expected_mu}        got = {mu}"))
    print(_safe(f"  expected mu_star  = {expected_mu_star}        got = {mu_star}"))
    print(_safe(f"  expected sigma    = {expected_sigma:.6f}  got = {sigma:.6f}"))

    assert abs(mu - expected_mu) < 1e-12, "mu mismatch"
    assert abs(mu_star - expected_mu_star) < 1e-12, "mu_star mismatch"
    assert abs(sigma - expected_sigma) < 1e-9, "sigma mismatch"
    print(_safe("\n[PASS] _morris_stats matches hand-computed reference."))

    # --- Edge case: single EE ---
    mu1, mus1, sig1 = _morris_stats(np.array([5.0]))
    assert mu1 == 5.0 and mus1 == 5.0 and sig1 == 0.0
    print(_safe(f"[PASS] single-EE edge case: mu=mu_star=5.0, sigma=0.0"))

    # --- Edge case: empty ---
    mu0, mus0, sig0 = _morris_stats(np.array([]))
    assert np.isnan(mu0) and np.isnan(mus0) and np.isnan(sig0)
    print(_safe(f"[PASS] empty-EE edge case: all NaN"))

    # --- Block bootstrap CI: 3 trajectories, 2 EEs each ---
    df = pd.DataFrame({
        "trajectory": [0, 0, 1, 1, 2, 2],
        "ee": [10.0, -6.0, 8.0, -4.0, 12.0, -2.0],
    })
    rng = np.random.default_rng(123)
    lo, hi = _block_bootstrap_mu_star_ci(df, n_bootstrap=5000, rng=rng, alpha=0.05)
    print(_safe(f"\nBlock bootstrap (3 traj x 2 EE, B=5000, alpha=0.05):"))
    print(_safe(f"  mu_star point = {expected_mu_star}"))
    print(_safe(f"  CI = [{lo:.4f}, {hi:.4f}]"))
    # CI should bracket the point estimate
    assert lo <= expected_mu_star <= hi, f"CI [{lo}, {hi}] does not bracket mu_star={expected_mu_star}"
    # Sanity: lo > 0 since all |EE| are positive integers
    assert lo > 0, f"CI lower bound should be > 0; got {lo}"
    print(_safe(f"[PASS] block bootstrap CI brackets the mu_star point estimate."))

    # --- Block bootstrap CI: 1 trajectory only -> NaN ---
    df1 = pd.DataFrame({"trajectory": [0, 0, 0], "ee": [1.0, 2.0, 3.0]})
    lo1, hi1 = _block_bootstrap_mu_star_ci(df1, n_bootstrap=100, rng=rng)
    assert np.isnan(lo1) and np.isnan(hi1)
    print(_safe(f"[PASS] single-trajectory block bootstrap correctly returns NaN CI"))

    # --- Cross-check: hand-walked Morris OAT step ---
    # Construct a 2-trajectory sample where flipping `hr` by +1.0 normalized
    # produces y deltas of +6 and +4; flipping `vt` by +1.0 produces +12 and -8.
    # Expected per-input mu_star: hr -> 5, vt -> 10.
    print(_safe("\nIndependent OAT cross-check:"))
    sample_ees_hr = np.array([6.0, 4.0])
    sample_ees_vt = np.array([12.0, -8.0])
    _, mus_hr, _ = _morris_stats(sample_ees_hr)
    _, mus_vt, _ = _morris_stats(sample_ees_vt)
    print(_safe(f"  hr mu_star: expected 5.0, got {mus_hr}"))
    print(_safe(f"  vt mu_star: expected 10.0, got {mus_vt}"))
    assert mus_hr == 5.0 and mus_vt == 10.0
    print(_safe("[PASS] independent OAT cross-check"))

    print(_safe("\nAll P3.3 math-isolation tests PASSED."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
