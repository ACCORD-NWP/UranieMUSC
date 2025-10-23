"""Configuration parser for UranMusc using pydantic."""

import os
import shutil
from pathlib import Path
from typing import List, Optional

import yaml
from pydantic import BaseModel, computed_field, field_validator, model_validator


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
    dataserver: Path
    namelist_dir: Optional[Path] = None
    namelist_template: Path


class VariablesConfig(BaseModel):
    inputs: List[str]
    minima: List[float]
    maxima: List[float]
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

    trajectories: Optional[int] = None
    levels: Optional[int] = None
    sample_size: Optional[str] = None
    distribution: Optional[str] = None
    data_files: DataFilesConfig
    variables: VariablesConfig

    def to_yaml(self, output_path: Path):
        model_dict = self.model_dump(mode="json", exclude_none=True)
        yaml.dump(model_dict, output_path)


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
    def namelist(self):
        doe = self.experiment.design_of_experiment
        if doe.data_files.namelist_dir is None:
            return self.home_exp_dir / doe.data_files.namelist_template
        return doe.data_files.namelist_dir / doe.data_files.namelist_template
