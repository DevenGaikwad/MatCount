"""User and normalized phone persistence operations."""

from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from db.models import User, UserPhone


def get_user(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)


def get_user_by_email(session: Session, email: str) -> User | None:
    return session.scalar(select(User).where(User.email == email.strip().lower()))


def list_users(
    session: Session,
    *,
    lab_id: int | None = None,
    role: str | None = None,
    search: str | None = None,
) -> list[User]:
    statement = select(User)
    if lab_id is not None:
        statement = statement.where(User.lab_id == lab_id)
    if role:
        statement = statement.where(User.role == role)
    if search:
        pattern = f"%{search.strip()}%"
        statement = statement.where(
            or_(User.full_name.ilike(pattern), User.email.ilike(pattern))
        )
    return list(session.scalars(statement.order_by(User.full_name)))


def create_user(session: Session, **values: object) -> User:
    record = User(**values)
    session.add(record)
    session.flush()
    return record


def add_phone(session: Session, user_id: int, phone_number: str) -> UserPhone:
    record = UserPhone(user_id=user_id, phone_number=phone_number)
    session.add(record)
    session.flush()
    return record


def list_phones(session: Session, user_id: int) -> list[UserPhone]:
    return list(
        session.scalars(
            select(UserPhone)
            .where(UserPhone.user_id == user_id)
            .order_by(UserPhone.phone_number)
        )
    )

