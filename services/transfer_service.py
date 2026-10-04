"""Atomic inter-laboratory reservation, transfer, receipt and return workflow."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Mapping

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from config.constants import (
    ApprovalStatus,
    InventoryStatus,
    RequestStatus,
    Role,
    TransferStatus,
)
from db.models import Inventory, RequestItem, Transfer, TransferItem
from db.session import session_scope
from repositories import (
    component_repository,
    inventory_repository,
    lab_repository,
    request_repository,
    transfer_repository,
)
from services.exceptions import (
    NotFoundError,
    StateTransitionError,
    ValidationError,
)
from services.rbac import (
    Actor,
    revalidate_actor,
    require_any_lab_scope,
    require_lab_scope,
    require_roles,
)
from services.request_service import recompute_request_progress
from services.rules import (
    StockSnapshot,
    add_received,
    dispatch_reserved,
    inventory_status,
    release_reservation,
    remove_free_stock,
    reserve_stock,
    validate_distinct_labs,
)
from services.validation import (
    actual_date,
    date_value,
    nonnegative_int,
    positive_int,
    required_text,
)


def list_transfers(actor: Actor, *, status: str | None = None):
    require_roles(actor, [Role.FACULTY, Role.LAB_ASSISTANT, Role.ADMINISTRATOR])
    if status is not None and status not in {item.value for item in TransferStatus}:
        raise ValidationError("Invalid transfer status filter.")
    lab_id = None if actor.role == Role.ADMINISTRATOR.value else actor.lab_id
    with session_scope() as session:
        revalidate_actor(session, actor)
        return transfer_repository.list_transfers(session, lab_id=lab_id, status=status)


def get_transfer_with_items(actor: Actor, transfer_id: int):
    require_roles(actor, [Role.FACULTY, Role.LAB_ASSISTANT, Role.ADMINISTRATOR])
    transfer_id = positive_int(transfer_id, "Transfer ID")
    with session_scope() as session:
        revalidate_actor(session, actor)
        transfer = transfer_repository.get_transfer(session, transfer_id)
        if transfer is None:
            raise NotFoundError("Transfer not found.")
        require_any_lab_scope(
            actor, [transfer.source_lab_id, transfer.destination_lab_id]
        )
        return transfer, transfer_repository.list_items(session, transfer_id)


def _request_approval_by_component(request_items: list[RequestItem]) -> dict[int, int]:
    return {
        item.component_id: item.quantity_approved
        for item in request_items
        if item.quantity_approved > 0
    }


def _validate_transfer_allocations(
    session: Session,
    transfer: Transfer,
    items: list[TransferItem],
) -> None:
    request = request_repository.get_request(
        session, transfer.request_id, for_update=True
    )
    if request is None:
        raise NotFoundError("Associated component request not found.")
    if request.request_status not in {
        RequestStatus.APPROVED.value,
        RequestStatus.PARTIALLY_APPROVED.value,
    }:
        raise StateTransitionError("The request is not approved for transfer allocation.")
    if transfer.destination_lab_id != request.requesting_lab_id:
        raise ValidationError(
            "Transfer destination must match the request's requesting laboratory."
        )

    request_items = request_repository.list_items(
        session, transfer.request_id, for_update=True
    )
    approved = _request_approval_by_component(request_items)
    existing = request_repository.allocated_quantity_by_component(
        session, transfer.request_id
    )
    current_transfer_totals: dict[int, int] = {}
    for item in items:
        inventory = inventory_repository.get_inventory(session, item.inventory_id)
        if inventory is None:
            raise NotFoundError("Allocated source inventory not found.")
        if inventory.lab_id != transfer.source_lab_id:
            raise ValidationError("Every allocation must belong to the source laboratory.")
        if inventory.inventory_status in {
            InventoryStatus.BLOCKED.value,
            InventoryStatus.INACTIVE.value,
        }:
            raise ValidationError("Blocked or inactive stock cannot be allocated.")
        if inventory.quantity_available < item.quantity_sent:
            raise ValidationError(
                "A DRAFT allocation exceeds the currently available source stock."
            )
        current_transfer_totals[inventory.component_id] = (
            current_transfer_totals.get(inventory.component_id, 0) + item.quantity_sent
        )

    for component_id, quantity in current_transfer_totals.items():
        previously_allocated = existing.get(component_id, 0)
        # The current DRAFT transfer is included in the aggregate. Remove it once.
        other_allocated = max(0, previously_allocated - quantity)
        if component_id not in approved or other_allocated + quantity > approved[component_id]:
            raise ValidationError(
                "Transfer allocation exceeds the approved request quantity."
            )


def create_transfer(
    actor: Actor,
    *,
    request_id: int,
    source_lab_id: int,
    destination_lab_id: int,
    allocations: list[Mapping[str, object]],
):
    require_roles(actor, [Role.LAB_ASSISTANT, Role.ADMINISTRATOR])
    request_id = positive_int(request_id, "Request ID")
    source_lab_id = positive_int(source_lab_id, "Source laboratory ID")
    destination_lab_id = positive_int(
        destination_lab_id, "Destination laboratory ID"
    )
    require_lab_scope(actor, source_lab_id)
    validate_distinct_labs(source_lab_id, destination_lab_id)
    if not allocations:
        raise ValidationError("A transfer must contain at least one allocation.")
    normalized_allocations: list[dict[str, object]] = []
    for position, row in enumerate(allocations, start=1):
        if "inventory_id" not in row or "quantity_sent" not in row:
            raise ValidationError(f"Transfer allocation {position} is incomplete.")
        due_date = row.get("return_due_date")
        if due_date is not None:
            due_date = date_value(due_date, f"Return due date on allocation {position}")
            if due_date < date.today():
                raise ValidationError("Return due dates cannot be in the past.")
        normalized_allocations.append(
            {
                "inventory_id": positive_int(
                    row["inventory_id"], f"Inventory ID on allocation {position}"
                ),
                "quantity_sent": positive_int(
                    row["quantity_sent"], f"Quantity on allocation {position}"
                ),
                "return_due_date": due_date,
            }
        )
    inventory_ids = [int(row["inventory_id"]) for row in normalized_allocations]
    if len(inventory_ids) != len(set(inventory_ids)):
        raise ValidationError("Source inventory may appear only once in a transfer.")

    try:
        with session_scope() as session:
            revalidate_actor(session, actor)
            request = request_repository.get_request(
                session, request_id, for_update=True
            )
            if request is None:
                raise NotFoundError("Component request not found.")
            if destination_lab_id != request.requesting_lab_id:
                raise ValidationError(
                    "Destination laboratory must match the requesting laboratory."
                )
            if lab_repository.get_lab(session, source_lab_id) is None:
                raise NotFoundError("Source laboratory not found.")
            transfer = transfer_repository.create_transfer(
                session,
                request_id=request_id,
                source_lab_id=source_lab_id,
                destination_lab_id=destination_lab_id,
                created_by=actor.user_id,
                received_by=None,
                dispatch_date=None,
                received_date=None,
                transfer_status=TransferStatus.DRAFT.value,
                approval_status=ApprovalStatus.PENDING.value,
            )
            items: list[TransferItem] = []
            for allocation in normalized_allocations:
                item = transfer_repository.create_item(
                    session,
                    transfer_id=transfer.transfer_id,
                    inventory_id=int(allocation["inventory_id"]),
                    quantity_sent=int(allocation["quantity_sent"]),
                    quantity_received=0,
                    return_due_date=allocation.get("return_due_date"),
                    return_date=None,
                    condition_on_issue=None,
                    condition_on_return=None,
                )
                items.append(item)
            _validate_transfer_allocations(session, transfer, items)
            return transfer
    except IntegrityError:
        raise ValidationError("The transfer contains duplicate or invalid data.") from None


def approve_transfer(actor: Actor, transfer_id: int):
    require_roles(actor, [Role.ADMINISTRATOR])
    transfer_id = positive_int(transfer_id, "Transfer ID")
    with session_scope() as session:
        revalidate_actor(session, actor)
        transfer = transfer_repository.get_transfer(session, transfer_id, for_update=True)
        if transfer is None:
            raise NotFoundError("Transfer not found.")
        require_lab_scope(actor, transfer.source_lab_id)
        if (
            transfer.approval_status != ApprovalStatus.PENDING.value
            or transfer.transfer_status != TransferStatus.DRAFT.value
        ):
            raise StateTransitionError("Only a pending DRAFT transfer may be approved.")
        items = transfer_repository.list_items(session, transfer_id, for_update=True)
        if not items:
            raise ValidationError("A transfer cannot be approved without items.")
        _validate_transfer_allocations(session, transfer, items)

        rows = inventory_repository.get_inventory_rows_for_update(
            session, [item.inventory_id for item in items]
        )
        by_id = {row.inventory_id: row for row in rows}
        if len(by_id) != len({item.inventory_id for item in items}):
            raise NotFoundError("One or more source inventory records are missing.")

        for item in items:
            inventory = by_id[item.inventory_id]
            if inventory.lab_id != transfer.source_lab_id:
                raise ValidationError("Allocated inventory does not belong to source lab.")
            if inventory.inventory_status in {
                InventoryStatus.BLOCKED.value,
                InventoryStatus.INACTIVE.value,
            }:
                raise ValidationError("Blocked or inactive stock cannot be reserved.")
            next_stock = reserve_stock(
                StockSnapshot(
                    inventory.quantity_available, inventory.quantity_reserved
                ),
                item.quantity_sent,
            )
            inventory.quantity_available = next_stock.available
            inventory.quantity_reserved = next_stock.reserved
            component = component_repository.get_component(
                session, inventory.component_id
            )
            if component is None:
                raise NotFoundError("Allocated component not found.")
            inventory.inventory_status = inventory_status(
                inventory.quantity_available,
                component.minimum_stock_level,
                inventory.inventory_status,
            )

        transfer.approval_status = ApprovalStatus.APPROVED.value
        transfer.transfer_status = TransferStatus.APPROVED.value
        recompute_request_progress(session, transfer.request_id)
        session.flush()
        return transfer


def reject_transfer(actor: Actor, transfer_id: int):
    require_roles(actor, [Role.ADMINISTRATOR])
    transfer_id = positive_int(transfer_id, "Transfer ID")
    with session_scope() as session:
        revalidate_actor(session, actor)
        transfer = transfer_repository.get_transfer(session, transfer_id, for_update=True)
        if transfer is None:
            raise NotFoundError("Transfer not found.")
        require_lab_scope(actor, transfer.source_lab_id)
        if (
            transfer.approval_status != ApprovalStatus.PENDING.value
            or transfer.transfer_status != TransferStatus.DRAFT.value
        ):
            raise StateTransitionError("Only a pending DRAFT transfer may be rejected.")
        transfer.approval_status = ApprovalStatus.REJECTED.value
        transfer.transfer_status = TransferStatus.CANCELLED.value
        recompute_request_progress(session, transfer.request_id)
        session.flush()
        return transfer


def cancel_transfer(actor: Actor, transfer_id: int):
    require_roles(actor, [Role.LAB_ASSISTANT, Role.ADMINISTRATOR])
    transfer_id = positive_int(transfer_id, "Transfer ID")
    with session_scope() as session:
        revalidate_actor(session, actor)
        transfer = transfer_repository.get_transfer(session, transfer_id, for_update=True)
        if transfer is None:
            raise NotFoundError("Transfer not found.")
        require_lab_scope(actor, transfer.source_lab_id)
        if transfer.transfer_status not in {
            TransferStatus.DRAFT.value,
            TransferStatus.APPROVED.value,
        }:
            raise StateTransitionError("A transfer cannot be cancelled after dispatch.")
        items = transfer_repository.list_items(session, transfer_id, for_update=True)
        if transfer.transfer_status == TransferStatus.APPROVED.value:
            rows = inventory_repository.get_inventory_rows_for_update(
                session, [item.inventory_id for item in items]
            )
            by_id = {row.inventory_id: row for row in rows}
            for item in items:
                inventory = by_id[item.inventory_id]
                next_stock = release_reservation(
                    StockSnapshot(
                        inventory.quantity_available, inventory.quantity_reserved
                    ),
                    item.quantity_sent,
                )
                inventory.quantity_available = next_stock.available
                inventory.quantity_reserved = next_stock.reserved
                component = component_repository.get_component(
                    session, inventory.component_id
                )
                if component is None:
                    raise NotFoundError("Allocated component not found.")
                inventory.inventory_status = inventory_status(
                    inventory.quantity_available,
                    component.minimum_stock_level,
                    inventory.inventory_status,
                )
        transfer.transfer_status = TransferStatus.CANCELLED.value
        recompute_request_progress(session, transfer.request_id)
        session.flush()
        return transfer


def dispatch_transfer(
    actor: Actor,
    transfer_id: int,
    *,
    dispatch_date: date,
    conditions_on_issue: Mapping[int, str],
):
    require_roles(actor, [Role.LAB_ASSISTANT, Role.ADMINISTRATOR])
    transfer_id = positive_int(transfer_id, "Transfer ID")
    dispatch_date = actual_date(dispatch_date, "Dispatch date")
    with session_scope() as session:
        revalidate_actor(session, actor)
        transfer = transfer_repository.get_transfer(session, transfer_id, for_update=True)
        if transfer is None:
            raise NotFoundError("Transfer not found.")
        require_lab_scope(actor, transfer.source_lab_id)
        if (
            transfer.approval_status != ApprovalStatus.APPROVED.value
            or transfer.transfer_status != TransferStatus.APPROVED.value
        ):
            raise StateTransitionError("Only an approved transfer may be dispatched.")
        request = request_repository.get_request(session, transfer.request_id)
        if request is None:
            raise NotFoundError("Associated component request not found.")
        if dispatch_date < request.request_date:
            raise ValidationError("Dispatch date cannot precede the request date.")
        items = transfer_repository.list_items(session, transfer_id, for_update=True)
        if set(conditions_on_issue) != {item.transfer_item_id for item in items}:
            raise ValidationError("Record condition on issue for every transfer item.")
        rows = inventory_repository.get_inventory_rows_for_update(
            session, [item.inventory_id for item in items]
        )
        by_id = {row.inventory_id: row for row in rows}
        for item in items:
            inventory = by_id[item.inventory_id]
            next_stock = dispatch_reserved(
                StockSnapshot(
                    inventory.quantity_available, inventory.quantity_reserved
                ),
                item.quantity_sent,
            )
            inventory.quantity_available = next_stock.available
            inventory.quantity_reserved = next_stock.reserved
            condition = required_text(
                conditions_on_issue[item.transfer_item_id],
                "Condition on issue",
                max_length=100,
            )
            item.condition_on_issue = condition
        transfer.dispatch_date = dispatch_date
        transfer.transfer_status = TransferStatus.DISPATCHED.value
        session.flush()
        return transfer


def _resolve_destination_candidates(
    session: Session,
    transfer: Transfer,
    items: list[TransferItem],
    receipts: Mapping[int, Mapping[str, object]],
) -> tuple[dict[int, int | None], dict[int, int]]:
    destination_ids: dict[int, int | None] = {}
    location_ids: dict[int, int] = {}
    source_by_item = {
        item.transfer_item_id: inventory_repository.get_inventory(
            session, item.inventory_id
        )
        for item in items
    }
    for item in items:
        receipt = receipts[item.transfer_item_id]
        source = source_by_item[item.transfer_item_id]
        if source is None:
            raise NotFoundError("Source inventory not found.")
        destination_id = receipt.get("destination_inventory_id")
        storage_location_id = receipt.get("storage_location_id")
        if bool(destination_id) == bool(storage_location_id):
            raise ValidationError(
                "Select either a destination inventory row or a destination storage location."
            )
        if destination_id:
            destination_ids[item.transfer_item_id] = positive_int(
                destination_id, "Destination inventory ID"
            )
            continue
        location_id = positive_int(
            storage_location_id, "Destination storage-location ID"
        )
        location = lab_repository.get_location(session, location_id)
        if location is None or location.lab_id != transfer.destination_lab_id:
            raise ValidationError("Destination location must belong to destination lab.")
        existing = inventory_repository.find_position(
            session,
            lab_id=transfer.destination_lab_id,
            component_id=source.component_id,
            storage_location_id=location_id,
        )
        destination_ids[item.transfer_item_id] = (
            existing.inventory_id if existing else None
        )
        location_ids[item.transfer_item_id] = location_id
    return destination_ids, location_ids


def receive_transfer(
    actor: Actor,
    transfer_id: int,
    *,
    receipt_date: date,
    receipts: Mapping[int, Mapping[str, object]],
):
    require_roles(actor, [Role.LAB_ASSISTANT, Role.ADMINISTRATOR])
    transfer_id = positive_int(transfer_id, "Transfer ID")
    receipt_date = actual_date(receipt_date, "Receipt date")
    try:
        with session_scope() as session:
            revalidate_actor(session, actor)
            transfer = transfer_repository.get_transfer(
                session, transfer_id, for_update=True
            )
            if transfer is None:
                raise NotFoundError("Transfer not found.")
            require_lab_scope(actor, transfer.destination_lab_id)
            if transfer.transfer_status != TransferStatus.DISPATCHED.value:
                raise StateTransitionError("Only a dispatched transfer may be received.")
            if transfer.dispatch_date and receipt_date < transfer.dispatch_date:
                raise ValidationError("Receipt date cannot precede dispatch date.")
            items = transfer_repository.list_items(session, transfer_id, for_update=True)
            if set(receipts) != {item.transfer_item_id for item in items}:
                raise ValidationError("Provide a receipt decision for every transfer item.")

            destination_ids, location_ids = _resolve_destination_candidates(
                session, transfer, items, receipts
            )
            all_lock_ids = [item.inventory_id for item in items]
            all_lock_ids.extend(
                destination_id
                for destination_id in destination_ids.values()
                if destination_id is not None
            )
            locked = inventory_repository.get_inventory_rows_for_update(
                session, all_lock_ids
            )
            by_id = {row.inventory_id: row for row in locked}
            created_positions: dict[tuple[int, int, int], Inventory] = {}
            total_received_delta = 0

            for item in items:
                receipt = receipts[item.transfer_item_id]
                if "quantity_received" not in receipt:
                    raise ValidationError("Every receipt requires a cumulative quantity.")
                new_total = nonnegative_int(
                    receipt["quantity_received"], "Cumulative received quantity"
                )
                if new_total < item.quantity_received or new_total > item.quantity_sent:
                    raise ValidationError(
                        "Received quantity must be between the recorded total and quantity sent."
                    )
                delta = new_total - item.quantity_received
                source = by_id.get(item.inventory_id)
                if source is None:
                    raise NotFoundError("Source inventory not found.")
                destination_id = destination_ids[item.transfer_item_id]
                if destination_id is not None:
                    destination = by_id.get(destination_id)
                    if destination is None:
                        raise NotFoundError("Destination inventory not found.")
                    if (
                        destination.lab_id != transfer.destination_lab_id
                        or destination.component_id != source.component_id
                    ):
                        raise ValidationError(
                            "Destination inventory must match destination lab and component."
                        )
                    if destination.inventory_status in {
                        InventoryStatus.BLOCKED.value,
                        InventoryStatus.INACTIVE.value,
                    }:
                        raise ValidationError(
                            "Blocked or inactive destination inventory cannot receive stock."
                        )
                else:
                    if delta == 0:
                        continue
                    location_id = location_ids[item.transfer_item_id]
                    position_key = (
                        transfer.destination_lab_id,
                        source.component_id,
                        location_id,
                    )
                    destination = created_positions.get(position_key)
                    if destination is None:
                        component = component_repository.get_component(
                            session, source.component_id
                        )
                        if component is None:
                            raise NotFoundError("Transferred component not found.")
                        destination = inventory_repository.create_inventory(
                            session,
                            lab_id=transfer.destination_lab_id,
                            component_id=source.component_id,
                            storage_location_id=location_id,
                            quantity_available=0,
                            quantity_reserved=0,
                            unit_cost=Decimal(source.unit_cost),
                            inventory_status=InventoryStatus.OUT_OF_STOCK.value,
                        )
                        created_positions[position_key] = destination
                if delta == 0:
                    continue
                next_stock = add_received(
                    StockSnapshot(
                        destination.quantity_available, destination.quantity_reserved
                    ),
                    delta,
                )
                destination.quantity_available = next_stock.available
                component = component_repository.get_component(
                    session, destination.component_id
                )
                if component is None:
                    raise NotFoundError("Transferred component not found.")
                destination.inventory_status = inventory_status(
                    destination.quantity_available,
                    component.minimum_stock_level,
                    destination.inventory_status,
                )
                item.quantity_received = new_total
                total_received_delta += delta

            if total_received_delta == 0:
                raise ValidationError(
                    "Enter at least one newly received quantity before confirming receipt."
                )

            if all(item.quantity_received == item.quantity_sent for item in items):
                transfer.transfer_status = TransferStatus.RECEIVED.value
                transfer.received_by = actor.user_id
                transfer.received_date = receipt_date
            recompute_request_progress(session, transfer.request_id)
            session.flush()
            return transfer
    except IntegrityError:
        raise ValidationError(
            "Destination inventory changed concurrently; refresh and retry."
        ) from None


def return_temporary_items(
    actor: Actor,
    transfer_id: int,
    *,
    return_date: date,
    returns: Mapping[int, Mapping[str, object]],
):
    require_roles(actor, [Role.LAB_ASSISTANT, Role.ADMINISTRATOR])
    transfer_id = positive_int(transfer_id, "Transfer ID")
    return_date = actual_date(return_date, "Return date")
    with session_scope() as session:
        revalidate_actor(session, actor)
        transfer = transfer_repository.get_transfer(session, transfer_id, for_update=True)
        if transfer is None:
            raise NotFoundError("Transfer not found.")
        require_any_lab_scope(
            actor, [transfer.source_lab_id, transfer.destination_lab_id]
        )
        if transfer.transfer_status not in {
            TransferStatus.RECEIVED.value,
            TransferStatus.PARTIALLY_RETURNED.value,
        }:
            raise StateTransitionError("This transfer is not ready for temporary return.")
        if transfer.received_date and return_date < transfer.received_date:
            raise ValidationError("Return date cannot precede receipt date.")
        items = transfer_repository.list_items(session, transfer_id, for_update=True)
        pending_temporary = [
            item
            for item in items
            if item.return_due_date is not None and item.return_date is None
        ]
        pending_ids = {item.transfer_item_id for item in pending_temporary}
        if set(returns) - pending_ids:
            raise ValidationError("A return selection contains an unknown or completed item.")
        selected = [item for item in pending_temporary if item.transfer_item_id in returns]
        if not selected:
            raise ValidationError("Select at least one pending temporary transfer item.")

        destination_ids = {
            item.transfer_item_id: positive_int(
                returns[item.transfer_item_id].get("destination_inventory_id"),
                "Current destination inventory ID",
            )
            for item in selected
        }
        locked = inventory_repository.get_inventory_rows_for_update(
            session,
            [item.inventory_id for item in selected] + list(destination_ids.values()),
        )
        by_id = {row.inventory_id: row for row in locked}

        for item in selected:
            source = by_id.get(item.inventory_id)
            destination = by_id.get(destination_ids[item.transfer_item_id])
            if source is None or destination is None:
                raise NotFoundError("Source or destination inventory not found.")
            if (
                source.lab_id != transfer.source_lab_id
                or destination.lab_id != transfer.destination_lab_id
                or source.component_id != destination.component_id
            ):
                raise ValidationError(
                    "Return inventory must match the transfer laboratories and component."
                )
            quantity = item.quantity_received
            if quantity <= 0:
                raise ValidationError("No received quantity is available to return.")
            destination_next = remove_free_stock(
                StockSnapshot(
                    destination.quantity_available, destination.quantity_reserved
                ),
                quantity,
            )
            source_next = add_received(
                StockSnapshot(source.quantity_available, source.quantity_reserved),
                quantity,
            )
            destination.quantity_available = destination_next.available
            source.quantity_available = source_next.available
            for inventory in (source, destination):
                component = component_repository.get_component(
                    session, inventory.component_id
                )
                if component is None:
                    raise NotFoundError("Returned component not found.")
                inventory.inventory_status = inventory_status(
                    inventory.quantity_available,
                    component.minimum_stock_level,
                    inventory.inventory_status,
                )
            condition = required_text(
                returns[item.transfer_item_id].get("condition_on_return", ""),
                "Condition on return",
                max_length=100,
            )
            item.return_date = return_date
            item.condition_on_return = condition

        still_pending = any(
            item.return_due_date is not None and item.return_date is None for item in items
        )
        transfer.transfer_status = (
            TransferStatus.PARTIALLY_RETURNED.value
            if still_pending
            else TransferStatus.RETURNED.value
        )
        session.flush()
        return transfer
