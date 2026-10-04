"""Environment/Streamlit-secret backed application settings."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Mapping
from urllib.parse import quote_plus

from dotenv import load_dotenv

from config.constants import DATABASE_NAME, DEFAULT_DB_PORT


PLACEHOLDER_MARKERS = ("REPLACE_WITH", "CHANGE_ME", "YOUR_")


def _streamlit_secrets() -> Mapping[str, Any]:
    try:
        import streamlit as st

        return dict(st.secrets)
    except Exception:
        return {}


def _nested(mapping: Mapping[str, Any], section: str, key: str) -> Any:
    value = mapping.get(section, {})
    return value.get(key) if hasattr(value, "get") else None


@dataclass(frozen=True, slots=True)
class Settings:
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_connect_timeout: int = 5
    log_level: str = "INFO"
    demo_credentials: Mapping[str, str] | None = None

    @property
    def database_url(self) -> str:
        user = quote_plus(self.db_user)
        password = quote_plus(self.db_password)
        return (
            f"mysql+pymysql://{user}:{password}@{self.db_host}:"
            f"{self.db_port}/{self.db_name}?charset=utf8mb4"
        )

    def connection_issues(self) -> list[str]:
        """Return safe, user-facing connection configuration problems."""

        issues: list[str] = []
        if not self.db_host.strip():
            issues.append("DB_HOST is missing")
        elif any(marker in self.db_host for marker in PLACEHOLDER_MARKERS):
            issues.append("DB_HOST still contains a configuration placeholder")
        if not 1 <= self.db_port <= 65535:
            issues.append("DB_PORT must be between 1 and 65535")
        if self.db_name != DATABASE_NAME:
            issues.append(f"DB_NAME must be {DATABASE_NAME}")
        if not self.db_user.strip():
            issues.append("DB_USER is missing")
        elif any(marker in self.db_user for marker in PLACEHOLDER_MARKERS):
            issues.append("DB_USER still contains a configuration placeholder")
        if not self.db_password:
            issues.append("DB_PASSWORD is missing")
        elif any(marker in self.db_password for marker in PLACEHOLDER_MARKERS):
            issues.append("DB_PASSWORD still contains a configuration placeholder")
        if self.db_pool_size < 1:
            issues.append("DB_POOL_SIZE must be at least 1")
        if self.db_max_overflow < 0:
            issues.append("DB_MAX_OVERFLOW cannot be negative")
        if not 1 <= self.db_connect_timeout <= 60:
            issues.append("DB_CONNECT_TIMEOUT must be between 1 and 60 seconds")
        return issues

    @classmethod
    def from_sources(cls) -> "Settings":
        load_dotenv(override=False)
        secrets = _streamlit_secrets()

        def value(env_name: str, section: str, key: str, default: Any) -> Any:
            env_value = os.getenv(env_name)
            if env_value is not None:
                return env_value
            secret_value = _nested(secrets, section, key)
            return default if secret_value is None else secret_value

        def integer(env_name: str, section: str, key: str, default: int) -> int:
            raw = value(env_name, section, key, default)
            try:
                return int(raw)
            except (TypeError, ValueError):
                # A sentinel lets startup show all safe configuration issues together.
                return -1

        credential_text = os.getenv("SEMS_DEMO_CREDENTIALS_JSON")
        credentials: Mapping[str, str]
        if credential_text:
            try:
                parsed = json.loads(credential_text)
            except json.JSONDecodeError as exc:
                raise ValueError("SEMS_DEMO_CREDENTIALS_JSON is not valid JSON") from exc
            if not isinstance(parsed, dict):
                raise ValueError("SEMS_DEMO_CREDENTIALS_JSON must be a JSON object")
            credentials = {str(k).lower(): str(v) for k, v in parsed.items()}
        else:
            auth_section = secrets.get("auth", {})
            raw_credentials = (
                auth_section.get("credentials", {})
                if hasattr(auth_section, "get")
                else {}
            )
            credentials = {
                str(k).lower(): str(v) for k, v in dict(raw_credentials).items()
            }

        return cls(
            db_host=str(value("DB_HOST", "database", "host", "127.0.0.1")),
            db_port=integer("DB_PORT", "database", "port", DEFAULT_DB_PORT),
            db_name=str(value("DB_NAME", "database", "name", DATABASE_NAME)),
            db_user=str(value("DB_USER", "database", "user", "sems_app")),
            db_password=str(value("DB_PASSWORD", "database", "password", "")),
            db_pool_size=integer("DB_POOL_SIZE", "database", "pool_size", 5),
            db_max_overflow=integer(
                "DB_MAX_OVERFLOW", "database", "max_overflow", 10
            ),
            db_connect_timeout=integer(
                "DB_CONNECT_TIMEOUT", "database", "connect_timeout", 5
            ),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            demo_credentials=credentials,
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_sources()
