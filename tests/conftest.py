"""Shared pytest configuration."""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection
from sqlalchemy.engine.url import make_url


@pytest.fixture
def mysql_connection() -> Iterator[Connection]:
    url_text = os.getenv("SEMS_TEST_DATABASE_URL")
    if not url_text:
        pytest.skip("SEMS_TEST_DATABASE_URL is not configured")
    url = make_url(url_text)
    database = url.database or ""
    if database not in {"sems_test", "sems_db_test"} and not database.endswith("_test"):
        pytest.fail("Integration tests require a dedicated database ending in _test")

    engine = create_engine(url_text, pool_pre_ping=True, future=True)
    connection = engine.connect()
    transaction = connection.begin()
    try:
        active_database = connection.execute(text("SELECT DATABASE()"))
        assert active_database.scalar_one() == database
        yield connection
    finally:
        if transaction.is_active:
            transaction.rollback()
        connection.close()
        engine.dispose()

