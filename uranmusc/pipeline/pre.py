"""Module for preliminary pipeline tasks.

This module contains Luigi tasks for cloning required repositories.
"""

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
    """Luigi task to clone necessary repositories."""

    def output(self):
        """Specifies the output targets for this task.

        Returns:
            list: A list of luigi.LocalTarget objects for each repository's
                .git directory.
        """
        return [
            luigi.LocalTarget(repo.repo / ".git") for _, repo in self.config.git_repos
        ]

    def run(self):
        """Executes the cloning of repositories.

        For each repository in the configuration, it removes any existing
        directory and then performs a git clone with submodules.
        """
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
