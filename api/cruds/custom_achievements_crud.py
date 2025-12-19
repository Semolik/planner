import uuid

from sqlalchemy import select

from api.cruds.base_crud import BaseCRUD
from api.models.user_models import CustomAchievementModel
from api.schemas.custom_achievements import (
    CustomAchievementCreate,
    CustomAchievementUpdate,
)


class CustomAchievementsCRUD(BaseCRUD):
    async def create_custom_achievement(
        self, custom_achievement: CustomAchievementCreate, user_id: uuid.UUID
    ):
        return await self.create(
            CustomAchievementModel(**custom_achievement.model_dump(), user_id=user_id)
        )

    async def get_custom_achievement_by_id(
        self, custom_achievement_id: uuid.UUID
    ) -> CustomAchievementModel:
        return await self.get(custom_achievement_id, CustomAchievementModel)

    async def update_custom_achievement(
        self,
        custom_achievement: CustomAchievementModel,
        update_data: CustomAchievementUpdate,
    ):
        for field, value in update_data.model_dump().items():
            setattr(custom_achievement, field, value)
        return await self.update(custom_achievement)
