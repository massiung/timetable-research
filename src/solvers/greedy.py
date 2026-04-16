"""Greedy construction heuristic for the IHTP.

Phase 1 — Patient assignment:
    Sort patients by urgency (mandatory → last_possible_day → surgery_duration),
    then for each patient try days in order, picking the first that has a
    compatible room, surgeon capacity, and theater capacity.

Phase 2 — Nurse assignment:
    For every occupied (room, shift) pair assign the best available nurse
    contracted for that shift, with three tiers of fallback to guarantee
    every occupied room gets covered where nurses exist.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Literal

from src.solvers.base import Solver
from src.utils.model import Instance, Patient
from src.utils.schedule import Schedule


@dataclass
class GreedyConfig:
    """Knobs controlling every non-trivial choice in the greedy.

    All defaults produce a conservative but feasible (or near-feasible) solution.
    """

    # Ordering of patients before the assignment loop.
    # "urgency":          mandatory first, then last_possible_day asc,
    #                     then surgery_duration desc (longer ops scheduled first).
    # "constrained_first": sort by number of valid (day, room) options ascending
    #                     (most constrained patients first), with urgency as a
    #                     tie-breaker.  Better at avoiding mandatory-unscheduled
    #                     violations on instances with tight room or surgeon capacity.
    patient_sort_key: Literal["urgency", "constrained_first"] = "urgency"

    # Which day within [surgery_release_day, last_possible_day] to use.
    # "earliest": first valid day (deterministic).
    # "random":   shuffle candidate days — useful for seed-based diversity.
    day_selection: Literal["earliest", "random"] = "earliest"

    # Which compatible room to pick among candidates.
    # "first_available": first room in index order.
    # "least_loaded":    room with fewest current occupants on the admission day.
    room_selection: Literal["first_available", "least_loaded"] = "first_available"

    # Which theater to assign the surgery to.
    # "first_available": first theater with enough remaining capacity.
    # "consolidate":     prefer a theater already used on that day to minimise
    #                    the OpenOperatingTheater soft cost.
    theater_selection: Literal["first_available", "consolidate"] = "consolidate"

    # Which nurse to assign to an occupied (room, shift).
    # "highest_skill":     highest-skill available nurse (minimises skill shortfall).
    # "lowest_sufficient": lowest-skill nurse whose skill meets the room's maximum
    #                      requirement (conserves high-skill nurses for needier rooms).
    nurse_selection: Literal["highest_skill", "lowest_sufficient"] = "highest_skill"


class GreedySolver(Solver):
    """Two-phase greedy construction heuristic."""

    def __init__(self, config: GreedyConfig | None = None) -> None:
        self.config = config or GreedyConfig()

    def solve(self, instance: Instance, time_limit_seconds: float, seed: int) -> Schedule:
        rng = random.Random(seed)
        schedule = Schedule(instance)
        theater_day_load: list[list[int]] = [
            [0] * instance.days for _ in instance.operating_theaters
        ]
        surgeon_day_load: list[list[int]] = [[0] * instance.days for _ in instance.surgeons]
        self._assign_patients(instance, schedule, rng, theater_day_load, surgeon_day_load)
        self._assign_nurses(instance, schedule)
        return schedule

    # ------------------------------------------------------------------
    # Phase 1: patient scheduling
    # ------------------------------------------------------------------

    @staticmethod
    def _patient_priority(pat: Patient) -> tuple[int, int, int]:
        """Lower tuple → scheduled earlier (urgency key)."""
        return (0 if pat.mandatory else 1, pat.last_possible_day, -pat.surgery_duration)

    @staticmethod
    def _count_valid_options(p: int, instance: Instance) -> int:
        """Count valid (day, room) pairs for patient p, ignoring other patients.

        Used by the constrained_first sort key to give priority to patients
        with fewer options (tightly constrained by LOS, surgeon schedule, or
        gender-restricted occupancy).
        """
        pat = instance.patients[p]
        surgeon = instance.surgeons[pat.surgeon]
        count = 0
        for day in range(pat.surgery_release_day, pat.last_possible_day + 1):
            if surgeon.max_surgery_time[day] < pat.surgery_duration:
                continue
            for r, room in enumerate(instance.rooms):
                if r in pat.incompatible_rooms:
                    continue
                valid = True
                for d in range(day, min(day + pat.length_of_stay, instance.days)):
                    os_list = instance.occupants_by_room_day[r][d]
                    if len(os_list) + 1 > room.capacity:
                        valid = False
                        break
                    for oi in os_list:
                        if instance.occupants[oi].gender != pat.gender:
                            valid = False
                            break
                    if not valid:
                        break
                if valid:
                    count += 1
        return count

    def _assign_patients(
        self,
        instance: Instance,
        schedule: Schedule,
        rng: random.Random,
        theater_day_load: list[list[int]],
        surgeon_day_load: list[list[int]],
    ) -> None:
        if self.config.patient_sort_key == "constrained_first":
            options = [
                self._count_valid_options(p, instance) for p in range(len(instance.patients))
            ]
            order = sorted(
                range(len(instance.patients)),
                key=lambda p: (
                    0 if instance.patients[p].mandatory else 1,  # mandatory always first
                    options[p],  # then fewest options (most constrained)
                    instance.patients[p].last_possible_day,
                    -instance.patients[p].surgery_duration,
                ),
            )
        else:
            order = sorted(
                range(len(instance.patients)),
                key=lambda p: self._patient_priority(instance.patients[p]),
            )
        for p in order:
            self._try_assign_patient(p, instance, schedule, rng, theater_day_load, surgeon_day_load)

    def _try_assign_patient(
        self,
        p: int,
        instance: Instance,
        schedule: Schedule,
        rng: random.Random,
        theater_day_load: list[list[int]],
        surgeon_day_load: list[list[int]],
    ) -> bool:
        pat = instance.patients[p]
        days = list(range(pat.surgery_release_day, pat.last_possible_day + 1))
        if self.config.day_selection == "random":
            rng.shuffle(days)
        for day in days:
            s_idx = pat.surgeon
            if (
                surgeon_day_load[s_idx][day] + pat.surgery_duration
                > instance.surgeons[s_idx].max_surgery_time[day]
            ):
                continue
            room = self._find_room(p, day, instance, schedule)
            if room is None:
                continue
            theater = self._find_theater(p, day, instance, theater_day_load)
            if theater is None:
                continue
            schedule.assign_patient(p, day, room, theater)
            theater_day_load[theater][day] += pat.surgery_duration
            surgeon_day_load[s_idx][day] += pat.surgery_duration
            return True
        return False

    def _find_room(self, p: int, day: int, instance: Instance, schedule: Schedule) -> int | None:
        pat = instance.patients[p]
        candidates: list[int] = []
        for r, room in enumerate(instance.rooms):
            if r in pat.incompatible_rooms:
                continue
            valid = True
            for d in range(day, min(day + pat.length_of_stay, instance.days)):
                ps = schedule._room_day_patients[r][d]
                os_list = instance.occupants_by_room_day[r][d]
                if len(ps) + len(os_list) + 1 > room.capacity:
                    valid = False
                    break
                for other_p in ps:
                    if instance.patients[other_p].gender != pat.gender:
                        valid = False
                        break
                if not valid:
                    break
                for occ_idx in os_list:
                    if instance.occupants[occ_idx].gender != pat.gender:
                        valid = False
                        break
                if not valid:
                    break
            if valid:
                candidates.append(r)
        if not candidates:
            return None
        if self.config.room_selection == "first_available":
            return candidates[0]
        return min(
            candidates,
            key=lambda r: (
                len(schedule._room_day_patients[r][day])
                + len(instance.occupants_by_room_day[r][day])
            ),
        )

    def _find_theater(
        self,
        p: int,
        day: int,
        instance: Instance,
        theater_day_load: list[list[int]],
    ) -> int | None:
        pat = instance.patients[p]
        candidates = [
            t
            for t, th in enumerate(instance.operating_theaters)
            if theater_day_load[t][day] + pat.surgery_duration <= th.availability[day]
        ]
        if not candidates:
            return None
        if self.config.theater_selection == "first_available":
            return candidates[0]
        # "consolidate": prefer theaters already in use to reduce open-theater cost
        used = [t for t in candidates if theater_day_load[t][day] > 0]
        return used[0] if used else candidates[0]

    # ------------------------------------------------------------------
    # Phase 2: nurse assignment
    # ------------------------------------------------------------------

    def _assign_nurses(self, instance: Instance, schedule: Schedule) -> None:
        spd = instance.shifts_per_day
        for s in range(instance.total_shifts):
            d = s // spd
            available = instance.nurses_by_shift[s]
            nurse_load: dict[int, int] = {n: 0 for n in available}
            for r in range(len(instance.rooms)):
                if (
                    not schedule._room_day_patients[r][d]
                    and not instance.occupants_by_room_day[r][d]
                ):
                    continue
                room_load = self._room_load(r, s, d, instance, schedule)
                nurse = self._find_nurse(
                    r, s, d, room_load, available, nurse_load, instance, schedule
                )
                if nurse is not None:
                    schedule.assign_nurse(nurse, s, r)
                    nurse_load[nurse] += room_load

    def _room_load(self, r: int, s: int, d: int, instance: Instance, schedule: Schedule) -> int:
        spd = instance.shifts_per_day
        s_within = s % spd
        load = 0
        for p in schedule._room_day_patients[r][d]:
            s_rel = (d - schedule.patient_day[p]) * spd + s_within
            load += instance.patients[p].workload_produced[s_rel]
        for occ_idx in instance.occupants_by_room_day[r][d]:
            load += instance.occupants[occ_idx].workload_produced[s]
        return load

    def _find_nurse(
        self,
        r: int,
        s: int,
        d: int,
        room_load: int,
        available: list[int],
        nurse_load: dict[int, int],
        instance: Instance,
        schedule: Schedule,
    ) -> int | None:
        spd = instance.shifts_per_day
        s_within = s % spd
        max_required = 0
        for p in schedule._room_day_patients[r][d]:
            s_rel = (d - schedule.patient_day[p]) * spd + s_within
            max_required = max(max_required, instance.patients[p].skill_level_required[s_rel])
        for occ_idx in instance.occupants_by_room_day[r][d]:
            max_required = max(max_required, instance.occupants[occ_idx].skill_level_required[s])

        def fits_load(n: int) -> bool:
            return nurse_load[n] + room_load <= instance.nurses[n].max_load_by_shift[s]

        # Tier 1: sufficient skill and load fits within max_load
        eligible = [
            n for n in available if instance.nurses[n].skill_level >= max_required and fits_load(n)
        ]
        if not eligible:
            # Tier 2: relax load — skill still met, may create ExcessiveNurseWorkload cost
            eligible = [n for n in available if instance.nurses[n].skill_level >= max_required]
        if not eligible:
            # Tier 3: relax skill — any available nurse (creates RoomSkillLevel cost)
            eligible = list(available)
        if not eligible:
            return None

        if self.config.nurse_selection == "highest_skill":
            return max(eligible, key=lambda n: instance.nurses[n].skill_level)
        return min(eligible, key=lambda n: instance.nurses[n].skill_level)
