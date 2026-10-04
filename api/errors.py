"""Sanitized API error mapping for domain, validation and unexpected failures."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from services.exceptions import (
    AuthenticationError,
    AuthorizationError,
    InsufficientStockError,
    NotFoundError,
    SemsError,
    StateTransitionError,
    ValidationError,
)


LOGGER = logging.getLogger(__name__)


def _body(code: str, message: str, *, details: list[dict[str, str]] | None = None):
    error: dict[str, object] = {"code": code, "message": message}
    if details:
        error["details"] = details
    return {"error": error}


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(SemsError)
    async def handle_domain_error(_request: Request, exc: SemsError) -> JSONResponse:
        if isinstance(exc, AuthenticationError):
            status, code = 401, "AUTHENTICATION_REQUIRED"
        elif isinstance(exc, AuthorizationError):
            status, code = 403, "PERMISSION_DENIED"
        elif isinstance(exc, NotFoundError):
            status, code = 404, "NOT_FOUND"
        elif isinstance(exc, InsufficientStockError):
            status, code = 409, "INSUFFICIENT_STOCK"
        elif isinstance(exc, StateTransitionError):
            status, code = 409, "INVALID_STATE_TRANSITION"
        elif isinstance(exc, ValidationError):
            status, code = 422, "VALIDATION_ERROR"
        else:
            status, code = 400, "SEMS_ERROR"
        return JSONResponse(status_code=status, content=_body(code, str(exc)))

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = []
        for item in exc.errors():
            location = ".".join(str(part) for part in item.get("loc", [])[1:])
            details.append(
                {
                    "field": location or "request",
                    "message": str(item.get("msg", "Invalid value")),
                }
            )
        return JSONResponse(
            status_code=422,
            content=_body(
                "INVALID_REQUEST",
                "Review the highlighted input and try again.",
                details=details,
            ),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        LOGGER.exception(
            "Unhandled API failure path=%s class=%s",
            request.url.path,
            exc.__class__.__name__,
        )
        return JSONResponse(
            status_code=500,
            content=_body(
                "INTERNAL_ERROR",
                "SEMS could not complete the operation. Check the server log.",
            ),
        )

