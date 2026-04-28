# exp016: alns-weights

**Branch:** exp/alns-weights
**Date:** 2026-04-28
**Solver:** local_search
**Status:** pending

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
