import logging
import logging.handlers
import os
import sys
from typing import Optional

from pythonjsonlogger import jsonlogger

from app.config import config

logger = logging.getLogger(config.SERVICE_NAME)
logging.getLogger("asyncio").setLevel(logging.WARNING)

MAX_LOG_FILE_MB = 10

# Store 10GB of logs
MAX_TOTAL_LOG_FILE_MB = 10000
MAX_LOG_FILE_BACKUPS = MAX_TOTAL_LOG_FILE_MB // MAX_LOG_FILE_MB
LOG_FILE_KWARGS = {
    "maxBytes": 1000 * 1000 * MAX_LOG_FILE_MB,
    "backupCount": MAX_LOG_FILE_BACKUPS,
}

LOG_FORMAT = "%(levelname) %(message) %(module) %(lineno) %(funcName) %(filename) %(asctime)"


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Logger formatter"""

    def process_log_record(self, log_record):
        """Process all record inside the log."""
        # Any items like %(levelname) that get mentioned in the "fmt" param of
        # __init__ are automatically added to the log_record dictionary and each
        # element in that dictionary is emitted as a json element by
        # CustomJsonFormatter. Here, we change the "levelname" element to
        # "severity".
        log_record["severity"] = log_record["levelname"]
        del log_record["levelname"]

        # Replace any non-string keys in log_record with their string equivalents
        for key in log_record.copy():
            if not isinstance(key, str):
                log_record[str(key)] = log_record[key]
                del log_record[key]

        # Look for log_record["override_<key name>"] and move their values to log_record["<key
        # name>"], then delete log_record["override_<key name>"].  This allows us to override
        # keys like "lineno" using "override_lineno" without raising an exception like 'KeyError:
        # "Attempt to overwrite 'lineno' in LogRecord"' in the logger library where lineno is
        # normally populated.
        for key in log_record.copy():
            override_prefix = "override_"
            if key.startswith(override_prefix):
                log_record[key[len(override_prefix):]] = log_record[key]  # fmt: skip
                del log_record[key]

        return super().process_log_record(log_record)


def add_stdout_handler(logger_instance: logging.Logger, log_level: str):
    """Adding stdout handlers to the logger."""
    log_handler = logging.StreamHandler(stream=sys.stdout)
    log_handler.set_name("stdout")
    log_handler.setFormatter(CustomJsonFormatter(fmt=LOG_FORMAT))
    log_handler.setLevel(log_level)
    logger_instance.addHandler(log_handler)


def add_file_handler(logger_instance: logging.Logger, level: str, filename: str):
    """Adding file handler to the logger instance."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    log_handler = logging.handlers.RotatingFileHandler(filename, **LOG_FILE_KWARGS)
    log_handler.setFormatter(CustomJsonFormatter(fmt=LOG_FORMAT))
    log_handler.setLevel(level)
    logger_instance.addHandler(log_handler)


def init_loggers(level: str, file_level: Optional[str] = None, filename: Optional[str] = None):
    """Start loggers for the whole app."""
    # We need the minimum log level of the two so that we don't accidentally
    # set a logger to log at a higher level than is expected by either the
    # stdout or file handlers.
    min_level = min_log_level(level, file_level)

    logging.captureWarnings(True)
    warnings_logger = logging.getLogger("py.warnings")
    asyncio_logger = logging.getLogger("asyncio")

    for logger_instance in [logger, asyncio_logger, warnings_logger]:
        logger_instance.setLevel(min_level)
        add_stdout_handler(logger_instance, level)
        if not (file_level is None or filename is None):
            add_file_handler(logger_instance, file_level, filename)

    if file_level is None or filename is None:
        logger.info("Not logging to a file")
    else:
        logger.info(
            "Logging at level %s to file %s",
            file_level,
            filename,
            extra={"config": LOG_FILE_KWARGS},
        )


def min_log_level(level1: str, level2: Optional[str]):
    """Check the minimum loge level by default."""
    return min([level1, level2 or "CRITICAL"], key=logging.getLevelName)
