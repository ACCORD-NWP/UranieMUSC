import argparse
from abc import ABC, abstractmethod
from pathlib import Path

import yaml
from loguru import logger
from rootlogon import DataServer, Launcher, Sampler, Sensitivity

from uranmusc.config_parser import DesignOfExperimentConfig


def parse_doe_config(doe_config):
    """Parse DOE configuration from dict and return pydantic model.

    Args:
        doe_config: Dict containing the design of experiment configuration

    Returns:
        DesignOfExperimentConfig pydantic model
    """
    if isinstance(doe_config, dict):
        config = DesignOfExperimentConfig(**doe_config)
    elif isinstance(doe_config, DesignOfExperimentConfig):
        config = doe_config
    else:
        raise TypeError("doe_config must be a dict or DesignOfExperimentConfig")

    return config


class DOEStrategy(ABC):
    """Base class for Design of Experiment strategies."""

    @abstractmethod
    def get_required_keys(self):
        """Return list of required configuration keys for this DOE type."""
        pass

    @abstractmethod
    def create_sampler(self, ds, config, dummy_model=None):
        """Create and return the appropriate sampler for this DOE type.

        Args:
            ds: URANIE DataServer
            config: DesignOfExperimentConfig pydantic model
            dummy_model: Optional dummy model for strategies that need it
        """
        pass

    @abstractmethod
    def validate_settings(self, config):
        """Validate that all required settings are present.

        Args:
            config: DesignOfExperimentConfig pydantic model
        """
        pass


class SamplingDOE(DOEStrategy):
    """Traditional sampling-based Design of Experiment using TSampling."""

    def get_required_keys(self):
        return ["sample_size", "distribution"]

    def validate_settings(self, config):
        missing_keys = []
        for key in self.get_required_keys():
            # Check if key exists in the extra fields
            if not hasattr(config, key) and key not in config.__pydantic_extra__:
                missing_keys.append(key)
            else:
                value = getattr(config, key, None) or config.__pydantic_extra__.get(key)
                if not value:
                    missing_keys.append(key)
        if missing_keys:
            raise KeyError(f"Following keys are missing for Sampling DOE: {missing_keys}")

    def create_sampler(self, ds, config, dummy_model=None):
        # Access doe parameters from config extra fields or nested doe dict
        distribution = getattr(
            config, "distribution", None
        ) or config.__pydantic_extra__.get("distribution")
        sample_size = getattr(
            config, "sample_size", None
        ) or config.__pydantic_extra__.get("sample_size")
        return Sampler.TSampling(ds, distribution, sample_size)


class MorrisSensitivityDOE(DOEStrategy):
    """Morris sensitivity analysis Design of Experiment using TMorris."""

    def get_required_keys(self):
        return ["trajectories", "levels"]

    def validate_settings(self, config):
        missing_keys = []
        for key in self.get_required_keys():
            # Check if key exists in the extra fields
            if not hasattr(config, key) and key not in config.__pydantic_extra__:
                missing_keys.append(key)
            else:
                value = getattr(config, key, None) or config.__pydantic_extra__.get(key)
                if not value:
                    missing_keys.append(key)
        if missing_keys:
            raise KeyError(
                f"Following keys are missing for Morris Sensitivity DOE: {missing_keys}"
            )

    def create_sampler(self, ds, config, dummy_model=None):
        if dummy_model is None:
            raise ValueError("Morris sensitivity analysis requires a dummy_model")

        # Access Morris parameters from config extra fields
        trajectories = getattr(
            config, "trajectories", None
        ) or config.__pydantic_extra__.get("trajectories")
        levels = getattr(config, "levels", None) or config.__pydantic_extra__.get(
            "levels"
        )

        return Sensitivity.TMorris(ds, dummy_model, trajectories, levels)


class DOEFactory:
    """Factory for creating appropriate DOE strategy based on configuration."""

    _strategies = {
        "sampling": SamplingDOE,
        "morris_sensitivity": MorrisSensitivityDOE,
    }

    @classmethod
    def register_strategy(cls, name, strategy_class):
        """Register a new DOE strategy."""
        if not issubclass(strategy_class, DOEStrategy):
            raise ValueError("Strategy must inherit from DOEStrategy")
        cls._strategies[name] = strategy_class

    @classmethod
    def create_strategy(cls, doe_type):
        """Create a DOE strategy instance based on the type."""
        if doe_type not in cls._strategies:
            available = ", ".join(cls._strategies.keys())
            raise ValueError(
                f"Unknown DOE type: {doe_type}. Available types: {available}"
            )
        return cls._strategies[doe_type]()

    @classmethod
    def list_strategies(cls):
        """List all available DOE strategies."""
        return list(cls._strategies.keys())


def run_doe(doe_config: Path, output_dir: Path, namelist_dir=None):
    """Main function to run Design of Experiment.

    Args:
        doe_config: Path to YAML file with DOE configuration
        output_dir: Directory to export the dataserver
        namelist_dir: Directory containing the namelist template (optional, inferred from config if not provided)
    """

    # Load from YAML file for backward compatibility
    with open(doe_config, "r", encoding="utf-8") as file:
        config_dict = yaml.safe_load(file)
    config = parse_doe_config(config_dict)
    if namelist_dir is None:
        namelist_dir = doe_config.parent

    doe_type = config.type
    logger.info(f"Using DOE type: {doe_type}")

    # Create appropriate strategy
    strategy: DOEStrategy = DOEFactory.create_strategy(doe_type)
    strategy.validate_settings(config)

    # 1. Create the URANIE dataserver
    ds = DataServer.TDataServer("tds", "Design of Experiment")
    variables = config.variables
    for i, var in enumerate(variables.inputs):
        # Access minima, maxima, and namelist_flags from the VariablesConfig
        minima = variables.__pydantic_extra__.get("minima", [])[i]
        maxima = variables.__pydantic_extra__.get("maxima", [])[i]
        flag = variables.namelist_flags[i]

        ds.addAttribute(DataServer.TUniformDistribution(var, minima, maxima))
        ds.getAttribute(var).setFileFlag(
            str(namelist_dir / config.data_files.namelist_template),
            flag,
        )

    # 2. Create the Dummy model
    dummy_model = Launcher.TCode(ds, "echo Running dummy model; echo OK | cat > out.dat")
    output_file = Launcher.TOutputFileKey("out.dat")
    dummy_model.addOutputFile(output_file)

    # 3. Create samples using the selected strategy
    sampler = strategy.create_sampler(ds, config, dummy_model)
    sampler.generateSample()

    # 4. Create Launcher and run the model
    launcher = Launcher.TLauncher(ds, dummy_model)
    launcher.setSave()
    launcher.setClean()
    launcher.run()

    # 5. Export the dataserver
    output_dir.mkdir(exist_ok=True)
    ds.exportData(str(output_dir / config.data_files.dataserver))
    logger.info("DOE completed successfully")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run Design of Experiment from a YAML config file."
    )
    parser.add_argument(
        "doe_config", type=Path, help="Path to the DOE YAML configuration file"
    )
    parser.add_argument(
        "--output-dir", type=Path, help="Directory to export the dataserver"
    )
    parser.add_argument(
        "--namelist-dir",
        type=Path,
        default=None,
        help=(
            "Directory containing the namelist template "
            "(default: inferred from doe_config path)"
        ),
    )
    args = parser.parse_args()

    run_doe(args.doe_config, output_dir=args.output_dir, namelist_dir=args.namelist_dir)
