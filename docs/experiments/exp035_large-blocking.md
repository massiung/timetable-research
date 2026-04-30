# exp035: large-blocking

**Branch:** exp/large-blocking
**Date:** 2026-04-30
**Solver:** local_search
**Status:** pending decision

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
