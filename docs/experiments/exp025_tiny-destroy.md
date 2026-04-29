# exp025: tiny-destroy

**Branch:** exp/tiny-destroy
**Date:** 2026-04-29
**Solver:** local_search
**Status:** pending

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

**Decision:** keep / discard

<!-- What did we learn? See docs/learnings.md for any reusable insight. -->
