"""MySQL-only academic feature, seed, valuation, and trigger verification."""

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import DBAPIError


pytestmark = pytest.mark.integration


def test_expected_routines_are_visible(mysql_connection: Connection) -> None:
    rows = set(
        mysql_connection.execute(
            text(
                "SELECT routine_name, routine_type FROM information_schema.routines "
                "WHERE routine_schema = DATABASE()"
            )
        )
    )
    assert ("fn_inventory_available_value", "FUNCTION") in rows
    assert ("sp_component_availability", "PROCEDURE") in rows


def test_inventory_value_function(mysql_connection: Connection) -> None:
    value = mysql_connection.execute(
        text("SELECT fn_inventory_available_value(5, 12.50)")
    ).scalar_one()
    assert float(value) == 62.50


def test_required_secondary_indexes_are_visible(mysql_connection: Connection) -> None:
    names = set(
        mysql_connection.execute(
            text(
                "SELECT index_name FROM information_schema.statistics "
                "WHERE table_schema = DATABASE()"
            )
        ).scalars()
    )
    assert {
        "idx_request_status_date",
        "idx_transfer_source_status",
        "idx_transfer_item_overdue",
        "idx_disposal_date_inventory",
    } <= names


def test_seed_contains_partial_approval_and_reserved_valuation(
    mysql_connection: Connection,
) -> None:
    status = mysql_connection.execute(
        text("SELECT request_status FROM component_request WHERE request_id = 5")
    ).scalar_one()
    assert status == "PARTIALLY_APPROVED"
    row = mysql_connection.execute(
        text(
            "SELECT quantity_available, quantity_reserved, inventory_value "
            "FROM v_inventory_detail WHERE inventory_id = 5"
        )
    ).one()
    assert tuple(row[:2]) == (9, 3)
    assert float(row[2]) == 12 * 620.00


def test_approval_above_requested_is_rejected(mysql_connection: Connection) -> None:
    with pytest.raises(DBAPIError):
        mysql_connection.execute(
            text(
                "UPDATE request_item SET quantity_approved = quantity_requested + 1 "
                "WHERE request_item_id = 6"
            )
        )


def test_inventory_location_update_trigger_rejects_cross_lab_position(
    mysql_connection: Connection,
) -> None:
    inventory_id, inventory_lab = mysql_connection.execute(
        text("SELECT inventory_id, lab_id FROM inventory ORDER BY inventory_id LIMIT 1")
    ).one()
    other_location = mysql_connection.execute(
        text(
            "SELECT storage_location_id FROM storage_location "
            "WHERE lab_id <> :lab_id ORDER BY storage_location_id LIMIT 1"
        ),
        {"lab_id": inventory_lab},
    ).scalar_one()
    with pytest.raises(DBAPIError):
        mysql_connection.execute(
            text(
                "UPDATE inventory SET storage_location_id = :location_id "
                "WHERE inventory_id = :inventory_id"
            ),
            {"location_id": other_location, "inventory_id": inventory_id},
        )
