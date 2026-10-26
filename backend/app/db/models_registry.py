# ==============================================================================
# FILE   : backend/app/db/models_registry.py
# STORY  : Foundation - shared scaffold (chore, no backlog issue)
# OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 0
# ==============================================================================
#
# PURPOSE
#   Imports every model module so Base.metadata knows all tables before create_all() or test setup.
#
# CODE TO WRITE
#   Use pkgutil.walk_packages over app.modules and importlib.import_module every module whose last name part is "models" or ends with "_models".
#   Never import models by hand: new stories add files and are picked up automatically. Expose `load_all_models()` and call it at import time.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

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
