"""Tests for solver base class and concrete solver stubs."""

from pathlib import Path

import pytest

from src.solvers.base import Solver
from src.solvers.cp import CPSolver
from src.solvers.greedy import GreedySolver
from src.solvers.local_search import LocalSearchSolver
from src.utils.loader import load_instance
from src.utils.schedule import Schedule


@pytest.fixture(scope="module")
def instance():
    return load_instance(Path("data/instances/test01.json"))


class TestSolverABC:
    def test_cannot_instantiate_abstract_solver(self):
        with pytest.raises(TypeError):
            Solver()  # type: ignore[abstract]

    def test_greedy_is_solver_subclass(self):
        assert issubclass(GreedySolver, Solver)

    def test_cp_is_solver_subclass(self):
        assert issubclass(CPSolver, Solver)

    def test_local_search_is_solver_subclass(self):
        assert issubclass(LocalSearchSolver, Solver)


class TestSolverStubs:
    """Each stub must accept the required arguments and return a Schedule."""

    def test_greedy_returns_schedule(self, instance):
        result = GreedySolver().solve(instance, time_limit_seconds=1.0, seed=0)
        assert isinstance(result, Schedule)

    def test_cp_returns_schedule(self, instance):
        result = CPSolver().solve(instance, time_limit_seconds=1.0, seed=0)
        assert isinstance(result, Schedule)

    def test_local_search_returns_schedule(self, instance):
        result = LocalSearchSolver().solve(instance, time_limit_seconds=1.0, seed=0)
        assert isinstance(result, Schedule)

    def test_different_seeds_accepted(self, instance):
        s1 = GreedySolver().solve(instance, time_limit_seconds=1.0, seed=1)
        s2 = GreedySolver().solve(instance, time_limit_seconds=1.0, seed=99)
        assert isinstance(s1, Schedule)
        assert isinstance(s2, Schedule)
