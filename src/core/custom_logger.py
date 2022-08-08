"""
https://medium.com/1mgofficial/how-to-override-uvicorn-logger-in-fastapi-using-loguru-124133cdcd4e
"""
import logging
import sys

from loguru import logger

from .config import LOCALLY_DEBUG, LOGURU_FORMAT, LOGURU_LEVEL


class InterceptHandler(logging.Handler):
    log_level_mapping = {
        50: "CRITICAL",
        40: "ERROR",
        30: "WARNING",
        20: "INFO",
        10: "DEBUG",
        0: "NOTSET",
    }

    def emit(self, record):
        """
        Emit a record to the logging system.

        Args:
            self: write your description
            record: write your description
        """
        try:
            level = logger.level(record.levelname).name
        except AttributeError:
            level = self.log_level_mapping[record.levelno]

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        log = logger.bind(request_id="app")
        log.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def custom_loguru_app_logger():
    """https://loguru.readthedocs.io/en/stable/api/logger.html"""
    logger.remove()
    logger.add(
        sys.stdout,
        enqueue=False,  # bug, it may silence logs if (encounter blocking io)?
        backtrace=False,  # too verbose
        colorize=LOCALLY_DEBUG,
        level=LOGURU_LEVEL,
        format=LOGURU_FORMAT,
        diagnose=False,  # too verbose
    )
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    logging.getLogger("uvicorn").handlers = []  # handler with basicConfig
    logging.getLogger("fastapi").handlers = [InterceptHandler()]
    return logger.bind(request_id=None, method=None)
