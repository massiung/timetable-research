# exp032: lahc

**Branch:** exp/lahc
**Date:** 2026-04-30
**Solver:** local_search
**Status:** discard

## Hypothesis

exp031 showed SA acceptance (T_start=2%) is worse than greedy for large instances — the
fixed temperature ratio is too aggressive. LAHC (Late Acceptance Hill Climbing) avoids
temperature calibration entirely: at each iteration, accept a new solution if its objective
is no worse than the objective from L iterations ago. This naturally scales to the problem
instance — as the search converges, the history fills with low values and acceptance
becomes more selective.

**Hypothesis**: LAHC with L=500 provides useful diversification on small/medium instances
(where SA helped) without destabilizing large instances (where SA hurt). The self-calibrating
nature of LAHC should give a better balance than the fixed 2% SA ratio.

Combined with 4 workers, expected: avg_cost ≤ 37761.8 (exp029, greedy acceptance).

**Changes** from exp029 (kept baseline):
- `src/solvers/local_search.py`:
  - Add `lahc_history_len: int = 500` to LNSConfig
  - In `_lns_worker`: initialize circular history `[best_obj] * L`; acceptance criterion
    changes to `obj ≤ history[pos % L]`; history is updated every iteration with the
    evaluated objective (regardless of acceptance). Revert to best on rejection.
  - Perturbation still restarts from `best` (as in exp031).
- `tests/test_local_search.py`: update `test_defaults` for new LAHC parameter.

## Changes vs. Previous Kept Experiment

- `src/solvers/local_search.py`:
  - Add Late Acceptance Hill Climbing acceptance criterion with history length L=500.

## Results

| Instance | Cost | Violations | Time (s) |
|----------|------|------------|----------|
| i01 | 5543 | 0 | 60.01 |
| i02 | 2527 | 0 | 60.02 |
| i03 | 12165 | 0 | 60.01 |
| i04 | 4504 | 0 | 60.02 |
| i05 | 14485 | 0 | 60.02 |
| i06 | 11810 | 0 | 60.02 |
| i07 | 7913 | 0 | 60.02 |
| i08 | 9291 | 0 | 60.03 |
| i09 | 12799 | 0 | 60.02 |
| i10 | 32430 | 0 | 60.02 |
| i11 | 32420 | 0 | 60.02 |
| i12 | 16904 | 0 | 60.02 |
| i13 | 27096 | 0 | 60.02 |
| i14 | 16742 | 0 | 60.02 |
| i15 | 23407 | 0 | 60.02 |
| i16 | 15080 | 4 | 60.02 |
| i17 | 74115 | 0 | 60.04 |
| i18 | 47758 | 0 | 60.04 |
| i19 | 71308 | 0 | 60.05 |
| i20 | 42401 | 0 | 60.02 |
| i21 | 41595 | 0 | 60.03 |
| i22 | 98817 | 0 | 60.05 |
| i23 | 58125 | 0 | 60.05 |
| i24 | 44212 | 0 | 60.05 |
| i25 | 19292 | 0 | 60.03 |
| i26 | 111883 | 0 | 60.05 |
| i27 | 103458 | 0 | 60.05 |
| i28 | 88699 | 0 | 60.04 |
| i29 | 24804 | 0 | 60.04 |
| i30 | 49216 | 0 | 60.04 |

**avg_cost:** 38128.2
**avg_time_s:** 60.03
**n_feasible:** 29 / 30

## Conclusion

**Decision:** discard

LAHC (L=500) gives 38128.2 — dramatically worse than greedy acceptance (exp029: 37761.8)
by 366 points. Large instances devastated: i26 +2912, i27 +2182, i19 +1832. The L=500
history initializes at best_obj, causing the solver to accept solutions worse than
best_obj throughout the early search as the history fills. This causes large drift,
especially on large instances with many alternative (worse) placements.

Key learning (combined with exp031): both SA and LAHC make performance worse. Greedy
acceptance ("accept only strict improvements, always revert to best") is optimal for
this problem. The tight constraint structure means uphill moves consistently lead to
worse-than-recoverable territory. Stop exploring alternative acceptance criteria.
