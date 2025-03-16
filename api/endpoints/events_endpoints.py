from models.events import Task
from schemas.events import EventFullInfo, EventCreateOrUpdate
import uuid
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from cruds.events_crud import EventsCRUD
from cruds.tasks_crud import TasksCRUD
from users_controller import current_superuser
from db.session import get_async_session
from models.user import UserRole

api_router = APIRouter(prefix="/events", tags=["events"])


@api_router.post("", response_model=EventFullInfo, dependencies=[Depends(current_superuser)])
async def create_event(event: EventCreateOrUpdate, db=Depends(get_async_session)):
    db_event = await EventsCRUD(db).create_event(
        name=event.name,
        date=event.date,
        location=event.location,
        organizer=event.organizer,
    )
    due_date = event.date.replace(
        hour=23, minute=59, second=59) + timedelta(days=3)
    task = await TasksCRUD(db).create_task(
        name="Освещение мероприятия",
        due_date=due_date,
        event_id=db_event.id,
    )
    await TasksCRUD(db).create_typed_task(
        task_id=task.id,
        task_type=UserRole.PHOTOGRAPHER,
        description=event.photographer_description,
        for_single_user=False,
    )
    await TasksCRUD(db).create_typed_task(
        task_id=task.id,
        task_type=UserRole.COPYWRITER,
        description=event.copywriter_description,
        for_single_user=True,
    )
    await TasksCRUD(db).create_typed_task(
        task_id=task.id,
        task_type=UserRole.DESIGNER,
        description=event.designer_description,
        for_single_user=True,
    )
    db_event = await EventsCRUD(db).get_full_event(db_event.id)
    task: Task = db_event.task

    return db_event


@api_router.get("/{event_id}", response_model=EventFullInfo)
async def get_event(event_id: uuid.UUID, db=Depends(get_async_session)):
    db_event = await EventsCRUD(db).get_full_event(event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")
    return db_event


@api_router.put("/{event_id}", response_model=EventFullInfo, dependencies=[Depends(current_superuser)])
async def update_event(event_id: uuid.UUID, event: EventCreateOrUpdate, db=Depends(get_async_session)):
    db_event = await EventsCRUD(db).get_full_event(event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")
    db_event = await EventsCRUD(db).update_event(
        event=db_event,
        name=event.name,
        date=event.date,
        location=event.location,
        organizer=event.organizer,
    )
    return db_event


@api_router.delete("/{event_id}", status_code=204, dependencies=[Depends(current_superuser)])
async def delete_event(event_id: uuid.UUID, db=Depends(get_async_session)):
    db_event = await EventsCRUD(db).get_event(event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")
    await EventsCRUD(db).delete(db_event)
