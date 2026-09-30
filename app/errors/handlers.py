from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.database import DatabaseConnectionError
from app.errors.exceptions import ApplicationError


REQUEST_ID_HEADER = "X-Request-ID"


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "req_unknown")


def _response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: Any = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    response_headers = dict(headers or {})
    response_headers[REQUEST_ID_HEADER] = _request_id(request)
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details,
                "request_id": _request_id(request),
            }
        },
        headers=response_headers,
    )


async def application_error_handler(
    request: Request,
    error: ApplicationError,
) -> JSONResponse:
    return _response(
        request,
        error.status_code,
        error.error_code,
        error.message,
        error.details,
    )


async def database_error_handler(
    request: Request,
    error: DatabaseConnectionError,
) -> JSONResponse:
    return _response(
        request,
        503,
        "database_unavailable",
        "Database unavailable",
    )


async def validation_error_handler(
    request: Request,
    error: RequestValidationError,
) -> JSONResponse:
    details = [
        {
            "field": ".".join(str(part) for part in item["loc"]),
            "message": item["msg"],
        }
        for item in error.errors()
    ]
    return _response(
        request,
        422,
        "validation_error",
        "Request validation failed",
        details,
    )


async def http_error_handler(
    request: Request,
    error: HTTPException,
) -> JSONResponse:
    message = error.detail if isinstance(error.detail, str) else "HTTP request failed"
    return _response(
        request,
        error.status_code,
        "http_error",
        message,
        headers=error.headers,
    )


async def unexpected_error_handler(request: Request, error: Exception) -> JSONResponse:
    return _response(
        request,
        500,
        "internal_server_error",
        "An unexpected error occurred.",
    )


def register_exception_handlers(application: Any) -> None:
    application.add_exception_handler(ApplicationError, application_error_handler)
    application.add_exception_handler(DatabaseConnectionError, database_error_handler)
    application.add_exception_handler(RequestValidationError, validation_error_handler)
    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(Exception, unexpected_error_handler)