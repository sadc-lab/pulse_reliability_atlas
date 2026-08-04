# Feasibility of a paired cross-body re-analysis

**Opened** 2026-08-04. **Status: descriptive measurement complete. Nothing in the
manuscript changed, and no result from this dossier has entered the paper.**

Reproducible via `scripts/audit_paired_design_feasibility.py`, which rebuilds
every number below from the run-level artefacts and fails loudly on any drift.

> **No hypothesis test was run.** No permutation, no Wilcoxon, no Wasserstein,
> no multiplicity correction. This dossier establishes only what a paired
> subset *is*, not what it would show.

This is a separate question from `preregistration_traffic_light_deviation.md`.
That dossier asks whether the implementation conforms to the protocol. This one
asks whether a paired between-body re-analysis is technically possible, and
what selection bias it would carry.

---

## 1. Why this was measured

`paper.tex` §2.5 concedes that a surviving male–female Wasserstein distance
"establishes that sex matters, without separating an effect on the physiology
from an effect on which configurations survive the flag filter", and states the
remedy:

> Telling these contributions apart would require a design in which both bodies
> retain the same grid points *and* receive matched relative ventilation doses.

That sentence promises a design without establishing that one exists, or how
large it would be. This dossier measures it.

---

## 2. Four independent checks, all passed

Every number is rebuilt from the eight per-cell `aggregated.parquet` files in
`data/runs/full_sweep/`. That is deliberately **above** both
`results/cell_flag_summary.csv` and `results/reliability_classification.csv`:
those are outputs of the aggregation chain, not independent evidence of it.

| # | Check | Result |
|---|---|---|
| 1 | **Design premise.** Is the same 160-point Morris grid really executed in all eight cells? | **Verified empirically.** 160 distinct input vectors per cell, identical across all eight. The paper asserts this; it had not been measured. |
| 2 | **Clean counts**, recounted from run level against the published artefact | 49 / 42, 87 / 92, 144 / 122, 67 / 60; total **663**. Identical to `cell_flag_summary.csv` and to the figure published in the paper. |
| 3 | **Analytic bounds**, derived by hand *before* measuring: $\max(0, n_M + n_F - 160) \le n_\cap \le \min(n_M, n_F)$ | S1 ∈ [0, 42] → 34 · S2 ∈ [19, 87] → 69 · S3 ∈ [106, 122] → 111 · S4 ∈ [0, 60] → 51. All inside their bounds. |
| 4 | **Ventilation-dose ranges**, recomputed inside the paired subset | 4.5–11.9 and 5.3–14.2 mL/kg actual weight; 4.0–10.7 and 5.4–14.5 mL/kg ideal weight; +19.8 % and +36.1 % female excess. Identical to the values written into paper §2.5 and supplement §S6.2 on 2026-08-04, reached from a different starting artefact. |

Matching is done on the **seven-input vector**, not on `case_id`: two runs are
paired when the engine received the same operational configuration, which is
what "the same grid points" means. The applied (post-clip) DBP is used, and the
pulse-pressure clip depends only on SBP, so the applied vector is
body-independent — which check 1 confirms rather than assumes.

---

## 3. The paired subset exists, in all four scenarios

| scenario | clean in M | clean in F | **paired** | clean in M only | clean in F only |
|---|---:|---:|---:|---:|---:|
| S1 | 49 | 42 | **34** | 15 | 8 |
| S2 | 87 | 92 | **69** | 18 | 23 |
| S3 | 144 | 122 | **111** | 33 | 11 |
| S4 | 67 | 60 | **51** | 16 | 9 |

The concern that S1 and S4 might be too thin — their analytic lower bound is
zero — does not materialise. A paired analysis is fed in every scenario.

---

## 4. But the paired subset does not represent the whole grid

### 4.1 Input levels present

Within each paired subset, **all swept levels are represented for six of the
seven inputs** (HR, RR, SBP, DBP, Vt, PEEP). FiO₂ is the exception, in S1 and
S4.

This is a statement of **level presence only. It is not a claim of balanced
combinatorial coverage**, and it must not be read as one: 34 paired points
cannot span a seven-input design, so the paired subsets are necessarily sparse
in the interior of the space.

### 4.2 FiO₂ is truncated in S1 and S4, in complementary directions

| scenario | 0.21 | 0.473 | 0.737 | 1.00 |
|---|---:|---:|---:|---:|
| S1 (n = 34) | 17 | 17 | **0** | **0** |
| S2 (n = 69) | 25 | 26 | 13 | 5 |
| S3 (n = 111) | 35 | 29 | 35 | 12 |
| S4 (n = 51) | **0** | **0** | 35 | 16 |

**S1 loses the upper half of the FiO₂ range entirely; S4 loses the lower half.**
The two truncations are complementary, and they corroborate the mechanism that
`paper.tex` §3 limitation (iv) already states qualitatively: SpO₂ saturation
pinning and transient hyperoxia flag the high-FiO₂ runs on healthy lungs, while
severe hypoxemia flags the low-FiO₂ runs in severe ARDS.

**Consequence for any future paired analysis.** Two of the five surviving
Wasserstein distances are in S4 — SpO₂ and PaO₂. A paired re-analysis of those
two would rest on a subset from which the lower half of the FiO₂ range is
absent, and FiO₂ is the dominant driver of PaO₂. Such a result could not be
presented as representative of the FiO₂ domain; it would speak only to the
high-FiO₂ sub-domain where both bodies survive the filter. The same restriction
applies in the opposite direction in S1.

---

## 5. Why configurations are not shared

Read the labels carefully: *clean in M only* means the configuration failed on
the **female** body, and the failure mode below is the one recorded in F.

| scenario | clean in M only — failure mode in F | clean in F only — failure mode in M |
|---|---|---|
| S1 (15 / 8) | `not_steady_state` 15 | `not_steady_state` 8 |
| S2 (18 / 23) | `not_steady_state` 18 | `not_steady_state` 22, **`diverged` 1** |
| S3 (33 / 11) | `not_steady_state` 33 | `not_steady_state` 8, **`diverged` 3** |
| S4 (16 / 9) | `not_steady_state` 16 | `not_steady_state` 4, **`diverged` 5** |

Two findings:

- **`implausible` contributes nothing to the asymmetry — zero, in all four
  scenarios.** Implausible runs are implausible on both bodies, so they leave
  the paired subset symmetrically and do not bias it. That is not obvious a
  priori: S1_F alone carries 23 implausible runs and S1_M carries 11.
- The asymmetry is carried by `not_steady_state`, plus **9 of the 20 male
  divergences** (1 in S2, 3 in S3, 5 in S4). The other 11 male divergences fall
  on configurations that were also non-clean on the female body, so they cost
  the paired subset nothing.

---

## 6. Conclusion

A paired between-body analysis is **technically feasible in all four
scenarios**, on 34 / 69 / 111 / 51 matched configurations.

It answers a **restricted question**: the difference between the two bodies
*among the configurations that are clean on both*. It does not recover the
regions where numerical stability itself differs between bodies — those must
continue to be analysed separately, as a selection and failure result rather
than as a physiological one. That is the same entanglement §2.5 already
concedes, narrowed rather than dissolved.

Two constraints must travel with any paired result:

1. **FiO₂ truncation in S1 and S4** (§4.2), which is where two of the five
   surviving distances live.
2. **The ventilation-dose mismatch is not removed by pairing** (§2, check 4).
   Matched grid points still deliver +19.8 % / +36.1 % more tidal volume per
   kilogram to the female body, because the sweep varies Vt in absolute
   millilitres. Pairing fixes the selection confound; it does not fix the dose
   confound. Both remedies named in §2.5 are needed, and only the first is
   available from the existing data.

---

## 7. Not done, deliberately

- No hypothesis test of any kind (§ header).
- Nothing written into `paper.tex`, `supplement.tex` or `manuscript.md`.
- No claim about what a paired analysis *would* show.
- The pooled `aggregated.parquet` and `morris_sample.parquet` in the same
  directory were not used: the first is derived from the eight per-cell files,
  the second is the input design rather than run output.
