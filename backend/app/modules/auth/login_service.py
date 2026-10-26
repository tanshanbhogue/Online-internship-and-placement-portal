# ==============================================================================
# FILE   : backend/app/modules/auth/login_service.py
# STORY  : #19 Student Login and Session Validation  [FR-001; SEC-01, SEC-03, SEC-04, SEC-05, SEC-07]
# OWNER  : Sanskar (@sanskarghenappagol)   |   MERGE ORDER: Phase 3
# ==============================================================================
#
# PURPOSE
#   Authentication business logic (use case 'Register & Login', steps 8-10).
#
# EXPOSES
#   authenticate(db, email, password, ip) -> tuple[User, str token, datetime expires]
#   logout(db, token_payload) -> None   # revoke jti
#
# FLOW
#   1. normalise email (strip, lowercase). 2. ensure_not_throttled. 3. load user; if none -> core.security.verify_dummy(password).
#   4. verify_password; on any failure (unknown, wrong password, inactive) record_attempt(success=False), write security.audit log "login_failed" (email hash/id only, no password), raise InvalidCredentials().
#   5. on success clear_failures, record_attempt(success=True), create token, return.
#   Error text must be identical for unknown account and wrong password (tests UT_02, UT_03, SEC-04).
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

import hashlib
import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import InvalidCredentials
from app.core.security import verify_dummy, verify_password
from app.core.tokens import create_access_token, revoke
from app.modules.auth.login_throttle import clear_failures, ensure_not_throttled, record_attempt
from app.modules.auth.models import User
from app.modules.auth.session_models import purge_expired
from app.db.base import utcnow

audit = logging.getLogger("security.audit")


def _email_ref(email: str) -> str:
    return hashlib.sha256(email.encode()).hexdigest()[:12]


def authenticate(db: Session, email: str, password: str, ip: str | None) -> tuple[User, str, datetime]:
    email = (email or "").strip().lower()
    ensure_not_throttled(db, email, ip)

    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        verify_dummy(password)  # same cost as a real check: no user enumeration (SEC-04)
        ok = False
    else:
        ok = verify_password(password, user.password_hash) and user.is_active

    if not ok:
        record_attempt(db, email, ip, success=False)
        audit.warning("login_failed email_ref=%s ip=%s", _email_ref(email), ip)
        raise InvalidCredentials()

    clear_failures(db, email)
    record_attempt(db, email, ip, success=True)
    token, _jti, expires_at = create_access_token(user.id, user.role.value)
    purge_expired(db)
    audit.info("login_succeeded user_id=%s", user.id)
    return user, token, expires_at


def logout(db: Session, token_payload: dict) -> None:
    from datetime import timezone

    exp = token_payload.get("exp")
    expires_at = datetime.fromtimestamp(exp, tz=timezone.utc) if exp else utcnow()
    revoke(db, token_payload["jti"], expires_at)
    audit.info("logout user_id=%s", token_payload.get("sub"))
