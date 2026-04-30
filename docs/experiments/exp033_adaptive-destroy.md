# exp033: adaptive-destroy

**Branch:** exp/adaptive-destroy
**Date:** 2026-04-30
**Solver:** local_search
**Status:** discard

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
| i01 | 5608 | 0 | 60.02 |
| i02 | 2451 | 0 | 60.02 |
| i03 | 12165 | 0 | 60.02 |
| i04 | 4444 | 0 | 60.03 |
| i05 | 14499 | 0 | 60.03 |
| i06 | 11810 | 0 | 60.03 |
| i07 | 8051 | 0 | 60.03 |
| i08 | 9503 | 0 | 60.04 |
| i09 | 12807 | 0 | 60.03 |
| i10 | 32240 | 0 | 60.04 |
| i11 | 32366 | 0 | 60.03 |
| i12 | 16789 | 0 | 60.03 |
| i13 | 27302 | 0 | 60.03 |
| i14 | 16698 | 0 | 60.03 |
| i15 | 23379 | 0 | 60.03 |
| i16 | 16760 | 1 | 60.04 |
| i17 | 73280 | 0 | 60.06 |
| i18 | 47814 | 0 | 60.05 |
| i19 | 69631 | 0 | 60.07 |
| i20 | 44034 | 0 | 60.03 |
| i21 | 40437 | 0 | 60.06 |
| i22 | 97814 | 0 | 60.06 |
| i23 | 57683 | 0 | 60.07 |
| i24 | 44149 | 0 | 60.08 |
| i25 | 19410 | 0 | 60.05 |
| i26 | 109269 | 0 | 60.08 |
| i27 | 101613 | 0 | 60.07 |
| i28 | 88657 | 0 | 60.05 |
| i29 | 24731 | 0 | 60.06 |
| i30 | 49477 | 0 | 60.06 |

**avg_cost:** 37865.9
**avg_time_s:** 60.04
**n_feasible:** 29 / 30

## Conclusion

**Decision:** discard

Adaptive destroy (large [0.20, 0.50] when infeasible, small [0.01, 0.06] when feasible) gives
37865.9 — worse than exp029 (37761.8) by 104 points. i16 improved from 3-4 violations to 1
violation (directional progress), but never reached feasibility within 60s.

The regression is concentrated in small-to-medium instances: i07 (+138), i08 (+212) vs
exp029. For i16, all 4 workers spend the full 60s using large destroy (since greedy init
leaves i16 infeasible). Large destroy means fewer total LNS iterations, so the infeasibility
reduction is real but insufficient — surgeon 2 capacity requires structural relief that
random large destroy cannot reliably provide in 60s.

Key learning: i16's infeasibility is a structural surgeon capacity problem that LNS cannot
fix within the 60s budget regardless of destroy ratio. Adaptive destroy does reduce i16
violations but creates a net regression across other instances. Stop targeting i16 feasibility;
accept it as persistently infeasible under current constraints and focus on cost reduction
across the 29 feasible instances.
