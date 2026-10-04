"""Cross-lab availability plus controlled inventory maintenance."""

import logging
from decimal import Decimal

import streamlit as st

from config.constants import InventoryStatus, Role
from services import analytics_service, inventory_service, master_data_service
from ui.components import csv_download, data_table, page_header, show_error
from ui.session import require_actor
from ui.theme import apply_theme


apply_theme()
actor = require_actor()
LOGGER = logging.getLogger(__name__)
page_header(
    "Inventory",
    "Search free/reserved stock, physical positions, valuation and low-stock state",
)

try:
    rows = analytics_service.availability_view(actor)
    search = st.text_input("Filter displayed inventory")
    if search:
        needle = search.lower()
        rows = [row for row in rows if needle in " ".join(map(str, row.values())).lower()]
    frame = data_table(rows)
    csv_download(frame, filename="sems_inventory.csv")

    if actor.role in {Role.LAB_ASSISTANT.value, Role.ADMINISTRATOR.value}:
        labs = master_data_service.list_labs()
        permitted_labs = labs if actor.role == Role.ADMINISTRATOR.value else [
            lab for lab in labs if lab.lab_id == actor.lab_id
        ]
        lab_options = {f"{lab.lab_id} — {lab.lab_name}": lab.lab_id for lab in permitted_labs}
        components = master_data_service.list_components()
        component_options = {
            f"{item.component_id} — {item.component_name}": item.component_id
            for item in components
        }
        tab_create, tab_restock, tab_metadata, tab_status = st.tabs(
            ["Register", "Restock", "Move / Cost", "Status"]
        )
        with tab_create:
            if not lab_options or not component_options:
                st.info("Create the laboratory, component and storage masters first.")
            else:
                lab_label = st.selectbox("Laboratory", list(lab_options), key="inv_lab")
                lab_id = lab_options[lab_label]
                locations = master_data_service.list_locations(actor, lab_id=lab_id)
                location_options = {
                    f"{item.storage_location_id} — {item.cabinet_no}/{item.shelf_no or '-'}/{item.drawer_no or '-'}": item.storage_location_id
                    for item in locations
                }
                if not location_options:
                    st.info("Create a storage location for the selected laboratory first.")
                else:
                    with st.form("create_inventory"):
                        component_label = st.selectbox("Component", list(component_options))
                        location_label = st.selectbox("Storage location", list(location_options))
                        quantity = st.number_input("Available quantity", min_value=0, step=1)
                        unit_cost = st.number_input("Unit cost (₹)", min_value=0.0, step=0.5)
                        create = st.form_submit_button("Register inventory", type="primary")
                    if create:
                        inventory_service.create_inventory(
                            actor,
                            lab_id=lab_id,
                            component_id=component_options[component_label],
                            storage_location_id=location_options[location_label],
                            quantity_available=int(quantity),
                            unit_cost=Decimal(str(unit_cost)),
                        )
                        st.success("Inventory registered.")
                        st.rerun()
        manageable_rows = (
            rows
            if actor.role == Role.ADMINISTRATOR.value
            else [row for row in rows if int(row["lab_id"]) == actor.lab_id]
        )
        inventory_ids = [int(row["inventory_id"]) for row in manageable_rows]
        with tab_restock:
            if not inventory_ids:
                st.info("No inventory record is available for restocking.")
            else:
                with st.form("restock_inventory"):
                    inventory_id = st.selectbox("Inventory ID", inventory_ids)
                    restock_quantity = st.number_input("Restock quantity", min_value=1, step=1)
                    restock = st.form_submit_button("Add stock")
                if restock:
                    inventory_service.restock_inventory(
                        actor, int(inventory_id), int(restock_quantity)
                    )
                    st.success("Stock added.")
                    st.rerun()
        with tab_metadata:
            if not inventory_ids:
                st.info("No inventory record is available for metadata updates.")
            else:
                with st.form("inventory_metadata"):
                    inventory_id = st.selectbox("Inventory ID", inventory_ids, key="meta_id")
                    selected_row = next(
                        row
                        for row in manageable_rows
                        if int(row["inventory_id"]) == int(inventory_id)
                    )
                    target_lab = int(selected_row["lab_id"])
                    locations = master_data_service.list_locations(actor, lab_id=target_lab)
                    location_options = {
                        f"{item.storage_location_id} — {item.cabinet_no}/{item.shelf_no or '-'}/{item.drawer_no or '-'}": item.storage_location_id
                        for item in locations
                    }
                    current_location = int(selected_row["storage_location_id"])
                    labels = list(location_options)
                    current_label = next(
                        label for label, value in location_options.items() if value == current_location
                    )
                    location_label = st.selectbox(
                        "Storage location", labels, index=labels.index(current_label)
                    )
                    unit_cost = st.number_input(
                        "Unit cost (₹)",
                        min_value=0.0,
                        value=float(selected_row["unit_cost"]),
                        step=0.5,
                    )
                    update = st.form_submit_button("Save inventory metadata")
                if update:
                    inventory_service.update_inventory_metadata(
                        actor,
                        int(inventory_id),
                        storage_location_id=location_options[location_label],
                        unit_cost=Decimal(str(unit_cost)),
                    )
                    st.success("Inventory metadata updated.")
                    st.rerun()
        with tab_status:
            if not inventory_ids:
                st.info("No inventory record is available for status control.")
            else:
                with st.form("inventory_status"):
                    inventory_id = st.selectbox("Inventory ID", inventory_ids, key="status_id")
                    status = st.selectbox(
                        "Operational status",
                        [
                            InventoryStatus.AVAILABLE.value,
                            InventoryStatus.BLOCKED.value,
                            InventoryStatus.INACTIVE.value,
                        ],
                    )
                    set_status = st.form_submit_button("Set status")
                if set_status:
                    inventory_service.set_operational_status(actor, int(inventory_id), status)
                    st.success("Inventory status updated.")
                    st.rerun()
except Exception as exc:
    LOGGER.exception("Inventory operation failed")
    show_error(exc)
