
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_client_ip, get_current_user
from app.core.errors import NotAuthenticated
from app.core.tokens import (
    clear_session_cookie,
    decode_access_token,
    set_session_cookie,
)
from app.modules.auth.login_schemas import LoginRequest, LoginResponse, UserOut
from app.modules.auth.login_service import authenticate, logout
from app.modules.auth.models import User


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> LoginResponse:
    user, token, _expires_at = authenticate(
        db=db,
        email=str(body.email),
        password=body.password,
        ip=get_client_ip(request),
    )

    set_session_cookie(response, token)
    return LoginResponse(user=UserOut.model_validate(user))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_route(
    request: Request,
    db: Session = Depends(get_db),
) -> Response:
    token = request.cookies.get("access_token")

    if token:
        try:
            payload = decode_access_token(token)
            logout(db, payload)
        except NotAuthenticated:
            # Logout must still succeed for an invalid or expired cookie.
            pass

    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    clear_session_cookie(response)
    return response


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(user)
