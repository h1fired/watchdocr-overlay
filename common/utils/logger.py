import logging
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
    format = '[%(asctime)s] %(levelname).4s -> %(message)s'

    FORMATS = {
        logging.DEBUG: Colors.GRAY + format + Colors.RESET,
        logging.INFO: Colors.GRAY + format + Colors.RESET,
        logging.WARNING: Colors.YELLOW + format + Colors.RESET,
        logging.ERROR: Colors.RED + format + Colors.RESET,
        logging.CRITICAL: Colors.BOLD_RED + format + Colors.RESET,
        SUCCESS_LEVEL: Colors.GREEN + format + Colors.RESET
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
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
log.setLevel(logging.DEBUG)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

formatter = CustomFormatter()
console_handler.setFormatter(formatter)

log.addHandler(console_handler)
