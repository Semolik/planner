from models.events_models import Task
from schemas.events import EventFullInfo, EventCreate, EventUpdate
import uuid
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from cruds.events_crud import EventsCRUD
from cruds.tasks_crud import TasksCRUD
from core.users_controller import current_superuser, current_user
from db.session import get_async_session
from models.user_models import UserRole

api_router = APIRouter(prefix="/events", tags=["events"])


@api_router.post("", response_model=EventFullInfo, dependencies=[Depends(current_superuser)])
async def create_event(event: EventCreate, db=Depends(get_async_session)):
    if event.start_time > event.end_time:
        raise HTTPException(
            status_code=400, detail="Время начала не может быть позже времени окончания")
    if event.required_photographers < 1:
        raise HTTPException(
            status_code=400, detail="Количество фотографов должно быть больше 0")

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

    task = await TasksCRUD(db).create_task(
        name="Освещение мероприятия",
        event_id=db_event.id,
    )
    if event.photographers_deadline:
        await TasksCRUD(db).create_typed_task(
            task_id=task.id,
            task_type=UserRole.PHOTOGRAPHER,
            description=event.photographer_description,
            for_single_user=False,
            due_date=event.photographers_deadline,
        )
    if event.copywriters_deadline:
        await TasksCRUD(db).create_typed_task(
            task_id=task.id,
            task_type=UserRole.COPYWRITER,
            description=event.copywriter_description,
            for_single_user=True,
            due_date=event.copywriters_deadline,
        )
    if event.designers_deadline:
        await TasksCRUD(db).create_typed_task(
            task_id=task.id,
            task_type=UserRole.DESIGNER,
            description=event.designer_description,
            for_single_user=True,
            due_date=event.designers_deadline,
        )

    return await EventsCRUD(db).get_full_event(db_event.id)


@api_router.get("/token", response_model=uuid.UUID, dependencies=[Depends(current_superuser)])
async def get_events_token(db=Depends(get_async_session)):
    str_token = await TasksCRUD(db).get_tasks_token(role=UserRole.PHOTOGRAPHER)
    return uuid.UUID(str_token)


@api_router.get("/{event_id}", response_model=EventFullInfo, dependencies=[Depends(current_user)])
async def get_event(event_id: uuid.UUID, db=Depends(get_async_session)):
    db_event = await EventsCRUD(db).get_full_event(event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")
    return db_event


@api_router.get("/{event_id}/history")
async def get_event_history(event_id: uuid.UUID, db=Depends(get_async_session)):
    db_event = await EventsCRUD(db).get_full_event(event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")
    return await db_event.get_audit_history(session=db)


@api_router.put("/{event_id}", response_model=EventFullInfo, dependencies=[Depends(current_superuser)])
async def update_event(event_id: uuid.UUID, event: EventUpdate, db=Depends(get_async_session)):
    db_event = await EventsCRUD(db).get_full_event(event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")
    db_level = await EventsCRUD(db).get_event_level(level_id=event.level_id)
    if db_level is None:
        raise HTTPException(
            status_code=404, detail="Уровень мероприятия не найден")
    if event.required_photographers < 1:
        raise HTTPException(
            status_code=400, detail="Количество фотографов должно быть больше 0")
    if event.start_time > event.end_time:
        raise HTTPException(
            status_code=400, detail="Время начала не может быть позже времени окончания")
    if event.group_id is not None:
        group = await EventsCRUD(db).get_event_group(event.group_id)
        if group is None:
            raise HTTPException(
                status_code=404, detail="Группа мероприятий не найдена")

    db_event = await EventsCRUD(db).update_event(
        event=db_event,
        name=event.name,
        date=event.date,
        location=event.location,
        organizer=event.organizer,
        start_time=event.start_time,
        end_time=event.end_time,
        name_approved=event.name_approved,
        required_photographers=event.required_photographers,
        description=event.description,
        level_id=event.level_id,
        group_id=event.group_id
    )
    return await EventsCRUD(db).get_full_event(db_event.id)


@api_router.delete("/{event_id}", status_code=204, dependencies=[Depends(current_superuser)])
async def delete_event(event_id: uuid.UUID, db=Depends(get_async_session)):
    db_event = await EventsCRUD(db).get_event(event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")
    await EventsCRUD(db).delete(db_event)
