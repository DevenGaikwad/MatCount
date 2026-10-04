"""SEMS FastAPI transport layer; business rules remain in Python services."""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from api.errors import install_error_handlers
from api.routes import (
    auth,
    dashboard,
    disposals,
    inventory,
    master_data,
    reports,
    requests,
    system,
    transfers,
)
from config.logging_config import configure_logging


LOGGER = logging.getLogger(__name__)


def _csv_setting(name: str, default: str) -> list[str]:
    values = [item.strip() for item in os.getenv(name, default).split(",")]
    return [item for item in values if item]


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging()
    LOGGER.info("SEMS API starting")
    yield
    LOGGER.info("SEMS API stopping")


app = FastAPI(
    title="Smart Electronics Management System API",
    description="Thin HTTP adapter over the frozen SEMS Python service layer.",
    version="1.0",
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=_csv_setting(
        "SEMS_ALLOWED_HOSTS", "localhost,127.0.0.1,testserver"
    ),
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_csv_setting(
        "SEMS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ),
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)

install_error_handlers(app)

for route in (
    system.router,
    auth.router,
    dashboard.router,
    master_data.router,
    inventory.router,
    requests.router,
    transfers.router,
    disposals.router,
    reports.router,
):
    app.include_router(route, prefix="/api")

