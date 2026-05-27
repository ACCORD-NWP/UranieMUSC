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

The Morris analysis is configured entirely within `config.yml` under the `experiment.design_of_experiment` block. Set `type: morris_sensitivity` and supply the Morris-specific fields (`trajectories` and `levels`):

```yaml
experiment:
  name: Test5
  fc_length: 6
  musc_id: DEF
  musc_case: REFL65
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
```

`RunUranie` reads this block, patches the namelist, and calls `design_of_experiment.py` with the Morris strategy.

---

## Configuration fields

### `data_files`

| Field | Description |
|---|---|
| `dataserver` | Filename of the URANIE output dataserver. Saved to `<uranie_dir>/init_doe.dat`. |
| `namelist_template` | Base name for the namelist. The pipeline appends `_atm_<musc_id>` to form the actual filename (e.g., `namelist_atm_DEF`). |

### `variables`

| Field | Description |
|---|---|
| `inputs` | List of namelist parameter names to perturb (must exist in the namelist). |
| `minima` | Lower bound for each parameter (same order as `inputs`). |
| `maxima` | Upper bound for each parameter (same order as `inputs`). |
| `namelist_flags` | URANIE token string for each parameter. By convention `@VARNAME@`. Must match what `RunUranie` substitutes into the namelist. |

### `doe` (Morris-specific)

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

To change the number of trajectories or the parameter range, edit the `design_of_experiment` block in `config.yml` and re-run from `RunUranie`:

```shell
uv run uranmusc RunUranie --rerun-task --local-scheduler
```

This regenerates all perturbed namelists without re-running the expensive Harmonie build.

To add more parameters to the sensitivity analysis, see {doc}`add_parameter`.
