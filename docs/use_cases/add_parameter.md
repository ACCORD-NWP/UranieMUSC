# Adding a New Parameter

This page shows how to extend the sensitivity analysis or LHS ensemble to include additional namelist parameters. No Python code changes are required — only the `design_of_experiment` block in `config.yml` needs editing.

The steps are the same whether you are using the Morris method (`type: morris_sensitivity`) or LHS (`type: sampling`).

---

## Prerequisites

Before adding a parameter, you need to know:

1. **The exact namelist parameter name** as it appears in `namelist_atm_<musc_id>`. For example, `VSIGQSAT`.
2. **A physically reasonable range** `[min, max]` for the parameter.

You can find parameter names by inspecting the generated namelist:

```shell
cat <hm_home>/<experiment.name>/namelist_atm_DEF
```

---

## Step 1: Edit `config.yml`

Open `config.yml` and add your parameter to the four lists under `experiment.design_of_experiment.variables`. The order must be consistent across all four lists.

**Example: adding `XLCOR` alongside the existing `VSIGQSAT`**

Before:

```yaml
experiment:
  design_of_experiment:
    variables:
      inputs: ["VSIGQSAT"]
      minima: [0.01]
      maxima: [0.5]
      namelist_flags: ["@VSIGQSAT@"]
```

After:

```yaml
experiment:
  design_of_experiment:
    variables:
      inputs: ["VSIGQSAT", "XLCOR"]
      minima: [0.01, 100000]
      maxima: [0.5,  300000]
      namelist_flags: ["@VSIGQSAT@", "@XLCOR@"]
```

Rules:
- `inputs`, `minima`, `maxima`, and `namelist_flags` must all have the same length.
- Each `namelist_flags` entry must be a unique token string of the form `@VARNAME@`.
- The parameter name in `inputs` must appear verbatim in the `namelist_atm_<musc_id>` file.

---

## Step 2: Update the number of runs (Morris only)

If you are using the Morris method, be aware that adding parameters **increases the number of MUSC runs**:

```
runs = trajectories × (len(inputs) + 1)
```

For 5 trajectories and 2 parameters: `5 × 3 = 15` runs.

You can adjust `trajectories` in the `design_of_experiment` block to control total cost:

```yaml
experiment:
  design_of_experiment:
    trajectories: 5    # keep as-is, or reduce if 15 runs is too many
    levels: 20
```

For LHS, the number of runs is always `sample_size` regardless of the number of parameters.

---

## Step 3: Re-run from `RunUranie`

The Harmonie build and MUSC namelist generation do not need to be redone. Re-run from `RunUranie`:

```shell
uv run uranmusc RunUranie --rerun-task --local-scheduler
```

Luigi will:
1. Re-patch the namelist to insert `@VSIGQSAT@` and `@XLCOR@` tokens.
2. Re-run the URANIE DOE script to generate new perturbed namelists.

---

## What changes on disk

The `URANIE/UranieLauncher_*` directories are recreated with updated namelists. For the example above, each namelist will contain both parameters substituted:

```
VSIGQSAT= 0.23 ,
XLCOR= 127000 ,
```

The dataserver file (`init_doe.dat`) will gain an additional column for `XLCOR`.

---

## Verifying the namelist was patched correctly

After `RunUranie` completes, inspect one of the generated namelists to confirm both parameters were substituted:

```shell
grep -E "VSIGQSAT|XLCOR" <scratch_hm_home>/<name>/URANIE/UranieLauncher_0/namelist_atm_DEF
```

You should see concrete numerical values (not the `@...@` token strings).
