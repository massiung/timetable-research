# exp026: micro-destroy

**Branch:** exp/micro-destroy
**Date:** 2026-04-29
**Solver:** local_search
**Status:** keep

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
| i01 | 5679 | 0 | 60.00 |
| i02 | 2451 | 0 | 60.00 |
| i03 | 12165 | 0 | 60.00 |
| i04 | 4546 | 0 | 60.00 |
| i05 | 14530 | 0 | 60.00 |
| i06 | 11810 | 0 | 60.00 |
| i07 | 8246 | 0 | 60.00 |
| i08 | 9581 | 0 | 60.00 |
| i09 | 12834 | 0 | 60.00 |
| i10 | 32620 | 0 | 60.00 |
| i11 | 32527 | 0 | 60.00 |
| i12 | 16789 | 0 | 60.00 |
| i13 | 27369 | 0 | 60.00 |
| i14 | 16786 | 0 | 60.00 |
| i15 | 23632 | 0 | 60.01 |
| i16 | 14988 | 5 | 60.01 |
| i17 | 72780 | 0 | 60.01 |
| i18 | 47822 | 0 | 60.00 |
| i19 | 70177 | 0 | 60.01 |
| i20 | 42790 | 0 | 60.01 |
| i21 | 40785 | 0 | 60.01 |
| i22 | 98517 | 0 | 60.01 |
| i23 | 57910 | 0 | 60.02 |
| i24 | 44115 | 0 | 60.02 |
| i25 | 19339 | 0 | 60.01 |
| i26 | 109070 | 0 | 60.02 |
| i27 | 101164 | 0 | 60.01 |
| i28 | 88660 | 0 | 60.01 |
| i29 | 24747 | 0 | 60.01 |
| i30 | 49407 | 0 | 60.01 |

**avg_cost:** 37891.3
**avg_time_s:** 60.01
**n_feasible:** 29 / 30

## Conclusion

**Decision:** keep

Micro destroy (1–6%) gives 37891.3 — 0.57% from exp011 (37675.6). Trend holds: each halving
of k reduces cost by ~0.4–0.5%. The small k + periodic large perturbation (N=100, 50%) is an
effective hybrid. Going even smaller (0.5–2%) may close the remaining gap.
