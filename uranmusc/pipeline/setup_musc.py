import logging
import subprocess

import luigi

from uranmusc.pipeline.base import RerunBaseTask
from uranmusc.pipeline.build import BuildExperiment
from uranmusc.pipeline.pre import CloneRepos
from uranmusc.pipeline.setup_experiment import SetupExperiment

# Use luigi logger interface set up in uranmusc/log.py
logger = logging.getLogger("luigi-interface")


class SetupMusc(RerunBaseTask):
    bin_dir = luigi.Parameter(default=None)

    def requires(self):
        return [
            CloneRepos(rerun_all=self.rerun_all, config=self.config),
            SetupExperiment(rerun_all=self.rerun_all, config=self.config),
            BuildExperiment(
                bin_dir=self.bin_dir, rerun_all=self.rerun_all, config=self.config
            ),
        ]

    def output(self):
        output_namelist_name = f"namelist_atm_{self.config.experiment.musc_id}"
        return [
            luigi.LocalTarget(self.config.home_exp_dir / "musc_run.sh"),
            luigi.LocalTarget(self.config.home_exp_dir / "musc_convert_netcdf.sh"),
            luigi.LocalTarget(self.config.home_exp_dir / "variable_list.csv"),
            luigi.LocalTarget(self.config.home_exp_dir / output_namelist_name),
        ]

    def run(self):
        """Build the experiment."""
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

        logger.info("Generating namelist")
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
