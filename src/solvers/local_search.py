"""Large Neighbourhood Search solver for the IHTP.

Initialises from GreedySolver output, then iterates destroy-repair cycles until
the time budget expires.  Three destroy operators are rotated randomly:

  random     — remove k uniformly-random assigned patients
  related    — remove k patients sharing the same surgeon as a randomly chosen seed
  high_delay — remove the k patients admitted latest relative to their release day

Repair scores each candidate placement (day, room, theater) by:
  delay_cost_delta + theater_opening_cost_delta
and takes the placement with the lowest score.  Nurses are cleared and
reassigned from scratch (greedy) after every repair.

Acceptance: keep the new solution if its weighted objective
  violations * PENALTY + total_cost
is strictly lower than the current best.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Literal

from src.solvers.base import Solver
from src.solvers.greedy import GreedyConfig, GreedySolver
from src.utils.model import Instance
from src.utils.schedule import Schedule

DestroyOp = Literal["random", "related", "high_delay"]


def _default_ops() -> list[DestroyOp]:
    return ["random", "related", "high_delay"]


@dataclass
class LNSConfig:
    min_destroy_ratio: float = 0.10
    max_destroy_ratio: float = 0.30
    destroy_ops: list[DestroyOp] = field(default_factory=_default_ops)
    violation_penalty: int = 1_000_000


class LocalSearchSolver(Solver):
    def __init__(self, config: LNSConfig | None = None) -> None:
        self.config = config or LNSConfig()

    def solve(self, instance: Instance, time_limit_seconds: float, seed: int) -> Schedule:
        rng = random.Random(seed)
        deadline = time.monotonic() + time_limit_seconds

        greedy = GreedySolver(GreedyConfig(patient_sort_key="constrained_first"))
        current = greedy.solve(instance, time_limit_seconds, seed)
        best = _clone(current)
        best_obj = _objective(best, self.config.violation_penalty)

        n_p = len(instance.patients)
        cfg = self.config

        while time.monotonic() < deadline:
            ratio = rng.uniform(cfg.min_destroy_ratio, cfg.max_destroy_ratio)
            k = max(1, int(ratio * n_p))
            op: DestroyOp = rng.choice(cfg.destroy_ops)

            if op == "random":
                removed = _destroy_random(current, k, rng, instance)
            elif op == "related":
                removed = _destroy_related(current, k, rng, instance)
            else:
                removed = _destroy_high_delay(current, k, instance)

            _repair_patients(current, removed, greedy, instance)
            _clear_nurses(current, instance)
            greedy._assign_nurses(instance, current)

            obj = _objective(current, cfg.violation_penalty)
            if obj < best_obj:
                best = _clone(current)
                best_obj = obj
            else:
                _copy_into(current, best)

        return best


# ---------------------------------------------------------------------------
# Objective
# ---------------------------------------------------------------------------


def _objective(schedule: Schedule, violation_penalty: int) -> int:
    return schedule.total_violations() * violation_penalty + schedule.total_cost()


# ---------------------------------------------------------------------------
# Schedule copy helpers
# ---------------------------------------------------------------------------


def _clone(schedule: Schedule) -> Schedule:
    """Return a new Schedule sharing the same Instance but with copied state."""
    inst = schedule.instance
    s = Schedule(inst)
    s.patient_day = schedule.patient_day[:]
    s.patient_room = schedule.patient_room[:]
    s.patient_theater = schedule.patient_theater[:]
    s.room_shift_nurse = [row[:] for row in schedule.room_shift_nurse]
    s.nurse_shift_rooms = [
        [list(rooms) for rooms in nurse_shifts] for nurse_shifts in schedule.nurse_shift_rooms
    ]
    s._room_day_patients = [
        [list(day_list) for day_list in room_days] for room_days in schedule._room_day_patients
    ]
    return s


def _copy_into(target: Schedule, source: Schedule) -> None:
    """Overwrite target's assignment state with source's (in-place, no allocation)."""
    target.patient_day = source.patient_day[:]
    target.patient_room = source.patient_room[:]
    target.patient_theater = source.patient_theater[:]
    target.room_shift_nurse = [row[:] for row in source.room_shift_nurse]
    target.nurse_shift_rooms = [
        [list(rooms) for rooms in nurse_shifts] for nurse_shifts in source.nurse_shift_rooms
    ]
    target._room_day_patients = [
        [list(day_list) for day_list in room_days] for room_days in source._room_day_patients
    ]


# ---------------------------------------------------------------------------
# Destroy operators
# ---------------------------------------------------------------------------


def _destroy_random(
    schedule: Schedule, k: int, rng: random.Random, instance: Instance
) -> list[int]:
    assigned = [p for p in range(len(instance.patients)) if schedule.patient_day[p] != -1]
    to_remove = rng.sample(assigned, min(k, len(assigned)))
    for p in to_remove:
        schedule.unassign_patient(p)
    return to_remove


def _destroy_related(
    schedule: Schedule, k: int, rng: random.Random, instance: Instance
) -> list[int]:
    assigned = [p for p in range(len(instance.patients)) if schedule.patient_day[p] != -1]
    if not assigned:
        return []
    seed_p = rng.choice(assigned)
    surgeon = instance.patients[seed_p].surgeon
    related = [p for p in assigned if instance.patients[p].surgeon == surgeon]
    if len(related) < k:
        others = [p for p in assigned if p not in set(related)]
        rng.shuffle(others)
        related = related + others[: k - len(related)]
    else:
        rng.shuffle(related)
        related = related[:k]
    for p in related:
        schedule.unassign_patient(p)
    return related


def _destroy_high_delay(schedule: Schedule, k: int, instance: Instance) -> list[int]:
    assigned = [p for p in range(len(instance.patients)) if schedule.patient_day[p] != -1]
    assigned.sort(
        key=lambda p: schedule.patient_day[p] - instance.patients[p].surgery_release_day,
        reverse=True,
    )
    to_remove = assigned[:k]
    for p in to_remove:
        schedule.unassign_patient(p)
    return to_remove


# ---------------------------------------------------------------------------
# Repair helpers
# ---------------------------------------------------------------------------


def _compute_theater_load(schedule: Schedule, instance: Instance) -> list[list[int]]:
    load = [[0] * instance.days for _ in instance.operating_theaters]
    for p, (d, _r, t) in enumerate(
        zip(schedule.patient_day, schedule.patient_room, schedule.patient_theater)
    ):
        if d != -1:
            load[t][d] += instance.patients[p].surgery_duration
    return load


def _compute_surgeon_load(schedule: Schedule, instance: Instance) -> list[list[int]]:
    load = [[0] * instance.days for _ in instance.surgeons]
    for p, d in enumerate(schedule.patient_day):
        if d != -1:
            load[instance.patients[p].surgeon][d] += instance.patients[p].surgery_duration
    return load


def _repair_patients(
    schedule: Schedule,
    removed: list[int],
    greedy: GreedySolver,
    instance: Instance,
) -> None:
    order = sorted(
        removed,
        key=lambda p: (
            0 if instance.patients[p].mandatory else 1,
            instance.patients[p].last_possible_day,
            -instance.patients[p].surgery_duration,
        ),
    )
    theater_load = _compute_theater_load(schedule, instance)
    surgeon_load = _compute_surgeon_load(schedule, instance)
    w_delay = instance.weights.patient_delay
    w_theater = instance.weights.open_operating_theater

    for p in order:
        _insert_best(p, schedule, greedy, instance, theater_load, surgeon_load, w_delay, w_theater)


def _insert_best(
    p: int,
    schedule: Schedule,
    greedy: GreedySolver,
    instance: Instance,
    theater_load: list[list[int]],
    surgeon_load: list[list[int]],
    w_delay: int,
    w_theater: int,
) -> None:
    pat = instance.patients[p]
    best: tuple[int, int, int] | None = None
    best_score = 0

    for day in range(pat.surgery_release_day, pat.last_possible_day + 1):
        s_idx = pat.surgeon
        if (
            surgeon_load[s_idx][day] + pat.surgery_duration
            > instance.surgeons[s_idx].max_surgery_time[day]
        ):
            continue

        room = greedy._find_room(p, day, instance, schedule)
        if room is None:
            continue

        for t, th in enumerate(instance.operating_theaters):
            if theater_load[t][day] + pat.surgery_duration > th.availability[day]:
                continue
            t_cost = 0 if theater_load[t][day] > 0 else w_theater
            score = (day - pat.surgery_release_day) * w_delay + t_cost
            if best is None or score < best_score:
                best_score = score
                best = (day, room, t)

    if best is not None:
        d, r, t = best
        schedule.assign_patient(p, d, r, t)
        theater_load[t][d] += pat.surgery_duration
        surgeon_load[pat.surgeon][d] += pat.surgery_duration


def _clear_nurses(schedule: Schedule, instance: Instance) -> None:
    n_r = len(instance.rooms)
    n_n = len(instance.nurses)
    n_s = instance.total_shifts
    schedule.room_shift_nurse = [[-1] * n_s for _ in range(n_r)]
    schedule.nurse_shift_rooms = [[[] for _ in range(n_s)] for _ in range(n_n)]
