"""Read-only MySQL 8.4 integration checks; skipped without test URL."""

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Connection


pytestmark = pytest.mark.integration


EXPECTED_TABLES = {
    "lab",
    "lab_contact",
    "user",
    "user_phone",
    "component_category",
    "component",
    "storage_location",
    "inventory",
    "component_request",
    "request_item",
    "transfer",
    "transfer_item",
    "disposal_record",
}


def test_mysql_version_and_exact_schema(mysql_connection: Connection) -> None:
    version = str(mysql_connection.execute(text("SELECT VERSION()" )).scalar_one())
    assert version.startswith("8.4.11")
    tables = set(
        mysql_connection.execute(
            text(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = DATABASE() AND table_type = 'BASE TABLE'
                """
            )
        ).scalars()
    )
    assert tables == EXPECTED_TABLES


def test_required_views_and_triggers_exist(mysql_connection: Connection) -> None:
    views = set(
        mysql_connection.execute(
            text(
                """
                SELECT table_name FROM information_schema.views
                WHERE table_schema = DATABASE()
                """
            )
        ).scalars()
    )
    assert {
        "v_inventory_detail",
        "v_component_stock_summary",
        "v_low_stock_components",
        "v_request_progress",
        "v_transfer_detail",
        "v_overdue_returns",
        "v_disposal_summary",
    } <= views
    trigger_count = mysql_connection.execute(
        text(
            "SELECT COUNT(*) FROM information_schema.triggers "
            "WHERE trigger_schema = DATABASE()"
        )
    ).scalar_one()
    assert trigger_count == 2


def test_seeded_views_return_rows(mysql_connection: Connection) -> None:
    assert mysql_connection.execute(text("SELECT COUNT(*) FROM v_inventory_detail")).scalar_one() > 0
    assert mysql_connection.execute(text("SELECT COUNT(*) FROM v_request_progress")).scalar_one() > 0
    assert mysql_connection.execute(text("SELECT COUNT(*) FROM v_transfer_detail")).scalar_one() > 0
