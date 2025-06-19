from datetime import date
from schemas.stats import StatsUser
from utilities.files import save_image
from core.users_controller import current_superuser
from cruds.statistics_crud import StatisticsCRUD
from fastapi import APIRouter, Depends, File, UploadFile

from db.session import get_async_session
api_router = APIRouter(
    prefix="/statistics", tags=["statistics"], dependencies=[Depends(current_superuser)])


@api_router.get("", response_model=list[StatsUser])
async def get_statistics(
    period_start: date,
    period_end: date,
    db=Depends(get_async_session),
):
    """
    Получить статистику пользователей за указанный период.
    Период задается датами начала и конца.
    """

    statistics_crud = StatisticsCRUD(db)
    return await statistics_crud.get_statistics(period_start, period_end)
