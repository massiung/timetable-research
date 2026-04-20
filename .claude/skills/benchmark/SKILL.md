---
name: benchmark
description: Use this skill when the user wants to benchmark a solver across all non-test instances — e.g. "/benchmark", "run benchmark", "evaluate on all instances". Runs the solver on i01–i30, records per-instance cost and timing, updates the active experiment doc, and appends a row to results.tsv.
version: 1.0.0
---

# Benchmark a Solver

Run the current solver on all 30 non-test instances (`i01`–`i30`), collect results, and record them.

## Steps

1. **Identify the active experiment.**
   - Run `git branch --show-current` to get the current branch.
   - If the branch is `exp/<slug>`, find the matching doc `docs/experiments/expNNN_<slug>.md`.
   - If no experiment doc exists, tell the user to run `/exp <slug>` first to set one up.
   - If not on an `exp/*` branch, warn the user and ask whether to proceed without recording.

2. **Identify the solver** from the user's argument or context (default: `greedy`).

3. **Build the validator** if `validator/IHTP_Validator` is missing:
   ```bash
   g++ -O2 -std=c++17 -o validator/IHTP_Validator validator/IHTP_Validator.cc
   ```

4. **Run the solver on each instance i01–i30** sequentially:
   ```bash
   uv run python -m src.main \
     --instance data/instances/i<NN>.json \
     --solver <solver> \
     --output data/solutions/i<NN>_solution.json \
     --time-limit 60
   ```
   For benchmarking, use `--time-limit 60` (1 minute per instance) unless the user specifies otherwise.
   After each run, capture:
   - `elapsed_s` — grep for `elapsed_s: ` in stdout.
   - Then run the validator and extract `Total violations` and `Total cost`.

5. **Fill in the experiment doc** `docs/experiments/expNNN_<slug>.md`:
   - Update the Results table row-by-row (instance, Cost, Violations, Time (s)).
   - After all 30, compute and fill:
     - `avg_cost` — mean cost over feasible instances (skip infeasible).
     - `avg_time_s` — mean elapsed_s across all 30.
     - `n_feasible` — count of feasible instances.
   - Set **Status** to `pending decision` (user sets keep/discard after reviewing).

6. **Commit and push the completed experiment branch**:
   ```bash
   git add docs/experiments/<exp_id>_<slug>.md
   git commit -m "exp: results for <exp_id> (<slug>)"
   git push origin exp/<slug>
   ```
   This preserves the full experiment (including code changes) on GitHub regardless of the keep/discard decision.

7. **Propagate doc + results row to `main`** (always, for every experiment):
   ```bash
   git checkout main
   # Copy the updated experiment doc and append the results.tsv row
   git checkout exp/<slug> -- docs/experiments/<exp_id>_<slug>.md
   # Append the TSV row to results.tsv on main
   git add docs/experiments/<exp_id>_<slug>.md results.tsv
   git commit -m "exp: log <exp_id> (<slug>) [<keep|discard|pending>]"
   git push origin main
   git checkout exp/<slug>
   ```
   - `avg_cost` — computed above (use `—` if no feasible instances).
   - `n_instances` — 30.
   - `avg_time_s` — computed above.
   - `status` — `pending` until the user decides.
   - `description` — ask the user for a one-line summary, or use `—`.

8. **Report a summary table** to the user:
   ```
   Instance | Cost   | Violations | Time (s)
   i01      | 4123   | 0          | 11.2
   ...
   avg_cost: 4891.3  avg_time_s: 12.1  n_feasible: 28/30
   ```
   Ask the user: **keep or discard?**
   - `keep` — merge the exp branch to `main` (brings in the code changes too), update `status` in `results.tsv` to `keep`, push `main`.
   - `discard` — update `status` in `results.tsv` to `discard` on `main`, push. The exp branch stays on GitHub but its code never reaches `main`.
   Optionally prompt the user to add a learning to `docs/learnings.md`.

## Notes

- Use `--time-limit 60` for benchmark runs to keep total time under ~30 minutes.
- Infeasible solutions (violations > 0) are excluded from `avg_cost` but included in `avg_time_s`.
- Instances `test01`–`test10` are never included in benchmarks.
- If a run crashes (non-zero exit code), record `crash` for that instance and continue.
- Do not write to `results.tsv` if fewer than 30 instances completed (partial runs are not records).
- **`main` always ends up with the experiment doc and `results.tsv` row**, even for discards. Only solver code changes are withheld from `main` on a discard.
