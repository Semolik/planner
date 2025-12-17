from datetime import date
import uuid
from api.schemas.stats import StatsUser, StatsMonth
from api.cruds.base_crud import BaseCRUD
from api.models.user_models import User, UserRole
from api.models.events_models import TaskState, TypedTask, State, Task, Event, EventGroup
from sqlalchemy import Integer, select, func, extract, case, Date, cast, between, String, and_, or_
from sqlalchemy.orm import selectinload, aliased
from api.schemas.users import UserReadShort
from typing import List, Dict
from sqlalchemy.sql.expression import literal_column


def get_months_between(start_date: date, end_date: date) -> set:
    """
    Возвращает множество номеров месяцев (от 1 до 12),
    которые попадают в период между start_date и end_date.
    """
    months = set()
    current = start_date.replace(day=1)

    while True:
        # Добавляем месяц
        if current <= end_date:
            months.add(current.month)
        else:
            break

        # Переход к следующему месяцу
        if current.month == 12:
            next_month = current.replace(year=current.year + 1, month=1)
        else:
            next_month = current.replace(month=current.month + 1)

        current = next_month

    return months

from datetime import date
import uuid
from api.schemas.stats import StatsUser, StatsMonth
from api.cruds.base_crud import BaseCRUD
from api.models.user_models import User, UserRole
from api.models.events_models import TaskState, TypedTask, State, Task, Event, EventGroup
from sqlalchemy import Integer, select, func, extract, case, Date, cast, between, String, and_, or_
from sqlalchemy.orm import selectinload, aliased
from api.schemas.users import UserReadShort
from typing import List, Dict
from sqlalchemy.sql.expression import literal_column


def get_months_between(start_date: date, end_date: date) -> set:
    """
    Возвращает множество номеров месяцев (от 1 до 12),
    которые попадают в период между start_date и end_date.
    """
    months = set()
    current = start_date.replace(day=1)

    while True:
        if current <= end_date:
            months.add(current.month)
        else:
            break

        if current.month == 12:
            next_month = current.replace(year=current.year + 1, month=1)
        else:
            next_month = current.replace(month=current.month + 1)

        current = next_month

    return months


class StatisticsCRUD(BaseCRUD):
    async def get_statistics(
        self,
        period_start: date,
        period_end: date,
        user_ids: List[uuid.UUID] | None = None,
    ) -> List[StatsUser]:
        all_months_in_range = get_months_between(period_start, period_end)

        user_alias = aliased(User)
        task_state_alias = aliased(TaskState)
        typed_task_alias = aliased(TypedTask)
        task_alias = aliased(Task)
        event_alias = aliased(Event)
        event_group_alias = aliased(EventGroup)

        # Подзапрос 1: typed_tasks агрегированных задач (по aggregate_task_id)
        agg_subq = (
            select(
                user_alias.id.label("user_id"),
                extract("month", cast(typed_task_alias.due_date, Date)).cast(Integer).label("month"),
                cast(typed_task_alias.task_type, String).label("role"),
                func.count(task_state_alias.id).label("count"),
            )
            .join(task_state_alias.user.of_type(user_alias))
            .join(task_state_alias.typed_task.of_type(typed_task_alias))
            .join(task_alias, typed_task_alias.task_id == task_alias.id)
            .join(event_group_alias, event_group_alias.aggregate_task_id == task_alias.id)
            .where(
                task_state_alias.state == State.COMPLETED,
                cast(typed_task_alias.due_date, Date).between(period_start, period_end),
            )
            .group_by(
                user_alias.id,
                extract("month", cast(typed_task_alias.due_date, Date)).cast(Integer),
                cast(typed_task_alias.task_type, String),
            )
        )

        # Подзапрос 2: typed_tasks задач мероприятий в группах с aggregate_task_id
        # ИСПРАВЛЕНИЕ: используем typed_task_alias.due_date вместо event_alias.date
        event_subq = (
            select(
                user_alias.id.label("user_id"),
                extract("month", cast(typed_task_alias.due_date, Date)).cast(Integer).label("month"),
                cast(typed_task_alias.task_type, String).label("role"),
                func.count(task_state_alias.id).label("count"),
            )
            .join(task_state_alias.user.of_type(user_alias))
            .join(task_state_alias.typed_task.of_type(typed_task_alias))
            .join(task_alias, typed_task_alias.task_id == task_alias.id)
            .join(event_alias, task_alias.event_id == event_alias.id)
            .join(event_group_alias, event_alias.group_id == event_group_alias.id)
            .where(
                task_state_alias.state == State.COMPLETED,
                event_group_alias.aggregate_task_id.isnot(None),
                cast(typed_task_alias.due_date, Date).between(period_start, period_end),
            )
            .group_by(
                user_alias.id,
                extract("month", cast(typed_task_alias.due_date, Date)).cast(Integer),
                cast(typed_task_alias.task_type, String),
            )
        )

        # Подзапрос 3: typed_tasks обычных задач (не агрегатор группы и не задача мероприятия группы)
        normal_subq = (
            select(
                user_alias.id.label("user_id"),
                extract("month", func.coalesce(event_alias.date, cast(typed_task_alias.due_date, Date))).cast(Integer).label("month"),
                cast(typed_task_alias.task_type, String).label("role"),
                func.count(task_state_alias.id).label("count"),
            )
            .join(task_state_alias.user.of_type(user_alias))
            .join(task_state_alias.typed_task.of_type(typed_task_alias))
            .join(task_alias, typed_task_alias.task_id == task_alias.id)
            .outerjoin(event_alias, task_alias.event_id == event_alias.id)
            .outerjoin(event_group_alias, event_group_alias.aggregate_task_id == task_alias.id)
            .where(
                task_state_alias.state == State.COMPLETED,
                event_group_alias.id.is_(None),  # Не агрегатор группы
                or_(event_alias.group_id.is_(None), event_alias.id.is_(None)),  # Не задача мероприятия группы
                func.coalesce(event_alias.date, cast(typed_task_alias.due_date, Date)).between(period_start, period_end),
            )
            .group_by(
                user_alias.id,
                extract("month", func.coalesce(event_alias.date, cast(typed_task_alias.due_date, Date))).cast(Integer),
                cast(typed_task_alias.task_type, String),
            )
        )

        # Объединяем все три подзапроса
        from sqlalchemy import union_all as sa_union_all
        union_subq = sa_union_all(agg_subq, event_subq, normal_subq).subquery()

        # Main query
        stmt = (
            select(User)
            .outerjoin(union_subq, union_subq.c.user_id == User.id)
            .add_columns(union_subq.c.month, union_subq.c.role, union_subq.c.count)
            .order_by(User.last_name)
            .options(
                selectinload(User.institute),
                selectinload(User.roles_objects),
            )
        )

        if user_ids:
            stmt = stmt.where(User.id.in_(user_ids))

        result = await self.db.execute(stmt)
        rows = result.all()

        # Build the statistics structure
        stats_map: Dict[uuid.UUID, Dict[int, Dict[UserRole, int]]] = {}
        users_map: Dict[uuid.UUID, User] = {}

        for row in rows:
            user = row[0]
            month = row[1]
            role = row[2]
            count = row[3]

            user_id = user.id

            if user_id not in stats_map:
                stats_map[user_id] = {
                    m: {
                        UserRole.PHOTOGRAPHER: 0,
                        UserRole.COPYWRITER: 0,
                        UserRole.DESIGNER: 0,
                    }
                    for m in all_months_in_range
                }
                users_map[user_id] = user

            if month is not None and role is not None:
                stats_map[user_id][month][role] = count

        # Convert to Pydantic models
        UserReadShort.model_config = {'from_attributes': True}
        return [
            StatsUser(
                user=UserReadShort.model_validate(users_map[user_id]),
                stats={
                    month: StatsMonth(
                        photographer=month_stats[UserRole.PHOTOGRAPHER],
                        copywriter=month_stats[UserRole.COPYWRITER],
                        designer=month_stats[UserRole.DESIGNER],
                    )
                    for month, month_stats in stats_map[user_id].items()
                },
            )
            for user_id in stats_map
        ]
