# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

See **AGENTS.md** for the canonical reference: commands, architecture, code quality rules, runtime constraints, and data model. Everything in AGENTS.md applies here too.

## Claude-Specific Workflows

### Scoring a solution

Use `/score` to run the C++ validator on any instance/solution pair and automatically record the result in `docs/experiments.md`. The skill handles building the validator if missing, parsing output, and appending the row.

### Benchmarking across instances

Use `/benchmark` (once implemented — see issue #4) to run a solver across all instances and log results in bulk.

## Keeping This File Current

After completing any task, ask: **do CLAUDE.md and AGENTS.md still accurately describe the repo?**

Update AGENTS.md when the change is agent-agnostic (new module, changed command, new data model fact, quality rule).  
Update CLAUDE.md only for Claude-specific additions (new skills, Claude-only workflow changes).

Do **not** add: implementation details already visible from reading the code, per-PR changelogs, or anything derivable from `git log`.
