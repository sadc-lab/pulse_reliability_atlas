---
id: S030
author: santino
date: 2026-07-26
status: done
tags: [ards, berlin-calibration, replication, hr-rr-bounds, pointer-entry]
linked_code:
  - scripts/run_s030_ards_berlin_recalibration.py
  - scripts/analyze_s030.py
  - scripts/run_s030b_severe_and_bounds.py
  - scripts/analyze_s030b.py
  - scripts/audit_s030_provenance.py
linked_data:
  - data/runs/s030_ards_berlin_recalibration/
  - data/runs/s030b_severe_and_bounds/
  - results/s030_published_value_provenance.csv
supersedes: ""
related: []
---

# S030 — In-repository replication of the ARDS severity → Berlin calibration, and of the HR / RR acceptance bounds

> **Pointer entry, added on 2026-10-12.** S030 ran on 2026-07-26, but at the
> time it was documented in `audit/`, not in this notebook. This entry only
> points to those records so that the notebook has no gap. It adds no result.

## Hypothesis

No separate hypothesis section was written. The plan set out to reproduce,
inside this repository, the companion project's severity → P/F calibration
and its HR / RR acceptance bounds; for the HR / RR probes, the expected result
of each probe is given in the "attendu" column of the probe table. See "Why",
"Second experiment, also pending — HR / RR acceptance bounds" and "Bloc 2" in
`audit/S030_recalibration_plan.md`.

## Motivation, method, results and interpretation

- `audit/S030_recalibration_plan.md`: motivation ("Why"), protocol, design,
  results of S030 (40 runs) and S030b (16 runs), and what the paper claims.
  Closed on 2026-08-13.
- `audit/s030_published_value_provenance.md`: provenance of the S030 values
  published in Supplement §S5 (2026-08-13).

## Next steps

None — question closed (2026-08-13).
