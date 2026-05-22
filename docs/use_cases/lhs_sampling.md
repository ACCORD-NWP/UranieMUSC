# Latin Hypercube Sampling

As an alternative to the {doc}`Morris sensitivity analysis <sensitivity_morris>`, UranieMUSC can generate parameter samples using **Latin Hypercube Sampling (LHS)**. LHS is useful when you want to build an ensemble of MUSC runs that uniformly covers the parameter space, for example to train a statistical emulator or to estimate output uncertainty.

---

## What is Latin Hypercube Sampling?

LHS is a stratified random sampling strategy. The range of each parameter is divided into `n` equally-sized intervals, and exactly one sample is drawn from each interval. The resulting set of `n` sample points covers the parameter space more evenly than simple random sampling.

Unlike the Morris method, LHS does not provide a sensitivity ranking — it is a sampling strategy, not a sensitivity analysis method. Use it when you want:

- A space-filling ensemble for uncertainty quantification.
- Input for training a surrogate/emulator model.
- A controlled set of runs to explore the parameter space.

---

## Configuration

To switch from Morris to LHS, make two changes in `config.yml`:

```yaml
experiment:
  ura_init: uranmusc/doe.py                # switch to the LHS script
  ura_init_namelist: nam/doe.yml           # switch to the LHS config file
```

---

## The `doe.yml` file

```yaml
data_files:
    dataserver: init_doe.dat
    namelist_template: namelist_atm_DEF   # adjust to match your musc_id

variables:
    inputs: ["VSIGQSAT"]
    minima: [0.01]
    maxima: [0.5]
    namelist_flags: ["@VSIGQSAT@"]

doe:
    sample_size: 20       # number of LHS samples
    distribution: "lhs"
```

The `variables` block has the same structure as in `doe_musc_sensitivity.yml`. See {doc}`sensitivity_morris` for a field-by-field description.

### `doe` block (LHS-specific fields)

| Field | Description |
|---|---|
| `sample_size` | Number of LHS samples to generate. Each sample produces one MUSC run. |
| `distribution` | Sampling distribution. Set to `"lhs"` for Latin Hypercube Sampling. |

:::{note}
The `nam/doe.yml` file that ships with the repository uses `namelist_template: harmonie_namelists.pm`, which is a different namelist format. Before using it for a standard MUSC run, update `namelist_template` to match your `musc_id` (e.g., `namelist_atm_DEF`).
:::

---

## Running with LHS

After editing `config.yml` and `doe.yml`:

```shell
uv run uranmusc Run --local-scheduler
```

If Harmonie is already built from a previous run, Luigi will skip `CloneRepos`, `SetupExperiment`, `BuildExperiment`, and `SetupMusc` (their outputs still exist) and run only `RunUranie`, `RunMusc`, and `ConvertLFAToNetCDF`.

To force `RunUranie` to regenerate the samples (e.g., after changing `sample_size`):

```shell
uv run uranmusc RunUranie --rerun --local-scheduler
```

---

## Comparison: Morris vs. LHS

| | Morris | LHS |
|---|---|---|
| **Goal** | Rank parameters by influence | Uniform space-filling ensemble |
| **Runs needed** | `trajectories × (k + 1)` | `sample_size` (user-chosen) |
| **Output** | Sensitivity indices (μ*, σ) | Ensemble of MUSC outputs |
| **Config file** | `doe_musc_sensitivity.yml` | `doe.yml` |
| **Script** | `doe_sensitivity.py` | `doe.py` |
