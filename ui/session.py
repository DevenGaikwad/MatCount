"""Streamlit session identity and page-level authorization."""

from __future__ import annotations

import streamlit as st

from config.constants import Role
from services.rbac import Actor


ACTOR_KEY = "sems_actor"


def current_actor() -> Actor | None:
    value = st.session_state.get(ACTOR_KEY)
    if not isinstance(value, dict):
        return None
    try:
        return Actor.from_session_dict(value)
    except (KeyError, TypeError, ValueError):
        st.session_state.pop(ACTOR_KEY, None)
        return None


def set_actor(actor: Actor) -> None:
    st.session_state[ACTOR_KEY] = actor.to_session_dict()


def clear_actor() -> None:
    st.session_state.pop(ACTOR_KEY, None)


def require_actor(*roles: str | Role) -> Actor:
    actor = current_actor()
    if actor is None:
        st.error("Please sign in from the SEMS home page.")
        st.stop()
    if roles and actor.role not in {str(role) for role in roles}:
        st.error("Your role is not authorized to open this page.")
        st.stop()
    return actor
