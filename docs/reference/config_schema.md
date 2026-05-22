# Configuration Schema

This page is the compact machine-readable reference for `config.yml`. For narrative explanations and usage tips, see {doc}`../configuration`.

---

## Top-level structure

```
config.yml
├── general          (required)
├── experiment       (required)
└── git_repos        (required)
    ├── harmonie     (required)
    ├── ddhtoolbox   (required)
    └── musc_data    (required)
```

---

## `general`

| Field | Type | Required | Description |
|---|---|---|---|
| `ura_env` | `Path` | yes | Path to the shell script that activates URANIE. Sourced before any URANIE invocation. |
| `musc_data_dir` | `Path` | yes | Directory containing reference MUSC initial/boundary condition data. |
| `hm_home` | `Path` | yes | Permanent home directory for Harmonie experiment setups. |
| `scratch_hm_home` | `Path` | yes | Scratch filesystem directory for active experiment runs. |
| `bin_dir` | `Path` | no | Pre-built Harmonie binary directory. When set, `BuildExperiment` skips compilation (`BUILD=no`). |
| `grp` | `str` | no | Unix group name for directory ownership. Omit to skip permission management. |

**Derived paths** (auto-created, not set by user):

| Property | Formula |
|---|---|
| `home_exp_dir` | `hm_home / experiment.name` |
| `scratch_exp_dir` | `scratch_hm_home / experiment.name` |
| `uranie_dir` | `scratch_exp_dir / "URANIE"` |
| `output_dir` | `scratch_exp_dir / "OUTPUT"` |
| `project_dir` | *(UranieMUSC package root)* |
| `namelist_atm` | `home_exp_dir / "<namelist_template>_atm_<musc_id>"` (or inside `namelist_dir` when set) |
| `namelist_sfx` | `home_exp_dir / "<namelist_template>_sfx_<musc_id>"` (or inside `namelist_dir` when set) |

---

## `experiment`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | `str` | yes | Experiment identifier. Used as subdirectory name. |
| `fc_length` | `int` | yes | Forecast length in hours. |
| `musc_id` | `str` | yes | MUSC configuration label (e.g., `DEF`). |
| `musc_case` | `str` | yes | MUSC test case name (e.g., `REFL65`). |
| `design_of_experiment` | `DesignOfExperimentConfig` | yes | Inline DOE configuration. See below. |

---

## `DesignOfExperimentConfig`

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | `"morris_sensitivity" \| "sampling"` | yes | DOE method to use. |
| `data_files` | `DataFilesConfig` | yes | Filenames for URANIE inputs/outputs. |
| `variables` | `VariablesConfig` | yes | Parameters to perturb and their ranges. |
| `trajectories` | `int` | Morris only | Number of Morris trajectories. |
| `levels` | `int` | Morris only | Number of grid levels for discretisation. |
| `sample_size` | `int` | LHS only | Number of LHS samples. |
| `distribution` | `str` | LHS only | Must be `"lhs"`. |

Extra fields are passed through to the URANIE script and ignored by Pydantic validation.

---

## `DataFilesConfig`

| Field | Type | Required | Description |
|---|---|---|---|
| `dataserver` | `Path` | yes | Filename of the URANIE dataserver output (e.g., `init_doe.dat`). Written to `uranie_dir`. |
| `namelist_template` | `str` | yes | Base name for namelist files. The pipeline appends `_atm_<musc_id>` and `_sfx_<musc_id>`. |
| `namelist_dir` | `Path` | no | If set, namelists are copied from `<namelist_dir>/<musc_case>/` instead of being generated. |

---

## `VariablesConfig`

All lists must have the same length `k`.

| Field | Type | Required | Description |
|---|---|---|---|
| `inputs` | `list[str]` | yes | Namelist parameter names (verbatim). |
| `namelist_flags` | `list[str]` | yes | URANIE token strings. Each must be of the form `@VARNAME@`. |
| `minima` | `list[float]` | yes (extra) | Lower bounds, one per parameter. |
| `maxima` | `list[float]` | yes (extra) | Upper bounds, one per parameter. |

(`minima` and `maxima` are extra fields; Pydantic passes them through to the DOE strategy.)

---

## `git_repos.<repo>`

Applies to each of `harmonie`, `ddhtoolbox`, `musc_data`.

| Field | Type | Required | Description |
|---|---|---|---|
| `repo` | `Path` | yes | Local path where the repository is cloned. |
| `url` | `str` | yes | Remote git URL used for cloning. |
| `branch` | `str` | yes | Branch to check out (`--single-branch --branch`). |

---

## Validation

The configuration is validated at startup by [Pydantic v2](https://docs.pydantic.dev/). Validation errors are reported before any task runs. Common errors:

| Error | Cause |
|---|---|
| `value is not a valid path` | A `Path` field contains an invalid string. |
| `field required` | A required field is missing from `config.yml`. |
| `Input should be a valid integer` | `fc_length` was given as a string (e.g., `"6"` instead of `6`). |
| `Input should be 'morris_sensitivity' or 'sampling'` | `design_of_experiment.type` has an unrecognised value. |
