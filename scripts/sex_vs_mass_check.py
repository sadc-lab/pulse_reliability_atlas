"""S011 — sex-vs-mass disentangling.

The published H4 finding ("sex matters for gas exchange") confounds the
sex flag with the 11.1 kg mass difference between Pulse's standard adult
surrogates (M = 67.3 kg, F = 56.2 kg). Pulse's `SetupPatient.cpp` has
sex-conditional branches *and* mass-driven equations, so the M-vs-F
distance we measure is a mixture of both effects.

Design — 4 controlled cells × 2 scenarios × midrange Morris inputs:

    (M, 67.3 kg)   - Pulse standard male
    (F, 67.3 kg)   - female with male's mass
    (M, 56.2 kg)   - male with female's mass
    (F, 56.2 kg)   - Pulse standard female

Compared at S1 (healthy) and S4 (severe ARDS) → 8 runs total.

If outputs at fixed mass differ by sex → "sex" is a true categorical
modifier. If outputs at fixed sex differ by mass → "size" is the driver.
The cross-comparison decomposes the H4 effect.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.aggregator import aggregate_under, write_parquet  # noqa: E402
from src.runner import run_many  # noqa: E402
from src.scenario import (  # noqa: E402
    DURATION_HOURS,
    SAMPLE_INTERVAL_S,
    VENT_MODE,
    derive_map,
)

RUN_ROOT = REPO_ROOT / "data" / "runs" / "sex_vs_mass"
RESULTS = REPO_ROOT / "results"

MIDRANGE = {
    "hr": 80.0, "sbp": 105.0, "dbp": 70.0, "rr": 14.0,
    "vt": 550.0, "fio2": 0.6, "peep": 10.0,
}

# 4 controlled (sex, mass, height) tuples — height held at the body's
# native value to avoid Pulse rejecting unusual height/weight pairs.
CELLS = [
    {"sex": "Male",   "mass_kg": 67.3, "height_cm": 180.0, "label": "M_67.3kg"},
    {"sex": "Female", "mass_kg": 67.3, "height_cm": 180.0, "label": "F_67.3kg"},  # F at male's mass
    {"sex": "Male",   "mass_kg": 56.2, "height_cm": 163.0, "label": "M_56.2kg"},  # M at female's mass
    {"sex": "Female", "mass_kg": 56.2, "height_cm": 163.0, "label": "F_56.2kg"},
]

SCENARIOS = [
    {"sid": "S1", "ards": 0.00, "label": "healthy"},
    {"sid": "S4", "ards": 0.95, "label": "severe_ards"},
]


def build_config(cell: dict, scenario: dict, case_id: str) -> dict[str, Any]:
    cfg: dict[str, Any] = {
        "case_id": case_id,
        "condition": "Healthy" if scenario["ards"] == 0.0 else "ARDS",
        "duration_hours": DURATION_HOURS,
        "sample_interval_s": SAMPLE_INTERVAL_S,
        "baselines": {
            "age_yr": 18,
            "weight_kg": cell["mass_kg"],
            "height_cm": cell["height_cm"],
            "sex": cell["sex"],
            "hr": MIDRANGE["hr"],
            "rr": MIDRANGE["rr"],
            "sbp": MIDRANGE["sbp"],
            "dbp": MIDRANGE["dbp"],
        },
        "ventilator": {
            "mode": VENT_MODE,
            "tidal_volume_ml": MIDRANGE["vt"],
            "set_rr": MIDRANGE["rr"],
            "peep_cmh2o": MIDRANGE["peep"],
            "fio2": MIDRANGE["fio2"],
        },
        "atlas_meta": {
            "scenario": scenario["sid"],
            "sex": "M" if cell["sex"] == "Male" else "F",
            "cell_label": cell["label"],
            "mass_kg": cell["mass_kg"],
            "height_cm": cell["height_cm"],
            "dbp_requested": MIDRANGE["dbp"],
            "dbp_applied": MIDRANGE["dbp"],
            "dbp_was_clipped": False,
            "map_derived": derive_map(MIDRANGE["sbp"], MIDRANGE["dbp"]),
        },
    }
    if scenario["ards"] > 0.0:
        cfg["ards_severity"] = {"left": scenario["ards"], "right": scenario["ards"]}
    return cfg


def main() -> int:
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    jobs = []
    for sc in SCENARIOS:
        for cell in CELLS:
            cid = f"SVM_{sc['sid']}_{cell['label']}"
            cfg = build_config(cell, sc, cid)
            jobs.append((cfg, cid))
    print(f"[svm] {len(jobs)} runs (4 cells x 2 scenarios)")
    run_many(jobs, runs_root=RUN_ROOT, overwrite=False)
    df = aggregate_under(RUN_ROOT)

    # Augment with metadata from configs (mass_kg, cell_label)
    import json
    metas = []
    for _, row in df.iterrows():
        cid = row["case_id"]
        # Parse cid: SVM_<scenario>_<sex>_<mass>kg
        cfg_path = RUN_ROOT / cid / "config.json"
        if cfg_path.exists():
            cfg = json.loads(cfg_path.read_text())
            am = cfg.get("atlas_meta", {})
            metas.append({"case_id": cid, "mass_kg": am.get("mass_kg"),
                          "cell_label": am.get("cell_label")})
        else:
            metas.append({"case_id": cid, "mass_kg": None, "cell_label": None})
    meta_df = pd.DataFrame(metas)
    df = df.merge(meta_df, on="case_id", how="left")

    out = RESULTS / "sex_vs_mass.parquet"
    write_parquet(df, out)

    cols = ["case_id", "scenario", "sex", "mass_kg", "primary_flag",
            "HR_mean", "MAP_mean", "Vt_mean", "SpO2_mean", "PaO2_mean", "PaCO2_mean"]
    print("\n=== Per-cell summary ===")
    print(df[cols].to_string(index=False))

    # Decomposition: for each (scenario, output), compute
    #   sex_effect_at_67.3kg  = F_67.3 - M_67.3
    #   sex_effect_at_56.2kg  = F_56.2 - M_56.2
    #   mass_effect_for_M     = M_67.3 - M_56.2
    #   mass_effect_for_F     = F_67.3 - F_56.2
    print("\n=== Effect decomposition (F minus M at fixed mass; large mass minus small at fixed sex) ===")
    rows = []
    for sk in ["S1", "S4"]:
        for ch in ["HR", "MAP", "Vt", "SpO2", "PaO2", "PaCO2"]:
            def get(sex, mass):
                sel = df[(df.scenario == sk) & (df.sex == sex) & (df.mass_kg == mass)]
                if sel.empty:
                    return None
                v = sel.iloc[0][f"{ch}_mean"]
                return None if pd.isna(v) else float(v)
            m67 = get("M", 67.3); f67 = get("F", 67.3)
            m56 = get("M", 56.2); f56 = get("F", 56.2)
            sex_at_67 = (f67 - m67) if (m67 is not None and f67 is not None) else None
            sex_at_56 = (f56 - m56) if (m56 is not None and f56 is not None) else None
            mass_M = (m67 - m56) if (m67 is not None and m56 is not None) else None
            mass_F = (f67 - f56) if (f67 is not None and f56 is not None) else None
            rows.append({
                "scenario": sk, "output": ch,
                "sex_effect_at_67.3kg": sex_at_67,
                "sex_effect_at_56.2kg": sex_at_56,
                "mass_effect_for_M": mass_M,
                "mass_effect_for_F": mass_F,
            })
    decomp = pd.DataFrame(rows)
    decomp.to_csv(RESULTS / "sex_vs_mass_decomposition.csv", index=False)
    print(decomp.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
