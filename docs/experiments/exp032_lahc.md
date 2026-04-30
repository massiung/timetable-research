# exp032: lahc

**Branch:** exp/lahc
**Date:** 2026-04-30
**Solver:** local_search
**Status:** pending

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

<!-- What did we learn? -->
