from api.schemas.events import EventLevelCreateOrUpdate, EventLevelRead
import uuid
from fastapi import APIRouter, Depends, HTTPException, Path
from api.cruds.events_crud import EventsCRUD
from api.core.users_controller import current_superuser
from api.db.session import get_async_session

api_router = APIRouter(prefix="/events/levels", tags=["events levels"])


@api_router.get("", response_model=list[EventLevelRead])
async def get_event_levels(
    db=Depends(get_async_session),
):
    return await EventsCRUD(db).get_event_levels()


@api_router.post(
    "", response_model=EventLevelRead, dependencies=[Depends(current_superuser)]
)
async def create_event_level(
    event_level: EventLevelCreateOrUpdate,
    session=Depends(get_async_session),
):
    existing_level = await EventsCRUD(session).get_event_level_by_name(
        name=event_level.name
    )
    if existing_level is not None:
        raise HTTPException(
            status_code=400, detail="Уровень мероприятия с таким именем уже существует"
        )
    db_event_level = await EventsCRUD(session).create_event_level(
        name=event_level.name, order=event_level.order
    )
    return db_event_level


@api_router.put(
    "/{level_id}",
    response_model=EventLevelRead,
    dependencies=[Depends(current_superuser)],
)
async def update_event_level(
    event_level: EventLevelCreateOrUpdate,
    level_id: uuid.UUID = Path(...),
    session=Depends(get_async_session),
):
    db_level = await EventsCRUD(session).get_event_level(level_id=level_id)
    if db_level is None:
        raise HTTPException(status_code=404, detail="Уровень не найден")
    return await EventsCRUD(session).update_event_level(
        level=db_level, name=event_level.name, order=event_level.order
    )


@api_router.delete(
    "/{level_id}", status_code=204, dependencies=[Depends(current_superuser)]
)
async def delete_event_level(
    level_id: uuid.UUID = Path(...),
    session=Depends(get_async_session),
):
    db_level = await EventsCRUD(session).get_event_level(level_id=level_id)
    if db_level is None:
        raise HTTPException(status_code=404, detail="Уровень не найден")
    await EventsCRUD(session).delete(db_level)
