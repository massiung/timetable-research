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
| i01 | 5746 | 0 | 60.02 |
| i02 | 2630 | 0 | 60.02 |
| i03 | 12230 | 0 | 60.02 |
| i04 | 4430 | 0 | 60.03 |
| i05 | 14668 | 0 | 60.03 |
| i06 | 11827 | 0 | 60.03 |
| i07 | 8435 | 0 | 60.03 |
| i08 | 9696 | 0 | 60.04 |
| i09 | 13045 | 0 | 60.03 |
| i10 | 32405 | 0 | 60.04 |
| i11 | 32812 | 0 | 60.04 |
| i12 | 16903 | 0 | 60.03 |
| i13 | 27306 | 0 | 60.03 |
| i14 | 16740 | 0 | 60.03 |
| i15 | 23452 | 0 | 60.03 |
| i16 | 14040 | 7 | 60.04 |
| i17 | 73880 | 0 | 60.06 |
| i18 | 47898 | 0 | 60.04 |
| i19 | 68512 | 0 | 60.06 |
| i20 | 43381 | 0 | 60.04 |
| i21 | 41414 | 0 | 60.05 |
| i22 | 98736 | 0 | 60.06 |
| i23 | 56559 | 0 | 60.07 |
| i24 | 44135 | 0 | 60.07 |
| i25 | 19297 | 0 | 60.06 |
| i26 | 111905 | 0 | 60.08 |
| i27 | 103939 | 0 | 60.07 |
| i28 | 88576 | 0 | 60.07 |
| i29 | 24757 | 0 | 60.06 |
| i30 | 48977 | 0 | 60.06 |

**avg_cost:** 38079.0
**avg_time_s:** 60.04
**n_feasible:** 29 / 30

## Conclusion

**Decision:** discard

Window-size sort key `(last_possible_day - surgery_release_day)` as primary order gives avg_cost=38079.0 — 317.2 points worse than exp029 (37761.8). 23 of 29 feasible instances regressed; only i04 (−14), i19 (−964), i23 (−995), i25 (−64), i28 (−45), i30 (−448) improved. i16 violations worsened from 5 (exp029) to 7.

This replicates exp020's finding: window-sort disrupts the temporal spreading property of EDF ordering. The absolute deadline `last_possible_day` is the correct primary key — it places the most time-critical patients first, ensuring they get valid slots before broadly-windowed patients consume resources. Window size is a weaker proxy that breaks the urgency invariant.

**Stop trying repair ordering changes. EDF (last_possible_day) is definitively better.**
