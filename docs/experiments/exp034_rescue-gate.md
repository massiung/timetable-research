# exp034: rescue-gate

**Branch:** exp/rescue-gate
**Date:** 2026-04-30
**Solver:** local_search
**Status:** pending decision

## Hypothesis

exp029's 29-instance average (37761.8) is already ~638 points better than exp011's
equivalent 29 instances — the only reason exp011 (37675.6) looks better overall is that it
counts i16 as feasible (at ~16500 cost). Every attempted cost-reduction experiment (SA,
LAHC, adaptive destroy) has been discarded. **Beating exp011 requires solving i16.**

i16's infeasibility is structural: patients 10 and 59 both need surgeon 2, which has
capacity on only a few days; on those days, compatible rooms are already occupied. The
`_destroy_blocking_mandatory` operator exists to target this exact bottleneck — it removes
non-mandatory patients competing for the target mandatory patient's feasible slots. But it
only fires after `rescue_fail_streak >= rescue_gate` (currently 50). With ~10 LNS
iterations per second for i16, that's ~5 seconds of failed rescues before the blocking
operator even activates.

**Hypothesis**: Lowering `rescue_gate` from 50 to 5 makes the blocking destroy operator
fire within ~0.5 seconds of the search start for i16, giving much earlier targeted relief
for the structural bottleneck. Since `rescue_fail_streak` only increments when
`best_infeasible=True`, the 29 feasible instances are completely unaffected. This should
increase the probability of i16 achieving feasibility within 60s, enabling the solver to
then minimize cost for the remaining ~55s — pushing avg_cost below exp011 (37675.6).

**Changes** from exp029 (kept baseline):
- `src/solvers/local_search.py`:
  - `rescue_gate: int = 50` → `rescue_gate: int = 5`
- `tests/test_local_search.py`: update `test_defaults` to assert `cfg.rescue_gate == 5`.

## Changes vs. Previous Kept Experiment

- `src/solvers/local_search.py`:
  - Lower rescue_gate from 50 to 5 to activate blocking destroy much earlier for i16.

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
