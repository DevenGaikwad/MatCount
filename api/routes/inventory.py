"""Inventory read and controlled-write HTTP adapters."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from api.dependencies import current_actor
from api.schemas import (
    InventoryInput,
    InventoryMetadataInput,
    InventoryStatusInput,
    RestockInput,
)
from api.serialization import success
from services import analytics_service, inventory_service
from services.rbac import Actor


router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("")
def inventory_detail(
    limit: int = Query(default=1000, ge=1, le=2000),
    actor: Actor = Depends(current_actor),
):
    return success(analytics_service.availability_view(actor, limit=limit))


@router.get("/positions")
def positions(
    lab_id: int | None = Query(default=None, gt=0),
    component_id: int | None = Query(default=None, gt=0),
    status: str | None = Query(default=None, max_length=30),
    actor: Actor = Depends(current_actor),
):
    return success(
        inventory_service.list_inventory(
            actor, lab_id=lab_id, component_id=component_id, status=status
        )
    )


@router.post("")
def create_inventory(payload: InventoryInput, actor: Actor = Depends(current_actor)):
    record = inventory_service.create_inventory(actor, **payload.model_dump())
    return success(record, message="Inventory position registered.")


@router.post("/{inventory_id}/restock")
def restock(
    inventory_id: int,
    payload: RestockInput,
    actor: Actor = Depends(current_actor),
):
    record = inventory_service.restock_inventory(
        actor, inventory_id, payload.quantity
    )
    return success(record, message="Available stock increased.")


@router.patch("/{inventory_id}/metadata")
def update_metadata(
    inventory_id: int,
    payload: InventoryMetadataInput,
    actor: Actor = Depends(current_actor),
):
    record = inventory_service.update_inventory_metadata(
        actor, inventory_id, **payload.model_dump()
    )
    return success(record, message="Inventory metadata updated.")


@router.patch("/{inventory_id}/status")
def update_status(
    inventory_id: int,
    payload: InventoryStatusInput,
    actor: Actor = Depends(current_actor),
):
    record = inventory_service.set_operational_status(
        actor, inventory_id, payload.status
    )
    return success(record, message="Inventory status updated.")

