# Configuration

All runtime settings for UranieMUSC live in a single file: **`config.yml`** at the root of the repository. The file is read once when any pipeline task starts. If a required field is missing or has the wrong type, the run will fail immediately with a validation error (courtesy of [Pydantic](https://docs.pydantic.dev/)).

Below is an annotated reference for every field. Replace `$USER` with your ATOS username.

---

## Annotated example

```yaml
general:
  ura_env: /hpcperm/cu0k/URANIE/uranie.env     # Point to an existing URANIE installation of the cu0k user.
  musc_data_dir: /hpcperm/$USER/musc/HarmonieMuscData/musc_ref
  hm_home: /home/$USER/hm_home
  scratch_hm_home: /scratch/$USER/hm_home
  grp: accord

experiment:
  name: TestExperiment
  fc_length: 6
  musc_id: DEF
  musc_case: REFL65
  design_of_experiment:
    type: morris_sensitivity       # or "sampling" for traditional sampling-based DOE
    trajectories: 5                # Morris-specific
    levels: 20                     # Morris-specific
    data_files:
      dataserver: init_doe.dat
      namelist_template: namelist  # produces namelist_atm_DEF
    variables:
      inputs: ["VSIGQSAT"]
      minima: [0.01]
      maxima: [0.5]
      namelist_flags: ["@VSIGQSAT@"]

git_repos:
  harmonie:
    repo: /hpcperm/$USER/harmonie_releases/musc_dev-CY49T2h/
    url: git@github.com:Hirlam/HarmonieCSC.git
    branch: dev-CY49T2h
  ddhtoolbox:
    repo: /hpcperm/$USER/ddhtoolbox/
    url: git@github.com:UMR-CNRM/ddhtoolbox.git
    branch: master
  musc_data:
    repo: /hpcperm/$USER/musc/HarmonieMuscData
    url: git@github.com:Hirlam/HarmonieMuscData.git
    branch: master
```

---

## `general` section

These fields describe the HPC environment and shared filesystem locations.

| Field | Type | Description |
|---|---|---|
| `ura_env` | path | Shell script that activates URANIE by loading the ROOT/URANIE environment variables. It is sourced (via `source`) before the `RunUranie` task is executed. |
| `musc_data_dir` | path | Directory containing the reference MUSC initial and boundary condition data. The `RunMusc` task passes this to `musc_run.sh -d`. |
| `hm_home` | path | Permanent home directory for Harmonie experiment setups. The experiment subdirectory `<hm_home>/<experiment.name>` is created here when the config is first loaded. |
| `scratch_hm_home` | path | Fast scratch filesystem directory for active experiment runs. MUSC namelists, URANIE outputs, and MUSC outputs are all written under `<scratch_hm_home>/<experiment.name>`. |
| `grp` | string (optional) | Unix group name (e.g., `accord`). When set, every directory created by the pipeline is group-owned by this group and given `rwxr-s---` permissions (setgid bit). Omit or leave blank to skip permission management. |

### Derived paths

The following directories are automatically created from the fields above when the config is loaded. You do not need to create them manually.

| Path | Formula | Purpose |
|---|---|---|
| `home_exp_dir` | `hm_home / experiment.name` | Harmonie experiment home (e.g., `/home/dnk3604/hm_home/TestExperiment`) |
| `scratch_exp_dir` | `scratch_hm_home / experiment.name` | Scratch working directory (e.g., `/scratch/dnk3604/hm_home/TestExperiment`) |
| `uranie_dir` | `scratch_exp_dir / "URANIE"` | Where URANIE writes the dataserver and per-sample namelist directories |
| `output_dir` | `scratch_exp_dir / "OUTPUT"` | Where MUSC writes LFA binary files; also where NetCDF files are placed after conversion |
| `project_dir` | *(package root)* | Absolute path to the installed UranieMUSC package root. Used internally to locate `design_of_experiment.py`. |
| `namelist_atm` | `home_exp_dir / "<namelist_template>_atm_<musc_id>"` | Path to the atmospheric namelist file (e.g., `namelist_atm_DEF`). If `design_of_experiment.data_files.namelist_dir` is set, resolves to that directory instead. |
| `namelist_sfx` | `home_exp_dir / "<namelist_template>_sfx_<musc_id>"` | Path to the surface namelist file (e.g., `namelist_sfx_DEF`). Same directory logic as `namelist_atm`. |

---

## `experiment` section

These fields describe the specific MUSC experiment to run.

| Field | Type | Description |
|---|---|---|
| `name` | string | A short identifier for this experiment (e.g., `TestExperiment`). Used as the subdirectory name inside `hm_home` and `scratch_hm_home`. Choose a name that is unique across your experiments. |
| `fc_length` | integer | Forecast length in **hours** (e.g., `6`). Passed to the `musc_namelist.sh` script via the `-l` flag. |
| `musc_id` | string | A short label for this MUSC configuration (e.g., `DEF`). Used to name the generated namelist file (`namelist_atm_DEF`) and the per-sample output directories (`DEF_URA_0`, `DEF_URA_1`, …). |
| `musc_case` | string | The name of the MUSC test case to run (e.g., `REFL65`). This selects which set of initial conditions and large-scale forcings to use from the `musc_data_dir`. Available cases are defined by the `musc_data` repository. |
| `design_of_experiment` | block | Inline configuration for the URANIE design of experiment. See below. |

### `experiment.design_of_experiment`

All DOE settings are specified inline in `config.yml`. The block has three required sub-fields and additional fields that depend on the DOE type.

| Field | Type | Description |
|---|---|---|
| `type` | string | DOE method: `"morris_sensitivity"` for a Morris Sensitivity analysis, or `"sampling"` for a traditional sampling-based analysis. |
| `data_files` | block | Filenames used by URANIE. See `data_files` below. |
| `variables` | block | The namelist parameters to perturb and their ranges. See `variables` below. |

**Morris-specific fields** (required when `type: morris_sensitivity`):

| Field | Type | Description |
|---|---|---|
| `trajectories` | integer | Number of Morris trajectories. Total MUSC runs = `trajectories × (len(inputs) + 1)`. |
| `levels` | integer | Number of grid levels for parameter discretisation. |

**Sampling-specific fields** (required when `type: sampling`):

| Field | Type | Description |
|---|---|---|
| `sample_size` | integer | Number of samples to generate. Equals the total number of MUSC runs. |
| `distribution` | string | Currently, only `"lhs"` (Latin Hypercube Sampling) is supported. |

### `experiment.design_of_experiment.data_files`

| Field | Type | Description |
|---|---|---|
| `dataserver` | string | Filename of the URANIE output dataserver file. Written to `<uranie_dir>/`. Example: `init_doe.dat`. |
| `namelist_template` | string | Base name for the namelist files. The pipeline appends `_atm_<musc_id>` and `_sfx_<musc_id>` to form the actual filenames. Example: `namelist` → `namelist_atm_DEF`, `namelist_sfx_DEF`. |
| `namelist_dir` | path (optional) | If set, `SetupMuscNamelists` copies pre-existing namelist files from `<namelist_dir>/<musc_case>/` instead of generating them with `musc_namelist.sh`. Omit to generate namelists from the built Harmonie code. |

### `experiment.design_of_experiment.variables`

All lists must have the same length `k` (one entry per perturbed parameter).

| Field | Type | Description |
|---|---|---|
| `inputs` | list of strings | Namelist parameter names exactly as they appear in the namelist file. Example: `["VSIGQSAT", "XLCOR"]`. |
| `minima` | list of numbers | Lower bound for each parameter. Example: `[0.01, 100000]`. |
| `maxima` | list of numbers | Upper bound for each parameter. Example: `[0.5, 300000]`. |
| `namelist_flags` | list of strings | URANIE token strings. Each token is inserted into the namelist template by `RunUranie` in place of the parameter's default value. Convention: `@VARNAME@`. Example: `["@VSIGQSAT@", "@XLCOR@"]`. |

For a full schema reference see {doc}`reference/namelist_yml`. For use-case examples see {doc}`use_cases/sensitivity_morris` and {doc}`use_cases/lhs_sampling`.

---

## `git_repos` section

UranieMUSC requires three git repositories. Each is described by three fields:

| Field | Type | Description |
|---|---|---|
| `repo` | path | Local filesystem path where the repository will be cloned (or is already present). |
| `url` | string | Remote git URL used by `CloneRepos` to clone the repository. |
| `branch` | string | Branch name to check out after cloning (`--single-branch --branch`). |

### `harmonie`

The Harmonie NWP system. Provides the build infrastructure, namelist generation scripts (`musc_namelist.sh`, `musc_setup.sh`), and the MUSC run script (`musc_run.sh`).

### `ddhtoolbox`

The DDH (Diagnostics in Horizontal Domains) toolbox. Provides the `lfac` binary used by `ConvertLFAToNetCDF` to translate MUSC's binary LFA output files into NetCDF format.

### `musc_data`

The HarmonieMuscData repository. Contains the reference initial condition and forcing data for each MUSC test case (e.g., `REFL65`).

---

## Tips

- **Use absolute paths.** All `path` fields must be absolute (starting with `/`). Relative paths are not supported.
- **Keep `experiment.name` short and alphanumeric.** It appears in directory names and SLURM job names.
- **Never share `scratch_hm_home` between two experiments with the same `name`.** The pipeline will silently overwrite outputs.
- **Check `ura_env` first.** If the URANIE environment file cannot be sourced, `RunUranie` will fail at runtime. Ask @j-fannon for the correct path.
- **Use `--config` to switch between configurations.** Pass `--config /path/to/other_config.yml` on the command line to use a config file other than the default `config.yml`.
