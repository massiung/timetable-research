# exp008: adaptive-destroy

**Branch:** exp/adaptive-destroy
**Date:** 2026-04-22
**Solver:** local_search
**Status:** pending decision

## Hypothesis

exp007 (rescue-gate) achieved 30/30 feasible and -1.9% avg_cost improvement. Most instances converge
to the same cost as exp004, suggesting the solver reaches local optima early and can't escape with
a fixed destroy range [10%, 30%].

Adaptive destroy size: linearly decay the destroy ratio range from an early "exploratory" range
to a late "exploitative" range over the full time budget.

- Early (progress=0): draw k from [15%, 40%] — large destroys explore diverse regions
- Late (progress=1): draw k from [10%, 30%] — finer-grained improvement of best solution

Expected benefits:
- Large early destroys help escape initial local optima for large instances (i26, i27)
- Small late destroys fine-tune solutions without disrupting them
- No effect on feasibility (rescue-gate mechanism unchanged)

## Changes vs. Previous Kept Experiment

Built on `exp/adaptive-destroy` (branched from main after exp007 merge):

- `src/solvers/local_search.py`:
  - Add `early_min_destroy_ratio: float = 0.15` and `early_max_destroy_ratio: float = 0.40` to `LNSConfig`.
  - Track `start_time` before the main loop.
  - In each iteration, compute `progress = elapsed / time_limit_seconds` and interpolate:
    `cur_min = early_min + (min - early_min) * progress`
    `cur_max = early_max + (max - early_max) * progress`
- `tests/test_local_search.py`: add assertions for new LNSConfig defaults.

## Results

| Instance | Cost | Violations | Time (s) |
|----------|------|------------|----------|
| i01 | 5439 | 0 | 60.00 |
| i02 | 2550 | 0 | 60.00 |
| i03 | 12105 | 0 | 60.00 |
| i04 | 4424 | 0 | 60.00 |
| i05 | 14851 | 0 | 60.00 |
| i06 | 11799 | 0 | 60.00 |
| i07 | 8095 | 0 | 60.00 |
| i08 | 8825 | 0 | 60.00 |
| i09 | 12742 | 0 | 60.00 |
| i10 | 33195 | 0 | 60.00 |
| i11 | 32157 | 0 | 60.00 |
| i12 | 16597 | 0 | 60.00 |
| i13 | 27060 | 0 | 60.00 |
| i14 | 16535 | 0 | 60.00 |
| i15 | 23912 | 0 | 60.00 |
| i16 | — | 2 | 60.00 |
| i17 | 76720 | 0 | 60.01 |
| i18 | 48295 | 0 | 60.00 |
| i19 | 73390 | 0 | 60.00 |
| i20 | 43486 | 0 | 60.00 |
| i21 | 42176 | 0 | 60.00 |
| i22 | 101551 | 0 | 60.00 |
| i23 | 58788 | 0 | 60.00 |
| i24 | 44275 | 0 | 60.01 |
| i25 | 19853 | 0 | 60.00 |
| i26 | 113110 | 0 | 60.01 |
| i27 | 106854 | 0 | 60.00 |
| i28 | 88702 | 0 | 60.00 |
| i29 | 25014 | 0 | 60.00 |
| i30 | 49539 | 0 | 60.01 |

**avg_cost:** 38691.0
**avg_time_s:** 60.00
**n_feasible:** 29 / 30

## Conclusion

**Decision:** discard

- avg_cost 38691.0 vs exp007's 37692.3 — **+2.6% regression**.
- i16 back to infeasible (2 violations) — adaptive destroy breaks the rescue-gate mechanism.
- Root cause: large early destroys occasionally place the mandatory patient during `_repair_patients`
  (not rescue), which causes `_rescue_mandatory` to return 0 and increment `rescue_fail_streak` as if
  rescue failed. But since repair-placed solutions have high cost (many patients displaced), they never
  beat best_obj — so current is reset to best with the mandatory still unplaced. The streak oscillates
  instead of monotonically rising, and blocking destroy never fully activates for i16.
- Adaptive destroy and rescue-gate are incompatible: the former assumes a fixed baseline; the latter
  depends on steady-state rescue failure accumulation.

## What to try next (exp009)

1. **No-improvement restart (perturbation)**: when no improvement for K=500 iterations, do a large
   random destroy (50% of patients) to escape deep local optima. Then continue normally. This is
   orthogonal to rescue-gate and doesn't disrupt the streak mechanism.
2. **Improved related destroy**: group patients by day or room (not just surgeon) to target locally
   dense regions of the schedule. May help large instances stuck in same local optima.
