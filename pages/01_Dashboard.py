"""Role-scoped SEMS dashboard."""

import logging

import pandas as pd
import plotly.express as px
import streamlit as st

from config.constants import Role
from services import analytics_service
from ui.components import kpi_cards, page_header, section_heading, show_error
from ui.session import require_actor
from ui.theme import apply_theme


apply_theme()
actor = require_actor()
LOGGER = logging.getLogger(__name__)
page_header("SEMS Dashboard", "Live operational summary from the shared MySQL database")

try:
    data = analytics_service.dashboard(actor)
    kpis = data["kpis"]
    cards = [
        ("Laboratories", kpis["laboratory_count"]),
        ("Users", kpis["user_count"]),
        ("Components", kpis["component_count"]),
        ("Inventory Positions", kpis["inventory_row_count"]),
        ("Available Stock", kpis["total_available_stock"]),
        ("Reserved Stock", kpis["total_reserved_stock"]),
        ("On-Hand Valuation", kpis["inventory_valuation"]),
        ("Low-Stock Items", kpis["low_stock_count"]),
        ("Open Requests", kpis["open_request_count"]),
    ]
    if actor.role != Role.STUDENT.value:
        cards.extend(
            [
                ("Active Transfers", kpis["active_transfer_count"]),
                ("Overdue Returns", kpis["overdue_return_count"]),
                ("Disposed Quantity", kpis["disposed_quantity"]),
            ]
        )
    kpi_cards(cards)

    section_heading("Stock by laboratory")
    stock = pd.DataFrame(data["stock_by_lab"])
    if stock.empty:
        st.info("No inventory data is available.")
    else:
        figure = px.bar(
            stock,
            x="lab_name",
            y=["quantity_available", "quantity_reserved"],
            barmode="group",
            color_discrete_sequence=["#F36B00", "#85000F"],
            labels={"value": "Quantity", "lab_name": "Laboratory", "variable": "Stock"},
        )
        figure.update_layout(legend_title_text="", margin=dict(l=10, r=10, t=25, b=10))
        st.plotly_chart(figure, use_container_width=True)

    section_heading("Request status distribution")
    requests = pd.DataFrame(data["request_status"])
    if requests.empty:
        st.info("No component requests are available.")
    else:
        figure = px.pie(
            requests,
            names="request_status",
            values="request_count",
            color_discrete_sequence=px.colors.sequential.Oranges_r,
            hole=0.48,
        )
        figure.update_layout(margin=dict(l=10, r=10, t=25, b=10))
        st.plotly_chart(figure, use_container_width=True)
except Exception as exc:
    LOGGER.exception("Dashboard load failed")
    show_error(exc)
