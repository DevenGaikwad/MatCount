"""ORM mapping checks against the frozen relational boundary."""

import pytest
from sqlalchemy.dialects import mysql
from sqlalchemy.schema import CreateTable

from db.models import Base, FROZEN_MODEL_CLASSES, TransferItem, User


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
pytestmark = pytest.mark.contract

EXPECTED_COLUMNS = {
    "lab": {"lab_id", "lab_name", "department_name", "building_name", "lab_type"},
    "lab_contact": {"lab_id", "contact_number"},
    "user": {"user_id", "lab_id", "full_name", "email", "role", "account_status"},
    "user_phone": {"user_id", "phone_number"},
    "component_category": {"category_id", "category_name", "description"},
    "component": {
        "component_id", "category_id", "component_name", "part_number",
        "specification", "unit_of_measure", "minimum_stock_level",
        "manufacturer_details",
    },
    "storage_location": {
        "storage_location_id", "lab_id", "cabinet_no", "shelf_no", "drawer_no",
        "location_type",
    },
    "inventory": {
        "inventory_id", "lab_id", "component_id", "storage_location_id",
        "quantity_available", "quantity_reserved", "unit_cost", "inventory_status",
        "last_updated",
    },
    "component_request": {
        "request_id", "requesting_lab_id", "created_by", "request_date",
        "required_by_date", "priority", "reason", "request_status",
    },
    "request_item": {
        "request_item_id", "request_id", "component_id", "quantity_requested",
        "quantity_approved", "item_status", "remarks",
    },
    "transfer": {
        "transfer_id", "request_id", "source_lab_id", "destination_lab_id",
        "created_by", "received_by", "dispatch_date", "received_date",
        "transfer_status", "approval_status",
    },
    "transfer_item": {
        "transfer_item_id", "transfer_id", "inventory_id", "quantity_sent",
        "quantity_received", "return_due_date", "return_date",
        "condition_on_issue", "condition_on_return",
    },
    "disposal_record": {
        "disposal_id", "inventory_id", "authorized_by", "quantity_disposed",
        "disposal_date", "disposal_reason", "disposal_method", "remarks",
    },
}

EXPECTED_PRIMARY_KEYS = {
    "lab": ("lab_id",),
    "lab_contact": ("lab_id", "contact_number"),
    "user": ("user_id",),
    "user_phone": ("user_id", "phone_number"),
    "component_category": ("category_id",),
    "component": ("component_id",),
    "storage_location": ("storage_location_id",),
    "inventory": ("inventory_id",),
    "component_request": ("request_id",),
    "request_item": ("request_item_id",),
    "transfer": ("transfer_id",),
    "transfer_item": ("transfer_item_id",),
    "disposal_record": ("disposal_id",),
}

EXPECTED_FOREIGN_KEYS = {
    ("lab_contact", "lab_id", "lab", "lab_id"),
    ("user", "lab_id", "lab", "lab_id"),
    ("user_phone", "user_id", "user", "user_id"),
    ("component", "category_id", "component_category", "category_id"),
    ("storage_location", "lab_id", "lab", "lab_id"),
    ("inventory", "lab_id", "lab", "lab_id"),
    ("inventory", "component_id", "component", "component_id"),
    (
        "inventory", "storage_location_id", "storage_location",
        "storage_location_id",
    ),
    ("component_request", "requesting_lab_id", "lab", "lab_id"),
    ("component_request", "created_by", "user", "user_id"),
    ("request_item", "request_id", "component_request", "request_id"),
    ("request_item", "component_id", "component", "component_id"),
    ("transfer", "request_id", "component_request", "request_id"),
    ("transfer", "source_lab_id", "lab", "lab_id"),
    ("transfer", "destination_lab_id", "lab", "lab_id"),
    ("transfer", "created_by", "user", "user_id"),
    ("transfer", "received_by", "user", "user_id"),
    ("transfer_item", "transfer_id", "transfer", "transfer_id"),
    ("transfer_item", "inventory_id", "inventory", "inventory_id"),
    ("disposal_record", "inventory_id", "inventory", "inventory_id"),
    ("disposal_record", "authorized_by", "user", "user_id"),
}


def test_exactly_thirteen_frozen_model_tables() -> None:
    assert set(Base.metadata.tables) == EXPECTED_TABLES
    assert len(FROZEN_MODEL_CLASSES) == 13


def test_every_model_has_exact_frozen_columns_and_primary_key() -> None:
    for name, expected_columns in EXPECTED_COLUMNS.items():
        table = Base.metadata.tables[name]
        assert set(table.columns.keys()) == expected_columns
        assert tuple(column.name for column in table.primary_key.columns) == (
            EXPECTED_PRIMARY_KEYS[name]
        )


def test_only_frozen_nullable_columns_are_nullable() -> None:
    expected_nullable = {
        "component_category": {"description"},
        "component": {"part_number", "specification", "manufacturer_details"},
        "storage_location": {"shelf_no", "drawer_no"},
        "request_item": {"remarks"},
        "transfer": {"received_by", "dispatch_date", "received_date"},
        "transfer_item": {
            "return_due_date", "return_date", "condition_on_issue",
            "condition_on_return",
        },
        "disposal_record": {"remarks"},
    }
    for table in Base.metadata.tables.values():
        nullable = {
            column.name
            for column in table.columns
            if column.nullable and not column.primary_key
        }
        assert nullable == expected_nullable.get(table.name, set())


def test_exact_frozen_foreign_key_placements() -> None:
    actual = {
        (
            table.name,
            foreign_key.parent.name,
            foreign_key.column.table.name,
            foreign_key.column.name,
        )
        for table in Base.metadata.tables.values()
        for foreign_key in table.foreign_keys
    }
    assert actual == EXPECTED_FOREIGN_KEYS


def test_user_is_quoted_for_mysql() -> None:
    ddl = str(CreateTable(User.__table__).compile(dialect=mysql.dialect()))
    assert "CREATE TABLE `user`" in ddl


def test_transfer_item_has_no_destination_inventory_fk() -> None:
    assert "destination_inventory_id" not in TransferItem.__table__.columns
    assert "password_hash" not in User.__table__.columns


def test_transfer_item_unique_pair_and_source_inventory_fk() -> None:
    unique_columns = {
        tuple(column.name for column in constraint.columns)
        for constraint in TransferItem.__table__.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    }
    assert ("transfer_id", "inventory_id") in unique_columns
    target_tables = {
        fk.column.table.name for fk in TransferItem.__table__.foreign_keys
    }
    assert target_tables == {"transfer", "inventory"}
