"""SEMS Streamlit entry point and role-aware navigation shell."""

from __future__ import annotations

import logging

import streamlit as st

from config.constants import Role
from config.logging_config import configure_logging
from db.healthcheck import check_database
from services.auth_service import authenticate, validate_session_actor
from services.exceptions import AuthenticationError, AuthorizationError
from ui.components import page_header, show_error
from ui.session import clear_actor, current_actor, set_actor
from ui.theme import apply_theme


st.set_page_config(
    page_title="SEMS",
    page_icon="🧰",
    layout="wide",
    initial_sidebar_state="expanded",
)
configure_logging()
apply_theme()
LOGGER = logging.getLogger(__name__)


def login_page() -> None:
    page_header(
        "Smart Electronics Management System",
        "Centralized electronic component and laboratory asset management",
    )
    health = check_database()
    if health.ok:
        st.success(
            f"Connected to {health.database_name} on MySQL {health.server_version}."
        )
    else:
        st.warning(
            f"{health.message} Complete the setup guide before signing in."
        )

    left, center, right = st.columns([1, 1.25, 1])
    with center:
        with st.form("login_form"):
            st.subheader("Demonstration login")
            email = st.text_input("Email", placeholder="admin@sems.local")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button(
                "Sign in", type="primary", use_container_width=True
            )
        if submitted:
            if not health.ok:
                st.error("Database connectivity must be restored before login.")
                return
            try:
                set_actor(authenticate(email, password))
                st.rerun()
            except AuthenticationError as exc:
                LOGGER.warning("Demonstration login rejected")
                show_error(exc)
            except Exception as exc:
                LOGGER.exception("Login failed")
                show_error(exc)


actor = current_actor()
if actor is None:
    login_page()
    st.stop()

try:
    validate_session_actor(actor)
except AuthorizationError as exc:
    clear_actor()
    st.warning(str(exc))
    st.stop()
except Exception as exc:
    LOGGER.warning("Active-session database validation failed: %s", exc.__class__.__name__)
    st.error("SEMS cannot validate this session while the database is unavailable.")
    st.stop()

with st.sidebar:
    st.markdown("### SEMS")
    st.caption(actor.full_name)
    st.caption(f"{actor.role.replace('_', ' ').title()} · Lab {actor.lab_id}")
    if st.button("Log out", use_container_width=True):
        clear_actor()
        st.rerun()

pages: list[st.Page] = [
    st.Page("pages/01_Dashboard.py", title="Dashboard", icon="📊"),
    st.Page("pages/04_Component_Catalogue.py", title="Component Catalogue", icon="🔧"),
    st.Page("pages/06_Inventory.py", title="Inventory", icon="📦"),
    st.Page("pages/07_Component_Requests.py", title="Component Requests", icon="📝"),
    st.Page("pages/10_Reports.py", title="Reports", icon="📈"),
]

if actor.role == Role.ADMINISTRATOR.value:
    pages[1:1] = [
        st.Page("pages/02_Laboratories.py", title="Laboratories", icon="🏫"),
        st.Page("pages/03_Users.py", title="Users", icon="👥"),
    ]
    pages.insert(4, st.Page("pages/05_Storage_Locations.py", title="Storage Locations", icon="🗄️"))
    pages.insert(-1, st.Page("pages/08_Transfers.py", title="Inter-Lab Transfers", icon="🔄"))
    pages.insert(-1, st.Page("pages/09_Disposal.py", title="Disposal", icon="♻️"))
elif actor.role == Role.LAB_ASSISTANT.value:
    pages.insert(2, st.Page("pages/05_Storage_Locations.py", title="Storage Locations", icon="🗄️"))
    pages.insert(-1, st.Page("pages/08_Transfers.py", title="Inter-Lab Transfers", icon="🔄"))
elif actor.role == Role.FACULTY.value:
    pages.insert(-1, st.Page("pages/08_Transfers.py", title="Inter-Lab Transfers", icon="🔄"))

navigation = st.navigation(pages, position="sidebar")
navigation.run()
