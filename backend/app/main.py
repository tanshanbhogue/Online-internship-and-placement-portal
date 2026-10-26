# ==============================================================================
# FILE   : backend/app/main.py
# STORY  : Foundation - shared scaffold (chore, no backlog issue)
# OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 0
# ==============================================================================
#
# PURPOSE
#   FastAPI application factory and entry point (uvicorn app.main:app). Wires middleware, error handlers and auto-discovers
#   every router, so feature owners never edit this file.
#
# ROLE
#   Composition root of the backend. Corresponds to the API Gateway box in the component diagram (single entry point to all services).
#
# CODE TO WRITE
#   1. create_app() -> FastAPI(title="Internship & Placement Prep Portal"); module-level `app = create_app()`.
#   2. CORS: allow origins from settings.CORS_ORIGINS, allow_credentials=True, methods and headers limited to what the SPA uses.
#   3. Startup: call db.base/database init_db() (Base.metadata.create_all) after importing app.db.models_registry.
#   4. Optional plug-in: try importlib.import_module("app.core.log_redaction") and call install() if it exists
#      (it arrives with story #20). A ModuleNotFoundError must be swallowed silently.
#   5. Router discovery: walk app.modules with pkgutil.walk_packages; import every module whose last name part is "router"
#      or ends with "_router"; if it has an attribute `router` (APIRouter) call app.include_router(router). Each router sets its own
#      prefix (e.g. "/api/auth"), so main.py adds none. Skip modules that fail with ModuleNotFoundError for optional deps only; real import errors must surface.
#   6. Register exception handlers from app.core.errors (AppError, RequestValidationError, generic Exception) so every error uses the shared body.
#   7. GET /api/health -> {"status": "ok"} (no auth, used for smoke tests).
#   8. Add a middleware that sets basic security headers (X-Content-Type-Options: nosniff, X-Frame-Options: DENY, Referrer-Policy: same-origin).
#
# DEPENDS ON
#   app.core.config, app.core.database, app.core.errors, app.db.models_registry
#
# DO NOT
#   import any feature module directly; hardcode routers; log request bodies (they contain passwords).
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
