# Algorithm Notes

## Architecture

```
src/utils/model.py      Immutable typed dataclasses for the parsed instance
src/utils/loader.py     load_instance(path) → Instance
src/utils/schedule.py   Mutable Schedule — assignment state + all cost/violation methods
src/solvers/base.py     Abstract base class Solver(ABC)
src/solvers/*.py        Concrete solvers — each subclasses Solver
src/main.py             CLI: load → solve → write JSON
```

### Instance (model.py)

All cross-references use integer indices (same as the C++ validator). String IDs only appear at JSON boundaries. Key lookup tables precomputed by the loader:

| Table | Type | Purpose |
|-------|------|---------|
| `nurses_by_shift` | `list[list[int]]` | Available nurses per global shift |
| `occupants_by_room_day` | `list[list[list[int]]]` | Fixed occupant presence per room-day |
| `patient_idx / nurse_idx / room_idx / …` | `dict[str, int]` | ID → index for JSON parsing |

Global shift index = `day * shifts_per_day + shift_within_day`. Workload/skill arrays on `Patient` are indexed **relative to admission day**; on `Occupant` they are indexed **absolutely** from day 0.

### Schedule (schedule.py)

Mutable state used by all solvers.  Primary state:

| Field | Type | Meaning |
|-------|------|---------|
| `patient_day[p]` | `int` | Admission day, -1 = unscheduled |
| `patient_room[p]` | `int` | Room index, -1 = unscheduled |
| `patient_theater[p]` | `int` | Theater index, -1 = unscheduled |
| `room_shift_nurse[r][s]` | `int` | Nurse covering room r in shift s, -1 = uncovered |
| `nurse_shift_rooms[n][s]` | `list[int]` | Rooms nurse n covers in shift s |
| `_room_day_patients[r][d]` | `list[int]` | Patient indices present (derived, kept in sync) |

All 9 violation methods and 8 weighted cost methods recompute from scratch (O(n)). This is fast enough for construction and validation. For LNS, add incremental delta methods alongside each cost method — do not replace the full recomputation.

### Solver contract (base.py)

```python
class MySolver(Solver):
    def solve(self, instance: Instance, time_limit_seconds: float, seed: int) -> Schedule:
        rng = random.Random(seed)
        deadline = time.monotonic() + time_limit_seconds
        schedule = Schedule(instance)
        # ... build solution ...
        return schedule
```

`solve()` must return before `deadline`. The returned Schedule should have `is_feasible() == True` where possible. `main.py` calls `to_solution_dict()` and writes the JSON.

---

## Approaches

### Greedy Construction
- Build an initial feasible solution by assigning patients and nurses greedily.
- Status: TODO

### Constraint Programming (OR-Tools CP-SAT)
- Model hard constraints as CP clauses; optimise soft penalties with the objective.
- Status: TODO
- Notes: `parameters.num_search_workers = 4`, `parameters.max_time_in_seconds`, `parameters.random_seed`

### Local Search / Large Neighbourhood Search
- Start from a constructed solution; iteratively apply destroy-and-repair operators.
- Status: TODO
- SDU-IMADA (2nd place, open source) uses this approach: https://github.com/Arthod/ihtc2024-imada-submission

---

## Key Design Decisions

_Document trade-offs here as they arise._
