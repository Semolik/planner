from models.events import Task
from schemas.events import EventGroupCreate, EventGroupRead
import uuid
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from cruds.events_crud import EventsCRUD
from cruds.tasks_crud import TasksCRUD
from users_controller import current_superuser
from db.session import get_async_session
from models.user import UserRole

api_router = APIRouter(prefix="/groups", tags=["events groups"])


@api_router.post("", response_model=EventGroupRead)
async def create_event_group(
    event_group: EventGroupCreate,
    session=Depends(get_async_session),
    current_user=Depends(current_superuser),
):
    db_event_group = await EventsCRUD(session).create_event_group(
        name=event_group.name,
        description=event_group.description,
        organizer=event_group.organizer,
        link=event_group.link,
    )
    return await EventsCRUD(session).get_event_group(group_id=db_event_group.id)


@api_router.get("/{group_id}", response_model=EventGroupRead)
async def get_event_group(
    group_id: uuid.UUID = Path(...),
    session=Depends(get_async_session),
    current_user=Depends(current_superuser),
):
    db_group = await EventsCRUD(session).get_event_group(group_id=group_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    return db_group


@api_router.post("/{group_id}/events/{event_id}", status_code=204, dependencies=[Depends(current_superuser)])
async def add_event_to_group(
    group_id: uuid.UUID = Path(...),
    event_id: uuid.UUID = Path(...),
    session=Depends(get_async_session),
):
    if await EventsCRUD(session).event_already_in_group(group_id=group_id, event_id=event_id):
        raise HTTPException(
            status_code=400, detail="Мероприятие уже добавлено в группу")
    await EventsCRUD(session).add_event_to_group(group_id=group_id, event_id=event_id)
