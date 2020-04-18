import os
import logging
from datetime import datetime


def setup_logging(options):
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
    path = os.getcwd() + '/logs'
    if not os.path.isdir(path):
        os.makedirs(path)

    # Set up logging to a file (overwriting)
    log_filename = (
        os.path.join(path, 'dashboard-{}.log').format(
            datetime.utcnow().strftime("%Y%m%d")
        )
    )

    # Possibly use %(pathname)s:%(lineno)d
    # logging.basicConfig(datefmt='%Y-%m-%d %H:%M:%S')

    # Get root logger
    logger = logging.getLogger()
    logger.setLevel('DEBUG')

    # Create a handler that writes INFO messages or higher to sys.stderr
    console = logging.StreamHandler()
    console.setLevel(options.console_log_level)
    console_formatter = logging.Formatter('%(name)s:%(levelname)s:%(message)s')
    console.setFormatter(console_formatter)
    logger.addHandler(console)

    # And one to log in files
    file_ = logging.FileHandler(filename=log_filename, mode='a')
    file_.setLevel(options.log_level)
    file_formatter = logging.Formatter(
        '%(asctime)s %(name)s:%(levelname)s:%(message)s'
    )
    file_.setFormatter(file_formatter)
    logger.addHandler(file_)

    # Demo usage
    # logger = logging.getLogger('setup_logging')
    # logger.debug('a debug log message')
    # logger.info('an info log message')
    # logger.warning('a warning log message')
    # logger.error('an error log message')
    # logger.critical('a critical log message')
