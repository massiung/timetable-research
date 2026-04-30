# exp035: large-blocking

**Branch:** exp/large-blocking
**Date:** 2026-04-30
**Solver:** local_search
**Status:** discard

## Hypothesis

Two experiments targeted i16's structural infeasibility separately:
- exp033 (adaptive destroy [0.20, 0.50] when infeasible): violations=1 — large k clears
  many patients, giving broad escape power, but blocking operator only fires after 50 failed
  rescues (rescue_gate=50 with large k means ~50 large destructions ≈ many seconds before
  blocking activates).
- exp034 (rescue_gate=5, small destroy): violations=4 — blocking fires quickly but k=1-6 is
  too small to clear surgeon 2's bottleneck resource (rooms + capacity) in one step.

The combination: large k (20-50 patients) + blocking always active when infeasible
(rescue_gate=0) means:
1. From the very first iteration when infeasible, blocking is in the operator pool
2. Blocking with large k removes 20-50 patients specifically competing for the unscheduled
   mandatory patient's feasible slots — enough to open a path for patients 10 and 59 in i16
3. Once feasible, normal small destroy [0.01, 0.06] resumes for cost minimization
4. For all 29 instances starting feasible: no impact (infeasible path never fires)

**Hypothesis**: Combining adaptive large destroy + rescue_gate=0 gives earlier AND larger
blocking destructions for i16, increasing the probability of achieving feasibility within 60s.
If i16 achieves violations=0, avg_cost drops below exp011 (37675.6).

**Changes** from exp029 (kept baseline):
- `src/solvers/local_search.py`:
  - Add `infeasible_min_destroy: float = 0.20` and `infeasible_max_destroy: float = 0.50`.
  - Use `infeasible_min/max_destroy` for ratio when `best_infeasible=True`.
  - Change `rescue_gate: int = 50` → `rescue_gate: int = 0` (blocking always active when infeasible).
- `tests/test_local_search.py`: update `test_defaults` for new parameters.

## Changes vs. Previous Kept Experiment

- `src/solvers/local_search.py`:
  - Adaptive large destroy [0.20, 0.50] when infeasible + blocking operator always active
    when infeasible (rescue_gate=0).

## Results

| Instance | Cost | Violations | Time (s) |
|----------|------|------------|----------|
| i01 | 5608 | 0 | 60.02 |
| i02 | 2451 | 0 | 60.02 |
| i03 | 12165 | 0 | 60.02 |
| i04 | 4444 | 0 | 60.03 |
| i05 | 14499 | 0 | 60.04 |
| i06 | 11810 | 0 | 60.03 |
| i07 | 8051 | 0 | 60.02 |
| i08 | 9491 | 0 | 60.05 |
| i09 | 12807 | 0 | 60.03 |
| i10 | 32240 | 0 | 60.03 |
| i11 | 32366 | 0 | 60.03 |
| i12 | 16789 | 0 | 60.03 |
| i13 | 27302 | 0 | 60.03 |
| i14 | 16698 | 0 | 60.03 |
| i15 | 23433 | 0 | 60.04 |
| i16 | 15778 | 2 | 60.04 |
| i17 | 73300 | 0 | 60.05 |
| i18 | 47814 | 0 | 60.04 |
| i19 | 69668 | 0 | 60.08 |
| i20 | 44233 | 0 | 60.03 |
| i21 | 40458 | 0 | 60.05 |
| i22 | 97814 | 0 | 60.06 |
| i23 | 57683 | 0 | 60.06 |
| i24 | 44149 | 0 | 60.07 |
| i25 | 19410 | 0 | 60.05 |
| i26 | 109269 | 0 | 60.08 |
| i27 | 101613 | 0 | 60.07 |
| i28 | 88657 | 0 | 60.06 |
| i29 | 24731 | 0 | 60.04 |
| i30 | 49480 | 0 | 60.06 |

**avg_cost:** 37877.0
**avg_time_s:** 60.04
**n_feasible:** 29 / 30

## Conclusion

**Decision:** discard

Large destroy + rescue_gate=0 gives 37877.0 — worse than exp029 (37761.8) by 115 points.
i16: violations=2 (better than exp034's 4, but worse than exp033's 1). The always-on blocking
(rescue_gate=0) dilutes the operator pool: blocking fires from the first iteration but
competes with random/related/high_delay (25% selection probability each), reducing the
effective exploration in the infeasibility phase.

Additionally, i20 regressed badly (+1431 vs exp029) because some workers start infeasible on
i20 (greedy leaves mandatory patients unscheduled) and spend the entire 60s using large
destroy — far fewer iterations than the small-k baseline.

Key learnings consolidated from exp033-035:
1. Large destroy (large k) helps escape i16's structural infeasibility — violations improved
   from 5 (exp029) to 1 (exp033)
2. rescue_gate=50 (late blocking) is better than rescue_gate=0/5 (early blocking) for i16
3. The persistent regression on i20 reveals that some workers start infeasible on normally-
   feasible instances, and any adaptive-destroy approach hurts them

exp036 plan: two-phase approach — Phase 1 fires only when infeasible AND only for a fixed
time window (e.g., 30s); Phase 2 (normal small LNS) starts immediately once feasibility
is achieved OR after phase1_time expires. This caps the Phase 1 overhead for i20-like workers
(which quickly become feasible) while giving i16 workers a full dedicated feasibility phase.
