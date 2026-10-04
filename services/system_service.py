"""Read-only system readiness service used by transport layers."""

from __future__ import annotations

from db.healthcheck import check_database


def health_status():
    """Return the existing sanitized database health result."""

    return check_database()
