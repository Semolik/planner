from pydantic import BaseModel

from schemas.files import ImageLink


class Setting(BaseModel):
    key: str
    value: str

    class Config:
        from_attributes = True


class SettingCreateOrUpdate(BaseModel):
    key: str
    value: str


class Settings(BaseModel):
    app_logo: ImageLink | None = None
    app_name: str
