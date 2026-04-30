# exp031: sa-accept

**Branch:** exp/sa-accept
**Date:** 2026-04-30
**Solver:** local_search
**Status:** discard

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
| i01 | 5528 | 0 | 60.01 |
| i02 | 2370 | 0 | 60.02 |
| i03 | 12165 | 0 | 60.02 |
| i04 | 4501 | 0 | 60.02 |
| i05 | 14467 | 0 | 60.02 |
| i06 | 11793 | 0 | 60.02 |
| i07 | 7985 | 0 | 60.02 |
| i08 | 9306 | 0 | 60.03 |
| i09 | 12706 | 0 | 60.02 |
| i10 | 31990 | 0 | 60.02 |
| i11 | 32441 | 0 | 60.02 |
| i12 | 16819 | 0 | 60.02 |
| i13 | 27284 | 0 | 60.02 |
| i14 | 16499 | 0 | 60.03 |
| i15 | 22981 | 0 | 60.02 |
| i16 | 14677 | 3 | 60.02 |
| i17 | 72870 | 0 | 60.04 |
| i18 | 47769 | 0 | 60.03 |
| i19 | 69641 | 0 | 60.05 |
| i20 | 42912 | 0 | 60.03 |
| i21 | 40992 | 0 | 60.04 |
| i22 | 97232 | 0 | 60.05 |
| i23 | 57864 | 0 | 60.06 |
| i24 | 44095 | 0 | 60.05 |
| i25 | 19355 | 0 | 60.03 |
| i26 | 109697 | 0 | 60.06 |
| i27 | 102382 | 0 | 60.05 |
| i28 | 88554 | 0 | 60.04 |
| i29 | 24719 | 0 | 60.04 |
| i30 | 49064 | 0 | 60.04 |

**avg_cost:** 37792.4
**avg_time_s:** 60.03
**n_feasible:** 29 / 30

## Conclusion

**Decision:** discard

SA with 2% temperature gives 37792.4 — worse than exp029 (37761.8, greedy acceptance) by 30
points. SA helps on 16 of 29 instances (especially small/medium) but badly hurts large
instances: i21 (+610), i26 (+726), i27 (+1106). For large instances, T_start = 2% of
initial cost (~2000 points) is far too permissive, allowing the solver to drift away from
good basins. With 4 workers already providing seed diversity, SA adds noise rather than useful
exploration. Greedy acceptance remains best at this temperature calibration.
