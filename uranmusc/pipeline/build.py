"""Module for building experiments and libraries.

This module contains Luigi tasks for building the Harmonie experiment
and installing the DDH library.
"""

import logging
import os
import subprocess
from pathlib import Path

import luigi

from uranmusc.ecflow_handles import await_ecflow_node_to_complete
from uranmusc.pipeline.base import RerunBaseTask
from uranmusc.pipeline.pre import CloneRepos
from uranmusc.pipeline.setup_experiment import SetupExperiment

# Use luigi logger interface set up in uranmusc/log.py
logger = logging.getLogger("luigi-interface")


class BuildExperiment(RerunBaseTask):
    """Luigi task to build the Harmonie experiment.

    Attributes:
        bin_dir (luigi.Parameter): Directory containing binaries. If provided, the experiment is installed without rebuilding.
    """

    bin_dir = luigi.Parameter(default=None)

    def requires(self):
        """Specifies the dependencies for this task.

        Returns:
            list: A list of tasks that must be completed before this task.
        """
        return SetupExperiment(rerun_all=self.rerun_all, config=self.config)

    def output(self):
        """Specifies the output target for this task.

        Returns:
            luigi.LocalTarget: A target file indicating the experiment is locked.
        """
        return luigi.LocalTarget(self.config.home_exp_dir / "experiment_is_locked")

    def run(self):
        """Executes the experiment build or installation.

        If `bin_dir` is provided and exists, it installs the experiment using
        the existing binaries. Otherwise, it runs the build command.
        """
        exp_name = self.config.experiment.name
        bin_dir = self.config.general.bin_dir
        if bin_dir is not None:
            bin_dir_path = Path(bin_dir).expanduser().absolute()
            if bin_dir_path.exists():
                logger.info(
                    f"Found build dir {bin_dir_path}. Install experiment in "
                    f"{self.config.scratch_exp_dir} without building."
                )
                os.environ["BUILD"] = "no"
                os.environ["BINDIR"] = str(bin_dir)
            else:
                raise RuntimeError(
                    f"Could not find build dir {bin_dir_path}."
                    " Make sure to point to an existing bin dir."
                )
        else:
            logger.info(f"Building experiment {exp_name}")

        # Run the build command
        subprocess.run(
            [
                self.config.git_repos.harmonie.repo / "config-sh/Harmonie",
                "install",
            ],
            cwd=self.config.home_exp_dir,
            check=True,
            env=os.environ,
        )

        # Call your function to wait for the ecflow node to complete
        await_ecflow_node_to_complete(f"/{exp_name}")
        logger.info("Build/InitRun finished")


class BuildDDH(RerunBaseTask):
    """Luigi task to install the DDH library."""

    def output(self):
        """Specifies the output target for this task.

        Returns:
            luigi.LocalTarget: A target file representing the lfac path.
        """
        lfac_path = self.config.git_repos.ddhtoolbox.repo / "tools/lfa/lfac"
        return luigi.LocalTarget(lfac_path)

    def requires(self):
        """Specifies the dependencies for this task.

        Returns:
            list: A list of tasks that must be completed before this task.
        """
        return CloneRepos(rerun_all=self.rerun_all, config=self.config)

    def run(self):
        """Executes the DDH library installation."""
        logger.info("Installing DDH library")
        subprocess.run(
            "export PATH=.:$PATH; install clean; install;",
            cwd=self.config.git_repos.ddhtoolbox.repo / "tools",
            check=True,
            shell=True,
        )
        logger.info("Done installing DDH library")
