from pydantic import BaseModel

from schemas.files import ImageLink


class SettingsUpdate(BaseModel):
    app_name: str
    photographers_deadline: int
    copywriters_deadline: int
    designers_deadline: int


class Settings(SettingsUpdate):
    app_logo: ImageLink | None = None
