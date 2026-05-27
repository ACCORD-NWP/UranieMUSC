# Design of Experiment Configuration Reference

The DOE (design of experiment) configuration is specified **inline** in `config.yml`, under the `experiment.design_of_experiment` key. There is no separate YAML file.

This page gives the complete schema. For context on how the configuration is used, see {doc}`../use_cases/sensitivity_morris` and {doc}`../use_cases/lhs_sampling`.

---

## Schema

```yaml
experiment:
  design_of_experiment:
    type: <"morris_sensitivity" | "sampling">   # required

    data_files:
      dataserver: <string>           # required
      namelist_template: <string>    # required
      namelist_dir: <path>           # optional

    variables:
      inputs: [<string>, ...]        # required, length k >= 1
      minima: [<number>, ...]        # required, length k
      maxima: [<number>, ...]        # required, length k
      namelist_flags: [<string>, ...]  # required, length k

    # Morris method fields (use when type: morris_sensitivity):
    trajectories: <int>              # required for Morris
    levels: <int>                    # required for Morris

    # LHS fields (use when type: sampling):
    sample_size: <int>               # required for LHS
    distribution: <string>           # required for LHS, must be "lhs"
```

---

## `type`

| Value | Description |
|---|---|
| `morris_sensitivity` | Morris Elementary Effects method. Also requires `trajectories` and `levels`. |
| `sampling` | Latin Hypercube Sampling. Also requires `sample_size` and `distribution`. |

---

## `data_files`

| Field | Type | Description |
|---|---|---|
| `dataserver` | string | Filename of the URANIE output dataserver file. Written to `<uranie_dir>/`. Example: `init_doe.dat`. |
| `namelist_template` | string | Base name for namelist files. The pipeline appends `_atm_<musc_id>` and `_sfx_<musc_id>` to form the actual filenames. Example: `namelist` → `namelist_atm_DEF`, `namelist_sfx_DEF`. |
| `namelist_dir` | path (optional) | If set, `SetupMuscNamelists` copies pre-existing namelist files from `<namelist_dir>/<musc_case>/` instead of generating them with `musc_namelist.sh`. |

---

## `variables`

All four lists must have the same length `k` (one entry per perturbed parameter). The i-th entry in each list refers to the same parameter.

| Field | Type | Description |
|---|---|---|
| `inputs` | list of strings | Namelist parameter names exactly as they appear in the namelist file. Example: `["VSIGQSAT", "XLCOR"]`. |
| `minima` | list of numbers | Lower bound for each parameter. Example: `[0.01, 100000]`. |
| `maxima` | list of numbers | Upper bound for each parameter. Example: `[0.5, 300000]`. |
| `namelist_flags` | list of strings | URANIE token strings. Each token is inserted into the namelist template by `RunUranie` in place of the parameter's default value. Convention: `@VARNAME@`. Example: `["@VSIGQSAT@", "@XLCOR@"]`. |

---

## `doe` — Morris method

Used when `type: morris_sensitivity`.

| Field | Type | Description |
|---|---|---|
| `trajectories` | int | Number of Morris trajectories. Total MUSC runs = `trajectories × (k + 1)`. Typical range: 5–20. |
| `levels` | int | Number of grid levels for parameter discretisation. Controls the resolution of elementary effects. Typical value: 20. |

---

## `doe` — Latin Hypercube Sampling

Used when `type: sampling`.

| Field | Type | Description |
|---|---|---|
| `sample_size` | int | Number of LHS samples to generate. Equals the total number of MUSC runs. |
| `distribution` | string | Must be `"lhs"`. |

---

## Complete examples

### Morris sensitivity analysis (2 parameters)

```yaml
experiment:
  name: TestExperiment
  fc_length: 6
  musc_id: DEF
  musc_case: REFL65
  design_of_experiment:
    type: morris_sensitivity
    data_files:
      dataserver: init_doe.dat
      namelist_template: namelist
    variables:
      inputs: ["VSIGQSAT", "XLCOR"]
      minima: [0.01, 100000]
      maxima: [0.5,  300000]
      namelist_flags: ["@VSIGQSAT@", "@XLCOR@"]
    trajectories: 10
    levels: 20
```

Total MUSC runs: `10 × (2 + 1) = 30`.

### Latin Hypercube Sampling (1 parameter, 50 samples)

```yaml
experiment:
  name: TestExperiment
  fc_length: 6
  musc_id: DEF
  musc_case: REFL65
  design_of_experiment:
    type: sampling
    data_files:
      dataserver: init_doe.dat
      namelist_template: namelist
    variables:
      inputs: ["VSIGQSAT"]
      minima: [0.01]
      maxima: [0.5]
      namelist_flags: ["@VSIGQSAT@"]
    sample_size: 50
    distribution: lhs
```

Total MUSC runs: 50.
