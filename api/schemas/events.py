from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
from schemas.users import UserReadShort, UserRole


class EventBase(BaseModel):
    name: str
    date: datetime
    location: str
    link: str | None = None
    organizer: str | None = None


class EventCreateOrUpdate(EventBase):
    photographer_description: str | None = None
    copywriter_description: str | None = None
    designer_description: str | None = None


class TaskBase(BaseModel):
    event_id: Optional[uuid.UUID] = None
    name: str
    due_date: datetime | None = None


class TaskCreate(TaskBase):
    pass


class TaskStateBase(UserReadShort):
    is_completed: bool
    comment: str | None = None

    class Config:
        from_attributes = True


class EventRead(EventBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


class EventReadShort(EventRead):
    photographer: List[TaskStateBase]
    copywriter: TaskStateBase
    designer: TaskStateBase

    class Config:
        from_attributes = True


class TypedTaskRead(BaseModel):
    id: uuid.UUID
    task_type: UserRole
    description: str | None
    for_single_user: bool
    users: List[UserReadShort]


class TaskRead(TaskBase):
    id: uuid.UUID
    event: EventRead
    typed_tasks: List[TypedTaskRead]

    class Config:
        from_attributes = True


class EventFullInfo(EventRead):
    task: TaskRead

    class Config:
        from_attributes = True
