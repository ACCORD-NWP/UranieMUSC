import logging
import shutil
import subprocess

import luigi

from uranmusc.pipeline.base import RerunBaseTask
from uranmusc.pipeline.pre import CloneRepos

# Use luigi logger interface set up in uranmusc/log.py
logger = logging.getLogger("luigi-interface")


class SetupExperiment(RerunBaseTask):
    def requires(self):
        return CloneRepos(rerun_all=self.rerun_all, config=self.config)

    def output(self):
        return luigi.LocalTarget(self.config.home_exp_dir / "config-sh")

    def run(self):
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
