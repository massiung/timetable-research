# exp029: multi-worker

**Branch:** exp/multi-worker
**Date:** 2026-04-30
**Solver:** local_search
**Status:** pending decision

## Hypothesis

exp026 ([0.01, 0.06] destroy, N=100, num_workers=1) gives 37891.3 — 0.57% above exp011
(37675.6). exp028 showed perturbation frequency is not the binding constraint. The remaining
gap is likely due to random seed luck: a single worker with seed=42 may plateau in a basin
that a different seed would escape.

**Hypothesis**: running 4 independent workers in parallel (each with a different seed offset)
and returning the best result across workers will reduce the gap to exp011. With 4 workers
and the same 60s wall-clock budget, we don't get more CPU time per worker — but with 4
diverse search trajectories, at least one is more likely to find a better basin.

This mirrors exp012 (4 workers, 600s) which achieved 37180.3. The delta between exp011 and
exp012 was 495 points (~1.3%) over 10× the time. A single 60s run with 4 workers should
capture some of that multi-seed diversity benefit.

**Changes**: single parameter change from exp026:
- `num_workers: int = 1` → `4`
- Everything else identical: [0.01, 0.06] destroy, N=100, ratio=0.50.

## Changes vs. Previous Kept Experiment

- `src/solvers/local_search.py`:
  - Change `num_workers: int = 1` → `4`.

## Results

| Instance | Cost | Violations | Time (s) |
|----------|------|------------|----------|
| i01 | 5608 | 0 | 60.02 |
| i02 | 2451 | 0 | 60.02 |
| i03 | 12165 | 0 | 60.02 |
| i04 | 4444 | 0 | 60.02 |
| i05 | 14491 | 0 | 60.02 |
| i06 | 11810 | 0 | 60.02 |
| i07 | 8046 | 0 | 60.02 |
| i08 | 9440 | 0 | 60.03 |
| i09 | 12807 | 0 | 60.02 |
| i10 | 32240 | 0 | 60.02 |
| i11 | 32329 | 0 | 60.02 |
| i12 | 16789 | 0 | 60.03 |
| i13 | 27302 | 0 | 60.02 |
| i14 | 16638 | 0 | 60.02 |
| i15 | 23271 | 0 | 60.03 |
| i16 | 14558 | 5 | 60.02 |
| i17 | 73015 | 0 | 60.04 |
| i18 | 47756 | 0 | 60.03 |
| i19 | 69476 | 0 | 60.05 |
| i20 | 42802 | 0 | 60.02 |
| i21 | 40382 | 0 | 60.03 |
| i22 | 97811 | 0 | 60.04 |
| i23 | 57554 | 0 | 60.05 |
| i24 | 44128 | 0 | 60.05 |
| i25 | 19361 | 0 | 60.04 |
| i26 | 108971 | 0 | 60.06 |
| i27 | 101276 | 0 | 60.05 |
| i28 | 88621 | 0 | 60.04 |
| i29 | 24683 | 0 | 60.03 |
| i30 | 49425 | 0 | 60.04 |

**avg_cost:** 37761.8
**avg_time_s:** 60.03
**n_feasible:** 29 / 30

## Conclusion

**Decision:** keep

4 workers (seed offsets 0–3) with [0.01, 0.06] destroy + N=100 gives 37761.8 — beating
exp026 (37891.3) by 129 points (~0.34%). This closes the gap to exp011 (37675.6) to just
86 points (0.23%). Multi-seed diversity adds real value even within the same 60s budget.

i16 remains infeasible (5 violations) consistent with all post-ALNS-merge experiments.
The 4-worker approach confirms that seed diversity is beneficial; further gains may come
from more workers or smarter seed selection.
