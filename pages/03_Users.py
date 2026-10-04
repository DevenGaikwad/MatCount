"""Administrator USER and account-status page."""

import logging

import streamlit as st

from config.constants import AccountStatus, Role
from services import master_data_service
from ui.components import data_table, page_header, section_heading, show_error
from ui.session import require_actor
from ui.theme import apply_theme


apply_theme()
actor = require_actor(Role.ADMINISTRATOR)
LOGGER = logging.getLogger(__name__)
page_header("Users and Roles", "Manage USER records; credential hashes remain external")

try:
    labs = master_data_service.list_labs()
    lab_options = {f"{lab.lab_id} — {lab.lab_name}": lab.lab_id for lab in labs}
    search = st.text_input("Search name or email")
    users = master_data_service.list_users(actor, search=search or None)
    data_table(users)

    section_heading("Create user")
    with st.form("create_user"):
        lab_label = st.selectbox("Assigned laboratory", list(lab_options))
        full_name = st.text_input("Full name")
        email = st.text_input("Email")
        role = st.selectbox("Role", [item.value for item in Role])
        account_status = st.selectbox(
            "Account status", [item.value for item in AccountStatus]
        )
        create = st.form_submit_button("Create user", type="primary")
    if create:
        master_data_service.create_user(
            actor,
            lab_id=lab_options[lab_label],
            full_name=full_name,
            email=email,
            role=role,
            account_status=account_status,
        )
        st.success("User created. Configure the demo hash separately if login is required.")
        st.rerun()

    if users:
        section_heading("User phone numbers")
        phone_user_map = {f"{user.user_id} — {user.full_name}": user.user_id for user in users}
        phone_user_label = st.selectbox("User for phone numbers", list(phone_user_map))
        phone_user_id = phone_user_map[phone_user_label]
        phones = master_data_service.list_user_phones(actor, phone_user_id)
        data_table(phones, empty_message="No phone number is recorded for this user.")
        with st.form("add_user_phone"):
            phone_number = st.text_input(
                "Phone number", placeholder="+91-90000-00001"
            )
            add_phone = st.form_submit_button("Add user phone number")
        if add_phone:
            master_data_service.add_user_phone(actor, phone_user_id, phone_number)
            st.success("User phone number added.")
            st.rerun()

        section_heading("Update user")
        user_map = {f"{user.user_id} — {user.full_name}": user for user in users}
        selected_label = st.selectbox("Select user", list(user_map))
        selected = user_map[selected_label]
        reverse_labs = {value: key for key, value in lab_options.items()}
        with st.form("update_user"):
            edit_lab_label = st.selectbox(
                "Assigned laboratory",
                list(lab_options),
                index=list(lab_options).index(reverse_labs[selected.lab_id]),
            )
            edit_name = st.text_input("Full name", selected.full_name)
            edit_email = st.text_input("Email", selected.email)
            role_values = [item.value for item in Role]
            edit_role = st.selectbox(
                "Role", role_values, index=role_values.index(selected.role)
            )
            status_values = [item.value for item in AccountStatus]
            edit_status = st.selectbox(
                "Account status",
                status_values,
                index=status_values.index(selected.account_status),
            )
            update = st.form_submit_button("Save changes")
        if update:
            master_data_service.update_user(
                actor,
                selected.user_id,
                lab_id=lab_options[edit_lab_label],
                full_name=edit_name,
                email=edit_email,
                role=edit_role,
                account_status=edit_status,
            )
            st.success("User updated.")
            st.rerun()
except Exception as exc:
    LOGGER.exception("User operation failed")
    show_error(exc)
