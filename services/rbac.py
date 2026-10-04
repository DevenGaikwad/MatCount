"""Server-side actor, role and laboratory-scope enforcement."""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from typing import Iterable

from sqlalchemy.orm import Session

from config.constants import AccountStatus, Role
from repositories import user_repository
from services.exceptions import AuthorizationError


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Actor:
    user_id: int
    email: str
    full_name: str
    role: str
    lab_id: int
    account_status: str = AccountStatus.ACTIVE.value

    def to_session_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_session_dict(cls, value: dict[str, object]) -> "Actor":
        return cls(
            user_id=int(value["user_id"]),
            email=str(value["email"]),
            full_name=str(value["full_name"]),
            role=str(value["role"]),
            lab_id=int(value["lab_id"]),
            account_status=str(value.get("account_status", AccountStatus.ACTIVE.value)),
        )


def require_active(actor: Actor) -> None:
    if actor.account_status != AccountStatus.ACTIVE.value:
        LOGGER.warning("Inactive session actor denied: user_id=%s", actor.user_id)
        raise AuthorizationError("This account is not active for operational writes.")


def require_roles(actor: Actor, allowed: Iterable[str | Role]) -> None:
    require_active(actor)
    allowed_values = {str(role) for role in allowed}
    if actor.role not in allowed_values:
        LOGGER.warning(
            "Role authorization denied: user_id=%s role=%s", actor.user_id, actor.role
        )
        raise AuthorizationError("Your role is not permitted to perform this operation.")


def require_lab_scope(actor: Actor, lab_id: int) -> None:
    require_active(actor)
    if actor.role != Role.ADMINISTRATOR.value and actor.lab_id != lab_id:
        LOGGER.warning(
            "Laboratory scope denied: user_id=%s actor_lab=%s target_lab=%s",
            actor.user_id,
            actor.lab_id,
            lab_id,
        )
        raise AuthorizationError("This operation is outside your assigned laboratory.")


def require_any_lab_scope(actor: Actor, lab_ids: Iterable[int]) -> None:
    require_active(actor)
    if actor.role == Role.ADMINISTRATOR.value:
        return
    if actor.lab_id not in set(lab_ids):
        LOGGER.warning("Transfer scope denied: user_id=%s", actor.user_id)
        raise AuthorizationError("This transfer is outside your laboratory scope.")


def revalidate_actor(session: Session, actor: Actor) -> None:
    """Reject stale/tampered sessions after USER role, lab, email, or status changes."""

    record = user_repository.get_user(session, actor.user_id)
    if record is None or record.account_status != AccountStatus.ACTIVE.value:
        LOGGER.warning("Database actor revalidation denied: user_id=%s", actor.user_id)
        raise AuthorizationError("Your account is no longer active. Sign in again.")
    if (
        record.email.lower() != actor.email.lower()
        or record.role != actor.role
        or record.lab_id != actor.lab_id
    ):
        LOGGER.warning("Stale session identity denied: user_id=%s", actor.user_id)
        raise AuthorizationError(
            "Your role, laboratory, or email changed. Sign out and sign in again."
        )
