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
| i01 | 5547 | 0 | 60.00 |
| i02 | 3026 | 0 | 60.00 |
| i03 | 12165 | 0 | 60.00 |
| i04 | 4751 | 0 | 60.00 |
| i05 | 14484 | 0 | 60.00 |
| i06 | 11800 | 0 | 60.00 |
| i07 | 8071 | 0 | 60.00 |
| i08 | 9691 | 0 | 60.01 |
| i09 | 12929 | 0 | 60.00 |
| i10 | 32515 | 0 | 60.00 |
| i11 | 32527 | 0 | 60.00 |
| i12 | 16789 | 0 | 60.00 |
| i13 | 27404 | 0 | 60.01 |
| i14 | 16798 | 0 | 60.01 |
| i15 | 23428 | 0 | 60.00 |
| i16 | 14988 | 5 | 60.00 |
| i17 | 72860 | 0 | 60.00 |
| i18 | 47601 | 0 | 60.01 |
| i19 | 69693 | 0 | 60.02 |
| i20 | 42572 | 0 | 60.00 |
| i21 | 40935 | 0 | 60.01 |
| i22 | 98502 | 0 | 60.02 |
| i23 | 57657 | 0 | 60.02 |
| i24 | 44126 | 0 | 60.02 |
| i25 | 19321 | 0 | 60.01 |
| i26 | 109249 | 0 | 60.02 |
| i27 | 101398 | 0 | 60.02 |
| i28 | 88569 | 0 | 60.01 |
| i29 | 24849 | 0 | 60.00 |
| i30 | 49644 | 0 | 60.01 |

**avg_cost:** 37893.1
**avg_time_s:** 60.01
**n_feasible:** 29 / 30

## Conclusion

**Decision:** discard

N=300 gives 37893.1 — essentially identical to exp026 (37891.3, N=100). Perturbation
frequency has no measurable effect at [0.01, 0.06] destroy ratios. The perturbation overhead
is not the binding constraint. N=100 is fine.
