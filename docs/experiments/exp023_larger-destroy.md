# exp023: larger-destroy

**Branch:** exp/two-phase
**Date:** 2026-04-29
**Solver:** local_search
**Status:** pending

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
