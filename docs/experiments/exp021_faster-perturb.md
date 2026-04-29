# exp021: faster-perturb

**Branch:** exp/faster-perturb
**Date:** 2026-04-29
**Solver:** local_search
**Status:** pending

## Hypothesis

All algorithmic changes (ALNS, regret repair, sort variants, targeted perturbation) have
regressed vs exp011 (37675.6). The only winning change so far was the perturbation frequency:
exp010 (N=500) → exp011 (N=100) gave a small improvement. The trend suggests more frequent
perturbations help at 60s budgets.

**Hypothesis**: halving no_improve_limit from 100 to 50 (more frequent restarts) and reducing
perturb_ratio from 0.50 to 0.40 (smaller restarts that recover faster) will give ~2× more
perturbation events per run while each perturbation disturbs fewer patients. This allows the
solver to escape more local optima per run at the cost of each escape being less dramatic.

**Changes**: no_improve_limit=50 (from 100), perturb_ratio=0.40 (from 0.50). All other code
identical to exp011: deadline-first repair sort, uniform random operator selection, num_workers=1.

## Changes vs. Previous Kept Experiment

Built on `main` (after exp016 merge), reverting to exp011 baseline:

- `src/solvers/local_search.py`:
  - Remove `_INF_COST` and `_compute_insertion_regret`; restore deadline-first repair sort.
  - Remove all ALNS code (config fields + runtime weight tracking).
  - Change `no_improve_limit: int = 100` → `no_improve_limit: int = 50`.
  - Change `perturb_ratio: float = 0.50` → `perturb_ratio: float = 0.40`.
  - Change `num_workers: int = 4` → `num_workers: int = 1`.

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

<!-- What did we learn? -->
