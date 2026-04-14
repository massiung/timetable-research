"""Base protocol that every solver must implement."""

from typing import Protocol


class Solver(Protocol):
    def solve(self, instance: dict, time_limit_seconds: float, seed: int) -> dict:
        """Solve the IHTP instance and return a solution dict.

        Args:
            instance: Parsed instance JSON as returned by json.load().
            time_limit_seconds: Wall-clock budget. Must be honoured; target ≤ 580 s
                to leave headroom for I/O before the 600 s competition cutoff.
            seed: Random seed supplied externally. Must be used to initialise all
                random state so that results are reproducible for a given seed.

        Returns:
            Solution dict with keys "patients" and "nurses" matching the
            competition solution JSON format (see docs/problem_description.md).
        """
        ...
