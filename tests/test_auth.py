"""External credential and frozen-schema security checks."""

import bcrypt

from config.settings import Settings


def test_bcrypt_demo_hash_is_external_and_verifiable() -> None:
    password = b"academic-demo-password"
    hashed = bcrypt.hashpw(password, bcrypt.gensalt(rounds=4))
    assert bcrypt.checkpw(password, hashed)
    assert not bcrypt.checkpw(b"wrong", hashed)


def test_database_url_uses_same_frozen_database_name() -> None:
    settings = Settings(
        db_host="127.0.0.1",
        db_port=3306,
        db_name="sems_db",
        db_user="sems_app",
        db_password="local only",
    )
    assert settings.database_url.endswith("/sems_db?charset=utf8mb4")
    assert "smart_electronics_lab_ddl" not in settings.database_url

