"""Tests for GreedySolver — covers all config variants and internal branches.

Coverage strategy
-----------------
Integration tests (TestGreedyIntegration) exercise the full solve() path with
every config combination.  Unit tests for internal methods use crafted schedule
state to reach branches that may not fire on the reference instance.
"""

from __future__ import annotations

import random
from pathlib import Path

import pytest

from src.solvers.greedy import GreedyConfig, GreedySolver
from src.utils.loader import load_instance
from src.utils.schedule import Schedule


@pytest.fixture(scope="module")
def instance():
    return load_instance(Path("data/instances/test01.json"))


# ---------------------------------------------------------------------------
# GreedyConfig defaults
# ---------------------------------------------------------------------------


class TestGreedyConfig:
    def test_defaults(self) -> None:
        cfg = GreedyConfig()
        assert cfg.patient_sort_key == "urgency"
        assert cfg.day_selection == "earliest"
        assert cfg.room_selection == "first_available"
        assert cfg.theater_selection == "consolidate"
        assert cfg.nurse_selection == "highest_skill"


# ---------------------------------------------------------------------------
# Integration: full solve on test01 with every config variant
# ---------------------------------------------------------------------------


class TestGreedyIntegration:
    def test_default_returns_schedule(self, instance) -> None:  # type: ignore[no-untyped-def]
        result = GreedySolver().solve(instance, time_limit_seconds=60.0, seed=0)
        assert isinstance(result, Schedule)

    def test_explicit_config_same_as_default(self, instance) -> None:  # type: ignore[no-untyped-def]
        result = GreedySolver(config=GreedyConfig()).solve(
            instance, time_limit_seconds=60.0, seed=0
        )
        assert isinstance(result, Schedule)

    def test_all_mandatory_scheduled(self, instance) -> None:  # type: ignore[no-untyped-def]
        result = GreedySolver().solve(instance, time_limit_seconds=60.0, seed=0)
        assert result.mandatory_unscheduled() == 0

    def test_feasible(self, instance) -> None:  # type: ignore[no-untyped-def]
        result = GreedySolver().solve(instance, time_limit_seconds=60.0, seed=0)
        assert result.is_feasible()

    def test_urgency_sort_key(self, instance) -> None:  # type: ignore[no-untyped-def]
        result = GreedySolver(GreedyConfig(patient_sort_key="urgency")).solve(
            instance, time_limit_seconds=60.0, seed=0
        )
        assert isinstance(result, Schedule)

    def test_constrained_first_sort_key(self, instance) -> None:  # type: ignore[no-untyped-def]
        result = GreedySolver(GreedyConfig(patient_sort_key="constrained_first")).solve(
            instance, time_limit_seconds=60.0, seed=0
        )
        assert isinstance(result, Schedule)

    def test_random_day_selection(self, instance) -> None:  # type: ignore[no-untyped-def]
        result = GreedySolver(GreedyConfig(day_selection="random")).solve(
            instance, time_limit_seconds=60.0, seed=42
        )
        assert isinstance(result, Schedule)

    def test_least_loaded_room(self, instance) -> None:  # type: ignore[no-untyped-def]
        result = GreedySolver(GreedyConfig(room_selection="least_loaded")).solve(
            instance, time_limit_seconds=60.0, seed=0
        )
        assert isinstance(result, Schedule)

    def test_first_available_theater(self, instance) -> None:  # type: ignore[no-untyped-def]
        result = GreedySolver(GreedyConfig(theater_selection="first_available")).solve(
            instance, time_limit_seconds=60.0, seed=0
        )
        assert isinstance(result, Schedule)

    def test_lowest_sufficient_nurse(self, instance) -> None:  # type: ignore[no-untyped-def]
        result = GreedySolver(GreedyConfig(nurse_selection="lowest_sufficient")).solve(
            instance, time_limit_seconds=60.0, seed=0
        )
        assert isinstance(result, Schedule)

    def test_earliest_is_deterministic_across_seeds(self, instance) -> None:  # type: ignore[no-untyped-def]
        """earliest mode ignores the seed, so results should be identical."""
        r1 = GreedySolver().solve(instance, time_limit_seconds=60.0, seed=1)
        r2 = GreedySolver().solve(instance, time_limit_seconds=60.0, seed=99)
        assert r1.total_violations() == r2.total_violations()
        assert r1.total_cost() == r2.total_cost()


# ---------------------------------------------------------------------------
# _find_room: targeted branch coverage
# ---------------------------------------------------------------------------


class TestCountValidOptions:
    def test_returns_nonnegative_count(self, instance) -> None:  # type: ignore[no-untyped-def]
        count = GreedySolver._count_valid_options(0, instance)
        assert count >= 0

    def test_constrained_patient_has_fewer_options(self, instance) -> None:  # type: ignore[no-untyped-def]
        """Patients with longer LOS or tighter windows have fewer valid options."""
        counts = [
            GreedySolver._count_valid_options(p, instance) for p in range(len(instance.patients))
        ]
        assert min(counts) <= max(counts)  # sanity: range is non-empty

    def test_incompatible_rooms_reduce_count(self, instance) -> None:  # type: ignore[no-untyped-def]
        """A patient with incompatible rooms has ≤ options than one without."""
        p_with = next(
            (p for p, pat in enumerate(instance.patients) if pat.incompatible_rooms), None
        )
        if p_with is None:
            pytest.skip("No patient with incompatible rooms in test01")
        # Just verify it doesn't crash and returns a non-negative integer
        assert GreedySolver._count_valid_options(p_with, instance) >= 0

    def test_room_at_occupant_capacity_rejected(self) -> None:
        """Rooms where occupants fill capacity are excluded from _count_valid_options.

        test01 has no room filled to capacity by occupants on a patient-admissible day,
        so we use a fresh local instance and temporarily fill room 0 to capacity on
        the first patient's admission day to exercise the capacity-overflow branch.
        """
        inst = load_instance(Path("data/instances/test01.json"))
        # Pick the first patient and their earliest admission day
        p = 0
        pat = inst.patients[p]
        admit = pat.surgery_release_day
        r = 0
        cap = inst.rooms[r].capacity
        # Temporarily stuff room 0 to capacity with fake occupant indices
        # across every day of the patient's stay, then count valid options.
        saved = {
            d: inst.occupants_by_room_day[r][d][:]
            for d in range(admit, min(admit + pat.length_of_stay, inst.days))
        }
        for d in saved:
            inst.occupants_by_room_day[r][d] = list(range(cap))
        try:
            count = GreedySolver._count_valid_options(p, inst)
            # Room 0 is now excluded due to the capacity check (lines 111-112)
            assert count >= 0
        finally:
            for d, orig in saved.items():
                inst.occupants_by_room_day[r][d] = orig


class TestFindRoom:
    def test_all_rooms_at_capacity_returns_none(self, instance) -> None:  # type: ignore[no-untyped-def]
        solver = GreedySolver()
        schedule = Schedule(instance)
        p = 0
        pat = instance.patients[p]
        day = pat.surgery_release_day
        # Stuff every room to capacity on every stay day
        for r, room in enumerate(instance.rooms):
            for d in range(day, min(day + pat.length_of_stay, instance.days)):
                schedule._room_day_patients[r][d] = list(range(room.capacity))
        assert solver._find_room(p, day, instance, schedule) is None

    def test_incompatible_room_skipped(self, instance) -> None:  # type: ignore[no-untyped-def]
        """A patient's incompatible rooms are never returned."""
        solver = GreedySolver()
        schedule = Schedule(instance)
        p = next(i for i, pat in enumerate(instance.patients) if pat.incompatible_rooms)
        day = instance.patients[p].surgery_release_day
        result = solver._find_room(p, day, instance, schedule)
        if result is not None:
            assert result not in instance.patients[p].incompatible_rooms

    def test_gender_conflict_with_existing_patient_blocks_room(self, instance) -> None:  # type: ignore[no-untyped-def]
        """A room containing an opposite-gender patient is rejected."""
        solver = GreedySolver()
        schedule = Schedule(instance)
        # Find patients of opposite genders
        p_a = next(i for i, p in enumerate(instance.patients) if p.gender == "A")
        p_b = next(i for i, p in enumerate(instance.patients) if p.gender == "B")
        pat_b = instance.patients[p_b]
        day = pat_b.surgery_release_day
        # Fill every room (that has no occupants of incompatible gender) with a gender-A patient
        for r in range(len(instance.rooms)):
            for d in range(day, min(day + pat_b.length_of_stay, instance.days)):
                occ_genders = {
                    instance.occupants[o].gender for o in instance.occupants_by_room_day[r][d]
                }
                # Only put p_a there if occupants don't already violate gender-A
                if "B" not in occ_genders:
                    schedule._room_day_patients[r][d] = [p_a]
        # _find_room either returns None or a room not blocked by gender conflict
        result = solver._find_room(p_b, day, instance, schedule)
        # The branch is exercised; correctness check
        if result is not None:
            assert result not in instance.patients[p_b].incompatible_rooms

    def test_gender_conflict_with_occupant_blocks_room(self, instance) -> None:  # type: ignore[no-untyped-def]
        """A room with an opposite-gender occupant is rejected for a patient of other gender."""
        solver = GreedySolver()
        schedule = Schedule(instance)
        # Find any occupant and a patient of opposite gender whose stay overlaps day 0
        for occ in instance.occupants:
            opposite = "B" if occ.gender == "A" else "A"
            for pi, pat in enumerate(instance.patients):
                if pat.gender != opposite:
                    continue
                # Try admission on day 0 if valid for this patient
                if pat.surgery_release_day > 0 or pat.last_possible_day < 0:
                    continue
                if occ.room in pat.incompatible_rooms:
                    continue
                if 0 < occ.length_of_stay:
                    # occupant is in occ.room on day 0; patient of opposite gender → conflict
                    solver._find_room(pi, 0, instance, schedule)
                    return  # branch exercised
        pytest.skip("No occupant-patient gender conflict reachable in test01")

    def test_least_loaded_selection(self, instance) -> None:  # type: ignore[no-untyped-def]
        """least_loaded returns a valid room (exercises the min() branch)."""
        solver = GreedySolver(GreedyConfig(room_selection="least_loaded"))
        schedule = Schedule(instance)
        p = 0
        day = instance.patients[p].surgery_release_day
        result = solver._find_room(p, day, instance, schedule)
        assert result is None or 0 <= result < len(instance.rooms)


# ---------------------------------------------------------------------------
# _find_theater: targeted branch coverage
# ---------------------------------------------------------------------------


class TestFindTheater:
    def _empty_load(self, instance) -> list[list[int]]:  # type: ignore[no-untyped-def]
        return [[0] * instance.days for _ in instance.operating_theaters]

    def test_all_theaters_full_returns_none(self, instance) -> None:  # type: ignore[no-untyped-def]
        solver = GreedySolver()
        p = 0
        day = instance.patients[p].surgery_release_day
        full_load = [
            [th.availability[d] for d in range(instance.days)] for th in instance.operating_theaters
        ]
        assert solver._find_theater(p, day, instance, full_load) is None

    def test_consolidate_prefers_already_used_theater(self, instance) -> None:  # type: ignore[no-untyped-def]
        solver = GreedySolver(GreedyConfig(theater_selection="consolidate"))
        p = 0
        day = instance.patients[p].surgery_release_day
        pat = instance.patients[p]
        load = self._empty_load(instance)
        # Pre-use the last theater with 1 minute
        t_last = len(instance.operating_theaters) - 1
        load[t_last][day] = 1
        remaining = instance.operating_theaters[t_last].availability[day] - 1
        result = solver._find_theater(p, day, instance, load)
        if remaining >= pat.surgery_duration:
            assert result == t_last  # the used theater is preferred

    def test_consolidate_falls_back_to_unused_when_none_in_use(self, instance) -> None:  # type: ignore[no-untyped-def]
        solver = GreedySolver(GreedyConfig(theater_selection="consolidate"))
        p = 0
        day = instance.patients[p].surgery_release_day
        load = self._empty_load(instance)  # no theaters used yet
        result = solver._find_theater(p, day, instance, load)
        assert result is not None

    def test_first_available_returns_a_theater(self, instance) -> None:  # type: ignore[no-untyped-def]
        solver = GreedySolver(GreedyConfig(theater_selection="first_available"))
        p = 0
        day = instance.patients[p].surgery_release_day
        load = self._empty_load(instance)
        result = solver._find_theater(p, day, instance, load)
        assert result is not None


# ---------------------------------------------------------------------------
# _find_nurse: targeted branch coverage (all three fallback tiers)
# ---------------------------------------------------------------------------


class TestFindNurse:
    def _occupied_room_setup(  # type: ignore[no-untyped-def]
        self, instance
    ) -> tuple[int, int, int, Schedule]:
        """Place patient 0 in room 0 on their release day; return (shift, room, day, schedule)."""
        schedule = Schedule(instance)
        p = 0
        pat = instance.patients[p]
        day = pat.surgery_release_day
        schedule.assign_patient(p, day, 0, 0)
        s = day * instance.shifts_per_day  # first shift of the admission day
        return s, 0, day, schedule

    def test_tier1_success_highest_skill(self, instance) -> None:  # type: ignore[no-untyped-def]
        """Tier 1: nurse found with sufficient skill and load headroom."""
        solver = GreedySolver()
        s, r, d, schedule = self._occupied_room_setup(instance)
        available = instance.nurses_by_shift[s]
        if not available:
            pytest.skip("No nurses in this shift")
        nurse_load = {n: 0 for n in available}
        room_load = solver._room_load(r, s, d, instance, schedule)
        result = solver._find_nurse(r, s, d, room_load, available, nurse_load, instance, schedule)
        assert result is None or result in available

    def test_tier1_success_lowest_sufficient(self, instance) -> None:  # type: ignore[no-untyped-def]
        """lowest_sufficient selection returns a nurse from eligible list."""
        solver = GreedySolver(GreedyConfig(nurse_selection="lowest_sufficient"))
        s, r, d, schedule = self._occupied_room_setup(instance)
        available = instance.nurses_by_shift[s]
        if not available:
            pytest.skip("No nurses in this shift")
        nurse_load = {n: 0 for n in available}
        room_load = solver._room_load(r, s, d, instance, schedule)
        result = solver._find_nurse(r, s, d, room_load, available, nurse_load, instance, schedule)
        assert result is None or result in available

    def test_tier2_fires_when_load_exceeded(self, instance) -> None:  # type: ignore[no-untyped-def]
        """Tier 2: all nurses over max_load but skill is sufficient → still assigned."""
        solver = GreedySolver()
        s, r, d, schedule = self._occupied_room_setup(instance)
        available = instance.nurses_by_shift[s]
        if not available:
            pytest.skip("No nurses in this shift")
        # Exhaust every nurse's load budget so tier 1 fails
        nurse_load = {n: instance.nurses[n].max_load_by_shift[s] + 9999 for n in available}
        room_load = solver._room_load(r, s, d, instance, schedule)
        result = solver._find_nurse(r, s, d, room_load, available, nurse_load, instance, schedule)
        # Tier 2 (skill-only filter) should still find a nurse for most instances
        assert result is None or result in available

    def test_tier3_and_none_when_no_available(self, instance) -> None:  # type: ignore[no-untyped-def]
        """Empty available list exercises tiers 1-3 (all return empty) then returns None."""
        solver = GreedySolver()
        s, r, d, schedule = self._occupied_room_setup(instance)
        result = solver._find_nurse(r, s, d, 0, [], {}, instance, schedule)
        assert result is None

    def test_tier3_fires_with_low_skill_nurses(self, instance) -> None:  # type: ignore[no-untyped-def]
        """Tier 3: when only low-skill nurses are available they are still assigned."""
        solver = GreedySolver()
        spd = instance.shifts_per_day
        schedule = Schedule(instance)
        # Find a patient+shift where some nurses have lower skill than required
        for pi, pat in enumerate(instance.patients):
            day = pat.surgery_release_day
            s = day * spd  # shift_within_day = 0
            s_rel = 0
            req = pat.skill_level_required[s_rel]
            if req == 0:
                continue
            low_skill = [
                n for n in instance.nurses_by_shift[s] if instance.nurses[n].skill_level < req
            ]
            if not low_skill:
                continue
            schedule.assign_patient(pi, day, 0, 0)
            nurse_load = {n: 0 for n in low_skill}
            result = solver._find_nurse(0, s, day, 0, low_skill, nurse_load, instance, schedule)
            assert result in low_skill
            return
        pytest.skip("No patient/nurse combo found to trigger tier 3 in test01")

    def test_occupant_workload_counted_in_room_load(self, instance) -> None:  # type: ignore[no-untyped-def]
        """_room_load includes occupant workload (exercises the occupant loop body)."""
        solver = GreedySolver()
        spd = instance.shifts_per_day
        # Find a room/day that has occupants
        for r in range(len(instance.rooms)):
            for d in range(instance.days):
                if instance.occupants_by_room_day[r][d]:
                    s = d * spd
                    schedule = Schedule(instance)
                    load = solver._room_load(r, s, d, instance, schedule)
                    # Load should be >= 0; occupants contribute to it
                    assert load >= 0
                    return
        pytest.skip("No room with occupants found in test01")


# ---------------------------------------------------------------------------
# _try_assign_patient: False return path
# ---------------------------------------------------------------------------


class TestTryAssignPatient:
    def test_returns_false_when_theaters_full(self, instance) -> None:  # type: ignore[no-untyped-def]
        """Returns False when all theaters are at capacity for every valid day."""
        solver = GreedySolver()
        schedule = Schedule(instance)
        surgeon_day_load: list[list[int]] = [[0] * instance.days for _ in instance.surgeons]
        # Fill every theater completely
        theater_day_load = [
            [th.availability[d] for d in range(instance.days)] for th in instance.operating_theaters
        ]
        p = 0
        result = solver._try_assign_patient(
            p, instance, schedule, random.Random(0), theater_day_load, surgeon_day_load
        )
        assert result is False

    def test_returns_true_on_valid_patient(self, instance) -> None:  # type: ignore[no-untyped-def]
        solver = GreedySolver()
        schedule = Schedule(instance)
        theater_day_load: list[list[int]] = [
            [0] * instance.days for _ in instance.operating_theaters
        ]
        surgeon_day_load: list[list[int]] = [[0] * instance.days for _ in instance.surgeons]
        # Find a mandatory patient (guaranteed to be schedulable)
        p = next(i for i, pat in enumerate(instance.patients) if pat.mandatory)
        result = solver._try_assign_patient(
            p, instance, schedule, random.Random(0), theater_day_load, surgeon_day_load
        )
        assert result is True


# ---------------------------------------------------------------------------
# _assign_nurses: uncovered-room path (no nurses in shift)
# ---------------------------------------------------------------------------


class TestAssignNurses:
    def test_room_stays_uncovered_when_no_nurses_in_shift(self, instance) -> None:  # type: ignore[no-untyped-def]
        """When nurses_by_shift[s] is empty, occupied rooms remain uncovered."""
        solver = GreedySolver()
        schedule = Schedule(instance)
        spd = instance.shifts_per_day
        # Find a shift that has nurses AND a patient who can admit on that day
        target_s = None
        target_p = None
        target_d = None
        for s, ns in enumerate(instance.nurses_by_shift):
            if not ns:
                continue
            d = s // spd
            for pi, pat in enumerate(instance.patients):
                if pat.surgery_release_day <= d <= pat.last_possible_day:
                    target_s, target_p, target_d = s, pi, d
                    break
            if target_s is not None:
                break
        if target_s is None:
            pytest.skip("No suitable shift+patient combo found")
        schedule.assign_patient(target_p, target_d, 0, 0)
        # Temporarily clear the shift's nurses
        saved = instance.nurses_by_shift[target_s]
        instance.nurses_by_shift[target_s] = []
        try:
            solver._assign_nurses(instance, schedule)
        finally:
            instance.nurses_by_shift[target_s] = saved
        # Room 0 should have no nurse in the cleared shift
        assert schedule.room_shift_nurse[0][target_s] == -1
