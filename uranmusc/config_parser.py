"""Configuration parser for UranMusc using pydantic."""

import os
import shutil
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, computed_field, model_validator


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
    ura_init_namelist: Path


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
