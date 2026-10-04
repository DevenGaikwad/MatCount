"""Static SQL/Workbench contract tests."""

import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SQL = ROOT / "sql"
pytestmark = pytest.mark.contract


def read(name: str) -> str:
    return (SQL / name).read_text(encoding="utf-8")


def test_schema_creates_exactly_thirteen_relations() -> None:
    tables = {
        value.lower()
        for value in re.findall(
            r"CREATE\s+TABLE\s+`?([a-z_]+)`?\s*\(",
            read("01_schema.sql"),
            flags=re.IGNORECASE,
        )
    }
    assert len(tables) == 13
    assert "audit_log" not in tables


def test_forbidden_schema_columns_are_absent() -> None:
    schema = read("01_schema.sql").lower()
    for token in ["password_hash", "destination_inventory_id", "lab_status"]:
        assert token not in schema


def test_required_views_exist() -> None:
    views = read("03_views.sql")
    for name in [
        "v_inventory_detail",
        "v_component_stock_summary",
        "v_low_stock_components",
        "v_request_progress",
        "v_transfer_detail",
        "v_overdue_returns",
        "v_disposal_summary",
    ]:
        assert f"VIEW {name}" in views


def test_inventory_valuation_includes_reserved_on_hand_stock() -> None:
    views = read("03_views.sql").replace("\n", " ")
    assert "quantity_available + i.quantity_reserved" in views
    verification = read("07_verification_queries.sql")
    assert "SUM(inventory_value)" in verification
    assert "total_on_hand_inventory_value" in verification


def test_workbench_verification_script_is_read_only() -> None:
    text = re.sub(r"--.*?$", "", read("07_verification_queries.sql"), flags=re.MULTILINE)
    assert not re.search(
        r"\b(INSERT|UPDATE|DELETE|REPLACE|DROP|ALTER|TRUNCATE|CREATE)\b",
        text,
        flags=re.IGNORECASE,
    )


def test_workbench_verification_covers_required_queries() -> None:
    text = read("07_verification_queries.sql").lower()
    for token in [
        "select version()",
        "select database()",
        "show tables",
        "information_schema.table_constraints",
        "v_low_stock_components",
        "v_request_progress",
        "v_transfer_detail",
        "v_overdue_returns",
        "v_disposal_summary",
        "group by",
    ]:
        assert token in text


def test_seed_supports_all_roles_and_core_workflows() -> None:
    seed = read("06_seed_data.sql")
    for token in [
        "'STUDENT'",
        "'FACULTY'",
        "'LAB_ASSISTANT'",
        "'ADMINISTRATOR'",
        "'RECEIVED'",
        "'APPROVED'",
        "'PARTIALLY_APPROVED'",
        "return_due_date",
        "disposal_record",
    ]:
        assert token in seed


def test_optional_faculty_demo_scripts_are_safe_and_explainable() -> None:
    constraint = (SQL / "demo/01_constraint_demo.sql").read_text(encoding="utf-8")
    transaction = (SQL / "demo/02_transaction_demo.sql").read_text(encoding="utf-8")
    explain = (SQL / "demo/03_index_and_explain_demo.sql").read_text(encoding="utf-8")
    assert constraint.count("EXPECTED FAILURE") >= 5
    assert "START TRANSACTION" in transaction
    assert "ROLLBACK" in transaction
    assert "rollback_restored_original" in transaction
    assert explain.upper().count("EXPLAIN") >= 4
