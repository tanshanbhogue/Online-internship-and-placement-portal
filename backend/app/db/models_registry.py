import importlib
import pkgutil


def load_all_models() -> None:
    """Import every ``models.py`` / ``*_models.py`` under app.modules so Base.metadata is complete."""
    import app.modules as modules_pkg

    for info in pkgutil.walk_packages(modules_pkg.__path__, prefix="app.modules."):
        last = info.name.rsplit(".", 1)[-1]
        if last == "models" or last.endswith("_models"):
            importlib.import_module(info.name)


load_all_models()
