"""Administrator laboratory master-data page."""

import logging

import streamlit as st

from config.constants import Role
from services import master_data_service
from ui.components import data_table, page_header, section_heading, show_error
from ui.session import require_actor
from ui.theme import apply_theme


apply_theme()
actor = require_actor(Role.ADMINISTRATOR)
LOGGER = logging.getLogger(__name__)
page_header("Laboratories", "Maintain the frozen LAB master without activation flags")

try:
    search = st.text_input("Search laboratory")
    labs = master_data_service.list_labs(search or None)
    data_table(labs)

    section_heading("Create laboratory")
    with st.form("create_lab"):
        lab_name = st.text_input("Laboratory name")
        department = st.text_input("Department name")
        building = st.text_input("Building name")
        lab_type = st.text_input("Laboratory type")
        create = st.form_submit_button("Create laboratory", type="primary")
    if create:
        master_data_service.create_lab(
            actor,
            lab_name=lab_name,
            department_name=department,
            building_name=building,
            lab_type=lab_type,
        )
        st.success("Laboratory created.")
        st.rerun()

    if labs:
        section_heading("Laboratory contacts")
        contact_lab_map = {f"{lab.lab_id} — {lab.lab_name}": lab.lab_id for lab in labs}
        contact_lab_label = st.selectbox(
            "Laboratory for contacts", list(contact_lab_map)
        )
        contact_lab_id = contact_lab_map[contact_lab_label]
        contacts = master_data_service.list_lab_contacts(actor, contact_lab_id)
        data_table(contacts, empty_message="No contact number is recorded for this laboratory.")
        with st.form("add_lab_contact"):
            contact_number = st.text_input(
                "Contact number", placeholder="020-5550-1101"
            )
            add_contact = st.form_submit_button("Add laboratory contact")
        if add_contact:
            master_data_service.add_lab_contact(
                actor, contact_lab_id, contact_number
            )
            st.success("Laboratory contact added.")
            st.rerun()

        section_heading("Update laboratory")
        lab_map = {f"{lab.lab_id} — {lab.lab_name}": lab for lab in labs}
        selected_label = st.selectbox("Select laboratory", list(lab_map))
        selected = lab_map[selected_label]
        with st.form("update_lab"):
            edit_name = st.text_input("Laboratory name", selected.lab_name)
            edit_department = st.text_input("Department name", selected.department_name)
            edit_building = st.text_input("Building name", selected.building_name)
            edit_type = st.text_input("Laboratory type", selected.lab_type)
            update = st.form_submit_button("Save changes")
        if update:
            master_data_service.update_lab(
                actor,
                selected.lab_id,
                lab_name=edit_name,
                department_name=edit_department,
                building_name=edit_building,
                lab_type=edit_type,
            )
            st.success("Laboratory updated.")
            st.rerun()
except Exception as exc:
    LOGGER.exception("Laboratory operation failed")
    show_error(exc)
