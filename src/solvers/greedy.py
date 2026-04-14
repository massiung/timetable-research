"""Greedy construction heuristic — placeholder."""

import random

from src.solvers.base import Solver
from src.utils.model import Instance
from src.utils.schedule import Schedule


class GreedySolver(Solver):
    def solve(self, instance: Instance, time_limit_seconds: float, seed: int) -> Schedule:
        rng = random.Random(seed)  # noqa: F841
        # TODO: implement greedy construction
        return Schedule(instance)
