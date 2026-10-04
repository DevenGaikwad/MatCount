"""Unit tests for UI-independent server-side RBAC."""

import pytest

from config.constants import AccountStatus, Role
from services.exceptions import AuthorizationError
from services.rbac import Actor, require_any_lab_scope, require_lab_scope, require_roles


def actor(role: Role, lab_id: int = 1, status: str = "ACTIVE") -> Actor:
    return Actor(1, "user@sems.local", "User", role.value, lab_id, status)


def test_administrator_can_cross_lab_scope() -> None:
    require_lab_scope(actor(Role.ADMINISTRATOR), 99)


def test_lab_assistant_is_restricted_to_assigned_lab() -> None:
    with pytest.raises(AuthorizationError):
        require_lab_scope(actor(Role.LAB_ASSISTANT, lab_id=1), 2)


def test_transfer_scope_allows_either_valid_side() -> None:
    require_any_lab_scope(actor(Role.LAB_ASSISTANT, lab_id=2), [1, 2])


def test_student_cannot_pass_administrator_role_check() -> None:
    with pytest.raises(AuthorizationError):
        require_roles(actor(Role.STUDENT), [Role.ADMINISTRATOR])


@pytest.mark.parametrize("status", [AccountStatus.INACTIVE.value, AccountStatus.SUSPENDED.value])
def test_nonactive_accounts_are_denied_writes(status: str) -> None:
    with pytest.raises(AuthorizationError):
        require_roles(actor(Role.ADMINISTRATOR, status=status), [Role.ADMINISTRATOR])

