import uuid
from datetime import date

from sqlalchemy import select, func, and_

from api.cruds.base_crud import BaseCRUD
from api.cruds.events_crud import EventsCRUD
from api.models.events_models import Event, Task, TypedTask, TaskState, State
from api.models.user_models import CustomAchievementModel
from api.schemas.custom_achievements import (
    AchievementCreate,
    AchievementUpdate,
)


class CustomAchievementsCRUD(BaseCRUD):
    async def create_custom_achievement(
        self, custom_achievement: AchievementCreate, user_id: uuid.UUID
    ):
        return await self.create(
            CustomAchievementModel(**custom_achievement.model_dump(), user_id=user_id)
        )

    async def get_custom_achievement_by_id(
        self, custom_achievement_id: uuid.UUID
    ) -> CustomAchievementModel:
        return await self.get(custom_achievement_id, CustomAchievementModel)

    async def update_custom_achievement(
        self,
        custom_achievement: CustomAchievementModel,
        update_data: AchievementUpdate,
    ):
        for field, value in update_data.model_dump().items():
            setattr(custom_achievement, field, value)
        return await self.update(custom_achievement)

    async def get_user_achievements_by_year(
            self,
            user_id: uuid.UUID,
            year: int,
            only_custom: bool = False,
    ) -> list[dict]:
        """
        Получить список достижений пользователя за год.

        Args:
            user_id: ID пользователя
            year: Год для фильтрации
            only_custom: Если True, возвращать только кастомные достижения

        Returns:
            Список достижений с полями:
            - id: UUID
            - name: название мероприятия
            - date_from: дата начала
            - date_to: дата окончания (опционально)
            - level_of_participation: уровень участия
            - achievement_level: уровень мероприятия
            - link: ссылка на подтверждение
            - is_custom: флаг кастомного достижения
        """
        results = []

        # Кастомные достижения
        custom_query = (
            select(CustomAchievementModel)
            .where(
                CustomAchievementModel.user_id == user_id,
                func.extract("year", CustomAchievementModel.date_from) == year,
            )
            .order_by(CustomAchievementModel.date_from.desc())
        )

        custom_result = await self.db.execute(custom_query)
        custom_achievements = custom_result.scalars().all()

        for achievement in custom_achievements:
            results.append({
                "id": achievement.id,
                "name": achievement.name,
                "date_from": achievement.date_from,
                "date_to": achievement.date_to,
                "level_of_participation": achievement.level_of_participation,
                "achievement_level": achievement.achievement_level,
                "link": achievement.link,
                "is_custom": True,
            })

        # Если только кастомные - возвращаем только их
        if only_custom:
            return results

        # Системные достижения из Event
        # Выбираем сами Event (entity), чтобы можно было применять .options(...) и затем
        # собрать информацию из уже загруженных связей (task -> typed_tasks -> task_states)
        system_query = (
            select(Event)
            .join(Task, Task.event_id == Event.id)
            .join(TypedTask, TypedTask.task_id == Task.id)
            .join(TaskState, TaskState.type_task_id == TypedTask.id)
            .where(
                and_(
                    TaskState.user_id == user_id,
                    TaskState.state == State.COMPLETED,
                    func.extract("year", Event.date) == year,
                    Task.use_in_pgas == True,
                    ~Event.exclude_admin_report,
                )
            )
            .distinct(Event.id)
            # PostgreSQL: when using DISTINCT ON (events.id), ORDER BY must start with events.id
            .order_by(Event.id, Event.date.desc())
            .options(
                EventsCRUD(self.db)._get_event_options(),
            )
        )

        system_result = await self.db.execute(system_query)
        system_events = system_result.scalars().all()

        # Маппинг ролей в читаемый вид
        role_mapping = {
            "PHOTOGRAPHER": "Фотограф",
            "photographer": "Фотограф",
            "COPYWRITER": "Журналист",
            "copywriter": "Журналист",
            "DESIGNER": "Дизайнер",
            "designer": "Дизайнер",
        }

        for event in system_events:
            # попытка получить связанную задачу (created task for event)
            task = getattr(event, "task", None)
            if task is None:
                # нет связанной задачи, пропускаем (маловероятно, т.к. join гарантировал наличие)
                continue

            # Собираем роли отдельными записями: role_key -> link
            role_to_link: dict[str, str | None] = {}

            # task.typed_tasks должен быть загружен благодаря опциям
            typed_tasks = getattr(task, "typed_tasks", []) or []
            for typed in typed_tasks:
                # проверяем, есть ли завершённый state для нашего пользователя
                task_states = getattr(typed, "task_states", []) or []
                for ts in task_states:
                    if ts.user_id == user_id and ts.state == State.COMPLETED:
                        tt = getattr(typed, "task_type", None)
                        if tt is None:
                            role_key = None
                        else:
                            try:
                                role_key = tt.value if hasattr(tt, "value") else str(tt)
                            except Exception:
                                role_key = str(tt)

                        if role_key:
                            # сохраняем первую найденную ссылку для роли
                            if role_key not in role_to_link:
                                role_to_link[role_key] = getattr(typed, "link", None)
                        break

            # Создаём отдельную запись для каждой роли (если есть)
            if role_to_link:
                for role_key, link in role_to_link.items():
                    results.append({
                        "id": event.id,
                        "name": event.name,
                        "date_from": event.date,
                        "date_to": None,
                        "level_of_participation": role_mapping.get(role_key, role_key),
                        "achievement_level": getattr(event, "level", None),
                        "link": link,
                        "is_custom": False,
                    })
            else:
                # если ролей не найдено — создаём одну запись без роли
                results.append({
                    "id": event.id,
                    "name": event.name,
                    "date_from": event.date,
                    "date_to": None,
                    "level_of_participation": None,
                    "achievement_level": getattr(event, "level", None),
                    "link": None,
                    "is_custom": False,
                })

        # Сортируем все результаты по дате (от новых к старым)
        results.sort(key=lambda x: x["date_from"] or date.min, reverse=True)

        return results
