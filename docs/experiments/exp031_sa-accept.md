# exp031: sa-accept

**Branch:** exp/sa-accept
**Date:** 2026-04-30
**Solver:** local_search
**Status:** pending

## Hypothesis

exp029 (4 workers, [0.01, 0.06], N=100, greedy acceptance) gives 37761.8 — 86 points (0.23%)
above exp011 (37675.6). Greedy acceptance (revert on any non-improvement) traps the solver
in local optima: once no improving neighbor exists, the only escape is the periodic big
perturbation (50% destroy, every N=100 iters). Between perturbations, the solver makes zero
lateral moves.

**Hypothesis**: simulated annealing (SA) acceptance allows lateral and slightly uphill moves,
enabling the solver to cross ridges between basins without waiting for the perturbation.
Temperature decays geometrically from `T_start = 2% of initial cost` to `T_end = 0.1`
over the 60s budget. At start, a move 2% worse is accepted with probability ~37%; at end,
the solver is effectively greedy. The perturbation is still kept as a safety net but now
restarts from `best` (not from wherever SA has wandered).

Expected: 0.5–2% improvement over exp029, potentially beating exp011 (37675.6).

**Changes** from exp029 (kept baseline):
- `src/solvers/local_search.py`:
  - Add `import math`
  - Add `sa_start_temp_ratio: float = 0.02` and `sa_end_temp: float = 0.1` to `LNSConfig`
  - In `_lns_worker`: compute `init_temp = best_obj * sa_start_temp_ratio` after init
  - Perturbation block: `_copy_into(current, best)` before perturbing (restart from best)
  - Acceptance block: accept worse solution with probability `exp(-delta/temp)` where
    `temp` decays geometrically from `init_temp` to `sa_end_temp`
- `tests/test_local_search.py`: update `test_defaults` for new SA parameters

## Changes vs. Previous Kept Experiment

- `src/solvers/local_search.py`:
  - Add simulated annealing acceptance criterion with geometric temperature decay.
  - Perturbation always restarts from `best`, not from current SA position.

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
