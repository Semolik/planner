from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date, time
import uuid
from models.events_models import State
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


class EventUpdate(EventBase):
    level_id: uuid.UUID


class EventCreate(EventUpdate):
    photographer_description: str
    copywriter_description: str
    designer_description: str
    photographers_deadline: date | None = None
    copywriters_deadline: date | None = None
    designers_deadline: date | None = None


class TaskBase(BaseModel):
    event_id: Optional[uuid.UUID] = None
    name: str


class TaskCreate(TaskBase):
    pass


class TaskStateBase(UserReadShort):
    state: State
    comment: str
    period_start: time
    period_end: time

    class Config:
        from_attributes = True


class EventRead(EventBase):
    id: uuid.UUID
    level: str
    level_id: uuid.UUID
    is_passed: bool = False

    class Config:
        from_attributes = True


class EventReadShort(EventRead):
    photographer: List[TaskStateBase]
    copywriter: TaskStateBase
    designer: TaskStateBase

    class Config:
        from_attributes = True


class StatePeriod(BaseModel):
    period_start: time
    period_end: time

    class Config:
        from_attributes = True


class CreateTypedTaskState(BaseModel):
    comment: str


class UpdateTypedTaskState(CreateTypedTaskState):
    state: State

    class Config:
        from_attributes = True


class TypedTaskState(UpdateTypedTaskState):
    id: uuid.UUID
    user: UserReadShort
    period: StatePeriod | None = None

    class Config:
        from_attributes = True


class UpdateTypedTask(BaseModel):
    description: str
    link: str
    for_single_user: bool
    due_date: datetime


class CreateTypedTask(UpdateTypedTask):
    task_type: UserRole


class TaskCreate(BaseModel):
    name: str
    typed_tasks: dict[UserRole, UpdateTypedTask | None] = {}


class TypedTaskRead(CreateTypedTask):
    id: uuid.UUID
    task_states: List[TypedTaskState]


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


class EventLevelCreateOrUpdate(BaseModel):
    name: str
    order: int


class EventLevelRead(EventLevelCreateOrUpdate):
    id: uuid.UUID

    class Config:
        from_attributes = True
