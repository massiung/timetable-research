# exp023: larger-destroy

**Branch:** exp/two-phase
**Date:** 2026-04-29
**Solver:** local_search
**Status:** discard

## Hypothesis

All previous experiments at 1-worker/60s regressed vs exp011 (37675.6). Every attempted change
has hurt: ALNS (diversity reduction), regret repair (slower iterations), targeted perturbation
(less random), window sort (disrupts temporal spreading), faster perturbation (premature restarts),
heavy_day operator (dilution).

The one dimension not yet explored: the size of each destroy move. exp011 uses min=0.10,
max=0.30 (destroy 10–30% of patients per iteration). Shifting this window upward to 15–35%
means each move is slightly larger on average, escaping deeper local optima at the cost of more
repair work per iteration. Unlike phase-based changes, this is deterministic (no wall-clock
dependency) and preserves RNG seed determinism.

**Hypothesis**: larger destroy moves (15–35% vs 10–30%) give the solver a stronger kick out of
local optima, at the cost of slightly fewer iterations. The net effect may be positive if the
current basin-of-attraction is the binding constraint. Expected: 0–3% improvement over exp011.

**Changes**: single parameter change — shift destroy ratio window from [0.10, 0.30] to [0.15, 0.35].
All other code identical to exp011: deadline-first repair sort, 3 operators (random/related/high_delay),
N=100, ratio=0.50 perturbation, num_workers=1.

## Changes vs. Previous Kept Experiment

Built on `main` (after exp016 merge), reverting algorithmic additions:

- `src/solvers/local_search.py`:
  - Remove `_INF_COST`, `_compute_insertion_regret`; restore deadline-first repair sort.
  - Remove ALNS config fields and runtime weight tracking.
  - Change `num_workers: int = 4` → `num_workers: int = 1`.
  - Change `min_destroy_ratio: float = 0.10` → `0.15`.
  - Change `max_destroy_ratio: float = 0.30` → `0.35`.

## Results

| Instance | Cost | Violations | Time (s) |
|----------|------|------------|----------|
| i01 | 5469 | 0 | 60.00 |
| i02 | 2500 | 0 | 60.00 |
| i03 | 12120 | 0 | 60.00 |
| i04 | 4339 | 0 | 60.00 |
| i05 | 14944 | 0 | 60.00 |
| i06 | 11799 | 0 | 60.00 |
| i07 | 8035 | 0 | 60.00 |
| i08 | 9235 | 0 | 60.01 |
| i09 | 12755 | 0 | 60.00 |
| i10 | 32755 | 0 | 60.00 |
| i11 | 32235 | 0 | 60.01 |
| i12 | 16514 | 0 | 60.00 |
| i13 | 27340 | 0 | 60.01 |
| i14 | 16643 | 0 | 60.01 |
| i15 | 24012 | 0 | 60.01 |
| i16 | 15816 | 2 | 60.00 |
| i17 | 76960 | 0 | 60.01 |
| i18 | 48176 | 0 | 60.01 |
| i19 | 74470 | 0 | 60.02 |
| i20 | 44455 | 0 | 60.00 |
| i21 | 42953 | 0 | 60.01 |
| i22 | 101745 | 0 | 60.02 |
| i23 | 59292 | 0 | 60.01 |
| i24 | 44348 | 0 | 60.03 |
| i25 | 19964 | 0 | 60.01 |
| i26 | 113937 | 0 | 60.01 |
| i27 | 107681 | 0 | 60.02 |
| i28 | 88707 | 0 | 60.01 |
| i29 | 25181 | 0 | 60.01 |
| i30 | 49569 | 0 | 60.01 |

**avg_cost:** 38901.1
**avg_time_s:** 60.01
**n_feasible:** 29 / 30

## Conclusion

**Decision:** discard

Larger destroy window (15–35%) gives 38901.1 — 3.2% WORSE than exp011 (37675.6). i16 still
infeasible. Larger moves reduce total iteration count enough to outweigh any benefit from escaping
deeper local optima. The exp011 range of 10–30% is well-calibrated.

Key learning: the 10–30% destroy range in exp011 is near-optimal. Going larger (15–35%) hurts by
reducing iteration count. Going smaller has not been tested yet.
