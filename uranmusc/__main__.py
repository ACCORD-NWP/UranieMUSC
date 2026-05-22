"""Main module of the UranMusc package"""

import logging

import luigi

from uranmusc.log import setup_luigi_log_interception
from uranmusc.tasks import *  # noqa: F403, F401


def main():
    setup_luigi_log_interception(loglevel=logging.DEBUG)
    luigi.run()
