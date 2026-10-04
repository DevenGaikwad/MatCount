"""Additional rollback-isolated MySQL constraints and view checks."""

import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import DBAPIError


pytestmark = pytest.mark.integration


def test_unique_component_category(mysql_connection: Connection) -> None:
    category_name = mysql_connection.execute(
        text("SELECT category_name FROM component_category LIMIT 1")
    ).scalar_one()
    with pytest.raises(DBAPIError):
        mysql_connection.execute(
            text(
                "INSERT INTO component_category (category_name) VALUES (:category_name)"
            ),
            {"category_name": category_name},
        )


def test_request_item_pair_is_unique(mysql_connection: Connection) -> None:
    request_id, component_id = mysql_connection.execute(
        text("SELECT request_id, component_id FROM request_item LIMIT 1")
    ).one()
    with pytest.raises(DBAPIError):
        mysql_connection.execute(
            text(
                "INSERT INTO request_item "
                "(request_id, component_id, quantity_requested, quantity_approved) "
                "VALUES (:request_id, :component_id, 1, 0)"
            ),
            {"request_id": request_id, "component_id": component_id},
        )


def test_transfer_item_pair_is_unique(mysql_connection: Connection) -> None:
    transfer_id, inventory_id = mysql_connection.execute(
        text("SELECT transfer_id, inventory_id FROM transfer_item LIMIT 1")
    ).one()
    with pytest.raises(DBAPIError):
        mysql_connection.execute(
            text(
                "INSERT INTO transfer_item "
                "(transfer_id, inventory_id, quantity_sent, quantity_received) "
                "VALUES (:transfer_id, :inventory_id, 1, 0)"
            ),
            {"transfer_id": transfer_id, "inventory_id": inventory_id},
        )


def test_invalid_request_dates_are_rejected(mysql_connection: Connection) -> None:
    user_id, lab_id = mysql_connection.execute(
        text("SELECT user_id, lab_id FROM `user` ORDER BY user_id LIMIT 1")
    ).one()
    with pytest.raises(DBAPIError):
        mysql_connection.execute(
            text(
                "INSERT INTO component_request "
                "(requesting_lab_id, created_by, request_date, required_by_date, reason) "
                "VALUES (:lab_id, :user_id, '2026-08-20', '2026-08-19', 'Invalid date test')"
            ),
            {"lab_id": lab_id, "user_id": user_id},
        )


def test_quantity_and_fk_constraints(mysql_connection: Connection) -> None:
    inventory_id = mysql_connection.execute(
        text("SELECT inventory_id FROM inventory LIMIT 1")
    ).scalar_one()
    with pytest.raises(DBAPIError):
        mysql_connection.execute(
            text(
                "UPDATE inventory SET quantity_available = -1 "
                "WHERE inventory_id = :inventory_id"
            ),
            {"inventory_id": inventory_id},
        )


def test_foreign_key_integrity(mysql_connection: Connection) -> None:
    with pytest.raises(DBAPIError):
        mysql_connection.execute(
            text(
                "INSERT INTO lab_contact (lab_id, contact_number) "
                "VALUES (999999999, :number)"
            ),
            {"number": f"X-{uuid.uuid4().hex[:8]}"},
        )


def test_seeded_reservation_and_reporting_values(mysql_connection: Connection) -> None:
    stock = mysql_connection.execute(
        text(
            "SELECT quantity_available, quantity_reserved FROM inventory "
            "WHERE inventory_id = 5"
        )
    ).one()
    assert tuple(stock) == (9, 3)
    valuation = mysql_connection.execute(
        text("SELECT SUM(available_value) FROM v_inventory_detail")
    ).scalar_one()
    assert valuation is not None and valuation > 0
    assert mysql_connection.execute(
        text("SELECT COUNT(*) FROM v_low_stock_components")
    ).scalar_one() > 0

