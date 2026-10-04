"""SQLAlchemy engine construction for the shared SEMS MySQL database."""

from __future__ import annotations

from functools import lru_cache

from sqlalchemy import Engine, create_engine

from config.settings import get_settings


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    settings = get_settings()
    issues = settings.connection_issues()
    if issues:
        raise ValueError("; ".join(issues))
    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_recycle=1800,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        connect_args={"connect_timeout": settings.db_connect_timeout},
        isolation_level="READ COMMITTED",
        future=True,
    )


def dispose_engine() -> None:
    if get_engine.cache_info().currsize:
        get_engine().dispose()
        get_engine.cache_clear()
