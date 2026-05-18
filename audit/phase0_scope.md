# Phase 0 — Reconnaissance scope memo

**Date:** 2026-05-18
**Audit pass:** Independent re-verification (Phase 0 + Phase 1 of the
6-phase plan). This pass does **not** trust the prior commit `2e69660`
audit; it re-derives every D-class statistic from raw data with a
fresh script.

## 1. Manuscript files in scope

| File | Lines | Role |
|---|---|---|
| `preprint/manuscript.md` | 2192 | Main paper (Abstract → §8 + Appendix A + Appendix B) |
| `preprint/supplementary.md` | 226 | Supplementary tables S1–S10 |
| `preprint/appendix_B_draft.md` | 26 | Older standalone draft of Appendix B |
| `preprint/references.bib` | 178 | BibTeX bibliography |

Appendix B is duplicated: an embedded version (§Appendix B in
`manuscript.md`, lines 2015–2192) and an older standalone draft
(`appendix_B_draft.md`). Both are in scope; **any disagreement
between them is itself a finding**.

## 2. Prior audit (commit `2e69660`, 2026-05-18, ~110 numeric claims)

Per the commit message, the prior pass logged 10 substantive
discrepancies (D1, D3, D4, D5, D9, D10, D11, D12, D13, D14), 7 wording
notes (W1–W7), and one code gap (D15), and **applied all fixes**.
Detailed in `preprint/audit_phase1_findings.md`.

**This pass treats the prior audit as untrusted ground truth.** Every
claim is re-derived independently. The prior audit will only be
consulted when (a) we find a discrepancy and want to see whether the
prior pass surfaced it, or (b) it documents a methodology decision the
manuscript depends on (e.g. σ/μ\* CI formula).

## 3. Data layout

```
data/runs/full_sweep/
├── morris_sample.parquet                  # locked 160-point Morris sample
├── aggregated.parquet                     # 1,280-row master (project aggregator)
└── <S1|S2|S3|S4>_<M|F>/
    ├── aggregated.parquet                 # per-cell aggregate
    └── <CELL>_<RUN_IDX>/                  # 160 runs per cell
        ├── config.json
        ├── output.csv                     # raw Pulse 5-s timeseries
        ├── output_pulse_native.csv        # 0.02-s native timeseries
        ├── pulse.log                      # stdout/stderr (with clamp regex lines)
        └── run_meta.json                  # exit_code, wall_time, image hash
```

Other data subtrees referenced by the manuscript:

| Path | Source | Manuscript role |
|---|---|---|
| `data/runs/continuous_ards/CONT_<F\|M>_NNN_sevXXXX/` | S009 | §3.5.1 continuous-severity sweep, 200 runs |
| `data/runs/s018_blood_volume/{bracket,floor,smoke,runs}/` | S018 | §3.5 BV mechanism dose-response, 3×20 runs |
| `data/runs/s014_trigger_lockout/` | S014 | §3.8 F-004 causal confirmation, 64+64 paired runs |
| `data/runs/phase4b_seed44_S2M/` | Phase 4b | §2.8 new-seed Morris stability check |
| `data/runs/full_sweep_repro/` | Phase 4a | §2.8 same-seed re-execution |
| `results/*.{csv,parquet}` | analysis outputs | source of headline statistics |

## 4. Anchor counts (manuscript surface area)

Crude counts via grep over `manuscript.md` + `supplementary.md` +
`appendix_B_draft.md`:

| Anchor type | Count | Method |
|---|---|---|
| `Sxxx` experiment IDs in prose | 20 distinct (S001–S020) | matches INDEX.md |
| Figures referenced | 6 (Fig 2 a–f, Fig 5, Fig 6) | |
| Tables referenced | 2 numbered (Table 1, Table 2) + several unnumbered §-tables | |
| Citations | 16 distinct keys + raw URLs | bib has 16 entries |
| BibTeX entries | 16 | `references.bib` count of `@` |

(These counts are scoping aids only; the Phase 1 deliverable below
audits the numeric content, not the anchors.)

## 5. D / L / P classification — Phase 1 scope

* **D (data-derived)** — number computed from this project's Pulse
  runs. **In scope for Phase 1.** Re-derived independently from raw
  files under `data/runs/`.
* **L (literature-derived)** — number cited from an external paper
  or Pulse documentation page. **Deferred to Phase 2.** Listed in
  Phase 1 deliverable for completeness only.
* **P (Pulse-source-derived)** — number read from Pulse C++ source
  or config files (e.g. `BloodVolumeBaseline = 4,802.63 mL`).
  **Deferred to Phase 2.** Listed for completeness.

Where a number is a *re-statement* of a literature value (e.g. "Pulse
docs report VC-AC error 0.07–2.25 %") it is classified L.

## 6. Fresh-aggregation methodology

For D-class claims the audit script:

* **Counts of runs by flag** — read `aggregated.parquet` flag columns
  (`clean`, `clamped`, `diverged`, `implausible`, `not_steady_state`)
  and recount with `groupby`. Manuscript references to flag counts
  are validated against these recounted values.
  *Caveat:* recounts trust the detector's flag assignment from the
  original sweep. Detector logic itself is Phase 3 scope; here we
  verify counts of an existing flag column.
* **Means / std / CV / slopes / drift on output channels** — read
  raw `output.csv` files directly (NOT the precomputed `*_mean`,
  `*_cv`, `*_slope_*`, `*_delta_60s` columns in `aggregated.parquet`).
  Compute the statistic with pandas / numpy primitives on the
  steady-state window [60, 120] s.
* **Linear fits** (e.g. `PaO2 ≈ 505 × FiO2 − 25`) — recomputed via
  `scipy.stats.linregress` on raw per-run means.
* **Wasserstein distances** — recomputed via
  `scipy.stats.wasserstein_distance` on raw per-run means; not read
  from `results/wasserstein_male_vs_female.csv`.
* **Spearman ρ** — recomputed via `scipy.stats.spearmanr` on
  per-input μ\* vectors read from `results/morris_indices.parquet`.
  μ\* itself is treated as a deferred fixed input (re-deriving the
  Morris EE math is out of Phase 1 scope; flagged for Phase 3 spot
  check).
* **BH-FDR survivors** — recomputed from p-values via the
  Benjamini-Hochberg formula directly (k · q / N), not via the
  project's `bh_fdr_adjust` helper.

## 7. Out-of-scope for Phase 1

* L-class and P-class claims (deferred Phase 2).
* Citation verification — DOIs, paper content, attribution (Phase 2).
* Code / logic review of detector and analysis pipeline (Phase 3).
* Figure regeneration / image diff (Phase 4).
* Verbatim-quote audit (Phase 5).
* **Re-running any Pulse simulation** — explicit user constraint.

## 8. Estimated wall clock

* Walking 1,280 raw `output.csv` files and recomputing per-channel
  statistics: ~3–5 min.
* Continuous-ARDS sweep (200 runs): ~1 min.
* S018 BV dose-response (60 runs): ~30 s.
* S014 paired-trigger runs (~128 runs): ~1 min.
* Composing the deliverable: ~15 min.

Wall-clock estimate: 30–60 min for Phase 1 end-to-end.

## 9. Hard stop

Phase 1 ends when `audit/phase1_numerical_claims.md` is written. No
manuscript edits, no Phase 2 work, no git commits. Wait for user
review.
