# exp028: less-perturb

**Branch:** exp/less-perturb
**Date:** 2026-04-29
**Solver:** local_search
**Status:** pending

## Hypothesis

exp026 (1–6% destroy, N=100) gives 37891.3. With k≈3 avg per iteration, the solver runs
~60,000 iterations in 60s, triggering ~600 perturbations. Each perturbation destroys 50%
of patients (k_perturb≈50 for 100-patient instances) — roughly 17× the regular iteration size.
The overhead from 600 perturbations may be excessive compared to exp011 (~150 perturbations).

**Hypothesis**: increasing no_improve_limit from 100 to 300 (3× fewer perturbations, ~200/run)
gives the solver more time to converge between restarts. The 50% perturbation size is preserved
for full escape power when it fires. Expected: 1–2% improvement over exp026 (37891.3).

**Changes**: two parameters change from exp026:
- `no_improve_limit: int = 100` → `300`
- Everything else identical: [0.01, 0.06] destroy, 3 ops, ratio=0.50, num_workers=1.

## Changes vs. Previous Kept Experiment

- `src/solvers/local_search.py`:
  - Change `no_improve_limit: int = 100` → `300`.

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
