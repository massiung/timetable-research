"""Local search / LNS solver — placeholder."""

import random
import time

from src.solvers.base import Solver
from src.utils.model import Instance
from src.utils.schedule import Schedule


class LocalSearchSolver(Solver):
    def solve(self, instance: Instance, time_limit_seconds: float, seed: int) -> Schedule:
        rng = random.Random(seed)  # noqa: F841
        deadline = time.monotonic() + time_limit_seconds

        # TODO: implement LNS
        # Stopping pattern:
        #   while time.monotonic() < deadline:
        #       ...destroy and repair...

        _ = deadline  # suppress unused warning until implemented
        return Schedule(instance)
