# exp019: targeted-perturb

**Branch:** exp/targeted-perturb
**Date:** 2026-04-28
**Solver:** local_search
**Status:** discard

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
| i01 | 5532 | 0 | 60.00 |
| i02 | 2495 | 0 | 60.00 |
| i03 | 12120 | 0 | 60.00 |
| i04 | 4443 | 0 | 60.00 |
| i05 | 14765 | 0 | 60.00 |
| i06 | 11799 | 0 | 60.01 |
| i07 | 7835 | 0 | 60.00 |
| i08 | 9410 | 0 | 60.01 |
| i09 | 12757 | 0 | 60.00 |
| i10 | 33275 | 0 | 60.00 |
| i11 | 32124 | 0 | 60.00 |
| i12 | 16588 | 0 | 60.00 |
| i13 | 27207 | 0 | 60.00 |
| i14 | 16637 | 0 | 60.00 |
| i15 | 23858 | 0 | 60.01 |
| i16 | 16713 | 2 | 60.01 |
| i17 | 76990 | 0 | 60.01 |
| i18 | 48089 | 0 | 60.01 |
| i19 | 72279 | 0 | 60.01 |
| i20 | 43255 | 0 | 60.01 |
| i21 | 42025 | 0 | 60.01 |
| i22 | 100546 | 0 | 60.01 |
| i23 | 58833 | 0 | 60.03 |
| i24 | 44298 | 0 | 60.02 |
| i25 | 19801 | 0 | 60.01 |
| i26 | 114085 | 0 | 60.01 |
| i27 | 107068 | 0 | 60.01 |
| i28 | 88706 | 0 | 60.02 |
| i29 | 25324 | 0 | 60.01 |
| i30 | 49561 | 0 | 60.02 |

**avg_cost:** 38679.5
**avg_time_s:** 60.01
**n_feasible:** 29 / 30

## Conclusion

**Decision:** discard

Targeted perturbation (high_delay destroy) gives 38679.5 — 2.7% WORSE than exp011 (37675.6).
i16 still infeasible. Root cause: consistently targeting high-delay patients reduces exploration
diversity. The perturbation restart is meant to escape local optima by introducing variety; always
disrupting the same high-cost patients creates similar restart points and the solver converges to
similar local optima.

Key learning: randomness in the perturbation is beneficial, not a weakness. The uniform random
selection in exp011 is better than any deterministic targeting strategy. Next direction: improve
the repair sort ordering using a better O(1) criterion. Current sort uses deadline-first; a
flexibility-window sort (narrowest window = last_possible_day − surgery_release_day first) would
place the most scheduling-constrained patients first, which should lead to fewer stuck patients.
