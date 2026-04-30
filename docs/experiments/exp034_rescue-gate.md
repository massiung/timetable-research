# exp034: rescue-gate

**Branch:** exp/rescue-gate
**Date:** 2026-04-30
**Solver:** local_search
**Status:** discard

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
| i01 | 5608 | 0 | 60.02 |
| i02 | 2451 | 0 | 60.02 |
| i03 | 12165 | 0 | 60.02 |
| i04 | 4444 | 0 | 60.02 |
| i05 | 14499 | 0 | 60.03 |
| i06 | 11810 | 0 | 60.03 |
| i07 | 8051 | 0 | 60.03 |
| i08 | 9500 | 0 | 60.04 |
| i09 | 12807 | 0 | 60.03 |
| i10 | 32240 | 0 | 60.03 |
| i11 | 32366 | 0 | 60.03 |
| i12 | 16789 | 0 | 60.04 |
| i13 | 27302 | 0 | 60.03 |
| i14 | 16698 | 0 | 60.04 |
| i15 | 23433 | 0 | 60.04 |
| i16 | 15047 | 4 | 60.03 |
| i17 | 73300 | 0 | 60.06 |
| i18 | 47814 | 0 | 60.05 |
| i19 | 69817 | 0 | 60.07 |
| i20 | 43201 | 0 | 60.03 |
| i21 | 40458 | 0 | 60.04 |
| i22 | 97885 | 0 | 60.07 |
| i23 | 57709 | 0 | 60.07 |
| i24 | 44149 | 0 | 60.06 |
| i25 | 19410 | 0 | 60.05 |
| i26 | 109386 | 0 | 60.13 |
| i27 | 101613 | 0 | 60.08 |
| i28 | 88657 | 0 | 60.06 |
| i29 | 24739 | 0 | 60.05 |
| i30 | 49499 | 0 | 60.05 |

**avg_cost:** 37855.2
**avg_time_s:** 60.04
**n_feasible:** 29 / 30

## Conclusion

**Decision:** discard

rescue_gate=5 (small destroy) gives 37855.2 — worse than exp029 (37761.8) by 93 points.
i16 regressed from exp033's violations=1 back to violations=4. The small-k blocking operator
(k=1-6 patients) fires earlier but removes too few targeted patients per step — iterating
over tiny targeted subsets without clearing the structural bottleneck (surgeon 2 capacity +
room availability for patients 10 and 59).

The exp033 insight is key: large destroy (k=20-50) was more effective at violations=1 than
small destroy + early blocking (violations=4). The blocking operator needs large k to
remove enough competing patients to open a feasible slot.

Next: exp035 — combine adaptive large destroy (exp033) + rescue_gate=0 (always use
blocking when infeasible). With large k AND always-on blocking, the targeted operator
removes 20-50 specifically competing patients per step from the first iteration.
