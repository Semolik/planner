import uuid

from fastapi import APIRouter, Depends, HTTPException

from api.models.user_models import User
from api.schemas.custom_achievements import (
    AchievementRead,
    AchievementCreate,
    AchievementUpdate,
)
from api.core.users_controller import current_user
from api.cruds.custom_achievements_crud import CustomAchievementsCRUD
from api.db.session import get_async_session

api_router = APIRouter(prefix="/achievements", tags=["achievements"])


@api_router.get("", response_model=list[AchievementRead])
async def get_achievements_by_year(
        year: int,
        only_custom: bool = False,
        db=Depends(get_async_session),
        current_user: User = Depends(current_user),
):
    achievements = await CustomAchievementsCRUD(db).get_user_achievements_by_year(
        user_id=current_user.id,
        year=year,
        only_custom=only_custom,
    )
    return achievements