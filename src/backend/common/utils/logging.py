import logging
import sys
from enum import StrEnum


SUCCESS_LEVEL = 25


class Colors(StrEnum):
    GRAY = '\x1b[38;20m'
    YELLOW = '\x1b[33;20m'
    RED = '\x1b[31;20m'
    BOLD_RED = '\x1b[31;1m'
    GREEN = '\x1b[32;20m'
    RESET = '\x1b[0m'


class CustomFormatter(logging.Formatter):
    _format = '[%(asctime)s] %(levelname).4s -> [%(title)s] %(message)s'
    colorized = False

    FORMATS = {
        logging.DEBUG: Colors.GRAY + _format + Colors.RESET,
        logging.INFO: Colors.GRAY + _format + Colors.RESET,
        logging.WARNING: Colors.YELLOW + _format + Colors.RESET,
        logging.ERROR: Colors.RED + _format + Colors.RESET,
        logging.CRITICAL: Colors.BOLD_RED + _format + Colors.RESET,
        SUCCESS_LEVEL: Colors.GREEN + _format + Colors.RESET
    }

    def format(self, record):
        if not hasattr(record, 'title'):
            record.title = 'DEBUG'
        else:
            record.title = record.title.upper()

        if self.colorized:
            log_fmt = self.FORMATS.get(record.levelno)
        else:
            log_fmt = self._format
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


# Add success level name
def success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL):
        self._log(SUCCESS_LEVEL, message, args, **kwargs)


logging.addLevelName(25, 'SUCCESS')
logging.Logger.success = success

# Create logger
log = logging.getLogger('logger')
log.setLevel(logging.INFO)

# Create a console handler
if sys.stdout:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    formatter = CustomFormatter()
    formatter.colorized = True
    console_handler.setFormatter(formatter)

    log.addHandler(console_handler)


def enable(value: bool):
    logging.disable(logging.NOTSET if value else logging.CRITICAL)
