from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import date, time, datetime
import uuid
from api.schemas.files import ImageInfo, File
from api.models.events_models import State
from api.schemas.users import UserReadShort, UserRole
from pydantic import Field

from api.schemas.utils import EmptyStrToNone


class EventBase(BaseModel):
    name: str = Field(..., min_length=1, strip_whitespace=True)
    date: date
    start_time: time | None
    end_time: time | None
    name_approved: bool = False
    location: str
    link: str
    organizer: str
    required_photographers: int
    group_id: Optional[uuid.UUID] = None
    description: str


class EventUpdate(EventBase):
    level_id: uuid.UUID
    use_in_pgas: bool


class PublicationTypedTasksParams(BaseModel):
    copywriter_description: str
    designer_description: str
    copywriters_deadline: date | None = None
    designers_deadline: date | None = None


class EventCreate(EventUpdate, PublicationTypedTasksParams):
    photographers_deadline: date
    photographer_description: str | None = None
    aggregate_task: bool = False


class TaskBase(BaseModel):
    event_id: Optional[uuid.UUID] = None
    name: str
    use_in_pgas: bool


class TaskStateBase(UserReadShort):
    state: State
    comment: str
    period_start: time
    period_end: time

    class Config:
        from_attributes = True


class EventGroupBase(BaseModel):
    name: str = Field(..., min_length=1, strip_whitespace=True)
    description: str
    organizer: str
    link: str


class GroupPublicationTypedTasksParams(PublicationTypedTasksParams):
    copywriters_deadline: date


class EventGroupUpdate(EventGroupBase):
    pass


class EventGroupCreate(EventGroupUpdate):
    aggregate_task_params: GroupPublicationTypedTasksParams | None


class TaskReadShortWithoutEvent(TaskBase):
    id: uuid.UUID
    all_typed_tasks_completed: bool
    name: str | None = None
    displayed_name: str | None = None
    birthday_user: UserReadShort | None = None

    class Config:
        from_attributes = True


class EventGroupReadShort(EventGroupBase):
    id: uuid.UUID
    events_count: int
    period_start: date | None = None
    period_end: date | None = None
    aggregate_task: TaskReadShortWithoutEvent | None = None

    class Config:
        from_attributes = True


class EventRead(EventBase):
    id: uuid.UUID
    level: str
    level_id: uuid.UUID
    is_passed: bool = False
    group: EventGroupReadShort | None = None
    has_assigned_photographers: bool = False

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
    name: EmptyStrToNone
    link: str
    for_single_user: bool
    due_date: date


class CreateTypedTask(UpdateTypedTask):
    task_type: UserRole


class TaskCreate(BaseModel):
    name: str
    typed_tasks: dict[UserRole, UpdateTypedTask | None] = {}
    use_in_pgas: bool


class TypedTaskRead(CreateTypedTask):
    id: uuid.UUID
    task_states: List[TypedTaskState]
    due_date_passed: bool = False
    due_date: datetime
    displayed_name: str | None = None

    class Config:
        from_attributes = True


class TaskReadShort(TaskReadShortWithoutEvent):
    event: EventRead | None = None

    class Config:
        from_attributes = True


class TypedTaskReadFull(TypedTaskRead):
    parent_task: TaskReadShort


class TaskRead(TaskReadShort):
    typed_tasks: List[TypedTaskRead]
    images: List[ImageInfo]
    files: List[File]
    group: EventGroupReadShort | None = None

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


class EventGroupRead(EventGroupReadShort):
    events: List[EventFullInfo]
    aggregate_task: TaskReadShortWithoutEvent | None = None

    class Config:
        from_attributes = True


class EventLevelCreateOrUpdate(BaseModel):
    name: str
    order: int


class EventLevelRead(EventLevelCreateOrUpdate):
    id: uuid.UUID

    class Config:
        from_attributes = True


class CalendarItem(BaseModel):
    item: TypedTaskReadFull | TaskReadShort | UserReadShort | EventFullInfo
    item_type: Literal["task", "user", "typed_task", "event"]

    class Config:
        from_attributes = True
