"""
Centralized logging configuration for the library system.
Use this instead of print() for all debug/info/error messages.
"""
import logging
import sys
from app.core.config import get_settings


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    settings = get_settings()
    
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(settings.log_level.upper())
    
    return logger
