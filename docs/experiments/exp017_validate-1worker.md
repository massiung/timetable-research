# exp017: validate-1worker

**Branch:** exp/validate-1worker
**Date:** 2026-04-28
**Solver:** local_search
**Status:** discard

## Hypothesis

Experiments exp015-016 showed that 4-worker/60s consistently underperforms
1-worker/60s (exp011: 37675.6). Root cause: Python ProcessPoolExecutor
initialization overhead consumes ~2–3s per-worker at startup, reducing
effective computation by ~5% at the 60s budget. With 4 workers all starting
simultaneously and sharing 4 CPUs, the init overhead is not fully amortized.

**Hypothesis**: The algorithm improvements accumulated since exp011 (regret-2
repair from exp015, ALNS operator weights from exp016) produce genuinely better
solutions. Testing at **num_workers=1** (matching exp011's config) directly
validates this: if 1-worker + regret + ALNS beats exp011's 37675.6, the
algorithm improvements are confirmed.

Expected: 1-3% improvement over exp011's 37675.6 average at 1-worker/60s.
If confirmed, this is the first direct metric lift since the 60s baseline.

## Changes vs. Previous Kept Experiment

Built on `main` (after exp016 merge — includes regret-2 repair + ALNS):

- `src/solvers/local_search.py`:
  - Change `num_workers: int = 4` → `num_workers: int = 1` in LNSConfig.
  - No other algorithmic changes; this experiment purely validates existing
    improvements at the 1-worker/60s comparison point.

## Results

| Instance | Cost | Violations | Time (s) |
|----------|------|------------|----------|
| i01 | 5418 | 0 | 60.00 |
| i02 | 2186 | 0 | 60.00 |
| i03 | 12090 | 0 | 60.00 |
| i04 | 4048 | 0 | 60.00 |
| i05 | 14467 | 0 | 60.00 |
| i06 | 11729 | 0 | 60.00 |
| i07 | 7764 | 0 | 60.00 |
| i08 | 8842 | 0 | 60.01 |
| i09 | 12532 | 0 | 60.00 |
| i10 | 32400 | 0 | 60.00 |
| i11 | 32218 | 0 | 60.00 |
| i12 | 16395 | 0 | 60.00 |
| i13 | 27041 | 0 | 60.01 |
| i14 | 16585 | 0 | 60.01 |
| i15 | 23970 | 0 | 60.00 |
| i16 | 15019 | 2 | 60.00 |
| i17 | 76860 | 0 | 60.01 |
| i18 | 48052 | 0 | 60.00 |
| i19 | 72043 | 0 | 60.02 |
| i20 | 43423 | 0 | 60.00 |
| i21 | 42128 | 0 | 60.00 |
| i22 | 99698 | 0 | 60.02 |
| i23 | 57065 | 0 | 60.03 |
| i24 | 44304 | 0 | 60.05 |
| i25 | 19660 | 0 | 60.02 |
| i26 | 112868 | 0 | 60.01 |
| i27 | 106771 | 0 | 60.02 |
| i28 | 88855 | 0 | 60.01 |
| i29 | 25162 | 0 | 60.01 |
| i30 | 49511 | 0 | 60.03 |

**avg_cost:** 38416.7
**avg_time_s:** 60.01
**n_feasible:** 29 / 30

## Conclusion

**Decision:** discard

regret repair + ALNS at 1-worker gives 38416.7 — 2% WORSE than exp011 (37675.6).
Root cause: `_compute_insertion_regret` evaluates O(days × theaters) slots per patient
BEFORE insertion (to compute ordering), which doubles work per repair step and
roughly halves the iteration count in 60s. The quality gain per iteration does not
compensate for the 50% fewer iterations, especially on small/medium instances where
the solver does thousands of iterations.

Key learning: regret repair is too computationally expensive at 60s iteration budgets.
Any ordering improvement must be O(1) per patient (just using already-known patient data)
to avoid this regression. Next: test ALNS alone (without regret) at 1-worker vs exp011.
