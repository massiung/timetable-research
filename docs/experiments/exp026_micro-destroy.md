# exp026: micro-destroy

**Branch:** exp/micro-destroy
**Date:** 2026-04-29
**Solver:** local_search
**Status:** pending

## Hypothesis

exp025 showed that [0.03, 0.12] gives 38051.8 — better than [0.05, 0.20] (38235.9), continuing
the trend that smaller destroy = more iterations = better. Gap to exp011 (37675.6) is now ~1%.

**Hypothesis**: pushing destroy even smaller to [0.01, 0.06] (roughly 2× more iterations than
exp025) continues the improvement. At this range, k = max(1, int(0.06 * n_p)). For a 100-patient
instance, max k ≈ 6. The solver does very fine local search, relying on the N=100 perturbation
restarts for global escapes.

**Changes**: single parameter change — shift destroy ratio window from [0.03, 0.12] to [0.01, 0.06].
All other code identical to exp025.

## Changes vs. Previous Kept Experiment

- `src/solvers/local_search.py`:
  - Change `min_destroy_ratio: float = 0.03` → `0.01`.
  - Change `max_destroy_ratio: float = 0.12` → `0.06`.

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

<!-- What did we learn? See docs/learnings.md for any reusable insight. -->
