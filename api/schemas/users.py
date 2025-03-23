from datetime import datetime
import uuid
from pydantic import BaseModel, EmailStr
from fastapi_users.schemas import BaseUserCreate
from models.user import UserRole


class BaseUserCustomFields(BaseModel):
    first_name: str
    last_name: str
    patronymic: str | None = None
    vk_username: str | None = None
    birth_date: datetime | None = None
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


class BaseUserEmail(BaseModel):
    email: EmailStr


class UserCreate(BaseUserCustomFields, BaseUserCreate):
    password: str
    institute_id: uuid.UUID


class UserReadShort(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    institute: Institute

    class Config:
        from_attributes = True


class UserReadShortWithEmail(UserReadShort, BaseUserEmail):
    pass


class UserRead(UserReadShortWithEmail, BaseUser):
    created_at: datetime
    updated_at: datetime

    model_config = {
        'exclude': {'phone'}
    }


class UserReadWithEmail(UserRead, BaseUserEmail):
    pass


class UserUpdate(UserCreate, BaseUserEmail):
    password: str | None = None
    institute_id: uuid.UUID | None = None
