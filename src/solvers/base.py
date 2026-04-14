"""Abstract base class for all IHTP solvers."""

from abc import ABC, abstractmethod

from src.utils.model import Instance
from src.utils.schedule import Schedule


class Solver(ABC):
    @abstractmethod
    def solve(self, instance: Instance, time_limit_seconds: float, seed: int) -> Schedule:
        """Solve the instance and return a Schedule.

        Args:
            instance: Parsed instance (use load_instance() to obtain).
            time_limit_seconds: Wall-clock budget.  Must be honoured; target
                ≤ 580 s to leave headroom before the 600 s competition cutoff.
            seed: Random seed supplied externally.  Must initialise all random
                state so results are reproducible for a given seed.

        Returns:
            A Schedule with is_feasible() == True where possible.
        """
