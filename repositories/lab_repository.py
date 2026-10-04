"""Laboratory and storage-location persistence operations."""

from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from db.models import Lab, LabContact, StorageLocation


def list_labs(session: Session, search: str | None = None) -> list[Lab]:
    statement = select(Lab)
    if search:
        pattern = f"%{search.strip()}%"
        statement = statement.where(
            or_(
                Lab.lab_name.ilike(pattern),
                Lab.department_name.ilike(pattern),
                Lab.building_name.ilike(pattern),
            )
        )
    return list(session.scalars(statement.order_by(Lab.lab_name)))


def get_lab(session: Session, lab_id: int) -> Lab | None:
    return session.get(Lab, lab_id)


def create_lab(session: Session, **values: object) -> Lab:
    record = Lab(**values)
    session.add(record)
    session.flush()
    return record


def add_contact(session: Session, lab_id: int, contact_number: str) -> LabContact:
    record = LabContact(lab_id=lab_id, contact_number=contact_number)
    session.add(record)
    session.flush()
    return record


def list_contacts(session: Session, lab_id: int) -> list[LabContact]:
    return list(
        session.scalars(
            select(LabContact)
            .where(LabContact.lab_id == lab_id)
            .order_by(LabContact.contact_number)
        )
    )


def list_locations(
    session: Session, lab_id: int | None = None
) -> list[StorageLocation]:
    statement = select(StorageLocation)
    if lab_id is not None:
        statement = statement.where(StorageLocation.lab_id == lab_id)
    return list(
        session.scalars(
            statement.order_by(
                StorageLocation.lab_id,
                StorageLocation.cabinet_no,
                StorageLocation.shelf_no,
                StorageLocation.drawer_no,
            )
        )
    )


def get_location(
    session: Session, storage_location_id: int, *, for_update: bool = False
) -> StorageLocation | None:
    statement = select(StorageLocation).where(
        StorageLocation.storage_location_id == storage_location_id
    )
    if for_update:
        statement = statement.with_for_update()
    return session.scalar(statement)


def find_null_normalized_location(
    session: Session,
    *,
    lab_id: int,
    cabinet_no: str,
    shelf_no: str | None,
    drawer_no: str | None,
    location_type: str,
    exclude_id: int | None = None,
) -> StorageLocation | None:
    statement = select(StorageLocation).where(
        StorageLocation.lab_id == lab_id,
        func.lower(StorageLocation.cabinet_no) == cabinet_no.strip().lower(),
        func.coalesce(func.lower(StorageLocation.shelf_no), "")
        == (shelf_no or "").strip().lower(),
        func.coalesce(func.lower(StorageLocation.drawer_no), "")
        == (drawer_no or "").strip().lower(),
        func.lower(StorageLocation.location_type) == location_type.strip().lower(),
    )
    if exclude_id is not None:
        statement = statement.where(
            StorageLocation.storage_location_id != exclude_id
        )
    return session.scalar(statement.limit(1))


def create_location(session: Session, **values: object) -> StorageLocation:
    record = StorageLocation(**values)
    session.add(record)
    session.flush()
    return record

