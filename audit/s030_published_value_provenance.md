# Provenance of the S030 values published in Supplement §S5

**Opened and closed 2026-08-13.** Status: **gap closed** — the values are now
re-derived by a committed script into a committed artefact, and a guard binds
them to the manuscript. **No claim was changed and no manuscript file was
touched.** One decision is left open in §7.

This is a provenance dossier, not a new analysis. The science of S030 is closed
in `audit/S030_recalibration_plan.md`.

---

## 1. The gap

Supplement §S5 publishes numbers that existed in **no committed artefact**:

| locus | value(s) | why it was untraceable |
|---|---|---|
| `supplement.tex:421` | P/F 256.5 / 150.5 / 96.6 mmHg at the companion's [108, 168] s window | computed ad hoc for `abd1e5f`, which changed **one file, the register** (+60 lines) |
| `supplement.tex:421` | "within 0.6 %" and "within 2 %" | derived from those values |
| `supplement.tex:440` | alveolar PO₂ 231.4 → 230.7; A-a gradients 196.6 / 185.6 (free) and 184.9 (locked) | no CSV column holds alveolar PO₂ or the gradient |

`results/s030_pf_by_arm.csv` holds the [60, 120] and [240, 300] values, and
`results/s030b_analysis.csv` holds a [108, 168] column for impairment
0.96–0.99 **only** — not for the five companion fractions. No ledger anchor
covered any of it (`grep` over `scripts/audit_claims.py`: zero hits).

## 2. What was built

- `scripts/audit_s030_provenance.py` — re-derives every value from the S030 run
  CSVs and writes `results/s030_published_value_provenance.csv`
  (30 rows = 2 arms × 5 fractions × 3 windows), carrying per row the effective
  window (`n_samples`, `t_first_s`, `t_last_s`), the FiO₂ read from that run's
  own `config.json`, and the derived quantities.
- `check_s030_provenance()` in `scripts/audit_claims.py` — **26 checks**: each
  published literal against the artefact, the presence of each literal in
  `supplement.tex`, the two tolerance phrases, the two recomputed bounds, and
  the effective sample count of the three windows.

### Conventions, declared before the first number was computed

- **Tolerance 0.05 mmHg** against each published literal (they carry one
  decimal, so this means "rounds to the same printed value"), plus an explicit
  `round(x, 1) == published` check in the guard.
- P/F = mean(PaO₂ over window) / FiO₂, FiO₂ read per run (0.40 here).
- Alveolar PO₂ = FiO₂ × (760 − 47) − mean(PaCO₂) / 0.8 — the repository's own
  convention, the one that yields the 663 mmHg ceiling at FiO₂ = 1.0.
- A-a gradient = alveolar PO₂ − mean(PaO₂).

### Result

**12 / 12 re-derived values agree** with what is published, and the two bounds
hold with room to spare: max deviation 0.519 % on the three published fractions
(published bound 0.6 %) and 1.910 % across all five (bound 2 %). §S5's choice of
"0.6 %" is the correct one: 96.6 against the companion's 96.1 is +0.52 %, so
"within 0.5 %" would have been false.

One value sits on a rounding boundary and is correct: alveolar PO₂ recomputes to
**231.3504**, which rounds to 231.4 under round-half-up, as published.

## 3. My own instrument was wrong first, and the declared tolerance caught it

The first run of the script produced **4 misses out of 12**. The manuscript was
not at fault; the script was. It filtered windows with a ±1e-6 s slack, which
the producing scripts do not use.

That matters because the recorded time grid drifts: a nominal 120 s sample is
stored as **120.0000000000557** and a nominal 300 s sample as
**299.99999999991473**. With the slack the first is admitted, without it the
first is excluded and the second admitted. The free-arm 0.95 run therefore reads

| window | with slack (13 samples) | without slack (12 samples) | committed `s030_pf_by_arm.csv` |
|---|---:|---:|---:|
| [60, 120] | P/F 87.34 | **86.83** | **86.83** |
| [240, 300] | P/F 112.64 | **112.81** | **112.81** |

Diagnosis, before any change: the values were also recomputed from
`output_pulse_native.csv` at full 0.02 s resolution, mapped through the 120 s
ventilator settle (native [180, 240] ≡ recorded [60, 120]) — 87.34, i.e. the
5 s grid is an unbiased subsample and the gap was not a sampling-rate effect.
The convention was then read at the source (`scripts/analyze_s030.py:36-38` and
`scripts/analyze_s030b.py:52-54`) rather than guessed, and the script was
aligned to it. **Nothing was tuned to make a number fit: the comparison rule was
copied from the code that produced the published values.**

## 4. Finding: the effective windows are not the nominal ones

Because of that drift, the S030 analysis windows actually contain:

| nominal window | effective samples | effective span |
|---|---:|---|
| [60, 120] s | 12 | 60 – 115 s |
| [108, 168] s | 12 | 110 – 165 s (endpoints are off-grid; convention-insensitive) |
| [240, 300] s | 12 | 245 – 300 s |

The atlas's own detector uses a ±1e-6 slack for the same nominal window
(`src/detector.py:370-372`, 13 samples), so **the S030 analysis and the atlas
detector do not admit identical sample sets**. Measured consequence: 0.5 mmHg
of P/F at [60, 120] (86.83 vs 87.34, 0.6 %) and 0.18 mmHg at [240, 300].
**No Berlin band assignment changes** — 86.8 and 87.3 are both severe, 112.6 and
112.8 both moderate — and no published sentence moves. The guard pins the
sample count so a future regeneration under the other convention fails loudly
instead of silently shifting the published values.

## 5. Guard calibration, both directions

- **Negative, with the exact defect that motivated the guard**: the artefact's
  free/0.95/[60, 120] row was rewritten to the slack values (13 samples,
  alveolar 231.344, gradient 196.410). The guard returned **exit 1, 3 FAIL /
  23 PASS** — the alveolar literal, the gradient literal and the sample count.
  The injection was verified independently before running (the file contained
  `196.41` once and `196.6171` zero times), and the restoration was verified by
  MD5 against a pre-perturbation copy, not by trusting the copy command.
- **Missing artefact**: the file was moved away; the guard returned **exit 1**
  with `ABSENT / FAIL`. There is deliberately **no SKIP path** — a missing
  artefact can never read as a pass.
- **Positive**: 26 / 26 PASS on the restored artefact, whole audit exit 0.

## 6. Availability limit — stated, not masked by a SKIP

`data/runs/s030_ards_berlin_recalibration/**` is gitignored (`.gitignore:19-23`
excludes every `output.csv`, `pulse.log`, `config.json` and `run_meta.json`
under `data/runs/`). Consequences, exactly:

- the **artefact is committed**, so the guard is live on every clone;
- the **re-derivation is local-only**: on a clone without the raw runs,
  `scripts/audit_s030_provenance.py` prints that the runs are absent and
  recomputes nothing, and no layer re-checks the artefact against the runs;
- full public reproducibility therefore depends on the raw-run deposit planned
  with the release (`TODO_publication_roadmap.md` Phase 2, item 5).

This is an improvement in traceability, not a claim of public reproducibility,
and it is written here so the guard's green does not imply more than it is.

## 7. Open — an author decision, not applied

Should `scripts/analyze_s030.py` and `scripts/analyze_s030b.py` adopt the
detector's ±1e-6 slack, so that "the atlas window" means the same sample set
everywhere? It would move published numbers by up to 0.6 % (86.8 → 87.3;
112.8 → 112.6) **without changing any band, any conclusion or any hypothesis**,
and would require re-editing §S5 plus this artefact. The alternative is to keep
the published values and record the difference, which is what this register
does. **Nothing was changed either way.**
