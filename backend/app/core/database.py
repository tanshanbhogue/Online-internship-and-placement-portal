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
