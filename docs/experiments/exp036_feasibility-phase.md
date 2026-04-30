# exp036: feasibility-phase

**Branch:** exp/feasibility-phase
**Date:** 2026-04-30
**Solver:** local_search
**Status:** discard

## Hypothesis

Three experiments (exp033-035) tried to fix i16's structural infeasibility:
- exp033 (large destroy, rescue_gate=50): violations=1 — best so far; large k clears broad
  areas but blocking fires late (after 50 failed rescues with large k)
- exp034 (small destroy, rescue_gate=5): violations=4 — early blocking but k too small
- exp035 (large destroy, rescue_gate=0): violations=2 — always-on blocking dilutes operator
  pool; i20 badly hurt (+1431) because workers starting infeasible use large k for 60s

The root problem with exp033/035: when a normally-feasible instance (e.g., i20) has a
worker start infeasible, the adaptive large destroy fires for the entire 60s — wasting
iterations that should be doing cheap small-k refinement.

**Two-phase design**: If the greedy init is infeasible, run Phase 1 (large destroy [0.20,
0.50] + blocking always active) for at most `feasibility_phase_time=30s`. Phase 1 exits
early if feasibility is achieved. Phase 2 (normal small destroy + perturbation) runs for
the remainder of the 60s budget.

- Instances starting feasible: Phase 1 never fires → 60s of identical-to-exp029 LNS
- i20-like (transiently infeasible workers): Phase 1 runs briefly until feasibility is
  achieved, then ~59s of normal LNS — minimal overhead
- i16 (chronically infeasible): Phase 1 runs for full 30s with large k + blocking, then 30s
  of Phase 2 cost minimization if feasibility is achieved

**Hypothesis**: This caps the Phase 1 overhead precisely. For i16, 30s of intensive
large-k blocking (4 workers × 30s = 120 worker-seconds) has a significantly higher
probability of achieving feasibility than the previous 60s attempts with mixed strategies.
If i16 achieves violations=0 and cost ~17000, avg_cost drops to ~37070 — beating exp011.

**Changes** from exp029 (kept baseline):
- `src/solvers/local_search.py`:
  - Add `feasibility_phase_time: float = 30.0`, `infeasible_min_destroy: float = 0.20`,
    `infeasible_max_destroy: float = 0.50` to `LNSConfig`.
  - In `_lns_worker`: compute `phase1_end = start_time + feasibility_phase_time` if
    initially infeasible. Each iteration checks `in_phase1 = best_infeasible and now <
    phase1_end`; Phase 1 uses large k + always-blocking; Phase 2 uses normal small k +
    gated blocking + perturbation restart.
- `tests/test_local_search.py`: update `test_defaults` and add `test_phase1_large_blocking`.

## Changes vs. Previous Kept Experiment

- `src/solvers/local_search.py`:
  - Two-phase search: 30s large-destroy + always-blocking feasibility phase (if infeasible
    at greedy init), then normal small-destroy LNS for remainder of budget.

## Results

| Instance | Cost | Violations | Time (s) |
|----------|------|------------|----------|
| i01 | 5608 | 0 | 60.02 |
| i02 | 2451 | 0 | 60.02 |
| i03 | 12165 | 0 | 60.02 |
| i04 | 4444 | 0 | 60.03 |
| i05 | 14499 | 0 | 60.03 |
| i06 | 11810 | 0 | 60.03 |
| i07 | 8056 | 0 | 60.03 |
| i08 | 9491 | 0 | 60.03 |
| i09 | 12807 | 0 | 60.03 |
| i10 | 32240 | 0 | 60.03 |
| i11 | 32366 | 0 | 60.03 |
| i12 | 16789 | 0 | 60.03 |
| i13 | 27302 | 0 | 60.03 |
| i14 | 16830 | 0 | 60.04 |
| i15 | 23433 | 0 | 60.03 |
| i16 | 17528 | 2 | 60.03 |
| i17 | 73300 | 0 | 60.05 |
| i18 | 47814 | 0 | 60.04 |
| i19 | 69631 | 0 | 60.06 |
| i20 | 44233 | 0 | 60.04 |
| i21 | 40439 | 0 | 60.06 |
| i22 | 97814 | 0 | 60.06 |
| i23 | 57709 | 0 | 60.06 |
| i24 | 44149 | 0 | 60.08 |
| i25 | 19424 | 0 | 60.05 |
| i26 | 109376 | 0 | 60.07 |
| i27 | 101693 | 0 | 60.07 |
| i28 | 88657 | 0 | 60.06 |
| i29 | 24731 | 0 | 60.06 |
| i30 | 49480 | 0 | 60.06 |

**avg_cost:** 37887.6
**avg_time_s:** 60.04
**n_feasible:** 29 / 30

## Conclusion

**Decision:** discard

Two-phase (30s Phase 1 large destroy + blocking, then normal LNS) gives 37887.6 — worst of
the i16-targeting experiments, 126 points worse than exp029 (37761.8). i16: violations=2.
i20 regressed +1431 again — the phase exit condition doesn't help because some i20 workers
remain infeasible for the full 30s Phase 1 (large destroy cannot fix i20's minor infeasibility
faster than small destroy + rescue in exp029).

Final conclusion on the i16 feasibility direction (exp033-036):
- Best achieved: violations=1 (exp033, large destroy + rescue_gate=50)
- No variant achieves violations=0 within 60s
- All variants cause regression on i20 (and sometimes other instances) when large destroy
  is active during the infeasibility phase
- Large destroy actually SLOWS feasibility recovery on i20-like instances vs small destroy
  + rescue, because large k iterations are more expensive and the rescue mechanism is more
  effective at targeted mandatory-patient placement

**Stop targeting i16 feasibility.** Accept 29/30 as the benchmark feasibility and focus on
cost reduction across the 29 feasible instances. Any improvement to avg_cost on feasible
instances directly improves the benchmark score without risking regressions from adaptive
destroy. Next: exp037 — improve repair ordering (window-size sort key).
