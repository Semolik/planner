from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, and_
from sqlalchemy.orm import selectinload

from api.cruds.events_crud import EventsCRUD
from api.cruds.tasks_crud import TasksCRUD
from api.models.events_models import Task, Event, EventGroup
from api.models.user_models import User
import re


class SearchCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def search(
        self,
        query: str,
        limit: int = 50,
    ) -> dict:
        """
        Поиск по задачам, мероприятиям, группам и пользователям
        """
        if not query or len(query.strip()) < 2:
            return {
                "tasks": [],
                "events": [],
                "groups": [],
                "users": [],
            }

        # Удаляем http/https только в начале запроса
        query_clean = re.sub(r"^https?://", "", query.strip(), flags=re.IGNORECASE)
        search_term = f"%{query_clean.lower()}%"
        results = {
            "tasks": [],
            "events": [],
            "groups": [],
            "users": [],
        }

        # Сначала получаем ID
        task_ids_query = (
            select(Task.id)
            .outerjoin(User, Task.birthday_user_id == User.id)
            .where(
                or_(
                    func.lower(Task.name).ilike(search_term),
                    func.lower(User.first_name).ilike(search_term),
                    func.lower(User.last_name).ilike(search_term),
                )
            )
            .limit(limit)
        )
        task_ids_result = await self.session.execute(task_ids_query)
        task_ids = [row[0] for row in task_ids_result]

        # Затем загружаем полные объекты
        if task_ids:
            tasks_query = (
                select(Task)
                .where(Task.id.in_(task_ids))
                .options(*TasksCRUD(self.session).get_task_options())
            )
            tasks = await self.session.execute(tasks_query)
            results["tasks"] = list(tasks.scalars().all())
        else:
            results["tasks"] = []

        # Поиск по мероприятиям (загружаем связанную задачу)
        event_query = (
            select(Event)
            .where(
                or_(
                    func.lower(Event.name).ilike(search_term),
                    func.lower(Event.location).ilike(search_term),
                    func.lower(Event.link).ilike(search_term),  # добавлен поиск по link
                )
            )
            .options(EventsCRUD(self.session)._get_event_options())
            .limit(limit)
        )
        events = await self.session.execute(event_query)
        results["events"] = list(events.scalars().all())

        # Поиск по группам мероприятий (загружаем события)
        group_query = (
            select(EventGroup)
            .where(
                or_(
                    func.lower(EventGroup.name).ilike(search_term),
                    func.lower(EventGroup.link).ilike(search_term),
                )
            )
            .options(*EventsCRUD(self.session).get_event_group_options())
            .limit(limit)
        )
        groups = await self.session.execute(group_query)
        results["groups"] = list(groups.scalars().all())

        user_query = (
            select(User)
            .where(
                or_(
                    func.lower(User.first_name).ilike(search_term),
                    func.lower(User.last_name).ilike(search_term),
                    func.lower(User.group).ilike(search_term),
                )
            )
            .options(selectinload(User.institute))
            .limit(limit)
        )
        users = await self.session.execute(user_query)
        results["users"] = list(users.scalars().all())

        return results
