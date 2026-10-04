"""Static checks for transaction/locking and frozen condition timing."""

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.contract


def test_transfer_service_uses_stable_row_lock_helper_for_stock_changes() -> None:
    source = (ROOT / "services/transfer_service.py").read_text(encoding="utf-8")
    assert source.count("get_inventory_rows_for_update") >= 5
    assert "dispatch_reserved(" in source
    assert "reserve_stock(" in source
    assert "release_reservation(" in source


def test_conditions_are_written_only_in_correct_workflow_methods() -> None:
    source = (ROOT / "services/transfer_service.py").read_text(encoding="utf-8")
    dispatch = source[source.index("def dispatch_transfer"):source.index("def _resolve_destination_candidates")]
    receive = source[source.index("def receive_transfer"):source.index("def return_temporary_items")]
    returned = source[source.index("def return_temporary_items"):]
    assert "condition_on_issue" in dispatch
    assert "condition_on_return" not in dispatch
    assert "condition_on_return" not in receive
    assert "condition_on_return" in returned


def test_no_destination_inventory_attribute_is_assigned() -> None:
    source = (ROOT / "services/transfer_service.py").read_text(encoding="utf-8")
    assert ".destination_inventory_id" not in source


def test_receipt_reuses_a_new_destination_position_within_one_transaction() -> None:
    source = (ROOT / "services/transfer_service.py").read_text(encoding="utf-8")
    assert "created_positions" in source
    assert "position_key = (" in source
    assert "created_positions.get(position_key)" in source
    assert "created_positions[position_key] = destination" in source


def test_request_review_is_frozen_after_transfer_allocation_begins() -> None:
    source = (ROOT / "services/request_service.py").read_text(encoding="utf-8")
    review = source[source.index("def review_request"):source.index("def cancel_request")]
    assert "allocated_quantity_by_component" in review
    assert "Approval quantities cannot be revised" in review
