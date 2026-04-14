"""Greedy construction heuristic — placeholder."""

import random


class GreedySolver:
    def solve(self, instance: dict, time_limit_seconds: float, seed: int) -> dict:
        rng = random.Random(seed)  # noqa: F841 — seed wired in, ready to use
        # TODO: implement greedy construction
        return {"patients": [], "nurses": []}
