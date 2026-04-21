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
