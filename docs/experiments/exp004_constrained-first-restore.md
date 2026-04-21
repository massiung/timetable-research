# exp004: constrained-first-restore

**Branch:** exp/constrained-first-restore
**Date:** 2026-04-21
**Solver:** local_search
**Status:** pending

## Hypothesis

exp003 showed an ~8.6% per-instance cost regression vs exp002 (over the 28 instances feasible in both).  Two causes were identified:

1. Switching from `constrained_first` to `urgency` greedy init gives a worse starting solution for most instances.
2. `_rescue_mandatory` runs a full O(n_patients) scan every iteration, reducing throughput even for the 29 instances where all mandatories are placed from the start.

Restoring `constrained_first` should recover most of the cost regression because the init produces better-cost starting schedules.  i20 (which was infeasible with `constrained_first` in exp001) should remain feasible thanks to the rescue pass introduced in exp003.

Skipping rescue when best is feasible and no mandatory patients were destroyed should increase iteration throughput for all 29 easy instances, giving the LNS more time to find better solutions.

## Changes vs. Previous Kept Experiment

Built on `exp/constrained-first-restore` (branched from main after exp003 merge):

- `src/solvers/local_search.py`:
  - Restore `constrained_first` greedy init: `GreedyConfig(patient_sort_key="constrained_first")`.
  - Pre-compute `mandatory_set` (frozenset of mandatory patient indices) once before the main loop.
  - Track `best_infeasible` flag: True when best has at least one unscheduled mandatory patient; updated whenever best improves.
  - Skip `_rescue_mandatory` call when `best_infeasible` is False and no mandatory patients are in `removed` — rescue cannot help in that case.

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
