# exp025: tiny-destroy

**Branch:** exp/tiny-destroy
**Date:** 2026-04-29
**Solver:** local_search
**Status:** keep

## Hypothesis

exp024 showed that reducing destroy ratio from [0.10, 0.30] to [0.05, 0.20] improved avg_cost
from ~38400 to 38235.9 — the best result since exp011 (37675.6). The smaller moves give more
iterations which improves local search quality. The direction is confirmed: smaller = better.

**Hypothesis**: shrinking further to [0.03, 0.12] (even more iterations, even finer moves)
continues the improvement trend. At 60s, each iteration is fast enough that the volume gain
from more iterations outweighs the weaker individual perturbations.

**Changes**: single parameter change — shift destroy ratio window from [0.05, 0.20] to [0.03, 0.12].
All other code identical to exp024 (which itself matches exp011 algorithm).

## Changes vs. Previous Kept Experiment

Built on exp/smaller-destroy (exp024), then updated:

- `src/solvers/local_search.py`:
  - Change `min_destroy_ratio: float = 0.05` → `0.03`.
  - Change `max_destroy_ratio: float = 0.20` → `0.12`.

## Results

| Instance | Cost | Violations | Time (s) |
|----------|------|------------|----------|
| i01 | 5492 | 0 | 60.00 |
| i02 | 2756 | 0 | 60.00 |
| i03 | 12105 | 0 | 60.00 |
| i04 | 4404 | 0 | 60.00 |
| i05 | 14640 | 0 | 60.00 |
| i06 | 11798 | 0 | 60.00 |
| i07 | 7709 | 0 | 60.00 |
| i08 | 9535 | 0 | 60.01 |
| i09 | 12464 | 0 | 60.00 |
| i10 | 32065 | 0 | 60.00 |
| i11 | 32232 | 0 | 60.00 |
| i12 | 16747 | 0 | 60.00 |
| i13 | 27199 | 0 | 60.00 |
| i14 | 16441 | 0 | 60.01 |
| i15 | 23392 | 0 | 60.01 |
| i16 | 15771 | 4 | 60.00 |
| i17 | 74965 | 0 | 60.01 |
| i18 | 47511 | 0 | 60.00 |
| i19 | 70623 | 0 | 60.02 |
| i20 | 43170 | 0 | 60.00 |
| i21 | 41384 | 0 | 60.01 |
| i22 | 98875 | 0 | 60.01 |
| i23 | 58194 | 0 | 60.02 |
| i24 | 44059 | 0 | 60.01 |
| i25 | 19688 | 0 | 60.01 |
| i26 | 109954 | 0 | 60.01 |
| i27 | 103201 | 0 | 60.03 |
| i28 | 88538 | 0 | 60.02 |
| i29 | 24804 | 0 | 60.01 |
| i30 | 49558 | 0 | 60.01 |

**avg_cost:** 38051.8
**avg_time_s:** 60.01
**n_feasible:** 29 / 30

## Conclusion

**Decision:** keep

Tiny destroy (3–12%) gives 38051.8 — best yet, beating exp024 (38235.9) and all others since
exp011 (37675.6). Trend confirmed: smaller k = more iterations = better local search. i16 still
infeasible. Gap to exp011 narrowed to 1.0%. The direction is clearly right; going even smaller
(1–6%) may close the gap further.
