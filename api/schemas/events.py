from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date, time
import uuid
from schemas.users import UserReadShort, UserRole


class EventBase(BaseModel):
    name: str
    date: date
    start_time: time
    end_time: time
    name_approved: bool = False
    location: str
    link: str
    organizer: str
    required_photographers: int
    group_id: Optional[uuid.UUID] = None
    description: str


class EventCreateOrUpdate(EventBase):
    level_id: Optional[uuid.UUID] = None
    photographer_description: str
    copywriter_description: str
    designer_description: str
    days_to_complete_photographers: int
    days_to_complete_copywriters: int
    days_to_complete_designers: int


class TaskBase(BaseModel):
    event_id: Optional[uuid.UUID] = None
    name: str


class TaskCreate(TaskBase):
    pass


class TaskStateBase(UserReadShort):
    is_completed: bool
    comment: str
    period_start: time
    period_end: time

    class Config:
        from_attributes = True


class EventRead(EventBase):
    id: uuid.UUID
    level: str

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
    due_date: datetime | None = None


class TaskReadShortWithoutEvent(TaskBase):
    id: uuid.UUID


class TaskReadShort(TaskReadShortWithoutEvent):
    event: EventRead | None = None

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


class UpdateTypedTaskState(BaseModel):
    is_completed: bool = False
    comment: str
    period_start: time
    period_end: time

    class Config:
        from_attributes = True


class EventLevelCreateOrUpdate(BaseModel):
    name: str
    order: int


class EventLevelRead(EventLevelCreateOrUpdate):
    id: uuid.UUID

    class Config:
        from_attributes = True
