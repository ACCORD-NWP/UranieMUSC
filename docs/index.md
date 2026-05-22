# UranieMUSC

**UranieMUSC** automates running the [MUSC](https://github.com/Hirlam/HarmonieMuscData) single-column model (SCM) inside the [URANIE](https://sourceforge.net/projects/uranie/) uncertainty quantification framework.

It is aimed at researchers who want to explore how sensitive MUSC forecasts are to the values of namelist parameters — for example when tuning parameterisation schemes or performing uncertainty quantification studies.

## What each component does

**MUSC** (Modèle Unifié Simple Colonne) is the single-column version of the ALARO/AROME numerical weather prediction model maintained by the ACCORD consortium. It runs the full atmospheric physics package at a single horizontal grid point, making it cheap enough to execute hundreds of times in a parameter study.

**URANIE** is a ROOT-based framework developed by CEA for uncertainty quantification, sensitivity analysis, and design of experiments. UranieMUSC uses it to generate sets of perturbed namelists — each representing one sample point in parameter space — before handing them off to MUSC.

**Harmonie** provides the build system, scripts, and namelist infrastructure needed to compile and configure MUSC on the target HPC system (ECMWF ATOS).

## How they fit together

```{figure} luigi_pipeline.png
:name: pipeline-diagram
:alt: UranieMUSC task dependency graph
:width: 80%

The UranieMUSC pipeline. Each box is a step that must complete before the next one can start. The pipeline is explained in detail in {doc}`pipeline/overview`.
```

The full workflow is:

1. Clone the required git repositories (Harmonie, DDH toolbox, MUSC data).
2. Set up and build a Harmonie experiment on ATOS.
3. Generate MUSC namelists from the built Harmonie code.
4. Use URANIE to produce a family of perturbed namelists (one per sample point).
5. Run MUSC once per perturbed namelist, in parallel on SLURM.
6. Convert the binary LFA output files to NetCDF.

## Quick start

1. Follow the {doc}`installation` instructions.
2. Edit `config.yml` — the {doc}`configuration` page explains every field.
3. Run the full pipeline:

```shell
uv run uranmusc Run --local-scheduler
```

For a guided walkthrough see {doc}`use_cases/full_run`.
