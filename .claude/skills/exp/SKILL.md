---
name: exp
description: Use this skill when the user wants to start a new experiment — e.g. "/exp greedy-tweak-x", "new experiment ls-swap", "start experiment". Creates the experiment branch, assigns an exp_id, and stubs the experiment doc for the user to fill in the hypothesis.
version: 1.0.0
---

# Start a New Experiment

Set up a new experiment: branch, ID, and doc page stub — ready for the user to fill in the hypothesis before coding.

## Steps

1. **Parse the slug** from the user's argument (e.g., `/exp greedy-tweak-x` → slug = `greedy-tweak-x`).
   - If no slug is provided, ask the user for one. It should be short and descriptive (kebab-case).

2. **Assign the next exp_id**:
   - Count data rows in `results.tsv` (lines after the header). Next ID = count + 1, zero-padded to 3 digits (e.g., `exp001`).

3. **Check the branch doesn't already exist**:
   ```bash
   git branch --list exp/<slug>
   ```
   If it exists, warn the user and ask for a different slug.

4. **Create and check out the branch**:
   ```bash
   git checkout -b exp/<slug>
   ```

5. **Create the experiment doc** `docs/experiments/<exp_id>_<slug>.md` by copying the TEMPLATE and filling in:
   - Title, branch name, date (today), exp_id.
   - Leave Hypothesis, Changes, Results table, and Conclusion blank for the user.

6. **Commit the stub doc** and push the branch to GitHub immediately:
   ```bash
   git add docs/experiments/<exp_id>_<slug>.md
   git commit -m "exp: stub doc for <exp_id> (<slug>)"
   git push -u origin exp/<slug>
   ```

7. **Report back** to the user:
   - Experiment ID and branch name (with GitHub URL).
   - Path to the doc file.
   - Remind them to: (1) fill in the Hypothesis section, (2) make code changes, (3) run `/benchmark` when ready.

## Notes

- Branch naming: `exp/<slug>` — no date prefix, no uppercase.
- **Always push `exp/*` branches to GitHub** — this preserves the code for every experiment, including discards.
- The experiment doc is the source of truth for hypothesis and results; `results.tsv` is the machine-readable summary.
- Only one experiment should be active (in-progress) at a time. If the user is already on an `exp/*` branch, warn them before creating a new one.
- After `/benchmark` runs and the user decides keep/discard, the skill handles propagating results to `main` — see `/benchmark` notes.
