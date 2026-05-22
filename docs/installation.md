# Installation

UranieMUSC is designed to run on the **ECMWF ATOS** HPC system. The steps below give a concise summary; the [full instructions including system requirements](https://github.com/ACCORD-NWP/UranieMUSC#installation) are maintained in the repository README.

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

**4. Install pre-commit hooks** (optional, recommended for contributors)

```shell
uv run pre-commit install
```

## Verifying the installation

After a successful install you should be able to run:

```shell
uv run uranmusc --help
```

and see the list of available tasks printed to the terminal.

## Building the documentation

With the dev dependencies installed (`uv sync --all-extras`), build these docs locally with:

```shell
uv run jupyter-book build docs/
```

The rendered HTML will appear in `docs/_build/html/`.
