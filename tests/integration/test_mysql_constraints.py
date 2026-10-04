"""Rollback-isolated MySQL constraint tests; skipped without test URL."""

import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import DBAPIError, IntegrityError


pytestmark = pytest.mark.integration


def test_unique_user_email(mysql_connection: Connection) -> None:
    row = mysql_connection.execute(
        text("SELECT lab_id, email FROM `user` ORDER BY user_id LIMIT 1")
    ).mappings().one()
    with pytest.raises(IntegrityError):
        mysql_connection.execute(
            text(
                "INSERT INTO `user` (lab_id, full_name, email, role, account_status) "
                "VALUES (:lab_id, 'Duplicate', :email, 'STUDENT', 'ACTIVE')"
            ),
            dict(row),
        )


def test_nullable_part_numbers_allow_multiple_nulls(mysql_connection: Connection) -> None:
    category_id = mysql_connection.execute(
        text("SELECT category_id FROM component_category ORDER BY category_id LIMIT 1")
    ).scalar_one()
    suffix = uuid.uuid4().hex[:8]
    mysql_connection.execute(
        text(
            "INSERT INTO component "
            "(category_id, component_name, part_number, unit_of_measure, minimum_stock_level) "
            "VALUES (:category_id, :name, NULL, 'piece', 0)"
        ),
        {"category_id": category_id, "name": f"Null Part A {suffix}"},
    )
    mysql_connection.execute(
        text(
            "INSERT INTO component "
            "(category_id, component_name, part_number, unit_of_measure, minimum_stock_level) "
            "VALUES (:category_id, :name, NULL, 'piece', 0)"
        ),
        {"category_id": category_id, "name": f"Null Part B {suffix}"},
    )


def test_distinct_transfer_labs_check(mysql_connection: Connection) -> None:
    request_id = mysql_connection.execute(
        text("SELECT request_id FROM component_request ORDER BY request_id LIMIT 1")
    ).scalar_one()
    user_id, lab_id = mysql_connection.execute(
        text("SELECT user_id, lab_id FROM `user` ORDER BY user_id LIMIT 1")
    ).one()
    with pytest.raises(IntegrityError):
        mysql_connection.execute(
            text(
                "INSERT INTO transfer "
                "(request_id, source_lab_id, destination_lab_id, created_by) "
                "VALUES (:request_id, :lab_id, :lab_id, :user_id)"
            ),
            {"request_id": request_id, "lab_id": lab_id, "user_id": user_id},
        )


def test_same_lab_inventory_location_trigger(mysql_connection: Connection) -> None:
    labs = mysql_connection.execute(
        text("SELECT lab_id FROM lab ORDER BY lab_id LIMIT 2")
    ).scalars().all()
    if len(labs) < 2:
        pytest.skip("Seed data requires at least two labs")
    component_id = mysql_connection.execute(
        text("SELECT component_id FROM component ORDER BY component_id LIMIT 1")
    ).scalar_one()
    location_id = mysql_connection.execute(
        text(
            "SELECT storage_location_id FROM storage_location "
            "WHERE lab_id = :lab_id ORDER BY storage_location_id LIMIT 1"
        ),
        {"lab_id": labs[1]},
    ).scalar_one()
    with pytest.raises(DBAPIError):
        mysql_connection.execute(
            text(
                "INSERT INTO inventory "
                "(lab_id, component_id, storage_location_id, quantity_available, "
                " quantity_reserved, unit_cost, inventory_status) "
                "VALUES (:lab_id, :component_id, :location_id, 1, 0, 1.00, 'AVAILABLE')"
            ),
            {
                "lab_id": labs[0],
                "component_id": component_id,
                "location_id": location_id,
            },
        )

