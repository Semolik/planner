import uuid

from pydantic import BaseModel
from datetime import date


class AchievementCreate(BaseModel):
    name: str
    date_from: date
    date_to: date | None
    level_of_participation: str | None
    link: str | None
    achievement_level: str | None


class AchievementUpdate(AchievementCreate):
    pass


class AchievementRead(AchievementUpdate):
    id: uuid.UUID
    is_custom: bool = True

    class Config:
        from_attributes = True
