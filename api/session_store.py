"""Small in-memory opaque-session store for the local SEMS web frontend."""

from __future__ import annotations

import os
import secrets
import threading
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from services.exceptions import AuthenticationError
from services.rbac import Actor


def _ttl_minutes() -> int:
    try:
        value = int(os.getenv("SEMS_API_SESSION_TTL_MINUTES", "480"))
    except ValueError:
        value = 480
    return min(max(value, 15), 1440)


@dataclass(frozen=True, slots=True)
class SessionRecord:
    actor: Actor
    expires_at: datetime


class SessionStore:
    """Process-local sessions suitable for a single-machine academic deployment."""

    def __init__(self, *, maximum_sessions: int = 512) -> None:
        self._records: dict[str, SessionRecord] = {}
        self._lock = threading.RLock()
        self._maximum_sessions = maximum_sessions

    def _prune(self, now: datetime) -> None:
        expired = [
            token for token, record in self._records.items() if record.expires_at <= now
        ]
        for token in expired:
            self._records.pop(token, None)
        if len(self._records) >= self._maximum_sessions:
            oldest = min(self._records, key=lambda key: self._records[key].expires_at)
            self._records.pop(oldest, None)

    def create(self, actor: Actor) -> tuple[str, datetime]:
        now = datetime.now(UTC)
        expires_at = now + timedelta(minutes=_ttl_minutes())
        token = secrets.token_urlsafe(32)
        with self._lock:
            self._prune(now)
            self._records[token] = SessionRecord(actor=actor, expires_at=expires_at)
        return token, expires_at

    def resolve(self, token: str) -> Actor:
        now = datetime.now(UTC)
        with self._lock:
            record = self._records.get(token)
            if record is None or record.expires_at <= now:
                self._records.pop(token, None)
                raise AuthenticationError("Your SEMS session has expired. Sign in again.")
            return record.actor

    def revoke(self, token: str) -> None:
        with self._lock:
            self._records.pop(token, None)

    def clear(self) -> None:
        """Testing/shutdown helper; does not alter database state."""

        with self._lock:
            self._records.clear()


SESSION_STORE = SessionStore()

