import sys

from app.core.database import engine, init_db
from app.modules.performance.indexes import ensure_indexes


def main() -> int:
    init_db()
    done = ensure_indexes(engine)
    print(f"Indexes ensured: {len(done)}")
    for name in done:
        print(f"  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
