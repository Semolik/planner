import uuid
from datetime import date

from pydantic import BaseModel, Field

from models.user_models import UserRole


class RoleConfig(BaseModel):
    user_role: UserRole
    count: int

    class Config:
        from_attributes = True


class RequiredPeriod(BaseModel):
    id: uuid.UUID
    period_start: date
    period_end: date
    roles_config: list[RoleConfig]

    class Config:
        from_attributes = True

class CreateOrUpdatePeriodRequest(BaseModel):
    period_start: date
    period_end: date
    photographers_count: int = Field(..., ge=0)
    designers_count: int = Field(..., ge=0)
    copywriters_count: int = Field(..., ge=0)
