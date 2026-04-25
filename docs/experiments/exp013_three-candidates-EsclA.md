# exp013: three-candidates-EsclA

**Branch:** claude/exp011-three-candidates-EsclA
**Date:** 2026-04-25
**Solver:** local_search
**Status:** pending decision

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
This benchmark run uses 60 s / 4 workers (matching exp011's config) for quick evaluation.

## Changes vs. Previous Kept Experiment

Built on main after exp012 merge:

- `src/solvers/local_search.py`:
  - `LNSConfig`: `perturb_ratio` default 0.50 → 0.30.
  - `LNSConfig`: new `destroy_op_weights: list[float]` (default `[1.0, 2.0, 2.0]`).
  - `_lns_worker`: op selection via `rng.choices(ops, weights=...)` instead of `rng.choice(ops)`.
  - `_destroy_related`: after building the surgeon-related set, add patients sharing the same room
    on overlapping stay days.
- `tests/test_local_search.py`: updated defaults assertions, new room-proximity test,
  incompatible-rooms unit test, timing-flaky determinism fix.

## Results

| Instance | Cost | Violations | Time (s) |
|----------|------|------------|----------|
| i01 | 5417 | 0 | 60.02 |
| i02 | 2287 | 0 | 60.02 |
| i03 | 12105 | 0 | 60.02 |
| i04 | 4185 | 0 | 60.02 |
| i05 | 14799 | 0 | 60.03 |
| i06 | 11778 | 0 | 60.02 |
| i07 | 7936 | 0 | 60.02 |
| i08 | 8916 | 0 | 60.04 |
| i09 | 12561 | 0 | 60.03 |
| i10 | 32990 | 0 | 60.03 |
| i11 | 31950 | 0 | 60.02 |
| i12 | 16498 | 0 | 60.02 |
| i13 | 27015 | 0 | 60.02 |
| i14 | 16358 | 0 | 60.03 |
| i15 | 23637 | 0 | 60.03 |
| i16 | 16597 | 1 | 60.03 |
| i17 | 75250 | 0 | 60.05 |
| i18 | 48097 | 0 | 60.03 |
| i19 | 72863 | 0 | 60.05 |
| i20 | 43654 | 0 | 60.02 |
| i21 | 41704 | 0 | 60.05 |
| i22 | 100214 | 0 | 60.06 |
| i23 | 58686 | 0 | 60.06 |
| i24 | 44307 | 0 | 60.06 |
| i25 | 19843 | 0 | 60.04 |
| i26 | 113105 | 0 | 60.06 |
| i27 | 106830 | 0 | 60.05 |
| i28 | 88787 | 0 | 60.06 |
| i29 | 25113 | 0 | 60.04 |
| i30 | 49456 | 0 | 60.06 |

**avg_cost:** 38494.5
**avg_time_s:** 60.04
**n_feasible:** 29 / 30

## Conclusion

**Decision:** pending

- avg_cost 38494.5 vs exp011's 37675.6 — **+2.2% regression** (worse, even excluding i16).
- **i16 infeasible** (1 violation): the feasibility gate held in exp011 but broke here. The
  solver finds cost 16597 (vs exp011's 17317) but with a constraint violation the validator
  catches — a known Python-vs-C++ model discrepancy that the three changes may be exposing
  more often.
- Mixed per-instance results: improvements on i01 (-3.2%), i02 (-9.5%), i04 (-4.4%), i17 (-2.2%),
  i08 (-3.3%); regressions on i07 (+3.0%), i19 (+1.0%), i20 (+2.1%), i26 (+1.4%), i27 (+1.4%).
- The three changes together appear to over-tune the search: more `related`/`high_delay` weight
  and larger related groups (room proximity) narrow the neighbourhood too much on larger instances,
  while the smaller perturbation (0.30) may not escape local optima as effectively as 0.50.
- Recommend **discard** and test each candidate in isolation to identify which (if any) helps.
