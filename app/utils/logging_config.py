"""
utils/logging_config.py — Centralized logging setup for WoxuDB.
Call configure_logging() once at application startup.
"""
import logging
import sys


def configure_logging(debug: bool = False) -> None:
    """Configure structured logging for the application."""
    level = logging.DEBUG if debug else logging.INFO
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%dT%H:%M:%S"

    logging.basicConfig(
        level=level,
        format=fmt,
        datefmt=datefmt,
        stream=sys.stdout,
        force=True,
    )

    # Keep noisy uvicorn access logs at INFO and reduce psycopg pool chatter
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("psycopg.pool").setLevel(logging.WARNING)


# Module-level logger for import convenience
logger = logging.getLogger("woxudb")
