# exp027: nano-destroy

**Branch:** exp/nano-destroy
**Date:** 2026-04-29
**Solver:** local_search
**Status:** pending

## Hypothesis

exp026 (1–6%) gave 37891.3 — 0.57% from exp011 (37675.6). Trend: each halving reduces cost
by ~0.4–0.5%. One more halving should bring us to [0.005, 0.02], cutting the gap by another
~0.4%.

**Hypothesis**: [0.005, 0.02] destroy ratio continues the improvement and may match or beat
exp011. At this level, k = max(1, int(0.02 * n_p)). For large instances (200+ patients),
max k ≈ 4. For small instances, k = 1 always. The periodic 50% perturbation restart provides
the global escape mechanism.

**Changes**: single parameter change — shift destroy ratio window from [0.01, 0.06] to [0.005, 0.02].

## Changes vs. Previous Kept Experiment

- `src/solvers/local_search.py`:
  - Change `min_destroy_ratio: float = 0.01` → `0.005`.
  - Change `max_destroy_ratio: float = 0.06` → `0.02`.

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
