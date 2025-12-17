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

        # Вычисляем дату для группировки: дата события если есть, иначе дата типизированной задачи
        effective_date = case(
            (event_alias.date.isnot(None), event_alias.date),
            else_=func.cast(typed_task_alias.due_date, type_=Date),
        )

        # Subquery that groups by user_id, month, and role
        subquery_stmt = (
            select(
                user_alias.id.label("user_id"),
                extract("month", effective_date).cast(Integer).label("month"),
                typed_task_alias.task_type.label("role"),
                func.count(task_state_alias.id).label("count"),
            )
            .join(task_state_alias.user.of_type(user_alias))
            .join(task_state_alias.typed_task.of_type(typed_task_alias))
            .join(task_alias, typed_task_alias.task_id == task_alias.id)
            .outerjoin(event_alias, task_alias.event_id == event_alias.id)
            .where(
                task_state_alias.state == State.COMPLETED,
                case(
                    (
                        event_alias.date.isnot(None),
                        event_alias.date.between(period_start, period_end),
                    ),
                    else_=func.cast(typed_task_alias.due_date, type_=Date).between(
                        period_start, period_end
                    ),
                ),
            )
            .group_by(
                user_alias.id,
                extract("month", effective_date).cast(Integer),
                typed_task_alias.task_type,
            )
        )

        if user_ids:
            subquery_stmt = subquery_stmt.where(user_alias.id.in_(user_ids))

        subquery = subquery_stmt.subquery()

        # Main query to get all users with their stats
        stmt = (
            select(User)
            .outerjoin(subquery, subquery.c.user_id == User.id)
            .add_columns(subquery.c.month, subquery.c.role, subquery.c.count)
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

            # Initialize user entry if not exists
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

            # Update the count for the specific month and role
            if month is not None and role is not None:
                stats_map[user_id][month][role] = count

        # Convert to Pydantic models
        return [
            StatsUser(
                user=users_map[user_id],
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