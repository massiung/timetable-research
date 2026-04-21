"""Entry point for running solvers on IHTC 2024 instances."""

import argparse
import json
import logging
import sys
import time
from pathlib import Path

from src.utils import load_instance

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
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level for solver internals (default: WARNING)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(name)s %(levelname)s %(message)s",
        stream=sys.stderr,
    )

    instance = load_instance(args.instance)
    output_path = args.output or Path("data/solutions") / (args.instance.stem + "_solution.json")

    print(
        f"Instance:   {args.instance.name}  "
        f"({len(instance.patients)} patients, {len(instance.nurses)} nurses, "
        f"{instance.days} days)"
    )
    print(f"Solver:     {args.solver}")
    print(f"Time limit: {args.time_limit} s")
    print(f"Seed:       {args.seed}")
    print(f"Output:     {output_path}")

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

    print("Solving…")
    start = time.monotonic()
    schedule = solver.solve(instance, time_limit_seconds=args.time_limit, seed=args.seed)
    elapsed = time.monotonic() - start

    violations = schedule.total_violations()
    cost = schedule.total_cost()
    feasible_tag = "FEASIBLE" if violations == 0 else "INFEASIBLE"
    print(f"Solved in {elapsed:.1f} s  |  violations={violations}  cost={cost}  [{feasible_tag}]")
    print(f"elapsed_s: {elapsed:.2f}")

    if violations > 0:
        print("\nWARNING: solution has hard-constraint violations and cannot be submitted.")
        print("Violation breakdown:")
        for name, count in schedule.violation_breakdown().items():
            if count:
                print(f"  {name}: {count}")
    else:
        print("Cost breakdown:")
        for name, val in schedule.cost_breakdown().items():
            if val:
                print(f"  {name}: {val}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(schedule.to_solution_dict(), f, indent=2)
    print(f"\nSolution written to {output_path}")


if __name__ == "__main__":
    main()
