"""Safe database-unavailable behavior without exposing credentials."""

import pytest

from config.settings import Settings
from db import healthcheck


pytestmark = pytest.mark.unit


def test_healthcheck_reports_unavailable_database_without_exception_details(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = Settings(
        db_host="127.0.0.1",
        db_port=3306,
        db_name="sems_db",
        db_user="sems_app",
        db_password="local-only-password",
    )
    monkeypatch.setattr(healthcheck, "get_settings", lambda: settings)
    monkeypatch.setattr(
        healthcheck, "get_engine", lambda: (_ for _ in ()).throw(ValueError("secret"))
    )
    result = healthcheck.check_database()
    assert not result.ok
    assert result.message == "Database connection failed: ValueError"
    assert "secret" not in result.message
