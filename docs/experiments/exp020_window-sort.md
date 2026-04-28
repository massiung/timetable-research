# exp020: window-sort

**Branch:** exp/window-sort
**Date:** 2026-04-28
**Solver:** local_search
**Status:** pending

## Hypothesis

exp019 confirmed that perturbation direction doesn't help — randomness is beneficial.
exp015/017 confirmed regret repair is too expensive (halves iteration count). 

The exp011 repair sort uses (mandatory, last_possible_day, -surgery_duration) — deadline-first.
Two patients with the same deadline but different release days get equal priority, even though
the one with a later release day has a narrower feasible window and is actually harder to place.

**Window sort**: sort by `(mandatory, last_possible_day − surgery_release_day, -surgery_duration)`.
This is O(1) per patient (no extra lookups) and places the most scheduling-constrained patients
first — those with the fewest feasible days. For patients sharing a deadline, those released later
(shorter window) come first.

**Hypothesis**: window sort improves placement quality in the repair step with zero iteration
overhead. Expected: 1–3% improvement over exp011 (37675.6) at 1-worker/60s.

**Changes**: single key change in `_repair_patients` sort. No ALNS, no regret. `num_workers=1`.

## Changes vs. Previous Kept Experiment

Built on `main` (after exp016 merge — includes regret-2 repair + ALNS), reverting to clean baseline:

- `src/solvers/local_search.py`:
  - Remove `_INF_COST` constant and `_compute_insertion_regret` function.
  - Change `_repair_patients` sort key from deadline-first to window-first:
    `(mandatory, last_possible_day − surgery_release_day, -surgery_duration)`.
  - Remove all ALNS code (config fields + runtime weight tracking).
  - Change `num_workers: int = 4` → `num_workers: int = 1`.

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
