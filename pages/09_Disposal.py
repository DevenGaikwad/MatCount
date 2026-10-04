"""Administrator-only disposal event page."""

import logging
from datetime import date

import streamlit as st

from config.constants import Role
from services import disposal_service, inventory_service
from ui.components import data_table, page_header, section_heading, show_error
from ui.session import require_actor
from ui.theme import apply_theme


apply_theme()
actor = require_actor(Role.ADMINISTRATOR)
LOGGER = logging.getLogger(__name__)
page_header("Authorized Disposal", "Preserve disposal history and decrement free stock atomically")

try:
    history = disposal_service.list_disposals(actor)
    data_table(history)
    inventory = inventory_service.list_inventory(actor)
    available = [item for item in inventory if item.quantity_available > 0]
    section_heading("Record disposal")
    if not available:
        st.info("No free inventory is available for disposal.")
    else:
        options = {
            f"{item.inventory_id} — Lab {item.lab_id} — Component {item.component_id} — Free {item.quantity_available}": item
            for item in available
        }
        with st.form("dispose_inventory"):
            inventory_label = st.selectbox("Inventory", list(options))
            selected = options[inventory_label]
            quantity = st.number_input(
                "Quantity disposed",
                min_value=1,
                max_value=int(selected.quantity_available),
                step=1,
            )
            event_date = st.date_input("Disposal date", date.today())
            reason = st.text_area("Disposal reason")
            method = st.text_input("Disposal method")
            remarks = st.text_area("Remarks (optional)")
            confirmed = st.checkbox("I confirm this authorized disposal event")
            submit = st.form_submit_button("Record disposal", type="primary")
        if submit:
            if not confirmed:
                st.error("Confirmation is required.")
            else:
                disposal_service.dispose_inventory(
                    actor,
                    inventory_id=selected.inventory_id,
                    quantity_disposed=int(quantity),
                    disposal_date=event_date,
                    disposal_reason=reason,
                    disposal_method=method,
                    remarks=remarks or None,
                )
                st.success("Disposal recorded and free stock decremented.")
                st.rerun()
except Exception as exc:
    LOGGER.exception("Disposal operation failed")
    show_error(exc)

