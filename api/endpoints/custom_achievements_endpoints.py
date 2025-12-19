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

api_router = APIRouter(prefix="/custom-achievements", tags=["custom-achievements"])

@api_router.post("", response_model=AchievementRead)
async def create_custom_achievement(
    custom_achievement: AchievementCreate,
    db=Depends(get_async_session),
    current_user: User = Depends(current_user),
):
    return await CustomAchievementsCRUD(db).create_custom_achievement(
        custom_achievement, user_id=current_user.id
    )


@api_router.put(
    "/{custom_achievement_id}",
    response_model=AchievementRead,
)
async def update_custom_achievement(
    custom_achievement: AchievementUpdate,
    custom_achievement_id: uuid.UUID,
    db=Depends(get_async_session),
    current_user: User = Depends(current_user),
):
    db_custom_achievement = await CustomAchievementsCRUD(
        db
    ).get_custom_achievement_by_id(custom_achievement_id)
    if db_custom_achievement is None:
        raise HTTPException(status_code=404, detail="Custom Achievement not found")
    if (
        db_custom_achievement.user_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Нет доступа")
    return await CustomAchievementsCRUD(db).update_custom_achievement(
        custom_achievement=db_custom_achievement,
        update_data=custom_achievement,
    )


@api_router.delete(
    "/{custom_achievement_id}",
    status_code=204,
)
async def delete_custom_achievement(
    custom_achievement_id: uuid.UUID,
    db=Depends(get_async_session),
    current_user: User = Depends(current_user),
):
    db_custom_achievement = await CustomAchievementsCRUD(
        db
    ).get_custom_achievement_by_id(custom_achievement_id)
    if db_custom_achievement is None:
        raise HTTPException(status_code=404, detail="Custom Achievement not found")
    if (
        db_custom_achievement.user_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Нет доступа")
    await CustomAchievementsCRUD(db).delete(db_custom_achievement)
