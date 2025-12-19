import uuid

from pydantic import BaseModel
from datetime import date


class CustomAchievementCreate(BaseModel):
    name: str
    date_from: date
    date_to: date | None
    level_of_participation: str | None
    link: str | None
    achievement_level: str | None


class CustomAchievementUpdate(CustomAchievementCreate):
    pass


class CustomAchievementRead(CustomAchievementUpdate):
    id: uuid.UUID

    class Config:
        from_attributes = True
