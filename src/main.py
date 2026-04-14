"""Entry point for running solvers on IHTC 2024 instances."""

import argparse
import json
import sys
import time
from pathlib import Path

DEFAULT_TIME_LIMIT = 580.0  # seconds — leaves headroom before the 600 s competition cutoff
DEFAULT_SEED = 42


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="IHTC 2024 solver runner")
    parser.add_argument("--instance", type=Path, required=True, help="Path to instance JSON")
    parser.add_argument(
        "--solver",
        choices=["greedy", "cp", "local_search"],
        default="greedy",
        help="Solver to use",
    )
    parser.add_argument("--output", type=Path, default=None, help="Output solution path")
    parser.add_argument(
        "--time-limit",
        type=float,
        default=DEFAULT_TIME_LIMIT,
        metavar="SECONDS",
        help=f"Wall-clock time budget in seconds (default: {DEFAULT_TIME_LIMIT})",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help=f"Random seed (default: {DEFAULT_SEED})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    with open(args.instance) as f:
        instance = json.load(f)

    output_path = args.output or Path("data/solutions") / (args.instance.stem + "_solution.json")

    print(f"Instance:   {args.instance.name}")
    print(f"Solver:     {args.solver}")
    print(f"Time limit: {args.time_limit} s")
    print(f"Seed:       {args.seed}")
    print(f"Output:     {output_path}")

    start = time.monotonic()

    if args.solver == "greedy":
        from src.solvers.greedy import GreedySolver
        solver = GreedySolver()
    elif args.solver == "cp":
        from src.solvers.cp import CPSolver
        solver = CPSolver()
    elif args.solver == "local_search":
        from src.solvers.local_search import LocalSearchSolver
        solver = LocalSearchSolver()
    else:
        print(f"Unknown solver: {args.solver}", file=sys.stderr)
        sys.exit(1)

    solution = solver.solve(instance, time_limit_seconds=args.time_limit, seed=args.seed)

    elapsed = time.monotonic() - start
    print(f"Solved in {elapsed:.1f} s")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(solution, f, indent=2)
    print(f"Solution written to {output_path}")


if __name__ == "__main__":
    main()
