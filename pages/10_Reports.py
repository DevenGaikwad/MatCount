"""Role-scoped SQL-view reports with mandatory CSV export."""

import logging

import pandas as pd
import plotly.express as px
import streamlit as st

from config.constants import Role
from services import analytics_service
from ui.components import csv_download, data_table, page_header, section_heading, show_error
from ui.session import require_actor
from ui.theme import apply_theme


apply_theme()
actor = require_actor()
LOGGER = logging.getLogger(__name__)
page_header("Reports and Analytics", "Read-only SQL views, correctly grained tables and CSV exports")

REPORTS = {
    "Inventory detail": "v_inventory_detail",
    "Component stock summary": "v_component_stock_summary",
    "Low-stock components": "v_low_stock_components",
    "Request progress": "v_request_progress",
    "Transfer detail": "v_transfer_detail",
    "Overdue temporary returns": "v_overdue_returns",
    "Disposal summary": "v_disposal_summary",
}

try:
    visible_reports = REPORTS
    if actor.role == Role.STUDENT.value:
        visible_reports = {
            label: view
            for label, view in REPORTS.items()
            if view in analytics_service.STUDENT_REPORT_VIEWS
        }
    selected_label = st.selectbox("Report", list(visible_reports))
    view_name = visible_reports[selected_label]
    rows = analytics_service.report_view(actor, view_name)
    frame = data_table(rows)
    csv_download(frame, filename=f"{view_name}.csv")

    section_heading("Focused visualization")
    if frame.empty:
        st.info("The selected report has no data to visualize.")
    elif view_name == "v_component_stock_summary":
        figure = px.bar(
            frame,
            x="component_name",
            y=["quantity_available", "quantity_reserved"],
            barmode="group",
            color_discrete_sequence=["#F36B00", "#85000F"],
        )
        st.plotly_chart(figure, use_container_width=True)
    elif view_name == "v_low_stock_components":
        figure = px.bar(
            frame,
            x="component_name",
            y="shortage_quantity",
            color="lab_name",
            color_discrete_sequence=px.colors.sequential.Oranges,
        )
        st.plotly_chart(figure, use_container_width=True)
    elif view_name == "v_overdue_returns":
        figure = px.bar(
            frame,
            x="component_name",
            y="days_overdue",
            color="destination_lab_name",
            color_discrete_sequence=px.colors.sequential.Oranges,
        )
        st.plotly_chart(figure, use_container_width=True)
    elif view_name == "v_disposal_summary":
        grouped = (
            frame.groupby("disposal_reason", as_index=False)["quantity_disposed"].sum()
        )
        figure = px.pie(
            grouped,
            names="disposal_reason",
            values="quantity_disposed",
            color_discrete_sequence=px.colors.sequential.Oranges_r,
        )
        st.plotly_chart(figure, use_container_width=True)
    else:
        st.caption("This report is clearer as a detailed table; no decorative chart is added.")
except Exception as exc:
    LOGGER.exception("Report operation failed")
    show_error(exc)
