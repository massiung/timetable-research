"""Local search / LNS solver — placeholder."""

import random
import time


class LocalSearchSolver:
    def solve(self, instance: dict, time_limit_seconds: float, seed: int) -> dict:
        rng = random.Random(seed)  # noqa: F841 — seed wired in, ready to use
        deadline = time.monotonic() + time_limit_seconds

        # TODO: implement LNS
        # Stopping pattern to follow:
        #   while time.monotonic() < deadline:
        #       ...destroy and repair...

        _ = deadline  # suppress unused warning until implemented
        return {"patients": [], "nurses": []}
