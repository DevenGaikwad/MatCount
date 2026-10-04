"""Server-side information-minimization and financial-field policy tests."""

from __future__ import annotations

from contextlib import contextmanager

import pytest

from config.constants import Role
from services import analytics_service
from services.data_policy import (
    FINANCIAL_FIELDS,
    has_financial_visibility,
    project_availability_rows,
    redact_financial_rows,
)
from services.rbac import Actor


pytestmark = pytest.mark.unit


def actor(role: Role, *, lab_id: int = 1) -> Actor:
    return Actor(
        user_id=17,
        email="policy-user@example.invalid",
        full_name="Policy User",
        role=role.value,
        lab_id=lab_id,
    )


RAW_FINANCIAL_ROW = {
    "inventory_id": 9,
    "lab_id": 1,
    "lab_name": "VLSI Laboratory",
    "component_id": 4,
    "component_name": "Operational Amplifier",
    "part_number": "LM358",
    "category_name": "Integrated Circuits",
    "storage_location_id": 7,
    "cabinet_no": "C-01",
    "shelf_no": "S-02",
    "drawer_no": "D-03",
    "quantity_available": 18,
    "quantity_reserved": 2,
    "quantity_accounted": 20,
    "unit_cost": 12.5,
    "available_value": 225.0,
    "inventory_value": 250.0,
    "inventory_status": "AVAILABLE",
}


def test_financial_policy_is_explicit_by_role() -> None:
    assert has_financial_visibility(actor(Role.ADMINISTRATOR))
    assert has_financial_visibility(actor(Role.LAB_ASSISTANT))
    assert not has_financial_visibility(actor(Role.FACULTY))
    assert not has_financial_visibility(actor(Role.STUDENT))


@pytest.mark.parametrize("role", [Role.STUDENT, Role.FACULTY])
def test_unauthorized_roles_never_receive_financial_fields(role: Role) -> None:
    [row] = redact_financial_rows(actor(role), [RAW_FINANCIAL_ROW])
    assert FINANCIAL_FIELDS.isdisjoint(row)
    assert row["quantity_available"] == 18


def test_student_availability_is_minimized_beyond_cosmetic_column_hiding() -> None:
    [row] = project_availability_rows(actor(Role.STUDENT), [RAW_FINANCIAL_ROW])
    assert FINANCIAL_FIELDS.isdisjoint(row)
    assert "storage_location_id" not in row
    assert "cabinet_no" not in row
    assert "quantity_reserved" not in row
    assert row["component_name"] == "Operational Amplifier"
    assert row["quantity_available"] == 18


def test_lab_assistant_keeps_operational_cost_fields() -> None:
    [row] = project_availability_rows(actor(Role.LAB_ASSISTANT), [RAW_FINANCIAL_ROW])
    assert row["unit_cost"] == 12.5
    assert row["inventory_value"] == 250.0


def test_report_service_redacts_before_csv_export(monkeypatch: pytest.MonkeyPatch) -> None:
    @contextmanager
    def session_scope():
        yield object()

    monkeypatch.setattr(analytics_service, "session_scope", session_scope)
    monkeypatch.setattr(analytics_service, "revalidate_actor", lambda *_: None)
    monkeypatch.setattr(
        analytics_service.report_repository,
        "fetch_view",
        lambda *_args, **_kwargs: [RAW_FINANCIAL_ROW],
    )

    rows = analytics_service.report_view(
        actor(Role.STUDENT), "v_inventory_detail"
    )
    csv_text = analytics_service.to_csv(rows).decode("utf-8")
    assert FINANCIAL_FIELDS.isdisjoint(rows[0])
    assert "unit_cost" not in csv_text
    assert "inventory_value" not in csv_text


def test_student_dashboard_omits_valuation(monkeypatch: pytest.MonkeyPatch) -> None:
    @contextmanager
    def session_scope():
        yield object()

    monkeypatch.setattr(analytics_service, "session_scope", session_scope)
    monkeypatch.setattr(analytics_service, "revalidate_actor", lambda *_: None)
    monkeypatch.setattr(
        analytics_service.report_repository,
        "dashboard_kpis",
        lambda *_args, **_kwargs: {
            "component_count": 12,
            "inventory_valuation": 9999.0,
        },
    )
    monkeypatch.setattr(
        analytics_service.report_repository,
        "stock_by_lab",
        lambda *_args, **_kwargs: [
            {
                "lab_id": 1,
                "lab_name": "VLSI Laboratory",
                "quantity_available": 18,
                "inventory_value": 9999.0,
            }
        ],
    )
    monkeypatch.setattr(
        analytics_service.report_repository,
        "request_status_distribution",
        lambda *_args, **_kwargs: [],
    )

    payload = analytics_service.dashboard(actor(Role.STUDENT))
    assert "inventory_valuation" not in payload["kpis"]
    assert "inventory_value" not in payload["stock_by_lab"][0]

