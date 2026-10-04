"""FastAPI dependencies that preserve service-level identity enforcement."""

from __future__ import annotations

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.session_store import SESSION_STORE
from services.auth_service import validate_session_actor
from services.exceptions import AuthenticationError, AuthorizationError
from services.rbac import Actor


BEARER = HTTPBearer(auto_error=False)


def bearer_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(BEARER),
) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AuthenticationError("Sign in is required to access SEMS.")
    return credentials.credentials


def current_actor(token: str = Depends(bearer_token)) -> Actor:
    actor = SESSION_STORE.resolve(token)
    try:
        validate_session_actor(actor)
    except AuthorizationError:
        SESSION_STORE.revoke(token)
        raise
    return actor

