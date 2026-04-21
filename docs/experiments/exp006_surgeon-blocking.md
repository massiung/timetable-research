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

## What to try next

TBD after results.
