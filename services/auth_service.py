"""External bcrypt demo authentication mapped to frozen USER.email."""

from __future__ import annotations

import logging

import bcrypt

from config.constants import AccountStatus
from config.settings import get_settings
from db.session import session_scope
from repositories import user_repository
from services.exceptions import AuthenticationError
from services.rbac import Actor, revalidate_actor


LOGGER = logging.getLogger(__name__)


def authenticate(email: str, password: str) -> Actor:
    normalized_email = email.strip().lower()
    credentials = get_settings().demo_credentials or {}
    stored_hash = credentials.get(normalized_email)

    if not normalized_email or not password or not stored_hash:
        raise AuthenticationError("Invalid demonstration credentials.")

    try:
        verified = bcrypt.checkpw(
            password.encode("utf-8"), stored_hash.encode("utf-8")
        )
    except ValueError:
        LOGGER.error("Invalid bcrypt hash configured for a demo account")
        raise AuthenticationError(
            "Demonstration credentials are not configured correctly."
        ) from None

    if not verified:
        raise AuthenticationError("Invalid demonstration credentials.")

    with session_scope() as session:
        user = user_repository.get_user_by_email(session, normalized_email)
        if user is None:
            raise AuthenticationError("Authenticated email is not registered in SEMS.")
        if user.account_status != AccountStatus.ACTIVE.value:
            raise AuthenticationError("This SEMS account is not active.")
        return Actor(
            user_id=user.user_id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            lab_id=user.lab_id,
            account_status=user.account_status,
        )


def validate_session_actor(actor: Actor) -> None:
    """Recheck the database identity represented by an existing UI session."""

    with session_scope() as session:
        revalidate_actor(session, actor)
