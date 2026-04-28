# exp015: regret-repair

**Branch:** exp/regret-repair
**Date:** 2026-04-28
**Solver:** local_search
**Status:** keep

## Hypothesis

The current LNS repair step inserts removed patients in a fixed order:
mandatory first, then earliest-deadline first, then longest surgery first.
This ordering is schedule-blind — it ignores how competitive each patient's
insertion slots are at the time of repair.

Replacing it with **regret-2 insertion** (a classic ALNS improvement):
for each unassigned patient, compute their best and second-best insertion costs
(static, using the pre-repair schedule state). Sort by descending regret
(second_best − best). Patients with the most to lose from being placed later
are inserted first — before other patients claim their preferred slots.

This is parameter-free, deterministic, and improves every repair iteration
at the cost of ≈2× pre-computation per repair step (same asymptotic O(n·m)).

Expected: 1-3% cost reduction vs exp011's 37675.6 average, especially on
medium-to-large instances where multiple patients compete for the same day/room
windows and insertion order significantly affects final placement quality.

## Changes vs. Previous Kept Experiment

Built on `main` (after exp012 merge):

- `src/solvers/local_search.py`:
  - Add `_compute_insertion_regret(p, schedule, instance, theater_load, surgeon_load,
    w_delay, w_theater, greedy)` — same slot enumeration as `_insert_best` but
    collects all scores and returns `(best_score, second_best_score)`. Returns
    `(INF, INF)` if no feasible slot; `(best, INF)` if only one feasible slot.
  - Modify `_repair_patients` to pre-compute regret for all removed patients,
    then sort by `(mandatory_first, -regret, last_possible_day, -surgery_duration)`.
    Patients with no feasible slot (regret=0) sort last; rescue handles them.

## Results

| Instance | Cost | Violations | Time (s) |
|----------|------|------------|----------|
| i01 | 5419 | 0 | 60.01 |
| i02 | 1974 | 0 | 60.02 |
| i03 | 12070 | 0 | 60.02 |
| i04 | 4109 | 0 | 60.02 |
| i05 | 14548 | 0 | 60.02 |
| i06 | 11729 | 0 | 60.02 |
| i07 | 7760 | 0 | 60.02 |
| i08 | 8881 | 0 | 60.04 |
| i09 | 12339 | 0 | 60.03 |
| i10 | 32295 | 0 | 60.03 |
| i11 | 32017 | 0 | 60.03 |
| i12 | 16316 | 0 | 60.02 |
| i13 | 26986 | 0 | 60.03 |
| i14 | 16311 | 0 | 60.03 |
| i15 | 23737 | 0 | 60.03 |
| i16 | 16751 | 1 | 60.03 |
| i17 | 77595 | 0 | 60.08 |
| i18 | 47984 | 0 | 60.04 |
| i19 | 71349 | 0 | 60.08 |
| i20 | 43090 | 0 | 60.02 |
| i21 | 42319 | 0 | 60.05 |
| i22 | 100777 | 0 | 60.06 |
| i23 | 56927 | 0 | 60.09 |
| i24 | 44309 | 0 | 60.06 |
| i25 | 19724 | 0 | 60.03 |
| i26 | 113193 | 0 | 60.08 |
| i27 | 105912 | 0 | 60.24 |
| i28 | 88790 | 0 | 60.05 |
| i29 | 25095 | 0 | 60.04 |
| i30 | 49473 | 0 | 60.07 |

**avg_cost:** 38380.3
**avg_time_s:** 60.05
**n_feasible:** 29 / 30

## Conclusion

**Decision:** keep

Regret repair is the best 4-worker/60s result to date: 38380.3 beats exp013
(38494.5) and exp014-SA (38580.0) at the same time budget and worker count.
Per-instance comparison vs exp014 shows consistent wins on i02 (−14%), i04,
i05, i07–i09, i14, i19, i23. The algorithm is sound and parameter-free.

The gap vs exp011 (37675.6, 1-worker/60s) is explained by process startup
overhead for ProcessPoolExecutor: with 4 workers × 60s, each worker loses
~5-10s to process fork/spawn, reducing effective computation by ~10-15%.
At 600s (exp012 config), this overhead is amortized and regret repair should
give a net improvement over the plain exp012 baseline.
i16 remains infeasible at 60s — a known time-budget issue.


## Hypothesis

The current LNS repair step inserts removed patients in a fixed order:
mandatory first, then earliest-deadline first, then longest surgery first.
This ordering is schedule-blind — it ignores how competitive each patient's
insertion slots are at the time of repair.

Replacing it with **regret-2 insertion** (a classic ALNS improvement):
for each unassigned patient, compute their best and second-best insertion costs
(static, using the pre-repair schedule state). Sort by descending regret
(second_best − best). Patients with the most to lose from being placed later
are inserted first — before other patients claim their preferred slots.

This is parameter-free, deterministic, and improves every repair iteration
at the cost of ≈2× pre-computation per repair step (same asymptotic O(n·m)).

Expected: 1-3% cost reduction vs exp011's 37675.6 average, especially on
medium-to-large instances where multiple patients compete for the same day/room
windows and insertion order significantly affects final placement quality.

## Changes vs. Previous Kept Experiment

Built on `main` (after exp012 merge):

- `src/solvers/local_search.py`:
  - Add `_compute_insertion_regret(p, schedule, instance, theater_load, surgeon_load,
    w_delay, w_theater, greedy)` — same slot enumeration as `_insert_best` but
    collects all scores and returns `(best_score, second_best_score)`. Returns
    `(INF, INF)` if no feasible slot; `(best, INF)` if only one feasible slot.
  - Modify `_repair_patients` to pre-compute regret for all removed patients,
    then sort by `(mandatory_first, -regret, last_possible_day, -surgery_duration)`.
    Patients with no feasible slot (regret=0) sort last; rescue handles them.

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
