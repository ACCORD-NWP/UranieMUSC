"""Module for setting up the experiment environment.

This module contains Luigi tasks for cleaning and configuring
the experiment directory.
"""
import logging
import shutil
import subprocess

import luigi

from uranmusc.pipeline.base import RerunBaseTask
from uranmusc.pipeline.pre import CloneRepos

# Use luigi logger interface set up in uranmusc/log.py
logger = logging.getLogger("luigi-interface")


class SetupExperiment(RerunBaseTask):
    """Luigi task to set up the experiment environment.

    Attributes:
        config (PydanticModelParameter): The experiment configuration.
    """

    def requires(self):
        """Specifies the dependencies for this task.

        Returns:
            list: A list of tasks that must be completed before this task.
        """
        return CloneRepos(rerun_all=self.rerun_all, config=self.config)

    def output(self):
        """Specifies the output target for this task.

        Returns:
            luigi.LocalTarget: A target file indicating the experiment is set up.
        """
        return luigi.LocalTarget(self.config.home_exp_dir / "config-sh")

    def run(self):
        """Executes the experiment setup.

        Cleans the experiment directory by removing non-essential directories,
        and then runs the Harmonie setup command.
        """
        logger.info("Cleaning up before setting up experiment")
        for path_ in self.config.home_exp_dir.iterdir():

            if path_ not in [
                self.config.output_dir,
                self.config.uranie_dir,
            ]:
                logger.debug("Removing path %s", path_)
                if path_.is_dir():
                    shutil.rmtree(path_, ignore_errors=True)
                else:
                    path_.unlink(missing_ok=True)

        logger.info(f"Setting up experiment {self.config.experiment.name}")
        logger.info(f"Using config\n{self.config}")
        subprocess.run(
            [
                str(self.config.git_repos.harmonie.repo / "config-sh/Harmonie"),
                "setup",
                "-r",
                str(self.config.git_repos.harmonie.repo),
                "-h",
                "ECMWF.atos",
            ],
            cwd=self.config.home_exp_dir,
            check=True,
        )
