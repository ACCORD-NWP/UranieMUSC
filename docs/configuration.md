# Configuration

All runtime settings for UranieMUSC live in a single file: **`config.yml`** at the root of the repository. The file is read once when any pipeline task starts. If a required field is missing or has the wrong type, the run will fail immediately with a validation error (courtesy of [Pydantic](https://docs.pydantic.dev/)).

Below is an annotated reference for every field.

---

## Annotated example

```yaml
general:
  ura_env: /hpcperm/cu0k/URANIE/uranie.env
  musc_data_dir: /hpcperm/dnk3604/musc/HarmonieMuscData/musc_ref
  hm_home: /home/dnk3604/hm_home
  scratch_hm_home: /scratch/dnk3604/hm_home
  grp: accord

experiment:
  name: Test5
  fc_length: 6
  musc_id: DEF
  musc_case: REFL65
  ura_init: uranmusc/doe_sensitivity.py
  ura_init_namelist: nam/doe_musc_sensitivity.yml

git_repos:
  harmonie:
    repo: /hpcperm/dnk3604/harmonie_releases/musc_dev-CY49T2h/
    url: git@github.com:Hirlam/HarmonieCSC.git
    branch: dev-CY49T2h
  ddhtoolbox:
    repo: /hpcperm/dnk3604/ddhtoolbox/
    url: git@github.com:UMR-CNRM/ddhtoolbox.git
    branch: master
  musc_data:
    repo: /hpcperm/dnk3604/musc/HarmonieMuscData
    url: git@github.com:Hirlam/HarmonieMuscData.git
    branch: master
```

---

## `general` section

These fields describe the HPC environment and shared filesystem locations.

| Field | Type | Description |
|---|---|---|
| `ura_env` | path | Shell script that activates URANIE by loading the ROOT/URANIE environment variables. It is sourced (via `source`) before any URANIE Python script is executed. Typically provided by a system administrator. |
| `musc_data_dir` | path | Directory containing the reference MUSC initial and boundary condition data. The `RunMusc` task passes this to `musc_run.sh -d`. |
| `hm_home` | path | Permanent home directory for Harmonie experiment setups. The experiment subdirectory `<hm_home>/<experiment.name>` is created here when the config is first loaded. |
| `scratch_hm_home` | path | Fast scratch filesystem directory for active experiment runs. MUSC namelists, URANIE outputs, and MUSC outputs are all written under `<scratch_hm_home>/<experiment.name>`. |
| `grp` | string (optional) | Unix group name (e.g., `accord`). When set, every directory created by the pipeline is group-owned by this group and given `rwxr-s---` permissions (setgid bit). Omit or leave blank to skip permission management. |

### Derived paths

The following four directories are automatically created from the fields above when the config is loaded. You do not need to create them manually.

| Path | Formula | Purpose |
|---|---|---|
| `home_exp_dir` | `hm_home / experiment.name` | Harmonie experiment home (e.g., `/home/dnk3604/hm_home/Test5`) |
| `scratch_exp_dir` | `scratch_hm_home / experiment.name` | Scratch working directory (e.g., `/scratch/dnk3604/hm_home/Test5`) |
| `uranie_dir` | `scratch_exp_dir / "URANIE"` | Where URANIE writes the dataserver and per-sample namelist directories |
| `output_dir` | `scratch_exp_dir / "OUTPUT"` | Where MUSC writes LFA binary files; also where NetCDF files are placed after conversion |

---

## `experiment` section

These fields describe the specific MUSC experiment to run.

| Field | Type | Description |
|---|---|---|
| `name` | string | A short identifier for this experiment (e.g., `Test5`). Used as the subdirectory name inside `hm_home` and `scratch_hm_home`. Choose a name that is unique across your experiments. |
| `fc_length` | integer | Forecast length in **hours** (e.g., `6`). Passed to the `musc_namelist.sh` script via the `-l` flag. |
| `musc_id` | string | A short label for this MUSC configuration (e.g., `DEF`). Used to name the generated namelist file (`namelist_atm_DEF`) and the per-sample output directories (`DEF_URA_0`, `DEF_URA_1`, …). |
| `musc_case` | string | The name of the MUSC test case to run (e.g., `REFL65`). This selects which set of initial conditions and large-scale forcings to use from the `musc_data_dir`. Available cases are defined by the `musc_data` repository. |
| `ura_init` | path | Path to the URANIE Python script that performs the design of experiment. Two scripts are provided: `uranmusc/doe_sensitivity.py` (Morris sensitivity analysis, the default) and `uranmusc/doe.py` (Latin Hypercube Sampling). See {doc}`use_cases/sensitivity_morris` and {doc}`use_cases/lhs_sampling`. |
| `ura_init_namelist` | path | Path to the YAML file that tells the URANIE script which namelist parameters to perturb and over what ranges. See {doc}`reference/namelist_yml` for the full schema. |

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

The DDH (Diagnostic du Bilan Dynamique Harmonisé) toolbox. Provides the `lfac` binary used by `ConvertLFAToNetCDF` to translate MUSC's binary LFA output files into NetCDF format.

### `musc_data`

The HarmonieMuscData repository. Contains the reference initial condition and forcing data for each MUSC test case (e.g., `REFL65`).

---

## Tips

- **Use absolute paths.** All `path` fields must be absolute (starting with `/`). Relative paths are not supported.
- **Keep `experiment.name` short and alphanumeric.** It appears in directory names and SLURM job names.
- **Never share `scratch_hm_home` between two experiments with the same `name`.** The pipeline will silently overwrite outputs.
- **Check `ura_env` first.** If the URANIE environment file cannot be sourced, `RunUranie` will fail at runtime. Ask your system administrator for the correct path.
