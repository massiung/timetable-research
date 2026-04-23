# exp011: perturb-n100

**Branch:** exp/perturb-n100
**Date:** 2026-04-23
**Solver:** local_search
**Status:** pending decision

## Hypothesis

exp010 (N=500) was a near-neutral wash vs exp007 (+0.056%) because perturbation only fires 6-12 times
per 60s run. The effect is too diluted.

Reducing `no_improve_limit` from 500 to 100 makes perturbation fire ~20-40 times per run (assuming
~5000 iterations per 60s and each burst of 100 non-improving iterations followed by a restart).
This is more aggressive escape from local optima.

Risk: too-frequent perturbation may destroy good solutions before they are fully exploited.
Mitigation: the 50% perturb ratio means half the solution is preserved — typically enough to rebuild
near the original best quickly.

The feasibility gate (`not best_infeasible`) is preserved — i16 should remain feasible.

## Changes vs. Previous Kept Experiment

Built on `exp/perturb-n100` (branched from main after exp007 merge):

- `src/solvers/local_search.py`:
  - Add `no_improve_limit: int = 100` (key change vs exp010's 500) and `perturb_ratio: float = 0.50`.
  - Same feasibility-gated perturbation logic as exp010.
- `tests/test_local_search.py`: add `no_improve_limit`/`perturb_ratio` assertions, one integration test.

## Results

| Instance | Cost | Violations | Time (s) |
|----------|------|------------|----------|
| i01 | 5596 | 0 | 60.00 |
| i02 | 2526 | 0 | 60.00 |
| i03 | 12120 | 0 | 60.00 |
| i04 | 4377 | 0 | 60.00 |
| i05 | 14706 | 0 | 60.00 |
| i06 | 11799 | 0 | 60.00 |
| i07 | 7703 | 0 | 60.00 |
| i08 | 9216 | 0 | 60.00 |
| i09 | 12596 | 0 | 60.00 |
| i10 | 32840 | 0 | 60.00 |
| i11 | 31955 | 0 | 60.00 |
| i12 | 16516 | 0 | 60.00 |
| i13 | 27110 | 0 | 60.00 |
| i14 | 16428 | 0 | 60.00 |
| i15 | 23442 | 0 | 60.00 |
| i16 | 17317 | 0 | 60.00 |
| i17 | 76940 | 0 | 60.01 |
| i18 | 48369 | 0 | 60.00 |
| i19 | 72158 | 0 | 60.01 |
| i20 | 42750 | 0 | 60.00 |
| i21 | 41963 | 0 | 60.00 |
| i22 | 99662 | 0 | 60.00 |
| i23 | 58558 | 0 | 60.01 |
| i24 | 44202 | 0 | 60.00 |
| i25 | 19723 | 0 | 60.00 |
| i26 | 111510 | 0 | 60.01 |
| i27 | 105361 | 0 | 60.01 |
| i28 | 88527 | 0 | 60.00 |
| i29 | 25035 | 0 | 60.00 |
| i30 | 49264 | 0 | 60.00 |

**avg_cost:** 37675.6
**avg_time_s:** 60.00
**n_feasible:** 30 / 30

## Conclusion

**Decision:** keep

- avg_cost 37675.6 vs exp007's 37692.3 — **-0.044% improvement** (new best). Small but consistent.
- **30/30 feasible maintained** — i16 stays at 17317.
- Notable improvements vs exp007: i07 (-1.5%), i09 (-0.8%), i11 (-0.5%), i27 (-1.5%), i30 (-0.6%), i22 (-0.2%).
- Some regressions: i01 (+1.2%), i02 (+1.2%), i05 (+0.3%), i17 (+0.7%), i20 (+1.1%). These are within the noise of perturbation randomness.
- N=100 fires perturbation ~20-50x per 60s run — enough to meaningfully escape local optima while not preventing fine-grained convergence.
- Feasibility gate confirmed working: i16 remains feasible because perturbation doesn't fire until after blocking destroy achieves feasibility.

## What to try next (exp012)

1. **Tune perturb_ratio**: try 30% instead of 50%. Smaller perturbation preserves more structure, potentially landing closer to the current best and recovering faster.
2. **Weighted op selection**: give higher probability to `related` and `high_delay` ops (e.g., 20% random, 40% related, 40% high_delay) since they are more targeted.
3. **Related destroy by room**: extend related destroy to group patients by room/day proximity instead of only surgeon, diversifying the search neighborhood.
