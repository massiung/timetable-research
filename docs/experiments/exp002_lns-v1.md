# exp002: lns-v1

**Branch:** exp/lns-v1
**Date:** 2026-04-20
**Solver:** local_search
**Status:** pending

## Hypothesis

Implementing LNS on top of the greedy construction should lower average cost significantly and fix the infeasible i16 instance. The destroy-repair cycle allows the search to escape greedy's locally-optimal but globally-suboptimal assignments. With 580 s of budget, even a simple random-destroy + best-insertion repair should explore enough diverse solutions to beat the greedy baseline on most instances.

Three destroy operators: random removal, related removal (same surgeon), and high-delay removal (patients admitted latest relative to their release day). Repair scores placements by `delay * w_delay + theater_opening * w_theater` to target the two highest-cost drivers visible without a full delta evaluation.

## Changes vs. Previous Kept Experiment

- `src/solvers/local_search.py`: full LNS implementation replacing the placeholder stub.
- `tests/test_local_search.py`: new test file with 100% coverage of all LNS helpers.

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

**Decision:** keep / discard

<!-- What did we learn? See docs/learnings.md for any reusable insight. -->
