"""Inter-laboratory transfer lifecycle UI."""

import logging
from datetime import date, timedelta

import streamlit as st

from config.constants import Role, TransferStatus
from services import (
    inventory_service,
    master_data_service,
    request_service,
    transfer_service,
)
from ui.components import data_table, page_header, section_heading, show_error
from ui.session import require_actor
from ui.theme import apply_theme


apply_theme()
actor = require_actor()
LOGGER = logging.getLogger(__name__)
page_header(
    "Inter-Laboratory Transfers",
    "Reservation, dispatch, receipt and temporary return with atomic stock control",
)

try:
    transfers = transfer_service.list_transfers(actor)
    data_table(transfers)

    if transfers:
        section_heading("Inspect transfer items")
        transfer_options = {
            f"{item.transfer_id} — {item.transfer_status} — Request {item.request_id}": item
            for item in transfers
        }
        inspect_label = st.selectbox("Transfer", list(transfer_options), key="inspect_transfer")
        inspected, inspected_items = transfer_service.get_transfer_with_items(
            actor, transfer_options[inspect_label].transfer_id
        )
        st.caption(
            f"Source Lab {inspected.source_lab_id} → Destination Lab {inspected.destination_lab_id}"
        )
        data_table(inspected_items)

    if actor.role in {Role.LAB_ASSISTANT.value, Role.ADMINISTRATOR.value}:
        section_heading("Plan transfer")
        approved_requests = request_service.list_approved_for_transfer(actor)
        if actor.role == Role.LAB_ASSISTANT.value:
            approved_requests = [
                item
                for item in approved_requests
                if item.requesting_lab_id != actor.lab_id
            ]
        if not approved_requests:
            st.info("No approved request is available for allocation.")
        else:
            request_options = {
                f"{item.request_id} — Destination Lab {item.requesting_lab_id} — {item.reason[:50]}": item
                for item in approved_requests
            }
            request_label = st.selectbox("Approved request", list(request_options))
            selected_request = request_options[request_label]
            if actor.role == Role.LAB_ASSISTANT.value:
                source_lab_id = actor.lab_id
            else:
                source_labs = [
                    lab
                    for lab in master_data_service.list_labs()
                    if lab.lab_id != selected_request.requesting_lab_id
                ]
                source_options = {
                    f"{lab.lab_id} — {lab.lab_name}": lab.lab_id for lab in source_labs
                }
                source_label = (
                    st.selectbox("Source laboratory", list(source_options))
                    if source_options
                    else None
                )
                source_lab_id = source_options[source_label] if source_label else None

            if source_lab_id is None:
                st.info("No distinct source laboratory is available.")
            else:
                inventory = inventory_service.list_inventory(
                    actor, lab_id=source_lab_id
                )
                inventory_options = {
                    f"{item.inventory_id} — Component {item.component_id} — Free {item.quantity_available}": item
                    for item in inventory
                    if item.quantity_available > 0
                }
                selected_inventory = st.multiselect(
                    "Source inventory allocations", list(inventory_options)
                )
                allocations = []
                for label in selected_inventory:
                    item = inventory_options[label]
                    quantity = st.number_input(
                        f"Quantity — {label}",
                        min_value=1,
                        max_value=max(1, int(item.quantity_available)),
                        value=1,
                        step=1,
                        key=f"alloc_q_{item.inventory_id}",
                    )
                    temporary = st.checkbox(
                        f"Temporary transfer — Inventory {item.inventory_id}",
                        key=f"temp_{item.inventory_id}",
                    )
                    due_date = (
                        st.date_input(
                            f"Return due date — Inventory {item.inventory_id}",
                            date.today() + timedelta(days=14),
                            key=f"due_{item.inventory_id}",
                        )
                        if temporary
                        else None
                    )
                    allocations.append(
                        {
                            "inventory_id": item.inventory_id,
                            "quantity_sent": int(quantity),
                            "return_due_date": due_date,
                        }
                    )
                if st.button("Create DRAFT transfer", type="primary"):
                    transfer_service.create_transfer(
                        actor,
                        request_id=selected_request.request_id,
                        source_lab_id=source_lab_id,
                        destination_lab_id=selected_request.requesting_lab_id,
                        allocations=allocations,
                    )
                    st.success("DRAFT transfer created.")
                    st.rerun()

    if actor.role == Role.ADMINISTRATOR.value:
        section_heading("Approve or reject transfer")
        pending = [
            item for item in transfers if item.transfer_status == TransferStatus.DRAFT.value
        ]
        if pending:
            pending_options = {
                f"{item.transfer_id} — Request {item.request_id}": item.transfer_id
                for item in pending
            }
            with st.form("approve_transfer"):
                pending_label = st.selectbox("Pending transfer", list(pending_options))
                choice = st.radio("Decision", ["APPROVE", "REJECT"], horizontal=True)
                commit = st.form_submit_button("Commit decision", type="primary")
            if commit:
                if choice == "APPROVE":
                    transfer_service.approve_transfer(
                        actor, pending_options[pending_label]
                    )
                else:
                    transfer_service.reject_transfer(
                        actor, pending_options[pending_label]
                    )
                st.success("Transfer decision committed.")
                st.rerun()
        else:
            st.info("No pending DRAFT transfer is visible.")

    if actor.role in {Role.LAB_ASSISTANT.value, Role.ADMINISTRATOR.value}:
        section_heading("Dispatch")
        dispatchable = [
            item
            for item in transfers
            if item.transfer_status == TransferStatus.APPROVED.value
            and (actor.role == Role.ADMINISTRATOR.value or item.source_lab_id == actor.lab_id)
        ]
        if dispatchable:
            dispatch_options = {
                f"{item.transfer_id} — Request {item.request_id}": item
                for item in dispatchable
            }
            dispatch_label = st.selectbox("Transfer to dispatch", list(dispatch_options))
            transfer = dispatch_options[dispatch_label]
            _, items = transfer_service.get_transfer_with_items(actor, transfer.transfer_id)
            conditions = {}
            with st.form("dispatch_transfer"):
                dispatch_date = st.date_input("Dispatch date", date.today())
                for item in items:
                    conditions[item.transfer_item_id] = st.text_input(
                        f"Condition on issue — Item {item.transfer_item_id}",
                        value="GOOD",
                    )
                dispatch = st.form_submit_button("Confirm dispatch", type="primary")
            if dispatch:
                transfer_service.dispatch_transfer(
                    actor,
                    transfer.transfer_id,
                    dispatch_date=dispatch_date,
                    conditions_on_issue=conditions,
                )
                st.success("Transfer dispatched; reserved stock was reduced only.")
                st.rerun()
        else:
            st.info("No approved transfer is ready for dispatch in your scope.")

        section_heading("Receive")
        receivable = [
            item
            for item in transfers
            if item.transfer_status == TransferStatus.DISPATCHED.value
            and (
                actor.role == Role.ADMINISTRATOR.value
                or item.destination_lab_id == actor.lab_id
            )
        ]
        if receivable:
            receive_options = {
                f"{item.transfer_id} — From Lab {item.source_lab_id}": item
                for item in receivable
            }
            receive_label = st.selectbox("Transfer to receive", list(receive_options))
            transfer = receive_options[receive_label]
            _, items = transfer_service.get_transfer_with_items(actor, transfer.transfer_id)
            destination_inventory = inventory_service.list_inventory(
                actor, lab_id=transfer.destination_lab_id
            )
            destination_locations = master_data_service.list_locations(
                actor, lab_id=transfer.destination_lab_id
            )
            destination_inventory_options = {
                f"Inventory {row.inventory_id} — Component {row.component_id} — Free {row.quantity_available}": row.inventory_id
                for row in destination_inventory
            }
            destination_location_options = {
                f"Location {row.storage_location_id} — {row.cabinet_no}/{row.shelf_no or '-'}/{row.drawer_no or '-'}": row.storage_location_id
                for row in destination_locations
            }
            receipts = {}
            receipt_ready = bool(
                destination_inventory_options or destination_location_options
            )
            with st.form("receive_transfer"):
                receipt_date = st.date_input("Receipt date", date.today())
                st.caption(
                    "For each item, select an existing destination row or a destination storage location."
                )
                for item in items:
                    quantity = st.number_input(
                        f"Cumulative quantity received — Item {item.transfer_item_id}",
                        min_value=int(item.quantity_received),
                        max_value=int(item.quantity_sent),
                        value=int(item.quantity_sent),
                        step=1,
                    )
                    methods = []
                    if destination_inventory_options:
                        methods.append("Existing inventory")
                    if destination_location_options:
                        methods.append("Storage location")
                    method = st.radio(
                        f"Destination method — Item {item.transfer_item_id}",
                        methods or ["No destination available"],
                        horizontal=True,
                        key=f"receipt_method_{item.transfer_item_id}",
                    )
                    destination_inventory_id = None
                    location_id = None
                    if method == "Existing inventory":
                        destination_label = st.selectbox(
                            f"Destination inventory — Item {item.transfer_item_id}",
                            list(destination_inventory_options),
                            key=f"receipt_inventory_{item.transfer_item_id}",
                        )
                        destination_inventory_id = destination_inventory_options[
                            destination_label
                        ]
                    elif method == "Storage location":
                        location_label = st.selectbox(
                            f"Destination storage location — Item {item.transfer_item_id}",
                            list(destination_location_options),
                            key=f"receipt_location_{item.transfer_item_id}",
                        )
                        location_id = destination_location_options[location_label]
                    receipts[item.transfer_item_id] = {
                        "quantity_received": int(quantity),
                        "destination_inventory_id": destination_inventory_id,
                        "storage_location_id": location_id,
                    }
                receive = st.form_submit_button(
                    "Confirm receipt", type="primary", disabled=not receipt_ready
                )
            if receive:
                transfer_service.receive_transfer(
                    actor,
                    transfer.transfer_id,
                    receipt_date=receipt_date,
                    receipts=receipts,
                )
                st.success("Receipt committed to selected destination inventory.")
                st.rerun()
        else:
            st.info("No dispatched transfer is awaiting receipt in your scope.")

        section_heading("Temporary return")
        returnable = [
            item
            for item in transfers
            if item.transfer_status
            in {TransferStatus.RECEIVED.value, TransferStatus.PARTIALLY_RETURNED.value}
        ]
        if returnable:
            return_options = {
                f"{item.transfer_id} — {item.transfer_status}": item for item in returnable
            }
            return_label = st.selectbox("Transfer", list(return_options), key="return_transfer")
            transfer = return_options[return_label]
            _, items = transfer_service.get_transfer_with_items(actor, transfer.transfer_id)
            pending_items = [
                item for item in items if item.return_due_date and not item.return_date
            ]
            if not pending_items:
                st.info("This transfer has no pending temporary item.")
            else:
                returns = {}
                can_list_destination = (
                    actor.role == Role.ADMINISTRATOR.value
                    or actor.lab_id == transfer.destination_lab_id
                )
                return_inventory_options = {}
                if can_list_destination:
                    destination_inventory = inventory_service.list_inventory(
                        actor, lab_id=transfer.destination_lab_id
                    )
                    return_inventory_options = {
                        f"Inventory {row.inventory_id} — Component {row.component_id} — Free {row.quantity_available}": row.inventory_id
                        for row in destination_inventory
                    }
                with st.form("return_items"):
                    actual_return_date = st.date_input("Actual return date", date.today())
                    for item in pending_items:
                        selected = st.checkbox(
                            f"Return item {item.transfer_item_id} ({item.quantity_received} units)"
                        )
                        if return_inventory_options:
                            destination_label = st.selectbox(
                                f"Current destination inventory — Item {item.transfer_item_id}",
                                list(return_inventory_options),
                                key=f"return_inventory_{item.transfer_item_id}",
                            )
                            destination_inventory_id = return_inventory_options[
                                destination_label
                            ]
                        else:
                            destination_inventory_id = st.number_input(
                                f"Current destination inventory ID — Item {item.transfer_item_id}",
                                min_value=1,
                                step=1,
                            )
                        condition = st.text_input(
                            f"Condition on return — Item {item.transfer_item_id}",
                            value="GOOD",
                        )
                        if selected:
                            returns[item.transfer_item_id] = {
                                "destination_inventory_id": int(
                                    destination_inventory_id
                                ),
                                "condition_on_return": condition,
                            }
                    return_items = st.form_submit_button(
                        "Confirm selected returns", type="primary"
                    )
                if return_items:
                    transfer_service.return_temporary_items(
                        actor,
                        transfer.transfer_id,
                        return_date=actual_return_date,
                        returns=returns,
                    )
                    st.success("Temporary return committed.")
                    st.rerun()
        else:
            st.info("No received transfer is available for temporary return.")

    if actor.role in {Role.LAB_ASSISTANT.value, Role.ADMINISTRATOR.value}:
        cancellable = [
            item
            for item in transfers
            if item.transfer_status
            in {TransferStatus.DRAFT.value, TransferStatus.APPROVED.value}
        ]
        section_heading("Cancel before dispatch")
        if cancellable:
            cancel_options = {
                f"{item.transfer_id} — {item.transfer_status}": item.transfer_id
                for item in cancellable
            }
            with st.form("cancel_transfer"):
                cancel_label = st.selectbox("Transfer", list(cancel_options))
                confirmed = st.checkbox("I confirm this pre-dispatch cancellation")
                cancel = st.form_submit_button("Cancel transfer")
            if cancel:
                if not confirmed:
                    st.error("Confirmation is required.")
                else:
                    transfer_service.cancel_transfer(actor, cancel_options[cancel_label])
                    st.success("Transfer cancelled; any reservation was released.")
                    st.rerun()
        else:
            st.info("No transfer is eligible for cancellation.")
except Exception as exc:
    LOGGER.exception("Transfer operation failed")
    show_error(exc)
