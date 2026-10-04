"""Administrator-only disposal HTTP adapters."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from api.dependencies import current_actor
from api.schemas import DisposalInput
from api.serialization import success
from services import disposal_service
from services.rbac import Actor


router = APIRouter(prefix="/disposals", tags=["Disposal"])


@router.get("")
def list_disposals(
    inventory_id: int | None = Query(default=None, gt=0),
    actor: Actor = Depends(current_actor),
):
    return success(disposal_service.list_disposals(actor, inventory_id=inventory_id))


@router.post("")
def create_disposal(payload: DisposalInput, actor: Actor = Depends(current_actor)):
    record = disposal_service.dispose_inventory(actor, **payload.model_dump())
    return success(
        record,
        message="Disposal recorded and available stock decremented atomically.",
    )

