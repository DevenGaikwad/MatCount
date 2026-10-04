"""Storage-coordinate edge cases required by the frozen nullable schema."""

from contextlib import contextmanager
from types import SimpleNamespace

import pytest

from config.constants import Role
from services import master_data_service
from services.exceptions import ValidationError
from services.rbac import Actor


pytestmark = pytest.mark.unit


class FakeSession:
    pass


def assistant() -> Actor:
    return Actor(3, "assistant@sems.local", "Assistant", Role.LAB_ASSISTANT.value, 1)


def install_location_fakes(monkeypatch: pytest.MonkeyPatch):
    captured: dict[str, object] = {}

    @contextmanager
    def fake_scope():
        yield FakeSession()

    monkeypatch.setattr(master_data_service, "session_scope", fake_scope)
    monkeypatch.setattr(master_data_service, "revalidate_actor", lambda *args: None)
    monkeypatch.setattr(
        master_data_service.lab_repository,
        "get_lab",
        lambda *args: SimpleNamespace(lab_id=1),
    )

    def find(*args, **kwargs):
        captured.update(kwargs)
        return None

    monkeypatch.setattr(
        master_data_service.lab_repository, "find_null_normalized_location", find
    )
    monkeypatch.setattr(
        master_data_service.lab_repository,
        "create_location",
        lambda session, **kwargs: SimpleNamespace(**kwargs),
    )
    return captured


def test_blank_shelf_and_drawer_are_normalized_to_null(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured = install_location_fakes(monkeypatch)
    master_data_service.create_location(
        assistant(),
        lab_id=1,
        cabinet_no=" C-A1 ",
        shelf_no="   ",
        drawer_no="",
        location_type=" cabinet ",
    )
    assert captured["cabinet_no"] == "C-A1"
    assert captured["shelf_no"] is None
    assert captured["drawer_no"] is None
    assert captured["location_type"] == "CABINET"


def test_null_normalized_duplicate_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_location_fakes(monkeypatch)
    monkeypatch.setattr(
        master_data_service.lab_repository,
        "find_null_normalized_location",
        lambda *args, **kwargs: SimpleNamespace(storage_location_id=8),
    )
    with pytest.raises(ValidationError, match="already exists"):
        master_data_service.create_location(
            assistant(),
            lab_id=1,
            cabinet_no="C-A1",
            shelf_no=None,
            drawer_no=None,
            location_type="CABINET",
        )
