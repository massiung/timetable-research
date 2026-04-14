"""CP-SAT solver — placeholder."""

from src.solvers.base import Solver
from src.utils.model import Instance
from src.utils.schedule import Schedule


class CPSolver(Solver):
    def solve(self, instance: Instance, time_limit_seconds: float, seed: int) -> Schedule:
        # TODO: implement CP-SAT model
        # Required OR-Tools parameters:
        #   parameters.max_time_in_seconds = time_limit_seconds
        #   parameters.num_search_workers = 4   # competition maximum
        #   parameters.random_seed = seed
        return Schedule(instance)
