import luigi

from uranmusc.pipeline.base import BaseTask, RerunBaseTask
from uranmusc.pipeline.build import BuildDDH, BuildExperiment
from uranmusc.pipeline.parameters import PydanticModelParameter
from uranmusc.pipeline.post import ConvertLFAToNetCDF
from uranmusc.pipeline.pre import CloneRepos
from uranmusc.pipeline.run import RunMusc, RunUranie
from uranmusc.pipeline.setup_experiment import SetupExperiment
from uranmusc.pipeline.setup_musc import SetupMusc

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
]


class Run(luigi.WrapperTask):
    bin_dir = luigi.Parameter(default=None)
    ntasks = luigi.IntParameter(default=1)
    rerun_all = luigi.BoolParameter()
    config = PydanticModelParameter(default="config.yml")

    def requires(self):
        yield ConvertLFAToNetCDF(
            bin_dir=self.bin_dir,
            ntasks=self.ntasks,
            rerun_all=self.rerun_all,
            config=self.config,
        )
