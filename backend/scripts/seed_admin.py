# ==============================================================================
# FILE   : backend/scripts/seed_admin.py
# STORY  : #19 Student Login and Session Validation  [FR-001; SEC-01, SEC-03, SEC-04, SEC-05, SEC-07]
# OWNER  : Sanskar (@sanskarghenappagol)   |   MERGE ORDER: Phase 3
# ==============================================================================
#
# PURPOSE
#   One-off script creating the admin account (admins cannot self-register).
#
# BEHAVIOUR
#   Run: python -m scripts.seed_admin  (from backend/). Reads ADMIN_EMAIL and ADMIN_PASSWORD from settings/env, validates strength, creates a User with role ADMIN if the email is not present,
#   otherwise prints 'already exists'. Idempotent. Never prints the password. Add backend/scripts/__init__.py as an empty package marker if needed.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

import sys

from pydantic import EmailStr, TypeAdapter, ValidationError
from sqlalchemy import select

from app.core.config import settings
from app.core.database import SessionLocal, init_db
from app.core.security import hash_password, validate_password_strength
from app.modules.auth.models import Role, User


def main() -> int:
    email = (settings.ADMIN_EMAIL or "").strip().lower()
    password = settings.ADMIN_PASSWORD or ""
    if not email or not password:
        print("ADMIN_EMAIL and ADMIN_PASSWORD must be set (environment or backend/.env).")
        return 1
    try:
        # Same validation the login endpoint applies: otherwise an admin could be created who can never log in.
        email = TypeAdapter(EmailStr).validate_python(email).lower()
    except ValidationError:
        print("ADMIN_EMAIL is not a valid email address (reserved domains such as .test or .local are rejected).")
        return 1
    problems = validate_password_strength(password)
    if problems:
        print("ADMIN_PASSWORD is too weak: " + "; ".join(problems))
        return 1

    init_db()
    with SessionLocal() as db:
        if db.scalar(select(User).where(User.email == email)) is not None:
            print(f"Admin {email} already exists.")
            return 0
        db.add(User(name="Administrator", email=email, password_hash=hash_password(password), role=Role.ADMIN))
        db.commit()
    print(f"Admin {email} created.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
