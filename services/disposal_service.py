"""Administrator-only atomic inventory disposal workflow."""

from __future__ import annotations

from datetime import date

from config.constants import Role
from db.session import session_scope
from repositories import (
    component_repository,
    disposal_repository,
    inventory_repository,
)
from services.exceptions import NotFoundError
from services.rbac import Actor, revalidate_actor, require_roles
from services.rules import StockSnapshot, inventory_status, remove_free_stock
from services.validation import actual_date, optional_text, positive_int, required_text


def list_disposals(actor: Actor, *, inventory_id: int | None = None):
    require_roles(actor, [Role.ADMINISTRATOR])
    with session_scope() as session:
        revalidate_actor(session, actor)
        return disposal_repository.list_disposals(
            session, inventory_id=inventory_id
        )


def dispose_inventory(
    actor: Actor,
    *,
    inventory_id: int,
    quantity_disposed: int,
    disposal_date: date,
    disposal_reason: str,
    disposal_method: str,
    remarks: str | None = None,
):
    require_roles(actor, [Role.ADMINISTRATOR])
    inventory_id = positive_int(inventory_id, "Inventory ID")
    quantity_disposed = positive_int(quantity_disposed, "Disposal quantity")
    disposal_date = actual_date(disposal_date, "Disposal date")
    disposal_reason = required_text(
        disposal_reason, "Disposal reason", max_length=500
    )
    disposal_method = required_text(
        disposal_method, "Disposal method", max_length=120
    )
    remarks = optional_text(remarks, "Disposal remarks", max_length=500)

    with session_scope() as session:
        revalidate_actor(session, actor)
        inventory = inventory_repository.get_inventory(
            session, inventory_id, for_update=True
        )
        if inventory is None:
            raise NotFoundError("Inventory record not found.")
        next_stock = remove_free_stock(
            StockSnapshot(
                inventory.quantity_available, inventory.quantity_reserved
            ),
            quantity_disposed,
        )
        record = disposal_repository.create_disposal(
            session,
            inventory_id=inventory_id,
            authorized_by=actor.user_id,
            quantity_disposed=quantity_disposed,
            disposal_date=disposal_date,
            disposal_reason=disposal_reason,
            disposal_method=disposal_method,
            remarks=remarks,
        )
        inventory.quantity_available = next_stock.available
        component = component_repository.get_component(
            session, inventory.component_id
        )
        if component is None:
            raise NotFoundError("Component not found.")
        inventory.inventory_status = inventory_status(
            inventory.quantity_available,
            component.minimum_stock_level,
            inventory.inventory_status,
        )
        session.flush()
        return record
