# ==============================================================================
# FILE   : backend/app/modules/auth/login_router.py
# STORY  : #19 Student Login and Session Validation  [FR-001; SEC-01, SEC-03, SEC-04, SEC-05, SEC-07]
# OWNER  : Sanskar (@sanskarghenappagol)   |   MERGE ORDER: Phase 3
# ==============================================================================
#
# PURPOSE
#   HTTP endpoints for login, logout and session check.
#
# ROUTES
#   router = APIRouter(prefix="/api/auth", tags=["auth"])
#   POST /api/auth/login   body LoginRequest -> 200 LoginResponse + Set-Cookie access_token ; 401 invalid_credentials ; 429 too_many_attempts
#   POST /api/auth/logout  -> 204, always clears the cookie, revokes the token if one was presented (reusing the old token afterwards must give 401)
#   GET  /api/auth/me      Depends(get_current_user) -> UserOut  (the SPA calls this on page load to restore the session; also proves session persists across modules, IT_03)
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

import jwt
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_client_ip, get_current_user
from app.core.tokens import COOKIE_NAME, ALGORITHM, clear_session_cookie, set_session_cookie
from app.modules.auth import login_service
from app.modules.auth.login_schemas import LoginRequest, LoginResponse, UserOut
from app.modules.auth.models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    user, token, _expires = login_service.authenticate(db, payload.email, payload.password, get_client_ip(request))
    set_session_cookie(response, token)
    return LoginResponse(user=UserOut.model_validate(user))


@router.post("/logout", status_code=204)
def logout(request: Request, db: Session = Depends(get_db)) -> Response:
    """Always clears the cookie; revokes the token if a valid one was presented."""
    response = Response(status_code=204)
    token = request.cookies.get(COOKIE_NAME)
    if token:
        try:
            # An expired token is already useless, so only its signature matters here.
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False, "require": ["jti"]}
            )
            login_service.logout(db, payload)
        except jwt.PyJWTError:
            pass
    clear_session_cookie(response)
    return response


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)
