# exp024: smaller-destroy

**Branch:** exp/smaller-destroy
**Date:** 2026-04-29
**Solver:** local_search
**Status:** pending

## Hypothesis

exp023 showed that larger destroy moves (15–35%) hurt by reducing iteration count. The natural
complement is smaller destroy moves (5–20%): each iteration disturbs fewer patients, the solver
can run more iterations within the 60s budget, and the search focuses on finer local structure.

**Hypothesis**: smaller destroy (5–20% vs 10–30% in exp011) gives more iterations, allowing
the solver to converge more precisely. The downside is weaker escape from local optima, but if
the search space is locally smooth, finer steps may help.

**Changes**: single parameter change — shift destroy ratio window from [0.10, 0.30] to [0.05, 0.20].
All other code identical to exp011: deadline-first repair sort, 3 operators (random/related/high_delay),
N=100, ratio=0.50 perturbation, num_workers=1.

## Changes vs. Previous Kept Experiment

Built on exp/two-phase (itself built on main with ALNS stripped), then updated:

- `src/solvers/local_search.py`:
  - Change `min_destroy_ratio: float = 0.15` → `0.05`.
  - Change `max_destroy_ratio: float = 0.35` → `0.20`.

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
