"""Service-level RBAC and stale-session regression tests."""

from types import SimpleNamespace

import pytest

from config.constants import AccountStatus, Role
from services import inventory_service, master_data_service, request_service, transfer_service
from services.exceptions import AuthorizationError
from services.rbac import Actor, revalidate_actor


pytestmark = pytest.mark.unit


def actor(role: Role, *, lab_id: int = 1) -> Actor:
    return Actor(
        user_id=7,
        email="actor@sems.local",
        full_name="Actor",
        role=role.value,
        lab_id=lab_id,
    )


def test_student_cannot_bypass_transfer_read_service() -> None:
    with pytest.raises(AuthorizationError):
        transfer_service.list_transfers(actor(Role.STUDENT))


def test_student_cannot_open_raw_inventory_positions() -> None:
    with pytest.raises(AuthorizationError):
        inventory_service.list_inventory(actor(Role.STUDENT))


def test_non_administrator_cannot_enumerate_user_private_data() -> None:
    with pytest.raises(AuthorizationError):
        master_data_service.list_users(actor(Role.STUDENT))


def test_faculty_cannot_enumerate_storage_coordinates() -> None:
    with pytest.raises(AuthorizationError):
        master_data_service.list_locations(actor(Role.FACULTY))


def test_faculty_cannot_approve_or_cancel_transfer() -> None:
    with pytest.raises(AuthorizationError):
        transfer_service.approve_transfer(actor(Role.FACULTY), 1)
    with pytest.raises(AuthorizationError):
        transfer_service.cancel_transfer(actor(Role.FACULTY), 1)


def test_only_operational_roles_can_open_cross_lab_transfer_plan_lines() -> None:
    with pytest.raises(AuthorizationError):
        request_service.get_approved_for_transfer_with_items(
            actor(Role.FACULTY), 1
        )


def test_database_revalidation_rejects_role_change(monkeypatch: pytest.MonkeyPatch) -> None:
    record = SimpleNamespace(
        email="actor@sems.local",
        role=Role.ADMINISTRATOR.value,
        lab_id=1,
        account_status=AccountStatus.ACTIVE.value,
    )
    monkeypatch.setattr(
        "services.rbac.user_repository.get_user", lambda session, user_id: record
    )
    with pytest.raises(AuthorizationError, match="changed"):
        revalidate_actor(object(), actor(Role.FACULTY))


def test_database_revalidation_rejects_suspended_account(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    record = SimpleNamespace(
        email="actor@sems.local",
        role=Role.FACULTY.value,
        lab_id=1,
        account_status=AccountStatus.SUSPENDED.value,
    )
    monkeypatch.setattr(
        "services.rbac.user_repository.get_user", lambda session, user_id: record
    )
    with pytest.raises(AuthorizationError, match="no longer active"):
        revalidate_actor(object(), actor(Role.FACULTY))
