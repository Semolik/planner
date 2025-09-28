from typing import Literal
from schemas.events import EventGroupCreate, EventGroupRead, EventGroupReadShort
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from cruds.events_crud import EventsCRUD
from core.users_controller import current_superuser, current_user
from db.session import get_async_session

api_router = APIRouter(prefix="/events/groups", tags=["events groups"])


@api_router.post(
    "", response_model=EventGroupRead, dependencies=[Depends(current_superuser)]
)
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


@api_router.get(
    "/search",
    response_model=list[EventGroupReadShort],
    dependencies=[Depends(current_user)],
)
async def search_event_groups(
    query: str = Query(None),
    page: int = Query(1, ge=1),
    filter: Literal["all", "active", "passed"] = Query("all"),
    session=Depends(get_async_session),
):
    db_groups = await EventsCRUD(session).search_event_groups(
        query=query, page=page, filter=filter
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
    event_group: EventGroupCreate,
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
