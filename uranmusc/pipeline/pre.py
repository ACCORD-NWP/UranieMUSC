import logging
import shutil
import subprocess
from typing import cast

import luigi

from uranmusc.config_parser import GitRepositoryConfig
from uranmusc.pipeline.base import RerunBaseTask

# Use luigi logger interface set up in uranmusc/log.py
logger = logging.getLogger("luigi-interface")


class CloneRepos(RerunBaseTask):
    def output(self):
        return [
            luigi.LocalTarget(repo.repo / ".git") for _, repo in self.config.git_repos
        ]

    def run(self):
        for repo_name, repo in self.config.git_repos:
            repo = cast(GitRepositoryConfig, repo)  # Make type checker happy
            logger.info(f"Removing old {repo_name} repo if it exists")
            shutil.rmtree(repo.repo, ignore_errors=True)
            logger.info(f"Cloning {repo_name} repo into '{repo.repo}'")
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--recurse-submodules",
                    "--single-branch",
                    "--branch",
                    repo.branch,
                    repo.url,
                    repo.repo,
                ],
                check=True,
            )
