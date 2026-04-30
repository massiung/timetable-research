# exp030: more-workers

**Branch:** exp/more-workers
**Date:** 2026-04-30
**Solver:** local_search
**Status:** pending

## Hypothesis

exp029 (4 workers, [0.01, 0.06], N=100) gives 37761.8 — 0.23% above exp011 (37675.6).
The 4-worker improvement over 1-worker (exp026: 37891.3) was 129 points. Each additional
worker adds another independent seed trajectory. With 8 workers, we double the search
diversity, which may close the remaining 86-point gap.

**Hypothesis**: 8 workers will yield another ~50–80 point improvement, potentially matching
or beating exp011. The cost is 8× the process-spawn overhead, but within a 60s budget this
is negligible (~0.02s startup per worker).

**Changes**: single parameter change from exp029:
- `num_workers: int = 4` → `8`
- Everything else identical: [0.01, 0.06] destroy, N=100, ratio=0.50.

## Changes vs. Previous Kept Experiment

- `src/solvers/local_search.py`:
  - Change `num_workers: int = 4` → `8`.

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

**Decision:** keep / discard

<!-- What did we learn? -->
