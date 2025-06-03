from sqlalchemy.sql import and_, exists
from sqlalchemy.sql import and_
from datetime import datetime
import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

from cruds.base_crud import BaseCRUD
from models.user_models import User, UserRole
from models.events_models import Event
from models.events_models import Task, TypedTask, TaskState, EventGroup, EventGroupAssociation, EventLevel


class EventsCRUD(BaseCRUD):
    async def create_event(self, name: str, date: datetime, location: str, organizer: str, start_time: datetime, end_time: datetime, name_approved: bool, required_photographers: int, description: str, group_id: uuid.UUID = None, level_id: uuid.UUID = None) -> Event:
        event = Event(
            name=name,
            date=date,
            location=location,
            organizer=organizer,
            start_time=start_time,
            end_time=end_time,
            name_approved=name_approved,
            required_photographers=required_photographers,
            description=description,
            group_id=group_id,
            level_id=level_id
        )
        return await self.create(event)

    async def get_event(self, event_id: uuid.UUID) -> Event:
        query = select(Event).where(Event.id == event_id).options(
            selectinload(Event.task))
        result = await self.db.execute(query)
        return result.scalars().first()

    def _get_full_event_query(self, event_id):
        return (
            select(Event)
            .where(Event.id == event_id)
            .options(
                selectinload(Event.task)
                .selectinload(Task.typed_tasks)
                .selectinload(TypedTask.task_states)
                .selectinload(TaskState.user)
            )
        )

    async def get_full_event(self, event_id: uuid.UUID) -> Event:
        query = self._get_full_event_query(event_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def update_event(self, event: Event, name: str, date: datetime, location: str, organizer: str) -> Event:
        event.name = name
        event.date = date
        event.location = location
        event.organizer = organizer
        return await self.update(event)

    async def create_event_group(self, name: str, description: str = None, organizer: str = None, link: str = None) -> EventGroup:
        event_group = EventGroup(
            name=name,
            description=description,
            organizer=organizer,
            link=link
        )
        return await self.create(event_group)

    def _get_event_group_query(self, group_id):
        return (
            select(EventGroup)
            .where(EventGroup.id == group_id)
            .options(
                selectinload(EventGroup.events)
                .selectinload(Event.task)
                .selectinload(Task.typed_tasks)
                .selectinload(TypedTask.task_states)
                .selectinload(TaskState.user)
            )
        )

    async def get_event_group(self, group_id: uuid.UUID) -> EventGroup:
        query = self._get_event_group_query(group_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def add_event_to_group(self, group_id: uuid.UUID, event_id: uuid.UUID):
        event_group_association = EventGroupAssociation(
            group_id=group_id,
            event_id=event_id
        )
        await self.create(event_group_association)
        return event_group_association

    async def get_event_group_association(self, group_id: uuid.UUID, event_id: uuid.UUID):
        query = select(EventGroupAssociation).where(
            EventGroupAssociation.group_id == group_id,
            EventGroupAssociation.event_id == event_id
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    def _get_event_options(self):
        return (
            joinedload(Event.task)
            .joinedload(Task.typed_tasks)
            .joinedload(TypedTask.task_states)
            .joinedload(TaskState.user)
        )

    def _get_unstaffed_events_query(self, subquery_has_photographers):
        return (
            select(Event)
            .options(self._get_event_options())
            .where(~Event.task.has(subquery_has_photographers))
            .order_by(Event.date)
        )

    def _get_regular_events_query(self, subquery_has_photographers, limit):
        return (
            select(Event)
            .options(self._get_event_options())
            .where(Event.task.has(subquery_has_photographers))
            .order_by(Event.date)
            .limit(limit)
        )

    def _get_paginated_events_query(self, unstaffed_event_ids, offset, limit):
        if unstaffed_event_ids:
            return (
                select(Event)
                .options(self._get_event_options())
                .where(Event.id.not_in(unstaffed_event_ids))
                .order_by(Event.date)
                .offset(offset)
                .limit(limit)
            )
        else:
            return (
                select(Event)
                .options(self._get_event_options())
                .order_by(Event.date)
                .offset(offset)
                .limit(limit)
            )

    async def get_event_levels(self):
        query = select(EventLevel).order_by(EventLevel.order.desc())
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_event_level(self, level_id: uuid.UUID):
        query = select(EventLevel).where(EventLevel.id == level_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_event_level_by_name(self, name: str):
        query = select(EventLevel).where(EventLevel.name == name)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create_event_level(self, name: str, order: int) -> EventLevel:
        event_level = EventLevel(
            name=name,
            order=order
        )
        return await self.create(event_level)

    async def update_event_level(self, level: EventLevel, name: str, order: int) -> EventLevel:
        level.name = name
        level.order = order
        return await self.update(level)

    async def delete_group_events(self, group_id: uuid.UUID):
        query = select(EventGroupAssociation).where(
            EventGroupAssociation.group_id == group_id).options(
                EventGroupAssociation.event)
        result = await self.db.execute(query)
        associations = result.scalars().all()
        for association in associations:
            await self.delete(association)
            await self.delete(association.event)
