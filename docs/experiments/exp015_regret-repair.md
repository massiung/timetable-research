# exp015: regret-repair

**Branch:** exp/regret-repair
**Date:** 2026-04-28
**Solver:** local_search
**Status:** pending

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
