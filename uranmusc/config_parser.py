"""Configuration parser for UranMusc using pydantic."""

import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    computed_field,
    field_validator,
    model_validator,
)


class GeneralConfig(BaseModel):
    """General configuration."""

    ura_env: Path
    musc_data_dir: Path
    hm_home: Path
    scratch_hm_home: Path
    bin_dir: Optional[Path] = None
    grp: Optional[str] = None


class ExperimentConfig(BaseModel):
    """Experiment configuration."""

    name: str
    fc_length: int
    musc_id: str
    musc_case: str
    ura_init: Path
    design_of_experiment: "DesignOfExperimentConfig"

    # @model_validator(mode="after")
    # def check_musc_namelists(self):
    #     if (
    #         self.musc_namelists is not None
    #         and self.design_of_experiment.data_files.namelist_template is not None
    #     ):
    #         raise ValueError(
    #             "Cannot specify both musc_namelists and "
    #             "design_of_experiment.data_files.namelist_template"
    #         )
    #     if (
    #         self.musc_namelists is None
    #         and self.design_of_experiment.data_files.namelist_template is None
    #     ):
    #         raise ValueError(
    #             "Must specify either musc_namelists or "
    #             "design_of_experiment.data_files.namelist_template"
    #         )
    #     return self


class DataFilesConfig(BaseModel):
    # Any extra fields are allowed to support custom options for the data files.
    model_config = ConfigDict(extra="allow")

    dataserver: Path
    namelist_dir: Optional[Path] = None
    namelist_template: Path

    def __getitem__(self, key: str) -> Any:
        """Method to access both defined and extra fields."""
        if key in self.__class__.model_fields:
            return getattr(self, key)
        return self.__pydantic_extra__.get(key)


class VariablesConfig(BaseModel):
    # Any extra fields are allowed to support custom options for the variables
    # (e.g. minima/maxima, etc.)
    model_config = ConfigDict(extra="allow")

    inputs: List[str]
    namelist_flags: List[str]

    @field_validator("namelist_flags", mode="after")
    def check_namelist_flags(cls, value):
        """Check that all namelist flags start and end with '@'.

        Args:
            value (List[str]): List of namelist flags

        Raises:
            ValueError: If any namelist flag does not start and end with '@'

        Returns:
            List[str]: List of namelist flags
        """
        for flag in value:
            flag = flag.strip()
            if flag[0] != "@" and flag[-1] != "@":
                raise ValueError("All namelist flags must start and end with '@'")
        return value


class DesignOfExperimentConfig(BaseModel):
    """Design of experiment configuration."""

    # Any extra fields are allowed to support custom options for the design
    # of experiment (e.g. trajectories, levels, etc.)
    model_config = ConfigDict(extra="allow")

    data_files: DataFilesConfig
    variables: VariablesConfig

    def __getitem__(self, key: str) -> Any:
        """Method to access both defined and extra fields."""
        if key in self.__class__.model_fields:
            return getattr(self, key)
        return self.__pydantic_extra__.get(key)

    def to_yaml(self, output_path: Path):
        model_dict = self.model_dump(mode="json", exclude_none=True)
        with open(output_path, "w", encoding="utf-8") as file_:
            yaml.dump(model_dict, file_)


class GitRepositoryConfig(BaseModel):
    """Git repository configuration."""

    repo: Path
    url: str
    branch: str


class GitRepositoriesConfig(BaseModel):
    """Git repositories configuration."""

    harmonie: GitRepositoryConfig
    ddhtoolbox: GitRepositoryConfig
    musc_data: GitRepositoryConfig


class Config(BaseModel):
    """Main configuration."""

    general: GeneralConfig
    experiment: ExperimentConfig
    git_repos: GitRepositoriesConfig

    @model_validator(mode="after")
    def create_dirs(self):
        self.home_exp_dir.mkdir(parents=True, exist_ok=True)
        self.scratch_exp_dir.mkdir(parents=True, exist_ok=True)
        self.uranie_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set permissions for group if specified
        if self.general.grp:
            for path_ in [
                self.home_exp_dir,
                self.scratch_exp_dir,
                self.uranie_dir,
                self.output_dir,
            ]:
                shutil.chown(path_, group=self.general.grp)
                os.chmod(path_, 0o2750)

        return self

    @computed_field
    @property
    def home_exp_dir(self) -> Path:
        return self.general.hm_home / self.experiment.name

    @computed_field
    @property
    def scratch_exp_dir(self) -> Path:
        return self.general.scratch_hm_home / self.experiment.name

    @computed_field
    @property
    def uranie_dir(self) -> Path:
        return self.scratch_exp_dir / "URANIE"

    @computed_field
    @property
    def output_dir(self) -> Path:
        return self.scratch_exp_dir / "OUTPUT"

    @computed_field
    @property
    def namelist(self) -> Path:
        doe = self.experiment.design_of_experiment
        if doe.data_files.namelist_dir is None:
            # NOTE: The namelist files will be created in the SetupMuscNamelists
            # task and placed in the home experiment directory
            return self.home_exp_dir / doe.data_files.namelist_template
        return doe.data_files.namelist_dir / doe.data_files.namelist_template
