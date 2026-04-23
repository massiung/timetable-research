# exp012: 4thread-600s

**Branch:** exp/4thread-600s
**Date:** 2026-04-23
**Solver:** local_search
**Status:** pending decision

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

**avg_cost:** —
**avg_time_s:** —
**n_feasible:** — / 30

## Conclusion

**Decision:** pending

