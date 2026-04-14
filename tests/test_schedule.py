"""Verify Schedule cost/violation methods against the C++ validator.

Reference scores are obtained by running:
  ./validator/IHTP_Validator data/instances/testNN.json data/solutions/sol_testNN.json

Run all tests:  uv run pytest
Run this file:  uv run pytest tests/test_schedule.py -v
"""

import json
from pathlib import Path

import pytest

from src.utils.loader import load_instance
from src.utils.schedule import Schedule

# Shared instance fixture reused across all test classes
@pytest.fixture(scope="module")
def instance():
    return load_instance(Path("data/instances/test01.json"))

INSTANCES_DIR = Path("data/instances")
SOLUTIONS_DIR = Path("data/solutions")


def load_schedule(instance_name: str, solution_name: str) -> Schedule:
    inst = load_instance(INSTANCES_DIR / f"{instance_name}.json")
    with open(SOLUTIONS_DIR / f"{solution_name}.json") as f:
        sol = json.load(f)
    return Schedule.from_solution_dict(inst, sol)


@pytest.fixture(scope="module")
def test01() -> Schedule:
    return load_schedule("test01", "sol_test01")


class TestTest01Violations:
    """All hard constraints must be zero for the reference solution."""

    def test_room_gender_mix(self, test01):
        assert test01.room_gender_mix() == 0

    def test_patient_room_compatibility(self, test01):
        assert test01.patient_room_compatibility() == 0

    def test_surgeon_overtime(self, test01):
        assert test01.surgeon_overtime() == 0

    def test_operating_theater_overtime(self, test01):
        assert test01.operating_theater_overtime() == 0

    def test_mandatory_unscheduled(self, test01):
        assert test01.mandatory_unscheduled() == 0

    def test_admission_day_violation(self, test01):
        assert test01.admission_day_violation() == 0

    def test_room_capacity_violation(self, test01):
        assert test01.room_capacity_violation() == 0

    def test_nurse_presence_violation(self, test01):
        assert test01.nurse_presence_violation() == 0

    def test_uncovered_room_violation(self, test01):
        assert test01.uncovered_room_violation() == 0

    def test_total_violations(self, test01):
        assert test01.total_violations() == 0

    def test_is_feasible(self, test01):
        assert test01.is_feasible()


class TestTest01Costs:
    """Individual weighted costs must match C++ validator output exactly."""

    def test_room_age_mix(self, test01):
        assert test01.room_age_mix_cost() == 35       # weight=5, raw=7

    def test_room_skill_level(self, test01):
        assert test01.room_skill_level_cost() == 43   # weight=1, raw=43

    def test_continuity_of_care(self, test01):
        assert test01.continuity_of_care_cost() == 885  # weight=5, raw=177

    def test_excessive_nurse_workload(self, test01):
        assert test01.excessive_nurse_workload_cost() == 24  # weight=1, raw=24

    def test_open_operating_theater(self, test01):
        assert test01.open_operating_theater_cost() == 330  # weight=30, raw=11

    def test_surgeon_transfer(self, test01):
        assert test01.surgeon_transfer_cost() == 0

    def test_patient_delay(self, test01):
        assert test01.patient_delay_cost() == 660    # weight=5, raw=132

    def test_unscheduled_optional(self, test01):
        assert test01.unscheduled_optional_cost() == 1200  # weight=150, raw=8

    def test_total_cost(self, test01):
        assert test01.total_cost() == 3177


class TestMutations:
    """Cover assign/unassign operations and their cache maintenance."""

    def test_unassign_patient_clears_state(self, instance):
        sched = Schedule(instance)
        sched.assign_patient(0, 0, 0, 0)
        assert 0 in sched._room_day_patients[0][0]
        sched.unassign_patient(0)
        assert sched.patient_day[0] == -1
        assert sched.patient_room[0] == -1
        assert sched.patient_theater[0] == -1
        assert 0 not in sched._room_day_patients[0][0]

    def test_unassign_already_unassigned_patient_is_noop(self, instance):
        sched = Schedule(instance)
        sched.unassign_patient(0)  # never assigned — must not raise

    def test_assign_nurse_replaces_previous(self, instance):
        sched = Schedule(instance)
        sched.assign_nurse(0, 0, 0)
        assert sched.room_shift_nurse[0][0] == 0
        sched.assign_nurse(1, 0, 0)  # replaces nurse 0
        assert sched.room_shift_nurse[0][0] == 1
        assert 0 not in sched.nurse_shift_rooms[0][0]
        assert 0 in sched.nurse_shift_rooms[1][0]

    def test_unassign_nurse(self, instance):
        sched = Schedule(instance)
        sched.assign_nurse(0, 0, 0)
        sched.unassign_nurse(0, 0, 0)
        assert sched.room_shift_nurse[0][0] == -1
        assert 0 not in sched.nurse_shift_rooms[0][0]


class TestViolationBranches:
    """Cover violation code-paths not exercised by the zero-violation reference solution."""

    def test_room_capacity_violation_detected(self, instance):
        sched = Schedule(instance)
        cap = instance.rooms[0].capacity
        # Pack capacity+1 patients into room 0 — violation fires on each overlapping day
        for i in range(cap + 1):
            sched.assign_patient(i, 0, 0, 0)
        assert sched.room_capacity_violation() > 0

    def test_nurse_presence_violation_detected(self, instance):
        sched = Schedule(instance)
        nurse = instance.nurses[0]
        non_working = next(
            s for s in range(instance.total_shifts)
            if s not in nurse.shift_indices
        )
        sched.assign_nurse(nurse.idx, non_working, 0)
        assert sched.nurse_presence_violation() == 1

    def test_uncovered_room_violation_detected(self, instance):
        sched = Schedule(instance)
        p = 0
        d = instance.patients[p].surgery_release_day
        sched.assign_patient(p, d, 0, 0)
        # Room 0 has a patient but no nurse → all three shifts on day d are uncovered
        assert sched.uncovered_room_violation() >= instance.shifts_per_day


class TestOccupantSkillDeficit:
    """Cover the occupant branch of room_skill_level_cost (line 250)."""

    def test_occupant_skill_deficit_counted(self, instance):
        # Find an occupant with at least one positive skill requirement
        occ = next(o for o in instance.occupants if any(o.skill_level_required))
        shift_with_req = next(
            s for s, req in enumerate(occ.skill_level_required) if req > 0
        )
        # Assign a nurse with skill_level 0 to the occupant's room in that shift
        sched = Schedule(instance)
        nurse = next(n for n in instance.nurses if n.skill_level == 0)
        sched.assign_nurse(nurse.idx, shift_with_req, occ.room)
        cost = sched.room_skill_level_cost()
        assert cost > 0


class TestBreakdownMethods:
    """cost_breakdown and violation_breakdown must return complete dicts."""

    def test_cost_breakdown_keys(self, test01):
        bd = test01.cost_breakdown()
        assert set(bd.keys()) == {
            "RoomAgeMix", "RoomSkillLevel", "ContinuityOfCare",
            "ExcessiveNurseWorkload", "OpenOperatingTheater",
            "SurgeonTransfer", "PatientDelay", "ElectiveUnscheduledPatients",
        }
        assert sum(bd.values()) == test01.total_cost()

    def test_violation_breakdown_keys(self, test01):
        bd = test01.violation_breakdown()
        assert set(bd.keys()) == {
            "RoomGenderMix", "PatientRoomCompatibility", "SurgeonOvertime",
            "OperatingTheaterOvertime", "MandatoryUnscheduledPatients",
            "AdmissionDay", "RoomCapacity", "NursePresence", "UncoveredRoom",
        }
        assert sum(bd.values()) == 0


class TestRoundTrip:
    """Serialise to dict and reload; costs must be identical."""

    def test_roundtrip_preserves_cost(self, test01):
        inst = test01.instance
        sol_dict = test01.to_solution_dict()
        reloaded = Schedule.from_solution_dict(inst, sol_dict)
        assert reloaded.total_cost() == test01.total_cost()
        assert reloaded.total_violations() == test01.total_violations()
