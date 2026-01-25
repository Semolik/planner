import uuid
from datetime import date
from typing import Optional

from sqlalchemy import select, func, and_, case
from sqlalchemy.orm import aliased

from api.cruds.base_crud import BaseCRUD
from api.cruds.tasks_crud import TasksCRUD
from api.models.events_models import (
    Event,
    Task,
    TypedTask,
    TaskState,
    State,
    EventGroup,
)
from api.models.user_models import CustomAchievementModel, UserRole
from api.schemas.achievements import (
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
        results: list[dict] = []

        # ---------- 1. Кастомные достижения ----------
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
            results.append(
                {
                    "id": achievement.id,
                    "name": achievement.name,
                    "date_from": achievement.date_from,
                    "date_to": achievement.date_to,
                    "level_of_participation": achievement.level_of_participation,
                    "achievement_level": achievement.achievement_level,
                    "link": achievement.link,
                    "score": achievement.score,
                    "is_custom": True,
                    "event_id": None,
                    "is_aggregated": False,
                }
            )

        if only_custom:
            results.sort(key=lambda x: x["date_from"] or date.min, reverse=True)
            return results

        # ---------- 2. Все завершённые TypedTask за год ----------
        task_alias = aliased(Task)
        event_alias = aliased(Event)

        # Подзапрос: является ли task агрегационной задачей группы
        is_aggregate_task = (
            select(1)
            .select_from(EventGroup)
            .where(EventGroup.aggregate_task_id == task_alias.id)
            .exists()
        )

        # Эффективная дата как в get_user_completed_typed_tasks
        effective_date = case(
            # Если это агрегационная задача группы → используем due_date
            (is_aggregate_task, TypedTask.due_date),
            # Если task привязан к event → используем event.date
            (task_alias.event_id.isnot(None), event_alias.date),
            # Во всех остальных случаях (например, дни рождения) → due_date
            else_=TypedTask.due_date,
        )

        period_start = date(year, 1, 1)
        period_end = date(year, 12, 31)

        typed_query = (
            select(TypedTask, task_alias, event_alias)
            .join(TaskState, TypedTask.id == TaskState.type_task_id)
            .join(task_alias, TypedTask.task_id == task_alias.id)
            .outerjoin(event_alias, task_alias.event_id == event_alias.id)
            .where(
                TaskState.user_id == user_id,
                TaskState.state == State.COMPLETED,
                effective_date.between(period_start, period_end),
                task_alias.use_in_pgas.is_(
                    True
                ),  # ВАЖНО: только задачи, используемые в ПГАС
            )
            .options(*TasksCRUD(self.db).get_typed_task_options())
        )

        typed_result = await self.db.execute(typed_query)
        typed_rows = typed_result.all()

        # aggregate_task_id для групп (для is_aggregated)
        aggregate_task_ids_result = await self.db.execute(
            select(EventGroup.aggregate_task_id)
        )
        aggregate_task_ids = set(
            row[0] for row in aggregate_task_ids_result if row[0] is not None
        )

        role_mapping = {
            UserRole.PHOTOGRAPHER.value: "Фотограф",
            UserRole.COPYWRITER.value: "Журналист",
            UserRole.DESIGNER.value: "Дизайнер",
        }

        for typed_task, task_obj, event_obj in typed_rows:
            # финальная дата:
            # если есть event → используем event.date, иначе берём due_date
            if task_obj.event_id is not None and event_obj is not None:
                final_date = event_obj.date
            else:
                final_date = typed_task.due_date

            if final_date is None:
                final_date = period_start

            # собираем роли для конкретного typed_task
            task_states = getattr(typed_task, "task_states", []) or []
            roles_for_user: set[str] = set()

            photographer_link: Optional[str] = None

            for ts in task_states:
                if ts.user_id != user_id or ts.state != State.COMPLETED:
                    continue

                tt = getattr(typed_task, "task_type", None)
                if tt is None:
                    role_key = None
                else:
                    try:
                        role_key = tt.value if hasattr(tt, "value") else str(tt)
                    except Exception:
                        role_key = str(tt)

                if not role_key:
                    continue

                roles_for_user.add(role_key)

                # только для фотографа тянем ссылку, и только один раз
                if (
                    role_key == UserRole.PHOTOGRAPHER.value
                    and photographer_link is None
                ):
                    link: Optional[str] = None

                    # 1) сначала event
                    if event_obj is not None:
                        link = getattr(event_obj, "link", None)

                    # 2) если нет — пробуем task
                    if not link and task_obj is not None:
                        link = getattr(task_obj, "link", None)

                    # 3) если нет — пробуем group
                    if (
                        not link
                        and event_obj is not None
                        and getattr(event_obj, "group", None) is not None
                    ):
                        link = getattr(event_obj.group, "link", None)

                    photographer_link = link

            name = typed_task.displayed_name
            if not name and event_obj is not None:
                name = event_obj.name
            if not name:
                print(event_obj)
                raise ValueError("Не удалось определить имя достижения")

            is_aggregated = False
            if task_obj and task_obj.id in aggregate_task_ids:
                is_aggregated = True

            achievement_base = {
                "name": name,
                "date_from": final_date,
                "date_to": None,
                "achievement_level": getattr(event_obj, "level", None)
                if event_obj is not None
                else None,
                "is_custom": False,
                "event_id": task_obj.event_id,
                "is_aggregated": is_aggregated,
            }

            # фотограф с линком (если роль есть)
            if UserRole.PHOTOGRAPHER.value in roles_for_user:
                score = 0
                if achievement_base["event_id"] or is_aggregated:
                    score = 10

                results.append(
                    {
                        "id": task_obj.id,
                        "level_of_participation": role_mapping.get(
                            UserRole.PHOTOGRAPHER.value, UserRole.PHOTOGRAPHER.value
                        ),
                        "link": photographer_link,
                        "score": score,
                        **achievement_base,
                    }
                )

            # остальные роли — без ссылок
            for role_key in roles_for_user:
                if role_key == UserRole.PHOTOGRAPHER.value:
                    continue

                score = 0
                if role_key == UserRole.DESIGNER.value:
                    score = 3

                if (
                    task_obj.birthday_user_id is not None
                    and achievement_base["achievement_level"] is None
                ):
                    achievement_base["achievement_level"] = "Университетский"

                results.append(
                    {
                        "id": task_obj.id,
                        "level_of_participation": role_mapping.get(role_key, role_key),
                        "link": None,
                        "score": score,
                        **achievement_base,
                    }
                )

        # ---------- финальная сортировка ----------
        results.sort(key=lambda x: x["date_from"] or date.min, reverse=True)

        return results
