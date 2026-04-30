# exp037: repair-order

**Branch:** exp/repair-order
**Date:** 2026-04-30
**Solver:** local_search
**Status:** pending decision

## Hypothesis

Experiments exp033-036 (targeting i16 feasibility) all failed and were discarded. The
fundamental learning: large destroy hurts instances where some workers start infeasible
(especially i20), and i16 cannot be made feasible within 60s with any destroy configuration.

Pivoting to cost reduction on the 29 feasible instances. The current repair in `_repair_patients`
sorts destroyed patients by `(mandatory, last_possible_day, -surgery_duration)`. This sorts
by absolute last possible day, ignoring how constrained the window actually is.

Consider: Patient A has release_day=0, last_possible_day=14 (window=14, many options).
Patient B has release_day=10, last_possible_day=14 (window=4, very constrained). Current
sort: A and B tie on last_possible_day=14, resolved by surgery_duration. But B is much more
constrained — it needs to be placed on a specific day-range before A takes the best slot.

**Fix**: Use `last_possible_day - surgery_release_day` (window size) as the primary sort
key within each mandatory/optional group. Smaller window → more constrained → placed first.
This ensures constrained patients get first pick of rooms and theaters every repair step,
reducing the frequency of suboptimal placements where a broadly-windowed patient forces a
tightly-windowed patient onto a worse (higher-delay or additional-theater) slot.

**Hypothesis**: Better repair ordering systematically reduces cost across all 29 feasible
instances by putting the most constrained patients first, reducing placement conflicts.
Expected: avg_cost < 37761.8 (exp029).

**Changes** from exp029 (kept baseline):
- `src/solvers/local_search.py`:
  - In `_repair_patients`: change sort key from `last_possible_day` to
    `(last_possible_day - surgery_release_day, last_possible_day)` — window size first,
    absolute deadline as tiebreaker.
- No config changes, no test changes needed.

## Changes vs. Previous Kept Experiment

- `src/solvers/local_search.py`:
  - Repair ordering: sort by window size (last_possible_day - surgery_release_day) to place
    most constrained patients first.

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
