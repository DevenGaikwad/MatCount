"""Local opaque-session behavior without database interaction."""

from __future__ import annotations

import pytest

from api.session_store import SessionStore
from config.constants import Role
from services.exceptions import AuthenticationError
from services.rbac import Actor


pytestmark = pytest.mark.api


def actor() -> Actor:
    return Actor(
        user_id=4,
        email="student@example.invalid",
        full_name="Student User",
        role=Role.STUDENT.value,
        lab_id=2,
    )


def test_session_token_is_opaque_and_revocable() -> None:
    store = SessionStore(maximum_sessions=4)
    token, expires_at = store.create(actor())
    assert len(token) >= 32
    assert "student" not in token.lower()
    assert store.resolve(token).user_id == 4
    assert expires_at.tzinfo is not None
    store.revoke(token)
    with pytest.raises(AuthenticationError):
        store.resolve(token)


def test_session_store_enforces_configured_capacity() -> None:
    store = SessionStore(maximum_sessions=1)
    first, _ = store.create(actor())
    second, _ = store.create(actor())
    assert first != second
    with pytest.raises(AuthenticationError):
        store.resolve(first)
    assert store.resolve(second).user_id == 4
