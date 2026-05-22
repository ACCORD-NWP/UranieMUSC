# Rerunning Tasks

By default, UranieMUSC never re-executes a task whose outputs already exist on disk. This page explains how to override that behaviour when you need to.

---

## Why tasks are skipped by default

When Luigi starts a task, it first checks whether the task's **output files already exist**. If they do, the task is considered **complete** and is skipped. This is intentional since a full pipeline run takes time, and often you only want to rerun specific task.

See {doc}`overview` for a broader explanation.

---

## The `--rerun-task` flag

Use `--rerun-task` to force a **single task** to re-execute, even if its outputs are present.

```shell
uv run uranmusc RunUranie --rerun-task --local-scheduler
```

This re-runs only `RunUranie`. All upstream tasks (`CloneRepos`, `SetupExperiment`, etc.) are still skipped if their outputs exist. 

**Typical use case:** You edited the `design_of_experiment` block in `config.yml` to change the parameter ranges and want to regenerate the perturbed namelists without rebuilding Harmonie.

---

## The `--rerun-all` flag

Use `--rerun-all` to force **all tasks in the pipeline** to re-execute from scratch.

```shell
uv run uranmusc Run --rerun-all --local-scheduler
```

This is equivalent to deleting all outputs and running the pipeline fresh. Use it with caution — it will re-trigger the Harmonie build.

**Typical use case:** You want a completely clean run e.g. to rule out errors due to cached output.

---

## Partial restarts after SLURM failures

`RunMusc` has special handling for partial failures. If a SLURM job completes but some individual MUSC runs failed (e.g., due to out-of-memory errors), only the successful runs will have written their output files (`*.lfa` files).

On the next invocation, `RunMusc` compares:
- The number of `URANIE/UranieLauncher_*` directories (total runs requested).
- The number of `OUTPUT/<musc_id>_URA_*` directories (runs that produced output).

If these counts differ, `RunMusc` considers itself incomplete and re-submits **only the missing runs**. You do not need to pass `--rerun-task` for this — it happens automatically.

The same logic applies to `ConvertLFAToNetCDF`.

---

## Summary

| Scenario | Command |
|---|---|
| Re-run a single task | `uv run uranmusc <TaskName> --rerun-task --local-scheduler` 
| Re-run everything from scratch | `uv run uranmusc Run --rerun-all --local-scheduler` |
| Resume after a partial MUSC failure | Re-run `RunMusc` without any flags — partial restart is automatic |
