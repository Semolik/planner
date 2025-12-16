from typing import Literal
from sqlalchemy.sql import and_
from datetime import date, datetime, time
import uuid

from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import selectinload

from api.cruds.tasks_crud import TasksCRUD
from api.cruds.base_crud import BaseCRUD
from api.models.user_models import User, UserRole
from api.models.events_models import Event, State
from api.models.events_models import Task, TypedTask, TaskState, EventGroup, EventLevel


class EventsCRUD(BaseCRUD):
    async def create_event(
        self,
        name: str,
        date: date,
        location: str,
        organizer: str,
        start_time: time,
        end_time: time,
        name_approved: bool,
        required_photographers: int,
        description: str,
        group_id: uuid.UUID = None,
        level_id: uuid.UUID = None,
        link: str = "",
    ) -> Event:
        event = Event(
            name=name,
            date=date,
            location=location,
            organizer=organizer,
            start_time=start_time,
            link=link,
            end_time=end_time,
            name_approved=name_approved,
            required_photographers=required_photographers,
            description=description,
            group_id=group_id,
            level_id=level_id,
        )
        return await self.create(event)

    async def get_event(self, event_id: uuid.UUID) -> Event:
        query = (
            select(Event).where(Event.id == event_id).options(selectinload(Event.task))
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    def _get_full_event_query(self, event_id):
        return (
            select(Event)
            .where(Event.id == event_id)
            .options(
                selectinload(Event.task)
                .selectinload(Task.typed_tasks)
                .options(*TasksCRUD(self.db).get_typed_task_options())
            )
        )

    async def get_full_event(self, event_id: uuid.UUID) -> Event:
        query = self._get_full_event_query(event_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def update_event(
        self,
        event: Event,
        name: str,
        date: datetime,
        location: str,
        organizer: str,
        level_id: uuid.UUID,
        start_time: time,
        end_time: time = None,
        name_approved: bool = False,
        required_photographers: int = 0,
        description: str = "",
        group_id: uuid.UUID = None,
        link: str = "",
    ) -> Event:
        event.name = name
        event.date = date
        event.location = location
        event.organizer = organizer
        event.start_time = start_time
        event.end_time = end_time if end_time else start_time
        event.name_approved = name_approved
        event.required_photographers = required_photographers
        event.description = description
        event.level_id = level_id
        event.link = link
        event.group_id = group_id
        return await self.update(event)

    async def create_event_group(
        self,
        name: str,
        description: str = None,
        organizer: str = None,
        link: str = None,
        aggregate_task_id: uuid.UUID | None = None,
    ) -> EventGroup:
        event_group = EventGroup(
            name=name,
            description=description,
            organizer=organizer,
            link=link,
            aggregate_task_id=aggregate_task_id,
        )
        return await self.create(event_group)

    def _get_event_group_query(self, group_id):
        return (
            select(EventGroup)
            .where(EventGroup.id == group_id)
            .options(
                selectinload(EventGroup.events).options(self._get_event_options()),
                selectinload(EventGroup.aggregate_task).selectinload(Task.typed_tasks),
            )
        )

    async def get_event_group(self, group_id: uuid.UUID) -> EventGroup:
        query = self._get_event_group_query(group_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    def _get_event_options(self):
        return (
            selectinload(Event.task)
            .selectinload(Task.typed_tasks)
            .selectinload(TypedTask.task_states)
            .options(
                selectinload(TaskState.period),
                selectinload(TaskState.user).options(selectinload(User.institute)),
            )
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
        event_level = EventLevel(name=name, order=order)
        return await self.create(event_level)

    async def update_event_level(
        self, level: EventLevel, name: str, order: int
    ) -> EventLevel:
        level.name = name
        level.order = order
        return await self.update(level)

    async def delete_group_events(self, group_id: uuid.UUID):
        query = delete(Event).where(Event.group_id == group_id)
        await self.db.execute(query)

    async def search_event_groups(
        self,
        query: str | None,
        page: int = 1,
        per_page: int = 10,
        filter: Literal["all", "active", "passed"] = "all",
        with_aggregate_task: bool | None = None,
    ) -> list[EventGroup]:
        end = page * per_page
        start = end - per_page
        search_query = select(EventGroup)

        if query:
            search_query = search_query.where(EventGroup.name.ilike(f"%{query}%"))
        if with_aggregate_task is not None:
            if with_aggregate_task:
                search_query = search_query.where(
                    EventGroup.aggregate_task_id.isnot(None)
                )
            else:
                search_query = search_query.where(
                    EventGroup.aggregate_task_id.is_(None)
                )
        search_query = (
            search_query.order_by(
                select(Event.date > datetime.now())
                .where(Event.group_id == EventGroup.id)
                .exists()
                .desc(),
                select(Event.date)
                .where(Event.group_id == EventGroup.id)
                .order_by(Event.date.desc())
                .limit(1)
                .scalar_subquery()
                .desc()
                .nulls_last(),
                EventGroup.name,
            )
            .slice(start, end)
            .options(
                selectinload(EventGroup.events)
                .selectinload(Event.task)
                .selectinload(Task.typed_tasks)
                .selectinload(TypedTask.task_states)
                .selectinload(TaskState.user),
                selectinload(EventGroup.aggregate_task).selectinload(Task.typed_tasks),
            )
        )

        result = await self.db.execute(search_query)
        return result.scalars().all()

    async def update_event_group(
        self,
        event_group: EventGroup,
        name: str,
        description: str = "",
        organizer: str = "",
        link: str = "",
    ) -> EventGroup:
        event_group.name = name
        event_group.description = description
        event_group.organizer = organizer
        event_group.link = link
        return await self.update(event_group)

    async def get_actual_events(self) -> list[Event]:
        min_date_query = (
            select(func.min(Event.date))
            .join(Task, Event.id == Task.event_id)
            .join(TypedTask, Task.id == TypedTask.task_id)
            .join(TaskState, TypedTask.id == TaskState.type_task_id)
            .where(
                or_(
                    # Событие ещё не прошло
                    and_(
                        Event.date >= date.today(),
                        or_(
                            Event.date > date.today(),
                            Event.end_time > datetime.now().time(),
                        ),
                    ),
                    # Или есть pending задача фотографа
                    and_(
                        TypedTask.task_type == UserRole.PHOTOGRAPHER,
                        TaskState.state == State.PENDING,
                    ),
                )
            )
        )
        actual_events_query = (
            select(Event)
            .where(Event.date >= min_date_query.scalar_subquery())
            .order_by(Event.date)
            .options(self._get_event_options())
        )

        result = await self.db.execute(actual_events_query)
        return result.scalars().all()

    async def get_events_by_period(self, date_from: date, date_to: date) -> list[Event]:
        query = (
            select(Event)
            .where(
                and_(
                    Event.date >= date_from,
                    Event.date <= date_to,
                )
            )
            .order_by(Event.date)
            .options(self._get_event_options())
        )
        result = await self.db.execute(query)
        return result.scalars().all()
