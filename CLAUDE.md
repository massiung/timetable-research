# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

Research repo for the [Integrated Healthcare Timetabling Competition 2024 (IHTC 2024)](https://ihtc2024.github.io/). The goal is to develop and compare algorithms (greedy, CP-SAT, local search) that jointly solve surgical case planning, patient admission scheduling, and nurse-to-room assignment — then score solutions with the official C++ validator.

The competition is over (results published June 2025); the repo is for ongoing research and algorithm exploration.

## Commands

### Python

```bash
uv sync                              # install / sync dependencies
uv run python -m src.main --instance data/instances/test01.json --solver greedy
uv run pytest                        # all tests
uv run pytest tests/test_foo.py      # single file
uv run ruff check src tests          # lint
uv run ruff format src tests         # format
```

### C++ Validator

```bash
# One-shot build (preferred — no CMake needed, json.hpp is already in validator/)
g++ -O2 -std=c++17 -o validator/IHTP_Validator validator/IHTP_Validator.cc

# Validate a solution (outputs violations + weighted costs)
./validator/IHTP_Validator data/instances/test01.json data/solutions/sol_test01.json
# With per-constraint detail:
./validator/IHTP_Validator data/instances/test01.json data/solutions/sol_test01.json verbose
```

Validator output: first prints 9 hard-constraint **violation** counts (all must be 0 for feasibility), then 8 **soft costs** (each = weight × raw count) and a total. Lower total cost is better.

Reference score for test01 reference solution: **3177** (0 violations).

## Runtime Constraints

These are hard limits imposed by the competition evaluation and must be respected by every solver:

| Constraint | Value |
|------------|-------|
| Wall-clock time per instance | **10 minutes (600 s)** |
| Maximum threads | **4** |
| Evaluation runs (finalist phase) | **10 independent trials with random seeds** |
| CPU | AMD Ryzen Threadripper PRO 3975WX, 3.50 GHz |
| RAM | 64 GB |
| OS | Ubuntu Linux 22.4 |

Scoring in the finalist phase: ranks are computed per trial and averaged across all trials and instances; lowest mean rank wins. This means **consistent quality across random seeds matters more than occasional best scores**.

**Practical implications for solver code:**

- Every solver must accept `time_limit_seconds` and `seed` parameters and enforce them internally. Target **≤ 580 s** to leave headroom for I/O and solution writing.
- OR-Tools CP-SAT: set `parameters.max_time_in_seconds = time_limit` and `parameters.num_search_workers = 4`.
- Local search / LNS: use `time.monotonic()` for the stopping criterion, never iteration counts alone.
- Solvers must accept an external random seed and use it consistently — the 10 trials each use a different seed supplied by the organisers. A solver that ignores the seed and always does the same thing will still be evaluated correctly, but one that crashes or degrades on certain seeds will be penalised.
- Ensure the solver runs correctly on **Linux** (Ubuntu 22.4). Avoid macOS-only dependencies.
- Do not benchmark with a wall-clock budget shorter than 600 s — the results won't be comparable to competition scores.

## Architecture

```
src/main.py          — CLI entry point; parses args, loads instance JSON, dispatches solver
src/solvers/         — one module per algorithm; each exposes solve(instance: dict) -> dict
src/utils/           — shared I/O, constraint helpers, experiment runners
tests/               — pytest tests mirroring src/ structure
data/instances/      — 30 competition (i01–i30) + 10 test (test01–test10) instance JSONs
data/solutions/      — reference solutions (sol_test01–10) + solver output
data/validation/     — validator output logs
docs/                — problem_description.md, algorithms.md, experiments.md
validator/           — IHTP_Validator.cc (official source) + json.hpp (nlohmann, header-only)
```

Each solver module returns a dict with keys `"patients"` and `"nurses"` matching the solution JSON format documented in `docs/problem_description.md`.

## Data Model (key facts from validator source)

- **Shifts** are indexed globally as `day * shifts_per_day + shift_index` (shifts_per_day = 3 for early/late/night).
- `workload_produced` and `skill_level_required` arrays on patients/occupants are indexed **relative to admission day** (index 0 = first shift of admission day). On occupants they are indexed absolutely from day 0.
- A nurse can be assigned to **multiple rooms** per shift; `nurse_shift_load` accumulates workload across all assigned rooms.
- `RoomGenderMix` is a **hard constraint** (any mixed-gender room-day is a violation), not just soft cost.
- `ContinuityOfCare` counts the **total** number of distinct nurses across all patients+occupants, not a max.
- `surgeon_due_day` is only present in the JSON for mandatory patients.

## Reference Implementation

The 2nd-place team (SDU-IMADA, University of Southern Denmark) published their full submission as open source — the only finalist to do so. It is the primary reference for algorithm ideas:

**https://github.com/Arthod/ihtc2024-imada-submission**

Their approach uses local search / large neighbourhood search. Study this before designing new solvers.

## Scoring Workflow

Use `/score` to run the validator on any instance/solution pair and automatically record the result in `docs/experiments.md`. The skill handles building the validator if missing, parsing output, and appending the row.

## Docs Maintenance

- `docs/problem_description.md` — update if problem spec changes.
- `docs/algorithms.md` — log every approach explored (including failures).
- `docs/experiments.md` — record every scored run: instance, solver, config, score, notes.
