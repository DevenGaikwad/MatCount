"""Atomic multi-line component-request workflow."""

from __future__ import annotations

from datetime import date
from typing import Iterable, Mapping

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from config.constants import RequestItemStatus, RequestPriority, RequestStatus, Role
from db.session import session_scope
from repositories import component_repository, request_repository
from services.exceptions import (
    AuthorizationError,
    NotFoundError,
    StateTransitionError,
    ValidationError,
)
from services.rbac import Actor, revalidate_actor, require_lab_scope, require_roles
from services.rules import (
    approval_item_status,
    derive_request_status,
    validate_approval,
)
from services.validation import (
    actual_date,
    date_value,
    nonnegative_int,
    optional_text,
    positive_int,
    required_text,
)


def list_requests(
    actor: Actor, *, status: str | None = None, own_only: bool = False
):
    if status is not None and status not in {item.value for item in RequestStatus}:
        raise ValidationError("Invalid request status filter.")
    lab_id = None if actor.role == Role.ADMINISTRATOR.value else actor.lab_id
    created_by = actor.user_id if own_only or actor.role == Role.STUDENT.value else None
    with session_scope() as session:
        revalidate_actor(session, actor)
        return request_repository.list_requests(
            session, lab_id=lab_id, created_by=created_by, status=status
        )


def list_approved_for_transfer(actor: Actor):
    require_roles(actor, [Role.LAB_ASSISTANT, Role.ADMINISTRATOR])
    with session_scope() as session:
        revalidate_actor(session, actor)
        return request_repository.list_requests(
            session, status=RequestStatus.APPROVED.value
        ) + request_repository.list_requests(
            session, status=RequestStatus.PARTIALLY_APPROVED.value
        )


def get_approved_for_transfer_with_items(actor: Actor, request_id: int):
    """Expose approved lines to authorized stock providers planning a transfer."""

    require_roles(actor, [Role.LAB_ASSISTANT, Role.ADMINISTRATOR])
    request_id = positive_int(request_id, "Request ID")
    with session_scope() as session:
        revalidate_actor(session, actor)
        request = request_repository.get_request(session, request_id)
        if request is None:
            raise NotFoundError("Component request not found.")
        if request.request_status not in {
            RequestStatus.APPROVED.value,
            RequestStatus.PARTIALLY_APPROVED.value,
        }:
            raise StateTransitionError(
                "Only an approved request may be inspected for transfer planning."
            )
        return request, request_repository.list_items(session, request_id)


def get_request_with_items(actor: Actor, request_id: int):
    request_id = positive_int(request_id, "Request ID")
    with session_scope() as session:
        revalidate_actor(session, actor)
        request = request_repository.get_request(session, request_id)
        if request is None:
            raise NotFoundError("Component request not found.")
        require_lab_scope(actor, request.requesting_lab_id)
        if actor.role == Role.STUDENT.value and request.created_by != actor.user_id:
            raise AuthorizationError("Students may view only their own requests.")
        return request, request_repository.list_items(session, request_id)


def create_draft(
    actor: Actor,
    *,
    requesting_lab_id: int,
    request_date: date,
    required_by_date: date,
    priority: str,
    reason: str,
    items: Iterable[Mapping[str, int]],
):
    require_roles(actor, [Role.STUDENT, Role.FACULTY, Role.ADMINISTRATOR])
    requesting_lab_id = positive_int(requesting_lab_id, "Requesting laboratory ID")
    require_lab_scope(actor, requesting_lab_id)
    request_date = actual_date(request_date, "Request date")
    required_by_date = date_value(required_by_date, "Required-by date")
    if required_by_date < request_date:
        raise ValidationError("Required-by date cannot precede request date.")
    if priority not in {item.value for item in RequestPriority}:
        raise ValidationError("Invalid request priority.")
    reason = required_text(reason, "Request reason", max_length=1000)

    normalized_items: list[dict[str, int]] = []
    for position, item in enumerate(items, start=1):
        if "component_id" not in item or "quantity_requested" not in item:
            raise ValidationError(f"Request line {position} is incomplete.")
        normalized_items.append(
            {
                "component_id": positive_int(
                    item["component_id"], f"Component ID on line {position}"
                ),
                "quantity_requested": positive_int(
                    item["quantity_requested"], f"Requested quantity on line {position}"
                ),
            }
        )
    if not normalized_items:
        raise ValidationError("Add at least one component to the request.")
    component_ids = [item["component_id"] for item in normalized_items]
    if len(component_ids) != len(set(component_ids)):
        raise ValidationError("A component may appear only once in a request.")

    try:
        with session_scope() as session:
            revalidate_actor(session, actor)
            request = request_repository.create_request(
                session,
                requesting_lab_id=requesting_lab_id,
                created_by=actor.user_id,
                request_date=request_date,
                required_by_date=required_by_date,
                priority=priority,
                reason=reason,
                request_status=RequestStatus.DRAFT.value,
            )
            for item in normalized_items:
                component_id = item["component_id"]
                if component_repository.get_component(session, component_id) is None:
                    raise NotFoundError(f"Component {component_id} not found.")
                request_repository.create_item(
                    session,
                    request_id=request.request_id,
                    component_id=component_id,
                    quantity_requested=item["quantity_requested"],
                    quantity_approved=0,
                    item_status=RequestItemStatus.PENDING.value,
                    remarks=None,
                )
            return request
    except IntegrityError:
        raise ValidationError("The request contains duplicate or invalid data.") from None


def add_item(
    actor: Actor, request_id: int, *, component_id: int, quantity_requested: int
):
    require_roles(actor, [Role.STUDENT, Role.FACULTY, Role.ADMINISTRATOR])
    request_id = positive_int(request_id, "Request ID")
    component_id = positive_int(component_id, "Component ID")
    quantity_requested = positive_int(quantity_requested, "Requested quantity")
    try:
        with session_scope() as session:
            revalidate_actor(session, actor)
            request = request_repository.get_request(session, request_id, for_update=True)
            if request is None:
                raise NotFoundError("Component request not found.")
            if request.request_status != RequestStatus.DRAFT.value:
                raise StateTransitionError("Items may be added only to a DRAFT request.")
            if request.created_by != actor.user_id and actor.role != Role.ADMINISTRATOR.value:
                raise AuthorizationError("Only the creator may edit this draft request.")
            require_lab_scope(actor, request.requesting_lab_id)
            if component_repository.get_component(session, component_id) is None:
                raise NotFoundError("Component not found.")
            return request_repository.create_item(
                session,
                request_id=request_id,
                component_id=component_id,
                quantity_requested=quantity_requested,
                quantity_approved=0,
                item_status=RequestItemStatus.PENDING.value,
                remarks=None,
            )
    except IntegrityError:
        raise ValidationError("This component is already present in the request.") from None


def submit_request(actor: Actor, request_id: int):
    require_roles(actor, [Role.STUDENT, Role.FACULTY, Role.ADMINISTRATOR])
    request_id = positive_int(request_id, "Request ID")
    with session_scope() as session:
        revalidate_actor(session, actor)
        request = request_repository.get_request(session, request_id, for_update=True)
        if request is None:
            raise NotFoundError("Component request not found.")
        if request.request_status != RequestStatus.DRAFT.value:
            raise StateTransitionError("Only a DRAFT request may be submitted.")
        if request.created_by != actor.user_id and actor.role != Role.ADMINISTRATOR.value:
            raise AuthorizationError("Only the creator may submit this request.")
        require_lab_scope(actor, request.requesting_lab_id)
        items = request_repository.list_items(session, request_id, for_update=True)
        if not items:
            raise ValidationError("A request cannot be submitted without items.")
        request.request_status = RequestStatus.SUBMITTED.value
        session.flush()
        return request


def review_request(
    actor: Actor,
    request_id: int,
    reviews: Mapping[int, Mapping[str, object]],
):
    require_roles(actor, [Role.FACULTY, Role.ADMINISTRATOR])
    request_id = positive_int(request_id, "Request ID")
    with session_scope() as session:
        revalidate_actor(session, actor)
        request = request_repository.get_request(session, request_id, for_update=True)
        if request is None:
            raise NotFoundError("Component request not found.")
        require_lab_scope(actor, request.requesting_lab_id)
        if request.request_status not in {
            RequestStatus.SUBMITTED.value,
            RequestStatus.PARTIALLY_APPROVED.value,
        }:
            raise StateTransitionError("This request is not awaiting faculty review.")
        items = request_repository.list_items(session, request_id, for_update=True)
        allocated = request_repository.allocated_quantity_by_component(
            session, request_id
        )
        if any(allocated.values()) or any(
            item.item_status
            in {RequestItemStatus.ALLOCATED.value, RequestItemStatus.FULFILLED.value}
            for item in items
        ):
            raise StateTransitionError(
                "Approval quantities cannot be revised after transfer allocation begins."
            )
        if set(reviews) != {item.request_item_id for item in items}:
            raise ValidationError("Every request item must receive a review outcome.")
        for item in items:
            review = reviews[item.request_item_id]
            approved = nonnegative_int(
                review.get("quantity_approved", 0), "Approved quantity"
            )
            validate_approval(item.quantity_requested, approved)
            item.quantity_approved = approved
            item.item_status = approval_item_status(item.quantity_requested, approved)
            remarks = review.get("remarks")
            item.remarks = optional_text(
                remarks, "Request-item remarks", max_length=500
            )
        request.request_status = derive_request_status(
            [item.item_status for item in items]
        )
        session.flush()
        return request


def cancel_request(actor: Actor, request_id: int):
    require_roles(actor, [Role.STUDENT, Role.FACULTY, Role.ADMINISTRATOR])
    request_id = positive_int(request_id, "Request ID")
    with session_scope() as session:
        revalidate_actor(session, actor)
        request = request_repository.get_request(session, request_id, for_update=True)
        if request is None:
            raise NotFoundError("Component request not found.")
        if request.request_status not in {
            RequestStatus.DRAFT.value,
            RequestStatus.SUBMITTED.value,
        }:
            raise StateTransitionError(
                "Only a DRAFT or unallocated SUBMITTED request may be cancelled."
            )
        if request.created_by != actor.user_id and actor.role != Role.ADMINISTRATOR.value:
            raise AuthorizationError("Only the creator may cancel this request.")
        require_lab_scope(actor, request.requesting_lab_id)
        request.request_status = RequestStatus.CANCELLED.value
        session.flush()
        return request


def cancel_draft(actor: Actor, request_id: int):
    """Backward-compatible alias retained for existing callers."""

    return cancel_request(actor, request_id)


def recompute_request_progress(session: Session, request_id: int) -> None:
    request = request_repository.get_request(session, request_id, for_update=True)
    if request is None:
        raise NotFoundError("Component request not found.")
    items = request_repository.list_items(session, request_id, for_update=True)
    allocated = request_repository.allocated_quantity_by_component(session, request_id)
    received = request_repository.received_quantity_by_component(session, request_id)

    for item in items:
        if item.quantity_approved == 0:
            item.item_status = RequestItemStatus.REJECTED.value
        elif received.get(item.component_id, 0) >= item.quantity_approved:
            item.item_status = RequestItemStatus.FULFILLED.value
        elif allocated.get(item.component_id, 0) > 0:
            item.item_status = RequestItemStatus.ALLOCATED.value
        else:
            item.item_status = approval_item_status(
                item.quantity_requested, item.quantity_approved
            )

    request.request_status = derive_request_status([item.item_status for item in items])
