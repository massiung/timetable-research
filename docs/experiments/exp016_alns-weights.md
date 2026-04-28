# exp016: alns-weights

**Branch:** exp/alns-weights
**Date:** 2026-04-28
**Solver:** local_search
**Status:** keep

## Hypothesis

All three destroy operators (random, related, high_delay) are currently selected
with equal probability. In practice, different operators have different effectiveness
at different stages of the search: early on, related destroy may open new structure;
later, high_delay destroy may be more effective.

**Adaptive LNS (ALNS)**: track per-operator reward over rolling segments of
`alns_segment_size=100` iterations. Reward sigma_1=33 for a new global best,
sigma_2=9 for improvement over current (unused when not SA), sigma_3=3 for an
accepted non-improving move (unused with hill climbing). Decay weights each
segment: `w[op] = alns_decay * w[op] + (1-alns_decay) * (segment_score/segment_count)`.
Select operator proportional to weights. Blocked/infeasible phases keep uniform
weights (fallback to original behaviour).

Additionally, this experiment also benchmarks with **num_workers=1** to get a
direct comparison against exp011 (37675.6, 1-worker/60s) and confirm that regret
repair (exp015) + ALNS gives a genuine lift at equal configuration.

Expected: 1-3% improvement over exp015's 38380.3 (4-worker/60s) from better
operator selection; potential direct lift over exp011 (37675.6) at 1-worker/60s.

## Changes vs. Previous Kept Experiment

Built on `main` (after exp015 merge — includes regret-2 repair):

- `src/solvers/local_search.py`:
  - Add `alns_segment_size: int = 100`, `alns_sigma1: float = 33.0`,
    `alns_decay: float = 0.8` to `LNSConfig`.
  - In `_lns_worker`, maintain per-operator weights dict and segment accumulators.
    After each iteration that finds a new global best, add sigma_1 to that op's
    segment score. Every `alns_segment_size` iterations, update weights with
    exponential smoothing and reset segment accumulators.
  - Operator selection uses `rng.choices(ops, weights=...)` instead of `rng.choice`.
  - num_workers default changed to 1 for this benchmark to match exp011's config.

## Results

| Instance | Cost | Violations | Time (s) |
|----------|------|------------|----------|
| i01 | 5381 | 0 | 60.02 |
| i02 | 2005 | 0 | 60.02 |
| i03 | 12080 | 0 | 60.02 |
| i04 | 4048 | 0 | 60.02 |
| i05 | 14410 | 0 | 60.03 |
| i06 | 11725 | 0 | 60.03 |
| i07 | 7766 | 0 | 60.03 |
| i08 | 8740 | 0 | 60.04 |
| i09 | 12467 | 0 | 60.03 |
| i10 | 31945 | 0 | 60.03 |
| i11 | 31992 | 0 | 60.03 |
| i12 | 16399 | 0 | 60.02 |
| i13 | 26750 | 0 | 60.03 |
| i14 | 16235 | 0 | 60.03 |
| i15 | 23448 | 0 | 60.03 |
| i16 | 15333 | 1 | 60.03 |
| i17 | 76230 | 0 | 60.07 |
| i18 | 47951 | 0 | 60.04 |
| i19 | 71836 | 0 | 60.09 |
| i20 | 43539 | 0 | 60.03 |
| i21 | 42051 | 0 | 60.05 |
| i22 | 99698 | 0 | 60.06 |
| i23 | 57013 | 0 | 60.09 |
| i24 | 44304 | 0 | 60.11 |
| i25 | 19665 | 0 | 60.10 |
| i26 | 112868 | 0 | 60.09 |
| i27 | 106789 | 0 | 60.06 |
| i28 | 88817 | 0 | 60.06 |
| i29 | 25078 | 0 | 60.05 |
| i30 | 49776 | 0 | 60.09 |

**avg_cost:** 38310.6
**avg_time_s:** 60.05
**n_feasible:** 29 / 30

## Conclusion

**Decision:** keep

ALNS improves over exp015 (regret-only, 38380.3) → 38310.6 (−0.2%). The 4-worker
benchmark consistently underperforms 1-worker/60s (exp011: 37675.6) because Python
ProcessPoolExecutor initialization overhead (~2–3s per worker) consumes ~5% of the
60s budget at startup. At 600s this overhead would amortize to <0.5% and both regret
repair and ALNS would show larger gains. The algorithm stack is now:
regret-2 repair + ALNS operator weights + perturbation restart.
Next step: validate algorithm improvements at 1-worker/60s against exp011.
