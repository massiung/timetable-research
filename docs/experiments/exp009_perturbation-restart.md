# exp009: perturbation-restart

**Branch:** exp/perturbation-restart
**Date:** 2026-04-22
**Solver:** local_search
**Status:** pending decision

## Hypothesis

exp007 achieved 30/30 feasible and -1.9% avg_cost. Most instances converge to the same cost in every
experiment, suggesting the solver gets trapped in deep local optima early and never escapes.

exp008 (adaptive destroy) failed because it disrupted the rescue-gate mechanism. A safer diversification
strategy is periodic perturbation: after `no_improve_limit=500` consecutive iterations with no new best,
destroy 50% of patients at random and re-repair. This is:
- Orthogonal to rescue-gate (the streak counter isn't touched during perturbation)
- Triggered by stagnation, not time position — only fires when truly stuck
- Large enough (50%) to escape deep local optima; normal search continues immediately after

Expected to improve avg_cost for instances where the solver stagnates (i26, i27) without regressing
easy instances or breaking i16 feasibility.

## Changes vs. Previous Kept Experiment

Built on `exp/perturbation-restart` (branched from main after exp007 merge):

- `src/solvers/local_search.py`:
  - Add `no_improve_limit: int = 500` and `perturb_ratio: float = 0.50` to `LNSConfig`.
  - Track `iters_since_improvement` counter (reset to 0 on new best or perturbation).
  - At top of main loop: if `iters_since_improvement >= no_improve_limit`, do a large random
    destroy (perturb_ratio), repair, optional rescue, nurse reassignment; reset counter.
  - `iters_since_improvement` increments on non-improving iterations only.
- `tests/test_local_search.py`: add `no_improve_limit`/`perturb_ratio` assertions and one
  integration test that verifies perturbation doesn't crash with `no_improve_limit=1`.

## Results

| Instance | Cost | Violations | Time (s) |
|----------|------|------------|----------|
| i01 | 5532 | 0 | 60.00 |
| i02 | 2458 | 0 | 60.00 |
| i03 | 12120 | 0 | 60.00 |
| i04 | 4401 | 0 | 60.00 |
| i05 | 14562 | 0 | 60.00 |
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
| i16 | — | 1 | 60.00 |
| i17 | 75630 | 0 | 60.01 |
| i18 | 48148 | 0 | 60.00 |
| i19 | 71792 | 0 | 60.00 |
| i20 | 42189 | 0 | 60.00 |
| i21 | 42079 | 0 | 60.00 |
| i22 | 100310 | 0 | 60.01 |
| i23 | 58302 | 0 | 60.01 |
| i24 | 44255 | 0 | 60.00 |
| i25 | 19626 | 0 | 60.00 |
| i26 | 112298 | 0 | 60.00 |
| i27 | 106812 | 0 | 60.01 |
| i28 | 88633 | 0 | 60.00 |
| i29 | 25013 | 0 | 60.01 |
| i30 | 49556 | 0 | 60.00 |

**avg_cost:** 38416.0
**avg_time_s:** 60.00
**n_feasible:** 29 / 30

## Conclusion

**Decision:** discard

- avg_cost 38416.0 vs exp007's 37692.3 — **+1.9% regression**.
- i16 back to infeasible (1 violation). Perturbation restart fires during the infeasible phase and disrupts the rescue_fail_streak→blocking_destroy pipeline that exp007 relied on.
- Root cause: perturbation's 50% random destroy includes mandatory patients; `_rescue_mandatory` is called, which may reset the streak or fail in ways that break streak monotonicity. The large collateral damage of 50% destroy prevents the targeted blocking destroy from working effectively for i16.
- Some feasible instances improved (i02 -1.5%, i05 -0.6%, i17 -1%, i25 -0.9%) but these gains are outweighed by i16 infeasibility.

## What to try next (exp010)

**Gate perturbation on best feasibility**: only fire perturbation when `best_infeasible=False`. This preserves the rescue_fail_streak mechanism for infeasible instances (i16 can still accumulate streak to 50 and activate blocking destroy), while allowing perturbation to escape local optima AFTER feasibility is achieved. For i16, the sequence would be:
1. rescue_fail_streak accumulates → blocking destroy activates → i16 mandatory gets placed → best_infeasible=False
2. Perturbation can now fire to improve i16's cost after feasibility

Change: `if iters_since_improvement >= cfg.no_improve_limit and not best_infeasible:`
