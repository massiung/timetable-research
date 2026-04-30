# exp036: feasibility-phase

**Branch:** exp/feasibility-phase
**Date:** 2026-04-30
**Solver:** local_search
**Status:** pending decision

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
