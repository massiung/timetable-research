# exp022: heavy-day

**Branch:** exp/heavy-day
**Date:** 2026-04-29
**Solver:** local_search
**Status:** discard

## Hypothesis

All previous experiments at 1-worker/60s regressed vs exp011. Sort changes, ALNS, perturbation
tuning, targeted perturbation — none helped. One avenue untried: a new destroy operator.

The existing `high_delay` operator removes patients with the highest individual delay cost. But
delay cost is a symptom, not the cause. Days with many patients (heavy surgery load) create
capacity bottlenecks that force subsequent patients into later days. Removing patients from the
heaviest-load days directly attacks capacity constraints and may allow more patients to be placed
earlier.

**New operator `heavy_day`**: remove k patients starting from the days with the highest total
surgery duration. This is O(patients + days·log days) per call — no overhead vs existing ops.

**Hypothesis**: adding `heavy_day` as a 4th operator (25% probability, down from 33% for each
existing op) gives qualitatively different destroy patterns that find lower-cost solutions. The
capacity-focused perspective complements the delay-focused `high_delay` operator.

**Changes**: add `_destroy_heavy_day`; update `DestroyOp` type, `_default_ops`, and `_lns_worker`
dispatch. All other code identical to exp011: deadline-first repair, N=100, ratio=0.50,
num_workers=1.

## Changes vs. Previous Kept Experiment

Built on `main` (after exp016 merge), reverting algorithmic additions:

- `src/solvers/local_search.py`:
  - Remove `_INF_COST`, `_compute_insertion_regret`; restore deadline-first repair sort.
  - Remove ALNS config fields and runtime weight tracking.
  - Change `num_workers: int = 4` → `num_workers: int = 1`.
  - Add `_destroy_heavy_day` function.
  - Extend `DestroyOp` to include `"heavy_day"`.
  - Update `_default_ops` to `["random", "related", "high_delay", "heavy_day"]`.
  - Add `heavy_day` dispatch branch in `_lns_worker`.

## Results

| Instance | Cost | Violations | Time (s) |
|----------|------|------------|----------|
| i01 | 5578 | 0 | 60.00 |
| i02 | 2278 | 0 | 60.00 |
| i03 | 12120 | 0 | 60.00 |
| i04 | 4416 | 0 | 60.00 |
| i05 | 14820 | 0 | 60.00 |
| i06 | 11799 | 0 | 60.00 |
| i07 | 7896 | 0 | 60.00 |
| i08 | 9338 | 0 | 60.01 |
| i09 | 12686 | 0 | 60.00 |
| i10 | 32960 | 0 | 60.00 |
| i11 | 31965 | 0 | 60.00 |
| i12 | 16557 | 0 | 60.01 |
| i13 | 27046 | 0 | 60.01 |
| i14 | 16371 | 0 | 60.01 |
| i15 | 24547 | 0 | 60.00 |
| i16 | 16060 | 2 | 60.00 |
| i17 | 76595 | 0 | 60.01 |
| i18 | 48142 | 0 | 60.00 |
| i19 | 73412 | 0 | 60.01 |
| i20 | 43167 | 0 | 60.01 |
| i21 | 41973 | 0 | 60.01 |
| i22 | 101158 | 0 | 60.02 |
| i23 | 59249 | 0 | 60.02 |
| i24 | 44221 | 0 | 60.03 |
| i25 | 19943 | 0 | 60.01 |
| i26 | 112791 | 0 | 60.01 |
| i27 | 106971 | 0 | 60.01 |
| i28 | 88770 | 0 | 60.01 |
| i29 | 25094 | 0 | 60.02 |
| i30 | 49379 | 0 | 60.01 |

**avg_cost:** 38663.5
**avg_time_s:** 60.01
**n_feasible:** 29 / 30

## Conclusion

**Decision:** discard

`heavy_day` as 4th operator (25% each) gives 38663.5 — 2.6% WORSE than exp011 (37675.6).
i16 still infeasible. The new operator doesn't improve things: adding a 4th operator dilutes
each existing operator to 25% (from 33%), reducing their useful exploration. The capacity-based
targeting also doesn't help — high-load days contain many short surgeries on small instances,
so removing them doesn't target cost-driving patients.

Key learning: adding operators hurts by diluting the existing balanced mix. With 3 operators at
33% each, the solver already explores random/related/delay evenly. A 4th operator cannibalizes
from one of the existing three. The optimal operator set for this problem is the original 3.
