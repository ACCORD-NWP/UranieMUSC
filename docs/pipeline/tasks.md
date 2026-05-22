# Tasks Reference

This page documents every task in the UranieMUSC pipeline. Tasks are listed in dependency order — each task requires all tasks above it (or a subset) to be complete.

For an explanation of what tasks, targets, and dependencies mean, see {doc}`overview`.

---

## `CloneRepos`

**Purpose:** Clone all three required git repositories to the local filesystem.

**Dependencies:** None — this is the first task in the pipeline.

**Outputs (completion markers):**
- `<harmonie.repo>/.git`
- `<ddhtoolbox.repo>/.git`
- `<musc_data.repo>/.git`

**What it does:**

For each repository defined under `git_repos` in `config.yml` (`harmonie`, `ddhtoolbox`, `musc_data`), the task deletes any existing clone at the configured `repo` path and runs:

```shell
git clone --recurse-submodules --single-branch --branch <branch> <url> <repo>
```

**CLI usage:**

```shell
uv run uranmusc CloneRepos --local-scheduler
```

---

## `SetupExperiment`

**Purpose:** Initialise a Harmonie experiment directory structure on ATOS.

**Dependencies:** `CloneRepos`

**Outputs:**
- `<home_exp_dir>/config-sh/` directory

**What it does:**

1. Cleans up `home_exp_dir` (removes all contents except `output_dir` and `uranie_dir` if they exist).
2. Runs the Harmonie setup script:

   ```shell
   <harmonie.repo>/config-sh/Harmonie setup -r <harmonie.repo> -h ECMWF.atos
   ```

   This creates the standard Harmonie experiment directory layout, including the `config-sh/` directory that holds system configuration.

**CLI usage:**

```shell
uv run uranmusc SetupExperiment --local-scheduler
```

---

## `BuildExperiment`

**Purpose:** Compile the Harmonie model on ATOS using CMake.

**Dependencies:** `SetupExperiment`

**Outputs:**
- `<home_exp_dir>/experiment_is_locked` (sentinel file created after a successful build)

**What it does:**

Runs the Harmonie install/build step:

```shell
Harmonie install BUILD=yes BUILD_WITH=cmake
```

This submits a job to the **ecFlow** workflow scheduler, which compiles the Harmonie model. The task then polls ecFlow every 60 seconds until the job reports `complete` or `aborted`. A successful build can take 30–60 minutes.

:::{note}
`BuildExperiment` is the most time-consuming step. If the build is aborted by ecFlow, the task will raise an error. Check the ecFlow log for the cause before retrying.
:::

**CLI usage:**

```shell
uv run uranmusc BuildExperiment --local-scheduler
```

---

## `SetupMusc`

**Purpose:** Set up the MUSC configuration and generate the base namelist.

**Dependencies:** `CloneRepos`, `SetupExperiment`, `BuildExperiment`

**Outputs:**
- `<home_exp_dir>/musc_run.sh`
- `<home_exp_dir>/musc_convert_netcdf.sh`
- `<home_exp_dir>/variable_list.csv`
- `<home_exp_dir>/namelist_atm_<musc_id>` (e.g., `namelist_atm_DEF`)

**What it does:**

1. Runs the MUSC setup script to install scripts and configuration files into the experiment directory:

   ```shell
   MUSCHOME=<home_exp_dir> <harmonie.repo>/util/musc/scr/musc_setup.sh -r <harmonie.repo>
   ```

2. Generates the base MUSC namelist for the configured forecast length:

   ```shell
   <home_exp_dir>/musc_namelist.sh -l <fc_length> -i <musc_id>
   ```

   The resulting namelist file (`namelist_atm_DEF`) contains all MUSC physics parameters at their default values. This file is later modified by `RunUranie` to insert URANIE's perturbed values.

**CLI usage:**

```shell
uv run uranmusc SetupMusc --local-scheduler
```

---

## `RunUranie`

**Purpose:** Use URANIE to generate a family of perturbed namelists — one per sample point in parameter space.

**Dependencies:** `CloneRepos`, `SetupExperiment`, `BuildExperiment`, `SetupMusc`

**Outputs:**
- `<uranie_dir>/<dataserver_filename>` — the URANIE dataserver file (e.g., `URANIE/init_doe.dat`)
- `<scratch_exp_dir>/<namelist_template>` — the namelist with `@VAR@` placeholder tokens

**What it does:**

1. Reads the `ura_init_namelist` YAML file to find the parameter names, bounds, and URANIE token strings.
2. Takes the base namelist (`namelist_atm_DEF`) and replaces each default parameter value with a `@VARNAME@` placeholder token. For example:

   ```
   VSIGQSAT= 0.1 ,   →   VSIGQSAT= @VSIGQSAT@ ,
   ```

3. Sources the URANIE environment file and runs the `ura_init` Python script (e.g., `doe_sensitivity.py`):

   ```shell
   source <ura_env> && python3 doe_sensitivity.py <ura_init_namelist>
   ```

4. URANIE reads the template namelist, substitutes each `@VARNAME@` token with a concrete sampled value, and writes one subdirectory per sample point:

   ```
   URANIE/UranieLauncher_0/namelist_atm_DEF   ← VSIGQSAT = 0.01
   URANIE/UranieLauncher_1/namelist_atm_DEF   ← VSIGQSAT = 0.13
   URANIE/UranieLauncher_2/namelist_atm_DEF   ← VSIGQSAT = 0.27
   ...
   ```

5. Also writes the URANIE dataserver file (`init_doe.dat`), which records all sampled values in a tabular format for later analysis.

**CLI usage:**

```shell
uv run uranmusc RunUranie --local-scheduler
```

---

## `RunMusc`

**Purpose:** Execute MUSC once per perturbed namelist, in parallel on SLURM.

**Dependencies:** `CloneRepos`, `SetupExperiment`, `BuildExperiment`, `SetupMusc`, `RunUranie`

**Outputs:**
- `<output_dir>/<musc_id>_URA_<N>/Out.000.0000.lfa` for each sample point N

**What it does:**

1. Identifies the set of `URANIE/UranieLauncher_*` directories produced by `RunUranie`.
2. For each launcher directory, copies its `namelist_atm_DEF` into the Harmonie experiment home as `namelist_atm_DEF_URA_<N>`, and creates a companion symlink for the surface namelist (`namelist_sfx_*`).
3. Writes a SLURM batch script that runs all MUSC instances **in parallel** using `musc_run.sh`:

   ```shell
   musc_run.sh -d <musc_data_dir> -n <musc_case> -i <musc_id>_URA_0 &
   musc_run.sh -d <musc_data_dir> -n <musc_case> -i <musc_id>_URA_1 &
   ...
   wait
   ```

4. Submits the batch script with `sbatch --wait` (blocks until all MUSC runs have finished).

The number of MUSC runs equals the number of sample points generated by URANIE (e.g., 10 runs for a 5-trajectory Morris analysis on 1 parameter).

**Partial restart:** If some outputs already exist (e.g., after a partial SLURM failure), only the missing runs are submitted. See {doc}`rerun` for details.

**CLI usage:**

```shell
uv run uranmusc RunMusc --local-scheduler
# optionally, to set the number of SLURM tasks:
uv run uranmusc RunMusc --ntasks 4 --local-scheduler
```

---

## `BuildDDH`

**Purpose:** Compile the `lfac` binary from the DDH toolbox. This tool converts MUSC's binary LFA output files to NetCDF.

**Dependencies:** `CloneRepos`

**Outputs:**
- `<ddhtoolbox.repo>/tools/lfa/lfac`

**What it does:**

Runs the DDH toolbox build system from the `tools/` directory:

```shell
export PATH=.:$PATH
install clean
install
```

This compiles the `lfac` Fortran program that understands the LFA binary format.

**CLI usage:**

```shell
uv run uranmusc BuildDDH --local-scheduler
```

---

## `ConvertLFAToNetCDF`

**Purpose:** Convert all MUSC binary LFA output files to NetCDF.

**Dependencies:** `BuildDDH`, `CloneRepos`, `SetupExperiment`, `BuildExperiment`, `SetupMusc`, `RunUranie`, `RunMusc`

**Outputs:**
- `<output_dir>/<musc_id>_URA_<N>/musc_output_<YYMMDD>.nc` for each sample point N

**What it does:**

1. For each `OUTPUT/<musc_id>_URA_<N>` directory, copies the `config-sh/` directory into it (required by the conversion script).
2. Writes a SLURM batch script that runs the conversion script for each output directory **in parallel**:

   ```shell
   musc_convert_netcdf.sh -e <output_dir>/<musc_id>_URA_0 -v <variable_list.csv> &
   musc_convert_netcdf.sh -e <output_dir>/<musc_id>_URA_1 -v <variable_list.csv> &
   ...
   wait
   ```

3. Submits with `sbatch --wait`.

**CLI usage:**

```shell
uv run uranmusc ConvertLFAToNetCDF --local-scheduler
```

---

## `Run` (full pipeline)

**Purpose:** Run the entire pipeline from start to finish.

**Dependencies:** `ConvertLFAToNetCDF` (which in turn depends on all other tasks)

**What it does:**

`Run` is a convenience wrapper. It has no work of its own — it simply declares `ConvertLFAToNetCDF` as its dependency, which causes Luigi to resolve and execute the entire graph.

**CLI usage:**

```shell
uv run uranmusc Run --local-scheduler
```

This is the command most users should start with.

---

## Quick reference

| Task | Key output | Approx. time |
|---|---|---|
| `CloneRepos` | `.git` in each repo dir | seconds |
| `SetupExperiment` | `home_exp_dir/config-sh/` | < 1 min |
| `BuildExperiment` | `experiment_is_locked` | 30–60 min |
| `SetupMusc` | `namelist_atm_<id>` | < 1 min |
| `RunUranie` | `URANIE/init_doe.dat` + `UranieLauncher_*/` | < 1 min |
| `RunMusc` | `OUTPUT/<id>_URA_*/Out.000.0000.lfa` | minutes (depends on sample size) |
| `BuildDDH` | `ddhtoolbox/tools/lfa/lfac` | < 1 min |
| `ConvertLFAToNetCDF` | `OUTPUT/<id>_URA_*/*.nc` | < 5 min |
| `Run` | (all of the above) | — |
