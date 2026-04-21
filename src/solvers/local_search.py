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

After repair, a mandatory-rescue pass attempts to place any unscheduled mandatory
patients, falling back to forced eviction of non-mandatory patients when needed.

Acceptance: keep the new solution if its weighted objective
  violations * PENALTY + total_cost
is strictly lower than the current best.

Logging: uses the standard ``logging`` module at level INFO (iteration summaries)
and DEBUG (per-iteration detail).  Enable with::

    import logging; logging.basicConfig(level=logging.DEBUG)

or set LOGLEVEL=DEBUG in the environment when running via main.py.
"""

from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass, field
from typing import Literal

from src.solvers.base import Solver
from src.solvers.greedy import GreedyConfig, GreedySolver
from src.utils.model import Instance
from src.utils.schedule import Schedule

_log = logging.getLogger(__name__)

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

        greedy = GreedySolver(GreedyConfig())
        current = greedy.solve(instance, time_limit_seconds, seed)
        best = _clone(current)
        best_obj = _objective(best, self.config.violation_penalty)

        n_undef = sum(
            1
            for p in range(len(instance.patients))
            if current.patient_day[p] == -1 and instance.patients[p].mandatory
        )
        _log.info(
            "init: violations=%d cost=%d unscheduled_mandatory=%d",
            best.total_violations(),
            best.total_cost(),
            n_undef,
        )

        n_p = len(instance.patients)
        cfg = self.config
        iters = 0

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
            rescued = _rescue_mandatory(current, greedy, instance)
            _clear_nurses(current, instance)
            greedy._assign_nurses(instance, current)

            obj = _objective(current, cfg.violation_penalty)
            if obj < best_obj:
                best = _clone(current)
                best_obj = obj
                _log.debug(
                    "iter %d: op=%s k=%d rescued=%d  NEW BEST violations=%d cost=%d",
                    iters,
                    op,
                    k,
                    rescued,
                    best.total_violations(),
                    best.total_cost(),
                )
            else:
                _copy_into(current, best)

            iters += 1

        _log.info(
            "done: iters=%d violations=%d cost=%d",
            iters,
            best.total_violations(),
            best.total_cost(),
        )
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


def _rescue_mandatory(
    schedule: Schedule,
    greedy: GreedySolver,
    instance: Instance,
) -> int:
    """Insert all unscheduled mandatory patients, using forced eviction if needed.

    First attempts a normal best-insertion for each.  Any still unscheduled
    receive a forced-insertion pass that evicts non-mandatory room occupants.

    Returns the number of newly scheduled mandatory patients.
    """
    unscheduled = [
        p
        for p in range(len(instance.patients))
        if schedule.patient_day[p] == -1 and instance.patients[p].mandatory
    ]
    if not unscheduled:
        return 0

    unscheduled.sort(
        key=lambda p: (
            instance.patients[p].last_possible_day,
            -instance.patients[p].surgery_duration,
        )
    )

    w_delay = instance.weights.patient_delay
    w_theater = instance.weights.open_operating_theater
    theater_load = _compute_theater_load(schedule, instance)
    surgeon_load = _compute_surgeon_load(schedule, instance)

    rescued = 0
    still_unscheduled: list[int] = []

    for p in unscheduled:
        _insert_best(p, schedule, greedy, instance, theater_load, surgeon_load, w_delay, w_theater)
        if schedule.patient_day[p] != -1:
            rescued += 1
            _log.debug("rescue(normal): placed p%d on day %d", p, schedule.patient_day[p])
        else:
            still_unscheduled.append(p)

    for p in still_unscheduled:
        evicted = _forced_insert(
            p, schedule, greedy, instance, theater_load, surgeon_load, w_delay, w_theater
        )
        if schedule.patient_day[p] != -1:
            rescued += 1
            _log.debug(
                "rescue(forced): placed p%d on day %d, evicted %d non-mandatory patients",
                p,
                schedule.patient_day[p],
                len(evicted),
            )
            for ep in sorted(
                evicted,
                key=lambda q: (
                    instance.patients[q].last_possible_day,
                    -instance.patients[q].surgery_duration,
                ),
            ):
                _insert_best(
                    ep, schedule, greedy, instance, theater_load, surgeon_load, w_delay, w_theater
                )
        else:
            _log.debug("rescue(failed): p%d has no feasible slot even with eviction", p)

    return rescued


def _forced_insert(
    p: int,
    schedule: Schedule,
    greedy: GreedySolver,
    instance: Instance,
    theater_load: list[list[int]],
    surgeon_load: list[list[int]],
    w_delay: int,
    w_theater: int,
) -> list[int]:
    """Insert mandatory patient p by evicting non-mandatory room occupants.

    Finds the (day, room, theater) slot that requires the fewest non-mandatory
    evictions.  All non-mandatory patients in the chosen room during p's stay
    window are evicted, then p is assigned and loads are updated.

    Returns the list of evicted patient indices (unassigned in-place).
    Returns [] and leaves p unassigned if no feasible slot exists.
    """
    pat = instance.patients[p]
    best_slot: tuple[int, int, int] | None = None
    best_evict: list[int] = []
    best_score: tuple[float, float] = (float("inf"), float("inf"))

    for day in range(pat.surgery_release_day, pat.last_possible_day + 1):
        s_idx = pat.surgeon
        if (
            surgeon_load[s_idx][day] + pat.surgery_duration
            > instance.surgeons[s_idx].max_surgery_time[day]
        ):
            continue

        for r, room in enumerate(instance.rooms):
            if r in pat.incompatible_rooms:
                continue

            to_evict_set: set[int] = set()
            feasible = True
            for stay_d in range(day, min(day + pat.length_of_stay, instance.days)):
                room_pats = schedule._room_day_patients[r][stay_d]
                n_occ = len(instance.occupants_by_room_day[r][stay_d])
                mandatory_cnt = sum(1 for q in room_pats if instance.patients[q].mandatory)
                # Even after evicting all non-mandatory, not enough capacity
                if mandatory_cnt + n_occ + 1 > room.capacity:
                    feasible = False
                    break
                for q in room_pats:
                    if not instance.patients[q].mandatory:
                        to_evict_set.add(q)

            if not feasible:
                continue

            to_evict = list(to_evict_set)

            # Gender check: remaining mandatory patients + occupants must match gender
            gender_ok = True
            for stay_d in range(day, min(day + pat.length_of_stay, instance.days)):
                for q in schedule._room_day_patients[r][stay_d]:
                    if q not in to_evict_set and instance.patients[q].gender != pat.gender:
                        gender_ok = False
                        break
                if not gender_ok:
                    break
                for occ_idx in instance.occupants_by_room_day[r][stay_d]:
                    if instance.occupants[occ_idx].gender != pat.gender:
                        gender_ok = False
                        break
                if not gender_ok:
                    break
            if not gender_ok:
                continue

            # Theater check
            t_found = -1
            t_cost = 0
            for t, th in enumerate(instance.operating_theaters):
                if theater_load[t][day] + pat.surgery_duration <= th.availability[day]:
                    t_found = t
                    t_cost = 0 if theater_load[t][day] > 0 else w_theater
                    break
            if t_found == -1:
                continue

            delay_cost = float((day - pat.surgery_release_day) * w_delay + t_cost)
            score: tuple[float, float] = (float(len(to_evict)), delay_cost)
            if score < best_score:
                best_score = score
                best_evict = to_evict
                best_slot = (day, r, t_found)

    if best_slot is None:
        return []

    day, r, t = best_slot

    # Save evictee state before unassigning (loads reference admission day / theater)
    evict_info = [(eq, schedule.patient_day[eq], schedule.patient_theater[eq]) for eq in best_evict]
    for eq, eq_day, eq_theater in evict_info:
        schedule.unassign_patient(eq)
        surgeon_load[instance.patients[eq].surgeon][eq_day] -= instance.patients[
            eq
        ].surgery_duration
        theater_load[eq_theater][eq_day] -= instance.patients[eq].surgery_duration

    schedule.assign_patient(p, day, r, t)
    theater_load[t][day] += pat.surgery_duration
    surgeon_load[pat.surgeon][day] += pat.surgery_duration

    return [eq for eq, _, _ in evict_info]


def _clear_nurses(schedule: Schedule, instance: Instance) -> None:
    n_r = len(instance.rooms)
    n_n = len(instance.nurses)
    n_s = instance.total_shifts
    schedule.room_shift_nurse = [[-1] * n_s for _ in range(n_r)]
    schedule.nurse_shift_rooms = [[[] for _ in range(n_s)] for _ in range(n_n)]
