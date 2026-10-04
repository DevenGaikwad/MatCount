"""Genuine rollback behavior test using an isolated in-memory database."""

import pytest
from sqlalchemy import create_engine, text

import db.session as session_module


def test_session_scope_rolls_back_on_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE sample (id INTEGER PRIMARY KEY, value TEXT)"))

    monkeypatch.setattr(session_module, "get_engine", lambda: engine)
    with pytest.raises(RuntimeError):
        with session_module.session_scope() as session:
            session.execute(text("INSERT INTO sample (value) VALUES ('temporary')"))
            raise RuntimeError("force rollback")

    with engine.connect() as connection:
        assert connection.execute(text("SELECT COUNT(*) FROM sample")).scalar_one() == 0
    engine.dispose()

