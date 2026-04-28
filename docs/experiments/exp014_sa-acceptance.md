# exp014: sa-acceptance

**Branch:** exp/sa-acceptance
**Date:** 2026-04-28
**Solver:** local_search
**Status:** pending

## Hypothesis

The current LNS uses pure greedy hill climbing — it only accepts improvements and
resets to best otherwise. This traps each worker in the first local optimum it finds.
Switching to **Simulated Annealing (SA) acceptance** should allow the search to escape
local optima and converge to significantly lower costs.

SA accepts a worse solution of cost-delta δ with probability `exp(-δ/T)` where T cools
from `T_0 = 0.02 × initial_cost` down to `T_final = T_0 × 1e-4` over the time budget.
Early in the run (hot), many diversifying moves are accepted; late in the run (cold),
only improvements pass — giving the solver time to exploit the better basin it found.

The perturbation restart (no_improve_limit=100) is kept but now tracks iterations since
the *best* improved, acting as a long-range escape hatch once the temperature is cold.

Expected: 3-8% improvement over exp012's 37180.3, especially on the large, expensive
instances (i17, i19, i22, i26, i27, i28) where greedy descent saturates earliest.

## Changes vs. Previous Kept Experiment

Built on `main` (after exp012 merge):

- `src/solvers/local_search.py`:
  - Add `sa_initial_temp_ratio: float = 0.02` and `sa_cooling_ratio: float = 1e-4`
    to `LNSConfig` — fractions of the initial feasible cost.
  - In `_lns_worker`, compute T(t) = T_0 × (sa_cooling_ratio)^(elapsed/total) using
    time-based exponential cooling.
  - Replace the "reset to best unless improving" acceptance with SA acceptance:
    accept if obj < current_obj always; accept if obj ≥ current_obj with probability
    exp(-δ/T); always update best when current beats it.
  - SA is applied only after the first feasible solution is found; during infeasible
    phases the original violation-penalty objective governs acceptance unchanged.

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
