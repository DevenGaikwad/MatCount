"""Component-category and catalogue persistence operations."""

from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from db.models import Component, ComponentCategory


def list_categories(session: Session) -> list[ComponentCategory]:
    return list(
        session.scalars(select(ComponentCategory).order_by(ComponentCategory.category_name))
    )


def get_category(session: Session, category_id: int) -> ComponentCategory | None:
    return session.get(ComponentCategory, category_id)


def create_category(session: Session, **values: object) -> ComponentCategory:
    record = ComponentCategory(**values)
    session.add(record)
    session.flush()
    return record


def get_component(session: Session, component_id: int) -> Component | None:
    return session.get(Component, component_id)


def list_components(
    session: Session,
    *,
    category_id: int | None = None,
    search: str | None = None,
) -> list[Component]:
    statement = select(Component)
    if category_id is not None:
        statement = statement.where(Component.category_id == category_id)
    if search:
        pattern = f"%{search.strip()}%"
        statement = statement.where(
            or_(
                Component.component_name.ilike(pattern),
                Component.part_number.ilike(pattern),
                Component.specification.ilike(pattern),
            )
        )
    return list(session.scalars(statement.order_by(Component.component_name)))


def create_component(session: Session, **values: object) -> Component:
    record = Component(**values)
    session.add(record)
    session.flush()
    return record
