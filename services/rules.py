"""Pure frozen business-rule helpers, independently unit-testable."""

from __future__ import annotations

from dataclasses import dataclass

from config.constants import InventoryStatus, RequestItemStatus, RequestStatus
from services.exceptions import InsufficientStockError, ValidationError


@dataclass(frozen=True, slots=True)
class StockSnapshot:
    available: int
    reserved: int


def _nonnegative(snapshot: StockSnapshot) -> StockSnapshot:
    if snapshot.available < 0 or snapshot.reserved < 0:
        raise InsufficientStockError("Stock quantity cannot become negative.")
    return snapshot


def _positive(quantity: int, label: str = "quantity") -> int:
    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
        raise ValidationError(f"{label} must be a positive whole number.")
    return quantity


def reserve_stock(snapshot: StockSnapshot, quantity: int) -> StockSnapshot:
    quantity = _positive(quantity)
    if snapshot.available < quantity:
        raise InsufficientStockError("Insufficient free stock for reservation.")
    return _nonnegative(
        StockSnapshot(
            available=snapshot.available - quantity,
            reserved=snapshot.reserved + quantity,
        )
    )


def release_reservation(snapshot: StockSnapshot, quantity: int) -> StockSnapshot:
    quantity = _positive(quantity)
    if snapshot.reserved < quantity:
        raise InsufficientStockError("Reservation release exceeds reserved stock.")
    return _nonnegative(
        StockSnapshot(
            available=snapshot.available + quantity,
            reserved=snapshot.reserved - quantity,
        )
    )


def dispatch_reserved(snapshot: StockSnapshot, quantity: int) -> StockSnapshot:
    quantity = _positive(quantity)
    if snapshot.reserved < quantity:
        raise InsufficientStockError("Dispatch exceeds reserved stock.")
    return _nonnegative(
        StockSnapshot(
            available=snapshot.available,
            reserved=snapshot.reserved - quantity,
        )
    )


def add_received(snapshot: StockSnapshot, quantity: int) -> StockSnapshot:
    quantity = _positive(quantity)
    return StockSnapshot(
        available=snapshot.available + quantity, reserved=snapshot.reserved
    )


def remove_free_stock(snapshot: StockSnapshot, quantity: int) -> StockSnapshot:
    quantity = _positive(quantity)
    if snapshot.available < quantity:
        raise InsufficientStockError("Operation exceeds free available stock.")
    return _nonnegative(
        StockSnapshot(
            available=snapshot.available - quantity,
            reserved=snapshot.reserved,
        )
    )


def validate_approval(quantity_requested: int, quantity_approved: int) -> None:
    _positive(quantity_requested, "Requested quantity")
    if (
        not isinstance(quantity_approved, int)
        or isinstance(quantity_approved, bool)
        or quantity_approved < 0
        or quantity_approved > quantity_requested
    ):
        raise ValidationError(
            "Approved quantity must be between zero and requested quantity."
        )


def approval_item_status(quantity_requested: int, quantity_approved: int) -> str:
    validate_approval(quantity_requested, quantity_approved)
    if quantity_approved == 0:
        return RequestItemStatus.REJECTED.value
    if quantity_approved < quantity_requested:
        return RequestItemStatus.PARTIALLY_APPROVED.value
    return RequestItemStatus.APPROVED.value


def derive_request_status(item_statuses: list[str]) -> str:
    if not item_statuses:
        raise ValidationError("A request must contain at least one item.")
    statuses = set(item_statuses)
    if statuses == {RequestItemStatus.REJECTED.value}:
        return RequestStatus.REJECTED.value
    if statuses <= {
        RequestItemStatus.FULFILLED.value,
        RequestItemStatus.REJECTED.value,
    } and RequestItemStatus.FULFILLED.value in statuses:
        return RequestStatus.FULFILLED.value
    if RequestItemStatus.PENDING.value in statuses:
        return RequestStatus.SUBMITTED.value
    approved_like = {
        RequestItemStatus.APPROVED.value,
        RequestItemStatus.ALLOCATED.value,
        RequestItemStatus.REJECTED.value,
    }
    if statuses <= approved_like and statuses.intersection(
        {RequestItemStatus.APPROVED.value, RequestItemStatus.ALLOCATED.value}
    ):
        if RequestItemStatus.REJECTED.value not in statuses:
            return RequestStatus.APPROVED.value
    return RequestStatus.PARTIALLY_APPROVED.value


def inventory_status(
    quantity_available: int, minimum_stock_level: int, current_status: str
) -> str:
    if quantity_available < 0 or minimum_stock_level < 0:
        raise ValidationError("Stock and minimum-stock values cannot be negative.")
    if current_status in {
        InventoryStatus.BLOCKED.value,
        InventoryStatus.INACTIVE.value,
    }:
        return current_status
    if quantity_available == 0:
        return InventoryStatus.OUT_OF_STOCK.value
    if quantity_available <= minimum_stock_level:
        return InventoryStatus.LOW_STOCK.value
    return InventoryStatus.AVAILABLE.value


def validate_distinct_labs(source_lab_id: int, destination_lab_id: int) -> None:
    if source_lab_id == destination_lab_id:
        raise ValidationError("Source and destination laboratories must differ.")
