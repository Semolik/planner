from datetime import date
import uuid
from schemas.stats import StatsUser
from cruds.base_crud import BaseCRUD
from models.user_models import User
from models.events_models import TaskState, TypedTask, State
from sqlalchemy import Integer, select, func, extract
from sqlalchemy.orm import aliased
from typing import List, Dict, Union
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

        subquery = (
            select(
                user_alias.id.label("user_id"),
                extract("month", typed_task_alias.due_date)
                .cast(Integer)
                .label("month"),
                func.count(task_state_alias.id).label("count"),
            )
            .outerjoin(task_state_alias.user.of_type(user_alias))
            .join(task_state_alias.typed_task.of_type(typed_task_alias))
            .where(
                task_state_alias.state == State.COMPLETED,
                typed_task_alias.due_date.between(period_start, period_end),
            )
            .group_by(
                user_alias.id, extract("month", typed_task_alias.due_date).cast(Integer)
            )
            .subquery()
        )

        stmt = (
            select(User)
            .outerjoin(subquery, subquery.c.user_id == User.id)
            .add_columns(subquery.c.month, subquery.c.count)
            .order_by(User.last_name)
            .options(
                selectinload(User.institute),
            )
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        stats_map: Dict[Union[str, uuid.UUID], Dict[int, int]] = {}
        users_map: Dict[Union[str, uuid.UUID], User] = {}

        for row in rows:
            user = row[0]
            month = row[1]
            count = row[2]

            user_id = user.id

            if user_id not in stats_map:
                stats_map[user_id] = {m: 0 for m in all_months_in_range}
                users_map[user_id] = user

            if month is not None:
                stats_map[user_id][month] = count

        return [
            StatsUser(user=users_map[user_id], stats=stats_map[user_id])
            for user_id in stats_map
        ]
