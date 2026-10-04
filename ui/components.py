"""Reusable presentation helpers; contains no SQL or business decisions."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from decimal import Decimal
from html import escape
from typing import Any

import pandas as pd
import streamlit as st

from services.exceptions import SemsError
from services.analytics_service import to_csv


def page_header(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="sems-header"><h1>{escape(title)}</h1>'
        f'<p>{escape(subtitle)}</p></div>',
        unsafe_allow_html=True,
    )


def section_heading(title: str) -> None:
    st.markdown(
        f'<h3 class="sems-section">{escape(title)}</h3>', unsafe_allow_html=True
    )


def status_badge(status: str) -> None:
    st.markdown(
        f'<span class="sems-badge">{escape(status.replace("_", " "))}</span>',
        unsafe_allow_html=True,
    )


def kpi_cards(items: list[tuple[str, Any]]) -> None:
    columns = st.columns(min(4, max(1, len(items))))
    for index, (label, value) in enumerate(items):
        with columns[index % len(columns)]:
            if isinstance(value, Decimal):
                display = f"₹{value:,.2f}"
            elif isinstance(value, float):
                display = f"{value:,.2f}"
            elif isinstance(value, int):
                display = f"{value:,}"
            else:
                display = str(value)
            st.markdown(
                f'<div class="sems-kpi"><div class="sems-kpi-label">{label}</div>'
                f'<div class="sems-kpi-value">{display}</div></div>',
                unsafe_allow_html=True,
            )


def record_to_dict(record: Any) -> dict[str, Any]:
    if isinstance(record, Mapping):
        return dict(record)
    table = getattr(record, "__table__", None)
    if table is not None:
        return {column.name: getattr(record, column.name) for column in table.columns}
    return dict(vars(record))


def records_frame(records: Iterable[Any]) -> pd.DataFrame:
    return pd.DataFrame([record_to_dict(record) for record in records])


def data_table(records: Iterable[Any], *, empty_message: str = "No records found.") -> pd.DataFrame:
    frame = records_frame(records)
    if frame.empty:
        st.info(empty_message)
    else:
        st.dataframe(frame, use_container_width=True, hide_index=True)
    return frame


def show_error(exc: Exception) -> None:
    if isinstance(exc, SemsError):
        st.error(str(exc))
    else:
        st.error("The operation could not be completed. Check the application log.")


def csv_download(frame: pd.DataFrame, *, filename: str, label: str = "Download CSV") -> None:
    st.download_button(
        label,
        data=to_csv(frame),
        file_name=filename,
        mime="text/csv",
        disabled=frame.empty,
    )
