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


class TestRoundTrip:
    """Serialise to dict and reload; costs must be identical."""

    def test_roundtrip_preserves_cost(self, test01):
        inst = test01.instance
        sol_dict = test01.to_solution_dict()
        reloaded = Schedule.from_solution_dict(inst, sol_dict)
        assert reloaded.total_cost() == test01.total_cost()
        assert reloaded.total_violations() == test01.total_violations()
