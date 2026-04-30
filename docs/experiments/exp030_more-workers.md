# exp030: more-workers

**Branch:** exp/more-workers
**Date:** 2026-04-30
**Solver:** local_search
**Status:** discard

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
| i01 | 5584 | 0 | 60.03 |
| i02 | 2562 | 0 | 60.03 |
| i03 | 12165 | 0 | 60.04 |
| i04 | 4448 | 0 | 60.04 |
| i05 | 14509 | 0 | 60.04 |
| i06 | 11798 | 0 | 60.03 |
| i07 | 8141 | 0 | 60.04 |
| i08 | 9547 | 0 | 60.06 |
| i09 | 12832 | 0 | 60.04 |
| i10 | 32255 | 0 | 60.05 |
| i11 | 32458 | 0 | 60.04 |
| i12 | 16663 | 0 | 60.04 |
| i13 | 27312 | 0 | 60.05 |
| i14 | 16491 | 0 | 60.05 |
| i15 | 23051 | 0 | 60.05 |
| i16 | 14579 | 5 | 60.05 |
| i17 | 73000 | 0 | 60.08 |
| i18 | 47730 | 0 | 60.07 |
| i19 | 70078 | 0 | 60.09 |
| i20 | 42884 | 0 | 60.05 |
| i21 | 40556 | 0 | 60.06 |
| i22 | 98044 | 0 | 60.08 |
| i23 | 57527 | 0 | 60.10 |
| i24 | 44183 | 0 | 60.12 |
| i25 | 19481 | 0 | 60.06 |
| i26 | 110373 | 0 | 60.10 |
| i27 | 102125 | 0 | 60.10 |
| i28 | 88628 | 0 | 60.08 |
| i29 | 24705 | 0 | 60.06 |
| i30 | 49311 | 0 | 60.08 |

**avg_cost:** 37877.3
**avg_time_s:** 60.06
**n_feasible:** 29 / 30

## Conclusion

**Decision:** discard

8 workers gives 37877.3 — worse than 4 workers (37761.8) by 116 points. CPU contention:
the benchmark machine doesn't have 8 idle cores, so each worker gets less effective CPU
time and does fewer LNS iterations per 60s. Quality per worker drops faster than the
diversity gain compensates. 4 workers (exp029) is the sweet spot for this hardware.
