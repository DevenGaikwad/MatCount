"""Transfer header/line persistence operations."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import Transfer, TransferItem


def get_transfer(
    session: Session, transfer_id: int, *, for_update: bool = False
) -> Transfer | None:
    statement = select(Transfer).where(Transfer.transfer_id == transfer_id)
    if for_update:
        statement = statement.with_for_update()
    return session.scalar(statement)


def list_transfers(
    session: Session,
    *,
    lab_id: int | None = None,
    status: str | None = None,
) -> list[Transfer]:
    statement = select(Transfer)
    if lab_id is not None:
        statement = statement.where(
            (Transfer.source_lab_id == lab_id) | (Transfer.destination_lab_id == lab_id)
        )
    if status:
        statement = statement.where(Transfer.transfer_status == status)
    return list(
        session.scalars(statement.order_by(Transfer.transfer_id.desc()))
    )


def create_transfer(session: Session, **values: object) -> Transfer:
    record = Transfer(**values)
    session.add(record)
    session.flush()
    return record


def list_items(
    session: Session, transfer_id: int, *, for_update: bool = False
) -> list[TransferItem]:
    statement = (
        select(TransferItem)
        .where(TransferItem.transfer_id == transfer_id)
        .order_by(TransferItem.inventory_id, TransferItem.transfer_item_id)
    )
    if for_update:
        statement = statement.with_for_update()
    return list(session.scalars(statement))


def get_item(
    session: Session, transfer_item_id: int, *, for_update: bool = False
) -> TransferItem | None:
    statement = select(TransferItem).where(
        TransferItem.transfer_item_id == transfer_item_id
    )
    if for_update:
        statement = statement.with_for_update()
    return session.scalar(statement)


def create_item(session: Session, **values: object) -> TransferItem:
    record = TransferItem(**values)
    session.add(record)
    session.flush()
    return record

