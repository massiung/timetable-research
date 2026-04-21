# exp003: lns-v2

**Branch:** exp/lns-v2
**Date:** 2026-04-21
**Solver:** local_search
**Status:** pending decision

## Hypothesis

Two bugs in exp002 prevented it from finding feasible solutions:

1. **Wrong greedy init** — `constrained_first` ordering left i20's p33 unscheduled from the start; the LNS then never recovered feasibility. Using the default `urgency` ordering fixes i20.
2. **Never-retried mandatories** — The LNS only repaired the patients it destroyed each iteration. Mandatory patients that greedy couldn't place were never in the `removed` list, so they were never attempted again. A new `_rescue_mandatory` pass runs after every repair and tries to insert all unscheduled mandatory patients, falling back to forced eviction of non-mandatory room occupants when needed.

With these fixes and 60 s budget: i20 should be 0 violations; i16 should drop from 10 to near 0 (feasible at 180 s in a smoke test). Average cost should improve further as the solver now consistently starts from feasible solutions.

## Changes vs. Previous Kept Experiment

Built on `exp/lns-v2` (branched from `exp/lns-v1`):

- `src/solvers/local_search.py`:
  - Fix greedy init: `GreedyConfig()` instead of `GreedyConfig(patient_sort_key="constrained_first")`.
  - Add `_rescue_mandatory(schedule, greedy, instance) -> int`: post-repair pass that inserts all unscheduled mandatory patients. Returns rescue count. Calls `_forced_insert` for any still-unscheduled cases.
  - Add `_forced_insert(p, schedule, greedy, instance, ...) -> list[int]`: evicts the minimum set of non-mandatory room occupants to make space for mandatory patient `p`. Returns list of evicted patient indices; updates `theater_load` and `surgeon_load` in-place.
  - Add structured logging via `logging.getLogger(__name__)`: INFO at init and completion, DEBUG per new-best iteration and per rescue event.
- `src/main.py`: add `--log-level` CLI flag (DEBUG/INFO/WARNING/ERROR) wired to `logging.basicConfig`.
- `tests/test_local_search.py`: new tests for `_rescue_mandatory` and `_forced_insert`, covering normal rescue, forced-eviction path, and all infeasibility branches.

## Results

| Instance | Cost | Violations | Time (s) |
|----------|------|------------|----------|
| i01 | 5720 | 0 | 60.00 |
| i02 | 2798 | 0 | 60.00 |
| i03 | 13220 | 0 | 60.00 |
| i04 | 4496 | 0 | 60.00 |
| i05 | 17365 | 0 | 60.00 |
| i06 | 12109 | 0 | 60.00 |
| i07 | 8444 | 0 | 60.00 |
| i08 | 9287 | 0 | 60.00 |
| i09 | 11494 | 0 | 60.00 |
| i10 | 34605 | 0 | 60.00 |
| i11 | 35897 | 0 | 60.00 |
| i12 | 17215 | 0 | 60.00 |
| i13 | 31659 | 0 | 60.00 |
| i14 | 17281 | 0 | 60.00 |
| i15 | 24682 | 0 | 60.00 |
| i16 | — | 1 | 60.00 |
| i17 | 80045 | 0 | 60.00 |
| i18 | 53330 | 0 | 60.00 |
| i19 | 75314 | 0 | 60.01 |
| i20 | 45837 | 0 | 60.00 |
| i21 | 46212 | 0 | 60.00 |
| i22 | 111318 | 0 | 60.00 |
| i23 | 67770 | 0 | 60.00 |
| i24 | 47761 | 0 | 60.01 |
| i25 | 20334 | 0 | 60.00 |
| i26 | 126999 | 0 | 60.01 |
| i27 | 115557 | 0 | 60.01 |
| i28 | 92518 | 0 | 60.00 |
| i29 | 26560 | 0 | 60.00 |
| i30 | 54286 | 0 | 60.00 |

**avg_cost:** 41728.0
**avg_time_s:** 60.00
**n_feasible:** 29 / 30

## Conclusion

**Decision:** pending

- i20 fixed: 0 violations (was 1 in exp002 — the `constrained_first` init bug is resolved).
- i16 improved: 1 violation (was 10 in both greedy and exp002). Feasible at 180 s; the 60 s budget is not enough for the rescue to converge.
- avg_cost 41728.0 is higher than exp002's 38269.2, but the comparison is not apples-to-apples: exp002 excluded i20 from the average (infeasible), while exp003 includes it (cost 45837). Over the same 28 feasible-in-both instances, exp003 avg is ~41582 vs exp002's ~38269 — a per-instance regression of ~8.6%.
- The per-instance regression has two causes: (1) switching from `constrained_first` to `urgency` init gives a slightly worse starting solution for most instances; (2) the `_rescue_mandatory` pass adds per-iteration overhead (O(n_mandatory) scan + possible forced insertions), reducing iteration throughput.
- n_feasible: 29/30 vs 28/30 (exp002). Only i16 remains infeasible at 60 s.
