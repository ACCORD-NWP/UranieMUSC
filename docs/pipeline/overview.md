# Pipeline Overview

UranieMUSC uses a **task pipeline** to coordinate all the steps needed to go from a fresh repository checkout to a set of NetCDF output files. This page explains what a pipeline is and how UranieMUSC's pipeline works — no prior knowledge assumed.

---

## What is a pipeline?

A **pipeline** is a series of steps where each step depends on the results of earlier steps. You can think of the steps as dominoes: you only need to push the last one, and it will trigger everything upstream that has not been done yet.

In UranieMUSC the pipeline is managed by a Python library called [Luigi](https://luigi.readthedocs.io/en/latest/). You do not need to know Luigi in detail to use UranieMUSC — this page covers everything you need.

---

## Tasks, targets, and dependencies

### Tasks

Each step in the pipeline is called a **task**. A task is a self-contained unit of work with a well-defined purpose: cloning a repository, building the Harmonie model, running MUSC, and so on.

UranieMUSC has nine tasks in total. They are described in detail on the {doc}`tasks` page.

### Targets (outputs)

Every task produces one or more **outputs** — files or directories that it writes to disk. Examples:

- `CloneRepos` produces three `.git` directories (one per cloned repository).
- `SetupMusc` produces `musc_run.sh`, `variable_list.csv`, and the namelist file.
- `RunMusc` produces one `Out.000.0000.lfa` binary file per MUSC run.

### Dependencies

Most tasks **depend** on earlier tasks. Before a task runs, Luigi checks that all its dependencies have completed. If they have not, Luigi runs them first — automatically, in the correct order.

The full dependency graph is shown in {ref}`pipeline-diagram` on the landing page.

---

## How Luigi decides whether to run a task

Before running a task, Luigi checks whether its outputs already exist on disk. If they do, Luigi considers the task **complete** and skips it. This has an important consequence:

> **If you run the pipeline a second time, only the tasks whose outputs are missing will run.**

This makes the pipeline **resumable**: if a step fails halfway through (e.g., a SLURM job times out), you can fix the problem and re-run the same command. Luigi will pick up from where it left off, skipping everything that already succeeded.

If you want to force a task to re-run even though its outputs exist, use the `--rerun` or `--rerun-all` flags — see {doc}`rerun`.

---

## Running a task

All tasks are launched from the command line via:

```shell
uv run uranmusc <TaskName> [options]
```

For example, to run the entire pipeline:

```shell
uv run uranmusc Run --local-scheduler
```

When you ask for a task, Luigi automatically runs all incomplete upstream tasks first. So asking for `Run` is equivalent to asking for everything.

### The `--local-scheduler` flag

By default, Luigi expects a central scheduler server to be running. The `--local-scheduler` flag tells Luigi to manage scheduling internally, without needing a server. This is the simplest way to get started.

If you want to monitor the pipeline progress in a web browser, start the Luigi server first and use `--scheduler-port` instead — see {doc}`../monitoring`.

---

## What happens on disk

When the config is loaded (at the start of any task), four directories are created automatically under your configured `hm_home` and `scratch_hm_home`:

```
<hm_home>/<experiment.name>/           ← Harmonie experiment home
<scratch_hm_home>/<experiment.name>/   ← Scratch working directory
<scratch_hm_home>/<experiment.name>/URANIE/   ← URANIE outputs
<scratch_hm_home>/<experiment.name>/OUTPUT/   ← MUSC outputs
```

As the pipeline progresses, files accumulate in these directories. The {doc}`tasks` page describes which files each task creates.

---

## Summary

| Concept | Plain-language meaning |
|---|---|
| Task | One step of the pipeline (e.g., "run MUSC") |
| Target | The file(s) a task writes to disk |
| Dependency | A task that must be complete before another task can start |
| Complete | A task whose output files already exist — Luigi will skip it |
| `--local-scheduler` | Run without a central Luigi server |
| `--rerun` | Force a specific task to run again |
