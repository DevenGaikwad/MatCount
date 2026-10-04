"""Component-request persistence operations."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from db.models import ComponentRequest, Inventory, RequestItem, Transfer, TransferItem


def get_request(
    session: Session, request_id: int, *, for_update: bool = False
) -> ComponentRequest | None:
    statement = select(ComponentRequest).where(ComponentRequest.request_id == request_id)
    if for_update:
        statement = statement.with_for_update()
    return session.scalar(statement)


def list_requests(
    session: Session,
    *,
    lab_id: int | None = None,
    created_by: int | None = None,
    status: str | None = None,
) -> list[ComponentRequest]:
    statement = select(ComponentRequest)
    if lab_id is not None:
        statement = statement.where(ComponentRequest.requesting_lab_id == lab_id)
    if created_by is not None:
        statement = statement.where(ComponentRequest.created_by == created_by)
    if status:
        statement = statement.where(ComponentRequest.request_status == status)
    return list(
        session.scalars(
            statement.order_by(
                ComponentRequest.request_date.desc(), ComponentRequest.request_id.desc()
            )
        )
    )


def create_request(session: Session, **values: object) -> ComponentRequest:
    record = ComponentRequest(**values)
    session.add(record)
    session.flush()
    return record


def list_items(
    session: Session, request_id: int, *, for_update: bool = False
) -> list[RequestItem]:
    statement = (
        select(RequestItem)
        .where(RequestItem.request_id == request_id)
        .order_by(RequestItem.request_item_id)
    )
    if for_update:
        statement = statement.with_for_update()
    return list(session.scalars(statement))


def get_item(
    session: Session, request_item_id: int, *, for_update: bool = False
) -> RequestItem | None:
    statement = select(RequestItem).where(
        RequestItem.request_item_id == request_item_id
    )
    if for_update:
        statement = statement.with_for_update()
    return session.scalar(statement)


def create_item(session: Session, **values: object) -> RequestItem:
    record = RequestItem(**values)
    session.add(record)
    session.flush()
    return record


def allocated_quantity_by_component(
    session: Session, request_id: int
) -> dict[int, int]:
    rows = session.execute(
        select(
            Inventory.component_id,
            func.coalesce(func.sum(TransferItem.quantity_sent), 0),
        )
        .join(Transfer, Transfer.transfer_id == TransferItem.transfer_id)
        .join(Inventory, Inventory.inventory_id == TransferItem.inventory_id)
        .where(
            Transfer.request_id == request_id,
            Transfer.transfer_status != "CANCELLED",
        )
        .group_by(Inventory.component_id)
    )
    return {int(component_id): int(quantity) for component_id, quantity in rows}


def received_quantity_by_component(
    session: Session, request_id: int
) -> dict[int, int]:
    rows = session.execute(
        select(
            Inventory.component_id,
            func.coalesce(func.sum(TransferItem.quantity_received), 0),
        )
        .join(Transfer, Transfer.transfer_id == TransferItem.transfer_id)
        .join(Inventory, Inventory.inventory_id == TransferItem.inventory_id)
        .where(
            Transfer.request_id == request_id,
            Transfer.transfer_status != "CANCELLED",
        )
        .group_by(Inventory.component_id)
    )
    return {int(component_id): int(quantity) for component_id, quantity in rows}
