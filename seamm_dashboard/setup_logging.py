import logging
import logging.handlers
from pathlib import Path


def setup_logging(datastore, options):
    """
    Sets up logging to console (INFO+) and logging of log file
    logs/myapp-<timestamp>.log. You can create a an extra logger to represent
    areas in your app: logger1 = logging.getLogger('area1')

    Logging Levels:

    https://docs.python.org/3/howto/logging.html#logging-levels

    DEBUG (default for FILE): Detailed information, typically of interest only
        when diagnosing problems.
    INFO (default for CONSOLE): Confirmation that things are working as
        expected.
    WARNING: An indication that something unexpected happened, or indicative of
        some problem in the near future (e.g. 'disk space low').
        The software is still working as expected.
    ERROR: Due to a more serious problem, the software has not been able
        to perform some function.
    CRITICAL: A serious error, indicating that the program itself may be unable
        to continue running.

    Params
        options
    """

    # Make sure the logs folder exists (avoid FileNotFoundError)
    log_dir = Path(options["log_dir"].replace("%datastore%", datastore)).expanduser()

    if not log_dir.is_dir():
        log_dir.mkdir(parents=True, exist_ok=True)

    # Set up logging to a file (overwriting)
    log_file = log_dir / "dashboard.log"

    # Get root logger
    logger = logging.getLogger()
    logger.setLevel("DEBUG")

    # Create a handler that writes INFO messages or higher to sys.stderr
    console_handler = logging.StreamHandler()
    console_handler.setLevel(options["console_log_level"])
    console_formatter = logging.Formatter("%(name)s:%(levelname)s:%(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # And one to log in files
    file_handler = logging.handlers.TimedRotatingFileHandler(
        str(log_file), when="W6", backupCount=4
    )
    file_handler.setLevel(options["log_level"])
    file_formatter = logging.Formatter("%(asctime)s %(name)s:%(levelname)s:%(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    new_logger = logging.getLogger("dashboard")
    new_logger.info(
        "Logging to the console at level {}.".format(options["console_log_level"])
    )
    new_logger.info("Logging to {} at level {}.".format(log_file, options["log_level"]))

    # Demo usage
    # logger = logging.getLogger(__name__)
    # logger.debug('a debug log message')
    # logger.info('an info log message')
    # logger.warning('a warning log message')
    # logger.error('an error log message')
    # logger.critical('a critical log message')
