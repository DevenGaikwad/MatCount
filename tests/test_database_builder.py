"""Tests for safe test-database targeting and MySQL delimiter splitting."""

import pytest

from scripts.build_database import split_mysql_script, target_script, validate_database_name
from scripts.validate_project import integration_target_is_safe


pytestmark = pytest.mark.contract


def test_database_target_accepts_frozen_and_test_names() -> None:
    assert validate_database_name("sems_db") == "sems_db"
    assert validate_database_name("sems_test") == "sems_test"
    assert validate_database_name("sems_db_test") == "sems_db_test"


@pytest.mark.parametrize("name", ["mysql", "production", "../sems_test", "sems-test"])
def test_database_target_rejects_unrelated_or_unsafe_names(name: str) -> None:
    with pytest.raises(ValueError):
        validate_database_name(name)


def test_target_script_changes_only_database_setup_and_use() -> None:
    source = "CREATE DATABASE IF NOT EXISTS sems_db;\nUSE sems_db;\nSELECT 'sems_db';"
    targeted = target_script(source, "sems_test")
    assert "CREATE DATABASE IF NOT EXISTS sems_test" in targeted
    assert "USE sems_test;" in targeted
    assert "SELECT 'sems_db'" in targeted


def test_splitter_preserves_procedure_body_delimiters() -> None:
    source = """
    USE sems_db;
    DELIMITER $$
    CREATE PROCEDURE demo()
    BEGIN
      SELECT 1;
      SELECT 2;
    END$$
    DELIMITER ;
    SELECT 3;
    """
    statements = list(split_mysql_script(source))
    assert len(statements) == 3
    assert statements[0].strip() == "USE sems_db"
    assert "SELECT 1;" in statements[1]
    assert statements[2].strip() == "SELECT 3"


def test_splitter_ignores_standalone_and_trailing_comments() -> None:
    source = """
    -- setup comment
    USE sems_db;
    -- a trailing documentation comment is not an incomplete statement
    """
    assert list(split_mysql_script(source)) == ["USE sems_db"]


def test_one_command_local_acceptance_requires_test_database(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "SEMS_TEST_DATABASE_URL",
        "mysql+pymysql://tester:secret@127.0.0.1:3306/sems_release_test",
    )
    assert integration_target_is_safe()
    monkeypatch.setenv(
        "SEMS_TEST_DATABASE_URL",
        "mysql+pymysql://tester:secret@127.0.0.1:3306/sems_db",
    )
    assert not integration_target_is_safe()
