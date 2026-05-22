# Adding a New Parameter

This page shows how to extend the sensitivity analysis or LHS ensemble to include additional namelist parameters. No Python code changes are required — only the YAML configuration file needs editing.

The steps are the same whether you are using the Morris method (`doe_musc_sensitivity.yml`) or LHS (`doe.yml`).

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

## Step 1: Edit the namelist YAML file

Open `nam/doe_musc_sensitivity.yml` (or `nam/doe.yml` for LHS) and add your parameter to the four lists under `variables`. The order must be consistent across all four lists.

**Example: adding `RPRCONV` alongside the existing `VSIGQSAT`**

Before:

```yaml
variables:
    inputs: ["VSIGQSAT"]
    minima: [0.01]
    maxima: [0.5]
    namelist_flags: ["@VSIGQSAT@"]
```

After:

```yaml
variables:
    inputs: ["VSIGQSAT", "RPRCONV"]
    minima: [0.01, 0.001]
    maxima: [0.5,  0.05]
    namelist_flags: ["@VSIGQSAT@", "@RPRCONV@"]
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

You can adjust `trajectories` in the `doe` block to control total cost:

```yaml
doe:
    trajectories: 5    # keep as-is, or reduce if 15 runs is too many
    levels: 20
```

For LHS, the number of runs is always `sample_size` regardless of the number of parameters.

---

## Step 3: Re-run from `RunUranie`

The Harmonie build and MUSC namelist generation do not need to be redone. Re-run from `RunUranie`:

```shell
uv run uranmusc RunUranie --rerun --local-scheduler
```

Luigi will:
1. Re-patch the namelist to insert `@VSIGQSAT@` and `@RPRCONV@` tokens.
2. Re-run the URANIE DOE script to generate new perturbed namelists.
3. Automatically continue with `RunMusc` and `ConvertLFAToNetCDF`.

---

## What changes on disk

The `URANIE/UranieLauncher_*` directories are recreated with updated namelists. For the example above, each namelist will contain both parameters substituted:

```
VSIGQSAT= 0.23 ,
RPRCONV= 0.018 ,
```

The dataserver file (`init_doe.dat`) will gain an additional column for `RPRCONV`.

---

## Verifying the namelist was patched correctly

After `RunUranie` completes, inspect one of the generated namelists to confirm both parameters were substituted:

```shell
grep -E "VSIGQSAT|RPRCONV" <scratch_hm_home>/<name>/URANIE/UranieLauncher_0/namelist_atm_DEF
```

You should see concrete numerical values (not the `@...@` token strings).
