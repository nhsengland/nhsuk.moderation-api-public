import logging
from logging.handlers import TimedRotatingFileHandler


def configure_logging():
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    debug_log_handler = TimedRotatingFileHandler(
        "debug.log", when="D", interval=1, backupCount=30
    )
    debug_log_handler.setLevel(logging.DEBUG)

    info_log_handler = TimedRotatingFileHandler(
        "info.log", when="D", interval=1, backupCount=30  # Keep last 30 days logs
    )
    info_log_handler.setLevel(logging.INFO)
    info_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    info_log_handler.setFormatter(info_formatter)

    # same time thing here
    error_log_handler = TimedRotatingFileHandler(
        "error.log", when="D", interval=1, backupCount=30
    )
    error_log_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    error_log_handler.setFormatter(error_formatter)

    # Add the handlers to the root logger
    logger = logging.getLogger()
    logger.addHandler(debug_log_handler)
    # logger.addHandler(info_log_handler)
    # logger.addHandler(error_log_handler)

    print("Logging configured")


configure_logging()
