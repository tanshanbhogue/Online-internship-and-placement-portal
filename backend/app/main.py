import importlib
import logging
import pkgutil
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.core.errors import register_error_handlers

logger = logging.getLogger("app.startup")


def _install_log_redaction() -> None:
    """Optional plug-in from story #20; a missing module is fine."""
    try:
        module = importlib.import_module("app.core.log_redaction")
    except ModuleNotFoundError as exc:
        if exc.name != "app.core.log_redaction":
            raise
        return
    module.install()


def _include_discovered_routers(app: FastAPI) -> None:
    """Include every `router` found in router.py / *_router.py under app.modules."""
    import app.modules as modules_pkg

    for info in sorted(pkgutil.walk_packages(modules_pkg.__path__, prefix="app.modules."), key=lambda i: i.name):
        last = info.name.rsplit(".", 1)[-1]
        if last != "router" and not last.endswith("_router"):
            continue
        try:
            module = importlib.import_module(info.name)
        except ModuleNotFoundError as exc:
            # Only a missing OPTIONAL third-party dependency is skipped. A missing app.* module is a real bug.
            if exc.name and not exc.name.startswith("app"):
                logger.warning("Skipping %s: optional dependency %s is not installed", info.name, exc.name)
                continue
            raise
        router = getattr(module, "router", None)
        if isinstance(router, APIRouter):
            app.include_router(router)


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    init_db()
    yield


def create_app() -> FastAPI:
    _install_log_redaction()

    app = FastAPI(title="Internship & Placement Prep Portal", lifespan=_lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Accept"],
    )

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        return response

    register_error_handlers(app)

    @app.get("/api/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    _include_discovered_routers(app)
    return app


app = create_app()
