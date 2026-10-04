"""Multi-line request creation, submission and review."""

import logging
from datetime import date, timedelta

import streamlit as st

from config.constants import RequestPriority, RequestStatus, Role
from services import master_data_service, request_service
from ui.components import data_table, page_header, section_heading, show_error
from ui.session import require_actor
from ui.theme import apply_theme


apply_theme()
actor = require_actor()
LOGGER = logging.getLogger(__name__)
page_header(
    "Component Requests",
    "Create, submit and review normalized multi-component laboratory requests",
)

try:
    requests = request_service.list_requests(actor)
    data_table(requests)

    section_heading("Inspect request")
    if requests:
        request_map = {
            f"{item.request_id} — {item.request_status} — {item.reason[:55]}": item
            for item in requests
        }
        inspect_label = st.selectbox("Request", list(request_map), key="inspect_request")
        inspected, inspected_items = request_service.get_request_with_items(
            actor, request_map[inspect_label].request_id
        )
        st.caption(
            f"Request {inspected.request_id} · {inspected.priority} · required {inspected.required_by_date}"
        )
        data_table(inspected_items)
    else:
        st.info("No requests are visible in your scope.")

    if actor.role in {
        Role.STUDENT.value,
        Role.FACULTY.value,
        Role.ADMINISTRATOR.value,
    }:
        section_heading("Create draft request")
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
        if not lab_options or not component_options:
            st.info("Create/assign a laboratory and add catalogue components first.")
        else:
            selected_components = st.multiselect(
                "Components (one line per selected component)", list(component_options)
            )
            quantities = {
                label: st.number_input(
                    f"Quantity — {label}", min_value=1, value=1, step=1, key=f"rq_{label}"
                )
                for label in selected_components
            }
            with st.form("create_request"):
                lab_label = st.selectbox("Requesting laboratory", list(lab_options))
                request_date_value = st.date_input("Request date", date.today())
                required_date = st.date_input(
                    "Required by", date.today() + timedelta(days=7)
                )
                priority = st.selectbox(
                    "Priority", [item.value for item in RequestPriority], index=1
                )
                reason = st.text_area("Reason")
                create = st.form_submit_button("Create DRAFT request", type="primary")
            if create:
                request_service.create_draft(
                    actor,
                    requesting_lab_id=lab_options[lab_label],
                    request_date=request_date_value,
                    required_by_date=required_date,
                    priority=priority,
                    reason=reason,
                    items=[
                        {
                            "component_id": component_options[label],
                            "quantity_requested": int(quantities[label]),
                        }
                        for label in selected_components
                    ],
                )
                st.success("DRAFT request created.")
                st.rerun()

        drafts = [
            item
            for item in requests
            if item.request_status == RequestStatus.DRAFT.value
            and (item.created_by == actor.user_id or actor.role == Role.ADMINISTRATOR.value)
        ]
        if drafts:
            section_heading("Submit draft")
            draft_options = {
                f"{item.request_id} — {item.reason[:70]}": item.request_id for item in drafts
            }
            with st.form("submit_request"):
                draft_label = st.selectbox("Draft request", list(draft_options))
                submit = st.form_submit_button("Submit for review")
            if submit:
                request_service.submit_request(actor, draft_options[draft_label])
                st.success("Request submitted.")
                st.rerun()

        cancellable = [
            item
            for item in requests
            if item.request_status
            in {RequestStatus.DRAFT.value, RequestStatus.SUBMITTED.value}
            and (item.created_by == actor.user_id or actor.role == Role.ADMINISTRATOR.value)
        ]
        section_heading("Cancel before approval")
        if cancellable:
            cancel_options = {
                f"{item.request_id} — {item.request_status} — {item.reason[:55]}": item.request_id
                for item in cancellable
            }
            with st.form("cancel_request"):
                cancel_label = st.selectbox("Request", list(cancel_options))
                confirmed = st.checkbox("I confirm this request cancellation")
                cancel = st.form_submit_button("Cancel request")
            if cancel:
                if not confirmed:
                    st.error("Confirmation is required.")
                else:
                    request_service.cancel_request(
                        actor, cancel_options[cancel_label]
                    )
                    st.success("Request cancelled before approval/allocation.")
                    st.rerun()
        else:
            st.info("No DRAFT or SUBMITTED request is eligible for cancellation.")

    if actor.role in {Role.FACULTY.value, Role.ADMINISTRATOR.value}:
        reviewable = [
            item
            for item in requests
            if item.request_status
            in {
                RequestStatus.SUBMITTED.value,
                RequestStatus.PARTIALLY_APPROVED.value,
            }
        ]
        section_heading("Faculty review")
        if not reviewable:
            st.info("No request is awaiting review.")
        else:
            review_options = {
                f"{item.request_id} — {item.priority} — {item.reason[:60]}": item.request_id
                for item in reviewable
            }
            review_label = st.selectbox("Request to review", list(review_options))
            _, items = request_service.get_request_with_items(
                actor, review_options[review_label]
            )
            reviews = {}
            with st.form("review_request"):
                for item in items:
                    st.markdown(f"**Request item {item.request_item_id} · Component {item.component_id}**")
                    approved = st.number_input(
                        "Approved quantity",
                        min_value=0,
                        max_value=int(item.quantity_requested),
                        value=int(item.quantity_approved),
                        step=1,
                        key=f"approved_{item.request_item_id}",
                    )
                    remarks = st.text_input(
                        "Remarks",
                        value=item.remarks or "",
                        key=f"remarks_{item.request_item_id}",
                    )
                    reviews[item.request_item_id] = {
                        "quantity_approved": int(approved),
                        "remarks": remarks,
                    }
                review = st.form_submit_button("Commit review", type="primary")
            if review:
                request_service.review_request(
                    actor, review_options[review_label], reviews
                )
                st.success("Request review committed atomically.")
                st.rerun()
except Exception as exc:
    LOGGER.exception("Request operation failed")
    show_error(exc)
