import uuid
from pydantic import BaseModel
from core.config import settings

from schemas.files import ImageLink


class SettingsUpdate(BaseModel):
    app_name: str
    photographers_deadline: int = settings.PHOTOGRAPHERS_DEADLINE_DEFAULT
    copywriters_deadline: int = settings.COPYWRITERS_DEADLINE_DEFAULT
    designers_deadline: int = settings.DESIGNERS_DEADLINE_DEFAULT
    default_event_level_id: uuid.UUID | None = None


class Settings(SettingsUpdate):
    app_logo: ImageLink | None = None
