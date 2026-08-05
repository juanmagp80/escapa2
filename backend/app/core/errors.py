"""Uniform API error model and exception handlers."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import Settings


class ApiError(Exception):
    """Base domain error carrying a stable error code."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class AiDisabledError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            code="AI_DISABLED",
            message="AI features are disabled.",
            status_code=503,
        )


class AiInvalidResponseError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            code="AI_INVALID_RESPONSE",
            message="The AI provider returned an invalid response.",
            status_code=502,
        )


class RateLimitedError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            code="RATE_LIMITED",
            message="Request limit reached. Try again later.",
            status_code=429,
        )


class ProviderUnavailableError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            code="PROVIDER_UNAVAILABLE",
            message="The AI provider is temporarily unavailable.",
            status_code=502,
        )


class NotFoundError(ApiError):
    def __init__(self, resource: str, resource_id: str) -> None:
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} '{resource_id}' was not found.",
            status_code=404,
            details={"resource": resource, "id": resource_id},
        )


def _error_payload(code: str, message: str, details: dict[str, Any]) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "details": details}}


def _serializable_errors(errors: Sequence[Any]) -> list[dict[str, Any]]:
    """Convert FastAPI/Pydantic validation errors into JSON-safe values.

    Pydantic may place non-serializable objects (e.g. a ValueError raised by a
    model validator) inside the ``ctx`` of an error; clients only need the
    message, so those are stringified.
    """
    safe: list[dict[str, Any]] = []
    for error in errors:
        item: dict[str, Any] = {}
        for key, value in error.items():
            if key == "ctx" and isinstance(value, dict):
                item[key] = {
                    inner_key: (
                        str(inner_value) if isinstance(inner_value, Exception) else inner_value
                    )
                    for inner_key, inner_value in value.items()
                }
            else:
                item[key] = value
        safe.append(item)
    return safe


def register_exception_handlers(app: FastAPI, settings: Settings) -> None:
    @app.exception_handler(ApiError)
    async def handle_api_error(_: Request, exc: ApiError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=_error_payload(
                "VALIDATION_ERROR",
                "The request is invalid",
                {"errors": _serializable_errors(exc.errors())},
            ),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        if settings.app_debug:
            raise exc
        return JSONResponse(
            status_code=500,
            content=_error_payload(
                "INTERNAL_ERROR",
                "An unexpected error occurred.",
                {},
            ),
        )
