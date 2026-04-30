# exp029: multi-worker

**Branch:** exp/multi-worker
**Date:** 2026-04-30
**Solver:** local_search
**Status:** pending

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
