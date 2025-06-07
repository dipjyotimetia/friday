"""Simple logging configuration for Friday application."""

import logging
import sys
from typing import Optional

from friday.config.config import settings


def configure_logging():
    """Configure basic logging for the application."""
    # Convert string log level to logging constant
    log_level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    # Get log level from settings
    log_level = log_level_map.get(settings.log_level.upper(), logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance."""
    if name:
        return logging.getLogger(name)
    return logging.getLogger("friday")


# Configure logging on import
configure_logging()

# Global logger instance
logger = get_logger()
