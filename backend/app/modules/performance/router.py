from fastapi import APIRouter, Depends, Response

from app.core.dependencies import get_current_admin
from app.middleware.request_timing import STATS
from app.modules.auth.models import User

router = APIRouter(prefix="/api/admin", tags=["performance"])


@router.get("/performance")
def performance(response: Response, _admin: User = Depends(get_current_admin)) -> dict:
    response.headers["Cache-Control"] = "no-store"
    return STATS.snapshot()
