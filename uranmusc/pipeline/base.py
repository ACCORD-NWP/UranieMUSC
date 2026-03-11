import logging
import warnings
from typing import cast

import luigi

from uranmusc.config_parser import Config
from uranmusc.pipeline.parameters import PydanticModelParameter

# Use luigi logger interface set up in uranmusc/log.py
logger = logging.getLogger("luigi-interface")


class BaseTask(luigi.Task):
    config: Config = PydanticModelParameter(default="config.yml")

    def run(self):
        """Dummy task to be overriden.

        Serves solely the purpose of making the type checker understand the
        correct type of self.config for all tasks that inherit from BaseTask"""
        self.config = cast(Config, self.config)


class RerunBaseTask(BaseTask):
    """A base class for all tasks that should be rerunnable."""

    rerun_task = luigi.BoolParameter(default=False)
    rerun_all = luigi.BoolParameter(default=False)

    def complete(self):
        """
        If the task has any outputs, return ``True`` if all outputs exist.
        Otherwise, return ``False``. If --rerun-task or --rerun-all is True,
        return ``False``.
        """
        if self.rerun_task or self.rerun_all:
            return False

        outputs = luigi.task.flatten(self.output())
        if len(outputs) == 0:
            warnings.warn(
                "Task %r without outputs has no custom complete() method" % self,
                stacklevel=2,
            )
            return False

        return all(map(lambda output: output.exists(), outputs))
