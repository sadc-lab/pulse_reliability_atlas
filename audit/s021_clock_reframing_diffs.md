# S021 — the two clocks: reframing register

**Opened 2026-08-06.** Trigger: the manuscript described the S021 hyperoxia
reruns as a *saved-state continuation* — a reload of Pulse's engine state at
the end of the original 120-second run, continuing for 300 more seconds. That
mechanism does not exist in this repository. The reruns are **separate
re-executions from time zero** with the recorded duration raised from 120 s to
300 s.

No published number changes. What changes is the described mechanism, the time
axis label, and one anchor that was passing for the wrong reason.

---

## 1. Ground truth, measured

| Fact | Source | Value |
|---|---|---|
| Rerun builds a fresh config, then overrides duration | `scripts/run_s021_hyperoxia_convergence.py:221-230` | `build_config(...)` then `cfg["duration_hours"] = 300/3600` |
| No serialisation / state reload anywhere | same file, full read | 0 occurrences |
| Plateau window | `run_s021_hyperoxia_convergence.py:93`; `summary.json` | `[240.0, 300.0]` s |
| Ventilator settle phase | `engine/run_atlas_engine.py:92`, `:234-235` | `VENT_SETTLE_S = 120.0`, applied **after** the ventilator is connected |
| Only two time advances in the engine | `engine/run_atlas_engine.py:235`, `:256` | settle, then the recording loop |
| Recording origin | `engine/run_atlas_engine.py:242-243` | CSV `t=0` is **after** the settle; 120 s is subtracted off |

### The two clocks

Pulse's native CSV carries the engine's own clock, undisplaced:

- original sweep run: `0.02 → 240.00` s → **240 s** = 120 settle + 120 recorded
- S021 rerun: `0.02 → 420.00` s → **420 s** = 120 settle + 300 recorded

**`420 seconds of total simulated time` is therefore TRUE**, and measured, not
inferred. It was never the defect. The trap is that `120 + 300 = 420` under
*both* the false reading (120 s original run + 300 more) and the true one
(120 s settle + 300 recorded) — the number was right while the mechanism was
wrong, which is exactly why it survived review.

The native clock starting at `0.02` s also shows `initialize_engine` consumes
**no** simulated time, so 420 s has no hidden third term.

**Vocabulary decided (maintainer, 2026-08-06):**

- *recorded simulation time* — 0–300 s, the CSV and every figure axis;
- *Pulse-internal time* — 420 s, settle included.
- **`total simulated time` is never used unqualified again.**

### Determinism: 60/60, twice, with a calibrated harness

Two independent instruments, both bash, neither sharing code with the analysis:

| Instrument | Artefact | Shared interval | Points | Result |
|---|---|---|---|---|
| `diff` | `output.csv` (atlas, 5 s) | t = 0–120 s | 25 | **60/60 identical**, 0 different, 0 missing |
| `cmp` (byte) | `output_pulse_native.csv` (50 Hz) | t = 0.02–240.00 s | **12,000** | **60/60 identical**, 0 different, 0 missing |

The native comparison spans the **settle phase itself**, so the 120 s settle is
proven identical between the original run and its rerun — not merely assumed.

Harness calibrated before being believed (per
`feedback_calibrate_tools_before_trusting`):

- negative control A — rerun vs a *different* run's original → DIFFERENT ✓
- negative control B — correct pair, **one digit** mutated → DIFFERENT ✓
- positive control — correct pair, untouched → IDENTICAL ✓

Scope of the claim: the **CSV artefacts** were compared, not the engine's
internal memory state. Cohort coverage: 22 S1_F + 22 S1_M + 4 each of S3_F,
S3_M, S4_F, S4_M = 60.

---

## 2. The preregistered log was already correct

`experiments_log/santino/S021_hyperoxia_convergence.md` contains **zero**
occurrences of *saved*, *reload* or *resum*. It states the protocol correctly
throughout:

- `:105` "rerun with **identical inputs**"
- `:108` "300 s recorded simulation instead of the locked 120 s"
- `:113-115` "The 120 s settle phase … is **not** changed"
- `:119` "on the recorded `[0, 300] s` PaO2 trajectory"
- `:121-123` plateau = mean over `[240, 300] s`
- `:174` "S021 is 420 s Pulse-internal" (against 240 s for the full sweep)

**The error was born in the write-up, not in the protocol.** The dated addendum
must say so; it must not imply the log carried the wrong description.

---

## 3. Physiological boundary — do not generalise the hyperoxia clause

The clause "PaO₂ is already hyperoxic at recorded t = 0, because the configured
FiO₂ applies during the preceding 120-s settling phase" is **true for S1 only**.

Measured PaO₂ at recorded t = 0 (index 0006, FiO₂ = 1.0):

| Cell | t = 0 | t = 300 |
|---|---:|---:|
| S1_F | 649.4 | 668.5 |
| S3_F | 217.8 | 254.4 |
| S3_M | 175.8 | 183.8 |
| S4_F | 57.1 | 73.3 |
| S4_M | 53.4 | 67.2 |

In S4 the patient is **hypoxaemic at FiO₂ = 1.0**, not hyperoxic — the expected
behaviour of a true shunt, which is poorly responsive to inspired oxygen. The
clause belongs in the Figure S3 caption and the §S9 paragraph, both scoped to
the S1 cohort, and nowhere else.

---

## 4. Cascade measured before drafting

- **Ledger:** among the durations, only `180.0` is an anchored
  `manuscript_value` (`audit_claims.py:2939`, T1.06u). **300, 420 and 240 are
  not anchored.** Correcting the prose breaks no numeric anchor.
- **Crosswalk:** the only duration-bearing counter is
  `'120 seconds of simulated time'` × 1 (`paper_to_monograph_map.md:723-724`),
  which lives in Methods §4.3 and is **not** among the loci below.
  `'643~mmHg'` × 3 (`:93-96`) is likewise untouched.
- **Two distinct `240`s exist in the corpus** — the plateau window `[240, 300]`
  and the original sweep's "240 s Pulse-internal" (log `:174`). Never anchor a
  bare `240`.
- `manuscript.md:3905` contains `420` inside **PMID 36661420**. Any guard must
  exclude it.

---

## 5. The T1.23 anchor is CORRECT — a claimed defect, withdrawn

**An earlier revision of this register claimed the 643 mmHg anchor was passing
for the wrong reason. That claim was wrong and is withdrawn.** It compared the
*supplement's* prose against an anchor that audits the *monograph*. The ledger
audits `preprint/manuscript.md`; the crosswalk is what relates the paper to it.

What each document actually says:

| Document | Locus | Stated quantity | Value |
|---|---|---|---|
| Monograph | `manuscript.md:2664`, `:2684` | "**S1 (n = 44):** plateau median 643.3 mmHg" | `S1_plateau_median_mmHg` = **643.3063** |
| Supplement | `supplement.tex:654` | "converged-subset median … over all **41** drift-converged runs" | `S1_converged_plateau_median_mmHg` = **642.8716** |
| Paper | `paper.tex:302` | "the **converged** S1 plateau median was 643~mmHg" | same 41-run quantity |

`audit_claims.py:918` points at `S1_plateau_median_mmHg`, which is **exactly**
what the monograph asserts (n = 44, 643.3). **Do not repoint it.** Repointing
to the 41-run median would make the anchor check a quantity the monograph does
not claim, and would silently unguard the explicit `643.3` at `:2664`/`:2684`.

Every figure is nonetheless accurate: 642.8716 rounds to 643, so the paper's
and supplement's "643~mmHg" for the 41 converged runs is exact.

### What remains — a coverage gap, not a defect

**No layer verifies the 41-run quantity (642.87).** The crosswalk counts the
*string* `643~mmHg` (3 occurrences: `paper.tex:118`, `:302`,
`supplement.tex:654`) without checking which quantity produced it, and the
ledger checks the 44-run median only. If the converged-subset median drifted,
nothing would see it.

Closing that gap means **adding** an anchor (382 → 383), not correcting one.
Maintainer decision — deliberately left open.

⚠️ Recorded so the arithmetic is not re-derived: the two medians differ by
**0.4348**, and `whole_unit = 0.5` (`audit_claims.py:111`). No tolerance ≥ 0.44
can separate them; both pass against a `manuscript_value` of 643.0. Any
negative test built by swapping one median for the other therefore **cannot
fail**, whichever way the pointer runs.

---

## 6. Sequencing — the proposed order blocks itself

`.githooks/pre-commit:94` runs
`audit_claims.py --check-paper-sync --check-monograph` and **aborts the commit
on failure**; `.github/workflows/tests.yml` runs it too.
**`check_render.py` is wired into neither.**

Consequences:

- A negative guard added to `audit_claims.py` **before** the loci are fixed
  **blocks its own commit** — the forbidden strings are still in the text. Same
  shape as the ledger trap: anchors land *with* their prose, never before it.
- A negative guard added to `check_render.py` never runs automatically. That is
  precisely the failure mode that let the retracted "2/20" survive seven weeks
  in the README.

**Revised order:**

1. `[AUDIT]` this register alone (§5 carries a withdrawn claim; no code
   change). Self-contained, changes no prose, passes the hook on its own.
2. `[PAPER+SUPP+MONOGRAPH+FIGURES]` the 12 loci **and** the negative guard, in
   **one** commit — guard and corrected prose must be atomic.
3. `[S032-style] [EXPERIMENT LOG]` dated addendum to the S021 log (§2).
   ⚠️ `.githooks/pre-commit:55-71` regenerates *and stages* `INDEX.md`; a log
   file must be committed **with or before** the rest.
4. Regenerate `fig_s3_hyperoxia_convergence.{pdf,png}`, rebuild PDFs/DOCX,
   verify the rendered axis label, re-run the audit.

---

## 7. The 12 loci

Legend: `−` current, `+` proposed. Surgical: only the marked clause changes.

### L0 — `preprint_npj/supplement.tex:654` (found late, in the "extended" sweep)

```
− converged to a stable plateau under a 300-second extended simulation
+ converged to a stable plateau under a 300-second rerun
```

⚠️ **Chirurgical, obligatoire:** this same line carries one of the three
crosswalk-counted `643~mmHg` strings, and the clause "(the per-run plateau
median over all 41 drift-converged runs)" is **already correct** — §5. Touch
neither. Post-edit check: `643~mmHg` must still total 3 across
`paper.tex` + `supplement.tex`.

### Deliberately NOT touched

`supplement.tex:678`, `:335`, `:104` ("extended window(s)") and
`manuscript.md:70`, `:313` ("an extended 300 s rerun") carry **no** false
mechanism — the recording window genuinely is longer. Editing them would widen
the scope without repairing a defect.

### L1 — `preprint_npj/paper.tex:302`

```
− Each rerun resumed from Pulse's saved engine state at the end of the original
  120-second run and continued for an additional 300 seconds (420 seconds of
  total simulated time), with the plateau computed from the final 60 seconds of
  the extension (Supplement~\S\,\ref{sec:s9}).
+ Each configuration was re-executed from time zero with the recorded
  simulation duration raised from 120 to 300 seconds, and the plateau computed
  over the final 60 seconds of that window ($t = 240$--$300$~s;
  Supplement~\S\,\ref{sec:s9}).
```

Also in the same sentence: "A preregistered 60-run extended-simulation
experiment" → "A preregistered 60-run longer-rerun experiment".

### L2 — `preprint_npj/paper.tex:304`

```
− hyperoxia studies on Pulse should be run for at least 300 seconds of total
  simulated time (the point by which PaO$_2$ reaches approximately 95~\% of its
  plateau) before extracting a steady-state plateau.
+ hyperoxia studies on Pulse should record at least 300 seconds of simulated
  time before extracting a steady-state plateau; 95~\% of the increase from the
  $t = 0$ value to the late plateau is reached by $t = 180$~s
  (Supplement~\S\,\ref{sec:s9}).
```

Rationale: `audit_claims.py:2932` computes
`_target = _floor + 0.95*(_asymptote − _floor)` — 95 % of the **gain**, not of
the plateau. 95 % of the plateau ≈ 607 mmHg; 95 % of the gain ≈ 635 mmHg. The
two are not interchangeable, and this sentence is operator-facing guidance.

Later in the same line: "Extended-window simulations" → "Longer-rerun
simulations"; "extended window" → "300-second rerun" (2 occurrences).

### L3 — `preprint_npj/supplement.tex:658`

```
− Each S021 rerun reloads Pulse's saved engine state from the end of the
  original locked 120-second simulation and continues for an additional 300
  seconds (420 seconds of total simulated time), sampled into the
  atlas-aggregated CSV at 5-second intervals. The figure x-axis is the elapsed
  time since the rerun start ($t' = 0$ corresponds to the end of the original
  120-second window, the saved-state reload point); the figure therefore
  visualises the \emph{late-phase convergence} of PaO$_2$ toward its true
  plateau, not a fresh wash-in from atmospheric-air baseline.
+ Each S021 rerun re-executes the same configuration from time zero with the
  recorded simulation duration raised from 120 to 300 seconds, sampled into the
  atlas-aggregated CSV at 5-second intervals. Each run retains the unchanged
  120-second ventilator-settling phase that precedes recording, so one rerun
  spans 420~s of Pulse-internal time in total; all reported times and figures
  use recorded simulation time, $t = 0$--$300$~s. The figure x-axis is that
  recorded time. Pulse is deterministic, and across all 60 reruns the
  atlas-aggregated CSVs are byte-identical to those of the corresponding
  120-second runs over the shared recorded interval $t = 0$--$120$~s: these are
  separate deterministic re-executions of the same configurations, not
  saved-state continuations. PaO$_2$ is already hyperoxic at $t = 0$ in this S1
  cohort, because the configured FiO$_2$ of 1.0 applies throughout the
  preceding settling phase, so the figure visualises the \emph{late-phase
  convergence} of PaO$_2$ toward its true plateau, not a fresh wash-in from an
  atmospheric-air baseline.
```

### L4 — `preprint_npj/supplement.tex:663` (Figure S3 caption)

Three clauses:

```
− Late-phase PaO$_2$ convergence in the S021 extended-simulation reruns
+ Late-phase PaO$_2$ convergence in the S021 300-second reruns

− The figure x-axis ($t'$) is the elapsed time since the rerun start; the rerun
  continues from the saved Pulse state at the end of the original 120-second
  window, so $t' = 0$ corresponds to $t = 120$~s of the original simulation
  timeline rather than to atmospheric-air baseline.
+ The figure x-axis is the rerun's own recorded simulation time $t$, from 0 to
  300~s. The rerun is a re-execution of the same configuration from time zero,
  not a continuation of the original run; PaO$_2$ is nevertheless already
  hyperoxic at $t = 0$, because the configured FiO$_2$ of 1.0 is in effect
  through the unchanged 120-second settling phase that precedes recording, so
  $t = 0$ is not an atmospheric-air baseline.

− rises from approximately 552~mmHg at the rerun reload point to approximately
  639~mmHg at $t' = 300$~s; 95~\% of that late-plateau gain is reached at
  $t' = 180$~s
+ rises from approximately 552~mmHg at $t = 0$ to approximately 639~mmHg at
  $t = 300$~s; 95~\% of that late-plateau gain is reached at $t = 180$~s
```

The values 552 / 639 / 180 are unchanged — they were always computed on the
0–300 s trajectory. Only the label was wrong.

### L5 — `preprint_npj/supplement.tex:676`

```
− The kinetic anchor (180 seconds of extended simulation to reach 95~\% of the
  late plateau on the 38 physiological-converged runs, starting from the saved
  state at the end of the original 120-second window)
+ The kinetic anchor (95~\% of the late-plateau gain reached by $t = 180$~s of
  recorded simulation on the 38 physiological-converged runs)

− simulating for at least 300 seconds of total simulated time and computing the
  steady-state mean over the final 60 seconds of that window
+ recording at least 300 seconds of simulated time and computing the
  steady-state mean over the final 60 seconds of that window ($t = 240$--$300$~s)
```

### L6 / L7 — `supplement.tex:682` and `:686`

```
− the final 60~s of the 300~s extension
+ the final 60~s of the 300~s rerun ($t = 240$--$300$~s)
```

`:682` also: "The extended-simulation experiment also replayed" → "The
300-second rerun experiment also replayed".
`:686` caption also: "in the S021 extended-simulation reruns" → "in the S021
300-second reruns".

### L8 — `preprint/manuscript.md:140`

```
− * Extended reruns ([S021](#s021); 300 s beyond the locked 120 s window = 420 s total) resolve it:
+ * Longer reruns ([S021](#s021); the same configurations re-executed at 300 s of recorded simulation instead of the locked 120 s) resolve it:
```

### L9 — `preprint/manuscript.md:2654`

```
− at FiO2 = 1.0 with the simulation extended by a further 300 s beyond the 120 s window, to 420 s of total simulated time
+ at FiO2 = 1.0, each re-executed from time zero with the recorded simulation duration raised from the locked 120 s to 300 s
```

### L10 — `scripts/make_supp_fig_s3.py` (4 lines)

`:2` — "from the S021 hyperoxia 300-second rerun cohort." → unchanged, already
correct.

`:4-10` docstring — currently self-contradictory: line 5 says plot `t=0` equals
`t=120 s` of the overall timeline, line 8 says the run goes "out to t=300s of
overall simulation time"; under its own premise that would be 420.

```
− t=0 on the plot corresponds to t=120s of the overall simulation timeline.
  The S021 reruns continue from the saved Pulse state at the end of the
  original locked 120-second window (where PaO2 was already in the
  hyperoxia regime) out to t=300s of overall simulation time.
+ The x-axis is the rerun's own recorded simulation time, t = 0 to 300 s.
  Each rerun is a separate re-execution of the same configuration from time
  zero, with the recorded duration raised from 120 s to 300 s — not a
  saved-state continuation. PaO2 is already hyperoxic at t = 0 because the
  configured FiO2 = 1.0 applies through the unchanged 120 s ventilator-settle
  phase that precedes recording.
```

`:102` xlabel — **this one reaches the rendered PDF**:

```
− r"Extended-simulation time $t'$ (s); $t' = 0$ corresponds to $t = 120$ s of the original simulation"
+ r"Recorded simulation time $t$ (s) --- 300-s rerun"
```

`:118-119` and `:128` prints — drop the `t'=0 (= t=120 s original)` and
`t'=300 (= t=300 s extended)` glosses; use `t=0` and `t=300`.

Then regenerate `fig_s3_hyperoxia_convergence.{pdf,png}` and verify the axis in
the rendered PDF, not only in the source.

### L11 — `scripts/audit_claims.py:2894-2895` (comment only, no literal)

```
− The "floor" is the median PaO2 at t=0 of the extended-simulation
  rerun (saved-state reload point, corresponding to the end of the
  original 120-second window)
+ The "floor" is the median PaO2 at t=0 of the 300-second rerun
  (recorded simulation time; the rerun re-executes from time zero, so
  t=0 follows the unchanged 120 s ventilator-settle phase)
```

---

## 8. Negative guard — target mechanisms, not the number 420

**Forbidden strings** (all currently present; all gone after §7):

- `saved engine state`
- `saved-state continuation`
- `saved Pulse state`
- `reload point`
- `continued for an additional 300`
- `300 s beyond the locked 120 s`
- `beyond the 120 s window`
- `120 s window = 420 s total`
- any equation of `t' = 0` with the end of the original run

**Do NOT forbid `420 seconds` / `420 s`** — the quantity is true and measured
(§1). Exclude `manuscript.md:3905` (PMID 36661420) explicitly.

**Positive controls — per file, on the strings actually written.**

⚠️ The maintainer's draft spec asked for `300-s rerun` and `t=240–300 s`.
**Neither string exists in the corrected text.** A guard built on them would
never match. The LaTeX forms below are authoritative:

| File | Required string (literal) |
|---|---|
| `paper.tex` | `300-second rerun` |
| `paper.tex` | `$t = 240$--$300$~s` |
| `supplement.tex` | `420~s of Pulse-internal time` |
| `supplement.tex` | `recorded simulation time` |
| `supplement.tex` | `120-second ventilator-settling phase` |
| rendered `fig_s3_hyperoxia_convergence.pdf` | `Recorded simulation time` |

Scope is per file by construction: `Pulse-internal time` is required in
`supplement.tex` and **must not** be required in `paper.tex`, which keeps only
the 300 s recorded clock (maintainer decision, 2026-08-06). A repo-wide
requirement would fail on the paper by design.

---

## 9. Reservations

- The byte-identity claim covers the **CSV artefacts**, not the engine's
  internal memory state. The published sentence says exactly that.
- `_asymptote` in `audit_claims.py:2931` is the median at t = 300 s, i.e. the
  last observed value, not a fitted asymptote. The prose says "late plateau",
  which is accurate; the variable name is looser than the claim.
- `t_95 = 180` s was not recomputed here directly; it is confirmed indirectly
  and rigorously by the ledger passing 382/382 with `whole_unit` tolerance on a
  5-second sampling grid, which admits only 180.
