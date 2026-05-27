# Latin Hypercube Sampling

As an alternative to the {doc}`Morris sensitivity analysis <sensitivity_morris>`, UranieMUSC can generate parameter samples using **Latin Hypercube Sampling (LHS)**. LHS is useful when you want to build an ensemble of MUSC runs that uniformly covers the parameter space, for example to train a statistical emulator or to estimate output uncertainty.

---

## What is Latin Hypercube Sampling?

LHS is a stratified random sampling strategy. The range of each parameter is divided into `n` equally-sized intervals, and exactly one sample is drawn from each interval. The resulting set of `n` sample points covers the parameter space more evenly than simple random sampling.

---

## Configuration

To switch from Morris to LHS, set `type: sampling` in the `design_of_experiment` block and replace the Morris-specific fields (`trajectories`, `levels`) with the LHS-specific ones (`sample_size`, `distribution`):

```yaml
experiment:
  name: Test5
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
    sample_size: 20        # number of LHS samples
    distribution: lhs
```

### `doe` block (LHS-specific fields)

| Field | Description |
|---|---|
| `sample_size` | Number of LHS samples to generate. Each sample produces one MUSC run. |
| `distribution` | Sampling distribution. Set to `"lhs"` for Latin Hypercube Sampling. |

The `variables` block has the same structure as in the Morris configuration. See {doc}`sensitivity_morris` for a field-by-field description.

---

## Running with LHS

After editing `config.yml`:

```shell
uv run uranmusc Run --local-scheduler
```

If Harmonie is already built from a previous run, Luigi will skip `CloneRepos`, `SetupExperiment`, `BuildExperiment`, `SetupMusc`, and `SetupMuscNamelists` (their outputs still exist) and run only `RunUranie`, `RunMusc`, and `ConvertLFAToNetCDF`.

To force `RunUranie` to regenerate the samples (e.g., after changing `sample_size`):

```shell
uv run uranmusc RunUranie --rerun-task --local-scheduler
```

---

## Comparison: Morris vs. LHS

| | Morris | LHS |
|---|---|---|
| **Goal** | Rank parameters by influence | Uniform space-filling ensemble |
| **Runs needed** | `trajectories × (k + 1)` | `sample_size` (user-chosen) |
| **Output** | Sensitivity indices (μ*, σ) | Ensemble of MUSC outputs |
| **`type` value** | `morris_sensitivity` | `sampling` |
