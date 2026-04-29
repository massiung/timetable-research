# exp027: nano-destroy

**Branch:** exp/nano-destroy
**Date:** 2026-04-29
**Solver:** local_search
**Status:** discard

## Hypothesis

exp026 (1–6%) gave 37891.3 — 0.57% from exp011 (37675.6). Trend: each halving reduces cost
by ~0.4–0.5%. One more halving should bring us to [0.005, 0.02], cutting the gap by another
~0.4%.

**Hypothesis**: [0.005, 0.02] destroy ratio continues the improvement and may match or beat
exp011. At this level, k = max(1, int(0.02 * n_p)). For large instances (200+ patients),
max k ≈ 4. For small instances, k = 1 always. The periodic 50% perturbation restart provides
the global escape mechanism.

**Changes**: single parameter change — shift destroy ratio window from [0.01, 0.06] to [0.005, 0.02].

## Changes vs. Previous Kept Experiment

- `src/solvers/local_search.py`:
  - Change `min_destroy_ratio: float = 0.01` → `0.005`.
  - Change `max_destroy_ratio: float = 0.06` → `0.02`.

## Results

| Instance | Cost | Violations | Time (s) |
|----------|------|------------|----------|
| i01 | 5679 | 0 | 60.00 |
| i02 | 2710 | 0 | 60.00 |
| i03 | 12235 | 0 | 60.00 |
| i04 | 4616 | 0 | 60.00 |
| i05 | 15799 | 0 | 60.00 |
| i06 | 11831 | 0 | 60.00 |
| i07 | 8516 | 0 | 60.00 |
| i08 | 10004 | 0 | 60.01 |
| i09 | 13239 | 0 | 60.00 |
| i10 | 33945 | 0 | 60.00 |
| i11 | 32896 | 0 | 60.00 |
| i12 | 17151 | 0 | 60.00 |
| i13 | 27550 | 0 | 60.00 |
| i14 | 17169 | 0 | 60.01 |
| i15 | 24755 | 0 | 60.01 |
| i16 | 15052 | 6 | 60.00 |
| i17 | 74260 | 0 | 60.01 |
| i18 | 48129 | 0 | 60.01 |
| i19 | 71382 | 0 | 60.02 |
| i20 | 43723 | 1 | 60.00 |
| i21 | 41593 | 0 | 60.00 |
| i22 | 100339 | 0 | 60.01 |
| i23 | 57889 | 0 | 60.02 |
| i24 | 44321 | 0 | 60.01 |
| i25 | 19485 | 0 | 60.01 |
| i26 | 110713 | 0 | 60.01 |
| i27 | 102696 | 0 | 60.02 |
| i28 | 88702 | 0 | 60.01 |
| i29 | 24981 | 0 | 60.01 |
| i30 | 50760 | 0 | 60.01 |

**avg_cost:** 38333.8
**avg_time_s:** 60.01
**n_feasible:** 28 / 30

## Conclusion

**Decision:** discard

Nano destroy (0.5–2%) gives 38333.8 with only 28/30 feasible — worse than exp026 (37891.3).
Moves are too small: k=1 for many instances means the solver can't escape local optima or
recover feasibility after perturbations. The sweet spot is around 1–6% (exp026).

Key learning: there is an optimal destroy window. Below 1% min/6% max, moves become too
fine-grained, diversity collapses, and infeasibility increases. exp026 [0.01, 0.06] is near-optimal.
