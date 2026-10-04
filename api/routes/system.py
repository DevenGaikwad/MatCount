"""Public liveness and database-health information with safe messages only."""

from __future__ import annotations

from fastapi import APIRouter

from api.serialization import success
from services.system_service import health_status


router = APIRouter(tags=["System"])


@router.get("/health")
def health():
    status = health_status()
    return success(
        {
            "api": "online",
            "database": {
                "ok": status.ok,
                "name": status.database_name,
                "server_version": status.server_version,
                "message": status.message,
            },
        }
    )
