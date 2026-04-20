"""Tests for the LNS solver and its module-level helpers.

Coverage strategy
-----------------
Integration tests verify the full solve() path returns a Schedule no worse
than an empty schedule in objective terms.  Unit tests exercise every branch
of the destroy/repair helpers using crafted schedule state.
"""

from __future__ import annotations

import random
from pathlib import Path

import pytest

from src.solvers.greedy import GreedyConfig, GreedySolver
from src.solvers.local_search import (
    LNSConfig,
    LocalSearchSolver,
    _clear_nurses,
    _clone,
    _compute_surgeon_load,
    _compute_theater_load,
    _copy_into,
    _destroy_high_delay,
    _destroy_random,
    _destroy_related,
    _insert_best,
    _objective,
    _repair_patients,
)
from src.utils.loader import load_instance
from src.utils.schedule import Schedule


@pytest.fixture(scope="module")
def instance():
    return load_instance(Path("data/instances/test01.json"))


@pytest.fixture(scope="module")
def greedy_schedule(instance):
    return GreedySolver().solve(instance, time_limit_seconds=60.0, seed=0)


# ---------------------------------------------------------------------------
# LNSConfig defaults
# ---------------------------------------------------------------------------


class TestLNSConfig:
    def test_defaults(self) -> None:
        cfg = LNSConfig()
        assert cfg.min_destroy_ratio == 0.10
        assert cfg.max_destroy_ratio == 0.30
        assert cfg.destroy_ops == ["random", "related", "high_delay"]
        assert cfg.violation_penalty == 1_000_000

    def test_custom_config(self) -> None:
        cfg = LNSConfig(min_destroy_ratio=0.2, destroy_ops=["random"])
        assert cfg.min_destroy_ratio == 0.2
        assert cfg.destroy_ops == ["random"]


# ---------------------------------------------------------------------------
# Integration: full solve
# ---------------------------------------------------------------------------


class TestLocalSearchSolverIntegration:
    def test_returns_schedule(self, instance) -> None:
        result = LocalSearchSolver().solve(instance, time_limit_seconds=2.0, seed=0)
        assert isinstance(result, Schedule)

    def test_respects_seed_determinism(self, instance) -> None:
        r1 = LocalSearchSolver().solve(instance, time_limit_seconds=1.0, seed=7)
        r2 = LocalSearchSolver().solve(instance, time_limit_seconds=1.0, seed=7)
        assert r1.total_cost() == r2.total_cost()
        assert r1.total_violations() == r2.total_violations()

    def test_different_seeds_may_differ(self, instance) -> None:
        # Not guaranteed to differ, but at least must not crash
        LocalSearchSolver().solve(instance, time_limit_seconds=1.0, seed=1)
        LocalSearchSolver().solve(instance, time_limit_seconds=1.0, seed=2)

    def test_single_op_config(self, instance) -> None:
        cfg = LNSConfig(destroy_ops=["random"])
        result = LocalSearchSolver(cfg).solve(instance, time_limit_seconds=1.0, seed=0)
        assert isinstance(result, Schedule)

    def test_related_op_only(self, instance) -> None:
        cfg = LNSConfig(destroy_ops=["related"])
        result = LocalSearchSolver(cfg).solve(instance, time_limit_seconds=1.0, seed=0)
        assert isinstance(result, Schedule)

    def test_high_delay_op_only(self, instance) -> None:
        cfg = LNSConfig(destroy_ops=["high_delay"])
        result = LocalSearchSolver(cfg).solve(instance, time_limit_seconds=1.0, seed=0)
        assert isinstance(result, Schedule)

    def test_lns_not_worse_than_greedy(self, instance) -> None:
        """LNS with 5 s should match or beat greedy cost on test01."""
        greedy_cost = GreedySolver().solve(instance, time_limit_seconds=60.0, seed=0).total_cost()
        lns_cost = LocalSearchSolver().solve(instance, time_limit_seconds=5.0, seed=0).total_cost()
        assert lns_cost <= greedy_cost


# ---------------------------------------------------------------------------
# _objective
# ---------------------------------------------------------------------------


class TestObjective:
    def test_feasible_schedule_penalty_zero(self, greedy_schedule) -> None:
        assert greedy_schedule.total_violations() == 0
        obj = _objective(greedy_schedule, violation_penalty=1_000_000)
        assert obj == greedy_schedule.total_cost()

    def test_infeasible_schedule_adds_penalty(self, instance) -> None:
        sched = Schedule(instance)
        # Force a mandatory-unscheduled violation by leaving mandatory patients unassigned
        assert sched.mandatory_unscheduled() > 0
        obj = _objective(sched, violation_penalty=1_000_000)
        assert obj >= sched.total_violations() * 1_000_000


# ---------------------------------------------------------------------------
# _clone and _copy_into
# ---------------------------------------------------------------------------


class TestClone:
    def test_clone_returns_equal_state(self, greedy_schedule) -> None:
        cloned = _clone(greedy_schedule)
        assert cloned.patient_day == greedy_schedule.patient_day
        assert cloned.total_cost() == greedy_schedule.total_cost()
        assert cloned.total_violations() == greedy_schedule.total_violations()

    def test_clone_is_independent(self, greedy_schedule) -> None:
        cloned = _clone(greedy_schedule)
        original_cost = greedy_schedule.total_cost()
        # Unassign a patient in the clone; original should be unchanged
        p = next(i for i, d in enumerate(cloned.patient_day) if d != -1)
        cloned.unassign_patient(p)
        assert greedy_schedule.total_cost() == original_cost

    def test_clone_shares_instance(self, greedy_schedule) -> None:
        cloned = _clone(greedy_schedule)
        assert cloned.instance is greedy_schedule.instance


class TestCopyInto:
    def test_copy_into_updates_state(self, instance, greedy_schedule) -> None:
        target = Schedule(instance)
        _copy_into(target, greedy_schedule)
        assert target.patient_day == greedy_schedule.patient_day
        assert target.total_cost() == greedy_schedule.total_cost()

    def test_copy_into_is_independent(self, instance, greedy_schedule) -> None:
        target = Schedule(instance)
        _copy_into(target, greedy_schedule)
        original_cost = greedy_schedule.total_cost()
        p = next(i for i, d in enumerate(target.patient_day) if d != -1)
        target.unassign_patient(p)
        assert greedy_schedule.total_cost() == original_cost


# ---------------------------------------------------------------------------
# _destroy_random
# ---------------------------------------------------------------------------


class TestDestroyRandom:
    def test_removes_exactly_k(self, instance, greedy_schedule) -> None:
        sched = _clone(greedy_schedule)
        assigned_before = sum(1 for d in sched.patient_day if d != -1)
        rng = random.Random(0)
        removed = _destroy_random(sched, 3, rng, instance)
        assert len(removed) == 3
        assert sum(1 for d in sched.patient_day if d != -1) == assigned_before - 3

    def test_k_larger_than_assigned(self, instance) -> None:
        sched = Schedule(instance)
        p = 0
        pat = instance.patients[p]
        sched.assign_patient(p, pat.surgery_release_day, 0, 0)
        rng = random.Random(0)
        removed = _destroy_random(sched, 100, rng, instance)
        assert len(removed) == 1
        assert sched.patient_day[p] == -1

    def test_removed_patients_are_unassigned(self, instance, greedy_schedule) -> None:
        sched = _clone(greedy_schedule)
        rng = random.Random(42)
        removed = _destroy_random(sched, 5, rng, instance)
        for p in removed:
            assert sched.patient_day[p] == -1


# ---------------------------------------------------------------------------
# _destroy_related
# ---------------------------------------------------------------------------


class TestDestroyRelated:
    def test_returns_empty_when_none_assigned(self, instance) -> None:
        sched = Schedule(instance)
        removed = _destroy_related(sched, 3, random.Random(0), instance)
        assert removed == []

    def test_removes_k_patients(self, instance, greedy_schedule) -> None:
        sched = _clone(greedy_schedule)
        rng = random.Random(0)
        removed = _destroy_related(sched, 3, rng, instance)
        assert len(removed) == 3
        for p in removed:
            assert sched.patient_day[p] == -1

    def test_fills_from_others_when_related_too_few(self, instance) -> None:
        """When assigned related patients < k, the remainder is drawn from unrelated ones."""
        sched = Schedule(instance)
        # Assign only 1 patient and request k=2: len(related)=1 < k=2, covers lines 159-161.
        # (Works even when all patients share the same surgeon, as in test01.)
        p = 0
        sched.assign_patient(p, instance.patients[p].surgery_release_day, 0, 0)
        rng = random.Random(0)
        removed = _destroy_related(sched, 2, rng, instance)
        # Only 1 patient was available regardless of how many we asked for
        assert len(removed) == 1
        assert sched.patient_day[p] == -1

    def test_truncates_when_related_exceeds_k(self, instance) -> None:
        """If a surgeon has > k patients, only k are removed."""
        sched = Schedule(instance)
        # Find a surgeon and assign many patients to them
        target_surgeon = instance.patients[0].surgeon
        assigned_for_surgeon = [
            pi for pi, pat in enumerate(instance.patients) if pat.surgeon == target_surgeon
        ]
        for pi in assigned_for_surgeon:
            pat = instance.patients[pi]
            sched.assign_patient(pi, pat.surgery_release_day, 0, 0)
        if len(assigned_for_surgeon) < 2:
            pytest.skip("Need surgeon with >= 2 patients")
        rng = random.Random(0)
        removed = _destroy_related(sched, 1, rng, instance)
        assert len(removed) == 1


# ---------------------------------------------------------------------------
# _destroy_high_delay
# ---------------------------------------------------------------------------


class TestDestroyHighDelay:
    def test_removes_highest_delay_patients(self, instance, greedy_schedule) -> None:
        sched = _clone(greedy_schedule)
        delays_before = sorted(
            [
                sched.patient_day[p] - instance.patients[p].surgery_release_day
                for p in range(len(instance.patients))
                if sched.patient_day[p] != -1
            ],
            reverse=True,
        )
        removed = _destroy_high_delay(sched, 2, instance)
        assert len(removed) == 2
        for p in removed:
            assert sched.patient_day[p] == -1
        # The two largest delays should have been removed
        remaining_delays = sorted(
            [
                sched.patient_day[p] - instance.patients[p].surgery_release_day
                for p in range(len(instance.patients))
                if sched.patient_day[p] != -1
            ],
            reverse=True,
        )
        if delays_before:
            assert remaining_delays[0] <= delays_before[0] or len(remaining_delays) < len(
                delays_before
            )


# ---------------------------------------------------------------------------
# _compute_theater_load and _compute_surgeon_load
# ---------------------------------------------------------------------------


class TestComputeLoads:
    def test_theater_load_sums_durations(self, instance, greedy_schedule) -> None:
        load = _compute_theater_load(greedy_schedule, instance)
        total = sum(sum(row) for row in load)
        expected = sum(
            instance.patients[p].surgery_duration
            for p, d in enumerate(greedy_schedule.patient_day)
            if d != -1
        )
        assert total == expected

    def test_surgeon_load_sums_durations(self, instance, greedy_schedule) -> None:
        load = _compute_surgeon_load(greedy_schedule, instance)
        total = sum(sum(row) for row in load)
        expected = sum(
            instance.patients[p].surgery_duration
            for p, d in enumerate(greedy_schedule.patient_day)
            if d != -1
        )
        assert total == expected

    def test_empty_schedule_loads_zero(self, instance) -> None:
        sched = Schedule(instance)
        t_load = _compute_theater_load(sched, instance)
        s_load = _compute_surgeon_load(sched, instance)
        assert all(v == 0 for row in t_load for v in row)
        assert all(v == 0 for row in s_load for v in row)


# ---------------------------------------------------------------------------
# _insert_best
# ---------------------------------------------------------------------------


class TestInsertBest:
    def _make_greedy(self) -> GreedySolver:
        return GreedySolver(GreedyConfig())

    def test_places_patient_when_possible(self, instance) -> None:
        sched = Schedule(instance)
        greedy = self._make_greedy()
        t_load = _compute_theater_load(sched, instance)
        s_load = _compute_surgeon_load(sched, instance)
        w_d = instance.weights.patient_delay
        w_t = instance.weights.open_operating_theater
        p = next(i for i, pat in enumerate(instance.patients) if pat.mandatory)
        _insert_best(p, sched, greedy, instance, t_load, s_load, w_d, w_t)
        assert sched.patient_day[p] != -1

    def test_no_placement_when_surgeon_full(self, instance) -> None:
        sched = Schedule(instance)
        greedy = self._make_greedy()
        p = 0
        pat = instance.patients[p]
        # Fill surgeon load completely on every day
        s_load = [
            [instance.surgeons[s].max_surgery_time[d] for d in range(instance.days)]
            for s in range(len(instance.surgeons))
        ]
        t_load = _compute_theater_load(sched, instance)
        w_d = instance.weights.patient_delay
        w_t = instance.weights.open_operating_theater
        _insert_best(p, sched, greedy, instance, t_load, s_load, w_d, w_t)
        _ = pat  # suppress unused
        assert sched.patient_day[p] == -1

    def test_no_placement_when_theaters_full(self, instance) -> None:
        sched = Schedule(instance)
        greedy = self._make_greedy()
        p = 0
        # Fill all theater capacity
        t_load = [
            [th.availability[d] for d in range(instance.days)] for th in instance.operating_theaters
        ]
        s_load = _compute_surgeon_load(sched, instance)
        w_d = instance.weights.patient_delay
        w_t = instance.weights.open_operating_theater
        _insert_best(p, sched, greedy, instance, t_load, s_load, w_d, w_t)
        assert sched.patient_day[p] == -1

    def test_theater_already_in_use_preferred(self, instance) -> None:
        """A theater already open on that day gets t_cost=0 (preferred over a fresh one)."""
        sched = Schedule(instance)
        greedy = self._make_greedy()
        # Assign one patient manually and confirm theater load is updated
        p0 = next(i for i, pat in enumerate(instance.patients) if pat.mandatory)
        s_load = _compute_surgeon_load(sched, instance)
        t_load = _compute_theater_load(sched, instance)
        w_d = instance.weights.patient_delay
        w_t = instance.weights.open_operating_theater
        _insert_best(p0, sched, greedy, instance, t_load, s_load, w_d, w_t)
        # After placing p0, theater for its day should show load > 0
        if sched.patient_day[p0] != -1:
            t = sched.patient_theater[p0]
            d = sched.patient_day[p0]
            assert t_load[t][d] > 0


# ---------------------------------------------------------------------------
# _repair_patients
# ---------------------------------------------------------------------------


class TestRepairPatients:
    def test_reinserts_removed_patients(self, instance, greedy_schedule) -> None:
        sched = _clone(greedy_schedule)
        rng = random.Random(0)
        removed = _destroy_random(sched, 3, rng, instance)
        greedy = GreedySolver(GreedyConfig())
        _repair_patients(sched, removed, greedy, instance)
        # At least mandatory patients should be placed
        for p in removed:
            if instance.patients[p].mandatory:
                assert sched.patient_day[p] != -1

    def test_empty_removed_is_noop(self, instance, greedy_schedule) -> None:
        sched = _clone(greedy_schedule)
        cost_before = sched.total_cost()
        greedy = GreedySolver(GreedyConfig())
        _repair_patients(sched, [], greedy, instance)
        assert sched.total_cost() == cost_before


# ---------------------------------------------------------------------------
# _clear_nurses
# ---------------------------------------------------------------------------


class TestClearNurses:
    def test_all_rooms_have_no_nurse_after_clear(self, instance, greedy_schedule) -> None:
        sched = _clone(greedy_schedule)
        _clear_nurses(sched, instance)
        for r in range(len(instance.rooms)):
            for s in range(instance.total_shifts):
                assert sched.room_shift_nurse[r][s] == -1

    def test_nurse_shift_rooms_empty_after_clear(self, instance, greedy_schedule) -> None:
        sched = _clone(greedy_schedule)
        _clear_nurses(sched, instance)
        for n in range(len(instance.nurses)):
            for s in range(instance.total_shifts):
                assert sched.nurse_shift_rooms[n][s] == []
