import uuid

from sqlalchemy import select

from api.cruds.base_crud import BaseCRUD
from api.models.meetings_models import MeetingModel
from api.schemas.meetings import MeetingCreate


class MeetingsCRUD(BaseCRUD):
    async def create_meeting(self, meeting: MeetingCreate):
        return await self.create(MeetingModel(**meeting.model_dump()))

    async def get_meeting_by_id(self, meeting_id: uuid.UUID) -> MeetingModel:
        return await self.get(meeting_id, MeetingModel)

    async def update_meeting(self, meeting: MeetingModel, update_data: MeetingCreate):
        for field, value in update_data.model_dump().items():
            setattr(meeting, field, value)
        return await self.update(meeting)

    async def get_all_meetings(self) -> list[MeetingModel]:
        query = await self.db.execute(select(MeetingModel))
        return query.scalars().all()
