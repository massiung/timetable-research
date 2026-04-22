# exp010: feasible-perturb

**Branch:** exp/feasible-perturb
**Date:** 2026-04-22
**Solver:** local_search
**Status:** pending decision

## Hypothesis

exp009 showed that perturbation restart improved some feasible instances but made i16 infeasible
by disrupting the rescue_fail_streak mechanism. The fix: gate perturbation on `not best_infeasible`.

For i16 (structural infeasibility):
1. rescue_fail_streak accumulates normally (no perturbation fires since best_infeasible=True)
2. Blocking destroy activates at streak=50
3. i16 eventually achieves feasibility (as in exp007)
4. Now best_infeasible=False → perturbation can fire to improve i16's cost further

For already-feasible instances:
- best_infeasible=False from the start → perturbation fires after 500 consecutive non-improving iterations
- Helps escape deep local optima that exp007 got stuck in (i17, i25, etc.)

Expected: maintain 30/30 feasibility (i16 still solved via blocking destroy) while improving avg_cost
for instances that stagnate.

## Changes vs. Previous Kept Experiment

Built on `exp/feasible-perturb` (branched from main after exp007 merge):

- `src/solvers/local_search.py`:
  - Add `no_improve_limit: int = 500` and `perturb_ratio: float = 0.50` to `LNSConfig`.
  - Track `iters_since_improvement` counter (reset on new best or perturbation).
  - Perturbation fires only when `not best_infeasible AND iters_since_improvement >= no_improve_limit`.
  - Perturbation: destroy `perturb_ratio` fraction of patients randomly, repair, clear/reassign nurses.
  - Does NOT call rescue during perturbation (best is already feasible at that point).
- `tests/test_local_search.py`: add `no_improve_limit`/`perturb_ratio` assertions, one integration test.

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

**Decision:** pending

## What to try next

TBD after results.
