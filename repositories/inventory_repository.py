"""Inventory persistence, lookup and row-lock operations."""

from __future__ import annotations

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from db.models import Inventory


def get_inventory(
    session: Session, inventory_id: int, *, for_update: bool = False
) -> Inventory | None:
    statement = select(Inventory).where(Inventory.inventory_id == inventory_id)
    if for_update:
        statement = statement.with_for_update()
    return session.scalar(statement)


def get_inventory_rows_for_update(
    session: Session, inventory_ids: list[int]
) -> list[Inventory]:
    ordered_ids = sorted(set(inventory_ids))
    if not ordered_ids:
        return []
    return list(
        session.scalars(
            select(Inventory)
            .where(Inventory.inventory_id.in_(ordered_ids))
            .order_by(Inventory.inventory_id)
            .with_for_update()
        )
    )


def list_inventory(
    session: Session,
    *,
    lab_id: int | None = None,
    component_id: int | None = None,
    status: str | None = None,
) -> list[Inventory]:
    statement: Select[tuple[Inventory]] = select(Inventory)
    if lab_id is not None:
        statement = statement.where(Inventory.lab_id == lab_id)
    if component_id is not None:
        statement = statement.where(Inventory.component_id == component_id)
    if status:
        statement = statement.where(Inventory.inventory_status == status)
    return list(session.scalars(statement.order_by(Inventory.inventory_id)))


def find_position(
    session: Session,
    *,
    lab_id: int,
    component_id: int,
    storage_location_id: int,
    for_update: bool = False,
) -> Inventory | None:
    statement = select(Inventory).where(
        Inventory.lab_id == lab_id,
        Inventory.component_id == component_id,
        Inventory.storage_location_id == storage_location_id,
    )
    if for_update:
        statement = statement.with_for_update()
    return session.scalar(statement)


def create_inventory(session: Session, **values: object) -> Inventory:
    record = Inventory(**values)
    session.add(record)
    session.flush()
    return record

