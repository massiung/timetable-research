"""Parse an IHTP instance JSON file into a typed Instance object."""

from __future__ import annotations

import json
from pathlib import Path

from .model import (
    Instance,
    Nurse,
    Occupant,
    OperatingTheater,
    Patient,
    Room,
    Surgeon,
    Weights,
    WorkingShift,
)


def load_instance(path: Path | str) -> Instance:
    with open(path) as f:
        data = json.load(f)

    days: int = data["days"]
    shift_names: list[str] = data["shift_types"]
    shifts_per_day: int = len(shift_names)
    total_shifts: int = days * shifts_per_day
    age_groups: list[str] = data["age_groups"]

    shift_idx: dict[str, int] = {name: i for i, name in enumerate(shift_names)}
    age_group_idx: dict[str, int] = {name: i for i, name in enumerate(age_groups)}

    w = data["weights"]
    weights = Weights(
        room_mixed_age=w["room_mixed_age"],
        room_nurse_skill=w["room_nurse_skill"],
        continuity_of_care=w["continuity_of_care"],
        nurse_excessive_workload=w["nurse_eccessive_workload"],  # typo is in spec
        open_operating_theater=w["open_operating_theater"],
        surgeon_transfer=w["surgeon_transfer"],
        patient_delay=w["patient_delay"],
        unscheduled_optional=w["unscheduled_optional"],
    )

    # Rooms must be parsed before patients (needed for incompatible_rooms lookup)
    rooms: list[Room] = []
    room_idx: dict[str, int] = {}
    for i, r in enumerate(data["rooms"]):
        rooms.append(Room(idx=i, id=r["id"], capacity=r["capacity"]))
        room_idx[r["id"]] = i

    surgeons: list[Surgeon] = []
    surgeon_idx: dict[str, int] = {}
    for i, s in enumerate(data["surgeons"]):
        surgeons.append(Surgeon(idx=i, id=s["id"], max_surgery_time=list(s["max_surgery_time"])))
        surgeon_idx[s["id"]] = i

    operating_theaters: list[OperatingTheater] = []
    theater_idx: dict[str, int] = {}
    for i, ot in enumerate(data["operating_theaters"]):
        operating_theaters.append(
            OperatingTheater(idx=i, id=ot["id"], availability=list(ot["availability"]))
        )
        theater_idx[ot["id"]] = i

    occupants: list[Occupant] = []
    for i, o in enumerate(data["occupants"]):
        occupants.append(
            Occupant(
                idx=i,
                id=o["id"],
                gender=o["gender"],
                age_group=age_group_idx[o["age_group"]],
                length_of_stay=o["length_of_stay"],
                workload_produced=list(o["workload_produced"]),
                skill_level_required=list(o["skill_level_required"]),
                room=room_idx[o["room_id"]],
            )
        )

    patients: list[Patient] = []
    patient_idx: dict[str, int] = {}
    for i, p in enumerate(data["patients"]):
        mandatory = bool(p["mandatory"])
        due = p["surgery_due_day"] if mandatory else -1
        patients.append(
            Patient(
                idx=i,
                id=p["id"],
                mandatory=mandatory,
                gender=p["gender"],
                age_group=age_group_idx[p["age_group"]],
                length_of_stay=p["length_of_stay"],
                surgery_release_day=p["surgery_release_day"],
                surgery_due_day=due,
                last_possible_day=due if mandatory else days - 1,
                surgery_duration=p["surgery_duration"],
                surgeon=surgeon_idx[p["surgeon_id"]],
                incompatible_rooms=frozenset(
                    room_idx[r] for r in (p["incompatible_room_ids"] or [])
                ),
                workload_produced=list(p["workload_produced"]),
                skill_level_required=list(p["skill_level_required"]),
            )
        )
        patient_idx[p["id"]] = i

    nurses: list[Nurse] = []
    nurse_idx: dict[str, int] = {}
    nurses_by_shift: list[list[int]] = [[] for _ in range(total_shifts)]
    for i, n in enumerate(data["nurses"]):
        working_shifts: list[WorkingShift] = []
        shift_indices_set: set[int] = set()
        max_load_by_shift: dict[int, int] = {}
        for ws in n["working_shifts"]:
            day = int(ws["day"])
            s_within = shift_idx[ws["shift"]]
            global_s = day * shifts_per_day + s_within
            working_shifts.append(
                WorkingShift(
                    global_shift=global_s,
                    day=day,
                    shift_within_day=s_within,
                    max_load=ws["max_load"],
                )
            )
            shift_indices_set.add(global_s)
            max_load_by_shift[global_s] = ws["max_load"]
            nurses_by_shift[global_s].append(i)
        nurses.append(
            Nurse(
                idx=i,
                id=n["id"],
                skill_level=n["skill_level"],
                working_shifts=working_shifts,
                shift_indices=frozenset(shift_indices_set),
                max_load_by_shift=max_load_by_shift,
            )
        )
        nurse_idx[n["id"]] = i

    # Precompute occupant presence per room per day
    occupants_by_room_day: list[list[list[int]]] = [
        [[] for _ in range(days)] for _ in range(len(rooms))
    ]
    for o in occupants:
        for d in range(o.length_of_stay):
            occupants_by_room_day[o.room][d].append(o.idx)

    return Instance(
        days=days,
        shifts_per_day=shifts_per_day,
        total_shifts=total_shifts,
        age_groups=age_groups,
        shift_names=shift_names,
        weights=weights,
        occupants=occupants,
        patients=patients,
        surgeons=surgeons,
        operating_theaters=operating_theaters,
        rooms=rooms,
        nurses=nurses,
        nurses_by_shift=nurses_by_shift,
        occupants_by_room_day=occupants_by_room_day,
        patient_idx=patient_idx,
        nurse_idx=nurse_idx,
        room_idx=room_idx,
        theater_idx=theater_idx,
        surgeon_idx=surgeon_idx,
        shift_idx=shift_idx,
        age_group_idx=age_group_idx,
    )
