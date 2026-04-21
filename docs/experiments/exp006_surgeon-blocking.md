# exp006: surgeon-blocking

**Branch:** exp/surgeon-blocking
**Date:** 2026-04-21
**Solver:** local_search
**Status:** pending decision

## Hypothesis

exp005 showed LAHC is harmful (+0.47% regression vs exp004) but blocking destroy reduced i16 violations 2→1.
Isolating the blocking destroy (without LAHC) should keep all exp004 gains while making further progress on i16.

Two improvements over exp005's blocking destroy:
1. **Drop LAHC** — revert to exp004's strict best-improvement acceptance.
2. **Surgeon-aware blocking destroy** — i16's bottleneck is surgeon capacity on day 4, not just room availability.
   Extend blocking destroy to also remove non-mandatory patients that compete for the same surgeon on the
   mandatory patient's only feasible surgery days. This directly targets the true constraint.

## Changes vs. Previous Kept Experiment

Built on `exp/surgeon-blocking` (branched from main after exp004 merge):

- `src/solvers/local_search.py`:
  - Add `best_infeasible` flag (already in exp004 — reused here).
  - Add blocking destroy dispatch in main loop: when `best_infeasible`, expand rotation to include `"blocking"` op alongside the 3 standard ops (uniform 25% weight each).
  - Add `_destroy_blocking_mandatory`: collects non-mandatory patients that are either (a) room-blocking in the target mandatory's feasible room/day windows, or (b) competing for the same surgeon on the mandatory's feasible surgery days. Falls back to random destroy if no blocking patients found.
- `tests/test_local_search.py`: add `_destroy_blocking_mandatory` import and two tests.

## Results

| Instance | Cost | Violations | Time (s) |
|----------|------|------------|----------|
| i01 | 5532 | 0 | 60.00 |
| i02 | 2495 | 0 | 60.00 |
| i03 | 12120 | 0 | 60.00 |
| i04 | 4401 | 0 | 60.00 |
| i05 | 14655 | 0 | 60.00 |
| i06 | 11799 | 0 | 60.00 |
| i07 | 7824 | 0 | 60.00 |
| i08 | 9089 | 0 | 60.00 |
| i09 | 12694 | 0 | 60.00 |
| i10 | 32985 | 0 | 60.00 |
| i11 | 32103 | 0 | 60.00 |
| i12 | 16357 | 0 | 60.00 |
| i13 | 27108 | 0 | 60.00 |
| i14 | 16447 | 0 | 60.00 |
| i15 | 23515 | 0 | 60.00 |
| i16 | — | 1 | 60.00 |
| i17 | 76440 | 0 | 60.01 |
| i18 | 48164 | 0 | 60.00 |
| i19 | 71645 | 0 | 60.00 |
| i20 | 45146 | 0 | 60.00 |
| i21 | 41868 | 0 | 60.00 |
| i22 | 100332 | 0 | 60.00 |
| i23 | 58246 | 0 | 60.01 |
| i24 | 44255 | 0 | 60.01 |
| i25 | 19795 | 0 | 60.00 |
| i26 | 112191 | 0 | 60.00 |
| i27 | 106921 | 0 | 60.01 |
| i28 | 88559 | 0 | 60.00 |
| i29 | 25007 | 0 | 60.00 |
| i30 | 49530 | 0 | 60.01 |

**avg_cost:** 38524.9
**avg_time_s:** 60.00
**n_feasible:** 29 / 30

## Conclusion

**Decision:** discard

- avg_cost 38524.9 vs exp004's 38415.3 — **+0.28% regression**. Surgeon-aware blocking destroy is strictly worse on average.
- i16 improved from 2 violations (exp004) to 1 violation — same as exp005, confirming the blocking destroy helps but 60 s is insufficient.
- i20 regression: 45146 vs 42267 (+6.8%). i20 starts infeasible with `constrained_first` init, so `best_infeasible=True` fires blocking destroy from the start. This disrupts early search instead of helping — the blocking destroy is counterproductive when infeasibility is transient (init artefact), not structural.
- Root cause: `best_infeasible` is a blunt trigger. It can't distinguish instances that are genuinely hard (i16, where mandatory p053 has very few feasible placements) from those that are merely transiently infeasible at startup (i20, where rescue quickly fixes things).

## What to try next (exp007)

1. **Rescue-count gating**: Gate blocking destroy on a `rescue_fail_streak` counter — only activate after N consecutive iterations where `_rescue_mandatory` failed to place any mandatory patient. This prevents blocking destroy firing during normal startup infeasibility (i20) while still activating for structural infeasibility (i16).
2. **Threshold N=50**: After 50 consecutive rescue failures, assume the mandatory is structurally stuck and trigger blocking destroy. Reset counter after any successful mandatory placement.
