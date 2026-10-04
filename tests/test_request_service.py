"""Focused request workflow tests with an isolated fake transaction."""

from contextlib import contextmanager
from types import SimpleNamespace

import pytest

from config.constants import RequestStatus, Role
from services import request_service
from services.exceptions import StateTransitionError
from services.rbac import Actor


pytestmark = pytest.mark.unit


class FakeSession:
    def __init__(self) -> None:
        self.flushed = False

    def flush(self) -> None:
        self.flushed = True


def student() -> Actor:
    return Actor(4, "student@sems.local", "Student", Role.STUDENT.value, 2)


def install_request_fakes(
    monkeypatch: pytest.MonkeyPatch, request: SimpleNamespace
) -> FakeSession:
    session = FakeSession()

    @contextmanager
    def fake_scope():
        yield session

    monkeypatch.setattr(request_service, "session_scope", fake_scope)
    monkeypatch.setattr(request_service, "revalidate_actor", lambda *args: None)
    monkeypatch.setattr(
        request_service.request_repository,
        "get_request",
        lambda *args, **kwargs: request,
    )
    return session


def test_creator_can_cancel_submitted_request_before_approval(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request = SimpleNamespace(
        request_status=RequestStatus.SUBMITTED.value,
        created_by=4,
        requesting_lab_id=2,
    )
    session = install_request_fakes(monkeypatch, request)
    result = request_service.cancel_request(student(), 9)
    assert result.request_status == RequestStatus.CANCELLED.value
    assert session.flushed


def test_approved_request_cannot_move_back_to_cancelled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request = SimpleNamespace(
        request_status=RequestStatus.APPROVED.value,
        created_by=4,
        requesting_lab_id=2,
    )
    install_request_fakes(monkeypatch, request)
    with pytest.raises(StateTransitionError):
        request_service.cancel_request(student(), 9)
