# Morris Sensitivity Analysis

This is the **default** analysis mode in UranieMUSC. It uses the **Morris Elementary Effects** method to screen which namelist parameters have the largest influence on MUSC forecast output.

---

## What is the Morris method?

The Morris method is a global sensitivity screening technique. "Global" means it explores the full range of each parameter, not just the behaviour near a single reference point.

The idea is simple:

1. Start from a random point in parameter space.
2. Change one parameter at a time by a fixed step and record how much the model output changes. This change is called an **elementary effect**.
3. Repeat from different starting points (called **trajectories**) to capture non-linear behaviour and interactions.
4. Average the elementary effects across all trajectories to get a sensitivity measure for each parameter: **μ*** (mean absolute effect) and **σ** (standard deviation, indicating non-linearity or interactions).

Parameters with large **μ*** are the most influential. Parameters with large **σ** have non-linear behaviour or interact strongly with other parameters.

The Morris method is designed to be **cheap**: it requires only `trajectories × (k + 1)` model runs, where `k` is the number of parameters. For 5 trajectories and 1 parameter, that is just 10 MUSC runs.

---

## How UranieMUSC implements it

The Morris analysis is driven by two files:

- **`uranmusc/doe_sensitivity.py`** — the URANIE Python script that sets up and runs the Morris DOE.
- **`nam/doe_musc_sensitivity.yml`** — the configuration file that tells the script which parameters to perturb and over what ranges.

These are selected in `config.yml`:

```yaml
experiment:
  ura_init: uranmusc/doe_sensitivity.py
  ura_init_namelist: nam/doe_musc_sensitivity.yml
```

---

## The `doe_musc_sensitivity.yml` file

```yaml
data_files:
    dataserver: init_doe.dat
    namelist_template: namelist_atm_DEF

variables:
    inputs: ["VSIGQSAT"]
    minima: [0.01]
    maxima: [0.5]
    namelist_flags: ["@VSIGQSAT@"]

doe:
    trajectories: 5
    levels: 20
```

### `data_files`

| Field | Description |
|---|---|
| `dataserver` | Filename of the URANIE output dataserver. Saved to `<uranie_dir>/init_doe.dat`. |
| `namelist_template` | Name of the namelist file to be patched with `@VAR@` tokens. Must match `<musc_id>` in `config.yml`. |

### `variables`

| Field | Description |
|---|---|
| `inputs` | List of namelist parameter names to perturb (must exist in the namelist). |
| `minima` | Lower bound for each parameter (same order as `inputs`). |
| `maxima` | Upper bound for each parameter (same order as `inputs`). |
| `namelist_flags` | URANIE token string for each parameter. By convention `@VARNAME@`. Must match what `RunUranie` substitutes into the namelist. |

### `doe`

| Field | Description |
|---|---|
| `trajectories` | Number of Morris trajectories. More trajectories give more stable sensitivity estimates but require more model runs. Typical values: 5–20. |
| `levels` | Number of grid levels for the parameter range. Controls the resolution of the elementary effects. Typical value: 20. |

**Number of MUSC runs** = `trajectories × (len(inputs) + 1)`.
For the default config: `5 × (1 + 1) = 10` runs.

---

## Interpreting the URANIE dataserver

After `RunUranie` completes, the file `URANIE/init_doe.dat` contains a table of all sampled parameter values. You can inspect it with URANIE's ROOT-based tools, or read it with a custom Python script using the ROOT `TTree` interface.

Each row corresponds to one `UranieLauncher_N` directory, and therefore one MUSC run. The column named after your input parameter (e.g., `VSIGQSAT`) gives the exact value used in that run.

---

## Adjusting the sampling

To change the number of trajectories or the parameter range, edit `doe_musc_sensitivity.yml` and re-run from `RunUranie`:

```shell
uv run uranmusc RunUranie --rerun --local-scheduler
```

This regenerates all perturbed namelists without re-running the expensive Harmonie build. `RunMusc` and `ConvertLFAToNetCDF` will then re-run automatically because their upstream inputs changed.

To add more parameters to the sensitivity analysis, see {doc}`add_parameter`.
