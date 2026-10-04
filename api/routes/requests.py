"""Component-request lifecycle HTTP adapters."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from api.dependencies import current_actor
from api.schemas import RequestCreateInput, RequestReviewInput
from api.serialization import success
from services import request_service
from services.rbac import Actor


router = APIRouter(prefix="/requests", tags=["Component Requests"])


@router.get("")
def list_requests(
    status: str | None = Query(default=None, max_length=30),
    own_only: bool = Query(default=False),
    actor: Actor = Depends(current_actor),
):
    return success(
        request_service.list_requests(actor, status=status, own_only=own_only)
    )


@router.get("/transfer-ready")
def transfer_ready(actor: Actor = Depends(current_actor)):
    return success(request_service.list_approved_for_transfer(actor))


@router.get("/{request_id}/transfer-plan")
def transfer_plan_detail(request_id: int, actor: Actor = Depends(current_actor)):
    header, items = request_service.get_approved_for_transfer_with_items(
        actor, request_id
    )
    return success({"request": header, "items": items})


@router.get("/{request_id}")
def request_detail(request_id: int, actor: Actor = Depends(current_actor)):
    header, items = request_service.get_request_with_items(actor, request_id)
    return success({"request": header, "items": items})


@router.post("")
def create_request(
    payload: RequestCreateInput, actor: Actor = Depends(current_actor)
):
    values = payload.model_dump()
    values["items"] = [item.model_dump() for item in payload.items]
    record = request_service.create_draft(actor, **values)
    return success(record, message="Draft component request created.")


@router.post("/{request_id}/submit")
def submit_request(request_id: int, actor: Actor = Depends(current_actor)):
    record = request_service.submit_request(actor, request_id)
    return success(record, message="Request submitted for review.")


@router.post("/{request_id}/cancel")
def cancel_request(request_id: int, actor: Actor = Depends(current_actor)):
    record = request_service.cancel_request(actor, request_id)
    return success(record, message="Request cancelled before approval/allocation.")


@router.post("/{request_id}/review")
def review_request(
    request_id: int,
    payload: RequestReviewInput,
    actor: Actor = Depends(current_actor),
):
    reviews = {
        item.request_item_id: {
            "quantity_approved": item.quantity_approved,
            "remarks": item.remarks,
        }
        for item in payload.reviews
    }
    record = request_service.review_request(actor, request_id, reviews)
    return success(record, message="Request review committed atomically.")
