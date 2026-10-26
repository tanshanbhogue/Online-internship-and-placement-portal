# ==============================================================================
# FILE   : backend/app/core/dependencies.py
# STORY  : #19 Student Login and Session Validation  [FR-001; SEC-01, SEC-03, SEC-04, SEC-05, SEC-07]
# OWNER  : Sanskar (@sanskarghenappagol)   |   MERGE ORDER: Phase 3
# ==============================================================================
#
# PURPOSE
#   FastAPI dependencies that every protected endpoint in the project uses for authentication and role checks. This file is the single
#   gatekeeper for SEC-01, SEC-06 and SEC-07.
#
# EXPOSES (other stories import these names)
#   get_current_user(request, response, db) -> User
#       read cookie access_token -> decode -> reject if revoked, user missing or inactive -> raise NotAuthenticated (401). On success re-issue the
#       cookie with a fresh 30-minute expiry (sliding expiry).
#   get_current_student(user=Depends(get_current_user)) -> User   # role must be STUDENT else Forbidden (403)
#   get_current_admin(user=Depends(get_current_user)) -> User     # role must be ADMIN else Forbidden (403); roles are checked server-side only
#   get_client_ip(request) -> str | None
#
# RULES
#   Guests get 401 not_authenticated; students on admin routes get 403 forbidden (test SEC-07). Ownership checks (SEC-06) are done by each service using user.id.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

from fastapi import Depends, Request, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import Forbidden, NotAuthenticated
from app.core.tokens import COOKIE_NAME, create_access_token, decode_access_token, is_revoked, set_session_cookie
from app.modules.auth.models import Role, User


def get_client_ip(request: Request) -> str | None:
    # Deliberately NOT reading X-Forwarded-For: it is client-controlled and would let attackers dodge throttling.
    return request.client.host if request.client else None


def get_current_user(request: Request, response: Response, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise NotAuthenticated()
    payload = decode_access_token(token)
    jti = payload["jti"]
    if is_revoked(db, jti):
        raise NotAuthenticated()
    try:
        user_id = int(payload["sub"])
    except (TypeError, ValueError):
        raise NotAuthenticated()
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise NotAuthenticated()

    # Sliding expiry: same jti (so logout still invalidates every copy), fresh 30-minute window.
    fresh, _, _ = create_access_token(user.id, user.role.value, jti=jti)
    set_session_cookie(response, fresh)
    request.state.token_jti = jti
    return user


def get_current_student(user: User = Depends(get_current_user)) -> User:
    if user.role != Role.STUDENT:
        raise Forbidden()
    return user


def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != Role.ADMIN:  # role comes from the database row, never from the client
        raise Forbidden()
    return user
