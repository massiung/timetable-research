# exp001: greedy-baseline

**Branch:** exp/greedy-baseline
**Date:** 2026-04-20
**Solver:** greedy
**Status:** pending decision

## Hypothesis

Establish the baseline score for the default GreedySolver across all 30 non-test instances. No code changes — this is the reference point all future experiments are measured against.

## Changes vs. Previous Kept Experiment

First experiment — no prior baseline.

## Results

| Instance | Cost | Violations | Time (s) |
|----------|------|------------|----------|
| i01 | 6382 | 0 | 0.00 |
| i02 | 3595 | 0 | 0.00 |
| i03 | 13295 | 0 | 0.00 |
| i04 | 5058 | 0 | 0.00 |
| i05 | 18018 | 0 | 0.00 |
| i06 | 12269 | 0 | 0.00 |
| i07 | 9146 | 0 | 0.00 |
| i08 | 10364 | 0 | 0.00 |
| i09 | 13052 | 0 | 0.00 |
| i10 | 36625 | 0 | 0.00 |
| i11 | 37397 | 0 | 0.00 |
| i12 | 18438 | 0 | 0.00 |
| i13 | 32495 | 0 | 0.00 |
| i14 | 19148 | 0 | 0.00 |
| i15 | 27713 | 0 | 0.00 |
| i16 | — | 10 | 0.00 |
| i17 | 84960 | 0 | 0.00 |
| i18 | 54759 | 0 | 0.00 |
| i19 | 81100 | 0 | 0.01 |
| i20 | 47437 | 0 | 0.00 |
| i21 | 48680 | 0 | 0.00 |
| i22 | 114614 | 0 | 0.00 |
| i23 | 68643 | 0 | 0.01 |
| i24 | 48273 | 0 | 0.01 |
| i25 | 21546 | 0 | 0.00 |
| i26 | 131391 | 0 | 0.01 |
| i27 | 121384 | 0 | 0.01 |
| i28 | 93342 | 0 | 0.00 |
| i29 | 27511 | 0 | 0.00 |
| i30 | 57543 | 0 | 0.00 |

**avg_cost:** 43592.3
**avg_time_s:** <0.01 (greedy is near-instant)
**n_feasible:** 29 / 30

## Conclusion

**Decision:** keep

This is the baseline. i16 is the only infeasible instance — worth investigating what constraint fires there. Costs vary enormously (3595–131391), suggesting instance difficulty varies greatly. The near-zero solve time means the greedy has no time budget constraint — all time budget is available for future local search on top.
