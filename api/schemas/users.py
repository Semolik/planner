from datetime import date, datetime
from typing import Optional
import uuid
from pydantic import BaseModel
from fastapi_users.schemas import CreateUpdateDictModel
from models.user_models import UserRole


class BaseUserCustomFields(BaseModel):
    first_name: str
    last_name: str
    patronymic: str | None = None
    vk_id: int | None = None
    birth_date: date | None = None
    phone: str | None = None
    group: str
    roles: list[UserRole] = []


class InstituteCreateOrEdit(BaseModel):
    name: str


class Institute(InstituteCreateOrEdit):
    id: uuid.UUID
    name: str

    class Config:
        from_attributes = True


class BaseUser(BaseUserCustomFields):
    is_active: bool
    is_superuser: bool
    is_verified: bool = True

    class Config:
        from_attributes = True


class BaseUserUsername(BaseModel):
    username: str


class UserCreate(BaseUserUsername, BaseUserCustomFields, CreateUpdateDictModel):
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False
    password: str
    institute_id: uuid.UUID

    class Config:
        exclude = {'email'}


class UserReadShort(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    institute: Institute

    class Config:
        from_attributes = True


class UserReadShortWithEmail(UserReadShort, BaseUserUsername):
    pass


class UserRead(UserReadShortWithEmail, BaseUser):
    created_at: datetime
    updated_at: datetime

    model_config = {
        'exclude': {'phone'}
    }


class UserReadWithEmail(UserRead, BaseUserUsername):
    pass


class UserUpdate(UserCreate, BaseUserUsername):
    password: str | None = None
    institute_id: uuid.UUID | None = None
