# exp017: validate-1worker

**Branch:** exp/validate-1worker
**Date:** 2026-04-28
**Solver:** local_search
**Status:** pending

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
