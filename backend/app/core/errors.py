import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("app.errors")


class AppError(Exception):
    status_code: int = 500
    code: str = "server_error"
    default_message: str = "Something went wrong"

    def __init__(
        self,
        message: str | None = None,
        fields: dict[str, list[str]] | None = None,
        code: str | None = None,
    ):
        self.message = message or self.default_message
        self.fields = fields
        if code is not None:
            self.code = code
        super().__init__(self.message)


class ValidationFailed(AppError):
    status_code = 422
    code = "validation_error"
    default_message = "Validation failed"


class DuplicateEmail(AppError):
    status_code = 409
    code = "duplicate_email"
    default_message = "Email already exists"


class InvalidCredentials(AppError):
    status_code = 401
    code = "invalid_credentials"
    default_message = "Invalid username or password"


class TooManyAttempts(AppError):
    status_code = 429
    code = "too_many_attempts"
    default_message = "Too many failed attempts. Try again later."


class NotAuthenticated(AppError):
    status_code = 401
    code = "not_authenticated"
    default_message = "Not authenticated"


class Forbidden(AppError):
    status_code = 403
    code = "forbidden"
    default_message = "You do not have permission to do this"


class NotFound(AppError):
    status_code = 404
    code = "not_found"
    default_message = "Not found"


class AlreadyApplied(AppError):
    status_code = 409
    code = "already_applied"
    default_message = "You have already applied to this internship"


class ApplicationWindowClosed(AppError):
    status_code = 409
    code = "application_window_closed"
    default_message = "Application window closed"


class InvalidFile(AppError):
    status_code = 422
    code = "invalid_file"
    default_message = "Invalid file"


class Conflict(AppError):
    status_code = 409
    code = "conflict"
    default_message = "Conflict"


_LOCATION_PREFIXES = {"body", "query", "path", "form", "header", "cookie"}


def _friendly_message(error: dict[str, Any]) -> str:
    """Human message for one pydantic error. Never uses error['input'] (SEC-19)."""
    kind = error.get("type", "")
    ctx = error.get("ctx") or {}
    msg = str(error.get("msg", "Invalid value"))
    if kind == "missing":
        return "This field is required"
    if kind == "string_too_short":
        minimum = ctx.get("min_length")
        return "This field is required" if minimum == 1 else f"Must be at least {minimum} characters"
    if kind == "string_too_long":
        return f"Must be at most {ctx.get('max_length')} characters"
    if kind in ("greater_than_equal", "less_than_equal", "greater_than", "less_than"):
        return msg
    if kind == "too_short":
        return f"Must contain at least {ctx.get('min_length')} items"
    if kind == "too_long":
        return f"Must contain at most {ctx.get('max_length')} items"
    if kind == "extra_forbidden":
        return "This field is not allowed"
    if msg.lower().startswith("value is not a valid email"):
        return "Enter a valid email address"
    if kind in ("json_invalid", "model_attributes_type", "model_type"):
        return "Invalid request body"
    if msg.startswith("Value error, "):
        return msg[len("Value error, "):]
    return msg


def fields_from_pydantic(errors: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Convert pydantic/FastAPI error dicts to {field: [messages]} without echoing submitted values."""
    fields: dict[str, list[str]] = {}
    for error in errors:
        loc = [str(part) for part in error.get("loc", ())]
        while len(loc) > 1 and loc[0] in _LOCATION_PREFIXES:
            loc = loc[1:]
        name = ".".join(loc) if loc else "body"
        message = _friendly_message(error)
        bucket = fields.setdefault(name, [])
        if message not in bucket:
            bucket.append(message)
    return fields


def _body(message: str, code: str, fields: dict[str, list[str]] | None = None) -> dict[str, Any]:
    body: dict[str, Any] = {"detail": message, "code": code}
    if fields:
        body["fields"] = fields
    return body


async def _handle_app_error(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=_body(exc.message, exc.code, exc.fields))


async def _handle_validation_error(_request: Request, exc: RequestValidationError) -> JSONResponse:
    fields = fields_from_pydantic(exc.errors())
    return JSONResponse(status_code=422, content=_body("Validation failed", "validation_error", fields))


async def _handle_http_exception(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
    codes = {404: "not_found", 405: "method_not_allowed", 401: "not_authenticated", 403: "forbidden"}
    messages = {404: "Not found", 405: "Method not allowed", 401: "Not authenticated", 403: "Forbidden"}
    code = codes.get(exc.status_code, "http_error")
    message = messages.get(exc.status_code, "Request failed")
    return JSONResponse(status_code=exc.status_code, content=_body(message, code), headers=exc.headers)


async def _handle_unexpected(_request: Request, exc: Exception) -> JSONResponse:
    # Traceback goes to the server log only; the client never sees it (SEC-19).
    logger.error("Unhandled exception", exc_info=(type(exc), exc, exc.__traceback__))
    return JSONResponse(status_code=500, content=_body("Something went wrong", "server_error"))


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, _handle_app_error)
    app.add_exception_handler(RequestValidationError, _handle_validation_error)
    app.add_exception_handler(StarletteHTTPException, _handle_http_exception)
    app.add_exception_handler(Exception, _handle_unexpected)
