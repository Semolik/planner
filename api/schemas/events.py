from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
from schemas.users import UserReadShort, UserRole


class EventBase(BaseModel):
    name: str
    date: datetime
    location: str
    link: str
    organizer: str


class EventCreateOrUpdate(EventBase):
    photographer_description: str
    copywriter_description: str
    designer_description: str


class TaskBase(BaseModel):
    event_id: Optional[uuid.UUID] = None
    name: str
    due_date: datetime | None = None


class TaskCreate(TaskBase):
    pass


class TaskStateBase(UserReadShort):
    is_completed: bool
    comment: str

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


class TypedTaskState(BaseModel):
    user: UserReadShort
    is_completed: bool
    comment: str

    class Config:
        from_attributes = True


class TypedTaskRead(BaseModel):
    id: uuid.UUID
    task_type: UserRole
    description: str
    link: str
    for_single_user: bool
    task_states: List[TypedTaskState]


class TaskReadShortWithoutEvent(TaskBase):
    id: uuid.UUID


class TaskReadShort(TaskReadShortWithoutEvent):
    event: EventRead

    class Config:
        from_attributes = True


class TypedTaskReadFull(TypedTaskRead):
    parent_task: TaskReadShort


class TaskRead(TaskReadShort):
    typed_tasks: List[TypedTaskRead]

    class Config:
        from_attributes = True


class TaskWithoutEventRead(TaskReadShortWithoutEvent):
    typed_tasks: List[TypedTaskRead]

    class Config:
        from_attributes = True


class EventFullInfo(EventRead):
    task: TaskWithoutEventRead

    class Config:
        from_attributes = True


class EventGroupBase(BaseModel):
    name: str
    description: str
    organizer: str
    link: str


class EventGroupCreate(EventGroupBase):
    pass


class EventGroupRead(EventGroupBase):
    id: uuid.UUID
    events: List[EventFullInfo]

    class Config:
        from_attributes = True
