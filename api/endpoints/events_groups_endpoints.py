from datetime import timedelta
from typing import Literal

from api.cruds.settings_crud import SettingsCRUD
from api.cruds.tasks_crud import TasksCRUD
from api.models.user_models import UserRole
from api.schemas.events import (
    EventGroupCreate,
    EventGroupRead,
    EventGroupReadShort,
    EventGroupUpdate,
)
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from api.cruds.events_crud import EventsCRUD
from api.core.users_controller import current_superuser, current_user
from api.db.session import get_async_session

api_router = APIRouter(prefix="/events/groups", tags=["events groups"])


@api_router.post(
    "", response_model=EventGroupRead, dependencies=[Depends(current_superuser)]
)
async def create_event_group(
    event_group: EventGroupCreate,
    session=Depends(get_async_session),
):
    task_id = None
    if event_group.aggregate_task_params:
        tasks_crud = TasksCRUD(session)
        task = await tasks_crud.create_task(
            name=f"Освещение группы мероприятий '{event_group.name}'",
            use_in_pgas=True,
        )
        await tasks_crud.create_typed_task(
            task_id=task.id,
            task_type=UserRole.COPYWRITER,
            name=f'Пост по группе мероприятий "{event_group.name}"',
            description=event_group.aggregate_task_params.copywriter_description,
            for_single_user=True,
            due_date=event_group.aggregate_task_params.copywriters_deadline,
        )
        if event_group.aggregate_task_params.designers_deadline:
            await tasks_crud.create_typed_task(
                task_id=task.id,
                name=f'Обложка на общий альбом по группе мероприятий "{event_group.name}"',
                task_type=UserRole.DESIGNER,
                description=event_group.aggregate_task_params.designer_description,
                for_single_user=True,
                due_date=event_group.aggregate_task_params.designers_deadline,
            )
        task_id = task.id
    db_event_group = await EventsCRUD(session).create_event_group(
        name=event_group.name,
        description=event_group.description,
        organizer=event_group.organizer,
        link=event_group.link,
        aggregate_task_id=task_id,
    )
    return await EventsCRUD(session).get_event_group(group_id=db_event_group.id)


@api_router.post(
    "/{group_id}/convert-to-aggregated",
    response_model=EventGroupRead,
    dependencies=[Depends(current_superuser)],
)
async def convert_event_group_to_aggregated(
    group_id: uuid.UUID = Path(...),
    session=Depends(get_async_session),
    is_single_album: bool = Query(...),
):
    db_group = await EventsCRUD(session).get_event_group(group_id=group_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    if db_group.aggregate_task_id is not None:
        raise HTTPException(
            status_code=400, detail="Группа уже является агрегированной"
        )
    tasks_crud = TasksCRUD(session)
    task = await tasks_crud.create_task(
        name=f"Освещение группы мероприятий '{db_group.name}'",
        use_in_pgas=True,
    )
    settings = await SettingsCRUD(session).get_settings()
    await tasks_crud.create_typed_task(
        task_id=task.id,
        task_type=UserRole.COPYWRITER,
        name=f'Пост по группе мероприятий "{db_group.name}"',
        description="Автоматически созданная задача для агрегированной группы мероприятий.",
        for_single_user=True,
        due_date=max(event.date for event in db_group.events)
        + timedelta(days=settings.copywriters_deadline),
    )
    if is_single_album:
        await tasks_crud.create_typed_task(
            task_id=task.id,
            name=f'Обложка на общий альбом по группе мероприятий "{db_group.name}"',
            task_type=UserRole.DESIGNER,
            description="Автоматически созданная задача для агрегированной группы мероприятий.",
            for_single_user=True,
            due_date=max(event.date for event in db_group.events)
            + timedelta(days=settings.designers_deadline),
        )
    for event in db_group.events:
        for typed_task in event.task.typed_tasks:
            if is_single_album and typed_task.task_type == UserRole.DESIGNER:
                await tasks_crud.delete(typed_task)
            elif typed_task.task_type == UserRole.COPYWRITER:
                await tasks_crud.delete(typed_task)
    db_group.aggregate_task_id = task.id
    await session.commit()
    await session.refresh(db_group)
    return await EventsCRUD(session).get_event_group(group_id=group_id)


@api_router.post(
    "/{group_id}/remove-aggregation",
    response_model=EventGroupRead,
    dependencies=[Depends(current_superuser)],
)
async def remove_aggregation_from_event_group(
    group_id: uuid.UUID = Path(...),
    session=Depends(get_async_session),
):
    db_group = await EventsCRUD(session).get_event_group(group_id=group_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    if db_group.aggregate_task_id is None:
        raise HTTPException(status_code=400, detail="Группа не является агрегированной")
    tasks_crud = TasksCRUD(session)
    aggregate_task_id = db_group.aggregate_task_id
    db_group.aggregate_task_id = None
    aggregate_task = await tasks_crud.get_task_by_id(aggregate_task_id)
    await session.delete(aggregate_task)
    settings = await SettingsCRUD(session).get_settings()
    for event in db_group.events:
        typed_tasks = event.task.typed_tasks
        exits_roles_tasks = {typed_task.task_type for typed_task in typed_tasks}
        if UserRole.COPYWRITER not in exits_roles_tasks:
            await tasks_crud.create_typed_task(
                task_id=event.task.id,
                task_type=UserRole.COPYWRITER,
                name=f"Публикация по мероприятию '{event.name}'",
                for_single_user=True,
                due_date=event.date + timedelta(days=settings.copywriters_deadline),
            )
        if UserRole.DESIGNER not in exits_roles_tasks:
            await tasks_crud.create_typed_task(
                task_id=event.task.id,
                task_type=UserRole.DESIGNER,
                name=f"Обложка на общий альбом по мероприятию '{event.name}'",
                for_single_user=True,
                due_date=event.date + timedelta(days=settings.designers_deadline),
            )

    await session.commit()
    await session.refresh(db_group)
    return await EventsCRUD(session).get_event_group(group_id=group_id)


@api_router.get(
    "/search",
    response_model=list[EventGroupReadShort],
    dependencies=[Depends(current_user)],
)
async def search_event_groups(
    query: str = Query(None),
    page: int = Query(1, ge=1),
    filter: Literal["all", "active", "passed"] = Query("all"),
    with_aggregate_task: bool | None = Query(None),
    session=Depends(get_async_session),
):
    db_groups = await EventsCRUD(session).search_event_groups(
        query=query, page=page, filter=filter, with_aggregate_task=with_aggregate_task
    )
    return db_groups


@api_router.get(
    "/{group_id}", response_model=EventGroupRead, dependencies=[Depends(current_user)]
)
async def get_event_group(
    group_id: uuid.UUID = Path(...),
    session=Depends(get_async_session),
):
    db_group = await EventsCRUD(session).get_event_group(group_id=group_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    return db_group


@api_router.delete(
    "/{group_id}", status_code=204, dependencies=[Depends(current_superuser)]
)
async def delete_event_group(
    group_id: uuid.UUID = Path(...),
    remove_events: bool = Query(False),
    session=Depends(get_async_session),
):
    db_group = await EventsCRUD(session).get_event_group(group_id=group_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    if remove_events:
        await EventsCRUD(session).delete_group_events(group_id=group_id)
    await EventsCRUD(session).delete(db_group)


@api_router.put(
    "/{group_id}",
    response_model=EventGroupRead,
    dependencies=[Depends(current_superuser)],
)
async def update_event_group(
    event_group: EventGroupUpdate,
    group_id: uuid.UUID = Path(...),
    session=Depends(get_async_session),
):
    db_group = await EventsCRUD(session).get_event_group(group_id=group_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    updated_group = await EventsCRUD(session).update_event_group(
        event_group=db_group,
        name=event_group.name,
        description=event_group.description,
        organizer=event_group.organizer,
        link=event_group.link,
    )

    return updated_group
