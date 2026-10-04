"""Role-scoped operational dashboard endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from api.dependencies import current_actor
from api.serialization import success
from services import analytics_service
from services.rbac import Actor


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("")
def dashboard(actor: Actor = Depends(current_actor)):
    return success(analytics_service.dashboard(actor))

