"""Run a solver across all 30 non-test instances and print a TSV summary."""

import argparse
import subprocess
import sys
from pathlib import Path

INSTANCES = [f"i{i:02d}" for i in range(1, 31)]
REPO = Path(__file__).parent.parent


def run_solver(instance: str, solver: str, time_limit: float) -> tuple[float, int]:
    """Return (elapsed_s, exit_code)."""
    out_path = REPO / "data" / "solutions" / f"{instance}_solution.json"
    result = subprocess.run(
        [
            sys.executable, "-m", "src.main",
            "--instance", str(REPO / "data" / "instances" / f"{instance}.json"),
            "--solver", solver,
            "--output", str(out_path),
            "--time-limit", str(time_limit),
        ],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    elapsed = 0.0
    for line in result.stdout.splitlines():
        if line.startswith("elapsed_s:"):
            elapsed = float(line.split(":")[1].strip())
    return elapsed, result.returncode


def run_validator(instance: str) -> tuple[int, int]:
    """Return (violations, cost). Returns (-1, -1) on validator error."""
    validator = REPO / "validator" / "IHTP_Validator"
    instance_path = REPO / "data" / "instances" / f"{instance}.json"
    solution_path = REPO / "data" / "solutions" / f"{instance}_solution.json"
    result = subprocess.run(
        [str(validator), str(instance_path), str(solution_path)],
        capture_output=True,
        text=True,
    )
    violations, cost = -1, -1
    for line in result.stdout.splitlines():
        if line.startswith("Total violations ="):
            violations = int(line.split("=")[1].strip())
        elif line.startswith("Total cost ="):
            cost = int(line.split("=")[1].strip())
    return violations, cost


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark solver on i01–i30")
    parser.add_argument("--solver", default="greedy", choices=["greedy", "cp", "local_search"])
    parser.add_argument("--time-limit", type=float, default=60.0, metavar="SECONDS")
    args = parser.parse_args()

    # Ensure validator exists
    validator = REPO / "validator" / "IHTP_Validator"
    if not validator.exists():
        print("Building validator…", file=sys.stderr)
        subprocess.run(
            ["g++", "-O2", "-std=c++17", "-o", str(validator),
             str(REPO / "validator" / "IHTP_Validator.cc")],
            check=True,
        )

    print(f"instance\tcost\tviolations\telapsed_s\tstatus", flush=True)

    feasible_costs: list[int] = []
    all_times: list[float] = []

    for instance in INSTANCES:
        elapsed, exit_code = run_solver(instance, args.solver, args.time_limit)
        if exit_code != 0:
            print(f"{instance}\t—\t—\t{elapsed:.2f}\tcrash", flush=True)
            continue

        violations, cost = run_validator(instance)
        status = "ok" if violations == 0 else "infeasible"
        print(f"{instance}\t{cost}\t{violations}\t{elapsed:.2f}\t{status}", flush=True)

        all_times.append(elapsed)
        if violations == 0:
            feasible_costs.append(cost)

    avg_cost = sum(feasible_costs) / len(feasible_costs) if feasible_costs else float("nan")
    avg_time = sum(all_times) / len(all_times) if all_times else float("nan")
    n_feasible = len(feasible_costs)
    print(
        f"\nsummary\tavg_cost={avg_cost:.1f}\tn_feasible={n_feasible}/30\tavg_time_s={avg_time:.2f}",
        flush=True,
    )


if __name__ == "__main__":
    main()
