from datetime import date
import uuid
from schemas.stats import StatsUser, StatsMonth
from cruds.base_crud import BaseCRUD
from models.user_models import User, UserRole
from models.events_models import TaskState, TypedTask, State, Task, Event
from sqlalchemy import Integer, select, func, extract, case, Date
from sqlalchemy.orm import aliased
from typing import List, Dict
from sqlalchemy.orm import selectinload


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


class StatisticsCRUD(BaseCRUD):
    async def get_statistics(
        self, period_start: date, period_end: date
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
            else_=func.cast(typed_task_alias.due_date, type_=Date)
        )

        # Subquery that groups by user_id, month, and role
        # ВАЖНО: джоиним только по TypedTask.task_type, а не по UserRoleAssociation
        subquery = (
            select(
                user_alias.id.label("user_id"),
                extract("month", effective_date)
                .cast(Integer)
                .label("month"),
                typed_task_alias.task_type.label("role"),
                func.count(task_state_alias.id).label("count"),
            )
            .join(task_state_alias.user.of_type(user_alias))
            .join(task_state_alias.typed_task.of_type(typed_task_alias))
            .join(
                task_alias,
                typed_task_alias.task_id == task_alias.id
            )
            .outerjoin(  # LEFT JOIN потому что не у всех задач есть событие
                event_alias,
                task_alias.event_id == event_alias.id
            )
            .where(
                task_state_alias.state == State.COMPLETED,
                case(
                    # Если есть событие, проверяем его дату
                    (event_alias.date.isnot(None),
                     event_alias.date.between(period_start, period_end)),
                    # Иначе проверяем дату типизированной задачи
                    else_=func.cast(typed_task_alias.due_date, type_=Date).between(
                        period_start, period_end
                    )
                )
            )
            .group_by(
                user_alias.id,
                extract("month", effective_date).cast(Integer),
                typed_task_alias.task_type  # Группируем по типу задачи, а не по ролям пользователя
            )
            .subquery()
        )

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
                # Initialize all months with zero counts for all roles
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
                }
            )
            for user_id in stats_map
        ]
