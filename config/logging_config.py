"""Safe rotating-file and console logging configuration."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config.settings import get_settings


def configure_logging() -> None:
    root = logging.getLogger()
    if root.handlers:
        return

    try:
        settings = get_settings()
        level = getattr(logging, settings.log_level, logging.INFO)
    except (TypeError, ValueError):
        # Invalid application configuration must not suppress safe startup logging.
        level = logging.INFO
    root.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)

    log_dir = Path(__file__).resolve().parents[1] / "logs"
    log_dir.mkdir(exist_ok=True)
    file_handler = RotatingFileHandler(
        log_dir / "sems.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)
    logging.getLogger(__name__).info("SEMS application logging initialized")
