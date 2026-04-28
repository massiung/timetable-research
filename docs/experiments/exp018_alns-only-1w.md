# exp018: alns-only-1w

**Branch:** exp/alns-only-1w
**Date:** 2026-04-28
**Solver:** local_search
**Status:** discard

## Hypothesis

exp017 showed regret repair halves iteration count at 60s/1-worker, causing a 2%
regression vs exp011. The ALNS operator-weight component from exp016 has negligible
overhead (just dict lookups per iteration). This experiment isolates the ALNS
contribution at 1-worker/60s by removing regret and keeping only ALNS.

**Changes**: remove `_compute_insertion_regret`, restore original sort in
`_repair_patients`, keep ALNS weights (sigma1=33, decay=0.8, seg=100), set
num_workers=1.

If ALNS alone beats exp011 (37675.6) at 1-worker/60s, we have a confirmed lift
with negligible iteration overhead.

## Changes vs. Previous Kept Experiment

Built on `main` (after exp016 merge — includes regret-2 repair + ALNS):

- `src/solvers/local_search.py`:
  - Remove `_INF_COST` constant and `_compute_insertion_regret` function.
  - Revert `_repair_patients` to original deadline-first sort.
  - Keep all ALNS code from exp016 (sigma1=33, decay=0.8, segment_size=100).
  - Change `num_workers: int = 4` → `num_workers: int = 1`.

## Results

| Instance | Cost | Violations | Time (s) |
|----------|------|------------|----------|
| i01 | 5440 | 0 | 60.00 |
| i02 | 2425 | 0 | 60.00 |
| i03 | 12120 | 0 | 60.00 |
| i04 | 4476 | 0 | 60.00 |
| i05 | 14742 | 0 | 60.00 |
| i06 | 11799 | 0 | 60.00 |
| i07 | 7731 | 0 | 60.00 |
| i08 | 9020 | 0 | 60.02 |
| i09 | 12792 | 0 | 60.00 |
| i10 | 32275 | 0 | 60.00 |
| i11 | 31932 | 0 | 60.00 |
| i12 | 16531 | 0 | 60.00 |
| i13 | 26971 | 0 | 60.00 |
| i14 | 16514 | 0 | 60.01 |
| i15 | 24118 | 0 | 60.00 |
| i16 | 15955 | 3 | 60.00 |
| i17 | 77280 | 0 | 60.02 |
| i18 | 48151 | 0 | 60.01 |
| i19 | 72325 | 0 | 60.02 |
| i20 | 43047 | 0 | 60.00 |
| i21 | 42430 | 0 | 60.01 |
| i22 | 100058 | 0 | 60.02 |
| i23 | 58664 | 0 | 60.01 |
| i24 | 44356 | 0 | 60.02 |
| i25 | 19597 | 0 | 60.01 |
| i26 | 112183 | 0 | 60.02 |
| i27 | 106655 | 0 | 60.01 |
| i28 | 88903 | 0 | 60.02 |
| i29 | 25053 | 0 | 60.01 |
| i30 | 49777 | 0 | 60.01 |

**avg_cost:** 38529.8
**avg_time_s:** 60.01
**n_feasible:** 29 / 30

## Conclusion

**Decision:** discard

ALNS alone (without regret) at 1-worker/60s gives 38529.8 — 2.3% WORSE than exp011 (37675.6).
i16 remains infeasible (3 violations). Root cause: ALNS operator-weight updates reduce search
diversity by concentrating exploration on operators that happened to find early improvements.
With only 3 operators and a noisy reward signal (improvements are rare events), the weight
updates cause premature convergence. Also, `rng.choices` with weights generates different random
sequences than `rng.choice`, altering the random number stream.

Key learning: ALNS is counterproductive with only 3 operators at 60s. Any improvement at
1-worker/60s must not reduce diversity or add per-iteration overhead. Next: test targeted
perturbation — replace random destroy in the perturbation restart with high_delay destroy,
which has zero overhead and targets the most delay-costly patients.
