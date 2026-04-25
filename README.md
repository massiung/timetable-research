# Timetabling Research — IHTC 2024

Research repository for the [Integrated Healthcare Timetabling Competition 2024](https://ihtc2024.github.io/).

## Autoresearch

This repo is an experiment in the spirit of [karpathy/autoresearch](https://github.com/karpathy/autoresearch): rather than a human researcher manually designing and benchmarking algorithms, an AI agent (Claude) drives the research loop — proposing algorithm variants, implementing them on short-lived `exp/*` branches, running them across all 30 competition instances via `/benchmark`, recording scores in `results.tsv`, and deciding what to keep or discard. The human role is to set the objective (minimise IHTC 2024 cost) and review what the agent learns; the agent handles the grind of iterating, scoring, and documenting experiments.

## Problem

IHTC 2024 combines three subproblems: **surgical case planning**, **patient admission scheduling**, and **nurse-to-room assignment**. The objective is to minimise a weighted sum of soft-constraint violations while satisfying all hard constraints. See [`docs/problem_description.md`](docs/problem_description.md) for the full formulation.

## Repository Layout

```
data/
  instances/      # 30 competition instances (i01–i30) + 10 test instances (test01–test10)
  solutions/      # Reference test solutions (sol_test01–sol_test10) + solver output
  validation/     # Validator stdout/stderr logs
docs/             # Problem description, algorithm notes, experiment log
src/
  solvers/        # Algorithm implementations
  utils/          # I/O helpers, constraint checkers
  main.py         # CLI entry point
tests/            # pytest tests
validator/        # Official C++ validator source (IHTP_Validator.cc + json.hpp)
pyproject.toml
```

## Quick Start

### Python

```bash
uv sync
uv run python -m src.main --instance data/instances/test01.json --solver greedy
```

### C++ Validator

```bash
# Direct (recommended)
g++ -O2 -std=c++17 -o validator/IHTP_Validator validator/IHTP_Validator.cc

# Or via CMake
cd validator && cmake -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build

# Validate a solution
./validator/IHTP_Validator data/instances/test01.json data/solutions/sol_test01.json
# Add "verbose" as a third argument for per-constraint breakdown
./validator/IHTP_Validator data/instances/test01.json data/solutions/sol_test01.json verbose
```

### Run tests

```bash
uv run pytest
uv run pytest tests/test_foo.py   # single file
```

## Development

### Pre-commit hooks

Formatting and lint checks run automatically on every `git commit`. After cloning, install the hooks once:

```bash
uv sync
uv run pre-commit install
```

The hooks run `ruff-format` and `ruff --fix` on `src/` and `tests/` before each commit. mypy and pytest are left to CI.

## Docs

| File | Contents |
|------|----------|
| [`docs/problem_description.md`](docs/problem_description.md) | Full problem formulation, JSON formats, all constraints |
| [`docs/algorithms.md`](docs/algorithms.md) | Algorithm exploration log |
| [`docs/experiments.md`](docs/experiments.md) | Scored run results |
