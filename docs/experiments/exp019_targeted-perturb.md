# exp019: targeted-perturb

**Branch:** exp/targeted-perturb
**Date:** 2026-04-28
**Solver:** local_search
**Status:** pending

## Hypothesis

exp018 confirmed ALNS reduces diversity and hurts 1-worker/60s performance. exp017
showed regret repair halves iteration count. All "algorithmic" additions regress vs
exp011 (37675.6).

Key insight: the perturbation restart is the primary escape mechanism from local optima.
Currently it uses `_destroy_random`, which removes arbitrary patients. High-delay patients
are the dominant cost driver — their placement determines most of the `delay_cost`. By
targeting them in the perturbation restart (using `_destroy_high_delay`), we force the
search to re-explore placements for the most expensive patients after stagnation.

**Hypothesis**: replacing `_destroy_random` with `_destroy_high_delay` in the perturbation
restart has **zero per-iteration overhead** (same k, same repair, just different selection),
but guides perturbation toward the highest-cost region of the solution. Expected: 1–3%
improvement over exp011 (37675.6) at 1-worker/60s.

**Changes**: single line change in `_lns_worker` perturbation restart.
Also removed ALNS config fields and runtime code (returning to clean exp011 baseline).
`num_workers=1` (matching exp011's comparison point).

## Changes vs. Previous Kept Experiment

Built on `exp/alns-only-1w` (exp018 — no regret, num_workers=1), with ALNS removed:

- `src/solvers/local_search.py`:
  - Remove ALNS config fields (`alns_segment_size`, `alns_sigma1`, `alns_decay`).
  - Remove ALNS runtime variables and weight-update block from `_lns_worker`.
  - Replace `_destroy_random` with `_destroy_high_delay` in perturbation restart.
  - `num_workers: int = 1` (unchanged from exp018).

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
