---
name: score
description: Use this skill when the user asks to score, validate, or benchmark a solution — e.g. "/score", "score this solution", "run the validator on i05", "what's the cost for my greedy output", "record these results". Runs the IHTP validator and appends a row to docs/experiments.md.
version: 2.0.0
---

# Score a Solution

Run the IHTP validator on an instance/solution pair, capture timing, and record the result.

## Steps

1. **Identify the instance and solution files** from the user's arguments or context:
   - Instance: `data/instances/<name>.json`  (e.g. `test01`, `i05`)
   - Solution: `data/solutions/<name_solution>.json` — infer from context; ask if ambiguous.

2. **Ensure the validator binary exists.** If `validator/IHTP_Validator` is missing, build it:
   ```bash
   g++ -O2 -std=c++17 -o validator/IHTP_Validator validator/IHTP_Validator.cc
   ```

3. **Run the validator:**
   ```bash
   ./validator/IHTP_Validator data/instances/<instance>.json data/solutions/<solution>.json
   ```
   Capture full stdout.

4. **Parse the output:**
   - Extract `Total violations` — if > 0, the solution is **infeasible**.
   - Extract `Total cost`.

5. **Detect timing:** Check if `main.py` stdout was captured (look for `elapsed_s: <float>`). Use that value if present; otherwise leave `avg_time_s` as `—`.

6. **Record the result:**

   a. **`docs/experiments.md`** — append a row (kept for quick reference):
   ```
   | YYYY-MM-DD | <instance> | <solver> | <config> | <violations> | <cost> | <notes> |
   ```

   b. **Active experiment doc** (if on an `exp/*` branch): update the matching row in the Results table of `docs/experiments/expNNN_<slug>.md`. Parse the instance name from the file and fill in Cost, Violations, and Time (s). Recompute `avg_cost`, `avg_time_s`, and `n_feasible` at the bottom whenever all 30 rows are filled.

   c. **`results.tsv`** — only update when `/benchmark` has produced a complete run (all 30 instances). Single `/score` calls do not write to `results.tsv`.

7. **Report back**: total violations, total cost, elapsed time if known, and whether the result was recorded.

## Notes

- The validator prints violations first (9 rows), then weighted costs (8 rows).
- A feasible solution has `Total violations = 0`.
- Lower total cost is better among feasible solutions.
- Reference score for `test01` reference solution: **3177** (0 violations).
- Instances `test01`–`test10` are excluded from experiment averages; use `i01`–`i30` for benchmarking.
- If the user only says `/score` with no args, ask for the instance and solution file names.
