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
