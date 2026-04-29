# exp024: smaller-destroy

**Branch:** exp/smaller-destroy
**Date:** 2026-04-29
**Solver:** local_search
**Status:** keep

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
| i01 | 5589 | 0 | 60.00 |
| i02 | 2636 | 0 | 60.00 |
| i03 | 12090 | 0 | 60.00 |
| i04 | 4430 | 0 | 60.01 |
| i05 | 14630 | 0 | 60.00 |
| i06 | 11775 | 0 | 60.00 |
| i07 | 7827 | 0 | 60.00 |
| i08 | 9116 | 0 | 60.01 |
| i09 | 12895 | 0 | 60.00 |
| i10 | 32990 | 0 | 60.00 |
| i11 | 32115 | 0 | 60.00 |
| i12 | 16722 | 0 | 60.00 |
| i13 | 27010 | 0 | 60.00 |
| i14 | 16450 | 0 | 60.01 |
| i15 | 22412 | 0 | 60.00 |
| i16 | 15947 | 3 | 60.01 |
| i17 | 75050 | 0 | 60.01 |
| i18 | 47652 | 0 | 60.00 |
| i19 | 72039 | 0 | 60.02 |
| i20 | 42814 | 0 | 60.01 |
| i21 | 41390 | 0 | 60.00 |
| i22 | 99237 | 0 | 60.01 |
| i23 | 57600 | 0 | 60.01 |
| i24 | 44200 | 0 | 60.01 |
| i25 | 19594 | 0 | 60.02 |
| i26 | 111977 | 0 | 60.01 |
| i27 | 105517 | 0 | 60.01 |
| i28 | 88834 | 0 | 60.00 |
| i29 | 24842 | 0 | 60.00 |
| i30 | 49407 | 0 | 60.01 |

**avg_cost:** 38235.9
**avg_time_s:** 60.01
**n_feasible:** 29 / 30

## Conclusion

**Decision:** keep

Smaller destroy window (5–20%) gives 38235.9 — best since exp011 (37675.6), beating all
experiments in the 38400–38900 range. More iterations with finer moves outperform larger moves
even though each move is weaker. i16 still infeasible. The downward trend with smaller moves
suggests going even smaller (3–12%) may give further gains.

Key learning: smaller destroy moves → more iterations → better local search quality.
The 10–30% range in exp011 is too large; 5–20% is better. Direction confirmed.
