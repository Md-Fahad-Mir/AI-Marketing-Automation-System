"""Centralized logging configuration for the application."""

import logging

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(level: int = logging.INFO) -> None:
    """Configure the root logger with a consistent console format.

    Calling this more than once is safe; existing handlers are reused.
    """
    logging.basicConfig(level=level, format=LOG_FORMAT, datefmt=DATE_FORMAT)
