"""Configuration validation that never requires a live database."""

import pytest

from config.settings import Settings


pytestmark = pytest.mark.unit


def settings(**changes: object) -> Settings:
    values = {
        "db_host": "127.0.0.1",
        "db_port": 3306,
        "db_name": "sems_db",
        "db_user": "sems_app",
        "db_password": "local-only-password",
    }
    values.update(changes)
    return Settings(**values)


def test_valid_connection_settings_have_no_issues() -> None:
    assert settings().connection_issues() == []


def test_connection_settings_report_all_safe_errors_without_password_value() -> None:
    issues = settings(
        db_port=-1,
        db_name="smart_electronics_lab_ddl",
        db_password="REPLACE_WITH_LOCAL_PASSWORD",
        db_pool_size=0,
        db_max_overflow=-1,
        db_connect_timeout=0,
    ).connection_issues()
    combined = "; ".join(issues)
    assert "DB_PORT" in combined
    assert "DB_NAME must be sems_db" in combined
    assert "placeholder" in combined
    assert "DB_POOL_SIZE" in combined
    assert "DB_MAX_OVERFLOW" in combined
    assert "DB_CONNECT_TIMEOUT" in combined
    assert "REPLACE_WITH_LOCAL_PASSWORD" not in combined


def test_database_url_percent_encodes_credentials() -> None:
    url = settings(db_user="sems app", db_password="p@ss/word").database_url
    assert "sems+app:p%40ss%2Fword" in url
    assert url.endswith("/sems_db?charset=utf8mb4")
