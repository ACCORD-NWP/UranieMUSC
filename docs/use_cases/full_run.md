# Full Run Walkthrough

This page guides you through a complete UranieMUSC run from a fresh checkout to a set of NetCDF output files. It assumes you have already completed the {doc}`../installation` steps.

---

## Step 1: Edit `config.yml`

Open `config.yml` at the root of the repository and fill in the fields for your environment. The fields most likely to need changing are:

```yaml
general:
  ura_env: /path/to/your/uranie.env        # ask your sysadmin for this
  musc_data_dir: /path/to/HarmonieMuscData/musc_ref
  hm_home: /home/<your-username>/hm_home
  scratch_hm_home: /scratch/<your-username>/hm_home
  grp: accord                               # your shared unix group

experiment:
  name: MyFirstRun      # choose a unique name
  fc_length: 6          # forecast length in hours
  musc_id: DEF
  musc_case: REFL65     # test case from musc_data
  design_of_experiment:
    type: morris_sensitivity
    data_files:
      dataserver: init_doe.dat
      namelist_template: namelist
    variables:
      inputs: ["VSIGQSAT"]
      minima: [0.01]
      maxima: [0.5]
      namelist_flags: ["@VSIGQSAT@"]
    trajectories: 5
    levels: 20

git_repos:
  harmonie:
    repo: /hpcperm/<your-username>/harmonie_releases/musc_dev
    url: git@github.com:Hirlam/HarmonieCSC.git
    branch: dev-CY49T2h
  ddhtoolbox:
    repo: /hpcperm/<your-username>/ddhtoolbox
    url: git@github.com:UMR-CNRM/ddhtoolbox.git
    branch: master
  musc_data:
    repo: /hpcperm/<your-username>/HarmonieMuscData
    url: git@github.com:Hirlam/HarmonieMuscData.git
    branch: master
```

See the {doc}`../configuration` page for a full explanation of every field.

To use a config file in a different location, pass `--config /path/to/config.yml` to any task command.

---

## Step 2: (Optional) Adjust what to perturb

The default `design_of_experiment` block above runs a Morris sensitivity analysis on a single parameter (`VSIGQSAT`). If this is your first run, leave it as-is. You can add more parameters later — see {doc}`add_parameter`.

---

## Step 3: Start the Luigi scheduler

For progress monitoring in a web browser, start the Luigi scheduler before running any tasks (see {doc}`../monitoring`). If you just want to run without the web UI, skip this step and use `--local-scheduler` instead (shown below).

---

## Step 4: Run the full pipeline

```shell
uv run uranmusc Run --local-scheduler
```

Luigi will now execute all tasks in dependency order. You can watch the log output in the terminal.

If you started the Luigi server on port 8082, use `--scheduler-port 8082` instead of `--local-scheduler`:

```shell
uv run uranmusc Run --scheduler-port 8082
```

---

## What happens at each step

### `CloneRepos`

Luigi clones the three repositories into the paths specified in `git_repos`. This takes some time since `harmonie` is large.

```
<harmonie.repo>/.git   ← created
<ddhtoolbox.repo>/.git ← created
<musc_data.repo>/.git  ← created
```

### `SetupExperiment`

Luigi initialises the Harmonie experiment directory:

```
<hm_home>/MyFirstRun/config-sh/   ← created
```

### `BuildExperiment`

Luigi submits the Harmonie CMake build job to ecFlow and waits for it to complete. **This step takes 30–60 minutes.** The terminal will show periodic log messages while it polls the ecFlow scheduler.

When the step finishes:

```
<hm_home>/MyFirstRun/experiment_is_locked   ← created
```

### `SetupMusc`

Luigi runs the MUSC setup scripts, generating the run scripts:

```
<hm_home>/MyFirstRun/musc_run.sh
<hm_home>/MyFirstRun/musc_convert_netcdf.sh
<hm_home>/MyFirstRun/variable_list.csv
```

### `SetupMuscNamelists`

Luigi generates the base MUSC namelist for the configured forecast length:

```
<hm_home>/MyFirstRun/namelist_atm_DEF   ← created
```

If `design_of_experiment.data_files.namelist_dir` is set, the namelist is copied from that directory instead.

### `RunUranie`

Luigi patches the namelist and runs the URANIE Python script. For the default Morris configuration (5 trajectories, 1 parameter), this creates 10 sample directories:

```
<scratch>/MyFirstRun/URANIE/init_doe.dat
<scratch>/MyFirstRun/URANIE/UranieLauncher_0/namelist_atm_DEF
<scratch>/MyFirstRun/URANIE/UranieLauncher_1/namelist_atm_DEF
...
<scratch>/MyFirstRun/URANIE/UranieLauncher_9/namelist_atm_DEF
```

Each namelist has a different value of `VSIGQSAT` substituted in.

### `BuildDDH` (runs in parallel with some upstream tasks)

Luigi compiles the `lfac` binary in the DDH toolbox repository:

```
<ddhtoolbox.repo>/tools/lfa/lfac   ← created
```

### `RunMusc`

Luigi submits a SLURM job that runs all 10 MUSC instances in parallel. When complete:

```
<scratch>/MyFirstRun/OUTPUT/DEF_URA_0/Out.000.0000.lfa
<scratch>/MyFirstRun/OUTPUT/DEF_URA_1/Out.000.0000.lfa
...
<scratch>/MyFirstRun/OUTPUT/DEF_URA_9/Out.000.0000.lfa
```

### `ConvertLFAToNetCDF`

Luigi submits a SLURM job to convert all LFA files to NetCDF in parallel:

```
<scratch>/MyFirstRun/OUTPUT/DEF_URA_0/musc_output_<date>.nc
<scratch>/MyFirstRun/OUTPUT/DEF_URA_1/musc_output_<date>.nc
...
<scratch>/MyFirstRun/OUTPUT/DEF_URA_9/musc_output_<date>.nc
```

---

## Step 5: Check the outputs

Navigate to the output directory:

```shell
ls <scratch_hm_home>/MyFirstRun/OUTPUT/
```

You should see ten subdirectories, each containing a `.nc` file. These are your MUSC forecast outputs, one per sample point in parameter space.

The URANIE dataserver file (`URANIE/init_doe.dat`) records the exact parameter value used in each run, enabling you to map each output file back to a specific `VSIGQSAT` value.

---

## Troubleshooting

**The build step fails / ecFlow shows `aborted`**
Check the Harmonie build log in `<hm_home>/MyFirstRun/`.

**`RunUranie` fails with an import error**
The URANIE environment script (`ura_env`) could not be sourced, or the ROOT Python bindings are not available. Verify the `ura_env` path and that the URANIE installation is functional on your system.

**`RunMusc` fails with a SLURM error**
Check the SLURM output file (written to `<scratch>/MyFirstRun/` with a name like `slurm-<jobid>.out`). Common causes are memory limits.

**A task is skipped unexpectedly**
Its output files already exist. Use `--rerun-task` to force it to re-run — see {doc}`../pipeline/rerun`.
