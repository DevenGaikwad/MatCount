"""Disposal-history persistence operations."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import DisposalRecord


def list_disposals(
    session: Session, *, inventory_id: int | None = None
) -> list[DisposalRecord]:
    statement = select(DisposalRecord)
    if inventory_id is not None:
        statement = statement.where(DisposalRecord.inventory_id == inventory_id)
    return list(
        session.scalars(
            statement.order_by(
                DisposalRecord.disposal_date.desc(), DisposalRecord.disposal_id.desc()
            )
        )
    )


def create_disposal(session: Session, **values: object) -> DisposalRecord:
    record = DisposalRecord(**values)
    session.add(record)
    session.flush()
    return record

