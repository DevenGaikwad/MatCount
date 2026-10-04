"""Inter-laboratory transfer lifecycle HTTP adapters."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from api.dependencies import current_actor
from api.schemas import (
    TransferCreateInput,
    TransferDispatchInput,
    TransferReceiptInput,
    TransferReturnInput,
)
from api.serialization import success
from services import analytics_service, transfer_service
from services.rbac import Actor


router = APIRouter(prefix="/transfers", tags=["Inter-Lab Transfers"])


@router.get("")
def list_transfers(
    status: str | None = Query(default=None, max_length=30),
    actor: Actor = Depends(current_actor),
):
    return success(transfer_service.list_transfers(actor, status=status))


@router.get("/{transfer_id}")
def transfer_detail(transfer_id: int, actor: Actor = Depends(current_actor)):
    header, items = transfer_service.get_transfer_with_items(actor, transfer_id)
    enriched = analytics_service.transfer_detail_view(actor, transfer_id)
    return success({"transfer": header, "items": enriched or items})


@router.post("")
def create_transfer(
    payload: TransferCreateInput, actor: Actor = Depends(current_actor)
):
    record = transfer_service.create_transfer(
        actor,
        request_id=payload.request_id,
        source_lab_id=payload.source_lab_id,
        destination_lab_id=payload.destination_lab_id,
        allocations=[item.model_dump() for item in payload.allocations],
    )
    return success(record, message="Draft transfer planned.")


@router.post("/{transfer_id}/approve")
def approve_transfer(transfer_id: int, actor: Actor = Depends(current_actor)):
    record = transfer_service.approve_transfer(actor, transfer_id)
    return success(record, message="Transfer approved and stock reserved.")


@router.post("/{transfer_id}/reject")
def reject_transfer(transfer_id: int, actor: Actor = Depends(current_actor)):
    record = transfer_service.reject_transfer(actor, transfer_id)
    return success(record, message="Transfer rejected.")


@router.post("/{transfer_id}/cancel")
def cancel_transfer(transfer_id: int, actor: Actor = Depends(current_actor)):
    record = transfer_service.cancel_transfer(actor, transfer_id)
    return success(record, message="Transfer cancelled; reservations were released.")


@router.post("/{transfer_id}/dispatch")
def dispatch_transfer(
    transfer_id: int,
    payload: TransferDispatchInput,
    actor: Actor = Depends(current_actor),
):
    conditions = {
        item.transfer_item_id: item.condition_on_issue for item in payload.items
    }
    record = transfer_service.dispatch_transfer(
        actor,
        transfer_id,
        dispatch_date=payload.dispatch_date,
        conditions_on_issue=conditions,
    )
    return success(record, message="Transfer dispatched; reserved stock reduced once.")


@router.post("/{transfer_id}/receive")
def receive_transfer(
    transfer_id: int,
    payload: TransferReceiptInput,
    actor: Actor = Depends(current_actor),
):
    receipts = {
        item.transfer_item_id: {
            "quantity_received": item.quantity_received,
            "destination_inventory_id": item.destination_inventory_id,
            "storage_location_id": item.storage_location_id,
        }
        for item in payload.items
    }
    record = transfer_service.receive_transfer(
        actor,
        transfer_id,
        receipt_date=payload.receipt_date,
        receipts=receipts,
    )
    return success(record, message="Receipt committed to the selected destination.")


@router.post("/{transfer_id}/return")
def return_transfer(
    transfer_id: int,
    payload: TransferReturnInput,
    actor: Actor = Depends(current_actor),
):
    returns = {
        item.transfer_item_id: {
            "destination_inventory_id": item.destination_inventory_id,
            "condition_on_return": item.condition_on_return,
        }
        for item in payload.items
    }
    record = transfer_service.return_temporary_items(
        actor, transfer_id, return_date=payload.return_date, returns=returns
    )
    return success(record, message="Selected temporary items returned.")
