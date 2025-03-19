from sqlalchemy.sql import and_, exists
from sqlalchemy.sql import and_
from datetime import datetime
import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

from cruds.base_crud import BaseCRUD
from models.user import User, UserRole
from models.events import Event
from models.events import Task, TypedTask, TaskState, EventGroup, EventGroupAssociation


class EventsCRUD(BaseCRUD):
    async def create_event(self, name: str, date: datetime, location: str, organizer: str) -> Event:
        event = Event(
            name=name,
            date=date,
            location=location,
            organizer=organizer,
        )
        return await self.create(event)

    async def get_events(self, page: int = 1, per_page: int = 10, prioritize_unstaffed: bool = True):
        if not prioritize_unstaffed or page > 1:
            # Обычная пагинация без приоритизации
            paginated_query = self._get_paginated_events_query(
                None, (page - 1) * per_page, per_page)
            result = await self.db.execute(paginated_query)
            return result.unique().scalars().all()

        # Подзапрос для проверки наличия исполнителей-фотографов
        subquery_has_photographers = (
            exists()
            .where(
                and_(
                    TypedTask.task_id == Task.id,
                    TypedTask.task_type == UserRole.PHOTOGRAPHER,
                    TaskState.type_task_id == TypedTask.id,
                    TaskState.user_id.is_not(None)
                )
            )
        )

        # Запрос для получения всех неоформленных мероприятий
        unstaffed_query = self._get_unstaffed_events_query(
            subquery_has_photographers)
        result = await self.db.execute(unstaffed_query)
        unstaffed_events = result.unique().scalars().all()

        if len(unstaffed_events) >= per_page:
            # Если неоформленных мероприятий достаточно для заполнения страницы
            return unstaffed_events

        # Если неоформленных мероприятий меньше, чем нужно, дополняем обычными мероприятиями
        remaining_count = per_page - len(unstaffed_events)
        regular_query = self._get_regular_events_query(
            subquery_has_photographers, remaining_count)
        result = await self.db.execute(regular_query)
        regular_events = result.unique().scalars().all()

        return unstaffed_events + regular_events

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

    async def event_already_in_group(self, group_id: uuid.UUID, event_id: uuid.UUID):
        query = select(EventGroupAssociation).where(
            EventGroupAssociation.group_id == group_id,
            EventGroupAssociation.event_id == event_id
        )
        result = await self.db.execute(query)
        return result.scalars().first() is not None

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
