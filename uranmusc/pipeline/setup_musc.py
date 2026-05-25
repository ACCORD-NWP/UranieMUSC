"""Module for setting up MUSC-specific configurations.

This module contains Luigi tasks for setting up MUSC run scripts
and namelists.
"""
import logging
import shutil
import subprocess

import luigi

from uranmusc.pipeline.base import RerunBaseTask
from uranmusc.pipeline.build import BuildExperiment
from uranmusc.pipeline.pre import CloneRepos
from uranmusc.pipeline.setup_experiment import SetupExperiment

# Use luigi logger interface set up in uranmusc/log.py
logger = logging.getLogger("luigi-interface")


class SetupMusc(RerunBaseTask):
    """Luigi task to set up MUSC environment.

    Attributes:
        bin_dir (luigi.Parameter): Directory containing binaries.
    """
    bin_dir = luigi.Parameter(default=None)

    def requires(self):
        """Specifies the dependencies for this task.

        Returns:
            list: A list of tasks that must be completed before this task.
        """
        return [
            CloneRepos(rerun_all=self.rerun_all, config=self.config),
            SetupExperiment(rerun_all=self.rerun_all, config=self.config),
            BuildExperiment(
                bin_dir=self.bin_dir, rerun_all=self.rerun_all, config=self.config
            ),
        ]

    def output(self):
        """Specifies the output targets for this task.

        Returns:
            list: A list of luigi.LocalTarget objects for the MUSC setup files.
        """
        return [
            luigi.LocalTarget(self.config.home_exp_dir / "musc_run.sh"),
            luigi.LocalTarget(self.config.home_exp_dir / "musc_convert_netcdf.sh"),
            luigi.LocalTarget(self.config.home_exp_dir / "variable_list.csv"),
        ]

    def run(self):
        """Executes the MUSC setup.

        Runs the Harmonie MUSC setup script to prepare the experiment directory.
        """
        logger.info(f"Setting up MUSC for experiment {self.config.experiment.name}")

        subprocess.run(
            [
                self.config.git_repos.harmonie.repo / "util/musc/scr/musc_setup.sh",
                "-r",
                self.config.git_repos.harmonie.repo,
            ],
            cwd=self.config.home_exp_dir,
            env={"MUSCHOME": str(self.config.home_exp_dir)},
            check=True,
        )


class SetupMuscNamelists(RerunBaseTask):
    """Luigi task to set up MUSC namelists.

    Attributes:
        bin_dir (luigi.Parameter): Directory containing binaries.
    """
    bin_dir = luigi.Parameter(default=None)

    def requires(self):
        """Specifies the dependencies for this task.

        Returns:
            list: A list of tasks that must be completed before this task.
        """
        return [
            CloneRepos(rerun_all=self.rerun_all),
            SetupExperiment(rerun_all=self.rerun_all),
            BuildExperiment(bin_dir=self.bin_dir, rerun_all=self.rerun_all),
        ]

    def output(self):
        """Specifies the output targets for this task.

        Returns:
            list: A list of luigi.LocalTarget objects for the generated namelists.
        """
        atm_namelist_name = "namelist_atm_" + self.config.experiment.musc_id
        return [
            luigi.LocalTarget(self.config.home_exp_dir / atm_namelist_name),
        ]

    def run(self):
        """Executes the MUSC namelist setup.

        Either copies existing namelists or generates them via a shell script.
        """
        doe = self.config.experiment.design_of_experiment
        if doe.data_files.namelist_dir is not None:
            namelist_dir = doe.data_files.namelist_dir / self.config.experiment.musc_case
            logger.info("Using MUSC namelists from %s", namelist_dir)
            shutil.copy(self.config.namelist, self.config.home_exp_dir)
        else:
            logger.info(
                "Generating namelists for experiment %s", self.config.experiment.name
            )
            subprocess.run(
                [
                    self.config.home_exp_dir / "musc_namelist.sh",
                    "-l",
                    str(self.config.experiment.fc_length),
                    "-i",
                    self.config.experiment.musc_id,
                ],
                cwd=self.config.home_exp_dir,
                check=True,
            )
