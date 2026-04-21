# exp004: constrained-first-restore

**Branch:** exp/constrained-first-restore
**Date:** 2026-04-21
**Solver:** local_search
**Status:** pending decision

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
| i01 | 5532 | 0 | 60.00 |
| i02 | 2495 | 0 | 60.00 |
| i03 | 12120 | 0 | 60.00 |
| i04 | 4401 | 0 | 60.00 |
| i05 | 14655 | 0 | 60.00 |
| i06 | 11799 | 0 | 60.00 |
| i07 | 7824 | 0 | 60.00 |
| i08 | 9087 | 0 | 60.00 |
| i09 | 12694 | 0 | 60.00 |
| i10 | 32500 | 0 | 60.00 |
| i11 | 32103 | 0 | 60.00 |
| i12 | 16357 | 0 | 60.00 |
| i13 | 27108 | 0 | 60.00 |
| i14 | 16447 | 0 | 60.00 |
| i15 | 23510 | 0 | 60.00 |
| i16 | — | 2 | 60.00 |
| i17 | 76375 | 0 | 60.00 |
| i18 | 48164 | 0 | 60.00 |
| i19 | 71645 | 0 | 60.01 |
| i20 | 42267 | 0 | 60.00 |
| i21 | 41868 | 0 | 60.00 |
| i22 | 100496 | 0 | 60.00 |
| i23 | 58246 | 0 | 60.01 |
| i24 | 44255 | 0 | 60.02 |
| i25 | 19815 | 0 | 60.00 |
| i26 | 112191 | 0 | 60.01 |
| i27 | 106923 | 0 | 60.01 |
| i28 | 88591 | 0 | 60.00 |
| i29 | 25020 | 0 | 60.00 |
| i30 | 49556 | 0 | 60.01 |

**avg_cost:** 38415.3
**avg_time_s:** 60.00
**n_feasible:** 29 / 30

## Conclusion

**Decision:** keep

- avg_cost 38415.3 vs exp003's 41728.0 — a **-7.9% improvement** (over 29 feasible instances each).
- 28 of the 29 feasible instances improved vs exp003; i09 regressed slightly (+10.4%, 12694 vs 11494).
- i20 remains feasible (rescue handles the constrained_first infeasibility from exp001).
- i16 worsened to 2 violations (from exp003's 1). The constrained_first ordering appears to place other mandatory patients in a way that makes p053's window harder to repair in 60 s. Targeted destroy for exp005.
- Rescue-skip is effective: for the 29 feasible instances rescue is skipped on almost every iteration (only triggered when a mandatory patient is in the destroyed set).

## What to try next (exp005)

1. **Late Acceptance Hill Climbing (LAHC)**: replace strict best-improvement acceptance with LAHC (accept if `obj ≤ history[h]`, history length L=100). Allows temporary escapes from local optima; expected to improve cost across all instances, especially larger ones.
2. **Blocking destroy**: when working solution has unscheduled mandatory patients, add a "blocking" destroy operator to the rotation that removes non-mandatory patients occupying the target mandatory's feasible placement windows. Should directly help i16 recover feasibility.
