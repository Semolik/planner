import uuid
from api.schemas.stats import StatsUser
from api.core.users_controller import current_superuser
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
