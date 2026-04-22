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
