from datetime import datetime
import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from cruds.base_crud import BaseCRUD
from models.user import User
from models.events import Event
from models.events import Task, TypedTask, TaskState


class EventsCRUD(BaseCRUD):
    async def create_event(self, name: str, date: datetime, location: str, organizer: str) -> Event:
        event = Event(
            name=name,
            date=date,
            location=location,
            organizer=organizer,
        )
        return await self.create(event)

    async def get_event(self, event_id: uuid.UUID) -> Event:
        query = select(Event).where(Event.id == event_id).options(
            selectinload(Event.users), selectinload(Event.task))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_full_event(self, event_id: uuid.UUID) -> Event:
        query = select(Event).where(Event.id == event_id).options(
            selectinload(Event.task).selectinload(Task.typed_tasks).selectinload(TypedTask.users))
        result = await self.db.execute(query)
        return result.scalars().first()
