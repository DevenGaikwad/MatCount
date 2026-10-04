"""Read-only, correctly grained dashboard and CSV-report service."""

from __future__ import annotations

from io import StringIO
from typing import Any, Iterable, Mapping

import pandas as pd

from config.constants import Role
from db.session import session_scope
from repositories import report_repository
from services.data_policy import (
    project_availability_rows,
    redact_financial_row,
    redact_financial_rows,
)
from services.exceptions import AuthorizationError
from services.rbac import Actor, revalidate_actor, require_active


FORMULA_PREFIXES = ("=", "+", "-", "@")
STUDENT_REPORT_VIEWS = {
    "v_inventory_detail",
    "v_component_stock_summary",
    "v_low_stock_components",
    "v_request_progress",
}


def _scope(actor: Actor) -> int | None:
    require_active(actor)
    return None if actor.role == Role.ADMINISTRATOR.value else actor.lab_id


def dashboard(actor: Actor) -> dict[str, Any]:
    lab_id = _scope(actor)
    created_by = actor.user_id if actor.role == Role.STUDENT.value else None
    with session_scope() as session:
        revalidate_actor(session, actor)
        return {
            "kpis": redact_financial_row(
                actor,
                report_repository.dashboard_kpis(
                    session, lab_id, created_by=created_by
                ),
            ),
            "stock_by_lab": redact_financial_rows(
                actor, report_repository.stock_by_lab(session, lab_id)
            ),
            "request_status": [
                dict(row)
                for row in report_repository.request_status_distribution(
                    session, lab_id, created_by=created_by
                )
            ],
        }


def report_view(actor: Actor, view_name: str, *, limit: int = 2000):
    lab_id = _scope(actor)
    if actor.role == Role.STUDENT.value and view_name not in STUDENT_REPORT_VIEWS:
        raise AuthorizationError("Students may open only inventory and own-request reports.")
    created_by = (
        actor.user_id
        if actor.role == Role.STUDENT.value and view_name == "v_request_progress"
        else None
    )
    with session_scope() as session:
        revalidate_actor(session, actor)
        return redact_financial_rows(
            actor,
            report_repository.fetch_view(
                session,
                view_name,
                lab_id=lab_id,
                created_by=created_by,
                limit=limit,
            ),
        )


def availability_view(actor: Actor, *, limit: int = 2000):
    require_active(actor)
    lab_id = actor.lab_id if actor.role == Role.LAB_ASSISTANT.value else None
    with session_scope() as session:
        revalidate_actor(session, actor)
        return project_availability_rows(
            actor,
            report_repository.fetch_view(
                session, "v_inventory_detail", lab_id=lab_id, limit=limit
            ),
        )


def transfer_detail_view(actor: Actor, transfer_id: int):
    """Return enriched lines for one transfer while preserving actor lab scope."""

    lab_id = _scope(actor)
    with session_scope() as session:
        revalidate_actor(session, actor)
        return redact_financial_rows(
            actor,
            report_repository.fetch_transfer_detail(
                session, transfer_id, lab_id=lab_id
            ),
        )


def _safe_spreadsheet_cell(value: Any) -> Any:
    if isinstance(value, str) and value.lstrip().startswith(FORMULA_PREFIXES):
        return "'" + value
    return value


def to_csv(rows: pd.DataFrame | Iterable[Mapping[str, Any]]) -> bytes:
    """Create UTF-8 CSV while neutralizing formula-like text cells."""

    frame = rows.copy() if isinstance(rows, pd.DataFrame) else pd.DataFrame(list(rows))
    for column in frame.columns:
        frame[column] = frame[column].map(_safe_spreadsheet_cell)
    output = StringIO()
    frame.to_csv(output, index=False)
    return output.getvalue().encode("utf-8")
