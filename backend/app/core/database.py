# ==============================================================================
# FILE   : backend/app/core/database.py
# STORY  : Foundation - shared scaffold (chore, no backlog issue)
# OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 0
# ==============================================================================
#
# PURPOSE
#   SQLAlchemy engine, session factory and the get_db FastAPI dependency.
#
# CODE TO WRITE
#   - engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False} only for sqlite).
#   - For SQLite attach an event listener that runs PRAGMA foreign_keys=ON on connect.
#   - SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False).
#   - def get_db(): yield a session, always close it in finally; do not commit implicitly (services commit explicitly).
#   - def init_db(): import app.db.models_registry then Base.metadata.create_all(bind=engine).
#
# DEPENDS ON
#   app.core.config, app.db.base
#
# SECURITY
#   SEC-09: all DB access goes through SQLAlchemy ORM / bound parameters. No string-built SQL anywhere in the project.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base

_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
)

if _is_sqlite:

    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, _record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    """FastAPI dependency. Services commit explicitly; nothing is committed implicitly here."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    import app.db.models_registry  # noqa: F401  (registers every table)

    Base.metadata.create_all(bind=engine)
