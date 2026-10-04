"""Unit tests for frozen quantity and state semantics."""

import pytest

from config.constants import InventoryStatus, RequestItemStatus, RequestStatus
from services.exceptions import InsufficientStockError, ValidationError
from services.rules import (
    StockSnapshot,
    add_received,
    approval_item_status,
    derive_request_status,
    dispatch_reserved,
    inventory_status,
    release_reservation,
    remove_free_stock,
    reserve_stock,
    validate_approval,
    validate_distinct_labs,
)


def test_approval_moves_available_to_reserved() -> None:
    assert reserve_stock(StockSnapshot(100, 4), 25) == StockSnapshot(75, 29)


def test_reservation_rejects_insufficient_free_stock() -> None:
    with pytest.raises(InsufficientStockError):
        reserve_stock(StockSnapshot(3, 10), 4)


def test_cancellation_releases_exact_reservation() -> None:
    assert release_reservation(StockSnapshot(75, 29), 25) == StockSnapshot(100, 4)


def test_dispatch_reduces_reserved_only() -> None:
    assert dispatch_reserved(StockSnapshot(75, 29), 25) == StockSnapshot(75, 4)


def test_dispatch_rejects_quantity_above_reserved() -> None:
    with pytest.raises(InsufficientStockError):
        dispatch_reserved(StockSnapshot(75, 3), 4)


def test_receipt_increments_destination_available() -> None:
    assert add_received(StockSnapshot(8, 0), 20) == StockSnapshot(28, 0)


def test_return_and_disposal_remove_only_free_stock() -> None:
    destination = remove_free_stock(StockSnapshot(8, 1), 3)
    assert destination == StockSnapshot(5, 1)
    with pytest.raises(InsufficientStockError):
        remove_free_stock(StockSnapshot(2, 50), 3)


@pytest.mark.parametrize(
    ("requested", "approved", "expected"),
    [
        (10, 0, RequestItemStatus.REJECTED.value),
        (10, 4, RequestItemStatus.PARTIALLY_APPROVED.value),
        (10, 10, RequestItemStatus.APPROVED.value),
    ],
)
def test_request_item_approval_states(requested: int, approved: int, expected: str) -> None:
    assert approval_item_status(requested, approved) == expected


def test_approved_quantity_cannot_exceed_requested() -> None:
    with pytest.raises(ValidationError):
        validate_approval(5, 6)


@pytest.mark.parametrize(
    ("statuses", "expected"),
    [
        ([RequestItemStatus.REJECTED.value], RequestStatus.REJECTED.value),
        ([RequestItemStatus.PENDING.value], RequestStatus.SUBMITTED.value),
        ([RequestItemStatus.APPROVED.value], RequestStatus.APPROVED.value),
        ([RequestItemStatus.ALLOCATED.value], RequestStatus.APPROVED.value),
        (
            [RequestItemStatus.APPROVED.value, RequestItemStatus.REJECTED.value],
            RequestStatus.PARTIALLY_APPROVED.value,
        ),
        (
            [RequestItemStatus.FULFILLED.value, RequestItemStatus.REJECTED.value],
            RequestStatus.FULFILLED.value,
        ),
    ],
)
def test_request_header_derivation(statuses: list[str], expected: str) -> None:
    assert derive_request_status(statuses) == expected


def test_empty_request_status_derivation_is_rejected() -> None:
    with pytest.raises(ValidationError):
        derive_request_status([])


@pytest.mark.parametrize(
    ("available", "minimum", "current", "expected"),
    [
        (0, 5, "AVAILABLE", InventoryStatus.OUT_OF_STOCK.value),
        (3, 5, "AVAILABLE", InventoryStatus.LOW_STOCK.value),
        (6, 5, "LOW_STOCK", InventoryStatus.AVAILABLE.value),
        (20, 5, "BLOCKED", InventoryStatus.BLOCKED.value),
        (20, 5, "INACTIVE", InventoryStatus.INACTIVE.value),
    ],
)
def test_inventory_status_precedence(
    available: int, minimum: int, current: str, expected: str
) -> None:
    assert inventory_status(available, minimum, current) == expected


def test_source_and_destination_labs_must_differ() -> None:
    with pytest.raises(ValidationError):
        validate_distinct_labs(2, 2)

