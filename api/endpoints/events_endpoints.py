from io import BytesIO

from starlette.responses import StreamingResponse
from docx import Document
from docx.shared import Pt
from api.schemas.events import (
    EventFullInfo,
    EventCreate,
    EventUpdate,
)
import uuid
from fastapi import APIRouter, Depends, HTTPException
from api.cruds.events_crud import EventsCRUD
from api.cruds.tasks_crud import TasksCRUD
from api.core.users_controller import current_superuser, current_user
from api.db.session import get_async_session
from api.models.user_models import UserRole

api_router = APIRouter(prefix="/events", tags=["events"])


@api_router.get("/actual", response_model=list[EventFullInfo])
async def get_actual_events(db=Depends(get_async_session)):
    """
    Получить список актуальных мероприятий.
    """
    events = await EventsCRUD(db).get_actual_events()
    return events


@api_router.get(
    "/export",
    dependencies=[Depends(current_superuser)],
    response_model=list[EventFullInfo],
)
async def export_events(year: int, db=Depends(get_async_session)):
    events = await EventsCRUD(db).get_events_by_year(year)
    return events


@api_router.get(
    "/export/excluded",
    dependencies=[Depends(current_superuser)],
    response_model=list[EventFullInfo],
)
async def export_excluded_events(year: int, db=Depends(get_async_session)):
    events = await EventsCRUD(db).get_events_excluded_by_year(year)
    return events


def render_events_docx(events, show_level: bool = True) -> BytesIO:
    """
    Генерирует DOCX-файл с мероприятиями. Если show_level=True, выводит уровень мероприятия после даты.
    Форматирует текст: 1.5 интервал, 14 кегль, Times New Roman.
    Сортирует события по дате в Python.
    """
    events = sorted(events, key=lambda e: e.date)
    doc = Document()
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Times New Roman"
    font.size = Pt(14)
    for event in events:
        date_str = event.date.strftime("%d.%m.%Y")
        level_str = (
            f", уровень мероприятия - {event.level}"
            if show_level and getattr(event, "level", None)
            else ""
        )
        text = f"{event.name} ({date_str}){level_str}"
        p = doc.add_paragraph(text, style="List Number")
        p_format = p.paragraph_format
        p_format.line_spacing = 1.5
    file_stream = BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream


@api_router.get("/export/docx", dependencies=[Depends(current_superuser)])
async def export_events_docx(
    year: int, db=Depends(get_async_session), show_level: bool = True
):
    events = await EventsCRUD(db).get_events_by_year(year)
    file_stream = render_events_docx(events, show_level=show_level)
    filename = f"events_{year}.docx"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )


@api_router.get("/export/excluded/docx", dependencies=[Depends(current_superuser)])
async def export_excluded_events_docx(
    year: int, db=Depends(get_async_session), show_level: bool = True
):
    events = await EventsCRUD(db).get_events_excluded_by_year(year)
    file_stream = render_events_docx(events, show_level=show_level)
    filename = f"excluded_events_{year}.docx"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )


@api_router.post(
    "", response_model=EventFullInfo, dependencies=[Depends(current_superuser)]
)
async def create_event(event: EventCreate, db=Depends(get_async_session)):
    if (
        (event.start_time is not None)
        and (event.end_time is not None)
        and event.start_time > event.end_time
    ):
        raise HTTPException(
            status_code=400, detail="Время начала не может быть позже времени окончания"
        )
    if event.required_photographers < 1:
        raise HTTPException(
            status_code=400, detail="Количество фотографов должно быть больше 0"
        )

    if event.group_id is not None:
        group = await EventsCRUD(db).get_event_group(event.group_id)
        if group is None:
            raise HTTPException(status_code=404, detail="Группа мероприятий не найдена")
        if event.aggregate_task:
            if group.aggregate_task_id is None:
                raise HTTPException(
                    status_code=400,
                    detail="Группа мероприятий не имеет агрегированной задачи",
                )
            if event.copywriters_deadline or event.designers_deadline:
                raise HTTPException(
                    status_code=400,
                    detail="Нельзя задать дедлайны для копирайтеров и дизайнеров при создании мероприятия с агрегированной задачей",
                )

    elif event.aggregate_task:
        raise HTTPException(
            status_code=400,
            detail="Нельзя создать мероприятие с агрегированной задачей без группы мероприятий",
        )
    level = await EventsCRUD(db).get_event_level(level_id=event.level_id)
    if level is None:
        raise HTTPException(status_code=404, detail="Уровень мероприятия не найден")
    db_event = await EventsCRUD(db).create_event(
        name=event.name,
        date=event.date,
        location=event.location,
        organizer=event.organizer,
        start_time=event.start_time,
        end_time=event.end_time,
        link=event.link,
        name_approved=event.name_approved,
        required_photographers=event.required_photographers,
        description=event.description,
        group_id=event.group_id,
        level_id=event.level_id,
    )

    task = await TasksCRUD(db).create_task(
        name="Освещение мероприятия",
        event_id=db_event.id,
        use_in_pgas=True,
    )
    if not event.aggregate_task:
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
    await TasksCRUD(db).create_typed_task(
        task_id=task.id,
        task_type=UserRole.PHOTOGRAPHER,
        description=event.photographer_description,
        name=f"Съемка мероприятия '{db_event.name}'",
        for_single_user=False,
        due_date=event.photographers_deadline,
    )

    return await EventsCRUD(db).get_full_event(db_event.id)


@api_router.get(
    "/token", response_model=uuid.UUID, dependencies=[Depends(current_superuser)]
)
async def get_events_token(db=Depends(get_async_session)):
    str_token = await TasksCRUD(db).get_tasks_token(role=UserRole.PHOTOGRAPHER)
    return uuid.UUID(str_token)


@api_router.get(
    "/{event_id}", response_model=EventFullInfo, dependencies=[Depends(current_user)]
)
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


@api_router.put(
    "/{event_id}",
    response_model=EventFullInfo,
    dependencies=[Depends(current_superuser)],
)
async def update_event(
    event_id: uuid.UUID, event: EventUpdate, db=Depends(get_async_session)
):
    db_event = await EventsCRUD(db).get_full_event(event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")
    db_level = await EventsCRUD(db).get_event_level(level_id=event.level_id)
    if db_level is None:
        raise HTTPException(status_code=404, detail="Уровень мероприятия не найден")
    if event.required_photographers < 1:
        raise HTTPException(
            status_code=400, detail="Количество фотографов должно быть больше 0"
        )
    if (
        event.start_time is not None
        and event.end_time is not None
        and event.start_time > event.end_time
    ):
        raise HTTPException(
            status_code=400, detail="Время начала не может быть позже времени окончания"
        )
    # Проверяем, переносится ли мероприятие в агрегированную группу
    old_group_id = db_event.group_id

    if event.group_id is not None:
        group = await EventsCRUD(db).get_event_group(event.group_id)
        if group is None:
            raise HTTPException(status_code=404, detail="Группа мероприятий не найдена")

        # Проверяем, агрегированная ли новая группа
        if group.aggregate_task_id is not None:
            # Если группа изменилась и новая группа агрегированная, удаляем подзадачи копирайтера
            if old_group_id != event.group_id:
                # Получаем подзадачи текущего мероприятия
                task = db_event.task
                if task and task.typed_tasks:
                    tasks_crud = TasksCRUD(db)

                    aggregate_task = group.aggregate_task
                    has_aggregate_designer = (
                        any(
                            t.task_type == UserRole.DESIGNER
                            for t in aggregate_task.typed_tasks
                        )
                        if aggregate_task and aggregate_task.typed_tasks
                        else False
                    )

                    # Удаляем задачи копирайтера
                    for typed_task in list(task.typed_tasks):
                        if typed_task.task_type == UserRole.COPYWRITER:
                            await tasks_crud.delete(typed_task)

                    # Удаляем задачи дизайнера, если группа с общим альбомом
                    if has_aggregate_designer:
                        for typed_task in list(task.typed_tasks):
                            if typed_task.task_type == UserRole.DESIGNER:
                                await tasks_crud.delete(typed_task)

    db_event = await EventsCRUD(db).update_event(
        event=db_event,
        name=event.name,
        date=event.date,
        exclude_admin_report=event.exclude_admin_report,
        location=event.location,
        organizer=event.organizer,
        start_time=event.start_time,
        end_time=event.end_time,
        name_approved=event.name_approved,
        required_photographers=event.required_photographers,
        description=event.description,
        level_id=event.level_id,
        group_id=event.group_id,
        link=event.link,
    )
    if db_event.task.use_in_pgas != event.use_in_pgas:
        db_event.task.use_in_pgas = event.use_in_pgas
        await db.commit()
    return await EventsCRUD(db).get_full_event(db_event.id)


@api_router.delete(
    "/{event_id}", status_code=204, dependencies=[Depends(current_superuser)]
)
async def delete_event(event_id: uuid.UUID, db=Depends(get_async_session)):
    db_event = await EventsCRUD(db).get_event(event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")
    await EventsCRUD(db).delete(db_event)
