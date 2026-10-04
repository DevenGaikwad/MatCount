"""Role-scoped SQL-view reports and formula-safe CSV downloads."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from api.dependencies import current_actor
from api.serialization import success
from services import analytics_service
from services.exceptions import ValidationError
from services.rbac import Actor


REPORTS = {
    "v_inventory_detail": "Inventory detail",
    "v_component_stock_summary": "Component stock summary",
    "v_low_stock_components": "Low-stock components",
    "v_request_progress": "Request progress",
    "v_transfer_detail": "Transfer detail",
    "v_overdue_returns": "Overdue temporary returns",
    "v_disposal_summary": "Disposal summary",
}

router = APIRouter(prefix="/reports", tags=["Reports"])


def _validate_view(view_name: str) -> str:
    if view_name not in REPORTS:
        raise ValidationError("The selected report is not supported by SEMS.")
    return view_name


@router.get("")
def report_catalogue(actor: Actor = Depends(current_actor)):
    permitted = REPORTS
    if actor.role == "STUDENT":
        permitted = {
            name: label
            for name, label in REPORTS.items()
            if name in analytics_service.STUDENT_REPORT_VIEWS
        }
    return success(
        [{"view_name": name, "label": label} for name, label in permitted.items()]
    )


@router.get("/{view_name}")
def report(
    view_name: str,
    limit: int = Query(default=1000, ge=1, le=2000),
    actor: Actor = Depends(current_actor),
):
    return success(
        analytics_service.report_view(actor, _validate_view(view_name), limit=limit)
    )


@router.get("/{view_name}/csv")
def report_csv(
    view_name: str,
    limit: int = Query(default=2000, ge=1, le=2000),
    actor: Actor = Depends(current_actor),
):
    safe_name = _validate_view(view_name)
    rows = analytics_service.report_view(actor, safe_name, limit=limit)
    return Response(
        content=analytics_service.to_csv(rows),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}.csv"'},
    )

