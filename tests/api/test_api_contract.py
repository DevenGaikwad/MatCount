"""HTTP-boundary regression tests for the thin FastAPI adapter."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from api.dependencies import current_actor
from api.main import app
from api.session_store import SESSION_STORE
from config.constants import Role
from services.exceptions import AuthorizationError
from services.rbac import Actor


pytestmark = pytest.mark.api


@pytest.fixture
def administrator() -> Actor:
    return Actor(
        user_id=9,
        email="administrator@example.invalid",
        full_name="API Administrator",
        role=Role.ADMINISTRATOR.value,
        lab_id=1,
    )


@pytest.fixture
def authenticated_client(administrator: Actor):
    app.dependency_overrides[current_actor] = lambda: administrator
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client
    app.dependency_overrides.clear()
    SESSION_STORE.clear()


@pytest.fixture
def student() -> Actor:
    return Actor(
        user_id=10,
        email="student@example.invalid",
        full_name="API Student",
        role=Role.STUDENT.value,
        lab_id=1,
    )


def test_protected_endpoint_requires_bearer_session() -> None:
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/api/reports")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"


def test_health_response_is_sanitized(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "api.routes.system.health_status",
        lambda: SimpleNamespace(
            ok=True,
            database_name="sems_db",
            server_version="8.4.11",
            message="Database connection is healthy.",
        ),
    )
    with TestClient(app) as client:
        payload = client.get("/api/health").json()["data"]
    assert payload["api"] == "online"
    assert payload["database"]["name"] == "sems_db"
    assert "password" not in str(payload).lower()


def test_login_returns_opaque_session_without_credential_material(
    monkeypatch: pytest.MonkeyPatch, administrator: Actor
) -> None:
    monkeypatch.setattr("api.routes.auth.authenticate", lambda email, password: administrator)
    with TestClient(app) as client:
        response = client.post(
            "/api/auth/login",
            json={"email": administrator.email, "password": "temporary-demo-value"},
        )
    SESSION_STORE.clear()
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) >= 32
    assert "password" not in str(data).lower()
    assert "hash" not in str(data).lower()


def test_dashboard_route_delegates_to_service(
    monkeypatch: pytest.MonkeyPatch, authenticated_client: TestClient
) -> None:
    monkeypatch.setattr(
        "api.routes.dashboard.analytics_service.dashboard",
        lambda actor: {"kpis": {"component_count": 12}, "stock_by_lab": [], "request_status": []},
    )
    response = authenticated_client.get("/api/dashboard")
    assert response.status_code == 200
    assert response.json()["data"]["kpis"]["component_count"] == 12


def test_student_inventory_api_contains_no_financial_or_storage_fields(
    monkeypatch: pytest.MonkeyPatch, student: Actor
) -> None:
    from services.data_policy import project_availability_rows

    raw = {
        "inventory_id": 4,
        "lab_id": 1,
        "lab_name": "Embedded Systems Laboratory",
        "component_name": "Microcontroller",
        "quantity_available": 8,
        "quantity_reserved": 2,
        "cabinet_no": "C-01",
        "unit_cost": 320.0,
        "inventory_value": 3200.0,
        "inventory_status": "AVAILABLE",
    }
    app.dependency_overrides[current_actor] = lambda: student
    monkeypatch.setattr(
        "api.routes.inventory.analytics_service.availability_view",
        lambda actor, limit: project_availability_rows(actor, [raw]),
    )
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/api/inventory")
    app.dependency_overrides.clear()
    row = response.json()["data"][0]
    assert response.status_code == 200
    assert "unit_cost" not in row
    assert "inventory_value" not in row
    assert "cabinet_no" not in row
    assert "quantity_reserved" not in row


@pytest.mark.parametrize(
    "path",
    [
        "/api/inventory/positions",
        "/api/users",
        "/api/storage-locations",
        "/api/transfers",
        "/api/disposals",
    ],
)
def test_student_cannot_bypass_navigation_with_direct_api_calls(
    path: str, student: Actor
) -> None:
    app.dependency_overrides[current_actor] = lambda: student
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get(path)
    app.dependency_overrides.clear()
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "PERMISSION_DENIED"


def test_student_cannot_request_an_unapproved_report_view(student: Actor) -> None:
    app.dependency_overrides[current_actor] = lambda: student
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/api/reports/v_disposal_summary")
    app.dependency_overrides.clear()
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "PERMISSION_DENIED"


def test_transfer_detail_prefers_enriched_service_view(
    monkeypatch: pytest.MonkeyPatch, authenticated_client: TestClient
) -> None:
    monkeypatch.setattr(
        "api.routes.transfers.transfer_service.get_transfer_with_items",
        lambda actor, transfer_id: (
            {"transfer_id": transfer_id, "transfer_status": "DISPATCHED"},
            [{"transfer_item_id": 4, "inventory_id": 8}],
        ),
    )
    monkeypatch.setattr(
        "api.routes.transfers.analytics_service.transfer_detail_view",
        lambda actor, transfer_id: [
            {
                "transfer_id": transfer_id,
                "transfer_item_id": 4,
                "inventory_id": 8,
                "component_id": 3,
                "component_name": "Operational Amplifier",
            }
        ],
    )
    response = authenticated_client.get("/api/transfers/2")
    assert response.status_code == 200
    assert response.json()["data"]["items"][0]["component_name"] == "Operational Amplifier"


def test_transfer_plan_endpoint_uses_narrow_approved_request_service(
    monkeypatch: pytest.MonkeyPatch, authenticated_client: TestClient
) -> None:
    monkeypatch.setattr(
        "api.routes.requests.request_service.get_approved_for_transfer_with_items",
        lambda actor, request_id: (
            {"request_id": request_id, "request_status": "APPROVED"},
            [
                {
                    "request_item_id": 7,
                    "component_id": 3,
                    "quantity_requested": 8,
                    "quantity_approved": 5,
                }
            ],
        ),
    )
    response = authenticated_client.get("/api/requests/3/transfer-plan")
    assert response.status_code == 200
    assert response.json()["data"]["items"][0]["quantity_approved"] == 5


def test_domain_authorization_is_mapped_to_403(
    monkeypatch: pytest.MonkeyPatch, authenticated_client: TestClient
) -> None:
    def deny(*_args, **_kwargs):
        raise AuthorizationError("Administrator role required.")

    monkeypatch.setattr("api.routes.disposals.disposal_service.list_disposals", deny)
    response = authenticated_client.get("/api/disposals")
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "PERMISSION_DENIED"


def test_request_validation_uses_safe_field_errors(
    authenticated_client: TestClient,
) -> None:
    response = authenticated_client.post(
        "/api/disposals",
        json={
            "inventory_id": 1,
            "quantity_disposed": 0,
            "disposal_date": "not-a-date",
            "disposal_reason": "",
            "disposal_method": "",
        },
    )
    assert response.status_code == 422
    payload = response.json()["error"]
    assert payload["code"] == "INVALID_REQUEST"
    assert payload["details"]
