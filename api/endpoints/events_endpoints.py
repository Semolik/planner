from models.events import Task
from schemas.events import EventFullInfo, EventCreateOrUpdate
import uuid
from datetime import timedelta
from typing import Annotated, Union
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from cruds.events_crud import EventsCRUD
from cruds.tasks_crud import TasksCRUD
from cruds.settings_crud import SettingsCRUD
from users_controller import current_superuser, current_active_user, optional_current_user
from db.session import get_async_session
from models.user import UserRole
from endpoints.events_groups_endpoints import api_router as groups_router
from endpoints.events_levels import api_router as levels_router

api_router = APIRouter(prefix="/events", tags=["events"])


@api_router.post("", response_model=EventFullInfo, dependencies=[Depends(current_superuser)])
async def create_event(event: EventCreateOrUpdate, db=Depends(get_async_session)):
    if event.start_time > event.end_time:
        raise HTTPException(
            status_code=400, detail="Время начала не может быть позже времени окончания")
    if event.required_photographers < 1:
        raise HTTPException(
            status_code=400, detail="Количество фотографов должно быть больше 0")
    if event.days_to_complete_copywriters < 1:
        raise HTTPException(
            status_code=400, detail="Количество дней на выполнение задания для копирайтеров должно быть больше 0")
    if event.days_to_complete_designers < 1:
        raise HTTPException(
            status_code=400, detail="Количество дней на выполнение задания для дизайнеров должно быть больше 0")
    if event.days_to_complete_photographers < 1:
        raise HTTPException(
            status_code=400, detail="Количество дней на выполнение задания для фотографов должно быть больше 0")
    if event.group_id is not None:
        group = await EventsCRUD(db).get_event_group(event.group_id)
        if group is None:
            raise HTTPException(
                status_code=404, detail="Группа мероприятий не найдена")
    level = await EventsCRUD(db).get_event_level(level_id=event.level_id)
    if level is None:
        raise HTTPException(
            status_code=404, detail="Уровень мероприятия не найден")
    db_event = await EventsCRUD(db).create_event(
        name=event.name,
        date=event.date,
        location=event.location,
        organizer=event.organizer,
        start_time=event.start_time,
        end_time=event.end_time,
        name_approved=event.name_approved,
        required_photographers=event.required_photographers,
        description=event.description,
        group_id=event.group_id,
        level_id=event.level_id
    )
    if event.group_id is not None:
        await EventsCRUD(db).add_event_to_group(group_id=event.group_id, event_id=db_event.id)

    due_date = event.date + \
        timedelta(days=event.days_to_complete_photographers)
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


@api_router.get("/token", response_model=uuid.UUID, dependencies=[Depends(current_superuser)])
async def get_events_token(db=Depends(get_async_session)):
    str_token = await TasksCRUD(db).get_tasks_token(role=UserRole.PHOTOGRAPHER)
    return uuid.UUID(str_token)


@api_router.get("/{event_id}", response_model=EventFullInfo, dependencies=[Depends(current_active_user)])
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
