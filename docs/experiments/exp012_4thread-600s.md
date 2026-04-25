# exp012: 4thread-600s

**Branch:** exp/4thread-600s
**Date:** 2026-04-23
**Solver:** local_search
**Status:** keep

## Hypothesis

Establish a new baseline using the full competition-legal configuration:

- **4 parallel LNS workers** (competition maximum) — each run spawns 4 independent
  trajectories with seeds `seed+0`…`seed+3`; the best-objective result is kept.
- **600 s time limit** (full 10-minute competition budget) — previous benchmarks used
  60 s, which is only 1/10 of the available time.

Expected outcome: substantially lower costs than exp011 (37675.6 avg, 60 s, 1 worker)
because (a) 4× more search diversity via parallel restarts, and (b) 10× more time per
instance for the LNS to converge.

This run also serves as the **reference baseline** for all future experiments, which
should now use the same 4-worker / 600 s configuration.

## Changes vs. Previous Kept Experiment

Built on `main` after exp011 merge:

- `src/solvers/local_search.py`:
  - Add `num_workers: int = 4` to `LNSConfig`.
  - Extract LNS loop into module-level `_lns_worker`; `solve()` spawns `num_workers`
    parallel processes via `ProcessPoolExecutor` and picks the best result.
- `scripts/benchmark.py`:
  - Default `--time-limit` changed from 60 s → 600 s.
  - New `--parallel N` flag (default 2) runs N instances concurrently via
    `ThreadPoolExecutor`.

## Results

| Instance | Cost | Violations | Time (s) |
|----------|------|------------|----------|
| i01 | 5427 | 0 | 600.11 |
| i02 | 2178 | 0 | 600.12 |
| i03 | 12090 | 0 | 600.14 |
| i04 | 4168 | 0 | 600.11 |
| i05 | 14492 | 0 | 600.11 |
| i06 | 11778 | 0 | 600.11 |
| i07 | 7420 | 0 | 600.11 |
| i08 | 8691 | 0 | 600.09 |
| i09 | 12414 | 0 | 600.10 |
| i10 | 32460 | 0 | 600.11 |
| i11 | 31862 | 0 | 600.10 |
| i12 | 16397 | 0 | 600.10 |
| i13 | 26889 | 0 | 600.13 |
| i14 | 16201 | 0 | 600.13 |
| i15 | 22627 | 0 | 600.11 |
| i16 | 16598 | 0 | 600.11 |
| i17 | 73940 | 0 | 600.10 |
| i18 | 47648 | 0 | 600.09 |
| i19 | 71167 | 0 | 600.12 |
| i20 | 42693 | 0 | 600.11 |
| i21 | 41365 | 0 | 600.09 |
| i22 | 98871 | 0 | 600.11 |
| i23 | 58028 | 0 | 600.12 |
| i24 | 44105 | 0 | 600.12 |
| i25 | 19422 | 0 | 600.11 |
| i26 | 110966 | 0 | 600.13 |
| i27 | 103626 | 0 | 600.13 |
| i28 | 88397 | 0 | 600.16 |
| i29 | 24639 | 0 | 600.09 |
| i30 | 48851 | 0 | 600.10 |

**avg_cost:** 37180.3
**avg_time_s:** 600.11
**n_feasible:** 30 / 30

## Conclusion

**Decision:** keep

- avg_cost 37180.3 vs exp011's 37675.6 — **-1.31% improvement**, every instance improved.
- 30/30 feasible maintained.
- Pure infrastructure gain: no algorithm change, just using the full competition time budget (600s vs 60s) and 4 parallel trajectories instead of 1.
- This is now the **reference baseline** for all future experiments (competition-legal configuration).

