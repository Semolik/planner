from datetime import date, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException

from api.cruds.tasks_crud import TasksCRUD
from api.db.session import get_async_session
from api.cruds.users_crud import UsersCRUD
from api.schemas.events import (
    CalendarItem,
    TaskReadShort,
    TypedTaskReadFull,
    EventFullInfo,
)
from api.schemas.users import UserReadShort
from api.models.events_models import Task, TypedTask
from api.models.user_models import User
from api.core.users_controller import current_user
from api.cruds.events_crud import EventsCRUD
from api.models.events_models import Event

api_router = APIRouter(prefix="/calendar", tags=["Calendar"])


@api_router.get(
    "",
    response_model=dict[date, list[CalendarItem]],
    dependencies=[Depends(current_user)],
)
async def get_calendar(
    date_from: date = (date.today() - timedelta(days=date.today().weekday())),
    date_to: date = (date.today() + timedelta(days=6 - date.today().weekday())),
    db=Depends(get_async_session),
):
    if date_from > date_to:
        raise HTTPException(
            status_code=400, detail="date_from не может быть позже date_to"
        )
    tasks = await TasksCRUD(db).get_tasks_by_period(
        date_from=date_from, date_to=date_to
    )
    events = await EventsCRUD(db).get_events_by_period(
        date_from=date_from, date_to=date_to
    )
    typed_tasks = await TasksCRUD(db).get_typed_tasks_by_period(
        date_from=date_from, date_to=date_to
    )
    users = await UsersCRUD(db).get_users_by_birthday_period(
        date_from=date_from, date_to=date_to
    )
    days = {}
    for items in [tasks, typed_tasks, users, events]:
        for item in items:
            item_type: Literal["task", "user", "typed_task", "event"]
            if isinstance(item, User):
                day = item.birth_date.replace(year=date_from.year)
                item_type = "user"
                schema_item = UserReadShort.model_validate(item)
            elif isinstance(item, Task):
                day = item.due_date
                item_type = "task"
                schema_item = TaskReadShort.model_validate(item)
            elif isinstance(item, TypedTask):
                day = item.due_date
                item_type = "typed_task"
                schema_item = TypedTaskReadFull.model_validate(item)
            elif isinstance(item, Event):
                day = item.date
                item_type = "event"
                schema_item = EventFullInfo.model_validate(item)
            else:
                continue
            if day is None:
                continue
            if day not in days:
                days[day] = []
            days[day].append(CalendarItem(item=schema_item, item_type=item_type))
    return days
