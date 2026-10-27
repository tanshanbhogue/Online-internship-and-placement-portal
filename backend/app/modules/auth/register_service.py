

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import DuplicateEmail, ValidationFailed
from app.core.security import hash_password, validate_password_strength
from app.modules.auth.models import Role, User
from app.modules.auth.register_schemas import RegisterRequest


def register_student(db: Session, data: RegisterRequest) -> User:
    name = data.name.strip()
    email = data.email.strip().lower()

    problems = validate_password_strength(data.password)
    if problems:
        raise ValidationFailed(fields={"password": problems})

    if db.scalar(select(User.id).where(User.email == email)) is not None:
        raise DuplicateEmail()

    user = User(
        name=name,
        email=email,
        password_hash=hash_password(data.password),
        role=Role.STUDENT,  # hard-coded: admins cannot be created through registration (SEC-07)
        college=data.college,
        batch=data.batch,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateEmail()
    return user


