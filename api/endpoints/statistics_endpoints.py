import uuid

from api.cruds.users_crud import UsersCRUD
from api.models.user_models import User
from api.schemas.stats import StatsUser
from api.core.users_controller import current_superuser, current_user
from api.cruds.statistics_crud import StatisticsCRUD
from fastapi import APIRouter, Depends, HTTPException

from api.db.session import get_async_session

from api.cruds.periods_crud import PeriodsCRUD

api_router = APIRouter(
    prefix="/statistics", tags=["statistics"], dependencies=[Depends(current_superuser)]
)


@api_router.get("", response_model=list[StatsUser])
async def get_statistics(
    period_id: uuid.UUID,
    db=Depends(get_async_session),
):
    periods_crud = PeriodsCRUD(db)
    period = await periods_crud.get_period_by_id(period_id)
    if not period:
        raise HTTPException(status_code=404, detail="Период не найден")
    statistics_crud = StatisticsCRUD(db)
    return await statistics_crud.get_statistics(
        period_start=period.period_start, period_end=period.period_end
    )


@api_router.get("/{user_id}", response_model=StatsUser)
async def get_user_statistics(
    user_id: uuid.UUID,
    period_id: uuid.UUID,
    db=Depends(get_async_session),
    current_db_user: User = Depends(current_user),
):
    user = await UsersCRUD(db).get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if user.id != current_db_user.id and not current_db_user.is_superuser:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    periods_crud = PeriodsCRUD(db)
    period = await periods_crud.get_period_by_id(period_id)
    if not period:
        raise HTTPException(status_code=404, detail="Период не найден")
    statistics_crud = StatisticsCRUD(db)
    users_stats = await statistics_crud.get_statistics(
        period_start=period.period_start,
        period_end=period.period_end,
        user_ids=[user_id],
    )
    return users_stats[0]
