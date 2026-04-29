# exp020: window-sort

**Branch:** exp/window-sort
**Date:** 2026-04-28
**Solver:** local_search
**Status:** discard

## Hypothesis

exp019 confirmed that perturbation direction doesn't help — randomness is beneficial.
exp015/017 confirmed regret repair is too expensive (halves iteration count). 

The exp011 repair sort uses (mandatory, last_possible_day, -surgery_duration) — deadline-first.
Two patients with the same deadline but different release days get equal priority, even though
the one with a later release day has a narrower feasible window and is actually harder to place.

**Window sort**: sort by `(mandatory, last_possible_day − surgery_release_day, -surgery_duration)`.
This is O(1) per patient (no extra lookups) and places the most scheduling-constrained patients
first — those with the fewest feasible days. For patients sharing a deadline, those released later
(shorter window) come first.

**Hypothesis**: window sort improves placement quality in the repair step with zero iteration
overhead. Expected: 1–3% improvement over exp011 (37675.6) at 1-worker/60s.

**Changes**: single key change in `_repair_patients` sort. No ALNS, no regret. `num_workers=1`.

## Changes vs. Previous Kept Experiment

Built on `main` (after exp016 merge — includes regret-2 repair + ALNS), reverting to clean baseline:

- `src/solvers/local_search.py`:
  - Remove `_INF_COST` constant and `_compute_insertion_regret` function.
  - Change `_repair_patients` sort key from deadline-first to window-first:
    `(mandatory, last_possible_day − surgery_release_day, -surgery_duration)`.
  - Remove all ALNS code (config fields + runtime weight tracking).
  - Change `num_workers: int = 4` → `num_workers: int = 1`.

## Results

| Instance | Cost | Violations | Time (s) |
|----------|------|------------|----------|
| i01 | 5633 | 0 | 60.00 |
| i02 | 2407 | 0 | 60.00 |
| i03 | 12130 | 0 | 60.00 |
| i04 | 4501 | 0 | 60.00 |
| i05 | 14895 | 0 | 60.00 |
| i06 | 11764 | 0 | 60.00 |
| i07 | 8157 | 0 | 60.00 |
| i08 | 9001 | 0 | 60.01 |
| i09 | 12768 | 0 | 60.00 |
| i10 | 32720 | 0 | 60.00 |
| i11 | 32130 | 0 | 60.00 |
| i12 | 16852 | 0 | 60.00 |
| i13 | 27035 | 0 | 60.00 |
| i14 | 16706 | 0 | 60.01 |
| i15 | 24277 | 0 | 60.01 |
| i16 | 16285 | 3 | 60.00 |
| i17 | 77995 | 0 | 60.01 |
| i18 | 48056 | 0 | 60.01 |
| i19 | 70772 | 0 | 60.03 |
| i20 | 44492 | 0 | 60.01 |
| i21 | 42442 | 0 | 60.02 |
| i22 | 101132 | 0 | 60.01 |
| i23 | 58007 | 0 | 60.03 |
| i24 | 44219 | 0 | 60.01 |
| i25 | 19495 | 0 | 60.01 |
| i26 | 114222 | 0 | 60.03 |
| i27 | 107008 | 0 | 60.03 |
| i28 | 88751 | 0 | 60.01 |
| i29 | 25107 | 0 | 60.01 |
| i30 | 48529 | 0 | 60.01 |

**avg_cost:** 38662.2
**avg_time_s:** 60.01
**n_feasible:** 29 / 30

## Conclusion

**Decision:** discard

Window sort (narrowest feasible window first) gives 38662.2 — 2.6% WORSE than exp011 (37675.6).
i16 still infeasible. Root cause: sorting by window size groups patients with similar release days
together, creating surgeon/theater capacity bursts. Deadline-first sort implicitly spreads load
across time; window sort disrupts this beneficial spreading.

Key learning: the deadline-first sort in exp011 is already near-optimal for the repair step. Sort
changes consistently hurt. The remaining avenue is parameter tuning of the perturbation restart.
