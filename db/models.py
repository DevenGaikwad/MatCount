"""SQLAlchemy mappings for the exactly 13 frozen SEMS relations."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    Enum,
    ForeignKey,
    String,
    Text,
    TIMESTAMP,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.mysql import BIGINT, DECIMAL, INTEGER
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import quoted_name


class Base(DeclarativeBase):
    """Declarative base for frozen SEMS mappings."""


class Lab(Base):
    __tablename__ = "lab"
    __table_args__ = (
        UniqueConstraint("lab_name", "department_name", name="uq_lab_name_department"),
    )

    lab_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True)
    lab_name: Mapped[str] = mapped_column(String(120), nullable=False)
    department_name: Mapped[str] = mapped_column(String(120), nullable=False)
    building_name: Mapped[str] = mapped_column(String(120), nullable=False)
    lab_type: Mapped[str] = mapped_column(String(60), nullable=False)


class LabContact(Base):
    __tablename__ = "lab_contact"

    lab_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("lab.lab_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    contact_number: Mapped[str] = mapped_column(String(20), primary_key=True)


class User(Base):
    __tablename__ = quoted_name("user", True)
    __table_args__ = (UniqueConstraint("email", name="uq_user_email"),)

    user_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True)
    lab_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("lab.lab_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(190), nullable=False)
    role: Mapped[str] = mapped_column(
        Enum(
            "STUDENT",
            "FACULTY",
            "LAB_ASSISTANT",
            "ADMINISTRATOR",
            name="user_role",
        ),
        nullable=False,
    )
    account_status: Mapped[str] = mapped_column(
        Enum("ACTIVE", "INACTIVE", "SUSPENDED", name="user_account_status"),
        nullable=False,
        server_default=text("'ACTIVE'"),
    )


class UserPhone(Base):
    __tablename__ = "user_phone"

    user_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("user.user_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    phone_number: Mapped[str] = mapped_column(String(20), primary_key=True)


class ComponentCategory(Base):
    __tablename__ = "component_category"
    __table_args__ = (
        UniqueConstraint("category_name", name="uq_component_category_name"),
    )

    category_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True)
    category_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)


class Component(Base):
    __tablename__ = "component"
    __table_args__ = (
        UniqueConstraint("part_number", name="uq_component_part_number"),
        CheckConstraint("minimum_stock_level >= 0", name="ck_component_minimum_stock"),
    )

    component_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True)
    category_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "component_category.category_id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    component_name: Mapped[str] = mapped_column(String(160), nullable=False)
    part_number: Mapped[str | None] = mapped_column(String(120), nullable=True)
    specification: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit_of_measure: Mapped[str] = mapped_column(String(30), nullable=False)
    minimum_stock_level: Mapped[int] = mapped_column(
        INTEGER(unsigned=True), nullable=False, server_default=text("0")
    )
    manufacturer_details: Mapped[str | None] = mapped_column(String(255), nullable=True)


class StorageLocation(Base):
    __tablename__ = "storage_location"
    __table_args__ = (
        UniqueConstraint(
            "lab_id",
            "cabinet_no",
            "shelf_no",
            "drawer_no",
            "location_type",
            name="uq_storage_coordinate",
        ),
    )

    storage_location_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True
    )
    lab_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("lab.lab_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    cabinet_no: Mapped[str] = mapped_column(String(30), nullable=False)
    shelf_no: Mapped[str | None] = mapped_column(String(30), nullable=True)
    drawer_no: Mapped[str | None] = mapped_column(String(30), nullable=True)
    location_type: Mapped[str] = mapped_column(String(50), nullable=False)


class Inventory(Base):
    __tablename__ = "inventory"
    __table_args__ = (
        UniqueConstraint(
            "lab_id",
            "component_id",
            "storage_location_id",
            name="uq_inventory_position",
        ),
        CheckConstraint(
            "quantity_available >= 0", name="ck_inventory_available_nonnegative"
        ),
        CheckConstraint(
            "quantity_reserved >= 0", name="ck_inventory_reserved_nonnegative"
        ),
        CheckConstraint("unit_cost >= 0", name="ck_inventory_unit_cost_nonnegative"),
    )

    inventory_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True)
    lab_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("lab.lab_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    component_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("component.component_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    storage_location_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "storage_location.storage_location_id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    quantity_available: Mapped[int] = mapped_column(
        INTEGER(unsigned=True), nullable=False, server_default=text("0")
    )
    quantity_reserved: Mapped[int] = mapped_column(
        INTEGER(unsigned=True), nullable=False, server_default=text("0")
    )
    unit_cost: Mapped[Decimal] = mapped_column(
        DECIMAL(12, 2, unsigned=True), nullable=False, server_default=text("0.00")
    )
    inventory_status: Mapped[str] = mapped_column(
        Enum(
            "AVAILABLE",
            "LOW_STOCK",
            "OUT_OF_STOCK",
            "BLOCKED",
            "INACTIVE",
            name="inventory_status",
        ),
        nullable=False,
        server_default=text("'AVAILABLE'"),
    )
    last_updated: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )


class ComponentRequest(Base):
    __tablename__ = "component_request"
    __table_args__ = (
        CheckConstraint(
            "required_by_date >= request_date", name="ck_component_request_dates"
        ),
    )

    request_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True)
    requesting_lab_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("lab.lab_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    created_by: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("user.user_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    request_date: Mapped[date] = mapped_column(Date, nullable=False)
    required_by_date: Mapped[date] = mapped_column(Date, nullable=False)
    priority: Mapped[str] = mapped_column(
        Enum("LOW", "MEDIUM", "HIGH", "URGENT", name="request_priority"),
        nullable=False,
        server_default=text("'MEDIUM'"),
    )
    reason: Mapped[str] = mapped_column(String(1000), nullable=False)
    request_status: Mapped[str] = mapped_column(
        Enum(
            "DRAFT",
            "SUBMITTED",
            "PARTIALLY_APPROVED",
            "APPROVED",
            "FULFILLED",
            "REJECTED",
            "CANCELLED",
            name="request_status",
        ),
        nullable=False,
        server_default=text("'DRAFT'"),
    )


class RequestItem(Base):
    __tablename__ = "request_item"
    __table_args__ = (
        UniqueConstraint(
            "request_id", "component_id", name="uq_request_item_component"
        ),
        CheckConstraint(
            "quantity_requested > 0", name="ck_request_item_requested_positive"
        ),
        CheckConstraint(
            "quantity_approved <= quantity_requested",
            name="ck_request_item_approval_range",
        ),
    )

    request_item_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True
    )
    request_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "component_request.request_id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    component_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("component.component_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity_requested: Mapped[int] = mapped_column(
        INTEGER(unsigned=True), nullable=False
    )
    quantity_approved: Mapped[int] = mapped_column(
        INTEGER(unsigned=True), nullable=False, server_default=text("0")
    )
    item_status: Mapped[str] = mapped_column(
        Enum(
            "PENDING",
            "PARTIALLY_APPROVED",
            "APPROVED",
            "REJECTED",
            "ALLOCATED",
            "FULFILLED",
            name="request_item_status",
        ),
        nullable=False,
        server_default=text("'PENDING'"),
    )
    remarks: Mapped[str | None] = mapped_column(String(500), nullable=True)


class Transfer(Base):
    __tablename__ = "transfer"
    __table_args__ = (
        CheckConstraint(
            "source_lab_id <> destination_lab_id", name="ck_transfer_distinct_labs"
        ),
        CheckConstraint(
            "received_date IS NULL OR "
            "(dispatch_date IS NOT NULL AND received_date >= dispatch_date)",
            name="ck_transfer_received_after_dispatch",
        ),
        CheckConstraint(
            "(received_by IS NULL AND received_date IS NULL) OR "
            "(received_by IS NOT NULL AND received_date IS NOT NULL)",
            name="ck_transfer_receipt_pair",
        ),
    )

    transfer_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True)
    request_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "component_request.request_id", onupdate="CASCADE", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    source_lab_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("lab.lab_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    destination_lab_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("lab.lab_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    created_by: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("user.user_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    received_by: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("user.user_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=True,
    )
    dispatch_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    received_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    transfer_status: Mapped[str] = mapped_column(
        Enum(
            "DRAFT",
            "APPROVED",
            "DISPATCHED",
            "RECEIVED",
            "PARTIALLY_RETURNED",
            "RETURNED",
            "CANCELLED",
            name="transfer_status",
        ),
        nullable=False,
        server_default=text("'DRAFT'"),
    )
    approval_status: Mapped[str] = mapped_column(
        Enum("PENDING", "APPROVED", "REJECTED", name="transfer_approval_status"),
        nullable=False,
        server_default=text("'PENDING'"),
    )


class TransferItem(Base):
    __tablename__ = "transfer_item"
    __table_args__ = (
        UniqueConstraint(
            "transfer_id", "inventory_id", name="uq_transfer_item_inventory"
        ),
        CheckConstraint(
            "quantity_sent > 0", name="ck_transfer_item_sent_positive"
        ),
        CheckConstraint(
            "quantity_received <= quantity_sent",
            name="ck_transfer_item_received_range",
        ),
        CheckConstraint(
            "return_date IS NULL OR return_due_date IS NOT NULL",
            name="ck_transfer_item_return_date",
        ),
    )

    transfer_item_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True
    )
    transfer_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("transfer.transfer_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    inventory_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "inventory.inventory_id", onupdate="CASCADE", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    quantity_sent: Mapped[int] = mapped_column(INTEGER(unsigned=True), nullable=False)
    quantity_received: Mapped[int] = mapped_column(
        INTEGER(unsigned=True), nullable=False, server_default=text("0")
    )
    return_due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    return_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    condition_on_issue: Mapped[str | None] = mapped_column(String(100), nullable=True)
    condition_on_return: Mapped[str | None] = mapped_column(String(100), nullable=True)


class DisposalRecord(Base):
    __tablename__ = "disposal_record"
    __table_args__ = (
        CheckConstraint(
            "quantity_disposed > 0", name="ck_disposal_quantity_positive"
        ),
    )

    disposal_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True)
    inventory_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "inventory.inventory_id", onupdate="CASCADE", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    authorized_by: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("user.user_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity_disposed: Mapped[int] = mapped_column(
        INTEGER(unsigned=True), nullable=False
    )
    disposal_date: Mapped[date] = mapped_column(Date, nullable=False)
    disposal_reason: Mapped[str] = mapped_column(String(500), nullable=False)
    disposal_method: Mapped[str] = mapped_column(String(120), nullable=False)
    remarks: Mapped[str | None] = mapped_column(String(500), nullable=True)


FROZEN_MODEL_CLASSES = (
    Lab,
    LabContact,
    User,
    UserPhone,
    ComponentCategory,
    Component,
    StorageLocation,
    Inventory,
    ComponentRequest,
    RequestItem,
    Transfer,
    TransferItem,
    DisposalRecord,
)
