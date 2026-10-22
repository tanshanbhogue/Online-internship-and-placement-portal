import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "portal.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn


def init_db():
    """Create tables from schema.sql if the file exists."""
    if not SCHEMA_PATH.exists():
        return
    with get_connection() as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))