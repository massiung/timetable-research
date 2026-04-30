# exp033: adaptive-destroy

**Branch:** exp/adaptive-destroy
**Date:** 2026-04-30
**Solver:** local_search
**Status:** pending decision

## Hypothesis

exp029 (4 workers, greedy acceptance, [0.01, 0.06]) gives 37761.8 — 86 points above exp011
(37675.6). The single infeasible instance is i16, which persistently has unscheduled mandatory
patients (surgeon 2 overloaded). The small destroy ratio [0.01, 0.06] is efficient for
cost-minimization on feasible solutions but insufficient for escaping infeasibility — it
never dislodges enough patients to free capacity for the mandatory patients.

Inline test (seeds 42-49 at 60s with large destroy when infeasible) reduced i16 violations
from 4 to 1-3, showing directional progress. The current static destroy ratio wastes search
time using tiny perturbations that cannot fix infeasibility.

**Hypothesis**: Using a large destroy ratio [0.20, 0.50] when `best_infeasible=True` and
small [0.01, 0.06] when feasible gives the infeasibility-escape power of large destroy while
preserving fast convergence on cost once feasibility is achieved. This adaptive strategy
should make i16 feasible within 60s (or at least reduce violations further) and improve the
overall avg_cost.

Combined with 4 workers, expected: avg_cost < 37761.8 (exp029, greedy acceptance).

**Changes** from exp029 (kept baseline):
- `src/solvers/local_search.py`:
  - Add `infeasible_min_destroy: float = 0.20` and `infeasible_max_destroy: float = 0.50`
    to `LNSConfig`.
  - In `_lns_worker`: use `infeasible_min/max_destroy` for ratio when `best_infeasible=True`,
    `min/max_destroy_ratio` otherwise.
- `tests/test_local_search.py`: update `test_defaults` for new adaptive-destroy parameters.

## Changes vs. Previous Kept Experiment

- `src/solvers/local_search.py`:
  - Add adaptive destroy: large ratio [0.20, 0.50] when infeasible, small [0.01, 0.06] when feasible.

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
