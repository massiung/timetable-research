# exp014: sa-acceptance

**Branch:** exp/sa-acceptance
**Date:** 2026-04-28
**Solver:** local_search
**Status:** discard

## Hypothesis

The current LNS uses pure greedy hill climbing — it only accepts improvements and
resets to best otherwise. This traps each worker in the first local optimum it finds.
Switching to **Simulated Annealing (SA) acceptance** should allow the search to escape
local optima and converge to significantly lower costs.

SA accepts a worse solution of cost-delta δ with probability `exp(-δ/T)` where T cools
from `T_0 = 0.02 × initial_cost` down via `T(i) = T_0 × sa_alpha^i` (iteration-based
exponential cooling with sa_alpha=0.9997) to maintain seed determinism.
Early in the run (hot), many diversifying moves are accepted; late in the run (cold),
only improvements pass — giving the solver time to exploit the better basin it found.

The perturbation restart (no_improve_limit=100) is kept but now tracks iterations since
the *best* improved, acting as a long-range escape hatch once the temperature is cold.

Expected: 3-8% improvement over exp012's 37180.3, especially on the large, expensive
instances (i17, i19, i22, i26, i27, i28) where greedy descent saturates earliest.

## Changes vs. Previous Kept Experiment

Built on `main` (after exp012 merge):

- `src/solvers/local_search.py`:
  - Add `sa_initial_temp_ratio: float = 0.02` and `sa_alpha: float = 0.9997`
    to `LNSConfig` — ratio calibrates T0 as fraction of initial feasible cost.
  - In `_lns_worker`, compute T(i) = T_0 × sa_alpha^i using iteration-based cooling
    (time-based cooling was initially tried but broke seed determinism).
  - Replace the "reset to best unless improving" acceptance with SA acceptance:
    accept if obj < current_obj always; accept if obj ≥ current_obj with probability
    exp(-δ/T); always update best when current beats it.
  - SA is applied only after the first feasible solution is found; during infeasible
    phases the original violation-penalty objective governs acceptance unchanged.
  - SA calibrates immediately if greedy init is feasible, or on infeasible→feasible
    transition inside the loop.

## Results

| Instance | Cost | Violations | Time (s) |
|----------|------|------------|----------|
| i01 | 5405 | 0 | 60.02 |
| i02 | 2300 | 0 | 60.02 |
| i03 | 12100 | 0 | 60.02 |
| i04 | 4224 | 0 | 60.02 |
| i05 | 14840 | 0 | 60.02 |
| i06 | 11778 | 0 | 60.03 |
| i07 | 7881 | 0 | 60.02 |
| i08 | 9003 | 0 | 60.03 |
| i09 | 12488 | 0 | 60.02 |
| i10 | 32625 | 0 | 60.03 |
| i11 | 31877 | 0 | 60.03 |
| i12 | 16498 | 0 | 60.02 |
| i13 | 27081 | 0 | 60.02 |
| i14 | 16519 | 0 | 60.03 |
| i15 | 23295 | 0 | 60.03 |
| i16 | 16907 | 1 | 60.03 |
| i17 | 77055 | 0 | 60.05 |
| i18 | 48146 | 0 | 60.03 |
| i19 | 73444 | 0 | 60.06 |
| i20 | 42937 | 0 | 60.03 |
| i21 | 42132 | 0 | 60.06 |
| i22 | 101235 | 0 | 60.05 |
| i23 | 58760 | 0 | 60.07 |
| i24 | 44334 | 0 | 60.07 |
| i25 | 19827 | 0 | 60.04 |
| i26 | 113425 | 0 | 60.06 |
| i27 | 106474 | 0 | 60.07 |
| i28 | 88772 | 0 | 60.05 |
| i29 | 25096 | 0 | 60.04 |
| i30 | 49270 | 0 | 60.06 |

**avg_cost:** 38580.0
**avg_time_s:** 60.04
**n_feasible:** 29 / 30

## Conclusion

**Decision:** discard

SA with alpha=0.9997 is too slow to cool at the 60s time budget. Each worker completes
only ~600 LNS iterations in 60s, so T(600) ≈ T0×0.83 — the solver stays near-maximal
temperature the entire run, accepting far too many worsening moves. Result is 2.4% worse
than exp011 (37675.6) and i16 becomes infeasible again. The iteration-based cooling
schedule is fundamentally mismatched to instance-size variability: small instances (fast
iterations) cool more than large ones, but large instances are where SA was most needed.

**Learning:** SA acceptance is not wrong in principle, but requires either (a) more
iterations (longer time budget), (b) faster cooling (alpha closer to 0.999 or lower),
or (c) instance-adaptive cooling. For the 60s competition setting, regret-based repair
is a higher-priority improvement target — it improves solution quality deterministically
at every iteration, without any parameter tuning.
