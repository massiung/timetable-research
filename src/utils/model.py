"""Immutable, typed representation of an IHTP instance.

All cross-references use integer indices into the corresponding lists on
Instance, matching the validator's internal representation.  String IDs are
only used at JSON I/O boundaries (loader / schedule).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Weights:
    room_mixed_age: int
    room_nurse_skill: int
    continuity_of_care: int
    nurse_excessive_workload: int
    open_operating_theater: int
    surgeon_transfer: int
    patient_delay: int
    unscheduled_optional: int


@dataclass
class Occupant:
    """Pre-admitted patient with a fixed room assignment."""

    idx: int
    id: str
    gender: str  # "A" or "B"
    age_group: int  # index into Instance.age_groups
    length_of_stay: int  # days, starting from day 0
    # Both arrays have length  length_of_stay * shifts_per_day.
    # Index = absolute global shift (day * spd + shift_within_day).
    workload_produced: list[int]
    skill_level_required: list[int]
    room: int  # Room.idx — fixed, never changes


@dataclass
class Patient:
    """Patient who must be scheduled (surgery + room + nurse)."""

    idx: int
    id: str
    mandatory: bool
    gender: str  # "A" or "B"
    age_group: int
    length_of_stay: int
    surgery_release_day: int  # earliest admission day (inclusive)
    surgery_due_day: int  # latest for mandatory patients; -1 for optional
    last_possible_day: int  # precomputed: surgery_due_day or Instance.days - 1
    surgery_duration: int  # minutes
    surgeon: int  # Surgeon.idx
    incompatible_rooms: frozenset[int]
    # Both arrays have length  length_of_stay * shifts_per_day.
    # Index = (day_relative_to_admission * spd + shift_within_day).
    workload_produced: list[int]
    skill_level_required: list[int]


@dataclass
class Surgeon:
    idx: int
    id: str
    max_surgery_time: list[int]  # minutes per day; 0 = unavailable


@dataclass
class OperatingTheater:
    idx: int
    id: str
    availability: list[int]  # minutes per day


@dataclass
class Room:
    idx: int
    id: str
    capacity: int


@dataclass
class WorkingShift:
    """One scheduled shift entry for a nurse."""

    global_shift: int  # day * shifts_per_day + shift_within_day
    day: int
    shift_within_day: int  # index into Instance.shift_names
    max_load: int


@dataclass
class Nurse:
    idx: int
    id: str
    skill_level: int
    working_shifts: list[WorkingShift]
    shift_indices: frozenset[int]  # O(1) availability lookup
    max_load_by_shift: dict[int, int]  # global_shift → max_load


@dataclass
class Instance:
    days: int
    shifts_per_day: int
    total_shifts: int  # days * shifts_per_day (convenience)
    age_groups: list[str]  # e.g. ["infant", "adult", "elderly"]
    shift_names: list[str]  # e.g. ["early", "late", "night"]
    weights: Weights
    occupants: list[Occupant]
    patients: list[Patient]
    surgeons: list[Surgeon]
    operating_theaters: list[OperatingTheater]
    rooms: list[Room]
    nurses: list[Nurse]
    # --- precomputed lookup tables (built once by loader) ---
    nurses_by_shift: list[list[int]]  # global_shift → [Nurse.idx]
    occupants_by_room_day: list[list[list[int]]]  # room → day → [Occupant.idx]
    # reverse id → idx maps
    patient_idx: dict[str, int]
    nurse_idx: dict[str, int]
    room_idx: dict[str, int]
    theater_idx: dict[str, int]
    surgeon_idx: dict[str, int]
    shift_idx: dict[str, int]  # shift name → index within day
    age_group_idx: dict[str, int]
