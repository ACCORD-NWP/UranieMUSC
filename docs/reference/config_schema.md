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
| `grp` | `str` | no | Unix group name for directory ownership. Omit to skip permission management. |

**Derived paths** (auto-created, not set by user):

| Property | Formula |
|---|---|
| `home_exp_dir` | `hm_home / experiment.name` |
| `scratch_exp_dir` | `scratch_hm_home / experiment.name` |
| `uranie_dir` | `scratch_exp_dir / "URANIE"` |
| `output_dir` | `scratch_exp_dir / "OUTPUT"` |

---

## `experiment`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | `str` | yes | Experiment identifier. Used as subdirectory name. |
| `fc_length` | `int` | yes | Forecast length in hours. |
| `musc_id` | `str` | yes | MUSC configuration label (e.g., `DEF`). |
| `musc_case` | `str` | yes | MUSC test case name (e.g., `REFL65`). |
| `ura_init` | `Path` | yes | Path to the URANIE Python script (`doe_sensitivity.py` or `doe.py`). |
| `ura_init_namelist` | `Path` | yes | Path to the URANIE DOE configuration YAML. |

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
