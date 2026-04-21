# exp005: lahc-blocking

**Branch:** exp/lahc-blocking
**Date:** 2026-04-21
**Solver:** local_search
**Status:** pending

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

**Decision:** keep / discard

<!-- What did we learn? See docs/learnings.md for any reusable insight. -->
