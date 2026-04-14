"""Mutable solution state for the IHTP.

Tracks patient and nurse assignments plus derived data needed to compute
all violations and soft costs.  Cost methods mirror the official C++ validator
(IHTP_Validator.cc v0.0) exactly so results can be cross-checked.

Design notes
------------
* All cost methods recompute from scratch (O(n)).  This is fast enough for
  construction heuristics and validation.  For LNS, add incremental delta
  methods alongside each cost method rather than replacing them.
* room_day_patients is maintained as a cached derived structure so the
  inner loops of cost methods are O(occupancy) rather than O(all patients).
* -1 is used as a sentinel for "unassigned" throughout.
"""

from __future__ import annotations

from .model import Instance


class Schedule:
    def __init__(self, instance: Instance) -> None:
        self.instance = instance
        n_p = len(instance.patients)
        n_n = len(instance.nurses)
        n_r = len(instance.rooms)
        n_s = instance.total_shifts

        # --- primary assignment state ---
        self.patient_day: list[int] = [-1] * n_p
        self.patient_room: list[int] = [-1] * n_p
        self.patient_theater: list[int] = [-1] * n_p

        # room_shift_nurse[r][s] = nurse index covering room r in shift s, or -1
        self.room_shift_nurse: list[list[int]] = [[-1] * n_s for _ in range(n_r)]
        # nurse_shift_rooms[n][s] = rooms nurse n covers in shift s
        self.nurse_shift_rooms: list[list[list[int]]] = [
            [[] for _ in range(n_s)] for _ in range(n_n)
        ]

        # Derived cache: room_day_patients[r][d] = patient indices present
        # Kept in sync by assign/unassign_patient.
        self._room_day_patients: list[list[list[int]]] = [
            [[] for _ in range(instance.days)] for _ in range(n_r)
        ]

    # ------------------------------------------------------------------
    # Assignment operations
    # ------------------------------------------------------------------

    def assign_patient(self, p: int, day: int, room: int, theater: int) -> None:
        self.patient_day[p] = day
        self.patient_room[p] = room
        self.patient_theater[p] = theater
        pat = self.instance.patients[p]
        for d in range(day, min(day + pat.length_of_stay, self.instance.days)):
            self._room_day_patients[room][d].append(p)

    def unassign_patient(self, p: int) -> None:
        day = self.patient_day[p]
        if day == -1:
            return
        room = self.patient_room[p]
        pat = self.instance.patients[p]
        for d in range(day, min(day + pat.length_of_stay, self.instance.days)):
            self._room_day_patients[room][d].remove(p)
        self.patient_day[p] = -1
        self.patient_room[p] = -1
        self.patient_theater[p] = -1

    def assign_nurse(self, nurse: int, shift: int, room: int) -> None:
        """Assign nurse to room in shift, replacing any prior assignment."""
        prev = self.room_shift_nurse[room][shift]
        if prev != -1:
            self.nurse_shift_rooms[prev][shift].remove(room)
        self.room_shift_nurse[room][shift] = nurse
        self.nurse_shift_rooms[nurse][shift].append(room)

    def unassign_nurse(self, nurse: int, shift: int, room: int) -> None:
        self.room_shift_nurse[room][shift] = -1
        self.nurse_shift_rooms[nurse][shift].remove(room)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _room_day_all(self, room: int, day: int) -> tuple[list[int], list[int]]:
        """Return (patient_indices, occupant_indices) present in room on day."""
        return (
            self._room_day_patients[room][day],
            self.instance.occupants_by_room_day[room][day],
        )

    # ------------------------------------------------------------------
    # Hard constraint violations  (must all be 0 for a feasible solution)
    # ------------------------------------------------------------------

    def room_gender_mix(self) -> int:
        """min(#gender_A, #gender_B) per room-day, summed over all room-days."""
        inst = self.instance
        cost = 0
        for r in range(len(inst.rooms)):
            for d in range(inst.days):
                ps, os = self._room_day_all(r, d)
                a = sum(1 for p in ps if inst.patients[p].gender == "A")
                a += sum(1 for o in os if inst.occupants[o].gender == "A")
                b = sum(1 for p in ps if inst.patients[p].gender == "B")
                b += sum(1 for o in os if inst.occupants[o].gender == "B")
                cost += min(a, b)
        return cost

    def patient_room_compatibility(self) -> int:
        inst = self.instance
        return sum(
            1 for p, r in enumerate(self.patient_room)
            if r != -1 and r in inst.patients[p].incompatible_rooms
        )

    def surgeon_overtime(self) -> int:
        inst = self.instance
        load: list[list[int]] = [[0] * inst.days for _ in inst.surgeons]
        for p, d in enumerate(self.patient_day):
            if d != -1:
                load[inst.patients[p].surgeon][d] += inst.patients[p].surgery_duration
        return sum(
            max(0, load[s][d] - surgeon.max_surgery_time[d])
            for s, surgeon in enumerate(inst.surgeons)
            for d in range(inst.days)
        )

    def operating_theater_overtime(self) -> int:
        inst = self.instance
        load: list[list[int]] = [[0] * inst.days for _ in inst.operating_theaters]
        for p, (d, _r, t) in enumerate(zip(self.patient_day, self.patient_room, self.patient_theater)):
            if d != -1:
                load[t][d] += inst.patients[p].surgery_duration
        return sum(
            max(0, load[t][d] - theater.availability[d])
            for t, theater in enumerate(inst.operating_theaters)
            for d in range(inst.days)
        )

    def mandatory_unscheduled(self) -> int:
        return sum(
            1 for p, pat in enumerate(self.instance.patients)
            if pat.mandatory and self.patient_day[p] == -1
        )

    def admission_day_violation(self) -> int:
        inst = self.instance
        return sum(
            1 for p, d in enumerate(self.patient_day)
            if d != -1 and (
                d < inst.patients[p].surgery_release_day
                or d > inst.patients[p].last_possible_day
            )
        )

    def room_capacity_violation(self) -> int:
        inst = self.instance
        cost = 0
        for r, room in enumerate(inst.rooms):
            for d in range(inst.days):
                ps, os = self._room_day_all(r, d)
                excess = len(ps) + len(os) - room.capacity
                if excess > 0:
                    cost += excess
        return cost

    def nurse_presence_violation(self) -> int:
        """Nurses assigned to a room in a shift they are not contracted for."""
        inst = self.instance
        cost = 0
        for r in range(len(inst.rooms)):
            for s in range(inst.total_shifts):
                n = self.room_shift_nurse[r][s]
                if n != -1 and s not in inst.nurses[n].shift_indices:
                    cost += 1
        return cost

    def uncovered_room_violation(self) -> int:
        """Occupied (room, shift) pairs with no nurse assigned."""
        inst = self.instance
        cost = 0
        for r in range(len(inst.rooms)):
            for s in range(inst.total_shifts):
                if self.room_shift_nurse[r][s] == -1:
                    d = s // inst.shifts_per_day
                    ps, os = self._room_day_all(r, d)
                    if ps or os:
                        cost += 1
        return cost

    def total_violations(self) -> int:
        return (
            self.room_gender_mix()
            + self.patient_room_compatibility()
            + self.surgeon_overtime()
            + self.operating_theater_overtime()
            + self.mandatory_unscheduled()
            + self.admission_day_violation()
            + self.room_capacity_violation()
            + self.nurse_presence_violation()
            + self.uncovered_room_violation()
        )

    def is_feasible(self) -> bool:
        return self.total_violations() == 0

    # ------------------------------------------------------------------
    # Soft costs  (weighted; minimise total_cost())
    # ------------------------------------------------------------------

    def room_age_mix_cost(self) -> int:
        """max_age_group - min_age_group per room-day, weighted."""
        inst = self.instance
        raw = 0
        for r in range(len(inst.rooms)):
            for d in range(inst.days):
                ps, os = self._room_day_all(r, d)
                if not ps and not os:
                    continue
                ages = [inst.patients[p].age_group for p in ps]
                ages += [inst.occupants[o].age_group for o in os]
                raw += max(ages) - min(ages)
        return raw * inst.weights.room_mixed_age

    def room_skill_level_cost(self) -> int:
        """Sum of (required_skill - nurse_skill) shortfalls per patient-shift, weighted."""
        inst = self.instance
        spd = inst.shifts_per_day
        raw = 0
        for r in range(len(inst.rooms)):
            for s in range(inst.total_shifts):
                n = self.room_shift_nurse[r][s]
                nurse_skill = inst.nurses[n].skill_level if n != -1 else 0
                d = s // spd
                s_within = s % spd
                ps, os = self._room_day_all(r, d)
                for p in ps:
                    pat = inst.patients[p]
                    s_rel = (d - self.patient_day[p]) * spd + s_within
                    deficit = pat.skill_level_required[s_rel] - nurse_skill
                    if deficit > 0:
                        raw += deficit
                for o in os:
                    deficit = inst.occupants[o].skill_level_required[s] - nurse_skill
                    if deficit > 0:
                        raw += deficit
        return raw * inst.weights.room_nurse_skill

    def continuity_of_care_cost(self) -> int:
        """Total distinct nurses seen per patient/occupant over their stay, weighted."""
        inst = self.instance
        spd = inst.shifts_per_day
        raw = 0
        for p, d in enumerate(self.patient_day):
            if d == -1:
                continue
            r = self.patient_room[p]
            last = min(d + inst.patients[p].length_of_stay, inst.days)
            nurses_seen: set[int] = set()
            for s in range(d * spd, last * spd):
                n = self.room_shift_nurse[r][s]
                if n != -1:
                    nurses_seen.add(n)
            raw += len(nurses_seen)
        for occ in inst.occupants:
            r = occ.room
            nurses_seen = set()
            for s in range(occ.length_of_stay * spd):
                n = self.room_shift_nurse[r][s]
                if n != -1:
                    nurses_seen.add(n)
            raw += len(nurses_seen)
        return raw * inst.weights.continuity_of_care

    def excessive_nurse_workload_cost(self) -> int:
        """Total workload excess above max_load per nurse-shift, weighted."""
        inst = self.instance
        spd = inst.shifts_per_day
        raw = 0
        for nurse in inst.nurses:
            for ws in nurse.working_shifts:
                s = ws.global_shift
                d = ws.day
                s_within = s % spd
                load = 0
                for r in self.nurse_shift_rooms[nurse.idx][s]:
                    ps, os = self._room_day_all(r, d)
                    for p in ps:
                        s_rel = (d - self.patient_day[p]) * spd + s_within
                        load += inst.patients[p].workload_produced[s_rel]
                    for o in os:
                        load += inst.occupants[o].workload_produced[s]
                excess = load - ws.max_load
                if excess > 0:
                    raw += excess
        return raw * inst.weights.nurse_excessive_workload

    def open_operating_theater_cost(self) -> int:
        """Number of (theater, day) pairs where the theater is used, weighted."""
        inst = self.instance
        used: list[list[bool]] = [[False] * inst.days for _ in inst.operating_theaters]
        for p, (d, _r, t) in enumerate(zip(self.patient_day, self.patient_room, self.patient_theater)):
            if d != -1:
                used[t][d] = True
        raw = sum(v for row in used for v in row)
        return raw * inst.weights.open_operating_theater

    def surgeon_transfer_cost(self) -> int:
        """(distinct_theaters - 1) per surgeon per day when > 1, weighted."""
        inst = self.instance
        seen: list[list[set[int]]] = [
            [set() for _ in range(inst.days)] for _ in inst.surgeons
        ]
        for p, (d, _r, t) in enumerate(zip(self.patient_day, self.patient_room, self.patient_theater)):
            if d != -1:
                seen[inst.patients[p].surgeon][d].add(t)
        raw = sum(
            max(0, len(seen[s][d]) - 1)
            for s in range(len(inst.surgeons))
            for d in range(inst.days)
        )
        return raw * inst.weights.surgeon_transfer

    def patient_delay_cost(self) -> int:
        """Days each patient is admitted after their release day, weighted."""
        inst = self.instance
        raw = sum(
            max(0, d - inst.patients[p].surgery_release_day)
            for p, d in enumerate(self.patient_day)
            if d != -1
        )
        return raw * inst.weights.patient_delay

    def unscheduled_optional_cost(self) -> int:
        """Count of optional patients not admitted, weighted."""
        inst = self.instance
        raw = sum(
            1 for p, pat in enumerate(inst.patients)
            if not pat.mandatory and self.patient_day[p] == -1
        )
        return raw * inst.weights.unscheduled_optional

    def total_cost(self) -> int:
        return (
            self.room_age_mix_cost()
            + self.room_skill_level_cost()
            + self.continuity_of_care_cost()
            + self.excessive_nurse_workload_cost()
            + self.open_operating_theater_cost()
            + self.surgeon_transfer_cost()
            + self.patient_delay_cost()
            + self.unscheduled_optional_cost()
        )

    def cost_breakdown(self) -> dict[str, int]:
        """Return all cost components as a dict, matching validator output order."""
        return {
            "RoomAgeMix": self.room_age_mix_cost(),
            "RoomSkillLevel": self.room_skill_level_cost(),
            "ContinuityOfCare": self.continuity_of_care_cost(),
            "ExcessiveNurseWorkload": self.excessive_nurse_workload_cost(),
            "OpenOperatingTheater": self.open_operating_theater_cost(),
            "SurgeonTransfer": self.surgeon_transfer_cost(),
            "PatientDelay": self.patient_delay_cost(),
            "ElectiveUnscheduledPatients": self.unscheduled_optional_cost(),
        }

    def violation_breakdown(self) -> dict[str, int]:
        return {
            "RoomGenderMix": self.room_gender_mix(),
            "PatientRoomCompatibility": self.patient_room_compatibility(),
            "SurgeonOvertime": self.surgeon_overtime(),
            "OperatingTheaterOvertime": self.operating_theater_overtime(),
            "MandatoryUnscheduledPatients": self.mandatory_unscheduled(),
            "AdmissionDay": self.admission_day_violation(),
            "RoomCapacity": self.room_capacity_violation(),
            "NursePresence": self.nurse_presence_violation(),
            "UncoveredRoom": self.uncovered_room_violation(),
        }

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_solution_dict(self) -> dict:
        inst = self.instance
        patients_out = []
        for p, pat in enumerate(inst.patients):
            d = self.patient_day[p]
            if d == -1:
                patients_out.append({"id": pat.id, "admission_day": "none"})
            else:
                patients_out.append({
                    "id": pat.id,
                    "admission_day": d,
                    "room": inst.rooms[self.patient_room[p]].id,
                    "operating_theater": inst.operating_theaters[self.patient_theater[p]].id,
                })
        nurses_out = []
        for n, nurse in enumerate(inst.nurses):
            assignments = []
            for ws in nurse.working_shifts:
                s = ws.global_shift
                rooms = self.nurse_shift_rooms[n][s]
                assignments.append({
                    "day": ws.day,
                    "shift": inst.shift_names[ws.shift_within_day],
                    "rooms": [inst.rooms[r].id for r in rooms],
                })
            if assignments:
                nurses_out.append({"id": nurse.id, "assignments": assignments})
        return {"patients": patients_out, "nurses": nurses_out}

    @classmethod
    def from_solution_dict(cls, instance: Instance, data: dict) -> Schedule:
        schedule = cls(instance)
        for entry in data.get("patients", []):
            if entry.get("admission_day") == "none":
                continue
            p = instance.patient_idx[entry["id"]]
            d = int(entry["admission_day"])
            r = instance.room_idx[entry["room"]]
            t = instance.theater_idx[entry["operating_theater"]]
            schedule.assign_patient(p, d, r, t)
        for entry in data.get("nurses", []):
            n = instance.nurse_idx[entry["id"]]
            for assignment in entry.get("assignments", []):
                day = int(assignment["day"])
                s_within = instance.shift_idx[assignment["shift"]]
                s = day * instance.shifts_per_day + s_within
                for room_id in assignment.get("rooms", []):
                    r = instance.room_idx[room_id]
                    schedule.assign_nurse(n, s, r)
        return schedule
