---
name: score
description: Use this skill when the user asks to score, validate, or benchmark a solution — e.g. "/score", "score this solution", "run the validator on i05", "what's the cost for my greedy output", "record these results". Runs the IHTP validator and appends a row to docs/experiments.md.
version: 1.0.0
---

# Score a Solution

Run the IHTP validator on an instance/solution pair and record the result in `docs/experiments.md`.

## Steps

1. **Identify the instance and solution files** from the user's arguments or context:
   - Instance: `data/instances/<name>.json`  (e.g. `test01`, `i05`)
   - Solution: `data/solutions/<name_solution>.json` — infer from context; ask if ambiguous.

2. **Ensure the validator binary exists.** If `validator/IHTP_Validator` is missing, build it first:
   ```bash
   g++ -O2 -std=c++17 -o validator/IHTP_Validator validator/IHTP_Validator.cc
   ```

3. **Run the validator:**
   ```bash
   ./validator/IHTP_Validator data/instances/<instance>.json data/solutions/<solution>.json
   ```
   Capture full stdout. Optionally run with `verbose` as a third argument to show per-constraint detail.

4. **Parse the output:**
   - Extract `Total violations` — if > 0, the solution is **infeasible**; note which constraints fire.
   - Extract each weighted cost line and `Total cost`.

5. **Append a row to `docs/experiments.md`** using today's date (YYYY-MM-DD), the instance name, solver name (from context or user), config if known, and total score. Use `-` for infeasible. Example row:
   ```
   | 2026-04-14 | test01 | greedy | default | 3177 | 0 violations |
   ```

6. **Report back** to the user: total violations, total cost, and whether the result was recorded.

## Notes

- The validator prints violations first (9 rows), then weighted costs (8 rows).
- A feasible solution has `Total violations = 0`.
- Lower total cost is better among feasible solutions.
- Reference score for `test01` reference solution: **3177** (0 violations).
- If the user only says `/score` with no args, ask for the instance and solution file names.
