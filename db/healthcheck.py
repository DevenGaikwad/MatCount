"""Database identity and availability checks."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from config.constants import DATABASE_NAME
from config.settings import get_settings
from db.connection import get_engine


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class DatabaseHealth:
    ok: bool
    server_version: str | None = None
    database_name: str | None = None
    message: str = ""


def check_database() -> DatabaseHealth:
    try:
        issues = get_settings().connection_issues()
        if issues:
            return DatabaseHealth(
                ok=False,
                message="Database configuration incomplete: " + "; ".join(issues),
            )
        with get_engine().connect() as connection:
            row = connection.execute(
                text("SELECT VERSION() AS version, DATABASE() AS database_name")
            ).mappings().one()
        database_name = str(row["database_name"] or "")
        if database_name != DATABASE_NAME:
            return DatabaseHealth(
                ok=False,
                server_version=str(row["version"]),
                database_name=database_name,
                message=f"Connected database is {database_name!r}; expected {DATABASE_NAME!r}.",
            )
        return DatabaseHealth(
            ok=True,
            server_version=str(row["version"]),
            database_name=database_name,
            message="SEMS database connection is healthy.",
        )
    except (SQLAlchemyError, TypeError, ValueError) as exc:
        LOGGER.warning("SEMS database health check failed: %s", exc.__class__.__name__)
        return DatabaseHealth(
            ok=False,
            message=f"Database connection failed: {exc.__class__.__name__}",
        )
