"""Entry point for running solvers on ITC 2024 instances."""

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ITC 2024 solver runner")
    parser.add_argument("--instance", type=Path, required=True, help="Path to instance JSON")
    parser.add_argument(
        "--solver",
        choices=["greedy", "cp", "local_search"],
        default="greedy",
        help="Solver to use",
    )
    parser.add_argument("--output", type=Path, default=None, help="Output solution path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    with open(args.instance) as f:
        instance = json.load(f)

    output_path = args.output or Path("data/solutions") / (args.instance.stem + "_solution.json")

    # TODO: dispatch to the chosen solver
    print(f"Instance: {args.instance.name}")
    print(f"Solver:   {args.solver}")
    print(f"Output:   {output_path}")


if __name__ == "__main__":
    main()
