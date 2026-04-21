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

## What to try next

TBD after results.
