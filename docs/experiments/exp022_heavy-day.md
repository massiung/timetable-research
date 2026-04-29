# exp022: heavy-day

**Branch:** exp/heavy-day
**Date:** 2026-04-29
**Solver:** local_search
**Status:** pending

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
| i01 | — | — | — |
| i02 | — | — | — |
| i03 | — | — | — |
| i04 | — | — | — |
| i05 | — | — | — |
| i06 | — | — | — |
| i07 | — | — | — |
| i08 | — | — | — |
| i09 | — | — | — |
| i10 | — | — | — |
| i11 | — | — | — |
| i12 | — | — | — |
| i13 | — | — | — |
| i14 | — | — | — |
| i15 | — | — | — |
| i16 | — | — | — |
| i17 | — | — | — |
| i18 | — | — | — |
| i19 | — | — | — |
| i20 | — | — | — |
| i21 | — | — | — |
| i22 | — | — | — |
| i23 | — | — | — |
| i24 | — | — | — |
| i25 | — | — | — |
| i26 | — | — | — |
| i27 | — | — | — |
| i28 | — | — | — |
| i29 | — | — | — |
| i30 | — | — | — |

**avg_cost:** —
**avg_time_s:** —
**n_feasible:** — / 30

## Conclusion

**Decision:** pending

<!-- What did we learn? -->
