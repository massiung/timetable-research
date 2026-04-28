# exp018: alns-only-1w

**Branch:** exp/alns-only-1w
**Date:** 2026-04-28
**Solver:** local_search
**Status:** pending

## Hypothesis

exp017 showed regret repair halves iteration count at 60s/1-worker, causing a 2%
regression vs exp011. The ALNS operator-weight component from exp016 has negligible
overhead (just dict lookups per iteration). This experiment isolates the ALNS
contribution at 1-worker/60s by removing regret and keeping only ALNS.

**Changes**: remove `_compute_insertion_regret`, restore original sort in
`_repair_patients`, keep ALNS weights (sigma1=33, decay=0.8, seg=100), set
num_workers=1.

If ALNS alone beats exp011 (37675.6) at 1-worker/60s, we have a confirmed lift
with negligible iteration overhead.

## Changes vs. Previous Kept Experiment

Built on `main` (after exp016 merge — includes regret-2 repair + ALNS):

- `src/solvers/local_search.py`:
  - Remove `_INF_COST` constant and `_compute_insertion_regret` function.
  - Revert `_repair_patients` to original deadline-first sort.
  - Keep all ALNS code from exp016 (sigma1=33, decay=0.8, segment_size=100).
  - Change `num_workers: int = 4` → `num_workers: int = 1`.

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
