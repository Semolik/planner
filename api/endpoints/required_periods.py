import uuid
from fastapi import APIRouter, Depends, HTTPException
from api.core.users_controller import current_superuser, current_user
from api.db.session import get_async_session
from api.schemas.periods import RequiredPeriod
from api.cruds.periods_crud import PeriodsCRUD
from api.schemas.periods import CreateOrUpdatePeriodRequest

api_router = APIRouter(prefix="/required-periods", tags=["required periods"])


@api_router.get(
    "", dependencies=[Depends(current_user)], response_model=list[RequiredPeriod]
)
async def get_required_periods(
    db=Depends(get_async_session),
):
    return await PeriodsCRUD(db).get_periods()


@api_router.post(
    "", response_model=RequiredPeriod, dependencies=[Depends(current_superuser)]
)
async def create_required_period(
    create_data: CreateOrUpdatePeriodRequest,
    db=Depends(get_async_session),
):
    if create_data.period_start >= create_data.period_end:
        raise HTTPException(
            status_code=400,
            detail="Дата начала периода должна быть меньше даты конца периода",
        )
    periods_crud = PeriodsCRUD(db)
    if await periods_crud.get_period_from_range(
        create_data.period_start, create_data.period_end
    ):
        raise HTTPException(
            status_code=400, detail="Период в этом диапазоне уже существует"
        )

    period = await PeriodsCRUD(db).create_period(
        period_start=create_data.period_start,
        period_end=create_data.period_end,
        photographers_count=create_data.photographers_count,
        designers_count=create_data.designers_count,
        copywriters_count=create_data.copywriters_count,
    )
    return await PeriodsCRUD(db).get_period_by_id(period.id)


@api_router.get(
    "/{period_id}", response_model=RequiredPeriod, dependencies=[Depends(current_user)]
)
async def get_required_period(
    period_id: uuid.UUID,
    db=Depends(get_async_session),
):
    period = await PeriodsCRUD(db).get_period_by_id(period_id)
    if not period:
        raise HTTPException(status_code=404, detail="Период не найден")
    return period


@api_router.put(
    "/{period_id}",
    response_model=RequiredPeriod,
    dependencies=[Depends(current_superuser)],
)
async def update_required_period(
    period_id: uuid.UUID,
    update_data: CreateOrUpdatePeriodRequest,
    db=Depends(get_async_session),
):
    if update_data.period_start >= update_data.period_end:
        raise HTTPException(
            status_code=400,
            detail="Дата начала периода должна быть меньше даты конца периода",
        )
    periods_crud = PeriodsCRUD(db)
    period = await periods_crud.get_period_by_id(period_id)
    if not period:
        raise HTTPException(status_code=404, detail="Период не найден")
    existing_period = await periods_crud.get_period_from_range(
        update_data.period_start, update_data.period_end
    )
    if existing_period and existing_period.id != period_id:
        raise HTTPException(
            status_code=400, detail="Период в этом диапазоне уже существует"
        )
    period.period_start = update_data.period_start
    period.period_end = update_data.period_end

    role_counts = {
        "PHOTOGRAPHER": update_data.photographers_count,
        "DESIGNER": update_data.designers_count,
        "COPYWRITER": update_data.copywriters_count,
    }
    for config in period.roles_config:
        if config.user_role.name in role_counts:
            config.count = role_counts[config.user_role.name]
    await db.commit()
    return await periods_crud.get_period_by_id(period.id)


@api_router.delete(
    "/{period_id}", status_code=204, dependencies=[Depends(current_superuser)]
)
async def delete_required_period(
    period_id: uuid.UUID,
    db=Depends(get_async_session),
):
    periods_crud = PeriodsCRUD(db)
    period = await periods_crud.get_period_by_id(period_id)
    if not period:
        raise HTTPException(status_code=404, detail="Период не найден")
    await periods_crud.delete(period)
