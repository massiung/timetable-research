# exp013: three-candidates-EsclA

**Branch:** claude/exp011-three-candidates-EsclA
**Date:** 2026-04-25
**Solver:** local_search
**Status:** pending

## Hypothesis

Three targeted tweaks to the perturbation-restart LNS (exp011 baseline, 4-worker/600s config from exp012):

1. **Reduce perturb_ratio 0.50 → 0.30**: Smaller perturbation preserves more of the current
   solution's structure. After a restart the solver should land closer to the previous best and
   recover faster, giving more iterations for fine-grained convergence per restart cycle.

2. **Weighted op selection (20% random / 40% related / 40% high_delay)**: The `related` and
   `high_delay` operators are more targeted (surgeon clusters, delay-heavy patients); giving them
   more probability should improve the quality of the neighbourhood explored vs. pure uniform
   selection.

3. **Related destroy + room proximity**: Extend `_destroy_related` to also pull in patients who
   share the same room as the seed patient during overlapping stay days (in addition to same-surgeon
   grouping). Room cohabitants create cost interactions (gender mix, continuity-of-care) that
   surgeon-only grouping misses.

All three changes are incremental on the current best (exp012: avg_cost 37180.3, 4 workers, 600 s).

## Changes vs. Previous Kept Experiment

Built on main after exp012 merge:

- `src/solvers/local_search.py`:
  - `LNSConfig`: `perturb_ratio` default 0.50 → 0.30.
  - `LNSConfig`: new `destroy_op_weights: list[float]` (default `[1.0, 2.0, 2.0]`).
  - `_lns_worker`: op selection via `rng.choices(ops, weights=...)` instead of `rng.choice(ops)`.
  - `_destroy_related`: after building the surgeon-related set, add patients sharing the same room
    on overlapping stay days.
- `tests/test_local_search.py`: updated defaults assertions, new room-proximity test.

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

<!-- Fill after /benchmark run. -->
