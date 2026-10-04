"""Role-aware inventory registration, search and controlled adjustment."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from config.constants import InventoryStatus, Role
from db.session import session_scope
from repositories import (
    component_repository,
    inventory_repository,
    lab_repository,
)
from services.exceptions import NotFoundError, ValidationError
from services.rbac import Actor, revalidate_actor, require_lab_scope, require_roles
from services.rules import StockSnapshot, add_received, inventory_status
from services.validation import nonnegative_decimal, nonnegative_int, positive_int


def list_inventory(
    actor: Actor,
    *,
    lab_id: int | None = None,
    component_id: int | None = None,
    status: str | None = None,
):
    require_roles(actor, [Role.LAB_ASSISTANT, Role.ADMINISTRATOR])
    if lab_id is not None:
        lab_id = positive_int(lab_id, "Laboratory ID")
    if component_id is not None:
        component_id = positive_int(component_id, "Component ID")
    if status is not None and status not in {item.value for item in InventoryStatus}:
        raise ValidationError("Invalid inventory status filter.")
    if actor.role != Role.ADMINISTRATOR.value:
        lab_id = actor.lab_id if lab_id is None else lab_id
        require_lab_scope(actor, lab_id)
    with session_scope() as session:
        revalidate_actor(session, actor)
        return inventory_repository.list_inventory(
            session, lab_id=lab_id, component_id=component_id, status=status
        )


def create_inventory(
    actor: Actor,
    *,
    lab_id: int,
    component_id: int,
    storage_location_id: int,
    quantity_available: int,
    unit_cost: Decimal,
):
    require_roles(actor, [Role.LAB_ASSISTANT, Role.ADMINISTRATOR])
    lab_id = positive_int(lab_id, "Laboratory ID")
    require_lab_scope(actor, lab_id)
    component_id = positive_int(component_id, "Component ID")
    storage_location_id = positive_int(storage_location_id, "Storage-location ID")
    quantity_available = nonnegative_int(quantity_available, "Available quantity")
    unit_cost = nonnegative_decimal(unit_cost, "Unit cost")
    try:
        with session_scope() as session:
            revalidate_actor(session, actor)
            location = lab_repository.get_location(session, storage_location_id)
            component = component_repository.get_component(session, component_id)
            if location is None or component is None:
                raise NotFoundError("Component or storage location not found.")
            if location.lab_id != lab_id:
                raise ValidationError(
                    "Inventory laboratory must match the storage-location laboratory."
                )
            status = inventory_status(
                quantity_available,
                component.minimum_stock_level,
                InventoryStatus.AVAILABLE.value,
            )
            return inventory_repository.create_inventory(
                session,
                lab_id=lab_id,
                component_id=component_id,
                storage_location_id=storage_location_id,
                quantity_available=quantity_available,
                quantity_reserved=0,
                unit_cost=unit_cost,
                inventory_status=status,
            )
    except IntegrityError:
        raise ValidationError(
            "An inventory record already exists for this lab, component and location."
        ) from None


def restock_inventory(actor: Actor, inventory_id: int, quantity: int):
    require_roles(actor, [Role.LAB_ASSISTANT, Role.ADMINISTRATOR])
    inventory_id = positive_int(inventory_id, "Inventory ID")
    quantity = positive_int(quantity, "Restock quantity")
    with session_scope() as session:
        revalidate_actor(session, actor)
        record = inventory_repository.get_inventory(session, inventory_id, for_update=True)
        if record is None:
            raise NotFoundError("Inventory record not found.")
        require_lab_scope(actor, record.lab_id)
        component = component_repository.get_component(session, record.component_id)
        if component is None:
            raise NotFoundError("Component not found.")
        next_stock = add_received(
            StockSnapshot(record.quantity_available, record.quantity_reserved), quantity
        )
        record.quantity_available = next_stock.available
        record.inventory_status = inventory_status(
            next_stock.available, component.minimum_stock_level, record.inventory_status
        )
        session.flush()
        return record


def update_inventory_metadata(
    actor: Actor,
    inventory_id: int,
    *,
    storage_location_id: int,
    unit_cost: Decimal,
):
    require_roles(actor, [Role.LAB_ASSISTANT, Role.ADMINISTRATOR])
    inventory_id = positive_int(inventory_id, "Inventory ID")
    storage_location_id = positive_int(storage_location_id, "Storage-location ID")
    unit_cost = nonnegative_decimal(unit_cost, "Unit cost")
    with session_scope() as session:
        revalidate_actor(session, actor)
        record = inventory_repository.get_inventory(session, inventory_id, for_update=True)
        if record is None:
            raise NotFoundError("Inventory record not found.")
        require_lab_scope(actor, record.lab_id)
        location = lab_repository.get_location(session, storage_location_id)
        if location is None or location.lab_id != record.lab_id:
            raise ValidationError("Storage location must belong to the inventory lab.")
        record.storage_location_id = storage_location_id
        record.unit_cost = unit_cost
        try:
            session.flush()
        except IntegrityError:
            raise ValidationError(
                "The selected inventory position already exists."
            ) from None
        return record


def set_operational_status(actor: Actor, inventory_id: int, status: str):
    require_roles(actor, [Role.LAB_ASSISTANT, Role.ADMINISTRATOR])
    if status not in {
        InventoryStatus.AVAILABLE.value,
        InventoryStatus.BLOCKED.value,
        InventoryStatus.INACTIVE.value,
    }:
        raise ValidationError("Unsupported manual inventory status.")
    inventory_id = positive_int(inventory_id, "Inventory ID")
    with session_scope() as session:
        revalidate_actor(session, actor)
        record = inventory_repository.get_inventory(session, inventory_id, for_update=True)
        if record is None:
            raise NotFoundError("Inventory record not found.")
        require_lab_scope(actor, record.lab_id)
        if (
            status in {InventoryStatus.BLOCKED.value, InventoryStatus.INACTIVE.value}
            and record.quantity_reserved > 0
        ):
            raise ValidationError(
                "Reserved inventory cannot be blocked or deactivated; dispatch or cancel its transfer first."
            )
        if status == InventoryStatus.AVAILABLE.value:
            component = component_repository.get_component(session, record.component_id)
            if component is None:
                raise NotFoundError("Component not found.")
            status = inventory_status(
                record.quantity_available,
                component.minimum_stock_level,
                InventoryStatus.AVAILABLE.value,
            )
        record.inventory_status = status
        session.flush()
        return record
