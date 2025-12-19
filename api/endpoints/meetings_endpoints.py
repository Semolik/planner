from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException
from api.core.users_controller import current_superuser
from api.cruds.meetings_crud import MeetingsCRUD
from api.db.session import get_async_session
from api.schemas.meetings import MeetingRead, MeetingCreate, MeetingUpdate

api_router = APIRouter(prefix="/meetings", tags=["meetings"])


@api_router.post(
    "", response_model=MeetingRead, dependencies=[Depends(current_superuser)]
)
async def create_meeting(meeting: MeetingCreate, db=Depends(get_async_session)):
    return await MeetingsCRUD(db).create_meeting(meeting)


@api_router.put(
    "/{meeting_id}",
    response_model=MeetingRead,
    dependencies=[Depends(current_superuser)],
)
async def update_meeting(
    meeting: MeetingUpdate, meeting_id: uuid.UUID, db=Depends(get_async_session)
):
    db_meeting = await MeetingsCRUD(db).get_meeting_by_id(meeting_id)
    if db_meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return await MeetingsCRUD(db).update_meeting(
        meeting=db_meeting,
        update_data=meeting,
    )


@api_router.delete(
    "/{meeting_id}", status_code=204, dependencies=[Depends(current_superuser)]
)
async def delete_meeting(meeting_id: uuid.UUID, db=Depends(get_async_session)):
    db_meeting = await MeetingsCRUD(db).get_meeting_by_id(meeting_id)
    if db_meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    await MeetingsCRUD(db).delete(db_meeting)


@api_router.get("/{meeting_id}", response_model=MeetingRead)
async def get_meeting(
    meeting_id: uuid.UUID,
    db=Depends(get_async_session),
):
    db_meeting = await MeetingsCRUD(db).get_meeting_by_id(meeting_id)
    if db_meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return db_meeting


@api_router.get("", response_model=List[MeetingRead])
async def get_meetings(
    db=Depends(get_async_session),
):
    return await MeetingsCRUD(db).get_all_meetings()
