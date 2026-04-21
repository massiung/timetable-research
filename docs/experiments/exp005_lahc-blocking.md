# exp005: lahc-blocking

**Branch:** exp/lahc-blocking
**Date:** 2026-04-21
**Solver:** local_search
**Status:** pending decision

## Hypothesis

exp004 restored `constrained_first` init and improved avg_cost by 7.9% vs exp003.  Two
remaining problems:

1. **Local optima**: strict best-improvement acceptance (exp004) gets trapped early. Late
   Acceptance Hill Climbing (LAHC, L=100) accepts candidates with `obj ≤ history[h]`
   (objective seen 100 iterations ago), allowing temporary uphill moves to escape local
   optima. Expected to reduce avg_cost on most instances.
2. **i16 infeasible (2 violations)**: the blocking destroy operator is added to the rotation
   (25% weight alongside the 3 standard ops) whenever the working solution has unscheduled
   mandatory patients. It specifically removes non-mandatory patients from the target
   mandatory's feasible room/day windows, giving the rescue pass room to place the mandatory.
   Expected to fix i16 feasibility.

## Changes vs. Previous Kept Experiment

Built on `exp/lahc-blocking` (branched from main after exp004 merge):

- `src/solvers/local_search.py`:
  - Update acceptance: LAHC with L=100. Accept if `obj ≤ history[h]`; always store
    `history[h] = obj`. On reject, reset current to best.
  - Add `current_infeasible` flag (tracks working solution, not just best) for correct
    rescue-skip with LAHC-accepted non-best solutions.
  - Add `_destroy_blocking_mandatory`: when `current_infeasible`, expand rotation to
    `[random, related, high_delay, blocking]` — each with equal 25% weight.
  - `LNSConfig`: add `lahc_history_length: int = 100`.
- `tests/test_local_search.py`: add `_destroy_blocking_mandatory` import, `lahc_history_length`
  assertion, and two tests for `_destroy_blocking_mandatory`.

## Results

| Instance | Cost | Violations | Time (s) |
|----------|------|------------|----------|
| i01 | 5531 | 0 | 60.00 |
| i02 | 2524 | 0 | 60.00 |
| i03 | 12120 | 0 | 60.00 |
| i04 | 4360 | 0 | 60.00 |
| i05 | 14777 | 0 | 60.00 |
| i06 | 11782 | 0 | 60.00 |
| i07 | 7909 | 0 | 60.00 |
| i08 | 9270 | 0 | 60.00 |
| i09 | 12562 | 0 | 60.00 |
| i10 | 32750 | 0 | 60.00 |
| i11 | 32008 | 0 | 60.00 |
| i12 | 16530 | 0 | 60.00 |
| i13 | 26945 | 0 | 60.00 |
| i14 | 16549 | 0 | 60.00 |
| i15 | 23785 | 0 | 60.00 |
| i16 | — | 1 | 60.00 |
| i17 | 78140 | 0 | 60.01 |
| i18 | 48233 | 0 | 60.00 |
| i19 | 72329 | 0 | 60.01 |
| i20 | 45098 | 0 | 60.00 |
| i21 | 42094 | 0 | 60.00 |
| i22 | 100094 | 0 | 60.01 |
| i23 | 58628 | 0 | 60.00 |
| i24 | 44259 | 0 | 60.01 |
| i25 | 19741 | 0 | 60.00 |
| i26 | 111424 | 0 | 60.00 |
| i27 | 106126 | 0 | 60.01 |
| i28 | 88801 | 0 | 60.00 |
| i29 | 25212 | 0 | 60.00 |
| i30 | 49637 | 0 | 60.00 |

**avg_cost:** 38593.7
**avg_time_s:** 60.00
**n_feasible:** 29 / 30

## Conclusion

**Decision:** discard

- avg_cost 38593.7 vs exp004's 38415.3 — **+0.47% regression**. LAHC + blocking is strictly worse.
- i16 improved from 2 violations (exp004) to 1 violation — blocking destroy is doing something, but 60 s is still not enough to achieve feasibility.
- i20 large regression: 45098 vs 42267 (+6.7%). LAHC acceptance of worse solutions during the rescue phase led the search astray; i20 starts infeasible with constrained_first and LAHC probably accepted some high-penalty intermediate states.
- LAHC with L=100 and "reset to best on reject" is neutral-to-slightly-harmful. The history fills with rejected candidate objectives, making acceptance progressively more permissive, but this effect wastes iterations rather than finding better solutions.
- Blocking destroy alone (without LAHC) is worth isolating: it reduced i16 violations from 2→1.

## What to try next (exp006)

1. **Drop LAHC, keep blocking destroy** — isolate the blocking destroy effect without LAHC noise. Start from exp004 code and add only the blocking destroy operator.
2. **Surgeon-aware blocking destroy** — i16's bottleneck is surgeon capacity on day 4 (not just room availability). Extend the blocking destroy to also remove patients using the same surgeon on the mandatory patient's only feasible day. This directly addresses the true constraint.
