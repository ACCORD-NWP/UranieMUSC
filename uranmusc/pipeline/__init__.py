"""Module providing a high-level interface for the uranmusc pipeline.

This module exports key Luigi tasks and parameters used to orchestrate
the full simulation workflow, from cloning repositories to post-processing.
"""

import luigi

from uranmusc.pipeline.base import BaseTask, RerunBaseTask
from uranmusc.pipeline.build import BuildDDH, BuildExperiment
from uranmusc.pipeline.parameters import PydanticModelParameter
from uranmusc.pipeline.post import ConvertLFAToNetCDF
from uranmusc.pipeline.pre import CloneRepos
from uranmusc.pipeline.run import RunMusc, RunUranie
from uranmusc.pipeline.setup_experiment import SetupExperiment
from uranmusc.pipeline.setup_musc import SetupMusc, SetupMuscNamelists

__all__ = [
    "BaseTask",
    "RerunBaseTask",
    "BuildDDH",
    "BuildExperiment",
    "PydanticModelParameter",
    "ConvertLFAToNetCDF",
    "CloneRepos",
    "Run",
    "RunMusc",
    "RunUranie",
    "SetupExperiment",
    "SetupMusc",
    "SetupMuscNamelists",
]


class Run(luigi.WrapperTask):
    """A wrapper task that runs the entire pipeline from end to end.

    Attributes:
        bin_dir (luigi.Parameter): Directory containing binaries.
        ntasks (luigi.IntParameter): Number of tasks for parallel execution.
        rerun_all (luigi.BoolParameter): Whether to rerun all tasks.
        config (PydanticModelParameter): Path to the configuration file.
    """

    bin_dir = luigi.Parameter(default=None)
    ntasks = luigi.IntParameter(default=1)
    rerun_all = luigi.BoolParameter()
    config = PydanticModelParameter(default="config.yml")

    def requires(self):
        """Specifies the full pipeline dependencies.

        Yields:
            ConvertLFAToNetCDF: The final task in the pipeline.
        """
        yield ConvertLFAToNetCDF(
            bin_dir=self.bin_dir,
            ntasks=self.ntasks,
            rerun_all=self.rerun_all,
            config=self.config,
        )
