"""This module is a hack to replace luigi's normal logging functionality so we can
use loguru instead
"""

import datetime
import inspect
import logging
import os

from loguru import logger

# Prevent Luigi from automatically configuring logging
os.environ["LUIGI_CONFIG_PATH"] = "/dev/null"


def is_luigi_logging_setup_in_call_stack():
    # Get the current call stack
    stack = inspect.stack()

    # Iterate through the call stack
    for frame_info in stack:
        module = inspect.getmodule(frame_info[0])
        if (
            module
            and module.__name__ == "luigi.setup_logging"
            and frame_info[3] == "setup"
        ):
            return True  # Found the setup function from luigi.setup_logging
            # in the call stack

    return False  # The specified function was not found in the call stack


original_addHandler = logging.Logger.addHandler


def setup_loguru_logger():
    fn_log = f"logs/{datetime.datetime.now().strftime('%Y%m%dT%H%M%S')}.log"
    logger.add(fn_log)
    logger.info(f"Logging to {fn_log}")


def addHandlerWithNotification(self, hdlr):
    if self.name == "luigi-interface" and is_luigi_logging_setup_in_call_stack():
        setup_loguru_logger()
    else:
        original_addHandler(self, hdlr)


# Monkey patch the Logger class's addHandler method
logging.Logger.addHandler = addHandlerWithNotification


class InterceptHandler(logging.Handler):
    """
    Intercept standard logging messages toward Loguru sinks.
    """

    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where logged message originated,
        # skipping frames to correctly report the caller
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        msg = record.getMessage()
        logger.opt(depth=depth, exception=record.exc_info).log(level, msg)


def setup_luigi_log_interception(loglevel=logging.INFO):
    # Get the luigi-interface logger
    luigi_logger = logging.getLogger("luigi-interface")

    # Clear existing handlers (optional, based on your needs)
    luigi_logger.handlers = []

    # Optionally, you might want to adjust the log level
    luigi_logger.setLevel(loglevel)

    # Create and add the intercept handler
    intercept_handler = InterceptHandler(level=loglevel)
    luigi_logger.addHandler(intercept_handler)
