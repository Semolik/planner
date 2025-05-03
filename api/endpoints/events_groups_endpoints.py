from schemas.events import EventGroupCreate, EventGroupRead
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from cruds.events_crud import EventsCRUD
from core.users_controller import current_superuser, current_user
from db.session import get_async_session

api_router = APIRouter(prefix="/events/groups", tags=["events groups"])


@api_router.post("", response_model=EventGroupRead, dependencies=[Depends(current_superuser)])
async def create_event_group(
    event_group: EventGroupCreate,
    session=Depends(get_async_session),
):
    db_event_group = await EventsCRUD(session).create_event_group(
        name=event_group.name,
        description=event_group.description,
        organizer=event_group.organizer,
        link=event_group.link,
    )
    return await EventsCRUD(session).get_event_group(group_id=db_event_group.id)


@api_router.get("/{group_id}", response_model=EventGroupRead, dependencies=[Depends(current_user)])
async def get_event_group(
    group_id: uuid.UUID = Path(...),
    session=Depends(get_async_session),
):
    db_group = await EventsCRUD(session).get_event_group(group_id=group_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    return db_group


@api_router.delete("/{group_id}", status_code=204, dependencies=[Depends(current_superuser)])
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


@api_router.post("/{group_id}/events/{event_id}", status_code=204, dependencies=[Depends(current_superuser)])
async def add_event_to_group(
    group_id: uuid.UUID = Path(...),
    event_id: uuid.UUID = Path(...),

    session=Depends(get_async_session),
):
    if await EventsCRUD(session).get_event_group_association(group_id=group_id, event_id=event_id):
        raise HTTPException(
            status_code=400, detail="Мероприятие уже добавлено в группу")
    await EventsCRUD(session).add_event_to_group(group_id=group_id, event_id=event_id)


@api_router.delete("/{group_id}/events/{event_id}", status_code=204, dependencies=[Depends(current_superuser)])
async def remove_event_from_group(
    group_id: uuid.UUID = Path(...),
    event_id: uuid.UUID = Path(...),
    session=Depends(get_async_session),
):
    event_group_association = await EventsCRUD(session).get_event_group_association(group_id=group_id, event_id=event_id)
    if event_group_association is None:
        raise HTTPException(
            status_code=404, detail="Мероприятие не найдено в группе")
    await EventsCRUD(session).delete(event_group_association)
