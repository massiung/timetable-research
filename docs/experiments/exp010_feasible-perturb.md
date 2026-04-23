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
| i01 | 5532 | 0 | 60.00 |
| i02 | 2458 | 0 | 60.00 |
| i03 | 12120 | 0 | 60.00 |
| i04 | 4401 | 0 | 60.00 |
| i05 | 14563 | 0 | 60.00 |
| i06 | 11799 | 0 | 60.00 |
| i07 | 7824 | 0 | 60.00 |
| i08 | 9273 | 0 | 60.00 |
| i09 | 12694 | 0 | 60.00 |
| i10 | 33205 | 0 | 60.00 |
| i11 | 32131 | 0 | 60.00 |
| i12 | 16343 | 0 | 60.00 |
| i13 | 27122 | 0 | 60.00 |
| i14 | 16447 | 0 | 60.00 |
| i15 | 23510 | 0 | 60.00 |
| i16 | 17318 | 0 | 60.00 |
| i17 | 75630 | 0 | 60.00 |
| i18 | 48148 | 0 | 60.00 |
| i19 | 71792 | 0 | 60.01 |
| i20 | 42189 | 0 | 60.00 |
| i21 | 42092 | 0 | 60.01 |
| i22 | 100310 | 0 | 60.00 |
| i23 | 58302 | 0 | 60.00 |
| i24 | 44255 | 0 | 60.00 |
| i25 | 19626 | 0 | 60.01 |
| i26 | 112298 | 0 | 60.00 |
| i27 | 106812 | 0 | 60.00 |
| i28 | 88633 | 0 | 60.00 |
| i29 | 25013 | 0 | 60.00 |
| i30 | 49556 | 0 | 60.00 |

**avg_cost:** 37713.2
**avg_time_s:** 60.00
**n_feasible:** 30 / 30

## Conclusion

**Decision:** discard

- avg_cost 37713.2 vs exp007's 37692.3 — **+0.056% regression** (essentially noise).
- **30/30 feasible maintained** — i16 stays at 17318 (feasibility gate worked correctly).
- Some instances improved (i17: -1.0%, i25: -0.9%, i02: -1.5%) and some regressed (i08: +2.1%, i10: +1.6%).
- Root cause of small effect: N=500 is too large for a 60s budget. With ~3000-6000 iterations per run, perturbation fires at most 6-12 times. The improvement signal is too diluted by noise from the random restart landing anywhere.

## What to try next (exp011)

**Lower no_improve_limit to N=100**: this fires perturbation ~20-40 times per run. With a 60s budget and ~5000 iterations, N=100 means perturbation fires whenever the solver stagnates for 2% of the total budget — more aggressive escape from local optima while still being selective enough not to disrupt convergence.
