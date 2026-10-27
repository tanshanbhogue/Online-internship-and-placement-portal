
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.database import SessionLocal, init_db
from app.core.errors import AppError
from app.core.security import hash_password, validate_password_strength
from app.modules.auth.models import Role, User


def main() -> None:
    email = (settings.ADMIN_EMAIL or "").strip().lower()
    password = settings.ADMIN_PASSWORD

    if not email or not password:
        raise SystemExit(
            "Set ADMIN_EMAIL and ADMIN_PASSWORD in your backend environment first."
        )

    problems = validate_password_strength(password)
    if problems:
        raise SystemExit("Admin password does not meet the password policy.")

    init_db()
    db = SessionLocal()

    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print("Admin account already exists.")
            return

        admin = User(
            name="Administrator",
            email=email,
            password_hash=hash_password(password),
            role=Role.ADMIN,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print("Admin account created successfully.")

    except IntegrityError:
        db.rollback()
        print("An account with that email already exists.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
