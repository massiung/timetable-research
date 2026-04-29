# exp021: faster-perturb

**Branch:** exp/faster-perturb
**Date:** 2026-04-29
**Solver:** local_search
**Status:** discard

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
| i01 | 5580 | 0 | 60.00 |
| i02 | 2447 | 0 | 60.00 |
| i03 | 12120 | 0 | 60.00 |
| i04 | 4404 | 0 | 60.00 |
| i05 | 14778 | 0 | 60.00 |
| i06 | 11799 | 0 | 60.00 |
| i07 | 7820 | 0 | 60.01 |
| i08 | 9126 | 0 | 60.02 |
| i09 | 12661 | 0 | 60.00 |
| i10 | 33150 | 0 | 60.00 |
| i11 | 32047 | 0 | 60.00 |
| i12 | 16368 | 0 | 60.00 |
| i13 | 27109 | 0 | 60.00 |
| i14 | 16325 | 0 | 60.01 |
| i15 | 23726 | 0 | 60.01 |
| i16 | 16713 | 2 | 60.01 |
| i17 | 77240 | 0 | 60.02 |
| i18 | 48453 | 0 | 60.00 |
| i19 | 71452 | 0 | 60.03 |
| i20 | 43213 | 0 | 60.01 |
| i21 | 42263 | 0 | 60.01 |
| i22 | 100310 | 0 | 60.01 |
| i23 | 59040 | 0 | 60.03 |
| i24 | 44218 | 0 | 60.04 |
| i25 | 19752 | 0 | 60.01 |
| i26 | 113545 | 0 | 60.02 |
| i27 | 107672 | 0 | 60.02 |
| i28 | 88745 | 0 | 60.02 |
| i29 | 25247 | 0 | 60.00 |
| i30 | 49725 | 0 | 60.01 |

**avg_cost:** 38632.2
**avg_time_s:** 60.01
**n_feasible:** 29 / 30

## Conclusion

**Decision:** discard

Faster perturbation (N=50, ratio=0.40) gives 38632.2 — 2.5% WORSE than exp011 (37675.6).
i16 still infeasible. More frequent but smaller perturbations don't help: each perturbation
fires before the local search has properly converged, wasting restarts on still-active local
optima. The 50% perturbation + N=100 in exp011 balances exploration depth and restart frequency.

Key learning: the N=100 / 50% configuration in exp011 is a sweet spot. Going more frequent (N=50)
or less frequent (N=500, exp010) both hurt. Perturbation parameters are well-tuned.
All structural and parameter changes have failed. Next: try a 4th destroy operator targeting
surgery-load heavy days, a fundamentally different exploration pattern.
