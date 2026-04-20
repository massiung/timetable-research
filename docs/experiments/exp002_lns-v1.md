# exp002: lns-v1

**Branch:** exp/lns-v1
**Date:** 2026-04-20
**Solver:** local_search
**Status:** pending decision

## Hypothesis

Implementing LNS on top of the greedy construction should lower average cost significantly and fix the infeasible i16 instance. The destroy-repair cycle allows the search to escape greedy's locally-optimal but globally-suboptimal assignments. With 580 s of budget, even a simple random-destroy + best-insertion repair should explore enough diverse solutions to beat the greedy baseline on most instances.

Three destroy operators: random removal, related removal (same surgeon), and high-delay removal (patients admitted latest relative to their release day). Repair scores placements by `delay * w_delay + theater_opening * w_theater` to target the two highest-cost drivers visible without a full delta evaluation.

## Changes vs. Previous Kept Experiment

- `src/solvers/local_search.py`: full LNS implementation replacing the placeholder stub.
- `tests/test_local_search.py`: new test file with 100% coverage of all LNS helpers.

## Results

| Instance | Cost | Violations | Time (s) |
|----------|------|------------|----------|
| i01 | 5532 | 0 | 60.00 |
| i02 | 2495 | 0 | 60.00 |
| i03 | 12120 | 0 | 60.00 |
| i04 | 4401 | 0 | 60.00 |
| i05 | 14655 | 0 | 60.00 |
| i06 | 11799 | 0 | 60.00 |
| i07 | 7824 | 0 | 60.00 |
| i08 | 9271 | 0 | 60.00 |
| i09 | 12694 | 0 | 60.00 |
| i10 | 32775 | 0 | 60.00 |
| i11 | 32103 | 0 | 60.00 |
| i12 | 16579 | 0 | 60.00 |
| i13 | 27108 | 0 | 60.00 |
| i14 | 16447 | 0 | 60.00 |
| i15 | 23505 | 0 | 60.00 |
| i16 | — | 10 | 60.00 |
| i17 | 76375 | 0 | 60.00 |
| i18 | 48148 | 0 | 60.00 |
| i19 | 71645 | 0 | 60.01 |
| i20 | — | 1 | 60.00 |
| i21 | 41868 | 0 | 60.00 |
| i22 | 99689 | 0 | 60.00 |
| i23 | 58246 | 0 | 60.00 |
| i24 | 44255 | 0 | 60.00 |
| i25 | 19795 | 0 | 60.00 |
| i26 | 112191 | 0 | 60.00 |
| i27 | 106921 | 0 | 60.00 |
| i28 | 88559 | 0 | 60.00 |
| i29 | 25007 | 0 | 60.00 |
| i30 | 49530 | 0 | 60.00 |

**avg_cost:** 38269.2
**avg_time_s:** 60.00
**n_feasible:** 28 / 30

## Conclusion

**Decision:** pending

- avg_cost improved from 43592.3 → 38269.2 (−12.2% vs greedy baseline).
- i16 remains infeasible with 10 violations (same as greedy) — the LNS destroy/repair cycle did not help this instance with the current operators.
- i20 regressed to infeasible (1 violation) vs greedy which had it feasible — the LNS accepted a worse state and failed to recover within the 60 s budget.
- All other instances improved or matched greedy cost.
- Feasible count: 28/30 vs 29/30 for greedy (regression on i20).
