# ==============================================================================
# FILE   : backend/app/core/errors.py
# STORY  : Foundation - shared scaffold (chore, no backlog issue)
# OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 0
# ==============================================================================
#
# PURPOSE
#   Shared exception hierarchy and the handlers that turn every failure into the standard error body.
#   All modules raise these; nobody returns ad-hoc error JSON.
#
# CODE TO WRITE
#   class AppError(Exception): status_code:int, code:str, message:str, fields:dict[str,list[str]]|None.
#   Subclasses (constructor takes optional message/fields overriding the default message):
#     ValidationFailed(422, "validation_error", "Validation failed")
#     DuplicateEmail(409, "duplicate_email", "Email already exists")
#     InvalidCredentials(401, "invalid_credentials", "Invalid username or password")
#     TooManyAttempts(429, "too_many_attempts", "Too many failed attempts. Try again later.")
#     NotAuthenticated(401, "not_authenticated", "Not authenticated")
#     Forbidden(403, "forbidden", "You do not have permission to do this")
#     NotFound(404, "not_found", "Not found")  - accepts code override (e.g. "no_questions")
#     AlreadyApplied(409, "already_applied", "You have already applied to this internship")
#     ApplicationWindowClosed(409, "application_window_closed", "Application window closed")
#     InvalidFile(422, "invalid_file", "Invalid file")
#     Conflict(409, "conflict", "Conflict")
#   Handlers (register_error_handlers(app)):
#     - AppError -> JSONResponse(status, {"detail": message, "code": code, "fields": fields?}).
#     - RequestValidationError -> 422 with code validation_error and fields {field_name: [messages]} (strip "body." prefixes, never echo the submitted value, especially passwords).
#     - Exception (catch-all) -> 500 {"detail": "Something went wrong", "code": "server_error"}; log the traceback server side only (SEC-19).
#   Also export a helper `fields_from_pydantic(errors)` used by the validation handler.
#
# SECURITY
#   SEC-19: responses never contain stack traces, SQL, file paths, tokens or the offending input value.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
