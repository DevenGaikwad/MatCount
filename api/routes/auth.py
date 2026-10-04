"""External demo authentication exposed through opaque API sessions."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from api.dependencies import bearer_token, current_actor
from api.schemas import LoginInput
from api.serialization import serialize, success
from api.session_store import SESSION_STORE
from services.auth_service import authenticate
from services.rbac import Actor


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
def login(payload: LoginInput):
    actor = authenticate(payload.email, payload.password)
    token, expires_at = SESSION_STORE.create(actor)
    return success(
        {
            "access_token": token,
            "token_type": "bearer",
            "expires_at": expires_at,
            "actor": serialize(actor),
        },
        message="Welcome to SEMS.",
    )


@router.get("/me")
def me(actor: Actor = Depends(current_actor)):
    return success(actor)


@router.post("/logout")
def logout(token: str = Depends(bearer_token)):
    SESSION_STORE.revoke(token)
    return success(message="Signed out successfully.")

