# exp007: rescue-gate

**Branch:** exp/rescue-gate
**Date:** 2026-04-21
**Solver:** local_search
**Status:** pending decision

## Hypothesis

exp006 showed the surgeon-aware blocking destroy regressed i20 (+6.8%) because `best_infeasible`
fires from iteration 1 for any instance where `constrained_first` init leaves mandatories unscheduled
(i20 starts infeasible but rescue fixes it within ~10 iterations).

The core problem: `best_infeasible` can't distinguish:
- **Transient infeasibility** (i20): rescue quickly succeeds, blocking destroy is noise
- **Structural infeasibility** (i16): rescue repeatedly fails, blocking destroy is needed

Fix: gate blocking destroy on `rescue_fail_streak >= rescue_gate` (default: 50). Count
consecutive iterations where `_rescue_mandatory` was called and rescued 0 patients. Only
activate blocking destroy after 50 consecutive rescue failures — this implies a genuine
structural block, not just startup infeasibility.

## Changes vs. Previous Kept Experiment

Built on `exp/rescue-gate` (branched from main after exp004 merge):

- `src/solvers/local_search.py`:
  - Add `rescue_gate: int = 50` to `LNSConfig`.
  - Add `rescue_fail_streak` counter (int, starts at 0).
  - Only include `"blocking"` op when `best_infeasible AND rescue_fail_streak >= rescue_gate`.
  - Increment `rescue_fail_streak` when rescue was called and placed 0 mandatory patients.
  - Reset `rescue_fail_streak` to 0 when rescue places ≥1 patient, or when best becomes feasible.
  - Add `_destroy_blocking_mandatory`: same surgeon-aware blocking destroy as exp006.
- `tests/test_local_search.py`: add `_destroy_blocking_mandatory` import, `rescue_gate` assertion,
  and two tests for `_destroy_blocking_mandatory`.

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
| i08 | 9087 | 0 | 60.00 |
| i09 | 12694 | 0 | 60.00 |
| i10 | 32680 | 0 | 60.00 |
| i11 | 32103 | 0 | 60.00 |
| i12 | 16357 | 0 | 60.00 |
| i13 | 27108 | 0 | 60.00 |
| i14 | 16447 | 0 | 60.00 |
| i15 | 23515 | 0 | 60.00 |
| i16 | 17318 | 0 | 60.00 |
| i17 | 76375 | 0 | 60.00 |
| i18 | 48148 | 0 | 60.00 |
| i19 | 71645 | 0 | 60.00 |
| i20 | 42267 | 0 | 60.00 |
| i21 | 41868 | 0 | 60.00 |
| i22 | 99839 | 0 | 60.00 |
| i23 | 58246 | 0 | 60.01 |
| i24 | 44255 | 0 | 60.01 |
| i25 | 19795 | 0 | 60.00 |
| i26 | 112191 | 0 | 60.01 |
| i27 | 106921 | 0 | 60.01 |
| i28 | 88546 | 0 | 60.01 |
| i29 | 25007 | 0 | 60.00 |
| i30 | 49530 | 0 | 60.00 |

**avg_cost:** 37692.3
**avg_time_s:** 60.00
**n_feasible:** 30 / 30

## Conclusion

**Decision:** keep

- avg_cost 37692.3 vs exp004's 38415.3 — **-1.9% improvement**.
- **i16 is now feasible** (cost 17318, 0 violations) — first feasible result across all experiments.
- **30/30 instances feasible** — up from 29/30 in exp004.
- i20 unchanged (42267) — rescue-gate correctly prevented blocking destroy from firing during transient startup infeasibility. The rescue_fail_streak was reset before reaching 50.
- i10 slight regression (+180, +0.6%); i22 improvement (-657, -0.7%). Everything else identical or marginally better.
- Rescue-gate (N=50) is the key insight: distinguishes structural infeasibility (i16, streak stays high because rescue keeps failing) from transient infeasibility (i20, rescue fixes it early so streak never grows).

## What to try next (exp008)

1. **Tune rescue_gate**: try lower values (N=20, N=10) — faster activation of blocking destroy may help other potentially-hard instances without hurting the easy ones.
2. **Diversification via random restarts**: after convergence (no improvement for K iterations), reset to a fresh greedy solution. May escape deep local optima on large instances (i26, i27).
3. **Adaptive destroy size**: scale k with remaining time — larger k early (exploration), smaller k late (exploitation).
