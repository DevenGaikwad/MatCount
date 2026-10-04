"""Lab-scoped storage-coordinate maintenance."""

import logging

import streamlit as st

from config.constants import Role
from services import master_data_service
from ui.components import data_table, page_header, show_error
from ui.session import require_actor
from ui.theme import apply_theme


apply_theme()
actor = require_actor(Role.LAB_ASSISTANT, Role.ADMINISTRATOR)
LOGGER = logging.getLogger(__name__)
page_header(
    "Storage Locations",
    "Cabinet, shelf and drawer coordinates with null-normalized duplicate protection",
)

try:
    labs = master_data_service.list_labs()
    permitted_labs = labs if actor.role == Role.ADMINISTRATOR.value else [
        lab for lab in labs if lab.lab_id == actor.lab_id
    ]
    lab_options = {f"{lab.lab_id} — {lab.lab_name}": lab.lab_id for lab in permitted_labs}
    if not lab_options:
        st.info("No permitted laboratory is available. Create/assign a laboratory first.")
        st.stop()
    selected_lab_label = st.selectbox("Laboratory", list(lab_options))
    selected_lab_id = lab_options[selected_lab_label]
    locations = master_data_service.list_locations(actor, lab_id=selected_lab_id)
    data_table(locations)

    tab_create, tab_update = st.tabs(["Create", "Update"])
    with tab_create:
        with st.form("create_location"):
            cabinet = st.text_input("Cabinet number")
            shelf = st.text_input("Shelf number (optional)")
            drawer = st.text_input("Drawer number (optional)")
            location_type = st.selectbox(
                "Location type", ["CABINET", "SHELF", "DRAWER", "BIN"]
            )
            create = st.form_submit_button("Create location", type="primary")
        if create:
            master_data_service.create_location(
                actor,
                lab_id=selected_lab_id,
                cabinet_no=cabinet,
                shelf_no=shelf or None,
                drawer_no=drawer or None,
                location_type=location_type,
            )
            st.success("Storage location created.")
            st.rerun()
    with tab_update:
        if not locations:
            st.info("No location is available for update.")
        else:
            location_map = {
                f"{item.storage_location_id} — {item.cabinet_no}/{item.shelf_no or '-'}/{item.drawer_no or '-'}": item
                for item in locations
            }
            selection = st.selectbox("Select location", list(location_map))
            selected = location_map[selection]
            with st.form("update_location"):
                edit_cabinet = st.text_input("Cabinet number", selected.cabinet_no)
                edit_shelf = st.text_input("Shelf number", selected.shelf_no or "")
                edit_drawer = st.text_input("Drawer number", selected.drawer_no or "")
                types = ["CABINET", "SHELF", "DRAWER", "BIN"]
                edit_type = st.selectbox(
                    "Location type",
                    types,
                    index=types.index(selected.location_type)
                    if selected.location_type in types
                    else 0,
                )
                update = st.form_submit_button("Save changes")
            if update:
                master_data_service.update_location(
                    actor,
                    selected.storage_location_id,
                    cabinet_no=edit_cabinet,
                    shelf_no=edit_shelf or None,
                    drawer_no=edit_drawer or None,
                    location_type=edit_type,
                )
                st.success("Storage location updated.")
                st.rerun()
except Exception as exc:
    LOGGER.exception("Storage-location operation failed")
    show_error(exc)
