# Installation

This installation guide of UranieMUSC is targeted the **ECMWF ATOS** HPC system. Please make sure to meet the below pre-requisites before installing.

## Prerequisites

- **Python 3.10 – 3.12** (available via the `python3/3.10.10-01` module on ATOS).
- **[uv](https://docs.astral.sh/uv/)** — a fast Python package manager. Install it once with:

  ```shell
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

- Access to the ECMWF `ecmwf-toolbox` module (provides ecFlow and related libraries).

## Steps

**1. Clone the repository**

```shell
git clone git@github.com:<FORK_NAME>/UranieMUSC.git
cd UranieMUSC
```

Replace `<FORK_NAME>` with the name of your fork of [UranieMUSC](https://github.com/ACCORD-NWP/UranieMUSC).

**2. Load the required modules**

```shell
module load ecmwf-toolbox
module load python3/3.10.10-01
```

**3. Create the virtual environment and install dependencies**

```shell
uv venv --system-site-packages
uv sync --all-extras
```

The `--system-site-packages` flag makes the system Python packages (including the ECMWF toolbox libraries) available inside the virtual environment.

**4. Install pre-commit hooks** (required, for contributors only)

```shell
uv run pre-commit install
```

## Verifying the installation

After a successful install you should be able to run:

```shell
uv run uranmusc --help
```

and see the list of available commandline arguments printed to the terminal.

## Building the documentation

With the dev dependencies installed (`uv sync --all-extras`), execute the command

```shell
uv run jupyter-book build docs/
```
to build the documentation.
