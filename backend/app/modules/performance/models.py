import importlib

from sqlalchemy import Index

from app.db.base import Base
from app.modules.performance.indexes import INDEXES

for _module in (
    "app.modules.application.models",
    "app.modules.internship.models",
    "app.modules.mock_test.models",
    "app.modules.practice.models",
    "app.modules.question_bank.models",
):
    try:
        importlib.import_module(_module)
    except ModuleNotFoundError as exc:  # a story that is not merged yet simply has no indexes to add
        if not (exc.name or "").startswith("app.modules"):
            raise

for _name, _table, _columns in INDEXES:
    _t = Base.metadata.tables.get(_table)
    if _t is not None and _name not in {i.name for i in _t.indexes}:
        Index(_name, *[_t.c[c] for c in _columns])
